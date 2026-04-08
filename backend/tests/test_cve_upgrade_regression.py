"""
CVE Upgrade Regression Tests
Tests to verify backend functionality after CVE vulnerability upgrades:
- aiohttp 3.13.3→3.13.4
- cbor2 5.8.0→5.9.0
- cryptography 46.0.5→46.0.6
- litellm 1.75.5→1.83.0
- pygments 2.19.2→2.20.0
- requests 2.32.5→2.33.0
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"
CVE_ADMIN_EMAIL = "cveadmin@test.com"
CVE_ADMIN_PASSWORD = "Test1234!"


class TestHealthEndpoints:
    """Health endpoint tests - verify services are running after upgrades"""
    
    def test_cve_monitor_health(self):
        """Test CVE Monitor health endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CVE Automated Monitoring"
        print("✓ CVE Monitor health endpoint working")
    
    def test_cve_management_health(self):
        """Test CVE Management health endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CVE Management Platform"
        print("✓ CVE Management health endpoint working")


class TestAuthEndpoints:
    """Authentication tests - verify auth works after cryptography upgrade"""
    
    def test_owner_login(self):
        """Test owner login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == OWNER_EMAIL
        print("✓ Owner login working")
    
    def test_cve_admin_login(self):
        """Test CVE admin login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": CVE_ADMIN_EMAIL, "password": CVE_ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == CVE_ADMIN_EMAIL
        print("✓ CVE Admin login working")
    
    def test_invalid_login(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("✓ Invalid login correctly returns 401")


class TestGS1Endpoints:
    """GS1 Hub endpoint tests"""
    
    def test_quick_actions_summary(self):
        """Test GS1 quick actions summary endpoint"""
        response = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary")
        assert response.status_code == 200
        data = response.json()
        # Verify expected fields exist
        assert "products_count" in data
        assert "digital_links_count" in data
        assert "active_licenses" in data
        assert "total_licenses" in data
        print(f"✓ GS1 quick actions summary working - {data['products_count']} products, {data['active_licenses']} active licenses")


class TestCVEMonitorEndpoints:
    """CVE Monitor endpoint tests - verify aiohttp/requests upgrades work"""
    
    def test_cve_monitor_stats(self):
        """Test CVE monitor stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/stats")
        assert response.status_code == 200
        data = response.json()
        # Stats should return some data structure
        assert isinstance(data, dict)
        print("✓ CVE Monitor stats endpoint working")
    
    def test_cve_monitor_feed(self):
        """Test CVE monitor feed endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/feed?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
        print("✓ CVE Monitor feed endpoint working")
    
    def test_cve_monitor_watches(self):
        """Test CVE monitor watches endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/watches")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ CVE Monitor watches endpoint working - {len(data)} watches")
    
    def test_cve_monitor_alerts(self):
        """Test CVE monitor alerts endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve-monitor/alerts?limit=10")
        assert response.status_code == 200
        data = response.json()
        # Response is a dict with items list
        assert isinstance(data, dict)
        assert "items" in data
        assert isinstance(data["items"], list)
        print(f"✓ CVE Monitor alerts endpoint working - {len(data['items'])} alerts")


class TestCVEManagementEndpoints:
    """CVE Management endpoint tests"""
    
    def test_cve_dashboard(self):
        """Test CVE dashboard endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print("✓ CVE dashboard endpoint working")
    
    def test_cve_entries_list(self):
        """Test CVE entries list endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve/entries?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
        print("✓ CVE entries list endpoint working")
    
    def test_cve_services_list(self):
        """Test CVE services list endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve/services")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ CVE services list endpoint working - {len(data)} services")
    
    def test_cve_policies(self):
        """Test CVE policies endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve/policies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print("✓ CVE policies endpoint working")
    
    def test_cve_owners(self):
        """Test CVE owners endpoint"""
        response = requests.get(f"{BASE_URL}/api/cve/owners")
        assert response.status_code == 200
        data = response.json()
        # Response is a dict with people and teams lists
        assert isinstance(data, dict)
        assert "people" in data
        assert "teams" in data
        print(f"✓ CVE owners endpoint working - {len(data['people'])} people, {len(data['teams'])} teams")


@pytest.fixture
def auth_token():
    """Get authentication token for authenticated tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
