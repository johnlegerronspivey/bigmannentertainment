"""
Snapchat Business API Provider
Integrates with Snapchat Ads API and Creative Studio
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import jwt


class SnapchatProvider:
    """Snapchat Business API integration provider"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://adsapi.snapchat.com/v1"
        self.creative_url = "https://canvas.snapchat.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def decode_token(self) -> Dict[str, Any]:
        """Decode JWT token to get metadata"""
        try:
            # Decode without verification for inspection
            decoded = jwt.decode(self.api_token, options={"verify_signature": False})
            return {
                "valid": True,
                "decoded": decoded,
                "audience": decoded.get("aud"),
                "issuer": decoded.get("iss"),
                "subject": decoded.get("sub")
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def verify_connection(self) -> Dict[str, Any]:
        """Verify API token and connection"""
        try:
            # Test with a simple API call
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "connected": True,
                    "status": "active",
                    "account_info": data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            elif response.status_code == 401:
                return {
                    "connected": False,
                    "status": "unauthorized",
                    "error": "Invalid or expired API token"
                }
            else:
                return {
                    "connected": False,
                    "status": "error",
                    "error": f"API returned status {response.status_code}",
                    "details": response.text
                }
        except requests.exceptions.RequestException as e:
            return {
                "connected": False,
                "status": "network_error",
                "error": str(e)
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Snapchat Business account information"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to fetch account info: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """Get list of ad accounts"""
        try:
            response = requests.get(
                f"{self.base_url}/me/adaccounts",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("adaccounts", [])
            else:
                return []
        except Exception as e:
            return []
    
    def get_campaigns(self, ad_account_id: str) -> List[Dict[str, Any]]:
        """Get campaigns for an ad account"""
        try:
            response = requests.get(
                f"{self.base_url}/adaccounts/{ad_account_id}/campaigns",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("campaigns", [])
            else:
                return []
        except Exception as e:
            return []
    
    def create_snap(self, media_url: str, caption: str = "", duration_ms: int = 10000) -> Dict[str, Any]:
        """Create a Snap (Story post)"""
        try:
            payload = {
                "media_url": media_url,
                "caption": caption,
                "duration_ms": duration_ms,
                "type": "IMAGE"  # or VIDEO
            }
            
            response = requests.post(
                f"{self.creative_url}/snaps",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create snap: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_creative(self, file_path: str, creative_type: str = "IMAGE") -> Dict[str, Any]:
        """Upload creative asset to Snapchat"""
        try:
            # First, get upload URL
            response = requests.post(
                f"{self.base_url}/media",
                headers=self.headers,
                json={"type": creative_type},
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "Failed to get upload URL"
                }
            
            upload_data = response.json()
            upload_url = upload_data.get("media", {}).get("upload_url")
            media_id = upload_data.get("media", {}).get("id")
            
            if not upload_url:
                return {
                    "success": False,
                    "error": "No upload URL provided"
                }
            
            # Upload file
            with open(file_path, 'rb') as f:
                upload_response = requests.put(
                    upload_url,
                    data=f,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=60
                )
            
            if upload_response.status_code in [200, 204]:
                return {
                    "success": True,
                    "media_id": media_id,
                    "upload_url": upload_url
                }
            else:
                return {
                    "success": False,
                    "error": f"Upload failed: {upload_response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_insights(self, ad_account_id: str, date_range: str = "LAST_7_DAYS") -> Dict[str, Any]:
        """Get performance insights"""
        try:
            params = {
                "time_range": date_range,
                "fields": "impressions,swipes,video_views,spend"
            }
            
            response = requests.get(
                f"{self.base_url}/adaccounts/{ad_account_id}/stats",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to fetch insights: {response.status_code}"
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_audience_demographics(self, ad_account_id: str) -> Dict[str, Any]:
        """Get audience demographics"""
        try:
            response = requests.get(
                f"{self.base_url}/adaccounts/{ad_account_id}/audience_segments",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to fetch demographics: {response.status_code}"
                }
        except Exception as e:
            return {"error": str(e)}
    
    def create_story_ad(self, ad_account_id: str, creative_id: str, 
                        name: str, daily_budget: float) -> Dict[str, Any]:
        """Create a Story Ad campaign"""
        try:
            payload = {
                "name": name,
                "status": "ACTIVE",
                "daily_budget_micro": int(daily_budget * 1000000),  # Convert to micro currency
                "creative_id": creative_id,
                "objective": "STORY_IMPRESSIONS"
            }
            
            response = requests.post(
                f"{self.base_url}/adaccounts/{ad_account_id}/campaigns",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "campaign": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create campaign: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_conversion_tracking(self, ad_account_id: str) -> Dict[str, Any]:
        """Get conversion tracking data"""
        try:
            response = requests.get(
                f"{self.base_url}/adaccounts/{ad_account_id}/pixel_domain_stats",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to fetch conversions: {response.status_code}"
                }
        except Exception as e:
            return {"error": str(e)}


class SnapchatMockProvider(SnapchatProvider):
    """Mock provider for testing without real API"""
    
    def __init__(self, api_token: str):
        super().__init__(api_token)
        self.mock_mode = True
    
    def verify_connection(self) -> Dict[str, Any]:
        """Mock connection verification"""
        # Decode token to verify format
        token_info = self.decode_token()
        
        if token_info["valid"]:
            return {
                "connected": True,
                "status": "active",
                "mode": "mock",
                "account_info": {
                    "id": "mock-account-123",
                    "name": "BME Snapchat Business",
                    "email": "business@bigmannentertainment.com",
                    "organization_id": "org-456"
                },
                "token_info": token_info,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "connected": False,
                "status": "invalid_token",
                "error": "Token format invalid"
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """Mock account info"""
        return {
            "id": "mock-account-123",
            "name": "BME Snapchat Business",
            "type": "BUSINESS",
            "organization": {
                "id": "org-456",
                "name": "Big Mann Entertainment"
            },
            "created_at": "2024-01-01T00:00:00Z",
            "status": "ACTIVE"
        }
    
    def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """Mock ad accounts"""
        return [
            {
                "id": "ad-account-789",
                "name": "BME Music Promotion",
                "status": "ACTIVE",
                "currency": "USD",
                "timezone": "America/Los_Angeles"
            }
        ]
    
    def get_insights(self, ad_account_id: str, date_range: str = "LAST_7_DAYS") -> Dict[str, Any]:
        """Mock insights"""
        return {
            "impressions": 125000,
            "swipes": 8500,
            "video_views": 45000,
            "spend": 1250.50,
            "ctr": 6.8,
            "date_range": date_range
        }
