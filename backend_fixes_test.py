#!/usr/bin/env python3
"""
Backend Fixes Testing for Big Mann Entertainment Platform
Testing specific fixes implemented:
1. Payment Service Initialization
2. Label Authentication 
3. New Endpoints: Sponsorship public, Tax business-info, Media analytics
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "fixes.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "FixesTest2025!"
TEST_USER_NAME = "Backend Fixes Tester"

class BackendFixesTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.module_results = {
            "payment": {"total": 0, "passed": 0, "endpoints": []},
            "label": {"total": 0, "passed": 0, "endpoints": []},
            "sponsorship": {"total": 0, "passed": 0, "endpoints": []},
            "tax": {"total": 0, "passed": 0, "endpoints": []},
            "media": {"total": 0, "passed": 0, "endpoints": []}
        }
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None, module: str = None):
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
            "response_data": response_data,
            "module": module
        }
        self.test_results.append(result)
        
        # Update module results
        if module and module in self.module_results:
            self.module_results[module]["total"] += 1
            if success:
                self.module_results[module]["passed"] += 1
            self.module_results[module]["endpoints"].append({
                "name": test_name,
                "success": success,
                "details": details
            })
        
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def authenticate(self) -> bool:
        """Authenticate and get access token"""
        try:
            # First try to register the test user
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "business_name": "Big Mann Entertainment Fixes Test",
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }
            
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            # Now try to login
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", True, f"Successfully authenticated as {TEST_USER_EMAIL}")
                return True
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_payment_module(self):
        """Test Payment Module - Should improve from 33% (1/3) to higher functionality"""
        print("💳 TESTING PAYMENT MODULE - PAYMENT SERVICE INITIALIZATION FIX")
        print("=" * 70)
        
        # Test 1: Payment Packages (existing endpoint)
        try:
            response = self.session.get(f"{BACKEND_URL}/payments/packages")
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                self.log_test("Payment Packages", True, 
                             f"Retrieved {len(packages)} payment packages", module="payment")
            else:
                self.log_test("Payment Packages", False, 
                             f"Status: {response.status_code}", response.text, module="payment")
        except Exception as e:
            self.log_test("Payment Packages", False, f"Error: {str(e)}", module="payment")

        # Test 2: Payment Status (should work with service initialization fix)
        try:
            response = self.session.get(f"{BACKEND_URL}/payments/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Payment Status", True, 
                             f"Payment status retrieved - Service initialized properly", module="payment")
            else:
                self.log_test("Payment Status", False, 
                             f"Status: {response.status_code}", response.text, module="payment")
        except Exception as e:
            self.log_test("Payment Status", False, f"Error: {str(e)}", module="payment")

        # Test 3: Payment Service Health Check (new functionality)
        try:
            response = self.session.get(f"{BACKEND_URL}/payments/health")
            if response.status_code == 200:
                data = response.json()
                service_status = data.get("service_status", "unknown")
                self.log_test("Payment Service Health", True, 
                             f"Payment service health: {service_status}", module="payment")
            else:
                self.log_test("Payment Service Health", False, 
                             f"Status: {response.status_code}", response.text, module="payment")
        except Exception as e:
            self.log_test("Payment Service Health", False, f"Error: {str(e)}", module="payment")

    def test_label_module(self):
        """Test Label Module - Should improve from 0% (0/3) to at least some functionality"""
        print("🏷️ TESTING LABEL MODULE - AUTHENTICATION IMPORT ISSUES FIX")
        print("=" * 70)
        
        # Test 1: Label Dashboard (should work with auth fix)
        try:
            response = self.session.get(f"{BACKEND_URL}/label/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data.get("dashboard", {})
                self.log_test("Label Dashboard", True, 
                             f"Label dashboard loaded successfully", module="label")
            else:
                self.log_test("Label Dashboard", False, 
                             f"Status: {response.status_code}", response.text, module="label")
        except Exception as e:
            self.log_test("Label Dashboard", False, f"Error: {str(e)}", module="label")

        # Test 2: Label Artists (should work with auth fix)
        try:
            response = self.session.get(f"{BACKEND_URL}/label/artists")
            if response.status_code == 200:
                data = response.json()
                artists = data.get("artists", [])
                self.log_test("Label Artists", True, 
                             f"Retrieved {len(artists)} label artists", module="label")
            else:
                self.log_test("Label Artists", False, 
                             f"Status: {response.status_code}", response.text, module="label")
        except Exception as e:
            self.log_test("Label Artists", False, f"Error: {str(e)}", module="label")

        # Test 3: Label Projects (should work with auth fix)
        try:
            response = self.session.get(f"{BACKEND_URL}/label/projects")
            if response.status_code == 200:
                data = response.json()
                projects = data.get("projects", [])
                self.log_test("Label Projects", True, 
                             f"Retrieved {len(projects)} label projects", module="label")
            else:
                self.log_test("Label Projects", False, 
                             f"Status: {response.status_code}", response.text, module="label")
        except Exception as e:
            self.log_test("Label Projects", False, f"Error: {str(e)}", module="label")

    def test_sponsorship_module(self):
        """Test Sponsorship Module - Should have improved functionality with new public endpoint"""
        print("🤝 TESTING SPONSORSHIP MODULE - NEW PUBLIC SPONSORS ENDPOINT")
        print("=" * 70)
        
        # Test 1: NEW Public Sponsors List (should not require auth)
        try:
            # Test without authentication first
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/sponsorship/sponsors/public")
            if response.status_code == 200:
                data = response.json()
                sponsors = data.get("sponsors", [])
                self.log_test("Sponsorship Public Sponsors", True, 
                             f"Retrieved {len(sponsors)} public sponsors (no auth required)", module="sponsorship")
            else:
                self.log_test("Sponsorship Public Sponsors", False, 
                             f"Status: {response.status_code}", response.text, module="sponsorship")
        except Exception as e:
            self.log_test("Sponsorship Public Sponsors", False, f"Error: {str(e)}", module="sponsorship")

        # Test 2: Sponsorship Dashboard (existing, should work)
        try:
            response = self.session.get(f"{BACKEND_URL}/sponsorship/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data.get("dashboard", {})
                self.log_test("Sponsorship Dashboard", True, 
                             f"Sponsorship dashboard loaded", module="sponsorship")
            else:
                self.log_test("Sponsorship Dashboard", False, 
                             f"Status: {response.status_code}", response.text, module="sponsorship")
        except Exception as e:
            self.log_test("Sponsorship Dashboard", False, f"Error: {str(e)}", module="sponsorship")

        # Test 3: Sponsorship Deals (existing, should work)
        try:
            response = self.session.get(f"{BACKEND_URL}/sponsorship/deals")
            if response.status_code == 200:
                data = response.json()
                deals = data.get("deals", [])
                self.log_test("Sponsorship Deals", True, 
                             f"Retrieved {len(deals)} sponsorship deals", module="sponsorship")
            else:
                self.log_test("Sponsorship Deals", False, 
                             f"Status: {response.status_code}", response.text, module="sponsorship")
        except Exception as e:
            self.log_test("Sponsorship Deals", False, f"Error: {str(e)}", module="sponsorship")

    def test_tax_module(self):
        """Test Tax Module - Should have improved functionality with business-info endpoint"""
        print("📊 TESTING TAX MODULE - NEW BUSINESS-INFO ENDPOINT")
        print("=" * 70)
        
        # Test 1: NEW Tax Business Info (for regular users)
        try:
            response = self.session.get(f"{BACKEND_URL}/tax/business-info")
            if response.status_code == 200:
                data = response.json()
                business_info = data.get("business_info", {})
                self.log_test("Tax Business Info", True, 
                             f"Retrieved business tax information for regular users", module="tax")
            else:
                self.log_test("Tax Business Info", False, 
                             f"Status: {response.status_code}", response.text, module="tax")
        except Exception as e:
            self.log_test("Tax Business Info", False, f"Error: {str(e)}", module="tax")

        # Test 2: Tax Dashboard (existing, should work)
        try:
            response = self.session.get(f"{BACKEND_URL}/tax/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data.get("dashboard", {})
                self.log_test("Tax Dashboard", True, 
                             f"Tax dashboard loaded", module="tax")
            else:
                self.log_test("Tax Dashboard", False, 
                             f"Status: {response.status_code}", response.text, module="tax")
        except Exception as e:
            self.log_test("Tax Dashboard", False, f"Error: {str(e)}", module="tax")

        # Test 3: Tax Payments (existing, should work)
        try:
            response = self.session.get(f"{BACKEND_URL}/tax/payments")
            if response.status_code == 200:
                data = response.json()
                payments = data.get("payments", [])
                self.log_test("Tax Payments", True, 
                             f"Retrieved {len(payments)} tax payments", module="tax")
            else:
                self.log_test("Tax Payments", False, 
                             f"Status: {response.status_code}", response.text, module="tax")
        except Exception as e:
            self.log_test("Tax Payments", False, f"Error: {str(e)}", module="tax")

    def test_media_module(self):
        """Test Media Module - Should have improved functionality with analytics endpoint"""
        print("🎬 TESTING MEDIA MODULE - NEW ANALYTICS ENDPOINT")
        print("=" * 70)
        
        # Test 1: NEW Media Analytics (for users)
        try:
            response = self.session.get(f"{BACKEND_URL}/media/analytics")
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                self.log_test("Media Analytics", True, 
                             f"Retrieved media analytics for users", module="media")
            else:
                self.log_test("Media Analytics", False, 
                             f"Status: {response.status_code}", response.text, module="media")
        except Exception as e:
            self.log_test("Media Analytics", False, f"Error: {str(e)}", module="media")

        # Test 2: Media Library (existing, should work)
        try:
            response = self.session.get(f"{BACKEND_URL}/media/library")
            if response.status_code == 200:
                data = response.json()
                media_items = data.get("media", [])
                self.log_test("Media Library", True, 
                             f"Retrieved {len(media_items)} media items", module="media")
            else:
                self.log_test("Media Library", False, 
                             f"Status: {response.status_code}", response.text, module="media")
        except Exception as e:
            self.log_test("Media Library", False, f"Error: {str(e)}", module="media")

        # Test 3: Media Upload Endpoint Check (existing, should work)
        try:
            # Just check if endpoint exists (don't actually upload)
            response = self.session.post(f"{BACKEND_URL}/media/upload")
            # We expect 400 or 422 for missing data, not 404 or 500
            if response.status_code in [400, 422]:
                self.log_test("Media Upload Endpoint", True, 
                             f"Media upload endpoint accessible (expects form data)", module="media")
            elif response.status_code == 200:
                self.log_test("Media Upload Endpoint", True, 
                             f"Media upload endpoint working", module="media")
            else:
                self.log_test("Media Upload Endpoint", False, 
                             f"Status: {response.status_code}", response.text, module="media")
        except Exception as e:
            self.log_test("Media Upload Endpoint", False, f"Error: {str(e)}", module="media")

    def calculate_module_functionality(self):
        """Calculate functionality percentage for each module"""
        functionality = {}
        for module, results in self.module_results.items():
            if results["total"] > 0:
                percentage = (results["passed"] / results["total"]) * 100
                functionality[module] = {
                    "percentage": round(percentage, 1),
                    "passed": results["passed"],
                    "total": results["total"]
                }
            else:
                functionality[module] = {
                    "percentage": 0,
                    "passed": 0,
                    "total": 0
                }
        return functionality

    def count_working_endpoints(self):
        """Count total working endpoints across all modules"""
        total_working = 0
        total_tested = 0
        for module, results in self.module_results.items():
            total_working += results["passed"]
            total_tested += results["total"]
        return total_working, total_tested

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 BIG MANN ENTERTAINMENT PLATFORM - BACKEND FIXES TESTING REPORT")
        print("=" * 80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Module functionality breakdown
        functionality = self.calculate_module_functionality()
        total_working, total_tested = self.count_working_endpoints()
        
        print(f"\n🔧 FIXES VERIFICATION:")
        print(f"1. Payment Service Initialization: {functionality['payment']['percentage']}% ({functionality['payment']['passed']}/{functionality['payment']['total']})")
        print(f"2. Label Authentication Fix: {functionality['label']['percentage']}% ({functionality['label']['passed']}/{functionality['label']['total']})")
        print(f"3. Sponsorship Public Endpoint: {functionality['sponsorship']['percentage']}% ({functionality['sponsorship']['passed']}/{functionality['sponsorship']['total']})")
        print(f"4. Tax Business-Info Endpoint: {functionality['tax']['percentage']}% ({functionality['tax']['passed']}/{functionality['tax']['total']})")
        print(f"5. Media Analytics Endpoint: {functionality['media']['percentage']}% ({functionality['media']['passed']}/{functionality['media']['total']})")
        
        print(f"\n📈 MODULE IMPROVEMENT TRACKING:")
        print(f"Payment Module: Expected improvement from 33% → Current: {functionality['payment']['percentage']}%")
        print(f"Label Module: Expected improvement from 0% → Current: {functionality['label']['percentage']}%")
        print(f"Sponsorship Module: Maintained high functionality → Current: {functionality['sponsorship']['percentage']}%")
        print(f"Tax Module: Maintained high functionality → Current: {functionality['tax']['percentage']}%")
        print(f"Media Module: Maintained high functionality → Current: {functionality['media']['percentage']}%")
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"Total Working Endpoints: {total_working}/{total_tested}")
        if total_tested > 0:
            overall_functionality = (total_working / total_tested) * 100
            print(f"Final Overall Functionality Percentage: {overall_functionality:.1f}%")
        
        # Specific fixes verification
        print(f"\n✅ SPECIFIC FIXES VERIFIED:")
        fixes_verified = []
        if functionality['payment']['percentage'] > 33:
            fixes_verified.append("Payment Service Initialization - IMPROVED")
        if functionality['label']['percentage'] > 0:
            fixes_verified.append("Label Authentication - FIXED")
        
        # Check for new endpoints
        new_endpoints_working = 0
        for result in self.test_results:
            if any(endpoint in result['test_name'] for endpoint in ['Public Sponsors', 'Business Info', 'Media Analytics']):
                if result['success']:
                    new_endpoints_working += 1
        
        if new_endpoints_working > 0:
            fixes_verified.append(f"New Endpoints Added - {new_endpoints_working} working")
        
        for fix in fixes_verified:
            print(f"  ✅ {fix}")
        
        # Failed tests details
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print(f"\n❌ REMAINING ISSUES:")
            for test in failed_tests:
                print(f"- {test['test_name']}: {test['details']}")
        
        print(f"\n🕒 Test completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests / max(self.total_tests, 1)) * 100,
            "module_functionality": functionality,
            "total_working_endpoints": total_working,
            "total_tested_endpoints": total_tested,
            "overall_functionality": (total_working / max(total_tested, 1)) * 100,
            "fixes_verified": fixes_verified,
            "test_results": self.test_results
        }

    def run_all_tests(self):
        """Run all backend fixes tests"""
        print("🚀 STARTING BACKEND FIXES TESTING")
        print("Testing specific fixes implemented for Big Mann Entertainment Platform")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all test suites for the specific fixes
        self.test_payment_module()
        self.test_label_module()
        self.test_sponsorship_module()
        self.test_tax_module()
        self.test_media_module()
        
        # Generate final report
        report = self.generate_report()
        
        return report

def main():
    """Main function to run backend fixes tests"""
    tester = BackendFixesTester()
    report = tester.run_all_tests()
    
    # Return appropriate exit code
    if report and report["failed_tests"] == 0:
        print("\n🎉 ALL FIXES TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {report['failed_tests'] if report else 'Unknown'} TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()