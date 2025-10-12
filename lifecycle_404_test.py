#!/usr/bin/env python3
"""
Focused test for Function 5 (Content Lifecycle Management) endpoints returning 404
Testing specific endpoints mentioned in the review request.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import time
import os
from typing import Dict, Any, List

class Lifecycle404Tester:
    def __init__(self):
        # Get backend URL from environment
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
            else:
                self.base_url = "https://bme-profile-boost.preview.emergentagent.com"
        
        self.api_base = f"{self.base_url}/api"
        
        # Test user credentials
        self.test_user = {
            "email": "lifecycle404.tester@bigmannentertainment.com",
            "password": "Lifecycle404Test2025!",
            "full_name": "Lifecycle 404 Test User",
            "business_name": "Lifecycle 404 Testing Co",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Lifecycle St",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
        self.auth_token = None
        
        # Test results tracking
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def setup_authentication(self) -> bool:
        """Setup authentication for testing"""
        try:
            # Register test user
            register_response = requests.post(
                f"{self.api_base}/auth/register",
                json=self.test_user,
                timeout=30
            )
            
            if register_response.status_code in [200, 201]:
                print("✅ Test user registered successfully")
            elif register_response.status_code == 400:
                print("ℹ️ Test user already exists, proceeding with login")
            else:
                print(f"⚠️ Registration response: {register_response.status_code}")
            
            # Login to get token
            login_response = requests.post(
                f"{self.api_base}/auth/login",
                json={
                    "email": self.test_user["email"],
                    "password": self.test_user["password"]
                },
                timeout=30
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.auth_token = login_data.get("access_token")
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication setup failed: {e}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    def test_lifecycle_health_check(self):
        """Test GET /api/lifecycle/health - Lifecycle Health Check (Previously 404)"""
        try:
            print(f"\n🔍 Testing: GET {self.api_base}/lifecycle/health")
            
            # Try without authentication first (health checks should be public)
            response = requests.get(
                f"{self.api_base}/lifecycle/health",
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    print(f"   Response Data: {json.dumps(health_data, indent=2)}")
                    
                    if health_data.get("success") and health_data.get("health", {}).get("status") == "healthy":
                        self.log_test(
                            "GET /api/lifecycle/health",
                            True,
                            f"Service healthy with {health_data['health'].get('total_lifecycles', 0)} lifecycles"
                        )
                    else:
                        self.log_test(
                            "GET /api/lifecycle/health",
                            False,
                            "Health check returned unhealthy status",
                            health_data
                        )
                except json.JSONDecodeError:
                    self.log_test(
                        "GET /api/lifecycle/health",
                        False,
                        "Invalid JSON response",
                        response.text
                    )
            elif response.status_code == 403:
                # Try with authentication if 403
                print("   Trying with authentication...")
                response = requests.get(
                    f"{self.api_base}/lifecycle/health",
                    headers=self.get_headers(),
                    timeout=30
                )
                
                print(f"   Authenticated Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        health_data = response.json()
                        print(f"   Authenticated Response: {json.dumps(health_data, indent=2)}")
                        
                        if health_data.get("success") and health_data.get("health", {}).get("status") == "healthy":
                            self.log_test(
                                "GET /api/lifecycle/health",
                                True,
                                f"Service healthy with auth - {health_data['health'].get('total_lifecycles', 0)} lifecycles"
                            )
                        else:
                            self.log_test(
                                "GET /api/lifecycle/health",
                                False,
                                "Health check returned unhealthy status with auth",
                                health_data
                            )
                    except json.JSONDecodeError:
                        self.log_test(
                            "GET /api/lifecycle/health",
                            False,
                            "Invalid JSON response with auth",
                            response.text
                        )
                else:
                    self.log_test(
                        "GET /api/lifecycle/health",
                        False,
                        f"HTTP {response.status_code} even with auth",
                        response.text
                    )
            else:
                self.log_test(
                    "GET /api/lifecycle/health",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("GET /api/lifecycle/health", False, f"Exception: {e}")

    def test_lifecycle_dashboard(self):
        """Test GET /api/lifecycle/dashboard - Lifecycle Dashboard (Previously 404)"""
        try:
            print(f"\n🔍 Testing: GET {self.api_base}/lifecycle/dashboard")
            
            response = requests.get(
                f"{self.api_base}/lifecycle/dashboard",
                headers=self.get_headers(),
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    dashboard_data = response.json()
                    print(f"   Response Data: {json.dumps(dashboard_data, indent=2)}")
                    
                    if dashboard_data.get("success") and "dashboard" in dashboard_data:
                        dashboard = dashboard_data["dashboard"]
                        self.log_test(
                            "GET /api/lifecycle/dashboard",
                            True,
                            f"Dashboard loaded with {dashboard.get('total_content_pieces', 0)} content pieces"
                        )
                    else:
                        self.log_test(
                            "GET /api/lifecycle/dashboard",
                            False,
                            "Dashboard response missing required fields",
                            dashboard_data
                        )
                except json.JSONDecodeError:
                    self.log_test(
                        "GET /api/lifecycle/dashboard",
                        False,
                        "Invalid JSON response",
                        response.text
                    )
            elif response.status_code == 403:
                self.log_test(
                    "GET /api/lifecycle/dashboard",
                    False,
                    "Authentication required (403 Forbidden)",
                    response.text
                )
            else:
                self.log_test(
                    "GET /api/lifecycle/dashboard",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("GET /api/lifecycle/dashboard", False, f"Exception: {e}")

    def test_lifecycle_enums(self):
        """Test GET /api/lifecycle/enums - Lifecycle Enums (Previously 404)"""
        try:
            print(f"\n🔍 Testing: GET {self.api_base}/lifecycle/enums")
            
            response = requests.get(
                f"{self.api_base}/lifecycle/enums",
                headers=self.get_headers(),
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Response Data: {json.dumps(result, indent=2)}")
                    
                    if result.get("success") and "enums" in result:
                        enums = result["enums"]
                        expected_keys = ["content_statuses", "lifecycle_stages", "automation_triggers", "action_types"]
                        has_all_keys = all(key in enums for key in expected_keys)
                        
                        self.log_test(
                            "GET /api/lifecycle/enums",
                            has_all_keys,
                            f"Retrieved enums: {list(enums.keys())}"
                        )
                    else:
                        self.log_test(
                            "GET /api/lifecycle/enums",
                            False,
                            "Response missing required fields",
                            result
                        )
                except json.JSONDecodeError:
                    self.log_test(
                        "GET /api/lifecycle/enums",
                        False,
                        "Invalid JSON response",
                        response.text
                    )
            else:
                self.log_test(
                    "GET /api/lifecycle/enums",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("GET /api/lifecycle/enums", False, f"Exception: {e}")

    def test_working_lifecycle_automation_rules(self):
        """Test GET /api/lifecycle/automation/rules - Working endpoint for comparison"""
        try:
            print(f"\n🔍 Testing: GET {self.api_base}/lifecycle/automation/rules (Working endpoint)")
            
            response = requests.get(
                f"{self.api_base}/lifecycle/automation/rules",
                headers=self.get_headers(),
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Response Data: {json.dumps(result, indent=2)}")
                    
                    if result.get("success") and "automation_rules" in result:
                        rules = result["automation_rules"]
                        self.log_test(
                            "GET /api/lifecycle/automation/rules",
                            True,
                            f"Retrieved {len(rules)} automation rules"
                        )
                    else:
                        self.log_test(
                            "GET /api/lifecycle/automation/rules",
                            False,
                            "Response missing required fields",
                            result
                        )
                except json.JSONDecodeError:
                    self.log_test(
                        "GET /api/lifecycle/automation/rules",
                        False,
                        "Invalid JSON response",
                        response.text
                    )
            else:
                self.log_test(
                    "GET /api/lifecycle/automation/rules",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("GET /api/lifecycle/automation/rules", False, f"Exception: {e}")

    def test_working_lifecycle_list(self):
        """Test GET /api/lifecycle/ - Working endpoint for comparison"""
        try:
            print(f"\n🔍 Testing: GET {self.api_base}/lifecycle/ (Working endpoint)")
            
            response = requests.get(
                f"{self.api_base}/lifecycle/",
                headers=self.get_headers(),
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Response Data: {json.dumps(result, indent=2)}")
                    
                    if result.get("success") and "lifecycles" in result:
                        lifecycles = result["lifecycles"]
                        self.log_test(
                            "GET /api/lifecycle/",
                            True,
                            f"Retrieved {len(lifecycles)} lifecycles"
                        )
                    else:
                        self.log_test(
                            "GET /api/lifecycle/",
                            False,
                            "Response missing required fields",
                            result
                        )
                except json.JSONDecodeError:
                    self.log_test(
                        "GET /api/lifecycle/",
                        False,
                        "Invalid JSON response",
                        response.text
                    )
            else:
                self.log_test(
                    "GET /api/lifecycle/",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("GET /api/lifecycle/", False, f"Exception: {e}")

    def run_focused_tests(self):
        """Run focused tests on the specific 404 endpoints"""
        print("🎯 FUNCTION 5: LIFECYCLE MANAGEMENT 404 ENDPOINTS TESTING")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print()
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        print("\n📋 TESTING PREVIOUSLY 404 ENDPOINTS:")
        print("-" * 50)
        
        # Test the 3 specific endpoints that were returning 404
        self.test_lifecycle_health_check()
        self.test_lifecycle_dashboard()
        self.test_lifecycle_enums()
        
        print("\n📋 TESTING WORKING ENDPOINTS FOR COMPARISON:")
        print("-" * 50)
        
        # Test working endpoints for comparison
        self.test_working_lifecycle_automation_rules()
        self.test_working_lifecycle_list()
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 LIFECYCLE 404 ENDPOINTS TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Separate 404 endpoints from working endpoints
        problem_endpoints = [
            "GET /api/lifecycle/health",
            "GET /api/lifecycle/dashboard", 
            "GET /api/lifecycle/enums"
        ]
        
        working_endpoints = [
            "GET /api/lifecycle/automation/rules",
            "GET /api/lifecycle/"
        ]
        
        print(f"\n❌ PREVIOUSLY 404 ENDPOINTS:")
        print("-" * 40)
        for result in self.test_results:
            if result["test"] in problem_endpoints:
                status = "✅ FIXED" if result["success"] else "❌ STILL FAILING"
                print(f"• {result['test']}: {status} - {result['details']}")
        
        print(f"\n✅ WORKING ENDPOINTS (FOR COMPARISON):")
        print("-" * 40)
        for result in self.test_results:
            if result["test"] in working_endpoints:
                status = "✅ WORKING" if result["success"] else "❌ BROKEN"
                print(f"• {result['test']}: {status} - {result['details']}")
        
        print("\n🔍 ROUTING ANALYSIS:")
        print("-" * 40)
        problem_count = len([r for r in self.test_results if r["test"] in problem_endpoints and not r["success"]])
        working_count = len([r for r in self.test_results if r["test"] in working_endpoints and r["success"]])
        
        if problem_count > 0 and working_count > 0:
            print("• Some lifecycle endpoints work while others return 404")
            print("• This suggests a routing configuration issue")
            print("• The lifecycle router may have incorrect prefix or inclusion")
        elif problem_count == 0:
            print("• All previously 404 endpoints are now working!")
        else:
            print("• All lifecycle endpoints appear to have issues")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = Lifecycle404Tester()
    tester.run_focused_tests()