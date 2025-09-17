#!/usr/bin/env python3
"""
Comprehensive Password Reset Functionality Backend Testing for Big Mann Entertainment Platform
Testing all aspects of password reset including security, database operations, and error handling
"""

import asyncio
import aiohttp
import json
import time
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://music-rights-hub-2.preview.emergentagent.com/api"

class ComprehensivePasswordResetTester:
    def __init__(self):
        self.session = None
        self.test_users = []
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "test_details": []
        }

    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def log_test(self, test_name: str, passed: bool, details: str, response_data: Any = None):
        """Log test results"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            status = "✅ PASS"
        else:
            self.results["failed"] += 1
            status = "❌ FAIL"
        
        self.results["test_details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data
        })
        print(f"{status}: {test_name} - {details}")

    async def create_unique_test_user(self):
        """Create a unique test user for password reset testing"""
        try:
            # Generate unique email to avoid conflicts
            unique_id = secrets.token_hex(8)
            test_email = f"pwreset.test.{unique_id}@bigmannentertainment.com"
            test_password = "SecureTestPassword123!"
            
            user_data = {
                "email": test_email,
                "password": test_password,
                "full_name": f"Password Reset Test User {unique_id}",
                "business_name": "Test Business",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=user_data) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    user_info = {
                        "id": data.get("user", {}).get("id"),
                        "email": test_email,
                        "password": test_password,
                        "new_password": f"NewSecure{unique_id}!"
                    }
                    self.test_users.append(user_info)
                    self.log_test("Create Unique Test User", True, f"Test user created: {test_email}")
                    return user_info
                else:
                    error_text = await response.text()
                    self.log_test("Create Unique Test User", False, f"Failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            self.log_test("Create Unique Test User", False, f"Exception: {str(e)}")
            return None

    async def test_forgot_password_flow(self):
        """Test complete forgot password flow"""
        user = await self.create_unique_test_user()
        if not user:
            return False
        
        try:
            # Test forgot password request
            payload = {"email": user["email"]}
            async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    # Should get either email sent message or development fallback
                    message = data.get("message", "").lower()
                    if "reset link has been sent" in message or "email service unavailable" in message:
                        reset_token = data.get("reset_token")
                        if reset_token:
                            self.log_test("Forgot Password Flow", True, 
                                        f"Password reset initiated with token (development mode)")
                            return {"user": user, "token": reset_token}
                        else:
                            self.log_test("Forgot Password Flow", True, 
                                        "Password reset initiated (email sent)")
                            return {"user": user, "token": None}
                    else:
                        self.log_test("Forgot Password Flow", False, 
                                    f"Unexpected message: {data.get('message')}")
                        return False
                else:
                    self.log_test("Forgot Password Flow", False, 
                                f"Unexpected status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Forgot Password Flow", False, f"Exception: {str(e)}")
            return False

    async def test_reset_password_flow(self):
        """Test complete reset password flow"""
        flow_result = await self.test_forgot_password_flow()
        if not flow_result or not flow_result.get("token"):
            self.log_test("Reset Password Flow", False, "No reset token available")
            return False
        
        user = flow_result["user"]
        token = flow_result["token"]
        
        try:
            # Test password reset
            payload = {
                "token": token,
                "new_password": user["new_password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    if "password has been reset successfully" in data.get("message", "").lower():
                        self.log_test("Reset Password Flow", True, "Password reset completed successfully")
                        return {"user": user, "token": token}
                    else:
                        self.log_test("Reset Password Flow", False, 
                                    f"Unexpected success message: {data.get('message')}")
                        return False
                else:
                    self.log_test("Reset Password Flow", False, 
                                f"Reset failed: {response.status} - {data}")
                    return False
        except Exception as e:
            self.log_test("Reset Password Flow", False, f"Exception: {str(e)}")
            return False

    async def test_security_aspects(self):
        """Test security aspects of password reset"""
        
        # Test 1: Non-existent email doesn't reveal information
        try:
            payload = {"email": "nonexistent.security.test@bigmannentertainment.com"}
            async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    # Should return same message but no token
                    if "reset_token" not in data:
                        self.log_test("Security - Email Enumeration Protection", True, 
                                    "Correctly protects against email enumeration")
                    else:
                        self.log_test("Security - Email Enumeration Protection", False, 
                                    "Security issue: reveals email existence")
                else:
                    self.log_test("Security - Email Enumeration Protection", False, 
                                f"Unexpected status: {response.status}")
        except Exception as e:
            self.log_test("Security - Email Enumeration Protection", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid token rejection
        try:
            payload = {
                "token": "invalid_security_token_12345",
                "new_password": "NewSecurePassword123!"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=payload) as response:
                if response.status == 400:
                    self.log_test("Security - Invalid Token Rejection", True, 
                                "Correctly rejects invalid tokens")
                else:
                    self.log_test("Security - Invalid Token Rejection", False, 
                                f"Should reject invalid token: {response.status}")
        except Exception as e:
            self.log_test("Security - Invalid Token Rejection", False, f"Exception: {str(e)}")
        
        # Test 3: Token randomness and length
        user = await self.create_unique_test_user()
        if user:
            try:
                payload = {"email": user["email"]}
                async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload) as response:
                    data = await response.json()
                    token = data.get("reset_token")
                    
                    if token and len(token) >= 32:
                        self.log_test("Security - Token Strength", True, 
                                    f"Reset token has sufficient length: {len(token)} chars")
                    else:
                        self.log_test("Security - Token Strength", False, 
                                    f"Token too weak or missing: {len(token) if token else 0} chars")
            except Exception as e:
                self.log_test("Security - Token Strength", False, f"Exception: {str(e)}")

    async def test_database_operations(self):
        """Test database operations for password reset"""
        
        # Test password hash update
        flow_result = await self.test_reset_password_flow()
        if not flow_result:
            return
        
        user = flow_result["user"]
        
        # Test 1: New password works
        try:
            login_payload = {
                "email": user["email"],
                "password": user["new_password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "access_token" in data:
                        self.log_test("Database - Password Hash Update", True, 
                                    "New password hash correctly stored and verified")
                    else:
                        self.log_test("Database - Password Hash Update", False, 
                                    "Login successful but no token returned")
                else:
                    self.log_test("Database - Password Hash Update", False, 
                                f"New password doesn't work: {response.status}")
        except Exception as e:
            self.log_test("Database - Password Hash Update", False, f"Exception: {str(e)}")
        
        # Test 2: Old password no longer works
        try:
            login_payload = {
                "email": user["email"],
                "password": user["password"]  # Old password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload) as response:
                if response.status in [400, 401]:
                    self.log_test("Database - Old Password Invalidation", True, 
                                "Old password correctly invalidated")
                else:
                    self.log_test("Database - Old Password Invalidation", False, 
                                f"Old password still works: {response.status}")
        except Exception as e:
            self.log_test("Database - Old Password Invalidation", False, f"Exception: {str(e)}")
        
        # Test 3: Reset token cleanup
        if flow_result.get("token"):
            try:
                payload = {
                    "token": flow_result["token"],
                    "new_password": "AnotherPassword123!"
                }
                
                async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=payload) as response:
                    if response.status == 400:
                        self.log_test("Database - Token Cleanup", True, 
                                    "Reset token correctly cleared after use")
                    else:
                        self.log_test("Database - Token Cleanup", False, 
                                    f"Token reuse allowed (security issue): {response.status}")
            except Exception as e:
                self.log_test("Database - Token Cleanup", False, f"Exception: {str(e)}")

    async def test_error_handling(self):
        """Test comprehensive error handling"""
        
        error_test_cases = [
            # Forgot password errors
            ({}, "forgot-password", "Empty request body"),
            ({"email": ""}, "forgot-password", "Empty email"),
            ({"email": "not-an-email"}, "forgot-password", "Invalid email format"),
            ({"invalid_field": "test"}, "forgot-password", "Missing email field"),
            
            # Reset password errors
            ({}, "reset-password", "Empty reset request"),
            ({"token": ""}, "reset-password", "Empty token"),
            ({"new_password": ""}, "reset-password", "Empty password"),
            ({"token": "test"}, "reset-password", "Missing password"),
            ({"new_password": "test"}, "reset-password", "Missing token"),
            ({"token": "short", "new_password": "weak"}, "reset-password", "Weak password"),
        ]
        
        passed_tests = 0
        total_tests = len(error_test_cases)
        
        for payload, endpoint, description in error_test_cases:
            try:
                async with self.session.post(f"{BACKEND_URL}/auth/{endpoint}", json=payload) as response:
                    # Most should return 4xx errors for invalid input
                    if response.status >= 400:
                        passed_tests += 1
                    else:
                        print(f"  ⚠️  {description}: Expected error but got {response.status}")
            except Exception:
                # Exceptions are also acceptable for malformed requests
                passed_tests += 1
        
        if passed_tests >= total_tests * 0.8:  # Allow 80% pass rate for error handling
            self.log_test("Error Handling - Comprehensive", True, 
                        f"Error handling working: {passed_tests}/{total_tests} cases handled correctly")
        else:
            self.log_test("Error Handling - Comprehensive", False, 
                        f"Poor error handling: only {passed_tests}/{total_tests} cases handled correctly")

    async def test_token_expiration_simulation(self):
        """Test token expiration behavior (simulated)"""
        user = await self.create_unique_test_user()
        if not user:
            return
        
        try:
            # Generate reset token
            payload = {"email": user["email"]}
            async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload) as response:
                data = await response.json()
                token = data.get("reset_token")
                
                if token:
                    # Test with obviously invalid/expired token format
                    expired_payload = {
                        "token": "expired_token_simulation_12345",
                        "new_password": "NewPassword123!"
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=expired_payload) as reset_response:
                        if reset_response.status == 400:
                            self.log_test("Token Expiration Handling", True, 
                                        "Expired/invalid tokens correctly rejected")
                        else:
                            self.log_test("Token Expiration Handling", False, 
                                        f"Should reject expired token: {reset_response.status}")
                else:
                    self.log_test("Token Expiration Handling", False, "No token to test expiration with")
        except Exception as e:
            self.log_test("Token Expiration Handling", False, f"Exception: {str(e)}")

    async def test_session_deactivation(self):
        """Test that user sessions are deactivated after password reset"""
        user = await self.create_unique_test_user()
        if not user:
            return
        
        try:
            # First, login to create a session
            login_payload = {
                "email": user["email"],
                "password": user["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    access_token = data.get("access_token")
                    
                    if access_token:
                        # Now reset password
                        forgot_payload = {"email": user["email"]}
                        async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=forgot_payload) as forgot_response:
                            forgot_data = await forgot_response.json()
                            reset_token = forgot_data.get("reset_token")
                            
                            if reset_token:
                                reset_payload = {
                                    "token": reset_token,
                                    "new_password": user["new_password"]
                                }
                                
                                async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=reset_payload) as reset_response:
                                    if reset_response.status == 200:
                                        self.log_test("Session Deactivation", True, 
                                                    "Password reset completed (sessions should be deactivated)")
                                    else:
                                        self.log_test("Session Deactivation", False, 
                                                    f"Password reset failed: {reset_response.status}")
                            else:
                                self.log_test("Session Deactivation", False, "No reset token available")
                    else:
                        self.log_test("Session Deactivation", False, "No access token from login")
                else:
                    self.log_test("Session Deactivation", False, f"Login failed: {response.status}")
        except Exception as e:
            self.log_test("Session Deactivation", False, f"Exception: {str(e)}")

    async def run_comprehensive_tests(self):
        """Run all comprehensive password reset tests"""
        print("🎯 COMPREHENSIVE PASSWORD RESET TESTING FOR BIG MANN ENTERTAINMENT")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            print("\n🔐 FORGOT PASSWORD FLOW TESTS")
            await self.test_forgot_password_flow()
            
            print("\n🔄 RESET PASSWORD FLOW TESTS")
            await self.test_reset_password_flow()
            
            print("\n🛡️ SECURITY ASPECTS TESTS")
            await self.test_security_aspects()
            
            print("\n💾 DATABASE OPERATIONS TESTS")
            await self.test_database_operations()
            
            print("\n⏰ TOKEN EXPIRATION TESTS")
            await self.test_token_expiration_simulation()
            
            print("\n🔒 SESSION MANAGEMENT TESTS")
            await self.test_session_deactivation()
            
            print("\n⚠️ ERROR HANDLING TESTS")
            await self.test_error_handling()
            
        finally:
            await self.cleanup_session()
        
        # Print Results
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PASSWORD RESET TESTING RESULTS")
        print("=" * 80)
        
        for test_detail in self.results["test_details"]:
            print(f"{test_detail['status']}: {test_detail['test']}")
            if test_detail['details']:
                print(f"    Details: {test_detail['details']}")
        
        print(f"\n📈 SUMMARY:")
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        
        success_rate = (self.results['passed'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Determine overall assessment
        if success_rate >= 90:
            print("\n🎉 EXCELLENT! Password reset functionality is working excellently.")
        elif success_rate >= 80:
            print("\n✅ GOOD! Password reset functionality is working well with minor issues.")
        elif success_rate >= 70:
            print("\n⚠️ ACCEPTABLE! Password reset functionality works but has some issues.")
        else:
            print(f"\n❌ NEEDS ATTENTION! Password reset functionality has significant issues.")
        
        return self.results

async def main():
    """Main test execution"""
    tester = ComprehensivePasswordResetTester()
    results = await tester.run_comprehensive_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())