"""
Test Security Audit CVE Monitoring APIs
Tests all endpoints under /api/security/
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestSecurityAuditHealth:
    """Test health endpoint"""
    
    def test_health_endpoint(self, api_client):
        """GET /api/security/health - should return healthy status"""
        response = api_client.get(f"{BASE_URL}/api/security/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data, "Response should contain 'status'"
        assert data["status"] == "healthy", f"Expected status 'healthy', got {data['status']}"
        assert "service" in data, "Response should contain 'service'"
        print(f"✓ Health check passed: {data}")


class TestSecurityAuditScanning:
    """Test audit scanning endpoints"""
    
    def test_full_audit(self, api_client):
        """GET /api/security/audit - runs full security audit"""
        response = api_client.get(f"{BASE_URL}/api/security/audit")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "security_score" in data, "Response should contain 'security_score'"
        assert "grade" in data, "Response should contain 'grade'"
        assert "total_vulnerabilities" in data, "Response should contain 'total_vulnerabilities'"
        assert "severity_breakdown" in data, "Response should contain 'severity_breakdown'"
        assert "frontend" in data, "Response should contain 'frontend'"
        assert "backend" in data, "Response should contain 'backend'"
        
        # Validate data types
        assert isinstance(data["security_score"], (int, float)), "security_score should be numeric"
        assert data["grade"] in ["A", "B", "C", "D", "F"], f"Invalid grade: {data['grade']}"
        assert isinstance(data["total_vulnerabilities"], int), "total_vulnerabilities should be int"
        
        print(f"✓ Full audit passed - Score: {data['security_score']}, Grade: {data['grade']}, Vulns: {data['total_vulnerabilities']}")
    
    def test_force_fresh_scan(self, api_client):
        """GET /api/security/audit?force=true - bypass cache and run fresh scan"""
        response = api_client.get(f"{BASE_URL}/api/security/audit?force=true")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "timestamp" in data, "Response should contain 'timestamp'"
        # Force scan should not be cached
        if "cached" in data:
            assert data["cached"] == False, "Force scan should not be cached"
        
        print(f"✓ Force scan passed - Timestamp: {data['timestamp']}")
    
    def test_frontend_audit(self, api_client):
        """GET /api/security/audit/frontend - frontend-only audit"""
        response = api_client.get(f"{BASE_URL}/api/security/audit/frontend")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "vulnerabilities" in data, "Response should contain 'vulnerabilities'"
        assert "summary" in data, "Response should contain 'summary'"
        assert isinstance(data["vulnerabilities"], list), "vulnerabilities should be a list"
        
        print(f"✓ Frontend audit passed - Found {len(data['vulnerabilities'])} vulnerabilities")
    
    def test_backend_audit(self, api_client):
        """GET /api/security/audit/backend - backend-only audit"""
        response = api_client.get(f"{BASE_URL}/api/security/audit/backend")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "vulnerabilities" in data, "Response should contain 'vulnerabilities'"
        assert "summary" in data, "Response should contain 'summary'"
        assert isinstance(data["vulnerabilities"], list), "vulnerabilities should be a list"
        
        print(f"✓ Backend audit passed - Found {len(data['vulnerabilities'])} vulnerabilities")


class TestSecurityAuditHistory:
    """Test audit history and trend endpoints"""
    
    def test_audit_history(self, api_client):
        """GET /api/security/audit/history - returns audit history records"""
        response = api_client.get(f"{BASE_URL}/api/security/audit/history?limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            record = data[0]
            assert "timestamp" in record, "History record should contain 'timestamp'"
            assert "security_score" in record, "History record should contain 'security_score'"
            assert "grade" in record, "History record should contain 'grade'"
            assert "total_vulnerabilities" in record, "History record should contain 'total_vulnerabilities'"
        
        print(f"✓ Audit history passed - Found {len(data)} records")
    
    def test_trend_data(self, api_client):
        """GET /api/security/audit/trend - returns trend data"""
        response = api_client.get(f"{BASE_URL}/api/security/audit/trend?days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"✓ Trend data passed - Found {len(data)} data points")


class TestMonitorConfiguration:
    """Test monitor configuration endpoints"""
    
    def test_get_monitor_config(self, api_client):
        """GET /api/security/monitor/config - returns monitor configuration"""
        response = api_client.get(f"{BASE_URL}/api/security/monitor/config")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "enabled" in data, "Response should contain 'enabled'"
        assert "interval_hours" in data, "Response should contain 'interval_hours'"
        assert "alert_on_critical" in data, "Response should contain 'alert_on_critical'"
        assert "alert_on_high" in data, "Response should contain 'alert_on_high'"
        assert "alert_on_moderate" in data, "Response should contain 'alert_on_moderate'"
        assert "alert_on_low" in data, "Response should contain 'alert_on_low'"
        
        print(f"✓ Monitor config passed - Enabled: {data['enabled']}, Interval: {data['interval_hours']}h")
        return data
    
    def test_update_monitor_config_enable(self, api_client):
        """PUT /api/security/monitor/config - enable monitor"""
        response = api_client.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"enabled": True, "interval_hours": 24}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["enabled"] == True, "Monitor should be enabled"
        assert data["interval_hours"] == 24, "Interval should be 24 hours"
        
        print(f"✓ Enable monitor passed - Enabled: {data['enabled']}")
    
    def test_update_monitor_config_severity(self, api_client):
        """PUT /api/security/monitor/config - update severity filters"""
        response = api_client.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={
                "alert_on_critical": True,
                "alert_on_high": True,
                "alert_on_moderate": True,
                "alert_on_low": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["alert_on_critical"] == True, "alert_on_critical should be True"
        assert data["alert_on_high"] == True, "alert_on_high should be True"
        assert data["alert_on_moderate"] == True, "alert_on_moderate should be True"
        assert data["alert_on_low"] == False, "alert_on_low should be False"
        
        print(f"✓ Update severity filters passed")
    
    def test_update_monitor_config_disable(self, api_client):
        """PUT /api/security/monitor/config - disable monitor"""
        response = api_client.put(
            f"{BASE_URL}/api/security/monitor/config",
            json={"enabled": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["enabled"] == False, "Monitor should be disabled"
        
        print(f"✓ Disable monitor passed - Enabled: {data['enabled']}")


class TestManualScan:
    """Test manual scan endpoint"""
    
    def test_scan_now(self, api_client):
        """POST /api/security/monitor/scan-now - trigger manual scan"""
        response = api_client.post(f"{BASE_URL}/api/security/monitor/scan-now")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "scan" in data, "Response should contain 'scan'"
        assert "config" in data, "Response should contain 'config'"
        
        # Validate scan result
        scan = data["scan"]
        assert "security_score" in scan, "Scan should contain 'security_score'"
        assert "grade" in scan, "Scan should contain 'grade'"
        assert "total_vulnerabilities" in scan, "Scan should contain 'total_vulnerabilities'"
        
        print(f"✓ Manual scan passed - Score: {scan['security_score']}, Grade: {scan['grade']}")


class TestAlerts:
    """Test alerts endpoints"""
    
    def test_get_alerts(self, api_client):
        """GET /api/security/alerts - returns list of alerts"""
        response = api_client.get(f"{BASE_URL}/api/security/alerts")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            alert = data[0]
            assert "type" in alert, "Alert should contain 'type'"
            assert "severity" in alert, "Alert should contain 'severity'"
            assert "timestamp" in alert, "Alert should contain 'timestamp'"
        
        print(f"✓ Get alerts passed - Found {len(data)} alerts")
    
    def test_get_alert_count(self, api_client):
        """GET /api/security/alerts/count - returns unread and total count"""
        response = api_client.get(f"{BASE_URL}/api/security/alerts/count")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "unread" in data, "Response should contain 'unread'"
        assert "total" in data, "Response should contain 'total'"
        assert isinstance(data["unread"], int), "unread should be int"
        assert isinstance(data["total"], int), "total should be int"
        
        print(f"✓ Alert count passed - Unread: {data['unread']}, Total: {data['total']}")
    
    def test_mark_alerts_read(self, api_client):
        """POST /api/security/alerts/read - mark alerts as read"""
        response = api_client.post(
            f"{BASE_URL}/api/security/alerts/read",
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "marked_read" in data, "Response should contain 'marked_read'"
        
        print(f"✓ Mark alerts read passed - Marked {data['marked_read']} alerts as read")
    
    def test_dismiss_alerts(self, api_client):
        """POST /api/security/alerts/dismiss - dismiss alerts"""
        response = api_client.post(
            f"{BASE_URL}/api/security/alerts/dismiss",
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "dismissed" in data, "Response should contain 'dismissed'"
        
        print(f"✓ Dismiss alerts passed - Dismissed {data['dismissed']} alerts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
