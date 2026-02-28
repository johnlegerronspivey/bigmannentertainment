"""
Ticketing Integration API Endpoints — Jira & ServiceNow
Config endpoints are auth-protected (super_admin / tenant_admin).
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import jwt
import os

from ticketing_service import get_ticketing_service, PROVIDERS
from tenant_context import get_optional_tenant_id
from rbac_service import get_cve_user, has_permission
from config.database import db as main_db
from config.settings import settings as app_settings

router = APIRouter(prefix="/cve/ticketing", tags=["Ticketing Integration"])

SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


# ── Auth helpers ──────────────────────────────────────────

async def _resolve_cve_user_and_tenant(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get cve_user + tenant_id from token."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    cve_user = await get_cve_user(user_id)
    if not cve_user:
        raise HTTPException(status_code=403, detail="CVE platform access not provisioned")

    # Resolve tenant_id
    main_user = await main_db.users.find_one({"id": user_id}, {"_id": 0, "tenant_id": 1})
    tenant_id = (main_user or {}).get("tenant_id", "") or cve_user.get("tenant_id", "")
    return cve_user, tenant_id


def _require_config_permission():
    """Only super_admin and tenant_admin can manage ticketing config."""
    async def _check(result=Depends(_resolve_cve_user_and_tenant)):
        cve_user, tenant_id = result
        role = cve_user.get("cve_role", "analyst")
        if role not in ("super_admin", "tenant_admin"):
            raise HTTPException(status_code=403, detail="Ticketing configuration requires tenant admin or super admin access")
        return cve_user, tenant_id
    return _check


# ── Models ────────────────────────────────────────────────

class TicketingConfig(BaseModel):
    provider: str = ""
    settings: Dict[str, Any] = {}


class BulkTicketRequest(BaseModel):
    severity: str = "critical"
    limit: int = 10


# ── Configuration (protected) ─────────────────────────────

@router.get("/providers")
async def list_providers():
    """List available ticketing providers with their required fields."""
    providers = {}
    for key, val in PROVIDERS.items():
        providers[key] = {
            "name": val["name"],
            "fields": val["fields"],
        }
    return {"providers": providers}


@router.get("/config")
async def get_config(tenant_id: Optional[str] = Depends(get_optional_tenant_id)):
    """Get ticketing config (masked credentials)."""
    svc = get_ticketing_service()
    return await svc.get_config_masked(tenant_id)


@router.put("/config")
async def save_config(body: TicketingConfig, result=Depends(_require_config_permission())):
    """Save ticketing config. Protected: super_admin / tenant_admin only."""
    cve_user, tenant_id = result
    svc = get_ticketing_service()
    return await svc.save_config(body.dict(), tenant_id=tenant_id)


@router.post("/test-connection")
async def test_connection(result=Depends(_require_config_permission())):
    """Test the ticketing provider connection. Protected."""
    cve_user, tenant_id = result
    svc = get_ticketing_service()
    return await svc.test_connection(tenant_id=tenant_id)


# ── Tickets ────────────────────────────────────────────────

@router.get("/tickets")
async def list_tickets(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    tenant_id: Optional[str] = Depends(get_optional_tenant_id),
):
    svc = get_ticketing_service()
    return await svc.list_tickets(limit=limit, skip=skip, tenant_id=tenant_id)


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    svc = get_ticketing_service()
    result = await svc.get_ticket(ticket_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result


@router.post("/tickets/create/{cve_id}")
async def create_ticket(cve_id: str, tenant_id: Optional[str] = Depends(get_optional_tenant_id)):
    svc = get_ticketing_service()
    result = await svc.create_ticket(cve_id, tenant_id=tenant_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/tickets/bulk")
async def bulk_create_tickets(body: BulkTicketRequest, tenant_id: Optional[str] = Depends(get_optional_tenant_id)):
    svc = get_ticketing_service()
    return await svc.bulk_create_tickets(severity=body.severity, limit=body.limit, tenant_id=tenant_id)


@router.post("/tickets/{ticket_id}/sync")
async def sync_ticket(ticket_id: str, tenant_id: Optional[str] = Depends(get_optional_tenant_id)):
    svc = get_ticketing_service()
    result = await svc.sync_ticket(ticket_id, tenant_id=tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result


@router.post("/sync-all")
async def sync_all_tickets():
    svc = get_ticketing_service()
    return await svc.sync_all_tickets()


@router.get("/stats")
async def get_stats(tenant_id: Optional[str] = Depends(get_optional_tenant_id)):
    svc = get_ticketing_service()
    return await svc.get_stats(tenant_id=tenant_id)
