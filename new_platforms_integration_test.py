#!/usr/bin/env python3
"""
🎯 NEW PLATFORMS DISPLAY & INTEGRATION VERIFICATION TESTING
Big Mann Entertainment Platform - Backend Testing

Testing the 8 new platforms integration:
1. threads.com (Social Media)
2. tumblr.com (Social Media) 
3. theshaderoom.com (Social Media)
4. hollywoodunlocked.com (Social Media)
5. livemixtapes.com (Music Streaming)
6. mymixtapez.com (Music Streaming)
7. worldstarhiphop.com (Music Streaming)
8. snapchat_enhanced (Social Media)

Verification Points:
- Platform count increased from 106 to 114+
- All 8 new platforms present in response
- Proper categorization by type
- Complete platform metadata
- Organized response structure
- Authentication security
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Backend URL from environment
BACKEND_URL = "https://mediahub-dashboard.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class NewPlatformsIntegrationTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "platforms.tester@bigmannentertainment.com"
        self.test_user_password = "PlatformTester2025!"
        self.test_results = []
        
        # Expected new platforms
        self.expected_new_platforms = [
            "threads",
            "tumblr", 
            "theshaderoom",
            "hollywoodunlocked",
            "livemixtapes",
            "mymixtapez",
            "worldstarhiphop",
            "snapchat_enhanced"
        ]
        
        # Expected platform types
        self.expected_platform_types = {
            "threads": "social_media",
            "tumblr": "social_media",
            "theshaderoom": "social_media", 
            "hollywoodunlocked": "social_media",
            "livemixtapes": "music_streaming",
            "mymixtapez": "music_streaming",
            "worldstarhiphop": "music_streaming",
            "snapchat_enhanced": "social_media"
        }
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
            
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add auth header if available
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers, params=data) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                json_headers = headers or {}
                json_headers["Content-Type"] = "application/json"
                async with self.session.post(url, json=data, headers=json_headers) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
                    
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
            
    async def test_user_authentication(self):
        """Test user registration and authentication for platform testing"""
        print("\n🔐 TESTING USER AUTHENTICATION FOR PLATFORM ACCESS")
        
        # Test user registration
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": "Platform Integration Tester",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Platform Street",
            "city": "Integration City",
            "state_province": "CA",
            "postal_code": "90210",
            "country": "USA"
        }
        
        response = await self.make_request("POST", "/auth/register", registration_data)
        
        if response["status"] == 201:
            self.log_test("User Registration", "PASS", "New user registered successfully", response["data"])
            if "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
        elif response["status"] == 400 and "already registered" in str(response["data"]).lower():
            self.log_test("User Registration", "PASS", "User already exists, proceeding to login", response["data"])
        else:
            self.log_test("User Registration", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test user login if registration failed or user exists
        if not self.auth_token:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = await self.make_request("POST", "/auth/login", login_data)
            
            if response["status"] == 200 and "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
                self.log_test("User Login", "PASS", "Authentication successful", response["data"])
            else:
                self.log_test("User Login", "FAIL", f"Status: {response['status']}", response["data"])
                return False
                
        return True
        
    async def test_distribution_platforms_endpoint(self):
        """Test /api/distribution/platforms endpoint for new platforms integration"""
        print("\n🌐 TESTING DISTRIBUTION PLATFORMS ENDPOINT")
        
        response = await self.make_request("GET", "/distribution/platforms")
        
        if response["status"] == 200:
            platforms_data = response["data"]
            
            # Test 1: Platform Count Verification
            if "platforms" in platforms_data:
                platforms = platforms_data["platforms"]
                platform_count = len(platforms)
                
                if platform_count >= 114:
                    self.log_test("Platform Count Verification", "PASS", 
                                f"Platform count: {platform_count} (≥114 expected)", 
                                {"platform_count": platform_count})
                else:
                    self.log_test("Platform Count Verification", "FAIL", 
                                f"Platform count: {platform_count} (expected ≥114)", 
                                {"platform_count": platform_count})
            else:
                self.log_test("Platform Count Verification", "FAIL", 
                            "No 'platforms' key in response", platforms_data)
                return
                
            # Test 2: New Platform Presence Verification
            found_platforms = []
            missing_platforms = []
            
            # Convert platforms to dict for easier lookup
            platform_dict = {}
            if isinstance(platforms, list):
                for platform in platforms:
                    if isinstance(platform, dict) and "name" in platform:
                        # Use lowercase name for matching
                        platform_key = platform["name"].lower().replace(" ", "").replace(".", "")
                        platform_dict[platform_key] = platform
            elif isinstance(platforms, dict):
                platform_dict = platforms
                
            for expected_platform in self.expected_new_platforms:
                # Try multiple matching strategies
                found = False
                
                # Direct key match
                if expected_platform in platform_dict:
                    found_platforms.append(expected_platform)
                    found = True
                else:
                    # Try name-based matching
                    for key, platform_data in platform_dict.items():
                        if isinstance(platform_data, dict):
                            platform_name = platform_data.get("name", "").lower()
                            if expected_platform.replace("_", "") in platform_name.replace(" ", "").replace(".", ""):
                                found_platforms.append(expected_platform)
                                found = True
                                break
                
                if not found:
                    missing_platforms.append(expected_platform)
                    
            if len(found_platforms) == len(self.expected_new_platforms):
                self.log_test("New Platform Presence", "PASS", 
                            f"All 8 new platforms found: {found_platforms}", 
                            {"found_platforms": found_platforms})
            else:
                self.log_test("New Platform Presence", "FAIL", 
                            f"Found {len(found_platforms)}/8 platforms. Missing: {missing_platforms}", 
                            {"found_platforms": found_platforms, "missing_platforms": missing_platforms})
                            
            # Test 3: Platform Categorization Verification
            categorization_results = {}
            for platform_key in found_platforms:
                if platform_key in platform_dict:
                    platform_data = platform_dict[platform_key]
                    actual_type = platform_data.get("type", "unknown")
                    expected_type = self.expected_platform_types.get(platform_key, "unknown")
                    
                    categorization_results[platform_key] = {
                        "expected": expected_type,
                        "actual": actual_type,
                        "match": actual_type == expected_type
                    }
                    
            correct_categorizations = sum(1 for result in categorization_results.values() if result["match"])
            
            if correct_categorizations == len(found_platforms):
                self.log_test("Platform Categorization", "PASS", 
                            f"All {correct_categorizations} platforms correctly categorized", 
                            categorization_results)
            else:
                self.log_test("Platform Categorization", "FAIL", 
                            f"{correct_categorizations}/{len(found_platforms)} platforms correctly categorized", 
                            categorization_results)
                            
            # Test 4: Platform Data Structure Verification
            required_fields = ["name", "type", "description", "supported_formats", "max_file_size"]
            structure_results = {}
            
            for platform_key in found_platforms[:3]:  # Test first 3 found platforms
                if platform_key in platform_dict:
                    platform_data = platform_dict[platform_key]
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in platform_data:
                            missing_fields.append(field)
                            
                    structure_results[platform_key] = {
                        "has_all_fields": len(missing_fields) == 0,
                        "missing_fields": missing_fields
                    }
                    
            platforms_with_complete_structure = sum(1 for result in structure_results.values() 
                                                  if result["has_all_fields"])
            
            if platforms_with_complete_structure == len(structure_results):
                self.log_test("Platform Data Structure", "PASS", 
                            f"All tested platforms have complete data structure", 
                            structure_results)
            else:
                self.log_test("Platform Data Structure", "FAIL", 
                            f"{platforms_with_complete_structure}/{len(structure_results)} platforms have complete structure", 
                            structure_results)
                            
            # Test 5: API Response Format Verification
            expected_response_keys = ["platforms", "total_count"]
            response_format_check = {}
            
            for key in expected_response_keys:
                response_format_check[key] = key in platforms_data
                
            if all(response_format_check.values()):
                self.log_test("API Response Format", "PASS", 
                            "Response contains all expected keys", 
                            response_format_check)
            else:
                self.log_test("API Response Format", "FAIL", 
                            "Response missing expected keys", 
                            response_format_check)
                            
            # Test 6: Categories Organization
            if "categories" in platforms_data:
                categories = platforms_data["categories"]
                self.log_test("Categories Organization", "PASS", 
                            f"Categories provided: {list(categories.keys()) if isinstance(categories, dict) else 'List format'}", 
                            {"categories": categories})
            else:
                self.log_test("Categories Organization", "WARN", 
                            "No categories key in response (may be organized differently)")
                            
        else:
            self.log_test("Distribution Platforms Endpoint", "FAIL", 
                        f"Status: {response['status']}", response["data"])
            
    async def test_authentication_security(self):
        """Test that the endpoint is accessible without breaking existing authentication"""
        print("\n🔒 TESTING AUTHENTICATION SECURITY")
        
        # Test with valid authentication
        response = await self.make_request("GET", "/distribution/platforms")
        
        if response["status"] == 200:
            self.log_test("Authenticated Access", "PASS", 
                        "Endpoint accessible with authentication", 
                        {"status": response["status"]})
        else:
            self.log_test("Authenticated Access", "FAIL", 
                        f"Endpoint not accessible with authentication: {response['status']}", 
                        response["data"])
            
        # Test without authentication
        old_token = self.auth_token
        self.auth_token = None
        
        response = await self.make_request("GET", "/distribution/platforms")
        
        # Restore token
        self.auth_token = old_token
        
        if response["status"] in [200, 401, 403]:
            self.log_test("Authentication Security", "PASS", 
                        f"Proper authentication handling (status: {response['status']})", 
                        {"status": response["status"]})
        else:
            self.log_test("Authentication Security", "FAIL", 
                        f"Unexpected authentication behavior: {response['status']}", 
                        response["data"])
                        
    async def test_platform_merging_verification(self):
        """Test that platform merging from enhanced_distribution_platforms.py is working"""
        print("\n🔄 TESTING PLATFORM MERGING VERIFICATION")
        
        response = await self.make_request("GET", "/distribution/platforms")
        
        if response["status"] == 200:
            platforms_data = response["data"]
            platforms = platforms_data.get("platforms", {})
            
            # Check for both old and new platforms to verify merging
            old_platform_samples = ["spotify", "instagram", "youtube", "facebook"]
            new_platform_samples = self.expected_new_platforms
            
            old_found = 0
            new_found = 0
            
            platform_dict = {}
            if isinstance(platforms, list):
                for platform in platforms:
                    if isinstance(platform, dict) and "name" in platform:
                        platform_key = platform["name"].lower().replace(" ", "").replace(".", "")
                        platform_dict[platform_key] = platform
            elif isinstance(platforms, dict):
                platform_dict = platforms
                
            # Check old platforms
            for old_platform in old_platform_samples:
                if old_platform in platform_dict:
                    old_found += 1
                    
            # Check new platforms
            for new_platform in new_platform_samples:
                if new_platform in platform_dict:
                    new_found += 1
                    
            if old_found >= 3 and new_found >= 6:
                self.log_test("Platform Merging Verification", "PASS", 
                            f"Both old ({old_found}/4) and new ({new_found}/8) platforms present", 
                            {"old_platforms_found": old_found, "new_platforms_found": new_found})
            else:
                self.log_test("Platform Merging Verification", "FAIL", 
                            f"Merging issue - Old: {old_found}/4, New: {new_found}/8", 
                            {"old_platforms_found": old_found, "new_platforms_found": new_found})
        else:
            self.log_test("Platform Merging Verification", "FAIL", 
                        f"Cannot test merging - endpoint failed: {response['status']}", 
                        response["data"])
                        
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 NEW PLATFORMS DISPLAY & INTEGRATION VERIFICATION - TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        warning_tests = len([t for t in self.test_results if t["status"] == "WARN"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Warnings: {warning_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for test in self.test_results:
            status_emoji = "✅" if test["status"] == "PASS" else "❌" if test["status"] == "FAIL" else "⚠️"
            print(f"   {status_emoji} {test['test']}: {test['status']}")
            if test["details"]:
                print(f"      {test['details']}")
                
        print(f"\n📋 CRITICAL ISSUES FOUND:")
        critical_issues = [t for t in self.test_results if t["status"] == "FAIL"]
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No critical issues found!")
            
        print(f"\n🎉 NEW PLATFORMS INTEGRATION STATUS:")
        platform_tests = [
            "Platform Count Verification", "New Platform Presence", 
            "Platform Categorization", "Platform Data Structure",
            "API Response Format", "Platform Merging Verification"
        ]
        
        for test_name in platform_tests:
            matching_tests = [t for t in self.test_results if test_name in t["test"]]
            if matching_tests:
                status = matching_tests[0]["status"]
                status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"   {status_emoji} {test_name}: {status}")
                
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "success_rate": success_rate,
            "critical_issues": len(critical_issues)
        }
        
    async def run_comprehensive_tests(self):
        """Run all comprehensive tests for new platforms integration"""
        print("🚀 STARTING NEW PLATFORMS DISPLAY & INTEGRATION VERIFICATION TESTING")
        print("Testing 8 New Platforms Integration for Big Mann Entertainment")
        print("="*80)
        
        try:
            await self.setup_session()
            
            # Authentication
            auth_success = await self.test_user_authentication()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with platform tests")
                return
                
            # Core platform integration tests
            await self.test_distribution_platforms_endpoint()
            await self.test_authentication_security()
            await self.test_platform_merging_verification()
            
            # Generate final summary
            summary = self.generate_summary()
            
            return summary
            
        except Exception as e:
            print(f"❌ Critical error during testing: {str(e)}")
            self.log_test("Critical Error", "FAIL", str(e))
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = NewPlatformsIntegrationTester()
    
    print("🎵 BIG MANN ENTERTAINMENT PLATFORM")
    print("New Platforms Display & Integration Verification Testing")
    print("Testing 8 New Platforms Integration")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    summary = await tester.run_comprehensive_tests()
    
    if summary:
        print(f"\n🏁 TESTING COMPLETED")
        print(f"Final Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] >= 90:
            print("🎉 EXCELLENT: New platforms integration is production-ready!")
        elif summary['success_rate'] >= 75:
            print("✅ GOOD: New platforms integration is functional with minor issues")
        else:
            print("⚠️ NEEDS ATTENTION: Critical issues require fixing")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())