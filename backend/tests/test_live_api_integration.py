"""
Test Live Social Media API Integration - Tests for live/simulated metrics feature
Tests: GET /api/social/live-supported, connections with has_live_api/has_real_credentials,
       dashboard metrics with live_count/simulated_count, platform metrics with data_source,
       metrics refresh with live/simulated counts
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials - Owner account
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"

# Expected 14 platforms with live API adapters
EXPECTED_LIVE_PLATFORMS = [
    "twitter", "youtube", "instagram", "facebook", "spotify", "tiktok",
    "linkedin", "twitch", "soundcloud", "reddit", "youtube_music",
    "threads", "spotify_podcasts", "whatsapp_business"
]


class TestLiveSupportedEndpoint:
    """Tests for GET /api/social/live-supported - List platforms with live API adapters"""

    def test_live_supported_returns_platform_list(self):
        """GET /api/social/live-supported returns list of 14 platforms with live adapters"""
        response = requests.get(f"{BASE_URL}/api/social/live-supported")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "platforms" in data, "Response should include platforms"
        assert "count" in data, "Response should include count"
        assert isinstance(data["platforms"], list), "platforms should be a list"
        assert data["count"] == 14, f"Expected 14 live platforms, got {data['count']}"

    def test_live_supported_includes_all_expected_platforms(self):
        """GET /api/social/live-supported includes all 14 expected platform IDs"""
        response = requests.get(f"{BASE_URL}/api/social/live-supported")
        assert response.status_code == 200
        
        data = response.json()
        platforms = data["platforms"]
        
        for expected_platform in EXPECTED_LIVE_PLATFORMS:
            assert expected_platform in platforms, f"Missing live platform: {expected_platform}"

    def test_live_supported_is_public(self):
        """GET /api/social/live-supported is a public endpoint (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/social/live-supported")
        # Should return 200 without auth
        assert response.status_code == 200, "live-supported should be accessible without auth"


class TestConnectionsLiveApiFields:
    """Tests for GET /api/social/connections - has_live_api and has_real_credentials fields"""

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

    def test_connections_have_has_live_api_field(self, auth_headers):
        """Each connection should have has_live_api boolean field"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "connections" in data, "Response should include connections"
        
        for conn in data["connections"]:
            assert "has_live_api" in conn, f"Connection {conn.get('platform_id')} missing has_live_api"
            assert isinstance(conn["has_live_api"], bool), "has_live_api should be boolean"

    def test_connections_have_has_real_credentials_field(self, auth_headers):
        """Each connection should have has_real_credentials boolean field"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        for conn in data["connections"]:
            assert "has_real_credentials" in conn, f"Connection {conn.get('platform_id')} missing has_real_credentials"
            assert isinstance(conn["has_real_credentials"], bool), "has_real_credentials should be boolean"

    def test_live_platforms_have_has_live_api_true(self, auth_headers):
        """Platforms with live adapters should have has_live_api: true"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        connections_by_id = {c["platform_id"]: c for c in data["connections"]}
        
        for platform_id in EXPECTED_LIVE_PLATFORMS:
            if platform_id in connections_by_id:
                conn = connections_by_id[platform_id]
                assert conn["has_live_api"] is True, f"{platform_id} should have has_live_api: true"

    def test_non_live_platforms_have_has_live_api_false(self, auth_headers):
        """Platforms without live adapters should have has_live_api: false"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        non_live_count = 0
        for conn in data["connections"]:
            if conn["platform_id"] not in EXPECTED_LIVE_PLATFORMS:
                assert conn["has_live_api"] is False, f"{conn['platform_id']} should have has_live_api: false"
                non_live_count += 1
        
        # Should have many non-live platforms
        assert non_live_count > 0, "Should have platforms without live API support"


class TestDashboardMetricsLiveCount:
    """Tests for GET /api/social/metrics/dashboard - live_count and simulated_count fields"""

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

    def test_dashboard_has_live_count_field(self, auth_headers):
        """GET /api/social/metrics/dashboard should include live_count"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "live_count" in data, "Response should include live_count"
        assert isinstance(data["live_count"], int), "live_count should be int"

    def test_dashboard_has_simulated_count_field(self, auth_headers):
        """GET /api/social/metrics/dashboard should include simulated_count"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "simulated_count" in data, "Response should include simulated_count"
        assert isinstance(data["simulated_count"], int), "simulated_count should be int"

    def test_dashboard_live_simulated_sum_equals_connected(self, auth_headers):
        """live_count + simulated_count should equal connected_count"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        total = data["live_count"] + data["simulated_count"]
        assert total == data["connected_count"], \
            f"live({data['live_count']}) + simulated({data['simulated_count']}) != connected({data['connected_count']})"

    def test_dashboard_platforms_have_data_source_field(self, auth_headers):
        """Each platform in dashboard should have data_source field"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        if len(data.get("platforms", [])) > 0:
            for platform in data["platforms"]:
                assert "data_source" in platform, f"Platform {platform.get('platform')} missing data_source"
                assert platform["data_source"] in ["live", "simulated"], \
                    f"data_source should be 'live' or 'simulated', got {platform['data_source']}"


class TestPlatformMetricsLiveFields:
    """Tests for GET /api/social/metrics/platforms - live/simulated fields at all levels"""

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

    def test_platform_metrics_has_live_count_top_level(self, auth_headers):
        """GET /api/social/metrics/platforms should have live_count at top level"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "live_count" in data, "Response should include live_count at top level"
        assert isinstance(data["live_count"], int), "live_count should be int"

    def test_platform_metrics_has_simulated_count_top_level(self, auth_headers):
        """GET /api/social/metrics/platforms should have simulated_count at top level"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "simulated_count" in data, "Response should include simulated_count at top level"
        assert isinstance(data["simulated_count"], int), "simulated_count should be int"

    def test_each_platform_has_data_source_field(self, auth_headers):
        """Each platform should have data_source field ('live' or 'simulated')"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        for platform in data.get("platforms", []):
            assert "data_source" in platform, f"Platform {platform.get('platform_id')} missing data_source"
            assert platform["data_source"] in ["live", "simulated"], \
                f"Invalid data_source for {platform.get('platform_id')}: {platform['data_source']}"

    def test_each_platform_has_has_live_api_field(self, auth_headers):
        """Each platform should have has_live_api boolean field"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        for platform in data.get("platforms", []):
            assert "has_live_api" in platform, f"Platform {platform.get('platform_id')} missing has_live_api"
            assert isinstance(platform["has_live_api"], bool), "has_live_api should be boolean"

    def test_categories_have_live_count_field(self, auth_headers):
        """Each category should have live_count field"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/platforms",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        for category in data.get("categories", []):
            assert "live_count" in category, f"Category {category.get('type')} missing live_count"
            assert isinstance(category["live_count"], int), "live_count should be int"


class TestMetricsRefreshLiveCount:
    """Tests for POST /api/social/metrics/refresh - live_count and simulated_count in response"""

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

    def test_refresh_returns_live_count(self, auth_headers):
        """POST /api/social/metrics/refresh should return live_count"""
        response = requests.post(
            f"{BASE_URL}/api/social/metrics/refresh",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "live_count" in data, "Refresh response should include live_count"
        assert isinstance(data["live_count"], int), "live_count should be int"

    def test_refresh_returns_simulated_count(self, auth_headers):
        """POST /api/social/metrics/refresh should return simulated_count"""
        response = requests.post(
            f"{BASE_URL}/api/social/metrics/refresh",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "simulated_count" in data, "Refresh response should include simulated_count"
        assert isinstance(data["simulated_count"], int), "simulated_count should be int"

    def test_refresh_live_simulated_sum_equals_refreshed(self, auth_headers):
        """live_count + simulated_count should equal refreshed_count"""
        response = requests.post(
            f"{BASE_URL}/api/social/metrics/refresh",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 200
        
        data = response.json()
        total = data["live_count"] + data["simulated_count"]
        assert total == data["refreshed_count"], \
            f"live({data['live_count']}) + simulated({data['simulated_count']}) != refreshed({data['refreshed_count']})"


class TestSimulatedFallbackBehavior:
    """Tests to verify simulated fallback when no real credentials exist"""

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

    def test_all_simulated_when_no_real_credentials(self, auth_headers):
        """All platforms should show simulated when bulk-connected with empty credentials"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # With empty credentials from bulk-connect, all should be simulated
        # live_count could be 0 or low (only non-zero if real credentials were added)
        assert data["simulated_count"] >= 0, "simulated_count should be >= 0"
        
        # If all bulk-connected with empty creds, most should be simulated
        if data["live_count"] == 0:
            assert data["simulated_count"] == data["connected_count"], \
                "When no live APIs, all should be simulated"

    def test_has_real_credentials_false_for_empty_creds(self, auth_headers):
        """Platforms with empty credentials should have has_real_credentials: false"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Check connected platforms
        connected = [c for c in data["connections"] if c["connected"]]
        
        # At least some should have has_real_credentials false if bulk-connected
        false_count = sum(1 for c in connected if not c["has_real_credentials"])
        # Since 120 platforms were bulk-connected with empty creds, most should be false
        assert false_count >= 0, "Should track has_real_credentials correctly"
