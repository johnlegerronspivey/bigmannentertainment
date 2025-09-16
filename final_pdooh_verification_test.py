#!/usr/bin/env python3
"""
Final pDOOH Integration Verification Test
Big Mann Entertainment Platform - Final Verification Testing

This script performs the final verification tests as requested:
1. Campaign Creation with Optional Creative (without primary_creative)
2. Platform Integration (verify all 8 platforms are accessible)
3. Weather Triggers (test real-time trigger functionality for NYC)
4. Performance Analytics (test campaign performance endpoint)

Test User: test_user_final_verification
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import uuid

# Add the backend directory to the path
sys.path.append('/app/backend')

class FinalPDOOHVerificationTester:
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
        self.test_user_id = "test_user_final_verification"
        self.test_campaign_id = None
        self.session = None
        
        # Test results tracking
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
        print(f"🎯 Final pDOOH Integration Verification Tester")
        print(f"📡 Backend URL: {self.base_url}")
        print(f"🔗 pDOOH API Base: {self.api_base}")
        print(f"👤 Test User ID: {self.test_user_id}")
        print("=" * 80)

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
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

    async def make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{self.api_base}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            elif method.upper() == "POST":
                async with self.session.post(url, params=params, json=data) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, params=params, json=data) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            else:
                return False, {"error": f"Unsupported method: {method}"}, 400
                
        except Exception as e:
            return False, {"error": str(e)}, 500

    async def test_campaign_creation_without_creative(self):
        """Test 1: Campaign Creation with Optional Creative (without primary_creative)"""
        print("🎯 TEST 1: CAMPAIGN CREATION WITHOUT PRIMARY_CREATIVE")
        print("-" * 60)
        
        # Test data as specified in the review request
        campaign_data = {
            "name": "Final Verification Campaign",
            "campaign_type": "artist_promotion",
            "start_date": "2025-01-20T00:00:00Z",
            "end_date": "2025-02-20T00:00:00Z",
            "budget_total": 5000,
            "platforms": ["trade_desk", "vistar_media"]
            # Note: Intentionally NOT including primary_creative to test validation fix
        }
        
        success, response, status = await self.make_request(
            "POST", "/campaigns", 
            params={"user_id": self.test_user_id}, 
            data=campaign_data
        )
        
        if success and response.get("success"):
            self.test_campaign_id = response.get("campaign_id")
            self.log_test_result(
                "Campaign Creation WITHOUT primary_creative",
                True,
                f"✅ Campaign created successfully with ID: {self.test_campaign_id}. Validation fix working - primary_creative is now optional."
            )
        else:
            self.log_test_result(
                "Campaign Creation WITHOUT primary_creative",
                False,
                f"❌ Campaign creation failed (Status: {status}). This indicates validation issue still exists.",
                response
            )

    async def test_platform_integration(self):
        """Test 2: Platform Integration - Verify all 8 platforms are accessible"""
        print("🏢 TEST 2: PLATFORM INTEGRATION - ALL 8 pDOOH PLATFORMS")
        print("-" * 60)
        
        success, response, status = await self.make_request("GET", "/platforms")
        
        if success and response.get("success"):
            platforms = response.get("platforms", {})
            total_platforms = response.get("total_platforms", 0)
            
            # Expected 8 pDOOH platforms
            expected_platforms = [
                "trade_desk", "vistar_media", "hivestack", "broadsign", 
                "viooh", "displayce", "hawk", "locala"
            ]
            
            available_platforms = list(platforms.keys()) if isinstance(platforms, dict) else []
            
            # Check if all 8 platforms are available
            missing_platforms = [p for p in expected_platforms if p not in available_platforms]
            
            if len(available_platforms) >= 8 and not missing_platforms:
                self.log_test_result(
                    "All 8 pDOOH Platforms Accessible",
                    True,
                    f"✅ All {total_platforms} pDOOH platforms accessible. Expected platforms found: {', '.join(expected_platforms)}"
                )
            else:
                self.log_test_result(
                    "All 8 pDOOH Platforms Accessible",
                    False,
                    f"❌ Missing platforms: {missing_platforms}. Available: {len(available_platforms)}, Expected: 8+",
                    {"available_platforms": available_platforms, "missing": missing_platforms}
                )
        else:
            self.log_test_result(
                "All 8 pDOOH Platforms Accessible",
                False,
                f"❌ Failed to get platforms (Status: {status})",
                response
            )

    async def test_weather_triggers_nyc(self):
        """Test 3: Weather Triggers - Test real-time trigger functionality for NYC"""
        print("⚡ TEST 3: WEATHER TRIGGERS FOR NYC")
        print("-" * 60)
        
        # NYC coordinates as specified
        nyc_lat = 40.7580
        nyc_lng = -73.9855
        
        success, response, status = await self.make_request(
            "GET", "/triggers/weather",
            params={
                "latitude": nyc_lat,
                "longitude": nyc_lng,
                "location_name": "New York City",
                "user_id": self.test_user_id
            }
        )
        
        if success and response.get("success"):
            weather_data = response.get("weather_data", {})
            condition = weather_data.get("condition", "unknown")
            temperature = weather_data.get("temperature", 0)
            humidity = weather_data.get("humidity", 0)
            
            # Validate that we got meaningful weather data
            if condition != "unknown" and temperature != 0:
                self.log_test_result(
                    "Weather Triggers for NYC",
                    True,
                    f"✅ Valid weather data retrieved: {condition}, {temperature}°C, {humidity}% humidity"
                )
            else:
                self.log_test_result(
                    "Weather Triggers for NYC",
                    False,
                    f"❌ Invalid weather data: condition={condition}, temperature={temperature}",
                    weather_data
                )
        else:
            self.log_test_result(
                "Weather Triggers for NYC",
                False,
                f"❌ Failed to get weather triggers (Status: {status})",
                response
            )

    async def test_performance_analytics(self):
        """Test 4: Performance Analytics - Test campaign performance endpoint"""
        print("📊 TEST 4: PERFORMANCE ANALYTICS")
        print("-" * 60)
        
        if not self.test_campaign_id:
            self.log_test_result(
                "Campaign Performance Analytics",
                False,
                "❌ No campaign ID available for testing (campaign creation failed)"
            )
            return
        
        success, response, status = await self.make_request(
            "GET", f"/campaigns/{self.test_campaign_id}/performance",
            params={"user_id": self.test_user_id}
        )
        
        if success and response.get("success"):
            performance_summary = response.get("performance_summary", {})
            total_impressions = performance_summary.get("total_impressions", 0)
            total_spend = performance_summary.get("total_spend", 0)
            cpm = performance_summary.get("average_cpm", 0)
            
            # Validate that we got analytics data structure
            if isinstance(performance_summary, dict) and len(performance_summary) > 0:
                self.log_test_result(
                    "Campaign Performance Analytics",
                    True,
                    f"✅ Analytics data retrieved: {total_impressions} impressions, ${total_spend} spend, ${cpm} CPM"
                )
            else:
                self.log_test_result(
                    "Campaign Performance Analytics",
                    False,
                    f"❌ Empty or invalid performance data structure",
                    performance_summary
                )
        else:
            self.log_test_result(
                "Campaign Performance Analytics",
                False,
                f"❌ Failed to get campaign performance (Status: {status})",
                response
            )

    async def test_all_endpoints_return_200(self):
        """Test 5: Verify all endpoints return 200 status codes"""
        print("🔍 TEST 5: ALL ENDPOINTS RETURN 200 STATUS CODES")
        print("-" * 60)
        
        endpoints_to_test = [
            ("GET", "/platforms", {}),
            ("GET", "/triggers/weather", {
                "latitude": 40.7580,
                "longitude": -73.9855,
                "location_name": "New York City",
                "user_id": self.test_user_id
            })
        ]
        
        if self.test_campaign_id:
            endpoints_to_test.extend([
                ("GET", f"/campaigns/{self.test_campaign_id}/performance", {"user_id": self.test_user_id}),
                ("GET", f"/campaigns/{self.test_campaign_id}", {"user_id": self.test_user_id})
            ])
        
        all_200 = True
        status_results = []
        
        for method, endpoint, params in endpoints_to_test:
            try:
                url = f"{self.api_base}{endpoint}"
                if method == "GET":
                    async with self.session.get(url, params=params) as response:
                        status_results.append((endpoint, response.status))
                        if response.status != 200:
                            all_200 = False
            except Exception as e:
                status_results.append((endpoint, f"Error: {e}"))
                all_200 = False
        
        if all_200:
            self.log_test_result(
                "All Endpoints Return 200 Status",
                True,
                f"✅ All {len(endpoints_to_test)} tested endpoints returned 200 status codes"
            )
        else:
            failed_endpoints = [(ep, status) for ep, status in status_results if status != 200]
            self.log_test_result(
                "All Endpoints Return 200 Status",
                False,
                f"❌ {len(failed_endpoints)} endpoints failed to return 200",
                {"failed_endpoints": failed_endpoints}
            )

    async def run_final_verification_tests(self):
        """Run all final verification tests"""
        print("🚀 STARTING FINAL pDOOH INTEGRATION VERIFICATION")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Run the 4 specific tests requested
            await self.test_campaign_creation_without_creative()
            await self.test_platform_integration()
            await self.test_weather_triggers_nyc()
            await self.test_performance_analytics()
            await self.test_all_endpoints_return_200()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR during testing: {e}")
            self.failed_tests += 1
        
        finally:
            await self.cleanup_session()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print final verification results"""
        print("=" * 80)
        print("🎯 FINAL pDOOH INTEGRATION VERIFICATION RESULTS")
        print("=" * 80)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Print individual test results
        print("📋 INDIVIDUAL TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"   {i}. {status} {result['test']}")
            if result['details']:
                print(f"      📝 {result['details']}")
        
        print()
        
        # Print failed tests details
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['test']}")
                if result['details']:
                    print(f"     📝 {result['details']}")
                if result.get('response'):
                    print(f"     📊 Response: {result['response']}")
        
        print()
        
        # Success criteria assessment
        print("🎯 SUCCESS CRITERIA ASSESSMENT:")
        criteria_met = 0
        total_criteria = 5
        
        # Check each success criterion
        campaign_creation_success = any(r["success"] and "Campaign Creation WITHOUT primary_creative" in r["test"] for r in self.test_results)
        platforms_success = any(r["success"] and "All 8 pDOOH Platforms Accessible" in r["test"] for r in self.test_results)
        weather_success = any(r["success"] and "Weather Triggers for NYC" in r["test"] for r in self.test_results)
        analytics_success = any(r["success"] and "Campaign Performance Analytics" in r["test"] for r in self.test_results)
        status_200_success = any(r["success"] and "All Endpoints Return 200 Status" in r["test"] for r in self.test_results)
        
        criteria = [
            ("Campaign creation works WITHOUT primary_creative", campaign_creation_success),
            ("All 8 pDOOH platforms accessible", platforms_success),
            ("Weather triggers return valid data for NYC", weather_success),
            ("Performance endpoint returns analytics data", analytics_success),
            ("All endpoints return 200 status codes", status_200_success)
        ]
        
        for criterion, met in criteria:
            status = "✅" if met else "❌"
            print(f"   {status} {criterion}")
            if met:
                criteria_met += 1
        
        print()
        
        # Final assessment
        if criteria_met == total_criteria:
            print("🎉 SUCCESS: All pDOOH integration issues have been resolved!")
            print("✅ The system is fully functional and ready for production use.")
        elif criteria_met >= 4:
            print("✅ MOSTLY SUCCESSFUL: Most pDOOH integration issues resolved.")
            print("⚠️ Minor issues remain but core functionality is working.")
        elif criteria_met >= 2:
            print("⚠️ PARTIAL SUCCESS: Some pDOOH integration issues resolved.")
            print("🔧 Significant issues still need attention.")
        else:
            print("❌ CRITICAL: Major pDOOH integration issues remain unresolved.")
            print("🚨 Immediate attention required before production deployment.")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = FinalPDOOHVerificationTester()
    await tester.run_final_verification_tests()

if __name__ == "__main__":
    asyncio.run(main())