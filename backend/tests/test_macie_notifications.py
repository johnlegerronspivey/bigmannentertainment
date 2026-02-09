"""
Backend tests for AWS Macie Notifications (Feature 2) - SNS/EventBridge integration
Tests notification rules, logs, stats, test functionality, and toggle/delete operations
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestMacieNotificationRules:
    """Tests for /api/macie/notifications/rules endpoints"""
    
    def test_get_notification_rules_returns_list(self):
        """Test GET /api/macie/notifications/rules returns rules list"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/rules")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "rules" in data, "Response should have 'rules' key"
        assert "total" in data, "Response should have 'total' key"
        assert isinstance(data["rules"], list), "Rules should be a list"
        assert len(data["rules"]) >= 1, "Should have at least 1 notification rule"
        print(f"✓ GET notification rules: {len(data['rules'])} rules returned")
    
    def test_notification_rule_has_required_fields(self):
        """Test that notification rules have all required fields"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/rules")
        assert response.status_code == 200
        
        rules = response.json()["rules"]
        assert len(rules) > 0, "Need at least 1 rule to test"
        
        rule = rules[0]
        required_fields = ["id", "name", "channel", "is_enabled", "min_severity"]
        for field in required_fields:
            assert field in rule, f"Rule missing required field: {field}"
        
        # Verify channel is one of expected values
        valid_channels = ["SNS", "EVENTBRIDGE", "EMAIL", "SLACK"]
        assert rule["channel"] in valid_channels, f"Invalid channel: {rule['channel']}"
        print(f"✓ Rule '{rule['name']}' has all required fields, channel={rule['channel']}")
    
    def test_notification_rules_have_channel_badges(self):
        """Test rules have proper channel types for badges (SNS, EventBridge, Email)"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/rules")
        assert response.status_code == 200
        
        rules = response.json()["rules"]
        channels_found = set(r["channel"] for r in rules)
        
        # Should have at least SNS and one other channel type
        assert "SNS" in channels_found or "EVENTBRIDGE" in channels_found or "EMAIL" in channels_found, \
            "Should have at least one notification channel"
        print(f"✓ Found channel types: {channels_found}")
    
    def test_create_notification_rule_sns(self):
        """Test POST /api/macie/notifications/rules creates SNS rule"""
        payload = {
            "name": "TEST_SNS_Rule_AutoTest",
            "description": "Test SNS notification rule for automated testing",
            "channel": "SNS",
            "min_severity": "High",
            "pii_types": ["CREDIT_CARD_NUMBER"],
            "sns_topic_arn": "arn:aws:sns:us-east-1:123456789:test-topic"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/macie/notifications/rules",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["name"] == payload["name"], "Rule name should match"
        assert data["channel"] == "SNS", "Channel should be SNS"
        assert data["min_severity"] == "High", "Severity should be High"
        assert "id" in data, "Response should have rule ID"
        
        # Store for cleanup
        TestMacieNotificationRules.created_rule_id = data["id"]
        print(f"✓ Created SNS rule: {data['name']} with ID {data['id']}")
        
        return data["id"]
    
    def test_create_notification_rule_eventbridge(self):
        """Test POST /api/macie/notifications/rules creates EventBridge rule"""
        payload = {
            "name": "TEST_EventBridge_Rule_AutoTest",
            "description": "Test EventBridge notification rule",
            "channel": "EVENTBRIDGE",
            "min_severity": "Medium",
            "eventbridge_bus_name": "test-macie-bus"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/macie/notifications/rules",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["channel"] == "EVENTBRIDGE"
        assert data["eventbridge_bus_name"] == "test-macie-bus"
        
        TestMacieNotificationRules.created_eb_rule_id = data["id"]
        print(f"✓ Created EventBridge rule: {data['name']}")
        
        return data["id"]
    
    def test_create_notification_rule_email(self):
        """Test POST /api/macie/notifications/rules creates Email rule"""
        payload = {
            "name": "TEST_Email_Rule_AutoTest",
            "description": "Test Email notification rule",
            "channel": "EMAIL",
            "min_severity": "Low",
            "email_recipients": ["test@example.com", "test2@example.com"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/macie/notifications/rules",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["channel"] == "EMAIL"
        assert len(data["email_recipients"]) == 2
        
        TestMacieNotificationRules.created_email_rule_id = data["id"]
        print(f"✓ Created Email rule: {data['name']}")


class TestMacieNotificationToggle:
    """Tests for notification rule toggle functionality"""
    
    def test_toggle_notification_rule(self):
        """Test PUT /api/macie/notifications/rules/{id}/toggle"""
        # Get existing rules first
        response = requests.get(f"{BASE_URL}/api/macie/notifications/rules")
        rules = response.json()["rules"]
        assert len(rules) > 0, "Need at least 1 rule to test toggle"
        
        rule = rules[0]
        original_state = rule["is_enabled"]
        
        # Toggle the rule
        toggle_response = requests.put(
            f"{BASE_URL}/api/macie/notifications/rules/{rule['id']}/toggle"
        )
        assert toggle_response.status_code == 200, f"Expected 200, got {toggle_response.status_code}"
        
        toggled_rule = toggle_response.json()
        assert toggled_rule["is_enabled"] != original_state, "is_enabled should toggle"
        print(f"✓ Toggled rule '{rule['name']}' from {original_state} to {toggled_rule['is_enabled']}")
        
        # Toggle back
        requests.put(f"{BASE_URL}/api/macie/notifications/rules/{rule['id']}/toggle")
        print(f"✓ Toggled rule back to original state")
    
    def test_toggle_nonexistent_rule_returns_404(self):
        """Test toggle with non-existent rule ID returns 404"""
        response = requests.put(
            f"{BASE_URL}/api/macie/notifications/rules/nonexistent-id-12345/toggle"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent rule toggle returns 404")


class TestMacieNotificationTest:
    """Tests for test notification functionality"""
    
    def test_send_test_notification(self):
        """Test POST /api/macie/notifications/test/{rule_id} sends test notification"""
        # Get an existing rule
        response = requests.get(f"{BASE_URL}/api/macie/notifications/rules")
        rules = response.json()["rules"]
        assert len(rules) > 0, "Need at least 1 rule to test"
        
        rule = rules[0]
        
        # Send test notification
        test_response = requests.post(
            f"{BASE_URL}/api/macie/notifications/test/{rule['id']}"
        )
        assert test_response.status_code == 200, f"Expected 200, got {test_response.status_code}"
        
        data = test_response.json()
        assert data["success"] == True, "Test notification should succeed"
        assert "message" in data, "Response should have message"
        assert "log" in data, "Response should have log entry"
        
        log = data["log"]
        assert log["status"] == "SENT", "Test notification log should be SENT"
        assert "[TEST]" in log["message"], "Test message should contain [TEST]"
        print(f"✓ Test notification sent for rule '{rule['name']}'")
    
    def test_test_nonexistent_rule_returns_404(self):
        """Test notification with non-existent rule ID returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/macie/notifications/test/nonexistent-id-12345"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent rule test returns 404")


class TestMacieNotificationLogs:
    """Tests for /api/macie/notifications/logs endpoints"""
    
    def test_get_notification_logs(self):
        """Test GET /api/macie/notifications/logs returns logs"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/logs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "logs" in data, "Response should have 'logs' key"
        assert "total" in data, "Response should have 'total' key"
        assert isinstance(data["logs"], list), "Logs should be a list"
        print(f"✓ GET notification logs: {len(data['logs'])} entries, total={data['total']}")
    
    def test_notification_log_has_required_fields(self):
        """Test notification logs have required fields"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/logs")
        assert response.status_code == 200
        
        logs = response.json()["logs"]
        if len(logs) == 0:
            pytest.skip("No log entries to test")
        
        log = logs[0]
        required_fields = ["id", "rule_id", "rule_name", "channel", "status", "message"]
        for field in required_fields:
            assert field in log, f"Log missing required field: {field}"
        
        # Verify status is one of expected values
        valid_statuses = ["SENT", "FAILED", "PENDING"]
        assert log["status"] in valid_statuses, f"Invalid status: {log['status']}"
        print(f"✓ Log entry has all required fields, status={log['status']}, channel={log['channel']}")
    
    def test_notification_logs_with_channel_filter(self):
        """Test GET /api/macie/notifications/logs with channel filter"""
        response = requests.get(
            f"{BASE_URL}/api/macie/notifications/logs?channel=SNS"
        )
        assert response.status_code == 200
        
        data = response.json()
        # If there are SNS logs, they should all be SNS channel
        for log in data["logs"]:
            assert log["channel"] == "SNS", f"Filtered log should be SNS, got {log['channel']}"
        print(f"✓ Channel filter works: {len(data['logs'])} SNS logs found")
    
    def test_notification_logs_have_channel_and_status_badges(self):
        """Test that logs have channel and status for badge display"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/logs?limit=10")
        assert response.status_code == 200
        
        logs = response.json()["logs"]
        if len(logs) == 0:
            pytest.skip("No log entries to test")
        
        channels_found = set()
        statuses_found = set()
        
        for log in logs:
            channels_found.add(log["channel"])
            statuses_found.add(log["status"])
        
        print(f"✓ Logs have channels: {channels_found}, statuses: {statuses_found}")


class TestMacieNotificationStats:
    """Tests for /api/macie/notifications/stats endpoint"""
    
    def test_get_notification_stats(self):
        """Test GET /api/macie/notifications/stats returns statistics"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        required_fields = [
            "total_rules", "active_rules", "total_notifications_sent",
            "total_log_entries", "failed_notifications"
        ]
        
        for field in required_fields:
            assert field in data, f"Stats missing required field: {field}"
        
        assert isinstance(data["total_rules"], int), "total_rules should be int"
        assert isinstance(data["active_rules"], int), "active_rules should be int"
        assert data["active_rules"] <= data["total_rules"], "active_rules should be <= total_rules"
        
        print(f"✓ Notification stats: {data['active_rules']} active rules, "
              f"{data['total_notifications_sent']} sent, {data['failed_notifications']} failed")
    
    def test_stats_have_channel_breakdown(self):
        """Test stats include channel breakdown"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "by_channel" in data, "Stats should have by_channel breakdown"
        assert isinstance(data["by_channel"], dict), "by_channel should be a dict"
        print(f"✓ Channel breakdown: {data['by_channel']}")


class TestMacieNotificationDelete:
    """Tests for notification rule deletion"""
    
    def test_delete_notification_rule(self):
        """Test DELETE /api/macie/notifications/rules/{id}"""
        # Create a rule to delete
        payload = {
            "name": "TEST_DeleteMe_Rule",
            "channel": "SNS",
            "min_severity": "Low",
            "sns_topic_arn": "arn:aws:sns:us-east-1:123:delete-test"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/macie/notifications/rules",
            json=payload
        )
        assert create_response.status_code == 200
        rule_id = create_response.json()["id"]
        print(f"  Created rule {rule_id} for deletion test")
        
        # Delete the rule
        delete_response = requests.delete(
            f"{BASE_URL}/api/macie/notifications/rules/{rule_id}"
        )
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        data = delete_response.json()
        assert data["success"] == True
        print(f"✓ Deleted rule {rule_id}")
        
        # Verify it's gone - check list no longer contains it
        list_response = requests.get(f"{BASE_URL}/api/macie/notifications/rules")
        rules = list_response.json()["rules"]
        rule_ids = [r["id"] for r in rules]
        assert rule_id not in rule_ids, "Deleted rule should not be in list"
        print(f"✓ Verified rule {rule_id} no longer in list")
    
    def test_delete_nonexistent_rule_returns_404(self):
        """Test delete with non-existent rule ID returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/macie/notifications/rules/nonexistent-id-12345"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent rule delete returns 404")


class TestCleanupNotificationRules:
    """Cleanup test-created notification rules"""
    
    def test_cleanup_test_rules(self):
        """Clean up TEST_ prefixed rules"""
        response = requests.get(f"{BASE_URL}/api/macie/notifications/rules")
        rules = response.json()["rules"]
        
        deleted_count = 0
        for rule in rules:
            if rule["name"].startswith("TEST_"):
                del_response = requests.delete(
                    f"{BASE_URL}/api/macie/notifications/rules/{rule['id']}"
                )
                if del_response.status_code == 200:
                    deleted_count += 1
        
        print(f"✓ Cleaned up {deleted_count} test rules")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
