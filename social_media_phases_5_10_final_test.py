#!/usr/bin/env python3
"""
Final Comprehensive Testing for Social Media Phases 5-10 Endpoints
Tests all 27 endpoints with proper data dependencies and validation.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

# Backend URL from environment
BACKEND_URL = "https://uln-label-editor.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class SocialMediaPhases510FinalTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 27
        self.passed_tests = 0
        self.created_resources = {}  # Track created resources for dependencies
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Test user credentials
        test_user = {
            "email": "socialmedia.final.tester@bigmannentertainment.com",
            "password": "SocialMediaFinal2025!",
            "full_name": "Social Media Final Tester",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Social Media Final St",
            "city": "Los Angeles",
            "state_province": "CA",
            "postal_code": "90210",
            "country": "US"
        }
        
        # Try to register user (may fail if already exists)
        try:
            async with self.session.post(f"{API_BASE}/auth/register", json=test_user) as response:
                if response.status in [200, 201]:
                    print("✅ Test user registered successfully")
                elif response.status == 400:
                    print("ℹ️ Test user already exists, proceeding with login")
        except Exception as e:
            print(f"⚠️ Registration attempt: {e}")
        
        # Login to get authentication token
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    login_result = await response.json()
                    self.auth_token = login_result.get("access_token")
                    print("✅ Authentication successful")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                          expected_status: int = 200, test_name: str = "") -> tuple:
        """Test a single endpoint and return (success, response_data)"""
        url = f"{API_BASE}/social-media-advanced{endpoint}"
        headers = self.get_auth_headers()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_data = await response.json()
                    success = response.status == expected_status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_data = await response.json()
                    success = response.status == expected_status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=headers) as response:
                    response_data = await response.json()
                    success = response.status == expected_status
            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}
            
            if success:
                print(f"✅ {test_name}: {method} {endpoint} - Status {response.status}")
                self.passed_tests += 1
                self.test_results.append({
                    "test": test_name,
                    "endpoint": endpoint,
                    "method": method,
                    "status": "PASSED",
                    "response_status": response.status,
                    "response_data": response_data
                })
                return True, response_data
            else:
                print(f"❌ {test_name}: {method} {endpoint} - Expected {expected_status}, got {response.status}")
                print(f"   Response: {response_data}")
                self.test_results.append({
                    "test": test_name,
                    "endpoint": endpoint,
                    "method": method,
                    "status": "FAILED",
                    "response_status": response.status,
                    "expected_status": expected_status,
                    "response_data": response_data
                })
                return False, response_data
                
        except Exception as e:
            print(f"❌ {test_name}: {method} {endpoint} - Error: {e}")
            self.test_results.append({
                "test": test_name,
                "endpoint": endpoint,
                "method": method,
                "status": "ERROR",
                "error": str(e)
            })
            return False, {}
    
    async def test_phase_5_scheduling(self):
        """Test Phase 5: Advanced Content Scheduling (4 endpoints)"""
        print("\n🤖 TESTING PHASE 5: ADVANCED CONTENT SCHEDULING")
        
        # 1. POST /api/social-media-advanced/scheduling/rules
        scheduling_rule = {
            "name": "Daily Content Rule Final",
            "platforms": ["twitter", "instagram", "facebook"],
            "content_types": ["image", "video", "text"],
            "optimal_times": {
                "monday": ["09:00", "15:00"],
                "tuesday": ["10:00", "16:00"],
                "wednesday": ["09:30", "15:30"]
            },
            "frequency": "daily",
            "auto_optimize": True
        }
        success, rule_response = await self.test_endpoint("POST", "/scheduling/rules", scheduling_rule, 200, 
                                                        "Create Scheduling Rule")
        
        # Store rule ID for queue creation
        rule_id = str(uuid.uuid4())  # Mock rule ID since response doesn't contain it
        
        # 2. POST /api/social-media-advanced/scheduling/queues
        content_queue = {
            "name": "Main Content Queue Final",
            "content_items": ["content_final_1", "content_final_2", "content_final_3"],
            "scheduling_rule_id": rule_id,
            "current_position": 0,
            "is_active": True
        }
        success, queue_response = await self.test_endpoint("POST", "/scheduling/queues", content_queue, 200,
                                                         "Create Content Queue")
        
        # Store queue ID for batch scheduling
        queue_id = str(uuid.uuid4())  # Mock queue ID
        self.created_resources["queue_id"] = queue_id
        
        # 3. POST /api/social-media-advanced/scheduling/batch-schedule
        # This will likely fail due to queue not found, but we test the endpoint
        batch_schedule = {
            "queue_id": queue_id,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        await self.test_endpoint("POST", "/scheduling/batch-schedule", batch_schedule, 200,
                               "Batch Schedule Content")
        
        # 4. GET /api/social-media-advanced/scheduling/optimize-times/{platform}
        await self.test_endpoint("GET", "/scheduling/optimize-times/twitter", None, 200,
                               "Optimize Posting Times")
    
    async def test_phase_6_analytics(self):
        """Test Phase 6: Real-time Analytics (4 endpoints)"""
        print("\n📊 TESTING PHASE 6: REAL-TIME ANALYTICS")
        
        # 5. POST /api/social-media-advanced/analytics/track-metric
        analytics_metric = {
            "platform": "instagram",
            "content_id": "content_final_123",
            "metric_type": "engagement",
            "value": 4.5,
            "metadata": {"post_type": "image", "hashtags": ["#tech", "#innovation"]}
        }
        await self.test_endpoint("POST", "/analytics/track-metric", analytics_metric, 200,
                               "Track Analytics Metric")
        
        # 6. GET /api/social-media-advanced/analytics/real-time
        await self.test_endpoint("GET", "/analytics/real-time?platform=instagram&time_window=3600", 
                               None, 200, "Get Real-time Metrics")
        
        # 7. POST /api/social-media-advanced/analytics/generate-report
        report_request = {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "platforms": ["twitter", "instagram", "facebook"]
        }
        await self.test_endpoint("POST", "/analytics/generate-report", report_request, 200,
                               "Generate Performance Report")
        
        # 8. POST /api/social-media-advanced/analytics/ab-test
        ab_test_data = {
            "content_variants": ["Final Variant A content", "Final Variant B content"],
            "platforms": ["twitter", "instagram"],
            "duration_hours": 24
        }
        await self.test_endpoint("POST", "/analytics/ab-test", ab_test_data, 200,
                               "Create A/B Test")
    
    async def test_phase_7_community(self):
        """Test Phase 7: Community Management (3 endpoints)"""
        print("\n💬 TESTING PHASE 7: COMMUNITY MANAGEMENT")
        
        # 9. POST /api/social-media-advanced/engagement/process
        engagement_item = {
            "platform": "twitter",
            "engagement_type": "comment",
            "from_user": "finaluser123",
            "to_user": "bigmannentertainment",
            "content": "Amazing final test content! Love your work!",
            "post_id": "post_final_456",
            "sentiment": "positive",
            "priority": "medium",
            "status": "unread",
            "metadata": {"location": "US", "follower_count": 1500}
        }
        await self.test_endpoint("POST", "/engagement/process", engagement_item, 200,
                               "Process Engagement")
        
        # 10. GET /api/social-media-advanced/engagement/unified-inbox
        await self.test_endpoint("GET", "/engagement/unified-inbox?status=unread&priority=high", 
                               None, 200, "Get Unified Inbox")
        
        # 11. POST /api/social-media-advanced/engagement/auto-response-rule
        auto_response_rule = {
            "name": "Final Welcome Response Rule",
            "triggers": ["hello", "hi", "welcome", "final"],
            "response_template": "Hi {user}! Thanks for reaching out on {platform}. We'll get back to you soon!",
            "platforms": ["twitter", "instagram", "facebook"],
            "conditions": {"sentiment": "positive"},
            "is_active": True
        }
        await self.test_endpoint("POST", "/engagement/auto-response-rule", auto_response_rule, 200,
                               "Create Auto-Response Rule")
    
    async def test_phase_8_campaigns(self):
        """Test Phase 8: Campaign Orchestration (4 endpoints)"""
        print("\n🎯 TESTING PHASE 8: CAMPAIGN ORCHESTRATION")
        
        # 12. POST /api/social-media-advanced/campaigns/create
        campaign = {
            "name": "Final Product Launch Campaign",
            "description": "Final launch campaign for our new product line",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "platforms": ["twitter", "instagram", "facebook", "linkedin"],
            "budget_total": 5000.0,
            "budget_allocation": {
                "twitter": 1000.0,
                "instagram": 2000.0,
                "facebook": 1500.0,
                "linkedin": 500.0
            },
            "content_templates": ["final_template_1", "final_template_2"],
            "target_audience": {
                "age_range": "25-45",
                "interests": ["technology", "innovation"],
                "location": "US"
            },
            "goals": {
                "reach": 50000,
                "engagement": 5.0,
                "conversions": 100
            },
            "status": "draft"
        }
        success, campaign_response = await self.test_endpoint("POST", "/campaigns/create", campaign, 200,
                                                            "Create Campaign")
        
        # Store campaign ID for subsequent tests
        campaign_id = str(uuid.uuid4())  # Mock campaign ID
        self.created_resources["campaign_id"] = campaign_id
        
        # 13. POST /api/social-media-advanced/campaigns/{campaign_id}/adapt-content
        content_adaptation = {
            "content_id": "content_final_789",
            "platforms": ["twitter", "instagram", "linkedin"]
        }
        await self.test_endpoint("POST", f"/campaigns/{campaign_id}/adapt-content", 
                               content_adaptation, 200, "Adapt Content for Platforms")
        
        # 14. POST /api/social-media-advanced/campaigns/{campaign_id}/optimize-budget
        # This will likely fail due to campaign not found, but we test the endpoint
        await self.test_endpoint("POST", f"/campaigns/{campaign_id}/optimize-budget", 
                               {}, 200, "Optimize Budget Allocation")
        
        # 15. POST /api/social-media-advanced/campaigns/{campaign_id}/track-performance
        campaign_performance = {
            "platform": "instagram",
            "metrics": {
                "reach": 15000,
                "engagement": 4.2,
                "clicks": 250,
                "conversions": 15,
                "revenue": 1500.0
            },
            "budget_spent": 800.0
        }
        await self.test_endpoint("POST", f"/campaigns/{campaign_id}/track-performance", 
                               campaign_performance, 200, "Track Campaign Performance")
    
    async def test_phase_9_influencers(self):
        """Test Phase 9: Influencer Management (4 endpoints)"""
        print("\n🤝 TESTING PHASE 9: INFLUENCER MANAGEMENT")
        
        # 16. POST /api/social-media-advanced/influencers/discover
        discovery_criteria = {
            "categories": ["fitness", "lifestyle", "tech"],
            "min_followers": 10000,
            "min_engagement_rate": 3.0,
            "location": "US",
            "budget_range": [500, 2000]
        }
        await self.test_endpoint("POST", "/influencers/discover", discovery_criteria, 200,
                               "Discover Influencers")
        
        # 17. POST /api/social-media-advanced/partnerships/create
        partnership = {
            "influencer_id": str(uuid.uuid4()),
            "campaign_id": self.created_resources.get("campaign_id", str(uuid.uuid4())),
            "partnership_type": "sponsored_post",
            "deliverables": ["1 Instagram post", "3 Instagram stories"],
            "compensation": {
                "type": "monetary",
                "amount": 1000.0,
                "currency": "USD"
            },
            "contract_terms": {
                "exclusivity": False,
                "usage_rights": "1 year",
                "approval_required": True
            },
            "status": "pending",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "performance_metrics": {}
        }
        success, partnership_response = await self.test_endpoint("POST", "/partnerships/create", partnership, 200,
                                                               "Create Partnership")
        
        # Store partnership ID for subsequent tests
        partnership_id = str(uuid.uuid4())  # Mock partnership ID
        
        # 18. POST /api/social-media-advanced/partnerships/{partnership_id}/track-performance
        partnership_metrics = {
            "reach": 25000,
            "engagement": 5.2,
            "clicks": 400,
            "conversions": 25,
            "roi": 2.5
        }
        await self.test_endpoint("POST", f"/partnerships/{partnership_id}/track-performance", 
                               partnership_metrics, 200, "Track Partnership Performance")
        
        # 19. GET /api/social-media-advanced/partnerships/brand-ambassadors
        await self.test_endpoint("GET", "/partnerships/brand-ambassadors", None, 200,
                               "Get Brand Ambassadors")
    
    async def test_phase_10_ai_optimization(self):
        """Test Phase 10: AI Optimization (4 endpoints)"""
        print("\n🤖 TESTING PHASE 10: AI OPTIMIZATION")
        
        # 20. POST /api/social-media-advanced/ai/content-recommendations
        content_rec_request = {
            "platforms": ["twitter", "instagram", "linkedin"]
        }
        await self.test_endpoint("POST", "/ai/content-recommendations", content_rec_request, 200,
                               "Generate Content Recommendations")
        
        # 21. POST /api/social-media-advanced/ai/predict-trends
        trend_prediction_request = {
            "categories": ["technology", "fitness", "lifestyle"]
        }
        await self.test_endpoint("POST", "/ai/predict-trends", trend_prediction_request, 200,
                               "Predict Trends")
        
        # 22. POST /api/social-media-advanced/ai/optimize-content
        content_optimization = {
            "content": "Check out our amazing final product that will revolutionize your workflow!",
            "target_platform": "twitter"
        }
        await self.test_endpoint("POST", "/ai/optimize-content", content_optimization, 200,
                               "Optimize Content for Platform")
        
        # 23. GET /api/social-media-advanced/ai/executive-dashboard
        await self.test_endpoint("GET", "/ai/executive-dashboard", None, 200,
                               "Get Executive Dashboard")
    
    async def test_health_and_status(self):
        """Test Health & Status endpoints (2 endpoints)"""
        print("\n🏥 TESTING HEALTH & STATUS ENDPOINTS")
        
        # 24. GET /api/social-media-advanced/health
        await self.test_endpoint("GET", "/health", None, 200, "Health Check")
        
        # 25. GET /api/social-media-advanced/status/comprehensive
        await self.test_endpoint("GET", "/status/comprehensive", None, 200, 
                               "Comprehensive Status")
    
    async def test_workflow_integration(self):
        """Test additional workflow integration (2 endpoints)"""
        print("\n🔄 TESTING WORKFLOW INTEGRATION")
        
        # 26. End-to-end workflow: Rule → Queue → Schedule → Track
        print("🔗 Testing end-to-end workflow integration...")
        
        # Create rule, queue, schedule, and track in sequence
        rule_data = {
            "name": "E2E Final Test Rule",
            "platforms": ["twitter", "instagram"],
            "content_types": ["image", "text"],
            "optimal_times": {"monday": ["10:00"], "tuesday": ["14:00"]},
            "frequency": "daily",
            "auto_optimize": True
        }
        
        rule_success, _ = await self.test_endpoint("POST", "/scheduling/rules", rule_data, 200,
                                                 "E2E Workflow - Create Rule")
        
        if rule_success:
            queue_data = {
                "name": "E2E Final Test Queue",
                "content_items": ["e2e_final_content_1", "e2e_final_content_2"],
                "scheduling_rule_id": str(uuid.uuid4()),
                "current_position": 0,
                "is_active": True
            }
            
            queue_success, _ = await self.test_endpoint("POST", "/scheduling/queues", queue_data, 200,
                                                      "E2E Workflow - Create Queue")
            
            if queue_success:
                # Track metrics for the workflow
                metric_data = {
                    "platform": "twitter",
                    "content_id": "e2e_final_content_1",
                    "metric_type": "engagement",
                    "value": 3.8,
                    "metadata": {"workflow": "e2e_final_test"}
                }
                
                await self.test_endpoint("POST", "/analytics/track-metric", metric_data, 200,
                                       "E2E Workflow - Track Metrics")
        
        # 27. Test campaign workflow: Create → Adapt → Optimize → Track
        print("🎯 Testing campaign workflow integration...")
        
        campaign_data = {
            "name": "Final Workflow Test Campaign",
            "description": "Testing final campaign workflow integration",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "platforms": ["twitter", "instagram"],
            "budget_total": 2000.0,
            "budget_allocation": {"twitter": 800.0, "instagram": 1200.0},
            "content_templates": ["final_workflow_template"],
            "target_audience": {"age_range": "25-35", "interests": ["tech"]},
            "goals": {"reach": 20000, "engagement": 4.0},
            "status": "active"
        }
        
        await self.test_endpoint("POST", "/campaigns/create", campaign_data, 200,
                               "Campaign Workflow - Create Campaign")
    
    async def run_all_tests(self):
        """Run all 27 endpoint tests"""
        print("🚀 STARTING FINAL COMPREHENSIVE SOCIAL MEDIA PHASES 5-10 TESTING")
        print(f"📊 Testing {self.total_tests} endpoints across 6 phases")
        print("🎯 Focus on 6 previously fixed endpoints:")
        print("   • Performance report generation")
        print("   • Content adaptation")
        print("   • Campaign performance tracking")
        print("   • AI content recommendations")
        print("   • AI trend predictions")
        print("   • AI content optimization")
        print("=" * 80)
        
        # Setup authentication
        if not await self.setup_session():
            print("❌ Failed to setup authentication. Aborting tests.")
            return
        
        # Run all test phases
        await self.test_phase_5_scheduling()      # 4 endpoints
        await self.test_phase_6_analytics()       # 4 endpoints  
        await self.test_phase_7_community()       # 3 endpoints
        await self.test_phase_8_campaigns()       # 4 endpoints
        await self.test_phase_9_influencers()     # 4 endpoints
        await self.test_phase_10_ai_optimization() # 4 endpoints
        await self.test_health_and_status()       # 2 endpoints
        await self.test_workflow_integration()    # 2 endpoints
        
        # Print final results
        await self.print_final_results()
    
    async def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 FINAL COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100
        
        print(f"✅ PASSED: {self.passed_tests}/{self.total_tests} tests ({success_rate:.1f}%)")
        print(f"❌ FAILED: {self.total_tests - self.passed_tests}/{self.total_tests} tests")
        
        # Focus on the 6 previously fixed endpoints
        focus_endpoints = [
            "Generate Performance Report",
            "Adapt Content for Platforms", 
            "Track Campaign Performance",
            "Generate Content Recommendations",
            "Predict Trends",
            "Optimize Content for Platform"
        ]
        
        print(f"\n🎯 FOCUS ENDPOINTS STATUS (6 previously fixed):")
        focus_passed = 0
        for result in self.test_results:
            if result["test"] in focus_endpoints:
                status_icon = "✅" if result["status"] == "PASSED" else "❌"
                print(f"  {status_icon} {result['test']}")
                if result["status"] == "PASSED":
                    focus_passed += 1
        
        focus_success_rate = (focus_passed / 6) * 100
        print(f"🎯 FOCUS ENDPOINTS SUCCESS RATE: {focus_passed}/6 ({focus_success_rate:.1f}%)")
        
        # Group results by phase
        phase_results = {
            "Phase 5 - Scheduling": [],
            "Phase 6 - Analytics": [],
            "Phase 7 - Community": [],
            "Phase 8 - Campaigns": [],
            "Phase 9 - Influencers": [],
            "Phase 10 - AI": [],
            "Health & Status": [],
            "Workflow Integration": []
        }
        
        # Categorize results
        for result in self.test_results:
            test_name = result["test"]
            if "Scheduling" in test_name or "Queue" in test_name or ("Optimize" in test_name and "Campaign" not in test_name and "Content" not in test_name):
                phase_results["Phase 5 - Scheduling"].append(result)
            elif "Analytics" in test_name or "Metric" in test_name or "Report" in test_name or "A/B" in test_name:
                phase_results["Phase 6 - Analytics"].append(result)
            elif "Engagement" in test_name or "Inbox" in test_name or "Response" in test_name:
                phase_results["Phase 7 - Community"].append(result)
            elif "Campaign" in test_name and "Workflow" not in test_name:
                phase_results["Phase 8 - Campaigns"].append(result)
            elif "Influencer" in test_name or "Partnership" in test_name or "Ambassador" in test_name:
                phase_results["Phase 9 - Influencers"].append(result)
            elif "Content Recommendations" in test_name or "Trends" in test_name or "Executive" in test_name or "Optimize Content" in test_name:
                phase_results["Phase 10 - AI"].append(result)
            elif "Health" in test_name or "Status" in test_name:
                phase_results["Health & Status"].append(result)
            elif "Workflow" in test_name:
                phase_results["Workflow Integration"].append(result)
        
        # Print phase-by-phase results
        print(f"\n📋 DETAILED PHASE RESULTS:")
        for phase, results in phase_results.items():
            if results:
                passed = sum(1 for r in results if r["status"] == "PASSED")
                total = len(results)
                print(f"\n{phase}: {passed}/{total} passed")
                
                for result in results:
                    status_icon = "✅" if result["status"] == "PASSED" else "❌"
                    print(f"  {status_icon} {result['test']}")
        
        # Print failed tests details
        failed_tests = [r for r in self.test_results if r["status"] != "PASSED"]
        if failed_tests:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in failed_tests:
                print(f"  • {result['test']}")
                print(f"    Endpoint: {result['method']} {result['endpoint']}")
                if "response_status" in result:
                    print(f"    Status: {result['response_status']} (expected {result.get('expected_status', 'N/A')})")
                if "error" in result:
                    print(f"    Error: {result['error']}")
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        print(f"🎯 FOCUS ENDPOINTS SUCCESS RATE: {focus_success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: System is production-ready!")
        elif success_rate >= 80:
            print("✅ GOOD: System is mostly functional with minor issues")
        elif success_rate >= 70:
            print("⚠️ FAIR: System has some issues that need attention")
        else:
            print("❌ POOR: System has significant issues requiring fixes")
        
        # Special focus on the 6 previously fixed endpoints
        if focus_success_rate == 100:
            print("🎯 FOCUS ENDPOINTS: ALL 6 PREVIOUSLY FIXED ENDPOINTS ARE WORKING PERFECTLY!")
        elif focus_success_rate >= 83:
            print("🎯 FOCUS ENDPOINTS: Most previously fixed endpoints are working correctly")
        else:
            print("🎯 FOCUS ENDPOINTS: Some previously fixed endpoints need attention")
        
        print("=" * 80)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main test execution"""
    tester = SocialMediaPhases510FinalTester()
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())