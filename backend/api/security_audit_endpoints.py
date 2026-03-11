"""
Security Audit API Endpoints - CVE Monitoring, Alerts & Configuration
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List

from security_audit_service import get_security_audit_service

router = APIRouter(prefix="/security", tags=["Security Audit"])


class MonitorConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    interval_hours: Optional[int] = None
    alert_on_critical: Optional[bool] = None
    alert_on_high: Optional[bool] = None
    alert_on_moderate: Optional[bool] = None
    alert_on_low: Optional[bool] = None
    email_notifications: Optional[bool] = None
    alert_email: Optional[str] = None


class AlertAction(BaseModel):
    alert_ids: Optional[List[str]] = None


class TestEmailRequest(BaseModel):
    recipient: Optional[str] = None


# ─── Health ────────────────────────────────────────────────────

@router.get("/health")
async def security_health():
    return {"status": "healthy", "service": "Security Audit Monitor"}


# ─── Audit Scanning ───────────────────────────────────────────

@router.get("/audit")
async def run_security_audit(force: bool = Query(False)):
    service = get_security_audit_service()
    return await service.run_full_audit(force=force)


@router.get("/audit/frontend")
async def run_frontend_audit():
    service = get_security_audit_service()
    return await service.run_frontend_audit()


@router.get("/audit/backend")
async def run_backend_audit():
    service = get_security_audit_service()
    return await service.run_backend_audit()


@router.get("/audit/history")
async def get_audit_history(limit: int = Query(20, ge=1, le=100)):
    service = get_security_audit_service()
    return await service.get_audit_history(limit=limit)


@router.get("/audit/trend")
async def get_trend_data(days: int = Query(30, ge=1, le=365)):
    service = get_security_audit_service()
    return await service.get_trend_data(days=days)


# ─── Monitor Configuration ────────────────────────────────────

@router.get("/monitor/config")
async def get_monitor_config():
    service = get_security_audit_service()
    return await service.get_monitor_config()


@router.put("/monitor/config")
async def update_monitor_config(body: MonitorConfigUpdate):
    service = get_security_audit_service()
    updates = body.dict(exclude_none=True)
    return await service.update_monitor_config(updates)


@router.post("/monitor/scan-now")
async def trigger_manual_scan():
    service = get_security_audit_service()
    result = await service.run_full_audit(force=True, is_scheduled=True)
    await service._check_and_alert(result)
    config = await service.get_monitor_config()
    await service.config_col.update_one(
        {"type": "monitor"},
        {"$set": {"last_scan": result["timestamp"]}, "$inc": {"total_scans": 1}},
    )
    return {"scan": result, "config": config}


# ─── Alerts ────────────────────────────────────────────────────

@router.get("/alerts")
async def get_alerts(
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
):
    service = get_security_audit_service()
    return await service.get_alerts(limit=limit, unread_only=unread_only)


@router.get("/alerts/count")
async def get_alert_count():
    service = get_security_audit_service()
    return await service.get_alert_count()


@router.post("/alerts/read")
async def mark_alerts_read(body: AlertAction):
    service = get_security_audit_service()
    count = await service.mark_alerts_read(body.alert_ids)
    return {"marked_read": count}


@router.post("/alerts/dismiss")
async def dismiss_alerts(body: AlertAction):
    service = get_security_audit_service()
    count = await service.dismiss_alerts(body.alert_ids)
    return {"dismissed": count}


# ─── Email Notifications ───────────────────────────────────────

@router.post("/email/test")
async def send_test_email(body: TestEmailRequest):
    service = get_security_audit_service()
    return await service.send_test_email(body.recipient or "")


@router.get("/email/status")
async def email_status():
    import resend as _resend
    has_key = bool(_resend.api_key)
    import os
    default_email = os.environ.get("CVE_ALERT_EMAIL", "")
    service = get_security_audit_service()
    config = await service.get_monitor_config()
    return {
        "configured": has_key and bool(config.get("alert_email")),
        "has_api_key": has_key,
        "alert_email": config.get("alert_email", default_email),
        "email_notifications_enabled": config.get("email_notifications", False),
    }
