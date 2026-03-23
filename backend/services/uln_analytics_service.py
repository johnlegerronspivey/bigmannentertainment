"""
ULN Analytics Service
=====================
Deep cross-label performance analytics for the Unified Label Network.
Provides revenue trends, content sharing metrics, genre/territory breakdowns,
and label comparison data.
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import random

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
logger = logging.getLogger(__name__)


class ULNAnalyticsService:
    def __init__(self):
        self.labels = db.uln_labels
        self.royalty_earnings = db.royalty_earnings
        self.royalty_pools = db.royalty_pools
        self.payout_ledger = db.payout_ledger
        self.federated_content = db.federated_content
        self.dao_proposals = db.dao_proposals
        self.audit_trail = db.uln_audit_trail
        self.analytics_cache = db.uln_analytics_cache

    async def get_cross_label_performance(self) -> Dict[str, Any]:
        """Compare performance across all labels."""
        labels = await self.labels.find({"status": "active"}, projection={"_id": 0}).to_list(length=None)
        performance = []
        for label in labels:
            gid = label["global_id"]["id"]
            name = label["metadata_profile"]["name"]
            ltype = label.get("label_type", "unknown")

            # Count shared content
            shared = await self.federated_content.count_documents({
                "$or": [{"primary_label_id": gid}, {"licensing_labels": gid}]
            })

            # Sum royalties
            pipeline = [
                {"$match": {f"label_splits.{gid}": {"$exists": True}}},
                {"$group": {"_id": None, "total": {"$sum": f"$label_splits.{gid}"}}},
            ]
            total_royalties = 0.0
            async for r in self.royalty_earnings.aggregate(pipeline):
                total_royalties = r.get("total", 0.0)

            contracts = len(label.get("smart_contracts", []))
            entities = len(label.get("associated_entities", []))

            performance.append({
                "label_id": gid,
                "name": name,
                "label_type": ltype,
                "territory": label["metadata_profile"].get("jurisdiction", "US"),
                "genres": label["metadata_profile"].get("genre_specialization", []),
                "shared_content": shared,
                "total_royalties": round(total_royalties, 2),
                "smart_contracts": contracts,
                "team_size": entities,
                "blockchain_enabled": contracts > 0,
                "compliance_verified": label.get("compliance_verified", False),
            })

        # Sort by royalties desc
        performance.sort(key=lambda x: x["total_royalties"], reverse=True)
        return {"success": True, "labels": performance, "total": len(performance)}

    async def get_revenue_trends(self, months: int = 12) -> Dict[str, Any]:
        """Get monthly revenue trends across the network."""
        now = datetime.now(timezone.utc)
        trends = []
        for i in range(months - 1, -1, -1):
            month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            label_str = month_start.strftime("%Y-%m")

            pipeline = [
                {"$match": {"created_at": {"$gte": month_start.isoformat(), "$lte": month_end.isoformat()}}},
                {"$group": {"_id": None, "total": {"$sum": "$gross_amount"}, "count": {"$sum": 1}}},
            ]
            total = 0.0
            count = 0
            async for r in self.royalty_earnings.aggregate(pipeline):
                total = r.get("total", 0.0)
                count = r.get("count", 0)

            trends.append({"month": label_str, "revenue": round(total, 2), "transactions": count})

        return {"success": True, "trends": trends, "period_months": months}

    async def get_genre_breakdown(self) -> Dict[str, Any]:
        """Aggregate label counts and revenue by genre."""
        labels = await self.labels.find({"status": "active"}, projection={"_id": 0}).to_list(length=None)
        genre_map: Dict[str, Dict[str, Any]] = {}
        for label in labels:
            for genre in label["metadata_profile"].get("genre_specialization", []):
                if genre not in genre_map:
                    genre_map[genre] = {"label_count": 0, "content_shared": 0}
                genre_map[genre]["label_count"] += 1

        breakdown = [{"genre": g, **d} for g, d in genre_map.items()]
        breakdown.sort(key=lambda x: x["label_count"], reverse=True)
        return {"success": True, "genres": breakdown}

    async def get_territory_breakdown(self) -> Dict[str, Any]:
        """Aggregate labels and revenue by territory."""
        pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": "$metadata_profile.jurisdiction", "count": {"$sum": 1}}},
        ]
        territories = []
        async for r in self.labels.aggregate(pipeline):
            territories.append({"territory": r["_id"], "label_count": r["count"]})
        territories.sort(key=lambda x: x["label_count"], reverse=True)
        return {"success": True, "territories": territories}

    async def get_content_sharing_analytics(self) -> Dict[str, Any]:
        """Analyze cross-label content sharing patterns."""
        total = await self.federated_content.count_documents({})
        by_access = {}
        pipeline = [{"$group": {"_id": "$access_level", "count": {"$sum": 1}}}]
        async for r in self.federated_content.aggregate(pipeline):
            by_access[r["_id"] or "unknown"] = r["count"]

        # Top sharers
        pipeline2 = [
            {"$group": {"_id": "$primary_label_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        top_sharers = []
        async for r in self.federated_content.aggregate(pipeline2):
            label = await self.labels.find_one({"global_id.id": r["_id"]}, projection={"_id": 0, "metadata_profile.name": 1})
            name = label["metadata_profile"]["name"] if label else r["_id"]
            top_sharers.append({"label_id": r["_id"], "name": name, "shared_count": r["count"]})

        return {
            "success": True,
            "total_shared_content": total,
            "by_access_level": by_access,
            "top_sharers": top_sharers,
        }

    async def get_dao_analytics(self) -> Dict[str, Any]:
        """DAO governance analytics."""
        total = await self.dao_proposals.count_documents({})
        by_status = {}
        pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
        async for r in self.dao_proposals.aggregate(pipeline):
            by_status[r["_id"] or "unknown"] = r["count"]

        by_type = {}
        pipeline2 = [{"$group": {"_id": "$proposal_type", "count": {"$sum": 1}}}]
        async for r in self.dao_proposals.aggregate(pipeline2):
            by_type[r["_id"] or "unknown"] = r["count"]

        return {
            "success": True,
            "total_proposals": total,
            "by_status": by_status,
            "by_type": by_type,
        }

    async def seed_sample_royalties(self) -> Dict[str, Any]:
        """Seed sample royalty earnings so dashboards have data."""
        labels = await self.labels.find({"status": "active"}, projection={"_id": 0}).to_list(length=None)
        if not labels:
            return {"success": False, "error": "No labels found. Initialize labels first."}

        existing = await self.royalty_earnings.count_documents({})
        if existing > 50:
            return {"success": True, "message": "Royalty data already seeded", "count": existing}

        platforms = ["Spotify", "Apple Music", "YouTube Music", "Amazon Music", "Tidal", "Deezer", "SoundCloud", "Pandora"]
        royalty_types = ["streaming", "performance", "mechanical", "sync", "master"]
        territories = ["US", "UK", "EU", "CA", "AU", "JP"]
        now = datetime.now(timezone.utc)
        inserted = 0

        for label in labels[:20]:
            gid = label["global_id"]["id"]
            for month_offset in range(12):
                period_start = (now - timedelta(days=30 * (11 - month_offset))).replace(day=1)
                period_end = (period_start + timedelta(days=28))
                for _ in range(random.randint(2, 6)):
                    platform = random.choice(platforms)
                    rtype = random.choice(royalty_types)
                    territory = random.choice(territories)
                    amount = round(random.uniform(500, 50000), 2)
                    streams = random.randint(10000, 5000000)
                    earning = {
                        "earning_id": str(__import__("uuid").uuid4()),
                        "content_id": f"CONTENT-{__import__('uuid').uuid4().hex[:8].upper()}",
                        "source": {
                            "source_id": f"SRC-{__import__('uuid').uuid4().hex[:6]}",
                            "source_name": platform,
                            "source_type": rtype,
                            "platform": platform,
                            "territory": territory,
                            "currency": "USD",
                        },
                        "royalty_type": rtype,
                        "gross_amount": amount,
                        "currency": "USD",
                        "period_start": period_start.strftime("%Y-%m-%d"),
                        "period_end": period_end.strftime("%Y-%m-%d"),
                        "usage_data": {"streams": streams, "downloads": random.randint(100, 10000)},
                        "label_splits": {gid: round(amount * 0.7, 2)},
                        "creator_splits": {},
                        "processed": True,
                        "distributed": month_offset < 10,
                        "processing_date": now.isoformat(),
                        "created_at": period_start.isoformat(),
                    }
                    await self.royalty_earnings.insert_one(earning)
                    inserted += 1

        return {"success": True, "message": f"Seeded {inserted} royalty earnings across {min(len(labels), 20)} labels"}
