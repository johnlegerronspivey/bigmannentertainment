"""
Backend Refactoring Regression Tests

This test suite verifies that all APIs continue to work correctly after the
backend codebase refactoring. The refactoring extracted shared code from the
monolithic 8141-line server.py into proper modules:
- config/ (database.py, settings.py, platforms.py)
- models/ (core.py, agency.py)
- auth/ (service.py)

All imports in 17 dependent files were updated to import from the new modules.
"""
import pytest
import requests
import os

# Backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "cveadmin@test.com"
TEST_PASSWORD = "Test1234!"


class TestHealthEndpoint:
    """Test /api/health endpoint - verifies 119 distribution platforms"""
    
    def test_health_returns_200(self):
        """Health endpoint should return 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
    def test_health_returns_119_platforms(self):
        """Health endpoint should show 119 distribution platforms from config/platforms.py"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["distribution_platforms"] == 119
        assert data["database"] == "connected"
        
    def test_health_services_operational(self):
        """Health endpoint should show all services operational"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        
        assert "services" in data
        services = data["services"]
        assert services.get("content_ingestion") == "operational"
        assert services.get("distribution") == "operational"
        assert services.get("licensing") == "operational"


class TestAuthentication:
    """Test auth endpoints - verifies auth/service.py functions"""
    
    def test_login_success(self):
        """POST /api/auth/login should authenticate user and return tokens"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        
    def test_login_invalid_credentials(self):
        """POST /api/auth/login should reject invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        assert response.status_code in [401, 404]
        
    def test_protected_route_without_token(self):
        """Protected routes should reject requests without token"""
        # Note: /api/cve/dashboard may not require auth in this app
        # Instead test /api/agency/profile which requires auth
        response = requests.get(f"{BASE_URL}/api/agency/profile")
        assert response.status_code in [401, 403]


class TestProtectedEndpoints:
    """Test protected endpoints with valid auth token"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
        
    def test_cve_dashboard(self, auth_token):
        """GET /api/cve/dashboard should return total_cves and severity data"""
        response = requests.get(
            f"{BASE_URL}/api/cve/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "total_cves" in data
        assert isinstance(data["total_cves"], int)
        assert "severity_breakdown" in data
        assert "critical" in data["severity_breakdown"]
        assert "high" in data["severity_breakdown"]
        assert "medium" in data["severity_breakdown"]
        assert "low" in data["severity_breakdown"]
        
    def test_cve_reporting_summary(self, auth_token):
        """GET /api/cve/reporting/summary should return severity_distribution"""
        response = requests.get(
            f"{BASE_URL}/api/cve/reporting/summary",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "severity_distribution" in data
        assert "total_cves" in data
        assert "sla_compliance" in data
        
    def test_sla_dashboard(self, auth_token):
        """GET /api/cve/sla/dashboard should return compliance data"""
        response = requests.get(
            f"{BASE_URL}/api/cve/sla/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "overall_compliance" in data
        assert "severity_stats" in data
        assert "critical" in data["severity_stats"]
        assert "high" in data["severity_stats"]
        
    def test_iac_overview(self, auth_token):
        """GET /api/cve/iac/overview should return terraform data"""
        response = requests.get(
            f"{BASE_URL}/api/cve/iac/overview",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "terraform" in data
        assert data["terraform"]["configured"] == True
        assert "lambda" in data
        assert "environments" in data


class TestUnprotectedEndpoints:
    """Test endpoints that don't require authentication"""
    
    def test_agency_status(self):
        """GET /api/agency/status should return operational status"""
        response = requests.get(f"{BASE_URL}/api/agency/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "operational"
        assert data["module"] == "Agency Onboarding"
        assert "features" in data
        assert len(data["features"]) >= 5
        
    def test_distribution_platforms(self):
        """GET /api/distribution/platforms should return platform list"""
        response = requests.get(f"{BASE_URL}/api/distribution/platforms")
        assert response.status_code == 200
        
        data = response.json()
        assert "platforms" in data
        platforms = data["platforms"]
        
        # Verify key platforms exist from config/platforms.py
        assert "instagram" in platforms
        assert "twitter" in platforms
        assert "spotify" in platforms
        assert "youtube" in platforms
        
        # Verify platform structure
        instagram = platforms["instagram"]
        assert instagram["type"] == "social_media"
        assert "api_endpoint" in instagram
        assert "supported_formats" in instagram
        
    def test_licensing_health(self):
        """GET /api/licensing/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/licensing/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "licensing_system"
        assert data["database"] == "connected"
        assert "capabilities" in data
        assert data["capabilities"]["license_generation"] == "enabled"


class TestModuleImports:
    """Verify that refactored modules are working correctly"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_config_database_module(self):
        """config/database.py - MongoDB connection should work"""
        # Verified by health endpoint returning database: connected
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        assert data["database"] == "connected"
        
    def test_config_platforms_module(self):
        """config/platforms.py - 119 platforms should be loaded"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        assert data["distribution_platforms"] == 119
        
    def test_config_settings_module(self):
        """config/settings.py - Settings should be loaded for JWT"""
        # Verified by successful auth that uses SECRET_KEY and ALGORITHM
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        
    def test_models_core_module(self, auth_token):
        """models/core.py - User model should work"""
        # Verified by user data in login response
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        user = response.json()["user"]
        
        # Verify User model fields from models/core.py
        assert "id" in user
        assert "email" in user
        assert "full_name" in user
        assert "is_active" in user
        assert "role" in user
        
    def test_models_agency_module(self):
        """models/agency.py - Agency models should work"""
        # Verified by agency/status endpoint
        response = requests.get(f"{BASE_URL}/api/agency/status")
        assert response.status_code == 200
        
    def test_auth_service_module(self, auth_token):
        """auth/service.py - Auth functions should work"""
        # Verified by protected endpoint access
        response = requests.get(
            f"{BASE_URL}/api/cve/dashboard",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200


class TestAdditionalEndpoints:
    """Additional endpoint tests to ensure full coverage"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_cve_dashboard_trends(self, auth_token):
        """GET /api/cve/reporting/dashboard-trends should return trend data"""
        response = requests.get(
            f"{BASE_URL}/api/cve/reporting/dashboard-trends",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "current_week" in data
        assert "previous_week" in data
        assert "mini_trend" in data
        
    def test_rights_compliance(self):
        """GET /api/rights/compliance should return compliance status"""
        response = requests.get(f"{BASE_URL}/api/rights/compliance")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "compliance_status" in data
        
    def test_licensing_comprehensive(self):
        """GET /api/licensing/comprehensive should return licensing overview"""
        response = requests.get(f"{BASE_URL}/api/licensing/comprehensive")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "comprehensive_licensing" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
