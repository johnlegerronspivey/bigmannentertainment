#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Workflow Enhancement Endpoints
Big Mann Entertainment Platform - Workflow Enhancement System Testing

This script tests all workflow enhancement endpoints including:
- User workflow progress tracking
- Action tracking for analytics
- Onboarding status and completion
- Enhanced dashboard data retrieval
- User analytics and engagement scoring
- Achievements and milestone tracking
- Personalized next step recommendations
- Milestone completion functionality
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://social-profile-sync.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class WorkflowEnhancementTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.access_token = None
        self.test_user_data = {
            "email": "workflow.tester@bigmannentertainment.com",
            "password": "WorkflowTest2025!",
            "full_name": "Workflow Enhancement Tester",
            "business_name": "Workflow Testing Studio",
            "date_of_birth": "1990-05-15T00:00:00Z",
            "address_line1": "123 Workflow Street",
            "city": "Enhancement City",
            "state_province": "Testing State",
            "postal_code": "12345",
            "country": "United States"
        }

    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")

    async def register_and_login_user(self) -> bool:
        """Register and login test user"""
        try:
            # Register user
            register_url = f"{API_BASE}/auth/register"
            async with self.session.post(register_url, json=self.test_user_data) as response:
                if response.status == 200:
                    register_data = await response.json()
                    self.access_token = register_data.get("access_token")
                    self.log_test_result("User Registration", True, "Test user registered successfully")
                    return True
                else:
                    # Try to login if user already exists
                    login_url = f"{API_BASE}/auth/login"
                    login_data = {
                        "email": self.test_user_data["email"],
                        "password": self.test_user_data["password"]
                    }
                    async with self.session.post(login_url, json=login_data) as login_response:
                        if login_response.status == 200:
                            login_result = await login_response.json()
                            self.access_token = login_result.get("access_token")
                            self.log_test_result("User Login", True, "Test user logged in successfully")
                            return True
                        else:
                            error_data = await login_response.text()
                            self.log_test_result("User Authentication", False, f"Failed to authenticate: {error_data}")
                            return False
        except Exception as e:
            self.log_test_result("User Authentication", False, f"Authentication error: {str(e)}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.access_token}"}

    async def test_workflow_progress_endpoint(self):
        """Test GET /api/user/workflow-progress endpoint"""
        try:
            url = f"{API_BASE}/user/workflow-progress"
            headers = self.get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    workflow_progress = data.get("workflow_progress", {})
                    
                    # Verify expected fields
                    expected_fields = [
                        "uploads_count", "library_count", "distributions_count",
                        "earnings_total", "earnings_pending", "earnings_paid",
                        "payouts_count", "workflow_completion", "next_steps",
                        "achievements", "milestones"
                    ]
                    
                    missing_fields = [field for field in expected_fields if field not in workflow_progress]
                    
                    if not missing_fields:
                        self.log_test_result(
                            "Workflow Progress Endpoint",
                            True,
                            f"Retrieved workflow progress with all expected fields. Completion: {workflow_progress.get('workflow_completion', 0)}%"
                        )
                    else:
                        self.log_test_result(
                            "Workflow Progress Endpoint",
                            False,
                            f"Missing fields: {missing_fields}",
                            data
                        )
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "Workflow Progress Endpoint",
                        False,
                        f"HTTP {response.status}: {error_data}"
                    )
        except Exception as e:
            self.log_test_result("Workflow Progress Endpoint", False, f"Exception: {str(e)}")

    async def test_track_action_endpoint(self):
        """Test POST /api/user/track-action endpoint"""
        try:
            url = f"{API_BASE}/user/track-action"
            headers = self.get_auth_headers()
            
            # Test tracking different types of actions
            test_actions = [
                {
                    "action": "page_view",
                    "details": {
                        "page": "/dashboard",
                        "session_id": "test_session_123",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                },
                {
                    "action": "upload_started",
                    "details": {
                        "file_type": "audio",
                        "file_size": 5242880
                    }
                },
                {
                    "action": "distribution_initiated",
                    "details": {
                        "platforms": ["spotify", "apple_music", "youtube"],
                        "content_id": "test_content_123"
                    }
                }
            ]
            
            success_count = 0
            for action_data in test_actions:
                async with self.session.post(url, headers=headers, json=action_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("message") == "Action tracked successfully":
                            success_count += 1
                    else:
                        error_data = await response.text()
                        self.log_test_result(
                            f"Track Action - {action_data['action']}",
                            False,
                            f"HTTP {response.status}: {error_data}"
                        )
            
            if success_count == len(test_actions):
                self.log_test_result(
                    "Track Action Endpoint",
                    True,
                    f"Successfully tracked {success_count} different actions"
                )
            else:
                self.log_test_result(
                    "Track Action Endpoint",
                    False,
                    f"Only {success_count}/{len(test_actions)} actions tracked successfully"
                )
                
        except Exception as e:
            self.log_test_result("Track Action Endpoint", False, f"Exception: {str(e)}")

    async def test_user_analytics_endpoint(self):
        """Test GET /api/user/analytics endpoint"""
        try:
            # Test with different period parameters
            test_periods = [7, 30, 90]
            
            for period in test_periods:
                url = f"{API_BASE}/user/analytics?period_days={period}"
                headers = self.get_auth_headers()
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        analytics = data.get("analytics", {})
                        
                        # Verify expected analytics fields
                        expected_fields = [
                            "period_days", "total_actions", "action_breakdown",
                            "daily_activity", "engagement_score"
                        ]
                        
                        missing_fields = [field for field in expected_fields if field not in analytics]
                        
                        if not missing_fields:
                            self.log_test_result(
                                f"User Analytics ({period} days)",
                                True,
                                f"Retrieved analytics with engagement score: {analytics.get('engagement_score', 0)}"
                            )
                        else:
                            self.log_test_result(
                                f"User Analytics ({period} days)",
                                False,
                                f"Missing fields: {missing_fields}",
                                data
                            )
                    else:
                        error_data = await response.text()
                        self.log_test_result(
                            f"User Analytics ({period} days)",
                            False,
                            f"HTTP {response.status}: {error_data}"
                        )
                        
        except Exception as e:
            self.log_test_result("User Analytics Endpoint", False, f"Exception: {str(e)}")

    async def test_onboarding_status_endpoint(self):
        """Test GET /api/user/onboarding-status endpoint"""
        try:
            url = f"{API_BASE}/user/onboarding-status"
            headers = self.get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    onboarding = data.get("onboarding", {})
                    
                    # Verify expected onboarding fields
                    expected_fields = [
                        "onboarding_steps", "completed_steps", "total_steps",
                        "completion_percentage", "current_step", "is_complete"
                    ]
                    
                    missing_fields = [field for field in expected_fields if field not in onboarding]
                    
                    if not missing_fields:
                        completion_pct = onboarding.get("completion_percentage", 0)
                        steps_info = f"{onboarding.get('completed_steps', 0)}/{onboarding.get('total_steps', 0)}"
                        self.log_test_result(
                            "Onboarding Status Endpoint",
                            True,
                            f"Onboarding progress: {completion_pct}% ({steps_info} steps completed)"
                        )
                    else:
                        self.log_test_result(
                            "Onboarding Status Endpoint",
                            False,
                            f"Missing fields: {missing_fields}",
                            data
                        )
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "Onboarding Status Endpoint",
                        False,
                        f"HTTP {response.status}: {error_data}"
                    )
        except Exception as e:
            self.log_test_result("Onboarding Status Endpoint", False, f"Exception: {str(e)}")

    async def test_enhanced_dashboard_endpoint(self):
        """Test GET /api/user/dashboard endpoint"""
        try:
            url = f"{API_BASE}/user/dashboard"
            headers = self.get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    dashboard = data.get("dashboard", {})
                    
                    # Verify expected dashboard sections
                    expected_sections = [
                        "user_info", "progress", "onboarding", "analytics",
                        "quick_actions", "notifications", "tips"
                    ]
                    
                    missing_sections = [section for section in expected_sections if section not in dashboard]
                    
                    if not missing_sections:
                        user_info = dashboard.get("user_info", {})
                        quick_actions = dashboard.get("quick_actions", [])
                        notifications = dashboard.get("notifications", [])
                        tips = dashboard.get("tips", [])
                        
                        self.log_test_result(
                            "Enhanced Dashboard Endpoint",
                            True,
                            f"Complete dashboard data: {len(quick_actions)} actions, {len(notifications)} notifications, {len(tips)} tips"
                        )
                    else:
                        self.log_test_result(
                            "Enhanced Dashboard Endpoint",
                            False,
                            f"Missing sections: {missing_sections}",
                            data
                        )
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "Enhanced Dashboard Endpoint",
                        False,
                        f"HTTP {response.status}: {error_data}"
                    )
        except Exception as e:
            self.log_test_result("Enhanced Dashboard Endpoint", False, f"Exception: {str(e)}")

    async def test_achievements_endpoint(self):
        """Test GET /api/user/achievements endpoint"""
        try:
            url = f"{API_BASE}/user/achievements"
            headers = self.get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify expected achievement fields
                    expected_fields = [
                        "achievements", "milestones", "total_achievements", "total_milestones"
                    ]
                    
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if not missing_fields:
                        achievements = data.get("achievements", [])
                        milestones = data.get("milestones", [])
                        total_achievements = data.get("total_achievements", 0)
                        total_milestones = data.get("total_milestones", 0)
                        
                        self.log_test_result(
                            "Achievements Endpoint",
                            True,
                            f"Retrieved {total_achievements} achievements and {total_milestones} milestones"
                        )
                    else:
                        self.log_test_result(
                            "Achievements Endpoint",
                            False,
                            f"Missing fields: {missing_fields}",
                            data
                        )
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "Achievements Endpoint",
                        False,
                        f"HTTP {response.status}: {error_data}"
                    )
        except Exception as e:
            self.log_test_result("Achievements Endpoint", False, f"Exception: {str(e)}")

    async def test_next_steps_endpoint(self):
        """Test GET /api/user/next-steps endpoint"""
        try:
            # Test with different limit parameters
            test_limits = [3, 5, 10]
            
            for limit in test_limits:
                url = f"{API_BASE}/user/next-steps?limit={limit}"
                headers = self.get_auth_headers()
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Verify expected fields
                        expected_fields = ["next_steps", "total_recommendations"]
                        missing_fields = [field for field in expected_fields if field not in data]
                        
                        if not missing_fields:
                            next_steps = data.get("next_steps", [])
                            total_recommendations = data.get("total_recommendations", 0)
                            
                            # Verify each next step has required fields
                            valid_steps = True
                            for step in next_steps:
                                required_step_fields = ["action", "title", "description", "link", "priority"]
                                if not all(field in step for field in required_step_fields):
                                    valid_steps = False
                                    break
                            
                            if valid_steps:
                                self.log_test_result(
                                    f"Next Steps Endpoint (limit={limit})",
                                    True,
                                    f"Retrieved {len(next_steps)} next steps (total: {total_recommendations})"
                                )
                            else:
                                self.log_test_result(
                                    f"Next Steps Endpoint (limit={limit})",
                                    False,
                                    "Next steps missing required fields",
                                    data
                                )
                        else:
                            self.log_test_result(
                                f"Next Steps Endpoint (limit={limit})",
                                False,
                                f"Missing fields: {missing_fields}",
                                data
                            )
                    else:
                        error_data = await response.text()
                        self.log_test_result(
                            f"Next Steps Endpoint (limit={limit})",
                            False,
                            f"HTTP {response.status}: {error_data}"
                        )
                        
        except Exception as e:
            self.log_test_result("Next Steps Endpoint", False, f"Exception: {str(e)}")

    async def test_complete_milestone_endpoint(self):
        """Test POST /api/user/complete-milestone endpoint"""
        try:
            url = f"{API_BASE}/user/complete-milestone"
            headers = self.get_auth_headers()
            
            # Test completing different types of milestones
            test_milestones = [
                {
                    "milestone_id": "first_upload_milestone",
                    "type": "upload"
                },
                {
                    "milestone_id": "first_distribution_milestone", 
                    "type": "distribution"
                },
                {
                    "milestone_id": "profile_completion_milestone",
                    "type": "profile"
                }
            ]
            
            success_count = 0
            for milestone_data in test_milestones:
                async with self.session.post(url, headers=headers, json=milestone_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("message") == "Milestone completed successfully":
                            success_count += 1
                    else:
                        error_data = await response.text()
                        self.log_test_result(
                            f"Complete Milestone - {milestone_data['type']}",
                            False,
                            f"HTTP {response.status}: {error_data}"
                        )
            
            if success_count == len(test_milestones):
                self.log_test_result(
                    "Complete Milestone Endpoint",
                    True,
                    f"Successfully completed {success_count} milestones"
                )
            else:
                self.log_test_result(
                    "Complete Milestone Endpoint",
                    False,
                    f"Only {success_count}/{len(test_milestones)} milestones completed successfully"
                )
                
        except Exception as e:
            self.log_test_result("Complete Milestone Endpoint", False, f"Exception: {str(e)}")

    async def test_authentication_security(self):
        """Test that all endpoints require proper authentication"""
        try:
            endpoints_to_test = [
                "/user/workflow-progress",
                "/user/analytics",
                "/user/onboarding-status", 
                "/user/dashboard",
                "/user/achievements",
                "/user/next-steps"
            ]
            
            unauthorized_count = 0
            for endpoint in endpoints_to_test:
                url = f"{API_BASE}{endpoint}"
                
                # Test without authorization header
                async with self.session.get(url) as response:
                    if response.status in [401, 403]:
                        unauthorized_count += 1
                    else:
                        self.log_test_result(
                            f"Authentication Security - {endpoint}",
                            False,
                            f"Endpoint accessible without auth (HTTP {response.status})"
                        )
            
            # Test POST endpoints
            post_endpoints = [
                ("/user/track-action", {"action": "test"}),
                ("/user/complete-milestone", {"milestone_id": "test", "type": "test"})
            ]
            
            for endpoint, test_data in post_endpoints:
                url = f"{API_BASE}{endpoint}"
                async with self.session.post(url, json=test_data) as response:
                    if response.status in [401, 403]:
                        unauthorized_count += 1
                    else:
                        self.log_test_result(
                            f"Authentication Security - {endpoint}",
                            False,
                            f"POST endpoint accessible without auth (HTTP {response.status})"
                        )
            
            total_endpoints = len(endpoints_to_test) + len(post_endpoints)
            if unauthorized_count == total_endpoints:
                self.log_test_result(
                    "Authentication Security",
                    True,
                    f"All {total_endpoints} endpoints properly require authentication"
                )
            else:
                self.log_test_result(
                    "Authentication Security",
                    False,
                    f"Only {unauthorized_count}/{total_endpoints} endpoints require authentication"
                )
                
        except Exception as e:
            self.log_test_result("Authentication Security", False, f"Exception: {str(e)}")

    async def run_comprehensive_tests(self):
        """Run all workflow enhancement tests"""
        print("🎯 STARTING COMPREHENSIVE WORKFLOW ENHANCEMENT BACKEND TESTING")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Authentication setup
            if not await self.register_and_login_user():
                print("❌ Failed to authenticate user. Cannot proceed with tests.")
                return
            
            print("\n📊 TESTING WORKFLOW ENHANCEMENT ENDPOINTS")
            print("-" * 50)
            
            # Test all workflow enhancement endpoints
            await self.test_workflow_progress_endpoint()
            await self.test_track_action_endpoint()
            await self.test_user_analytics_endpoint()
            await self.test_onboarding_status_endpoint()
            await self.test_enhanced_dashboard_endpoint()
            await self.test_achievements_endpoint()
            await self.test_next_steps_endpoint()
            await self.test_complete_milestone_endpoint()
            
            print("\n🔒 TESTING AUTHENTICATION & SECURITY")
            print("-" * 50)
            await self.test_authentication_security()
            
        finally:
            await self.cleanup_session()
        
        # Print comprehensive results
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "=" * 80)
        print("🎯 WORKFLOW ENHANCEMENT BACKEND TESTING RESULTS")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {len(self.test_results)}")
        print(f"   Passed: {len(passed_tests)} ✅")
        print(f"   Failed: {len(failed_tests)} ❌")
        print(f"   Success Rate: {(len(passed_tests)/len(self.test_results)*100):.1f}%")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['test']}: {test['details']}")
        
        print("\n" + "=" * 80)
        
        # Determine overall status
        if len(failed_tests) == 0:
            print("🎉 ALL WORKFLOW ENHANCEMENT TESTS PASSED! System is production-ready.")
        elif len(failed_tests) <= 2:
            print("⚠️  MOSTLY SUCCESSFUL with minor issues. Review failed tests.")
        else:
            print("❌ MULTIPLE FAILURES detected. System needs attention before production.")
        
        print("=" * 80)

async def main():
    """Main test execution function"""
    tester = WorkflowEnhancementTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())