"""
Automated CVE Monitoring Service
Fetches CVEs from the NVD (National Vulnerability Database) API,
manages watch rules, detects matching vulnerabilities, and generates alerts.
"""

import httpx
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger("cve_monitor_service")

_service_instance = None

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def get_cve_monitor_service():
    global _service_instance
    if _service_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _service_instance = CVEMonitorService(db)
    return _service_instance


SEVERITY_MAP = {
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low",
    "NONE": "info",
}


class CVEMonitorService:
    def __init__(self, db):
        self.db = db
        self.feed_col = db["cve_monitor_feed"]
        self.watches_col = db["cve_monitor_watches"]
        self.alerts_col = db["cve_monitor_alerts"]
        self.refresh_col = db["cve_monitor_refreshes"]

    # ═══════════════════════════════════════════════════════════
    # NVD FEED — Fetch & Store
    # ═══════════════════════════════════════════════════════════

    async def fetch_nvd_feed(self, keyword: Optional[str] = None, days: int = 7, limit: int = 40) -> Dict[str, Any]:
        """Fetch recent CVEs from NVD API."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days)
        params = {
            "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "pubEndDate": now.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "resultsPerPage": min(limit, 100),
        }
        if keyword:
            params["keywordSearch"] = keyword

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(NVD_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.error(f"NVD API error: {e}")
            # Return cached data on failure
            return await self._get_cached_feed(keyword, limit)

        vulnerabilities = data.get("vulnerabilities", [])
        total_results = data.get("totalResults", 0)
        feed_items = []

        for item in vulnerabilities:
            cve_data = item.get("cve", {})
            cve_id = cve_data.get("id", "")
            descriptions = cve_data.get("descriptions", [])
            description = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")

            metrics = cve_data.get("metrics", {})
            cvss_score = 0.0
            severity = "medium"
            # Try CVSS v3.1 first, then v3.0, then v2.0
            for version_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                metric_list = metrics.get(version_key, [])
                if metric_list:
                    cvss_data = metric_list[0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    base_severity = metric_list[0].get("baseSeverity", "") or cvss_data.get("baseSeverity", "")
                    severity = SEVERITY_MAP.get(base_severity.upper(), "medium")
                    break

            references = [r.get("url", "") for r in cve_data.get("references", [])[:5]]
            published = cve_data.get("published", "")
            last_modified = cve_data.get("lastModified", "")

            weaknesses = cve_data.get("weaknesses", [])
            cwe_ids = []
            for w in weaknesses:
                for wd in w.get("description", []):
                    if wd.get("value", "").startswith("CWE-"):
                        cwe_ids.append(wd["value"])

            configurations = cve_data.get("configurations", [])
            affected_products = []
            for config in configurations:
                for node in config.get("nodes", []):
                    for cpe_match in node.get("cpeMatch", []):
                        criteria = cpe_match.get("criteria", "")
                        if criteria:
                            parts = criteria.split(":")
                            if len(parts) >= 5:
                                vendor = parts[3]
                                product = parts[4]
                                if vendor != "*" and product != "*":
                                    affected_products.append(f"{vendor}/{product}")

            feed_entry = {
                "cve_id": cve_id,
                "description": description[:500],
                "cvss_score": cvss_score,
                "severity": severity,
                "published": published,
                "last_modified": last_modified,
                "references": references,
                "cwe_ids": cwe_ids,
                "affected_products": list(set(affected_products))[:10],
                "source": "NVD",
                "fetched_at": now.isoformat(),
            }
            feed_items.append(feed_entry)

            # Upsert into cache
            await self.feed_col.update_one(
                {"cve_id": cve_id},
                {"$set": feed_entry},
                upsert=True,
            )

        # Log refresh
        await self.refresh_col.insert_one({
            "id": str(uuid.uuid4()),
            "keyword": keyword or "recent",
            "results_count": len(feed_items),
            "total_available": total_results,
            "timestamp": now.isoformat(),
        })

        # Check watches after fetching
        match_count = await self._check_watches_against_feed(feed_items)

        return {
            "items": feed_items,
            "total_results": total_results,
            "fetched": len(feed_items),
            "new_alerts": match_count,
            "source": "NVD",
            "timestamp": now.isoformat(),
        }

    async def _get_cached_feed(self, keyword: Optional[str] = None, limit: int = 40) -> Dict[str, Any]:
        """Return cached feed data when NVD is unreachable."""
        query = {}
        if keyword:
            query["$or"] = [
                {"cve_id": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
            ]
        items = []
        cursor = self.feed_col.find(query, {"_id": 0}).sort("published", -1).limit(limit)
        async for doc in cursor:
            items.append(doc)
        return {
            "items": items,
            "total_results": len(items),
            "fetched": len(items),
            "new_alerts": 0,
            "source": "cache",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def get_feed(self, severity: Optional[str] = None, search: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get cached feed with optional filters."""
        query = {}
        if severity:
            query["severity"] = severity
        if search:
            query["$or"] = [
                {"cve_id": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]
        total = await self.feed_col.count_documents(query)
        items = []
        cursor = self.feed_col.find(query, {"_id": 0}).sort("published", -1).limit(limit)
        async for doc in cursor:
            items.append(doc)
        return {"items": items, "total": total}

    # ═══════════════════════════════════════════════════════════
    # WATCH RULES
    # ═══════════════════════════════════════════════════════════

    async def create_watch(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        watch = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "keyword": data.get("keyword", ""),
            "watch_type": data.get("watch_type", "keyword"),  # keyword, package, vendor
            "severity_filter": data.get("severity_filter", "all"),  # all, critical, high, medium
            "enabled": True,
            "alerts_count": 0,
            "last_checked": None,
            "created_at": now,
            "updated_at": now,
        }
        await self.watches_col.insert_one({**watch})
        return watch

    async def list_watches(self) -> List[Dict[str, Any]]:
        items = []
        cursor = self.watches_col.find({}, {"_id": 0}).sort("created_at", -1)
        async for doc in cursor:
            items.append(doc)
        return items

    async def toggle_watch(self, watch_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.watches_col.find_one({"id": watch_id})
        if not doc:
            return None
        new_enabled = not doc.get("enabled", True)
        await self.watches_col.update_one(
            {"id": watch_id},
            {"$set": {"enabled": new_enabled, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        doc["enabled"] = new_enabled
        doc.pop("_id", None)
        return doc

    async def delete_watch(self, watch_id: str) -> bool:
        result = await self.watches_col.delete_one({"id": watch_id})
        return result.deleted_count > 0

    async def refresh_watch(self, watch_id: str) -> Dict[str, Any]:
        """Manually refresh a single watch rule against NVD."""
        watch = await self.watches_col.find_one({"id": watch_id}, {"_id": 0})
        if not watch:
            return {"error": "Watch not found"}
        keyword = watch.get("keyword", "")
        if not keyword:
            return {"error": "Watch has no keyword"}

        result = await self.fetch_nvd_feed(keyword=keyword, days=30, limit=20)
        now = datetime.now(timezone.utc).isoformat()
        await self.watches_col.update_one(
            {"id": watch_id},
            {"$set": {"last_checked": now, "updated_at": now}}
        )
        return {
            "watch_id": watch_id,
            "keyword": keyword,
            "results": result.get("fetched", 0),
            "new_alerts": result.get("new_alerts", 0),
        }

    # ═══════════════════════════════════════════════════════════
    # ALERTS
    # ═══════════════════════════════════════════════════════════

    async def _check_watches_against_feed(self, feed_items: List[Dict]) -> int:
        """Check all enabled watches against new feed items, generate alerts."""
        watches = []
        cursor = self.watches_col.find({"enabled": True}, {"_id": 0})
        async for w in cursor:
            watches.append(w)

        alert_count = 0
        now = datetime.now(timezone.utc).isoformat()

        for item in feed_items:
            cve_id = item.get("cve_id", "")
            description = item.get("description", "").lower()
            products = [p.lower() for p in item.get("affected_products", [])]

            for watch in watches:
                keyword = watch.get("keyword", "").lower()
                if not keyword:
                    continue

                sev_filter = watch.get("severity_filter", "all")
                item_severity = item.get("severity", "medium")
                if sev_filter != "all":
                    severity_order = ["critical", "high", "medium", "low", "info"]
                    filter_idx = severity_order.index(sev_filter) if sev_filter in severity_order else 4
                    item_idx = severity_order.index(item_severity) if item_severity in severity_order else 4
                    if item_idx > filter_idx:
                        continue

                matched = False
                if keyword in cve_id.lower():
                    matched = True
                elif keyword in description:
                    matched = True
                elif any(keyword in p for p in products):
                    matched = True

                if matched:
                    existing = await self.alerts_col.find_one({"cve_id": cve_id, "watch_id": watch["id"]})
                    if not existing:
                        alert = {
                            "id": str(uuid.uuid4()),
                            "cve_id": cve_id,
                            "watch_id": watch["id"],
                            "watch_name": watch.get("name", ""),
                            "keyword": watch.get("keyword", ""),
                            "severity": item_severity,
                            "cvss_score": item.get("cvss_score", 0.0),
                            "description": item.get("description", "")[:300],
                            "status": "new",
                            "created_at": now,
                        }
                        await self.alerts_col.insert_one({**alert})
                        await self.watches_col.update_one(
                            {"id": watch["id"]},
                            {"$inc": {"alerts_count": 1}}
                        )
                        alert_count += 1

        return alert_count

    async def get_alerts(self, status: Optional[str] = None, severity: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        query = {}
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity
        total = await self.alerts_col.count_documents(query)
        items = []
        cursor = self.alerts_col.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
        async for doc in cursor:
            items.append(doc)
        new_count = await self.alerts_col.count_documents({"status": "new"})
        return {"items": items, "total": total, "new_count": new_count}

    async def acknowledge_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        result = await self.alerts_col.find_one_and_update(
            {"id": alert_id},
            {"$set": {"status": "acknowledged"}},
            return_document=True,
        )
        if result:
            result.pop("_id", None)
        return result

    async def dismiss_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        result = await self.alerts_col.find_one_and_update(
            {"id": alert_id},
            {"$set": {"status": "dismissed"}},
            return_document=True,
        )
        if result:
            result.pop("_id", None)
        return result

    async def acknowledge_all_alerts(self) -> Dict[str, Any]:
        result = await self.alerts_col.update_many(
            {"status": "new"},
            {"$set": {"status": "acknowledged"}}
        )
        return {"acknowledged": result.modified_count}

    # ═══════════════════════════════════════════════════════════
    # STATS
    # ═══════════════════════════════════════════════════════════

    async def get_stats(self) -> Dict[str, Any]:
        total_feed = await self.feed_col.count_documents({})
        total_watches = await self.watches_col.count_documents({})
        active_watches = await self.watches_col.count_documents({"enabled": True})
        total_alerts = await self.alerts_col.count_documents({})
        new_alerts = await self.alerts_col.count_documents({"status": "new"})
        acknowledged_alerts = await self.alerts_col.count_documents({"status": "acknowledged"})
        dismissed_alerts = await self.alerts_col.count_documents({"status": "dismissed"})

        severity_breakdown = {}
        for sev in ["critical", "high", "medium", "low", "info"]:
            severity_breakdown[sev] = await self.feed_col.count_documents({"severity": sev})

        last_refresh = await self.refresh_col.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])

        # Recent 7-day trend
        now = datetime.now(timezone.utc)
        daily_counts = []
        for i in range(7):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            day_end = (day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).isoformat()
            count = await self.feed_col.count_documents({
                "published": {"$gte": day_start, "$lt": day_end}
            })
            daily_counts.append({"date": day.strftime("%Y-%m-%d"), "count": count})

        daily_counts.reverse()

        return {
            "total_feed_entries": total_feed,
            "total_watches": total_watches,
            "active_watches": active_watches,
            "total_alerts": total_alerts,
            "new_alerts": new_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "dismissed_alerts": dismissed_alerts,
            "severity_breakdown": severity_breakdown,
            "last_refresh": last_refresh,
            "daily_trend": daily_counts,
        }
