#!/usr/bin/env python3
"""
pDOOH Integration Backend Testing
Big Mann Entertainment Platform - Comprehensive pDOOH Testing

This script tests all pDOOH (Programmatic Digital Out-of-Home) integration endpoints
including campaign management, real-time triggers, platform inventory, performance analytics,
and dynamic creative optimization.
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

class PDOOHBackendTester:
    def __init__(self):
        # Get backend URL from environment
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
        else:
            self.base_url = "http://localhost:8001"
        
        self.api_base = f"{self.base_url}/api/pdooh"
        self.test_user_id = "test_user_pdooh_integration"
        self.test_campaign_id = None
        self.session = None
        
        # Test results tracking
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
        print(f"🎯 pDOOH Backend Tester initialized")
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

    async def test_campaign_management_endpoints(self):
        """Test Campaign Management Endpoints (5 endpoints)"""
        print("🎯 TESTING CAMPAIGN MANAGEMENT ENDPOINTS")
        print("-" * 50)
        
        # 1. Test POST /api/pdooh/campaigns - Create new pDOOH campaign
        campaign_data = {
            "name": "Test pDOOH Campaign",
            "description": "Testing programmatic DOOH integration",
            "campaign_type": "artist_promotion",
            "start_date": "2025-01-20T00:00:00Z",
            "end_date": "2025-02-20T00:00:00Z",
            "budget_total": 10000,
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
                "name": "Summer Festival Creative",
                "format": "static_image",
                "file_url": "/assets/creative.jpg",
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
            self.log_test_result(
                "POST /api/pdooh/campaigns - Create Campaign",
                True,
                f"Campaign created with ID: {self.test_campaign_id}"
            )
        else:
            self.log_test_result(
                "POST /api/pdooh/campaigns - Create Campaign",
                False,
                f"Failed to create campaign (Status: {status})",
                response
            )
        
        # 2. Test GET /api/pdooh/campaigns - Get user campaigns
        success, response, status = await self.make_request(
            "GET", "/campaigns",
            params={"user_id": self.test_user_id, "limit": 10, "offset": 0}
        )
        
        if success and response.get("success"):
            campaigns_count = len(response.get("campaigns", []))
            self.log_test_result(
                "GET /api/pdooh/campaigns - Get User Campaigns",
                True,
                f"Retrieved {campaigns_count} campaigns"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/campaigns - Get User Campaigns",
                False,
                f"Failed to get campaigns (Status: {status})",
                response
            )
        
        # 3. Test GET /api/pdooh/campaigns/{campaign_id} - Get specific campaign
        if self.test_campaign_id:
            success, response, status = await self.make_request(
                "GET", f"/campaigns/{self.test_campaign_id}",
                params={"user_id": self.test_user_id}
            )
            
            if success and response.get("success"):
                campaign = response.get("campaign", {})
                self.log_test_result(
                    "GET /api/pdooh/campaigns/{campaign_id} - Get Specific Campaign",
                    True,
                    f"Retrieved campaign: {campaign.get('name', 'Unknown')}"
                )
            else:
                self.log_test_result(
                    "GET /api/pdooh/campaigns/{campaign_id} - Get Specific Campaign",
                    False,
                    f"Failed to get specific campaign (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "GET /api/pdooh/campaigns/{campaign_id} - Get Specific Campaign",
                False,
                "No campaign ID available for testing"
            )
        
        # 4. Test POST /api/pdooh/campaigns/{campaign_id}/launch - Launch campaign
        if self.test_campaign_id:
            success, response, status = await self.make_request(
                "POST", f"/campaigns/{self.test_campaign_id}/launch",
                params={"user_id": self.test_user_id}
            )
            
            if success and response.get("success"):
                launch_results = response.get("launch_results", {})
                self.log_test_result(
                    "POST /api/pdooh/campaigns/{campaign_id}/launch - Launch Campaign",
                    True,
                    f"Campaign launched on {len(launch_results)} platforms"
                )
            else:
                self.log_test_result(
                    "POST /api/pdooh/campaigns/{campaign_id}/launch - Launch Campaign",
                    False,
                    f"Failed to launch campaign (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "POST /api/pdooh/campaigns/{campaign_id}/launch - Launch Campaign",
                False,
                "No campaign ID available for testing"
            )
        
        # 5. Test PUT /api/pdooh/campaigns/{campaign_id}/status - Update campaign status
        if self.test_campaign_id:
            success, response, status = await self.make_request(
                "PUT", f"/campaigns/{self.test_campaign_id}/status",
                params={"user_id": self.test_user_id, "status": "paused"}
            )
            
            if success and response.get("success"):
                new_status = response.get("new_status")
                self.log_test_result(
                    "PUT /api/pdooh/campaigns/{campaign_id}/status - Update Status",
                    True,
                    f"Campaign status updated to: {new_status}"
                )
            else:
                self.log_test_result(
                    "PUT /api/pdooh/campaigns/{campaign_id}/status - Update Status",
                    False,
                    f"Failed to update campaign status (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "PUT /api/pdooh/campaigns/{campaign_id}/status - Update Status",
                False,
                "No campaign ID available for testing"
            )

    async def test_platform_inventory_endpoints(self):
        """Test Platform & Inventory Endpoints (2 endpoints)"""
        print("🏢 TESTING PLATFORM & INVENTORY ENDPOINTS")
        print("-" * 50)
        
        # 1. Test GET /api/pdooh/platforms - Get available pDOOH platforms
        success, response, status = await self.make_request("GET", "/platforms")
        
        if success and response.get("success"):
            platforms = response.get("platforms", {})
            total_platforms = response.get("total_platforms", 0)
            self.log_test_result(
                "GET /api/pdooh/platforms - Get Available Platforms",
                True,
                f"Retrieved {total_platforms} pDOOH platforms"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/platforms - Get Available Platforms",
                False,
                f"Failed to get platforms (Status: {status})",
                response
            )
        
        # 2. Test GET /api/pdooh/platforms/{platform}/inventory - Get platform inventory
        test_platform = "trade_desk"
        success, response, status = await self.make_request(
            "GET", f"/platforms/{test_platform}/inventory",
            params={
                "user_id": self.test_user_id,
                "location": "New York",
                "min_impressions": 50000,
                "max_cpm": 15.0
            }
        )
        
        if success and response.get("success"):
            inventory_count = response.get("inventory_count", 0)
            locations = response.get("locations", [])
            self.log_test_result(
                "GET /api/pdooh/platforms/{platform}/inventory - Get Platform Inventory",
                True,
                f"Retrieved {inventory_count} inventory locations for {test_platform}"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/platforms/{platform}/inventory - Get Platform Inventory",
                False,
                f"Failed to get platform inventory (Status: {status})",
                response
            )

    async def test_real_time_triggers_endpoints(self):
        """Test Real-Time Triggers Endpoints (5 endpoints)"""
        print("⚡ TESTING REAL-TIME TRIGGERS ENDPOINTS")
        print("-" * 50)
        
        # 1. Test GET /api/pdooh/triggers/weather - Get weather triggers
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
            self.log_test_result(
                "GET /api/pdooh/triggers/weather - Get Weather Triggers",
                True,
                f"Weather: {condition}, Temperature: {temperature}°C"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/triggers/weather - Get Weather Triggers",
                False,
                f"Failed to get weather triggers (Status: {status})",
                response
            )
        
        # 2. Test GET /api/pdooh/triggers/sports - Get sports event triggers
        success, response, status = await self.make_request(
            "GET", "/triggers/sports",
            params={
                "location": "New York",
                "user_id": self.test_user_id
            }
        )
        
        if success and response.get("success"):
            events_count = response.get("events_count", 0)
            sports_events = response.get("sports_events", [])
            self.log_test_result(
                "GET /api/pdooh/triggers/sports - Get Sports Event Triggers",
                True,
                f"Found {events_count} sports events"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/triggers/sports - Get Sports Event Triggers",
                False,
                f"Failed to get sports triggers (Status: {status})",
                response
            )
        
        # 3. Test GET /api/pdooh/triggers/events - Get local event triggers
        success, response, status = await self.make_request(
            "GET", "/triggers/events",
            params={
                "location": "New York",
                "radius_km": 25,
                "user_id": self.test_user_id
            }
        )
        
        if success and response.get("success"):
            events_count = response.get("events_count", 0)
            local_events = response.get("local_events", [])
            self.log_test_result(
                "GET /api/pdooh/triggers/events - Get Local Event Triggers",
                True,
                f"Found {events_count} local events within 25km"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/triggers/events - Get Local Event Triggers",
                False,
                f"Failed to get event triggers (Status: {status})",
                response
            )
        
        # 4. Test POST /api/pdooh/triggers/evaluate - Evaluate campaign triggers
        if self.test_campaign_id:
            trigger_data = {
                "campaign_id": self.test_campaign_id,
                "location": "New York City",
                "latitude": 40.7580,
                "longitude": -73.9855
            }
            
            success, response, status = await self.make_request(
                "POST", "/triggers/evaluate",
                params={"user_id": self.test_user_id},
                data=trigger_data
            )
            
            if success and response.get("success"):
                triggered_conditions = response.get("triggered_conditions", [])
                creative_variants = response.get("creative_variants", {})
                self.log_test_result(
                    "POST /api/pdooh/triggers/evaluate - Evaluate Campaign Triggers",
                    True,
                    f"Evaluated {len(triggered_conditions)} trigger conditions"
                )
            else:
                self.log_test_result(
                    "POST /api/pdooh/triggers/evaluate - Evaluate Campaign Triggers",
                    False,
                    f"Failed to evaluate triggers (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "POST /api/pdooh/triggers/evaluate - Evaluate Campaign Triggers",
                False,
                "No campaign ID available for testing"
            )
        
        # 5. Test POST /api/pdooh/triggers/rules - Create trigger rules
        rule_data = {
            "name": "Hot Weather Music Promotion",
            "trigger_type": "weather",
            "conditions": {
                "temperature": ">25",
                "weather": "sunny"
            },
            "actions": {
                "creative_variant": "summer_theme",
                "message_overlay": "Beat the heat with cool music!"
            },
            "active": True,
            "priority": 2
        }
        
        success, response, status = await self.make_request(
            "POST", "/triggers/rules",
            params={"user_id": self.test_user_id},
            data=rule_data
        )
        
        if success and response.get("success"):
            rule_id = response.get("rule_id")
            self.log_test_result(
                "POST /api/pdooh/triggers/rules - Create Trigger Rules",
                True,
                f"Created trigger rule with ID: {rule_id}"
            )
        else:
            self.log_test_result(
                "POST /api/pdooh/triggers/rules - Create Trigger Rules",
                False,
                f"Failed to create trigger rule (Status: {status})",
                response
            )

    async def test_performance_analytics_endpoints(self):
        """Test Performance & Analytics Endpoints (4 endpoints)"""
        print("📊 TESTING PERFORMANCE & ANALYTICS ENDPOINTS")
        print("-" * 50)
        
        # 1. Test GET /api/pdooh/campaigns/{campaign_id}/performance - Get campaign performance
        if self.test_campaign_id:
            success, response, status = await self.make_request(
                "GET", f"/campaigns/{self.test_campaign_id}/performance",
                params={"user_id": self.test_user_id}
            )
            
            if success and response.get("success"):
                performance_summary = response.get("performance_summary", {})
                total_impressions = performance_summary.get("total_impressions", 0)
                total_spend = performance_summary.get("total_spend", 0)
                self.log_test_result(
                    "GET /api/pdooh/campaigns/{campaign_id}/performance - Get Campaign Performance",
                    True,
                    f"Performance: {total_impressions} impressions, ${total_spend} spend"
                )
            else:
                self.log_test_result(
                    "GET /api/pdooh/campaigns/{campaign_id}/performance - Get Campaign Performance",
                    False,
                    f"Failed to get campaign performance (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "GET /api/pdooh/campaigns/{campaign_id}/performance - Get Campaign Performance",
                False,
                "No campaign ID available for testing"
            )
        
        # 2. Test GET /api/pdooh/campaigns/{campaign_id}/attribution - Get attribution data
        if self.test_campaign_id:
            success, response, status = await self.make_request(
                "GET", f"/campaigns/{self.test_campaign_id}/attribution",
                params={
                    "user_id": self.test_user_id,
                    "attribution_window_hours": 24
                }
            )
            
            if success and response.get("success"):
                attribution_data = response.get("attribution_data", {})
                total_conversions = attribution_data.get("total_conversions", 0)
                attribution_rate = attribution_data.get("attribution_rate", 0)
                self.log_test_result(
                    "GET /api/pdooh/campaigns/{campaign_id}/attribution - Get Attribution Data",
                    True,
                    f"Attribution: {total_conversions} conversions, {attribution_rate}% rate"
                )
            else:
                self.log_test_result(
                    "GET /api/pdooh/campaigns/{campaign_id}/attribution - Get Attribution Data",
                    False,
                    f"Failed to get attribution data (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "GET /api/pdooh/campaigns/{campaign_id}/attribution - Get Attribution Data",
                False,
                "No campaign ID available for testing"
            )
        
        # 3. Test GET /api/pdooh/monitoring/dashboard - Get monitoring dashboard
        success, response, status = await self.make_request(
            "GET", "/monitoring/dashboard",
            params={
                "user_id": self.test_user_id,
                "time_range": "24h"
            }
        )
        
        if success and response.get("success"):
            dashboard = response.get("dashboard", {})
            campaign_overview = dashboard.get("campaign_overview", {})
            total_campaigns = campaign_overview.get("total_campaigns", 0)
            active_campaigns = campaign_overview.get("active_campaigns", 0)
            self.log_test_result(
                "GET /api/pdooh/monitoring/dashboard - Get Monitoring Dashboard",
                True,
                f"Dashboard: {total_campaigns} total campaigns, {active_campaigns} active"
            )
        else:
            self.log_test_result(
                "GET /api/pdooh/monitoring/dashboard - Get Monitoring Dashboard",
                False,
                f"Failed to get monitoring dashboard (Status: {status})",
                response
            )
        
        # 4. Test GET /api/pdooh/reporting/export/{campaign_id} - Export campaign report
        if self.test_campaign_id:
            success, response, status = await self.make_request(
                "GET", f"/reporting/export/{self.test_campaign_id}",
                params={
                    "user_id": self.test_user_id,
                    "format": "csv"
                }
            )
            
            if success and response.get("success"):
                download_url = response.get("download_url", "")
                export_format = response.get("export_data", {}).get("export_format", "")
                self.log_test_result(
                    "GET /api/pdooh/reporting/export/{campaign_id} - Export Campaign Report",
                    True,
                    f"Report exported in {export_format.upper()} format"
                )
            else:
                self.log_test_result(
                    "GET /api/pdooh/reporting/export/{campaign_id} - Export Campaign Report",
                    False,
                    f"Failed to export campaign report (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "GET /api/pdooh/reporting/export/{campaign_id} - Export Campaign Report",
                False,
                "No campaign ID available for testing"
            )

    async def test_dynamic_creative_optimization_endpoints(self):
        """Test Dynamic Creative Optimization Endpoints (2 endpoints)"""
        print("🎨 TESTING DYNAMIC CREATIVE OPTIMIZATION ENDPOINTS")
        print("-" * 50)
        
        # 1. Test POST /api/pdooh/dco/optimize - Optimize creative based on triggers
        if self.test_campaign_id:
            location_data = {
                "location": "New York City",
                "latitude": 40.7580,
                "longitude": -73.9855
            }
            
            success, response, status = await self.make_request(
                "POST", f"/dco/optimize?campaign_id={self.test_campaign_id}",
                params={"user_id": self.test_user_id},
                data=location_data
            )
            
            if success and response.get("success"):
                optimization = response.get("optimization", {})
                optimization_score = optimization.get("optimization_score", 0)
                recommendations = optimization.get("recommendations", {})
                self.log_test_result(
                    "POST /api/pdooh/dco/optimize - Optimize Creative",
                    True,
                    f"Optimization score: {optimization_score}, Primary creative: {recommendations.get('primary_creative', 'default')}"
                )
            else:
                self.log_test_result(
                    "POST /api/pdooh/dco/optimize - Optimize Creative",
                    False,
                    f"Failed to optimize creative (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "POST /api/pdooh/dco/optimize - Optimize Creative",
                False,
                "No campaign ID available for testing"
            )
        
        # 2. Test GET /api/pdooh/dco/variants/{campaign_id} - Get creative variants
        if self.test_campaign_id:
            success, response, status = await self.make_request(
                "GET", f"/dco/variants/{self.test_campaign_id}",
                params={"user_id": self.test_user_id}
            )
            
            if success and response.get("success"):
                creative_variants = response.get("creative_variants", {})
                variants_count = response.get("variants_count", 0)
                self.log_test_result(
                    "GET /api/pdooh/dco/variants/{campaign_id} - Get Creative Variants",
                    True,
                    f"Retrieved {variants_count} creative variants"
                )
            else:
                self.log_test_result(
                    "GET /api/pdooh/dco/variants/{campaign_id} - Get Creative Variants",
                    False,
                    f"Failed to get creative variants (Status: {status})",
                    response
                )
        else:
            self.log_test_result(
                "GET /api/pdooh/dco/variants/{campaign_id} - Get Creative Variants",
                False,
                "No campaign ID available for testing"
            )

    async def run_comprehensive_tests(self):
        """Run all pDOOH integration tests"""
        print("🚀 STARTING COMPREHENSIVE pDOOH INTEGRATION BACKEND TESTING")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Test all endpoint categories
            await self.test_campaign_management_endpoints()
            await self.test_platform_inventory_endpoints()
            await self.test_real_time_triggers_endpoints()
            await self.test_performance_analytics_endpoints()
            await self.test_dynamic_creative_optimization_endpoints()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR during testing: {e}")
            self.failed_tests += 1
        
        finally:
            await self.cleanup_session()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("=" * 80)
        print("🎯 pDOOH INTEGRATION BACKEND TESTING RESULTS")
        print("=" * 80)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        categories = {
            "Campaign Management": 0,
            "Platform & Inventory": 0,
            "Real-Time Triggers": 0,
            "Performance & Analytics": 0,
            "Dynamic Creative Optimization": 0
        }
        
        category_passed = {cat: 0 for cat in categories}
        
        for result in self.test_results:
            test_name = result["test"]
            success = result["success"]
            
            if "campaigns" in test_name.lower() and ("create" in test_name.lower() or "get" in test_name.lower() or "launch" in test_name.lower() or "status" in test_name.lower()):
                categories["Campaign Management"] += 1
                if success:
                    category_passed["Campaign Management"] += 1
            elif "platforms" in test_name.lower() or "inventory" in test_name.lower():
                categories["Platform & Inventory"] += 1
                if success:
                    category_passed["Platform & Inventory"] += 1
            elif "triggers" in test_name.lower():
                categories["Real-Time Triggers"] += 1
                if success:
                    category_passed["Real-Time Triggers"] += 1
            elif "performance" in test_name.lower() or "attribution" in test_name.lower() or "monitoring" in test_name.lower() or "reporting" in test_name.lower():
                categories["Performance & Analytics"] += 1
                if success:
                    category_passed["Performance & Analytics"] += 1
            elif "dco" in test_name.lower() or "creative" in test_name.lower():
                categories["Dynamic Creative Optimization"] += 1
                if success:
                    category_passed["Dynamic Creative Optimization"] += 1
        
        print("📋 CATEGORY BREAKDOWN:")
        for category, total in categories.items():
            if total > 0:
                passed = category_passed[category]
                rate = (passed / total * 100)
                status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
                print(f"   {status} {category}: {passed}/{total} ({rate:.1f}%)")
        
        print()
        
        # Print failed tests details
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['test']}")
                if result['details']:
                    print(f"     📝 {result['details']}")
        
        print()
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: pDOOH integration is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: pDOOH integration is mostly functional with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: pDOOH integration has significant issues that need attention.")
        else:
            print("❌ CRITICAL: pDOOH integration has major problems requiring immediate fixes.")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = PDOOHBackendTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())