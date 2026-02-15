"""
Notification & Reporting API Endpoints - Phase 5
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import io

from notification_service import get_notification_service

router = APIRouter(prefix="/cve/notifications", tags=["Notifications & Reporting"])
reports_router = APIRouter(prefix="/cve/reports", tags=["Reports & Exports"])


# ─── Request Models ───────────────────────────────────────────

class CreateNotification(BaseModel):
    type: str = "new_cve"
    title: str
    message: str
    severity: str = "info"
    cve_id: str = ""
    send_email: bool = False


class UpdatePreferences(BaseModel):
    email_enabled: Optional[bool] = None
    email_recipient: Optional[str] = None
    email_types: Optional[Dict[str, bool]] = None
    sla_warning_threshold: Optional[int] = None


class TestEmail(BaseModel):
    recipient: str = ""


# ─── Notification Endpoints ──────────────────────────────────

@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
    type: str = Query("", alias="type"),
):
    svc = get_notification_service()
    return await svc.list_notifications(page=page, limit=limit, unread_only=unread_only, notification_type=type)


@router.get("/unread-count")
async def get_unread_count():
    svc = get_notification_service()
    return await svc.get_unread_count()


@router.post("")
async def create_notification(body: CreateNotification):
    svc = get_notification_service()
    return await svc.create_notification(
        notification_type=body.type,
        title=body.title,
        message=body.message,
        severity=body.severity,
        cve_id=body.cve_id,
        send_email=body.send_email,
    )


@router.put("/{notification_id}/read")
async def mark_read(notification_id: str):
    svc = get_notification_service()
    return await svc.mark_read(notification_id)


@router.put("/read-all")
async def mark_all_read():
    svc = get_notification_service()
    return await svc.mark_all_read()


@router.delete("/{notification_id}")
async def dismiss_notification(notification_id: str):
    svc = get_notification_service()
    return await svc.dismiss_notification(notification_id)


# ─── SLA Check ────────────────────────────────────────────────

@router.post("/check-sla")
async def check_sla():
    svc = get_notification_service()
    return await svc.check_sla_compliance()


# ─── Preferences ──────────────────────────────────────────────

@router.get("/preferences")
async def get_preferences():
    svc = get_notification_service()
    return await svc.get_preferences()


@router.put("/preferences")
async def update_preferences(body: UpdatePreferences):
    svc = get_notification_service()
    updates = body.dict(exclude_none=True)
    return await svc.update_preferences(updates)


# ─── Test Email ───────────────────────────────────────────────

@router.post("/test-email")
async def send_test_email(body: TestEmail):
    svc = get_notification_service()
    return await svc.send_test_email(body.recipient)


# ─── Weekly Digest ────────────────────────────────────────────

@router.post("/weekly-digest")
async def generate_weekly_digest():
    svc = get_notification_service()
    return await svc.generate_weekly_digest()


# ═══════════════════════════════════════════════════════════════
# REPORT EXPORT ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@reports_router.get("/cves/csv")
async def export_cves_csv(
    status: str = Query(""),
    severity: str = Query(""),
):
    svc = get_notification_service()
    csv_data = await svc.export_cves_csv(status_filter=status, severity_filter=severity)
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cve_export.csv"},
    )


@reports_router.get("/governance/csv")
async def export_governance_csv():
    svc = get_notification_service()
    csv_data = await svc.export_governance_csv()
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=governance_report.csv"},
    )
