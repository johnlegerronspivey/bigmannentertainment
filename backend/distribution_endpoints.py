"""
Distribution API Endpoints - Function 3: Content Distribution & Delivery Management
Provides API endpoints for content distribution, delivery optimization, and analytics.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import json
import uuid

from delivery_optimization_service import (
    DeliveryOptimizationService,
    DeliveryStrategy,
    OptimizationGoal,
    DeliveryPlan,
    DeliveryAnalytics,
    PlatformType
)
from distribution_service import DistributionService

# Initialize services
delivery_optimization_service = DeliveryOptimizationService()
# We'll access the existing distribution service through the database
# since it's already initialized in the main server

# Create router
router = APIRouter(prefix="/api/distribution", tags=["Content Distribution & Delivery Management"])
security = HTTPBearer()

# Request models
class DeliveryPlanRequest(BaseModel):
    content_id: str
    target_platforms: List[str]
    strategy: DeliveryStrategy = DeliveryStrategy.OPTIMIZED_TIMING
    optimization_goal: OptimizationGoal = OptimizationGoal.MAX_REACH
    target_timezone: str = "UTC"
    content_type: str = "music"

class DistributionJobRequest(BaseModel):
    content_id: str
    content_title: str
    main_artist: str
    content_type: str
    target_platforms: List[str]
    strategy: DeliveryStrategy = DeliveryStrategy.OPTIMIZED_TIMING
    optimization_goal: OptimizationGoal = OptimizationGoal.MAX_REACH
    scheduled_delivery: Optional[datetime] = None
    priority: str = "medium"
    metadata: Optional[Dict[str, Any]] = None

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This would integrate with your authentication system
    # For now, returning a mock user ID
    return "user_123"

# Delivery Optimization Endpoints

@router.post("/delivery-plans/create")
async def create_delivery_plan(
    request: DeliveryPlanRequest,
    user_id: str = Depends(get_current_user)
):
    """Create an optimized delivery plan for content distribution"""
    try:
        delivery_plan = await delivery_optimization_service.create_delivery_plan(
            user_id=user_id,
            content_id=request.content_id,
            target_platforms=request.target_platforms,
            strategy=request.strategy,
            optimization_goal=request.optimization_goal,
            target_timezone=request.target_timezone,
            content_type=request.content_type
        )
        
        return {
            "success": True,
            "delivery_plan": delivery_plan,
            "message": "Delivery plan created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delivery-plans/{plan_id}")
async def get_delivery_plan(
    plan_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get delivery plan details"""
    try:
        plan = await delivery_optimization_service.get_delivery_plan(plan_id, user_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="Delivery plan not found")
        
        return {
            "success": True,
            "delivery_plan": plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delivery-plans")
async def list_delivery_plans(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user)
):
    """List delivery plans for user"""
    try:
        plans = await delivery_optimization_service.list_user_delivery_plans(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "delivery_plans": plans,
            "total_plans": len(plans),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delivery-plans/{plan_id}/performance")
async def update_delivery_performance(
    plan_id: str,
    actual_reach: int,
    actual_revenue: float,
    user_id: str = Depends(get_current_user)
):
    """Update delivery plan with actual performance data"""
    try:
        success = await delivery_optimization_service.update_delivery_performance(
            plan_id, user_id, actual_reach, actual_revenue
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Delivery plan not found")
        
        return {
            "success": True,
            "message": "Performance data updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Platform Recommendation Endpoints

@router.get("/recommendations/platforms")
async def get_platform_recommendations(
    content_type: str = Query(..., description="Type of content (music, video, podcast, etc.)"),
    target_audience: str = Query("general", description="Target audience demographic"),
    budget_level: str = Query("medium", description="Budget level (low, medium, high)"),
    user_id: str = Depends(get_current_user)
):
    """Get platform recommendations based on content and audience"""
    try:
        recommendations = delivery_optimization_service.get_platform_recommendations(
            content_type=content_type,
            target_audience=target_audience,
            budget_level=budget_level
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "content_type": content_type,
            "target_audience": target_audience,
            "budget_level": budget_level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints

@router.get("/analytics/delivery-performance")
async def get_delivery_performance_analytics(
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get delivery performance analytics for user"""
    try:
        analytics = await delivery_optimization_service.analyze_delivery_performance(
            user_id=user_id,
            days=days
        )
        
        return {
            "success": True,
            "analytics": analytics,
            "period_days": days,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Distribution Status and Management Endpoints

@router.get("/platforms")
async def get_available_platforms(user_id: str = Depends(get_current_user)):
    """Get all available distribution platforms"""
    try:
        platforms = delivery_optimization_service.get_available_platforms()
        
        return {
            "success": True,
            "platforms": platforms,
            "total_platforms": len(platforms)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/by-type/{platform_type}")
async def get_platforms_by_type(
    platform_type: str,
    user_id: str = Depends(get_current_user)
):
    """Get platforms by type (streaming_music, streaming_video, social_media, etc.)"""
    try:
        from delivery_optimization_service import PlatformType
        
        # Convert string to enum
        try:
            platform_type_enum = PlatformType(platform_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid platform type: {platform_type}")
        
        platforms = delivery_optimization_service.get_platforms_by_type(platform_type_enum)
        
        return {
            "success": True,
            "platform_type": platform_type,
            "platforms": platforms,
            "total_platforms": len(platforms)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_delivery_strategies(user_id: str = Depends(get_current_user)):
    """Get available delivery strategies and their descriptions"""
    try:
        strategies = {
            "immediate": {
                "name": "Immediate",
                "description": "Distribute to all platforms simultaneously for maximum speed",
                "best_for": "Time-sensitive releases, breaking news content",
                "estimated_time": "Based on slowest platform",
                "risk_level": "Medium"
            },
            "optimized_timing": {
                "name": "Optimized Timing",
                "description": "Distribute at optimal times for each platform's audience",
                "best_for": "Maximum engagement and reach",
                "estimated_time": "1-3 days",
                "risk_level": "Low"
            },
            "staggered_release": {
                "name": "Staggered Release",
                "description": "Release to fastest platforms first, then progressively to others",
                "best_for": "Building momentum and managing resources",
                "estimated_time": "3-7 days",
                "risk_level": "Low"
            },
            "regional_rollout": {
                "name": "Regional Rollout",
                "description": "Prioritize platforms by regional reach and preferences",
                "best_for": "Region-specific content, international expansion",
                "estimated_time": "2-5 days",
                "risk_level": "Medium"
            },
            "test_and_scale": {
                "name": "Test and Scale",
                "description": "Start with high-success platforms, then expand based on results",
                "best_for": "New content creators, experimental content",
                "estimated_time": "5-10 days",
                "risk_level": "Low"
            }
        }
        
        return {
            "success": True,
            "strategies": strategies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimization-goals")
async def get_optimization_goals(user_id: str = Depends(get_current_user)):
    """Get available optimization goals and their descriptions"""
    try:
        goals = {
            "max_reach": {
                "name": "Maximum Reach",
                "description": "Prioritize platforms with largest audience bases",
                "focus": "Audience size and global reach",
                "typical_outcome": "Highest total impressions and views"
            },
            "max_revenue": {
                "name": "Maximum Revenue",
                "description": "Prioritize platforms with best revenue sharing",
                "focus": "Revenue per stream/view and monetization",
                "typical_outcome": "Highest earnings per engagement"
            },
            "fastest_delivery": {
                "name": "Fastest Delivery",
                "description": "Prioritize platforms with shortest processing times",
                "focus": "Speed to market and processing efficiency",
                "typical_outcome": "Content live across platforms quickly"
            },
            "quality_focused": {
                "name": "Quality Focused",
                "description": "Prioritize platforms with best engagement and success rates",
                "focus": "User engagement and platform reliability",
                "typical_outcome": "Higher quality interactions and loyalty"
            },
            "cost_effective": {
                "name": "Cost Effective",
                "description": "Optimize for best ROI and lowest delivery costs",
                "focus": "Cost efficiency and resource optimization",
                "typical_outcome": "Maximum results per dollar spent"
            }
        }
        
        return {
            "success": True,
            "optimization_goals": goals
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch Operations

@router.post("/delivery-plans/batch")
async def create_batch_delivery_plans(
    batch_request: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Create multiple delivery plans at once"""
    try:
        content_ids = batch_request.get("content_ids", [])
        target_platforms = batch_request.get("target_platforms", [])
        strategy = DeliveryStrategy(batch_request.get("strategy", "optimized_timing"))
        optimization_goal = OptimizationGoal(batch_request.get("optimization_goal", "max_reach"))
        
        created_plans = []
        failed_plans = []
        
        for i, content_id in enumerate(content_ids):
            try:
                delivery_plan = await delivery_optimization_service.create_delivery_plan(
                    user_id=user_id,
                    content_id=content_id,
                    target_platforms=target_platforms,
                    strategy=strategy,
                    optimization_goal=optimization_goal
                )
                
                created_plans.append({
                    "content_id": content_id,
                    "plan_id": delivery_plan.plan_id
                })
                
            except Exception as e:
                failed_plans.append({
                    "content_id": content_id,
                    "error": str(e)
                })
        
        return {
            "success": len(failed_plans) == 0,
            "created_plans": created_plans,
            "failed_plans": failed_plans,
            "total_requested": len(content_ids),
            "total_created": len(created_plans),
            "total_failed": len(failed_plans)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Health and Monitoring

@router.get("/health")
async def health_check():
    """Health check endpoint for distribution service"""
    try:
        health_status = {
            "service": "Content Distribution & Delivery Management API",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "3.0.0",
            "available_platforms": len(delivery_optimization_service.platform_audience_data),
            "supported_strategies": len(DeliveryStrategy),
            "supported_optimization_goals": len(OptimizationGoal)
        }
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }

# Distribution Job Integration (bridging with existing distribution service)

@router.post("/jobs/create-with-optimization")
async def create_distribution_job_with_optimization(
    content_id: str,
    content_title: str,
    main_artist: str,
    content_type: str,
    target_platforms: List[str],
    strategy: DeliveryStrategy = DeliveryStrategy.OPTIMIZED_TIMING,
    optimization_goal: OptimizationGoal = OptimizationGoal.MAX_REACH,
    scheduled_delivery: Optional[datetime] = None,
    priority: str = "medium",
    metadata: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user)
):
    """Create a distribution job with delivery optimization"""
    try:
        # First create an optimized delivery plan
        delivery_plan = await delivery_optimization_service.create_delivery_plan(
            user_id=user_id,
            content_id=content_id,
            target_platforms=target_platforms,
            strategy=strategy,
            optimization_goal=optimization_goal,
            content_type=content_type
        )
        
        # Use the optimized sequence for distribution
        optimized_platforms = delivery_plan.recommended_sequence or target_platforms
        
        # Create distribution job data (this would integrate with existing distribution service)
        distribution_job_data = {
            "job_id": str(uuid.uuid4()),
            "user_id": user_id,
            "content_id": content_id,
            "content_title": content_title,
            "main_artist": main_artist,
            "content_type": content_type,
            "target_platforms": optimized_platforms,
            "delivery_plan_id": delivery_plan.plan_id,
            "priority": priority,
            "scheduled_delivery": scheduled_delivery.isoformat() if scheduled_delivery else None,
            "metadata": metadata or {},
            "estimated_reach": delivery_plan.total_estimated_reach,
            "estimated_revenue": delivery_plan.total_estimated_revenue,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "distribution_job": distribution_job_data,
            "delivery_plan": delivery_plan,
            "optimization_applied": True,
            "message": "Distribution job created with optimization"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_distribution_dashboard(
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive distribution dashboard data"""
    try:
        # Get delivery analytics
        analytics = await delivery_optimization_service.analyze_delivery_performance(user_id, days)
        
        # Get recent delivery plans
        recent_plans = await delivery_optimization_service.list_user_delivery_plans(user_id, limit=10)
        
        # Get platform recommendations
        recommendations = delivery_optimization_service.get_platform_recommendations(
            content_type="music",
            target_audience="general",
            budget_level="medium"
        )
        
        dashboard_data = {
            "analytics": analytics,
            "recent_plans": recent_plans,
            "platform_recommendations": recommendations[:5],  # Top 5
            "available_platforms": len(delivery_optimization_service.platform_audience_data),
            "period_days": days,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Platform Performance Insights

@router.get("/insights/platform-performance")
async def get_platform_performance_insights(
    platform: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get detailed platform performance insights"""
    try:
        insights = {}
        
        # Get platform data
        if platform:
            if platform in delivery_optimization_service.platform_audience_data:
                platform_data = delivery_optimization_service.platform_audience_data[platform]
                insights[platform] = {
                    "platform_name": platform,
                    "engagement_score": platform_data.get("engagement_score", 75),
                    "success_rate": platform_data.get("success_rate", 90),
                    "global_reach": platform_data.get("global_reach", 1000000),
                    "avg_processing_time": platform_data.get("avg_processing_time", 24),
                    "revenue_multiplier": platform_data.get("revenue_multiplier", 1.0),
                    "peak_hours": platform_data.get("peak_hours", [19, 20, 21]),
                    "audience_demographics": platform_data.get("audience_demographics", {}),
                    "content_preferences": platform_data.get("content_preference", []),
                    "delivery_cost": delivery_optimization_service.delivery_costs.get(platform, 0.05)
                }
            else:
                raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
        else:
            # Get insights for all platforms
            for plat, data in delivery_optimization_service.platform_audience_data.items():
                insights[plat] = {
                    "platform_name": plat,
                    "engagement_score": data.get("engagement_score", 75),
                    "success_rate": data.get("success_rate", 90),
                    "global_reach": data.get("global_reach", 1000000),
                    "avg_processing_time": data.get("avg_processing_time", 24),
                    "revenue_multiplier": data.get("revenue_multiplier", 1.0),
                    "delivery_cost": delivery_optimization_service.delivery_costs.get(plat, 0.05)
                }
        
        return {
            "success": True,
            "insights": insights,
            "platform_filter": platform,
            "period_days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import uuid