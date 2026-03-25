"""
ULN Label Members Endpoints
============================
Manages label membership: who belongs to which label, role management,
and the /me/labels endpoint for label switching context.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from uln_auth import get_current_user, get_current_admin_user, User, db
from services.uln_label_members_service import (
    add_member,
    remove_member,
    update_member_role,
    get_label_members,
    get_user_labels,
    check_permission,
    ensure_owner_membership,
    VALID_ROLES,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uln", tags=["ULN Label Members"])


class AddMemberRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: str = "viewer"


class UpdateRoleRequest(BaseModel):
    role: str


# ── My Labels (for label switcher) ──────────────────────────────────


@router.get("/me/labels")
async def my_labels(current_user: User = Depends(get_current_user)):
    """
    Get all labels the current user belongs to.
    Used by the Label Switcher in the frontend.
    """
    labels = await get_user_labels(current_user.id)

    # If user has no memberships yet, check if they're an admin and auto-assign
    # them to all labels (backward-compat for existing system)
    if not labels and (current_user.is_admin or current_user.role in ("admin", "super_admin")):
        async for lbl in db.uln_labels.find({"status": "active"}, {"_id": 0, "global_id": 1}):
            lid = lbl.get("global_id", {}).get("id")
            if lid:
                await ensure_owner_membership(lid, current_user.id)
        labels = await get_user_labels(current_user.id)

    return {
        "labels": labels,
        "count": len(labels),
    }


# ── Label Members CRUD ──────────────────────────────────────────────


@router.get("/labels/{label_id}/members")
async def list_members(label_id: str, current_user: User = Depends(get_current_user)):
    """List all members of a label."""
    has_access = await check_permission(label_id, current_user.id, "viewer")
    # Admins can always view
    if not has_access and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not a member of this label")
    members = await get_label_members(label_id)
    return {"members": members, "count": len(members), "label_id": label_id}


@router.post("/labels/{label_id}/members")
async def add_label_member(
    label_id: str,
    req: AddMemberRequest,
    current_user: User = Depends(get_current_user),
):
    """Add a member to a label. Requires admin+ role on the label."""
    has_perm = await check_permission(label_id, current_user.id, "admin")
    if not has_perm and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only label admins or owners can add members")

    # Resolve user_id from email if needed
    target_user_id = req.user_id
    if not target_user_id and req.email:
        user = await db.users.find_one({"email": req.email}, {"_id": 0, "id": 1})
        if not user:
            raise HTTPException(status_code=404, detail=f"No user found with email {req.email}")
        target_user_id = user["id"]

    if not target_user_id:
        raise HTTPException(status_code=400, detail="Provide user_id or email")

    result = await add_member(label_id, target_user_id, req.role, current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/labels/{label_id}/members/{user_id}/role")
async def change_member_role(
    label_id: str,
    user_id: str,
    req: UpdateRoleRequest,
    current_user: User = Depends(get_current_user),
):
    """Change a member's role. Requires owner role on the label."""
    has_perm = await check_permission(label_id, current_user.id, "owner")
    if not has_perm and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only label owners can change roles")

    result = await update_member_role(label_id, user_id, req.role, current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/labels/{label_id}/members/{user_id}")
async def remove_label_member(
    label_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    """Remove a member from a label. Requires admin+ role, or self-removal."""
    is_self = user_id == current_user.id
    has_perm = await check_permission(label_id, current_user.id, "admin")
    if not has_perm and not is_self and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only label admins or owners can remove members")

    result = await remove_member(label_id, user_id, current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/labels/{label_id}/my-role")
async def my_role_in_label(label_id: str, current_user: User = Depends(get_current_user)):
    """Check the current user's role in a specific label."""
    doc = await db.label_members.find_one(
        {"label_id": label_id, "user_id": current_user.id}, {"_id": 0}
    )
    if not doc:
        return {"member": False, "role": None, "label_id": label_id}
    return {"member": True, "role": doc["role"], "label_id": label_id, "joined_at": doc.get("joined_at")}


@router.get("/roles")
async def list_roles(current_user: User = Depends(get_current_user)):
    """Return valid roles and their descriptions."""
    return {
        "roles": [
            {"id": "owner", "label": "Owner", "level": 4, "description": "Full control over label, can manage all members and settings"},
            {"id": "admin", "label": "Admin", "level": 3, "description": "Can manage members, content, and distribution"},
            {"id": "a_and_r", "label": "A&R", "level": 2, "description": "Can manage catalog, scouting, and artist relations"},
            {"id": "viewer", "label": "Viewer", "level": 1, "description": "Read-only access to label data and analytics"},
        ]
    }
