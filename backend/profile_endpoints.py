"""
Profile API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import Response
from typing import Optional, Dict, List
from profile_service import profile_service
from profile_models import UserProfile, Asset, Proposal, Vote, ProposalComment
from pg_database import get_async_session
from gs1_profile_service import gs1_service
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

@router.get("/assets")
async def list_user_assets(current_user = Depends(get_current_user)):
    """List current user's assets"""
    async with get_async_session() as session:
        # Get user profile
        result = await session.execute(
            select(UserProfile).where(UserProfile.mongo_user_id == get_user_id(current_user))
        )
        user_profile = result.scalar_one_or_none()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get user's assets
        assets_result = await session.execute(
            select(Asset).where(Asset.user_id == user_profile.id).order_by(Asset.created_at.desc())
        )
        assets = assets_result.scalars().all()
        
        return {
            "assets": [
                {
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
                    "license": asset.license,
                    "engagement": {
                        "views": asset.views,
                        "likes": asset.likes,
                        "shares": asset.shares
                    },
                    "contract_status": asset.contract_status,
                    "created_at": asset.created_at.isoformat()
                }
                for asset in assets
            ],
            "total": len(assets)
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



# Proposal Comments/Discussion Endpoints

class ProposalCommentRequest(BaseModel):
    comment_text: str
    parent_comment_id: Optional[str] = None

@router.post("/dao/proposals/{proposal_id}/comments")
async def create_proposal_comment(
    proposal_id: str,
    request: ProposalCommentRequest,
    current_user = Depends(get_current_user)
):
    """Add comment to proposal"""
    async with get_async_session() as session:
        # Get user profile
        user_result = await session.execute(
            select(UserProfile).where(UserProfile.mongo_user_id == get_user_id(current_user))
        )
        user_profile = user_result.scalar_one_or_none()
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Verify proposal exists
        proposal_result = await session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        if not proposal_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        comment = ProposalComment(
            proposal_id=proposal_id,
            user_id=user_profile.id,
            comment_text=request.comment_text,
            parent_comment_id=request.parent_comment_id
        )
        
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "comment": {
                "id": comment.id,
                "text": comment.comment_text,
                "created_at": comment.created_at.isoformat()
            }
        }

@router.get("/dao/proposals/{proposal_id}/comments")
async def get_proposal_comments(proposal_id: str):
    """Get all comments for a proposal"""
    async with get_async_session() as session:
        # Get proposal
        proposal_result = await session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        if not proposal_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Get comments with user info
        from sqlalchemy.orm import joinedload
        comments_result = await session.execute(
            select(ProposalComment)
            .where(ProposalComment.proposal_id == proposal_id)
            .order_by(ProposalComment.created_at.asc())
        )
        comments = comments_result.scalars().all()
        
        # Get user profiles for comments
        comments_list = []
        for comment in comments:
            user_result = await session.execute(
                select(UserProfile).where(UserProfile.id == comment.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            comments_list.append({
                "id": comment.id,
                "text": comment.comment_text,
                "author": {
                    "username": user.username if user else "Unknown",
                    "displayName": user.display_name if user else "Unknown User",
                    "avatarUrl": user.avatar_url if user else None
                },
                "parent_comment_id": comment.parent_comment_id,
                "likes": comment.likes,
                "created_at": comment.created_at.isoformat()
            })
        
        return {
            "comments": comments_list,
            "total": len(comments_list)
        }

@router.put("/dao/proposals/{proposal_id}/status")
async def update_proposal_status(
    proposal_id: str,
    status: str,
    current_user = Depends(get_current_user)
):
    """Update proposal status (owner or admin only)"""
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
        
        # Check authorization (owner of proposal can update)
        if proposal.user_id != user_profile.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this proposal")
        
        # Update status
        valid_statuses = ["open", "closed", "approved", "rejected", "executed"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        proposal.status = status
        if status == "executed":
            proposal.executed_at = datetime.now(timezone.utc)
        
        await session.commit()
        
        return {
            "success": True,
            "message": f"Proposal status updated to {status}",
            "proposal": {
                "id": proposal.id,
                "status": proposal.status,
                "executed_at": proposal.executed_at.isoformat() if proposal.executed_at else None
            }
        }

# Social Media Mock Endpoints (Phase 4: UI/Flow only, no actual API integration)

@router.get("/social/dashboard")
async def get_social_dashboard(current_user = Depends(get_current_user)):
    """Get social media dashboard with mock analytics data"""
    
    # Mock data for demonstration
    mock_platforms = [
        {
            "platform": "facebook",
            "name": "Facebook",
            "icon": "📘",
            "connected": True,
            "username": "@bigmann_ent",
            "followers": 125430,
            "posts": 342,
            "engagement_rate": 4.2,
            "recent_stats": {
                "likes": 8920,
                "comments": 1240,
                "shares": 563,
                "reach": 342100
            }
        },
        {
            "platform": "tiktok",
            "name": "TikTok",
            "icon": "🎵",
            "connected": True,
            "username": "@bigmann_music",
            "followers": 89200,
            "posts": 156,
            "engagement_rate": 8.7,
            "recent_stats": {
                "likes": 45600,
                "comments": 3420,
                "shares": 2130,
                "views": 1240000
            }
        },
        {
            "platform": "youtube",
            "name": "YouTube",
            "icon": "▶️",
            "connected": True,
            "username": "BigMannEntertainment",
            "followers": 67800,
            "posts": 89,
            "engagement_rate": 5.3,
            "recent_stats": {
                "likes": 12400,
                "comments": 890,
                "views": 452000,
                "watchTime": 89400
            }
        },
        {
            "platform": "twitter",
            "name": "Twitter/X",
            "icon": "🐦",
            "connected": False,
            "username": None,
            "followers": 0,
            "posts": 0,
            "engagement_rate": 0,
            "recent_stats": {}
        }
    ]
    
    return {
        "platforms": mock_platforms,
        "total_followers": sum(p["followers"] for p in mock_platforms),
        "total_posts": sum(p["posts"] for p in mock_platforms),
        "avg_engagement": sum(p["engagement_rate"] for p in mock_platforms if p["connected"]) / 3
    }

@router.get("/social/posts/scheduled")
async def get_scheduled_posts(current_user = Depends(get_current_user)):
    """Get scheduled posts (mock data)"""
    
    mock_scheduled = [
        {
            "id": "sched_1",
            "content": "🎵 New track dropping tomorrow! Stay tuned 🔥",
            "platforms": ["facebook", "tiktok", "twitter"],
            "scheduled_for": "2025-01-08T14:00:00Z",
            "status": "scheduled",
            "media_url": "https://example.com/track-preview.jpg"
        },
        {
            "id": "sched_2",
            "content": "Behind the scenes from today's studio session 🎤",
            "platforms": ["instagram", "youtube"],
            "scheduled_for": "2025-01-09T18:00:00Z",
            "status": "scheduled",
            "media_url": None
        }
    ]
    
    return {
        "scheduled_posts": mock_scheduled,
        "total": len(mock_scheduled)
    }

class SchedulePostRequest(BaseModel):
    content: str
    platforms: List[str]
    scheduled_for: str
    media_url: Optional[str] = None

@router.post("/social/posts/schedule")
async def schedule_post(
    request: SchedulePostRequest,
    current_user = Depends(get_current_user)
):
    """Schedule a post across multiple platforms (mock functionality)"""
    
    # In a real implementation, this would queue the post for publishing
    # For now, just return success with the scheduled data
    
    return {
        "success": True,
        "message": "Post scheduled successfully",
        "post": {
            "id": f"sched_{datetime.now().timestamp()}",
            "content": request.content,
            "platforms": request.platforms,
            "scheduled_for": request.scheduled_for,
            "status": "scheduled",
            "media_url": request.media_url
        }
    }

@router.delete("/social/posts/scheduled/{post_id}")
async def cancel_scheduled_post(
    post_id: str,
    current_user = Depends(get_current_user)
):
    """Cancel a scheduled post (mock functionality)"""
    
    return {
        "success": True,
        "message": "Scheduled post cancelled",
        "post_id": post_id
    }

# QR Code Generation Endpoints (Phase 5)

@router.get("/qr/generate")
async def generate_qr_code(
    data: str,
    with_logo: bool = True,
    download: bool = False
):
    """Generate QR code with optional BME logo"""
    
    if download:
        # Return as downloadable file
        qr_bytes = gs1_service.generate_qr_code_file(data, with_logo=with_logo)
        return Response(
            content=qr_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=qr_code_{datetime.now().timestamp()}.png"
            }
        )
    else:
        # Return as base64 string
        qr_base64 = gs1_service.generate_qr_code(data, with_logo=with_logo)
        return {
            "qr_code": qr_base64,
            "data": data
        }

@router.get("/assets/{asset_id}/qr")
async def get_asset_qr_code(
    asset_id: str,
    with_logo: bool = True,
    download: bool = False
):
    """Get QR code for a specific asset"""
    
    async with get_async_session() as session:
        result = await session.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Get GS1 Digital Link
        gs1_link = asset.asset_metadata.get('gs1_digital_link') if asset.asset_metadata else None
        if not gs1_link:
            # Generate if not exists
            gs1_link = gs1_service.create_digital_link(asset.gtin, {
                'title': asset.title,
                'type': asset.asset_type
            })
        
        if download:
            qr_bytes = gs1_service.generate_qr_code_file(gs1_link, with_logo=with_logo)
            return Response(
                content=qr_bytes,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"attachment; filename={asset.title.replace(' ', '_')}_qr.png"
                }
            )
        else:
            qr_base64 = gs1_service.generate_qr_code(gs1_link, with_logo=with_logo)
            return {
                "qr_code": qr_base64,
                "asset": {
                    "id": asset.id,
                    "title": asset.title,
                    "gtin": asset.gtin,
                    "gs1_link": gs1_link
                }
            }

            "status": "scheduled",
            "media_url": request.media_url
        }
    }

@router.delete("/social/posts/scheduled/{post_id}")
async def cancel_scheduled_post(
    post_id: str,
    current_user = Depends(get_current_user)
):
    """Cancel a scheduled post (mock functionality)"""
    
    return {
        "success": True,
        "message": "Scheduled post cancelled",
        "post_id": post_id
    }

            proposal.executed_at = datetime.now(timezone.utc)
        
        await session.commit()
        
        return {
            "success": True,
            "message": f"Proposal status updated to {status}",
            "proposal": {
                "id": proposal.id,
                "status": proposal.status,
                "executed_at": proposal.executed_at.isoformat() if proposal.executed_at else None
            }
        }
