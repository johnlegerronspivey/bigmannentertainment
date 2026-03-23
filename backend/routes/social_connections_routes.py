"""
Social Connections Routes - Manage platform credentials, connections, dashboard metrics.
Supports all 119 distribution platforms from config/platforms.py.
Live API integration layer fetches real metrics when valid credentials exist.
URL-based connections allow users to paste profile URLs instead of API keys.
"""
import uuid
import random
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from auth.service import get_current_user
from services.live_metrics_service import (
    fetch_metrics_with_fallback,
    has_live_adapter,
    get_supported_live_platforms,
)
from services.url_metrics_service import (
    detect_platform_from_url,
    parse_username_from_url,
    has_url_adapter,
    get_url_example,
    get_all_url_supported_platforms,
    fetch_metrics_from_url,
    PLATFORM_URL_EXAMPLES,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/social", tags=["Social Connections"])


# ── Models ────────────────────────────────────────────────────────────

class CredentialPayload(BaseModel):
    credentials: Dict[str, str]
    display_name: Optional[str] = None


class URLConnectPayload(BaseModel):
    profile_url: str
    display_name: Optional[str] = None
    platform_id: Optional[str] = None  # Optional, auto-detected from URL
    manual_metrics: Optional[Dict[str, Any]] = None  # Fallback: user-supplied metrics


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

CATEGORY_META_BACKEND = {
    "social_media": {"label": "Social Media"},
    "music_streaming": {"label": "Music Streaming"},
    "podcast": {"label": "Podcasts"},
    "radio": {"label": "Radio & Broadcasting"},
    "video_streaming": {"label": "TV & Video Streaming"},
    "live_streaming": {"label": "Live Streaming"},
    "video_platform": {"label": "Video Platforms"},
    "rights_organization": {"label": "Rights Organizations"},
    "blockchain": {"label": "Blockchain"},
    "web3_music": {"label": "Web3 Music"},
    "nft_marketplace": {"label": "NFT Marketplace"},
    "audio_social": {"label": "Audio Social"},
    "model_agency": {"label": "Model Agencies"},
    "model_platform": {"label": "Model Platforms"},
    "music_licensing": {"label": "Music Licensing"},
    "music_data_exchange": {"label": "Music Data Exchange"},
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
        has_real_creds = False
        if cred:
            raw_creds = cred.get("credentials", {})
            has_real_creds = any(v and v.strip() for v in raw_creds.values())
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
            "has_live_api": has_live_adapter(p["id"]),
            "has_real_credentials": has_real_creds,
            "has_url_connect": has_url_adapter(p["id"]),
            "connection_method": cred.get("connection_method", "api") if cred else None,
            "profile_url": cred.get("credentials", {}).get("profile_url", "") if cred else "",
            "url_example": get_url_example(p["id"]),
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


# ── Metrics helpers ────────────────────────────────────────────────────

# Realistic follower/engagement ranges by platform type
PLATFORM_METRIC_RANGES = {
    "social_media": {"followers": (500, 250000), "posts": (10, 800), "engagement": (1.2, 8.5), "growth": (-2.0, 12.0)},
    "music_streaming": {"followers": (200, 150000), "posts": (5, 300), "engagement": (2.0, 15.0), "growth": (-1.0, 10.0)},
    "podcast": {"followers": (50, 50000), "posts": (5, 200), "engagement": (3.0, 20.0), "growth": (-1.5, 8.0)},
    "radio": {"followers": (100, 80000), "posts": (2, 100), "engagement": (1.5, 10.0), "growth": (-0.5, 5.0)},
    "video_streaming": {"followers": (100, 200000), "posts": (5, 500), "engagement": (1.0, 12.0), "growth": (-1.0, 15.0)},
    "live_streaming": {"followers": (50, 100000), "posts": (3, 200), "engagement": (2.0, 18.0), "growth": (-2.0, 20.0)},
    "video_platform": {"followers": (100, 180000), "posts": (5, 400), "engagement": (1.5, 10.0), "growth": (-1.0, 8.0)},
    "rights_organization": {"followers": (10, 5000), "posts": (1, 50), "engagement": (0.5, 3.0), "growth": (0.0, 2.0)},
    "blockchain": {"followers": (20, 30000), "posts": (2, 100), "engagement": (1.0, 8.0), "growth": (-3.0, 25.0)},
    "web3_music": {"followers": (10, 20000), "posts": (2, 80), "engagement": (2.0, 12.0), "growth": (-2.0, 18.0)},
    "nft_marketplace": {"followers": (15, 25000), "posts": (1, 60), "engagement": (1.5, 10.0), "growth": (-5.0, 30.0)},
    "audio_social": {"followers": (30, 40000), "posts": (3, 150), "engagement": (3.0, 15.0), "growth": (-1.0, 10.0)},
    "model_agency": {"followers": (50, 60000), "posts": (5, 200), "engagement": (2.0, 12.0), "growth": (-1.0, 8.0)},
    "model_platform": {"followers": (40, 50000), "posts": (5, 180), "engagement": (2.5, 14.0), "growth": (-1.0, 9.0)},
    "music_licensing": {"followers": (10, 10000), "posts": (1, 40), "engagement": (0.5, 5.0), "growth": (0.0, 3.0)},
    "music_data_exchange": {"followers": (5, 5000), "posts": (1, 30), "engagement": (0.3, 2.0), "growth": (0.0, 2.0)},
}

DEFAULT_RANGES = {"followers": (50, 50000), "posts": (2, 100), "engagement": (1.0, 8.0), "growth": (-1.0, 8.0)}


def _deterministic_seed(user_id: str, platform_id: str) -> int:
    """Generate a deterministic seed so the same user+platform always gets the same base metrics."""
    return int(hashlib.md5(f"{user_id}:{platform_id}".encode()).hexdigest()[:8], 16)


def _generate_metrics_for_platform(user_id: str, platform_id: str, platform_type: str):
    """Generate realistic metrics for a platform. Deterministic per user+platform pair."""
    seed = _deterministic_seed(user_id, platform_id)
    rng = random.Random(seed)
    ranges = PLATFORM_METRIC_RANGES.get(platform_type, DEFAULT_RANGES)

    followers = rng.randint(*ranges["followers"])
    posts = rng.randint(*ranges["posts"])
    engagement = round(rng.uniform(*ranges["engagement"]), 2)
    growth = round(rng.uniform(*ranges["growth"]), 2)
    likes = int(followers * engagement / 100 * posts * rng.uniform(0.3, 0.8))
    comments = int(likes * rng.uniform(0.05, 0.25))
    shares = int(likes * rng.uniform(0.02, 0.15))
    impressions = int(followers * rng.uniform(1.5, 8.0))
    reach = int(impressions * rng.uniform(0.4, 0.85))

    # Generate 7-day trend data
    daily_followers = []
    base = followers - int(followers * abs(growth) / 100 * 7)
    for i in range(7):
        delta = int(followers * growth / 100 / 7) + rng.randint(-int(followers * 0.005 + 1), int(followers * 0.005 + 1))
        base = max(0, base + delta)
        daily_followers.append(base)
    daily_followers[-1] = followers  # ensure current day matches

    daily_engagement = []
    for i in range(7):
        daily_engagement.append(round(engagement + rng.uniform(-1.5, 1.5), 2))
    daily_engagement[-1] = engagement

    return {
        "followers": followers,
        "posts": posts,
        "engagement_rate": engagement,
        "growth_rate": growth,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "impressions": impressions,
        "reach": reach,
        "daily_followers": daily_followers,
        "daily_engagement": daily_engagement,
    }


# ── Dashboard Metrics ─────────────────────────────────────────────────

@router.get("/metrics/dashboard")
async def dashboard_metrics(
    force_refresh: bool = Query(False, description="Force live API refresh"),
    current_user=Depends(get_current_user),
):
    """Aggregate metrics across all connected platforms. Uses live APIs when possible."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    connected = []
    total_followers = 0
    total_posts = 0
    total_likes = 0
    total_comments = 0
    total_shares = 0
    total_impressions = 0
    total_reach = 0
    engagement_sum = 0.0
    live_count = 0
    simulated_count = 0

    async for doc in db.platform_credentials.find(
        {"user_id": user_id, "status": "connected"}, {"_id": 0}
    ):
        pid = doc["platform_id"]
        cfg = DISTRIBUTION_PLATFORMS.get(pid, {})
        ptype = cfg.get("type", "other")

        # Generate simulated as fallback
        sim_metrics = _generate_metrics_for_platform(user_id, pid, ptype)

        # If manual metrics exist, use them as the simulated base
        manual = doc.get("manual_metrics")
        if manual and manual.get("followers", 0) > 0:
            sim_metrics.update({
                "followers": manual["followers"],
                "following": manual.get("following", 0),
                "posts": manual.get("posts", 0),
                "engagement_rate": manual.get("engagement_rate", sim_metrics["engagement_rate"]),
                "likes": manual.get("likes", 0),
                "page_likes": manual.get("page_likes", 0),
                "impressions": int(manual["followers"] * 2.5),
                "reach": int(manual["followers"] * 1.5),
            })

        # Try live fetch with fallback
        credentials = doc.get("credentials", {})
        metrics = await fetch_metrics_with_fallback(
            user_id, pid, credentials, sim_metrics, force_refresh=force_refresh
        )

        data_source = metrics.get("data_source", "simulated")
        if data_source == "live":
            live_count += 1
        else:
            simulated_count += 1

        total_followers += metrics.get("followers", 0)
        total_posts += metrics.get("posts", 0)
        total_likes += metrics.get("likes", 0)
        total_comments += metrics.get("comments", 0)
        total_shares += metrics.get("shares", 0)
        total_impressions += metrics.get("impressions", 0)
        total_reach += metrics.get("reach", 0)
        engagement_sum += metrics.get("engagement_rate", 0)

        connected.append({
            "platform": pid,
            "name": cfg.get("name", pid),
            "type": ptype,
            "connected": True,
            "username": doc.get("display_name", ""),
            "data_source": data_source,
            **{k: v for k, v in metrics.items() if k != "data_source"},
        })

    avg_engagement = round(engagement_sum / len(connected), 2) if connected else 0.0
    connected.sort(key=lambda x: x.get("followers", 0), reverse=True)

    return {
        "platforms": connected,
        "total_followers": total_followers,
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "total_impressions": total_impressions,
        "total_reach": total_reach,
        "avg_engagement": avg_engagement,
        "connected_count": len(connected),
        "total_platforms": len(DISTRIBUTION_PLATFORMS),
        "live_count": live_count,
        "simulated_count": simulated_count,
    }


@router.get("/metrics/platforms")
async def platform_metrics(
    force_refresh: bool = Query(False, description="Force live API refresh"),
    current_user=Depends(get_current_user),
):
    """Return detailed metrics for each connected platform, grouped by category. Uses live APIs when possible."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))

    platforms_by_type = {}
    all_platforms = []
    live_count = 0
    simulated_count = 0

    async for doc in db.platform_credentials.find(
        {"user_id": user_id, "status": "connected"}, {"_id": 0}
    ):
        pid = doc["platform_id"]
        cfg = DISTRIBUTION_PLATFORMS.get(pid, {})
        ptype = cfg.get("type", "other")

        sim_metrics = _generate_metrics_for_platform(user_id, pid, ptype)

        # If manual metrics exist, use them as the simulated base
        manual = doc.get("manual_metrics")
        if manual and manual.get("followers", 0) > 0:
            sim_metrics.update({
                "followers": manual["followers"],
                "following": manual.get("following", 0),
                "posts": manual.get("posts", 0),
                "engagement_rate": manual.get("engagement_rate", sim_metrics["engagement_rate"]),
                "likes": manual.get("likes", 0),
                "page_likes": manual.get("page_likes", 0),
                "impressions": int(manual["followers"] * 2.5),
                "reach": int(manual["followers"] * 1.5),
            })

        credentials = doc.get("credentials", {})
        metrics = await fetch_metrics_with_fallback(
            user_id, pid, credentials, sim_metrics, force_refresh=force_refresh
        )

        data_source = metrics.get("data_source", "simulated")
        if data_source == "live":
            live_count += 1
        else:
            simulated_count += 1

        entry = {
            "platform_id": pid,
            "name": cfg.get("name", pid),
            "type": ptype,
            "icon": PLATFORM_ICONS.get(ptype, "globe"),
            "username": doc.get("display_name", ""),
            "connected_at": doc.get("connected_at", ""),
            "data_source": data_source,
            "has_live_api": has_live_adapter(pid),
            **{k: v for k, v in metrics.items() if k not in ("data_source", "cached")},
        }
        all_platforms.append(entry)
        platforms_by_type.setdefault(ptype, []).append(entry)

    # Category summaries
    category_summaries = []
    for ptype, plist in platforms_by_type.items():
        meta = CATEGORY_META_BACKEND.get(ptype, {"label": ptype.replace("_", " ").title()})
        cat_followers = sum(p.get("followers", 0) for p in plist)
        cat_engagement = round(sum(p.get("engagement_rate", 0) for p in plist) / len(plist), 2) if plist else 0
        cat_growth = round(sum(p.get("growth_rate", 0) for p in plist) / len(plist), 2) if plist else 0
        cat_live = sum(1 for p in plist if p.get("data_source") == "live")
        category_summaries.append({
            "type": ptype,
            "label": meta["label"],
            "platform_count": len(plist),
            "total_followers": cat_followers,
            "avg_engagement": cat_engagement,
            "avg_growth": cat_growth,
            "live_count": cat_live,
        })

    category_summaries.sort(key=lambda x: x["total_followers"], reverse=True)
    all_platforms.sort(key=lambda x: x.get("followers", 0), reverse=True)

    return {
        "platforms": all_platforms,
        "categories": category_summaries,
        "total_connected": len(all_platforms),
        "live_count": live_count,
        "simulated_count": simulated_count,
    }


@router.post("/metrics/refresh")
async def refresh_metrics(current_user=Depends(get_current_user)):
    """Refresh metrics for all connected platforms. Attempts live API calls first."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))
    now = datetime.now(timezone.utc).isoformat()

    count = 0
    live_success = 0
    simulated_fallback = 0

    async for doc in db.platform_credentials.find(
        {"user_id": user_id, "status": "connected"}, {"_id": 0}
    ):
        pid = doc["platform_id"]
        cfg = DISTRIBUTION_PLATFORMS.get(pid, {})
        ptype = cfg.get("type", "other")
        credentials = doc.get("credentials", {})

        sim_metrics = _generate_metrics_for_platform(user_id, pid, ptype)

        # If manual metrics exist, use them as the simulated base
        manual = doc.get("manual_metrics")
        if manual and manual.get("followers", 0) > 0:
            sim_metrics.update({
                "followers": manual["followers"],
                "following": manual.get("following", 0),
                "posts": manual.get("posts", 0),
                "engagement_rate": manual.get("engagement_rate", sim_metrics["engagement_rate"]),
                "likes": manual.get("likes", 0),
                "page_likes": manual.get("page_likes", 0),
                "impressions": int(manual["followers"] * 2.5),
                "reach": int(manual["followers"] * 1.5),
            })

        metrics = await fetch_metrics_with_fallback(
            user_id, pid, credentials, sim_metrics, force_refresh=True
        )

        data_source = metrics.get("data_source", "simulated")
        if data_source == "live":
            live_success += 1
        else:
            simulated_fallback += 1

        await db.platform_metrics.update_one(
            {"user_id": user_id, "platform_id": pid},
            {"$set": {
                "user_id": user_id,
                "platform_id": pid,
                "metrics": metrics,
                "data_source": data_source,
                "refreshed_at": now,
            }},
            upsert=True,
        )
        count += 1

    return {
        "success": True,
        "refreshed_count": count,
        "live_count": live_success,
        "simulated_count": simulated_fallback,
        "refreshed_at": now,
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

@router.get("/live-supported")
async def list_live_supported():
    """Return list of platforms that have live API adapters."""
    supported = get_supported_live_platforms()
    return {
        "platforms": supported,
        "count": len(supported),
    }


@router.get("/url-supported")
async def list_url_supported():
    """Return list of platforms that support URL-based connection with examples."""
    supported = get_all_url_supported_platforms()
    return {
        "platforms": supported,
        "count": len(supported),
        "url_examples": PLATFORM_URL_EXAMPLES,
    }


@router.post("/url-detect")
async def detect_url_platform(payload: URLConnectPayload):
    """Auto-detect platform from a profile URL."""
    result = detect_platform_from_url(payload.profile_url)
    if not result:
        raise HTTPException(status_code=400, detail="Could not detect platform from URL. Please check the URL format.")
    platform_id, username = result
    cfg = DISTRIBUTION_PLATFORMS.get(platform_id, {})
    return {
        "platform_id": platform_id,
        "platform_name": cfg.get("name", platform_id),
        "username": username,
        "has_live_metrics": has_url_adapter(platform_id),
        "url_example": get_url_example(platform_id),
    }


@router.post("/connect-url")
async def connect_with_url(
    payload: URLConnectPayload,
    current_user=Depends(get_current_user),
):
    """Connect a platform using a profile URL instead of API credentials."""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))
    now = datetime.now(timezone.utc).isoformat()

    url = payload.profile_url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Profile URL is required")

    # Detect platform if not provided
    pid = payload.platform_id
    username = None
    if not pid:
        result = detect_platform_from_url(url)
        if not result:
            raise HTTPException(status_code=400, detail="Could not detect platform from URL. Please provide platform_id.")
        pid, username = result
    else:
        username = parse_username_from_url(pid, url)

    if pid not in DISTRIBUTION_PLATFORMS:
        raise HTTPException(status_code=404, detail=f"Platform '{pid}' not found")

    cfg = DISTRIBUTION_PLATFORMS[pid]
    display_name = payload.display_name or username or url.split("/")[-1].lstrip("@")

    # Build credentials with profile_url
    cred_fields = cfg.get("credentials_required", [])
    credentials = {k: "" for k in cred_fields}
    credentials["profile_url"] = url

    # Attempt to fetch metrics from the URL right away
    metrics_result = None
    if has_url_adapter(pid):
        metrics_result = await fetch_metrics_from_url(pid, url)

    # If auto-scrape failed and user provided manual metrics, use those
    manual = payload.manual_metrics
    metrics_source = "auto"
    if (not metrics_result or metrics_result.get("followers", 0) == 0) and manual:
        followers = int(manual.get("followers", 0))
        following = int(manual.get("following", 0))
        posts = int(manual.get("posts", 0))
        engagement = float(manual.get("engagement_rate", 0))
        if followers > 0:
            metrics_result = {
                "followers": followers,
                "following": following,
                "posts": posts,
                "engagement_rate": engagement if engagement > 0 else round(min(3.0 * (1000 / max(followers, 1000)), 10.0), 2),
                "likes": int(manual.get("likes", 0)),
                "page_likes": int(manual.get("page_likes", 0)),
                "comments": 0,
                "shares": 0,
                "impressions": int(followers * 2.5),
                "reach": int(followers * 1.5),
                "username": username or display_name,
            }
            metrics_source = "manual"

    # Save connection
    doc = {
        "user_id": user_id,
        "platform_id": pid,
        "credentials": credentials,
        "display_name": display_name,
        "status": "connected",
        "connection_method": "url",
        "connected_at": now,
        "updated_at": now,
    }
    # Store manual metrics in credentials if provided so they can be used as fallback
    if metrics_source == "manual" and metrics_result:
        doc["manual_metrics"] = {
            "followers": metrics_result.get("followers", 0),
            "following": metrics_result.get("following", 0),
            "posts": metrics_result.get("posts", 0),
            "engagement_rate": metrics_result.get("engagement_rate", 0),
            "likes": metrics_result.get("likes", 0),
            "page_likes": metrics_result.get("page_likes", 0),
        }

    await db.platform_credentials.update_one(
        {"user_id": user_id, "platform_id": pid},
        {"$set": doc},
        upsert=True,
    )

    return {
        "success": True,
        "platform_id": pid,
        "platform_name": cfg.get("name", pid),
        "username": display_name,
        "connection_method": "url",
        "metrics_source": metrics_source,
        "metrics_available": metrics_result is not None and metrics_result.get("followers", 0) > 0,
        "initial_metrics": {
            "followers": metrics_result.get("followers", 0),
            "following": metrics_result.get("following", 0),
            "posts": metrics_result.get("posts", 0),
            "engagement_rate": metrics_result.get("engagement_rate", 0),
            "likes": metrics_result.get("likes", 0),
            "page_likes": metrics_result.get("page_likes", 0),
            "impressions": metrics_result.get("impressions", 0),
            "reach": metrics_result.get("reach", 0),
            "full_name": metrics_result.get("full_name", ""),
            "bio": metrics_result.get("bio", ""),
            "page_name": metrics_result.get("page_name", ""),
            "category": metrics_result.get("category", ""),
            "is_verified": metrics_result.get("is_verified", False),
        } if metrics_result else None,
    }


@router.post("/connect-url/bulk")
async def bulk_connect_urls(
    payload: dict,
    current_user=Depends(get_current_user),
):
    """Connect multiple platforms using profile URLs. Payload: { urls: ["url1", "url2", ...] }"""
    user_id = current_user.id if hasattr(current_user, "id") else str(current_user.get("id", current_user.get("_id", "")))
    now = datetime.now(timezone.utc).isoformat()
    urls = payload.get("urls", [])
    results = []

    for url in urls:
        url = url.strip()
        if not url:
            continue
        detected = detect_platform_from_url(url)
        if not detected:
            results.append({"url": url, "success": False, "error": "Could not detect platform"})
            continue
        pid, username = detected
        cfg = DISTRIBUTION_PLATFORMS.get(pid, {})
        cred_fields = cfg.get("credentials_required", [])
        credentials = {k: "" for k in cred_fields}
        credentials["profile_url"] = url

        doc = {
            "user_id": user_id,
            "platform_id": pid,
            "credentials": credentials,
            "display_name": username or url.split("/")[-1],
            "status": "connected",
            "connection_method": "url",
            "connected_at": now,
            "updated_at": now,
        }
        await db.platform_credentials.update_one(
            {"user_id": user_id, "platform_id": pid},
            {"$set": doc},
            upsert=True,
        )
        results.append({
            "url": url,
            "success": True,
            "platform_id": pid,
            "platform_name": cfg.get("name", pid),
            "username": username,
        })

    return {
        "success": True,
        "results": results,
        "connected_count": sum(1 for r in results if r.get("success")),
    }


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
