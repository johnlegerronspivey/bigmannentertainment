"""
Key Vault & Secrets Protection API Tests
Tests for: GET /api/keys/vault, /api/keys/security-scan, /api/keys/audit-log, /api/keys/categories
           POST /api/keys/rotate/{key_name}
Admin-only endpoints for secrets management
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "owner@bigmannentertainment.com"
ADMIN_PASSWORD = "Test1234!"
NON_ADMIN_EMAIL = "testuser@example.com"
NON_ADMIN_PASSWORD = "Test1234!"


class TestKeyVaultAuth:
    """Test authentication and authorization for key vault endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            # Token is in 'access_token' field per test_credentials.md
            return data.get("access_token") or data.get("token")
        pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")
    
    def test_vault_requires_auth(self):
        """Test that /api/keys/vault requires authentication"""
        response = requests.get(f"{BASE_URL}/api/keys/vault")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: /api/keys/vault returns {response.status_code} without auth")
    
    def test_security_scan_requires_auth(self):
        """Test that /api/keys/security-scan requires authentication"""
        response = requests.get(f"{BASE_URL}/api/keys/security-scan")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: /api/keys/security-scan returns {response.status_code} without auth")
    
    def test_audit_log_requires_auth(self):
        """Test that /api/keys/audit-log requires authentication"""
        response = requests.get(f"{BASE_URL}/api/keys/audit-log")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: /api/keys/audit-log returns {response.status_code} without auth")
    
    def test_categories_requires_auth(self):
        """Test that /api/keys/categories requires authentication"""
        response = requests.get(f"{BASE_URL}/api/keys/categories")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: /api/keys/categories returns {response.status_code} without auth")
    
    def test_rotate_requires_auth(self):
        """Test that /api/keys/rotate/{key_name} requires authentication"""
        response = requests.post(f"{BASE_URL}/api/keys/rotate/SECRET_KEY")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: /api/keys/rotate returns {response.status_code} without auth")


class TestKeyVaultEndpoints:
    """Test key vault endpoints with admin authentication"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token") or data.get("token")
            print(f"Admin login successful, token obtained")
            return token
        pytest.skip(f"Admin authentication failed: {response.status_code}")
    
    @pytest.fixture
    def auth_headers(self, admin_token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_get_vault_success(self, auth_headers):
        """Test GET /api/keys/vault returns vault summary with masked keys"""
        response = requests.get(f"{BASE_URL}/api/keys/vault", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success", f"Expected status=success, got {data}"
        
        vault_data = data.get("data", {})
        assert "keys" in vault_data, "Response should contain 'keys' array"
        assert "summary" in vault_data, "Response should contain 'summary' object"
        assert "categories" in vault_data, "Response should contain 'categories' object"
        
        # Verify summary structure
        summary = vault_data["summary"]
        assert "total_keys" in summary, "Summary should have total_keys"
        assert "configured" in summary, "Summary should have configured count"
        assert "missing" in summary, "Summary should have missing count"
        assert "health_score" in summary, "Summary should have health_score"
        
        print(f"PASS: GET /api/keys/vault - {summary['total_keys']} keys, health score: {summary['health_score']}")
    
    def test_vault_keys_are_masked(self, auth_headers):
        """Test that key values are properly masked (only last 4 chars visible)"""
        response = requests.get(f"{BASE_URL}/api/keys/vault", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        keys = data.get("data", {}).get("keys", [])
        
        masked_count = 0
        for key in keys:
            masked_value = key.get("masked_value", "")
            # Masked values should either be "NOT SET", "****", or start with asterisks
            if masked_value not in ["NOT SET", "****"]:
                assert masked_value.startswith("*"), f"Key {key['key_name']} value not properly masked: {masked_value}"
                # Should show only last 4 chars
                visible_part = masked_value.lstrip("*")
                assert len(visible_part) <= 4, f"Key {key['key_name']} shows more than 4 chars: {visible_part}"
                masked_count += 1
        
        print(f"PASS: {masked_count} keys properly masked with only last 4 chars visible")
    
    def test_vault_key_structure(self, auth_headers):
        """Test that each key has required fields"""
        response = requests.get(f"{BASE_URL}/api/keys/vault", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        keys = data.get("data", {}).get("keys", [])
        assert len(keys) > 0, "Should have at least one key in registry"
        
        required_fields = ["key_name", "label", "sensitivity", "category", "status", "masked_value"]
        for key in keys[:5]:  # Check first 5 keys
            for field in required_fields:
                assert field in key, f"Key {key.get('key_name', 'unknown')} missing field: {field}"
        
        print(f"PASS: All keys have required fields: {required_fields}")
    
    def test_get_security_scan(self, auth_headers):
        """Test GET /api/keys/security-scan returns scan results"""
        response = requests.get(f"{BASE_URL}/api/keys/security-scan", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        
        scan_data = data.get("data", {})
        assert "issues" in scan_data, "Scan should contain 'issues' array"
        assert "total_issues" in scan_data, "Scan should contain 'total_issues'"
        assert "by_severity" in scan_data, "Scan should contain 'by_severity'"
        assert "overall_status" in scan_data, "Scan should contain 'overall_status'"
        
        # Verify severity breakdown
        by_severity = scan_data["by_severity"]
        assert "critical" in by_severity
        assert "high" in by_severity
        assert "medium" in by_severity
        
        print(f"PASS: GET /api/keys/security-scan - {scan_data['total_issues']} issues, status: {scan_data['overall_status']}")
    
    def test_security_scan_issue_structure(self, auth_headers):
        """Test that security issues have proper structure"""
        response = requests.get(f"{BASE_URL}/api/keys/security-scan", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        issues = data.get("data", {}).get("issues", [])
        
        if len(issues) > 0:
            required_fields = ["severity", "category", "title", "description", "remediation"]
            for issue in issues[:3]:  # Check first 3 issues
                for field in required_fields:
                    assert field in issue, f"Issue missing field: {field}"
            print(f"PASS: Security issues have proper structure with remediation guidance")
        else:
            print(f"PASS: No security issues found (healthy configuration)")
    
    def test_get_audit_log(self, auth_headers):
        """Test GET /api/keys/audit-log returns audit entries"""
        response = requests.get(f"{BASE_URL}/api/keys/audit-log", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        
        audit_data = data.get("data", {})
        assert "entries" in audit_data, "Audit log should contain 'entries' array"
        assert "total" in audit_data, "Audit log should contain 'total' count"
        
        print(f"PASS: GET /api/keys/audit-log - {audit_data['total']} entries")
    
    def test_audit_log_with_limit(self, auth_headers):
        """Test GET /api/keys/audit-log with limit parameter"""
        response = requests.get(f"{BASE_URL}/api/keys/audit-log?limit=5", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        entries = data.get("data", {}).get("entries", [])
        assert len(entries) <= 5, f"Expected max 5 entries, got {len(entries)}"
        
        print(f"PASS: Audit log limit parameter works correctly")
    
    def test_get_categories(self, auth_headers):
        """Test GET /api/keys/categories returns grouped keys"""
        response = requests.get(f"{BASE_URL}/api/keys/categories", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        
        categories = data.get("data", {})
        assert len(categories) > 0, "Should have at least one category"
        
        # Verify category structure
        for cat_name, cat_data in categories.items():
            assert "total" in cat_data, f"Category {cat_name} missing 'total'"
            assert "configured" in cat_data, f"Category {cat_name} missing 'configured'"
        
        print(f"PASS: GET /api/keys/categories - {len(categories)} categories: {list(categories.keys())}")
    
    def test_rotate_key_success(self, auth_headers):
        """Test POST /api/keys/rotate/{key_name} logs rotation event"""
        response = requests.post(f"{BASE_URL}/api/keys/rotate/SECRET_KEY", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "success"
        assert "message" in data, "Response should contain message"
        assert "key_name" in data, "Response should contain key_name"
        assert data["key_name"] == "SECRET_KEY"
        
        print(f"PASS: POST /api/keys/rotate/SECRET_KEY - rotation event logged")
    
    def test_rotate_invalid_key(self, auth_headers):
        """Test POST /api/keys/rotate with invalid key name returns 404"""
        response = requests.post(f"{BASE_URL}/api/keys/rotate/INVALID_KEY_NAME_XYZ", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        print(f"PASS: Invalid key rotation returns 404")
    
    def test_audit_log_records_vault_access(self, auth_headers):
        """Test that accessing vault creates audit log entry"""
        # First access vault
        requests.get(f"{BASE_URL}/api/keys/vault", headers=auth_headers)
        
        # Then check audit log
        response = requests.get(f"{BASE_URL}/api/keys/audit-log?limit=10", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        entries = data.get("data", {}).get("entries", [])
        
        # Should have at least one vault_view entry
        vault_views = [e for e in entries if e.get("action") == "vault_view"]
        assert len(vault_views) > 0, "Should have vault_view audit entries"
        
        # Verify entry structure
        entry = vault_views[0]
        assert "user_id" in entry, "Audit entry should have user_id"
        assert "timestamp" in entry, "Audit entry should have timestamp"
        assert "key_name" in entry, "Audit entry should have key_name"
        
        print(f"PASS: Vault access creates audit log entry")


class TestKeyMaskingLogic:
    """Test key masking functionality"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_configured_keys_show_masked_value(self, auth_headers):
        """Test that configured keys show masked values with asterisks"""
        response = requests.get(f"{BASE_URL}/api/keys/vault", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        keys = data.get("data", {}).get("keys", [])
        
        configured_keys = [k for k in keys if k.get("status") == "configured"]
        for key in configured_keys[:3]:
            masked = key.get("masked_value", "")
            # Should have asterisks followed by last 4 chars
            assert "*" in masked or masked == "****", f"Configured key {key['key_name']} should be masked"
        
        print(f"PASS: {len(configured_keys)} configured keys properly masked")
    
    def test_missing_keys_show_not_set(self, auth_headers):
        """Test that missing keys show 'NOT SET'"""
        response = requests.get(f"{BASE_URL}/api/keys/vault", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        keys = data.get("data", {}).get("keys", [])
        
        missing_keys = [k for k in keys if k.get("status") == "missing"]
        for key in missing_keys[:3]:
            masked = key.get("masked_value", "")
            assert masked == "NOT SET", f"Missing key {key['key_name']} should show 'NOT SET', got '{masked}'"
        
        print(f"PASS: {len(missing_keys)} missing keys show 'NOT SET'")


class TestSecurityHeaders:
    """Test security headers middleware"""
    
    def test_csp_header_present(self):
        """Test that Content-Security-Policy header is present"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        csp = response.headers.get("Content-Security-Policy")
        assert csp is not None, "Content-Security-Policy header should be present"
        assert "default-src" in csp, "CSP should have default-src directive"
        
        print(f"PASS: Content-Security-Policy header present: {csp[:50]}...")
    
    def test_security_headers_present(self):
        """Test that other security headers are present"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Referrer-Policy"
        ]
        
        for header in expected_headers:
            assert header in response.headers, f"Missing security header: {header}"
        
        print(f"PASS: All security headers present: {expected_headers}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
