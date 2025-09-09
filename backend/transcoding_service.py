"""
Transcoding Service - Function 2: Transcoding & Format Optimization
Handles media transcoding, format conversion, and quality optimization using FFmpeg.
"""

import os
import uuid
import json
import asyncio
import subprocess
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
import shutil
from pydantic import BaseModel, Field
from pymongo import MongoClient

class TranscodingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class QualityPreset(str, Enum):
    LOW = "low"          # 480p, low bitrate
    MEDIUM = "medium"    # 720p, medium bitrate
    HIGH = "high"        # 1080p, high bitrate
    ULTRA = "ultra"      # 4K, highest quality
    CUSTOM = "custom"    # User-defined settings

class OutputFormat(str, Enum):
    # Video formats
    MP4 = "mp4"
    WEBM = "webm" 
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    
    # Audio formats
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    FLAC = "flac"
    WAV = "wav"

class TranscodingPreset(BaseModel):
    preset_id: str
    name: str
    description: str
    output_format: OutputFormat
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    video_bitrate: Optional[str] = None
    audio_bitrate: Optional[str] = None
    resolution: Optional[str] = None
    frame_rate: Optional[int] = None
    quality_level: QualityPreset = QualityPreset.MEDIUM
    platform_optimized: List[str] = []  # Platform names this preset is optimized for
    ffmpeg_params: Dict[str, Any] = {}

class TranscodingJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content_id: str
    input_file_path: str
    input_format: str
    output_format: OutputFormat
    quality_preset: QualityPreset
    custom_settings: Optional[Dict[str, Any]] = None
    platform_target: Optional[str] = None
    
    # Job status
    status: TranscodingStatus = TranscodingStatus.PENDING
    progress_percentage: float = 0.0
    estimated_duration: Optional[int] = None  # seconds
    actual_duration: Optional[int] = None
    
    # Output information
    output_file_path: Optional[str] = None
    output_file_size: Optional[int] = None
    output_resolution: Optional[str] = None
    output_bitrate: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    metadata: Dict[str, Any] = {}

class TranscodingService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        self.transcoding_collection = self.db['transcoding_jobs']
        
        # Working directory for transcoding operations
        self.working_dir = "/tmp/transcoding"
        os.makedirs(self.working_dir, exist_ok=True)
        
        # Initialize transcoding presets
        self.presets = self._initialize_presets()
        
        # FFmpeg availability check
        self.ffmpeg_available = self._check_ffmpeg_availability()
        
    def _check_ffmpeg_availability(self) -> bool:
        """Check if FFmpeg is available on the system"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("Warning: FFmpeg not found. Transcoding functionality will be limited.")
            return False
    
    def _initialize_presets(self) -> Dict[str, TranscodingPreset]:
        """Initialize transcoding presets for different quality levels and platforms"""
        presets = {}
        
        # Video presets
        
        # Low quality (480p) - mobile/low bandwidth
        presets["video_low_mp4"] = TranscodingPreset(
            preset_id="video_low_mp4",
            name="Low Quality MP4",
            description="480p MP4 for mobile and low bandwidth",
            output_format=OutputFormat.MP4,
            video_codec="libx264",
            audio_codec="aac",
            video_bitrate="800k",
            audio_bitrate="128k",
            resolution="854x480",
            frame_rate=30,
            quality_level=QualityPreset.LOW,
            platform_optimized=["tiktok", "instagram_stories", "snapchat"],
            ffmpeg_params={
                "preset": "fast",
                "crf": "28",
                "profile:v": "main",
                "level": "3.1"
            }
        )
        
        # Medium quality (720p) - standard web
        presets["video_medium_mp4"] = TranscodingPreset(
            preset_id="video_medium_mp4",
            name="Medium Quality MP4",
            description="720p MP4 for standard web streaming",
            output_format=OutputFormat.MP4,
            video_codec="libx264",
            audio_codec="aac",
            video_bitrate="2500k",
            audio_bitrate="192k",
            resolution="1280x720",
            frame_rate=30,
            quality_level=QualityPreset.MEDIUM,
            platform_optimized=["youtube", "facebook", "instagram", "twitter"],
            ffmpeg_params={
                "preset": "medium",
                "crf": "23",
                "profile:v": "high",
                "level": "4.0"
            }
        )
        
        # High quality (1080p) - high-end streaming
        presets["video_high_mp4"] = TranscodingPreset(
            preset_id="video_high_mp4",
            name="High Quality MP4",
            description="1080p MP4 for high-quality streaming",
            output_format=OutputFormat.MP4,
            video_codec="libx264",
            audio_codec="aac",
            video_bitrate="5000k",
            audio_bitrate="256k",
            resolution="1920x1080",
            frame_rate=30,
            quality_level=QualityPreset.HIGH,
            platform_optimized=["youtube", "vimeo", "netflix", "hulu"],
            ffmpeg_params={
                "preset": "slow",
                "crf": "20",
                "profile:v": "high",
                "level": "4.2"
            }
        )
        
        # WebM presets for web optimization
        presets["video_medium_webm"] = TranscodingPreset(
            preset_id="video_medium_webm",
            name="Medium Quality WebM",
            description="720p WebM for web optimization",
            output_format=OutputFormat.WEBM,
            video_codec="libvpx-vp9",
            audio_codec="libopus",
            video_bitrate="2000k",
            audio_bitrate="192k",
            resolution="1280x720",
            frame_rate=30,
            quality_level=QualityPreset.MEDIUM,
            platform_optimized=["web", "html5_video"],
            ffmpeg_params={
                "crf": "30",
                "b:v": "0",
                "speed": "2"
            }
        )
        
        # Audio presets
        
        # High quality MP3
        presets["audio_high_mp3"] = TranscodingPreset(
            preset_id="audio_high_mp3",
            name="High Quality MP3",
            description="320kbps MP3 for music distribution",
            output_format=OutputFormat.MP3,
            audio_codec="libmp3lame",
            audio_bitrate="320k",
            quality_level=QualityPreset.HIGH,
            platform_optimized=["spotify", "apple_music", "soundcloud"],
            ffmpeg_params={
                "q:a": "0"  # Highest quality VBR
            }
        )
        
        # Medium quality MP3
        presets["audio_medium_mp3"] = TranscodingPreset(
            preset_id="audio_medium_mp3",
            name="Medium Quality MP3",
            description="192kbps MP3 for general use",
            output_format=OutputFormat.MP3,
            audio_codec="libmp3lame",
            audio_bitrate="192k",
            quality_level=QualityPreset.MEDIUM,
            platform_optimized=["web", "streaming"],
            ffmpeg_params={
                "q:a": "2"
            }
        )
        
        # AAC for Apple/mobile platforms
        presets["audio_high_aac"] = TranscodingPreset(
            preset_id="audio_high_aac",
            name="High Quality AAC",
            description="256kbps AAC for Apple platforms",
            output_format=OutputFormat.AAC,
            audio_codec="aac",
            audio_bitrate="256k",
            quality_level=QualityPreset.HIGH,
            platform_optimized=["apple_music", "itunes", "ios"],
            ffmpeg_params={
                "profile:a": "aac_low"
            }
        )
        
        # OGG for open-source platforms
        presets["audio_medium_ogg"] = TranscodingPreset(
            preset_id="audio_medium_ogg",
            name="Medium Quality OGG",
            description="192kbps OGG Vorbis for open platforms",
            output_format=OutputFormat.OGG,
            audio_codec="libvorbis",
            audio_bitrate="192k",
            quality_level=QualityPreset.MEDIUM,
            platform_optimized=["web", "linux", "open_source"],
            ffmpeg_params={
                "q:a": "6"
            }
        )
        
        return presets
    
    async def create_transcoding_job(self, 
                                   user_id: str,
                                   content_id: str,
                                   input_file_path: str,
                                   input_format: str,
                                   output_format: OutputFormat,
                                   quality_preset: QualityPreset = QualityPreset.MEDIUM,
                                   platform_target: Optional[str] = None,
                                   custom_settings: Optional[Dict[str, Any]] = None) -> TranscodingJob:
        """Create a new transcoding job"""
        
        # Create transcoding job
        transcoding_job = TranscodingJob(
            user_id=user_id,
            content_id=content_id,
            input_file_path=input_file_path,
            input_format=input_format,
            output_format=output_format,
            quality_preset=quality_preset,
            platform_target=platform_target,
            custom_settings=custom_settings or {}
        )
        
        # Store in MongoDB
        job_dict = transcoding_job.dict()
        # Convert datetime objects for MongoDB
        for key, value in job_dict.items():
            if isinstance(value, datetime):
                job_dict[key] = value.isoformat()
        
        result = self.transcoding_collection.insert_one(job_dict)
        transcoding_job.job_id = str(result.inserted_id)
        
        return transcoding_job
    
    async def get_transcoding_job(self, job_id: str, user_id: str) -> Optional[TranscodingJob]:
        """Get a transcoding job by ID"""
        try:
            job_data = self.transcoding_collection.find_one({
                "job_id": job_id,
                "user_id": user_id
            })
            
            if job_data:
                job_data['_id'] = str(job_data['_id'])
                return TranscodingJob(**job_data)
            
            return None
        except Exception as e:
            print(f"Error retrieving transcoding job: {e}")
            return None
    
    async def list_user_transcoding_jobs(self, user_id: str, 
                                       status_filter: Optional[TranscodingStatus] = None,
                                       limit: int = 50, 
                                       offset: int = 0) -> List[TranscodingJob]:
        """List transcoding jobs for a user"""
        try:
            query = {"user_id": user_id}
            if status_filter:
                query["status"] = status_filter.value
            
            cursor = self.transcoding_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
            
            jobs = []
            for job_data in cursor:
                try:
                    job_data['_id'] = str(job_data['_id'])
                    jobs.append(TranscodingJob(**job_data))
                except Exception as e:
                    print(f"Error parsing transcoding job: {e}")
                    continue
            
            return jobs
        except Exception as e:
            print(f"Error listing transcoding jobs: {e}")
            return []
    
    async def start_transcoding_job(self, job_id: str, user_id: str) -> bool:
        """Start processing a transcoding job"""
        
        if not self.ffmpeg_available:
            await self._update_job_status(job_id, user_id, TranscodingStatus.FAILED, 
                                        error_message="FFmpeg not available")
            return False
        
        try:
            # Get job details
            job = await self.get_transcoding_job(job_id, user_id)
            if not job:
                return False
            
            # Update status to processing
            await self._update_job_status(job_id, user_id, TranscodingStatus.PROCESSING)
            
            # Start transcoding in background
            asyncio.create_task(self._process_transcoding_job(job))
            
            return True
            
        except Exception as e:
            print(f"Error starting transcoding job: {e}")
            await self._update_job_status(job_id, user_id, TranscodingStatus.FAILED, 
                                        error_message=str(e))
            return False
    
    async def _process_transcoding_job(self, job: TranscodingJob):
        """Process a transcoding job using FFmpeg"""
        
        try:
            # Update started timestamp
            await self._update_job_timestamp(job.job_id, job.user_id, "started_at")
            
            # Get appropriate preset
            preset = self._get_optimal_preset(job)
            if not preset:
                raise Exception(f"No suitable preset found for {job.output_format.value}")
            
            # Prepare file paths
            input_path = job.input_file_path
            output_filename = f"{job.job_id}.{job.output_format.value}"
            output_path = os.path.join(self.working_dir, output_filename)
            
            # Ensure input file exists
            if not os.path.exists(input_path):
                raise Exception(f"Input file not found: {input_path}")
            
            # Build FFmpeg command
            ffmpeg_cmd = self._build_ffmpeg_command(input_path, output_path, preset, job)
            
            # Execute FFmpeg with progress tracking
            success = await self._execute_ffmpeg_with_progress(ffmpeg_cmd, job)
            
            if success:
                # Get output file info
                output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                output_info = await self._analyze_output_file(output_path)
                
                # Update job with completion info
                await self._update_job_completion(
                    job.job_id, job.user_id, output_path, output_size, output_info
                )
                
                await self._update_job_status(job.job_id, job.user_id, TranscodingStatus.COMPLETED)
                
            else:
                await self._update_job_status(job.job_id, job.user_id, TranscodingStatus.FAILED,
                                            error_message="FFmpeg processing failed")
                
        except Exception as e:
            print(f"Transcoding job {job.job_id} failed: {str(e)}")
            await self._update_job_status(job.job_id, job.user_id, TranscodingStatus.FAILED,
                                        error_message=str(e))
            
            # Retry logic
            if job.retry_count < job.max_retries:
                await self._increment_retry_count(job.job_id, job.user_id)
                # Schedule retry after delay
                await asyncio.sleep(60)  # Wait 1 minute before retry
                await self.start_transcoding_job(job.job_id, job.user_id)
    
    def _get_optimal_preset(self, job: TranscodingJob) -> Optional[TranscodingPreset]:
        """Get the optimal preset for a transcoding job"""
        
        # Try platform-specific preset first
        if job.platform_target:
            for preset in self.presets.values():
                if (job.platform_target in preset.platform_optimized and 
                    preset.output_format == job.output_format and
                    preset.quality_level == job.quality_preset):
                    return preset
        
        # Try format and quality match
        for preset in self.presets.values():
            if (preset.output_format == job.output_format and 
                preset.quality_level == job.quality_preset):
                return preset
        
        # Fallback to any preset with matching format
        for preset in self.presets.values():
            if preset.output_format == job.output_format:
                return preset
        
        return None
    
    def _build_ffmpeg_command(self, input_path: str, output_path: str, 
                            preset: TranscodingPreset, job: TranscodingJob) -> List[str]:
        """Build FFmpeg command for transcoding"""
        
        cmd = ['ffmpeg', '-i', input_path]
        
        # Add video codec and settings
        if preset.video_codec:
            cmd.extend(['-c:v', preset.video_codec])
            
            if preset.video_bitrate:
                cmd.extend(['-b:v', preset.video_bitrate])
            
            if preset.resolution:
                cmd.extend(['-s', preset.resolution])
                
            if preset.frame_rate:
                cmd.extend(['-r', str(preset.frame_rate)])
        
        # Add audio codec and settings
        if preset.audio_codec:
            cmd.extend(['-c:a', preset.audio_codec])
            
            if preset.audio_bitrate:
                cmd.extend(['-b:a', preset.audio_bitrate])
        
        # Add FFmpeg parameters from preset
        for param, value in preset.ffmpeg_params.items():
            if param.startswith('-'):
                cmd.extend([param, str(value)])
            else:
                cmd.extend([f'-{param}', str(value)])
        
        # Add custom settings from job
        if job.custom_settings:
            for param, value in job.custom_settings.items():
                if param.startswith('-'):
                    cmd.extend([param, str(value)])
                else:
                    cmd.extend([f'-{param}', str(value)])
        
        # Progress and overwrite settings
        cmd.extend(['-progress', 'pipe:1', '-y'])
        
        # Output file
        cmd.append(output_path)
        
        return cmd
    
    async def _execute_ffmpeg_with_progress(self, cmd: List[str], job: TranscodingJob) -> bool:
        """Execute FFmpeg command with progress tracking"""
        
        try:
            # Get duration for progress calculation
            duration = await self._get_media_duration(job.input_file_path)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor progress
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                line = line.decode('utf-8').strip()
                
                # Parse progress information
                if line.startswith('out_time_ms='):
                    try:
                        time_ms = int(line.split('=')[1])
                        if duration and duration > 0:
                            progress = min((time_ms / 1000000) / duration * 100, 100)
                            await self._update_job_progress(job.job_id, job.user_id, progress)
                    except (ValueError, IndexError):
                        pass
            
            # Wait for process completion
            await process.wait()
            
            return process.returncode == 0
            
        except Exception as e:
            print(f"FFmpeg execution error: {str(e)}")
            return False
    
    async def _get_media_duration(self, file_path: str) -> Optional[float]:
        """Get media duration using FFprobe"""
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 
                'format=duration', '-of', 'csv=p=0', file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                duration_str = stdout.decode('utf-8').strip()
                return float(duration_str)
            
        except Exception as e:
            print(f"Error getting media duration: {str(e)}")
        
        return None
    
    async def _analyze_output_file(self, output_path: str) -> Dict[str, Any]:
        """Analyze output file to get metadata"""
        
        info = {
            "file_size": 0,
            "duration": None,
            "resolution": None,
            "bitrate": None,
            "codec": None
        }
        
        try:
            if os.path.exists(output_path):
                info["file_size"] = os.path.getsize(output_path)
            
            # Use FFprobe to get detailed info
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                probe_data = json.loads(stdout.decode('utf-8'))
                
                # Extract format info
                if 'format' in probe_data:
                    format_info = probe_data['format']
                    info["duration"] = float(format_info.get('duration', 0))
                    info["bitrate"] = format_info.get('bit_rate')
                
                # Extract stream info
                if 'streams' in probe_data:
                    for stream in probe_data['streams']:
                        if stream.get('codec_type') == 'video':
                            info["resolution"] = f"{stream.get('width')}x{stream.get('height')}"
                            info["codec"] = stream.get('codec_name')
                            break
                
        except Exception as e:
            print(f"Error analyzing output file: {str(e)}")
        
        return info
    
    async def _update_job_status(self, job_id: str, user_id: str, status: TranscodingStatus, 
                               error_message: Optional[str] = None):
        """Update job status in database"""
        
        update_data = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if error_message:
            update_data["error_message"] = error_message
        
        if status == TranscodingStatus.COMPLETED:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        self.transcoding_collection.update_one(
            {"job_id": job_id, "user_id": user_id},
            {"$set": update_data}
        )
    
    async def _update_job_progress(self, job_id: str, user_id: str, progress: float):
        """Update job progress percentage"""
        
        self.transcoding_collection.update_one(
            {"job_id": job_id, "user_id": user_id},
            {"$set": {"progress_percentage": progress}}
        )
    
    async def _update_job_timestamp(self, job_id: str, user_id: str, timestamp_field: str):
        """Update job timestamp"""
        
        self.transcoding_collection.update_one(
            {"job_id": job_id, "user_id": user_id},
            {"$set": {timestamp_field: datetime.now(timezone.utc).isoformat()}}
        )
    
    async def _update_job_completion(self, job_id: str, user_id: str, output_path: str, 
                                   output_size: int, output_info: Dict[str, Any]):
        """Update job with completion information"""
        
        update_data = {
            "output_file_path": output_path,
            "output_file_size": output_size,
            "output_resolution": output_info.get("resolution"),
            "output_bitrate": output_info.get("bitrate"),
            "actual_duration": output_info.get("duration"),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.transcoding_collection.update_one(
            {"job_id": job_id, "user_id": user_id},
            {"$set": update_data}
        )
    
    async def _increment_retry_count(self, job_id: str, user_id: str):
        """Increment retry count for a job"""
        
        self.transcoding_collection.update_one(
            {"job_id": job_id, "user_id": user_id},
            {"$inc": {"retry_count": 1}}
        )
    
    async def cancel_transcoding_job(self, job_id: str, user_id: str) -> bool:
        """Cancel a transcoding job"""
        
        try:
            result = self.transcoding_collection.update_one(
                {"job_id": job_id, "user_id": user_id, "status": {"$in": ["pending", "processing"]}},
                {"$set": {"status": TranscodingStatus.CANCELLED.value}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error cancelling transcoding job: {e}")
            return False
    
    def get_available_presets(self) -> Dict[str, TranscodingPreset]:
        """Get all available transcoding presets"""
        return self.presets
    
    def get_presets_for_platform(self, platform: str) -> List[TranscodingPreset]:
        """Get presets optimized for a specific platform"""
        return [preset for preset in self.presets.values() 
                if platform.lower() in [p.lower() for p in preset.platform_optimized]]
    
    def get_presets_for_format(self, output_format: OutputFormat) -> List[TranscodingPreset]:
        """Get presets for a specific output format"""
        return [preset for preset in self.presets.values() 
                if preset.output_format == output_format]
    
    async def get_transcoding_stats(self, user_id: str) -> Dict[str, Any]:
        """Get transcoding statistics for a user"""
        
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_size": {"$sum": {"$ifNull": ["$output_file_size", 0]}}
                }}
            ]
            
            results = list(self.transcoding_collection.aggregate(pipeline))
            
            stats = {
                "total_jobs": 0,
                "by_status": {},
                "total_output_size": 0,
                "average_job_time": 0
            }
            
            for result in results:
                status = result["_id"]
                count = result["count"]
                size = result["total_size"]
                
                stats["by_status"][status] = count
                stats["total_jobs"] += count
                stats["total_output_size"] += size
            
            return stats
            
        except Exception as e:
            print(f"Error getting transcoding stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_completed_jobs(self, older_than_days: int = 7) -> int:
        """Clean up completed transcoding jobs and their files"""
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
            
            # Find completed jobs older than cutoff
            old_jobs = list(self.transcoding_collection.find({
                "status": TranscodingStatus.COMPLETED.value,
                "completed_at": {"$lt": cutoff_date.isoformat()}
            }))
            
            cleaned_count = 0
            
            for job_data in old_jobs:
                try:
                    # Remove output file if it exists
                    if job_data.get("output_file_path"):
                        output_path = job_data["output_file_path"]
                        if os.path.exists(output_path):
                            os.remove(output_path)
                    
                    # Remove job record
                    self.transcoding_collection.delete_one({"_id": job_data["_id"]})
                    cleaned_count += 1
                    
                except Exception as e:
                    print(f"Error cleaning up job {job_data.get('job_id')}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0