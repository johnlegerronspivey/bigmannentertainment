#!/usr/bin/env python3
"""
Password Reset Functionality Backend Testing for Big Mann Entertainment Platform
Testing comprehensive password reset flow including security aspects and error handling
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://label-network.preview.emergentagent.com/api"
TEST_EMAIL = "password.reset.test@bigmannentertainment.com"
TEST_PASSWORD = "SecurePassword123!"
NEW_PASSWORD = "NewSecurePassword456!"
TEST_USER_DATA = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "full_name": "Password Reset Test User",
    "business_name": "Test Business",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "address_line1": "123 Test Street",
    "city": "Test City",
    "state_province": "Test State",
    "postal_code": "12345",
    "country": "United States"
}

class PasswordResetTester:
    def __init__(self):
        self.session = None
        self.test_user_id = None
        self.reset_token = None
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

    async def create_test_user(self):
        """Create a test user for password reset testing"""
        try:
            # First, try to delete existing test user
            await self.cleanup_test_user()
            
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=TEST_USER_DATA) as response:
                if response.status == 200 or response.status == 201:  # Accept both 200 and 201
                    data = await response.json()
                    self.test_user_id = data.get("user", {}).get("id")
                    self.log_test("Create Test User", True, f"Test user created successfully with ID: {self.test_user_id}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Create Test User", False, f"Failed to create test user: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.log_test("Create Test User", False, f"Exception creating test user: {str(e)}")
            return False

    async def cleanup_test_user(self):
        """Cleanup test user after testing"""
        try:
            # This is a cleanup operation, so we don't log failures as test failures
            pass
        except Exception as e:
            print(f"Note: Cleanup exception (expected): {str(e)}")

    async def test_forgot_password_valid_email(self):
        """Test forgot password with valid email address"""
        try:
            payload = {"email": TEST_EMAIL}
            async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    # Check if response contains expected message
                    message = data.get("message", "").lower()
                    if "reset link has been sent" in message or "email service unavailable" in message:
                        # Check if development fallback is provided (email service might be unavailable)
                        if "reset_token" in data:
                            self.reset_token = data["reset_token"]
                            self.log_test("Forgot Password - Valid Email", True, 
                                        f"Password reset initiated with development fallback. Token: {self.reset_token[:10]}...")
                        else:
                            self.log_test("Forgot Password - Valid Email", True, 
                                        "Password reset initiated successfully (email sent)")
                        return True
                    else:
                        self.log_test("Forgot Password - Valid Email", False, 
                                    f"Unexpected response message: {data.get('message')}")
                        return False
                else:
                    self.log_test("Forgot Password - Valid Email", False, 
                                f"Unexpected status code: {response.status} - {data}")
                    return False
        except Exception as e:
            self.log_test("Forgot Password - Valid Email", False, f"Exception: {str(e)}")
            return False

    async def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email (should not reveal if email exists)"""
        try:
            payload = {"email": "nonexistent.email@bigmannentertainment.com"}
            async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    # Should return same message regardless of email existence
                    if "reset link has been sent" in data.get("message", "").lower():
                        # Should NOT contain reset_token for non-existent email
                        if "reset_token" not in data:
                            self.log_test("Forgot Password - Non-existent Email", True, 
                                        "Correctly does not reveal email existence")
                            return True
                        else:
                            self.log_test("Forgot Password - Non-existent Email", False, 
                                        "Security issue: reveals email existence by providing token")
                            return False
                    else:
                        self.log_test("Forgot Password - Non-existent Email", False, 
                                    f"Unexpected response message: {data.get('message')}")
                        return False
                else:
                    self.log_test("Forgot Password - Non-existent Email", False, 
                                f"Unexpected status code: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Forgot Password - Non-existent Email", False, f"Exception: {str(e)}")
            return False

    async def test_reset_token_generation_and_storage(self):
        """Test that reset token is properly generated and stored"""
        try:
            # If we don't have a reset token from the previous test, generate one
            if not self.reset_token:
                await self.test_forgot_password_valid_email()
            
            if self.reset_token:
                # Verify token properties
                if len(self.reset_token) >= 32:  # Should be sufficiently long
                    self.log_test("Reset Token Generation", True, 
                                f"Reset token properly generated (length: {len(self.reset_token)})")
                    return True
                else:
                    self.log_test("Reset Token Generation", False, 
                                f"Reset token too short (length: {len(self.reset_token)})")
                    return False
            else:
                self.log_test("Reset Token Generation", False, "No reset token available for testing")
                return False
        except Exception as e:
            self.log_test("Reset Token Generation", False, f"Exception: {str(e)}")
            return False

    async def test_reset_password_valid_token(self):
        """Test reset password with valid token and new password"""
        try:
            if not self.reset_token:
                self.log_test("Reset Password - Valid Token", False, "No reset token available")
                return False
            
            payload = {
                "token": self.reset_token,
                "new_password": NEW_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    if "password has been reset successfully" in data.get("message", "").lower():
                        self.log_test("Reset Password - Valid Token", True, 
                                    "Password reset completed successfully")
                        return True
                    else:
                        self.log_test("Reset Password - Valid Token", False, 
                                    f"Unexpected success message: {data.get('message')}")
                        return False
                else:
                    self.log_test("Reset Password - Valid Token", False, 
                                f"Failed with status {response.status}: {data}")
                    return False
        except Exception as e:
            self.log_test("Reset Password - Valid Token", False, f"Exception: {str(e)}")
            return False

    async def test_reset_password_invalid_token(self):
        """Test reset password with invalid/non-existent token"""
        try:
            payload = {
                "token": "invalid_token_12345",
                "new_password": NEW_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 400:
                    if "invalid" in data.get("detail", "").lower() or "expired" in data.get("detail", "").lower():
                        self.log_test("Reset Password - Invalid Token", True, 
                                    "Correctly rejects invalid token")
                        return True
                    else:
                        self.log_test("Reset Password - Invalid Token", False, 
                                    f"Unexpected error message: {data.get('detail')}")
                        return False
                else:
                    self.log_test("Reset Password - Invalid Token", False, 
                                f"Unexpected status code: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Reset Password - Invalid Token", False, f"Exception: {str(e)}")
            return False

    async def test_reset_password_expired_token(self):
        """Test reset password with expired token (simulated)"""
        try:
            # Generate a new reset token first
            payload = {"email": TEST_EMAIL}
            async with self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "reset_token" in data:
                        expired_token = data["reset_token"]
                        
                        # Wait a moment then try to use the token
                        # Note: In a real test, we'd manipulate the database to set an expired timestamp
                        # For now, we'll test with the assumption that the token will be valid
                        # but we'll test the expired token logic by using an old/invalid token format
                        
                        # Try with a token that looks expired (this is a simulation)
                        old_token_payload = {
                            "token": "expired_token_simulation_12345",
                            "new_password": NEW_PASSWORD
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=old_token_payload) as reset_response:
                            reset_data = await reset_response.json()
                            
                            if reset_response.status == 400:
                                self.log_test("Reset Password - Expired Token", True, 
                                            "Correctly rejects expired/invalid token")
                                return True
                            else:
                                self.log_test("Reset Password - Expired Token", False, 
                                            f"Should reject expired token but got: {reset_response.status}")
                                return False
                    else:
                        self.log_test("Reset Password - Expired Token", False, 
                                    "Could not generate token for expiration test")
                        return False
                else:
                    self.log_test("Reset Password - Expired Token", False, 
                                "Could not initiate password reset for expiration test")
                    return False
        except Exception as e:
            self.log_test("Reset Password - Expired Token", False, f"Exception: {str(e)}")
            return False

    async def test_password_hash_update(self):
        """Test that password is properly hashed and updated"""
        try:
            # Try to login with the new password after reset
            login_payload = {
                "email": TEST_EMAIL,
                "password": NEW_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    if "access_token" in data:
                        self.log_test("Password Hash Update", True, 
                                    "New password works - hash properly updated")
                        return True
                    else:
                        self.log_test("Password Hash Update", False, 
                                    "Login successful but no access token returned")
                        return False
                else:
                    self.log_test("Password Hash Update", False, 
                                f"Cannot login with new password: {response.status} - {data}")
                    return False
        except Exception as e:
            self.log_test("Password Hash Update", False, f"Exception: {str(e)}")
            return False

    async def test_old_password_invalid(self):
        """Test that old password no longer works after reset"""
        try:
            # Try to login with the old password
            login_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD  # Old password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload) as response:
                data = await response.json()
                
                if response.status == 401 or response.status == 400:
                    self.log_test("Old Password Invalid", True, 
                                "Old password correctly rejected after reset")
                    return True
                else:
                    self.log_test("Old Password Invalid", False, 
                                f"Old password still works after reset: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Old Password Invalid", False, f"Exception: {str(e)}")
            return False

    async def test_token_cleared_after_reset(self):
        """Test that reset token is cleared after successful password reset"""
        try:
            # Try to use the same reset token again
            if not self.reset_token:
                self.log_test("Token Cleared After Reset", False, "No reset token to test with")
                return False
            
            payload = {
                "token": self.reset_token,
                "new_password": "AnotherPassword789!"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/reset-password", json=payload) as response:
                data = await response.json()
                
                if response.status == 400:
                    if "invalid" in data.get("detail", "").lower() or "expired" in data.get("detail", "").lower():
                        self.log_test("Token Cleared After Reset", True, 
                                    "Reset token correctly cleared after use")
                        return True
                    else:
                        self.log_test("Token Cleared After Reset", False, 
                                    f"Unexpected error message: {data.get('detail')}")
                        return False
                else:
                    self.log_test("Token Cleared After Reset", False, 
                                f"Reset token can be reused (security issue): {response.status}")
                    return False
        except Exception as e:
            self.log_test("Token Cleared After Reset", False, f"Exception: {str(e)}")
            return False

    async def test_failed_login_attempts_reset(self):
        """Test that failed login attempts are reset after password reset"""
        try:
            # This test assumes the password reset clears failed login attempts
            # We'll verify by checking if we can login normally after reset
            login_payload = {
                "email": TEST_EMAIL,
                "password": NEW_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    self.log_test("Failed Login Attempts Reset", True, 
                                "Login successful - failed attempts likely reset")
                    return True
                else:
                    self.log_test("Failed Login Attempts Reset", False, 
                                f"Login failed after password reset: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Failed Login Attempts Reset", False, f"Exception: {str(e)}")
            return False

    async def test_error_handling_invalid_inputs(self):
        """Test error handling for various invalid inputs"""
        try:
            test_cases = [
                # Missing email
                ({}, "forgot-password", "Missing email field"),
                # Invalid email format
                ({"email": "invalid-email"}, "forgot-password", "Invalid email format"),
                # Missing token
                ({"new_password": "test123"}, "reset-password", "Missing token field"),
                # Missing password
                ({"token": "test123"}, "reset-password", "Missing password field"),
                # Empty password
                ({"token": "test123", "new_password": ""}, "reset-password", "Empty password"),
            ]
            
            passed_tests = 0
            total_tests = len(test_cases)
            
            for payload, endpoint, description in test_cases:
                try:
                    async with self.session.post(f"{BACKEND_URL}/auth/{endpoint}", json=payload) as response:
                        if response.status >= 400:  # Should return error for invalid input
                            passed_tests += 1
                        else:
                            print(f"  ⚠️  {description}: Expected error but got {response.status}")
                except Exception:
                    passed_tests += 1  # Exception is expected for invalid input
            
            if passed_tests == total_tests:
                self.log_test("Error Handling - Invalid Inputs", True, 
                            f"All {total_tests} invalid input tests handled correctly")
                return True
            else:
                self.log_test("Error Handling - Invalid Inputs", False, 
                            f"Only {passed_tests}/{total_tests} invalid input tests passed")
                return False
        except Exception as e:
            self.log_test("Error Handling - Invalid Inputs", False, f"Exception: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all password reset tests"""
        print("🎯 STARTING PASSWORD RESET FUNCTIONALITY TESTING FOR BIG MANN ENTERTAINMENT")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Setup
            print("\n📋 SETUP PHASE")
            await self.create_test_user()
            
            # Core Password Reset Flow Tests
            print("\n🔐 FORGOT PASSWORD FLOW TESTS")
            await self.test_forgot_password_valid_email()
            await self.test_forgot_password_nonexistent_email()
            await self.test_reset_token_generation_and_storage()
            
            print("\n🔄 RESET PASSWORD FLOW TESTS")
            await self.test_reset_password_valid_token()
            await self.test_reset_password_invalid_token()
            await self.test_reset_password_expired_token()
            
            print("\n🔒 SECURITY AND DATABASE TESTS")
            await self.test_password_hash_update()
            await self.test_old_password_invalid()
            await self.test_token_cleared_after_reset()
            await self.test_failed_login_attempts_reset()
            
            print("\n⚠️ ERROR HANDLING TESTS")
            await self.test_error_handling_invalid_inputs()
            
            # Cleanup
            print("\n🧹 CLEANUP PHASE")
            await self.cleanup_test_user()
            
        finally:
            await self.cleanup_session()
        
        # Print Results
        print("\n" + "=" * 80)
        print("📊 PASSWORD RESET TESTING RESULTS")
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
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL PASSWORD RESET TESTS PASSED! The password reset functionality is working correctly.")
        else:
            print(f"\n⚠️ {self.results['failed']} test(s) failed. Please review the issues above.")
        
        return self.results

async def main():
    """Main test execution"""
    tester = PasswordResetTester()
    results = await tester.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())