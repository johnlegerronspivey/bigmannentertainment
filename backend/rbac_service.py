"""
Phase 6: RBAC Service for CVE Management Platform
Roles: super_admin, tenant_admin, admin, manager, analyst
"""
from datetime import datetime, timezone
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

# Role hierarchy (higher index = more privileged)
ROLE_HIERARCHY = ["analyst", "manager", "admin", "tenant_admin", "super_admin"]

# Role definitions with permissions
ROLES = {
    "super_admin": {
        "label": "Super Admin",
        "description": "Global platform admin — manages all tenants and cross-tenant operations",
        "permissions": [
            "users.view", "users.manage",
            "tenants.view", "tenants.create", "tenants.delete", "tenants.manage",
            "migration.view", "migration.run",
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
    "tenant_admin": {
        "label": "Tenant Admin",
        "description": "Organization admin — manages users and settings within own tenant",
        "permissions": [
            "users.view", "users.manage",
            "tenants.view_own",
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
    "admin": {
        "label": "Admin",
        "description": "Full CVE platform access within own tenant",
        "permissions": [
            "users.view",
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


def get_role_level(role: str) -> int:
    """Return numeric level for role hierarchy comparison."""
    try:
        return ROLE_HIERARCHY.index(role)
    except ValueError:
        return 0


def can_assign_role(actor_role: str, target_role: str) -> bool:
    """Check if actor_role is allowed to assign target_role.
    An actor can only assign roles strictly below their own level."""
    return get_role_level(actor_role) > get_role_level(target_role)


async def get_cve_user(user_id: str) -> Optional[dict]:
    if db is None:
        return None
    doc = await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})
    return doc


async def ensure_cve_user(user_id: str, email: str, full_name: str, tenant_id: str = "") -> dict:
    """Auto-provision a CVE user on first access. First user becomes super_admin."""
    if db is None:
        return {"user_id": user_id, "email": email, "full_name": full_name, "cve_role": "analyst", "is_active": True, "tenant_id": tenant_id}

    existing = await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})
    if existing:
        # Backfill tenant_id if missing
        if not existing.get("tenant_id") and tenant_id:
            await db.cve_users.update_one(
                {"user_id": user_id},
                {"$set": {"tenant_id": tenant_id}},
            )
            existing["tenant_id"] = tenant_id
        return existing

    # First user becomes super_admin
    count = await db.cve_users.count_documents({})
    role = "super_admin" if count == 0 else "analyst"

    doc = {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "cve_role": role,
        "tenant_id": tenant_id,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.cve_users.insert_one(doc)
    return await db.cve_users.find_one({"user_id": user_id}, {"_id": 0})


async def list_cve_users(tenant_id: Optional[str] = None) -> list:
    """List CVE users, optionally filtered by tenant_id."""
    if db is None:
        return []
    query = {}
    if tenant_id:
        query["tenant_id"] = tenant_id
    cursor = db.cve_users.find(query, {"_id": 0}).sort("created_at", 1)
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


async def sync_cve_users_tenant_ids() -> dict:
    """Backfill tenant_id on cve_users from the main users collection."""
    if db is None:
        return {"synced": 0}
    # Find cve_users missing tenant_id
    cursor = db.cve_users.find(
        {"$or": [{"tenant_id": {"$exists": False}}, {"tenant_id": ""}, {"tenant_id": None}]},
        {"_id": 0, "user_id": 1},
    )
    missing = await cursor.to_list(length=500)
    synced = 0
    for cve_u in missing:
        main_user = await db.users.find_one({"id": cve_u["user_id"]}, {"_id": 0, "tenant_id": 1})
        if main_user and main_user.get("tenant_id"):
            await db.cve_users.update_one(
                {"user_id": cve_u["user_id"]},
                {"$set": {"tenant_id": main_user["tenant_id"]}},
            )
            synced += 1
    return {"synced": synced, "total_missing": len(missing)}
