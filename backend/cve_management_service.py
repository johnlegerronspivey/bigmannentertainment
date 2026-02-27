"""
CVE Management Service - Central CVE Brain with SBOM, Lifecycle Tracking, Severity Policies & Audit Trail
Phase 1 of the Enterprise CVE Management Platform
"""

import asyncio
import json
import logging
import subprocess
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger("cve_management_service")

_service_instance = None


def get_cve_management_service():
    global _service_instance
    if _service_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _service_instance = CVEManagementService(db)
    return _service_instance


def initialize_cve_management(db):
    global _service_instance
    _service_instance = CVEManagementService(db)
    return _service_instance


# ─── Constants ─────────────────────────────────────────────────

CVE_STATES = ["detected", "triaged", "in_progress", "fixed", "verified", "dismissed", "wont_fix"]
SEVERITY_LEVELS = ["critical", "high", "medium", "low", "info"]
DEFAULT_POLICIES = {
    "critical": {"sla_hours": 24, "auto_block_deploy": True, "auto_create_pr": True},
    "high": {"sla_hours": 72, "auto_block_deploy": True, "auto_create_pr": False},
    "medium": {"sla_hours": 336, "auto_block_deploy": False, "auto_create_pr": False},
    "low": {"sla_hours": 720, "auto_block_deploy": False, "auto_create_pr": False},
    "info": {"sla_hours": 0, "auto_block_deploy": False, "auto_create_pr": False},
}


class CVEManagementService:
    def __init__(self, db):
        self.db = db
        self.cves_col = db["cve_entries"]
        self.services_col = db["cve_services"]
        self.sbom_col = db["cve_sbom_records"]
        self.policies_col = db["cve_severity_policies"]
        self.audit_col = db["cve_audit_trail"]

    # ═══════════════════════════════════════════════════════════
    # DASHBOARD
    # ═══════════════════════════════════════════════════════════

    async def get_dashboard(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        base_q = self._tenant_filter({}, tenant_id)
        open_q = self._tenant_filter({"status": {"$in": ["detected", "triaged", "in_progress"]}}, tenant_id)
        total_cves = await self.cves_col.count_documents(base_q)
        open_cves = await self.cves_col.count_documents(open_q)
        fixed_cves = await self.cves_col.count_documents(self._tenant_filter({"status": "fixed"}, tenant_id))
        verified_cves = await self.cves_col.count_documents(self._tenant_filter({"status": "verified"}, tenant_id))
        dismissed_cves = await self.cves_col.count_documents(self._tenant_filter({"status": {"$in": ["dismissed", "wont_fix"]}}, tenant_id))

        severity_breakdown = {}
        for sev in SEVERITY_LEVELS:
            severity_breakdown[sev] = await self.cves_col.count_documents(
                self._tenant_filter({"severity": sev, "status": {"$in": ["detected", "triaged", "in_progress"]}}, tenant_id)
            )

        total_services = await self.services_col.count_documents(self._tenant_filter({}, tenant_id))
        total_sboms = await self.sbom_col.count_documents(self._tenant_filter({}, tenant_id))

        recent_cves = []
        cursor = self.cves_col.find(self._tenant_filter({}, tenant_id), {"_id": 0}).sort("detected_at", -1).limit(10)
        async for doc in cursor:
            recent_cves.append(doc)

        recent_activity = []
        cursor = self.audit_col.find(self._tenant_filter({}, tenant_id), {"_id": 0}).sort("timestamp", -1).limit(10)
        async for doc in cursor:
            recent_activity.append(doc)

        policies = await self.get_severity_policies()
        overdue_cves = await self._count_overdue(policies, tenant_id)

        services_affected = await self.cves_col.distinct("affected_services", open_q)

        return {
            "total_cves": total_cves,
            "open_cves": open_cves,
            "fixed_cves": fixed_cves,
            "verified_cves": verified_cves,
            "dismissed_cves": dismissed_cves,
            "overdue_cves": overdue_cves,
            "severity_breakdown": severity_breakdown,
            "total_services": total_services,
            "total_sboms": total_sboms,
            "services_affected": len(services_affected) if services_affected else 0,
            "recent_cves": recent_cves,
            "recent_activity": recent_activity,
        }

    async def _count_overdue(self, policies: Dict, tenant_id: Optional[str] = None) -> int:
        count = 0
        now = datetime.now(timezone.utc)
        cursor = self.cves_col.find(
            self._tenant_filter({"status": {"$in": ["detected", "triaged", "in_progress"]}}, tenant_id),
            {"_id": 0}
        )
        async for cve in cursor:
            sev = cve.get("severity", "medium")
            policy = policies.get(sev, {})
            sla_hours = policy.get("sla_hours", 0)
            if sla_hours > 0:
                detected = cve.get("detected_at")
                if detected:
                    if isinstance(detected, str):
                        detected = datetime.fromisoformat(detected.replace("Z", "+00:00"))
                    deadline = detected + timedelta(hours=sla_hours)
                    if now > deadline:
                        count += 1
        return count

    # ═══════════════════════════════════════════════════════════
    # CVE ENTRIES CRUD
    # ═══════════════════════════════════════════════════════════

    def _tenant_filter(self, query: Dict, tenant_id: Optional[str] = None) -> Dict:
        """Inject tenant_id into a MongoDB query if provided.
        Strict mode: only matches documents with the exact tenant_id."""
        if tenant_id:
            query["tenant_id"] = tenant_id
        return query

    async def create_cve(self, data: Dict[str, Any], tenant_id: Optional[str] = None) -> Dict[str, Any]:
        cve_id = data.get("cve_id") or f"CVE-{datetime.now(timezone.utc).strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "id": str(uuid.uuid4()),
            "cve_id": cve_id,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "severity": data.get("severity", "medium"),
            "cvss_score": data.get("cvss_score", 0.0),
            "status": "detected",
            "affected_package": data.get("affected_package", ""),
            "affected_version": data.get("affected_version", ""),
            "fixed_version": data.get("fixed_version", ""),
            "affected_services": data.get("affected_services", []),
            "assigned_to": data.get("assigned_to", ""),
            "assigned_team": data.get("assigned_team", ""),
            "source": data.get("source", "manual"),
            "references": data.get("references", []),
            "exploitability": data.get("exploitability", "unknown"),
            "tags": data.get("tags", []),
            "tenant_id": tenant_id or "",
            "detected_at": now,
            "triaged_at": None,
            "fixed_at": None,
            "verified_at": None,
            "created_at": now,
            "updated_at": now,
        }
        await self.cves_col.insert_one({**entry})
        await self._log_audit("cve_created", cve_id, f"CVE {cve_id} detected: {entry['title']}", data={"severity": entry["severity"]})
        return entry

    async def list_cves(self, status: Optional[str] = None, severity: Optional[str] = None,
                        service: Optional[str] = None, search: Optional[str] = None,
                        limit: int = 50, skip: int = 0, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        query = {}
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity
        if service:
            query["affected_services"] = service
        if search:
            query["$or"] = [
                {"cve_id": {"$regex": search, "$options": "i"}},
                {"title": {"$regex": search, "$options": "i"}},
                {"affected_package": {"$regex": search, "$options": "i"}},
            ]
        self._tenant_filter(query, tenant_id)
        total = await self.cves_col.count_documents(query)
        cursor = self.cves_col.find(query, {"_id": 0}).sort("detected_at", -1).skip(skip).limit(limit)
        items = []
        async for doc in cursor:
            items.append(doc)
        return {"items": items, "total": total, "limit": limit, "skip": skip}

    async def get_cve(self, cve_entry_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.cves_col.find_one({"id": cve_entry_id}, {"_id": 0})
        if not doc:
            doc = await self.cves_col.find_one({"cve_id": cve_entry_id}, {"_id": 0})
        return doc

    async def update_cve_status(self, cve_entry_id: str, new_status: str, notes: str = "") -> Optional[Dict[str, Any]]:
        if new_status not in CVE_STATES:
            return None
        now = datetime.now(timezone.utc).isoformat()
        updates: Dict[str, Any] = {"status": new_status, "updated_at": now}
        if new_status == "triaged":
            updates["triaged_at"] = now
        elif new_status == "fixed":
            updates["fixed_at"] = now
        elif new_status == "verified":
            updates["verified_at"] = now

        result = await self.cves_col.find_one_and_update(
            {"id": cve_entry_id}, {"$set": updates}, return_document=True
        )
        if not result:
            result = await self.cves_col.find_one_and_update(
                {"cve_id": cve_entry_id}, {"$set": updates}, return_document=True
            )
        if result:
            cve_id = result.get("cve_id", cve_entry_id)
            await self._log_audit("status_changed", cve_id, f"Status changed to {new_status}", data={"new_status": new_status, "notes": notes})
            result.pop("_id", None)
            return result
        return None

    async def update_cve(self, cve_entry_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        data.pop("id", None)
        data.pop("_id", None)
        result = await self.cves_col.find_one_and_update(
            {"id": cve_entry_id}, {"$set": data}, return_document=True
        )
        if result:
            result.pop("_id", None)
            await self._log_audit("cve_updated", result.get("cve_id", cve_entry_id), "CVE updated", data=data)
            return result
        return None

    # ═══════════════════════════════════════════════════════════
    # CVE OWNERSHIP MODEL
    # ═══════════════════════════════════════════════════════════

    async def assign_owner(self, cve_entry_id: str, assigned_to: str, assigned_team: str, notes: str = "") -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        updates = {"assigned_to": assigned_to, "assigned_team": assigned_team, "updated_at": now}
        result = await self.cves_col.find_one_and_update(
            {"id": cve_entry_id}, {"$set": updates}, return_document=True
        )
        if not result:
            result = await self.cves_col.find_one_and_update(
                {"cve_id": cve_entry_id}, {"$set": updates}, return_document=True
            )
        if result:
            result.pop("_id", None)
            cve_id = result.get("cve_id", cve_entry_id)
            await self._log_audit(
                "owner_assigned", cve_id,
                f"Ownership assigned: {assigned_to or 'N/A'} / Team: {assigned_team or 'N/A'}",
                data={"assigned_to": assigned_to, "assigned_team": assigned_team, "notes": notes}
            )
            return result
        return None

    async def bulk_assign_owner(self, cve_ids: List[str], assigned_to: str, assigned_team: str, notes: str = "") -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        updated = 0
        failed = []
        for cve_id in cve_ids:
            result = await self.cves_col.find_one_and_update(
                {"id": cve_id}, {"$set": {"assigned_to": assigned_to, "assigned_team": assigned_team, "updated_at": now}}, return_document=True
            )
            if result:
                result.pop("_id", None)
                updated += 1
                await self._log_audit(
                    "owner_assigned", result.get("cve_id", cve_id),
                    f"Bulk ownership assigned: {assigned_to or 'N/A'} / Team: {assigned_team or 'N/A'}",
                    data={"assigned_to": assigned_to, "assigned_team": assigned_team, "bulk": True}
                )
            else:
                failed.append(cve_id)
        return {"updated": updated, "failed": failed, "total_requested": len(cve_ids)}

    async def get_available_owners(self) -> Dict[str, Any]:
        people = await self.cves_col.distinct("assigned_to", {"assigned_to": {"$ne": "", "$exists": True}})
        teams = await self.cves_col.distinct("assigned_team", {"assigned_team": {"$ne": "", "$exists": True}})
        service_owners = await self.services_col.distinct("owner", {"owner": {"$ne": "", "$exists": True}})
        service_teams = await self.services_col.distinct("team", {"team": {"$ne": "", "$exists": True}})
        all_people = sorted(set(p for p in (people + service_owners) if p))
        all_teams = sorted(set(t for t in (teams + service_teams) if t))
        unassigned_count = await self.cves_col.count_documents({
            "status": {"$in": ["detected", "triaged", "in_progress"]},
            "$or": [{"assigned_to": ""}, {"assigned_to": None}, {"assigned_to": {"$exists": False}}]
        })
        return {"people": all_people, "teams": all_teams, "unassigned_open_cves": unassigned_count}

    async def get_unassigned_cves(self, severity: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        query = {
            "status": {"$in": ["detected", "triaged", "in_progress"]},
            "$or": [{"assigned_to": ""}, {"assigned_to": None}, {"assigned_to": {"$exists": False}}]
        }
        if severity:
            query["severity"] = severity
        total = await self.cves_col.count_documents(query)
        cursor = self.cves_col.find(query, {"_id": 0}).sort("detected_at", -1).limit(limit)
        items = []
        async for doc in cursor:
            items.append(doc)
        return {"items": items, "total": total}

    # ═══════════════════════════════════════════════════════════
    # SERVICE REGISTRY
    # ═══════════════════════════════════════════════════════════

    async def create_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        service = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "repo_url": data.get("repo_url", ""),
            "owner": data.get("owner", ""),
            "team": data.get("team", ""),
            "environment": data.get("environment", "production"),
            "criticality": data.get("criticality", "medium"),
            "tech_stack": data.get("tech_stack", []),
            "tags": data.get("tags", []),
            "created_at": now,
            "updated_at": now,
        }
        await self.services_col.insert_one({**service})
        await self._log_audit("service_created", service["id"], f"Service registered: {service['name']}")
        return service

    async def list_services(self) -> List[Dict[str, Any]]:
        services = []
        cursor = self.services_col.find({}, {"_id": 0}).sort("name", 1)
        async for doc in cursor:
            open_cves = await self.cves_col.count_documents({
                "affected_services": doc["name"],
                "status": {"$in": ["detected", "triaged", "in_progress"]}
            })
            doc["open_cves"] = open_cves
            services.append(doc)
        return services

    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        return await self.services_col.find_one({"id": service_id}, {"_id": 0})

    async def update_service(self, service_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        data.pop("id", None)
        data.pop("_id", None)
        result = await self.services_col.find_one_and_update(
            {"id": service_id}, {"$set": data}, return_document=True
        )
        if result:
            result.pop("_id", None)
            await self._log_audit("service_updated", service_id, f"Service updated: {result.get('name')}")
            return result
        return None

    async def delete_service(self, service_id: str) -> bool:
        result = await self.services_col.delete_one({"id": service_id})
        if result.deleted_count:
            await self._log_audit("service_deleted", service_id, "Service removed")
            return True
        return False

    # ═══════════════════════════════════════════════════════════
    # SBOM GENERATION & MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    async def generate_sbom(self, service_name: str = "bigmann-platform", environment: str = "production") -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        sbom_id = str(uuid.uuid4())

        # Gather frontend dependencies
        frontend_deps = await self._get_frontend_deps()
        # Gather backend dependencies
        backend_deps = await self._get_backend_deps()

        all_components = frontend_deps + backend_deps
        sbom_hash = hashlib.sha256(json.dumps(all_components, sort_keys=True).encode()).hexdigest()

        sbom = {
            "id": sbom_id,
            "service_name": service_name,
            "environment": environment,
            "format": "CycloneDX-like",
            "version": "1.0",
            "total_components": len(all_components),
            "frontend_components": len(frontend_deps),
            "backend_components": len(backend_deps),
            "components": all_components,
            "hash": sbom_hash,
            "generated_at": now,
            "created_at": now,
        }

        await self.sbom_col.insert_one({**sbom})
        await self._log_audit("sbom_generated", sbom_id, f"SBOM generated for {service_name}: {len(all_components)} components")
        sbom_copy = {k: v for k, v in sbom.items() if k != "components"}
        sbom_copy["component_summary"] = {
            "frontend": len(frontend_deps),
            "backend": len(backend_deps),
            "total": len(all_components),
        }
        return sbom_copy

    async def list_sboms(self, limit: int = 20) -> List[Dict[str, Any]]:
        sboms = []
        cursor = self.sbom_col.find({}, {"_id": 0, "components": 0}).sort("generated_at", -1).limit(limit)
        async for doc in cursor:
            sboms.append(doc)
        return sboms

    async def get_sbom(self, sbom_id: str) -> Optional[Dict[str, Any]]:
        return await self.sbom_col.find_one({"id": sbom_id}, {"_id": 0})

    async def _get_frontend_deps(self) -> List[Dict[str, Any]]:
        deps = []
        try:
            pkg_path = "/app/frontend/package.json"
            if os.path.exists(pkg_path):
                with open(pkg_path) as f:
                    pkg = json.load(f)
                for name, version in pkg.get("dependencies", {}).items():
                    deps.append({
                        "name": name,
                        "version": version.lstrip("^~"),
                        "type": "npm",
                        "layer": "frontend",
                        "scope": "runtime",
                    })
                for name, version in pkg.get("devDependencies", {}).items():
                    deps.append({
                        "name": name,
                        "version": version.lstrip("^~"),
                        "type": "npm",
                        "layer": "frontend",
                        "scope": "dev",
                    })
        except Exception as e:
            logger.error(f"Failed to read frontend deps: {e}")
        return deps

    async def _get_backend_deps(self) -> List[Dict[str, Any]]:
        deps = []
        try:
            req_path = "/app/backend/requirements.txt"
            if os.path.exists(req_path):
                with open(req_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "==" in line:
                            name, version = line.split("==", 1)
                        elif ">=" in line:
                            name, version = line.split(">=", 1)
                        elif "<=" in line:
                            name, version = line.split("<=", 1)
                        else:
                            name = line
                            version = "unknown"
                        deps.append({
                            "name": name.strip(),
                            "version": version.strip(),
                            "type": "pip",
                            "layer": "backend",
                            "scope": "runtime",
                        })
        except Exception as e:
            logger.error(f"Failed to read backend deps: {e}")
        return deps

    # ═══════════════════════════════════════════════════════════
    # SEVERITY POLICIES
    # ═══════════════════════════════════════════════════════════

    async def get_severity_policies(self) -> Dict[str, Any]:
        doc = await self.policies_col.find_one({"type": "severity_policies"}, {"_id": 0})
        if not doc:
            doc = {"type": "severity_policies", "policies": DEFAULT_POLICIES}
            await self.policies_col.insert_one({**doc})
        return doc.get("policies", DEFAULT_POLICIES)

    async def update_severity_policies(self, policies: Dict[str, Any]) -> Dict[str, Any]:
        await self.policies_col.update_one(
            {"type": "severity_policies"},
            {"$set": {"policies": policies}},
            upsert=True
        )
        await self._log_audit("policies_updated", "severity_policies", "Severity policies updated", data=policies)
        return policies

    # ═══════════════════════════════════════════════════════════
    # COMPREHENSIVE SCAN
    # ═══════════════════════════════════════════════════════════

    async def run_comprehensive_scan(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        results = {"scan_id": str(uuid.uuid4()), "started_at": now, "vulnerabilities_found": [], "summary": {}}

        # Frontend scan (yarn audit)
        frontend_vulns = await self._scan_frontend()
        # Backend scan (pip-audit)
        backend_vulns = await self._scan_backend()

        all_vulns = frontend_vulns + backend_vulns
        results["vulnerabilities_found"] = all_vulns
        results["summary"] = {
            "total": len(all_vulns),
            "critical": sum(1 for v in all_vulns if v["severity"] == "critical"),
            "high": sum(1 for v in all_vulns if v["severity"] == "high"),
            "medium": sum(1 for v in all_vulns if v["severity"] == "medium"),
            "low": sum(1 for v in all_vulns if v["severity"] == "low"),
            "frontend": len(frontend_vulns),
            "backend": len(backend_vulns),
        }
        results["completed_at"] = datetime.now(timezone.utc).isoformat()

        # Auto-create CVE entries for new findings
        new_count = 0
        for vuln in all_vulns:
            existing = await self.cves_col.find_one({"cve_id": vuln.get("cve_id", ""), "affected_package": vuln["package"]})
            if not existing:
                await self.create_cve({
                    "cve_id": vuln.get("cve_id", f"SCAN-{uuid.uuid4().hex[:8].upper()}"),
                    "title": vuln.get("title", f"Vulnerability in {vuln['package']}"),
                    "description": vuln.get("description", ""),
                    "severity": vuln["severity"],
                    "cvss_score": vuln.get("cvss_score", 0.0),
                    "affected_package": vuln["package"],
                    "affected_version": vuln.get("version", ""),
                    "fixed_version": vuln.get("fixed_version", ""),
                    "source": "automated_scan",
                    "affected_services": ["bigmann-platform"],
                    "references": vuln.get("references", []),
                })
                new_count += 1

        results["new_cves_created"] = new_count
        await self._log_audit("scan_completed", results["scan_id"], f"Scan complete: {len(all_vulns)} vulns, {new_count} new CVEs")
        return results

    async def _scan_frontend(self) -> List[Dict[str, Any]]:
        vulns = []
        try:
            result = subprocess.run(
                ["yarn", "audit", "--json"],
                capture_output=True, text=True, cwd="/app/frontend", timeout=120
            )
            for line in result.stdout.split("\n"):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data.get("type") == "auditAdvisory":
                        adv = data.get("data", {}).get("advisory", {})
                        severity_map = {"info": "low", "low": "low", "moderate": "medium", "high": "high", "critical": "critical"}
                        vulns.append({
                            "package": adv.get("module_name", "unknown"),
                            "version": adv.get("findings", [{}])[0].get("version", "") if adv.get("findings") else "",
                            "severity": severity_map.get(adv.get("severity", "moderate"), "medium"),
                            "title": adv.get("title", ""),
                            "description": adv.get("overview", ""),
                            "cve_id": adv.get("cves", [""])[0] if adv.get("cves") else "",
                            "fixed_version": adv.get("patched_versions", ""),
                            "references": [adv.get("url", "")],
                            "layer": "frontend",
                        })
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.error(f"Frontend scan error: {e}")
        return vulns

    async def _scan_backend(self) -> List[Dict[str, Any]]:
        vulns = []
        try:
            result = subprocess.run(
                ["pip-audit", "--format=json", "-r", "/app/backend/requirements.txt"],
                capture_output=True, text=True, timeout=120
            )
            try:
                data = json.loads(result.stdout)
                for item in data.get("dependencies", []):
                    for vuln in item.get("vulns", []):
                        severity = "medium"
                        desc = vuln.get("description", "")
                        vid = vuln.get("id", "")
                        if "critical" in desc.lower():
                            severity = "critical"
                        elif "high" in desc.lower():
                            severity = "high"
                        vulns.append({
                            "package": item.get("name", "unknown"),
                            "version": item.get("version", ""),
                            "severity": severity,
                            "title": f"{vid}: {item.get('name', '')}",
                            "description": desc,
                            "cve_id": vid,
                            "fixed_version": vuln.get("fix_versions", [""])[0] if vuln.get("fix_versions") else "",
                            "references": [],
                            "layer": "backend",
                        })
            except json.JSONDecodeError:
                pass
        except Exception as e:
            logger.error(f"Backend scan error: {e}")
        return vulns

    # ═══════════════════════════════════════════════════════════
    # AUDIT TRAIL
    # ═══════════════════════════════════════════════════════════

    async def _log_audit(self, action: str, target_id: str, message: str, user: str = "system", data: Optional[Dict] = None):
        entry = {
            "id": str(uuid.uuid4()),
            "action": action,
            "target_id": target_id,
            "message": message,
            "user": user,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self.audit_col.insert_one({**entry})

    async def get_audit_trail(self, target_id: Optional[str] = None, action: Optional[str] = None,
                              limit: int = 50, skip: int = 0) -> Dict[str, Any]:
        query = {}
        if target_id:
            query["target_id"] = target_id
        if action:
            query["action"] = action
        total = await self.audit_col.count_documents(query)
        items = []
        cursor = self.audit_col.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit)
        async for doc in cursor:
            items.append(doc)
        return {"items": items, "total": total}

    # ═══════════════════════════════════════════════════════════
    # SEED SAMPLE DATA (for demo)
    # ═══════════════════════════════════════════════════════════

    async def seed_sample_data(self) -> Dict[str, Any]:
        existing = await self.cves_col.count_documents({})
        if existing > 0:
            return {"message": "Data already exists", "cves": existing}

        # Seed services
        services = [
            {"name": "bigmann-frontend", "description": "React frontend application", "repo_url": "https://github.com/johnlegerronspivey/bigmannentertainment", "owner": "John Spivey", "team": "Frontend", "environment": "production", "criticality": "high", "tech_stack": ["React", "Node.js", "Tailwind"]},
            {"name": "bigmann-backend", "description": "FastAPI backend service", "repo_url": "https://github.com/johnlegerronspivey/bigmannentertainment", "owner": "John Spivey", "team": "Backend", "environment": "production", "criticality": "critical", "tech_stack": ["Python", "FastAPI", "MongoDB"]},
            {"name": "bigmann-blockchain", "description": "Ethereum smart contracts & Web3", "repo_url": "https://github.com/johnlegerronspivey/bigmannentertainment", "owner": "John Spivey", "team": "Blockchain", "environment": "production", "criticality": "critical", "tech_stack": ["Solidity", "Ethereum", "Web3.js"]},
            {"name": "bigmann-aws-infra", "description": "AWS infrastructure (S3, Lambda, CloudWatch)", "repo_url": "https://github.com/johnlegerronspivey/bigmannentertainment", "owner": "John Spivey", "team": "DevOps", "environment": "production", "criticality": "high", "tech_stack": ["AWS", "Terraform", "CloudFormation"]},
        ]
        for s in services:
            await self.create_service(s)

        # Seed CVEs
        sample_cves = [
            {"cve_id": "CVE-2026-1615", "title": "jsonpath Arbitrary Code Injection", "severity": "critical", "cvss_score": 9.8, "affected_package": "jsonpath", "affected_version": "all", "fixed_version": "N/A (removed via bfj upgrade)", "status": "verified", "source": "yarn_audit", "affected_services": ["bigmann-frontend"]},
            {"cve_id": "CVE-2026-25639", "title": "Axios Prototype Pollution", "severity": "high", "cvss_score": 7.5, "affected_package": "axios", "affected_version": "<=1.13.4", "fixed_version": "1.13.5", "status": "verified", "source": "yarn_audit", "affected_services": ["bigmann-frontend"]},
            {"cve_id": "CVE-2025-43864", "title": "React Router XSS", "severity": "medium", "cvss_score": 5.3, "affected_package": "react-router-dom", "affected_version": "<6.28.2", "fixed_version": "6.28.2", "status": "fixed", "source": "yarn_audit", "affected_services": ["bigmann-frontend"]},
            {"cve_id": "CVE-2025-12816", "title": "Node-Forge RSA Signature Vulnerability", "severity": "high", "cvss_score": 7.1, "affected_package": "node-forge", "affected_version": "<1.3.2", "fixed_version": "1.3.2", "status": "verified", "source": "yarn_audit", "affected_services": ["bigmann-frontend", "bigmann-blockchain"]},
            {"cve_id": "PYSEC-2025-001", "title": "Jinja2 Sandbox Escape", "severity": "medium", "cvss_score": 6.1, "affected_package": "jinja2", "affected_version": "<3.1.6", "fixed_version": "3.1.6", "status": "fixed", "source": "pip_audit", "affected_services": ["bigmann-backend"]},
        ]
        for cve_data in sample_cves:
            status = cve_data.pop("status", "detected")
            entry = await self.create_cve(cve_data)
            if status != "detected":
                await self.update_cve_status(entry["id"], status)

        return {"message": "Sample data seeded", "services": len(services), "cves": len(sample_cves)}
