"""
Social Media OAuth Service
Handles OAuth flows for Facebook, Instagram, TikTok, YouTube, Twitter
"""
import os
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from typing import Dict, Optional
import httpx

router = APIRouter(prefix="/api/oauth", tags=["Social OAuth"])

# OAuth configuration
oauth = OAuth()

# Facebook/Instagram OAuth
oauth.register(
    name='facebook',
    client_id=os.getenv('FACEBOOK_APP_ID', ''),
    client_secret=os.getenv('FACEBOOK_APP_SECRET', ''),
    authorize_url='https://www.facebook.com/v18.0/dialog/oauth',
    access_token_url='https://graph.facebook.com/v18.0/oauth/access_token',
    api_base_url='https://graph.facebook.com/v18.0/',
    client_kwargs={'scope': 'public_profile,email,instagram_basic,pages_show_list'}
)

# TikTok OAuth
oauth.register(
    name='tiktok',
    client_id=os.getenv('TIKTOK_CLIENT_KEY', ''),
    client_secret=os.getenv('TIKTOK_CLIENT_SECRET', ''),
    authorize_url='https://www.tiktok.com/v2/auth/authorize/',
    access_token_url='https://open.tiktokapis.com/v2/oauth/token/',
    api_base_url='https://open.tiktokapis.com',
    client_kwargs={'scope': 'user.info.basic,user.info.profile,user.info.stats,video.list,video.publish'}
)

# YouTube (Google) OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/youtube.readonly'}
)

# Twitter OAuth
oauth.register(
    name='twitter',
    client_id=os.getenv('TWITTER_CLIENT_ID', ''),
    client_secret=os.getenv('TWITTER_CLIENT_SECRET', ''),
    api_base_url='https://api.twitter.com/2/',
    authorize_url='https://twitter.com/i/oauth2/authorize',
    access_token_url='https://api.twitter.com/2/oauth2/token',
    client_kwargs={'scope': 'tweet.read users.read follows.read'}
)

class SocialOAuthService:
    """Service for managing social media OAuth"""
    
    def __init__(self):
        self.callback_base = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    async def get_facebook_profile(self, access_token: str) -> Dict:
        """Get Facebook profile data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://graph.facebook.com/v18.0/me',
                params={
                    'fields': 'id,name,email,picture',
                    'access_token': access_token
                }
            )
            return response.json()
    
    async def get_facebook_insights(self, access_token: str, user_id: str) -> Dict:
        """Get Facebook page insights"""
        async with httpx.AsyncClient() as client:
            # Get pages
            pages_response = await client.get(
                f'https://graph.facebook.com/v18.0/{user_id}/accounts',
                params={'access_token': access_token}
            )
            pages = pages_response.json().get('data', [])
            
            insights = []
            for page in pages[:1]:  # Get first page only
                page_id = page.get('id')
                insights_response = await client.get(
                    f'https://graph.facebook.com/v18.0/{page_id}/insights',
                    params={
                        'metric': 'page_fans,page_impressions,page_engaged_users',
                        'access_token': page.get('access_token')
                    }
                )
                insights.append(insights_response.json())
            
            return {
                "pages": pages,
                "insights": insights
            }
    
    async def get_instagram_profile(self, access_token: str) -> Dict:
        """Get Instagram business account"""
        async with httpx.AsyncClient() as client:
            # First get Facebook pages
            pages_response = await client.get(
                'https://graph.facebook.com/v18.0/me/accounts',
                params={'access_token': access_token}
            )
            pages = pages_response.json().get('data', [])
            
            if pages:
                page_id = pages[0].get('id')
                # Get Instagram business account
                ig_response = await client.get(
                    f'https://graph.facebook.com/v18.0/{page_id}',
                    params={
                        'fields': 'instagram_business_account',
                        'access_token': access_token
                    }
                )
                ig_account = ig_response.json().get('instagram_business_account')
                
                if ig_account:
                    ig_id = ig_account.get('id')
                    # Get Instagram insights
                    profile_response = await client.get(
                        f'https://graph.facebook.com/v18.0/{ig_id}',
                        params={
                            'fields': 'username,followers_count,follows_count,media_count,profile_picture_url',
                            'access_token': access_token
                        }
                    )
                    return profile_response.json()
            
            return {}
    
    async def get_tiktok_profile(self, access_token: str) -> Dict:
        """Get TikTok user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://open-api.tiktok.com/user/info/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            return response.json()
    
    async def get_tiktok_videos(self, access_token: str) -> Dict:
        """Get TikTok videos"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://open-api.tiktok.com/video/list/',
                headers={'Authorization': f'Bearer {access_token}'},
                params={'max_count': 20}
            )
            return response.json()
    
    async def get_youtube_channel(self, access_token: str) -> Dict:
        """Get YouTube channel info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://www.googleapis.com/youtube/v3/channels',
                params={
                    'part': 'snippet,statistics',
                    'mine': 'true'
                },
                headers={'Authorization': f'Bearer {access_token}'}
            )
            return response.json()
    
    async def get_twitter_profile(self, access_token: str) -> Dict:
        """Get Twitter user profile"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.twitter.com/2/users/me',
                params={'user.fields': 'public_metrics,profile_image_url'},
                headers={'Authorization': f'Bearer {access_token}'}
            )
            return response.json()

social_oauth_service = SocialOAuthService()

# OAuth Endpoints

@router.get("/connect/{provider}")
async def oauth_connect(provider: str, request: Request):
    """Initiate OAuth flow for social media platform"""
    if provider not in ['facebook', 'tiktok', 'google', 'twitter']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    redirect_uri = f"{request.base_url}api/oauth/callback/{provider}"
    
    return await oauth.create_client(provider).authorize_redirect(
        request,
        redirect_uri
    )

@router.get("/callback/{provider}")
async def oauth_callback(provider: str, request: Request):
    """Handle OAuth callback"""
    try:
        client = oauth.create_client(provider)
        token = await client.authorize_access_token(request)
        
        # Store token and fetch profile data
        # This should be saved to the user's profile in PostgreSQL
        
        # Redirect to frontend with success
        return RedirectResponse(
            url=f"{social_oauth_service.callback_base}/profile/settings?oauth=success&provider={provider}"
        )
    except Exception as e:
        print(f"OAuth error: {str(e)}")
        return RedirectResponse(
            url=f"{social_oauth_service.callback_base}/profile/settings?oauth=error"
        )

@router.post("/disconnect/{provider}")
async def oauth_disconnect(provider: str, user_id: str):
    """Disconnect social media account"""
    # Remove tokens from database
    return {
        "success": True,
        "message": f"{provider} disconnected successfully"
    }

@router.get("/status")
async def oauth_status():
    """Get OAuth configuration status"""
    return {
        "facebook": {
            "configured": bool(os.getenv('FACEBOOK_APP_ID')),
            "scope": "public_profile,email,instagram_basic"
        },
        "tiktok": {
            "configured": bool(os.getenv('TIKTOK_CLIENT_KEY')),
            "scope": "user.info.basic,video.list"
        },
        "google_youtube": {
            "configured": bool(os.getenv('GOOGLE_CLIENT_ID')),
            "scope": "youtube.readonly"
        },
        "twitter": {
            "configured": bool(os.getenv('TWITTER_CLIENT_ID')),
            "scope": "tweet.read,users.read"
        }
    }
