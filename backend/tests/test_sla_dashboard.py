"""
SLA Dashboard API Tests - Iteration 47
Tests for SLA Tracking Dashboard with metrics, team performance, policies, and breach timeline
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')


class TestSLADashboard:
    """SLA Dashboard overview endpoint tests"""

    def test_get_sla_dashboard(self):
        """GET /api/cve/sla/dashboard - Returns SLA compliance overview"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        # Validate structure
        assert "overall_compliance" in data
        assert "total_open" in data
        assert "total_within_sla" in data
        assert "total_warning" in data
        assert "total_breached" in data
        assert "severity_stats" in data
        assert "generated_at" in data
        
        # Validate severity stats
        for sev in ["critical", "high", "medium", "low"]:
            assert sev in data["severity_stats"]
            sev_data = data["severity_stats"][sev]
            assert "sla_hours" in sev_data
            assert "total" in sev_data
            assert "within_sla" in sev_data
            assert "warning" in sev_data
            assert "breached" in sev_data
            assert "compliance_pct" in sev_data
        
        # Validate compliance is percentage
        assert 0 <= data["overall_compliance"] <= 100


class TestSLAMetrics:
    """SLA Metrics and MTTR endpoint tests"""

    def test_get_sla_metrics(self):
        """GET /api/cve/sla/metrics - Returns MTTR and resolution analytics"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/metrics")
        assert response.status_code == 200
        
        data = response.json()
        # Validate structure
        assert "overall_mttr_hours" in data
        assert "overall_mttr_days" in data
        assert "avg_triage_hours" in data
        assert "total_resolved" in data
        assert "total_open" in data
        assert "resolved_this_week" in data
        assert "mttr_by_severity" in data
        assert "resolution_within_sla" in data
        assert "generated_at" in data
        
        # Validate MTTR by severity
        for sev in ["critical", "high", "medium", "low"]:
            assert sev in data["mttr_by_severity"]
            mttr = data["mttr_by_severity"][sev]
            assert "avg_hours" in mttr
            assert "avg_days" in mttr
            assert "min_hours" in mttr
            assert "max_hours" in mttr
            assert "sample_size" in mttr
            assert "sla_hours" in mttr
        
        # Validate resolution within SLA
        for sev in ["critical", "high", "medium", "low"]:
            assert sev in data["resolution_within_sla"]
            res = data["resolution_within_sla"][sev]
            assert "resolved_total" in res
            assert "within_sla" in res
            assert "breached" in res
            assert "rate_pct" in res


class TestTeamPerformance:
    """Team performance endpoint tests"""

    def test_get_team_performance(self):
        """GET /api/cve/sla/team-performance - Returns per-assignee performance"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/team-performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "team" in data
        assert isinstance(data["team"], list)
        
        # Validate team member structure
        if len(data["team"]) > 0:
            member = data["team"][0]
            assert "assignee" in member
            assert "team" in member
            assert "total" in member
            assert "open" in member
            assert "resolved" in member
            assert "breached" in member
            assert "within_sla" in member
            assert "avg_mttr_hours" in member
            assert "avg_mttr_days" in member
            assert "compliance_pct" in member


class TestSLAPolicies:
    """SLA Policies endpoint tests"""

    def test_get_sla_policies(self):
        """GET /api/cve/sla/policies - Returns SLA policy configuration"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/policies")
        assert response.status_code == 200
        
        data = response.json()
        assert "policies" in data
        assert "defaults" in data
        assert isinstance(data["policies"], list)
        
        # Validate policies structure
        severities = [p["severity"] for p in data["policies"]]
        assert "critical" in severities
        assert "high" in severities
        assert "medium" in severities
        assert "low" in severities
        
        for policy in data["policies"]:
            assert "severity" in policy
            assert "sla_hours" in policy
            assert "is_default" in policy
        
        # Validate defaults
        assert "critical" in data["defaults"]
        assert "high" in data["defaults"]
        assert "medium" in data["defaults"]
        assert "low" in data["defaults"]

    def test_update_sla_policies(self):
        """PUT /api/cve/sla/policies - Update SLA hours per severity"""
        # Get current policies first
        get_response = requests.get(f"{BASE_URL}/api/cve/sla/policies")
        assert get_response.status_code == 200
        original_policies = get_response.json()["policies"]
        
        # Update with test values
        test_policies = [
            {"severity": "critical", "sla_hours": 48},
            {"severity": "high", "sla_hours": 96}
        ]
        
        response = requests.put(
            f"{BASE_URL}/api/cve/sla/policies",
            json={"policies": test_policies},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "policies" in data
        
        # Verify update was applied
        critical_pol = next((p for p in data["policies"] if p["severity"] == "critical"), None)
        if critical_pol:
            assert critical_pol["sla_hours"] == 48
            assert critical_pol["is_default"] == False
            assert "updated_at" in critical_pol
        
        # Restore original values
        restore_policies = [
            {"severity": "critical", "sla_hours": 24},
            {"severity": "high", "sla_hours": 72},
            {"severity": "medium", "sla_hours": 168},
            {"severity": "low", "sla_hours": 720}
        ]
        requests.put(
            f"{BASE_URL}/api/cve/sla/policies",
            json={"policies": restore_policies},
            headers={"Content-Type": "application/json"}
        )


class TestBreachTimeline:
    """Breach timeline endpoint tests"""

    def test_get_breach_timeline_default(self):
        """GET /api/cve/sla/breach-timeline - Returns breach timeline for 30 days"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/breach-timeline")
        assert response.status_code == 200
        
        data = response.json()
        assert "timeline" in data
        assert "period_days" in data
        assert data["period_days"] == 30
        assert isinstance(data["timeline"], list)
        
        # Validate timeline entry structure
        if len(data["timeline"]) > 0:
            entry = data["timeline"][0]
            assert "date" in entry
            assert "label" in entry
            assert "new_breaches" in entry
            assert "critical" in entry
            assert "high" in entry
            assert "medium" in entry
            assert "low" in entry

    def test_get_breach_timeline_custom_days(self):
        """GET /api/cve/sla/breach-timeline?days=14 - Custom period"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/breach-timeline?days=14")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 14


class TestAtRiskCVEs:
    """At-risk CVEs endpoint tests"""

    def test_get_at_risk_cves(self):
        """GET /api/cve/sla/at-risk - Returns CVEs approaching or past SLA"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/at-risk?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        
        # Validate at-risk CVE structure
        if len(data["items"]) > 0:
            cve = data["items"][0]
            assert "cve_id" in cve
            assert "title" in cve
            assert "severity" in cve
            assert "status" in cve
            assert "sla_status" in cve
            assert "sla_hours" in cve
            assert "elapsed_hours" in cve
            assert "remaining_hours" in cve
            assert "overdue_hours" in cve
            assert "percent_elapsed" in cve
            assert "escalation_level" in cve
            assert "deadline" in cve
            
            # Validate sla_status is valid
            assert cve["sla_status"] in ["approaching", "warning", "breached"]
            
            # Validate escalation level is 0-3
            assert 0 <= cve["escalation_level"] <= 3


class TestEscalationRules:
    """Escalation rules endpoint tests"""

    def test_get_escalation_rules(self):
        """GET /api/cve/sla/escalation-rules - Returns escalation configuration"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/escalation-rules")
        assert response.status_code == 200
        
        data = response.json()
        assert "rules" in data
        assert isinstance(data["rules"], list)
        assert len(data["rules"]) >= 1
        
        # Validate rule structure
        for rule in data["rules"]:
            assert "id" in rule
            assert "level" in rule
            assert "name" in rule
            assert "threshold_pct" in rule
            assert "action" in rule
            assert "notify_role" in rule
            assert "description" in rule


class TestEscalationStats:
    """Escalation stats endpoint tests"""

    def test_get_escalation_stats(self):
        """GET /api/cve/sla/escalation-stats - Returns escalation counts"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/escalation-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "open" in data
        assert "acknowledged" in data
        assert "assigned" in data
        assert "resolved" in data
        
        # Validate all are non-negative integers
        assert isinstance(data["total"], int)
        assert isinstance(data["open"], int)
        assert data["total"] >= 0


class TestSLAHistory:
    """SLA History endpoint tests"""

    def test_get_sla_history_default(self):
        """GET /api/cve/sla/history - Returns compliance history for 30 days"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/history?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert "history" in data
        assert "period_days" in data
        assert data["period_days"] == 30
        assert isinstance(data["history"], list)
        
        # Validate history entry structure
        if len(data["history"]) > 0:
            entry = data["history"][0]
            assert "date" in entry
            assert "compliance_pct" in entry


class TestDataIntegrity:
    """Cross-endpoint data integrity tests"""

    def test_dashboard_matches_at_risk_totals(self):
        """Verify dashboard breached count is consistent with at-risk data"""
        dashboard = requests.get(f"{BASE_URL}/api/cve/sla/dashboard").json()
        at_risk = requests.get(f"{BASE_URL}/api/cve/sla/at-risk?limit=200").json()
        
        # Count breached from at-risk
        breached_count = sum(1 for item in at_risk["items"] if item["sla_status"] == "breached")
        
        # Dashboard breached should match or be close to at-risk breached count
        # Some variance is acceptable due to timing
        assert abs(dashboard["total_breached"] - breached_count) <= 2

    def test_team_performance_totals_make_sense(self):
        """Verify team performance totals are consistent"""
        team_data = requests.get(f"{BASE_URL}/api/cve/sla/team-performance").json()
        
        for member in team_data["team"]:
            # Total should equal open + resolved
            assert member["total"] == member["open"] + member["resolved"]
            
            # Compliance should be 0-100
            assert 0 <= member["compliance_pct"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
