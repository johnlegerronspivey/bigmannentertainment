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
        allowed = {"enabled", "interval_hours", "alert_on_critical", "alert_on_high", "alert_on_moderate", "alert_on_low"}
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
