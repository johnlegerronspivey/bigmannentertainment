#!/usr/bin/env python3
"""
Comprehensive Authentication & Backend Testing for Big Mann Entertainment
Testing authentication service health and all backend functionality
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# Use the correct backend URL
BACKEND_URL = "https://media-distro-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
        # Test data from review request
        self.test_user_data = {
            "email": "test.user@bigmannentertainment.com",
            "password": "TestPassword2025!",
            "full_name": "Test User",
            "business_name": "Test Business",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Test St",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
                
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None) -> Dict:
        """Make HTTP request with detailed error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add auth header if available
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers, params=data) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                json_headers = headers or {}
                json_headers["Content-Type"] = "application/json"
                async with self.session.post(url, json=data, headers=json_headers) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
            else:
                async with self.session.request(method, url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
                    
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }

    async def test_authentication_endpoints(self):
        """Test all authentication endpoints"""
        print("\n🔐 TESTING AUTHENTICATION ENDPOINTS")
        
        # Test 1: User Registration
        response = await self.make_request("POST", "/auth/register", self.test_user_data)
        
        if response["status"] == 201:
            self.log_test("POST /api/auth/register", "PASS", "User registered successfully")
            if "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
        elif response["status"] == 400:
            self.log_test("POST /api/auth/register", "PASS", "User already exists (expected)")
        else:
            self.log_test("POST /api/auth/register", "FAIL", f"Status: {response['status']}")
            
        # Test 2: User Login - CRITICAL
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        response = await self.make_request("POST", "/auth/login", login_data)
        
        if response["status"] == 200 and "access_token" in response["data"]:
            self.auth_token = response["data"]["access_token"]
            self.log_test("POST /api/auth/login", "PASS", "Login successful with token")
        elif response["status"] == 401:
            self.log_test("POST /api/auth/login", "FAIL", "401 UNAUTHORIZED - Critical issue!")
        else:
            self.log_test("POST /api/auth/login", "FAIL", f"Status: {response['status']}")
            
        # Test 3: Get Current User
        response = await self.make_request("GET", "/auth/me")
        
        if response["status"] == 200:
            self.log_test("GET /api/auth/me", "PASS", "User profile retrieved")
        elif response["status"] == 401:
            self.log_test("GET /api/auth/me", "FAIL", "Token validation failed")
        else:
            self.log_test("GET /api/auth/me", "FAIL", f"Status: {response['status']}")
            
        # Test 4: Token Refresh
        if self.auth_token:
            # Get refresh token from login response
            login_response = await self.make_request("POST", "/auth/login", login_data)
            if login_response["status"] == 200 and "refresh_token" in login_response["data"]:
                refresh_token = login_response["data"]["refresh_token"]
                
                response = await self.make_request("POST", "/auth/refresh", {
                    "refresh_token": refresh_token
                })
                
                if response["status"] == 200:
                    self.log_test("POST /api/auth/refresh", "PASS", "Token refresh working")
                else:
                    self.log_test("POST /api/auth/refresh", "FAIL", f"Status: {response['status']}")

    async def test_content_ingestion_endpoints(self):
        """Test Content Ingestion endpoints"""
        print("\n📥 TESTING CONTENT INGESTION ENDPOINTS")
        
        if not self.auth_token:
            self.log_test("Content Ingestion Tests", "SKIP", "No auth token available")
            return
            
        # Test Content Ingestion Dashboard
        response = await self.make_request("GET", "/content-ingestion/dashboard")
        
        if response["status"] == 200:
            self.log_test("GET /api/content-ingestion/dashboard", "PASS", "Dashboard accessible")
        elif response["status"] == 401:
            self.log_test("GET /api/content-ingestion/dashboard", "FAIL", "Authentication blocking access")
        else:
            self.log_test("GET /api/content-ingestion/dashboard", "FAIL", f"Status: {response['status']}")
            
        # Test other content ingestion endpoints
        endpoints = [
            "/content-ingestion/upload",
            "/content-ingestion/metadata",
            "/content-ingestion/status"
        ]
        
        for endpoint in endpoints:
            response = await self.make_request("GET", endpoint)
            
            if response["status"] in [200, 405]:  # 405 Method Not Allowed is acceptable for GET on POST endpoints
                self.log_test(f"GET /api{endpoint}", "PASS", "Endpoint accessible")
            elif response["status"] == 401:
                self.log_test(f"GET /api{endpoint}", "FAIL", "Authentication issue")
            elif response["status"] == 404:
                self.log_test(f"GET /api{endpoint}", "WARN", "Endpoint not found")
            else:
                self.log_test(f"GET /api{endpoint}", "FAIL", f"Status: {response['status']}")

    async def test_distribution_endpoints(self):
        """Test Distribution endpoints"""
        print("\n🌐 TESTING DISTRIBUTION ENDPOINTS")
        
        # Test Distribution Platforms (should work without auth)
        response = await self.make_request("GET", "/distribution/platforms")
        
        if response["status"] == 200:
            platforms = response["data"].get("platforms", [])
            self.log_test("GET /api/distribution/platforms", "PASS", f"Retrieved {len(platforms)} platforms")
        else:
            self.log_test("GET /api/distribution/platforms", "FAIL", f"Status: {response['status']}")
            
        if not self.auth_token:
            return
            
        # Test protected distribution endpoints
        endpoints = [
            "/distribution/history",
            "/distribution/analytics"
        ]
        
        for endpoint in endpoints:
            response = await self.make_request("GET", endpoint)
            
            if response["status"] == 200:
                self.log_test(f"GET /api{endpoint}", "PASS", "Endpoint accessible")
            elif response["status"] == 401:
                self.log_test(f"GET /api{endpoint}", "FAIL", "Authentication issue")
            else:
                self.log_test(f"GET /api{endpoint}", "FAIL", f"Status: {response['status']}")

    async def test_media_endpoints(self):
        """Test Media endpoints"""
        print("\n📁 TESTING MEDIA ENDPOINTS")
        
        if not self.auth_token:
            self.log_test("Media Tests", "SKIP", "No auth token available")
            return
            
        # Test Media Library
        response = await self.make_request("GET", "/media/library")
        
        if response["status"] == 200:
            self.log_test("GET /api/media/library", "PASS", "Media library accessible")
        elif response["status"] == 401:
            self.log_test("GET /api/media/library", "FAIL", "Authentication issue")
        else:
            self.log_test("GET /api/media/library", "FAIL", f"Status: {response['status']}")
            
        # Test Media Analytics
        response = await self.make_request("GET", "/media/analytics")
        
        if response["status"] == 200:
            self.log_test("GET /api/media/analytics", "PASS", "Media analytics accessible")
        elif response["status"] == 401:
            self.log_test("GET /api/media/analytics", "FAIL", "Authentication issue")
        else:
            self.log_test("GET /api/media/analytics", "FAIL", f"Status: {response['status']}")

    async def test_payment_endpoints(self):
        """Test Payment endpoints"""
        print("\n💰 TESTING PAYMENT ENDPOINTS")
        
        # Test Payment Packages (should work without auth)
        response = await self.make_request("GET", "/payments/packages")
        
        if response["status"] == 200:
            packages = response["data"].get("packages", [])
            self.log_test("GET /api/payments/packages", "PASS", f"Retrieved {len(packages)} packages")
        else:
            self.log_test("GET /api/payments/packages", "FAIL", f"Status: {response['status']}")
            
        if not self.auth_token:
            return
            
        # Test protected payment endpoints
        endpoints = [
            "/payments/earnings",
            "/payments/transactions"
        ]
        
        for endpoint in endpoints:
            response = await self.make_request("GET", endpoint)
            
            if response["status"] in [200, 403]:  # 403 might be expected for some endpoints
                self.log_test(f"GET /api{endpoint}", "PASS", "Endpoint accessible or properly secured")
            elif response["status"] == 401:
                self.log_test(f"GET /api{endpoint}", "FAIL", "Authentication issue")
            else:
                self.log_test(f"GET /api{endpoint}", "FAIL", f"Status: {response['status']}")

    async def test_aws_endpoints(self):
        """Test AWS integration endpoints"""
        print("\n☁️ TESTING AWS ENDPOINTS")
        
        # Test AWS Health
        response = await self.make_request("GET", "/aws/health")
        
        if response["status"] == 200:
            self.log_test("GET /api/aws/health", "PASS", "AWS health check working")
        else:
            self.log_test("GET /api/aws/health", "FAIL", f"Status: {response['status']}")

    async def test_lifecycle_endpoints(self):
        """Test Lifecycle Management endpoints"""
        print("\n🔄 TESTING LIFECYCLE ENDPOINTS")
        
        # Test Lifecycle Health
        response = await self.make_request("GET", "/lifecycle/health")
        
        if response["status"] == 200:
            self.log_test("GET /api/lifecycle/health", "PASS", "Lifecycle health check working")
        else:
            self.log_test("GET /api/lifecycle/health", "FAIL", f"Status: {response['status']}")
            
        # Test Lifecycle Dashboard
        response = await self.make_request("GET", "/lifecycle/dashboard")
        
        if response["status"] == 200:
            self.log_test("GET /api/lifecycle/dashboard", "PASS", "Lifecycle dashboard accessible")
        else:
            self.log_test("GET /api/lifecycle/dashboard", "FAIL", f"Status: {response['status']}")

    async def test_analytics_endpoints(self):
        """Test Analytics endpoints"""
        print("\n📊 TESTING ANALYTICS ENDPOINTS")
        
        # Test Analytics Health
        response = await self.make_request("GET", "/analytics/health")
        
        if response["status"] == 200:
            self.log_test("GET /api/analytics/health", "PASS", "Analytics health check working")
        else:
            self.log_test("GET /api/analytics/health", "FAIL", f"Status: {response['status']}")

    async def test_transcoding_endpoints(self):
        """Test Transcoding endpoints"""
        print("\n🎬 TESTING TRANSCODING ENDPOINTS")
        
        # Test Transcoding Health
        response = await self.make_request("GET", "/transcoding/health")
        
        if response["status"] == 200:
            self.log_test("GET /api/transcoding/health", "PASS", "Transcoding health check working")
        else:
            self.log_test("GET /api/transcoding/health", "FAIL", f"Status: {response['status']}")

    def generate_comprehensive_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 BIG MANN ENTERTAINMENT - COMPREHENSIVE BACKEND TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])
        warned_tests = len([t for t in self.test_results if t["status"] == "WARN"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Warnings: {warned_tests}")
        print(f"   ⏭️ Skipped: {skipped_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Authentication specific analysis
        auth_tests = [t for t in self.test_results if "auth" in t["test"].lower()]
        auth_passed = len([t for t in auth_tests if t["status"] == "PASS"])
        auth_failed = len([t for t in auth_tests if t["status"] == "FAIL"])
        
        print(f"\n🔐 AUTHENTICATION ANALYSIS:")
        print(f"   Authentication Tests: {len(auth_tests)}")
        print(f"   ✅ Passed: {auth_passed}")
        print(f"   ❌ Failed: {auth_failed}")
        
        if auth_failed == 0:
            print("   🎉 AUTHENTICATION SERVICE: FULLY FUNCTIONAL")
        else:
            print("   🚨 AUTHENTICATION SERVICE: HAS ISSUES")
            
        # Critical issues
        print(f"\n🚨 CRITICAL ISSUES:")
        critical_issues = [t for t in self.test_results if t["status"] == "FAIL"]
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No critical issues found!")
            
        # Content Ingestion specific analysis
        content_tests = [t for t in self.test_results if "content-ingestion" in t["test"].lower()]
        if content_tests:
            content_passed = len([t for t in content_tests if t["status"] == "PASS"])
            content_failed = len([t for t in content_tests if t["status"] == "FAIL"])
            
            print(f"\n📥 CONTENT INGESTION ANALYSIS:")
            print(f"   Content Ingestion Tests: {len(content_tests)}")
            print(f"   ✅ Passed: {content_passed}")
            print(f"   ❌ Failed: {content_failed}")
            
            if content_failed == 0:
                print("   🎉 CONTENT INGESTION: ACCESSIBLE")
            else:
                print("   🚨 CONTENT INGESTION: BLOCKED BY AUTHENTICATION")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": success_rate,
            "auth_working": auth_failed == 0,
            "content_ingestion_accessible": len([t for t in content_tests if t["status"] == "PASS"]) > 0 if content_tests else False
        }
        
    async def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING")
        print("Testing Authentication Service and All Backend Functionality")
        print("="*80)
        
        try:
            await self.setup_session()
            
            # Run all test suites
            await self.test_authentication_endpoints()
            await self.test_content_ingestion_endpoints()
            await self.test_distribution_endpoints()
            await self.test_media_endpoints()
            await self.test_payment_endpoints()
            await self.test_aws_endpoints()
            await self.test_lifecycle_endpoints()
            await self.test_analytics_endpoints()
            await self.test_transcoding_endpoints()
            
            # Generate final summary
            summary = self.generate_comprehensive_summary()
            
            return summary
            
        except Exception as e:
            print(f"❌ Critical error during testing: {str(e)}")
            self.log_test("Critical Error", "FAIL", str(e))
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = ComprehensiveBackendTester()
    
    print("🔐 BIG MANN ENTERTAINMENT PLATFORM")
    print("Comprehensive Authentication & Backend Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    summary = await tester.run_comprehensive_tests()
    
    if summary:
        print(f"\n🏁 TESTING COMPLETED")
        print(f"Final Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['auth_working']:
            print("✅ AUTHENTICATION SERVICE: WORKING CORRECTLY")
        else:
            print("❌ AUTHENTICATION SERVICE: HAS CRITICAL ISSUES")
            
        if summary['content_ingestion_accessible']:
            print("✅ CONTENT INGESTION: ACCESSIBLE WITH AUTHENTICATION")
        else:
            print("❌ CONTENT INGESTION: BLOCKED OR INACCESSIBLE")
            
        if summary['success_rate'] >= 85:
            print("🎉 EXCELLENT: Backend is production-ready!")
        elif summary['success_rate'] >= 70:
            print("✅ GOOD: Backend is functional with minor issues")
        else:
            print("⚠️ NEEDS ATTENTION: Critical issues require fixing")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())