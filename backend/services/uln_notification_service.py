"""
ULN Notification Service
=========================
Manages notifications for the Unified Label Network.
Supports creating, listing, marking read, and managing notification preferences.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config.database import db

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_id() -> str:
    return f"NOTIF-{uuid.uuid4().hex[:12].upper()}"


VALID_NOTIFICATION_TYPES = [
    "member_added",
    "member_removed",
    "governance_rule_created",
    "governance_rule_updated",
    "governance_rule_deleted",
    "dispute_filed",
    "dispute_updated",
    "dispute_resolved",
    "catalog_asset_added",
    "distribution_updated",
    "royalty_payout",
    "label_registered",
    "system",
]

VALID_SEVERITIES = ["info", "warning", "success", "error"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CREATE NOTIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def create_notification(
    user_id: str,
    label_id: str,
    notification_type: str,
    title: str,
    message: str,
    severity: str = "info",
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    if notification_type not in VALID_NOTIFICATION_TYPES:
        notification_type = "system"
    if severity not in VALID_SEVERITIES:
        severity = "info"

    now = _now_iso()
    notif_id = _gen_id()

    notification = {
        "notification_id": notif_id,
        "user_id": user_id,
        "label_id": label_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "severity": severity,
        "is_read": False,
        "metadata": metadata or {},
        "created_at": now,
    }

    await db.uln_notifications.insert_one(notification)
    logger.info(f"Notification created: {notif_id} for user {user_id}")

    return {"success": True, "notification_id": notif_id}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  EMIT NOTIFICATION (helper for other services)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def emit_notification(
    label_id: str,
    notification_type: str,
    title: str,
    message: str,
    severity: str = "info",
    actor_id: str = "",
    metadata: Dict[str, Any] = None,
):
    """Broadcast a notification to all members of a label (except the actor)."""
    members = []
    async for doc in db.label_members.find({"label_id": label_id}, {"_id": 0, "user_id": 1}):
        uid = doc.get("user_id", "")
        if uid and uid != actor_id:
            members.append(uid)

    # Also notify the label owner
    label = await db.uln_labels.find_one({"global_id.id": label_id}, {"_id": 0, "owner_user_id": 1})
    if label:
        owner_id = label.get("owner_user_id", "")
        if owner_id and owner_id != actor_id and owner_id not in members:
            members.append(owner_id)

    # If no members found, notify the actor themselves
    if not members and actor_id:
        members = [actor_id]

    for uid in members:
        # Check user preferences
        prefs = await db.uln_notification_preferences.find_one(
            {"user_id": uid}, {"_id": 0}
        )
        if prefs:
            muted_types = prefs.get("muted_types", [])
            if notification_type in muted_types:
                continue
            if not prefs.get("enabled", True):
                continue

        await create_notification(
            user_id=uid,
            label_id=label_id,
            notification_type=notification_type,
            title=title,
            message=message,
            severity=severity,
            metadata=metadata,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LIST NOTIFICATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def list_notifications(
    user_id: str,
    label_id: str = "",
    notification_type: str = "",
    unread_only: bool = False,
    page: int = 1,
    limit: int = 50,
) -> Dict[str, Any]:
    query: Dict[str, Any] = {"user_id": user_id}
    if label_id:
        query["label_id"] = label_id
    if notification_type:
        query["type"] = notification_type
    if unread_only:
        query["is_read"] = False

    total = await db.uln_notifications.count_documents(query)
    skip = (page - 1) * limit

    notifications: List[Dict] = []
    async for doc in db.uln_notifications.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit):
        notifications.append(doc)

    return {
        "success": True,
        "notifications": notifications,
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  UNREAD COUNT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_unread_count(user_id: str, label_id: str = "") -> Dict[str, Any]:
    query: Dict[str, Any] = {"user_id": user_id, "is_read": False}
    if label_id:
        query["label_id"] = label_id

    count = await db.uln_notifications.count_documents(query)
    return {"success": True, "unread_count": count}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MARK READ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def mark_notification_read(user_id: str, notification_id: str) -> Dict[str, Any]:
    result = await db.uln_notifications.update_one(
        {"notification_id": notification_id, "user_id": user_id},
        {"$set": {"is_read": True}},
    )
    if result.matched_count == 0:
        return {"success": False, "error": "Notification not found"}
    return {"success": True, "message": "Notification marked as read"}


async def mark_all_read(user_id: str, label_id: str = "") -> Dict[str, Any]:
    query: Dict[str, Any] = {"user_id": user_id, "is_read": False}
    if label_id:
        query["label_id"] = label_id

    result = await db.uln_notifications.update_many(query, {"$set": {"is_read": True}})
    return {"success": True, "updated": result.modified_count}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DELETE NOTIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def delete_notification(user_id: str, notification_id: str) -> Dict[str, Any]:
    result = await db.uln_notifications.delete_one(
        {"notification_id": notification_id, "user_id": user_id}
    )
    if result.deleted_count == 0:
        return {"success": False, "error": "Notification not found"}
    return {"success": True, "message": "Notification deleted"}


async def clear_all_notifications(user_id: str, label_id: str = "") -> Dict[str, Any]:
    query: Dict[str, Any] = {"user_id": user_id}
    if label_id:
        query["label_id"] = label_id
    result = await db.uln_notifications.delete_many(query)
    return {"success": True, "deleted": result.deleted_count}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NOTIFICATION PREFERENCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_preferences(user_id: str) -> Dict[str, Any]:
    prefs = await db.uln_notification_preferences.find_one(
        {"user_id": user_id}, {"_id": 0}
    )
    if not prefs:
        prefs = {
            "user_id": user_id,
            "enabled": True,
            "muted_types": [],
            "created_at": _now_iso(),
        }
        await db.uln_notification_preferences.insert_one(prefs)
        prefs.pop("_id", None)

    return {"success": True, "preferences": prefs}


async def update_preferences(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    allowed = ["enabled", "muted_types"]
    filtered = {k: v for k, v in updates.items() if k in allowed}
    if not filtered:
        return {"success": False, "error": "No valid fields to update"}

    filtered["updated_at"] = _now_iso()

    await db.uln_notification_preferences.update_one(
        {"user_id": user_id},
        {"$set": filtered},
        upsert=True,
    )
    return {"success": True, "message": "Preferences updated"}
