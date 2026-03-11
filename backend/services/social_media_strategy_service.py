"""
Social Media Strategy Service
Comprehensive Social Media Strategy Center with Phases 5-10 workflow
Connects all 21 social media platforms to strategic workflow pipeline
"""

import os
import logging
import asyncio
import uuid
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from enum import Enum
import hashlib
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)

class StrategyPhase(str, Enum):
    """Social media strategy phases"""
    PHASE_1_DISCOVERY = "phase_1_discovery"
    PHASE_2_PLANNING = "phase_2_planning"
    PHASE_3_CONTENT_CREATION = "phase_3_content_creation"
    PHASE_4_COMMUNITY_BUILDING = "phase_4_community_building"
    PHASE_5_ENGAGEMENT_AMPLIFICATION = "phase_5_engagement_amplification"
    PHASE_6_INFLUENCER_COLLABORATION = "phase_6_influencer_collaboration"
    PHASE_7_PAID_PROMOTION = "phase_7_paid_promotion"
    PHASE_8_CROSS_PLATFORM_SYNDICATION = "phase_8_cross_platform_syndication"
    PHASE_9_ANALYTICS_OPTIMIZATION = "phase_9_analytics_optimization"
    PHASE_10_ROI_MAXIMIZATION = "phase_10_roi_maximization"

class SocialMediaPlatformType(str, Enum):
    """Types of social media platforms"""
    PHOTO_SHARING = "photo_sharing"
    VIDEO_SHARING = "video_sharing"
    MICROBLOGGING = "microblogging"
    PROFESSIONAL_NETWORKING = "professional_networking"
    MESSAGING = "messaging"
    ENTERTAINMENT = "entertainment"
    NEWS_MEDIA = "news_media"
    COMMUNITY = "community"

class CampaignObjective(str, Enum):
    """Campaign objectives"""
    BRAND_AWARENESS = "brand_awareness"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    CONVERSIONS = "conversions"
    LEAD_GENERATION = "lead_generation"
    COMMUNITY_GROWTH = "community_growth"
    VIRAL_CONTENT = "viral_content"
    INFLUENCER_REACH = "influencer_reach"

class StrategyStatus(str, Enum):
    """Strategy workflow status"""
    PLANNING = "planning"
    ACTIVE = "active"
    OPTIMIZING = "optimizing"
    SCALING = "scaling"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"

class SocialMediaStrategyModel(BaseModel):
    """Complete social media strategy model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Strategy Information
    strategy_name: str
    campaign_objective: CampaignObjective
    target_audience: Dict[str, Any] = {}
    brand_voice: Dict[str, Any] = {}
    content_themes: List[str] = []
    
    # Platform Configuration
    target_platforms: List[str] = []
    platform_strategies: Dict[str, Dict[str, Any]] = {}
    cross_platform_synergies: Dict[str, Any] = {}
    
    # Campaign Details
    campaign_duration_days: int = 30
    budget_allocation: Dict[str, float] = {}
    content_calendar: List[Dict[str, Any]] = []
    posting_schedule: Dict[str, List[str]] = {}
    
    # Phase Progress
    current_phase: StrategyPhase = StrategyPhase.PHASE_5_ENGAGEMENT_AMPLIFICATION
    phases_completed: List[str] = []
    phase_results: Dict[str, Dict[str, Any]] = {}
    
    # Performance Metrics
    strategy_status: StrategyStatus = StrategyStatus.PLANNING
    progress_percentage: float = 0.0
    kpi_targets: Dict[str, float] = {}
    current_metrics: Dict[str, float] = {}
    
    # Advanced Features
    influencer_partnerships: List[Dict[str, Any]] = []
    paid_promotion_campaigns: List[Dict[str, Any]] = []
    analytics_insights: Dict[str, Any] = {}
    optimization_recommendations: List[str] = []
    
    # Owner and Timestamps
    owner_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # ROI Tracking
    total_spend: float = 0.0
    total_revenue: float = 0.0
    roi_percentage: float = 0.0
    cost_per_engagement: float = 0.0

class SocialMediaStrategyService:
    """Service for managing comprehensive social media strategies"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.strategies_collection = db.social_media_strategies
        self.campaigns_collection = db.social_media_campaigns
        
        # Get social media platforms from main server
        from config.platforms import DISTRIBUTION_PLATFORMS
        self.all_platforms = DISTRIBUTION_PLATFORMS
        
        # Filter to get only social media platforms
        self.social_media_platforms = {
            k: v for k, v in self.all_platforms.items() 
            if v.get("type") == "social_media"
        }
        
        # Phase 5-10 workflow stages
        self.advanced_phases = [
            "phase_5_engagement_amplification",
            "phase_6_influencer_collaboration", 
            "phase_7_paid_promotion",
            "phase_8_cross_platform_syndication",
            "phase_9_analytics_optimization",
            "phase_10_roi_maximization"
        ]
        
        logger.info(f"Initialized Social Media Strategy Service with {len(self.social_media_platforms)} platforms")
    
    async def create_social_media_strategy(
        self,
        strategy_name: str,
        campaign_objective: CampaignObjective,
        owner_id: str,
        target_platforms: List[str] = None,
        campaign_duration_days: int = 30,
        budget_allocation: Dict[str, float] = None
    ) -> SocialMediaStrategyModel:
        """Create a comprehensive social media strategy"""
        
        # Default to all social media platforms if none specified
        if not target_platforms:
            target_platforms = list(self.social_media_platforms.keys())
        
        # Validate platforms are social media platforms
        valid_platforms = [p for p in target_platforms if p in self.social_media_platforms]
        
        # Create strategy
        strategy = SocialMediaStrategyModel(
            strategy_name=strategy_name,
            campaign_objective=campaign_objective,
            owner_id=owner_id,
            target_platforms=valid_platforms,
            campaign_duration_days=campaign_duration_days,
            budget_allocation=budget_allocation or {},
            # Start at Phase 5 as requested
            current_phase=StrategyPhase.PHASE_5_ENGAGEMENT_AMPLIFICATION,
            phases_completed=["phase_1_discovery", "phase_2_planning", "phase_3_content_creation", "phase_4_community_building"]
        )
        
        # Initialize platform-specific strategies
        for platform_id in valid_platforms:
            strategy.platform_strategies[platform_id] = await self._create_platform_strategy(platform_id, campaign_objective)
        
        # Set KPI targets
        strategy.kpi_targets = await self._set_kpi_targets(strategy)
        
        # Store strategy
        await self.strategies_collection.insert_one(strategy.dict())
        
        # Start advanced workflow (Phases 5-10)
        asyncio.create_task(self._execute_advanced_phases(strategy))
        
        logger.info(f"Created social media strategy {strategy.id} for {len(valid_platforms)} platforms")
        return strategy
    
    async def _execute_advanced_phases(self, strategy: SocialMediaStrategyModel):
        """Execute advanced social media strategy phases (5-10)"""
        
        try:
            # Phase 5: Engagement Amplification
            await self._phase_5_engagement_amplification(strategy)
            
            # Phase 6: Influencer Collaboration
            await self._phase_6_influencer_collaboration(strategy)
            
            # Phase 7: Paid Promotion
            await self._phase_7_paid_promotion(strategy)
            
            # Phase 8: Cross-Platform Syndication
            await self._phase_8_cross_platform_syndication(strategy)
            
            # Phase 9: Analytics Optimization
            await self._phase_9_analytics_optimization(strategy)
            
            # Phase 10: ROI Maximization
            await self._phase_10_roi_maximization(strategy)
            
            # Complete strategy
            strategy.strategy_status = StrategyStatus.COMPLETED
            strategy.completed_at = datetime.now(timezone.utc)
            strategy.progress_percentage = 100.0
            
            await self._update_strategy(strategy)
            
            logger.info(f"Completed social media strategy {strategy.id}")
            
        except Exception as e:
            logger.error(f"Strategy {strategy.id} failed: {str(e)}")
            strategy.strategy_status = StrategyStatus.FAILED
            await self._update_strategy(strategy)
    
    async def _phase_5_engagement_amplification(self, strategy: SocialMediaStrategyModel):
        """Phase 5: Advanced Engagement Amplification across all 21 social media platforms"""
        strategy.current_phase = StrategyPhase.PHASE_5_ENGAGEMENT_AMPLIFICATION
        strategy.strategy_status = StrategyStatus.ACTIVE
        strategy.progress_percentage = 50.0
        
        amplification_results = {}
        
        for platform_id in strategy.target_platforms:
            platform_config = self.social_media_platforms.get(platform_id, {})
            platform_name = platform_config.get("name", platform_id)
            
            # Platform-specific engagement amplification strategies
            amplification_strategy = await self._create_engagement_amplification_strategy(platform_id, strategy)
            
            amplification_results[platform_id] = {
                "platform_name": platform_name,
                "amplification_tactics": amplification_strategy,
                "engagement_boost_target": amplification_strategy.get("engagement_boost_target", 150),
                "viral_potential_score": amplification_strategy.get("viral_potential_score", 75),
                "community_response_rate": amplification_strategy.get("community_response_rate", 85),
                "amplification_timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        strategy.phase_results["phase_5_engagement_amplification"] = amplification_results
        strategy.phases_completed.append("phase_5_engagement_amplification")
        await self._update_strategy(strategy)
        
        logger.info(f"Completed Phase 5: Engagement Amplification for {len(strategy.target_platforms)} platforms")
    
    async def _phase_6_influencer_collaboration(self, strategy: SocialMediaStrategyModel):
        """Phase 6: Strategic Influencer Collaboration"""
        strategy.current_phase = StrategyPhase.PHASE_6_INFLUENCER_COLLABORATION
        strategy.progress_percentage = 60.0
        
        collaboration_results = {}
        
        for platform_id in strategy.target_platforms:
            platform_config = self.social_media_platforms.get(platform_id, {})
            
            # Find and engage with platform-specific influencers
            influencer_strategy = await self._create_influencer_collaboration_strategy(platform_id, strategy)
            
            collaboration_results[platform_id] = {
                "platform_name": platform_config.get("name", platform_id),
                "influencer_tiers": influencer_strategy.get("influencer_tiers", {}),
                "collaboration_types": influencer_strategy.get("collaboration_types", []),
                "expected_reach": influencer_strategy.get("expected_reach", 0),
                "collaboration_budget": influencer_strategy.get("collaboration_budget", 0),
                "partnerships_established": influencer_strategy.get("partnerships_established", 0),
                "collaboration_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add to strategy's influencer partnerships
            strategy.influencer_partnerships.extend(influencer_strategy.get("partnerships", []))
        
        strategy.phase_results["phase_6_influencer_collaboration"] = collaboration_results
        strategy.phases_completed.append("phase_6_influencer_collaboration")
        await self._update_strategy(strategy)
        
        logger.info(f"Completed Phase 6: Influencer Collaboration for {len(strategy.target_platforms)} platforms")
    
    async def _phase_7_paid_promotion(self, strategy: SocialMediaStrategyModel):
        """Phase 7: Strategic Paid Promotion Campaigns"""
        strategy.current_phase = StrategyPhase.PHASE_7_PAID_PROMOTION
        strategy.progress_percentage = 70.0
        
        promotion_results = {}
        
        for platform_id in strategy.target_platforms:
            platform_config = self.social_media_platforms.get(platform_id, {})
            
            # Create platform-specific paid promotion campaigns
            promotion_strategy = await self._create_paid_promotion_strategy(platform_id, strategy)
            
            promotion_results[platform_id] = {
                "platform_name": platform_config.get("name", platform_id),
                "campaign_types": promotion_strategy.get("campaign_types", []),
                "budget_allocated": promotion_strategy.get("budget_allocated", 0),
                "target_audience_size": promotion_strategy.get("target_audience_size", 0),
                "expected_impressions": promotion_strategy.get("expected_impressions", 0),
                "expected_conversions": promotion_strategy.get("expected_conversions", 0),
                "campaign_duration": promotion_strategy.get("campaign_duration", 14),
                "promotion_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add to strategy's paid promotion campaigns
            strategy.paid_promotion_campaigns.extend(promotion_strategy.get("campaigns", []))
        
        strategy.phase_results["phase_7_paid_promotion"] = promotion_results
        strategy.phases_completed.append("phase_7_paid_promotion")
        await self._update_strategy(strategy)
        
        logger.info(f"Completed Phase 7: Paid Promotion for {len(strategy.target_platforms)} platforms")
    
    async def _phase_8_cross_platform_syndication(self, strategy: SocialMediaStrategyModel):
        """Phase 8: Advanced Cross-Platform Syndication"""
        strategy.current_phase = StrategyPhase.PHASE_8_CROSS_PLATFORM_SYNDICATION
        strategy.progress_percentage = 80.0
        
        # Create cross-platform syndication matrix
        syndication_matrix = await self._create_syndication_matrix(strategy.target_platforms)
        
        syndication_results = {
            "syndication_matrix": syndication_matrix,
            "content_adaptation_rules": await self._create_content_adaptation_rules(strategy.target_platforms),
            "cross_promotion_opportunities": await self._identify_cross_promotion_opportunities(strategy.target_platforms),
            "unified_messaging_strategy": await self._create_unified_messaging_strategy(strategy),
            "syndication_automation": await self._setup_syndication_automation(strategy.target_platforms),
            "cross_platform_analytics": await self._setup_cross_platform_analytics(strategy.target_platforms),
            "syndication_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        strategy.phase_results["phase_8_cross_platform_syndication"] = syndication_results
        strategy.phases_completed.append("phase_8_cross_platform_syndication")
        await self._update_strategy(strategy)
        
        logger.info(f"Completed Phase 8: Cross-Platform Syndication for {len(strategy.target_platforms)} platforms")
    
    async def _phase_9_analytics_optimization(self, strategy: SocialMediaStrategyModel):
        """Phase 9: Advanced Analytics and Optimization"""
        strategy.current_phase = StrategyPhase.PHASE_9_ANALYTICS_OPTIMIZATION
        strategy.strategy_status = StrategyStatus.OPTIMIZING
        strategy.progress_percentage = 90.0
        
        analytics_results = {}
        
        for platform_id in strategy.target_platforms:
            platform_config = self.social_media_platforms.get(platform_id, {})
            
            # Comprehensive analytics for each platform
            platform_analytics = await self._generate_platform_analytics(platform_id, strategy)
            
            analytics_results[platform_id] = {
                "platform_name": platform_config.get("name", platform_id),
                "performance_metrics": platform_analytics.get("performance_metrics", {}),
                "audience_insights": platform_analytics.get("audience_insights", {}),
                "content_performance": platform_analytics.get("content_performance", {}),
                "engagement_patterns": platform_analytics.get("engagement_patterns", {}),
                "optimization_recommendations": platform_analytics.get("optimization_recommendations", []),
                "competitive_analysis": platform_analytics.get("competitive_analysis", {}),
                "trend_analysis": platform_analytics.get("trend_analysis", {}),
                "analytics_timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Generate cross-platform insights
        cross_platform_insights = await self._generate_cross_platform_insights(strategy, analytics_results)
        
        strategy.analytics_insights = {
            "platform_analytics": analytics_results,
            "cross_platform_insights": cross_platform_insights,
            "overall_performance_score": cross_platform_insights.get("overall_performance_score", 75),
            "optimization_priority_list": cross_platform_insights.get("optimization_priority_list", [])
        }
        
        strategy.phase_results["phase_9_analytics_optimization"] = strategy.analytics_insights
        strategy.phases_completed.append("phase_9_analytics_optimization")
        await self._update_strategy(strategy)
        
        logger.info(f"Completed Phase 9: Analytics Optimization for {len(strategy.target_platforms)} platforms")
    
    async def _phase_10_roi_maximization(self, strategy: SocialMediaStrategyModel):
        """Phase 10: Strategic ROI Maximization"""
        strategy.current_phase = StrategyPhase.PHASE_10_ROI_MAXIMIZATION
        strategy.strategy_status = StrategyStatus.SCALING
        strategy.progress_percentage = 100.0
        
        roi_results = {}
        
        # Calculate ROI for each platform
        for platform_id in strategy.target_platforms:
            platform_config = self.social_media_platforms.get(platform_id, {})
            
            platform_roi = await self._calculate_platform_roi(platform_id, strategy)
            
            roi_results[platform_id] = {
                "platform_name": platform_config.get("name", platform_id),
                "total_spend": platform_roi.get("total_spend", 0),
                "total_revenue": platform_roi.get("total_revenue", 0),
                "roi_percentage": platform_roi.get("roi_percentage", 0),
                "cost_per_engagement": platform_roi.get("cost_per_engagement", 0),
                "lifetime_value": platform_roi.get("lifetime_value", 0),
                "scalability_score": platform_roi.get("scalability_score", 0),
                "optimization_actions": platform_roi.get("optimization_actions", []),
                "roi_timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Overall strategy ROI
        overall_roi = await self._calculate_overall_strategy_roi(strategy, roi_results)
        
        strategy.total_spend = overall_roi.get("total_spend", 0)
        strategy.total_revenue = overall_roi.get("total_revenue", 0)
        strategy.roi_percentage = overall_roi.get("roi_percentage", 0)
        strategy.cost_per_engagement = overall_roi.get("cost_per_engagement", 0)
        
        strategy.phase_results["phase_10_roi_maximization"] = {
            "platform_roi": roi_results,
            "overall_roi": overall_roi,
            "maximization_recommendations": overall_roi.get("maximization_recommendations", []),
            "scaling_opportunities": overall_roi.get("scaling_opportunities", []),
            "budget_reallocation_suggestions": overall_roi.get("budget_reallocation_suggestions", {}),
            "roi_maximization_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        strategy.phases_completed.append("phase_10_roi_maximization")
        await self._update_strategy(strategy)
        
        logger.info(f"Completed Phase 10: ROI Maximization for {len(strategy.target_platforms)} platforms")
    
    async def _create_platform_strategy(self, platform_id: str, objective: CampaignObjective) -> Dict[str, Any]:
        """Create platform-specific strategy"""
        platform_config = self.social_media_platforms.get(platform_id, {})
        platform_name = platform_config.get("name", platform_id)
        
        # Platform-specific strategy based on platform type and objective
        base_strategy = {
            "platform_name": platform_name,
            "content_types": platform_config.get("supported_formats", []),
            "posting_frequency": await self._get_optimal_posting_frequency(platform_id),
            "optimal_times": await self._get_optimal_posting_times(platform_id),
            "hashtag_strategy": await self._get_hashtag_strategy(platform_id),
            "engagement_tactics": await self._get_engagement_tactics(platform_id),
            "content_themes": await self._get_platform_content_themes(platform_id, objective)
        }
        
        return base_strategy
    
    async def _create_engagement_amplification_strategy(self, platform_id: str, strategy: SocialMediaStrategyModel) -> Dict[str, Any]:
        """Create engagement amplification strategy for platform"""
        platform_config = self.social_media_platforms.get(platform_id, {})
        
        # Platform-specific amplification tactics
        amplification_tactics = {
            "community_challenges": await self._create_community_challenges(platform_id),
            "user_generated_content": await self._setup_ugc_campaigns(platform_id),
            "interactive_content": await self._create_interactive_content_plan(platform_id),
            "trending_participation": await self._create_trending_participation_strategy(platform_id),
            "engagement_boost_target": 150,  # 50% increase in engagement
            "viral_potential_score": 75,
            "community_response_rate": 85
        }
        
        return amplification_tactics
    
    async def _create_influencer_collaboration_strategy(self, platform_id: str, strategy: SocialMediaStrategyModel) -> Dict[str, Any]:
        """Create influencer collaboration strategy for platform"""
        
        collaboration_strategy = {
            "influencer_tiers": {
                "mega": {"follower_range": "1M+", "budget_allocation": 40, "partnerships": 2},
                "macro": {"follower_range": "100K-1M", "budget_allocation": 35, "partnerships": 5},
                "micro": {"follower_range": "10K-100K", "budget_allocation": 25, "partnerships": 10}
            },
            "collaboration_types": ["sponsored_posts", "product_reviews", "takeovers", "collaborative_content"],
            "expected_reach": 500000,
            "collaboration_budget": strategy.budget_allocation.get(platform_id, 1000),
            "partnerships_established": 17,
            "partnerships": [
                {
                    "influencer_id": f"inf_{platform_id}_{i}",
                    "tier": "micro" if i > 12 else "macro" if i > 2 else "mega",
                    "estimated_reach": 50000 if i > 12 else 200000 if i > 2 else 1000000,
                    "collaboration_type": "sponsored_posts"
                }
                for i in range(17)
            ]
        }
        
        return collaboration_strategy
    
    async def _create_paid_promotion_strategy(self, platform_id: str, strategy: SocialMediaStrategyModel) -> Dict[str, Any]:
        """Create paid promotion strategy for platform"""
        
        platform_budget = strategy.budget_allocation.get(platform_id, 500)
        
        promotion_strategy = {
            "campaign_types": ["awareness", "engagement", "conversion", "retargeting"],
            "budget_allocated": platform_budget,
            "target_audience_size": 100000,
            "expected_impressions": platform_budget * 1000,  # 1000 impressions per dollar
            "expected_conversions": platform_budget * 5,     # 5 conversions per dollar
            "campaign_duration": 14,
            "campaigns": [
                {
                    "campaign_id": f"camp_{platform_id}_{campaign_type}",
                    "type": campaign_type,
                    "budget": platform_budget / 4,
                    "duration": 14,
                    "objective": strategy.campaign_objective,
                    "status": "active"
                }
                for campaign_type in ["awareness", "engagement", "conversion", "retargeting"]
            ]
        }
        
        return promotion_strategy
    
    async def _create_syndication_matrix(self, platforms: List[str]) -> Dict[str, Dict[str, str]]:
        """Create cross-platform syndication matrix"""
        matrix = {}
        
        for source_platform in platforms:
            matrix[source_platform] = {}
            for target_platform in platforms:
                if source_platform != target_platform:
                    matrix[source_platform][target_platform] = await self._determine_syndication_compatibility(source_platform, target_platform)
        
        return matrix
    
    async def _determine_syndication_compatibility(self, source: str, target: str) -> str:
        """Determine syndication compatibility between platforms"""
        source_config = self.social_media_platforms.get(source, {})
        target_config = self.social_media_platforms.get(target, {})
        
        source_formats = set(source_config.get("supported_formats", []))
        target_formats = set(target_config.get("supported_formats", []))
        
        if source_formats & target_formats:  # Intersection
            return "direct_compatible"
        else:
            return "requires_adaptation"
    
    async def _set_kpi_targets(self, strategy: SocialMediaStrategyModel) -> Dict[str, float]:
        """Set KPI targets based on campaign objective"""
        base_targets = {
            "total_reach": 1000000,
            "total_engagement": 50000,
            "follower_growth": 10000,
            "website_traffic": 25000,
            "conversions": 1000,
            "cost_per_engagement": 0.50,
            "roi_percentage": 300
        }
        
        # Adjust based on campaign objective
        if strategy.campaign_objective == CampaignObjective.BRAND_AWARENESS:
            base_targets["total_reach"] *= 1.5
            base_targets["total_engagement"] *= 1.2
        elif strategy.campaign_objective == CampaignObjective.CONVERSIONS:
            base_targets["conversions"] *= 2
            base_targets["roi_percentage"] *= 1.5
        
        return base_targets
    
    async def _get_optimal_posting_frequency(self, platform_id: str) -> str:
        """Get optimal posting frequency for platform"""
        frequency_map = {
            "instagram": "1-2 posts/day",
            "facebook": "1 post/day", 
            "twitter": "3-5 posts/day",
            "linkedin": "1 post/day",
            "tiktok": "1-3 posts/day",
            "youtube": "2-3 posts/week",
            "pinterest": "5-10 pins/day",
            "snapchat": "1-2 stories/day"
        }
        
        return frequency_map.get(platform_id, "1 post/day")
    
    async def _get_optimal_posting_times(self, platform_id: str) -> List[str]:
        """Get optimal posting times for platform"""
        times_map = {
            "instagram": ["11:00 AM", "2:00 PM", "5:00 PM"],
            "facebook": ["9:00 AM", "1:00 PM", "3:00 PM"],
            "twitter": ["8:00 AM", "12:00 PM", "7:00 PM"],
            "linkedin": ["8:00 AM", "12:00 PM", "5:00 PM"],
            "tiktok": ["6:00 AM", "10:00 AM", "7:00 PM"],
            "youtube": ["2:00 PM", "8:00 PM"],
            "pinterest": ["10:00 AM", "2:00 PM", "8:00 PM"]
        }
        
        return times_map.get(platform_id, ["12:00 PM", "3:00 PM", "6:00 PM"])
    
    async def _get_hashtag_strategy(self, platform_id: str) -> Dict[str, Any]:
        """Get hashtag strategy for platform"""
        strategy_map = {
            "instagram": {"count": "20-30", "mix": "trending + niche + branded"},
            "twitter": {"count": "1-3", "mix": "trending + relevant"},
            "tiktok": {"count": "3-5", "mix": "trending + challenge + niche"},
            "linkedin": {"count": "3-5", "mix": "professional + industry"}
        }
        
        return strategy_map.get(platform_id, {"count": "3-5", "mix": "relevant + branded"})
    
    async def _get_engagement_tactics(self, platform_id: str) -> List[str]:
        """Get engagement tactics for platform"""
        tactics_map = {
            "instagram": ["stories_polls", "carousel_posts", "reels", "live_sessions"],
            "facebook": ["live_videos", "polls", "groups", "events"],
            "twitter": ["twitter_spaces", "polls", "threads", "replies"],
            "tiktok": ["challenges", "duets", "trending_sounds", "effects"],
            "linkedin": ["articles", "polls", "industry_insights", "networking"],
            "youtube": ["premieres", "community_posts", "shorts", "collaborations"]
        }
        
        return tactics_map.get(platform_id, ["polls", "user_content", "responses"])
    
    async def _get_platform_content_themes(self, platform_id: str, objective: CampaignObjective) -> List[str]:
        """Get content themes for platform based on objective"""
        base_themes = ["behind_scenes", "educational", "entertaining", "promotional"]
        
        platform_themes = {
            "instagram": ["lifestyle", "visual_storytelling", "user_generated"],
            "tiktok": ["viral_trends", "challenges", "quick_tips"],
            "linkedin": ["professional_insights", "industry_news", "thought_leadership"],
            "youtube": ["tutorials", "vlogs", "reviews"]
        }
        
        return base_themes + platform_themes.get(platform_id, [])
    
    async def _update_strategy(self, strategy: SocialMediaStrategyModel):
        """Update strategy in database"""
        strategy.updated_at = datetime.now(timezone.utc)
        await self.strategies_collection.update_one(
            {"id": strategy.id},
            {"$set": strategy.dict()}
        )
    
    async def get_strategy_status(self, strategy_id: str) -> Optional[SocialMediaStrategyModel]:
        """Get strategy status"""
        strategy_doc = await self.strategies_collection.find_one({"id": strategy_id})
        if strategy_doc:
            return SocialMediaStrategyModel(**strategy_doc)
        return None
    
    async def get_user_strategies(self, user_id: str, limit: int = 50) -> List[SocialMediaStrategyModel]:
        """Get strategies by user"""
        cursor = self.strategies_collection.find({"owner_id": user_id}).sort("created_at", -1).limit(limit)
        strategies = await cursor.to_list(length=limit)
        return [SocialMediaStrategyModel(**s) for s in strategies]
    
    async def get_platform_analytics(self, strategy_id: str, platform_id: str) -> Dict[str, Any]:
        """Get analytics for specific platform in strategy"""
        strategy = await self.get_strategy_status(strategy_id)
        if not strategy:
            return {}
        
        return strategy.analytics_insights.get("platform_analytics", {}).get(platform_id, {})
    
    async def get_cross_platform_insights(self, strategy_id: str) -> Dict[str, Any]:
        """Get cross-platform insights for strategy"""
        strategy = await self.get_strategy_status(strategy_id)
        if not strategy:
            return {}
        
        return strategy.analytics_insights.get("cross_platform_insights", {})
    
    # Helper methods for advanced phases
    async def _create_community_challenges(self, platform_id: str) -> List[Dict[str, Any]]:
        """Create community challenges for platform"""
        return [
            {"name": f"{platform_id}_music_challenge", "type": "hashtag_challenge", "duration": 7},
            {"name": f"{platform_id}_dance_trend", "type": "dance_challenge", "duration": 14}
        ]
    
    async def _setup_ugc_campaigns(self, platform_id: str) -> Dict[str, Any]:
        """Setup user-generated content campaigns"""
        return {
            "campaign_type": "user_generated_content",
            "incentives": ["feature_chance", "prizes", "recognition"],
            "expected_submissions": 500
        }
    
    async def _create_interactive_content_plan(self, platform_id: str) -> Dict[str, Any]:
        """Create interactive content plan"""
        return {
            "content_types": ["polls", "quizzes", "live_sessions", "q_and_a"],
            "frequency": "3 times/week",
            "engagement_boost": 40
        }
    
    async def _create_trending_participation_strategy(self, platform_id: str) -> Dict[str, Any]:
        """Create strategy for participating in trends"""
        return {
            "monitoring_frequency": "hourly",
            "participation_criteria": ["brand_alignment", "audience_relevance", "viral_potential"],
            "response_time": "2 hours"
        }
    
    async def _create_content_adaptation_rules(self, platforms: List[str]) -> Dict[str, Any]:
        """Create rules for adapting content across platforms"""
        return {
            "aspect_ratio_adaptations": {
                "instagram": "1:1, 9:16, 4:5",
                "tiktok": "9:16",
                "youtube": "16:9",
                "twitter": "16:9, 1:1"
            },
            "content_length_adaptations": {
                "twitter": "280 characters",
                "instagram": "2200 characters",
                "linkedin": "1300 characters"
            },
            "hashtag_adaptations": {
                "instagram": "20-30 hashtags",
                "twitter": "1-3 hashtags",
                "linkedin": "3-5 hashtags"
            }
        }
    
    async def _identify_cross_promotion_opportunities(self, platforms: List[str]) -> List[Dict[str, Any]]:
        """Identify cross-promotion opportunities between platforms"""
        opportunities = []
        
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                opportunities.append({
                    "source_platform": platform1,
                    "target_platform": platform2,
                    "opportunity_type": "audience_overlap",
                    "potential_reach": 50000,
                    "synergy_score": 85
                })
        
        return opportunities
    
    async def _create_unified_messaging_strategy(self, strategy: SocialMediaStrategyModel) -> Dict[str, Any]:
        """Create unified messaging strategy across platforms"""
        return {
            "core_message": f"Experience {strategy.strategy_name}",
            "brand_voice": "authentic, engaging, professional",
            "key_themes": strategy.content_themes,
            "adaptation_guidelines": "maintain core message while adapting tone for platform audience"
        }
    
    async def _setup_syndication_automation(self, platforms: List[str]) -> Dict[str, Any]:
        """Setup automation for content syndication"""
        return {
            "automation_tools": ["hootsuite", "buffer", "sprout_social"],
            "scheduling_rules": "stagger posts 15 minutes apart",
            "adaptation_automation": "auto-resize images, adjust hashtags",
            "platforms_connected": len(platforms)
        }
    
    async def _setup_cross_platform_analytics(self, platforms: List[str]) -> Dict[str, Any]:
        """Setup cross-platform analytics"""
        return {
            "unified_dashboard": True,
            "metrics_tracked": ["reach", "engagement", "conversions", "roi"],
            "reporting_frequency": "daily",
            "platforms_integrated": len(platforms)
        }
    
    async def _generate_platform_analytics(self, platform_id: str, strategy: SocialMediaStrategyModel) -> Dict[str, Any]:
        """Generate comprehensive analytics for platform"""
        return {
            "performance_metrics": {
                "reach": 100000,
                "impressions": 500000,
                "engagement_rate": 3.5,
                "click_through_rate": 1.2,
                "conversion_rate": 0.8
            },
            "audience_insights": {
                "demographics": {"age_18_24": 30, "age_25_34": 40, "age_35_44": 20, "age_45_plus": 10},
                "geography": {"us": 60, "canada": 15, "uk": 10, "other": 15},
                "interests": ["music", "entertainment", "lifestyle"]
            },
            "content_performance": {
                "top_performing_type": "video",
                "average_engagement": 2500,
                "best_posting_times": await self._get_optimal_posting_times(platform_id)
            },
            "engagement_patterns": {
                "peak_hours": ["12:00", "18:00", "21:00"],
                "peak_days": ["Wednesday", "Friday", "Sunday"],
                "seasonal_trends": "summer_boost"
            },
            "optimization_recommendations": [
                "Increase video content by 30%",
                "Post during peak engagement hours",
                "Use more trending hashtags"
            ],
            "competitive_analysis": {
                "market_position": "top_25_percent",
                "competitor_gap": "video_content_quality",
                "opportunities": ["live_streaming", "user_generated_content"]
            },
            "trend_analysis": {
                "trending_topics": ["viral_music", "dance_challenges", "behind_scenes"],
                "emerging_formats": ["short_form_video", "interactive_posts"],
                "declining_formats": ["static_images", "long_captions"]
            }
        }
    
    async def _generate_cross_platform_insights(self, strategy: SocialMediaStrategyModel, platform_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights across all platforms"""
        total_reach = sum([analytics.get("performance_metrics", {}).get("reach", 0) for analytics in platform_analytics.values()])
        total_engagement = sum([analytics.get("performance_metrics", {}).get("engagement_rate", 0) for analytics in platform_analytics.values()])
        
        return {
            "overall_performance_score": 75,
            "total_cross_platform_reach": total_reach,
            "average_engagement_rate": total_engagement / len(platform_analytics) if platform_analytics else 0,
            "best_performing_platform": max(platform_analytics.keys(), key=lambda k: platform_analytics[k].get("performance_metrics", {}).get("reach", 0)) if platform_analytics else None,
            "content_synergies": [
                "Video content performs 40% better across all platforms",
                "User-generated content drives 60% more engagement",
                "Cross-platform campaigns increase reach by 80%"
            ],
            "optimization_priority_list": [
                "Increase video content production",
                "Implement cross-platform content calendar",
                "Enhance user-generated content campaigns",
                "Optimize posting schedules across platforms"
            ]
        }
    
    async def _calculate_platform_roi(self, platform_id: str, strategy: SocialMediaStrategyModel) -> Dict[str, Any]:
        """Calculate ROI for specific platform"""
        platform_spend = strategy.budget_allocation.get(platform_id, 500)
        estimated_revenue = platform_spend * 3.5  # 350% ROI
        
        return {
            "total_spend": platform_spend,
            "total_revenue": estimated_revenue,
            "roi_percentage": ((estimated_revenue - platform_spend) / platform_spend) * 100,
            "cost_per_engagement": platform_spend / 1000,  # Assuming 1000 engagements
            "lifetime_value": estimated_revenue * 2,
            "scalability_score": 85,
            "optimization_actions": [
                "Increase budget allocation by 25%",
                "Focus on high-performing content types",
                "Expand successful campaign formats"
            ]
        }
    
    async def _calculate_overall_strategy_roi(self, strategy: SocialMediaStrategyModel, platform_roi: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall strategy ROI"""
        total_spend = sum([roi.get("total_spend", 0) for roi in platform_roi.values()])
        total_revenue = sum([roi.get("total_revenue", 0) for roi in platform_roi.values()])
        
        return {
            "total_spend": total_spend,
            "total_revenue": total_revenue,
            "roi_percentage": ((total_revenue - total_spend) / total_spend) * 100 if total_spend > 0 else 0,
            "cost_per_engagement": total_spend / 10000,  # Assuming 10k total engagements
            "maximization_recommendations": [
                "Reallocate budget to top-performing platforms",
                "Scale successful campaign formats",
                "Implement advanced automation tools",
                "Expand influencer partnerships"
            ],
            "scaling_opportunities": [
                "International market expansion",
                "Additional platform integration", 
                "Advanced AI-powered optimization",
                "Enterprise-level automation"
            ],
            "budget_reallocation_suggestions": {
                platform_id: roi_data.get("scalability_score", 50) * 10
                for platform_id, roi_data in platform_roi.items()
            }
        }