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
    get_role_permissions,
    has_permission,
    get_cve_user,
    ensure_cve_user,
    list_cve_users,
    update_cve_user_role,
    update_cve_user_status,
)

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


async def _get_current_cve_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get or auto-provision the CVE user for the JWT holder."""
    payload = await _get_jwt_payload(credentials)
    user_id = payload["sub"]
    email = payload.get("email", "")

    # Try DB lookup first
    cve_user = await get_cve_user(user_id)
    if cve_user:
        if not cve_user.get("is_active", True):
            raise HTTPException(status_code=403, detail="Your CVE platform access has been deactivated")
        return cve_user

    # Auto-provision on first access
    from motor.motor_asyncio import AsyncIOMotorClient
    cve_user = await ensure_cve_user(user_id, email, email.split("@")[0])
    return cve_user


def _require_permission(permission: str):
    """Dependency factory: raises 403 if user lacks permission."""
    async def _check(cve_user: dict = Depends(_get_current_cve_user)):
        role = cve_user.get("cve_role", "analyst")
        if not has_permission(role, permission):
            raise HTTPException(status_code=403, detail=f"Permission denied: {permission}")
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
        }
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
        "is_active": cve_user.get("is_active", True),
        "permissions": get_role_permissions(role),
        "created_at": cve_user.get("created_at"),
        "updated_at": cve_user.get("updated_at"),
    }


@router.get("/users")
async def list_users(cve_user: dict = Depends(_require_permission("users.view"))):
    """List all CVE platform users (admin only)."""
    users = await list_cve_users()
    return {"users": users, "total": len(users)}


@router.put("/users/{user_id}/role")
async def change_user_role(user_id: str, body: RoleUpdate, cve_user: dict = Depends(_require_permission("users.manage"))):
    """Change a user's CVE role (admin only)."""
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(ROLES.keys())}")

    # Prevent admin from demoting themselves if they're the only admin
    if user_id == cve_user["user_id"] and body.role != "admin":
        all_users = await list_cve_users()
        admin_count = sum(1 for u in all_users if u.get("cve_role") == "admin" and u.get("is_active", True))
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last admin. Promote another user first.")

    updated = await update_cve_user_role(user_id, body.role)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.put("/users/{user_id}/status")
async def change_user_status(user_id: str, body: StatusUpdate, cve_user: dict = Depends(_require_permission("users.manage"))):
    """Activate or deactivate a CVE user (admin only)."""
    if user_id == cve_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    updated = await update_cve_user_status(user_id, body.is_active)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.post("/users/invite")
async def invite_user(body: InviteUser, cve_user: dict = Depends(_require_permission("users.manage"))):
    """Invite/create a new CVE platform user (admin only)."""
    if body.role and body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(ROLES.keys())}")

    # Check if user with this email already exists
    existing_users = await list_cve_users()
    for u in existing_users:
        if u.get("email", "").lower() == body.email.lower():
            raise HTTPException(status_code=400, detail="User with this email already exists in CVE platform")

    # Use email-based ID for invited users (they'll be linked when they log in)
    import hashlib
    user_id = hashlib.sha256(body.email.lower().encode()).hexdigest()[:32]

    new_user = await ensure_cve_user(user_id, body.email, body.full_name)
    # Override default role if specified
    if body.role and body.role != new_user.get("cve_role"):
        new_user = await update_cve_user_role(user_id, body.role)

    return new_user
