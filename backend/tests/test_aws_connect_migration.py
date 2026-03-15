"""
AWS Pinpoint to Amazon Connect Migration Tests
Tests for the migration from AWS Pinpoint (marketing campaigns) to Amazon Connect (contact center).
Validates that:
1. All Pinpoint routes are removed
2. All Connect routes are properly implemented
3. Status endpoint now returns 'connect' instead of 'pinpoint'
4. WorkMail endpoints still work
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://feature-signoff.preview.emergentagent.com")

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
    token = data.get("access_token")
    assert token, f"No access_token in response: {data}"
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ══════════════════════════════════════════════════════════════════
# STATUS ENDPOINT - Should return 'connect' instead of 'pinpoint'
# ══════════════════════════════════════════════════════════════════
class TestCommsStatus:
    """Test the overall status endpoint returns Connect instead of Pinpoint."""

    def test_status_returns_connect_not_pinpoint(self, auth_headers):
        """GET /api/aws-comms/status should return 'connect' key, NOT 'pinpoint' key."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/status", headers=auth_headers)
        assert response.status_code == 200, f"Status failed: {response.text}"
        data = response.json()
        
        # Should have 'connect' key
        assert "connect" in data, f"Missing 'connect' key in status. Got keys: {data.keys()}"
        assert "available" in data["connect"], "Missing 'available' in connect status"
        
        # Should NOT have 'pinpoint' key (migration removed it)
        assert "pinpoint" not in data, f"'pinpoint' key should be removed after migration. Got keys: {data.keys()}"
        
        # WorkMail should still be present
        assert "workmail" in data, "WorkMail should still be present"
        assert "available" in data["workmail"], "Missing 'available' in workmail status"
        
        print(f"✓ Status correctly shows Connect (no Pinpoint): connect={data['connect']['available']}, workmail={data['workmail']['available']}")

    def test_status_connect_has_correct_fields(self, auth_headers):
        """Connect status should have expected fields."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        connect = data["connect"]
        assert "available" in connect, "Missing 'available'"
        assert connect["available"] is True, "Connect should be available"
        
        # Check for optional fields when available
        if connect["available"]:
            assert "region" in connect or "service" in connect or "instances_found" in connect, \
                "Connect status should include additional info when available"
        
        print(f"✓ Connect status fields verified: {connect}")


# ══════════════════════════════════════════════════════════════════
# OLD PINPOINT ROUTES - Should all return 404 (removed)
# ══════════════════════════════════════════════════════════════════
class TestPinpointRoutesRemoved:
    """Verify all old Pinpoint routes are removed and return 404."""

    def test_pinpoint_applications_removed(self, auth_headers):
        """GET /api/aws-comms/pinpoint/applications should return 404."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/applications", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404 (route removed), got {response.status_code}"
        print("✓ /pinpoint/applications correctly removed (404)")

    def test_pinpoint_segments_removed(self, auth_headers):
        """GET /api/aws-comms/pinpoint/segments/{app_id} should return 404."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/segments/fake-app-id", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404 (route removed), got {response.status_code}"
        print("✓ /pinpoint/segments correctly removed (404)")

    def test_pinpoint_campaigns_removed(self, auth_headers):
        """GET /api/aws-comms/pinpoint/campaigns/{app_id} should return 404."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/pinpoint/campaigns/fake-app-id", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404 (route removed), got {response.status_code}"
        print("✓ /pinpoint/campaigns correctly removed (404)")

    def test_pinpoint_send_email_removed(self, auth_headers):
        """POST /api/aws-comms/pinpoint/send-email should return 404."""
        response = requests.post(
            f"{BASE_URL}/api/aws-comms/pinpoint/send-email", 
            headers=auth_headers,
            json={"application_id": "fake", "to": "test@test.com", "subject": "Test", "body": "Test"}
        )
        assert response.status_code == 404, f"Expected 404 (route removed), got {response.status_code}"
        print("✓ /pinpoint/send-email correctly removed (404)")

    def test_pinpoint_send_sms_removed(self, auth_headers):
        """POST /api/aws-comms/pinpoint/send-sms should return 404."""
        response = requests.post(
            f"{BASE_URL}/api/aws-comms/pinpoint/send-sms", 
            headers=auth_headers,
            json={"application_id": "fake", "phone": "+1234567890", "message": "Test"}
        )
        assert response.status_code == 404, f"Expected 404 (route removed), got {response.status_code}"
        print("✓ /pinpoint/send-sms correctly removed (404)")


# ══════════════════════════════════════════════════════════════════
# AMAZON CONNECT ROUTES - New endpoints
# ══════════════════════════════════════════════════════════════════
class TestConnectInstances:
    """Test Amazon Connect instances endpoints."""

    def test_list_connect_instances(self, auth_headers):
        """GET /api/aws-comms/connect/instances - returns list of instances."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/connect/instances", headers=auth_headers)
        assert response.status_code == 200, f"List instances failed: {response.text}"
        data = response.json()
        
        assert "instances" in data, "Missing 'instances' key"
        assert "total" in data, "Missing 'total' key"
        assert isinstance(data["instances"], list), "instances should be a list"
        
        # Empty list is expected since AWS account may have 0 instances
        print(f"✓ Connect instances endpoint working. Found {data['total']} instances")


class TestConnectQueues:
    """Test Amazon Connect queues endpoints."""

    def test_list_queues_requires_instance_id(self, auth_headers):
        """GET /api/aws-comms/connect/queues requires instance_id query param."""
        # Without instance_id should fail with 422
        response = requests.get(f"{BASE_URL}/api/aws-comms/connect/queues", headers=auth_headers)
        assert response.status_code == 422, f"Expected 422 (missing param), got {response.status_code}"
        print("✓ Queues endpoint correctly requires instance_id parameter")

    def test_list_queues_with_fake_instance(self, auth_headers):
        """GET /api/aws-comms/connect/queues?instance_id=xxx - handles non-existent instance."""
        response = requests.get(
            f"{BASE_URL}/api/aws-comms/connect/queues?instance_id=fake-instance-id", 
            headers=auth_headers
        )
        # Should return 500 (AWS error) or 404 (instance not found)
        assert response.status_code in [404, 500], f"Expected 404/500 for fake instance, got {response.status_code}"
        print(f"✓ Queues endpoint handles non-existent instance (status {response.status_code})")


class TestConnectContactFlows:
    """Test Amazon Connect contact flows endpoints."""

    def test_contact_flows_requires_instance_id(self, auth_headers):
        """GET /api/aws-comms/connect/contact-flows requires instance_id query param."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/connect/contact-flows", headers=auth_headers)
        assert response.status_code == 422, f"Expected 422 (missing param), got {response.status_code}"
        print("✓ Contact flows endpoint correctly requires instance_id parameter")


class TestConnectHoursOfOperation:
    """Test Amazon Connect hours of operation endpoints."""

    def test_hours_requires_instance_id(self, auth_headers):
        """GET /api/aws-comms/connect/hours-of-operation requires instance_id query param."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/connect/hours-of-operation", headers=auth_headers)
        assert response.status_code == 422, f"Expected 422 (missing param), got {response.status_code}"
        print("✓ Hours of operation endpoint correctly requires instance_id parameter")


class TestConnectUsers:
    """Test Amazon Connect users endpoints."""

    def test_connect_users_requires_instance_id(self, auth_headers):
        """GET /api/aws-comms/connect/users requires instance_id query param."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/connect/users", headers=auth_headers)
        assert response.status_code == 422, f"Expected 422 (missing param), got {response.status_code}"
        print("✓ Connect users endpoint correctly requires instance_id parameter")


class TestConnectRoutingProfiles:
    """Test Amazon Connect routing profiles endpoints."""

    def test_routing_profiles_requires_instance_id(self, auth_headers):
        """GET /api/aws-comms/connect/routing-profiles requires instance_id query param."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/connect/routing-profiles", headers=auth_headers)
        assert response.status_code == 422, f"Expected 422 (missing param), got {response.status_code}"
        print("✓ Routing profiles endpoint correctly requires instance_id parameter")


# ══════════════════════════════════════════════════════════════════
# WORKMAIL ROUTES - Should still work unchanged
# ══════════════════════════════════════════════════════════════════
class TestWorkMailStillWorks:
    """Verify WorkMail endpoints still work after migration."""

    def test_workmail_organizations(self, auth_headers):
        """GET /api/aws-comms/workmail/organizations still works."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/workmail/organizations", headers=auth_headers)
        assert response.status_code == 200, f"WorkMail orgs failed: {response.text}"
        data = response.json()
        
        assert "organizations" in data, "Missing 'organizations' key"
        assert "total" in data, "Missing 'total' key"
        assert isinstance(data["organizations"], list), "organizations should be a list"
        
        print(f"✓ WorkMail organizations still working. Found {data['total']} organizations")


# ══════════════════════════════════════════════════════════════════
# AUTHENTICATION REQUIRED - All endpoints need auth
# ══════════════════════════════════════════════════════════════════
class TestAuthenticationRequired:
    """Verify all endpoints require authentication."""

    def test_status_requires_auth(self):
        """Status endpoint requires authentication."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/status")
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("✓ Status endpoint correctly requires authentication")

    def test_connect_instances_requires_auth(self):
        """Connect instances endpoint requires authentication."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/connect/instances")
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("✓ Connect instances endpoint correctly requires authentication")

    def test_workmail_orgs_requires_auth(self):
        """WorkMail organizations endpoint requires authentication."""
        response = requests.get(f"{BASE_URL}/api/aws-comms/workmail/organizations")
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("✓ WorkMail organizations endpoint correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
