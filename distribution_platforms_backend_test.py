#!/usr/bin/env python3
"""
Distribution Platforms Backend Testing
Testing the newly integrated 8 distribution platforms to verify they are working correctly in the backend.

TESTING FOCUS:
1. Distribution Platforms Endpoint: Test GET /api/distribution/platforms
2. Platform Count Verification: Confirm total platform count increased from 106 to 114 platforms  
3. New Platform Presence: Verify 8 specific new platforms are in the response
4. Platform Categorization: Verify proper categorization by type
5. Platform Metadata: Check complete data structure for each platform

Expected 8 New Platforms:
- threads (Meta's text-based conversation platform)
- tumblr (Microblogging platform) 
- theshaderoom (Entertainment news platform)
- hollywoodunlocked (Celebrity news platform)
- snapchat_enhanced (Enhanced multimedia messaging)
- livemixtapes (Hip-hop mixtape hosting)
- mymixtapez (Premier mixtape platform) 
- worldstarhiphop (Leading hip-hop content platform)
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://record-net.preview.emergentagent.com/api"

class DistributionPlatformsTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Expected 8 new platforms
        self.expected_new_platforms = {
            "threads": {
                "name": "Threads",
                "type": "social_media",
                "description_contains": "Meta's text-based conversation platform"
            },
            "tumblr": {
                "name": "Tumblr", 
                "type": "social_media",
                "description_contains": "Microblogging platform"
            },
            "theshaderoom": {
                "name": "The Shade Room",
                "type": "social_media", 
                "description_contains": "Entertainment"
            },
            "hollywoodunlocked": {
                "name": "Hollywood Unlocked",
                "type": "social_media",
                "description_contains": "Celebrity news"
            },
            "snapchat_enhanced": {
                "name": "Snapchat Enhanced",
                "type": "social_media",
                "description_contains": "Enhanced multimedia messaging"
            },
            "livemixtapes": {
                "name": "LiveMixtapes.com",
                "type": "music_streaming",
                "description_contains": "Hip-hop mixtape hosting"
            },
            "mymixtapez": {
                "name": "MyMixtapez.com", 
                "type": "music_streaming",
                "description_contains": "Premier mixtape platform"
            },
            "worldstarhiphop": {
                "name": "WorldStar Hip Hop",
                "type": "music_streaming",
                "description_contains": "Leading hip-hop content"
            }
        }

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)

    async def test_distribution_platforms_endpoint(self):
        """Test GET /api/distribution/platforms endpoint accessibility"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/distribution/platforms") as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extract platforms from the response structure
                        platforms_data = data.get("platforms", {})
                        total_count = data.get("total_count", len(platforms_data))
                        self.log_test("Distribution Platforms Endpoint Access", True, 
                                    f"Status: {response.status}, Total platforms: {total_count}")
                        return platforms_data
                    else:
                        self.log_test("Distribution Platforms Endpoint Access", False, 
                                    f"Status: {response.status}")
                        return None
        except Exception as e:
            self.log_test("Distribution Platforms Endpoint Access", False, f"Error: {str(e)}")
            return None

    async def test_platform_count_verification(self, platforms_data: Dict):
        """Test that platform count increased from 106 to 114 platforms"""
        if not platforms_data:
            self.log_test("Platform Count Verification", False, "No platforms data available")
            return
        
        try:
            total_platforms = len(platforms_data)
            expected_min_count = 114
            
            if total_platforms >= expected_min_count:
                self.log_test("Platform Count Verification", True, 
                            f"Total platforms: {total_platforms} (meets {expected_min_count}+ requirement)")
            else:
                self.log_test("Platform Count Verification", False, 
                            f"Total platforms: {total_platforms} (expected {expected_min_count}+)")
                
        except Exception as e:
            self.log_test("Platform Count Verification", False, f"Error: {str(e)}")

    async def test_new_platform_presence(self, platforms_data: Dict):
        """Test that all 8 new platforms are present in the response"""
        if not platforms_data:
            self.log_test("New Platform Presence Check", False, "No platforms data available")
            return
        
        found_platforms = []
        missing_platforms = []
        
        for platform_id, expected_info in self.expected_new_platforms.items():
            if platform_id in platforms_data:
                platform_data = platforms_data[platform_id]
                found_platforms.append(platform_id)
                
                # Verify platform details
                name_match = platform_data.get("name") == expected_info["name"]
                type_match = platform_data.get("type") == expected_info["type"]
                description_match = expected_info["description_contains"].lower() in platform_data.get("description", "").lower()
                
                details = f"Name: {name_match}, Type: {type_match}, Description: {description_match}"
                self.log_test(f"Platform {platform_id} Details Verification", 
                            name_match and type_match and description_match, details)
            else:
                missing_platforms.append(platform_id)
        
        # Overall presence test
        all_found = len(missing_platforms) == 0
        details = f"Found: {len(found_platforms)}/8, Missing: {missing_platforms}" if missing_platforms else f"All 8 platforms found: {found_platforms}"
        self.log_test("New Platform Presence Check", all_found, details)

    async def test_platform_categorization(self, platforms_data: Dict):
        """Test proper categorization by type (social_media vs music_streaming)"""
        if not platforms_data:
            self.log_test("Platform Categorization Check", False, "No platforms data available")
            return
        
        try:
            # Count platforms by type
            type_counts = {}
            social_media_platforms = []
            music_streaming_platforms = []
            
            for platform_id, platform_data in platforms_data.items():
                platform_type = platform_data.get("type", "unknown")
                type_counts[platform_type] = type_counts.get(platform_type, 0) + 1
                
                if platform_type == "social_media":
                    social_media_platforms.append(platform_id)
                elif platform_type == "music_streaming":
                    music_streaming_platforms.append(platform_id)
            
            # Check new platforms categorization
            new_social_media = ["threads", "tumblr", "theshaderoom", "hollywoodunlocked", "snapchat_enhanced"]
            new_music_streaming = ["livemixtapes", "mymixtapez", "worldstarhiphop"]
            
            social_media_correct = all(platform in social_media_platforms for platform in new_social_media if platform in platforms_data)
            music_streaming_correct = all(platform in music_streaming_platforms for platform in new_music_streaming if platform in platforms_data)
            
            details = f"Social Media: {type_counts.get('social_media', 0)}, Music Streaming: {type_counts.get('music_streaming', 0)}"
            self.log_test("Platform Categorization Check", 
                        social_media_correct and music_streaming_correct, details)
            
        except Exception as e:
            self.log_test("Platform Categorization Check", False, f"Error: {str(e)}")

    async def test_platform_metadata_structure(self, platforms_data: Dict):
        """Test that each platform has complete data structure"""
        if not platforms_data:
            self.log_test("Platform Metadata Structure Check", False, "No platforms data available")
            return
        
        required_fields = ["name", "type", "description", "supported_formats", "max_file_size", "api_endpoint", "credentials_required"]
        
        for platform_id in self.expected_new_platforms.keys():
            if platform_id in platforms_data:
                platform_data = platforms_data[platform_id]
                missing_fields = []
                
                for field in required_fields:
                    if field not in platform_data:
                        missing_fields.append(field)
                
                has_complete_structure = len(missing_fields) == 0
                details = f"Missing fields: {missing_fields}" if missing_fields else "All required fields present"
                self.log_test(f"Platform {platform_id} Metadata Structure", 
                            has_complete_structure, details)

    async def test_platform_specific_configurations(self, platforms_data: Dict):
        """Test platform-specific configurations and settings"""
        if not platforms_data:
            self.log_test("Platform Specific Configurations", False, "No platforms data available")
            return
        
        # Test specific platform configurations
        test_cases = [
            {
                "platform": "threads",
                "checks": {
                    "api_endpoint": "https://graph.threads.net/v1",
                    "max_file_size": 100 * 1024 * 1024,  # 100MB
                    "supported_formats": ["image", "video", "audio"]
                }
            },
            {
                "platform": "livemixtapes", 
                "checks": {
                    "api_endpoint": "https://api.livemixtapes.com/v1",
                    "max_file_size": 150 * 1024 * 1024,  # 150MB
                    "supported_formats": ["audio"]
                }
            },
            {
                "platform": "worldstarhiphop",
                "checks": {
                    "api_endpoint": "https://api.worldstarhiphop.com/v1", 
                    "max_file_size": 500 * 1024 * 1024,  # 500MB
                    "supported_formats": ["audio", "video"]
                }
            }
        ]
        
        for test_case in test_cases:
            platform_id = test_case["platform"]
            if platform_id in platforms_data:
                platform_data = platforms_data[platform_id]
                all_checks_passed = True
                failed_checks = []
                
                for check_field, expected_value in test_case["checks"].items():
                    actual_value = platform_data.get(check_field)
                    if actual_value != expected_value:
                        all_checks_passed = False
                        failed_checks.append(f"{check_field}: expected {expected_value}, got {actual_value}")
                
                details = "All configuration checks passed" if all_checks_passed else f"Failed: {failed_checks}"
                self.log_test(f"Platform {platform_id} Configuration", all_checks_passed, details)

    async def run_comprehensive_test(self):
        """Run all distribution platform tests"""
        print("🎯 DISTRIBUTION PLATFORMS INTEGRATION TESTING STARTED")
        print("=" * 80)
        
        # Test 1: Distribution Platforms Endpoint Access
        platforms_data = await self.test_distribution_platforms_endpoint()
        
        if platforms_data:
            # Test 2: Platform Count Verification
            await self.test_platform_count_verification(platforms_data)
            
            # Test 3: New Platform Presence
            await self.test_new_platform_presence(platforms_data)
            
            # Test 4: Platform Categorization
            await self.test_platform_categorization(platforms_data)
            
            # Test 5: Platform Metadata Structure
            await self.test_platform_metadata_structure(platforms_data)
            
            # Test 6: Platform Specific Configurations
            await self.test_platform_specific_configurations(platforms_data)
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 DISTRIBUTION PLATFORMS TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n✅ EXCELLENT: Distribution platforms integration is working excellently ({success_rate:.1f}% success rate)")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Distribution platforms integration is working well ({success_rate:.1f}% success rate)")
        elif success_rate >= 50:
            print(f"\n⚠️ PARTIAL: Distribution platforms integration has some issues ({success_rate:.1f}% success rate)")
        else:
            print(f"\n❌ CRITICAL: Distribution platforms integration has major issues ({success_rate:.1f}% success rate)")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": success_rate,
            "platforms_data": platforms_data
        }

async def main():
    """Main test execution"""
    tester = DistributionPlatformsTest()
    results = await tester.run_comprehensive_test()
    
    # Return results for further processing
    return results

if __name__ == "__main__":
    # Run the test
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results["success_rate"] >= 75:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure