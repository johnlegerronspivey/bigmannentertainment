#!/usr/bin/env python3
"""
Final Verification Test for Metadata Parser & Validator Implementation
Big Mann Entertainment Platform - Phase 1 Complete System Testing

This test suite verifies the complete Metadata Parser & Validator system
to confirm 90%+ success rate as requested in the review.

Test Coverage:
1. Authentication & Setup
2. GET /api/metadata/formats/supported
3. POST /api/metadata/validate-json with sample metadata
4. POST /api/metadata/parse with JSON metadata file
5. GET /api/metadata/duplicates/check for ISRC and UPC
6. POST /api/metadata/upload with metadata file
7. GET /api/metadata/statistics
8. GET /api/metadata/validation-results

Expected Outcome: 90%+ success rate confirming production readiness
"""

import requests
import json
import time
import os
import tempfile
from datetime import datetime
import xml.etree.ElementTree as ET

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://metadata-maestro-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user credentials for metadata testing
TEST_USER = {
    "email": "metadata.final.test@bigmannentertainment.com",
    "password": "MetadataFinal2025!",
    "full_name": "Metadata Final Test User",
    "business_name": "Metadata Final Testing LLC",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "address_line1": "123 Final Test Street",
    "city": "Test City",
    "state_province": "Test State",
    "postal_code": "12345",
    "country": "United States"
}

class MetadataFinalVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.critical_failures = []
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results with detailed tracking"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if not success:
            self.critical_failures.append(result)
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def setup_authentication(self):
        """Setup authentication for metadata testing"""
        print("🔐 Setting up authentication for Metadata Parser & Validator testing...")
        
        # Try to register user (may fail if already exists)
        try:
            register_response = self.session.post(
                f"{API_BASE}/auth/register",
                json=TEST_USER
            )
            if register_response.status_code in [200, 201]:
                print("✅ User registered successfully")
            elif register_response.status_code == 400:
                print("ℹ️ User already exists, proceeding with login")
        except Exception as e:
            print(f"⚠️ Registration attempt: {str(e)}")

        # Login to get token
        try:
            login_response = self.session.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.auth_token = login_data.get("access_token")
                self.user_id = login_data.get("user", {}).get("id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                self.log_test(
                    "Authentication & Setup",
                    True,
                    f"Successfully authenticated user: {TEST_USER['email']}"
                )
                return True
            else:
                self.log_test(
                    "Authentication & Setup",
                    False,
                    error_msg=f"Login failed: {login_response.status_code} - {login_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication & Setup",
                False,
                error_msg=f"Authentication error: {str(e)}"
            )
            return False

    def test_supported_formats_endpoint(self):
        """Test GET /api/metadata/formats/supported endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/metadata/formats/supported")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if data.get("success") and "supported_formats" in data:
                    formats = data["supported_formats"]
                    
                    # Check for required formats
                    required_formats = ["ddex_ern", "mead", "json", "csv"]
                    missing_formats = [fmt for fmt in required_formats if fmt not in formats]
                    
                    if not missing_formats:
                        # Check validation features
                        validation_features = data.get("validation_features", {})
                        
                        self.log_test(
                            "Supported Formats Endpoint",
                            True,
                            f"All required formats supported: {list(formats.keys())}, Validation features: {list(validation_features.keys())}"
                        )
                    else:
                        self.log_test(
                            "Supported Formats Endpoint",
                            False,
                            error_msg=f"Missing formats: {missing_formats}"
                        )
                else:
                    self.log_test(
                        "Supported Formats Endpoint",
                        False,
                        error_msg="Invalid response structure"
                    )
            else:
                self.log_test(
                    "Supported Formats Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Supported Formats Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_json_validation_endpoint(self):
        """Test POST /api/metadata/validate-json with sample metadata"""
        try:
            # Test with comprehensive valid JSON metadata
            sample_metadata = {
                "title": "Final Test Track",
                "artist": "Final Test Artist",
                "album": "Final Test Album",
                "isrc": "USRC17607850",
                "upc": "123456789050",
                "release_date": "2025-01-15T00:00:00Z",
                "rights_holders": ["Big Mann Entertainment", "Final Test Publishing"],
                "publisher_name": "Final Test Publishing",
                "composer_name": "Final Test Composer",
                "copyright_year": 2025,
                "genre": "Hip-Hop",
                "duration": "3:45",
                "description": "Final verification test track for metadata validation",
                "tags": ["hip-hop", "test", "metadata", "final"]
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/validate-json",
                json={
                    "metadata_json": sample_metadata,
                    "check_duplicates": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    validation_status = result.get("validation_status")
                    validation_errors = result.get("validation_errors", [])
                    duplicates_found = result.get("duplicates_found", 0)
                    
                    self.log_test(
                        "JSON Validation Endpoint",
                        True,
                        f"Validation status: {validation_status}, Errors: {len(validation_errors)}, Duplicates: {duplicates_found}"
                    )
                else:
                    self.log_test(
                        "JSON Validation Endpoint",
                        False,
                        error_msg=f"Validation failed: {result.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "JSON Validation Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "JSON Validation Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_file_parsing_endpoint(self):
        """Test POST /api/metadata/parse with JSON metadata file"""
        try:
            # Create sample JSON metadata file
            sample_metadata = {
                "title": "File Parse Test Track",
                "artist": "File Parse Test Artist",
                "album": "File Parse Test Album",
                "isrc": "USRC17607851",
                "upc": "123456789051",
                "release_date": "2025-01-15T00:00:00Z",
                "rights_holders": ["Big Mann Entertainment"],
                "genre": "Hip-Hop",
                "duration": "4:12"
            }
            
            # Create temporary file
            json_content = json.dumps(sample_metadata).encode('utf-8')
            
            # Prepare multipart form data
            files = {
                'file': ('test_metadata.json', json_content, 'application/json')
            }
            data = {
                'format': 'json',
                'validate': 'true',
                'check_duplicates': 'true'
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/parse",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    parsed_metadata = result.get("parsed_metadata", {})
                    validation_status = result.get("validation_status")
                    validation_id = result.get("validation_id")
                    
                    # Check if metadata was parsed correctly
                    if parsed_metadata.get("title") == sample_metadata["title"]:
                        self.log_test(
                            "File Parsing Endpoint",
                            True,
                            f"Successfully parsed: {parsed_metadata.get('title')} by {parsed_metadata.get('artist')}, Status: {validation_status}, ID: {validation_id}"
                        )
                    else:
                        self.log_test(
                            "File Parsing Endpoint",
                            False,
                            error_msg="Parsed metadata doesn't match input"
                        )
                else:
                    self.log_test(
                        "File Parsing Endpoint",
                        False,
                        error_msg=f"Parse failed: {result.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "File Parsing Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "File Parsing Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_duplicate_detection_endpoint(self):
        """Test GET /api/metadata/duplicates/check for ISRC and UPC"""
        try:
            # Test ISRC duplicate check
            test_isrc = "USRC17607850"  # From our JSON validation test
            
            response = self.session.get(
                f"{API_BASE}/metadata/duplicates/check",
                params={
                    "identifier_type": "isrc",
                    "identifier_value": test_isrc
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    duplicates_found = result.get("duplicates_found", 0)
                    
                    self.log_test(
                        "ISRC Duplicate Detection",
                        True,
                        f"Checked ISRC {test_isrc}, Found {duplicates_found} duplicates"
                    )
                else:
                    self.log_test(
                        "ISRC Duplicate Detection",
                        False,
                        error_msg="ISRC duplicate check failed"
                    )
            else:
                self.log_test(
                    "ISRC Duplicate Detection",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
            
            # Test UPC duplicate check
            test_upc = "123456789050"  # From our JSON validation test
            
            response = self.session.get(
                f"{API_BASE}/metadata/duplicates/check",
                params={
                    "identifier_type": "upc",
                    "identifier_value": test_upc
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    duplicates_found = result.get("duplicates_found", 0)
                    
                    self.log_test(
                        "UPC Duplicate Detection",
                        True,
                        f"Checked UPC {test_upc}, Found {duplicates_found} duplicates"
                    )
                else:
                    self.log_test(
                        "UPC Duplicate Detection",
                        False,
                        error_msg="UPC duplicate check failed"
                    )
            else:
                self.log_test(
                    "UPC Duplicate Detection",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Duplicate Detection Endpoints",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_integrated_upload_endpoint(self):
        """Test POST /api/metadata/upload with metadata file (if exists)"""
        try:
            # Check if integrated upload endpoint exists
            # This might be part of the regular media upload with metadata
            
            # First try the metadata upload endpoint
            sample_metadata = {
                "title": "Integrated Upload Test",
                "artist": "Upload Test Artist",
                "album": "Upload Test Album",
                "isrc": "USRC17607852",
                "upc": "123456789052",
                "release_date": "2025-01-15T00:00:00Z",
                "rights_holders": ["Big Mann Entertainment"],
                "genre": "Hip-Hop"
            }
            
            json_content = json.dumps(sample_metadata).encode('utf-8')
            
            # Try metadata upload endpoint
            files = {
                'file': ('upload_test.json', json_content, 'application/json')
            }
            data = {
                'format': 'json',
                'validate': 'true',
                'check_duplicates': 'true'
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/upload",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test(
                        "Integrated Upload Endpoint",
                        True,
                        f"Successfully uploaded metadata file"
                    )
                else:
                    self.log_test(
                        "Integrated Upload Endpoint",
                        False,
                        error_msg=f"Upload failed: {result.get('message', 'Unknown error')}"
                    )
            elif response.status_code == 404:
                # Endpoint doesn't exist, try alternative approach
                self.log_test(
                    "Integrated Upload Endpoint",
                    False,
                    error_msg="Metadata upload endpoint not found (404) - may use regular media upload with metadata"
                )
            else:
                self.log_test(
                    "Integrated Upload Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Integrated Upload Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_user_statistics_endpoint(self):
        """Test GET /api/metadata/statistics"""
        try:
            response = self.session.get(f"{API_BASE}/metadata/statistics")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    stats = result.get("statistics", {})
                    
                    total_validations = stats.get("total_validations", 0)
                    success_rate = stats.get("success_rate", 0)
                    format_distribution = stats.get("format_distribution", {})
                    validation_status = stats.get("validation_status", {})
                    
                    self.log_test(
                        "User Statistics Endpoint",
                        True,
                        f"Total validations: {total_validations}, Success rate: {success_rate}%, Formats: {list(format_distribution.keys())}, Status distribution: {validation_status}"
                    )
                else:
                    self.log_test(
                        "User Statistics Endpoint",
                        False,
                        error_msg="Failed to retrieve statistics"
                    )
            else:
                self.log_test(
                    "User Statistics Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "User Statistics Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_validation_results_endpoint(self):
        """Test GET /api/metadata/validation-results"""
        try:
            # Test list validation results
            response = self.session.get(f"{API_BASE}/metadata/validation-results")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    results = result.get("validation_results", [])
                    total_count = result.get("total_count", 0)
                    
                    self.log_test(
                        "Validation Results Endpoint",
                        True,
                        f"Retrieved {len(results)} results, Total: {total_count}"
                    )
                    
                    # Test individual result retrieval if we have results
                    if results:
                        first_result_id = results[0].get("id")
                        if first_result_id:
                            detail_response = self.session.get(
                                f"{API_BASE}/metadata/validation-results/{first_result_id}"
                            )
                            
                            if detail_response.status_code == 200:
                                detail_result = detail_response.json()
                                if detail_result.get("success"):
                                    self.log_test(
                                        "Individual Validation Result",
                                        True,
                                        f"Retrieved result details for ID: {first_result_id}"
                                    )
                                else:
                                    self.log_test(
                                        "Individual Validation Result",
                                        False,
                                        error_msg="Failed to get result details"
                                    )
                            else:
                                self.log_test(
                                    "Individual Validation Result",
                                    False,
                                    error_msg=f"HTTP {detail_response.status_code}"
                                )
                else:
                    self.log_test(
                        "Validation Results Endpoint",
                        False,
                        error_msg="Failed to retrieve results"
                    )
            else:
                self.log_test(
                    "Validation Results Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Validation Results Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_error_handling_and_validation_logic(self):
        """Test comprehensive validation logic and error handling"""
        try:
            # Test with invalid metadata to verify validation logic
            invalid_metadata = {
                "title": "",  # Empty required field
                "artist": "Test Artist",
                "isrc": "INVALID-ISRC-FORMAT",  # Invalid ISRC format
                "upc": "12345",  # Too short UPC
                "release_date": "invalid-date-format",  # Invalid date
                "rights_holders": [],  # Empty required array
                "copyright_year": 2050  # Future year (should trigger warning)
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/validate-json",
                json={
                    "metadata_json": invalid_metadata,
                    "check_duplicates": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                validation_errors = result.get("validation_errors", [])
                validation_status = result.get("validation_status")
                
                # Should have validation errors for invalid data
                if validation_errors and validation_status in ["error", "warning"]:
                    error_fields = [error.get("field") for error in validation_errors]
                    
                    self.log_test(
                        "Validation Logic & Error Handling",
                        True,
                        f"Correctly detected {len(validation_errors)} validation errors in fields: {error_fields}"
                    )
                else:
                    self.log_test(
                        "Validation Logic & Error Handling",
                        False,
                        error_msg=f"Expected validation errors but got status: {validation_status}, errors: {len(validation_errors)}"
                    )
            else:
                self.log_test(
                    "Validation Logic & Error Handling",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Validation Logic & Error Handling",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def run_final_verification_tests(self):
        """Run complete final verification test suite"""
        print("🎯 STARTING FINAL VERIFICATION TEST FOR METADATA PARSER & VALIDATOR")
        print("=" * 80)
        print("Target: 90%+ success rate to confirm production readiness")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        print("\n📋 TESTING CORE METADATA ENDPOINTS...")
        print("-" * 60)
        
        # Core endpoint tests as specified in review request
        self.test_supported_formats_endpoint()
        self.test_json_validation_endpoint()
        self.test_file_parsing_endpoint()
        self.test_duplicate_detection_endpoint()
        self.test_integrated_upload_endpoint()
        self.test_user_statistics_endpoint()
        self.test_validation_results_endpoint()
        
        print("\n🔍 TESTING VALIDATION LOGIC & ERROR HANDLING...")
        print("-" * 60)
        
        # Validation logic tests
        self.test_error_handling_and_validation_logic()
        
        # Generate final summary
        self.generate_final_verification_summary()

    def generate_final_verification_summary(self):
        """Generate comprehensive final verification summary"""
        print("\n" + "=" * 80)
        print("📊 METADATA PARSER & VALIDATOR FINAL VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 FINAL VERIFICATION RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Success rate evaluation
        if success_rate >= 90:
            print(f"\n🎉 SUCCESS: {success_rate:.1f}% success rate EXCEEDS 90% target!")
            print("✅ Metadata Parser & Validator is PRODUCTION READY")
        elif success_rate >= 75:
            print(f"\n⚠️ PARTIAL SUCCESS: {success_rate:.1f}% success rate below 90% target")
            print("⚠️ Some issues need attention before full production deployment")
        else:
            print(f"\n❌ FAILURE: {success_rate:.1f}% success rate significantly below 90% target")
            print("❌ Major fixes required before production deployment")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {result['test']}")
            if result["error"]:
                print(f"      Error: {result['error']}")
        
        # Critical failures analysis
        if self.critical_failures:
            print(f"\n⚠️ CRITICAL ISSUES REQUIRING ATTENTION:")
            for failure in self.critical_failures:
                print(f"   ❌ {failure['test']}: {failure['error']}")
        
        # Production readiness assessment
        print(f"\n💡 PRODUCTION READINESS ASSESSMENT:")
        
        core_endpoints_passed = len([r for r in self.test_results if r["success"] and 
                                   any(keyword in r["test"].lower() for keyword in 
                                       ["supported formats", "json validation", "file parsing", 
                                        "duplicate detection", "statistics", "validation results"])])
        
        core_endpoints_total = len([r for r in self.test_results if 
                                  any(keyword in r["test"].lower() for keyword in 
                                      ["supported formats", "json validation", "file parsing", 
                                       "duplicate detection", "statistics", "validation results"])])
        
        core_success_rate = (core_endpoints_passed / core_endpoints_total * 100) if core_endpoints_total > 0 else 0
        
        print(f"   Core Endpoints: {core_endpoints_passed}/{core_endpoints_total} passed ({core_success_rate:.1f}%)")
        
        if core_success_rate >= 90:
            print("   ✅ Core functionality is working excellently")
        elif core_success_rate >= 75:
            print("   ⚠️ Core functionality mostly working with minor issues")
        else:
            print("   ❌ Core functionality has significant issues")
        
        # Final recommendation
        print(f"\n🎯 FINAL RECOMMENDATION:")
        if success_rate >= 90 and core_success_rate >= 90:
            print("   ✅ APPROVED FOR PRODUCTION: Metadata Parser & Validator system is ready")
            print("   ✅ All critical functionality working with 90%+ success rate achieved")
        elif success_rate >= 75:
            print("   ⚠️ CONDITIONAL APPROVAL: System mostly working but needs minor fixes")
            print("   ⚠️ Address critical issues before full production deployment")
        else:
            print("   ❌ NOT READY FOR PRODUCTION: Significant issues require resolution")
            print("   ❌ Major development work needed before deployment")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = MetadataFinalVerificationTester()
    tester.run_final_verification_tests()