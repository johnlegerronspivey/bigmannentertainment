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
        """Inject tenant_id into a MongoDB query if provided.
        Strict mode: only matches documents with the exact tenant_id."""
        if tenant_id:
            query["tenant_id"] = tenant_id
        return query

    # ── Configuration ────────────────────────────────────────

    def _config_key(self, tenant_id: Optional[str] = None) -> str:
        if tenant_id:
            return f"ticketing_config:{tenant_id}"
        return "ticketing_config"

    async def get_config(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        doc = await self.config_col.find_one({"_id": self._config_key(tenant_id)})
        if not doc:
            # Fallback to global config for backward compat
            if tenant_id:
                doc = await self.config_col.find_one({"_id": "ticketing_config"})
            if not doc:
                return {"provider": "", "configured": False, "simulation_mode": True, "settings": {}, "tenant_id": tenant_id or ""}
        doc.pop("_id", None)
        return doc

    async def get_config_masked(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Return config with sensitive fields masked for API responses."""
        config = await self.get_config(tenant_id)
        masked_settings = {}
        secret_fields = {"api_token", "password"}
        for k, v in config.get("settings", {}).items():
            if k in secret_fields and v:
                masked_settings[k] = "••••" + v[-4:] if len(v) > 4 else "••••"
            else:
                masked_settings[k] = v
        return {**config, "settings": masked_settings}

    async def save_config(self, data: Dict[str, Any], tenant_id: Optional[str] = None) -> Dict[str, Any]:
        provider = data.get("provider", "")
        settings = data.get("settings", {})

        # Merge: if a secret field comes in masked (starts with ••••), keep existing value
        existing = await self.get_config(tenant_id)
        existing_settings = existing.get("settings", {})
        secret_fields = {"api_token", "password"}
        for f in secret_fields:
            if settings.get(f, "").startswith("••••") and existing_settings.get(f):
                settings[f] = existing_settings[f]

        simulation = not self._has_real_credentials(provider, settings)
        key = self._config_key(tenant_id)

        config = {
            "_id": key,
            "provider": provider,
            "configured": bool(provider),
            "simulation_mode": simulation,
            "settings": settings,
            "tenant_id": tenant_id or "",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.config_col.replace_one({"_id": key}, config, upsert=True)
        config.pop("_id", None)
        # Return masked version
        return await self.get_config_masked(tenant_id)

    def _has_real_credentials(self, provider: str, settings: Dict) -> bool:
        if provider == "jira":
            return all(settings.get(f) for f in ["base_url", "email", "api_token", "project_key"])
        if provider == "servicenow":
            return all(settings.get(f) for f in ["instance_url", "username", "password"])
        return False

    # ── Ticket CRUD ──────────────────────────────────────────

    async def create_ticket(self, cve_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        config = await self.get_config(tenant_id)
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

    async def sync_ticket(self, ticket_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        ticket = await self.tickets_col.find_one({"id": ticket_id})
        if not ticket:
            return None
        config = await self.get_config(tenant_id)
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

    async def bulk_create_tickets(self, severity: str = "critical", limit: int = 10, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        query = self._tenant_filter(
            {"severity": severity, "status": {"$nin": ["fixed", "verified", "dismissed", "wont_fix"]}},
            tenant_id,
        )
        cursor = self.cves_col.find(query, {"_id": 0, "id": 1}).limit(limit)
        cves = await cursor.to_list(length=limit)
        created = 0
        errors = 0
        for c in cves:
            result = await self.create_ticket(c["id"], tenant_id=tenant_id)
            if "error" in result:
                errors += 1
            else:
                created += 1
        return {"created": created, "errors": errors, "severity": severity}

    async def get_stats(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        query = self._tenant_filter({}, tenant_id)
        total = await self.tickets_col.count_documents(query)
        open_count = await self.tickets_col.count_documents(self._tenant_filter({"status": "open"}, tenant_id))
        in_progress = await self.tickets_col.count_documents(self._tenant_filter({"status": "in_progress"}, tenant_id))
        closed = await self.tickets_col.count_documents(self._tenant_filter({"status": {"$in": ["closed", "resolved"]}}, tenant_id))
        config = await self.get_config(tenant_id)
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

    # ── Real API Implementation ────────────────────────────────

    async def _real_create(self, provider: str, cve: Dict, config: Dict) -> str:
        import httpx
        settings = config.get("settings", {})
        severity = cve.get("severity", "medium")
        title = f"[{severity.upper()}] {cve.get('cve_id', '')} — {cve.get('title', 'Vulnerability')}"
        description = cve.get("description", "") or f"CVE: {cve.get('cve_id', '')}\nSeverity: {severity}\nPackage: {cve.get('affected_package', '')}"

        try:
            if provider == "jira":
                return await self._jira_create_issue(settings, title, description, severity)
            elif provider == "servicenow":
                return await self._servicenow_create_incident(settings, title, description, severity)
        except Exception as e:
            logger.error(f"Real ticket creation failed for {provider}: {e}")
            # Fallback to simulation on API error
            return self._simulate_create(provider, cve, config)
        return self._simulate_create(provider, cve, config)

    async def _jira_create_issue(self, settings: Dict, title: str, description: str, severity: str) -> str:
        import httpx
        base_url = settings.get("base_url", "").rstrip("/")
        email = settings.get("email", "")
        api_token = settings.get("api_token", "")
        project_key = settings.get("project_key", "CVE")

        priority_map = {"critical": "Highest", "high": "High", "medium": "Medium", "low": "Low", "info": "Lowest"}
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}],
                },
                "issuetype": {"name": "Bug"},
                "priority": {"name": priority_map.get(severity, "Medium")},
                "labels": ["cve-management", f"severity-{severity}"],
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{base_url}/rest/api/3/issue",
                json=payload,
                auth=(email, api_token),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("key", f"{project_key}-UNKNOWN")

    async def _servicenow_create_incident(self, settings: Dict, title: str, description: str, severity: str) -> str:
        import httpx
        instance_url = settings.get("instance_url", "").rstrip("/")
        username = settings.get("username", "")
        password = settings.get("password", "")

        urgency_map = {"critical": "1", "high": "2", "medium": "2", "low": "3", "info": "3"}
        impact_map = {"critical": "1", "high": "1", "medium": "2", "low": "3", "info": "3"}
        payload = {
            "short_description": title,
            "description": description,
            "urgency": urgency_map.get(severity, "2"),
            "impact": impact_map.get(severity, "2"),
            "category": "Software",
            "subcategory": "Security",
        }
        assignment_group = settings.get("assignment_group")
        if assignment_group:
            payload["assignment_group"] = assignment_group

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{instance_url}/api/now/table/incident",
                json=payload,
                auth=(username, password),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            result = data.get("result", {})
            return result.get("number", result.get("sys_id", "INC-UNKNOWN"))

    async def _real_sync(self, provider: str, ticket: Dict, config: Dict) -> str:
        import httpx
        settings = config.get("settings", {})
        external_key = ticket.get("external_key", "")

        try:
            if provider == "jira":
                return await self._jira_get_status(settings, external_key)
            elif provider == "servicenow":
                return await self._servicenow_get_status(settings, external_key)
        except Exception as e:
            logger.error(f"Real ticket sync failed for {provider}/{external_key}: {e}")
        return ticket.get("status", "open")

    async def _jira_get_status(self, settings: Dict, issue_key: str) -> str:
        import httpx
        base_url = settings.get("base_url", "").rstrip("/")
        email = settings.get("email", "")
        api_token = settings.get("api_token", "")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{base_url}/rest/api/3/issue/{issue_key}?fields=status",
                auth=(email, api_token),
            )
            resp.raise_for_status()
            data = resp.json()
            jira_status = data.get("fields", {}).get("status", {}).get("name", "")
            return STATUS_MAP_JIRA.get(jira_status, "open")

    async def _servicenow_get_status(self, settings: Dict, incident_number: str) -> str:
        import httpx
        instance_url = settings.get("instance_url", "").rstrip("/")
        username = settings.get("username", "")
        password = settings.get("password", "")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{instance_url}/api/now/table/incident?sysparm_query=number={incident_number}&sysparm_fields=state",
                auth=(username, password),
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("result", [])
            if results:
                state = str(results[0].get("state", "1"))
                state_map = {"1": "open", "2": "in_progress", "3": "on_hold", "6": "resolved", "7": "closed"}
                return state_map.get(state, "open")
        return "open"

    async def test_connection(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        config = await self.get_config(tenant_id)
        provider = config.get("provider")
        if not provider:
            return {"success": False, "message": "No ticketing provider configured"}

        if config.get("simulation_mode"):
            return {
                "success": True,
                "simulation": True,
                "message": f"{PROVIDERS.get(provider, {}).get('name', provider)} connection simulated — configure real credentials for live integration",
            }

        # Real connection test
        import httpx
        settings = config.get("settings", {})
        try:
            if provider == "jira":
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        f"{settings.get('base_url', '').rstrip('/')}/rest/api/3/myself",
                        auth=(settings.get("email", ""), settings.get("api_token", "")),
                    )
                    if resp.status_code == 200:
                        user_data = resp.json()
                        return {"success": True, "simulation": False, "message": f"Connected to Jira as {user_data.get('displayName', user_data.get('emailAddress', 'unknown'))}"}
                    return {"success": False, "simulation": False, "message": f"Jira auth failed: HTTP {resp.status_code}"}
            elif provider == "servicenow":
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        f"{settings.get('instance_url', '').rstrip('/')}/api/now/table/incident?sysparm_limit=1",
                        auth=(settings.get("username", ""), settings.get("password", "")),
                        headers={"Accept": "application/json"},
                    )
                    if resp.status_code == 200:
                        return {"success": True, "simulation": False, "message": "Connected to ServiceNow successfully"}
                    return {"success": False, "simulation": False, "message": f"ServiceNow auth failed: HTTP {resp.status_code}"}
        except httpx.ConnectError:
            return {"success": False, "simulation": False, "message": f"Cannot reach {provider} server — check URL"}
        except Exception as e:
            return {"success": False, "simulation": False, "message": f"Connection error: {str(e)}"}

        return {"success": False, "simulation": False, "message": f"Connected to {provider}"}
