"""
Format Optimization Service - Function 2: Transcoding & Format Optimization
Handles format-specific optimizations, quality presets management, and platform requirements.
"""

import os
import uuid
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from pymongo import MongoClient

from transcoding_service import OutputFormat, QualityPreset, TranscodingPreset

class PlatformType(str, Enum):
    STREAMING_MUSIC = "streaming_music"
    STREAMING_VIDEO = "streaming_video" 
    SOCIAL_MEDIA = "social_media"
    BROADCAST = "broadcast"
    PODCAST = "podcast"
    DOWNLOAD = "download"
    WEB = "web"

class OptimizationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    platform_types: List[PlatformType] = []
    specific_platforms: List[str] = []  # Specific platform names
    content_types: List[str] = []  # audio, video, image
    conditions: Dict[str, Any] = {}  # Conditions that trigger this rule
    optimizations: Dict[str, Any] = {}  # Optimization parameters to apply
    priority: int = 0  # Higher number = higher priority
    is_active: bool = True

class PlatformRequirement(BaseModel):
    platform_name: str
    platform_type: PlatformType
    supported_formats: List[OutputFormat] = []
    preferred_formats: List[OutputFormat] = []
    max_file_size: Optional[int] = None  # bytes
    max_duration: Optional[int] = None  # seconds
    min_quality: Optional[QualityPreset] = None
    max_quality: Optional[QualityPreset] = None
    required_bitrates: Dict[str, str] = {}  # video/audio bitrate requirements
    supported_codecs: Dict[str, List[str]] = {}  # video/audio codec lists
    aspect_ratios: List[str] = []  # Supported aspect ratios
    frame_rates: List[int] = []  # Supported frame rates
    special_requirements: Dict[str, Any] = {}
    metadata_requirements: List[str] = []  # Required metadata fields

class FormatOptimizationService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        self.optimization_collection = self.db['format_optimizations']
        
        # Initialize platform requirements and optimization rules
        self.platform_requirements = self._initialize_platform_requirements()
        self.optimization_rules = self._initialize_optimization_rules()
        
    def _initialize_platform_requirements(self) -> Dict[str, PlatformRequirement]:
        """Initialize platform-specific format requirements"""
        requirements = {}
        
        # Music Streaming Platforms
        requirements["spotify"] = PlatformRequirement(
            platform_name="spotify",
            platform_type=PlatformType.STREAMING_MUSIC,
            supported_formats=[OutputFormat.MP3, OutputFormat.AAC, OutputFormat.OGG],
            preferred_formats=[OutputFormat.OGG],
            max_file_size=100 * 1024 * 1024,  # 100MB
            max_duration=600,  # 10 minutes for normal tracks
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"audio": "320k"},
            supported_codecs={"audio": ["vorbis", "mp3", "aac"]},
            metadata_requirements=["title", "artist", "isrc", "duration"]
        )
        
        requirements["apple_music"] = PlatformRequirement(
            platform_name="apple_music",
            platform_type=PlatformType.STREAMING_MUSIC,
            supported_formats=[OutputFormat.AAC, OutputFormat.MP3],
            preferred_formats=[OutputFormat.AAC],
            max_file_size=200 * 1024 * 1024,  # 200MB
            min_quality=QualityPreset.HIGH,
            required_bitrates={"audio": "256k"},
            supported_codecs={"audio": ["aac", "mp3"]},
            metadata_requirements=["title", "artist", "album", "isrc"]
        )
        
        requirements["soundcloud"] = PlatformRequirement(
            platform_name="soundcloud",
            platform_type=PlatformType.STREAMING_MUSIC,
            supported_formats=[OutputFormat.MP3, OutputFormat.AAC],
            preferred_formats=[OutputFormat.MP3],
            max_file_size=80 * 1024 * 1024,  # 80MB
            max_duration=600,
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"audio": "320k"},
            supported_codecs={"audio": ["mp3", "aac"]},
            metadata_requirements=["title", "artist"]
        )
        
        # Video Streaming Platforms
        requirements["youtube"] = PlatformRequirement(
            platform_name="youtube",
            platform_type=PlatformType.STREAMING_VIDEO,
            supported_formats=[OutputFormat.MP4, OutputFormat.WEBM],
            preferred_formats=[OutputFormat.MP4],
            max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
            max_duration=43200,  # 12 hours
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"video": "2500k", "audio": "192k"},
            supported_codecs={"video": ["h264", "vp9"], "audio": ["aac", "opus"]},
            aspect_ratios=["16:9", "4:3", "1:1", "9:16"],
            frame_rates=[24, 25, 30, 48, 50, 60],
            metadata_requirements=["title", "description", "tags"]
        )
        
        requirements["tiktok"] = PlatformRequirement(
            platform_name="tiktok",
            platform_type=PlatformType.SOCIAL_MEDIA,
            supported_formats=[OutputFormat.MP4],
            preferred_formats=[OutputFormat.MP4],
            max_file_size=500 * 1024 * 1024,  # 500MB
            max_duration=180,  # 3 minutes
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"video": "1500k", "audio": "128k"},
            supported_codecs={"video": ["h264"], "audio": ["aac"]},
            aspect_ratios=["9:16", "1:1"],  # Vertical and square preferred
            frame_rates=[30, 60],
            special_requirements={
                "vertical_preferred": True,
                "min_resolution": "720x1280",
                "max_resolution": "1080x1920"
            }
        )
        
        requirements["instagram"] = PlatformRequirement(
            platform_name="instagram",
            platform_type=PlatformType.SOCIAL_MEDIA,
            supported_formats=[OutputFormat.MP4],
            preferred_formats=[OutputFormat.MP4],
            max_file_size=100 * 1024 * 1024,  # 100MB
            max_duration=60,  # 1 minute for feed posts
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"video": "2000k", "audio": "128k"},
            supported_codecs={"video": ["h264"], "audio": ["aac"]},
            aspect_ratios=["1:1", "4:5", "9:16"],
            frame_rates=[30],
            special_requirements={
                "square_preferred": True,
                "min_resolution": "600x600",
                "max_resolution": "1080x1080"
            }
        )
        
        requirements["facebook"] = PlatformRequirement(
            platform_name="facebook",
            platform_type=PlatformType.SOCIAL_MEDIA,
            supported_formats=[OutputFormat.MP4, OutputFormat.WEBM],
            preferred_formats=[OutputFormat.MP4],
            max_file_size=1024 * 1024 * 1024,  # 1GB  
            max_duration=240,  # 4 minutes
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"video": "2000k", "audio": "192k"},
            supported_codecs={"video": ["h264", "vp9"], "audio": ["aac", "opus"]},
            aspect_ratios=["16:9", "1:1", "4:5"],
            frame_rates=[30, 60]
        )
        
        requirements["twitter"] = PlatformRequirement(
            platform_name="twitter",
            platform_type=PlatformType.SOCIAL_MEDIA,
            supported_formats=[OutputFormat.MP4],
            preferred_formats=[OutputFormat.MP4],
            max_file_size=512 * 1024 * 1024,  # 512MB
            max_duration=140,  # 2 minutes 20 seconds
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"video": "1500k", "audio": "128k"},
            supported_codecs={"video": ["h264"], "audio": ["aac"]},
            aspect_ratios=["16:9", "1:1"],
            frame_rates=[30, 60]
        )
        
        # Podcast Platforms
        requirements["podcast"] = PlatformRequirement(
            platform_name="podcast",
            platform_type=PlatformType.PODCAST,
            supported_formats=[OutputFormat.MP3, OutputFormat.AAC],
            preferred_formats=[OutputFormat.MP3],
            max_file_size=250 * 1024 * 1024,  # 250MB
            max_duration=14400,  # 4 hours
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"audio": "128k"},
            supported_codecs={"audio": ["mp3", "aac"]},
            metadata_requirements=["title", "description", "author", "duration"]
        )
        
        # Web/HTML5 Video
        requirements["web"] = PlatformRequirement(
            platform_name="web",
            platform_type=PlatformType.WEB,
            supported_formats=[OutputFormat.MP4, OutputFormat.WEBM],
            preferred_formats=[OutputFormat.MP4, OutputFormat.WEBM],
            max_file_size=500 * 1024 * 1024,  # 500MB
            min_quality=QualityPreset.MEDIUM,
            required_bitrates={"video": "2000k", "audio": "192k"},
            supported_codecs={"video": ["h264", "vp9"], "audio": ["aac", "opus"]},
            aspect_ratios=["16:9", "4:3"],
            frame_rates=[24, 30, 60],
            special_requirements={
                "progressive_download": True,
                "streaming_optimized": True
            }
        )
        
        return requirements
    
    def _initialize_optimization_rules(self) -> List[OptimizationRule]:
        """Initialize format optimization rules"""
        rules = []
        
        # Mobile optimization rule
        rules.append(OptimizationRule(
            name="Mobile Optimization",
            description="Optimize content for mobile devices and low bandwidth",
            platform_types=[PlatformType.SOCIAL_MEDIA],
            specific_platforms=["tiktok", "instagram", "snapchat"],
            content_types=["video"],
            conditions={
                "target_device": "mobile",
                "bandwidth": "low"
            },
            optimizations={
                "max_resolution": "720p",
                "max_bitrate": "1500k",
                "frame_rate": 30,
                "audio_bitrate": "128k"
            },
            priority=10
        ))
        
        # High quality streaming rule
        rules.append(OptimizationRule(
            name="High Quality Streaming",
            description="Optimize for high-quality streaming platforms",
            platform_types=[PlatformType.STREAMING_MUSIC, PlatformType.STREAMING_VIDEO],
            specific_platforms=["spotify", "apple_music", "youtube", "vimeo"],
            conditions={
                "quality_preference": "high",
                "bandwidth": "high"
            },
            optimizations={
                "min_resolution": "1080p",
                "min_bitrate": "5000k",
                "audio_bitrate": "320k",
                "codec": "h264_high"
            },
            priority=20
        ))
        
        # Web compatibility rule
        rules.append(OptimizationRule(
            name="Web Compatibility",
            description="Ensure maximum web browser compatibility",
            platform_types=[PlatformType.WEB],
            content_types=["video", "audio"],
            conditions={
                "target": "web_browsers"
            },
            optimizations={
                "format": "mp4",
                "video_codec": "h264",
                "audio_codec": "aac",
                "profile": "baseline",
                "progressive": True
            },
            priority=15
        ))
        
        # Podcast optimization rule
        rules.append(OptimizationRule(
            name="Podcast Optimization",
            description="Optimize audio content for podcast distribution",
            platform_types=[PlatformType.PODCAST],
            content_types=["audio"],
            conditions={
                "content_type": "podcast",
                "duration": {"min": 300}  # 5+ minutes
            },
            optimizations={
                "format": "mp3",
                "audio_bitrate": "128k",
                "mono": False,
                "normalize_audio": True,
                "remove_silence": True
            },
            priority=18
        ))
        
        # Social media vertical video rule
        rules.append(OptimizationRule(
            name="Vertical Video Optimization",
            description="Optimize vertical videos for social media",
            specific_platforms=["tiktok", "instagram_stories", "youtube_shorts"],
            content_types=["video"],
            conditions={
                "aspect_ratio": "vertical",
                "platform_type": "social_media"
            },
            optimizations={
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "frame_rate": 30,
                "video_bitrate": "2500k",
                "audio_bitrate": "192k"
            },
            priority=25
        ))
        
        # Bandwidth optimization rule
        rules.append(OptimizationRule(
            name="Low Bandwidth Optimization",
            description="Optimize for low bandwidth conditions",
            conditions={
                "bandwidth_limit": True,
                "file_size_limit": {"max": 50 * 1024 * 1024}  # 50MB
            },
            optimizations={
                "max_resolution": "480p",
                "video_bitrate": "800k",
                "audio_bitrate": "96k",
                "frame_rate": 24,
                "two_pass": True
            },
            priority=12
        ))
        
        return rules
    
    def get_platform_requirements(self, platform_name: str) -> Optional[PlatformRequirement]:
        """Get format requirements for a specific platform"""
        return self.platform_requirements.get(platform_name.lower())
    
    def get_platforms_by_type(self, platform_type: PlatformType) -> List[PlatformRequirement]:
        """Get all platforms of a specific type"""
        return [req for req in self.platform_requirements.values() 
                if req.platform_type == platform_type]
    
    def get_supported_formats_for_platform(self, platform_name: str) -> List[OutputFormat]:
        """Get supported formats for a platform"""
        req = self.get_platform_requirements(platform_name)
        return req.supported_formats if req else []
    
    def get_optimal_format_for_platform(self, platform_name: str, 
                                      content_type: str = "video") -> Optional[OutputFormat]:
        """Get the optimal format for a specific platform"""
        req = self.get_platform_requirements(platform_name)
        if not req:
            return None
        
        # Return preferred format if available
        if req.preferred_formats:
            return req.preferred_formats[0]
        
        # Otherwise return first supported format
        if req.supported_formats:
            return req.supported_formats[0]
        
        return None
    
    def validate_content_for_platform(self, platform_name: str, 
                                    content_metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate if content meets platform requirements"""
        req = self.get_platform_requirements(platform_name)
        if not req:
            return False, [f"Platform {platform_name} not supported"]
        
        issues = []
        
        # Check file size
        if req.max_file_size and content_metadata.get("file_size", 0) > req.max_file_size:
            max_mb = req.max_file_size / (1024 * 1024)
            issues.append(f"File size exceeds {max_mb:.1f}MB limit")
        
        # Check duration
        if req.max_duration and content_metadata.get("duration", 0) > req.max_duration:
            max_min = req.max_duration / 60
            issues.append(f"Duration exceeds {max_min:.1f} minute limit")
        
        # Check format
        content_format = content_metadata.get("format")
        if content_format and content_format not in [f.value for f in req.supported_formats]:
            issues.append(f"Format {content_format} not supported. Supported: {[f.value for f in req.supported_formats]}")
        
        # Check resolution for video content
        if content_metadata.get("content_type") == "video":
            resolution = content_metadata.get("resolution")
            if resolution and req.special_requirements:
                min_res = req.special_requirements.get("min_resolution")
                max_res = req.special_requirements.get("max_resolution")
                
                if min_res and not self._compare_resolution(resolution, min_res, ">="):
                    issues.append(f"Resolution {resolution} below minimum {min_res}")
                
                if max_res and not self._compare_resolution(resolution, max_res, "<="):
                    issues.append(f"Resolution {resolution} exceeds maximum {max_res}")
        
        # Check aspect ratio
        aspect_ratio = content_metadata.get("aspect_ratio")
        if aspect_ratio and req.aspect_ratios and aspect_ratio not in req.aspect_ratios:
            issues.append(f"Aspect ratio {aspect_ratio} not supported. Supported: {req.aspect_ratios}")
        
        # Check frame rate
        frame_rate = content_metadata.get("frame_rate")
        if frame_rate and req.frame_rates and frame_rate not in req.frame_rates:
            issues.append(f"Frame rate {frame_rate} not supported. Supported: {req.frame_rates}")
        
        # Check required metadata
        for required_field in req.metadata_requirements:
            if not content_metadata.get(required_field):
                issues.append(f"Required metadata field missing: {required_field}")
        
        return len(issues) == 0, issues
    
    def get_optimization_recommendations(self, platform_name: str, 
                                       content_metadata: Dict[str, Any],
                                       user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get optimization recommendations for specific platform and content"""
        
        recommendations = {
            "platform": platform_name,
            "optimizations": {},
            "format_changes": {},
            "quality_adjustments": {},
            "special_requirements": {},
            "estimated_file_size_reduction": 0,
            "estimated_quality_impact": "none"
        }
        
        req = self.get_platform_requirements(platform_name)
        if not req:
            return recommendations
        
        user_preferences = user_preferences or {}
        content_type = content_metadata.get("content_type", "video")
        
        # Format optimization
        current_format = content_metadata.get("format")
        optimal_format = self.get_optimal_format_for_platform(platform_name, content_type)
        
        if optimal_format and optimal_format.value != current_format:
            recommendations["format_changes"]["target_format"] = optimal_format.value
            recommendations["format_changes"]["reason"] = f"Optimized for {platform_name}"
        
        # Resolution optimization
        if content_type == "video":
            current_resolution = content_metadata.get("resolution")
            if current_resolution and req.special_requirements:
                target_res = self._get_optimal_resolution(current_resolution, req, user_preferences)
                if target_res != current_resolution:
                    recommendations["quality_adjustments"]["target_resolution"] = target_res
        
        # Bitrate optimization
        current_video_bitrate = content_metadata.get("video_bitrate")
        current_audio_bitrate = content_metadata.get("audio_bitrate")
        
        if req.required_bitrates:
            if "video" in req.required_bitrates and current_video_bitrate:
                target_bitrate = req.required_bitrates["video"]
                if target_bitrate != current_video_bitrate:
                    recommendations["quality_adjustments"]["target_video_bitrate"] = target_bitrate
            
            if "audio" in req.required_bitrates and current_audio_bitrate:
                target_bitrate = req.required_bitrates["audio"]
                if target_bitrate != current_audio_bitrate:
                    recommendations["quality_adjustments"]["target_audio_bitrate"] = target_bitrate
        
        # Apply optimization rules
        applicable_rules = self._get_applicable_rules(platform_name, content_metadata, user_preferences)
        for rule in sorted(applicable_rules, key=lambda x: x.priority, reverse=True):
            for opt_key, opt_value in rule.optimizations.items():
                recommendations["optimizations"][opt_key] = opt_value
        
        # Special platform requirements
        if req.special_requirements:
            recommendations["special_requirements"] = req.special_requirements.copy()
        
        # Estimate impact
        recommendations.update(self._estimate_optimization_impact(content_metadata, recommendations))
        
        return recommendations
    
    def _get_applicable_rules(self, platform_name: str, content_metadata: Dict[str, Any], 
                            user_preferences: Dict[str, Any]) -> List[OptimizationRule]:
        """Get optimization rules applicable to the given context"""
        applicable_rules = []
        
        req = self.get_platform_requirements(platform_name)
        platform_type = req.platform_type if req else None
        content_type = content_metadata.get("content_type", "video")
        
        for rule in self.optimization_rules:
            if not rule.is_active:
                continue
            
            # Check platform type match
            if rule.platform_types and platform_type not in rule.platform_types:
                continue
            
            # Check specific platform match
            if rule.specific_platforms and platform_name not in rule.specific_platforms:
                continue
            
            # Check content type match
            if rule.content_types and content_type not in rule.content_types:
                continue
            
            # Check conditions
            if not self._evaluate_rule_conditions(rule.conditions, content_metadata, user_preferences):
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    def _evaluate_rule_conditions(self, conditions: Dict[str, Any], 
                                 content_metadata: Dict[str, Any],
                                 user_preferences: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        if not conditions:
            return True
        
        for condition_key, condition_value in conditions.items():
            # Check content metadata conditions
            if condition_key in content_metadata:
                content_value = content_metadata[condition_key]
                if isinstance(condition_value, dict):
                    # Handle range conditions
                    if "min" in condition_value and content_value < condition_value["min"]:
                        return False
                    if "max" in condition_value and content_value > condition_value["max"]:
                        return False
                elif content_value != condition_value:
                    return False
            
            # Check user preference conditions
            elif condition_key in user_preferences:
                if user_preferences[condition_key] != condition_value:
                    return False
            
            # Handle special conditions
            elif condition_key == "bandwidth":
                # This would be determined by user connection or preferences
                user_bandwidth = user_preferences.get("bandwidth", "medium")
                if user_bandwidth != condition_value:
                    return False
            
            elif condition_key == "target_device":
                user_device = user_preferences.get("device", "desktop")
                if user_device != condition_value:
                    return False
        
        return True
    
    def _get_optimal_resolution(self, current_resolution: str, 
                              req: PlatformRequirement,
                              user_preferences: Dict[str, Any]) -> str:
        """Determine optimal resolution for platform"""
        
        # Check special requirements first
        if req.special_requirements:
            min_res = req.special_requirements.get("min_resolution")
            max_res = req.special_requirements.get("max_resolution")
            
            if min_res and not self._compare_resolution(current_resolution, min_res, ">="):
                return min_res
            
            if max_res and not self._compare_resolution(current_resolution, max_res, "<="):
                return max_res
        
        # Consider user quality preference
        quality_pref = user_preferences.get("quality_preference", "medium")
        
        if quality_pref == "high" and req.min_quality == QualityPreset.HIGH:
            return "1920x1080"
        elif quality_pref == "low" or user_preferences.get("bandwidth") == "low":
            return "854x480"
        else:
            return "1280x720"  # Default medium quality
    
    def _compare_resolution(self, res1: str, res2: str, operator: str) -> bool:
        """Compare two resolutions"""
        try:
            w1, h1 = map(int, res1.split('x'))
            w2, h2 = map(int, res2.split('x'))
            
            pixels1 = w1 * h1
            pixels2 = w2 * h2
            
            if operator == ">=":
                return pixels1 >= pixels2
            elif operator == "<=":
                return pixels1 <= pixels2
            elif operator == "==":
                return pixels1 == pixels2
            
        except (ValueError, AttributeError):
            return False
        
        return False
    
    def _estimate_optimization_impact(self, content_metadata: Dict[str, Any], 
                                    recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate the impact of applying optimizations"""
        
        impact = {
            "estimated_file_size_reduction": 0,
            "estimated_quality_impact": "none",
            "processing_time_estimate": "medium"
        }
        
        current_size = content_metadata.get("file_size", 0)
        
        # Estimate size reduction based on format and quality changes
        size_reduction_factor = 1.0
        
        # Format change impact
        format_changes = recommendations.get("format_changes", {})
        if format_changes.get("target_format"):
            current_format = content_metadata.get("format", "")
            target_format = format_changes["target_format"]
            
            # Rough estimates for format efficiency
            format_efficiency = {
                "mp4": 1.0,
                "webm": 0.8,  # More efficient
                "avi": 1.2,   # Less efficient
                "mov": 1.1,
                "mp3": 1.0,
                "aac": 0.9,   # More efficient
                "ogg": 0.85,  # More efficient
                "flac": 3.0,  # Much larger
                "wav": 5.0    # Uncompressed
            }
            
            current_eff = format_efficiency.get(current_format.lower(), 1.0)
            target_eff = format_efficiency.get(target_format.lower(), 1.0)
            size_reduction_factor *= target_eff / current_eff
        
        # Resolution change impact
        quality_adj = recommendations.get("quality_adjustments", {})
        if quality_adj.get("target_resolution"):
            current_res = content_metadata.get("resolution", "1280x720")
            target_res = quality_adj["target_resolution"]
            
            try:
                current_pixels = int(current_res.split('x')[0]) * int(current_res.split('x')[1])
                target_pixels = int(target_res.split('x')[0]) * int(target_res.split('x')[1])
                
                # Size scales roughly with pixel count
                size_reduction_factor *= target_pixels / current_pixels
                
            except (ValueError, AttributeError):
                pass
        
        # Bitrate change impact
        if quality_adj.get("target_video_bitrate"):
            try:
                current_bitrate = int(content_metadata.get("video_bitrate", "2500k").replace('k', ''))
                target_bitrate = int(quality_adj["target_video_bitrate"].replace('k', ''))
                
                size_reduction_factor *= target_bitrate / current_bitrate
                
            except (ValueError, AttributeError):
                pass
        
        # Calculate estimated size reduction
        if size_reduction_factor < 1.0:
            impact["estimated_file_size_reduction"] = int((1.0 - size_reduction_factor) * current_size)
            impact["estimated_quality_impact"] = "slight_reduction"
        elif size_reduction_factor > 1.2:
            impact["estimated_quality_impact"] = "improvement"
        
        # Estimate processing time based on optimizations
        optimization_count = len(recommendations.get("optimizations", {}))
        if optimization_count > 5:
            impact["processing_time_estimate"] = "long"
        elif optimization_count > 2:
            impact["processing_time_estimate"] = "medium"
        else:
            impact["processing_time_estimate"] = "short"
        
        return impact
    
    def create_optimized_transcoding_preset(self, platform_name: str, 
                                          content_metadata: Dict[str, Any],
                                          user_preferences: Dict[str, Any] = None) -> Optional[TranscodingPreset]:
        """Create a custom transcoding preset optimized for specific platform"""
        
        recommendations = self.get_optimization_recommendations(platform_name, content_metadata, user_preferences)
        req = self.get_platform_requirements(platform_name)
        
        if not req:
            return None
        
        # Determine output format
        output_format = OutputFormat.MP4  # Default
        if recommendations.get("format_changes", {}).get("target_format"):
            format_str = recommendations["format_changes"]["target_format"]
            try:
                output_format = OutputFormat(format_str)
            except ValueError:
                pass
        
        # Build preset
        preset = TranscodingPreset(
            preset_id=f"optimized_{platform_name}_{uuid.uuid4().hex[:8]}",
            name=f"Optimized for {platform_name.title()}",
            description=f"Custom preset optimized for {platform_name} platform requirements",
            output_format=output_format,
            platform_optimized=[platform_name],
            quality_level=QualityPreset.CUSTOM
        )
        
        # Apply video settings
        if content_metadata.get("content_type") == "video":
            if req.supported_codecs.get("video"):
                preset.video_codec = req.supported_codecs["video"][0]  # Use first supported codec
            
            # Resolution
            if recommendations.get("quality_adjustments", {}).get("target_resolution"):
                preset.resolution = recommendations["quality_adjustments"]["target_resolution"]
            
            # Video bitrate
            if recommendations.get("quality_adjustments", {}).get("target_video_bitrate"):
                preset.video_bitrate = recommendations["quality_adjustments"]["target_video_bitrate"]
            elif req.required_bitrates.get("video"):
                preset.video_bitrate = req.required_bitrates["video"]
            
            # Frame rate
            if req.frame_rates:
                preset.frame_rate = req.frame_rates[0]  # Use first supported frame rate
        
        # Apply audio settings
        if req.supported_codecs.get("audio"):
            preset.audio_codec = req.supported_codecs["audio"][0]
        
        if recommendations.get("quality_adjustments", {}).get("target_audio_bitrate"):
            preset.audio_bitrate = recommendations["quality_adjustments"]["target_audio_bitrate"]
        elif req.required_bitrates.get("audio"):
            preset.audio_bitrate = req.required_bitrates["audio"]
        
        # Add optimization parameters
        ffmpeg_params = {}
        optimizations = recommendations.get("optimizations", {})
        
        for opt_key, opt_value in optimizations.items():
            if opt_key == "codec":
                if content_metadata.get("content_type") == "video":
                    preset.video_codec = opt_value
                else:
                    preset.audio_codec = opt_value
            elif opt_key in ["profile", "level", "preset", "crf", "two_pass"]:
                ffmpeg_params[opt_key] = opt_value
        
        preset.ffmpeg_params = ffmpeg_params
        
        return preset
    
    def get_multi_platform_optimization(self, target_platforms: List[str], 
                                      content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimization strategy for multiple platforms"""
        
        multi_optimization = {
            "target_platforms": target_platforms,
            "common_optimizations": {},
            "platform_specific": {},
            "recommended_approach": "single_optimized",  # or "multiple_versions"
            "compromise_settings": {}
        }
        
        platform_reqs = []
        for platform in target_platforms:
            req = self.get_platform_requirements(platform)
            if req:
                platform_reqs.append((platform, req))
        
        if not platform_reqs:
            return multi_optimization
        
        # Find common supported formats
        common_formats = set()
        for i, (platform, req) in enumerate(platform_reqs):
            platform_formats = set(f.value for f in req.supported_formats)
            if i == 0:
                common_formats = platform_formats
            else:
                common_formats &= platform_formats
        
        if common_formats:
            multi_optimization["common_optimizations"]["format"] = list(common_formats)[0]
            multi_optimization["recommended_approach"] = "single_optimized"
        else:
            multi_optimization["recommended_approach"] = "multiple_versions"
        
        # Find compromise settings
        if len(platform_reqs) > 1:
            # Find middle ground for bitrates, resolutions, etc.
            compromise = self._calculate_compromise_settings(platform_reqs, content_metadata)
            multi_optimization["compromise_settings"] = compromise
        
        # Get platform-specific requirements
        for platform, req in platform_reqs:
            platform_opts = self.get_optimization_recommendations(platform, content_metadata)
            multi_optimization["platform_specific"][platform] = platform_opts
        
        return multi_optimization
    
    def _calculate_compromise_settings(self, platform_reqs: List[Tuple[str, PlatformRequirement]], 
                                     content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate compromise settings that work across multiple platforms"""
        
        compromise = {}
        
        # Find the most restrictive file size limit
        max_sizes = [req.max_file_size for _, req in platform_reqs if req.max_file_size]
        if max_sizes:
            compromise["max_file_size"] = min(max_sizes)
        
        # Find the most restrictive duration limit
        max_durations = [req.max_duration for _, req in platform_reqs if req.max_duration]
        if max_durations:
            compromise["max_duration"] = min(max_durations)
        
        # Find common aspect ratios
        common_ratios = set()
        for i, (_, req) in enumerate(platform_reqs):
            if req.aspect_ratios:
                ratios = set(req.aspect_ratios)
                if i == 0:
                    common_ratios = ratios
                else:
                    common_ratios &= ratios
        
        if common_ratios:
            compromise["aspect_ratio"] = list(common_ratios)[0]
        
        # Calculate average bitrate requirements
        video_bitrates = []
        audio_bitrates = []
        
        for _, req in platform_reqs:
            if req.required_bitrates.get("video"):
                try:
                    bitrate = int(req.required_bitrates["video"].replace('k', ''))
                    video_bitrates.append(bitrate)
                except ValueError:
                    pass
            
            if req.required_bitrates.get("audio"):
                try:
                    bitrate = int(req.required_bitrates["audio"].replace('k', ''))
                    audio_bitrates.append(bitrate)
                except ValueError:
                    pass
        
        if video_bitrates:
            avg_video_bitrate = sum(video_bitrates) // len(video_bitrates)
            compromise["video_bitrate"] = f"{avg_video_bitrate}k"
        
        if audio_bitrates:
            avg_audio_bitrate = sum(audio_bitrates) // len(audio_bitrates)
            compromise["audio_bitrate"] = f"{avg_audio_bitrate}k"
        
        return compromise