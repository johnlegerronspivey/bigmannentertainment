"""
Usage Analytics Service
Tracks user engagement, feature usage, and provides aggregated analytics.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid


class UsageAnalyticsService:
    """Service for tracking and querying usage analytics"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.events_collection = db.usage_analytics_events
        self.sessions_collection = db.usage_analytics_sessions

    async def track_event(self, event_type: str, category: str,
                          user_id: str = "anonymous",
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Track a single usage event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "category": category,
            "user_id": user_id,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.events_collection.insert_one(event)
        return {
            "event_id": event["event_id"],
            "event_type": event_type,
            "category": category,
            "tracked": True
        }

    async def track_batch_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Track multiple events at once"""
        docs = []
        for e in events:
            docs.append({
                "event_id": str(uuid.uuid4()),
                "event_type": e.get("event_type", "unknown"),
                "category": e.get("category", "general"),
                "user_id": e.get("user_id", "anonymous"),
                "metadata": e.get("metadata", {}),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        if docs:
            await self.events_collection.insert_many(docs)
        return {"tracked": len(docs)}

    async def get_dashboard_stats(self, period: str = "7d") -> Dict[str, Any]:
        """Get aggregated dashboard statistics"""
        cutoff = self._get_cutoff(period)

        pipeline_total = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$count": "total"}
        ]
        total_result = await self.events_collection.aggregate(pipeline_total).to_list(1)
        total_events = total_result[0]["total"] if total_result else 0

        pipeline_users = [
            {"$match": {"timestamp": {"$gte": cutoff}, "user_id": {"$ne": "anonymous"}}},
            {"$group": {"_id": "$user_id"}},
            {"$count": "total"}
        ]
        users_result = await self.events_collection.aggregate(pipeline_users).to_list(1)
        active_users = users_result[0]["total"] if users_result else 0

        pipeline_categories = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        cat_result = await self.events_collection.aggregate(pipeline_categories).to_list(20)
        categories = {r["_id"]: r["count"] for r in cat_result}

        pipeline_types = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 15}
        ]
        type_result = await self.events_collection.aggregate(pipeline_types).to_list(15)
        top_events = [{"event": r["_id"], "count": r["count"]} for r in type_result]

        pipeline_daily = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$addFields": {"date": {"$substr": ["$timestamp", 0, 10]}}},
            {"$group": {"_id": "$date", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        daily_result = await self.events_collection.aggregate(pipeline_daily).to_list(60)
        daily_trend = [{"date": r["_id"], "events": r["count"]} for r in daily_result]

        # If no data in DB, return sample data for demo
        if total_events == 0:
            return self._sample_dashboard(period)

        return {
            "period": period,
            "total_events": total_events,
            "active_users": active_users,
            "categories": categories,
            "top_events": top_events,
            "daily_trend": daily_trend,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def get_feature_usage(self, period: str = "7d") -> Dict[str, Any]:
        """Get feature-level usage breakdown"""
        cutoff = self._get_cutoff(period)

        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$group": {
                "_id": {"category": "$category", "event_type": "$event_type"},
                "count": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"}
            }},
            {"$project": {
                "_id": 0,
                "category": "$_id.category",
                "event_type": "$_id.event_type",
                "count": 1,
                "unique_users": {"$size": "$unique_users"}
            }},
            {"$sort": {"count": -1}}
        ]
        result = await self.events_collection.aggregate(pipeline).to_list(50)

        if not result:
            return self._sample_feature_usage(period)

        features = {}
        for r in result:
            cat = r["category"]
            if cat not in features:
                features[cat] = {"total": 0, "events": []}
            features[cat]["total"] += r["count"]
            features[cat]["events"].append({
                "event_type": r["event_type"],
                "count": r["count"],
                "unique_users": r["unique_users"]
            })

        return {"period": period, "features": features}

    async def get_user_activity(self, user_id: str, period: str = "30d") -> Dict[str, Any]:
        """Get activity breakdown for a specific user"""
        cutoff = self._get_cutoff(period)

        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff}, "user_id": user_id}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = await self.events_collection.aggregate(pipeline).to_list(30)
        activity = [{"event": r["_id"], "count": r["count"]} for r in result]

        pipeline_daily = [
            {"$match": {"timestamp": {"$gte": cutoff}, "user_id": user_id}},
            {"$addFields": {"date": {"$substr": ["$timestamp", 0, 10]}}},
            {"$group": {"_id": "$date", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        daily = await self.events_collection.aggregate(pipeline_daily).to_list(60)
        daily_trend = [{"date": r["_id"], "events": r["count"]} for r in daily]

        return {
            "user_id": user_id,
            "period": period,
            "activity": activity,
            "daily_trend": daily_trend,
            "total_events": sum(a["count"] for a in activity)
        }

    async def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time stats (last 1 hour)"""
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        pipeline = [
            {"$match": {"timestamp": {"$gte": one_hour_ago}}},
            {"$group": {
                "_id": "$event_type",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        result = await self.events_collection.aggregate(pipeline).to_list(10)

        pipeline_total = [
            {"$match": {"timestamp": {"$gte": one_hour_ago}}},
            {"$count": "total"}
        ]
        total = await self.events_collection.aggregate(pipeline_total).to_list(1)

        return {
            "last_hour_events": total[0]["total"] if total else 0,
            "top_events": [{"event": r["_id"], "count": r["count"]} for r in result],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _get_cutoff(self, period: str) -> str:
        days_map = {"1d": 1, "7d": 7, "14d": 14, "30d": 30, "90d": 90}
        days = days_map.get(period, 7)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return cutoff.isoformat()

    def _sample_dashboard(self, period: str) -> Dict[str, Any]:
        """Generate sample data for demo when no real data exists"""
        now = datetime.now(timezone.utc)
        days = {"1d": 1, "7d": 7, "14d": 14, "30d": 30, "90d": 90}.get(period, 7)

        daily_trend = []
        for i in range(days):
            d = now - timedelta(days=days - 1 - i)
            base = 45 + (i * 3)
            daily_trend.append({
                "date": d.strftime("%Y-%m-%d"),
                "events": base + (hash(d.strftime("%Y-%m-%d")) % 30)
            })

        total = sum(d["events"] for d in daily_trend)

        return {
            "period": period,
            "total_events": total,
            "active_users": 24,
            "categories": {
                "creative_studio": int(total * 0.35),
                "ai_tools": int(total * 0.25),
                "collaboration": int(total * 0.15),
                "projects": int(total * 0.12),
                "marketplace": int(total * 0.08),
                "auth": int(total * 0.05)
            },
            "top_events": [
                {"event": "canvas_edit", "count": int(total * 0.18)},
                {"event": "ai_text_generate", "count": int(total * 0.12)},
                {"event": "project_open", "count": int(total * 0.10)},
                {"event": "ai_palette_generate", "count": int(total * 0.09)},
                {"event": "element_add", "count": int(total * 0.08)},
                {"event": "smart_resize", "count": int(total * 0.07)},
                {"event": "comment_add", "count": int(total * 0.06)},
                {"event": "layout_apply", "count": int(total * 0.05)},
                {"event": "export_png", "count": int(total * 0.04)},
                {"event": "login", "count": int(total * 0.03)}
            ],
            "daily_trend": daily_trend,
            "generated_at": now.isoformat(),
            "sample_data": True
        }

    def _sample_feature_usage(self, period: str) -> Dict[str, Any]:
        return {
            "period": period,
            "features": {
                "creative_studio": {
                    "total": 312,
                    "events": [
                        {"event_type": "canvas_edit", "count": 142, "unique_users": 18},
                        {"event_type": "element_add", "count": 89, "unique_users": 15},
                        {"event_type": "project_create", "count": 45, "unique_users": 12},
                        {"event_type": "export_png", "count": 36, "unique_users": 10}
                    ]
                },
                "ai_tools": {
                    "total": 224,
                    "events": [
                        {"event_type": "ai_text_generate", "count": 98, "unique_users": 16},
                        {"event_type": "ai_palette_generate", "count": 62, "unique_users": 14},
                        {"event_type": "smart_resize", "count": 38, "unique_users": 9},
                        {"event_type": "layout_suggest", "count": 26, "unique_users": 8}
                    ]
                },
                "collaboration": {
                    "total": 156,
                    "events": [
                        {"event_type": "comment_add", "count": 67, "unique_users": 12},
                        {"event_type": "version_save", "count": 48, "unique_users": 11},
                        {"event_type": "presence_join", "count": 41, "unique_users": 14}
                    ]
                },
                "projects": {
                    "total": 95,
                    "events": [
                        {"event_type": "project_open", "count": 52, "unique_users": 18},
                        {"event_type": "project_create", "count": 28, "unique_users": 12},
                        {"event_type": "project_delete", "count": 15, "unique_users": 8}
                    ]
                }
            },
            "sample_data": True
        }


_analytics_service = None


def initialize_analytics_tracking(db: AsyncIOMotorDatabase) -> UsageAnalyticsService:
    global _analytics_service
    _analytics_service = UsageAnalyticsService(db)
    return _analytics_service


def get_analytics_tracking_service() -> Optional[UsageAnalyticsService]:
    return _analytics_service
