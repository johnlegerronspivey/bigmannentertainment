"""DNS Health Checker API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from auth.service import get_current_user
from models.core import User
from services.dns_health_service import (
    lookup_domain,
    health_check,
    save_lookup_history,
    get_lookup_history,
    add_monitored_domain,
    list_monitored_domains,
    remove_monitored_domain,
    refresh_monitor,
)

router = APIRouter(prefix="/dns", tags=["DNS Health Checker"])


class LookupRequest(BaseModel):
    domain: str
    record_types: Optional[list] = None


class MonitorRequest(BaseModel):
    domain: str


@router.post("/lookup")
async def dns_lookup(body: LookupRequest, current_user: User = Depends(get_current_user)):
    """Perform DNS lookup for a domain."""
    domain = body.domain.strip().lower()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
    record_types = body.record_types or ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    results = lookup_domain(domain, record_types)
    await save_lookup_history(current_user.id, domain, record_types, results)
    return {"domain": domain, "results": results}


@router.get("/health/{domain}")
async def dns_health(domain: str, current_user: User = Depends(get_current_user)):
    """Run comprehensive DNS health check on a domain."""
    domain = domain.strip().lower()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
    return health_check(domain)


@router.get("/history")
async def dns_history(
    limit: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get lookup history for the current user."""
    history = await get_lookup_history(current_user.id, limit)
    return {"history": history}


@router.post("/monitors")
async def add_monitor(body: MonitorRequest, current_user: User = Depends(get_current_user)):
    """Add a domain to monitoring."""
    domain = body.domain.strip().lower()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
    doc = await add_monitored_domain(current_user.id, domain)
    if doc is None:
        raise HTTPException(status_code=409, detail="Domain already monitored")
    return doc


@router.get("/monitors")
async def list_monitors(current_user: User = Depends(get_current_user)):
    """List all monitored domains."""
    monitors = await list_monitored_domains(current_user.id)
    return {"monitors": monitors}


@router.delete("/monitors/{monitor_id}")
async def delete_monitor(monitor_id: str, current_user: User = Depends(get_current_user)):
    """Remove a domain from monitoring."""
    deleted = await remove_monitored_domain(current_user.id, monitor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return {"status": "deleted"}


@router.post("/monitors/{monitor_id}/refresh")
async def refresh_monitor_endpoint(monitor_id: str, current_user: User = Depends(get_current_user)):
    """Run a health check on a monitored domain."""
    result = await refresh_monitor(current_user.id, monitor_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return result
