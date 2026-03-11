"""
Security Audit Service - Automated dependency vulnerability monitoring with CVE alerting
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
import resend

logger = logging.getLogger("security_audit_service")

# Resend email config
resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = "onboarding@resend.dev"
DEFAULT_ALERT_EMAIL = os.environ.get("CVE_ALERT_EMAIL", "")

FRONTEND_DIR = "/app/frontend"
BACKEND_DIR = "/app/backend"

_service_instance = None


def get_security_audit_service():
    global _service_instance
    if _service_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _service_instance = SecurityAuditService(db)
    return _service_instance


class SecurityAuditService:
    def __init__(self, db):
        self.db = db
        self.audits_col = db["security_audits"]
        self.alerts_col = db["security_alerts"]
        self.config_col = db["security_monitor_config"]
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 300
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_running = False

    # ─── Monitoring Scheduler ──────────────────────────────────────

    async def get_monitor_config(self) -> Dict[str, Any]:
        config = await self.config_col.find_one({"type": "monitor"}, {"_id": 0})
        if not config:
            config = {
                "type": "monitor",
                "enabled": False,
                "interval_hours": 24,
                "alert_on_critical": True,
                "alert_on_high": True,
                "alert_on_moderate": False,
                "alert_on_low": False,
                "email_notifications": bool(DEFAULT_ALERT_EMAIL),
                "alert_email": DEFAULT_ALERT_EMAIL,
                "last_scan": None,
                "next_scan": None,
                "total_scans": 0,
            }
            await self.config_col.insert_one({**config})
        else:
            # Migrate old configs missing email fields
            if "email_notifications" not in config:
                config["email_notifications"] = bool(DEFAULT_ALERT_EMAIL)
                config["alert_email"] = DEFAULT_ALERT_EMAIL
                await self.config_col.update_one(
                    {"type": "monitor"},
                    {"$set": {"email_notifications": config["email_notifications"], "alert_email": config["alert_email"]}},
                )
        return {k: v for k, v in config.items() if k != "_id"}

    async def update_monitor_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {"enabled", "interval_hours", "alert_on_critical", "alert_on_high", "alert_on_moderate", "alert_on_low", "email_notifications", "alert_email"}
        clean = {k: v for k, v in updates.items() if k in allowed}
        if not clean:
            return await self.get_monitor_config()

        await self.config_col.update_one(
            {"type": "monitor"},
            {"$set": clean},
            upsert=True,
        )

        config = await self.get_monitor_config()
        if config.get("enabled") and not self._monitor_running:
            self._start_monitor(config["interval_hours"])
        elif not config.get("enabled") and self._monitor_running:
            self._stop_monitor()

        return config

    def _start_monitor(self, interval_hours: int):
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
        self._monitor_running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(interval_hours))
        logger.info(f"CVE monitor started with {interval_hours}h interval")

    def _stop_monitor(self):
        self._monitor_running = False
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
        logger.info("CVE monitor stopped")

    async def _monitor_loop(self, interval_hours: int):
        while self._monitor_running:
            try:
                logger.info("Automated CVE scan starting...")
                result = await self.run_full_audit(force=True, is_scheduled=True)
                await self._check_and_alert(result)

                next_scan = datetime.now(timezone.utc) + timedelta(hours=interval_hours)
                await self.config_col.update_one(
                    {"type": "monitor"},
                    {"$set": {
                        "last_scan": datetime.now(timezone.utc).isoformat(),
                        "next_scan": next_scan.isoformat(),
                    }, "$inc": {"total_scans": 1}},
                )
                logger.info(f"Scan complete. Next scan at {next_scan.isoformat()}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor scan error: {e}")

            try:
                await asyncio.sleep(interval_hours * 3600)
            except asyncio.CancelledError:
                break

    async def start_if_enabled(self):
        config = await self.get_monitor_config()
        if config.get("enabled"):
            self._start_monitor(config["interval_hours"])

    # ─── Alert System ──────────────────────────────────────────────

    async def _check_and_alert(self, scan_result: Dict[str, Any]):
        config = await self.get_monitor_config()
        fe_vulns = scan_result.get("frontend", {}).get("vulnerabilities", [])
        be_vulns = scan_result.get("backend", {}).get("vulnerabilities", [])
        all_vulns = fe_vulns + be_vulns

        if not all_vulns:
            return

        # Get previous scan's vulnerability signatures
        previous = await self.audits_col.find_one(
            {"is_scheduled": True},
            {"_id": 0, "vuln_signatures": 1},
            sort=[("timestamp", -1)],
            skip=1,
        )
        prev_sigs = set(previous.get("vuln_signatures", [])) if previous else set()

        severity_filter = set()
        if config.get("alert_on_critical"):
            severity_filter.add("critical")
        if config.get("alert_on_high"):
            severity_filter.add("high")
        if config.get("alert_on_moderate"):
            severity_filter.add("moderate")
        if config.get("alert_on_low"):
            severity_filter.add("low")

        now = datetime.now(timezone.utc).isoformat()
        new_alerts = []

        for v in all_vulns:
            sig = f"{v.get('module', '')}|{v.get('title', '')}"
            sev = v.get("severity", "unknown").lower()
            if sig not in prev_sigs and sev in severity_filter:
                alert = {
                    "type": "new_vulnerability",
                    "severity": sev,
                    "module": v.get("module", "unknown"),
                    "title": v.get("title", ""),
                    "description": v.get("description", v.get("recommendation", "")),
                    "url": v.get("url", ""),
                    "stack": "frontend" if v in fe_vulns else "backend",
                    "timestamp": now,
                    "read": False,
                    "dismissed": False,
                }
                new_alerts.append(alert)

        if new_alerts:
            await self.alerts_col.insert_many(new_alerts)
            logger.info(f"Generated {len(new_alerts)} new vulnerability alerts")
            # Send email notification
            if config.get("email_notifications") and config.get("alert_email"):
                await self._send_alert_email(new_alerts, scan_result, config["alert_email"])

        # Also generate summary alert if total vulns changed
        total = scan_result.get("total_vulnerabilities", 0)
        sb = scan_result.get("severity_breakdown", {})
        if total > 0 and not prev_sigs:
            summary_alert = {
                "type": "scan_summary",
                "severity": "critical" if sb.get("critical", 0) > 0 else "high" if sb.get("high", 0) > 0 else "moderate",
                "module": "System",
                "title": f"Scan detected {total} vulnerabilities",
                "description": f"Critical: {sb.get('critical', 0)}, High: {sb.get('high', 0)}, Moderate: {sb.get('moderate', 0)}, Low: {sb.get('low', 0)}",
                "url": "",
                "stack": "all",
                "timestamp": now,
                "read": False,
                "dismissed": False,
            }
            await self.alerts_col.insert_one(summary_alert)

    # ─── Email Notifications via Resend ──────────────────────────

    def _build_alert_html(self, alerts: List[Dict[str, Any]], scan_result: Dict[str, Any]) -> str:
        sb = scan_result.get("severity_breakdown", {})
        score = scan_result.get("security_score", 0)
        grade = scan_result.get("grade", "?")
        sev_colors = {"critical": "#ef4444", "high": "#f97316", "moderate": "#eab308", "low": "#3b82f6"}

        vuln_rows = ""
        for a in alerts[:20]:
            color = sev_colors.get(a["severity"], "#94a3b8")
            vuln_rows += f"""
            <tr>
              <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;">
                <span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;text-transform:uppercase;">{a['severity']}</span>
              </td>
              <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;font-weight:600;">{a['module']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;color:#475569;">{a['title']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;">{a['stack']}</td>
            </tr>"""

        return f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:640px;margin:0 auto;background:#0f172a;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:24px 32px;">
            <h1 style="color:#fff;margin:0;font-size:22px;">CVE Alert: {len(alerts)} New Vulnerabilities Detected</h1>
            <p style="color:#c7d2fe;margin:8px 0 0;font-size:14px;">Big Mann Entertainment - Security Monitor</p>
          </div>
          <div style="padding:24px 32px;">
            <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
              <tr>
                <td style="padding:12px;background:#1e293b;border-radius:8px;text-align:center;width:25%;">
                  <div style="font-size:28px;font-weight:700;color:{'#34d399' if score >= 90 else '#facc15' if score >= 60 else '#f87171'};">{score}</div>
                  <div style="font-size:11px;color:#94a3b8;margin-top:4px;">SCORE (Grade {grade})</div>
                </td>
                <td style="width:8px;"></td>
                <td style="padding:12px;background:#1e293b;border-radius:8px;text-align:center;width:25%;">
                  <div style="font-size:28px;font-weight:700;color:#ef4444;">{sb.get('critical', 0)}</div>
                  <div style="font-size:11px;color:#94a3b8;margin-top:4px;">CRITICAL</div>
                </td>
                <td style="width:8px;"></td>
                <td style="padding:12px;background:#1e293b;border-radius:8px;text-align:center;width:25%;">
                  <div style="font-size:28px;font-weight:700;color:#f97316;">{sb.get('high', 0)}</div>
                  <div style="font-size:11px;color:#94a3b8;margin-top:4px;">HIGH</div>
                </td>
                <td style="width:8px;"></td>
                <td style="padding:12px;background:#1e293b;border-radius:8px;text-align:center;width:25%;">
                  <div style="font-size:28px;font-weight:700;color:#eab308;">{sb.get('moderate', 0) + sb.get('low', 0)}</div>
                  <div style="font-size:11px;color:#94a3b8;margin-top:4px;">OTHER</div>
                </td>
              </tr>
            </table>
            <h2 style="color:#e2e8f0;font-size:16px;margin:20px 0 12px;">New Vulnerabilities</h2>
            <table style="width:100%;border-collapse:collapse;background:#1e293b;border-radius:8px;overflow:hidden;">
              <thead>
                <tr style="background:#334155;">
                  <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-size:11px;font-weight:600;">SEVERITY</th>
                  <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-size:11px;font-weight:600;">PACKAGE</th>
                  <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-size:11px;font-weight:600;">ISSUE</th>
                  <th style="padding:10px 12px;text-align:left;color:#94a3b8;font-size:11px;font-weight:600;">STACK</th>
                </tr>
              </thead>
              <tbody style="color:#e2e8f0;font-size:13px;">{vuln_rows}</tbody>
            </table>
            {f'<p style="color:#94a3b8;font-size:12px;margin-top:8px;">Showing first 20 of {len(alerts)} vulnerabilities.</p>' if len(alerts) > 20 else ''}
            <p style="color:#64748b;font-size:12px;margin-top:24px;text-align:center;">
              Sent by CVE Monitor at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
            </p>
          </div>
        </div>"""

    async def _send_alert_email(self, alerts: List[Dict[str, Any]], scan_result: Dict[str, Any], recipient: str):
        if not resend.api_key:
            logger.warning("Resend API key not configured, skipping email")
            return {"sent": False, "error": "No API key"}
        try:
            html = self._build_alert_html(alerts, scan_result)
            critical_count = sum(1 for a in alerts if a["severity"] == "critical")
            high_count = sum(1 for a in alerts if a["severity"] == "high")
            subject = f"[CVE Alert] {len(alerts)} new vulnerabilities detected"
            if critical_count:
                subject = f"[CRITICAL] {critical_count} critical CVEs detected"
            elif high_count:
                subject = f"[HIGH] {high_count} high-severity CVEs detected"

            params = {
                "from": SENDER_EMAIL,
                "to": [recipient],
                "subject": subject,
                "html": html,
            }
            result = await asyncio.to_thread(resend.Emails.send, params)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", str(result))
            logger.info(f"CVE alert email sent to {recipient}, id={email_id}")

            # Log the notification
            await self.alerts_col.insert_one({
                "type": "email_notification",
                "severity": "info",
                "module": "Email",
                "title": f"Alert email sent to {recipient}",
                "description": f"Notified about {len(alerts)} new vulnerabilities (id: {email_id})",
                "url": "",
                "stack": "system",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "read": True,
                "dismissed": False,
            })
            return {"sent": True, "email_id": email_id}
        except Exception as e:
            logger.error(f"Failed to send CVE alert email: {e}")
            return {"sent": False, "error": str(e)}

    async def send_test_email(self, recipient: str = "") -> Dict[str, Any]:
        """Send a test email to verify Resend integration."""
        to = recipient or DEFAULT_ALERT_EMAIL
        if not to:
            return {"sent": False, "error": "No recipient email configured"}
        if not resend.api_key:
            return {"sent": False, "error": "Resend API key not configured"}

        html = """
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:640px;margin:0 auto;background:#0f172a;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:24px 32px;">
            <h1 style="color:#fff;margin:0;font-size:22px;">CVE Monitor - Test Email</h1>
            <p style="color:#c7d2fe;margin:8px 0 0;font-size:14px;">Big Mann Entertainment</p>
          </div>
          <div style="padding:24px 32px;">
            <div style="background:#1e293b;border-radius:8px;padding:20px;text-align:center;">
              <div style="font-size:48px;margin-bottom:12px;">&#9989;</div>
              <h2 style="color:#34d399;margin:0 0 8px;">Email Notifications Working</h2>
              <p style="color:#94a3b8;font-size:14px;margin:0;">Your CVE Monitor email alerts are configured correctly. You will receive notifications when new vulnerabilities are detected.</p>
            </div>
            <p style="color:#64748b;font-size:12px;margin-top:24px;text-align:center;">
              Sent at """ + datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC') + """
            </p>
          </div>
        </div>"""

        try:
            params = {
                "from": SENDER_EMAIL,
                "to": [to],
                "subject": "[CVE Monitor] Test Notification - Email Working",
                "html": html,
            }
            result = await asyncio.to_thread(resend.Emails.send, params)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", str(result))
            logger.info(f"Test email sent to {to}, id={email_id}")
            return {"sent": True, "email_id": email_id, "recipient": to}
        except Exception as e:
            logger.error(f"Test email failed: {e}")
            return {"sent": False, "error": str(e)}

    async def get_alerts(self, limit: int = 50, unread_only: bool = False) -> List[Dict[str, Any]]:
        query = {"dismissed": False}
        if unread_only:
            query["read"] = False
        cursor = self.alerts_col.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_alert_count(self) -> Dict[str, int]:
        unread = await self.alerts_col.count_documents({"read": False, "dismissed": False})
        total = await self.alerts_col.count_documents({"dismissed": False})
        return {"unread": unread, "total": total}

    async def mark_alerts_read(self, alert_ids: Optional[List[str]] = None) -> int:
        if alert_ids:
            result = await self.alerts_col.update_many(
                {"timestamp": {"$in": alert_ids}, "read": False},
                {"$set": {"read": True}},
            )
        else:
            result = await self.alerts_col.update_many(
                {"read": False},
                {"$set": {"read": True}},
            )
        return result.modified_count

    async def dismiss_alerts(self, alert_ids: Optional[List[str]] = None) -> int:
        if alert_ids:
            result = await self.alerts_col.update_many(
                {"timestamp": {"$in": alert_ids}},
                {"$set": {"dismissed": True}},
            )
        else:
            result = await self.alerts_col.update_many(
                {},
                {"$set": {"dismissed": True}},
            )
        return result.modified_count

    # ─── Core Audit Methods ────────────────────────────────────────

    async def run_frontend_audit(self) -> Dict[str, Any]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "yarn", "audit", "--json",
                cwd=FRONTEND_DIR,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            return self._parse_yarn_audit(stdout.decode("utf-8", errors="replace"))
        except asyncio.TimeoutError:
            return {"error": "Frontend audit timed out", "vulnerabilities": [], "summary": {}}
        except Exception as e:
            return {"error": str(e), "vulnerabilities": [], "summary": {}}

    def _parse_yarn_audit(self, raw: str) -> Dict[str, Any]:
        vulnerabilities: List[Dict[str, Any]] = []
        summary: Dict[str, Any] = {}

        for line in raw.strip().splitlines():
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "auditAdvisory":
                    adv = data["data"]["advisory"]
                    vulnerabilities.append({
                        "module": adv.get("module_name", "unknown"),
                        "severity": adv.get("severity", "unknown"),
                        "title": adv.get("title", ""),
                        "url": adv.get("url", ""),
                        "patched_versions": adv.get("patched_versions", ""),
                        "vulnerable_versions": adv.get("vulnerable_versions", ""),
                        "cwe": adv.get("cwe", ""),
                        "recommendation": adv.get("recommendation", ""),
                    })
                elif data.get("type") == "auditSummary":
                    s = data["data"]
                    summary = {
                        "total_dependencies": s.get("totalDependencies", 0),
                        "vulnerabilities": s.get("vulnerabilities", {}),
                    }
            except (json.JSONDecodeError, KeyError):
                continue

        seen = set()
        unique = []
        for v in vulnerabilities:
            key = f"{v['module']}|{v['title']}"
            if key not in seen:
                seen.add(key)
                unique.append(v)

        sev_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3, "info": 4}
        unique.sort(key=lambda x: sev_order.get(x["severity"], 5))

        return {"vulnerabilities": unique, "summary": summary}

    async def run_backend_audit(self) -> Dict[str, Any]:
        pip_audit_path = "/root/.venv/bin/pip-audit"
        try:
            proc = await asyncio.create_subprocess_exec(
                pip_audit_path, "--format", "json", "--progress-spinner", "off",
                cwd=BACKEND_DIR,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            return self._parse_pip_audit(stdout.decode("utf-8", errors="replace"))
        except FileNotFoundError:
            return await self._run_safety_check()
        except asyncio.TimeoutError:
            return {"error": "Backend audit timed out", "vulnerabilities": [], "summary": {}}
        except Exception as e:
            return {"error": str(e), "vulnerabilities": [], "summary": {}}

    def _parse_pip_audit(self, raw: str) -> Dict[str, Any]:
        vulnerabilities: List[Dict[str, Any]] = []
        try:
            data = json.loads(raw)
            deps = data if isinstance(data, list) else data.get("dependencies", [])
            for dep in deps:
                for vuln in dep.get("vulns", []):
                    vulnerabilities.append({
                        "module": dep.get("name", "unknown"),
                        "installed_version": dep.get("version", "unknown"),
                        "severity": vuln.get("fix_versions", ["unknown"])[0] if vuln.get("fix_versions") else "unknown",
                        "title": vuln.get("id", ""),
                        "description": vuln.get("description", ""),
                        "url": f"https://osv.dev/vulnerability/{vuln.get('id', '')}",
                        "fix_versions": vuln.get("fix_versions", []),
                    })
        except (json.JSONDecodeError, KeyError):
            pass

        return {
            "vulnerabilities": vulnerabilities,
            "summary": {"total_vulnerabilities": len(vulnerabilities)},
        }

    async def _run_safety_check(self) -> Dict[str, Any]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "safety", "check", "--json",
                cwd=BACKEND_DIR,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            raw = stdout.decode("utf-8", errors="replace")
            vulns = []
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, list) and len(item) >= 5:
                            vulns.append({
                                "module": item[0],
                                "installed_version": item[2],
                                "severity": "unknown",
                                "title": item[4],
                                "url": "",
                                "fix_versions": [],
                            })
            except json.JSONDecodeError:
                pass
            return {"vulnerabilities": vulns, "summary": {"total_vulnerabilities": len(vulns)}}
        except Exception:
            return {
                "vulnerabilities": [],
                "summary": {"total_vulnerabilities": 0},
                "note": "Neither pip-audit nor safety installed. Install with: pip install pip-audit",
            }

    async def run_full_audit(self, force: bool = False, is_scheduled: bool = False) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)

        if not force and self._cache and self._cache_time:
            age = (now - self._cache_time).total_seconds()
            if age < self._cache_ttl:
                return {**self._cache, "cached": True, "cache_age_seconds": int(age)}

        frontend_result, backend_result = await asyncio.gather(
            self.run_frontend_audit(),
            self.run_backend_audit(),
        )

        fe_vulns = frontend_result.get("vulnerabilities", [])
        be_vulns = backend_result.get("vulnerabilities", [])
        fe_summary = frontend_result.get("summary", {})
        fe_vuln_counts = fe_summary.get("vulnerabilities", {})

        total_critical = fe_vuln_counts.get("critical", 0)
        total_high = fe_vuln_counts.get("high", 0)
        total_moderate = fe_vuln_counts.get("moderate", 0)
        total_low = fe_vuln_counts.get("low", 0)

        for v in be_vulns:
            sev = v.get("severity", "").lower()
            if sev == "critical":
                total_critical += 1
            elif sev == "high":
                total_high += 1
            elif sev in ("moderate", "medium"):
                total_moderate += 1
            else:
                total_low += 1

        total_vulns = len(fe_vulns) + len(be_vulns)
        score = 100
        score -= total_critical * 25
        score -= total_high * 15
        score -= total_moderate * 5
        score -= total_low * 1
        score = max(0, score)

        if score >= 90:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 60:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"

        # Build vulnerability signatures for diff detection
        vuln_sigs = [f"{v.get('module', '')}|{v.get('title', '')}" for v in fe_vulns + be_vulns]

        result = {
            "timestamp": now.isoformat(),
            "security_score": score,
            "grade": grade,
            "total_dependencies": fe_summary.get("total_dependencies", 0),
            "total_vulnerabilities": total_vulns,
            "severity_breakdown": {
                "critical": total_critical,
                "high": total_high,
                "moderate": total_moderate,
                "low": total_low,
            },
            "frontend": {
                "vulnerabilities": fe_vulns,
                "total_dependencies": fe_summary.get("total_dependencies", 0),
                "vulnerability_counts": fe_vuln_counts,
            },
            "backend": {
                "vulnerabilities": be_vulns,
                "total_vulnerabilities": len(be_vulns),
                "note": backend_result.get("note", ""),
            },
            "cached": False,
        }

        audit_record = {
            "timestamp": now.isoformat(),
            "security_score": score,
            "grade": grade,
            "total_vulnerabilities": total_vulns,
            "severity_breakdown": result["severity_breakdown"],
            "frontend_vuln_count": len(fe_vulns),
            "backend_vuln_count": len(be_vulns),
            "total_dependencies": fe_summary.get("total_dependencies", 0),
            "is_scheduled": is_scheduled,
            "vuln_signatures": vuln_sigs,
        }
        await self.audits_col.insert_one(audit_record)

        self._cache = result
        self._cache_time = now

        return result

    async def get_audit_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = self.audits_col.find(
            {}, {"_id": 0, "vuln_signatures": 0}
        ).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_trend_data(self, days: int = 30) -> List[Dict[str, Any]]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        cursor = self.audits_col.find(
            {"timestamp": {"$gte": cutoff}},
            {"_id": 0, "vuln_signatures": 0},
        ).sort("timestamp", 1)
        return await cursor.to_list(length=500)
