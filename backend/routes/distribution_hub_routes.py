"""
Distribution Hub API Routes - Central command for content distribution.
Handles content CRUD, deliveries, export packages, metadata/rights, and platform connections.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel

from auth.service import get_current_user
from models.core import User
from services.distribution_hub_service import (
    distribution_hub_svc,
    PLATFORM_CATEGORIES,
    ALL_HUB_PLATFORMS,
)

router = APIRouter(prefix="/distribution-hub", tags=["Distribution Hub"])


# ─── Request Models ───

class ContentCreateRequest(BaseModel):
    title: str
    content_type: str  # audio, video, image, film
    description: str = ""
    file_url: str = ""
    file_name: str = ""
    file_size: int = 0
    thumbnail_url: str = ""
    duration: Optional[float] = None
    artist: str = ""
    album: str = ""
    genre: str = ""
    release_date: str = ""
    tags: List[str] = []
    language: str = "en"
    isrc: str = ""
    upc: str = ""
    iswc: str = ""
    copyright_holder: str = ""
    copyright_year: str = ""
    publisher: str = ""
    record_label: str = ""
    licensing_type: str = ""
    content_rating: str = ""
    territory_rights: List[str] = ["worldwide"]
    copyright_info: str = ""
    licensing_terms: str = ""
    royalty_splits: list = []
    drm_enabled: bool = False
    exclusive_rights: list = []


class DistributeRequest(BaseModel):
    content_id: str
    platform_ids: List[str]
    metadata_overrides: dict = {}


class MetadataUpdateRequest(BaseModel):
    basic: dict = {}
    advanced: dict = {}
    rights: dict = {}
    title: str = ""
    description: str = ""


class PlatformCredentialsRequest(BaseModel):
    platform_id: str
    credentials: dict


# ─── Hub Dashboard ───

@router.get("/stats")
async def get_hub_stats(current_user: User = Depends(get_current_user)):
    """Get distribution hub dashboard statistics."""
    stats = await distribution_hub_svc.get_hub_stats(current_user.id)
    return stats


@router.get("/platforms")
async def get_hub_platforms():
    """Get all available hub platforms organized by category."""
    return {
        "categories": PLATFORM_CATEGORIES,
        "total_platforms": len(ALL_HUB_PLATFORMS),
    }


# ─── Content CRUD ───

@router.post("/content")
async def create_content(
    req: ContentCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Register new content in the distribution hub."""
    content = await distribution_hub_svc.create_content(current_user.id, req.dict())
    return {"message": "Content created successfully", "content": content}


@router.get("/content")
async def get_content_library(
    content_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's content library."""
    items = await distribution_hub_svc.get_content_library(current_user.id, content_type)
    return {"content": items, "total": len(items)}


@router.get("/content/{content_id}")
async def get_content_detail(content_id: str, current_user: User = Depends(get_current_user)):
    """Get detailed content info including metadata and rights."""
    content = await distribution_hub_svc.get_content_by_id(content_id, current_user.id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.put("/content/{content_id}/metadata")
async def update_content_metadata(
    content_id: str,
    req: MetadataUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update content metadata and rights information."""
    updated = await distribution_hub_svc.update_content_metadata(
        content_id, current_user.id, req.dict(exclude_none=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Content not found or no changes made")
    return {"message": "Metadata updated", "content": updated}


@router.delete("/content/{content_id}")
async def delete_content(content_id: str, current_user: User = Depends(get_current_user)):
    """Delete content from the hub."""
    deleted = await distribution_hub_svc.delete_content(content_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"message": "Content deleted successfully"}


# ─── Content Upload via File ───

@router.post("/upload")
async def upload_content_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    content_type: str = Form(...),
    description: str = Form(""),
    artist: str = Form(""),
    genre: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    """Upload a file directly to the hub."""
    upload_dir = "/app/uploads/hub"
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1]
    safe_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, safe_name)

    file_bytes = await file.read()
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    file_url = f"/api/distribution-hub/files/{safe_name}"

    content = await distribution_hub_svc.create_content(current_user.id, {
        "title": title,
        "content_type": content_type,
        "description": description,
        "file_url": file_url,
        "file_name": file.filename,
        "file_size": len(file_bytes),
        "artist": artist,
        "genre": genre,
    })
    return {"message": "File uploaded and content created", "content": content}


@router.get("/files/{filename}")
async def serve_hub_file(filename: str):
    """Serve uploaded hub files."""
    from fastapi.responses import FileResponse
    file_path = f"/app/uploads/hub/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


# ─── Distribution / Delivery ───

@router.post("/distribute")
async def distribute_content(
    req: DistributeRequest,
    current_user: User = Depends(get_current_user)
):
    """Distribute content to selected platforms. Auto-push or export package depending on platform."""
    try:
        result = await distribution_hub_svc.create_delivery(
            current_user.id, req.content_id, req.platform_ids, req.metadata_overrides
        )
        return {
            "message": f"Distribution initiated to {result['total_deliveries']} platforms",
            "batch_id": result["batch_id"],
            "api_push_count": result["api_push"],
            "export_package_count": result["export_packages"],
            "deliveries": result["deliveries"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/deliveries")
async def get_deliveries(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get delivery history."""
    items = await distribution_hub_svc.get_deliveries(current_user.id, status, limit)
    return {"deliveries": items, "total": len(items)}


@router.get("/deliveries/batch/{batch_id}")
async def get_delivery_batch(batch_id: str, current_user: User = Depends(get_current_user)):
    """Get all deliveries in a batch."""
    items = await distribution_hub_svc.get_delivery_batch(batch_id, current_user.id)
    return {"batch_id": batch_id, "deliveries": items, "total": len(items)}


@router.put("/deliveries/{delivery_id}/status")
async def update_delivery_status(
    delivery_id: str,
    status: str,
    response_data: dict = {},
    current_user: User = Depends(get_current_user)
):
    """Update a delivery's status (e.g., mark as delivered after manual upload)."""
    updated = await distribution_hub_svc.update_delivery_status(
        delivery_id, current_user.id, status, response_data
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return {"message": "Delivery status updated", "delivery": updated}


# ─── Export Packages ───

@router.post("/deliveries/{delivery_id}/export")
async def generate_export_package(delivery_id: str, current_user: User = Depends(get_current_user)):
    """Generate a platform-ready export package for a delivery."""
    try:
        package = await distribution_hub_svc.generate_export_package(delivery_id, current_user.id)
        return {"message": "Export package generated", "package": package}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── Platform Credentials ───

@router.post("/platforms/connect")
async def connect_platform(
    req: PlatformCredentialsRequest,
    current_user: User = Depends(get_current_user)
):
    """Save credentials for a platform connection."""
    result = await distribution_hub_svc.save_platform_credentials(
        current_user.id, req.platform_id, req.credentials
    )
    return {"message": f"Connected to {result['platform_name']}", "connection": result}


@router.get("/platforms/connected")
async def get_connected_platforms(current_user: User = Depends(get_current_user)):
    """Get list of connected platforms for the user."""
    items = await distribution_hub_svc.get_connected_platforms(current_user.id)
    return {"connected_platforms": items, "total": len(items)}


@router.delete("/platforms/{platform_id}/disconnect")
async def disconnect_platform(platform_id: str, current_user: User = Depends(get_current_user)):
    """Disconnect a platform."""
    disconnected = await distribution_hub_svc.disconnect_platform(current_user.id, platform_id)
    if not disconnected:
        raise HTTPException(status_code=404, detail="Platform connection not found")
    return {"message": "Platform disconnected"}


# ─── Distribution Templates ───

class TemplateCreateRequest(BaseModel):
    name: str
    description: str = ""
    icon: str = "layers"
    platform_ids: List[str] = []


class TemplateUpdateRequest(BaseModel):
    name: str = ""
    description: str = ""
    icon: str = ""
    platform_ids: List[str] = []


@router.get("/templates")
async def get_templates(current_user: User = Depends(get_current_user)):
    """Get all distribution templates (system + custom)."""
    templates = await distribution_hub_svc.get_templates(current_user.id)
    system = [t for t in templates if t.get("is_system")]
    custom = [t for t in templates if not t.get("is_system")]
    return {"templates": templates, "system_count": len(system), "custom_count": len(custom)}


@router.get("/templates/{template_id}")
async def get_template(template_id: str, current_user: User = Depends(get_current_user)):
    """Get a single template by ID."""
    template = await distribution_hub_svc.get_template_by_id(template_id, current_user.id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates")
async def create_template(req: TemplateCreateRequest, current_user: User = Depends(get_current_user)):
    """Create a custom distribution template."""
    template = await distribution_hub_svc.create_template(current_user.id, req.dict())
    return {"message": "Template created", "template": template}


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    req: TemplateUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a custom distribution template."""
    updated = await distribution_hub_svc.update_template(
        template_id, current_user.id, {k: v for k, v in req.dict().items() if v}
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Template not found or cannot be edited")
    return {"message": "Template updated", "template": updated}


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str, current_user: User = Depends(get_current_user)):
    """Delete a custom distribution template."""
    deleted = await distribution_hub_svc.delete_template(template_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found or cannot be deleted")
    return {"message": "Template deleted"}
