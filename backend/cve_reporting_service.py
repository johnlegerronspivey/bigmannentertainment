"""
CVE Reporting & Analytics Service
Provides executive summaries, trend analysis, team performance,
scanner effectiveness, and data export (CSV/PDF).
"""

import io
import csv
import json
import logging
import os
import uuid
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("cve_reporting_service")

_reporting_instance = None


def get_cve_reporting_service():
    global _reporting_instance
    if _reporting_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _reporting_instance = CVEReportingService(db)
    return _reporting_instance


def initialize_cve_reporting_service(db):
    global _reporting_instance
    _reporting_instance = CVEReportingService(db)
    return _reporting_instance


class CVEReportingService:
    def __init__(self, db):
        self.db = db
        self.cves_col = db["cve_entries"]
        self.scan_results_col = db["cve_scan_results"]
        self.remediation_col = db["cve_remediation_items"]
        self.audit_col = db["cve_audit_trail"]
        self.sla_snapshots_col = db["cve_sla_snapshots"]
        self.policies_col = db["cve_severity_policies"]
        self.saved_reports_col = db["cve_saved_reports"]

    # ─── Executive Summary ────────────────────────────────────────

    async def get_executive_summary(self, days: int = 30) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(days=days)).isoformat()

        total = await self.cves_col.count_documents({})
        open_statuses = ["detected", "triaged", "in_progress"]
        closed_statuses = ["fixed", "verified", "dismissed", "wont_fix"]

        total_open = await self.cves_col.count_documents({"status": {"$in": open_statuses}})
        total_closed = await self.cves_col.count_documents({"status": {"$in": closed_statuses}})
        new_in_period = await self.cves_col.count_documents({"created_at": {"$gte": cutoff}})
        fixed_in_period = await self.cves_col.count_documents({
            "status": {"$in": ["fixed", "verified"]},
            "resolved_at": {"$gte": cutoff},
        })

        # Severity breakdown
        severity_dist = {}
        for sev in ["critical", "high", "medium", "low", "info"]:
            severity_dist[sev] = await self.cves_col.count_documents({"severity": sev})

        # MTTR calculation (mean time to resolution in hours)
        mttr = await self._calculate_mttr(cutoff)

        # SLA compliance
        sla_compliance = await self._calculate_sla_compliance()

        # Risk score (0-100): weighted by open severity
        risk_score = self._calculate_risk_score(severity_dist, total_open, total)

        # Resolution rate
        resolution_rate = round((fixed_in_period / new_in_period * 100) if new_in_period else 100, 1)

        return {
            "period_days": days,
            "total_cves": total,
            "total_open": total_open,
            "total_closed": total_closed,
            "new_in_period": new_in_period,
            "fixed_in_period": fixed_in_period,
            "resolution_rate": resolution_rate,
            "mttr_hours": mttr,
            "sla_compliance": sla_compliance,
            "risk_score": risk_score,
            "severity_distribution": severity_dist,
            "generated_at": now.isoformat(),
        }

    async def _calculate_mttr(self, cutoff: str) -> float:
        resolved = []
        cursor = self.cves_col.find(
            {"status": {"$in": ["fixed", "verified"]}, "resolved_at": {"$gte": cutoff}},
            {"_id": 0, "created_at": 1, "resolved_at": 1},
        )
        async for doc in cursor:
            created = doc.get("created_at", "")
            resolved_at = doc.get("resolved_at", "")
            if created and resolved_at:
                try:
                    c = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    r = datetime.fromisoformat(resolved_at.replace("Z", "+00:00"))
                    resolved.append((r - c).total_seconds() / 3600)
                except (ValueError, TypeError):
                    pass
        return round(sum(resolved) / len(resolved), 1) if resolved else 0

    async def _calculate_sla_compliance(self) -> float:
        now = datetime.now(timezone.utc)
        sla_map = {"critical": 24, "high": 72, "medium": 168, "low": 720}
        async for doc in self.policies_col.find({}, {"_id": 0}):
            sev = doc.get("severity")
            if sev and "sla_hours" in doc:
                sla_map[sev] = doc["sla_hours"]

        open_cves = []
        cursor = self.cves_col.find(
            {"status": {"$in": ["detected", "triaged", "in_progress"]}},
            {"_id": 0, "severity": 1, "created_at": 1, "detected_at": 1},
        )
        async for doc in cursor:
            open_cves.append(doc)

        if not open_cves:
            return 100.0

        within = 0
        for cve in open_cves:
            sev = cve.get("severity", "medium")
            sla_hours = sla_map.get(sev, 168)
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
            if elapsed_h <= sla_hours:
                within += 1

        return round(within / len(open_cves) * 100, 1)

    def _calculate_risk_score(self, severity_dist: Dict, total_open: int, total: int) -> int:
        if total == 0:
            return 0
        weights = {"critical": 10, "high": 6, "medium": 3, "low": 1, "info": 0}
        weighted = sum(severity_dist.get(s, 0) * w for s, w in weights.items())
        max_possible = total * 10
        raw = (weighted / max_possible * 100) if max_possible else 0
        openness_factor = (total_open / total) if total else 0
        return min(100, int(raw * (0.5 + 0.5 * openness_factor)))

    # ─── Trend Analysis ───────────────────────────────────────────

    async def get_cve_trends(self, days: int = 30) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        trends = []

        for i in range(days, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0).isoformat()
            day_end = day.replace(hour=23, minute=59, second=59).isoformat()

            discovered = await self.cves_col.count_documents({
                "created_at": {"$gte": day_start, "$lte": day_end}
            })
            resolved = await self.cves_col.count_documents({
                "resolved_at": {"$gte": day_start, "$lte": day_end}
            })
            backlog = await self.cves_col.count_documents({
                "status": {"$in": ["detected", "triaged", "in_progress"]},
                "created_at": {"$lte": day_end},
            })

            trends.append({
                "date": day.strftime("%Y-%m-%d"),
                "label": day.strftime("%b %d"),
                "discovered": discovered,
                "resolved": resolved,
                "backlog": backlog,
            })

        return {"trends": trends, "period_days": days}

    # ─── Severity Trends ──────────────────────────────────────────

    async def get_severity_trends(self, days: int = 30) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        trends = []

        for i in range(days, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0).isoformat()
            day_end = day.replace(hour=23, minute=59, second=59).isoformat()

            entry = {"date": day.strftime("%Y-%m-%d"), "label": day.strftime("%b %d")}
            for sev in ["critical", "high", "medium", "low"]:
                entry[sev] = await self.cves_col.count_documents({
                    "severity": sev,
                    "created_at": {"$gte": day_start, "$lte": day_end},
                })
            trends.append(entry)

        return {"trends": trends, "period_days": days}

    # ─── Team Performance ─────────────────────────────────────────

    async def get_team_performance(self) -> Dict[str, Any]:
        owner_stats = defaultdict(lambda: {
            "assigned": 0, "open": 0, "resolved": 0, "total_resolution_hours": 0,
            "critical": 0, "high": 0, "medium": 0, "low": 0,
        })

        cursor = self.cves_col.find({}, {"_id": 0, "assigned_to": 1, "status": 1, "severity": 1, "created_at": 1, "resolved_at": 1})
        async for doc in cursor:
            owner = doc.get("assigned_to") or "Unassigned"
            stats = owner_stats[owner]
            stats["assigned"] += 1

            sev = doc.get("severity", "medium")
            if sev in stats:
                stats[sev] += 1

            status = doc.get("status", "detected")
            if status in ["fixed", "verified"]:
                stats["resolved"] += 1
                created = doc.get("created_at", "")
                resolved_at = doc.get("resolved_at", "")
                if created and resolved_at:
                    try:
                        c = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        r = datetime.fromisoformat(resolved_at.replace("Z", "+00:00"))
                        stats["total_resolution_hours"] += (r - c).total_seconds() / 3600
                    except (ValueError, TypeError):
                        pass
            else:
                stats["open"] += 1

        teams = []
        for owner, stats in owner_stats.items():
            avg_resolution = round(stats["total_resolution_hours"] / stats["resolved"], 1) if stats["resolved"] else 0
            resolution_rate = round(stats["resolved"] / stats["assigned"] * 100, 1) if stats["assigned"] else 0
            teams.append({
                "owner": owner,
                "assigned": stats["assigned"],
                "open": stats["open"],
                "resolved": stats["resolved"],
                "resolution_rate": resolution_rate,
                "avg_resolution_hours": avg_resolution,
                "critical": stats["critical"],
                "high": stats["high"],
                "medium": stats["medium"],
                "low": stats["low"],
            })

        teams.sort(key=lambda x: x["assigned"], reverse=True)
        return {"teams": teams, "total_owners": len(teams)}

    # ─── Scanner Effectiveness ────────────────────────────────────

    async def get_scanner_stats(self) -> Dict[str, Any]:
        scanner_counts = defaultdict(lambda: {"total_scans": 0, "cves_found": 0, "severities": defaultdict(int)})

        cursor = self.scan_results_col.find({}, {"_id": 0})
        async for doc in cursor:
            scanner = doc.get("scanner", "unknown")
            stats = scanner_counts[scanner]
            stats["total_scans"] += 1
            findings = doc.get("findings_count", 0)
            stats["cves_found"] += findings

        # Also look at CVE source
        cursor2 = self.cves_col.find({}, {"_id": 0, "source": 1, "severity": 1})
        async for doc in cursor2:
            source = doc.get("source", "manual")
            if source in scanner_counts:
                sev = doc.get("severity", "medium")
                scanner_counts[source]["severities"][sev] += 1

        scanners = []
        for name, stats in scanner_counts.items():
            scanners.append({
                "scanner": name,
                "total_scans": stats["total_scans"],
                "cves_found": stats["cves_found"],
                "avg_findings_per_scan": round(stats["cves_found"] / stats["total_scans"], 1) if stats["total_scans"] else 0,
                "severities": dict(stats["severities"]),
            })

        scanners.sort(key=lambda x: x["cves_found"], reverse=True)
        return {"scanners": scanners}

    # ─── Status Distribution ──────────────────────────────────────

    async def get_status_distribution(self) -> Dict[str, Any]:
        statuses = ["detected", "triaged", "in_progress", "fixed", "verified", "dismissed", "wont_fix"]
        dist = {}
        for s in statuses:
            dist[s] = await self.cves_col.count_documents({"status": s})
        return {"distribution": dist, "total": sum(dist.values())}

    # ─── CSV Export ───────────────────────────────────────────────

    async def export_cves_csv(self, filters: Optional[Dict] = None) -> bytes:
        query = filters or {}
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "CVE ID", "Title", "Severity", "Status", "CVSS Score",
            "Assigned To", "Source", "Detected At", "Resolved At", "Created At",
        ])

        cursor = self.cves_col.find(query, {"_id": 0})
        async for doc in cursor:
            writer.writerow([
                doc.get("cve_id", ""),
                doc.get("title", ""),
                doc.get("severity", ""),
                doc.get("status", ""),
                doc.get("cvss_score", ""),
                doc.get("assigned_to", ""),
                doc.get("source", ""),
                doc.get("detected_at", ""),
                doc.get("resolved_at", ""),
                doc.get("created_at", ""),
            ])

        return output.getvalue().encode("utf-8")

    async def export_executive_csv(self, days: int = 30) -> bytes:
        summary = await self.get_executive_summary(days)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["CVE Executive Report"])
        writer.writerow(["Generated", summary["generated_at"]])
        writer.writerow(["Period (days)", summary["period_days"]])
        writer.writerow([])

        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total CVEs", summary["total_cves"]])
        writer.writerow(["Open CVEs", summary["total_open"]])
        writer.writerow(["Closed CVEs", summary["total_closed"]])
        writer.writerow(["New in Period", summary["new_in_period"]])
        writer.writerow(["Fixed in Period", summary["fixed_in_period"]])
        writer.writerow(["Resolution Rate (%)", summary["resolution_rate"]])
        writer.writerow(["MTTR (hours)", summary["mttr_hours"]])
        writer.writerow(["SLA Compliance (%)", summary["sla_compliance"]])
        writer.writerow(["Risk Score", summary["risk_score"]])
        writer.writerow([])

        writer.writerow(["Severity Distribution"])
        writer.writerow(["Severity", "Count"])
        for sev, count in summary["severity_distribution"].items():
            writer.writerow([sev.capitalize(), count])

        return output.getvalue().encode("utf-8")

    async def export_team_csv(self) -> bytes:
        data = await self.get_team_performance()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Owner", "Assigned", "Open", "Resolved", "Resolution Rate (%)",
            "Avg Resolution (hours)", "Critical", "High", "Medium", "Low",
        ])
        for t in data["teams"]:
            writer.writerow([
                t["owner"], t["assigned"], t["open"], t["resolved"],
                t["resolution_rate"], t["avg_resolution_hours"],
                t["critical"], t["high"], t["medium"], t["low"],
            ])
        return output.getvalue().encode("utf-8")

    # ─── Saved Reports ────────────────────────────────────────────

    async def get_saved_reports(self) -> Dict[str, Any]:
        reports = []
        cursor = self.saved_reports_col.find({}, {"_id": 0}).sort("created_at", -1)
        async for doc in cursor:
            reports.append(doc)
        return {"reports": reports}

    async def save_report(self, name: str, report_type: str, config: Dict) -> Dict[str, Any]:
        report = {
            "id": str(uuid.uuid4()),
            "name": name,
            "report_type": report_type,
            "config": config,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.saved_reports_col.insert_one({**report})
        return {k: v for k, v in report.items() if k != "_id"}

    async def delete_saved_report(self, report_id: str) -> Dict[str, Any]:
        result = await self.saved_reports_col.delete_one({"id": report_id})
        return {"deleted": result.deleted_count > 0}
