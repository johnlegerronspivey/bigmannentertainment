"""
Delivery Optimization Service - Function 3: Content Distribution & Delivery Management
Handles content delivery optimization, scheduling strategies, and performance analytics.
"""

import os
import uuid
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from pymongo import MongoClient

class DeliveryStrategy(str, Enum):
    IMMEDIATE = "immediate"
    OPTIMIZED_TIMING = "optimized_timing"
    STAGGERED_RELEASE = "staggered_release"
    REGIONAL_ROLLOUT = "regional_rollout"
    TEST_AND_SCALE = "test_and_scale"

class OptimizationGoal(str, Enum):
    MAX_REACH = "max_reach"
    MAX_REVENUE = "max_revenue"
    FASTEST_DELIVERY = "fastest_delivery"
    QUALITY_FOCUSED = "quality_focused"
    COST_EFFECTIVE = "cost_effective"

class PlatformType(str, Enum):
    STREAMING_MUSIC = "streaming_music"
    STREAMING_VIDEO = "streaming_video"
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    RADIO = "radio"
    BLOCKCHAIN = "blockchain"
    WEB3_MUSIC = "web3_music"
    NFT_MARKETPLACE = "nft_marketplace"
    LIVE_STREAMING = "live_streaming"
    VIDEO_PLATFORM = "video_platform"
    AUDIO_SOCIAL = "audio_social"
    MODEL_AGENCY = "model_agency"
    MODEL_PLATFORM = "model_platform"
    RIGHTS_ORGANIZATION = "rights_organization"

class DeliveryWindow(BaseModel):
    platform: str
    optimal_start_time: datetime
    optimal_end_time: datetime
    audience_peak_hours: List[int]  # Hours of day (0-23)
    timezone: str = "UTC"
    engagement_score: float = 0.0  # 0-100 scale

class DeliveryPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content_id: str
    strategy: DeliveryStrategy
    optimization_goal: OptimizationGoal
    
    # Delivery schedule
    delivery_windows: List[DeliveryWindow] = []
    estimated_completion_time: Optional[datetime] = None
    total_estimated_reach: int = 0
    total_estimated_revenue: float = 0.0
    
    # Optimization results
    platform_priorities: Dict[str, int] = {}  # platform -> priority (1-10)
    recommended_sequence: List[str] = []
    risk_factors: List[str] = []
    confidence_score: float = 0.0  # 0-100 scale
    
    # Performance tracking
    actual_reach: Optional[int] = None
    actual_revenue: Optional[float] = None
    performance_vs_estimate: Optional[float] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class DeliveryAnalytics(BaseModel):
    analytics_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    delivery_plan_id: str
    user_id: str
    
    # Performance metrics
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    success_rate: float = 0.0
    
    # Timing analysis
    average_delivery_time: Optional[float] = None  # hours
    fastest_platform: Optional[str] = None
    slowest_platform: Optional[str] = None
    
    # Reach and engagement
    total_reach: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Revenue tracking
    total_revenue: float = 0.0
    revenue_per_platform: Dict[str, float] = {}
    roi_percentage: float = 0.0
    
    # Platform performance
    platform_performance: Dict[str, Dict[str, Any]] = {}
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DeliveryOptimizationService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        self.delivery_plans_collection = self.db['delivery_plans']
        self.delivery_analytics_collection = self.db['delivery_analytics']
        
        # Platform audience data for optimization
        self.platform_audience_data = self._initialize_audience_data()
        
        # Delivery cost factors
        self.delivery_costs = self._initialize_delivery_costs()
    
    def _initialize_audience_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific audience and engagement data"""
        return {
            "spotify": {
                "peak_hours": [8, 9, 17, 18, 19, 20, 21],  # Commute and evening
                "engagement_score": 85,
                "global_reach": 400000000,
                "avg_processing_time": 48,  # hours
                "success_rate": 95,
                "revenue_multiplier": 1.2,
                "audience_demographics": {"age_18_34": 60, "age_35_54": 30},
                "content_preference": ["music", "podcast"]
            },
            "apple_music": {
                "peak_hours": [7, 8, 18, 19, 20, 21, 22],
                "engagement_score": 80,
                "global_reach": 100000000,
                "avg_processing_time": 72,
                "success_rate": 92,
                "revenue_multiplier": 1.3,
                "audience_demographics": {"age_25_44": 55, "age_18_34": 35},
                "content_preference": ["music", "exclusive_content"]
            },
            "youtube": {
                "peak_hours": [19, 20, 21, 22, 23],  # Prime time
                "engagement_score": 95,
                "global_reach": 2000000000,
                "avg_processing_time": 2,
                "success_rate": 98,
                "revenue_multiplier": 0.8,
                "audience_demographics": {"age_16_34": 70, "age_35_54": 25},
                "content_preference": ["video", "music", "entertainment"]
            },
            "youtube_music": {
                "peak_hours": [8, 9, 17, 18, 19, 20, 21],
                "engagement_score": 82,
                "global_reach": 80000000,
                "avg_processing_time": 24,
                "success_rate": 94,
                "revenue_multiplier": 0.9,
                "audience_demographics": {"age_18_34": 65, "age_35_54": 25},
                "content_preference": ["music", "video"]
            },
            "tiktok": {
                "peak_hours": [18, 19, 20, 21, 22, 23, 0],  # Evening and late night
                "engagement_score": 90,
                "global_reach": 1000000000,
                "avg_processing_time": 4,
                "success_rate": 96,
                "revenue_multiplier": 0.6,
                "audience_demographics": {"age_16_24": 60, "age_25_34": 30},
                "content_preference": ["short_video", "music", "viral_content"]
            },
            "instagram": {
                "peak_hours": [11, 12, 17, 18, 19, 20],
                "engagement_score": 88,
                "global_reach": 2000000000,
                "avg_processing_time": 2,
                "success_rate": 97,
                "revenue_multiplier": 0.4,
                "audience_demographics": {"age_18_34": 65, "age_35_54": 25},
                "content_preference": ["image", "video", "story"]
            },
            "facebook": {
                "peak_hours": [12, 13, 18, 19, 20, 21],
                "engagement_score": 75,
                "global_reach": 2800000000,
                "avg_processing_time": 1,
                "success_rate": 94,
                "revenue_multiplier": 0.5,
                "audience_demographics": {"age_25_54": 60, "age_35_65": 30},
                "content_preference": ["video", "article", "image"]
            },
            "soundcloud": {
                "peak_hours": [20, 21, 22, 23, 0, 1],  # Late evening/night
                "engagement_score": 78,
                "global_reach": 175000000,
                "avg_processing_time": 1,
                "success_rate": 93,
                "revenue_multiplier": 0.7,
                "audience_demographics": {"age_18_34": 70, "age_16_24": 20},
                "content_preference": ["music", "podcast", "independent_content"]
            },
            "amazon_music": {
                "peak_hours": [8, 9, 17, 18, 19, 20],
                "engagement_score": 76,
                "global_reach": 75000000,
                "avg_processing_time": 96,
                "success_rate": 91,
                "revenue_multiplier": 1.1,
                "audience_demographics": {"age_25_54": 65, "age_35_65": 25},
                "content_preference": ["music", "audiobook"]
            },
            "tidal": {
                "peak_hours": [19, 20, 21, 22],
                "engagement_score": 85,
                "global_reach": 5000000,
                "avg_processing_time": 120,
                "success_rate": 89,
                "revenue_multiplier": 1.5,
                "audience_demographics": {"age_25_44": 50, "age_18_34": 35},
                "content_preference": ["high_quality_music", "exclusive_content"]
            }
        }
    
    def _initialize_delivery_costs(self) -> Dict[str, float]:
        """Initialize delivery cost factors per platform"""
        return {
            "spotify": 0.05,      # Per delivery cost
            "apple_music": 0.08,
            "youtube": 0.02,
            "youtube_music": 0.04,
            "tiktok": 0.01,
            "instagram": 0.01,
            "facebook": 0.02,
            "soundcloud": 0.03,
            "amazon_music": 0.06,
            "tidal": 0.10
        }
    
    async def create_delivery_plan(self, 
                                 user_id: str,
                                 content_id: str,
                                 target_platforms: List[str],
                                 strategy: DeliveryStrategy = DeliveryStrategy.OPTIMIZED_TIMING,
                                 optimization_goal: OptimizationGoal = OptimizationGoal.MAX_REACH,
                                 target_timezone: str = "UTC",
                                 content_type: str = "music") -> DeliveryPlan:
        """Create an optimized delivery plan"""
        
        # Create base delivery plan
        delivery_plan = DeliveryPlan(
            user_id=user_id,
            content_id=content_id,
            strategy=strategy,
            optimization_goal=optimization_goal
        )
        
        # Generate delivery windows for each platform
        delivery_windows = []
        for platform in target_platforms:
            if platform in self.platform_audience_data:
                window = self._generate_delivery_window(platform, target_timezone, content_type)
                delivery_windows.append(window)
        
        delivery_plan.delivery_windows = delivery_windows
        
        # Optimize delivery sequence based on strategy and goal
        delivery_plan = await self._optimize_delivery_sequence(delivery_plan)
        
        # Calculate estimates
        delivery_plan.total_estimated_reach = self._calculate_total_reach(target_platforms)
        delivery_plan.total_estimated_revenue = self._calculate_total_revenue(target_platforms, optimization_goal)
        delivery_plan.estimated_completion_time = self._calculate_completion_time(delivery_plan)
        
        # Assess risks and confidence
        delivery_plan.risk_factors = self._assess_risk_factors(target_platforms, strategy)
        delivery_plan.confidence_score = self._calculate_confidence_score(delivery_plan)
        
        # Store in MongoDB
        plan_dict = delivery_plan.dict()
        # Convert datetime objects for MongoDB
        for key, value in plan_dict.items():
            if isinstance(value, datetime):
                plan_dict[key] = value.isoformat()
        
        # Handle nested datetime objects in delivery_windows
        for i, window in enumerate(plan_dict.get('delivery_windows', [])):
            for dt_field in ['optimal_start_time', 'optimal_end_time']:
                if dt_field in window and isinstance(window[dt_field], datetime):
                    plan_dict['delivery_windows'][i][dt_field] = window[dt_field].isoformat()
        
        result = self.delivery_plans_collection.insert_one(plan_dict)
        delivery_plan.plan_id = str(result.inserted_id)
        
        return delivery_plan
    
    def _generate_delivery_window(self, platform: str, target_timezone: str, content_type: str) -> DeliveryWindow:
        """Generate optimal delivery window for a platform"""
        
        platform_data = self.platform_audience_data.get(platform, {})
        peak_hours = platform_data.get("peak_hours", [19, 20, 21])
        engagement_score = platform_data.get("engagement_score", 75)
        
        # Calculate optimal start time (beginning of peak hours)
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=peak_hours[0], minute=0, second=0, microsecond=0)
        
        # If we've passed today's optimal time, schedule for tomorrow
        if now.hour >= peak_hours[-1]:
            today_start += timedelta(days=1)
        
        # Calculate optimal end time (end of peak hours)
        optimal_end = today_start.replace(hour=peak_hours[-1], minute=59, second=59)
        
        return DeliveryWindow(
            platform=platform,
            optimal_start_time=today_start,
            optimal_end_time=optimal_end,
            audience_peak_hours=peak_hours,
            timezone=target_timezone,
            engagement_score=engagement_score
        )
    
    async def _optimize_delivery_sequence(self, plan: DeliveryPlan) -> DeliveryPlan:
        """Optimize the delivery sequence based on strategy and goal"""
        
        platforms = [window.platform for window in plan.delivery_windows]
        
        if plan.strategy == DeliveryStrategy.IMMEDIATE:
            # All platforms simultaneously, prioritize by processing speed
            sequence = sorted(platforms, 
                            key=lambda p: self.platform_audience_data.get(p, {}).get("avg_processing_time", 24))
            priorities = {platform: 10 for platform in platforms}  # All high priority
            
        elif plan.strategy == DeliveryStrategy.OPTIMIZED_TIMING:
            # Sequence based on optimal delivery windows and engagement
            sequence = sorted(platforms,
                            key=lambda p: (
                                self.platform_audience_data.get(p, {}).get("engagement_score", 75),
                                -self.platform_audience_data.get(p, {}).get("avg_processing_time", 24)
                            ), reverse=True)
            
            # Assign priorities based on optimization goal
            priorities = self._assign_priorities_by_goal(platforms, plan.optimization_goal)
            
        elif plan.strategy == DeliveryStrategy.STAGGERED_RELEASE:
            # Release to fastest platforms first, then slower ones
            sequence = sorted(platforms,
                            key=lambda p: self.platform_audience_data.get(p, {}).get("avg_processing_time", 24))
            priorities = {platform: max(1, 11 - i) for i, platform in enumerate(sequence)}
            
        elif plan.strategy == DeliveryStrategy.REGIONAL_ROLLOUT:
            # Prioritize by global reach and regional preferences
            sequence = sorted(platforms,
                            key=lambda p: self.platform_audience_data.get(p, {}).get("global_reach", 1000000),
                            reverse=True)
            priorities = self._assign_priorities_by_reach(platforms)
            
        elif plan.strategy == DeliveryStrategy.TEST_AND_SCALE:
            # Start with platforms that have high success rates
            sequence = sorted(platforms,
                            key=lambda p: (
                                self.platform_audience_data.get(p, {}).get("success_rate", 90),
                                self.platform_audience_data.get(p, {}).get("engagement_score", 75)
                            ), reverse=True)
            priorities = {platform: 8 if i < len(platforms)//2 else 5 for i, platform in enumerate(sequence)}
        
        else:
            # Default sequence
            sequence = platforms
            priorities = {platform: 7 for platform in platforms}
        
        plan.recommended_sequence = sequence
        plan.platform_priorities = priorities
        
        return plan
    
    def _assign_priorities_by_goal(self, platforms: List[str], goal: OptimizationGoal) -> Dict[str, int]:
        """Assign platform priorities based on optimization goal"""
        
        priorities = {}
        
        if goal == OptimizationGoal.MAX_REACH:
            # Prioritize by global reach
            for platform in platforms:
                reach = self.platform_audience_data.get(platform, {}).get("global_reach", 1000000)
                if reach > 1000000000:  # Billion+
                    priorities[platform] = 10
                elif reach > 100000000:  # 100M+
                    priorities[platform] = 8
                elif reach > 50000000:   # 50M+
                    priorities[platform] = 6
                else:
                    priorities[platform] = 4
                    
        elif goal == OptimizationGoal.MAX_REVENUE:
            # Prioritize by revenue multiplier
            for platform in platforms:
                multiplier = self.platform_audience_data.get(platform, {}).get("revenue_multiplier", 1.0)
                if multiplier >= 1.3:
                    priorities[platform] = 10
                elif multiplier >= 1.0:
                    priorities[platform] = 8
                elif multiplier >= 0.7:
                    priorities[platform] = 6
                else:
                    priorities[platform] = 4
                    
        elif goal == OptimizationGoal.FASTEST_DELIVERY:
            # Prioritize by processing time (inverse)
            for platform in platforms:
                processing_time = self.platform_audience_data.get(platform, {}).get("avg_processing_time", 24)
                if processing_time <= 4:    # 4 hours or less
                    priorities[platform] = 10
                elif processing_time <= 24:  # 1 day
                    priorities[platform] = 8
                elif processing_time <= 72:  # 3 days
                    priorities[platform] = 6
                else:
                    priorities[platform] = 4
                    
        elif goal == OptimizationGoal.QUALITY_FOCUSED:
            # Prioritize by engagement score and success rate
            for platform in platforms:
                engagement = self.platform_audience_data.get(platform, {}).get("engagement_score", 75)
                success_rate = self.platform_audience_data.get(platform, {}).get("success_rate", 90)
                combined_score = (engagement + success_rate) / 2
                
                if combined_score >= 90:
                    priorities[platform] = 10
                elif combined_score >= 85:
                    priorities[platform] = 8
                elif combined_score >= 80:
                    priorities[platform] = 6
                else:
                    priorities[platform] = 4
                    
        elif goal == OptimizationGoal.COST_EFFECTIVE:
            # Prioritize by low delivery costs and high success rates
            for platform in platforms:
                cost = self.delivery_costs.get(platform, 0.05)
                success_rate = self.platform_audience_data.get(platform, {}).get("success_rate", 90)
                efficiency_score = success_rate / (cost * 100)  # Higher is better
                
                if efficiency_score >= 20:
                    priorities[platform] = 10
                elif efficiency_score >= 15:
                    priorities[platform] = 8
                elif efficiency_score >= 10:
                    priorities[platform] = 6
                else:
                    priorities[platform] = 4
        
        else:
            # Default equal priority
            priorities = {platform: 7 for platform in platforms}
        
        return priorities
    
    def _assign_priorities_by_reach(self, platforms: List[str]) -> Dict[str, int]:
        """Assign priorities based on global reach"""
        priorities = {}
        
        for platform in platforms:
            reach = self.platform_audience_data.get(platform, {}).get("global_reach", 1000000)
            if reach > 2000000000:      # 2B+
                priorities[platform] = 10
            elif reach > 1000000000:    # 1B+
                priorities[platform] = 9
            elif reach > 500000000:     # 500M+
                priorities[platform] = 8
            elif reach > 100000000:     # 100M+
                priorities[platform] = 7
            elif reach > 50000000:      # 50M+
                priorities[platform] = 6
            else:
                priorities[platform] = 5
        
        return priorities
    
    def _calculate_total_reach(self, platforms: List[str]) -> int:
        """Calculate estimated total reach across platforms"""
        total_reach = 0
        
        for platform in platforms:
            platform_reach = self.platform_audience_data.get(platform, {}).get("global_reach", 1000000)
            total_reach += platform_reach
        
        # Apply overlap reduction factor (people using multiple platforms)
        overlap_factor = min(0.4, len(platforms) * 0.05)  # Max 40% overlap
        unique_reach = int(total_reach * (1 - overlap_factor))
        
        return unique_reach
    
    def _calculate_total_revenue(self, platforms: List[str], goal: OptimizationGoal) -> float:
        """Calculate estimated total revenue across platforms"""
        base_revenue_per_platform = 100.0  # Base estimate per platform
        total_revenue = 0.0
        
        for platform in platforms:
            multiplier = self.platform_audience_data.get(platform, {}).get("revenue_multiplier", 1.0)
            platform_revenue = base_revenue_per_platform * multiplier
            
            # Apply goal-specific adjustments
            if goal == OptimizationGoal.MAX_REVENUE:
                platform_revenue *= 1.2  # 20% boost for revenue-focused strategy
            elif goal == OptimizationGoal.COST_EFFECTIVE:
                platform_revenue *= 0.8  # Conservative estimate
            
            total_revenue += platform_revenue
        
        return round(total_revenue, 2)
    
    def _calculate_completion_time(self, plan: DeliveryPlan) -> datetime:
        """Calculate estimated completion time for the delivery plan"""
        
        if not plan.delivery_windows:
            return datetime.now(timezone.utc) + timedelta(hours=24)
        
        if plan.strategy == DeliveryStrategy.IMMEDIATE:
            # All platforms simultaneously - completion time is the slowest platform
            max_processing_time = max(
                self.platform_audience_data.get(window.platform, {}).get("avg_processing_time", 24)
                for window in plan.delivery_windows
            )
            return datetime.now(timezone.utc) + timedelta(hours=max_processing_time)
        
        elif plan.strategy == DeliveryStrategy.STAGGERED_RELEASE:
            # Sequential release - sum of processing times with some overlap
            total_time = sum(
                self.platform_audience_data.get(window.platform, {}).get("avg_processing_time", 24)
                for window in plan.delivery_windows
            )
            # Allow 50% overlap between platforms
            adjusted_time = total_time * 0.7
            return datetime.now(timezone.utc) + timedelta(hours=adjusted_time)
        
        else:
            # Other strategies - estimate based on average processing time
            avg_processing_time = sum(
                self.platform_audience_data.get(window.platform, {}).get("avg_processing_time", 24)
                for window in plan.delivery_windows
            ) / len(plan.delivery_windows)
            
            return datetime.now(timezone.utc) + timedelta(hours=avg_processing_time * 1.5)
    
    def _assess_risk_factors(self, platforms: List[str], strategy: DeliveryStrategy) -> List[str]:
        """Assess potential risk factors for the delivery plan"""
        
        risks = []
        
        # Platform-specific risks
        for platform in platforms:
            platform_data = self.platform_audience_data.get(platform, {})
            success_rate = platform_data.get("success_rate", 90)
            
            if success_rate < 92:
                risks.append(f"Lower success rate on {platform} ({success_rate}%)")
            
            processing_time = platform_data.get("avg_processing_time", 24)
            if processing_time > 96:  # More than 4 days
                risks.append(f"Long processing time on {platform} ({processing_time} hours)")
        
        # Strategy-specific risks
        if strategy == DeliveryStrategy.IMMEDIATE:
            if len(platforms) > 5:
                risks.append("Simultaneous delivery to many platforms may cause bottlenecks")
        
        elif strategy == DeliveryStrategy.STAGGERED_RELEASE:
            risks.append("Sequential delivery may delay overall completion")
        
        elif strategy == DeliveryStrategy.TEST_AND_SCALE:
            risks.append("Test phase results may require plan adjustments")
        
        # Content type risks (would be determined by content analysis)
        if len(platforms) > 8:
            risks.append("High platform count increases complexity and failure risk")
        
        return risks
    
    def _calculate_confidence_score(self, plan: DeliveryPlan) -> float:
        """Calculate confidence score for the delivery plan"""
        
        if not plan.delivery_windows:
            return 50.0
        
        # Base confidence factors
        platform_reliability = sum(
            self.platform_audience_data.get(window.platform, {}).get("success_rate", 90)
            for window in plan.delivery_windows
        ) / len(plan.delivery_windows)
        
        # Strategy confidence multiplier
        strategy_confidence = {
            DeliveryStrategy.IMMEDIATE: 0.85,
            DeliveryStrategy.OPTIMIZED_TIMING: 0.95,
            DeliveryStrategy.STAGGERED_RELEASE: 0.90,
            DeliveryStrategy.REGIONAL_ROLLOUT: 0.80,
            DeliveryStrategy.TEST_AND_SCALE: 0.75
        }
        
        strategy_factor = strategy_confidence.get(plan.strategy, 0.85)
        
        # Risk factor reduction
        risk_penalty = len(plan.risk_factors) * 5  # 5% penalty per risk
        
        # Calculate final confidence
        confidence = (platform_reliability * strategy_factor) - risk_penalty
        confidence = max(20.0, min(98.0, confidence))  # Clamp between 20-98%
        
        return round(confidence, 1)
    
    async def get_delivery_plan(self, plan_id: str, user_id: str) -> Optional[DeliveryPlan]:
        """Get a delivery plan by ID"""
        try:
            plan_data = self.delivery_plans_collection.find_one({
                "plan_id": plan_id,
                "user_id": user_id
            })
            
            if plan_data:
                plan_data['_id'] = str(plan_data['_id'])
                return DeliveryPlan(**plan_data)
            
            return None
        except Exception as e:
            print(f"Error retrieving delivery plan: {e}")
            return None
    
    async def list_user_delivery_plans(self, user_id: str, limit: int = 50, offset: int = 0) -> List[DeliveryPlan]:
        """List delivery plans for a user"""
        try:
            cursor = self.delivery_plans_collection.find({"user_id": user_id}).sort("created_at", -1).skip(offset).limit(limit)
            
            plans = []
            for plan_data in cursor:
                try:
                    plan_data['_id'] = str(plan_data['_id'])
                    plans.append(DeliveryPlan(**plan_data))
                except Exception as e:
                    print(f"Error parsing delivery plan: {e}")
                    continue
            
            return plans
        except Exception as e:
            print(f"Error listing delivery plans: {e}")
            return []
    
    async def update_delivery_performance(self, plan_id: str, user_id: str, 
                                        actual_reach: int, actual_revenue: float) -> bool:
        """Update delivery plan with actual performance data"""
        
        try:
            plan = await self.get_delivery_plan(plan_id, user_id)
            if not plan:
                return False
            
            # Calculate performance vs estimate
            reach_performance = (actual_reach / plan.total_estimated_reach * 100) if plan.total_estimated_reach > 0 else 0
            revenue_performance = (actual_revenue / plan.total_estimated_revenue * 100) if plan.total_estimated_revenue > 0 else 0
            avg_performance = (reach_performance + revenue_performance) / 2
            
            update_data = {
                "actual_reach": actual_reach,
                "actual_revenue": actual_revenue,
                "performance_vs_estimate": round(avg_performance, 2),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            self.delivery_plans_collection.update_one(
                {"plan_id": plan_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating delivery performance: {e}")
            return False
    
    async def analyze_delivery_performance(self, user_id: str, days: int = 30) -> DeliveryAnalytics:
        """Analyze delivery performance over a time period"""
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get delivery plans from the period
            cursor = self.delivery_plans_collection.find({
                "user_id": user_id,
                "created_at": {"$gte": cutoff_date.isoformat()}
            })
            
            total_deliveries = 0
            successful_deliveries = 0
            total_reach = 0
            total_revenue = 0.0
            platform_performance = {}
            delivery_times = []
            
            for plan_data in cursor:
                total_deliveries += 1
                
                # Check if plan was successful (has actual performance data)
                if plan_data.get("actual_reach") and plan_data.get("actual_revenue"):
                    successful_deliveries += 1
                    total_reach += plan_data["actual_reach"]
                    total_revenue += plan_data["actual_revenue"]
                    
                    # Calculate delivery time if available
                    if plan_data.get("estimated_completion_time") and plan_data.get("updated_at"):
                        estimated_time = datetime.fromisoformat(plan_data["estimated_completion_time"])
                        actual_time = datetime.fromisoformat(plan_data["updated_at"])
                        delivery_time = (actual_time - estimated_time).total_seconds() / 3600  # hours
                        delivery_times.append(delivery_time)
                
                # Aggregate platform performance
                for window in plan_data.get("delivery_windows", []):
                    platform = window["platform"]
                    if platform not in platform_performance:
                        platform_performance[platform] = {
                            "total_uses": 0,
                            "successful_uses": 0,
                            "total_reach": 0,
                            "total_revenue": 0.0
                        }
                    
                    platform_performance[platform]["total_uses"] += 1
                    if plan_data.get("actual_reach"):
                        platform_performance[platform]["successful_uses"] += 1
            
            # Calculate metrics
            success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else None
            
            # Find fastest and slowest platforms
            fastest_platform = None
            slowest_platform = None
            if platform_performance:
                # This would be based on actual performance data in a real implementation
                fastest_platform = min(platform_performance.keys(), 
                                     key=lambda p: self.platform_audience_data.get(p, {}).get("avg_processing_time", 24))
                slowest_platform = max(platform_performance.keys(),
                                     key=lambda p: self.platform_audience_data.get(p, {}).get("avg_processing_time", 24))
            
            analytics = DeliveryAnalytics(
                delivery_plan_id="aggregate",
                user_id=user_id,
                total_deliveries=total_deliveries,
                successful_deliveries=successful_deliveries,
                failed_deliveries=total_deliveries - successful_deliveries,
                success_rate=round(success_rate, 2),
                average_delivery_time=avg_delivery_time,
                fastest_platform=fastest_platform,
                slowest_platform=slowest_platform,
                total_reach=total_reach,
                total_revenue=total_revenue,
                platform_performance=platform_performance
            )
            
            # Store analytics
            analytics_dict = analytics.dict()
            # Convert datetime objects for MongoDB
            for key, value in analytics_dict.items():
                if isinstance(value, datetime):
                    analytics_dict[key] = value.isoformat()
            
            self.delivery_analytics_collection.insert_one(analytics_dict)
            
            return analytics
            
        except Exception as e:
            print(f"Error analyzing delivery performance: {e}")
            return DeliveryAnalytics(delivery_plan_id="error", user_id=user_id)
    
    def get_platform_recommendations(self, content_type: str, target_audience: str, 
                                   budget_level: str = "medium") -> List[Dict[str, Any]]:
        """Get platform recommendations based on content and audience"""
        
        recommendations = []
        
        for platform, data in self.platform_audience_data.items():
            # Check content type compatibility
            content_preferences = data.get("content_preference", [])
            content_match = any(content_type.lower() in pref.lower() for pref in content_preferences)
            
            if not content_match:
                continue
            
            # Calculate recommendation score
            engagement_score = data.get("engagement_score", 75)
            success_rate = data.get("success_rate", 90)
            reach = data.get("global_reach", 1000000)
            cost = self.delivery_costs.get(platform, 0.05)
            
            # Normalize reach (0-100 scale)
            normalized_reach = min(100, (reach / 2000000000) * 100)  # Based on max reach (2B)
            
            # Calculate cost effectiveness (higher is better)
            cost_effectiveness = (success_rate / (cost * 100)) * 10
            
            # Combined recommendation score
            recommendation_score = (
                engagement_score * 0.3 +
                success_rate * 0.3 +
                normalized_reach * 0.2 +
                cost_effectiveness * 0.2
            )
            
            # Budget level adjustments
            if budget_level == "low" and cost > 0.05:
                recommendation_score *= 0.8
            elif budget_level == "high" and cost < 0.03:
                recommendation_score *= 1.2
            
            recommendations.append({
                "platform": platform,
                "recommendation_score": round(recommendation_score, 1),
                "engagement_score": engagement_score,
                "success_rate": success_rate,
                "estimated_reach": reach,
                "cost_per_delivery": cost,
                "processing_time_hours": data.get("avg_processing_time", 24),
                "content_match": content_match,
                "reasoning": self._generate_recommendation_reasoning(platform, data, recommendation_score)
            })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _generate_recommendation_reasoning(self, platform: str, data: Dict[str, Any], 
                                         score: float) -> str:
        """Generate human-readable reasoning for platform recommendation"""
        
        reasons = []
        
        engagement = data.get("engagement_score", 75)
        if engagement >= 85:
            reasons.append("high user engagement")
        elif engagement >= 75:
            reasons.append("good user engagement")
        
        success_rate = data.get("success_rate", 90)
        if success_rate >= 95:
            reasons.append("excellent success rate")
        elif success_rate >= 90:
            reasons.append("high success rate")
        
        reach = data.get("global_reach", 1000000)
        if reach >= 1000000000:
            reasons.append("massive global reach")
        elif reach >= 100000000:
            reasons.append("large audience base")
        
        processing_time = data.get("avg_processing_time", 24)
        if processing_time <= 4:
            reasons.append("fast processing time")
        elif processing_time <= 24:
            reasons.append("reasonable processing time")
        
        cost = self.delivery_costs.get(platform, 0.05)
        if cost <= 0.02:
            reasons.append("low delivery costs")
        elif cost <= 0.05:
            reasons.append("moderate delivery costs")
        
        if not reasons:
            reasons.append("balanced performance metrics")
        
        return f"Recommended due to {', '.join(reasons)}."
    
    def get_available_platforms(self) -> Dict[str, Any]:
        """Get all available platforms with metadata"""
        platforms = {}
        
        for platform_id, data in self.platform_audience_data.items():
            platforms[platform_id] = {
                "id": platform_id,
                "name": platform_id.replace("_", " ").title(),
                "engagement_score": data.get("engagement_score", 75),
                "success_rate": data.get("success_rate", 90),
                "global_reach": data.get("global_reach", 1000000),
                "avg_processing_time": data.get("avg_processing_time", 24),
                "revenue_multiplier": data.get("revenue_multiplier", 1.0),
                "peak_hours": data.get("peak_hours", [19, 20, 21]),
                "audience_demographics": data.get("audience_demographics", {}),
                "content_preferences": data.get("content_preference", []),
                "delivery_cost": self.delivery_costs.get(platform_id, 0.05)
            }
        
        return platforms
    
    def get_platforms_by_type(self, platform_type: PlatformType) -> List[Dict[str, Any]]:
        """Get platforms filtered by type"""
        # Map platform types to actual platforms
        type_mapping = {
            PlatformType.STREAMING_MUSIC: ["spotify", "apple_music", "youtube_music", "amazon_music", "tidal", "soundcloud"],
            PlatformType.SOCIAL_MEDIA: ["instagram", "facebook", "tiktok"],
            PlatformType.VIDEO_PLATFORM: ["youtube"],
            PlatformType.PODCAST: [],
            PlatformType.RADIO: [],
            PlatformType.BLOCKCHAIN: [],
            PlatformType.WEB3_MUSIC: [],
            PlatformType.NFT_MARKETPLACE: [],
            PlatformType.LIVE_STREAMING: [],
            PlatformType.AUDIO_SOCIAL: [],
            PlatformType.MODEL_AGENCY: [],
            PlatformType.MODEL_PLATFORM: [],
            PlatformType.RIGHTS_ORGANIZATION: []
        }
        
        platform_ids = type_mapping.get(platform_type, [])
        platforms = []
        
        for platform_id in platform_ids:
            if platform_id in self.platform_audience_data:
                data = self.platform_audience_data[platform_id]
                platforms.append({
                    "id": platform_id,
                    "name": platform_id.replace("_", " ").title(),
                    "type": platform_type.value,
                    "engagement_score": data.get("engagement_score", 75),
                    "success_rate": data.get("success_rate", 90),
                    "global_reach": data.get("global_reach", 1000000),
                    "avg_processing_time": data.get("avg_processing_time", 24),
                    "revenue_multiplier": data.get("revenue_multiplier", 1.0),
                    "delivery_cost": self.delivery_costs.get(platform_id, 0.05)
                })
        
        return platforms