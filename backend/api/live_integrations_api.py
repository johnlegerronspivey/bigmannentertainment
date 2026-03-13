"""
Live Integration API Routes
- CloudFront distribution setup
- Twitter/X, TikTok, Snapchat OAuth flows & connection testing
- Unified multi-platform content publishing
- Platform credential management
"""
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from auth.service import get_current_user
from models.core import User
from config.database import db
from services.cloudfront_setup_service import CloudFrontSetupService
from services.social_platform_manager import (
    TwitterConnectionManager,
    TikTokConnectionManager,
    SnapchatConnectionManager,
    save_platform_credentials,
    get_platform_credentials,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integrations", tags=["Live Integrations"])


# ── Request Models ──────────────────────────────────────────

class OAuthCallbackPayload(BaseModel):
    code: str
    redirect_uri: str
    code_verifier: Optional[str] = None  # For Twitter PKCE
    state: Optional[str] = None


class CredentialSavePayload(BaseModel):
    platform_id: str
    credentials: dict
    display_name: Optional[str] = ""


class TweetPayload(BaseModel):
    text: str
    access_token: Optional[str] = None


class TikTokPublishPayload(BaseModel):
    title: str
    video_url: Optional[str] = None
    photo_urls: Optional[List[str]] = None


class SnapchatPublishPayload(BaseModel):
    text: str


class MultiPlatformPublishPayload(BaseModel):
    text: str
    platforms: List[str]
    media_url: Optional[str] = None


# ── CloudFront Setup ────────────────────────────────────────

@router.post("/cloudfront/setup")
async def setup_cloudfront(current_user: User = Depends(get_current_user)):
    """Create a CloudFront distribution for the S3 media bucket."""
    svc = CloudFrontSetupService()
    result = svc.create_distribution()

    if result.get("success") and result.get("distribution_id"):
        svc.update_env_distribution_id(
            result["distribution_id"],
            result.get("domain_name", ""),
        )

    return {
        "status": "success" if result.get("success") else "error",
        "data": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/cloudfront/status")
async def cloudfront_status(current_user: User = Depends(get_current_user)):
    """Get the current CloudFront distribution status."""
    dist_id = os.environ.get("CLOUDFRONT_DISTRIBUTION_ID", "")
    domain = os.environ.get("CLOUDFRONT_DOMAIN", "")

    if not dist_id:
        return {
            "configured": False,
            "message": "No CloudFront distribution ID set. Call POST /api/integrations/cloudfront/setup",
            "domain": domain,
        }

    svc = CloudFrontSetupService()
    status = svc.get_distribution_status(dist_id)
    return {
        "configured": True,
        "distribution_id": dist_id,
        "domain": domain,
        **status,
    }


# ── Twitter / X ─────────────────────────────────────────────

_twitter = TwitterConnectionManager()


@router.get("/twitter/auth-url")
async def twitter_auth_url(
    redirect_uri: str = Query(..., description="OAuth redirect URI"),
    current_user: User = Depends(get_current_user),
):
    """Generate a Twitter OAuth 2.0 authorization URL with PKCE."""
    state = str(uuid.uuid4())
    result = _twitter.get_authorization_url(redirect_uri, state)
    return result


@router.post("/twitter/callback")
async def twitter_callback(
    payload: OAuthCallbackPayload,
    current_user: User = Depends(get_current_user),
):
    """Exchange Twitter authorization code for access tokens."""
    if not payload.code_verifier:
        raise HTTPException(400, "code_verifier is required for Twitter PKCE flow")

    result = await _twitter.exchange_code(payload.code, payload.redirect_uri, payload.code_verifier)

    if result.get("success"):
        await save_platform_credentials(
            user_id=current_user.id,
            platform_id="twitter_x",
            credentials={
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", ""),
                "token_type": result.get("token_type", "bearer"),
                "scope": result.get("scope", ""),
            },
            display_name="Twitter/X",
        )

    return result


@router.get("/twitter/test")
async def twitter_test(current_user: User = Depends(get_current_user)):
    """Test Twitter connection using stored or env credentials."""
    creds = await get_platform_credentials(current_user.id, "twitter_x")
    token = creds.get("access_token") or creds.get("bearer_token") if creds else None
    result = await _twitter.test_connection(token)
    return result


@router.post("/twitter/tweet")
async def post_tweet(
    payload: TweetPayload,
    current_user: User = Depends(get_current_user),
):
    """Post a tweet to Twitter/X."""
    creds = await get_platform_credentials(current_user.id, "twitter_x")
    token = payload.access_token or (creds.get("access_token") if creds else None)
    if not token:
        raise HTTPException(400, "No access token. Connect Twitter first via OAuth.")
    result = await _twitter.post_tweet(payload.text, token)
    return result


# ── TikTok ───────────────────────────────────────────────────

_tiktok = TikTokConnectionManager()


@router.get("/tiktok/auth-url")
async def tiktok_auth_url(
    redirect_uri: str = Query(..., description="OAuth redirect URI"),
    current_user: User = Depends(get_current_user),
):
    """Generate a TikTok authorization URL."""
    state = str(uuid.uuid4())
    result = _tiktok.get_authorization_url(redirect_uri, state)
    return result


@router.post("/tiktok/callback")
async def tiktok_callback(
    payload: OAuthCallbackPayload,
    current_user: User = Depends(get_current_user),
):
    """Exchange TikTok authorization code for access tokens."""
    result = await _tiktok.exchange_code(payload.code, payload.redirect_uri)

    if result.get("success"):
        await save_platform_credentials(
            user_id=current_user.id,
            platform_id="tiktok",
            credentials={
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", ""),
                "open_id": result.get("open_id", ""),
                "expires_in": result.get("expires_in", 0),
            },
            display_name="TikTok",
        )

    return result


@router.get("/tiktok/test")
async def tiktok_test(current_user: User = Depends(get_current_user)):
    """Test TikTok connection using stored credentials."""
    creds = await get_platform_credentials(current_user.id, "tiktok")
    token = creds.get("access_token") if creds else ""
    if not token:
        return {"connected": False, "error": "No TikTok access token. Connect via OAuth first."}
    result = await _tiktok.test_connection(token)
    return result


# ── Snapchat ─────────────────────────────────────────────────

_snapchat = SnapchatConnectionManager()


@router.get("/snapchat/test")
async def snapchat_test(current_user: User = Depends(get_current_user)):
    """Test Snapchat connection using stored or env token."""
    creds = await get_platform_credentials(current_user.id, "snapchat")
    token = creds.get("api_token") if creds else None
    result = await _snapchat.test_connection(token)
    return result


@router.get("/snapchat/ad-accounts")
async def snapchat_ad_accounts(current_user: User = Depends(get_current_user)):
    """List Snapchat ad accounts."""
    creds = await get_platform_credentials(current_user.id, "snapchat")
    token = creds.get("api_token") if creds else None
    result = await _snapchat.get_ad_accounts(token)
    return result


@router.post("/snapchat/publish")
async def snapchat_publish(
    payload: SnapchatPublishPayload,
    current_user: User = Depends(get_current_user),
):
    """Publish content to Snapchat."""
    creds = await get_platform_credentials(current_user.id, "snapchat")
    token = creds.get("api_token") if creds else None
    if not token:
        raise HTTPException(400, "No Snapchat API token. Configure credentials first.")
    result = await _snapchat.publish_content(payload.text, token)
    return result


# ── TikTok Publish ────────────────────────────────────────────

@router.post("/tiktok/publish")
async def tiktok_publish(
    payload: TikTokPublishPayload,
    current_user: User = Depends(get_current_user),
):
    """Publish video or photo content to TikTok."""
    creds = await get_platform_credentials(current_user.id, "tiktok")
    token = creds.get("access_token") if creds else ""
    if not token:
        raise HTTPException(400, "No TikTok access token. Connect via OAuth first.")

    if payload.video_url:
        result = await _tiktok.publish_video(payload.video_url, payload.title, token)
    elif payload.photo_urls:
        result = await _tiktok.publish_photo(payload.photo_urls, payload.title, token)
    else:
        raise HTTPException(400, "Provide video_url or photo_urls for TikTok publishing.")
    return result


# ── Unified Multi-Platform Publish ────────────────────────────

@router.post("/publish")
async def publish_to_platforms(
    payload: MultiPlatformPublishPayload,
    current_user: User = Depends(get_current_user),
):
    """Publish content to multiple platforms simultaneously."""
    results = {}
    publish_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    for platform in payload.platforms:
        try:
            if platform == "twitter_x":
                creds = await get_platform_credentials(current_user.id, "twitter_x")
                token = creds.get("access_token") if creds else None
                if not token:
                    results[platform] = {"success": False, "error": "No Twitter access token. Connect via OAuth for write access."}
                    continue
                result = await _twitter.post_tweet(payload.text, token)
                results[platform] = result

            elif platform == "tiktok":
                creds = await get_platform_credentials(current_user.id, "tiktok")
                token = creds.get("access_token") if creds else ""
                if not token:
                    results[platform] = {"success": False, "error": "No TikTok access token. Connect via OAuth first."}
                    continue
                if payload.media_url:
                    result = await _tiktok.publish_video(payload.media_url, payload.text, token)
                else:
                    results[platform] = {"success": False, "error": "TikTok requires a video or photo URL to publish."}
                    continue
                results[platform] = result

            elif platform == "snapchat":
                creds = await get_platform_credentials(current_user.id, "snapchat")
                token = creds.get("api_token") if creds else None
                if not token:
                    results[platform] = {"success": False, "error": "No Snapchat API token configured."}
                    continue
                result = await _snapchat.publish_content(payload.text, token)
                results[platform] = result

            else:
                results[platform] = {"success": False, "error": f"Unsupported platform: {platform}"}

        except Exception as e:
            logger.error(f"Publish to {platform} failed: {e}")
            results[platform] = {"success": False, "error": str(e)[:300]}

    # Save publish record to DB
    succeeded = sum(1 for r in results.values() if r.get("success"))
    total = len(payload.platforms)
    record = {
        "id": publish_id,
        "user_id": current_user.id,
        "text": payload.text,
        "media_url": payload.media_url,
        "platforms": payload.platforms,
        "results": results,
        "succeeded": succeeded,
        "total": total,
        "created_at": now,
    }
    await db.publish_history.insert_one(record)

    return {
        "publish_id": publish_id,
        "results": results,
        "summary": f"{succeeded}/{total} platforms succeeded",
        "timestamp": now,
    }


@router.get("/publish/history")
async def publish_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get recent publish history for the current user."""
    records = []
    cursor = db.publish_history.find(
        {"user_id": current_user.id}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    async for doc in cursor:
        records.append(doc)
    return {"history": records, "count": len(records)}


# ── Generic Credential Management ────────────────────────────

@router.post("/credentials/save")
async def save_credentials(
    payload: CredentialSavePayload,
    current_user: User = Depends(get_current_user),
):
    """Save credentials for any platform."""
    result = await save_platform_credentials(
        user_id=current_user.id,
        platform_id=payload.platform_id,
        credentials=payload.credentials,
        display_name=payload.display_name,
    )
    return result


@router.get("/credentials/{platform_id}")
async def get_credentials(
    platform_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get stored credentials for a platform (masked)."""
    creds = await get_platform_credentials(current_user.id, platform_id)
    if not creds:
        return {"platform_id": platform_id, "has_credentials": False}

    masked = {}
    for k, v in creds.items():
        if isinstance(v, str) and len(v) > 8:
            masked[k] = v[:4] + "****" + v[-4:]
        else:
            masked[k] = v
    return {"platform_id": platform_id, "has_credentials": True, "credentials": masked}


@router.get("/status/all")
async def all_integration_status(current_user: User = Depends(get_current_user)):
    """Get connection status for all live-integration platforms."""
    platforms = {}

    # Twitter
    twitter_creds = await get_platform_credentials(current_user.id, "twitter_x")
    platforms["twitter_x"] = {
        "platform": "Twitter/X",
        "has_credentials": bool(twitter_creds),
        "credential_source": "env" if (twitter_creds and twitter_creds.get("bearer_token")) else "user",
        "oauth_required": True,
        "can_read": bool(twitter_creds),
        "can_write": bool(twitter_creds and twitter_creds.get("access_token") and twitter_creds.get("access_token") != twitter_creds.get("bearer_token")),
    }

    # TikTok
    tiktok_creds = await get_platform_credentials(current_user.id, "tiktok")
    platforms["tiktok"] = {
        "platform": "TikTok",
        "has_credentials": bool(tiktok_creds and tiktok_creds.get("access_token")),
        "credential_source": "user",
        "oauth_required": True,
        "can_read": bool(tiktok_creds and tiktok_creds.get("access_token")),
        "can_write": bool(tiktok_creds and tiktok_creds.get("access_token")),
    }

    # Snapchat
    snap_creds = await get_platform_credentials(current_user.id, "snapchat")
    platforms["snapchat"] = {
        "platform": "Snapchat",
        "has_credentials": bool(snap_creds),
        "credential_source": "env" if (snap_creds and not (await get_platform_credentials(current_user.id, "snapchat"))) else "env_fallback",
        "oauth_required": False,
        "can_read": bool(snap_creds),
        "can_write": bool(snap_creds),
    }

    # CloudFront
    dist_id = os.environ.get("CLOUDFRONT_DISTRIBUTION_ID", "")
    platforms["cloudfront"] = {
        "platform": "AWS CloudFront CDN",
        "configured": bool(dist_id),
        "distribution_id": dist_id,
        "domain": os.environ.get("CLOUDFRONT_DOMAIN", ""),
    }

    return {
        "platforms": platforms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
