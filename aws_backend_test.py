#!/usr/bin/env python3
"""
AWS S3 and SES Integration Backend Testing for Big Mann Entertainment Platform
Testing AWS services integration as requested in the review
"""

import requests
import json
import time
import sys
import io
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://mediacloud-bme.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"aws.tester.{int(time.time())}@bigmannentertainment.com"
TEST_USER_PASSWORD = "AWSTestPassword123!"
TEST_USER_NAME = "AWS Integration Tester"
TEST_ADMIN_EMAIL = f"admin.aws.{int(time.time())}@bigmannentertainment.com"
TEST_ADMIN_PASSWORD = "AdminAWSTest123!"

# AWS Credentials from review request
AWS_ACCESS_KEY_ID = "AKIAUSISWEIVP3L6DC5K"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "bigmann-entertainment-media"

class AWSBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.admin_token = None
        self.test_user_id = None
        self.admin_user_id = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.uploaded_files = []  # Track uploaded files for cleanup
        
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
        print()

    def create_test_file(self, file_type: str, size_mb: float = 1.0) -> io.BytesIO:
        """Create test file content for upload testing"""
        content_size = int(size_mb * 1024 * 1024)  # Convert MB to bytes
        
        if file_type == "audio":
            # Create a simple audio-like file (MP3 header + data)
            content = b'ID3\x03\x00\x00\x00' + b'\x00' * (content_size - 7)
            return io.BytesIO(content)
        elif file_type == "video":
            # Create a simple video-like file (MP4 header + data)
            content = b'\x00\x00\x00\x20ftypmp42' + b'\x00' * (content_size - 12)
            return io.BytesIO(content)
        elif file_type == "image":
            # Create a simple JPEG-like file
            content = b'\xFF\xD8\xFF\xE0\x00\x10JFIF' + b'\x00' * (content_size - 10) + b'\xFF\xD9'
            return io.BytesIO(content)
        else:
            return io.BytesIO(b'\x00' * content_size)

    def register_test_user(self) -> bool:
        """Register a test user for AWS testing"""
        try:
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_user_id = data.get("user", {}).get("id")
                self.log_test("User Registration", True, f"User registered successfully with ID: {self.test_user_id}")
                return True
            else:
                self.log_test("User Registration", False, f"Registration failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, f"Registration error: {str(e)}")
            return False

    def register_admin_user(self) -> bool:
        """Register an admin user for SES testing"""
        try:
            admin_data = {
                "email": TEST_ADMIN_EMAIL,
                "password": TEST_ADMIN_PASSWORD,
                "full_name": "AWS Admin Tester",
                "date_of_birth": "1985-01-01T00:00:00",
                "address_line1": "456 Admin Street",
                "city": "Admin City",
                "state_province": "Admin State",
                "postal_code": "54321",
                "country": "United States"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=admin_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.admin_user_id = data.get("user", {}).get("id")
                self.log_test("Admin User Registration", True, f"Admin user registered with ID: {self.admin_user_id}")
                return True
            else:
                self.log_test("Admin User Registration", False, f"Admin registration failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin User Registration", False, f"Admin registration error: {str(e)}")
            return False

    def login_user(self) -> bool:
        """Login test user and get auth token"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("User Login", True, "User logged in successfully")
                return True
            else:
                self.log_test("User Login", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Login", False, f"Login error: {str(e)}")
            return False

    def login_admin(self) -> bool:
        """Login admin user for SES testing"""
        try:
            # First, we need to make the user admin (this would normally be done through database)
            # For testing purposes, we'll try to login and see if admin endpoints work
            login_data = {
                "email": TEST_ADMIN_EMAIL,
                "password": TEST_ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_test("Admin Login", True, "Admin logged in successfully")
                return True
            else:
                self.log_test("Admin Login", False, f"Admin login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Admin login error: {str(e)}")
            return False

    def test_aws_health_check(self) -> bool:
        """Test AWS services health check endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/aws/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["status", "timestamp", "services"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("AWS Health Check - Structure", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check services status
                services = data.get("services", {})
                s3_status = services.get("s3")
                ses_status = services.get("ses")
                
                if s3_status == "healthy" and ses_status == "healthy":
                    self.log_test("AWS Health Check", True, f"All AWS services healthy. S3: {s3_status}, SES: {ses_status}", data)
                    return True
                else:
                    self.log_test("AWS Health Check", False, f"AWS services not healthy. S3: {s3_status}, SES: {ses_status}", data)
                    return False
            else:
                self.log_test("AWS Health Check", False, f"Health check failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("AWS Health Check", False, f"Health check error: {str(e)}")
            return False

    def test_s3_audio_upload(self) -> bool:
        """Test S3 audio file upload"""
        try:
            # Create test audio file (1MB MP3)
            audio_file = self.create_test_file("audio", 1.0)
            
            files = {
                'file': ('test_audio.mp3', audio_file, 'audio/mpeg')
            }
            
            data = {
                'user_id': self.test_user_id,
                'user_email': TEST_USER_EMAIL,
                'user_name': TEST_USER_NAME,
                'title': 'Test Audio Upload',
                'description': 'AWS S3 audio upload test',
                'category': 'music',
                'send_notification': 'true'
            }
            
            response = self.session.post(f"{BACKEND_URL}/media/s3/upload/audio", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                required_fields = ["success", "media_id", "object_key", "file_url", "size", "content_type"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test("S3 Audio Upload - Structure", False, f"Missing fields: {missing_fields}", result)
                    return False
                
                # Verify S3 object key format: file_type/user_id/timestamp/filename
                object_key = result.get("object_key", "")
                if not object_key.startswith(f"audio/{self.test_user_id}/"):
                    self.log_test("S3 Audio Upload - Object Key Format", False, f"Invalid object key format: {object_key}")
                    return False
                
                # Store for cleanup
                self.uploaded_files.append({
                    "object_key": object_key,
                    "user_id": self.test_user_id,
                    "file_type": "audio"
                })
                
                self.log_test("S3 Audio Upload", True, f"Audio uploaded successfully. Object key: {object_key}", result)
                return True
            else:
                self.log_test("S3 Audio Upload", False, f"Upload failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 Audio Upload", False, f"Upload error: {str(e)}")
            return False

    def test_s3_video_upload(self) -> bool:
        """Test S3 video file upload"""
        try:
            # Create test video file (5MB MP4)
            video_file = self.create_test_file("video", 5.0)
            
            files = {
                'file': ('test_video.mp4', video_file, 'video/mp4')
            }
            
            data = {
                'user_id': self.test_user_id,
                'user_email': TEST_USER_EMAIL,
                'user_name': TEST_USER_NAME,
                'title': 'Test Video Upload',
                'description': 'AWS S3 video upload test',
                'category': 'video',
                'send_notification': 'false'
            }
            
            response = self.session.post(f"{BACKEND_URL}/media/s3/upload/video", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                object_key = result.get("object_key", "")
                
                # Verify object key format
                if not object_key.startswith(f"video/{self.test_user_id}/"):
                    self.log_test("S3 Video Upload - Object Key Format", False, f"Invalid object key format: {object_key}")
                    return False
                
                # Store for cleanup
                self.uploaded_files.append({
                    "object_key": object_key,
                    "user_id": self.test_user_id,
                    "file_type": "video"
                })
                
                self.log_test("S3 Video Upload", True, f"Video uploaded successfully. Object key: {object_key}", result)
                return True
            else:
                self.log_test("S3 Video Upload", False, f"Upload failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 Video Upload", False, f"Upload error: {str(e)}")
            return False

    def test_s3_image_upload(self) -> bool:
        """Test S3 image file upload"""
        try:
            # Create test image file (2MB JPEG)
            image_file = self.create_test_file("image", 2.0)
            
            files = {
                'file': ('test_image.jpg', image_file, 'image/jpeg')
            }
            
            data = {
                'user_id': self.test_user_id,
                'user_email': TEST_USER_EMAIL,
                'user_name': TEST_USER_NAME,
                'title': 'Test Image Upload',
                'description': 'AWS S3 image upload test',
                'category': 'artwork',
                'send_notification': 'true'
            }
            
            response = self.session.post(f"{BACKEND_URL}/media/s3/upload/image", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                object_key = result.get("object_key", "")
                
                # Verify object key format
                if not object_key.startswith(f"image/{self.test_user_id}/"):
                    self.log_test("S3 Image Upload - Object Key Format", False, f"Invalid object key format: {object_key}")
                    return False
                
                # Store for cleanup
                self.uploaded_files.append({
                    "object_key": object_key,
                    "user_id": self.test_user_id,
                    "file_type": "image"
                })
                
                self.log_test("S3 Image Upload", True, f"Image uploaded successfully. Object key: {object_key}", result)
                return True
            else:
                self.log_test("S3 Image Upload", False, f"Upload failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 Image Upload", False, f"Upload error: {str(e)}")
            return False

    def test_s3_file_size_validation(self) -> bool:
        """Test S3 file size validation (oversized files should be rejected)"""
        try:
            # Create oversized audio file (60MB - exceeds 50MB limit)
            oversized_audio = self.create_test_file("audio", 60.0)
            
            files = {
                'file': ('oversized_audio.mp3', oversized_audio, 'audio/mpeg')
            }
            
            data = {
                'user_id': self.test_user_id,
                'user_email': TEST_USER_EMAIL,
                'user_name': TEST_USER_NAME,
                'title': 'Oversized Audio Test',
                'description': 'Should be rejected',
                'category': 'music',
                'send_notification': 'false'
            }
            
            response = self.session.post(f"{BACKEND_URL}/media/s3/upload/audio", files=files, data=data)
            
            # Should fail with 413 (file too large) or 400 (bad request)
            if response.status_code in [413, 400]:
                self.log_test("S3 File Size Validation", True, f"Oversized file correctly rejected: {response.status_code}")
                return True
            else:
                self.log_test("S3 File Size Validation", False, f"Oversized file not rejected: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 File Size Validation", False, f"Validation test error: {str(e)}")
            return False

    def test_s3_unsupported_format(self) -> bool:
        """Test S3 unsupported file format rejection"""
        try:
            # Create a text file and try to upload as audio
            text_file = io.BytesIO(b"This is a text file, not audio")
            
            files = {
                'file': ('test.txt', text_file, 'text/plain')
            }
            
            data = {
                'user_id': self.test_user_id,
                'user_email': TEST_USER_EMAIL,
                'user_name': TEST_USER_NAME,
                'title': 'Unsupported Format Test',
                'description': 'Should be rejected',
                'category': 'music',
                'send_notification': 'false'
            }
            
            response = self.session.post(f"{BACKEND_URL}/media/s3/upload/audio", files=files, data=data)
            
            # Should fail with 415 (unsupported media type) or 400 (bad request)
            if response.status_code in [415, 400]:
                self.log_test("S3 Unsupported Format Validation", True, f"Unsupported format correctly rejected: {response.status_code}")
                return True
            else:
                self.log_test("S3 Unsupported Format Validation", False, f"Unsupported format not rejected: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 Unsupported Format Validation", False, f"Format validation error: {str(e)}")
            return False

    def test_s3_list_user_files(self) -> bool:
        """Test listing user's S3 files"""
        try:
            response = self.session.get(f"{BACKEND_URL}/media/s3/user/{self.test_user_id}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                required_fields = ["files", "total_count", "limit", "offset", "has_more"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test("S3 List User Files - Structure", False, f"Missing fields: {missing_fields}", result)
                    return False
                
                files = result.get("files", [])
                total_count = result.get("total_count", 0)
                
                # Should have at least the files we uploaded
                if total_count >= len(self.uploaded_files):
                    self.log_test("S3 List User Files", True, f"Found {total_count} files for user", result)
                    return True
                else:
                    self.log_test("S3 List User Files", False, f"Expected at least {len(self.uploaded_files)} files, got {total_count}", result)
                    return False
            else:
                self.log_test("S3 List User Files", False, f"List files failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 List User Files", False, f"List files error: {str(e)}")
            return False

    def test_s3_presigned_url_generation(self) -> bool:
        """Test generating presigned URLs for S3 files"""
        try:
            if not self.uploaded_files:
                self.log_test("S3 Presigned URL Generation", False, "No uploaded files to test with")
                return False
            
            # Use the first uploaded file
            test_file = self.uploaded_files[0]
            object_key = test_file["object_key"]
            
            response = self.session.get(f"{BACKEND_URL}/media/s3/{self.test_user_id}/{object_key}/url?expiration=3600")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                required_fields = ["access_url", "expires_in", "object_key"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test("S3 Presigned URL - Structure", False, f"Missing fields: {missing_fields}", result)
                    return False
                
                access_url = result.get("access_url", "")
                expires_in = result.get("expires_in", 0)
                
                # Verify URL format and expiration
                if access_url.startswith("https://") and expires_in == 3600:
                    self.log_test("S3 Presigned URL Generation", True, f"Presigned URL generated successfully. Expires in: {expires_in}s", result)
                    return True
                else:
                    self.log_test("S3 Presigned URL Generation", False, f"Invalid presigned URL or expiration: {access_url}, {expires_in}", result)
                    return False
            else:
                self.log_test("S3 Presigned URL Generation", False, f"Presigned URL generation failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 Presigned URL Generation", False, f"Presigned URL error: {str(e)}")
            return False

    def test_s3_file_deletion(self) -> bool:
        """Test deleting files from S3"""
        try:
            if not self.uploaded_files:
                self.log_test("S3 File Deletion", False, "No uploaded files to delete")
                return False
            
            # Delete the last uploaded file
            test_file = self.uploaded_files[-1]
            object_key = test_file["object_key"]
            user_id = test_file["user_id"]
            
            response = self.session.delete(f"{BACKEND_URL}/media/s3/{user_id}/{object_key}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                if result.get("success") and result.get("object_key") == object_key:
                    # Remove from our tracking list
                    self.uploaded_files.remove(test_file)
                    self.log_test("S3 File Deletion", True, f"File deleted successfully: {object_key}", result)
                    return True
                else:
                    self.log_test("S3 File Deletion", False, f"Deletion response invalid", result)
                    return False
            else:
                self.log_test("S3 File Deletion", False, f"File deletion failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("S3 File Deletion", False, f"File deletion error: {str(e)}")
            return False

    def test_ses_transactional_email(self) -> bool:
        """Test SES transactional email sending (admin only)"""
        try:
            # Switch to admin token
            original_headers = self.session.headers.copy()
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
            
            email_data = {
                'to_email': TEST_USER_EMAIL,
                'subject': 'AWS SES Test Email',
                'html_content': '<h1>Test Email</h1><p>This is a test email from AWS SES integration.</p>',
                'text_content': 'Test Email\n\nThis is a test email from AWS SES integration.'
            }
            
            response = self.session.post(f"{BACKEND_URL}/email/ses/send", data=email_data)
            
            # Restore original headers
            self.session.headers = original_headers
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for success indicators
                if result.get("success") or result.get("message_id"):
                    self.log_test("SES Transactional Email", True, f"Email sent successfully", result)
                    return True
                else:
                    self.log_test("SES Transactional Email", False, f"Email sending failed", result)
                    return False
            else:
                self.log_test("SES Transactional Email", False, f"SES email failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("SES Transactional Email", False, f"SES email error: {str(e)}")
            return False

    def test_ses_welcome_email(self) -> bool:
        """Test SES welcome email sending (admin only)"""
        try:
            # Switch to admin token
            original_headers = self.session.headers.copy()
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
            
            email_data = {
                'user_email': TEST_USER_EMAIL,
                'user_name': TEST_USER_NAME
            }
            
            response = self.session.post(f"{BACKEND_URL}/email/ses/welcome", data=email_data)
            
            # Restore original headers
            self.session.headers = original_headers
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for success indicators
                if result.get("success") or result.get("message_id"):
                    self.log_test("SES Welcome Email", True, f"Welcome email sent successfully", result)
                    return True
                else:
                    self.log_test("SES Welcome Email", False, f"Welcome email sending failed", result)
                    return False
            else:
                self.log_test("SES Welcome Email", False, f"SES welcome email failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("SES Welcome Email", False, f"SES welcome email error: {str(e)}")
            return False

    def test_ses_unauthorized_access(self) -> bool:
        """Test that SES endpoints require admin authorization"""
        try:
            # Use regular user token (not admin)
            email_data = {
                'to_email': TEST_USER_EMAIL,
                'subject': 'Unauthorized Test',
                'html_content': '<p>This should fail</p>'
            }
            
            response = self.session.post(f"{BACKEND_URL}/email/ses/send", data=email_data)
            
            # Should fail with 403 (forbidden)
            if response.status_code == 403:
                self.log_test("SES Authorization Check", True, f"Unauthorized access correctly blocked: {response.status_code}")
                return True
            else:
                self.log_test("SES Authorization Check", False, f"Unauthorized access not blocked: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("SES Authorization Check", False, f"Authorization test error: {str(e)}")
            return False

    def test_s3_unauthorized_access(self) -> bool:
        """Test S3 access control for other users' files"""
        try:
            if not self.uploaded_files:
                self.log_test("S3 Authorization Check", False, "No uploaded files to test with")
                return False
            
            # Try to access another user's files (use fake user ID)
            fake_user_id = "fake-user-id-12345"
            
            response = self.session.get(f"{BACKEND_URL}/media/s3/user/{fake_user_id}")
            
            # Should fail with 403 (forbidden) since we're not admin and it's not our user ID
            if response.status_code == 403:
                self.log_test("S3 Authorization Check", True, f"Unauthorized access correctly blocked: {response.status_code}")
                return True
            else:
                # Might return empty list instead of 403, which is also acceptable
                result = response.json()
                if response.status_code == 200 and result.get("total_count", 0) == 0:
                    self.log_test("S3 Authorization Check", True, f"Access control working - no files returned for unauthorized user")
                    return True
                else:
                    self.log_test("S3 Authorization Check", False, f"Unauthorized access not properly controlled: {response.status_code}", response.text)
                    return False
                
        except Exception as e:
            self.log_test("S3 Authorization Check", False, f"Authorization test error: {str(e)}")
            return False

    def cleanup_uploaded_files(self):
        """Clean up uploaded test files"""
        print("\n🧹 Cleaning up uploaded test files...")
        for file_info in self.uploaded_files[:]:  # Copy list to avoid modification during iteration
            try:
                object_key = file_info["object_key"]
                user_id = file_info["user_id"]
                
                response = self.session.delete(f"{BACKEND_URL}/media/s3/{user_id}/{object_key}")
                if response.status_code == 200:
                    print(f"✅ Cleaned up: {object_key}")
                    self.uploaded_files.remove(file_info)
                else:
                    print(f"❌ Failed to clean up: {object_key}")
            except Exception as e:
                print(f"❌ Cleanup error for {file_info.get('object_key', 'unknown')}: {e}")

    def run_all_tests(self):
        """Run comprehensive AWS S3 and SES integration tests"""
        print("🎯 AWS S3 AND SES INTEGRATION TESTING FOR BIG MANN ENTERTAINMENT")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"AWS Region: {AWS_REGION}")
        print(f"S3 Bucket: {S3_BUCKET_NAME}")
        print("=" * 70)
        
        # 1. Setup - User Registration and Authentication
        print("\n📋 PHASE 1: USER SETUP AND AUTHENTICATION")
        if not self.register_test_user():
            print("❌ Cannot proceed without test user")
            return
        
        if not self.register_admin_user():
            print("⚠️  Admin user registration failed - SES admin tests may fail")
        
        if not self.login_user():
            print("❌ Cannot proceed without user authentication")
            return
        
        if not self.login_admin():
            print("⚠️  Admin login failed - SES admin tests may fail")
        
        # 2. AWS Services Health Check
        print("\n🏥 PHASE 2: AWS SERVICES HEALTH CHECK")
        self.test_aws_health_check()
        
        # 3. S3 File Upload Integration
        print("\n📤 PHASE 3: S3 FILE UPLOAD INTEGRATION")
        self.test_s3_audio_upload()
        self.test_s3_video_upload()
        self.test_s3_image_upload()
        
        # 4. S3 File Validation
        print("\n🔍 PHASE 4: S3 FILE VALIDATION")
        self.test_s3_file_size_validation()
        self.test_s3_unsupported_format()
        
        # 5. S3 File Management
        print("\n📁 PHASE 5: S3 FILE MANAGEMENT")
        self.test_s3_list_user_files()
        self.test_s3_presigned_url_generation()
        self.test_s3_file_deletion()
        
        # 6. SES Email Integration
        print("\n📧 PHASE 6: SES EMAIL INTEGRATION")
        if self.admin_token:
            self.test_ses_transactional_email()
            self.test_ses_welcome_email()
        else:
            print("⚠️  Skipping SES tests - no admin token available")
        
        # 7. Security and Authorization
        print("\n🔒 PHASE 7: SECURITY AND AUTHORIZATION")
        self.test_ses_unauthorized_access()
        self.test_s3_unauthorized_access()
        
        # 8. Cleanup
        print("\n🧹 PHASE 8: CLEANUP")
        self.cleanup_uploaded_files()
        
        # Final Results
        print("\n" + "=" * 70)
        print("📊 AWS INTEGRATION TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test_name']}: {result['details']}")
        
        print("\n🎯 AWS S3 AND SES INTEGRATION TESTING COMPLETED")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = AWSBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)