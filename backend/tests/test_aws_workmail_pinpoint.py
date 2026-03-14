"""
AWS Communications (WorkMail + Pinpoint) API Tests - Phase C
Tests for business email (WorkMail) and marketing campaigns (Pinpoint) integration.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://social-media-aws.preview.emergentagent.com")

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def auth_headers():
    """Authenticate and return headers with Bearer token."""
    login_url = f"{BASE_URL}/api/auth/login"
    response = requests.post(login_url, json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("access_token")  # Note: API returns 'access_token' not 'token'
    assert token, f"No access_token in response: {data}"
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


class TestAWSCommsStatus:
    """Test overall status endpoint for WorkMail + Pinpoint."""

    def test_get_comms_status(self, auth_headers):
        """GET /api/aws-comms/status - returns availability for both services."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/status", headers=auth_headers)
        assert response.status_code == 200, f"Status failed: {response.text}"
        data = response.json()
        
        # Validate WorkMail status
        assert "workmail" in data, "Missing 'workmail' key in status"
        assert "available" in data["workmail"], "Missing 'available' in workmail status"
        assert data["workmail"]["available"] is True, "WorkMail should be available"
        
        # Validate Pinpoint status
        assert "pinpoint" in data, "Missing 'pinpoint' key in status"
        assert "available" in data["pinpoint"], "Missing 'available' in pinpoint status"
        assert data["pinpoint"]["available"] is True, "Pinpoint should be available"
        
        print(f"✓ Comms status: WorkMail={data['workmail']['available']}, Pinpoint={data['pinpoint']['available']}")


class TestWorkMailOrganizations:
    """Test WorkMail organization endpoints."""

    def test_list_organizations(self, auth_headers):
        """GET /api/aws-comms/workmail/organizations - lists organizations."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/workmail/organizations", headers=auth_headers)
        assert response.status_code == 200, f"List orgs failed: {response.text}"
        data = response.json()
        
        assert "organizations" in data, "Missing 'organizations' key"
        assert "total" in data, "Missing 'total' key"
        assert isinstance(data["organizations"], list), "organizations should be a list"
        
        print(f"✓ Found {data['total']} WorkMail organizations")
        
        # If organizations exist, validate structure
        if data["organizations"]:
            org = data["organizations"][0]
            assert "organization_id" in org, "Missing organization_id"
            assert "state" in org, "Missing state field"


class TestPinpointApplications:
    """Test Pinpoint application (project) CRUD endpoints."""

    @pytest.fixture(scope="class")
    def created_app_id(self, auth_headers):
        """Create a test Pinpoint app and return its ID for other tests."""
        create_url = f"{BASE_URL}/api/aws-comms/pinpoint/applications"
        response = requests.post(
            create_url, 
            headers=auth_headers, 
            json={"name": "TEST_PinpointApp_Automated"}
        )
        if response.status_code == 200:
            data = response.json()
            app_id = data.get("application_id")
            print(f"✓ Created test Pinpoint app: {app_id}")
            yield app_id
            # Cleanup after tests
            requests.delete(f"{BASE_URL}/api/aws-comms/pinpoint/applications/{app_id}", headers=auth_headers)
            print(f"✓ Cleaned up test app: {app_id}")
        else:
            pytest.skip(f"Could not create test app: {response.text}")
            yield None

    def test_list_pinpoint_apps(self, auth_headers):
        """GET /api/aws-comms/pinpoint/applications - lists Pinpoint applications."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/applications", headers=auth_headers)
        assert response.status_code == 200, f"List apps failed: {response.text}"
        data = response.json()
        
        assert "applications" in data, "Missing 'applications' key"
        assert "total" in data, "Missing 'total' key"
        assert isinstance(data["applications"], list), "applications should be a list"
        
        print(f"✓ Found {data['total']} Pinpoint applications")
        
        # Validate structure if apps exist
        if data["applications"]:
            app = data["applications"][0]
            assert "application_id" in app, "Missing application_id"
            assert "name" in app, "Missing name field"

    def test_create_pinpoint_app(self, auth_headers):
        """POST /api/aws-comms/pinpoint/applications - creates a Pinpoint application."""
        create_url = f"{BASE_URL}/api/aws-comms/pinpoint/applications"
        response = requests.post(
            create_url, 
            headers=auth_headers, 
            json={"name": "TEST_CreateApp_Temp"}
        )
        assert response.status_code == 200, f"Create app failed: {response.text}"
        data = response.json()
        
        assert "application_id" in data, "Missing application_id in response"
        assert "name" in data, "Missing name in response"
        assert data["name"] == "TEST_CreateApp_Temp", "Name mismatch"
        
        app_id = data["application_id"]
        print(f"✓ Created Pinpoint app: {app_id}")
        
        # Cleanup
        delete_response = requests.delete(
            f"{BASE_URL}/api/aws-comms/pinpoint/applications/{app_id}", 
            headers=auth_headers
        )
        assert delete_response.status_code == 200, f"Cleanup delete failed: {delete_response.text}"
        print(f"✓ Deleted test app: {app_id}")

    def test_delete_pinpoint_app(self, auth_headers):
        """DELETE /api/aws-comms/pinpoint/applications/{application_id} - deletes an app."""
        # First create an app to delete
        create_response = requests.post(
            f"{BASE_URL}/api/aws-comms/pinpoint/applications",
            headers=auth_headers,
            json={"name": "TEST_DeleteMe"}
        )
        assert create_response.status_code == 200, f"Create for delete test failed: {create_response.text}"
        app_id = create_response.json()["application_id"]
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/aws-comms/pinpoint/applications/{app_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        data = delete_response.json()
        assert data.get("deleted") is True, "Expected 'deleted': true"
        print(f"✓ Successfully deleted app: {app_id}")


class TestPinpointSegments:
    """Test Pinpoint segment endpoints."""

    def test_list_segments(self, auth_headers):
        """GET /api/aws-comms/pinpoint/segments/{application_id} - lists segments for an app."""
        # First get an existing app or create one
        apps_response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/applications", headers=auth_headers)
        assert apps_response.status_code == 200
        apps = apps_response.json().get("applications", [])
        
        if apps:
            app_id = apps[0]["application_id"]
        else:
            # Create a temp app
            create_resp = requests.post(
                f"{BASE_URL}/api/aws-comms/pinpoint/applications",
                headers=auth_headers,
                json={"name": "TEST_SegmentTestApp"}
            )
            assert create_resp.status_code == 200
            app_id = create_resp.json()["application_id"]
        
        # List segments
        response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/segments/{app_id}", headers=auth_headers)
        assert response.status_code == 200, f"List segments failed: {response.text}"
        data = response.json()
        
        assert "segments" in data, "Missing 'segments' key"
        assert "total" in data, "Missing 'total' key"
        assert isinstance(data["segments"], list), "segments should be a list"
        
        print(f"✓ Found {data['total']} segments for app {app_id}")

    def test_create_segment(self, auth_headers):
        """POST /api/aws-comms/pinpoint/segments - creates a segment."""
        # Get or create an app
        apps_response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/applications", headers=auth_headers)
        apps = apps_response.json().get("applications", [])
        
        if apps:
            app_id = apps[0]["application_id"]
        else:
            create_app_resp = requests.post(
                f"{BASE_URL}/api/aws-comms/pinpoint/applications",
                headers=auth_headers,
                json={"name": "TEST_SegmentCreatorApp"}
            )
            app_id = create_app_resp.json()["application_id"]
        
        # Create segment
        response = requests.post(
            f"{BASE_URL}/api/aws-comms/pinpoint/segments",
            headers=auth_headers,
            json={"application_id": app_id, "name": "TEST_AutomatedSegment"}
        )
        assert response.status_code == 200, f"Create segment failed: {response.text}"
        data = response.json()
        
        assert "segment_id" in data, "Missing segment_id"
        assert "name" in data, "Missing name"
        assert data["name"] == "TEST_AutomatedSegment", "Name mismatch"
        
        segment_id = data["segment_id"]
        print(f"✓ Created segment: {segment_id}")
        
        # Cleanup segment
        delete_seg_resp = requests.delete(
            f"{BASE_URL}/api/aws-comms/pinpoint/segments/{app_id}/{segment_id}",
            headers=auth_headers
        )
        if delete_seg_resp.status_code == 200:
            print(f"✓ Cleaned up segment: {segment_id}")


class TestPinpointCampaigns:
    """Test Pinpoint campaign endpoints."""

    def test_list_campaigns(self, auth_headers):
        """GET /api/aws-comms/pinpoint/campaigns/{application_id} - lists campaigns."""
        # Get existing app
        apps_response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/applications", headers=auth_headers)
        assert apps_response.status_code == 200
        apps = apps_response.json().get("applications", [])
        
        if apps:
            app_id = apps[0]["application_id"]
        else:
            # Create temp app
            create_resp = requests.post(
                f"{BASE_URL}/api/aws-comms/pinpoint/applications",
                headers=auth_headers,
                json={"name": "TEST_CampaignTestApp"}
            )
            app_id = create_resp.json()["application_id"]
        
        response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/campaigns/{app_id}", headers=auth_headers)
        assert response.status_code == 200, f"List campaigns failed: {response.text}"
        data = response.json()
        
        assert "campaigns" in data, "Missing 'campaigns' key"
        assert "total" in data, "Missing 'total' key"
        assert isinstance(data["campaigns"], list), "campaigns should be a list"
        
        print(f"✓ Found {data['total']} campaigns for app {app_id}")


class TestUnauthenticated:
    """Test that endpoints require authentication."""

    def test_status_requires_auth(self):
        """Status endpoint should require authentication."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/status")
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("✓ Status endpoint correctly requires authentication")

    def test_workmail_orgs_requires_auth(self):
        """WorkMail organizations endpoint should require authentication."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/workmail/organizations")
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("✓ WorkMail organizations endpoint correctly requires authentication")

    def test_pinpoint_apps_requires_auth(self):
        """Pinpoint applications endpoint should require authentication."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/applications")
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("✓ Pinpoint applications endpoint correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
