"""
Programmatic DOOH Integration Service
Big Mann Entertainment Platform - Advanced Advertising Module

This service provides comprehensive pDOOH (Programmatic Digital Out-of-Home) integration
with leading SSPs and DSPs for automated campaign management and real-time optimization.
"""

import uuid
import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CampaignType(str, Enum):
    ARTIST_PROMOTION = "artist_promotion"
    RELEASE_ANNOUNCEMENT = "release_announcement"
    EVENT_PROMOTION = "event_promotion"
    BRAND_PARTNERSHIP = "brand_partnership"
    LOCATION_BASED = "location_based"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TriggerType(str, Enum):
    WEATHER = "weather"
    SPORTS_EVENT = "sports_event"
    TIME_BASED = "time_based"
    LOCATION_BASED = "location_based"
    CUSTOM_EVENT = "custom_event"

class CreativeFormat(str, Enum):
    STATIC_IMAGE = "static_image"
    VIDEO = "video"
    DYNAMIC_HTML = "dynamic_html"
    INTERACTIVE = "interactive"

class DOOHPlatform(str, Enum):
    BROADSIGN = "broadsign"
    HIVESTACK = "hivestack"
    VIOOH = "viooh"
    DISPLAYCE = "displayce"
    VISTAR_MEDIA = "vistar_media"
    HAWK = "hawk"
    LOCALA = "locala"
    TRADE_DESK = "trade_desk"

# Pydantic Models
class GeotargetingRule(BaseModel):
    latitude: float
    longitude: float
    radius_km: float
    location_name: str
    demographics: Dict[str, Any] = {}

class TriggerCondition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: TriggerType
    conditions: Dict[str, Any]  # e.g., {"temperature": ">25", "weather": "sunny"}
    creative_variant_id: str
    priority: int = 1

class CreativeAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    format: CreativeFormat
    file_url: str
    dimensions: Dict[str, int]  # {"width": 1920, "height": 1080}
    duration_seconds: Optional[int] = None
    metadata: Dict[str, Any] = {}
    variants: List[str] = []  # IDs of variant assets for DCO

class DOOHCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    campaign_type: CampaignType
    status: CampaignStatus
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    start_date: datetime
    end_date: datetime
    budget_total: float
    budget_spent: float = 0.0
    currency: str = "USD"
    
    # Targeting
    geotargeting_rules: List[GeotargetingRule]
    demographics: Dict[str, Any] = {}
    time_targeting: Dict[str, Any] = {}
    
    # Creative and DCO
    primary_creative: Optional[CreativeAsset] = None
    trigger_conditions: List[TriggerCondition] = []
    
    # Platform Integration
    platforms: List[DOOHPlatform]
    platform_configs: Dict[DOOHPlatform, Dict[str, Any]] = {}
    
    # Performance
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    cpm: float = 0.0
    ctr: float = 0.0
    conversion_rate: float = 0.0

class CampaignPerformance(BaseModel):
    campaign_id: str
    date: datetime
    platform: DOOHPlatform
    location: str
    impressions: int
    estimated_views: int
    engagement_score: float
    weather_condition: Optional[str] = None
    triggered_conditions: List[str] = []
    revenue_attributed: float = 0.0

class RealTimeTrigger(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: TriggerType
    location: GeotargetingRule
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    campaigns_triggered: List[str] = []

class PDOOHIntegrationService:
    """Service for managing Programmatic DOOH campaigns and integrations"""
    
    def __init__(self):
        self.campaigns = {}
        self.performance_data = {}
        self.active_triggers = {}
        self.platform_configs = {}
        
        # Initialize platform configurations
        self._initialize_platform_configs()
        
        # Cache for external API data
        self.weather_cache = {}
        self.sports_cache = {}
        self.events_cache = {}
        
        logger.info("pDOOH Integration Service initialized")
    
    def _initialize_platform_configs(self):
        """Initialize platform-specific configurations"""
        self.platform_configs = {
            DOOHPlatform.BROADSIGN: {
                "api_base": "https://api.broadsign.com/v1",
                "auth_type": "bearer",
                "features": ["header_bidder", "programmatic", "analytics"],
                "creative_formats": ["jpg", "png", "mp4", "html"],
                "max_creative_size_mb": 50,
                "bidding_model": "cpm"
            },
            DOOHPlatform.HIVESTACK: {
                "api_base": "https://api.hivestack.com/v2",
                "auth_type": "api_key",
                "features": ["ssp", "exchange", "ad_server", "analytics"],
                "creative_formats": ["jpg", "png", "mp4", "gif"],
                "max_creative_size_mb": 25,
                "bidding_model": "rtb"
            },
            DOOHPlatform.VIOOH: {
                "api_base": "https://api.viooh.com/v1",
                "auth_type": "oauth2",
                "features": ["inventory_management", "audience_data", "attribution"],
                "creative_formats": ["jpg", "png", "mp4"],
                "max_creative_size_mb": 30,
                "bidding_model": "programmatic_guaranteed"
            },
            DOOHPlatform.VISTAR_MEDIA: {
                "api_base": "https://api.vistarmedia.com/v1",
                "auth_type": "bearer",
                "features": ["dsp", "pmp_deals", "location_intelligence"],
                "creative_formats": ["jpg", "png", "mp4", "html5"],
                "max_creative_size_mb": 40,
                "bidding_model": "rtb"
            },
            DOOHPlatform.TRADE_DESK: {
                "api_base": "https://api.thetradedesk.com/v3",
                "auth_type": "bearer",
                "features": ["dsp", "audience_targeting", "cross_device"],
                "creative_formats": ["jpg", "png", "mp4", "html5", "gif"],
                "max_creative_size_mb": 100,
                "bidding_model": "rtb"
            },
            DOOHPlatform.DISPLAYCE: {
                "api_base": "https://api.displayce.com/v1",
                "auth_type": "api_key",
                "features": ["campaign_management", "real_time_optimization"],
                "creative_formats": ["jpg", "png", "mp4"],
                "max_creative_size_mb": 35,
                "bidding_model": "cpm"
            },
            DOOHPlatform.HAWK: {
                "api_base": "https://api.hawk.co/v2",
                "auth_type": "bearer",
                "features": ["contextual_targeting", "brand_safety"],
                "creative_formats": ["jpg", "png", "mp4", "gif"],
                "max_creative_size_mb": 45,
                "bidding_model": "rtb"
            },
            DOOHPlatform.LOCALA: {
                "api_base": "https://api.locala.com/v1",
                "auth_type": "oauth2",
                "features": ["location_intelligence", "footfall_attribution"],
                "creative_formats": ["jpg", "png", "mp4"],
                "max_creative_size_mb": 30,
                "bidding_model": "location_based"
            }
        }
    
    async def create_campaign(self, campaign_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new pDOOH campaign"""
        try:
            # Validate campaign data
            required_fields = ['name', 'campaign_type', 'start_date', 'end_date', 'budget_total', 'platforms']
            missing_fields = [field for field in required_fields if field not in campaign_data]
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Create campaign object
            campaign = DOOHCampaign(
                name=campaign_data['name'],
                description=campaign_data.get('description', ''),
                campaign_type=CampaignType(campaign_data['campaign_type']),
                status=CampaignStatus.DRAFT,
                created_by=user_id,
                start_date=datetime.fromisoformat(campaign_data['start_date']),
                end_date=datetime.fromisoformat(campaign_data['end_date']),
                budget_total=float(campaign_data['budget_total']),
                currency=campaign_data.get('currency', 'USD'),
                platforms=[DOOHPlatform(p) for p in campaign_data['platforms']],
                geotargeting_rules=[
                    GeotargetingRule(**rule) for rule in campaign_data.get('geotargeting_rules', [])
                ],
                demographics=campaign_data.get('demographics', {}),
                time_targeting=campaign_data.get('time_targeting', {}),
                primary_creative=CreativeAsset(**campaign_data['primary_creative']) if 'primary_creative' in campaign_data else None,
                trigger_conditions=[
                    TriggerCondition(**condition) for condition in campaign_data.get('trigger_conditions', [])
                ]
            )
            
            # Store campaign
            self.campaigns[campaign.id] = campaign
            
            # Initialize performance tracking
            self.performance_data[campaign.id] = []
            
            logger.info(f"Created pDOOH campaign {campaign.id} for user {user_id}")
            
            return {
                "success": True,
                "campaign_id": campaign.id,
                "campaign": campaign.dict(),
                "message": "pDOOH campaign created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating pDOOH campaign: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def launch_campaign(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """Launch a campaign across selected platforms"""
        try:
            if campaign_id not in self.campaigns:
                return {"success": False, "error": "Campaign not found"}
            
            campaign = self.campaigns[campaign_id]
            
            # Launch on each platform
            launch_results = {}
            for platform in campaign.platforms:
                result = await self._launch_on_platform(campaign, platform)
                launch_results[platform.value] = result
            
            # Update campaign status
            campaign.status = CampaignStatus.ACTIVE
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "launch_results": launch_results,
                "message": "Campaign launched successfully"
            }
            
        except Exception as e:
            logger.error(f"Error launching campaign {campaign_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _launch_on_platform(self, campaign: DOOHCampaign, platform: DOOHPlatform) -> Dict[str, Any]:
        """Launch campaign on specific platform"""
        try:
            platform_config = self.platform_configs[platform]
            
            # Prepare campaign payload for platform
            payload = {
                "name": campaign.name,
                "description": campaign.description,
                "start_date": campaign.start_date.isoformat(),
                "end_date": campaign.end_date.isoformat(),
                "budget": campaign.budget_total / len(campaign.platforms),  # Split budget across platforms
                "currency": campaign.currency,
                "targeting": {
                    "geotargeting": [rule.dict() for rule in campaign.geotargeting_rules],
                    "demographics": campaign.demographics,
                    "time_targeting": campaign.time_targeting
                },
                "creative": campaign.primary_creative.dict() if campaign.primary_creative else None,
                "trigger_conditions": [condition.dict() for condition in campaign.trigger_conditions]
            }
            
            # Simulate platform-specific API call
            # In production, this would make actual HTTP requests to platform APIs
            mock_response = {
                "platform_campaign_id": f"{platform.value}_{uuid.uuid4().hex[:8]}",
                "status": "active",
                "estimated_reach": self._estimate_reach(campaign, platform),
                "estimated_cpm": self._estimate_cpm(platform),
                "approval_status": "approved"
            }
            
            # Store platform-specific configuration
            if campaign.id not in campaign.platform_configs:
                campaign.platform_configs[platform] = {}
            campaign.platform_configs[platform].update(mock_response)
            
            logger.info(f"Launched campaign {campaign.id} on {platform.value}")
            
            return {
                "success": True,
                "platform": platform.value,
                "platform_campaign_id": mock_response["platform_campaign_id"],
                "estimated_reach": mock_response["estimated_reach"]
            }
            
        except Exception as e:
            logger.error(f"Error launching on {platform.value}: {e}")
            return {
                "success": False,
                "platform": platform.value,
                "error": str(e)
            }
    
    def _estimate_reach(self, campaign: DOOHCampaign, platform: DOOHPlatform) -> int:
        """Estimate campaign reach based on targeting and platform"""
        base_reach = 10000
        
        # Adjust based on geotargeting
        if campaign.geotargeting_rules:
            for rule in campaign.geotargeting_rules:
                base_reach += int(rule.radius_km * 1000)  # Rough estimate
        
        # Platform-specific multipliers
        platform_multipliers = {
            DOOHPlatform.TRADE_DESK: 2.5,
            DOOHPlatform.VISTAR_MEDIA: 2.0,
            DOOHPlatform.HIVESTACK: 1.8,
            DOOHPlatform.BROADSIGN: 1.5,
            DOOHPlatform.VIOOH: 1.3,
            DOOHPlatform.DISPLAYCE: 1.2,
            DOOHPlatform.HAWK: 1.1,
            DOOHPlatform.LOCALA: 1.0
        }
        
        return int(base_reach * platform_multipliers.get(platform, 1.0))
    
    def _estimate_cpm(self, platform: DOOHPlatform) -> float:
        """Estimate CPM based on platform"""
        platform_cpms = {
            DOOHPlatform.TRADE_DESK: 8.50,
            DOOHPlatform.VISTAR_MEDIA: 7.80,
            DOOHPlatform.HIVESTACK: 6.90,
            DOOHPlatform.VIOOH: 6.20,
            DOOHPlatform.BROADSIGN: 5.80,
            DOOHPlatform.DISPLAYCE: 5.40,
            DOOHPlatform.HAWK: 4.90,
            DOOHPlatform.LOCALA: 4.50
        }
        
        return platform_cpms.get(platform, 5.00)
    
    async def get_campaigns(self, user_id: str, status: Optional[CampaignStatus] = None) -> Dict[str, Any]:
        """Get campaigns for a user"""
        try:
            user_campaigns = [
                campaign for campaign in self.campaigns.values() 
                if campaign.created_by == user_id
            ]
            
            if status:
                user_campaigns = [c for c in user_campaigns if c.status == status]
            
            return {
                "success": True,
                "campaigns": [campaign.dict() for campaign in user_campaigns],
                "total_count": len(user_campaigns)
            }
            
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_campaign_performance(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """Get performance data for a campaign"""
        try:
            if campaign_id not in self.campaigns:
                return {"success": False, "error": "Campaign not found"}
            
            campaign = self.campaigns[campaign_id]
            if campaign.created_by != user_id:
                return {"success": False, "error": "Unauthorized"}
            
            # Generate mock performance data
            performance_data = []
            for i in range(7):  # Last 7 days
                date = datetime.now(timezone.utc) - timedelta(days=i)
                for platform in campaign.platforms:
                    performance_data.append({
                        "date": date.isoformat(),
                        "platform": platform.value,
                        "impressions": np.random.randint(1000, 5000),
                        "estimated_views": np.random.randint(800, 4500),
                        "engagement_score": round(np.random.uniform(0.1, 0.8), 2),
                        "cpm": self._estimate_cpm(platform),
                        "spend": round(np.random.uniform(50, 200), 2)
                    })
            
            # Calculate summary metrics
            total_impressions = sum(p["impressions"] for p in performance_data)
            total_spend = sum(p["spend"] for p in performance_data)
            avg_cpm = total_spend / (total_impressions / 1000) if total_impressions > 0 else 0
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "performance_summary": {
                    "total_impressions": total_impressions,
                    "total_spend": round(total_spend, 2),
                    "average_cpm": round(avg_cpm, 2),
                    "budget_utilization": round((total_spend / campaign.budget_total) * 100, 1),
                    "active_platforms": len(campaign.platforms)
                },
                "daily_performance": performance_data,
                "platform_breakdown": self._get_platform_breakdown(performance_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign performance: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_platform_breakdown(self, performance_data: List[Dict]) -> Dict[str, Any]:
        """Calculate platform-wise performance breakdown"""
        platform_stats = {}
        
        for entry in performance_data:
            platform = entry["platform"]
            if platform not in platform_stats:
                platform_stats[platform] = {
                    "impressions": 0,
                    "spend": 0,
                    "avg_engagement": 0,
                    "days_active": 0
                }
            
            platform_stats[platform]["impressions"] += entry["impressions"]
            platform_stats[platform]["spend"] += entry["spend"]
            platform_stats[platform]["avg_engagement"] += entry["engagement_score"]
            platform_stats[platform]["days_active"] += 1
        
        # Calculate averages
        for platform, stats in platform_stats.items():
            if stats["days_active"] > 0:
                stats["avg_engagement"] = round(stats["avg_engagement"] / stats["days_active"], 2)
                stats["avg_cpm"] = round(stats["spend"] / (stats["impressions"] / 1000), 2) if stats["impressions"] > 0 else 0
        
        return platform_stats
    
    async def get_platform_inventory(self, platform: DOOHPlatform, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get available inventory for a platform"""
        try:
            # Mock inventory data
            locations = [
                {
                    "id": f"loc_{uuid.uuid4().hex[:8]}",
                    "name": "Times Square Billboard",
                    "latitude": 40.7580,
                    "longitude": -73.9855,
                    "screen_type": "LED Billboard",
                    "dimensions": {"width": 1920, "height": 1080},
                    "daily_impressions": 150000,
                    "cpm_range": {"min": 12.0, "max": 25.0},
                    "availability": "high",
                    "demographics": {
                        "age_groups": {"18-24": 25, "25-34": 30, "35-44": 25, "45+": 20},
                        "income_levels": {"high": 40, "medium": 35, "low": 25}
                    }
                },
                {
                    "id": f"loc_{uuid.uuid4().hex[:8]}",
                    "name": "LAX Airport Terminal",
                    "latitude": 33.9425,
                    "longitude": -118.4081,
                    "screen_type": "Digital Display",
                    "dimensions": {"width": 1080, "height": 1920},
                    "daily_impressions": 85000,
                    "cpm_range": {"min": 8.0, "max": 15.0},
                    "availability": "medium",
                    "demographics": {
                        "age_groups": {"18-24": 20, "25-34": 35, "35-44": 30, "45+": 15},
                        "income_levels": {"high": 60, "medium": 30, "low": 10}
                    }
                },
                {
                    "id": f"loc_{uuid.uuid4().hex[:8]}",
                    "name": "Chicago Transit Hub",
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                    "screen_type": "Interactive Kiosk",
                    "dimensions": {"width": 1080, "height": 1920},
                    "daily_impressions": 65000,
                    "cpm_range": {"min": 6.0, "max": 12.0},
                    "availability": "high",
                    "demographics": {
                        "age_groups": {"18-24": 30, "25-34": 35, "35-44": 20, "45+": 15},
                        "income_levels": {"high": 25, "medium": 45, "low": 30}
                    }
                }
            ]
            
            # Apply filters if provided
            if filters:
                if "min_impressions" in filters:
                    locations = [loc for loc in locations if loc["daily_impressions"] >= filters["min_impressions"]]
                if "max_cpm" in filters:
                    locations = [loc for loc in locations if loc["cpm_range"]["min"] <= filters["max_cpm"]]
                if "location_type" in filters:
                    locations = [loc for loc in locations if filters["location_type"].lower() in loc["name"].lower()]
            
            return {
                "success": True,
                "platform": platform.value,
                "inventory_count": len(locations),
                "locations": locations,
                "platform_features": self.platform_configs[platform]["features"]
            }
            
        except Exception as e:
            logger.error(f"Error getting platform inventory: {e}")
            return {"success": False, "error": str(e)}

# Global instance
pdooh_integration_service = PDOOHIntegrationService()

# Import numpy for performance calculations
try:
    import numpy as np
except ImportError:
    # Fallback to random module if numpy not available
    import random
    class MockNumpy:
        @staticmethod
        def random():
            return MockRandom()
    
    class MockRandom:
        @staticmethod
        def randint(low, high):
            return random.randint(low, high)
        
        @staticmethod
        def uniform(low, high):
            return random.uniform(low, high)
    
    np = MockNumpy()