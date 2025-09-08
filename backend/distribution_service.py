import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import json
from decimal import Decimal
import motor.motor_asyncio
from pydantic import BaseModel
import os

logger = logging.getLogger(__name__)

class DistributionPlatform(BaseModel):
    id: str
    name: str
    category: str  # streaming, social, broadcast, etc.
    revenue_share: float  # Platform's revenue share (0.0 to 1.0)
    minimum_payout: float
    processing_time_days: int
    supported_formats: List[str]
    geographic_availability: List[str]
    is_active: bool = True

class DistributionStatus(BaseModel):
    platform: str
    status: str  # pending, submitted, live, rejected, removed
    submission_id: Optional[str] = None
    go_live_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    streams: int = 0
    revenue: float = 0.0
    last_updated: datetime

class EarningsRecord(BaseModel):
    media_id: str
    platform: str
    streams: int
    revenue: float
    reporting_period: str  # YYYY-MM format
    currency: str = "USD"
    recorded_at: datetime

class PayoutRequest(BaseModel):
    id: str
    user_id: str
    amount: float
    method: str  # paypal, stripe, bank_transfer
    details: str
    status: str  # pending, processing, completed, failed
    processing_fee: float
    net_amount: float
    requested_at: datetime
    processed_at: Optional[datetime] = None

class DistributionService:
    """Comprehensive distribution service for Big Mann Entertainment"""
    
    def __init__(self, db):
        self.db = db
        self.platforms = {}
        self.initialize_platforms()
    
    def initialize_platforms(self):
        """Initialize available distribution platforms"""
        self.platforms = {
            # Music Streaming Platforms
            "spotify": DistributionPlatform(
                id="spotify",
                name="Spotify",
                category="streaming",
                revenue_share=0.70,
                minimum_payout=1.00,
                processing_time_days=7,
                supported_formats=["mp3", "wav", "flac"],
                geographic_availability=["global"],
                is_active=True
            ),
            "apple_music": DistributionPlatform(
                id="apple_music",
                name="Apple Music",
                category="streaming",
                revenue_share=0.68,
                minimum_payout=1.00,
                processing_time_days=5,
                supported_formats=["mp3", "m4a", "wav"],
                geographic_availability=["global"],
                is_active=True
            ),
            "youtube_music": DistributionPlatform(
                id="youtube_music",
                name="YouTube Music",
                category="streaming",
                revenue_share=0.55,
                minimum_payout=0.50,
                processing_time_days=3,
                supported_formats=["mp3", "wav", "mp4"],
                geographic_availability=["global"],
                is_active=True
            ),
            "amazon_music": DistributionPlatform(
                id="amazon_music",
                name="Amazon Music",
                category="streaming",
                revenue_share=0.66,
                minimum_payout=1.00,
                processing_time_days=10,
                supported_formats=["mp3", "wav"],
                geographic_availability=["us", "uk", "ca", "au", "de", "fr"],
                is_active=True
            ),
            "tidal": DistributionPlatform(
                id="tidal",
                name="Tidal",
                category="streaming",
                revenue_share=0.75,
                minimum_payout=2.00,
                processing_time_days=14,
                supported_formats=["flac", "wav", "mp3"],
                geographic_availability=["global"],
                is_active=True
            ),
            
            # Social Media Platforms
            "tiktok": DistributionPlatform(
                id="tiktok",
                name="TikTok",
                category="social",
                revenue_share=0.50,
                minimum_payout=0.25,
                processing_time_days=2,
                supported_formats=["mp3", "mp4"],
                geographic_availability=["global"],
                is_active=True
            ),
            "instagram": DistributionPlatform(
                id="instagram",
                name="Instagram",
                category="social",
                revenue_share=0.45,
                minimum_payout=0.25,
                processing_time_days=1,
                supported_formats=["mp3", "mp4"],
                geographic_availability=["global"],
                is_active=True
            ),
            "facebook": DistributionPlatform(
                id="facebook",
                name="Facebook",
                category="social",
                revenue_share=0.45,
                minimum_payout=0.25,
                processing_time_days=1,
                supported_formats=["mp3", "mp4"],
                geographic_availability=["global"],
                is_active=True
            ),
            
            # Video Platforms
            "youtube": DistributionPlatform(
                id="youtube",
                name="YouTube",
                category="video",
                revenue_share=0.55,
                minimum_payout=0.10,
                processing_time_days=1,
                supported_formats=["mp4", "mov", "avi"],
                geographic_availability=["global"],
                is_active=True
            ),
            "vimeo": DistributionPlatform(
                id="vimeo",
                name="Vimeo",
                category="video",
                revenue_share=0.60,
                minimum_payout=1.00,
                processing_time_days=7,
                supported_formats=["mp4", "mov"],
                geographic_availability=["global"],
                is_active=True
            ),
            
            # Radio & Broadcast
            "iheartradio": DistributionPlatform(
                id="iheartradio",
                name="iHeartRadio",
                category="radio",
                revenue_share=0.65,
                minimum_payout=5.00,
                processing_time_days=21,
                supported_formats=["mp3", "wav"],
                geographic_availability=["us", "ca", "au"],
                is_active=True
            ),
            "pandora": DistributionPlatform(
                id="pandora",
                name="Pandora",
                category="radio",
                revenue_share=0.70,
                minimum_payout=5.00,
                processing_time_days=30,
                supported_formats=["mp3", "wav"],
                geographic_availability=["us"],
                is_active=True
            )
        }
    
    async def submit_for_distribution(self, media_id: str, user_id: str, platforms: List[str], metadata: Dict = None) -> Dict:
        """Submit media for distribution to selected platforms"""
        try:
            # Validate media exists and belongs to user
            media = await self.db.media_uploads.find_one({
                "id": media_id,
                "user_id": user_id
            })
            
            if not media:
                raise ValueError("Media not found or access denied")
            
            # Validate platforms
            invalid_platforms = [p for p in platforms if p not in self.platforms]
            if invalid_platforms:
                raise ValueError(f"Invalid platforms: {invalid_platforms}")
            
            # Create distribution record
            distribution_id = str(uuid.uuid4())
            distribution_statuses = []
            
            for platform_id in platforms:
                platform = self.platforms[platform_id]
                
                # Check format compatibility
                file_extension = media["file_path"].split('.')[-1].lower()
                if file_extension not in platform.supported_formats:
                    status = DistributionStatus(
                        platform=platform_id,
                        status="rejected",
                        rejection_reason=f"Unsupported format: {file_extension}",
                        last_updated=datetime.utcnow()
                    )
                else:
                    # Simulate platform submission
                    submission_id = f"{platform_id}_{str(uuid.uuid4())[:8]}"
                    go_live_date = datetime.utcnow() + timedelta(days=platform.processing_time_days)
                    
                    status = DistributionStatus(
                        platform=platform_id,
                        status="submitted",
                        submission_id=submission_id,
                        go_live_date=go_live_date,
                        last_updated=datetime.utcnow()
                    )
                
                distribution_statuses.append(status.dict())
            
            # Store distribution record
            distribution_record = {
                "id": distribution_id,
                "media_id": media_id,
                "user_id": user_id,
                "platforms": platforms,
                "status": "submitted",
                "distribution_statuses": distribution_statuses,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.db.distributions.insert_one(distribution_record)
            
            return {
                "distribution_id": distribution_id,
                "platforms_submitted": len([s for s in distribution_statuses if s["status"] == "submitted"]),
                "platforms_rejected": len([s for s in distribution_statuses if s["status"] == "rejected"]),
                "statuses": distribution_statuses
            }
            
        except Exception as e:
            logger.error(f"Distribution submission error: {str(e)}")
            raise
    
    async def update_distribution_status(self, distribution_id: str, platform: str, status: str, metadata: Dict = None):
        """Update distribution status for a specific platform"""
        try:
            update_data = {
                "distribution_statuses.$.status": status,
                "distribution_statuses.$.last_updated": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if metadata:
                for key, value in metadata.items():
                    update_data[f"distribution_statuses.$.{key}"] = value
            
            result = await self.db.distributions.update_one(
                {
                    "id": distribution_id,
                    "distribution_statuses.platform": platform
                },
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Status update error: {str(e)}")
            raise
    
    async def simulate_earnings(self, days_back: int = 30):
        """Simulate earnings data for testing purposes"""
        try:
            # Get all live distributions
            pipeline = [
                {"$match": {"status": "submitted"}},
                {"$unwind": "$distribution_statuses"},
                {"$match": {"distribution_statuses.status": {"$in": ["submitted", "live"]}}},
                {"$project": {
                    "distribution_id": "$id",
                    "media_id": 1,
                    "user_id": 1,
                    "platform": "$distribution_statuses.platform",
                    "status": "$distribution_statuses.status"
                }}
            ]
            
            distributions = await self.db.distributions.aggregate(pipeline).to_list(length=None)
            
            earnings_records = []
            
            for dist in distributions:
                # Simulate varying performance
                base_streams = 100 + (hash(dist["media_id"]) % 1000)
                platform_multiplier = {
                    "spotify": 1.5,
                    "apple_music": 1.2,
                    "youtube_music": 2.0,
                    "tiktok": 5.0,
                    "instagram": 3.0,
                    "youtube": 0.8
                }.get(dist["platform"], 1.0)
                
                streams = int(base_streams * platform_multiplier)
                
                # Calculate revenue based on platform rates
                platform_info = self.platforms.get(dist["platform"])
                if platform_info:
                    revenue_per_stream = 0.003 * platform_info.revenue_share
                    revenue = streams * revenue_per_stream
                    
                    earnings_record = EarningsRecord(
                        media_id=dist["media_id"],
                        platform=dist["platform"],
                        streams=streams,
                        revenue=revenue,
                        reporting_period=datetime.utcnow().strftime("%Y-%m"),
                        recorded_at=datetime.utcnow()
                    )
                    
                    earnings_records.append(earnings_record.dict())
            
            # Store earnings records
            if earnings_records:
                await self.db.earnings.insert_many(earnings_records)
            
            return len(earnings_records)
            
        except Exception as e:
            logger.error(f"Earnings simulation error: {str(e)}")
            raise
    
    async def get_user_earnings(self, user_id: str, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Get comprehensive earnings data for a user"""
        try:
            # Build aggregation pipeline
            match_stage = {"user_id": user_id}
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                match_stage["recorded_at"] = date_filter
            
            # Get user's media IDs
            user_media = await self.db.media_uploads.find({"user_id": user_id}).to_list(length=None)
            media_ids = [media["id"] for media in user_media]
            
            if not media_ids:
                return {
                    "total_earnings": 0.0,
                    "total_streams": 0,
                    "platform_breakdown": {},
                    "media_breakdown": {},
                    "recent_earnings": []
                }
            
            # Aggregate earnings
            pipeline = [
                {"$match": {"media_id": {"$in": media_ids}}},
                {"$group": {
                    "_id": None,
                    "total_earnings": {"$sum": "$revenue"},
                    "total_streams": {"$sum": "$streams"},
                    "platform_earnings": {
                        "$push": {
                            "platform": "$platform",
                            "earnings": "$revenue",
                            "streams": "$streams"
                        }
                    },
                    "media_earnings": {
                        "$push": {
                            "media_id": "$media_id",
                            "earnings": "$revenue",
                            "streams": "$streams"
                        }
                    }
                }}
            ]
            
            result = await self.db.earnings.aggregate(pipeline).to_list(length=1)
            
            if not result:
                return {
                    "total_earnings": 0.0,
                    "total_streams": 0,
                    "platform_breakdown": {},
                    "media_breakdown": {},
                    "recent_earnings": []
                }
            
            data = result[0]
            
            # Process platform breakdown
            platform_breakdown = {}
            for item in data["platform_earnings"]:
                platform = item["platform"]
                if platform not in platform_breakdown:
                    platform_breakdown[platform] = {"earnings": 0.0, "streams": 0}
                platform_breakdown[platform]["earnings"] += item["earnings"]
                platform_breakdown[platform]["streams"] += item["streams"]
            
            # Process media breakdown
            media_breakdown = {}
            for item in data["media_earnings"]:
                media_id = item["media_id"]
                if media_id not in media_breakdown:
                    media_breakdown[media_id] = {"earnings": 0.0, "streams": 0}
                media_breakdown[media_id]["earnings"] += item["earnings"]
                media_breakdown[media_id]["streams"] += item["streams"]
            
            # Add media titles
            for media_id, breakdown in media_breakdown.items():
                media_info = next((m for m in user_media if m["id"] == media_id), None)
                if media_info:
                    breakdown["title"] = media_info["title"]
            
            return {
                "total_earnings": round(data["total_earnings"], 2),
                "total_streams": data["total_streams"],
                "platform_breakdown": platform_breakdown,
                "media_breakdown": media_breakdown,
                "recent_earnings": []  # Could add recent earnings query here
            }
            
        except Exception as e:
            logger.error(f"Get earnings error: {str(e)}")
            raise
    
    async def process_payout_request(self, user_id: str, amount: float, method: str, details: str) -> Dict:
        """Process a payout request"""
        try:
            # Get user's available balance
            earnings_data = await self.get_user_earnings(user_id)
            available_balance = earnings_data["total_earnings"]
            
            # Check for pending payouts
            pending_payouts = await self.db.payout_requests.find({
                "user_id": user_id,
                "status": {"$in": ["pending", "processing"]}
            }).to_list(length=None)
            
            pending_amount = sum(p["amount"] for p in pending_payouts)
            available_balance -= pending_amount
            
            if amount > available_balance:
                raise ValueError(f"Insufficient balance. Available: ${available_balance:.2f}")
            
            # Calculate processing fee
            fee_rate = {
                "paypal": 0.025,  # 2.5%
                "stripe": 0.029,  # 2.9%
                "bank_transfer": 0.015  # 1.5%
            }.get(method, 0.03)
            
            processing_fee = amount * fee_rate
            net_amount = amount - processing_fee
            
            # Create payout request
            payout_id = str(uuid.uuid4())
            payout_request = PayoutRequest(
                id=payout_id,
                user_id=user_id,
                amount=amount,
                method=method,
                details=details,
                status="pending",
                processing_fee=processing_fee,
                net_amount=net_amount,
                requested_at=datetime.utcnow()
            )
            
            await self.db.payout_requests.insert_one(payout_request.dict())
            
            return {
                "payout_id": payout_id,
                "amount": amount,
                "processing_fee": processing_fee,
                "net_amount": net_amount,
                "status": "pending",
                "estimated_processing_time": "3-5 business days"
            }
            
        except Exception as e:
            logger.error(f"Payout request error: {str(e)}")
            raise
    
    async def get_platform_analytics(self, user_id: str) -> Dict:
        """Get analytics for all platforms"""
        try:
            # Get user's distributions
            distributions = await self.db.distributions.find({"user_id": user_id}).to_list(length=None)
            
            platform_analytics = {}
            
            for platform_id, platform_info in self.platforms.items():
                # Count distributions to this platform
                platform_distributions = [
                    d for d in distributions 
                    if platform_id in d.get("platforms", [])
                ]
                
                live_count = 0
                pending_count = 0
                rejected_count = 0
                
                for dist in platform_distributions:
                    for status in dist.get("distribution_statuses", []):
                        if status["platform"] == platform_id:
                            if status["status"] == "live":
                                live_count += 1
                            elif status["status"] in ["submitted", "pending"]:
                                pending_count += 1
                            elif status["status"] == "rejected":
                                rejected_count += 1
                
                platform_analytics[platform_id] = {
                    "name": platform_info.name,
                    "category": platform_info.category,
                    "total_submissions": len(platform_distributions),
                    "live_content": live_count,
                    "pending_content": pending_count,
                    "rejected_content": rejected_count,
                    "revenue_share": platform_info.revenue_share,
                    "minimum_payout": platform_info.minimum_payout
                }
            
            return platform_analytics
            
        except Exception as e:
            logger.error(f"Platform analytics error: {str(e)}")
            raise