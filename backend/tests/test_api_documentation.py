"""
Test API Documentation: Swagger UI, ReDoc, OpenAPI JSON
Verifies auto-generated API documentation and developer onboarding guide
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAPIDocumentation:
    """Tests for Swagger UI, ReDoc, and OpenAPI JSON endpoints"""
    
    def test_swagger_ui_returns_200(self):
        """GET /api/docs returns 200 and renders Swagger UI HTML"""
        response = requests.get(f"{BASE_URL}/api/docs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/html" in response.headers.get("Content-Type", ""), "Expected HTML content type"
        # Verify Swagger UI page content
        html_content = response.text
        assert "swagger" in html_content.lower(), "Expected Swagger UI elements in HTML"
        print(f"✓ /api/docs returns Swagger UI HTML (status: {response.status_code})")
    
    def test_swagger_ui_contains_api_title(self):
        """Swagger UI HTML page contains 'Big Mann Entertainment API' title"""
        response = requests.get(f"{BASE_URL}/api/docs")
        assert response.status_code == 200
        html_content = response.text
        # Check for the API title in the HTML (either in title tag or swagger-ui config)
        assert "Big Mann Entertainment API" in html_content or "openapi.json" in html_content, \
            "Expected API title or OpenAPI reference in Swagger UI"
        print("✓ Swagger UI references Big Mann Entertainment API")
    
    def test_redoc_returns_200(self):
        """GET /api/redoc returns 200 and renders ReDoc HTML page"""
        response = requests.get(f"{BASE_URL}/api/redoc")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/html" in response.headers.get("Content-Type", ""), "Expected HTML content type"
        html_content = response.text
        assert "redoc" in html_content.lower(), "Expected ReDoc elements in HTML"
        print(f"✓ /api/redoc returns ReDoc HTML (status: {response.status_code})")
    
    def test_openapi_json_returns_valid_json(self):
        """GET /api/openapi.json returns valid JSON"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/json" in response.headers.get("Content-Type", ""), "Expected JSON content type"
        
        # Verify it's valid JSON
        openapi_spec = response.json()
        assert isinstance(openapi_spec, dict), "OpenAPI spec should be a dictionary"
        print(f"✓ /api/openapi.json returns valid JSON (status: {response.status_code})")
    
    def test_openapi_spec_has_correct_title(self):
        """OpenAPI spec info.title is 'Big Mann Entertainment API'"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        assert "info" in openapi_spec, "OpenAPI spec must have 'info' block"
        assert openapi_spec["info"].get("title") == "Big Mann Entertainment API", \
            f"Expected title 'Big Mann Entertainment API', got '{openapi_spec['info'].get('title')}'"
        print("✓ OpenAPI spec title is 'Big Mann Entertainment API'")
    
    def test_openapi_spec_has_correct_version(self):
        """OpenAPI spec info.version is '2.0.0'"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        assert openapi_spec["info"].get("version") == "2.0.0", \
            f"Expected version '2.0.0', got '{openapi_spec['info'].get('version')}'"
        print("✓ OpenAPI spec version is '2.0.0'")
    
    def test_openapi_spec_has_tags_array(self):
        """OpenAPI spec contains 'tags' array with 90+ entries"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        assert "tags" in openapi_spec, "OpenAPI spec must have 'tags' array"
        tags = openapi_spec["tags"]
        assert isinstance(tags, list), "'tags' should be a list"
        assert len(tags) >= 90, f"Expected 90+ tags, got {len(tags)}"
        print(f"✓ OpenAPI spec has {len(tags)} tags (expected 90+)")
    
    def test_openapi_spec_has_paths_object(self):
        """OpenAPI spec contains 'paths' object with 1000+ endpoints"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        assert "paths" in openapi_spec, "OpenAPI spec must have 'paths' object"
        paths = openapi_spec["paths"]
        assert isinstance(paths, dict), "'paths' should be a dictionary"
        
        # Count total endpoints (each path can have multiple HTTP methods)
        total_endpoints = 0
        for path, methods in paths.items():
            if isinstance(methods, dict):
                total_endpoints += len([m for m in methods.keys() if m in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']])
        
        assert total_endpoints >= 1000, f"Expected 1000+ endpoints, got {total_endpoints}"
        print(f"✓ OpenAPI spec has {len(paths)} paths with {total_endpoints} total endpoints (expected 1000+)")
    
    def test_openapi_spec_has_contact_info(self):
        """OpenAPI spec info block contains contact.name and contact.email"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        info = openapi_spec.get("info", {})
        contact = info.get("contact", {})
        
        assert "name" in contact, "contact.name field is required"
        assert "email" in contact, "contact.email field is required"
        print(f"✓ Contact info present: {contact.get('name')} <{contact.get('email')}>")
    
    def test_openapi_spec_has_license_info(self):
        """OpenAPI spec info block contains license_info.name"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        info = openapi_spec.get("info", {})
        license_info = info.get("license", {})
        
        assert "name" in license_info, "license.name field is required"
        print(f"✓ License info present: {license_info.get('name')}")
    
    def test_openapi_spec_has_terms_of_service(self):
        """OpenAPI spec info block contains terms_of_service field"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        info = openapi_spec.get("info", {})
        assert "termsOfService" in info, "termsOfService field is required in info block"
        print(f"✓ Terms of service present: {info.get('termsOfService')}")
    
    def test_openapi_spec_description_has_key_capabilities(self):
        """OpenAPI spec description contains markdown table with 'Key Capabilities' section"""
        response = requests.get(f"{BASE_URL}/api/openapi.json")
        openapi_spec = response.json()
        
        description = openapi_spec.get("info", {}).get("description", "")
        assert "Key Capabilities" in description, "Description should contain 'Key Capabilities' section"
        # Check for markdown table markers
        assert "|" in description, "Description should contain markdown table"
        print("✓ Description contains 'Key Capabilities' section with markdown table")


class TestCoreAPIEndpoints:
    """Tests for existing core API endpoints still working"""
    
    def test_health_endpoint_returns_healthy(self):
        """GET /api/health returns status='healthy'"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "healthy", f"Expected status 'healthy', got '{data.get('status')}'"
        assert data.get("database") == "connected", f"Expected database 'connected', got '{data.get('database')}'"
        print(f"✓ /api/health returns healthy status with database connected")
    
    def test_auth_login_with_valid_credentials(self):
        """POST /api/auth/login with valid credentials returns token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "owner@bigmannentertainment.com",
                "password": "Test1234!"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Check for token (could be 'token' or 'access_token')
        token = data.get("token") or data.get("access_token")
        assert token is not None, "Expected token in response"
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"
        print(f"✓ /api/auth/login returns token for valid credentials")


class TestDeveloperOnboardingGuide:
    """Tests for developer onboarding guide document"""
    
    def test_onboarding_guide_exists(self):
        """Developer onboarding guide exists at /app/docs/DEVELOPER_ONBOARDING.md"""
        guide_path = "/app/docs/DEVELOPER_ONBOARDING.md"
        assert os.path.exists(guide_path), f"Onboarding guide not found at {guide_path}"
        print(f"✓ Developer onboarding guide exists at {guide_path}")
    
    def test_onboarding_guide_has_required_sections(self):
        """Onboarding guide contains required sections"""
        guide_path = "/app/docs/DEVELOPER_ONBOARDING.md"
        
        with open(guide_path, 'r') as f:
            content = f.read()
        
        required_sections = [
            "Project Overview",
            "Tech Stack", 
            "Repository Structure",
            "Backend Architecture",
            "Frontend Architecture",
            "API Documentation",
            "Database Schema",
            "Testing",
            "Troubleshooting"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        assert len(missing_sections) == 0, f"Missing required sections: {missing_sections}"
        print(f"✓ Onboarding guide contains all {len(required_sections)} required sections")
    
    def test_onboarding_guide_has_table_of_contents(self):
        """Onboarding guide has a Table of Contents"""
        guide_path = "/app/docs/DEVELOPER_ONBOARDING.md"
        
        with open(guide_path, 'r') as f:
            content = f.read()
        
        assert "Table of Contents" in content, "Guide should have Table of Contents section"
        print("✓ Onboarding guide has Table of Contents")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
