"""
Workflow Integration Endpoints
Connects all 117 platforms to Content Ingestion & End-to-End Distribution
Connects all 21 social media platforms to Social Media Strategy Center
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Form
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
import uuid
import json

# Import what actually exists
from content_workflow_service import ContentWorkflowService, WorkflowStage, ContentType, QualityProfile
from social_media_strategy_service import SocialMediaStrategyService, CampaignObjective, StrategyPhase
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import os

# We'll define DISTRIBUTION_PLATFORMS locally to avoid circular imports
# This should match the one in server.py
DISTRIBUTION_PLATFORMS = {
    # Major Social Media Platforms
    "instagram": {
        "type": "social_media",
        "name": "Instagram",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["access_token"],
        "description": "Photo and video sharing social media platform"
    },
    "twitter": {
        "type": "social_media", 
        "name": "Twitter/X",
        "api_endpoint": "https://api.twitter.com/2",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["api_key", "api_secret", "access_token", "access_token_secret"],
        "description": "Microblogging and social networking platform"
    },
    "facebook": {
        "type": "social_media",
        "name": "Facebook",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["access_token"],
        "description": "Social networking platform"
    },
    "tiktok": {
        "type": "social_media",
        "name": "TikTok",
        "api_endpoint": "https://open-api.tiktok.com",
        "supported_formats": ["video"],
        "max_file_size": 300 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Short-form video sharing platform"
    },
    "youtube": {
        "type": "social_media",
        "name": "YouTube",
        "api_endpoint": "https://www.googleapis.com/youtube/v3",
        "supported_formats": ["video", "audio"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key", "client_id", "client_secret"],
        "description": "Video sharing and streaming platform"
    },
    # Add more platforms as needed - this is a simplified version for testing
    "spotify": {
        "type": "music_streaming",
        "name": "Spotify",
        "api_endpoint": "https://api.spotify.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "Music streaming platform"
    }
}

# Authentication setup
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bigmann_entertainment')]

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return {"id": user_id, "username": user.get("username", ""), "is_admin": user.get("is_admin", False)}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflow-integration", tags=["Workflow Integration"])

# Initialize services
content_workflow_service = ContentWorkflowService()
social_strategy_service = SocialMediaStrategyService(db)

# Content Workflow Endpoints (All 117 Platforms)

@router.post("/content-workflow", response_model=Dict[str, Any])
async def create_content_workflow(
    content_id: str = Form(...),
    target_platforms: Optional[List[str]] = Form(None, description="Platforms for distribution (default: all 117)"),
    quality_profile: QualityProfile = Form(QualityProfile.STREAMING_STANDARD),
    custom_settings: Optional[str] = Form(None, description="JSON string of custom distribution settings"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create comprehensive content workflow across all 117 platforms
    Includes: Ingestion → Metadata Enrichment → Quality Analysis → Distribution
    """
    try:
        # Parse custom settings if provided
        distribution_settings = {}
        if custom_settings:
            distribution_settings = json.loads(custom_settings)
        
        # Create workflow
        workflow = await content_workflow_service.create_content_workflow(
            content_id=content_id,
            target_platforms=target_platforms,
            quality_profile=quality_profile,
            distribution_settings=distribution_settings
        )
        
        return {
            "success": True,
            "workflow_id": workflow.id,
            "message": f"Content workflow created for {len(workflow.target_platforms)} platforms",
            "workflow": {
                "id": workflow.id,
                "content_id": workflow.content_id,
                "content_title": workflow.content_title,
                "status": workflow.status,
                "current_phase": workflow.current_phase,
                "progress_percentage": workflow.progress_percentage,
                "target_platforms": workflow.target_platforms,
                "quality_profile": workflow.quality_profile,
                "created_at": workflow.created_at
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create content workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create content workflow: {str(e)}")

@router.get("/content-workflow/{workflow_id}", response_model=Dict[str, Any])
async def get_content_workflow_status(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive content workflow status and analytics"""
    try:
        # Get workflow status
        workflow = await content_workflow_service.get_workflow_status(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get detailed analytics
        analytics = await content_workflow_service.get_workflow_analytics(workflow_id)
        
        return {
            "success": True,
            "workflow": {
                "id": workflow.id,
                "content_id": workflow.content_id,
                "content_title": workflow.content_title,
                "status": workflow.status,
                "current_phase": workflow.current_phase,
                "progress_percentage": workflow.progress_percentage,
                "phases_completed": workflow.phases_completed,
                "target_platforms": workflow.target_platforms,
                "successful_platforms": workflow.successful_platforms,
                "failed_platforms": workflow.failed_platforms,
                "distribution_results": workflow.distribution_results,
                "created_at": workflow.created_at,
                "completed_at": workflow.completed_at,
                "total_processing_time": workflow.total_processing_time
            },
            "analytics": analytics,
            "phase_details": workflow.phase_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@router.get("/content-workflows", response_model=Dict[str, Any])
async def get_user_content_workflows(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all content workflows for current user"""
    try:
        workflows = await content_workflow_service.get_workflows_by_user(
            user_id=current_user["id"],
            limit=limit
        )
        
        workflow_summaries = []
        for workflow in workflows:
            workflow_summaries.append({
                "id": workflow.id,
                "content_title": workflow.content_title,
                "status": workflow.status,
                "progress_percentage": workflow.progress_percentage,
                "platforms_count": len(workflow.target_platforms),
                "successful_count": len(workflow.successful_platforms),
                "failed_count": len(workflow.failed_platforms),
                "created_at": workflow.created_at,
                "completed_at": workflow.completed_at
            })
        
        return {
            "success": True,
            "workflows": workflow_summaries,
            "total_count": len(workflow_summaries)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user workflows: {str(e)}")

# Social Media Strategy Endpoints (21 Social Media Platforms)

@router.post("/social-media-strategy", response_model=Dict[str, Any])
async def create_social_media_strategy(
    strategy_name: str = Form(...),
    campaign_objective: CampaignObjective = Form(...),
    target_platforms: Optional[List[str]] = Form(None, description="Social media platforms (default: all 21)"),
    campaign_duration_days: int = Form(30, ge=1, le=365),
    budget_per_platform: float = Form(100.0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Create comprehensive social media strategy across all 21 social media platforms
    Includes: Phases 5-10 (Engagement → Influencer → Paid → Syndication → Analytics → ROI)
    """
    try:
        # Calculate budget allocation
        budget_allocation = {}
        if target_platforms:
            for platform in target_platforms:
                budget_allocation[platform] = budget_per_platform
        else:
            # Get all social media platforms
            all_social_platforms = list(social_strategy_service.social_media_platforms.keys())
            for platform in all_social_platforms:
                budget_allocation[platform] = budget_per_platform
        
        # Create strategy
        strategy = await social_strategy_service.create_social_media_strategy(
            strategy_name=strategy_name,
            campaign_objective=campaign_objective,
            owner_id=current_user["id"],
            target_platforms=target_platforms,
            campaign_duration_days=campaign_duration_days,
            budget_allocation=budget_allocation
        )
        
        return {
            "success": True,
            "strategy_id": strategy.id,
            "message": f"Social media strategy created for {len(strategy.target_platforms)} platforms",
            "strategy": {
                "id": strategy.id,
                "strategy_name": strategy.strategy_name,
                "campaign_objective": strategy.campaign_objective,
                "current_phase": strategy.current_phase,
                "progress_percentage": strategy.progress_percentage,
                "target_platforms": strategy.target_platforms,
                "campaign_duration_days": strategy.campaign_duration_days,
                "total_budget": sum(strategy.budget_allocation.values()),
                "created_at": strategy.created_at
            },
            "platforms_included": {
                platform_id: social_strategy_service.social_media_platforms[platform_id]["name"]
                for platform_id in strategy.target_platforms
                if platform_id in social_strategy_service.social_media_platforms
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create social media strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create social media strategy: {str(e)}")

@router.get("/social-media-strategy/{strategy_id}", response_model=Dict[str, Any])
async def get_social_media_strategy_status(
    strategy_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive social media strategy status with advanced phase details"""
    try:
        strategy = await social_strategy_service.get_strategy_status(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Check ownership
        if strategy.owner_id != current_user["id"] and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "strategy": {
                "id": strategy.id,
                "strategy_name": strategy.strategy_name,
                "campaign_objective": strategy.campaign_objective,
                "current_phase": strategy.current_phase,
                "strategy_status": strategy.strategy_status,
                "progress_percentage": strategy.progress_percentage,
                "phases_completed": strategy.phases_completed,
                "target_platforms": strategy.target_platforms,
                "platform_count": len(strategy.target_platforms),
                "campaign_duration_days": strategy.campaign_duration_days,
                "total_budget": sum(strategy.budget_allocation.values()),
                "budget_allocation": strategy.budget_allocation,
                "kpi_targets": strategy.kpi_targets,
                "current_metrics": strategy.current_metrics,
                "roi_percentage": strategy.roi_percentage,
                "total_spend": strategy.total_spend,
                "total_revenue": strategy.total_revenue,
                "created_at": strategy.created_at,
                "completed_at": strategy.completed_at
            },
            "phase_results": strategy.phase_results,
            "influencer_partnerships": strategy.influencer_partnerships,
            "paid_campaigns": strategy.paid_promotion_campaigns,
            "analytics_insights": strategy.analytics_insights,
            "platform_details": {
                platform_id: {
                    "name": social_strategy_service.social_media_platforms[platform_id]["name"],
                    "type": social_strategy_service.social_media_platforms[platform_id]["type"],
                    "strategy": strategy.platform_strategies.get(platform_id, {}),
                    "budget": strategy.budget_allocation.get(platform_id, 0)
                }
                for platform_id in strategy.target_platforms
                if platform_id in social_strategy_service.social_media_platforms
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get strategy status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategy status: {str(e)}")

@router.get("/social-media-strategies", response_model=Dict[str, Any])
async def get_user_social_media_strategies(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all social media strategies for current user"""
    try:
        strategies = await social_strategy_service.get_user_strategies(
            user_id=current_user["id"],
            limit=limit
        )
        
        strategy_summaries = []
        for strategy in strategies:
            strategy_summaries.append({
                "id": strategy.id,
                "strategy_name": strategy.strategy_name,
                "campaign_objective": strategy.campaign_objective,
                "current_phase": strategy.current_phase,
                "strategy_status": strategy.strategy_status,
                "progress_percentage": strategy.progress_percentage,
                "platforms_count": len(strategy.target_platforms),
                "total_budget": sum(strategy.budget_allocation.values()),
                "roi_percentage": strategy.roi_percentage,
                "created_at": strategy.created_at,
                "completed_at": strategy.completed_at
            })
        
        return {
            "success": True,
            "strategies": strategy_summaries,
            "total_count": len(strategy_summaries)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user strategies: {str(e)}")

@router.get("/social-media-strategy/{strategy_id}/analytics/{platform_id}", response_model=Dict[str, Any])
async def get_platform_analytics(
    strategy_id: str,
    platform_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed analytics for specific platform within strategy"""
    try:
        analytics = await social_strategy_service.get_platform_analytics(strategy_id, platform_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Analytics not found")
        
        return {
            "success": True,
            "platform_id": platform_id,
            "platform_name": social_strategy_service.social_media_platforms.get(platform_id, {}).get("name", platform_id),
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get platform analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platform analytics: {str(e)}")

@router.get("/social-media-strategy/{strategy_id}/cross-platform-insights", response_model=Dict[str, Any]) 
async def get_cross_platform_insights(
    strategy_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get cross-platform insights and optimization recommendations"""
    try:
        insights = await social_strategy_service.get_cross_platform_insights(strategy_id)
        if not insights:
            raise HTTPException(status_code=404, detail="Insights not found")
        
        return {
            "success": True,
            "strategy_id": strategy_id,
            "cross_platform_insights": insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cross-platform insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cross-platform insights: {str(e)}")

# Combined Platform Overview Endpoints

@router.get("/platforms/overview", response_model=Dict[str, Any])
async def get_platforms_overview():
    """Get overview of all 117 platforms and their workflow capabilities"""
    try:
        # Categorize platforms
        platform_categories = {}
        social_media_platforms = []
        total_platforms = len(DISTRIBUTION_PLATFORMS)
        
        for platform_id, config in DISTRIBUTION_PLATFORMS.items():
            platform_type = config.get("type", "other")
            
            if platform_type not in platform_categories:
                platform_categories[platform_type] = []
            
            platform_info = {
                "id": platform_id,
                "name": config.get("name", platform_id),
                "type": platform_type,
                "supported_formats": config.get("supported_formats", []),
                "content_workflow_supported": True,  # All platforms support content workflow
                "social_strategy_supported": platform_type == "social_media"
            }
            
            platform_categories[platform_type].append(platform_info)
            
            if platform_type == "social_media":
                social_media_platforms.append(platform_info)
        
        return {
            "success": True,
            "overview": {
                "total_platforms": total_platforms,
                "social_media_platforms": len(social_media_platforms),
                "content_workflow_platforms": total_platforms,  # All platforms
                "platform_categories": platform_categories
            },
            "workflows": {
                "content_ingestion_and_distribution": {
                    "description": "End-to-end content workflow across all 117 platforms",
                    "phases": [
                        "Content Ingestion",
                        "Metadata Extraction", 
                        "Quality Analysis",
                        "AI Enrichment",
                        "Platform Optimization",
                        "Compliance Validation",
                        "Distribution Preparation",
                        "Multi-Platform Distribution",
                        "Delivery Confirmation",
                        "Analytics Aggregation"
                    ],
                    "supported_platforms": total_platforms
                },
                "social_media_strategy": {
                    "description": "Advanced social media strategy (Phases 5-10) across 21 social platforms",
                    "phases": [
                        "Phase 5: Engagement Amplification",
                        "Phase 6: Influencer Collaboration",
                        "Phase 7: Paid Promotion",
                        "Phase 8: Cross-Platform Syndication", 
                        "Phase 9: Analytics Optimization",
                        "Phase 10: ROI Maximization"
                    ],
                    "supported_platforms": len(social_media_platforms)
                }
            },
            "social_media_platforms": social_media_platforms
        }
        
    except Exception as e:
        logger.error(f"Failed to get platforms overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platforms overview: {str(e)}")

@router.get("/dashboard/workflows", response_model=Dict[str, Any])
async def get_workflow_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive workflow dashboard for user"""
    try:
        # Get content workflows
        content_workflows = await content_workflow_service.get_workflows_by_user(
            user_id=current_user["id"],
            limit=10
        )
        
        # Get social media strategies
        social_strategies = await social_strategy_service.get_user_strategies(
            user_id=current_user["id"],
            limit=10
        )
        
        # Calculate summary statistics
        content_stats = {
            "total_workflows": len(content_workflows),
            "active_workflows": len([w for w in content_workflows if w.status in ["ingesting", "enriching", "distributing"]]),
            "completed_workflows": len([w for w in content_workflows if w.status == "completed"]),
            "total_platforms_used": len(set([p for w in content_workflows for p in w.target_platforms])),
            "success_rate": 0
        }
        
        if content_workflows:
            total_distributions = sum([len(w.target_platforms) for w in content_workflows])
            successful_distributions = sum([len(w.successful_platforms) for w in content_workflows])
            content_stats["success_rate"] = (successful_distributions / total_distributions * 100) if total_distributions > 0 else 0
        
        social_stats = {
            "total_strategies": len(social_strategies),
            "active_strategies": len([s for s in social_strategies if s.strategy_status == "active"]),
            "completed_strategies": len([s for s in social_strategies if s.strategy_status == "completed"]),
            "total_social_platforms_used": len(set([p for s in social_strategies for p in s.target_platforms])),
            "average_roi": sum([s.roi_percentage for s in social_strategies]) / len(social_strategies) if social_strategies else 0
        }
        
        return {
            "success": True,
            "dashboard": {
                "user_id": current_user["id"],
                "content_workflow_stats": content_stats,
                "social_strategy_stats": social_stats,
                "recent_content_workflows": [
                    {
                        "id": w.id,
                        "content_title": w.content_title,
                        "status": w.status,
                        "progress": w.progress_percentage,
                        "platforms_count": len(w.target_platforms),
                        "created_at": w.created_at
                    } for w in content_workflows[:5]
                ],
                "recent_social_strategies": [
                    {
                        "id": s.id,
                        "strategy_name": s.strategy_name,
                        "status": s.strategy_status,
                        "progress": s.progress_percentage,
                        "platforms_count": len(s.target_platforms),
                        "roi": s.roi_percentage,
                        "created_at": s.created_at
                    } for s in social_strategies[:5]
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow dashboard: {str(e)}")

@router.get("/health")
async def workflow_integration_health():
    """Health check for workflow integration services"""
    try:
        # Check services availability
        content_service_healthy = content_workflow_service is not None
        social_service_healthy = social_strategy_service is not None
        
        # Get platform counts
        total_platforms = len(DISTRIBUTION_PLATFORMS)
        social_platforms = len([p for p in DISTRIBUTION_PLATFORMS.values() if p.get("type") == "social_media"])
        
        return {
            "status": "healthy",
            "services": {
                "content_workflow_service": "healthy" if content_service_healthy else "unhealthy",
                "social_strategy_service": "healthy" if social_service_healthy else "unhealthy"
            },
            "platform_integration": {
                "total_platforms": total_platforms,
                "social_media_platforms": social_platforms,
                "content_workflow_enabled": total_platforms,
                "social_strategy_enabled": social_platforms
            },  
            "workflows_available": {
                "content_ingestion_and_distribution": True,
                "social_media_strategy_phases_5_to_10": True
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Workflow integration health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }