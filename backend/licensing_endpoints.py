from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import jwt
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import uuid

from licensing_service import LicensingService
from licensing_models import PlatformLicense, LicensingAgreement

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Database setup
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Authentication setup
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()

# User Model (local copy to avoid circular imports)
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str = ""
    is_admin: bool = False
    role: str = "user"

# Authentication functions (local copies)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

async def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.role not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

router = APIRouter(prefix="/licensing", tags=["Licensing System"])
licensing_service = LicensingService()

# Define platforms configuration locally to avoid circular import
DISTRIBUTION_PLATFORMS = {
    "spotify": {"type": "streaming", "name": "Spotify"},
    "apple_music": {"type": "streaming", "name": "Apple Music"},
    "youtube": {"type": "social_media", "name": "YouTube"},
    "instagram": {"type": "social_media", "name": "Instagram"},
    "tiktok": {"type": "social_media", "name": "TikTok"},
    # Add more platforms as needed - this is a simplified version
}

@router.post("/initialize-all-platforms")
async def initialize_all_platform_licenses(current_user: User = Depends(require_admin)):
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
                platform_id, license_id, current_user.email
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

@router.get("/dashboard")
async def get_licensing_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive licensing dashboard"""
    try:
        dashboard_data = licensing_service.get_licensing_dashboard()
        
        return {
            "licensing_overview": {
                "total_platforms_licensed": dashboard_data.get("total_platforms", 0),
                "active_licenses": dashboard_data.get("active_licenses", 0),
                "pending_licenses": dashboard_data.get("pending_licenses", 0),
                "expired_licenses": dashboard_data.get("expired_licenses", 0),
                "compliance_rate": dashboard_data.get("compliance_rate", 0)
            },
            "business_info": {
                "business_entity": "Big Mann Entertainment",
                "business_owner": "John LeGerron Spivey",
                "license_holder": "John LeGerron Spivey",
                "business_type": "Entertainment/Media Distribution",
                "established": "2020"
            },
            "financial_summary": {
                "total_licensing_fees": dashboard_data.get("total_fees", 0),
                "monthly_licensing_costs": dashboard_data.get("monthly_costs", 0),
                "annual_licensing_budget": dashboard_data.get("annual_budget", 0),
                "cost_per_platform": dashboard_data.get("cost_per_platform", 0)
            },
            "platform_categories": dashboard_data.get("platform_categories", {}),
            "recent_activity": dashboard_data.get("recent_activity", []),
            "alerts": dashboard_data.get("alerts", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve licensing dashboard: {str(e)}")

@router.get("/platforms")
async def get_platform_licenses(
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get platform licenses with optional filtering"""
    try:
        licenses = licensing_service.get_platform_licenses(
            status=status, 
            category=category, 
            limit=limit, 
            offset=offset
        )
        
        return {
            "total_licenses": len(licenses),
            "licenses": licenses,
            "filters": {
                "status": status,
                "category": category,
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve platform licenses: {str(e)}")

@router.get("/platforms/{platform_id}")
async def get_platform_license_details(
    platform_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information for a specific platform license"""
    try:
        license_details = licensing_service.get_platform_license_details(platform_id)
        
        if not license_details:
            raise HTTPException(status_code=404, detail="Platform license not found")
        
        return {
            "platform_license": license_details,
            "compliance_status": licensing_service.check_platform_compliance(platform_id),
            "usage_metrics": licensing_service.get_platform_usage_metrics(platform_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve platform license details: {str(e)}")

@router.post("/platforms/{platform_id}/activate")
async def activate_platform_license(
    platform_id: str,
    current_user: User = Depends(require_admin)
):
    """Activate a platform license (admin only)"""
    try:
        activation_id = licensing_service.activate_platform_license(
            platform_id, 
            platform_id,  # Using platform_id as license_id for simplicity
            current_user.email
        )
        
        return {
            "message": f"Platform {platform_id} license activated successfully",
            "activation_id": activation_id,
            "platform_id": platform_id,
            "activated_by": current_user.email,
            "activation_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate platform license: {str(e)}")

@router.post("/platforms/{platform_id}/deactivate")
async def deactivate_platform_license(
    platform_id: str,
    current_user: User = Depends(require_admin)
):
    """Deactivate a platform license (admin only)"""
    try:
        deactivation_id = licensing_service.deactivate_platform_license(
            platform_id,
            current_user.email
        )
        
        return {
            "message": f"Platform {platform_id} license deactivated successfully",
            "deactivation_id": deactivation_id,
            "platform_id": platform_id,
            "deactivated_by": current_user.email,
            "deactivation_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate platform license: {str(e)}")

@router.post("/compliance-check/{platform_id}")
async def check_platform_compliance(
    platform_id: str,
    current_user: User = Depends(get_current_user)
):
    """Check compliance status for a specific platform"""
    try:
        compliance_data = licensing_service.check_platform_compliance(platform_id)
        
        return {
            "platform_id": platform_id,
            "overall_compliance": compliance_data.get("compliant", False),
            "compliance_score": compliance_data.get("score", 0),
            "compliance_details": compliance_data.get("details", {}),
            "recommendations": compliance_data.get("recommendations", []),
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check platform compliance: {str(e)}")

@router.get("/status")
async def get_licensing_status(current_user: User = Depends(get_current_user)):
    """Get overall licensing system status and health"""
    try:
        status_data = licensing_service.get_licensing_status()
        
        return {
            "business_entity": "Big Mann Entertainment",
            "license_owner": "John LeGerron Spivey",
            "licensing_health_score": status_data.get("health_score", 0),
            "total_platforms": status_data.get("total_platforms", 0),
            "active_licenses": status_data.get("active_licenses", 0),
            "compliance_rate": status_data.get("compliance_rate", 0),
            "last_updated": datetime.utcnow().isoformat(),
            "system_status": "operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve licensing status: {str(e)}")

@router.get("/agreements")
async def get_licensing_agreements(
    agreement_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get licensing agreements with optional filtering"""
    try:
        agreements = licensing_service.get_licensing_agreements(
            agreement_type=agreement_type,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "total_agreements": len(agreements),
            "agreements": agreements,
            "filters": {
                "agreement_type": agreement_type,
                "status": status,
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve licensing agreements: {str(e)}")

@router.post("/usage/{platform_id}")
async def update_platform_usage(
    platform_id: str,
    usage_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update usage metrics for a platform"""
    try:
        updated_usage = licensing_service.update_platform_usage(platform_id, usage_data)
        
        return {
            "message": f"Usage metrics updated for platform {platform_id}",
            "platform_id": platform_id,
            "usage_data": updated_usage,
            "updated_by": current_user.email,
            "update_date": datetime.utcnow().isoformat(),
            "check_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update platform usage: {str(e)}")

@router.get("/statutory-rates")
async def get_statutory_rates(
    royalty_type: Optional[str] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Get current statutory rates for music licensing"""
    try:
        rates = licensing_service.get_statutory_rates(royalty_type=royalty_type, active_only=active_only)
        
        return {
            "statutory_rates": rates,
            "total_rates": len(rates),
            "rate_source": "CRB (Copyright Royalty Board)",
            "effective_year": "2025",
            "business_entity": "Big Mann Entertainment",
            "filters": {
                "royalty_type": royalty_type,
                "active_only": active_only
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statutory rates: {str(e)}")

@router.post("/daily-compensation")
async def calculate_daily_compensation(
    compensation_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Calculate daily compensation for all active platforms using statutory rates"""
    try:
        # Parse compensation date if provided
        comp_date = None
        if compensation_date:
            comp_date = datetime.fromisoformat(compensation_date.replace('Z', '+00:00'))
        
        compensation_data = licensing_service.calculate_daily_compensation(comp_date)
        
        return {
            "message": "Daily compensation calculated successfully",
            "compensation_data": compensation_data,
            "calculation_type": "statutory_rates_based",
            "business_entity": "Big Mann Entertainment",
            "calculated_by": current_user.email,
            "calculation_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate daily compensation: {str(e)}")

@router.post("/daily-payouts")
async def process_daily_payouts(
    minimum_amount: float = 1.00,
    current_user: User = Depends(require_admin)
):
    """Process daily compensation payouts (admin only)"""
    try:
        from decimal import Decimal
        min_amount = Decimal(str(minimum_amount))
        
        payout_data = licensing_service.process_daily_payouts(minimum_amount=min_amount)
        
        return {
            "message": "Daily payouts processed successfully",
            "payout_data": payout_data,
            "processing_type": "automated_statutory_payouts",
            "business_entity": "Big Mann Entertainment",
            "processed_by": current_user.email,
            "processing_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process daily payouts: {str(e)}")

@router.get("/compensation-dashboard")
async def get_compensation_dashboard(
    period_days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive compensation and payout dashboard"""
    try:
        dashboard_data = licensing_service.get_compensation_dashboard(period_days=period_days)
        
        return {
            "compensation_dashboard": dashboard_data,
            "dashboard_type": "statutory_rates_compensation",
            "business_entity": "Big Mann Entertainment",
            "business_owner": "John LeGerron Spivey",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compensation dashboard: {str(e)}")

@router.get("/compensation-history")
async def get_compensation_history(
    platform_id: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get compensation history with optional platform filtering"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = {
            "compensation_date": {"$gte": start_date, "$lte": end_date}
        }
        if platform_id:
            query["platform_id"] = platform_id
        
        compensations = list(licensing_service.daily_compensations.find(query).sort("compensation_date", -1).limit(limit))
        
        # Convert ObjectId and Decimal for JSON serialization
        for comp in compensations:
            comp["_id"] = str(comp["_id"])
            for field in ["gross_revenue", "net_revenue", "total_compensation", "artist_compensation", 
                         "songwriter_compensation", "publisher_compensation", "big_mann_commission"]:
                if field in comp:
                    comp[field] = float(comp[field])
        
        return {
            "compensation_history": compensations,
            "total_records": len(compensations),
            "period_days": days,
            "platform_filter": platform_id,
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compensation history: {str(e)}")

@router.get("/payout-history")
async def get_payout_history(
    recipient_type: Optional[str] = None,
    days: int = 30,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get payout history with optional recipient filtering"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = {
            "payout_date": {"$gte": start_date, "$lte": end_date}
        }
        if recipient_type:
            query["recipient_type"] = recipient_type
        
        payouts = list(licensing_service.compensation_payouts.find(query).sort("payout_date", -1).limit(limit))
        
        # Convert ObjectId and Decimal for JSON serialization
        for payout in payouts:
            payout["_id"] = str(payout["_id"])
            for field in ["total_amount", "tax_withholding", "net_payout"]:
                if field in payout:
                    payout[field] = float(payout[field])
        
        return {
            "payout_history": payouts,
            "total_records": len(payouts),
            "period_days": days,
            "recipient_filter": recipient_type,
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payout history: {str(e)}")

# Export the router
licensing_router = router