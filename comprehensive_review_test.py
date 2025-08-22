#!/usr/bin/env python3
"""
Comprehensive Review Testing Suite for Big Mann Entertainment Platform
Tests ALL previously broken endpoints and UPC/ISRC generation functionality
Based on the specific review request for 100% platform functionality verification
"""

import requests
import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://bme-media-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"review.test.{uuid.uuid4().hex[:8]}@bigmannentertainment.com"
TEST_USER_PASSWORD = "BigMannReview2025!"
TEST_USER_NAME = "Big Mann Review Tester"
TEST_BUSINESS_NAME = "Big Mann Entertainment"

class ComprehensiveReviewTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.admin_token = None
        self.test_user_id = None
        self.results = {
            "previously_broken_endpoints": {"passed": 0, "failed": 0, "details": []},
            "upc_isrc_generation": {"passed": 0, "failed": 0, "details": []},
            "authentication_system": {"passed": 0, "failed": 0, "details": []},
            "core_functionality": {"passed": 0, "failed": 0, "details": []}
        }
    
    def log_result(self, category: str, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results[category]["failed"] += 1
            status = "❌ FAIL"
        
        self.results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
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
                "full_name": TEST_USER_NAME,
                "business_name": TEST_BUSINESS_NAME,
                "date_of_birth": (datetime.utcnow() - timedelta(days=25*365)).isoformat(),
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
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                # Try login instead
                login_data = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
                login_response = self.make_request('POST', '/auth/login', json=login_data)
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.auth_token = data.get('access_token')
                    self.test_user_id = data.get('user', {}).get('id')
                    return True
            
            return False
            
        except Exception as e:
            print(f"Authentication setup failed: {e}")
            return False
    
    def test_previously_broken_endpoints(self) -> bool:
        """Test all previously broken endpoints that returned 404 errors"""
        previously_broken_endpoints = [
            ('/business/products', 'GET', 'Business Products Listing'),
            ('/tax/dashboard', 'GET', 'Tax Dashboard Data'),
            ('/tax/1099-generation', 'GET', '1099 Form Data'),
            ('/tax/reporting', 'GET', 'Tax Reporting Data'),
            ('/label/dashboard', 'GET', 'Label Dashboard'),
            ('/label/artists', 'GET', 'Artist Listings'),
            ('/label/contracts', 'GET', 'Contract Data'),
            ('/label/analytics', 'GET', 'Label Analytics'),
            ('/payments/checkout', 'GET', 'Payment Checkout Info'),
            ('/gs1/business-info', 'GET', 'GS1 Business Data'),
            ('/gs1/products', 'GET', 'GS1 Product Data'),
            ('/gs1/locations', 'GET', 'GS1 Location Data'),
            ('/gs1/validation', 'GET', 'GS1 Validation Results'),
            ('/admin/content/pending', 'GET', 'Pending Content'),
            ('/admin/content/reported', 'GET', 'Reported Content'),
            ('/sponsorship/analytics', 'GET', 'Sponsorship Analytics')
        ]
        
        all_working = True
        working_count = 0
        
        for endpoint, method, description in previously_broken_endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 404:
                    self.log_result("previously_broken_endpoints", description, False, 
                                  f"Still returns 404 - endpoint not fixed: {endpoint}")
                    all_working = False
                elif response.status_code in [200, 401, 403]:
                    # 200 = working, 401/403 = working but needs auth (expected for protected routes)
                    self.log_result("previously_broken_endpoints", description, True, 
                                  f"Endpoint fixed - returns {response.status_code}: {endpoint}")
                    working_count += 1
                elif response.status_code == 422:
                    # Validation error - endpoint exists but needs proper data
                    self.log_result("previously_broken_endpoints", description, True, 
                                  f"Endpoint fixed - validation error (needs data): {endpoint}")
                    working_count += 1
                elif response.status_code == 500:
                    self.log_result("previously_broken_endpoints", description, False, 
                                  f"Server error - endpoint may have issues: {endpoint}")
                    all_working = False
                else:
                    self.log_result("previously_broken_endpoints", description, True, 
                                  f"Endpoint responding (status {response.status_code}): {endpoint}")
                    working_count += 1
                    
            except Exception as e:
                self.log_result("previously_broken_endpoints", description, False, 
                              f"Exception testing {endpoint}: {str(e)}")
                all_working = False
        
        # Overall result
        total_endpoints = len(previously_broken_endpoints)
        if working_count == total_endpoints:
            self.log_result("previously_broken_endpoints", "All Previously Broken Endpoints", True, 
                          f"All {total_endpoints} endpoints now working correctly")
        else:
            self.log_result("previously_broken_endpoints", "All Previously Broken Endpoints", False, 
                          f"Only {working_count}/{total_endpoints} endpoints working")
        
        return all_working
    
    def test_upc_generation(self) -> bool:
        """Test UPC generation with proper form data"""
        try:
            if not self.auth_token:
                self.log_result("upc_isrc_generation", "UPC Generation", False, "No auth token available")
                return False
            
            # Test UPC generation with proper form data
            upc_data = {
                'product_name': 'Big Mann Entertainment Test Album',
                'artist_name': 'Big Mann Artist',
                'album_title': 'Test Album 2025',
                'product_category': 'music_album',
                'release_date': datetime.utcnow().isoformat(),
                'record_label': 'Big Mann Entertainment'
            }
            
            response = self.make_request('POST', '/business/generate-upc', data=upc_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'upc' in data and 'gtin' in data:
                    upc_code = data['upc']
                    gtin = data['gtin']
                    
                    # Validate UPC format (12 digits)
                    if len(upc_code) == 12 and upc_code.isdigit():
                        self.log_result("upc_isrc_generation", "UPC Generation", True, 
                                      f"Successfully generated UPC: {upc_code}, GTIN: {gtin}")
                        return True
                    else:
                        self.log_result("upc_isrc_generation", "UPC Generation", False, 
                                      f"Invalid UPC format: {upc_code}")
                        return False
                else:
                    self.log_result("upc_isrc_generation", "UPC Generation", False, 
                                  f"Missing UPC or GTIN in response: {list(data.keys())}")
                    return False
            elif response.status_code == 422:
                self.log_result("upc_isrc_generation", "UPC Generation", False, 
                              f"Validation error (422) - form data issues: {response.text}")
                return False
            else:
                self.log_result("upc_isrc_generation", "UPC Generation", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("upc_isrc_generation", "UPC Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_isrc_generation(self) -> bool:
        """Test ISRC generation with proper form data"""
        try:
            if not self.auth_token:
                self.log_result("upc_isrc_generation", "ISRC Generation", False, "No auth token available")
                return False
            
            # Test ISRC generation with proper form data
            isrc_data = {
                'track_title': 'Big Mann Entertainment Test Track',
                'artist_name': 'Big Mann Artist',
                'album_title': 'Test Album 2025',
                'duration_seconds': 180,
                'release_date': datetime.utcnow().isoformat(),
                'record_label': 'Big Mann Entertainment',
                'publisher_name': 'Big Mann Publishing',
                'songwriter_credits': 'Big Mann Songwriter'
            }
            
            response = self.make_request('POST', '/business/generate-isrc', data=isrc_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'isrc_code' in data:
                    isrc_code = data['isrc_code']
                    
                    # Validate ISRC format (12 characters with dashes: CC-XXX-YY-NNNNN)
                    if len(isrc_code) == 12 and isrc_code.count('-') == 3:
                        self.log_result("upc_isrc_generation", "ISRC Generation", True, 
                                      f"Successfully generated ISRC: {isrc_code}")
                        return True
                    else:
                        self.log_result("upc_isrc_generation", "ISRC Generation", False, 
                                      f"Invalid ISRC format: {isrc_code}")
                        return False
                else:
                    self.log_result("upc_isrc_generation", "ISRC Generation", False, 
                                  f"Missing ISRC in response: {list(data.keys())}")
                    return False
            elif response.status_code == 422:
                self.log_result("upc_isrc_generation", "ISRC Generation", False, 
                              f"Validation error (422) - form data issues: {response.text}")
                return False
            else:
                self.log_result("upc_isrc_generation", "ISRC Generation", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("upc_isrc_generation", "ISRC Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_system(self) -> bool:
        """Test authentication system functionality"""
        try:
            # Test login
            login_data = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
            response = self.make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.log_result("authentication_system", "User Login", True, 
                                  "Authentication system working correctly")
                    
                    # Test protected route access
                    me_response = self.make_request('GET', '/auth/me')
                    if me_response.status_code == 200:
                        self.log_result("authentication_system", "Protected Route Security", True, 
                                      "Protected routes working with JWT authentication")
                        
                        # Test email system (forgot password)
                        forgot_data = {"email": TEST_USER_EMAIL}
                        forgot_response = self.make_request('POST', '/auth/forgot-password', json=forgot_data)
                        
                        if forgot_response.status_code == 200:
                            forgot_result = forgot_response.json()
                            if 'reset_token' in forgot_result:
                                self.log_result("authentication_system", "Email System", True, 
                                              "Email system functional with password reset")
                                return True
                            else:
                                self.log_result("authentication_system", "Email System", False, 
                                              "Email system not providing reset tokens")
                                return False
                        else:
                            self.log_result("authentication_system", "Email System", False, 
                                          f"Forgot password failed: {forgot_response.status_code}")
                            return False
                    else:
                        self.log_result("authentication_system", "Protected Route Security", False, 
                                      "Protected routes not working properly")
                        return False
                else:
                    self.log_result("authentication_system", "User Login", False, 
                                  "Login response missing required fields")
                    return False
            else:
                self.log_result("authentication_system", "User Login", False, 
                              f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("authentication_system", "Authentication System", False, f"Exception: {str(e)}")
            return False
    
    def test_core_functionality(self) -> bool:
        """Test core platform functionality"""
        try:
            if not self.auth_token:
                self.log_result("core_functionality", "Core Functionality", False, "No auth token available")
                return False
            
            # Test distribution platforms (90+ platforms)
            platforms_response = self.make_request('GET', '/distribution/platforms')
            
            if platforms_response.status_code == 200:
                platforms_data = platforms_response.json()
                if 'platforms' in platforms_data:
                    platform_count = len(platforms_data['platforms'])
                    if platform_count >= 90:
                        self.log_result("core_functionality", "Distribution System", True, 
                                      f"Distribution system working with {platform_count} platforms")
                    else:
                        self.log_result("core_functionality", "Distribution System", False, 
                                      f"Only {platform_count} platforms available (expected 90+)")
                        return False
                else:
                    self.log_result("core_functionality", "Distribution System", False, 
                                  "Platforms data not in expected format")
                    return False
            else:
                self.log_result("core_functionality", "Distribution System", False, 
                              f"Distribution platforms endpoint failed: {platforms_response.status_code}")
                return False
            
            # Test business identifiers
            business_response = self.make_request('GET', '/business/identifiers')
            
            if business_response.status_code == 200:
                business_data = business_response.json()
                if 'business_ein' in business_data:
                    self.log_result("core_functionality", "Business Identifiers", True, 
                                  f"Business identifiers working - EIN: {business_data['business_ein']}")
                else:
                    self.log_result("core_functionality", "Business Identifiers", False, 
                                  "Business identifiers missing required fields")
                    return False
            else:
                self.log_result("core_functionality", "Business Identifiers", False, 
                              f"Business identifiers failed: {business_response.status_code}")
                return False
            
            # Test media management (library access)
            library_response = self.make_request('GET', '/media/library')
            
            if library_response.status_code == 200:
                self.log_result("core_functionality", "Media Management", True, 
                              "Media management system accessible")
            else:
                self.log_result("core_functionality", "Media Management", False, 
                              f"Media library access failed: {library_response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("core_functionality", "Core Functionality", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_review_tests(self):
        """Run all comprehensive review tests"""
        print("🎯 STARTING COMPREHENSIVE REVIEW TESTING FOR BIG MANN ENTERTAINMENT PLATFORM")
        print("=" * 80)
        
        # Setup authentication
        print("\n📋 Setting up authentication...")
        if not self.setup_authentication():
            print("❌ Authentication setup failed - cannot proceed with tests")
            return
        
        print(f"✅ Authentication setup successful - Token: {self.auth_token[:20]}...")
        
        # Test 1: Previously Broken Endpoints
        print("\n🔍 Testing Previously Broken Endpoints (404 errors)...")
        self.test_previously_broken_endpoints()
        
        # Test 2: UPC/ISRC Generation
        print("\n🏷️ Testing UPC/ISRC Generation...")
        self.test_upc_generation()
        self.test_isrc_generation()
        
        # Test 3: Authentication System
        print("\n🔐 Testing Authentication System...")
        self.test_authentication_system()
        
        # Test 4: Core Functionality
        print("\n⚙️ Testing Core Functionality...")
        self.test_core_functionality()
        
        # Print comprehensive results
        self.print_comprehensive_results()
    
    def print_comprehensive_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE REVIEW TEST RESULTS")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n📊 {category.replace('_', ' ').title()}:")
            print(f"   ✅ Passed: {passed}")
            print(f"   ❌ Failed: {failed}")
            print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "   📈 Success Rate: N/A")
            
            # Show details for failed tests
            if failed > 0:
                print("   🔍 Failed Test Details:")
                for detail in results["details"]:
                    if "❌ FAIL" in detail:
                        print(f"      {detail}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   ✅ Total Passed: {total_passed}")
        print(f"   ❌ Total Failed: {total_failed}")
        print(f"   📈 Overall Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%" if (total_passed+total_failed) > 0 else "   📈 Overall Success Rate: N/A")
        
        if total_failed == 0:
            print("\n🎉 ALL TESTS PASSED - BIG MANN ENTERTAINMENT PLATFORM 100% FUNCTIONAL!")
        else:
            print(f"\n⚠️ {total_failed} TESTS FAILED - PLATFORM NEEDS ATTENTION")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = ComprehensiveReviewTester()
    tester.run_comprehensive_review_tests()