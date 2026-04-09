"""
Audience Analytics Service — Demographics, geographic distribution,
and best-time-to-post analysis computed from real analytics_events data.
"""

import logging
from datetime import datetime, timezone, timedelta
from config.database import db
from collections import defaultdict

logger = logging.getLogger(__name__)

AUDIENCE_COLLECTION = "audience_analytics"
ANALYTICS_EVENTS = "analytics_events"


async def get_audience_demographics(user_id: str) -> dict:
    """Get aggregated audience demographics across all connected platforms."""
    cached = await db[AUDIENCE_COLLECTION].find_one(
        {"user_id": user_id, "type": "demographics"}, {"_id": 0}
    )
    if cached and _is_fresh(cached.get("updated_at", ""), hours=6):
        return cached.get("data", {})

    demographics = await _build_demographics(user_id)

    await db[AUDIENCE_COLLECTION].update_one(
        {"user_id": user_id, "type": "demographics"},
        {"$set": {"data": demographics, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return demographics


async def get_best_times_to_post(user_id: str) -> dict:
    """Analyze engagement patterns to recommend optimal posting times."""
    cached = await db[AUDIENCE_COLLECTION].find_one(
        {"user_id": user_id, "type": "best_times"}, {"_id": 0}
    )
    if cached and _is_fresh(cached.get("updated_at", ""), hours=6):
        return cached.get("data", {})

    best_times = await _analyze_posting_times(user_id)

    await db[AUDIENCE_COLLECTION].update_one(
        {"user_id": user_id, "type": "best_times"},
        {"$set": {"data": best_times, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return best_times


async def get_geographic_distribution(user_id: str) -> dict:
    """Get audience geographic distribution."""
    cached = await db[AUDIENCE_COLLECTION].find_one(
        {"user_id": user_id, "type": "geo"}, {"_id": 0}
    )
    if cached and _is_fresh(cached.get("updated_at", ""), hours=12):
        return cached.get("data", {})

    geo = await _build_geo_distribution(user_id)

    await db[AUDIENCE_COLLECTION].update_one(
        {"user_id": user_id, "type": "geo"},
        {"$set": {"data": geo, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return geo


def _is_fresh(updated_at: str, hours: int) -> bool:
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds() < hours * 3600
    except Exception:
        return False


async def _build_demographics(user_id: str) -> dict:
    """Build audience demographics from real analytics_events data."""
    # Count connected platforms
    connected = await db.platform_credentials.count_documents({"user_id": user_id, "status": "connected"})
    hub_connected = await db.distribution_hub_credentials.count_documents({"user_id": user_id, "connected": True})
    total_platforms = connected + hub_connected

    # Get total followers from metrics_history
    total_followers = 0
    platform_audiences = []
    seen_platforms = set()
    async for doc in db.metrics_history.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("date", -1):
        pid = doc.get("platform_id")
        followers = doc.get("metrics", {}).get("followers", 0)
        if followers and pid not in seen_platforms:
            platform_audiences.append({"platform": pid, "followers": int(followers)})
            total_followers += int(followers)
            seen_platforms.add(pid)

    # Aggregate engagement from user_content
    content_count = await db.user_content.count_documents({"user_id": user_id})
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "total_views": {"$sum": "$stats.views"},
            "total_likes": {"$sum": "$stats.likes"},
            "total_downloads": {"$sum": "$stats.downloads"},
        }},
    ]
    agg = await db.user_content.aggregate(pipeline).to_list(1)
    engagement = agg[0] if agg else {}
    engagement.pop("_id", None)

    # Compute age group distribution from analytics_events
    age_groups = await _compute_distribution(user_id, "age_group", [
        "13-17", "18-24", "25-34", "35-44", "45-54", "55+"
    ])

    # Compute gender distribution
    gender_split = await _compute_distribution(user_id, "gender", [
        "Male", "Female", "Other"
    ])
    # Rename key for frontend compatibility
    gender_split = [{"gender": g["label"], "percentage": g["percentage"]} for g in gender_split]

    # Compute device distribution
    devices = await _compute_distribution(user_id, "device_type", [
        "Mobile", "Desktop", "Tablet", "Smart TV"
    ])
    devices = [{"type": d["label"], "percentage": d["percentage"]} for d in devices]

    # Compute interest categories from content engagement by platform
    interests = await _compute_interests(user_id)

    # Count total analytics events for data quality indicator
    event_count = await db[ANALYTICS_EVENTS].count_documents({"user_id": user_id})

    return {
        "total_followers": total_followers,
        "total_platforms": total_platforms,
        "content_count": content_count,
        "engagement_summary": engagement,
        "age_groups": [{"range": a["label"], "percentage": a["percentage"]} for a in age_groups],
        "gender_split": gender_split,
        "interests": interests,
        "devices": devices,
        "platform_audiences": sorted(platform_audiences, key=lambda x: x["followers"], reverse=True)[:10],
        "data_points": event_count,
        "data_source": "analytics_events",
    }


async def _compute_distribution(user_id: str, field: str, labels: list) -> list:
    """Aggregate a field from analytics_events into percentage distribution."""
    pipeline = [
        {"$match": {"user_id": user_id, field: {"$ne": None, "$exists": True}}},
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    results = await db[ANALYTICS_EVENTS].aggregate(pipeline).to_list(50)

    if not results:
        return [{"label": label, "percentage": 0.0} for label in labels]

    total = sum(r["count"] for r in results)
    dist_map = {r["_id"]: r["count"] for r in results}

    distribution = []
    for label in labels:
        count = dist_map.get(label, 0)
        pct = round((count / total) * 100, 1) if total > 0 else 0.0
        distribution.append({"label": label, "percentage": pct})

    return distribution


async def _compute_interests(user_id: str) -> list:
    """Compute interest categories from engagement patterns by platform and content type."""
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$platform",
            "count": {"$sum": 1},
        }},
        {"$sort": {"count": -1}},
    ]
    results = await db[ANALYTICS_EVENTS].aggregate(pipeline).to_list(20)

    if not results:
        return []

    # Map platforms to interest categories
    platform_to_interest = {
        "spotify": "Hip-Hop/Rap",
        "apple_music": "R&B/Soul",
        "youtube": "Pop",
        "youtube_music": "Pop",
        "tiktok": "Electronic/Dance",
        "instagram": "Visual Arts",
        "soundcloud": "Hip-Hop/Rap",
        "twitter_x": "Cultural Commentary",
        "facebook": "Community",
    }

    total = sum(r["count"] for r in results)
    interest_map = defaultdict(float)
    for r in results:
        platform = r["_id"]
        interest = platform_to_interest.get(platform, "Other")
        interest_map[interest] += r["count"]

    interests = []
    for category, count in sorted(interest_map.items(), key=lambda x: x[1], reverse=True):
        pct = round((count / total) * 100, 1) if total > 0 else 0.0
        affinity = round(count / (total / max(len(interest_map), 1)), 1)
        interests.append({
            "category": category,
            "percentage": pct,
            "affinity_index": affinity,
        })

    return interests[:6]


async def _analyze_posting_times(user_id: str) -> dict:
    """Analyze engagement patterns to find best times to post from real data."""
    heatmap = [[0.0] * 24 for _ in range(7)]  # 7 days x 24 hours

    # Query analytics events with proper fields
    pipeline = [
        {"$match": {"user_id": user_id, "day_of_week": {"$exists": True}, "hour": {"$exists": True}}},
        {"$group": {
            "_id": {"day": "$day_of_week", "hour": "$hour"},
            "count": {"$sum": 1},
        }},
    ]
    results = await db[ANALYTICS_EVENTS].aggregate(pipeline).to_list(200)

    has_real_data = len(results) > 0

    if results:
        for r in results:
            day = r["_id"]["day"]
            hour = r["_id"]["hour"]
            if 0 <= day < 7 and 0 <= hour < 24:
                heatmap[day][hour] = r["count"]
    else:
        # Fallback: check for events with created_at datetime
        events = []
        async for doc in db[ANALYTICS_EVENTS].find(
            {"user_id": user_id, "created_at": {"$exists": True}},
            {"_id": 0, "created_at": 1}
        ).limit(2000):
            events.append(doc)

        if events:
            has_real_data = True
            for ev in events:
                ca = ev.get("created_at")
                if isinstance(ca, datetime):
                    heatmap[ca.weekday()][ca.hour] += 1.0
                elif isinstance(ca, str):
                    try:
                        dt = datetime.fromisoformat(ca.replace("Z", "+00:00"))
                        heatmap[dt.weekday()][dt.hour] += 1.0
                    except Exception:
                        pass

    # Normalize heatmap to 0-1
    max_val = max(max(row) for row in heatmap) or 1
    normalized = [[round(v / max_val, 3) for v in row] for row in heatmap]

    # Find top posting windows
    slots = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for d in range(7):
        for h in range(24):
            slots.append({"day": days[d], "day_index": d, "hour": h, "score": normalized[d][h]})

    slots.sort(key=lambda x: x["score"], reverse=True)
    top_slots = slots[:10]

    # Recommend best windows
    recommendations = []
    seen = set()
    for s in top_slots:
        if s["day"] not in seen:
            recommendations.append({
                "day": s["day"],
                "time_range": f"{s['hour']:02d}:00 - {(s['hour'] + 1) % 24:02d}:00",
                "score": round(s["score"] * 100, 1),
                "label": "Peak" if s["score"] >= 0.9 else "High" if s["score"] >= 0.7 else "Good",
            })
            seen.add(s["day"])

    return {
        "heatmap": normalized,
        "days": days,
        "hours": list(range(24)),
        "top_slots": top_slots[:10],
        "recommendations": recommendations[:5],
        "timezone": "UTC",
        "data_source": "real" if has_real_data else "insufficient_data",
    }


async def _build_geo_distribution(user_id: str) -> dict:
    """Build geographic distribution from real analytics_events data."""
    # Aggregate country data from analytics_events
    pipeline = [
        {"$match": {"user_id": user_id, "country": {"$ne": None, "$exists": True}}},
        {"$group": {
            "_id": "$country",
            "count": {"$sum": 1},
            "country_name": {"$first": "$country_name"},
        }},
        {"$sort": {"count": -1}},
    ]
    results = await db[ANALYTICS_EVENTS].aggregate(pipeline).to_list(50)

    total_events = sum(r["count"] for r in results) if results else 0

    # Get total followers for listener count scaling
    total_followers = 0
    async for doc in db.metrics_history.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("date", -1).limit(20):
        f = doc.get("metrics", {}).get("followers", 0)
        total_followers += int(f)

    total_followers = max(total_followers, 1000)

    # Country name mapping fallback
    code_to_name = {
        "US": "United States", "GB": "United Kingdom", "CA": "Canada",
        "DE": "Germany", "FR": "France", "AU": "Australia", "BR": "Brazil",
        "NG": "Nigeria", "JP": "Japan", "MX": "Mexico", "IN": "India",
        "ZA": "South Africa", "KR": "South Korea", "SE": "Sweden",
    }

    countries = []
    if results:
        for r in results:
            code = r["_id"]
            name = r.get("country_name") or code_to_name.get(code, code)
            pct = round((r["count"] / total_events) * 100, 1) if total_events > 0 else 0.0
            listeners = int(total_followers * pct / 100)
            countries.append({
                "code": code,
                "name": name,
                "percentage": pct,
                "listeners": listeners,
            })

    # US region / city breakdown
    us_cities = await _compute_us_cities(user_id, total_followers)

    return {
        "countries": countries[:15],
        "top_cities_us": us_cities,
        "total_countries": len(countries),
        "primary_market": countries[0]["name"] if countries else "Unknown",
        "primary_market_pct": countries[0]["percentage"] if countries else 0.0,
        "data_points": total_events,
        "data_source": "analytics_events",
    }


async def _compute_us_cities(user_id: str, total_followers: int) -> list:
    """Compute US city distribution from analytics_events region data."""
    pipeline = [
        {"$match": {"user_id": user_id, "country": "US", "region": {"$ne": "", "$exists": True}}},
        {"$group": {"_id": "$region", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    results = await db[ANALYTICS_EVENTS].aggregate(pipeline).to_list(10)

    if not results:
        return []

    total = sum(r["count"] for r in results)

    # Map states to representative cities
    state_to_city = {
        "Georgia": ("Atlanta", "GA"),
        "New York": ("New York", "NY"),
        "California": ("Los Angeles", "CA"),
        "Texas": ("Houston", "TX"),
        "Illinois": ("Chicago", "IL"),
        "Florida": ("Miami", "FL"),
        "Pennsylvania": ("Philadelphia", "PA"),
        "Michigan": ("Detroit", "MI"),
        "Tennessee": ("Memphis", "TN"),
        "Alabama": ("Alexander City", "AL"),
        "Ohio": ("Columbus", "OH"),
        "North Carolina": ("Charlotte", "NC"),
    }

    cities = []
    for r in results:
        state = r["_id"]
        city_info = state_to_city.get(state, (state, state[:2].upper()))
        pct = round((r["count"] / total) * 100, 1) if total > 0 else 0.0
        cities.append({
            "city": city_info[0],
            "state": city_info[1],
            "percentage": pct,
        })

    return cities
