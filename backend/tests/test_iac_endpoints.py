"""
IaC Endpoints Tests
Tests for Infrastructure as Code management API endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestIaCOverview:
    """Test GET /api/cve/iac/overview endpoint"""

    def test_overview_returns_200(self):
        """Overview endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_overview_has_terraform_status(self):
        """Overview includes terraform configuration status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        assert "terraform" in data, "Missing 'terraform' field"
        assert "configured" in data["terraform"], "Missing 'configured' in terraform"
        assert isinstance(data["terraform"]["configured"], bool)

    def test_overview_has_lambda_status(self):
        """Overview includes lambda configuration status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        assert "lambda" in data, "Missing 'lambda' field"
        assert "configured" in data["lambda"], "Missing 'configured' in lambda"
        assert isinstance(data["lambda"]["configured"], bool)

    def test_overview_has_github_actions_status(self):
        """Overview includes github_actions configuration status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        assert "github_actions" in data, "Missing 'github_actions' field"
        assert "configured" in data["github_actions"], "Missing 'configured' in github_actions"
        assert isinstance(data["github_actions"]["configured"], bool)

    def test_overview_has_environments(self):
        """Overview includes environments list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        assert "environments" in data, "Missing 'environments' field"
        assert isinstance(data["environments"], list)
        assert len(data["environments"]) == 3, "Should have 3 environments (dev, staging, prod)"
        for env in data["environments"]:
            assert "name" in env
            assert "configured" in env

    def test_overview_has_deployment_count(self):
        """Overview includes total_deployments count"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        data = response.json()
        assert "total_deployments" in data, "Missing 'total_deployments' field"
        assert isinstance(data["total_deployments"], int)


class TestIaCTerraform:
    """Test GET /api/cve/iac/terraform endpoint"""

    def test_terraform_returns_200(self):
        """Terraform endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_terraform_has_main_tf(self):
        """Terraform includes main.tf content"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform")
        data = response.json()
        assert "main_tf" in data, "Missing 'main_tf' field"
        assert data["main_tf"] is not None, "main_tf should not be None"
        assert "terraform" in data["main_tf"].lower(), "main_tf should contain terraform code"

    def test_terraform_has_environment_configs(self):
        """Terraform includes environment configurations"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform")
        data = response.json()
        assert "environments" in data, "Missing 'environments' field"
        for env in ["dev", "staging", "prod"]:
            assert env in data["environments"], f"Missing environment: {env}"
            assert "exists" in data["environments"][env]
            assert "parsed" in data["environments"][env]


class TestIaCLambda:
    """Test GET /api/cve/iac/lambda endpoint"""

    def test_lambda_returns_200(self):
        """Lambda endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_lambda_has_handler_info(self):
        """Lambda includes handler information"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda")
        data = response.json()
        assert "handler" in data, "Missing 'handler' field"
        assert "file" in data["handler"]
        assert "exists" in data["handler"]

    def test_lambda_has_requirements(self):
        """Lambda includes requirements information"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda")
        data = response.json()
        assert "requirements" in data, "Missing 'requirements' field"
        assert "content" in data["requirements"]
        assert "packages" in data["requirements"]
        assert isinstance(data["requirements"]["packages"], list)

    def test_lambda_has_runtime_details(self):
        """Lambda includes runtime details"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda")
        data = response.json()
        assert "runtime" in data, "Missing 'runtime' field"
        assert "handler_entry" in data, "Missing 'handler_entry' field"
        assert "timeout" in data, "Missing 'timeout' field"
        assert "memory_mb" in data, "Missing 'memory_mb' field"
        assert data["runtime"] == "python3.12"


class TestIaCWorkflow:
    """Test GET /api/cve/iac/workflow endpoint"""

    def test_workflow_returns_200(self):
        """Workflow endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/workflow")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_workflow_has_content(self):
        """Workflow includes build-lambda.yml content"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/workflow")
        data = response.json()
        assert "exists" in data, "Missing 'exists' field"
        assert "content" in data, "Missing 'content' field"
        assert data["exists"] == True, "Workflow should exist"
        assert data["content"] is not None, "content should not be None"
        assert "build" in data["content"].lower() or "lambda" in data["content"].lower()


class TestIaCDeployments:
    """Test GET and POST /api/cve/iac/deployments endpoint"""

    def test_get_deployments_returns_200(self):
        """GET deployments endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/deployments")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_deployments_returns_list(self):
        """GET deployments returns a list"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/deployments")
        data = response.json()
        assert isinstance(data, list), "Deployments should be a list"

    def test_post_deployment_creates_record(self):
        """POST deployments creates a new deployment record"""
        payload = {
            "environment": "dev",
            "component": "lambda",
            "status": "success",
            "deployed_by": "test_suite"
        }
        response = requests.post(
            f"{BASE_URL}/api/cve/iac/deployments",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["environment"] == "dev"
        assert data["component"] == "lambda"
        assert data["status"] == "success"
        assert "deployed_at" in data

    def test_post_deployment_with_all_fields(self):
        """POST deployments with all optional fields"""
        payload = {
            "environment": "staging",
            "component": "terraform",
            "version": "v1.2.3",
            "status": "success",
            "deployed_by": "ci-pipeline",
            "notes": "Test deployment with all fields"
        }
        response = requests.post(
            f"{BASE_URL}/api/cve/iac/deployments",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["version"] == "v1.2.3"
        assert data["notes"] == "Test deployment with all fields"


class TestIaCCommands:
    """Test GET /api/cve/iac/commands/{environment} endpoint"""

    def test_commands_dev_returns_200(self):
        """GET commands/dev returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/dev")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_commands_dev_has_steps(self):
        """GET commands/dev returns deployment steps"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/dev")
        data = response.json()
        assert "environment" in data
        assert data["environment"] == "dev"
        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) > 0
        for step in data["steps"]:
            assert "title" in step
            assert "command" in step
            assert "description" in step

    def test_commands_staging_returns_200(self):
        """GET commands/staging returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/staging")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_commands_staging_has_correct_env(self):
        """GET commands/staging has staging-specific commands"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/staging")
        data = response.json()
        assert data["environment"] == "staging"
        # Check commands contain staging references
        steps_text = " ".join([s["command"] for s in data["steps"]])
        assert "staging" in steps_text

    def test_commands_prod_returns_200(self):
        """GET commands/prod returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/prod")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_commands_prod_has_correct_env(self):
        """GET commands/prod has prod-specific commands"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/prod")
        data = response.json()
        assert data["environment"] == "prod"
        # Check commands contain prod references
        steps_text = " ".join([s["command"] for s in data["steps"]])
        assert "prod" in steps_text

    def test_commands_invalid_env_returns_400(self):
        """GET commands/invalid returns 400 status"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/invalid")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

    def test_commands_invalid_env_error_message(self):
        """GET commands/invalid has proper error message"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/commands/invalid")
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower() or "environment" in data["detail"].lower()


class TestDeploymentPersistence:
    """Test that deployment records persist correctly"""

    def test_create_and_verify_deployment(self):
        """Create deployment and verify it appears in list"""
        # Create deployment
        unique_notes = f"TestPersistence_{os.urandom(4).hex()}"
        payload = {
            "environment": "prod",
            "component": "lambda",
            "status": "success",
            "deployed_by": "persistence_test",
            "notes": unique_notes
        }
        create_response = requests.post(
            f"{BASE_URL}/api/cve/iac/deployments",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert create_response.status_code == 200

        # Verify it appears in list
        list_response = requests.get(f"{BASE_URL}/api/cve/iac/deployments")
        assert list_response.status_code == 200
        deployments = list_response.json()
        found = any(d.get("notes") == unique_notes for d in deployments)
        assert found, f"Deployment with notes '{unique_notes}' not found in list"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
