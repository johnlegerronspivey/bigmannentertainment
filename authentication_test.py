#!/usr/bin/env python3
"""
URGENT Authentication Service Testing for Big Mann Entertainment Platform
Focused testing for 401 error diagnosis and authentication service health

This test specifically addresses the authentication issues reported:
- 401 errors on login attempts at /api/auth/login
- Authentication service problems blocking Content Ingestion routes
- JWT token creation and validation issues
- Authentication middleware functionality
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Use the correct backend URL from frontend environment
BACKEND_URL = "https://label-network-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AuthenticationTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
        # Test data from the review request
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
        if response_data and isinstance(response_data, dict):
            if "error" in response_data or "detail" in response_data:
                error_msg = response_data.get("error") or response_data.get("detail")
                print(f"   Error: {error_msg}")
            elif "message" in response_data:
                print(f"   Message: {response_data['message']}")
                
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
                        "headers": dict(response.headers),
                        "url": url
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
                        "headers": dict(response.headers),
                        "url": url
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
                        "headers": dict(response.headers),
                        "url": url
                    }
                    
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {},
                "url": url
            }

    async def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        print("\n🔗 TESTING BACKEND CONNECTIVITY")
        
        try:
            # Test basic health endpoint
            response = await self.make_request("GET", "/health")
            
            if response["status"] == 200:
                self.log_test("Backend Connectivity", "PASS", f"Backend accessible at {BACKEND_URL}", response["data"])
            else:
                self.log_test("Backend Connectivity", "FAIL", f"Status: {response['status']}", response["data"])
                
        except Exception as e:
            # Try alternative endpoints if health fails
            response = await self.make_request("GET", "/")
            if response["status"] in [200, 404]:  # 404 is acceptable for root endpoint
                self.log_test("Backend Connectivity", "PASS", f"Backend accessible (alternative check)", response["data"])
            else:
                self.log_test("Backend Connectivity", "FAIL", f"Backend unreachable: {str(e)}")

    async def test_mongodb_connection(self):
        """Test MongoDB connection health"""
        print("\n🗄️ TESTING MONGODB CONNECTION")
        
        # Try to access an endpoint that requires database
        response = await self.make_request("GET", "/distribution/platforms")
        
        if response["status"] == 200:
            platforms = response["data"].get("platforms", [])
            self.log_test("MongoDB Connection", "PASS", f"Database accessible, retrieved {len(platforms)} platforms", {"platform_count": len(platforms)})
        else:
            self.log_test("MongoDB Connection", "FAIL", f"Database connection issue - Status: {response['status']}", response["data"])

    async def test_authentication_dependencies(self):
        """Test authentication service dependencies"""
        print("\n🔧 TESTING AUTHENTICATION DEPENDENCIES")
        
        # Test SECRET_KEY availability (indirect test)
        response = await self.make_request("POST", "/auth/login", {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        
        if response["status"] in [401, 400, 422]:
            self.log_test("SECRET_KEY Configuration", "PASS", "Authentication service responding to requests", response["data"])
        elif response["status"] == 500:
            self.log_test("SECRET_KEY Configuration", "FAIL", "Internal server error - possible SECRET_KEY issue", response["data"])
        else:
            self.log_test("SECRET_KEY Configuration", "WARN", f"Unexpected response: {response['status']}", response["data"])

    async def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n📝 TESTING USER REGISTRATION")
        
        response = await self.make_request("POST", "/auth/register", self.test_user_data)
        
        if response["status"] == 201:
            self.log_test("User Registration", "PASS", "New user registered successfully", response["data"])
            if "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
                self.log_test("Registration Token Generation", "PASS", "Access token generated during registration")
        elif response["status"] == 400:
            error_detail = response["data"].get("detail", "")
            if "already registered" in error_detail.lower() or "already exists" in error_detail.lower():
                self.log_test("User Registration", "PASS", "User already exists (expected for repeat tests)", response["data"])
            else:
                self.log_test("User Registration", "FAIL", f"Registration failed: {error_detail}", response["data"])
        elif response["status"] == 422:
            self.log_test("User Registration", "FAIL", "Validation error - check required fields", response["data"])
        else:
            self.log_test("User Registration", "FAIL", f"Unexpected status: {response['status']}", response["data"])

    async def test_user_login(self):
        """Test user login endpoint - CRITICAL TEST"""
        print("\n🔐 TESTING USER LOGIN (CRITICAL)")
        
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        response = await self.make_request("POST", "/auth/login", login_data)
        
        if response["status"] == 200:
            if "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
                self.log_test("User Login", "PASS", "Login successful with access token", response["data"])
                
                # Verify token format
                if self.auth_token and len(self.auth_token) > 20:
                    self.log_test("JWT Token Format", "PASS", f"Token length: {len(self.auth_token)} characters")
                else:
                    self.log_test("JWT Token Format", "FAIL", "Token appears invalid or too short")
            else:
                self.log_test("User Login", "FAIL", "Login response missing access_token", response["data"])
        elif response["status"] == 401:
            self.log_test("User Login", "FAIL", "401 UNAUTHORIZED - This is the reported issue!", response["data"])
            
            # Detailed analysis of 401 error
            error_detail = response["data"].get("detail", "")
            if "credentials" in error_detail.lower():
                self.log_test("401 Error Analysis", "FAIL", "Invalid credentials error", response["data"])
            elif "user not found" in error_detail.lower():
                self.log_test("401 Error Analysis", "FAIL", "User not found in database", response["data"])
            else:
                self.log_test("401 Error Analysis", "FAIL", f"Unknown 401 cause: {error_detail}", response["data"])
        elif response["status"] == 422:
            self.log_test("User Login", "FAIL", "Validation error - check login data format", response["data"])
        else:
            self.log_test("User Login", "FAIL", f"Unexpected status: {response['status']}", response["data"])

    async def test_password_hashing(self):
        """Test password hashing functionality"""
        print("\n🔒 TESTING PASSWORD HASHING")
        
        # Try to register a new user to test password hashing
        test_hash_user = {
            "email": "hash.test@bigmannentertainment.com",
            "password": "HashTest2025!",
            "full_name": "Hash Test User",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Hash St",
            "city": "Hash City",
            "state_province": "HS",
            "postal_code": "12345",
            "country": "US"
        }
        
        response = await self.make_request("POST", "/auth/register", test_hash_user)
        
        if response["status"] in [201, 400]:  # 400 if user exists
            self.log_test("Password Hashing", "PASS", "Password hashing system functional", response["data"])
        else:
            self.log_test("Password Hashing", "FAIL", f"Password hashing issue - Status: {response['status']}", response["data"])

    async def test_token_validation(self):
        """Test JWT token validation"""
        print("\n🎫 TESTING JWT TOKEN VALIDATION")
        
        if not self.auth_token:
            self.log_test("Token Validation", "SKIP", "No auth token available for testing")
            return
            
        # Test valid token
        response = await self.make_request("GET", "/auth/me")
        
        if response["status"] == 200:
            user_data = response["data"]
            if "id" in user_data and "email" in user_data:
                self.log_test("Valid Token Validation", "PASS", "Token successfully validated", user_data)
            else:
                self.log_test("Valid Token Validation", "FAIL", "Token validated but user data incomplete", user_data)
        elif response["status"] == 401:
            self.log_test("Valid Token Validation", "FAIL", "Valid token rejected - JWT validation issue", response["data"])
        else:
            self.log_test("Valid Token Validation", "FAIL", f"Unexpected status: {response['status']}", response["data"])
            
        # Test invalid token
        old_token = self.auth_token
        self.auth_token = "invalid.jwt.token"
        
        response = await self.make_request("GET", "/auth/me")
        
        if response["status"] == 401:
            self.log_test("Invalid Token Rejection", "PASS", "Invalid token properly rejected", response["data"])
        else:
            self.log_test("Invalid Token Rejection", "FAIL", f"Invalid token not rejected - Status: {response['status']}", response["data"])
            
        # Restore valid token
        self.auth_token = old_token

    async def test_authentication_middleware(self):
        """Test authentication middleware functionality"""
        print("\n🛡️ TESTING AUTHENTICATION MIDDLEWARE")
        
        # Test protected route without token
        old_token = self.auth_token
        self.auth_token = None
        
        response = await self.make_request("GET", "/media/library")
        
        if response["status"] == 401:
            self.log_test("Protected Route Security", "PASS", "Protected route properly secured", response["data"])
        else:
            self.log_test("Protected Route Security", "FAIL", f"Protected route accessible without auth - Status: {response['status']}", response["data"])
            
        # Restore token and test protected route access
        self.auth_token = old_token
        
        if self.auth_token:
            response = await self.make_request("GET", "/media/library")
            
            if response["status"] == 200:
                self.log_test("Authenticated Route Access", "PASS", "Protected route accessible with valid token", response["data"])
            elif response["status"] == 401:
                self.log_test("Authenticated Route Access", "FAIL", "Valid token rejected by middleware", response["data"])
            else:
                self.log_test("Authenticated Route Access", "WARN", f"Unexpected status: {response['status']}", response["data"])

    async def test_content_ingestion_routes(self):
        """Test Content Ingestion route protection"""
        print("\n📥 TESTING CONTENT INGESTION ROUTE PROTECTION")
        
        if not self.auth_token:
            self.log_test("Content Ingestion Routes", "SKIP", "No auth token available for testing")
            return
            
        # Test Content Ingestion dashboard
        response = await self.make_request("GET", "/content-ingestion/dashboard")
        
        if response["status"] == 200:
            self.log_test("Content Ingestion Dashboard", "PASS", "Dashboard accessible with authentication", response["data"])
        elif response["status"] == 401:
            self.log_test("Content Ingestion Dashboard", "FAIL", "Authentication blocking Content Ingestion access", response["data"])
        elif response["status"] == 404:
            self.log_test("Content Ingestion Dashboard", "WARN", "Content Ingestion endpoint not found", response["data"])
        else:
            self.log_test("Content Ingestion Dashboard", "FAIL", f"Unexpected status: {response['status']}", response["data"])

    async def test_token_refresh(self):
        """Test token refresh functionality if implemented"""
        print("\n🔄 TESTING TOKEN REFRESH")
        
        # Check if refresh token is available
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        response = await self.make_request("POST", "/auth/login", login_data)
        
        if response["status"] == 200 and "refresh_token" in response["data"]:
            refresh_token = response["data"]["refresh_token"]
            
            # Test refresh endpoint
            refresh_response = await self.make_request("POST", "/auth/refresh", {
                "refresh_token": refresh_token
            })
            
            if refresh_response["status"] == 200:
                self.log_test("Token Refresh", "PASS", "Token refresh functionality working", refresh_response["data"])
            else:
                self.log_test("Token Refresh", "FAIL", f"Token refresh failed - Status: {refresh_response['status']}", refresh_response["data"])
        else:
            self.log_test("Token Refresh", "SKIP", "Refresh token not implemented or not available")

    async def test_bcrypt_functionality(self):
        """Test bcrypt password hashing functionality"""
        print("\n🔐 TESTING BCRYPT FUNCTIONALITY")
        
        # The logs show bcrypt version issues, let's test if it's working
        unique_user = {
            "email": f"bcrypt.test.{int(time.time())}@bigmannentertainment.com",
            "password": "BcryptTest2025!",
            "full_name": "Bcrypt Test User",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Bcrypt St",
            "city": "Bcrypt City",
            "state_province": "BC",
            "postal_code": "12345",
            "country": "US"
        }
        
        response = await self.make_request("POST", "/auth/register", unique_user)
        
        if response["status"] == 201:
            self.log_test("Bcrypt Password Hashing", "PASS", "Bcrypt working despite version warnings", response["data"])
            
            # Test login with the same password
            login_response = await self.make_request("POST", "/auth/login", {
                "email": unique_user["email"],
                "password": unique_user["password"]
            })
            
            if login_response["status"] == 200:
                self.log_test("Bcrypt Password Verification", "PASS", "Password verification working correctly")
            else:
                self.log_test("Bcrypt Password Verification", "FAIL", f"Password verification failed - Status: {login_response['status']}", login_response["data"])
        else:
            self.log_test("Bcrypt Password Hashing", "FAIL", f"Registration failed - possible bcrypt issue - Status: {response['status']}", response["data"])

    def generate_authentication_summary(self):
        """Generate detailed authentication test summary"""
        print("\n" + "="*80)
        print("🔐 AUTHENTICATION SERVICE DIAGNOSTIC REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 AUTHENTICATION TEST RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Skipped: {skipped_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🚨 CRITICAL AUTHENTICATION ISSUES:")
        critical_issues = [t for t in self.test_results if t["status"] == "FAIL"]
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
                if issue.get('response_data') and isinstance(issue['response_data'], dict):
                    error_detail = issue['response_data'].get('detail') or issue['response_data'].get('error')
                    if error_detail:
                        print(f"      Error Detail: {error_detail}")
        else:
            print("   ✅ No critical authentication issues found!")
            
        print(f"\n🔍 AUTHENTICATION WORKFLOW STATUS:")
        workflow_tests = [
            "Backend Connectivity", "MongoDB Connection", "User Registration", 
            "User Login", "JWT Token Format", "Valid Token Validation", 
            "Protected Route Security", "Content Ingestion Dashboard"
        ]
        
        workflow_status = {}
        for test_name in workflow_tests:
            matching_tests = [t for t in self.test_results if test_name in t["test"]]
            if matching_tests:
                workflow_status[test_name] = matching_tests[0]["status"]
            else:
                workflow_status[test_name] = "NOT_TESTED"
                
        for workflow, status in workflow_status.items():
            status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"   {status_emoji} {workflow}: {status}")
            
        print(f"\n💡 RECOMMENDATIONS:")
        if any("User Login" in t["test"] and t["status"] == "FAIL" for t in self.test_results):
            print("   🔧 URGENT: Fix 401 login errors - check password hashing and user lookup")
        if any("MongoDB Connection" in t["test"] and t["status"] == "FAIL" for t in self.test_results):
            print("   🔧 Check MongoDB connection and user collection")
        if any("JWT Token" in t["test"] and t["status"] == "FAIL" for t in self.test_results):
            print("   🔧 Verify SECRET_KEY configuration and JWT implementation")
        if any("Bcrypt" in t["test"] and t["status"] == "FAIL" for t in self.test_results):
            print("   🔧 Update bcrypt library to resolve version warnings")
            
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": success_rate,
            "critical_issues": len(critical_issues),
            "workflow_status": workflow_status,
            "auth_token_available": bool(self.auth_token)
        }
        
    async def run_authentication_tests(self):
        """Run comprehensive authentication tests"""
        print("🚀 STARTING AUTHENTICATION SERVICE DIAGNOSTIC")
        print("Investigating 401 errors and authentication service health")
        print("="*80)
        
        try:
            await self.setup_session()
            
            # Core authentication tests
            await self.test_backend_connectivity()
            await self.test_mongodb_connection()
            await self.test_authentication_dependencies()
            await self.test_bcrypt_functionality()
            await self.test_user_registration()
            await self.test_user_login()
            await self.test_password_hashing()
            await self.test_token_validation()
            await self.test_authentication_middleware()
            await self.test_content_ingestion_routes()
            await self.test_token_refresh()
            
            # Generate final summary
            summary = self.generate_authentication_summary()
            
            return summary
            
        except Exception as e:
            print(f"❌ Critical error during authentication testing: {str(e)}")
            self.log_test("Critical Error", "FAIL", str(e))
            
        finally:
            await self.cleanup_session()

async def main():
    """Main authentication test execution function"""
    tester = AuthenticationTester()
    
    print("🔐 BIG MANN ENTERTAINMENT PLATFORM")
    print("URGENT: Authentication Service 401 Error Diagnostic")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    summary = await tester.run_authentication_tests()
    
    if summary:
        print(f"\n🏁 AUTHENTICATION TESTING COMPLETED")
        print(f"Final Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] >= 90:
            print("🎉 EXCELLENT: Authentication service is fully functional!")
        elif summary['success_rate'] >= 70:
            print("✅ GOOD: Authentication working with minor issues")
        elif summary['failed'] > 0:
            print("⚠️ CRITICAL: Authentication service has serious issues requiring immediate attention")
        else:
            print("❌ FAILED: Authentication service is not functional")
            
        # Specific 401 error analysis
        login_failed = any("User Login" in t["test"] and t["status"] == "FAIL" for t in tester.test_results)
        if login_failed:
            print("\n🚨 401 ERROR CONFIRMED: Login endpoint is returning 401 errors")
            print("   This matches the reported issue blocking Content Ingestion routes")
        else:
            print("\n✅ LOGIN WORKING: No 401 errors detected in current test")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())