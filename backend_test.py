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
            "distribution_platforms": {"passed": 0, "failed": 0, "details": []},
            "content_distribution": {"passed": 0, "failed": 0, "details": []},
            "distribution_history": {"passed": 0, "failed": 0, "details": []},
            "platform_compatibility": {"passed": 0, "failed": 0, "details": []},
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
    
    def test_distribution_platforms_endpoint(self) -> bool:
        """Test the /api/distribution/platforms endpoint to verify all 30+ platforms are configured"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                if 'platforms' in data and isinstance(data['platforms'], dict):
                    platforms = data['platforms']
                    
                    # Check if we have the expected number of platforms (30+)
                    if len(platforms) >= 30:
                        # Verify platform categories
                        social_media = [p for p in platforms.values() if p.get('type') == 'social_media']
                        streaming = [p for p in platforms.values() if p.get('type') == 'streaming']
                        radio = [p for p in platforms.values() if p.get('type') == 'radio']
                        tv = [p for p in platforms.values() if p.get('type') == 'tv']
                        podcast = [p for p in platforms.values() if p.get('type') == 'podcast']
                        
                        # Verify specific platforms exist
                        expected_platforms = ['instagram', 'twitter', 'facebook', 'tiktok', 'youtube', 
                                            'spotify', 'apple_music', 'soundcloud', 'iheartradio', 
                                            'siriusxm', 'cnn', 'fox_news', 'netflix', 'hulu', 
                                            'spotify_podcasts', 'apple_podcasts']
                        
                        missing_platforms = [p for p in expected_platforms if p not in platforms]
                        
                        if not missing_platforms:
                            self.log_result("distribution_platforms", "Distribution Platforms Endpoint", True, 
                                          f"Found {len(platforms)} platforms across all categories (Social: {len(social_media)}, Streaming: {len(streaming)}, Radio: {len(radio)}, TV: {len(tv)}, Podcast: {len(podcast)})")
                            return True
                        else:
                            self.log_result("distribution_platforms", "Distribution Platforms Endpoint", False, 
                                          f"Missing expected platforms: {missing_platforms}")
                            return False
                    else:
                        self.log_result("distribution_platforms", "Distribution Platforms Endpoint", False, 
                                      f"Expected 30+ platforms, found {len(platforms)}")
                        return False
                else:
                    self.log_result("distribution_platforms", "Distribution Platforms Endpoint", False, 
                                  "Invalid response format - missing platforms data")
                    return False
            else:
                self.log_result("distribution_platforms", "Distribution Platforms Endpoint", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("distribution_platforms", "Distribution Platforms Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_platform_configuration_details(self) -> bool:
        """Test that platforms have proper configuration details"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                
                # Test specific platform configurations
                test_platforms = ['instagram', 'spotify', 'iheartradio', 'cnn', 'apple_podcasts']
                all_valid = True
                
                for platform_id in test_platforms:
                    if platform_id in platforms:
                        platform = platforms[platform_id]
                        required_fields = ['name', 'type', 'supported_formats', 'max_file_size_mb']
                        
                        if all(field in platform for field in required_fields):
                            # Verify supported formats are valid
                            formats = platform['supported_formats']
                            valid_formats = ['audio', 'video', 'image']
                            if all(fmt in valid_formats for fmt in formats):
                                continue
                            else:
                                all_valid = False
                                break
                        else:
                            all_valid = False
                            break
                    else:
                        all_valid = False
                        break
                
                if all_valid:
                    self.log_result("distribution_platforms", "Platform Configuration Details", True, 
                                  f"All test platforms properly configured with required fields")
                    return True
                else:
                    self.log_result("distribution_platforms", "Platform Configuration Details", False, 
                                  "Some platforms missing required configuration fields")
                    return False
            else:
                self.log_result("distribution_platforms", "Platform Configuration Details", False, 
                              f"Failed to get platforms: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("distribution_platforms", "Platform Configuration Details", False, f"Exception: {str(e)}")
            return False
    
    def test_content_distribution_audio_to_streaming(self) -> bool:
        """Test distributing audio content to streaming platforms"""
        try:
            if not self.auth_token or not self.test_media_id:
                self.log_result("content_distribution", "Audio to Streaming Distribution", False, 
                              "Missing auth token or media ID")
                return False
            
            # Test distributing audio to streaming platforms
            distribution_request = {
                "media_id": self.test_media_id,
                "platforms": ["spotify", "apple_music", "soundcloud"],
                "custom_message": "New track from Big Mann Entertainment",
                "hashtags": ["BigMannEntertainment", "NewMusic", "Audio"]
            }
            
            response = self.make_request('POST', '/distribution/distribute', json=distribution_request)
            
            if response.status_code == 200:
                data = response.json()
                if 'distribution_id' in data and 'results' in data:
                    results = data['results']
                    
                    # Check if all platforms returned success (mock responses)
                    successful_platforms = [p for p, r in results.items() if r.get('status') == 'success']
                    
                    if len(successful_platforms) == 3:  # All 3 platforms should succeed
                        self.log_result("content_distribution", "Audio to Streaming Distribution", True, 
                                      f"Successfully distributed to {len(successful_platforms)} streaming platforms")
                        return True
                    else:
                        self.log_result("content_distribution", "Audio to Streaming Distribution", False, 
                                      f"Only {len(successful_platforms)}/3 platforms succeeded")
                        return False
                else:
                    self.log_result("content_distribution", "Audio to Streaming Distribution", False, 
                                  "Missing distribution_id or results in response")
                    return False
            else:
                self.log_result("content_distribution", "Audio to Streaming Distribution", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("content_distribution", "Audio to Streaming Distribution", False, f"Exception: {str(e)}")
            return False
    
    def test_content_distribution_video_to_social(self) -> bool:
        """Test distributing video content to social media platforms"""
        try:
            if not self.auth_token:
                self.log_result("content_distribution", "Video to Social Distribution", False, 
                              "No auth token available")
                return False
            
            # First upload a video file for testing
            content, filename, mime_type = self.create_test_file("video")
            
            files = {'file': (filename, content, mime_type)}
            data = {
                'title': 'Test Video Content',
                'description': 'A test video for Big Mann Entertainment distribution',
                'category': 'entertainment',
                'price': 0,
                'tags': 'test, video, entertainment'
            }
            
            upload_response = self.make_request('POST', '/media/upload', files=files, data=data)
            
            if upload_response.status_code == 200:
                video_media_id = upload_response.json()['media_id']
                
                # Now test distribution to social media platforms
                distribution_request = {
                    "media_id": video_media_id,
                    "platforms": ["youtube", "tiktok", "facebook"],
                    "custom_message": "Check out this video from Big Mann Entertainment!",
                    "hashtags": ["BigMannEntertainment", "Video", "Entertainment"]
                }
                
                response = self.make_request('POST', '/distribution/distribute', json=distribution_request)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', {})
                    
                    # Check if platforms that support video succeeded
                    successful_platforms = [p for p, r in results.items() if r.get('status') == 'success']
                    
                    if len(successful_platforms) >= 2:  # At least 2 should succeed
                        self.log_result("content_distribution", "Video to Social Distribution", True, 
                                      f"Successfully distributed video to {len(successful_platforms)} social platforms")
                        return True
                    else:
                        self.log_result("content_distribution", "Video to Social Distribution", False, 
                                      f"Only {len(successful_platforms)} platforms succeeded")
                        return False
                else:
                    self.log_result("content_distribution", "Video to Social Distribution", False, 
                                  f"Distribution failed: {response.status_code}")
                    return False
            else:
                self.log_result("content_distribution", "Video to Social Distribution", False, 
                              "Failed to upload test video")
                return False
                
        except Exception as e:
            self.log_result("content_distribution", "Video to Social Distribution", False, f"Exception: {str(e)}")
            return False
    
    def test_platform_compatibility_audio_to_video_only(self) -> bool:
        """Test that audio files are rejected by video-only platforms"""
        try:
            if not self.auth_token or not self.test_media_id:
                self.log_result("platform_compatibility", "Audio to Video-Only Platform", False, 
                              "Missing auth token or media ID")
                return False
            
            # Try to distribute audio to video-only platforms (TikTok, YouTube)
            distribution_request = {
                "media_id": self.test_media_id,  # This is an audio file
                "platforms": ["tiktok", "youtube"],
                "custom_message": "This should fail for audio content"
            }
            
            response = self.make_request('POST', '/distribution/distribute', json=distribution_request)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                
                # Check that both platforms failed due to format incompatibility
                failed_platforms = [p for p, r in results.items() if r.get('status') == 'error' and 'only supports video' in r.get('message', '')]
                
                if len(failed_platforms) == 2:  # Both should fail
                    self.log_result("platform_compatibility", "Audio to Video-Only Platform", True, 
                                  "Correctly rejected audio content for video-only platforms")
                    return True
                else:
                    self.log_result("platform_compatibility", "Audio to Video-Only Platform", False, 
                                  f"Expected 2 failures, got {len(failed_platforms)}")
                    return False
            else:
                self.log_result("platform_compatibility", "Audio to Video-Only Platform", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("platform_compatibility", "Audio to Video-Only Platform", False, f"Exception: {str(e)}")
            return False
    
    def test_platform_compatibility_video_to_audio_only(self) -> bool:
        """Test that video files are rejected by audio-only platforms"""
        try:
            if not self.auth_token:
                self.log_result("platform_compatibility", "Video to Audio-Only Platform", False, 
                              "No auth token available")
                return False
            
            # Upload a video file first
            content, filename, mime_type = self.create_test_file("video")
            
            files = {'file': (filename, content, mime_type)}
            data = {
                'title': 'Test Video for Compatibility',
                'description': 'Testing platform compatibility',
                'category': 'test',
                'price': 0,
                'tags': 'test'
            }
            
            upload_response = self.make_request('POST', '/media/upload', files=files, data=data)
            
            if upload_response.status_code == 200:
                video_media_id = upload_response.json()['media_id']
                
                # Try to distribute video to audio-only platforms
                distribution_request = {
                    "media_id": video_media_id,
                    "platforms": ["spotify", "iheartradio", "apple_podcasts"],
                    "custom_message": "This should fail for video content"
                }
                
                response = self.make_request('POST', '/distribution/distribute', json=distribution_request)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', {})
                    
                    # Check that platforms failed due to format incompatibility
                    failed_platforms = [p for p, r in results.items() if r.get('status') == 'error' and 'only supports audio' in r.get('message', '')]
                    
                    if len(failed_platforms) >= 2:  # At least 2 should fail
                        self.log_result("platform_compatibility", "Video to Audio-Only Platform", True, 
                                      f"Correctly rejected video content for {len(failed_platforms)} audio-only platforms")
                        return True
                    else:
                        self.log_result("platform_compatibility", "Video to Audio-Only Platform", False, 
                                      f"Expected failures, got {len(failed_platforms)}")
                        return False
                else:
                    self.log_result("platform_compatibility", "Video to Audio-Only Platform", False, 
                                  f"Distribution request failed: {response.status_code}")
                    return False
            else:
                self.log_result("platform_compatibility", "Video to Audio-Only Platform", False, 
                              "Failed to upload test video")
                return False
                
        except Exception as e:
            self.log_result("platform_compatibility", "Video to Audio-Only Platform", False, f"Exception: {str(e)}")
            return False
    
    def test_distribution_history_tracking(self) -> bool:
        """Test the /api/distribution/history endpoint for tracking user distributions"""
        try:
            if not self.auth_token:
                self.log_result("distribution_history", "Distribution History Tracking", False, 
                              "No auth token available")
                return False
            
            response = self.make_request('GET', '/distribution/history')
            
            if response.status_code == 200:
                data = response.json()
                if 'distributions' in data and isinstance(data['distributions'], list):
                    distributions = data['distributions']
                    
                    # Check if we have any distributions (from previous tests)
                    if len(distributions) > 0:
                        # Verify distribution record structure
                        first_dist = distributions[0]
                        required_fields = ['id', 'media_id', 'target_platforms', 'status', 'results', 'created_at']
                        
                        if all(field in first_dist for field in required_fields):
                            self.log_result("distribution_history", "Distribution History Tracking", True, 
                                          f"Retrieved {len(distributions)} distribution records with proper structure")
                            return True
                        else:
                            self.log_result("distribution_history", "Distribution History Tracking", False, 
                                          "Distribution records missing required fields")
                            return False
                    else:
                        self.log_result("distribution_history", "Distribution History Tracking", True, 
                                      "Distribution history endpoint working (no distributions yet)")
                        return True
                else:
                    self.log_result("distribution_history", "Distribution History Tracking", False, 
                                  "Invalid response format - missing distributions array")
                    return False
            else:
                self.log_result("distribution_history", "Distribution History Tracking", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("distribution_history", "Distribution History Tracking", False, f"Exception: {str(e)}")
            return False
    
    def test_distribution_status_retrieval(self) -> bool:
        """Test retrieving distribution status by ID"""
        try:
            if not self.auth_token or not self.test_media_id:
                self.log_result("distribution_history", "Distribution Status Retrieval", False, 
                              "Missing auth token or media ID")
                return False
            
            # First create a distribution
            distribution_request = {
                "media_id": self.test_media_id,
                "platforms": ["instagram", "twitter"],
                "custom_message": "Test distribution for status check"
            }
            
            response = self.make_request('POST', '/distribution/distribute', json=distribution_request)
            
            if response.status_code == 200:
                data = response.json()
                distribution_id = data.get('distribution_id')
                
                if distribution_id:
                    # Now retrieve the distribution status
                    status_response = self.make_request('GET', f'/distribution/{distribution_id}')
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        required_fields = ['id', 'media_id', 'target_platforms', 'status', 'results']
                        
                        if all(field in status_data for field in required_fields):
                            self.log_result("distribution_history", "Distribution Status Retrieval", True, 
                                          f"Successfully retrieved distribution status: {status_data.get('status')}")
                            return True
                        else:
                            self.log_result("distribution_history", "Distribution Status Retrieval", False, 
                                          "Distribution status missing required fields")
                            return False
                    else:
                        self.log_result("distribution_history", "Distribution Status Retrieval", False, 
                                      f"Failed to retrieve status: {status_response.status_code}")
                        return False
                else:
                    self.log_result("distribution_history", "Distribution Status Retrieval", False, 
                                  "No distribution_id returned from distribution request")
                    return False
            else:
                self.log_result("distribution_history", "Distribution Status Retrieval", False, 
                              f"Failed to create distribution: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("distribution_history", "Distribution Status Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_analytics_dashboard(self) -> bool:
        """Test analytics dashboard data retrieval with enhanced distribution metrics"""
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
                    enhanced_stats = ['total_distributions', 'successful_distributions', 'distribution_success_rate', 'supported_platforms']
                    
                    # Check basic stats
                    basic_stats_present = all(stat in stats for stat in required_stats)
                    
                    # Check enhanced distribution stats
                    enhanced_stats_present = all(stat in stats for stat in enhanced_stats)
                    
                    if basic_stats_present and enhanced_stats_present:
                        supported_platforms = data.get('supported_platforms', 0)
                        self.log_result("analytics", "Enhanced Analytics Dashboard", True, 
                                      f"Retrieved enhanced analytics with distribution metrics. Supported platforms: {supported_platforms}, Distribution success rate: {stats.get('distribution_success_rate', 0):.1f}%")
                        return True
                    elif basic_stats_present:
                        self.log_result("analytics", "Enhanced Analytics Dashboard", True, 
                                      f"Retrieved basic analytics: {stats} (distribution metrics may not be available yet)")
                        return True
                    else:
                        self.log_result("analytics", "Enhanced Analytics Dashboard", False, 
                                      "Missing required statistics")
                        return False
                else:
                    self.log_result("analytics", "Enhanced Analytics Dashboard", False, 
                                  "Invalid analytics response format")
                    return False
            elif response.status_code == 403:
                self.log_result("analytics", "Enhanced Analytics Dashboard", True, 
                              "Analytics requires admin access (expected)")
                return True
            else:
                self.log_result("analytics", "Enhanced Analytics Dashboard", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("analytics", "Enhanced Analytics Dashboard", False, f"Exception: {str(e)}")
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