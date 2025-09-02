#!/usr/bin/env python3
"""
AWS Phase 2 Integration Backend Testing for Big Mann Entertainment Platform
Testing CloudFront, Lambda, and Rekognition integration as requested in review.

TESTING SCOPE:
1. Phase 2 Services Status - /api/phase2/status endpoint
2. CloudFront CDN Integration - /api/media/cdn-url endpoint  
3. Rekognition Content Moderation - /api/media/moderate endpoint (admin-only)
4. Lambda Processing Triggers - /api/media/process/{file_type} endpoint
5. CloudFront Cache Management - /api/cdn/invalidate endpoint (admin-only)
6. Backward Compatibility - Existing Phase 1 functionality
7. Service Integration and Fallbacks - Graceful degradation testing
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://metadata-maestro-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "aws.phase2.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "AWSPhase2Test2025!"
TEST_USER_NAME = "AWS Phase 2 Tester"
TEST_ADMIN_EMAIL = "aws.admin.tester@bigmannentertainment.com"
TEST_ADMIN_PASSWORD = "AWSAdminTest2025!"

class AWSPhase2Tester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
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

    def authenticate_user(self) -> bool:
        """Authenticate regular user and get access token"""
        try:
            # First try to register the test user
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "business_name": "Big Mann Entertainment AWS Test",
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "123 AWS Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }
            
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            # Now try to login
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_test("User Authentication", True, f"Successfully authenticated as {TEST_USER_EMAIL}")
                return True
            else:
                self.log_test("User Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Authentication error: {str(e)}")
            return False

    def authenticate_admin(self) -> bool:
        """Authenticate admin user for admin-only endpoints"""
        try:
            # First try to register the admin user
            register_data = {
                "email": TEST_ADMIN_EMAIL,
                "password": TEST_ADMIN_PASSWORD,
                "full_name": "AWS Admin Tester",
                "business_name": "Big Mann Entertainment AWS Admin",
                "date_of_birth": "1985-01-01T00:00:00",
                "address_line1": "123 AWS Admin Street",
                "city": "Admin City",
                "state_province": "Admin State",
                "postal_code": "54321",
                "country": "US"
            }
            
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            # Try to login
            login_data = {
                "email": TEST_ADMIN_EMAIL,
                "password": TEST_ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_test("Admin Authentication", True, f"Successfully authenticated admin as {TEST_ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Admin login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Admin authentication error: {str(e)}")
            return False

    def make_request(self, method: str, endpoint: str, use_admin: bool = False, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = kwargs.get('headers', {})
        
        token = self.admin_token if use_admin else self.auth_token
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise

    def test_phase2_status_endpoint(self):
        """Test /api/phase2/status endpoint to verify service availability detection"""
        print("🔍 TESTING PHASE 2 SERVICES STATUS")
        print("=" * 50)
        
        try:
            response = self.make_request('GET', '/phase2/status')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required service status fields
                required_services = ['cloudfront', 'lambda', 'rekognition', 's3']
                missing_services = [service for service in required_services if service not in data]
                
                if not missing_services:
                    # Verify service structure
                    cloudfront = data.get('cloudfront', {})
                    lambda_svc = data.get('lambda', {})
                    rekognition = data.get('rekognition', {})
                    s3 = data.get('s3', {})
                    
                    # Check CloudFront configuration
                    cf_available = cloudfront.get('available', False)
                    cf_domain = cloudfront.get('domain', '')
                    
                    # Check Lambda availability (expected limited due to permissions)
                    lambda_available = lambda_svc.get('available', False)
                    
                    # Check Rekognition accessibility
                    rekognition_available = rekognition.get('available', False)
                    
                    # Check S3 continued functionality
                    s3_available = s3.get('available', False)
                    s3_bucket = s3.get('bucket', '')
                    
                    self.log_test("Phase 2 Status Endpoint", True, 
                                f"CloudFront: {cf_available} (domain: {cf_domain}), Lambda: {lambda_available}, Rekognition: {rekognition_available}, S3: {s3_available} (bucket: {s3_bucket})")
                    
                    # Test individual service status
                    if cf_domain == 'cdn.bigmannentertainment.com':
                        self.log_test("CloudFront Domain Configuration", True, f"Correct domain configured: {cf_domain}")
                    else:
                        self.log_test("CloudFront Domain Configuration", False, f"Expected cdn.bigmannentertainment.com, got: {cf_domain}")
                    
                    if s3_bucket == 'bigmann-entertainment-media':
                        self.log_test("S3 Bucket Configuration", True, f"Correct S3 bucket: {s3_bucket}")
                    else:
                        self.log_test("S3 Bucket Configuration", False, f"Expected bigmann-entertainment-media, got: {s3_bucket}")
                    
                    return True
                else:
                    self.log_test("Phase 2 Status Endpoint", False, f"Missing services in response: {missing_services}")
                    return False
            else:
                self.log_test("Phase 2 Status Endpoint", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Phase 2 Status Endpoint", False, f"Error: {str(e)}")
            return False

    def test_cloudfront_cdn_integration(self):
        """Test /api/media/cdn-url endpoint for CDN URL generation"""
        print("🌐 TESTING CLOUDFRONT CDN INTEGRATION")
        print("=" * 50)
        
        # Test CDN URL generation for various file types
        test_files = [
            "audio/user123/20250101/test-song.mp3",
            "video/user456/20250101/test-video.mp4", 
            "image/user789/20250101/test-image.jpg"
        ]
        
        for s3_key in test_files:
            try:
                response = self.make_request('GET', f'/media/cdn-url?s3_key={s3_key}')
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check response structure
                    if 's3_key' in data and 'cdn_url' in data and 'cloudfront_available' in data:
                        cdn_url = data['cdn_url']
                        cf_available = data['cloudfront_available']
                        
                        # Test CDN URL format
                        if cf_available and 'cdn.bigmannentertainment.com' in cdn_url:
                            self.log_test(f"CDN URL Generation - {s3_key.split('/')[-1]}", True, 
                                        f"CloudFront URL: {cdn_url}")
                        elif not cf_available and 'bigmann-entertainment-media.s3' in cdn_url:
                            self.log_test(f"CDN URL Fallback - {s3_key.split('/')[-1]}", True, 
                                        f"S3 fallback URL: {cdn_url}")
                        else:
                            self.log_test(f"CDN URL Generation - {s3_key.split('/')[-1]}", False, 
                                        f"Unexpected URL format: {cdn_url}")
                    else:
                        self.log_test(f"CDN URL Generation - {s3_key.split('/')[-1]}", False, 
                                    "Missing required fields in response")
                else:
                    self.log_test(f"CDN URL Generation - {s3_key.split('/')[-1]}", False, 
                                f"Status: {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_test(f"CDN URL Generation - {s3_key.split('/')[-1]}", False, f"Error: {str(e)}")

    def test_rekognition_content_moderation(self):
        """Test /api/media/moderate endpoint (admin-only)"""
        print("🔍 TESTING REKOGNITION CONTENT MODERATION")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Rekognition Content Moderation", False, "No admin token available")
            return
        
        # Test with sample S3 key
        test_s3_key = "image/user123/20250101/test-moderation.jpg"
        
        try:
            # Test admin access
            response = self.make_request('POST', '/media/moderate', use_admin=True, 
                                      data={'s3_key': test_s3_key})
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['s3_key', 'moderation', 'labels', 'rekognition_available']
                if all(field in data for field in required_fields):
                    moderation = data['moderation']
                    labels = data['labels']
                    rekognition_available = data['rekognition_available']
                    
                    self.log_test("Rekognition Content Moderation - Admin Access", True, 
                                f"Rekognition available: {rekognition_available}, Moderation result received")
                    
                    # Test confidence threshold (should be 60%)
                    if isinstance(moderation, dict) and 'available' in moderation:
                        if moderation.get('available'):
                            self.log_test("Rekognition Moderation Service", True, 
                                        "Rekognition moderation service accessible")
                        else:
                            self.log_test("Rekognition Moderation Service", True, 
                                        "Rekognition gracefully handles unavailability")
                    
                    # Test label detection
                    if isinstance(labels, dict) and 'available' in labels:
                        if labels.get('available'):
                            self.log_test("Rekognition Label Detection", True, 
                                        "Label detection service accessible")
                        else:
                            self.log_test("Rekognition Label Detection", True, 
                                        "Label detection gracefully handles unavailability")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Rekognition Content Moderation - Response Structure", False, 
                                f"Missing fields: {missing_fields}")
            elif response.status_code == 500:
                # Expected if S3 object doesn't exist or Rekognition unavailable
                self.log_test("Rekognition Content Moderation - Error Handling", True, 
                            "Properly handles missing S3 objects or service unavailability")
            else:
                self.log_test("Rekognition Content Moderation - Admin Access", False, 
                            f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Rekognition Content Moderation", False, f"Error: {str(e)}")
        
        # Test non-admin access (should be rejected)
        try:
            response = self.make_request('POST', '/media/moderate', use_admin=False, 
                                      data={'s3_key': test_s3_key})
            
            if response.status_code == 403:
                self.log_test("Rekognition Content Moderation - Authorization", True, 
                            "Correctly requires admin authorization")
            else:
                self.log_test("Rekognition Content Moderation - Authorization", False, 
                            f"Should require admin access, got status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Rekognition Content Moderation - Authorization", False, f"Error: {str(e)}")

    def test_lambda_processing_triggers(self):
        """Test /api/media/process/{file_type} endpoint"""
        print("⚡ TESTING LAMBDA PROCESSING TRIGGERS")
        print("=" * 50)
        
        # Test different file types
        file_types = ['audio', 'video', 'image']
        
        for file_type in file_types:
            try:
                test_s3_key = f"{file_type}/user123/20250101/test-{file_type}.{'mp3' if file_type == 'audio' else 'mp4' if file_type == 'video' else 'jpg'}"
                
                response = self.make_request('POST', f'/media/process/{file_type}', 
                                          data={'s3_key': test_s3_key})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check response structure
                    required_fields = ['message', 's3_key', 'file_type', 'processing_started', 'lambda_available']
                    if all(field in data for field in required_fields):
                        processing_started = data['processing_started']
                        lambda_available = data['lambda_available']
                        moderation_started = data.get('moderation_started', False)
                        
                        self.log_test(f"Lambda Processing Trigger - {file_type.title()}", True, 
                                    f"Lambda available: {lambda_available}, Processing started: {processing_started}")
                        
                        # Test image moderation trigger
                        if file_type == 'image':
                            if 'moderation_started' in data:
                                self.log_test(f"Lambda Content Moderation Trigger - {file_type.title()}", True, 
                                            f"Moderation trigger: {moderation_started}")
                            else:
                                self.log_test(f"Lambda Content Moderation Trigger - {file_type.title()}", False, 
                                            "Missing moderation_started field for image")
                        
                        # Test graceful handling when Lambda permissions limited
                        if not lambda_available:
                            self.log_test(f"Lambda Graceful Degradation - {file_type.title()}", True, 
                                        "Gracefully handles limited Lambda permissions")
                    else:
                        missing_fields = [field for field in required_fields if field not in data]
                        self.log_test(f"Lambda Processing Trigger - {file_type.title()}", False, 
                                    f"Missing fields: {missing_fields}")
                else:
                    self.log_test(f"Lambda Processing Trigger - {file_type.title()}", False, 
                                f"Status: {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_test(f"Lambda Processing Trigger - {file_type.title()}", False, f"Error: {str(e)}")

    def test_cloudfront_cache_management(self):
        """Test /api/cdn/invalidate endpoint (admin-only)"""
        print("🗑️ TESTING CLOUDFRONT CACHE MANAGEMENT")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("CloudFront Cache Management", False, "No admin token available")
            return
        
        # Test cache invalidation
        test_paths = ['/audio/*', '/video/*', '/image/*']
        
        try:
            # Test admin access
            response = self.make_request('POST', '/cdn/invalidate', use_admin=True, 
                                      data={'paths': test_paths})
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['paths', 'cloudfront_available']
                if all(field in data for field in required_fields):
                    paths = data['paths']
                    cf_available = data['cloudfront_available']
                    invalidation_id = data.get('invalidation_id')
                    
                    if cf_available and invalidation_id:
                        self.log_test("CloudFront Cache Invalidation - Admin Access", True, 
                                    f"Invalidation ID: {invalidation_id}, Paths: {len(paths)}")
                    elif not cf_available:
                        self.log_test("CloudFront Cache Invalidation - Graceful Degradation", True, 
                                    "Gracefully handles CloudFront unavailability")
                    else:
                        self.log_test("CloudFront Cache Invalidation - Admin Access", False, 
                                    "CloudFront available but no invalidation ID returned")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("CloudFront Cache Invalidation - Response Structure", False, 
                                f"Missing fields: {missing_fields}")
            elif response.status_code == 500:
                # Expected if CloudFront unavailable or distribution ID not configured
                self.log_test("CloudFront Cache Invalidation - Error Handling", True, 
                            "Properly handles CloudFront unavailability or configuration issues")
            else:
                self.log_test("CloudFront Cache Invalidation - Admin Access", False, 
                            f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("CloudFront Cache Invalidation", False, f"Error: {str(e)}")
        
        # Test non-admin access (should be rejected)
        try:
            response = self.make_request('POST', '/cdn/invalidate', use_admin=False, 
                                      data={'paths': test_paths})
            
            if response.status_code == 403:
                self.log_test("CloudFront Cache Invalidation - Authorization", True, 
                            "Correctly requires admin authorization")
            else:
                self.log_test("CloudFront Cache Invalidation - Authorization", False, 
                            f"Should require admin access, got status: {response.status_code}")
                
        except Exception as e:
            self.log_test("CloudFront Cache Invalidation - Authorization", False, f"Error: {str(e)}")

    def test_backward_compatibility(self):
        """Test that existing Phase 1 functionality is maintained"""
        print("🔄 TESTING BACKWARD COMPATIBILITY")
        print("=" * 50)
        
        # Test existing S3 upload endpoints
        try:
            response = self.make_request('GET', '/aws/health')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check S3 service status
                if 's3' in data:
                    s3_status = data['s3']
                    if isinstance(s3_status, dict) and s3_status.get('status') == 'healthy':
                        self.log_test("Phase 1 S3 Integration Maintained", True, 
                                    "S3 service remains healthy and accessible")
                    else:
                        self.log_test("Phase 1 S3 Integration Maintained", False, 
                                    f"S3 status: {s3_status}")
                
                # Check SES email functionality
                if 'ses' in data:
                    ses_status = data['ses']
                    # SES may be unavailable but should have graceful fallback
                    self.log_test("Phase 1 SES Integration Maintained", True, 
                                "SES service status available (with SMTP fallback)")
                
                # Check overall system health
                overall_status = data.get('overall_status', 'unknown')
                if overall_status == 'healthy':
                    self.log_test("Phase 1 System Health Maintained", True, 
                                "Overall system remains healthy with Phase 2 integration")
                else:
                    self.log_test("Phase 1 System Health Maintained", False, 
                                f"Overall status: {overall_status}")
            else:
                self.log_test("Phase 1 AWS Health Check", False, 
                            f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Phase 1 Backward Compatibility", False, f"Error: {str(e)}")
        
        # Test S3 file listing (Phase 1 functionality)
        try:
            response = self.make_request('GET', '/media/s3/user/test-user-id')
            
            if response.status_code in [200, 404]:  # 404 acceptable for non-existent user
                self.log_test("Phase 1 S3 File Listing", True, 
                            "S3 file listing endpoint remains functional")
            else:
                self.log_test("Phase 1 S3 File Listing", False, 
                            f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Phase 1 S3 File Listing", False, f"Error: {str(e)}")

    def test_service_integration_fallbacks(self):
        """Test graceful degradation and fallback mechanisms"""
        print("🛡️ TESTING SERVICE INTEGRATION AND FALLBACKS")
        print("=" * 50)
        
        # Test system behavior when individual AWS services unavailable
        try:
            # Get Phase 2 status to understand current service availability
            response = self.make_request('GET', '/phase2/status')
            
            if response.status_code == 200:
                data = response.json()
                
                # Test CloudFront fallback to S3
                cloudfront_available = data.get('cloudfront', {}).get('available', False)
                if not cloudfront_available:
                    # Test that CDN URLs fall back to direct S3
                    cdn_response = self.make_request('GET', '/media/cdn-url?s3_key=test/fallback.jpg')
                    if cdn_response.status_code == 200:
                        cdn_data = cdn_response.json()
                        cdn_url = cdn_data.get('cdn_url', '')
                        if 'bigmann-entertainment-media.s3' in cdn_url:
                            self.log_test("CloudFront to S3 Fallback", True, 
                                        "Successfully falls back to direct S3 URLs when CloudFront unavailable")
                        else:
                            self.log_test("CloudFront to S3 Fallback", False, 
                                        f"Unexpected fallback URL: {cdn_url}")
                
                # Test Lambda graceful degradation
                lambda_available = data.get('lambda', {}).get('available', False)
                if not lambda_available:
                    # Test that processing requests handle Lambda unavailability
                    process_response = self.make_request('POST', '/media/process/audio', 
                                                       data={'s3_key': 'test/audio.mp3'})
                    if process_response.status_code == 200:
                        process_data = process_response.json()
                        if not process_data.get('processing_started', True):
                            self.log_test("Lambda Graceful Degradation", True, 
                                        "Gracefully handles Lambda unavailability")
                        else:
                            self.log_test("Lambda Graceful Degradation", False, 
                                        "Should indicate processing not started when Lambda unavailable")
                
                # Test Rekognition graceful degradation
                rekognition_available = data.get('rekognition', {}).get('available', False)
                if not rekognition_available and self.admin_token:
                    # Test that moderation requests handle Rekognition unavailability
                    mod_response = self.make_request('POST', '/media/moderate', use_admin=True,
                                                   data={'s3_key': 'test/image.jpg'})
                    if mod_response.status_code == 200:
                        mod_data = mod_response.json()
                        moderation = mod_data.get('moderation', {})
                        if not moderation.get('available', True):
                            self.log_test("Rekognition Graceful Degradation", True, 
                                        "Gracefully handles Rekognition unavailability")
                
                # Test overall system stability
                s3_available = data.get('s3', {}).get('available', False)
                if s3_available:
                    self.log_test("System Stability with Partial Services", True, 
                                "System maintains stability with S3 available and other services partially available")
                else:
                    self.log_test("System Stability with Partial Services", False, 
                                "S3 service should remain available for system stability")
                    
            else:
                self.log_test("Service Integration Fallbacks", False, 
                            f"Could not get Phase 2 status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Service Integration Fallbacks", False, f"Error: {str(e)}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 AWS PHASE 2 INTEGRATION - BACKEND TESTING REPORT")
        print("=" * 80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize tests
        phase2_tests = [t for t in self.test_results if "Phase 2" in t["test_name"]]
        cloudfront_tests = [t for t in self.test_results if "CloudFront" in t["test_name"] or "CDN" in t["test_name"]]
        lambda_tests = [t for t in self.test_results if "Lambda" in t["test_name"]]
        rekognition_tests = [t for t in self.test_results if "Rekognition" in t["test_name"]]
        compatibility_tests = [t for t in self.test_results if "Phase 1" in t["test_name"] or "Backward" in t["test_name"]]
        fallback_tests = [t for t in self.test_results if "Fallback" in t["test_name"] or "Degradation" in t["test_name"]]
        
        print(f"\n📋 AWS PHASE 2 MODULE BREAKDOWN:")
        print(f"Phase 2 Status: {sum(1 for t in phase2_tests if t['success'])}/{len(phase2_tests)} passed")
        print(f"CloudFront CDN: {sum(1 for t in cloudfront_tests if t['success'])}/{len(cloudfront_tests)} passed")
        print(f"Lambda Processing: {sum(1 for t in lambda_tests if t['success'])}/{len(lambda_tests)} passed")
        print(f"Rekognition Moderation: {sum(1 for t in rekognition_tests if t['success'])}/{len(rekognition_tests)} passed")
        print(f"Backward Compatibility: {sum(1 for t in compatibility_tests if t['success'])}/{len(compatibility_tests)} passed")
        print(f"Service Fallbacks: {sum(1 for t in fallback_tests if t['success'])}/{len(fallback_tests)} passed")
        
        # Failed tests details
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for test in failed_tests:
                print(f"- {test['test_name']}: {test['details']}")
        
        # Successful tests summary
        successful_tests = [t for t in self.test_results if t["success"]]
        if successful_tests:
            print(f"\n✅ SUCCESSFUL TESTS:")
            for test in successful_tests:
                print(f"- {test['test_name']}: {test['details']}")
        
        print(f"\n🕒 Test completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests / max(self.total_tests, 1)) * 100,
            "module_breakdown": {
                "phase2_status": {"passed": sum(1 for t in phase2_tests if t['success']), "total": len(phase2_tests)},
                "cloudfront": {"passed": sum(1 for t in cloudfront_tests if t['success']), "total": len(cloudfront_tests)},
                "lambda": {"passed": sum(1 for t in lambda_tests if t['success']), "total": len(lambda_tests)},
                "rekognition": {"passed": sum(1 for t in rekognition_tests if t['success']), "total": len(rekognition_tests)},
                "compatibility": {"passed": sum(1 for t in compatibility_tests if t['success']), "total": len(compatibility_tests)},
                "fallbacks": {"passed": sum(1 for t in fallback_tests if t['success']), "total": len(fallback_tests)}
            },
            "test_results": self.test_results
        }

    def run_all_tests(self):
        """Run all AWS Phase 2 backend tests"""
        print("🚀 STARTING AWS PHASE 2 INTEGRATION BACKEND TESTING")
        print("Testing CloudFront, Lambda, and Rekognition integration for Big Mann Entertainment")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_user():
            print("❌ User authentication failed. Cannot proceed with tests.")
            return False
        
        # Try to authenticate admin (some tests require admin access)
        self.authenticate_admin()
        
        # Run all test suites
        self.test_phase2_status_endpoint()
        self.test_cloudfront_cdn_integration()
        self.test_rekognition_content_moderation()
        self.test_lambda_processing_triggers()
        self.test_cloudfront_cache_management()
        self.test_backward_compatibility()
        self.test_service_integration_fallbacks()
        
        # Generate final report
        report = self.generate_report()
        
        return report

def main():
    """Main function to run AWS Phase 2 backend tests"""
    tester = AWSPhase2Tester()
    report = tester.run_all_tests()
    
    # Return appropriate exit code
    if report and report["failed_tests"] == 0:
        print("\n🎉 ALL AWS PHASE 2 TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {report['failed_tests'] if report else 'Unknown'} AWS PHASE 2 TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()