"""
Governance Service - Phase 4: Governance Dashboards & Advanced Analytics
Provides security metrics, SLA tracking, ownership stats, and trend data.
"""

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("governance_service")

_governance_instance = None


def get_governance_service():
    global _governance_instance
    if _governance_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _governance_instance = GovernanceService(db)
    return _governance_instance


def initialize_governance_service(db):
    global _governance_instance
    _governance_instance = GovernanceService(db)
    return _governance_instance


class GovernanceService:
    def __init__(self, db):
        self.db = db
        self.cves_col = db["cve_entries"]
        self.services_col = db["cve_services"]
        self.remediation_col = db["cve_remediation_items"]
        self.audit_col = db["cve_audit_trail"]
        self.policies_col = db["cve_severity_policies"]
        self.scan_results_col = db["cve_scan_results"]
        self.aws_findings_col = db["cve_aws_findings"]

    async def get_governance_metrics(self) -> Dict[str, Any]:
        """Main governance dashboard metrics"""
        now = datetime.now(timezone.utc)
        thirty_days_ago = (now - timedelta(days=30)).isoformat()
        seven_days_ago = (now - timedelta(days=7)).isoformat()

        total = await self.cves_col.count_documents({})
        open_cves = await self.cves_col.count_documents({"status": {"$in": ["detected", "triaged", "in_progress"]}})
        fixed = await self.cves_col.count_documents({"status": "fixed"})
        verified = await self.cves_col.count_documents({"status": "verified"})
        dismissed = await self.cves_col.count_documents({"status": {"$in": ["dismissed", "wont_fix"]}})

        # Severity distribution for all open CVEs
        severity_dist = {}
        for sev in ["critical", "high", "medium", "low", "info"]:
            severity_dist[sev] = await self.cves_col.count_documents({
                "severity": sev,
                "status": {"$in": ["detected", "triaged", "in_progress"]}
            })

        # CVEs detected in last 30 days
        new_last_30 = await self.cves_col.count_documents({"created_at": {"$gte": thirty_days_ago}})
        new_last_7 = await self.cves_col.count_documents({"created_at": {"$gte": seven_days_ago}})
        fixed_last_30 = await self.cves_col.count_documents({"fixed_at": {"$gte": thirty_days_ago}})

        # Services with open CVEs
        pipeline = [
            {"$match": {"status": {"$in": ["detected", "triaged", "in_progress"]}}},
            {"$unwind": {"path": "$affected_services", "preserveNullAndEmptyArrays": False}},
            {"$group": {"_id": "$affected_services", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        services_affected = []
        async for doc in self.cves_col.aggregate(pipeline):
            services_affected.append({"service": doc["_id"], "count": doc["count"]})

        # Remediation stats
        rem_total = await self.remediation_col.count_documents({})
        rem_open = await self.remediation_col.count_documents({"status": "open"})
        rem_merged = await self.remediation_col.count_documents({"status": "merged"})

        # Risk score (weighted)
        risk_score = min(100, severity_dist.get("critical", 0) * 25 + severity_dist.get("high", 0) * 15 + severity_dist.get("medium", 0) * 5 + severity_dist.get("low", 0) * 1)

        return {
            "total_cves": total,
            "open_cves": open_cves,
            "fixed_cves": fixed,
            "verified_cves": verified,
            "dismissed_cves": dismissed,
            "severity_distribution": severity_dist,
            "new_last_30_days": new_last_30,
            "new_last_7_days": new_last_7,
            "fixed_last_30_days": fixed_last_30,
            "services_affected": services_affected,
            "remediation_total": rem_total,
            "remediation_open": rem_open,
            "remediation_merged": rem_merged,
            "risk_score": risk_score,
            "fix_rate_30d": round((fixed_last_30 / new_last_30 * 100) if new_last_30 > 0 else 100, 1),
        }

    async def get_trends(self, days: int = 30) -> Dict[str, Any]:
        """Historical trend data for charting"""
        now = datetime.now(timezone.utc)
        trends = []

        for i in range(days, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

            detected = await self.cves_col.count_documents({"created_at": {"$gte": day_start, "$lte": day_end}})
            fixed_count = await self.cves_col.count_documents({"fixed_at": {"$gte": day_start, "$lte": day_end}})

            trends.append({
                "date": day.strftime("%Y-%m-%d"),
                "label": day.strftime("%b %d"),
                "detected": detected,
                "fixed": fixed_count,
            })

        return {"trends": trends, "period_days": days}

    async def get_sla_compliance(self) -> Dict[str, Any]:
        """SLA compliance tracking based on severity policies"""
        policies = {}
        cursor = self.policies_col.find({}, {"_id": 0})
        async for p in cursor:
            policies[p.get("severity", "")] = p

        # Default SLA targets (hours)
        default_sla = {"critical": 24, "high": 72, "medium": 168, "low": 720}
        now = datetime.now(timezone.utc)

        sla_data = []
        for sev in ["critical", "high", "medium", "low"]:
            sla_hours = policies.get(sev, {}).get("sla_hours", default_sla.get(sev, 168))

            # All open CVEs of this severity
            open_count = await self.cves_col.count_documents({
                "severity": sev,
                "status": {"$in": ["detected", "triaged", "in_progress"]}
            })

            # Overdue (open longer than SLA)
            cutoff = (now - timedelta(hours=sla_hours)).isoformat()
            overdue = await self.cves_col.count_documents({
                "severity": sev,
                "status": {"$in": ["detected", "triaged", "in_progress"]},
                "created_at": {"$lte": cutoff}
            })

            # Fixed within SLA (estimate from fixed CVEs)
            fixed_total = await self.cves_col.count_documents({"severity": sev, "status": {"$in": ["fixed", "verified"]}})

            compliance_pct = round(((open_count - overdue) / open_count * 100) if open_count > 0 else 100, 1)

            sla_data.append({
                "severity": sev,
                "sla_hours": sla_hours,
                "open": open_count,
                "overdue": overdue,
                "within_sla": open_count - overdue,
                "fixed_total": fixed_total,
                "compliance_pct": compliance_pct,
            })

        overall = sum(d["compliance_pct"] for d in sla_data) / len(sla_data) if sla_data else 100

        return {"sla_data": sla_data, "overall_compliance": round(overall, 1)}

    async def get_ownership_stats(self) -> Dict[str, Any]:
        """CVE ownership and team distribution"""
        # By assigned team
        team_pipeline = [
            {"$match": {"status": {"$in": ["detected", "triaged", "in_progress"]}}},
            {"$group": {"_id": {"$ifNull": ["$assigned_team", "Unassigned"]}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        by_team = []
        async for doc in self.cves_col.aggregate(team_pipeline):
            team = doc["_id"] if doc["_id"] else "Unassigned"
            by_team.append({"team": team, "count": doc["count"]})

        # By assigned person
        person_pipeline = [
            {"$match": {"status": {"$in": ["detected", "triaged", "in_progress"]}}},
            {"$group": {"_id": {"$ifNull": ["$assigned_to", "Unassigned"]}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        by_person = []
        async for doc in self.cves_col.aggregate(person_pipeline):
            person = doc["_id"] if doc["_id"] else "Unassigned"
            by_person.append({"person": person, "count": doc["count"]})

        # By source
        source_pipeline = [
            {"$group": {"_id": {"$ifNull": ["$source", "manual"]}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        by_source = []
        async for doc in self.cves_col.aggregate(source_pipeline):
            by_source.append({"source": doc["_id"] or "manual", "count": doc["count"]})

        # By status
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        by_status = []
        async for doc in self.cves_col.aggregate(status_pipeline):
            by_status.append({"status": doc["_id"], "count": doc["count"]})

        return {
            "by_team": by_team,
            "by_person": by_person,
            "by_source": by_source,
            "by_status": by_status,
        }

    async def get_mttr(self) -> Dict[str, Any]:
        """Mean Time to Remediate by severity"""
        results = {}
        for sev in ["critical", "high", "medium", "low"]:
            pipeline = [
                {"$match": {
                    "severity": sev,
                    "status": {"$in": ["fixed", "verified"]},
                    "fixed_at": {"$ne": None},
                    "detected_at": {"$ne": None}
                }},
                {"$limit": 100}
            ]
            times = []
            async for doc in self.cves_col.aggregate(pipeline):
                try:
                    detected = datetime.fromisoformat(doc["detected_at"].replace("Z", "+00:00")) if isinstance(doc["detected_at"], str) else doc["detected_at"]
                    fixed = datetime.fromisoformat(doc["fixed_at"].replace("Z", "+00:00")) if isinstance(doc["fixed_at"], str) else doc["fixed_at"]
                    hours = (fixed - detected).total_seconds() / 3600
                    if hours > 0:
                        times.append(hours)
                except Exception:
                    continue

            avg_hours = round(sum(times) / len(times), 1) if times else 0
            results[sev] = {
                "avg_hours": avg_hours,
                "avg_days": round(avg_hours / 24, 1),
                "sample_size": len(times),
                "min_hours": round(min(times), 1) if times else 0,
                "max_hours": round(max(times), 1) if times else 0,
            }

        return {"mttr": results}

    async def get_scan_activity(self) -> Dict[str, Any]:
        """Scan activity summary"""
        total_scans = await self.scan_results_col.count_documents({})
        recent_scans = await self.scan_results_col.find(
            {}, {"_id": 0, "id": 1, "scanner": 1, "scan_type": 1, "created_at": 1, "total_findings": 1, "critical": 1, "high": 1}
        ).sort("created_at", -1).limit(10).to_list(10)

        by_scanner = {}
        async for doc in self.scan_results_col.aggregate([
            {"$group": {"_id": "$scanner", "count": {"$sum": 1}, "total_findings": {"$sum": "$total_findings"}}},
            {"$sort": {"count": -1}}
        ]):
            by_scanner[doc["_id"]] = {"scans": doc["count"], "findings": doc["total_findings"]}

        return {"total_scans": total_scans, "recent_scans": recent_scans, "by_scanner": by_scanner}
