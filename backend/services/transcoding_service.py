"""
Transcoding Service - Handles content transcoding and packaging for different platforms
Supports TV longform/episodic, OTT/social, Radio formats with platform-specific optimizations
"""

import os
import uuid
import json
import asyncio
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from pymongo import MongoClient
import ffmpeg
from pathlib import Path

class TranscodingProfile(str, Enum):
    # TV Formats
    TV_PRORES_HD = "tv_prores_hd"
    TV_XDCAM_HD = "tv_xdcam_hd"
    TV_IMF_PACKAGE = "tv_imf_package"
    
    # OTT/Streaming
    HLS_LADDER = "hls_ladder"
    DASH_LADDER = "dash_ladder"
    HEVC_4K = "hevc_4k"
    
    # Social Media
    YOUTUBE_HD = "youtube_hd"
    TIKTOK_VERTICAL = "tiktok_vertical"
    INSTAGRAM_SQUARE = "instagram_square"
    
    # Audio/Radio
    RADIO_MASTER_WAV = "radio_master_wav"
    STREAMING_AAC = "streaming_aac"
    PODCAST_MP3 = "podcast_mp3"

class AudioStandard(str, Enum):
    ATSC_A85 = "atsc_a85"  # -24 LKFS for US TV
    EBU_R128 = "ebu_r128"  # -23 LUFS for EU TV
    STREAMING = "streaming"  # -16 to -14 LUFS
    RADIO = "radio"  # Conservative peaks

class TranscodingJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    version_id: str
    user_id: str
    
    # Job configuration
    source_file_path: str
    profile: TranscodingProfile
    audio_standard: AudioStandard
    
    # Output specifications
    output_specifications: Dict[str, Any] = {}
    output_files: List[Dict[str, str]] = []
    
    # Job status
    status: str = "queued"  # queued, processing, completed, failed
    progress_percentage: float = 0.0
    
    # Processing details
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TranscodingService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        
        # Collections
        self.transcoding_jobs_collection = self.db['transcoding_jobs']
        
        # Output directory
        self.output_dir = "/tmp/bme_transcoded"
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Transcoding profiles configuration
        self.profiles_config = self._initialize_transcoding_profiles()
    
    def _initialize_transcoding_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize transcoding profile configurations"""
        
        return {
            # TV Longform/Episodic Profiles
            TranscodingProfile.TV_PRORES_HD.value: {
                "name": "ProRes HD for Broadcast",
                "video": {
                    "codec": "prores_ks",
                    "profile": "hq",
                    "resolution": "1920x1080",
                    "frame_rate": 29.97,
                    "pix_fmt": "yuv422p10le",
                    "color_range": "tv",
                    "color_primaries": "bt709",
                    "container": "mov"
                },
                "audio": {
                    "codec": "pcm_s24le",
                    "sample_rate": 48000,
                    "channels": 2,
                    "loudness_target": -24.0,
                    "true_peak_max": -2.0
                },
                "features": ["bars_tone", "slate", "2_pop"]
            },
            
            TranscodingProfile.HLS_LADDER.value: {
                "name": "HLS Multi-bitrate Ladder",
                "variants": [
                    {
                        "resolution": "3840x2160",
                        "bitrate": "15000k",
                        "frame_rate": 30
                    },
                    {
                        "resolution": "1920x1080", 
                        "bitrate": "8000k",
                        "frame_rate": 30
                    },
                    {
                        "resolution": "1280x720",
                        "bitrate": "4500k", 
                        "frame_rate": 30
                    },
                    {
                        "resolution": "854x480",
                        "bitrate": "2000k",
                        "frame_rate": 30
                    }
                ],
                "video": {
                    "codec": "libx264",
                    "profile": "high",
                    "level": "4.1",
                    "pix_fmt": "yuv420p",
                    "preset": "medium"
                },
                "audio": {
                    "codec": "aac",
                    "sample_rate": 48000,
                    "bitrate": "128k",
                    "channels": 2,
                    "loudness_target": -16.0
                },
                "container": "m3u8"
            },
            
            TranscodingProfile.YOUTUBE_HD.value: {
                "name": "YouTube HD Optimized",
                "video": {
                    "codec": "libx264",
                    "resolution": "1920x1080",
                    "frame_rate": 30,
                    "bitrate": "8000k",
                    "profile": "high",
                    "preset": "medium",
                    "pix_fmt": "yuv420p",
                    "container": "mp4"
                },
                "audio": {
                    "codec": "aac",
                    "sample_rate": 48000,
                    "bitrate": "192k",
                    "channels": 2,
                    "loudness_target": -14.0
                },
                "features": ["thumbnails", "chapters"]
            },
            
            TranscodingProfile.TIKTOK_VERTICAL.value: {
                "name": "TikTok Vertical Video",
                "video": {
                    "codec": "libx264",
                    "resolution": "1080x1920",
                    "frame_rate": 30,
                    "bitrate": "4000k",
                    "profile": "main",
                    "preset": "fast",
                    "max_duration": 180,
                    "container": "mp4"
                },
                "audio": {
                    "codec": "aac",
                    "sample_rate": 44100,
                    "bitrate": "128k",
                    "channels": 2,
                    "loudness_target": -14.0
                }
            },
            
            TranscodingProfile.RADIO_MASTER_WAV.value: {
                "name": "Radio Master WAV",
                "audio": {
                    "codec": "pcm_s16le",
                    "sample_rate": 44100,
                    "channels": 2,
                    "loudness_target": -16.0,
                    "true_peak_max": -1.0,
                    "container": "wav"
                },
                "features": ["intro_outro_timing", "clean_edit"]
            }
        }
    
    async def create_transcoding_job(self,
                                   content_id: str,
                                   version_id: str,
                                   user_id: str,
                                   source_file_path: str,
                                   profile: TranscodingProfile,
                                   audio_standard: AudioStandard = AudioStandard.STREAMING) -> TranscodingJob:
        """Create a new transcoding job"""
        
        try:
            # Get profile configuration
            profile_config = self.profiles_config.get(profile.value)
            if not profile_config:
                raise ValueError(f"Unknown transcoding profile: {profile.value}")
            
            # Create transcoding job
            job = TranscodingJob(
                content_id=content_id,
                version_id=version_id,
                user_id=user_id,
                source_file_path=source_file_path,
                profile=profile,
                audio_standard=audio_standard,
                output_specifications=profile_config
            )
            
            # Store job in database
            job_dict = job.dict()
            job_dict["created_at"] = job.created_at.isoformat()
            job_dict["updated_at"] = job.updated_at.isoformat()
            
            result = self.transcoding_jobs_collection.insert_one(job_dict)
            job.job_id = str(result.inserted_id)
            
            # Update with job_id
            self.transcoding_jobs_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"job_id": job.job_id}}
            )
            
            print(f"✅ Transcoding job created: {job.job_id}")
            return job
            
        except Exception as e:
            print(f"❌ Error creating transcoding job: {e}")
            raise
    
    async def process_transcoding_job(self, job_id: str) -> bool:
        """Process a transcoding job"""
        
        try:
            # Get job from database
            job_data = self.transcoding_jobs_collection.find_one({"job_id": job_id})
            if not job_data:
                raise ValueError("Transcoding job not found")
            
            job = TranscodingJob(**job_data)
            
            # Update job status
            await self._update_job_status(job_id, "processing", 0.0)
            job.started_at = datetime.now(timezone.utc)
            
            # Process based on profile type
            if job.profile in [TranscodingProfile.TV_PRORES_HD, TranscodingProfile.TV_XDCAM_HD]:
                output_files = await self._process_broadcast_format(job)
            elif job.profile in [TranscodingProfile.HLS_LADDER, TranscodingProfile.DASH_LADDER]:
                output_files = await self._process_streaming_ladder(job)
            elif job.profile in [TranscodingProfile.YOUTUBE_HD, TranscodingProfile.TIKTOK_VERTICAL]:
                output_files = await self._process_social_format(job)
            elif job.profile in [TranscodingProfile.RADIO_MASTER_WAV]:
                output_files = await self._process_audio_format(job)
            else:
                raise ValueError(f"Unsupported profile: {job.profile}")
            
            # Update job completion
            job.completed_at = datetime.now(timezone.utc)
            job.processing_time_seconds = (job.completed_at - job.started_at).total_seconds()
            job.output_files = output_files
            
            await self._update_job_status(job_id, "completed", 100.0, output_files=output_files)
            
            print(f"✅ Transcoding job completed: {job_id}")
            return True
            
        except Exception as e:
            print(f"❌ Transcoding job failed: {e}")
            await self._update_job_status(job_id, "failed", error_message=str(e))
            return False
    
    async def _process_broadcast_format(self, job: TranscodingJob) -> List[Dict[str, str]]:
        """Process content for broadcast television"""
        
        try:
            profile_config = job.output_specifications
            video_config = profile_config.get("video", {})
            audio_config = profile_config.get("audio", {})
            
            # Generate output filename
            output_filename = f"{job.content_id}_{job.profile.value}.{video_config.get('container', 'mov')}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Build FFmpeg command for broadcast format
            input_stream = ffmpeg.input(job.source_file_path)
            
            # Video processing
            video_stream = input_stream.video
            if "resolution" in video_config:
                width, height = map(int, video_config["resolution"].split('x'))
                video_stream = ffmpeg.filter(video_stream, 'scale', width, height)
            
            # Apply broadcast safe colors
            if video_config.get("color_range") == "tv":
                video_stream = ffmpeg.filter(video_stream, 'scale', out_color_matrix='bt709', out_range='tv')
                
            # Audio processing with loudness normalization
            audio_stream = input_stream.audio
            if "loudness_target" in audio_config:
                loudness_target = audio_config["loudness_target"]
                # Apply loudness normalization (simplified - in production would use loudnorm filter)
                audio_stream = ffmpeg.filter(audio_stream, 'volume', '0.8')
            
            # Combine and output
            output = ffmpeg.output(
                video_stream, 
                audio_stream,
                output_path,
                vcodec=video_config.get("codec", "prores_ks"),
                acodec=audio_config.get("codec", "pcm_s24le"),
                **{"r": video_config.get("frame_rate", 29.97)}
            )
            
            # Run transcoding
            await asyncio.create_subprocess_exec(*ffmpeg.compile(output))
            
            # Update progress
            await self._update_job_status(job.job_id, "processing", 50.0)
            
            # Add slate and bars/tone if required
            features = profile_config.get("features", [])
            if "slate" in features:
                await self._add_title_slate(output_path, job.content_id)
            if "bars_tone" in features:
                await self._add_bars_tone(output_path)
            
            await self._update_job_status(job.job_id, "processing", 90.0)
            
            return [{
                "type": "primary",
                "path": output_path,
                "filename": output_filename,
                "format": video_config.get("container", "mov"),
                "size_bytes": os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }]
            
        except Exception as e:
            print(f"Error processing broadcast format: {e}")
            raise
    
    async def _process_streaming_ladder(self, job: TranscodingJob) -> List[Dict[str, str]]:
        """Process content for OTT streaming with multiple bitrates"""
        
        try:
            profile_config = job.output_specifications
            variants = profile_config.get("variants", [])
            
            output_files = []
            
            for i, variant in enumerate(variants):
                # Generate output for each variant
                resolution = variant.get("resolution")
                bitrate = variant.get("bitrate")
                
                output_filename = f"{job.content_id}_{resolution}_{bitrate}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Build FFmpeg command for this variant
                input_stream = ffmpeg.input(job.source_file_path)
                
                width, height = map(int, resolution.split('x'))
                video_stream = ffmpeg.filter(input_stream.video, 'scale', width, height)
                
                output = ffmpeg.output(
                    video_stream,
                    input_stream.audio,
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    **{"b:v": bitrate, "b:a": "128k"}
                )
                
                # Run transcoding for this variant
                await asyncio.create_subprocess_exec(*ffmpeg.compile(output))
                
                output_files.append({
                    "type": "variant",
                    "resolution": resolution,
                    "bitrate": bitrate,
                    "path": output_path,
                    "filename": output_filename,
                    "format": "mp4",
                    "size_bytes": os.path.getsize(output_path) if os.path.exists(output_path) else 0
                })
                
                # Update progress
                progress = ((i + 1) / len(variants)) * 80.0
                await self._update_job_status(job.job_id, "processing", progress)
            
            # Generate HLS playlist
            playlist_path = os.path.join(self.output_dir, f"{job.content_id}_playlist.m3u8")
            await self._generate_hls_playlist(output_files, playlist_path)
            
            output_files.append({
                "type": "playlist",
                "path": playlist_path,
                "filename": f"{job.content_id}_playlist.m3u8",
                "format": "m3u8",
                "size_bytes": os.path.getsize(playlist_path) if os.path.exists(playlist_path) else 0
            })
            
            return output_files
            
        except Exception as e:
            print(f"Error processing streaming ladder: {e}")
            raise
    
    async def _process_social_format(self, job: TranscodingJob) -> List[Dict[str, str]]:
        """Process content for social media platforms"""
        
        try:
            profile_config = job.output_specifications
            video_config = profile_config.get("video", {})
            audio_config = profile_config.get("audio", {})
            
            output_filename = f"{job.content_id}_{job.profile.value}.{video_config.get('container', 'mp4')}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Build FFmpeg command for social format
            input_stream = ffmpeg.input(job.source_file_path)
            
            # Handle aspect ratio conversion for vertical video
            if job.profile == TranscodingProfile.TIKTOK_VERTICAL:
                width, height = map(int, video_config["resolution"].split('x'))
                video_stream = ffmpeg.filter(
                    input_stream.video, 
                    'scale', 
                    width, height,
                    force_original_aspect_ratio='decrease'
                )
                # Add padding for vertical format
                video_stream = ffmpeg.filter(
                    video_stream,
                    'pad',
                    width, height,
                    '(ow-iw)/2', '(oh-ih)/2',
                    color='black'
                )
            else:
                width, height = map(int, video_config["resolution"].split('x'))
                video_stream = ffmpeg.filter(input_stream.video, 'scale', width, height)
            
            # Audio processing for social media
            audio_stream = input_stream.audio
            
            # Trim if max duration specified
            if "max_duration" in video_config:
                max_duration = video_config["max_duration"]
                video_stream = ffmpeg.filter(video_stream, 'trim', duration=max_duration)
                audio_stream = ffmpeg.filter(audio_stream, 'atrim', duration=max_duration)
            
            output = ffmpeg.output(
                video_stream,
                audio_stream,
                output_path,
                vcodec=video_config.get("codec", "libx264"),
                acodec=audio_config.get("codec", "aac"),
                **{"b:v": video_config.get("bitrate", "4000k")}
            )
            
            await asyncio.create_subprocess_exec(*ffmpeg.compile(output))
            
            await self._update_job_status(job.job_id, "processing", 80.0)
            
            # Generate thumbnails if required
            output_files = [{
                "type": "primary",
                "path": output_path,
                "filename": output_filename,
                "format": video_config.get("container", "mp4"),
                "size_bytes": os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }]
            
            if "thumbnails" in profile_config.get("features", []):
                thumbnail_files = await self._generate_thumbnails(output_path, job.content_id)
                output_files.extend(thumbnail_files)
            
            return output_files
            
        except Exception as e:
            print(f"Error processing social format: {e}")
            raise
    
    async def _process_audio_format(self, job: TranscodingJob) -> List[Dict[str, str]]:
        """Process audio content for radio/streaming"""
        
        try:
            profile_config = job.output_specifications
            audio_config = profile_config.get("audio", {})
            
            output_filename = f"{job.content_id}_{job.profile.value}.{audio_config.get('container', 'wav')}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Build FFmpeg command for audio
            input_stream = ffmpeg.input(job.source_file_path)
            
            audio_stream = input_stream.audio
            
            # Apply loudness normalization based on standard
            if job.audio_standard == AudioStandard.RADIO:
                # Conservative peaks for radio
                audio_stream = ffmpeg.filter(audio_stream, 'volume', '0.9')
            elif job.audio_standard == AudioStandard.ATSC_A85:
                # -24 LKFS target for US TV
                audio_stream = ffmpeg.filter(audio_stream, 'loudnorm', I=-24.0, TP=-2.0)
            elif job.audio_standard == AudioStandard.EBU_R128:
                # -23 LUFS target for EU TV
                audio_stream = ffmpeg.filter(audio_stream, 'loudnorm', I=-23.0, TP=-1.0)
            
            output = ffmpeg.output(
                audio_stream,
                output_path,
                acodec=audio_config.get("codec", "pcm_s16le"),
                ar=audio_config.get("sample_rate", 44100),
                ac=audio_config.get("channels", 2)
            )
            
            await asyncio.create_subprocess_exec(*ffmpeg.compile(output))
            
            await self._update_job_status(job.job_id, "processing", 80.0)
            
            output_files = [{
                "type": "primary",
                "path": output_path,
                "filename": output_filename,
                "format": audio_config.get("container", "wav"),
                "size_bytes": os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }]
            
            # Create radio edit if required
            features = profile_config.get("features", [])
            if "clean_edit" in features:
                clean_edit_file = await self._create_clean_edit(output_path, job.content_id)
                output_files.append(clean_edit_file)
            
            return output_files
            
        except Exception as e:
            print(f"Error processing audio format: {e}")
            raise
    
    async def _update_job_status(self, 
                               job_id: str, 
                               status: str, 
                               progress: float = None,
                               error_message: str = None,
                               output_files: List[Dict[str, str]] = None):
        """Update transcoding job status"""
        
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if progress is not None:
            update_data["progress_percentage"] = progress
        
        if error_message:
            update_data["error_message"] = error_message
        
        if output_files:
            update_data["output_files"] = output_files
        
        if status == "processing" and progress == 0.0:
            update_data["started_at"] = datetime.now(timezone.utc).isoformat()
        elif status == "completed":
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        self.transcoding_jobs_collection.update_one(
            {"job_id": job_id},
            {"$set": update_data}
        )
    
    async def _add_title_slate(self, video_path: str, content_id: str):
        """Add title slate to beginning of video"""
        # Placeholder for title slate generation
        pass
    
    async def _add_bars_tone(self, video_path: str):
        """Add bars and tone to beginning of video"""
        # Placeholder for bars/tone generation
        pass
    
    async def _generate_hls_playlist(self, variant_files: List[Dict[str, str]], playlist_path: str):
        """Generate HLS playlist file"""
        
        playlist_content = "#EXTM3U\n#EXT-X-VERSION:3\n"
        
        for variant in variant_files:
            if variant["type"] == "variant":
                resolution = variant["resolution"]
                bitrate = int(variant["bitrate"].replace('k', '000'))
                
                playlist_content += f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={resolution}\n"
                playlist_content += f"{variant['filename']}\n"
        
        with open(playlist_path, 'w') as f:
            f.write(playlist_content)
    
    async def _generate_thumbnails(self, video_path: str, content_id: str) -> List[Dict[str, str]]:
        """Generate thumbnail images from video"""
        
        thumbnails = []
        
        for i in range(3):  # Generate 3 thumbnails
            thumbnail_filename = f"{content_id}_thumb_{i+1}.jpg"
            thumbnail_path = os.path.join(self.output_dir, thumbnail_filename)
            
            # Extract frame at different time positions
            time_position = f"00:00:{i*10:02d}"
            
            # Use FFmpeg to extract thumbnail
            thumbnail_cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', time_position,
                '-vframes', '1',
                '-q:v', '2',
                '-y', thumbnail_path
            ]
            
            process = await asyncio.create_subprocess_exec(*thumbnail_cmd)
            await process.wait()
            
            if os.path.exists(thumbnail_path):
                thumbnails.append({
                    "type": "thumbnail",
                    "index": i + 1,
                    "path": thumbnail_path,
                    "filename": thumbnail_filename,
                    "format": "jpg",
                    "size_bytes": os.path.getsize(thumbnail_path)
                })
        
        return thumbnails
    
    async def _create_clean_edit(self, audio_path: str, content_id: str) -> Dict[str, str]:
        """Create clean edit of audio content for radio"""
        
        clean_filename = f"{content_id}_clean_edit.wav"
        clean_path = os.path.join(self.output_dir, clean_filename)
        
        # Placeholder for clean edit processing (would remove explicit content)
        import shutil
        shutil.copy2(audio_path, clean_path)
        
        return {
            "type": "clean_edit",
            "path": clean_path,
            "filename": clean_filename,
            "format": "wav",
            "size_bytes": os.path.getsize(clean_path)
        }
    
    async def get_job_status(self, job_id: str) -> Optional[TranscodingJob]:
        """Get status of a transcoding job"""
        
        try:
            job_data = self.transcoding_jobs_collection.find_one({"job_id": job_id})
            if job_data:
                job_data["_id"] = str(job_data["_id"])
                return TranscodingJob(**job_data)
            return None
            
        except Exception as e:
            print(f"Error getting job status: {e}")
            return None
    
    async def list_user_jobs(self, user_id: str, status: str = None) -> List[TranscodingJob]:
        """List transcoding jobs for a user"""
        
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            
            jobs_data = list(self.transcoding_jobs_collection.find(query).sort("created_at", -1))
            
            jobs = []
            for job_data in jobs_data:
                job_data["_id"] = str(job_data["_id"])
                jobs.append(TranscodingJob(**job_data))
            
            return jobs
            
        except Exception as e:
            print(f"Error listing user jobs: {e}")
            return []