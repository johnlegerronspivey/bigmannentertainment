"""
Usage Analytics API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from usage_analytics_service import get_analytics_tracking_service

router = APIRouter(prefix="/analytics-tracking", tags=["Usage Analytics"])


class TrackEventRequest(BaseModel):
    event_type: str
    category: str = "general"
    user_id: str = "anonymous"
    metadata: Optional[Dict[str, Any]] = None


class TrackBatchRequest(BaseModel):
    events: List[Dict[str, Any]]


@router.get("/health")
async def analytics_health():
    return {"status": "healthy", "service": "Usage Analytics Tracking"}


@router.post("/track")
async def track_event(request: TrackEventRequest):
    """Track a single usage event"""
    svc = get_analytics_tracking_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Analytics service unavailable")
    return await svc.track_event(
        request.event_type, request.category,
        request.user_id, request.metadata
    )


@router.post("/track-batch")
async def track_batch(request: TrackBatchRequest):
    """Track multiple events at once"""
    svc = get_analytics_tracking_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Analytics service unavailable")
    return await svc.track_batch_events(request.events)


@router.get("/dashboard")
async def get_dashboard(period: str = Query(default="7d", regex="^(1d|7d|14d|30d|90d)$")):
    """Get aggregated analytics dashboard"""
    svc = get_analytics_tracking_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Analytics service unavailable")
    return await svc.get_dashboard_stats(period)


@router.get("/features")
async def get_feature_usage(period: str = Query(default="7d", regex="^(1d|7d|14d|30d|90d)$")):
    """Get feature-level usage breakdown"""
    svc = get_analytics_tracking_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Analytics service unavailable")
    return await svc.get_feature_usage(period)


@router.get("/users/{user_id}")
async def get_user_activity(user_id: str,
                            period: str = Query(default="30d", regex="^(1d|7d|14d|30d|90d)$")):
    """Get activity for a specific user"""
    svc = get_analytics_tracking_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Analytics service unavailable")
    return await svc.get_user_activity(user_id, period)


@router.get("/realtime")
async def get_realtime_stats():
    """Get real-time stats (last 1 hour)"""
    svc = get_analytics_tracking_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Analytics service unavailable")
    return await svc.get_real_time_stats()
