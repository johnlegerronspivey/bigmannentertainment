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
                        "status": "open",
                        "acknowledged_by": "",
                        "acknowledged_at": "",
                        "assignee": "",
                        "assigned_by": "",
                        "assigned_at": "",
                        "resolved_by": "",
                        "resolved_at": "",
                        "resolution_note": "",
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

                    # Broadcast individual SLA event via WebSocket
                    try:
                        from sla_ws_manager import sla_ws_manager
                        if pct >= 100:
                            asyncio.ensure_future(sla_ws_manager.broadcast_breach(
                                cve_item["cve_id"], cve_item["severity"],
                                (pct - 100) * cve_item["sla_hours"] / 100
                            ))
                        else:
                            asyncio.ensure_future(sla_ws_manager.broadcast_warning(
                                cve_item["cve_id"], cve_item["severity"], pct
                            ))
                    except Exception:
                        pass

        result = {
            "checked": len(at_risk),
            "escalations_created": escalations_created,
            "rules_applied": len(rules),
        }

        # Broadcast escalation result via WebSocket
        try:
            from sla_ws_manager import sla_ws_manager
            asyncio.ensure_future(sla_ws_manager.broadcast_escalation(result))
        except Exception as e:
            logger.warning(f"SLA WS broadcast failed: {e}")

        return result

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

    # ─── SLA Policies CRUD ─────────────────────────────────────
    async def get_sla_policies(self) -> Dict[str, Any]:
        """Get SLA policy configuration per severity."""
        sla_map = await self._get_sla_hours()
        policies = []
        for sev in ["critical", "high", "medium", "low"]:
            doc = await self.policies_col.find_one({"severity": sev}, {"_id": 0})
            policies.append({
                "severity": sev,
                "sla_hours": sla_map.get(sev, SEVERITY_SLA_DEFAULTS.get(sev, 168)),
                "is_default": doc is None,
                "updated_at": doc.get("updated_at", "") if doc else "",
            })
        return {"policies": policies, "defaults": SEVERITY_SLA_DEFAULTS}

    async def update_sla_policies(self, policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update SLA hours per severity."""
        now = datetime.now(timezone.utc).isoformat()
        saved = []
        for p in policies:
            sev = p.get("severity")
            hours = p.get("sla_hours")
            if sev not in SEVERITY_SLA_DEFAULTS or not isinstance(hours, (int, float)) or hours < 1:
                continue
            await self.policies_col.update_one(
                {"severity": sev},
                {"$set": {"severity": sev, "sla_hours": int(hours), "updated_at": now}},
                upsert=True,
            )
            saved.append({"severity": sev, "sla_hours": int(hours), "updated_at": now, "is_default": False})
        return {"policies": saved}

    # ─── SLA Metrics & Analytics ──────────────────────────────
    async def get_sla_metrics(self) -> Dict[str, Any]:
        """Compute MTTR, resolution rates, breach analytics."""
        now = datetime.now(timezone.utc)
        sla_map = await self._get_sla_hours()

        # Resolved CVEs (fixed or verified)
        resolved = []
        async for doc in self.cves_col.find(
            {"status": {"$in": ["fixed", "verified"]}}, {"_id": 0}
        ):
            resolved.append(doc)

        # Open CVEs
        open_cves = []
        async for doc in self.cves_col.find(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}}, {"_id": 0}
        ):
            open_cves.append(doc)

        # Calculate MTTR per severity
        mttr_by_severity = {}
        resolution_within_sla = {}
        for sev in ["critical", "high", "medium", "low"]:
            sla_hours = sla_map.get(sev, 168)
            sev_resolved = [c for c in resolved if c.get("severity") == sev]
            times = []
            within = 0
            for cve in sev_resolved:
                detected_str = cve.get("detected_at") or cve.get("created_at", "")
                resolved_str = cve.get("fixed_at") or cve.get("verified_at") or cve.get("updated_at", "")
                if not detected_str or not resolved_str:
                    continue
                try:
                    d = datetime.fromisoformat(detected_str.replace("Z", "+00:00"))
                    r = datetime.fromisoformat(resolved_str.replace("Z", "+00:00"))
                    hours = (r - d).total_seconds() / 3600
                    if hours >= 0:
                        times.append(hours)
                        if hours <= sla_hours:
                            within += 1
                except (ValueError, TypeError):
                    continue

            avg_mttr = round(sum(times) / len(times), 1) if times else 0
            mttr_by_severity[sev] = {
                "avg_hours": avg_mttr,
                "avg_days": round(avg_mttr / 24, 1),
                "min_hours": round(min(times), 1) if times else 0,
                "max_hours": round(max(times), 1) if times else 0,
                "sample_size": len(times),
                "sla_hours": sla_hours,
            }
            resolution_within_sla[sev] = {
                "resolved_total": len(sev_resolved),
                "within_sla": within,
                "breached": len(sev_resolved) - within,
                "rate_pct": round((within / len(sev_resolved) * 100) if sev_resolved else 100, 1),
            }

        # Overall MTTR
        all_times = []
        for sev_data in mttr_by_severity.values():
            if sev_data["sample_size"] > 0:
                all_times.extend([sev_data["avg_hours"]] * sev_data["sample_size"])
        overall_mttr = round(sum(all_times) / len(all_times), 1) if all_times else 0

        # Time to triage
        triage_times = []
        for cve in resolved + open_cves:
            detected_str = cve.get("detected_at") or cve.get("created_at", "")
            triaged_str = cve.get("triaged_at", "")
            if not detected_str or not triaged_str or triaged_str == "None":
                continue
            try:
                d = datetime.fromisoformat(detected_str.replace("Z", "+00:00"))
                t = datetime.fromisoformat(triaged_str.replace("Z", "+00:00"))
                h = (t - d).total_seconds() / 3600
                if h >= 0:
                    triage_times.append(h)
            except (ValueError, TypeError):
                continue
        avg_triage = round(sum(triage_times) / len(triage_times), 1) if triage_times else 0

        # Weekly stats
        week_ago = now - timedelta(days=7)
        resolved_this_week = sum(
            1 for c in resolved
            if self._parse_date(c.get("fixed_at") or c.get("verified_at") or "") and
               self._parse_date(c.get("fixed_at") or c.get("verified_at") or "") >= week_ago
        )

        return {
            "overall_mttr_hours": overall_mttr,
            "overall_mttr_days": round(overall_mttr / 24, 1),
            "avg_triage_hours": avg_triage,
            "total_resolved": len(resolved),
            "total_open": len(open_cves),
            "resolved_this_week": resolved_this_week,
            "mttr_by_severity": mttr_by_severity,
            "resolution_within_sla": resolution_within_sla,
            "generated_at": now.isoformat(),
        }

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str or date_str == "None":
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    # ─── Team Performance ─────────────────────────────────────
    async def get_team_performance(self) -> Dict[str, Any]:
        """Get per-assignee/team SLA performance metrics."""
        sla_map = await self._get_sla_hours()

        all_cves = []
        async for doc in self.cves_col.find({}, {"_id": 0}):
            all_cves.append(doc)

        assignee_stats = {}
        for cve in all_cves:
            assignee = cve.get("assigned_to") or "Unassigned"
            if assignee not in assignee_stats:
                assignee_stats[assignee] = {
                    "assignee": assignee,
                    "team": cve.get("assigned_team", ""),
                    "total": 0,
                    "open": 0,
                    "resolved": 0,
                    "breached": 0,
                    "within_sla": 0,
                    "mttr_hours_list": [],
                }

            stats = assignee_stats[assignee]
            stats["total"] += 1
            severity = cve.get("severity", "medium")
            sla_hours = sla_map.get(severity, 168)

            if cve.get("status") in ["fixed", "verified"]:
                stats["resolved"] += 1
                detected_str = cve.get("detected_at") or cve.get("created_at", "")
                resolved_str = cve.get("fixed_at") or cve.get("verified_at") or ""
                dt_d = self._parse_date(detected_str)
                dt_r = self._parse_date(resolved_str)
                if dt_d and dt_r:
                    h = (dt_r - dt_d).total_seconds() / 3600
                    stats["mttr_hours_list"].append(h)
                    if h <= sla_hours:
                        stats["within_sla"] += 1
                    else:
                        stats["breached"] += 1
            else:
                stats["open"] += 1
                detected_str = cve.get("detected_at") or cve.get("created_at", "")
                dt_d = self._parse_date(detected_str)
                if dt_d:
                    now = datetime.now(timezone.utc)
                    elapsed_h = (now - dt_d).total_seconds() / 3600
                    if elapsed_h > sla_hours:
                        stats["breached"] += 1

        # Compute averages
        result = []
        for assignee, stats in assignee_stats.items():
            mttr_list = stats.pop("mttr_hours_list")
            avg_mttr = round(sum(mttr_list) / len(mttr_list), 1) if mttr_list else 0
            compliance = round(
                (stats["within_sla"] / stats["resolved"] * 100) if stats["resolved"] else 100, 1
            )
            result.append({
                **stats,
                "avg_mttr_hours": avg_mttr,
                "avg_mttr_days": round(avg_mttr / 24, 1),
                "compliance_pct": compliance,
            })

        result.sort(key=lambda x: (-x["compliance_pct"], x["avg_mttr_hours"]))
        return {"team": result}

    # ─── Breach Timeline ──────────────────────────────────────
    async def get_breach_timeline(self, days: int = 30) -> Dict[str, Any]:
        """Get a timeline of SLA breach events for the past N days."""
        now = datetime.now(timezone.utc)
        sla_map = await self._get_sla_hours()

        open_cves = []
        async for doc in self.cves_col.find(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}}, {"_id": 0}
        ):
            open_cves.append(doc)

        timeline_by_day = {}
        for i in range(days, -1, -1):
            day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            timeline_by_day[day] = {"date": day, "label": (now - timedelta(days=i)).strftime("%b %d"), "new_breaches": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}

        for cve in open_cves:
            severity = cve.get("severity", "medium")
            sla_hours = sla_map.get(severity, 168)
            detected_str = cve.get("detected_at") or cve.get("created_at", "")
            dt_d = self._parse_date(detected_str)
            if not dt_d:
                continue
            breach_time = dt_d + timedelta(hours=sla_hours)
            if breach_time > now:
                continue  # Not yet breached
            breach_day = breach_time.strftime("%Y-%m-%d")
            if breach_day in timeline_by_day:
                timeline_by_day[breach_day]["new_breaches"] += 1
                if severity in timeline_by_day[breach_day]:
                    timeline_by_day[breach_day][severity] += 1

        timeline = sorted(timeline_by_day.values(), key=lambda x: x["date"])
        return {"timeline": timeline, "period_days": days}

    # ─── Phase 2: Auto-Escalation Config ──────────────────────
    async def get_auto_escalation_config(self) -> Dict[str, Any]:
        doc = await self.sla_config_col.find_one({"key": "auto_escalation"}, {"_id": 0})
        if not doc:
            doc = {
                "key": "auto_escalation",
                "enabled": False,
                "interval_minutes": 60,
                "email_on_warning": True,
                "email_on_breach": True,
                "email_on_escalation": True,
                "digest_enabled": False,
                "digest_cron_hour": 8,
                "recipients": [],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.sla_config_col.insert_one({**doc, "_id": "auto_escalation"})
        doc.pop("key", None)
        return doc

    async def update_auto_escalation_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        config["key"] = "auto_escalation"
        config["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.sla_config_col.update_one(
            {"key": "auto_escalation"}, {"$set": config}, upsert=True
        )
        was_enabled = config.get("enabled", False)
        interval = config.get("interval_minutes", 60)
        if was_enabled:
            self.start_auto_escalation(interval)
        else:
            self.stop_auto_escalation()
        config.pop("key", None)
        return config

    # ─── Phase 2: Notification Preferences ────────────────────
    async def get_notification_preferences(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        key = f"sla_notif_prefs:{user_id}" if user_id else "sla_notif_prefs"
        doc = await self.sla_config_col.find_one({"key": key}, {"_id": 0})
        if not doc:
            # Fall back to global defaults
            doc = await self.sla_config_col.find_one({"key": "sla_notif_prefs"}, {"_id": 0})
        if not doc:
            doc = {
                "key": key,
                "user_id": user_id or "",
                "notify_on_warning": True,
                "notify_on_breach": True,
                "notify_on_escalation": True,
                "muted_severities": [],
                "quiet_hours_enabled": False,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "07:00",
                "per_severity": {
                    "critical": {"email": True, "in_app": True, "ws": True},
                    "high": {"email": True, "in_app": True, "ws": True},
                    "medium": {"email": False, "in_app": True, "ws": True},
                    "low": {"email": False, "in_app": True, "ws": False},
                },
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.sla_config_col.insert_one({**doc, "_id": key})
        doc.pop("key", None)
        return doc

    async def update_notification_preferences(self, prefs: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        key = f"sla_notif_prefs:{user_id}" if user_id else "sla_notif_prefs"
        prefs["key"] = key
        prefs["user_id"] = user_id or ""
        prefs["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.sla_config_col.update_one(
            {"key": key}, {"$set": prefs}, upsert=True
        )
        prefs.pop("key", None)
        return prefs

    async def should_notify_user(self, user_id: str, event_type: str, severity: str) -> Dict[str, bool]:
        """Check if a user should receive a specific notification type."""
        prefs = await self.get_notification_preferences(user_id=user_id)

        # Check muted severities
        muted = prefs.get("muted_severities", [])
        if severity in muted:
            return {"email": False, "in_app": False, "ws": False}

        # Check quiet hours
        if prefs.get("quiet_hours_enabled", False):
            now = datetime.now(timezone.utc)
            try:
                start_h, start_m = map(int, prefs.get("quiet_hours_start", "22:00").split(":"))
                end_h, end_m = map(int, prefs.get("quiet_hours_end", "07:00").split(":"))
                current_minutes = now.hour * 60 + now.minute
                start_minutes = start_h * 60 + start_m
                end_minutes = end_h * 60 + end_m
                if start_minutes > end_minutes:
                    in_quiet = current_minutes >= start_minutes or current_minutes < end_minutes
                else:
                    in_quiet = start_minutes <= current_minutes < end_minutes
                if in_quiet:
                    return {"email": False, "in_app": True, "ws": False}
            except (ValueError, TypeError):
                pass

        # Check per-event-type toggle
        type_map = {"sla_warning": "notify_on_warning", "sla_breach": "notify_on_breach", "escalation_run": "notify_on_escalation"}
        toggle_key = type_map.get(event_type, "notify_on_warning")
        if not prefs.get(toggle_key, True):
            return {"email": False, "in_app": False, "ws": False}

        # Check per-severity settings
        sev_prefs = prefs.get("per_severity", {}).get(severity, {"email": False, "in_app": True, "ws": True})
        return {
            "email": sev_prefs.get("email", False),
            "in_app": sev_prefs.get("in_app", True),
            "ws": sev_prefs.get("ws", True),
        }

    # ─── Phase 2: Escalation Workflow ─────────────────────────
    async def acknowledge_escalation(self, log_id: str, acknowledged_by: str = "") -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        result = await self.escalation_log_col.update_one(
            {"id": log_id, "status": {"$nin": ["resolved"]}},
            {"$set": {"status": "acknowledged", "acknowledged_by": acknowledged_by, "acknowledged_at": now}},
        )
        if result.modified_count == 0:
            return {"success": False, "error": "Escalation not found or already resolved"}
        return {"success": True, "status": "acknowledged"}

    async def assign_escalation(self, log_id: str, assignee: str, assigned_by: str = "") -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        result = await self.escalation_log_col.update_one(
            {"id": log_id, "status": {"$nin": ["resolved"]}},
            {"$set": {"status": "assigned", "assignee": assignee, "assigned_by": assigned_by, "assigned_at": now}},
        )
        if result.modified_count == 0:
            return {"success": False, "error": "Escalation not found or already resolved"}
        return {"success": True, "status": "assigned", "assignee": assignee}

    async def resolve_escalation(self, log_id: str, resolution_note: str = "", resolved_by: str = "") -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        result = await self.escalation_log_col.update_one(
            {"id": log_id},
            {"$set": {"status": "resolved", "resolution_note": resolution_note, "resolved_by": resolved_by, "resolved_at": now}},
        )
        if result.modified_count == 0:
            return {"success": False, "error": "Escalation not found"}
        return {"success": True, "status": "resolved"}

    async def get_escalation_stats(self) -> Dict[str, Any]:
        total = await self.escalation_log_col.count_documents({})
        open_count = await self.escalation_log_col.count_documents({"status": {"$nin": ["resolved", "acknowledged", "assigned"]}})
        ack_count = await self.escalation_log_col.count_documents({"status": "acknowledged"})
        assigned_count = await self.escalation_log_col.count_documents({"status": "assigned"})
        resolved_count = await self.escalation_log_col.count_documents({"status": "resolved"})
        return {
            "total": total,
            "open": open_count,
            "acknowledged": ack_count,
            "assigned": assigned_count,
            "resolved": resolved_count,
        }

    # ─── Phase 2: Email Sending ───────────────────────────────
    async def _send_sla_email(self, recipients: List[str], subject: str, html_body: str) -> Dict[str, Any]:
        if not resend.api_key or not recipients:
            return {"sent": False, "reason": "No API key or no recipients"}
        try:
            params = {
                "from": SLA_SENDER_EMAIL,
                "to": recipients,
                "subject": subject,
                "html": html_body,
            }
            result = resend.Emails.send(params)
            return {"sent": True, "id": result.get("id", "")}
        except Exception as e:
            logger.error(f"SLA email failed: {e}")
            return {"sent": False, "reason": str(e)}

    def _build_escalation_email_html(self, escalations: List[Dict], summary: Dict) -> str:
        rows = ""
        for esc in escalations[:20]:
            sev_color = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#3b82f6"}.get(esc.get("severity", ""), "#94a3b8")
            rows += f"""<tr>
                <td style="padding:8px;border-bottom:1px solid #334155;color:#e2e8f0;font-family:monospace;font-size:13px">{esc.get('cve_id','')}</td>
                <td style="padding:8px;border-bottom:1px solid #334155;color:{sev_color};font-weight:600;text-transform:uppercase;font-size:12px">{esc.get('severity','')}</td>
                <td style="padding:8px;border-bottom:1px solid #334155;color:#f59e0b;font-size:13px">L{esc.get('level',0)}</td>
                <td style="padding:8px;border-bottom:1px solid #334155;color:#94a3b8;font-size:13px">{esc.get('actual_pct',0)}%</td>
            </tr>"""
        return f"""<div style="background:#0f172a;padding:32px;font-family:system-ui,sans-serif">
            <h2 style="color:#22d3ee;margin:0 0 8px">SLA Escalation Alert</h2>
            <p style="color:#94a3b8;margin:0 0 24px;font-size:14px">
                {summary.get('escalations_created',0)} new escalation(s) from {summary.get('checked',0)} at-risk CVEs
            </p>
            <table style="width:100%;border-collapse:collapse;background:#1e293b;border-radius:8px;overflow:hidden">
                <thead><tr style="background:#334155">
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">CVE</th>
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">Severity</th>
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">Level</th>
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">SLA %</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>"""

    def _build_digest_email_html(self, dashboard: Dict, at_risk_items: List[Dict]) -> str:
        compliance = dashboard.get("overall_compliance", 0)
        color = "#10b981" if compliance >= 90 else "#f59e0b" if compliance >= 70 else "#ef4444"
        sev_rows = ""
        for sev in ["critical", "high", "medium", "low"]:
            s = dashboard.get("severity_stats", {}).get(sev, {})
            sev_color = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#3b82f6"}[sev]
            sev_rows += f"""<tr>
                <td style="padding:8px;border-bottom:1px solid #334155;color:{sev_color};font-weight:600;text-transform:uppercase;font-size:12px">{sev}</td>
                <td style="padding:8px;border-bottom:1px solid #334155;color:#e2e8f0;font-size:13px">{s.get('total',0)}</td>
                <td style="padding:8px;border-bottom:1px solid #334155;color:#10b981;font-size:13px">{s.get('within_sla',0)}</td>
                <td style="padding:8px;border-bottom:1px solid #334155;color:#f59e0b;font-size:13px">{s.get('warning',0)}</td>
                <td style="padding:8px;border-bottom:1px solid #334155;color:#ef4444;font-size:13px">{s.get('breached',0)}</td>
            </tr>"""
        risk_rows = ""
        for item in at_risk_items[:10]:
            risk_rows += f"<li style='color:#e2e8f0;font-size:13px;margin-bottom:4px'><span style='font-family:monospace;color:#22d3ee'>{item.get('cve_id','')}</span> — {item.get('severity','').upper()} — {item.get('percent_elapsed',0)}% elapsed</li>"
        return f"""<div style="background:#0f172a;padding:32px;font-family:system-ui,sans-serif">
            <h2 style="color:#22d3ee;margin:0 0 8px">SLA Compliance Digest</h2>
            <p style="color:#94a3b8;margin:0 0 24px;font-size:14px">
                Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
            </p>
            <div style="background:#1e293b;border-radius:12px;padding:24px;margin-bottom:24px;text-align:center">
                <div style="font-size:48px;font-weight:700;color:{color}">{compliance}%</div>
                <div style="color:#94a3b8;font-size:13px">Overall SLA Compliance</div>
                <div style="color:#64748b;font-size:12px;margin-top:4px">{dashboard.get('total_open',0)} open | {dashboard.get('total_breached',0)} breached | {dashboard.get('total_warning',0)} warning</div>
            </div>
            <table style="width:100%;border-collapse:collapse;background:#1e293b;border-radius:8px;overflow:hidden;margin-bottom:24px">
                <thead><tr style="background:#334155">
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">Severity</th>
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">Total</th>
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">Within</th>
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">Warning</th>
                    <th style="padding:10px;text-align:left;color:#e2e8f0;font-size:12px">Breached</th>
                </tr></thead>
                <tbody>{sev_rows}</tbody>
            </table>
            {"<h3 style='color:#e2e8f0;font-size:14px;margin-bottom:8px'>Top At-Risk CVEs</h3><ul style='padding-left:20px;margin:0'>" + risk_rows + "</ul>" if risk_rows else ""}
        </div>"""

    # ─── Phase 2: Enhanced Run Escalations (with email) ───────
    async def run_escalations_with_notifications(self) -> Dict[str, Any]:
        result = await self.run_escalations()
        if result["escalations_created"] > 0:
            config = await self.get_auto_escalation_config()
            recipients = config.get("recipients", [])
            if config.get("email_on_escalation", True) and recipients:
                recent_log = await self.get_escalation_log(limit=result["escalations_created"])
                html = self._build_escalation_email_html(recent_log.get("items", []), result)
                email_result = await self._send_sla_email(
                    recipients,
                    f"SLA Alert: {result['escalations_created']} new escalation(s)",
                    html,
                )
                result["email_sent"] = email_result.get("sent", False)
            else:
                result["email_sent"] = False
        else:
            result["email_sent"] = False
        return result

    # ─── Phase 2: SLA Digest ──────────────────────────────────
    async def send_sla_digest(self) -> Dict[str, Any]:
        config = await self.get_auto_escalation_config()
        recipients = config.get("recipients", [])
        if not recipients:
            return {"sent": False, "reason": "No recipients configured"}
        dashboard = await self.get_sla_dashboard()
        at_risk_data = await self.get_at_risk_cves(limit=10)
        html = self._build_digest_email_html(dashboard, at_risk_data.get("items", []))
        email_result = await self._send_sla_email(
            recipients,
            f"SLA Digest — {dashboard.get('overall_compliance', 0)}% Compliance",
            html,
        )
        return {
            "sent": email_result.get("sent", False),
            "recipients": len(recipients),
            "compliance": dashboard.get("overall_compliance", 0),
            "total_open": dashboard.get("total_open", 0),
            "total_breached": dashboard.get("total_breached", 0),
        }

    # ─── Phase 2: Auto-Escalation Background Task ────────────
    def start_auto_escalation(self, interval_minutes: int = 60):
        self.stop_auto_escalation()
        self._auto_task = asyncio.ensure_future(self._auto_escalation_loop(interval_minutes))
        logger.info(f"Auto-escalation started: every {interval_minutes} min")

    def stop_auto_escalation(self):
        if self._auto_task and not self._auto_task.done():
            self._auto_task.cancel()
            self._auto_task = None
            logger.info("Auto-escalation stopped")

    async def _auto_escalation_loop(self, interval_minutes: int):
        while True:
            try:
                await asyncio.sleep(interval_minutes * 60)
                result = await self.run_escalations_with_notifications()
                await self.take_snapshot()
                logger.info(f"Auto-escalation run: {result.get('escalations_created', 0)} created")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-escalation error: {e}")
                await asyncio.sleep(60)
