#!/usr/bin/env python3
"""
pDOOH Integration Quick Verification Test
Big Mann Entertainment Platform - Quick pDOOH Verification

This script tests the 3 key pDOOH endpoints as requested:
1. GET /api/pdooh/platforms - Verify 8 platforms are available
2. POST /api/pdooh/campaigns - Create a test campaign
3. GET /api/pdooh/triggers/weather - Test weather triggers for NYC

Test Data:
- User: "test_user_verification"
- Location: NYC (40.7580, -73.9855)
- Simple campaign for testing

Success Criteria:
- All 3 endpoints respond with 200 status
- Platform data shows 8 pDOOH platforms
- Campaign creation successful
- Weather trigger returns valid data
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone

class PDOOHVerificationTester:
    def __init__(self):
        # Get backend URL from environment
        self.base_url = "http://localhost:8001"  # Default
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=')[1].strip()
                        break
        except FileNotFoundError:
            pass
        
        self.api_base = f"{self.base_url}/api/pdooh"
        self.test_user_id = "test_user_verification"
        self.test_campaign_id = None
        self.session = None
        
        # Test results tracking
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
        print(f"🔧 pDOOH QUICK VERIFICATION TEST")
        print(f"📡 Backend URL: {self.base_url}")
        print(f"🔗 pDOOH API Base: {self.api_base}")
        print(f"👤 Test User: {self.test_user_id}")
        print(f"📍 Test Location: NYC (40.7580, -73.9855)")
        print("=" * 60)

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        if not success and response_data:
            print(f"    📊 Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        print()

    async def make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{self.api_base}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
                    return response.status == 200, response_data, response.status
            elif method.upper() == "POST":
                async with self.session.post(url, params=params, json=data) as response:
                    response_data = await response.json()
                    return response.status == 200, response_data, response.status
            else:
                return False, {"error": f"Unsupported method: {method}"}, 400
                
        except Exception as e:
            return False, {"error": str(e)}, 500

    async def test_1_platforms_endpoint(self):
        """Test 1: GET /api/pdooh/platforms - Verify 8 platforms are available"""
        print("🏢 TEST 1: GET /api/pdooh/platforms")
        print("-" * 40)
        
        success, response, status = await self.make_request("GET", "/platforms")
        
        if success and response.get("success"):
            platforms = response.get("platforms", {})
            total_platforms = response.get("total_platforms", 0)
            
            # Check if we have 8 platforms as expected
            if total_platforms >= 8:
                platform_names = list(platforms.keys())[:8]  # Show first 8
                self.log_test_result(
                    "GET /api/pdooh/platforms - Platform Count Verification",
                    True,
                    f"✅ Found {total_platforms} pDOOH platforms (≥8 required). Platforms: {', '.join(platform_names)}"
                )
            else:
                self.log_test_result(
                    "GET /api/pdooh/platforms - Platform Count Verification",
                    False,
                    f"❌ Only found {total_platforms} platforms, expected ≥8"
                )
        else:
            self.log_test_result(
                "GET /api/pdooh/platforms - Platform Count Verification",
                False,
                f"❌ Failed to get platforms (Status: {status})",
                response
            )

    async def test_2_campaign_creation(self):
        """Test 2: POST /api/pdooh/campaigns - Create a test campaign"""
        print("🎯 TEST 2: POST /api/pdooh/campaigns")
        print("-" * 40)
        
        # Simple campaign data for testing
        campaign_data = {
            "name": "Test Verification Campaign",
            "description": "Simple test campaign for pDOOH verification",
            "campaign_type": "artist_promotion",
            "start_date": "2025-01-20T00:00:00Z",
            "end_date": "2025-02-20T00:00:00Z",
            "budget_total": 5000,
            "currency": "USD",
            "platforms": ["trade_desk", "vistar_media"],
            "geotargeting_rules": [
                {
                    "latitude": 40.7580,
                    "longitude": -73.9855,
                    "radius_km": 10,
                    "location_name": "New York City"
                }
            ],
            "primary_creative": {
                "name": "Test Creative",
                "format": "static_image",
                "file_url": "/assets/test_creative.jpg",
                "dimensions": {"width": 1920, "height": 1080}
            }
        }
        
        success, response, status = await self.make_request(
            "POST", "/campaigns", 
            params={"user_id": self.test_user_id}, 
            data=campaign_data
        )
        
        if success and response.get("success"):
            self.test_campaign_id = response.get("campaign_id")
            campaign_name = response.get("campaign", {}).get("name", "Unknown")
            self.log_test_result(
                "POST /api/pdooh/campaigns - Campaign Creation",
                True,
                f"✅ Campaign created successfully: '{campaign_name}' (ID: {self.test_campaign_id})"
            )
        else:
            self.log_test_result(
                "POST /api/pdooh/campaigns - Campaign Creation",
                False,
                f"❌ Failed to create campaign (Status: {status})",
                response
            )

    async def test_3_weather_triggers(self):
        """Test 3: GET /api/pdooh/triggers/weather - Test weather triggers for NYC"""
        print("🌤️ TEST 3: GET /api/pdooh/triggers/weather")
        print("-" * 40)
        
        success, response, status = await self.make_request(
            "GET", "/triggers/weather",
            params={
                "latitude": 40.7580,
                "longitude": -73.9855,
                "location_name": "New York City",
                "user_id": self.test_user_id
            }
        )
        
        if success and response.get("success"):
            weather_data = response.get("weather_data", {})
            condition = weather_data.get("condition", "unknown")
            temperature = weather_data.get("temperature", 0)
            humidity = weather_data.get("humidity", 0)
            
            self.log_test_result(
                "GET /api/pdooh/triggers/weather - Weather Data for NYC",
                True,
                f"✅ Weather data retrieved: {condition}, {temperature}°C, {humidity}% humidity"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/triggers/weather - Weather Data for NYC",
                False,
                f"❌ Failed to get weather triggers (Status: {status})",
                response
            )

    async def run_verification_tests(self):
        """Run the 3 key pDOOH verification tests"""
        print("🚀 STARTING pDOOH VERIFICATION TESTS")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Run the 3 key tests in sequence
            await self.test_1_platforms_endpoint()
            await self.test_2_campaign_creation()
            await self.test_3_weather_triggers()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR during testing: {e}")
            self.failed_tests += 1
        
        finally:
            await self.cleanup_session()
        
        # Print final results
        self.print_verification_results()

    def print_verification_results(self):
        """Print verification test results"""
        print("=" * 60)
        print("🔧 pDOOH VERIFICATION TEST RESULTS")
        print("=" * 60)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 VERIFICATION RESULTS:")
        print(f"   ✅ Passed: {self.passed_tests}/3")
        print(f"   ❌ Failed: {self.failed_tests}/3")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Check success criteria
        print("🎯 SUCCESS CRITERIA CHECK:")
        
        # Criteria 1: All 3 endpoints respond with 200 status
        all_200_status = all(result["success"] for result in self.test_results)
        print(f"   {'✅' if all_200_status else '❌'} All 3 endpoints respond with 200 status: {'YES' if all_200_status else 'NO'}")
        
        # Criteria 2: Platform data shows 8 pDOOH platforms
        platform_test = next((r for r in self.test_results if "platforms" in r["test"].lower()), None)
        platforms_ok = platform_test and platform_test["success"]
        print(f"   {'✅' if platforms_ok else '❌'} Platform data shows ≥8 pDOOH platforms: {'YES' if platforms_ok else 'NO'}")
        
        # Criteria 3: Campaign creation successful
        campaign_test = next((r for r in self.test_results if "campaign" in r["test"].lower()), None)
        campaign_ok = campaign_test and campaign_test["success"]
        print(f"   {'✅' if campaign_ok else '❌'} Campaign creation successful: {'YES' if campaign_ok else 'NO'}")
        
        # Criteria 4: Weather trigger returns valid data
        weather_test = next((r for r in self.test_results if "weather" in r["test"].lower()), None)
        weather_ok = weather_test and weather_test["success"]
        print(f"   {'✅' if weather_ok else '❌'} Weather trigger returns valid data: {'YES' if weather_ok else 'NO'}")
        
        print()
        
        # Print failed tests details if any
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['test']}")
                if result['details']:
                    print(f"     📝 {result['details']}")
        
        print()
        
        # Final verification assessment
        if success_rate == 100:
            print("🎉 VERIFICATION SUCCESSFUL: All pDOOH integration tests passed!")
            print("✅ pDOOH integration is working correctly and ready for use.")
        elif success_rate >= 67:  # 2/3 tests passed
            print("⚠️ PARTIAL SUCCESS: Most pDOOH integration tests passed.")
            print("🔧 Minor issues detected that may need attention.")
        else:
            print("❌ VERIFICATION FAILED: Major pDOOH integration issues detected.")
            print("🚨 Immediate attention required to fix pDOOH integration.")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    tester = PDOOHVerificationTester()
    await tester.run_verification_tests()

if __name__ == "__main__":
    asyncio.run(main())