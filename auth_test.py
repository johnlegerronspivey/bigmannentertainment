#!/usr/bin/env python3
"""
Authentication Testing Suite for Big Mann Entertainment Platform
Tests authentication system after WebAuthn/Face ID removal
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "auth.test@bigmannentertainment.com"
TEST_USER_PASSWORD = "AuthTest2025!"
TEST_USER_NAME = "Authentication Test User"
TEST_BUSINESS_NAME = "Big Mann Entertainment"

class AuthenticationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "business_functionality": {"passed": 0, "failed": 0, "details": []},
            "media_management": {"passed": 0, "failed": 0, "details": []},
            "distribution_platforms": {"passed": 0, "failed": 0, "details": []}
        }
    
    def log_result(self, category: str, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results[category]["failed"] += 1
            status = "❌ FAIL"
        
        self.results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise
    
    def test_user_registration(self) -> bool:
        """Test standard user registration with username/password"""
        try:
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "business_name": TEST_BUSINESS_NAME,
                "date_of_birth": (datetime.utcnow() - timedelta(days=25*365)).isoformat(),
                "address_line1": "1314 Lincoln Heights Street",
                "city": "Alexander City",
                "state_province": "Alabama",
                "postal_code": "35010",
                "country": "United States"
            }
            
            response = self.make_request('POST', '/auth/register', json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data['user']['id']
                    self.log_result("authentication", "User Registration", True, 
                                  f"Successfully registered user with standard auth")
                    return True
                else:
                    self.log_result("authentication", "User Registration", False, 
                                  "Missing token or user data in response")
                    return False
            elif response.status_code == 400 and "already registered" in response.text:
                self.log_result("authentication", "User Registration", True, "User already exists (expected)")
                return True
            else:
                self.log_result("authentication", "User Registration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "User Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_user_login(self) -> bool:
        """Test standard user login with email/password"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data['user']['id']
                    self.log_result("authentication", "User Login", True, 
                                  "Successfully logged in with email/password")
                    return True
                else:
                    self.log_result("authentication", "User Login", False, 
                                  "Missing token or user data in response")
                    return False
            else:
                self.log_result("authentication", "User Login", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "User Login", False, f"Exception: {str(e)}")
            return False
    
    def test_token_refresh(self) -> bool:
        """Test JWT token refresh functionality"""
        try:
            refresh_data = {
                "refresh_token": "dummy_refresh_token_for_testing"
            }
            
            response = self.make_request('POST', '/auth/refresh', json=refresh_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.log_result("authentication", "Token Refresh", True, 
                                  "Token refresh endpoint working correctly")
                    return True
                else:
                    self.log_result("authentication", "Token Refresh", False, 
                                  "Missing access_token in refresh response")
                    return False
            elif response.status_code == 401 and ("Invalid" in response.text or "expired" in response.text):
                self.log_result("authentication", "Token Refresh", True, 
                              "Token refresh correctly validates refresh tokens")
                return True
            else:
                self.log_result("authentication", "Token Refresh", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "Token Refresh", False, f"Exception: {str(e)}")
            return False
    
    def test_logout(self) -> bool:
        """Test user logout functionality"""
        try:
            if not self.auth_token:
                self.log_result("authentication", "User Logout", False, "No auth token available")
                return False
            
            response = self.make_request('POST', '/auth/logout')
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'logged out' in data['message'].lower():
                    self.log_result("authentication", "User Logout", True, 
                                  "Successfully logged out")
                    return True
                else:
                    self.log_result("authentication", "User Logout", False, 
                                  f"Unexpected logout response: {data}")
                    return False
            else:
                self.log_result("authentication", "User Logout", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "User Logout", False, f"Exception: {str(e)}")
            return False
    
    def test_forgot_password(self) -> bool:
        """Test forgot password functionality"""
        try:
            forgot_password_data = {
                "email": TEST_USER_EMAIL
            }
            
            response = self.make_request('POST', '/auth/forgot-password', json=forgot_password_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'reset' in data['message'].lower():
                    self.log_result("authentication", "Forgot Password", True, 
                                  "Password reset initiated successfully")
                    return True
                else:
                    self.log_result("authentication", "Forgot Password", False, 
                                  f"Unexpected response format: {data}")
                    return False
            elif response.status_code == 500 and "not configured" in response.text:
                self.log_result("authentication", "Forgot Password", True, 
                              "Email service not configured (expected in test environment)")
                return True
            else:
                self.log_result("authentication", "Forgot Password", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "Forgot Password", False, f"Exception: {str(e)}")
            return False
    
    def test_reset_password(self) -> bool:
        """Test password reset functionality"""
        try:
            reset_password_data = {
                "token": "dummy_reset_token_for_testing",
                "new_password": "NewPassword123!"
            }
            
            response = self.make_request('POST', '/auth/reset-password', json=reset_password_data)
            
            if response.status_code == 400 and ("Invalid" in response.text or "expired" in response.text):
                self.log_result("authentication", "Reset Password", True, 
                              "Correctly rejected invalid/expired reset token")
                return True
            elif response.status_code == 200:
                self.log_result("authentication", "Reset Password", True, 
                              "Password reset endpoint working")
                return True
            else:
                self.log_result("authentication", "Reset Password", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "Reset Password", False, f"Exception: {str(e)}")
            return False
    
    def test_webauthn_endpoints_removed(self) -> bool:
        """Test that WebAuthn endpoints have been removed and return 404"""
        try:
            webauthn_endpoints = [
                '/auth/webauthn/register/begin',
                '/auth/webauthn/register/complete',
                '/auth/webauthn/authenticate/begin',
                '/auth/webauthn/authenticate/complete',
                '/auth/webauthn/credentials'
            ]
            
            all_removed = True
            for endpoint in webauthn_endpoints:
                response = self.make_request('POST', endpoint)
                if response.status_code != 404:
                    self.log_result("authentication", f"WebAuthn Endpoint Removed {endpoint}", False, 
                                  f"Expected 404, got {response.status_code}")
                    all_removed = False
                else:
                    self.log_result("authentication", f"WebAuthn Endpoint Removed {endpoint}", True, 
                                  "Correctly returns 404 - endpoint removed")
            
            if all_removed:
                self.log_result("authentication", "WebAuthn Endpoints Removed", True, 
                              "All WebAuthn endpoints correctly removed (return 404)")
                return True
            else:
                self.log_result("authentication", "WebAuthn Endpoints Removed", False, 
                              "Some WebAuthn endpoints still exist")
                return False
                
        except Exception as e:
            self.log_result("authentication", "WebAuthn Endpoints Removed", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_routes_security(self) -> bool:
        """Test that protected routes require JWT authentication"""
        try:
            protected_endpoints = [
                ('/auth/me', 'GET'),
                ('/media/upload', 'POST'),
                ('/media/library', 'GET'),
                ('/admin/users', 'GET'),
                ('/admin/analytics', 'GET')
            ]
            
            all_protected = True
            # Test without auth token
            original_token = self.auth_token
            self.auth_token = None
            
            for endpoint, method in protected_endpoints:
                response = self.make_request(method, endpoint)
                if response.status_code not in [401, 403]:
                    self.log_result("authentication", f"Protected Route {method} {endpoint}", False, 
                                  f"Expected 401/403, got {response.status_code}")
                    all_protected = False
                else:
                    self.log_result("authentication", f"Protected Route {method} {endpoint}", True, 
                                  f"Correctly rejected with {response.status_code}")
            
            # Restore auth token
            self.auth_token = original_token
            
            if all_protected:
                self.log_result("authentication", "Protected Routes Security", True, 
                              "All protected routes correctly require authentication")
                return True
            else:
                self.log_result("authentication", "Protected Routes Security", False, 
                              "Some protected routes allow unauthenticated access")
                return False
                
        except Exception as e:
            self.auth_token = original_token if 'original_token' in locals() else self.auth_token
            self.log_result("authentication", "Protected Routes Security", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_endpoints_permissions(self) -> bool:
        """Test that admin endpoints require proper admin permissions"""
        try:
            if not self.auth_token:
                self.log_result("authentication", "Admin Endpoints Permissions", False, "No auth token available")
                return False
            
            admin_endpoints = [
                ('/admin/users', 'GET'),
                ('/admin/content', 'GET'),
                ('/admin/analytics', 'GET')
            ]
            
            all_protected = True
            for endpoint, method in admin_endpoints:
                response = self.make_request(method, endpoint)
                if response.status_code == 200:
                    self.log_result("authentication", f"Admin {method} {endpoint}", True, 
                                  "Admin endpoint accessible (user has admin permissions)")
                elif response.status_code == 403:
                    self.log_result("authentication", f"Admin {method} {endpoint}", True, 
                                  "Admin endpoint correctly requires admin permissions")
                else:
                    self.log_result("authentication", f"Admin {method} {endpoint}", False, 
                                  f"Unexpected status: {response.status_code}")
                    all_protected = False
            
            if all_protected:
                self.log_result("authentication", "Admin Endpoints Permissions", True, 
                              "All admin endpoints properly check permissions")
                return True
            else:
                self.log_result("authentication", "Admin Endpoints Permissions", False, 
                              "Some admin endpoints have permission issues")
                return False
                
        except Exception as e:
            self.log_result("authentication", "Admin Endpoints Permissions", False, f"Exception: {str(e)}")
            return False
    
    def test_business_identifiers_endpoint(self) -> bool:
        """Test business identifiers endpoint works with standard auth"""
        try:
            if not self.auth_token:
                self.log_result("business_functionality", "Business Identifiers Access", False, "No auth token available")
                return False
            
            response = self.make_request('GET', '/business/identifiers')
            
            if response.status_code == 200:
                data = response.json()
                if 'business_legal_name' in data and 'business_ein' in data:
                    expected_ein = "270658077"
                    expected_name = "Big Mann Entertainment"
                    
                    if data.get('business_ein') == expected_ein and expected_name in data.get('business_legal_name', ''):
                        self.log_result("business_functionality", "Business Identifiers Access", True, 
                                      f"Successfully retrieved business identifiers - EIN: {data['business_ein']}")
                        return True
                    else:
                        self.log_result("business_functionality", "Business Identifiers Access", False, 
                                      f"Incorrect business data - EIN: {data.get('business_ein')}")
                        return False
                else:
                    self.log_result("business_functionality", "Business Identifiers Access", False, 
                                  "Missing required business identifier fields")
                    return False
            else:
                self.log_result("business_functionality", "Business Identifiers Access", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("business_functionality", "Business Identifiers Access", False, f"Exception: {str(e)}")
            return False
    
    def test_distribution_platforms_endpoint(self) -> bool:
        """Test distribution platforms endpoint works with standard auth"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                if 'platforms' in data and isinstance(data['platforms'], list):
                    platforms = data['platforms']
                    platform_count = len(platforms)
                    
                    # Check for expected platforms
                    platform_names = [p.get('name', '') for p in platforms]
                    expected_platforms = ['Instagram', 'Twitter/X', 'Facebook', 'Spotify', 'YouTube']
                    found_platforms = [name for name in expected_platforms if name in platform_names]
                    
                    if platform_count >= 90 and len(found_platforms) >= 3:
                        self.log_result("distribution_platforms", "Distribution Platforms Access", True, 
                                      f"Successfully retrieved {platform_count} platforms including: {', '.join(found_platforms[:5])}")
                        return True
                    else:
                        self.log_result("distribution_platforms", "Distribution Platforms Access", False, 
                                      f"Insufficient platforms or missing expected ones - Count: {platform_count}")
                        return False
                else:
                    self.log_result("distribution_platforms", "Distribution Platforms Access", False, 
                                  "Invalid platforms response format")
                    return False
            else:
                self.log_result("distribution_platforms", "Distribution Platforms Access", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("distribution_platforms", "Distribution Platforms Access", False, f"Exception: {str(e)}")
            return False
    
    def test_media_library_with_auth(self) -> bool:
        """Test media library access works with standard authentication"""
        try:
            if not self.auth_token:
                self.log_result("media_management", "Media Library Auth Access", False, "No auth token available")
                return False
            
            response = self.make_request('GET', '/media/library')
            
            if response.status_code == 200:
                data = response.json()
                if 'media' in data and isinstance(data['media'], list):
                    self.log_result("media_management", "Media Library Auth Access", True, 
                                  f"Successfully accessed media library with {len(data['media'])} items")
                    return True
                else:
                    self.log_result("media_management", "Media Library Auth Access", False, 
                                  "Invalid media library response format")
                    return False
            else:
                self.log_result("media_management", "Media Library Auth Access", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("media_management", "Media Library Auth Access", False, f"Exception: {str(e)}")
            return False
    
    def test_media_upload_with_auth(self) -> bool:
        """Test media upload works with standard authentication"""
        try:
            if not self.auth_token:
                self.log_result("media_management", "Media Upload Auth", False, "No auth token available")
                return False
            
            # Create a simple test file
            content = b"RIFF\x24\x08WAVE"  # Minimal WAV header
            filename = "test_auth_audio.wav"
            mime_type = "audio/wav"
            
            files = {'file': (filename, content, mime_type)}
            data = {
                'title': 'Authentication Test Track',
                'description': 'Testing media upload with standard authentication',
                'category': 'music',
                'price': 9.99,
                'tags': 'authentication, test, BigMannEntertainment'
            }
            
            response = self.make_request('POST', '/media/upload', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'media_id' in result:
                    self.log_result("media_management", "Media Upload Auth", True, 
                                  f"Successfully uploaded media with standard auth, ID: {result['media_id']}")
                    return True
                else:
                    self.log_result("media_management", "Media Upload Auth", False, 
                                  "Missing media_id in upload response")
                    return False
            else:
                self.log_result("media_management", "Media Upload Auth", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("media_management", "Media Upload Auth", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🎯 STARTING AUTHENTICATION SYSTEM TESTING AFTER WEBAUTHN REMOVAL")
        print("=" * 80)
        
        # Standard Authentication Tests
        print("\n📋 TESTING STANDARD AUTHENTICATION...")
        self.test_user_registration()
        self.test_user_login()
        self.test_token_refresh()
        self.test_logout()
        self.test_forgot_password()
        self.test_reset_password()
        
        # WebAuthn Removal Verification
        print("\n🚫 TESTING WEBAUTHN ENDPOINTS REMOVAL...")
        self.test_webauthn_endpoints_removed()
        
        # Security Tests
        print("\n🔒 TESTING PROTECTED ENDPOINTS SECURITY...")
        self.test_protected_routes_security()
        self.test_admin_endpoints_permissions()
        
        # Business Functionality Tests
        print("\n🏢 TESTING BUSINESS FUNCTIONALITY PRESERVATION...")
        self.test_business_identifiers_endpoint()
        self.test_distribution_platforms_endpoint()
        self.test_media_library_with_auth()
        self.test_media_upload_with_auth()
        
        # Print Results
        print("\n" + "=" * 80)
        print("🎯 AUTHENTICATION TESTING RESULTS SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            if results["details"]:
                for detail in results["details"]:
                    print(f"    {detail}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📊 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%" if (total_passed + total_failed) > 0 else "  📊 Success Rate: 0%")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)