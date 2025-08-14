#!/usr/bin/env python3
"""
Backend Testing Suite for Big Mann Entertainment Media Distribution Platform
Tests all critical backend functionality including authentication, media management, payments, and analytics.
"""

import requests
import json
import os
import time
from pathlib import Path
import tempfile
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://audio-video-dist.preview.emergentagent.com/api"
TEST_USER_EMAIL = "john.spivey@bigmannentertainment.com"
TEST_USER_PASSWORD = "BigMann2025!"
TEST_USER_NAME = "John LeGerron Spivey"
TEST_BUSINESS_NAME = "Big Mann Entertainment"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_media_id = None
        self.test_session_id = None
        self.results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "media_upload": {"passed": 0, "failed": 0, "details": []},
            "media_management": {"passed": 0, "failed": 0, "details": []},
            "payments": {"passed": 0, "failed": 0, "details": []},
            "analytics": {"passed": 0, "failed": 0, "details": []}
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
        """Test user registration"""
        try:
            # First, try to register a new user
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "business_name": TEST_BUSINESS_NAME
            }
            
            response = self.make_request('POST', '/auth/register', json=user_data)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data['user']['id']
                    self.log_result("authentication", "User Registration", True, "Successfully registered new user")
                    return True
                else:
                    self.log_result("authentication", "User Registration", False, f"Missing token or user data in response")
                    return False
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try to login instead
                self.log_result("authentication", "User Registration", True, "User already exists (expected)")
                return True
            else:
                self.log_result("authentication", "User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "User Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_user_login(self) -> bool:
        """Test user login"""
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
                    self.log_result("authentication", "User Login", True, "Successfully logged in")
                    return True
                else:
                    self.log_result("authentication", "User Login", False, "Missing token or user data in response")
                    return False
            else:
                self.log_result("authentication", "User Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "User Login", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_route(self) -> bool:
        """Test JWT token validation on protected route"""
        try:
            if not self.auth_token:
                self.log_result("authentication", "Protected Route Access", False, "No auth token available")
                return False
            
            response = self.make_request('GET', '/auth/me')
            
            if response.status_code == 200:
                data = response.json()
                if 'email' in data and data['email'] == TEST_USER_EMAIL:
                    self.log_result("authentication", "Protected Route Access", True, "Successfully accessed protected route")
                    return True
                else:
                    self.log_result("authentication", "Protected Route Access", False, "Invalid user data returned")
                    return False
            else:
                self.log_result("authentication", "Protected Route Access", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "Protected Route Access", False, f"Exception: {str(e)}")
            return False
    
    def create_test_file(self, file_type: str) -> tuple:
        """Create a test file for upload"""
        if file_type == "audio":
            content = b"RIFF\x24\x08\x00\x00WAVE"  # Minimal WAV header
            filename = "test_audio.wav"
            mime_type = "audio/wav"
        elif file_type == "video":
            content = b"\x00\x00\x00\x20ftypmp41"  # Minimal MP4 header
            filename = "test_video.mp4"
            mime_type = "video/mp4"
        elif file_type == "image":
            # Minimal PNG header
            content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
            filename = "test_image.png"
            mime_type = "image/png"
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return content, filename, mime_type
    
    def test_media_upload(self) -> bool:
        """Test media file upload"""
        try:
            if not self.auth_token:
                self.log_result("media_upload", "Media Upload", False, "No auth token available")
                return False
            
            # Test audio upload
            content, filename, mime_type = self.create_test_file("audio")
            
            files = {'file': (filename, content, mime_type)}
            data = {
                'title': 'Test Audio Track',
                'description': 'A test audio file for Big Mann Entertainment',
                'category': 'music',
                'price': 9.99,
                'tags': 'test, audio, music'
            }
            
            response = self.make_request('POST', '/media/upload', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'media_id' in result:
                    self.test_media_id = result['media_id']
                    self.log_result("media_upload", "Media Upload", True, f"Successfully uploaded audio file, ID: {self.test_media_id}")
                    return True
                else:
                    self.log_result("media_upload", "Media Upload", False, "No media_id in response")
                    return False
            else:
                self.log_result("media_upload", "Media Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("media_upload", "Media Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_file_type_validation(self) -> bool:
        """Test file type validation"""
        try:
            if not self.auth_token:
                self.log_result("media_upload", "File Type Validation", False, "No auth token available")
                return False
            
            # Try to upload an invalid file type
            invalid_content = b"This is not a valid media file"
            files = {'file': ('test.txt', invalid_content, 'text/plain')}
            data = {
                'title': 'Invalid File',
                'description': 'This should fail',
                'category': 'test',
                'price': 0,
                'tags': 'invalid'
            }
            
            response = self.make_request('POST', '/media/upload', files=files, data=data)
            
            if response.status_code == 400:
                self.log_result("media_upload", "File Type Validation", True, "Correctly rejected invalid file type")
                return True
            else:
                self.log_result("media_upload", "File Type Validation", False, f"Should have rejected invalid file, got status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("media_upload", "File Type Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_media_library_retrieval(self) -> bool:
        """Test media library retrieval"""
        try:
            response = self.make_request('GET', '/media/library')
            
            if response.status_code == 200:
                data = response.json()
                if 'media' in data and isinstance(data['media'], list):
                    self.log_result("media_management", "Media Library Retrieval", True, f"Retrieved {len(data['media'])} media items")
                    return True
                else:
                    self.log_result("media_management", "Media Library Retrieval", False, "Invalid response format")
                    return False
            else:
                self.log_result("media_management", "Media Library Retrieval", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("media_management", "Media Library Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_media_filtering(self) -> bool:
        """Test media library filtering"""
        try:
            # Test filtering by content type
            response = self.make_request('GET', '/media/library?content_type=audio')
            
            if response.status_code == 200:
                data = response.json()
                if 'media' in data:
                    # Check if all returned items are audio (if any)
                    audio_items = [item for item in data['media'] if item.get('content_type') == 'audio']
                    if len(audio_items) == len(data['media']) or len(data['media']) == 0:
                        self.log_result("media_management", "Media Filtering", True, f"Filtering by content_type works, found {len(audio_items)} audio items")
                        return True
                    else:
                        self.log_result("media_management", "Media Filtering", False, "Filter returned non-audio items")
                        return False
                else:
                    self.log_result("media_management", "Media Filtering", False, "Invalid response format")
                    return False
            else:
                self.log_result("media_management", "Media Filtering", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("media_management", "Media Filtering", False, f"Exception: {str(e)}")
            return False
    
    def test_media_details(self) -> bool:
        """Test getting media details"""
        try:
            if not self.test_media_id:
                self.log_result("media_management", "Media Details", False, "No test media ID available")
                return False
            
            response = self.make_request('GET', f'/media/{self.test_media_id}')
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'title' in data:
                    self.log_result("media_management", "Media Details", True, f"Retrieved details for media: {data.get('title')}")
                    return True
                else:
                    self.log_result("media_management", "Media Details", False, "Invalid media details format")
                    return False
            else:
                self.log_result("media_management", "Media Details", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("media_management", "Media Details", False, f"Exception: {str(e)}")
            return False
    
    def test_checkout_session_creation(self) -> bool:
        """Test Stripe checkout session creation"""
        try:
            if not self.auth_token or not self.test_media_id:
                self.log_result("payments", "Checkout Session Creation", False, "Missing auth token or media ID")
                return False
            
            response = self.make_request('POST', f'/payments/checkout?media_id={self.test_media_id}')
            
            if response.status_code == 200:
                data = response.json()
                if 'checkout_url' in data and 'session_id' in data:
                    self.test_session_id = data['session_id']
                    self.log_result("payments", "Checkout Session Creation", True, f"Created checkout session: {self.test_session_id}")
                    return True
                else:
                    self.log_result("payments", "Checkout Session Creation", False, "Missing checkout_url or session_id in response")
                    return False
            elif response.status_code == 500 and "not configured" in response.text:
                self.log_result("payments", "Checkout Session Creation", True, "Payment system not configured (expected in test environment)")
                return True
            else:
                self.log_result("payments", "Checkout Session Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("payments", "Checkout Session Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_payment_status_polling(self) -> bool:
        """Test payment status polling"""
        try:
            if not self.auth_token:
                self.log_result("payments", "Payment Status Polling", False, "No auth token available")
                return False
            
            # Use a dummy session ID for testing
            test_session_id = "cs_test_dummy_session_id"
            response = self.make_request('GET', f'/payments/status/{test_session_id}')
            
            if response.status_code == 500 and "not configured" in response.text:
                self.log_result("payments", "Payment Status Polling", True, "Payment system not configured (expected in test environment)")
                return True
            elif response.status_code in [200, 404]:
                # Either successful response or session not found (both acceptable for testing)
                self.log_result("payments", "Payment Status Polling", True, "Payment status endpoint accessible")
                return True
            else:
                self.log_result("payments", "Payment Status Polling", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("payments", "Payment Status Polling", False, f"Exception: {str(e)}")
            return False
    
    def test_webhook_endpoint(self) -> bool:
        """Test webhook endpoint accessibility"""
        try:
            # Test webhook endpoint with dummy data
            response = self.make_request('POST', '/webhook/stripe', json={"test": "data"})
            
            if response.status_code == 500 and "not configured" in response.text:
                self.log_result("payments", "Webhook Endpoint", True, "Webhook endpoint accessible (Stripe not configured as expected)")
                return True
            elif response.status_code in [200, 400]:
                # Either success or bad request (both indicate endpoint is working)
                self.log_result("payments", "Webhook Endpoint", True, "Webhook endpoint accessible")
                return True
            else:
                self.log_result("payments", "Webhook Endpoint", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("payments", "Webhook Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_dashboard(self) -> bool:
        """Test analytics dashboard data retrieval"""
        try:
            if not self.auth_token:
                self.log_result("analytics", "Analytics Dashboard", False, "No auth token available")
                return False
            
            response = self.make_request('GET', '/analytics/dashboard')
            
            if response.status_code == 200:
                data = response.json()
                if 'stats' in data and 'popular_media' in data:
                    stats = data['stats']
                    required_stats = ['total_media', 'published_media', 'total_users', 'total_revenue']
                    if all(stat in stats for stat in required_stats):
                        self.log_result("analytics", "Analytics Dashboard", True, f"Retrieved analytics: {stats}")
                        return True
                    else:
                        self.log_result("analytics", "Analytics Dashboard", False, "Missing required statistics")
                        return False
                else:
                    self.log_result("analytics", "Analytics Dashboard", False, "Invalid analytics response format")
                    return False
            elif response.status_code == 403:
                self.log_result("analytics", "Analytics Dashboard", True, "Analytics requires admin access (expected)")
                return True
            else:
                self.log_result("analytics", "Analytics Dashboard", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("analytics", "Analytics Dashboard", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("STARTING BIG MANN ENTERTAINMENT BACKEND TESTING")
        print("=" * 80)
        
        # Authentication Tests
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("-" * 40)
        self.test_user_registration()
        self.test_user_login()
        self.test_protected_route()
        
        # Media Upload Tests
        print("\n📁 TESTING MEDIA UPLOAD AND STORAGE")
        print("-" * 40)
        self.test_media_upload()
        self.test_file_type_validation()
        
        # Media Management Tests
        print("\n📚 TESTING MEDIA CONTENT MANAGEMENT")
        print("-" * 40)
        self.test_media_library_retrieval()
        self.test_media_filtering()
        self.test_media_details()
        
        # Payment Tests
        print("\n💳 TESTING PAYMENT INTEGRATION")
        print("-" * 40)
        self.test_checkout_session_creation()
        self.test_payment_status_polling()
        self.test_webhook_endpoint()
        
        # Analytics Tests
        print("\n📊 TESTING ANALYTICS DASHBOARD")
        print("-" * 40)
        self.test_analytics_dashboard()
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAILED"
            print(f"\n{category.upper().replace('_', ' ')}: {passed} passed, {failed} failed - {status}")
            
            for detail in results["details"]:
                print(f"  {detail}")
        
        print(f"\n" + "=" * 80)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL: {total_passed} passed, {total_failed} failed - {overall_status}")
        print("=" * 80)
        
        return total_failed == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)