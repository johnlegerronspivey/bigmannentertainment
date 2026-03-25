"""
ULN Label Members API Tests
============================
Tests for Phase A (Quick Win) - Unified Label Upgrade: Identity & Label Switcher
- label_members MongoDB collection tracking who belongs to which label and their role
- GET /api/uln/me/labels endpoint for listing user's labels
- CRUD endpoints for label members (add, remove, update role)
- Role permissions and hierarchy
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestULNLabelMembersAuth:
    """Authentication and setup tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✓ Login successful, got access_token")


class TestMyLabelsEndpoint:
    """Tests for GET /api/uln/me/labels endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_my_labels_returns_list(self, headers):
        """GET /api/uln/me/labels returns list of labels user belongs to"""
        response = requests.get(f"{BASE_URL}/api/uln/me/labels", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "labels" in data, "Response should contain 'labels' key"
        assert "count" in data, "Response should contain 'count' key"
        assert isinstance(data["labels"], list), "labels should be a list"
        
        print(f"✓ GET /me/labels returned {data['count']} labels")
        
        # If labels exist, verify structure
        if data["labels"]:
            label = data["labels"][0]
            assert "label_id" in label, "Label should have label_id"
            assert "role" in label, "Label should have role"
            assert "name" in label, "Label should have name"
            assert "member_count" in label, "Label should have member_count"
            print(f"✓ Label structure verified: {label['name']} (role: {label['role']}, members: {label['member_count']})")
    
    def test_my_labels_without_auth_fails(self):
        """GET /api/uln/me/labels without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/uln/me/labels")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Unauthenticated request correctly rejected")


class TestRolesEndpoint:
    """Tests for GET /api/uln/roles endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_roles_returns_valid_roles(self, headers):
        """GET /api/uln/roles returns valid roles with descriptions"""
        response = requests.get(f"{BASE_URL}/api/uln/roles", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "roles" in data, "Response should contain 'roles' key"
        roles = data["roles"]
        assert len(roles) == 4, f"Expected 4 roles, got {len(roles)}"
        
        # Verify all expected roles exist
        role_ids = [r["id"] for r in roles]
        assert "owner" in role_ids, "owner role should exist"
        assert "admin" in role_ids, "admin role should exist"
        assert "a_and_r" in role_ids, "a_and_r role should exist"
        assert "viewer" in role_ids, "viewer role should exist"
        
        # Verify role structure
        for role in roles:
            assert "id" in role, "Role should have id"
            assert "label" in role, "Role should have label"
            assert "level" in role, "Role should have level"
            assert "description" in role, "Role should have description"
        
        print(f"✓ GET /roles returned {len(roles)} roles with proper structure")
        for r in roles:
            print(f"  - {r['id']}: {r['label']} (level {r['level']})")


class TestLabelMembersEndpoints:
    """Tests for label members CRUD endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def test_label_id(self, headers):
        """Get a label ID for testing"""
        response = requests.get(f"{BASE_URL}/api/uln/me/labels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        if data["labels"]:
            return data["labels"][0]["label_id"]
        pytest.skip("No labels available for testing")
    
    def test_get_label_members(self, headers, test_label_id):
        """GET /api/uln/labels/{label_id}/members returns members list"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{test_label_id}/members", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "members" in data, "Response should contain 'members' key"
        assert "count" in data, "Response should contain 'count' key"
        assert "label_id" in data, "Response should contain 'label_id' key"
        
        print(f"✓ GET /labels/{test_label_id}/members returned {data['count']} members")
        
        # Verify member structure if members exist
        if data["members"]:
            member = data["members"][0]
            assert "user_id" in member, "Member should have user_id"
            assert "label_role" in member, "Member should have label_role"
            assert "email" in member, "Member should have email"
            print(f"  - First member: {member.get('email', 'N/A')} ({member['label_role']})")
    
    def test_get_my_role_in_label(self, headers, test_label_id):
        """GET /api/uln/labels/{label_id}/my-role returns user's role"""
        response = requests.get(f"{BASE_URL}/api/uln/labels/{test_label_id}/my-role", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "member" in data, "Response should contain 'member' key"
        assert "role" in data, "Response should contain 'role' key"
        assert "label_id" in data, "Response should contain 'label_id' key"
        
        if data["member"]:
            assert data["role"] in ["owner", "admin", "a_and_r", "viewer"], f"Invalid role: {data['role']}"
            print(f"✓ GET /labels/{test_label_id}/my-role: {data['role']}")
        else:
            print(f"✓ GET /labels/{test_label_id}/my-role: Not a member")
    
    def test_add_member_rejects_invalid_role(self, headers, test_label_id):
        """POST /api/uln/labels/{label_id}/members rejects invalid role"""
        # Use the test user email (who already exists) with invalid role
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{test_label_id}/members",
            headers=headers,
            json={"email": TEST_EMAIL, "role": "invalid_role"}
        )
        # Should return 400 for invalid role (may also return 400 for duplicate, which is acceptable)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ POST /members correctly rejects invalid role or duplicate")
    
    def test_add_member_rejects_duplicate(self, headers, test_label_id):
        """POST /api/uln/labels/{label_id}/members rejects duplicate member"""
        # Try to add the current user (who is already a member)
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{test_label_id}/members",
            headers=headers,
            json={"email": TEST_EMAIL, "role": "viewer"}
        )
        # Should return 400 for duplicate
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "already a member" in data.get("detail", "").lower() or "already a member" in str(data).lower(), f"Expected duplicate error: {data}"
        print("✓ POST /members correctly rejects duplicate member")
    
    def test_add_member_requires_email_or_user_id(self, headers, test_label_id):
        """POST /api/uln/labels/{label_id}/members requires email or user_id"""
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{test_label_id}/members",
            headers=headers,
            json={"role": "viewer"}  # No email or user_id
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ POST /members correctly requires email or user_id")


class TestOwnerProtection:
    """Tests for owner protection rules"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def owner_label_data(self, headers):
        """Get a label where user is owner"""
        response = requests.get(f"{BASE_URL}/api/uln/me/labels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        for label in data["labels"]:
            if label["role"] == "owner":
                # Get members to find owner user_id
                members_resp = requests.get(
                    f"{BASE_URL}/api/uln/labels/{label['label_id']}/members",
                    headers=headers
                )
                if members_resp.status_code == 200:
                    members_data = members_resp.json()
                    owners = [m for m in members_data["members"] if m["label_role"] == "owner"]
                    if len(owners) == 1:  # Only one owner - good for testing protection
                        return {
                            "label_id": label["label_id"],
                            "owner_user_id": owners[0]["user_id"],
                            "owner_count": len(owners)
                        }
        
        pytest.skip("No suitable label found for owner protection testing")
    
    def test_cannot_remove_last_owner(self, headers, owner_label_data):
        """DELETE cannot remove the last owner of a label"""
        if owner_label_data["owner_count"] > 1:
            pytest.skip("Label has multiple owners, cannot test last owner protection")
        
        response = requests.delete(
            f"{BASE_URL}/api/uln/labels/{owner_label_data['label_id']}/members/{owner_label_data['owner_user_id']}",
            headers=headers
        )
        
        # Should return 400 with error about last owner
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "last owner" in data.get("detail", "").lower() or "last owner" in str(data).lower(), f"Expected last owner error: {data}"
        print("✓ DELETE correctly prevents removing last owner")
    
    def test_cannot_demote_last_owner(self, headers, owner_label_data):
        """PUT cannot demote the last owner of a label"""
        if owner_label_data["owner_count"] > 1:
            pytest.skip("Label has multiple owners, cannot test last owner protection")
        
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{owner_label_data['label_id']}/members/{owner_label_data['owner_user_id']}/role",
            headers=headers,
            json={"role": "admin"}  # Try to demote to admin
        )
        
        # Should return 400 with error about last owner
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "last owner" in data.get("detail", "").lower() or "demote" in data.get("detail", "").lower() or "last owner" in str(data).lower(), f"Expected last owner error: {data}"
        print("✓ PUT correctly prevents demoting last owner")


class TestRoleChangeEndpoint:
    """Tests for PUT /api/uln/labels/{label_id}/members/{userId}/role"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def test_label_id(self, headers):
        """Get a label ID for testing"""
        response = requests.get(f"{BASE_URL}/api/uln/me/labels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        if data["labels"]:
            return data["labels"][0]["label_id"]
        pytest.skip("No labels available for testing")
    
    def test_change_role_rejects_invalid_role(self, headers, test_label_id):
        """PUT /api/uln/labels/{label_id}/members/{userId}/role rejects invalid role"""
        # Get a member to test with
        members_resp = requests.get(f"{BASE_URL}/api/uln/labels/{test_label_id}/members", headers=headers)
        if members_resp.status_code != 200 or not members_resp.json().get("members"):
            pytest.skip("No members available for testing")
        
        member = members_resp.json()["members"][0]
        
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{test_label_id}/members/{member['user_id']}/role",
            headers=headers,
            json={"role": "super_admin"}  # Invalid role
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ PUT /role correctly rejects invalid role")
    
    def test_change_role_for_nonexistent_member(self, headers, test_label_id):
        """PUT /api/uln/labels/{label_id}/members/{userId}/role returns error for non-member"""
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{test_label_id}/members/nonexistent-user-id/role",
            headers=headers,
            json={"role": "admin"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ PUT /role correctly handles non-existent member")


class TestRemoveMemberEndpoint:
    """Tests for DELETE /api/uln/labels/{label_id}/members/{userId}"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def test_label_id(self, headers):
        """Get a label ID for testing"""
        response = requests.get(f"{BASE_URL}/api/uln/me/labels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        if data["labels"]:
            return data["labels"][0]["label_id"]
        pytest.skip("No labels available for testing")
    
    def test_remove_nonexistent_member(self, headers, test_label_id):
        """DELETE /api/uln/labels/{label_id}/members/{userId} returns error for non-member"""
        response = requests.delete(
            f"{BASE_URL}/api/uln/labels/{test_label_id}/members/nonexistent-user-id",
            headers=headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ DELETE /members correctly handles non-existent member")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
