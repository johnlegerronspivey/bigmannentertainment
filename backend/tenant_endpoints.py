"""
Multi-Tenant API Endpoints — Organization/Tenant Management
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional

from tenant_service import get_tenant_service

router = APIRouter(prefix="/tenants", tags=["Multi-Tenant"])


class TenantCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    plan: str = "free"
    owner_user_id: Optional[str] = ""
    settings: Dict[str, Any] = {}


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class UserTenantAssign(BaseModel):
    user_id: str
    tenant_id: str


# ── Tenant CRUD ──────────────────────────────────────────

@router.get("/")
async def list_tenants(limit: int = Query(50, ge=1, le=200), skip: int = Query(0, ge=0)):
    svc = get_tenant_service()
    return await svc.list_tenants(limit=limit, skip=skip)


@router.post("/")
async def create_tenant(body: TenantCreate):
    svc = get_tenant_service()
    return await svc.create_tenant(body.dict())


@router.get("/stats")
async def get_tenant_stats():
    svc = get_tenant_service()
    return await svc.get_tenant_stats()


@router.post("/seed")
async def seed_default_tenant():
    svc = get_tenant_service()
    return await svc.seed_default_tenant()


@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str):
    svc = get_tenant_service()
    result = await svc.get_tenant(tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return result


@router.put("/{tenant_id}")
async def update_tenant(tenant_id: str, body: TenantUpdate):
    svc = get_tenant_service()
    data = {k: v for k, v in body.dict().items() if v is not None}
    result = await svc.update_tenant(tenant_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return result


@router.delete("/{tenant_id}")
async def delete_tenant(tenant_id: str):
    svc = get_tenant_service()
    ok = await svc.delete_tenant(tenant_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"deleted": True}


# ── User-Tenant Association ──────────────────────────────

@router.get("/{tenant_id}/users")
async def get_tenant_users(tenant_id: str):
    svc = get_tenant_service()
    return await svc.get_tenant_users(tenant_id)


@router.post("/assign-user")
async def assign_user(body: UserTenantAssign):
    svc = get_tenant_service()
    result = await svc.assign_user_to_tenant(body.user_id, body.tenant_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/remove-user/{user_id}")
async def remove_user(user_id: str):
    svc = get_tenant_service()
    return await svc.remove_user_from_tenant(user_id)
