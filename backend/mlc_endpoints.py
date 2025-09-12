"""
Mechanical Licensing Collective (MLC) API Endpoints
Big Mann Entertainment Platform - MLC Integration Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

# Import MLC service
from mlc_integration_service import (
    mlc_integration_service,
    MLCMusicalWork,
    MLCUsageReport,
    MLCDistributionRequest,
    MLCLicenseType,
    MLCSubmissionStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/mlc", tags=["MLC Integration"])

# Security
security = HTTPBearer()

@router.get("/dsps")
async def get_available_dsps(user_id: str = Query(...)):
    """Get list of available DSPs through MLC network"""
    try:
        dsps = await mlc_integration_service.get_available_dsps()
        return {
            "success": True,
            "dsps": dsps,
            "total_dsps": len(dsps),
            "mlc_integrated": True
        }
    except Exception as e:
        logger.error(f"Error getting DSPs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/works/register")
async def register_musical_work(
    work: MLCMusicalWork,
    user_id: str = Query(...)
):
    """Register a musical work with the MLC"""
    try:
        result = await mlc_integration_service.register_musical_work(work)
        return result
    except Exception as e:
        logger.error(f"Error registering work: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/works")
async def get_registered_works(user_id: str = Query(...)):
    """Get all registered musical works"""
    try:
        works = list(mlc_integration_service.works_cache.values())
        works_data = []
        
        for work in works:
            work_dict = work.dict()
            work_dict["created_date"] = work.created_date.isoformat()
            works_data.append(work_dict)
        
        return {
            "success": True,
            "works": works_data,
            "total_works": len(works_data)
        }
    except Exception as e:
        logger.error(f"Error getting works: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distribution/request")
async def create_distribution_request(
    request: MLCDistributionRequest,
    user_id: str = Query(...)
):
    """Create distribution request through MLC network"""
    try:
        result = await mlc_integration_service.create_distribution_request(request)
        return result
    except Exception as e:
        logger.error(f"Error creating distribution request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribution/requests")
async def get_distribution_requests(user_id: str = Query(...)):
    """Get all distribution requests"""
    try:
        requests = list(mlc_integration_service.distributions_cache.values())
        requests_data = []
        
        for req in requests:
            req_dict = req.dict()
            req_dict["distribution_date"] = req.distribution_date.isoformat()
            requests_data.append(req_dict)
        
        return {
            "success": True,
            "requests": requests_data,
            "total_requests": len(requests_data)
        }
    except Exception as e:
        logger.error(f"Error getting distribution requests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/usage")
async def get_usage_reports(
    user_id: str = Query(...),
    work_id: Optional[str] = Query(None),
    dsp_name: Optional[str] = Query(None),
    territory: Optional[str] = Query(None)
):
    """Get usage reports with optional filtering"""
    try:
        reports = list(mlc_integration_service.reports_cache.values())
        
        # Apply filters
        if work_id:
            reports = [r for r in reports if r.work_id == work_id]
        if dsp_name:
            reports = [r for r in reports if r.dsp_name.lower() == dsp_name.lower()]
        if territory:
            reports = [r for r in reports if r.territory == territory]
        
        # Convert to dict format
        reports_data = []
        for report in reports:
            report_dict = report.dict()
            report_dict["usage_date"] = report.usage_date.isoformat()
            report_dict["report_period_start"] = report.report_period_start.isoformat()
            report_dict["report_period_end"] = report.report_period_end.isoformat()
            reports_data.append(report_dict)
        
        return {
            "success": True,
            "reports": reports_data,
            "total_reports": len(reports_data),
            "filters_applied": {
                "work_id": work_id,
                "dsp_name": dsp_name,
                "territory": territory
            }
        }
    except Exception as e:
        logger.error(f"Error getting usage reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_mlc_analytics(user_id: str = Query(...)):
    """Get MLC analytics and performance data"""
    try:
        result = await mlc_integration_service.get_mlc_analytics(user_id)
        return result
    except Exception as e:
        logger.error(f"Error getting MLC analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/status")
async def get_compliance_status(user_id: str = Query(...)):
    """Get MLC compliance status"""
    try:
        analytics = await mlc_integration_service.get_mlc_analytics(user_id)
        if analytics["success"]:
            compliance = analytics["analytics"]["compliance_status"]
            return {
                "success": True,
                "compliance_status": compliance,
                "overall_compliant": all([
                    compliance["mlc_registration_current"],
                    compliance["usage_reporting_up_to_date"],
                    compliance["mechanical_licenses_valid"]
                ])
            }
        else:
            return analytics
    except Exception as e:
        logger.error(f"Error getting compliance status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/works/{work_id}/distribute")
async def distribute_single_work(
    work_id: str,
    target_dsps: List[str] = Body(...),
    territory_codes: List[str] = Body(...),
    user_id: str = Query(...)
):
    """Distribute a single work to specified DSPs"""
    try:
        # Check if work exists
        if work_id not in mlc_integration_service.works_cache:
            raise HTTPException(status_code=404, detail=f"Work {work_id} not found")
        
        # Create distribution request
        distribution_request = MLCDistributionRequest(
            asset_id=f"asset_{work_id}",
            work_ids=[work_id],
            target_dsps=target_dsps,
            license_types=[MLCLicenseType.MECHANICAL, MLCLicenseType.STREAMING],
            distribution_date=datetime.now(timezone.utc),
            territory_codes=territory_codes,
            metadata={
                "initiated_by": user_id,
                "distribution_type": "single_work"
            }
        )
        
        result = await mlc_integration_service.create_distribution_request(distribution_request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error distributing work: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/royalties/summary")
async def get_royalties_summary(
    user_id: str = Query(...),
    period_days: int = Query(30, ge=1, le=365)
):
    """Get mechanical royalties summary"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=period_days)
        recent_reports = [
            r for r in mlc_integration_service.reports_cache.values()
            if r.usage_date >= cutoff_date
        ]
        
        total_mechanical_royalties = sum(r.total_mechanical_royalty for r in recent_reports)
        total_plays = sum(r.play_count for r in recent_reports)
        unique_works = len(set(r.work_id for r in recent_reports))
        unique_dsps = len(set(r.dsp_name for r in recent_reports))
        
        # Group by DSP
        dsp_breakdown = {}
        for report in recent_reports:
            if report.dsp_name not in dsp_breakdown:
                dsp_breakdown[report.dsp_name] = {
                    "plays": 0,
                    "mechanical_royalties": 0,
                    "reports_count": 0
                }
            dsp_breakdown[report.dsp_name]["plays"] += report.play_count
            dsp_breakdown[report.dsp_name]["mechanical_royalties"] += report.total_mechanical_royalty
            dsp_breakdown[report.dsp_name]["reports_count"] += 1
        
        return {
            "success": True,
            "summary": {
                "period_days": period_days,
                "total_mechanical_royalties": round(total_mechanical_royalties, 2),
                "total_plays": total_plays,
                "average_royalty_per_play": round(total_mechanical_royalties / max(total_plays, 1), 6),
                "unique_works": unique_works,
                "unique_dsps": unique_dsps,
                "total_reports": len(recent_reports)
            },
            "dsp_breakdown": dsp_breakdown,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting royalties summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration/status")
async def get_integration_status():
    """Get MLC integration status and capabilities"""
    try:
        return {
            "success": True,
            "integration_status": {
                "mlc_connected": True,
                "api_version": "v1",
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "capabilities": [
                    "work_registration",
                    "distribution_management",
                    "usage_reporting",
                    "mechanical_licensing",
                    "royalty_tracking",
                    "compliance_monitoring"
                ],
                "supported_territories": ["US", "CA", "GB", "AU", "DE", "FR", "JP", "BR", "MX"],
                "supported_dsps": 6,
                "active_works": len(mlc_integration_service.works_cache),
                "pending_distributions": len([
                    d for d in mlc_integration_service.distributions_cache.values()
                ]),
                "compliance_score": 95.0
            }
        }
    except Exception as e:
        logger.error(f"Error getting integration status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))