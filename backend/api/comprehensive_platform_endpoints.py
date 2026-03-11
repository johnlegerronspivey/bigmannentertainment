"""
Big Mann Entertainment - Comprehensive Platform API Endpoints
All endpoints for the 9-module comprehensive platform
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

# Import all services
from comprehensive_platform_core import comprehensive_platform_core
from content_manager_service import content_manager_service
from distribution_tracker_service import distribution_tracker_service
from analytics_forecasting_service import analytics_forecasting_service
from compliance_center_service import compliance_center_service
from sponsorship_campaigns_service import sponsorship_campaigns_service
from contributor_hub_service import contributor_hub_service
from system_health_service import system_health_service
from dao_governance_service import dao_governance_service

# Import Pydantic models
from comprehensive_platform_core import KPIData, RecentActivity, SystemAlert, NotificationData
from content_manager_service import ContentAsset, ContentFolder, ContentMetadata, ContentType, ContentStatus, QualityLevel, ContentFormat
from distribution_tracker_service import DistributionJob, PlatformDelivery, DeliveryPriority, DistributionStatus, PlatformCategory
from analytics_forecasting_service import MetricType, TimeFrame, ForecastModel
from compliance_center_service import ComplianceType, ComplianceStatus, RiskLevel, Territory
from sponsorship_campaigns_service import Campaign, CampaignType, CampaignStatus, BudgetType, TargetingCriteria
from contributor_hub_service import ContributorProfile, CollaborationRequest, ContributorRole, CollaborationStatus
from system_health_service import LogQuery, LogLevel, SystemComponent, HealthStatus, AlertSeverity
from dao_governance_service import GovernanceProposal, ProposalType, ProposalStatus, VoteChoice, GovernanceRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/platform", tags=["Comprehensive Platform"])

# ===== CORE PLATFORM ENDPOINTS =====

@router.get("/dashboard/kpi")
async def get_dashboard_kpi(user_id: str = Query(...)):
    """Get KPI data for main dashboard"""
    try:
        result = await comprehensive_platform_core.get_kpi_data(user_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in get_dashboard_kpi: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/activities")
async def get_recent_activities(
    user_id: str = Query(...),
    limit: int = Query(10, ge=1, le=50)
):
    """Get recent platform activities"""
    try:
        result = await comprehensive_platform_core.get_recent_activities(user_id, limit)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in get_recent_activities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/alerts")
async def get_system_alerts(
    user_id: str = Query(...),
    severity: Optional[str] = Query(None)
):
    """Get system alerts for dashboard"""
    try:
        result = await comprehensive_platform_core.get_system_alerts(user_id, severity)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in get_system_alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications")
async def get_notifications(
    user_id: str = Query(...),
    limit: int = Query(10, ge=1, le=50)
):
    """Get user notifications"""
    try:
        result = await comprehensive_platform_core.get_notifications(user_id, limit)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in get_notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Query(...)
):
    """Mark notification as read"""
    try:
        result = await comprehensive_platform_core.mark_notification_read(notification_id, user_id)
        return {"success": result, "message": "Notification marked as read" if result else "Failed to mark notification as read"}
    except Exception as e:
        logger.error(f"Error in mark_notification_read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_platform(
    query: str = Query(..., min_length=1),
    user_id: str = Query(...)
):
    """Search across the platform"""
    try:
        result = await comprehensive_platform_core.search_platform(query, user_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in search_platform: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CONTENT MANAGER ENDPOINTS =====

@router.get("/content/assets")
async def get_content_assets(
    user_id: str = Query(...),
    folder_id: Optional[str] = Query(None),
    content_type: Optional[ContentType] = Query(None),
    status: Optional[ContentStatus] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get content assets"""
    try:
        result = await content_manager_service.get_assets(user_id, folder_id, content_type, status, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_content_assets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/assets/{asset_id}")
async def get_content_asset(
    asset_id: str,
    user_id: str = Query(...)
):
    """Get specific content asset"""
    try:
        result = await content_manager_service.get_asset(asset_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_content_asset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/content/assets/{asset_id}")
async def update_content_asset(
    asset_id: str,
    updates: Dict[str, Any],
    user_id: str = Query(...)
):
    """Update content asset"""
    try:
        result = await content_manager_service.update_asset(asset_id, updates, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in update_content_asset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/content/assets/{asset_id}")
async def delete_content_asset(
    asset_id: str,
    user_id: str = Query(...)
):
    """Delete content asset"""
    try:
        result = await content_manager_service.delete_asset(asset_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_content_asset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/folders")
async def get_content_folders(
    user_id: str = Query(...),
    parent_id: Optional[str] = Query(None)
):
    """Get content folders"""
    try:
        result = await content_manager_service.get_folders(user_id, parent_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_content_folders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/stats")
async def get_content_stats(user_id: str = Query(...)):
    """Get content statistics"""
    try:
        result = await content_manager_service.get_content_stats(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_content_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/search")
async def search_content(
    query: str = Query(..., min_length=1),
    user_id: str = Query(...),
    filters: Optional[Dict[str, Any]] = None
):
    """Search content assets"""
    try:
        result = await content_manager_service.search_content(query, user_id, filters)
        return result
    except Exception as e:
        logger.error(f"Error in search_content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== DISTRIBUTION TRACKER ENDPOINTS =====

@router.post("/distribution/jobs")
async def create_distribution_job(
    asset_id: str,
    asset_title: str,
    platforms: List[str],
    user_id: str = Query(...),
    priority: DeliveryPriority = DeliveryPriority.NORMAL
):
    """Create distribution job"""
    try:
        result = await distribution_tracker_service.create_distribution_job(
            asset_id, asset_title, platforms, user_id, priority
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_distribution_job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribution/jobs")
async def get_distribution_jobs(
    user_id: str = Query(...),
    status: Optional[DistributionStatus] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get distribution jobs"""
    try:
        result = await distribution_tracker_service.get_distribution_jobs(user_id, status, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_distribution_jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribution/jobs/{job_id}")
async def get_distribution_job(
    job_id: str,
    user_id: str = Query(...)
):
    """Get specific distribution job"""
    try:
        result = await distribution_tracker_service.get_distribution_job(job_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_distribution_job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribution/platforms")
async def get_distribution_platforms(category: Optional[PlatformCategory] = Query(None)):
    """Get available distribution platforms"""
    try:
        result = await distribution_tracker_service.get_platforms(category)
        return result
    except Exception as e:
        logger.error(f"Error in get_distribution_platforms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribution/analytics")
async def get_distribution_analytics(
    user_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get distribution analytics"""
    try:
        result = await distribution_tracker_service.get_distribution_analytics(user_id, start_date, end_date)
        return result
    except Exception as e:
        logger.error(f"Error in get_distribution_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distribution/deliveries/{delivery_id}/retry")
async def retry_failed_delivery(
    delivery_id: str,
    user_id: str = Query(...)
):
    """Retry failed delivery"""
    try:
        result = await distribution_tracker_service.retry_failed_delivery(delivery_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in retry_failed_delivery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ANALYTICS & FORECASTING ENDPOINTS =====

@router.get("/analytics/revenue")
async def get_revenue_analytics(
    user_id: str = Query(...),
    time_frame: TimeFrame = Query(TimeFrame.MONTH)
):
    """Get revenue analytics"""
    try:
        result = await analytics_forecasting_service.get_revenue_analytics(user_id, time_frame)
        return result
    except Exception as e:
        logger.error(f"Error in get_revenue_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/performance")
async def get_performance_metrics(
    user_id: str = Query(...),
    time_frame: TimeFrame = Query(TimeFrame.MONTH)
):
    """Get performance metrics"""
    try:
        result = await analytics_forecasting_service.get_performance_metrics(user_id, time_frame)
        return result
    except Exception as e:
        logger.error(f"Error in get_performance_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/forecast")
async def generate_forecast(
    metric_type: MetricType,
    time_frame: TimeFrame,
    forecast_periods: int = Query(12, ge=1, le=24),
    model: ForecastModel = ForecastModel.LINEAR,
    user_id: str = Query(...)
):
    """Generate forecast"""
    try:
        result = await analytics_forecasting_service.generate_forecast(
            metric_type, time_frame, forecast_periods, model, user_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in generate_forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/roi")
async def get_roi_analysis(
    user_id: str = Query(...),
    time_period: TimeFrame = Query(TimeFrame.MONTH)
):
    """Get ROI analysis"""
    try:
        result = await analytics_forecasting_service.get_roi_analysis(user_id, time_period)
        return result
    except Exception as e:
        logger.error(f"Error in get_roi_analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/trends")
async def get_trend_analysis(
    user_id: str = Query(...),
    metrics: List[MetricType] = Query([MetricType.REVENUE, MetricType.STREAMS])
):
    """Get trend analysis"""
    try:
        result = await analytics_forecasting_service.get_trend_analysis(user_id, metrics)
        return result
    except Exception as e:
        logger.error(f"Error in get_trend_analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== COMPLIANCE CENTER ENDPOINTS =====

@router.post("/compliance/check")
async def run_compliance_check(
    asset_id: str,
    asset_title: str,
    user_id: str = Query(...),
    rule_ids: Optional[List[str]] = None
):
    """Run compliance check"""
    try:
        result = await compliance_center_service.run_compliance_check(asset_id, asset_title, user_id, rule_ids)
        return result
    except Exception as e:
        logger.error(f"Error in run_compliance_check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/status")
async def get_compliance_status(
    asset_id: Optional[str] = Query(None),
    user_id: str = Query(...)
):
    """Get compliance status"""
    try:
        result = await compliance_center_service.get_compliance_status(asset_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_compliance_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/alerts")
async def get_compliance_alerts(
    user_id: str = Query(...),
    risk_level: Optional[RiskLevel] = Query(None)
):
    """Get compliance alerts"""
    try:
        result = await compliance_center_service.get_compliance_alerts(user_id, risk_level)
        return result
    except Exception as e:
        logger.error(f"Error in get_compliance_alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/rights/{asset_id}")
async def get_rights_information(
    asset_id: str,
    user_id: str = Query(...)
):
    """Get rights information for asset"""
    try:
        result = await compliance_center_service.get_rights_information(asset_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_rights_information: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance/report")
async def generate_compliance_report(
    start_date: datetime,
    end_date: datetime,
    user_id: str = Query(...),
    compliance_types: Optional[List[ComplianceType]] = None,
    territories: Optional[List[Territory]] = None
):
    """Generate compliance report"""
    try:
        result = await compliance_center_service.generate_compliance_report(
            user_id, start_date, end_date, compliance_types, territories
        )
        return result
    except Exception as e:
        logger.error(f"Error in generate_compliance_report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance/issues/{check_id}/resolve")
async def resolve_compliance_issue(
    check_id: str,
    resolution_notes: str,
    user_id: str = Query(...)
):
    """Resolve compliance issue"""
    try:
        result = await compliance_center_service.resolve_compliance_issue(check_id, resolution_notes, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in resolve_compliance_issue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== SPONSORSHIP & CAMPAIGNS ENDPOINTS =====

@router.get("/sponsorship/campaigns")
async def get_campaigns(
    user_id: str = Query(...),
    status: Optional[CampaignStatus] = Query(None),
    campaign_type: Optional[CampaignType] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get campaigns"""
    try:
        result = await sponsorship_campaigns_service.get_campaigns(user_id, status, campaign_type, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsorship/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    user_id: str = Query(...)
):
    """Get specific campaign"""
    try:
        result = await sponsorship_campaigns_service.get_campaign(campaign_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsorship/opportunities")
async def get_sponsorship_opportunities(
    user_id: str = Query(...),
    industry: Optional[str] = Query(None),
    campaign_type: Optional[CampaignType] = Query(None),
    budget_min: Optional[float] = Query(None)
):
    """Get sponsorship opportunities"""
    try:
        result = await sponsorship_campaigns_service.get_sponsorship_opportunities(
            user_id, industry, campaign_type, budget_min
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_sponsorship_opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sponsorship/opportunities/{opportunity_id}/apply")
async def apply_for_opportunity(
    opportunity_id: str,
    application_data: Dict[str, Any],
    user_id: str = Query(...)
):
    """Apply for sponsorship opportunity"""
    try:
        result = await sponsorship_campaigns_service.apply_for_opportunity(opportunity_id, application_data, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in apply_for_opportunity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsorship/analytics")
async def get_campaign_analytics(
    user_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get campaign analytics"""
    try:
        result = await sponsorship_campaigns_service.get_campaign_analytics(user_id, start_date, end_date)
        return result
    except Exception as e:
        logger.error(f"Error in get_campaign_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sponsorship/campaigns/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: str,
    status: CampaignStatus,
    user_id: str = Query(...)
):
    """Update campaign status"""
    try:
        result = await sponsorship_campaigns_service.update_campaign_status(campaign_id, status, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in update_campaign_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CONTRIBUTOR HUB ENDPOINTS =====

@router.get("/contributors/search")
async def search_contributors(
    user_id: str = Query(...),
    roles: Optional[List[ContributorRole]] = Query(None),
    skills: Optional[List[str]] = Query(None),
    genres: Optional[List[str]] = Query(None),
    location: Optional[str] = Query(None),
    budget_max: Optional[float] = Query(None),
    rating_min: Optional[float] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Search contributors"""
    try:
        result = await contributor_hub_service.search_contributors(
            user_id, roles, skills, genres, location, budget_max, rating_min, limit, offset
        )
        return result
    except Exception as e:
        logger.error(f"Error in search_contributors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contributors/requests")
async def get_collaboration_requests(
    user_id: str = Query(...),
    request_type: str = Query("all"),
    status: Optional[CollaborationStatus] = Query(None)
):
    """Get collaboration requests"""
    try:
        result = await contributor_hub_service.get_collaboration_requests(user_id, request_type, status)
        return result
    except Exception as e:
        logger.error(f"Error in get_collaboration_requests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contributors/requests/{request_id}/respond")
async def respond_to_collaboration_request(
    request_id: str,
    response: str,
    message: str,
    user_id: str = Query(...)
):
    """Respond to collaboration request"""
    try:
        result = await contributor_hub_service.respond_to_collaboration_request(request_id, response, message, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in respond_to_collaboration_request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contributors/collaborations")
async def get_active_collaborations(user_id: str = Query(...)):
    """Get active collaborations"""
    try:
        result = await contributor_hub_service.get_active_collaborations(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_active_collaborations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contributors/payments")
async def get_contributor_payments(
    user_id: str = Query(...),
    status: Optional[str] = Query(None)
):
    """Get contributor payments"""
    try:
        result = await contributor_hub_service.get_contributor_payments(user_id, status)
        return result
    except Exception as e:
        logger.error(f"Error in get_contributor_payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contributors/stats")
async def get_contributor_stats(user_id: str = Query(...)):
    """Get contributor statistics"""
    try:
        result = await contributor_hub_service.get_contributor_stats(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_contributor_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== SYSTEM HEALTH & LOGS ENDPOINTS =====

@router.get("/system/health")
async def get_system_health():
    """Get system health status"""
    try:
        result = await system_health_service.get_system_health()
        return result
    except Exception as e:
        logger.error(f"Error in get_system_health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/logs")
async def get_system_logs(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    level: Optional[LogLevel] = Query(None),
    component: Optional[SystemComponent] = Query(None),
    user_id: Optional[str] = Query(None),
    search_text: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get system logs"""
    try:
        query = LogQuery(
            start_time=start_time,
            end_time=end_time,
            level=level,
            component=component,
            user_id=user_id,
            search_text=search_text,
            limit=limit,
            offset=offset
        )
        result = await system_health_service.get_logs(query)
        return result
    except Exception as e:
        logger.error(f"Error in get_system_logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/metrics")
async def get_system_metrics(
    component: Optional[SystemComponent] = Query(None),
    hours: int = Query(24, ge=1, le=168)
):
    """Get system metrics"""
    try:
        result = await system_health_service.get_system_metrics(component, hours)
        return result
    except Exception as e:
        logger.error(f"Error in get_system_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/alerts")
async def get_system_health_alerts(
    severity: Optional[AlertSeverity] = Query(None),
    component: Optional[SystemComponent] = Query(None),
    resolved: Optional[bool] = Query(None)
):
    """Get system alerts"""
    try:
        result = await system_health_service.get_system_alerts(severity, component, resolved)
        return result
    except Exception as e:
        logger.error(f"Error in get_system_health_alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    user_id: str = Query(...)
):
    """Acknowledge system alert"""
    try:
        result = await system_health_service.acknowledge_alert(alert_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in acknowledge_alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/alerts/{alert_id}/resolve")
async def resolve_system_alert(
    alert_id: str,
    user_id: str = Query(...),
    resolution_notes: Optional[str] = Query(None)
):
    """Resolve system alert"""
    try:
        result = await system_health_service.resolve_alert(alert_id, user_id, resolution_notes)
        return result
    except Exception as e:
        logger.error(f"Error in resolve_system_alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        result = await system_health_service.get_system_stats()
        return result
    except Exception as e:
        logger.error(f"Error in get_system_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== DAO GOVERNANCE ENDPOINTS =====

@router.get("/dao/proposals")
async def get_dao_proposals(
    user_id: str = Query(...),
    status: Optional[ProposalStatus] = Query(None),
    proposal_type: Optional[ProposalType] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Get DAO proposals"""
    try:
        result = await dao_governance_service.get_proposals(user_id, status, proposal_type, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_dao_proposals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dao/proposals/{proposal_id}/vote")
async def cast_dao_vote(
    proposal_id: str,
    choice: VoteChoice,
    reason: str,
    user_id: str = Query(...),
    wallet_address: str = Query(...)
):
    """Cast vote on DAO proposal"""
    try:
        result = await dao_governance_service.cast_vote(proposal_id, choice, reason, user_id, wallet_address)
        return result
    except Exception as e:
        logger.error(f"Error in cast_dao_vote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dao/metrics")
async def get_dao_metrics(user_id: str = Query(...)):
    """Get DAO metrics"""
    try:
        result = await dao_governance_service.get_dao_metrics(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_dao_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dao/member")
async def get_dao_member_profile(
    user_id: str = Query(...),
    wallet_address: Optional[str] = Query(None)
):
    """Get DAO member profile"""
    try:
        result = await dao_governance_service.get_member_profile(user_id, wallet_address)
        return result
    except Exception as e:
        logger.error(f"Error in get_dao_member_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dao/delegate")
async def delegate_voting_power(
    delegate_address: str,
    user_id: str = Query(...),
    wallet_address: str = Query(...)
):
    """Delegate voting power"""
    try:
        result = await dao_governance_service.delegate_voting_power(delegate_address, user_id, wallet_address)
        return result
    except Exception as e:
        logger.error(f"Error in delegate_voting_power: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dao/treasury")
async def get_dao_treasury(user_id: str = Query(...)):
    """Get DAO treasury information"""
    try:
        result = await dao_governance_service.get_treasury_info(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_dao_treasury: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dao/contracts")
async def get_dao_smart_contracts(user_id: str = Query(...)):
    """Get DAO smart contracts"""
    try:
        result = await dao_governance_service.get_smart_contracts(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_dao_smart_contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dao/blockchain/status")
async def get_blockchain_integration_status():
    """Get blockchain integration status"""
    try:
        result = await dao_governance_service.get_blockchain_integration_status()
        return result
    except Exception as e:
        logger.error(f"Error in get_blockchain_integration_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dao/blockchain/deploy")
async def deploy_dao_contracts(deployer_address: str = Query(...)):
    """Deploy DAO smart contracts (development/testing)"""
    try:
        result = await dao_governance_service.deploy_dao_contracts(deployer_address)
        return result
    except Exception as e:
        logger.error(f"Error in deploy_dao_contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dao/proposals")
async def create_dao_proposal(
    proposal: GovernanceProposal,
    user_id: str = Query(...)
):
    """Create a new DAO proposal with blockchain integration"""
    try:
        result = await dao_governance_service.create_proposal(proposal, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in create_dao_proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))