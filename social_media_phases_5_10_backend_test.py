#!/usr/bin/env python3
"""
Social Media Phases 5-10 Backend Testing
Comprehensive testing of newly implemented Social Media Phases 5-10 endpoints

This test suite covers:
1. PHASE 5 - Advanced Content Scheduling endpoints
2. PHASE 6 - Real-time Analytics endpoints  
3. PHASE 7 - Community Management endpoints
4. PHASE 8 - Campaign Orchestration endpoints
5. PHASE 9 - Influencer Management endpoints
6. PHASE 10 - AI Optimization endpoints
7. Status and health endpoints
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
BACKEND_URL = "https://content-license-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class SocialMediaPhases510Tester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "social.media.tester@bigmannentertainment.com"
        self.test_user_password = "SocialMedia2025!"
        self.test_results = []
        
        # Test data storage
        self.scheduling_rule_id = None
        self.content_queue_id = None
        self.campaign_id = None
        self.partnership_id = None
        
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
        """Test user registration and authentication for social media testing"""
        print("\n🔐 TESTING USER AUTHENTICATION FOR SOCIAL MEDIA PHASES 5-10")
        
        # Test user registration
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": "Social Media Tester",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Social Media Street",
            "city": "Digital City",
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
        
    async def test_phase5_advanced_scheduling(self):
        """Test PHASE 5 - Advanced Content Scheduling endpoints"""
        print("\n📅 TESTING PHASE 5 - ADVANCED CONTENT SCHEDULING")
        
        # Test 1: Create Scheduling Rule
        scheduling_rule_data = {
            "name": "Hip-Hop Content Schedule",
            "platforms": ["instagram", "twitter", "tiktok"],
            "content_types": ["image", "video", "text"],
            "optimal_times": {
                "monday": ["09:00", "15:00", "19:00"],
                "tuesday": ["10:00", "14:00", "18:00"],
                "wednesday": ["09:30", "13:30", "17:30"],
                "thursday": ["08:30", "12:30", "16:30"],
                "friday": ["11:00", "15:00", "19:00"],
                "saturday": ["10:00", "14:00", "20:00"],
                "sunday": ["12:00", "16:00", "18:00"]
            },
            "frequency": "daily",
            "auto_optimize": True
        }
        
        response = await self.make_request("POST", "/social-media-advanced/scheduling/rules", scheduling_rule_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.scheduling_rule_id = response["data"].get("rule_id")
            self.log_test("Create Scheduling Rule", "PASS", f"Rule created with ID: {self.scheduling_rule_id}", response["data"])
        else:
            self.log_test("Create Scheduling Rule", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 2: Create Content Queue
        content_queue_data = {
            "name": "Big Mann Entertainment Queue",
            "content_items": ["content_001", "content_002", "content_003", "content_004"],
            "scheduling_rule_id": self.scheduling_rule_id or "test_rule_id",
            "current_position": 0,
            "is_active": True
        }
        
        response = await self.make_request("POST", "/social-media-advanced/scheduling/queues", content_queue_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.content_queue_id = response["data"].get("queue_id")
            self.log_test("Create Content Queue", "PASS", f"Queue created with ID: {self.content_queue_id}", response["data"])
        else:
            self.log_test("Create Content Queue", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 3: Batch Schedule Content
        queue_id = self.content_queue_id or "test_queue_id"
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        batch_schedule_data = {
            "queue_id": queue_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = await self.make_request("POST", "/social-media-advanced/scheduling/batch-schedule", batch_schedule_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Batch Schedule Content", "PASS", f"Scheduled {response['data'].get('scheduled_posts', 0)} posts", response["data"])
        else:
            self.log_test("Batch Schedule Content", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 4: Optimize Posting Times
        response = await self.make_request("GET", "/social-media-advanced/scheduling/optimize-times/instagram")
        
        if response["status"] == 200 and response["data"].get("success"):
            optimal_times = response["data"].get("optimal_times", {})
            self.log_test("Optimize Posting Times", "PASS", f"Retrieved optimal times for {len(optimal_times)} days", response["data"])
        else:
            self.log_test("Optimize Posting Times", "FAIL", f"Status: {response['status']}", response["data"])
            
    async def test_phase6_real_time_analytics(self):
        """Test PHASE 6 - Real-time Analytics endpoints"""
        print("\n📊 TESTING PHASE 6 - REAL-TIME ANALYTICS")
        
        # Test 1: Track Analytics Metric
        analytics_metric_data = {
            "platform": "instagram",
            "content_id": "content_001",
            "metric_type": "engagement",
            "value": 85.5,
            "metadata": {
                "likes": 120,
                "comments": 15,
                "shares": 8
            }
        }
        
        response = await self.make_request("POST", "/social-media-advanced/analytics/track-metric", analytics_metric_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Track Analytics Metric", "PASS", "Metric tracked successfully", response["data"])
        else:
            self.log_test("Track Analytics Metric", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 2: Get Real-time Metrics
        response = await self.make_request("GET", "/social-media-advanced/analytics/real-time", {"time_window": 3600})
        
        if response["status"] == 200 and response["data"].get("success"):
            summary = response["data"].get("summary", {})
            self.log_test("Get Real-time Metrics", "PASS", f"Retrieved {summary.get('total_metrics', 0)} metrics", response["data"])
        else:
            self.log_test("Get Real-time Metrics", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 3: Generate Performance Report
        report_data = {
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "platforms": ["instagram", "twitter", "tiktok"]
        }
        
        response = await self.make_request("POST", "/social-media-advanced/analytics/generate-report", report_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Generate Performance Report", "PASS", "Performance report generated", response["data"])
        else:
            self.log_test("Generate Performance Report", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 4: Create A/B Test
        ab_test_data = {
            "content_variants": ["variant_a", "variant_b"],
            "platforms": ["instagram", "twitter"],
            "duration_hours": 24
        }
        
        response = await self.make_request("POST", "/social-media-advanced/analytics/ab-test", ab_test_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Create A/B Test", "PASS", f"A/B test created for {ab_test_data['duration_hours']} hours", response["data"])
        else:
            self.log_test("Create A/B Test", "FAIL", f"Status: {response['status']}", response["data"])
            
    async def test_phase7_community_management(self):
        """Test PHASE 7 - Community Management endpoints"""
        print("\n💬 TESTING PHASE 7 - COMMUNITY MANAGEMENT")
        
        # Test 1: Process Engagement
        engagement_data = {
            "platform": "instagram",
            "engagement_type": "comment",
            "from_user": "fan_user_123",
            "to_user": "bigmannentertainment",
            "content": "Love this new track! When is the next album dropping?",
            "post_id": "post_12345",
            "sentiment": "positive",
            "priority": "medium",
            "status": "unread",
            "metadata": {
                "follower_count": 1500,
                "verified": False
            }
        }
        
        response = await self.make_request("POST", "/social-media-advanced/engagement/process", engagement_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Process Engagement", "PASS", f"Engagement processed with {response['data'].get('sentiment')} sentiment", response["data"])
        else:
            self.log_test("Process Engagement", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 2: Get Unified Inbox
        response = await self.make_request("GET", "/social-media-advanced/engagement/unified-inbox")
        
        if response["status"] == 200 and response["data"].get("success"):
            total_engagements = response["data"].get("total_engagements", 0)
            platform_summary = response["data"].get("platform_summary", {})
            self.log_test("Get Unified Inbox", "PASS", f"Retrieved {total_engagements} engagements across {len(platform_summary)} platforms", response["data"])
        else:
            self.log_test("Get Unified Inbox", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 3: Create Auto Response Rule
        auto_response_data = {
            "name": "Album Release Response",
            "triggers": ["album", "release", "new music", "when"],
            "response_template": "Thanks for your interest! Stay tuned to our social media for the latest updates on new releases. 🎵",
            "platforms": ["instagram", "twitter", "facebook"],
            "conditions": {
                "sentiment": "positive",
                "follower_threshold": 100
            },
            "is_active": True
        }
        
        response = await self.make_request("POST", "/social-media-advanced/engagement/auto-response-rule", auto_response_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Create Auto Response Rule", "PASS", "Auto-response rule created successfully", response["data"])
        else:
            self.log_test("Create Auto Response Rule", "FAIL", f"Status: {response['status']}", response["data"])
            
    async def test_phase8_campaign_orchestration(self):
        """Test PHASE 8 - Campaign Orchestration endpoints"""
        print("\n🎯 TESTING PHASE 8 - CAMPAIGN ORCHESTRATION")
        
        # Test 1: Create Campaign
        campaign_data = {
            "name": "Big Mann Summer Tour 2025",
            "description": "Promoting the upcoming summer tour with new album release",
            "platforms": ["instagram", "twitter", "tiktok", "facebook"],
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "budget_total": 5000.0,
            "budget_allocation": {
                "instagram": 2000.0,
                "twitter": 1000.0,
                "tiktok": 1500.0,
                "facebook": 500.0
            },
            "content_templates": [
                "summer_tour_announcement",
                "new_album_teaser",
                "behind_the_scenes"
            ],
            "target_audience": {
                "age_range": "18-35",
                "interests": ["hip-hop", "music", "concerts"],
                "locations": ["US", "CA"]
            },
            "goals": {
                "reach": 100000,
                "engagement": 5.0,
                "ticket_sales": 500
            },
            "status": "active"
        }
        
        response = await self.make_request("POST", "/social-media-advanced/campaigns/create", campaign_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.campaign_id = response["data"].get("campaign_id")
            self.log_test("Create Campaign", "PASS", f"Campaign created with ID: {self.campaign_id}", response["data"])
        else:
            self.log_test("Create Campaign", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 2: Adapt Content for Platforms
        adapt_content_data = {
            "content_id": "summer_tour_announcement",
            "platforms": ["instagram", "twitter", "tiktok"]
        }
        
        campaign_id = self.campaign_id or "test_campaign_id"
        response = await self.make_request("POST", f"/social-media-advanced/campaigns/{campaign_id}/adapt-content", adapt_content_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            adaptations = response["data"].get("adaptations", {})
            self.log_test("Adapt Content for Platforms", "PASS", f"Content adapted for {len(adaptations)} platforms", response["data"])
        else:
            self.log_test("Adapt Content for Platforms", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 3: Optimize Budget Allocation
        response = await self.make_request("POST", f"/social-media-advanced/campaigns/{campaign_id}/optimize-budget")
        
        if response["status"] == 200 and response["data"].get("success"):
            optimized_allocation = response["data"].get("optimized_allocation", {})
            self.log_test("Optimize Budget Allocation", "PASS", f"Budget optimized across {len(optimized_allocation)} platforms", response["data"])
        else:
            self.log_test("Optimize Budget Allocation", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 4: Track Campaign Performance
        performance_data = {
            "platform": "instagram",
            "metrics": {
                "impressions": 15000,
                "clicks": 450,
                "conversions": 25,
                "engagement_rate": 3.2
            },
            "budget_spent": 250.0
        }
        
        response = await self.make_request("POST", f"/social-media-advanced/campaigns/{campaign_id}/track-performance", performance_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Track Campaign Performance", "PASS", "Campaign performance tracked successfully", response["data"])
        else:
            self.log_test("Track Campaign Performance", "FAIL", f"Status: {response['status']}", response["data"])
            
    async def test_phase9_influencer_management(self):
        """Test PHASE 9 - Influencer Management endpoints"""
        print("\n🌟 TESTING PHASE 9 - INFLUENCER MANAGEMENT")
        
        # Test 1: Discover Influencers
        discovery_criteria = {
            "platforms": ["instagram", "tiktok"],
            "follower_range": {"min": 10000, "max": 500000},
            "engagement_rate": {"min": 2.0},
            "categories": ["music", "hip-hop", "entertainment"],
            "location": "US",
            "age_range": "18-35"
        }
        
        response = await self.make_request("POST", "/social-media-advanced/influencers/discover", discovery_criteria)
        
        if response["status"] == 200 and response["data"].get("success"):
            influencers = response["data"].get("influencers", [])
            self.log_test("Discover Influencers", "PASS", f"Found {len(influencers)} matching influencers", response["data"])
        else:
            self.log_test("Discover Influencers", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 2: Create Partnership
        partnership_data = {
            "influencer_id": "influencer_12345",
            "campaign_id": self.campaign_id or "test_campaign_id",
            "partnership_type": "sponsored_post",
            "deliverables": [
                "1 Instagram post",
                "3 Instagram stories",
                "1 TikTok video"
            ],
            "compensation": {
                "type": "monetary",
                "amount": 1500.0,
                "currency": "USD"
            },
            "contract_terms": {
                "hashtags": ["#BigMannEntertainment", "#SummerTour2025"],
                "mentions": ["@bigmannentertainment"],
                "content_approval": True,
                "exclusivity_period": 30
            },
            "status": "pending",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "performance_metrics": {}
        }
        
        response = await self.make_request("POST", "/social-media-advanced/partnerships/create", partnership_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.partnership_id = response["data"].get("partnership_id")
            self.log_test("Create Partnership", "PASS", f"Partnership created with ID: {self.partnership_id}", response["data"])
        else:
            self.log_test("Create Partnership", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 3: Track Partnership Performance
        partnership_metrics = {
            "reach": 45000,
            "impressions": 67000,
            "engagement": 2850,
            "clicks": 320,
            "conversions": 18,
            "engagement_rate": 4.25,
            "cost_per_engagement": 0.53
        }
        
        partnership_id = self.partnership_id or "test_partnership_id"
        response = await self.make_request("POST", f"/social-media-advanced/partnerships/{partnership_id}/track-performance", partnership_metrics)
        
        if response["status"] == 200 and response["data"].get("success"):
            self.log_test("Track Partnership Performance", "PASS", "Partnership performance tracked successfully", response["data"])
        else:
            self.log_test("Track Partnership Performance", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 4: Get Brand Ambassadors
        response = await self.make_request("GET", "/social-media-advanced/partnerships/brand-ambassadors")
        
        if response["status"] == 200 and response["data"].get("success"):
            ambassadors = response["data"].get("ambassadors", [])
            self.log_test("Get Brand Ambassadors", "PASS", f"Retrieved {len(ambassadors)} brand ambassadors", response["data"])
        else:
            self.log_test("Get Brand Ambassadors", "FAIL", f"Status: {response['status']}", response["data"])
            
    async def test_phase10_ai_optimization(self):
        """Test PHASE 10 - AI Optimization endpoints"""
        print("\n🤖 TESTING PHASE 10 - AI OPTIMIZATION")
        
        # Test 1: Generate Content Recommendations
        platforms = ["instagram", "twitter", "tiktok"]
        
        response = await self.make_request("POST", "/social-media-advanced/ai/content-recommendations", {"platforms": platforms})
        
        if response["status"] == 200 and response["data"].get("success"):
            recommendations = response["data"].get("recommendations", [])
            self.log_test("Generate Content Recommendations", "PASS", f"Generated {len(recommendations)} content recommendations", response["data"])
        else:
            self.log_test("Generate Content Recommendations", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 2: Predict Trends
        trend_categories = ["hip-hop", "music", "entertainment", "social-media"]
        
        response = await self.make_request("POST", "/social-media-advanced/ai/predict-trends", {"categories": trend_categories})
        
        if response["status"] == 200 and response["data"].get("success"):
            predictions = response["data"].get("predictions", [])
            self.log_test("Predict Trends", "PASS", f"Generated {len(predictions)} trend predictions", response["data"])
        else:
            self.log_test("Predict Trends", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 3: Optimize Content for Platform
        content_optimization_data = {
            "content": "Check out our new track! It's fire 🔥 Link in bio for streaming on all platforms. What do you think?",
            "target_platform": "tiktok"
        }
        
        response = await self.make_request("POST", "/social-media-advanced/ai/optimize-content", content_optimization_data)
        
        if response["status"] == 200 and response["data"].get("success"):
            optimizations = response["data"].get("optimizations", {})
            self.log_test("Optimize Content for Platform", "PASS", f"Content optimized for {content_optimization_data['target_platform']}", response["data"])
        else:
            self.log_test("Optimize Content for Platform", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 4: Generate Executive Dashboard
        response = await self.make_request("GET", "/social-media-advanced/ai/executive-dashboard")
        
        if response["status"] == 200 and response["data"].get("success"):
            dashboard = response["data"].get("dashboard", {})
            self.log_test("Generate Executive Dashboard", "PASS", "AI-powered executive dashboard generated", response["data"])
        else:
            self.log_test("Generate Executive Dashboard", "FAIL", f"Status: {response['status']}", response["data"])
            
    async def test_health_and_status_endpoints(self):
        """Test health and status endpoints"""
        print("\n🏥 TESTING HEALTH AND STATUS ENDPOINTS")
        
        # Test 1: Health Check
        response = await self.make_request("GET", "/social-media-advanced/health")
        
        if response["status"] == 200 and response["data"].get("success"):
            services = response["data"].get("services", {})
            healthy_services = [k for k, v in services.items() if v == "healthy"]
            self.log_test("Health Check", "PASS", f"{len(healthy_services)}/6 services healthy", response["data"])
        else:
            self.log_test("Health Check", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test 2: Comprehensive Status
        response = await self.make_request("GET", "/social-media-advanced/status/comprehensive")
        
        if response["status"] == 200 and response["data"].get("success"):
            status = response["data"].get("status", {})
            phases = list(status.keys())
            self.log_test("Comprehensive Status", "PASS", f"Status retrieved for {len(phases)} phases", response["data"])
        else:
            self.log_test("Comprehensive Status", "FAIL", f"Status: {response['status']}", response["data"])
            
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 SOCIAL MEDIA PHASES 5-10 - COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Skipped: {skipped_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 RESULTS BY PHASE:")
        
        phases = {
            "Phase 5 (Scheduling)": [t for t in self.test_results if "Scheduling" in t["test"] or "Queue" in t["test"] or "Batch" in t["test"] or "Optimize" in t["test"]],
            "Phase 6 (Analytics)": [t for t in self.test_results if "Analytics" in t["test"] or "Metric" in t["test"] or "Report" in t["test"] or "A/B" in t["test"]],
            "Phase 7 (Community)": [t for t in self.test_results if "Engagement" in t["test"] or "Inbox" in t["test"] or "Response" in t["test"]],
            "Phase 8 (Campaigns)": [t for t in self.test_results if "Campaign" in t["test"] or "Adapt" in t["test"] or "Budget" in t["test"]],
            "Phase 9 (Influencers)": [t for t in self.test_results if "Influencer" in t["test"] or "Partnership" in t["test"] or "Ambassador" in t["test"]],
            "Phase 10 (AI)": [t for t in self.test_results if "Content Recommendations" in t["test"] or "Predict" in t["test"] or "Optimize Content" in t["test"] or "Executive" in t["test"]],
            "Health/Status": [t for t in self.test_results if "Health" in t["test"] or "Status" in t["test"]]
        }
        
        for phase, tests in phases.items():
            if tests:
                phase_passed = len([t for t in tests if t["status"] == "PASS"])
                phase_total = len(tests)
                phase_rate = (phase_passed / phase_total * 100) if phase_total > 0 else 0
                print(f"   {phase}: {phase_passed}/{phase_total} ({phase_rate:.1f}%)")
                
        print(f"\n📋 CRITICAL ISSUES FOUND:")
        critical_issues = [t for t in self.test_results if t["status"] == "FAIL"]
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No critical issues found!")
            
        print(f"\n🎉 ENDPOINT STATUS:")
        endpoint_categories = [
            "Advanced Content Scheduling",
            "Real-time Analytics", 
            "Community Management",
            "Campaign Orchestration",
            "Influencer Management",
            "AI Optimization",
            "Health & Status"
        ]
        
        for category in endpoint_categories:
            category_tests = [t for t in self.test_results if any(keyword in t["test"] for keyword in category.split())]
            if category_tests:
                category_passed = len([t for t in category_tests if t["status"] == "PASS"])
                category_total = len(category_tests)
                status_emoji = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
                print(f"   {status_emoji} {category}: {category_passed}/{category_total}")
                
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": success_rate,
            "critical_issues": len(critical_issues)
        }
        
    async def run_comprehensive_tests(self):
        """Run all comprehensive tests for Social Media Phases 5-10"""
        print("🚀 STARTING SOCIAL MEDIA PHASES 5-10 BACKEND TESTING")
        print("Testing newly implemented Social Media Advanced Features")
        print("="*80)
        
        try:
            await self.setup_session()
            
            # Authentication
            auth_success = await self.test_user_authentication()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Test all phases
            await self.test_phase5_advanced_scheduling()
            await self.test_phase6_real_time_analytics()
            await self.test_phase7_community_management()
            await self.test_phase8_campaign_orchestration()
            await self.test_phase9_influencer_management()
            await self.test_phase10_ai_optimization()
            await self.test_health_and_status_endpoints()
            
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
    tester = SocialMediaPhases510Tester()
    
    print("🎵 BIG MANN ENTERTAINMENT PLATFORM")
    print("Social Media Phases 5-10 Backend Testing")
    print("Testing Advanced Social Media Management Features")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    summary = await tester.run_comprehensive_tests()
    
    if summary:
        print(f"\n🏁 TESTING COMPLETED")
        print(f"Final Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] >= 85:
            print("🎉 EXCELLENT: Social Media Phases 5-10 are production-ready!")
        elif summary['success_rate'] >= 70:
            print("✅ GOOD: Social Media features are functional with minor issues")
        else:
            print("⚠️ NEEDS ATTENTION: Critical issues require fixing")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())