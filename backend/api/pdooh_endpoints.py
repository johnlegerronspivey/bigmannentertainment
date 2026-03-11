"""
Programmatic DOOH API Endpoints
Big Mann Entertainment Platform - Advanced Advertising Module

API endpoints for pDOOH campaign management, real-time triggers,
and dynamic creative optimization.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

# Import services
from pdooh_integration_service import (
    pdooh_integration_service,
    DOOHCampaign,
    CampaignType,
    CampaignStatus,
    DOOHPlatform,
    CreativeAsset,
    GeotargetingRule,
    TriggerCondition
)
from real_time_triggers_service import (
    real_time_triggers_service,
    WeatherTrigger,
    SportsEventTrigger,
    CustomEventTrigger,
    TriggerRule
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/pdooh", tags=["Programmatic DOOH"])

# ===== CAMPAIGN MANAGEMENT ENDPOINTS =====

@router.post("/campaigns")
async def create_pdooh_campaign(
    campaign_data: Dict[str, Any] = Body(...),
    user_id: str = Query(...)
):
    """Create a new pDOOH campaign"""
    try:
        logger.info(f"Creating pDOOH campaign for user {user_id}")
        result = await pdooh_integration_service.create_campaign(campaign_data, user_id)
        return result
    except Exception as e:
        logger.error(f"Error creating pDOOH campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns")
async def get_pdooh_campaigns(
    user_id: str = Query(...),
    status: Optional[CampaignStatus] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get pDOOH campaigns for a user"""
    try:
        result = await pdooh_integration_service.get_campaigns(user_id, status)
        
        # Apply pagination
        campaigns = result.get("campaigns", [])
        total_count = len(campaigns)
        paginated_campaigns = campaigns[offset:offset + limit]
        
        return {
            "success": True,
            "campaigns": paginated_campaigns,
            "total_count": total_count,
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting pDOOH campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}")
async def get_pdooh_campaign(
    campaign_id: str,
    user_id: str = Query(...)
):
    """Get specific pDOOH campaign"""
    try:
        if campaign_id not in pdooh_integration_service.campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = pdooh_integration_service.campaigns[campaign_id]
        if campaign.created_by != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        return {
            "success": True,
            "campaign": campaign.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pDOOH campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns/{campaign_id}/launch")
async def launch_pdooh_campaign(
    campaign_id: str,
    user_id: str = Query(...)
):
    """Launch a pDOOH campaign across selected platforms"""
    try:
        result = await pdooh_integration_service.launch_campaign(campaign_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error launching pDOOH campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/campaigns/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: str,
    status: CampaignStatus,
    user_id: str = Query(...)
):
    """Update campaign status (pause, resume, cancel)"""
    try:
        if campaign_id not in pdooh_integration_service.campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = pdooh_integration_service.campaigns[campaign_id]
        if campaign.created_by != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        campaign.status = status
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "new_status": status.value,
            "message": f"Campaign status updated to {status.value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PERFORMANCE & ANALYTICS ENDPOINTS =====

@router.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: str,
    user_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get performance analytics for a campaign"""
    try:
        result = await pdooh_integration_service.get_campaign_performance(campaign_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error getting campaign performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/attribution")
async def get_attribution_data(
    campaign_id: str,
    user_id: str = Query(...),
    attribution_window_hours: int = Query(24, ge=1, le=168)
):
    """Get attribution data for campaign conversions"""
    try:
        if campaign_id not in pdooh_integration_service.campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = pdooh_integration_service.campaigns[campaign_id]
        if campaign.created_by != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Mock attribution data
        attribution_data = {
            "campaign_id": campaign_id,
            "attribution_window_hours": attribution_window_hours,
            "total_conversions": 247,
            "attributed_conversions": 186,
            "attribution_rate": 75.3,
            "conversion_types": {
                "app_installs": 98,
                "website_visits": 156,
                "store_visits": 89,
                "streaming_plays": 234
            },
            "attribution_by_platform": {
                "vistar_media": {"conversions": 67, "attribution_rate": 82.1},
                "trade_desk": {"conversions": 54, "attribution_rate": 73.8},
                "hivestack": {"conversions": 45, "attribution_rate": 69.2},
                "broadsign": {"conversions": 20, "attribution_rate": 58.3}
            },
            "footfall_attribution": {
                "estimated_footfall": 12450,
                "attributed_visits": 1834,
                "lift_percentage": 23.7
            }
        }
        
        return {
            "success": True,
            "attribution_data": attribution_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attribution data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PLATFORM & INVENTORY ENDPOINTS =====

@router.get("/platforms")
async def get_dooh_platforms():
    """Get available pDOOH platforms and their capabilities"""
    try:
        platforms_info = {}
        for platform in DOOHPlatform:
            config = pdooh_integration_service.platform_configs.get(platform, {})
            platforms_info[platform.value] = {
                "name": platform.value.replace("_", " ").title(),
                "features": config.get("features", []),
                "creative_formats": config.get("creative_formats", []),
                "max_creative_size_mb": config.get("max_creative_size_mb", 0),
                "bidding_model": config.get("bidding_model", "unknown")
            }
        
        return {
            "success": True,
            "platforms": platforms_info,
            "total_platforms": len(platforms_info)
        }
    except Exception as e:
        logger.error(f"Error getting pDOOH platforms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/{platform}/inventory")
async def get_platform_inventory(
    platform: DOOHPlatform,
    user_id: str = Query(...),
    location: Optional[str] = Query(None),
    min_impressions: Optional[int] = Query(None),
    max_cpm: Optional[float] = Query(None)
):
    """Get available inventory for a specific platform"""
    try:
        filters = {}
        if min_impressions:
            filters["min_impressions"] = min_impressions
        if max_cpm:
            filters["max_cpm"] = max_cpm
        if location:
            filters["location_type"] = location
        
        result = await pdooh_integration_service.get_platform_inventory(platform, filters)
        return result
    except Exception as e:
        logger.error(f"Error getting platform inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== REAL-TIME TRIGGERS ENDPOINTS =====

@router.get("/triggers/weather")
async def get_weather_trigger(
    latitude: float = Query(...),
    longitude: float = Query(...),
    location_name: str = Query(""),
    user_id: str = Query(...)
):
    """Get current weather data for trigger evaluation"""
    try:
        weather_data = await real_time_triggers_service.get_weather_data(
            latitude, longitude, location_name
        )
        return {
            "success": True,
            "weather_data": weather_data.dict()
        }
    except Exception as e:
        logger.error(f"Error getting weather trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/triggers/sports")
async def get_sports_triggers(
    location: str = Query(...),
    date: Optional[datetime] = Query(None),
    user_id: str = Query(...)
):
    """Get sports events for trigger evaluation"""
    try:
        sports_events = await real_time_triggers_service.get_sports_events(location, date)
        return {
            "success": True,
            "sports_events": [event.dict() for event in sports_events],
            "events_count": len(sports_events)
        }
    except Exception as e:
        logger.error(f"Error getting sports triggers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/triggers/events")
async def get_event_triggers(
    location: str = Query(...),
    radius_km: int = Query(25, ge=1, le=100),
    date: Optional[datetime] = Query(None),
    user_id: str = Query(...)
):
    """Get local events for trigger evaluation"""
    try:
        local_events = await real_time_triggers_service.get_local_events(location, radius_km, date)
        return {
            "success": True,
            "local_events": [event.dict() for event in local_events],
            "events_count": len(local_events)
        }
    except Exception as e:
        logger.error(f"Error getting event triggers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triggers/evaluate")
async def evaluate_campaign_triggers(
    campaign_id: str,
    location: str,
    latitude: float,
    longitude: float,
    user_id: str = Query(...)
):
    """Evaluate all triggers for a campaign and location"""
    try:
        result = await real_time_triggers_service.evaluate_triggers(
            campaign_id, location, latitude, longitude
        )
        return result
    except Exception as e:
        logger.error(f"Error evaluating triggers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triggers/rules")
async def create_trigger_rule(
    rule_data: Dict[str, Any] = Body(...),
    user_id: str = Query(...)
):
    """Create a custom trigger rule"""
    try:
        result = await real_time_triggers_service.create_trigger_rule(rule_data, user_id)
        return result
    except Exception as e:
        logger.error(f"Error creating trigger rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/triggers/history/{campaign_id}")
async def get_trigger_history(
    campaign_id: str,
    hours: int = Query(24, ge=1, le=168),
    user_id: str = Query(...)
):
    """Get trigger evaluation history for a campaign"""
    try:
        result = await real_time_triggers_service.get_trigger_history(campaign_id, hours)
        return result
    except Exception as e:
        logger.error(f"Error getting trigger history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== DYNAMIC CREATIVE OPTIMIZATION ENDPOINTS =====

@router.post("/dco/optimize")
async def optimize_creative(
    campaign_id: str,
    location_data: Dict[str, Any] = Body(...),
    user_id: str = Query(...)
):
    """Optimize creative based on real-time conditions"""
    try:
        # Extract location information
        location = location_data.get("location", "Unknown")
        latitude = location_data.get("latitude", 0.0)
        longitude = location_data.get("longitude", 0.0)
        
        # Evaluate triggers
        trigger_result = await real_time_triggers_service.evaluate_triggers(
            campaign_id, location, latitude, longitude
        )
        
        if not trigger_result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to evaluate triggers")
        
        # Get creative optimization recommendations
        creative_variants = trigger_result.get("creative_variants", {})
        triggered_conditions = trigger_result.get("triggered_conditions", [])
        
        optimization_result = {
            "campaign_id": campaign_id,
            "location": location,
            "optimization_timestamp": datetime.now(timezone.utc).isoformat(),
            "creative_variants": creative_variants,
            "triggered_conditions": triggered_conditions,
            "optimization_score": len(triggered_conditions) * 0.2 + 0.6,  # Base score + trigger bonus
            "recommendations": {
                "primary_creative": creative_variants.get("primary_variant", "default"),
                "color_scheme": creative_variants.get("color_scheme", "default"),
                "messaging": creative_variants.get("messaging", "default"),
                "overlay_elements": creative_variants.get("overlay_elements", []),
                "call_to_action": creative_variants.get("call_to_action", "default")
            },
            "performance_prediction": {
                "expected_ctr_lift": f"+{len(triggered_conditions) * 5}%",
                "engagement_score": min(100, 60 + len(triggered_conditions) * 8),
                "relevance_score": min(100, 70 + len(triggered_conditions) * 6)
            }
        }
        
        return {
            "success": True,
            "optimization": optimization_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing creative: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dco/variants/{campaign_id}")
async def get_creative_variants(
    campaign_id: str,
    user_id: str = Query(...)
):
    """Get available creative variants for a campaign"""
    try:
        if campaign_id not in pdooh_integration_service.campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = pdooh_integration_service.campaigns[campaign_id]
        if campaign.created_by != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Mock creative variants data
        variants = {
            "default": {
                "name": "Default Creative",
                "description": "Standard campaign creative",
                "file_url": "/assets/creatives/default.jpg",
                "triggers": ["none"]
            },
            "summer": {
                "name": "Summer Theme",
                "description": "Hot weather optimized creative",
                "file_url": "/assets/creatives/summer.jpg",
                "triggers": ["hot_weather", "sunny"]
            },
            "cozy": {
                "name": "Cozy Indoor",
                "description": "Rainy day optimized creative",
                "file_url": "/assets/creatives/cozy.jpg",
                "triggers": ["rainy", "cold_weather"]
            },
            "sports": {
                "name": "Sports Excitement",
                "description": "Live sports optimized creative",
                "file_url": "/assets/creatives/sports.jpg",
                "triggers": ["live_game", "upcoming_game"]
            },
            "nightlife": {
                "name": "Nightlife Vibes",
                "description": "Evening/night optimized creative",
                "file_url": "/assets/creatives/nightlife.jpg",
                "triggers": ["nightlife_hours", "weekend"]
            }
        }
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "creative_variants": variants,
            "variants_count": len(variants)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting creative variants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== MONITORING & REPORTING ENDPOINTS =====

@router.get("/monitoring/dashboard")
async def get_monitoring_dashboard(
    user_id: str = Query(...),
    time_range: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$")
):
    """Get comprehensive monitoring dashboard data"""
    try:
        # Convert time range to hours
        time_multipliers = {"1h": 1, "6h": 6, "24h": 24, "7d": 168, "30d": 720}
        hours = time_multipliers.get(time_range, 24)
        
        # Get user campaigns
        campaigns_result = await pdooh_integration_service.get_campaigns(user_id)
        user_campaigns = campaigns_result.get("campaigns", [])
        
        # Calculate aggregate metrics
        total_campaigns = len(user_campaigns)
        active_campaigns = len([c for c in user_campaigns if c.get("status") == "active"])
        total_budget = sum(c.get("budget_total", 0) for c in user_campaigns)
        total_spend = sum(c.get("budget_spent", 0) for c in user_campaigns)
        
        dashboard_data = {
            "time_range": time_range,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "campaign_overview": {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "paused_campaigns": len([c for c in user_campaigns if c.get("status") == "paused"]),
                "completed_campaigns": len([c for c in user_campaigns if c.get("status") == "completed"])
            },
            "budget_overview": {
                "total_budget": round(total_budget, 2),
                "total_spend": round(total_spend, 2),
                "remaining_budget": round(total_budget - total_spend, 2),
                "budget_utilization": round((total_spend / total_budget * 100), 1) if total_budget > 0 else 0
            },
            "performance_metrics": {
                "total_impressions": 847623,
                "total_reach": 645892,
                "average_cpm": 6.85,
                "average_ctr": 0.34,
                "total_conversions": 2847
            },
            "platform_distribution": {
                "trade_desk": {"campaigns": 8, "spend": 12450.80, "impressions": 245000},
                "vistar_media": {"campaigns": 6, "spend": 9820.40, "impressions": 198000},
                "hivestack": {"campaigns": 5, "spend": 7650.30, "impressions": 167000},
                "broadsign": {"campaigns": 4, "spend": 6420.50, "impressions": 145000}
            },
            "trigger_analytics": {
                "total_trigger_evaluations": 1247,
                "successful_triggers": 892,
                "trigger_success_rate": 71.5,
                "most_active_triggers": [
                    {"type": "weather", "count": 342},
                    {"type": "time_based", "count": 287},
                    {"type": "sports", "count": 156},
                    {"type": "events", "count": 107}
                ]
            },
            "recent_alerts": [
                {
                    "type": "performance",
                    "message": "Campaign 'Summer Music Fest' exceeding expected CTR by 23%",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "severity": "info"
                },
                {
                    "type": "budget",
                    "message": "Campaign 'Artist Spotlight' approaching budget limit (85% spent)",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                    "severity": "warning"
                }
            ]
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reporting/export/{campaign_id}")
async def export_campaign_report(
    campaign_id: str,
    format: str = Query("csv", regex="^(csv|json|pdf)$"),
    user_id: str = Query(...)
):
    """Export campaign performance report"""
    try:
        if campaign_id not in pdooh_integration_service.campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = pdooh_integration_service.campaigns[campaign_id]
        if campaign.created_by != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get campaign performance data
        performance_result = await pdooh_integration_service.get_campaign_performance(campaign_id, user_id)
        
        export_data = {
            "campaign_info": {
                "id": campaign_id,
                "name": campaign.name,
                "type": campaign.campaign_type.value,
                "status": campaign.status.value,
                "start_date": campaign.start_date.isoformat(),
                "end_date": campaign.end_date.isoformat()
            },
            "performance_data": performance_result.get("performance_summary", {}),
            "platform_breakdown": performance_result.get("platform_breakdown", {}),
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "export_format": format
        }
        
        return {
            "success": True,
            "export_data": export_data,
            "download_url": f"/api/pdooh/downloads/{campaign_id}_{format}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
            "message": f"Report exported successfully in {format.upper()} format"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting campaign report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))