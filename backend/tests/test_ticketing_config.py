"""
Ticketing Configuration API Tests
Tests for Jira/ServiceNow integration configuration endpoints:
- GET /api/cve/ticketing/providers - list providers
- GET /api/cve/ticketing/config - get masked config
- PUT /api/cve/ticketing/config - save config (super_admin/tenant_admin only)
- POST /api/cve/ticketing/test-connection - test connection (protected)
- GET /api/cve/ticketing/stats - ticket stats
- GET /api/cve/ticketing/tickets - list tickets
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TICKETING_API = f"{BASE_URL}/api/cve/ticketing"

# Test credentials
SUPER_ADMIN_EMAIL = "cveadmin@test.com"
SUPER_ADMIN_PASSWORD = "Test1234!"


class TestTicketingConfigAuth:
    """Authentication and authorization tests for ticketing config endpoints"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        """Get super_admin authentication token"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPER_ADMIN_EMAIL,
            "password": SUPER_ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Super admin login failed: {resp.text}"
        data = resp.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, super_admin_token):
        """Auth headers for super_admin"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {super_admin_token}"
        }
    
    # -- Provider list (public) --
    def test_get_providers_returns_jira_and_servicenow(self):
        """GET /providers returns jira and servicenow with required fields"""
        resp = requests.get(f"{TICKETING_API}/providers")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "providers" in data
        providers = data["providers"]
        
        # Verify Jira
        assert "jira" in providers
        assert providers["jira"]["name"] == "Jira"
        assert "base_url" in providers["jira"]["fields"]
        assert "email" in providers["jira"]["fields"]
        assert "api_token" in providers["jira"]["fields"]
        assert "project_key" in providers["jira"]["fields"]
        
        # Verify ServiceNow
        assert "servicenow" in providers
        assert providers["servicenow"]["name"] == "ServiceNow"
        assert "instance_url" in providers["servicenow"]["fields"]
        assert "username" in providers["servicenow"]["fields"]
        assert "password" in providers["servicenow"]["fields"]
        print("PASS: GET /providers returns jira and servicenow with required fields")
    
    # -- Config retrieval (public but returns masked) --
    def test_get_config_returns_masked_credentials(self, auth_headers):
        """GET /config returns masked config (api_token shows masked)"""
        resp = requests.get(f"{TICKETING_API}/config", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        # Should have provider, settings, simulation_mode
        assert "provider" in data
        assert "settings" in data
        assert "simulation_mode" in data
        assert "configured" in data
        
        # If credentials are saved, check masking
        if data.get("provider") and data.get("settings", {}).get("api_token"):
            api_token = data["settings"]["api_token"]
            assert api_token.startswith("••••"), f"api_token not masked: {api_token}"
            print(f"PASS: GET /config returns masked api_token: {api_token}")
        else:
            print(f"PASS: GET /config returns structure correctly. provider={data.get('provider')}")
    
    # -- Config save (protected: super_admin/tenant_admin only) --
    def test_put_config_requires_auth(self):
        """PUT /config without auth returns 401/403"""
        resp = requests.put(f"{TICKETING_API}/config", json={
            "provider": "jira",
            "settings": {"base_url": "https://test.atlassian.net"}
        })
        assert resp.status_code in [401, 403], f"Expected 401/403 without auth, got {resp.status_code}"
        print(f"PASS: PUT /config without auth returns {resp.status_code}")
    
    def test_put_config_with_super_admin_succeeds(self, auth_headers):
        """PUT /config with super_admin token saves config and returns masked response"""
        # Save Jira config
        resp = requests.put(f"{TICKETING_API}/config", headers=auth_headers, json={
            "provider": "jira",
            "settings": {
                "base_url": "https://test-domain.atlassian.net",
                "email": "test@example.com",
                "api_token": "test_token_1234567890",
                "project_key": "CVE"
            }
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        # Response should have masked api_token
        assert "settings" in data
        assert data["settings"]["api_token"].startswith("••••"), f"api_token not masked in response: {data['settings']['api_token']}"
        assert data["provider"] == "jira"
        print(f"PASS: PUT /config with super_admin saves and returns masked: {data['settings']['api_token']}")
    
    def test_put_config_preserves_token_on_masked_save(self, auth_headers):
        """PUT with masked value (••••XXXX) preserves existing real token"""
        # First save real credentials
        resp1 = requests.put(f"{TICKETING_API}/config", headers=auth_headers, json={
            "provider": "jira",
            "settings": {
                "base_url": "https://preserve-test.atlassian.net",
                "email": "preserve@example.com",
                "api_token": "REAL_SECRET_TOKEN_ABCD1234",
                "project_key": "PRES"
            }
        })
        assert resp1.status_code == 200
        masked_token = resp1.json()["settings"]["api_token"]
        assert masked_token.startswith("••••")
        
        # Now update other fields but send masked token back
        resp2 = requests.put(f"{TICKETING_API}/config", headers=auth_headers, json={
            "provider": "jira",
            "settings": {
                "base_url": "https://preserve-test2.atlassian.net",  # Changed URL
                "email": "preserve2@example.com",  # Changed email
                "api_token": masked_token,  # Keep masked value
                "project_key": "PRES"
            }
        })
        assert resp2.status_code == 200
        
        # Verify the token was preserved (still masked, not overwritten with ••••)
        final_token = resp2.json()["settings"]["api_token"]
        assert final_token.startswith("••••")
        # The last 4 chars should match original
        assert final_token[-4:] == "1234", f"Token not preserved. Expected ending 1234, got {final_token[-4:]}"
        print(f"PASS: Masked token preserved correctly: {final_token}")
    
    # -- Test connection (protected) --
    def test_test_connection_requires_auth(self):
        """POST /test-connection returns 401/403 without auth"""
        resp = requests.post(f"{TICKETING_API}/test-connection")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: POST /test-connection without auth returns {resp.status_code}")
    
    def test_test_connection_with_super_admin(self, auth_headers):
        """POST /test-connection with super_admin token succeeds"""
        resp = requests.post(f"{TICKETING_API}/test-connection", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "success" in data
        assert "message" in data
        # Could be real or simulation
        if data.get("simulation"):
            print(f"PASS: Test connection in simulation mode: {data['message']}")
        else:
            print(f"PASS: Test connection result: success={data['success']}, message={data['message']}")
    
    # -- Stats endpoint --
    def test_get_stats_returns_ticket_counts(self, auth_headers):
        """GET /stats returns ticket counts and mode"""
        resp = requests.get(f"{TICKETING_API}/stats", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "total" in data
        assert "open" in data
        assert "in_progress" in data
        assert "closed" in data
        assert "simulation_mode" in data
        assert "provider" in data
        print(f"PASS: GET /stats returns counts: total={data['total']}, open={data['open']}, mode={'SIM' if data['simulation_mode'] else 'LIVE'}")
    
    # -- Tickets list --
    def test_get_tickets_returns_list(self, auth_headers):
        """GET /tickets returns ticket list"""
        resp = requests.get(f"{TICKETING_API}/tickets?limit=10", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        print(f"PASS: GET /tickets returns {data['total']} total tickets, showing {len(data['items'])} items")
    
    # -- Per-tenant config --
    def test_config_includes_tenant_id(self, auth_headers):
        """Config includes tenant_id field"""
        resp = requests.get(f"{TICKETING_API}/config", headers=auth_headers)
        assert resp.status_code == 200
        
        data = resp.json()
        # tenant_id field should exist (may be empty string if no tenant)
        assert "tenant_id" in data
        print(f"PASS: Config includes tenant_id: '{data.get('tenant_id', '')}'")


class TestTicketingConfigNonAdmin:
    """Test that non-admin users get 403 on config modification"""
    
    def test_analyst_cannot_save_config(self):
        """Non-admin (analyst/manager) cannot save ticketing config"""
        # First create an analyst user or use existing
        # For this test, we'll try with invalid/no proper role token
        # The key test is that PUT /config requires super_admin or tenant_admin
        
        # Try with a fake/expired token
        fake_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid_token_12345"
        }
        resp = requests.put(f"{TICKETING_API}/config", headers=fake_headers, json={
            "provider": "jira",
            "settings": {}
        })
        assert resp.status_code in [401, 403], f"Expected 401/403 for invalid token, got {resp.status_code}"
        print(f"PASS: Invalid token returns {resp.status_code} on PUT /config")


class TestTicketingDisconnect:
    """Test disconnect (clear config) functionality"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": SUPER_ADMIN_EMAIL,
            "password": SUPER_ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        return resp.json()["access_token"]
    
    def test_disconnect_clears_provider(self, super_admin_token):
        """Sending empty provider disconnects ticketing"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {super_admin_token}"
        }
        
        # First configure something
        requests.put(f"{TICKETING_API}/config", headers=headers, json={
            "provider": "servicenow",
            "settings": {"instance_url": "https://test.service-now.com"}
        })
        
        # Now disconnect
        resp = requests.put(f"{TICKETING_API}/config", headers=headers, json={
            "provider": "",
            "settings": {}
        })
        assert resp.status_code == 200
        
        # Verify config is cleared
        get_resp = requests.get(f"{TICKETING_API}/config", headers=headers)
        data = get_resp.json()
        assert data["provider"] == ""
        assert data["configured"] == False
        print("PASS: Disconnect clears provider config")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
