from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

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