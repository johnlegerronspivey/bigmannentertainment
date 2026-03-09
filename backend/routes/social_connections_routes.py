"""
Social Connections Routes - Manage platform credentials, connections, dashboard metrics.
Supports all 119 distribution platforms from config/platforms.py.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from auth.service import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/social", tags=["Social Connections"])


# ── Models ────────────────────────────────────────────────────────────

class CredentialPayload(BaseModel):
    credentials: Dict[str, str]
    display_name: Optional[str] = None


class PostPayload(BaseModel):
    provider: str
    content: str
    media_urls: list = []


# ── Helpers ───────────────────────────────────────────────────────────

PLATFORM_ICONS = {
    "social_media": "share-2",
    "music_streaming": "music",
    "podcast": "mic",
    "radio": "radio",
    "video_streaming": "tv",
    "live_streaming": "video",
    "video_platform": "film",
    "rights_organization": "shield",
    "blockchain": "link",
    "web3_music": "headphones",
    "nft_marketplace": "image",
    "audio_social": "volume-2",
    "model_agency": "camera",
    "model_platform": "users",
    "music_licensing": "file-text",
    "music_data_exchange": "database",
}


def _build_platform_list():
    """Return a list of all platforms with metadata."""
    platforms = []
    for pid, cfg in DISTRIBUTION_PLATFORMS.items():
        platforms.append({
            "id": pid,
            "name": cfg["name"],
            "type": cfg.get("type", "other"),
            "description": cfg.get("description", ""),
            "supported_formats": cfg.get("supported_formats", []),
            "credentials_required": cfg.get("credentials_required", []),
            "icon": PLATFORM_ICONS.get(cfg.get("type", ""), "globe"),
        })
    return platforms


# ── Connections CRUD ──────────────────────────────────────────────────

@router.get("/connections")
async def list_connections(current_user=Depends(get_current_user)):
    """Return every platform + its connection status for the current user."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    # Fetch saved credentials for this user
    saved = {}
    async for doc in db.platform_credentials.find(
        {"user_id": user_id}, {"_id": 0}
    ):
        saved[doc["platform_id"]] = doc

    platforms = _build_platform_list()
    connections = []
    for p in platforms:
        cred = saved.get(p["id"])
        connections.append({
            "platform_id": p["id"],
            "provider": p["id"],
            "name": p["name"],
            "type": p["type"],
            "description": p["description"],
            "icon": p["icon"],
            "supported_formats": p["supported_formats"],
            "credentials_required": p["credentials_required"],
            "connected": cred is not None,
            "status": cred["status"] if cred else "disconnected",
            "display_name": cred.get("display_name", "") if cred else "",
            "connected_at": cred.get("connected_at", "") if cred else "",
            "username": cred.get("display_name", "") if cred else "",
        })

    return {
        "connections": connections,
        "total": len(connections),
        "connected_count": sum(1 for c in connections if c["connected"]),
    }


@router.post("/credentials/{platform_id}")
async def save_credentials(
    platform_id: str,
    payload: CredentialPayload,
    current_user=Depends(get_current_user),
):
    """Store (or update) credentials for a platform."""
    if platform_id not in DISTRIBUTION_PLATFORMS:
        raise HTTPException(status_code=404, detail="Platform not found")

    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "user_id": user_id,
        "platform_id": platform_id,
        "credentials": payload.credentials,
        "display_name": payload.display_name or "",
        "status": "connected",
        "connected_at": now,
        "updated_at": now,
    }

    await db.platform_credentials.update_one(
        {"user_id": user_id, "platform_id": platform_id},
        {"$set": doc},
        upsert=True,
    )

    return {
        "success": True,
        "platform_id": platform_id,
        "status": "connected",
        "message": f"Credentials saved for {DISTRIBUTION_PLATFORMS[platform_id]['name']}",
    }


@router.get("/credentials/{platform_id}")
async def get_credentials(platform_id: str, current_user=Depends(get_current_user)):
    """Retrieve stored credentials for a platform (masked)."""
    if platform_id not in DISTRIBUTION_PLATFORMS:
        raise HTTPException(status_code=404, detail="Platform not found")

    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    doc = await db.platform_credentials.find_one(
        {"user_id": user_id, "platform_id": platform_id}, {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="No credentials found")

    # Mask credential values for security
    masked = {}
    for key, val in doc.get("credentials", {}).items():
        if val and len(val) > 6:
            masked[key] = val[:3] + "*" * (len(val) - 6) + val[-3:]
        else:
            masked[key] = "***"

    return {
        "platform_id": platform_id,
        "name": DISTRIBUTION_PLATFORMS[platform_id]["name"],
        "credentials": masked,
        "display_name": doc.get("display_name", ""),
        "status": doc.get("status", "connected"),
        "connected_at": doc.get("connected_at", ""),
    }


@router.delete("/credentials/{platform_id}")
async def delete_credentials(platform_id: str, current_user=Depends(get_current_user)):
    """Remove credentials (disconnect) for a platform."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    result = await db.platform_credentials.delete_one(
        {"user_id": user_id, "platform_id": platform_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No credentials to remove")

    return {"success": True, "message": f"{platform_id} disconnected"}


# Alias used by the frontend's disconnect button
@router.post("/disconnect/{provider}")
async def disconnect_platform(provider: str, current_user=Depends(get_current_user)):
    return await delete_credentials(provider, current_user)


# ── Dashboard Metrics ─────────────────────────────────────────────────

@router.get("/metrics/dashboard")
async def dashboard_metrics(current_user=Depends(get_current_user)):
    """Aggregate metrics across all connected platforms."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    connected = []
    async for doc in db.platform_credentials.find(
        {"user_id": user_id, "status": "connected"}, {"_id": 0}
    ):
        pid = doc["platform_id"]
        cfg = DISTRIBUTION_PLATFORMS.get(pid, {})
        connected.append({
            "platform": pid,
            "name": cfg.get("name", pid),
            "type": cfg.get("type", "other"),
            "connected": True,
            "username": doc.get("display_name", ""),
            "followers": 0,
            "posts": 0,
            "engagement_rate": 0.0,
        })

    return {
        "platforms": connected,
        "total_followers": 0,
        "total_posts": 0,
        "avg_engagement": 0.0,
        "connected_count": len(connected),
        "total_platforms": len(DISTRIBUTION_PLATFORMS),
    }


# ── Posts ─────────────────────────────────────────────────────────────

@router.get("/posts")
async def list_posts(current_user=Depends(get_current_user)):
    """List social media posts for the user."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    posts = []
    async for doc in db.social_posts.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(50):
        posts.append(doc)

    return {"posts": posts}


@router.post("/post")
async def create_post(payload: PostPayload, current_user=Depends(get_current_user)):
    """Create a social media post."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    # Check platform is connected
    cred = await db.platform_credentials.find_one(
        {"user_id": user_id, "platform_id": payload.provider, "status": "connected"},
        {"_id": 0},
    )
    if not cred:
        raise HTTPException(status_code=400, detail=f"{payload.provider} is not connected. Please add credentials first.")

    now = datetime.now(timezone.utc).isoformat()
    post = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "platforms": [payload.provider],
        "content": payload.content,
        "media_urls": payload.media_urls,
        "status": "posted",
        "posted_at": now,
        "created_at": now,
    }
    await db.social_posts.insert_one(post)

    return {
        "success": True,
        "post_id": post["id"],
        "message": f"Posted to {DISTRIBUTION_PLATFORMS.get(payload.provider, {}).get('name', payload.provider)}",
    }


# ── Platforms list (public) ───────────────────────────────────────────

@router.get("/platforms")
async def list_all_platforms():
    """Return all available platforms grouped by category."""
    platforms = _build_platform_list()
    categories = {}
    for p in platforms:
        cat = p["type"]
        if cat not in categories:
            categories[cat] = {"label": cat.replace("_", " ").title(), "platforms": []}
        categories[cat]["platforms"].append(p)

    return {
        "platforms": platforms,
        "categories": categories,
        "total": len(platforms),
    }


# ── Bulk connect / disconnect ─────────────────────────────────────────

class BulkConnectPayload(BaseModel):
    platform_ids: list


@router.post("/bulk-connect")
async def bulk_connect(
    payload: BulkConnectPayload,
    current_user=Depends(get_current_user),
):
    """Mark multiple platforms as connected with empty credentials (placeholder)."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))
    now = datetime.now(timezone.utc).isoformat()
    connected = []

    for pid in payload.platform_ids:
        if pid not in DISTRIBUTION_PLATFORMS:
            continue
        cfg = DISTRIBUTION_PLATFORMS[pid]
        doc = {
            "user_id": user_id,
            "platform_id": pid,
            "credentials": {k: "" for k in cfg.get("credentials_required", [])},
            "display_name": "",
            "status": "connected",
            "connected_at": now,
            "updated_at": now,
        }
        await db.platform_credentials.update_one(
            {"user_id": user_id, "platform_id": pid},
            {"$set": doc},
            upsert=True,
        )
        connected.append(pid)

    return {
        "success": True,
        "connected": connected,
        "count": len(connected),
    }
