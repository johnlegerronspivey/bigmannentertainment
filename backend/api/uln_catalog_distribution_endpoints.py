"""
ULN Catalog, Rights, Distribution & Audit Endpoints
=====================================================
Phase B — Full CRUD for label_assets, label_rights, label_endpoints.
Includes CSV bulk-import for catalog migration.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import Response
from typing import Dict, Any
from pydantic import BaseModel, Field
from typing import List, Optional

from uln_auth import get_current_user, User
from services.uln_catalog_distribution_service import (
    get_label_catalog,
    create_asset,
    update_asset,
    delete_asset,
    get_asset_rights,
    upsert_asset_rights,
    get_label_distribution_status,
    create_endpoint,
    update_endpoint,
    delete_endpoint,
    generate_audit_snapshot,
)
from services.catalog_import_service import (
    parse_and_import_csv,
    preview_csv,
    generate_csv_template,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uln", tags=["ULN Catalog & Distribution"])


# ── Request models ─────────────────────────────────────────────────

class AssetCreateRequest(BaseModel):
    title: str
    type: str = "single"
    artist: str = ""
    isrc: str = ""
    upc: str = ""
    gtin: str = ""
    release_date: str = ""
    genre: str = ""
    status: str = "draft"
    platforms: List[str] = Field(default_factory=list)
    streams_total: int = 0


class AssetUpdateRequest(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    artist: Optional[str] = None
    isrc: Optional[str] = None
    upc: Optional[str] = None
    gtin: Optional[str] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    status: Optional[str] = None
    platforms: Optional[List[str]] = None
    streams_total: Optional[int] = None


class RightsSplit(BaseModel):
    party: str
    role: str = ""
    percentage: float = 0.0


class RightsUpsertRequest(BaseModel):
    splits: List[Dict[str, Any]] = Field(default_factory=list)
    territories: List[str] = Field(default_factory=lambda: ["GLOBAL"])
    ai_consent: bool = False
    ai_consent_details: str = ""
    sponsorship_rules: str = ""
    exclusive: bool = True
    expiry_date: Optional[str] = None


class EndpointCreateRequest(BaseModel):
    platform: str
    status: str = "pending"
    endpoint_type: str = "streaming"
    credentials_ref: str = ""
    gs1_gln: str = ""
    gs1_company_prefix: str = ""


class EndpointUpdateRequest(BaseModel):
    platform: Optional[str] = None
    status: Optional[str] = None
    endpoint_type: Optional[str] = None
    credentials_ref: Optional[str] = None
    last_delivery: Optional[str] = None
    assets_delivered: Optional[int] = None
    errors: Optional[int] = None
    error_message: Optional[str] = None


# ── Catalog (Assets) ──────────────────────────────────────────────


@router.get("/labels/{label_id}/catalog")
async def label_catalog(label_id: str, current_user: User = Depends(get_current_user)):
    result = await get_label_catalog(label_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/labels/{label_id}/catalog/assets")
async def add_asset(label_id: str, req: AssetCreateRequest, current_user: User = Depends(get_current_user)):
    # Mandatory GS1 identifier validation
    from utils.gs1_validators import validate_asset_identifiers
    id_errors = validate_asset_identifiers({"gtin": req.gtin, "isrc": req.isrc, "upc": req.upc})
    if id_errors:
        raise HTTPException(status_code=400, detail={"validation_errors": id_errors, "message": "GS1 identifier validation failed"})

    result = await create_asset(label_id, req.dict(), current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/labels/{label_id}/catalog/assets/{asset_id}")
async def edit_asset(label_id: str, asset_id: str, req: AssetUpdateRequest, current_user: User = Depends(get_current_user)):
    data = {k: v for k, v in req.dict().items() if v is not None}
    result = await update_asset(label_id, asset_id, data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/labels/{label_id}/catalog/assets/{asset_id}")
async def remove_asset(label_id: str, asset_id: str, current_user: User = Depends(get_current_user)):
    result = await delete_asset(label_id, asset_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Rights ──────────────────────────────────────────────────────────


@router.get("/labels/{label_id}/catalog/assets/{asset_id}/rights")
async def asset_rights(label_id: str, asset_id: str, current_user: User = Depends(get_current_user)):
    result = await get_asset_rights(label_id, asset_id)
    return result


@router.put("/labels/{label_id}/catalog/assets/{asset_id}/rights")
async def set_asset_rights(label_id: str, asset_id: str, req: RightsUpsertRequest, current_user: User = Depends(get_current_user)):
    result = await upsert_asset_rights(label_id, asset_id, req.dict(), current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── Distribution Endpoints ─────────────────────────────────────────


@router.get("/labels/{label_id}/distribution/status")
async def label_distribution_status(label_id: str, current_user: User = Depends(get_current_user)):
    result = await get_label_distribution_status(label_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/labels/{label_id}/endpoints")
async def add_endpoint(label_id: str, req: EndpointCreateRequest, current_user: User = Depends(get_current_user)):
    # Mandatory GS1 identifiers on distribution endpoints
    from utils.gs1_validators import validate_gln, validate_gs1_company_prefix
    errors = {}
    if not req.gs1_gln.strip():
        errors["gs1_gln"] = "GLN is required for distribution endpoints"
    else:
        err = validate_gln(req.gs1_gln)
        if err:
            errors["gs1_gln"] = err
    if not req.gs1_company_prefix.strip():
        errors["gs1_company_prefix"] = "GS1 Company Prefix is required for distribution endpoints"
    else:
        err = validate_gs1_company_prefix(req.gs1_company_prefix)
        if err:
            errors["gs1_company_prefix"] = err
    if errors:
        raise HTTPException(status_code=400, detail={"validation_errors": errors, "message": "GS1 identifier validation failed"})

    result = await create_endpoint(label_id, req.dict(), current_user.id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/labels/{label_id}/endpoints/{endpoint_id}")
async def edit_endpoint(label_id: str, endpoint_id: str, req: EndpointUpdateRequest, current_user: User = Depends(get_current_user)):
    data = {k: v for k, v in req.dict().items() if v is not None}
    result = await update_endpoint(label_id, endpoint_id, data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/labels/{label_id}/endpoints/{endpoint_id}")
async def remove_endpoint(label_id: str, endpoint_id: str, current_user: User = Depends(get_current_user)):
    result = await delete_endpoint(label_id, endpoint_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Audit Snapshot ──────────────────────────────────────────────────


@router.get("/labels/{label_id}/audit-snapshot")
async def label_audit_snapshot(label_id: str, current_user: User = Depends(get_current_user)):
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



# ── CSV Bulk Import ─────────────────────────────────────────────────


@router.get("/labels/{label_id}/catalog/csv-template")
async def download_csv_template(label_id: str, current_user: User = Depends(get_current_user)):
    csv_content = generate_csv_template()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="catalog_import_template_{label_id}.csv"'
        },
    )


@router.post("/labels/{label_id}/catalog/preview-csv")
async def preview_csv_upload(
    label_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    try:
        csv_text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            csv_text = content.decode("latin-1")
        except Exception:
            raise HTTPException(status_code=400, detail="Unable to decode CSV file")

    result = await preview_csv(csv_text)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/labels/{label_id}/catalog/import-csv")
async def import_csv_catalog(
    label_id: str,
    file: UploadFile = File(...),
    skip_duplicates: bool = Form(default=True),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    try:
        csv_text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            csv_text = content.decode("latin-1")
        except Exception:
            raise HTTPException(status_code=400, detail="Unable to decode CSV file")

    result = await parse_and_import_csv(label_id, csv_text, current_user.id, skip_duplicates)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
