"""
ULN Notification Endpoints
===========================
CRUD for ULN notifications and preferences.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from uln_auth import get_current_user, User
from services.uln_notification_service import (
    create_notification,
    list_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_read,
    delete_notification,
    clear_all_notifications,
    get_preferences,
    update_preferences,
    emit_notification,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uln/notifications", tags=["ULN Notifications"])


# ── Request models ─────────────────────────────────────────────


class CreateNotificationRequest(BaseModel):
    label_id: str
    type: str = "system"
    title: str
    message: str
    severity: str = "info"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdatePreferencesRequest(BaseModel):
    enabled: Optional[bool] = None
    muted_types: Optional[List[str]] = None


# ── Notifications CRUD ─────────────────────────────────────────


@router.get("")
async def get_notifications(
    label_id: str = Query("", description="Filter by label"),
    type: str = Query("", description="Filter by notification type"),
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    result = await list_notifications(
        user_id=current_user.id,
        label_id=label_id,
        notification_type=type,
        unread_only=unread_only,
        page=page,
        limit=limit,
    )
    return result


@router.get("/unread-count")
async def unread_count(
    label_id: str = Query("", description="Filter by label"),
    current_user: User = Depends(get_current_user),
):
    return await get_unread_count(current_user.id, label_id)


@router.post("")
async def new_notification(
    req: CreateNotificationRequest,
    current_user: User = Depends(get_current_user),
):
    result = await create_notification(
        user_id=current_user.id,
        label_id=req.label_id,
        notification_type=req.type,
        title=req.title,
        message=req.message,
        severity=req.severity,
        metadata=req.metadata,
    )
    return result


@router.put("/{notification_id}/read")
async def read_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
):
    result = await mark_notification_read(current_user.id, notification_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.put("/read-all")
async def read_all(
    label_id: str = Query("", description="Filter by label"),
    current_user: User = Depends(get_current_user),
):
    return await mark_all_read(current_user.id, label_id)


@router.delete("/clear")
async def clear_all(
    label_id: str = Query("", description="Filter by label"),
    current_user: User = Depends(get_current_user),
):
    return await clear_all_notifications(current_user.id, label_id)


@router.delete("/{notification_id}")
async def remove_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
):
    result = await delete_notification(current_user.id, notification_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Preferences ────────────────────────────────────────────────


@router.get("/preferences")
async def notification_preferences(
    current_user: User = Depends(get_current_user),
):
    return await get_preferences(current_user.id)


@router.put("/preferences")
async def update_notification_preferences(
    req: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
):
    updates = {k: v for k, v in req.dict().items() if v is not None}
    return await update_preferences(current_user.id, updates)
