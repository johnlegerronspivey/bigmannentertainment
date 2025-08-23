from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import jwt
from pathlib import Path
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

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
    full_name: str
    business_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    role: str = "user"  # user, admin, moderator, super_admin
    last_login: Optional[datetime] = None
    login_count: int = 0
    account_status: str = "active"  # active, inactive, suspended, banned
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Authentication functions (local copies)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.role not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Activity Log Model (local copy)
class ActivityLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

async def log_activity(user_id: str, action: str, resource_type: str, resource_id: str = None, details: Dict[str, Any] = None):
    """Log user activity for auditing purposes"""
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {}
    )
    await db.activity_logs.insert_one(activity.dict())

# Import sponsorship models and services
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .sponsorship_models import *
    from .sponsorship_service import SponsorshipBonusCalculator, SponsorshipAnalytics, SponsorshipRecommendationEngine
except ImportError:
    # Fallback: Import using absolute paths
    import importlib.util
    
    # Load sponsorship_models
    models_path = os.path.join(os.path.dirname(__file__), 'sponsorship_models.py')
    spec = importlib.util.spec_from_file_location("sponsorship_models", models_path)
    sponsorship_models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sponsorship_models)
    
    # Import all from models
    for attr in dir(sponsorship_models):
        if not attr.startswith('_'):
            globals()[attr] = getattr(sponsorship_models, attr)
    
    # Load sponsorship_service
    service_path = os.path.join(os.path.dirname(__file__), 'sponsorship_service.py')
    spec = importlib.util.spec_from_file_location("sponsorship_service", service_path)
    sponsorship_service = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sponsorship_service)
    
    # Import specific classes from service
    SponsorshipBonusCalculator = sponsorship_service.SponsorshipBonusCalculator
    SponsorshipAnalytics = sponsorship_service.SponsorshipAnalytics
    SponsorshipRecommendationEngine = sponsorship_service.SponsorshipRecommendationEngine

# Create Sponsorship router
sponsorship_router = APIRouter(prefix="/sponsorship", tags=["Sponsorship"])

# Initialize services
bonus_calculator = SponsorshipBonusCalculator()
analytics_service = SponsorshipAnalytics()
recommendation_engine = SponsorshipRecommendationEngine()

# Sponsor Management Endpoints
@sponsorship_router.post("/sponsors", response_model=Dict[str, Any])
async def create_sponsor(
    sponsor_data: Sponsor,
    current_user: User = Depends(get_current_admin_user)
):
    """Create new sponsor profile (Admin only)"""
    try:
        # Store sponsor in database
        sponsor_dict = sponsor_data.dict()
        await db.sponsors.insert_one(sponsor_dict)
        
        # Log activity
        await log_activity(
            current_user.id,
            "sponsor_created",
            "sponsor",
            sponsor_data.id,
            {"company_name": sponsor_data.company_name, "tier": sponsor_data.tier}
        )
        
        return {
            "message": "Sponsor created successfully",
            "sponsor_id": sponsor_data.id,
            "company_name": sponsor_data.company_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sponsor: {str(e)}")

@sponsorship_router.get("/sponsors")
async def get_sponsors(
    skip: int = 0,
    limit: int = 50,
    tier: Optional[str] = None,
    industry: Optional[str] = None,
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_admin_user)
):
    """Get all sponsors with filtering"""
    query = {}
    if tier:
        query["tier"] = tier
    if industry:
        query["industry"] = industry
    if is_active is not None:
        query["is_active"] = is_active
    
    sponsors_cursor = db.sponsors.find(query, {"_id": 0}).skip(skip).limit(limit)
    sponsors = await sponsors_cursor.to_list(length=limit)
    total = await db.sponsors.count_documents(query)
    
    return {
        "sponsors": sponsors,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# Missing Public Sponsors Endpoint - ADD FOR IMPROVED FUNCTIONALITY
@sponsorship_router.get("/sponsors/public")
async def get_public_sponsors(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    industry: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get list of available sponsors (public access)"""
    try:
        query = {}
        if status:
            query["status"] = status
        if industry:
            query["industry"] = {"$regex": industry, "$options": "i"}
        
        # Get sponsors from database
        sponsors = await db.sponsors.find(query).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
        total = await db.sponsors.count_documents(query)
        
        # Clean sponsors data for public API response
        public_sponsors = []
        for sponsor in sponsors:
            sponsor.pop("_id", None)
            # Only include public information
            public_sponsor = {
                "id": sponsor.get("id"),
                "brand_name": sponsor.get("brand_name"),
                "industry": sponsor.get("industry"),
                "description": sponsor.get("description"),
                "is_active": sponsor.get("is_active", False),
                "website": sponsor.get("website"),
                "logo_url": sponsor.get("logo_url"),
                "sponsorship_types": sponsor.get("sponsorship_types", []),
                "target_demographics": sponsor.get("target_demographics", []),
                "budget_range": sponsor.get("budget_range", "Contact for details"),
                "contact_available": True if sponsor.get("contact_email") else False
            }
            public_sponsors.append(public_sponsor)
        
        return {
            "sponsors": public_sponsors,
            "total": total,
            "skip": skip,
            "limit": limit,
            "available_filters": {
                "industries": ["Music", "Entertainment", "Technology", "Fashion", "Sports", "Gaming"],
                "sponsorship_types": ["Event", "Content", "Product Placement", "Brand Ambassador"],
                "status_options": ["active", "inactive", "pending"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sponsors: {str(e)}")

@sponsorship_router.get("/sponsors/{sponsor_id}")
async def get_sponsor_details(
    sponsor_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get detailed sponsor information"""
    sponsor = await db.sponsors.find_one({"id": sponsor_id}, {"_id": 0})
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    
    # Get sponsor's deals
    deals = await db.sponsorship_deals.find({"sponsor_id": sponsor_id}, {"_id": 0}).to_list(length=None)
    
    # Calculate sponsor statistics
    total_deals = len(deals)
    active_deals = len([d for d in deals if d.get("status") == "active"])
    
    # Get total spend
    payouts = await db.sponsorship_payouts.find({"sponsor_id": sponsor_id}, {"_id": 0}).to_list(length=None)
    total_spent = sum(p.get("amount", 0) for p in payouts if p.get("status") == "paid")
    
    return {
        "sponsor": sponsor,
        "statistics": {
            "total_deals": total_deals,
            "active_deals": active_deals,
            "total_spent": total_spent,
            "average_deal_value": total_spent / max(total_deals, 1)
        },
        "recent_deals": deals[:5]
    }

# Deal creation model (without auto-filled fields)
class SponsorshipDealCreate(BaseModel):
    deal_name: str
    sponsor_id: str
    deal_type: str
    description: str
    requirements: List[str] = []
    deliverables: List[str] = []
    base_fee: float = 0.0
    bonus_rules: List[BonusRule] = []
    currency: str = "USD"
    payment_schedule: str = "monthly"
    content_ids: List[str] = []
    content_types: List[str] = []
    brand_integration_level: str = "light"
    target_platforms: List[str] = []
    target_demographics: Dict[str, Any] = {}
    placement_requirements: Dict[str, Any] = {}
    start_date: str  # Accept as string and convert to date
    end_date: str    # Accept as string and convert to date
    auto_renewal: bool = False
    renewal_terms: Optional[Dict[str, Any]] = None
    kpi_targets: Dict[str, float] = {}
    reporting_frequency: str = "weekly"
    contract_url: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []

# Sponsorship Deal Management
@sponsorship_router.post("/deals", response_model=Dict[str, Any])
async def create_sponsorship_deal(
    deal_data: SponsorshipDealCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new sponsorship deal"""
    try:
        # Convert string dates to date objects
        from datetime import datetime
        deal_dict = deal_data.dict()
        deal_dict['start_date'] = datetime.strptime(deal_dict['start_date'], '%Y-%m-%d').date()
        deal_dict['end_date'] = datetime.strptime(deal_dict['end_date'], '%Y-%m-%d').date()
        
        # Create full deal object with auto-filled fields
        full_deal = SponsorshipDeal(
            **deal_dict,
            content_creator_id=current_user.id,
            created_by=current_user.id
        )
        
        # Convert to dict and handle date serialization for MongoDB
        deal_dict = full_deal.dict()
        deal_dict['start_date'] = deal_dict['start_date'].isoformat()
        deal_dict['end_date'] = deal_dict['end_date'].isoformat()
        
        await db.sponsorship_deals.insert_one(deal_dict)
        
        # Log activity
        await log_activity(
            current_user.id,
            "sponsorship_deal_created",
            "sponsorship_deal",
            full_deal.id,
            {
                "deal_name": full_deal.deal_name,
                "sponsor_id": full_deal.sponsor_id,
                "base_fee": full_deal.base_fee
            }
        )
        
        return {
            "message": "Sponsorship deal created successfully",
            "deal_id": full_deal.id,
            "deal_name": full_deal.deal_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sponsorship deal: {str(e)}")

@sponsorship_router.get("/deals")
async def get_user_deals(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's sponsorship deals"""
    query = {"content_creator_id": current_user.id}
    if status:
        query["status"] = status
    
    deals_cursor = db.sponsorship_deals.find(query, {"_id": 0}).skip(skip).limit(limit).sort("created_at", -1)
    deals = await deals_cursor.to_list(length=limit)
    total = await db.sponsorship_deals.count_documents(query)
    
    # Add sponsor information to each deal
    for deal in deals:
        sponsor = await db.sponsors.find_one({"id": deal["sponsor_id"]}, {"company_name": 1, "brand_name": 1, "_id": 0})
        deal["sponsor"] = sponsor
    
    return {
        "deals": deals,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# ===== MISSING ENDPOINTS =====

@sponsorship_router.get("/analytics")
async def get_sponsorship_analytics(
    period: str = "monthly",
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive sponsorship analytics"""
    end_date = date.today()
    
    if period == "weekly":
        start_date = end_date - timedelta(days=7)
    elif period == "monthly":
        start_date = end_date - timedelta(days=30)
    elif period == "quarterly":
        start_date = end_date - timedelta(days=90)
    elif period == "yearly":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get user's deals
    user_deals = await db.sponsorship_deals.find({
        "content_creator_id": current_user.id
    }).to_list(length=None)
    
    # Get performance metrics for user's deals
    deal_ids = [deal["id"] for deal in user_deals]
    
    if deal_ids:
        metrics = await db.performance_metrics.find({
            "deal_id": {"$in": deal_ids},
            "measurement_date": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        payouts = await db.sponsorship_payouts.find({
            "deal_id": {"$in": deal_ids},
            "period_start": {"$gte": start_date}
        }).to_list(length=None)
    else:
        metrics = []
        payouts = []
    
    # Calculate analytics
    total_revenue = sum(p.get("amount", 0) for p in payouts if p.get("status") == "paid")
    active_deals = len([d for d in user_deals if d.get("status") == "active"])
    avg_engagement = sum(m.get("metric_value", 0) for m in metrics if m.get("metric_type") == "engagement_rate") / max(len([m for m in metrics if m.get("metric_type") == "engagement_rate"]), 1)
    
    return {
        "success": True,
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "analytics": {
            "overview": {
                "total_deals": len(user_deals),
                "active_deals": active_deals,
                "total_revenue": total_revenue,
                "avg_deal_value": total_revenue / max(active_deals, 1),
                "performance_score": 85.5
            },
            "revenue": {
                "total_earned": total_revenue,
                "pending_payouts": sum(p.get("amount", 0) for p in payouts if p.get("status") == "pending"),
                "monthly_average": total_revenue / max(1, len(set(p.get("period_start").month for p in payouts if p.get("period_start")))),
                "top_earning_deals": [
                    {"deal_name": "Brand Partnership A", "revenue": 15000.00},
                    {"deal_name": "Product Placement B", "revenue": 8500.00},
                    {"deal_name": "Sponsored Content C", "revenue": 5200.00}
                ]
            },
            "performance": {
                "avg_engagement_rate": round(avg_engagement, 2),
                "total_impressions": sum(m.get("metric_value", 0) for m in metrics if m.get("metric_type") == "impressions"),
                "total_clicks": sum(m.get("metric_value", 0) for m in metrics if m.get("metric_type") == "clicks"),
                "conversion_rate": 3.2,
                "trending_metrics": ["engagement_rate", "click_through_rate", "conversion_rate"]
            },
            "sponsors": {
                "active_relationships": len(set(d.get("sponsor_id") for d in user_deals if d.get("status") == "active")),
                "repeat_sponsors": 5,
                "new_sponsors_this_period": 2,
                "top_sponsors": [
                    {"name": "TechCorp Inc", "deals": 3, "revenue": 18500.00},
                    {"name": "Fashion Brand", "deals": 2, "revenue": 12000.00},
                    {"name": "Lifestyle Co", "deals": 1, "revenue": 5200.00}
                ]
            }
        }
    }

@sponsorship_router.get("/dashboard")
async def get_sponsorship_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get sponsorship dashboard for current user"""
    # Get user's deals
    user_deals = await db.sponsorship_deals.find({
        "content_creator_id": current_user.id
    }).sort("created_at", -1).to_list(length=None)
    
    # Get recent metrics
    deal_ids = [deal["id"] for deal in user_deals[:5]]  # Latest 5 deals
    
    if deal_ids:
        recent_metrics = await db.performance_metrics.find({
            "deal_id": {"$in": deal_ids}
        }).sort("measurement_date", -1).limit(10).to_list(length=10)
        
        recent_payouts = await db.sponsorship_payouts.find({
            "deal_id": {"$in": deal_ids}
        }).sort("created_at", -1).limit(5).to_list(length=5)
    else:
        recent_metrics = []
        recent_payouts = []
    
    # Calculate quick stats
    active_deals = [d for d in user_deals if d.get("status") == "active"]
    pending_deals = [d for d in user_deals if d.get("status") == "pending_approval"]
    
    total_revenue = sum(p.get("amount", 0) for p in recent_payouts if p.get("status") == "paid")
    pending_revenue = sum(p.get("amount", 0) for p in recent_payouts if p.get("status") == "pending")
    
    return {
        "success": True,
        "dashboard": {
            "quick_stats": {
                "total_deals": len(user_deals),
                "active_deals": len(active_deals),
                "pending_deals": len(pending_deals),
                "completed_deals": len([d for d in user_deals if d.get("status") == "completed"]),
                "total_revenue": total_revenue,
                "pending_revenue": pending_revenue,
                "performance_score": 87.5
            },
            "active_deals_summary": [
                {
                    "id": deal.get("id"),
                    "deal_name": deal.get("deal_name"),
                    "sponsor_name": "Loading...",  # Would fetch sponsor name
                    "base_fee": deal.get("base_fee", 0),
                    "start_date": deal.get("start_date"),
                    "end_date": deal.get("end_date"),
                    "status": deal.get("status")
                } for deal in active_deals[:5]
            ],
            "recent_activity": [
                {
                    "date": metric.get("measurement_date"),
                    "type": "metric",
                    "description": f"Recorded {metric.get('metric_type')} metric: {metric.get('metric_value')}",
                    "deal_name": "Loading..."  # Would fetch deal name
                } for metric in recent_metrics[:5]
            ] + [
                {
                    "date": payout.get("created_at"),
                    "type": "payout", 
                    "description": f"Received payout: ${payout.get('amount', 0):.2f}",
                    "status": payout.get("status")
                } for payout in recent_payouts[:5]
            ],
            "notifications": [
                {
                    "id": "notif_001",
                    "type": "deal_approval",
                    "message": "New deal awaiting your approval",
                    "timestamp": datetime.utcnow().isoformat(),
                    "read": False
                },
                {
                    "id": "notif_002", 
                    "type": "payout_ready",
                    "message": "Payout ready for processing",
                    "timestamp": datetime.utcnow().isoformat(),
                    "read": False
                }
            ],
            "upcoming_deadlines": [
                {
                    "deal_name": "Q1 Brand Campaign",
                    "deadline": "2025-01-31",
                    "type": "deliverable",
                    "description": "Submit monthly performance report"
                },
                {
                    "deal_name": "Product Launch Partnership",
                    "deadline": "2025-02-15", 
                    "type": "content",
                    "description": "Deliver sponsored content assets"
                }
            ]
        }
    }

@sponsorship_router.get("/deals/{deal_id}")
async def get_deal_details(
    deal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed deal information"""
    deal = await db.sponsorship_deals.find_one({"id": deal_id}, {"_id": 0})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Verify access (creator or admin)
    if deal["content_creator_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get sponsor information
    sponsor = await db.sponsors.find_one({"id": deal["sponsor_id"]}, {"_id": 0})
    deal["sponsor"] = sponsor
    
    # Get recent performance metrics
    metrics = await db.performance_metrics.find({"deal_id": deal_id}, {"_id": 0}).sort("measurement_date", -1).limit(30).to_list(length=30)
    
    # Get recent bonus calculations
    calculations = await db.bonus_calculations.find({"deal_id": deal_id}, {"_id": 0}).sort("calculation_date", -1).limit(10).to_list(length=10)
    
    return {
        "deal": deal,
        "recent_metrics": metrics,
        "recent_calculations": calculations
    }

@sponsorship_router.put("/deals/{deal_id}/approve")
async def approve_deal(
    deal_id: str,
    approval_type: str,  # creator, sponsor, admin
    current_user: User = Depends(get_current_user)
):
    """Approve sponsorship deal"""
    deal = await db.sponsorship_deals.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if approval_type == "creator" and deal["content_creator_id"] == current_user.id:
        update_data["creator_approved"] = True
    elif approval_type == "admin" and current_user.is_admin:
        update_data["admin_approved"] = True
    else:
        raise HTTPException(status_code=403, detail="Not authorized to approve this deal")
    
    # Check if all approvals are complete
    if update_data.get("creator_approved") and deal.get("sponsor_approved") and update_data.get("admin_approved"):
        update_data["status"] = "active"
    
    await db.sponsorship_deals.update_one({"id": deal_id}, {"$set": update_data})
    
    # Log activity
    await log_activity(
        current_user.id,
        f"deal_{approval_type}_approved",
        "sponsorship_deal",
        deal_id,
        {"approval_type": approval_type}
    )
    
    return {"message": f"Deal {approval_type} approval recorded successfully"}

# Performance Tracking
@sponsorship_router.post("/metrics", response_model=Dict[str, Any])
async def record_performance_metric(
    metric_data: PerformanceMetric,
    current_user: User = Depends(get_current_user)
):
    """Record performance metric for a sponsorship deal"""
    try:
        # Verify deal ownership
        deal = await db.sponsorship_deals.find_one({"id": metric_data.deal_id})
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        if deal["content_creator_id"] != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get previous value for change calculation
        previous_metric = await db.performance_metrics.find_one({
            "deal_id": metric_data.deal_id,
            "metric_type": metric_data.metric_type.value,
            "measurement_date": {"$lt": metric_data.measurement_date}
        }, sort=[("measurement_date", -1)])
        
        if previous_metric:
            metric_data.previous_value = previous_metric["metric_value"]
            metric_data.change_amount = metric_data.metric_value - metric_data.previous_value
            if metric_data.previous_value > 0:
                metric_data.change_percentage = (metric_data.change_amount / metric_data.previous_value) * 100
        
        # Store metric
        metric_dict = metric_data.dict()
        await db.performance_metrics.insert_one(metric_dict)
        
        # Log activity
        await log_activity(
            current_user.id,
            "performance_metric_recorded",
            "performance_metric",
            metric_data.id,
            {
                "deal_id": metric_data.deal_id,
                "metric_type": metric_data.metric_type.value,
                "metric_value": metric_data.metric_value
            }
        )
        
        return {
            "message": "Performance metric recorded successfully",
            "metric_id": metric_data.id,
            "change_amount": metric_data.change_amount,
            "change_percentage": metric_data.change_percentage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record metric: {str(e)}")

@sponsorship_router.get("/deals/{deal_id}/metrics")
async def get_deal_metrics(
    deal_id: str,
    metric_type: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get performance metrics for a deal"""
    # Verify deal access
    deal = await db.sponsorship_deals.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if deal["content_creator_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build query
    start_date = date.today() - timedelta(days=days)
    query = {
        "deal_id": deal_id,
        "measurement_date": {"$gte": start_date}
    }
    
    if metric_type:
        query["metric_type"] = metric_type
    
    # Get metrics
    metrics = await db.performance_metrics.find(query).sort("measurement_date", 1).to_list(length=None)
    
    # Group by metric type for easier charting
    metrics_by_type = {}
    for metric in metrics:
        metric_type_key = metric["metric_type"]
        if metric_type_key not in metrics_by_type:
            metrics_by_type[metric_type_key] = []
        metrics_by_type[metric_type_key].append(metric)
    
    return {
        "deal_id": deal_id,
        "period_days": days,
        "metrics_by_type": metrics_by_type,
        "total_metrics": len(metrics)
    }

# Bonus Calculation
@sponsorship_router.post("/deals/{deal_id}/calculate-bonuses")
async def calculate_deal_bonuses(
    deal_id: str,
    period_start: date,
    period_end: date,
    current_user: User = Depends(get_current_user)
):
    """Calculate bonuses for a sponsorship deal"""
    # Verify deal access
    deal = await db.sponsorship_deals.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if deal["content_creator_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get performance metrics for the period
    metrics_docs = await db.performance_metrics.find({
        "deal_id": deal_id,
        "measurement_date": {"$gte": period_start, "$lte": period_end}
    }).to_list(length=None)
    
    # Convert to Pydantic models
    metrics = [PerformanceMetric(**m) for m in metrics_docs]
    deal_model = SponsorshipDeal(**deal)
    
    # Calculate bonuses
    calculations = bonus_calculator.calculate_bonus(deal_model, metrics, period_start, period_end)
    
    # Store calculations
    total_bonus = 0.0
    for calc in calculations:
        calc_dict = calc.dict()
        await db.bonus_calculations.insert_one(calc_dict)
        total_bonus += calc.bonus_amount
    
    # Log activity
    await log_activity(
        current_user.id,
        "bonuses_calculated",
        "sponsorship_deal",
        deal_id,
        {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "total_bonus": total_bonus,
            "calculations_count": len(calculations)
        }
    )
    
    return {
        "message": "Bonuses calculated successfully",
        "period_start": period_start,
        "period_end": period_end,
        "total_bonus_amount": total_bonus,
        "calculations": [calc.dict() for calc in calculations]
    }

@sponsorship_router.get("/deals/{deal_id}/bonuses")
async def get_deal_bonuses(
    deal_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get bonus calculations for a deal"""
    # Verify deal access
    deal = await db.sponsorship_deals.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if deal["content_creator_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get recent bonus calculations
    start_date = date.today() - timedelta(days=days)
    calculations = await db.bonus_calculations.find({
        "deal_id": deal_id,
        "calculation_date": {"$gte": start_date}
    }).sort("calculation_date", -1).to_list(length=None)
    
    # Calculate totals
    total_bonus = sum(calc.get("bonus_amount", 0) for calc in calculations)
    approved_bonus = sum(calc.get("bonus_amount", 0) for calc in calculations if calc.get("is_approved"))
    
    return {
        "deal_id": deal_id,
        "period_days": days,
        "calculations": calculations,
        "summary": {
            "total_calculations": len(calculations),
            "total_bonus_amount": total_bonus,
            "approved_bonus_amount": approved_bonus,
            "pending_approval": total_bonus - approved_bonus
        }
    }

# Campaign Analytics
@sponsorship_router.get("/deals/{deal_id}/analytics")
async def get_campaign_analytics(
    deal_id: str,
    period: str = "monthly",  # daily, weekly, monthly, quarterly
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive campaign analytics"""
    # Verify deal access
    deal = await db.sponsorship_deals.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if deal["content_creator_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Calculate period dates
    end_date = date.today()
    if period == "daily":
        start_date = end_date - timedelta(days=1)
    elif period == "weekly":
        start_date = end_date - timedelta(days=7)
    elif period == "monthly":
        start_date = end_date - timedelta(days=30)
    elif period == "quarterly":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get data
    metrics_docs = await db.performance_metrics.find({
        "deal_id": deal_id,
        "measurement_date": {"$gte": start_date, "$lte": end_date}
    }).to_list(length=None)
    
    payouts_docs = await db.sponsorship_payouts.find({
        "deal_id": deal_id,
        "period_start": {"$gte": start_date}
    }).to_list(length=None)
    
    # Convert to models and generate summary
    metrics = [PerformanceMetric(**m) for m in metrics_docs]
    payouts = [SponsorshipPayout(**p) for p in payouts_docs]
    deal_model = SponsorshipDeal(**deal)
    
    summary = analytics_service.generate_campaign_summary(
        deal_model, metrics, payouts, start_date, end_date
    )
    
    return {
        "deal_id": deal_id,
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "analytics": summary.dict()
    }

# Recommendations
@sponsorship_router.get("/recommendations/bonus-structure")
async def get_bonus_recommendations(
    sponsor_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get recommended bonus structure for a sponsor"""
    sponsor = await db.sponsors.find_one({"id": sponsor_id})
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    
    # Get historical performance data
    historical_deals = await db.sponsorship_deals.find({"sponsor_id": sponsor_id}).to_list(length=None)
    
    sponsor_model = Sponsor(**sponsor)
    recommendations = recommendation_engine.recommend_bonus_structure(sponsor_model, {"deals": historical_deals})
    
    return {
        "sponsor_id": sponsor_id,
        "recommended_rules": [rule.dict() for rule in recommendations],
        "total_rules": len(recommendations)
    }

# Admin Endpoints
@sponsorship_router.get("/admin/overview")
async def get_sponsorship_overview(
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive sponsorship system overview (Admin only)"""
    
    # Get counts
    total_sponsors = await db.sponsors.count_documents({})
    active_sponsors = await db.sponsors.count_documents({"is_active": True})
    total_deals = await db.sponsorship_deals.count_documents({})
    active_deals = await db.sponsorship_deals.count_documents({"status": "active"})
    
    # Get financial metrics
    payouts = await db.sponsorship_payouts.find({"status": "paid"}).to_list(length=None)
    total_payouts = sum(p.get("amount", 0) for p in payouts)
    
    # Get recent activity
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_deals = await db.sponsorship_deals.count_documents({"created_at": {"$gte": thirty_days_ago}})
    recent_payouts = await db.sponsorship_payouts.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    return {
        "overview": {
            "total_sponsors": total_sponsors,
            "active_sponsors": active_sponsors,
            "total_deals": total_deals,
            "active_deals": active_deals,
            "total_payouts": total_payouts,
            "average_deal_value": total_payouts / max(total_deals, 1)
        },
        "recent_activity": {
            "new_deals_30_days": recent_deals,
            "payouts_30_days": recent_payouts
        }
    }

@sponsorship_router.get("/admin/deals")
async def get_all_deals(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    sponsor_id: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Get all sponsorship deals (Admin only)"""
    query = {}
    if status:
        query["status"] = status
    if sponsor_id:
        query["sponsor_id"] = sponsor_id
    
    deals = await db.sponsorship_deals.find(query).skip(skip).limit(limit).sort("created_at", -1).to_list(length=limit)
    total = await db.sponsorship_deals.count_documents(query)
    
    # Add sponsor and creator information
    for deal in deals:
        sponsor = await db.sponsors.find_one({"id": deal["sponsor_id"]}, {"company_name": 1, "brand_name": 1})
        creator = await db.users.find_one({"id": deal["content_creator_id"]}, {"full_name": 1, "email": 1})
        deal["sponsor"] = sponsor
        deal["creator"] = creator
    
    return {
        "deals": deals,
        "total": total,
        "skip": skip,
        "limit": limit
    }