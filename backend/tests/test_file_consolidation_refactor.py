"""
Tests for backend file consolidation refactoring.
Verifies all critical APIs still work after 232 files were moved from /app/backend/ root
into organized subdirectories (api/, services/, models/, utils/).

Test coverage:
- Health check endpoint
- Authentication flow (login)
- Notifications API
- Messages API
- Analytics API
- Social Connections API
- Distribution Hub API
- Anomaly Detection API
- Revenue API
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasicEndpoints:
    """Health check and root endpoints"""
    
    def test_health_endpoint(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get('status') == 'healthy', f"Expected healthy status, got: {data}"
        assert 'database' in data
        assert data['database'] == 'connected'
        print(f"✅ Health check passed: {data['status']}")

    def test_root_endpoint(self):
        """GET / returns frontend HTML (expected in SPA architecture)"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        # Root returns frontend HTML, not API JSON
        assert 'html' in response.text.lower() or 'Big Mann' in response.text
        print(f"✅ Root endpoint returns frontend HTML (expected SPA behavior)")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_owner_account(self):
        """POST /api/auth/login with owner credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "owner@bigmannentertainment.com",
                "password": "Test1234!"
            }
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert 'access_token' in data or 'token' in data, f"No token in response: {data}"
        print(f"✅ Owner login successful")
        return data.get('access_token') or data.get('token')

    def test_login_invalid_credentials(self):
        """POST /api/auth/login with invalid credentials should fail"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code in [401, 400, 404], f"Expected auth failure, got: {response.status_code}"
        print(f"✅ Invalid login correctly rejected with status {response.status_code}")


class TestAuthenticatedAPIs:
    """APIs that require authentication"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "owner@bigmannentertainment.com",
                "password": "Test1234!"
            }
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access_token') or data.get('token')
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed - skipping authenticated tests")

    def test_notifications_api(self):
        """GET /api/notifications with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers=self.headers
        )
        assert response.status_code == 200, f"Notifications API failed: {response.status_code} - {response.text}"
        data = response.json()
        # Response should be a list or contain notifications key
        assert isinstance(data, (list, dict)), f"Unexpected response type: {type(data)}"
        print(f"✅ Notifications API working - response type: {type(data).__name__}")

    def test_messages_conversations_api(self):
        """GET /api/messages/conversations with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/messages/conversations",
            headers=self.headers
        )
        assert response.status_code == 200, f"Messages API failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✅ Messages/Conversations API working")

    def test_analytics_overview_api(self):
        """GET /api/analytics/overview with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/overview",
            headers=self.headers
        )
        assert response.status_code == 200, f"Analytics Overview API failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, dict)
        print(f"✅ Analytics Overview API working - keys: {list(data.keys())[:5]}")

    def test_social_connections_api(self):
        """GET /api/social/connections with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=self.headers
        )
        assert response.status_code == 200, f"Social Connections API failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✅ Social Connections API working")

    def test_distribution_hub_content_api(self):
        """GET /api/distribution-hub/content with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/content",
            headers=self.headers
        )
        assert response.status_code == 200, f"Distribution Hub API failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✅ Distribution Hub Content API working")

    def test_analytics_anomalies_api(self):
        """GET /api/analytics/anomalies with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/anomalies",
            headers=self.headers
        )
        assert response.status_code == 200, f"Anomaly Detection API failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✅ Analytics Anomalies API working")

    def test_revenue_overview_api(self):
        """GET /api/analytics/revenue/overview with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/revenue/overview",
            headers=self.headers
        )
        assert response.status_code == 200, f"Revenue Overview API failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, dict)
        print(f"✅ Revenue Overview API working - keys: {list(data.keys())[:5]}")


class TestAdditionalEndpoints:
    """Additional endpoint tests to verify refactoring didn't break imports"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "owner@bigmannentertainment.com",
                "password": "Test1234!"
            }
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access_token') or data.get('token')
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")

    def test_distribution_hub_adapters(self):
        """GET /api/distribution-hub/adapters"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/adapters",
            headers=self.headers
        )
        assert response.status_code == 200, f"Adapters endpoint failed: {response.text}"
        data = response.json()
        assert 'live_adapters' in data or 'adapters' in data or isinstance(data, list)
        print(f"✅ Distribution Hub Adapters API working")

    def test_distribution_hub_deliveries(self):
        """GET /api/distribution-hub/deliveries"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries",
            headers=self.headers
        )
        assert response.status_code == 200, f"Deliveries endpoint failed: {response.text}"
        print(f"✅ Distribution Hub Deliveries API working")

    def test_distribution_hub_platforms(self):
        """GET /api/distribution-hub/platforms"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/platforms",
            headers=self.headers
        )
        assert response.status_code == 200, f"Platforms endpoint failed: {response.text}"
        print(f"✅ Distribution Hub Platforms API working")

    def test_creator_profile(self):
        """GET /api/creator/profile"""
        response = requests.get(
            f"{BASE_URL}/api/creator/profile",
            headers=self.headers
        )
        # 200 or 404 (if no profile exists yet) are both acceptable
        assert response.status_code in [200, 404], f"Creator profile endpoint failed: {response.text}"
        print(f"✅ Creator Profile API responding - status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
