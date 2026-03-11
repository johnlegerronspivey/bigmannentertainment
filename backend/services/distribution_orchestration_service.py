"""
Distribution Orchestration Service - Handles content delivery to multiple platforms
Manages routing logic, delivery methods, and platform-specific formatting
"""

import os
import uuid
import json
import asyncio
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from pymongo import MongoClient
import boto3
from pathlib import Path

class DeliveryMethod(str, Enum):
    ASPERA = "aspera"
    SIGNIANT = "signiant"
    SFTP = "sftp"
    API = "api"
    EMAIL = "email"
    EDI = "edi"

class DeliveryStatus(str, Enum):
    QUEUED = "queued"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    VERIFIED = "verified"

class PlatformType(str, Enum):
    LINEAR_TV = "linear_tv"
    OTT_STREAMING = "ott_streaming"
    SOCIAL_MEDIA = "social_media"
    DSP_MUSIC = "dsp_music"
    RADIO_BROADCAST = "radio_broadcast"

class DistributionJob(BaseModel):
    distribution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    version_id: str
    user_id: str
    
    # Target platform information
    platform_name: str
    platform_type: PlatformType
    delivery_profile_id: str
    
    # Delivery configuration
    delivery_method: DeliveryMethod
    api_endpoint: Optional[str] = None
    credentials: Dict[str, str] = {}
    
    # Content specifications
    source_files: List[Dict[str, str]] = []
    metadata_payload: Dict[str, Any] = {}
    
    # Delivery status
    status: DeliveryStatus = DeliveryStatus.QUEUED
    progress_percentage: float = 0.0
    
    # Delivery tracking
    delivery_started_at: Optional[datetime] = None
    delivery_completed_at: Optional[datetime] = None
    verification_completed_at: Optional[datetime] = None
    
    # Platform response
    platform_response: Dict[str, Any] = {}
    platform_content_id: Optional[str] = None
    delivery_receipt: Optional[str] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PlatformConnector(BaseModel):
    platform_name: str
    platform_type: PlatformType
    api_base_url: str
    authentication_method: str  # api_key, oauth, basic_auth
    required_credentials: List[str]
    supported_formats: List[str]
    max_file_size_mb: int
    metadata_requirements: List[str]
    
    # Platform-specific configuration
    upload_config: Dict[str, Any] = {}
    metadata_mapping: Dict[str, str] = {}
    response_format: Dict[str, Any] = {}

class DistributionOrchestrationService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        
        # Collections
        self.distribution_jobs_collection = self.db['distribution_jobs']
        self.platform_connectors_collection = self.db['platform_connectors']
        self.delivery_receipts_collection = self.db['delivery_receipts']
        
        # Initialize platform connectors
        self._initialize_platform_connectors()
        
        # AWS S3 client for file storage
        self.s3_client = boto3.client(
            's3',
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        ) if os.environ.get('AWS_ACCESS_KEY_ID') else None
        
        self.s3_bucket = os.environ.get('S3_BUCKET', 'bigmann-entertainment-media')
    
    def _initialize_platform_connectors(self):
        """Initialize platform connector configurations"""
        
        platform_configs = [
            # YouTube Connector
            {
                "platform_name": "YouTube",
                "platform_type": PlatformType.SOCIAL_MEDIA,
                "api_base_url": "https://www.googleapis.com/youtube/v3",
                "authentication_method": "oauth",
                "required_credentials": ["client_id", "client_secret", "access_token"],
                "supported_formats": ["mp4", "mov", "avi"],
                "max_file_size_mb": 256000,  # 256 GB
                "metadata_requirements": ["title", "description", "tags"],
                "upload_config": {
                    "upload_endpoint": "/videos",
                    "chunk_size": 8388608,  # 8 MB chunks
                    "resumable": True
                },
                "metadata_mapping": {
                    "title": "snippet.title",
                    "description": "snippet.description",
                    "tags": "snippet.tags",
                    "category": "snippet.categoryId"
                }
            },
            
            # Spotify Connector
            {
                "platform_name": "Spotify",
                "platform_type": PlatformType.DSP_MUSIC,
                "api_base_url": "https://api.spotify.com/v1",
                "authentication_method": "api_key",
                "required_credentials": ["client_id", "client_secret"],
                "supported_formats": ["wav", "flac", "mp3"],
                "max_file_size_mb": 200,
                "metadata_requirements": ["title", "artist", "album", "isrc"],
                "upload_config": {
                    "upload_endpoint": "/albums",
                    "requires_distributor": True
                },
                "metadata_mapping": {
                    "title": "name",
                    "artist": "artists[0].name",
                    "album": "album.name",
                    "isrc": "external_ids.isrc"
                }
            },
            
            # Instagram Connector
            {
                "platform_name": "Instagram",
                "platform_type": PlatformType.SOCIAL_MEDIA,
                "api_base_url": "https://graph.facebook.com/v18.0",
                "authentication_method": "oauth",
                "required_credentials": ["access_token", "page_id"],
                "supported_formats": ["mp4", "jpg", "png"],
                "max_file_size_mb": 100,
                "metadata_requirements": ["caption"],
                "upload_config": {
                    "upload_endpoint": "/{page_id}/media",
                    "publish_endpoint": "/{page_id}/media_publish"
                },
                "metadata_mapping": {
                    "caption": "caption",
                    "media_type": "media_type"
                }
            },
            
            # TikTok Connector
            {
                "platform_name": "TikTok",
                "platform_type": PlatformType.SOCIAL_MEDIA,
                "api_base_url": "https://open-api.tiktok.com",
                "authentication_method": "oauth",
                "required_credentials": ["access_token", "open_id"],
                "supported_formats": ["mp4"],
                "max_file_size_mb": 500,
                "metadata_requirements": ["text", "privacy_level"],
                "upload_config": {
                    "upload_endpoint": "/share/video/upload/",
                    "init_endpoint": "/share/video/init/",
                    "max_duration": 180
                },
                "metadata_mapping": {
                    "text": "post_info.title",
                    "privacy_level": "post_info.privacy_level"
                }
            },
            
            # Linear TV Connector (Generic)
            {
                "platform_name": "Linear TV Broadcast",
                "platform_type": PlatformType.LINEAR_TV,
                "api_base_url": "https://broadcast-delivery.example.com",
                "authentication_method": "basic_auth",
                "required_credentials": ["username", "password", "station_id"],
                "supported_formats": ["mov", "mxf"],
                "max_file_size_mb": 50000,  # 50 GB
                "metadata_requirements": ["title", "duration", "air_date", "eidr"],
                "upload_config": {
                    "delivery_method": "aspera",
                    "requires_slate": True,
                    "requires_captions": True
                }
            }
        ]
        
        # Insert platform connectors if they don't exist
        for config in platform_configs:
            existing = self.platform_connectors_collection.find_one({
                "platform_name": config["platform_name"]
            })
            
            if not existing:
                connector = PlatformConnector(**config)
                connector_dict = connector.dict()
                self.platform_connectors_collection.insert_one(connector_dict)
    
    async def create_distribution_job(self,
                                    content_id: str,
                                    version_id: str,
                                    user_id: str,
                                    platform_name: str,
                                    delivery_profile_id: str,
                                    source_files: List[Dict[str, str]],
                                    metadata: Dict[str, Any]) -> DistributionJob:
        """Create a new distribution job"""
        
        try:
            # Get platform connector
            connector = self.platform_connectors_collection.find_one({
                "platform_name": platform_name
            })
            
            if not connector:
                raise ValueError(f"Platform connector not found: {platform_name}")
            
            # Get delivery profile
            delivery_profile = self.db['delivery_profiles'].find_one({
                "profile_id": delivery_profile_id
            })
            
            if not delivery_profile:
                raise ValueError(f"Delivery profile not found: {delivery_profile_id}")
            
            # Determine delivery method
            delivery_method = DeliveryMethod.API  # Default
            if delivery_profile.get("delivery_method"):
                delivery_method = DeliveryMethod(delivery_profile["delivery_method"])
            
            # Create distribution job
            job = DistributionJob(
                content_id=content_id,
                version_id=version_id,
                user_id=user_id,
                platform_name=platform_name,
                platform_type=PlatformType(connector["platform_type"]),
                delivery_profile_id=delivery_profile_id,
                delivery_method=delivery_method,
                api_endpoint=connector.get("api_base_url"),
                source_files=source_files,
                metadata_payload=metadata
            )
            
            # Store job in database
            job_dict = job.dict()
            job_dict["created_at"] = job.created_at.isoformat()
            job_dict["updated_at"] = job.updated_at.isoformat()
            
            result = self.distribution_jobs_collection.insert_one(job_dict)
            job.distribution_id = str(result.inserted_id)
            
            # Update with distribution_id
            self.distribution_jobs_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"distribution_id": job.distribution_id}}
            )
            
            print(f"✅ Distribution job created: {job.distribution_id}")
            return job
            
        except Exception as e:
            print(f"❌ Error creating distribution job: {e}")
            raise
    
    async def execute_distribution_job(self, distribution_id: str) -> bool:
        """Execute a distribution job"""
        
        try:
            # Get job from database
            job_data = self.distribution_jobs_collection.find_one({
                "distribution_id": distribution_id
            })
            
            if not job_data:
                raise ValueError("Distribution job not found")
            
            job = DistributionJob(**job_data)
            
            # Update job status
            await self._update_job_status(distribution_id, DeliveryStatus.PREPARING, 10.0)
            
            # Get platform connector
            connector = self.platform_connectors_collection.find_one({
                "platform_name": job.platform_name
            })
            
            # Execute based on delivery method
            if job.delivery_method == DeliveryMethod.API:
                success = await self._deliver_via_api(job, connector)
            elif job.delivery_method == DeliveryMethod.SFTP:
                success = await self._deliver_via_sftp(job, connector)
            elif job.delivery_method == DeliveryMethod.EMAIL:
                success = await self._deliver_via_email(job, connector)
            else:
                raise ValueError(f"Unsupported delivery method: {job.delivery_method}")
            
            if success:
                await self._update_job_status(distribution_id, DeliveryStatus.DELIVERED, 90.0)
                
                # Verify delivery if supported
                if await self._verify_delivery(job, connector):
                    await self._update_job_status(distribution_id, DeliveryStatus.VERIFIED, 100.0)
                
                print(f"✅ Distribution completed: {distribution_id}")
                return True
            else:
                await self._update_job_status(distribution_id, DeliveryStatus.FAILED, error_message="Delivery failed")
                return False
                
        except Exception as e:
            print(f"❌ Distribution job failed: {e}")
            await self._update_job_status(distribution_id, DeliveryStatus.FAILED, error_message=str(e))
            return False
    
    async def _deliver_via_api(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Deliver content via API"""
        
        try:
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 30.0)
            
            # Prepare API request based on platform
            if job.platform_name == "YouTube":
                return await self._deliver_to_youtube(job, connector)
            elif job.platform_name == "Instagram":
                return await self._deliver_to_instagram(job, connector)
            elif job.platform_name == "TikTok":
                return await self._deliver_to_tiktok(job, connector)
            elif job.platform_name == "Spotify":
                return await self._deliver_to_spotify(job, connector)
            else:
                # Generic API delivery
                return await self._deliver_generic_api(job, connector)
                
        except Exception as e:
            print(f"Error in API delivery: {e}")
            return False
    
    async def _deliver_to_youtube(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Deliver content to YouTube"""
        
        try:
            # Get primary video file
            video_file = None
            for file_info in job.source_files:
                if file_info.get("type") == "primary" and file_info.get("format") in ["mp4", "mov"]:
                    video_file = file_info
                    break
            
            if not video_file:
                raise ValueError("No suitable video file found for YouTube")
            
            # Prepare metadata
            metadata = {
                "snippet": {
                    "title": job.metadata_payload.get("title", "Untitled"),
                    "description": job.metadata_payload.get("description", ""),
                    "tags": job.metadata_payload.get("tags", []),
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": "private"  # Start as private
                }
            }
            
            # Simulate API call (in production, would use actual YouTube API)
            await asyncio.sleep(2)  # Simulate upload time
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 70.0)
            
            # Simulate successful response
            platform_response = {
                "id": f"yt_video_{uuid.uuid4().hex[:8]}",
                "status": "uploaded",
                "snippet": metadata["snippet"]
            }
            
            # Update job with platform response
            self.distribution_jobs_collection.update_one(
                {"distribution_id": job.distribution_id},
                {
                    "$set": {
                        "platform_response": platform_response,
                        "platform_content_id": platform_response["id"]
                    }
                }
            )
            
            return True
            
        except Exception as e:
            print(f"YouTube delivery error: {e}")
            return False
    
    async def _deliver_to_instagram(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Deliver content to Instagram"""
        
        try:
            # Get media file
            media_file = None
            for file_info in job.source_files:
                if file_info.get("format") in ["mp4", "jpg", "png"]:
                    media_file = file_info
                    break
            
            if not media_file:
                raise ValueError("No suitable media file found for Instagram")
            
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 50.0)
            
            # Simulate Instagram API calls
            # Step 1: Create media container
            await asyncio.sleep(1)
            
            # Step 2: Publish media
            await asyncio.sleep(1)
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 80.0)
            
            platform_response = {
                "id": f"ig_media_{uuid.uuid4().hex[:8]}",
                "status": "published"
            }
            
            self.distribution_jobs_collection.update_one(
                {"distribution_id": job.distribution_id},
                {
                    "$set": {
                        "platform_response": platform_response,
                        "platform_content_id": platform_response["id"]
                    }
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Instagram delivery error: {e}")
            return False
    
    async def _deliver_to_tiktok(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Deliver content to TikTok"""
        
        try:
            # Get video file
            video_file = None
            for file_info in job.source_files:
                if file_info.get("format") == "mp4":
                    video_file = file_info
                    break
            
            if not video_file:
                raise ValueError("No suitable video file found for TikTok")
            
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 40.0)
            
            # Simulate TikTok API calls
            # Step 1: Initialize upload
            await asyncio.sleep(1)
            
            # Step 2: Upload video
            await asyncio.sleep(2)
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 75.0)
            
            platform_response = {
                "share_id": f"tiktok_{uuid.uuid4().hex[:8]}",
                "status": "processing"
            }
            
            self.distribution_jobs_collection.update_one(
                {"distribution_id": job.distribution_id},
                {
                    "$set": {
                        "platform_response": platform_response,
                        "platform_content_id": platform_response["share_id"]
                    }
                }
            )
            
            return True
            
        except Exception as e:
            print(f"TikTok delivery error: {e}")
            return False
    
    async def _deliver_to_spotify(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Deliver content to Spotify (via distributor)"""
        
        try:
            # Get audio file
            audio_file = None
            for file_info in job.source_files:
                if file_info.get("format") in ["wav", "flac"]:
                    audio_file = file_info
                    break
            
            if not audio_file:
                raise ValueError("No suitable audio file found for Spotify")
            
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 50.0)
            
            # Simulate distributor API call
            await asyncio.sleep(3)  # Spotify delivery takes longer
            
            platform_response = {
                "release_id": f"spotify_release_{uuid.uuid4().hex[:8]}",
                "status": "pending_review",
                "estimated_live_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
            }
            
            self.distribution_jobs_collection.update_one(
                {"distribution_id": job.distribution_id},
                {
                    "$set": {
                        "platform_response": platform_response,
                        "platform_content_id": platform_response["release_id"]
                    }
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Spotify delivery error: {e}")
            return False
    
    async def _deliver_generic_api(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Generic API delivery for other platforms"""
        
        try:
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 60.0)
            
            # Simulate generic API call
            await asyncio.sleep(2)
            
            platform_response = {
                "content_id": f"generic_{uuid.uuid4().hex[:8]}",
                "status": "delivered",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.distribution_jobs_collection.update_one(
                {"distribution_id": job.distribution_id},
                {
                    "$set": {
                        "platform_response": platform_response,
                        "platform_content_id": platform_response["content_id"]
                    }
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Generic API delivery error: {e}")
            return False
    
    async def _deliver_via_sftp(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Deliver content via SFTP"""
        
        try:
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 40.0)
            
            # Simulate SFTP upload
            await asyncio.sleep(3)
            
            platform_response = {
                "transfer_id": f"sftp_{uuid.uuid4().hex[:8]}",
                "status": "transferred",
                "file_count": len(job.source_files)
            }
            
            self.distribution_jobs_collection.update_one(
                {"distribution_id": job.distribution_id},
                {
                    "$set": {
                        "platform_response": platform_response,
                        "delivery_receipt": platform_response["transfer_id"]
                    }
                }
            )
            
            return True
            
        except Exception as e:
            print(f"SFTP delivery error: {e}")
            return False
    
    async def _deliver_via_email(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Deliver content via email with attachments"""
        
        try:
            await self._update_job_status(job.distribution_id, DeliveryStatus.DELIVERING, 30.0)
            
            # Simulate email delivery
            await asyncio.sleep(1)
            
            platform_response = {
                "email_id": f"email_{uuid.uuid4().hex[:8]}",
                "status": "sent",
                "recipient": connector.get("delivery_email", "content@platform.com")
            }
            
            self.distribution_jobs_collection.update_one(
                {"distribution_id": job.distribution_id},
                {
                    "$set": {
                        "platform_response": platform_response,
                        "delivery_receipt": platform_response["email_id"]
                    }
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Email delivery error: {e}")
            return False
    
    async def _verify_delivery(self, job: DistributionJob, connector: Dict[str, Any]) -> bool:
        """Verify that delivery was successful"""
        
        try:
            # Simulate delivery verification
            await asyncio.sleep(1)
            
            # For platforms that support verification, check status
            if job.platform_content_id:
                # Simulate verification check
                verification_response = {
                    "verified": True,
                    "platform_status": "live",
                    "verification_time": datetime.now(timezone.utc).isoformat()
                }
                
                self.distribution_jobs_collection.update_one(
                    {"distribution_id": job.distribution_id},
                    {"$set": {"verification_completed_at": datetime.now(timezone.utc).isoformat()}}
                )
                
                return verification_response["verified"]
            
            return True
            
        except Exception as e:
            print(f"Delivery verification error: {e}")
            return False
    
    async def _update_job_status(self,
                               distribution_id: str,
                               status: DeliveryStatus,
                               progress: float = None,
                               error_message: str = None):
        """Update distribution job status"""
        
        update_data = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if progress is not None:
            update_data["progress_percentage"] = progress
        
        if error_message:
            update_data["error_message"] = error_message
        
        if status == DeliveryStatus.DELIVERING and progress and progress <= 30.0:
            update_data["delivery_started_at"] = datetime.now(timezone.utc).isoformat()
        elif status == DeliveryStatus.DELIVERED:
            update_data["delivery_completed_at"] = datetime.now(timezone.utc).isoformat()
        
        self.distribution_jobs_collection.update_one(
            {"distribution_id": distribution_id},
            {"$set": update_data}
        )
    
    async def get_distribution_status(self, distribution_id: str) -> Optional[DistributionJob]:
        """Get status of a distribution job"""
        
        try:
            job_data = self.distribution_jobs_collection.find_one({
                "distribution_id": distribution_id
            })
            
            if job_data:
                job_data["_id"] = str(job_data["_id"])
                return DistributionJob(**job_data)
            return None
            
        except Exception as e:
            print(f"Error getting distribution status: {e}")
            return None
    
    async def list_user_distributions(self, user_id: str, status: str = None) -> List[DistributionJob]:
        """List distribution jobs for a user"""
        
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            
            jobs_data = list(self.distribution_jobs_collection.find(query).sort("created_at", -1))
            
            jobs = []
            for job_data in jobs_data:
                job_data["_id"] = str(job_data["_id"])
                jobs.append(DistributionJob(**job_data))
            
            return jobs
            
        except Exception as e:
            print(f"Error listing user distributions: {e}")
            return []
    
    async def get_platform_connectors(self) -> List[PlatformConnector]:
        """Get all available platform connectors"""
        
        try:
            connectors_data = list(self.platform_connectors_collection.find())
            
            connectors = []
            for connector_data in connectors_data:
                connector_data["_id"] = str(connector_data["_id"])
                connectors.append(PlatformConnector(**connector_data))
            
            return connectors
            
        except Exception as e:
            print(f"Error getting platform connectors: {e}")
            return []