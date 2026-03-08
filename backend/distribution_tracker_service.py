"""
Big Mann Entertainment - Distribution Tracker Service
Phase 2: Content & Distribution Modules - Distribution Tracker Backend
"""

import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistributionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    REMOVED = "removed"

class PlatformCategory(str, Enum):
    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_STREAMING = "video_streaming"
    PODCAST = "podcast"
    RADIO = "radio"
    TELEVISION = "television"
    BLOCKCHAIN = "blockchain"
    OTHER = "other"

class DeliveryPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Pydantic Models
class PlatformInfo(BaseModel):
    id: str
    name: str
    category: PlatformCategory
    api_endpoint: Optional[str] = None
    max_file_size: Optional[int] = None
    supported_formats: List[str] = Field(default_factory=list)
    delivery_time_estimate: Optional[str] = "2-4 hours"
    status: str = "active"
    last_successful_delivery: Optional[datetime] = None
    error_rate: float = 0.0

class DistributionJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    asset_title: str
    platforms: List[str]  # Platform IDs
    status: DistributionStatus
    priority: DeliveryPriority
    submitted_by: str
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    total_platforms: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    estimated_completion: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PlatformDelivery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    platform_id: str
    platform_name: str
    asset_id: str
    status: DistributionStatus
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    platform_response: Dict[str, Any] = Field(default_factory=dict)
    external_id: Optional[str] = None  # Platform's ID for the content

class DistributionAnalytics(BaseModel):
    total_jobs: int = 0
    active_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    success_rate: float = 0.0
    average_delivery_time: float = 0.0  # in hours
    platform_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    daily_stats: Dict[str, int] = Field(default_factory=dict)

class DistributionTrackerService:
    """Service for tracking content distribution across platforms"""
    
    def __init__(self):
        self.jobs_cache = {}
        self.deliveries_cache = {}
        self.platforms = self._initialize_platforms()
    
    def _initialize_platforms(self) -> Dict[str, PlatformInfo]:
        """Initialize platform information"""
        platforms = {
            # Social Media Platforms
            "instagram": PlatformInfo(
                id="instagram",
                name="Instagram",
                category=PlatformCategory.SOCIAL_MEDIA,
                api_endpoint="https://graph.facebook.com/v18.0",
                max_file_size=100 * 1024 * 1024,  # 100MB
                supported_formats=["jpg", "png", "mp4", "gif"],
                delivery_time_estimate="1-2 hours"
            ),
            "tiktok": PlatformInfo(
                id="tiktok",
                name="TikTok",
                category=PlatformCategory.SOCIAL_MEDIA,
                api_endpoint="https://open-api.tiktok.com/v1.3",
                max_file_size=72 * 1024 * 1024,  # 72MB
                supported_formats=["mp4"],
                delivery_time_estimate="2-4 hours"
            ),
            "fansly": PlatformInfo(
                id="fansly",
                name="Fansly",
                category=PlatformCategory.SOCIAL_MEDIA,
                api_endpoint="https://apiv3.fansly.com/api/v1",
                max_file_size=500 * 1024 * 1024,  # 500MB
                supported_formats=["jpg", "png", "mp4", "mp3", "gif"],
                delivery_time_estimate="1-2 hours"
            ),
            "youtube": PlatformInfo(
                id="youtube",
                name="YouTube",
                category=PlatformCategory.VIDEO_STREAMING,
                api_endpoint="https://www.googleapis.com/youtube/v3",
                max_file_size=256 * 1024 * 1024,  # 256MB
                supported_formats=["mp4", "mov", "avi"],
                delivery_time_estimate="1-3 hours"
            ),
            
            # Music Streaming Platforms
            "spotify": PlatformInfo(
                id="spotify",
                name="Spotify",
                category=PlatformCategory.MUSIC_STREAMING,
                api_endpoint="https://api.spotify.com/v1",
                max_file_size=50 * 1024 * 1024,  # 50MB
                supported_formats=["mp3", "wav", "flac"],
                delivery_time_estimate="4-6 hours"
            ),
            "apple_music": PlatformInfo(
                id="apple_music",
                name="Apple Music",
                category=PlatformCategory.MUSIC_STREAMING,
                api_endpoint="https://api.music.apple.com/v1",
                max_file_size=50 * 1024 * 1024,  # 50MB
                supported_formats=["mp3", "wav", "m4a"],
                delivery_time_estimate="6-8 hours"
            ),
            "amazon_music": PlatformInfo(
                id="amazon_music",
                name="Amazon Music",
                category=PlatformCategory.MUSIC_STREAMING,
                max_file_size=50 * 1024 * 1024,  # 50MB
                supported_formats=["mp3", "wav", "flac"],
                delivery_time_estimate="4-6 hours"
            ),
            
            # Additional platforms
            "netflix": PlatformInfo(
                id="netflix",
                name="Netflix",
                category=PlatformCategory.VIDEO_STREAMING,
                max_file_size=2 * 1024 * 1024 * 1024,  # 2GB
                supported_formats=["mp4", "mov"],
                delivery_time_estimate="12-24 hours"
            )
        }
        return platforms
    
    async def create_distribution_job(self, asset_id: str, asset_title: str, 
                                    platforms: List[str], user_id: str,
                                    priority: DeliveryPriority = DeliveryPriority.NORMAL) -> Dict[str, Any]:
        """Create a new distribution job"""
        try:
            # Validate platforms
            invalid_platforms = [p for p in platforms if p not in self.platforms]
            if invalid_platforms:
                return {
                    "success": False,
                    "error": f"Invalid platforms: {', '.join(invalid_platforms)}"
                }
            
            job = DistributionJob(
                asset_id=asset_id,
                asset_title=asset_title,
                platforms=platforms,
                status=DistributionStatus.PENDING,
                priority=priority,
                submitted_by=user_id,
                total_platforms=len(platforms),
                estimated_completion=datetime.now(timezone.utc) + timedelta(hours=6)
            )
            
            # Store job
            self.jobs_cache[job.id] = job
            
            # Create individual platform deliveries
            for platform_id in platforms:
                platform = self.platforms[platform_id]
                delivery = PlatformDelivery(
                    job_id=job.id,
                    platform_id=platform_id,
                    platform_name=platform.name,
                    asset_id=asset_id,
                    status=DistributionStatus.PENDING
                )
                self.deliveries_cache[delivery.id] = delivery
            
            logger.info(f"Created distribution job {job.id} for asset {asset_id}")
            
            return {
                "success": True,
                "job_id": job.id,
                "message": f"Distribution job created for {len(platforms)} platforms",
                "estimated_completion": job.estimated_completion.isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating distribution job: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_distribution_jobs(self, user_id: str, status: DistributionStatus = None,
                                  limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get distribution jobs for a user"""
        try:
            # Sample jobs for demo
            sample_jobs = [
                DistributionJob(
                    id="job_001",
                    asset_id="asset_001",
                    asset_title="Summer Vibes Instrumental",
                    platforms=["spotify", "apple_music", "youtube", "instagram"],
                    status=DistributionStatus.DELIVERED,
                    priority=DeliveryPriority.NORMAL,
                    submitted_by=user_id,
                    progress=100.0,
                    total_platforms=4,
                    successful_deliveries=4,
                    failed_deliveries=0,
                    completed_at=datetime.now(timezone.utc) - timedelta(hours=2)
                ),
                DistributionJob(
                    id="job_002",
                    asset_id="asset_002",
                    asset_title="Brand Logo Animation",
                    platforms=["youtube", "tiktok", "instagram"],
                    status=DistributionStatus.PROCESSING,
                    priority=DeliveryPriority.HIGH,
                    submitted_by=user_id,
                    progress=66.7,
                    total_platforms=3,
                    successful_deliveries=2,
                    failed_deliveries=0,
                    started_at=datetime.now(timezone.utc) - timedelta(minutes=30)
                ),
                DistributionJob(
                    id="job_003",
                    asset_id="asset_003",
                    asset_title="Artist Portrait",
                    platforms=["instagram", "tiktok"],
                    status=DistributionStatus.FAILED,
                    priority=DeliveryPriority.NORMAL,
                    submitted_by=user_id,
                    progress=50.0,
                    total_platforms=2,
                    successful_deliveries=1,
                    failed_deliveries=1,
                    completed_at=datetime.now(timezone.utc) - timedelta(hours=1)
                )
            ]
            
            # Apply filters
            filtered_jobs = sample_jobs
            if status:
                filtered_jobs = [j for j in filtered_jobs if j.status == status]
            
            # Apply pagination
            total = len(filtered_jobs)
            jobs = filtered_jobs[offset:offset + limit]
            
            return {
                "success": True,
                "jobs": [job.dict() for job in jobs],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error fetching distribution jobs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "jobs": [],
                "total": 0
            }
    
    async def get_distribution_job(self, job_id: str, user_id: str) -> Dict[str, Any]:
        """Get a specific distribution job with details"""
        try:
            # Sample job details
            job = DistributionJob(
                id=job_id,
                asset_id="asset_001",
                asset_title="Summer Vibes Instrumental",
                platforms=["spotify", "apple_music", "youtube", "instagram"],
                status=DistributionStatus.DELIVERED,
                priority=DeliveryPriority.NORMAL,
                submitted_by=user_id,
                progress=100.0,
                total_platforms=4,
                successful_deliveries=4,
                failed_deliveries=0,
                completed_at=datetime.now(timezone.utc) - timedelta(hours=2)
            )
            
            # Sample platform deliveries
            deliveries = [
                PlatformDelivery(
                    id="delivery_001",
                    job_id=job_id,
                    platform_id="spotify",
                    platform_name="Spotify",
                    asset_id="asset_001",
                    status=DistributionStatus.DELIVERED,
                    delivered_at=datetime.now(timezone.utc) - timedelta(hours=2),
                    external_id="spotify_track_123456"
                ),
                PlatformDelivery(
                    id="delivery_002",
                    job_id=job_id,
                    platform_id="apple_music",
                    platform_name="Apple Music",
                    asset_id="asset_001",
                    status=DistributionStatus.DELIVERED,
                    delivered_at=datetime.now(timezone.utc) - timedelta(hours=1),
                    external_id="apple_song_789012"
                ),
                PlatformDelivery(
                    id="delivery_003",
                    job_id=job_id,
                    platform_id="youtube",
                    platform_name="YouTube",
                    asset_id="asset_001",
                    status=DistributionStatus.DELIVERED,
                    delivered_at=datetime.now(timezone.utc) - timedelta(minutes=30),
                    external_id="youtube_video_345678"
                ),
                PlatformDelivery(
                    id="delivery_004",
                    job_id=job_id,
                    platform_id="instagram",
                    platform_name="Instagram",
                    asset_id="asset_001",
                    status=DistributionStatus.DELIVERED,
                    delivered_at=datetime.now(timezone.utc) - timedelta(minutes=15),
                    external_id="instagram_media_901234"
                )
            ]
            
            return {
                "success": True,
                "job": job.dict(),
                "deliveries": [delivery.dict() for delivery in deliveries]
            }
        except Exception as e:
            logger.error(f"Error fetching distribution job {job_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_platforms(self, category: PlatformCategory = None) -> Dict[str, Any]:
        """Get available distribution platforms"""
        try:
            platforms = list(self.platforms.values())
            
            if category:
                platforms = [p for p in platforms if p.category == category]
            
            return {
                "success": True,
                "platforms": [platform.dict() for platform in platforms],
                "total": len(platforms)
            }
        except Exception as e:
            logger.error(f"Error fetching platforms: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platforms": []
            }
    
    async def get_distribution_analytics(self, user_id: str, 
                                       start_date: datetime = None,
                                       end_date: datetime = None) -> Dict[str, Any]:
        """Get distribution analytics"""
        try:
            analytics = DistributionAnalytics(
                total_jobs=156,
                active_jobs=3,
                completed_jobs=145,
                failed_jobs=8,
                success_rate=93.6,
                average_delivery_time=4.2,
                platform_performance={
                    "spotify": {"success_rate": 98.5, "avg_delivery_time": 5.1},
                    "apple_music": {"success_rate": 96.2, "avg_delivery_time": 6.8},
                    "youtube": {"success_rate": 94.1, "avg_delivery_time": 2.3},
                    "instagram": {"success_rate": 91.7, "avg_delivery_time": 1.8},
                    "tiktok": {"success_rate": 89.3, "avg_delivery_time": 3.2}
                },
                daily_stats={
                    "today": 12,
                    "yesterday": 18,
                    "week_ago": 15,
                    "month_ago": 23
                }
            )
            
            return {
                "success": True,
                "analytics": analytics.dict()
            }
        except Exception as e:
            logger.error(f"Error fetching distribution analytics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def retry_failed_delivery(self, delivery_id: str, user_id: str) -> Dict[str, Any]:
        """Retry a failed platform delivery"""
        try:
            # In production, this would retry the actual delivery
            logger.info(f"Retrying delivery {delivery_id} for user {user_id}")
            
            return {
                "success": True,
                "message": "Delivery retry initiated"
            }
        except Exception as e:
            logger.error(f"Error retrying delivery {delivery_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_distribution_job(self, job_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel a pending or processing distribution job"""
        try:
            # In production, this would cancel the job and pending deliveries
            logger.info(f"Cancelled distribution job {job_id} for user {user_id}")
            
            return {
                "success": True,
                "message": "Distribution job cancelled"
            }
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
distribution_tracker_service = DistributionTrackerService()