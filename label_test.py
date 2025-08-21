#!/usr/bin/env python3
"""
Label Management System Testing for Big Mann Entertainment
Tests the specific endpoints mentioned in the review request after routing fixes.
"""

import requests
import json
import os
from datetime import datetime, date

# Configuration
BASE_URL = "https://bme-media-system.preview.emergentagent.com/api"
TEST_USER_EMAIL = "owner@bigmannentertainment.com"
TEST_USER_PASSWORD = "OwnerBigMann2025!"

class LabelTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_artist_id = None
        self.test_demo_id = None
        
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
    
    def test_authentication(self) -> bool:
        """Test user authentication"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    print("✅ Authentication successful")
                    return True
                else:
                    print("❌ Authentication failed - no access token in response")
                    return False
            else:
                print(f"❌ Authentication failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication failed - Exception: {str(e)}")
            return False
    
    def test_demo_submission_public(self) -> bool:
        """Test POST /api/label/ar/demos (public endpoint - no auth required)"""
        try:
            demo_data = {
                "artist_name": "Demo Artist Test",
                "contact_email": "demoartist@example.com",
                "genre": "hip-hop",
                "submission_type": "demo",
                "audio_files": [
                    {
                        "title": "Demo Track 1",
                        "url": "/uploads/demo_track_1.mp3",
                        "duration": "3:45"
                    }
                ],
                "bio": "Aspiring artist looking to get signed to Big Mann Entertainment"
            }
            
            # Test without authentication (public endpoint)
            temp_token = self.auth_token
            self.auth_token = None  # Remove auth for public endpoint test
            
            response = self.make_request('POST', '/label/ar/demos', json=demo_data)
            
            # Restore auth token
            self.auth_token = temp_token
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success'] and 'submission_id' in data:
                    self.test_demo_id = data['submission_id']
                    print(f"✅ Demo submission successful (public endpoint): {data.get('submission_id')}")
                    return True
                else:
                    print(f"❌ Demo submission failed - Invalid response format: {data}")
                    return False
            else:
                print(f"❌ Demo submission failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Demo submission failed - Exception: {str(e)}")
            return False
    
    def test_create_artist(self) -> bool:
        """Test POST /api/label/artists (requires auth)"""
        try:
            if not self.auth_token:
                print("❌ Create artist failed - No auth token available")
                return False
            
            artist_data = {
                "stage_name": "Test Artist Label",
                "real_name": "John Test Artist",
                "email": "testartist@bigmannentertainment.com",
                "phone": "+1-555-0123",
                "genres": ["hip-hop", "r&b"],
                "bio": "A talented artist signed to Big Mann Entertainment for testing purposes.",
                "social_media": {
                    "instagram": "@testartist",
                    "twitter": "@testartist",
                    "tiktok": "@testartist"
                }
            }
            
            response = self.make_request('POST', '/label/artists', json=artist_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success'] and 'artist_id' in data:
                    self.test_artist_id = data['artist_id']
                    print(f"✅ Artist creation successful: {data.get('artist_id')}")
                    return True
                else:
                    print(f"❌ Artist creation failed - Invalid response format: {data}")
                    return False
            else:
                print(f"❌ Artist creation failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Artist creation failed - Exception: {str(e)}")
            return False
    
    def test_get_artist_roster(self) -> bool:
        """Test GET /api/label/artists (requires auth)"""
        try:
            if not self.auth_token:
                print("❌ Get artist roster failed - No auth token available")
                return False
            
            response = self.make_request('GET', '/label/artists')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Artist roster retrieval successful: {len(data)} artists found")
                    return True
                else:
                    print(f"❌ Artist roster failed - Invalid response format, expected list")
                    return False
            else:
                print(f"❌ Artist roster failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Artist roster failed - Exception: {str(e)}")
            return False
    
    def test_get_demo_submissions(self) -> bool:
        """Test GET /api/label/ar/demos (requires auth)"""
        try:
            if not self.auth_token:
                print("❌ Get demo submissions failed - No auth token available")
                return False
            
            response = self.make_request('GET', '/label/ar/demos')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Demo submissions retrieval successful: {len(data)} demos found")
                    return True
                else:
                    print(f"❌ Demo submissions failed - Invalid response format, expected list")
                    return False
            else:
                print(f"❌ Demo submissions failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Demo submissions failed - Exception: {str(e)}")
            return False
    
    def test_industry_trends(self) -> bool:
        """Test GET /api/label/ar/industry-trends (requires auth)"""
        try:
            if not self.auth_token:
                print("❌ Industry trends failed - No auth token available")
                return False
            
            response = self.make_request('GET', '/label/ar/industry-trends')
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['trending_genres', 'popular_artists', 'playlist_trends', 'market_insights']
                
                if all(field in data for field in required_fields):
                    print(f"✅ Industry trends retrieval successful: {len(data.get('trending_genres', []))} trending genres")
                    return True
                else:
                    print(f"❌ Industry trends failed - Missing required fields in response")
                    return False
            else:
                print(f"❌ Industry trends failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Industry trends failed - Exception: {str(e)}")
            return False
    
    def test_industry_contacts(self) -> bool:
        """Test GET /api/label/ar/industry-contacts with query 'radio' (requires auth)"""
        try:
            if not self.auth_token:
                print("❌ Industry contacts failed - No auth token available")
                return False
            
            response = self.make_request('GET', '/label/ar/industry-contacts?query=radio&category=radio')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Industry contacts search successful: {len(data)} radio contacts found")
                    return True
                else:
                    print(f"❌ Industry contacts failed - Invalid response format, expected list")
                    return False
            else:
                print(f"❌ Industry contacts failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Industry contacts failed - Exception: {str(e)}")
            return False
    
    def test_label_dashboard(self) -> bool:
        """Test GET /api/label/dashboard (requires auth)"""
        try:
            if not self.auth_token:
                print("❌ Label dashboard failed - No auth token available")
                return False
            
            response = self.make_request('GET', '/label/dashboard')
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_artists', 'active_projects', 'total_revenue', 'revenue_breakdown']
                
                if all(field in data for field in required_fields):
                    print(f"✅ Label dashboard retrieval successful: {data.get('total_artists')} artists, {data.get('active_projects')} active projects")
                    return True
                else:
                    print(f"❌ Label dashboard failed - Missing required fields in response")
                    return False
            else:
                print(f"❌ Label dashboard failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Label dashboard failed - Exception: {str(e)}")
            return False
    
    def test_available_studios(self) -> bool:
        """Test GET /api/label/studios/available (requires auth)"""
        try:
            if not self.auth_token:
                print("❌ Available studios failed - No auth token available")
                return False
            
            response = self.make_request('GET', '/label/studios/available')
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Available studios retrieval successful: {len(data)} studios found")
                    return True
                else:
                    print(f"❌ Available studios failed - Invalid response format, expected list")
                    return False
            else:
                print(f"❌ Available studios failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Available studios failed - Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all label management tests"""
        print("🎵 TESTING BIG MANN ENTERTAINMENT COMMERCIAL LABEL MANAGEMENT SYSTEM")
        print("=" * 80)
        print("Testing key functionalities after routing issue fixes")
        print()
        
        # Test authentication first
        if not self.test_authentication():
            print("❌ Cannot proceed without authentication")
            return
        
        print()
        print("--- Testing Label Management Endpoints ---")
        
        # Test all endpoints mentioned in the review request
        tests = [
            ("Demo Submission (Public)", self.test_demo_submission_public),
            ("Create Artist", self.test_create_artist),
            ("Get Artist Roster", self.test_get_artist_roster),
            ("Get Demo Submissions", self.test_get_demo_submissions),
            ("Industry Trends", self.test_industry_trends),
            ("Industry Contacts (Radio)", self.test_industry_contacts),
            ("Label Dashboard", self.test_label_dashboard),
            ("Available Studios", self.test_available_studios),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\nTesting {test_name}...")
            if test_func():
                passed += 1
            else:
                failed += 1
        
        print()
        print("=" * 80)
        print("LABEL MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL LABEL MANAGEMENT ENDPOINTS WORKING CORRECTLY!")
        else:
            print(f"\n⚠️  {failed} endpoint(s) need attention")

if __name__ == "__main__":
    tester = LabelTester()
    tester.run_all_tests()