"""
URL-based Metrics Service - Fetches public metrics from social platforms using profile URLs.
Users paste their profile URL instead of API keys.
Parses username, fetches public data from available endpoints.
"""
import re
import json
import aiohttp
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

JSON_HEADERS = {
    "User-Agent": "BigMannApp/1.0",
    "Accept": "application/json",
}


async def _fetch_text(url: str, headers: Optional[Dict] = None, timeout: int = 15) -> Optional[str]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers or BROWSER_HEADERS, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True) as resp:
                if resp.status == 200:
                    return await resp.text()
                logger.warning("URL fetch %s returned %s", url, resp.status)
    except Exception as e:
        logger.warning("URL fetch failed %s: %s", url, str(e))
    return None


async def _fetch_json(url: str, headers: Optional[Dict] = None, timeout: int = 15) -> Optional[Dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers or JSON_HEADERS, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.warning("JSON fetch %s returned %s", url, resp.status)
    except Exception as e:
        logger.warning("JSON fetch failed %s: %s", url, str(e))
    return None


def _extract_number(text: str) -> int:
    """Extract a number from text like '1.2M', '45.3K', '1,234'."""
    if not text:
        return 0
    text = text.strip().replace(",", "").replace(" ", "")
    multipliers = {"k": 1000, "m": 1000000, "b": 1000000000}
    for suffix, mult in multipliers.items():
        if text.lower().endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def _search_meta(html: str, property_name: str) -> Optional[str]:
    """Extract content from meta tag."""
    patterns = [
        rf'<meta[^>]+(?:property|name)=["\'](?:og:)?{re.escape(property_name)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:)?{re.escape(property_name)}["\']',
    ]
    for pattern in patterns:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


# ──────────────────────────────────────────────────────────────────────
# URL Parsers - Extract username/ID from profile URLs
# ──────────────────────────────────────────────────────────────────────

URL_PATTERNS: Dict[str, list] = {
    "twitter": [
        r"(?:twitter\.com|x\.com)/(?:@)?([A-Za-z0-9_]{1,15})/?",
    ],
    "youtube": [
        r"youtube\.com/@([A-Za-z0-9_\-\.]+)",
        r"youtube\.com/channel/(UC[A-Za-z0-9_\-]+)",
        r"youtube\.com/c/([A-Za-z0-9_\-]+)",
        r"youtube\.com/user/([A-Za-z0-9_\-]+)",
    ],
    "instagram": [
        r"instagram\.com/(?:@)?([A-Za-z0-9_\.]+)/?",
    ],
    "tiktok": [
        r"tiktok\.com/@([A-Za-z0-9_\.]+)",
    ],
    "facebook": [
        r"facebook\.com/(?:profile\.php\?id=)?([A-Za-z0-9\.\-]+)",
    ],
    "linkedin": [
        r"linkedin\.com/in/([A-Za-z0-9\-]+)",
        r"linkedin\.com/company/([A-Za-z0-9\-]+)",
    ],
    "twitch": [
        r"twitch\.tv/([A-Za-z0-9_]+)",
    ],
    "reddit": [
        r"reddit\.com/(?:user|u)/([A-Za-z0-9_\-]+)",
    ],
    "soundcloud": [
        r"soundcloud\.com/([A-Za-z0-9_\-]+)",
    ],
    "spotify": [
        r"open\.spotify\.com/artist/([A-Za-z0-9]+)",
        r"open\.spotify\.com/user/([A-Za-z0-9]+)",
    ],
    "pinterest": [
        r"pinterest\.com/([A-Za-z0-9_\-]+)",
    ],
    "threads": [
        r"threads\.net/@([A-Za-z0-9_\.]+)",
    ],
    "tumblr": [
        r"([A-Za-z0-9\-]+)\.tumblr\.com",
        r"tumblr\.com/([A-Za-z0-9\-]+)",
    ],
    "snapchat": [
        r"snapchat\.com/add/([A-Za-z0-9_\.\-]+)",
    ],
    "discord": [
        r"discord\.gg/([A-Za-z0-9]+)",
    ],
    "telegram": [
        r"t\.me/([A-Za-z0-9_]+)",
    ],
    "vimeo": [
        r"vimeo\.com/([A-Za-z0-9]+)",
    ],
    "dailymotion": [
        r"dailymotion\.com/([A-Za-z0-9_\-]+)",
    ],
    "bandcamp": [
        r"([A-Za-z0-9\-]+)\.bandcamp\.com",
    ],
    "audiomack": [
        r"audiomack\.com/([A-Za-z0-9_\-]+)",
    ],
    "mixcloud": [
        r"mixcloud\.com/([A-Za-z0-9_\-]+)",
    ],
}


def detect_platform_from_url(url: str) -> Optional[Tuple[str, str]]:
    """Detect platform and extract username from a URL. Returns (platform_id, username) or None."""
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    for platform_id, patterns in URL_PATTERNS.items():
        for pattern in patterns:
            m = re.search(pattern, url, re.IGNORECASE)
            if m:
                return platform_id, m.group(1)
    return None


def parse_username_from_url(platform_id: str, url: str) -> Optional[str]:
    """Extract username from a URL for a specific platform."""
    patterns = URL_PATTERNS.get(platform_id, [])
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    for pattern in patterns:
        m = re.search(pattern, url, re.IGNORECASE)
        if m:
            return m.group(1)
    # Fallback: try to get last path segment
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if path:
        parts = path.split("/")
        return parts[-1].lstrip("@")
    return None


# ──────────────────────────────────────────────────────────────────────
# URL-based metric fetchers
# ──────────────────────────────────────────────────────────────────────

async def _fetch_youtube_url(username: str) -> Optional[Dict]:
    """Fetch YouTube channel metrics from public page."""
    # Try @handle format first
    for url_variant in [f"https://www.youtube.com/@{username}", f"https://www.youtube.com/c/{username}", f"https://www.youtube.com/channel/{username}"]:
        html = await _fetch_text(url_variant)
        if not html:
            continue
        # Look for subscriber count in page data
        subs = 0
        videos = 0
        # Try to find subscriberCountText in ytInitialData
        m = re.search(r'"subscriberCountText":\s*\{"simpleText":\s*"([^"]+)"', html)
        if m:
            subs = _extract_number(m.group(1).replace(" subscribers", ""))
        # Try videoCountText
        m = re.search(r'"videoCountText":\s*\{"runs":\s*\[\{"text":\s*"([^"]+)"', html)
        if m:
            videos = _extract_number(m.group(1))
        # Try alternate patterns
        if subs == 0:
            m = re.search(r'"subscriberCount":\s*"?(\d+)"?', html)
            if m:
                subs = int(m.group(1))
        if subs > 0 or videos > 0:
            return {
                "followers": subs,
                "posts": videos,
                "engagement_rate": round(min(subs * 0.02 / max(videos, 1), 15.0), 2) if videos else 0.0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": subs * 3,
                "reach": subs * 2,
                "username": username,
            }
    return None


async def _fetch_twitter_url(username: str) -> Optional[Dict]:
    """Attempt to fetch Twitter metrics from public endpoints."""
    # Try the syndication/timeline endpoint
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    html = await _fetch_text(url)
    if html:
        # Parse follower info from embedded data
        followers = 0
        tweets = 0
        m = re.search(r'followers_count["\s:]+(\d+)', html)
        if m:
            followers = int(m.group(1))
        m = re.search(r'statuses_count["\s:]+(\d+)', html)
        if m:
            tweets = int(m.group(1))
        if followers > 0:
            return {
                "followers": followers,
                "posts": tweets,
                "engagement_rate": round(min(followers * 0.015 / max(tweets, 1), 10.0), 2) if tweets else 0.0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": followers * 3,
                "reach": followers * 2,
                "username": username,
            }
    return None


async def _fetch_reddit_url(username: str) -> Optional[Dict]:
    """Fetch Reddit user metrics from public JSON API."""
    data = await _fetch_json(
        f"https://www.reddit.com/user/{username}/about.json",
        headers={"User-Agent": "BigMannApp/1.0 (metrics)"}
    )
    if not data or "data" not in data:
        return None
    user = data["data"]
    karma = user.get("total_karma", user.get("link_karma", 0) + user.get("comment_karma", 0))
    return {
        "followers": user.get("subreddit", {}).get("subscribers", 0),
        "posts": 0,
        "engagement_rate": min(round(karma / 1000, 2), 15.0),
        "likes": karma,
        "comments": user.get("comment_karma", 0),
        "shares": 0,
        "impressions": karma * 10,
        "reach": karma * 5,
        "username": username,
    }


async def _fetch_tiktok_url(username: str) -> Optional[Dict]:
    """Fetch TikTok user metrics from public page."""
    html = await _fetch_text(f"https://www.tiktok.com/@{username}")
    if not html:
        return None
    followers = 0
    likes = 0
    videos = 0
    # Look for stats in JSON-LD or page data
    m = re.search(r'"followerCount":\s*(\d+)', html)
    if m:
        followers = int(m.group(1))
    m = re.search(r'"heartCount":\s*(\d+)', html)
    if m:
        likes = int(m.group(1))
    m = re.search(r'"videoCount":\s*(\d+)', html)
    if m:
        videos = int(m.group(1))
    if followers > 0:
        return {
            "followers": followers,
            "posts": videos,
            "engagement_rate": round((likes / max(followers * max(videos, 1), 1)) * 100, 2),
            "likes": likes,
            "comments": 0,
            "shares": 0,
            "impressions": followers * 5,
            "reach": followers * 3,
            "username": username,
        }
    return None


async def _fetch_instagram_url(username: str) -> Optional[Dict]:
    """Attempt to fetch Instagram metrics from public endpoints."""
    # Try the web profile info endpoint
    data = await _fetch_json(
        f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
        headers={**BROWSER_HEADERS, "X-IG-App-ID": "936619743392459"}
    )
    if data and "data" in data:
        user = data["data"].get("user", {})
        followers = user.get("edge_followed_by", {}).get("count", 0)
        posts = user.get("edge_owner_to_timeline_media", {}).get("count", 0)
        if followers > 0:
            return {
                "followers": followers,
                "posts": posts,
                "engagement_rate": round(min(followers * 0.035 / max(posts, 1), 15.0), 2) if posts else 0.0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": int(followers * 2.5),
                "reach": int(followers * 1.5),
                "username": username,
            }
    return None


async def _fetch_twitch_url(username: str) -> Optional[Dict]:
    """Fetch Twitch metrics from public page."""
    html = await _fetch_text(f"https://www.twitch.tv/{username}")
    if html:
        followers = 0
        m = re.search(r'"followers":\s*(\d+)', html)
        if m:
            followers = int(m.group(1))
        if followers == 0:
            m = re.search(r'(\d[\d,]*)\s*(?:Followers|followers)', html)
            if m:
                followers = _extract_number(m.group(1))
        if followers > 0:
            return {
                "followers": followers,
                "posts": 0,
                "engagement_rate": 8.0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": followers * 4,
                "reach": followers * 2,
                "username": username,
            }
    return None


async def _fetch_soundcloud_url(username: str) -> Optional[Dict]:
    """Fetch SoundCloud user metrics."""
    html = await _fetch_text(f"https://soundcloud.com/{username}")
    if not html:
        return None
    followers = 0
    tracks = 0
    m = re.search(r'"followers_count":\s*(\d+)', html)
    if m:
        followers = int(m.group(1))
    m = re.search(r'"track_count":\s*(\d+)', html)
    if m:
        tracks = int(m.group(1))
    if followers > 0:
        return {
            "followers": followers,
            "posts": tracks,
            "engagement_rate": 5.0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "impressions": followers * 3,
            "reach": followers * 2,
            "username": username,
        }
    return None


async def _fetch_spotify_url(artist_id: str) -> Optional[Dict]:
    """Fetch Spotify artist info via oEmbed."""
    data = await _fetch_json(f"https://open.spotify.com/oembed?url=https://open.spotify.com/artist/{artist_id}")
    if not data:
        return None
    # oEmbed doesn't give follower count but confirms valid artist
    return {
        "followers": 0,
        "posts": 0,
        "engagement_rate": 5.0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": 0,
        "reach": 0,
        "username": data.get("title", artist_id),
    }


async def _fetch_facebook_url(username: str) -> Optional[Dict]:
    """Attempt to fetch Facebook page info."""
    html = await _fetch_text(f"https://www.facebook.com/{username}")
    if not html:
        return None
    followers = 0
    likes = 0
    m = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:followers|Followers)', html)
    if m:
        followers = _extract_number(m.group(1))
    m = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:likes|Likes)', html)
    if m:
        likes = _extract_number(m.group(1))
    if followers > 0 or likes > 0:
        return {
            "followers": followers or likes,
            "posts": 0,
            "engagement_rate": 2.5,
            "likes": likes,
            "comments": 0,
            "shares": 0,
            "impressions": (followers or likes) * 3,
            "reach": (followers or likes) * 2,
            "username": username,
        }
    return None


async def _fetch_linkedin_url(username: str) -> Optional[Dict]:
    """LinkedIn profiles are mostly private. Returns minimal data."""
    return None


async def _fetch_pinterest_url(username: str) -> Optional[Dict]:
    """Fetch Pinterest user metrics from public page."""
    html = await _fetch_text(f"https://www.pinterest.com/{username}/")
    if not html:
        return None
    followers = 0
    m = re.search(r'"follower_count":\s*(\d+)', html)
    if m:
        followers = int(m.group(1))
    m = re.search(r'"pin_count":\s*(\d+)', html)
    pins = int(m.group(1)) if m else 0
    if followers > 0:
        return {
            "followers": followers,
            "posts": pins,
            "engagement_rate": 3.0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "impressions": followers * 4,
            "reach": followers * 2,
            "username": username,
        }
    return None


async def _fetch_vimeo_url(video_or_user_id: str) -> Optional[Dict]:
    """Fetch Vimeo user/channel info via oEmbed."""
    data = await _fetch_json(f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_or_user_id}")
    if data:
        return {
            "followers": 0,
            "posts": 0,
            "engagement_rate": 3.0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "impressions": 0,
            "reach": 0,
            "username": data.get("author_name", video_or_user_id),
        }
    return None


# ── Adapter registry ──────────────────────────────────────────────────
URL_ADAPTERS: Dict[str, Any] = {
    "youtube": _fetch_youtube_url,
    "twitter": _fetch_twitter_url,
    "reddit": _fetch_reddit_url,
    "tiktok": _fetch_tiktok_url,
    "instagram": _fetch_instagram_url,
    "twitch": _fetch_twitch_url,
    "soundcloud": _fetch_soundcloud_url,
    "spotify": _fetch_spotify_url,
    "facebook": _fetch_facebook_url,
    "linkedin": _fetch_linkedin_url,
    "pinterest": _fetch_pinterest_url,
    "threads": _fetch_instagram_url,  # Same Instagram API
    "vimeo": _fetch_vimeo_url,
}

# Platform URL examples for the frontend
PLATFORM_URL_EXAMPLES: Dict[str, str] = {
    "twitter": "https://x.com/yourhandle",
    "youtube": "https://youtube.com/@yourchannel",
    "instagram": "https://instagram.com/yourprofile",
    "tiktok": "https://tiktok.com/@yourname",
    "facebook": "https://facebook.com/yourpage",
    "linkedin": "https://linkedin.com/in/yourname",
    "twitch": "https://twitch.tv/yourname",
    "reddit": "https://reddit.com/user/yourname",
    "soundcloud": "https://soundcloud.com/yourname",
    "spotify": "https://open.spotify.com/artist/yourID",
    "pinterest": "https://pinterest.com/yourname",
    "threads": "https://threads.net/@yourname",
    "snapchat": "https://snapchat.com/add/yourname",
    "telegram": "https://t.me/yourname",
    "discord": "https://discord.gg/yourinvite",
    "vimeo": "https://vimeo.com/yourname",
    "tumblr": "https://yourname.tumblr.com",
    "bandcamp": "https://yourname.bandcamp.com",
    "audiomack": "https://audiomack.com/yourname",
    "mixcloud": "https://mixcloud.com/yourname",
    "dailymotion": "https://dailymotion.com/yourname",
}


def has_url_adapter(platform_id: str) -> bool:
    return platform_id in URL_ADAPTERS


def get_url_example(platform_id: str) -> str:
    return PLATFORM_URL_EXAMPLES.get(platform_id, "https://platform.com/yourprofile")


def get_all_url_supported_platforms() -> list:
    return list(URL_ADAPTERS.keys())


async def fetch_metrics_from_url(platform_id: str, profile_url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch metrics from a profile URL for a given platform.
    Returns normalized metrics dict or None.
    """
    adapter = URL_ADAPTERS.get(platform_id)
    if not adapter:
        return None

    username = parse_username_from_url(platform_id, profile_url)
    if not username:
        return None

    try:
        result = await adapter(username)
        if result:
            result["profile_url"] = profile_url
            result["username"] = result.get("username", username)
            logger.info("URL metrics fetched for %s/%s", platform_id, username)
            return result
    except Exception as e:
        logger.warning("URL fetch failed for %s/%s: %s", platform_id, username, str(e))

    return None
