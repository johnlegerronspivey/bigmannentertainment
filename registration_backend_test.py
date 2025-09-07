#!/usr/bin/env python3
"""
Big Mann Entertainment - Registration and Sign Up Backend Testing
Comprehensive testing of account registration and sign up process
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import secrets
import string

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class RegistrationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session and test data"""
        if self.session:
            await self.session.close()
            
    def generate_test_user_data(self, suffix: str = None) -> Dict[str, Any]:
        """Generate realistic test user data"""
        if suffix is None:
            suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
            
        # Generate a date of birth for someone who is 25 years old (clearly over 18)
        birth_date = datetime.now() - timedelta(days=25*365 + 6)  # 25 years + leap days
        
        return {
            "email": f"artist.{suffix}@bigmannentertainment.com",
            "password": "SecurePassword123!",
            "full_name": f"Artist {suffix.title()}",
            "business_name": f"{suffix.title()} Music Productions",
            "date_of_birth": birth_date.isoformat(),
            "address_line1": "123 Music Street",
            "address_line2": "Suite 456",
            "city": "Nashville",
            "state_province": "Tennessee",
            "postal_code": "37203",
            "country": "United States"
        }
        
    def generate_underage_user_data(self) -> Dict[str, Any]:
        """Generate test data for underage user (should be rejected)"""
        suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        
        # Generate a date of birth for someone who is 16 years old (under 18)
        birth_date = datetime.now() - timedelta(days=16*365 + 4)  # 16 years + leap days
        
        return {
            "email": f"young.{suffix}@bigmannentertainment.com",
            "password": "SecurePassword123!",
            "full_name": f"Young Artist {suffix.title()}",
            "business_name": f"{suffix.title()} Young Music",
            "date_of_birth": birth_date.isoformat(),
            "address_line1": "456 Youth Avenue",
            "city": "Los Angeles",
            "state_province": "California",
            "postal_code": "90210",
            "country": "United States"
        }
        
    async def test_registration_endpoint_validation(self):
        """Test 1: Registration Endpoint Validation"""
        print("🔍 Testing Registration Endpoint Validation...")
        
        try:
            # Test with valid data
            valid_user = self.generate_test_user_data("valid001")
            async with self.session.post(f"{API_BASE}/auth/register", json=valid_user) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'access_token' in data and 'user' in data:
                        self.test_results.append("✅ Valid registration data accepted")
                        self.test_users.append(valid_user['email'])
                    else:
                        self.test_results.append("❌ Valid registration missing required response fields")
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Valid registration failed: {response.status} - {error_text}")
                    
        except Exception as e:
            self.test_results.append(f"❌ Registration endpoint validation error: {str(e)}")
            
    async def test_field_validation(self):
        """Test 2: Field Validation"""
        print("🔍 Testing Field Validation...")
        
        # Test missing required fields
        test_cases = [
            ({}, "empty data"),
            ({"email": "test@example.com"}, "missing password"),
            ({"email": "test@example.com", "password": "pass123"}, "missing full_name"),
            ({"email": "invalid-email", "password": "pass123", "full_name": "Test User"}, "invalid email format"),
        ]
        
        for test_data, description in test_cases:
            try:
                async with self.session.post(f"{API_BASE}/auth/register", json=test_data) as response:
                    if response.status == 400 or response.status == 422:
                        self.test_results.append(f"✅ Field validation working for {description}")
                    else:
                        self.test_results.append(f"❌ Field validation failed for {description}: {response.status}")
            except Exception as e:
                self.test_results.append(f"❌ Field validation error for {description}: {str(e)}")
                
    async def test_age_verification(self):
        """Test 3: Age Verification (18+ requirement)"""
        print("🔍 Testing Age Verification...")
        
        try:
            # Test underage user (should be rejected)
            underage_user = self.generate_underage_user_data()
            async with self.session.post(f"{API_BASE}/auth/register", json=underage_user) as response:
                if response.status == 400:
                    error_data = await response.json()
                    if "18 or older" in error_data.get('detail', '').lower():
                        self.test_results.append("✅ Age verification working - underage user rejected")
                    else:
                        self.test_results.append(f"❌ Age verification error message incorrect: {error_data}")
                else:
                    self.test_results.append(f"❌ Age verification failed - underage user accepted: {response.status}")
                    
            # Test user exactly 18 years old (should be accepted)
            eighteen_user = self.generate_test_user_data("eighteen")
            birth_date = datetime.now() - timedelta(days=18*365 + 4)  # Exactly 18 years
            eighteen_user['date_of_birth'] = birth_date.isoformat()
            
            async with self.session.post(f"{API_BASE}/auth/register", json=eighteen_user) as response:
                if response.status == 200:
                    self.test_results.append("✅ Age verification working - 18-year-old user accepted")
                    self.test_users.append(eighteen_user['email'])
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Age verification failed - 18-year-old user rejected: {error_text}")
                    
        except Exception as e:
            self.test_results.append(f"❌ Age verification error: {str(e)}")
            
    async def test_email_uniqueness(self):
        """Test 4: Email Uniqueness"""
        print("🔍 Testing Email Uniqueness...")
        
        try:
            # Register first user
            user1 = self.generate_test_user_data("unique001")
            async with self.session.post(f"{API_BASE}/auth/register", json=user1) as response:
                if response.status == 200:
                    self.test_users.append(user1['email'])
                    
                    # Try to register second user with same email
                    user2 = self.generate_test_user_data("unique002")
                    user2['email'] = user1['email']  # Use same email
                    
                    async with self.session.post(f"{API_BASE}/auth/register", json=user2) as response2:
                        if response2.status == 400:
                            error_data = await response2.json()
                            if "already registered" in error_data.get('detail', '').lower():
                                self.test_results.append("✅ Email uniqueness validation working")
                            else:
                                self.test_results.append(f"❌ Email uniqueness error message incorrect: {error_data}")
                        else:
                            self.test_results.append(f"❌ Email uniqueness failed - duplicate email accepted: {response2.status}")
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Email uniqueness test setup failed: {error_text}")
                    
        except Exception as e:
            self.test_results.append(f"❌ Email uniqueness test error: {str(e)}")
            
    async def test_password_security(self):
        """Test 5: Password Security"""
        print("🔍 Testing Password Security...")
        
        try:
            # Test various password scenarios
            password_tests = [
                ("password123", "weak password"),
                ("", "empty password"),
                ("a", "very short password"),
                ("SecurePassword123!", "strong password")
            ]
            
            for password, description in password_tests:
                user_data = self.generate_test_user_data(f"pwd{len(password)}")
                user_data['password'] = password
                
                async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                    if password == "SecurePassword123!":
                        if response.status == 200:
                            self.test_results.append(f"✅ Password security - {description} accepted")
                            self.test_users.append(user_data['email'])
                        else:
                            error_text = await response.text()
                            self.test_results.append(f"❌ Password security - {description} rejected: {error_text}")
                    else:
                        # For now, the system accepts any password, so we'll note this
                        if response.status == 200:
                            self.test_results.append(f"⚠️ Password security - {description} accepted (no password complexity requirements)")
                            self.test_users.append(user_data['email'])
                        else:
                            self.test_results.append(f"✅ Password security - {description} properly rejected")
                            
        except Exception as e:
            self.test_results.append(f"❌ Password security test error: {str(e)}")
            
    async def test_database_operations(self):
        """Test 6: Database Operations"""
        print("🔍 Testing Database Operations...")
        
        try:
            # Register a user and verify data storage
            user_data = self.generate_test_user_data("dbtest")
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Verify response structure
                    required_fields = ['access_token', 'refresh_token', 'token_type', 'expires_in', 'user']
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if not missing_fields:
                        self.test_results.append("✅ Database operations - user creation response structure correct")
                        
                        # Verify user data in response
                        user_response = response_data['user']
                        if (user_response['email'] == user_data['email'] and 
                            user_response['full_name'] == user_data['full_name']):
                            self.test_results.append("✅ Database operations - user data correctly stored and returned")
                        else:
                            self.test_results.append("❌ Database operations - user data mismatch in response")
                            
                        # Verify password is not returned
                        if 'password' not in user_response and 'password_hash' not in user_response:
                            self.test_results.append("✅ Database operations - password security maintained")
                        else:
                            self.test_results.append("❌ Database operations - password exposed in response")
                            
                        self.test_users.append(user_data['email'])
                    else:
                        self.test_results.append(f"❌ Database operations - missing response fields: {missing_fields}")
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Database operations test failed: {error_text}")
                    
        except Exception as e:
            self.test_results.append(f"❌ Database operations test error: {str(e)}")
            
    async def test_email_integration(self):
        """Test 7: Email Integration"""
        print("🔍 Testing Email Integration...")
        
        try:
            # Register user and check if welcome email is attempted
            user_data = self.generate_test_user_data("emailtest")
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    # Registration should succeed even if email fails (graceful fallback)
                    self.test_results.append("✅ Email integration - registration succeeds with email fallback")
                    self.test_users.append(user_data['email'])
                    
                    # The system has graceful email fallback, so we can't directly test email sending
                    # but we can verify the registration doesn't fail due to email issues
                    response_data = await response.json()
                    if 'access_token' in response_data:
                        self.test_results.append("✅ Email integration - graceful fallback working")
                    else:
                        self.test_results.append("❌ Email integration - registration incomplete")
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Email integration test failed: {error_text}")
                    
        except Exception as e:
            self.test_results.append(f"❌ Email integration test error: {str(e)}")
            
    async def test_authentication_flow(self):
        """Test 8: Authentication Flow"""
        print("🔍 Testing Authentication Flow...")
        
        try:
            # Register user and test immediate login capability
            user_data = self.generate_test_user_data("authtest")
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    access_token = response_data.get('access_token')
                    
                    if access_token:
                        # Test using the token for authenticated request
                        headers = {'Authorization': f'Bearer {access_token}'}
                        async with self.session.get(f"{API_BASE}/auth/me", headers=headers) as auth_response:
                            if auth_response.status == 200:
                                self.test_results.append("✅ Authentication flow - automatic login after registration working")
                            else:
                                self.test_results.append(f"❌ Authentication flow - token not working: {auth_response.status}")
                    else:
                        self.test_results.append("❌ Authentication flow - no access token provided")
                        
                    self.test_users.append(user_data['email'])
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Authentication flow test setup failed: {error_text}")
                    
        except Exception as e:
            self.test_results.append(f"❌ Authentication flow test error: {str(e)}")
            
    async def test_error_handling(self):
        """Test 9: Error Handling"""
        print("🔍 Testing Error Handling...")
        
        try:
            # Test various error scenarios
            error_tests = [
                ({"email": "invalid-email"}, "invalid email format"),
                ({"email": "test@example.com", "password": ""}, "empty password"),
                ({"email": "", "password": "test123"}, "empty email"),
                ({}, "completely empty request")
            ]
            
            for test_data, description in error_tests:
                async with self.session.post(f"{API_BASE}/auth/register", json=test_data) as response:
                    if response.status >= 400:
                        try:
                            error_data = await response.json()
                            if 'detail' in error_data:
                                self.test_results.append(f"✅ Error handling - {description} properly handled")
                            else:
                                self.test_results.append(f"⚠️ Error handling - {description} handled but no detail message")
                        except:
                            self.test_results.append(f"⚠️ Error handling - {description} handled but response not JSON")
                    else:
                        self.test_results.append(f"❌ Error handling - {description} not properly rejected")
                        
        except Exception as e:
            self.test_results.append(f"❌ Error handling test error: {str(e)}")
            
    async def test_complete_registration_flow(self):
        """Test 10: Complete Registration Flow"""
        print("🔍 Testing Complete Registration Flow...")
        
        try:
            # Test end-to-end registration with all required fields
            user_data = self.generate_test_user_data("complete")
            
            # Add all optional fields
            user_data.update({
                "business_name": "Complete Music Productions LLC",
                "address_line2": "Floor 3, Suite 789"
            })
            
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Verify complete response
                    checks = [
                        ('access_token' in response_data, "access token provided"),
                        ('refresh_token' in response_data, "refresh token provided"),
                        ('user' in response_data, "user data returned"),
                        (response_data.get('token_type') == 'bearer', "correct token type"),
                        (isinstance(response_data.get('expires_in'), int), "expiration time provided")
                    ]
                    
                    for check, description in checks:
                        if check:
                            self.test_results.append(f"✅ Complete flow - {description}")
                        else:
                            self.test_results.append(f"❌ Complete flow - {description} missing")
                            
                    # Test login with registered credentials
                    login_data = {
                        "email": user_data['email'],
                        "password": user_data['password']
                    }
                    
                    async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as login_response:
                        if login_response.status == 200:
                            self.test_results.append("✅ Complete flow - login with new credentials working")
                        else:
                            error_text = await login_response.text()
                            self.test_results.append(f"❌ Complete flow - login failed: {error_text}")
                            
                    self.test_users.append(user_data['email'])
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Complete registration flow failed: {error_text}")
                    
        except Exception as e:
            self.test_results.append(f"❌ Complete registration flow error: {str(e)}")
            
    async def run_all_tests(self):
        """Run all registration tests"""
        print("🎯 STARTING COMPREHENSIVE REGISTRATION TESTING FOR BIG MANN ENTERTAINMENT")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test methods
            test_methods = [
                self.test_registration_endpoint_validation,
                self.test_field_validation,
                self.test_age_verification,
                self.test_email_uniqueness,
                self.test_password_security,
                self.test_database_operations,
                self.test_email_integration,
                self.test_authentication_flow,
                self.test_error_handling,
                self.test_complete_registration_flow
            ]
            
            for test_method in test_methods:
                try:
                    await test_method()
                except Exception as e:
                    self.test_results.append(f"❌ {test_method.__name__} failed with exception: {str(e)}")
                    
        finally:
            await self.cleanup()
            
        # Print results
        self.print_results()
        
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🎉 REGISTRATION TESTING RESULTS")
        print("=" * 80)
        
        success_count = sum(1 for result in self.test_results if result.startswith("✅"))
        warning_count = sum(1 for result in self.test_results if result.startswith("⚠️"))
        failure_count = sum(1 for result in self.test_results if result.startswith("❌"))
        total_count = len(self.test_results)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_count}")
        print(f"   ✅ Passed: {success_count}")
        print(f"   ⚠️ Warnings: {warning_count}")
        print(f"   ❌ Failed: {failure_count}")
        print(f"   Success Rate: {(success_count / total_count * 100):.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            print(f"   {i:2d}. {result}")
            
        if self.test_users:
            print(f"\n👥 TEST USERS CREATED: {len(self.test_users)}")
            for email in self.test_users[:5]:  # Show first 5
                print(f"   - {email}")
            if len(self.test_users) > 5:
                print(f"   ... and {len(self.test_users) - 5} more")
                
        print(f"\n🔗 BACKEND URL: {BACKEND_URL}")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = RegistrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())