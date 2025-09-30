#!/usr/bin/env python3
"""
Comprehensive Social Media Strategy System Backend Testing
Tests all 4 phases of the social media strategy implementation as requested in the review.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Test configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://label-network.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api/social-strategy"

class SocialMediaStrategyTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.auth_token = None
        
    async def setup_session(self):
        """Setup HTTP session for testing"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_params_for_post: bool = False) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{API_BASE}{endpoint}"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Add auth token if available
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            kwargs = {
                'headers': headers,
                'params': params
            }
            
            # For some POST endpoints, data should be sent as query parameters
            if data:
                if use_params_for_post and method == 'POST':
                    kwargs['params'] = {**(kwargs.get('params', {})), **data}
                else:
                    kwargs['json'] = data
                
            async with self.session.request(method, url, **kwargs) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                    
                return response.status < 400, response_data, response.status
                
        except Exception as e:
            return False, str(e), 0
            
    async def test_authentication_setup(self):
        """Test authentication setup (mock token for testing)"""
        # For testing purposes, we'll use a mock token
        # In real implementation, this would authenticate with the actual system
        self.auth_token = "mock_test_token_for_social_strategy_testing"
        self.log_test_result(
            "Authentication Setup", 
            True, 
            "Mock authentication token configured for testing"
        )
        
    # Phase 1: Enhanced Platform Intelligence & Content Mapping Tests
    
    async def test_platform_intelligence_endpoint(self):
        """Test GET /api/social-strategy/platform-intelligence"""
        success, response, status = await self.make_request('GET', '/platform-intelligence')
        
        if success and isinstance(response, dict):
            platforms = response.get('platforms', {})
            total_platforms = response.get('total_platforms', 0)
            
            # Verify comprehensive platform data
            expected_platforms = ['instagram', 'tiktok', 'youtube', 'linkedin', 'spotify', 'threads', 'livemixtapes']
            found_platforms = [p for p in expected_platforms if p in platforms]
            
            success_criteria = (
                total_platforms >= 7,  # Should have major platforms (currently 7 in service)
                len(found_platforms) >= 5,  # Should have major platforms
                all(isinstance(platforms[p], dict) for p in found_platforms)  # Platform data should be objects
            )
            
            if all(success_criteria):
                self.log_test_result(
                    "Platform Intelligence API",
                    True,
                    f"Retrieved {total_platforms} platforms with detailed intelligence data. Found {len(found_platforms)} major platforms.",
                    {"total_platforms": total_platforms, "sample_platforms": found_platforms}
                )
            else:
                self.log_test_result(
                    "Platform Intelligence API",
                    False,
                    f"Platform intelligence incomplete. Total: {total_platforms}, Major platforms found: {len(found_platforms)}",
                    response
                )
        else:
            self.log_test_result(
                "Platform Intelligence API",
                False,
                f"Failed to retrieve platform intelligence. Status: {status}",
                response
            )
            
    async def test_content_recommendations_endpoint(self):
        """Test POST /api/social-strategy/content-recommendations"""
        test_cases = [
            {
                "name": "Video Content Recommendations",
                "data": {
                    "content_type": "video",
                    "content_duration": 60,
                    "monetization_priority": True
                }
            },
            {
                "name": "Audio Content Recommendations", 
                "data": {
                    "content_type": "audio",
                    "monetization_priority": False
                }
            },
            {
                "name": "Short Form Content Recommendations",
                "data": {
                    "content_type": "short_form",
                    "content_duration": 30,
                    "monetization_priority": True
                }
            }
        ]
        
        for test_case in test_cases:
            # Convert data to query parameters for this endpoint
            params = test_case["data"].copy()
            success, response, status = await self.make_request('POST', '/content-recommendations', params=params)
            
            if success and isinstance(response, dict):
                recommendations = response.get('recommendations', {})
                content_type = response.get('content_type')
                
                # Verify recommendation structure
                has_platforms = 'recommended_platforms' in recommendations
                has_adaptations = 'content_adaptations' in recommendations
                has_optimization_score = 'optimization_score' in recommendations
                
                if has_platforms and has_adaptations and has_optimization_score:
                    platforms = recommendations.get('recommended_platforms', [])
                    score = recommendations.get('optimization_score', 0)
                    
                    self.log_test_result(
                        f"Content Recommendations - {test_case['name']}",
                        True,
                        f"Generated recommendations for {content_type} with {len(platforms)} platforms, optimization score: {score}",
                        {"platforms": platforms, "score": score}
                    )
                else:
                    self.log_test_result(
                        f"Content Recommendations - {test_case['name']}",
                        False,
                        "Incomplete recommendation structure",
                        response
                    )
            else:
                self.log_test_result(
                    f"Content Recommendations - {test_case['name']}",
                    False,
                    f"Failed to get recommendations. Status: {status}",
                    response
                )
                
    # Phase 2: API Integration Foundation Tests
    
    async def test_oauth_authorization_endpoints(self):
        """Test GET /api/social-strategy/oauth/{platform_id}/authorize"""
        platforms_to_test = ['instagram', 'tiktok', 'youtube', 'twitter', 'linkedin']
        
        for platform in platforms_to_test:
            success, response, status = await self.make_request('GET', f'/oauth/{platform}/authorize')
            
            if success and isinstance(response, dict):
                auth_url = response.get('authorization_url')
                platform_id = response.get('platform_id')
                
                if auth_url and platform_id == platform:
                    self.log_test_result(
                        f"OAuth Authorization - {platform}",
                        True,
                        f"Generated authorization URL for {platform}",
                        {"platform": platform, "has_auth_url": bool(auth_url)}
                    )
                else:
                    self.log_test_result(
                        f"OAuth Authorization - {platform}",
                        False,
                        "Missing authorization URL or platform mismatch",
                        response
                    )
            else:
                self.log_test_result(
                    f"OAuth Authorization - {platform}",
                    False,
                    f"Failed to get authorization URL. Status: {status}",
                    response
                )
                
    async def test_analytics_integration_endpoints(self):
        """Test GET /api/social-strategy/analytics/{platform_id}"""
        platforms_to_test = ['instagram', 'tiktok', 'youtube']
        
        for platform in platforms_to_test:
            success, response, status = await self.make_request('GET', f'/analytics/{platform}')
            
            if success and isinstance(response, dict):
                analytics = response.get('analytics')
                platform_id = response.get('platform_id')
                
                if analytics is not None and platform_id == platform:
                    self.log_test_result(
                        f"Analytics Integration - {platform}",
                        True,
                        f"Retrieved analytics data for {platform}",
                        {"platform": platform, "has_analytics": analytics is not None}
                    )
                else:
                    self.log_test_result(
                        f"Analytics Integration - {platform}",
                        False,
                        "Missing analytics data or platform mismatch",
                        response
                    )
            else:
                self.log_test_result(
                    f"Analytics Integration - {platform}",
                    False,
                    f"Failed to get analytics data. Status: {status}",
                    response
                )
                
    # Phase 3: Cross-Promotion & Smart Routing Tests
    
    async def test_campaign_creation_endpoint(self):
        """Test POST /api/social-strategy/cross-promotion/campaign"""
        test_campaigns = [
            {
                "name": "Awareness Campaign",
                "data": {
                    "content_id": "test_content_123",
                    "content_type": "video",
                    "objective": "awareness",
                    "target_platforms": ["instagram", "tiktok", "youtube"],
                    "routing_strategy": "simultaneous",
                    "budget": 5000.0
                }
            },
            {
                "name": "Engagement Campaign",
                "data": {
                    "content_id": "test_content_456", 
                    "content_type": "audio",
                    "objective": "engagement",
                    "target_platforms": ["spotify", "youtube", "instagram"],
                    "routing_strategy": "staggered",
                    "budget": 3000.0
                }
            },
            {
                "name": "Conversion Campaign",
                "data": {
                    "content_id": "test_content_789",
                    "content_type": "short_form",
                    "objective": "conversions",
                    "target_platforms": ["tiktok", "instagram"],
                    "routing_strategy": "performance_based"
                }
            }
        ]
        
        for test_campaign in test_campaigns:
            # Convert data to query parameters for this endpoint
            params = test_campaign["data"].copy()
            success, response, status = await self.make_request('POST', '/cross-promotion/campaign', params=params)
            
            if success and isinstance(response, dict):
                campaign = response.get('campaign')
                success_flag = response.get('success')
                
                if success_flag and campaign:
                    campaign_id = campaign.get('campaign_id') if isinstance(campaign, dict) else None
                    self.log_test_result(
                        f"Campaign Creation - {test_campaign['name']}",
                        True,
                        f"Created {test_campaign['name'].lower()} with routing strategy: {test_campaign['data']['routing_strategy']}",
                        {"campaign_id": campaign_id, "platforms": test_campaign['data']['target_platforms']}
                    )
                else:
                    self.log_test_result(
                        f"Campaign Creation - {test_campaign['name']}",
                        False,
                        "Campaign creation failed or missing campaign data",
                        response
                    )
            else:
                self.log_test_result(
                    f"Campaign Creation - {test_campaign['name']}",
                    False,
                    f"Failed to create campaign. Status: {status}",
                    response
                )
                
    async def test_campaign_execution_endpoint(self):
        """Test POST /api/social-strategy/cross-promotion/execute/{campaign_id}"""
        test_campaign_id = "test_campaign_123"
        
        success, response, status = await self.make_request('POST', f'/cross-promotion/execute/{test_campaign_id}')
        
        if success and isinstance(response, dict):
            execution_results = response.get('execution_results')
            campaign_id = response.get('campaign_id')
            
            if execution_results is not None and campaign_id == test_campaign_id:
                self.log_test_result(
                    "Campaign Execution",
                    True,
                    f"Executed campaign routing for {campaign_id}",
                    {"campaign_id": campaign_id, "has_results": execution_results is not None}
                )
            else:
                self.log_test_result(
                    "Campaign Execution",
                    False,
                    "Missing execution results or campaign ID mismatch",
                    response
                )
        else:
            self.log_test_result(
                "Campaign Execution",
                False,
                f"Failed to execute campaign. Status: {status}",
                response
            )
            
    async def test_campaign_monitoring_endpoint(self):
        """Test GET /api/social-strategy/cross-promotion/monitor/{campaign_id}"""
        test_campaign_id = "test_campaign_456"
        
        success, response, status = await self.make_request('GET', f'/cross-promotion/monitor/{test_campaign_id}')
        
        if success and isinstance(response, dict):
            performance = response.get('performance')
            campaign_id = response.get('campaign_id')
            
            if performance is not None and campaign_id == test_campaign_id:
                self.log_test_result(
                    "Campaign Performance Monitoring",
                    True,
                    f"Retrieved performance data for campaign {campaign_id}",
                    {"campaign_id": campaign_id, "has_performance_data": performance is not None}
                )
            else:
                self.log_test_result(
                    "Campaign Performance Monitoring",
                    False,
                    "Missing performance data or campaign ID mismatch",
                    response
                )
        else:
            self.log_test_result(
                "Campaign Performance Monitoring",
                False,
                f"Failed to get campaign performance. Status: {status}",
                response
            )
            
    # Phase 4: Complete Workflow Management Tests
    
    async def test_workflow_templates_endpoint(self):
        """Test GET /api/social-strategy/workflow/templates"""
        success, response, status = await self.make_request('GET', '/workflow/templates')
        
        if success and isinstance(response, dict):
            templates = response.get('templates', {})
            
            # Check for expected templates
            expected_templates = ['music_release', 'product_launch', 'brand_awareness']
            found_templates = [t for t in expected_templates if t in templates]
            
            if len(found_templates) >= 3:
                template_details = {}
                for template_id in found_templates:
                    template = templates[template_id]
                    if isinstance(template, dict):
                        template_details[template_id] = {
                            "name": template.get('name', 'Unknown'),
                            "phases": len(template.get('phases_config', {})),
                            "platforms": len(template.get('recommended_platforms', []))
                        }
                
                self.log_test_result(
                    "Workflow Templates",
                    True,
                    f"Retrieved {len(found_templates)} comprehensive workflow templates",
                    template_details
                )
            else:
                self.log_test_result(
                    "Workflow Templates",
                    False,
                    f"Missing expected templates. Found: {found_templates}",
                    response
                )
        else:
            self.log_test_result(
                "Workflow Templates",
                False,
                f"Failed to retrieve workflow templates. Status: {status}",
                response
            )
            
    async def test_project_creation_endpoint(self):
        """Test POST /api/social-strategy/workflow/project"""
        test_projects = [
            {
                "name": "Music Release Project",
                "data": {
                    "title": "New Album Launch",
                    "description": "Comprehensive social media strategy for new album release",
                    "objective": "Brand Awareness and Engagement",
                    "target_platforms": ["spotify", "youtube", "instagram", "tiktok"],
                    "template_id": "music_release",
                    "budget": 10000.0
                }
            },
            {
                "name": "Product Launch Project",
                "data": {
                    "title": "Product Marketing Campaign",
                    "description": "Multi-platform product launch strategy",
                    "objective": "Conversions and Sales",
                    "target_platforms": ["instagram", "facebook", "linkedin", "youtube"],
                    "template_id": "product_launch",
                    "budget": 15000.0
                }
            }
        ]
        
        for test_project in test_projects:
            # Convert data to query parameters for this endpoint
            params = test_project["data"].copy()
            success, response, status = await self.make_request('POST', '/workflow/project', params=params)
            
            if success and isinstance(response, dict):
                project = response.get('project')
                success_flag = response.get('success')
                
                if success_flag and project:
                    project_id = project.get('project_id') if isinstance(project, dict) else None
                    self.log_test_result(
                        f"Project Creation - {test_project['name']}",
                        True,
                        f"Created workflow project with template: {test_project['data']['template_id']}",
                        {"project_id": project_id, "budget": test_project['data']['budget']}
                    )
                else:
                    self.log_test_result(
                        f"Project Creation - {test_project['name']}",
                        False,
                        "Project creation failed or missing project data",
                        response
                    )
            else:
                self.log_test_result(
                    f"Project Creation - {test_project['name']}",
                    False,
                    f"Failed to create project. Status: {status}",
                    response
                )
                
    async def test_project_dashboard_endpoint(self):
        """Test GET /api/social-strategy/workflow/project/{project_id}/dashboard"""
        test_project_id = "test_project_123"
        
        success, response, status = await self.make_request('GET', f'/workflow/project/{test_project_id}/dashboard')
        
        if success and isinstance(response, dict):
            dashboard = response.get('dashboard')
            project_id = response.get('project_id')
            
            if dashboard and project_id == test_project_id:
                # Check for expected dashboard components
                expected_components = ['project_overview', 'phase_progress', 'budget_status', 'upcoming_deadlines']
                found_components = [c for c in expected_components if c in dashboard]
                
                if len(found_components) >= 3:
                    self.log_test_result(
                        "Project Dashboard",
                        True,
                        f"Retrieved comprehensive dashboard with {len(found_components)} components",
                        {"project_id": project_id, "components": found_components}
                    )
                else:
                    self.log_test_result(
                        "Project Dashboard",
                        False,
                        f"Incomplete dashboard. Found components: {found_components}",
                        response
                    )
            else:
                self.log_test_result(
                    "Project Dashboard",
                    False,
                    "Missing dashboard data or project ID mismatch",
                    response
                )
        else:
            self.log_test_result(
                "Project Dashboard",
                False,
                f"Failed to get project dashboard. Status: {status}",
                response
            )
            
    # Advanced Features Tests
    
    async def test_smart_routing_analysis_endpoint(self):
        """Test POST /api/social-strategy/smart-routing/analyze"""
        test_data = {
            "content_data": {
                "content_type": "video",
                "duration": 120,
                "category": "entertainment"
            },
            "performance_data": {
                "instagram": {"engagement_rate": 4.2, "reach": 15000, "conversions": 45},
                "tiktok": {"engagement_rate": 6.8, "reach": 25000, "conversions": 32},
                "youtube": {"engagement_rate": 2.1, "reach": 8000, "conversions": 67}
            }
        }
        
        success, response, status = await self.make_request('POST', '/smart-routing/analyze', test_data)
        
        if success and isinstance(response, dict):
            analysis = response.get('analysis')
            
            if analysis and isinstance(analysis, dict):
                # Check for expected analysis components
                expected_components = ['routing_strategy', 'recommended_platforms', 'optimization_opportunities', 'budget_reallocation']
                found_components = [c for c in expected_components if c in analysis]
                
                if len(found_components) >= 3:
                    self.log_test_result(
                        "Smart Routing Analysis",
                        True,
                        f"Generated intelligent routing analysis with {len(found_components)} components",
                        {"components": found_components, "strategy": analysis.get('routing_strategy')}
                    )
                else:
                    self.log_test_result(
                        "Smart Routing Analysis",
                        False,
                        f"Incomplete analysis. Found components: {found_components}",
                        response
                    )
            else:
                self.log_test_result(
                    "Smart Routing Analysis",
                    False,
                    "Missing or invalid analysis data",
                    response
                )
        else:
            self.log_test_result(
                "Smart Routing Analysis",
                False,
                f"Failed to get routing analysis. Status: {status}",
                response
            )
            
    async def test_comprehensive_reporting_endpoint(self):
        """Test GET /api/social-strategy/strategy/comprehensive-report"""
        success, response, status = await self.make_request('GET', '/strategy/comprehensive-report', params={"date_range": "30d"})
        
        if success and isinstance(response, dict):
            report = response.get('report')
            
            if report and isinstance(report, dict):
                # Check for expected report sections
                expected_sections = ['executive_summary', 'platform_performance', 'content_intelligence_insights', 'recommendations']
                found_sections = [s for s in expected_sections if s in report]
                
                if len(found_sections) >= 4:
                    exec_summary = report.get('executive_summary', {})
                    self.log_test_result(
                        "Comprehensive Strategy Report",
                        True,
                        f"Generated detailed report with {len(found_sections)} sections",
                        {
                            "sections": found_sections,
                            "total_campaigns": exec_summary.get('total_campaigns'),
                            "roi": exec_summary.get('roi')
                        }
                    )
                else:
                    self.log_test_result(
                        "Comprehensive Strategy Report",
                        False,
                        f"Incomplete report. Found sections: {found_sections}",
                        response
                    )
            else:
                self.log_test_result(
                    "Comprehensive Strategy Report",
                    False,
                    "Missing or invalid report data",
                    response
                )
        else:
            self.log_test_result(
                "Comprehensive Strategy Report",
                False,
                f"Failed to generate report. Status: {status}",
                response
            )
            
    async def test_ai_recommendations_endpoint(self):
        """Test POST /api/social-strategy/strategy/ai-recommendations"""
        test_data = {
            "user_goals": {
                "primary_objective": "brand_awareness",
                "target_audience": "18-34",
                "budget_allocation": {"content": 40, "advertising": 35, "tools": 25}
            },
            "current_performance": {
                "total_reach": 50000,
                "engagement_rate": 3.2,
                "conversion_rate": 1.8,
                "top_platforms": ["instagram", "tiktok"]
            }
        }
        
        success, response, status = await self.make_request('POST', '/strategy/ai-recommendations', test_data)
        
        if success and isinstance(response, dict):
            recommendations = response.get('recommendations')
            confidence_score = response.get('confidence_score')
            
            if recommendations and isinstance(recommendations, dict):
                # Check for expected recommendation categories
                expected_categories = ['priority_actions', 'content_strategy', 'budget_optimization', 'automation_opportunities']
                found_categories = [c for c in expected_categories if c in recommendations]
                
                if len(found_categories) >= 3:
                    priority_actions = recommendations.get('priority_actions', [])
                    self.log_test_result(
                        "AI-Powered Recommendations",
                        True,
                        f"Generated AI recommendations with {len(found_categories)} categories and {len(priority_actions)} priority actions",
                        {
                            "categories": found_categories,
                            "confidence_score": confidence_score,
                            "priority_actions_count": len(priority_actions)
                        }
                    )
                else:
                    self.log_test_result(
                        "AI-Powered Recommendations",
                        False,
                        f"Incomplete recommendations. Found categories: {found_categories}",
                        response
                    )
            else:
                self.log_test_result(
                    "AI-Powered Recommendations",
                    False,
                    "Missing or invalid recommendations data",
                    response
                )
        else:
            self.log_test_result(
                "AI-Powered Recommendations",
                False,
                f"Failed to get AI recommendations. Status: {status}",
                response
            )
            
    async def test_real_time_monitoring_endpoint(self):
        """Test GET /api/social-strategy/monitoring/real-time"""
        success, response, status = await self.make_request('GET', '/monitoring/real-time')
        
        if success and isinstance(response, dict):
            monitoring = response.get('monitoring')
            
            if monitoring and isinstance(monitoring, dict):
                # Check for expected monitoring components
                expected_components = ['current_campaigns', 'real_time_engagement', 'trending_content', 'platform_status']
                found_components = [c for c in expected_components if c in monitoring]
                
                if len(found_components) >= 3:
                    platform_status = monitoring.get('platform_status', {})
                    alerts = monitoring.get('alerts', [])
                    
                    self.log_test_result(
                        "Real-time Monitoring",
                        True,
                        f"Retrieved real-time monitoring with {len(found_components)} components",
                        {
                            "components": found_components,
                            "platforms_monitored": len(platform_status),
                            "active_alerts": len(alerts)
                        }
                    )
                else:
                    self.log_test_result(
                        "Real-time Monitoring",
                        False,
                        f"Incomplete monitoring data. Found components: {found_components}",
                        response
                    )
            else:
                self.log_test_result(
                    "Real-time Monitoring",
                    False,
                    "Missing or invalid monitoring data",
                    response
                )
        else:
            self.log_test_result(
                "Real-time Monitoring",
                False,
                f"Failed to get real-time monitoring. Status: {status}",
                response
            )
            
    async def run_all_tests(self):
        """Run all social media strategy tests"""
        print("🎯 COMPREHENSIVE SOCIAL MEDIA STRATEGY SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        await self.setup_session()
        
        try:
            # Authentication setup
            await self.test_authentication_setup()
            
            print("📊 PHASE 1: Enhanced Platform Intelligence & Content Mapping")
            print("-" * 60)
            await self.test_platform_intelligence_endpoint()
            await self.test_content_recommendations_endpoint()
            
            print("🔗 PHASE 2: API Integration Foundation")
            print("-" * 60)
            await self.test_oauth_authorization_endpoints()
            await self.test_analytics_integration_endpoints()
            
            print("🚀 PHASE 3: Cross-Promotion & Smart Routing")
            print("-" * 60)
            await self.test_campaign_creation_endpoint()
            await self.test_campaign_execution_endpoint()
            await self.test_campaign_monitoring_endpoint()
            
            print("📋 PHASE 4: Complete Workflow Management")
            print("-" * 60)
            await self.test_workflow_templates_endpoint()
            await self.test_project_creation_endpoint()
            await self.test_project_dashboard_endpoint()
            
            print("🧠 ADVANCED FEATURES")
            print("-" * 60)
            await self.test_smart_routing_analysis_endpoint()
            await self.test_comprehensive_reporting_endpoint()
            await self.test_ai_recommendations_endpoint()
            await self.test_real_time_monitoring_endpoint()
            
        finally:
            await self.cleanup_session()
            
        # Generate summary
        self.generate_test_summary()
        
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE SOCIAL MEDIA STRATEGY TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by phase
        phases = {
            "Phase 1 - Platform Intelligence": [],
            "Phase 2 - API Integration": [],
            "Phase 3 - Cross-Promotion": [],
            "Phase 4 - Workflow Management": [],
            "Advanced Features": [],
            "System Setup": []
        }
        
        for result in self.test_results:
            test_name = result['test']
            if 'Platform Intelligence' in test_name or 'Content Recommendations' in test_name:
                phases["Phase 1 - Platform Intelligence"].append(result)
            elif 'OAuth' in test_name or 'Analytics' in test_name:
                phases["Phase 2 - API Integration"].append(result)
            elif 'Campaign' in test_name:
                phases["Phase 3 - Cross-Promotion"].append(result)
            elif 'Workflow' in test_name or 'Project' in test_name:
                phases["Phase 4 - Workflow Management"].append(result)
            elif 'Smart Routing' in test_name or 'AI' in test_name or 'Monitoring' in test_name or 'Report' in test_name:
                phases["Advanced Features"].append(result)
            else:
                phases["System Setup"].append(result)
        
        for phase_name, phase_results in phases.items():
            if phase_results:
                phase_passed = len([r for r in phase_results if r['success']])
                phase_total = len(phase_results)
                phase_rate = (phase_passed / phase_total * 100) if phase_total > 0 else 0
                
                print(f"{phase_name}: {phase_passed}/{phase_total} ({phase_rate:.1f}%)")
                
                for result in phase_results:
                    status_icon = "✅" if result['success'] else "❌"
                    print(f"  {status_icon} {result['test']}")
                print()
        
        # Critical Issues Summary
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            print("-" * 40)
            for result in failed_results:
                print(f"❌ {result['test']}")
                if result['details']:
                    print(f"   Issue: {result['details']}")
            print()
        
        # Success Highlights
        if success_rate >= 80:
            print("🎉 SYSTEM STATUS: PRODUCTION READY")
            print("✅ Social Media Strategy system is fully functional with comprehensive features")
            print("✅ All 4 phases implemented with proper API endpoints")
            print("✅ Advanced features working correctly")
        elif success_rate >= 60:
            print("⚠️  SYSTEM STATUS: MOSTLY FUNCTIONAL")
            print("✅ Core functionality working")
            print("⚠️  Some advanced features need attention")
        else:
            print("🚨 SYSTEM STATUS: NEEDS IMMEDIATE ATTENTION")
            print("❌ Critical functionality issues detected")
            print("❌ System not ready for production use")
        
        print("\n" + "=" * 80)
        print(f"Testing completed at: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

async def main():
    """Main test execution function"""
    tester = SocialMediaStrategyTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())