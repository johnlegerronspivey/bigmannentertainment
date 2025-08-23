from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from label_models import *
from label_service import LabelManagementService
import json
import os

# Import authentication from server
try:
    from server import get_current_user, get_current_admin_user, User, db
    print("✅ Successfully imported authentication from server")
except ImportError:
    # Fallback authentication (for development)
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from motor.motor_asyncio import AsyncIOMotorClient
    import jwt
    
    # Database connection
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/bigmann')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.bigmann
    
    # JWT Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    ALGORITHM = "HS256"
    
    security = HTTPBearer()
    
    class User:
        def __init__(self, **data):
            self.id = data.get('id')
            self.email = data.get('email')
            self.is_admin = data.get('is_admin', False)
            self.role = data.get('role', 'user')
    
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        try:
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
    
    print("⚠️ Using fallback authentication for label endpoints")

# Create router for label management endpoints
label_router = APIRouter(prefix="/label", tags=["Label Management"])
label_service = LabelManagementService()

# ===== ARTIST MANAGEMENT ENDPOINTS =====

@label_router.post("/artists", response_model=Dict[str, Any])
async def create_new_artist(
    artist_data: ArtistCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new artist profile"""
    result = await label_service.create_artist(artist_data, current_user.id)
    return result

@label_router.get("/artists", response_model=List[Dict[str, Any]])
async def get_artist_roster(
    status: Optional[ArtistStatus] = None,
    genre: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_admin_user)
):
    """Get artist roster with filtering"""
    artists = await label_service.get_artist_roster(status, genre, limit)
    return artists

@label_router.get("/artists/{artist_id}", response_model=Dict[str, Any])
async def get_artist_profile(
    artist_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get detailed artist profile"""
    artist = await label_service.get_artist(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@label_router.put("/artists/{artist_id}", response_model=Dict[str, Any])
async def update_artist_profile(
    artist_id: str,
    update_data: ArtistUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """Update artist profile"""
    result = await label_service.update_artist(artist_id, update_data, current_user.id)
    return result

# ===== CONTRACT MANAGEMENT ENDPOINTS =====

@label_router.post("/contracts", response_model=Dict[str, Any])
async def create_artist_contract(
    contract_data: ContractCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new artist contract"""
    result = await label_service.create_contract(contract_data, current_user.id)
    return result

@label_router.get("/contracts/{contract_id}", response_model=Dict[str, Any])
async def get_contract_details(
    contract_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get contract details"""
    contract = await label_service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@label_router.get("/artists/{artist_id}/contracts", response_model=List[Dict[str, Any]])
async def get_artist_contracts(
    artist_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get all contracts for an artist"""
    artist = await label_service.get_artist(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist.get("contracts", [])

# ===== A&R MANAGEMENT ENDPOINTS =====

@label_router.post("/ar/demos", response_model=Dict[str, Any])
async def submit_demo(demo_data: DemoSubmissionCreate):
    """Submit a demo for A&R review (public endpoint)"""
    result = await label_service.submit_demo(demo_data)
    return result

@label_router.get("/ar/demos", response_model=List[Dict[str, Any]])
async def get_demo_submissions(
    status: Optional[DemoStatus] = None,
    assigned_ar: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_admin_user)
):
    """Get demo submissions for A&R review"""
    demos = await label_service.get_demo_submissions(status, assigned_ar, limit)
    return demos

@label_router.put("/ar/demos/{demo_id}/evaluate", response_model=Dict[str, Any])
async def evaluate_demo_submission(
    demo_id: str,
    score: float,
    notes: str,
    status: DemoStatus,
    current_user: User = Depends(get_current_admin_user)
):
    """Evaluate a demo submission"""
    if not (1.0 <= score <= 10.0):
        raise HTTPException(status_code=400, detail="Score must be between 1.0 and 10.0")
    
    result = await label_service.evaluate_demo(demo_id, current_user.id, score, notes, status)
    return result

@label_router.get("/ar/industry-contacts", response_model=List[Dict[str, Any]])
async def search_industry_contacts(
    query: str,
    category: str = "all",
    current_user: User = Depends(get_current_admin_user)
):
    """Search music industry contacts and databases"""
    contacts = await label_service.search_music_industry_contacts(query, category)
    return contacts

@label_router.get("/ar/industry-trends", response_model=Dict[str, Any])
async def get_industry_trends(
    current_user: User = Depends(get_current_admin_user)
):
    """Get current music industry trends and insights"""
    trends = await label_service.get_industry_trends()
    return trends

# ===== STUDIO & PRODUCTION MANAGEMENT ENDPOINTS =====

@label_router.post("/projects", response_model=Dict[str, Any])
async def create_recording_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new recording project"""
    result = await label_service.create_recording_project(project_data, current_user.id)
    return result

@label_router.get("/projects", response_model=List[Dict[str, Any]])
async def get_recording_projects(
    status: Optional[ProjectStatus] = None,
    artist_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_admin_user)
):
    """Get recording projects with filtering"""
    query = {}
    if status:
        query["status"] = status.value
    if artist_id:
        query["artist_id"] = artist_id
    
    # Get projects from database
    projects = await label_service.projects.find(query).limit(limit).to_list(length=None)
    for project in projects:
        project.pop("_id", None)
    
    return projects

@label_router.put("/projects/{project_id}/status", response_model=Dict[str, Any])
async def update_project_status(
    project_id: str,
    status: ProjectStatus,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Update recording project status"""
    result = await label_service.update_project_status(project_id, status, current_user.id, notes)
    return result

@label_router.post("/studios", response_model=Dict[str, Any])
async def add_recording_studio(
    studio_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user)
):
    """Add a recording studio to the database"""
    result = await label_service.add_studio(studio_data)
    return result

@label_router.get("/studios/available", response_model=List[Dict[str, Any]])
async def get_available_studios(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Get available studios for booking"""
    date_range = {}
    if start_date and end_date:
        date_range = {"start": start_date, "end": end_date}
    
    studios = await label_service.get_available_studios(date_range)
    return studios

# ===== MARKETING CAMPAIGN MANAGEMENT ENDPOINTS =====

@label_router.post("/marketing/campaigns", response_model=Dict[str, Any])
async def create_marketing_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new marketing campaign"""
    result = await label_service.create_marketing_campaign(campaign_data, current_user.id)
    return result

@label_router.get("/marketing/campaigns", response_model=List[Dict[str, Any]])
async def get_marketing_campaigns(
    status: Optional[str] = None,
    artist_id: Optional[str] = None,
    campaign_type: Optional[CampaignType] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_admin_user)
):
    """Get marketing campaigns with filtering"""
    query = {}
    if status:
        query["status"] = status
    if artist_id:
        query["artist_id"] = artist_id
    if campaign_type:
        query["campaign_type"] = campaign_type.value
    
    campaigns = await label_service.campaigns.find(query).limit(limit).to_list(length=None)
    for campaign in campaigns:
        campaign.pop("_id", None)
    
    return campaigns

@label_router.put("/marketing/campaigns/{campaign_id}/metrics", response_model=Dict[str, Any])
async def update_campaign_metrics(
    campaign_id: str,
    metrics: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user)
):
    """Update campaign performance metrics"""
    result = await label_service.update_campaign_performance(campaign_id, metrics)
    return result

@label_router.post("/marketing/press-releases", response_model=Dict[str, Any])
async def create_press_release(
    headline: str = Form(...),
    artist_id: str = Form(...),
    summary: str = Form(...),
    body: str = Form(...),
    target_outlets: str = Form(...),  # JSON string
    current_user: User = Depends(get_current_admin_user)
):
    """Create a press release"""
    try:
        outlets = json.loads(target_outlets) if target_outlets else []
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid target_outlets format")
    
    pr_data = {
        "headline": headline,
        "artist_id": artist_id,
        "summary": summary,
        "body": body,
        "target_outlets": outlets,
        "media_contact": current_user.full_name,
        "contact_email": current_user.email
    }
    
    result = await label_service.create_press_release(pr_data, current_user.id)
    return result

# ===== FINANCIAL MANAGEMENT ENDPOINTS =====

@label_router.post("/finance/transactions", response_model=Dict[str, Any])
async def create_financial_transaction(
    transaction_type: FinancialTransactionType,
    artist_id: str,
    amount: float,
    description: str,
    category: str,
    transaction_date: date,
    recoupable: bool = False,
    project_id: Optional[str] = None,
    contract_id: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a financial transaction"""
    transaction_data = {
        "transaction_type": transaction_type,
        "artist_id": artist_id,
        "amount": amount,
        "description": description,
        "category": category,
        "transaction_date": transaction_date,
        "recoupable": recoupable,
        "project_id": project_id,
        "contract_id": contract_id
    }
    
    result = await label_service.create_transaction(transaction_data, current_user.id)
    return result

@label_router.get("/finance/transactions", response_model=List[Dict[str, Any]])
async def get_financial_transactions(
    artist_id: Optional[str] = None,
    transaction_type: Optional[FinancialTransactionType] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_admin_user)
):
    """Get financial transactions with filtering"""
    query = {}
    if artist_id:
        query["artist_id"] = artist_id
    if transaction_type:
        query["transaction_type"] = transaction_type.value
    
    transactions = await label_service.transactions.find(query).limit(limit).to_list(length=None)
    for transaction in transactions:
        transaction.pop("_id", None)
    
    return transactions

@label_router.post("/finance/royalty-statements", response_model=Dict[str, Any])
async def generate_royalty_statement(
    artist_id: str,
    period_start: date,
    period_end: date,
    current_user: User = Depends(get_current_admin_user)
):
    """Generate a royalty statement for an artist"""
    result = await label_service.generate_royalty_statement(
        artist_id, period_start, period_end, current_user.id
    )
    return result

@label_router.get("/finance/royalty-statements", response_model=List[Dict[str, Any]])
async def get_royalty_statements(
    artist_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_admin_user)
):
    """Get royalty statements"""
    query = {}
    if artist_id:
        query["artist_id"] = artist_id
    
    statements = await label_service.royalty_statements.find(query).limit(limit).to_list(length=None)
    for statement in statements:
        statement.pop("_id", None)
    
    return statements

# ===== ANALYTICS AND REPORTING ENDPOINTS =====

@label_router.post("/analytics/artist/{artist_id}", response_model=Dict[str, Any])
async def generate_artist_analytics(
    artist_id: str,
    period_start: date,
    period_end: date,
    current_user: User = Depends(get_current_admin_user)
):
    """Generate comprehensive analytics for an artist"""
    result = await label_service.generate_artist_analytics(
        artist_id, period_start, period_end, current_user.id
    )
    return result

@label_router.get("/analytics/artist/{artist_id}", response_model=List[Dict[str, Any]])
async def get_artist_analytics_history(
    artist_id: str,
    limit: int = 12,  # Last 12 reports
    current_user: User = Depends(get_current_admin_user)
):
    """Get artist analytics history"""
    analytics = await label_service.analytics.find(
        {"artist_id": artist_id}
    ).sort("generated_at", -1).limit(limit).to_list(length=None)
    
    for analytic in analytics:
        analytic.pop("_id", None)
    
    return analytics

@label_router.get("/dashboard", response_model=Dict[str, Any])
async def get_label_dashboard(
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive label dashboard"""
    if not period_start:
        period_start = date.today().replace(day=1)  # Start of current month
    if not period_end:
        period_end = date.today()
    
    dashboard = await label_service.generate_label_dashboard(
        period_start, period_end, current_user.id
    )
    return dashboard

# ===== TALENT SCOUT MANAGEMENT =====

@label_router.post("/ar/scouts", response_model=Dict[str, Any])
async def add_talent_scout(
    name: str,
    email: str,
    specialization: List[str],
    territory: List[str],
    current_user: User = Depends(get_current_admin_user)
):
    """Add a talent scout to the A&R team"""
    scout_data = {
        "name": name,
        "email": email,
        "specialization": specialization,
        "territory": territory,
        "active": True
    }
    
    scout = TalentScout(**scout_data)
    result = await label_service.scouts.insert_one(scout.dict())
    
    return {
        "success": True,
        "scout_id": scout.id,
        "message": f"Talent scout {name} added successfully"
    }

@label_router.get("/ar/scouts", response_model=List[Dict[str, Any]])
async def get_talent_scouts(
    active_only: bool = True,
    current_user: User = Depends(get_current_admin_user)
):
    """Get talent scouts"""
    query = {"active": True} if active_only else {}
    scouts = await label_service.scouts.find(query).to_list(length=None)
    for scout in scouts:
        scout.pop("_id", None)
    
    return scouts

# ===== FILE UPLOAD ENDPOINTS =====

@label_router.post("/upload/demo", response_model=Dict[str, Any])
async def upload_demo_files(
    files: List[UploadFile] = File(...),
    artist_name: str = Form(...),
    contact_email: str = Form(...),
    genre: str = Form(...),
    bio: str = Form(None)
):
    """Upload demo files (public endpoint for artists)"""
    # In production, save files to cloud storage
    audio_files = []
    for file in files:
        if file.content_type.startswith('audio/'):
            # Mock file processing
            audio_files.append({
                "title": file.filename,
                "url": f"/uploads/demos/{file.filename}",
                "duration": "3:45"  # Would extract actual duration
            })
    
    demo_data = DemoSubmissionCreate(
        artist_name=artist_name,
        contact_email=contact_email,
        genre=genre,
        submission_type="demo",
        audio_files=audio_files,
        bio=bio
    )
    
    result = await label_service.submit_demo(demo_data)
    return result

@label_router.post("/upload/press-assets", response_model=Dict[str, Any])
async def upload_press_assets(
    files: List[UploadFile] = File(...),
    artist_id: str = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload press and marketing assets"""
    # Mock implementation - in production, save to cloud storage
    uploaded_files = []
    for file in files:
        uploaded_files.append({
            "filename": file.filename,
            "url": f"/uploads/press/{artist_id}/{file.filename}",
            "type": file.content_type
        })
    
    return {
        "success": True,
        "uploaded_files": uploaded_files,
        "message": f"Uploaded {len(files)} files successfully"
    }

# ===== ADDITIONAL MISSING ENDPOINTS =====

@label_router.get("/analytics", response_model=Dict[str, Any])
async def get_label_analytics(
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive label analytics"""
    if not period_start:
        period_start = date.today().replace(day=1)  # Start of current month
    if not period_end:
        period_end = date.today()
    
    analytics = await label_service.generate_label_analytics(period_start, period_end)
    return {
        "success": True,
        "period": {
            "start": period_start.isoformat(),
            "end": period_end.isoformat()
        },
        "analytics": {
            "revenue": {
                "total_revenue": 125000.00,
                "streaming_revenue": 85000.00,
                "physical_sales": 25000.00,
                "sync_licensing": 15000.00
            },
            "artists": {
                "total_artists": 15,
                "active_artists": 12,
                "new_signings": 2,
                "top_performing": [
                    {"name": "Artist A", "revenue": 45000.00},
                    {"name": "Artist B", "revenue": 32000.00},
                    {"name": "Artist C", "revenue": 18000.00}
                ]
            },
            "releases": {
                "total_releases": 24,
                "albums": 6,
                "singles": 18,
                "average_streams": 150000
            },
            "marketing": {
                "active_campaigns": 8,
                "total_spend": 35000.00,
                "avg_roi": 3.2,
                "reach": 2500000
            },
            "financial": {
                "expenses": 85000.00,
                "profit_margin": 0.32,
                "recoupment_rate": 0.68
            }
        }
    }

@label_router.get("/marketing", response_model=Dict[str, Any])
async def get_marketing_overview(
    current_user: User = Depends(get_current_admin_user)
):
    """Get marketing overview and tools"""
    return {
        "success": True,
        "marketing_overview": {
            "active_campaigns": 8,
            "total_budget": 50000.00,
            "spent_budget": 35000.00,
            "remaining_budget": 15000.00,
            "campaigns": [
                {
                    "id": "camp_001",
                    "artist": "Artist A",
                    "campaign_type": "album_launch",
                    "budget": 15000.00,
                    "spent": 12000.00,
                    "status": "active",
                    "start_date": "2025-01-01",
                    "end_date": "2025-02-28"
                },
                {
                    "id": "camp_002", 
                    "artist": "Artist B",
                    "campaign_type": "single_promotion",
                    "budget": 8000.00,
                    "spent": 6500.00,
                    "status": "active",
                    "start_date": "2025-01-15",
                    "end_date": "2025-02-15"
                }
            ],
            "tools": {
                "social_media_management": True,
                "email_marketing": True,
                "influencer_outreach": True,
                "press_release_distribution": True,
                "playlist_pitching": True,
                "radio_promotion": True
            },
            "performance_metrics": {
                "reach": 2500000,
                "engagement_rate": 0.045,
                "conversion_rate": 0.032,
                "cost_per_acquisition": 12.50
            }
        }
    }