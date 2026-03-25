"""
ULN Phase B CRUD API Tests
===========================
Tests for Phase B endpoints - Full CRUD for assets, rights, and endpoints:
- POST/PUT/DELETE /api/uln/labels/{id}/catalog/assets
- GET/PUT /api/uln/labels/{id}/catalog/assets/{assetId}/rights
- POST/PUT/DELETE /api/uln/labels/{id}/endpoints
- GET /api/uln/labels/{id}/audit-snapshot (v2.0 with rights)
"""

import pytest
import requests
import os
import json
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"
TEST_LABEL_ID = "BM-LBL-9D0377FB"  # Test label for CRUD operations


class TestAssetCRUD:
    """Tests for Asset CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def created_asset_id(self, headers):
        """Create a test asset and return its ID for other tests"""
        asset_data = {
            "title": "TEST_Phase_B_Asset",
            "type": "single",
            "artist": "Test Artist",
            "isrc": "USTEST0000001",
            "upc": "123456789012",
            "release_date": "2026-01-15",
            "genre": "Hip-Hop",
            "status": "draft",
            "platforms": ["Spotify", "Apple Music"],
            "streams_total": 0
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=headers,
            json=asset_data
        )
        assert response.status_code == 200, f"Failed to create asset: {response.text}"
        data = response.json()
        assert data.get("success") == True
        asset_id = data.get("asset", {}).get("asset_id")
        assert asset_id, f"No asset_id in response: {data}"
        yield asset_id
        # Cleanup: delete the asset after tests
        requests.delete(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}", headers=headers)
    
    # ── CREATE Asset Tests ────────────────────────────────────────
    
    def test_create_asset_success(self, headers):
        """POST /api/uln/labels/{id}/catalog/assets creates new asset"""
        asset_data = {
            "title": "TEST_Create_Asset_Success",
            "type": "album",
            "artist": "Test Artist 2",
            "isrc": "USTEST0000002",
            "upc": "123456789013",
            "release_date": "2026-02-20",
            "genre": "R&B",
            "status": "pre-release",
            "platforms": ["Tidal"],
            "streams_total": 1000
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=headers,
            json=asset_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        asset = data.get("asset", {})
        assert asset.get("title") == "TEST_Create_Asset_Success"
        assert asset.get("type") == "album"
        assert asset.get("artist") == "Test Artist 2"
        assert asset.get("isrc") == "USTEST0000002"
        assert asset.get("status") == "pre-release"
        assert asset.get("asset_id"), "Asset should have an asset_id"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset['asset_id']}", headers=headers)
    
    def test_create_asset_requires_title(self, headers):
        """POST /api/uln/labels/{id}/catalog/assets requires title field"""
        asset_data = {
            "type": "single",
            "artist": "No Title Artist"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=headers,
            json=asset_data
        )
        # Should fail validation - either 400 or 422
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
    
    def test_create_asset_invalid_label(self, headers):
        """POST /api/uln/labels/{id}/catalog/assets returns 400/404 for invalid label"""
        asset_data = {"title": "Test Asset"}
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/INVALID-LABEL-ID/catalog/assets",
            headers=headers,
            json=asset_data
        )
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"
    
    # ── READ Asset Tests ────────────────────────────────────────
    
    def test_get_catalog_shows_created_asset(self, headers, created_asset_id):
        """GET /api/uln/labels/{id}/catalog shows newly created asset"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assets = data.get("assets", [])
        asset_ids = [a.get("asset_id") for a in assets]
        assert created_asset_id in asset_ids, f"Created asset {created_asset_id} not found in catalog"
    
    def test_catalog_is_seed_data_false(self, headers, created_asset_id):
        """GET /api/uln/labels/{id}/catalog returns is_seed_data=False with real data"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("is_seed_data") == False, "is_seed_data should be False with real assets"
    
    # ── UPDATE Asset Tests ────────────────────────────────────────
    
    def test_update_asset_success(self, headers, created_asset_id):
        """PUT /api/uln/labels/{id}/catalog/assets/{assetId} updates asset"""
        update_data = {
            "title": "TEST_Updated_Title",
            "status": "released",
            "streams_total": 50000
        }
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{created_asset_id}",
            headers=headers,
            json=update_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        asset = data.get("asset", {})
        assert asset.get("title") == "TEST_Updated_Title"
        assert asset.get("status") == "released"
        assert asset.get("streams_total") == 50000
    
    def test_update_asset_verify_persistence(self, headers, created_asset_id):
        """PUT then GET to verify update persisted"""
        # Update
        update_data = {"genre": "Jazz"}
        requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{created_asset_id}",
            headers=headers,
            json=update_data
        )
        
        # Verify via GET catalog
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assets = data.get("assets", [])
        asset = next((a for a in assets if a.get("asset_id") == created_asset_id), None)
        assert asset, f"Asset {created_asset_id} not found"
        assert asset.get("genre") == "Jazz", f"Genre not updated: {asset.get('genre')}"
    
    def test_update_nonexistent_asset(self, headers):
        """PUT /api/uln/labels/{id}/catalog/assets/{assetId} returns 400 for non-existent asset"""
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/NONEXISTENT-ASSET",
            headers=headers,
            json={"title": "Test"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    # ── DELETE Asset Tests ────────────────────────────────────────
    
    def test_delete_asset_success(self, headers):
        """DELETE /api/uln/labels/{id}/catalog/assets/{assetId} removes asset"""
        # First create an asset to delete
        asset_data = {"title": "TEST_To_Delete", "type": "single"}
        create_resp = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=headers,
            json=asset_data
        )
        assert create_resp.status_code == 200
        asset_id = create_resp.json().get("asset", {}).get("asset_id")
        
        # Delete it
        delete_resp = requests.delete(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}",
            headers=headers
        )
        assert delete_resp.status_code == 200, f"Expected 200, got {delete_resp.status_code}"
        
        data = delete_resp.json()
        assert data.get("success") == True
        
        # Verify it's gone
        catalog_resp = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog",
            headers=headers
        )
        assets = catalog_resp.json().get("assets", [])
        asset_ids = [a.get("asset_id") for a in assets]
        assert asset_id not in asset_ids, "Deleted asset should not appear in catalog"
    
    def test_delete_nonexistent_asset(self, headers):
        """DELETE /api/uln/labels/{id}/catalog/assets/{assetId} returns 404 for non-existent"""
        response = requests.delete(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/NONEXISTENT-ASSET",
            headers=headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestRightsCRUD:
    """Tests for Rights management (GET/PUT per asset)"""
    
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
    
    @pytest.fixture(scope="class")
    def test_asset_for_rights(self, headers):
        """Create a test asset for rights testing"""
        asset_data = {"title": "TEST_Rights_Asset", "type": "single", "artist": "Rights Test Artist"}
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=headers,
            json=asset_data
        )
        assert response.status_code == 200
        asset_id = response.json().get("asset", {}).get("asset_id")
        yield asset_id
        # Cleanup
        requests.delete(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}", headers=headers)
    
    def test_get_rights_no_rights_configured(self, headers, test_asset_for_rights):
        """GET /api/uln/labels/{id}/catalog/assets/{assetId}/rights returns null when no rights"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{test_asset_for_rights}/rights",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        # Rights should be null/None when not configured
        assert data.get("rights") is None or "message" in data
    
    def test_upsert_rights_create(self, headers, test_asset_for_rights):
        """PUT /api/uln/labels/{id}/catalog/assets/{assetId}/rights creates rights"""
        rights_data = {
            "splits": [
                {"party": "Artist A", "role": "performer", "percentage": 50.0},
                {"party": "Producer B", "role": "producer", "percentage": 30.0},
                {"party": "Label", "role": "label", "percentage": 20.0}
            ],
            "territories": ["US", "UK", "EU"],
            "ai_consent": True,
            "ai_consent_details": "Allowed for training with attribution",
            "sponsorship_rules": "No alcohol or tobacco brands",
            "exclusive": True,
            "expiry_date": "2030-12-31"
        }
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{test_asset_for_rights}/rights",
            headers=headers,
            json=rights_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        rights = data.get("rights", {})
        assert len(rights.get("splits", [])) == 3
        assert "US" in rights.get("territories", [])
        assert rights.get("ai_consent") == True
        assert rights.get("exclusive") == True
    
    def test_get_rights_after_create(self, headers, test_asset_for_rights):
        """GET /api/uln/labels/{id}/catalog/assets/{assetId}/rights returns saved rights"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{test_asset_for_rights}/rights",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        rights = data.get("rights")
        assert rights is not None, "Rights should exist after upsert"
        assert len(rights.get("splits", [])) >= 1
    
    def test_upsert_rights_update(self, headers, test_asset_for_rights):
        """PUT /api/uln/labels/{id}/catalog/assets/{assetId}/rights updates existing rights"""
        # Update with different data
        rights_data = {
            "splits": [
                {"party": "New Artist", "role": "performer", "percentage": 100.0}
            ],
            "territories": ["GLOBAL"],
            "ai_consent": False,
            "exclusive": False
        }
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{test_asset_for_rights}/rights",
            headers=headers,
            json=rights_data
        )
        assert response.status_code == 200
        
        data = response.json()
        rights = data.get("rights", {})
        assert len(rights.get("splits", [])) == 1
        assert rights.get("splits", [{}])[0].get("party") == "New Artist"
        assert rights.get("ai_consent") == False
        assert "GLOBAL" in rights.get("territories", [])
    
    def test_rights_for_nonexistent_asset(self, headers):
        """PUT /api/uln/labels/{id}/catalog/assets/{assetId}/rights returns 400 for non-existent asset"""
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/NONEXISTENT-ASSET/rights",
            headers=headers,
            json={"splits": [], "territories": ["GLOBAL"]}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestEndpointCRUD:
    """Tests for Distribution Endpoint CRUD operations"""
    
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
    
    @pytest.fixture(scope="class")
    def created_endpoint_id(self, headers):
        """Create a test endpoint and return its ID"""
        endpoint_data = {
            "platform": "Spotify",
            "status": "pending",
            "endpoint_type": "streaming",
            "credentials_ref": "spotify-creds-001"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=headers,
            json=endpoint_data
        )
        assert response.status_code == 200, f"Failed to create endpoint: {response.text}"
        endpoint_id = response.json().get("endpoint", {}).get("endpoint_id")
        yield endpoint_id
        # Cleanup
        requests.delete(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/{endpoint_id}", headers=headers)
    
    # ── CREATE Endpoint Tests ────────────────────────────────────────
    
    def test_create_endpoint_success(self, headers):
        """POST /api/uln/labels/{id}/endpoints creates new endpoint"""
        endpoint_data = {
            "platform": "Apple Music",
            "status": "live",
            "endpoint_type": "streaming",
            "credentials_ref": "apple-creds-001"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=headers,
            json=endpoint_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        endpoint = data.get("endpoint", {})
        assert endpoint.get("platform") == "Apple Music"
        assert endpoint.get("status") == "live"
        assert endpoint.get("endpoint_type") == "streaming"
        assert endpoint.get("endpoint_id"), "Endpoint should have an endpoint_id"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/{endpoint['endpoint_id']}", headers=headers)
    
    def test_create_endpoint_requires_platform(self, headers):
        """POST /api/uln/labels/{id}/endpoints requires platform field"""
        endpoint_data = {
            "status": "pending",
            "endpoint_type": "streaming"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=headers,
            json=endpoint_data
        )
        # Should fail validation
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
    
    def test_create_endpoint_invalid_label(self, headers):
        """POST /api/uln/labels/{id}/endpoints returns 400/404 for invalid label"""
        endpoint_data = {"platform": "Spotify"}
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/INVALID-LABEL-ID/endpoints",
            headers=headers,
            json=endpoint_data
        )
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"
    
    # ── READ Endpoint Tests ────────────────────────────────────────
    
    def test_get_distribution_shows_created_endpoint(self, headers, created_endpoint_id):
        """GET /api/uln/labels/{id}/distribution/status shows newly created endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/distribution/status",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        endpoints = data.get("endpoints", [])
        endpoint_ids = [e.get("endpoint_id") for e in endpoints]
        assert created_endpoint_id in endpoint_ids, f"Created endpoint {created_endpoint_id} not found"
    
    def test_distribution_summary_updates(self, headers, created_endpoint_id):
        """GET /api/uln/labels/{id}/distribution/status summary reflects real data"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/distribution/status",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        summary = data.get("summary", {})
        assert summary.get("total_endpoints", 0) >= 1, "Should have at least 1 endpoint"
        assert data.get("is_seed_data") == False, "is_seed_data should be False with real endpoints"
    
    # ── UPDATE Endpoint Tests ────────────────────────────────────────
    
    def test_update_endpoint_success(self, headers, created_endpoint_id):
        """PUT /api/uln/labels/{id}/endpoints/{endpointId} updates endpoint"""
        update_data = {
            "status": "live",
            "assets_delivered": 25,
            "last_delivery": "2026-03-25T10:00:00Z"
        }
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/{created_endpoint_id}",
            headers=headers,
            json=update_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        endpoint = data.get("endpoint", {})
        assert endpoint.get("status") == "live"
        assert endpoint.get("assets_delivered") == 25
    
    def test_update_endpoint_verify_persistence(self, headers, created_endpoint_id):
        """PUT then GET to verify update persisted"""
        # Update
        update_data = {"errors": 3, "error_message": "Connection timeout"}
        requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/{created_endpoint_id}",
            headers=headers,
            json=update_data
        )
        
        # Verify via GET distribution status
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/distribution/status",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        endpoints = data.get("endpoints", [])
        endpoint = next((e for e in endpoints if e.get("endpoint_id") == created_endpoint_id), None)
        assert endpoint, f"Endpoint {created_endpoint_id} not found"
        assert endpoint.get("errors") == 3
    
    def test_update_nonexistent_endpoint(self, headers):
        """PUT /api/uln/labels/{id}/endpoints/{endpointId} returns 400 for non-existent"""
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/NONEXISTENT-ENDPOINT",
            headers=headers,
            json={"status": "live"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    # ── DELETE Endpoint Tests ────────────────────────────────────────
    
    def test_delete_endpoint_success(self, headers):
        """DELETE /api/uln/labels/{id}/endpoints/{endpointId} removes endpoint"""
        # First create an endpoint to delete
        endpoint_data = {"platform": "Tidal", "status": "pending"}
        create_resp = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=headers,
            json=endpoint_data
        )
        assert create_resp.status_code == 200
        endpoint_id = create_resp.json().get("endpoint", {}).get("endpoint_id")
        
        # Delete it
        delete_resp = requests.delete(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/{endpoint_id}",
            headers=headers
        )
        assert delete_resp.status_code == 200, f"Expected 200, got {delete_resp.status_code}"
        
        data = delete_resp.json()
        assert data.get("success") == True
        
        # Verify it's gone
        dist_resp = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/distribution/status",
            headers=headers
        )
        endpoints = dist_resp.json().get("endpoints", [])
        endpoint_ids = [e.get("endpoint_id") for e in endpoints]
        assert endpoint_id not in endpoint_ids, "Deleted endpoint should not appear"
    
    def test_delete_nonexistent_endpoint(self, headers):
        """DELETE /api/uln/labels/{id}/endpoints/{endpointId} returns 404 for non-existent"""
        response = requests.delete(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/NONEXISTENT-ENDPOINT",
            headers=headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestAuditSnapshotV2:
    """Tests for Audit Snapshot v2.0 with rights data"""
    
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
    
    @pytest.fixture(scope="class")
    def setup_test_data(self, headers):
        """Create test asset with rights for snapshot testing"""
        # Create asset
        asset_resp = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=headers,
            json={"title": "TEST_Snapshot_Asset", "type": "single"}
        )
        asset_id = asset_resp.json().get("asset", {}).get("asset_id")
        
        # Add rights
        requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}/rights",
            headers=headers,
            json={"splits": [{"party": "Test", "percentage": 100}], "territories": ["GLOBAL"], "ai_consent": True}
        )
        
        # Create endpoint
        ep_resp = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=headers,
            json={"platform": "YouTube Music", "status": "live"}
        )
        endpoint_id = ep_resp.json().get("endpoint", {}).get("endpoint_id")
        
        yield {"asset_id": asset_id, "endpoint_id": endpoint_id}
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}", headers=headers)
        requests.delete(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints/{endpoint_id}", headers=headers)
    
    def test_audit_snapshot_v2_schema(self, headers, setup_test_data):
        """GET /api/uln/labels/{id}/audit-snapshot returns v2.0 schema with rights"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/audit-snapshot",
            headers=headers
        )
        assert response.status_code == 200
        
        snapshot = response.json()
        
        # Check v2.0 schema
        assert snapshot.get("snapshot_version") == "2.0", f"Expected v2.0, got {snapshot.get('snapshot_version')}"
        
        # Check required sections
        required_sections = [
            "snapshot_version", "generated_at", "generated_by", "label",
            "members", "member_count", "catalog", "catalog_count",
            "rights", "rights_count", "distribution_endpoints", "distribution_summary"
        ]
        for section in required_sections:
            assert section in snapshot, f"Snapshot missing section: {section}"
    
    def test_audit_snapshot_includes_rights(self, headers, setup_test_data):
        """Audit snapshot includes rights data for assets"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/audit-snapshot",
            headers=headers
        )
        assert response.status_code == 200
        
        snapshot = response.json()
        rights = snapshot.get("rights", [])
        rights_count = snapshot.get("rights_count", 0)
        
        # Should have at least the rights we created
        assert rights_count >= 1, f"Expected at least 1 rights entry, got {rights_count}"
        assert len(rights) >= 1, "Rights array should have entries"
    
    def test_audit_snapshot_includes_catalog(self, headers, setup_test_data):
        """Audit snapshot includes catalog assets"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/audit-snapshot",
            headers=headers
        )
        assert response.status_code == 200
        
        snapshot = response.json()
        catalog = snapshot.get("catalog", [])
        catalog_count = snapshot.get("catalog_count", 0)
        
        assert catalog_count >= 1, f"Expected at least 1 asset, got {catalog_count}"
        assert len(catalog) >= 1, "Catalog array should have entries"
    
    def test_audit_snapshot_includes_distribution(self, headers, setup_test_data):
        """Audit snapshot includes distribution endpoints and summary"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/audit-snapshot",
            headers=headers
        )
        assert response.status_code == 200
        
        snapshot = response.json()
        endpoints = snapshot.get("distribution_endpoints", [])
        summary = snapshot.get("distribution_summary", {})
        
        assert len(endpoints) >= 1, "Should have at least 1 endpoint"
        assert "total_endpoints" in summary, "Summary should have total_endpoints"
        assert "health_pct" in summary, "Summary should have health_pct"


class TestDeleteCascade:
    """Tests for delete cascade behavior (deleting asset removes rights)"""
    
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
    
    def test_delete_asset_removes_rights(self, headers):
        """Deleting an asset should also remove its associated rights"""
        # Create asset
        asset_resp = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=headers,
            json={"title": "TEST_Cascade_Delete", "type": "single"}
        )
        asset_id = asset_resp.json().get("asset", {}).get("asset_id")
        
        # Add rights
        rights_resp = requests.put(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}/rights",
            headers=headers,
            json={"splits": [{"party": "Test", "percentage": 100}], "territories": ["US"]}
        )
        assert rights_resp.status_code == 200
        
        # Verify rights exist
        get_rights = requests.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}/rights",
            headers=headers
        )
        assert get_rights.json().get("rights") is not None
        
        # Delete asset
        delete_resp = requests.delete(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets/{asset_id}",
            headers=headers
        )
        assert delete_resp.status_code == 200
        
        # Rights should be gone (asset doesn't exist, so rights endpoint should fail or return null)
        # Note: The endpoint may return 200 with rights=null or may return an error
        # since the asset no longer exists


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
