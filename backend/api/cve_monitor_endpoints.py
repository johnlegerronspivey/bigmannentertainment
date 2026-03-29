"""
Automated CVE Monitoring API Endpoints
Provides watch rules, NVD feed integration, alerts, and statistics.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from cve_monitor_service import get_cve_monitor_service

router = APIRouter(prefix="/cve-monitor", tags=["CVE Monitoring"])


class WatchCreate(BaseModel):
    name: str
    keyword: str
    watch_type: str = "keyword"
    severity_filter: str = "all"


# ─── Health ────────────────────────────────────────────────────

@router.get("/health")
async def monitor_health():
    return {"status": "healthy", "service": "CVE Automated Monitoring"}


# ─── Stats ─────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats():
    svc = get_cve_monitor_service()
    return await svc.get_stats()


# ─── Feed ──────────────────────────────────────────────────────

@router.get("/feed")
async def get_feed(
    severity: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    svc = get_cve_monitor_service()
    return await svc.get_feed(severity=severity, search=search, limit=limit)


@router.post("/feed/refresh")
async def refresh_feed(
    keyword: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30),
):
    svc = get_cve_monitor_service()
    return await svc.fetch_nvd_feed(keyword=keyword, days=days)


# ─── Watches ───────────────────────────────────────────────────

@router.get("/watches")
async def list_watches():
    svc = get_cve_monitor_service()
    return await svc.list_watches()


@router.post("/watches")
async def create_watch(body: WatchCreate):
    svc = get_cve_monitor_service()
    return await svc.create_watch(body.dict())


@router.put("/watches/{watch_id}/toggle")
async def toggle_watch(watch_id: str):
    svc = get_cve_monitor_service()
    result = await svc.toggle_watch(watch_id)
    if not result:
        raise HTTPException(status_code=404, detail="Watch not found")
    return result


@router.delete("/watches/{watch_id}")
async def delete_watch(watch_id: str):
    svc = get_cve_monitor_service()
    ok = await svc.delete_watch(watch_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Watch not found")
    return {"deleted": True}


@router.post("/watches/{watch_id}/refresh")
async def refresh_watch(watch_id: str):
    svc = get_cve_monitor_service()
    return await svc.refresh_watch(watch_id)


# ─── Alerts ────────────────────────────────────────────────────

@router.get("/alerts")
async def get_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    svc = get_cve_monitor_service()
    return await svc.get_alerts(status=status, severity=severity, limit=limit)


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    svc = get_cve_monitor_service()
    result = await svc.acknowledge_alert(alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.put("/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str):
    svc = get_cve_monitor_service()
    result = await svc.dismiss_alert(alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.post("/alerts/acknowledge-all")
async def acknowledge_all_alerts():
    svc = get_cve_monitor_service()
    return await svc.acknowledge_all_alerts()
