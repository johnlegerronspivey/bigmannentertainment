#!/usr/bin/env python3
"""
Function 5: Content Lifecycle Management & Automation System Backend Testing
Testing the lifecycle management endpoints with focus on previously failing areas.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import time
import os
from typing import Dict, Any, List

class Function5LifecycleBackendTester:
    def __init__(self):
        # Get backend URL from environment
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
            else:
                self.base_url = "https://mediahub-dashboard.preview.emergentagent.com"
        
        self.api_base = f"{self.base_url}/api"
        self.lifecycle_base = f"{self.api_base}/lifecycle"
        
        # Test user credentials
        self.test_user = {
            "email": "lifecycle.tester@bigmannentertainment.com",
            "password": "LifecycleTest2025!",
            "full_name": "Lifecycle Test User",
            "business_name": "Lifecycle Testing Co",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Lifecycle St",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
        self.auth_token = None
        self.test_content_id = None
        self.test_version_id = None
        self.test_rule_id = None
        
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
        """Test the lifecycle health check endpoint (Previously 404)"""
        try:
            # Try without authentication first (health checks should be public)
            response = requests.get(
                f"{self.lifecycle_base}/health",
                timeout=30
            )
            
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("success") and health_data.get("health", {}).get("status") == "healthy":
                    self.log_test(
                        "Lifecycle Health Check",
                        True,
                        f"Service healthy with {health_data['health'].get('total_lifecycles', 0)} lifecycles"
                    )
                else:
                    self.log_test(
                        "Lifecycle Health Check",
                        False,
                        "Health check returned unhealthy status",
                        health_data
                    )
            elif response.status_code == 403:
                # Try with authentication if 403
                response = requests.get(
                    f"{self.lifecycle_base}/health",
                    headers=self.get_headers(),
                    timeout=30
                )
                
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("success") and health_data.get("health", {}).get("status") == "healthy":
                        self.log_test(
                            "Lifecycle Health Check",
                            True,
                            f"Service healthy with auth - {health_data['health'].get('total_lifecycles', 0)} lifecycles"
                        )
                    else:
                        self.log_test(
                            "Lifecycle Health Check",
                            False,
                            "Health check returned unhealthy status with auth",
                            health_data
                        )
                else:
                    self.log_test(
                        "Lifecycle Health Check",
                        False,
                        f"HTTP {response.status_code} even with auth",
                        response.text
                    )
            else:
                self.log_test(
                    "Lifecycle Health Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Lifecycle Health Check", False, f"Exception: {e}")

    def test_lifecycle_dashboard(self):
        """Test the lifecycle dashboard endpoint (Previously 404)"""
        try:
            response = requests.get(
                f"{self.lifecycle_base}/dashboard",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                dashboard_data = response.json()
                if dashboard_data.get("success") and "dashboard" in dashboard_data:
                    dashboard = dashboard_data["dashboard"]
                    self.log_test(
                        "Lifecycle Dashboard",
                        True,
                        f"Dashboard loaded with {dashboard.get('total_content_pieces', 0)} content pieces"
                    )
                else:
                    self.log_test(
                        "Lifecycle Dashboard",
                        False,
                        "Dashboard response missing required fields",
                        dashboard_data
                    )
            elif response.status_code == 403:
                self.log_test(
                    "Lifecycle Dashboard",
                    False,
                    "Authentication required (403 Forbidden)",
                    response.text
                )
            else:
                self.log_test(
                    "Lifecycle Dashboard",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Lifecycle Dashboard", False, f"Exception: {e}")

    def test_create_content_lifecycle(self):
        """Test creating a content lifecycle"""
        try:
            self.test_content_id = str(uuid.uuid4())
            
            lifecycle_data = {
                "content_id": self.test_content_id,
                "initial_version": {
                    "title": "Test Music Track for Lifecycle",
                    "description": "A test music track for lifecycle management testing",
                    "file_path": "/test/music/track.mp3",
                    "file_size": 5242880,  # 5MB
                    "file_format": "mp3",
                    "metadata": {
                        "content_type": "music",
                        "genre": "Hip-Hop",
                        "artist": "Test Artist",
                        "duration": 180
                    }
                },
                "policies": ["music_standard"]
            }
            
            response = requests.post(
                f"{self.lifecycle_base}/create",
                headers=self.get_headers(),
                json=lifecycle_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "lifecycle" in result:
                    lifecycle = result["lifecycle"]
                    self.log_test(
                        "Create Content Lifecycle",
                        True,
                        f"Lifecycle created with ID: {lifecycle.get('lifecycle_id')}"
                    )
                else:
                    self.log_test(
                        "Create Content Lifecycle",
                        False,
                        "Response missing required fields",
                        result
                    )
            else:
                self.log_test(
                    "Create Content Lifecycle",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Create Content Lifecycle", False, f"Exception: {e}")

    def test_version_creation(self):
        """Test version creation (Previously 500 error)"""
        try:
            if not self.test_content_id:
                self.log_test("Version Creation", False, "No test content ID available")
                return
            
            version_data = {
                "content_id": self.test_content_id,
                "version_data": {
                    "title": "Test Music Track for Lifecycle - Version 2",
                    "description": "Updated version with improved quality",
                    "file_path": "/test/music/track_v2.mp3",
                    "file_size": 6291456,  # 6MB
                    "file_format": "mp3",
                    "metadata": {
                        "content_type": "music",
                        "genre": "Hip-Hop",
                        "artist": "Test Artist",
                        "duration": 185,
                        "quality": "high"
                    }
                },
                "changes_summary": "Improved audio quality and extended duration",
                "set_as_current": True
            }
            
            response = requests.post(
                f"{self.lifecycle_base}/versions/create",
                headers=self.get_headers(),
                json=version_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "version" in result:
                    version = result["version"]
                    self.test_version_id = version.get("version_id")
                    self.log_test(
                        "Version Creation",
                        True,
                        f"Version created: {version.get('version_number')} (ID: {self.test_version_id})"
                    )
                else:
                    self.log_test(
                        "Version Creation",
                        False,
                        "Response missing required fields",
                        result
                    )
            else:
                self.log_test(
                    "Version Creation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Version Creation", False, f"Exception: {e}")

    def test_create_automation_rule(self):
        """Test creating automation rules"""
        try:
            rule_data = {
                "rule_name": "Auto-Archive Old Content",
                "description": "Automatically archive content that hasn't been viewed in 90 days",
                "trigger_type": "time_based",
                "trigger_conditions": {
                    "days_inactive": 90
                },
                "action_type": "archive_content",
                "action_parameters": {
                    "reason": "Inactive for 90 days"
                },
                "applies_to_content_types": ["music", "video"],
                "applies_to_platforms": ["spotify", "youtube"]
            }
            
            response = requests.post(
                f"{self.lifecycle_base}/automation/rules",
                headers=self.get_headers(),
                json=rule_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "automation_rule" in result:
                    rule = result["automation_rule"]
                    self.test_rule_id = rule.get("rule_id")
                    self.log_test(
                        "Create Automation Rule",
                        True,
                        f"Rule created: {rule.get('rule_name')} (ID: {self.test_rule_id})"
                    )
                else:
                    self.log_test(
                        "Create Automation Rule",
                        False,
                        "Response missing required fields",
                        result
                    )
            else:
                self.log_test(
                    "Create Automation Rule",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Create Automation Rule", False, f"Exception: {e}")

    def test_update_automation_rule(self):
        """Test updating automation rule (Previously 404)"""
        try:
            if not self.test_rule_id:
                self.log_test("Update Automation Rule", False, "No test rule ID available")
                return
            
            update_data = {
                "description": "Updated: Automatically archive content that hasn't been viewed in 60 days",
                "trigger_conditions": {
                    "days_inactive": 60
                },
                "is_active": True
            }
            
            response = requests.put(
                f"{self.lifecycle_base}/automation/rules/{self.test_rule_id}",
                headers=self.get_headers(),
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test(
                        "Update Automation Rule",
                        True,
                        f"Rule updated successfully: {result.get('rule_id')}"
                    )
                else:
                    self.log_test(
                        "Update Automation Rule",
                        False,
                        "Update failed",
                        result
                    )
            elif response.status_code == 404:
                self.log_test(
                    "Update Automation Rule",
                    False,
                    "Automation rule not found",
                    response.text
                )
            else:
                self.log_test(
                    "Update Automation Rule",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Update Automation Rule", False, f"Exception: {e}")

    def test_delete_automation_rule(self):
        """Test deleting automation rule (Previously 404)"""
        try:
            if not self.test_rule_id:
                self.log_test("Delete Automation Rule", False, "No test rule ID available")
                return
            
            response = requests.delete(
                f"{self.lifecycle_base}/automation/rules/{self.test_rule_id}",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test(
                        "Delete Automation Rule",
                        True,
                        f"Rule deleted successfully: {result.get('rule_id')}"
                    )
                else:
                    self.log_test(
                        "Delete Automation Rule",
                        False,
                        "Delete failed",
                        result
                    )
            elif response.status_code == 404:
                self.log_test(
                    "Delete Automation Rule",
                    False,
                    "Automation rule not found",
                    response.text
                )
            else:
                self.log_test(
                    "Delete Automation Rule",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Delete Automation Rule", False, f"Exception: {e}")

    def test_list_content_lifecycles(self):
        """Test listing content lifecycles"""
        try:
            response = requests.get(
                f"{self.lifecycle_base}/",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "lifecycles" in result:
                    lifecycles = result["lifecycles"]
                    self.log_test(
                        "List Content Lifecycles",
                        True,
                        f"Retrieved {len(lifecycles)} lifecycles"
                    )
                else:
                    self.log_test(
                        "List Content Lifecycles",
                        False,
                        "Response missing required fields",
                        result
                    )
            else:
                self.log_test(
                    "List Content Lifecycles",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("List Content Lifecycles", False, f"Exception: {e}")

    def test_get_content_lifecycle(self):
        """Test getting specific content lifecycle"""
        try:
            if not self.test_content_id:
                self.log_test("Get Content Lifecycle", False, "No test content ID available")
                return
            
            response = requests.get(
                f"{self.lifecycle_base}/{self.test_content_id}",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "lifecycle" in result:
                    lifecycle = result["lifecycle"]
                    self.log_test(
                        "Get Content Lifecycle",
                        True,
                        f"Lifecycle retrieved: Status={lifecycle.get('current_status')}, Stage={lifecycle.get('current_stage')}"
                    )
                else:
                    self.log_test(
                        "Get Content Lifecycle",
                        False,
                        "Response missing required fields",
                        result
                    )
            elif response.status_code == 404:
                self.log_test(
                    "Get Content Lifecycle",
                    False,
                    "Content lifecycle not found",
                    response.text
                )
            else:
                self.log_test(
                    "Get Content Lifecycle",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Get Content Lifecycle", False, f"Exception: {e}")

    def test_lifecycle_enums(self):
        """Test lifecycle enums endpoint"""
        try:
            response = requests.get(
                f"{self.lifecycle_base}/enums",
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "enums" in result:
                    enums = result["enums"]
                    expected_keys = ["content_statuses", "lifecycle_stages", "automation_triggers", "action_types"]
                    has_all_keys = all(key in enums for key in expected_keys)
                    
                    self.log_test(
                        "Lifecycle Enums",
                        has_all_keys,
                        f"Retrieved enums: {list(enums.keys())}"
                    )
                else:
                    self.log_test(
                        "Lifecycle Enums",
                        False,
                        "Response missing required fields",
                        result
                    )
            else:
                self.log_test(
                    "Lifecycle Enums",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Lifecycle Enums", False, f"Exception: {e}")

    def run_all_tests(self):
        """Run all Function 5 lifecycle management tests"""
        print("🎯 FUNCTION 5: CONTENT LIFECYCLE MANAGEMENT & AUTOMATION SYSTEM TESTING")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print()
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        print("\n📋 PRIORITY TESTING AREAS (Previously Failing):")
        print("-" * 50)
        
        # Test previously failing endpoints
        self.test_lifecycle_health_check()
        self.test_lifecycle_dashboard()
        
        print("\n📋 COMPREHENSIVE FUNCTION 5 TESTING:")
        print("-" * 50)
        
        # Core lifecycle management
        self.test_create_content_lifecycle()
        self.test_version_creation()
        self.test_get_content_lifecycle()
        self.test_list_content_lifecycles()
        
        # Automation management (Previously failing endpoints)
        self.test_create_automation_rule()
        self.test_update_automation_rule()  # Previously 404
        self.test_delete_automation_rule()  # Previously 404
        
        # Additional endpoints
        self.test_lifecycle_enums()
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 FUNCTION 5 LIFECYCLE MANAGEMENT TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({self.failed_tests}):")
            print("-" * 40)
            for result in self.test_results:
                if not result["success"]:
                    print(f"• {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS ({self.passed_tests}):")
        print("-" * 40)
        for result in self.test_results:
            if result["success"]:
                print(f"• {result['test']}: {result['details']}")
        
        # Priority issues analysis
        priority_tests = [
            "Version Creation",
            "Lifecycle Health Check", 
            "Lifecycle Dashboard",
            "Update Automation Rule",
            "Delete Automation Rule"
        ]
        
        priority_results = [r for r in self.test_results if r["test"] in priority_tests]
        priority_passed = len([r for r in priority_results if r["success"]])
        priority_total = len(priority_results)
        
        print(f"\n🎯 PRIORITY ISSUES RESOLUTION:")
        print("-" * 40)
        print(f"Priority Tests: {priority_total}")
        print(f"Priority Passed: {priority_passed}")
        print(f"Priority Success Rate: {(priority_passed/priority_total*100) if priority_total > 0 else 0:.1f}%")
        
        if priority_passed == priority_total:
            print("✅ All previously failing endpoints are now working!")
        else:
            print("❌ Some priority issues remain unresolved")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = Function5LifecycleBackendTester()
    tester.run_all_tests()