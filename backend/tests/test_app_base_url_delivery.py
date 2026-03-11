"""
Backend tests for APP_BASE_URL delivery feature.
Tests that the app's own URL is used correctly for content delivery in Distribution Hub.
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
EXPECTED_APP_BASE_URL = "https://creator-hub-700.preview.emergentagent.com"

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    if response.status_code != 200:
        pytest.skip("Authentication failed - skipping authenticated tests")
    return response.json().get("access_token")


@pytest.fixture
def api_client(auth_token):
    """Authenticated session for API calls"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


class TestAdaptersEndpoint:
    """Tests for GET /api/distribution-hub/adapters endpoint"""
    
    def test_adapters_returns_app_base_url(self):
        """Verify /adapters returns app_base_url with correct value"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "app_base_url" in data, "Response must include app_base_url field"
        assert data["app_base_url"] == EXPECTED_APP_BASE_URL, \
            f"Expected app_base_url to be {EXPECTED_APP_BASE_URL}, got {data['app_base_url']}"
    
    def test_adapters_returns_all_10_platforms(self):
        """Verify /adapters returns all 10 live platform adapters"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters")
        assert response.status_code == 200
        
        data = response.json()
        expected_adapters = ["youtube", "twitter_x", "tiktok", "soundcloud", "vimeo", 
                           "bluesky", "discord", "telegram", "instagram", "facebook"]
        
        assert "adapters" in data, "Response must include adapters list"
        assert data["total"] == 10, f"Expected 10 adapters, got {data['total']}"
        
        for adapter in expected_adapters:
            assert adapter in data["adapters"], f"Expected adapter '{adapter}' not found"
    
    def test_adapters_includes_helpful_message(self):
        """Verify /adapters includes message about content served from app URL"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data, "Response must include message field"
        assert "app URL" in data["message"] or "Content is served" in data["message"], \
            "Message should mention content served from app URL"


class TestDistributionDeliverySourceUrl:
    """Tests for POST /api/distribution-hub/distribute - source_url field"""
    
    def test_distribution_creates_deliveries_with_app_base_url(self, api_client):
        """Verify distribute endpoint creates deliveries with correct source_url"""
        # Create test content
        content_data = {
            "title": f"TEST_URL_VERIFY_{uuid.uuid4().hex[:8]}",
            "content_type": "audio",
            "description": "Test content for APP_BASE_URL verification",
            "artist": "Test Artist",
            "genre": "Hip-Hop",
            "file_url": "/api/distribution-hub/files/test-track.mp3"
        }
        
        content_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        assert content_resp.status_code == 200, f"Content creation failed: {content_resp.text}"
        content_id = content_resp.json()["content"]["id"]
        
        # Distribute to 2 platforms
        dist_data = {
            "content_id": content_id,
            "platform_ids": ["youtube", "discord"]
        }
        dist_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/distribute", json=dist_data)
        assert dist_resp.status_code == 200, f"Distribution failed: {dist_resp.text}"
        
        data = dist_resp.json()
        assert "deliveries" in data, "Response must include deliveries list"
        assert len(data["deliveries"]) == 2, f"Expected 2 deliveries, got {len(data['deliveries'])}"
        
        # Verify source_url in each delivery
        for delivery in data["deliveries"]:
            assert "source_url" in delivery, "Each delivery must have source_url"
            assert delivery["source_url"] == EXPECTED_APP_BASE_URL, \
                f"Expected source_url to be {EXPECTED_APP_BASE_URL}, got {delivery['source_url']}"
        
        # Cleanup - delete test content
        api_client.delete(f"{BASE_URL}/api/distribution-hub/content/{content_id}")
    
    def test_distribution_response_includes_live_adapters(self, api_client):
        """Verify distribute response includes list of live adapters"""
        # Create minimal test content
        content_data = {
            "title": f"TEST_ADAPTERS_LIST_{uuid.uuid4().hex[:8]}",
            "content_type": "video",
            "description": "Test for live adapters list"
        }
        
        content_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        assert content_resp.status_code == 200
        content_id = content_resp.json()["content"]["id"]
        
        # Distribute to 1 platform
        dist_data = {
            "content_id": content_id,
            "platform_ids": ["tiktok"]
        }
        dist_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/distribute", json=dist_data)
        assert dist_resp.status_code == 200
        
        data = dist_resp.json()
        assert "live_adapters" in data, "Response must include live_adapters list"
        assert len(data["live_adapters"]) == 10, f"Expected 10 live adapters, got {len(data['live_adapters'])}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/distribution-hub/content/{content_id}")


class TestBatchProgress:
    """Tests for GET /api/distribution-hub/deliveries/batch/{batch_id}/progress"""
    
    def test_batch_progress_returns_correct_structure(self, api_client):
        """Verify batch progress endpoint returns expected fields"""
        # Create content and distribute
        content_data = {
            "title": f"TEST_BATCH_PROGRESS_{uuid.uuid4().hex[:8]}",
            "content_type": "audio",
            "description": "Test for batch progress"
        }
        
        content_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        assert content_resp.status_code == 200
        content_id = content_resp.json()["content"]["id"]
        
        dist_data = {
            "content_id": content_id,
            "platform_ids": ["youtube", "twitter_x", "discord"]
        }
        dist_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/distribute", json=dist_data)
        assert dist_resp.status_code == 200
        batch_id = dist_resp.json()["batch_id"]
        
        # Check batch progress
        progress_resp = api_client.get(f"{BASE_URL}/api/distribution-hub/deliveries/batch/{batch_id}/progress")
        assert progress_resp.status_code == 200
        
        data = progress_resp.json()
        expected_fields = ["total", "delivered", "failed", "delivering", "queued", 
                         "preparing", "export_ready", "progress_pct", "is_complete"]
        
        for field in expected_fields:
            assert field in data, f"Expected field '{field}' in progress response"
        
        assert data["total"] == 3, f"Expected 3 total deliveries, got {data['total']}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/distribution-hub/content/{content_id}")
    
    def test_nonexistent_batch_returns_empty_progress(self, api_client):
        """Verify nonexistent batch returns zero counts"""
        fake_batch_id = str(uuid.uuid4())
        response = api_client.get(f"{BASE_URL}/api/distribution-hub/deliveries/batch/{fake_batch_id}/progress")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert data["is_complete"] == True


class TestDeliveryHistorySourceUrl:
    """Tests for GET /api/distribution-hub/deliveries - verify source_url in history"""
    
    def test_deliveries_have_source_url(self, api_client):
        """Verify deliveries in history have source_url field"""
        response = api_client.get(f"{BASE_URL}/api/distribution-hub/deliveries?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "deliveries" in data
        
        # If there are deliveries, check they have source_url
        if len(data["deliveries"]) > 0:
            for delivery in data["deliveries"]:
                assert "source_url" in delivery, "Each delivery must have source_url"
                # New deliveries should use APP_BASE_URL
                # Old deliveries might have old URL, so we just verify field exists


class TestPlatformAdaptersUrlResolution:
    """Tests verifying platform adapters correctly use APP_BASE_URL for content"""
    
    def test_adapters_endpoint_has_correct_url(self):
        """Verify the adapters endpoint reflects APP_BASE_URL environment"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters")
        assert response.status_code == 200
        
        data = response.json()
        # The app_base_url should match what's configured in backend/.env
        assert data["app_base_url"] == EXPECTED_APP_BASE_URL


class TestExportPackageSourceUrl:
    """Tests for export package generation"""
    
    def test_export_package_includes_source_url(self, api_client):
        """Verify export package has source_of_truth field with APP_BASE_URL"""
        # Create content and distribute
        content_data = {
            "title": f"TEST_EXPORT_PKG_{uuid.uuid4().hex[:8]}",
            "content_type": "audio",
            "description": "Test for export package source URL",
            "file_url": "/api/distribution-hub/files/test-export.mp3"
        }
        
        content_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        assert content_resp.status_code == 200
        content_id = content_resp.json()["content"]["id"]
        
        # Distribute to export-only platform (spotify uses export_package)
        dist_data = {
            "content_id": content_id,
            "platform_ids": ["spotify"]
        }
        dist_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/distribute", json=dist_data)
        assert dist_resp.status_code == 200
        
        deliveries = dist_resp.json()["deliveries"]
        assert len(deliveries) == 1
        delivery_id = deliveries[0]["id"]
        
        # Generate export package
        export_resp = api_client.post(f"{BASE_URL}/api/distribution-hub/deliveries/{delivery_id}/export")
        assert export_resp.status_code == 200
        
        data = export_resp.json()
        assert "package" in data
        pkg = data["package"]
        
        assert "source_of_truth" in pkg, "Export package must have source_of_truth"
        assert pkg["source_of_truth"] == EXPECTED_APP_BASE_URL, \
            f"Expected source_of_truth to be {EXPECTED_APP_BASE_URL}, got {pkg['source_of_truth']}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/distribution-hub/content/{content_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
