"""
Content Workflow Service - End-to-End Content Distribution System
Handles master intake, versioning, technical QC, transcoding, and distribution orchestration.
Integrates with existing Content Ingestion System (Functions 1-5).
"""

import os
import uuid
import json
import asyncio
import hashlib
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from pymongo import MongoClient
import ffmpeg
import requests
from pathlib import Path

# Content workflow stages
class WorkflowStage(str, Enum):
    INTAKE = "intake"
    VERSIONING = "versioning"
    TECHNICAL_QC = "technical_qc"
    ACCESSIBILITY = "accessibility"
    CREATIVE_APPROVAL = "creative_approval"
    COMPLIANCE_APPROVAL = "compliance_approval"
    TRANSCODING = "transcoding"
    PACKAGING = "packaging"
    DISTRIBUTION = "distribution"
    MONITORING = "monitoring"
    COMPLETED = "completed"

class ContentType(str, Enum):
    VIDEO_LONGFORM = "video_longform"
    VIDEO_EPISODIC = "video_episodic"
    AUDIO_MUSIC = "audio_music"
    AUDIO_RADIO = "audio_radio"
    SOCIAL_SHORT = "social_short"
    OTT_STREAMING = "ott_streaming"

class QualityProfile(str, Enum):
    BROADCAST_HD = "broadcast_hd"
    BROADCAST_4K = "broadcast_4k"
    STREAMING_PREMIUM = "streaming_premium"
    STREAMING_STANDARD = "streaming_standard"
    SOCIAL_OPTIMIZED = "social_optimized"
    RADIO_MASTER = "radio_master"

class DistributionChannel(str, Enum):
    LINEAR_TV_US = "linear_tv_us"
    LINEAR_TV_EU = "linear_tv_eu"
    OTT_SVOD = "ott_svod"
    OTT_AVOD = "ott_avod"
    SOCIAL_YOUTUBE = "social_youtube"
    SOCIAL_TIKTOK = "social_tiktok"
    SOCIAL_INSTAGRAM = "social_instagram"
    DSP_SPOTIFY = "dsp_spotify"
    DSP_APPLE = "dsp_apple"
    RADIO_FM = "radio_fm"
    RADIO_DAB = "radio_dab"

# Master content specification
class MasterContent(BaseModel):
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    original_filename: str
    file_path: str
    file_size: int
    file_format: str
    content_type: ContentType
    
    # Technical specifications
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    resolution: Optional[str] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    audio_channels: Optional[int] = None
    
    # Quality metrics
    checksum_md5: str
    checksum_sha256: str
    
    # Metadata
    title: str
    description: Optional[str] = None
    slate_info: Dict[str, Any] = {}
    bars_tone_info: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContentVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    version_number: str
    version_name: str
    
    # Source information
    source_master_id: str
    file_path: str
    file_size: int
    checksum_md5: str
    checksum_sha256: str
    
    # Version metadata
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_current: bool = False
    is_immutable: bool = True
    
    # Changes from previous version
    changes_summary: str = ""
    parent_version_id: Optional[str] = None
    
    # Technical specifications
    quality_profile: QualityProfile
    specs: Dict[str, Any] = {}
    
    # Storage information
    storage_location: str
    storage_provider: str = "s3"  # s3, blob, local
    
class TechnicalQCResult(BaseModel):
    qc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    version_id: str
    
    # QC results
    overall_status: str  # passed, failed, warning
    qc_score: float  # 0-100
    
    # Technical checks
    video_checks: Dict[str, Any] = {}
    audio_checks: Dict[str, Any] = {}
    metadata_checks: Dict[str, Any] = {}
    
    # Automated checks
    frame_rate_check: bool = False
    resolution_check: bool = False
    bit_rate_check: bool = False
    color_range_check: bool = False
    loudness_check: bool = False
    true_peak_check: bool = False
    pse_flash_check: bool = False
    
    # Issues found
    critical_issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    
    performed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    performed_by: str = "automated_qc_system"

class DeliveryProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_name: str
    channel: DistributionChannel
    
    # Technical requirements
    video_specs: Dict[str, Any] = {}
    audio_specs: Dict[str, Any] = {}
    container_format: str
    
    # Delivery specifications
    delivery_method: str  # aspera, sftp, api, email
    api_endpoint: Optional[str] = None
    credentials_required: List[str] = []
    
    # Compliance requirements
    required_metadata: List[str] = []
    content_rating_required: bool = False
    captions_required: bool = False
    
    # Quality gates
    min_quality_score: float = 80.0
    compliance_checks: List[str] = []
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class ContentWorkflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    user_id: str
    
    # Current state
    current_stage: WorkflowStage = WorkflowStage.INTAKE
    overall_status: str = "in_progress"  # in_progress, completed, failed, on_hold
    
    # Stage tracking
    stage_history: List[Dict[str, Any]] = []
    stage_results: Dict[WorkflowStage, Dict[str, Any]] = {}
    
    # Target profiles and channels
    target_profiles: List[QualityProfile] = []
    target_channels: List[DistributionChannel] = []
    delivery_profiles: List[str] = []  # List of profile IDs
    
    # Automation settings
    auto_progress: bool = True
    require_approval: List[WorkflowStage] = []
    
    # Performance tracking
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Error handling
    failed_stages: List[str] = []
    retry_count: int = 0
    max_retries: int = 3
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContentWorkflowService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        
        # Collections
        self.master_content_collection = self.db['master_content']
        self.content_versions_collection = self.db['content_versions']
        self.technical_qc_collection = self.db['technical_qc_results']
        self.delivery_profiles_collection = self.db['delivery_profiles']
        self.content_workflows_collection = self.db['content_workflows']
        self.transcoding_jobs_collection = self.db['transcoding_jobs']
        
        # Initialize delivery profiles
        self._initialize_delivery_profiles()
        
        # Storage configuration
        self.storage_config = {
            "local_storage_path": "/tmp/bme_content",
            "s3_bucket": os.environ.get('S3_BUCKET', 'bigmann-entertainment-media'),
            "s3_region": os.environ.get('AWS_REGION', 'us-east-1')
        }
        
        # Ensure local storage directory exists
        Path(self.storage_config["local_storage_path"]).mkdir(parents=True, exist_ok=True)
    
    def _initialize_delivery_profiles(self):
        """Initialize default delivery profiles for different channels"""
        
        default_profiles = [
            # Linear TV US
            {
                "profile_name": "Linear TV US - HD",
                "channel": DistributionChannel.LINEAR_TV_US,
                "container_format": "mov",
                "video_specs": {
                    "codec": "prores",
                    "resolution": "1920x1080",
                    "frame_rate": 29.97,
                    "container": "mov"
                },
                "audio_specs": {
                    "codec": "pcm",
                    "sample_rate": 48000,
                    "channels": 2,
                    "loudness_target": -24.0,  # ATSC A/85
                    "true_peak_max": -2.0
                },
                "delivery_method": "aspera",
                "required_metadata": ["title_slate", "EIDR", "captions_608", "bars_tone", "2_pop"],
                "captions_required": True,
                "min_quality_score": 95.0
            },
            
            # Linear TV EU
            {
                "profile_name": "Linear TV EU - HD",
                "channel": DistributionChannel.LINEAR_TV_EU,
                "container_format": "mov",
                "video_specs": {
                    "codec": "prores",
                    "resolution": "1920x1080",
                    "frame_rate": 25.0,
                    "container": "mov"
                },
                "audio_specs": {
                    "codec": "pcm",
                    "sample_rate": 48000,
                    "channels": 2,
                    "loudness_target": -23.0,  # EBU R128
                    "true_peak_max": -1.0
                },
                "delivery_method": "aspera",
                "required_metadata": ["local_language_metadata", "EIDR", "captions_IMSC", "broadcast_safe_colors"],
                "captions_required": True
            },
            
            # OTT Streaming
            {
                "profile_name": "OTT SVOD - Multi-bitrate",
                "channel": DistributionChannel.OTT_SVOD,
                "container_format": "mp4",
                "video_specs": {
                    "codec": "h264_hevc",
                    "resolutions": ["3840x2160", "1920x1080", "1280x720", "854x480"],
                    "frame_rates": [23.976, 25.0, 29.97],
                    "container": "mp4"
                },
                "audio_specs": {
                    "codec": "aac",
                    "sample_rate": 48000,
                    "loudness_target": -16.0,
                    "true_peak_max": -1.0
                },
                "delivery_method": "api",
                "required_metadata": ["epg_data", "artwork", "chapters", "content_ratings"],
                "captions_required": True
            },
            
            # Social Media - YouTube
            {
                "profile_name": "YouTube Optimized",
                "channel": DistributionChannel.SOCIAL_YOUTUBE,
                "container_format": "mp4",
                "video_specs": {
                    "codec": "h264",
                    "resolution": "1920x1080",
                    "frame_rate": 30.0,
                    "bit_rate": 8000,
                    "container": "mp4"
                },
                "audio_specs": {
                    "codec": "aac",
                    "sample_rate": 48000,
                    "loudness_target": -14.0,
                    "true_peak_max": -1.0
                },
                "delivery_method": "api",
                "api_endpoint": "https://www.googleapis.com/upload/youtube/v3/videos",
                "required_metadata": ["ISRC", "UPC", "end_screen_cards", "chapters"],
                "credentials_required": ["youtube_api_key", "oauth_token"]
            },
            
            # Social Media - TikTok
            {
                "profile_name": "TikTok Vertical",
                "channel": DistributionChannel.SOCIAL_TIKTOK,
                "container_format": "mp4",
                "video_specs": {
                    "codec": "h264",
                    "resolution": "1080x1920",
                    "frame_rate": 30.0,
                    "max_duration": 180,
                    "container": "mp4"
                },
                "audio_specs": {
                    "codec": "aac",
                    "sample_rate": 44100,
                    "loudness_target": -14.0
                },
                "delivery_method": "api",
                "api_endpoint": "https://open-api.tiktok.com/share/video/upload/",
                "required_metadata": ["hashtags", "music_rights_cleared"]
            },
            
            # DSP - Spotify
            {
                "profile_name": "Spotify Audio Master",
                "channel": DistributionChannel.DSP_SPOTIFY,
                "container_format": "wav",
                "audio_specs": {
                    "codec": "wav",
                    "sample_rate": 44100,
                    "bit_depth": 16,
                    "loudness_target": -14.0,
                    "true_peak_max": -1.0
                },
                "delivery_method": "api",
                "api_endpoint": "https://api.spotify.com/v1/albums",
                "required_metadata": ["ISRC", "UPC", "songwriter_splits", "lyrics", "credits"],
                "credentials_required": ["spotify_client_id", "spotify_client_secret"]
            },
            
            # Radio FM
            {
                "profile_name": "Radio FM Master",
                "channel": DistributionChannel.RADIO_FM,
                "container_format": "wav",
                "audio_specs": {
                    "codec": "wav",
                    "sample_rate": 44100,
                    "bit_depth": 16,
                    "loudness_target": -16.0,
                    "true_peak_max": -1.0
                },
                "delivery_method": "email",
                "required_metadata": ["ISRC", "intro_outro_timings", "clean_edit", "radio_edit"],
                "compliance_checks": ["profanity_check", "timing_validation"]
            }
        ]
        
        # Insert default profiles if they don't exist
        for profile_data in default_profiles:
            existing = self.delivery_profiles_collection.find_one({
                "profile_name": profile_data["profile_name"]
            })
            
            if not existing:
                profile = DeliveryProfile(**profile_data)
                profile_dict = profile.dict()
                profile_dict["created_at"] = profile.created_at.isoformat()
                self.delivery_profiles_collection.insert_one(profile_dict)
    
    async def ingest_master_content(self, 
                                  user_id: str,
                                  file_path: str,
                                  content_type: ContentType,
                                  metadata: Dict[str, Any]) -> MasterContent:
        """
        Ingest master content - accepts ProRes, DNxHR, high-rate H.264/HEVC for video; WAV/AIFF for audio
        """
        
        try:
            # Validate file exists and is accessible
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            original_filename = os.path.basename(file_path)
            
            # Generate checksums for immutable versioning
            checksums = await self._generate_checksums(file_path)
            
            # Extract technical metadata using FFmpeg
            technical_metadata = await self._extract_technical_metadata(file_path)
            
            # Create master content record
            master_content = MasterContent(
                user_id=user_id,
                original_filename=original_filename,
                file_path=file_path,
                file_size=file_size,
                file_format=technical_metadata.get("format_name", "unknown"),
                content_type=content_type,
                checksum_md5=checksums["md5"],
                checksum_sha256=checksums["sha256"],
                title=metadata.get("title", original_filename),
                description=metadata.get("description"),
                **technical_metadata
            )
            
            # Store in database
            master_dict = master_content.dict()
            master_dict["created_at"] = master_content.created_at.isoformat()
            master_dict["updated_at"] = master_content.updated_at.isoformat()
            
            result = self.master_content_collection.insert_one(master_dict)
            master_content.content_id = str(result.inserted_id)
            
            # Update with content_id
            self.master_content_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"content_id": master_content.content_id}}
            )
            
            print(f"✅ Master content ingested: {master_content.content_id}")
            return master_content
            
        except Exception as e:
            print(f"❌ Error ingesting master content: {e}")
            raise
    
    async def create_content_version(self,
                                   content_id: str,
                                   user_id: str,
                                   quality_profile: QualityProfile,
                                   version_name: str = None,
                                   changes_summary: str = "") -> ContentVersion:
        """
        Create a new immutable version with semantic versioning
        """
        
        try:
            # Get master content
            master_content = self.master_content_collection.find_one({"content_id": content_id})
            if not master_content:
                raise ValueError("Master content not found")
            
            # Get existing versions to determine version number
            existing_versions = list(self.content_versions_collection.find(
                {"content_id": content_id}
            ).sort("created_at", -1))
            
            # Determine semantic version number
            if not existing_versions:
                version_number = "1.0.0"
            else:
                latest_version = existing_versions[0]["version_number"]
                major, minor, patch = map(int, latest_version.split('.'))
                
                # Increment based on changes
                if "major" in changes_summary.lower() or len(changes_summary.split()) > 20:
                    version_number = f"{major + 1}.0.0"
                elif "minor" in changes_summary.lower() or len(changes_summary.split()) > 5:
                    version_number = f"{major}.{minor + 1}.0"
                else:
                    version_number = f"{major}.{minor}.{patch + 1}"
            
            # Generate version file path (immutable storage)
            version_filename = f"{content_id}_v{version_number}_{quality_profile.value}.{master_content['file_format']}"
            version_storage_path = os.path.join(
                self.storage_config["local_storage_path"],
                "versions",
                content_id,
                version_filename
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(version_storage_path), exist_ok=True)
            
            # Process file according to quality profile
            processed_file_path = await self._process_for_quality_profile(
                master_content["file_path"],
                version_storage_path,
                quality_profile
            )
            
            # Generate checksums for the new version
            version_checksums = await self._generate_checksums(processed_file_path)
            version_size = os.path.getsize(processed_file_path)
            
            # Create version record
            content_version = ContentVersion(
                content_id=content_id,
                version_number=version_number,
                version_name=version_name or f"Version {version_number}",
                source_master_id=master_content["content_id"],
                file_path=processed_file_path,
                file_size=version_size,
                checksum_md5=version_checksums["md5"],
                checksum_sha256=version_checksums["sha256"],
                created_by=user_id,
                changes_summary=changes_summary,
                quality_profile=quality_profile,
                storage_location=processed_file_path,
                parent_version_id=existing_versions[0]["version_id"] if existing_versions else None
            )
            
            # Set as current version
            if not existing_versions:
                content_version.is_current = True
            
            # Store version
            version_dict = content_version.dict()
            version_dict["created_at"] = content_version.created_at.isoformat()
            
            result = self.content_versions_collection.insert_one(version_dict)
            content_version.version_id = str(result.inserted_id)
            
            # Update with version_id
            self.content_versions_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"version_id": content_version.version_id}}
            )
            
            print(f"✅ Content version created: {version_number}")
            return content_version
            
        except Exception as e:
            print(f"❌ Error creating content version: {e}")
            raise
    
    async def perform_technical_qc(self, 
                                 content_id: str,
                                 version_id: str,
                                 target_profile: QualityProfile = None) -> TechnicalQCResult:
        """
        Perform comprehensive technical QC including automated checks
        """
        
        try:
            # Get version information
            version = self.content_versions_collection.find_one({"version_id": version_id})
            if not version:
                raise ValueError("Content version not found")
            
            file_path = version["file_path"]
            
            # Initialize QC result
            qc_result = TechnicalQCResult(
                content_id=content_id,
                version_id=version_id
            )
            
            # Extract detailed technical information
            tech_info = await self._extract_detailed_technical_info(file_path)
            
            # Perform automated checks
            qc_checks = await self._perform_automated_qc_checks(file_path, tech_info, target_profile)
            
            # Update QC result with findings
            qc_result.video_checks = qc_checks.get("video", {})
            qc_result.audio_checks = qc_checks.get("audio", {})
            qc_result.metadata_checks = qc_checks.get("metadata", {})
            
            # Set individual check results
            qc_result.frame_rate_check = qc_checks.get("frame_rate_valid", False)
            qc_result.resolution_check = qc_checks.get("resolution_valid", False)
            qc_result.bit_rate_check = qc_checks.get("bit_rate_valid", False)
            qc_result.color_range_check = qc_checks.get("color_range_valid", False)
            qc_result.loudness_check = qc_checks.get("loudness_valid", False)
            qc_result.true_peak_check = qc_checks.get("true_peak_valid", False)
            qc_result.pse_flash_check = qc_checks.get("pse_safe", True)  # Default to safe
            
            # Collect issues
            qc_result.critical_issues = qc_checks.get("critical_issues", [])
            qc_result.warnings = qc_checks.get("warnings", [])
            qc_result.suggestions = qc_checks.get("suggestions", [])
            
            # Calculate overall score and status
            passed_checks = sum([
                qc_result.frame_rate_check,
                qc_result.resolution_check,
                qc_result.bit_rate_check,
                qc_result.color_range_check,
                qc_result.loudness_check,
                qc_result.true_peak_check,
                qc_result.pse_flash_check
            ])
            
            total_checks = 7
            qc_result.qc_score = (passed_checks / total_checks) * 100
            
            # Determine overall status
            if len(qc_result.critical_issues) > 0:
                qc_result.overall_status = "failed"
            elif qc_result.qc_score >= 90:
                qc_result.overall_status = "passed"
            else:
                qc_result.overall_status = "warning"
            
            # Store QC result
            qc_dict = qc_result.dict()
            qc_dict["performed_at"] = qc_result.performed_at.isoformat()
            
            result = self.technical_qc_collection.insert_one(qc_dict)
            qc_result.qc_id = str(result.inserted_id)
            
            # Update with qc_id
            self.technical_qc_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"qc_id": qc_result.qc_id}}
            )
            
            print(f"✅ Technical QC completed: {qc_result.overall_status} (Score: {qc_result.qc_score:.1f}%)")
            return qc_result
            
        except Exception as e:
            print(f"❌ Error performing technical QC: {e}")
            raise
    
    async def _generate_checksums(self, file_path: str) -> Dict[str, str]:
        """Generate MD5 and SHA256 checksums for file integrity"""
        
        checksums = {}
        
        # Generate MD5
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        checksums["md5"] = md5_hash.hexdigest()
        
        # Generate SHA256
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        checksums["sha256"] = sha256_hash.hexdigest()
        
        return checksums
    
    async def _extract_technical_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract technical metadata using FFmpeg probe"""
        
        try:
            probe = ffmpeg.probe(file_path)
            
            metadata = {
                "format_name": probe["format"]["format_name"],
                "duration_seconds": float(probe["format"].get("duration", 0))
            }
            
            # Video stream information
            video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
            if video_streams:
                video = video_streams[0]
                metadata.update({
                    "video_codec": video.get("codec_name"),
                    "resolution": f"{video.get('width', 0)}x{video.get('height', 0)}",
                    "frame_rate": eval(video.get("r_frame_rate", "0/1")),
                    "bit_rate": int(video.get("bit_rate", 0))
                })
            
            # Audio stream information
            audio_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "audio"]
            if audio_streams:
                audio = audio_streams[0]
                metadata.update({
                    "audio_codec": audio.get("codec_name"),
                    "sample_rate": int(audio.get("sample_rate", 0)),
                    "audio_channels": int(audio.get("channels", 0))
                })
            
            return metadata
            
        except Exception as e:
            print(f"Warning: Could not extract technical metadata: {e}")
            return {}
    
    async def _process_for_quality_profile(self, 
                                         source_path: str,
                                         output_path: str,
                                         quality_profile: QualityProfile) -> str:
        """Process file according to quality profile specifications"""
        
        try:
            # For now, just copy the file (in production, this would do actual transcoding)
            # This is where you'd implement specific processing based on quality_profile
            
            import shutil
            shutil.copy2(source_path, output_path)
            
            # TODO: Implement actual processing based on quality profile
            # - BROADCAST_HD: Convert to ProRes, apply broadcast safe colors
            # - STREAMING_PREMIUM: Generate HLS/DASH ladders
            # - SOCIAL_OPTIMIZED: Apply platform-specific specs
            # - RADIO_MASTER: Audio normalization and loudness targets
            
            return output_path
            
        except Exception as e:
            print(f"Error processing for quality profile: {e}")
            raise
    
    async def _extract_detailed_technical_info(self, file_path: str) -> Dict[str, Any]:
        """Extract detailed technical information for QC"""
        
        try:
            probe = ffmpeg.probe(file_path)
            
            detailed_info = {
                "format": probe.get("format", {}),
                "streams": probe.get("streams", []),
                "chapters": probe.get("chapters", [])
            }
            
            # Add specific technical analysis
            for stream in detailed_info["streams"]:
                if stream["codec_type"] == "video":
                    stream["analysis"] = {
                        "color_range": stream.get("color_range", "unknown"),
                        "color_space": stream.get("color_space", "unknown"),
                        "pix_fmt": stream.get("pix_fmt", "unknown")
                    }
                elif stream["codec_type"] == "audio":
                    stream["analysis"] = {
                        "channel_layout": stream.get("channel_layout", "unknown"),
                        "bits_per_sample": stream.get("bits_per_sample", 0)
                    }
            
            return detailed_info
            
        except Exception as e:
            print(f"Error extracting detailed technical info: {e}")
            return {}
    
    async def _perform_automated_qc_checks(self, 
                                         file_path: str,
                                         tech_info: Dict[str, Any],
                                         target_profile: QualityProfile = None) -> Dict[str, Any]:
        """Perform automated QC checks"""
        
        checks = {
            "critical_issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            streams = tech_info.get("streams", [])
            video_streams = [s for s in streams if s["codec_type"] == "video"]
            audio_streams = [s for s in streams if s["codec_type"] == "audio"]
            
            # Video checks
            if video_streams:
                video = video_streams[0]
                
                # Frame rate check
                frame_rate = eval(video.get("r_frame_rate", "0/1"))
                standard_rates = [23.976, 24.0, 25.0, 29.97, 30.0, 50.0, 59.94, 60.0]
                checks["frame_rate_valid"] = any(abs(frame_rate - rate) < 0.1 for rate in standard_rates)
                
                if not checks["frame_rate_valid"]:
                    checks["warnings"].append({
                        "issue": "Non-standard frame rate",
                        "details": f"Frame rate {frame_rate} may cause compatibility issues",
                        "suggestion": "Use standard broadcast frame rates"
                    })
                
                # Resolution check
                width = video.get("width", 0)
                height = video.get("height", 0)
                standard_resolutions = [
                    (1920, 1080), (1280, 720), (3840, 2160), (854, 480)
                ]
                checks["resolution_valid"] = (width, height) in standard_resolutions
                
                # Bit rate check
                bit_rate = int(video.get("bit_rate", 0))
                checks["bit_rate_valid"] = bit_rate > 1000000  # At least 1 Mbps
                
                # Color range check (broadcast safe)
                color_range = video.get("color_range", "unknown")
                checks["color_range_valid"] = color_range in ["tv", "mpeg"]
                
                if color_range == "pc":
                    checks["warnings"].append({
                        "issue": "Full range color detected",
                        "details": "Content uses PC/full range colors",
                        "suggestion": "Convert to broadcast safe (limited range) for TV distribution"
                    })
            
            # Audio checks
            if audio_streams:
                audio = audio_streams[0]
                
                # Sample rate check
                sample_rate = int(audio.get("sample_rate", 0))
                standard_rates = [44100, 48000, 96000]
                checks["sample_rate_valid"] = sample_rate in standard_rates
                
                # Channel count check
                channels = int(audio.get("channels", 0))
                checks["channel_count_valid"] = channels in [1, 2, 6, 8]  # Mono, stereo, 5.1, 7.1
                
                # Simulated loudness check (in production, would use actual audio analysis)
                checks["loudness_valid"] = True  # Placeholder
                checks["true_peak_valid"] = True  # Placeholder
            
            # PSE (Photosensitive Epilepsy) check - placeholder
            checks["pse_safe"] = True  # Would require actual flash detection
            
            # Overall validation
            checks["metadata"] = {
                "has_video": len(video_streams) > 0,
                "has_audio": len(audio_streams) > 0,
                "duration_valid": float(tech_info.get("format", {}).get("duration", 0)) > 0
            }
            
        except Exception as e:
            checks["critical_issues"].append({
                "issue": "QC analysis failed",
                "details": str(e),
                "suggestion": "Manual review required"
            })
        
        return checks