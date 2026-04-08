"""
Vite 8 Migration Regression Tests
Tests to verify the CRA-to-Vite migration didn't break any functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://unified-media-mgmt.preview.emergentagent.com')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"
CVE_ADMIN_EMAIL = "cveadmin@test.com"
CVE_ADMIN_PASSWORD = "Test1234!"


class TestHealthEndpoints:
    """Health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"Root endpoint: {response.status_code}")
    
    def test_cve_monitor_health(self):
        """Test CVE monitor health endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"CVE Monitor health: {data}")


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_owner_login_success(self):
        """Test owner login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == OWNER_EMAIL
        print(f"Owner login successful: {data['user']['email']}")
    
    def test_cve_admin_login_success(self):
        """Test CVE admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CVE_ADMIN_EMAIL,
            "password": CVE_ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == CVE_ADMIN_EMAIL
        print(f"CVE admin login successful: {data['user']['email']}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("Invalid credentials correctly rejected")


class TestGS1Endpoints:
    """GS1 Licensing Hub endpoint tests"""
    
    def test_quick_actions_summary(self):
        """Test GS1 quick actions summary endpoint"""
        response = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary")
        assert response.status_code == 200
        data = response.json()
        assert "products_count" in data
        assert "digital_links_count" in data
        assert "active_licenses" in data
        assert "total_licenses" in data
        print(f"GS1 Quick Actions: products={data['products_count']}, licenses={data['active_licenses']}")
    
    def test_governance_overview(self):
        """Test GS1 governance overview endpoint"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        assert response.status_code == 200
        data = response.json()
        assert "governance" in data
        assert "disputes" in data
        print(f"Governance overview: rules={data['governance']['total_rules']}, disputes={data['disputes']['total_disputes']}")


class TestCVEMonitorEndpoints:
    """CVE Monitor endpoint tests"""
    
    def test_cve_monitor_stats(self):
        """Test CVE monitor stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/stats")
        assert response.status_code == 200
        print(f"CVE Monitor stats: {response.status_code}")
    
    def test_cve_monitor_feed(self):
        """Test CVE monitor feed endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/feed")
        assert response.status_code == 200
        print(f"CVE Monitor feed: {response.status_code}")
    
    def test_cve_monitor_alerts(self):
        """Test CVE monitor alerts endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"CVE Monitor alerts: {len(data.get('items', []))} items")


class TestProtectedEndpoints:
    """Protected endpoint tests requiring authentication"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_auth_me_endpoint(self, auth_token):
        """Test /auth/me endpoint with valid token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == OWNER_EMAIL
        print(f"Auth me: {data['email']}")
    
    def test_auth_me_without_token(self):
        """Test /auth/me endpoint without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        # API returns 403 (Forbidden) for missing token
        assert response.status_code in [401, 403]
        print("Auth me without token correctly rejected")


class TestFrontendRoutes:
    """Test that frontend routes return 200 (Vite serving correctly)"""
    
    def test_homepage(self):
        """Test homepage loads"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert "Big Mann Entertainment" in response.text
        print("Homepage loads correctly")
    
    def test_login_page(self):
        """Test login page loads"""
        response = requests.get(f"{BASE_URL}/login")
        assert response.status_code == 200
        print("Login page loads correctly")
    
    def test_about_page(self):
        """Test about page loads"""
        response = requests.get(f"{BASE_URL}/about")
        assert response.status_code == 200
        print("About page loads correctly")
    
    def test_platforms_page(self):
        """Test platforms page loads"""
        response = requests.get(f"{BASE_URL}/platforms")
        assert response.status_code == 200
        print("Platforms page loads correctly")
    
    def test_register_page(self):
        """Test register page loads"""
        response = requests.get(f"{BASE_URL}/register")
        assert response.status_code == 200
        print("Register page loads correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
