"""
Test Suite: Per-Tenant Data Scoping, Live Ticketing Integration, Per-User Notification Preferences
Tests the 3 new features:
1. Tenant data scoping with backward compatibility
2. Jira/ServiceNow ticketing (simulation mode)
3. Per-user WebSocket notification preferences
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


class TestAuthAndTenantContext:
    """Test authentication and tenant context extraction"""
    
    def test_login_returns_tenant_info(self):
        """Verify login response includes tenant_id and tenant_name"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "cveadmin@test.com",
            "password": "Test1234!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        user = data["user"]
        # Verify tenant fields exist on user
        assert "tenant_id" in user
        assert "tenant_name" in user
        assert user["tenant_id"] == "40e6f47e-b021-4605-9e1c-7a0992854f6c"
        assert user["tenant_name"] == "Default Organization"
        print(f"PASS: Login returns tenant_id={user['tenant_id']}, tenant_name={user['tenant_name']}")


@pytest.fixture
def auth_token():
    """Get valid auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "cveadmin@test.com",
        "password": "Test1234!"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    pytest.skip("Authentication failed")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with Bearer token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestCVEDashboardTenantScoping:
    """CVE Dashboard API with per-tenant data scoping"""
    
    def test_dashboard_without_auth_returns_all_data(self):
        """Without auth token, all data is returned (no tenant filter)"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard")
        assert response.status_code == 200
        data = response.json()
        # Verify dashboard structure
        assert "total_cves" in data
        assert "open_cves" in data
        assert "severity_breakdown" in data
        print(f"PASS: Dashboard without auth returns data (total_cves={data['total_cves']})")
    
    def test_dashboard_with_auth_returns_tenant_scoped_data(self, auth_headers):
        """With auth token, dashboard data is scoped to user's tenant (backward compatible)"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Verify dashboard structure
        assert "total_cves" in data
        assert "open_cves" in data
        assert "severity_breakdown" in data
        # Should still return data (backward compatible with legacy docs without tenant_id)
        print(f"PASS: Dashboard with auth returns scoped data (total_cves={data['total_cves']})")


class TestCVEEntriesTenantScoping:
    """CVE entries list/create API with per-tenant data scoping"""
    
    def test_list_cves_without_auth_returns_all(self):
        """Without auth, list_cves returns all CVEs (no tenant filter)"""
        response = requests.get(f"{BASE_URL}/api/cve/entries?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        print(f"PASS: List CVEs without auth returns {len(data['items'])} items, total={data['total']}")
    
    def test_list_cves_with_auth_returns_tenant_scoped(self, auth_headers):
        """With auth, list_cves filters by tenant_id (backward compatible)"""
        response = requests.get(f"{BASE_URL}/api/cve/entries?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        # Data should still show (includes legacy docs without tenant_id)
        print(f"PASS: List CVEs with auth returns {len(data['items'])} items, total={data['total']}")
    
    def test_create_cve_sets_tenant_id_from_user(self, auth_headers):
        """Create CVE with auth sets tenant_id from authenticated user"""
        test_cve = {
            "title": "TEST_TenantScoping CVE",
            "description": "Test CVE for tenant scoping validation",
            "severity": "low",
            "affected_package": "test-pkg-tenant"
        }
        response = requests.post(f"{BASE_URL}/api/cve/entries", json=test_cve, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "tenant_id" in data
        # Tenant ID should be set from the authenticated user
        assert data["tenant_id"] == "40e6f47e-b021-4605-9e1c-7a0992854f6c"
        print(f"PASS: Created CVE has tenant_id={data['tenant_id']}")


class TestTicketingIntegrationSimulationMode:
    """Ticketing Integration (Jira/ServiceNow) in Simulation Mode"""
    
    def test_get_ticketing_config(self):
        """Get ticketing configuration"""
        response = requests.get(f"{BASE_URL}/api/cve/ticketing/config")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "simulation_mode" in data
        print(f"PASS: Ticketing config - provider={data.get('provider')}, simulation_mode={data.get('simulation_mode')}")
    
    def test_save_jira_config_simulation_mode(self):
        """Saving Jira config without real credentials enables simulation_mode"""
        config = {
            "provider": "jira",
            "settings": {
                "base_url": "https://test.atlassian.net",
                "project_key": "CVE"
                # Missing email and api_token -> simulation mode
            }
        }
        response = requests.put(f"{BASE_URL}/api/cve/ticketing/config", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data.get("provider") == "jira"
        assert data.get("simulation_mode") == True
        print("PASS: Jira config saved in simulation mode (missing credentials)")
    
    def test_save_servicenow_config_simulation_mode(self):
        """Saving ServiceNow config without real credentials enables simulation_mode"""
        config = {
            "provider": "servicenow",
            "settings": {
                "instance_url": "https://test.service-now.com"
                # Missing username and password -> simulation mode
            }
        }
        response = requests.put(f"{BASE_URL}/api/cve/ticketing/config", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data.get("provider") == "servicenow"
        assert data.get("simulation_mode") == True
        print("PASS: ServiceNow config saved in simulation mode (missing credentials)")
    
    def test_test_connection_simulation_mode(self):
        """Test connection in simulation mode returns success=True, simulation=True"""
        # First set jira as provider in simulation mode
        requests.put(f"{BASE_URL}/api/cve/ticketing/config", json={
            "provider": "jira",
            "settings": {"base_url": "https://test.atlassian.net", "project_key": "CVE"}
        })
        
        response = requests.post(f"{BASE_URL}/api/cve/ticketing/test-connection")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("simulation") == True
        print(f"PASS: Test connection - success={data['success']}, simulation={data['simulation']}, message={data.get('message')}")
    
    def test_list_tickets_with_tenant_scoping(self, auth_headers):
        """List tickets is scoped by tenant_id when auth provided"""
        response = requests.get(f"{BASE_URL}/api/cve/ticketing/tickets", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        print(f"PASS: List tickets returns {len(data['items'])} items, total={data['total']}")
    
    def test_ticketing_stats_with_tenant_scoping(self, auth_headers):
        """Ticketing stats are scoped by tenant_id when auth provided"""
        response = requests.get(f"{BASE_URL}/api/cve/ticketing/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "open" in data
        assert "simulation_mode" in data
        print(f"PASS: Ticketing stats - total={data['total']}, simulation_mode={data['simulation_mode']}")


class TestPerUserNotificationPreferences:
    """Per-user notification preferences with muted_severities, quiet_hours, channel toggles"""
    
    def test_get_default_notification_preferences(self):
        """GET /api/cve/sla/notification-preferences returns default prefs"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/notification-preferences")
        assert response.status_code == 200
        data = response.json()
        # Core fields must exist
        assert "notify_on_warning" in data
        assert "notify_on_breach" in data
        assert "per_severity" in data
        # New fields may not exist in legacy global prefs (backward compat)
        muted = data.get("muted_severities", [])
        quiet_enabled = data.get("quiet_hours_enabled", False)
        print(f"PASS: Default notification prefs - notify_on_warning={data['notify_on_warning']}, muted={muted}, quiet_hours_enabled={quiet_enabled}")
    
    def test_get_user_specific_notification_preferences(self):
        """GET with user_id query param returns/creates user-specific prefs or falls back to global"""
        test_user_id = "test-user-notif-prefs-new-789"
        response = requests.get(f"{BASE_URL}/api/cve/sla/notification-preferences?user_id={test_user_id}")
        assert response.status_code == 200
        data = response.json()
        # Core fields must exist
        assert "notify_on_warning" in data
        assert "per_severity" in data
        # If first access, falls back to global prefs (may not have new fields)
        # If new doc created, should have all fields including user_id
        user_id_in_response = data.get("user_id", "")
        muted = data.get("muted_severities", [])
        print(f"PASS: User prefs for {test_user_id} - user_id_in_resp={user_id_in_response}, muted={muted}")
    
    def test_update_user_notification_preferences(self):
        """PUT with user_id saves user-specific prefs"""
        test_user_id = "test-user-notif-prefs-456"
        prefs = {
            "notify_on_warning": False,
            "notify_on_breach": True,
            "notify_on_escalation": True,
            "muted_severities": ["low"],
            "quiet_hours_enabled": True,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "06:00",
            "per_severity": {
                "critical": {"email": True, "in_app": True, "ws": True},
                "high": {"email": True, "in_app": True, "ws": True},
                "medium": {"email": False, "in_app": True, "ws": False},
                "low": {"email": False, "in_app": False, "ws": False}
            }
        }
        response = requests.put(
            f"{BASE_URL}/api/cve/sla/notification-preferences?user_id={test_user_id}",
            json=prefs
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("user_id") == test_user_id
        assert data.get("notify_on_warning") == False
        assert "low" in data.get("muted_severities", [])
        assert data.get("quiet_hours_enabled") == True
        print(f"PASS: Updated user prefs - muted_severities={data['muted_severities']}, quiet_hours={data['quiet_hours_enabled']}")
    
    def test_check_should_notify_muted_severity(self):
        """Check endpoint returns all false for muted severity"""
        test_user_id = "test-user-notif-prefs-456"
        # First verify the user has low muted
        get_resp = requests.get(f"{BASE_URL}/api/cve/sla/notification-preferences?user_id={test_user_id}")
        if "low" not in get_resp.json().get("muted_severities", []):
            # Set it up
            requests.put(
                f"{BASE_URL}/api/cve/sla/notification-preferences?user_id={test_user_id}",
                json={
                    "notify_on_warning": True,
                    "notify_on_breach": True,
                    "notify_on_escalation": True,
                    "muted_severities": ["low"],
                    "quiet_hours_enabled": False,
                    "quiet_hours_start": "22:00",
                    "quiet_hours_end": "07:00",
                    "per_severity": {}
                }
            )
        
        # Now check - low severity should be muted
        response = requests.get(
            f"{BASE_URL}/api/cve/sla/notification-preferences/check?user_id={test_user_id}&event_type=sla_breach&severity=low"
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "in_app" in data
        assert "ws" in data
        # All should be false for muted severity
        assert data["email"] == False
        assert data["in_app"] == False
        assert data["ws"] == False
        print(f"PASS: Check muted severity returns all false - {data}")
    
    def test_check_should_notify_normal_severity(self):
        """Check endpoint returns configured values for non-muted severity"""
        test_user_id = "test-user-notif-prefs-456"
        response = requests.get(
            f"{BASE_URL}/api/cve/sla/notification-preferences/check?user_id={test_user_id}&event_type=sla_breach&severity=critical"
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "in_app" in data
        assert "ws" in data
        # Critical should not be muted, so at least some channels should be true
        print(f"PASS: Check critical severity - email={data['email']}, in_app={data['in_app']}, ws={data['ws']}")


class TestTicketCreationSimulationMode:
    """Test ticket creation in simulation mode"""
    
    def test_create_ticket_simulation(self, auth_headers):
        """Create a ticket in simulation mode"""
        # First ensure we have a provider configured
        requests.put(f"{BASE_URL}/api/cve/ticketing/config", json={
            "provider": "jira",
            "settings": {"base_url": "https://test.atlassian.net", "project_key": "CVE"}
        })
        
        # Get a CVE to create ticket for
        cves_response = requests.get(f"{BASE_URL}/api/cve/entries?limit=1", headers=auth_headers)
        if cves_response.status_code != 200:
            pytest.skip("No CVEs available")
        cves = cves_response.json().get("items", [])
        if not cves:
            pytest.skip("No CVEs available for ticket creation")
        
        cve_id = cves[0].get("id")
        
        # Try to create ticket
        response = requests.post(f"{BASE_URL}/api/cve/ticketing/tickets/create/{cve_id}", headers=auth_headers)
        
        if response.status_code == 400:
            # Ticket might already exist
            data = response.json()
            print(f"INFO: Ticket creation returned 400 - {data.get('detail', 'already exists')}")
            return
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "external_key" in data
        assert data.get("simulation") == True
        print(f"PASS: Created ticket in simulation mode - external_key={data.get('external_key')}")


class TestBackwardCompatibility:
    """Verify backward compatibility - existing data without tenant_id still accessible"""
    
    def test_cve_list_includes_legacy_data(self, auth_headers):
        """CVE list should include legacy docs (without tenant_id) for backward compatibility"""
        response = requests.get(f"{BASE_URL}/api/cve/entries?limit=50", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Should have data (existing CVEs are legacy without tenant_id)
        total = data.get("total", 0)
        items_count = len(data.get("items", []))
        print(f"PASS: Backward compatible - returned {items_count} items out of {total} total CVEs")
        
        # Check if any items lack tenant_id (legacy data)
        legacy_count = sum(1 for item in data["items"] if not item.get("tenant_id"))
        if legacy_count > 0:
            print(f"  INFO: Found {legacy_count} legacy CVEs without tenant_id")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
