"""
CDK Constructs and Terraform Modules API Endpoint Tests
Tests for GET /api/cve/iac/cdk/constructs and GET /api/cve/iac/terraform/modules
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCDKConstructsEndpoint:
    """Tests for GET /api/cve/iac/cdk/constructs - CDK construct metadata"""

    def test_cdk_constructs_endpoint_returns_200(self):
        """Test that CDK constructs endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ CDK constructs endpoint returns 200")

    def test_cdk_constructs_exists_true(self):
        """Test that CDK project exists"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        assert data.get("exists") == True, f"Expected exists=true, got {data.get('exists')}"
        print("✓ CDK project exists=true")

    def test_cdk_constructs_count_is_8(self):
        """Test that 8 CDK constructs are returned"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        assert data.get("total_constructs") == 8, f"Expected 8 constructs, got {data.get('total_constructs')}"
        print("✓ CDK has 8 constructs")

    def test_cdk_services_count_is_20(self):
        """Test that 20 total services are returned"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        assert data.get("total_services") == 20, f"Expected 20 services, got {data.get('total_services')}"
        print("✓ CDK has 20 services")

    def test_cdk_constructs_list_names(self):
        """Test that all 8 expected constructs are present"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        constructs = data.get("constructs", [])
        names = [c["name"] for c in constructs]
        expected = ["api", "auth", "dynamodb", "eventbridge", "frontend", "kinesis", "lambdas", "qldb"]
        for expected_name in expected:
            assert expected_name in names, f"Missing construct: {expected_name}"
        print(f"✓ All 8 constructs present: {', '.join(expected)}")

    def test_cdk_construct_has_required_fields(self):
        """Test that each construct has required fields: name, file, description, icon, category, services, exports, code, lines"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        constructs = data.get("constructs", [])
        required_fields = ["name", "file", "description", "icon", "category", "services", "exports", "code", "lines"]
        for c in constructs:
            for field in required_fields:
                assert field in c, f"Construct {c.get('name')} missing field: {field}"
        print(f"✓ All constructs have required fields: {', '.join(required_fields)}")

    def test_cdk_stack_file_present(self):
        """Test that stack_file is returned with name and code"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        stack_file = data.get("stack_file", {})
        assert stack_file.get("name") == "lib/infra-stack.ts", f"Expected lib/infra-stack.ts, got {stack_file.get('name')}"
        assert stack_file.get("code") is not None and len(stack_file.get("code", "")) > 0, "stack_file code is empty"
        assert stack_file.get("lines", 0) > 0, "stack_file lines should be > 0"
        print(f"✓ stack_file present: {stack_file.get('name')} ({stack_file.get('lines')} lines)")

    def test_cdk_entry_file_present(self):
        """Test that entry_file is returned with name and code"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        entry_file = data.get("entry_file", {})
        assert entry_file.get("name") == "bin/infra.ts", f"Expected bin/infra.ts, got {entry_file.get('name')}"
        assert entry_file.get("code") is not None and len(entry_file.get("code", "")) > 0, "entry_file code is empty"
        assert entry_file.get("lines", 0) > 0, "entry_file lines should be > 0"
        print(f"✓ entry_file present: {entry_file.get('name')} ({entry_file.get('lines')} lines)")

    def test_cdk_config_files_present(self):
        """Test that config_files contains package.json, cdk.json, tsconfig.json"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        config_files = data.get("config_files", {})
        expected = ["package.json", "cdk.json", "tsconfig.json"]
        for fname in expected:
            assert fname in config_files, f"Missing config file: {fname}"
            assert config_files[fname] is not None and len(config_files[fname]) > 0, f"{fname} content is empty"
        print(f"✓ config_files present: {', '.join(expected)}")

    def test_cdk_auth_construct_details(self):
        """Test auth construct has correct services"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        constructs = data.get("constructs", [])
        auth = next((c for c in constructs if c["name"] == "auth"), None)
        assert auth is not None, "auth construct not found"
        assert auth["category"] == "auth", f"Expected category=auth, got {auth.get('category')}"
        assert "Cognito" in auth["description"], f"auth description should mention Cognito"
        assert len(auth["services"]) == 2, f"Expected 2 services for auth, got {len(auth['services'])}"
        print(f"✓ auth construct: services={auth['services']}")

    def test_cdk_lambdas_construct_details(self):
        """Test lambdas construct has correct services"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/cdk/constructs")
        data = response.json()
        constructs = data.get("constructs", [])
        lambdas = next((c for c in constructs if c["name"] == "lambdas"), None)
        assert lambdas is not None, "lambdas construct not found"
        assert lambdas["category"] == "compute", f"Expected category=compute, got {lambdas.get('category')}"
        assert len(lambdas["services"]) == 4, f"Expected 4 services for lambdas, got {len(lambdas['services'])}"
        print(f"✓ lambdas construct: services={lambdas['services']}")


class TestTerraformModulesEndpoint:
    """Tests for GET /api/cve/iac/terraform/modules - Terraform module metadata"""

    def test_terraform_modules_endpoint_returns_200(self):
        """Test that Terraform modules endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Terraform modules endpoint returns 200")

    def test_terraform_modules_exists_true(self):
        """Test that Terraform modules exist"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        assert data.get("exists") == True, f"Expected exists=true, got {data.get('exists')}"
        print("✓ Terraform modules exists=true")

    def test_terraform_modules_count_is_12(self):
        """Test that 12 Terraform modules are returned (including vpc)"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        assert data.get("total_modules") == 12, f"Expected 12 modules, got {data.get('total_modules')}"
        print("✓ Terraform has 12 modules")

    def test_terraform_resources_count_is_40(self):
        """Test that 40 total resources are returned"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        assert data.get("total_resources") == 40, f"Expected 40 resources, got {data.get('total_resources')}"
        print("✓ Terraform has 40 total resources")

    def test_terraform_modules_list_names(self):
        """Test that all 12 expected modules are present including vpc"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get("modules", [])
        names = [m["name"] for m in modules]
        expected = ["cognito", "dynamodb", "eventbridge", "kinesis", "lambda", "media-convert", 
                    "qldb", "s3-cloudfront", "secrets-manager", "sns", "stepfunctions", "vpc"]
        for expected_name in expected:
            assert expected_name in names, f"Missing module: {expected_name}"
        print(f"✓ All 12 modules present including vpc")

    def test_terraform_vpc_module_exists(self):
        """Test that vpc module is present"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get("modules", [])
        vpc = next((m for m in modules if m["name"] == "vpc"), None)
        assert vpc is not None, "vpc module not found"
        print("✓ vpc module exists")

    def test_terraform_vpc_module_category(self):
        """Test that vpc module has networking category"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get("modules", [])
        vpc = next((m for m in modules if m["name"] == "vpc"), None)
        assert vpc["category"] == "networking", f"Expected category=networking, got {vpc.get('category')}"
        print(f"✓ vpc module category=networking")

    def test_terraform_vpc_module_resources_count(self):
        """Test that vpc module has 10 resources"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get("modules", [])
        vpc = next((m for m in modules if m["name"] == "vpc"), None)
        assert vpc["resource_count"] == 10, f"Expected 10 resources, got {vpc.get('resource_count')}"
        print(f"✓ vpc module has 10 resources")

    def test_terraform_vpc_module_resources_list(self):
        """Test that vpc module has expected resources: vpc, private subnet, public subnet, igw, eip, nat, route tables"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get("modules", [])
        vpc = next((m for m in modules if m["name"] == "vpc"), None)
        resource_types = [r["type"] for r in vpc.get("resources", [])]
        expected_types = ["aws_vpc", "aws_subnet", "aws_internet_gateway", "aws_eip", 
                         "aws_nat_gateway", "aws_route_table", "aws_route_table_association"]
        for expected_type in expected_types:
            assert expected_type in resource_types, f"Missing resource type: {expected_type}"
        print(f"✓ vpc module has all expected resource types")

    def test_terraform_vpc_module_files(self):
        """Test that vpc module has main.tf file with content"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get("modules", [])
        vpc = next((m for m in modules if m["name"] == "vpc"), None)
        files = vpc.get("files", {})
        assert "main.tf" in files, "vpc module missing main.tf"
        assert files["main.tf"] is not None and len(files["main.tf"]) > 0, "main.tf content is empty"
        print(f"✓ vpc module has main.tf with content")

    def test_terraform_module_has_required_fields(self):
        """Test that each module has required fields"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get("modules", [])
        required_fields = ["name", "description", "icon", "category", "files", "resources", "variables", "outputs", "file_count", "resource_count"]
        for m in modules:
            for field in required_fields:
                assert field in m, f"Module {m.get('name')} missing field: {field}"
        print(f"✓ All modules have required fields")


class TestExistingEndpoints:
    """Tests to verify existing endpoints still work"""

    def test_overview_endpoint(self):
        """Test that overview endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        assert response.status_code == 200
        data = response.json()
        assert "terraform" in data
        assert "lambda" in data
        assert "github_actions" in data
        print("✓ overview endpoint works")

    def test_live_status_endpoint(self):
        """Test that live-status endpoint returns connection info"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/live-status")
        assert response.status_code == 200
        data = response.json()
        assert "aws_lambda" in data
        assert "aws_s3" in data
        assert "github" in data
        print("✓ live-status endpoint works")

    def test_lambda_live_endpoint(self):
        """Test that lambda/live endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        print("✓ lambda/live endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
