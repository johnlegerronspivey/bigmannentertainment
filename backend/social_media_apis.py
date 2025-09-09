"""
Social Media APIs Service - Phase 2: API Integration Foundation
Handles OAuth authentication and API integrations for major social media platforms.
"""

import os
import aiohttp
import json
import base64
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, parse_qs
from pydantic import BaseModel, Field
import jwt

class OAuthToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def is_expired(self) -> bool:
        if not self.expires_in:
            return False
        expiry_time = self.created_at + timedelta(seconds=self.expires_in)
        return datetime.now(timezone.utc) > expiry_time

class PlatformCredentials(BaseModel):
    platform_id: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: List[str]
    additional_params: Dict[str, Any] = {}

class UploadRequest(BaseModel):
    platform_id: str
    content_type: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    title: str
    description: Optional[str] = None
    tags: List[str] = []
    privacy: str = "public"
    scheduled_time: Optional[datetime] = None
    additional_metadata: Dict[str, Any] = {}

class UploadResponse(BaseModel):
    success: bool
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    message: str
    error_details: Optional[Dict[str, Any]] = None

class SocialMediaAPIs:
    def __init__(self):
        self.credentials = self._load_platform_credentials()
        self.oauth_tokens = {}  # Store active tokens
        
    def _load_platform_credentials(self) -> Dict[str, PlatformCredentials]:
        """Load platform credentials from environment variables"""
        base_url = os.environ.get('FRONTEND_URL', 'https://bigmannentertainment.com')
        
        return {
            "instagram": PlatformCredentials(
                platform_id="instagram",
                client_id=os.environ.get('INSTAGRAM_CLIENT_ID', ''),
                client_secret=os.environ.get('INSTAGRAM_CLIENT_SECRET', ''),
                redirect_uri=f"{base_url}/auth/instagram/callback",
                scope=["instagram_basic", "instagram_content_publish", "pages_show_list"]
            ),
            
            "youtube": PlatformCredentials(
                platform_id="youtube",
                client_id=os.environ.get('YOUTUBE_CLIENT_ID', ''),
                client_secret=os.environ.get('YOUTUBE_CLIENT_SECRET', ''),
                redirect_uri=f"{base_url}/auth/youtube/callback",
                scope=["https://www.googleapis.com/auth/youtube.upload", 
                      "https://www.googleapis.com/auth/youtube"]
            ),
            
            "tiktok": PlatformCredentials(
                platform_id="tiktok",
                client_id=os.environ.get('TIKTOK_CLIENT_ID', ''),
                client_secret=os.environ.get('TIKTOK_CLIENT_SECRET', ''),
                redirect_uri=f"{base_url}/auth/tiktok/callback",
                scope=["user.info.basic", "video.upload"]
            ),
            
            "twitter": PlatformCredentials(
                platform_id="twitter",
                client_id=os.environ.get('TWITTER_CLIENT_ID', ''),
                client_secret=os.environ.get('TWITTER_CLIENT_SECRET', ''),
                redirect_uri=f"{base_url}/auth/twitter/callback",
                scope=["tweet.read", "tweet.write", "users.read"]
            ),
            
            "linkedin": PlatformCredentials(
                platform_id="linkedin",
                client_id=os.environ.get('LINKEDIN_CLIENT_ID', ''),
                client_secret=os.environ.get('LINKEDIN_CLIENT_SECRET', ''),
                redirect_uri=f"{base_url}/auth/linkedin/callback",
                scope=["r_liteprofile", "r_emailaddress", "w_member_social"]
            ),
            
            "spotify": PlatformCredentials(
                platform_id="spotify",
                client_id=os.environ.get('SPOTIFY_CLIENT_ID', ''),
                client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET', ''),
                redirect_uri=f"{base_url}/auth/spotify/callback",
                scope=["user-read-private", "user-read-email", "playlist-modify-public"]
            )
        }
    
    async def get_authorization_url(self, platform_id: str, user_id: str) -> str:
        """Generate OAuth authorization URL for platform"""
        if platform_id not in self.credentials:
            raise ValueError(f"Platform {platform_id} not supported")
        
        creds = self.credentials[platform_id]
        state = self._generate_state_token(user_id, platform_id)
        
        # Platform-specific authorization URLs
        auth_urls = {
            "instagram": "https://api.instagram.com/oauth/authorize",
            "youtube": "https://accounts.google.com/o/oauth2/v2/auth",
            "tiktok": "https://www.tiktok.com/auth/authorize/",
            "twitter": "https://twitter.com/i/oauth2/authorize",
            "linkedin": "https://www.linkedin.com/oauth/v2/authorization",
            "spotify": "https://accounts.spotify.com/authorize"
        }
        
        base_url = auth_urls.get(platform_id)
        if not base_url:
            raise ValueError(f"Authorization URL not configured for {platform_id}")
        
        params = {
            "client_id": creds.client_id,
            "redirect_uri": creds.redirect_uri,
            "scope": " ".join(creds.scope),
            "response_type": "code",
            "state": state
        }
        
        # Platform-specific parameters
        if platform_id == "twitter":
            params["code_challenge"] = self._generate_pkce_challenge()
            params["code_challenge_method"] = "S256"
        
        return f"{base_url}?{urlencode(params)}"
    
    async def handle_oauth_callback(self, platform_id: str, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for access token"""
        if platform_id not in self.credentials:
            raise ValueError(f"Platform {platform_id} not supported")
        
        # Verify state token
        user_id = self._verify_state_token(state, platform_id)
        if not user_id:
            raise ValueError("Invalid state token")
        
        creds = self.credentials[platform_id]
        
        # Exchange authorization code for access token
        token_urls = {
            "instagram": "https://api.instagram.com/oauth/access_token",
            "youtube": "https://oauth2.googleapis.com/token",
            "tiktok": "https://open-api.tiktok.com/oauth/access_token/",
            "twitter": "https://api.twitter.com/2/oauth2/token",
            "linkedin": "https://www.linkedin.com/oauth/v2/accessToken",
            "spotify": "https://accounts.spotify.com/api/token"
        }
        
        token_url = token_urls.get(platform_id)
        if not token_url:
            raise ValueError(f"Token URL not configured for {platform_id}")
        
        # Prepare token request data
        token_data = {
            "grant_type": "authorization_code",
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "redirect_uri": creds.redirect_uri,
            "code": code
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as response:
                if response.status == 200:
                    token_info = await response.json()
                    
                    # Create OAuth token object
                    oauth_token = OAuthToken(
                        access_token=token_info["access_token"],
                        token_type=token_info.get("token_type", "Bearer"),
                        expires_in=token_info.get("expires_in"),
                        refresh_token=token_info.get("refresh_token"),
                        scope=token_info.get("scope")
                    )
                    
                    # Store token for user
                    if user_id not in self.oauth_tokens:
                        self.oauth_tokens[user_id] = {}
                    self.oauth_tokens[user_id][platform_id] = oauth_token
                    
                    return {
                        "success": True,
                        "platform": platform_id,
                        "user_id": user_id,
                        "expires_in": oauth_token.expires_in
                    }
                else:
                    error_data = await response.text()
                    return {
                        "success": False,
                        "error": f"Token exchange failed: {error_data}"
                    }
    
    async def upload_content(self, user_id: str, upload_request: UploadRequest) -> UploadResponse:
        """Upload content to specified platform"""
        platform_id = upload_request.platform_id
        
        # Check if user has valid token for platform
        if not self._has_valid_token(user_id, platform_id):
            return UploadResponse(
                success=False,
                message=f"No valid authentication token for {platform_id}"
            )
        
        token = self.oauth_tokens[user_id][platform_id]
        
        # Platform-specific upload logic
        upload_methods = {
            "instagram": self._upload_to_instagram,
            "youtube": self._upload_to_youtube,
            "tiktok": self._upload_to_tiktok,
            "twitter": self._upload_to_twitter,
            "linkedin": self._upload_to_linkedin,
            "spotify": self._upload_to_spotify
        }
        
        upload_method = upload_methods.get(platform_id)
        if not upload_method:
            return UploadResponse(
                success=False,
                message=f"Upload not implemented for {platform_id}"
            )
        
        return await upload_method(token, upload_request)
    
    async def _upload_to_instagram(self, token: OAuthToken, request: UploadRequest) -> UploadResponse:
        """Upload content to Instagram"""
        try:
            headers = {"Authorization": f"Bearer {token.access_token}"}
            
            # Instagram requires multi-step upload process
            if request.content_type == "image":
                # Step 1: Create media container
                create_url = "https://graph.facebook.com/v18.0/me/media"
                create_data = {
                    "image_url": request.file_url,
                    "caption": f"{request.title}\n{request.description}" if request.description else request.title,
                    "access_token": token.access_token
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(create_url, data=create_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            creation_id = result["id"]
                            
                            # Step 2: Publish media
                            publish_url = "https://graph.facebook.com/v18.0/me/media_publish"
                            publish_data = {
                                "creation_id": creation_id,
                                "access_token": token.access_token
                            }
                            
                            async with session.post(publish_url, data=publish_data) as pub_response:
                                if pub_response.status == 200:
                                    pub_result = await pub_response.json()
                                    return UploadResponse(
                                        success=True,
                                        platform_post_id=pub_result["id"],
                                        message="Successfully uploaded to Instagram"
                                    )
                                else:
                                    error_data = await pub_response.text()
                                    return UploadResponse(
                                        success=False,
                                        message=f"Instagram publish failed: {error_data}"
                                    )
                        else:
                            error_data = await response.text()
                            return UploadResponse(
                                success=False,
                                message=f"Instagram upload failed: {error_data}"
                            )
            
            return UploadResponse(
                success=False,
                message=f"Content type {request.content_type} not supported for Instagram"
            )
            
        except Exception as e:
            return UploadResponse(
                success=False,
                message=f"Instagram upload error: {str(e)}"
            )
    
    async def _upload_to_youtube(self, token: OAuthToken, request: UploadRequest) -> UploadResponse:
        """Upload content to YouTube"""
        try:
            if request.content_type != "video":
                return UploadResponse(
                    success=False,
                    message="YouTube only supports video uploads"
                )
            
            headers = {
                "Authorization": f"Bearer {token.access_token}",
                "Content-Type": "application/json"
            }
            
            # YouTube upload requires resumable upload
            upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
            params = {
                "part": "snippet,status",
                "uploadType": "resumable"
            }
            
            metadata = {
                "snippet": {
                    "title": request.title,
                    "description": request.description or "",
                    "tags": request.tags,
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": request.privacy
                }
            }
            
            async with aiohttp.ClientSession() as session:
                # This is a simplified version - actual YouTube upload requires resumable upload
                return UploadResponse(
                    success=False,
                    message="YouTube upload requires resumable upload implementation"
                )
                
        except Exception as e:
            return UploadResponse(
                success=False,
                message=f"YouTube upload error: {str(e)}"
            )
    
    async def _upload_to_tiktok(self, token: OAuthToken, request: UploadRequest) -> UploadResponse:
        """Upload content to TikTok"""
        try:
            if request.content_type != "video":
                return UploadResponse(
                    success=False,
                    message="TikTok only supports video uploads"
                )
            
            headers = {"Authorization": f"Bearer {token.access_token}"}
            
            # TikTok Content Publishing API
            upload_url = "https://open-api.tiktok.com/share/video/upload/"
            
            upload_data = {
                "video_url": request.file_url,
                "description": f"{request.title}\n{request.description}" if request.description else request.title,
                "privacy_level": "SELF_ONLY" if request.privacy == "private" else "PUBLIC_TO_EVERYONE"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(upload_url, headers=headers, json=upload_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("error", {}).get("code") == "ok":
                            return UploadResponse(
                                success=True,
                                platform_post_id=result.get("data", {}).get("share_id"),
                                message="Successfully uploaded to TikTok"
                            )
                        else:
                            return UploadResponse(
                                success=False,
                                message=f"TikTok upload failed: {result.get('error', {}).get('message')}"
                            )
                    else:
                        error_data = await response.text()
                        return UploadResponse(
                            success=False,
                            message=f"TikTok upload failed: {error_data}"
                        )
                        
        except Exception as e:
            return UploadResponse(
                success=False,
                message=f"TikTok upload error: {str(e)}"
            )
    
    async def _upload_to_twitter(self, token: OAuthToken, request: UploadRequest) -> UploadResponse:
        """Upload content to Twitter"""
        try:
            headers = {"Authorization": f"Bearer {token.access_token}"}
            
            if request.content_type == "text":
                # Text tweet
                tweet_url = "https://api.twitter.com/2/tweets"
                tweet_data = {
                    "text": f"{request.title}\n{request.description}" if request.description else request.title
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(tweet_url, headers=headers, json=tweet_data) as response:
                        if response.status == 201:
                            result = await response.json()
                            return UploadResponse(
                                success=True,
                                platform_post_id=result["data"]["id"],
                                platform_url=f"https://twitter.com/user/status/{result['data']['id']}",
                                message="Successfully posted to Twitter"
                            )
                        else:
                            error_data = await response.text()
                            return UploadResponse(
                                success=False,
                                message=f"Twitter post failed: {error_data}"
                            )
            else:
                return UploadResponse(
                    success=False,
                    message="Media uploads to Twitter require additional implementation"
                )
                
        except Exception as e:
            return UploadResponse(
                success=False,
                message=f"Twitter upload error: {str(e)}"
            )
    
    async def _upload_to_linkedin(self, token: OAuthToken, request: UploadRequest) -> UploadResponse:
        """Upload content to LinkedIn"""
        try:
            headers = {"Authorization": f"Bearer {token.access_token}"}
            
            # LinkedIn Posts API
            post_url = "https://api.linkedin.com/v2/posts"
            
            post_data = {
                "author": "urn:li:person:YOUR_PERSON_ID",  # This would need to be dynamically determined
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": f"{request.title}\n{request.description}" if request.description else request.title
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(post_url, headers=headers, json=post_data) as response:
                    if response.status == 201:
                        result = await response.json()
                        return UploadResponse(
                            success=True,
                            platform_post_id=result.get("id"),
                            message="Successfully posted to LinkedIn"
                        )
                    else:
                        error_data = await response.text()
                        return UploadResponse(
                            success=False,
                            message=f"LinkedIn post failed: {error_data}"
                        )
                        
        except Exception as e:
            return UploadResponse(
                success=False,
                message=f"LinkedIn upload error: {str(e)}"
            )
    
    async def _upload_to_spotify(self, token: OAuthToken, request: UploadRequest) -> UploadResponse:
        """Handle Spotify integration (playlist creation, not direct upload)"""
        try:
            if request.content_type != "music":
                return UploadResponse(
                    success=False,
                    message="Spotify integration is for music playlist management only"
                )
            
            headers = {"Authorization": f"Bearer {token.access_token}"}
            
            # Create playlist or add to existing playlist
            # This is a simplified example - actual music upload to Spotify requires distribution services
            return UploadResponse(
                success=False,
                message="Direct music upload to Spotify requires distribution service integration"
            )
            
        except Exception as e:
            return UploadResponse(
                success=False,
                message=f"Spotify integration error: {str(e)}"
            )
    
    def _has_valid_token(self, user_id: str, platform_id: str) -> bool:
        """Check if user has valid authentication token for platform"""
        if user_id not in self.oauth_tokens:
            return False
        
        if platform_id not in self.oauth_tokens[user_id]:
            return False
        
        token = self.oauth_tokens[user_id][platform_id]
        return not token.is_expired
    
    def _generate_state_token(self, user_id: str, platform_id: str) -> str:
        """Generate secure state token for OAuth flow"""
        data = f"{user_id}:{platform_id}:{secrets.token_urlsafe(16)}"
        return base64.urlsafe_b64encode(data.encode()).decode()
    
    def _verify_state_token(self, state: str, platform_id: str) -> Optional[str]:
        """Verify state token and return user_id if valid"""
        try:
            decoded_data = base64.urlsafe_b64decode(state.encode()).decode()
            parts = decoded_data.split(":")
            if len(parts) >= 3 and parts[1] == platform_id:
                return parts[0]  # user_id
        except Exception:
            pass
        return None
    
    def _generate_pkce_challenge(self) -> str:
        """Generate PKCE challenge for Twitter OAuth 2.0"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        return code_challenge
    
    async def get_platform_analytics(self, user_id: str, platform_id: str, 
                                   post_id: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics data from platform APIs"""
        if not self._has_valid_token(user_id, platform_id):
            return {"error": "No valid authentication token"}
        
        token = self.oauth_tokens[user_id][platform_id]
        headers = {"Authorization": f"Bearer {token.access_token}"}
        
        # Platform-specific analytics endpoints
        analytics_urls = {
            "instagram": f"https://graph.facebook.com/v18.0/{post_id}/insights",
            "youtube": f"https://youtubeanalytics.googleapis.com/v2/reports",
            "tiktok": "https://open-api.tiktok.com/video/data/",
            "twitter": f"https://api.twitter.com/2/tweets/{post_id}/metrics"
        }
        
        analytics_url = analytics_urls.get(platform_id)
        if not analytics_url:
            return {"error": f"Analytics not implemented for {platform_id}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(analytics_url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        return {"error": f"Analytics request failed: {error_data}"}
        except Exception as e:
            return {"error": f"Analytics error: {str(e)}"}
    
    async def refresh_token(self, user_id: str, platform_id: str) -> bool:
        """Refresh expired access token using refresh token"""
        if user_id not in self.oauth_tokens or platform_id not in self.oauth_tokens[user_id]:
            return False
        
        token = self.oauth_tokens[user_id][platform_id]
        if not token.refresh_token:
            return False
        
        creds = self.credentials[platform_id]
        
        # Platform-specific token refresh URLs
        refresh_urls = {
            "youtube": "https://oauth2.googleapis.com/token",
            "spotify": "https://accounts.spotify.com/api/token",
            "linkedin": "https://www.linkedin.com/oauth/v2/accessToken"
        }
        
        refresh_url = refresh_urls.get(platform_id)
        if not refresh_url:
            return False
        
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(refresh_url, data=refresh_data) as response:
                    if response.status == 200:
                        token_info = await response.json()
                        
                        # Update token
                        token.access_token = token_info["access_token"]
                        token.expires_in = token_info.get("expires_in")
                        token.created_at = datetime.now(timezone.utc)
                        
                        if "refresh_token" in token_info:
                            token.refresh_token = token_info["refresh_token"]
                        
                        return True
        except Exception as e:
            print(f"Token refresh error for {platform_id}: {str(e)}")
        
        return False