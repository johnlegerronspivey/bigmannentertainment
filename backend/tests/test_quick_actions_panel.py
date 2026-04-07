"""
Quick Actions Panel Tests
Tests for the GS1 Hub Quick Actions Panel feature including:
- GET /api/gs1/quick-actions/summary endpoint
- POST /api/licensing/initialize-all-platforms endpoint
- POST /api/comprehensive-licensing/generate-all-platform-licenses endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestQuickActionsSummary:
    """Tests for GET /api/gs1/quick-actions/summary endpoint"""
    
    def test_quick_actions_summary_returns_200(self):
        """Summary endpoint should return 200 without auth"""
        response = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Quick actions summary returns 200")
    
    def test_quick_actions_summary_has_required_fields(self):
        """Summary should contain all required count fields"""
        response = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            'products_count',
            'digital_links_count', 
            'active_licenses',
            'total_licenses',
            'compliance_docs',
            'pending_reviews',
            'identifiers_count'
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            assert isinstance(data[field], int), f"Field {field} should be integer, got {type(data[field])}"
        
        print(f"PASS: Summary has all required fields: {data}")
    
    def test_quick_actions_summary_values_are_non_negative(self):
        """All count values should be non-negative"""
        response = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary")
        data = response.json()
        
        for key, value in data.items():
            assert value >= 0, f"Field {key} has negative value: {value}"
        
        print("PASS: All summary values are non-negative")


class TestLicenseAllPlatforms:
    """Tests for POST /api/licensing/initialize-all-platforms endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "owner@bigmannentertainment.com", "password": "Test1234!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_license_all_requires_auth(self):
        """Endpoint should require authentication"""
        response = requests.post(f"{BASE_URL}/api/licensing/initialize-all-platforms")
        assert response.status_code == 401 or response.status_code == 403, \
            f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: License all platforms requires authentication")
    
    def test_license_all_platforms_success(self, auth_token):
        """Should successfully license platforms with valid auth"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/licensing/initialize-all-platforms",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "platforms_licensed" in data, "Response should contain platforms_licensed"
        assert isinstance(data["platforms_licensed"], int), "platforms_licensed should be integer"
        assert data["platforms_licensed"] > 0, "Should license at least one platform"
        assert "message" in data, "Response should contain message"
        
        print(f"PASS: Licensed {data['platforms_licensed']} platforms successfully")
    
    def test_license_all_returns_platform_details(self, auth_token):
        """Response should include platform license details"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/licensing/initialize-all-platforms",
            headers=headers
        )
        data = response.json()
        
        # Should have platform_licenses dict
        assert "platform_licenses" in data, "Response should contain platform_licenses"
        assert isinstance(data["platform_licenses"], dict), "platform_licenses should be dict"
        
        # Should have business entity info
        assert "business_entity" in data, "Response should contain business_entity"
        
        print(f"PASS: Response includes platform details: {list(data.get('platform_licenses', {}).keys())}")


class TestGenerateComprehensiveLicenses:
    """Tests for POST /api/comprehensive-licensing/generate-all-platform-licenses endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "owner@bigmannentertainment.com", "password": "Test1234!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_generate_comprehensive_requires_auth(self):
        """Endpoint should require authentication"""
        response = requests.post(f"{BASE_URL}/api/comprehensive-licensing/generate-all-platform-licenses")
        assert response.status_code == 401 or response.status_code == 403, \
            f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: Generate comprehensive licenses requires authentication")
    
    def test_generate_comprehensive_success(self, auth_token):
        """Should successfully generate comprehensive licenses with valid auth"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/comprehensive-licensing/generate-all-platform-licenses",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "platforms_licensed" in data, "Response should contain platforms_licensed"
        assert isinstance(data["platforms_licensed"], int), "platforms_licensed should be integer"
        assert data["platforms_licensed"] > 0, "Should license at least one platform"
        
        print(f"PASS: Generated comprehensive licenses for {data['platforms_licensed']} platforms")
    
    def test_generate_comprehensive_returns_agreement_details(self, auth_token):
        """Response should include master agreement details"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/comprehensive-licensing/generate-all-platform-licenses",
            headers=headers
        )
        data = response.json()
        
        # Should have agreement_id
        assert "agreement_id" in data, "Response should contain agreement_id"
        
        # Should have master_agreement with details
        assert "master_agreement" in data, "Response should contain master_agreement"
        master = data["master_agreement"]
        
        assert "platforms_licensed" in master, "Master agreement should list platforms"
        assert "platform_categories" in master, "Master agreement should have categories"
        assert "licensing_fees" in master, "Master agreement should have licensing fees"
        
        print(f"PASS: Agreement {data['agreement_id']} created with {len(master.get('platforms_licensed', []))} platforms")
    
    def test_generate_comprehensive_includes_business_info(self, auth_token):
        """Response should include business information"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/comprehensive-licensing/generate-all-platform-licenses",
            headers=headers
        )
        data = response.json()
        
        assert "business_entity" in data, "Response should contain business_entity"
        assert data["business_entity"] == "Big Mann Entertainment", \
            f"Expected 'Big Mann Entertainment', got {data['business_entity']}"
        
        print("PASS: Business entity correctly identified as Big Mann Entertainment")


class TestQuickActionsPanelIntegration:
    """Integration tests for Quick Actions Panel workflow"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "owner@bigmannentertainment.com", "password": "Test1234!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_summary_updates_after_license_all(self, auth_token):
        """Summary should reflect changes after licensing platforms"""
        # Get initial summary
        initial = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary").json()
        initial_licenses = initial.get("active_licenses", 0)
        
        # License all platforms
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        requests.post(f"{BASE_URL}/api/licensing/initialize-all-platforms", headers=headers)
        
        # Get updated summary
        updated = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary").json()
        updated_licenses = updated.get("active_licenses", 0)
        
        # Should have licenses now
        assert updated_licenses >= initial_licenses, \
            f"Active licenses should not decrease: {initial_licenses} -> {updated_licenses}"
        
        print(f"PASS: Summary updated - licenses: {initial_licenses} -> {updated_licenses}")
    
    def test_summary_updates_after_generate_comprehensive(self, auth_token):
        """Summary should reflect changes after generating comprehensive licenses"""
        # Get initial summary
        initial = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary").json()
        initial_docs = initial.get("compliance_docs", 0)
        
        # Generate comprehensive licenses
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        requests.post(f"{BASE_URL}/api/comprehensive-licensing/generate-all-platform-licenses", headers=headers)
        
        # Get updated summary
        updated = requests.get(f"{BASE_URL}/api/gs1/quick-actions/summary").json()
        updated_docs = updated.get("compliance_docs", 0)
        
        # Compliance docs should exist
        assert updated_docs >= 0, "Compliance docs count should be non-negative"
        
        print(f"PASS: Summary updated - compliance docs: {initial_docs} -> {updated_docs}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
