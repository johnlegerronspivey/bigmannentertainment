"""
Phase 6: RBAC Service for CVE Management Platform
Roles: admin, manager, analyst
"""
from datetime import datetime, timezone
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

# Role definitions with permissions
ROLES = {
    "admin": {
        "label": "Admin",
        "description": "Full platform access including user management",
        "permissions": [
            "users.view", "users.manage",
            "cves.view", "cves.create", "cves.edit", "cves.delete", "cves.assign",
            "scans.run", "scans.view",
            "remediation.view", "remediation.manage",
            "governance.view",
            "notifications.view", "notifications.manage",
            "policies.view", "policies.manage",
            "services.view", "services.manage",
            "reports.view", "reports.export",
            "audit.view",
            "sbom.view", "sbom.generate",
            "cicd.view", "cicd.manage",
        ],
    },
    "manager": {
        "label": "Manager",
        "description": "Manage CVEs, remediation, and scans",
        "permissions": [
            "cves.view", "cves.create", "cves.edit", "cves.assign",
            "scans.run", "scans.view",
            "remediation.view", "remediation.manage",
            "governance.view",
            "notifications.view", "notifications.manage",
            "policies.view",
            "services.view",
            "reports.view", "reports.export",
            "audit.view",
            "sbom.view", "sbom.generate",
            "cicd.view",
        ],
    },
    "analyst": {
        "label": "Analyst",
        "description": "View and triage CVEs, run scans",
        "permissions": [
            "cves.view", "cves.create", "cves.edit",
            "scans.run", "scans.view",
            "remediation.view",
            "governance.view",
            "notifications.view",
            "policies.view",
            "services.view",
            "reports.view",
            "audit.view",
            "sbom.view",
            "cicd.view",
        ],
    },
}

db: Optional[AsyncIOMotorDatabase] = None


def initialize_rbac_service(database: AsyncIOMotorDatabase):
    global db
    db = database
    return True


def get_role_permissions(role: str) -> list:
    return ROLES.get(role, {}).get("permissions", [])


def has_permission(role: str, permission: str) -> bool:
    return permission in get_role_permissions(role)


async def get_cve_user(user_id: str) -> Optional[dict]:
    if db is None:
        return None
    doc = await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})
    return doc


async def ensure_cve_user(user_id: str, email: str, full_name: str) -> dict:
    """Auto-provision a CVE user on first access. First user becomes admin."""
    if db is None:
        return {"user_id": user_id, "email": email, "full_name": full_name, "cve_role": "analyst", "is_active": True}

    existing = await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})
    if existing:
        return existing

    # First user becomes admin
    count = await db.cve_users.count_documents({})
    role = "admin" if count == 0 else "analyst"

    doc = {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "cve_role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.cve_users.insert_one(doc)
    # Re-fetch without _id
    return await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})


async def list_cve_users() -> list:
    if db is None:
        return []
    cursor = db.cve_users.find({}, {"_id": 0}).sort("created_at", 1)
    return await cursor.to_list(length=500)


async def update_cve_user_role(user_id: str, new_role: str) -> Optional[dict]:
    if new_role not in ROLES:
        return None
    if db is None:
        return None
    await db.cve_users.update_one(
        {"user_id": user_id},
        {"$set": {"cve_role": new_role, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})


async def update_cve_user_status(user_id: str, is_active: bool) -> Optional[dict]:
    if db is None:
        return None
    await db.cve_users.update_one(
        {"user_id": user_id},
        {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})
