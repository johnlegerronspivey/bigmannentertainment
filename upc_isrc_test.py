#!/usr/bin/env python3
"""
Focused Testing for UPC/ISRC Generation Endpoints - Big Mann Entertainment Platform
Testing the recently fixed UPC and ISRC generation endpoints with both JSON and Form data
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "upc.isrc.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "UPC ISRC Tester"

class UPCISRCTester:
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
            "business_name": "Big Mann Entertainment Testing",
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

    def test_business_identifiers_get(self):
        """Test GET /api/business/identifiers endpoint"""
        success, response = self.make_request("GET", "/business/identifiers")
        
        if success:
            # Check if response has expected business identifier fields
            expected_fields = ["business_legal_name", "business_ein", "business_address"]
            has_expected_fields = any(field in str(response) for field in expected_fields)
            
            if has_expected_fields:
                self.log_test(
                    "GET /business/identifiers",
                    True,
                    "Business identifiers retrieved successfully",
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

    def test_business_products_get(self):
        """Test GET /api/business/products endpoint"""
        success, response = self.make_request("GET", "/business/products")
        
        if success:
            # Check if response is a list or has products data
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
        """Test POST /api/business/generate-upc with JSON data"""
        test_data = {
            "product_name": "Big Mann Hip Hop Album",
            "product_category": "music"
        }
        
        success, response = self.make_request("POST", "/business/generate-upc", test_data)
        
        if success:
            # Check if response contains UPC-related fields
            upc_fields = ["upc", "upc_full_code", "gtin", "product_name"]
            has_upc_fields = any(field in str(response).lower() for field in upc_fields)
            
            if has_upc_fields:
                self.log_test(
                    "POST /business/generate-upc (JSON)",
                    True,
                    "UPC generated successfully with JSON data",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-upc (JSON)",
                    False,
                    "Response missing UPC fields",
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
        """Test POST /api/business/generate-upc with Form data"""
        test_data = {
            "product_name": "Big Mann R&B Single",
            "product_category": "music"
        }
        
        success, response = self.make_request("POST", "/business/generate-upc", test_data, use_form=True)
        
        if success:
            # Check if response contains UPC-related fields
            upc_fields = ["upc", "upc_full_code", "gtin", "product_name"]
            has_upc_fields = any(field in str(response).lower() for field in upc_fields)
            
            if has_upc_fields:
                self.log_test(
                    "POST /business/generate-upc (Form)",
                    True,
                    "UPC generated successfully with Form data",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-upc (Form)",
                    False,
                    "Response missing UPC fields",
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
        """Test POST /api/business/generate-isrc with JSON data"""
        test_data = {
            "product_name": "Big Mann Entertainment Track",
            "product_category": "music"
        }
        
        success, response = self.make_request("POST", "/business/generate-isrc", test_data)
        
        if success:
            # Check if response contains ISRC-related fields
            isrc_fields = ["isrc", "isrc_code", "product_name"]
            has_isrc_fields = any(field in str(response).lower() for field in isrc_fields)
            
            if has_isrc_fields:
                self.log_test(
                    "POST /business/generate-isrc (JSON)",
                    True,
                    "ISRC generated successfully with JSON data",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-isrc (JSON)",
                    False,
                    "Response missing ISRC fields",
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
        """Test POST /api/business/generate-isrc with Form data"""
        test_data = {
            "product_name": "Big Mann Mixtape Track",
            "product_category": "music"
        }
        
        success, response = self.make_request("POST", "/business/generate-isrc", test_data, use_form=True)
        
        if success:
            # Check if response contains ISRC-related fields
            isrc_fields = ["isrc", "isrc_code", "product_name"]
            has_isrc_fields = any(field in str(response).lower() for field in isrc_fields)
            
            if has_isrc_fields:
                self.log_test(
                    "POST /business/generate-isrc (Form)",
                    True,
                    "ISRC generated successfully with Form data",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-isrc (Form)",
                    False,
                    "Response missing ISRC fields",
                    response
                )
        else:
            self.log_test(
                "POST /business/generate-isrc (Form)",
                False,
                "Failed to generate ISRC with Form data",
                response
            )

    def test_upc_generation_missing_params(self):
        """Test UPC generation with missing parameters"""
        test_data = {
            "product_name": "Test Product"
            # Missing product_category
        }
        
        success, response = self.make_request("POST", "/business/generate-upc", test_data)
        
        # This should fail with proper error handling
        if not success:
            error_message = str(response).lower()
            if "missing" in error_message or "required" in error_message or "category" in error_message:
                self.log_test(
                    "POST /business/generate-upc (Missing Params)",
                    True,
                    "Proper error handling for missing parameters",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-upc (Missing Params)",
                    False,
                    "Error message not descriptive enough",
                    response
                )
        else:
            self.log_test(
                "POST /business/generate-upc (Missing Params)",
                False,
                "Should have failed with missing parameters",
                response
            )

    def test_isrc_generation_missing_params(self):
        """Test ISRC generation with missing parameters"""
        test_data = {
            "product_category": "music"
            # Missing product_name
        }
        
        success, response = self.make_request("POST", "/business/generate-isrc", test_data)
        
        # This should fail with proper error handling
        if not success:
            error_message = str(response).lower()
            if "missing" in error_message or "required" in error_message or "name" in error_message:
                self.log_test(
                    "POST /business/generate-isrc (Missing Params)",
                    True,
                    "Proper error handling for missing parameters",
                    response
                )
            else:
                self.log_test(
                    "POST /business/generate-isrc (Missing Params)",
                    False,
                    "Error message not descriptive enough",
                    response
                )
        else:
            self.log_test(
                "POST /business/generate-isrc (Missing Params)",
                False,
                "Should have failed with missing parameters",
                response
            )

    def run_all_tests(self):
        """Run all UPC/ISRC focused tests"""
        print("🎯 STARTING UPC/ISRC GENERATION ENDPOINT TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        print("\n📊 TESTING BUSINESS MODULE ENDPOINTS...")
        print("-" * 40)
        
        # Test existing endpoints first
        self.test_business_identifiers_get()
        self.test_business_products_get()
        
        print("\n🏷️ TESTING UPC GENERATION ENDPOINTS...")
        print("-" * 40)
        
        # Test UPC generation with both formats
        self.test_upc_generation_json()
        self.test_upc_generation_form()
        self.test_upc_generation_missing_params()
        
        print("\n🎵 TESTING ISRC GENERATION ENDPOINTS...")
        print("-" * 40)
        
        # Test ISRC generation with both formats
        self.test_isrc_generation_json()
        self.test_isrc_generation_form()
        self.test_isrc_generation_missing_params()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 UPC/ISRC GENERATION TESTING RESULTS")
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
        
        print(f"\n🎯 BUSINESS MODULE FUNCTIONALITY:")
        business_tests = [r for r in self.test_results if "business" in r['test_name'].lower()]
        if business_tests:
            business_passed = sum(1 for r in business_tests if r['success'])
            business_total = len(business_tests)
            business_percentage = (business_passed / business_total) * 100 if business_total > 0 else 0
            print(f"   Business Endpoints: {business_passed}/{business_total} ({business_percentage:.1f}%)")
        
        print(f"\n🏷️ UPC GENERATION FUNCTIONALITY:")
        upc_tests = [r for r in self.test_results if "upc" in r['test_name'].lower()]
        if upc_tests:
            upc_passed = sum(1 for r in upc_tests if r['success'])
            upc_total = len(upc_tests)
            upc_percentage = (upc_passed / upc_total) * 100 if upc_total > 0 else 0
            print(f"   UPC Generation: {upc_passed}/{upc_total} ({upc_percentage:.1f}%)")
        
        print(f"\n🎵 ISRC GENERATION FUNCTIONALITY:")
        isrc_tests = [r for r in self.test_results if "isrc" in r['test_name'].lower()]
        if isrc_tests:
            isrc_passed = sum(1 for r in isrc_tests if r['success'])
            isrc_total = len(isrc_tests)
            isrc_percentage = (isrc_passed / isrc_total) * 100 if isrc_total > 0 else 0
            print(f"   ISRC Generation: {isrc_passed}/{isrc_total} ({isrc_percentage:.1f}%)")
        
        # Overall assessment
        if self.total_tests > 0:
            overall_success_rate = (self.passed_tests / self.total_tests) * 100
            if overall_success_rate >= 90:
                print(f"\n🎉 EXCELLENT: UPC/ISRC generation fixes are working perfectly!")
            elif overall_success_rate >= 75:
                print(f"\n✅ GOOD: UPC/ISRC generation is mostly functional with minor issues.")
            elif overall_success_rate >= 50:
                print(f"\n⚠️ PARTIAL: UPC/ISRC generation has significant issues that need attention.")
            else:
                print(f"\n❌ CRITICAL: UPC/ISRC generation endpoints have major problems.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = UPCISRCTester()
    tester.run_all_tests()