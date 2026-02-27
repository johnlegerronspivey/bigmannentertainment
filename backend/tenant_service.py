"""
Multi-Tenant Service — Organization/Tenant Management
Provides tenant CRUD, user-tenant association, and tenant context.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("tenant_service")

_tenant_instance = None


def get_tenant_service():
    global _tenant_instance
    if _tenant_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _tenant_instance = TenantService(db)
    return _tenant_instance


def initialize_tenant_service(db):
    global _tenant_instance
    _tenant_instance = TenantService(db)
    return _tenant_instance


PLAN_LIMITS = {
    "free": {"max_users": 5, "max_cves": 100, "features": ["basic_dashboard", "manual_scan"]},
    "pro": {"max_users": 25, "max_cves": 5000, "features": ["basic_dashboard", "manual_scan", "auto_scan", "sla_tracking", "reporting"]},
    "enterprise": {"max_users": -1, "max_cves": -1, "features": ["all"]},
}


class TenantService:
    def __init__(self, db):
        self.db = db
        self.tenants_col = db["tenants"]
        self.users_col = db["users"]

    async def create_tenant(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        plan = data.get("plan", "free")
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

        tenant = {
            "id": tenant_id,
            "name": data["name"],
            "slug": data.get("slug", data["name"].lower().replace(" ", "-")),
            "plan": plan,
            "limits": limits,
            "owner_user_id": data.get("owner_user_id", ""),
            "settings": data.get("settings", {}),
            "active": True,
            "created_at": now,
            "updated_at": now,
        }
        await self.tenants_col.insert_one({**tenant, "_id": tenant_id})
        return tenant

    async def list_tenants(self, limit: int = 50, skip: int = 0) -> Dict[str, Any]:
        cursor = self.tenants_col.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await self.tenants_col.count_documents({})
        return {"items": items, "total": total}

    async def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        return await self.tenants_col.find_one({"id": tenant_id}, {"_id": 0})

    async def update_tenant(self, tenant_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        if "plan" in data:
            data["limits"] = PLAN_LIMITS.get(data["plan"], PLAN_LIMITS["free"])
        result = await self.tenants_col.find_one_and_update(
            {"id": tenant_id},
            {"$set": data},
            return_document=True,
        )
        if result:
            result.pop("_id", None)
        return result

    async def delete_tenant(self, tenant_id: str) -> bool:
        result = await self.tenants_col.delete_one({"id": tenant_id})
        if result.deleted_count > 0:
            await self.users_col.update_many(
                {"tenant_id": tenant_id},
                {"$set": {"tenant_id": ""}},
            )
            return True
        return False

    async def assign_user_to_tenant(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return {"error": "Tenant not found"}

        plan = tenant.get("plan", "free")
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        max_users = limits.get("max_users", 5)
        if max_users > 0:
            current_count = await self.users_col.count_documents({"tenant_id": tenant_id})
            if current_count >= max_users:
                return {"error": f"Tenant user limit reached ({max_users})"}

        result = await self.users_col.update_one(
            {"id": user_id},
            {"$set": {"tenant_id": tenant_id, "tenant_name": tenant["name"]}},
        )
        if result.modified_count == 0:
            return {"error": "User not found or already in this tenant"}
        return {"success": True, "user_id": user_id, "tenant_id": tenant_id}

    async def remove_user_from_tenant(self, user_id: str) -> Dict[str, Any]:
        result = await self.users_col.update_one(
            {"id": user_id},
            {"$set": {"tenant_id": "", "tenant_name": ""}},
        )
        return {"success": result.modified_count > 0}

    async def get_tenant_users(self, tenant_id: str) -> List[Dict[str, Any]]:
        cursor = self.users_col.find({"tenant_id": tenant_id}, {"_id": 0, "password_hash": 0})
        return await cursor.to_list(length=500)

    async def get_tenant_stats(self) -> Dict[str, Any]:
        total_tenants = await self.tenants_col.count_documents({})
        active_tenants = await self.tenants_col.count_documents({"active": True})
        plan_dist = {}
        for plan in PLAN_LIMITS:
            plan_dist[plan] = await self.tenants_col.count_documents({"plan": plan})
        users_with_tenant = await self.users_col.count_documents({"tenant_id": {"$exists": True, "$ne": ""}})
        users_without = await self.users_col.count_documents({"$or": [{"tenant_id": {"$exists": False}}, {"tenant_id": ""}]})
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "plan_distribution": plan_dist,
            "users_with_tenant": users_with_tenant,
            "users_without_tenant": users_without,
        }

    async def seed_default_tenant(self) -> Dict[str, Any]:
        existing = await self.tenants_col.find_one({"slug": "default"})
        if existing:
            existing.pop("_id", None)
            return {"message": "Default tenant already exists", "tenant": existing}
        tenant = await self.create_tenant({
            "name": "Default Organization",
            "slug": "default",
            "plan": "enterprise",
        })
        # Assign all existing users without a tenant
        await self.users_col.update_many(
            {"$or": [{"tenant_id": {"$exists": False}}, {"tenant_id": ""}]},
            {"$set": {"tenant_id": tenant["id"], "tenant_name": tenant["name"]}},
        )
        return {"message": "Default tenant created and users assigned", "tenant": tenant}
