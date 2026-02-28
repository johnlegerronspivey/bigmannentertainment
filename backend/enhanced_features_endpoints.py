"""
Enhanced Features API Endpoints
- AI Release Optimization
- Social Platform Distribution
- Smart Royalty Routing
- Metadata & Cover Art Automation
- Global Market Support
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid

from enhanced_features_models import (
    ReleaseOptimizationRequest,
    ReleaseOptimization,
    SocialDistributionRequest,
    SocialDistribution,
    RoyaltyRouting,
    RoyaltySplit,
    RoyaltyTransaction,
    MetadataAutoFillRequest,
    CoverArtGenerationRequest,
    AutomatedMetadata,
    GlobalMarketConfig,
    GlobalMarket,
    MarketPerformance,
    EnhancedFeaturesDashboard
)

from enhanced_features_service import (
    AIReleaseOptimizationService,
    CoverArtAutomationService,
    GlobalMarketService,
    RoyaltyRoutingService
)

router = APIRouter(prefix="/enhanced", tags=["Enhanced Features"])

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bigmann_entertainment_production')]


# ============== AI-Powered Release Optimization Endpoints ==============

@router.post("/ai-optimization/analyze", response_model=ReleaseOptimization)
async def analyze_release_optimization(request: ReleaseOptimizationRequest):
    """
    Analyze release and get AI-powered platform recommendations using GPT-5
    """
    try:
        service = AIReleaseOptimizationService()
        optimization = await service.analyze_release(request)
        
        # Save to database
        optimization_dict = optimization.dict()
        optimization_dict['created_at'] = optimization_dict['created_at'].isoformat()
        optimization_dict['updated_at'] = optimization_dict['updated_at'].isoformat()
        
        await db.release_optimizations.insert_one(optimization_dict)
        
        return optimization
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI optimization failed: {str(e)}")


@router.get("/ai-optimization/{optimization_id}", response_model=ReleaseOptimization)
async def get_release_optimization(optimization_id: str):
    """Get AI optimization result by ID"""
    
    optimization = await db.release_optimizations.find_one({"id": optimization_id})
    
    if not optimization:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    return ReleaseOptimization(**optimization)


@router.get("/ai-optimization/release/{release_id}")
async def get_optimizations_by_release(release_id: str):
    """Get all AI optimizations for a specific release"""
    
    optimizations = await db.release_optimizations.find(
        {"release_id": release_id}
    ).sort("created_at", -1).to_list(length=100)
    
    return {
        "release_id": release_id,
        "total_analyses": len(optimizations),
        "optimizations": optimizations
    }


# ============== Social Platform Native Distribution Endpoints ==============

@router.post("/social-distribution/create", response_model=SocialDistribution)
async def create_social_distribution(request: SocialDistributionRequest):
    """
    Create native distribution to social platforms (TikTok, YouTube Shorts, Instagram Reels)
    """
    try:
        distributions = []
        
        for platform in request.platforms:
            distribution = SocialDistribution(
                media_id=request.media_id,
                platform=platform,
                status="pending",
                caption=request.caption,
                hashtags=request.hashtags,
                scheduled_time=request.scheduled_time
            )
            
            distribution_dict = distribution.dict()
            distribution_dict['created_at'] = distribution_dict['created_at'].isoformat()
            distribution_dict['updated_at'] = distribution_dict['updated_at'].isoformat()
            if distribution_dict.get('scheduled_time'):
                distribution_dict['scheduled_time'] = distribution_dict['scheduled_time'].isoformat()
            if distribution_dict.get('published_at'):
                distribution_dict['published_at'] = distribution_dict['published_at'].isoformat()
            
            await db.social_distributions.insert_one(distribution_dict)
            distributions.append(distribution)
        
        return distributions[0] if distributions else None
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Distribution creation failed: {str(e)}")


@router.get("/social-distribution/{distribution_id}")
async def get_social_distribution(distribution_id: str):
    """Get social distribution status"""
    
    distribution = await db.social_distributions.find_one({"id": distribution_id})
    
    if not distribution:
        raise HTTPException(status_code=404, detail="Distribution not found")
    
    return distribution


@router.get("/social-distribution/media/{media_id}")
async def get_distributions_by_media(media_id: str):
    """Get all distributions for a specific media"""
    
    distributions = await db.social_distributions.find(
        {"media_id": media_id}
    ).sort("created_at", -1).to_list(length=100)
    
    return {
        "media_id": media_id,
        "total_distributions": len(distributions),
        "distributions": distributions
    }


@router.put("/social-distribution/{distribution_id}/update-metrics")
async def update_distribution_metrics(
    distribution_id: str,
    views: int = 0,
    likes: int = 0,
    shares: int = 0,
    comments: int = 0
):
    """Update engagement metrics for a distribution"""
    
    result = await db.social_distributions.update_one(
        {"id": distribution_id},
        {
            "$set": {
                "views": views,
                "likes": likes,
                "shares": shares,
                "comments": comments,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Distribution not found")
    
    return {"success": True, "message": "Metrics updated"}


# ============== Smart Royalty Routing & Splits Endpoints ==============

@router.post("/royalty-routing/create", response_model=RoyaltyRouting)
async def create_royalty_routing(routing: RoyaltyRouting):
    """Create smart royalty routing configuration"""
    
    # Validate splits
    splits_dict = [split.dict() for split in routing.splits]
    is_valid, message = RoyaltyRoutingService.validate_splits(splits_dict)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    routing_dict = routing.dict()
    routing_dict['created_at'] = routing_dict['created_at'].isoformat()
    routing_dict['updated_at'] = routing_dict['updated_at'].isoformat()
    
    await db.royalty_routings.insert_one(routing_dict)
    
    return routing


@router.get("/royalty-routing/{routing_id}")
async def get_royalty_routing(routing_id: str):
    """Get royalty routing configuration"""
    
    routing = await db.royalty_routings.find_one({"id": routing_id})
    
    if not routing:
        raise HTTPException(status_code=404, detail="Routing configuration not found")
    
    return routing


@router.get("/royalty-routing/release/{release_id}")
async def get_routing_by_release(release_id: str):
    """Get royalty routing for a specific release"""
    
    routing = await db.royalty_routings.find_one({"release_id": release_id})
    
    if not routing:
        raise HTTPException(status_code=404, detail="No routing configuration found for this release")
    
    return routing


@router.post("/royalty-routing/transaction/create")
async def create_royalty_transaction(
    routing_id: str,
    platform: str,
    revenue_amount: float,
    currency: str = "USD"
):
    """Create and process royalty transaction"""
    
    # Get routing configuration
    routing = await db.royalty_routings.find_one({"id": routing_id})
    
    if not routing:
        raise HTTPException(status_code=404, detail="Routing configuration not found")
    
    # Calculate splits
    splits = routing.get("splits", [])
    payments = RoyaltyRoutingService.calculate_splits(revenue_amount, splits)
    
    # Create transaction
    transaction = RoyaltyTransaction(
        routing_id=routing_id,
        platform=platform,
        revenue_amount=revenue_amount,
        currency=currency,
        collaborator_payments=payments,
        reconciliation_status="completed" if routing.get("auto_reconciliation") else "pending"
    )
    
    transaction_dict = transaction.dict()
    transaction_dict['transaction_date'] = transaction_dict['transaction_date'].isoformat()
    transaction_dict['created_at'] = transaction_dict['created_at'].isoformat()
    
    await db.royalty_transactions.insert_one(transaction_dict)
    
    return transaction


@router.get("/royalty-routing/{routing_id}/transactions")
async def get_routing_transactions(routing_id: str):
    """Get all transactions for a routing configuration"""
    
    transactions = await db.royalty_transactions.find(
        {"routing_id": routing_id}
    ).sort("transaction_date", -1).to_list(length=1000)
    
    total_revenue = sum(t.get("revenue_amount", 0) for t in transactions)
    
    return {
        "routing_id": routing_id,
        "total_transactions": len(transactions),
        "total_revenue": total_revenue,
        "transactions": transactions
    }


# ============== Metadata & Cover Art Automation Endpoints ==============

@router.post("/metadata/generate-cover-art")
async def generate_cover_art(request: CoverArtGenerationRequest):
    """Generate AI-powered cover art using gpt-image-1"""
    
    try:
        service = CoverArtAutomationService()
        result = await service.generate_cover_art(request)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate cover art"))
        
        return {
            "success": True,
            "image_base64": result["image_base64"],
            "prompt_used": result["prompt_used"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover art generation failed: {str(e)}")


@router.post("/metadata/auto-generate")
async def auto_generate_metadata(request: MetadataAutoFillRequest):
    """Auto-generate metadata using AI"""
    
    try:
        service = CoverArtAutomationService()
        
        # Generate metadata
        metadata_suggestions = await service.generate_metadata(
            track_title=request.track_title or "Unknown Track",
            artist_name=request.artist_name or "Unknown Artist",
            genre=request.genre or "Unknown"
        )
        
        # Generate cover art if requested
        cover_art_base64 = None
        if request.ai_enhance:
            cover_result = await service.generate_cover_art(
                CoverArtGenerationRequest(
                    track_title=request.track_title or "Unknown Track",
                    artist_name=request.artist_name or "Unknown Artist",
                    genre=request.genre or "Unknown",
                    mood=metadata_suggestions.get("mood")
                )
            )
            if cover_result.get("success"):
                cover_art_base64 = cover_result["image_base64"]
        
        # Create automated metadata record
        automated_metadata = AutomatedMetadata(
            track_id=str(uuid.uuid4()),
            title=request.track_title or "Unknown Track",
            artist=request.artist_name or "Unknown Artist",
            genre=request.genre or "Unknown",
            mood=metadata_suggestions.get("mood"),
            ai_generated_tags=metadata_suggestions.get("tags", []),
            cover_art_base64=cover_art_base64,
            validation_status="pending"
        )
        
        metadata_dict = automated_metadata.dict()
        metadata_dict['created_at'] = metadata_dict['created_at'].isoformat()
        metadata_dict['updated_at'] = metadata_dict['updated_at'].isoformat()
        
        await db.automated_metadata.insert_one(metadata_dict)
        
        return {
            "success": True,
            "metadata": metadata_dict,
            "suggestions": metadata_suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata generation failed: {str(e)}")


@router.get("/metadata/{metadata_id}")
async def get_automated_metadata(metadata_id: str):
    """Get automated metadata by ID"""
    
    metadata = await db.automated_metadata.find_one({"id": metadata_id})
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata not found")
    
    return metadata


# ============== Global Market Support Endpoints ==============

@router.post("/global-market/configure", response_model=GlobalMarketConfig)
async def configure_global_market(config: GlobalMarketConfig):
    """Configure global market support for a release"""
    
    service = GlobalMarketService()
    
    # Auto-populate region-specific platforms
    region_platforms = {}
    for market in config.enabled_markets:
        platforms = service.get_market_platforms(market.value)
        region_platforms[market.value] = platforms
    
    config.region_specific_platforms = region_platforms
    
    config_dict = config.dict()
    config_dict['created_at'] = config_dict['created_at'].isoformat()
    config_dict['updated_at'] = config_dict['updated_at'].isoformat()
    
    await db.global_market_configs.insert_one(config_dict)
    
    return config


@router.get("/global-market/config/{release_id}")
async def get_global_market_config(release_id: str):
    """Get global market configuration for a release"""
    
    config = await db.global_market_configs.find_one({"release_id": release_id})
    
    if not config:
        raise HTTPException(status_code=404, detail="Global market configuration not found")
    
    return config


@router.post("/global-market/localize-metadata")
async def localize_metadata(
    release_id: str,
    track_title: str,
    artist_name: str,
    target_market: str
):
    """Generate localized metadata for a target market using AI"""
    
    try:
        service = GlobalMarketService()
        localized = await service.generate_localized_metadata(
            track_title=track_title,
            artist_name=artist_name,
            target_market=target_market
        )
        
        # Update global market config with localized metadata
        await db.global_market_configs.update_one(
            {"release_id": release_id},
            {
                "$set": {
                    f"localized_metadata.{target_market}": localized,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "market": target_market,
            "localized_metadata": localized
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Localization failed: {str(e)}")


@router.get("/global-market/performance/{release_id}")
async def get_market_performance(release_id: str):
    """Get performance data across global markets"""
    
    performances = await db.market_performances.find(
        {"release_id": release_id}
    ).to_list(length=100)
    
    total_streams = sum(p.get("total_streams", 0) for p in performances)
    total_revenue = sum(p.get("total_revenue", 0) for p in performances)
    
    return {
        "release_id": release_id,
        "total_markets": len(performances),
        "total_streams": total_streams,
        "total_revenue": total_revenue,
        "market_breakdown": performances
    }


# ============== Dashboard & Health Endpoints ==============

@router.get("/dashboard")
async def get_enhanced_features_dashboard(user_id: str):
    """Get consolidated dashboard for all enhanced features"""
    
    # Aggregate data from all collections
    ai_optimizations = await db.release_optimizations.count_documents({"user_id": user_id})
    social_distributions = await db.social_distributions.count_documents({"user_id": user_id})
    active_routings = await db.royalty_routings.count_documents({"user_id": user_id, "status": "active"})
    automated_metadata = await db.automated_metadata.count_documents({"user_id": user_id})
    
    # Get global market configs count
    global_configs = await db.global_market_configs.find(
        {"user_id": user_id}
    ).to_list(length=100)
    enabled_markets = sum(len(c.get("enabled_markets", [])) for c in global_configs)
    
    # Calculate totals
    distributions = await db.social_distributions.find(
        {"user_id": user_id}
    ).to_list(length=1000)
    total_reach = sum(d.get("views", 0) for d in distributions)
    
    transactions = await db.royalty_transactions.count_documents({"user_id": user_id})
    
    dashboard = EnhancedFeaturesDashboard(
        user_id=user_id,
        ai_optimization_count=ai_optimizations,
        social_distributions_count=social_distributions,
        active_royalty_routings=active_routings,
        automated_metadata_count=automated_metadata,
        enabled_global_markets=enabled_markets,
        total_ai_insights_generated=ai_optimizations,
        total_cover_arts_generated=automated_metadata,
        total_social_reach=total_reach,
        total_royalty_transactions=transactions
    )
    
    return dashboard


@router.get("/health")
async def enhanced_features_health():
    """Health check for enhanced features system"""
    
    return {
        "status": "healthy",
        "service": "enhanced_features",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": {
            "ai_release_optimization": "enabled",
            "social_platform_distribution": "enabled",
            "smart_royalty_routing": "enabled",
            "metadata_automation": "enabled",
            "cover_art_generation": "enabled",
            "global_market_support": "enabled"
        },
        "ai_integration": {
            "gpt5_text": "configured",
            "gpt_image1": "configured",
            "llm_key": "active"
        }
    }
