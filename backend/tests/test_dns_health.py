"""
DNS Health Checker API Tests
Tests for DNS lookup, health check, monitors, and history endpoints.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestDNSHealthEndpoints:
    """DNS Health Checker endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            # Token key is 'access_token' per main agent context
            token = data.get("access_token") or data.get("token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.token = token
            else:
                pytest.skip("No token in login response")
        else:
            pytest.skip(f"Authentication failed: {login_response.status_code}")
        
        yield
        
        # Cleanup: Remove test monitors
        try:
            monitors_resp = self.session.get(f"{BASE_URL}/api/dns/monitors")
            if monitors_resp.status_code == 200:
                monitors = monitors_resp.json().get("monitors", [])
                for m in monitors:
                    if m.get("domain", "").startswith("test-"):
                        self.session.delete(f"{BASE_URL}/api/dns/monitors/{m['monitor_id']}")
        except:
            pass

    # ==================== DNS Lookup Tests ====================
    
    def test_dns_lookup_basic(self):
        """Test basic DNS lookup for google.com"""
        response = self.session.post(f"{BASE_URL}/api/dns/lookup", json={
            "domain": "google.com"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data
        assert data["domain"] == "google.com"
        assert "results" in data
        
        # Should have default record types
        results = data["results"]
        assert "A" in results, "Should have A records"
        print(f"DNS Lookup for google.com: {len(results)} record types returned")
    
    def test_dns_lookup_with_record_types(self):
        """Test DNS lookup with specific record types"""
        response = self.session.post(f"{BASE_URL}/api/dns/lookup", json={
            "domain": "google.com",
            "record_types": ["A", "MX", "NS"]
        })
        
        assert response.status_code == 200
        
        data = response.json()
        results = data["results"]
        
        # Should only have requested types
        assert "A" in results
        assert "MX" in results
        assert "NS" in results
        
        # A records should have values
        a_records = results.get("A", {})
        assert a_records.get("status") == "ok", f"A record status: {a_records.get('status')}"
        assert a_records.get("count", 0) > 0, "Should have at least one A record"
        print(f"A records: {a_records.get('count')}, MX records: {results.get('MX', {}).get('count')}")
    
    def test_dns_lookup_all_record_types(self):
        """Test DNS lookup with all supported record types"""
        all_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV", "CAA"]
        
        response = self.session.post(f"{BASE_URL}/api/dns/lookup", json={
            "domain": "google.com",
            "record_types": all_types
        })
        
        assert response.status_code == 200
        
        data = response.json()
        results = data["results"]
        
        # Should have all requested types in results
        for rt in all_types:
            assert rt in results, f"Missing record type: {rt}"
            assert "status" in results[rt], f"Missing status for {rt}"
            assert "records" in results[rt], f"Missing records for {rt}"
        
        print(f"All {len(all_types)} record types returned successfully")
    
    def test_dns_lookup_empty_domain(self):
        """Test DNS lookup with empty domain returns 400"""
        response = self.session.post(f"{BASE_URL}/api/dns/lookup", json={
            "domain": ""
        })
        
        assert response.status_code == 400, f"Expected 400 for empty domain, got {response.status_code}"
    
    def test_dns_lookup_nonexistent_domain(self):
        """Test DNS lookup for non-existent domain"""
        response = self.session.post(f"{BASE_URL}/api/dns/lookup", json={
            "domain": f"nonexistent-{uuid.uuid4().hex[:8]}.invalid"
        })
        
        assert response.status_code == 200
        
        data = response.json()
        results = data["results"]
        
        # Should return nxdomain status for A records
        a_result = results.get("A", {})
        assert a_result.get("status") in ["nxdomain", "error"], f"Expected nxdomain/error, got {a_result.get('status')}"
        print(f"Non-existent domain status: {a_result.get('status')}")

    # ==================== Health Check Tests ====================
    
    def test_health_check_basic(self):
        """Test health check for google.com"""
        response = self.session.get(f"{BASE_URL}/api/dns/health/google.com")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data
        assert data["domain"] == "google.com"
        assert "health_score" in data
        assert "checks" in data
        assert "timestamp" in data
        
        # Health score should be a number between 0-100
        score = data["health_score"]
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100, f"Health score {score} out of range"
        
        # Should have various checks
        checks = data["checks"]
        expected_checks = ["a_record", "ipv6", "nameservers", "mail", "spf", "dmarc", "soa", "http", "https"]
        for check in expected_checks:
            assert check in checks, f"Missing check: {check}"
            assert "status" in checks[check], f"Missing status for {check}"
            assert "detail" in checks[check], f"Missing detail for {check}"
        
        print(f"Health check for google.com: score={score}, checks={len(checks)}")
    
    def test_health_check_empty_domain(self):
        """Test health check with empty domain returns 400"""
        response = self.session.get(f"{BASE_URL}/api/dns/health/%20")  # URL-encoded space
        
        assert response.status_code == 400, f"Expected 400 for empty domain, got {response.status_code}"
    
    def test_health_check_response_structure(self):
        """Test health check response has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/dns/health/example.com")
        
        assert response.status_code == 200
        
        data = response.json()
        checks = data["checks"]
        
        # Each check should have status and detail
        for check_name, check_data in checks.items():
            assert "status" in check_data, f"Check {check_name} missing status"
            assert check_data["status"] in ["pass", "warn", "fail", "info"], f"Invalid status for {check_name}"
            assert "detail" in check_data, f"Check {check_name} missing detail"
        
        print(f"Health check structure verified for example.com")

    # ==================== History Tests ====================
    
    def test_history_get(self):
        """Test getting lookup history"""
        # First do a lookup to ensure there's history
        self.session.post(f"{BASE_URL}/api/dns/lookup", json={
            "domain": "example.com",
            "record_types": ["A"]
        })
        
        response = self.session.get(f"{BASE_URL}/api/dns/history")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "history" in data
        
        history = data["history"]
        assert isinstance(history, list)
        
        if len(history) > 0:
            entry = history[0]
            assert "lookup_id" in entry
            assert "domain" in entry
            assert "record_types" in entry
            assert "created_at" in entry
            # Should NOT have MongoDB _id
            assert "_id" not in entry, "Should not expose MongoDB _id"
        
        print(f"History returned {len(history)} entries")
    
    def test_history_limit(self):
        """Test history limit parameter"""
        response = self.session.get(f"{BASE_URL}/api/dns/history?limit=5")
        
        assert response.status_code == 200
        
        data = response.json()
        history = data["history"]
        
        assert len(history) <= 5, f"Expected max 5 entries, got {len(history)}"
        print(f"History with limit=5 returned {len(history)} entries")

    # ==================== Monitor Tests ====================
    
    def test_monitor_add(self):
        """Test adding a domain to monitoring"""
        test_domain = f"test-{uuid.uuid4().hex[:8]}.example.com"
        
        response = self.session.post(f"{BASE_URL}/api/dns/monitors", json={
            "domain": test_domain
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "monitor_id" in data
        assert "domain" in data
        assert data["domain"] == test_domain
        assert "created_at" in data
        assert "_id" not in data, "Should not expose MongoDB _id"
        
        # Store for cleanup
        self.test_monitor_id = data["monitor_id"]
        print(f"Added monitor: {data['monitor_id']} for {test_domain}")
    
    def test_monitor_add_duplicate(self):
        """Test adding duplicate domain returns 409"""
        test_domain = f"test-dup-{uuid.uuid4().hex[:8]}.example.com"
        
        # Add first time
        response1 = self.session.post(f"{BASE_URL}/api/dns/monitors", json={
            "domain": test_domain
        })
        assert response1.status_code == 200
        
        # Add second time - should fail
        response2 = self.session.post(f"{BASE_URL}/api/dns/monitors", json={
            "domain": test_domain
        })
        assert response2.status_code == 409, f"Expected 409 for duplicate, got {response2.status_code}"
        print(f"Duplicate monitor correctly rejected with 409")
    
    def test_monitor_list(self):
        """Test listing monitored domains"""
        response = self.session.get(f"{BASE_URL}/api/dns/monitors")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "monitors" in data
        
        monitors = data["monitors"]
        assert isinstance(monitors, list)
        
        for m in monitors:
            assert "monitor_id" in m
            assert "domain" in m
            assert "_id" not in m, "Should not expose MongoDB _id"
        
        print(f"Listed {len(monitors)} monitors")
    
    def test_monitor_delete(self):
        """Test deleting a monitored domain"""
        # First add a monitor
        test_domain = f"test-del-{uuid.uuid4().hex[:8]}.example.com"
        add_response = self.session.post(f"{BASE_URL}/api/dns/monitors", json={
            "domain": test_domain
        })
        assert add_response.status_code == 200
        monitor_id = add_response.json()["monitor_id"]
        
        # Delete it
        delete_response = self.session.delete(f"{BASE_URL}/api/dns/monitors/{monitor_id}")
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        data = delete_response.json()
        assert data.get("status") == "deleted"
        
        # Verify it's gone
        list_response = self.session.get(f"{BASE_URL}/api/dns/monitors")
        monitors = list_response.json().get("monitors", [])
        monitor_ids = [m["monitor_id"] for m in monitors]
        assert monitor_id not in monitor_ids, "Monitor should be deleted"
        
        print(f"Successfully deleted monitor {monitor_id}")
    
    def test_monitor_delete_not_found(self):
        """Test deleting non-existent monitor returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = self.session.delete(f"{BASE_URL}/api/dns/monitors/{fake_id}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent monitor delete correctly returned 404")
    
    def test_monitor_refresh(self):
        """Test refreshing health check on a monitored domain"""
        # Add a real domain to monitor
        test_domain = "example.com"
        
        # Check if already monitored, if not add it
        list_response = self.session.get(f"{BASE_URL}/api/dns/monitors")
        monitors = list_response.json().get("monitors", [])
        
        monitor_id = None
        for m in monitors:
            if m["domain"] == test_domain:
                monitor_id = m["monitor_id"]
                break
        
        if not monitor_id:
            add_response = self.session.post(f"{BASE_URL}/api/dns/monitors", json={
                "domain": test_domain
            })
            if add_response.status_code == 200:
                monitor_id = add_response.json()["monitor_id"]
            elif add_response.status_code == 409:
                # Already exists, get the ID
                list_response = self.session.get(f"{BASE_URL}/api/dns/monitors")
                for m in list_response.json().get("monitors", []):
                    if m["domain"] == test_domain:
                        monitor_id = m["monitor_id"]
                        break
        
        if not monitor_id:
            pytest.skip("Could not get monitor ID for refresh test")
        
        # Refresh the monitor
        response = self.session.post(f"{BASE_URL}/api/dns/monitors/{monitor_id}/refresh")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "health_score" in data
        assert "checks" in data
        assert "domain" in data
        
        print(f"Refreshed monitor {monitor_id}: health_score={data['health_score']}")
    
    def test_monitor_refresh_not_found(self):
        """Test refreshing non-existent monitor returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = self.session.post(f"{BASE_URL}/api/dns/monitors/{fake_id}/refresh")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent monitor refresh correctly returned 404")

    # ==================== Authentication Tests ====================
    
    def test_endpoints_require_auth(self):
        """Test that all endpoints require authentication"""
        # Create a new session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        endpoints = [
            ("POST", f"{BASE_URL}/api/dns/lookup", {"domain": "google.com"}),
            ("GET", f"{BASE_URL}/api/dns/health/google.com", None),
            ("GET", f"{BASE_URL}/api/dns/history", None),
            ("POST", f"{BASE_URL}/api/dns/monitors", {"domain": "test.com"}),
            ("GET", f"{BASE_URL}/api/dns/monitors", None),
            ("DELETE", f"{BASE_URL}/api/dns/monitors/fake-id", None),
            ("POST", f"{BASE_URL}/api/dns/monitors/fake-id/refresh", None),
        ]
        
        for method, url, body in endpoints:
            if method == "GET":
                response = no_auth_session.get(url)
            elif method == "POST":
                response = no_auth_session.post(url, json=body)
            elif method == "DELETE":
                response = no_auth_session.delete(url)
            
            assert response.status_code in [401, 403], f"{method} {url} should require auth, got {response.status_code}"
        
        print("All endpoints correctly require authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
