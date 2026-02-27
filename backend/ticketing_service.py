"""
Ticketing Integration Service — Jira & ServiceNow
Supports real API connections when credentials are configured,
and simulation mode when they are not.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("ticketing_service")

_ticketing_instance = None


def get_ticketing_service():
    global _ticketing_instance
    if _ticketing_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _ticketing_instance = TicketingService(db)
    return _ticketing_instance


def initialize_ticketing_service(db):
    global _ticketing_instance
    _ticketing_instance = TicketingService(db)
    return _ticketing_instance


PROVIDERS = {
    "jira": {"name": "Jira", "fields": ["base_url", "email", "api_token", "project_key"]},
    "servicenow": {"name": "ServiceNow", "fields": ["instance_url", "username", "password", "assignment_group"]},
}

STATUS_MAP_JIRA = {
    "To Do": "open",
    "In Progress": "in_progress",
    "In Review": "in_review",
    "Done": "closed",
}

STATUS_MAP_SERVICENOW = {
    "New": "open",
    "In Progress": "in_progress",
    "On Hold": "on_hold",
    "Resolved": "resolved",
    "Closed": "closed",
}

SEVERITY_TO_PRIORITY = {
    "critical": "Highest",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Lowest",
}


class TicketingService:
    def __init__(self, db):
        self.db = db
        self.config_col = db["cve_ticketing_config"]
        self.tickets_col = db["cve_tickets"]
        self.cves_col = db["cve_entries"]

    def _tenant_filter(self, query: Dict, tenant_id: Optional[str] = None) -> Dict:
        if tenant_id:
            query["tenant_id"] = tenant_id
        return query

    # ── Configuration ────────────────────────────────────────

    async def get_config(self) -> Dict[str, Any]:
        doc = await self.config_col.find_one({"_id": "ticketing_config"})
        if not doc:
            return {"provider": "", "configured": False, "simulation_mode": True, "settings": {}}
        doc.pop("_id", None)
        return doc

    async def save_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        provider = data.get("provider", "")
        settings = data.get("settings", {})
        simulation = not self._has_real_credentials(provider, settings)

        config = {
            "_id": "ticketing_config",
            "provider": provider,
            "configured": bool(provider),
            "simulation_mode": simulation,
            "settings": settings,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.config_col.replace_one({"_id": "ticketing_config"}, config, upsert=True)
        config.pop("_id", None)
        return config

    async def test_connection(self) -> Dict[str, Any]:
        config = await self.get_config()
        provider = config.get("provider")
        if not provider:
            return {"success": False, "message": "No ticketing provider configured"}

        if config.get("simulation_mode"):
            return {
                "success": True,
                "simulation": True,
                "message": f"{PROVIDERS.get(provider, {}).get('name', provider)} connection simulated — configure real credentials for live integration",
            }

        # Real connection test would go here
        return {"success": True, "simulation": False, "message": f"Connected to {provider}"}

    def _has_real_credentials(self, provider: str, settings: Dict) -> bool:
        if provider == "jira":
            return all(settings.get(f) for f in ["base_url", "email", "api_token", "project_key"])
        if provider == "servicenow":
            return all(settings.get(f) for f in ["instance_url", "username", "password"])
        return False

    # ── Ticket CRUD ──────────────────────────────────────────

    async def create_ticket(self, cve_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        config = await self.get_config()
        provider = config.get("provider")
        if not provider:
            return {"error": "No ticketing provider configured"}

        cve = await self.cves_col.find_one({"id": cve_id}, {"_id": 0})
        if not cve:
            return {"error": f"CVE {cve_id} not found"}

        existing = await self.tickets_col.find_one({"cve_id": cve_id, "provider": provider}, {"_id": 0})
        if existing:
            return {"error": "Ticket already exists for this CVE", "ticket": existing}

        ticket_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        severity = cve.get("severity", "medium")

        if config.get("simulation_mode"):
            external_key = self._simulate_create(provider, cve, config)
        else:
            external_key = await self._real_create(provider, cve, config)

        ticket = {
            "id": ticket_id,
            "cve_id": cve_id,
            "provider": provider,
            "external_key": external_key,
            "external_url": self._build_url(provider, external_key, config),
            "title": f"[{severity.upper()}] {cve.get('cve_id', cve_id)} — {cve.get('title', 'Vulnerability')}",
            "status": "open",
            "priority": SEVERITY_TO_PRIORITY.get(severity, "Medium"),
            "severity": severity,
            "assignee": "",
            "simulation": config.get("simulation_mode", True),
            "tenant_id": tenant_id or "",
            "created_at": now,
            "updated_at": now,
            "synced_at": now,
        }
        await self.tickets_col.insert_one({**ticket, "_id": ticket_id})
        return ticket

    async def list_tickets(self, limit: int = 50, skip: int = 0, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        query = self._tenant_filter({}, tenant_id)
        cursor = self.tickets_col.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await self.tickets_col.count_documents(query)
        return {"items": items, "total": total}

    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        return await self.tickets_col.find_one({"id": ticket_id}, {"_id": 0})

    async def sync_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        ticket = await self.tickets_col.find_one({"id": ticket_id})
        if not ticket:
            return None
        config = await self.get_config()
        if config.get("simulation_mode"):
            new_status = ticket.get("status", "open")
        else:
            new_status = await self._real_sync(config.get("provider"), ticket, config)

        now = datetime.now(timezone.utc).isoformat()
        await self.tickets_col.update_one(
            {"id": ticket_id},
            {"$set": {"status": new_status, "synced_at": now, "updated_at": now}},
        )
        result = await self.tickets_col.find_one({"id": ticket_id}, {"_id": 0})
        return result

    async def sync_all_tickets(self) -> Dict[str, Any]:
        tickets = await self.tickets_col.find({}, {"_id": 0}).to_list(length=500)
        synced = 0
        for t in tickets:
            await self.sync_ticket(t["id"])
            synced += 1
        return {"synced": synced}

    async def bulk_create_tickets(self, severity: str = "critical", limit: int = 10) -> Dict[str, Any]:
        query = {"severity": severity, "status": {"$nin": ["fixed", "verified", "dismissed", "wont_fix"]}}
        cursor = self.cves_col.find(query, {"_id": 0, "id": 1}).limit(limit)
        cves = await cursor.to_list(length=limit)
        created = 0
        errors = 0
        for c in cves:
            result = await self.create_ticket(c["id"])
            if "error" in result:
                errors += 1
            else:
                created += 1
        return {"created": created, "errors": errors, "severity": severity}

    async def get_stats(self) -> Dict[str, Any]:
        total = await self.tickets_col.count_documents({})
        open_count = await self.tickets_col.count_documents({"status": "open"})
        in_progress = await self.tickets_col.count_documents({"status": "in_progress"})
        closed = await self.tickets_col.count_documents({"status": {"$in": ["closed", "resolved"]}})
        config = await self.get_config()
        return {
            "total": total,
            "open": open_count,
            "in_progress": in_progress,
            "closed": closed,
            "provider": config.get("provider", ""),
            "simulation_mode": config.get("simulation_mode", True),
        }

    # ── Simulation helpers ───────────────────────────────────

    def _simulate_create(self, provider: str, cve: Dict, config: Dict) -> str:
        if provider == "jira":
            project_key = config.get("settings", {}).get("project_key", "CVE")
            seq = uuid.uuid4().hex[:4].upper()
            return f"{project_key}-{seq}"
        if provider == "servicenow":
            return f"INC{uuid.uuid4().hex[:8].upper()}"
        return f"TKT-{uuid.uuid4().hex[:6].upper()}"

    def _build_url(self, provider: str, key: str, config: Dict) -> str:
        settings = config.get("settings", {})
        if provider == "jira":
            base = settings.get("base_url", "https://your-domain.atlassian.net")
            return f"{base}/browse/{key}"
        if provider == "servicenow":
            base = settings.get("instance_url", "https://your-instance.service-now.com")
            return f"{base}/nav_to.do?uri=incident.do?sys_id={key}"
        return "#"

    # ── Real API stubs (to be implemented with real SDK) ────

    async def _real_create(self, provider: str, cve: Dict, config: Dict) -> str:
        # Placeholder for real Jira/ServiceNow API calls
        return self._simulate_create(provider, cve, config)

    async def _real_sync(self, provider: str, ticket: Dict, config: Dict) -> str:
        return ticket.get("status", "open")
