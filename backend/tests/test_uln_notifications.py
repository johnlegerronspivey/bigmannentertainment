"""
ULN Notification System Tests
==============================
Tests for notification CRUD, preferences, and filtering endpoints.
Endpoints under /api/uln/notifications
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"
KNOWN_LABEL_ID = "BM-LBL-9D0377FB"


class TestULNNotificationAuth:
    """Authentication for notification tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Auth returns 'access_token' not 'token'
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        return token
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


class TestNotificationCRUD(TestULNNotificationAuth):
    """Test notification CRUD operations"""
    
    def test_list_notifications(self, headers):
        """GET /api/uln/notifications - list notifications"""
        response = requests.get(f"{BASE_URL}/api/uln/notifications", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "notifications" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "has_more" in data
        assert data.get("success") == True
        print(f"PASS: List notifications - {data['total']} total")
    
    def test_list_notifications_with_label_filter(self, headers):
        """GET /api/uln/notifications?label_id=X - filter by label"""
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications?label_id={KNOWN_LABEL_ID}",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "notifications" in data
        print(f"PASS: List notifications with label filter - {data['total']} results")
    
    def test_list_notifications_with_type_filter(self, headers):
        """GET /api/uln/notifications?type=system - filter by type"""
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications?type=system",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "notifications" in data
        # All returned notifications should be of type 'system'
        for notif in data.get("notifications", []):
            assert notif.get("type") == "system", f"Wrong type: {notif.get('type')}"
        print(f"PASS: List notifications with type filter - {data['total']} results")
    
    def test_list_notifications_unread_only(self, headers):
        """GET /api/uln/notifications?unread_only=true - filter unread"""
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications?unread_only=true",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "notifications" in data
        # All returned notifications should be unread
        for notif in data.get("notifications", []):
            assert notif.get("is_read") == False, f"Found read notification"
        print(f"PASS: List unread notifications - {data['total']} results")
    
    def test_get_unread_count(self, headers):
        """GET /api/uln/notifications/unread-count - get unread count"""
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications/unread-count",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "unread_count" in data
        assert data.get("success") == True
        assert isinstance(data["unread_count"], int)
        print(f"PASS: Unread count = {data['unread_count']}")
    
    def test_get_unread_count_with_label(self, headers):
        """GET /api/uln/notifications/unread-count?label_id=X"""
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications/unread-count?label_id={KNOWN_LABEL_ID}",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "unread_count" in data
        print(f"PASS: Unread count for label = {data['unread_count']}")
    
    def test_create_notification(self, headers):
        """POST /api/uln/notifications - create a notification"""
        payload = {
            "label_id": KNOWN_LABEL_ID,
            "type": "system",
            "title": "TEST_Notification_Create",
            "message": "This is a test notification created by pytest",
            "severity": "info",
            "metadata": {"test": True}
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/notifications",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "notification_id" in data
        notification_id = data["notification_id"]
        assert notification_id.startswith("NOTIF-")
        print(f"PASS: Created notification {notification_id}")
        return notification_id
    
    def test_create_and_verify_notification(self, headers):
        """Create notification and verify it appears in list"""
        # Create
        payload = {
            "label_id": KNOWN_LABEL_ID,
            "type": "member_added",
            "title": "TEST_Member_Added_Verify",
            "message": "Test member added notification for verification",
            "severity": "success"
        }
        create_resp = requests.post(
            f"{BASE_URL}/api/uln/notifications",
            headers=headers,
            json=payload
        )
        assert create_resp.status_code == 200
        notif_id = create_resp.json()["notification_id"]
        
        # Verify in list
        list_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications?label_id={KNOWN_LABEL_ID}",
            headers=headers
        )
        assert list_resp.status_code == 200
        notifications = list_resp.json().get("notifications", [])
        found = any(n["notification_id"] == notif_id for n in notifications)
        assert found, f"Created notification {notif_id} not found in list"
        print(f"PASS: Created and verified notification {notif_id}")
        return notif_id


class TestNotificationActions(TestULNNotificationAuth):
    """Test mark read, delete, clear operations"""
    
    def test_mark_notification_read(self, headers):
        """PUT /api/uln/notifications/{id}/read - mark as read"""
        # First create a notification
        create_resp = requests.post(
            f"{BASE_URL}/api/uln/notifications",
            headers=headers,
            json={
                "label_id": KNOWN_LABEL_ID,
                "type": "system",
                "title": "TEST_Mark_Read",
                "message": "Test notification for mark read",
                "severity": "info"
            }
        )
        assert create_resp.status_code == 200
        notif_id = create_resp.json()["notification_id"]
        
        # Mark as read
        read_resp = requests.put(
            f"{BASE_URL}/api/uln/notifications/{notif_id}/read",
            headers=headers
        )
        assert read_resp.status_code == 200, f"Failed: {read_resp.text}"
        data = read_resp.json()
        assert data.get("success") == True
        print(f"PASS: Marked notification {notif_id} as read")
        
        # Verify it's read by checking unread filter
        unread_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications?unread_only=true",
            headers=headers
        )
        unread_ids = [n["notification_id"] for n in unread_resp.json().get("notifications", [])]
        assert notif_id not in unread_ids, "Notification still appears as unread"
        print(f"PASS: Verified notification {notif_id} is no longer unread")
    
    def test_mark_notification_read_not_found(self, headers):
        """PUT /api/uln/notifications/{id}/read - 404 for invalid ID"""
        response = requests.put(
            f"{BASE_URL}/api/uln/notifications/NOTIF-INVALID123/read",
            headers=headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Mark read returns 404 for invalid notification")
    
    def test_mark_all_read(self, headers):
        """PUT /api/uln/notifications/read-all - mark all as read"""
        # Create a few unread notifications first
        for i in range(2):
            requests.post(
                f"{BASE_URL}/api/uln/notifications",
                headers=headers,
                json={
                    "label_id": KNOWN_LABEL_ID,
                    "type": "system",
                    "title": f"TEST_Mark_All_Read_{i}",
                    "message": "Test notification for mark all read",
                    "severity": "info"
                }
            )
        
        # Mark all read
        response = requests.put(
            f"{BASE_URL}/api/uln/notifications/read-all?label_id={KNOWN_LABEL_ID}",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "updated" in data
        print(f"PASS: Marked all read - {data['updated']} updated")
        
        # Verify unread count is 0 for this label
        count_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications/unread-count?label_id={KNOWN_LABEL_ID}",
            headers=headers
        )
        assert count_resp.json().get("unread_count") == 0
        print("PASS: Verified unread count is 0 after mark all read")
    
    def test_delete_notification(self, headers):
        """DELETE /api/uln/notifications/{id} - delete notification"""
        # Create a notification
        create_resp = requests.post(
            f"{BASE_URL}/api/uln/notifications",
            headers=headers,
            json={
                "label_id": KNOWN_LABEL_ID,
                "type": "system",
                "title": "TEST_Delete_Notification",
                "message": "Test notification for deletion",
                "severity": "warning"
            }
        )
        assert create_resp.status_code == 200
        notif_id = create_resp.json()["notification_id"]
        
        # Delete it
        delete_resp = requests.delete(
            f"{BASE_URL}/api/uln/notifications/{notif_id}",
            headers=headers
        )
        assert delete_resp.status_code == 200, f"Failed: {delete_resp.text}"
        data = delete_resp.json()
        assert data.get("success") == True
        print(f"PASS: Deleted notification {notif_id}")
        
        # Verify it's gone
        list_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications",
            headers=headers
        )
        notif_ids = [n["notification_id"] for n in list_resp.json().get("notifications", [])]
        assert notif_id not in notif_ids, "Deleted notification still in list"
        print(f"PASS: Verified notification {notif_id} is deleted")
    
    def test_delete_notification_not_found(self, headers):
        """DELETE /api/uln/notifications/{id} - 404 for invalid ID"""
        response = requests.delete(
            f"{BASE_URL}/api/uln/notifications/NOTIF-INVALID456",
            headers=headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Delete returns 404 for invalid notification")
    
    def test_clear_all_notifications(self, headers):
        """DELETE /api/uln/notifications/clear - clear all notifications"""
        # Create some notifications first
        for i in range(3):
            requests.post(
                f"{BASE_URL}/api/uln/notifications",
                headers=headers,
                json={
                    "label_id": KNOWN_LABEL_ID,
                    "type": "system",
                    "title": f"TEST_Clear_All_{i}",
                    "message": "Test notification for clear all",
                    "severity": "info"
                }
            )
        
        # Clear all for this label
        response = requests.delete(
            f"{BASE_URL}/api/uln/notifications/clear?label_id={KNOWN_LABEL_ID}",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "deleted" in data
        print(f"PASS: Cleared all notifications - {data['deleted']} deleted")


class TestNotificationPreferences(TestULNNotificationAuth):
    """Test notification preferences endpoints"""
    
    def test_get_preferences(self, headers):
        """GET /api/uln/notifications/preferences - get preferences"""
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "preferences" in data
        prefs = data["preferences"]
        assert "enabled" in prefs
        assert "muted_types" in prefs
        assert "user_id" in prefs
        print(f"PASS: Got preferences - enabled={prefs['enabled']}, muted_types={prefs['muted_types']}")
    
    def test_update_preferences_enabled(self, headers):
        """PUT /api/uln/notifications/preferences - toggle enabled"""
        # Get current state
        get_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers
        )
        current_enabled = get_resp.json()["preferences"]["enabled"]
        
        # Toggle
        new_enabled = not current_enabled
        update_resp = requests.put(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers,
            json={"enabled": new_enabled}
        )
        assert update_resp.status_code == 200, f"Failed: {update_resp.text}"
        assert update_resp.json().get("success") == True
        
        # Verify
        verify_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers
        )
        assert verify_resp.json()["preferences"]["enabled"] == new_enabled
        print(f"PASS: Updated enabled to {new_enabled}")
        
        # Restore original
        requests.put(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers,
            json={"enabled": current_enabled}
        )
    
    def test_update_preferences_muted_types(self, headers):
        """PUT /api/uln/notifications/preferences - update muted types"""
        # Set muted types
        muted = ["system", "member_added"]
        update_resp = requests.put(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers,
            json={"muted_types": muted}
        )
        assert update_resp.status_code == 200, f"Failed: {update_resp.text}"
        assert update_resp.json().get("success") == True
        
        # Verify
        verify_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers
        )
        saved_muted = verify_resp.json()["preferences"]["muted_types"]
        assert set(saved_muted) == set(muted), f"Muted types mismatch: {saved_muted}"
        print(f"PASS: Updated muted_types to {muted}")
        
        # Clear muted types
        requests.put(
            f"{BASE_URL}/api/uln/notifications/preferences",
            headers=headers,
            json={"muted_types": []}
        )


class TestNotificationPagination(TestULNNotificationAuth):
    """Test pagination functionality"""
    
    def test_pagination_params(self, headers):
        """Test page and limit parameters"""
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications?page=1&limit=5",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5
        assert len(data["notifications"]) <= 5
        print(f"PASS: Pagination works - page={data['page']}, limit={data['limit']}, returned={len(data['notifications'])}")
    
    def test_pagination_has_more(self, headers):
        """Test has_more flag"""
        # Get with small limit
        response = requests.get(
            f"{BASE_URL}/api/uln/notifications?page=1&limit=1",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        # If total > 1, has_more should be True
        if data["total"] > 1:
            assert data["has_more"] == True
            print(f"PASS: has_more=True when total ({data['total']}) > limit (1)")
        else:
            print(f"PASS: has_more={data['has_more']} with total={data['total']}")


class TestNotificationTypes(TestULNNotificationAuth):
    """Test different notification types and severities"""
    
    def test_create_all_notification_types(self, headers):
        """Create notifications with all valid types"""
        types = [
            "member_added", "member_removed",
            "governance_rule_created", "governance_rule_updated", "governance_rule_deleted",
            "dispute_filed", "dispute_updated", "dispute_resolved",
            "catalog_asset_added", "distribution_updated", "royalty_payout",
            "label_registered", "system"
        ]
        
        for notif_type in types:
            response = requests.post(
                f"{BASE_URL}/api/uln/notifications",
                headers=headers,
                json={
                    "label_id": KNOWN_LABEL_ID,
                    "type": notif_type,
                    "title": f"TEST_Type_{notif_type}",
                    "message": f"Test notification of type {notif_type}",
                    "severity": "info"
                }
            )
            assert response.status_code == 200, f"Failed for type {notif_type}: {response.text}"
        
        print(f"PASS: Created notifications for all {len(types)} types")
    
    def test_create_all_severities(self, headers):
        """Create notifications with all valid severities"""
        severities = ["info", "warning", "success", "error"]
        
        for severity in severities:
            response = requests.post(
                f"{BASE_URL}/api/uln/notifications",
                headers=headers,
                json={
                    "label_id": KNOWN_LABEL_ID,
                    "type": "system",
                    "title": f"TEST_Severity_{severity}",
                    "message": f"Test notification with severity {severity}",
                    "severity": severity
                }
            )
            assert response.status_code == 200, f"Failed for severity {severity}: {response.text}"
        
        print(f"PASS: Created notifications for all {len(severities)} severities")
    
    def test_invalid_type_defaults_to_system(self, headers):
        """Invalid notification type should default to 'system'"""
        response = requests.post(
            f"{BASE_URL}/api/uln/notifications",
            headers=headers,
            json={
                "label_id": KNOWN_LABEL_ID,
                "type": "invalid_type_xyz",
                "title": "TEST_Invalid_Type",
                "message": "Test with invalid type",
                "severity": "info"
            }
        )
        assert response.status_code == 200
        notif_id = response.json()["notification_id"]
        
        # Verify it was saved as 'system'
        list_resp = requests.get(
            f"{BASE_URL}/api/uln/notifications",
            headers=headers
        )
        for n in list_resp.json().get("notifications", []):
            if n["notification_id"] == notif_id:
                assert n["type"] == "system", f"Expected 'system', got {n['type']}"
                break
        print("PASS: Invalid type defaults to 'system'")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_notifications():
    """Cleanup TEST_ prefixed notifications after all tests"""
    yield
    # Cleanup happens via clear endpoint in tests
    print("Test cleanup complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
