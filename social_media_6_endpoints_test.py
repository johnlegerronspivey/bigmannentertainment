#!/usr/bin/env python3
"""
Social Media Phases 5-10 - 6 Previously Failing Endpoints Testing
Testing the 6 specific endpoints that were previously failing due to parameter validation issues
and have now been fixed with proper request models.

Endpoints to test:
1. Performance Report Generation - /api/social-media-advanced/analytics/generate-report (POST)
2. Content Adaptation - /api/social-media-advanced/campaigns/{campaign_id}/adapt-content (POST)
3. Campaign Performance Tracking - /api/social-media-advanced/campaigns/{campaign_id}/track-performance (POST)
4. AI Content Recommendations - /api/social-media-advanced/ai/content-recommendations (POST)
5. AI Trend Predictions - /api/social-media-advanced/ai/predict-trends (POST)
6. AI Content Optimization - /api/social-media-advanced/ai/optimize-content (POST)
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Backend URL from environment
BACKEND_URL = "https://bme-creator-hub.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class SocialMediaEndpointsTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "endpoint.tester@bigmannentertainment.com"
        self.test_user_password = "EndpointTest2025!"
        self.test_results = []
        self.campaign_id = None
        
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
        if response_data and isinstance(response_data, dict):
            if "error" in response_data:
                print(f"   Error: {response_data['error']}")
            elif "message" in response_data:
                print(f"   Message: {response_data['message']}")
                
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          files: Dict = None, headers: Dict = None) -> Dict:
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
            else:
                # Handle other methods
                async with self.session.request(method, url, json=data, headers=headers) as response:
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
        """Test user registration and authentication"""
        print("\n🔐 TESTING USER AUTHENTICATION")
        
        # Test user registration
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": "Endpoint Tester",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Test Street",
            "city": "Test City",
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

    async def create_test_campaign(self):
        """Create a test campaign for testing campaign-related endpoints"""
        print("\n🎯 CREATING TEST CAMPAIGN")
        
        campaign_data = {
            "name": "Test Campaign for Endpoint Testing",
            "description": "Campaign created for testing the 6 fixed endpoints",
            "platforms": ["instagram", "twitter", "tiktok"],
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "budget_total": 1000.0,
            "budget_allocation": {
                "instagram": 400.0,
                "twitter": 300.0,
                "tiktok": 300.0
            },
            "content_templates": ["test_template"],
            "target_audience": {
                "age_range": "18-35",
                "interests": ["music", "entertainment"],
                "locations": ["US"]
            },
            "goals": {
                "reach": 50000,
                "engagement": 3.0
            },
            "status": "active"
        }
        
        response = await self.make_request("POST", "/social-media-advanced/campaigns/create", campaign_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.campaign_id = response["data"].get("campaign_id")
            self.log_test("Create Test Campaign", "PASS", f"Campaign created with ID: {self.campaign_id}", response["data"])
            return True
        else:
            self.log_test("Create Test Campaign", "FAIL", f"Status: {response['status']}", response["data"])
            # Use a fallback campaign ID for testing
            self.campaign_id = "test_campaign_id"
            return False

    async def test_performance_report_generation(self):
        """Test 1: Performance Report Generation with PerformanceReportRequest model"""
        print("\n📊 TESTING PERFORMANCE REPORT GENERATION")
        
        # Test with new PerformanceReportRequest model format
        report_request = {
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "platforms": ["instagram", "twitter", "tiktok"]
        }
        
        response = await self.make_request("POST", "/social-media-advanced/analytics/generate-report", report_request)
        
        if response["status"] == 200:
            if response["data"].get("success"):
                self.log_test("Performance Report Generation", "PASS", "Report generated successfully with new request model", response["data"])
            else:
                self.log_test("Performance Report Generation", "FAIL", "Request succeeded but response indicates failure", response["data"])
        else:
            self.log_test("Performance Report Generation", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_content_adaptation(self):
        """Test 2: Content Adaptation with ContentAdaptationRequest model"""
        print("\n🔄 TESTING CONTENT ADAPTATION")
        
        # Test with new ContentAdaptationRequest model format
        adaptation_request = {
            "content_id": "test_content_001",
            "platforms": ["instagram", "twitter", "tiktok"]
        }
        
        campaign_id = self.campaign_id or "test_campaign_id"
        response = await self.make_request("POST", f"/social-media-advanced/campaigns/{campaign_id}/adapt-content", adaptation_request)
        
        if response["status"] == 200:
            if response["data"].get("success"):
                adaptations = response["data"].get("adaptations", {})
                self.log_test("Content Adaptation", "PASS", f"Content adapted for {len(adaptations)} platforms with new request model", response["data"])
            else:
                self.log_test("Content Adaptation", "FAIL", "Request succeeded but response indicates failure", response["data"])
        else:
            self.log_test("Content Adaptation", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_campaign_performance_tracking(self):
        """Test 3: Campaign Performance Tracking with CampaignPerformanceRequest model"""
        print("\n📈 TESTING CAMPAIGN PERFORMANCE TRACKING")
        
        # Test with new CampaignPerformanceRequest model format
        performance_request = {
            "platform": "instagram",
            "metrics": {
                "impressions": 15000,
                "clicks": 450,
                "conversions": 25,
                "engagement_rate": 3.2
            },
            "budget_spent": 250.0
        }
        
        campaign_id = self.campaign_id or "test_campaign_id"
        response = await self.make_request("POST", f"/social-media-advanced/campaigns/{campaign_id}/track-performance", performance_request)
        
        if response["status"] == 200:
            if response["data"].get("success"):
                self.log_test("Campaign Performance Tracking", "PASS", "Performance tracked successfully with new request model", response["data"])
            else:
                self.log_test("Campaign Performance Tracking", "FAIL", "Request succeeded but response indicates failure", response["data"])
        else:
            self.log_test("Campaign Performance Tracking", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_ai_content_recommendations(self):
        """Test 4: AI Content Recommendations with ContentRecommendationRequest model"""
        print("\n🤖 TESTING AI CONTENT RECOMMENDATIONS")
        
        # Test with new ContentRecommendationRequest model format
        recommendation_request = {
            "platforms": ["instagram", "twitter", "tiktok"]
        }
        
        response = await self.make_request("POST", "/social-media-advanced/ai/content-recommendations", recommendation_request)
        
        if response["status"] == 200:
            if response["data"].get("success"):
                recommendations = response["data"].get("recommendations", [])
                self.log_test("AI Content Recommendations", "PASS", f"Generated {len(recommendations)} recommendations with new request model", response["data"])
            else:
                self.log_test("AI Content Recommendations", "FAIL", "Request succeeded but response indicates failure", response["data"])
        else:
            self.log_test("AI Content Recommendations", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_ai_trend_predictions(self):
        """Test 5: AI Trend Predictions with TrendPredictionRequest model"""
        print("\n🔮 TESTING AI TREND PREDICTIONS")
        
        # Test with new TrendPredictionRequest model format
        prediction_request = {
            "categories": ["hip-hop", "music", "entertainment", "social-media"]
        }
        
        response = await self.make_request("POST", "/social-media-advanced/ai/predict-trends", prediction_request)
        
        if response["status"] == 200:
            if response["data"].get("success"):
                predictions = response["data"].get("predictions", [])
                self.log_test("AI Trend Predictions", "PASS", f"Generated {len(predictions)} trend predictions with new request model", response["data"])
            else:
                self.log_test("AI Trend Predictions", "FAIL", "Request succeeded but response indicates failure", response["data"])
        else:
            self.log_test("AI Trend Predictions", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_ai_content_optimization(self):
        """Test 6: AI Content Optimization with ContentOptimizationRequest model"""
        print("\n⚡ TESTING AI CONTENT OPTIMIZATION")
        
        # Test with new ContentOptimizationRequest model format
        optimization_request = {
            "content": "Check out our new track! It's fire 🔥 Link in bio for streaming on all platforms. What do you think?",
            "target_platform": "tiktok"
        }
        
        response = await self.make_request("POST", "/social-media-advanced/ai/optimize-content", optimization_request)
        
        if response["status"] == 200:
            if response["data"].get("success"):
                optimizations = response["data"].get("optimizations", {})
                self.log_test("AI Content Optimization", "PASS", f"Content optimized for {optimization_request['target_platform']} with new request model", response["data"])
            else:
                self.log_test("AI Content Optimization", "FAIL", "Request succeeded but response indicates failure", response["data"])
        else:
            self.log_test("AI Content Optimization", "FAIL", f"Status: {response['status']}", response["data"])

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 6 PREVIOUSLY FAILING ENDPOINTS - TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        
        # Group tests by category
        endpoint_tests = [t for t in self.test_results if any(keyword in t["test"] for keyword in 
                         ["Performance Report", "Content Adaptation", "Campaign Performance", 
                          "AI Content Recommendations", "AI Trend Predictions", "AI Content Optimization"])]
        
        for test in endpoint_tests:
            status_emoji = "✅" if test["status"] == "PASS" else "❌"
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
            
        print(f"\n🎉 ENDPOINT VALIDATION STATUS:")
        endpoint_names = [
            "Performance Report Generation",
            "Content Adaptation", 
            "Campaign Performance Tracking",
            "AI Content Recommendations",
            "AI Trend Predictions",
            "AI Content Optimization"
        ]
        
        for endpoint in endpoint_names:
            endpoint_test = next((t for t in self.test_results if endpoint in t["test"]), None)
            if endpoint_test:
                status_emoji = "✅" if endpoint_test["status"] == "PASS" else "❌"
                print(f"   {status_emoji} {endpoint}: {endpoint_test['status']}")
            else:
                print(f"   ⚠️ {endpoint}: NOT TESTED")
                
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "critical_issues": len(critical_issues)
        }
        
    async def run_endpoint_tests(self):
        """Run tests for the 6 previously failing endpoints"""
        print("🚀 STARTING 6 PREVIOUSLY FAILING ENDPOINTS TESTING")
        print("Testing endpoints that were fixed with proper request models")
        print("="*80)
        
        try:
            await self.setup_session()
            
            # Authentication
            auth_success = await self.test_user_authentication()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Create test campaign for campaign-related endpoints
            await self.create_test_campaign()
                
            # Test the 6 specific endpoints
            await self.test_performance_report_generation()
            await self.test_content_adaptation()
            await self.test_campaign_performance_tracking()
            await self.test_ai_content_recommendations()
            await self.test_ai_trend_predictions()
            await self.test_ai_content_optimization()
            
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
    tester = SocialMediaEndpointsTester()
    
    print("🎵 BIG MANN ENTERTAINMENT PLATFORM")
    print("6 Previously Failing Endpoints Testing")
    print("Testing Fixed Parameter Validation Issues")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    summary = await tester.run_endpoint_tests()
    
    if summary:
        print(f"\n🏁 TESTING COMPLETED")
        print(f"Final Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] == 100:
            print("🎉 PERFECT: All 6 endpoints are now working correctly!")
        elif summary['success_rate'] >= 80:
            print("✅ GOOD: Most endpoints are working with minor issues")
        else:
            print("⚠️ NEEDS ATTENTION: Critical issues still exist")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())