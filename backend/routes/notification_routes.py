"""
Real-time Notifications - Notify creators of new subscribers, messages, etc.
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db
from auth.service import get_current_user
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ── WebSocket connection manager ──────────────────────────────
class NotificationWSManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, user_id: str):
        await ws.accept()
        self._connections.setdefault(user_id, []).append(ws)

    def disconnect(self, ws: WebSocket, user_id: str):
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self._connections.pop(user_id, None)

    async def push(self, user_id: str, payload: dict):
        for ws in self._connections.get(user_id, []):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                pass


ws_manager = NotificationWSManager()


# ── Helper: create + push a notification ──────────────────────
async def create_notification(
    recipient_id: str,
    notif_type: str,
    title: str,
    message: str,
    link: str = "",
    sender_id: str = "",
    sender_name: str = "",
):
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": recipient_id,
        "type": notif_type,
        "title": title,
        "message": message,
        "link": link,
        "sender_id": sender_id,
        "sender_name": sender_name,
        "read": False,
        "created_at": now,
    }
    result = await db.notifications.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    doc["created_at"] = now.isoformat()

    # Push to any connected WebSocket clients
    await ws_manager.push(recipient_id, {"type": "new_notification", "notification": doc})
    return doc


# ── Serialization ─────────────────────────────────────────────
def _serialize(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    if "created_at" in doc and isinstance(doc["created_at"], datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


# ── REST endpoints ────────────────────────────────────────────
@router.get("")
async def list_notifications(
    skip: int = 0,
    limit: int = 30,
    unread_only: bool = False,
    current_user=Depends(get_current_user),
):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
    cursor = db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        items.append(_serialize(doc))
    total = await db.notifications.count_documents(query)
    unread = await db.notifications.count_documents({"user_id": user_id, "read": False})
    return {"items": items, "total": total, "unread": unread}


@router.get("/unread-count")
async def unread_count(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    count = await db.notifications.count_documents({"user_id": user_id, "read": False})
    return {"unread": count}


@router.put("/{notif_id}/read")
async def mark_read(notif_id: str, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    try:
        result = await db.notifications.update_one(
            {"_id": ObjectId(notif_id), "user_id": user_id},
            {"$set": {"read": True}},
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid notification ID")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Marked as read"}


@router.put("/read-all")
async def mark_all_read(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    await db.notifications.update_many(
        {"user_id": user_id, "read": False},
        {"$set": {"read": True}},
    )
    return {"message": "All notifications marked as read"}


@router.delete("/{notif_id}")
async def delete_notification(notif_id: str, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    try:
        result = await db.notifications.delete_one(
            {"_id": ObjectId(notif_id), "user_id": user_id}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid notification ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}
