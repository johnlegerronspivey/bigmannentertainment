"""
Phase 6: RBAC API Endpoints for CVE Management Platform
Prefix: /api/cve/rbac
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import os

from rbac_service import (
    ROLES,
    ROLE_HIERARCHY,
    get_role_permissions,
    has_permission,
    get_role_level,
    can_assign_role,
    get_cve_user,
    ensure_cve_user,
    list_cve_users,
    update_cve_user_role,
    update_cve_user_status,
    sync_cve_users_tenant_ids,
)
from config.database import db as main_db
from config.settings import settings

router = APIRouter(prefix="/cve/rbac", tags=["CVE RBAC"])

SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()


# ── Auth helpers ──────────────────────────────────────────────

async def _get_jwt_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def _resolve_tenant_id(user_id: str) -> str:
    """Lookup the tenant_id from the main users collection."""
    user = await main_db.users.find_one({"id": user_id}, {"_id": 0, "tenant_id": 1})
    return (user or {}).get("tenant_id", "")


async def _get_current_cve_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get or auto-provision the CVE user for the JWT holder."""
    payload = await _get_jwt_payload(credentials)
    user_id = payload["sub"]
    email = payload.get("email", "")

    # Resolve tenant_id from main user
    tenant_id = await _resolve_tenant_id(user_id)

    # Try DB lookup first
    cve_user = await get_cve_user(user_id)
    if cve_user:
        if not cve_user.get("is_active", True):
            raise HTTPException(status_code=403, detail="Your CVE platform access has been deactivated")
        # Backfill tenant_id if missing
        if not cve_user.get("tenant_id") and tenant_id:
            cve_user["tenant_id"] = tenant_id
        return cve_user

    # Auto-provision on first access
    cve_user = await ensure_cve_user(user_id, email, email.split("@")[0], tenant_id=tenant_id)
    return cve_user


def _require_permission(permission: str):
    """Dependency factory: raises 403 if user lacks permission."""
    async def _check(cve_user: dict = Depends(_get_current_cve_user)):
        role = cve_user.get("cve_role", "analyst")
        if not has_permission(role, permission):
            raise HTTPException(status_code=403, detail=f"Permission denied: {permission}")
        return cve_user
    return _check


def _require_role(*allowed_roles):
    """Dependency factory: raises 403 if user's role is not in allowed_roles."""
    async def _check(cve_user: dict = Depends(_get_current_cve_user)):
        role = cve_user.get("cve_role", "analyst")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Requires one of: {', '.join(allowed_roles)}")
        return cve_user
    return _check


# ── Models ────────────────────────────────────────────────────

class RoleUpdate(BaseModel):
    role: str

class StatusUpdate(BaseModel):
    is_active: bool

class InviteUser(BaseModel):
    email: str
    full_name: str
    role: Optional[str] = "analyst"


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/roles")
async def get_roles():
    """List all available CVE roles and their permissions."""
    return {
        "roles": {
            k: {"label": v["label"], "description": v["description"], "permissions": v["permissions"]}
            for k, v in ROLES.items()
        },
        "hierarchy": ROLE_HIERARCHY,
    }


@router.get("/me")
async def get_my_cve_profile(cve_user: dict = Depends(_get_current_cve_user)):
    """Get current user's CVE role and permissions."""
    role = cve_user.get("cve_role", "analyst")
    return {
        "user_id": cve_user["user_id"],
        "email": cve_user.get("email", ""),
        "full_name": cve_user.get("full_name", ""),
        "cve_role": role,
        "tenant_id": cve_user.get("tenant_id", ""),
        "is_active": cve_user.get("is_active", True),
        "permissions": get_role_permissions(role),
        "role_level": get_role_level(role),
        "created_at": cve_user.get("created_at"),
        "updated_at": cve_user.get("updated_at"),
    }


@router.get("/users")
async def list_users(cve_user: dict = Depends(_require_permission("users.view"))):
    """List CVE platform users. super_admin sees all; others see own tenant only."""
    role = cve_user.get("cve_role", "analyst")
    if role == "super_admin":
        users = await list_cve_users()
    else:
        tenant_id = cve_user.get("tenant_id", "")
        users = await list_cve_users(tenant_id=tenant_id) if tenant_id else []
    return {"users": users, "total": len(users)}


@router.put("/users/{user_id}/role")
async def change_user_role(user_id: str, body: RoleUpdate, cve_user: dict = Depends(_require_permission("users.manage"))):
    """Change a user's CVE role. Enforces role hierarchy."""
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(ROLES.keys())}")

    actor_role = cve_user.get("cve_role", "analyst")

    # Enforce hierarchy: actor cannot assign a role >= their own level
    if not can_assign_role(actor_role, body.role):
        raise HTTPException(status_code=403, detail=f"Cannot assign role '{body.role}'. You can only assign roles below your own level ({actor_role}).")

    # Tenant scoping: non-super_admin can only manage users within their tenant
    if actor_role != "super_admin":
        target_user = await get_cve_user(user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        if target_user.get("tenant_id") != cve_user.get("tenant_id"):
            raise HTTPException(status_code=403, detail="Cannot manage users outside your tenant")

    # Prevent removing the last super_admin
    if user_id == cve_user["user_id"] and body.role != actor_role:
        if actor_role == "super_admin":
            all_users = await list_cve_users()
            sa_count = sum(1 for u in all_users if u.get("cve_role") == "super_admin" and u.get("is_active", True))
            if sa_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot demote the last super admin. Promote another user first.")

    updated = await update_cve_user_role(user_id, body.role)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.put("/users/{user_id}/status")
async def change_user_status(user_id: str, body: StatusUpdate, cve_user: dict = Depends(_require_permission("users.manage"))):
    """Activate or deactivate a CVE user."""
    if user_id == cve_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    actor_role = cve_user.get("cve_role", "analyst")

    # Tenant scoping: non-super_admin can only manage users within their tenant
    if actor_role != "super_admin":
        target_user = await get_cve_user(user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        if target_user.get("tenant_id") != cve_user.get("tenant_id"):
            raise HTTPException(status_code=403, detail="Cannot manage users outside your tenant")
        # Cannot deactivate someone of higher or equal role
        target_level = get_role_level(target_user.get("cve_role", "analyst"))
        actor_level = get_role_level(actor_role)
        if target_level >= actor_level:
            raise HTTPException(status_code=403, detail="Cannot change status of a user with equal or higher role")

    updated = await update_cve_user_status(user_id, body.is_active)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.post("/users/invite")
async def invite_user(body: InviteUser, cve_user: dict = Depends(_require_permission("users.manage"))):
    """Invite/create a new CVE platform user. Enforces role hierarchy."""
    if body.role and body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(ROLES.keys())}")

    actor_role = cve_user.get("cve_role", "analyst")
    target_role = body.role or "analyst"

    # Enforce hierarchy
    if not can_assign_role(actor_role, target_role):
        raise HTTPException(status_code=403, detail=f"Cannot invite with role '{target_role}'. You can only assign roles below your own level.")

    # Check if user with this email already exists
    existing_users = await list_cve_users()
    for u in existing_users:
        if u.get("email", "").lower() == body.email.lower():
            raise HTTPException(status_code=400, detail="User with this email already exists in CVE platform")

    # Use email-based ID for invited users
    import hashlib
    user_id = hashlib.sha256(body.email.lower().encode()).hexdigest()[:32]

    # Invited user inherits the inviter's tenant
    tenant_id = cve_user.get("tenant_id", "")

    new_user = await ensure_cve_user(user_id, body.email, body.full_name, tenant_id=tenant_id)
    # Override default role if specified
    if target_role != new_user.get("cve_role"):
        new_user = await update_cve_user_role(user_id, target_role)

    return new_user


@router.post("/sync-tenant-ids")
async def sync_tenant_ids(cve_user: dict = Depends(_require_role("super_admin"))):
    """Backfill tenant_id on cve_users from main users collection. Super admin only."""
    result = await sync_cve_users_tenant_ids()
    return result
