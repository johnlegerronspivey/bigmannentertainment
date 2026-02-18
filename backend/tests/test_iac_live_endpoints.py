"""
IaC Live Endpoints Tests
Tests for Infrastructure as Code LIVE AWS/GitHub API endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestLiveStatus:
    """Test GET /api/cve/iac/live-status endpoint - AWS Lambda, S3, GitHub connectivity"""

    def test_live_status_returns_200(self):
        """Live status endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_live_status_has_aws_lambda_connection(self):
        """Live status includes AWS Lambda connection status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert "aws_lambda" in data, "Missing 'aws_lambda' field"
        assert "connected" in data["aws_lambda"], "Missing 'connected' in aws_lambda"
        assert data["aws_lambda"]["connected"] == True, "AWS Lambda should be connected"
        assert "region" in data["aws_lambda"], "Missing 'region' in aws_lambda"

    def test_live_status_has_aws_s3_connection(self):
        """Live status includes AWS S3 connection status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert "aws_s3" in data, "Missing 'aws_s3' field"
        assert "connected" in data["aws_s3"], "Missing 'connected' in aws_s3"
        assert data["aws_s3"]["connected"] == True, "AWS S3 should be connected"
        assert "bucket" in data["aws_s3"], "Missing 'bucket' in aws_s3"

    def test_live_status_has_github_connection(self):
        """Live status includes GitHub connection status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert "github" in data, "Missing 'github' field"
        assert "connected" in data["github"], "Missing 'connected' in github"
        assert data["github"]["connected"] == True, "GitHub should be connected"
        assert "user" in data["github"], "Missing 'user' in github"
        assert data["github"]["user"] is not None, "GitHub user should not be None"

    def test_live_status_has_checked_at_timestamp(self):
        """Live status includes timestamp"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert "checked_at" in data, "Missing 'checked_at' field"
        assert data["checked_at"] is not None, "checked_at should not be None"


class TestLambdaLive:
    """Test GET /api/cve/iac/lambda/live endpoint - Real AWS Lambda functions"""

    def test_lambda_live_returns_200(self):
        """Lambda live endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_lambda_live_connected(self):
        """Lambda live shows connected status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, "Lambda live should be connected"

    def test_lambda_live_has_functions(self):
        """Lambda live returns list of functions"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        assert "functions" in data, "Missing 'functions' field"
        assert isinstance(data["functions"], list), "functions should be a list"
        assert len(data["functions"]) > 0, "Should have at least one Lambda function"

    def test_lambda_live_has_total_count(self):
        """Lambda live returns total count"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        assert "total" in data, "Missing 'total' field"
        assert data["total"] > 0, "Total should be > 0"
        assert data["total"] == len(data["functions"]), "Total should match functions count"

    def test_lambda_live_function_details(self):
        """Lambda live functions have required details"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        assert len(data["functions"]) > 0, "Need at least one function to test"
        fn = data["functions"][0]
        assert "name" in fn, "Function missing 'name'"
        assert "runtime" in fn, "Function missing 'runtime'"
        assert "memory_mb" in fn, "Function missing 'memory_mb'"
        assert "timeout" in fn, "Function missing 'timeout'"
        assert "handler" in fn, "Function missing 'handler'"
        assert "code_size_bytes" in fn, "Function missing 'code_size_bytes'"

    def test_lambda_live_function_metrics(self):
        """Lambda live functions have CloudWatch metrics"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        assert len(data["functions"]) > 0, "Need at least one function to test"
        fn = data["functions"][0]
        assert "metrics" in fn, "Function missing 'metrics'"
        assert isinstance(fn["metrics"], dict), "metrics should be a dict"


class TestGitHubRuns:
    """Test GET /api/cve/iac/github/runs endpoint - Real GitHub Actions runs"""

    def test_github_runs_returns_200(self):
        """GitHub runs endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_github_runs_connected(self):
        """GitHub runs shows connected status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, "GitHub runs should be connected"

    def test_github_runs_has_runs_list(self):
        """GitHub runs returns list of workflow runs"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        data = response.json()
        assert "runs" in data, "Missing 'runs' field"
        assert isinstance(data["runs"], list), "runs should be a list"

    def test_github_runs_has_repo(self):
        """GitHub runs returns repo info"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        data = response.json()
        assert "repo" in data, "Missing 'repo' field"
        assert data["repo"] is not None, "Repo should not be None"

    def test_github_runs_run_details(self):
        """GitHub runs have required details"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        data = response.json()
        if len(data.get("runs", [])) > 0:
            run = data["runs"][0]
            assert "id" in run, "Run missing 'id'"
            assert "name" in run, "Run missing 'name'"
            assert "status" in run, "Run missing 'status'"
            assert "conclusion" in run, "Run missing 'conclusion'"
            assert "branch" in run, "Run missing 'branch'"
            assert "html_url" in run, "Run missing 'html_url'"
        else:
            pytest.skip("No workflow runs to test")

    def test_github_runs_limit_param(self):
        """GitHub runs respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("runs", [])) <= 5, "Should respect limit parameter"


class TestTerraformState:
    """Test GET /api/cve/iac/terraform/state endpoint - S3-stored Terraform state"""

    def test_terraform_state_returns_200(self):
        """Terraform state endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/state?environment=dev")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_terraform_state_connected(self):
        """Terraform state shows connected status (even if no state file exists)"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/state?environment=dev")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, "Should be connected to S3"

    def test_terraform_state_has_error_or_resources(self):
        """Terraform state returns error message or resources list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/state?environment=dev")
        data = response.json()
        assert "error" in data or "resources" in data, "Should have 'error' or 'resources'"
        # Expected: error about missing state file (no Terraform deployed yet)
        if data.get("error"):
            assert "state" in data["error"].lower() or "s3" in data["error"].lower()

    def test_terraform_state_invalid_env_returns_400(self):
        """Terraform state with invalid environment returns 400"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/state?environment=invalid")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestOverviewLiveConnections:
    """Test that /api/cve/iac/overview includes live_connections field"""

    def test_overview_has_live_connections(self):
        """Overview now includes live_connections field"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        assert "live_connections" in data, "Missing 'live_connections' field in overview"

    def test_overview_live_connections_structure(self):
        """Overview live_connections has correct structure"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        live = data.get("live_connections", {})
        assert "aws_lambda" in live, "Missing 'aws_lambda' in live_connections"
        assert "aws_s3" in live, "Missing 'aws_s3' in live_connections"
        assert "github" in live, "Missing 'github' in live_connections"

    def test_overview_live_connections_values(self):
        """Overview live_connections shows all services connected"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        live = data.get("live_connections", {})
        assert live.get("aws_lambda", {}).get("connected") == True, "AWS Lambda should be connected"
        assert live.get("aws_s3", {}).get("connected") == True, "AWS S3 should be connected"
        assert live.get("github", {}).get("connected") == True, "GitHub should be connected"


class TestExistingEndpointsStillWork:
    """Verify existing endpoints still work after live endpoints added"""

    def test_terraform_endpoint_works(self):
        """GET /api/cve/iac/terraform still works"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform")
        assert response.status_code == 200
        data = response.json()
        assert "main_tf" in data

    def test_lambda_endpoint_works(self):
        """GET /api/cve/iac/lambda still works"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda")
        assert response.status_code == 200
        data = response.json()
        assert "runtime" in data

    def test_workflow_endpoint_works(self):
        """GET /api/cve/iac/workflow still works"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/workflow")
        assert response.status_code == 200
        data = response.json()
        assert "exists" in data

    def test_deployments_get_works(self):
        """GET /api/cve/iac/deployments still works"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/deployments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_deployments_post_works(self):
        """POST /api/cve/iac/deployments still works"""
        payload = {
            "environment": "dev",
            "component": "test",
            "status": "success",
            "deployed_by": "live_test_suite",
            "notes": "Test from live endpoints test"
        }
        response = requests.post(
            f"{BASE_URL}/api/cve/iac/deployments",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["environment"] == "dev"

    def test_commands_dev_endpoint_works(self):
        """GET /api/cve/iac/commands/dev still works"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/dev")
        assert response.status_code == 200
        data = response.json()
        assert "steps" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
