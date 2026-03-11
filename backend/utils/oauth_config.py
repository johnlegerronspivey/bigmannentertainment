"""
OAuth Provider Configuration Registry
Centralized configuration for all social media OAuth providers
"""
import os
from typing import Dict, Any

# OAuth Provider Registry
OAUTH_PROVIDERS = {
    "twitter": {
        "name": "Twitter/X",
        "oauth_version": "2.0",
        "client_id": os.getenv('TWITTER_CLIENT_ID', ''),
        "client_secret": os.getenv('TWITTER_CLIENT_SECRET', ''),
        "bearer_token": os.getenv('TWITTER_BEARER_TOKEN', ''),
        "authorize_url": "https://twitter.com/i/oauth2/authorize",
        "access_token_url": "https://api.twitter.com/2/oauth2/token",
        "api_base_url": "https://api.twitter.com/2/",
        "scopes": [
            "tweet.read",
            "tweet.write",
            "users.read",
            "follows.read",
            "offline.access"  # For refresh token
        ],
        "endpoints": {
            "user_info": "users/me",
            "post_tweet": "tweets",
            "user_metrics": "users/:id/metrics",
            "tweet_metrics": "tweets/:id"
        }
    },
    "facebook": {
        "name": "Facebook",
        "oauth_version": "2.0",
        "client_id": os.getenv('FACEBOOK_APP_ID', ''),
        "client_secret": os.getenv('FACEBOOK_APP_SECRET', ''),
        "authorize_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "access_token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "api_base_url": "https://graph.facebook.com/v18.0/",
        "scopes": [
            "public_profile",
            "email",
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_posts"
        ],
        "endpoints": {
            "user_info": "me",
            "pages": "me/accounts",
            "page_insights": ":page_id/insights"
        }
    },
    "instagram": {
        "name": "Instagram",
        "oauth_version": "2.0",
        "client_id": os.getenv('FACEBOOK_APP_ID', ''),  # Instagram uses Facebook OAuth
        "client_secret": os.getenv('FACEBOOK_APP_SECRET', ''),
        "authorize_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "access_token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "api_base_url": "https://graph.facebook.com/v18.0/",
        "scopes": [
            "instagram_basic",
            "instagram_content_publish",
            "pages_show_list"
        ],
        "endpoints": {
            "user_info": "me",
            "media": ":ig_user_id/media"
        }
    },
    "tiktok": {
        "name": "TikTok",
        "oauth_version": "2.0",
        "client_id": os.getenv('TIKTOK_CLIENT_KEY', ''),
        "client_secret": os.getenv('TIKTOK_CLIENT_SECRET', ''),
        "authorize_url": "https://www.tiktok.com/v2/auth/authorize/",
        "access_token_url": "https://open.tiktokapis.com/v2/oauth/token/",
        "api_base_url": "https://open.tiktokapis.com",
        "scopes": [
            "user.info.basic",
            "user.info.profile",
            "user.info.stats",
            "video.list",
            "video.publish"
        ],
        "endpoints": {
            "user_info": "user/info/",
            "videos": "video/list/",
            "video_publish": "post/publish/video/init/",
            "photo_publish": "post/publish/content/init/",
            "publish_status": "post/publish/status/fetch/"
        }
    },
    "linkedin": {
        "name": "LinkedIn",
        "oauth_version": "2.0",
        "client_id": os.getenv('LINKEDIN_CLIENT_ID', ''),
        "client_secret": os.getenv('LINKEDIN_CLIENT_SECRET', ''),
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "access_token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "api_base_url": "https://api.linkedin.com/v2/",
        "scopes": [
            "r_liteprofile",
            "r_emailaddress",
            "w_member_social"
        ],
        "endpoints": {
            "user_info": "me",
            "share": "ugcPosts"
        }
    },
    "youtube": {
        "name": "YouTube",
        "oauth_version": "2.0",
        "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET', ''),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "access_token_url": "https://oauth2.googleapis.com/token",
        "api_base_url": "https://www.googleapis.com/youtube/v3/",
        "scopes": [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/userinfo.profile"
        ],
        "endpoints": {
            "channels": "channels",
            "videos": "videos"
        }
    }
}

def get_provider_config(provider: str) -> Dict[str, Any]:
    """Get configuration for a specific provider"""
    config = OAUTH_PROVIDERS.get(provider.lower())
    if not config:
        raise ValueError(f"Unknown provider: {provider}")
    return config

def is_provider_configured(provider: str) -> bool:
    """Check if a provider has credentials configured"""
    config = get_provider_config(provider)
    return bool(config.get('client_id') and config.get('client_secret'))

def get_configured_providers() -> list:
    """Get list of all configured providers"""
    return [
        {
            "provider": provider,
            "name": config["name"],
            "configured": bool(config.get('client_id') and config.get('client_secret'))
        }
        for provider, config in OAUTH_PROVIDERS.items()
    ]

def get_oauth_scopes(provider: str) -> list:
    """Get OAuth scopes for a provider"""
    config = get_provider_config(provider)
    return config.get('scopes', [])
