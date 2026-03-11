"""
Creative Studio for Agencies - API Endpoints
REST API for creative content management and AI-powered design generation
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime

from creative_studio_models import (
    BrandKit, BrandAsset, BrandColor, BrandFont, AssetType,
    DesignTemplate, TemplateCategory, SocialPlatform,
    CreativeProject, ProjectStatus, CollaboratorRole,
    AIGenerationRequest, AIGenerationResult, PublishConfig, PublishResult,
    CreativeStudioStats, ExportFormat,
    CreateBrandKitRequest, CreateProjectRequest, UpdateProjectRequest,
    AddCollaboratorRequest, AddCommentRequest, ExportProjectRequest,
    PublishProjectRequest, PLATFORM_DIMENSIONS
)
from creative_studio_service import get_creative_studio_service, CreativeStudioService

router = APIRouter(prefix="/creative-studio", tags=["Creative Studio"])

# Default agency ID for demo purposes
DEFAULT_AGENCY_ID = "agency_001"
DEFAULT_USER_ID = "user_001"


def get_service() -> CreativeStudioService:
    """Get the Creative Studio service"""
    service = get_creative_studio_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Creative Studio service not initialized")
    return service


# ==================== Health & Stats ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Creative Studio for Agencies",
        "version": "1.0.0",
        "features": [
            "Template-based content creation",
            "AI-powered design generation (Gemini)",
            "Brand asset management",
            "Collaboration tools",
            "Multi-platform publishing"
        ]
    }


@router.get("/stats", response_model=CreativeStudioStats)
async def get_studio_stats(
    agency_id: str = Query(default=DEFAULT_AGENCY_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Get creative studio statistics"""
    return await service.get_studio_stats(agency_id)


@router.get("/platform-dimensions")
async def get_platform_dimensions():
    """Get dimensions for all supported platforms"""
    return {
        platform.value: dims
        for platform, dims in PLATFORM_DIMENSIONS.items()
    }


# ==================== Brand Kits ====================

@router.post("/brand-kits", response_model=BrandKit)
async def create_brand_kit(
    request: CreateBrandKitRequest,
    agency_id: str = Query(default=DEFAULT_AGENCY_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Create a new brand kit"""
    return await service.create_brand_kit(agency_id, request)


@router.get("/brand-kits", response_model=List[BrandKit])
async def get_brand_kits(
    agency_id: str = Query(default=DEFAULT_AGENCY_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Get all brand kits for an agency"""
    return await service.get_brand_kits(agency_id)


@router.get("/brand-kits/{brand_kit_id}", response_model=BrandKit)
async def get_brand_kit(
    brand_kit_id: str,
    service: CreativeStudioService = Depends(get_service)
):
    """Get a specific brand kit"""
    brand_kit = await service.get_brand_kit(brand_kit_id)
    if not brand_kit:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return brand_kit


@router.put("/brand-kits/{brand_kit_id}", response_model=BrandKit)
async def update_brand_kit(
    brand_kit_id: str,
    request: CreateBrandKitRequest,
    service: CreativeStudioService = Depends(get_service)
):
    """Update a brand kit"""
    brand_kit = await service.update_brand_kit(brand_kit_id, request.dict(exclude_unset=True))
    if not brand_kit:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return brand_kit


@router.delete("/brand-kits/{brand_kit_id}")
async def delete_brand_kit(
    brand_kit_id: str,
    service: CreativeStudioService = Depends(get_service)
):
    """Delete a brand kit"""
    success = await service.delete_brand_kit(brand_kit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return {"success": True, "message": "Brand kit deleted"}


@router.post("/brand-kits/{brand_kit_id}/assets", response_model=BrandKit)
async def add_brand_asset(
    brand_kit_id: str,
    asset: BrandAsset,
    service: CreativeStudioService = Depends(get_service)
):
    """Add an asset to a brand kit"""
    brand_kit = await service.add_brand_asset(brand_kit_id, asset)
    if not brand_kit:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return brand_kit


# ==================== Templates ====================

@router.get("/templates", response_model=List[DesignTemplate])
async def get_templates(
    category: Optional[TemplateCategory] = None,
    platform: Optional[SocialPlatform] = None,
    search: Optional[str] = None,
    service: CreativeStudioService = Depends(get_service)
):
    """Get design templates with optional filters"""
    return await service.get_templates(category, platform, search)


@router.get("/templates/{template_id}", response_model=DesignTemplate)
async def get_template(
    template_id: str,
    service: CreativeStudioService = Depends(get_service)
):
    """Get a specific template"""
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


# ==================== Projects ====================

@router.post("/projects", response_model=CreativeProject)
async def create_project(
    request: CreateProjectRequest,
    agency_id: str = Query(default=DEFAULT_AGENCY_ID),
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Create a new creative project"""
    return await service.create_project(agency_id, user_id, request)


@router.get("/projects")
async def get_projects(
    agency_id: str = Query(default=DEFAULT_AGENCY_ID),
    status: Optional[ProjectStatus] = None,
    category: Optional[TemplateCategory] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    service: CreativeStudioService = Depends(get_service)
):
    """Get projects with filters"""
    projects, total = await service.get_projects(agency_id, status, category, search, limit, offset)
    return {
        "success": True,
        "projects": projects,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/projects/{project_id}", response_model=CreativeProject)
async def get_project(
    project_id: str,
    service: CreativeStudioService = Depends(get_service)
):
    """Get a specific project"""
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=CreativeProject)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    service: CreativeStudioService = Depends(get_service)
):
    """Update a project"""
    project = await service.update_project(project_id, request)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    service: CreativeStudioService = Depends(get_service)
):
    """Delete a project"""
    success = await service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "message": "Project deleted"}


@router.post("/projects/{project_id}/versions", response_model=CreativeProject)
async def save_project_version(
    project_id: str,
    name: Optional[str] = None,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Save a version snapshot of the project"""
    project = await service.save_project_version(project_id, user_id, name)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ==================== Collaboration ====================

@router.post("/projects/{project_id}/collaborators", response_model=CreativeProject)
async def add_collaborator(
    project_id: str,
    request: AddCollaboratorRequest,
    service: CreativeStudioService = Depends(get_service)
):
    """Add a collaborator to a project"""
    import uuid
    project = await service.add_collaborator(
        project_id,
        user_id=str(uuid.uuid4()),
        user_email=request.user_email,
        user_name=request.user_email.split("@")[0],
        role=request.role
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}/collaborators/{user_id}", response_model=CreativeProject)
async def remove_collaborator(
    project_id: str,
    user_id: str,
    service: CreativeStudioService = Depends(get_service)
):
    """Remove a collaborator from a project"""
    project = await service.remove_collaborator(project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/comments", response_model=CreativeProject)
async def add_comment(
    project_id: str,
    request: AddCommentRequest,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Add a comment to a project"""
    project = await service.add_comment(
        project_id,
        user_id=user_id,
        user_name="User",
        content=request.content,
        position=request.position
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/comments/{comment_id}/resolve", response_model=CreativeProject)
async def resolve_comment(
    project_id: str,
    comment_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Resolve a comment"""
    project = await service.resolve_comment(project_id, comment_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ==================== AI Generation ====================

@router.post("/ai/generate", response_model=AIGenerationResult)
async def generate_ai_image(
    request: AIGenerationRequest,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Generate an image using AI"""
    return await service.generate_ai_image(request, user_id)


@router.get("/ai/history", response_model=List[AIGenerationResult])
async def get_ai_generation_history(
    user_id: str = Query(default=DEFAULT_USER_ID),
    limit: int = Query(default=20, le=50),
    service: CreativeStudioService = Depends(get_service)
):
    """Get AI generation history"""
    return await service.get_ai_generation_history(user_id, limit)


@router.get("/ai/styles")
async def get_ai_styles():
    """Get available AI generation styles"""
    return {
        "styles": [
            {"id": "photorealistic", "name": "Photorealistic", "description": "High-quality realistic images"},
            {"id": "illustration", "name": "Illustration", "description": "Hand-drawn style illustrations"},
            {"id": "minimal", "name": "Minimal", "description": "Clean, simple designs"},
            {"id": "3d_render", "name": "3D Render", "description": "3D rendered graphics"},
            {"id": "watercolor", "name": "Watercolor", "description": "Watercolor painting style"},
            {"id": "pop_art", "name": "Pop Art", "description": "Bold, colorful pop art style"},
            {"id": "vintage", "name": "Vintage", "description": "Retro and vintage aesthetics"},
            {"id": "neon", "name": "Neon", "description": "Glowing neon effects"},
            {"id": "gradient", "name": "Gradient", "description": "Smooth gradient backgrounds"},
            {"id": "abstract", "name": "Abstract", "description": "Abstract artistic designs"}
        ]
    }


# ==================== Export & Publish ====================

@router.post("/projects/{project_id}/export")
async def export_project(
    project_id: str,
    request: ExportProjectRequest,
    service: CreativeStudioService = Depends(get_service)
):
    """Export a project to specified format"""
    result = await service.export_project(
        project_id,
        request.format,
        request.quality,
        request.scale
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Export failed"))
    return result


@router.post("/projects/{project_id}/publish")
async def publish_project(
    project_id: str,
    request: PublishProjectRequest,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: CreativeStudioService = Depends(get_service)
):
    """Publish a project to multiple platforms"""
    results = []
    for config in request.platforms:
        result = await service.publish_to_platform(project_id, config, user_id)
        results.append(result)
    
    return {
        "success": True,
        "results": results,
        "total_published": len([r for r in results if r.status == "published"]),
        "total_failed": len([r for r in results if r.status == "failed"])
    }


@router.get("/publish-history", response_model=List[PublishResult])
async def get_publish_history(
    agency_id: str = Query(default=DEFAULT_AGENCY_ID),
    platform: Optional[SocialPlatform] = None,
    limit: int = Query(default=50, le=100),
    service: CreativeStudioService = Depends(get_service)
):
    """Get publishing history"""
    return await service.get_publish_history(agency_id, platform, limit)


# ==================== Categories & Platforms ====================

@router.get("/categories")
async def get_categories():
    """Get available template categories"""
    return {
        "categories": [
            {"id": cat.value, "name": cat.value.replace("_", " ").title()}
            for cat in TemplateCategory
        ]
    }


@router.get("/platforms")
async def get_platforms():
    """Get available social platforms with dimensions"""
    platforms = []
    for platform in SocialPlatform:
        dims = PLATFORM_DIMENSIONS.get(platform, {"width": 1080, "height": 1080})
        platforms.append({
            "id": platform.value,
            "name": platform.value.replace("_", " ").title(),
            "width": dims["width"],
            "height": dims["height"]
        })
    return {"platforms": platforms}
