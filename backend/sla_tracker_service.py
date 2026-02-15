"""
SLA Tracker Service - Enhanced SLA Tracking (Phase 2)
Provides live countdown timers, escalation chains, SLA history, at-risk CVE tracking,
proactive notifications, auto-escalation scheduling, and escalation workflows.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

import resend
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("sla_tracker_service")

resend.api_key = os.environ.get("RESEND_API_KEY", "")
SLA_SENDER_EMAIL = "onboarding@resend.dev"

SEVERITY_SLA_DEFAULTS = {"critical": 24, "high": 72, "medium": 168, "low": 720}

DEFAULT_ESCALATION_RULES = [
    {
        "id": "esc-l1",
        "level": 1,
        "name": "L1 - Team Lead",
        "threshold_pct": 75,
        "action": "notify",
        "notify_role": "manager",
        "description": "Alert team lead when 75% of SLA window has elapsed",
    },
    {
        "id": "esc-l2",
        "level": 2,
        "name": "L2 - Security Manager",
        "threshold_pct": 100,
        "action": "escalate",
        "notify_role": "admin",
        "description": "Escalate to security manager on SLA breach",
    },
    {
        "id": "esc-l3",
        "level": 3,
        "name": "L3 - CISO / Executive",
        "threshold_pct": 150,
        "action": "escalate",
        "notify_role": "admin",
        "description": "Executive escalation when 150% overdue",
    },
]

_sla_tracker_instance = None


def get_sla_tracker_service():
    global _sla_tracker_instance
    if _sla_tracker_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _sla_tracker_instance = SLATrackerService(db)
    return _sla_tracker_instance


def initialize_sla_tracker_service(db):
    global _sla_tracker_instance
    _sla_tracker_instance = SLATrackerService(db)
    return _sla_tracker_instance


class SLATrackerService:
    def __init__(self, db):
        self.db = db
        self.cves_col = db["cve_entries"]
        self.policies_col = db["cve_severity_policies"]
        self.escalation_rules_col = db["cve_escalation_rules"]
        self.escalation_log_col = db["cve_escalation_log"]
        self.sla_snapshots_col = db["cve_sla_snapshots"]
        self.notifications_col = db["cve_notifications"]
        self.sla_config_col = db["cve_sla_config"]
        self._auto_task: Optional[asyncio.Task] = None

    async def _get_sla_hours(self) -> Dict[str, int]:
        """Get SLA hours per severity from policies or defaults."""
        sla_map = dict(SEVERITY_SLA_DEFAULTS)
        async for doc in self.policies_col.find({}, {"_id": 0}):
            sev = doc.get("severity")
            if sev and "sla_hours" in doc:
                sla_map[sev] = doc["sla_hours"]
        return sla_map

    async def get_sla_dashboard(self) -> Dict[str, Any]:
        """Main SLA dashboard with per-severity stats and overall health."""
        now = datetime.now(timezone.utc)
        sla_map = await self._get_sla_hours()

        open_cves = []
        cursor = self.cves_col.find(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}}, {"_id": 0}
        )
        async for doc in cursor:
            open_cves.append(doc)

        severity_stats = {}
        total_within = 0
        total_warning = 0
        total_breached = 0

        for sev in ["critical", "high", "medium", "low"]:
            sla_hours = sla_map.get(sev, 168)
            sev_cves = [c for c in open_cves if c.get("severity") == sev]

            within = 0
            warning = 0
            breached = 0

            for cve in sev_cves:
                detected_str = cve.get("detected_at") or cve.get("created_at", "")
                if not detected_str:
                    within += 1
                    continue
                try:
                    detected_at = datetime.fromisoformat(detected_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    within += 1
                    continue

                elapsed_h = (now - detected_at).total_seconds() / 3600
                pct = (elapsed_h / sla_hours * 100) if sla_hours else 0

                if pct >= 100:
                    breached += 1
                elif pct >= 75:
                    warning += 1
                else:
                    within += 1

            total_within += within
            total_warning += warning
            total_breached += breached

            compliance = round(((within + warning) / len(sev_cves) * 100) if sev_cves else 100, 1)
            severity_stats[sev] = {
                "sla_hours": sla_hours,
                "total": len(sev_cves),
                "within_sla": within,
                "warning": warning,
                "breached": breached,
                "compliance_pct": compliance,
            }

        total_open = total_within + total_warning + total_breached
        overall_compliance = round(
            ((total_within + total_warning) / total_open * 100) if total_open else 100, 1
        )

        return {
            "overall_compliance": overall_compliance,
            "total_open": total_open,
            "total_within_sla": total_within,
            "total_warning": total_warning,
            "total_breached": total_breached,
            "severity_stats": severity_stats,
            "generated_at": now.isoformat(),
        }

    async def get_at_risk_cves(self, limit: int = 50) -> Dict[str, Any]:
        """Get CVEs that are approaching or have breached SLA, sorted by urgency."""
        now = datetime.now(timezone.utc)
        sla_map = await self._get_sla_hours()

        open_cves = []
        cursor = self.cves_col.find(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}}, {"_id": 0}
        )
        async for doc in cursor:
            open_cves.append(doc)

        at_risk = []
        for cve in open_cves:
            severity = cve.get("severity", "medium")
            sla_hours = sla_map.get(severity, 168)
            if sla_hours == 0:
                continue

            detected_str = cve.get("detected_at") or cve.get("created_at", "")
            if not detected_str:
                continue
            try:
                detected_at = datetime.fromisoformat(detected_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue

            elapsed_h = (now - detected_at).total_seconds() / 3600
            pct = (elapsed_h / sla_hours * 100) if sla_hours else 0
            remaining_h = max(0, sla_hours - elapsed_h)
            overdue_h = max(0, elapsed_h - sla_hours)

            if pct < 50:
                continue

            status = "breached" if pct >= 100 else "warning" if pct >= 75 else "approaching"

            # Determine escalation level
            escalation_level = 0
            if pct >= 150:
                escalation_level = 3
            elif pct >= 100:
                escalation_level = 2
            elif pct >= 75:
                escalation_level = 1

            at_risk.append({
                "cve_id": cve.get("cve_id", cve.get("id", "")),
                "title": cve.get("title", ""),
                "severity": severity,
                "status": cve.get("status", ""),
                "sla_status": status,
                "sla_hours": sla_hours,
                "elapsed_hours": round(elapsed_h, 1),
                "remaining_hours": round(remaining_h, 1),
                "overdue_hours": round(overdue_h, 1),
                "percent_elapsed": round(pct, 1),
                "escalation_level": escalation_level,
                "assigned_to": cve.get("assigned_to", ""),
                "assigned_team": cve.get("assigned_team", ""),
                "detected_at": detected_str,
                "deadline": (detected_at + timedelta(hours=sla_hours)).isoformat(),
            })

        at_risk.sort(key=lambda x: -x["percent_elapsed"])
        return {"items": at_risk[:limit], "total": len(at_risk)}

    async def get_escalation_rules(self) -> Dict[str, Any]:
        """Get escalation rules configuration."""
        rules = []
        async for doc in self.escalation_rules_col.find({}, {"_id": 0}).sort("level", 1):
            rules.append(doc)

        if not rules:
            rules = list(DEFAULT_ESCALATION_RULES)
            for r in rules:
                await self.escalation_rules_col.update_one(
                    {"id": r["id"]}, {"$set": r}, upsert=True
                )

        return {"rules": rules}

    async def update_escalation_rules(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update escalation rules."""
        saved = []
        for r in rules:
            if "id" not in r:
                r["id"] = f"esc-{str(uuid.uuid4())[:8]}"
            r["updated_at"] = datetime.now(timezone.utc).isoformat()
            await self.escalation_rules_col.update_one(
                {"id": r["id"]}, {"$set": r}, upsert=True
            )
            saved.append({k: v for k, v in r.items() if k != "_id"})

        # Remove rules not in the update
        rule_ids = [r["id"] for r in saved]
        await self.escalation_rules_col.delete_many({"id": {"$nin": rule_ids}})

        return {"rules": saved}

    async def run_escalations(self) -> Dict[str, Any]:
        """Check at-risk CVEs and create escalation notifications per rules."""
        now = datetime.now(timezone.utc)
        rules_data = await self.get_escalation_rules()
        rules = sorted(rules_data["rules"], key=lambda r: r.get("level", 0))

        at_risk_data = await self.get_at_risk_cves(limit=200)
        at_risk = at_risk_data["items"]

        escalations_created = 0
        for cve_item in at_risk:
            pct = cve_item["percent_elapsed"]
            for rule in rules:
                threshold = rule.get("threshold_pct", 100)
                if pct >= threshold:
                    log_key = f"{cve_item['cve_id']}:{rule['id']}"
                    existing = await self.escalation_log_col.find_one({"log_key": log_key})
                    if existing:
                        continue

                    log_entry = {
                        "id": str(uuid.uuid4()),
                        "log_key": log_key,
                        "cve_id": cve_item["cve_id"],
                        "rule_id": rule["id"],
                        "rule_name": rule.get("name", ""),
                        "level": rule.get("level", 0),
                        "threshold_pct": threshold,
                        "actual_pct": round(pct, 1),
                        "severity": cve_item["severity"],
                        "action": rule.get("action", "notify"),
                        "created_at": now.isoformat(),
                    }
                    await self.escalation_log_col.insert_one({**log_entry, "_id": log_entry["id"]})

                    notif = {
                        "id": str(uuid.uuid4()),
                        "type": "sla_breach" if pct >= 100 else "sla_warning",
                        "title": f"Escalation L{rule.get('level', 0)}: {cve_item['cve_id']}",
                        "message": f"{rule.get('name', '')} — {cve_item['title']} ({cve_item['severity'].upper()}) is at {round(pct, 1)}% of SLA ({cve_item['sla_hours']}h)",
                        "severity": cve_item["severity"],
                        "cve_id": cve_item["cve_id"],
                        "metadata": {
                            "escalation_level": rule.get("level", 0),
                            "rule_name": rule.get("name", ""),
                            "percent_elapsed": round(pct, 1),
                        },
                        "read": False,
                        "dismissed": False,
                        "email_sent": False,
                        "created_at": now.isoformat(),
                    }
                    await self.notifications_col.insert_one({**notif, "_id": notif["id"]})
                    escalations_created += 1

        return {
            "checked": len(at_risk),
            "escalations_created": escalations_created,
            "rules_applied": len(rules),
        }

    async def get_escalation_log(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent escalation log entries."""
        items = []
        cursor = (
            self.escalation_log_col.find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
        async for doc in cursor:
            items.append(doc)
        total = await self.escalation_log_col.count_documents({})
        return {"items": items, "total": total}

    async def get_sla_history(self, days: int = 30) -> Dict[str, Any]:
        """Get SLA compliance history from snapshots."""
        snapshots = []
        cursor = (
            self.sla_snapshots_col.find({}, {"_id": 0})
            .sort("date", -1)
            .limit(days)
        )
        async for doc in cursor:
            snapshots.append(doc)

        snapshots.reverse()

        if not snapshots:
            snapshots = await self._generate_sla_history(days)

        return {"history": snapshots, "period_days": days}

    async def _generate_sla_history(self, days: int) -> List[Dict[str, Any]]:
        """Generate SLA history snapshots on-the-fly from CVE data."""
        now = datetime.now(timezone.utc)
        sla_map = await self._get_sla_hours()
        history = []

        for i in range(days, -1, -1):
            day = now - timedelta(days=i)
            day_iso = day.replace(hour=23, minute=59, second=59).isoformat()

            total_open = await self.cves_col.count_documents({
                "status": {"$in": ["detected", "triaged", "in_progress"]},
                "created_at": {"$lte": day_iso},
            })

            total_breached = 0
            for sev in ["critical", "high", "medium", "low"]:
                sla_hours = sla_map.get(sev, 168)
                cutoff = (day - timedelta(hours=sla_hours)).isoformat()
                breached = await self.cves_col.count_documents({
                    "severity": sev,
                    "status": {"$in": ["detected", "triaged", "in_progress"]},
                    "created_at": {"$lte": cutoff},
                })
                total_breached += breached

            compliance = round(
                ((total_open - total_breached) / total_open * 100) if total_open > 0 else 100, 1
            )

            entry = {
                "date": day.strftime("%Y-%m-%d"),
                "label": day.strftime("%b %d"),
                "total_open": total_open,
                "breached": total_breached,
                "compliance_pct": compliance,
            }
            history.append(entry)

        return history

    async def take_snapshot(self) -> Dict[str, Any]:
        """Take a point-in-time SLA compliance snapshot for history tracking."""
        now = datetime.now(timezone.utc)
        dashboard = await self.get_sla_dashboard()

        snapshot = {
            "id": str(uuid.uuid4()),
            "date": now.strftime("%Y-%m-%d"),
            "label": now.strftime("%b %d"),
            "total_open": dashboard["total_open"],
            "breached": dashboard["total_breached"],
            "warning": dashboard["total_warning"],
            "compliance_pct": dashboard["overall_compliance"],
            "severity_stats": dashboard["severity_stats"],
            "created_at": now.isoformat(),
        }

        await self.sla_snapshots_col.update_one(
            {"date": snapshot["date"]}, {"$set": snapshot}, upsert=True
        )

        return snapshot
