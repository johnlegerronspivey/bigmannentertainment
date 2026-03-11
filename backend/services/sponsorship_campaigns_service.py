"""
Big Mann Entertainment - Sponsorship & Campaigns Service
Phase 4: Advanced Features - Sponsorship & Campaigns Backend
"""

import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, Enum):
    BRAND_SPONSORSHIP = "brand_sponsorship"
    PRODUCT_PLACEMENT = "product_placement"
    INFLUENCER_CAMPAIGN = "influencer_campaign"
    CONTENT_PARTNERSHIP = "content_partnership"
    EVENT_SPONSORSHIP = "event_sponsorship"

class BudgetType(str, Enum):
    FIXED = "fixed"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"

class TargetingCriteria(BaseModel):
    age_range: Optional[Dict[str, int]] = None  # {"min": 18, "max": 65}
    gender: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    demographics: Optional[Dict[str, Any]] = None

# Pydantic Models
class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    campaign_type: CampaignType
    status: CampaignStatus
    brand_name: str
    budget_total: float
    budget_type: BudgetType
    budget_spent: float = 0.0
    start_date: datetime
    end_date: datetime
    targeting: TargetingCriteria
    deliverables: List[str] = Field(default_factory=list)
    metrics_goals: Dict[str, float] = Field(default_factory=dict)
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SponsorshipDeal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    sponsor_name: str
    sponsor_contact: Dict[str, str] = Field(default_factory=dict)
    deal_value: float
    deal_terms: Dict[str, Any] = Field(default_factory=dict)
    contract_signed: bool = False
    contract_date: Optional[datetime] = None
    payment_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    deliverables_status: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CampaignMetrics(BaseModel):
    campaign_id: str
    impressions: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    reach: int = 0
    video_views: int = 0
    social_shares: int = 0
    cost_per_impression: float = 0.0
    cost_per_click: float = 0.0
    return_on_ad_spend: float = 0.0
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CampaignContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    asset_id: str
    asset_title: str
    content_type: str  # video, audio, image, text
    platform: str
    scheduled_publish: Optional[datetime] = None
    published_at: Optional[datetime] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    approval_status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SponsorshipOpportunity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    brand_name: str
    industry: str
    budget_range: Dict[str, float]  # {"min": 5000, "max": 15000}
    campaign_type: CampaignType
    requirements: List[str] = Field(default_factory=list)
    deadline: datetime
    contact_info: Dict[str, str] = Field(default_factory=dict)
    status: str = "open"  # open, applied, closed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SponsorshipCampaignsService:
    """Service for managing sponsorships and campaigns"""
    
    def __init__(self):
        self.campaigns_cache = {}
        self.deals_cache = {}
        self.opportunities_cache = {}
        self.metrics_cache = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample sponsorship opportunities"""
        sample_opportunities = [
            SponsorshipOpportunity(
                id="opp_001",
                title="Tech Brand Music Campaign",
                description="Looking for music artists to feature in our new product launch campaign",
                brand_name="TechCorp",
                industry="Technology",
                budget_range={"min": 15000, "max": 50000},
                campaign_type=CampaignType.BRAND_SPONSORSHIP,
                requirements=[
                    "Electronic/Tech music genre",
                    "Minimum 100K monthly streams",
                    "Social media presence required"
                ],
                deadline=datetime.now(timezone.utc) + timedelta(days=30),
                contact_info={
                    "email": "partnerships@techcorp.com",
                    "phone": "+1-555-0123"
                }
            ),
            SponsorshipOpportunity(
                id="opp_002",
                title="Fashion Brand Influencer Campaign",
                description="Seeking content creators for lifestyle brand partnership",
                brand_name="StyleCo",
                industry="Fashion",
                budget_range={"min": 8000, "max": 25000},
                campaign_type=CampaignType.INFLUENCER_CAMPAIGN,
                requirements=[
                    "Fashion/Lifestyle content focus",
                    "Instagram following 50K+",
                    "High engagement rate"
                ],
                deadline=datetime.now(timezone.utc) + timedelta(days=21),
                contact_info={
                    "email": "marketing@styleco.com",
                    "phone": "+1-555-0456"
                }
            )
        ]
        
        for opp in sample_opportunities:
            self.opportunities_cache[opp.id] = opp
    
    async def create_campaign(self, campaign_data: Campaign, user_id: str) -> Dict[str, Any]:
        """Create a new campaign"""
        try:
            campaign = Campaign(**campaign_data.dict())
            campaign.created_by = user_id
            
            self.campaigns_cache[campaign.id] = campaign
            
            logger.info(f"Created campaign: {campaign.id}")
            return {
                "success": True,
                "campaign_id": campaign.id,
                "message": "Campaign created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_campaigns(self, user_id: str, status: CampaignStatus = None,
                           campaign_type: CampaignType = None,
                           limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get campaigns for a user"""
        try:
            # Sample campaigns for demo
            sample_campaigns = [
                Campaign(
                    id="camp_001",
                    title="Summer Music Festival Partnership",
                    description="Partnership campaign for summer music festival promotion",
                    campaign_type=CampaignType.EVENT_SPONSORSHIP,
                    status=CampaignStatus.ACTIVE,
                    brand_name="MusicFest Pro",
                    budget_total=25000.0,
                    budget_type=BudgetType.FIXED,
                    budget_spent=8750.50,
                    start_date=datetime.now(timezone.utc) - timedelta(days=15),
                    end_date=datetime.now(timezone.utc) + timedelta(days=45),
                    targeting=TargetingCriteria(
                        age_range={"min": 18, "max": 35},
                        interests=["music", "festivals", "entertainment"],
                        platforms=["instagram", "tiktok", "youtube"]
                    ),
                    deliverables=[
                        "5 Instagram posts",
                        "2 TikTok videos",
                        "1 YouTube promotional video"
                    ],
                    metrics_goals={
                        "impressions": 500000,
                        "engagement_rate": 5.5,
                        "video_views": 100000
                    },
                    created_by=user_id
                ),
                Campaign(
                    id="camp_002",
                    title="Tech Product Launch Campaign",
                    description="Brand partnership for new smartphone launch",
                    campaign_type=CampaignType.PRODUCT_PLACEMENT,
                    status=CampaignStatus.COMPLETED,
                    brand_name="PhoneTech Inc",
                    budget_total=40000.0,
                    budget_type=BudgetType.PERFORMANCE_BASED,
                    budget_spent=37500.00,
                    start_date=datetime.now(timezone.utc) - timedelta(days=60),
                    end_date=datetime.now(timezone.utc) - timedelta(days=5),
                    targeting=TargetingCriteria(
                        age_range={"min": 25, "max": 45},
                        interests=["technology", "gadgets", "innovation"],
                        platforms=["youtube", "instagram"]
                    ),
                    deliverables=[
                        "Product integration in music video",
                        "3 Instagram stories",
                        "YouTube review video"
                    ],
                    metrics_goals={
                        "impressions": 750000,
                        "conversion_rate": 2.1,
                        "video_views": 200000
                    },
                    created_by=user_id
                ),
                Campaign(
                    id="camp_003",
                    title="Fashion Brand Collaboration",
                    description="Ongoing partnership with lifestyle fashion brand",
                    campaign_type=CampaignType.CONTENT_PARTNERSHIP,
                    status=CampaignStatus.PAUSED,
                    brand_name="Urban Style Co",
                    budget_total=18000.0,
                    budget_type=BudgetType.HYBRID,
                    budget_spent=5400.00,
                    start_date=datetime.now(timezone.utc) - timedelta(days=30),
                    end_date=datetime.now(timezone.utc) + timedelta(days=30),
                    targeting=TargetingCriteria(
                        age_range={"min": 18, "max": 28},
                        gender=["female", "non-binary"],
                        interests=["fashion", "lifestyle", "music"],
                        platforms=["instagram", "tiktok"]
                    ),
                    deliverables=[
                        "Monthly fashion lookbook posts",
                        "TikTok styling videos",
                        "Brand event appearances"
                    ],
                    metrics_goals={
                        "impressions": 300000,
                        "engagement_rate": 8.2,
                        "social_shares": 5000
                    },
                    created_by=user_id
                )
            ]
            
            # Apply filters
            filtered_campaigns = sample_campaigns
            if status:
                filtered_campaigns = [c for c in filtered_campaigns if c.status == status]
            if campaign_type:
                filtered_campaigns = [c for c in filtered_campaigns if c.campaign_type == campaign_type]
            
            # Apply pagination
            total = len(filtered_campaigns)
            campaigns = filtered_campaigns[offset:offset + limit]
            
            return {
                "success": True,
                "campaigns": [campaign.dict() for campaign in campaigns],
                "total": total,
                "limit": limit,
                "offset": offset,
                "summary": {
                    "active": len([c for c in sample_campaigns if c.status == CampaignStatus.ACTIVE]),
                    "completed": len([c for c in sample_campaigns if c.status == CampaignStatus.COMPLETED]),
                    "paused": len([c for c in sample_campaigns if c.status == CampaignStatus.PAUSED]),
                    "total_budget": sum(c.budget_total for c in sample_campaigns),
                    "total_spent": sum(c.budget_spent for c in sample_campaigns)
                }
            }
        except Exception as e:
            logger.error(f"Error fetching campaigns: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "campaigns": []
            }
    
    async def get_campaign(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """Get a specific campaign with details"""
        try:
            # Sample campaign details
            campaign = Campaign(
                id=campaign_id,
                title="Summer Music Festival Partnership",
                description="Partnership campaign for summer music festival promotion",
                campaign_type=CampaignType.EVENT_SPONSORSHIP,
                status=CampaignStatus.ACTIVE,
                brand_name="MusicFest Pro",
                budget_total=25000.0,
                budget_type=BudgetType.FIXED,
                budget_spent=8750.50,
                start_date=datetime.now(timezone.utc) - timedelta(days=15),
                end_date=datetime.now(timezone.utc) + timedelta(days=45),
                targeting=TargetingCriteria(
                    age_range={"min": 18, "max": 35},
                    interests=["music", "festivals", "entertainment"],
                    platforms=["instagram", "tiktok", "youtube"]
                ),
                deliverables=[
                    "5 Instagram posts",
                    "2 TikTok videos",
                    "1 YouTube promotional video"
                ],
                metrics_goals={
                    "impressions": 500000,
                    "engagement_rate": 5.5,
                    "video_views": 100000
                },
                created_by=user_id
            )
            
            # Sample metrics
            metrics = CampaignMetrics(
                campaign_id=campaign_id,
                impressions=345678,
                clicks=18934,
                engagement_rate=6.2,
                conversion_rate=2.8,
                reach=234567,
                video_views=87654,
                social_shares=3456,
                cost_per_impression=0.025,
                cost_per_click=0.46,
                return_on_ad_spend=3.4
            )
            
            # Sample content
            content = [
                CampaignContent(
                    id="content_001",
                    campaign_id=campaign_id,
                    asset_id="asset_001",
                    asset_title="Festival Teaser Video",
                    content_type="video",
                    platform="instagram",
                    published_at=datetime.now(timezone.utc) - timedelta(days=10),
                    performance_metrics={
                        "views": 45678,
                        "likes": 3456,
                        "comments": 234,
                        "shares": 567
                    },
                    approval_status="approved"
                ),
                CampaignContent(
                    id="content_002",
                    campaign_id=campaign_id,
                    asset_id="asset_002",
                    asset_title="Behind the Scenes TikTok",
                    content_type="video",
                    platform="tiktok",
                    scheduled_publish=datetime.now(timezone.utc) + timedelta(days=2),
                    approval_status="pending"
                )
            ]
            
            return {
                "success": True,
                "campaign": campaign.dict(),
                "metrics": metrics.dict(),
                "content": [c.dict() for c in content],
                "progress": {
                    "budget_utilization": (campaign.budget_spent / campaign.budget_total) * 100,
                    "time_elapsed": ((datetime.now(timezone.utc) - campaign.start_date).days / 
                                   (campaign.end_date - campaign.start_date).days) * 100,
                    "deliverables_completed": 2,
                    "deliverables_total": len(campaign.deliverables)
                }
            }
        except Exception as e:
            logger.error(f"Error fetching campaign {campaign_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sponsorship_opportunities(self, user_id: str, 
                                          industry: str = None,
                                          campaign_type: CampaignType = None,
                                          budget_min: float = None) -> Dict[str, Any]:
        """Get available sponsorship opportunities"""
        try:
            opportunities = list(self.opportunities_cache.values())
            
            # Apply filters
            if industry:
                opportunities = [o for o in opportunities if o.industry.lower() == industry.lower()]
            if campaign_type:
                opportunities = [o for o in opportunities if o.campaign_type == campaign_type]
            if budget_min:
                opportunities = [o for o in opportunities if o.budget_range.get("max", 0) >= budget_min]
            
            return {
                "success": True,
                "opportunities": [opp.dict() for opp in opportunities],
                "total": len(opportunities),
                "categories": {
                    "technology": len([o for o in opportunities if o.industry.lower() == "technology"]),
                    "fashion": len([o for o in opportunities if o.industry.lower() == "fashion"]),
                    "entertainment": len([o for o in opportunities if o.industry.lower() == "entertainment"]),
                    "lifestyle": len([o for o in opportunities if o.industry.lower() == "lifestyle"])
                }
            }
        except Exception as e:
            logger.error(f"Error fetching sponsorship opportunities: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "opportunities": []
            }
    
    async def apply_for_opportunity(self, opportunity_id: str, application_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Apply for a sponsorship opportunity"""
        try:
            if opportunity_id not in self.opportunities_cache:
                return {
                    "success": False,
                    "error": "Opportunity not found"
                }
            
            # In production, this would create an application record
            logger.info(f"User {user_id} applied for opportunity {opportunity_id}")
            
            return {
                "success": True,
                "message": "Application submitted successfully",
                "application_id": str(uuid.uuid4()),
                "next_steps": [
                    "Your application is under review",
                    "You will receive a response within 5-7 business days",
                    "Please check your email for updates"
                ]
            }
        except Exception as e:
            logger.error(f"Error applying for opportunity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_campaign_analytics(self, user_id: str, 
                                   start_date: datetime = None,
                                   end_date: datetime = None) -> Dict[str, Any]:
        """Get campaign analytics and performance data"""
        try:
            analytics = {
                "overview": {
                    "total_campaigns": 15,
                    "active_campaigns": 3,
                    "total_budget": 125000.0,
                    "total_spent": 89750.50,
                    "total_revenue_generated": 234567.89,
                    "roi": 161.4
                },
                "performance_metrics": {
                    "total_impressions": 2456789,
                    "total_clicks": 123456,
                    "average_ctr": 5.02,
                    "total_conversions": 6789,
                    "average_conversion_rate": 5.5,
                    "total_reach": 1234567
                },
                "top_performing_campaigns": [
                    {
                        "id": "camp_001",
                        "title": "Summer Music Festival Partnership",
                        "roi": 340.2,
                        "impressions": 567890,
                        "engagement_rate": 8.7
                    },
                    {
                        "id": "camp_002",
                        "title": "Tech Product Launch Campaign",
                        "roi": 245.6,
                        "impressions": 456789,
                        "engagement_rate": 6.4
                    }
                ],
                "by_platform": {
                    "instagram": {
                        "campaigns": 8,
                        "impressions": 987654,
                        "engagement_rate": 7.2,
                        "cost_per_impression": 0.032
                    },
                    "tiktok": {
                        "campaigns": 6,
                        "impressions": 765432,
                        "engagement_rate": 9.8,
                        "cost_per_impression": 0.028
                    },
                    "youtube": {
                        "campaigns": 5,
                        "impressions": 654321,
                        "engagement_rate": 5.1,
                        "cost_per_impression": 0.045
                    }
                },
                "monthly_trends": [
                    {"month": "Jan", "spend": 12000, "revenue": 34000, "roi": 183.3},
                    {"month": "Feb", "spend": 15000, "revenue": 42000, "roi": 180.0},
                    {"month": "Mar", "spend": 18000, "revenue": 52000, "roi": 188.9},
                    {"month": "Apr", "spend": 22000, "revenue": 67000, "roi": 204.5},
                    {"month": "May", "spend": 16000, "revenue": 48000, "roi": 200.0},
                    {"month": "Jun", "spend": 19000, "revenue": 58000, "roi": 205.3}
                ]
            }
            
            return {
                "success": True,
                "analytics": analytics,
                "insights": [
                    "TikTok campaigns show highest engagement rates at 9.8%",
                    "ROI has been consistently improving over past 6 months",
                    "Summer festival partnership is your top performer",
                    "Instagram provides largest reach but lower engagement"
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching campaign analytics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_campaign_status(self, campaign_id: str, status: CampaignStatus, user_id: str) -> Dict[str, Any]:
        """Update campaign status"""
        try:
            # In production, this would update the database
            logger.info(f"Updated campaign {campaign_id} status to {status} by user {user_id}")
            
            return {
                "success": True,
                "message": f"Campaign status updated to {status}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating campaign status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_sponsorship_deal(self, deal_data: SponsorshipDeal, user_id: str) -> Dict[str, Any]:
        """Create a new sponsorship deal"""
        try:
            deal = SponsorshipDeal(**deal_data.dict())
            self.deals_cache[deal.id] = deal
            
            logger.info(f"Created sponsorship deal: {deal.id}")
            return {
                "success": True,
                "deal_id": deal.id,
                "message": "Sponsorship deal created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating sponsorship deal: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
sponsorship_campaigns_service = SponsorshipCampaignsService()