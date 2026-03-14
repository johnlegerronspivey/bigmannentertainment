"""AWS Live Streaming routes - IVS channels + MediaPackage packaging."""
import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from config.database import db
from auth.service import get_current_user
from models.core import User
from datetime import datetime, timezone

router = APIRouter(prefix="/aws-livestream", tags=["AWS Live Streaming"])
logger = logging.getLogger(__name__)

# Lazy-init services
_ivs_svc = None
_mp_svc = None


def _ivs():
    global _ivs_svc
    if _ivs_svc is None:
        from services.ivs_service import IVSService
        _ivs_svc = IVSService()
    return _ivs_svc


def _mediapackage():
    global _mp_svc
    if _mp_svc is None:
        from services.mediapackage_service import MediaPackageService
        _mp_svc = MediaPackageService()
    return _mp_svc


# ── Pydantic models ──────────────────────────────────────────────
class CreateIVSChannelRequest(BaseModel):
    name: str
    channel_type: str = "STANDARD"
    latency_mode: str = "LOW"


class CreateMPChannelRequest(BaseModel):
    channel_id: str
    description: str = ""


class CreateOriginEndpointRequest(BaseModel):
    channel_id: str
    endpoint_id: str
    packaging_format: str = "hls"
    startover_window: int = 86400
    time_delay: int = 0
    description: str = ""


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def livestream_status(current_user: User = Depends(get_current_user)):
    """Overall status of IVS + MediaPackage."""
    ivs = _ivs()
    mp = _mediapackage()

    ivs_status = ivs.get_status()
    mp_status = mp.get_status()

    # Pull stats from MongoDB
    ivs_channels = await db.ivs_channels.count_documents({"user_id": current_user.id})
    mp_channels = await db.mediapackage_channels.count_documents({"user_id": current_user.id})

    return {
        "ivs": {**ivs_status, "total_channels": ivs_channels},
        "mediapackage": {**mp_status, "total_channels": mp_channels},
    }


# ══════════════════════════════════════════════════════════════════
#  IVS CHANNELS
# ══════════════════════════════════════════════════════════════════
@router.post("/ivs/channels")
async def create_ivs_channel(
    body: CreateIVSChannelRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new IVS live streaming channel."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    try:
        result = ivs.create_channel(
            name=body.name,
            channel_type=body.channel_type,
            latency_mode=body.latency_mode,
            tags={"user_id": current_user.id, "Project": "BigMannEntertainment"},
        )
        doc = {
            **result,
            "user_id": current_user.id,
        }
        await db.ivs_channels.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"IVS create channel error: {e}")
        raise HTTPException(500, f"Failed to create channel: {str(e)}")


@router.get("/ivs/channels")
async def list_ivs_channels(current_user: User = Depends(get_current_user)):
    """List all IVS channels."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    try:
        channels = ivs.list_channels()
        # Filter by user tag
        user_channels = [
            ch for ch in channels
            if ch.get("tags", {}).get("user_id") == current_user.id
        ]
        return {"channels": user_channels, "total": len(user_channels)}
    except Exception as e:
        logger.error(f"List IVS channels error: {e}")
        # Fall back to Mongo
        docs = await db.ivs_channels.find(
            {"user_id": current_user.id}, {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        return {"channels": docs, "total": len(docs), "source": "cache"}


@router.get("/ivs/channels/{channel_arn:path}")
async def get_ivs_channel(channel_arn: str, current_user: User = Depends(get_current_user)):
    """Get details of a specific IVS channel."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    try:
        return ivs.get_channel(channel_arn)
    except Exception as e:
        raise HTTPException(404, f"Channel not found: {str(e)}")


@router.delete("/ivs/channels/{channel_arn:path}")
async def delete_ivs_channel(channel_arn: str, current_user: User = Depends(get_current_user)):
    """Delete an IVS channel."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    success = ivs.delete_channel(channel_arn)
    if success:
        await db.ivs_channels.delete_one({"channel_arn": channel_arn})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete channel")


# ── IVS Streams ──────────────────────────────────────────────────
@router.get("/ivs/streams")
async def list_ivs_streams(current_user: User = Depends(get_current_user)):
    """List active IVS streams."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    try:
        streams = ivs.list_streams()
        return {"streams": streams, "total": len(streams)}
    except Exception as e:
        logger.error(f"List streams error: {e}")
        return {"streams": [], "total": 0}


@router.get("/ivs/streams/{channel_arn:path}")
async def get_ivs_stream(channel_arn: str, current_user: User = Depends(get_current_user)):
    """Get stream status for a specific channel."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    try:
        stream = ivs.get_stream(channel_arn)
        if stream:
            return {"streaming": True, **stream}
        return {"streaming": False, "channel_arn": channel_arn}
    except Exception as e:
        raise HTTPException(404, f"Stream not found: {str(e)}")


@router.post("/ivs/streams/{channel_arn:path}/stop")
async def stop_ivs_stream(channel_arn: str, current_user: User = Depends(get_current_user)):
    """Stop an active IVS stream."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    success = ivs.stop_stream(channel_arn)
    if success:
        return {"stopped": True}
    raise HTTPException(500, "Failed to stop stream")


# ── IVS Stream Keys ─────────────────────────────────────────────
@router.post("/ivs/channels/{channel_arn:path}/stream-keys")
async def create_stream_key(channel_arn: str, current_user: User = Depends(get_current_user)):
    """Create a new stream key for an IVS channel."""
    ivs = _ivs()
    if not ivs.available:
        raise HTTPException(503, "IVS not available")
    try:
        return ivs.create_stream_key(channel_arn)
    except Exception as e:
        raise HTTPException(500, f"Failed to create stream key: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  MEDIAPACKAGE CHANNELS
# ══════════════════════════════════════════════════════════════════
@router.get("/mediapackage/formats")
async def list_packaging_formats(current_user: User = Depends(get_current_user)):
    """List available packaging formats."""
    return {"formats": _mediapackage().get_packaging_formats()}


@router.post("/mediapackage/channels")
async def create_mp_channel(
    body: CreateMPChannelRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a MediaPackage channel."""
    mp = _mediapackage()
    if not mp.available:
        raise HTTPException(503, "MediaPackage not available")
    try:
        result = mp.create_channel(body.channel_id, body.description)
        doc = {**result, "user_id": current_user.id}
        await db.mediapackage_channels.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"MediaPackage create channel error: {e}")
        raise HTTPException(500, f"Failed to create channel: {str(e)}")


@router.get("/mediapackage/channels")
async def list_mp_channels(current_user: User = Depends(get_current_user)):
    """List all MediaPackage channels."""
    mp = _mediapackage()
    if not mp.available:
        raise HTTPException(503, "MediaPackage not available")
    try:
        channels = mp.list_channels()
        return {"channels": channels, "total": len(channels)}
    except Exception as e:
        logger.error(f"List MP channels error: {e}")
        docs = await db.mediapackage_channels.find(
            {"user_id": current_user.id}, {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        return {"channels": docs, "total": len(docs), "source": "cache"}


@router.get("/mediapackage/channels/{channel_id}")
async def get_mp_channel(channel_id: str, current_user: User = Depends(get_current_user)):
    """Get details of a specific MediaPackage channel."""
    mp = _mediapackage()
    if not mp.available:
        raise HTTPException(503, "MediaPackage not available")
    try:
        return mp.get_channel(channel_id)
    except Exception as e:
        raise HTTPException(404, f"Channel not found: {str(e)}")


@router.delete("/mediapackage/channels/{channel_id}")
async def delete_mp_channel(channel_id: str, current_user: User = Depends(get_current_user)):
    """Delete a MediaPackage channel."""
    mp = _mediapackage()
    if not mp.available:
        raise HTTPException(503, "MediaPackage not available")
    success = mp.delete_channel(channel_id)
    if success:
        await db.mediapackage_channels.delete_one({"id": channel_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete channel")


# ── MediaPackage Origin Endpoints ────────────────────────────────
@router.post("/mediapackage/endpoints")
async def create_origin_endpoint(
    body: CreateOriginEndpointRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a MediaPackage origin endpoint."""
    mp = _mediapackage()
    if not mp.available:
        raise HTTPException(503, "MediaPackage not available")
    try:
        result = mp.create_origin_endpoint(
            channel_id=body.channel_id,
            endpoint_id=body.endpoint_id,
            packaging_format=body.packaging_format,
            start_over_window=body.startover_window,
            time_delay=body.time_delay,
            description=body.description,
        )
        doc = {**result, "user_id": current_user.id}
        await db.mediapackage_endpoints.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Create origin endpoint error: {e}")
        raise HTTPException(500, f"Failed to create endpoint: {str(e)}")


@router.get("/mediapackage/endpoints")
async def list_origin_endpoints(
    channel_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """List MediaPackage origin endpoints."""
    mp = _mediapackage()
    if not mp.available:
        raise HTTPException(503, "MediaPackage not available")
    try:
        endpoints = mp.list_origin_endpoints(channel_id=channel_id)
        return {"endpoints": endpoints, "total": len(endpoints)}
    except Exception as e:
        logger.error(f"List endpoints error: {e}")
        query = {"user_id": current_user.id}
        if channel_id:
            query["channel_id"] = channel_id
        docs = await db.mediapackage_endpoints.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
        return {"endpoints": docs, "total": len(docs), "source": "cache"}


@router.delete("/mediapackage/endpoints/{endpoint_id}")
async def delete_origin_endpoint(endpoint_id: str, current_user: User = Depends(get_current_user)):
    """Delete a MediaPackage origin endpoint."""
    mp = _mediapackage()
    if not mp.available:
        raise HTTPException(503, "MediaPackage not available")
    success = mp.delete_origin_endpoint(endpoint_id)
    if success:
        await db.mediapackage_endpoints.delete_one({"id": endpoint_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete endpoint")
