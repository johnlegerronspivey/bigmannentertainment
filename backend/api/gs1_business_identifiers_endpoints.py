"""
GS1 Business Identifiers API
==============================
Mandatory business & GS1 identifier management for labels/companies.
Pre-populates and protects Big Mann Entertainment identifiers.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from uln_auth import get_current_user, User
from config.database import db
from utils.gs1_validators import (
    validate_business_identifiers,
    validate_gtin, validate_gln, validate_isrc, validate_upc,
    validate_gs1_company_prefix, validate_ein, validate_duns,
    validate_business_registration,
)
from utils.ownership_guard import (
    is_protected_owner,
    block_identifier_change,
    log_ownership_violation,
    PROTECTED_OWNER_USER_ID,
    PROTECTED_BUSINESS_IDENTIFIERS,
    PROTECTED_OWNER_FULL_NAME,
    PROTECTED_BUSINESS_NAME,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gs1-identifiers", tags=["GS1 Business Identifiers"])


class BusinessIdentifiersRequest(BaseModel):
    gs1_company_prefix: str = ""
    gln: str = ""
    ein: str = ""
    duns: str = ""
    business_registration_number: str = ""
    business_entity: str = ""
    business_owner: str = ""
    business_type: str = ""


class IdentifierValidateRequest(BaseModel):
    identifier_type: str
    value: str


# ── Get business identifiers for a label ──────────────────────

@router.get("/labels/{label_id}")
async def get_label_business_identifiers(
    label_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all mandatory business & GS1 identifiers for a label."""
    doc = await db.business_identifiers.find_one(
        {"label_id": label_id}, {"_id": 0}
    )
    if not doc:
        return {
            "success": True,
            "identifiers": None,
            "is_protected": False,
            "message": "No business identifiers configured for this label yet",
        }

    owner_id = doc.get("owner_user_id", "")
    return {
        "success": True,
        "identifiers": doc,
        "is_protected": is_protected_owner(user_id=owner_id),
    }


# ── Create/Update business identifiers ────────────────────────

@router.put("/labels/{label_id}")
async def upsert_label_business_identifiers(
    label_id: str,
    req: BusinessIdentifiersRequest,
    current_user: User = Depends(get_current_user),
):
    """Set or update mandatory business & GS1 identifiers for a label."""
    data = req.dict()

    # Check if existing record belongs to protected owner
    existing = await db.business_identifiers.find_one({"label_id": label_id}, {"_id": 0})
    if existing:
        owner_id = existing.get("owner_user_id", "")
        blocked = block_identifier_change(owner_id, data, actor_description=current_user.email)
        if blocked:
            await log_ownership_violation(db, current_user.id, "update_business_identifiers", {
                "label_id": label_id, "blocked": blocked,
            })
            raise HTTPException(status_code=403, detail=blocked)

    # Validate all identifiers
    errors = validate_business_identifiers(data)
    if errors:
        raise HTTPException(status_code=400, detail={"validation_errors": errors})

    now = datetime.now(timezone.utc).isoformat()
    update_doc = {
        **data,
        "label_id": label_id,
        "owner_user_id": current_user.id,
        "updated_at": now,
        "updated_by": current_user.id,
    }

    result = await db.business_identifiers.update_one(
        {"label_id": label_id},
        {"$set": update_doc, "$setOnInsert": {"created_at": now, "created_by": current_user.id}},
        upsert=True,
    )

    # Audit trail
    await db.uln_audit_trail.insert_one({
        "action_type": "business_identifiers_updated",
        "actor_id": current_user.id,
        "resource_type": "business_identifiers",
        "resource_id": label_id,
        "description": f"Business identifiers {'created' if result.upserted_id else 'updated'} for label {label_id}",
        "changes": data,
        "timestamp": now,
        "severity": "info",
    })

    return {
        "success": True,
        "message": f"Business identifiers {'created' if result.upserted_id else 'updated'} for label {label_id}",
        "identifiers": update_doc,
    }


# ── Get protected owner identifiers ───────────────────────────

@router.get("/protected-owner")
async def get_protected_owner_identifiers(
    current_user: User = Depends(get_current_user),
):
    """Get the immutable pre-populated identifiers for Big Mann Entertainment."""
    return {
        "success": True,
        "protected_owner": PROTECTED_OWNER_FULL_NAME,
        "protected_business": PROTECTED_BUSINESS_NAME,
        "identifiers": PROTECTED_BUSINESS_IDENTIFIERS,
        "protection_level": "IMMUTABLE",
    }


# ── Validate a single identifier ──────────────────────────────

@router.post("/validate")
async def validate_single_identifier(
    req: IdentifierValidateRequest,
    current_user: User = Depends(get_current_user),
):
    """Validate a single GS1 or business identifier with format & check-digit verification."""
    validators = {
        "gtin": validate_gtin,
        "upc": validate_upc,
        "gln": validate_gln,
        "isrc": validate_isrc,
        "gs1_company_prefix": validate_gs1_company_prefix,
        "ein": validate_ein,
        "duns": validate_duns,
        "business_registration_number": validate_business_registration,
    }

    fn = validators.get(req.identifier_type)
    if not fn:
        raise HTTPException(status_code=400, detail=f"Unknown identifier type: {req.identifier_type}")

    error = fn(req.value)
    return {
        "success": True,
        "identifier_type": req.identifier_type,
        "value": req.value,
        "valid": error is None,
        "error": error,
    }


# ── Compliance check: does a label have all mandatory identifiers? ─

@router.get("/labels/{label_id}/compliance")
async def check_label_identifier_compliance(
    label_id: str,
    current_user: User = Depends(get_current_user),
):
    """Check whether a label has all mandatory business & GS1 identifiers configured."""
    doc = await db.business_identifiers.find_one({"label_id": label_id}, {"_id": 0})

    required = ["gs1_company_prefix", "gln", "ein", "duns", "business_registration_number"]
    missing = []
    invalid = {}

    if not doc:
        missing = required[:]
    else:
        for field in required:
            val = doc.get(field, "").strip()
            if not val:
                missing.append(field)
            else:
                validators_map = {
                    "gs1_company_prefix": validate_gs1_company_prefix,
                    "gln": validate_gln,
                    "ein": validate_ein,
                    "duns": validate_duns,
                    "business_registration_number": validate_business_registration,
                }
                err = validators_map[field](val)
                if err:
                    invalid[field] = err

    compliant = len(missing) == 0 and len(invalid) == 0

    return {
        "success": True,
        "label_id": label_id,
        "compliant": compliant,
        "missing_identifiers": missing,
        "invalid_identifiers": invalid,
        "total_required": len(required),
        "total_present": len(required) - len(missing),
    }
