"""
ULN Label Members Service
=========================
Manages label membership: who belongs to which label and in what role.
Roles: owner, admin, a_and_r, viewer
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from config.database import db

logger = logging.getLogger(__name__)

VALID_ROLES = {"owner", "admin", "a_and_r", "viewer"}

ROLE_HIERARCHY = {
    "owner": 4,
    "admin": 3,
    "a_and_r": 2,
    "viewer": 1,
}


async def add_member(label_id: str, user_id: str, role: str, added_by: str) -> Dict[str, Any]:
    """Add a user to a label with a specific role."""
    if role not in VALID_ROLES:
        return {"success": False, "error": f"Invalid role '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}"}

    # Check label exists
    label = await db.uln_labels.find_one({"global_id.id": label_id}, {"_id": 0, "global_id": 1, "metadata_profile.name": 1})
    if not label:
        return {"success": False, "error": "Label not found"}

    # Check if already a member
    existing = await db.label_members.find_one({"label_id": label_id, "user_id": user_id})
    if existing:
        return {"success": False, "error": "User is already a member of this label"}

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "label_id": label_id,
        "user_id": user_id,
        "role": role,
        "added_by": added_by,
        "joined_at": now,
        "updated_at": now,
    }
    await db.label_members.insert_one(doc)

    # Audit
    await db.uln_audit_trail.insert_one({
        "action_type": "member_added",
        "actor_id": added_by,
        "resource_type": "label_member",
        "resource_id": label_id,
        "description": f"Added user {user_id} as {role} to label {label_id}",
        "changes": {"user_id": user_id, "role": role},
        "timestamp": now,
    })

    # Emit notification
    try:
        from services.uln_notification_service import emit_notification
        label_name = label.get("metadata_profile", {}).get("name", label_id)
        asyncio.ensure_future(emit_notification(
            label_id=label_id,
            notification_type="member_added",
            title="New Member Added",
            message=f"User was added as {role} to {label_name}",
            severity="info",
            actor_id=added_by,
            metadata={"user_id": user_id, "role": role},
        ))
    except Exception:
        pass

    return {"success": True, "label_id": label_id, "user_id": user_id, "role": role}


async def remove_member(label_id: str, user_id: str, removed_by: str) -> Dict[str, Any]:
    """Remove a user from a label."""
    # OWNERSHIP PROTECTION: Cannot remove the protected owner from any label
    from utils.ownership_guard import block_owner_removal_from_label, log_ownership_violation
    blocked = block_owner_removal_from_label(label_id, user_id)
    if blocked:
        await log_ownership_violation(db, removed_by, "remove_member", {"label_id": label_id, "user_id": user_id})
        return {"success": False, "error": blocked}

    existing = await db.label_members.find_one({"label_id": label_id, "user_id": user_id})
    if not existing:
        return {"success": False, "error": "User is not a member of this label"}

    if existing.get("role") == "owner":
        # Count owners — can't remove the last owner
        owner_count = await db.label_members.count_documents({"label_id": label_id, "role": "owner"})
        if owner_count <= 1:
            return {"success": False, "error": "Cannot remove the last owner of a label"}

    await db.label_members.delete_one({"label_id": label_id, "user_id": user_id})

    now = datetime.now(timezone.utc).isoformat()
    await db.uln_audit_trail.insert_one({
        "action_type": "member_removed",
        "actor_id": removed_by,
        "resource_type": "label_member",
        "resource_id": label_id,
        "description": f"Removed user {user_id} from label {label_id}",
        "changes": {"user_id": user_id},
        "timestamp": now,
    })

    return {"success": True, "message": f"User {user_id} removed from label {label_id}"}


async def update_member_role(label_id: str, user_id: str, new_role: str, updated_by: str) -> Dict[str, Any]:
    """Change a member's role within a label."""
    # OWNERSHIP PROTECTION: Cannot change the protected owner's role
    from utils.ownership_guard import block_owner_role_change, log_ownership_violation
    blocked = block_owner_role_change(label_id, user_id, new_role)
    if blocked:
        await log_ownership_violation(db, updated_by, "update_member_role", {"label_id": label_id, "user_id": user_id, "new_role": new_role})
        return {"success": False, "error": blocked}

    if new_role not in VALID_ROLES:
        return {"success": False, "error": f"Invalid role '{new_role}'"}

    existing = await db.label_members.find_one({"label_id": label_id, "user_id": user_id})
    if not existing:
        return {"success": False, "error": "User is not a member of this label"}

    old_role = existing.get("role")
    if old_role == "owner" and new_role != "owner":
        owner_count = await db.label_members.count_documents({"label_id": label_id, "role": "owner"})
        if owner_count <= 1:
            return {"success": False, "error": "Cannot demote the last owner"}

    now = datetime.now(timezone.utc).isoformat()
    await db.label_members.update_one(
        {"label_id": label_id, "user_id": user_id},
        {"$set": {"role": new_role, "updated_at": now}},
    )

    await db.uln_audit_trail.insert_one({
        "action_type": "member_role_changed",
        "actor_id": updated_by,
        "resource_type": "label_member",
        "resource_id": label_id,
        "description": f"Changed user {user_id} role from {old_role} to {new_role}",
        "changes": {"user_id": user_id, "old_role": old_role, "new_role": new_role},
        "timestamp": now,
    })

    return {"success": True, "user_id": user_id, "old_role": old_role, "new_role": new_role}


async def get_label_members(label_id: str) -> List[Dict[str, Any]]:
    """Get all members of a label with user info."""
    members = []
    async for doc in db.label_members.find({"label_id": label_id}, {"_id": 0}):
        # Enrich with user data
        user = await db.users.find_one({"id": doc["user_id"]}, {"_id": 0, "id": 1, "email": 1, "full_name": 1, "role": 1})
        members.append({
            "user_id": doc["user_id"],
            "label_role": doc["role"],
            "joined_at": doc.get("joined_at", ""),
            "email": user.get("email", "") if user else "",
            "full_name": user.get("full_name", "") if user else "",
            "system_role": user.get("role", "user") if user else "user",
        })
    # Sort: owners first, then by role hierarchy
    members.sort(key=lambda m: -ROLE_HIERARCHY.get(m["label_role"], 0))
    return members


async def get_user_labels(user_id: str) -> List[Dict[str, Any]]:
    """Get all labels a user belongs to, with their role in each."""
    labels = []
    async for doc in db.label_members.find({"user_id": user_id}, {"_id": 0}):
        label = await db.uln_labels.find_one({"global_id.id": doc["label_id"]}, {"_id": 0})
        if label:
            member_count = await db.label_members.count_documents({"label_id": doc["label_id"]})
            labels.append({
                "label_id": doc["label_id"],
                "role": doc["role"],
                "joined_at": doc.get("joined_at", ""),
                "name": label.get("metadata_profile", {}).get("name", "Unknown"),
                "label_type": label.get("label_type", "unknown"),
                "status": label.get("status", "unknown"),
                "member_count": member_count,
            })
    return labels


async def check_permission(label_id: str, user_id: str, min_role: str = "viewer") -> bool:
    """Check if a user has at least the given role for a label."""
    doc = await db.label_members.find_one({"label_id": label_id, "user_id": user_id})
    if not doc:
        return False
    user_level = ROLE_HIERARCHY.get(doc["role"], 0)
    required_level = ROLE_HIERARCHY.get(min_role, 0)
    return user_level >= required_level


async def ensure_owner_membership(label_id: str, owner_user_id: str):
    """Ensure the label creator is added as owner. Called after label registration."""
    existing = await db.label_members.find_one({"label_id": label_id, "user_id": owner_user_id})
    if not existing:
        now = datetime.now(timezone.utc).isoformat()
        await db.label_members.insert_one({
            "label_id": label_id,
            "user_id": owner_user_id,
            "role": "owner",
            "added_by": "system",
            "joined_at": now,
            "updated_at": now,
        })
