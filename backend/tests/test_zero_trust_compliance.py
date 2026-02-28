"""
Zero-Trust Compliance Layer API Tests
=====================================
Tests for:
- Release Verification
- Identity Verification
- Usage Rights Validation
- Fraud Detection
- Privacy Compliance
- Audit Trail
- License Expiry
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestReleaseVerification:
    """Release Verification endpoint tests"""
    
    def test_verify_release_with_all_consents(self):
        """Test release verification with all consents provided"""
        release_id = f"TEST_release_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/verify-release/{release_id}?actor_id=test-user",
            json={
                "has_model_consent": True,
                "has_photographer_consent": True,
                "has_brand_clearance": True,
                "has_location_clearance": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "release_id" in data
        assert "status" in data
        assert "model_consent" in data
        assert "photographer_consent" in data
        assert "brand_clearance" in data
        assert "verification_date" in data
        assert "expiry_date" in data
        
        # Verify data values
        assert data["release_id"] == release_id
        assert data["status"] == "verified"
        assert data["model_consent"] == True
        assert data["photographer_consent"] == True
        assert data["brand_clearance"] == True
    
    def test_verify_release_missing_model_consent(self):
        """Test release verification without model consent"""
        release_id = f"TEST_release_no_model_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/verify-release/{release_id}?actor_id=test-user",
            json={
                "has_model_consent": False,
                "has_photographer_consent": True,
                "has_brand_clearance": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have issues when model consent is missing
        assert data["model_consent"] == False
        assert "issues" in data
        assert len(data["issues"]) > 0
    
    def test_verify_release_minor_without_guardian_consent(self):
        """Test release verification for minor without guardian consent"""
        release_id = f"TEST_release_minor_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/verify-release/{release_id}?actor_id=test-user",
            json={
                "has_model_consent": True,
                "has_photographer_consent": True,
                "is_minor": True,
                "has_guardian_consent": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should flag guardian consent issue for minors
        assert "issues" in data
        # Status should not be verified without guardian consent
        assert data["status"] in ["pending", "failed"]


class TestIdentityVerification:
    """Identity Verification endpoint tests"""
    
    def test_verify_identity_complete_data(self):
        """Test identity verification with complete data"""
        user_id = f"TEST_user_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/verify-identity/{user_id}?actor_id=test-user",
            json={
                "id_type": "passport",
                "id_number": "ABC123456",
                "date_of_birth": "1990-05-15",
                "id_document": True,
                "selfie": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "user_id" in data
        assert "verification_status" in data
        assert "id_type" in data
        assert "date_of_birth_verified" in data
        assert "age_verified" in data
        assert "is_minor" in data
        
        # Verify data values
        assert data["user_id"] == user_id
        assert data["verification_status"] == "verified"
        assert data["id_type"] == "passport"
        assert data["date_of_birth_verified"] == True
        assert data["is_minor"] == False  # 1990 DOB = adult
    
    def test_verify_identity_minor(self):
        """Test identity verification for a minor"""
        user_id = f"TEST_user_minor_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/verify-identity/{user_id}?actor_id=test-user",
            json={
                "id_type": "school_id",
                "id_number": "STUDENT123",
                "date_of_birth": "2015-01-01",  # Minor
                "id_document": True,
                "selfie": True,
                "guardian_consent": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_minor"] == True
        assert data["guardian_consent_if_minor"] == True
    
    def test_verify_identity_missing_documents(self):
        """Test identity verification with missing documents"""
        user_id = f"TEST_user_incomplete_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/verify-identity/{user_id}?actor_id=test-user",
            json={
                "id_type": "passport",
                "id_number": "ABC123",
                "date_of_birth": "1990-01-01",
                "id_document": False,
                "selfie": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should require resubmission without documents
        assert data["verification_status"] in ["pending", "requires_resubmission"]


class TestUsageRightsValidation:
    """Usage Rights Validation endpoint tests"""
    
    def test_validate_commercial_usage(self):
        """Test usage rights validation for commercial use"""
        asset_id = f"TEST_asset_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/validate-usage-rights/{asset_id}?actor_id=test-user",
            json={
                "use_type": "commercial",
                "territory": "worldwide",
                "duration_days": 365,
                "exclusive": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "asset_id" in data
        assert "status" in data
        assert "allowed_uses" in data
        assert "restricted_uses" in data
        assert "territories" in data
        assert "duration_days" in data
        
        # Verify data values
        assert data["asset_id"] == asset_id
        assert data["status"] == "compliant"
        assert isinstance(data["allowed_uses"], list)
        assert len(data["allowed_uses"]) > 0
    
    def test_validate_exclusive_worldwide_usage(self):
        """Test usage rights for exclusive worldwide - should require action"""
        asset_id = f"TEST_asset_exclusive_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/validate-usage-rights/{asset_id}?actor_id=test-user",
            json={
                "use_type": "advertising",
                "territory": "worldwide",
                "duration_days": 365,
                "exclusive": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Exclusive worldwide should require action
        assert data["status"] == "requires_action"
        assert data["exclusivity"] == True
    
    def test_validate_long_duration_usage(self):
        """Test usage rights for long duration - should require review"""
        asset_id = f"TEST_asset_long_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/validate-usage-rights/{asset_id}?actor_id=test-user",
            json={
                "use_type": "editorial",
                "territory": "north_america",
                "duration_days": 1000,  # >2 years
                "exclusive": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Long duration should require review
        assert data["status"] == "pending_review"


class TestFraudDetection:
    """Fraud Detection endpoint tests"""
    
    def test_detect_fraud_clean_upload(self):
        """Test fraud detection for a clean upload"""
        upload_id = f"TEST_upload_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/detect-fraud/{upload_id}?actor_id=test-user",
            json={
                "file_name": "test_photo.jpg",
                "file_hash": f"hash_{datetime.now().timestamp()}",
                "file_size": 1024000,
                "uploader_id": "user-001",
                "upload_source": "web"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "upload_id" in data
        assert "risk_level" in data
        assert "is_duplicate" in data
        assert "flags" in data
        assert "recommended_action" in data
        
        # Verify data values
        assert data["upload_id"] == upload_id
        assert data["risk_level"] in ["none", "low", "medium", "high", "critical"]
        assert data["is_duplicate"] == False
    
    def test_detect_fraud_zero_size_file(self):
        """Test fraud detection for zero-size file"""
        upload_id = f"TEST_upload_zero_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/detect-fraud/{upload_id}?actor_id=test-user",
            json={
                "file_name": "empty.jpg",
                "file_hash": "empty_hash",
                "file_size": 0,
                "uploader_id": "user-001",
                "upload_source": "web"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Zero-size file should be flagged
        assert data["risk_level"] in ["medium", "high"]
        assert len(data["flags"]) > 0
    
    def test_detect_fraud_api_upload(self):
        """Test fraud detection for API upload source"""
        upload_id = f"TEST_upload_api_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/detect-fraud/{upload_id}?actor_id=test-user",
            json={
                "file_name": "bulk_upload.jpg",
                "file_hash": f"api_hash_{datetime.now().timestamp()}",
                "file_size": 2048000,
                "uploader_id": "api-user",
                "upload_source": "api"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # API uploads should be flagged for verification
        assert "flags" in data
        # Should have a flag about automated upload


class TestPrivacyCompliance:
    """Privacy Compliance endpoint tests"""
    
    def test_check_privacy_gdpr_compliant(self):
        """Test privacy compliance check for GDPR compliant entity"""
        entity_id = f"TEST_entity_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/check-privacy/{entity_id}?actor_id=test-user&entity_type=user&regions=EU",
            json={
                "name": "Test User",
                "consent_collected": True,
                "right_to_erasure_supported": True,
                "data_portability_supported": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "entity_id" in data
        assert "entity_type" in data
        assert "status" in data
        assert "gdpr_compliant" in data
        assert "regulations_checked" in data
        
        # Verify data values
        assert data["entity_id"] == entity_id
        assert data["entity_type"] == "user"
        assert data["gdpr_compliant"] == True
        assert "gdpr" in data["regulations_checked"]
    
    def test_check_privacy_ccpa_region(self):
        """Test privacy compliance check for California (CCPA)"""
        entity_id = f"TEST_entity_ccpa_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/check-privacy/{entity_id}?actor_id=test-user&entity_type=user&regions=US-CA",
            json={
                "name": "California User",
                "consent_collected": True,
                "right_to_erasure_supported": True,
                "data_portability_supported": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["ccpa_compliant"] == True
        assert "ccpa" in data["regulations_checked"]
    
    def test_check_privacy_multiple_regions(self):
        """Test privacy compliance check for multiple regions"""
        entity_id = f"TEST_entity_multi_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/check-privacy/{entity_id}?actor_id=test-user&entity_type=user&regions=EU&regions=US-CA&regions=Brazil",
            json={
                "name": "Global User",
                "consent_collected": True,
                "right_to_erasure_supported": True,
                "data_portability_supported": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should check multiple regulations
        assert len(data["regulations_checked"]) >= 2
    
    def test_check_privacy_non_compliant(self):
        """Test privacy compliance check for non-compliant entity"""
        entity_id = f"TEST_entity_noncompliant_{datetime.now().timestamp()}"
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/check-privacy/{entity_id}?actor_id=test-user&entity_type=user&regions=EU",
            json={
                "name": "Non-Compliant User",
                "consent_collected": False,
                "right_to_erasure_supported": False,
                "data_portability_supported": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have issues and remediation steps
        assert data["status"] in ["non_compliant", "requires_action"]
        assert len(data["issues"]) > 0
        assert len(data["remediation_steps"]) > 0


class TestAuditTrail:
    """Audit Trail endpoint tests"""
    
    def test_get_audit_trail(self):
        """Test retrieving audit trail"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/compliance/audit-trail?limit=10"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # If there are entries, verify structure
        if len(data) > 0:
            entry = data[0]
            assert "log_id" in entry
            assert "timestamp" in entry
            assert "action_type" in entry
            assert "entity_type" in entry
            assert "entity_id" in entry
            assert "actor_id" in entry
    
    def test_get_audit_trail_compliance_only(self):
        """Test retrieving compliance-only audit trail"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/compliance/audit-trail?compliance_only=true&limit=10"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        # All entries should be compliance relevant
        for entry in data:
            assert entry.get("compliance_relevant", True) == True


class TestLicenseExpiry:
    """License Expiry endpoint tests"""
    
    def test_get_expiring_licenses(self):
        """Test retrieving expiring licenses"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/compliance/expiring-licenses?days_ahead=30"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # If there are entries, verify structure
        if len(data) > 0:
            entry = data[0]
            assert "license_id" in entry
            assert "expiry_date" in entry
            assert "days_until_expiry" in entry
    
    def test_auto_expire_licenses(self):
        """Test auto-expire licenses endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/enterprise/compliance/auto-expire-licenses"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return expired count
        assert "expired_count" in data
        assert isinstance(data["expired_count"], int)


class TestAuditChainIntegrity:
    """Audit Chain Integrity tests"""
    
    def test_verify_audit_chain(self):
        """Test audit chain integrity verification"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/compliance/verify-audit-chain"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "valid" in data
        assert "entries_checked" in data


# Fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_base_url():
    """Ensure BASE_URL is set"""
    global BASE_URL
    if not BASE_URL:
        BASE_URL = "http://localhost:8001"
    print(f"Testing against: {BASE_URL}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
