"""
SLA Tracker API Endpoints - Enhanced SLA Tracking
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from sla_tracker_service import get_sla_tracker_service

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
    return await svc.run_escalations()


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
