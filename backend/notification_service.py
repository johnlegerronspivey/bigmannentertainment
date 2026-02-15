"""
Notification Service - Phase 5: Notifications & Reporting
Manages in-app notifications, email alerts (Resend), SLA monitoring, and report exports.
"""

import asyncio
import csv
import io
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

import resend
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("notification_service")

resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = "onboarding@resend.dev"
DEFAULT_ALERT_EMAIL = os.environ.get("CVE_ALERT_EMAIL", "")

SEVERITY_SLA_HOURS = {
    "critical": 24,
    "high": 72,
    "medium": 336,
    "low": 720,
    "info": 0,
}

NOTIFICATION_TYPES = [
    "new_cve",
    "cve_assigned",
    "sla_warning",
    "sla_breach",
    "status_change",
    "remediation_update",
    "scan_complete",
    "weekly_digest",
]

_notification_instance = None


def get_notification_service():
    global _notification_instance
    if _notification_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _notification_instance = NotificationService(db)
    return _notification_instance


def initialize_notification_service(db):
    global _notification_instance
    _notification_instance = NotificationService(db)
    return _notification_instance


class NotificationService:
    def __init__(self, db):
        self.db = db
        self.notifications_col = db["cve_notifications"]
        self.preferences_col = db["cve_notification_preferences"]
        self.cves_col = db["cve_entries"]
        self.policies_col = db["cve_severity_policies"]
        self.remediation_col = db["cve_remediation_items"]
        self.services_col = db["cve_services"]
        self.scan_results_col = db["cve_scan_results"]

    # ─── Create Notification ──────────────────────────────────
    async def create_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        severity: str = "info",
        cve_id: str = "",
        metadata: Optional[Dict] = None,
        send_email: bool = False,
    ) -> Dict[str, Any]:
        notif = {
            "id": str(uuid.uuid4()),
            "type": notification_type,
            "title": title,
            "message": message,
            "severity": severity,
            "cve_id": cve_id,
            "metadata": metadata or {},
            "read": False,
            "dismissed": False,
            "email_sent": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        await self.notifications_col.insert_one({**notif, "_id": notif["id"]})

        if send_email:
            prefs = await self._get_preferences()
            should_email = prefs.get("email_enabled", True)
            type_prefs = prefs.get("email_types", {})
            if should_email and type_prefs.get(notification_type, True):
                email_result = await self._send_notification_email(notif)
                if email_result.get("sent"):
                    await self.notifications_col.update_one(
                        {"id": notif["id"]}, {"$set": {"email_sent": True}}
                    )

        return {k: v for k, v in notif.items() if k != "_id"}

    # ─── List Notifications ───────────────────────────────────
    async def list_notifications(
        self,
        page: int = 1,
        limit: int = 50,
        unread_only: bool = False,
        notification_type: str = "",
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {"dismissed": {"$ne": True}}
        if unread_only:
            query["read"] = False
        if notification_type:
            query["type"] = notification_type

        total = await self.notifications_col.count_documents(query)
        skip = (page - 1) * limit
        items = []
        cursor = (
            self.notifications_col.find(query, {"_id": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        async for doc in cursor:
            items.append(doc)

        return {
            "notifications": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": max(1, (total + limit - 1) // limit),
        }

    # ─── Unread Count ─────────────────────────────────────────
    async def get_unread_count(self) -> Dict[str, Any]:
        total_unread = await self.notifications_col.count_documents(
            {"read": False, "dismissed": {"$ne": True}}
        )
        by_type: Dict[str, int] = {}
        for ntype in NOTIFICATION_TYPES:
            count = await self.notifications_col.count_documents(
                {"read": False, "dismissed": {"$ne": True}, "type": ntype}
            )
            if count > 0:
                by_type[ntype] = count
        return {"unread": total_unread, "by_type": by_type}

    # ─── Mark Read ────────────────────────────────────────────
    async def mark_read(self, notification_id: str) -> Dict[str, Any]:
        result = await self.notifications_col.update_one(
            {"id": notification_id}, {"$set": {"read": True}}
        )
        if result.modified_count == 0:
            return {"success": False, "error": "Notification not found"}
        return {"success": True}

    async def mark_all_read(self) -> Dict[str, Any]:
        result = await self.notifications_col.update_many(
            {"read": False}, {"$set": {"read": True}}
        )
        return {"success": True, "marked": result.modified_count}

    # ─── Dismiss ──────────────────────────────────────────────
    async def dismiss_notification(self, notification_id: str) -> Dict[str, Any]:
        result = await self.notifications_col.update_one(
            {"id": notification_id}, {"$set": {"dismissed": True, "read": True}}
        )
        if result.modified_count == 0:
            return {"success": False, "error": "Notification not found"}
        return {"success": True}

    # ─── SLA Check ────────────────────────────────────────────
    async def check_sla_compliance(self) -> Dict[str, Any]:
        """Check all open CVEs for SLA warnings (75% elapsed) and breaches."""
        now = datetime.now(timezone.utc)
        policies = {}
        async for doc in self.policies_col.find({}, {"_id": 0}):
            policies[doc.get("severity")] = doc.get("sla_hours", SEVERITY_SLA_HOURS.get(doc.get("severity"), 0))

        open_cves = []
        cursor = self.cves_col.find(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}}, {"_id": 0}
        )
        async for doc in cursor:
            open_cves.append(doc)

        warnings = []
        breaches = []
        for cve in open_cves:
            severity = cve.get("severity", "medium")
            sla_hours = policies.get(severity, SEVERITY_SLA_HOURS.get(severity, 0))
            if sla_hours == 0:
                continue

            detected_str = cve.get("detected_at") or cve.get("created_at", "")
            if not detected_str:
                continue
            try:
                detected_at = datetime.fromisoformat(detected_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue

            elapsed = (now - detected_at).total_seconds() / 3600
            pct = (elapsed / sla_hours) * 100 if sla_hours else 0

            if pct >= 100:
                breaches.append({
                    "cve_id": cve.get("cve_id", cve.get("id", "")),
                    "title": cve.get("title", ""),
                    "severity": severity,
                    "sla_hours": sla_hours,
                    "elapsed_hours": round(elapsed, 1),
                    "overdue_hours": round(elapsed - sla_hours, 1),
                })
            elif pct >= 75:
                warnings.append({
                    "cve_id": cve.get("cve_id", cve.get("id", "")),
                    "title": cve.get("title", ""),
                    "severity": severity,
                    "sla_hours": sla_hours,
                    "elapsed_hours": round(elapsed, 1),
                    "remaining_hours": round(sla_hours - elapsed, 1),
                    "percent_elapsed": round(pct, 1),
                })

        # Create notifications for breaches
        for b in breaches:
            existing = await self.notifications_col.find_one(
                {"type": "sla_breach", "cve_id": b["cve_id"], "dismissed": {"$ne": True}}
            )
            if not existing:
                await self.create_notification(
                    notification_type="sla_breach",
                    title=f"SLA Breach: {b['cve_id']}",
                    message=f"{b['title']} — {b['severity'].upper()} severity overdue by {b['overdue_hours']}h (SLA: {b['sla_hours']}h)",
                    severity=b["severity"],
                    cve_id=b["cve_id"],
                    metadata=b,
                    send_email=True,
                )

        # Create notifications for warnings
        for w in warnings:
            existing = await self.notifications_col.find_one(
                {"type": "sla_warning", "cve_id": w["cve_id"], "dismissed": {"$ne": True}}
            )
            if not existing:
                await self.create_notification(
                    notification_type="sla_warning",
                    title=f"SLA Warning: {w['cve_id']}",
                    message=f"{w['title']} — {w['percent_elapsed']}% of SLA elapsed, {w['remaining_hours']}h remaining",
                    severity=w["severity"],
                    cve_id=w["cve_id"],
                    metadata=w,
                    send_email=False,
                )

        return {
            "checked": len(open_cves),
            "warnings": len(warnings),
            "breaches": len(breaches),
            "warning_details": warnings,
            "breach_details": breaches,
        }

    # ─── Preferences ──────────────────────────────────────────
    async def _get_preferences(self) -> Dict[str, Any]:
        prefs = await self.preferences_col.find_one({"id": "default"}, {"_id": 0})
        if not prefs:
            prefs = {
                "id": "default",
                "email_enabled": True,
                "email_recipient": DEFAULT_ALERT_EMAIL,
                "email_types": {t: True for t in NOTIFICATION_TYPES},
                "sla_warning_threshold": 75,
            }
        return prefs

    async def get_preferences(self) -> Dict[str, Any]:
        return await self._get_preferences()

    async def update_preferences(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        current = await self._get_preferences()
        current.update(updates)
        current["id"] = "default"
        await self.preferences_col.update_one(
            {"id": "default"}, {"$set": current}, upsert=True
        )
        return {k: v for k, v in current.items() if k != "_id"}

    # ─── Email Sending ────────────────────────────────────────
    async def _send_notification_email(self, notif: Dict[str, Any]) -> Dict[str, Any]:
        if not resend.api_key:
            logger.warning("Resend API key not configured")
            return {"sent": False, "error": "No API key"}

        prefs = await self._get_preferences()
        recipient = prefs.get("email_recipient", DEFAULT_ALERT_EMAIL)
        if not recipient:
            return {"sent": False, "error": "No recipient configured"}

        severity_colors = {
            "critical": "#ef4444", "high": "#f97316",
            "medium": "#eab308", "low": "#3b82f6", "info": "#64748b",
        }
        color = severity_colors.get(notif.get("severity", "info"), "#64748b")

        html = f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:640px;margin:0 auto;background:#0f172a;border-radius:12px;overflow:hidden;">
          <div style="background:{color};padding:20px 32px;">
            <h1 style="color:#fff;margin:0;font-size:20px;">{notif['title']}</h1>
            <p style="color:rgba(255,255,255,0.8);margin:6px 0 0;font-size:13px;">CVE Management Platform</p>
          </div>
          <div style="padding:24px 32px;">
            <div style="background:#1e293b;border-radius:8px;padding:16px;margin-bottom:16px;">
              <p style="color:#e2e8f0;margin:0;font-size:14px;line-height:1.6;">{notif['message']}</p>
            </div>
            <table style="width:100%;font-size:13px;color:#94a3b8;">
              <tr><td style="padding:4px 0;">Type:</td><td style="padding:4px 0;color:#e2e8f0;">{notif['type'].replace('_', ' ').title()}</td></tr>
              <tr><td style="padding:4px 0;">Severity:</td><td style="padding:4px 0;"><span style="color:{color};font-weight:600;">{notif.get('severity', 'info').upper()}</span></td></tr>
              {"<tr><td style='padding:4px 0;'>CVE:</td><td style='padding:4px 0;color:#e2e8f0;'>" + notif['cve_id'] + "</td></tr>" if notif.get('cve_id') else ""}
            </table>
            <p style="color:#475569;font-size:11px;margin-top:24px;text-align:center;">
              Sent at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by CVE Management Platform
            </p>
          </div>
        </div>"""

        try:
            params = {
                "from": SENDER_EMAIL,
                "to": [recipient],
                "subject": f"[CVE] {notif['title']}",
                "html": html,
            }
            result = await asyncio.to_thread(resend.Emails.send, params)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", str(result))
            logger.info(f"Notification email sent to {recipient}, id={email_id}")
            return {"sent": True, "email_id": email_id}
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")
            return {"sent": False, "error": str(e)}

    async def send_test_email(self, recipient: str = "") -> Dict[str, Any]:
        if not resend.api_key:
            return {"sent": False, "error": "Resend API key not configured"}
        to = recipient or DEFAULT_ALERT_EMAIL
        if not to:
            return {"sent": False, "error": "No recipient email"}
        html = """
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:640px;margin:0 auto;background:#0f172a;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(135deg,#06b6d4,#3b82f6);padding:20px 32px;">
            <h1 style="color:#fff;margin:0;font-size:20px;">CVE Notifications - Test Email</h1>
          </div>
          <div style="padding:24px 32px;text-align:center;">
            <div style="font-size:48px;margin-bottom:12px;">&#9989;</div>
            <h2 style="color:#34d399;margin:0 0 8px;">Email Notifications Working</h2>
            <p style="color:#94a3b8;font-size:14px;">You will receive CVE alerts, SLA warnings, and weekly digests.</p>
          </div>
        </div>"""
        try:
            params = {"from": SENDER_EMAIL, "to": [to], "subject": "[CVE] Test Notification", "html": html}
            result = await asyncio.to_thread(resend.Emails.send, params)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", str(result))
            return {"sent": True, "email_id": email_id, "recipient": to}
        except Exception as e:
            return {"sent": False, "error": str(e)}

    # ─── Weekly Digest ────────────────────────────────────────
    async def generate_weekly_digest(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        week_ago = (now - timedelta(days=7)).isoformat()

        new_cves = await self.cves_col.count_documents({"created_at": {"$gte": week_ago}})
        fixed_cves = await self.cves_col.count_documents({"fixed_at": {"$gte": week_ago}})
        open_cves = await self.cves_col.count_documents(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}}
        )
        critical_open = await self.cves_col.count_documents(
            {"severity": "critical", "status": {"$in": ["detected", "triaged", "in_progress"]}}
        )
        high_open = await self.cves_col.count_documents(
            {"severity": "high", "status": {"$in": ["detected", "triaged", "in_progress"]}}
        )

        sla_check = await self.check_sla_compliance()

        digest = {
            "period": f"{(now - timedelta(days=7)).strftime('%b %d')} - {now.strftime('%b %d, %Y')}",
            "new_cves": new_cves,
            "fixed_cves": fixed_cves,
            "open_cves": open_cves,
            "critical_open": critical_open,
            "high_open": high_open,
            "sla_warnings": sla_check["warnings"],
            "sla_breaches": sla_check["breaches"],
            "generated_at": now.isoformat(),
        }

        # Send digest email
        prefs = await self._get_preferences()
        if prefs.get("email_enabled") and prefs.get("email_types", {}).get("weekly_digest", True):
            await self._send_digest_email(digest)

        return digest

    async def _send_digest_email(self, digest: Dict[str, Any]) -> Dict[str, Any]:
        if not resend.api_key:
            return {"sent": False, "error": "No API key"}
        prefs = await self._get_preferences()
        recipient = prefs.get("email_recipient", DEFAULT_ALERT_EMAIL)
        if not recipient:
            return {"sent": False, "error": "No recipient"}

        html = f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:640px;margin:0 auto;background:#0f172a;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(135deg,#06b6d4,#8b5cf6);padding:20px 32px;">
            <h1 style="color:#fff;margin:0;font-size:20px;">Weekly Security Digest</h1>
            <p style="color:rgba(255,255,255,0.8);margin:6px 0 0;font-size:13px;">{digest['period']}</p>
          </div>
          <div style="padding:24px 32px;">
            <div style="display:flex;gap:12px;margin-bottom:20px;">
              <div style="flex:1;background:#1e293b;border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:28px;font-weight:700;color:#ef4444;">{digest['open_cves']}</div>
                <div style="font-size:12px;color:#94a3b8;">Open CVEs</div>
              </div>
              <div style="flex:1;background:#1e293b;border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:28px;font-weight:700;color:#f97316;">{digest['new_cves']}</div>
                <div style="font-size:12px;color:#94a3b8;">New This Week</div>
              </div>
              <div style="flex:1;background:#1e293b;border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:28px;font-weight:700;color:#34d399;">{digest['fixed_cves']}</div>
                <div style="font-size:12px;color:#94a3b8;">Fixed</div>
              </div>
            </div>
            <div style="background:#1e293b;border-radius:8px;padding:16px;margin-bottom:16px;">
              <h3 style="color:#e2e8f0;margin:0 0 8px;font-size:14px;">Risk Summary</h3>
              <p style="color:#94a3b8;margin:0;font-size:13px;">
                <span style="color:#ef4444;font-weight:600;">{digest['critical_open']}</span> critical &middot;
                <span style="color:#f97316;font-weight:600;">{digest['high_open']}</span> high severity open<br/>
                <span style="color:#eab308;font-weight:600;">{digest['sla_warnings']}</span> SLA warnings &middot;
                <span style="color:#ef4444;font-weight:600;">{digest['sla_breaches']}</span> SLA breaches
              </p>
            </div>
          </div>
        </div>"""

        try:
            params = {
                "from": SENDER_EMAIL,
                "to": [recipient],
                "subject": f"[CVE] Weekly Security Digest — {digest['period']}",
                "html": html,
            }
            result = await asyncio.to_thread(resend.Emails.send, params)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", str(result))
            return {"sent": True, "email_id": email_id}
        except Exception as e:
            return {"sent": False, "error": str(e)}

    # ─── CSV Export ───────────────────────────────────────────
    async def export_cves_csv(self, status_filter: str = "", severity_filter: str = "") -> str:
        query: Dict[str, Any] = {}
        if status_filter:
            query["status"] = status_filter
        if severity_filter:
            query["severity"] = severity_filter

        cves = []
        cursor = self.cves_col.find(query, {"_id": 0}).sort("created_at", -1)
        async for doc in cursor:
            cves.append(doc)

        output = io.StringIO()
        fieldnames = [
            "cve_id", "title", "severity", "status", "cvss_score",
            "affected_package", "affected_version", "fixed_version",
            "assigned_to", "assigned_team", "source",
            "detected_at", "created_at", "fixed_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for cve in cves:
            writer.writerow(cve)

        return output.getvalue()

    # ─── Governance Report Export ─────────────────────────────
    async def export_governance_csv(self) -> str:
        now = datetime.now(timezone.utc)
        thirty_days_ago = (now - timedelta(days=30)).isoformat()

        total = await self.cves_col.count_documents({})
        open_cves = await self.cves_col.count_documents(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}}
        )
        fixed = await self.cves_col.count_documents({"status": "fixed"})
        verified = await self.cves_col.count_documents({"status": "verified"})

        severity_data = {}
        for sev in ["critical", "high", "medium", "low", "info"]:
            severity_data[sev] = await self.cves_col.count_documents(
                {"severity": sev, "status": {"$in": ["detected", "triaged", "in_progress"]}}
            )

        new_30d = await self.cves_col.count_documents({"created_at": {"$gte": thirty_days_ago}})
        fixed_30d = await self.cves_col.count_documents({"fixed_at": {"$gte": thirty_days_ago}})

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["CVE Governance Report", now.strftime("%Y-%m-%d %H:%M UTC")])
        writer.writerow([])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total CVEs", total])
        writer.writerow(["Open CVEs", open_cves])
        writer.writerow(["Fixed CVEs", fixed])
        writer.writerow(["Verified CVEs", verified])
        writer.writerow(["New (Last 30 Days)", new_30d])
        writer.writerow(["Fixed (Last 30 Days)", fixed_30d])
        writer.writerow([])
        writer.writerow(["Open CVEs by Severity", ""])
        for sev, count in severity_data.items():
            writer.writerow([sev.upper(), count])

        return output.getvalue()
