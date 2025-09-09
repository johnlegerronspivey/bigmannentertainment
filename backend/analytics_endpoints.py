"""
Analytics API Endpoints - Function 4: Content Analytics & Performance Monitoring
Provides API endpoints for content analytics, performance tracking, and ROI analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import json

from analytics_service import (
    AnalyticsService,
    AnalyticsEvent,
    ContentPerformance,
    ROIAnalysis,
    PlatformAnalytics,
    MetricType,
    Timeframe
)

# Initialize service
analytics_service = AnalyticsService()

# Create router
router = APIRouter(prefix="/api/analytics", tags=["Content Analytics & Performance Monitoring"])
security = HTTPBearer()

# Request models
class EventTrackingRequest(BaseModel):
    content_id: str
    platform: str
    metric_type: MetricType
    value: float
    metadata: Optional[Dict[str, Any]] = None
    geo_data: Optional[Dict[str, str]] = None

class BatchEventRequest(BaseModel):
    events: List[Dict[str, Any]]

class ROICalculationRequest(BaseModel):
    content_id: str
    production_cost: float = 0.0
    marketing_cost: float = 0.0
    distribution_cost: float = 0.0
    platform_fees: float = 0.0

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This would integrate with your authentication system
    # For now, returning a mock user ID
    return "user_123"

# Event Tracking Endpoints

@router.post("/events/track")
async def track_analytics_event(
    request: EventTrackingRequest,
    user_id: str = Depends(get_current_user)
):
    """Track a single analytics event"""
    try:
        event = await analytics_service.track_event(
            user_id=user_id,
            content_id=request.content_id,
            platform=request.platform,
            metric_type=request.metric_type,
            value=request.value,
            metadata=request.metadata,
            geo_data=request.geo_data
        )
        
        return {
            "success": True,
            "event": event,
            "message": "Analytics event tracked successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/batch")
async def track_batch_events(
    request: BatchEventRequest,
    user_id: str = Depends(get_current_user)
):
    """Track multiple analytics events in batch"""
    try:
        # Add user_id to each event
        events_with_user_id = []
        for event in request.events:
            event_with_user = event.copy()
            event_with_user["user_id"] = user_id
            events_with_user_id.append(event_with_user)
        
        events = await analytics_service.track_batch_events(events_with_user_id)
        
        return {
            "success": True,
            "events_tracked": len(events),
            "events": events,
            "message": f"Successfully tracked {len(events)} analytics events"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Performance Endpoints

@router.get("/content/{content_id}/performance")
async def get_content_performance(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get performance metrics for specific content"""
    try:
        performance = await analytics_service.get_content_performance(content_id, user_id)
        
        if not performance:
            raise HTTPException(status_code=404, detail="Content performance data not found")
        
        return {
            "success": True,
            "content_performance": performance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/performance/all")
async def get_all_content_performance(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user)
):
    """Get performance metrics for all user content"""
    try:
        performances = await analytics_service.get_user_content_performance(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "content_performances": performances,
            "total_items": len(performances),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{content_id}/trends")
async def get_content_trends(
    content_id: str,
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get trend analysis for specific content"""
    try:
        trends = await analytics_service.get_content_trends(user_id, content_id, days)
        
        return {
            "success": True,
            "content_trends": trends,
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ROI Analysis Endpoints

@router.post("/roi/calculate")
async def calculate_roi_analysis(
    request: ROICalculationRequest,
    user_id: str = Depends(get_current_user)
):
    """Calculate ROI analysis for content"""
    try:
        investment_data = {
            "production_cost": request.production_cost,
            "marketing_cost": request.marketing_cost,
            "distribution_cost": request.distribution_cost,
            "platform_fees": request.platform_fees
        }
        
        roi_analysis = await analytics_service.calculate_roi_analysis(
            request.content_id, user_id, investment_data
        )
        
        return {
            "success": True,
            "roi_analysis": roi_analysis,
            "message": "ROI analysis calculated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roi/{content_id}")
async def get_roi_analysis(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get ROI analysis for specific content"""
    try:
        roi_data = analytics_service.roi_collection.find_one({
            "content_id": content_id,
            "user_id": user_id
        })
        
        if not roi_data:
            raise HTTPException(status_code=404, detail="ROI analysis not found")
        
        roi_data['_id'] = str(roi_data['_id'])
        roi_analysis = ROIAnalysis(**roi_data)
        
        return {
            "success": True,
            "roi_analysis": roi_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Platform Analytics Endpoints

@router.get("/platforms/{platform}/analytics")
async def get_platform_analytics(
    platform: str,
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive analytics for a specific platform"""
    try:
        platform_analytics = await analytics_service.get_platform_analytics(user_id, platform)
        
        return {
            "success": True,
            "platform_analytics": platform_analytics,
            "platform": platform
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/analytics/all")
async def get_all_platform_analytics(
    user_id: str = Depends(get_current_user)
):
    """Get analytics for all platforms"""
    try:
        # Common platforms to analyze
        platforms = [
            "spotify", "apple_music", "youtube", "youtube_music", "soundcloud",
            "tiktok", "instagram", "facebook", "twitter", "amazon_music"
        ]
        
        all_analytics = {}
        for platform in platforms:
            try:
                analytics = await analytics_service.get_platform_analytics(user_id, platform)
                if analytics.total_content_pieces > 0:  # Only include platforms with content
                    all_analytics[platform] = analytics
            except Exception as e:
                print(f"Error getting analytics for {platform}: {e}")
                continue
        
        return {
            "success": True,
            "platform_analytics": all_analytics,
            "total_platforms": len(all_analytics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard and Summary Endpoints

@router.get("/dashboard")
async def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive analytics dashboard"""
    try:
        dashboard_metrics = await analytics_service.get_dashboard_metrics(user_id, days)
        
        return {
            "success": True,
            "dashboard": dashboard_metrics,
            "period_days": days,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get quick analytics summary"""
    try:
        dashboard = await analytics_service.get_dashboard_metrics(user_id, days)
        
        # Create condensed summary
        summary = {
            "period_days": days,
            "total_views": dashboard.get("total_views", 0),
            "total_streams": dashboard.get("total_streams", 0),
            "total_revenue": dashboard.get("total_revenue", 0.0),
            "engagement_rate": dashboard.get("average_engagement_rate", 0.0),
            "content_pieces": dashboard.get("total_content_pieces", 0),
            "top_platform": None,
            "growth_trend": "stable"
        }
        
        # Find top platform by views
        platform_breakdown = dashboard.get("platform_breakdown", {})
        if platform_breakdown:
            top_platform = max(platform_breakdown.items(), 
                             key=lambda x: x[1].get("views", 0))
            summary["top_platform"] = top_platform[0]
        
        return {
            "success": True,
            "summary": summary,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insights and Recommendations Endpoints

@router.get("/insights/performance")
async def get_performance_insights(
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get performance insights and recommendations"""
    try:
        dashboard = await analytics_service.get_dashboard_metrics(user_id, days)
        performances = await analytics_service.get_user_content_performance(user_id, limit=100)
        
        insights = {
            "period_days": days,
            "key_insights": [],
            "recommendations": dashboard.get("optimization_opportunities", []),
            "performance_highlights": [],
            "areas_for_improvement": []
        }
        
        # Generate key insights
        if dashboard.get("total_views", 0) > 10000:
            insights["key_insights"].append("Strong viewership performance with 10K+ total views")
        
        if dashboard.get("average_engagement_rate", 0) > 5.0:
            insights["key_insights"].append("Excellent audience engagement above industry average")
        
        if dashboard.get("total_revenue", 0) > 100:
            insights["key_insights"].append("Successful monetization with $100+ revenue")
        
        # Performance highlights
        top_content = dashboard.get("top_performing_content", [])
        if top_content:
            best_performer = top_content[0]
            insights["performance_highlights"].append(
                f"Top content '{best_performer['content_title']}' achieved {best_performer['total_views']} views"
            )
        
        # Areas for improvement
        if dashboard.get("average_engagement_rate", 0) < 2.0:
            insights["areas_for_improvement"].append("Low engagement rate - focus on audience interaction")
        
        if len(dashboard.get("platform_breakdown", {})) < 3:
            insights["areas_for_improvement"].append("Limited platform presence - consider expanding reach")
        
        return {
            "success": True,
            "insights": insights,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/content-optimization")
async def get_content_optimization_insights(
    user_id: str = Depends(get_current_user)
):
    """Get content optimization insights"""
    try:
        performances = await analytics_service.get_user_content_performance(user_id, limit=50)
        
        if not performances:
            return {
                "success": True,
                "insights": {
                    "message": "No content data available for analysis",
                    "recommendations": ["Start creating and tracking content performance"]
                }
            }
        
        # Analyze content performance patterns
        high_performers = [p for p in performances if p.total_views > 1000]
        low_performers = [p for p in performances if p.total_views < 100]
        
        insights = {
            "total_content_analyzed": len(performances),
            "high_performers": len(high_performers),
            "low_performers": len(low_performers),
            "success_patterns": [],
            "optimization_recommendations": [],
            "content_strategy_tips": []
        }
        
        # Success patterns analysis
        if high_performers:
            avg_engagement_high = sum(p.engagement_rate for p in high_performers) / len(high_performers)
            insights["success_patterns"].append(
                f"High-performing content averages {avg_engagement_high:.1f}% engagement rate"
            )
            
            # Find common platforms for high performers
            platform_counts = {}
            for perf in high_performers:
                for platform in perf.platform_metrics.keys():
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            if platform_counts:
                top_platform = max(platform_counts.items(), key=lambda x: x[1])
                insights["success_patterns"].append(
                    f"Most successful content performs well on {top_platform[0]}"
                )
        
        # Optimization recommendations
        if low_performers:
            insights["optimization_recommendations"].append(
                f"{len(low_performers)} content pieces need optimization"
            )
            insights["optimization_recommendations"].append(
                "Focus on improving titles, thumbnails, and content quality"
            )
        
        # Content strategy tips
        insights["content_strategy_tips"] = [
            "Analyze your top-performing content for successful patterns",
            "Optimize posting times based on audience engagement data",
            "Cross-promote successful content across multiple platforms",
            "Engage with your audience through comments and social interactions"
        ]
        
        return {
            "success": True,
            "insights": insights,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Comparison and Benchmarking Endpoints

@router.get("/benchmarks/industry")
async def get_industry_benchmarks(
    content_type: str = Query("music", description="Content type for benchmarking"),
    user_id: str = Depends(get_current_user)
):
    """Get industry benchmarks for comparison"""
    try:
        benchmarks = analytics_service.industry_benchmarks.get(content_type, {})
        
        if not benchmarks:
            return {
                "success": False,
                "message": f"No benchmarks available for content type: {content_type}",
                "available_types": list(analytics_service.industry_benchmarks.keys())
            }
        
        # Get user performance for comparison
        performances = await analytics_service.get_user_content_performance(user_id, limit=50)
        
        user_metrics = {
            "engagement_rate": 0.0,
            "completion_rate": 0.0,
            "viral_coefficient": 0.0,
            "revenue_per_view": 0.0
        }
        
        if performances:
            engagement_rates = [p.engagement_rate for p in performances if p.engagement_rate > 0]
            if engagement_rates:
                user_metrics["engagement_rate"] = sum(engagement_rates) / len(engagement_rates)
            
            # Calculate revenue per view
            total_views = sum(p.total_views for p in performances)
            total_revenue = sum(p.total_revenue for p in performances)
            if total_views > 0:
                user_metrics["revenue_per_view"] = total_revenue / total_views
        
        comparison = {
            "content_type": content_type,
            "industry_benchmarks": benchmarks,
            "user_performance": user_metrics,
            "performance_vs_industry": {}
        }
        
        # Calculate performance comparison
        for metric, benchmark_value in benchmarks.items():
            user_value = user_metrics.get(metric, 0)
            if benchmark_value > 0:
                performance_ratio = (user_value / benchmark_value) * 100
                comparison["performance_vs_industry"][metric] = {
                    "user_value": user_value,
                    "industry_average": benchmark_value,
                    "performance_percentage": round(performance_ratio, 1),
                    "status": "above_average" if performance_ratio > 100 else "below_average"
                }
        
        return {
            "success": True,
            "benchmark_comparison": comparison,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export and Reporting Endpoints

@router.get("/reports/performance")
async def generate_performance_report(
    format: str = Query("json", description="Report format (json, summary)"),
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Generate comprehensive performance report"""
    try:
        # Get comprehensive data
        dashboard = await analytics_service.get_dashboard_metrics(user_id, days)
        performances = await analytics_service.get_user_content_performance(user_id, limit=100)
        
        report = {
            "report_type": "performance_report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period_days": days,
            "user_id": user_id,
            "executive_summary": {
                "total_content": len(performances),
                "total_views": dashboard.get("total_views", 0),
                "total_revenue": dashboard.get("total_revenue", 0.0),
                "average_engagement": dashboard.get("average_engagement_rate", 0.0)
            },
            "detailed_metrics": dashboard,
            "content_performance": [p.dict() for p in performances[:20]],  # Top 20
            "recommendations": dashboard.get("optimization_opportunities", [])
        }
        
        if format == "summary":
            # Return condensed summary version
            return {
                "success": True,
                "report": {
                    "executive_summary": report["executive_summary"],
                    "key_insights": report["recommendations"][:3],
                    "top_content": dashboard.get("top_performing_content", [])[:3]
                }
            }
        
        return {
            "success": True,
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Health and Monitoring

@router.get("/health")
async def health_check():
    """Health check endpoint for analytics service"""
    try:
        # Test database connection
        test_query = analytics_service.events_collection.count_documents({})
        
        health_status = {
            "service": "Content Analytics & Performance Monitoring API",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "4.0.0",
            "database_connection": "healthy",
            "total_events_tracked": test_query,
            "supported_metric_types": [metric.value for metric in MetricType],
            "supported_timeframes": [timeframe.value for timeframe in Timeframe],
            "industry_benchmarks_available": len(analytics_service.industry_benchmarks)
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