# Enhanced Distribution Platforms Configuration
# Adding the 8 requested new platforms to existing categories

NEW_DISTRIBUTION_PLATFORMS = {
    # Social Media Platforms - Adding requested social platforms
    "threads": {
        "type": "social_media",
        "name": "Threads",
        "api_endpoint": "https://graph.threads.net/v1.0",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["access_token"],
        "description": "Meta's text-based conversation platform",
        "demographics": ["Gen Z", "Millennials", "Social media users"],
        "content_guidelines": {
            "max_duration": 600,  # 10 minutes for video
            "recommended_formats": ["MP4", "JPG", "PNG", "MP3"],
            "hashtag_limit": 30,
            "character_limit": 500
        },
        "features": ["text_posts", "image_sharing", "video_sharing", "audio_posts"],
        "distribution_fee": 0.00,
        "revenue_share": 0.95  # 95% to creator
    },
    
    "tumblr": {
        "type": "social_media", 
        "name": "Tumblr",
        "api_endpoint": "https://api.tumblr.com/v2",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["consumer_key", "consumer_secret", "token", "token_secret"],
        "description": "Microblogging platform for creative expression",
        "demographics": ["Creative artists", "Gen Z", "Alternative culture enthusiasts"],
        "content_guidelines": {
            "max_duration": 300,  # 5 minutes for video
            "recommended_formats": ["GIF", "MP4", "JPG", "PNG", "MP3"],
            "tag_limit": 30,
            "supports_nsfw": True
        },
        "features": ["multimedia_posts", "reblogging", "tagging", "creative_content"],
        "distribution_fee": 0.00,
        "revenue_share": 0.90  # 90% to creator
    },

    "theshaderoom": {
        "type": "social_media",
        "name": "The Shade Room",
        "api_endpoint": "https://api.theshaderoom.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["api_key", "access_token"],
        "description": "Entertainment and celebrity news platform",
        "demographics": ["Urban culture", "Entertainment enthusiasts", "Social media users"],
        "content_guidelines": {
            "max_duration": 180,  # 3 minutes for video
            "recommended_formats": ["MP4", "JPG", "PNG"],
            "content_focus": ["entertainment", "celebrity", "urban_culture"],
            "editorial_review": True
        },
        "features": ["entertainment_content", "celebrity_news", "viral_content", "social_commentary"],
        "distribution_fee": 2.99,
        "revenue_share": 0.80  # 80% to creator
    },

    "hollywoodunlocked": {
        "type": "social_media",
        "name": "Hollywood Unlocked", 
        "api_endpoint": "https://api.hollywoodunlocked.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 150 * 1024 * 1024,  # 150MB
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Celebrity news and entertainment platform",
        "demographics": ["Entertainment industry", "Celebrity followers", "Urban audience"],
        "content_guidelines": {
            "max_duration": 300,  # 5 minutes for video
            "recommended_formats": ["MP4", "JPG", "PNG", "MP3"],
            "content_focus": ["celebrity", "entertainment", "exclusive_content"],
            "editorial_review": True
        },
        "features": ["celebrity_content", "exclusive_interviews", "entertainment_news", "social_media_integration"],
        "distribution_fee": 3.99,
        "revenue_share": 0.85  # 85% to creator
    },

    # Music Streaming Platforms - Adding mixtape platforms  
    "livemixtapes": {
        "type": "music_streaming",
        "name": "LiveMixtapes.com",
        "api_endpoint": "https://api.livemixtapes.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 150 * 1024 * 1024,  # 150MB
        "credentials_required": ["api_key", "user_token"],
        "description": "Hip-hop mixtape hosting and streaming platform",
        "demographics": ["Hip-hop artists", "Rap enthusiasts", "Urban music fans"],
        "content_guidelines": {
            "recommended_formats": ["MP3", "WAV"],
            "genre_focus": ["hip-hop", "rap", "r&b", "urban"],
            "mixtape_hosting": True,
            "free_distribution": True
        },
        "features": ["mixtape_hosting", "artist_profiles", "playlist_features", "mobile_app_integration"],
        "distribution_fee": 0.00,  # Free distribution
        "revenue_share": 0.95  # 95% to creator
    },

    "mymixtapez": {
        "type": "music_streaming", 
        "name": "MyMixtapez.com",
        "api_endpoint": "https://api.mymixtapez.com/v2",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,  # 200MB
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Premier mixtape platform for independent artists",
        "demographics": ["Independent artists", "Mixtape culture", "Hip-hop community"],
        "content_guidelines": {
            "recommended_formats": ["MP3", "WAV", "FLAC"],
            "genre_focus": ["hip-hop", "rap", "trap", "drill", "r&b"],
            "mixtape_branding": True,
            "free_distribution": True
        },
        "features": ["mixtape_distribution", "artist_promotion", "community_features", "chart_tracking"],
        "distribution_fee": 0.00,  # Free distribution
        "revenue_share": 0.92  # 92% to creator
    },

    "worldstarhiphop": { 
        "type": "music_streaming",
        "name": "WorldStar Hip Hop",
        "api_endpoint": "https://api.worldstarhiphop.com/v1",
        "supported_formats": ["video", "audio"],
        "max_file_size": 500 * 1024 * 1024,  # 500MB
        "credentials_required": ["api_key", "secret_key", "access_token"],
        "description": "Leading hip-hop content and music platform",
        "demographics": ["Hip-hop culture", "Urban audience", "Music video enthusiasts"],
        "content_guidelines": {
            "max_duration": 600,  # 10 minutes for video
            "recommended_formats": ["MP4", "MP3", "WAV"],
            "genre_focus": ["hip-hop", "rap", "urban", "viral_content"],
            "video_priority": True,
            "editorial_review": True
        },
        "features": ["music_videos", "viral_content", "hip_hop_culture", "artist_promotion"],
        "distribution_fee": 4.99,
        "revenue_share": 0.80  # 80% to creator
    },

    # Adding Snapchat to social media (if not already present with updated config)
    "snapchat_enhanced": {
        "type": "social_media",
        "name": "Snapchat",
        "api_endpoint": "https://adsapi.snapchat.com/v1", 
        "supported_formats": ["video", "image", "audio"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Multimedia messaging and content sharing platform",
        "demographics": ["Gen Z", "Millennials", "Mobile-first users"],
        "content_guidelines": {
            "max_duration": 60,  # 60 seconds for video
            "recommended_formats": ["MP4", "JPG", "PNG", "MP3"],
            "vertical_video_preferred": True,
            "ephemeral_content": True
        },
        "features": ["stories", "spotlight", "snap_map", "ar_filters"],
        "distribution_fee": 1.99,
        "revenue_share": 0.88  # 88% to creator
    }
}

# Platform categorization for frontend display
PLATFORM_CATEGORIES = {
    "social_media": {
        "name": "Social Media Platforms",
        "description": "Share content across social networks and community platforms",
        "platforms": [
            "instagram", "twitter", "facebook", "tiktok", "youtube", "linkedin", 
            "pinterest", "reddit", "discord", "telegram", "whatsapp_business",
            "threads", "tumblr", "theshaderoom", "hollywoodunlocked", "snapchat_enhanced"
        ]
    },
    "music_streaming": {
        "name": "Music Streaming Services", 
        "description": "Distribute music to streaming platforms and mixtape sites",
        "platforms": [
            "spotify", "apple_music", "amazon_music", "tidal", "deezer", "pandora",
            "soundcloud", "bandcamp", "audiomack", "datpiff", "spinrilla",
            "livemixtapes", "mymixtapez", "worldstarhiphop"
        ]
    },
    "radio_broadcast": {
        "name": "Radio & Broadcast",
        "description": "Reach audiences through radio stations and broadcast networks",
        "platforms": [
            "iheartradio", "siriusxm", "pandora_radio", "tunein", "radio_com",
            "clear_channel", "cumulus_media", "entercom", "townsquare_media"
        ]
    },
    "television_video": {
        "name": "Television & Video Platforms",
        "description": "Distribute video content to TV networks and streaming services", 
        "platforms": [
            "netflix", "hulu", "amazon_prime", "hbo_max", "disney_plus",
            "paramount_plus", "peacock", "apple_tv_plus", "discovery_plus"
        ]
    }
}

# Revenue sharing and fee structure for new platforms
PLATFORM_REVENUE_CONFIG = {
    "threads": {"distribution_fee": 0.00, "revenue_share": 0.95},
    "tumblr": {"distribution_fee": 0.00, "revenue_share": 0.90},
    "theshaderoom": {"distribution_fee": 2.99, "revenue_share": 0.80},
    "hollywoodunlocked": {"distribution_fee": 3.99, "revenue_share": 0.85},
    "livemixtapes": {"distribution_fee": 0.00, "revenue_share": 0.95},
    "mymixtapez": {"distribution_fee": 0.00, "revenue_share": 0.92},
    "worldstarhiphop": {"distribution_fee": 4.99, "revenue_share": 0.80},
    "snapchat_enhanced": {"distribution_fee": 1.99, "revenue_share": 0.88}
}

# Platform-specific submission requirements
PLATFORM_SUBMISSION_REQUIREMENTS = {
    "livemixtapes": {
        "required_metadata": ["artist_name", "track_title", "genre", "cover_art"],
        "optional_metadata": ["producer", "features", "release_date", "label"],
        "content_restrictions": ["explicit_content_allowed", "mixtape_format_preferred"],
        "approval_process": "automated"
    },
    "mymixtapez": {
        "required_metadata": ["artist_name", "track_title", "genre", "cover_art", "track_duration"],
        "optional_metadata": ["producer", "writer", "release_year", "label", "featured_artists"],
        "content_restrictions": ["explicit_content_allowed", "original_content_required"],
        "approval_process": "community_moderated"
    },
    "worldstarhiphop": {
        "required_metadata": ["artist_name", "track_title", "genre", "cover_art", "video_thumbnail"],
        "optional_metadata": ["director", "producer", "label", "release_date", "featured_artists"],
        "content_restrictions": ["editorial_review_required", "viral_potential_preferred"],
        "approval_process": "editorial_review"
    },
    "theshaderoom": {
        "required_metadata": ["content_title", "content_type", "thumbnail", "description"],
        "optional_metadata": ["celebrity_tags", "event_date", "location", "source"],
        "content_restrictions": ["entertainment_focus_required", "editorial_guidelines"],
        "approval_process": "editorial_review"
    },
    "hollywoodunlocked": {
        "required_metadata": ["content_title", "content_type", "thumbnail", "description", "category"],
        "optional_metadata": ["celebrity_subject", "exclusivity_level", "publication_date"],
        "content_restrictions": ["celebrity_news_focus", "exclusive_content_preferred"],
        "approval_process": "editorial_review"
    },
    "threads": {
        "required_metadata": ["content_text", "media_type"],
        "optional_metadata": ["hashtags", "mentions", "location"],
        "content_restrictions": ["community_guidelines", "character_limit_500"],
        "approval_process": "automated"
    },
    "tumblr": {
        "required_metadata": ["post_type", "content", "tags"],
        "optional_metadata": ["blog_title", "publish_date", "reblog_source"],
        "content_restrictions": ["creative_content_focus", "nsfw_allowed_with_tags"],
        "approval_process": "automated"
    },
    "snapchat_enhanced": {
        "required_metadata": ["content_type", "media_file", "duration"],
        "optional_metadata": ["location", "filters", "music_overlay"],
        "content_restrictions": ["vertical_format_preferred", "60_second_limit"],  
        "approval_process": "automated"
    }
}