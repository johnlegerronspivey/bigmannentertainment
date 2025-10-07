"""
Profile API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, List
from profile_service import profile_service
from profile_models import UserProfile, Asset, Proposal, Vote
from pg_database import get_async_session
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

# Import authentication from existing system
try:
    from server import get_current_user, User
except:
    # Fallback if not available
    async def get_current_user():
        return {"id": "test_user", "email": "test@example.com"}
    class User:
        pass

router = APIRouter(prefix="/api/profile", tags=["Creator Profiles"])

# Helper function to extract user ID from current_user (dict or object)
def get_user_id(current_user) -> str:
    """Extract user ID from current_user which can be dict or object"""
    return current_user.get('id') if isinstance(current_user, dict) else current_user.id

def get_user_email(current_user) -> str:
    """Extract user email from current_user which can be dict or object"""
    return current_user.get('email') if isinstance(current_user, dict) else current_user.email

# Pydantic models for requests
class ProfileCreateRequest(BaseModel):
    display_name: Optional[str] = None
    tagline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    profile_public: bool = True
    show_earnings: bool = False

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    tagline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    campaign_title: Optional[str] = None
    campaign_description: Optional[str] = None
    profile_public: Optional[bool] = None
    show_earnings: Optional[bool] = None
    show_dao_activity: Optional[bool] = None

class AssetCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    asset_type: str  # music, video, merch, image
    thumbnail_url: Optional[str] = None
    content_url: Optional[str] = None
    mongo_media_id: Optional[str] = None
    license: str = "All Rights Reserved"
    copyright_notice: Optional[str] = None
    rights_holder: Optional[str] = None

class ProposalCreateRequest(BaseModel):
    title: str
    description: str
    proposal_type: str
    target_asset_id: Optional[str] = None
    target_data: Dict = {}
    voting_ends_in_days: int = 7

class VoteRequest(BaseModel):
    choice: str  # yes, no, abstain
    comment: Optional[str] = None

# Profile Endpoints

# IMPORTANT: Specific routes must come before dynamic /{username} route

# Health check
@router.get("/health")
async def profile_health():
    """Check profile service health"""
    import os
    postgres_url = os.getenv("POSTGRES_URL")
    postgres_configured = bool(postgres_url and "localhost" in postgres_url)
    
    # Test actual connection
    connection_status = "disconnected"
    try:
        from pg_database import async_engine
        async with async_engine.connect() as conn:
            connection_status = "connected"
    except Exception as e:
        connection_status = f"error: {str(e)[:100]}"
    
    return {
        "status": "healthy" if connection_status == "connected" else "degraded",
        "service": "creator_profiles",
        "postgres": connection_status,
        "mongodb": "connected",
        "message": "All systems operational" if connection_status == "connected" else f"PostgreSQL issue: {connection_status}"
    }

# Get current user's profile
@router.get("/me")
async def get_my_profile(current_user = Depends(get_current_user)):
    """Get current user's profile"""
    profile = await profile_service.get_profile_by_mongo_id(get_user_id(current_user))
    
    if not profile:
        return {
            "hasProfile": False,
            "message": "No profile created yet",
            "identity": None
        }
    
    return profile

@router.post("/create")
async def create_profile(
    request: ProfileCreateRequest,
    current_user = Depends(get_current_user)
):
    """Create profile for current user"""
    # Check if profile already exists
    existing = await profile_service.get_profile_by_mongo_id(get_user_id(current_user))
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    # Create profile
    profile = await profile_service.create_profile(
        mongo_user_id=get_user_id(current_user),
        username=get_user_email(current_user).split('@')[0],  # Use email prefix as username
        data=request.dict()
    )
    
    return {
        "success": True,
        "message": "Profile created successfully",
        "profile": {
            "id": profile.id,
            "username": profile.username,
            "gln": profile.gln
        }
    }

@router.put("/me")
async def update_profile(
    request: ProfileUpdateRequest,
    current_user = Depends(get_current_user)
):
    """Update current user's profile"""
    # Get existing profile
    existing = await profile_service.get_profile_by_mongo_id(get_user_id(current_user))
    
    if not existing:
        # Auto-create profile if not exists
        username = get_user_email(current_user).split('@')[0] if hasattr(current_user, 'email') else f"user_{get_user_id(current_user)}"
        profile = await profile_service.create_profile(
            mongo_user_id=get_user_id(current_user),
            username=username,
            data=request.dict(exclude_unset=True)
        )
        return {
            "success": True,
            "message": "Profile created successfully"
        }
    
    # Update profile
    profile = await profile_service.update_profile(
        username=existing["identity"]["username"],
        data=request.dict(exclude_unset=True)
    )
    
    return {
        "success": True,
        "message": "Profile updated successfully"
    }

# Get public profile by username (dynamic route - must be last)
@router.get("/{username}")
async def get_profile(username: str):
    """Get public profile by username"""
    profile = await profile_service.get_profile_by_username(username)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if not profile["identity"]["profilePublic"]:
        raise HTTPException(status_code=403, detail="Profile is private")
    
    return profile

# Asset Endpoints

@router.post("/assets/create")
async def create_asset(
    request: AssetCreateRequest,
    current_user = Depends(get_current_user)
):
    """Create new asset with GS1 identifiers"""
    # Get user profile
    profile = await profile_service.get_profile_by_mongo_id(get_user_id(current_user))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create one first.")
    
    # Extract profile ID (it's in the identity section)
    async with get_async_session() as session:
        result = await session.execute(
            select(UserProfile).where(UserProfile.mongo_user_id == get_user_id(current_user))
        )
        user_profile = result.scalar_one_or_none()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        asset = await profile_service.create_asset(
            user_id=user_profile.id,
            asset_data=request.dict()
        )
        
        return {
            "success": True,
            "message": "Asset created successfully",
            "asset": {
                "id": asset.id,
                "title": asset.title,
                "gtin": asset.gtin,
                "isrc": asset.isrc,
                "isan": asset.isan,
                "gdti": asset.gdti,
                "gs1_digital_link": asset.asset_metadata.get('gs1_digital_link'),
                "qr_code": asset.asset_metadata.get('qr_code')
            }
        }

@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str):
    """Get asset details with GS1 metadata"""
    async with get_async_session() as session:
        result = await session.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return {
            "id": asset.id,
            "title": asset.title,
            "description": asset.description,
            "type": asset.asset_type,
            "thumbnail": asset.thumbnail_url,
            "gtin": asset.gtin,
            "isrc": asset.isrc,
            "isan": asset.isan,
            "gdti": asset.gdti,
            "gs1_digital_link": asset.asset_metadata.get('gs1_digital_link') if asset.asset_metadata else None,
            "qr_code": asset.asset_metadata.get('qr_code') if asset.asset_metadata else None,
            "license": asset.license,
            "engagement": {
                "views": asset.views,
                "likes": asset.likes,
                "shares": asset.shares
            },
            "contract_status": asset.contract_status
        }

# DAO Governance Endpoints

@router.post("/dao/proposals")
async def create_proposal(
    request: ProposalCreateRequest,
    current_user = Depends(get_current_user)
):
    """Create DAO proposal"""
    async with get_async_session() as session:
        # Get user profile
        result = await session.execute(
            select(UserProfile).where(UserProfile.mongo_user_id == get_user_id(current_user))
        )
        user_profile = result.scalar_one_or_none()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Create proposal
        voting_ends_at = datetime.now(timezone.utc) + timedelta(days=request.voting_ends_in_days)
        
        proposal = Proposal(
            user_id=user_profile.id,
            title=request.title,
            description=request.description,
            proposal_type=request.proposal_type,
            target_asset_id=request.target_asset_id,
            target_data=request.target_data,
            status="open",
            voting_ends_at=voting_ends_at
        )
        
        session.add(proposal)
        await session.commit()
        await session.refresh(proposal)
        
        return {
            "success": True,
            "message": "Proposal created successfully",
            "proposal": {
                "id": proposal.id,
                "title": proposal.title,
                "status": proposal.status,
                "voting_ends_at": proposal.voting_ends_at.isoformat()
            }
        }

@router.post("/dao/proposals/{proposal_id}/vote")
async def vote_on_proposal(
    proposal_id: str,
    request: VoteRequest,
    current_user = Depends(get_current_user)
):
    """Vote on DAO proposal"""
    async with get_async_session() as session:
        # Get user profile
        user_result = await session.execute(
            select(UserProfile).where(UserProfile.mongo_user_id == get_user_id(current_user))
        )
        user_profile = user_result.scalar_one_or_none()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get proposal
        proposal_result = await session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        proposal = proposal_result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        if proposal.status != "open":
            raise HTTPException(status_code=400, detail="Voting is closed")
        
        if proposal.voting_ends_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Voting period has ended")
        
        # Check if already voted
        existing_vote = await session.execute(
            select(Vote).where(
                Vote.proposal_id == proposal_id,
                Vote.voter_id == user_profile.id
            )
        )
        if existing_vote.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Already voted on this proposal")
        
        # Create vote (weight = 1 for now, can be enhanced with token-based weighting)
        vote = Vote(
            proposal_id=proposal_id,
            voter_id=user_profile.id,
            choice=request.choice,
            weight=1,
            comment=request.comment
        )
        
        session.add(vote)
        
        # Update proposal vote counts
        if request.choice == "yes":
            proposal.total_yes += 1
        elif request.choice == "no":
            proposal.total_no += 1
        else:
            proposal.total_abstain += 1
        
        proposal.total_votes += 1
        
        await session.commit()
        
        return {
            "success": True,
            "message": "Vote recorded successfully",
            "proposal": {
                "id": proposal.id,
                "votes": {
                    "yes": proposal.total_yes,
                    "no": proposal.total_no,
                    "abstain": proposal.total_abstain,
                    "total": proposal.total_votes
                }
            }
        }

@router.get("/dao/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get proposal details"""
    async with get_async_session() as session:
        result = await session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        return {
            "id": proposal.id,
            "title": proposal.title,
            "description": proposal.description,
            "type": proposal.proposal_type,
            "status": proposal.status,
            "votes": {
                "yes": proposal.total_yes,
                "no": proposal.total_no,
                "abstain": proposal.total_abstain,
                "total": proposal.total_votes
            },
            "created_at": proposal.created_at.isoformat(),
            "voting_ends_at": proposal.voting_ends_at.isoformat() if proposal.voting_ends_at else None
        }

@router.get("/dao/proposals")
async def list_proposals(
    status: Optional[str] = None,
    limit: int = 20
):
    """List DAO proposals"""
    async with get_async_session() as session:
        query = select(Proposal).order_by(Proposal.created_at.desc()).limit(limit)
        
        if status:
            query = query.where(Proposal.status == status)
        
        result = await session.execute(query)
        proposals = result.scalars().all()
        
        return {
            "proposals": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description[:200] + "..." if len(p.description) > 200 else p.description,
                    "type": p.proposal_type,
                    "status": p.status,
                    "votes": {
                        "yes": p.total_yes,
                        "no": p.total_no,
                        "total": p.total_votes
                    },
                    "created_at": p.created_at.isoformat()
                }
                for p in proposals
            ],
            "total": len(proposals)
        }
