"""
Anomaly Detection Service — Monitors platform metrics and content performance
for abnormal spikes or drops using statistical analysis (z-score, moving averages).
Creates alert records when anomalies are detected.
"""

import math
import logging
from datetime import datetime, timezone, timedelta
from config.database import db

logger = logging.getLogger(__name__)

ANOMALY_COLLECTION = "anomaly_alerts"
METRICS_HISTORY = "metrics_history"

# Z-score threshold for anomaly detection
Z_THRESHOLD = 2.0
MIN_DATA_POINTS = 5


def _z_score(value: float, mean: float, std: float) -> float:
    if std == 0:
        return 0.0
    return (value - mean) / std


def _mean(values: list) -> float:
    return sum(values) / max(len(values), 1)


def _std_dev(values: list, mean_val: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def _detect_anomalies_in_series(data_points: list, metric_name: str) -> list:
    """Detect anomalies in a time series using z-score method."""
    if len(data_points) < MIN_DATA_POINTS:
        return []

    values = [p["value"] for p in data_points]
    mean_val = _mean(values[:-1])  # exclude latest for baseline
    std_val = _std_dev(values[:-1], mean_val)
    latest = values[-1]
    z = _z_score(latest, mean_val, std_val)

    anomalies = []
    if abs(z) >= Z_THRESHOLD:
        direction = "spike" if z > 0 else "drop"
        change_pct = ((latest - mean_val) / max(abs(mean_val), 0.01)) * 100
        anomalies.append({
            "metric": metric_name,
            "direction": direction,
            "z_score": round(z, 2),
            "current_value": latest,
            "baseline_mean": round(mean_val, 2),
            "baseline_std": round(std_val, 2),
            "change_pct": round(change_pct, 1),
            "timestamp": data_points[-1].get("date", datetime.now(timezone.utc).isoformat()),
        })
    return anomalies


async def record_metric_snapshot(user_id: str, platform_id: str, metrics: dict):
    """Store a metrics snapshot for trend analysis."""
    doc = {
        "user_id": user_id,
        "platform_id": platform_id,
        "metrics": metrics,
        "date": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[METRICS_HISTORY].insert_one(doc)


async def run_anomaly_detection(user_id: str) -> list:
    """
    Run anomaly detection across all platforms and metrics for a user.
    Returns list of detected anomalies.
    """
    now = datetime.now(timezone.utc)
    lookback = now - timedelta(days=30)
    lookback_str = lookback.isoformat()

    # Gather metric history
    history = []
    async for doc in db[METRICS_HISTORY].find(
        {"user_id": user_id, "date": {"$gte": lookback_str}},
        {"_id": 0}
    ).sort("date", 1):
        history.append(doc)

    if not history:
        # Generate synthetic history from platform credentials for demo
        await _seed_metric_history(user_id)
        async for doc in db[METRICS_HISTORY].find(
            {"user_id": user_id}, {"_id": 0}
        ).sort("date", 1):
            history.append(doc)

    # Group by platform + metric
    platform_series = {}
    for h in history:
        pid = h["platform_id"]
        metrics = h.get("metrics", {})
        date = h["date"]
        for metric_key, value in metrics.items():
            if isinstance(value, (int, float)):
                key = f"{pid}_{metric_key}"
                if key not in platform_series:
                    platform_series[key] = {"platform_id": pid, "metric": metric_key, "points": []}
                platform_series[key]["points"].append({"date": date, "value": value})

    # Detect anomalies
    all_anomalies = []
    for key, series in platform_series.items():
        detected = _detect_anomalies_in_series(series["points"], series["metric"])
        for a in detected:
            a["platform_id"] = series["platform_id"]
            a["user_id"] = user_id
            all_anomalies.append(a)

    # Store new alerts
    for anomaly in all_anomalies:
        existing = await db[ANOMALY_COLLECTION].find_one({
            "user_id": user_id,
            "platform_id": anomaly["platform_id"],
            "metric": anomaly["metric"],
            "direction": anomaly["direction"],
            "dismissed": {"$ne": True},
        }, {"_id": 0})
        if not existing:
            anomaly["created_at"] = datetime.now(timezone.utc).isoformat()
            anomaly["dismissed"] = False
            anomaly["severity"] = "critical" if abs(anomaly["z_score"]) >= 3.0 else "warning"
            await db[ANOMALY_COLLECTION].insert_one(anomaly)

    return all_anomalies


async def get_anomaly_alerts(user_id: str, include_dismissed: bool = False) -> list:
    """Get all anomaly alerts for a user."""
    query = {"user_id": user_id}
    if not include_dismissed:
        query["dismissed"] = {"$ne": True}

    alerts = []
    async for doc in db[ANOMALY_COLLECTION].find(query, {"_id": 0}).sort("created_at", -1).limit(50):
        alerts.append(doc)
    return alerts


async def dismiss_anomaly(user_id: str, platform_id: str, metric: str) -> bool:
    """Dismiss an anomaly alert."""
    result = await db[ANOMALY_COLLECTION].update_many(
        {"user_id": user_id, "platform_id": platform_id, "metric": metric},
        {"$set": {"dismissed": True, "dismissed_at": datetime.now(timezone.utc).isoformat()}},
    )
    return result.modified_count > 0


async def _seed_metric_history(user_id: str):
    """Seed metric history with realistic data for anomaly detection demo."""
    import random
    now = datetime.now(timezone.utc)
    platforms = [
        ("youtube", {"followers": 12400, "views": 89000, "engagement_rate": 4.2, "likes": 3200}),
        ("twitter_x", {"followers": 8900, "impressions": 45000, "engagement_rate": 2.8, "likes": 1500}),
        ("spotify", {"followers": 5600, "streams": 34000, "monthly_listeners": 12000, "saves": 890}),
        ("tiktok", {"followers": 22000, "views": 150000, "engagement_rate": 6.1, "likes": 18000}),
        ("instagram", {"followers": 15000, "reach": 67000, "engagement_rate": 3.5, "likes": 5600}),
        ("soundcloud", {"followers": 3200, "plays": 21000, "likes": 980, "reposts": 340}),
    ]

    docs = []
    for pid, base_metrics in platforms:
        for day in range(30):
            date = (now - timedelta(days=29 - day)).isoformat()
            metrics = {}
            for k, base_val in base_metrics.items():
                # Normal variation with occasional spikes
                noise = random.gauss(0, base_val * 0.05)
                # Inject anomaly on last day for some platforms
                if day == 29 and pid in ("youtube", "tiktok") and k in ("views", "engagement_rate"):
                    noise = base_val * random.choice([0.4, -0.35])
                metrics[k] = round(max(0, base_val + noise), 2)
            docs.append({
                "user_id": user_id,
                "platform_id": pid,
                "metrics": metrics,
                "date": date,
                "created_at": date,
            })

    if docs:
        await db[METRICS_HISTORY].insert_many(docs)
