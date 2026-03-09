"""
Test Social Media Metrics Analytics API - Real-time metrics display
Tests: GET /api/social/metrics/dashboard, GET /api/social/metrics/platforms, POST /api/social/metrics/refresh
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"


class TestDashboardMetrics:
    """Tests for GET /api/social/metrics/dashboard - Aggregate metrics"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_dashboard_metrics_returns_aggregate_data(self, auth_headers):
        """GET /api/social/metrics/dashboard returns all aggregate metrics"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify all required aggregate fields exist
        required_fields = [
            "total_followers", "total_likes", "total_comments", 
            "total_shares", "total_impressions", "total_reach",
            "avg_engagement", "connected_count", "total_platforms"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify values are numeric and reasonable
        assert isinstance(data["total_followers"], int), "total_followers should be int"
        assert isinstance(data["total_likes"], int), "total_likes should be int"
        assert isinstance(data["avg_engagement"], (int, float)), "avg_engagement should be numeric"
        assert data["total_platforms"] == 120, f"Expected 120 platforms, got {data['total_platforms']}"

    def test_dashboard_metrics_has_platforms_array(self, auth_headers):
        """GET /api/social/metrics/dashboard includes platforms array with metrics"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "platforms" in data, "Response should include platforms array"
        assert isinstance(data["platforms"], list), "platforms should be a list"
        
        # Verify platform structure if platforms exist
        if len(data["platforms"]) > 0:
            platform = data["platforms"][0]
            platform_fields = ["platform", "name", "type", "followers", "engagement_rate", "growth_rate"]
            for field in platform_fields:
                assert field in platform, f"Platform missing field: {field}"

    def test_dashboard_metrics_without_auth_returns_401(self):
        """GET /api/social/metrics/dashboard without auth should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/social/metrics/dashboard")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestPlatformMetrics:
    """Tests for GET /api/social/metrics/platforms - Per-platform metrics with categories"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_platform_metrics_returns_categories_breakdown(self, auth_headers):
        """GET /api/social/metrics/platforms returns category summaries"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "categories" in data, "Response should include categories"
        assert isinstance(data["categories"], list), "categories should be a list"
        
        # Verify category structure
        if len(data["categories"]) > 0:
            cat = data["categories"][0]
            cat_fields = ["type", "label", "platform_count", "total_followers", "avg_engagement", "avg_growth"]
            for field in cat_fields:
                assert field in cat, f"Category missing field: {field}"

    def test_platform_metrics_returns_per_platform_data(self, auth_headers):
        """GET /api/social/metrics/platforms returns detailed per-platform metrics"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "platforms" in data, "Response should include platforms"
        assert "total_connected" in data, "Response should include total_connected"
        
        # Verify platform has trend data (daily_followers, daily_engagement)
        if len(data["platforms"]) > 0:
            platform = data["platforms"][0]
            assert "daily_followers" in platform, "Platform should have daily_followers for sparkline"
            assert "daily_engagement" in platform, "Platform should have daily_engagement"
            assert isinstance(platform["daily_followers"], list), "daily_followers should be a list"
            assert len(platform["daily_followers"]) == 7, "daily_followers should have 7 days of data"

    def test_platform_metrics_has_growth_indicators(self, auth_headers):
        """Each platform should have growth_rate for growth indicators"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        if len(data["platforms"]) > 0:
            platform = data["platforms"][0]
            assert "growth_rate" in platform, "Platform should have growth_rate"
            assert isinstance(platform["growth_rate"], (int, float)), "growth_rate should be numeric"
            assert "engagement_rate" in platform, "Platform should have engagement_rate"

    def test_platform_metrics_without_auth_returns_401(self):
        """GET /api/social/metrics/platforms without auth should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/social/metrics/platforms")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestMetricsRefresh:
    """Tests for POST /api/social/metrics/refresh - Refresh all metrics"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_refresh_metrics_returns_success(self, auth_headers):
        """POST /api/social/metrics/refresh refreshes metrics for all connected platforms"""
        response = requests.post(
            f"{BASE_URL}/api/social/metrics/refresh",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True, "refresh should return success: true"
        assert "refreshed_count" in data, "Should include refreshed_count"
        assert "refreshed_at" in data, "Should include refreshed_at timestamp"
        assert isinstance(data["refreshed_count"], int), "refreshed_count should be int"

    def test_refresh_metrics_updates_all_connected(self, auth_headers):
        """POST /api/social/metrics/refresh should refresh all connected platforms"""
        # First get connected count
        dashboard_response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        connected_count = dashboard_response.json().get("connected_count", 0)
        
        # Refresh metrics
        response = requests.post(
            f"{BASE_URL}/api/social/metrics/refresh",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 200
        
        data = response.json()
        # refreshed_count should match connected_count
        assert data["refreshed_count"] == connected_count, f"Expected {connected_count} refreshed, got {data['refreshed_count']}"

    def test_refresh_metrics_without_auth_returns_401(self):
        """POST /api/social/metrics/refresh without auth should return 401/403"""
        response = requests.post(f"{BASE_URL}/api/social/metrics/refresh", json={})
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestMetricsDataIntegrity:
    """Tests to verify metrics data consistency and integrity"""

    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_metrics_are_deterministic(self, auth_headers):
        """Metrics should be deterministic (same values for same user+platform)"""
        # Fetch metrics twice
        response1 = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        response2 = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Aggregate metrics should be the same
        assert data1["total_followers"] == data2["total_followers"], "Followers should be deterministic"
        assert data1["total_likes"] == data2["total_likes"], "Likes should be deterministic"
        assert data1["avg_engagement"] == data2["avg_engagement"], "Engagement should be deterministic"

    def test_category_counts_match_platform_counts(self, auth_headers):
        """Sum of platform_count in categories should equal total platforms"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        total_from_categories = sum(cat["platform_count"] for cat in data["categories"])
        assert total_from_categories == data["total_connected"], \
            f"Category sum {total_from_categories} != total_connected {data['total_connected']}"

    def test_all_16_categories_present(self, auth_headers):
        """All 16 platform categories should be represented"""
        expected_categories = [
            "social_media", "music_streaming", "podcast", "radio",
            "video_streaming", "rights_organization", "blockchain",
            "web3_music", "nft_marketplace", "live_streaming",
            "video_platform", "audio_social", "model_agency",
            "model_platform", "music_licensing", "music_data_exchange"
        ]
        
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        category_types = [cat["type"] for cat in data["categories"]]
        
        for expected_cat in expected_categories:
            assert expected_cat in category_types, f"Missing category: {expected_cat}"
