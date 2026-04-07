"""
Test cases for Governance Dashboard Widget - GET /api/gs1/governance-overview endpoint
Tests governance rules and disputes aggregation across all labels
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://unified-label-net.preview.emergentagent.com').rstrip('/')


class TestGovernanceOverviewEndpoint:
    """Tests for GET /api/gs1/governance-overview endpoint"""

    def test_governance_overview_returns_200(self):
        """Test that governance-overview endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Governance overview endpoint returns 200")

    def test_governance_overview_has_governance_key(self):
        """Test that response contains governance key with rule counts"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        data = response.json()
        
        assert "governance" in data, "Response missing 'governance' key"
        governance = data["governance"]
        
        # Check required fields
        assert "total_rules" in governance, "Missing total_rules"
        assert "active_rules" in governance, "Missing active_rules"
        assert "draft_rules" in governance, "Missing draft_rules"
        assert "inactive_rules" in governance, "Missing inactive_rules"
        assert "rules_by_type" in governance, "Missing rules_by_type"
        
        # Validate types
        assert isinstance(governance["total_rules"], int), "total_rules should be int"
        assert isinstance(governance["active_rules"], int), "active_rules should be int"
        assert isinstance(governance["rules_by_type"], dict), "rules_by_type should be dict"
        
        print(f"PASS: Governance data structure valid - {governance['total_rules']} total rules, {governance['active_rules']} active")

    def test_governance_overview_has_disputes_key(self):
        """Test that response contains disputes key with dispute counts"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        data = response.json()
        
        assert "disputes" in data, "Response missing 'disputes' key"
        disputes = data["disputes"]
        
        # Check required fields
        assert "total_disputes" in disputes, "Missing total_disputes"
        assert "open_disputes" in disputes, "Missing open_disputes"
        assert "under_review" in disputes, "Missing under_review"
        assert "resolved_disputes" in disputes, "Missing resolved_disputes"
        assert "escalated_disputes" in disputes, "Missing escalated_disputes"
        assert "closed_disputes" in disputes, "Missing closed_disputes"
        assert "disputes_by_priority" in disputes, "Missing disputes_by_priority"
        assert "recent_disputes" in disputes, "Missing recent_disputes"
        
        # Validate types
        assert isinstance(disputes["total_disputes"], int), "total_disputes should be int"
        assert isinstance(disputes["open_disputes"], int), "open_disputes should be int"
        assert isinstance(disputes["disputes_by_priority"], dict), "disputes_by_priority should be dict"
        assert isinstance(disputes["recent_disputes"], list), "recent_disputes should be list"
        
        print(f"PASS: Disputes data structure valid - {disputes['total_disputes']} total, {disputes['open_disputes']} open")

    def test_disputes_by_priority_has_valid_keys(self):
        """Test that disputes_by_priority contains valid priority levels"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        data = response.json()
        disputes = data["disputes"]
        
        valid_priorities = {"critical", "high", "medium", "low"}
        for priority in disputes["disputes_by_priority"].keys():
            assert priority in valid_priorities, f"Invalid priority: {priority}"
        
        print(f"PASS: Disputes by priority valid - {disputes['disputes_by_priority']}")

    def test_recent_disputes_structure(self):
        """Test that recent_disputes list has correct structure"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        data = response.json()
        recent = data["disputes"]["recent_disputes"]
        
        # Should have max 5 recent disputes
        assert len(recent) <= 5, f"Expected max 5 recent disputes, got {len(recent)}"
        
        if len(recent) > 0:
            dispute = recent[0]
            # Check required fields in each dispute
            assert "dispute_id" in dispute, "Missing dispute_id"
            assert "title" in dispute, "Missing title"
            assert "status" in dispute, "Missing status"
            assert "priority" in dispute, "Missing priority"
            assert "dispute_type" in dispute, "Missing dispute_type"
            assert "label_id" in dispute, "Missing label_id"
            
            print(f"PASS: Recent disputes structure valid - {len(recent)} disputes returned")
        else:
            print("PASS: Recent disputes structure valid - 0 disputes (empty list)")

    def test_rules_by_type_structure(self):
        """Test that rules_by_type contains valid rule types"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        data = response.json()
        rules_by_type = data["governance"]["rules_by_type"]
        
        valid_rule_types = {"voting", "content_approval", "financial", "distribution", "membership"}
        for rule_type in rules_by_type.keys():
            assert rule_type in valid_rule_types, f"Invalid rule type: {rule_type}"
            assert isinstance(rules_by_type[rule_type], int), f"Count for {rule_type} should be int"
        
        print(f"PASS: Rules by type valid - {rules_by_type}")

    def test_dispute_counts_sum_correctly(self):
        """Test that individual dispute status counts sum to total"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        data = response.json()
        disputes = data["disputes"]
        
        calculated_total = (
            disputes["open_disputes"] +
            disputes["under_review"] +
            disputes["resolved_disputes"] +
            disputes["escalated_disputes"] +
            disputes["closed_disputes"]
        )
        
        assert calculated_total == disputes["total_disputes"], \
            f"Status counts ({calculated_total}) don't sum to total ({disputes['total_disputes']})"
        
        print(f"PASS: Dispute counts sum correctly - {calculated_total} = {disputes['total_disputes']}")

    def test_governance_overview_no_auth_required(self):
        """Test that endpoint is public (no auth required)"""
        # Make request without any auth headers
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        assert response.status_code == 200, f"Expected 200 without auth, got {response.status_code}"
        print("PASS: Governance overview endpoint is public (no auth required)")


class TestGovernanceOverviewDataValues:
    """Tests for actual data values in governance overview"""

    def test_current_data_values(self):
        """Test current expected data values based on seed data"""
        response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        data = response.json()
        
        governance = data["governance"]
        disputes = data["disputes"]
        
        # Based on provided info: 1 active rule (voting type), 7 total disputes
        assert governance["active_rules"] >= 1, f"Expected at least 1 active rule, got {governance['active_rules']}"
        assert disputes["total_disputes"] >= 7, f"Expected at least 7 disputes, got {disputes['total_disputes']}"
        
        # Check priorities exist: 2 critical, 2 high, 1 medium, 2 low
        priority_counts = disputes["disputes_by_priority"]
        assert priority_counts.get("critical", 0) >= 2, "Expected at least 2 critical disputes"
        assert priority_counts.get("high", 0) >= 2, "Expected at least 2 high disputes"
        assert priority_counts.get("medium", 0) >= 1, "Expected at least 1 medium dispute"
        assert priority_counts.get("low", 0) >= 2, "Expected at least 2 low disputes"
        
        print(f"PASS: Data values match expected - {governance['active_rules']} active rules, {disputes['total_disputes']} disputes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
