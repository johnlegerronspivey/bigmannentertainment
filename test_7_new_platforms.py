#!/usr/bin/env python3
"""
Focused Testing for 7 New Platform Integrations
Tests the newly added modeling agencies and entertainment media outlets
"""

import requests
import json
import os
from typing import Dict, Any

# Configuration
BASE_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "platform.test@bigmannentertainment.com"
TEST_USER_PASSWORD = "PlatformTest2025!"

class NewPlatformTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.results = {
            "new_7_platforms_integration": {"passed": 0, "failed": 0, "details": []},
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
    
    def login(self) -> bool:
        """Login to get auth token"""
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
                    print("✅ Successfully logged in")
                    return True
            
            # Try registration if login fails
            from datetime import datetime, timedelta
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "Platform Test User",
                "business_name": "Big Mann Entertainment",
                "date_of_birth": (datetime.utcnow() - timedelta(days=25*365)).isoformat(),
                "address_line1": "1314 Lincoln Heights Street",
                "city": "Alexander City",
                "state_province": "Alabama",
                "postal_code": "35010",
                "country": "United States"
            }
            
            reg_response = self.make_request('POST', '/auth/register', json=user_data)
            if reg_response.status_code in [200, 201]:
                reg_data = reg_response.json()
                if 'access_token' in reg_data:
                    self.auth_token = reg_data['access_token']
                    print("✅ Successfully registered and logged in")
                    return True
            
            print("❌ Failed to login or register")
            return False
                
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def test_7_new_platforms_integration(self) -> bool:
        """Test the 7 new platform integrations (4 modeling agencies + 3 entertainment media outlets)"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                
                # Expected 7 new platforms
                expected_new_platforms = {
                    # Modeling Agencies (4)
                    'imgmodels': 'IMG Models',
                    'elitemodelmanagement': 'Elite Model Management', 
                    'lamodels': 'LA Models',
                    'stormmanagement': 'Storm Management LA',
                    # Entertainment Media Outlets (3)
                    'thesource': 'The Source',
                    'billboard': 'Billboard',
                    'tmz': 'TMZ'
                }
                
                missing_platforms = []
                found_platforms = []
                
                for platform_key, platform_name in expected_new_platforms.items():
                    if platform_key in platforms:
                        platform_config = platforms[platform_key]
                        if platform_config.get('name') == platform_name:
                            found_platforms.append(f"{platform_key} ({platform_name})")
                        else:
                            missing_platforms.append(f"{platform_key} (name mismatch: expected '{platform_name}', got '{platform_config.get('name')}')")
                    else:
                        missing_platforms.append(f"{platform_key} ({platform_name})")
                
                if not missing_platforms:
                    self.log_result("new_7_platforms_integration", "7 New Platforms Integration", True, 
                                  f"Successfully found all 7 new platforms: {', '.join(found_platforms)}")
                    return True
                else:
                    self.log_result("new_7_platforms_integration", "7 New Platforms Integration", False, 
                                  f"Missing platforms: {', '.join(missing_platforms)}. Found: {', '.join(found_platforms)}")
                    return False
            else:
                self.log_result("new_7_platforms_integration", "7 New Platforms Integration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("new_7_platforms_integration", "7 New Platforms Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_platform_count_83_to_90_verification(self) -> bool:
        """Test that platform count increased from 83 to 90 platforms with the 7 new additions"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                
                total_platforms = len(platforms)
                expected_minimum = 90  # Should be at least 90 with the new additions
                
                if total_platforms >= expected_minimum:
                    self.log_result("new_7_platforms_integration", "Platform Count 83 to 90 Verification", True, 
                                  f"Platform count successfully increased to {total_platforms} (expected minimum: {expected_minimum})")
                    return True
                else:
                    self.log_result("new_7_platforms_integration", "Platform Count 83 to 90 Verification", False, 
                                  f"Platform count insufficient: {total_platforms} (expected minimum: {expected_minimum})")
                    return False
            else:
                self.log_result("new_7_platforms_integration", "Platform Count 83 to 90 Verification", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("new_7_platforms_integration", "Platform Count 83 to 90 Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_modeling_agencies_configuration(self) -> bool:
        """Test configuration of the 4 new modeling agency platforms"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                
                modeling_agencies = ['imgmodels', 'elitemodelmanagement', 'lamodels', 'stormmanagement']
                configured_correctly = []
                configuration_issues = []
                
                for agency in modeling_agencies:
                    platform = platforms.get(agency, {})
                    if not platform:
                        configuration_issues.append(f"{agency}: Platform not found")
                        continue
                    
                    # Check required fields
                    required_fields = ['type', 'name', 'api_endpoint', 'max_file_size', 'target_demographics', 'content_guidelines']
                    missing_fields = [field for field in required_fields if field not in platform or not platform[field]]
                    
                    if missing_fields:
                        configuration_issues.append(f"{agency}: Missing fields {missing_fields}")
                    elif platform.get('type') != 'social_media':
                        configuration_issues.append(f"{agency}: Wrong type {platform.get('type')}")
                    else:
                        configured_correctly.append(agency)
                
                if not configuration_issues:
                    self.log_result("new_7_platforms_integration", "Modeling Agencies Configuration", True, 
                                  f"All 4 modeling agency platforms configured correctly: {', '.join(configured_correctly)}")
                    return True
                else:
                    self.log_result("new_7_platforms_integration", "Modeling Agencies Configuration", False, 
                                  f"Configuration issues: {'; '.join(configuration_issues)}")
                    return False
            else:
                self.log_result("new_7_platforms_integration", "Modeling Agencies Configuration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("new_7_platforms_integration", "Modeling Agencies Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_entertainment_media_configuration(self) -> bool:
        """Test configuration of the 3 new entertainment media outlet platforms"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                
                media_outlets = ['thesource', 'billboard', 'tmz']
                configured_correctly = []
                configuration_issues = []
                
                for outlet in media_outlets:
                    platform = platforms.get(outlet, {})
                    if not platform:
                        configuration_issues.append(f"{outlet}: Platform not found")
                        continue
                    
                    # Check required fields
                    required_fields = ['type', 'name', 'api_endpoint', 'max_file_size', 'target_demographics', 'content_guidelines']
                    missing_fields = [field for field in required_fields if field not in platform or not platform[field]]
                    
                    if missing_fields:
                        configuration_issues.append(f"{outlet}: Missing fields {missing_fields}")
                    elif platform.get('type') != 'social_media':
                        configuration_issues.append(f"{outlet}: Wrong type {platform.get('type')}")
                    else:
                        configured_correctly.append(outlet)
                
                if not configuration_issues:
                    self.log_result("new_7_platforms_integration", "Entertainment Media Configuration", True, 
                                  f"All 3 entertainment media platforms configured correctly: {', '.join(configured_correctly)}")
                    return True
                else:
                    self.log_result("new_7_platforms_integration", "Entertainment Media Configuration", False, 
                                  f"Configuration issues: {'; '.join(configuration_issues)}")
                    return False
            else:
                self.log_result("new_7_platforms_integration", "Entertainment Media Configuration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("new_7_platforms_integration", "Entertainment Media Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_platform_api_endpoints_structure(self) -> bool:
        """Test that all 7 new platforms have properly configured API endpoints"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                
                # Expected API endpoints for the 7 new platforms
                expected_endpoints = {
                    'imgmodels': 'https://api.imgmodels.com/v1',
                    'elitemodelmanagement': 'https://api.elitemodel.com/v1',
                    'lamodels': 'https://api.lamodels.com/v1',
                    'stormmanagement': 'https://api.stormmanagement-la.com/v1',
                    'thesource': 'https://api.thesource.com/v1',
                    'billboard': 'https://api.billboard.com/v1',
                    'tmz': 'https://api.tmz.com/v1'
                }
                
                incorrect_endpoints = []
                correct_endpoints = []
                
                for platform_key, expected_endpoint in expected_endpoints.items():
                    platform = platforms.get(platform_key, {})
                    actual_endpoint = platform.get('api_endpoint')
                    
                    if actual_endpoint == expected_endpoint:
                        correct_endpoints.append(platform_key)
                    else:
                        incorrect_endpoints.append(f"{platform_key} (expected: {expected_endpoint}, got: {actual_endpoint})")
                
                if not incorrect_endpoints:
                    self.log_result("new_7_platforms_integration", "Platform API Endpoints Structure", True, 
                                  f"All 7 new platforms have correctly configured API endpoints: {', '.join(correct_endpoints)}")
                    return True
                else:
                    self.log_result("new_7_platforms_integration", "Platform API Endpoints Structure", False, 
                                  f"Incorrect API endpoints: {', '.join(incorrect_endpoints)}")
                    return False
            else:
                self.log_result("new_7_platforms_integration", "Platform API Endpoints Structure", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("new_7_platforms_integration", "Platform API Endpoints Structure", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all 7 new platform integration tests"""
        print("\n" + "=" * 80)
        print("🎯 7 NEW PLATFORM INTEGRATION TESTING FOR BIG MANN ENTERTAINMENT")
        print("=" * 80)
        print("Testing 4 Modeling Agencies + 3 Entertainment Media Outlets")
        print("Expected platforms: IMG Models, Elite Model Management, LA Models, Storm Management LA")
        print("                   The Source, Billboard, TMZ")
        print("-" * 80)
        
        # Login first
        if not self.login():
            print("❌ Failed to authenticate - cannot run tests")
            return
        
        # Run tests
        print("\n🔍 Testing Platform Integration...")
        self.test_7_new_platforms_integration()
        
        print("\n📊 Testing Platform Count Increase...")
        self.test_platform_count_83_to_90_verification()
        
        print("\n👗 Testing Modeling Agencies Configuration...")
        self.test_modeling_agencies_configuration()
        
        print("\n📺 Testing Entertainment Media Configuration...")
        self.test_entertainment_media_configuration()
        
        print("\n🔗 Testing API Endpoints Structure...")
        self.test_platform_api_endpoints_structure()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
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
                print("  Details:")
                for detail in results["details"]:
                    print(f"    {detail}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        
        if total_failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! 7 new platforms successfully integrated.")
        else:
            print(f"\n⚠️  {total_failed} test(s) failed. Review issues above.")

if __name__ == "__main__":
    tester = NewPlatformTester()
    tester.run_all_tests()