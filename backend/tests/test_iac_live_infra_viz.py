"""
IaC Live Infrastructure Visualization Tests
Tests for new live AWS/GitHub visualization API endpoints:
- GET /api/cve/iac/live-status (CloudWatch connection status)
- GET /api/cve/iac/github/repo (repo info, commits, branches, PRs)
- GET /api/cve/iac/s3/artifacts (S3 bucket objects with prefix filter)
- GET /api/cve/iac/cloudwatch/alarms (CloudWatch alarms)
- GET /api/cve/iac/terraform/modules (Terraform module structure)
- GET /api/cve/iac/cdk/constructs (CDK construct structure)
- GET /api/cve/iac/overview (live_connections included)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestLiveStatusCloudWatch:
    """Test GET /api/cve/iac/live-status endpoint - CloudWatch connectivity included"""

    def test_live_status_returns_200(self):
        """Live status endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_live_status_all_connections(self):
        """Live status includes Lambda, S3, GitHub connections"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert "aws_lambda" in data, "Missing 'aws_lambda' field"
        assert "aws_s3" in data, "Missing 'aws_s3' field"
        assert "github" in data, "Missing 'github' field"
        assert "checked_at" in data, "Missing 'checked_at' field"

    def test_live_status_aws_lambda_connected(self):
        """AWS Lambda should be connected"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert data["aws_lambda"]["connected"] == True, f"AWS Lambda not connected: {data['aws_lambda'].get('detail')}"
        assert "region" in data["aws_lambda"], "Missing region in aws_lambda"

    def test_live_status_aws_s3_connected(self):
        """AWS S3 should be connected"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert data["aws_s3"]["connected"] == True, f"AWS S3 not connected: {data['aws_s3'].get('detail')}"
        assert "bucket" in data["aws_s3"], "Missing bucket in aws_s3"

    def test_live_status_github_connected(self):
        """GitHub should be connected"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        data = response.json()
        assert data["github"]["connected"] == True, f"GitHub not connected: {data['github'].get('detail')}"
        assert "user" in data["github"], "Missing user in github"


class TestGitHubRepoInfo:
    """Test GET /api/cve/iac/github/repo endpoint - repo info, commits, branches, PRs"""

    def test_github_repo_returns_200(self):
        """GitHub repo endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/repo")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_github_repo_connected(self):
        """GitHub repo shows connected status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/repo")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, f"GitHub repo not connected: {data.get('error')}"

    def test_github_repo_has_repo_info(self):
        """GitHub repo returns repo metadata"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/repo")
        data = response.json()
        assert "repo" in data, "Missing 'repo' field"
        repo = data["repo"]
        assert "name" in repo, "Missing repo name"
        assert "default_branch" in repo, "Missing default_branch"
        assert "language" in repo, "Missing language"

    def test_github_repo_has_commits(self):
        """GitHub repo returns recent commits"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/repo")
        data = response.json()
        assert "commits" in data, "Missing 'commits' field"
        assert isinstance(data["commits"], list), "commits should be a list"
        if len(data["commits"]) > 0:
            commit = data["commits"][0]
            assert "sha" in commit, "Commit missing sha"
            assert "message" in commit, "Commit missing message"
            assert "author" in commit, "Commit missing author"

    def test_github_repo_has_branches(self):
        """GitHub repo returns branches"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/repo")
        data = response.json()
        assert "branches" in data, "Missing 'branches' field"
        assert isinstance(data["branches"], list), "branches should be a list"
        if len(data["branches"]) > 0:
            branch = data["branches"][0]
            assert "name" in branch, "Branch missing name"
            assert "sha" in branch, "Branch missing sha"

    def test_github_repo_has_pulls(self):
        """GitHub repo returns open pull requests"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/repo")
        data = response.json()
        assert "pulls" in data, "Missing 'pulls' field"
        assert isinstance(data["pulls"], list), "pulls should be a list"


class TestS3Artifacts:
    """Test GET /api/cve/iac/s3/artifacts endpoint - S3 bucket objects with prefix filter"""

    def test_s3_artifacts_returns_200(self):
        """S3 artifacts endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/s3/artifacts")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_s3_artifacts_connected(self):
        """S3 artifacts shows connected status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/s3/artifacts")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, f"S3 not connected: {data.get('error')}"

    def test_s3_artifacts_has_bucket(self):
        """S3 artifacts returns bucket name"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/s3/artifacts")
        data = response.json()
        assert "bucket" in data, "Missing 'bucket' field"
        assert data["bucket"] == "bigmann-entertainment-media", f"Unexpected bucket: {data['bucket']}"

    def test_s3_artifacts_has_objects(self):
        """S3 artifacts returns objects list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/s3/artifacts")
        data = response.json()
        assert "objects" in data, "Missing 'objects' field"
        assert isinstance(data["objects"], list), "objects should be a list"
        assert "total_objects" in data, "Missing 'total_objects' field"

    def test_s3_artifacts_object_details(self):
        """S3 artifacts objects have required details"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/s3/artifacts")
        data = response.json()
        if len(data.get("objects", [])) > 0:
            obj = data["objects"][0]
            assert "key" in obj, "Object missing 'key'"
            assert "size_bytes" in obj, "Object missing 'size_bytes'"
            assert "size_display" in obj, "Object missing 'size_display'"
            assert "last_modified" in obj, "Object missing 'last_modified'"
            assert "storage_class" in obj, "Object missing 'storage_class'"
        else:
            pytest.skip("No S3 objects to test")

    def test_s3_artifacts_prefix_filter(self):
        """S3 artifacts prefix filter works"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/s3/artifacts?prefix=audio/")
        assert response.status_code == 200
        data = response.json()
        assert "prefix" in data, "Missing 'prefix' field"
        assert data["prefix"] == "audio/", "Prefix should be 'audio/'"
        # All returned objects should start with the prefix
        for obj in data.get("objects", []):
            assert obj["key"].startswith("audio/"), f"Object key '{obj['key']}' doesn't start with 'audio/'"

    def test_s3_artifacts_max_keys(self):
        """S3 artifacts respects max_keys parameter"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/s3/artifacts?max_keys=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("objects", [])) <= 10, "Should respect max_keys parameter"


class TestCloudWatchAlarms:
    """Test GET /api/cve/iac/cloudwatch/alarms endpoint - CloudWatch alarms"""

    def test_cloudwatch_alarms_returns_200(self):
        """CloudWatch alarms endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cloudwatch/alarms")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_cloudwatch_alarms_connected(self):
        """CloudWatch alarms shows connected status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cloudwatch/alarms")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, f"CloudWatch not connected: {data.get('error')}"

    def test_cloudwatch_alarms_has_alarms_list(self):
        """CloudWatch alarms returns alarms list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cloudwatch/alarms")
        data = response.json()
        assert "alarms" in data, "Missing 'alarms' field"
        assert isinstance(data["alarms"], list), "alarms should be a list"
        assert "total" in data, "Missing 'total' field"
        assert "in_alarm" in data, "Missing 'in_alarm' field"

    def test_cloudwatch_alarms_has_composite(self):
        """CloudWatch alarms returns composite alarms list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cloudwatch/alarms")
        data = response.json()
        assert "composite_alarms" in data, "Missing 'composite_alarms' field"
        assert isinstance(data["composite_alarms"], list), "composite_alarms should be a list"

    def test_cloudwatch_alarm_details(self):
        """CloudWatch alarms have required details"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cloudwatch/alarms")
        data = response.json()
        if len(data.get("alarms", [])) > 0:
            alarm = data["alarms"][0]
            assert "name" in alarm, "Alarm missing 'name'"
            assert "state" in alarm, "Alarm missing 'state'"
            assert alarm["state"] in ["OK", "ALARM", "INSUFFICIENT_DATA"], f"Invalid alarm state: {alarm['state']}"
        else:
            pytest.skip("No CloudWatch alarms configured to test")


class TestTerraformModules:
    """Test GET /api/cve/iac/terraform/modules endpoint - Terraform module structure"""

    def test_terraform_modules_returns_200(self):
        """Terraform modules endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_terraform_modules_structure(self):
        """Terraform modules returns expected structure"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        assert "exists" in data, "Missing 'exists' field"
        assert "modules" in data, "Missing 'modules' field"
        assert isinstance(data["modules"], list), "modules should be a list"

    def test_terraform_modules_totals(self):
        """Terraform modules returns total counts"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        assert "total_modules" in data, "Missing 'total_modules' field"
        assert "total_resources" in data, "Missing 'total_resources' field"

    def test_terraform_module_details(self):
        """Terraform modules have required metadata"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        if data.get("exists") and len(data.get("modules", [])) > 0:
            mod = data["modules"][0]
            assert "name" in mod, "Module missing 'name'"
            assert "description" in mod, "Module missing 'description'"
            assert "icon" in mod, "Module missing 'icon'"
            assert "category" in mod, "Module missing 'category'"
            assert "files" in mod, "Module missing 'files'"
            assert "resources" in mod, "Module missing 'resources'"
        else:
            pytest.skip("No Terraform modules found")


class TestCdkConstructs:
    """Test GET /api/cve/iac/cdk/constructs endpoint - CDK construct structure"""

    def test_cdk_constructs_returns_200(self):
        """CDK constructs endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_cdk_constructs_structure(self):
        """CDK constructs returns expected structure"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        assert "exists" in data, "Missing 'exists' field"
        assert "constructs" in data, "Missing 'constructs' field"
        assert isinstance(data["constructs"], list), "constructs should be a list"

    def test_cdk_constructs_totals(self):
        """CDK constructs returns total counts"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        assert "total_constructs" in data, "Missing 'total_constructs' field"
        assert "total_services" in data, "Missing 'total_services' field"

    def test_cdk_construct_details(self):
        """CDK constructs have required metadata"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        if data.get("exists") and len(data.get("constructs", [])) > 0:
            construct = data["constructs"][0]
            assert "name" in construct, "Construct missing 'name'"
            assert "description" in construct, "Construct missing 'description'"
            assert "icon" in construct, "Construct missing 'icon'"
            assert "category" in construct, "Construct missing 'category'"
            assert "services" in construct, "Construct missing 'services'"
        else:
            pytest.skip("No CDK constructs found")


class TestOverviewLiveConnections:
    """Test GET /api/cve/iac/overview includes live_connections"""

    def test_overview_returns_200(self):
        """Overview endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_overview_has_live_connections(self):
        """Overview includes live_connections field"""
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

    def test_overview_live_all_connected(self):
        """Overview shows all services connected"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        live = data.get("live_connections", {})
        assert live.get("aws_lambda", {}).get("connected") == True, "AWS Lambda should be connected"
        assert live.get("aws_s3", {}).get("connected") == True, "AWS S3 should be connected"
        assert live.get("github", {}).get("connected") == True, "GitHub should be connected"


class TestLambdaLive:
    """Test GET /api/cve/iac/lambda/live - Lambda functions with CloudWatch metrics"""

    def test_lambda_live_returns_200(self):
        """Lambda live endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_lambda_live_connected(self):
        """Lambda live shows connected status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, f"Lambda not connected: {data.get('error')}"

    def test_lambda_live_has_functions(self):
        """Lambda live returns functions list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        assert "functions" in data, "Missing 'functions' field"
        assert isinstance(data["functions"], list), "functions should be a list"
        assert "total" in data, "Missing 'total' field"

    def test_lambda_live_function_metrics(self):
        """Lambda functions have CloudWatch metrics"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        data = response.json()
        if len(data.get("functions", [])) > 0:
            fn = data["functions"][0]
            assert "metrics" in fn, "Function missing 'metrics'"
            metrics = fn["metrics"]
            # Metrics should include invocations, errors, duration, throttles
            assert isinstance(metrics, dict), "metrics should be a dict"


class TestGitHubRuns:
    """Test GET /api/cve/iac/github/runs - GitHub Actions workflow runs"""

    def test_github_runs_returns_200(self):
        """GitHub runs endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_github_runs_connected(self):
        """GitHub runs shows connected status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == True, f"GitHub not connected: {data.get('error')}"

    def test_github_runs_has_runs(self):
        """GitHub runs returns runs list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        data = response.json()
        assert "runs" in data, "Missing 'runs' field"
        assert isinstance(data["runs"], list), "runs should be a list"

    def test_github_runs_limit_param(self):
        """GitHub runs respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("runs", [])) <= 5, "Should respect limit parameter"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
