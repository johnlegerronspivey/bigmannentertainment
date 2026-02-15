"""
SLA Tracker API Tests - Enhanced SLA Tracking
Tests: Dashboard, At-Risk CVEs, Escalation Rules, SLA History, Escalation Log, Snapshot, Run Escalations
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://exposure-control-1.preview.emergentagent.com').rstrip('/')
SLA_API = f"{BASE_URL}/api/cve/sla"


class TestSLADashboard:
    """Test GET /api/cve/sla/dashboard - SLA dashboard with compliance stats"""
    
    def test_dashboard_returns_200(self):
        """Dashboard endpoint should return 200 OK"""
        response = requests.get(f"{SLA_API}/dashboard")
        assert response.status_code == 200
        print(f"✓ Dashboard returned 200 OK")
    
    def test_dashboard_structure(self):
        """Dashboard should return overall compliance and severity stats"""
        response = requests.get(f"{SLA_API}/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "overall_compliance" in data
        assert "total_open" in data
        assert "total_within_sla" in data
        assert "total_warning" in data
        assert "total_breached" in data
        assert "severity_stats" in data
        assert "generated_at" in data
        
        # Check overall_compliance is a percentage
        assert 0 <= data["overall_compliance"] <= 100
        
        # Check severity_stats has all severities
        severities = data["severity_stats"]
        assert all(sev in severities for sev in ["critical", "high", "medium", "low"])
        
        print(f"✓ Dashboard structure verified: compliance={data['overall_compliance']}%, open={data['total_open']}")
    
    def test_dashboard_severity_stats_structure(self):
        """Each severity stat should have required fields"""
        response = requests.get(f"{SLA_API}/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        for sev, stats in data["severity_stats"].items():
            assert "sla_hours" in stats
            assert "total" in stats
            assert "within_sla" in stats
            assert "warning" in stats
            assert "breached" in stats
            assert "compliance_pct" in stats
            assert 0 <= stats["compliance_pct"] <= 100
        
        print(f"✓ All severity stats have correct structure")


class TestAtRiskCVEs:
    """Test GET /api/cve/sla/at-risk - CVEs approaching or breaching SLA"""
    
    def test_at_risk_returns_200(self):
        """At-risk endpoint should return 200 OK"""
        response = requests.get(f"{SLA_API}/at-risk")
        assert response.status_code == 200
        print(f"✓ At-risk endpoint returned 200 OK")
    
    def test_at_risk_with_limit(self):
        """At-risk should accept limit parameter"""
        response = requests.get(f"{SLA_API}/at-risk?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) <= 5
        print(f"✓ At-risk with limit=5: {len(data['items'])} items, {data['total']} total")
    
    def test_at_risk_item_structure(self):
        """At-risk items should have countdown/escalation fields"""
        response = requests.get(f"{SLA_API}/at-risk?limit=50")
        assert response.status_code == 200
        data = response.json()
        
        if data["items"]:
            item = data["items"][0]
            required_fields = [
                "cve_id", "title", "severity", "status", "sla_status",
                "sla_hours", "elapsed_hours", "remaining_hours", "overdue_hours",
                "percent_elapsed", "escalation_level", "deadline"
            ]
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
            
            # sla_status should be one of: breached, warning, approaching
            assert item["sla_status"] in ["breached", "warning", "approaching"]
            print(f"✓ At-risk item structure verified: {item['cve_id']} - {item['sla_status']}")
        else:
            print(f"✓ No at-risk items (all CVEs within SLA)")


class TestEscalationRules:
    """Test escalation rules CRUD"""
    
    def test_get_escalation_rules_returns_200(self):
        """Get escalation rules should return 200 OK"""
        response = requests.get(f"{SLA_API}/escalation-rules")
        assert response.status_code == 200
        print(f"✓ Escalation rules GET returned 200 OK")
    
    def test_default_escalation_rules(self):
        """Should have 3 default escalation rules (L1, L2, L3)"""
        response = requests.get(f"{SLA_API}/escalation-rules")
        assert response.status_code == 200
        data = response.json()
        
        assert "rules" in data
        rules = data["rules"]
        assert len(rules) >= 3, "Should have at least 3 default rules"
        
        # Check L1, L2, L3 exist
        levels = [r["level"] for r in rules]
        assert 1 in levels, "Missing L1 rule"
        assert 2 in levels, "Missing L2 rule"
        assert 3 in levels, "Missing L3 rule"
        
        print(f"✓ Found {len(rules)} escalation rules with levels: {levels}")
    
    def test_escalation_rule_structure(self):
        """Each rule should have required fields"""
        response = requests.get(f"{SLA_API}/escalation-rules")
        assert response.status_code == 200
        data = response.json()
        
        for rule in data["rules"]:
            assert "id" in rule
            assert "level" in rule
            assert "name" in rule
            assert "threshold_pct" in rule
            assert "action" in rule
            assert rule["action"] in ["notify", "escalate"]
        
        print(f"✓ All escalation rules have correct structure")
    
    def test_update_escalation_rules(self):
        """PUT should update escalation rules"""
        # First get current rules
        get_response = requests.get(f"{SLA_API}/escalation-rules")
        assert get_response.status_code == 200
        original_rules = get_response.json()["rules"]
        
        # Update rules (just send them back as-is to verify endpoint works)
        update_response = requests.put(
            f"{SLA_API}/escalation-rules",
            json={"rules": original_rules},
            headers={"Content-Type": "application/json"}
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert "rules" in data
        assert len(data["rules"]) == len(original_rules)
        
        print(f"✓ Escalation rules update successful")


class TestRunEscalations:
    """Test POST /api/cve/sla/run-escalations - Execute escalation checks"""
    
    def test_run_escalations_returns_200(self):
        """Run escalations should return 200 OK"""
        response = requests.post(f"{SLA_API}/run-escalations")
        assert response.status_code == 200
        print(f"✓ Run escalations returned 200 OK")
    
    def test_run_escalations_response_structure(self):
        """Run escalations should return check summary"""
        response = requests.post(f"{SLA_API}/run-escalations")
        assert response.status_code == 200
        data = response.json()
        
        assert "checked" in data
        assert "escalations_created" in data
        assert "rules_applied" in data
        
        assert isinstance(data["checked"], int)
        assert isinstance(data["escalations_created"], int)
        assert isinstance(data["rules_applied"], int)
        
        print(f"✓ Escalation check: {data['checked']} CVEs checked, {data['escalations_created']} escalated, {data['rules_applied']} rules")


class TestEscalationLog:
    """Test GET /api/cve/sla/escalation-log - Escalation history"""
    
    def test_escalation_log_returns_200(self):
        """Escalation log should return 200 OK"""
        response = requests.get(f"{SLA_API}/escalation-log")
        assert response.status_code == 200
        print(f"✓ Escalation log returned 200 OK")
    
    def test_escalation_log_structure(self):
        """Escalation log should have items and total"""
        response = requests.get(f"{SLA_API}/escalation-log?limit=30")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        
        print(f"✓ Escalation log: {len(data['items'])} items, {data['total']} total")


class TestSLAHistory:
    """Test GET /api/cve/sla/history - SLA compliance history"""
    
    def test_history_returns_200(self):
        """History endpoint should return 200 OK"""
        response = requests.get(f"{SLA_API}/history")
        assert response.status_code == 200
        print(f"✓ SLA history returned 200 OK")
    
    def test_history_with_days_parameter(self):
        """History should accept days parameter"""
        response = requests.get(f"{SLA_API}/history?days=7")
        assert response.status_code == 200
        data = response.json()
        
        assert "history" in data
        assert "period_days" in data
        assert data["period_days"] == 7
        
        print(f"✓ SLA history with days=7: {len(data['history'])} entries")
    
    def test_history_entry_structure(self):
        """History entries should have date, compliance, counts"""
        response = requests.get(f"{SLA_API}/history?days=30")
        assert response.status_code == 200
        data = response.json()
        
        if data["history"]:
            entry = data["history"][-1]  # Most recent
            assert "date" in entry
            assert "label" in entry
            assert "total_open" in entry
            assert "breached" in entry
            assert "compliance_pct" in entry
            
            print(f"✓ History entry structure verified: {entry['date']}")
        else:
            print(f"✓ No history entries yet")


class TestSLASnapshot:
    """Test POST /api/cve/sla/snapshot - Create point-in-time snapshot"""
    
    def test_snapshot_returns_200(self):
        """Snapshot endpoint should return 200 OK"""
        response = requests.post(f"{SLA_API}/snapshot")
        assert response.status_code == 200
        print(f"✓ Snapshot returned 200 OK")
    
    def test_snapshot_response_structure(self):
        """Snapshot should return compliance data"""
        response = requests.post(f"{SLA_API}/snapshot")
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "date" in data
        assert "label" in data
        assert "total_open" in data
        assert "breached" in data
        assert "warning" in data
        assert "compliance_pct" in data
        assert "severity_stats" in data
        assert "created_at" in data
        
        print(f"✓ Snapshot created: {data['date']} - {data['compliance_pct']}% compliance")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_at_risk_limit_validation(self):
        """At-risk should validate limit parameter"""
        # Limit should be between 1 and 200
        response = requests.get(f"{SLA_API}/at-risk?limit=0")
        # Should either return 422 (validation error) or clamp to valid range
        assert response.status_code in [200, 422]
        print(f"✓ At-risk limit validation: status {response.status_code}")
    
    def test_history_days_validation(self):
        """History should validate days parameter (7-90)"""
        response = requests.get(f"{SLA_API}/history?days=5")
        # Should either return 422 or use minimum
        assert response.status_code in [200, 422]
        print(f"✓ History days validation: status {response.status_code}")
    
    def test_escalation_rules_invalid_json(self):
        """Update rules should handle invalid JSON gracefully"""
        response = requests.put(
            f"{SLA_API}/escalation-rules",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity
        print(f"✓ Invalid JSON handling: status {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
