"""
Base Social Media Provider
Abstract base class for all social media platform integrations
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
from datetime import datetime, timezone
import httpx

class BaseSocialProvider(ABC):
    """Base class for social media providers"""
    
    def __init__(self, access_token: str, provider_config: Dict[str, Any]):
        """
        Initialize provider with access token and configuration
        
        Args:
            access_token: OAuth access token
            provider_config: Provider-specific configuration from oauth_config
        """
        self.access_token = access_token
        self.config = provider_config
        self.api_base_url = provider_config.get('api_base_url')
        self.client = httpx.AsyncClient(
            base_url=self.api_base_url,
            timeout=30.0,
            headers=self._get_default_headers()
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    @abstractmethod
    async def get_user_profile(self) -> Dict[str, Any]:
        """
        Get authenticated user's profile information
        
        Returns:
            Dict with user profile data (id, username, name, etc.)
        """
        pass
    
    @abstractmethod
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to the platform
        
        Args:
            content: Text content to post
            media_urls: Optional list of media URLs
            **kwargs: Platform-specific parameters
        
        Returns:
            Dict with post data (id, url, created_at, etc.)
        """
        pass
    
    @abstractmethod
    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific post
        
        Args:
            post_id: Platform-specific post ID
        
        Returns:
            Dict with metrics (likes, shares, comments, views, etc.)
        """
        pass
    
    @abstractmethod
    async def get_user_metrics(self) -> Dict[str, Any]:
        """
        Get overall user metrics
        
        Returns:
            Dict with user metrics (followers, posts, engagement, etc.)
        """
        pass
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh the access token using refresh token
        
        Args:
            refresh_token: OAuth refresh token
        
        Returns:
            Dict with new tokens (access_token, refresh_token, expires_in)
        """
        # Default implementation - override if needed
        raise NotImplementedError(f"{self.__class__.__name__} does not support token refresh")
    
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from the platform
        
        Args:
            post_id: Platform-specific post ID
        
        Returns:
            True if successful, False otherwise
        """
        # Default implementation - override if needed
        raise NotImplementedError(f"{self.__class__.__name__} does not support post deletion")
    
    async def verify_webhook(self, payload: Dict, signature: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            payload: Webhook payload
            signature: Signature from webhook headers
        
        Returns:
            True if valid, False otherwise
        """
        # Default implementation - override if needed
        return True
    
    async def handle_webhook_event(self, event_type: str, payload: Dict) -> None:
        """
        Handle webhook event
        
        Args:
            event_type: Type of event
            payload: Event payload
        """
        # Default implementation - override if needed
        pass
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
