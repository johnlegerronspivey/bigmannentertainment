"""
AWS DNS Health Tracking API Tests
Tests for Route 53 health check integration endpoints under /api/aws-dns/*
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestAWSDNSHealthAuth:
    """Authentication tests for AWS DNS Health endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Auth returns 'access_token' not 'token'
        return data.get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_targets_requires_auth(self):
        """Test that /api/aws-dns/targets requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-dns/targets")
        assert response.status_code == 401 or response.status_code == 403
        print("PASS: GET /api/aws-dns/targets requires authentication")
    
    def test_aws_checks_requires_auth(self):
        """Test that /api/aws-dns/aws-checks requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-dns/aws-checks")
        assert response.status_code == 401 or response.status_code == 403
        print("PASS: GET /api/aws-dns/aws-checks requires authentication")


class TestAWSDNSHealthTargets:
    """Tests for AWS DNS Health target management"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_list_targets(self, headers):
        """Test GET /api/aws-dns/targets - List all registered targets"""
        response = requests.get(f"{BASE_URL}/api/aws-dns/targets", headers=headers)
        assert response.status_code == 200, f"Failed to list targets: {response.text}"
        
        data = response.json()
        assert "targets" in data, "Response should contain 'targets' key"
        assert isinstance(data["targets"], list), "targets should be a list"
        
        print(f"PASS: GET /api/aws-dns/targets - Found {len(data['targets'])} targets")
        
        # Check structure of existing targets
        if data["targets"]:
            target = data["targets"][0]
            assert "target_id" in target, "Target should have target_id"
            assert "domain" in target, "Target should have domain"
            assert "health_check_id" in target, "Target should have health_check_id"
            assert "status" in target, "Target should have status"
            print(f"  - First target: {target['domain']} (status: {target['status']})")
    
    def test_list_aws_checks(self, headers):
        """Test GET /api/aws-dns/aws-checks - List all Route 53 health checks"""
        response = requests.get(f"{BASE_URL}/api/aws-dns/aws-checks", headers=headers)
        assert response.status_code == 200, f"Failed to list AWS checks: {response.text}"
        
        data = response.json()
        assert "checks" in data, "Response should contain 'checks' key"
        assert "count" in data, "Response should contain 'count' key"
        assert isinstance(data["checks"], list), "checks should be a list"
        
        print(f"PASS: GET /api/aws-dns/aws-checks - Found {data['count']} AWS health checks")
        
        # Check structure of health checks
        if data["checks"]:
            check = data["checks"][0]
            assert "health_check_id" in check, "Check should have health_check_id"
            assert "domain" in check, "Check should have domain"
            print(f"  - First check: {check['domain']} (type: {check.get('type', 'N/A')})")


class TestAWSDNSHealthCRUD:
    """Tests for AWS DNS Health CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def created_target_id(self, headers):
        """Create a test target and return its ID for cleanup"""
        # Use a unique test domain
        test_domain = f"test-{int(time.time())}.example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/aws-dns/targets",
            headers=headers,
            json={
                "domain": test_domain,
                "port": 443,
                "protocol": "HTTPS",
                "resource_path": "/",
                "request_interval": 30
            }
        )
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            target_id = data.get("target_id")
            print(f"Created test target: {test_domain} (ID: {target_id})")
            yield target_id
            
            # Cleanup: Delete the test target
            delete_response = requests.delete(
                f"{BASE_URL}/api/aws-dns/targets/{target_id}",
                headers=headers
            )
            print(f"Cleanup: Deleted test target (status: {delete_response.status_code})")
        else:
            # If creation fails, yield None and skip cleanup
            print(f"Warning: Could not create test target: {response.text}")
            yield None
    
    def test_register_target(self, headers):
        """Test POST /api/aws-dns/targets - Register a new domain"""
        test_domain = f"test-register-{int(time.time())}.example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/aws-dns/targets",
            headers=headers,
            json={
                "domain": test_domain,
                "port": 443,
                "protocol": "HTTPS",
                "resource_path": "/health",
                "failure_threshold": 3,
                "request_interval": 30
            }
        )
        
        # Accept 200 or 201 for creation
        assert response.status_code in [200, 201], f"Failed to register target: {response.text}"
        
        data = response.json()
        assert "target_id" in data, "Response should contain target_id"
        assert "domain" in data, "Response should contain domain"
        assert "health_check_id" in data, "Response should contain health_check_id"
        assert data["domain"] == test_domain.lower(), "Domain should match"
        
        print(f"PASS: POST /api/aws-dns/targets - Created target for {test_domain}")
        print(f"  - target_id: {data['target_id']}")
        print(f"  - health_check_id: {data['health_check_id']}")
        
        # Cleanup: Delete the created target
        target_id = data["target_id"]
        delete_response = requests.delete(
            f"{BASE_URL}/api/aws-dns/targets/{target_id}",
            headers=headers
        )
        print(f"  - Cleanup: Deleted target (status: {delete_response.status_code})")
    
    def test_register_target_validation(self, headers):
        """Test POST /api/aws-dns/targets - Validation for empty domain"""
        response = requests.post(
            f"{BASE_URL}/api/aws-dns/targets",
            headers=headers,
            json={
                "domain": "",
                "port": 443,
                "protocol": "HTTPS"
            }
        )
        
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422], f"Expected validation error, got: {response.status_code}"
        print("PASS: POST /api/aws-dns/targets - Validates empty domain")
    
    def test_refresh_target_status(self, headers, created_target_id):
        """Test POST /api/aws-dns/targets/{target_id}/refresh - Refresh health status"""
        if created_target_id is None:
            pytest.skip("No test target available")
        
        # Wait a moment for AWS to initialize the health check
        time.sleep(2)
        
        response = requests.post(
            f"{BASE_URL}/api/aws-dns/targets/{created_target_id}/refresh",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to refresh target: {response.text}"
        
        data = response.json()
        assert "health_check_id" in data, "Response should contain health_check_id"
        assert "overall_status" in data, "Response should contain overall_status"
        assert "checkers" in data, "Response should contain checkers"
        assert "checker_count" in data, "Response should contain checker_count"
        
        print(f"PASS: POST /api/aws-dns/targets/{created_target_id}/refresh")
        print(f"  - overall_status: {data['overall_status']}")
        print(f"  - checker_count: {data['checker_count']}")
        
        # Verify checkers structure
        if data["checkers"]:
            checker = data["checkers"][0]
            assert "region" in checker, "Checker should have region"
            assert "status" in checker, "Checker should have status"
            print(f"  - First checker region: {checker['region']}")
    
    def test_refresh_nonexistent_target(self, headers):
        """Test POST /api/aws-dns/targets/{target_id}/refresh - 404 for nonexistent target"""
        fake_id = "nonexistent-target-id-12345"
        
        response = requests.post(
            f"{BASE_URL}/api/aws-dns/targets/{fake_id}/refresh",
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
        print("PASS: POST /api/aws-dns/targets/{fake_id}/refresh - Returns 404 for nonexistent target")
    
    def test_delete_target(self, headers):
        """Test DELETE /api/aws-dns/targets/{target_id} - Delete a target"""
        # First create a target to delete
        test_domain = f"test-delete-{int(time.time())}.example.com"
        
        create_response = requests.post(
            f"{BASE_URL}/api/aws-dns/targets",
            headers=headers,
            json={
                "domain": test_domain,
                "port": 443,
                "protocol": "HTTPS"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create target for delete test: {create_response.text}")
        
        target_id = create_response.json()["target_id"]
        health_check_id = create_response.json()["health_check_id"]
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/aws-dns/targets/{target_id}",
            headers=headers
        )
        
        assert delete_response.status_code == 200, f"Failed to delete target: {delete_response.text}"
        
        data = delete_response.json()
        assert data.get("status") == "deleted", "Response should indicate deleted status"
        assert data.get("health_check_id") == health_check_id, "Response should return health_check_id"
        
        print(f"PASS: DELETE /api/aws-dns/targets/{target_id}")
        print(f"  - Deleted target and AWS health check: {health_check_id}")
        
        # Verify target is gone
        get_response = requests.get(
            f"{BASE_URL}/api/aws-dns/targets",
            headers=headers
        )
        targets = get_response.json().get("targets", [])
        target_ids = [t["target_id"] for t in targets]
        assert target_id not in target_ids, "Deleted target should not appear in list"
        print("  - Verified target no longer in list")
    
    def test_delete_nonexistent_target(self, headers):
        """Test DELETE /api/aws-dns/targets/{target_id} - 404 for nonexistent target"""
        fake_id = "nonexistent-target-id-67890"
        
        response = requests.delete(
            f"{BASE_URL}/api/aws-dns/targets/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
        print("PASS: DELETE /api/aws-dns/targets/{fake_id} - Returns 404 for nonexistent target")


class TestExistingDNSEndpoints:
    """Tests to verify existing DNS endpoints still work"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_dns_lookup(self, headers):
        """Test POST /api/dns/lookup - DNS lookup still works"""
        response = requests.post(
            f"{BASE_URL}/api/dns/lookup",
            headers=headers,
            json={
                "domain": "google.com",
                "record_types": ["A", "MX"]
            }
        )
        
        assert response.status_code == 200, f"DNS lookup failed: {response.text}"
        data = response.json()
        assert "domain" in data, "Response should contain domain"
        assert "results" in data, "Response should contain results"
        print("PASS: POST /api/dns/lookup - DNS lookup still works")
    
    def test_dns_health_check(self, headers):
        """Test GET /api/dns/health/{domain} - Health check still works"""
        response = requests.get(
            f"{BASE_URL}/api/dns/health/google.com",
            headers=headers
        )
        
        assert response.status_code == 200, f"DNS health check failed: {response.text}"
        data = response.json()
        assert "domain" in data, "Response should contain domain"
        assert "health_score" in data, "Response should contain health_score"
        assert "checks" in data, "Response should contain checks"
        print(f"PASS: GET /api/dns/health/google.com - Health score: {data['health_score']}")
    
    def test_dns_monitors_list(self, headers):
        """Test GET /api/dns/monitors - Monitors list still works"""
        response = requests.get(
            f"{BASE_URL}/api/dns/monitors",
            headers=headers
        )
        
        assert response.status_code == 200, f"DNS monitors list failed: {response.text}"
        data = response.json()
        assert "monitors" in data, "Response should contain monitors"
        print(f"PASS: GET /api/dns/monitors - Found {len(data['monitors'])} monitors")
    
    def test_dns_history(self, headers):
        """Test GET /api/dns/history - History still works"""
        response = requests.get(
            f"{BASE_URL}/api/dns/history?limit=5",
            headers=headers
        )
        
        assert response.status_code == 200, f"DNS history failed: {response.text}"
        data = response.json()
        assert "history" in data, "Response should contain history"
        print(f"PASS: GET /api/dns/history - Found {len(data['history'])} history entries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
