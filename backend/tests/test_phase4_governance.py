"""
Phase 4 Governance Dashboards & Advanced Analytics Tests
Tests for:
- GET /api/cve/governance/metrics
- GET /api/cve/governance/trends
- GET /api/cve/governance/sla
- GET /api/cve/governance/ownership
- GET /api/cve/governance/mttr
- GET /api/cve/governance/scan-activity
- GET /api/cve/remediation/aws/findings (enhanced)
- GET /api/cve/remediation/aws/security-hub (enhanced)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://threat-hub-1.preview.emergentagent.com")
GOVERNANCE_API = f"{BASE_URL}/api/cve/governance"
REMEDIATION_API = f"{BASE_URL}/api/cve/remediation"


class TestGovernanceMetrics:
    """Test /api/cve/governance/metrics endpoint"""

    def test_metrics_returns_200(self):
        """GET /metrics should return 200"""
        response = requests.get(f"{GOVERNANCE_API}/metrics")
        assert response.status_code == 200
        print(f"✓ GET /metrics returned {response.status_code}")

    def test_metrics_response_structure(self):
        """Metrics response should have required fields"""
        response = requests.get(f"{GOVERNANCE_API}/metrics")
        data = response.json()
        
        # Required top-level fields
        required_fields = [
            "total_cves", "open_cves", "fixed_cves", "verified_cves",
            "severity_distribution", "risk_score", "fix_rate_30d", "services_affected"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate severity_distribution structure
        severity_dist = data["severity_distribution"]
        for sev in ["critical", "high", "medium", "low", "info"]:
            assert sev in severity_dist, f"Missing severity: {sev}"
            assert isinstance(severity_dist[sev], int), f"{sev} should be int"
        
        # Validate services_affected is array
        assert isinstance(data["services_affected"], list), "services_affected should be list"
        
        # Validate risk_score is numeric and bounded
        assert isinstance(data["risk_score"], (int, float)), "risk_score should be numeric"
        assert 0 <= data["risk_score"] <= 100, "risk_score should be 0-100"
        
        print(f"✓ Metrics response has correct structure: total_cves={data['total_cves']}, risk_score={data['risk_score']}")

    def test_metrics_additional_fields(self):
        """Metrics should include additional tracking fields"""
        response = requests.get(f"{GOVERNANCE_API}/metrics")
        data = response.json()
        
        additional_fields = [
            "new_last_30_days", "new_last_7_days", "fixed_last_30_days",
            "remediation_total", "remediation_open", "remediation_merged"
        ]
        for field in additional_fields:
            assert field in data, f"Missing additional field: {field}"
        
        print(f"✓ Additional metrics present: new_30d={data.get('new_last_30_days')}, fixed_30d={data.get('fixed_last_30_days')}")


class TestGovernanceTrends:
    """Test /api/cve/governance/trends endpoint"""

    def test_trends_returns_200(self):
        """GET /trends should return 200"""
        response = requests.get(f"{GOVERNANCE_API}/trends?days=30")
        assert response.status_code == 200
        print(f"✓ GET /trends?days=30 returned {response.status_code}")

    def test_trends_response_structure(self):
        """Trends response should have trends array with daily data"""
        response = requests.get(f"{GOVERNANCE_API}/trends?days=30")
        data = response.json()
        
        assert "trends" in data, "Missing 'trends' field"
        assert "period_days" in data, "Missing 'period_days' field"
        assert isinstance(data["trends"], list), "trends should be array"
        
        # Should have ~31 days of data (days + today)
        assert len(data["trends"]) >= 20, f"Expected at least 20 trend entries, got {len(data['trends'])}"
        
        # Validate individual trend item structure
        if data["trends"]:
            item = data["trends"][0]
            assert "date" in item, "Trend item missing 'date'"
            assert "label" in item, "Trend item missing 'label'"
            assert "detected" in item, "Trend item missing 'detected'"
            assert "fixed" in item, "Trend item missing 'fixed'"
        
        print(f"✓ Trends returned {len(data['trends'])} entries for {data['period_days']} days")

    def test_trends_days_parameter(self):
        """Trends should respect days parameter (7-90 range)"""
        response = requests.get(f"{GOVERNANCE_API}/trends?days=7")
        data = response.json()
        assert len(data["trends"]) >= 7, "Should return at least 7 days of trends"
        print(f"✓ GET /trends?days=7 returned {len(data['trends'])} entries")


class TestGovernanceSLA:
    """Test /api/cve/governance/sla endpoint"""

    def test_sla_returns_200(self):
        """GET /sla should return 200"""
        response = requests.get(f"{GOVERNANCE_API}/sla")
        assert response.status_code == 200
        print(f"✓ GET /sla returned {response.status_code}")

    def test_sla_response_structure(self):
        """SLA response should have sla_data array and overall_compliance"""
        response = requests.get(f"{GOVERNANCE_API}/sla")
        data = response.json()
        
        assert "sla_data" in data, "Missing 'sla_data' field"
        assert "overall_compliance" in data, "Missing 'overall_compliance' field"
        assert isinstance(data["sla_data"], list), "sla_data should be array"
        assert len(data["sla_data"]) == 4, "Should have 4 severity levels in SLA data"
        
        # Validate overall compliance is percentage
        assert isinstance(data["overall_compliance"], (int, float)), "overall_compliance should be numeric"
        
        print(f"✓ SLA response: overall_compliance={data['overall_compliance']}%")

    def test_sla_severity_structure(self):
        """Each SLA severity entry should have required fields"""
        response = requests.get(f"{GOVERNANCE_API}/sla")
        data = response.json()
        
        required_fields = ["severity", "sla_hours", "open", "overdue", "within_sla", "fixed_total", "compliance_pct"]
        
        for sla_entry in data["sla_data"]:
            for field in required_fields:
                assert field in sla_entry, f"SLA entry missing '{field}'"
            
            # Validate severity is one of expected values
            assert sla_entry["severity"] in ["critical", "high", "medium", "low"]
            
            # Validate compliance_pct is bounded
            assert 0 <= sla_entry["compliance_pct"] <= 100, f"compliance_pct out of range: {sla_entry['compliance_pct']}"
        
        print(f"✓ All 4 severity SLA entries have correct structure")


class TestGovernanceOwnership:
    """Test /api/cve/governance/ownership endpoint"""

    def test_ownership_returns_200(self):
        """GET /ownership should return 200"""
        response = requests.get(f"{GOVERNANCE_API}/ownership")
        assert response.status_code == 200
        print(f"✓ GET /ownership returned {response.status_code}")

    def test_ownership_response_structure(self):
        """Ownership response should have by_team, by_person, by_source, by_status arrays"""
        response = requests.get(f"{GOVERNANCE_API}/ownership")
        data = response.json()
        
        required_arrays = ["by_team", "by_person", "by_source", "by_status"]
        for arr in required_arrays:
            assert arr in data, f"Missing '{arr}' field"
            assert isinstance(data[arr], list), f"'{arr}' should be array"
        
        print(f"✓ Ownership arrays: teams={len(data['by_team'])}, persons={len(data['by_person'])}, sources={len(data['by_source'])}, statuses={len(data['by_status'])}")

    def test_ownership_data_structure(self):
        """Ownership data items should have correct structure"""
        response = requests.get(f"{GOVERNANCE_API}/ownership")
        data = response.json()
        
        # Validate by_team structure
        for item in data.get("by_team", []):
            assert "team" in item, "by_team item missing 'team'"
            assert "count" in item, "by_team item missing 'count'"
        
        # Validate by_person structure
        for item in data.get("by_person", []):
            assert "person" in item, "by_person item missing 'person'"
            assert "count" in item, "by_person item missing 'count'"
        
        # Validate by_source structure
        for item in data.get("by_source", []):
            assert "source" in item, "by_source item missing 'source'"
            assert "count" in item, "by_source item missing 'count'"
        
        # Validate by_status structure
        for item in data.get("by_status", []):
            assert "status" in item, "by_status item missing 'status'"
            assert "count" in item, "by_status item missing 'count'"
        
        print("✓ Ownership data structures validated")


class TestGovernanceMTTR:
    """Test /api/cve/governance/mttr endpoint"""

    def test_mttr_returns_200(self):
        """GET /mttr should return 200"""
        response = requests.get(f"{GOVERNANCE_API}/mttr")
        assert response.status_code == 200
        print(f"✓ GET /mttr returned {response.status_code}")

    def test_mttr_response_structure(self):
        """MTTR response should have mttr object with severity breakdown"""
        response = requests.get(f"{GOVERNANCE_API}/mttr")
        data = response.json()
        
        assert "mttr" in data, "Missing 'mttr' field"
        mttr = data["mttr"]
        
        for sev in ["critical", "high", "medium", "low"]:
            assert sev in mttr, f"Missing severity '{sev}' in MTTR"
            sev_data = mttr[sev]
            
            # Required fields per severity
            for field in ["avg_hours", "avg_days", "sample_size"]:
                assert field in sev_data, f"MTTR {sev} missing '{field}'"
        
        print(f"✓ MTTR response has correct structure for all severities")

    def test_mttr_additional_fields(self):
        """MTTR should include min/max hours per severity"""
        response = requests.get(f"{GOVERNANCE_API}/mttr")
        data = response.json()
        mttr = data["mttr"]
        
        for sev in ["critical", "high", "medium", "low"]:
            sev_data = mttr[sev]
            assert "min_hours" in sev_data, f"MTTR {sev} missing 'min_hours'"
            assert "max_hours" in sev_data, f"MTTR {sev} missing 'max_hours'"
        
        print("✓ MTTR includes min_hours and max_hours per severity")


class TestGovernanceScanActivity:
    """Test /api/cve/governance/scan-activity endpoint"""

    def test_scan_activity_returns_200(self):
        """GET /scan-activity should return 200"""
        response = requests.get(f"{GOVERNANCE_API}/scan-activity")
        assert response.status_code == 200
        print(f"✓ GET /scan-activity returned {response.status_code}")

    def test_scan_activity_response_structure(self):
        """Scan activity should have total_scans, recent_scans, by_scanner"""
        response = requests.get(f"{GOVERNANCE_API}/scan-activity")
        data = response.json()
        
        assert "total_scans" in data, "Missing 'total_scans'"
        assert "recent_scans" in data, "Missing 'recent_scans'"
        assert "by_scanner" in data, "Missing 'by_scanner'"
        
        assert isinstance(data["total_scans"], int), "total_scans should be int"
        assert isinstance(data["recent_scans"], list), "recent_scans should be array"
        assert isinstance(data["by_scanner"], dict), "by_scanner should be object"
        
        print(f"✓ Scan activity: total={data['total_scans']}, recent={len(data['recent_scans'])}")

    def test_scan_activity_recent_scans_structure(self):
        """Recent scans should have id, scanner, scan_type"""
        response = requests.get(f"{GOVERNANCE_API}/scan-activity")
        data = response.json()
        
        for scan in data.get("recent_scans", []):
            assert "id" in scan, "Recent scan missing 'id'"
            assert "scanner" in scan, "Recent scan missing 'scanner'"
            assert "scan_type" in scan, "Recent scan missing 'scan_type'"
        
        print("✓ Recent scans have correct structure")


class TestAWSIntegration:
    """Test AWS Inspector and Security Hub endpoints"""

    def test_aws_findings_returns_200(self):
        """GET /aws/findings should return 200"""
        response = requests.get(f"{REMEDIATION_API}/aws/findings")
        assert response.status_code == 200
        print(f"✓ GET /aws/findings returned {response.status_code}")

    def test_aws_findings_response_structure(self):
        """AWS findings should have findings array, count, source"""
        response = requests.get(f"{REMEDIATION_API}/aws/findings")
        data = response.json()
        
        assert "findings" in data, "Missing 'findings'"
        assert "count" in data, "Missing 'count'"
        assert "source" in data, "Missing 'source'"
        assert isinstance(data["findings"], list), "findings should be array"
        
        # Source should indicate connection status
        print(f"✓ AWS Inspector: source={data['source']}, count={data['count']}")

    def test_aws_inspector_connection(self):
        """AWS Inspector should be connected (source=aws_inspector)"""
        response = requests.get(f"{REMEDIATION_API}/aws/findings")
        data = response.json()
        
        # With real AWS credentials, source should be aws_inspector
        assert data["source"] in ["aws_inspector", "cached"], f"Unexpected source: {data['source']}"
        print(f"✓ AWS Inspector connection status: {data['source']}")

    def test_security_hub_returns_200(self):
        """GET /aws/security-hub should return 200"""
        response = requests.get(f"{REMEDIATION_API}/aws/security-hub")
        assert response.status_code == 200
        print(f"✓ GET /aws/security-hub returned {response.status_code}")

    def test_security_hub_response_structure(self):
        """Security Hub should have findings array, count, source"""
        response = requests.get(f"{REMEDIATION_API}/aws/security-hub")
        data = response.json()
        
        assert "findings" in data, "Missing 'findings'"
        assert "count" in data, "Missing 'count'"
        assert "source" in data, "Missing 'source'"
        assert isinstance(data["findings"], list), "findings should be array"
        
        print(f"✓ Security Hub: source={data['source']}, count={data['count']}")

    def test_security_hub_finding_structure(self):
        """Security Hub findings should have proper structure"""
        response = requests.get(f"{REMEDIATION_API}/aws/security-hub")
        data = response.json()
        
        if data["findings"]:
            finding = data["findings"][0]
            # Should have at least id, title, severity
            assert "id" in finding, "Finding missing 'id'"
            assert "title" in finding, "Finding missing 'title'"
            assert "severity" in finding, "Finding missing 'severity'"
            print(f"✓ Security Hub finding structure verified: {finding['title'][:50]}...")


class TestGovernanceEndToEnd:
    """End-to-end governance workflow tests"""

    def test_full_governance_data_load(self):
        """Test loading all governance data like frontend does"""
        # Simulate GovernanceTab fetchAll
        metrics_resp = requests.get(f"{GOVERNANCE_API}/metrics")
        trends_resp = requests.get(f"{GOVERNANCE_API}/trends?days=30")
        sla_resp = requests.get(f"{GOVERNANCE_API}/sla")
        ownership_resp = requests.get(f"{GOVERNANCE_API}/ownership")
        mttr_resp = requests.get(f"{GOVERNANCE_API}/mttr")
        
        assert metrics_resp.status_code == 200
        assert trends_resp.status_code == 200
        assert sla_resp.status_code == 200
        assert ownership_resp.status_code == 200
        assert mttr_resp.status_code == 200
        
        metrics = metrics_resp.json()
        trends = trends_resp.json()
        sla = sla_resp.json()
        ownership = ownership_resp.json()
        mttr = mttr_resp.json()
        
        print(f"✓ Full governance data load successful:")
        print(f"  - Metrics: total_cves={metrics['total_cves']}, risk_score={metrics['risk_score']}")
        print(f"  - Trends: {len(trends['trends'])} days")
        print(f"  - SLA: overall={sla['overall_compliance']}%")
        print(f"  - Ownership: {len(ownership['by_source'])} sources")
        print(f"  - MTTR: {len(mttr['mttr'])} severities")

    def test_governance_data_consistency(self):
        """Verify data consistency across governance endpoints"""
        metrics = requests.get(f"{GOVERNANCE_API}/metrics").json()
        ownership = requests.get(f"{GOVERNANCE_API}/ownership").json()
        
        # Total CVEs from ownership by_status should match or be close to metrics
        status_total = sum(item["count"] for item in ownership.get("by_status", []))
        assert status_total == metrics["total_cves"], \
            f"Status total ({status_total}) should match total_cves ({metrics['total_cves']})"
        
        print(f"✓ Data consistency verified: {status_total} CVEs across all statuses")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
