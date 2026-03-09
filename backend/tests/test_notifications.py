"""
Tests for Real-time Notifications Feature
- GET /api/notifications - list notifications with total and unread count
- GET /api/notifications/unread-count - returns unread count
- PUT /api/notifications/{id}/read - marks a single notification as read
- PUT /api/notifications/read-all - marks all notifications as read
- DELETE /api/notifications/{id} - deletes a notification
- POST /api/messages/send - triggers notification for recipient
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"
ADMIN_EMAIL = "cveadmin@test.com"
ADMIN_PASSWORD = "Test1234!"
ADMIN_USER_ID = "02493aff-49cd-4fd2-9554-0810eed7ad23"


@pytest.fixture(scope="module")
def owner_session():
    """Login as owner and return authenticated session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": OWNER_EMAIL,
        "password": OWNER_PASSWORD
    })
    
    if response.status_code != 200:
        pytest.skip(f"Owner login failed: {response.status_code} - {response.text}")
    
    data = response.json()
    token = data.get("access_token") or data.get("token")
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
    
    session.user_data = data.get("user", data)
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Login as admin and return authenticated session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    
    data = response.json()
    token = data.get("access_token") or data.get("token")
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
    
    session.user_data = data.get("user", data)
    return session


class TestNotificationEndpoints:
    """Test notification API endpoints"""
    
    def test_get_notifications_list(self, admin_session):
        """GET /api/notifications - returns notifications list with total and unread count"""
        response = admin_session.get(f"{BASE_URL}/api/notifications")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "items" in data, "Response should contain 'items' array"
        assert "total" in data, "Response should contain 'total' count"
        assert "unread" in data, "Response should contain 'unread' count"
        assert isinstance(data["items"], list), "'items' should be a list"
        assert isinstance(data["total"], int), "'total' should be an integer"
        assert isinstance(data["unread"], int), "'unread' should be an integer"
        print(f"Got {len(data['items'])} notifications, total={data['total']}, unread={data['unread']}")
    
    def test_get_notifications_with_pagination(self, admin_session):
        """GET /api/notifications with skip and limit parameters"""
        response = admin_session.get(f"{BASE_URL}/api/notifications?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5, "Should respect limit parameter"
    
    def test_get_notifications_unread_only(self, admin_session):
        """GET /api/notifications?unread_only=true - returns only unread notifications"""
        response = admin_session.get(f"{BASE_URL}/api/notifications?unread_only=true")
        
        assert response.status_code == 200
        data = response.json()
        # All returned items should be unread
        for item in data["items"]:
            assert item.get("read") == False, "Unread filter should return only unread notifications"
    
    def test_get_unread_count(self, admin_session):
        """GET /api/notifications/unread-count - returns unread count"""
        response = admin_session.get(f"{BASE_URL}/api/notifications/unread-count")
        
        assert response.status_code == 200
        data = response.json()
        assert "unread" in data, "Response should contain 'unread' key"
        assert isinstance(data["unread"], int), "'unread' should be an integer"
        print(f"Unread count: {data['unread']}")


class TestNotificationActions:
    """Test notification mark read and delete actions"""
    
    def test_mark_notification_read(self, admin_session):
        """PUT /api/notifications/{id}/read - marks a single notification as read"""
        # First get list of notifications
        list_response = admin_session.get(f"{BASE_URL}/api/notifications")
        assert list_response.status_code == 200
        data = list_response.json()
        
        if len(data["items"]) == 0:
            pytest.skip("No notifications to test mark read")
        
        # Find an unread notification if available, otherwise use first one
        notif = None
        for item in data["items"]:
            if not item.get("read"):
                notif = item
                break
        if not notif:
            notif = data["items"][0]
        
        notif_id = notif["id"]
        
        # Mark as read
        response = admin_session.put(f"{BASE_URL}/api/notifications/{notif_id}/read")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert "message" in result, "Response should contain 'message'"
        print(f"Marked notification {notif_id} as read")
    
    def test_mark_all_notifications_read(self, admin_session):
        """PUT /api/notifications/read-all - marks all notifications as read"""
        response = admin_session.put(f"{BASE_URL}/api/notifications/read-all")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert "message" in result, "Response should contain 'message'"
        
        # Verify all are now read
        verify_response = admin_session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert verify_response.status_code == 200
        assert verify_response.json()["unread"] == 0, "Unread count should be 0 after mark-all-read"
        print("Marked all notifications as read successfully")
    
    def test_mark_invalid_notification_read(self, admin_session):
        """PUT /api/notifications/{id}/read - returns 404 for non-existent notification"""
        response = admin_session.put(f"{BASE_URL}/api/notifications/000000000000000000000000/read")
        
        assert response.status_code == 404, f"Expected 404 for non-existent notification, got {response.status_code}"


class TestNotificationCreationViaMessaging:
    """Test that sending a message creates a notification for the recipient"""
    
    def test_send_message_creates_notification(self, owner_session, admin_session):
        """POST /api/messages/send - should create a notification for the recipient"""
        # Get owner user ID
        owner_id = owner_session.user_data.get("id") or owner_session.user_data.get("user_id")
        
        # Get admin's initial notification count
        initial_response = admin_session.get(f"{BASE_URL}/api/notifications")
        assert initial_response.status_code == 200
        initial_total = initial_response.json()["total"]
        
        # Send message from owner to admin
        test_message = f"TEST_Notification_Test_Message_{int(time.time())}"
        send_response = owner_session.post(f"{BASE_URL}/api/messages/send", json={
            "recipient_id": ADMIN_USER_ID,
            "content": test_message
        })
        
        assert send_response.status_code == 200, f"Message send failed: {send_response.status_code} - {send_response.text}"
        
        # Wait briefly for notification to be created
        time.sleep(0.5)
        
        # Verify admin has a new notification
        new_response = admin_session.get(f"{BASE_URL}/api/notifications")
        assert new_response.status_code == 200
        new_data = new_response.json()
        
        # Check that total increased
        assert new_data["total"] > initial_total, "Notification count should increase after message sent"
        
        # Verify the new notification exists and has correct type
        found_notif = None
        for notif in new_data["items"]:
            if notif.get("type") == "new_message" and test_message[:50] in notif.get("message", ""):
                found_notif = notif
                break
        
        assert found_notif is not None, "Should find the new message notification"
        assert found_notif["title"] == "New Message", "Notification title should be 'New Message'"
        assert found_notif["read"] == False, "New notification should be unread"
        print(f"Notification created successfully with id: {found_notif['id']}")


class TestNotificationDelete:
    """Test notification deletion"""
    
    def test_delete_notification(self, owner_session, admin_session):
        """DELETE /api/notifications/{id} - deletes a notification"""
        # First create a notification by sending a message
        test_message = f"TEST_Delete_Notification_{int(time.time())}"
        send_response = owner_session.post(f"{BASE_URL}/api/messages/send", json={
            "recipient_id": ADMIN_USER_ID,
            "content": test_message
        })
        
        if send_response.status_code != 200:
            pytest.skip("Could not create notification to delete")
        
        time.sleep(0.5)
        
        # Get the notification we just created
        list_response = admin_session.get(f"{BASE_URL}/api/notifications")
        assert list_response.status_code == 200
        data = list_response.json()
        
        # Find our test notification
        notif_to_delete = None
        for notif in data["items"]:
            if test_message[:50] in notif.get("message", ""):
                notif_to_delete = notif
                break
        
        if not notif_to_delete:
            pytest.skip("Could not find notification to delete")
        
        notif_id = notif_to_delete["id"]
        initial_total = data["total"]
        
        # Delete the notification
        delete_response = admin_session.delete(f"{BASE_URL}/api/notifications/{notif_id}")
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.status_code} - {delete_response.text}"
        
        result = delete_response.json()
        assert "message" in result, "Response should contain 'message'"
        
        # Verify it's deleted
        verify_response = admin_session.get(f"{BASE_URL}/api/notifications")
        assert verify_response.status_code == 200
        new_total = verify_response.json()["total"]
        
        assert new_total == initial_total - 1, "Total notifications should decrease by 1"
        
        # Verify notification is not in list anymore
        for notif in verify_response.json()["items"]:
            assert notif["id"] != notif_id, "Deleted notification should not appear in list"
        
        print(f"Successfully deleted notification {notif_id}")
    
    def test_delete_nonexistent_notification(self, admin_session):
        """DELETE /api/notifications/{id} - returns 404 for non-existent notification"""
        response = admin_session.delete(f"{BASE_URL}/api/notifications/000000000000000000000000")
        
        assert response.status_code == 404, f"Expected 404 for non-existent notification, got {response.status_code}"
    
    def test_delete_invalid_id(self, admin_session):
        """DELETE /api/notifications/{id} - returns 400 for invalid notification ID"""
        response = admin_session.delete(f"{BASE_URL}/api/notifications/invalid-id")
        
        assert response.status_code == 400, f"Expected 400 for invalid ID format, got {response.status_code}"


class TestNotificationDataValidation:
    """Test notification data structure and fields"""
    
    def test_notification_structure(self, admin_session):
        """Verify notification items have required fields"""
        response = admin_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["items"]) == 0:
            pytest.skip("No notifications to validate structure")
        
        notif = data["items"][0]
        
        # Check required fields
        assert "id" in notif, "Notification should have 'id'"
        assert "type" in notif, "Notification should have 'type'"
        assert "title" in notif, "Notification should have 'title'"
        assert "message" in notif, "Notification should have 'message'"
        assert "read" in notif, "Notification should have 'read'"
        assert "created_at" in notif, "Notification should have 'created_at'"
        
        print(f"Notification structure valid: {list(notif.keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
