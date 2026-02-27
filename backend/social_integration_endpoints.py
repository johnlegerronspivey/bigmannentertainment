"""
Social Media Integration API Endpoints
Unified endpoints for OAuth, posting, metrics, and webhooks
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from fastapi.responses import RedirectResponse
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import os
import httpx

# Import authentication
try:
    from auth.service import get_current_user
except:
    async def get_current_user():
        return {"id": "test_user", "email": "test@example.com"}

# Import database and models
from pg_database import get_async_session
from profile_models import UserProfile
from social_media_models import OAuthToken, SocialConnection, SocialPost, SocialMetric, WebhookEvent
from sqlalchemy import select, and_

# Import utilities
from oauth_config import get_provider_config, get_configured_providers, get_oauth_scopes
from encryption_utils import encrypt_token, decrypt_token
from providers import TwitterProvider
from providers.tiktok_provider import TikTokProvider
from authlib.integrations.starlette_client import OAuth

router = APIRouter(prefix="/api/social", tags=["Social Media Integration"])

# Initialize OAuth
oauth = OAuth()

# Helper functions
def get_user_id(current_user) -> str:
    """Extract user ID from current_user"""
    return current_user.get('id') if isinstance(current_user, dict) else current_user.id

async def get_user_profile_id(mongo_user_id: str, auto_create: bool = True) -> str:
    """
    Get PostgreSQL profile ID from MongoDB user ID
    If auto_create=True, creates a minimal profile if not exists
    """
    async with get_async_session() as session:
        result = await session.execute(
            select(UserProfile).where(UserProfile.mongo_user_id == mongo_user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile and auto_create:
            # Auto-create a minimal profile for social media use
            from datetime import datetime, timezone
            import uuid
            profile = UserProfile(
                mongo_user_id=mongo_user_id,
                username=f"user_{str(uuid.uuid4())[:8]}",  # Generate unique username
                display_name="Social Media User",
                profile_public=True,
                show_dao_activity=True
            )
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            print(f"✅ Auto-created profile for user {mongo_user_id}")
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found. Please create your profile first.")
        
        return profile.id

async def get_provider_instance(provider: str, user_id: str):
    """Get provider instance with user's access token"""
    async with get_async_session() as session:
        # Get OAuth token
        result = await session.execute(
            select(OAuthToken).where(
                and_(
                    OAuthToken.user_id == user_id,
                    OAuthToken.provider == provider
                )
            ).order_by(OAuthToken.created_at.desc())
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            raise HTTPException(
                status_code=404,
                detail=f"No {provider} connection found. Please connect your account first."
            )
        
        # Decrypt token
        access_token = decrypt_token(token_record.access_token)
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="Failed to decrypt access token"
            )
        
        # Get provider config
        config = get_provider_config(provider)
        
        # Return provider instance based on type
        if provider == "twitter":
            return TwitterProvider(access_token, config)
        elif provider == "tiktok":
            return TikTokProvider(access_token, config)
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Provider {provider} not yet implemented"
            )

# Pydantic Models
class PostRequest(BaseModel):
    provider: str
    content: str
    media_urls: Optional[List[str]] = None
    scheduled_for: Optional[str] = None

class ConnectionResponse(BaseModel):
    provider: str
    username: Optional[str]
    connected: bool
    connected_at: Optional[str]

# OAuth Endpoints

@router.get("/providers")
async def list_providers():
    """Get list of available social media providers"""
    return {
        "providers": get_configured_providers()
    }

@router.get("/connect/{provider}")
async def connect_provider(
    provider: str,
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    Initiate OAuth connection for a social media provider
    Redirects user to provider's authorization page
    """
    try:
        config = get_provider_config(provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not config.get('client_id') or not config.get('client_secret'):
        raise HTTPException(
            status_code=400,
            detail=f"{provider} is not configured. Missing API credentials."
        )
    
    # Register OAuth client dynamically
    oauth.register(
        name=provider,
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        authorize_url=config['authorize_url'],
        access_token_url=config['access_token_url'],
        api_base_url=config.get('api_base_url'),
        client_kwargs={
            'scope': ' '.join(config['scopes'])
        }
    )
    
    # Generate callback URL
    callback_url = str(request.url_for('oauth_callback', provider=provider))
    
    # Store user ID in state for callback
    redirect_response = await oauth.create_client(provider).authorize_redirect(
        request,
        callback_url,
        state=get_user_id(current_user)
    )
    
    return redirect_response

@router.get("/callback/{provider}")
async def oauth_callback(provider: str, request: Request):
    """
    OAuth callback endpoint
    Exchanges authorization code for access token and stores it
    """
    try:
        # Get provider config
        config = get_provider_config(provider)
        
        # Register OAuth client
        oauth.register(
            name=provider,
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            authorize_url=config['authorize_url'],
            access_token_url=config['access_token_url'],
            api_base_url=config.get('api_base_url'),
            client_kwargs={
                'scope': ' '.join(config['scopes'])
            }
        )
        
        # Exchange code for token
        client = oauth.create_client(provider)
        token = await client.authorize_access_token(request)
        
        # Get user ID from state
        mongo_user_id = request.query_params.get('state')
        if not mongo_user_id:
            raise HTTPException(status_code=400, detail="Missing state parameter")
        
        # Get profile ID
        profile_id = await get_user_profile_id(mongo_user_id)
        
        # Get user profile from provider
        provider_instance = None
        if provider == "twitter":
            provider_instance = TwitterProvider(token['access_token'], config)
            user_profile = await provider_instance.get_user_profile()
        elif provider == "tiktok":
            provider_instance = TikTokProvider(token['access_token'], config)
            user_profile = await provider_instance.get_user_profile()
        else:
            raise HTTPException(status_code=501, detail=f"Provider {provider} not implemented")
        
        async with get_async_session() as session:
            # Store OAuth token
            oauth_token = OAuthToken(
                user_id=profile_id,
                provider=provider,
                access_token=encrypt_token(token['access_token']),
                refresh_token=encrypt_token(token.get('refresh_token')) if token.get('refresh_token') else None,
                token_type=token.get('token_type', 'Bearer'),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=token.get('expires_in', 7200)) if token.get('expires_in') else None,
                scope=token.get('scope', ' '.join(config['scopes']))
            )
            session.add(oauth_token)
            
            # Store or update social connection
            existing_conn = await session.execute(
                select(SocialConnection).where(
                    and_(
                        SocialConnection.user_id == profile_id,
                        SocialConnection.provider == provider
                    )
                )
            )
            conn = existing_conn.scalar_one_or_none()
            
            if conn:
                # Update existing connection
                conn.platform_user_id = user_profile.get('id')
                conn.username = user_profile.get('username')
                conn.display_name = user_profile.get('name')
                conn.profile_image_url = user_profile.get('profile_image_url')
                conn.profile_data = user_profile
                conn.is_active = True
                conn.last_sync = datetime.now(timezone.utc)
            else:
                # Create new connection
                conn = SocialConnection(
                    user_id=profile_id,
                    provider=provider,
                    platform_user_id=user_profile.get('id'),
                    username=user_profile.get('username'),
                    display_name=user_profile.get('name'),
                    profile_image_url=user_profile.get('profile_image_url'),
                    profile_data=user_profile,
                    is_active=True,
                    last_sync=datetime.now(timezone.utc)
                )
                session.add(conn)
            
            await session.commit()
        
        # Close provider instance
        if provider_instance:
            await provider_instance.close()
        
        # Redirect to frontend with success
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(url=f"{frontend_url}/social?connected={provider}")
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(url=f"{frontend_url}/social?error=connection_failed")

@router.get("/connections")
async def get_connections(current_user = Depends(get_current_user)):
    """Get user's connected social media accounts"""
    profile_id = await get_user_profile_id(get_user_id(current_user))
    
    async with get_async_session() as session:
        result = await session.execute(
            select(SocialConnection).where(
                and_(
                    SocialConnection.user_id == profile_id,
                    SocialConnection.is_active == True
                )
            )
        )
        connections = result.scalars().all()
        
        return {
            "connections": [
                {
                    "provider": conn.provider,
                    "username": conn.username,
                    "display_name": conn.display_name,
                    "profile_image_url": conn.profile_image_url,
                    "connected_at": conn.connected_at.isoformat() if conn.connected_at else None,
                    "last_sync": conn.last_sync.isoformat() if conn.last_sync else None
                }
                for conn in connections
            ]
        }

@router.post("/disconnect/{provider}")
async def disconnect_provider(
    provider: str,
    current_user = Depends(get_current_user)
):
    """Disconnect a social media provider"""
    profile_id = await get_user_profile_id(get_user_id(current_user))
    
    async with get_async_session() as session:
        # Deactivate connection
        result = await session.execute(
            select(SocialConnection).where(
                and_(
                    SocialConnection.user_id == profile_id,
                    SocialConnection.provider == provider
                )
            )
        )
        conn = result.scalar_one_or_none()
        
        if conn:
            conn.is_active = False
            await session.commit()
            
            return {
                "success": True,
                "message": f"{provider} disconnected successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=f"{provider} connection not found")

# Posting Endpoints

@router.post("/post")
async def create_post(
    request: PostRequest,
    current_user = Depends(get_current_user)
):
    """
    Create and post content to social media platform(s)
    Supports immediate posting or scheduling
    """
    profile_id = await get_user_profile_id(get_user_id(current_user))
    
    try:
        # Get provider instance
        provider_instance = await get_provider_instance(request.provider, profile_id)
        
        # Post content
        post_result = await provider_instance.post_content(
            content=request.content,
            media_urls=request.media_urls
        )
        
        # Store post record
        async with get_async_session() as session:
            # Get connection
            conn_result = await session.execute(
                select(SocialConnection).where(
                    and_(
                        SocialConnection.user_id == profile_id,
                        SocialConnection.provider == request.provider
                    )
                )
            )
            connection = conn_result.scalar_one_or_none()
            
            social_post = SocialPost(
                user_id=profile_id,
                connection_id=connection.id if connection else None,
                content=request.content,
                media_urls=request.media_urls or [],
                platforms=[request.provider],
                platform_post_ids={request.provider: post_result.get('id')},
                posted_at=datetime.now(timezone.utc),
                status="posted"
            )
            session.add(social_post)
            await session.commit()
            await session.refresh(social_post)
            
            # Close provider
            await provider_instance.close()
            
            return {
                "success": True,
                "message": "Posted successfully",
                "post": {
                    "id": social_post.id,
                    "platform_post_id": post_result.get('id'),
                    "url": post_result.get('url'),
                    "posted_at": social_post.posted_at.isoformat()
                }
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
async def get_user_posts(
    limit: int = 20,
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get user's social media posts"""
    profile_id = await get_user_profile_id(get_user_id(current_user))
    
    async with get_async_session() as session:
        query = select(SocialPost).where(
            SocialPost.user_id == profile_id
        ).order_by(SocialPost.created_at.desc()).limit(limit)
        
        if status:
            query = query.where(SocialPost.status == status)
        
        result = await session.execute(query)
        posts = result.scalars().all()
        
        return {
            "posts": [
                {
                    "id": post.id,
                    "content": post.content,
                    "platforms": post.platforms,
                    "platform_post_ids": post.platform_post_ids,
                    "status": post.status,
                    "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                    "created_at": post.created_at.isoformat()
                }
                for post in posts
            ],
            "total": len(posts)
        }

@router.get("/metrics/dashboard")
async def get_metrics_dashboard(current_user = Depends(get_current_user)):
    """
    Get aggregated metrics dashboard for all connected platforms
    Includes real-time data from platform APIs
    """
    profile_id = await get_user_profile_id(get_user_id(current_user))
    
    dashboard_data = {
        "platforms": [],
        "total_followers": 0,
        "total_posts": 0,
        "avg_engagement": 0.0
    }
    
    async with get_async_session() as session:
        # Get all active connections
        result = await session.execute(
            select(SocialConnection).where(
                and_(
                    SocialConnection.user_id == profile_id,
                    SocialConnection.is_active == True
                )
            )
        )
        connections = result.scalars().all()
        
        total_engagement = 0
        engagement_count = 0
        
        for conn in connections:
            try:
                # Get provider instance
                provider_instance = await get_provider_instance(conn.provider, profile_id)
                
                # Get user metrics from platform
                metrics = await provider_instance.get_user_metrics()
                
                platform_data = {
                    "platform": conn.provider,
                    "name": conn.provider.capitalize(),
                    "username": conn.username,
                    "connected": True,
                    "followers": metrics.get('followers', 0),
                    "posts": metrics.get('tweets', 0) if conn.provider == 'twitter' else metrics.get('posts', 0),
                    "engagement_rate": metrics.get('engagement_rate', 0.0),
                    "profile_image": conn.profile_image_url
                }
                
                dashboard_data["platforms"].append(platform_data)
                dashboard_data["total_followers"] += platform_data["followers"]
                dashboard_data["total_posts"] += platform_data["posts"]
                
                if platform_data["engagement_rate"] > 0:
                    total_engagement += platform_data["engagement_rate"]
                    engagement_count += 1
                
                await provider_instance.close()
                
            except Exception as e:
                print(f"⚠️ Error getting metrics for {conn.provider}: {e}")
                # Add platform with error state
                dashboard_data["platforms"].append({
                    "platform": conn.provider,
                    "name": conn.provider.capitalize(),
                    "username": conn.username,
                    "connected": True,
                    "followers": 0,
                    "posts": 0,
                    "engagement_rate": 0.0,
                    "error": str(e)
                })
        
        if engagement_count > 0:
            dashboard_data["avg_engagement"] = round(total_engagement / engagement_count, 2)
        
        return dashboard_data

@router.get("/metrics/post/{post_id}")
async def get_post_metrics(
    post_id: str,
    current_user = Depends(get_current_user)
):
    """Get metrics for a specific post"""
    profile_id = await get_user_profile_id(get_user_id(current_user))
    
    async with get_async_session() as session:
        # Get post
        result = await session.execute(
            select(SocialPost).where(
                and_(
                    SocialPost.id == post_id,
                    SocialPost.user_id == profile_id
                )
            )
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Get metrics from each platform
        metrics = {}
        for platform in post.platforms:
            platform_post_id = post.platform_post_ids.get(platform)
            if platform_post_id:
                try:
                    provider_instance = await get_provider_instance(platform, profile_id)
                    platform_metrics = await provider_instance.get_post_metrics(platform_post_id)
                    metrics[platform] = platform_metrics
                    await provider_instance.close()
                except Exception as e:
                    print(f"⚠️ Error getting metrics for {platform}: {e}")
                    metrics[platform] = {"error": str(e)}
        
        return {
            "post_id": post_id,
            "content": post.content,
            "platforms": post.platforms,
            "metrics": metrics,
            "posted_at": post.posted_at.isoformat() if post.posted_at else None
        }

# Webhook Endpoints

@router.post("/webhook/{provider}")
async def webhook_receiver(provider: str, request: Request):
    """
    Receive webhooks from social media platforms
    Stores events for processing
    """
    try:
        # Get payload
        payload = await request.json()
        
        # Get signature for verification
        signature = request.headers.get('X-Signature') or request.headers.get('X-Hub-Signature')
        
        # Store webhook event
        async with get_async_session() as session:
            event = WebhookEvent(
                provider=provider,
                event_type=payload.get('event', 'unknown'),
                payload=payload,
                signature=signature,
                processed=False
            )
            session.add(event)
            await session.commit()
        
        return {"status": "received", "event_id": event.id}
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/health")
async def social_health():
    """Health check for social media integration"""
    return {
        "status": "healthy",
        "service": "social_media_integration",
        "providers": get_configured_providers()
    }
