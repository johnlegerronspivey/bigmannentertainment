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

    # ─── PDF Chart Helpers ───────────────────────────────────────
    def _render_severity_chart(self, severity_dist: Dict, total: int) -> bytes:
        """Generate severity distribution bar chart as PNG bytes."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        sevs = ["critical", "high", "medium", "low", "info"]
        counts = [severity_dist.get(s, 0) for s in sevs]
        colors = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"]

        fig, ax = plt.subplots(figsize=(5, 2.2), dpi=150)
        bars = ax.barh(sevs[::-1], counts[::-1], color=colors[::-1], height=0.6, edgecolor="white", linewidth=0.5)
        for bar, c in zip(bars, counts[::-1]):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, str(c),
                    va="center", fontsize=8, color="#1e293b", fontweight="bold")
        ax.set_xlim(0, max(counts) * 1.3 if max(counts) else 1)
        ax.set_xlabel("Count", fontsize=8, color="#64748b")
        ax.tick_params(axis="both", labelsize=8, colors="#64748b")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    def _render_risk_gauge(self, score: int) -> bytes:
        """Generate a risk gauge chart as PNG bytes."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=(2.5, 1.5), dpi=150, subplot_kw={"projection": "polar"})
        theta = np.linspace(np.pi, 0, 100)
        colors_arr = plt.cm.RdYlGn_r(np.linspace(0, 1, 100))
        for i in range(len(theta) - 1):
            ax.bar((theta[i] + theta[i + 1]) / 2, 1, width=(theta[i] - theta[i + 1]),
                   bottom=0.5, color=colors_arr[i], edgecolor="none")
        needle_angle = np.pi * (1 - score / 100)
        ax.plot([needle_angle, needle_angle], [0.3, 1.4], color="#1e293b", linewidth=2)
        ax.plot(needle_angle, 1.4, "o", color="#1e293b", markersize=3)
        ax.set_ylim(0, 1.6)
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_axis_off()
        ax.text(np.pi / 2, 0.1, f"{score}", ha="center", va="center", fontsize=14, fontweight="bold", color="#1e293b")
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    def _render_trend_chart(self, trends: List[Dict]) -> bytes:
        """Generate 7-day trend line chart as PNG bytes."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        days = [t["day"] for t in trends]
        counts = [t["count"] for t in trends]

        fig, ax = plt.subplots(figsize=(5, 1.8), dpi=150)
        ax.fill_between(range(len(days)), counts, alpha=0.15, color="#06b6d4")
        ax.plot(range(len(days)), counts, color="#06b6d4", linewidth=2, marker="o", markersize=4)
        for i, c in enumerate(counts):
            ax.text(i, c + 0.2, str(c), ha="center", fontsize=7, color="#06b6d4", fontweight="bold")
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(days, fontsize=7, color="#64748b")
        ax.set_ylabel("New CVEs", fontsize=8, color="#64748b")
        ax.tick_params(axis="y", labelsize=7, colors="#64748b")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylim(bottom=0)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    # ─── PDF Export ───────────────────────────────────────────────

    async def export_executive_pdf(self, days: int = 30) -> bytes:
        from fpdf import FPDF

        summary = await self.get_executive_summary(days)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(0, 180, 216)
        pdf.cell(0, 15, "CVE Executive Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Generated: {summary['generated_at'][:19]} | Period: {days} days", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(8)

        # Key Metrics Section
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, "Key Metrics", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(0, 180, 216)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        metrics = [
            ("Total CVEs", str(summary["total_cves"])),
            ("Open CVEs", str(summary["total_open"])),
            ("Closed CVEs", str(summary["total_closed"])),
            ("New in Period", str(summary["new_in_period"])),
            ("Fixed in Period", str(summary["fixed_in_period"])),
            ("Resolution Rate", f"{summary['resolution_rate']}%"),
            ("Mean Time to Resolve", f"{summary['mttr_hours']} hours"),
            ("SLA Compliance", f"{summary['sla_compliance']}%"),
            ("Risk Score", f"{summary['risk_score']}/100"),
        ]

        pdf.set_font("Helvetica", "", 11)
        for label, value in metrics:
            pdf.set_text_color(80, 80, 80)
            pdf.cell(90, 8, label, border=0)
            pdf.set_text_color(30, 30, 30)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)

        pdf.ln(6)

        # Severity Distribution
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, "Severity Distribution", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(0, 180, 216)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        sev_colors = {
            "critical": (239, 68, 68),
            "high": (249, 115, 22),
            "medium": (234, 179, 8),
            "low": (59, 130, 246),
            "info": (100, 116, 139),
        }

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(60, 8, "Severity", border=1, fill=True)
        pdf.cell(40, 8, "Count", border=1, fill=True, align="C")
        pdf.cell(80, 8, "Percentage", border=1, fill=True, align="C")
        pdf.ln()

        total = summary["total_cves"] or 1
        pdf.set_font("Helvetica", "", 10)
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = summary["severity_distribution"].get(sev, 0)
            pct = round(count / total * 100, 1)
            r, g, b = sev_colors.get(sev, (100, 100, 100))
            pdf.set_text_color(r, g, b)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(60, 8, sev.upper(), border=1)
            pdf.set_text_color(30, 30, 30)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(40, 8, str(count), border=1, align="C")
            pdf.cell(80, 8, f"{pct}%", border=1, align="C")
            pdf.ln()

        pdf.ln(8)

        # Embedded Severity Distribution Chart
        try:
            import tempfile
            chart_bytes = self._render_severity_chart(summary["severity_distribution"], total)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(chart_bytes)
                tmp_path = tmp.name
            pdf.image(tmp_path, x=15, w=120)
            os.unlink(tmp_path)
            pdf.ln(4)
        except Exception as e:
            logger.warning(f"Chart render failed: {e}")

        # Risk Assessment
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, "Risk Assessment", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(0, 180, 216)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        risk = summary["risk_score"]
        risk_label = "Critical" if risk >= 75 else "High" if risk >= 50 else "Medium" if risk >= 25 else "Low"
        risk_color = (239, 68, 68) if risk >= 75 else (249, 115, 22) if risk >= 50 else (234, 179, 8) if risk >= 25 else (16, 185, 129)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(50, 8, "Risk Level:")
        pdf.set_text_color(*risk_color)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"{risk_label} ({risk}/100)", new_x="LMARGIN", new_y="NEXT")

        sla = summary["sla_compliance"]
        sla_label = "Healthy" if sla >= 90 else "At Risk" if sla >= 70 else "Critical"
        sla_color = (16, 185, 129) if sla >= 90 else (234, 179, 8) if sla >= 70 else (239, 68, 68)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(50, 8, "SLA Status:")
        pdf.set_text_color(*sla_color)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"{sla_label} ({sla}%)", new_x="LMARGIN", new_y="NEXT")

        # Embedded Risk Gauge
        try:
            import tempfile
            gauge_bytes = self._render_risk_gauge(risk)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(gauge_bytes)
                tmp_path = tmp.name
            pdf.image(tmp_path, x=60, w=60)
            os.unlink(tmp_path)
            pdf.ln(4)
        except Exception as e:
            logger.warning(f"Gauge render failed: {e}")

        # 7-Day Trend Chart
        try:
            import tempfile
            trends = await self.get_dashboard_trends()
            mini_trend = trends.get("mini_trend", [])
            if mini_trend:
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(30, 30, 30)
                pdf.cell(0, 10, "7-Day CVE Trend", new_x="LMARGIN", new_y="NEXT")
                pdf.set_draw_color(0, 180, 216)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(4)
                trend_bytes = self._render_trend_chart(mini_trend)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(trend_bytes)
                    tmp_path = tmp.name
                pdf.image(tmp_path, x=15, w=140)
                os.unlink(tmp_path)
                pdf.ln(4)
        except Exception as e:
            logger.warning(f"Trend chart render failed: {e}")

        # Footer
        pdf.ln(10)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 6, "CVE Management Platform - Confidential", align="C")

        return pdf.output()

    async def export_cves_pdf(self, filters: Optional[Dict] = None) -> bytes:
        from fpdf import FPDF

        query = filters or {}
        cves = []
        cursor = self.cves_col.find(query, {"_id": 0}).sort("created_at", -1)
        async for doc in cursor:
            cves.append(doc)

        pdf = FPDF(orientation="L")
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(0, 180, 216)
        pdf.cell(0, 12, "CVE Database Export", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Total: {len(cves)} CVEs | Generated: {datetime.now(timezone.utc).isoformat()[:19]}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(6)

        # Table header
        col_widths = [35, 65, 22, 22, 18, 40, 28, 47]
        headers = ["CVE ID", "Title", "Severity", "Status", "CVSS", "Package", "Source", "Detected"]

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
        pdf.ln()

        # Table rows
        pdf.set_font("Helvetica", "", 7)
        sev_colors = {
            "critical": (239, 68, 68), "high": (249, 115, 22),
            "medium": (180, 150, 0), "low": (59, 130, 246), "info": (100, 116, 139),
        }
        for cve in cves:
            sev = cve.get("severity", "info")
            r, g, b = sev_colors.get(sev, (100, 100, 100))

            pdf.set_text_color(0, 140, 180)
            pdf.cell(col_widths[0], 7, str(cve.get("cve_id", ""))[:18], border=1)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(col_widths[1], 7, str(cve.get("title", ""))[:35], border=1)
            pdf.set_text_color(r, g, b)
            pdf.set_font("Helvetica", "B", 7)
            pdf.cell(col_widths[2], 7, sev.upper(), border=1, align="C")
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(col_widths[3], 7, str(cve.get("status", "")).replace("_", " "), border=1, align="C")
            pdf.cell(col_widths[4], 7, str(cve.get("cvss_score", "")), border=1, align="C")
            pdf.cell(col_widths[5], 7, str(cve.get("affected_package", ""))[:22], border=1)
            pdf.cell(col_widths[6], 7, str(cve.get("source", ""))[:15], border=1)
            detected = str(cve.get("detected_at", ""))[:10]
            pdf.cell(col_widths[7], 7, detected, border=1, align="C")
            pdf.ln()

        # Footer
        pdf.ln(6)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 6, "CVE Management Platform - Confidential", align="C")

        return pdf.output()

    async def export_team_pdf(self) -> bytes:
        from fpdf import FPDF

        data = await self.get_team_performance()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(0, 180, 216)
        pdf.cell(0, 12, "Team Performance Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Generated: {datetime.now(timezone.utc).isoformat()[:19]}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(6)

        if not data.get("teams"):
            pdf.set_font("Helvetica", "", 12)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 10, "No team data available.", new_x="LMARGIN", new_y="NEXT", align="C")
            return pdf.output()

        # Table
        col_widths = [40, 20, 20, 20, 22, 25, 15, 15, 15, 15]
        headers = ["Owner", "Assigned", "Open", "Resolved", "Rate (%)", "Avg MTTR", "Crit", "High", "Med", "Low"]

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 30, 30)
        for t in data["teams"]:
            pdf.cell(col_widths[0], 7, str(t["owner"])[:22], border=1)
            pdf.cell(col_widths[1], 7, str(t["assigned"]), border=1, align="C")
            pdf.cell(col_widths[2], 7, str(t["open"]), border=1, align="C")
            pdf.cell(col_widths[3], 7, str(t["resolved"]), border=1, align="C")
            rate = t["resolution_rate"]
            if rate >= 80:
                pdf.set_text_color(16, 185, 129)
            elif rate >= 50:
                pdf.set_text_color(234, 179, 8)
            else:
                pdf.set_text_color(239, 68, 68)
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(col_widths[4], 7, f"{rate}%", border=1, align="C")
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(col_widths[5], 7, f"{t['avg_resolution_hours']}h", border=1, align="C")
            pdf.cell(col_widths[6], 7, str(t["critical"]), border=1, align="C")
            pdf.cell(col_widths[7], 7, str(t["high"]), border=1, align="C")
            pdf.cell(col_widths[8], 7, str(t["medium"]), border=1, align="C")
            pdf.cell(col_widths[9], 7, str(t["low"]), border=1, align="C")
            pdf.ln()

        # Footer
        pdf.ln(8)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 6, "CVE Management Platform - Confidential", align="C")

        return pdf.output()

    # ─── Dashboard Trends (for Overview tab) ──────────────────────

    async def get_dashboard_trends(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        periods = {
            "current": (now - timedelta(days=7), now),
            "previous": (now - timedelta(days=14), now - timedelta(days=7)),
        }
        result = {}
        for period_name, (start, end) in periods.items():
            start_iso = start.isoformat()
            end_iso = end.isoformat()
            open_count = await self.cves_col.count_documents({
                "status": {"$in": ["detected", "triaged", "in_progress"]},
                "created_at": {"$lte": end_iso},
            })
            fixed_count = await self.cves_col.count_documents({
                "status": {"$in": ["fixed", "verified"]},
                "resolved_at": {"$gte": start_iso, "$lte": end_iso},
            })
            new_count = await self.cves_col.count_documents({
                "created_at": {"$gte": start_iso, "$lte": end_iso},
            })
            result[period_name] = {
                "open": open_count,
                "fixed": fixed_count,
                "new": new_count,
            }

        # 7-day mini trend for sparkline
        mini_trend = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = await self.cves_col.count_documents({
                "created_at": {"$gte": day_start.isoformat(), "$lt": day_end.isoformat()},
            })
            mini_trend.append({
                "day": day_start.strftime("%a"),
                "count": count,
            })

        # Calculate deltas
        curr = result["current"]
        prev = result["previous"]
        deltas = {
            "open_delta": curr["open"] - prev["open"],
            "fixed_delta": curr["fixed"] - prev["fixed"],
            "new_delta": curr["new"] - prev["new"],
        }

        return {
            "current_week": curr,
            "previous_week": prev,
            "deltas": deltas,
            "mini_trend": mini_trend,
        }

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
