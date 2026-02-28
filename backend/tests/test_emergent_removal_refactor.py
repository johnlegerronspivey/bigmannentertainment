"""
Test: Emergent Removal Refactoring
Verifies all 'emergent' references have been replaced with native integrations
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cve-refactor-1.preview.emergentagent.com')

# Test credentials
SUPER_ADMIN_EMAIL = "cveadmin@test.com"
SUPER_ADMIN_PASSWORD = "Test1234!"


class TestBackendHealth:
    """Backend health and configuration tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """Verify backend health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"Health check passed: {data['status']}")
    
    def test_api_root_returns_big_mann_info(self):
        """Verify API root returns Big Mann Entertainment info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Big Mann Entertainment API"
        assert data["status"] == "operational"
        print(f"API root shows: {data['message']}")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_super_admin_login_success(self):
        """Super admin can login successfully"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == SUPER_ADMIN_EMAIL
        print(f"Super admin login successful: {data['user']['email']}")
        return data["access_token"]
    
    def test_invalid_login_returns_401(self):
        """Invalid credentials return 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("Invalid login correctly rejected with 401")


class TestCVEEndpoints:
    """CVE Management endpoints tests"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
        )
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cve_dashboard_returns_data(self):
        """CVE dashboard endpoint returns proper data structure"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_cves" in data
        assert "severity_breakdown" in data
        print(f"CVE Dashboard: Total CVEs = {data['total_cves']}")
    
    def test_sla_dashboard_returns_data(self):
        """SLA dashboard endpoint returns proper data structure"""
        response = requests.get(f"{BASE_URL}/api/cve/sla/dashboard", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "overall_compliance" in data
        assert "total_open" in data
        assert "severity_stats" in data
        print(f"SLA Dashboard: Compliance = {data['overall_compliance']}%")


class TestCodebaseRefactoring:
    """Verify no 'emergent' references remain in production code"""
    
    def test_no_emergentintegrations_imports_in_backend(self):
        """Check no emergentintegrations imports in backend Python files"""
        backend_dir = "/app/backend"
        found_imports = []
        
        for root, dirs, files in os.walk(backend_dir):
            # Skip test directories and __pycache__
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'tests', '.pytest_cache']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            # Check for actual imports (not comments/docstrings)
                            if re.search(r'^(from|import)\s+emergentintegrations', content, re.MULTILINE):
                                found_imports.append(filepath)
                    except Exception:
                        pass
        
        if found_imports:
            print(f"Found emergentintegrations imports in: {found_imports}")
        assert len(found_imports) == 0, f"Found emergentintegrations imports in: {found_imports}"
        print("SUCCESS: No emergentintegrations imports found in production code")
    
    def test_no_emergent_llm_key_in_backend(self):
        """Check no EMERGENT_LLM_KEY references in backend files"""
        backend_dir = "/app/backend"
        found_refs = []
        
        for root, dirs, files in os.walk(backend_dir):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'tests', '.pytest_cache']]
            
            for file in files:
                if file.endswith('.py') or file == '.env':
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            if 'EMERGENT_LLM_KEY' in content:
                                found_refs.append(filepath)
                    except Exception:
                        pass
        
        if found_refs:
            print(f"Found EMERGENT_LLM_KEY in: {found_refs}")
        assert len(found_refs) == 0, f"Found EMERGENT_LLM_KEY in: {found_refs}"
        print("SUCCESS: No EMERGENT_LLM_KEY references found")
    
    def test_google_api_key_in_env(self):
        """Verify GOOGLE_API_KEY is set in backend .env"""
        env_path = "/app/backend/.env"
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                assert 'GOOGLE_API_KEY=' in content, "GOOGLE_API_KEY not found in .env"
                # Verify it has a value
                match = re.search(r'GOOGLE_API_KEY=(\S+)', content)
                assert match and len(match.group(1)) > 10, "GOOGLE_API_KEY appears empty or too short"
                print("SUCCESS: GOOGLE_API_KEY is properly configured in .env")
        except FileNotFoundError:
            pytest.fail(".env file not found")
    
    def test_tracking_blocker_uses_bigmannentertainment(self):
        """Verify tracking blocker pattern uses bigmannentertainment.com"""
        index_path = "/app/frontend/public/index.html"
        try:
            with open(index_path, 'r') as f:
                content = f.read()
                assert 'bigmannentertainment.com' in content, "bigmannentertainment.com pattern not found"
                # Make sure old emergent.sh pattern is gone
                assert 'emergent.sh' not in content, "Old emergent.sh pattern still present"
                print("SUCCESS: Tracking blocker correctly uses bigmannentertainment.com pattern")
        except FileNotFoundError:
            pytest.fail("index.html file not found")


class TestNativeIntegrationFiles:
    """Verify native integration files exist and are properly structured"""
    
    def test_llm_service_exists(self):
        """Verify native LLM service file exists with correct structure"""
        llm_path = "/app/backend/llm_service.py"
        try:
            with open(llm_path, 'r') as f:
                content = f.read()
                # Check for expected classes
                assert 'class LlmChat' in content, "LlmChat class not found"
                assert 'class UserMessage' in content, "UserMessage class not found"
                assert 'google.generativeai' in content, "google-generativeai import not found"
                print("SUCCESS: llm_service.py has correct native Google Gemini structure")
        except FileNotFoundError:
            pytest.fail("llm_service.py not found")
    
    def test_stripe_native_service_exists(self):
        """Verify native Stripe service file exists with correct structure"""
        stripe_path = "/app/backend/stripe_native_service.py"
        try:
            with open(stripe_path, 'r') as f:
                content = f.read()
                # Check for expected classes
                assert 'class StripeCheckout' in content, "StripeCheckout class not found"
                assert 'class CheckoutSessionRequest' in content, "CheckoutSessionRequest not found"
                assert 'import stripe' in content, "stripe import not found"
                print("SUCCESS: stripe_native_service.py has correct native Stripe structure")
        except FileNotFoundError:
            pytest.fail("stripe_native_service.py not found")
    
    def test_services_import_from_llm_service(self):
        """Verify key services import from llm_service instead of emergentintegrations"""
        services_to_check = [
            "/app/backend/moderation_service.py",
            "/app/backend/enhanced_features_service.py",
            "/app/backend/ai_support_service.py",
            "/app/backend/modular_agency_workspace.py",
            "/app/backend/zero_trust_compliance_engine.py",
        ]
        
        for service_path in services_to_check:
            try:
                with open(service_path, 'r') as f:
                    content = f.read()
                    if 'LlmChat' in content or 'UserMessage' in content:
                        assert 'from llm_service import' in content, \
                            f"{service_path} should import from llm_service"
                        print(f"SUCCESS: {os.path.basename(service_path)} imports from llm_service")
            except FileNotFoundError:
                print(f"SKIP: {service_path} not found")
    
    def test_stripe_payment_service_imports_native(self):
        """Verify stripe_payment_service imports from stripe_native_service"""
        stripe_payment_path = "/app/backend/stripe_payment_service.py"
        try:
            with open(stripe_payment_path, 'r') as f:
                content = f.read()
                assert 'from stripe_native_service import' in content, \
                    "stripe_payment_service should import from stripe_native_service"
                print("SUCCESS: stripe_payment_service.py imports from stripe_native_service")
        except FileNotFoundError:
            pytest.fail("stripe_payment_service.py not found")


class TestFrontendBranding:
    """Verify frontend branding is correct"""
    
    def test_index_html_has_big_mann_branding(self):
        """Verify index.html has Big Mann Entertainment branding"""
        index_path = "/app/frontend/public/index.html"
        try:
            with open(index_path, 'r') as f:
                content = f.read()
                assert 'Big Mann Entertainment' in content, "Big Mann Entertainment not found in index.html"
                print("SUCCESS: index.html has Big Mann Entertainment branding")
        except FileNotFoundError:
            pytest.fail("index.html not found")
    
    def test_no_emergent_visible_text_in_index(self):
        """Verify no visible 'Emergent' text in index.html (excluding URLs)"""
        index_path = "/app/frontend/public/index.html"
        try:
            with open(index_path, 'r') as f:
                content = f.read()
                # Remove URL references for check
                content_no_urls = re.sub(r'https?://[^\s"\']+', '', content)
                # Check for standalone "Emergent" (not part of emergentagent.com URL)
                if re.search(r'\bEmergent\b', content_no_urls, re.IGNORECASE):
                    # Check if it's in a visible element (not just code comments)
                    pytest.fail("Found 'Emergent' text in index.html content")
                print("SUCCESS: No visible 'Emergent' text in index.html")
        except FileNotFoundError:
            pytest.fail("index.html not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
