"""
Phase 5 Notification & Reporting API Tests
Tests all endpoints for:
- Notification CRUD operations
- SLA compliance checks
- Notification preferences
- Email sending (test email, weekly digest)
- CSV report exports
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cve-remediation.preview.emergentagent.com")
NOTIFICATION_API = f"{BASE_URL}/api/cve/notifications"
REPORTS_API = f"{BASE_URL}/api/cve/reports"


class TestNotificationEndpoints:
    """Tests for notification CRUD operations"""

    def test_list_notifications(self):
        """GET /api/cve/notifications - List notifications with pagination"""
        response = requests.get(f"{NOTIFICATION_API}")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "notifications" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "pages" in data
        assert isinstance(data["notifications"], list)

    def test_list_notifications_with_filters(self):
        """GET /api/cve/notifications with query params"""
        # Test with unread_only filter
        response = requests.get(f"{NOTIFICATION_API}?unread_only=true")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        
        # Test with type filter
        response = requests.get(f"{NOTIFICATION_API}?type=sla_warning")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        
        # Test pagination
        response = requests.get(f"{NOTIFICATION_API}?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10

    def test_get_unread_count(self):
        """GET /api/cve/notifications/unread-count"""
        response = requests.get(f"{NOTIFICATION_API}/unread-count")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "unread" in data
        assert "by_type" in data
        assert isinstance(data["unread"], int)
        assert isinstance(data["by_type"], dict)

    def test_create_notification(self):
        """POST /api/cve/notifications - Create a new notification"""
        test_id = uuid.uuid4().hex[:8]
        payload = {
            "type": "new_cve",
            "title": f"TEST_Notification_{test_id}",
            "message": f"Test notification message {test_id}",
            "severity": "high",
            "cve_id": f"CVE-2026-TEST{test_id}",
            "send_email": False
        }
        
        response = requests.post(
            f"{NOTIFICATION_API}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate created notification structure
        assert "id" in data
        assert data["type"] == "new_cve"
        assert data["title"] == payload["title"]
        assert data["message"] == payload["message"]
        assert data["severity"] == "high"
        assert data["cve_id"] == payload["cve_id"]
        assert data["read"] == False
        assert data["dismissed"] == False
        assert "created_at" in data
        
        # Store for cleanup
        return data["id"]

    def test_create_notification_all_types(self):
        """Test creating notifications of all supported types"""
        notification_types = [
            "new_cve", "cve_assigned", "sla_warning", "sla_breach",
            "status_change", "remediation_update", "scan_complete", "weekly_digest"
        ]
        
        created_ids = []
        for ntype in notification_types:
            test_id = uuid.uuid4().hex[:6]
            payload = {
                "type": ntype,
                "title": f"TEST_{ntype}_{test_id}",
                "message": f"Test {ntype} message",
                "severity": "info"
            }
            response = requests.post(f"{NOTIFICATION_API}", json=payload)
            assert response.status_code == 200, f"Failed to create {ntype} notification"
            data = response.json()
            assert data["type"] == ntype
            created_ids.append(data["id"])
        
        return created_ids

    def test_mark_notification_read(self):
        """PUT /api/cve/notifications/{id}/read - Mark notification as read"""
        # First create a notification
        test_id = uuid.uuid4().hex[:8]
        create_payload = {
            "type": "new_cve",
            "title": f"TEST_MarkRead_{test_id}",
            "message": "To be marked as read",
            "severity": "low"
        }
        create_response = requests.post(f"{NOTIFICATION_API}", json=create_payload)
        notification_id = create_response.json()["id"]
        
        # Mark it as read
        response = requests.put(f"{NOTIFICATION_API}/{notification_id}/read")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        # Verify it's marked as read in the list
        list_response = requests.get(f"{NOTIFICATION_API}")
        notifications = list_response.json()["notifications"]
        found = next((n for n in notifications if n["id"] == notification_id), None)
        if found:
            assert found["read"] == True

    def test_mark_all_read(self):
        """PUT /api/cve/notifications/read-all - Mark all notifications as read"""
        # Create multiple unread notifications
        for i in range(2):
            requests.post(f"{NOTIFICATION_API}", json={
                "type": "sla_warning",
                "title": f"TEST_MarkAllRead_{i}",
                "message": f"Unread notification {i}",
                "severity": "medium"
            })
        
        # Check there are unread notifications
        unread_before = requests.get(f"{NOTIFICATION_API}/unread-count").json()["unread"]
        
        # Mark all as read
        response = requests.put(f"{NOTIFICATION_API}/read-all")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "marked" in data
        
        # Verify unread count is now 0
        unread_after = requests.get(f"{NOTIFICATION_API}/unread-count").json()["unread"]
        assert unread_after == 0

    def test_dismiss_notification(self):
        """DELETE /api/cve/notifications/{id} - Dismiss notification"""
        # First create a notification
        test_id = uuid.uuid4().hex[:8]
        create_payload = {
            "type": "new_cve",
            "title": f"TEST_Dismiss_{test_id}",
            "message": "To be dismissed",
            "severity": "low"
        }
        create_response = requests.post(f"{NOTIFICATION_API}", json=create_payload)
        notification_id = create_response.json()["id"]
        
        # Dismiss it
        response = requests.delete(f"{NOTIFICATION_API}/{notification_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        # Verify it's no longer in the list (dismissed notifications are filtered out)
        list_response = requests.get(f"{NOTIFICATION_API}")
        notifications = list_response.json()["notifications"]
        found = next((n for n in notifications if n["id"] == notification_id), None)
        assert found is None, "Dismissed notification should not appear in list"


class TestSLACompliance:
    """Tests for SLA check endpoint"""

    def test_check_sla_compliance(self):
        """POST /api/cve/notifications/check-sla - Run SLA compliance check"""
        response = requests.post(f"{NOTIFICATION_API}/check-sla")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "checked" in data
        assert "warnings" in data
        assert "breaches" in data
        assert "warning_details" in data
        assert "breach_details" in data
        
        assert isinstance(data["checked"], int)
        assert isinstance(data["warnings"], int)
        assert isinstance(data["breaches"], int)
        assert isinstance(data["warning_details"], list)
        assert isinstance(data["breach_details"], list)


class TestNotificationPreferences:
    """Tests for notification preferences endpoints"""

    def test_get_preferences(self):
        """GET /api/cve/notifications/preferences - Get notification preferences"""
        response = requests.get(f"{NOTIFICATION_API}/preferences")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "id" in data
        assert "email_enabled" in data
        assert "email_recipient" in data
        assert "email_types" in data
        assert "sla_warning_threshold" in data
        
        assert isinstance(data["email_types"], dict)
        # Verify all notification types are present
        expected_types = ["new_cve", "cve_assigned", "sla_warning", "sla_breach", 
                        "status_change", "remediation_update", "scan_complete", "weekly_digest"]
        for etype in expected_types:
            assert etype in data["email_types"]

    def test_update_preferences(self):
        """PUT /api/cve/notifications/preferences - Update notification preferences"""
        # First get current preferences
        current = requests.get(f"{NOTIFICATION_API}/preferences").json()
        original_threshold = current.get("sla_warning_threshold", 75)
        
        # Update threshold
        new_threshold = 85 if original_threshold != 85 else 90
        response = requests.put(
            f"{NOTIFICATION_API}/preferences",
            json={"sla_warning_threshold": new_threshold}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sla_warning_threshold"] == new_threshold
        
        # Verify persistence by fetching again
        verify = requests.get(f"{NOTIFICATION_API}/preferences").json()
        assert verify["sla_warning_threshold"] == new_threshold
        
        # Restore original
        requests.put(f"{NOTIFICATION_API}/preferences", json={"sla_warning_threshold": original_threshold})

    def test_update_email_enabled(self):
        """Test toggling email_enabled preference"""
        # Get current state
        current = requests.get(f"{NOTIFICATION_API}/preferences").json()
        original = current.get("email_enabled", True)
        
        # Toggle it
        new_value = not original
        response = requests.put(
            f"{NOTIFICATION_API}/preferences",
            json={"email_enabled": new_value}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email_enabled"] == new_value
        
        # Restore original
        requests.put(f"{NOTIFICATION_API}/preferences", json={"email_enabled": original})

    def test_update_email_types(self):
        """Test updating email_types preferences"""
        # Get current state
        current = requests.get(f"{NOTIFICATION_API}/preferences").json()
        original_types = current.get("email_types", {})
        
        # Update one type
        new_types = {**original_types, "scan_complete": not original_types.get("scan_complete", True)}
        response = requests.put(
            f"{NOTIFICATION_API}/preferences",
            json={"email_types": new_types}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email_types"]["scan_complete"] == new_types["scan_complete"]
        
        # Restore original
        requests.put(f"{NOTIFICATION_API}/preferences", json={"email_types": original_types})


class TestEmailEndpoints:
    """Tests for email-related endpoints"""

    def test_send_test_email(self):
        """POST /api/cve/notifications/test-email - Send test email via Resend"""
        response = requests.post(
            f"{NOTIFICATION_API}/test-email",
            json={},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Response should indicate sent status
        assert "sent" in data
        if data["sent"]:
            assert "email_id" in data
            assert "recipient" in data
        else:
            # If not sent, should have an error reason
            assert "error" in data

    def test_generate_weekly_digest(self):
        """POST /api/cve/notifications/weekly-digest - Generate and send weekly security digest"""
        response = requests.post(f"{NOTIFICATION_API}/weekly-digest")
        assert response.status_code == 200
        data = response.json()
        
        # Validate digest response structure
        assert "period" in data
        assert "new_cves" in data
        assert "fixed_cves" in data
        assert "open_cves" in data
        assert "critical_open" in data
        assert "high_open" in data
        assert "sla_warnings" in data
        assert "sla_breaches" in data
        assert "generated_at" in data
        
        # All counts should be integers
        assert isinstance(data["new_cves"], int)
        assert isinstance(data["fixed_cves"], int)
        assert isinstance(data["open_cves"], int)
        assert isinstance(data["critical_open"], int)


class TestReportExports:
    """Tests for CSV report export endpoints"""

    def test_export_cves_csv(self):
        """GET /api/cve/reports/cves/csv - Export CVEs as CSV download"""
        response = requests.get(f"{REPORTS_API}/cves/csv")
        assert response.status_code == 200
        
        # Verify content type is CSV
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type or "application/octet-stream" in content_type
        
        # Verify CSV content
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        assert len(lines) >= 1, "CSV should have at least a header row"
        
        # Check header columns
        header = lines[0]
        expected_columns = ["cve_id", "title", "severity", "status", "cvss_score", 
                          "affected_package", "affected_version", "fixed_version",
                          "assigned_to", "assigned_team", "source"]
        for col in expected_columns:
            assert col in header, f"Header should contain {col}"

    def test_export_cves_csv_with_filters(self):
        """GET /api/cve/reports/cves/csv with status and severity filters"""
        # Test with status filter
        response = requests.get(f"{REPORTS_API}/cves/csv?status=detected")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("Content-Type", "")
        
        # Test with severity filter
        response = requests.get(f"{REPORTS_API}/cves/csv?severity=critical")
        assert response.status_code == 200

    def test_export_governance_csv(self):
        """GET /api/cve/reports/governance/csv - Export governance report as CSV download"""
        response = requests.get(f"{REPORTS_API}/governance/csv")
        assert response.status_code == 200
        
        # Verify content type is CSV
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type or "application/octet-stream" in content_type
        
        # Verify CSV content
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        assert len(lines) >= 5, "Governance CSV should have multiple rows"
        
        # Check for expected metrics
        assert "Total CVEs" in csv_content
        assert "Open CVEs" in csv_content
        assert "Fixed CVEs" in csv_content
        assert "Verified CVEs" in csv_content


class TestNotificationEndpointEdgeCases:
    """Edge case and error handling tests"""

    def test_mark_read_invalid_id(self):
        """PUT /api/cve/notifications/{id}/read with invalid ID"""
        fake_id = "nonexistent-id-12345"
        response = requests.put(f"{NOTIFICATION_API}/{fake_id}/read")
        # Should return success false or 404
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == False or "error" in data

    def test_dismiss_invalid_id(self):
        """DELETE /api/cve/notifications/{id} with invalid ID"""
        fake_id = "nonexistent-id-12345"
        response = requests.delete(f"{NOTIFICATION_API}/{fake_id}")
        # Should return success false or 404
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == False or "error" in data

    def test_create_notification_invalid_type(self):
        """POST /api/cve/notifications with invalid type"""
        payload = {
            "type": "invalid_type_xyz",
            "title": "Test Invalid Type",
            "message": "This should still work as type is flexible"
        }
        response = requests.post(f"{NOTIFICATION_API}", json=payload)
        # The API may accept any type string
        assert response.status_code in [200, 400, 422]


# Cleanup test to run at the end
class TestCleanup:
    """Cleanup test notifications"""

    def test_cleanup_test_notifications(self):
        """Dismiss all test notifications"""
        response = requests.get(f"{NOTIFICATION_API}?limit=100")
        if response.status_code == 200:
            notifications = response.json().get("notifications", [])
            for n in notifications:
                if "TEST_" in n.get("title", "") or "test" in n.get("title", "").lower():
                    requests.delete(f"{NOTIFICATION_API}/{n['id']}")
