"""
ULN Governance & Disputes Service
===================================
Phase C — CRUD for label_governance and label_disputes collections.
Hooks into label IDs and generates audit trail entries.
"""

import logging
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config.database import db

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def _verify_label(label_id: str) -> Optional[Dict[str, Any]]:
    label = await db.uln_labels.find_one(
        {"global_id.id": label_id},
        {"_id": 0, "global_id": 1, "metadata_profile.name": 1},
    )
    return label


async def _write_audit(label_id: str, user_id: str, action: str, description: str, changes: Dict[str, Any] = None):
    await db.uln_audit_trail.insert_one({
        "action_type": action,
        "actor_id": user_id,
        "resource_type": "label",
        "resource_id": label_id,
        "description": description,
        "changes": changes or {},
        "timestamp": _now_iso(),
    })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GOVERNANCE RULES (label_governance)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VALID_RULE_TYPES = ["voting", "content_approval", "financial", "distribution", "membership"]
VALID_ENFORCEMENT = ["automatic", "manual"]
VALID_RULE_STATUS = ["active", "inactive", "draft"]


async def get_label_governance(label_id: str) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    label_name = label.get("metadata_profile", {}).get("name", "Unknown")

    rules: List[Dict] = []
    async for doc in db.label_governance.find({"label_id": label_id}, {"_id": 0}).sort("created_at", -1):
        rules.append(doc)

    by_type = {}
    for r in rules:
        t = r.get("rule_type", "other")
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "success": True,
        "label_id": label_id,
        "label_name": label_name,
        "rules": rules,
        "total_rules": len(rules),
        "active_rules": sum(1 for r in rules if r.get("status") == "active"),
        "rules_by_type": by_type,
    }


async def create_governance_rule(label_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    rule_type = data.get("rule_type", "")
    if rule_type not in VALID_RULE_TYPES:
        return {"success": False, "error": f"Invalid rule_type. Must be one of: {VALID_RULE_TYPES}"}

    now = _now_iso()
    rule_id = _gen_id("GOV")

    rule = {
        "rule_id": rule_id,
        "label_id": label_id,
        "rule_type": rule_type,
        "title": data.get("title", "Untitled Rule"),
        "description": data.get("description", ""),
        "conditions": data.get("conditions", {}),
        "enforcement": data.get("enforcement", "manual") if data.get("enforcement") in VALID_ENFORCEMENT else "manual",
        "status": data.get("status", "draft") if data.get("status") in VALID_RULE_STATUS else "draft",
        "created_by": user_id,
        "created_at": now,
        "updated_at": now,
    }

    await db.label_governance.insert_one(rule)
    saved = await db.label_governance.find_one({"rule_id": rule_id}, {"_id": 0})

    await _write_audit(label_id, user_id, "governance_rule_created",
                       f"Created governance rule '{rule['title']}' ({rule_type})",
                       {"rule_id": rule_id, "rule_type": rule_type})

    # Emit notification
    try:
        from services.uln_notification_service import emit_notification
        asyncio.ensure_future(emit_notification(
            label_id=label_id,
            notification_type="governance_rule_created",
            title="New Governance Rule",
            message=f"Rule '{rule['title']}' ({rule_type}) was created",
            severity="info",
            actor_id=user_id,
            metadata={"rule_id": rule_id, "rule_type": rule_type},
        ))
    except Exception:
        pass

    return {"success": True, "rule": saved}


async def update_governance_rule(label_id: str, rule_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    allowed = ["title", "description", "conditions", "enforcement", "status", "rule_type"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return {"success": False, "error": "No valid fields to update"}

    if "rule_type" in updates and updates["rule_type"] not in VALID_RULE_TYPES:
        return {"success": False, "error": f"Invalid rule_type. Must be one of: {VALID_RULE_TYPES}"}
    if "enforcement" in updates and updates["enforcement"] not in VALID_ENFORCEMENT:
        return {"success": False, "error": f"Invalid enforcement. Must be one of: {VALID_ENFORCEMENT}"}
    if "status" in updates and updates["status"] not in VALID_RULE_STATUS:
        return {"success": False, "error": f"Invalid status. Must be one of: {VALID_RULE_STATUS}"}

    updates["updated_at"] = _now_iso()
    result = await db.label_governance.update_one(
        {"rule_id": rule_id, "label_id": label_id},
        {"$set": updates},
    )
    if result.matched_count == 0:
        return {"success": False, "error": "Governance rule not found"}

    saved = await db.label_governance.find_one({"rule_id": rule_id}, {"_id": 0})

    await _write_audit(label_id, user_id, "governance_rule_updated",
                       f"Updated governance rule {rule_id}",
                       {"rule_id": rule_id, "updates": list(updates.keys())})

    return {"success": True, "rule": saved}


async def delete_governance_rule(label_id: str, rule_id: str, user_id: str) -> Dict[str, Any]:
    result = await db.label_governance.delete_one({"rule_id": rule_id, "label_id": label_id})
    if result.deleted_count == 0:
        return {"success": False, "error": "Governance rule not found"}

    await _write_audit(label_id, user_id, "governance_rule_deleted",
                       f"Deleted governance rule {rule_id}",
                       {"rule_id": rule_id})

    return {"success": True, "message": "Governance rule deleted"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DISPUTES (label_disputes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VALID_DISPUTE_TYPES = ["royalty_split", "rights_ownership", "distribution", "content_takedown", "membership", "other"]
VALID_PRIORITIES = ["low", "medium", "high", "critical"]
VALID_DISPUTE_STATUS = ["open", "under_review", "resolved", "escalated", "closed"]


async def get_label_disputes(label_id: str, status_filter: str = None) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    label_name = label.get("metadata_profile", {}).get("name", "Unknown")

    query = {"label_id": label_id}
    if status_filter and status_filter in VALID_DISPUTE_STATUS:
        query["status"] = status_filter

    disputes: List[Dict] = []
    async for doc in db.label_disputes.find(query, {"_id": 0}).sort("created_at", -1):
        disputes.append(doc)

    by_status = {}
    for d in disputes:
        s = d.get("status", "open")
        by_status[s] = by_status.get(s, 0) + 1

    return {
        "success": True,
        "label_id": label_id,
        "label_name": label_name,
        "disputes": disputes,
        "total_disputes": len(disputes),
        "disputes_by_status": by_status,
    }


async def get_dispute_detail(label_id: str, dispute_id: str) -> Dict[str, Any]:
    doc = await db.label_disputes.find_one(
        {"dispute_id": dispute_id, "label_id": label_id}, {"_id": 0}
    )
    if not doc:
        return {"success": False, "error": "Dispute not found"}
    return {"success": True, "dispute": doc}


async def create_dispute(label_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    label = await _verify_label(label_id)
    if not label:
        return {"success": False, "error": "Label not found"}

    dispute_type = data.get("dispute_type", "")
    if dispute_type not in VALID_DISPUTE_TYPES:
        return {"success": False, "error": f"Invalid dispute_type. Must be one of: {VALID_DISPUTE_TYPES}"}

    priority = data.get("priority", "medium")
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    now = _now_iso()
    dispute_id = _gen_id("DISP")

    dispute = {
        "dispute_id": dispute_id,
        "label_id": label_id,
        "dispute_type": dispute_type,
        "title": data.get("title", "Untitled Dispute"),
        "description": data.get("description", ""),
        "status": "open",
        "priority": priority,
        "filed_by": user_id,
        "assigned_to": data.get("assigned_to", ""),
        "related_asset_id": data.get("related_asset_id", ""),
        "related_endpoint_id": data.get("related_endpoint_id", ""),
        "responses": [],
        "resolution": "",
        "resolved_at": None,
        "created_at": now,
        "updated_at": now,
    }

    await db.label_disputes.insert_one(dispute)
    saved = await db.label_disputes.find_one({"dispute_id": dispute_id}, {"_id": 0})

    await _write_audit(label_id, user_id, "dispute_filed",
                       f"Filed dispute '{dispute['title']}' ({dispute_type}, {priority})",
                       {"dispute_id": dispute_id, "dispute_type": dispute_type, "priority": priority})

    # Emit notification
    try:
        from services.uln_notification_service import emit_notification
        sev = "warning" if priority in ("high", "critical") else "info"
        asyncio.ensure_future(emit_notification(
            label_id=label_id,
            notification_type="dispute_filed",
            title="New Dispute Filed",
            message=f"Dispute '{dispute['title']}' ({dispute_type}) — priority: {priority}",
            severity=sev,
            actor_id=user_id,
            metadata={"dispute_id": dispute_id, "dispute_type": dispute_type, "priority": priority},
        ))
    except Exception:
        pass

    return {"success": True, "dispute": saved}


async def update_dispute(label_id: str, dispute_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    allowed = ["title", "description", "priority", "status", "assigned_to", "resolution"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return {"success": False, "error": "No valid fields to update"}

    if "priority" in updates and updates["priority"] not in VALID_PRIORITIES:
        return {"success": False, "error": f"Invalid priority. Must be one of: {VALID_PRIORITIES}"}
    if "status" in updates and updates["status"] not in VALID_DISPUTE_STATUS:
        return {"success": False, "error": f"Invalid status. Must be one of: {VALID_DISPUTE_STATUS}"}

    now = _now_iso()
    updates["updated_at"] = now

    if updates.get("status") == "resolved" and "resolution" in updates:
        updates["resolved_at"] = now

    result = await db.label_disputes.update_one(
        {"dispute_id": dispute_id, "label_id": label_id},
        {"$set": updates},
    )
    if result.matched_count == 0:
        return {"success": False, "error": "Dispute not found"}

    saved = await db.label_disputes.find_one({"dispute_id": dispute_id}, {"_id": 0})

    await _write_audit(label_id, user_id, "dispute_updated",
                       f"Updated dispute {dispute_id}",
                       {"dispute_id": dispute_id, "updates": list(updates.keys())})

    return {"success": True, "dispute": saved}


async def respond_to_dispute(label_id: str, dispute_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    existing = await db.label_disputes.find_one(
        {"dispute_id": dispute_id, "label_id": label_id}
    )
    if not existing:
        return {"success": False, "error": "Dispute not found"}

    message = data.get("message", "").strip()
    if not message:
        return {"success": False, "error": "Response message is required"}

    now = _now_iso()
    response_id = _gen_id("RESP")

    response_entry = {
        "response_id": response_id,
        "author_id": user_id,
        "author_name": data.get("author_name", ""),
        "message": message,
        "action": data.get("action", "comment"),
        "created_at": now,
    }

    update_fields = {"updated_at": now}
    new_status = data.get("new_status")
    if new_status and new_status in VALID_DISPUTE_STATUS:
        update_fields["status"] = new_status
        response_entry["action"] = "status_change"
        if new_status == "resolved":
            update_fields["resolved_at"] = now
            update_fields["resolution"] = data.get("resolution", message)

    await db.label_disputes.update_one(
        {"dispute_id": dispute_id, "label_id": label_id},
        {
            "$push": {"responses": response_entry},
            "$set": update_fields,
        },
    )

    saved = await db.label_disputes.find_one({"dispute_id": dispute_id}, {"_id": 0})

    await _write_audit(label_id, user_id, "dispute_response_added",
                       f"Responded to dispute {dispute_id}",
                       {"dispute_id": dispute_id, "action": response_entry["action"]})

    # Emit notification
    try:
        from services.uln_notification_service import emit_notification
        ntype = "dispute_resolved" if new_status == "resolved" else "dispute_updated"
        ntitle = "Dispute Resolved" if new_status == "resolved" else "Dispute Updated"
        asyncio.ensure_future(emit_notification(
            label_id=label_id,
            notification_type=ntype,
            title=ntitle,
            message=f"Dispute {dispute_id}: {message[:80]}",
            severity="success" if new_status == "resolved" else "info",
            actor_id=user_id,
            metadata={"dispute_id": dispute_id, "action": response_entry["action"]},
        ))
    except Exception:
        pass

    return {"success": True, "dispute": saved}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GOVERNANCE + DISPUTES SUMMARY (for Audit Snapshot v3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_governance_disputes_summary(label_id: str) -> Dict[str, Any]:
    governance = await get_label_governance(label_id)
    disputes = await get_label_disputes(label_id)

    return {
        "governance_rules": governance.get("total_rules", 0),
        "active_governance_rules": governance.get("active_rules", 0),
        "rules_by_type": governance.get("rules_by_type", {}),
        "total_disputes": disputes.get("total_disputes", 0),
        "disputes_by_status": disputes.get("disputes_by_status", {}),
    }
