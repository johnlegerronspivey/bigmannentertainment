#!/usr/bin/env python3
"""
Corrected Business Module Testing - Big Mann Entertainment Platform
Fixed validation logic for UPC generation testing
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "corrected.business.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "TestPassword123!"

class CorrectedBusinessTester:
    def __init__(self):
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        print()

    def authenticate(self) -> bool:
        """Authenticate and get token"""
        # Register user
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": "Corrected Business Tester",
            "business_name": "Big Mann Entertainment Corrected Testing",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "USA"
        }
        
        requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        
        # Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]
            return True
        return False

    def test_business_endpoints(self):
        """Test all business endpoints with corrected validation"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test 1: GET /business/identifiers
        response = requests.get(f"{BACKEND_URL}/business/identifiers", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "business_legal_name" in str(data) or "business_ein" in str(data):
                self.log_test("GET /business/identifiers", True, "Business identifiers retrieved successfully")
            else:
                self.log_test("GET /business/identifiers", False, "Missing expected business fields")
        else:
            self.log_test("GET /business/identifiers", False, f"HTTP {response.status_code}")
        
        # Test 2: GET /business/products
        response = requests.get(f"{BACKEND_URL}/business/products", headers=headers)
        if response.status_code == 200:
            self.log_test("GET /business/products", True, "Business products retrieved successfully")
        else:
            self.log_test("GET /business/products", False, f"HTTP {response.status_code}")
        
        # Test 3: UPC Generation (JSON)
        upc_json_data = {
            "product_name": "Big Mann Hip Hop Album",
            "product_category": "music"
        }
        response = requests.post(f"{BACKEND_URL}/business/generate-upc", json=upc_json_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "upc" in data.get("data", {}):
                upc_code = data["data"]["upc"]
                self.log_test("POST /business/generate-upc (JSON)", True, f"UPC generated: {upc_code}")
            else:
                self.log_test("POST /business/generate-upc (JSON)", False, "Invalid UPC response structure")
        else:
            self.log_test("POST /business/generate-upc (JSON)", False, f"HTTP {response.status_code}")
        
        # Test 4: UPC Generation (Form)
        upc_form_data = {
            "product_name": "Big Mann R&B Single",
            "product_category": "music"
        }
        response = requests.post(f"{BACKEND_URL}/business/generate-upc", data=upc_form_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "upc" in data.get("data", {}):
                upc_code = data["data"]["upc"]
                self.log_test("POST /business/generate-upc (Form)", True, f"UPC generated: {upc_code}")
            else:
                self.log_test("POST /business/generate-upc (Form)", False, "Invalid UPC response structure")
        else:
            self.log_test("POST /business/generate-upc (Form)", False, f"HTTP {response.status_code}")
        
        # Test 5: ISRC Generation (JSON)
        isrc_json_data = {
            "product_name": "Big Mann Track",
            "product_category": "music",
            "artist_name": "Big Mann Entertainment",
            "track_title": "Urban Anthem"
        }
        response = requests.post(f"{BACKEND_URL}/business/generate-isrc", json=isrc_json_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "isrc_code" in data.get("data", {}):
                isrc_code = data["data"]["isrc_code"]
                self.log_test("POST /business/generate-isrc (JSON)", True, f"ISRC generated: {isrc_code}")
            else:
                self.log_test("POST /business/generate-isrc (JSON)", False, "Invalid ISRC response structure")
        else:
            self.log_test("POST /business/generate-isrc (JSON)", False, f"HTTP {response.status_code}")
        
        # Test 6: ISRC Generation (Form)
        isrc_form_data = {
            "product_name": "Big Mann Mixtape Track",
            "product_category": "music",
            "artist_name": "Big Mann Entertainment",
            "track_title": "Street Vibes"
        }
        response = requests.post(f"{BACKEND_URL}/business/generate-isrc", data=isrc_form_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "isrc_code" in data.get("data", {}):
                isrc_code = data["data"]["isrc_code"]
                self.log_test("POST /business/generate-isrc (Form)", True, f"ISRC generated: {isrc_code}")
            else:
                self.log_test("POST /business/generate-isrc (Form)", False, "Invalid ISRC response structure")
        else:
            self.log_test("POST /business/generate-isrc (Form)", False, f"HTTP {response.status_code}")
        
        # Test 7: Error Handling - UPC Missing Category
        upc_error_data = {"product_name": "Test Product"}
        response = requests.post(f"{BACKEND_URL}/business/generate-upc", json=upc_error_data, headers=headers)
        if response.status_code >= 400:
            self.log_test("UPC Error Handling (Missing Category)", True, "Proper error response for missing category")
        else:
            self.log_test("UPC Error Handling (Missing Category)", False, "Should have returned error")
        
        # Test 8: Error Handling - ISRC Missing Artist
        isrc_error_data = {
            "product_name": "Test Track",
            "product_category": "music",
            "track_title": "Test Title"
        }
        response = requests.post(f"{BACKEND_URL}/business/generate-isrc", json=isrc_error_data, headers=headers)
        if response.status_code >= 400:
            self.log_test("ISRC Error Handling (Missing Artist)", True, "Proper error response for missing artist")
        else:
            self.log_test("ISRC Error Handling (Missing Artist)", False, "Should have returned error")

    def run_tests(self):
        """Run all corrected tests"""
        print("🎯 CORRECTED BUSINESS MODULE TESTING")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Authentication failed")
            return
        
        print("✅ Authentication successful\n")
        
        self.test_business_endpoints()
        
        # Print results
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print("=" * 60)
        print("🎯 CORRECTED TEST RESULTS")
        print("=" * 60)
        print(f"📊 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🏢 BUSINESS MODULE FUNCTIONALITY: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("🎉 EXCELLENT: Business module is fully functional!")
            print("✅ UPC/ISRC generation fixes are working perfectly!")
        elif success_rate >= 85:
            print("✅ VERY GOOD: Business module is highly functional.")
        elif success_rate >= 75:
            print("⚠️ GOOD: Business module is mostly functional.")
        else:
            print("❌ NEEDS WORK: Business module has issues.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = CorrectedBusinessTester()
    tester.run_tests()