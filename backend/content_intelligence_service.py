"""
Content Intelligence Service - Phase 1: Enhanced Platform Intelligence & Content Mapping
Provides smart platform mapping, content type optimization, and intelligent recommendations.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ContentType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"
    PODCAST = "podcast"
    MUSIC = "music"

class PlatformCapability(str, Enum):
    SHORT_FORM_VIDEO = "short_form_video"
    LONG_FORM_VIDEO = "long_form_video"
    LIVE_STREAMING = "live_streaming"
    AUDIO_STREAMING = "audio_streaming"
    IMAGE_SHARING = "image_sharing"
    STORY_FEATURE = "story_feature"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    COMMUNITY_FEATURES = "community_features"
    ADVERTISING = "advertising"
    E_COMMERCE = "e_commerce"
    PROFESSIONAL_NETWORK = "professional_network"

class ContentOptimizationRule(BaseModel):
    content_type: ContentType
    recommended_platforms: List[str]
    optimization_tips: List[str]
    format_requirements: Dict[str, Any]
    engagement_strategy: str
    best_posting_times: List[str]
    hashtag_strategy: Optional[str] = None
    cta_recommendations: List[str]

class PlatformIntelligence(BaseModel):
    platform_id: str
    primary_content_types: List[ContentType]
    capabilities: List[PlatformCapability]
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, str]
    monetization_options: List[str]
    content_length_limits: Dict[str, Any]
    optimal_posting_schedule: Dict[str, List[str]]
    platform_specific_features: List[str]
    cross_promotion_compatibility: List[str]

class ContentRecommendation(BaseModel):
    recommended_platforms: List[str]
    optimization_score: float
    content_adaptations: Dict[str, Dict[str, Any]]
    cross_promotion_strategy: Dict[str, List[str]]
    estimated_reach: Dict[str, int]
    monetization_potential: Dict[str, float]

class ContentIntelligenceService:
    def __init__(self):
        self.platform_intelligence = self._initialize_platform_intelligence()
        self.optimization_rules = self._initialize_optimization_rules()
        
    def _initialize_platform_intelligence(self) -> Dict[str, PlatformIntelligence]:
        """Initialize comprehensive platform intelligence data"""
        return {
            # Social Media Platforms
            "instagram": PlatformIntelligence(
                platform_id="instagram",
                primary_content_types=[ContentType.IMAGE, ContentType.VIDEO, ContentType.REEL, ContentType.STORY],
                capabilities=[
                    PlatformCapability.SHORT_FORM_VIDEO, PlatformCapability.IMAGE_SHARING,
                    PlatformCapability.STORY_FEATURE, PlatformCapability.MONETIZATION,
                    PlatformCapability.E_COMMERCE, PlatformCapability.ANALYTICS
                ],
                audience_demographics={
                    "age_range": "18-44",
                    "primary_gender": "female_skewed",
                    "interests": ["lifestyle", "fashion", "entertainment", "fitness"]
                },
                engagement_metrics={
                    "avg_engagement_rate": "1.22%",
                    "best_content_type": "video_reels",
                    "peak_activity": "lunch_evening"
                },
                monetization_options=["sponsored_posts", "shopping", "reels_play_bonus", "badges"],
                content_length_limits={
                    "video": "60_seconds_reels_90_seconds_stories",
                    "image": "multiple_carousel",
                    "caption": "2200_characters"
                },
                optimal_posting_schedule={
                    "weekdays": ["11:00-13:00", "19:00-21:00"],
                    "weekends": ["10:00-12:00", "14:00-16:00"]
                },
                platform_specific_features=["reels", "stories", "igtv", "shopping_tags", "live"],
                cross_promotion_compatibility=["threads", "facebook", "youtube", "tiktok"]
            ),
            
            "tiktok": PlatformIntelligence(
                platform_id="tiktok",
                primary_content_types=[ContentType.SHORT_FORM, ContentType.VIDEO, ContentType.MUSIC],
                capabilities=[
                    PlatformCapability.SHORT_FORM_VIDEO, PlatformCapability.LIVE_STREAMING,
                    PlatformCapability.MONETIZATION, PlatformCapability.ANALYTICS,
                    PlatformCapability.COMMUNITY_FEATURES
                ],
                audience_demographics={
                    "age_range": "16-34",
                    "primary_gender": "balanced",
                    "interests": ["entertainment", "music", "dance", "comedy", "trends"]
                },
                engagement_metrics={
                    "avg_engagement_rate": "5.96%",
                    "best_content_type": "trending_challenges",
                    "peak_activity": "evening_night"
                },
                monetization_options=["creator_fund", "live_gifts", "brand_partnerships", "tiktok_shop"],
                content_length_limits={
                    "video": "15_seconds_to_10_minutes",
                    "description": "300_characters"
                },
                optimal_posting_schedule={
                    "weekdays": ["15:00-18:00", "20:00-23:00"],
                    "weekends": ["12:00-15:00", "19:00-22:00"]
                },
                platform_specific_features=["duets", "effects", "sounds", "hashtag_challenges", "live"],
                cross_promotion_compatibility=["instagram", "youtube", "twitter", "snapchat"]
            ),
            
            "youtube": PlatformIntelligence(
                platform_id="youtube",
                primary_content_types=[ContentType.LONG_FORM, ContentType.VIDEO, ContentType.LIVE_STREAM],
                capabilities=[
                    PlatformCapability.LONG_FORM_VIDEO, PlatformCapability.SHORT_FORM_VIDEO,
                    PlatformCapability.LIVE_STREAMING, PlatformCapability.MONETIZATION,
                    PlatformCapability.ANALYTICS, PlatformCapability.COMMUNITY_FEATURES
                ],
                audience_demographics={
                    "age_range": "18-49",
                    "primary_gender": "male_skewed",
                    "interests": ["education", "entertainment", "gaming", "music", "how_to"]
                },
                engagement_metrics={
                    "avg_engagement_rate": "1.63%",
                    "best_content_type": "educational_entertainment",
                    "peak_activity": "afternoon_evening"
                },
                monetization_options=["ad_revenue", "channel_memberships", "super_chat", "merch_shelf"],
                content_length_limits={
                    "video": "up_to_12_hours",
                    "shorts": "60_seconds",
                    "title": "100_characters",
                    "description": "5000_characters"
                },
                optimal_posting_schedule={
                    "weekdays": ["14:00-16:00", "20:00-22:00"],
                    "weekends": ["09:00-11:00", "14:00-16:00"]
                },
                platform_specific_features=["shorts", "premieres", "live_streaming", "community_tab", "chapters"],
                cross_promotion_compatibility=["instagram", "tiktok", "twitter", "facebook"]
            ),
            
            "linkedin": PlatformIntelligence(
                platform_id="linkedin",
                primary_content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO, ContentType.LONG_FORM],
                capabilities=[
                    PlatformCapability.PROFESSIONAL_NETWORK, PlatformCapability.LONG_FORM_VIDEO,
                    PlatformCapability.ANALYTICS, PlatformCapability.ADVERTISING,
                    PlatformCapability.COMMUNITY_FEATURES
                ],
                audience_demographics={
                    "age_range": "25-54",
                    "primary_gender": "male_skewed",
                    "interests": ["business", "technology", "career", "industry_news", "networking"]
                },
                engagement_metrics={
                    "avg_engagement_rate": "2.05%",
                    "best_content_type": "industry_insights",
                    "peak_activity": "business_hours"
                },
                monetization_options=["sponsored_content", "lead_generation", "premium_features"],
                content_length_limits={
                    "video": "10_minutes",
                    "post": "3000_characters",
                    "article": "125000_characters"
                },
                optimal_posting_schedule={
                    "weekdays": ["08:00-10:00", "17:00-18:00"],
                    "weekends": ["minimal_activity"]
                },
                platform_specific_features=["articles", "live_events", "polls", "newsletters", "company_pages"],
                cross_promotion_compatibility=["twitter", "facebook", "youtube"]
            ),
            
            # Music Streaming Platforms
            "spotify": PlatformIntelligence(
                platform_id="spotify",
                primary_content_types=[ContentType.AUDIO, ContentType.MUSIC, ContentType.PODCAST],
                capabilities=[
                    PlatformCapability.AUDIO_STREAMING, PlatformCapability.ANALYTICS,
                    PlatformCapability.MONETIZATION, PlatformCapability.COMMUNITY_FEATURES
                ],
                audience_demographics={
                    "age_range": "18-44",
                    "primary_gender": "balanced",
                    "interests": ["music", "podcasts", "discovery", "playlists"]
                },
                engagement_metrics={
                    "avg_engagement_rate": "playlist_inclusion_rate",
                    "best_content_type": "high_quality_audio",
                    "peak_activity": "commute_workout_times"
                },
                monetization_options=["streaming_royalties", "spotify_for_artists", "playlist_pitching"],
                content_length_limits={
                    "track": "unlimited",
                    "podcast": "unlimited"
                },
                optimal_posting_schedule={
                    "release_day": ["friday_global_release"],
                    "promotion": ["ongoing_playlist_pitching"]
                },
                platform_specific_features=["playlists", "spotify_canvas", "artist_pick", "concerts"],
                cross_promotion_compatibility=["youtube", "instagram", "tiktok", "apple_music"]
            ),
            
            # New Integrated Platforms
            "threads": PlatformIntelligence(
                platform_id="threads",
                primary_content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO],
                capabilities=[
                    PlatformCapability.SHORT_FORM_VIDEO, PlatformCapability.IMAGE_SHARING,
                    PlatformCapability.COMMUNITY_FEATURES, PlatformCapability.ANALYTICS
                ],
                audience_demographics={
                    "age_range": "18-34",
                    "primary_gender": "balanced",
                    "interests": ["real_time_conversations", "news", "entertainment", "community"]
                },
                engagement_metrics={
                    "avg_engagement_rate": "3.2%",
                    "best_content_type": "conversational_content",
                    "peak_activity": "real_time_events"
                },
                monetization_options=["brand_partnerships", "creator_bonus"],
                content_length_limits={
                    "text": "500_characters",
                    "video": "5_minutes"
                },
                optimal_posting_schedule={
                    "weekdays": ["12:00-14:00", "18:00-20:00"],
                    "weekends": ["10:00-12:00", "16:00-18:00"]
                },
                platform_specific_features=["threaded_conversations", "meta_integration", "real_time_trending"],
                cross_promotion_compatibility=["instagram", "facebook", "twitter"]
            ),
            
            "livemixtapes": PlatformIntelligence(
                platform_id="livemixtapes",
                primary_content_types=[ContentType.AUDIO, ContentType.MUSIC],
                capabilities=[
                    PlatformCapability.AUDIO_STREAMING, PlatformCapability.COMMUNITY_FEATURES,
                    PlatformCapability.ANALYTICS
                ],
                audience_demographics={
                    "age_range": "16-35",
                    "primary_gender": "male_skewed",
                    "interests": ["hip_hop", "rap", "mixtapes", "underground_music"]
                },
                engagement_metrics={
                    "avg_engagement_rate": "4.5%",
                    "best_content_type": "mixtapes_singles",
                    "peak_activity": "evening_night"
                },
                monetization_options=["download_sales", "streaming", "artist_promotion"],
                content_length_limits={
                    "mixtape": "unlimited_tracks",
                    "single": "individual_tracks"
                },
                optimal_posting_schedule={
                    "weekdays": ["16:00-20:00"],
                    "weekends": ["14:00-18:00"]
                },
                platform_specific_features=["mixtape_hosting", "artist_profiles", "download_tracking"],
                cross_promotion_compatibility=["spotify", "apple_music", "soundcloud", "youtube"]
            )
        }
    
    def _initialize_optimization_rules(self) -> List[ContentOptimizationRule]:
        """Initialize content optimization rules for different content types"""
        return [
            ContentOptimizationRule(
                content_type=ContentType.SHORT_FORM,
                recommended_platforms=["tiktok", "instagram", "youtube", "snapchat"],
                optimization_tips=[
                    "Keep videos under 60 seconds for maximum engagement",
                    "Use trending audio and hashtags",
                    "Hook viewers in first 3 seconds",
                    "Vertical format (9:16) preferred"
                ],
                format_requirements={
                    "aspect_ratio": "9:16",
                    "duration": "15-60 seconds",
                    "resolution": "1080x1920 minimum"
                },
                engagement_strategy="trend_participation_and_authentic_content",
                best_posting_times=["15:00-18:00", "20:00-23:00"],
                hashtag_strategy="mix_of_trending_and_niche_hashtags",
                cta_recommendations=["follow_for_more", "share_with_friends", "try_this_trend"]
            ),
            
            ContentOptimizationRule(
                content_type=ContentType.MUSIC,
                recommended_platforms=["spotify", "apple_music", "youtube", "soundcloud", "livemixtapes"],
                optimization_tips=[
                    "High-quality audio (320kbps minimum)",
                    "Professional mastering and mixing",
                    "Consistent branding across platforms",
                    "Leverage playlist pitching opportunities"
                ],
                format_requirements={
                    "audio_quality": "320kbps_minimum",
                    "format": "WAV_or_FLAC_master",
                    "metadata": "complete_id3_tags"
                },
                engagement_strategy="playlist_inclusion_and_cross_platform_promotion",
                best_posting_times=["friday_global_release", "thursday_pre_release"],
                hashtag_strategy="genre_specific_and_discovery_hashtags",
                cta_recommendations=["add_to_playlist", "stream_and_share", "follow_artist"]
            ),
            
            ContentOptimizationRule(
                content_type=ContentType.LONG_FORM,
                recommended_platforms=["youtube", "linkedin", "facebook", "vimeo"],
                optimization_tips=[
                    "Strong opening hook (first 15 seconds)",
                    "Clear value proposition",
                    "Engaging thumbnails and titles",
                    "Include timestamps for long content"
                ],
                format_requirements={
                    "aspect_ratio": "16:9",
                    "duration": "3-20 minutes optimal",
                    "resolution": "1080p minimum"
                },
                engagement_strategy="educational_entertainment_and_storytelling",
                best_posting_times=["14:00-16:00", "20:00-22:00"],
                hashtag_strategy="topic_specific_and_searchable_keywords",
                cta_recommendations=["subscribe_and_bell", "watch_next_video", "comment_your_thoughts"]
            ),
            
            ContentOptimizationRule(
                content_type=ContentType.IMAGE,
                recommended_platforms=["instagram", "pinterest", "facebook", "linkedin"],
                optimization_tips=[
                    "High-resolution images (1080x1080 minimum)",
                    "Consistent visual branding",
                    "Compelling captions with storytelling",
                    "Use platform-appropriate filters"
                ],
                format_requirements={
                    "aspect_ratio": "1:1_or_4:5_for_instagram",
                    "resolution": "1080x1080_minimum",
                    "format": "JPG_or_PNG"
                },
                engagement_strategy="visual_storytelling_and_community_building",
                best_posting_times=["11:00-13:00", "19:00-21:00"],
                hashtag_strategy="location_and_interest_based_hashtags",
                cta_recommendations=["double_tap_if_agree", "tag_a_friend", "save_for_later"]
            )
        ]
    
    def get_platform_recommendations(self, content_type: ContentType, 
                                   target_audience: Optional[Dict[str, Any]] = None,
                                   content_duration: Optional[int] = None,
                                   monetization_priority: bool = False) -> ContentRecommendation:
        """Get intelligent platform recommendations based on content characteristics"""
        
        # Find matching optimization rule
        matching_rule = next(
            (rule for rule in self.optimization_rules if rule.content_type == content_type),
            None
        )
        
        if not matching_rule:
            # Default recommendation for unknown content types
            return ContentRecommendation(
                recommended_platforms=["instagram", "facebook", "twitter"],
                optimization_score=0.5,
                content_adaptations={},
                cross_promotion_strategy={},
                estimated_reach={},
                monetization_potential={}
            )
        
        recommended_platforms = matching_rule.recommended_platforms.copy()
        content_adaptations = {}
        cross_promotion_strategy = {}
        estimated_reach = {}
        monetization_potential = {}
        
        # Calculate optimization score and generate adaptations
        for platform_id in recommended_platforms:
            if platform_id in self.platform_intelligence:
                platform = self.platform_intelligence[platform_id]
                
                # Generate platform-specific adaptations
                adaptations = self._generate_platform_adaptations(platform, content_type, content_duration)
                content_adaptations[platform_id] = adaptations
                
                # Generate cross-promotion strategy
                cross_promotion_strategy[platform_id] = platform.cross_promotion_compatibility
                
                # Estimate reach (simplified calculation)
                estimated_reach[platform_id] = self._estimate_platform_reach(platform, content_type)
                
                # Calculate monetization potential
                if monetization_priority:
                    monetization_potential[platform_id] = self._calculate_monetization_potential(platform, content_type)
        
        # Calculate overall optimization score
        optimization_score = self._calculate_optimization_score(content_type, recommended_platforms)
        
        return ContentRecommendation(
            recommended_platforms=recommended_platforms,
            optimization_score=optimization_score,
            content_adaptations=content_adaptations,
            cross_promotion_strategy=cross_promotion_strategy,
            estimated_reach=estimated_reach,
            monetization_potential=monetization_potential
        )
    
    def _generate_platform_adaptations(self, platform: PlatformIntelligence, 
                                     content_type: ContentType, 
                                     content_duration: Optional[int]) -> Dict[str, Any]:
        """Generate platform-specific content adaptations"""
        adaptations = {
            "optimal_format": {},
            "caption_style": "",
            "hashtag_count": 0,
            "posting_schedule": platform.optimal_posting_schedule,
            "engagement_tactics": []
        }
        
        # Platform-specific adaptations
        if platform.platform_id == "tiktok":
            adaptations.update({
                "optimal_format": {"aspect_ratio": "9:16", "duration": "15-60 seconds"},
                "caption_style": "engaging_hook_with_trending_hashtags",
                "hashtag_count": 3-5,
                "engagement_tactics": ["use_trending_sounds", "participate_in_challenges", "quick_hook"]
            })
        elif platform.platform_id == "instagram":
            adaptations.update({
                "optimal_format": {"aspect_ratio": "1:1 or 4:5", "duration": "15-90 seconds for reels"},
                "caption_style": "storytelling_with_strong_cta",
                "hashtag_count": 5-10,
                "engagement_tactics": ["use_stories", "create_reels", "engage_with_comments"]
            })
        elif platform.platform_id == "youtube":
            adaptations.update({
                "optimal_format": {"aspect_ratio": "16:9", "duration": "3-20 minutes"},
                "caption_style": "detailed_description_with_timestamps",
                "hashtag_count": 10-15,
                "engagement_tactics": ["compelling_thumbnail", "clear_title", "end_screen_cards"]
            })
        elif platform.platform_id == "linkedin":
            adaptations.update({
                "optimal_format": {"professional_quality": True, "business_relevant": True},
                "caption_style": "professional_insights_with_industry_relevance",
                "hashtag_count": 3-5,
                "engagement_tactics": ["thought_leadership", "industry_insights", "professional_networking"]
            })
        
        return adaptations
    
    def _estimate_platform_reach(self, platform: PlatformIntelligence, content_type: ContentType) -> int:
        """Estimate potential reach based on platform and content type"""
        base_reach = {
            "tiktok": 10000,
            "instagram": 5000,
            "youtube": 3000,
            "facebook": 2000,
            "linkedin": 1500,
            "twitter": 1000,
            "spotify": 500,
            "threads": 2000,
            "livemixtapes": 800
        }
        
        # Apply content type multiplier
        content_multipliers = {
            ContentType.SHORT_FORM: 1.5,
            ContentType.VIDEO: 1.3,
            ContentType.MUSIC: 1.2,
            ContentType.IMAGE: 1.0,
            ContentType.TEXT: 0.8
        }
        
        platform_reach = base_reach.get(platform.platform_id, 1000)
        content_multiplier = content_multipliers.get(content_type, 1.0)
        
        return int(platform_reach * content_multiplier)
    
    def _calculate_monetization_potential(self, platform: PlatformIntelligence, content_type: ContentType) -> float:
        """Calculate monetization potential score (0-1)"""
        monetization_scores = {
            "youtube": 0.9,
            "spotify": 0.8,
            "instagram": 0.7,
            "tiktok": 0.6,
            "facebook": 0.5,
            "linkedin": 0.7,
            "livemixtapes": 0.6,
            "threads": 0.3
        }
        
        return monetization_scores.get(platform.platform_id, 0.3)
    
    def _calculate_optimization_score(self, content_type: ContentType, platforms: List[str]) -> float:
        """Calculate overall optimization score for the recommendation"""
        # Simplified scoring based on platform compatibility with content type
        score = 0.0
        for platform_id in platforms:
            if platform_id in self.platform_intelligence:
                platform = self.platform_intelligence[platform_id]
                if content_type in platform.primary_content_types:
                    score += 0.3
                else:
                    score += 0.1
        
        return min(score, 1.0)
    
    def get_cross_promotion_strategy(self, primary_platform: str, content_type: ContentType) -> Dict[str, Any]:
        """Generate cross-promotion strategy for multi-platform distribution"""
        if primary_platform not in self.platform_intelligence:
            return {}
        
        primary = self.platform_intelligence[primary_platform]
        compatible_platforms = primary.cross_promotion_compatibility
        
        strategy = {
            "primary_platform": primary_platform,
            "secondary_platforms": compatible_platforms,
            "content_variations": {},
            "timing_strategy": {},
            "cta_strategy": {}
        }
        
        # Generate platform-specific variations
        for platform_id in compatible_platforms:
            if platform_id in self.platform_intelligence:
                platform = self.platform_intelligence[platform_id]
                strategy["content_variations"][platform_id] = {
                    "format_adaptation": self._generate_platform_adaptations(platform, content_type, None),
                    "messaging_adaptation": self._generate_platform_messaging(platform_id, primary_platform)
                }
        
        return strategy
    
    def _generate_platform_messaging(self, target_platform: str, source_platform: str) -> Dict[str, str]:
        """Generate platform-specific messaging for cross-promotion"""
        messaging_templates = {
            "instagram_to_tiktok": {
                "cta": "Check out the full version on TikTok! 🎵",
                "hashtags": "#TikTokVersion #FullVideo #CheckItOut"
            },
            "tiktok_to_youtube": {
                "cta": "Watch the extended version on YouTube! ▶️",
                "hashtags": "#YouTubeVideo #LongForm #WatchMore"
            },
            "youtube_to_instagram": {
                "cta": "Quick highlights on Instagram! 📸",
                "hashtags": "#InstaHighlights #QuickVersion #BehindScenes"
            },
            "spotify_to_instagram": {
                "cta": "Stream the full track on Spotify! 🎶",
                "hashtags": "#NowStreaming #SpotifyMusic #NewMusic"
            }
        }
        
        key = f"{source_platform}_to_{target_platform}"
        return messaging_templates.get(key, {
            "cta": f"More content on {target_platform.title()}!",
            "hashtags": f"#{target_platform.title()}Content #MoreContent"
        })
    
    def analyze_content_performance(self, content_data: Dict[str, Any], 
                                  platform_performance: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content performance across platforms and provide optimization insights"""
        analysis = {
            "best_performing_platforms": [],
            "optimization_opportunities": [],
            "content_format_insights": {},
            "audience_engagement_patterns": {},
            "monetization_insights": {}
        }
        
        # Analyze performance metrics
        platform_scores = {}
        for platform_id, metrics in platform_performance.items():
            if platform_id in self.platform_intelligence:
                # Calculate performance score
                engagement_rate = metrics.get("engagement_rate", 0)
                reach = metrics.get("reach", 0)
                conversions = metrics.get("conversions", 0)
                
                score = (engagement_rate * 0.4) + (reach * 0.3) + (conversions * 0.3)
                platform_scores[platform_id] = score
        
        # Sort platforms by performance
        analysis["best_performing_platforms"] = sorted(
            platform_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Generate optimization opportunities
        for platform_id, score in platform_scores.items():
            if score < 0.5:  # Low performance threshold
                platform = self.platform_intelligence[platform_id]
                analysis["optimization_opportunities"].append({
                    "platform": platform_id,
                    "current_score": score,
                    "recommendations": self._generate_optimization_recommendations(platform_id, metrics)
                })
        
        return analysis
    
    def _generate_optimization_recommendations(self, platform_id: str, metrics: Dict[str, Any]) -> List[str]:
        """Generate specific optimization recommendations for underperforming content"""
        recommendations = []
        platform = self.platform_intelligence.get(platform_id)
        
        if not platform:
            return recommendations
        
        # Analyze specific metrics and provide recommendations
        if metrics.get("engagement_rate", 0) < 1.0:
            recommendations.extend([
                f"Improve engagement by posting during optimal times: {platform.optimal_posting_schedule}",
                f"Use platform-specific features: {', '.join(platform.platform_specific_features)}",
                "Include strong call-to-actions in your content"
            ])
        
        if metrics.get("reach", 0) < 1000:
            recommendations.extend([
                "Optimize hashtag strategy for better discoverability",
                "Engage with your audience through comments and stories",
                "Collaborate with other creators in your niche"
            ])
        
        return recommendations