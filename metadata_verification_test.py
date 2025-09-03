#!/usr/bin/env python3
"""
Quick Verification Test for Metadata Parser & Validator
Focus: Testing key endpoints after backend restart to confirm fixes

Testing endpoints:
1. GET /api/metadata/formats/supported - Test supported formats endpoint
2. POST /api/metadata/parse - Test file upload with parsing (using a simple JSON metadata file)
3. POST /api/metadata/validate-json - Test direct JSON validation
4. GET /api/metadata/duplicates/check - Test duplicate detection for sample ISRC
5. POST /api/metadata/upload - Test the integrated upload endpoint

Goal: Confirm 26.7% success rate has improved to 90%+ after fixes
"""

import requests
import json
import time
import os
import tempfile
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://bigmannentertainment.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user credentials
TEST_USER = {
    "email": "metadata.quicktest@bigmannentertainment.com",
    "password": "QuickTest2025!",
    "full_name": "Metadata Quick Test User",
    "business_name": "Quick Test LLC",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "address_line1": "123 Quick Test Street",
    "city": "Test City",
    "state_province": "Test State",
    "postal_code": "12345",
    "country": "United States"
}

class MetadataQuickVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
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
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def setup_authentication(self):
        """Setup authentication for testing"""
        print("🔐 Setting up authentication...")
        
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
                    "Authentication Setup",
                    True,
                    f"Successfully authenticated user: {TEST_USER['email']}"
                )
                return True
            else:
                self.log_test(
                    "Authentication Setup",
                    False,
                    error_msg=f"Login failed: {login_response.status_code} - {login_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication Setup",
                False,
                error_msg=f"Authentication error: {str(e)}"
            )
            return False

    def test_1_supported_formats_endpoint(self):
        """Test 1: GET /api/metadata/formats/supported endpoint"""
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
                        validation_features = data.get("validation_features", {})
                        
                        self.log_test(
                            "1. Supported Formats Endpoint",
                            True,
                            f"All required formats supported: {list(formats.keys())}, Features: {list(validation_features.keys())}"
                        )
                    else:
                        self.log_test(
                            "1. Supported Formats Endpoint",
                            False,
                            error_msg=f"Missing formats: {missing_formats}"
                        )
                else:
                    self.log_test(
                        "1. Supported Formats Endpoint",
                        False,
                        error_msg="Invalid response structure"
                    )
            else:
                self.log_test(
                    "1. Supported Formats Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "1. Supported Formats Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_2_metadata_parse_endpoint(self):
        """Test 2: POST /api/metadata/parse - Test file upload with parsing"""
        try:
            # Create a simple JSON metadata file
            sample_metadata = {
                "title": "Quick Test Track",
                "artist": "Quick Test Artist",
                "album": "Quick Test Album",
                "isrc": "USQT25000001",
                "upc": "860004340201",
                "release_date": "2025-01-15T00:00:00Z",
                "rights_holders": ["Big Mann Entertainment"],
                "publisher_name": "BME Publishing",
                "composer_name": "Quick Test Composer",
                "copyright_year": 2025,
                "genre": "Hip-Hop",
                "duration": "3:30",
                "description": "Quick verification test track",
                "tags": ["test", "verification", "metadata"]
            }
            
            # Create temporary file
            json_content = json.dumps(sample_metadata).encode('utf-8')
            
            # Prepare multipart form data
            files = {
                'file': ('quick_test_metadata.json', json_content, 'application/json')
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
                    validation_errors = result.get("validation_errors", [])
                    
                    # Check if metadata was parsed correctly
                    if parsed_metadata.get("title") == sample_metadata["title"]:
                        self.log_test(
                            "2. Metadata Parse Endpoint",
                            True,
                            f"Successfully parsed: '{parsed_metadata.get('title')}' by {parsed_metadata.get('artist', 'N/A')}, Status: {validation_status}, Errors: {len(validation_errors)}"
                        )
                    else:
                        self.log_test(
                            "2. Metadata Parse Endpoint",
                            False,
                            error_msg=f"Parsed title mismatch: expected '{sample_metadata['title']}', got '{parsed_metadata.get('title')}'"
                        )
                else:
                    self.log_test(
                        "2. Metadata Parse Endpoint",
                        False,
                        error_msg=f"Parse failed: {result.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "2. Metadata Parse Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "2. Metadata Parse Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_3_json_validation_endpoint(self):
        """Test 3: POST /api/metadata/validate-json - Test direct JSON validation"""
        try:
            # Test with valid JSON metadata
            valid_metadata = {
                "title": "Direct JSON Validation Test",
                "artist": "JSON Test Artist",
                "album": "JSON Test Album",
                "isrc": "USQT25000002",
                "upc": "860004340202",
                "release_date": "2025-01-15T00:00:00Z",
                "rights_holders": ["Big Mann Entertainment"],
                "genre": "Hip-Hop",
                "duration": "3:45"
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/validate-json",
                json={
                    "metadata_json": valid_metadata,
                    "check_duplicates": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    validation_status = result.get("validation_status")
                    validation_errors = result.get("validation_errors", [])
                    duplicates_found = result.get("duplicates_found", 0)
                    schema_valid = result.get("schema_valid", False)
                    
                    self.log_test(
                        "3. JSON Direct Validation",
                        True,
                        f"Validation status: {validation_status}, Schema valid: {schema_valid}, Errors: {len(validation_errors)}, Duplicates: {duplicates_found}"
                    )
                else:
                    self.log_test(
                        "3. JSON Direct Validation",
                        False,
                        error_msg=f"Validation failed: {result}"
                    )
            else:
                self.log_test(
                    "3. JSON Direct Validation",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "3. JSON Direct Validation",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_4_duplicate_detection_endpoint(self):
        """Test 4: GET /api/metadata/duplicates/check - Test duplicate detection for sample ISRC"""
        try:
            # Test ISRC duplicate check with a sample ISRC
            test_isrc = "USQT25000001"  # From our previous test
            
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
                    identifier_type = result.get("identifier_type")
                    identifier_value = result.get("identifier_value")
                    
                    self.log_test(
                        "4. ISRC Duplicate Detection",
                        True,
                        f"Checked {identifier_type.upper()} '{identifier_value}', Found {duplicates_found} duplicates"
                    )
                else:
                    self.log_test(
                        "4. ISRC Duplicate Detection",
                        False,
                        error_msg="Duplicate check failed"
                    )
            else:
                self.log_test(
                    "4. ISRC Duplicate Detection",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
            
            # Also test UPC duplicate check
            test_upc = "860004340201"  # From our previous test
            
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
                        "4. UPC Duplicate Detection",
                        True,
                        f"Checked UPC '{test_upc}', Found {duplicates_found} duplicates"
                    )
                else:
                    self.log_test(
                        "4. UPC Duplicate Detection",
                        False,
                        error_msg="UPC duplicate check failed"
                    )
            else:
                self.log_test(
                    "4. UPC Duplicate Detection",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "4. Duplicate Detection Endpoints",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_5_integrated_upload_endpoint(self):
        """Test 5: POST /api/metadata/upload - Test the integrated upload endpoint"""
        try:
            # Create a simple JSON metadata file for upload
            upload_metadata = {
                "title": "Integrated Upload Test Track",
                "artist": "Upload Test Artist",
                "album": "Upload Test Album",
                "isrc": "USQT25000003",
                "upc": "860004340203",
                "release_date": "2025-01-15T00:00:00Z",
                "rights_holders": ["Big Mann Entertainment"],
                "publisher_name": "BME Publishing",
                "genre": "Hip-Hop",
                "duration": "4:00",
                "description": "Integrated upload endpoint test"
            }
            
            # Create temporary file
            json_content = json.dumps(upload_metadata).encode('utf-8')
            
            # Prepare multipart form data
            files = {
                'file': ('integrated_upload_test.json', json_content, 'application/json')
            }
            data = {
                'title': 'Integrated Upload Test',
                'description': 'Testing the integrated metadata upload endpoint',
                'validate_metadata': 'true',
                'check_duplicates': 'true',
                'send_notification': 'false'  # Don't send email for test
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/upload",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    media_id = result.get("media_id")
                    validation_status = result.get("validation_status")
                    parsed_metadata = result.get("parsed_metadata", {})
                    
                    self.log_test(
                        "5. Integrated Upload Endpoint",
                        True,
                        f"Successfully uploaded and processed metadata file, Media ID: {media_id}, Status: {validation_status}, Title: '{parsed_metadata.get('title', 'N/A')}'"
                    )
                else:
                    self.log_test(
                        "5. Integrated Upload Endpoint",
                        False,
                        error_msg=f"Upload failed: {result.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "5. Integrated Upload Endpoint",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "5. Integrated Upload Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_authentication_issues_resolved(self):
        """Test that authentication issues are resolved"""
        try:
            # Test without authentication to ensure proper 401 response
            temp_session = requests.Session()
            
            response = temp_session.get(f"{API_BASE}/metadata/validation-results")
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Issues Resolved",
                    True,
                    "Correctly requires authentication (401 Unauthorized)"
                )
            else:
                self.log_test(
                    "Authentication Issues Resolved",
                    False,
                    error_msg=f"Expected 401 but got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Authentication Issues Resolved",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_import_errors_fixed(self):
        """Test that import errors are fixed by checking endpoint availability"""
        try:
            # Test that all metadata endpoints are available (no import errors)
            endpoints_to_check = [
                "/metadata/formats/supported",
                "/metadata/statistics"
            ]
            
            all_available = True
            unavailable_endpoints = []
            
            for endpoint in endpoints_to_check:
                try:
                    response = self.session.get(f"{API_BASE}{endpoint}")
                    # 200 (success) or 401 (auth required) are both acceptable - means no import errors
                    if response.status_code not in [200, 401]:
                        all_available = False
                        unavailable_endpoints.append(f"{endpoint} ({response.status_code})")
                except Exception as e:
                    all_available = False
                    unavailable_endpoints.append(f"{endpoint} (error: {str(e)})")
            
            if all_available:
                self.log_test(
                    "Import Errors Fixed",
                    True,
                    "All metadata endpoints are accessible (no import errors)"
                )
            else:
                self.log_test(
                    "Import Errors Fixed",
                    False,
                    error_msg=f"Some endpoints unavailable: {unavailable_endpoints}"
                )
                
        except Exception as e:
            self.log_test(
                "Import Errors Fixed",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_database_integration(self):
        """Test that database integration is functional"""
        try:
            # Test statistics endpoint which requires database access
            response = self.session.get(f"{API_BASE}/metadata/statistics")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    stats = result.get("statistics", {})
                    
                    # Check if we get valid statistics structure
                    if "total_validations" in stats and "validation_status" in stats:
                        self.log_test(
                            "Database Integration Functional",
                            True,
                            f"Database accessible, Total validations: {stats.get('total_validations', 0)}"
                        )
                    else:
                        self.log_test(
                            "Database Integration Functional",
                            False,
                            error_msg="Invalid statistics structure returned"
                        )
                else:
                    self.log_test(
                        "Database Integration Functional",
                        False,
                        error_msg="Failed to retrieve statistics"
                    )
            else:
                self.log_test(
                    "Database Integration Functional",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Database Integration Functional",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def run_quick_verification_tests(self):
        """Run quick verification tests for metadata parser & validator"""
        print("🎯 STARTING QUICK VERIFICATION TEST FOR METADATA PARSER & VALIDATOR")
        print("=" * 80)
        print("Goal: Verify that 26.7% success rate has improved to 90%+ after fixes")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        print("\n📋 TESTING KEY METADATA ENDPOINTS...")
        print("-" * 60)
        
        # Core endpoint tests (as specified in review request)
        self.test_1_supported_formats_endpoint()
        self.test_2_metadata_parse_endpoint()
        self.test_3_json_validation_endpoint()
        self.test_4_duplicate_detection_endpoint()
        self.test_5_integrated_upload_endpoint()
        
        print("\n🔍 TESTING FIXES VERIFICATION...")
        print("-" * 60)
        
        # Verify specific issues are resolved
        self.test_authentication_issues_resolved()
        self.test_import_errors_fixed()
        self.test_database_integration()
        
        # Generate summary
        self.generate_verification_summary()

    def generate_verification_summary(self):
        """Generate quick verification test summary"""
        print("\n" + "=" * 80)
        print("📊 METADATA PARSER & VALIDATOR QUICK VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 VERIFICATION RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Key endpoints results
        key_endpoints = [r for r in self.test_results if any(num in r["test"] for num in ["1.", "2.", "3.", "4.", "5."])]
        key_passed = len([r for r in key_endpoints if r["success"]])
        key_total = len(key_endpoints)
        key_success_rate = (key_passed / key_total * 100) if key_total > 0 else 0
        
        print(f"\n🎯 KEY ENDPOINTS RESULTS:")
        print(f"   Key Endpoints Tested: {key_total}")
        print(f"   Key Endpoints Passed: {key_passed}")
        print(f"   Key Endpoints Success Rate: {key_success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {result['test']}")
            if result["error"]:
                print(f"      Error: {result['error']}")
        
        # Critical issues
        critical_failures = [r for r in self.test_results if not r["success"]]
        
        if critical_failures:
            print(f"\n⚠️ ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['error']}")
        
        # Final assessment
        print(f"\n💡 VERIFICATION ASSESSMENT:")
        if success_rate >= 90:
            print("   ✅ SUCCESS: Metadata Parser & Validator fixes are working excellently!")
            print("   ✅ Target of 90%+ success rate achieved.")
            print("   ✅ All authentication, import, and database integration issues resolved.")
        elif success_rate >= 75:
            print("   ⚠️ PARTIAL SUCCESS: Most fixes are working but some issues remain.")
            print("   ⚠️ Close to 90% target but needs minor adjustments.")
        else:
            print("   ❌ VERIFICATION FAILED: Significant issues still present.")
            print("   ❌ Success rate still below acceptable threshold.")
            print("   ❌ Major fixes still required.")
        
        # Improvement assessment
        if success_rate >= 90:
            improvement = success_rate - 26.7
            print(f"   🎉 IMPROVEMENT: Success rate improved by {improvement:.1f}% (from 26.7% to {success_rate:.1f}%)")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = MetadataQuickVerificationTester()
    tester.run_quick_verification_tests()