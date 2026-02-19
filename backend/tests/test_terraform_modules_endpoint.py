"""
Test suite for GET /api/cve/iac/terraform/modules endpoint
Tests the Terraform module structure, file contents, and metadata.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTerraformModulesEndpoint:
    """Tests for GET /api/cve/iac/terraform/modules endpoint"""
    
    def test_terraform_modules_endpoint_returns_200(self):
        """Test that the endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        assert response.status_code == 200
        print("PASS: Endpoint returns 200")
    
    def test_terraform_modules_count_is_11(self):
        """Test that the endpoint returns exactly 11 modules"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        assert data.get('exists') == True
        assert data.get('total_modules') == 11
        print(f"PASS: total_modules = {data.get('total_modules')}")
    
    def test_terraform_total_resources_is_30(self):
        """Test that total resources count is 30"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        assert data.get('total_resources') == 30
        print(f"PASS: total_resources = {data.get('total_resources')}")
    
    def test_terraform_environments_count_is_2(self):
        """Test that there are 2 environments (prod, staging)"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        environments = data.get('environments', [])
        assert len(environments) == 2
        env_names = [e['name'] for e in environments]
        assert 'prod' in env_names
        assert 'staging' in env_names
        print(f"PASS: environments = {env_names}")
    
    def test_all_11_modules_present(self):
        """Test that all 11 expected modules are present"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get('modules', [])
        module_names = [m['name'] for m in modules]
        
        expected_modules = [
            "cognito", "dynamodb", "eventbridge", "kinesis", "lambda",
            "media-convert", "qldb", "s3-cloudfront", "secrets-manager",
            "sns", "stepfunctions"
        ]
        
        for mod in expected_modules:
            assert mod in module_names, f"Missing module: {mod}"
        
        print(f"PASS: All 11 modules present: {module_names}")
    
    def test_module_has_required_fields(self):
        """Test that each module has required fields"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get('modules', [])
        
        required_fields = ['name', 'description', 'icon', 'category', 'files', 'resources', 'variables', 'outputs']
        
        for mod in modules:
            for field in required_fields:
                assert field in mod, f"Module {mod.get('name')} missing field: {field}"
        
        print(f"PASS: All modules have required fields")
    
    def test_cognito_module_structure(self):
        """Test cognito module has correct resources, variables, outputs"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get('modules', [])
        cognito = next((m for m in modules if m['name'] == 'cognito'), None)
        
        assert cognito is not None
        assert cognito['category'] == 'auth'
        assert len(cognito['resources']) == 2  # aws_cognito_user_pool, aws_cognito_user_pool_client
        assert 'project' in cognito['variables']
        assert 'env' in cognito['variables']
        assert 'user_pool_id' in cognito['outputs']
        assert 'user_pool_client_id' in cognito['outputs']
        
        # Check files
        assert 'main.tf' in cognito['files']
        assert 'variables.tf' in cognito['files']
        assert 'outputs.tf' in cognito['files']
        
        print(f"PASS: Cognito module structure verified")
    
    def test_lambda_module_has_6_resources(self):
        """Test lambda module has 6 resources"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get('modules', [])
        lambda_mod = next((m for m in modules if m['name'] == 'lambda'), None)
        
        assert lambda_mod is not None
        assert lambda_mod['resource_count'] == 6
        assert lambda_mod['category'] == 'compute'
        
        print(f"PASS: Lambda module has {lambda_mod['resource_count']} resources")
    
    def test_dynamodb_module_has_4_resources(self):
        """Test dynamodb module has 4 resources"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        modules = data.get('modules', [])
        dynamodb = next((m for m in modules if m['name'] == 'dynamodb'), None)
        
        assert dynamodb is not None
        assert dynamodb['resource_count'] == 4
        assert dynamodb['category'] == 'database'
        
        print(f"PASS: DynamoDB module has {dynamodb['resource_count']} resources")
    
    def test_environment_prod_has_files(self):
        """Test prod environment has configuration files"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        environments = data.get('environments', [])
        prod = next((e for e in environments if e['name'] == 'prod'), None)
        
        assert prod is not None
        assert prod['file_count'] >= 2
        assert 'main.tf' in prod['files'] or 'variables.tf' in prod['files']
        
        print(f"PASS: Prod environment has {prod['file_count']} files")
    
    def test_environment_staging_has_files(self):
        """Test staging environment has configuration files"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/modules")
        data = response.json()
        environments = data.get('environments', [])
        staging = next((e for e in environments if e['name'] == 'staging'), None)
        
        assert staging is not None
        assert staging['file_count'] >= 2
        
        print(f"PASS: Staging environment has {staging['file_count']} files")


class TestExistingIACEndpoints:
    """Tests for existing IaC endpoints to ensure they still work"""
    
    def test_overview_endpoint(self):
        """Test GET /api/cve/iac/overview returns valid data"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/overview")
        assert response.status_code == 200
        data = response.json()
        assert 'terraform' in data
        assert 'lambda' in data
        assert 'github_actions' in data
        print("PASS: Overview endpoint working")
    
    def test_lambda_live_endpoint(self):
        """Test GET /api/cve/iac/lambda/live returns data"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/lambda/live")
        assert response.status_code == 200
        data = response.json()
        assert 'connected' in data
        print(f"PASS: Lambda live endpoint returns connected={data.get('connected')}")
    
    def test_github_runs_endpoint(self):
        """Test GET /api/cve/iac/github/runs returns data"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/github/runs")
        assert response.status_code == 200
        data = response.json()
        assert 'connected' in data
        print(f"PASS: GitHub runs endpoint returns connected={data.get('connected')}")
    
    def test_terraform_state_endpoint(self):
        """Test GET /api/cve/iac/terraform/state returns data"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/terraform/state")
        assert response.status_code == 200
        data = response.json()
        assert 'connected' in data
        print(f"PASS: Terraform state endpoint returns connected={data.get('connected')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
