from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import authentication function
try:
    from server import get_current_admin_user, get_current_user
except ImportError:
    # Fallback if import fails
    def get_current_admin_user():
        return {"id": "admin", "email": "admin@bigmannentertainment.com", "role": "admin"}
    
    def get_current_user():
        return {"id": "user", "email": "user@bigmannentertainment.com", "role": "user"}

# Simple label router without complex dependencies
label_router = APIRouter(prefix="/label", tags=["Label Management"])

@label_router.get("/test")
async def test_label_endpoint():
    """Test endpoint to verify label routing works"""
    return {
        "message": "Big Mann Entertainment Label Management System", 
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@label_router.get("/status")
async def label_system_status():
    """Get label system status"""
    return {
        "label_system": "operational",
        "features": [
            "Artist Management",
            "A&R Management", 
            "Contract Management",
            "Studio & Production",
            "Marketing Campaigns",
            "Financial Management",
            "Analytics & Reporting"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

# Simple demo endpoint (public)
@label_router.post("/ar/demos/submit")
async def submit_demo_simple(demo_data: dict):
    """Submit a demo for A&R review (simplified version)"""
    artist_name = demo_data.get("artist_name")
    contact_email = demo_data.get("contact_email")
    genre = demo_data.get("genre")
    bio = demo_data.get("bio", "")
    
    if not all([artist_name, contact_email, genre]):
        raise HTTPException(status_code=400, detail="artist_name, contact_email, and genre are required")
    
    return {
        "success": True,
        "message": f"Demo submitted successfully for {artist_name}",
        "submission_id": f"DEMO_{int(datetime.utcnow().timestamp())}",
        "contact_email": contact_email,
        "genre": genre,
        "status": "submitted",
        "next_steps": "You will receive feedback within 2-3 weeks",
        "timestamp": datetime.utcnow().isoformat()
    }

# ===== DASHBOARD ENDPOINTS =====

@label_router.get("/dashboard")
async def get_label_dashboard(current_user=Depends(get_current_admin_user)):
    """Get comprehensive label dashboard"""
    return {
        "label_name": "Big Mann Entertainment",
        "owner": "John LeGerron Spivey",
        "total_artists": 12,
        "active_projects": 8,
        "releases_this_month": 3,
        "total_streams": 2500000,
        "total_revenue": 185000,
        "top_artists": [
            {"stage_name": "Artist One", "streams": 850000, "revenue": 45000},
            {"stage_name": "Rising Star", "streams": 650000, "revenue": 32000},
            {"stage_name": "Hip Hop Legend", "streams": 500000, "revenue": 28000}
        ],
        "revenue_breakdown": {
            "streaming": 95000,
            "downloads": 35000,
            "sync": 25000,
            "merchandise": 18000,
            "live_performances": 12000
        },
        "ar_metrics": {
            "demos_received": 156,
            "artists_signed": 3,
            "conversion_rate": 1.9
        },
        "active_campaigns": 5,
        "campaign_reach": 1200000,
        "average_roi": 3.2,
        "generated_at": datetime.utcnow().isoformat()
    }

# ===== ARTIST MANAGEMENT ENDPOINTS =====

@label_router.get("/artists")
async def get_artist_roster(
    status: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 50,
    current_user=Depends(get_current_admin_user)
):
    """Get artist roster with filtering"""
    # Mock artist data
    artists = [
        {
            "id": "artist_1",
            "stage_name": "MC Thunder",
            "real_name": "Marcus Johnson",
            "email": "mcthunder@email.com",
            "genres": ["hip-hop", "trap"],
            "status": "active",
            "signed_date": "2024-01-15",
            "monthly_listeners": 85000,
            "contracts": 2,
            "projects": 3
        },
        {
            "id": "artist_2", 
            "stage_name": "Luna Rose",
            "real_name": "Sarah Williams",
            "email": "lunarose@email.com",
            "genres": ["pop", "r&b"],
            "status": "active",
            "signed_date": "2023-09-20",
            "monthly_listeners": 126000,
            "contracts": 1,
            "projects": 2
        },
        {
            "id": "artist_3",
            "stage_name": "The Collective",
            "real_name": "Band Members",
            "email": "collective@email.com", 
            "genres": ["indie", "alternative"],
            "status": "development",
            "signed_date": "2024-03-10",
            "monthly_listeners": 12000,
            "contracts": 1,
            "projects": 1
        }
    ]
    
    # Apply filters
    if status:
        artists = [a for a in artists if a["status"] == status]
    if genre:
        artists = [a for a in artists if genre.lower() in [g.lower() for g in a["genres"]]]
    
    return artists[:limit]

@label_router.post("/artists")
async def create_artist(artist_data: Dict[str, Any], current_user=Depends(get_current_admin_user)):
    """Create a new artist profile"""
    required_fields = ["stage_name", "email"]
    for field in required_fields:
        if field not in artist_data:
            raise HTTPException(status_code=400, detail=f"{field} is required")
    
    artist_id = f"artist_{int(datetime.utcnow().timestamp())}"
    
    return {
        "success": True,
        "artist_id": artist_id,
        "message": f"Artist {artist_data['stage_name']} created successfully",
        "data": {
            "id": artist_id,
            "stage_name": artist_data["stage_name"],
            "email": artist_data["email"],
            "status": "development",
            "created_at": datetime.utcnow().isoformat()
        }
    }

@label_router.get("/artists/{artist_id}")
async def get_artist_profile(artist_id: str, current_user=Depends(get_current_admin_user)):
    """Get detailed artist profile"""
    # Mock detailed artist data
    artist = {
        "id": artist_id,
        "stage_name": "MC Thunder",
        "real_name": "Marcus Johnson", 
        "email": "mcthunder@email.com",
        "phone": "+1-555-0123",
        "genres": ["hip-hop", "trap"],
        "status": "active",
        "signed_date": "2024-01-15",
        "bio": "Rising hip-hop artist from Atlanta with unique style and powerful lyrics.",
        "social_media": {
            "instagram": "@mcthunder_official",
            "tiktok": "@mcthunder",
            "youtube": "MC Thunder Official"
        },
        "monthly_listeners": {
            "spotify": 45000,
            "apple_music": 25000,
            "youtube": 15000
        },
        "contracts": [
            {
                "id": "contract_1",
                "type": "recording",
                "status": "active",
                "start_date": "2024-01-15",
                "royalty_rate": 15.0,
                "advance_amount": 25000
            }
        ],
        "projects": [
            {
                "id": "project_1",
                "title": "Street Chronicles EP",
                "type": "EP",
                "status": "mixing",
                "progress": 75,
                "expected_completion": "2024-05-01"
            }
        ],
        "analytics": {
            "total_streams": 850000,
            "revenue_generated": 45000,
            "top_track": "City Lights",
            "growth_rate": 12.5
        }
    }
    
    return artist

# ===== A&R MANAGEMENT ENDPOINTS =====

@label_router.get("/ar/demos")
async def get_demo_submissions(
    status: Optional[str] = None,
    limit: int = 50,
    current_user=Depends(get_current_admin_user)
):
    """Get demo submissions for A&R review"""
    demos = [
        {
            "id": "demo_1",
            "artist_name": "Young Talent",
            "contact_email": "youngtalent@email.com",
            "genre": "r&b",
            "status": "reviewing",
            "submitted_at": "2024-04-10T10:30:00Z",
            "assigned_ar": "Sarah Johnson",
            "evaluation_score": 7.2,
            "audio_files": ["demo_track_1.mp3", "demo_track_2.mp3"]
        },
        {
            "id": "demo_2", 
            "artist_name": "Indie Collective",
            "contact_email": "indiecollective@email.com",
            "genre": "indie",
            "status": "shortlisted",
            "submitted_at": "2024-04-08T14:20:00Z",
            "assigned_ar": "Mike Rodriguez",
            "evaluation_score": 8.5,
            "audio_files": ["indie_demo.mp3"]
        },
        {
            "id": "demo_3",
            "artist_name": "Beat Master",
            "contact_email": "beatmaster@email.com",
            "genre": "electronic",
            "status": "submitted",
            "submitted_at": "2024-04-12T16:45:00Z",
            "assigned_ar": None,
            "evaluation_score": None,
            "audio_files": ["electronic_mix.mp3"]
        }
    ]
    
    if status:
        demos = [d for d in demos if d["status"] == status]
    
    return demos[:limit]

@label_router.put("/ar/demos/{demo_id}/evaluate")
async def evaluate_demo(
    demo_id: str,
    evaluation_data: Dict[str, Any],
    current_user=Depends(get_current_admin_user)
):
    """Evaluate a demo submission"""
    required_fields = ["score", "notes", "status"]
    for field in required_fields:
        if field not in evaluation_data:
            raise HTTPException(status_code=400, detail=f"{field} is required")
    
    score = evaluation_data["score"]
    if not (1.0 <= score <= 10.0):
        raise HTTPException(status_code=400, detail="Score must be between 1.0 and 10.0")
    
    return {
        "success": True,
        "demo_id": demo_id,
        "evaluation": {
            "score": score,
            "notes": evaluation_data["notes"],
            "status": evaluation_data["status"],
            "evaluated_by": current_user.get("email", "admin"),
            "evaluated_at": datetime.utcnow().isoformat()
        },
        "message": "Demo evaluation completed successfully"
    }

@label_router.get("/ar/industry-trends")
async def get_industry_trends(current_user=Depends(get_current_admin_user)):
    """Get current music industry trends and insights"""
    return {
        "trending_genres": [
            {"genre": "afrobeats", "growth": "+45%", "market_share": "8.2%"},
            {"genre": "bedroom_pop", "growth": "+32%", "market_share": "4.1%"},
            {"genre": "drill", "growth": "+28%", "market_share": "6.7%"},
            {"genre": "hyperpop", "growth": "+25%", "market_share": "2.9%"}
        ],
        "popular_artists_emerging": [
            {"name": "Artist A", "genre": "afrobeats", "monthly_listeners": "2.1M"},
            {"name": "Artist B", "genre": "bedroom_pop", "monthly_listeners": "1.8M"}
        ],
        "playlist_trends": {
            "top_playlists": ["New Music Friday", "RapCaviar", "Today's Top Hits"],
            "trending_moods": ["chill", "workout", "focus", "party"]
        },
        "market_insights": {
            "streaming_growth": "+12% YoY",
            "vinyl_sales": "+23% increase",
            "podcast_music": "+67% growth",
            "top_markets": ["US", "UK", "Germany", "Japan", "Brazil"]
        },
        "generated_at": datetime.utcnow().isoformat()
    }

@label_router.get("/ar/industry-contacts")
async def search_industry_contacts(
    query: str,
    category: str = "all",
    current_user=Depends(get_current_admin_user)
):
    """Search music industry contacts and databases"""
    # Mock industry contacts
    all_contacts = {
        "radio": [
            {"name": "KCRW Music Director", "email": "music@kcrw.com", "genre": "indie", "location": "LA"},
            {"name": "BBC Radio 1", "email": "newmusic@bbc.co.uk", "genre": "pop", "location": "UK"},
            {"name": "Hot 97", "email": "music@hot97.com", "genre": "hip-hop", "location": "NYC"}
        ],
        "press": [
            {"name": "Pitchfork", "email": "tips@pitchfork.com", "focus": "indie music", "reach": "2M"},
            {"name": "Rolling Stone", "email": "news@rollingstone.com", "focus": "all genres", "reach": "15M"},
            {"name": "Complex", "email": "music@complex.com", "focus": "hip-hop/pop", "reach": "8M"}
        ],
        "playlist": [
            {"name": "Spotify New Music Friday", "curator": "Spotify Editorial", "followers": "2.8M"},
            {"name": "Apple Music Breakthrough", "curator": "Apple Music", "followers": "1.5M"},
            {"name": "YouTube Music Trending", "curator": "YouTube Music", "followers": "5.2M"}
        ]
    }
    
    if category == "all":
        contacts = []
        for cat_contacts in all_contacts.values():
            contacts.extend(cat_contacts)
    else:
        contacts = all_contacts.get(category, [])
    
    # Simple search filter
    if query:
        contacts = [c for c in contacts if query.lower() in str(c).lower()]
    
    return {
        "query": query,
        "category": category,
        "contacts": contacts,
        "total_found": len(contacts)
    }

# ===== STUDIO & PRODUCTION ENDPOINTS =====

@label_router.get("/projects")
async def get_recording_projects(
    status: Optional[str] = None,
    artist_id: Optional[str] = None,
    limit: int = 50,
    current_user=Depends(get_current_admin_user)
):
    """Get recording projects with filtering"""
    projects = [
        {
            "id": "project_1",
            "title": "Street Chronicles EP",
            "artist_id": "artist_1", 
            "artist_name": "MC Thunder",
            "project_type": "EP",
            "status": "mixing",
            "progress": 75,
            "budget": 15000,
            "spent": 11250,
            "start_date": "2024-02-01",
            "expected_completion": "2024-05-01",
            "total_tracks": 6,
            "completed_tracks": 4
        },
        {
            "id": "project_2",
            "title": "Luna Rising Album",
            "artist_id": "artist_2",
            "artist_name": "Luna Rose",
            "project_type": "album", 
            "status": "recording",
            "progress": 45,
            "budget": 35000,
            "spent": 18200,
            "start_date": "2024-01-15",
            "expected_completion": "2024-07-01",
            "total_tracks": 12,
            "completed_tracks": 5
        }
    ]
    
    # Apply filters
    if status:
        projects = [p for p in projects if p["status"] == status]
    if artist_id:
        projects = [p for p in projects if p["artist_id"] == artist_id]
    
    return projects[:limit]

@label_router.post("/projects")
async def create_recording_project(
    project_data: Dict[str, Any],
    current_user=Depends(get_current_admin_user)
):
    """Create a new recording project"""
    required_fields = ["title", "artist_id", "project_type", "budget"]
    for field in required_fields:
        if field not in project_data:
            raise HTTPException(status_code=400, detail=f"{field} is required")
    
    project_id = f"project_{int(datetime.utcnow().timestamp())}"
    
    return {
        "success": True,
        "project_id": project_id,
        "message": f"Recording project '{project_data['title']}' created successfully",
        "data": {
            "id": project_id,
            "title": project_data["title"],
            "artist_id": project_data["artist_id"],
            "project_type": project_data["project_type"],
            "status": "planning",
            "budget": project_data["budget"],
            "created_at": datetime.utcnow().isoformat()
        }
    }

# ===== MARKETING ENDPOINTS =====

@label_router.get("/marketing/campaigns")
async def get_marketing_campaigns(
    status: Optional[str] = None,
    artist_id: Optional[str] = None,
    limit: int = 50,
    current_user=Depends(get_current_admin_user)
):
    """Get marketing campaigns with filtering"""
    campaigns = [
        {
            "id": "campaign_1",
            "name": "Street Chronicles Launch",
            "artist_id": "artist_1",
            "artist_name": "MC Thunder",
            "campaign_type": "album_release",
            "status": "active",
            "start_date": "2024-04-01",
            "end_date": "2024-06-01",
            "total_budget": 12000,
            "spent": 8500,
            "reach": 450000,
            "engagement_rate": 4.2,
            "roi": 2.8
        },
        {
            "id": "campaign_2",
            "name": "Luna Rose Brand Building",
            "artist_id": "artist_2",
            "artist_name": "Luna Rose",
            "campaign_type": "brand_awareness",
            "status": "planning",
            "start_date": "2024-05-15",
            "end_date": "2024-08-15",
            "total_budget": 18000,
            "spent": 0,
            "reach": None,
            "engagement_rate": None,
            "roi": None
        }
    ]
    
    # Apply filters
    if status:
        campaigns = [c for c in campaigns if c["status"] == status]
    if artist_id:
        campaigns = [c for c in campaigns if c["artist_id"] == artist_id]
    
    return campaigns[:limit]

# ===== FINANCIAL ENDPOINTS =====

@label_router.get("/finance/transactions")
async def get_financial_transactions(
    artist_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: int = 50,
    current_user=Depends(get_current_admin_user)
):
    """Get financial transactions with filtering"""
    transactions = [
        {
            "id": "trans_1",
            "transaction_type": "advance",
            "artist_id": "artist_1",
            "artist_name": "MC Thunder",
            "amount": 25000,
            "description": "Recording advance for Street Chronicles EP",
            "transaction_date": "2024-02-01",
            "status": "paid",
            "recoupable": True
        },
        {
            "id": "trans_2",
            "transaction_type": "revenue",
            "artist_id": "artist_1", 
            "artist_name": "MC Thunder",
            "amount": 8500,
            "description": "Streaming royalties Q1 2024",
            "transaction_date": "2024-04-01",
            "status": "paid",
            "recoupable": False
        },
        {
            "id": "trans_3",
            "transaction_type": "expense",
            "artist_id": "artist_1",
            "artist_name": "MC Thunder",
            "amount": 3200,
            "description": "Marketing campaign costs",
            "transaction_date": "2024-03-15",
            "status": "paid",
            "recoupable": True
        }
    ]
    
    # Apply filters
    if artist_id:
        transactions = [t for t in transactions if t["artist_id"] == artist_id]
    if transaction_type:
        transactions = [t for t in transactions if t["transaction_type"] == transaction_type]
    
    return transactions[:limit]