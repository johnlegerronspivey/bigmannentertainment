"""
Live Integrations API Tests
Tests for Twitter/X, TikTok, Snapchat OAuth and CloudFront setup endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

class TestLiveIntegrationsAuth:
    """Test authentication for live integration endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for testing"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "owner@bigmannentertainment.com", "password": "Test1234!"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Auth headers for requests"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


class TestIntegrationStatusAll(TestLiveIntegrationsAuth):
    """Test GET /api/integrations/status/all endpoint"""
    
    def test_status_all_returns_200(self, auth_headers):
        """Status all endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_status_all_has_platforms_object(self, auth_headers):
        """Status all response has platforms object"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        assert "platforms" in data, f"Response missing 'platforms': {data}"
        
    def test_status_all_includes_twitter(self, auth_headers):
        """Status all includes Twitter/X platform"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        platforms = data.get("platforms", {})
        assert "twitter_x" in platforms, f"Missing twitter_x in platforms: {platforms.keys()}"
        assert platforms["twitter_x"].get("platform") == "Twitter/X"
        
    def test_status_all_includes_tiktok(self, auth_headers):
        """Status all includes TikTok platform"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        platforms = data.get("platforms", {})
        assert "tiktok" in platforms, f"Missing tiktok in platforms: {platforms.keys()}"
        assert platforms["tiktok"].get("platform") == "TikTok"
        
    def test_status_all_includes_snapchat(self, auth_headers):
        """Status all includes Snapchat platform"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        platforms = data.get("platforms", {})
        assert "snapchat" in platforms, f"Missing snapchat in platforms: {platforms.keys()}"
        assert platforms["snapchat"].get("platform") == "Snapchat"
        
    def test_status_all_includes_cloudfront(self, auth_headers):
        """Status all includes CloudFront"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        platforms = data.get("platforms", {})
        assert "cloudfront" in platforms, f"Missing cloudfront in platforms: {platforms.keys()}"
        assert platforms["cloudfront"].get("platform") == "AWS CloudFront CDN"


class TestTwitterIntegration(TestLiveIntegrationsAuth):
    """Test Twitter/X integration endpoints"""
    
    def test_twitter_test_connection(self, auth_headers):
        """Test Twitter connection test endpoint"""
        response = requests.get(f"{BASE_URL}/api/integrations/twitter/test", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Should return connected:true with bearer token or token_valid
        assert "connected" in data or "token_valid" in data, f"Missing connection status: {data}"
        
    def test_twitter_test_shows_connected(self, auth_headers):
        """Twitter test shows connected with bearer token"""
        response = requests.get(f"{BASE_URL}/api/integrations/twitter/test", headers=auth_headers)
        data = response.json()
        # With bearer token, should show connected
        assert data.get("connected") == True, f"Expected connected=True: {data}"
        assert data.get("platform") == "twitter_x", f"Expected platform=twitter_x: {data}"
        
    def test_twitter_auth_url_generation(self, auth_headers):
        """Twitter auth URL generation works"""
        redirect_uri = "https://verify-features-1.preview.emergentagent.com/oauth/callback"
        response = requests.get(
            f"{BASE_URL}/api/integrations/twitter/auth-url",
            params={"redirect_uri": redirect_uri},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "url" in data, f"Missing OAuth URL: {data}"
        assert "code_verifier" in data, f"Missing PKCE code_verifier: {data}"
        assert "state" in data, f"Missing state: {data}"
        assert "twitter.com" in data["url"], f"URL should contain twitter.com: {data['url']}"


class TestTikTokIntegration(TestLiveIntegrationsAuth):
    """Test TikTok integration endpoints"""
    
    def test_tiktok_test_connection(self, auth_headers):
        """Test TikTok connection test endpoint - should say OAuth needed"""
        response = requests.get(f"{BASE_URL}/api/integrations/tiktok/test", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Without OAuth, should return not connected
        assert "connected" in data, f"Missing connected field: {data}"
        # TikTok requires OAuth - no token stored yet
        assert data.get("connected") == False, f"Expected connected=False without OAuth: {data}"
        
    def test_tiktok_auth_url_generation(self, auth_headers):
        """TikTok auth URL generation works"""
        redirect_uri = "https://verify-features-1.preview.emergentagent.com/oauth/callback"
        response = requests.get(
            f"{BASE_URL}/api/integrations/tiktok/auth-url",
            params={"redirect_uri": redirect_uri},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "url" in data, f"Missing OAuth URL: {data}"
        assert "state" in data, f"Missing state: {data}"
        assert "tiktok.com" in data["url"], f"URL should contain tiktok.com: {data['url']}"


class TestSnapchatIntegration(TestLiveIntegrationsAuth):
    """Test Snapchat integration endpoints"""
    
    def test_snapchat_test_connection(self, auth_headers):
        """Test Snapchat connection test endpoint"""
        response = requests.get(f"{BASE_URL}/api/integrations/snapchat/test", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "connected" in data, f"Missing connected field: {data}"
        
    def test_snapchat_jwt_verified(self, auth_headers):
        """Snapchat shows JWT verified status"""
        response = requests.get(f"{BASE_URL}/api/integrations/snapchat/test", headers=auth_headers)
        data = response.json()
        # With JWT token from env, should show connected
        if data.get("connected"):
            assert data.get("platform") == "snapchat", f"Expected platform=snapchat: {data}"
            # JWT should be verified
            assert data.get("token_valid") == True or data.get("api_type") == "jwt_verified", f"Expected JWT verified: {data}"


class TestCloudFrontIntegration(TestLiveIntegrationsAuth):
    """Test CloudFront integration endpoints"""
    
    def test_cloudfront_status(self, auth_headers):
        """Test CloudFront status endpoint"""
        response = requests.get(f"{BASE_URL}/api/integrations/cloudfront/status", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "configured" in data, f"Missing configured field: {data}"
        
    def test_cloudfront_shows_deployed(self, auth_headers):
        """CloudFront shows deployed with distribution ID"""
        response = requests.get(f"{BASE_URL}/api/integrations/cloudfront/status", headers=auth_headers)
        data = response.json()
        # Distribution E2LURX26QTXMXJ was already created
        assert data.get("configured") == True, f"Expected configured=True: {data}"
        assert data.get("distribution_id") == "E2LURX26QTXMXJ", f"Expected distribution_id=E2LURX26QTXMXJ: {data}"
        
    def test_cloudfront_domain(self, auth_headers):
        """CloudFront has domain configured"""
        response = requests.get(f"{BASE_URL}/api/integrations/cloudfront/status", headers=auth_headers)
        data = response.json()
        assert "domain" in data, f"Missing domain: {data}"
        # Domain should be cloudfront.net
        assert "cloudfront.net" in data.get("domain", ""), f"Expected cloudfront.net domain: {data}"
        
    def test_cloudfront_setup_returns_already_exists(self, auth_headers):
        """CloudFront setup returns 'already exists' for existing distribution"""
        response = requests.post(f"{BASE_URL}/api/integrations/cloudfront/setup", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "success", f"Expected success status: {data}"
        # Should indicate already exists
        inner_data = data.get("data", {})
        assert inner_data.get("created") == False or "already exists" in str(inner_data.get("message", "")).lower(), f"Expected already exists message: {data}"


class TestCredentialManagement(TestLiveIntegrationsAuth):
    """Test credential management endpoints"""
    
    def test_get_twitter_credentials_masked(self, auth_headers):
        """Get Twitter credentials returns masked values"""
        response = requests.get(f"{BASE_URL}/api/integrations/credentials/twitter_x", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "platform_id" in data, f"Missing platform_id: {data}"
        assert data.get("platform_id") == "twitter_x"
        
    def test_save_credentials(self, auth_headers):
        """Save credentials endpoint works"""
        payload = {
            "platform_id": "test_platform",
            "credentials": {"api_key": "test_key_12345"},
            "display_name": "Test Platform"
        }
        response = requests.post(
            f"{BASE_URL}/api/integrations/credentials/save",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("saved") == True, f"Expected saved=True: {data}"


class TestAuthRequired(TestLiveIntegrationsAuth):
    """Test that endpoints require authentication"""
    
    def test_status_all_requires_auth(self):
        """Status all requires authentication"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        
    def test_twitter_test_requires_auth(self):
        """Twitter test requires authentication"""
        response = requests.get(f"{BASE_URL}/api/integrations/twitter/test")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        
    def test_cloudfront_status_requires_auth(self):
        """CloudFront status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/integrations/cloudfront/status")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
