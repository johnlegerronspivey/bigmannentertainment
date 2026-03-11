"""
Remediation API Endpoints - Phase 3: Automated Remediation, GitHub Integration, AWS Inspector
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from remediation_service import get_remediation_service

router = APIRouter(prefix="/cve/remediation", tags=["Remediation & GitHub"])


class StatusUpdate(BaseModel):
    status: str
    notes: str = ""


class BulkIssueRequest(BaseModel):
    severity: str = "critical"
    limit: int = 10


# ─── GitHub Config ─────────────────────────────────────────────

@router.get("/config")
async def get_github_config():
    svc = get_remediation_service()
    return await svc.get_github_config()


# ─── Remediation Items ────────────────────────────────────────

@router.get("/items")
async def list_items(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
):
    svc = get_remediation_service()
    return await svc.list_items(status=status, severity=severity, limit=limit, skip=skip)


@router.get("/items/{item_id}")
async def get_item(item_id: str):
    svc = get_remediation_service()
    result = await svc.get_item(item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Remediation item not found")
    return result


@router.put("/items/{item_id}/status")
async def update_item_status(item_id: str, body: StatusUpdate):
    svc = get_remediation_service()
    result = await svc.update_item_status(item_id, body.status, body.notes)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found or invalid status")
    return result


# ─── GitHub Issue / PR Creation ────────────────────────────────

@router.post("/create-issue/{cve_entry_id}")
async def create_github_issue(cve_entry_id: str):
    svc = get_remediation_service()
    result = await svc.create_github_issue(cve_entry_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create issue"))
    return result


@router.post("/create-pr/{cve_entry_id}")
async def create_github_pr(cve_entry_id: str):
    svc = get_remediation_service()
    result = await svc.create_github_pr(cve_entry_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create PR"))
    return result


@router.post("/bulk-create-issues")
async def bulk_create_issues(body: BulkIssueRequest):
    svc = get_remediation_service()
    return await svc.bulk_create_issues(severity_filter=body.severity, limit=body.limit)


# ─── GitHub Sync ───────────────────────────────────────────────

@router.post("/sync-github")
async def sync_github_status():
    svc = get_remediation_service()
    return await svc.sync_github_status()


# ─── AWS Inspector / Security Hub ──────────────────────────────

@router.get("/aws/findings")
async def get_aws_findings(limit: int = Query(50, ge=1, le=100)):
    svc = get_remediation_service()
    return await svc.get_aws_findings(limit=limit)


@router.post("/aws/sync")
async def sync_aws_findings():
    svc = get_remediation_service()
    return await svc.sync_aws_findings()


@router.get("/aws/security-hub")
async def get_security_hub_summary():
    svc = get_remediation_service()
    return await svc.get_security_hub_summary()


# ─── Stats ─────────────────────────────────────────────────────

@router.get("/stats")
async def get_remediation_stats():
    svc = get_remediation_service()
    return await svc._get_remediation_stats()
