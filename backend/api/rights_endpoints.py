"""
Rights & Compliance API Endpoints
Handles territory rights, usage rights validation, and embargo management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, date
import jwt

from rights_models import (
    TerritoryCode, UsageRightType, RightsOwnership, ComplianceCheckResult,
    RightsValidationConfig, TerritoryRights, UsageRights, EmbargoRestriction,
    ComplianceStatus
)
from rights_compliance_service import RightsComplianceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rights", tags=["Rights & Compliance"])

# Global service (will be initialized in server.py)
rights_service = None
mongo_db = None

# Authentication setup (copied from server.py to avoid circular import)
SECRET_KEY = "big-mann-entertainment-secret-key-2025"
ALGORITHM = "HS256"
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    if mongo_db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    user = await mongo_db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Get current admin user"""
    if not current_user.get('is_admin') and current_user.get('role') not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

def init_rights_service(db, services_dict):
    """Initialize rights & compliance service"""
    global rights_service, mongo_db
    mongo_db = db
    rights_service = RightsComplianceService(mongo_db=db)
    services_dict['rights_compliance'] = rights_service

@router.post("/check-compliance")
async def check_rights_compliance(
    content_id: str = Form(...),
    isrc: Optional[str] = Form(None),
    territories: List[str] = Form(...),
    usage_types: List[str] = Form(...),
    strict_mode: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    """Check rights compliance for content across territories and usage types"""
    
    try:
        # Parse territories and usage types
        try:
            territory_codes = [TerritoryCode(t) for t in territories]
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid territory code: {str(e)}"
            )
        
        try:
            usage_type_codes = [UsageRightType(u) for u in usage_types]
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid usage type: {str(e)}"
            )
        
        # Create validation config
        config = RightsValidationConfig(
            strict_mode=strict_mode,
            default_territories=territory_codes,
            default_usage_types=usage_type_codes
        )
        
        # Perform compliance check
        compliance_result = await rights_service.check_rights_compliance(
            content_id=content_id,
            isrc=isrc,
            territories=territory_codes,
            usage_types=usage_type_codes,
            config=config,
            checked_by=current_user.get('id')
        )
        
        return {
            "success": True,
            "message": "Compliance check completed",
            "compliance_result": compliance_result.dict(),
            "summary": {
                "overall_status": compliance_result.overall_status,
                "violations_count": len(compliance_result.violations),
                "warnings_count": len(compliance_result.warnings),
                "missing_rights_count": len(compliance_result.missing_rights),
                "expired_rights_count": len(compliance_result.expired_rights),
                "embargoed_items_count": len(compliance_result.embargoed_items),
                "processing_time": compliance_result.processing_time
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking rights compliance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check rights compliance: {str(e)}"
        )

@router.post("/ownership")
async def create_rights_ownership(
    rights_data: RightsOwnership,
    current_user: dict = Depends(get_current_user)
):
    """Create or update rights ownership record"""
    
    try:
        # Set creator information
        rights_data.created_by = current_user.get('id')
        rights_data.created_date = datetime.now()
        
        # Create rights ownership
        content_id = await rights_service.create_rights_ownership(rights_data)
        
        return {
            "success": True,
            "message": "Rights ownership record created successfully",
            "content_id": content_id
        }
        
    except Exception as e:
        logger.error(f"Error creating rights ownership: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create rights ownership: {str(e)}"
        )

@router.get("/ownership/{content_id}")
async def get_rights_ownership(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get rights ownership information for content"""
    
    try:
        rights_data = await rights_service._load_rights_ownership(content_id, None)
        
        if not rights_data:
            raise HTTPException(
                status_code=404,
                detail="Rights ownership record not found"
            )
        
        return {
            "success": True,
            "rights_ownership": rights_data.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rights ownership: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve rights ownership: {str(e)}"
        )

@router.get("/territories")
async def get_supported_territories():
    """Get list of supported territories and their information"""
    
    try:
        territories_info = {}
        
        for territory in TerritoryCode:
            territory_mapping = rights_service.get_territory_info(territory) if rights_service else None
            
            if territory_mapping:
                territories_info[territory.value] = {
                    "name": territory_mapping.territory_name,
                    "region": territory_mapping.region,
                    "iso_code": territory_mapping.iso_code,
                    "currency": territory_mapping.currency,
                    "time_zone": territory_mapping.time_zone,
                    "eu_member": territory_mapping.eu_member,
                    "embargo_prone": territory_mapping.embargo_prone,
                    "collecting_societies": territory_mapping.collecting_societies
                }
            else:
                territories_info[territory.value] = {
                    "name": territory.value,
                    "region": "Unknown",
                    "iso_code": territory.value
                }
        
        return {
            "success": True,
            "territories": territories_info,
            "total_count": len(territories_info)
        }
        
    except Exception as e:
        logger.error(f"Error getting territories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get territories: {str(e)}"
        )

@router.get("/usage-types")
async def get_usage_types():
    """Get list of supported usage types"""
    
    try:
        usage_types_info = {}
        
        for usage_type in UsageRightType:
            usage_types_info[usage_type.value] = {
                "name": usage_type.value.replace('_', ' ').title(),
                "description": f"{usage_type.value} rights and permissions"
            }
        
        # Add detailed descriptions
        descriptions = {
            "streaming": "Digital streaming services (Spotify, Apple Music, etc.)",
            "download": "Digital download platforms (iTunes, Amazon, etc.)",
            "physical": "Physical distribution (CDs, vinyl, etc.)",
            "radio": "Radio broadcasting (terrestrial, satellite, internet)",
            "tv": "Television broadcasting and programming",
            "sync": "Synchronization for film, TV, advertising, games",
            "public_performance": "Live venues, concerts, background music",
            "mechanical": "Mechanical reproduction rights",
            "print": "Sheet music and lyric publications",
            "master": "Master recording ownership rights",
            "publishing": "Musical composition and publishing rights",
            "neighboring": "Performers and producers neighboring rights"
        }
        
        for usage_type, info in usage_types_info.items():
            if usage_type in descriptions:
                info["description"] = descriptions[usage_type]
        
        return {
            "success": True,
            "usage_types": usage_types_info,
            "total_count": len(usage_types_info)
        }
        
    except Exception as e:
        logger.error(f"Error getting usage types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage types: {str(e)}"
        )

@router.get("/templates/usage-rights")
async def get_usage_rights_templates():
    """Get pre-defined usage rights templates"""
    
    try:
        templates = {}
        
        if rights_service and rights_service.usage_templates:
            for template_name, template in rights_service.usage_templates.items():
                templates[template_name] = {
                    "name": template.template_name,
                    "description": template.description,
                    "usage_types": [ut.value for ut in template.usage_types],
                    "default_territories": [tc.value for tc in template.default_territories],
                    "standard_royalty_rates": template.standard_royalty_rates,
                    "exclusivity_default": template.exclusivity_default,
                    "typical_term_months": template.typical_term_months,
                    "industry_standard": template.industry_standard,
                    "common_restrictions": template.common_restrictions
                }
        
        return {
            "success": True,
            "usage_templates": templates,
            "total_count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Error getting usage templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage templates: {str(e)}"
        )

@router.get("/compliance-history/{content_id}")
async def get_compliance_history(
    content_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get compliance check history for content"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get compliance history
        query = {"content_id": content_id}
        
        # Get total count
        total_count = await mongo_db["compliance_check_results"].count_documents(query)
        
        # Get paginated results
        cursor = mongo_db["compliance_check_results"].find(query).sort("check_date", -1).skip(offset).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id for response
        for result in results:
            result.pop("_id", None)
        
        return {
            "success": True,
            "compliance_history": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compliance history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get compliance history: {str(e)}"
        )

@router.post("/quick-check")
async def quick_compliance_check(
    isrc: str = Form(...),
    territory: str = Form(...),
    usage_type: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Quick compliance check for ISRC in specific territory and usage"""
    
    try:
        # Parse inputs
        territory_code = TerritoryCode(territory)
        usage_type_code = UsageRightType(usage_type)
        
        # Perform quick check
        compliance_result = await rights_service.check_rights_compliance(
            content_id=f"quick_check_{isrc}",
            isrc=isrc,
            territories=[territory_code],
            usage_types=[usage_type_code],
            checked_by=current_user.get('id')
        )
        
        # Simplified response for quick check
        return {
            "success": True,
            "isrc": isrc,
            "territory": territory,
            "usage_type": usage_type,
            "compliance_status": compliance_result.overall_status,
            "is_compliant": compliance_result.overall_status == ComplianceStatus.COMPLIANT,
            "has_warnings": len(compliance_result.warnings) > 0,
            "has_violations": len(compliance_result.violations) > 0,
            "summary_message": f"ISRC {isrc} is {compliance_result.overall_status.value} for {usage_type} in {territory}",
            "violations": compliance_result.violations[:3],  # First 3 violations
            "warnings": compliance_result.warnings[:3],     # First 3 warnings
            "processing_time": compliance_result.processing_time
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in quick compliance check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform quick check: {str(e)}"
        )

@router.get("/dashboard/rights-summary")
async def get_rights_dashboard_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get rights management dashboard summary for user"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # User's rights ownership count
        user_query = {"created_by": current_user.get('id')}
        total_rights_records = await mongo_db["rights_ownership"].count_documents(user_query)
        
        # Recent compliance checks
        recent_checks_query = {"checked_by": current_user.get('id')}
        recent_checks = await mongo_db["compliance_check_results"].count_documents(recent_checks_query)
        
        # Compliance status breakdown
        status_pipeline = [
            {"$match": {"checked_by": current_user.get('id')}},
            {"$group": {"_id": "$overall_status", "count": {"$sum": 1}}}
        ]
        
        status_results = await mongo_db["compliance_check_results"].aggregate(status_pipeline).to_list(None)
        status_breakdown = {result["_id"]: result["count"] for result in status_results}
        
        # Items requiring attention (non-compliant or warnings)
        attention_needed = status_breakdown.get("non_compliant", 0) + status_breakdown.get("warning", 0)
        
        return {
            "success": True,
            "rights_summary": {
                "total_rights_records": total_rights_records,
                "recent_compliance_checks": recent_checks,
                "compliance_breakdown": status_breakdown,
                "items_needing_attention": attention_needed,
                "compliance_rate": (status_breakdown.get("compliant", 0) / recent_checks * 100) if recent_checks > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting rights dashboard summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get rights summary: {str(e)}"
        )

# Admin endpoints
@router.get("/admin/all-rights")
async def admin_get_all_rights(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin_user)
):
    """Admin endpoint to get all rights ownership records"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get total count
        total_count = await mongo_db["rights_ownership"].count_documents({})
        
        # Get paginated results
        cursor = mongo_db["rights_ownership"].find({}).sort("created_date", -1).skip(offset).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id for response
        for result in results:
            result.pop("_id", None)
        
        return {
            "success": True,
            "rights_records": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting all rights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get all rights: {str(e)}"
        )

@router.get("/admin/compliance-analytics")
async def admin_get_compliance_analytics(
    current_user: dict = Depends(get_current_admin_user)
):
    """Admin endpoint for compliance analytics"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Overall compliance statistics
        total_checks = await mongo_db["compliance_check_results"].count_documents({})
        
        # Status breakdown
        status_pipeline = [
            {"$group": {"_id": "$overall_status", "count": {"$sum": 1}}}
        ]
        status_results = await mongo_db["compliance_check_results"].aggregate(status_pipeline).to_list(None)
        status_breakdown = {result["_id"]: result["count"] for result in status_results}
        
        # Territory compliance
        territory_pipeline = [
            {"$unwind": "$territory_compliance"},
            {"$group": {
                "_id": "$territory_compliance.k",
                "compliant": {
                    "$sum": {
                        "$cond": [{"$eq": ["$territory_compliance.v", "compliant"]}, 1, 0]
                    }
                },
                "total": {"$sum": 1}
            }}
        ]
        
        territory_results = await mongo_db["compliance_check_results"].aggregate(territory_pipeline).to_list(None)
        territory_analytics = {
            result["_id"]: {
                "compliance_rate": (result["compliant"] / result["total"] * 100) if result["total"] > 0 else 0,
                "total_checks": result["total"]
            }
            for result in territory_results
        }
        
        # Usage type compliance
        usage_pipeline = [
            {"$unwind": "$usage_compliance"},
            {"$group": {
                "_id": "$usage_compliance.k",
                "compliant": {
                    "$sum": {
                        "$cond": [{"$eq": ["$usage_compliance.v", "compliant"]}, 1, 0]
                    }
                },
                "total": {"$sum": 1}
            }}
        ]
        
        usage_results = await mongo_db["compliance_check_results"].aggregate(usage_pipeline).to_list(None)
        usage_analytics = {
            result["_id"]: {
                "compliance_rate": (result["compliant"] / result["total"] * 100) if result["total"] > 0 else 0,
                "total_checks": result["total"]
            }
            for result in usage_results
        }
        
        return {
            "success": True,
            "compliance_analytics": {
                "total_compliance_checks": total_checks,
                "overall_status_breakdown": status_breakdown,
                "territory_compliance": territory_analytics,
                "usage_type_compliance": usage_analytics,
                "platform_compliance_rate": (status_breakdown.get("compliant", 0) / total_checks * 100) if total_checks > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting compliance analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get compliance analytics: {str(e)}"
        )