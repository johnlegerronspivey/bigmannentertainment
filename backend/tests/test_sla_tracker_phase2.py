"""
SLA Tracker Phase 2 API Tests - Enhanced SLA Tracking with Auto-Escalation & Notifications
Tests: Auto-Escalation Config, Notification Preferences, Escalation Workflow, SLA Digest, Enhanced Run Escalations
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')
SLA_API = f"{BASE_URL}/api/cve/sla"


# ─── Phase 1 Core Endpoints (Existing) ───────────────────────────

class TestPhase1SLADashboard:
    """Test GET /api/cve/sla/dashboard - SLA dashboard with compliance stats"""
    
    def test_dashboard_returns_200(self):
        """Dashboard endpoint should return 200 OK"""
        response = requests.get(f"{SLA_API}/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "overall_compliance" in data
        assert "total_open" in data
        assert "severity_stats" in data
        print(f"✓ Dashboard: {data['overall_compliance']}% compliance, {data['total_open']} open CVEs")

    def test_dashboard_severity_stats(self):
        """Dashboard should have all severity stats"""
        response = requests.get(f"{SLA_API}/dashboard")
        assert response.status_code == 200
        data = response.json()
        for sev in ["critical", "high", "medium", "low"]:
            assert sev in data["severity_stats"]
            stats = data["severity_stats"][sev]
            assert "sla_hours" in stats
            assert "compliance_pct" in stats
        print(f"✓ Severity stats verified for all 4 severities")


class TestPhase1AtRisk:
    """Test GET /api/cve/sla/at-risk - CVEs approaching or breaching SLA"""
    
    def test_at_risk_returns_200(self):
        """At-risk endpoint should return 200 OK"""
        response = requests.get(f"{SLA_API}/at-risk?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        print(f"✓ At-risk: {data['total']} total at-risk CVEs")


class TestPhase1EscalationRules:
    """Test GET/PUT /api/cve/sla/escalation-rules - Escalation rules config"""
    
    def test_get_escalation_rules(self):
        """Get escalation rules should return 200 OK with L1/L2/L3"""
        response = requests.get(f"{SLA_API}/escalation-rules")
        assert response.status_code == 200
        data = response.json()
        assert "rules" in data
        levels = [r["level"] for r in data["rules"]]
        assert 1 in levels and 2 in levels and 3 in levels
        print(f"✓ Escalation rules: {len(data['rules'])} rules")

    def test_update_escalation_rules(self):
        """PUT should update escalation rules"""
        get_response = requests.get(f"{SLA_API}/escalation-rules")
        original_rules = get_response.json()["rules"]
        update_response = requests.put(
            f"{SLA_API}/escalation-rules",
            json={"rules": original_rules},
            headers={"Content-Type": "application/json"}
        )
        assert update_response.status_code == 200
        print(f"✓ Escalation rules update successful")


class TestPhase1EscalationLog:
    """Test GET /api/cve/sla/escalation-log - Escalation history"""
    
    def test_escalation_log_returns_200(self):
        """Escalation log should return 200 OK"""
        response = requests.get(f"{SLA_API}/escalation-log?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        print(f"✓ Escalation log: {data['total']} total entries")


class TestPhase1History:
    """Test GET /api/cve/sla/history - SLA compliance history"""
    
    def test_history_returns_200(self):
        """History endpoint should return 200 OK"""
        response = requests.get(f"{SLA_API}/history?days=30")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "period_days" in data
        print(f"✓ SLA history: {len(data['history'])} entries for {data['period_days']} days")


class TestPhase1Snapshot:
    """Test POST /api/cve/sla/snapshot - Create point-in-time snapshot"""
    
    def test_snapshot_returns_200(self):
        """Snapshot endpoint should return 200 OK"""
        response = requests.post(f"{SLA_API}/snapshot")
        assert response.status_code == 200
        data = response.json()
        assert "compliance_pct" in data
        assert "date" in data
        print(f"✓ Snapshot created: {data['compliance_pct']}% compliance on {data['date']}")


# ─── Phase 2: Auto-Escalation Config ─────────────────────────────

class TestPhase2AutoEscalationConfig:
    """Test GET/PUT /api/cve/sla/auto-escalation-config - Auto-escalation settings"""
    
    def test_get_auto_escalation_config_returns_200(self):
        """Get auto-escalation config should return 200 OK"""
        response = requests.get(f"{SLA_API}/auto-escalation-config")
        assert response.status_code == 200
        print(f"✓ Auto-escalation config GET returned 200")
    
    def test_get_auto_escalation_config_structure(self):
        """Config should have enabled, interval, email settings, recipients"""
        response = requests.get(f"{SLA_API}/auto-escalation-config")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "enabled", "interval_minutes", 
            "email_on_warning", "email_on_breach", "email_on_escalation",
            "digest_enabled", "digest_cron_hour", "recipients"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert isinstance(data["enabled"], bool)
        assert isinstance(data["interval_minutes"], int)
        assert isinstance(data["recipients"], list)
        
        print(f"✓ Auto-escalation config: enabled={data['enabled']}, interval={data['interval_minutes']}min, {len(data['recipients'])} recipients")
    
    def test_update_auto_escalation_config(self):
        """PUT should update auto-escalation config"""
        # First get current config
        get_response = requests.get(f"{SLA_API}/auto-escalation-config")
        assert get_response.status_code == 200
        original_config = get_response.json()
        
        # Update with modified values
        update_payload = {
            "enabled": False,  # Keep disabled for testing
            "interval_minutes": 45,
            "email_on_warning": True,
            "email_on_breach": True,
            "email_on_escalation": True,
            "digest_enabled": False,
            "digest_cron_hour": 8,
            "recipients": ["test-phase2@example.com"]
        }
        update_response = requests.put(
            f"{SLA_API}/auto-escalation-config",
            json=update_payload,
            headers={"Content-Type": "application/json"}
        )
        assert update_response.status_code == 200
        data = update_response.json()
        
        assert data["interval_minutes"] == 45
        assert "test-phase2@example.com" in data["recipients"]
        
        print(f"✓ Auto-escalation config updated successfully")
        
        # Restore original
        requests.put(
            f"{SLA_API}/auto-escalation-config",
            json=original_config,
            headers={"Content-Type": "application/json"}
        )
    
    def test_update_config_add_remove_recipients(self):
        """Config recipients should be updateable"""
        # Get current
        get_response = requests.get(f"{SLA_API}/auto-escalation-config")
        original_config = get_response.json()
        
        # Add a test recipient
        test_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        new_recipients = original_config.get("recipients", []) + [test_email]
        
        update_response = requests.put(
            f"{SLA_API}/auto-escalation-config",
            json={**original_config, "recipients": new_recipients},
            headers={"Content-Type": "application/json"}
        )
        assert update_response.status_code == 200
        assert test_email in update_response.json()["recipients"]
        
        print(f"✓ Recipients add/update works correctly")
        
        # Restore
        requests.put(
            f"{SLA_API}/auto-escalation-config",
            json=original_config,
            headers={"Content-Type": "application/json"}
        )


# ─── Phase 2: Notification Preferences ───────────────────────────

class TestPhase2NotificationPreferences:
    """Test GET/PUT /api/cve/sla/notification-preferences - Per-severity notification settings"""
    
    def test_get_notification_preferences_returns_200(self):
        """Get notification preferences should return 200 OK"""
        response = requests.get(f"{SLA_API}/notification-preferences")
        assert response.status_code == 200
        print(f"✓ Notification preferences GET returned 200")
    
    def test_get_notification_preferences_structure(self):
        """Preferences should have per-severity email/in-app toggles"""
        response = requests.get(f"{SLA_API}/notification-preferences")
        assert response.status_code == 200
        data = response.json()
        
        # Check global settings
        assert "notify_on_warning" in data
        assert "notify_on_breach" in data
        assert "notify_on_escalation" in data
        assert "per_severity" in data
        
        # Check per-severity structure
        per_sev = data["per_severity"]
        for sev in ["critical", "high", "medium", "low"]:
            assert sev in per_sev, f"Missing severity: {sev}"
            assert "email" in per_sev[sev]
            assert "in_app" in per_sev[sev]
        
        print(f"✓ Notification preferences: per_severity has email/in_app for all 4 severities")
    
    def test_update_notification_preferences(self):
        """PUT should update notification preferences"""
        # Get current
        get_response = requests.get(f"{SLA_API}/notification-preferences")
        original_prefs = get_response.json()
        
        # Update
        update_payload = {
            "notify_on_warning": True,
            "notify_on_breach": True,
            "notify_on_escalation": True,
            "per_severity": {
                "critical": {"email": True, "in_app": True},
                "high": {"email": True, "in_app": True},
                "medium": {"email": False, "in_app": True},
                "low": {"email": False, "in_app": False}  # Changed for test
            }
        }
        
        update_response = requests.put(
            f"{SLA_API}/notification-preferences",
            json=update_payload,
            headers={"Content-Type": "application/json"}
        )
        assert update_response.status_code == 200
        data = update_response.json()
        
        assert data["per_severity"]["low"]["in_app"] == False
        
        print(f"✓ Notification preferences updated successfully")
        
        # Restore
        requests.put(
            f"{SLA_API}/notification-preferences",
            json=original_prefs,
            headers={"Content-Type": "application/json"}
        )


# ─── Phase 2: Escalation Workflow Stats ──────────────────────────

class TestPhase2EscalationStats:
    """Test GET /api/cve/sla/escalation-stats - Escalation workflow statistics"""
    
    def test_escalation_stats_returns_200(self):
        """Escalation stats should return 200 OK"""
        response = requests.get(f"{SLA_API}/escalation-stats")
        assert response.status_code == 200
        print(f"✓ Escalation stats GET returned 200")
    
    def test_escalation_stats_structure(self):
        """Stats should have total, open, acknowledged, assigned, resolved"""
        response = requests.get(f"{SLA_API}/escalation-stats")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["total", "open", "acknowledged", "assigned", "resolved"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], int)
        
        print(f"✓ Escalation stats: total={data['total']}, open={data['open']}, ack={data['acknowledged']}, assigned={data['assigned']}, resolved={data['resolved']}")


# ─── Phase 2: Escalation Workflow Actions ────────────────────────

class TestPhase2EscalationWorkflowActions:
    """Test POST /api/cve/sla/escalation-log/{id}/acknowledge|assign|resolve"""
    
    def test_acknowledge_nonexistent_escalation(self):
        """Acknowledge non-existent escalation should return error"""
        fake_id = "nonexistent-id-12345"
        response = requests.post(
            f"{SLA_API}/escalation-log/{fake_id}/acknowledge",
            json={"performed_by": "test@example.com"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should indicate not found or no modification
        assert data.get("success") == False or "error" in data
        print(f"✓ Acknowledge non-existent returns proper error")
    
    def test_assign_nonexistent_escalation(self):
        """Assign non-existent escalation should return error"""
        fake_id = "nonexistent-id-12345"
        response = requests.post(
            f"{SLA_API}/escalation-log/{fake_id}/assign",
            json={"assignee": "test@example.com", "performed_by": "admin"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False or "error" in data
        print(f"✓ Assign non-existent returns proper error")
    
    def test_resolve_nonexistent_escalation(self):
        """Resolve non-existent escalation should return error"""
        fake_id = "nonexistent-id-12345"
        response = requests.post(
            f"{SLA_API}/escalation-log/{fake_id}/resolve",
            json={"resolution_note": "Test resolution", "performed_by": "admin"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False or "error" in data
        print(f"✓ Resolve non-existent returns proper error")
    
    def test_workflow_action_endpoints_accept_body(self):
        """All workflow action endpoints should accept JSON body"""
        fake_id = "test-action-endpoint"
        
        # Acknowledge with performed_by
        ack_response = requests.post(
            f"{SLA_API}/escalation-log/{fake_id}/acknowledge",
            json={"performed_by": "test_user"},
            headers={"Content-Type": "application/json"}
        )
        assert ack_response.status_code == 200
        
        # Assign with assignee
        assign_response = requests.post(
            f"{SLA_API}/escalation-log/{fake_id}/assign",
            json={"assignee": "john@example.com", "performed_by": "admin"},
            headers={"Content-Type": "application/json"}
        )
        assert assign_response.status_code == 200
        
        # Resolve with note
        resolve_response = requests.post(
            f"{SLA_API}/escalation-log/{fake_id}/resolve",
            json={"resolution_note": "Fixed by updating config", "performed_by": "admin"},
            headers={"Content-Type": "application/json"}
        )
        assert resolve_response.status_code == 200
        
        print(f"✓ All workflow action endpoints accept JSON body correctly")


# ─── Phase 2: SLA Digest ─────────────────────────────────────────

class TestPhase2SLADigest:
    """Test POST /api/cve/sla/send-digest - Trigger SLA digest email"""
    
    def test_send_digest_returns_200(self):
        """Send digest should return 200 OK"""
        response = requests.post(f"{SLA_API}/send-digest")
        assert response.status_code == 200
        print(f"✓ Send digest returned 200")
    
    def test_send_digest_response_structure(self):
        """Digest response should have sent status and compliance info"""
        response = requests.post(f"{SLA_API}/send-digest")
        assert response.status_code == 200
        data = response.json()
        
        # Response should indicate if email was sent
        assert "sent" in data
        assert isinstance(data["sent"], bool)
        
        # Should include compliance metrics
        assert "compliance" in data
        assert "total_open" in data
        assert "total_breached" in data
        
        # If not sent, should have reason or recipients count
        if not data["sent"]:
            assert "reason" in data or "recipients" in data
        
        print(f"✓ Digest response: sent={data['sent']}, compliance={data['compliance']}%, open={data['total_open']}")


# ─── Phase 2: Enhanced Run Escalations ───────────────────────────

class TestPhase2EnhancedRunEscalations:
    """Test POST /api/cve/sla/run-escalations - Enhanced with email support"""
    
    def test_run_escalations_returns_200(self):
        """Run escalations should return 200 OK"""
        response = requests.post(f"{SLA_API}/run-escalations")
        assert response.status_code == 200
        print(f"✓ Run escalations returned 200")
    
    def test_run_escalations_enhanced_response(self):
        """Run escalations should include email_sent flag (Phase 2)"""
        response = requests.post(f"{SLA_API}/run-escalations")
        assert response.status_code == 200
        data = response.json()
        
        # Phase 1 fields
        assert "checked" in data
        assert "escalations_created" in data
        assert "rules_applied" in data
        
        # Phase 2 enhancement - email_sent field
        assert "email_sent" in data
        assert isinstance(data["email_sent"], bool)
        
        print(f"✓ Run escalations: {data['checked']} checked, {data['escalations_created']} created, email_sent={data['email_sent']}")


# ─── Integration Tests ───────────────────────────────────────────

class TestPhase2Integration:
    """Integration tests for Phase 2 features working together"""
    
    def test_full_sla_data_flow(self):
        """Test complete data flow: dashboard -> at-risk -> escalation"""
        # Get dashboard
        dashboard_resp = requests.get(f"{SLA_API}/dashboard")
        assert dashboard_resp.status_code == 200
        dashboard = dashboard_resp.json()
        
        # Get at-risk CVEs
        at_risk_resp = requests.get(f"{SLA_API}/at-risk")
        assert at_risk_resp.status_code == 200
        at_risk = at_risk_resp.json()
        
        # Get escalation stats
        stats_resp = requests.get(f"{SLA_API}/escalation-stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        
        # Data should be consistent
        total_open = dashboard["total_open"]
        print(f"✓ Integration flow: {total_open} open CVEs, {at_risk['total']} at-risk, {stats['total']} escalations")
    
    def test_config_and_digest_integration(self):
        """Test that config affects digest behavior"""
        # Get auto-escalation config
        config_resp = requests.get(f"{SLA_API}/auto-escalation-config")
        assert config_resp.status_code == 200
        config = config_resp.json()
        
        # Try sending digest
        digest_resp = requests.post(f"{SLA_API}/send-digest")
        assert digest_resp.status_code == 200
        digest = digest_resp.json()
        
        # If no recipients in config, digest should not be sent
        if not config.get("recipients"):
            assert digest["sent"] == False
            print(f"✓ Digest correctly not sent with no recipients")
        else:
            # With recipients, sent depends on email service availability
            print(f"✓ Digest attempted with {len(config['recipients'])} recipients, sent={digest['sent']}")
    
    def test_notification_prefs_and_escalation_config_independent(self):
        """Notification preferences and auto-escalation config should work independently"""
        notif_resp = requests.get(f"{SLA_API}/notification-preferences")
        config_resp = requests.get(f"{SLA_API}/auto-escalation-config")
        
        assert notif_resp.status_code == 200
        assert config_resp.status_code == 200
        
        notif = notif_resp.json()
        config = config_resp.json()
        
        # Both should have their own structure
        assert "per_severity" in notif
        assert "interval_minutes" in config
        
        print(f"✓ Notification prefs and auto-escalation config are independent")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
