"""
Phase 2: Multi-Scanner Integration, CI/CD Pipeline Generator, Policy-as-Code Engine Tests
Tests for: Trivy, Grype, Syft, Checkov scanners + Pipeline Generator + Policy Rules Engine
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')
SCANNER_API = f"{BASE_URL}/api/cve/scanners"

# Long timeout for real scanner operations (tools run actual scans)
SCAN_TIMEOUT = 180


class TestToolStatus:
    """Test security tool installation status - should be fast"""
    
    def test_get_tool_status(self):
        """GET /api/cve/scanners/tools - Returns all 4 installed tools"""
        response = requests.get(f"{SCANNER_API}/tools", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # All 4 tools should be present
        assert "trivy" in data, "trivy not in response"
        assert "grype" in data, "grype not in response"
        assert "syft" in data, "syft not in response"
        assert "checkov" in data, "checkov not in response"
        
        # All tools should be installed
        assert data["trivy"]["installed"] == True, "Trivy not installed"
        assert data["grype"]["installed"] == True, "Grype not installed"
        assert data["syft"]["installed"] == True, "Syft not installed"
        assert data["checkov"]["installed"] == True, "Checkov not installed"
        
        # Verify version strings present
        assert data["trivy"]["version"] is not None, "Trivy version missing"
        assert data["grype"]["version"] is not None, "Grype version missing"
        assert data["syft"]["version"] is not None, "Syft version missing"
        assert data["checkov"]["version"] is not None, "Checkov version missing"
        
        print(f"All 4 tools installed: trivy={data['trivy']['version']}, grype={data['grype']['version']}, syft={data['syft']['version']}, checkov={data['checkov']['version']}")


class TestTrivyScanner:
    """Test Trivy filesystem and IaC scanning - REAL SCANS"""
    
    def test_trivy_filesystem_scan(self):
        """POST /api/cve/scanners/trivy/fs - Trivy filesystem scan returns vulnerabilities"""
        response = requests.post(
            f"{SCANNER_API}/trivy/fs?target=/app/backend&severity=CRITICAL,HIGH,MEDIUM,LOW",
            timeout=SCAN_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify scan result structure
        assert "id" in data, "Missing scan id"
        assert data["scanner"] == "trivy", f"Expected scanner=trivy, got {data['scanner']}"
        assert data["scan_type"] == "filesystem", f"Expected scan_type=filesystem, got {data['scan_type']}"
        assert data["status"] == "completed", f"Scan status: {data['status']}"
        assert "vulnerabilities" in data, "Missing vulnerabilities array"
        assert "summary" in data, "Missing summary"
        
        # Verify summary structure
        summary = data["summary"]
        assert "total" in summary, "Missing total in summary"
        assert "critical" in summary, "Missing critical count"
        assert "high" in summary, "Missing high count"
        
        print(f"Trivy FS scan completed: {summary['total']} vulns (C:{summary['critical']}, H:{summary['high']}, M:{summary.get('medium', 0)}, L:{summary.get('low', 0)})")
        
        return data["id"]  # Return scan_id for later tests
    
    def test_trivy_iac_scan(self):
        """POST /api/cve/scanners/trivy/iac - Trivy IaC scan returns misconfigurations"""
        response = requests.post(
            f"{SCANNER_API}/trivy/iac?target=/tmp/test_iac",
            timeout=SCAN_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify scan result structure
        assert "id" in data, "Missing scan id"
        assert data["scanner"] == "trivy", f"Expected scanner=trivy, got {data['scanner']}"
        assert data["scan_type"] == "iac", f"Expected scan_type=iac, got {data['scan_type']}"
        assert data["status"] == "completed", f"Scan status: {data['status']}"
        assert "misconfigurations" in data, "Missing misconfigurations array"
        assert "summary" in data, "Missing summary"
        
        # Verify we found misconfigs (expected ~19 from demo Terraform)
        misconfig_count = len(data["misconfigurations"])
        assert misconfig_count > 0, "Expected misconfigurations in demo Terraform"
        
        print(f"Trivy IaC scan completed: {misconfig_count} misconfigurations found")
        
        # Verify misconfig structure
        if data["misconfigurations"]:
            misconfig = data["misconfigurations"][0]
            assert "id" in misconfig, "Missing misconfig id"
            assert "severity" in misconfig, "Missing misconfig severity"
            assert "title" in misconfig, "Missing misconfig title"


class TestGrypeScanner:
    """Test Grype dependency vulnerability scanning - REAL SCANS"""
    
    def test_grype_scan(self):
        """POST /api/cve/scanners/grype - Grype scan returns real vulnerabilities"""
        response = requests.post(
            f"{SCANNER_API}/grype?target=dir%3A/app/backend",
            timeout=SCAN_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify scan result structure
        assert "id" in data, "Missing scan id"
        assert data["scanner"] == "grype", f"Expected scanner=grype, got {data['scanner']}"
        assert data["scan_type"] == "dependency", f"Expected scan_type=dependency, got {data['scan_type']}"
        assert data["status"] == "completed", f"Scan status: {data['status']}"
        assert "vulnerabilities" in data, "Missing vulnerabilities array"
        assert "summary" in data, "Missing summary"
        
        # Verify summary structure
        summary = data["summary"]
        vuln_count = summary.get("total", 0)
        
        print(f"Grype scan completed: {vuln_count} vulns (C:{summary.get('critical', 0)}, H:{summary.get('high', 0)}, M:{summary.get('medium', 0)}, L:{summary.get('low', 0)})")
        
        # Verify vulnerability structure if any found
        if data["vulnerabilities"]:
            vuln = data["vulnerabilities"][0]
            assert "id" in vuln, "Missing vuln id"
            assert "package" in vuln, "Missing package name"
            assert "severity" in vuln, "Missing severity"
        
        return data["id"]


class TestSyftScanner:
    """Test Syft SBOM generation - REAL SCAN"""
    
    def test_syft_sbom_generation(self):
        """POST /api/cve/scanners/syft - Syft SBOM returns packages"""
        response = requests.post(
            f"{SCANNER_API}/syft?target=/app/backend",
            timeout=SCAN_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify scan result structure
        assert "id" in data, "Missing scan id"
        assert data["scanner"] == "syft", f"Expected scanner=syft, got {data['scanner']}"
        assert data["scan_type"] == "sbom", f"Expected scan_type=sbom, got {data['scan_type']}"
        assert data["status"] == "completed", f"Scan status: {data['status']}"
        assert "packages" in data, "Missing packages array"
        assert "summary" in data, "Missing summary"
        
        # Verify summary structure
        summary = data["summary"]
        pkg_count = summary.get("total_packages", 0)
        
        # Expect many packages from /app/backend (Python dependencies)
        assert pkg_count > 50, f"Expected >50 packages, got {pkg_count}"
        
        print(f"Syft SBOM completed: {pkg_count} packages by type: {summary.get('by_type', {})}")
        
        # Verify package structure if any found
        if data["packages"]:
            pkg = data["packages"][0]
            assert "name" in pkg, "Missing package name"
            assert "version" in pkg, "Missing package version"
            assert "type" in pkg, "Missing package type"


class TestCheckovScanner:
    """Test Checkov IaC security scanning - REAL SCAN"""
    
    def test_checkov_iac_scan(self):
        """POST /api/cve/scanners/checkov - Checkov scan returns passed/failed checks"""
        response = requests.post(
            f"{SCANNER_API}/checkov?target=/tmp/test_iac",
            timeout=SCAN_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify scan result structure
        assert "id" in data, "Missing scan id"
        assert data["scanner"] == "checkov", f"Expected scanner=checkov, got {data['scanner']}"
        assert data["scan_type"] == "iac", f"Expected scan_type=iac, got {data['scan_type']}"
        assert data["status"] == "completed", f"Scan status: {data['status']}"
        assert "checks" in data, "Missing checks array"
        assert "summary" in data, "Missing summary"
        
        # Verify summary has passed/failed
        summary = data["summary"]
        assert "passed" in summary, "Missing passed count"
        assert "failed" in summary, "Missing failed count"
        total = summary.get("total", summary.get("passed", 0) + summary.get("failed", 0))
        
        print(f"Checkov scan completed: {total} checks (passed:{summary['passed']}, failed:{summary['failed']})")
        
        # Verify checks structure if any
        if data["checks"]:
            check = data["checks"][0]
            assert "check_id" in check, "Missing check_id"
            assert "status" in check, "Missing status"


class TestScanHistory:
    """Test scan history retrieval"""
    
    def test_list_scan_results(self):
        """GET /api/cve/scanners/results - Lists scan history"""
        response = requests.get(f"{SCANNER_API}/results?limit=20", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        
        # Verify scan result structure (without full details)
        if data:
            result = data[0]
            assert "id" in result, "Missing id"
            assert "scanner" in result, "Missing scanner"
            assert "scan_type" in result, "Missing scan_type"
            assert "status" in result, "Missing status"
            assert "started_at" in result, "Missing started_at"
            
            # Should NOT include full details in list (vulnerabilities, packages, etc.)
            # These are excluded for performance
        
        print(f"Scan history: {len(data)} results")
    
    def test_get_scan_result_by_id(self):
        """GET /api/cve/scanners/results/{scan_id} - Gets full scan result with details"""
        # First get list to find a scan_id
        list_response = requests.get(f"{SCANNER_API}/results?limit=1", timeout=30)
        assert list_response.status_code == 200
        
        results = list_response.json()
        if not results:
            pytest.skip("No scan results to test")
        
        scan_id = results[0]["id"]
        
        # Get full result by ID
        response = requests.get(f"{SCANNER_API}/results/{scan_id}", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify full result structure
        assert "id" in data, "Missing id"
        assert data["id"] == scan_id, f"ID mismatch: expected {scan_id}, got {data['id']}"
        assert "scanner" in data, "Missing scanner"
        
        # Full result should include details based on scanner type
        scanner = data["scanner"]
        if scanner in ["trivy", "grype"] and data.get("scan_type") != "iac":
            # Expect vulnerabilities for vuln scans
            pass  # vulnerabilities may or may not be present
        
        print(f"Retrieved full scan result: {scan_id} ({data['scanner']})")
    
    def test_get_nonexistent_scan_result(self):
        """GET /api/cve/scanners/results/{invalid_id} - Returns 404"""
        response = requests.get(f"{SCANNER_API}/results/nonexistent-id-12345", timeout=15)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestPolicyRules:
    """Test Policy-as-Code rules engine"""
    
    def test_list_policy_rules(self):
        """GET /api/cve/scanners/policy-rules - Lists all policy rules"""
        response = requests.get(f"{SCANNER_API}/policy-rules", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        
        print(f"Policy rules: {len(data)} rules found")
        
        # Verify rule structure if any rules exist
        if data:
            rule = data[0]
            assert "id" in rule, "Missing id"
            assert "name" in rule, "Missing name"
            assert "enabled" in rule, "Missing enabled flag"
            assert "condition_type" in rule, "Missing condition_type"
            assert "action" in rule, "Missing action"
    
    def test_seed_default_rules(self):
        """POST /api/cve/scanners/policy-rules/seed - Seeds 5 default policy rules"""
        response = requests.post(f"{SCANNER_API}/policy-rules/seed", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Either seeded new rules or rules already exist
        assert "message" in data, "Missing message"
        print(f"Seed rules result: {data['message']}")
    
    def test_create_custom_policy_rule(self):
        """POST /api/cve/scanners/policy-rules - Creates custom policy rule"""
        rule_data = {
            "name": "TEST_Custom Block High CVE Count",
            "description": "Block if more than 10 high severity vulns",
            "enabled": True,
            "condition_type": "severity_threshold",
            "condition": {"min_severity": "high", "max_count": 10},
            "action": "block_deploy",
            "scope": "all"
        }
        
        response = requests.post(
            f"{SCANNER_API}/policy-rules",
            json=rule_data,
            timeout=15
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify created rule
        assert "id" in data, "Missing id in response"
        assert data["name"] == rule_data["name"], f"Name mismatch"
        assert data["enabled"] == True, "Should be enabled"
        assert data["condition_type"] == "severity_threshold"
        
        print(f"Created custom rule: {data['id']}")
        
        return data["id"]
    
    def test_update_policy_rule_toggle(self):
        """PUT /api/cve/scanners/policy-rules/{id} - Toggles enabled/disabled"""
        # First create a rule to toggle
        rule_data = {
            "name": "TEST_Toggle Rule",
            "description": "Rule for toggle testing",
            "enabled": True,
            "condition_type": "severity_threshold",
            "condition": {"min_severity": "critical", "max_count": 0},
            "action": "warn"
        }
        
        create_response = requests.post(f"{SCANNER_API}/policy-rules", json=rule_data, timeout=15)
        assert create_response.status_code == 200
        rule_id = create_response.json()["id"]
        
        # Toggle to disabled
        toggle_response = requests.put(
            f"{SCANNER_API}/policy-rules/{rule_id}",
            json={"enabled": False},
            timeout=15
        )
        assert toggle_response.status_code == 200, f"Expected 200, got {toggle_response.status_code}"
        
        updated = toggle_response.json()
        assert updated["enabled"] == False, "Should be disabled after toggle"
        
        print(f"Toggled rule {rule_id} to disabled")
        
        # Cleanup - delete the rule
        requests.delete(f"{SCANNER_API}/policy-rules/{rule_id}", timeout=15)
    
    def test_delete_policy_rule(self):
        """DELETE /api/cve/scanners/policy-rules/{id} - Deletes a rule"""
        # First create a rule to delete
        rule_data = {
            "name": "TEST_Delete Rule",
            "description": "Rule for delete testing",
            "enabled": True,
            "condition_type": "severity_threshold",
            "condition": {"min_severity": "low", "max_count": 100},
            "action": "notify"
        }
        
        create_response = requests.post(f"{SCANNER_API}/policy-rules", json=rule_data, timeout=15)
        assert create_response.status_code == 200
        rule_id = create_response.json()["id"]
        
        # Delete the rule
        delete_response = requests.delete(f"{SCANNER_API}/policy-rules/{rule_id}", timeout=15)
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        delete_data = delete_response.json()
        assert delete_data["deleted"] == True, "Should indicate deleted"
        
        # Verify deleted - should 404
        verify_response = requests.get(f"{SCANNER_API}/policy-rules", timeout=15)
        rules = verify_response.json()
        assert not any(r["id"] == rule_id for r in rules), "Rule should be deleted"
        
        print(f"Deleted rule {rule_id}")
    
    def test_delete_nonexistent_rule(self):
        """DELETE /api/cve/scanners/policy-rules/{invalid_id} - Returns 404"""
        response = requests.delete(f"{SCANNER_API}/policy-rules/nonexistent-rule-12345", timeout=15)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestPolicyEvaluation:
    """Test policy evaluation against scan results"""
    
    def test_evaluate_policies_against_scan(self):
        """POST /api/cve/scanners/policy-rules/evaluate/{scan_id} - Evaluates policies against scan result"""
        # Get a scan result to evaluate
        list_response = requests.get(f"{SCANNER_API}/results?limit=10", timeout=30)
        assert list_response.status_code == 200
        
        results = list_response.json()
        
        # Find a grype or trivy vuln scan (not IaC)
        scan_id = None
        for r in results:
            if r["scanner"] in ["grype", "trivy"] and r.get("scan_type") != "iac":
                scan_id = r["id"]
                break
        
        if not scan_id and results:
            scan_id = results[0]["id"]
        
        if not scan_id:
            pytest.skip("No scan results available for policy evaluation")
        
        # Evaluate policies
        response = requests.post(f"{SCANNER_API}/policy-rules/evaluate/{scan_id}", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify evaluation structure
        assert "deploy_allowed" in data, "Missing deploy_allowed flag"
        assert "rules_evaluated" in data, "Missing rules_evaluated count"
        assert "rules_triggered" in data, "Missing rules_triggered list"
        assert "rules_passed" in data, "Missing rules_passed list"
        
        print(f"Policy evaluation for {scan_id}: deploy_allowed={data['deploy_allowed']}, rules_evaluated={data['rules_evaluated']}, triggered={len(data['rules_triggered'])}, passed={len(data['rules_passed'])}")
        
        # If rules triggered, verify structure
        if data["rules_triggered"]:
            triggered = data["rules_triggered"][0]
            assert "rule_id" in triggered, "Missing rule_id"
            assert "rule_name" in triggered, "Missing rule_name"
            assert "action" in triggered, "Missing action"
    
    def test_evaluate_nonexistent_scan(self):
        """POST /api/cve/scanners/policy-rules/evaluate/{invalid_id} - Returns 404"""
        response = requests.post(f"{SCANNER_API}/policy-rules/evaluate/nonexistent-scan-12345", timeout=15)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestPipelineGenerator:
    """Test CI/CD Pipeline Generator"""
    
    def test_generate_github_actions_pipeline(self):
        """POST /api/cve/scanners/pipeline/generate - Generates GitHub Actions YAML"""
        config = {
            "repo_name": "TEST_bigmannentertainment",
            "branch": "main",
            "enable_trivy": True,
            "enable_grype": True,
            "enable_checkov": True,
            "enable_syft": True,
            "fail_on_critical": True,
            "fail_on_high": False,
            "container_image": "",
            "terraform_dir": "terraform/",
            "notify_email": ""
        }
        
        response = requests.post(
            f"{SCANNER_API}/pipeline/generate",
            json=config,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify pipeline structure
        assert "id" in data, "Missing pipeline id"
        assert "yaml_content" in data, "Missing yaml_content"
        assert "repo_name" in data, "Missing repo_name"
        assert "branch" in data, "Missing branch"
        assert "created_at" in data, "Missing created_at"
        
        # Verify YAML content includes expected jobs
        yaml_content = data["yaml_content"]
        assert "name:" in yaml_content, "Missing name in YAML"
        assert "jobs:" in yaml_content, "Missing jobs in YAML"
        assert "trivy" in yaml_content.lower(), "Missing trivy job in YAML"
        assert "grype" in yaml_content.lower(), "Missing grype job in YAML"
        
        print(f"Generated pipeline {data['id']} for {data['repo_name']}/{data['branch']}")
        print(f"YAML content length: {len(yaml_content)} chars")
        
        return data["id"]
    
    def test_list_generated_pipelines(self):
        """GET /api/cve/scanners/pipeline/list - Lists generated pipelines"""
        response = requests.get(f"{SCANNER_API}/pipeline/list", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        
        print(f"Generated pipelines: {len(data)} found")
        
        # Verify pipeline summary structure (yaml_content excluded in list)
        if data:
            pipeline = data[0]
            assert "id" in pipeline, "Missing id"
            assert "repo_name" in pipeline, "Missing repo_name"
            assert "branch" in pipeline, "Missing branch"
            # yaml_content should NOT be in list view for performance
    
    def test_get_pipeline_by_id(self):
        """GET /api/cve/scanners/pipeline/{id} - Gets pipeline with yaml_content"""
        # First generate a pipeline
        config = {
            "repo_name": "TEST_pipeline_get",
            "branch": "develop",
            "enable_trivy": True,
            "enable_grype": False,
            "enable_checkov": True,
            "enable_syft": False,
            "fail_on_critical": True
        }
        
        create_response = requests.post(f"{SCANNER_API}/pipeline/generate", json=config, timeout=30)
        assert create_response.status_code == 200
        pipeline_id = create_response.json()["id"]
        
        # Get by ID
        response = requests.get(f"{SCANNER_API}/pipeline/{pipeline_id}", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Full result should include yaml_content
        assert "id" in data, "Missing id"
        assert data["id"] == pipeline_id, f"ID mismatch"
        assert "yaml_content" in data, "Missing yaml_content in full result"
        assert "config" in data, "Missing config"
        
        print(f"Retrieved pipeline {pipeline_id} with {len(data['yaml_content'])} char YAML")
    
    def test_get_nonexistent_pipeline(self):
        """GET /api/cve/scanners/pipeline/{invalid_id} - Returns 404"""
        response = requests.get(f"{SCANNER_API}/pipeline/nonexistent-pipeline-12345", timeout=15)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestCleanup:
    """Cleanup test data created during tests"""
    
    def test_cleanup_test_rules(self):
        """Delete TEST_ prefixed policy rules"""
        response = requests.get(f"{SCANNER_API}/policy-rules", timeout=15)
        if response.status_code == 200:
            rules = response.json()
            for rule in rules:
                if rule.get("name", "").startswith("TEST_"):
                    requests.delete(f"{SCANNER_API}/policy-rules/{rule['id']}", timeout=15)
                    print(f"Cleaned up test rule: {rule['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
