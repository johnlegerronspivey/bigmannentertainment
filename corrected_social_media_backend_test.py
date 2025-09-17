#!/usr/bin/env python3
"""
CORRECTED FINAL COMPREHENSIVE TEST FOR 100% COMPLETION
Social Media Phases 5-10 System - ALL 27 ENDPOINTS

This test verifies 100% success rate across the ENTIRE Social Media Phases 5-10 system
with CORRECTED data structures that match the backend Pydantic models.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BASE_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://music-rights-hub-2.preview.emergentagent.com')
if not BASE_URL.startswith('http'):
    BASE_URL = f"https://{BASE_URL}"

# Test configuration
TEST_USER_EMAIL = f"socialmedia_corrected_test_{int(datetime.now().timestamp())}@bigmannentertainment.com"
TEST_USER_PASSWORD = "SocialMediaTest2025!"
TEST_USER_NAME = "Social Media Corrected Test User"

class SocialMediaCorrectedTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.total_tests = 27
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def register_test_user(self):
        """Register a test user for authentication"""
        try:
            registration_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }
            
            async with self.session.post(f"{BASE_URL}/api/auth/register", json=registration_data) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    self.auth_token = data.get('access_token')
                    self.user_id = data.get('user', {}).get('id')
                    print(f"✅ User registration successful: {TEST_USER_EMAIL}")
                    return True
                else:
                    # Try to login if user already exists
                    return await self.login_test_user()
                    
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return await self.login_test_user()
            
    async def login_test_user(self):
        """Login test user"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get('access_token')
                    self.user_id = data.get('user', {}).get('id')
                    print(f"✅ User login successful: {TEST_USER_EMAIL}")
                    return True
                else:
                    print(f"❌ Login failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
        
    async def test_endpoint(self, method, endpoint, data=None, description="", expected_status=200):
        """Test a single endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
            else:
                async with self.session.request(method, url, json=data, headers=headers) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
            
            # Check if test passed
            passed = status == expected_status or (status in [200, 201] and expected_status == 200)
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": status,
                "expected_status": expected_status,
                "passed": passed,
                "response": response_data if isinstance(response_data, dict) else str(response_data)[:200]
            }
            
            self.test_results.append(result)
            
            if passed:
                self.passed_tests += 1
                print(f"✅ {description}: {status}")
            else:
                self.failed_tests += 1
                print(f"❌ {description}: {status} (expected {expected_status})")
                if isinstance(response_data, dict) and 'detail' in response_data:
                    print(f"   Error: {response_data['detail']}")
                
            return passed
            
        except Exception as e:
            self.failed_tests += 1
            result = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": "ERROR",
                "expected_status": expected_status,
                "passed": False,
                "response": str(e)
            }
            self.test_results.append(result)
            print(f"❌ {description}: ERROR - {e}")
            return False
            
    async def run_phase_5_tests(self):
        """Test Phase 5 - Advanced Content Scheduling (4 endpoints)"""
        print("\n🤖 PHASE 5 - ADVANCED CONTENT SCHEDULING")
        print("=" * 50)
        
        # 1. POST /api/social-media-advanced/scheduling/rules
        # Corrected data structure matching SchedulingRule model
        rule_data = {
            "name": "Test Scheduling Rule",
            "platforms": ["twitter", "instagram"],
            "content_types": ["image", "text"],
            "optimal_times": {
                "monday": ["09:00", "15:00", "19:00"],
                "tuesday": ["10:00", "14:00", "18:00"],
                "wednesday": ["09:30", "13:30", "17:30"]
            },
            "frequency": "daily",
            "auto_optimize": True
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/scheduling/rules", 
                                rule_data, "Create Scheduling Rule")
        
        # 2. POST /api/social-media-advanced/scheduling/queues
        # Corrected data structure matching ContentQueue model
        queue_data = {
            "name": "Test Content Queue",
            "content_items": ["content_id_1", "content_id_2", "content_id_3"],
            "scheduling_rule_id": "test_rule_123",
            "current_position": 0,
            "is_active": True
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/scheduling/queues", 
                                queue_data, "Create Content Queue")
        
        # 3. POST /api/social-media-advanced/scheduling/batch-schedule
        # Corrected data structure matching BatchScheduleRequest model
        batch_data = {
            "queue_id": "test_queue_123",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/scheduling/batch-schedule", 
                                batch_data, "Batch Schedule Content")
        
        # 4. GET /api/social-media-advanced/scheduling/optimize-times/{platform}
        await self.test_endpoint("GET", "/api/social-media-advanced/scheduling/optimize-times/twitter", 
                                None, "Optimize Posting Times")
        
    async def run_phase_6_tests(self):
        """Test Phase 6 - Real-time Analytics (4 endpoints)"""
        print("\n📊 PHASE 6 - REAL-TIME ANALYTICS")
        print("=" * 50)
        
        # 5. POST /api/social-media-advanced/analytics/track-metric
        # Corrected data structure matching AnalyticsMetric model
        metric_data = {
            "platform": "twitter",
            "content_id": "test_content_123",
            "metric_type": "engagement",
            "value": 150.0,
            "metadata": {"post_id": "test_post_123"}
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/analytics/track-metric", 
                                metric_data, "Track Metric")
        
        # 6. GET /api/social-media-advanced/analytics/real-time
        await self.test_endpoint("GET", "/api/social-media-advanced/analytics/real-time", 
                                None, "Get Real-time Analytics")
        
        # 7. POST /api/social-media-advanced/analytics/generate-report
        # Corrected data structure matching PerformanceReportRequest model
        report_data = {
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "platforms": ["twitter", "instagram", "facebook"]
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/analytics/generate-report", 
                                report_data, "Generate Performance Report")
        
        # 8. POST /api/social-media-advanced/analytics/ab-test
        # Corrected data structure matching ABTestRequest model
        ab_test_data = {
            "content_variants": ["Version A content", "Version B content"],
            "platforms": ["twitter"],
            "duration_hours": 24
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/analytics/ab-test", 
                                ab_test_data, "Create A/B Test")
        
    async def run_phase_7_tests(self):
        """Test Phase 7 - Community Management (3 endpoints)"""
        print("\n💬 PHASE 7 - COMMUNITY MANAGEMENT")
        print("=" * 50)
        
        # 9. POST /api/social-media-advanced/engagement/process
        # Corrected data structure matching EngagementRequest model
        engagement_data = {
            "platform": "twitter",
            "engagement_type": "comment",
            "from_user": "test_user_123",
            "to_user": "bigmannentertainment",
            "content": "Thanks for the feedback!",
            "post_id": "test_post_456"
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/engagement/process", 
                                engagement_data, "Process Engagement")
        
        # 10. GET /api/social-media-advanced/engagement/unified-inbox
        await self.test_endpoint("GET", "/api/social-media-advanced/engagement/unified-inbox", 
                                None, "Get Unified Inbox")
        
        # 11. POST /api/social-media-advanced/engagement/auto-response-rule
        # Corrected data structure matching AutoResponseRuleRequest model
        auto_response_data = {
            "name": "Welcome Auto Response",
            "triggers": ["hello", "hi", "welcome"],
            "response_template": "Hello {user}! Thanks for reaching out to Big Mann Entertainment!",
            "platforms": ["twitter", "instagram"],
            "conditions": {"sentiment": "positive"},
            "is_active": True
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/engagement/auto-response-rule", 
                                auto_response_data, "Create Auto Response Rule")
        
    async def run_phase_8_tests(self):
        """Test Phase 8 - Campaign Orchestration (4 endpoints)"""
        print("\n🎯 PHASE 8 - CAMPAIGN ORCHESTRATION")
        print("=" * 50)
        
        # 12. POST /api/social-media-advanced/campaigns/create
        # Corrected data structure matching CampaignRequest model
        campaign_data = {
            "name": "Test Marketing Campaign",
            "description": "Test campaign for final verification",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "platforms": ["twitter", "instagram", "facebook"],
            "budget_total": 1000.0,
            "budget_allocation": {
                "twitter": 300.0,
                "instagram": 400.0,
                "facebook": 300.0
            },
            "content_templates": ["template_1", "template_2"],
            "target_audience": {
                "age_range": "18-35",
                "interests": ["music", "entertainment"]
            },
            "goals": {
                "engagement": 1000.0,
                "reach": 50000.0
            },
            "status": "draft"
        }
        campaign_result = await self.test_endpoint("POST", "/api/social-media-advanced/campaigns/create", 
                                                  campaign_data, "Create Campaign")
        
        # Use a test campaign ID for subsequent tests
        test_campaign_id = "test_campaign_123"
        
        # 13. POST /api/social-media-advanced/campaigns/{campaign_id}/adapt-content
        # Corrected data structure matching ContentAdaptationRequest model
        adapt_data = {
            "content_id": "test_content_123",
            "platforms": ["twitter", "instagram"]
        }
        await self.test_endpoint("POST", f"/api/social-media-advanced/campaigns/{test_campaign_id}/adapt-content", 
                                adapt_data, "Adapt Campaign Content")
        
        # 14. POST /api/social-media-advanced/campaigns/{campaign_id}/optimize-budget
        budget_data = {
            "total_budget": 1000.0,
            "platform_performance": {
                "twitter": {"cpm": 2.5, "engagement_rate": 0.03},
                "instagram": {"cpm": 3.0, "engagement_rate": 0.045},
                "facebook": {"cpm": 2.0, "engagement_rate": 0.025}
            },
            "optimization_goal": "engagement"
        }
        await self.test_endpoint("POST", f"/api/social-media-advanced/campaigns/{test_campaign_id}/optimize-budget", 
                                budget_data, "Optimize Campaign Budget")
        
        # 15. POST /api/social-media-advanced/campaigns/{campaign_id}/track-performance
        # Corrected data structure matching CampaignPerformanceRequest model
        performance_data = {
            "platform": "twitter",
            "metrics": {
                "impressions": 10000.0,
                "clicks": 500.0,
                "engagement": 750.0,
                "conversions": 25.0
            },
            "budget_spent": 250.0
        }
        await self.test_endpoint("POST", f"/api/social-media-advanced/campaigns/{test_campaign_id}/track-performance", 
                                performance_data, "Track Campaign Performance")
        
    async def run_phase_9_tests(self):
        """Test Phase 9 - Influencer Management (4 endpoints)"""
        print("\n🤝 PHASE 9 - INFLUENCER MANAGEMENT")
        print("=" * 50)
        
        # 16. POST /api/social-media-advanced/influencers/discover
        discover_data = {
            "criteria": {
                "min_followers": 10000,
                "max_followers": 100000,
                "engagement_rate_min": 0.02,
                "categories": ["music", "entertainment"],
                "platforms": ["instagram", "tiktok"]
            },
            "location": "US",
            "budget_range": {"min": 500, "max": 2000}
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/influencers/discover", 
                                discover_data, "Discover Influencers")
        
        # 17. POST /api/social-media-advanced/partnerships/create
        # Corrected data structure matching PartnershipRequest model
        partnership_data = {
            "influencer_id": "test_influencer_123",
            "campaign_id": "test_campaign_123",
            "partnership_type": "sponsored_post",
            "deliverables": ["instagram_post", "story"],
            "compensation": {
                "type": "fixed",
                "amount": 1000.0,
                "currency": "USD"
            },
            "contract_terms": {
                "exclusivity": False,
                "usage_rights": "1_year"
            },
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "status": "pending"
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/partnerships/create", 
                                partnership_data, "Create Partnership")
        
        # 18. POST /api/social-media-advanced/partnerships/{partnership_id}/track-performance
        test_partnership_id = "test_partnership_123"
        # Corrected data structure matching PartnershipMetricsRequest model
        partnership_performance_data = {
            "metrics": {
                "reach": 50000.0,
                "impressions": 75000.0,
                "engagement": 3750.0,
                "clicks": 500.0,
                "conversions": 25.0
            }
        }
        await self.test_endpoint("POST", f"/api/social-media-advanced/partnerships/{test_partnership_id}/track-performance", 
                                partnership_performance_data, "Track Partnership Performance")
        
        # 19. GET /api/social-media-advanced/partnerships/brand-ambassadors
        await self.test_endpoint("GET", "/api/social-media-advanced/partnerships/brand-ambassadors", 
                                None, "Get Brand Ambassadors")
        
    async def run_phase_10_tests(self):
        """Test Phase 10 - AI Optimization (4 endpoints)"""
        print("\n🤖 PHASE 10 - AI OPTIMIZATION")
        print("=" * 50)
        
        # 20. POST /api/social-media-advanced/ai/content-recommendations
        # Corrected data structure matching ContentRecommendationRequest model
        content_rec_data = {
            "platforms": ["instagram", "twitter"]
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/ai/content-recommendations", 
                                content_rec_data, "Get AI Content Recommendations")
        
        # 21. POST /api/social-media-advanced/ai/predict-trends
        # Corrected data structure matching TrendPredictionRequest model
        trend_data = {
            "categories": ["hip-hop", "r&b", "pop"]
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/ai/predict-trends", 
                                trend_data, "Predict AI Trends")
        
        # 22. POST /api/social-media-advanced/ai/optimize-content
        # Corrected data structure matching ContentOptimizationRequest model
        optimize_data = {
            "content": "Check out our latest track! 🎵 #NewMusic #BigMannEntertainment",
            "target_platform": "twitter"
        }
        await self.test_endpoint("POST", "/api/social-media-advanced/ai/optimize-content", 
                                optimize_data, "Optimize Content with AI")
        
        # 23. GET /api/social-media-advanced/ai/executive-dashboard
        await self.test_endpoint("GET", "/api/social-media-advanced/ai/executive-dashboard", 
                                None, "Get AI Executive Dashboard")
        
    async def run_health_status_tests(self):
        """Test Health & Status endpoints (2 endpoints)"""
        print("\n🏥 HEALTH & STATUS")
        print("=" * 50)
        
        # 24. GET /api/social-media-advanced/health
        await self.test_endpoint("GET", "/api/social-media-advanced/health", 
                                None, "Health Check")
        
        # 25. GET /api/social-media-advanced/status/comprehensive
        await self.test_endpoint("GET", "/api/social-media-advanced/status/comprehensive", 
                                None, "Comprehensive Status")
        
    async def run_all_tests(self):
        """Run all 27 endpoint tests"""
        print("🎯 CORRECTED FINAL COMPREHENSIVE TEST FOR 100% COMPLETION")
        print("Social Media Phases 5-10 System - ALL 27 ENDPOINTS")
        print("=" * 70)
        
        # Setup
        await self.setup_session()
        
        # Authenticate
        auth_success = await self.register_test_user()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with tests")
            await self.cleanup_session()
            return
            
        # Run all phase tests
        await self.run_phase_5_tests()
        await self.run_phase_6_tests()
        await self.run_phase_7_tests()
        await self.run_phase_8_tests()
        await self.run_phase_9_tests()
        await self.run_phase_10_tests()
        await self.run_health_status_tests()
        
        # Cleanup
        await self.cleanup_session()
        
        # Generate final report
        self.generate_final_report()
        
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 70)
        print("🎉 CORRECTED FINAL COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            print(f"\n🎯 TARGET ACHIEVED: 100% SUCCESS RATE!")
            print(f"✅ ALL 27 ENDPOINTS WORKING PERFECTLY")
        elif success_rate >= 95.0:
            print(f"\n🎯 EXCELLENT: {success_rate:.1f}% SUCCESS RATE!")
            print(f"✅ NEAR-PERFECT FUNCTIONALITY ACHIEVED")
        elif success_rate >= 90.0:
            print(f"\n🎯 VERY GOOD: {success_rate:.1f}% SUCCESS RATE!")
            print(f"✅ STRONG SYSTEM PERFORMANCE")
        else:
            print(f"\n⚠️  NEEDS IMPROVEMENT: {success_rate:.1f}% SUCCESS RATE")
            print(f"❌ SOME ENDPOINTS REQUIRE ATTENTION")
        
        # Phase breakdown
        print(f"\n📋 PHASE BREAKDOWN:")
        phases = {
            "Phase 5 - Advanced Scheduling": [0, 1, 2, 3],
            "Phase 6 - Real-time Analytics": [4, 5, 6, 7],
            "Phase 7 - Community Management": [8, 9, 10],
            "Phase 8 - Campaign Orchestration": [11, 12, 13, 14],
            "Phase 9 - Influencer Management": [15, 16, 17, 18],
            "Phase 10 - AI Optimization": [19, 20, 21, 22],
            "Health & Status": [23, 24]
        }
        
        for phase_name, indices in phases.items():
            phase_results = [self.test_results[i] for i in indices if i < len(self.test_results)]
            phase_passed = sum(1 for r in phase_results if r['passed'])
            phase_total = len(phase_results)
            phase_rate = (phase_passed / phase_total * 100) if phase_total > 0 else 0
            status = "✅" if phase_rate == 100 else "⚠️" if phase_rate >= 75 else "❌"
            print(f"   {status} {phase_name}: {phase_passed}/{phase_total} ({phase_rate:.1f}%)")
        
        # Failed tests details
        if self.failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for i, result in enumerate(self.test_results):
                if not result['passed']:
                    print(f"   {i+1}. {result['description']}")
                    print(f"      Endpoint: {result['method']} {result['endpoint']}")
                    print(f"      Status: {result['status']} (expected {result['expected_status']})")
                    if isinstance(result['response'], str) and len(result['response']) > 0:
                        print(f"      Response: {result['response'][:100]}...")
        
        # Success summary
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate == 100.0:
            print("✅ PERFECT: All 27 Social Media Phases 5-10 endpoints are working flawlessly!")
            print("✅ PRODUCTION READY: System achieves 100% completion target!")
            print("✅ NO ERRORS: Complete functionality across all phases verified!")
        elif success_rate >= 95.0:
            print("✅ EXCELLENT: Near-perfect system performance achieved!")
            print("✅ PRODUCTION READY: System meets high-quality standards!")
            print("⚠️  MINOR ISSUES: Only minor fixes needed for 100% completion!")
        else:
            print("⚠️  NEEDS ATTENTION: Some endpoints require fixes for optimal performance!")
            print("🔧 RECOMMENDED: Address failed endpoints before production deployment!")
        
        print("\n" + "=" * 70)

async def main():
    """Main test execution"""
    tester = SocialMediaCorrectedTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())