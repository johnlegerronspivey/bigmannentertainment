#!/usr/bin/env python3
"""
Comprehensive Platform Licensing System Backend Testing
Tests all comprehensive licensing endpoints including business information,
license agreements, automated workflows, dashboard, and master platform licensing
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://uln-label-editor-1.preview.emergentagent.com/api"

class ComprehensiveLicensingTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.user_email = "testuser_comprehensive_licensing@bigmannentertainment.com"
        self.user_password = "ComprehensiveLicensing2025!"
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def register_and_login(self):
        """Register test user and login to get auth token"""
        try:
            # Check if backend is accessible first
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status != 200:
                    print(f"❌ Backend health check failed: {response.status}")
                    # Try without authentication for basic endpoint testing
                    print("ℹ️ Proceeding with unauthenticated testing...")
                    return True
            
            # Registration data
            registration_data = {
                "email": self.user_email,
                "password": self.user_password,
                "full_name": "Comprehensive Licensing Test User",
                "business_name": "Big Mann Entertainment Licensing Division",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "1314 Lincoln Heights Street",
                "city": "Alexander City",
                "state_province": "Alabama",
                "postal_code": "35010",
                "country": "United States"
            }
            
            # Try registration
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=registration_data) as response:
                if response.status in [200, 201]:
                    print("✅ User registration successful")
                elif response.status == 400:
                    print("ℹ️ User already exists, proceeding to login")
                elif response.status == 502:
                    print("⚠️ Backend service unavailable, testing endpoint accessibility...")
                    return True
                else:
                    print(f"⚠️ Registration response: {response.status}")
            
            # Login
            login_data = {
                "email": self.user_email,
                "password": self.user_password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get("access_token")
                    print("✅ Login successful")
                    return True
                elif response.status == 502:
                    print("⚠️ Backend service unavailable, testing endpoint accessibility...")
                    return True
                else:
                    print(f"❌ Login failed: {response.status}")
                    return True  # Continue with testing even without auth
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            print("ℹ️ Continuing with endpoint accessibility testing...")
            return True
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_business_information_consolidation(self):
        """Test business information consolidation service"""
        print("\n🔍 Testing Business Information Consolidation Service...")
        
        tests = [
            {
                "name": "Get Consolidated Business Information",
                "method": "GET",
                "endpoint": "/comprehensive-licensing/business-information",
                "expected_fields": ["business_information", "data_sources", "last_updated", "verification_status", "completeness_score"]
            },
            {
                "name": "Validate Business Information",
                "method": "POST", 
                "endpoint": "/comprehensive-licensing/business-information/validate",
                "expected_fields": ["validation_results", "business_id", "validation_date", "recommendations"]
            }
        ]
        
        for test in tests:
            try:
                headers = self.get_auth_headers()
                
                if test["method"] == "GET":
                    async with self.session.get(f"{BACKEND_URL}{test['endpoint']}", headers=headers) as response:
                        await self._process_test_response(test, response)
                elif test["method"] == "POST":
                    async with self.session.post(f"{BACKEND_URL}{test['endpoint']}", headers=headers, json={}) as response:
                        await self._process_test_response(test, response)
                        
            except Exception as e:
                self._record_test_result(test["name"], False, f"Exception: {e}")
    
    async def test_comprehensive_license_agreements(self):
        """Test comprehensive license agreement endpoints"""
        print("\n📋 Testing Comprehensive License Agreement System...")
        
        # Test creating comprehensive license agreement
        try:
            headers = self.get_auth_headers()
            
            # Create comprehensive license agreement
            license_request = {
                "platform_ids": ["spotify", "apple_music", "youtube", "instagram", "tiktok"],
                "license_type": "comprehensive_agreement",
                "license_duration_months": 12,
                "auto_renewal": True,
                "include_compliance_docs": True,
                "generate_workflows": True
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/comprehensive-licensing/license-agreements",
                headers=headers,
                json=license_request
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    expected_fields = ["message", "agreement", "agreement_id", "platforms_licensed", "total_platforms"]
                    
                    if all(field in result for field in expected_fields):
                        self._record_test_result("Create Comprehensive License Agreement", True, 
                                               f"Created agreement for {result.get('total_platforms', 0)} platforms")
                        self.test_agreement_id = result.get("agreement_id")
                    else:
                        self._record_test_result("Create Comprehensive License Agreement", False, 
                                               f"Missing expected fields in response")
                else:
                    self._record_test_result("Create Comprehensive License Agreement", False, 
                                           f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self._record_test_result("Create Comprehensive License Agreement", False, f"Exception: {e}")
        
        # Test getting license agreements
        try:
            async with self.session.get(
                f"{BACKEND_URL}/comprehensive-licensing/license-agreements",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    expected_fields = ["agreements", "total_count"]
                    
                    if all(field in result for field in expected_fields):
                        self._record_test_result("Get License Agreements", True, 
                                               f"Retrieved {result.get('total_count', 0)} agreements")
                    else:
                        self._record_test_result("Get License Agreements", False, "Missing expected fields")
                else:
                    self._record_test_result("Get License Agreements", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self._record_test_result("Get License Agreements", False, f"Exception: {e}")
        
        # Test getting specific agreement details if we have an agreement ID
        if hasattr(self, 'test_agreement_id'):
            try:
                async with self.session.get(
                    f"{BACKEND_URL}/comprehensive-licensing/license-agreements/{self.test_agreement_id}",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        expected_fields = ["agreement", "compliance_documents", "platform_breakdown", "financial_summary"]
                        
                        if all(field in result for field in expected_fields):
                            self._record_test_result("Get License Agreement Details", True, 
                                                   f"Retrieved detailed agreement information")
                        else:
                            self._record_test_result("Get License Agreement Details", False, "Missing expected fields")
                    else:
                        self._record_test_result("Get License Agreement Details", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self._record_test_result("Get License Agreement Details", False, f"Exception: {e}")
    
    async def test_automated_licensing_workflows(self):
        """Test automated licensing workflows"""
        print("\n⚙️ Testing Automated Licensing Workflows...")
        
        # Test creating automated workflow
        try:
            headers = self.get_auth_headers()
            
            workflow_request = {
                "workflow_name": "Comprehensive Music Streaming Workflow",
                "platform_categories": ["music_streaming", "social_media"],
                "trigger_conditions": ["business_info_validated", "compliance_docs_ready"],
                "auto_execute_steps": ["validate_business_info", "generate_agreements", "create_compliance_docs"]
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/comprehensive-licensing/workflows",
                headers=headers,
                json=workflow_request
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    expected_fields = ["message", "workflow", "workflow_id", "platform_categories", "total_automation_steps"]
                    
                    if all(field in result for field in expected_fields):
                        self._record_test_result("Create Automated Workflow", True, 
                                               f"Created workflow with {result.get('total_automation_steps', 0)} steps")
                        self.test_workflow_id = result.get("workflow_id")
                    else:
                        self._record_test_result("Create Automated Workflow", False, "Missing expected fields")
                else:
                    self._record_test_result("Create Automated Workflow", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self._record_test_result("Create Automated Workflow", False, f"Exception: {e}")
        
        # Test getting workflows
        try:
            async with self.session.get(
                f"{BACKEND_URL}/comprehensive-licensing/workflows",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    expected_fields = ["workflows", "total_workflows", "active_workflows", "automation_capabilities"]
                    
                    if all(field in result for field in expected_fields):
                        self._record_test_result("Get Automated Workflows", True, 
                                               f"Retrieved {result.get('total_workflows', 0)} workflows")
                    else:
                        self._record_test_result("Get Automated Workflows", False, "Missing expected fields")
                else:
                    self._record_test_result("Get Automated Workflows", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self._record_test_result("Get Automated Workflows", False, f"Exception: {e}")
        
        # Test workflow execution if we have a workflow ID
        if hasattr(self, 'test_workflow_id'):
            try:
                execution_request = ["spotify", "apple_music", "youtube"]
                
                async with self.session.post(
                    f"{BACKEND_URL}/comprehensive-licensing/workflows/{self.test_workflow_id}/execute",
                    headers=self.get_auth_headers(),
                    json=execution_request
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        expected_fields = ["message", "workflow_id", "platforms_to_process", "total_automation_steps"]
                        
                        if all(field in result for field in expected_fields):
                            self._record_test_result("Execute Automated Workflow", True, 
                                                   f"Workflow execution started for {len(execution_request)} platforms")
                        else:
                            self._record_test_result("Execute Automated Workflow", False, "Missing expected fields")
                    else:
                        self._record_test_result("Execute Automated Workflow", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self._record_test_result("Execute Automated Workflow", False, f"Exception: {e}")
    
    async def test_comprehensive_dashboard(self):
        """Test comprehensive licensing dashboard"""
        print("\n📊 Testing Comprehensive Licensing Dashboard...")
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/comprehensive-licensing/dashboard",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    expected_fields = [
                        "comprehensive_licensing_dashboard", 
                        "dashboard_type", 
                        "business_entity",
                        "total_platforms_licensed",
                        "total_licensing_investment",
                        "dashboard_capabilities"
                    ]
                    
                    if all(field in result for field in expected_fields):
                        self._record_test_result("Comprehensive Dashboard", True, 
                                               f"Dashboard loaded with {result.get('total_platforms_licensed', 0)} licensed platforms")
                    else:
                        self._record_test_result("Comprehensive Dashboard", False, "Missing expected fields")
                else:
                    self._record_test_result("Comprehensive Dashboard", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self._record_test_result("Comprehensive Dashboard", False, f"Exception: {e}")
        
        # Test compliance documents
        try:
            async with self.session.get(
                f"{BACKEND_URL}/comprehensive-licensing/compliance-documents",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    expected_fields = ["compliance_documents", "total_documents", "document_status_breakdown"]
                    
                    if all(field in result for field in expected_fields):
                        self._record_test_result("Compliance Documents", True, 
                                               f"Retrieved {result.get('total_documents', 0)} compliance documents")
                    else:
                        self._record_test_result("Compliance Documents", False, "Missing expected fields")
                else:
                    self._record_test_result("Compliance Documents", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self._record_test_result("Compliance Documents", False, f"Exception: {e}")
    
    async def test_master_platform_licensing(self):
        """Test master platform licensing for all 114+ platforms"""
        print("\n🌐 Testing Master Platform Licensing (All 114+ Platforms)...")
        
        try:
            headers = self.get_auth_headers()
            
            # Generate comprehensive licenses for all platforms
            request_data = {
                "include_compliance_docs": True,
                "generate_workflows": True
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/comprehensive-licensing/generate-all-platform-licenses",
                headers=headers,
                json=request_data
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    expected_fields = [
                        "message",
                        "master_agreement", 
                        "agreement_id",
                        "business_entity",
                        "platforms_licensed",
                        "platform_categories",
                        "estimated_annual_investment",
                        "comprehensive_features"
                    ]
                    
                    if all(field in result for field in expected_fields):
                        platforms_count = result.get("platforms_licensed", 0)
                        annual_investment = result.get("estimated_annual_investment", 0)
                        
                        self._record_test_result("Master Platform Licensing", True, 
                                               f"Generated comprehensive licenses for {platforms_count} platforms with ${annual_investment:,.2f} annual investment")
                        
                        # Verify platform count meets requirement
                        if platforms_count >= 114:
                            self._record_test_result("Platform Count Verification", True, 
                                                   f"Meets 114+ platform requirement with {platforms_count} platforms")
                        else:
                            self._record_test_result("Platform Count Verification", False, 
                                                   f"Only {platforms_count} platforms, below 114+ requirement")
                    else:
                        self._record_test_result("Master Platform Licensing", False, "Missing expected fields")
                else:
                    self._record_test_result("Master Platform Licensing", False, 
                                           f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self._record_test_result("Master Platform Licensing", False, f"Exception: {e}")
    
    async def test_authentication_and_authorization(self):
        """Test authentication and authorization on all endpoints"""
        print("\n🔐 Testing Authentication and Authorization...")
        
        # Test endpoints without authentication
        test_endpoints = [
            "/comprehensive-licensing/dashboard",
            "/comprehensive-licensing/business-information", 
            "/comprehensive-licensing/license-agreements",
            "/comprehensive-licensing/workflows"
        ]
        
        for endpoint in test_endpoints:
            try:
                # Test without auth token
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    if response.status in [401, 403]:
                        self._record_test_result(f"Auth Required - {endpoint}", True, 
                                               f"Properly requires authentication (HTTP {response.status})")
                    else:
                        self._record_test_result(f"Auth Required - {endpoint}", False, 
                                               f"Should require authentication but got HTTP {response.status}")
                        
            except Exception as e:
                self._record_test_result(f"Auth Required - {endpoint}", False, f"Exception: {e}")
        
        # Test admin-only endpoints
        admin_endpoints = [
            "/comprehensive-licensing/generate-all-platform-licenses"
        ]
        
        for endpoint in admin_endpoints:
            try:
                # Test with regular user token (should fail)
                async with self.session.post(
                    f"{BACKEND_URL}{endpoint}",
                    headers=self.get_auth_headers(),
                    json={}
                ) as response:
                    if response.status == 403:
                        self._record_test_result(f"Admin Required - {endpoint}", True, 
                                               "Properly requires admin permissions")
                    else:
                        self._record_test_result(f"Admin Required - {endpoint}", False, 
                                               f"Should require admin but got HTTP {response.status}")
                        
            except Exception as e:
                self._record_test_result(f"Admin Required - {endpoint}", False, f"Exception: {e}")
    
    async def test_error_handling_and_responses(self):
        """Test error handling and response structures"""
        print("\n🛡️ Testing Error Handling and Response Structures...")
        
        # Test invalid agreement ID
        try:
            async with self.session.get(
                f"{BACKEND_URL}/comprehensive-licensing/license-agreements/invalid-id",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 404:
                    self._record_test_result("Invalid Agreement ID Handling", True, 
                                           "Properly returns 404 for invalid agreement ID")
                else:
                    self._record_test_result("Invalid Agreement ID Handling", False, 
                                           f"Expected 404 but got {response.status}")
                    
        except Exception as e:
            self._record_test_result("Invalid Agreement ID Handling", False, f"Exception: {e}")
        
        # Test invalid workflow ID
        try:
            async with self.session.post(
                f"{BACKEND_URL}/comprehensive-licensing/workflows/invalid-id/execute",
                headers=self.get_auth_headers(),
                json=["spotify"]
            ) as response:
                if response.status == 404:
                    self._record_test_result("Invalid Workflow ID Handling", True, 
                                           "Properly returns 404 for invalid workflow ID")
                else:
                    self._record_test_result("Invalid Workflow ID Handling", False, 
                                           f"Expected 404 but got {response.status}")
                    
        except Exception as e:
            self._record_test_result("Invalid Workflow ID Handling", False, f"Exception: {e}")
    
    async def _process_test_response(self, test: Dict, response):
        """Process test response and record results"""
        try:
            if response.status == 200:
                result = await response.json()
                expected_fields = test.get("expected_fields", [])
                
                if all(field in result for field in expected_fields):
                    self._record_test_result(test["name"], True, "All expected fields present")
                else:
                    missing_fields = [field for field in expected_fields if field not in result]
                    self._record_test_result(test["name"], False, f"Missing fields: {missing_fields}")
            else:
                self._record_test_result(test["name"], False, f"HTTP {response.status}")
                
        except Exception as e:
            self._record_test_result(test["name"], False, f"Exception: {e}")
    
    def _record_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}: {details}")
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["passed"]])
        failed_tests = total_tests - passed_tests
        
        print(f"\n" + "="*80)
        print("🎯 COMPREHENSIVE PLATFORM LICENSING SYSTEM TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n🎉 COMPREHENSIVE RESULTS:")
        
        # Group results by category
        categories = {
            "Business Information": [r for r in self.test_results if "Business" in r["test"]],
            "License Agreements": [r for r in self.test_results if "License" in r["test"] or "Agreement" in r["test"]],
            "Automated Workflows": [r for r in self.test_results if "Workflow" in r["test"]],
            "Dashboard & Compliance": [r for r in self.test_results if "Dashboard" in r["test"] or "Compliance" in r["test"]],
            "Master Platform Licensing": [r for r in self.test_results if "Master" in r["test"] or "Platform" in r["test"]],
            "Authentication & Security": [r for r in self.test_results if "Auth" in r["test"] or "Admin" in r["test"]],
            "Error Handling": [r for r in self.test_results if "Invalid" in r["test"] or "Error" in r["test"]]
        }
        
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if r["passed"]])
                total = len(results)
                print(f"  {category}: {passed}/{total} tests passed")
        
        print("="*80)

async def main():
    """Main test execution"""
    print("🎯 COMPREHENSIVE PLATFORM LICENSING SYSTEM BACKEND TESTING")
    print("="*80)
    print("Testing comprehensive licensing system with business information integration,")
    print("automated workflows, compliance documentation, and master platform licensing")
    print("="*80)
    
    tester = ComprehensiveLicensingTester()
    
    try:
        await tester.setup_session()
        
        # Authentication
        if not await tester.register_and_login():
            print("❌ Authentication failed, cannot proceed with testing")
            return
        
        # Run all test suites
        await tester.test_business_information_consolidation()
        await tester.test_comprehensive_license_agreements()
        await tester.test_automated_licensing_workflows()
        await tester.test_comprehensive_dashboard()
        await tester.test_master_platform_licensing()
        await tester.test_authentication_and_authorization()
        await tester.test_error_handling_and_responses()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())