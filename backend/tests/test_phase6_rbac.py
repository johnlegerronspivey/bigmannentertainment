"""
Phase 6: RBAC (Role-Based Access Control) API Tests
Tests for User Management & Role-Based Permissions for CVE Management Platform
Roles: Admin, Manager, Analyst
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials - first user becomes admin
TEST_EMAIL = "enterprise@test.com"
TEST_PASSWORD = "TestPass123!"


class TestRBACRoles:
    """Test GET /api/cve/rbac/roles - Returns all 3 roles with permissions (no auth required)"""

    def test_get_roles_returns_all_roles(self):
        """GET /api/cve/rbac/roles should return admin, manager, analyst roles"""
        response = requests.get(f"{BASE_URL}/api/cve/rbac/roles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "roles" in data, "Response should contain 'roles' key"
        
        roles = data["roles"]
        assert "admin" in roles, "Should have admin role"
        assert "manager" in roles, "Should have manager role"
        assert "analyst" in roles, "Should have analyst role"
        print(f"✓ GET /api/cve/rbac/roles - All 3 roles present")

    def test_admin_role_has_user_permissions(self):
        """Admin role should have users.view and users.manage permissions"""
        response = requests.get(f"{BASE_URL}/api/cve/rbac/roles")
        assert response.status_code == 200
        
        admin = response.json()["roles"]["admin"]
        assert "permissions" in admin, "Admin should have permissions list"
        assert "users.view" in admin["permissions"], "Admin should have users.view"
        assert "users.manage" in admin["permissions"], "Admin should have users.manage"
        assert admin["label"] == "Admin", "Admin label should be 'Admin'"
        print(f"✓ Admin role has correct permissions: {len(admin['permissions'])} total")

    def test_manager_role_permissions(self):
        """Manager role should have CVE and scan permissions but NOT user management"""
        response = requests.get(f"{BASE_URL}/api/cve/rbac/roles")
        assert response.status_code == 200
        
        manager = response.json()["roles"]["manager"]
        assert "cves.view" in manager["permissions"], "Manager should view CVEs"
        assert "cves.edit" in manager["permissions"], "Manager should edit CVEs"
        assert "scans.run" in manager["permissions"], "Manager should run scans"
        assert "users.view" not in manager["permissions"], "Manager should NOT have users.view"
        assert "users.manage" not in manager["permissions"], "Manager should NOT have users.manage"
        print(f"✓ Manager role has correct permissions: {len(manager['permissions'])} total")

    def test_analyst_role_limited_permissions(self):
        """Analyst should have read-mostly access with scan capability"""
        response = requests.get(f"{BASE_URL}/api/cve/rbac/roles")
        assert response.status_code == 200
        
        analyst = response.json()["roles"]["analyst"]
        assert "cves.view" in analyst["permissions"], "Analyst should view CVEs"
        assert "scans.run" in analyst["permissions"], "Analyst should run scans"
        assert "cves.delete" not in analyst["permissions"], "Analyst should NOT delete CVEs"
        assert "users.view" not in analyst["permissions"], "Analyst should NOT view users"
        print(f"✓ Analyst role has correct permissions: {len(analyst['permissions'])} total")


class TestRBACAuthentication:
    """Tests requiring authentication"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get authentication token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
        
        self.token = response.json()["access_token"]
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        print(f"✓ Authenticated as {TEST_EMAIL}")


class TestRBACMe(TestRBACAuthentication):
    """Test GET /api/cve/rbac/me - Returns current user's CVE role & permissions"""

    def test_get_my_profile_returns_role_and_permissions(self):
        """GET /api/cve/rbac/me should return user's CVE profile"""
        response = requests.get(
            f"{BASE_URL}/api/cve/rbac/me",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "user_id" in data, "Should have user_id"
        assert "email" in data, "Should have email"
        assert "cve_role" in data, "Should have cve_role"
        assert "permissions" in data, "Should have permissions list"
        assert "is_active" in data, "Should have is_active status"
        
        # First user is auto-provisioned as admin
        assert data["cve_role"] in ["admin", "manager", "analyst"], f"Invalid role: {data['cve_role']}"
        assert isinstance(data["permissions"], list), "Permissions should be a list"
        print(f"✓ GET /api/cve/rbac/me - User role: {data['cve_role']}, permissions: {len(data['permissions'])}")

    def test_me_requires_authentication(self):
        """GET /api/cve/rbac/me without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/cve/rbac/me")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ /api/cve/rbac/me correctly requires authentication")


class TestRBACUsers(TestRBACAuthentication):
    """Test /api/cve/rbac/users endpoints (admin only)"""

    def test_list_users_admin_only(self):
        """GET /api/cve/rbac/users should list all CVE platform users"""
        response = requests.get(
            f"{BASE_URL}/api/cve/rbac/users",
            headers=self.headers
        )
        
        # First user is admin, should succeed
        if response.status_code == 403:
            pytest.skip("Current user is not admin - skipping admin-only test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "users" in data, "Should have 'users' list"
        assert "total" in data, "Should have 'total' count"
        assert isinstance(data["users"], list), "Users should be a list"
        
        if len(data["users"]) > 0:
            user = data["users"][0]
            assert "user_id" in user, "User should have user_id"
            assert "email" in user, "User should have email"
            assert "cve_role" in user, "User should have cve_role"
            assert "is_active" in user, "User should have is_active"
        
        print(f"✓ GET /api/cve/rbac/users - Found {data['total']} users")

    def test_list_users_requires_auth(self):
        """GET /api/cve/rbac/users without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/cve/rbac/users")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ /api/cve/rbac/users correctly requires authentication")


class TestRBACInviteUser(TestRBACAuthentication):
    """Test POST /api/cve/rbac/users/invite (admin only)"""

    def test_invite_user_creates_cve_user(self):
        """POST /api/cve/rbac/users/invite should create a new CVE platform user"""
        test_email = f"test_invite_{int(time.time())}@example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={
                "email": test_email,
                "full_name": "Test Invite User",
                "role": "analyst"
            }
        )
        
        if response.status_code == 403:
            pytest.skip("Current user is not admin - skipping admin-only test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["email"] == test_email, f"Email should match: {data.get('email')} != {test_email}"
        assert data["full_name"] == "Test Invite User", "Full name should match"
        assert data["cve_role"] == "analyst", f"Role should be analyst, got {data.get('cve_role')}"
        assert data["is_active"] == True, "New user should be active"
        print(f"✓ POST /api/cve/rbac/users/invite - Created user: {test_email}")

    def test_invite_user_invalid_role(self):
        """POST /api/cve/rbac/users/invite with invalid role should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={
                "email": "invalid_role@example.com",
                "full_name": "Test Invalid Role",
                "role": "superuser"  # Invalid role
            }
        )
        
        if response.status_code == 403:
            pytest.skip("Current user is not admin")
        
        assert response.status_code == 400, f"Expected 400 for invalid role, got {response.status_code}"
        print("✓ Invalid role correctly rejected with 400")

    def test_invite_duplicate_email(self):
        """POST /api/cve/rbac/users/invite with existing email should return 400"""
        # First, invite a user
        test_email = f"test_dup_{int(time.time())}@example.com"
        
        response1 = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={"email": test_email, "full_name": "Test Dup", "role": "analyst"}
        )
        
        if response1.status_code == 403:
            pytest.skip("Current user is not admin")
        
        assert response1.status_code == 200
        
        # Try to invite again with same email
        response2 = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={"email": test_email, "full_name": "Test Dup 2", "role": "manager"}
        )
        
        assert response2.status_code == 400, f"Expected 400 for duplicate email, got {response2.status_code}"
        print("✓ Duplicate email correctly rejected with 400")


class TestRBACUpdateUserRole(TestRBACAuthentication):
    """Test PUT /api/cve/rbac/users/{user_id}/role (admin only)"""

    def test_change_user_role(self):
        """PUT /api/cve/rbac/users/{user_id}/role should change user's role"""
        # First create a test user to modify
        test_email = f"test_role_change_{int(time.time())}@example.com"
        
        create_resp = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={"email": test_email, "full_name": "Test Role Change", "role": "analyst"}
        )
        
        if create_resp.status_code == 403:
            pytest.skip("Current user is not admin")
        
        assert create_resp.status_code == 200
        user_id = create_resp.json()["user_id"]
        
        # Change role to manager
        response = requests.put(
            f"{BASE_URL}/api/cve/rbac/users/{user_id}/role",
            headers=self.headers,
            json={"role": "manager"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["cve_role"] == "manager", f"Role should be manager, got {data.get('cve_role')}"
        print(f"✓ PUT /api/cve/rbac/users/{user_id}/role - Changed to manager")

    def test_change_role_invalid_role(self):
        """PUT /api/cve/rbac/users/{user_id}/role with invalid role should return 400"""
        # Create test user
        test_email = f"test_invalid_role_{int(time.time())}@example.com"
        
        create_resp = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={"email": test_email, "full_name": "Test Invalid", "role": "analyst"}
        )
        
        if create_resp.status_code == 403:
            pytest.skip("Current user is not admin")
        
        user_id = create_resp.json()["user_id"]
        
        # Try invalid role
        response = requests.put(
            f"{BASE_URL}/api/cve/rbac/users/{user_id}/role",
            headers=self.headers,
            json={"role": "superadmin"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid role change correctly rejected")


class TestRBACUpdateUserStatus(TestRBACAuthentication):
    """Test PUT /api/cve/rbac/users/{user_id}/status (admin only)"""

    def test_deactivate_user(self):
        """PUT /api/cve/rbac/users/{user_id}/status should deactivate user"""
        # Create test user
        test_email = f"test_deactivate_{int(time.time())}@example.com"
        
        create_resp = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={"email": test_email, "full_name": "Test Deactivate", "role": "analyst"}
        )
        
        if create_resp.status_code == 403:
            pytest.skip("Current user is not admin")
        
        user_id = create_resp.json()["user_id"]
        
        # Deactivate
        response = requests.put(
            f"{BASE_URL}/api/cve/rbac/users/{user_id}/status",
            headers=self.headers,
            json={"is_active": False}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert response.json()["is_active"] == False, "User should be inactive"
        print(f"✓ PUT /api/cve/rbac/users/{user_id}/status - Deactivated user")

    def test_reactivate_user(self):
        """PUT /api/cve/rbac/users/{user_id}/status should reactivate user"""
        # Create and deactivate test user
        test_email = f"test_reactivate_{int(time.time())}@example.com"
        
        create_resp = requests.post(
            f"{BASE_URL}/api/cve/rbac/users/invite",
            headers=self.headers,
            json={"email": test_email, "full_name": "Test Reactivate", "role": "analyst"}
        )
        
        if create_resp.status_code == 403:
            pytest.skip("Current user is not admin")
        
        user_id = create_resp.json()["user_id"]
        
        # Deactivate first
        requests.put(
            f"{BASE_URL}/api/cve/rbac/users/{user_id}/status",
            headers=self.headers,
            json={"is_active": False}
        )
        
        # Reactivate
        response = requests.put(
            f"{BASE_URL}/api/cve/rbac/users/{user_id}/status",
            headers=self.headers,
            json={"is_active": True}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json()["is_active"] == True, "User should be active"
        print("✓ User reactivated successfully")

    def test_cannot_deactivate_self(self):
        """PUT /api/cve/rbac/users/{user_id}/status should not allow self-deactivation"""
        # Get current user's ID
        me_resp = requests.get(f"{BASE_URL}/api/cve/rbac/me", headers=self.headers)
        
        if me_resp.status_code != 200:
            pytest.skip("Could not get current user")
        
        my_user_id = me_resp.json()["user_id"]
        
        # Try to deactivate self
        response = requests.put(
            f"{BASE_URL}/api/cve/rbac/users/{my_user_id}/status",
            headers=self.headers,
            json={"is_active": False}
        )
        
        assert response.status_code == 400, f"Expected 400 for self-deactivation, got {response.status_code}"
        print("✓ Self-deactivation correctly prevented")


class TestRBACPermissionEnforcement(TestRBACAuthentication):
    """Test that permission checks work correctly"""

    def test_admin_has_all_permissions(self):
        """Admin should have all CVE-related permissions"""
        # Get my profile
        response = requests.get(f"{BASE_URL}/api/cve/rbac/me", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # If admin, check all key permissions
        if data["cve_role"] == "admin":
            expected_perms = ["users.view", "users.manage", "cves.view", "cves.create", "scans.run"]
            for perm in expected_perms:
                assert perm in data["permissions"], f"Admin should have {perm}"
            print(f"✓ Admin has all expected permissions ({len(data['permissions'])} total)")
        else:
            print(f"⚠ Current user is {data['cve_role']}, not admin - permission check limited")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
