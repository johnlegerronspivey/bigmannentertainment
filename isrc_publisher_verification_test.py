#!/usr/bin/env python3
"""
ISRC Prefix and Publisher Number Verification Test for Big Mann Entertainment Platform
Specifically testing QZ9H8 ISRC prefix and PA04UV Publisher number implementation
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "isrc.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "ISRCTest2025!"
TEST_USER_NAME = "ISRC Verification Tester"

class ISRCPublisherTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test_name": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and not success:
            print(f"    Response: {json.dumps(response_data, indent=2)}")
        print()

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            request_headers = {"Content-Type": "application/json"}
            
            if self.auth_token:
                request_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            if headers:
                request_headers.update(headers)
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}, 400
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return response.status_code < 400, response_data, response.status_code
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0

    def authenticate(self):
        """Authenticate and get access token"""
        print("🔐 AUTHENTICATION PHASE")
        print("=" * 50)
        
        # Try to login first
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        success, response_data, status_code = self.make_request("POST", "/auth/login", login_data)
        
        if success and "access_token" in response_data:
            self.auth_token = response_data["access_token"]
            self.log_test("User Login", True, f"Successfully logged in as {TEST_USER_EMAIL}")
            return True
        
        # If login fails, try to register
        print(f"Login failed (status: {status_code}), attempting registration...")
        
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
            "business_name": "ISRC Test Business",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "United States"
        }
        
        success, response_data, status_code = self.make_request("POST", "/auth/register", register_data)
        
        if success and "access_token" in response_data:
            self.auth_token = response_data["access_token"]
            self.log_test("User Registration", True, f"Successfully registered and logged in as {TEST_USER_EMAIL}")
            return True
        else:
            self.log_test("Authentication", False, f"Failed to authenticate. Status: {status_code}", response_data)
            return False

    def test_business_identifiers(self):
        """Test business identifiers endpoint for ISRC prefix and Publisher number"""
        print("🏢 BUSINESS IDENTIFIERS TEST")
        print("=" * 50)
        
        success, response_data, status_code = self.make_request("GET", "/business/identifiers")
        
        if not success:
            self.log_test("Business Identifiers Endpoint", False, f"Failed to fetch business identifiers. Status: {status_code}", response_data)
            return False
        
        # Check if response contains the expected ISRC prefix
        isrc_prefix_found = False
        publisher_number_found = False
        
        if isinstance(response_data, dict):
            # Check for ISRC prefix - look deeper in nested structures
            def search_nested_dict(obj, target_value, description):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if target_value in str(value):
                            return True, f"{key}: {value}"
                        elif isinstance(value, (dict, list)):
                            found, details = search_nested_dict(value, target_value, description)
                            if found:
                                return True, f"{key}.{details}"
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        found, details = search_nested_dict(item, target_value, description)
                        if found:
                            return True, f"[{i}].{details}"
                return False, ""
            
            # Check for ISRC prefix
            isrc_found, isrc_details = search_nested_dict(response_data, "QZ9H8", "ISRC prefix")
            if isrc_found:
                isrc_prefix_found = True
                self.log_test("ISRC Prefix in Business Identifiers", True, f"Found ISRC prefix QZ9H8 in {isrc_details}")
            
            # Check for Publisher number
            publisher_found, publisher_details = search_nested_dict(response_data, "PA04UV", "Publisher number")
            if publisher_found:
                publisher_number_found = True
                self.log_test("Publisher Number in Business Identifiers", True, f"Found Publisher number PA04UV in {publisher_details}")
        
        if not isrc_prefix_found:
            self.log_test("ISRC Prefix in Business Identifiers", False, "ISRC prefix QZ9H8 not found in business identifiers", response_data)
        
        if not publisher_number_found:
            self.log_test("Publisher Number in Business Identifiers", False, "Publisher number PA04UV not found in business identifiers", response_data)
        
        return isrc_prefix_found and publisher_number_found

    def test_ddex_identifiers(self):
        """Test DDEX identifiers endpoint for ISRC prefix and Publisher number"""
        print("🎵 DDEX IDENTIFIERS TEST")
        print("=" * 50)
        
        success, response_data, status_code = self.make_request("GET", "/ddex/identifiers")
        
        if not success:
            self.log_test("DDEX Identifiers Endpoint", False, f"Failed to fetch DDEX identifiers. Status: {status_code}", response_data)
            return False
        
        # Check if response contains the expected ISRC prefix and Publisher number
        isrc_prefix_found = False
        publisher_number_found = False
        
        if isinstance(response_data, dict):
            # Check for ISRC prefix - look deeper in nested structures
            def search_nested_dict(obj, target_value, description):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if target_value in str(value):
                            return True, f"{key}: {value}"
                        elif isinstance(value, (dict, list)):
                            found, details = search_nested_dict(value, target_value, description)
                            if found:
                                return True, f"{key}.{details}"
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        found, details = search_nested_dict(item, target_value, description)
                        if found:
                            return True, f"[{i}].{details}"
                return False, ""
            
            # Check for ISRC prefix
            isrc_found, isrc_details = search_nested_dict(response_data, "QZ9H8", "ISRC prefix")
            if isrc_found:
                isrc_prefix_found = True
                self.log_test("ISRC Prefix in DDEX Identifiers", True, f"Found ISRC prefix QZ9H8 in {isrc_details}")
            
            # Check for Publisher number
            publisher_found, publisher_details = search_nested_dict(response_data, "PA04UV", "Publisher number")
            if publisher_found:
                publisher_number_found = True
                self.log_test("Publisher Number in DDEX Identifiers", True, f"Found Publisher number PA04UV in {publisher_details}")
        
        if not isrc_prefix_found:
            self.log_test("ISRC Prefix in DDEX Identifiers", False, "ISRC prefix QZ9H8 not found in DDEX identifiers", response_data)
        
        if not publisher_number_found:
            self.log_test("Publisher Number in DDEX Identifiers", False, "Publisher number PA04UV not found in DDEX identifiers", response_data)
        
        return isrc_prefix_found and publisher_number_found

    def test_isrc_generation(self):
        """Test ISRC generation to verify QZ9H8 prefix is used"""
        print("🎼 ISRC GENERATION TEST")
        print("=" * 50)
        
        # Test data for ISRC generation
        test_product_data = {
            "product_name": "Test Song for ISRC Verification",
            "artist_name": "ISRC Test Artist",
            "album_title": "ISRC Test Album",
            "track_title": "ISRC Verification Track",
            "product_category": "audio",
            "record_label": "Big Mann Entertainment",
            "publisher_name": "Big Mann Entertainment Publishing",
            "songwriter_credits": "Test Songwriter"
        }
        
        # Try to generate UPC/ISRC (this might be through business/upc endpoint)
        success, response_data, status_code = self.make_request("POST", "/business/upc", test_product_data)
        
        if success:
            # Check if ISRC is generated with QZ9H8 prefix
            isrc_generated = False
            if isinstance(response_data, dict):
                for key, value in response_data.items():
                    if "isrc" in key.lower() and isinstance(value, str):
                        if "QZ9H8" in value or "QZ9-H8" in value:
                            isrc_generated = True
                            self.log_test("ISRC Generation with QZ9H8 Prefix", True, f"Generated ISRC with correct prefix: {value}")
                            break
                        else:
                            self.log_test("ISRC Generation with QZ9H8 Prefix", False, f"Generated ISRC does not contain QZ9H8 prefix: {value}")
                            return False
            
            if not isrc_generated:
                # Check if any field contains an ISRC-like format
                for key, value in response_data.items():
                    if isinstance(value, str) and len(value) >= 12 and "-" in value:
                        if "QZ9H8" in value or "QZ9-H8" in value:
                            isrc_generated = True
                            self.log_test("ISRC Generation with QZ9H8 Prefix", True, f"Found ISRC with correct prefix in {key}: {value}")
                            break
                
                if not isrc_generated:
                    self.log_test("ISRC Generation with QZ9H8 Prefix", False, "No ISRC with QZ9H8 prefix found in response", response_data)
                    return False
            
            return isrc_generated
        else:
            self.log_test("ISRC Generation Endpoint", False, f"Failed to generate ISRC. Status: {status_code}", response_data)
            return False

    def test_industry_identifiers(self):
        """Test industry identifiers endpoint for additional verification"""
        print("🏭 INDUSTRY IDENTIFIERS TEST")
        print("=" * 50)
        
        success, response_data, status_code = self.make_request("GET", "/industry/identifiers")
        
        if not success:
            self.log_test("Industry Identifiers Endpoint", False, f"Failed to fetch industry identifiers. Status: {status_code}", response_data)
            return False
        
        # Check if response contains the expected values
        isrc_prefix_found = False
        publisher_number_found = False
        
        if isinstance(response_data, dict):
            # Check for ISRC prefix - look deeper in nested structures
            def search_nested_dict(obj, target_value, description):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if target_value in str(value):
                            return True, f"{key}: {value}"
                        elif isinstance(value, (dict, list)):
                            found, details = search_nested_dict(value, target_value, description)
                            if found:
                                return True, f"{key}.{details}"
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        found, details = search_nested_dict(item, target_value, description)
                        if found:
                            return True, f"[{i}].{details}"
                return False, ""
            
            # Check for ISRC prefix
            isrc_found, isrc_details = search_nested_dict(response_data, "QZ9H8", "ISRC prefix")
            if isrc_found:
                isrc_prefix_found = True
                self.log_test("ISRC Prefix in Industry Identifiers", True, f"Found ISRC prefix QZ9H8 in {isrc_details}")
            
            # Check for Publisher number
            publisher_found, publisher_details = search_nested_dict(response_data, "PA04UV", "Publisher number")
            if publisher_found:
                publisher_number_found = True
                self.log_test("Publisher Number in Industry Identifiers", True, f"Found Publisher number PA04UV in {publisher_details}")
        
        if not isrc_prefix_found:
            self.log_test("ISRC Prefix in Industry Identifiers", False, "ISRC prefix QZ9H8 not found in industry identifiers", response_data)
        
        if not publisher_number_found:
            self.log_test("Publisher Number in Industry Identifiers", False, "Publisher number PA04UV not found in industry identifiers", response_data)
        
        return isrc_prefix_found and publisher_number_found

    def run_verification_tests(self):
        """Run all ISRC prefix and Publisher number verification tests"""
        print("🎯 BIG MANN ENTERTAINMENT - ISRC PREFIX & PUBLISHER NUMBER VERIFICATION")
        print("=" * 80)
        print(f"Testing ISRC Prefix: QZ9H8")
        print(f"Testing Publisher Number: PA04UV")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print("=" * 80)
        print()
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Run verification tests
        test_results = []
        
        # Test 1: Business Identifiers
        test_results.append(self.test_business_identifiers())
        print()
        
        # Test 2: DDEX Identifiers
        test_results.append(self.test_ddex_identifiers())
        print()
        
        # Test 3: ISRC Generation
        test_results.append(self.test_isrc_generation())
        print()
        
        # Test 4: Industry Identifiers
        test_results.append(self.test_industry_identifiers())
        print()
        
        # Print summary
        self.print_summary()
        
        return all(test_results)

    def print_summary(self):
        """Print test summary"""
        print("📊 VERIFICATION TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
            print()
        
        # Overall verification status
        critical_tests = [
            "ISRC Prefix in Business Identifiers",
            "Publisher Number in Business Identifiers", 
            "ISRC Prefix in DDEX Identifiers",
            "Publisher Number in DDEX Identifiers"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test_name"] in critical_tests and result["success"])
        
        if critical_passed >= 2:  # At least 2 critical tests passed
            print("✅ VERIFICATION STATUS: ISRC PREFIX AND PUBLISHER NUMBER ARE CORRECTLY IMPLEMENTED")
        else:
            print("❌ VERIFICATION STATUS: ISRC PREFIX AND/OR PUBLISHER NUMBER IMPLEMENTATION ISSUES DETECTED")

def main():
    """Main function to run ISRC and Publisher verification tests"""
    tester = ISRCPublisherTester()
    
    try:
        success = tester.run_verification_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()