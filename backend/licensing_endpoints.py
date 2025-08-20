from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from auth import get_current_user, require_admin
from licensing_service import LicensingService
from licensing_models import PlatformLicense, LicensingAgreement

router = APIRouter(prefix="/api/licensing", tags=["Licensing System"])
licensing_service = LicensingService()

# Import the existing platforms configuration
from server import DISTRIBUTION_PLATFORMS

@router.post("/initialize-all-platforms")
async def initialize_all_platform_licenses(current_user: dict = Depends(require_admin)):
    """Initialize licenses for all 83+ platforms"""
    try:
        # Initialize licenses for all platforms
        created_licenses = licensing_service.initialize_all_platform_licenses(DISTRIBUTION_PLATFORMS)
        
        # Create master licensing agreement
        license_ids = list(created_licenses.values())
        master_agreement_id = licensing_service.create_master_licensing_agreement(license_ids)
        
        # Activate all platform licenses
        activations = {}
        for platform_id, license_id in created_licenses.items():
            activation_id = licensing_service.activate_platform_license(
                platform_id, license_id, current_user.get("email", "admin")
            )
            activations[platform_id] = activation_id
        
        return {
            "message": f"Successfully licensed and activated {len(created_licenses)} platforms",
            "platforms_licensed": len(created_licenses),
            "master_agreement_id": master_agreement_id,
            "platform_licenses": created_licenses,
            "platform_activations": activations,
            "business_entity": "Big Mann Entertainment",
            "license_owner": "John LeGerron Spivey"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize platform licenses: {str(e)}")

@router.get("/api/licensing/dashboard")
async def get_licensing_dashboard(current_user: dict = Depends(get_current_user)):
    """Get comprehensive licensing dashboard"""
    try:
        dashboard_data = licensing_service.get_licensing_dashboard()
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get licensing dashboard: {str(e)}")

@router.get("/api/licensing/platforms")
async def get_platform_licenses(
    status: Optional[str] = None,
    platform_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all platform licenses with optional filtering"""
    try:
        licenses = licensing_service.get_platform_licenses(status=status, platform_type=platform_type)
        return {
            "total_licenses": len(licenses),
            "licenses": licenses,
            "filters_applied": {
                "status": status,
                "platform_type": platform_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform licenses: {str(e)}")

@router.get("/api/licensing/platforms/{platform_id}")
async def get_platform_license_details(platform_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed licensing information for a specific platform"""
    try:
        license_doc = licensing_service.platform_licenses.find_one({"platform_id": platform_id})
        
        if not license_doc:
            raise HTTPException(status_code=404, detail="Platform license not found")
        
        # Convert ObjectId to string
        license_doc["_id"] = str(license_doc["_id"])
        
        # Get platform activation status
        activation = licensing_service.platform_activations.find_one({"platform_id": platform_id})
        if activation:
            activation["_id"] = str(activation["_id"])
        
        # Get recent usage data
        recent_usage = list(licensing_service.license_usage.find(
            {"platform_id": platform_id}
        ).sort("usage_date", -1).limit(10))
        
        for usage in recent_usage:
            usage["_id"] = str(usage["_id"])
        
        return {
            "platform_license": license_doc,
            "activation_status": activation,
            "recent_usage": recent_usage,
            "platform_config": DISTRIBUTION_PLATFORMS.get(platform_id, {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform license details: {str(e)}")

@router.post("/api/licensing/platforms/{platform_id}/activate")
async def activate_platform_license(platform_id: str, current_user: dict = Depends(require_admin)):
    """Activate a platform license"""
    try:
        # Check if license exists
        license_doc = licensing_service.platform_licenses.find_one({"platform_id": platform_id})
        if not license_doc:
            raise HTTPException(status_code=404, detail="Platform license not found")
        
        license_id = str(license_doc.get("id", license_doc["_id"]))
        
        # Activate the license
        activation_id = licensing_service.activate_platform_license(
            platform_id, license_id, current_user.get("email", "admin")
        )
        
        # Update license status to active
        licensing_service.platform_licenses.update_one(
            {"platform_id": platform_id},
            {"$set": {"license_status": "active", "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": f"Platform {platform_id} license activated successfully",
            "platform_id": platform_id,
            "activation_id": activation_id,
            "activated_by": current_user.get("email", "admin"),
            "activation_date": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate platform license: {str(e)}")

@router.post("/api/licensing/platforms/{platform_id}/deactivate")
async def deactivate_platform_license(platform_id: str, reason: str, current_user: dict = Depends(require_admin)):
    """Deactivate a platform license"""
    try:
        # Update activation status
        licensing_service.platform_activations.update_one(
            {"platform_id": platform_id},
            {
                "$set": {
                    "is_active": False,
                    "deactivation_date": datetime.utcnow(),
                    "deactivation_reason": reason,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update license status
        licensing_service.platform_licenses.update_one(
            {"platform_id": platform_id},
            {"$set": {"license_status": "suspended", "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": f"Platform {platform_id} license deactivated",
            "platform_id": platform_id,
            "deactivated_by": current_user.get("email", "admin"),
            "reason": reason,
            "deactivation_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate platform license: {str(e)}")

@router.post("/api/licensing/compliance-check/{platform_id}")
async def run_compliance_check(platform_id: str, current_user: dict = Depends(get_current_user)):
    """Run compliance check for a platform license"""
    try:
        license_doc = licensing_service.platform_licenses.find_one({"platform_id": platform_id})
        if not license_doc:
            raise HTTPException(status_code=404, detail="Platform license not found")
        
        license_id = str(license_doc.get("id", license_doc["_id"]))
        compliance_result = licensing_service.check_compliance(platform_id, license_id)
        
        return compliance_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run compliance check: {str(e)}")

@router.post("/api/licensing/usage/{platform_id}")
async def update_platform_usage(platform_id: str, usage_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Update usage metrics for a platform license"""
    try:
        license_doc = licensing_service.platform_licenses.find_one({"platform_id": platform_id})
        if not license_doc:
            raise HTTPException(status_code=404, detail="Platform license not found")
        
        license_id = str(license_doc.get("id", license_doc["_id"]))
        
        # Add platform_id to usage_data
        usage_data["platform_id"] = platform_id
        
        success = licensing_service.update_license_usage(license_id, usage_data)
        
        if success:
            return {
                "message": "Usage metrics updated successfully",
                "platform_id": platform_id,
                "usage_data": usage_data,
                "updated_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update usage metrics")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update platform usage: {str(e)}")

@router.get("/api/licensing/agreements")
async def get_licensing_agreements(current_user: dict = Depends(get_current_user)):
    """Get all licensing agreements"""
    try:
        agreements = list(licensing_service.licensing_agreements.find({}))
        
        for agreement in agreements:
            agreement["_id"] = str(agreement["_id"])
            
        return {
            "total_agreements": len(agreements),
            "agreements": agreements
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get licensing agreements: {str(e)}")

@router.get("/api/licensing/status")
async def get_overall_licensing_status(current_user: dict = Depends(get_current_user)):
    """Get overall licensing status for Big Mann Entertainment"""
    try:
        dashboard_data = licensing_service.get_licensing_dashboard()
        
        # Calculate licensing health score
        total_platforms = dashboard_data["licensing_overview"]["total_platforms_licensed"]
        active_platforms = dashboard_data["licensing_overview"]["active_licenses"]
        compliance_rate = dashboard_data["licensing_overview"]["licensing_compliance_rate"]
        
        health_score = ((active_platforms / total_platforms) * 0.7 + (compliance_rate / 100) * 0.3) * 100 if total_platforms > 0 else 0
        
        return {
            "business_entity": "Big Mann Entertainment",
            "business_owner": "John LeGerron Spivey",
            "total_platforms_licensed": total_platforms,
            "active_licenses": active_platforms,
            "licensing_health_score": round(health_score, 2),
            "compliance_rate": compliance_rate,
            "licensing_status": "Fully Licensed" if health_score > 90 else "Needs Attention",
            "master_agreement_active": True,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get licensing status: {str(e)}")