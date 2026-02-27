"""
Multi-Tenant API Endpoints — Organization/Tenant Management
Protected by role-based auth: super_admin for full CRUD, tenant_admin for own-tenant views.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional
import jwt
import os

from tenant_service import get_tenant_service
from rbac_service import get_cve_user, has_permission, get_role_level

router = APIRouter(prefix="/tenants", tags=["Multi-Tenant"])

SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()


# ── Auth helpers ──────────────────────────────────────────

async def _get_cve_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
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
    if not cve_user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Your CVE platform access has been deactivated")
    return cve_user


def _require_super_admin():
    async def _check(cve_user: dict = Depends(_get_cve_user_from_token)):
        if cve_user.get("cve_role") != "super_admin":
            raise HTTPException(status_code=403, detail="Super admin access required")
        return cve_user
    return _check


def _require_tenant_view():
    """Allow super_admin (all tenants) or tenant_admin (own tenant only)."""
    async def _check(cve_user: dict = Depends(_get_cve_user_from_token)):
        role = cve_user.get("cve_role", "analyst")
        if role not in ("super_admin", "tenant_admin"):
            raise HTTPException(status_code=403, detail="Tenant admin or super admin access required")
        return cve_user
    return _check


# ── Models ────────────────────────────────────────────────

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


# ── Tenant CRUD (super_admin only) ──────────────────────────

@router.get("/")
async def list_tenants(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    cve_user: dict = Depends(_require_tenant_view()),
):
    svc = get_tenant_service()
    role = cve_user.get("cve_role")
    if role == "super_admin":
        return await svc.list_tenants(limit=limit, skip=skip)
    # tenant_admin: return only their own tenant
    tenant_id = cve_user.get("tenant_id", "")
    if not tenant_id:
        return {"items": [], "total": 0}
    tenant = await svc.get_tenant(tenant_id)
    return {"items": [tenant] if tenant else [], "total": 1 if tenant else 0}


@router.post("/")
async def create_tenant(body: TenantCreate, cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    return await svc.create_tenant(body.dict())


@router.get("/stats")
async def get_tenant_stats(cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    return await svc.get_tenant_stats()


@router.post("/seed")
async def seed_default_tenant(cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    return await svc.seed_default_tenant()


# ── Data Migration (super_admin only) ────────────────────────

@router.get("/migration-analysis")
async def migration_analysis(cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    return await svc.analyze_migration()


class MigrateDataRequest(BaseModel):
    target_tenant_id: str


@router.post("/migrate-data")
async def migrate_data(body: MigrateDataRequest, cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    result = await svc.run_data_migration(body.target_tenant_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Migration failed"))
    return result


# ── Tenant detail ────────────────────────────────────────────

@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str, cve_user: dict = Depends(_require_tenant_view())):
    role = cve_user.get("cve_role")
    # tenant_admin can only view their own tenant
    if role != "super_admin" and cve_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Cannot view other tenants")
    svc = get_tenant_service()
    result = await svc.get_tenant(tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return result


@router.put("/{tenant_id}")
async def update_tenant(tenant_id: str, body: TenantUpdate, cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    data = {k: v for k, v in body.dict().items() if v is not None}
    result = await svc.update_tenant(tenant_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return result


@router.delete("/{tenant_id}")
async def delete_tenant(tenant_id: str, cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    ok = await svc.delete_tenant(tenant_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"deleted": True}


# ── User-Tenant Association (super_admin only) ───────────────

@router.get("/{tenant_id}/users")
async def get_tenant_users(tenant_id: str, cve_user: dict = Depends(_require_tenant_view())):
    role = cve_user.get("cve_role")
    if role != "super_admin" and cve_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Cannot view other tenants' users")
    svc = get_tenant_service()
    return await svc.get_tenant_users(tenant_id)


@router.post("/assign-user")
async def assign_user(body: UserTenantAssign, cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    result = await svc.assign_user_to_tenant(body.user_id, body.tenant_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/remove-user/{user_id}")
async def remove_user(user_id: str, cve_user: dict = Depends(_require_super_admin())):
    svc = get_tenant_service()
    return await svc.remove_user_from_tenant(user_id)
