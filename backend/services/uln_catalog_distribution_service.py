"""
ULN Catalog, Rights & Distribution Service
============================================
Phase B — Real CRUD for label_assets, label_rights, label_endpoints collections.
Replaces Phase A seed-data approach with persistent MongoDB storage.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config.database import db

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ASSETS (label_assets)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def _verify_label(label_id: str) -> Optional[Dict[str, Any]]:
    label = await db.uln_labels.find_one(
        {"global_id.id": label_id},
        {"_id": 0, "global_id": 1, "metadata_profile.name": 1},
    )
    return label


async def get_label_catalog(label_id: str) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    label_name = label.get("metadata_profile", {}).get("name", "Unknown")

    assets: List[Dict] = []
    async for doc in db.label_assets.find({"label_id": label_id}, {"_id": 0}).sort("created_at", -1):
        assets.append(doc)

    return {
        "success": True,
        "label_id": label_id,
        "label_name": label_name,
        "assets": assets,
        "total_assets": len(assets),
        "is_seed_data": False,
    }


async def create_asset(label_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    now = _now_iso()
    asset_id = _gen_id("ASSET")

    asset = {
        "asset_id": asset_id,
        "label_id": label_id,
        "title": data.get("title", "Untitled"),
        "type": data.get("type", "single"),
        "artist": data.get("artist", ""),
        "isrc": data.get("isrc", ""),
        "upc": data.get("upc", ""),
        "release_date": data.get("release_date", ""),
        "genre": data.get("genre", ""),
        "status": data.get("status", "draft"),
        "platforms": data.get("platforms", []),
        "streams_total": data.get("streams_total", 0),
        "created_by": user_id,
        "created_at": now,
        "updated_at": now,
    }

    await db.label_assets.insert_one(asset)
    # refetch to drop _id
    saved = await db.label_assets.find_one({"asset_id": asset_id}, {"_id": 0})
    return {"success": True, "asset": saved}


async def update_asset(label_id: str, asset_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    allowed = ["title", "type", "artist", "isrc", "upc", "release_date", "genre", "status", "platforms", "streams_total"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return {"success": False, "error": "No valid fields to update"}

    updates["updated_at"] = _now_iso()
    result = await db.label_assets.update_one(
        {"asset_id": asset_id, "label_id": label_id},
        {"$set": updates},
    )
    if result.matched_count == 0:
        return {"success": False, "error": "Asset not found"}

    saved = await db.label_assets.find_one({"asset_id": asset_id}, {"_id": 0})
    return {"success": True, "asset": saved}


async def delete_asset(label_id: str, asset_id: str) -> Dict[str, Any]:
    result = await db.label_assets.delete_one({"asset_id": asset_id, "label_id": label_id})
    if result.deleted_count == 0:
        return {"success": False, "error": "Asset not found"}
    # Also remove associated rights
    await db.label_rights.delete_many({"asset_id": asset_id, "label_id": label_id})
    return {"success": True, "message": "Asset deleted"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RIGHTS (label_rights)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_asset_rights(label_id: str, asset_id: str) -> Dict[str, Any]:
    doc = await db.label_rights.find_one(
        {"asset_id": asset_id, "label_id": label_id}, {"_id": 0}
    )
    if not doc:
        return {
            "success": True,
            "rights": None,
            "message": "No rights configured yet for this asset",
        }
    return {"success": True, "rights": doc}


async def upsert_asset_rights(label_id: str, asset_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    # verify asset exists
    asset = await db.label_assets.find_one({"asset_id": asset_id, "label_id": label_id})
    if not asset:
        return {"success": False, "error": "Asset not found"}

    now = _now_iso()
    rights_id = _gen_id("RIGHTS")

    rights_doc = {
        "rights_id": rights_id,
        "asset_id": asset_id,
        "label_id": label_id,
        "splits": data.get("splits", []),
        "territories": data.get("territories", ["GLOBAL"]),
        "ai_consent": data.get("ai_consent", False),
        "ai_consent_details": data.get("ai_consent_details", ""),
        "sponsorship_rules": data.get("sponsorship_rules", ""),
        "exclusive": data.get("exclusive", True),
        "expiry_date": data.get("expiry_date"),
        "updated_by": user_id,
        "updated_at": now,
    }

    existing = await db.label_rights.find_one({"asset_id": asset_id, "label_id": label_id})
    if existing:
        rights_doc.pop("rights_id")
        await db.label_rights.update_one(
            {"asset_id": asset_id, "label_id": label_id},
            {"$set": rights_doc},
        )
    else:
        rights_doc["created_at"] = now
        await db.label_rights.insert_one(rights_doc)

    saved = await db.label_rights.find_one({"asset_id": asset_id, "label_id": label_id}, {"_id": 0})
    return {"success": True, "rights": saved}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DISTRIBUTION ENDPOINTS (label_endpoints)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_label_distribution_status(label_id: str) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    label_name = label.get("metadata_profile", {}).get("name", "Unknown")

    endpoints: List[Dict] = []
    async for doc in db.label_endpoints.find({"label_id": label_id}, {"_id": 0}):
        endpoints.append(doc)

    total = len(endpoints)
    live_count = sum(1 for e in endpoints if e.get("status") == "live")
    pending_count = sum(1 for e in endpoints if e.get("status") == "pending")
    error_count = sum(1 for e in endpoints if e.get("status") == "error")

    return {
        "success": True,
        "label_id": label_id,
        "label_name": label_name,
        "endpoints": endpoints,
        "summary": {
            "total_endpoints": total,
            "live": live_count,
            "pending": pending_count,
            "error": error_count,
            "health_pct": round((live_count / total) * 100, 1) if total else 0,
        },
        "is_seed_data": False,
    }


async def create_endpoint(label_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    now = _now_iso()
    endpoint_id = _gen_id("EP")

    ep = {
        "endpoint_id": endpoint_id,
        "label_id": label_id,
        "platform": data.get("platform", ""),
        "status": data.get("status", "pending"),
        "endpoint_type": data.get("endpoint_type", "streaming"),
        "credentials_ref": data.get("credentials_ref", ""),
        "last_delivery": None,
        "assets_delivered": 0,
        "errors": 0,
        "error_message": "",
        "created_by": user_id,
        "created_at": now,
        "updated_at": now,
    }

    await db.label_endpoints.insert_one(ep)
    saved = await db.label_endpoints.find_one({"endpoint_id": endpoint_id}, {"_id": 0})
    return {"success": True, "endpoint": saved}


async def update_endpoint(label_id: str, endpoint_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    allowed = ["platform", "status", "endpoint_type", "credentials_ref", "last_delivery", "assets_delivered", "errors", "error_message"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return {"success": False, "error": "No valid fields to update"}

    updates["updated_at"] = _now_iso()
    result = await db.label_endpoints.update_one(
        {"endpoint_id": endpoint_id, "label_id": label_id},
        {"$set": updates},
    )
    if result.matched_count == 0:
        return {"success": False, "error": "Endpoint not found"}

    saved = await db.label_endpoints.find_one({"endpoint_id": endpoint_id}, {"_id": 0})
    return {"success": True, "endpoint": saved}


async def delete_endpoint(label_id: str, endpoint_id: str) -> Dict[str, Any]:
    result = await db.label_endpoints.delete_one({"endpoint_id": endpoint_id, "label_id": label_id})
    if result.deleted_count == 0:
        return {"success": False, "error": "Endpoint not found"}
    return {"success": True, "message": "Endpoint deleted"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  AUDIT SNAPSHOT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def generate_audit_snapshot(label_id: str, user_id: str) -> Dict[str, Any]:
    label = await db.uln_labels.find_one({"global_id.id": label_id}, {"_id": 0})
    if not label:
        return {"success": False, "error": "Label not found"}

    members: List[Dict] = []
    async for doc in db.label_members.find({"label_id": label_id}, {"_id": 0}):
        members.append(doc)

    catalog_result = await get_label_catalog(label_id)
    assets = catalog_result.get("assets", [])

    dist_result = await get_label_distribution_status(label_id)
    endpoints = dist_result.get("endpoints", [])

    # Gather rights per asset
    rights: List[Dict] = []
    async for doc in db.label_rights.find({"label_id": label_id}, {"_id": 0}):
        rights.append(doc)

    audit_entries: List[Dict] = []
    async for doc in db.uln_audit_trail.find({"resource_id": label_id}, {"_id": 0}).sort("timestamp", -1).limit(100):
        audit_entries.append(doc)

    now = _now_iso()
    snapshot = {
        "snapshot_version": "2.0",
        "generated_at": now,
        "generated_by": user_id,
        "label": label,
        "members": members,
        "member_count": len(members),
        "catalog": assets,
        "catalog_count": len(assets),
        "rights": rights,
        "rights_count": len(rights),
        "distribution_endpoints": endpoints,
        "distribution_summary": dist_result.get("summary", {}),
        "recent_audit_entries": audit_entries,
        "audit_entry_count": len(audit_entries),
    }

    await db.uln_audit_trail.insert_one({
        "action_type": "audit_snapshot_generated",
        "actor_id": user_id,
        "resource_type": "label",
        "resource_id": label_id,
        "description": f"Audit snapshot v2.0 generated for label {label_id}",
        "changes": {"snapshot_version": "2.0"},
        "timestamp": now,
    })

    return {"success": True, "snapshot": snapshot}
