#!/usr/bin/env python3
"""
Enhanced Upload Component Backend Integration Testing for Big Mann Entertainment Platform
Testing AWS S3 Upload Endpoints, Metadata Handling, File Validation, Authentication, and Error Handling
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import tempfile

# Configuration
BACKEND_URL = "https://bigmannentertainment.com/api"
TEST_USER_EMAIL = "enhanced.upload.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "EnhancedUpload123!"
TEST_USER_NAME = "Enhanced Upload Tester"

class EnhancedUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.user_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test_name": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
            
    def create_test_file(self, file_type: str, size_mb: float = 1.0) -> tuple:
        """Create test files for different types"""
        content_types = {
            'audio': ('test_audio.mp3', 'audio/mpeg', b'ID3\x03\x00\x00\x00' + b'0' * int(size_mb * 1024 * 1024 - 10)),
            'video': ('test_video.mp4', 'video/mp4', b'\x00\x00\x00\x20ftypmp42' + b'0' * int(size_mb * 1024 * 1024 - 12)),
            'image': ('test_image.jpg', 'image/jpeg', b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'0' * int(size_mb * 1024 * 1024 - 14)),
            'metadata': ('test_metadata.json', 'application/json', json.dumps({
                "title": "Test Track",
                "artist": "Test Artist",
                "album": "Test Album",
                "genre": "Hip-Hop",
                "duration": "3:45"
            }).encode() + b'0' * max(0, int(size_mb * 1024 * 1024 - 200)))
        }
        
        if file_type not in content_types:
            raise ValueError(f"Unsupported file type: {file_type}")
            
        filename, content_type, content = content_types[file_type]
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}")
        temp_file.write(content)
        temp_file.close()
        
        return temp_file.name, filename, content_type

    def authenticate(self):
        """Authenticate and get access token"""
        print("\n🔐 Testing Authentication...")
        
        # First try to register user
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            if response.status_code in [200, 201]:
                self.log_test("User Registration", True, "User registered successfully")
            elif response.status_code == 400 and "already exists" in response.text.lower():
                self.log_test("User Registration", True, "User already exists, proceeding to login")
            else:
                self.log_test("User Registration", False, f"Registration failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("User Registration", False, f"Registration error: {str(e)}")
        
        # Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("User Login", True, f"Login successful, user_id: {self.user_id}")
                return True
            else:
                self.log_test("User Login", False, f"Login failed: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Login error: {str(e)}")
            return False

    def test_enhanced_upload_endpoints(self):
        """Test Enhanced Upload Component specific endpoints"""
        print("\n🎯 Testing Enhanced Upload Component Endpoints...")
        
        # Test specific Enhanced Upload Component endpoints mentioned in review
        enhanced_endpoints = [
            "/media/s3/upload/media",
            "/media/s3/upload/artwork", 
            "/media/s3/upload/metadata"
        ]
        
        for endpoint in enhanced_endpoints:
            try:
                # Test with OPTIONS to check if endpoint exists
                response = self.session.options(f"{BACKEND_URL}{endpoint}")
                if response.status_code in [200, 405]:
                    self.log_test(f"Enhanced Upload Endpoint Exists: {endpoint}", True, 
                                f"Endpoint accessible (Status: {response.status_code})")
                else:
                    self.log_test(f"Enhanced Upload Endpoint Exists: {endpoint}", False, 
                                f"Endpoint not found (Status: {response.status_code})")
            except Exception as e:
                self.log_test(f"Enhanced Upload Endpoint Exists: {endpoint}", False, f"Error: {str(e)}")

    def test_s3_upload_endpoints(self):
        """Test AWS S3 Upload Endpoints for Enhanced Upload Component"""
        print("\n📤 Testing AWS S3 Upload Endpoints...")
        
        # Test file types as specified in review request
        file_types = {
            'audio': {'formats': ['MP3', 'WAV', 'FLAC'], 'max_size': 500},  # 500MB
            'video': {'formats': ['MP4', 'AVI', 'MOV'], 'max_size': 500},   # 500MB  
            'image': {'formats': ['JPG', 'PNG', 'GIF'], 'max_size': 10},    # 10MB
            'metadata': {'formats': ['TXT', 'JSON', 'XML', 'PDF'], 'max_size': 5}  # 5MB
        }
        
        for file_type, config in file_types.items():
            self.test_file_upload(file_type, config['max_size'])

    def test_file_upload(self, file_type: str, max_size_mb: int):
        """Test file upload for specific type"""
        try:
            # Create test file (small size for testing)
            temp_file_path, filename, content_type = self.create_test_file(file_type, 0.1)  # 0.1MB test file
            
            # Enhanced metadata as specified in review request
            enhanced_metadata = {
                'user_id': self.user_id,
                'user_email': TEST_USER_EMAIL,
                'user_name': TEST_USER_NAME,
                'title': f'Test {file_type.title()} Upload',
                'description': f'Testing Enhanced Upload Component for {file_type}',
                'category': file_type,
                'send_notification': True,
                # Enhanced metadata fields from review request
                'metadata_title': f'Enhanced {file_type.title()} Title',
                'metadata_artist': 'Big Mann Entertainment',
                'metadata_album': 'Test Album 2025',
                'metadata_isrc': 'USRC17607839',
                'metadata_upc': '123456789012',
                'metadata_rightsHolders': 'Big Mann Entertainment LLC',
                'metadata_genre': 'Hip-Hop',
                'metadata_releaseDate': '2025-01-15',
                'metadata_description': f'Enhanced Upload Component test for {file_type} files',
                'metadata_tags': 'test,enhanced,upload,component',
                'metadata_copyrightYear': 2025,
                'metadata_publisherName': 'Big Mann Publishing',
                'metadata_composerName': 'Test Composer',
                'metadata_duration': '3:45'
            }
            
            # Test current S3 upload endpoint
            with open(temp_file_path, 'rb') as f:
                files = {'file': (filename, f, content_type)}
                response = self.session.post(
                    f"{BACKEND_URL}/media/s3/upload/{file_type}",
                    files=files,
                    data=enhanced_metadata
                )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(f"S3 Upload - {file_type.title()}", True, 
                            f"Upload successful, file_url: {data.get('file_url', 'N/A')}")
                
                # Verify enhanced metadata was processed
                metadata = data.get('metadata', {})
                if metadata.get('title') and metadata.get('artist'):
                    self.log_test(f"Enhanced Metadata Processing - {file_type.title()}", True,
                                f"Metadata processed: title={metadata.get('title')}, artist={metadata.get('artist')}")
                else:
                    self.log_test(f"Enhanced Metadata Processing - {file_type.title()}", False,
                                "Enhanced metadata not properly processed")
                    
            else:
                self.log_test(f"S3 Upload - {file_type.title()}", False, 
                            f"Upload failed: {response.status_code}", response.text)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.log_test(f"S3 Upload - {file_type.title()}", False, f"Error: {str(e)}")

    def test_file_validation(self):
        """Test File Type and Size Validation"""
        print("\n🔍 Testing File Type and Size Validation...")
        
        # Test oversized files
        oversized_tests = [
            ('audio', 501),  # Over 500MB limit
            ('video', 501),  # Over 500MB limit  
            ('image', 11),   # Over 10MB limit
            ('metadata', 6)  # Over 5MB limit
        ]
        
        for file_type, size_mb in oversized_tests:
            try:
                temp_file_path, filename, content_type = self.create_test_file(file_type, size_mb)
                
                with open(temp_file_path, 'rb') as f:
                    files = {'file': (filename, f, content_type)}
                    data = {
                        'user_id': self.user_id,
                        'user_email': TEST_USER_EMAIL,
                        'user_name': TEST_USER_NAME,
                        'title': f'Oversized {file_type} Test'
                    }
                    response = self.session.post(
                        f"{BACKEND_URL}/media/s3/upload/{file_type}",
                        files=files,
                        data=data
                    )
                
                # Should reject oversized files
                if response.status_code in [413, 422, 400]:
                    self.log_test(f"File Size Validation - {file_type.title()} ({size_mb}MB)", True,
                                f"Correctly rejected oversized file (Status: {response.status_code})")
                else:
                    self.log_test(f"File Size Validation - {file_type.title()} ({size_mb}MB)", False,
                                f"Should reject oversized file but got: {response.status_code}")
                
                os.unlink(temp_file_path)
                
            except Exception as e:
                self.log_test(f"File Size Validation - {file_type.title()}", False, f"Error: {str(e)}")

    def test_authentication_requirements(self):
        """Test Authentication Requirements for Upload Endpoints"""
        print("\n🔒 Testing Authentication Requirements...")
        
        # Save current auth token
        original_token = self.session.headers.get("Authorization")
        
        # Test without authentication
        self.session.headers.pop("Authorization", None)
        
        try:
            temp_file_path, filename, content_type = self.create_test_file('audio', 0.1)
            
            with open(temp_file_path, 'rb') as f:
                files = {'file': (filename, f, content_type)}
                data = {
                    'user_id': 'test_user',
                    'user_email': TEST_USER_EMAIL,
                    'user_name': TEST_USER_NAME,
                    'title': 'Unauthorized Test'
                }
                response = self.session.post(
                    f"{BACKEND_URL}/media/s3/upload/audio",
                    files=files,
                    data=data
                )
            
            if response.status_code in [401, 403]:
                self.log_test("Authentication Required", True,
                            f"Correctly rejected unauthorized request (Status: {response.status_code})")
            else:
                self.log_test("Authentication Required", False,
                            f"Should require authentication but got: {response.status_code}")
            
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.log_test("Authentication Required", False, f"Error: {str(e)}")
        
        # Restore authentication
        if original_token:
            self.session.headers["Authorization"] = original_token

    def test_aws_integration(self):
        """Test AWS S3 Service Integration"""
        print("\n☁️ Testing AWS S3 Integration...")
        
        # Test AWS health check
        try:
            response = self.session.get(f"{BACKEND_URL}/aws/health")
            if response.status_code == 200:
                data = response.json()
                s3_status = data.get('s3', {}).get('status')
                if s3_status == 'healthy':
                    self.log_test("AWS S3 Integration", True, "S3 service is healthy and accessible")
                else:
                    self.log_test("AWS S3 Integration", False, f"S3 status: {s3_status}")
            else:
                self.log_test("AWS S3 Integration", False, f"Health check failed: {response.status_code}")
        except Exception as e:
            self.log_test("AWS S3 Integration", False, f"Error: {str(e)}")

    def test_error_handling(self):
        """Test Error Handling for Various Scenarios"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test invalid file type
        try:
            temp_file_path, filename, content_type = self.create_test_file('audio', 0.1)
            
            with open(temp_file_path, 'rb') as f:
                files = {'file': (filename, f, content_type)}
                data = {
                    'user_id': self.user_id,
                    'user_email': TEST_USER_EMAIL,
                    'user_name': TEST_USER_NAME,
                    'title': 'Invalid Type Test'
                }
                response = self.session.post(
                    f"{BACKEND_URL}/media/s3/upload/invalid_type",
                    files=files,
                    data=data
                )
            
            if response.status_code in [400, 422]:
                self.log_test("Invalid File Type Error Handling", True,
                            f"Correctly rejected invalid file type (Status: {response.status_code})")
            else:
                self.log_test("Invalid File Type Error Handling", False,
                            f"Should reject invalid file type but got: {response.status_code}")
            
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.log_test("Invalid File Type Error Handling", False, f"Error: {str(e)}")
        
        # Test missing required fields
        try:
            temp_file_path, filename, content_type = self.create_test_file('audio', 0.1)
            
            with open(temp_file_path, 'rb') as f:
                files = {'file': (filename, f, content_type)}
                # Missing required fields
                data = {}
                response = self.session.post(
                    f"{BACKEND_URL}/media/s3/upload/audio",
                    files=files,
                    data=data
                )
            
            if response.status_code in [400, 422]:
                self.log_test("Missing Fields Error Handling", True,
                            f"Correctly rejected missing required fields (Status: {response.status_code})")
            else:
                self.log_test("Missing Fields Error Handling", False,
                            f"Should reject missing fields but got: {response.status_code}")
            
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.log_test("Missing Fields Error Handling", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all Enhanced Upload Component tests"""
        print("🎵 ENHANCED UPLOAD COMPONENT BACKEND INTEGRATION TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run all test suites
        self.test_enhanced_upload_endpoints()
        self.test_s3_upload_endpoints()
        self.test_file_validation()
        self.test_authentication_requirements()
        self.test_aws_integration()
        self.test_error_handling()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 ENHANCED UPLOAD COMPONENT TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        print("\n🎵 Enhanced Upload Component Backend Integration Testing Complete!")
        print("=" * 70)

if __name__ == "__main__":
    tester = EnhancedUploadTester()
    tester.run_all_tests()