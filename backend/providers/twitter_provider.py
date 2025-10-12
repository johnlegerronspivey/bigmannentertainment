"""
Twitter/X API Provider Implementation
Implements posting, metrics retrieval, and OAuth for Twitter API v2
"""
from typing import Dict, Optional, List, Any
from datetime import datetime, timezone
import httpx
from .base_provider import BaseSocialProvider

class TwitterProvider(BaseSocialProvider):
    """Twitter API v2 provider implementation"""
    
    def __init__(self, access_token: str, provider_config: Dict[str, Any]):
        super().__init__(access_token, provider_config)
        # Twitter API v2 uses different base URL
        self.api_base_url = "https://api.twitter.com/2/"
        self.client = httpx.AsyncClient(
            base_url=self.api_base_url,
            timeout=30.0,
            headers=self._get_default_headers()
        )
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """
        Get authenticated user's Twitter profile
        
        Returns:
            {
                'id': '123456',
                'username': 'example',
                'name': 'Example User',
                'profile_image_url': 'https://...',
                'public_metrics': {
                    'followers_count': 1000,
                    'following_count': 500,
                    'tweet_count': 5000
                }
            }
        """
        try:
            response = await self.client.get(
                "users/me",
                params={
                    "user.fields": "id,name,username,profile_image_url,public_metrics,description,created_at"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                return data['data']
            return data
            
        except httpx.HTTPStatusError as e:
            print(f"❌ Twitter API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to get Twitter profile: {e.response.text}")
        except Exception as e:
            print(f"❌ Error getting Twitter profile: {e}")
            raise
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post a tweet
        
        Args:
            content: Tweet text (max 280 characters)
            media_urls: Optional list of media URLs (not yet implemented)
            **kwargs: Additional parameters (reply_to, quote_tweet_id, etc.)
        
        Returns:
            {
                'id': 'tweet_id',
                'text': 'Tweet content',
                'created_at': '2025-01-07T...',
                'url': 'https://twitter.com/user/status/tweet_id'
            }
        """
        try:
            # Prepare tweet data
            tweet_data = {
                "text": content[:280]  # Enforce character limit
            }
            
            # Add reply or quote tweet if specified
            if kwargs.get('reply_to'):
                tweet_data['reply'] = {
                    'in_reply_to_tweet_id': kwargs['reply_to']
                }
            
            if kwargs.get('quote_tweet_id'):
                tweet_data['quote_tweet_id'] = kwargs['quote_tweet_id']
            
            # Post tweet
            response = await self.client.post(
                "tweets",
                json=tweet_data
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                tweet = data['data']
                # Get user info to construct URL
                user_profile = await self.get_user_profile()
                tweet['url'] = f"https://twitter.com/{user_profile['username']}/status/{tweet['id']}"
                tweet['created_at'] = datetime.now(timezone.utc).isoformat()
                return tweet
            
            return data
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.headers.get('content-type') == 'application/json' else e.response.text
            print(f"❌ Twitter API error posting tweet: {e.response.status_code} - {error_detail}")
            raise Exception(f"Failed to post tweet: {error_detail}")
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            raise
    
    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific tweet
        
        Args:
            post_id: Twitter tweet ID
        
        Returns:
            {
                'likes': 10,
                'retweets': 5,
                'replies': 3,
                'impressions': 1000,
                'engagement_rate': 1.8
            }
        """
        try:
            # Get tweet with metrics
            response = await self.client.get(
                f"tweets/{post_id}",
                params={
                    "tweet.fields": "public_metrics,created_at",
                    "expansions": "author_id"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                tweet = data['data']
                public_metrics = tweet.get('public_metrics', {})
                
                # Calculate engagement rate
                impressions = public_metrics.get('impression_count', 0)
                engagements = (
                    public_metrics.get('like_count', 0) +
                    public_metrics.get('retweet_count', 0) +
                    public_metrics.get('reply_count', 0) +
                    public_metrics.get('quote_count', 0)
                )
                engagement_rate = (engagements / impressions * 100) if impressions > 0 else 0
                
                return {
                    'likes': public_metrics.get('like_count', 0),
                    'retweets': public_metrics.get('retweet_count', 0),
                    'replies': public_metrics.get('reply_count', 0),
                    'quotes': public_metrics.get('quote_count', 0),
                    'impressions': impressions,
                    'engagement_rate': round(engagement_rate, 2),
                    'collected_at': datetime.now(timezone.utc).isoformat()
                }
            
            return {}
            
        except httpx.HTTPStatusError as e:
            # If metrics not available (e.g., tweet too new), return zeros
            if e.response.status_code == 404:
                return {
                    'likes': 0,
                    'retweets': 0,
                    'replies': 0,
                    'quotes': 0,
                    'impressions': 0,
                    'engagement_rate': 0.0,
                    'collected_at': datetime.now(timezone.utc).isoformat()
                }
            print(f"❌ Twitter API error getting metrics: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to get tweet metrics: {e.response.text}")
        except Exception as e:
            print(f"❌ Error getting tweet metrics: {e}")
            raise
    
    async def get_user_metrics(self) -> Dict[str, Any]:
        """
        Get overall user metrics from Twitter
        
        Returns:
            {
                'followers': 1000,
                'following': 500,
                'tweets': 5000,
                'engagement_rate': 2.5
            }
        """
        try:
            profile = await self.get_user_profile()
            public_metrics = profile.get('public_metrics', {})
            
            return {
                'followers': public_metrics.get('followers_count', 0),
                'following': public_metrics.get('following_count', 0),
                'tweets': public_metrics.get('tweet_count', 0),
                'listed_count': public_metrics.get('listed_count', 0),
                'engagement_rate': 0.0  # Would need historical data to calculate
            }
            
        except Exception as e:
            print(f"❌ Error getting user metrics: {e}")
            raise
    
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a tweet
        
        Args:
            post_id: Twitter tweet ID
        
        Returns:
            True if successful
        """
        try:
            response = await self.client.delete(f"tweets/{post_id}")
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('deleted', False)
            
        except httpx.HTTPStatusError as e:
            print(f"❌ Twitter API error deleting tweet: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Error deleting tweet: {e}")
            return False
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh Twitter OAuth 2.0 access token
        
        Args:
            refresh_token: OAuth refresh token
        
        Returns:
            {
                'access_token': 'new_token',
                'refresh_token': 'new_refresh_token',
                'expires_in': 7200
            }
        """
        try:
            # Twitter OAuth 2.0 token refresh
            token_url = "https://api.twitter.com/2/oauth2/token"
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.config.get('client_id')
            }
            
            # Use basic auth for client credentials
            import base64
            client_id = self.config.get('client_id')
            client_secret = self.config.get('client_secret')
            credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            print(f"❌ Error refreshing token: {e}")
            raise
