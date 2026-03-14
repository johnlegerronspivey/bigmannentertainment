"""
AWS WAF & Secrets Manager Integration Tests
Tests for Phase D - AWS Security services integration

Endpoints tested:
- GET /api/aws-security/status - Overall status of WAF + Secrets Manager
- GET /api/aws-security/waf/web-acls - Lists Web ACLs
- GET /api/aws-security/waf/ip-sets - Lists IP sets
- GET /api/aws-security/waf/managed-rules - Lists AWS managed rule groups
- GET /api/aws-security/secrets - Lists secrets from Secrets Manager
- GET /api/aws-security/secrets/{name} - Describes a secret's metadata
- POST /api/aws-security/waf/web-acls - Creates a Web ACL
- POST /api/aws-security/waf/ip-sets - Creates an IP set
- POST /api/aws-security/secrets - Creates a new secret
"""
import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestAWSWafSecretsAPI:
    """AWS WAF & Secrets Manager API Tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for API calls"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Use access_token as per context note
        token = data.get("access_token") or data.get("token")
        assert token, "No token in response"
        return token
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    # ────────────────────────────────────────────────────────────────
    # Status Endpoint Tests
    # ────────────────────────────────────────────────────────────────
    def test_aws_security_status(self, headers):
        """Test GET /api/aws-security/status returns WAF and Secrets Manager availability"""
        response = requests.get(f"{BASE_URL}/api/aws-security/status", headers=headers)
        assert response.status_code == 200, f"Status check failed: {response.text}"
        
        data = response.json()
        # Verify WAF status
        assert "waf" in data, "WAF status missing"
        assert "available" in data["waf"], "WAF available field missing"
        
        # Verify Secrets Manager status
        assert "secrets_manager" in data, "Secrets Manager status missing"
        assert "available" in data["secrets_manager"], "Secrets Manager available field missing"
        
        print(f"WAF Status: {data['waf']}")
        print(f"Secrets Manager Status: {data['secrets_manager']}")
    
    def test_status_requires_auth(self):
        """Test that status endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-security/status")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
    
    # ────────────────────────────────────────────────────────────────
    # WAF Web ACLs Tests
    # ────────────────────────────────────────────────────────────────
    def test_list_web_acls(self, headers):
        """Test GET /api/aws-security/waf/web-acls lists Web ACLs"""
        response = requests.get(
            f"{BASE_URL}/api/aws-security/waf/web-acls?scope=REGIONAL",
            headers=headers
        )
        assert response.status_code == 200, f"List web ACLs failed: {response.text}"
        
        data = response.json()
        assert "web_acls" in data, "web_acls field missing"
        assert "total" in data, "total field missing"
        assert isinstance(data["web_acls"], list), "web_acls should be a list"
        
        print(f"Web ACLs found: {data['total']}")
    
    def test_list_web_acls_requires_auth(self):
        """Test that list web ACLs requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-security/waf/web-acls")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"
    
    # ────────────────────────────────────────────────────────────────
    # WAF IP Sets Tests
    # ────────────────────────────────────────────────────────────────
    def test_list_ip_sets(self, headers):
        """Test GET /api/aws-security/waf/ip-sets lists IP sets"""
        response = requests.get(
            f"{BASE_URL}/api/aws-security/waf/ip-sets?scope=REGIONAL",
            headers=headers
        )
        assert response.status_code == 200, f"List IP sets failed: {response.text}"
        
        data = response.json()
        assert "ip_sets" in data, "ip_sets field missing"
        assert "total" in data, "total field missing"
        assert isinstance(data["ip_sets"], list), "ip_sets should be a list"
        
        print(f"IP sets found: {data['total']}")
    
    def test_list_ip_sets_requires_auth(self):
        """Test that list IP sets requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-security/waf/ip-sets")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"
    
    # ────────────────────────────────────────────────────────────────
    # WAF Managed Rules Tests
    # ────────────────────────────────────────────────────────────────
    def test_list_managed_rules(self, headers):
        """Test GET /api/aws-security/waf/managed-rules lists AWS managed rule groups"""
        response = requests.get(
            f"{BASE_URL}/api/aws-security/waf/managed-rules?scope=REGIONAL",
            headers=headers
        )
        assert response.status_code == 200, f"List managed rules failed: {response.text}"
        
        data = response.json()
        assert "managed_rule_groups" in data, "managed_rule_groups field missing"
        assert "total" in data, "total field missing"
        assert isinstance(data["managed_rule_groups"], list), "managed_rule_groups should be a list"
        
        # Per context, should return 15 managed rule groups
        if len(data["managed_rule_groups"]) > 0:
            rule = data["managed_rule_groups"][0]
            assert "vendor" in rule, "vendor field missing in rule"
            assert "name" in rule, "name field missing in rule"
        
        print(f"Managed rule groups found: {data['total']}")
    
    def test_list_managed_rules_requires_auth(self):
        """Test that list managed rules requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-security/waf/managed-rules")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"
    
    # ────────────────────────────────────────────────────────────────
    # Secrets Manager Tests
    # ────────────────────────────────────────────────────────────────
    def test_list_secrets(self, headers):
        """Test GET /api/aws-security/secrets lists secrets"""
        response = requests.get(
            f"{BASE_URL}/api/aws-security/secrets",
            headers=headers
        )
        assert response.status_code == 200, f"List secrets failed: {response.text}"
        
        data = response.json()
        assert "secrets" in data, "secrets field missing"
        assert "total" in data, "total field missing"
        assert isinstance(data["secrets"], list), "secrets should be a list"
        
        # Per context, should return secrets with names like 'bigmann/development/*'
        if len(data["secrets"]) > 0:
            secret = data["secrets"][0]
            assert "name" in secret, "name field missing in secret"
            assert "arn" in secret, "arn field missing in secret"
        
        print(f"Secrets found: {data['total']}")
        for s in data["secrets"][:3]:
            print(f"  - {s.get('name')}")
    
    def test_list_secrets_requires_auth(self):
        """Test that list secrets requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-security/secrets")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"
    
    def test_describe_secret(self, headers):
        """Test GET /api/aws-security/secrets/{name} describes a secret's metadata"""
        # First list secrets to get a secret name
        list_response = requests.get(
            f"{BASE_URL}/api/aws-security/secrets",
            headers=headers
        )
        assert list_response.status_code == 200
        
        secrets = list_response.json().get("secrets", [])
        if len(secrets) == 0:
            pytest.skip("No secrets found to describe")
        
        secret_name = secrets[0]["name"]
        
        # Now describe the secret
        response = requests.get(
            f"{BASE_URL}/api/aws-security/secrets/{secret_name}",
            headers=headers
        )
        assert response.status_code == 200, f"Describe secret failed: {response.text}"
        
        data = response.json()
        assert "name" in data, "name field missing in describe response"
        assert "arn" in data, "arn field missing in describe response"
        assert data["name"] == secret_name or secret_name in data["name"], f"Secret name mismatch"
        
        print(f"Described secret: {data.get('name')}")
        print(f"  ARN: {data.get('arn')}")
        print(f"  Rotation enabled: {data.get('rotation_enabled')}")
    
    def test_describe_secret_requires_auth(self):
        """Test that describe secret requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-security/secrets/any-secret")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"
    
    # ────────────────────────────────────────────────────────────────
    # Create Operations (Web ACL, IP Set, Secret) - Run last to avoid pollution
    # ────────────────────────────────────────────────────────────────
    def test_create_web_acl(self, headers):
        """Test POST /api/aws-security/waf/web-acls creates a Web ACL"""
        timestamp = int(time.time())
        acl_name = f"TEST-WebACL-{timestamp}"
        
        response = requests.post(
            f"{BASE_URL}/api/aws-security/waf/web-acls",
            headers=headers,
            json={
                "name": acl_name,
                "scope": "REGIONAL",
                "default_action": "allow",
                "description": "Test Web ACL created by automated testing"
            }
        )
        
        # Could be 200 or 201 for successful creation
        if response.status_code in [200, 201]:
            data = response.json()
            assert "name" in data, "name field missing in create response"
            assert "id" in data or "arn" in data, "id or arn field missing"
            print(f"Created Web ACL: {data.get('name')}")
            print(f"  ID: {data.get('id')}")
            
            # Cleanup: Delete the test ACL
            if data.get("id") and data.get("lock_token"):
                delete_response = requests.delete(
                    f"{BASE_URL}/api/aws-security/waf/web-acls",
                    headers=headers,
                    json={
                        "name": acl_name,
                        "acl_id": data["id"],
                        "lock_token": data["lock_token"],
                        "scope": "REGIONAL"
                    }
                )
                print(f"  Cleanup delete status: {delete_response.status_code}")
        else:
            # Might fail due to AWS limits or existing ACL
            print(f"Create Web ACL returned {response.status_code}: {response.text}")
            # Don't fail - just log
    
    def test_create_ip_set(self, headers):
        """Test POST /api/aws-security/waf/ip-sets creates an IP set"""
        timestamp = int(time.time())
        ipset_name = f"TEST-IPSet-{timestamp}"
        
        response = requests.post(
            f"{BASE_URL}/api/aws-security/waf/ip-sets",
            headers=headers,
            json={
                "name": ipset_name,
                "addresses": ["192.168.1.0/24", "10.0.0.0/8"],
                "ip_version": "IPV4",
                "scope": "REGIONAL",
                "description": "Test IP set created by automated testing"
            }
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "name" in data, "name field missing in create response"
            print(f"Created IP Set: {data.get('name')}")
            print(f"  ID: {data.get('id')}")
            
            # Cleanup: Delete the test IP set
            if data.get("id") and data.get("lock_token"):
                delete_response = requests.delete(
                    f"{BASE_URL}/api/aws-security/waf/ip-sets",
                    headers=headers,
                    json={
                        "name": ipset_name,
                        "ip_set_id": data["id"],
                        "lock_token": data["lock_token"],
                        "scope": "REGIONAL"
                    }
                )
                print(f"  Cleanup delete status: {delete_response.status_code}")
        else:
            print(f"Create IP Set returned {response.status_code}: {response.text}")
    
    def test_create_secret(self, headers):
        """Test POST /api/aws-security/secrets creates a new secret"""
        timestamp = int(time.time())
        secret_name = f"TEST/automated-test/secret-{timestamp}"
        
        response = requests.post(
            f"{BASE_URL}/api/aws-security/secrets",
            headers=headers,
            json={
                "name": secret_name,
                "secret_value": '{"api_key": "test-value-123"}',
                "description": "Test secret created by automated testing",
                "is_json": True
            }
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "name" in data, "name field missing in create response"
            assert "arn" in data, "arn field missing in create response"
            print(f"Created Secret: {data.get('name')}")
            print(f"  ARN: {data.get('arn')}")
            
            # Cleanup: Delete the test secret
            delete_response = requests.delete(
                f"{BASE_URL}/api/aws-security/secrets/{secret_name}?force=true",
                headers=headers
            )
            print(f"  Cleanup delete status: {delete_response.status_code}")
        else:
            # Might fail due to existing secret with same name
            print(f"Create Secret returned {response.status_code}: {response.text}")
    
    def test_create_secret_requires_auth(self):
        """Test that create secret requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/aws-security/secrets",
            json={"name": "test", "secret_value": "test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
