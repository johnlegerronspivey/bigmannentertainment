"""
Creator Analytics Dashboard - Insights on content, audience, revenue,
anomaly detection, demographics, and best-time-to-post.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from config.database import db
from auth.service import get_current_user
from services.anomaly_detection_service import (
    run_anomaly_detection,
    get_anomaly_alerts,
    dismiss_anomaly,
)
from services.audience_analytics_service import (
    get_audience_demographics,
    get_best_times_to_post,
    get_geographic_distribution,
)
from services.revenue_tracking_service import (
    get_revenue_overview,
    get_platform_revenue_detail,
    record_revenue,
)

router = APIRouter(prefix="/analytics", tags=["Creator Analytics"])


@router.get("/overview")
async def get_overview(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    # Content stats
    total_content = await db.user_content.count_documents({"user_id": user_id})
    content_by_type = {}
    for ctype in ["audio", "video", "image"]:
        content_by_type[ctype] = await db.user_content.count_documents({"user_id": user_id, "content_type": ctype})

    # Aggregate views/downloads/likes across all content
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "total_views": {"$sum": "$stats.views"},
            "total_downloads": {"$sum": "$stats.downloads"},
            "total_likes": {"$sum": "$stats.likes"},
        }},
    ]
    agg = await db.user_content.aggregate(pipeline).to_list(1)
    engagement = agg[0] if agg else {"total_views": 0, "total_downloads": 0, "total_likes": 0}
    engagement.pop("_id", None)

    # Profile stats
    profile = await db.creator_profiles.find_one({"user_id": user_id}, {"_id": 0, "stats": 1, "subscription_tier": 1})
    profile_stats = profile.get("stats", {}) if profile else {}
    tier = profile.get("subscription_tier", "free") if profile else "free"

    # Message stats
    total_conversations = await db.conversations.count_documents({"participants.user_id": user_id})

    return {
        "total_content": total_content,
        "content_by_type": content_by_type,
        "engagement": engagement,
        "profile_stats": profile_stats,
        "subscription_tier": tier,
        "total_conversations": total_conversations,
    }


@router.get("/content-performance")
async def get_content_performance(
    sort_by: str = "views",
    limit: int = 20,
    current_user=Depends(get_current_user),
):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    sort_field = f"stats.{sort_by}" if sort_by in ["views", "downloads", "likes"] else "stats.views"

    cursor = db.user_content.find(
        {"user_id": user_id},
        {"_id": 0, "file_id": 1, "title": 1, "content_type": 1, "stats": 1, "visibility": 1, "created_at": 1, "tags": 1},
    ).sort(sort_field, -1).limit(limit)

    items = []
    async for doc in cursor:
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        items.append(doc)

    return {"items": items}


@router.get("/audience")
async def get_audience_insights(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    profile = await db.creator_profiles.find_one({"user_id": user_id}, {"_id": 0, "stats": 1})
    followers = profile.get("stats", {}).get("total_followers", 0) if profile else 0

    # Simulate growth data (last 7 days) from analytics_events if available
    now = datetime.now(timezone.utc)
    growth = []
    for i in range(7):
        day = now - timedelta(days=6 - i)
        day_str = day.strftime("%Y-%m-%d")
        count = await db.analytics_events.count_documents({
            "user_id": user_id,
            "event_type": "follow",
            "date": day_str,
        })
        growth.append({"date": day_str, "new_followers": count})

    # Top content that attracted followers
    top_content = await db.user_content.find(
        {"user_id": user_id, "visibility": "public"},
        {"_id": 0, "title": 1, "content_type": 1, "stats": 1},
    ).sort("stats.views", -1).limit(5).to_list(5)

    return {
        "total_followers": followers,
        "growth": growth,
        "top_content": top_content,
    }


@router.get("/revenue")
async def get_revenue_insights(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    profile = await db.creator_profiles.find_one({"user_id": user_id}, {"_id": 0, "stats": 1})
    total_earnings = profile.get("stats", {}).get("total_earnings", 0.0) if profile else 0.0

    # Revenue by month (from analytics_events)
    now = datetime.now(timezone.utc)
    monthly = []
    for i in range(6):
        month = now - timedelta(days=30 * (5 - i))
        month_str = month.strftime("%Y-%m")
        pipeline = [
            {"$match": {"user_id": user_id, "event_type": "revenue", "month": month_str}},
            {"$group": {"_id": None, "amount": {"$sum": "$amount"}}},
        ]
        result = await db.analytics_events.aggregate(pipeline).to_list(1)
        amount = result[0]["amount"] if result else 0.0
        monthly.append({"month": month_str, "amount": amount})

    return {
        "total_earnings": total_earnings,
        "monthly_revenue": monthly,
    }


@router.post("/track")
async def track_event(
    event_type: str,
    target_user_id: str = None,
    content_id: str = None,
    amount: float = 0.0,
    current_user=Depends(get_current_user),
):
    """Track an analytics event (view, download, like, follow, revenue)."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    now = datetime.now(timezone.utc)

    event = {
        "user_id": target_user_id or user_id,
        "triggered_by": user_id,
        "event_type": event_type,
        "content_id": content_id,
        "amount": amount,
        "date": now.strftime("%Y-%m-%d"),
        "month": now.strftime("%Y-%m"),
        "created_at": now,
    }
    await db.analytics_events.insert_one(event)

    # Update content stats if applicable
    if content_id and event_type in ["view", "download", "like"]:
        stat_key = f"stats.{event_type}s"
        await db.user_content.update_one(
            {"file_id": content_id},
            {"$inc": {stat_key: 1}},
        )

    return {"message": "Event tracked"}


# ─── Anomaly Detection Endpoints ───

@router.get("/anomalies")
async def get_anomalies(include_dismissed: bool = False, current_user=Depends(get_current_user)):
    """Get anomaly alerts for the current user."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    alerts = await get_anomaly_alerts(user_id, include_dismissed)
    return {"alerts": alerts, "total": len(alerts)}


@router.post("/anomalies/scan")
async def scan_anomalies(current_user=Depends(get_current_user)):
    """Run anomaly detection scan across all platforms."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    anomalies = await run_anomaly_detection(user_id)
    return {"detected": len(anomalies), "anomalies": anomalies}


class DismissAnomalyRequest(BaseModel):
    platform_id: str
    metric: str


@router.post("/anomalies/dismiss")
async def dismiss_anomaly_alert(req: DismissAnomalyRequest, current_user=Depends(get_current_user)):
    """Dismiss an anomaly alert."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    dismissed = await dismiss_anomaly(user_id, req.platform_id, req.metric)
    if not dismissed:
        raise HTTPException(status_code=404, detail="Anomaly alert not found")
    return {"message": "Alert dismissed"}


# ─── Audience Demographics & Best Time Endpoints ───

@router.get("/demographics")
async def get_demographics(current_user=Depends(get_current_user)):
    """Get audience demographics breakdown."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    return await get_audience_demographics(user_id)


@router.get("/best-times")
async def get_best_posting_times(current_user=Depends(get_current_user)):
    """Get best times to post based on engagement analysis."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    return await get_best_times_to_post(user_id)


@router.get("/geo")
async def get_geo_distribution(current_user=Depends(get_current_user)):
    """Get audience geographic distribution."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    return await get_geographic_distribution(user_id)


# ─── Enhanced Revenue Endpoints ───

@router.get("/revenue/overview")
async def get_revenue_dashboard(current_user=Depends(get_current_user)):
    """Get comprehensive revenue overview with platform and source breakdowns."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    return await get_revenue_overview(user_id)


@router.get("/revenue/platform/{platform_id}")
async def get_platform_revenue(platform_id: str, current_user=Depends(get_current_user)):
    """Get detailed revenue for a specific platform."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    return await get_platform_revenue_detail(user_id, platform_id)


class RecordRevenueRequest(BaseModel):
    platform_id: str
    platform_name: str = ""
    content_id: str = ""
    content_title: str = ""
    source: str = "streaming"
    amount: float
    description: str = ""


@router.post("/revenue/record")
async def record_new_revenue(req: RecordRevenueRequest, current_user=Depends(get_current_user)):
    """Record a new revenue entry."""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    return await record_revenue(user_id, req.dict())
