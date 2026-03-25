"""
ULN Catalog, Distribution & Audit Snapshot Endpoints
=====================================================
Phase A (Quick Win) — Exposes:
  GET  /labels/{labelId}/catalog
  GET  /labels/{labelId}/distribution/status
  GET  /labels/{labelId}/audit-snapshot   (JSON download)
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from typing import Dict, Any

from uln_auth import get_current_user, get_current_admin_user, User
from services.uln_catalog_distribution_service import (
    get_label_catalog,
    get_label_distribution_status,
    generate_audit_snapshot,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uln", tags=["ULN Catalog & Distribution"])


@router.get("/labels/{label_id}/catalog")
async def label_catalog(label_id: str, current_user: User = Depends(get_current_user)):
    """Return catalog (assets) for a label."""
    result = await get_label_catalog(label_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/labels/{label_id}/distribution/status")
async def label_distribution_status(label_id: str, current_user: User = Depends(get_current_user)):
    """Return distribution endpoint statuses for a label."""
    result = await get_label_distribution_status(label_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/labels/{label_id}/audit-snapshot")
async def label_audit_snapshot(label_id: str, current_user: User = Depends(get_current_user)):
    """
    Generate and download a full audit snapshot of the label as JSON.
    Returns a downloadable JSON file.
    """
    result = await generate_audit_snapshot(label_id, current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    snapshot_json = json.dumps(result["snapshot"], indent=2, default=str)

    return Response(
        content=snapshot_json,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="label_{label_id}_audit_snapshot.json"'
        },
    )
