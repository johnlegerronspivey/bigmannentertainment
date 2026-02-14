"""
Test Email Notifications Integration via Resend
Tests the new email notification features for CVE alerts
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://vuln-alert.preview.emergentagent.com').rstrip('/')

class TestEmailStatus:
    """Tests for GET /api/security/email/status endpoint"""
    
    def test_email_status_returns_correct_fields(self):
        """Test that email status returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/security/email/status")
        assert response.status_code == 200
        
        data = response.json()
        # Verify all required fields are present
        assert "configured" in data, "Missing 'configured' field"
        assert "has_api_key" in data, "Missing 'has_api_key' field"
        assert "alert_email" in data, "Missing 'alert_email' field"
        assert "email_notifications_enabled" in data, "Missing 'email_notifications_enabled' field"
        
        # Verify data types
        assert isinstance(data["configured"], bool)
        assert isinstance(data["has_api_key"], bool)
        assert isinstance(data["email_notifications_enabled"], bool)
        print(f"PASS: Email status returns: configured={data['configured']}, has_api_key={data['has_api_key']}, email={data['alert_email']}")
    
    def test_email_status_api_key_configured(self):
        """Test that Resend API key is configured"""
        response = requests.get(f"{BASE_URL}/api/security/email/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_api_key"] == True, "Resend API key should be configured"
        assert data["configured"] == True, "Email should be fully configured"
        print("PASS: Resend API key is configured")


class TestTestEmail:
    """Tests for POST /api/security/email/test endpoint"""
    
    def test_send_test_email_success(self):
        """Test that sending a test email works via Resend"""
        response = requests.post(
            f"{BASE_URL}/api/security/email/test",
            json={"recipient": "owner@bigmannentertainment.com"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["sent"] == True, f"Test email should be sent, got error: {data.get('error', 'No error')}"
        assert "email_id" in data, "Should return email_id from Resend"
        assert "recipient" in data, "Should return recipient email"
        assert len(data["email_id"]) > 0, "email_id should not be empty"
        print(f"PASS: Test email sent successfully, email_id={data['email_id']}")
    
    def test_send_test_email_without_recipient_uses_default(self):
        """Test that omitting recipient uses default alert email"""
        response = requests.post(
            f"{BASE_URL}/api/security/email/test",
            json={}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Either sends successfully (if default email configured) or returns error
        if data["sent"]:
            assert "email_id" in data
            print(f"PASS: Test email sent to default recipient, email_id={data['email_id']}")
        else:
            # Expected if no default email is configured
            assert "error" in data
            print(f"PASS: No default email configured: {data['error']}")


class TestMonitorConfigEmailFields:
    """Tests for PUT /api/security/monitor/config with email fields"""
    
    def test_update_email_notifications_toggle_off(self):
        """Test toggling email_notifications off"""
        # First get current state
        get_response = requests.get(f"{BASE_URL}/api/security/monitor/config")
        original_config = get_response.json()
        
        # Toggle off
        response = requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"email_notifications": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["email_notifications"] == False, "email_notifications should be False"
        
        # Verify persistence
        verify_response = requests.get(f"{BASE_URL}/api/security/monitor/config")
        verify_data = verify_response.json()
        assert verify_data["email_notifications"] == False, "email_notifications should persist as False"
        print("PASS: email_notifications toggled OFF and persisted")
        
        # Restore original state
        requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"email_notifications": original_config.get("email_notifications", True)}
        )
    
    def test_update_email_notifications_toggle_on(self):
        """Test toggling email_notifications on"""
        # Toggle on
        response = requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"email_notifications": True}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["email_notifications"] == True, "email_notifications should be True"
        
        # Verify persistence
        verify_response = requests.get(f"{BASE_URL}/api/security/monitor/config")
        verify_data = verify_response.json()
        assert verify_data["email_notifications"] == True, "email_notifications should persist as True"
        print("PASS: email_notifications toggled ON and persisted")
    
    def test_update_alert_email(self):
        """Test updating alert_email field"""
        # Get original
        get_response = requests.get(f"{BASE_URL}/api/security/monitor/config")
        original_email = get_response.json().get("alert_email", "")
        
        # Update to test email
        new_email = "test-cve-alerts@bigmannentertainment.com"
        response = requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"alert_email": new_email}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["alert_email"] == new_email, f"alert_email should be {new_email}"
        
        # Verify persistence
        verify_response = requests.get(f"{BASE_URL}/api/security/monitor/config")
        verify_data = verify_response.json()
        assert verify_data["alert_email"] == new_email, "alert_email should persist"
        print(f"PASS: alert_email updated to {new_email}")
        
        # Restore original
        requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"alert_email": original_email}
        )
        print(f"Restored alert_email to {original_email}")
    
    def test_update_both_email_fields_together(self):
        """Test updating both email_notifications and alert_email together"""
        # Get original
        get_response = requests.get(f"{BASE_URL}/api/security/monitor/config")
        original = get_response.json()
        
        # Update both
        response = requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={
                "email_notifications": True,
                "alert_email": "combined-test@bigmannentertainment.com"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["email_notifications"] == True
        assert data["alert_email"] == "combined-test@bigmannentertainment.com"
        print("PASS: Both email fields updated together")
        
        # Restore original
        requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={
                "email_notifications": original.get("email_notifications", True),
                "alert_email": original.get("alert_email", "")
            }
        )


class TestEmailStatusReflectsConfig:
    """Test that email status endpoint reflects monitor config changes"""
    
    def test_email_status_reflects_notifications_toggle(self):
        """Test that email_notifications_enabled in status matches config"""
        # Get config
        config_response = requests.get(f"{BASE_URL}/api/security/monitor/config")
        config = config_response.json()
        
        # Get status
        status_response = requests.get(f"{BASE_URL}/api/security/email/status")
        status = status_response.json()
        
        # Should match
        assert status["email_notifications_enabled"] == config["email_notifications"], \
            f"Status ({status['email_notifications_enabled']}) should match config ({config['email_notifications']})"
        assert status["alert_email"] == config["alert_email"], \
            f"Status email ({status['alert_email']}) should match config ({config['alert_email']})"
        print("PASS: Email status reflects monitor config correctly")


class TestPreviousMonitoringFeatures:
    """Verify all previous monitoring features still work"""
    
    def test_monitor_enable_disable(self):
        """Test monitor enable/disable still works"""
        # Disable
        response = requests.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"enabled": False}
        )
        assert response.status_code == 200
        assert response.json()["enabled"] == False
        print("PASS: Monitor disable works")
    
    def test_scan_now(self):
        """Test scan now still works"""
        response = requests.post(f"{BASE_URL}/api/security/monitor/scan-now")
        assert response.status_code == 200
        
        data = response.json()
        assert "scan" in data
        assert "config" in data
        assert "security_score" in data["scan"]
        print(f"PASS: Scan Now works, score={data['scan']['security_score']}")
    
    def test_alerts_endpoint(self):
        """Test alerts endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/security/alerts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("PASS: Alerts endpoint works")
    
    def test_audit_history(self):
        """Test audit history still works"""
        response = requests.get(f"{BASE_URL}/api/security/audit/history?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "security_score" in data[0]
            assert "grade" in data[0]
        print(f"PASS: Audit history works, {len(data)} records")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
