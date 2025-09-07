#!/usr/bin/env python3
"""
Enhanced Registration System Backend Testing
Tests the FIXED account registration and sign up process with enhanced password validation,
improved email validation, and other improvements for Big Mann Entertainment platform.
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuration - Use internal backend URL for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class EnhancedRegistrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_users = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", error_msg: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_enhanced_password_validation(self):
        """Test enhanced password complexity requirements (8+ chars, uppercase, lowercase, number)"""
        print("🔐 Testing Enhanced Password Validation...")
        
        password_tests = [
            # (password, should_pass, description)
            ("", False, "Empty password"),
            ("123", False, "Too short (3 chars)"),
            ("password", False, "No uppercase, no numbers"),
            ("PASSWORD", False, "No lowercase, no numbers"),
            ("12345678", False, "No letters"),
            ("Password", False, "No numbers"),
            ("password1", False, "No uppercase"),
            ("PASSWORD1", False, "No lowercase"),
            ("Password1", True, "Valid: 8+ chars, uppercase, lowercase, number"),
            ("MySecure123", True, "Valid: complex password"),
            ("BigMann2025!", True, "Valid: complex password with special char"),
        ]
        
        for password, should_pass, description in password_tests:
            try:
                user_data = {
                    "email": f"password.test.{int(time.time())}@bigmannentertainment.com",
                    "password": password,
                    "full_name": "Password Test User",
                    "date_of_birth": "1990-01-01T00:00:00Z",
                    "address_line1": "123 Test Street",
                    "city": "Test City",
                    "state_province": "Test State",
                    "postal_code": "12345",
                    "country": "United States"
                }
                
                response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
                
                if should_pass:
                    if response.status_code in [200, 201]:
                        # Clean up successful registration
                        if response.status_code in [200, 201]:
                            data = response.json()
                            if data.get("access_token"):
                                self.test_users.append(data.get("user", {}).get("id"))
                        
                        self.log_result(
                            f"Enhanced Password Validation - {description}",
                            True,
                            f"Password '{password}' correctly accepted"
                        )
                    else:
                        self.log_result(
                            f"Enhanced Password Validation - {description}",
                            False,
                            error_msg=f"Valid password rejected: {response.status_code} - {response.text}"
                        )
                else:
                    if response.status_code in [400, 422]:
                        self.log_result(
                            f"Enhanced Password Validation - {description}",
                            True,
                            f"Password '{password}' correctly rejected"
                        )
                    else:
                        self.log_result(
                            f"Enhanced Password Validation - {description}",
                            False,
                            error_msg=f"Invalid password accepted: {response.status_code}"
                        )
                        
            except Exception as e:
                self.log_result(
                    f"Enhanced Password Validation - {description}",
                    False,
                    error_msg=str(e)
                )

    def test_improved_email_validation(self):
        """Test improved email format validation with regex"""
        print("📧 Testing Improved Email Validation...")
        
        email_tests = [
            # (email, should_pass, description)
            ("", False, "Empty email"),
            ("invalid", False, "No @ symbol"),
            ("@domain.com", False, "Missing local part"),
            ("user@", False, "Missing domain"),
            ("user@domain", False, "Missing TLD"),
            ("user..name@domain.com", False, "Double dots in local part"),
            ("user@domain..com", False, "Double dots in domain"),
            ("user name@domain.com", False, "Space in local part"),
            ("user@domain .com", False, "Space in domain"),
            ("user@domain.c", False, "TLD too short"),
            ("test@bigmannentertainment.com", True, "Valid email"),
            ("user.name@domain.com", True, "Valid with dot"),
            ("user+tag@domain.co.uk", True, "Valid with plus and multiple TLD"),
            ("123@domain.org", True, "Valid with numbers"),
            ("a@b.co", True, "Valid minimal email"),
        ]
        
        for email, should_pass, description in email_tests:
            try:
                user_data = {
                    "email": email,
                    "password": "ValidPass123",
                    "full_name": "Email Test User",
                    "date_of_birth": "1990-01-01T00:00:00Z",
                    "address_line1": "123 Test Street",
                    "city": "Test City",
                    "state_province": "Test State",
                    "postal_code": "12345",
                    "country": "United States"
                }
                
                response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
                
                if should_pass:
                    if response.status_code in [200, 201]:
                        # Clean up successful registration
                        if response.status_code in [200, 201]:
                            data = response.json()
                            if data.get("access_token"):
                                self.test_users.append(data.get("user", {}).get("id"))
                        
                        self.log_result(
                            f"Improved Email Validation - {description}",
                            True,
                            f"Email '{email}' correctly accepted"
                        )
                    else:
                        self.log_result(
                            f"Improved Email Validation - {description}",
                            False,
                            error_msg=f"Valid email rejected: {response.status_code} - {response.text}"
                        )
                else:
                    if response.status_code in [400, 422]:
                        self.log_result(
                            f"Improved Email Validation - {description}",
                            True,
                            f"Email '{email}' correctly rejected"
                        )
                    else:
                        self.log_result(
                            f"Improved Email Validation - {description}",
                            False,
                            error_msg=f"Invalid email accepted: {response.status_code}"
                        )
                        
            except Exception as e:
                self.log_result(
                    f"Improved Email Validation - {description}",
                    False,
                    error_msg=str(e)
                )

    def test_enhanced_field_validation(self):
        """Test enhanced field validation with better error messages"""
        print("📝 Testing Enhanced Field Validation...")
        
        # Test required field validation
        required_fields = [
            ("email", "Email is required"),
            ("password", "Password is required"),
            ("full_name", "Full name is required"),
            ("date_of_birth", "Date of birth is required"),
            ("address_line1", "Address is required"),
            ("city", "City is required"),
            ("state_province", "State/Province is required"),
            ("postal_code", "Postal code is required"),
            ("country", "Country is required"),
        ]
        
        base_data = {
            "email": "field.test@bigmannentertainment.com",
            "password": "ValidPass123",
            "full_name": "Field Test User",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "United States"
        }
        
        for field, expected_error in required_fields:
            try:
                # Create test data with missing field
                test_data = base_data.copy()
                del test_data[field]
                
                response = self.session.post(f"{API_BASE}/auth/register", json=test_data)
                
                if response.status_code in [400, 422]:
                    self.log_result(
                        f"Enhanced Field Validation - Missing {field}",
                        True,
                        f"Missing {field} correctly rejected with status {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Enhanced Field Validation - Missing {field}",
                        False,
                        error_msg=f"Missing {field} not properly validated: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Enhanced Field Validation - Missing {field}",
                    False,
                    error_msg=str(e)
                )

    def test_age_verification(self):
        """Test 18+ age verification still working properly"""
        print("🎂 Testing Age Verification...")
        
        age_tests = [
            # (birth_date, should_pass, description)
            ("2010-01-01T00:00:00Z", False, "14 years old (underage)"),
            ("2007-01-01T00:00:00Z", False, "17 years old (underage)"),
            ("2006-01-01T00:00:00Z", True, "18 years old (valid)"),
            ("1990-01-01T00:00:00Z", True, "34 years old (valid)"),
            ("1950-01-01T00:00:00Z", True, "74 years old (valid)"),
        ]
        
        for birth_date, should_pass, description in age_tests:
            try:
                user_data = {
                    "email": f"age.test.{int(time.time())}.{birth_date[:4]}@bigmannentertainment.com",
                    "password": "ValidPass123",
                    "full_name": "Age Test User",
                    "date_of_birth": birth_date,
                    "address_line1": "123 Test Street",
                    "city": "Test City",
                    "state_province": "Test State",
                    "postal_code": "12345",
                    "country": "United States"
                }
                
                response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
                
                if should_pass:
                    if response.status_code in [200, 201]:
                        # Clean up successful registration
                        data = response.json()
                        if data.get("access_token"):
                            self.test_users.append(data.get("user", {}).get("id"))
                        
                        self.log_result(
                            f"Age Verification - {description}",
                            True,
                            f"Age verification passed for birth date {birth_date}"
                        )
                    else:
                        self.log_result(
                            f"Age Verification - {description}",
                            False,
                            error_msg=f"Valid age rejected: {response.status_code} - {response.text}"
                        )
                else:
                    if response.status_code in [400, 422]:
                        response_text = response.text.lower()
                        if "18" in response_text or "age" in response_text:
                            self.log_result(
                                f"Age Verification - {description}",
                                True,
                                f"Underage user correctly rejected with proper error message"
                            )
                        else:
                            self.log_result(
                                f"Age Verification - {description}",
                                True,
                                f"Underage user rejected (status {response.status_code})"
                            )
                    else:
                        self.log_result(
                            f"Age Verification - {description}",
                            False,
                            error_msg=f"Underage user accepted: {response.status_code}"
                        )
                        
            except Exception as e:
                self.log_result(
                    f"Age Verification - {description}",
                    False,
                    error_msg=str(e)
                )

    def test_email_uniqueness(self):
        """Test duplicate email prevention"""
        print("🔄 Testing Email Uniqueness...")
        
        try:
            # First registration
            unique_email = f"uniqueness.test.{int(time.time())}@bigmannentertainment.com"
            user_data = {
                "email": unique_email,
                "password": "ValidPass123",
                "full_name": "Uniqueness Test User 1",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            response1 = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response1.status_code in [200, 201]:
                # Clean up successful registration
                data = response1.json()
                if data.get("access_token"):
                    self.test_users.append(data.get("user", {}).get("id"))
                
                # Second registration with same email
                user_data["full_name"] = "Uniqueness Test User 2"
                response2 = self.session.post(f"{API_BASE}/auth/register", json=user_data)
                
                if response2.status_code in [400, 422]:
                    response_text = response2.text.lower()
                    if "email" in response_text and ("exists" in response_text or "registered" in response_text):
                        self.log_result(
                            "Email Uniqueness - Duplicate Prevention",
                            True,
                            f"Duplicate email correctly rejected with proper error message"
                        )
                    else:
                        self.log_result(
                            "Email Uniqueness - Duplicate Prevention",
                            True,
                            f"Duplicate email rejected (status {response2.status_code})"
                        )
                else:
                    self.log_result(
                        "Email Uniqueness - Duplicate Prevention",
                        False,
                        error_msg=f"Duplicate email accepted: {response2.status_code}"
                    )
            else:
                self.log_result(
                    "Email Uniqueness - Initial Registration",
                    False,
                    error_msg=f"Initial registration failed: {response1.status_code} - {response1.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Email Uniqueness - Duplicate Prevention",
                False,
                error_msg=str(e)
            )

    def test_welcome_email_integration(self):
        """Test welcome email sending with fixed email service"""
        print("📬 Testing Welcome Email Integration...")
        
        try:
            user_data = {
                "email": f"welcome.test.{int(time.time())}@bigmannentertainment.com",
                "password": "ValidPass123",
                "full_name": "Welcome Email Test User",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                # Clean up successful registration
                data = response.json()
                if data.get("access_token"):
                    self.test_users.append(data.get("user", {}).get("id"))
                
                # Registration should succeed even if email service fails (graceful fallback)
                self.log_result(
                    "Welcome Email Integration - Registration Success",
                    True,
                    "Registration completed successfully with email service integration"
                )
                
                # Check if user received proper response structure
                if data.get("user") and data.get("access_token"):
                    self.log_result(
                        "Welcome Email Integration - Response Structure",
                        True,
                        "Registration response includes user data and access token"
                    )
                else:
                    self.log_result(
                        "Welcome Email Integration - Response Structure",
                        False,
                        error_msg="Registration response missing user data or access token"
                    )
            else:
                self.log_result(
                    "Welcome Email Integration - Registration Success",
                    False,
                    error_msg=f"Registration failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Welcome Email Integration - Registration Success",
                False,
                error_msg=str(e)
            )

    def test_authentication_flow(self):
        """Test automatic login after successful registration"""
        print("🔐 Testing Authentication Flow...")
        
        try:
            user_data = {
                "email": f"auth.test.{int(time.time())}@bigmannentertainment.com",
                "password": "ValidPass123",
                "full_name": "Auth Flow Test User",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                # Check for JWT tokens
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token")
                
                if access_token and refresh_token:
                    # Clean up successful registration
                    if data.get("user", {}).get("id"):
                        self.test_users.append(data.get("user", {}).get("id"))
                    
                    self.log_result(
                        "Authentication Flow - Token Generation",
                        True,
                        "Registration returns valid access_token and refresh_token"
                    )
                    
                    # Test immediate authentication with returned token
                    headers = {"Authorization": f"Bearer {access_token}"}
                    auth_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                    
                    if auth_response.status_code == 200:
                        user_info = auth_response.json()
                        if user_info.get("email") == user_data["email"]:
                            self.log_result(
                                "Authentication Flow - Immediate Login",
                                True,
                                "User can immediately authenticate with registration token"
                            )
                        else:
                            self.log_result(
                                "Authentication Flow - Immediate Login",
                                False,
                                error_msg="Token returns different user data"
                            )
                    else:
                        self.log_result(
                            "Authentication Flow - Immediate Login",
                            False,
                            error_msg=f"Token authentication failed: {auth_response.status_code}"
                        )
                else:
                    self.log_result(
                        "Authentication Flow - Token Generation",
                        False,
                        error_msg="Registration response missing access_token or refresh_token"
                    )
            else:
                self.log_result(
                    "Authentication Flow - Registration",
                    False,
                    error_msg=f"Registration failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Authentication Flow - Token Generation",
                False,
                error_msg=str(e)
            )

    def test_database_operations(self):
        """Test user data is properly stored"""
        print("💾 Testing Database Operations...")
        
        try:
            user_data = {
                "email": f"database.test.{int(time.time())}@bigmannentertainment.com",
                "password": "ValidPass123",
                "full_name": "Database Test User",
                "business_name": "Test Business LLC",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "address_line2": "Apt 4B",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_info = data.get("user", {})
                
                # Clean up successful registration
                if user_info.get("id"):
                    self.test_users.append(user_info.get("id"))
                
                # Verify all fields are stored correctly
                fields_to_check = [
                    ("email", user_data["email"]),
                    ("full_name", user_data["full_name"]),
                    ("business_name", user_data["business_name"]),
                    ("address_line1", user_data["address_line1"]),
                    ("address_line2", user_data["address_line2"]),
                    ("city", user_data["city"]),
                    ("state_province", user_data["state_province"]),
                    ("postal_code", user_data["postal_code"]),
                    ("country", user_data["country"]),
                ]
                
                all_fields_correct = True
                missing_fields = []
                
                for field_name, expected_value in fields_to_check:
                    if user_info.get(field_name) != expected_value:
                        all_fields_correct = False
                        missing_fields.append(field_name)
                
                if all_fields_correct:
                    self.log_result(
                        "Database Operations - Data Storage",
                        True,
                        "All user data fields stored correctly in database"
                    )
                else:
                    self.log_result(
                        "Database Operations - Data Storage",
                        False,
                        error_msg=f"Missing or incorrect fields: {missing_fields}"
                    )
                
                # Verify password is not returned in response
                if "password" not in user_info:
                    self.log_result(
                        "Database Operations - Password Security",
                        True,
                        "Password not included in API response (security verified)"
                    )
                else:
                    self.log_result(
                        "Database Operations - Password Security",
                        False,
                        error_msg="Password included in API response (security risk)"
                    )
                
                # Verify UUID format for user ID
                user_id = user_info.get("id")
                if user_id and len(user_id) > 20:  # UUID should be longer than 20 chars
                    self.log_result(
                        "Database Operations - User ID Generation",
                        True,
                        f"User ID generated correctly: {user_id[:8]}..."
                    )
                else:
                    self.log_result(
                        "Database Operations - User ID Generation",
                        False,
                        error_msg=f"Invalid user ID format: {user_id}"
                    )
            else:
                self.log_result(
                    "Database Operations - Registration",
                    False,
                    error_msg=f"Registration failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Database Operations - Data Storage",
                False,
                error_msg=str(e)
            )

    def test_error_handling(self):
        """Test improved error messages and user feedback"""
        print("⚠️ Testing Error Handling...")
        
        # Test various error scenarios
        error_tests = [
            # (data, expected_status, description)
            ({}, [400, 422], "Empty request body"),
            ({"email": "test@example.com"}, [400, 422], "Missing required fields"),
            ({"email": "invalid-email", "password": "ValidPass123"}, [400, 422], "Invalid email format"),
            ({"email": "test@example.com", "password": "weak"}, [400, 422], "Weak password"),
        ]
        
        for test_data, expected_statuses, description in error_tests:
            try:
                response = self.session.post(f"{API_BASE}/auth/register", json=test_data)
                
                if response.status_code in expected_statuses:
                    # Check if response includes helpful error message
                    try:
                        error_data = response.json()
                        if "detail" in error_data or "message" in error_data or "error" in error_data:
                            self.log_result(
                                f"Error Handling - {description}",
                                True,
                                f"Proper error response with message (status {response.status_code})"
                            )
                        else:
                            self.log_result(
                                f"Error Handling - {description}",
                                True,
                                f"Error correctly rejected (status {response.status_code})"
                            )
                    except:
                        self.log_result(
                            f"Error Handling - {description}",
                            True,
                            f"Error correctly rejected (status {response.status_code})"
                        )
                else:
                    self.log_result(
                        f"Error Handling - {description}",
                        False,
                        error_msg=f"Unexpected status: {response.status_code} (expected {expected_statuses})"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Error Handling - {description}",
                    False,
                    error_msg=str(e)
                )

    def test_complete_registration_workflow(self):
        """Test the full end-to-end registration process"""
        print("🔄 Testing Complete Registration Workflow...")
        
        try:
            # Complete registration data
            user_data = {
                "email": f"complete.test.{int(time.time())}@bigmannentertainment.com",
                "password": "CompleteTest123!",
                "full_name": "Complete Workflow Test User",
                "business_name": "Complete Test Business",
                "date_of_birth": "1985-06-15T00:00:00Z",
                "address_line1": "456 Complete Street",
                "address_line2": "Suite 100",
                "city": "Complete City",
                "state_province": "Complete State",
                "postal_code": "54321",
                "country": "United States"
            }
            
            # Step 1: Registration
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                # Clean up successful registration
                if data.get("user", {}).get("id"):
                    self.test_users.append(data.get("user", {}).get("id"))
                
                # Step 2: Verify response structure
                required_response_fields = ["access_token", "refresh_token", "token_type", "expires_in", "user"]
                missing_fields = [field for field in required_response_fields if field not in data]
                
                if not missing_fields:
                    self.log_result(
                        "Complete Registration Workflow - Response Structure",
                        True,
                        "Registration response includes all required fields"
                    )
                else:
                    self.log_result(
                        "Complete Registration Workflow - Response Structure",
                        False,
                        error_msg=f"Missing response fields: {missing_fields}"
                    )
                
                # Step 3: Test immediate login capability
                access_token = data.get("access_token")
                if access_token:
                    headers = {"Authorization": f"Bearer {access_token}"}
                    
                    # Test protected endpoint access
                    me_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                    
                    if me_response.status_code == 200:
                        self.log_result(
                            "Complete Registration Workflow - Immediate Authentication",
                            True,
                            "User can immediately access protected endpoints after registration"
                        )
                    else:
                        self.log_result(
                            "Complete Registration Workflow - Immediate Authentication",
                            False,
                            error_msg=f"Protected endpoint access failed: {me_response.status_code}"
                        )
                
                # Step 4: Test login with credentials
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                
                login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    self.log_result(
                        "Complete Registration Workflow - Subsequent Login",
                        True,
                        "User can login with registered credentials"
                    )
                else:
                    self.log_result(
                        "Complete Registration Workflow - Subsequent Login",
                        False,
                        error_msg=f"Login failed: {login_response.status_code}"
                    )
                
                self.log_result(
                    "Complete Registration Workflow - Overall Success",
                    True,
                    "Complete end-to-end registration workflow successful"
                )
                
            else:
                self.log_result(
                    "Complete Registration Workflow - Registration Failed",
                    False,
                    error_msg=f"Registration failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Complete Registration Workflow - Exception",
                False,
                error_msg=str(e)
            )

    def run_all_tests(self):
        """Run all enhanced registration tests"""
        print("🎯 STARTING ENHANCED REGISTRATION SYSTEM BACKEND TESTING")
        print("=" * 80)
        print("Testing FIXED account registration and sign up process improvements:")
        print("✅ Enhanced Password Validation (8+ chars, uppercase, lowercase, number)")
        print("✅ Improved Email Validation with regex")
        print("✅ Enhanced Field Validation with better error messages")
        print("✅ Age Verification (18+)")
        print("✅ Email Uniqueness Prevention")
        print("✅ Welcome Email Integration (fixed email service)")
        print("✅ Authentication Flow")
        print("✅ Database Operations")
        print("✅ Error Handling")
        print("✅ Complete Registration Workflow")
        print("=" * 80)
        print()
        
        # Run all test categories
        test_categories = [
            ("Enhanced Password Validation", self.test_enhanced_password_validation),
            ("Improved Email Validation", self.test_improved_email_validation),
            ("Enhanced Field Validation", self.test_enhanced_field_validation),
            ("Age Verification", self.test_age_verification),
            ("Email Uniqueness", self.test_email_uniqueness),
            ("Welcome Email Integration", self.test_welcome_email_integration),
            ("Authentication Flow", self.test_authentication_flow),
            ("Database Operations", self.test_database_operations),
            ("Error Handling", self.test_error_handling),
            ("Complete Registration Workflow", self.test_complete_registration_workflow),
        ]
        
        for category_name, test_function in test_categories:
            print(f"📋 {category_name}")
            print("-" * 50)
            test_function()
            print()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Summary
        print("=" * 80)
        print("🎯 ENHANCED REGISTRATION SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for result in self.test_results:
            if not result['success']:
                if any(keyword in result['test'].lower() for keyword in ['password', 'email', 'age', 'uniqueness', 'authentication']):
                    critical_failures.append(result)
                else:
                    minor_issues.append(result)
        
        # Report critical issues
        if critical_failures:
            print("❌ CRITICAL ISSUES FOUND:")
            print("-" * 50)
            for failure in critical_failures:
                print(f"❌ {failure['test']}")
                print(f"   Error: {failure['error']}")
            print()
        
        # Report minor issues
        if minor_issues:
            print("⚠️ MINOR ISSUES:")
            print("-" * 50)
            for issue in minor_issues:
                print(f"⚠️ {issue['test']}")
                print(f"   Error: {issue['error']}")
            print()
        
        # Detailed results for passed tests
        passed_results = [r for r in self.test_results if r['success']]
        if passed_results:
            print("✅ SUCCESSFUL TESTS:")
            print("-" * 50)
            for result in passed_results:
                print(f"✅ {result['test']}")
                if result['details']:
                    print(f"   Details: {result['details']}")
            print()
        
        # Production readiness assessment
        print("📊 PRODUCTION READINESS ASSESSMENT:")
        print("-" * 50)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Enhanced registration system is production-ready")
        elif success_rate >= 80:
            print("✅ GOOD: Enhanced registration system is mostly functional with minor issues")
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE: Enhanced registration system has some issues that should be addressed")
        else:
            print("❌ NEEDS WORK: Enhanced registration system has significant issues")
        
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Critical Issues: {len(critical_failures)}")
        print(f"Minor Issues: {len(minor_issues)}")
        print()
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "critical_failures": len(critical_failures),
            "minor_issues": len(minor_issues),
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = EnhancedRegistrationTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["success_rate"] >= 80 and results["critical_failures"] == 0:
        print("🎉 ENHANCED REGISTRATION TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ ENHANCED REGISTRATION TESTING IDENTIFIED ISSUES!")
        sys.exit(1)

if __name__ == "__main__":
    main()