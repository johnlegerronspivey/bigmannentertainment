"""
CVE Reporting & Analytics API Endpoints
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import io

from cve_reporting_service import get_cve_reporting_service

router = APIRouter(prefix="/cve/reporting", tags=["CVE Reporting & Analytics"])


class SaveReportRequest(BaseModel):
    name: str
    report_type: str = "executive"
    config: Dict[str, Any] = {}


@router.get("/summary")
async def get_executive_summary(days: int = Query(30, ge=7, le=365)):
    svc = get_cve_reporting_service()
    return await svc.get_executive_summary(days=days)


@router.get("/trends")
async def get_cve_trends(days: int = Query(30, ge=7, le=90)):
    svc = get_cve_reporting_service()
    return await svc.get_cve_trends(days=days)


@router.get("/severity-trends")
async def get_severity_trends(days: int = Query(30, ge=7, le=90)):
    svc = get_cve_reporting_service()
    return await svc.get_severity_trends(days=days)


@router.get("/team-performance")
async def get_team_performance():
    svc = get_cve_reporting_service()
    return await svc.get_team_performance()


@router.get("/scanner-stats")
async def get_scanner_stats():
    svc = get_cve_reporting_service()
    return await svc.get_scanner_stats()


@router.get("/status-distribution")
async def get_status_distribution():
    svc = get_cve_reporting_service()
    return await svc.get_status_distribution()


@router.get("/export/cves")
async def export_cves_csv(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    svc = get_cve_reporting_service()
    filters = {}
    if severity:
        filters["severity"] = severity
    if status:
        filters["status"] = status
    csv_bytes = await svc.export_cves_csv(filters=filters if filters else None)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cve_export.csv"},
    )


@router.get("/export/executive")
async def export_executive_csv(days: int = Query(30, ge=7, le=365)):
    svc = get_cve_reporting_service()
    csv_bytes = await svc.export_executive_csv(days=days)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=executive_report.csv"},
    )


@router.get("/export/team")
async def export_team_csv():
    svc = get_cve_reporting_service()
    csv_bytes = await svc.export_team_csv()
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=team_performance.csv"},
    )


@router.get("/saved")
async def get_saved_reports():
    svc = get_cve_reporting_service()
    return await svc.get_saved_reports()


@router.post("/saved")
async def save_report(body: SaveReportRequest):
    svc = get_cve_reporting_service()
    return await svc.save_report(name=body.name, report_type=body.report_type, config=body.config)


@router.delete("/saved/{report_id}")
async def delete_saved_report(report_id: str):
    svc = get_cve_reporting_service()
    return await svc.delete_saved_report(report_id)
