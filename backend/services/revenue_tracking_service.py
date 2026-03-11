"""
Revenue Tracking Service — Tracks revenue per platform from content distribution,
streaming royalties, ad revenue, and licensing.
"""

import logging
from datetime import datetime, timezone, timedelta
from config.database import db

logger = logging.getLogger(__name__)

REVENUE_COLLECTION = "revenue_tracking"


async def get_revenue_overview(user_id: str) -> dict:
    """Get comprehensive revenue overview with per-platform and per-source breakdowns."""
    # Aggregate from revenue tracking records
    records = []
    async for doc in db[REVENUE_COLLECTION].find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("date", -1):
        records.append(doc)

    if not records:
        await _seed_revenue_data(user_id)
        async for doc in db[REVENUE_COLLECTION].find(
            {"user_id": user_id}, {"_id": 0}
        ).sort("date", -1):
            records.append(doc)

    # Total revenue
    total = sum(r.get("amount", 0) for r in records)

    # By platform
    by_platform = {}
    for r in records:
        pid = r.get("platform_id", "unknown")
        if pid not in by_platform:
            by_platform[pid] = {"platform_id": pid, "platform_name": r.get("platform_name", pid), "total": 0, "count": 0}
        by_platform[pid]["total"] += r.get("amount", 0)
        by_platform[pid]["count"] += 1

    platform_list = sorted(by_platform.values(), key=lambda x: x["total"], reverse=True)
    for p in platform_list:
        p["total"] = round(p["total"], 2)
        p["percentage"] = round((p["total"] / max(total, 0.01)) * 100, 1)

    # By source type
    by_source = {}
    for r in records:
        src = r.get("source", "other")
        if src not in by_source:
            by_source[src] = {"source": src, "total": 0, "count": 0}
        by_source[src]["total"] += r.get("amount", 0)
        by_source[src]["count"] += 1

    source_list = sorted(by_source.values(), key=lambda x: x["total"], reverse=True)
    for s in source_list:
        s["total"] = round(s["total"], 2)
        s["percentage"] = round((s["total"] / max(total, 0.01)) * 100, 1)

    # Monthly trend (last 12 months)
    now = datetime.now(timezone.utc)
    monthly = []
    for i in range(12):
        m = now - timedelta(days=30 * (11 - i))
        month_str = m.strftime("%Y-%m")
        month_total = sum(r.get("amount", 0) for r in records if r.get("month", "") == month_str)
        monthly.append({"month": month_str, "amount": round(month_total, 2)})

    # Per-content revenue
    by_content = {}
    for r in records:
        cid = r.get("content_id")
        if cid:
            if cid not in by_content:
                by_content[cid] = {"content_id": cid, "title": r.get("content_title", "Unknown"), "total": 0}
            by_content[cid]["total"] += r.get("amount", 0)

    content_list = sorted(by_content.values(), key=lambda x: x["total"], reverse=True)[:10]
    for c in content_list:
        c["total"] = round(c["total"], 2)

    return {
        "total_revenue": round(total, 2),
        "currency": "USD",
        "by_platform": platform_list,
        "by_source": source_list,
        "monthly_trend": monthly,
        "top_earning_content": content_list,
        "total_transactions": len(records),
        "period": "Last 12 months",
    }


async def get_platform_revenue_detail(user_id: str, platform_id: str) -> dict:
    """Get detailed revenue breakdown for a specific platform."""
    records = []
    async for doc in db[REVENUE_COLLECTION].find(
        {"user_id": user_id, "platform_id": platform_id}, {"_id": 0}
    ).sort("date", -1):
        records.append(doc)

    total = sum(r.get("amount", 0) for r in records)

    by_source = {}
    for r in records:
        src = r.get("source", "other")
        by_source.setdefault(src, 0)
        by_source[src] += r.get("amount", 0)

    # Recent transactions
    recent = records[:20]

    return {
        "platform_id": platform_id,
        "total_revenue": round(total, 2),
        "by_source": {k: round(v, 2) for k, v in by_source.items()},
        "transaction_count": len(records),
        "recent_transactions": recent,
    }


async def record_revenue(user_id: str, data: dict):
    """Record a new revenue entry."""
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "platform_id": data.get("platform_id", ""),
        "platform_name": data.get("platform_name", ""),
        "content_id": data.get("content_id", ""),
        "content_title": data.get("content_title", ""),
        "source": data.get("source", "streaming"),
        "amount": float(data.get("amount", 0)),
        "currency": "USD",
        "date": now.isoformat(),
        "month": now.strftime("%Y-%m"),
        "description": data.get("description", ""),
        "created_at": now.isoformat(),
    }
    await db[REVENUE_COLLECTION].insert_one(doc)
    return {"message": "Revenue recorded"}


async def _seed_revenue_data(user_id: str):
    """Seed realistic revenue data for demo."""
    import random
    now = datetime.now(timezone.utc)

    platforms = [
        ("spotify", "Spotify", "streaming"),
        ("apple_music", "Apple Music", "streaming"),
        ("youtube", "YouTube", "ad_revenue"),
        ("youtube_music", "YouTube Music", "streaming"),
        ("tidal", "TIDAL", "streaming"),
        ("amazon_music", "Amazon Music", "streaming"),
        ("soundcloud", "SoundCloud", "streaming"),
        ("tiktok", "TikTok", "sync_licensing"),
        ("instagram", "Instagram", "ad_revenue"),
        ("deezer", "Deezer", "streaming"),
    ]

    content_items = [
        ("track_001", "Summer Vibes"),
        ("track_002", "Midnight Flow"),
        ("track_003", "City Lights"),
        ("track_004", "On My Way Up"),
        ("track_005", "Real Talk"),
        ("album_001", "The Journey (Album)"),
    ]

    docs = []
    for month_offset in range(12):
        month_date = now - timedelta(days=30 * (11 - month_offset))
        month_str = month_date.strftime("%Y-%m")
        # Growth factor — more recent months earn more
        growth = 1.0 + (month_offset * 0.08)

        for pid, pname, source in platforms:
            # Each platform generates multiple transactions per month
            num_transactions = random.randint(1, 4)
            for _ in range(num_transactions):
                content = random.choice(content_items)
                base_amount = {
                    "spotify": random.uniform(15, 180),
                    "apple_music": random.uniform(12, 120),
                    "youtube": random.uniform(25, 300),
                    "youtube_music": random.uniform(8, 60),
                    "tidal": random.uniform(5, 45),
                    "amazon_music": random.uniform(8, 70),
                    "soundcloud": random.uniform(3, 25),
                    "tiktok": random.uniform(10, 150),
                    "instagram": random.uniform(5, 80),
                    "deezer": random.uniform(3, 30),
                }.get(pid, 10)
                amount = round(base_amount * growth * random.uniform(0.7, 1.3), 2)

                day = random.randint(1, 28)
                date = month_date.replace(day=day)

                docs.append({
                    "user_id": user_id,
                    "platform_id": pid,
                    "platform_name": pname,
                    "content_id": content[0],
                    "content_title": content[1],
                    "source": source,
                    "amount": amount,
                    "currency": "USD",
                    "date": date.isoformat(),
                    "month": month_str,
                    "description": f"{source.replace('_', ' ').title()} - {pname}",
                    "created_at": date.isoformat(),
                })

    if docs:
        await db[REVENUE_COLLECTION].insert_many(docs)
        logger.info(f"Seeded {len(docs)} revenue records for user {user_id}")
