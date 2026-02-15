"""
Governance API Endpoints - Phase 4: Governance Dashboards & Advanced Analytics
"""

from fastapi import APIRouter, Query
from governance_service import get_governance_service

router = APIRouter(prefix="/cve/governance", tags=["Governance & Analytics"])


@router.get("/metrics")
async def get_governance_metrics():
    svc = get_governance_service()
    return await svc.get_governance_metrics()


@router.get("/trends")
async def get_trends(days: int = Query(30, ge=7, le=90)):
    svc = get_governance_service()
    return await svc.get_trends(days=days)


@router.get("/sla")
async def get_sla_compliance():
    svc = get_governance_service()
    return await svc.get_sla_compliance()


@router.get("/ownership")
async def get_ownership_stats():
    svc = get_governance_service()
    return await svc.get_ownership_stats()


@router.get("/mttr")
async def get_mttr():
    svc = get_governance_service()
    return await svc.get_mttr()


@router.get("/scan-activity")
async def get_scan_activity():
    svc = get_governance_service()
    return await svc.get_scan_activity()
