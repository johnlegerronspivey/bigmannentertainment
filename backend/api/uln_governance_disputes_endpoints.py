"""
ULN Governance & Disputes Endpoints
=====================================
Phase C — CRUD for label_governance and label_disputes.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from uln_auth import get_current_user, User
from services.uln_governance_disputes_service import (
    get_label_governance,
    create_governance_rule,
    update_governance_rule,
    delete_governance_rule,
    get_label_disputes,
    get_dispute_detail,
    create_dispute,
    update_dispute,
    respond_to_dispute,
    get_governance_disputes_summary,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uln", tags=["ULN Governance & Disputes"])


# ── Request models ─────────────────────────────────────────────


class GovernanceRuleCreateRequest(BaseModel):
    rule_type: str
    title: str
    description: str = ""
    conditions: Dict[str, Any] = Field(default_factory=dict)
    enforcement: str = "manual"
    status: str = "draft"


class GovernanceRuleUpdateRequest(BaseModel):
    rule_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    enforcement: Optional[str] = None
    status: Optional[str] = None


class DisputeCreateRequest(BaseModel):
    dispute_type: str
    title: str
    description: str = ""
    priority: str = "medium"
    assigned_to: str = ""
    related_asset_id: str = ""
    related_endpoint_id: str = ""


class DisputeUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None


class DisputeResponseRequest(BaseModel):
    message: str
    author_name: str = ""
    action: str = "comment"
    new_status: Optional[str] = None
    resolution: Optional[str] = None


# ── Governance Rules ───────────────────────────────────────────


@router.get("/labels/{label_id}/governance")
async def label_governance(label_id: str, current_user: User = Depends(get_current_user)):
    result = await get_label_governance(label_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/labels/{label_id}/governance")
async def add_governance_rule(label_id: str, req: GovernanceRuleCreateRequest, current_user: User = Depends(get_current_user)):
    result = await create_governance_rule(label_id, req.dict(), current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/labels/{label_id}/governance/{rule_id}")
async def edit_governance_rule(label_id: str, rule_id: str, req: GovernanceRuleUpdateRequest, current_user: User = Depends(get_current_user)):
    data = {k: v for k, v in req.dict().items() if v is not None}
    result = await update_governance_rule(label_id, rule_id, data, current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/labels/{label_id}/governance/{rule_id}")
async def remove_governance_rule(label_id: str, rule_id: str, current_user: User = Depends(get_current_user)):
    result = await delete_governance_rule(label_id, rule_id, current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Disputes ───────────────────────────────────────────────────


@router.get("/labels/{label_id}/disputes")
async def label_disputes(label_id: str, status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    result = await get_label_disputes(label_id, status_filter=status)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/labels/{label_id}/disputes/{dispute_id}")
async def label_dispute_detail(label_id: str, dispute_id: str, current_user: User = Depends(get_current_user)):
    result = await get_dispute_detail(label_id, dispute_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/labels/{label_id}/disputes")
async def file_dispute(label_id: str, req: DisputeCreateRequest, current_user: User = Depends(get_current_user)):
    result = await create_dispute(label_id, req.dict(), current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/labels/{label_id}/disputes/{dispute_id}")
async def edit_dispute(label_id: str, dispute_id: str, req: DisputeUpdateRequest, current_user: User = Depends(get_current_user)):
    data = {k: v for k, v in req.dict().items() if v is not None}
    result = await update_dispute(label_id, dispute_id, data, current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/labels/{label_id}/disputes/{dispute_id}/respond")
async def dispute_respond(label_id: str, dispute_id: str, req: DisputeResponseRequest, current_user: User = Depends(get_current_user)):
    result = await respond_to_dispute(label_id, dispute_id, req.dict(), current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── Summary ────────────────────────────────────────────────────


@router.get("/labels/{label_id}/governance-disputes-summary")
async def governance_disputes_summary(label_id: str, current_user: User = Depends(get_current_user)):
    result = await get_governance_disputes_summary(label_id)
    return {"success": True, **result}
