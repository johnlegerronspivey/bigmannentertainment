"""
TikTok API Provider Implementation
Implements OAuth 2.0, content posting, analytics, and user profile management for TikTok
Based on TikTok for Developers API v2
"""
from typing import Dict, Optional, List, Any, BinaryIO
from datetime import datetime, timezone
import httpx
import math
from pathlib import Path
from .base_provider import BaseSocialProvider


class TikTokProvider(BaseSocialProvider):
    """TikTok API v2 provider implementation with OAuth 2.0, content publishing, and analytics"""
    
    # Chunking parameters for video uploads
    CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks
    MIN_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB minimum
    MAX_CHUNK_SIZE = 64 * 1024 * 1024  # 64MB maximum
    
    def __init__(self, access_token: str, provider_config: Dict[str, Any]):
        super().__init__(access_token, provider_config)
        # TikTok API v2 uses different base URL
        self.api_base_url = "https://open.tiktokapis.com"
        self.auth_base_url = "https://www.tiktok.com/v2/auth"
        self.client = httpx.AsyncClient(
            base_url=self.api_base_url,
            timeout=60.0,  # Longer timeout for uploads
            headers=self._get_default_headers()
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for TikTok API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """
        Get authenticated user's TikTok profile with all available fields
        
        Returns:
            {
                'open_id': 'user_open_id',
                'union_id': 'user_union_id',
                'avatar_url': 'https://...',
                'display_name': 'User Name',
                'username': 'username',
                'bio_description': 'User bio',
                'is_verified': True/False,
                'follower_count': 1000,
                'following_count': 500,
                'likes_count': 5000,
                'video_count': 100
            }
        """
        try:
            # Request all available user info fields
            response = await self.client.get(
                "/v2/user/info/",
                params={
                    "fields": ",".join([
                        "open_id",
                        "union_id",
                        "avatar_url",
                        "avatar_url_100",
                        "avatar_large_url",
                        "display_name",
                        "bio_description",
                        "profile_deep_link",
                        "is_verified",
                        "username",
                        "follower_count",
                        "following_count",
                        "likes_count",
                        "video_count"
                    ])
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'user' in data['data']:
                return data['data']['user']
            return data
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.headers.get('content-type', '').startswith('application/json') else e.response.text
            print(f"❌ TikTok API error getting profile: {e.response.status_code} - {error_detail}")
            raise Exception(f"Failed to get TikTok profile: {error_detail}")
        except Exception as e:
            print(f"❌ Error getting TikTok profile: {e}")
            raise
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to TikTok (video or photo)
        
        Args:
            content: Post title/description
            media_urls: List of media URLs (for photos) or local file path (for video)
            **kwargs: Additional parameters
                - media_type: 'video' or 'photo' (default: 'video')
                - video_file: Path to video file for direct upload
                - privacy_level: 'PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS', 'SELF_ONLY'
                - disable_comment: bool
                - disable_duet: bool
                - disable_stitch: bool
                - auto_add_music: bool (for photos)
        
        Returns:
            {
                'id': 'publish_id',
                'status': 'processing' or 'uploaded',
                'message': 'Status message'
            }
        """
        media_type = kwargs.get('media_type', 'video')
        
        if media_type == 'photo':
            return await self._publish_photo(content, media_urls or [], **kwargs)
        else:
            video_file = kwargs.get('video_file')
            if video_file:
                return await self._publish_video_from_file(video_file, content, **kwargs)
            elif media_urls and len(media_urls) > 0:
                return await self._publish_video_from_url(media_urls[0], content, **kwargs)
            else:
                raise ValueError("Either video_file or media_urls must be provided for video posts")
    
    async def _publish_video_from_file(
        self,
        video_path: str,
        title: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish video to TikTok from local file using FILE_UPLOAD method
        """
        try:
            video_file = Path(video_path)
            if not video_file.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            video_size = video_file.stat().st_size
            
            # Calculate chunking parameters
            if video_size < self.MIN_CHUNK_SIZE:
                chunk_size = video_size
                total_chunk_count = 1
            else:
                chunk_size = self.CHUNK_SIZE
                total_chunk_count = math.ceil(video_size / chunk_size)
            
            # Get parameters with defaults
            privacy_level = kwargs.get('privacy_level', 'PUBLIC_TO_EVERYONE')
            disable_comment = kwargs.get('disable_comment', False)
            disable_duet = kwargs.get('disable_duet', False)
            disable_stitch = kwargs.get('disable_stitch', False)
            video_cover_timestamp_ms = kwargs.get('video_cover_timestamp_ms', 1000)
            
            # Initialize video upload
            init_data = {
                "post_info": {
                    "title": title,
                    "privacy_level": privacy_level,
                    "disable_duet": disable_duet,
                    "disable_comment": disable_comment,
                    "disable_stitch": disable_stitch,
                    "video_cover_timestamp_ms": video_cover_timestamp_ms
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": video_size,
                    "chunk_size": chunk_size,
                    "total_chunk_count": total_chunk_count
                }
            }
            
            response = await self.client.post(
                "/v2/post/publish/video/init/",
                json=init_data
            )
            response.raise_for_status()
            init_response = response.json()
            
            upload_url = init_response['data']['upload_url']
            publish_id = init_response['data']['publish_id']
            
            # Upload video in chunks
            with open(video_path, "rb") as vf:
                await self._upload_video_chunks(
                    upload_url=upload_url,
                    video_file=vf,
                    video_size=video_size,
                    chunk_size=chunk_size,
                    total_chunk_count=total_chunk_count
                )
            
            return {
                'id': publish_id,
                'status': 'uploaded',
                'message': 'Video uploaded successfully and is being processed by TikTok'
            }
            
        except Exception as e:
            print(f"❌ Error publishing video from file: {e}")
            raise
    
    async def _upload_video_chunks(
        self,
        upload_url: str,
        video_file: BinaryIO,
        video_size: int,
        chunk_size: int,
        total_chunk_count: int
    ):
        """Upload video file in chunks to TikTok servers"""
        async with httpx.AsyncClient(timeout=300.0) as client:
            for chunk_index in range(total_chunk_count):
                # Calculate chunk boundaries
                start_byte = chunk_index * chunk_size
                
                if chunk_index == total_chunk_count - 1:
                    # Last chunk includes trailing bytes
                    end_byte = video_size - 1
                    current_chunk_size = video_size - start_byte
                else:
                    end_byte = start_byte + chunk_size - 1
                    current_chunk_size = chunk_size
                
                # Read chunk data
                video_file.seek(start_byte)
                chunk_data = video_file.read(current_chunk_size)
                
                # Upload chunk
                headers = {
                    "Content-Type": "video/mp4",
                    "Content-Length": str(current_chunk_size),
                    "Content-Range": f"bytes {start_byte}-{end_byte}/{video_size}"
                }
                
                response = await client.put(
                    upload_url,
                    content=chunk_data,
                    headers=headers
                )
                
                # Check response status
                if chunk_index < total_chunk_count - 1:
                    if response.status_code != 206:
                        raise Exception(f"Chunk upload failed: {response.status_code} - {response.text}")
                else:
                    if response.status_code != 201:
                        raise Exception(f"Final chunk upload failed: {response.status_code} - {response.text}")
    
    async def _publish_video_from_url(
        self,
        video_url: str,
        title: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish video to TikTok from URL using PULL_FROM_URL method
        Note: Domain must be verified in TikTok developer portal
        """
        try:
            privacy_level = kwargs.get('privacy_level', 'PUBLIC_TO_EVERYONE')
            disable_comment = kwargs.get('disable_comment', False)
            disable_duet = kwargs.get('disable_duet', False)
            disable_stitch = kwargs.get('disable_stitch', False)
            video_cover_timestamp_ms = kwargs.get('video_cover_timestamp_ms', 1000)
            
            init_data = {
                "post_info": {
                    "title": title,
                    "privacy_level": privacy_level,
                    "disable_duet": disable_duet,
                    "disable_comment": disable_comment,
                    "disable_stitch": disable_stitch,
                    "video_cover_timestamp_ms": video_cover_timestamp_ms
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url
                }
            }
            
            response = await self.client.post(
                "/v2/post/publish/video/init/",
                json=init_data
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'id': data['data']['publish_id'],
                'status': 'processing',
                'message': 'Video is being processed by TikTok'
            }
            
        except Exception as e:
            print(f"❌ Error publishing video from URL: {e}")
            raise
    
    async def _publish_photo(
        self,
        title: str,
        photo_urls: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish photo post to TikTok from URLs
        Note: Photo URLs must be from verified domains (1-35 photos)
        """
        try:
            if not photo_urls or len(photo_urls) > 35:
                raise ValueError("Must provide 1-35 photo URLs")
            
            privacy_level = kwargs.get('privacy_level', 'PUBLIC_TO_EVERYONE')
            disable_comment = kwargs.get('disable_comment', False)
            auto_add_music = kwargs.get('auto_add_music', True)
            description = kwargs.get('description', '')
            photo_cover_index = kwargs.get('photo_cover_index', 1)
            
            init_data = {
                "post_info": {
                    "title": title,
                    "description": description,
                    "privacy_level": privacy_level,
                    "disable_comment": disable_comment,
                    "auto_add_music": auto_add_music
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "photo_cover_index": photo_cover_index,
                    "photo_images": photo_urls
                },
                "post_mode": "DIRECT_POST",
                "media_type": "PHOTO"
            }
            
            response = await self.client.post(
                "/v2/post/publish/content/init/",
                json=init_data
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'id': data['data']['publish_id'],
                'status': 'processing',
                'message': 'Photo post is being processed by TikTok'
            }
            
        except Exception as e:
            print(f"❌ Error publishing photo: {e}")
            raise
    
    async def get_publish_status(self, publish_id: str) -> Dict[str, Any]:
        """
        Check status of published content
        
        Args:
            publish_id: Publish ID from initialization response
        
        Returns:
            Dict with status information
        """
        try:
            response = await self.client.post(
                "/v2/post/publish/status/fetch/",
                json={"publish_id": publish_id}
            )
            response.raise_for_status()
            data = response.json()
            return data.get('data', {})
            
        except Exception as e:
            print(f"❌ Error getting publish status: {e}")
            raise
    
    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific TikTok video
        
        Args:
            post_id: TikTok video ID
        
        Returns:
            {
                'likes': 100,
                'comments': 50,
                'shares': 25,
                'views': 10000,
                'engagement_rate': 1.75
            }
        """
        try:
            # Get video list and find the specific video
            videos = await self._get_video_list(max_count=20)
            
            video = next((v for v in videos.get('videos', []) if v.get('id') == post_id), None)
            
            if not video:
                return {
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'views': 0,
                    'engagement_rate': 0.0,
                    'collected_at': datetime.now(timezone.utc).isoformat()
                }
            
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)
            shares = video.get('share_count', 0)
            views = video.get('view_count', 0)
            
            engagement = likes + comments + shares
            engagement_rate = (engagement / views * 100) if views > 0 else 0
            
            return {
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'views': views,
                'engagement_rate': round(engagement_rate, 2),
                'collected_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting post metrics: {e}")
            raise
    
    async def get_user_metrics(self) -> Dict[str, Any]:
        """
        Get overall user metrics from TikTok
        
        Returns:
            {
                'followers': 1000,
                'following': 500,
                'likes': 50000,
                'videos': 100,
                'engagement_rate': 2.5
            }
        """
        try:
            profile = await self.get_user_profile()
            
            # Get video metrics for engagement rate calculation
            videos = await self._get_all_videos()
            
            # Calculate aggregate metrics
            total_likes = sum(video.get('like_count', 0) for video in videos)
            total_comments = sum(video.get('comment_count', 0) for video in videos)
            total_shares = sum(video.get('share_count', 0) for video in videos)
            total_views = sum(video.get('view_count', 0) for video in videos)
            
            # Calculate overall engagement rate
            engagement_rate = 0.0
            if total_views > 0:
                total_engagement = total_likes + total_comments + total_shares
                engagement_rate = (total_engagement / total_views) * 100
            
            return {
                'followers': profile.get('follower_count', 0),
                'following': profile.get('following_count', 0),
                'likes': profile.get('likes_count', 0),
                'videos': profile.get('video_count', 0),
                'engagement_rate': round(engagement_rate, 2),
                'total_views': total_views,
                'average_views_per_video': round(total_views / len(videos), 2) if videos else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting user metrics: {e}")
            raise
    
    async def _get_video_list(
        self,
        max_count: int = 20,
        cursor: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get paginated list of user's public videos
        
        Args:
            max_count: Number of videos per page (max 20)
            cursor: Pagination cursor
        
        Returns:
            {
                'videos': [...],
                'cursor': 123,
                'has_more': True/False
            }
        """
        try:
            if max_count > 20:
                max_count = 20
            
            fields = [
                "id", "create_time", "cover_image_url", "share_url",
                "video_description", "duration", "height", "width",
                "title", "like_count", "comment_count", "share_count", "view_count"
            ]
            
            endpoint = f"/v2/video/list/?fields={','.join(fields)}"
            
            body = {"max_count": max_count}
            if cursor is not None:
                body["cursor"] = cursor
            
            response = await self.client.post(endpoint, json=body)
            response.raise_for_status()
            data = response.json()
            
            return data.get('data', {})
            
        except Exception as e:
            print(f"❌ Error getting video list: {e}")
            raise
    
    async def _get_all_videos(self) -> List[Dict[str, Any]]:
        """
        Retrieve all videos for a user by paginating through results
        
        Returns:
            List of all videos
        """
        all_videos = []
        cursor = None
        has_more = True
        
        try:
            while has_more:
                result = await self._get_video_list(max_count=20, cursor=cursor)
                all_videos.extend(result.get('videos', []))
                cursor = result.get('cursor')
                has_more = result.get('has_more', False)
            
            return all_videos
        except Exception as e:
            print(f"❌ Error getting all videos: {e}")
            return all_videos  # Return partial results
    
    async def get_analytics_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics dashboard data
        
        Returns:
            Complete analytics including profile stats and video metrics
        """
        try:
            # Get user profile with stats
            user_info = await self.get_user_profile()
            
            # Get all videos
            videos = await self._get_all_videos()
            
            # Calculate aggregate metrics
            total_likes = sum(video.get('like_count', 0) for video in videos)
            total_comments = sum(video.get('comment_count', 0) for video in videos)
            total_shares = sum(video.get('share_count', 0) for video in videos)
            total_views = sum(video.get('view_count', 0) for video in videos)
            
            avg_likes = total_likes / len(videos) if videos else 0
            avg_comments = total_comments / len(videos) if videos else 0
            avg_shares = total_shares / len(videos) if videos else 0
            avg_views = total_views / len(videos) if videos else 0
            
            # Calculate engagement rate
            engagement_rate = 0
            if total_views > 0:
                engagement_rate = ((total_likes + total_comments + total_shares) / total_views) * 100
            
            return {
                "profile": {
                    "display_name": user_info.get('display_name'),
                    "username": user_info.get('username'),
                    "is_verified": user_info.get('is_verified', False),
                    "avatar_url": user_info.get('avatar_url'),
                    "bio_description": user_info.get('bio_description', ''),
                    "profile_link": user_info.get('profile_deep_link', '')
                },
                "stats": {
                    "follower_count": user_info.get('follower_count', 0),
                    "following_count": user_info.get('following_count', 0),
                    "likes_count": user_info.get('likes_count', 0),
                    "video_count": user_info.get('video_count', 0)
                },
                "video_metrics": {
                    "total_videos": len(videos),
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "total_shares": total_shares,
                    "total_views": total_views,
                    "average_likes_per_video": round(avg_likes, 2),
                    "average_comments_per_video": round(avg_comments, 2),
                    "average_shares_per_video": round(avg_shares, 2),
                    "average_views_per_video": round(avg_views, 2),
                    "engagement_rate": round(engagement_rate, 2)
                },
                "recent_videos": videos[:10] if len(videos) > 10 else videos
            }
            
        except Exception as e:
            print(f"❌ Error getting analytics dashboard: {e}")
            raise
    
    async def delete_post(self, post_id: str) -> bool:
        """
        Note: TikTok API does not support post deletion via API
        Users must delete content through the TikTok app
        
        Args:
            post_id: TikTok video ID
        
        Returns:
            False (not supported)
        """
        print("ℹ️  TikTok API does not support post deletion. Users must delete content through the TikTok app.")
        return False
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh TikTok OAuth 2.0 access token
        
        Args:
            refresh_token: OAuth refresh token
        
        Returns:
            {
                'access_token': 'new_token',
                'refresh_token': 'new_refresh_token',
                'expires_in': 86400
            }
        """
        try:
            token_url = f"{self.api_base_url}/v2/oauth/token/"
            
            data = {
                "client_key": self.config.get('client_id'),
                "client_secret": self.config.get('client_secret'),
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            print(f"❌ Error refreshing TikTok token: {e}")
            raise
