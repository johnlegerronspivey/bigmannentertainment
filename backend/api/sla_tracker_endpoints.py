"""
SLA Tracker API Endpoints - Enhanced SLA Tracking (Phase 2)
Includes auto-escalation config, escalation workflows, notification prefs, and digest.
"""

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from sla_tracker_service import get_sla_tracker_service
from tenant_context import get_optional_tenant_id

router = APIRouter(prefix="/cve/sla", tags=["SLA Tracker"])


class EscalationRule(BaseModel):
    id: Optional[str] = None
    level: int = 1
    name: str
    threshold_pct: float = 100
    action: str = "notify"
    notify_role: str = "manager"
    description: str = ""


class EscalationRulesUpdate(BaseModel):
    rules: List[EscalationRule]


class AutoEscalationConfig(BaseModel):
    enabled: bool = False
    interval_minutes: int = 60
    email_on_warning: bool = True
    email_on_breach: bool = True
    email_on_escalation: bool = True
    digest_enabled: bool = False
    digest_cron_hour: int = 8
    recipients: List[str] = []


class NotificationPreferences(BaseModel):
    notify_on_warning: bool = True
    notify_on_breach: bool = True
    notify_on_escalation: bool = True
    muted_severities: List[str] = []
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"
    per_severity: Dict[str, Dict[str, bool]] = {}


class EscalationAction(BaseModel):
    performed_by: str = ""
    assignee: str = ""
    resolution_note: str = ""


# ─── SLA Policies ─────────────────────────────────────────────

class SLAPolicy(BaseModel):
    severity: str
    sla_hours: int


class SLAPoliciesUpdate(BaseModel):
    policies: List[SLAPolicy]


@router.get("/policies")
async def get_sla_policies():
    svc = get_sla_tracker_service()
    return await svc.get_sla_policies()


@router.put("/policies")
async def update_sla_policies(body: SLAPoliciesUpdate):
    svc = get_sla_tracker_service()
    return await svc.update_sla_policies([p.dict() for p in body.policies])


# ─── SLA Metrics & Analytics ─────────────────────────────────

@router.get("/metrics")
async def get_sla_metrics():
    svc = get_sla_tracker_service()
    return await svc.get_sla_metrics()


@router.get("/team-performance")
async def get_team_performance():
    svc = get_sla_tracker_service()
    return await svc.get_team_performance()


@router.get("/breach-timeline")
async def get_breach_timeline(days: int = Query(30, ge=7, le=90)):
    svc = get_sla_tracker_service()
    return await svc.get_breach_timeline(days=days)


# ─── Phase 1 Endpoints ───────────────────────────────────────

@router.get("/dashboard")
async def get_sla_dashboard():
    svc = get_sla_tracker_service()
    return await svc.get_sla_dashboard()


@router.get("/at-risk")
async def get_at_risk_cves(limit: int = Query(50, ge=1, le=200)):
    svc = get_sla_tracker_service()
    return await svc.get_at_risk_cves(limit=limit)


@router.get("/escalation-rules")
async def get_escalation_rules():
    svc = get_sla_tracker_service()
    return await svc.get_escalation_rules()


@router.put("/escalation-rules")
async def update_escalation_rules(body: EscalationRulesUpdate):
    svc = get_sla_tracker_service()
    rules_dicts = [r.dict() for r in body.rules]
    return await svc.update_escalation_rules(rules_dicts)


@router.post("/run-escalations")
async def run_escalations():
    svc = get_sla_tracker_service()
    return await svc.run_escalations_with_notifications()


@router.get("/escalation-log")
async def get_escalation_log(limit: int = Query(50, ge=1, le=200)):
    svc = get_sla_tracker_service()
    return await svc.get_escalation_log(limit=limit)


@router.get("/history")
async def get_sla_history(days: int = Query(30, ge=7, le=90)):
    svc = get_sla_tracker_service()
    return await svc.get_sla_history(days=days)


@router.post("/snapshot")
async def take_snapshot():
    svc = get_sla_tracker_service()
    return await svc.take_snapshot()


# ─── Phase 2: Auto-Escalation Config ─────────────────────────

@router.get("/auto-escalation-config")
async def get_auto_escalation_config():
    svc = get_sla_tracker_service()
    return await svc.get_auto_escalation_config()


@router.put("/auto-escalation-config")
async def update_auto_escalation_config(body: AutoEscalationConfig):
    svc = get_sla_tracker_service()
    return await svc.update_auto_escalation_config(body.dict())


# ─── Phase 2: Notification Preferences ───────────────────────

@router.get("/notification-preferences")
async def get_notification_preferences(user_id: Optional[str] = Query(None)):
    svc = get_sla_tracker_service()
    return await svc.get_notification_preferences(user_id=user_id)


@router.put("/notification-preferences")
async def update_notification_preferences(body: NotificationPreferences, user_id: Optional[str] = Query(None)):
    svc = get_sla_tracker_service()
    return await svc.update_notification_preferences(body.dict(), user_id=user_id)


@router.get("/notification-preferences/check")
async def check_should_notify(
    user_id: str = Query(...),
    event_type: str = Query("sla_breach"),
    severity: str = Query("critical"),
):
    """Check if a specific user should receive a given notification type."""
    svc = get_sla_tracker_service()
    return await svc.should_notify_user(user_id, event_type, severity)


# ─── Phase 2: Escalation Workflow ────────────────────────────

@router.post("/escalation-log/{log_id}/acknowledge")
async def acknowledge_escalation(log_id: str, body: EscalationAction):
    svc = get_sla_tracker_service()
    return await svc.acknowledge_escalation(log_id, acknowledged_by=body.performed_by)


@router.post("/escalation-log/{log_id}/assign")
async def assign_escalation(log_id: str, body: EscalationAction):
    svc = get_sla_tracker_service()
    return await svc.assign_escalation(log_id, assignee=body.assignee, assigned_by=body.performed_by)


@router.post("/escalation-log/{log_id}/resolve")
async def resolve_escalation(log_id: str, body: EscalationAction):
    svc = get_sla_tracker_service()
    return await svc.resolve_escalation(log_id, resolution_note=body.resolution_note, resolved_by=body.performed_by)


@router.get("/escalation-stats")
async def get_escalation_stats():
    svc = get_sla_tracker_service()
    return await svc.get_escalation_stats()


# ─── Phase 2: SLA Digest ─────────────────────────────────────

@router.post("/send-digest")
async def send_sla_digest():
    svc = get_sla_tracker_service()
    return await svc.send_sla_digest()
