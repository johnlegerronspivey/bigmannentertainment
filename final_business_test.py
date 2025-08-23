#!/usr/bin/env python3
"""
Final Comprehensive Business Module Testing - Big Mann Entertainment Platform
Testing all business endpoints including UPC/ISRC generation with correct parameters
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "final.business.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Final Business Tester"

class FinalBusinessTester:
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
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def make_request(self, method: str, endpoint: str, data: Any = None, headers: Dict = None, 
                    use_form: bool = False) -> tuple[bool, Any]:
        """Make HTTP request with error handling"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            request_headers = {"Content-Type": "application/json"}
            
            if self.auth_token:
                request_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            if headers:
                request_headers.update(headers)
            
            if use_form and data:
                # Use form data instead of JSON
                request_headers.pop("Content-Type", None)  # Let requests set it
                response = self.session.request(method, url, data=data, headers=request_headers)
            else:
                response = self.session.request(method, url, json=data, headers=request_headers)
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            return response.status_code < 400, response_data
        except Exception as e:
            return False, {"error": str(e)}

    def authenticate(self) -> bool:
        """Authenticate user and get token"""
        print("🔐 AUTHENTICATING USER...")
        
        # Try to register user first (in case they don't exist)
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
            "business_name": "Big Mann Entertainment Final Testing",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "USA"
        }
        
        success, response = self.make_request("POST", "/auth/register", register_data)
        if success:
            print("✅ User registered successfully")
        else:
            print("ℹ️ User may already exist, proceeding to login")
        
        # Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        success, response = self.make_request("POST", "/auth/login", login_data)
        if success and "access_token" in response:
            self.auth_token = response["access_token"]
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response}")
            return False

    def test_business_identifiers(self):
        """Test GET /api/business/identifiers"""
        success, response = self.make_request("GET", "/business/identifiers")
        
        if success:
            expected_fields = ["business_legal_name", "business_ein", "business_address"]
            has_expected_fields = any(field in str(response) for field in expected_fields)
            
            if has_expected_fields:
                self.log_test(
                    "GET /business/identifiers",
                    True,
                    "Business identifiers retrieved with expected fields",
                    response
                )
            else:
                self.log_test(
                    "GET /business/identifiers",
                    False,
                    "Response missing expected business identifier fields",
                    response
                )
        else:
            self.log_test(
                "GET /business/identifiers",
                False,
                "Failed to retrieve business identifiers",
                response
            )

    def test_business_products(self):
        """Test GET /api/business/products"""
        success, response = self.make_request("GET", "/business/products")
        
        if success:
            is_valid_response = isinstance(response, list) or "products" in str(response).lower()
            
            if is_valid_response:
                self.log_test(
                    "GET /business/products",
                    True,
                    "Business products retrieved successfully",
                    response
                )
            else:
                self.log_test(
                    "GET /business/products",
                    False,
                    "Invalid products response format",
                    response
                )
        else:
            self.log_test(
                "GET /business/products",
                False,
                "Failed to retrieve business products",
                response
            )

    def test_upc_generation_json(self):
        """Test UPC generation with JSON data"""
        test_data = {
            "product_name": "Big Mann Hip Hop Album Deluxe",
            "product_category": "music"
        }
        
        success, response = self.make_request("POST", "/business/generate-upc", test_data)
        
        if success and isinstance(response, dict) and response.get("success"):
            upc_data = response.get("data", {})
            if "upc_full_code" in upc_data and "gtin" in upc_data:
                self.log_test(
                    "POST /business/generate-upc (JSON)",
                    True,
                    f"UPC generated: {upc_data.get('upc_full_code')}",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-upc (JSON)",
                    False,
                    "Response missing UPC/GTIN fields",
                    response
                )
        else:
            self.log_test(
                "POST /business/generate-upc (JSON)",
                False,
                "Failed to generate UPC with JSON data",
                response
            )

    def test_upc_generation_form(self):
        """Test UPC generation with Form data"""
        test_data = {
            "product_name": "Big Mann R&B Single Collection",
            "product_category": "music"
        }
        
        success, response = self.make_request("POST", "/business/generate-upc", test_data, use_form=True)
        
        if success and isinstance(response, dict) and response.get("success"):
            upc_data = response.get("data", {})
            if "upc_full_code" in upc_data and "gtin" in upc_data:
                self.log_test(
                    "POST /business/generate-upc (Form)",
                    True,
                    f"UPC generated: {upc_data.get('upc_full_code')}",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-upc (Form)",
                    False,
                    "Response missing UPC/GTIN fields",
                    response
                )
        else:
            self.log_test(
                "POST /business/generate-upc (Form)",
                False,
                "Failed to generate UPC with Form data",
                response
            )

    def test_isrc_generation_json(self):
        """Test ISRC generation with JSON data (complete parameters)"""
        test_data = {
            "product_name": "Big Mann Entertainment Track",
            "product_category": "music",
            "artist_name": "Big Mann Entertainment",
            "track_title": "Urban Anthem 2025"
        }
        
        success, response = self.make_request("POST", "/business/generate-isrc", test_data)
        
        if success and isinstance(response, dict) and response.get("success"):
            isrc_data = response.get("data", {})
            if "isrc_code" in isrc_data and isrc_data["isrc_code"].startswith("US-QZ9"):
                self.log_test(
                    "POST /business/generate-isrc (JSON)",
                    True,
                    f"ISRC generated: {isrc_data.get('isrc_code')}",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-isrc (JSON)",
                    False,
                    "Invalid ISRC code format",
                    response
                )
        else:
            self.log_test(
                "POST /business/generate-isrc (JSON)",
                False,
                "Failed to generate ISRC with JSON data",
                response
            )

    def test_isrc_generation_form(self):
        """Test ISRC generation with Form data (complete parameters)"""
        test_data = {
            "product_name": "Big Mann Mixtape Track",
            "product_category": "music",
            "artist_name": "Big Mann Entertainment",
            "track_title": "Street Anthem"
        }
        
        success, response = self.make_request("POST", "/business/generate-isrc", test_data, use_form=True)
        
        if success and isinstance(response, dict) and response.get("success"):
            isrc_data = response.get("data", {})
            if "isrc_code" in isrc_data and isrc_data["isrc_code"].startswith("US-QZ9"):
                self.log_test(
                    "POST /business/generate-isrc (Form)",
                    True,
                    f"ISRC generated: {isrc_data.get('isrc_code')}",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-isrc (Form)",
                    False,
                    "Invalid ISRC code format",
                    response
                )
        else:
            self.log_test(
                "POST /business/generate-isrc (Form)",
                False,
                "Failed to generate ISRC with Form data",
                response
            )

    def test_error_handling(self):
        """Test error handling for missing parameters"""
        # Test UPC with missing category
        upc_data = {"product_name": "Test Product"}
        success, response = self.make_request("POST", "/business/generate-upc", upc_data)
        
        if not success and "category" in str(response).lower():
            self.log_test(
                "UPC Error Handling (Missing Category)",
                True,
                "Proper error handling for missing product_category",
                response
            )
        else:
            self.log_test(
                "UPC Error Handling (Missing Category)",
                False,
                "Error handling not working properly",
                response
            )
        
        # Test ISRC with missing artist_name
        isrc_data = {
            "product_name": "Test Track",
            "product_category": "music",
            "track_title": "Test Title"
        }
        success, response = self.make_request("POST", "/business/generate-isrc", isrc_data)
        
        if not success and "artist_name" in str(response).lower():
            self.log_test(
                "ISRC Error Handling (Missing Artist)",
                True,
                "Proper error handling for missing artist_name",
                response
            )
        else:
            self.log_test(
                "ISRC Error Handling (Missing Artist)",
                False,
                "Error handling not working properly",
                response
            )

    def run_all_tests(self):
        """Run comprehensive business module tests"""
        print("🎯 FINAL BUSINESS MODULE COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        print("\n📊 TESTING BUSINESS ENDPOINTS...")
        print("-" * 40)
        
        # Test existing endpoints
        self.test_business_identifiers()
        self.test_business_products()
        
        print("\n🏷️ TESTING UPC GENERATION (BOTH FORMATS)...")
        print("-" * 40)
        
        # Test UPC generation
        self.test_upc_generation_json()
        self.test_upc_generation_form()
        
        print("\n🎵 TESTING ISRC GENERATION (BOTH FORMATS)...")
        print("-" * 40)
        
        # Test ISRC generation
        self.test_isrc_generation_json()
        self.test_isrc_generation_form()
        
        print("\n⚠️ TESTING ERROR HANDLING...")
        print("-" * 40)
        
        # Test error handling
        self.test_error_handling()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 FINAL BUSINESS MODULE TEST RESULTS")
        print("=" * 60)
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"   {result['status']}: {result['test_name']}")
            if result['details']:
                print(f"      └─ {result['details']}")
        
        # Calculate specific functionality percentages
        business_basic = [r for r in self.test_results if r['test_name'].startswith("GET /business")]
        upc_tests = [r for r in self.test_results if "upc" in r['test_name'].lower() and "error" not in r['test_name'].lower()]
        isrc_tests = [r for r in self.test_results if "isrc" in r['test_name'].lower() and "error" not in r['test_name'].lower()]
        error_tests = [r for r in self.test_results if "error" in r['test_name'].lower()]
        
        print(f"\n🎯 FUNCTIONALITY BREAKDOWN:")
        
        if business_basic:
            basic_passed = sum(1 for r in business_basic if r['success'])
            basic_total = len(business_basic)
            basic_percentage = (basic_passed / basic_total) * 100 if basic_total > 0 else 0
            print(f"   📊 Basic Business Endpoints: {basic_passed}/{basic_total} ({basic_percentage:.1f}%)")
        
        if upc_tests:
            upc_passed = sum(1 for r in upc_tests if r['success'])
            upc_total = len(upc_tests)
            upc_percentage = (upc_passed / upc_total) * 100 if upc_total > 0 else 0
            print(f"   🏷️ UPC Generation (JSON + Form): {upc_passed}/{upc_total} ({upc_percentage:.1f}%)")
        
        if isrc_tests:
            isrc_passed = sum(1 for r in isrc_tests if r['success'])
            isrc_total = len(isrc_tests)
            isrc_percentage = (isrc_passed / isrc_total) * 100 if isrc_total > 0 else 0
            print(f"   🎵 ISRC Generation (JSON + Form): {isrc_passed}/{isrc_total} ({isrc_percentage:.1f}%)")
        
        if error_tests:
            error_passed = sum(1 for r in error_tests if r['success'])
            error_total = len(error_tests)
            error_percentage = (error_passed / error_total) * 100 if error_total > 0 else 0
            print(f"   ⚠️ Error Handling: {error_passed}/{error_total} ({error_percentage:.1f}%)")
        
        # Overall business module assessment
        if self.total_tests > 0:
            overall_success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"\n🏢 BUSINESS MODULE OVERALL FUNCTIONALITY: {overall_success_rate:.1f}%")
            
            if overall_success_rate >= 95:
                print(f"🎉 EXCELLENT: Business module is fully functional!")
                print(f"✅ UPC/ISRC generation fixes are working perfectly!")
            elif overall_success_rate >= 85:
                print(f"✅ VERY GOOD: Business module is highly functional with minor issues.")
            elif overall_success_rate >= 75:
                print(f"⚠️ GOOD: Business module is mostly functional but needs some attention.")
            else:
                print(f"❌ NEEDS WORK: Business module has significant issues.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = FinalBusinessTester()
    tester.run_all_tests()