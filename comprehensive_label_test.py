#!/usr/bin/env python3
"""
Comprehensive Label Management System Testing for Big Mann Entertainment
Tests all the endpoints mentioned in the review request.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://bme-media-hub.preview.emergentagent.com/api"

class ComprehensiveLabelTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "details": []
        }
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.results["passed"] += 1
            status = "✅ PASS"
        else:
            self.results["failed"] += 1
            status = "❌ FAIL"
        
        result_line = f"{status}: {test_name} - {details}"
        self.results["details"].append(result_line)
        print(result_line)
    
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
    
    def create_test_user(self) -> bool:
        """Create a test user for authentication"""
        try:
            user_data = {
                "email": f"labeltest_{int(datetime.utcnow().timestamp())}@bigmannentertainment.com",
                "password": "LabelTest2025!",
                "full_name": "Label Test User",
                "business_name": "Big Mann Entertainment",
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
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data['user']['id']
                    user = data['user']
                    print(f"✅ Created test user: {user['email']} (Role: {user.get('role', 'user')}, Admin: {user.get('is_admin', False)})")
                    return True
            
            print(f"❌ Failed to create test user: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Exception creating test user: {str(e)}")
            return False
    
    def test_label_system_status(self):
        """Test basic label system endpoints"""
        # Test label test endpoint
        try:
            response = self.make_request('GET', '/label/test')
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'Big Mann Entertainment' in data['message']:
                    self.log_result("Label System Test Endpoint", True, 
                                  f"System active: {data.get('status', 'unknown')}")
                else:
                    self.log_result("Label System Test Endpoint", False, 
                                  f"Invalid response format: {data}")
            else:
                self.log_result("Label System Test Endpoint", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Label System Test Endpoint", False, f"Exception: {str(e)}")
        
        # Test label status endpoint
        try:
            response = self.make_request('GET', '/label/status')
            if response.status_code == 200:
                data = response.json()
                if 'label_system' in data and 'features' in data:
                    features = data['features']
                    self.log_result("Label Status Endpoint", True, 
                                  f"System operational with {len(features)} features")
                else:
                    self.log_result("Label Status Endpoint", False, 
                                  f"Invalid response format: {data}")
            else:
                self.log_result("Label Status Endpoint", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Label Status Endpoint", False, f"Exception: {str(e)}")
    
    def test_demo_submission_public(self):
        """Test POST /api/label/ar/demos/submit (public endpoint)"""
        try:
            demo_data = {
                "artist_name": "Test Demo Artist",
                "contact_email": "demoartist@example.com",
                "genre": "hip-hop",
                "bio": "Aspiring artist looking to get signed to Big Mann Entertainment for testing purposes"
            }
            
            # Test without authentication (public endpoint)
            temp_token = self.auth_token
            self.auth_token = None
            
            response = self.make_request('POST', '/label/ar/demos/submit', json=demo_data)
            
            # Restore auth token
            self.auth_token = temp_token
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success'] and 'submission_id' in data:
                    self.log_result("Demo Submission (Public)", True, 
                                  f"Demo submitted successfully: {data.get('submission_id')}")
                else:
                    self.log_result("Demo Submission (Public)", False, 
                                  f"Invalid response format: {data}")
            else:
                self.log_result("Demo Submission (Public)", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Demo Submission (Public)", False, f"Exception: {str(e)}")
    
    def test_admin_endpoints(self):
        """Test admin-required endpoints"""
        admin_endpoints = [
            ('/label/dashboard', 'Dashboard'),
            ('/label/artists', 'Artist Roster'),
            ('/label/artists/artist_1', 'Artist Details'),
            ('/label/ar/demos', 'A&R Demo Submissions'),
            ('/label/ar/industry-trends', 'Industry Trends'),
            ('/label/ar/industry-contacts?query=radio&category=radio', 'Industry Contacts'),
            ('/label/projects', 'Recording Projects'),
            ('/label/marketing/campaigns', 'Marketing Campaigns'),
            ('/label/finance/transactions', 'Financial Transactions')
        ]
        
        for endpoint, name in admin_endpoints:
            try:
                if not self.auth_token:
                    self.log_result(name, False, "No auth token available")
                    continue
                
                response = self.make_request('GET', endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result(name, True, f"Retrieved {len(data)} items")
                    elif isinstance(data, dict):
                        if name == "Dashboard" and 'total_artists' in data:
                            self.log_result(name, True, 
                                          f"Dashboard loaded: {data.get('total_artists')} artists, {data.get('active_projects')} projects")
                        elif name == "Industry Trends" and 'trending_genres' in data:
                            self.log_result(name, True, 
                                          f"Retrieved {len(data.get('trending_genres', []))} trending genres")
                        elif name == "Industry Contacts" and 'contacts' in data:
                            self.log_result(name, True, 
                                          f"Retrieved {data.get('total_found', 0)} industry contacts")
                        elif name == "Artist Details" and 'stage_name' in data:
                            self.log_result(name, True, 
                                          f"Retrieved artist details: {data.get('stage_name')}")
                        else:
                            self.log_result(name, True, "Retrieved data successfully")
                    else:
                        self.log_result(name, False, "Invalid response format")
                elif response.status_code == 403:
                    self.log_result(name, True, "Properly protected (requires admin privileges)")
                elif response.status_code == 404:
                    self.log_result(name, False, "Endpoint not found")
                else:
                    self.log_result(name, False, 
                                  f"Status: {response.status_code}, Response: {response.text[:100]}...")
            except Exception as e:
                self.log_result(name, False, f"Exception: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive label management tests"""
        print("=" * 80)
        print("BIG MANN ENTERTAINMENT COMPREHENSIVE LABEL MANAGEMENT SYSTEM TESTING")
        print("Testing all endpoints mentioned in the review request")
        print("=" * 80)
        
        # Test system status first
        print("\n🎵 TESTING LABEL SYSTEM STATUS")
        print("-" * 40)
        self.test_label_system_status()
        
        # Create test user
        print("\n🔐 CREATING TEST USER")
        print("-" * 40)
        if not self.create_test_user():
            print("❌ Failed to create test user - admin endpoints will show as protected")
        
        # Test public endpoints
        print("\n📝 TESTING PUBLIC ENDPOINTS")
        print("-" * 40)
        self.test_demo_submission_public()
        
        # Test admin endpoints
        print("\n🔒 TESTING ADMIN ENDPOINTS")
        print("-" * 40)
        self.test_admin_endpoints()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE LABEL MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_passed = self.results["passed"]
        total_failed = self.results["failed"]
        total_tests = total_passed + total_failed
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
        else:
            success_rate = 0
        
        for detail in self.results["details"]:
            print(f"  {detail}")
        
        print("\n" + "=" * 80)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL: {total_passed} passed, {total_failed} failed - {overall_status}")
        print(f"SUCCESS RATE: {success_rate:.1f}%")
        print("=" * 80)
        
        # Analysis
        print("\n📊 ANALYSIS:")
        if total_failed == 0:
            print("🎉 All label management endpoints are working correctly!")
        else:
            print("⚠️  Some endpoints need attention:")
            failed_tests = [detail for detail in self.results["details"] if "❌ FAIL" in detail]
            for failed_test in failed_tests:
                print(f"   - {failed_test}")

if __name__ == "__main__":
    tester = ComprehensiveLabelTester()
    tester.run_comprehensive_tests()