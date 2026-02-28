"""
Phase 4 Complete Testing - GitHub Remediation & CVE Ownership
Tests all endpoints specified in the review request
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")

# Known CVE IDs from context
CVE_HIGH = "b06d16c4-6ea7-4cbc-8383-f42c0ef4c3e8"
CVE_CRITICAL = "8843dea7-05c2-451e-b5a4-b79019acc2f6"
CVE_LOW = "ab93d7dd-91d5-4c6b-b605-a3207a2927c8"


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestGitHubRemediationConfig:
    """GitHub Remediation: GET /api/cve/remediation/config"""

    def test_config_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/config")
        assert response.status_code == 200
        print(f"✓ Config endpoint returned 200")

    def test_config_has_write_access(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/config")
        data = response.json()
        
        assert data.get("write_access") == True, "Expected write_access: true"
        assert data.get("connected") == True, "Expected connected: true"
        assert data.get("repo_connected") == True, "Expected repo_connected: true"
        print(f"✓ GitHub config shows write_access=True, connected=True, repo_connected=True")

    def test_config_has_stats(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/config")
        data = response.json()
        
        assert "stats" in data, "Config should have stats"
        stats = data["stats"]
        assert "total" in stats
        assert "issues_created" in stats
        print(f"✓ Config has stats: total={stats['total']}, issues_created={stats['issues_created']}")


class TestGitHubRemediationItems:
    """GitHub Remediation: GET /api/cve/remediation/items"""

    def test_items_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items")
        assert response.status_code == 200
        print(f"✓ Items endpoint returned 200")

    def test_items_has_at_least_one(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items")
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1, "Expected at least 1 remediation item"
        print(f"✓ Has {data['total']} remediation items")

    def test_items_have_github_links(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items")
        data = response.json()
        
        items_with_issues = [item for item in data["items"] if item.get("github_issue_number")]
        assert len(items_with_issues) >= 1, "Expected at least 1 item with GitHub issue"
        
        # Verify issue structure
        item = items_with_issues[0]
        assert "github_issue_url" in item
        assert "github_issue_number" in item
        print(f"✓ Found {len(items_with_issues)} items with GitHub issues")


class TestGitHubRemediationStats:
    """GitHub Remediation: GET /api/cve/remediation/stats"""

    def test_stats_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/stats")
        assert response.status_code == 200
        print(f"✓ Stats endpoint returned 200")

    def test_stats_structure(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/stats")
        data = response.json()
        
        required = ["total", "open", "issues_created", "prs_created", "merged", "closed", "by_severity"]
        for field in required:
            assert field in data, f"Missing field: {field}"
        
        assert isinstance(data["by_severity"], dict)
        print(f"✓ Stats has correct structure: total={data['total']}, issues_created={data['issues_created']}")


class TestCVEOwnership:
    """CVE Ownership: PUT /api/cve/entries/{id}/owner"""

    def test_assign_owner_returns_200(self, api_client):
        # Assign owner to a CVE
        payload = {
            "assigned_to": "Test Agent Owner",
            "assigned_team": "Test Team",
            "notes": "Testing assignment"
        }
        response = api_client.put(f"{BASE_URL}/api/cve/entries/{CVE_LOW}/owner", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("assigned_to") == "Test Agent Owner"
        assert data.get("assigned_team") == "Test Team"
        print(f"✓ Owner assignment successful")

    def test_assign_owner_invalid_cve_returns_404(self, api_client):
        payload = {"assigned_to": "Test", "assigned_team": "Test"}
        response = api_client.put(f"{BASE_URL}/api/cve/entries/invalid-id/owner", json=payload)
        assert response.status_code == 404
        print(f"✓ Invalid CVE returns 404 as expected")


class TestCVEBulkAssign:
    """CVE Ownership: POST /api/cve/entries/bulk-assign"""

    def test_bulk_assign_returns_200(self, api_client):
        payload = {
            "cve_ids": [CVE_LOW],
            "assigned_to": "Bulk Test Owner",
            "assigned_team": "Bulk Test Team",
            "notes": "Bulk assignment test"
        }
        response = api_client.post(f"{BASE_URL}/api/cve/entries/bulk-assign", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "updated" in data
        assert "failed" in data
        print(f"✓ Bulk assign: {data['updated']} updated, {data['failed']} failed")


class TestCVEOwners:
    """CVE Ownership: GET /api/cve/owners"""

    def test_owners_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/owners")
        assert response.status_code == 200
        print(f"✓ Owners endpoint returned 200")

    def test_owners_structure(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/owners")
        data = response.json()
        
        assert "people" in data, "Missing 'people' list"
        assert "teams" in data, "Missing 'teams' list"
        assert "unassigned_open_cves" in data, "Missing 'unassigned_open_cves'"
        
        assert isinstance(data["people"], list)
        assert isinstance(data["teams"], list)
        print(f"✓ Owners: {len(data['people'])} people, {len(data['teams'])} teams, {data['unassigned_open_cves']} unassigned")


class TestCVEUnassigned:
    """CVE Ownership: GET /api/cve/unassigned"""

    def test_unassigned_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/unassigned")
        assert response.status_code == 200
        print(f"✓ Unassigned endpoint returned 200")

    def test_unassigned_structure(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/unassigned")
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        
        # All items should have no owner
        for item in data["items"]:
            assert item.get("assigned_to") == "" or item.get("assigned_to") is None
        
        print(f"✓ Unassigned: {data['total']} CVEs without owner")


class TestCoreCVE:
    """Core CVE: GET /api/cve/dashboard and GET /api/cve/entries"""

    def test_dashboard_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/dashboard")
        assert response.status_code == 200
        print(f"✓ Dashboard endpoint returned 200")

    def test_dashboard_structure(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/dashboard")
        data = response.json()
        
        required = ["total_cves", "open_cves", "fixed_cves", "verified_cves", "severity_breakdown"]
        for field in required:
            assert field in data, f"Dashboard missing {field}"
        
        print(f"✓ Dashboard: total={data['total_cves']}, open={data['open_cves']}")

    def test_entries_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/entries")
        assert response.status_code == 200
        print(f"✓ Entries endpoint returned 200")

    def test_entries_structure(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/entries")
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0
        
        # Verify entry has ownership fields
        entry = data["items"][0]
        assert "assigned_to" in entry
        assert "assigned_team" in entry
        print(f"✓ Entries: {data['total']} total CVEs")


class TestGovernance:
    """Governance: metrics, sla, ownership"""

    def test_metrics_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/governance/metrics")
        assert response.status_code == 200
        
        data = response.json()
        required = ["total_cves", "open_cves", "severity_distribution", "risk_score"]
        for field in required:
            assert field in data, f"Missing {field}"
        
        print(f"✓ Governance metrics: total={data['total_cves']}, risk_score={data['risk_score']}")

    def test_sla_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/governance/sla")
        assert response.status_code == 200
        
        data = response.json()
        assert "sla_data" in data
        assert "overall_compliance" in data
        assert len(data["sla_data"]) == 4, "Should have 4 severity levels"
        print(f"✓ Governance SLA: overall={data['overall_compliance']}%")

    def test_ownership_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/cve/governance/ownership")
        assert response.status_code == 200
        
        data = response.json()
        assert "by_team" in data
        assert "by_person" in data
        assert "by_source" in data
        assert "by_status" in data
        print(f"✓ Governance ownership: {len(data['by_team'])} teams, {len(data['by_person'])} persons")


class TestExistingGitHubIssue:
    """Verify existing GitHub issue (issue #2) - DO NOT CREATE NEW ISSUES"""

    def test_issue_2_exists_in_remediation_items(self, api_client):
        """Check that issue #2 for CVE-2026-2DF54E exists"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items")
        data = response.json()
        
        issue_2 = None
        for item in data["items"]:
            if item.get("github_issue_number") == 2:
                issue_2 = item
                break
        
        assert issue_2 is not None, "Issue #2 should exist"
        assert issue_2.get("cve_id") == "CVE-2026-2DF54E"
        assert "github_issue_url" in issue_2
        print(f"✓ Issue #2 exists for CVE-2026-2DF54E: {issue_2['github_issue_url']}")

    def test_create_issue_already_exists(self, api_client):
        """Creating issue for CVE that already has one should fail gracefully"""
        response = api_client.post(f"{BASE_URL}/api/cve/remediation/create-issue/{CVE_CRITICAL}")
        
        # Should return 400 with 'already exists' error
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data.get("detail", "").lower() or "issue" in data.get("detail", "").lower()
        print(f"✓ Correctly reports that issue already exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
