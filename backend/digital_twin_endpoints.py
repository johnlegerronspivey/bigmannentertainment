"""
Digital Twin API Endpoints
==========================
REST API for Digital Twin Model Creation system.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime

from digital_twin_service import (
    DigitalTwinService, get_digital_twin_service,
    DigitalTwinProfile, VirtualPhotoshoot, TwinLicense,
    ARTryOnAsset, MetaverseAvatar,
    TwinType, TwinStyle, UsageContext, LicenseType, TwinStatus
)

router = APIRouter(prefix="/digital-twin", tags=["Digital Twin"])


# Database dependency
async def get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    return client[os.environ.get("DB_NAME", "bigmann_entertainment_production")]


# ============================================
# DIGITAL TWIN CREATION & MANAGEMENT
# ============================================

@router.post("/create", response_model=DigitalTwinProfile)
async def create_digital_twin(
    model_id: str = Query(..., description="ID of the real model"),
    model_data: Dict[str, Any] = Body(..., description="Model profile data"),
    twin_type: TwinType = Query(default=TwinType.AVATAR_2D),
    style: TwinStyle = Query(default=TwinStyle.PHOTOREALISTIC),
    generate_immediately: bool = Query(default=True),
    db=Depends(get_db)
):
    """
    Create a digital twin for a real model.
    This generates an AI avatar that can be used for virtual campaigns,
    AR try-ons, and metaverse presence.
    """
    service = get_digital_twin_service(db)
    return await service.create_digital_twin(
        model_id=model_id,
        model_data=model_data,
        twin_type=twin_type,
        style=style,
        generate_immediately=generate_immediately
    )


@router.get("/{twin_id}", response_model=DigitalTwinProfile)
async def get_digital_twin(twin_id: str, db=Depends(get_db)):
    """Get a digital twin by ID."""
    service = get_digital_twin_service(db)
    twin = await service.get_twin(twin_id)
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    return twin


@router.get("/model/{model_id}", response_model=List[DigitalTwinProfile])
async def get_twins_by_model(model_id: str, db=Depends(get_db)):
    """Get all digital twins for a specific model."""
    service = get_digital_twin_service(db)
    return await service.get_twins_by_model(model_id)


@router.get("/agency/{agency_id}", response_model=List[DigitalTwinProfile])
async def get_twins_by_agency(agency_id: str, db=Depends(get_db)):
    """Get all digital twins for an agency."""
    service = get_digital_twin_service(db)
    return await service.get_twins_by_agency(agency_id)


@router.post("/{twin_id}/variants")
async def generate_avatar_variants(
    twin_id: str,
    variant_styles: List[str] = Body(..., description="List of style descriptions"),
    count_per_style: int = Query(default=1, ge=1, le=3),
    db=Depends(get_db)
):
    """
    Generate multiple style variants of a digital twin.
    Example styles: "summer beach vibes", "corporate professional", "evening glamour"
    """
    service = get_digital_twin_service(db)
    variants = await service.generate_avatar_variants(twin_id, variant_styles, count_per_style)
    return {"twin_id": twin_id, "variants_generated": len(variants), "variant_urls": variants}


@router.get("/{twin_id}/analytics")
async def get_twin_analytics(twin_id: str, db=Depends(get_db)):
    """Get comprehensive analytics for a digital twin."""
    service = get_digital_twin_service(db)
    analytics = await service.get_twin_analytics(twin_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    return analytics


@router.get("/{twin_id}/recommendations")
async def get_ai_recommendations(twin_id: str, db=Depends(get_db)):
    """Get AI-powered revenue maximization recommendations for a twin."""
    service = get_digital_twin_service(db)
    recommendations = await service.get_ai_recommendations(twin_id)
    if not recommendations or "error" in recommendations:
        raise HTTPException(status_code=404, detail=recommendations.get("error", "Unable to generate recommendations"))
    return recommendations


# ============================================
# VIRTUAL PHOTOSHOOTS
# ============================================

@router.post("/{twin_id}/photoshoot", response_model=VirtualPhotoshoot)
async def create_virtual_photoshoot(
    twin_id: str,
    client_id: str = Query(...),
    client_name: str = Query(...),
    photoshoot_data: Dict[str, Any] = Body(default={}),
    style: TwinStyle = Query(default=TwinStyle.FASHION_EDITORIAL),
    background_setting: str = Query(default="professional studio"),
    outfit_description: str = Query(default="elegant fashion attire"),
    num_images: int = Query(default=5, ge=1, le=10),
    db=Depends(get_db)
):
    """
    Create a virtual photoshoot with a digital twin.
    Zero travel costs, instant delivery.
    
    Body can include: {"concept": "...", "poses": ["pose1", "pose2"]}
    """
    service = get_digital_twin_service(db)
    
    # Extract from body or use defaults
    concept = photoshoot_data.get("concept", "Professional fashion photoshoot")
    poses = photoshoot_data.get("poses", ["confident stance", "natural smile", "profile view", "dynamic pose", "relaxed pose"])
    
    try:
        photoshoot = await service.create_virtual_photoshoot(
            twin_id=twin_id,
            client_id=client_id,
            client_name=client_name,
            concept=concept,
            style=style,
            background_setting=background_setting,
            outfit_description=outfit_description,
            poses=poses,
            num_images=num_images
        )
        return photoshoot
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/photoshoots/{photoshoot_id}")
async def get_photoshoot(photoshoot_id: str, db=Depends(get_db)):
    """Get a virtual photoshoot by ID."""
    try:
        photoshoots_collection = db["virtual_photoshoots"]
        photoshoot = await photoshoots_collection.find_one({"photoshoot_id": photoshoot_id})
        if not photoshoot:
            raise HTTPException(status_code=404, detail="Photoshoot not found")
        photoshoot.pop("_id", None)
        return photoshoot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{twin_id}/photoshoots")
async def get_twin_photoshoots(twin_id: str, limit: int = Query(default=20), db=Depends(get_db)):
    """Get all photoshoots for a digital twin."""
    try:
        photoshoots_collection = db["virtual_photoshoots"]
        photoshoots = await photoshoots_collection.find({"twin_id": twin_id}).sort("created_at", -1).limit(limit).to_list(limit)
        return [{"photoshoot_id": p.get("photoshoot_id"), "concept": p.get("concept"), "status": p.get("status"), "images_generated": p.get("images_generated", 0), "total_price": p.get("total_price", 0), "created_at": p.get("created_at")} for p in photoshoots]
    except Exception:
        return []


# ============================================
# LICENSING
# ============================================

@router.post("/{twin_id}/license", response_model=TwinLicense)
async def create_twin_license(
    twin_id: str,
    licensee_id: str = Query(...),
    licensee_name: str = Query(...),
    license_type: LicenseType = Query(default=LicenseType.NON_EXCLUSIVE),
    usage_contexts: List[UsageContext] = Body(...),
    duration_days: int = Query(default=365, ge=1, le=3650),
    auto_renewal: bool = Query(default=False),
    db=Depends(get_db)
):
    """
    Create a license for using a digital twin.
    Licensing enables revenue sharing with the original model.
    """
    service = get_digital_twin_service(db)
    try:
        license = await service.create_twin_license(
            twin_id=twin_id,
            licensee_id=licensee_id,
            licensee_name=licensee_name,
            license_type=license_type,
            usage_contexts=usage_contexts,
            duration_days=duration_days,
            auto_renewal=auto_renewal
        )
        return license
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{twin_id}/licenses")
async def get_twin_licenses(twin_id: str, status: Optional[str] = Query(default=None), db=Depends(get_db)):
    """Get all licenses for a digital twin."""
    try:
        licenses_collection = db["twin_licenses"]
        query = {"twin_id": twin_id}
        if status:
            query["status"] = status
        licenses = await licenses_collection.find(query).sort("created_at", -1).to_list(100)
        return [{k: v for k, v in lic.items() if k != "_id"} for lic in licenses]
    except Exception:
        return []


# ============================================
# AR TRY-ON ASSETS
# ============================================

@router.post("/{twin_id}/ar-asset", response_model=ARTryOnAsset)
async def create_ar_tryon_asset(
    twin_id: str,
    asset_type: str = Query(..., description="clothing, accessory, makeup, hairstyle"),
    asset_name: str = Query(...),
    product_data: Dict[str, Any] = Body(default={}),
    db=Depends(get_db)
):
    """
    Create an AR try-on compatible asset for the digital twin.
    Enables virtual try-on experiences for products.
    """
    service = get_digital_twin_service(db)
    try:
        asset = await service.create_ar_tryon_asset(
            twin_id=twin_id,
            asset_type=asset_type,
            asset_name=asset_name,
            product_data=product_data
        )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{twin_id}/ar-assets")
async def get_twin_ar_assets(twin_id: str, db=Depends(get_db)):
    """Get all AR try-on assets for a digital twin."""
    try:
        ar_assets_collection = db["ar_tryon_assets"]
        assets = await ar_assets_collection.find({"twin_id": twin_id}).to_list(100)
        return [{k: v for k, v in a.items() if k != "_id"} for a in assets]
    except Exception:
        return []


# ============================================
# METAVERSE AVATARS
# ============================================

@router.post("/{twin_id}/metaverse-avatar", response_model=MetaverseAvatar)
async def create_metaverse_avatar(
    twin_id: str,
    platform: str = Query(..., description="decentraland, sandbox, roblox, meta_horizon"),
    animations: List[str] = Body(default=["idle", "walk", "wave", "pose"]),
    wearables: List[str] = Body(default=[]),
    db=Depends(get_db)
):
    """
    Create a metaverse-compatible avatar from a digital twin.
    Ready for virtual worlds and experiences.
    """
    service = get_digital_twin_service(db)
    try:
        avatar = await service.create_metaverse_avatar(
            twin_id=twin_id,
            platform=platform,
            animations=animations,
            wearables=wearables
        )
        return avatar
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{twin_id}/metaverse-avatars")
async def get_twin_metaverse_avatars(twin_id: str, db=Depends(get_db)):
    """Get all metaverse avatars for a digital twin."""
    try:
        metaverse_collection = db["metaverse_avatars"]
        avatars = await metaverse_collection.find({"twin_id": twin_id}).to_list(100)
        return [{k: v for k, v in a.items() if k != "_id"} for a in avatars]
    except Exception:
        return []


# ============================================
# TWIN TYPES & STYLES REFERENCE
# ============================================

@router.get("/reference/twin-types")
async def get_twin_types():
    """Get available digital twin types."""
    return {
        "twin_types": [
            {"value": t.value, "name": t.name, "description": _get_type_description(t)}
            for t in TwinType
        ]
    }


@router.get("/reference/styles")
async def get_twin_styles():
    """Get available digital twin styles."""
    return {
        "styles": [
            {"value": s.value, "name": s.name, "description": _get_style_description(s)}
            for s in TwinStyle
        ]
    }


@router.get("/reference/usage-contexts")
async def get_usage_contexts():
    """Get available usage contexts for licensing."""
    return {
        "usage_contexts": [
            {"value": u.value, "name": u.name, "description": _get_usage_description(u)}
            for u in UsageContext
        ]
    }


def _get_type_description(t: TwinType) -> str:
    descriptions = {
        TwinType.AVATAR_2D: "2D digital avatar - perfect for social media and campaigns",
        TwinType.AVATAR_3D: "Full 3D avatar - AR, VR, and metaverse ready",
        TwinType.FULL_BODY: "Full body representation - ideal for fashion and e-commerce",
        TwinType.HEADSHOT: "Professional headshot - corporate and editorial use",
        TwinType.STYLIZED: "Artistic stylized version - unique brand collaborations",
        TwinType.REALISTIC: "Hyper-realistic twin - indistinguishable from photos"
    }
    return descriptions.get(t, "")


def _get_style_description(s: TwinStyle) -> str:
    descriptions = {
        TwinStyle.PHOTOREALISTIC: "Ultra-realistic photography style",
        TwinStyle.FASHION_EDITORIAL: "High fashion magazine aesthetic",
        TwinStyle.COMMERCIAL: "Clean, approachable commercial look",
        TwinStyle.ARTISTIC: "Creative, fine art inspired",
        TwinStyle.ANIME: "Japanese anime/manga style",
        TwinStyle.CYBERPUNK: "Futuristic cyberpunk aesthetic",
        TwinStyle.MINIMAL: "Clean, minimalist approach",
        TwinStyle.LUXURY: "Premium luxury brand aesthetic"
    }
    return descriptions.get(s, "")


def _get_usage_description(u: UsageContext) -> str:
    descriptions = {
        UsageContext.VIRTUAL_CAMPAIGN: "Digital advertising and marketing campaigns",
        UsageContext.AR_TRYON: "Augmented reality try-on experiences",
        UsageContext.METAVERSE: "Virtual world presence and events",
        UsageContext.SOCIAL_MEDIA: "Social media content and posts",
        UsageContext.E_COMMERCE: "Online shopping and product displays",
        UsageContext.GAMING: "Video game characters and assets",
        UsageContext.NFT: "Non-fungible token creation",
        UsageContext.VIRTUAL_PHOTOSHOOT: "AI-generated photoshoot content"
    }
    return descriptions.get(u, "")
