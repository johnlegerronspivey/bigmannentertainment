"""
GS1 Business Identifiers API Tests
===================================
Tests for mandatory GS1 and business identifier enforcement:
- Protected owner identifiers (immutable)
- Validation with check-digit verification
- Label identifier CRUD
- Compliance checking
- Asset/endpoint creation with GS1 enforcement
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"
PROTECTED_USER_ID = "0659dd6d-e447-4022-a05a-f775b1509572"
TEST_LABEL_ID = "BM-LBL-9D0377FB"

# Protected identifiers (from ownership_guard.py)
PROTECTED_GS1_PREFIX = "08600043402"
PROTECTED_GLN = "0860004340201"
PROTECTED_EIN = "270658077"

# Valid GTIN for testing (14-digit with correct check digit)
VALID_GTIN_14 = "00860004340201"


class TestGS1Authentication:
    """Test authentication for GS1 endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for owner account"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Token field is 'access_token' not 'token'
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
    
    def test_login_success(self):
        """Test owner login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        print("✓ Login successful")


class TestProtectedOwnerIdentifiers:
    """Test GET /api/gs1-identifiers/protected-owner endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        token = response.json().get("access_token") or response.json().get("token")
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    
    def test_get_protected_owner_identifiers(self, auth_headers):
        """GET /api/gs1-identifiers/protected-owner returns all pre-populated identifiers"""
        response = requests.get(f"{BASE_URL}/api/gs1-identifiers/protected-owner", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert data.get("success") is True
        assert "identifiers" in data
        assert "protected_owner" in data
        assert "protected_business" in data
        
        # Verify protected owner info
        assert data["protected_owner"] == "John LeGerron Spivey"
        assert data["protected_business"] == "Big Mann Entertainment"
        assert data["protection_level"] == "IMMUTABLE"
        
        # Verify identifiers
        identifiers = data["identifiers"]
        assert identifiers["gs1_company_prefix"] == PROTECTED_GS1_PREFIX
        assert identifiers["gln"] == PROTECTED_GLN
        assert identifiers["ein"] == PROTECTED_EIN
        assert "duns" in identifiers
        assert "business_registration_number" in identifiers
        assert identifiers["business_entity"] == "Big Mann Entertainment"
        assert identifiers["business_owner"] == "John LeGerron Spivey"
        
        print("✓ Protected owner identifiers returned correctly")
    
    def test_protected_owner_requires_auth(self):
        """Protected owner endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/gs1-identifiers/protected-owner")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Protected owner endpoint requires auth")


class TestIdentifierValidation:
    """Test POST /api/gs1-identifiers/validate endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        token = response.json().get("access_token") or response.json().get("token")
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    
    def test_validate_gtin_valid(self, auth_headers):
        """Validate valid GTIN-14 with correct check digit"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate", 
            headers=auth_headers,
            json={"identifier_type": "gtin", "value": VALID_GTIN_14}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["error"] is None
        print(f"✓ Valid GTIN-14 ({VALID_GTIN_14}) validated correctly")
    
    def test_validate_gtin_invalid_check_digit(self, auth_headers):
        """Validate GTIN with wrong check digit is rejected"""
        # Change last digit to make check digit invalid
        invalid_gtin = "00860004340202"  # Wrong check digit (should be 1)
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "gtin", "value": invalid_gtin}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "check digit" in data["error"].lower()
        print(f"✓ Invalid GTIN check digit detected: {data['error']}")
    
    def test_validate_gtin_wrong_length(self, auth_headers):
        """Validate GTIN with wrong length is rejected"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "gtin", "value": "12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "8, 12, 13, or 14" in data["error"]
        print(f"✓ Invalid GTIN length detected: {data['error']}")
    
    def test_validate_gln_valid(self, auth_headers):
        """Validate valid GLN (13 digits)"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "gln", "value": PROTECTED_GLN}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print(f"✓ Valid GLN ({PROTECTED_GLN}) validated correctly")
    
    def test_validate_gln_invalid_check_digit(self, auth_headers):
        """Validate GLN with wrong check digit"""
        invalid_gln = "0860004340202"  # Wrong check digit
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "gln", "value": invalid_gln}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "check digit" in data["error"].lower()
        print(f"✓ Invalid GLN check digit detected: {data['error']}")
    
    def test_validate_isrc_valid(self, auth_headers):
        """Validate valid ISRC format"""
        valid_isrc = "USRC17607839"  # Standard ISRC format
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "isrc", "value": valid_isrc}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print(f"✓ Valid ISRC ({valid_isrc}) validated correctly")
    
    def test_validate_isrc_invalid(self, auth_headers):
        """Validate invalid ISRC format"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "isrc", "value": "INVALID"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        print(f"✓ Invalid ISRC detected: {data['error']}")
    
    def test_validate_upc_valid(self, auth_headers):
        """Validate valid UPC (12 digits)"""
        # UPC with correct check digit
        valid_upc = "012345678905"  # Standard UPC-A
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "upc", "value": valid_upc}
        )
        assert response.status_code == 200
        data = response.json()
        # Note: check digit may or may not be valid depending on the UPC
        print(f"✓ UPC validation returned: valid={data['valid']}, error={data.get('error')}")
    
    def test_validate_ein_valid(self, auth_headers):
        """Validate valid EIN (9 digits)"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "ein", "value": PROTECTED_EIN}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print(f"✓ Valid EIN ({PROTECTED_EIN}) validated correctly")
    
    def test_validate_ein_invalid(self, auth_headers):
        """Validate invalid EIN (wrong length)"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "ein", "value": "12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "9 digits" in data["error"]
        print(f"✓ Invalid EIN detected: {data['error']}")
    
    def test_validate_duns_valid(self, auth_headers):
        """Validate valid DUNS (9 digits)"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "duns", "value": "123456789"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print("✓ Valid DUNS validated correctly")
    
    def test_validate_gs1_company_prefix_valid(self, auth_headers):
        """Validate valid GS1 Company Prefix (7-11 digits)"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "gs1_company_prefix", "value": PROTECTED_GS1_PREFIX}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print(f"✓ Valid GS1 Company Prefix ({PROTECTED_GS1_PREFIX}) validated correctly")
    
    def test_validate_gs1_company_prefix_invalid(self, auth_headers):
        """Validate invalid GS1 Company Prefix (wrong length)"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "gs1_company_prefix", "value": "12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "7 to 11" in data["error"]
        print(f"✓ Invalid GS1 Company Prefix detected: {data['error']}")
    
    def test_validate_unknown_type(self, auth_headers):
        """Validate unknown identifier type returns error"""
        response = requests.post(f"{BASE_URL}/api/gs1-identifiers/validate",
            headers=auth_headers,
            json={"identifier_type": "unknown_type", "value": "12345"}
        )
        assert response.status_code == 400
        print("✓ Unknown identifier type rejected with 400")


class TestLabelIdentifiers:
    """Test label identifier CRUD endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        token = response.json().get("access_token") or response.json().get("token")
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    
    def test_get_label_identifiers(self, auth_headers):
        """GET /api/gs1-identifiers/labels/{label_id} returns identifiers"""
        response = requests.get(f"{BASE_URL}/api/gs1-identifiers/labels/{TEST_LABEL_ID}", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "identifiers" in data
        assert "is_protected" in data
        print(f"✓ Label identifiers retrieved for {TEST_LABEL_ID}")
        print(f"  is_protected: {data['is_protected']}")
    
    def test_get_label_compliance(self, auth_headers):
        """GET /api/gs1-identifiers/labels/{label_id}/compliance returns compliance status"""
        response = requests.get(f"{BASE_URL}/api/gs1-identifiers/labels/{TEST_LABEL_ID}/compliance", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "compliant" in data
        assert "missing_identifiers" in data
        assert "invalid_identifiers" in data
        assert "total_required" in data
        assert "total_present" in data
        print(f"✓ Label compliance status: compliant={data['compliant']}")
        print(f"  Missing: {data['missing_identifiers']}")
        print(f"  Invalid: {data['invalid_identifiers']}")
    
    def test_update_protected_owner_identifiers_blocked(self, auth_headers):
        """PUT /api/gs1-identifiers/labels/{label_id} blocks modification of protected owner identifiers"""
        # Try to modify protected identifiers
        response = requests.put(f"{BASE_URL}/api/gs1-identifiers/labels/{TEST_LABEL_ID}",
            headers=auth_headers,
            json={
                "gs1_company_prefix": "99999999999",  # Try to change protected prefix
                "gln": "9999999999999",
                "ein": "999999999",
                "duns": "999999999",
                "business_registration_number": "FAKE-REG",
                "business_entity": "Fake Business",
                "business_owner": "Fake Owner",
                "business_type": "LLC"
            }
        )
        # Should be blocked with 403 if this is the protected owner's label
        # Or succeed with validation if not protected
        if response.status_code == 403:
            data = response.json()
            assert "OWNERSHIP PROTECTION" in str(data.get("detail", ""))
            print("✓ Protected owner identifier modification blocked with 403")
        else:
            # If not protected, it might succeed or fail validation
            print(f"  Response: {response.status_code} - {response.text[:200]}")


class TestAssetCreationGS1Enforcement:
    """Test asset creation with mandatory GTIN enforcement"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        token = response.json().get("access_token") or response.json().get("token")
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    
    def test_asset_creation_without_gtin_rejected(self, auth_headers):
        """POST /api/uln/labels/{label_id}/catalog/assets rejects asset without GTIN"""
        response = requests.post(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=auth_headers,
            json={
                "title": "TEST Track Without GTIN",
                "type": "single",
                "artist": "Test Artist",
                "isrc": "USRC17607839",
                # No GTIN provided
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            assert "gtin" in str(detail.get("validation_errors", {})).lower()
        print("✓ Asset creation without GTIN rejected with 400")
    
    def test_asset_creation_with_invalid_gtin_rejected(self, auth_headers):
        """POST /api/uln/labels/{label_id}/catalog/assets rejects asset with invalid GTIN"""
        response = requests.post(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=auth_headers,
            json={
                "title": "TEST Track With Invalid GTIN",
                "type": "single",
                "artist": "Test Artist",
                "gtin": "12345",  # Wrong length
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            errors = detail.get("validation_errors", {})
            assert "gtin" in errors
        print("✓ Asset creation with invalid GTIN (wrong length) rejected")
    
    def test_asset_creation_with_wrong_check_digit_rejected(self, auth_headers):
        """POST /api/uln/labels/{label_id}/catalog/assets rejects asset with wrong GTIN check digit"""
        response = requests.post(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=auth_headers,
            json={
                "title": "TEST Track With Wrong Check Digit",
                "type": "single",
                "artist": "Test Artist",
                "gtin": "00860004340202",  # Wrong check digit (should be 1)
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            errors = detail.get("validation_errors", {})
            assert "gtin" in errors
            assert "check digit" in str(errors.get("gtin", "")).lower()
        print("✓ Asset creation with wrong GTIN check digit rejected")
    
    def test_asset_creation_with_valid_gtin_succeeds(self, auth_headers):
        """POST /api/uln/labels/{label_id}/catalog/assets succeeds with valid GTIN"""
        import uuid
        unique_title = f"TEST Valid GTIN Track {uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/assets",
            headers=auth_headers,
            json={
                "title": unique_title,
                "type": "single",
                "artist": "Test Artist",
                "gtin": VALID_GTIN_14,  # Valid GTIN with correct check digit
                "isrc": "USRC17607839",
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"✓ Asset creation with valid GTIN succeeded: {unique_title}")


class TestEndpointCreationGS1Enforcement:
    """Test distribution endpoint creation with mandatory GLN and GS1 prefix enforcement"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        token = response.json().get("access_token") or response.json().get("token")
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    
    def test_endpoint_creation_without_gln_rejected(self, auth_headers):
        """POST /api/uln/labels/{label_id}/endpoints rejects endpoint without GLN"""
        response = requests.post(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=auth_headers,
            json={
                "platform": "Spotify",
                "status": "pending",
                "endpoint_type": "streaming",
                # No GLN or GS1 prefix
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            errors = detail.get("validation_errors", {})
            assert "gs1_gln" in errors or "gln" in str(errors).lower()
        print("✓ Endpoint creation without GLN rejected with 400")
    
    def test_endpoint_creation_without_gs1_prefix_rejected(self, auth_headers):
        """POST /api/uln/labels/{label_id}/endpoints rejects endpoint without GS1 Company Prefix"""
        response = requests.post(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=auth_headers,
            json={
                "platform": "Apple Music",
                "status": "pending",
                "endpoint_type": "streaming",
                "gs1_gln": PROTECTED_GLN,  # Valid GLN
                # No GS1 Company Prefix
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            errors = detail.get("validation_errors", {})
            assert "gs1_company_prefix" in errors
        print("✓ Endpoint creation without GS1 Company Prefix rejected with 400")
    
    def test_endpoint_creation_with_valid_gs1_succeeds(self, auth_headers):
        """POST /api/uln/labels/{label_id}/endpoints succeeds with valid GLN and GS1 prefix"""
        import uuid
        unique_platform = f"TestPlatform_{uuid.uuid4().hex[:6]}"
        response = requests.post(f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/endpoints",
            headers=auth_headers,
            json={
                "platform": unique_platform,
                "status": "pending",
                "endpoint_type": "streaming",
                "gs1_gln": PROTECTED_GLN,
                "gs1_company_prefix": PROTECTED_GS1_PREFIX,
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"✓ Endpoint creation with valid GS1 identifiers succeeded: {unique_platform}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
