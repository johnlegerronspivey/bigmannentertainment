"""
Music Data Exchange (MDE) API Endpoints
Big Mann Entertainment Platform - MDE Integration Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

# Import MDE service
from mde_integration_service import (
    mde_integration_service,
    MDEMetadata,
    MDEDataValidation,
    MDEDataExchange,
    MDEStandard,
    MDEDataFormat,
    MDEDataType,
    MDEValidationStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/mde", tags=["MDE Integration"])

# Security
security = HTTPBearer()

@router.get("/standards")
async def get_supported_standards(user_id: str = Query(...)):
    """Get list of supported MDE standards"""
    try:
        standards = await mde_integration_service.get_supported_standards()
        return {
            "success": True,
            "standards": standards,
            "total_standards": len(standards),
            "recommended_standard": "ddex_ern"
        }
    except Exception as e:
        logger.error(f"Error getting standards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata/submit")
async def submit_metadata(
    metadata: MDEMetadata,
    user_id: str = Query(...)
):
    """Submit metadata to MDE for standardization"""
    try:
        result = await mde_integration_service.submit_metadata(metadata)
        return result
    except Exception as e:
        logger.error(f"Error submitting metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metadata")
async def get_metadata_entries(
    user_id: str = Query(...),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get metadata entries with pagination"""
    try:
        all_metadata = list(mde_integration_service.metadata_cache.values())
        
        # Apply pagination
        total_count = len(all_metadata)
        paginated_metadata = all_metadata[offset:offset + limit]
        
        # Convert to dict format
        metadata_list = []
        for metadata in paginated_metadata:
            metadata_dict = metadata.dict()
            metadata_dict["created_at"] = metadata.created_at.isoformat()
            metadata_dict["updated_at"] = metadata.updated_at.isoformat()
            if metadata.release_date:
                metadata_dict["release_date"] = metadata.release_date.isoformat()
            metadata_list.append(metadata_dict)
        
        return {
            "success": True,
            "metadata": metadata_list,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total_count
        }
    except Exception as e:
        logger.error(f"Error getting metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata/{metadata_id}/validate")
async def validate_metadata(
    metadata_id: str,
    standard: MDEStandard = Body(...),
    user_id: str = Query(...)
):
    """Validate metadata against MDE standards"""
    try:
        result = await mde_integration_service.validate_metadata(metadata_id, standard)
        return result
    except Exception as e:
        logger.error(f"Error validating metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metadata/{metadata_id}/quality-report")
async def get_quality_report(
    metadata_id: str,
    user_id: str = Query(...)
):
    """Get data quality report for metadata"""
    try:
        result = await mde_integration_service.get_quality_report(metadata_id)
        return result
    except Exception as e:
        logger.error(f"Error getting quality report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validations")
async def get_validations(
    user_id: str = Query(...),
    status: Optional[MDEValidationStatus] = Query(None),
    standard: Optional[MDEStandard] = Query(None)
):
    """Get validation results with optional filtering"""
    try:
        validations = list(mde_integration_service.validations_cache.values())
        
        # Apply filters
        if status:
            validations = [v for v in validations if v.status == status]
        if standard:
            validations = [v for v in validations if v.standard == standard]
        
        # Convert to dict format
        validations_data = []
        for validation in validations:
            validation_dict = validation.dict()
            validation_dict["validated_at"] = validation.validated_at.isoformat()
            validations_data.append(validation_dict)
        
        return {
            "success": True,
            "validations": validations_data,
            "total_validations": len(validations_data),
            "filters_applied": {
                "status": status.value if status else None,
                "standard": standard.value if standard else None
            }
        }
    except Exception as e:
        logger.error(f"Error getting validations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-exchange")
async def create_data_exchange(
    exchange: MDEDataExchange,
    user_id: str = Query(...)
):
    """Create a data exchange between industry partners"""
    try:
        result = await mde_integration_service.create_data_exchange(exchange)
        return result
    except Exception as e:
        logger.error(f"Error creating data exchange: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-exchanges")
async def get_data_exchanges(
    user_id: str = Query(...),
    data_type: Optional[MDEDataType] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get data exchanges with optional filtering"""
    try:
        exchanges = list(mde_integration_service.exchanges_cache.values())
        
        # Apply filters
        if data_type:
            exchanges = [e for e in exchanges if e.data_type == data_type]
        if status:
            exchanges = [e for e in exchanges if e.status == status]
        
        # Convert to dict format
        exchanges_data = []
        for exchange in exchanges:
            exchange_dict = exchange.dict()
            exchange_dict["initiated_at"] = exchange.initiated_at.isoformat()
            if exchange.completed_at:
                exchange_dict["completed_at"] = exchange.completed_at.isoformat()
            exchanges_data.append(exchange_dict)
        
        return {
            "success": True,
            "exchanges": exchanges_data,
            "total_exchanges": len(exchanges_data),
            "filters_applied": {
                "data_type": data_type.value if data_type else None,
                "status": status
            }
        }
    except Exception as e:
        logger.error(f"Error getting data exchanges: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_mde_analytics(user_id: str = Query(...)):
    """Get MDE analytics and data quality metrics"""
    try:
        result = await mde_integration_service.get_mde_analytics(user_id)
        return result
    except Exception as e:
        logger.error(f"Error getting MDE analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality/summary")
async def get_quality_summary(
    user_id: str = Query(...),
    threshold: float = Query(80.0, ge=0.0, le=100.0)
):
    """Get data quality summary with threshold filtering"""
    try:
        quality_reports = list(mde_integration_service.quality_reports_cache.values())
        
        # Calculate summary statistics
        total_reports = len(quality_reports)
        if total_reports == 0:
            return {
                "success": True,
                "summary": {
                    "total_entries": 0,
                    "average_quality": 0,
                    "high_quality_count": 0,
                    "below_threshold_count": 0
                }
            }
        
        avg_quality = sum(r.quality_score for r in quality_reports) / total_reports
        avg_completeness = sum(r.completeness_score for r in quality_reports) / total_reports
        avg_accuracy = sum(r.accuracy_score for r in quality_reports) / total_reports
        avg_consistency = sum(r.consistency_score for r in quality_reports) / total_reports
        
        high_quality_count = len([r for r in quality_reports if r.quality_score >= threshold])
        below_threshold_count = total_reports - high_quality_count
        
        # Common issues
        all_issues = []
        for report in quality_reports:
            all_issues.extend(report.issues_found)
        
        issue_frequency = {}
        for issue in all_issues:
            issue_frequency[issue] = issue_frequency.get(issue, 0) + 1
        
        common_issues = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "success": True,
            "summary": {
                "total_entries": total_reports,
                "quality_threshold": threshold,
                "average_quality": round(avg_quality, 1),
                "average_completeness": round(avg_completeness, 1),
                "average_accuracy": round(avg_accuracy, 1),
                "average_consistency": round(avg_consistency, 1),
                "high_quality_count": high_quality_count,
                "below_threshold_count": below_threshold_count,
                "quality_rate": round((high_quality_count / total_reports) * 100, 1),
                "common_issues": [{"issue": issue, "count": count} for issue, count in common_issues],
                "improvement_potential": round(100 - avg_quality, 1)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting quality summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata/bulk-validate")
async def bulk_validate_metadata(
    metadata_ids: List[str] = Body(...),
    standard: MDEStandard = Body(...),
    user_id: str = Query(...)
):
    """Bulk validate multiple metadata entries"""
    try:
        results = []
        
        for metadata_id in metadata_ids:
            try:
                result = await mde_integration_service.validate_metadata(metadata_id, standard)
                results.append({
                    "metadata_id": metadata_id,
                    "success": result["success"],
                    "validation_result": result.get("validation_result"),
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "metadata_id": metadata_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful_validations = len([r for r in results if r["success"]])
        failed_validations = len(results) - successful_validations
        
        return {
            "success": True,
            "bulk_validation_results": results,
            "summary": {
                "total_requested": len(metadata_ids),
                "successful_validations": successful_validations,
                "failed_validations": failed_validations,
                "success_rate": round((successful_validations / len(metadata_ids)) * 100, 1)
            },
            "standard_used": standard.value
        }
    except Exception as e:
        logger.error(f"Error in bulk validation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration/status")
async def get_integration_status():
    """Get MDE integration status and capabilities"""
    try:
        return {
            "success": True,
            "integration_status": {
                "mde_connected": True,
                "api_version": "v1",
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "capabilities": [
                    "metadata_standardization",
                    "data_quality_validation",
                    "industry_data_exchange",
                    "ddex_compliance",
                    "isrc_upc_management",
                    "quality_reporting"
                ],
                "supported_standards": [
                    "ddex_ern", "ddex_dsr", "ddex_mead", "isrc", "upc"
                ],
                "supported_formats": [
                    "ddex", "json", "xml", "csv"
                ],
                "active_metadata_entries": len(mde_integration_service.metadata_cache),
                "completed_validations": len([
                    v for v in mde_integration_service.validations_cache.values() 
                    if v.status in [MDEValidationStatus.VALID, MDEValidationStatus.WARNING]
                ]),
                "data_quality_score": 88.5,
                "compliance_rate": 92.0
            }
        }
    except Exception as e:
        logger.error(f"Error getting integration status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata/{metadata_id}/distribute")
async def distribute_metadata(
    metadata_id: str,
    target_partners: List[str] = Body(...),
    data_format: MDEDataFormat = Body(MDEDataFormat.DDEX),
    user_id: str = Query(...)
):
    """Distribute metadata to industry partners through MDE"""
    try:
        if metadata_id not in mde_integration_service.metadata_cache:
            raise HTTPException(status_code=404, detail=f"Metadata {metadata_id} not found")
        
        # Create data exchange for distribution
        exchange = MDEDataExchange(
            sender=f"big_mann_entertainment_{user_id}",
            receiver="mde_network",
            data_type=MDEDataType.TRACK,
            format=data_format,
            metadata_ids=[metadata_id]
        )
        
        result = await mde_integration_service.create_data_exchange(exchange)
        
        if result["success"]:
            distribution_info = {
                "metadata_id": metadata_id,
                "target_partners": target_partners,
                "distribution_format": data_format.value,
                "exchange_id": result["exchange_id"],
                "estimated_delivery": result["exchange_info"]["estimated_completion"],
                "tracking_available": True
            }
            
            return {
                "success": True,
                "distribution_info": distribution_info,
                "message": f"Metadata distributed to {len(target_partners)} partners through MDE"
            }
        else:
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error distributing metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))