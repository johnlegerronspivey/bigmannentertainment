"""
PDF Export and Dashboard Trends Backend Tests
Tests the new PDF export endpoints and dashboard-trends endpoint added in this iteration.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

class TestPDFExportEndpoints:
    """Tests for the new PDF export endpoints"""

    def test_executive_pdf_returns_200(self):
        """GET /api/cve/reporting/export/executive-pdf returns 200"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/executive-pdf?days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Executive PDF endpoint returns 200")

    def test_executive_pdf_content_type(self):
        """Executive PDF has correct content-type: application/pdf"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/executive-pdf?days=30")
        assert "application/pdf" in response.headers.get("content-type", ""), \
            f"Expected application/pdf, got {response.headers.get('content-type')}"
        print("PASS: Executive PDF content-type is application/pdf")

    def test_executive_pdf_valid_header(self):
        """Executive PDF starts with %PDF- header (valid PDF)"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/executive-pdf?days=30")
        assert response.content[:5] == b"%PDF-", \
            f"PDF should start with %PDF-, got {response.content[:10]}"
        print("PASS: Executive PDF has valid PDF header")

    def test_executive_pdf_has_content(self):
        """Executive PDF has reasonable content length (>500 bytes)"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/executive-pdf?days=30")
        assert len(response.content) > 500, \
            f"PDF should be >500 bytes, got {len(response.content)}"
        print(f"PASS: Executive PDF has {len(response.content)} bytes")

    def test_cves_pdf_returns_200(self):
        """GET /api/cve/reporting/export/cves-pdf returns 200"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/cves-pdf")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: CVEs PDF endpoint returns 200")

    def test_cves_pdf_content_type(self):
        """CVEs PDF has correct content-type: application/pdf"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/cves-pdf")
        assert "application/pdf" in response.headers.get("content-type", ""), \
            f"Expected application/pdf, got {response.headers.get('content-type')}"
        print("PASS: CVEs PDF content-type is application/pdf")

    def test_cves_pdf_valid_header(self):
        """CVEs PDF starts with %PDF- header (valid PDF)"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/cves-pdf")
        assert response.content[:5] == b"%PDF-", \
            f"PDF should start with %PDF-, got {response.content[:10]}"
        print("PASS: CVEs PDF has valid PDF header")

    def test_cves_pdf_with_severity_filter(self):
        """CVEs PDF accepts severity filter parameter"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/cves-pdf?severity=high")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/pdf" in response.headers.get("content-type", "")
        print("PASS: CVEs PDF with severity filter works")

    def test_cves_pdf_with_status_filter(self):
        """CVEs PDF accepts status filter parameter"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/cves-pdf?status=detected")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/pdf" in response.headers.get("content-type", "")
        print("PASS: CVEs PDF with status filter works")

    def test_team_pdf_returns_200(self):
        """GET /api/cve/reporting/export/team-pdf returns 200"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/team-pdf")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Team PDF endpoint returns 200")

    def test_team_pdf_content_type(self):
        """Team PDF has correct content-type: application/pdf"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/team-pdf")
        assert "application/pdf" in response.headers.get("content-type", ""), \
            f"Expected application/pdf, got {response.headers.get('content-type')}"
        print("PASS: Team PDF content-type is application/pdf")

    def test_team_pdf_valid_header(self):
        """Team PDF starts with %PDF- header (valid PDF)"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/team-pdf")
        assert response.content[:5] == b"%PDF-", \
            f"PDF should start with %PDF-, got {response.content[:10]}"
        print("PASS: Team PDF has valid PDF header")


class TestCSVExportsStillWork:
    """Ensure existing CSV exports still function"""

    def test_cves_csv_returns_200(self):
        """GET /api/cve/reporting/export/cves still returns CSV"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/cves")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/csv" in response.headers.get("content-type", ""), \
            f"Expected text/csv, got {response.headers.get('content-type')}"
        print("PASS: CVEs CSV export still works")

    def test_executive_csv_returns_200(self):
        """GET /api/cve/reporting/export/executive?days=30 still returns CSV"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/executive?days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/csv" in response.headers.get("content-type", ""), \
            f"Expected text/csv, got {response.headers.get('content-type')}"
        print("PASS: Executive CSV export still works")

    def test_team_csv_returns_200(self):
        """GET /api/cve/reporting/export/team still returns CSV"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/export/team")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/csv" in response.headers.get("content-type", ""), \
            f"Expected text/csv, got {response.headers.get('content-type')}"
        print("PASS: Team CSV export still works")


class TestDashboardTrendsEndpoint:
    """Tests for the new dashboard-trends endpoint"""

    def test_dashboard_trends_returns_200(self):
        """GET /api/cve/reporting/dashboard-trends returns 200"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/dashboard-trends")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Dashboard trends endpoint returns 200")

    def test_dashboard_trends_json_structure(self):
        """Dashboard trends returns expected JSON structure"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/dashboard-trends")
        data = response.json()
        
        # Check top-level keys
        assert "current_week" in data, "Missing current_week"
        assert "previous_week" in data, "Missing previous_week"
        assert "deltas" in data, "Missing deltas"
        assert "mini_trend" in data, "Missing mini_trend"
        print("PASS: Dashboard trends has all required top-level keys")

    def test_dashboard_trends_current_week_fields(self):
        """current_week has open, fixed, new fields"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/dashboard-trends")
        data = response.json()
        current = data.get("current_week", {})
        
        assert "open" in current, "current_week missing 'open'"
        assert "fixed" in current, "current_week missing 'fixed'"
        assert "new" in current, "current_week missing 'new'"
        assert isinstance(current["open"], int), "open should be int"
        assert isinstance(current["fixed"], int), "fixed should be int"
        assert isinstance(current["new"], int), "new should be int"
        print(f"PASS: current_week fields - open={current['open']}, fixed={current['fixed']}, new={current['new']}")

    def test_dashboard_trends_previous_week_fields(self):
        """previous_week has open, fixed, new fields"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/dashboard-trends")
        data = response.json()
        previous = data.get("previous_week", {})
        
        assert "open" in previous, "previous_week missing 'open'"
        assert "fixed" in previous, "previous_week missing 'fixed'"
        assert "new" in previous, "previous_week missing 'new'"
        print(f"PASS: previous_week fields - open={previous['open']}, fixed={previous['fixed']}, new={previous['new']}")

    def test_dashboard_trends_deltas_fields(self):
        """deltas has open_delta, fixed_delta, new_delta"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/dashboard-trends")
        data = response.json()
        deltas = data.get("deltas", {})
        
        assert "open_delta" in deltas, "deltas missing 'open_delta'"
        assert "fixed_delta" in deltas, "deltas missing 'fixed_delta'"
        assert "new_delta" in deltas, "deltas missing 'new_delta'"
        print(f"PASS: deltas fields - open_delta={deltas['open_delta']}, fixed_delta={deltas['fixed_delta']}, new_delta={deltas['new_delta']}")

    def test_dashboard_trends_mini_trend_array(self):
        """mini_trend is an array with 7 entries (one per day)"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/dashboard-trends")
        data = response.json()
        mini_trend = data.get("mini_trend", [])
        
        assert isinstance(mini_trend, list), "mini_trend should be a list"
        assert len(mini_trend) == 7, f"mini_trend should have 7 entries, got {len(mini_trend)}"
        print(f"PASS: mini_trend has 7 entries")

    def test_dashboard_trends_mini_trend_entry_structure(self):
        """Each mini_trend entry has day and count"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/dashboard-trends")
        data = response.json()
        mini_trend = data.get("mini_trend", [])
        
        for entry in mini_trend:
            assert "day" in entry, f"Entry missing 'day': {entry}"
            assert "count" in entry, f"Entry missing 'count': {entry}"
            assert isinstance(entry["count"], int), f"count should be int: {entry}"
        print(f"PASS: All mini_trend entries have day and count fields")


class TestSummaryAndDashboardEndpoints:
    """Verify existing summary and dashboard endpoints"""

    def test_reporting_summary_returns_200(self):
        """GET /api/cve/reporting/summary returns 200"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/summary?days=30")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Reporting summary endpoint returns 200")

    def test_reporting_summary_has_severity_distribution(self):
        """Summary includes severity_distribution"""
        response = requests.get(f"{BASE_URL}/api/cve/reporting/summary?days=30")
        data = response.json()
        
        assert "severity_distribution" in data, "Missing severity_distribution"
        sd = data["severity_distribution"]
        for sev in ["critical", "high", "medium", "low", "info"]:
            assert sev in sd, f"Missing severity: {sev}"
        print(f"PASS: Summary has severity_distribution: {sd}")

    def test_dashboard_returns_200(self):
        """GET /api/cve/dashboard returns 200"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Dashboard endpoint returns 200")

    def test_dashboard_has_severity_breakdown(self):
        """Dashboard includes severity_breakdown"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard")
        data = response.json()
        
        assert "severity_breakdown" in data, "Missing severity_breakdown"
        sb = data["severity_breakdown"]
        for sev in ["critical", "high", "medium", "low", "info"]:
            assert sev in sb, f"Missing severity: {sev}"
        print(f"PASS: Dashboard has severity_breakdown: {sb}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
