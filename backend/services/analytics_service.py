"""
Analytics Service - Function 4: Content Analytics & Performance Monitoring
Handles real-time content performance tracking, ROI analysis, and advanced analytics.
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
import statistics
from collections import defaultdict

class MetricType(str, Enum):
    VIEWS = "views"
    STREAMS = "streams"
    DOWNLOADS = "downloads"
    SHARES = "shares"
    LIKES = "likes"
    COMMENTS = "comments"
    REVENUE = "revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"

class Timeframe(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class AnalyticsEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content_id: str
    platform: str
    metric_type: MetricType
    value: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = {}
    
    # Geo and demographic data
    country: Optional[str] = None
    region: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    
    # Technical data
    device_type: Optional[str] = None
    browser: Optional[str] = None
    referrer: Optional[str] = None

class ContentPerformance(BaseModel):
    content_id: str
    user_id: str
    content_title: str
    content_type: str
    
    # Core metrics
    total_views: int = 0
    total_streams: int = 0
    total_downloads: int = 0
    total_shares: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_revenue: float = 0.0
    
    # Calculated metrics
    engagement_rate: float = 0.0
    average_watch_time: Optional[float] = None
    completion_rate: float = 0.0
    viral_coefficient: float = 0.0
    
    # Platform breakdown
    platform_metrics: Dict[str, Dict[str, Any]] = {}
    
    # Time-based performance
    daily_metrics: Dict[str, Dict[str, float]] = {}
    weekly_trends: Dict[str, float] = {}
    monthly_totals: Dict[str, float] = {}
    
    # Geographic performance
    country_breakdown: Dict[str, Dict[str, float]] = {}
    
    # Demographic insights
    age_group_breakdown: Dict[str, Dict[str, float]] = {}
    gender_breakdown: Dict[str, Dict[str, float]] = {}
    
    # Performance benchmarks
    industry_percentile: Optional[float] = None
    platform_ranking: Optional[int] = None
    
    # Timestamps
    first_published: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ROIAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    user_id: str
    
    # Investment costs
    production_cost: float = 0.0
    marketing_cost: float = 0.0
    distribution_cost: float = 0.0
    platform_fees: float = 0.0
    total_investment: float = 0.0
    
    # Revenue streams
    streaming_revenue: float = 0.0
    download_revenue: float = 0.0
    licensing_revenue: float = 0.0
    merchandise_revenue: float = 0.0
    sponsorship_revenue: float = 0.0
    total_revenue: float = 0.0
    
    # ROI calculations
    net_profit: float = 0.0
    roi_percentage: float = 0.0
    payback_period_days: Optional[int] = None
    break_even_point: Optional[datetime] = None
    
    # Performance indicators
    revenue_per_view: float = 0.0
    revenue_per_stream: float = 0.0
    cost_per_acquisition: float = 0.0
    lifetime_value: float = 0.0
    
    # Projections
    projected_30_day_revenue: float = 0.0
    projected_90_day_revenue: float = 0.0
    projected_annual_revenue: float = 0.0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PlatformAnalytics(BaseModel):
    platform_id: str
    platform_name: str
    user_id: str
    
    # Content volume
    total_content_pieces: int = 0
    active_content_pieces: int = 0
    top_performing_content: List[str] = []
    
    # Performance metrics
    total_views: int = 0
    total_revenue: float = 0.0
    average_engagement_rate: float = 0.0
    average_completion_rate: float = 0.0
    
    # Efficiency metrics
    content_success_rate: float = 0.0  # % of content that meets success criteria
    average_roi: float = 0.0
    revenue_per_content: float = 0.0
    cost_efficiency: float = 0.0
    
    # Trend analysis
    growth_rate_30d: float = 0.0
    growth_rate_90d: float = 0.0
    momentum_score: float = 0.0  # Trending up/down indicator
    
    # Audience insights
    primary_demographics: Dict[str, Any] = {}
    geographic_distribution: Dict[str, float] = {}
    peak_engagement_hours: List[int] = []
    
    # Recommendations
    optimization_suggestions: List[str] = []
    content_strategy_insights: List[str] = []
    
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnalyticsService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        
        # Collections
        self.events_collection = self.db['analytics_events']
        self.performance_collection = self.db['content_performance']
        self.roi_collection = self.db['roi_analysis']
        self.platform_analytics_collection = self.db['platform_analytics']
        
        # Create indexes for better performance
        self._create_indexes()
        
        # Industry benchmarks for comparison
        self.industry_benchmarks = self._initialize_benchmarks()
    
    def _create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Analytics events indexes
            self.events_collection.create_index([("user_id", 1), ("timestamp", -1)])
            self.events_collection.create_index([("content_id", 1), ("timestamp", -1)])
            self.events_collection.create_index([("platform", 1), ("timestamp", -1)])
            self.events_collection.create_index([("metric_type", 1), ("timestamp", -1)])
            
            # Performance collection indexes
            self.performance_collection.create_index([("user_id", 1), ("last_updated", -1)])
            self.performance_collection.create_index([("content_id", 1)])
            
            # ROI collection indexes
            self.roi_collection.create_index([("user_id", 1), ("updated_at", -1)])
            self.roi_collection.create_index([("content_id", 1)])
            
            print("✅ Analytics database indexes created successfully")
        except Exception as e:
            print(f"⚠️ Error creating analytics indexes: {e}")
    
    def _initialize_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Initialize industry benchmarks for performance comparison"""
        return {
            "music": {
                "engagement_rate": 3.2,
                "completion_rate": 68.5,
                "viral_coefficient": 0.8,
                "revenue_per_stream": 0.004
            },
            "video": {
                "engagement_rate": 4.8,
                "completion_rate": 45.2,
                "viral_coefficient": 1.2,
                "revenue_per_view": 0.002
            },
            "podcast": {
                "engagement_rate": 12.5,
                "completion_rate": 78.3,
                "viral_coefficient": 0.3,
                "revenue_per_listen": 0.01
            }
        }
    
    async def track_event(self, 
                         user_id: str,
                         content_id: str,
                         platform: str,
                         metric_type: MetricType,
                         value: float,
                         metadata: Dict[str, Any] = None,
                         geo_data: Dict[str, str] = None) -> AnalyticsEvent:
        """Track a single analytics event"""
        
        event = AnalyticsEvent(
            user_id=user_id,
            content_id=content_id,
            platform=platform,
            metric_type=metric_type,
            value=value,
            metadata=metadata or {}
        )
        
        # Add geo and demographic data if provided
        if geo_data:
            event.country = geo_data.get("country")
            event.region = geo_data.get("region")
            event.age_group = geo_data.get("age_group")
            event.gender = geo_data.get("gender")
            event.device_type = geo_data.get("device_type")
            event.browser = geo_data.get("browser")
            event.referrer = geo_data.get("referrer")
        
        # Store event
        event_dict = event.dict()
        event_dict["timestamp"] = event.timestamp.isoformat()
        
        self.events_collection.insert_one(event_dict)
        
        # Update content performance asynchronously
        asyncio.create_task(self._update_content_performance(content_id, user_id))
        
        return event
    
    async def track_batch_events(self, events: List[Dict[str, Any]]) -> List[AnalyticsEvent]:
        """Track multiple analytics events in batch"""
        
        analytics_events = []
        event_dicts = []
        
        for event_data in events:
            event = AnalyticsEvent(
                user_id=event_data["user_id"],
                content_id=event_data["content_id"],
                platform=event_data["platform"],
                metric_type=MetricType(event_data["metric_type"]),
                value=event_data["value"],
                metadata=event_data.get("metadata", {})
            )
            
            # Add optional data
            geo_data = event_data.get("geo_data", {})
            if geo_data:
                event.country = geo_data.get("country")
                event.region = geo_data.get("region")
                event.age_group = geo_data.get("age_group")
                event.gender = geo_data.get("gender")
                event.device_type = geo_data.get("device_type")
                event.browser = geo_data.get("browser")
                event.referrer = geo_data.get("referrer")
            
            analytics_events.append(event)
            
            event_dict = event.dict()
            event_dict["timestamp"] = event.timestamp.isoformat()
            event_dicts.append(event_dict)
        
        # Batch insert
        if event_dicts:
            self.events_collection.insert_many(event_dicts)
        
        # Update content performance for unique content IDs
        unique_content_user_pairs = set((e["content_id"], e["user_id"]) for e in events)
        for content_id, user_id in unique_content_user_pairs:
            asyncio.create_task(self._update_content_performance(content_id, user_id))
        
        return analytics_events
    
    async def _update_content_performance(self, content_id: str, user_id: str):
        """Update content performance metrics based on recent events"""
        
        try:
            # Get all events for this content
            events_cursor = self.events_collection.find({
                "content_id": content_id,
                "user_id": user_id
            })
            
            events = list(events_cursor)
            if not events:
                return
            
            # Calculate metrics
            metrics = defaultdict(float)
            platform_metrics = defaultdict(lambda: defaultdict(float))
            daily_metrics = defaultdict(lambda: defaultdict(float))
            country_breakdown = defaultdict(lambda: defaultdict(float))
            age_breakdown = defaultdict(lambda: defaultdict(float))
            gender_breakdown = defaultdict(lambda: defaultdict(float))
            
            for event in events:
                metric_type = event["metric_type"]
                value = event["value"]
                platform = event["platform"]
                timestamp = datetime.fromisoformat(event["timestamp"])
                date_str = timestamp.date().isoformat()
                
                # Aggregate totals
                metrics[f"total_{metric_type}"] += value
                
                # Platform breakdown
                platform_metrics[platform][metric_type] += value
                
                # Daily breakdown
                daily_metrics[date_str][metric_type] += value
                
                # Geographic breakdown
                if event.get("country"):
                    country_breakdown[event["country"]][metric_type] += value
                
                # Demographic breakdown
                if event.get("age_group"):
                    age_breakdown[event["age_group"]][metric_type] += value
                
                if event.get("gender"):
                    gender_breakdown[event["gender"]][metric_type] += value
            
            # Calculate derived metrics
            total_views = metrics.get("total_views", 0)
            total_streams = metrics.get("total_streams", 0)
            total_engagement = metrics.get("total_likes", 0) + metrics.get("total_shares", 0) + metrics.get("total_comments", 0)
            
            engagement_rate = 0.0
            if total_views > 0:
                engagement_rate = (total_engagement / total_views) * 100
            
            # Create or update performance record
            performance = ContentPerformance(
                content_id=content_id,
                user_id=user_id,
                content_title=f"Content {content_id}",  # Would be fetched from content metadata
                content_type="music",  # Would be determined from content data
                total_views=int(metrics.get("total_views", 0)),
                total_streams=int(metrics.get("total_streams", 0)),
                total_downloads=int(metrics.get("total_downloads", 0)),
                total_shares=int(metrics.get("total_shares", 0)),
                total_likes=int(metrics.get("total_likes", 0)),
                total_comments=int(metrics.get("total_comments", 0)),
                total_revenue=metrics.get("total_revenue", 0.0),
                engagement_rate=round(engagement_rate, 2),
                platform_metrics=dict(platform_metrics),
                daily_metrics=dict(daily_metrics),
                country_breakdown=dict(country_breakdown),
                age_group_breakdown=dict(age_breakdown),
                gender_breakdown=dict(gender_breakdown)
            )
            
            # Calculate industry percentile
            content_type = performance.content_type
            if content_type in self.industry_benchmarks:
                benchmark_engagement = self.industry_benchmarks[content_type]["engagement_rate"]
                if benchmark_engagement > 0:
                    performance.industry_percentile = min(100, (engagement_rate / benchmark_engagement) * 50)
            
            # Store performance data
            performance_dict = performance.dict()
            performance_dict["last_updated"] = performance.last_updated.isoformat()
            performance_dict["analysis_date"] = performance.analysis_date.isoformat()
            
            if performance.first_published:
                performance_dict["first_published"] = performance.first_published.isoformat()
            
            self.performance_collection.update_one(
                {"content_id": content_id, "user_id": user_id},
                {"$set": performance_dict},
                upsert=True
            )
            
        except Exception as e:
            print(f"Error updating content performance: {e}")
    
    async def get_content_performance(self, content_id: str, user_id: str) -> Optional[ContentPerformance]:
        """Get performance metrics for specific content"""
        
        try:
            perf_data = self.performance_collection.find_one({
                "content_id": content_id,
                "user_id": user_id
            })
            
            if perf_data:
                perf_data['_id'] = str(perf_data['_id'])
                return ContentPerformance(**perf_data)
            
            return None
            
        except Exception as e:
            print(f"Error getting content performance: {e}")
            return None
    
    async def get_user_content_performance(self, user_id: str, 
                                         limit: int = 50, 
                                         offset: int = 0) -> List[ContentPerformance]:
        """Get performance metrics for all user content"""
        
        try:
            cursor = self.performance_collection.find({"user_id": user_id}) \
                         .sort("last_updated", -1) \
                         .skip(offset).limit(limit)
            
            performances = []
            for perf_data in cursor:
                try:
                    perf_data['_id'] = str(perf_data['_id'])
                    performances.append(ContentPerformance(**perf_data))
                except Exception as e:
                    print(f"Error parsing performance data: {e}")
                    continue
            
            return performances
            
        except Exception as e:
            print(f"Error getting user content performance: {e}")
            return []
    
    async def calculate_roi_analysis(self, 
                                   content_id: str, 
                                   user_id: str,
                                   investment_data: Dict[str, float]) -> ROIAnalysis:
        """Calculate ROI analysis for content"""
        
        # Get performance data
        performance = await self.get_content_performance(content_id, user_id)
        
        roi_analysis = ROIAnalysis(
            content_id=content_id,
            user_id=user_id,
            production_cost=investment_data.get("production_cost", 0.0),
            marketing_cost=investment_data.get("marketing_cost", 0.0),
            distribution_cost=investment_data.get("distribution_cost", 0.0),
            platform_fees=investment_data.get("platform_fees", 0.0)
        )
        
        # Calculate total investment
        roi_analysis.total_investment = (
            roi_analysis.production_cost +
            roi_analysis.marketing_cost +
            roi_analysis.distribution_cost +
            roi_analysis.platform_fees
        )
        
        # Get revenue data from performance
        if performance:
            roi_analysis.streaming_revenue = performance.total_revenue
            roi_analysis.total_revenue = performance.total_revenue
            
            # Calculate revenue metrics
            if performance.total_views > 0:
                roi_analysis.revenue_per_view = performance.total_revenue / performance.total_views
            
            if performance.total_streams > 0:
                roi_analysis.revenue_per_stream = performance.total_revenue / performance.total_streams
        
        # Calculate ROI metrics
        roi_analysis.net_profit = roi_analysis.total_revenue - roi_analysis.total_investment
        
        if roi_analysis.total_investment > 0:
            roi_analysis.roi_percentage = (roi_analysis.net_profit / roi_analysis.total_investment) * 100
        
        # Estimate payback period
        if roi_analysis.total_revenue > 0 and roi_analysis.total_investment > 0:
            daily_revenue = roi_analysis.total_revenue / 30  # Assume 30-day period
            if daily_revenue > 0:
                roi_analysis.payback_period_days = int(roi_analysis.total_investment / daily_revenue)
        
        # Revenue projections based on current performance
        current_daily_revenue = roi_analysis.total_revenue / 30 if roi_analysis.total_revenue > 0 else 0
        roi_analysis.projected_30_day_revenue = current_daily_revenue * 30
        roi_analysis.projected_90_day_revenue = current_daily_revenue * 90 * 0.8  # Assume 20% decay
        roi_analysis.projected_annual_revenue = current_daily_revenue * 365 * 0.6  # Assume 40% decay
        
        # Store ROI analysis
        roi_dict = roi_analysis.dict()
        roi_dict["created_at"] = roi_analysis.created_at.isoformat()
        roi_dict["updated_at"] = roi_analysis.updated_at.isoformat()
        
        if roi_analysis.break_even_point:
            roi_dict["break_even_point"] = roi_analysis.break_even_point.isoformat()
        
        self.roi_collection.update_one(
            {"content_id": content_id, "user_id": user_id},
            {"$set": roi_dict},
            upsert=True
        )
        
        return roi_analysis
    
    async def get_platform_analytics(self, user_id: str, platform: str) -> PlatformAnalytics:
        """Get comprehensive analytics for a specific platform"""
        
        try:
            # Get all user content performance data for this platform
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$match": {f"platform_metrics.{platform}": {"$exists": True}}}
            ]
            
            cursor = self.performance_collection.aggregate(pipeline)
            content_performances = list(cursor)
            
            platform_analytics = PlatformAnalytics(
                platform_id=platform,
                platform_name=platform.replace("_", " ").title(),
                user_id=user_id
            )
            
            if not content_performances:
                return platform_analytics
            
            # Aggregate metrics
            total_views = 0
            total_revenue = 0.0
            engagement_rates = []
            
            for perf in content_performances:
                platform_metrics = perf.get("platform_metrics", {}).get(platform, {})
                
                platform_analytics.total_content_pieces += 1
                
                views = platform_metrics.get("views", 0)
                revenue = platform_metrics.get("revenue", 0.0)
                
                total_views += views
                total_revenue += revenue
                
                # Calculate engagement rate for this content on this platform
                likes = platform_metrics.get("likes", 0)
                shares = platform_metrics.get("shares", 0)
                comments = platform_metrics.get("comments", 0)
                
                if views > 0:
                    engagement_rate = ((likes + shares + comments) / views) * 100
                    engagement_rates.append(engagement_rate)
            
            platform_analytics.total_views = total_views
            platform_analytics.total_revenue = total_revenue
            
            if engagement_rates:
                platform_analytics.average_engagement_rate = statistics.mean(engagement_rates)
            
            if platform_analytics.total_content_pieces > 0:
                platform_analytics.revenue_per_content = total_revenue / platform_analytics.total_content_pieces
            
            # Generate optimization suggestions
            platform_analytics.optimization_suggestions = self._generate_platform_suggestions(
                platform, platform_analytics
            )
            
            # Store platform analytics
            analytics_dict = platform_analytics.dict()
            analytics_dict["last_updated"] = platform_analytics.last_updated.isoformat()
            
            self.platform_analytics_collection.update_one(
                {"platform_id": platform, "user_id": user_id},
                {"$set": analytics_dict},
                upsert=True
            )
            
            return platform_analytics
            
        except Exception as e:
            print(f"Error getting platform analytics: {e}")
            return PlatformAnalytics(
                platform_id=platform,
                platform_name=platform.replace("_", " ").title(),
                user_id=user_id
            )
    
    def _generate_platform_suggestions(self, platform: str, analytics: PlatformAnalytics) -> List[str]:
        """Generate optimization suggestions for a platform"""
        
        suggestions = []
        
        # Engagement rate suggestions
        if analytics.average_engagement_rate < 2.0:
            suggestions.append("Consider improving content quality to boost engagement")
            suggestions.append("Try posting at different times to reach more active audiences")
        elif analytics.average_engagement_rate > 8.0:
            suggestions.append("Excellent engagement! Consider increasing posting frequency")
        
        # Revenue suggestions
        if analytics.revenue_per_content < 10.0:
            suggestions.append("Explore monetization options like sponsorships or premium content")
            suggestions.append("Consider cross-promoting your best-performing content")
        
        # Content volume suggestions
        if analytics.total_content_pieces < 5:
            suggestions.append("Increase content volume to build audience and improve performance")
        elif analytics.total_content_pieces > 50:
            suggestions.append("Focus on quality over quantity - analyze your top performers")
        
        # Platform-specific suggestions
        platform_specific = {
            "youtube": [
                "Optimize video thumbnails and titles for better click-through rates",
                "Use YouTube Shorts for viral content potential"
            ],
            "spotify": [
                "Create playlists to increase discoverability",
                "Collaborate with other artists for cross-promotion"
            ],
            "instagram": [
                "Use Stories and Reels for higher engagement",
                "Post consistently during peak hours (6-9 PM)"
            ],
            "tiktok": [
                "Focus on trending sounds and hashtags",
                "Keep videos under 30 seconds for better completion rates"
            ]
        }
        
        if platform in platform_specific:
            suggestions.extend(platform_specific[platform])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    async def get_dashboard_metrics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics for a user"""
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get recent events
            events_cursor = self.events_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_date.isoformat()}
            })
            
            events = list(events_cursor)
            
            # Get content performance data
            performances = await self.get_user_content_performance(user_id, limit=100)
            
            # Calculate dashboard metrics
            dashboard = {
                "period_days": days,
                "total_events": len(events),
                "total_content_pieces": len(performances),
                "total_views": sum(p.total_views for p in performances),
                "total_streams": sum(p.total_streams for p in performances),
                "total_revenue": sum(p.total_revenue for p in performances),
                "average_engagement_rate": 0.0,
                "top_performing_content": [],
                "platform_breakdown": {},
                "recent_trends": {},
                "optimization_opportunities": []
            }
            
            # Calculate average engagement rate
            if performances:
                engagement_rates = [p.engagement_rate for p in performances if p.engagement_rate > 0]
                if engagement_rates:
                    dashboard["average_engagement_rate"] = statistics.mean(engagement_rates)
            
            # Get top performing content
            sorted_performances = sorted(performances, key=lambda x: x.total_views, reverse=True)
            dashboard["top_performing_content"] = [
                {
                    "content_id": p.content_id,
                    "content_title": p.content_title,
                    "total_views": p.total_views,
                    "engagement_rate": p.engagement_rate,
                    "total_revenue": p.total_revenue
                }
                for p in sorted_performances[:5]
            ]
            
            # Platform breakdown
            platform_totals = defaultdict(lambda: {"views": 0, "revenue": 0.0})
            for perf in performances:
                for platform, metrics in perf.platform_metrics.items():
                    platform_totals[platform]["views"] += metrics.get("views", 0)
                    platform_totals[platform]["revenue"] += metrics.get("revenue", 0.0)
            
            dashboard["platform_breakdown"] = dict(platform_totals)
            
            # Generate optimization opportunities
            dashboard["optimization_opportunities"] = self._generate_optimization_opportunities(
                dashboard, performances
            )
            
            return dashboard
            
        except Exception as e:
            print(f"Error getting dashboard metrics: {e}")
            return {
                "error": str(e),
                "period_days": days,
                "total_events": 0,
                "total_content_pieces": 0
            }
    
    def _generate_optimization_opportunities(self, dashboard: Dict[str, Any], 
                                           performances: List[ContentPerformance]) -> List[str]:
        """Generate optimization opportunities based on analytics"""
        
        opportunities = []
        
        # Revenue optimization
        if dashboard["total_revenue"] < 100:
            opportunities.append("Explore monetization strategies to increase revenue")
        
        # Engagement optimization
        if dashboard["average_engagement_rate"] < 3.0:
            opportunities.append("Focus on creating more engaging content to improve audience interaction")
        
        # Content volume optimization
        if dashboard["total_content_pieces"] < 10:
            opportunities.append("Increase content production to build audience and improve performance")
        
        # Platform optimization
        platform_counts = len(dashboard["platform_breakdown"])
        if platform_counts < 3:
            opportunities.append("Expand to more platforms to diversify your audience reach")
        elif platform_counts > 8:
            opportunities.append("Focus on your top-performing platforms for better ROI")
        
        # Performance consistency
        if performances:
            view_counts = [p.total_views for p in performances]
            if len(set(view_counts)) > len(view_counts) * 0.8:  # High variance
                opportunities.append("Analyze successful content patterns to improve consistency")
        
        return opportunities[:5]
    
    async def get_content_trends(self, user_id: str, content_id: str, days: int = 30) -> Dict[str, Any]:
        """Get trend analysis for specific content"""
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get events for this content in the time period
            events_cursor = self.events_collection.find({
                "user_id": user_id,
                "content_id": content_id,
                "timestamp": {"$gte": cutoff_date.isoformat()}
            }).sort("timestamp", 1)
            
            events = list(events_cursor)
            
            # Group events by day
            daily_trends = defaultdict(lambda: defaultdict(float))
            
            for event in events:
                timestamp = datetime.fromisoformat(event["timestamp"])
                date_str = timestamp.date().isoformat()
                metric_type = event["metric_type"]
                value = event["value"]
                
                daily_trends[date_str][metric_type] += value
            
            # Calculate trend direction
            trend_analysis = {
                "content_id": content_id,
                "period_days": days,
                "daily_trends": dict(daily_trends),
                "trend_direction": "stable",
                "growth_rate": 0.0,
                "peak_performance_date": None,
                "total_events": len(events)
            }
            
            # Calculate growth rate if we have enough data
            if len(daily_trends) >= 7:
                dates = sorted(daily_trends.keys())
                early_week = dates[:7]
                late_week = dates[-7:]
                
                early_views = sum(daily_trends[date].get("views", 0) for date in early_week)
                late_views = sum(daily_trends[date].get("views", 0) for date in late_week)
                
                if early_views > 0:
                    growth_rate = ((late_views - early_views) / early_views) * 100
                    trend_analysis["growth_rate"] = round(growth_rate, 2)
                    
                    if growth_rate > 10:
                        trend_analysis["trend_direction"] = "growing"
                    elif growth_rate < -10:
                        trend_analysis["trend_direction"] = "declining"
            
            # Find peak performance date
            if daily_trends:
                peak_date = max(daily_trends.keys(), 
                              key=lambda date: daily_trends[date].get("views", 0))
                trend_analysis["peak_performance_date"] = peak_date
            
            return trend_analysis
            
        except Exception as e:
            print(f"Error getting content trends: {e}")
            return {
                "content_id": content_id,
                "error": str(e),
                "period_days": days,
                "total_events": 0
            }