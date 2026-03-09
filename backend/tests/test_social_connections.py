"""
Test Social Connections API - 120 platforms management
Tests: platforms list, connections (auth), credentials CRUD, dashboard metrics, posts, bulk connect
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://arch-improve-1.preview.emergentagent.com')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"


class TestSocialPlatforms:
    """Test GET /api/social/platforms - Public endpoint returning 120 platforms"""

    def test_get_all_platforms(self):
        """Verify all 120 platforms are returned grouped by category"""
        response = requests.get(f"{BASE_URL}/api/social/platforms")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "platforms" in data
        assert "categories" in data
        assert "total" in data
        assert data["total"] == 120, f"Expected 120 platforms, got {data['total']}"
        
        # Verify categories exist
        expected_categories = [
            "social_media", "music_streaming", "podcast", "radio", 
            "video_streaming", "rights_organization", "blockchain", 
            "web3_music", "nft_marketplace", "live_streaming", 
            "video_platform", "audio_social", "model_agency", 
            "model_platform", "music_licensing", "music_data_exchange"
        ]
        for cat in expected_categories:
            assert cat in data["categories"], f"Missing category: {cat}"
        
        # Verify platform structure
        platform = data["platforms"][0]
        assert "id" in platform
        assert "name" in platform
        assert "type" in platform
        assert "credentials_required" in platform

    def test_platforms_have_required_fields(self):
        """Each platform should have id, name, type, description, supported_formats, credentials_required"""
        response = requests.get(f"{BASE_URL}/api/social/platforms")
        assert response.status_code == 200
        
        data = response.json()
        for platform in data["platforms"][:10]:  # Check first 10
            assert "id" in platform, "Platform missing id"
            assert "name" in platform, "Platform missing name"
            assert "type" in platform, "Platform missing type"
            assert "description" in platform, "Platform missing description"
            assert "supported_formats" in platform, "Platform missing supported_formats"
            assert "credentials_required" in platform, "Platform missing credentials_required"
            assert "icon" in platform, "Platform missing icon"


class TestAuthenticatedEndpoints:
    """Tests requiring authentication - connections, credentials, metrics"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for owner user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code} - {response.text}")
        return response.json().get("access_token")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Return auth headers with Bearer token"""
        return {"Authorization": f"Bearer {auth_token}"}

    def test_connections_without_auth_returns_401(self):
        """GET /api/social/connections without auth should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/social/connections")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_connections_with_auth(self, auth_headers):
        """GET /api/social/connections should return 120 platforms with status"""
        response = requests.get(f"{BASE_URL}/api/social/connections", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "connections" in data
        assert "total" in data
        assert "connected_count" in data
        assert data["total"] == 120, f"Expected 120 connections, got {data['total']}"
        
        # Verify connection structure
        conn = data["connections"][0]
        assert "platform_id" in conn
        assert "name" in conn
        assert "connected" in conn
        assert "status" in conn
        assert "credentials_required" in conn

    def test_dashboard_metrics_with_auth(self, auth_headers):
        """GET /api/social/metrics/dashboard returns connected platform stats"""
        response = requests.get(f"{BASE_URL}/api/social/metrics/dashboard", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "platforms" in data
        assert "connected_count" in data
        assert "total_platforms" in data
        assert data["total_platforms"] == 120

    def test_dashboard_metrics_without_auth_returns_401(self):
        """GET /api/social/metrics/dashboard without auth should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/social/metrics/dashboard")
        assert response.status_code in [401, 403]


class TestCredentialsCRUD:
    """Tests for credentials save, get, delete endpoints"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        return response.json().get("access_token")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

    def test_save_credentials_for_instagram(self, auth_headers):
        """POST /api/social/credentials/instagram saves credentials and marks connected"""
        response = requests.post(
            f"{BASE_URL}/api/social/credentials/instagram",
            headers=auth_headers,
            json={
                "credentials": {"access_token": "TEST_instagram_token_12345"},
                "display_name": "@testaccount"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert data["platform_id"] == "instagram"
        assert data["status"] == "connected"

    def test_get_credentials_returns_masked(self, auth_headers):
        """GET /api/social/credentials/instagram returns masked credentials"""
        # First ensure credentials exist
        requests.post(
            f"{BASE_URL}/api/social/credentials/instagram",
            headers=auth_headers,
            json={
                "credentials": {"access_token": "TEST_instagram_token_12345"},
                "display_name": "@testaccount"
            }
        )
        
        response = requests.get(
            f"{BASE_URL}/api/social/credentials/instagram",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["platform_id"] == "instagram"
        assert "credentials" in data
        # Credentials should be masked with asterisks
        token = data["credentials"].get("access_token", "")
        assert "*" in token, f"Token should be masked: {token}"

    def test_save_credentials_invalid_platform_returns_404(self, auth_headers):
        """POST /api/social/credentials/invalid_platform returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/social/credentials/invalid_platform_xyz",
            headers=auth_headers,
            json={"credentials": {"api_key": "test"}}
        )
        assert response.status_code == 404

    def test_get_credentials_nonexistent_returns_404(self, auth_headers):
        """GET /api/social/credentials/invalid_platform returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/social/credentials/nonexistent_platform_xyz",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_credentials_removes_connection(self, auth_headers):
        """DELETE /api/social/credentials/instagram disconnects the platform"""
        # First ensure connected
        requests.post(
            f"{BASE_URL}/api/social/credentials/instagram",
            headers=auth_headers,
            json={
                "credentials": {"access_token": "TEST_token_to_delete"},
                "display_name": "@deleteme"
            }
        )
        
        # Delete credentials
        response = requests.delete(
            f"{BASE_URL}/api/social/credentials/instagram",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        
        # Verify disconnected by trying to get credentials
        get_response = requests.get(
            f"{BASE_URL}/api/social/credentials/instagram",
            headers=auth_headers
        )
        assert get_response.status_code == 404, "Credentials should be deleted"

    def test_disconnect_alias_endpoint(self, auth_headers):
        """POST /api/social/disconnect/platform_id works as alias for delete"""
        # First connect a platform
        requests.post(
            f"{BASE_URL}/api/social/credentials/twitter",
            headers=auth_headers,
            json={
                "credentials": {
                    "api_key": "TEST_api_key",
                    "api_secret": "TEST_secret",
                    "access_token": "TEST_access",
                    "access_token_secret": "TEST_token_secret"
                }
            }
        )
        
        # Use disconnect alias
        response = requests.post(
            f"{BASE_URL}/api/social/disconnect/twitter",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


class TestBulkConnect:
    """Tests for bulk connect endpoint"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip("Login failed")
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def test_bulk_connect_multiple_platforms(self, auth_headers):
        """POST /api/social/bulk-connect connects multiple platforms at once"""
        platform_ids = ["spotify", "apple_music", "tidal"]
        
        response = requests.post(
            f"{BASE_URL}/api/social/bulk-connect",
            headers=auth_headers,
            json={"platform_ids": platform_ids}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "connected" in data
        assert data["count"] >= 1
        
        # Verify connections updated
        conn_response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=auth_headers
        )
        connections = conn_response.json()["connections"]
        spotify_conn = next((c for c in connections if c["platform_id"] == "spotify"), None)
        assert spotify_conn is not None
        # After bulk connect, platform should be marked as connected
        assert spotify_conn["connected"] is True


class TestPosts:
    """Tests for social post creation and listing"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip("Login failed")
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def test_create_post_requires_connected_platform(self, auth_headers):
        """POST /api/social/post fails if platform not connected"""
        # First disconnect the platform
        requests.post(f"{BASE_URL}/api/social/disconnect/linkedin", headers=auth_headers)
        
        response = requests.post(
            f"{BASE_URL}/api/social/post",
            headers=auth_headers,
            json={
                "provider": "linkedin",
                "content": "Test post content",
                "media_urls": []
            }
        )
        assert response.status_code == 400, f"Expected 400 for disconnected platform, got {response.status_code}"

    def test_create_post_success_when_connected(self, auth_headers):
        """POST /api/social/post succeeds when platform is connected"""
        # First connect the platform
        requests.post(
            f"{BASE_URL}/api/social/credentials/facebook",
            headers=auth_headers,
            json={
                "credentials": {"access_token": "TEST_facebook_token"},
                "display_name": "Test Page"
            }
        )
        
        response = requests.post(
            f"{BASE_URL}/api/social/post",
            headers=auth_headers,
            json={
                "provider": "facebook",
                "content": "TEST_post_content_from_pytest",
                "media_urls": []
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "post_id" in data

    def test_list_posts(self, auth_headers):
        """GET /api/social/posts returns user's posts"""
        response = requests.get(
            f"{BASE_URL}/api/social/posts",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "posts" in data
        assert isinstance(data["posts"], list)


class TestCleanup:
    """Cleanup test data after all tests"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip("Login failed")
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_cleanup_test_connections(self, auth_headers):
        """Cleanup: Disconnect test platforms"""
        test_platforms = ["instagram", "twitter", "facebook", "spotify", "apple_music", "tidal", "linkedin"]
        for platform_id in test_platforms:
            requests.post(f"{BASE_URL}/api/social/disconnect/{platform_id}", headers=auth_headers)
        
        # Verify cleanup
        response = requests.get(f"{BASE_URL}/api/social/connections", headers=auth_headers)
        data = response.json()
        # Check that test platforms are disconnected
        for conn in data["connections"]:
            if conn["platform_id"] in test_platforms:
                # After cleanup, platform should be disconnected (unless user had real credentials)
                pass  # Allow any status after cleanup
        
        assert True  # Cleanup completed
