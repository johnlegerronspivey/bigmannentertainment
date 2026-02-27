"""
Profile Service
Aggregates data from MongoDB and PostgreSQL for creator profiles
"""
from typing import Optional, Dict, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from profile_models import (
    UserProfile, Asset, Royalty, Sponsor, TraceEvent, 
    Comment, Proposal, Vote
)
from pg_database import get_async_session
from gs1_profile_service import gs1_service
from datetime import datetime, timezone
import os

# MongoDB connection (from existing server.py)
from config.database import db

class ProfileService:
    """Service for managing creator profiles"""
    
    async def get_profile_by_username(self, username: str) -> Optional[Dict]:
        """
        Get complete profile data by username
        Aggregates from both MongoDB and PostgreSQL
        """
        async with get_async_session() as session:
            # Get user profile from PostgreSQL
            result = await session.execute(
                select(UserProfile)
                .options(
                    selectinload(UserProfile.assets),
                    selectinload(UserProfile.royalties),
                    selectinload(UserProfile.sponsors),
                    selectinload(UserProfile.trace_events),
                    selectinload(UserProfile.comments)
                )
                .where(UserProfile.username == username)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return None
            
            # Get MongoDB user data for additional info
            mongo_user = await db.users.find_one({"_id": profile.mongo_user_id})
            
            # Build response
            return await self._build_profile_response(profile, mongo_user, session)
    
    async def get_profile_by_mongo_id(self, mongo_user_id: str) -> Optional[Dict]:
        """Get profile by MongoDB user ID"""
        async with get_async_session() as session:
            result = await session.execute(
                select(UserProfile)
                .options(
                    selectinload(UserProfile.assets),
                    selectinload(UserProfile.royalties),
                    selectinload(UserProfile.sponsors),
                    selectinload(UserProfile.trace_events),
                    selectinload(UserProfile.comments)
                )
                .where(UserProfile.mongo_user_id == mongo_user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return None
            
            mongo_user = await db.users.find_one({"_id": mongo_user_id})
            
            return await self._build_profile_response(profile, mongo_user, session)
    
    async def create_profile(self, mongo_user_id: str, username: str, data: Dict) -> UserProfile:
        """Create new profile"""
        async with get_async_session() as session:
            # Generate GLN for user
            gln = gs1_service.generate_gln_for_location()
            
            profile = UserProfile(
                mongo_user_id=mongo_user_id,
                username=username,
                display_name=data.get('display_name', username),
                avatar_url=data.get('avatar_url'),
                tagline=data.get('tagline'),
                bio=data.get('bio'),
                gln=gln,
                gtin_prefix=gs1_service.company_prefix,
                location=data.get('location', ''),
                social_links=data.get('social_links', []),
                profile_public=data.get('profile_public', True),
                show_earnings=data.get('show_earnings', False),
                show_dao_activity=data.get('show_dao_activity', True)
            )
            
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            
            return profile
    
    async def update_profile(self, username: str, data: Dict) -> Optional[UserProfile]:
        """Update existing profile"""
        async with get_async_session() as session:
            result = await session.execute(
                select(UserProfile).where(UserProfile.username == username)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return None
            
            # Update fields
            for key, value in data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.updated_at = datetime.now(timezone.utc)
            
            await session.commit()
            await session.refresh(profile)
            
            return profile
    
    async def create_asset(self, user_id: str, asset_data: Dict) -> Asset:
        """Create new asset with GS1 identifiers"""
        async with get_async_session() as session:
            # Generate appropriate GS1 identifier based on asset type
            asset_type = asset_data.get('asset_type', 'image')
            
            gtin = gs1_service.generate_gtin()
            gs1_link = gs1_service.create_digital_link(gtin, {
                'title': asset_data.get('title', ''),
                'type': asset_type
            })
            qr_code = gs1_service.generate_qr_code(gs1_link)
            
            # Type-specific identifiers
            isrc = None
            isan = None
            gdti = None
            
            if asset_type == 'music':
                isrc = gs1_service.generate_isrc()
            elif asset_type == 'video':
                isan = gs1_service.generate_isan()
            elif asset_type == 'image':
                gdti = gs1_service.generate_gdti()
            
            asset = Asset(
                user_id=user_id,
                mongo_media_id=asset_data.get('mongo_media_id'),
                title=asset_data['title'],
                description=asset_data.get('description', ''),
                asset_type=asset_type,
                thumbnail_url=asset_data.get('thumbnail_url'),
                content_url=asset_data.get('content_url'),
                gtin=gtin,
                isrc=isrc,
                isan=isan,
                gdti=gdti,
                license=asset_data.get('license', 'All Rights Reserved'),
                copyright_notice=asset_data.get('copyright_notice'),
                rights_holder=asset_data.get('rights_holder'),
                asset_metadata={
                    'gs1_digital_link': gs1_link,
                    'qr_code': qr_code
                }
            )
            
            session.add(asset)
            await session.commit()
            await session.refresh(asset)
            
            return asset
    
    async def _build_profile_response(self, profile: UserProfile, mongo_user: Optional[Dict], session) -> Dict:
        """Build complete profile response"""
        
        # Get DAO proposals and votes
        proposals_result = await session.execute(
            select(Proposal)
            .where(Proposal.user_id == profile.id)
            .order_by(Proposal.created_at.desc())
            .limit(10)
        )
        proposals = proposals_result.scalars().all()
        
        # Calculate total royalties
        total_royalties = sum(r.amount for r in profile.royalties)
        
        # Build assets list with GS1 metadata
        assets_list = []
        for asset in profile.assets:
            asset_dict = {
                "id": asset.id,
                "title": asset.title,
                "description": asset.description,
                "type": asset.asset_type,
                "thumbnail": asset.thumbnail_url,
                "content_url": asset.content_url,
                "gtin": asset.gtin,
                "isrc": asset.isrc,
                "isan": asset.isan,
                "gdti": asset.gdti,
                "gs1_digital_link": asset.asset_metadata.get('gs1_digital_link') if asset.asset_metadata else None,
                "qr_code": asset.asset_metadata.get('qr_code') if asset.asset_metadata else None,
                "license": asset.license,
                "copyright": asset.copyright_notice,
                "engagement": {
                    "views": asset.views,
                    "likes": asset.likes,
                    "shares": asset.shares,
                    "total": asset.engagement_count
                },
                "contract_status": asset.contract_status,
                "contract_address": asset.contract_address,
                "created_at": asset.created_at.isoformat() if asset.created_at else None
            }
            assets_list.append(asset_dict)
        
        # Build response
        return {
            "identity": {
                "username": profile.username,
                "displayName": profile.display_name,
                "avatarUrl": profile.avatar_url,
                "tagline": profile.tagline,
                "bio": profile.bio,
                "gs1Link": f"{gs1_service.base_url}/414/{profile.gln}",
                "gln": profile.gln,
                "gtinPrefix": profile.gtin_prefix,
                "location": profile.location,
                "socials": profile.social_links or [],
                "profilePublic": profile.profile_public,
                "showEarnings": profile.show_earnings,
                "email": mongo_user.get('email') if mongo_user else None
            },
            "assets": assets_list,
            "traceability": [
                {
                    "id": te.id,
                    "timestamp": te.timestamp.isoformat(),
                    "description": te.description,
                    "platform": te.platform,
                    "location": te.location,
                    "eventType": te.event_type
                }
                for te in profile.trace_events
            ],
            "royalties": {
                "total": total_royalties,
                "showPublic": profile.show_earnings,
                "contributors": [
                    {
                        "name": r.contributor_name,
                        "amount": r.amount,
                        "percentage": r.percentage,
                        "status": r.payment_status
                    }
                    for r in profile.royalties
                ] if profile.show_earnings else [],
                "sponsors": [
                    {
                        "name": s.name,
                        "logo": s.logo_url,
                        "website": s.website_url,
                        "active": s.active
                    }
                    for s in profile.sponsors
                ]
            },
            "dao": {
                "showActivity": profile.show_dao_activity,
                "proposals": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "type": p.proposal_type,
                        "status": p.status,
                        "votes": {
                            "yes": p.total_yes,
                            "no": p.total_no,
                            "abstain": p.total_abstain,
                            "total": p.total_votes
                        },
                        "createdAt": p.created_at.isoformat(),
                        "votingEndsAt": p.voting_ends_at.isoformat() if p.voting_ends_at else None
                    }
                    for p in proposals
                ] if profile.show_dao_activity else []
            },
            "sidebar": {
                "campaign": {
                    "title": profile.campaign_title,
                    "description": profile.campaign_description
                } if profile.campaign_title else None,
                "sponsors": [
                    {"name": s.name, "logo": s.logo_url}
                    for s in profile.sponsors
                    if s.active
                ],
                "comments": [
                    {
                        "id": c.id,
                        "text": c.text,
                        "commenterName": c.commenter_name,
                        "timestamp": c.timestamp.isoformat(),
                        "likes": c.likes
                    }
                    for c in sorted(profile.comments, key=lambda x: x.timestamp, reverse=True)[:10]
                ]
            },
            "stats": {
                "totalAssets": len(profile.assets),
                "totalRoyalties": total_royalties,
                "activeSponsors": len([s for s in profile.sponsors if s.active]),
                "daoProposals": len(proposals),
                "traceabilityEvents": len(profile.trace_events)
            }
        }

# Singleton instance
profile_service = ProfileService()
