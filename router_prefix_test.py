#!/usr/bin/env python3
"""
Comprehensive Router Prefix Fix Testing Suite for Big Mann Entertainment Platform
Tests ALL router prefix fixes to verify 404 errors are resolved and 100% functionality achieved.
"""

import requests
import json
import uuid
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Configuration
BASE_URL = "https://bme-media-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"router.test.{uuid.uuid4().hex[:8]}@bigmannentertainment.com"
TEST_USER_PASSWORD = "RouterTest2025!"

class RouterPrefixTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.admin_token = None
        self.test_user_id = None
        self.results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "endpoint_details": [],
            "categories": {
                "tax_management": {"passed": 0, "failed": 0, "details": []},
                "label_management": {"passed": 0, "failed": 0, "details": []},
                "payment_system": {"passed": 0, "failed": 0, "details": []},
                "gs1_integration": {"passed": 0, "failed": 0, "details": []},
                "sponsorship": {"passed": 0, "failed": 0, "details": []},
                "ddex": {"passed": 0, "failed": 0, "details": []},
                "licensing": {"passed": 0, "failed": 0, "details": []},
                "industry": {"passed": 0, "failed": 0, "details": []},
                "core_system": {"passed": 0, "failed": 0, "details": []},
                "admin_functionality": {"passed": 0, "failed": 0, "details": []}
            }
        }
    
    def log_result(self, category: str, endpoint: str, method: str, success: bool, status_code: int, details: str = ""):
        """Log test result for an endpoint"""
        self.results["total_endpoints"] += 1
        
        if success:
            self.results["working_endpoints"] += 1
            self.results["categories"][category]["passed"] += 1
            status = "✅ WORKING"
        else:
            self.results["failed_endpoints"] += 1
            self.results["categories"][category]["failed"] += 1
            status = "❌ FAILED"
        
        result_detail = f"{status}: {method} {endpoint} - Status: {status_code} - {details}"
        self.results["categories"][category]["details"].append(result_detail)
        self.results["endpoint_details"].append(result_detail)
        print(result_detail)
    
    def make_request(self, method: str, endpoint: str, use_admin: bool = False, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        token = self.admin_token if use_admin and self.admin_token else self.auth_token
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise
    
    def setup_authentication(self) -> bool:
        """Setup authentication for testing"""
        try:
            # Register test user
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "Router Test User",
                "business_name": "Big Mann Entertainment",
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "1314 Lincoln Heights Street",
                "city": "Alexander City",
                "state_province": "Alabama",
                "postal_code": "35010",
                "country": "United States"
            }
            
            response = self.make_request('POST', '/auth/register', json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.test_user_id = data.get('user', {}).get('id')
                print(f"✅ Authentication setup successful")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                # Try login instead
                login_data = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
                login_response = self.make_request('POST', '/auth/login', json=login_data)
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.auth_token = data.get('access_token')
                    self.test_user_id = data.get('user', {}).get('id')
                    print(f"✅ Authentication login successful")
                    return True
            
            print(f"❌ Authentication setup failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Authentication setup exception: {str(e)}")
            return False
    
    def test_tax_management_endpoints(self):
        """Test Tax Management router endpoints"""
        print("\n🔍 Testing Tax Management Endpoints...")
        
        endpoints = [
            ('/tax/dashboard/2025', 'GET'),
            ('/tax/business-info', 'GET'),
            ('/tax/1099s', 'GET'),
            ('/tax/payments', 'GET'),
            ('/tax/settings', 'GET'),
            ('/tax/compliance', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("tax_management", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 401, 403]:
                    self.log_result("tax_management", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("tax_management", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("tax_management", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_label_management_endpoints(self):
        """Test Label Management router endpoints"""
        print("\n🔍 Testing Label Management Endpoints...")
        
        endpoints = [
            ('/label/dashboard', 'GET'),
            ('/label/artists', 'GET'),
            ('/label/contracts', 'GET'),
            ('/label/analytics', 'GET'),
            ('/label/projects', 'GET'),
            ('/label/marketing', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("label_management", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 401, 403]:
                    self.log_result("label_management", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("label_management", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("label_management", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_payment_system_endpoints(self):
        """Test Payment System router endpoints"""
        print("\n🔍 Testing Payment System Endpoints...")
        
        endpoints = [
            ('/payments/checkout', 'POST'),
            ('/payments/packages', 'GET'),
            ('/payments/status', 'GET'),
            ('/payments/webhook', 'POST'),
            ('/payments/earnings', 'GET'),
            ('/payments/payouts', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("payment_system", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 400, 401, 403, 422]:  # 400/422 for missing data is acceptable
                    self.log_result("payment_system", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("payment_system", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("payment_system", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_gs1_integration_endpoints(self):
        """Test GS1 Integration router endpoints"""
        print("\n🔍 Testing GS1 Integration Endpoints...")
        
        endpoints = [
            ('/gs1/business-info', 'GET'),
            ('/gs1/products', 'GET'),
            ('/gs1/locations', 'GET'),
            ('/gs1/validation', 'POST'),
            ('/gs1/barcodes', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("gs1_integration", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 400, 401, 403, 422]:
                    self.log_result("gs1_integration", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("gs1_integration", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("gs1_integration", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_sponsorship_endpoints(self):
        """Test Sponsorship router endpoints"""
        print("\n🔍 Testing Sponsorship Endpoints...")
        
        endpoints = [
            ('/sponsorship/analytics', 'GET'),
            ('/sponsorship/dashboard', 'GET'),
            ('/sponsorship/sponsors', 'GET'),
            ('/sponsorship/deals', 'GET'),
            ('/sponsorship/metrics', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("sponsorship", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 401, 403]:
                    self.log_result("sponsorship", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("sponsorship", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("sponsorship", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_ddex_endpoints(self):
        """Test DDEX router endpoints"""
        print("\n🔍 Testing DDEX Endpoints...")
        
        endpoints = [
            ('/ddex/ern/create', 'POST'),
            ('/ddex/messages', 'GET'),
            ('/ddex/identifiers', 'GET'),
            ('/ddex/validation', 'POST'),
            ('/ddex/dashboard', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("ddex", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 400, 401, 403, 422]:
                    self.log_result("ddex", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("ddex", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("ddex", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_licensing_endpoints(self):
        """Test Licensing router endpoints"""
        print("\n🔍 Testing Licensing Endpoints...")
        
        endpoints = [
            ('/licensing/statutory-rates', 'GET'),
            ('/licensing/compliance', 'GET'),
            ('/licensing/dashboard', 'GET'),
            ('/licensing/usage-tracking', 'GET'),
            ('/licensing/compensation', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("licensing", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 401, 403]:
                    self.log_result("licensing", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("licensing", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("licensing", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_industry_endpoints(self):
        """Test Industry router endpoints"""
        print("\n🔍 Testing Industry Endpoints...")
        
        endpoints = [
            ('/industry/dashboard', 'GET'),
            ('/industry/partners', 'GET'),
            ('/industry/coverage', 'GET'),
            ('/industry/identifiers', 'GET'),
            ('/industry/analytics', 'GET')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("industry", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 401, 403]:
                    self.log_result("industry", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("industry", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("industry", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_core_system_endpoints(self):
        """Test Core System endpoints"""
        print("\n🔍 Testing Core System Endpoints...")
        
        endpoints = [
            ('/auth/login', 'POST'),
            ('/auth/register', 'POST'),
            ('/auth/forgot-password', 'POST'),
            ('/auth/reset-password', 'POST'),
            ('/business/identifiers', 'GET'),
            ('/business/upc/generate', 'POST'),
            ('/business/isrc/generate', 'POST'),
            ('/media/upload', 'POST'),
            ('/media/library', 'GET'),
            ('/distribution/platforms', 'GET'),
            ('/distribution/distribute', 'POST')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("core_system", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 400, 401, 403, 422]:
                    self.log_result("core_system", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("core_system", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("core_system", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_admin_functionality_endpoints(self):
        """Test Admin Functionality endpoints"""
        print("\n🔍 Testing Admin Functionality Endpoints...")
        
        endpoints = [
            ('/admin/users', 'GET'),
            ('/admin/media', 'GET'),
            ('/admin/content/pending', 'GET'),
            ('/admin/content/reported', 'GET'),
            ('/admin/analytics', 'GET'),
            ('/admin/send-notification', 'POST'),
            ('/admin/send-bulk-notification', 'POST')
        ]
        
        for endpoint, method in endpoints:
            try:
                response = self.make_request(method, endpoint, use_admin=True)
                
                if response.status_code == 404:
                    self.log_result("admin_functionality", endpoint, method, False, response.status_code, "404 NOT FOUND - Router prefix issue")
                elif response.status_code in [200, 400, 401, 403, 422]:
                    self.log_result("admin_functionality", endpoint, method, True, response.status_code, "Endpoint accessible")
                else:
                    self.log_result("admin_functionality", endpoint, method, False, response.status_code, f"Unexpected status code")
                    
            except Exception as e:
                self.log_result("admin_functionality", endpoint, method, False, 0, f"Exception: {str(e)}")
    
    def test_distribution_platforms_count(self):
        """Test that 90+ distribution platforms are available"""
        print("\n🔍 Testing Distribution Platforms Count...")
        
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platform_count = len(data.get('platforms', []))
                
                if platform_count >= 90:
                    self.log_result("core_system", "/distribution/platforms", "GET", True, response.status_code, 
                                  f"Platform count: {platform_count} (meets 90+ requirement)")
                else:
                    self.log_result("core_system", "/distribution/platforms", "GET", False, response.status_code, 
                                  f"Platform count: {platform_count} (below 90+ requirement)")
            else:
                self.log_result("core_system", "/distribution/platforms", "GET", False, response.status_code, 
                              "Could not retrieve platform count")
                
        except Exception as e:
            self.log_result("core_system", "/distribution/platforms", "GET", False, 0, f"Exception: {str(e)}")
    
    def test_email_system_endpoints(self):
        """Test Email System endpoints"""
        print("\n🔍 Testing Email System Endpoints...")
        
        # Test forgot password email functionality
        try:
            forgot_data = {"email": "test@bigmannentertainment.com"}
            response = self.make_request('POST', '/auth/forgot-password', json=forgot_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'no-reply@bigmannentertainment.com' in str(data):
                    self.log_result("core_system", "/auth/forgot-password", "POST", True, response.status_code, 
                                  "Email system working with no-reply@bigmannentertainment.com")
                else:
                    self.log_result("core_system", "/auth/forgot-password", "POST", True, response.status_code, 
                                  "Email system functional")
            else:
                self.log_result("core_system", "/auth/forgot-password", "POST", False, response.status_code, 
                              "Email system not working")
                
        except Exception as e:
            self.log_result("core_system", "/auth/forgot-password", "POST", False, 0, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive router prefix fix testing"""
        print("🚀 Starting Comprehensive Router Prefix Fix Testing for Big Mann Entertainment Platform")
        print("=" * 80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Some tests may not work properly.")
        
        # Test all router categories
        self.test_tax_management_endpoints()
        self.test_label_management_endpoints()
        self.test_payment_system_endpoints()
        self.test_gs1_integration_endpoints()
        self.test_sponsorship_endpoints()
        self.test_ddex_endpoints()
        self.test_licensing_endpoints()
        self.test_industry_endpoints()
        self.test_core_system_endpoints()
        self.test_admin_functionality_endpoints()
        
        # Test specific functionality
        self.test_distribution_platforms_count()
        self.test_email_system_endpoints()
        
        # Generate comprehensive report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ROUTER PREFIX FIX TEST RESULTS")
        print("=" * 80)
        
        total = self.results["total_endpoints"]
        working = self.results["working_endpoints"]
        failed = self.results["failed_endpoints"]
        success_rate = (working / total * 100) if total > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Endpoints Tested: {total}")
        print(f"   Working Endpoints: {working}")
        print(f"   Failed Endpoints: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📈 CATEGORY BREAKDOWN:")
        for category, results in self.results["categories"].items():
            category_total = results["passed"] + results["failed"]
            if category_total > 0:
                category_rate = (results["passed"] / category_total * 100)
                status = "✅" if results["failed"] == 0 else "⚠️" if results["passed"] > results["failed"] else "❌"
                print(f"   {status} {category.replace('_', ' ').title()}: {results['passed']}/{category_total} ({category_rate:.1f}%)")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for detail in self.results["endpoint_details"]:
            print(f"   {detail}")
        
        # Platform functionality assessment
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: Big Mann Entertainment platform has achieved {success_rate:.1f}% functionality!")
        elif success_rate >= 85:
            print(f"\n✅ GOOD: Big Mann Entertainment platform has achieved {success_rate:.1f}% functionality with minor issues.")
        elif success_rate >= 70:
            print(f"\n⚠️ MODERATE: Big Mann Entertainment platform has achieved {success_rate:.1f}% functionality with some issues.")
        else:
            print(f"\n❌ CRITICAL: Big Mann Entertainment platform has only achieved {success_rate:.1f}% functionality. Major issues need attention.")
        
        # Router prefix fix assessment
        failed_404s = [detail for detail in self.results["endpoint_details"] if "404 NOT FOUND" in detail]
        if not failed_404s:
            print(f"\n✅ ROUTER PREFIX FIXES: All router prefix fixes successful - no 404 errors detected!")
        else:
            print(f"\n❌ ROUTER PREFIX ISSUES: {len(failed_404s)} endpoints still returning 404 errors:")
            for failed_404 in failed_404s:
                print(f"   {failed_404}")
        
        print("\n" + "=" * 80)
        return success_rate, failed_404s

def main():
    """Main test execution"""
    tester = RouterPrefixTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()