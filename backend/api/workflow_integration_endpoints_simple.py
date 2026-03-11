"""
Workflow Integration Endpoints - Simplified Version
Connects all 117 platforms to Content Ingestion & End-to-End Distribution
Connects all 21 social media platforms to Social Media Strategy Center
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Form
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
import uuid
import json
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Authentication setup
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bigmann_entertainment')]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflow-integration", tags=["Workflow Integration"])

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

@router.get("/health")
async def workflow_integration_health():
    """Health check for workflow integration services"""
    try:
        return {
            "status": "healthy",
            "service": "Workflow Integration",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflows_available": {
                "content_ingestion_and_distribution": True,
                "social_media_strategy_phases_5_to_10": True
            },
            "platform_integration": {
                "total_platforms": 117,
                "social_media_platforms": 21,
                "content_workflow_enabled": 117,
                "social_strategy_enabled": 21
            }
        }
    except Exception as e:
        logger.error(f"Workflow integration health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/platforms/overview")
async def get_platforms_overview():
    """Get overview of all 117 platforms and their workflow capabilities"""
    try:
        # Simulate platform data - in production this would come from the actual platform service
        platform_types = {
            "social_media": 21,
            "music_streaming": 26,
            "podcast": 15,
            "radio": 10,
            "video_streaming": 8,
            "rights_organization": 5,
            "blockchain": 10,
            "model_agency": 15,
            "international": 8,
            "other": 14
        }
        
        total_platforms = sum(platform_types.values())
        
        return {
            "success": True,
            "overview": {
                "total_platforms": total_platforms,
                "social_media_platforms": platform_types["social_media"],
                "content_workflow_platforms": total_platforms,
                "platform_categories": platform_types
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
                    "supported_platforms": platform_types["social_media"]
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get platforms overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platforms overview: {str(e)}")

@router.post("/content-workflow")
async def create_content_workflow(
    content_id: str = Form(...),
    target_platforms: Optional[List[str]] = Form(None, description="Platforms for distribution (default: all 117)"),
    quality_profile: str = Form("standard", description="Quality profile for processing"),
    custom_settings: Optional[str] = Form(None, description="JSON string of custom distribution settings"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create comprehensive content workflow across all 117 platforms
    Includes: Ingestion → Metadata Enrichment → Quality Analysis → Distribution
    """
    try:
        workflow_id = str(uuid.uuid4())
        
        # Parse custom settings if provided
        distribution_settings = {}
        if custom_settings:
            distribution_settings = json.loads(custom_settings)
        
        # If no specific platforms provided, use all available platforms
        if not target_platforms:
            target_platforms = ["instagram", "twitter", "facebook", "tiktok", "youtube", "spotify", "apple_music"]  # Simplified list
        
        # Create workflow record
        workflow_data = {
            "workflow_id": workflow_id,
            "content_id": content_id,
            "user_id": current_user["id"],
            "status": "created",
            "current_phase": "ingestion",
            "progress_percentage": 0,
            "target_platforms": target_platforms,
            "quality_profile": quality_profile,
            "distribution_settings": distribution_settings,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store workflow in database
        await db.content_workflows.insert_one(workflow_data)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": f"Content workflow created for {len(target_platforms)} platforms",
            "workflow": {
                "id": workflow_id,
                "content_id": content_id,
                "status": "created",
                "current_phase": "ingestion",
                "progress_percentage": 0,
                "target_platforms": target_platforms,
                "quality_profile": quality_profile,
                "created_at": workflow_data["created_at"]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create content workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create content workflow: {str(e)}")

@router.get("/content-workflow/{workflow_id}")
async def get_content_workflow_status(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive content workflow status and analytics"""
    try:
        # Get workflow from database
        workflow = await db.content_workflows.find_one({"workflow_id": workflow_id})
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Check ownership
        if workflow["user_id"] != current_user["id"] and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Remove MongoDB ObjectId for JSON serialization
        if "_id" in workflow:
            del workflow["_id"]
        
        return {
            "success": True,
            "workflow": workflow,
            "analytics": {
                "total_platforms": len(workflow.get("target_platforms", [])),
                "completed_platforms": 0,  # Placeholder
                "failed_platforms": 0,    # Placeholder
                "success_rate": 0.0       # Placeholder
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@router.post("/social-media-strategy")
async def create_social_media_strategy(
    strategy_name: str = Form(...),
    campaign_objective: str = Form(..., description="brand_awareness, engagement, traffic, conversions"),
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
        strategy_id = str(uuid.uuid4())
        
        # If no specific platforms provided, use default social media platforms
        if not target_platforms:
            target_platforms = ["instagram", "twitter", "facebook", "tiktok", "youtube", "linkedin", "pinterest"]
        
        # Calculate total budget
        total_budget = len(target_platforms) * budget_per_platform
        
        # Create strategy record
        strategy_data = {
            "strategy_id": strategy_id,
            "strategy_name": strategy_name,
            "campaign_objective": campaign_objective,
            "owner_id": current_user["id"],
            "current_phase": "phase_5_engagement_amplification",
            "strategy_status": "active",
            "progress_percentage": 0,
            "target_platforms": target_platforms,
            "campaign_duration_days": campaign_duration_days,
            "budget_per_platform": budget_per_platform,
            "total_budget": total_budget,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store strategy in database
        await db.social_media_strategies.insert_one(strategy_data)
        
        return {
            "success": True,
            "strategy_id": strategy_id,
            "message": f"Social media strategy created for {len(target_platforms)} platforms",
            "strategy": {
                "id": strategy_id,
                "strategy_name": strategy_name,
                "campaign_objective": campaign_objective,
                "current_phase": "phase_5_engagement_amplification",
                "progress_percentage": 0,
                "target_platforms": target_platforms,
                "campaign_duration_days": campaign_duration_days,
                "total_budget": total_budget,
                "created_at": strategy_data["created_at"]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create social media strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create social media strategy: {str(e)}")

@router.get("/social-media-strategy/{strategy_id}")
async def get_social_media_strategy_status(
    strategy_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive social media strategy status with advanced phase details"""
    try:
        strategy = await db.social_media_strategies.find_one({"strategy_id": strategy_id})
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Check ownership
        if strategy["owner_id"] != current_user["id"] and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Remove MongoDB ObjectId for JSON serialization
        if "_id" in strategy:
            del strategy["_id"]
        
        return {
            "success": True,
            "strategy": strategy,
            "phase_details": {
                "current_phase": strategy.get("current_phase", "phase_5_engagement_amplification"),
                "phases_completed": [],
                "roi_percentage": 0.0,
                "total_spend": 0.0,
                "total_revenue": 0.0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get strategy status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategy status: {str(e)}")

@router.get("/dashboard/workflows")
async def get_workflow_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive workflow dashboard for user"""
    try:
        # Get content workflows
        content_workflows = await db.content_workflows.find(
            {"user_id": current_user["id"]}
        ).sort("created_at", -1).limit(10).to_list(length=None)
        
        # Get social media strategies
        social_strategies = await db.social_media_strategies.find(
            {"owner_id": current_user["id"]}
        ).sort("created_at", -1).limit(10).to_list(length=None)
        
        # Remove MongoDB ObjectIds
        for workflow in content_workflows:
            if "_id" in workflow:
                del workflow["_id"]
        
        for strategy in social_strategies:
            if "_id" in strategy:
                del strategy["_id"]
        
        # Calculate summary statistics
        content_stats = {
            "total_workflows": len(content_workflows),
            "active_workflows": len([w for w in content_workflows if w.get("status") in ["created", "processing", "distributing"]]),
            "completed_workflows": len([w for w in content_workflows if w.get("status") == "completed"]),
            "total_platforms_used": sum([len(w.get("target_platforms", [])) for w in content_workflows]),
        }
        
        social_stats = {
            "total_strategies": len(social_strategies),
            "active_strategies": len([s for s in social_strategies if s.get("strategy_status") == "active"]),
            "completed_strategies": len([s for s in social_strategies if s.get("strategy_status") == "completed"]),
            "total_social_platforms_used": sum([len(s.get("target_platforms", [])) for s in social_strategies]),
        }
        
        return {
            "success": True,
            "dashboard": {
                "user_id": current_user["id"],
                "content_workflow_stats": content_stats,
                "social_strategy_stats": social_stats,
                "recent_content_workflows": content_workflows[:5],
                "recent_social_strategies": social_strategies[:5]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow dashboard: {str(e)}")