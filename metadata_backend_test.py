#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Big Mann Entertainment Platform
Focus: Metadata Parser & Validator Implementation Testing

This test suite covers:
1. New metadata-specific API endpoints
2. Format support testing (DDEX ERN, MEAD, JSON, CSV)
3. Validation logic testing
4. Integration testing with AWS S3
5. Authentication & Security
6. Database operations
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

# Test user credentials
TEST_USER = {
    "email": "metadata.tester@bigmannentertainment.com",
    "password": "MetadataTest2025!",
    "full_name": "Metadata Test User",
    "business_name": "Metadata Testing LLC",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "address_line1": "123 Metadata Street",
    "city": "Test City",
    "state_province": "Test State",
    "postal_code": "12345",
    "country": "United States"
}

class MetadataParserValidatorTester:
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
                        # Check format details
                        format_details = []
                        for fmt_name, fmt_info in formats.items():
                            format_details.append(f"{fmt_name}: {fmt_info.get('name', 'N/A')}")
                        
                        self.log_test(
                            "Supported Formats Endpoint",
                            True,
                            f"All required formats supported: {', '.join(format_details)}"
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

    def create_sample_metadata_files(self):
        """Create sample metadata files for testing"""
        self.sample_files = {}
        
        # 1. DDEX ERN XML Sample
        ddex_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<ern:NewReleaseMessage xmlns:ern="http://ddex.net/xml/ern/44" xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <MessageHeader>
        <MessageId>MSG123456789</MessageId>
        <MessageSender>
            <PartyId>PARTY001</PartyId>
            <PartyName>
                <FullName>Big Mann Entertainment</FullName>
            </PartyName>
        </MessageSender>
        <MessageRecipient>
            <PartyId>RECIPIENT001</PartyId>
        </MessageRecipient>
        <MessageCreatedDateTime>2025-01-01T12:00:00Z</MessageCreatedDateTime>
    </MessageHeader>
    <PartyList>
        <Party>
            <PartyId>PARTY001</PartyId>
            <PartyName>
                <FullName>Big Mann Entertainment</FullName>
            </PartyName>
        </Party>
    </PartyList>
    <ReleaseList>
        <Release>
            <ReleaseId>
                <Namespace>UPC</Namespace>
                <ProprietaryId>123456789012</ProprietaryId>
            </ReleaseId>
            <ReleaseReference>REL001</ReleaseReference>
            <ReferenceTitle>
                <TitleText>Test Album</TitleText>
            </ReferenceTitle>
            <ReleaseDate>2025-01-15</ReleaseDate>
            <Genre>Hip-Hop</Genre>
        </Release>
    </ReleaseList>
    <ResourceList>
        <SoundRecording>
            <SoundRecordingId>
                <ISRC>USRC17607839</ISRC>
            </SoundRecordingId>
            <ReferenceTitle>
                <TitleText>Test Track</TitleText>
            </ReferenceTitle>
            <DisplayArtistName>Test Artist</DisplayArtistName>
            <Duration>PT3M45S</Duration>
            <CopyrightYear>2025</CopyrightYear>
        </SoundRecording>
    </ResourceList>
</ern:NewReleaseMessage>'''
        
        # 2. MEAD JSON Sample
        mead_json = {
            "title": "Test Track MEAD",
            "artist_name": "MEAD Test Artist",
            "album_title": "MEAD Test Album",
            "isrc": "USRC17607840",
            "upc": "123456789013",
            "release_date": "2025-01-15T00:00:00Z",
            "rights_holder": "Big Mann Entertainment",
            "label_name": "BME Records",
            "genre": "Hip-Hop",
            "track_duration": "3:45"
        }
        
        # 3. Standard JSON Sample
        standard_json = {
            "title": "Test Track JSON",
            "artist": "JSON Test Artist",
            "album": "JSON Test Album",
            "isrc": "USRC17607841",
            "upc": "123456789014",
            "release_date": "2025-01-15T00:00:00Z",
            "rights_holders": ["Big Mann Entertainment", "BME Publishing"],
            "publisher_name": "BME Publishing",
            "composer_name": "Test Composer",
            "copyright_year": 2025,
            "genre": "Hip-Hop",
            "duration": "3:45",
            "description": "Test track for JSON metadata validation",
            "tags": ["hip-hop", "test", "metadata"]
        }
        
        # 4. CSV Sample
        csv_content = '''title,artist,album,isrc,upc,release_date,rights_holders,genre,duration
Test Track CSV,CSV Test Artist,CSV Test Album,USRC17607842,123456789015,2025-01-15,Big Mann Entertainment,Hip-Hop,3:45'''
        
        # Create temporary files
        self.sample_files = {
            "ddex_ern": ("test_ddex.xml", ddex_xml.encode('utf-8'), "application/xml"),
            "mead": ("test_mead.json", json.dumps(mead_json).encode('utf-8'), "application/json"),
            "json": ("test_metadata.json", json.dumps(standard_json).encode('utf-8'), "application/json"),
            "csv": ("test_metadata.csv", csv_content.encode('utf-8'), "text/csv")
        }

    def test_metadata_parse_endpoint(self):
        """Test POST /api/metadata/parse endpoint with different formats"""
        self.create_sample_metadata_files()
        
        for format_name, (filename, content, mime_type) in self.sample_files.items():
            try:
                # Prepare multipart form data
                files = {
                    'file': (filename, content, mime_type)
                }
                data = {
                    'format': format_name,
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
                        
                        # Check if metadata was parsed
                        if parsed_metadata.get("title"):
                            self.log_test(
                                f"Parse {format_name.upper()} Format",
                                True,
                                f"Successfully parsed: {parsed_metadata.get('title')} by {parsed_metadata.get('artist', 'N/A')}, Status: {validation_status}"
                            )
                        else:
                            self.log_test(
                                f"Parse {format_name.upper()} Format",
                                False,
                                error_msg="No title found in parsed metadata"
                            )
                    else:
                        self.log_test(
                            f"Parse {format_name.upper()} Format",
                            False,
                            error_msg=f"Parse failed: {result.get('message', 'Unknown error')}"
                        )
                else:
                    self.log_test(
                        f"Parse {format_name.upper()} Format",
                        False,
                        error_msg=f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Parse {format_name.upper()} Format",
                    False,
                    error_msg=f"Request error: {str(e)}"
                )

    def test_json_validation_endpoint(self):
        """Test POST /api/metadata/validate-json endpoint"""
        try:
            # Test with valid JSON metadata
            valid_metadata = {
                "title": "Direct JSON Test",
                "artist": "JSON Validator Test Artist",
                "album": "JSON Validator Test Album",
                "isrc": "USRC17607843",
                "upc": "123456789016",
                "release_date": "2025-01-15T00:00:00Z",
                "rights_holders": ["Big Mann Entertainment"],
                "genre": "Hip-Hop"
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
                    
                    self.log_test(
                        "JSON Direct Validation",
                        True,
                        f"Validation status: {validation_status}, Errors: {len(validation_errors)}"
                    )
                else:
                    self.log_test(
                        "JSON Direct Validation",
                        False,
                        error_msg=f"Validation failed: {result}"
                    )
            else:
                self.log_test(
                    "JSON Direct Validation",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "JSON Direct Validation",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_validation_results_endpoints(self):
        """Test validation results retrieval endpoints"""
        try:
            # Test list validation results
            response = self.session.get(f"{API_BASE}/metadata/validation-results")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    results = result.get("validation_results", [])
                    total_count = result.get("total_count", 0)
                    
                    self.log_test(
                        "List Validation Results",
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
                                        "Get Individual Validation Result",
                                        True,
                                        f"Retrieved result details for ID: {first_result_id}"
                                    )
                                else:
                                    self.log_test(
                                        "Get Individual Validation Result",
                                        False,
                                        error_msg="Failed to get result details"
                                    )
                            else:
                                self.log_test(
                                    "Get Individual Validation Result",
                                    False,
                                    error_msg=f"HTTP {detail_response.status_code}"
                                )
                else:
                    self.log_test(
                        "List Validation Results",
                        False,
                        error_msg="Failed to retrieve results"
                    )
            else:
                self.log_test(
                    "List Validation Results",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Validation Results Endpoints",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_duplicate_detection_endpoint(self):
        """Test GET /api/metadata/duplicates/check endpoint"""
        try:
            # Test ISRC duplicate check
            test_isrc = "USRC17607839"  # From our DDEX sample
            
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
                        error_msg="Duplicate check failed"
                    )
            else:
                self.log_test(
                    "ISRC Duplicate Detection",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
            
            # Test UPC duplicate check
            test_upc = "123456789012"  # From our DDEX sample
            
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
                        error_msg="Duplicate check failed"
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

    def test_statistics_endpoint(self):
        """Test GET /api/metadata/statistics endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/metadata/statistics")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    stats = result.get("statistics", {})
                    
                    total_validations = stats.get("total_validations", 0)
                    success_rate = stats.get("success_rate", 0)
                    format_distribution = stats.get("format_distribution", {})
                    
                    self.log_test(
                        "User Statistics",
                        True,
                        f"Total validations: {total_validations}, Success rate: {success_rate}%, Formats: {list(format_distribution.keys())}"
                    )
                else:
                    self.log_test(
                        "User Statistics",
                        False,
                        error_msg="Failed to retrieve statistics"
                    )
            else:
                self.log_test(
                    "User Statistics",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Statistics Endpoint",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_validation_logic(self):
        """Test comprehensive validation logic"""
        try:
            # Test with invalid ISRC format
            invalid_metadata = {
                "title": "Validation Test",
                "artist": "Test Artist",
                "isrc": "INVALID-ISRC",  # Invalid format
                "upc": "12345",  # Too short
                "release_date": "invalid-date",  # Invalid date
                "rights_holders": []  # Empty required field
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
                        "Validation Logic - Error Detection",
                        True,
                        f"Correctly detected {len(validation_errors)} validation errors in fields: {error_fields}"
                    )
                else:
                    self.log_test(
                        "Validation Logic - Error Detection",
                        False,
                        error_msg=f"Expected validation errors but got status: {validation_status}"
                    )
            else:
                self.log_test(
                    "Validation Logic - Error Detection",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Validation Logic Testing",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_authentication_security(self):
        """Test authentication and security for metadata endpoints"""
        try:
            # Test without authentication
            temp_session = requests.Session()
            
            response = temp_session.get(f"{API_BASE}/metadata/validation-results")
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Required - Validation Results",
                    True,
                    "Correctly requires authentication (401 Unauthorized)"
                )
            else:
                self.log_test(
                    "Authentication Required - Validation Results",
                    False,
                    error_msg=f"Expected 401 but got {response.status_code}"
                )
            
            # Test parse endpoint without auth
            response = temp_session.post(f"{API_BASE}/metadata/parse")
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Required - Parse Endpoint",
                    True,
                    "Correctly requires authentication (401 Unauthorized)"
                )
            else:
                self.log_test(
                    "Authentication Required - Parse Endpoint",
                    False,
                    error_msg=f"Expected 401 but got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Authentication Security Testing",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def test_aws_s3_integration(self):
        """Test integration with existing AWS S3 upload workflow"""
        try:
            # Test AWS health check to verify S3 integration
            response = self.session.get(f"{API_BASE}/aws/health")
            
            if response.status_code == 200:
                result = response.json()
                
                s3_status = result.get("s3", {}).get("status")
                
                if s3_status == "healthy":
                    self.log_test(
                        "AWS S3 Integration Health Check",
                        True,
                        f"S3 service is healthy: {result.get('s3', {}).get('bucket', 'N/A')}"
                    )
                else:
                    self.log_test(
                        "AWS S3 Integration Health Check",
                        False,
                        error_msg=f"S3 status: {s3_status}"
                    )
            else:
                self.log_test(
                    "AWS S3 Integration Health Check",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "AWS S3 Integration Testing",
                False,
                error_msg=f"Request error: {str(e)}"
            )

    def run_comprehensive_tests(self):
        """Run all metadata parser & validator tests"""
        print("🎯 STARTING COMPREHENSIVE METADATA PARSER & VALIDATOR TESTING")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        print("\n📋 TESTING METADATA PARSER & VALIDATOR ENDPOINTS...")
        print("-" * 60)
        
        # Core endpoint tests
        self.test_supported_formats_endpoint()
        self.test_metadata_parse_endpoint()
        self.test_json_validation_endpoint()
        self.test_validation_results_endpoints()
        self.test_duplicate_detection_endpoint()
        self.test_statistics_endpoint()
        
        print("\n🔍 TESTING VALIDATION LOGIC...")
        print("-" * 60)
        
        # Validation logic tests
        self.test_validation_logic()
        
        print("\n🔐 TESTING AUTHENTICATION & SECURITY...")
        print("-" * 60)
        
        # Security tests
        self.test_authentication_security()
        
        print("\n☁️ TESTING AWS INTEGRATION...")
        print("-" * 60)
        
        # AWS integration tests
        self.test_aws_s3_integration()
        
        # Generate summary
        self.generate_test_summary()

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 METADATA PARSER & VALIDATOR TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Group results by category
        categories = {
            "Endpoint Tests": [],
            "Format Support": [],
            "Validation Logic": [],
            "Authentication": [],
            "AWS Integration": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if any(keyword in test_name.lower() for keyword in ["parse", "endpoint", "results", "statistics", "duplicate"]):
                categories["Endpoint Tests"].append(result)
            elif any(keyword in test_name.lower() for keyword in ["ddex", "mead", "json", "csv", "format"]):
                categories["Format Support"].append(result)
            elif "validation" in test_name.lower():
                categories["Validation Logic"].append(result)
            elif "authentication" in test_name.lower():
                categories["Authentication"].append(result)
            elif "aws" in test_name.lower():
                categories["AWS Integration"].append(result)
            else:
                categories["Endpoint Tests"].append(result)
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if r["success"]])
                total = len(results)
                print(f"\n   {category}: {passed}/{total} passed")
                
                for result in results:
                    status_icon = "✅" if result["success"] else "❌"
                    print(f"      {status_icon} {result['test']}")
                    if result["error"]:
                        print(f"         Error: {result['error']}")
        
        # Critical issues
        critical_failures = [r for r in self.test_results if not r["success"] and 
                           any(keyword in r["test"].lower() for keyword in ["parse", "validation", "authentication"])]
        
        if critical_failures:
            print(f"\n⚠️ CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['error']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ Metadata Parser & Validator implementation is working excellently!")
            print("   ✅ All core functionality is operational and ready for production use.")
        elif success_rate >= 75:
            print("   ⚠️ Metadata Parser & Validator implementation is mostly working.")
            print("   ⚠️ Some minor issues need attention before full production deployment.")
        else:
            print("   ❌ Metadata Parser & Validator implementation has significant issues.")
            print("   ❌ Major fixes required before production deployment.")
        
        if failed_tests == 0:
            print("   🎉 All tests passed! The Metadata Parser & Validator is fully functional.")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = MetadataParserValidatorTester()
    tester.run_comprehensive_tests()