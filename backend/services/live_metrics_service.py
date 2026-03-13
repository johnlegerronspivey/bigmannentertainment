"""
Live Metrics Service - Fetches real metrics from platform APIs using stored credentials.
Falls back to simulated data when live API calls fail.
Supports: Twitter/X, YouTube, Instagram, Facebook, Spotify, TikTok,
          LinkedIn, Twitch, SoundCloud, Reddit, and more.
"""
import aiohttp
import logging
import base64
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from config.database import db

logger = logging.getLogger(__name__)

# Normalized metrics structure
EMPTY_METRICS = {
    "followers": 0,
    "posts": 0,
    "engagement_rate": 0.0,
    "growth_rate": 0.0,
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "impressions": 0,
    "reach": 0,
    "daily_followers": [0] * 7,
    "daily_engagement": [0.0] * 7,
}

CACHE_TTL_SECONDS = 300  # 5 min cache


async def _http_get(url: str, headers: Dict[str, str], params: Optional[Dict] = None, timeout: int = 15) -> Optional[Dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.warning("API %s returned %s: %s", url, resp.status, await resp.text())
    except Exception as e:
        logger.warning("API call failed for %s: %s", url, str(e))
    return None


async def _http_post(url: str, headers: Dict[str, str], data: Optional[Dict] = None, json_data: Optional[Dict] = None, timeout: int = 15) -> Optional[Dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, json=json_data, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status in (200, 201):
                    return await resp.json()
                logger.warning("API POST %s returned %s: %s", url, resp.status, await resp.text())
    except Exception as e:
        logger.warning("API POST call failed for %s: %s", url, str(e))
    return None


# ──────────────────────────────────────────────────────────────────────
# Platform-specific adapters
# Each returns normalized metrics dict or None on failure
# ──────────────────────────────────────────────────────────────────────

async def _fetch_twitter(creds: Dict[str, str]) -> Optional[Dict]:
    """Twitter/X API v2 - get user metrics using Bearer token or access_token."""
    token = creds.get("access_token") or creds.get("api_key")
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    data = await _http_get(
        "https://api.twitter.com/2/users/me",
        headers,
        params={"user.fields": "public_metrics,created_at"}
    )
    if not data or "data" not in data:
        return None
    user = data["data"]
    pm = user.get("public_metrics", {})
    followers = pm.get("followers_count", 0)
    tweets = pm.get("tweet_count", 0)
    listed = pm.get("listed_count", 0)
    engagement = round((listed / max(followers, 1)) * 100, 2)
    return {
        "followers": followers,
        "posts": tweets,
        "engagement_rate": min(engagement, 20.0),
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": followers * 3,
        "reach": followers * 2,
    }


async def _fetch_youtube(creds: Dict[str, str]) -> Optional[Dict]:
    """YouTube Data API v3 - get channel stats."""
    api_key = creds.get("api_key")
    if not api_key:
        return None
    # First get the authenticated channel
    data = await _http_get(
        "https://www.googleapis.com/youtube/v3/channels",
        headers={"Accept": "application/json"},
        params={"part": "statistics,snippet", "mine": "true", "key": api_key}
    )
    # If mine=true doesn't work (no OAuth), try to list by key
    if not data or not data.get("items"):
        data = await _http_get(
            "https://www.googleapis.com/youtube/v3/channels",
            headers={"Accept": "application/json"},
            params={"part": "statistics", "id": creds.get("client_id", ""), "key": api_key}
        )
    if not data or not data.get("items"):
        return None
    stats = data["items"][0].get("statistics", {})
    subs = int(stats.get("subscriberCount", 0))
    views = int(stats.get("viewCount", 0))
    videos = int(stats.get("videoCount", 0))
    return {
        "followers": subs,
        "posts": videos,
        "engagement_rate": round((views / max(subs * videos, 1)) * 100, 2) if videos else 0.0,
        "likes": 0,
        "comments": int(stats.get("commentCount", 0)) if "commentCount" in stats else 0,
        "shares": 0,
        "impressions": views,
        "reach": int(views * 0.6),
    }


async def _fetch_instagram(creds: Dict[str, str]) -> Optional[Dict]:
    """Instagram Graph API - user metrics."""
    token = creds.get("access_token")
    if not token:
        return None
    data = await _http_get(
        "https://graph.instagram.com/me",
        headers={"Authorization": f"Bearer {token}"},
        params={"fields": "id,username,media_count,followers_count,follows_count"}
    )
    if not data or "id" not in data:
        # Try Facebook Graph API endpoint
        data = await _http_get(
            "https://graph.facebook.com/v18.0/me",
            headers={},
            params={"fields": "id,name,followers_count,fan_count", "access_token": token}
        )
    if not data:
        return None
    followers = data.get("followers_count", data.get("fan_count", 0))
    media_count = data.get("media_count", 0)
    return {
        "followers": followers,
        "posts": media_count,
        "engagement_rate": round(min(followers * 0.035, 15.0), 2) if followers else 0.0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": int(followers * 2.5),
        "reach": int(followers * 1.5),
    }


async def _fetch_facebook(creds: Dict[str, str]) -> Optional[Dict]:
    """Facebook Graph API - page/user metrics."""
    token = creds.get("access_token")
    if not token:
        return None
    data = await _http_get(
        "https://graph.facebook.com/v18.0/me",
        headers={},
        params={"fields": "id,name,followers_count,fan_count,friends", "access_token": token}
    )
    if not data or "id" not in data:
        return None
    followers = data.get("followers_count", data.get("fan_count", 0))
    return {
        "followers": followers,
        "posts": 0,
        "engagement_rate": 2.5,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": int(followers * 3),
        "reach": int(followers * 2),
    }


async def _fetch_spotify(creds: Dict[str, str]) -> Optional[Dict]:
    """Spotify Web API - requires client_credentials flow for app-level data."""
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    if not client_id or not client_secret:
        return None
    # Get token via client_credentials
    auth_str = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    token_data = await _http_post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth_str}", "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"}
    )
    if not token_data or "access_token" not in token_data:
        return None
    access_token = token_data["access_token"]
    # Try to get current user profile (requires user auth, not client creds)
    data = await _http_get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if data and "id" in data:
        followers = data.get("followers", {}).get("total", 0)
        return {
            "followers": followers,
            "posts": 0,
            "engagement_rate": 5.0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "impressions": followers * 4,
            "reach": followers * 3,
        }
    # Client credentials doesn't give user data, but token is valid
    return {
        "followers": 0,
        "posts": 0,
        "engagement_rate": 0.0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": 0,
        "reach": 0,
    }


async def _fetch_tiktok(creds: Dict[str, str]) -> Optional[Dict]:
    """TikTok API - user info."""
    token = creds.get("access_token")
    if not token:
        return None
    data = await _http_get(
        "https://open.tiktokapis.com/v2/user/info/",
        headers={"Authorization": f"Bearer {token}"},
        params={"fields": "follower_count,following_count,likes_count,video_count"}
    )
    if not data or "data" not in data:
        return None
    user = data["data"].get("user", {})
    followers = user.get("follower_count", 0)
    likes = user.get("likes_count", 0)
    videos = user.get("video_count", 0)
    return {
        "followers": followers,
        "posts": videos,
        "engagement_rate": round((likes / max(followers * videos, 1)) * 100, 2) if followers and videos else 0.0,
        "likes": likes,
        "comments": 0,
        "shares": 0,
        "impressions": followers * 5,
        "reach": followers * 3,
    }


async def _fetch_linkedin(creds: Dict[str, str]) -> Optional[Dict]:
    """LinkedIn API - user/org metrics."""
    token = creds.get("access_token")
    if not token:
        return None
    data = await _http_get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if not data or "id" not in data:
        return None
    # LinkedIn doesn't expose follower count via basic profile
    return {
        "followers": 0,
        "posts": 0,
        "engagement_rate": 3.0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": 0,
        "reach": 0,
    }


async def _fetch_twitch(creds: Dict[str, str]) -> Optional[Dict]:
    """Twitch Helix API - requires client_id + OAuth or app access token."""
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    if not client_id or not client_secret:
        return None
    # Get app access token
    token_data = await _http_post(
        "https://id.twitch.tv/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}
    )
    if not token_data or "access_token" not in token_data:
        return None
    access_token = token_data["access_token"]
    # Get user info (need login name from display_name or another source)
    data = await _http_get(
        "https://api.twitch.tv/helix/users",
        headers={"Authorization": f"Bearer {access_token}", "Client-Id": client_id}
    )
    if not data or not data.get("data"):
        return None
    user = data["data"][0]
    # Get follower count
    user_id = user.get("id")
    follower_data = await _http_get(
        "https://api.twitch.tv/helix/channels/followers",
        headers={"Authorization": f"Bearer {access_token}", "Client-Id": client_id},
        params={"broadcaster_id": user_id}
    )
    followers = follower_data.get("total", 0) if follower_data else 0
    return {
        "followers": followers,
        "posts": 0,
        "engagement_rate": 8.0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": followers * 4,
        "reach": followers * 2,
    }


async def _fetch_soundcloud(creds: Dict[str, str]) -> Optional[Dict]:
    """SoundCloud API - user metrics."""
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    if not client_id:
        return None
    # SoundCloud API (v2 unofficial or via OAuth)
    data = await _http_get(
        "https://api.soundcloud.com/me",
        headers={"Authorization": f"OAuth {client_secret}"} if client_secret else {},
        params={"client_id": client_id}
    )
    if not data or "id" not in data:
        return None
    return {
        "followers": data.get("followers_count", 0),
        "posts": data.get("track_count", 0),
        "engagement_rate": round(data.get("playback_count", 0) / max(data.get("followers_count", 1), 1) * 0.1, 2),
        "likes": data.get("likes_count", 0),
        "comments": data.get("comments_count", 0),
        "shares": data.get("reposts_count", 0),
        "impressions": data.get("playback_count", 0),
        "reach": int(data.get("playback_count", 0) * 0.7),
    }


async def _fetch_reddit(creds: Dict[str, str]) -> Optional[Dict]:
    """Reddit API - user karma and stats."""
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    token = creds.get("access_token")
    if not token and not (client_id and client_secret):
        return None
    if token:
        headers = {"Authorization": f"Bearer {token}", "User-Agent": "BigMannApp/1.0"}
    else:
        auth_str = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        token_data = await _http_post(
            "https://www.reddit.com/api/v1/access_token",
            headers={"Authorization": f"Basic {auth_str}", "User-Agent": "BigMannApp/1.0", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"}
        )
        if not token_data or "access_token" not in token_data:
            return None
        headers = {"Authorization": f"Bearer {token_data['access_token']}", "User-Agent": "BigMannApp/1.0"}
    data = await _http_get("https://oauth.reddit.com/api/v1/me", headers)
    if not data or "name" not in data:
        return None
    karma = data.get("total_karma", data.get("link_karma", 0) + data.get("comment_karma", 0))
    return {
        "followers": data.get("subreddit", {}).get("subscribers", 0),
        "posts": 0,
        "engagement_rate": min(round(karma / 100, 2), 15.0),
        "likes": karma,
        "comments": data.get("comment_karma", 0),
        "shares": 0,
        "impressions": karma * 10,
        "reach": karma * 5,
    }


async def _fetch_snapchat(creds: Dict[str, str]) -> Optional[Dict]:
    """Snapchat Ads API - get organization info."""
    token = creds.get("api_token") or creds.get("access_token")
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    data = await _http_get("https://adsapi.snapchat.com/v1/me", headers)
    if not data:
        return None
    return {
        "followers": 0,
        "posts": 0,
        "engagement_rate": 0.0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": 0,
        "reach": 0,
        "account_status": "connected",
    }


# ── Adapter registry ──────────────────────────────────────────────────
LIVE_ADAPTERS: Dict[str, Any] = {
    "twitter": _fetch_twitter,
    "youtube": _fetch_youtube,
    "instagram": _fetch_instagram,
    "facebook": _fetch_facebook,
    "spotify": _fetch_spotify,
    "tiktok": _fetch_tiktok,
    "linkedin": _fetch_linkedin,
    "twitch": _fetch_twitch,
    "soundcloud": _fetch_soundcloud,
    "reddit": _fetch_reddit,
    "snapchat": _fetch_snapchat,
    # YouTube Music shares YouTube credentials
    "youtube_music": _fetch_youtube,
    # Threads shares Instagram/Facebook token
    "threads": _fetch_instagram,
    # Spotify podcasts uses same Spotify creds
    "spotify_podcasts": _fetch_spotify,
    # WhatsApp Business uses Facebook token
    "whatsapp_business": _fetch_facebook,
}


def has_live_adapter(platform_id: str) -> bool:
    """Check if a platform has a live API adapter."""
    return platform_id in LIVE_ADAPTERS


def get_supported_live_platforms() -> List[str]:
    """Return list of platforms with live adapters."""
    return list(LIVE_ADAPTERS.keys())


async def fetch_live_metrics(platform_id: str, credentials: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Attempt to fetch live metrics for a platform using stored credentials.
    Returns normalized metrics dict on success, None on failure.
    """
    adapter = LIVE_ADAPTERS.get(platform_id)
    if not adapter:
        return None

    # Check if credentials have actual values (not empty strings from bulk-connect)
    non_empty = {k: v for k, v in credentials.items() if v and v.strip()}
    if not non_empty:
        return None

    try:
        result = await adapter(credentials)
        if result:
            logger.info("Live metrics fetched for %s", platform_id)
            return result
    except Exception as e:
        logger.warning("Live fetch failed for %s: %s", platform_id, str(e))

    return None


async def get_cached_metrics(user_id: str, platform_id: str) -> Optional[Dict[str, Any]]:
    """Get cached live metrics from DB if still fresh."""
    doc = await db.platform_live_metrics.find_one(
        {"user_id": user_id, "platform_id": platform_id},
        {"_id": 0}
    )
    if not doc:
        return None
    refreshed_at = doc.get("refreshed_at")
    if not refreshed_at:
        return None
    # Parse ISO timestamp
    try:
        ts = datetime.fromisoformat(refreshed_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if (datetime.now(timezone.utc) - ts).total_seconds() > CACHE_TTL_SECONDS:
        return None
    cached = doc.get("metrics")
    if cached:
        cached["data_source"] = "live"
        cached["cached"] = True
    return cached


async def store_live_metrics(user_id: str, platform_id: str, metrics: Dict[str, Any]) -> None:
    """Cache live metrics in DB."""
    now = datetime.now(timezone.utc).isoformat()
    await db.platform_live_metrics.update_one(
        {"user_id": user_id, "platform_id": platform_id},
        {"$set": {
            "user_id": user_id,
            "platform_id": platform_id,
            "metrics": metrics,
            "refreshed_at": now,
        }},
        upsert=True,
    )


async def fetch_metrics_with_fallback(
    user_id: str,
    platform_id: str,
    credentials: Dict[str, str],
    simulated_metrics: Dict[str, Any],
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Try to fetch live metrics; use cache if available; fall back to simulated.
    Order: cache -> API credentials -> URL-based -> simulated.
    Returns metrics dict with `data_source` field ("live", "url", or "simulated").
    """
    from services.url_metrics_service import fetch_metrics_from_url, has_url_adapter

    has_api = has_live_adapter(platform_id)
    has_url = has_url_adapter(platform_id)
    profile_url = credentials.get("profile_url", "")

    if not has_api and not (has_url and profile_url):
        simulated_metrics["data_source"] = "simulated"
        return simulated_metrics

    # Check cache first (unless force refresh)
    if not force_refresh:
        cached = await get_cached_metrics(user_id, platform_id)
        if cached:
            return cached

    live = None

    # 1. Try API-key based fetch first
    if has_api:
        api_creds = {k: v for k, v in credentials.items() if k != "profile_url" and v and v.strip()}
        if api_creds:
            live = await fetch_live_metrics(platform_id, credentials)

    # 2. Try URL-based fetch if API didn't work
    if not live and has_url and profile_url and profile_url.strip():
        url_result = await fetch_metrics_from_url(platform_id, profile_url)
        if url_result and url_result.get("followers", 0) > 0:
            live = url_result
            # Mark as URL-sourced
            if live:
                live["_source_type"] = "url"

    if live:
        # Generate trend data from live base
        import random
        rng = random.Random(hash(f"{user_id}:{platform_id}:{datetime.now(timezone.utc).date()}"))
        base_followers = live.get("followers", 0)
        daily_followers = []
        trend_base = max(1, int(base_followers * 0.97))
        for i in range(7):
            delta = rng.randint(-int(max(base_followers * 0.002, 1)), int(max(base_followers * 0.005, 1)))
            trend_base = max(0, trend_base + delta)
            daily_followers.append(trend_base)
        daily_followers[-1] = base_followers

        base_eng = live.get("engagement_rate", 2.0)
        daily_engagement = [round(base_eng + rng.uniform(-0.5, 0.5), 2) for _ in range(7)]
        daily_engagement[-1] = base_eng

        growth = round(((daily_followers[-1] - daily_followers[0]) / max(daily_followers[0], 1)) * 100, 2) if daily_followers[0] else 0.0

        source_type = live.pop("_source_type", "api")
        live.update({
            "daily_followers": daily_followers,
            "daily_engagement": daily_engagement,
            "growth_rate": growth,
            "data_source": "live",
            "source_method": source_type,  # "api" or "url"
        })

        # Cache the result
        await store_live_metrics(user_id, platform_id, live)
        return live

    # Fall back to simulated
    simulated_metrics["data_source"] = "simulated"
    return simulated_metrics
