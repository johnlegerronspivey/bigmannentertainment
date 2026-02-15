"""
CVE Reporting & Analytics API Tests
Tests for:
- Executive Summary API
- Trend Analysis API
- Severity Trends API
- Team Performance API
- Scanner Stats API
- Status Distribution API
- CSV Export APIs (cves, executive, team)
- Saved Reports CRUD
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Base URL from environment
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
REPORTING_API = f"{BASE_URL}/api/cve/reporting"


class TestExecutiveSummary:
    """Executive Summary endpoint tests - GET /api/cve/reporting/summary"""

    def test_summary_default_30_days(self):
        """Test executive summary with default 30 days"""
        response = requests.get(f"{REPORTING_API}/summary")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Validate structure
        assert "period_days" in data
        assert "total_cves" in data
        assert "total_open" in data
        assert "total_closed" in data
        assert "risk_score" in data
        assert "sla_compliance" in data
        assert "resolution_rate" in data
        assert "mttr_hours" in data
        assert "severity_distribution" in data
        
        # Validate types
        assert isinstance(data["total_cves"], int)
        assert isinstance(data["total_open"], int)
        assert isinstance(data["total_closed"], int)
        assert isinstance(data["risk_score"], int)
        assert isinstance(data["sla_compliance"], (int, float))
        assert isinstance(data["resolution_rate"], (int, float))
        assert isinstance(data["mttr_hours"], (int, float))
        assert isinstance(data["severity_distribution"], dict)
        
        print(f"Executive Summary: {data['total_cves']} CVEs, {data['total_open']} open, {data['total_closed']} closed")
        print(f"Risk Score: {data['risk_score']}, SLA Compliance: {data['sla_compliance']}%")

    def test_summary_custom_7_days(self):
        """Test executive summary with 7 days period"""
        response = requests.get(f"{REPORTING_API}/summary?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 7
        print(f"7-day summary: new_in_period={data.get('new_in_period')}, fixed_in_period={data.get('fixed_in_period')}")

    def test_summary_custom_90_days(self):
        """Test executive summary with 90 days period"""
        response = requests.get(f"{REPORTING_API}/summary?days=90")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 90

    def test_summary_severity_distribution(self):
        """Test severity distribution breakdown"""
        response = requests.get(f"{REPORTING_API}/summary")
        assert response.status_code == 200
        
        data = response.json()
        severity_dist = data.get("severity_distribution", {})
        
        # Check severity levels exist
        assert "critical" in severity_dist
        assert "high" in severity_dist
        assert "medium" in severity_dist
        assert "low" in severity_dist
        
        print(f"Severity Distribution: {severity_dist}")


class TestTrendAnalysis:
    """Trend Analysis endpoint tests - GET /api/cve/reporting/trends"""

    def test_trends_default(self):
        """Test CVE trends with default 30 days"""
        response = requests.get(f"{REPORTING_API}/trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
        assert "period_days" in data
        assert isinstance(data["trends"], list)
        
        if data["trends"]:
            trend = data["trends"][0]
            assert "date" in trend
            assert "label" in trend
            assert "discovered" in trend
            assert "resolved" in trend
            assert "backlog" in trend
            
        print(f"Trends: {len(data['trends'])} data points")

    def test_trends_7_days(self):
        """Test CVE trends with 7 days period"""
        response = requests.get(f"{REPORTING_API}/trends?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 7
        # 7 days = 8 data points (day 0 through day 7)
        assert len(data["trends"]) >= 7

    def test_trends_data_structure(self):
        """Validate trend data structure for charting"""
        response = requests.get(f"{REPORTING_API}/trends?days=7")
        assert response.status_code == 200
        
        data = response.json()
        for trend in data["trends"]:
            # All values should be integers
            assert isinstance(trend["discovered"], int)
            assert isinstance(trend["resolved"], int)
            assert isinstance(trend["backlog"], int)


class TestSeverityTrends:
    """Severity Trends endpoint tests - GET /api/cve/reporting/severity-trends"""

    def test_severity_trends_default(self):
        """Test severity trends with default 30 days"""
        response = requests.get(f"{REPORTING_API}/severity-trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
        assert "period_days" in data
        assert isinstance(data["trends"], list)
        
        if data["trends"]:
            trend = data["trends"][0]
            assert "date" in trend
            assert "label" in trend
            assert "critical" in trend
            assert "high" in trend
            assert "medium" in trend
            assert "low" in trend
            
        print(f"Severity Trends: {len(data['trends'])} data points")

    def test_severity_trends_7_days(self):
        """Test severity trends with 7 days period"""
        response = requests.get(f"{REPORTING_API}/severity-trends?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 7


class TestTeamPerformance:
    """Team Performance endpoint tests - GET /api/cve/reporting/team-performance"""

    def test_team_performance(self):
        """Test team performance metrics"""
        response = requests.get(f"{REPORTING_API}/team-performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "teams" in data
        assert "total_owners" in data
        assert isinstance(data["teams"], list)
        
        if data["teams"]:
            team = data["teams"][0]
            assert "owner" in team
            assert "assigned" in team
            assert "open" in team
            assert "resolved" in team
            assert "resolution_rate" in team
            assert "avg_resolution_hours" in team
            
            # Validate types
            assert isinstance(team["assigned"], int)
            assert isinstance(team["open"], int)
            assert isinstance(team["resolved"], int)
            assert isinstance(team["resolution_rate"], (int, float))
            assert isinstance(team["avg_resolution_hours"], (int, float))
            
        print(f"Team Performance: {data['total_owners']} team members")
        for t in data["teams"][:3]:
            print(f"  - {t['owner']}: {t['assigned']} assigned, {t['resolved']} resolved ({t['resolution_rate']}%)")


class TestScannerStats:
    """Scanner Stats endpoint tests - GET /api/cve/reporting/scanner-stats"""

    def test_scanner_stats(self):
        """Test scanner effectiveness statistics"""
        response = requests.get(f"{REPORTING_API}/scanner-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "scanners" in data
        assert isinstance(data["scanners"], list)
        
        if data["scanners"]:
            scanner = data["scanners"][0]
            assert "scanner" in scanner
            assert "total_scans" in scanner
            assert "cves_found" in scanner
            assert "avg_findings_per_scan" in scanner
            
        print(f"Scanner Stats: {len(data['scanners'])} scanners")
        for s in data["scanners"]:
            print(f"  - {s['scanner']}: {s['total_scans']} scans, {s['cves_found']} CVEs found")


class TestStatusDistribution:
    """Status Distribution endpoint tests - GET /api/cve/reporting/status-distribution"""

    def test_status_distribution(self):
        """Test CVE status distribution"""
        response = requests.get(f"{REPORTING_API}/status-distribution")
        assert response.status_code == 200
        
        data = response.json()
        assert "distribution" in data
        assert "total" in data
        
        dist = data["distribution"]
        # Check expected statuses exist
        expected_statuses = ["detected", "triaged", "in_progress", "fixed", "verified", "dismissed", "wont_fix"]
        for status in expected_statuses:
            assert status in dist, f"Missing status: {status}"
            assert isinstance(dist[status], int)
            
        # Total should match sum
        total = sum(dist.values())
        assert data["total"] == total
        
        print(f"Status Distribution: {dist}")


class TestCSVExport:
    """CSV Export endpoint tests"""

    def test_export_cves_csv(self):
        """Test CVE database export - GET /api/cve/reporting/export/cves"""
        response = requests.get(f"{REPORTING_API}/export/cves")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/csv; charset=utf-8"
        assert "attachment; filename=cve_export.csv" in response.headers.get("content-disposition", "")
        
        # Validate CSV content
        content = response.text
        lines = content.strip().split("\n")
        assert len(lines) >= 1  # At least header
        
        # Check header
        header = lines[0]
        assert "CVE ID" in header
        assert "Title" in header
        assert "Severity" in header
        assert "Status" in header
        
        print(f"CVE Export: {len(lines)} lines (including header)")

    def test_export_cves_with_filter(self):
        """Test CVE export with severity filter"""
        response = requests.get(f"{REPORTING_API}/export/cves?severity=critical")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/csv; charset=utf-8"

    def test_export_executive_csv(self):
        """Test executive summary export - GET /api/cve/reporting/export/executive"""
        response = requests.get(f"{REPORTING_API}/export/executive?days=30")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/csv; charset=utf-8"
        assert "attachment; filename=executive_report.csv" in response.headers.get("content-disposition", "")
        
        # Validate CSV content
        content = response.text
        assert "CVE Executive Report" in content
        assert "Total CVEs" in content
        assert "Open CVEs" in content
        assert "Severity Distribution" in content
        
        print(f"Executive Export: {len(content)} bytes")

    def test_export_team_csv(self):
        """Test team performance export - GET /api/cve/reporting/export/team"""
        response = requests.get(f"{REPORTING_API}/export/team")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/csv; charset=utf-8"
        assert "attachment; filename=team_performance.csv" in response.headers.get("content-disposition", "")
        
        # Validate CSV content
        content = response.text
        lines = content.strip().split("\n")
        assert len(lines) >= 1  # At least header
        
        header = lines[0]
        assert "Owner" in header
        assert "Assigned" in header
        assert "Resolved" in header
        
        print(f"Team Export: {len(lines)} lines")


class TestSavedReports:
    """Saved Reports CRUD tests"""

    def test_saved_reports_crud_flow(self):
        """Test create, read, delete saved report"""
        # CREATE
        report_name = f"TEST_Report_{uuid.uuid4().hex[:8]}"
        create_payload = {
            "name": report_name,
            "report_type": "executive",
            "config": {"days": 30}
        }
        
        create_response = requests.post(
            f"{REPORTING_API}/saved",
            json=create_payload,
            headers={"Content-Type": "application/json"}
        )
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        
        created_report = create_response.json()
        assert created_report["name"] == report_name
        assert created_report["report_type"] == "executive"
        assert "id" in created_report
        assert "created_at" in created_report
        
        report_id = created_report["id"]
        print(f"Created report: {report_id}")
        
        # READ
        get_response = requests.get(f"{REPORTING_API}/saved")
        assert get_response.status_code == 200
        
        saved_reports = get_response.json()
        assert "reports" in saved_reports
        
        # Verify created report exists in list
        report_ids = [r["id"] for r in saved_reports["reports"]]
        assert report_id in report_ids, "Created report not found in saved reports list"
        print(f"Found {len(saved_reports['reports'])} saved reports")
        
        # DELETE
        delete_response = requests.delete(f"{REPORTING_API}/saved/{report_id}")
        assert delete_response.status_code == 200
        
        delete_result = delete_response.json()
        assert delete_result["deleted"] == True
        print(f"Deleted report: {report_id}")
        
        # VERIFY DELETION
        verify_response = requests.get(f"{REPORTING_API}/saved")
        assert verify_response.status_code == 200
        
        remaining_reports = verify_response.json()
        remaining_ids = [r["id"] for r in remaining_reports["reports"]]
        assert report_id not in remaining_ids, "Report still exists after deletion"

    def test_list_saved_reports(self):
        """Test listing saved reports"""
        response = requests.get(f"{REPORTING_API}/saved")
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)
        
        print(f"Saved Reports: {len(data['reports'])} reports")

    def test_delete_nonexistent_report(self):
        """Test deleting non-existent report"""
        fake_id = str(uuid.uuid4())
        response = requests.delete(f"{REPORTING_API}/saved/{fake_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted"] == False


class TestEdgeCases:
    """Edge case and validation tests"""

    def test_summary_invalid_days_too_low(self):
        """Test summary with days below minimum (7)"""
        response = requests.get(f"{REPORTING_API}/summary?days=1")
        # Should return 422 validation error
        assert response.status_code == 422

    def test_summary_invalid_days_too_high(self):
        """Test summary with days above maximum (365)"""
        response = requests.get(f"{REPORTING_API}/summary?days=500")
        # Should return 422 validation error
        assert response.status_code == 422

    def test_trends_invalid_days(self):
        """Test trends with invalid days parameter"""
        response = requests.get(f"{REPORTING_API}/trends?days=5")
        # Should return 422 validation error
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
