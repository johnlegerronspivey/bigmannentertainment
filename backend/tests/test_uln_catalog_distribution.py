"""
ULN Catalog, Distribution Status & Audit Snapshot API Tests
============================================================
Tests for Phase A (Quick Win) endpoints:
- GET /api/uln/labels/{labelId}/catalog
- GET /api/uln/labels/{labelId}/distribution/status
- GET /api/uln/labels/{labelId}/audit-snapshot
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"
KNOWN_LABEL_ID = "BM-LBL-1758F4E9"  # Big Mann Entertainment


class TestAuthentication:
    """Authentication tests - verify auth is required for all endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Login returns 'access_token' not 'token'
        token = data.get("access_token")
        assert token, f"No access_token in response: {data}"
        return token
    
    def test_catalog_requires_auth(self):
        """GET /api/uln/labels/{labelId}/catalog returns 401/403 without token"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/catalog")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_distribution_requires_auth(self):
        """GET /api/uln/labels/{labelId}/distribution/status returns 401/403 without token"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/distribution/status")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_audit_snapshot_requires_auth(self):
        """GET /api/uln/labels/{labelId}/audit-snapshot returns 401/403 without token"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/audit-snapshot")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"


class TestCatalogEndpoint:
    """Tests for GET /api/uln/labels/{labelId}/catalog"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_catalog_returns_200_for_valid_label(self, headers):
        """GET /api/uln/labels/{labelId}/catalog returns 200 with catalog data"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/catalog", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True: {data}"
        assert "assets" in data, "Response should contain 'assets' field"
        assert "total_assets" in data, "Response should contain 'total_assets' field"
        assert "label_id" in data, "Response should contain 'label_id' field"
        assert "label_name" in data, "Response should contain 'label_name' field"
    
    def test_catalog_assets_have_required_fields(self, headers):
        """Catalog assets should have title, type, artist, isrc, release_date, status, streams_total"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/catalog", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assets = data.get("assets", [])
        
        # Should have at least seed data
        assert len(assets) > 0, "Expected at least one asset (seed data)"
        
        # Check first asset has required fields
        asset = assets[0]
        required_fields = ["title", "type", "artist", "isrc", "release_date", "status", "streams_total"]
        for field in required_fields:
            assert field in asset, f"Asset missing required field: {field}"
    
    def test_catalog_returns_404_for_nonexistent_label(self, headers):
        """GET /api/uln/labels/{labelId}/catalog returns 404 for non-existent label"""
        fake_label_id = "NONEXISTENT-LABEL-12345"
        response = requests.get(f"{BASE_URL}/api/uln/labels/{fake_label_id}/catalog", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_catalog_seed_data_indicator(self, headers):
        """Catalog response should indicate if data is seed/placeholder"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/catalog", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "is_seed_data" in data, "Response should contain 'is_seed_data' field"


class TestDistributionStatusEndpoint:
    """Tests for GET /api/uln/labels/{labelId}/distribution/status"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_distribution_returns_200_for_valid_label(self, headers):
        """GET /api/uln/labels/{labelId}/distribution/status returns 200 with distribution data"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/distribution/status", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True: {data}"
        assert "endpoints" in data, "Response should contain 'endpoints' field"
        assert "summary" in data, "Response should contain 'summary' field"
        assert "label_id" in data, "Response should contain 'label_id' field"
        assert "label_name" in data, "Response should contain 'label_name' field"
    
    def test_distribution_summary_has_metrics(self, headers):
        """Distribution summary should have total_endpoints, live, pending, error, health_pct"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/distribution/status", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        summary = data.get("summary", {})
        
        required_fields = ["total_endpoints", "live", "pending", "error", "health_pct"]
        for field in required_fields:
            assert field in summary, f"Summary missing required field: {field}"
    
    def test_distribution_endpoints_have_required_fields(self, headers):
        """Distribution endpoints should have platform, status, last_delivery, assets_delivered, errors"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/distribution/status", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        endpoints = data.get("endpoints", [])
        
        # Should have at least seed data
        assert len(endpoints) > 0, "Expected at least one endpoint (seed data)"
        
        # Check first endpoint has required fields
        endpoint = endpoints[0]
        required_fields = ["platform", "status", "assets_delivered", "errors"]
        for field in required_fields:
            assert field in endpoint, f"Endpoint missing required field: {field}"
    
    def test_distribution_returns_404_for_nonexistent_label(self, headers):
        """GET /api/uln/labels/{labelId}/distribution/status returns 404 for non-existent label"""
        fake_label_id = "NONEXISTENT-LABEL-12345"
        response = requests.get(f"{BASE_URL}/api/uln/labels/{fake_label_id}/distribution/status", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_distribution_health_percentage_calculation(self, headers):
        """Health percentage should be calculated correctly (live/total * 100)"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/distribution/status", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        summary = data.get("summary", {})
        
        total = summary.get("total_endpoints", 0)
        live = summary.get("live", 0)
        health_pct = summary.get("health_pct", 0)
        
        if total > 0:
            expected_health = round((live / total) * 100, 1)
            assert health_pct == expected_health, f"Health % mismatch: expected {expected_health}, got {health_pct}"


class TestAuditSnapshotEndpoint:
    """Tests for GET /api/uln/labels/{labelId}/audit-snapshot"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_audit_snapshot_returns_200_for_valid_label(self, headers):
        """GET /api/uln/labels/{labelId}/audit-snapshot returns 200 with JSON file"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/audit-snapshot", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_audit_snapshot_has_content_disposition_header(self, headers):
        """Audit snapshot should have Content-Disposition header for file download"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/audit-snapshot", headers=headers)
        assert response.status_code == 200
        
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition, f"Expected attachment header, got: {content_disposition}"
        assert "filename=" in content_disposition, f"Expected filename in header, got: {content_disposition}"
        assert KNOWN_LABEL_ID in content_disposition, f"Expected label ID in filename, got: {content_disposition}"
    
    def test_audit_snapshot_is_valid_json(self, headers):
        """Audit snapshot content should be valid JSON"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/audit-snapshot", headers=headers)
        assert response.status_code == 200
        
        # Should be parseable as JSON
        try:
            snapshot = response.json()
        except json.JSONDecodeError as e:
            pytest.fail(f"Response is not valid JSON: {e}")
        
        assert isinstance(snapshot, dict), "Snapshot should be a JSON object"
    
    def test_audit_snapshot_contains_required_sections(self, headers):
        """Audit snapshot should contain label, members, catalog, distribution_endpoints, audit entries"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/audit-snapshot", headers=headers)
        assert response.status_code == 200
        
        snapshot = response.json()
        
        required_sections = [
            "snapshot_version",
            "generated_at",
            "generated_by",
            "label",
            "members",
            "catalog",
            "distribution_endpoints",
            "distribution_summary"
        ]
        
        for section in required_sections:
            assert section in snapshot, f"Snapshot missing required section: {section}"
    
    def test_audit_snapshot_returns_404_for_nonexistent_label(self, headers):
        """GET /api/uln/labels/{labelId}/audit-snapshot returns 404 for non-existent label"""
        fake_label_id = "NONEXISTENT-LABEL-12345"
        response = requests.get(f"{BASE_URL}/api/uln/labels/{fake_label_id}/audit-snapshot", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_audit_snapshot_content_type_is_json(self, headers):
        """Audit snapshot should have application/json content type"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/audit-snapshot", headers=headers)
        assert response.status_code == 200
        
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected application/json, got: {content_type}"


class TestLabelSwitcherIntegration:
    """Tests to verify label switcher still works with new endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_me_labels_endpoint_still_works(self, headers):
        """GET /api/uln/me/labels should still return user's labels"""
        response = requests.get(f"{BASE_URL}/api/uln/me/labels", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "labels" in data, "Response should contain 'labels' field"
        labels = data.get("labels", [])
        assert len(labels) > 0, "User should have at least one label"
    
    def test_members_endpoint_still_works(self, headers):
        """GET /api/uln/labels/{labelId}/members should still work (regression)"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{KNOWN_LABEL_ID}/members", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "members" in data, "Response should contain 'members' field"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
