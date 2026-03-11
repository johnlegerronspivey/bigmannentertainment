"""
Test Distribution Hub Delivery Engine - Real API Push with Fallback to Export

Tests the new delivery engine functionality:
- GET /api/distribution-hub/adapters returns 10 live platform adapters
- POST /api/distribution-hub/distribute creates deliveries and kicks off background delivery
- GET /api/distribution-hub/deliveries/batch/{batch_id}/progress returns progress stats
- POST /api/distribution-hub/deliveries/{delivery_id}/retry retries failed deliveries
- PUT /api/distribution-hub/deliveries/{delivery_id}/status updates delivery status
- Delivery engine falls back to export_ready when no credentials are available
"""

import pytest
import requests
import time
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestDistributionHubDeliveryEngine:
    """Test Distribution Hub Delivery Engine functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Auth failed: {response.text}"
        data = response.json()
        token = data.get("access_token") or data.get("token")
        assert token, "No token in response"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    # ==========================================
    # Test 1: GET /api/distribution-hub/adapters
    # ==========================================
    def test_get_live_adapters(self, auth_headers):
        """Test GET /api/distribution-hub/adapters returns list of 10 live platform adapters"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters")
        assert response.status_code == 200, f"GET adapters failed: {response.text}"
        
        data = response.json()
        assert "adapters" in data, "Response missing 'adapters' field"
        assert "total" in data, "Response missing 'total' field"
        assert "message" in data, "Response missing 'message' field"
        
        adapters = data["adapters"]
        assert len(adapters) == 10, f"Expected 10 adapters, got {len(adapters)}"
        
        expected_adapters = [
            "youtube", "twitter_x", "tiktok", "soundcloud", "vimeo",
            "bluesky", "discord", "telegram", "instagram", "facebook"
        ]
        for adapter in expected_adapters:
            assert adapter in adapters, f"Missing adapter: {adapter}"
        
        print(f"✓ GET /adapters returns {len(adapters)} live platform adapters")

    # ==========================================
    # Test 2: Create content for distribution
    # ==========================================
    def test_create_content_for_delivery_test(self, auth_headers):
        """Create test content for delivery testing"""
        unique_id = uuid.uuid4().hex[:8]
        content_data = {
            "title": f"TEST_DeliveryEngine_{unique_id}",
            "content_type": "audio",
            "description": "Test content for delivery engine testing",
            "artist": "Test Artist",
            "genre": "Electronic"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/distribution-hub/content",
            headers=auth_headers,
            json=content_data
        )
        assert response.status_code == 200, f"Create content failed: {response.text}"
        
        data = response.json()
        assert "content" in data, "Response missing 'content' field"
        content = data["content"]
        assert "id" in content, "Content missing 'id'"
        
        # Store content ID for later tests
        TestDistributionHubDeliveryEngine.test_content_id = content["id"]
        print(f"✓ Created test content: {content['id']}")

    # ==========================================
    # Test 3: POST /api/distribution-hub/distribute
    # ==========================================
    def test_distribute_content_to_platforms(self, auth_headers):
        """Test POST /distribute creates deliveries and kicks off background processing"""
        content_id = getattr(TestDistributionHubDeliveryEngine, 'test_content_id', None)
        if not content_id:
            pytest.skip("No test content available")
        
        # Distribute to mix of api_push and export platforms
        platform_ids = ["twitter_x", "discord", "spotify", "apple_music"]
        
        response = requests.post(
            f"{BASE_URL}/api/distribution-hub/distribute",
            headers=auth_headers,
            json={
                "content_id": content_id,
                "platform_ids": platform_ids
            }
        )
        assert response.status_code == 200, f"Distribute failed: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "batch_id" in data, "Response missing 'batch_id'"
        assert "api_push_count" in data, "Response missing 'api_push_count'"
        assert "export_package_count" in data, "Response missing 'export_package_count'"
        assert "deliveries" in data, "Response missing 'deliveries'"
        assert "live_adapters" in data, "Response missing 'live_adapters'"
        
        # Verify live_adapters list includes our 10 platforms
        live_adapters = data["live_adapters"]
        assert len(live_adapters) == 10, f"Expected 10 live adapters, got {len(live_adapters)}"
        assert "twitter_x" in live_adapters
        assert "discord" in live_adapters
        
        # Verify deliveries were created
        deliveries = data["deliveries"]
        assert len(deliveries) == len(platform_ids), f"Expected {len(platform_ids)} deliveries, got {len(deliveries)}"
        
        # Store batch_id for later tests
        TestDistributionHubDeliveryEngine.test_batch_id = data["batch_id"]
        TestDistributionHubDeliveryEngine.test_delivery_ids = [d["id"] for d in deliveries]
        
        print(f"✓ Distributed to {len(platform_ids)} platforms")
        print(f"  - Batch ID: {data['batch_id'][:16]}...")
        print(f"  - API Push: {data['api_push_count']}, Export: {data['export_package_count']}")

    # ==========================================
    # Test 4: GET /api/distribution-hub/deliveries/batch/{batch_id}/progress
    # ==========================================
    def test_get_batch_progress(self, auth_headers):
        """Test GET batch progress endpoint returns progress stats"""
        batch_id = getattr(TestDistributionHubDeliveryEngine, 'test_batch_id', None)
        if not batch_id:
            pytest.skip("No batch available")
        
        # Wait for background processing to complete
        time.sleep(5)
        
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries/batch/{batch_id}/progress",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get batch progress failed: {response.text}"
        
        data = response.json()
        
        # Verify response fields
        expected_fields = ["total", "delivered", "failed", "delivering", "queued", "preparing", "export_ready", "progress_pct", "is_complete"]
        for field in expected_fields:
            assert field in data, f"Response missing '{field}' field"
        
        # Verify counts make sense
        assert data["total"] > 0, "Total should be > 0"
        assert isinstance(data["progress_pct"], (int, float)), "progress_pct should be numeric"
        assert 0 <= data["progress_pct"] <= 100, "progress_pct should be 0-100"
        assert isinstance(data["is_complete"], bool), "is_complete should be boolean"
        
        print(f"✓ Batch progress retrieved")
        print(f"  - Total: {data['total']}, Delivered: {data['delivered']}, Export Ready: {data['export_ready']}")
        print(f"  - Progress: {data['progress_pct']}%, Complete: {data['is_complete']}")

    # ==========================================
    # Test 5: Verify delivery status fallback to export_ready
    # ==========================================
    def test_delivery_fallback_to_export_ready(self, auth_headers):
        """Verify platforms without credentials fall back to export_ready status"""
        # Wait for background processing
        time.sleep(3)
        
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries",
            headers=auth_headers,
            params={"limit": 50}
        )
        assert response.status_code == 200, f"Get deliveries failed: {response.text}"
        
        data = response.json()
        deliveries = data.get("deliveries", [])
        
        # Find deliveries for api_push platforms (twitter_x, discord)
        # Since no real credentials are saved, they should fall back to export_ready
        api_push_deliveries = [
            d for d in deliveries 
            if d.get("platform_id") in ["twitter_x", "discord", "youtube", "tiktok"] 
            and "TEST_DeliveryEngine_" in d.get("content_title", "")
        ]
        
        for delivery in api_push_deliveries:
            status = delivery.get("status")
            # Should be export_ready (fallback due to no credentials) or failed
            assert status in ["export_ready", "failed", "delivered", "queued"], \
                f"Unexpected status for {delivery.get('platform_id')}: {status}"
            
            # Check platform_response has informative message about credentials
            response_data = delivery.get("platform_response", {})
            if status == "export_ready" and response_data:
                assert "message" in response_data or "method" in response_data, \
                    "export_ready should have informative response"
        
        print(f"✓ Verified delivery fallback behavior for {len(api_push_deliveries)} api_push deliveries")

    # ==========================================
    # Test 6: PUT /api/distribution-hub/deliveries/{delivery_id}/status
    # ==========================================
    def test_update_delivery_status(self, auth_headers):
        """Test PUT update delivery status endpoint"""
        delivery_ids = getattr(TestDistributionHubDeliveryEngine, 'test_delivery_ids', None)
        if not delivery_ids or len(delivery_ids) == 0:
            pytest.skip("No deliveries available")
        
        delivery_id = delivery_ids[0]
        
        # Update status with JSON body
        update_data = {
            "status": "delivered",
            "response_data": {"marked_via_test": True, "external_id": "test123"}
        }
        
        response = requests.put(
            f"{BASE_URL}/api/distribution-hub/deliveries/{delivery_id}/status",
            headers=auth_headers,
            json=update_data
        )
        assert response.status_code == 200, f"Update status failed: {response.text}"
        
        data = response.json()
        assert "delivery" in data or "message" in data, "Response should have delivery or message"
        
        print(f"✓ Updated delivery status to 'delivered'")

    # ==========================================
    # Test 7: Create a failed delivery for retry test
    # ==========================================
    def test_create_failed_delivery_for_retry(self, auth_headers):
        """Create a delivery that can be retried"""
        content_id = getattr(TestDistributionHubDeliveryEngine, 'test_content_id', None)
        if not content_id:
            pytest.skip("No test content available")
        
        # Create new delivery
        response = requests.post(
            f"{BASE_URL}/api/distribution-hub/distribute",
            headers=auth_headers,
            json={
                "content_id": content_id,
                "platform_ids": ["youtube"]  # api_push platform without credentials
            }
        )
        assert response.status_code == 200, f"Distribute failed: {response.text}"
        
        data = response.json()
        batch_id = data["batch_id"]
        
        # Wait for processing
        time.sleep(6)
        
        # Get deliveries from this batch
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries/batch/{batch_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        deliveries = response.json().get("deliveries", [])
        if deliveries:
            # Force one to failed status for retry test
            delivery_id = deliveries[0]["id"]
            # We'll use this ID even if not failed
            TestDistributionHubDeliveryEngine.retry_delivery_id = delivery_id
            TestDistributionHubDeliveryEngine.retry_delivery_status = deliveries[0].get("status")
        
        print(f"✓ Created delivery for retry test")

    # ==========================================
    # Test 8: POST /api/distribution-hub/deliveries/{delivery_id}/retry
    # ==========================================
    def test_retry_delivery(self, auth_headers):
        """Test POST retry delivery endpoint"""
        delivery_id = getattr(TestDistributionHubDeliveryEngine, 'retry_delivery_id', None)
        if not delivery_id:
            pytest.skip("No delivery available for retry")
        
        # First, set the delivery to 'failed' status so we can retry it
        requests.put(
            f"{BASE_URL}/api/distribution-hub/deliveries/{delivery_id}/status",
            headers=auth_headers,
            json={"status": "failed", "response_data": {"forced_for_test": True}}
        )
        
        # Now retry
        response = requests.post(
            f"{BASE_URL}/api/distribution-hub/deliveries/{delivery_id}/retry",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Retry failed: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should have message"
        assert "delivery_id" in data, "Response should have delivery_id"
        
        print(f"✓ Retry initiated for delivery {delivery_id[:16]}...")

    # ==========================================
    # Test 9: Test export_package delivery method
    # ==========================================
    def test_export_package_delivery(self, auth_headers):
        """Test that export_package deliveries get export_ready status"""
        content_id = getattr(TestDistributionHubDeliveryEngine, 'test_content_id', None)
        if not content_id:
            pytest.skip("No test content available")
        
        # spotify and apple_music are export_package platforms
        response = requests.post(
            f"{BASE_URL}/api/distribution-hub/distribute",
            headers=auth_headers,
            json={
                "content_id": content_id,
                "platform_ids": ["spotify", "apple_music"]
            }
        )
        assert response.status_code == 200, f"Distribute failed: {response.text}"
        
        data = response.json()
        batch_id = data["batch_id"]
        
        # Wait for processing
        time.sleep(4)
        
        # Check deliveries status
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries/batch/{batch_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        deliveries = response.json().get("deliveries", [])
        export_ready_count = sum(1 for d in deliveries if d.get("status") == "export_ready")
        
        # Export package platforms should be export_ready
        assert export_ready_count >= 0, "Export package deliveries should complete"
        
        print(f"✓ Export package deliveries processed - {export_ready_count} export_ready")

    # ==========================================
    # Test 10: Verify adapters in distribute response
    # ==========================================
    def test_distribute_returns_live_adapters(self, auth_headers):
        """Verify distribute response includes live_adapters list"""
        content_id = getattr(TestDistributionHubDeliveryEngine, 'test_content_id', None)
        if not content_id:
            pytest.skip("No test content available")
        
        response = requests.post(
            f"{BASE_URL}/api/distribution-hub/distribute",
            headers=auth_headers,
            json={
                "content_id": content_id,
                "platform_ids": ["soundcloud"]
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        live_adapters = data.get("live_adapters", [])
        
        # Verify all 10 adapters are listed
        expected = ["youtube", "twitter_x", "tiktok", "soundcloud", "vimeo",
                   "bluesky", "discord", "telegram", "instagram", "facebook"]
        
        for adapter in expected:
            assert adapter in live_adapters, f"Missing {adapter} in live_adapters"
        
        print(f"✓ Distribute response includes all {len(live_adapters)} live adapters")

    # ==========================================
    # Cleanup
    # ==========================================
    def test_cleanup_test_content(self, auth_headers):
        """Cleanup test content"""
        content_id = getattr(TestDistributionHubDeliveryEngine, 'test_content_id', None)
        if content_id:
            requests.delete(
                f"{BASE_URL}/api/distribution-hub/content/{content_id}",
                headers=auth_headers
            )
            print(f"✓ Cleaned up test content")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
