#!/usr/bin/env python3
"""
Backend Testing Script for Function 3: Content Distribution & Delivery Management System
Big Mann Entertainment Platform - Comprehensive API Testing

This script tests all distribution endpoints and functionality including:
1. Delivery Optimization (Create delivery plans, Get delivery plans, List plans, Update performance)
2. Platform Recommendations (Get recommendations based on content type and audience)
3. Analytics & Insights (Delivery performance analytics, Platform performance insights)
4. Distribution Strategies & Goals (Get available strategies and optimization goals)
5. Platform Management (Get available platforms, Get platforms by type)
6. Batch Operations (Create multiple delivery plans)
7. System Health & Monitoring
8. Integration Features (Create distribution jobs with optimization, Dashboard)
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://bme-dashboard.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user credentials for authentication
TEST_USER = {
    "email": "distribution.tester@bigmannentertainment.com",
    "password": "DistributionTest2025!",
    "full_name": "Distribution System Tester",
    "business_name": "Big Mann Entertainment Testing",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "address_line1": "123 Distribution Test St",
    "city": "Test City",
    "state_province": "Test State",
    "postal_code": "12345",
    "country": "US"
}

class DistributionTestRunner:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get access token"""
        try:
            # Try to register user (might already exist)
            register_url = f"{API_BASE}/auth/register"
            async with self.session.post(register_url, json=TEST_USER) as response:
                if response.status in [200, 201]:
                    print("✅ User registration successful")
                elif response.status == 400:
                    print("ℹ️ User already exists, proceeding to login")
                else:
                    print(f"⚠️ Registration response: {response.status}")
            
            # Login to get token
            login_url = f"{API_BASE}/auth/login"
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(login_url, json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    if self.auth_token:
                        print("✅ Authentication successful")
                        return True
                    else:
                        print("❌ No access token in response")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Login failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_endpoint(self, name: str, method: str, url: str, 
                          data: Optional[Dict] = None, 
                          params: Optional[Dict] = None,
                          expected_status: int = 200,
                          auth_required: bool = True) -> Dict[str, Any]:
        """Test a single endpoint"""
        self.total_tests += 1
        
        try:
            headers = self.get_auth_headers() if auth_required else {}
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers, params=params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    status = response.status
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data, params=params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    status = response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, headers=headers, json=data, params=params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    status = response.status
            else:
                return {
                    "name": name,
                    "success": False,
                    "error": f"Unsupported method: {method}",
                    "status": 0,
                    "response": None
                }
            
            success = status == expected_status
            if success:
                self.passed_tests += 1
                
            result = {
                "name": name,
                "success": success,
                "status": status,
                "expected_status": expected_status,
                "response": response_data,
                "error": None if success else f"Expected {expected_status}, got {status}"
            }
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            error_result = {
                "name": name,
                "success": False,
                "status": 0,
                "expected_status": expected_status,
                "response": None,
                "error": str(e)
            }
            self.test_results.append(error_result)
            return error_result

    async def test_delivery_optimization(self):
        """Test Delivery Optimization endpoints"""
        print("\n🎯 Testing Delivery Optimization Endpoints...")
        
        # Test 1: Create Delivery Plan
        create_plan_data = {
            "content_id": "test_content_123",
            "target_platforms": ["spotify", "apple_music", "youtube_music", "tiktok"],
            "strategy": "optimized_timing",
            "optimization_goal": "max_reach",
            "target_timezone": "UTC",
            "content_type": "music"
        }
        
        result = await self.test_endpoint(
            "Create Delivery Plan",
            "POST",
            f"{API_BASE}/distribution/delivery-plans/create",
            data=create_plan_data
        )
        
        plan_id = None
        if result["success"] and isinstance(result["response"], dict):
            delivery_plan = result["response"].get("delivery_plan", {})
            plan_id = delivery_plan.get("plan_id")
        
        # Test 2: Get Delivery Plan (if we have a plan_id)
        if plan_id:
            await self.test_endpoint(
                "Get Delivery Plan",
                "GET",
                f"{API_BASE}/distribution/delivery-plans/{plan_id}"
            )
            
            # Test 4: Update Delivery Performance (if we have a plan_id)
            performance_data = {
                "actual_reach": 50000,
                "actual_revenue": 250.75
            }
            await self.test_endpoint(
                "Update Delivery Performance",
                "POST",
                f"{API_BASE}/distribution/delivery-plans/{plan_id}/performance",
                data=performance_data
            )
        else:
            await self.test_endpoint(
                "Get Delivery Plan (Non-existent)",
                "GET",
                f"{API_BASE}/distribution/delivery-plans/non_existent_plan",
                expected_status=404
            )
        
        # Test 3: List Delivery Plans
        await self.test_endpoint(
            "List Delivery Plans",
            "GET",
            f"{API_BASE}/distribution/delivery-plans",
            params={"limit": 10, "offset": 0}
        )
    
    async def test_platform_recommendations(self):
        """Test Platform Recommendation endpoints"""
        print("\n🎯 Testing Platform Recommendation Endpoints...")
        
        # Test 1: Get Platform Recommendations - Music
        await self.test_endpoint(
            "Get Platform Recommendations (Music)",
            "GET",
            f"{API_BASE}/distribution/recommendations/platforms",
            params={
                "content_type": "music",
                "target_audience": "general",
                "budget_level": "medium"
            }
        )
        
        # Test 2: Get Platform Recommendations - Video
        await self.test_endpoint(
            "Get Platform Recommendations (Video)",
            "GET",
            f"{API_BASE}/distribution/recommendations/platforms",
            params={
                "content_type": "video",
                "target_audience": "young_adults",
                "budget_level": "high"
            }
        )
        
        # Test 3: Get Platform Recommendations - Podcast
        await self.test_endpoint(
            "Get Platform Recommendations (Podcast)",
            "GET",
            f"{API_BASE}/distribution/recommendations/platforms",
            params={
                "content_type": "podcast",
                "target_audience": "professionals",
                "budget_level": "low"
            }
        )
    
    async def test_analytics_insights(self):
        """Test Analytics & Insights endpoints"""
        print("\n📊 Testing Analytics & Insights Endpoints...")
        
        # Test 1: Get Delivery Performance Analytics
        await self.test_endpoint(
            "Get Delivery Performance Analytics (30 days)",
            "GET",
            f"{API_BASE}/distribution/analytics/delivery-performance",
            params={"days": 30}
        )
        
        # Test 2: Get Delivery Performance Analytics (7 days)
        await self.test_endpoint(
            "Get Delivery Performance Analytics (7 days)",
            "GET",
            f"{API_BASE}/distribution/analytics/delivery-performance",
            params={"days": 7}
        )
        
        # Test 3: Get Platform Performance Insights (All platforms)
        await self.test_endpoint(
            "Get Platform Performance Insights (All)",
            "GET",
            f"{API_BASE}/distribution/insights/platform-performance",
            params={"days": 30}
        )
        
        # Test 4: Get Platform Performance Insights (Specific platform)
        await self.test_endpoint(
            "Get Platform Performance Insights (Spotify)",
            "GET",
            f"{API_BASE}/distribution/insights/platform-performance",
            params={"platform": "spotify", "days": 30}
        )
        
        # Test 5: Get Platform Performance Insights (Invalid platform)
        await self.test_endpoint(
            "Get Platform Performance Insights (Invalid)",
            "GET",
            f"{API_BASE}/distribution/insights/platform-performance",
            params={"platform": "invalid_platform", "days": 30},
            expected_status=404
        )
    
    async def test_strategies_goals(self):
        """Test Distribution Strategies & Goals endpoints"""
        print("\n🎯 Testing Distribution Strategies & Goals Endpoints...")
        
        # Test 1: Get Delivery Strategies
        await self.test_endpoint(
            "Get Delivery Strategies",
            "GET",
            f"{API_BASE}/distribution/strategies"
        )
        
        # Test 2: Get Optimization Goals
        await self.test_endpoint(
            "Get Optimization Goals",
            "GET",
            f"{API_BASE}/distribution/optimization-goals"
        )
    
    async def test_platform_management(self):
        """Test Platform Management endpoints"""
        print("\n🏢 Testing Platform Management Endpoints...")
        
        # Test 1: Get Available Platforms
        await self.test_endpoint(
            "Get Available Platforms",
            "GET",
            f"{API_BASE}/distribution/platforms"
        )
        
        # Test 2: Get Platforms by Type (streaming_music)
        await self.test_endpoint(
            "Get Platforms by Type (streaming_music)",
            "GET",
            f"{API_BASE}/distribution/platforms/by-type/streaming_music"
        )
        
        # Test 3: Get Platforms by Type (social_media)
        await self.test_endpoint(
            "Get Platforms by Type (social_media)",
            "GET",
            f"{API_BASE}/distribution/platforms/by-type/social_media"
        )
        
        # Test 4: Get Platforms by Type (Invalid type)
        await self.test_endpoint(
            "Get Platforms by Type (Invalid)",
            "GET",
            f"{API_BASE}/distribution/platforms/by-type/invalid_type",
            expected_status=400
        )
    
    async def test_batch_operations(self):
        """Test Batch Operations endpoints"""
        print("\n📦 Testing Batch Operations Endpoints...")
        
        # Test 1: Create Batch Delivery Plans
        batch_data = {
            "content_ids": ["content_1", "content_2", "content_3"],
            "target_platforms": ["spotify", "apple_music", "youtube_music"],
            "strategy": "optimized_timing",
            "optimization_goal": "max_reach"
        }
        
        await self.test_endpoint(
            "Create Batch Delivery Plans",
            "POST",
            f"{API_BASE}/distribution/delivery-plans/batch",
            data=batch_data
        )
    
    async def test_system_health(self):
        """Test System Health & Monitoring endpoints"""
        print("\n🏥 Testing System Health & Monitoring Endpoints...")
        
        # Test 1: Health Check (No auth required)
        await self.test_endpoint(
            "Distribution Service Health Check",
            "GET",
            f"{API_BASE}/distribution/health",
            auth_required=False
        )
    
    async def test_integration_features(self):
        """Test Integration Features endpoints"""
        print("\n🔗 Testing Integration Features Endpoints...")
        
        # Test 1: Create Distribution Job with Optimization
        job_data = {
            "content_id": "integration_test_content",
            "content_title": "Test Song for Distribution",
            "main_artist": "Test Artist",
            "content_type": "music",
            "target_platforms": ["spotify", "apple_music", "tiktok"],
            "strategy": "optimized_timing",
            "optimization_goal": "max_revenue",
            "priority": "high",
            "metadata": {
                "genre": "Hip-Hop",
                "duration": 180,
                "explicit": False
            }
        }
        
        await self.test_endpoint(
            "Create Distribution Job with Optimization",
            "POST",
            f"{API_BASE}/distribution/jobs/create-with-optimization",
            data=job_data
        )
        
        # Test 2: Get Distribution Dashboard
        await self.test_endpoint(
            "Get Distribution Dashboard (30 days)",
            "GET",
            f"{API_BASE}/distribution/dashboard",
            params={"days": 30}
        )
        
        # Test 3: Get Distribution Dashboard (7 days)
        await self.test_endpoint(
            "Get Distribution Dashboard (7 days)",
            "GET",
            f"{API_BASE}/distribution/dashboard",
            params={"days": 7}
        )
    
    async def run_all_tests(self):
        """Run all distribution system tests"""
        print("🎵 Starting Function 3: Content Distribution & Delivery Management System Testing")
        print("=" * 80)
        
        await self.setup_session()
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            await self.cleanup_session()
            return
        
        try:
            # Run all test categories
            await self.test_delivery_optimization()
            await self.test_platform_recommendations()
            await self.test_analytics_insights()
            await self.test_strategies_goals()
            await self.test_platform_management()
            await self.test_batch_operations()
            await self.test_system_health()
            await self.test_integration_features()
            
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
        
        finally:
            await self.cleanup_session()
        
        # Print results summary
        self.print_results_summary()
    
    def print_results_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "=" * 80)
        print("📊 FUNCTION 3: CONTENT DISTRIBUTION & DELIVERY MANAGEMENT TESTING RESULTS")
        print("=" * 80)
        
        # Overall statistics
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"📈 Overall Success Rate: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests})")
        
        # Category breakdown
        categories = {
            "Delivery Optimization": [],
            "Platform Recommendations": [],
            "Analytics & Insights": [],
            "Strategies & Goals": [],
            "Platform Management": [],
            "Batch Operations": [],
            "System Health": [],
            "Integration Features": []
        }
        
        # Categorize results
        for result in self.test_results:
            name = result["name"]
            if "Delivery Plan" in name or "Performance" in name:
                categories["Delivery Optimization"].append(result)
            elif "Recommendation" in name:
                categories["Platform Recommendations"].append(result)
            elif "Analytics" in name or "Insights" in name:
                categories["Analytics & Insights"].append(result)
            elif "Strategies" in name or "Goals" in name:
                categories["Strategies & Goals"].append(result)
            elif "Platforms" in name and "batch" not in name.lower():
                categories["Platform Management"].append(result)
            elif "Batch" in name:
                categories["Batch Operations"].append(result)
            elif "Health" in name:
                categories["System Health"].append(result)
            elif "Distribution Job" in name or "Dashboard" in name:
                categories["Integration Features"].append(result)
        
        # Print category results
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
                print(f"\n{status} {category}: {rate:.1f}% ({passed}/{total})")
                
                for result in results:
                    status_icon = "✅" if result["success"] else "❌"
                    print(f"  {status_icon} {result['name']}")
                    if not result["success"]:
                        print(f"     Error: {result.get('error', 'Unknown error')}")
        
        # Detailed failure analysis
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ANALYSIS ({len(failed_tests)} failures):")
            for result in failed_tests:
                print(f"\n🔍 {result['name']}:")
                print(f"   Status: {result['status']} (expected {result['expected_status']})")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                if result.get('response'):
                    print(f"   Response: {str(result['response'])[:200]}...")
        
        # Success highlights
        successful_tests = [r for r in self.test_results if r["success"]]
        if successful_tests:
            print(f"\n✅ SUCCESSFUL TESTS HIGHLIGHTS ({len(successful_tests)} successes):")
            
            # Highlight key successful endpoints
            key_endpoints = [
                "Get Available Platforms",
                "Get Delivery Strategies", 
                "Get Optimization Goals",
                "Distribution Service Health Check",
                "Create Delivery Plan",
                "Get Platform Recommendations"
            ]
            
            for endpoint in key_endpoints:
                matching_results = [r for r in successful_tests if endpoint in r["name"]]
                if matching_results:
                    result = matching_results[0]
                    print(f"   ✅ {result['name']} - Status: {result['status']}")
        
        # Production readiness assessment
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT: System is production-ready with outstanding functionality")
        elif success_rate >= 75:
            print("   🟡 GOOD: System is mostly functional with minor issues")
        elif success_rate >= 50:
            print("   🟠 FAIR: System has core functionality but needs improvements")
        else:
            print("   🔴 POOR: System requires significant fixes before production")
        
        # Key metrics summary
        print(f"\n📋 KEY METRICS SUMMARY:")
        print(f"   • Total Endpoints Tested: {self.total_tests}")
        print(f"   • Successful Responses: {self.passed_tests}")
        print(f"   • Failed Responses: {self.total_tests - self.passed_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        
        # Integration verification
        integration_tests = [r for r in self.test_results if "Distribution Job" in r["name"] or "Dashboard" in r["name"]]
        if integration_tests:
            integration_success = sum(1 for r in integration_tests if r["success"])
            integration_total = len(integration_tests)
            integration_rate = (integration_success / integration_total * 100) if integration_total > 0 else 0
            print(f"   • Integration Features: {integration_rate:.1f}% ({integration_success}/{integration_total})")
        
        print("\n" + "=" * 80)
        print("🎵 Function 3: Content Distribution & Delivery Management Testing Complete!")
        print("=" * 80)

async def main():
    """Main test execution function"""
    runner = DistributionTestRunner()
    await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())