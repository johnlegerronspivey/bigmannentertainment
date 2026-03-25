"""
ULN Catalog & Distribution Service
====================================
Phase A (Quick Win) - provides catalog listing and distribution status per label.
Uses placeholder/seed data that will be replaced with real data in Phase B.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from config.database import db

logger = logging.getLogger(__name__)


# ── Catalog ──────────────────────────────────────────────────────────

async def get_label_catalog(label_id: str) -> Dict[str, Any]:
    """
    Return the catalog (assets) associated with a label.
    Phase A: pulls from `label_assets` collection. If empty, returns seed data.
    """
    # Verify label exists
    label = await db.uln_labels.find_one(
        {"global_id.id": label_id},
        {"_id": 0, "global_id": 1, "metadata_profile.name": 1},
    )
    if not label:
        return {"success": False, "error": "Label not found"}

    label_name = label.get("metadata_profile", {}).get("name", "Unknown")

    # Try real data first
    assets = []
    async for doc in db.label_assets.find({"label_id": label_id}, {"_id": 0}).sort("created_at", -1):
        assets.append(doc)

    # If no real assets yet, return seed/placeholder data for demo
    if not assets:
        assets = _seed_catalog(label_id, label_name)

    return {
        "success": True,
        "label_id": label_id,
        "label_name": label_name,
        "assets": assets,
        "total_assets": len(assets),
        "is_seed_data": len(assets) > 0 and assets[0].get("seed", False),
    }


def _seed_catalog(label_id: str, label_name: str) -> List[Dict[str, Any]]:
    """Generate placeholder catalog entries for demo/Phase A."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "asset_id": f"{label_id}-ASSET-001",
            "label_id": label_id,
            "title": "Midnight Dreams (Single)",
            "type": "single",
            "artist": "Demo Artist",
            "isrc": "USRC12345678",
            "upc": "012345678901",
            "release_date": "2025-06-15",
            "genre": "Pop",
            "status": "released",
            "platforms": ["Spotify", "Apple Music", "YouTube Music"],
            "streams_total": 1250000,
            "created_at": now,
            "seed": True,
        },
        {
            "asset_id": f"{label_id}-ASSET-002",
            "label_id": label_id,
            "title": "Electric Sunrise (Album)",
            "type": "album",
            "artist": "Demo Artist",
            "isrc": "USRC12345679",
            "upc": "012345678902",
            "release_date": "2025-09-01",
            "genre": "R&B",
            "status": "released",
            "platforms": ["Spotify", "Apple Music", "Tidal", "Deezer"],
            "streams_total": 4300000,
            "created_at": now,
            "seed": True,
        },
        {
            "asset_id": f"{label_id}-ASSET-003",
            "label_id": label_id,
            "title": "City Lights (EP)",
            "type": "ep",
            "artist": "Another Artist",
            "isrc": "USRC12345680",
            "upc": "012345678903",
            "release_date": "2026-01-10",
            "genre": "Hip-Hop",
            "status": "pre-release",
            "platforms": ["Spotify", "Apple Music"],
            "streams_total": 0,
            "created_at": now,
            "seed": True,
        },
    ]


# ── Distribution Status ─────────────────────────────────────────────

async def get_label_distribution_status(label_id: str) -> Dict[str, Any]:
    """
    Return distribution status for a label across endpoints/DSPs.
    Phase A: pulls from `label_distribution_status` collection.
    Falls back to seed data.
    """
    label = await db.uln_labels.find_one(
        {"global_id.id": label_id},
        {"_id": 0, "global_id": 1, "metadata_profile.name": 1},
    )
    if not label:
        return {"success": False, "error": "Label not found"}

    label_name = label.get("metadata_profile", {}).get("name", "Unknown")

    # Try real data
    endpoints = []
    async for doc in db.label_distribution_status.find({"label_id": label_id}, {"_id": 0}):
        endpoints.append(doc)

    if not endpoints:
        endpoints = _seed_distribution(label_id)

    # Aggregate summary
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
        "is_seed_data": len(endpoints) > 0 and endpoints[0].get("seed", False),
    }


def _seed_distribution(label_id: str) -> List[Dict[str, Any]]:
    """Generate placeholder distribution endpoint statuses."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {"endpoint_id": f"{label_id}-DSP-001", "label_id": label_id, "platform": "Spotify", "status": "live", "last_delivery": now, "assets_delivered": 3, "errors": 0, "seed": True},
        {"endpoint_id": f"{label_id}-DSP-002", "label_id": label_id, "platform": "Apple Music", "status": "live", "last_delivery": now, "assets_delivered": 3, "errors": 0, "seed": True},
        {"endpoint_id": f"{label_id}-DSP-003", "label_id": label_id, "platform": "YouTube Music", "status": "live", "last_delivery": now, "assets_delivered": 2, "errors": 0, "seed": True},
        {"endpoint_id": f"{label_id}-DSP-004", "label_id": label_id, "platform": "Tidal", "status": "pending", "last_delivery": None, "assets_delivered": 0, "errors": 0, "seed": True},
        {"endpoint_id": f"{label_id}-DSP-005", "label_id": label_id, "platform": "Deezer", "status": "live", "last_delivery": now, "assets_delivered": 2, "errors": 0, "seed": True},
        {"endpoint_id": f"{label_id}-DSP-006", "label_id": label_id, "platform": "Amazon Music", "status": "error", "last_delivery": None, "assets_delivered": 0, "errors": 1, "error_message": "Authentication expired", "seed": True},
    ]


# ── Audit Snapshot ───────────────────────────────────────────────────

async def generate_audit_snapshot(label_id: str, user_id: str) -> Dict[str, Any]:
    """
    Generate a comprehensive JSON snapshot of a label's current state
    for audit / compliance purposes.
    """
    label = await db.uln_labels.find_one({"global_id.id": label_id}, {"_id": 0})
    if not label:
        return {"success": False, "error": "Label not found"}

    # Gather members
    members = []
    async for doc in db.label_members.find({"label_id": label_id}, {"_id": 0}):
        members.append(doc)

    # Gather catalog
    catalog_result = await get_label_catalog(label_id)
    assets = catalog_result.get("assets", [])

    # Gather distribution status
    dist_result = await get_label_distribution_status(label_id)
    endpoints = dist_result.get("endpoints", [])

    # Gather audit trail entries for this label
    audit_entries = []
    async for doc in db.uln_audit_trail.find({"resource_id": label_id}, {"_id": 0}).sort("timestamp", -1).limit(100):
        audit_entries.append(doc)

    now = datetime.now(timezone.utc).isoformat()

    snapshot = {
        "snapshot_version": "1.0",
        "generated_at": now,
        "generated_by": user_id,
        "label": label,
        "members": members,
        "member_count": len(members),
        "catalog": assets,
        "catalog_count": len(assets),
        "distribution_endpoints": endpoints,
        "distribution_summary": dist_result.get("summary", {}),
        "recent_audit_entries": audit_entries,
        "audit_entry_count": len(audit_entries),
    }

    # Log this snapshot generation in audit trail
    await db.uln_audit_trail.insert_one({
        "action_type": "audit_snapshot_generated",
        "actor_id": user_id,
        "resource_type": "label",
        "resource_id": label_id,
        "description": f"Audit snapshot generated for label {label_id}",
        "changes": {"snapshot_version": "1.0"},
        "timestamp": now,
    })

    return {"success": True, "snapshot": snapshot}
