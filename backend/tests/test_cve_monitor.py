"""
CVE Monitor API Tests
Tests for the Automated CVE Monitoring Dashboard feature.
Endpoints: /api/cve-monitor/*
Features: Health check, stats, feed, watches, alerts
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_PREFIX = f"{BASE_URL}/api/cve-monitor"

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestCVEMonitorHealth:
    """Health check endpoint tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """GET /api/cve-monitor/health - should return healthy status"""
        response = requests.get(f"{API_PREFIX}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy status, got: {data}"
        assert "service" in data, "Response should include service name"
        print(f"✓ Health check passed: {data}")


class TestCVEMonitorStats:
    """Stats endpoint tests"""
    
    def test_stats_endpoint_returns_data(self):
        """GET /api/cve-monitor/stats - should return monitoring statistics"""
        response = requests.get(f"{API_PREFIX}/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify required fields
        assert "total_feed_entries" in data, "Stats should include total_feed_entries"
        assert "total_watches" in data, "Stats should include total_watches"
        assert "active_watches" in data, "Stats should include active_watches"
        assert "total_alerts" in data, "Stats should include total_alerts"
        assert "new_alerts" in data, "Stats should include new_alerts"
        assert "severity_breakdown" in data, "Stats should include severity_breakdown"
        assert "daily_trend" in data, "Stats should include daily_trend"
        
        # Verify severity breakdown structure
        severity = data["severity_breakdown"]
        for sev in ["critical", "high", "medium", "low", "info"]:
            assert sev in severity, f"Severity breakdown should include {sev}"
        
        # Verify daily trend is a list
        assert isinstance(data["daily_trend"], list), "daily_trend should be a list"
        
        print(f"✓ Stats endpoint passed: {data['total_feed_entries']} feed entries, {data['total_alerts']} alerts")


class TestCVEMonitorFeed:
    """Feed endpoint tests"""
    
    def test_get_feed_returns_items(self):
        """GET /api/cve-monitor/feed - should return cached CVE feed entries"""
        response = requests.get(f"{API_PREFIX}/feed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "items" in data, "Feed response should include items"
        assert "total" in data, "Feed response should include total"
        assert isinstance(data["items"], list), "items should be a list"
        
        print(f"✓ Feed endpoint passed: {len(data['items'])} items, {data['total']} total")
    
    def test_get_feed_with_severity_filter(self):
        """GET /api/cve-monitor/feed?severity=critical - should filter by severity"""
        response = requests.get(f"{API_PREFIX}/feed", params={"severity": "critical"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # All items should have critical severity
        for item in data["items"]:
            assert item.get("severity") == "critical", f"Expected critical severity, got: {item.get('severity')}"
        
        print(f"✓ Feed severity filter passed: {len(data['items'])} critical items")
    
    def test_get_feed_with_search(self):
        """GET /api/cve-monitor/feed?search=CVE - should search CVE ID or description"""
        response = requests.get(f"{API_PREFIX}/feed", params={"search": "CVE"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data["items"], list), "items should be a list"
        print(f"✓ Feed search passed: {len(data['items'])} items matching 'CVE'")
    
    def test_get_feed_with_limit(self):
        """GET /api/cve-monitor/feed?limit=5 - should limit results"""
        response = requests.get(f"{API_PREFIX}/feed", params={"limit": 5})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert len(data["items"]) <= 5, f"Expected max 5 items, got {len(data['items'])}"
        print(f"✓ Feed limit passed: {len(data['items'])} items (limit=5)")


class TestCVEMonitorFeedRefresh:
    """Feed refresh endpoint tests - Note: NVD API has rate limiting"""
    
    def test_refresh_feed_endpoint(self):
        """POST /api/cve-monitor/feed/refresh - should fetch fresh CVEs from NVD"""
        response = requests.post(f"{API_PREFIX}/feed/refresh", params={"days": 7})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Response should include fetch results
        assert "items" in data or "fetched" in data, "Refresh response should include items or fetched count"
        assert "source" in data, "Refresh response should include source"
        
        print(f"✓ Feed refresh passed: source={data.get('source')}, fetched={data.get('fetched', len(data.get('items', [])))}")


class TestCVEMonitorWatches:
    """Watch rules CRUD tests"""
    
    @pytest.fixture
    def created_watch_id(self):
        """Create a test watch and return its ID for cleanup"""
        watch_data = {
            "name": f"TEST_Watch_{uuid.uuid4().hex[:8]}",
            "keyword": "test-keyword",
            "watch_type": "keyword",
            "severity_filter": "all"
        }
        response = requests.post(f"{API_PREFIX}/watches", json=watch_data)
        assert response.status_code == 200, f"Failed to create watch: {response.text}"
        watch = response.json()
        yield watch["id"]
        # Cleanup
        requests.delete(f"{API_PREFIX}/watches/{watch['id']}")
    
    def test_create_watch(self):
        """POST /api/cve-monitor/watches - should create a new watch rule"""
        watch_data = {
            "name": f"TEST_Watch_{uuid.uuid4().hex[:8]}",
            "keyword": "python",
            "watch_type": "keyword",
            "severity_filter": "high"
        }
        response = requests.post(f"{API_PREFIX}/watches", json=watch_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "id" in data, "Watch should have an id"
        assert data["name"] == watch_data["name"], "Watch name should match"
        assert data["keyword"] == watch_data["keyword"], "Watch keyword should match"
        assert data["watch_type"] == watch_data["watch_type"], "Watch type should match"
        assert data["severity_filter"] == watch_data["severity_filter"], "Severity filter should match"
        assert data["enabled"] == True, "New watch should be enabled by default"
        
        # Cleanup
        requests.delete(f"{API_PREFIX}/watches/{data['id']}")
        print(f"✓ Create watch passed: {data['name']}")
    
    def test_list_watches(self):
        """GET /api/cve-monitor/watches - should list all watch rules"""
        response = requests.get(f"{API_PREFIX}/watches")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Watches response should be a list"
        print(f"✓ List watches passed: {len(data)} watches")
    
    def test_toggle_watch(self, created_watch_id):
        """PUT /api/cve-monitor/watches/{id}/toggle - should toggle watch enabled/disabled"""
        # Get initial state
        response = requests.get(f"{API_PREFIX}/watches")
        watches = response.json()
        watch = next((w for w in watches if w["id"] == created_watch_id), None)
        assert watch is not None, "Created watch should exist"
        initial_enabled = watch["enabled"]
        
        # Toggle
        response = requests.put(f"{API_PREFIX}/watches/{created_watch_id}/toggle")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["enabled"] != initial_enabled, "Watch enabled state should be toggled"
        print(f"✓ Toggle watch passed: enabled={data['enabled']}")
    
    def test_delete_watch(self):
        """DELETE /api/cve-monitor/watches/{id} - should delete a watch rule"""
        # Create a watch to delete
        watch_data = {
            "name": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
            "keyword": "delete-test",
            "watch_type": "keyword",
            "severity_filter": "all"
        }
        create_response = requests.post(f"{API_PREFIX}/watches", json=watch_data)
        watch_id = create_response.json()["id"]
        
        # Delete
        response = requests.delete(f"{API_PREFIX}/watches/{watch_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("deleted") == True, "Delete response should confirm deletion"
        
        # Verify deletion
        response = requests.get(f"{API_PREFIX}/watches")
        watches = response.json()
        assert not any(w["id"] == watch_id for w in watches), "Deleted watch should not exist"
        
        print(f"✓ Delete watch passed")
    
    def test_delete_nonexistent_watch(self):
        """DELETE /api/cve-monitor/watches/{id} - should return 404 for non-existent watch"""
        fake_id = str(uuid.uuid4())
        response = requests.delete(f"{API_PREFIX}/watches/{fake_id}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Delete non-existent watch returns 404")
    
    def test_toggle_nonexistent_watch(self):
        """PUT /api/cve-monitor/watches/{id}/toggle - should return 404 for non-existent watch"""
        fake_id = str(uuid.uuid4())
        response = requests.put(f"{API_PREFIX}/watches/{fake_id}/toggle")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Toggle non-existent watch returns 404")


class TestCVEMonitorWatchRefresh:
    """Watch refresh endpoint tests"""
    
    def test_refresh_watch(self):
        """POST /api/cve-monitor/watches/{id}/refresh - should refresh a specific watch"""
        # Create a watch to refresh
        watch_data = {
            "name": f"TEST_Refresh_{uuid.uuid4().hex[:8]}",
            "keyword": "linux",
            "watch_type": "keyword",
            "severity_filter": "all"
        }
        create_response = requests.post(f"{API_PREFIX}/watches", json=watch_data)
        watch_id = create_response.json()["id"]
        
        try:
            # Refresh
            response = requests.post(f"{API_PREFIX}/watches/{watch_id}/refresh")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            assert "watch_id" in data or "keyword" in data, "Refresh response should include watch info"
            print(f"✓ Refresh watch passed: {data}")
        finally:
            # Cleanup
            requests.delete(f"{API_PREFIX}/watches/{watch_id}")
    
    def test_refresh_nonexistent_watch(self):
        """POST /api/cve-monitor/watches/{id}/refresh - should handle non-existent watch"""
        fake_id = str(uuid.uuid4())
        response = requests.post(f"{API_PREFIX}/watches/{fake_id}/refresh")
        # Should return 200 with error message or 404
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.text}"
        if response.status_code == 200:
            data = response.json()
            assert "error" in data, "Should return error for non-existent watch"
        print(f"✓ Refresh non-existent watch handled correctly")


class TestCVEMonitorAlerts:
    """Alerts endpoint tests"""
    
    def test_get_alerts(self):
        """GET /api/cve-monitor/alerts - should list alerts"""
        response = requests.get(f"{API_PREFIX}/alerts")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "items" in data, "Alerts response should include items"
        assert "total" in data, "Alerts response should include total"
        assert "new_count" in data, "Alerts response should include new_count"
        assert isinstance(data["items"], list), "items should be a list"
        
        print(f"✓ Get alerts passed: {len(data['items'])} items, {data['new_count']} new")
    
    def test_get_alerts_with_status_filter(self):
        """GET /api/cve-monitor/alerts?status=new - should filter by status"""
        response = requests.get(f"{API_PREFIX}/alerts", params={"status": "new"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # All items should have 'new' status
        for item in data["items"]:
            assert item.get("status") == "new", f"Expected new status, got: {item.get('status')}"
        
        print(f"✓ Alerts status filter passed: {len(data['items'])} new alerts")
    
    def test_get_alerts_with_severity_filter(self):
        """GET /api/cve-monitor/alerts?severity=critical - should filter by severity"""
        response = requests.get(f"{API_PREFIX}/alerts", params={"severity": "critical"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # All items should have critical severity
        for item in data["items"]:
            assert item.get("severity") == "critical", f"Expected critical severity, got: {item.get('severity')}"
        
        print(f"✓ Alerts severity filter passed: {len(data['items'])} critical alerts")


class TestCVEMonitorAlertActions:
    """Alert acknowledge/dismiss tests"""
    
    def test_acknowledge_alert(self):
        """PUT /api/cve-monitor/alerts/{id}/acknowledge - should acknowledge an alert"""
        # Get a new alert to acknowledge
        response = requests.get(f"{API_PREFIX}/alerts", params={"status": "new", "limit": 1})
        data = response.json()
        
        if len(data["items"]) == 0:
            pytest.skip("No new alerts to acknowledge")
        
        alert_id = data["items"][0]["id"]
        
        # Acknowledge
        response = requests.put(f"{API_PREFIX}/alerts/{alert_id}/acknowledge")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()
        
        assert result.get("status") == "acknowledged", f"Alert should be acknowledged, got: {result.get('status')}"
        print(f"✓ Acknowledge alert passed: {alert_id}")
    
    def test_dismiss_alert(self):
        """PUT /api/cve-monitor/alerts/{id}/dismiss - should dismiss an alert"""
        # Get an alert to dismiss (new or acknowledged)
        response = requests.get(f"{API_PREFIX}/alerts", params={"limit": 1})
        data = response.json()
        
        if len(data["items"]) == 0:
            pytest.skip("No alerts to dismiss")
        
        alert_id = data["items"][0]["id"]
        
        # Dismiss
        response = requests.put(f"{API_PREFIX}/alerts/{alert_id}/dismiss")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()
        
        assert result.get("status") == "dismissed", f"Alert should be dismissed, got: {result.get('status')}"
        print(f"✓ Dismiss alert passed: {alert_id}")
    
    def test_acknowledge_nonexistent_alert(self):
        """PUT /api/cve-monitor/alerts/{id}/acknowledge - should return 404 for non-existent alert"""
        fake_id = str(uuid.uuid4())
        response = requests.put(f"{API_PREFIX}/alerts/{fake_id}/acknowledge")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Acknowledge non-existent alert returns 404")
    
    def test_dismiss_nonexistent_alert(self):
        """PUT /api/cve-monitor/alerts/{id}/dismiss - should return 404 for non-existent alert"""
        fake_id = str(uuid.uuid4())
        response = requests.put(f"{API_PREFIX}/alerts/{fake_id}/dismiss")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Dismiss non-existent alert returns 404")
    
    def test_acknowledge_all_alerts(self):
        """POST /api/cve-monitor/alerts/acknowledge-all - should acknowledge all new alerts"""
        response = requests.post(f"{API_PREFIX}/alerts/acknowledge-all")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "acknowledged" in data, "Response should include acknowledged count"
        print(f"✓ Acknowledge all alerts passed: {data['acknowledged']} acknowledged")


class TestCVEMonitorFeedItemStructure:
    """Verify feed item structure"""
    
    def test_feed_item_has_required_fields(self):
        """Feed items should have all required fields"""
        response = requests.get(f"{API_PREFIX}/feed", params={"limit": 1})
        assert response.status_code == 200
        data = response.json()
        
        if len(data["items"]) == 0:
            pytest.skip("No feed items to verify")
        
        item = data["items"][0]
        required_fields = ["cve_id", "description", "severity", "cvss_score", "published"]
        
        for field in required_fields:
            assert field in item, f"Feed item should have {field}"
        
        # Verify no MongoDB _id
        assert "_id" not in item, "Feed item should not expose MongoDB _id"
        
        print(f"✓ Feed item structure verified: {item['cve_id']}")


class TestCVEMonitorAlertStructure:
    """Verify alert structure"""
    
    def test_alert_has_required_fields(self):
        """Alerts should have all required fields"""
        response = requests.get(f"{API_PREFIX}/alerts", params={"limit": 1})
        assert response.status_code == 200
        data = response.json()
        
        if len(data["items"]) == 0:
            pytest.skip("No alerts to verify")
        
        alert = data["items"][0]
        required_fields = ["id", "cve_id", "severity", "status", "created_at"]
        
        for field in required_fields:
            assert field in alert, f"Alert should have {field}"
        
        # Verify no MongoDB _id
        assert "_id" not in alert, "Alert should not expose MongoDB _id"
        
        print(f"✓ Alert structure verified: {alert['cve_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
