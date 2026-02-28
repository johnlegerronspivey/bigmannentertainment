"""
Test Suite for Phase 3: Automated Remediation & GitHub Integration
Tests remediation endpoints, GitHub integration, and AWS Inspector/Security Hub
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")

# ═══════════════════════════════════════════════════════════════
# Test Session Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

# Test CVE ID provided in context
TEST_CVE_ID = "9053f579-46aa-4573-aabb-bf424fafc202"

# ═══════════════════════════════════════════════════════════════
# Remediation Config & Stats Tests
# ═══════════════════════════════════════════════════════════════

class TestRemediationConfig:
    """GitHub config and remediation stats tests"""

    def test_get_remediation_config(self, api_client):
        """GET /api/cve/remediation/config - Returns GitHub connection status and repo details"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/config")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify config structure
        assert "connected" in data, "Config should include 'connected' field"
        assert "repo_connected" in data, "Config should include 'repo_connected' field"
        assert "token_configured" in data, "Config should include 'token_configured' field"
        assert "stats" in data, "Config should include 'stats' field"
        
        # Token and repo should be configured based on backend/.env
        assert data["token_configured"] == True, "GitHub token should be configured"
        print(f"GitHub config: connected={data['connected']}, repo_connected={data['repo_connected']}, repo_name={data.get('repo_name', 'N/A')}")
        
    def test_config_stats_structure(self, api_client):
        """Verify stats structure in config response"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/config")
        assert response.status_code == 200
        
        stats = response.json().get("stats", {})
        # Verify stats fields
        assert "total" in stats, "Stats should include 'total'"
        assert "open" in stats, "Stats should include 'open'"
        assert "issues_created" in stats, "Stats should include 'issues_created'"
        assert "prs_created" in stats, "Stats should include 'prs_created'"
        assert "merged" in stats, "Stats should include 'merged'"
        assert "closed" in stats, "Stats should include 'closed'"
        assert "by_severity" in stats, "Stats should include 'by_severity'"
        print(f"Remediation stats: total={stats['total']}, open={stats['open']}, issues_created={stats['issues_created']}, prs_created={stats['prs_created']}")

    def test_get_remediation_stats_endpoint(self, api_client):
        """GET /api/cve/remediation/stats - Returns standalone remediation statistics"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data
        assert "open" in data
        assert "by_severity" in data
        assert isinstance(data["by_severity"], dict)
        print(f"Stats endpoint: total={data['total']}, by_severity={data['by_severity']}")

# ═══════════════════════════════════════════════════════════════
# Remediation Items Tests
# ═══════════════════════════════════════════════════════════════

class TestRemediationItems:
    """Remediation items CRUD tests"""

    def test_list_remediation_items(self, api_client):
        """GET /api/cve/remediation/items - Lists remediation items"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "items" in data, "Response should include 'items'"
        assert "total" in data, "Response should include 'total'"
        assert "limit" in data, "Response should include 'limit'"
        assert "skip" in data, "Response should include 'skip'"
        assert isinstance(data["items"], list), "Items should be a list"
        print(f"Remediation items: total={data['total']}, returned={len(data['items'])}")

    def test_list_items_with_status_filter(self, api_client):
        """GET /api/cve/remediation/items?status=open - Filter by status"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items?status=open")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data["items"], list)
        # If there are items, verify they all have status=open
        for item in data["items"]:
            assert item.get("status") == "open", f"Expected status 'open', got '{item.get('status')}'"
        print(f"Open items: {len(data['items'])}")

    def test_list_items_with_severity_filter(self, api_client):
        """GET /api/cve/remediation/items?severity=critical - Filter by severity"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items?severity=critical")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data["items"], list)
        # If there are items, verify they all have severity=critical
        for item in data["items"]:
            assert item.get("severity") == "critical", f"Expected severity 'critical', got '{item.get('severity')}'"
        print(f"Critical items: {len(data['items'])}")

    def test_list_items_with_pagination(self, api_client):
        """GET /api/cve/remediation/items?limit=10&skip=0 - Pagination works"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/items?limit=10&skip=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 10, f"Expected limit 10, got {data['limit']}"
        assert data["skip"] == 0, f"Expected skip 0, got {data['skip']}"

# ═══════════════════════════════════════════════════════════════
# GitHub Issue/PR Creation Tests (Expect 400 due to read-only token)
# ═══════════════════════════════════════════════════════════════

class TestGitHubIntegration:
    """Tests for GitHub issue/PR creation - expect 400 with informative error due to read-only token"""

    def test_create_github_issue_permission_error(self, api_client):
        """POST /api/cve/remediation/create-issue/{cve_id} - Returns 400 with permission error (expected)"""
        response = api_client.post(f"{BASE_URL}/api/cve/remediation/create-issue/{TEST_CVE_ID}")
        
        # With read-only token, expect 400 Bad Request with permission error message
        # OR 200 if issue already exists
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data, "Error response should include 'detail'"
            detail = data["detail"].lower()
            # Should mention permissions or already exists
            has_permission_msg = "permission" in detail or "403" in detail or "already exists" in detail or "not found" in detail
            assert has_permission_msg, f"Error should mention permission issue or already exists, got: {data['detail']}"
            print(f"Expected behavior: 400 error with message: {data['detail']}")
        elif response.status_code == 200:
            data = response.json()
            print(f"Issue creation succeeded (issue may already exist): {data}")
        else:
            print(f"Status: {response.status_code}, Response: {response.text}")
            # Allow 404 if CVE not found
            assert response.status_code in [200, 400, 404], f"Unexpected status: {response.status_code}"

    def test_create_github_pr_permission_error(self, api_client):
        """POST /api/cve/remediation/create-pr/{cve_id} - Returns 400 with permission error (expected)"""
        response = api_client.post(f"{BASE_URL}/api/cve/remediation/create-pr/{TEST_CVE_ID}")
        
        # With read-only token, expect 400 Bad Request with permission error
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data, "Error response should include 'detail'"
            detail = data["detail"].lower()
            # Should mention permissions, package info missing, or similar
            has_expected_msg = "permission" in detail or "403" in detail or "missing" in detail or "not found" in detail
            assert has_expected_msg, f"Error should be informative, got: {data['detail']}"
            print(f"Expected behavior: 400 error with message: {data['detail']}")
        elif response.status_code == 200:
            data = response.json()
            print(f"PR creation succeeded: {data}")
        else:
            print(f"Status: {response.status_code}, Response: {response.text}")
            # Allow 404 if CVE not found
            assert response.status_code in [200, 400, 404], f"Unexpected status: {response.status_code}"

    def test_create_issue_nonexistent_cve(self, api_client):
        """POST /api/cve/remediation/create-issue/{invalid} - Returns 400 for invalid CVE"""
        response = api_client.post(f"{BASE_URL}/api/cve/remediation/create-issue/nonexistent-cve-id-12345")
        
        # Should return 400 with "CVE not found" error
        assert response.status_code == 400, f"Expected 400 for nonexistent CVE, got {response.status_code}"
        data = response.json()
        assert "not found" in data["detail"].lower() or "cve" in data["detail"].lower(), f"Should mention CVE not found: {data['detail']}"
        print(f"Correctly handles nonexistent CVE: {data['detail']}")

# ═══════════════════════════════════════════════════════════════
# Bulk Operations Tests
# ═══════════════════════════════════════════════════════════════

class TestBulkOperations:
    """Bulk issue creation tests"""

    def test_bulk_create_issues(self, api_client):
        """POST /api/cve/remediation/bulk-create-issues - Bulk creates issues for CVEs by severity"""
        payload = {"severity": "critical", "limit": 5}
        response = api_client.post(f"{BASE_URL}/api/cve/remediation/bulk-create-issues", json=payload)
        
        # May return 200 with results even if creation fails due to permissions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_processed" in data, "Response should include 'total_processed'"
        assert "created" in data, "Response should include 'created'"
        assert "skipped" in data, "Response should include 'skipped'"
        assert "errors" in data, "Response should include 'errors'"
        print(f"Bulk create results: processed={data['total_processed']}, created={len(data['created'])}, skipped={len(data['skipped'])}, errors={len(data['errors'])}")

# ═══════════════════════════════════════════════════════════════
# GitHub Sync Tests
# ═══════════════════════════════════════════════════════════════

class TestGitHubSync:
    """GitHub sync functionality tests"""

    def test_sync_github_status(self, api_client):
        """POST /api/cve/remediation/sync-github - Syncs remediation items with GitHub"""
        response = api_client.post(f"{BASE_URL}/api/cve/remediation/sync-github")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should return sync results
        assert "synced" in data or "error" in data, "Response should include 'synced' count or error"
        if "synced" in data:
            print(f"Sync completed: {data['synced']} items synced")
        else:
            print(f"Sync result: {data}")

# ═══════════════════════════════════════════════════════════════
# AWS Integration Tests
# ═══════════════════════════════════════════════════════════════

class TestAWSIntegration:
    """AWS Inspector and Security Hub integration tests"""

    def test_get_aws_findings(self, api_client):
        """GET /api/cve/remediation/aws/findings - Returns AWS Inspector findings"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/aws/findings")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "findings" in data, "Response should include 'findings'"
        assert "count" in data, "Response should include 'count'"
        assert "source" in data, "Response should include 'source'"
        
        # Findings may be empty if AWS Inspector has no active findings
        assert isinstance(data["findings"], list), "Findings should be a list"
        print(f"AWS findings: count={data['count']}, source={data['source']}")
        if data.get("note"):
            print(f"Note: {data['note']}")

    def test_get_security_hub_summary(self, api_client):
        """GET /api/cve/remediation/aws/security-hub - Returns Security Hub summary"""
        response = api_client.get(f"{BASE_URL}/api/cve/remediation/aws/security-hub")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "findings" in data, "Response should include 'findings'"
        assert "count" in data, "Response should include 'count'"
        assert "source" in data, "Response should include 'source'"
        print(f"Security Hub: count={data['count']}, source={data['source']}")
        if data.get("note"):
            print(f"Note: {data['note']}")

    def test_sync_aws_findings(self, api_client):
        """POST /api/cve/remediation/aws/sync - Syncs AWS findings into CVE database"""
        response = api_client.post(f"{BASE_URL}/api/cve/remediation/aws/sync")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "synced" in data or "error" in data, "Response should include sync result"
        print(f"AWS sync result: {data}")

# ═══════════════════════════════════════════════════════════════
# Remediation Item Status Update Tests
# ═══════════════════════════════════════════════════════════════

class TestRemediationStatusUpdate:
    """Tests for updating remediation item status"""

    def test_update_item_status_invalid_id(self, api_client):
        """PUT /api/cve/remediation/items/{invalid}/status - Returns 404 for invalid item"""
        payload = {"status": "closed", "notes": "Test note"}
        response = api_client.put(f"{BASE_URL}/api/cve/remediation/items/invalid-item-id/status", json=payload)
        
        assert response.status_code == 404, f"Expected 404 for invalid item, got {response.status_code}: {response.text}"
        print("Correctly returns 404 for invalid item ID")

    def test_update_item_status_invalid_status(self, api_client):
        """PUT /api/cve/remediation/items/{id}/status - Returns 404 for invalid status value"""
        # First get an item if one exists
        items_response = api_client.get(f"{BASE_URL}/api/cve/remediation/items?limit=1")
        items = items_response.json().get("items", [])
        
        if items:
            item_id = items[0]["id"]
            payload = {"status": "invalid_status_value", "notes": "Test"}
            response = api_client.put(f"{BASE_URL}/api/cve/remediation/items/{item_id}/status", json=payload)
            # Should fail with 404 or 422 due to invalid status
            assert response.status_code in [404, 422], f"Expected 404/422 for invalid status, got {response.status_code}"
            print(f"Correctly rejects invalid status: {response.status_code}")
        else:
            pytest.skip("No remediation items to test status update")

# ═══════════════════════════════════════════════════════════════
# Integration Flow Test
# ═══════════════════════════════════════════════════════════════

class TestRemediationWorkflow:
    """End-to-end workflow tests"""

    def test_full_remediation_flow(self, api_client):
        """Test the complete remediation flow from config to items"""
        # 1. Get config
        config_response = api_client.get(f"{BASE_URL}/api/cve/remediation/config")
        assert config_response.status_code == 200
        config = config_response.json()
        print(f"Step 1: Config loaded - GitHub connected: {config['repo_connected']}")
        
        # 2. Get stats
        stats_response = api_client.get(f"{BASE_URL}/api/cve/remediation/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        print(f"Step 2: Stats loaded - Total items: {stats['total']}")
        
        # 3. List items
        items_response = api_client.get(f"{BASE_URL}/api/cve/remediation/items")
        assert items_response.status_code == 200
        items = items_response.json()
        print(f"Step 3: Items listed - Count: {items['total']}")
        
        # 4. Test AWS findings
        aws_response = api_client.get(f"{BASE_URL}/api/cve/remediation/aws/findings")
        assert aws_response.status_code == 200
        aws = aws_response.json()
        print(f"Step 4: AWS findings - Count: {aws['count']}, Source: {aws['source']}")
        
        # 5. Test sync
        sync_response = api_client.post(f"{BASE_URL}/api/cve/remediation/sync-github")
        assert sync_response.status_code == 200
        print(f"Step 5: GitHub sync completed")
        
        print("✓ Full remediation workflow completed successfully")
