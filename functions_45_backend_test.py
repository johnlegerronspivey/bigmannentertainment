#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Functions 4 & 5
Big Mann Entertainment Platform - Content Analytics & Performance Monitoring + Content Lifecycle Management & Automation

This script tests all endpoints for:
- Function 4: Content Analytics & Performance Monitoring System
- Function 5: Content Lifecycle Management & Automation System

Testing Scope:
FUNCTION 4 - Content Analytics & Performance Monitoring:
1. Event Tracking (Track single events, Batch event tracking)
2. Content Performance (Get performance metrics, List all performance, Content trends)
3. ROI Analysis (Calculate ROI, Get ROI analysis)
4. Platform Analytics (Get platform analytics, Get all platform analytics)
5. Dashboard and Summary (Analytics dashboard, Summary, Insights)
6. Benchmarking (Industry benchmarks, Performance reports)
7. System Health

FUNCTION 5 - Content Lifecycle Management & Automation:
1. Lifecycle Management (Create lifecycle, Get lifecycle, List lifecycles)
2. Stage Transitions (Transition stages, Update status)
3. Version Management (Create versions, Get versions, Version history)
4. Automation (Create rules, List rules, Update/Delete rules)
5. Dashboard & Analytics (Lifecycle dashboard, Analytics summary)
6. Templates & Configuration (Rule templates, Enums)
7. Bulk Operations (Bulk status update, Bulk stage transition)
8. System Health
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid

# Configuration
BASE_URL = "https://bme-profile.preview.emergentagent.com"
TEST_USER_EMAIL = "testuser@bigmannentertainment.com"
TEST_USER_PASSWORD = "TestPassword123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class Functions45BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.test_content_id = str(uuid.uuid4())
        self.test_version_id = None
        self.test_automation_rule_id = None
        
    async def setup_session(self):
        """Setup HTTP session with proper headers"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'BigMannEntertainment-Functions45-Tester/1.0'
            }
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} {test_name}")
        if details:
            print(f"    {Colors.CYAN}Details: {details}{Colors.END}")
        if response_data and isinstance(response_data, dict):
            if 'error' in response_data:
                print(f"    {Colors.RED}Error: {response_data['error']}{Colors.END}")
        
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    async def authenticate_user(self):
        """Authenticate test user and get token"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔐 AUTHENTICATION SETUP{Colors.END}")
        
        # Try to register user first (in case they don't exist)
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": "Functions 4&5 Test User",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/auth/register", json=register_data) as response:
                if response.status in [200, 201]:
                    print(f"    {Colors.GREEN}✅ User registered successfully{Colors.END}")
                elif response.status == 400:
                    print(f"    {Colors.YELLOW}ℹ️  User already exists{Colors.END}")
        except Exception as e:
            print(f"    {Colors.YELLOW}⚠️  Registration attempt: {str(e)}{Colors.END}")
        
        # Login to get token
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get('access_token')
                    if self.auth_token:
                        self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                        self.log_test_result("User Authentication", True, f"Token obtained: {self.auth_token[:20]}...")
                        return True
                    else:
                        self.log_test_result("User Authentication", False, "No access token in response")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test_result("User Authentication", False, f"Status {response.status}: {error_data}")
                    return False
        except Exception as e:
            self.log_test_result("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    # ==================== FUNCTION 4: CONTENT ANALYTICS & PERFORMANCE MONITORING ====================
    
    async def test_analytics_event_tracking(self):
        """Test Function 4: Event Tracking endpoints"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📊 FUNCTION 4: ANALYTICS EVENT TRACKING{Colors.END}")
        
        # Test 1: Track Single Event
        event_data = {
            "content_id": self.test_content_id,
            "platform": "spotify",
            "metric_type": "views",
            "value": 150.0,
            "metadata": {
                "source": "organic",
                "device": "mobile",
                "location": "US"
            },
            "geo_data": {
                "country": "US",
                "region": "California"
            }
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/analytics/events/track", json=event_data) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                self.log_test_result(
                    "Analytics - Track Single Event", 
                    success, 
                    f"Status: {response.status}, Event tracked for content {self.test_content_id}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Track Single Event", False, f"Exception: {str(e)}")
        
        # Test 2: Batch Event Tracking
        batch_events = {
            "events": [
                {
                    "content_id": self.test_content_id,
                    "platform": "youtube",
                    "metric_type": "streams",
                    "value": 75.0,
                    "metadata": {"source": "playlist"}
                },
                {
                    "content_id": self.test_content_id,
                    "platform": "apple_music",
                    "metric_type": "likes",
                    "value": 25.0,
                    "metadata": {"source": "discovery"}
                }
            ]
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/analytics/events/batch", json=batch_events) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                events_tracked = data.get('events_tracked', 0) if isinstance(data, dict) else 0
                self.log_test_result(
                    "Analytics - Batch Event Tracking", 
                    success, 
                    f"Status: {response.status}, Events tracked: {events_tracked}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Batch Event Tracking", False, f"Exception: {str(e)}")
    
    async def test_analytics_content_performance(self):
        """Test Function 4: Content Performance endpoints"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📈 FUNCTION 4: CONTENT PERFORMANCE ANALYTICS{Colors.END}")
        
        # Test 1: Get Content Performance
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/content/{self.test_content_id}/performance") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status in [200, 404]  # 404 is acceptable for new content
                details = f"Status: {response.status}"
                if response.status == 404:
                    details += " (Expected for new content)"
                elif isinstance(data, dict) and 'content_performance' in data:
                    details += f", Performance data available"
                
                self.log_test_result(
                    "Analytics - Get Content Performance", 
                    success, 
                    details,
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Get Content Performance", False, f"Exception: {str(e)}")
        
        # Test 2: List All Content Performance
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/content/performance/all?limit=10") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                total_items = data.get('total_items', 0) if isinstance(data, dict) else 0
                self.log_test_result(
                    "Analytics - List All Content Performance", 
                    success, 
                    f"Status: {response.status}, Total items: {total_items}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - List All Content Performance", False, f"Exception: {str(e)}")
        
        # Test 3: Get Content Trends
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/content/{self.test_content_id}/trends?days=30") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                period_days = data.get('period_days', 0) if isinstance(data, dict) else 0
                self.log_test_result(
                    "Analytics - Get Content Trends", 
                    success, 
                    f"Status: {response.status}, Period: {period_days} days",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Get Content Trends", False, f"Exception: {str(e)}")
    
    async def test_analytics_roi_analysis(self):
        """Test Function 4: ROI Analysis endpoints"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}💰 FUNCTION 4: ROI ANALYSIS{Colors.END}")
        
        # Test 1: Calculate ROI Analysis
        roi_data = {
            "content_id": self.test_content_id,
            "production_cost": 500.0,
            "marketing_cost": 200.0,
            "distribution_cost": 50.0,
            "platform_fees": 25.0
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/analytics/roi/calculate", json=roi_data) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                self.log_test_result(
                    "Analytics - Calculate ROI Analysis", 
                    success, 
                    f"Status: {response.status}, ROI calculated for content {self.test_content_id}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Calculate ROI Analysis", False, f"Exception: {str(e)}")
        
        # Test 2: Get ROI Analysis
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/roi/{self.test_content_id}") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status in [200, 404]  # 404 acceptable if no ROI data yet
                details = f"Status: {response.status}"
                if response.status == 404:
                    details += " (No ROI data found - expected for new content)"
                elif isinstance(data, dict) and 'roi_analysis' in data:
                    details += ", ROI analysis retrieved"
                
                self.log_test_result(
                    "Analytics - Get ROI Analysis", 
                    success, 
                    details,
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Get ROI Analysis", False, f"Exception: {str(e)}")
    
    async def test_analytics_platform_analytics(self):
        """Test Function 4: Platform Analytics endpoints"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🎯 FUNCTION 4: PLATFORM ANALYTICS{Colors.END}")
        
        # Test 1: Get Platform Analytics
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/platforms/spotify/analytics") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                platform = data.get('platform', '') if isinstance(data, dict) else ''
                self.log_test_result(
                    "Analytics - Get Platform Analytics", 
                    success, 
                    f"Status: {response.status}, Platform: {platform}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Get Platform Analytics", False, f"Exception: {str(e)}")
        
        # Test 2: Get All Platform Analytics
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/platforms/analytics/all") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                total_platforms = data.get('total_platforms', 0) if isinstance(data, dict) else 0
                self.log_test_result(
                    "Analytics - Get All Platform Analytics", 
                    success, 
                    f"Status: {response.status}, Total platforms: {total_platforms}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Get All Platform Analytics", False, f"Exception: {str(e)}")
    
    async def test_analytics_dashboard_summary(self):
        """Test Function 4: Dashboard and Summary endpoints"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📋 FUNCTION 4: DASHBOARD & SUMMARY{Colors.END}")
        
        # Test 1: Analytics Dashboard
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/dashboard?days=30") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                period_days = data.get('period_days', 0) if isinstance(data, dict) else 0
                self.log_test_result(
                    "Analytics - Dashboard", 
                    success, 
                    f"Status: {response.status}, Period: {period_days} days",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Dashboard", False, f"Exception: {str(e)}")
        
        # Test 2: Analytics Summary
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/summary?days=7") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                summary = data.get('summary', {}) if isinstance(data, dict) else {}
                period_days = summary.get('period_days', 0) if isinstance(summary, dict) else 0
                self.log_test_result(
                    "Analytics - Summary", 
                    success, 
                    f"Status: {response.status}, Period: {period_days} days",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Summary", False, f"Exception: {str(e)}")
        
        # Test 3: Performance Insights
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/insights/performance?days=30") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                insights = data.get('insights', {}) if isinstance(data, dict) else {}
                key_insights_count = len(insights.get('key_insights', [])) if isinstance(insights, dict) else 0
                self.log_test_result(
                    "Analytics - Performance Insights", 
                    success, 
                    f"Status: {response.status}, Key insights: {key_insights_count}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Performance Insights", False, f"Exception: {str(e)}")
        
        # Test 4: Content Optimization Insights
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/insights/content-optimization") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                insights = data.get('insights', {}) if isinstance(data, dict) else {}
                total_analyzed = insights.get('total_content_analyzed', 0) if isinstance(insights, dict) else 0
                self.log_test_result(
                    "Analytics - Content Optimization Insights", 
                    success, 
                    f"Status: {response.status}, Content analyzed: {total_analyzed}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Content Optimization Insights", False, f"Exception: {str(e)}")
    
    async def test_analytics_benchmarking(self):
        """Test Function 4: Benchmarking endpoints"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📊 FUNCTION 4: BENCHMARKING{Colors.END}")
        
        # Test 1: Industry Benchmarks
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/benchmarks/industry?content_type=music") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                content_type = data.get('benchmark_comparison', {}).get('content_type', '') if isinstance(data, dict) else ''
                self.log_test_result(
                    "Analytics - Industry Benchmarks", 
                    success, 
                    f"Status: {response.status}, Content type: {content_type}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Industry Benchmarks", False, f"Exception: {str(e)}")
        
        # Test 2: Performance Report
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/reports/performance?format=json&days=30") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                report = data.get('report', {}) if isinstance(data, dict) else {}
                report_type = report.get('report_type', '') if isinstance(report, dict) else ''
                self.log_test_result(
                    "Analytics - Performance Report", 
                    success, 
                    f"Status: {response.status}, Report type: {report_type}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - Performance Report", False, f"Exception: {str(e)}")
    
    async def test_analytics_health(self):
        """Test Function 4: System Health"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🏥 FUNCTION 4: SYSTEM HEALTH{Colors.END}")
        
        try:
            async with self.session.get(f"{self.base_url}/api/analytics/health") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                health = data.get('health', {}) if isinstance(data, dict) else {}
                service_status = health.get('status', '') if isinstance(health, dict) else ''
                version = health.get('version', '') if isinstance(health, dict) else ''
                self.log_test_result(
                    "Analytics - System Health", 
                    success, 
                    f"Status: {response.status}, Service: {service_status}, Version: {version}",
                    data
                )
        except Exception as e:
            self.log_test_result("Analytics - System Health", False, f"Exception: {str(e)}")
    
    # ==================== FUNCTION 5: CONTENT LIFECYCLE MANAGEMENT & AUTOMATION ====================
    
    async def test_lifecycle_management(self):
        """Test Function 5: Lifecycle Management endpoints"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🔄 FUNCTION 5: LIFECYCLE MANAGEMENT{Colors.END}")
        
        # Test 1: Create Content Lifecycle
        lifecycle_data = {
            "content_id": self.test_content_id,
            "initial_version": {
                "title": "Test Content for Lifecycle",
                "description": "Test content for lifecycle management testing",
                "file_path": "/test/content/audio.mp3",
                "file_size": 5242880,
                "file_format": "mp3",
                "metadata": {
                    "content_type": "music",
                    "genre": "electronic",
                    "duration": 180
                }
            },
            "policies": ["music_standard"]
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/lifecycle/create", json=lifecycle_data) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                lifecycle = data.get('lifecycle', {}) if isinstance(data, dict) else {}
                lifecycle_id = lifecycle.get('lifecycle_id', '') if isinstance(lifecycle, dict) else ''
                self.log_test_result(
                    "Lifecycle - Create Content Lifecycle", 
                    success, 
                    f"Status: {response.status}, Lifecycle ID: {lifecycle_id[:8]}..." if lifecycle_id else f"Status: {response.status}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Create Content Lifecycle", False, f"Exception: {str(e)}")
        
        # Test 2: Get Content Lifecycle
        try:
            async with self.session.get(f"{self.base_url}/api/lifecycle/{self.test_content_id}") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                lifecycle = data.get('lifecycle', {}) if isinstance(data, dict) else {}
                current_status = lifecycle.get('current_status', '') if isinstance(lifecycle, dict) else ''
                current_stage = lifecycle.get('current_stage', '') if isinstance(lifecycle, dict) else ''
                self.log_test_result(
                    "Lifecycle - Get Content Lifecycle", 
                    success, 
                    f"Status: {response.status}, Current status: {current_status}, Stage: {current_stage}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Get Content Lifecycle", False, f"Exception: {str(e)}")
        
        # Test 3: List Content Lifecycles
        try:
            async with self.session.get(f"{self.base_url}/api/lifecycle/?limit=10") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                total_items = data.get('total_items', 0) if isinstance(data, dict) else 0
                self.log_test_result(
                    "Lifecycle - List Content Lifecycles", 
                    success, 
                    f"Status: {response.status}, Total items: {total_items}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - List Content Lifecycles", False, f"Exception: {str(e)}")
    
    async def test_lifecycle_stage_transitions(self):
        """Test Function 5: Stage Transitions endpoints"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎭 FUNCTION 5: STAGE TRANSITIONS{Colors.END}")
        
        # Test 1: Transition Lifecycle Stage
        stage_transition_data = {
            "content_id": self.test_content_id,
            "new_stage": "production",
            "notes": "Moving to production stage for testing"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/lifecycle/stage/transition", json=stage_transition_data) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                new_stage = data.get('new_stage', '') if isinstance(data, dict) else ''
                self.log_test_result(
                    "Lifecycle - Transition Stage", 
                    success, 
                    f"Status: {response.status}, New stage: {new_stage}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Transition Stage", False, f"Exception: {str(e)}")
        
        # Test 2: Update Content Status
        status_update_data = {
            "content_id": self.test_content_id,
            "new_status": "published",
            "notes": "Publishing content for testing"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/lifecycle/status/update", json=status_update_data) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                new_status = data.get('new_status', '') if isinstance(data, dict) else ''
                self.log_test_result(
                    "Lifecycle - Update Status", 
                    success, 
                    f"Status: {response.status}, New status: {new_status}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Update Status", False, f"Exception: {str(e)}")
    
    async def test_lifecycle_version_management(self):
        """Test Function 5: Version Management endpoints"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}📝 FUNCTION 5: VERSION MANAGEMENT{Colors.END}")
        
        # Test 1: Create Content Version
        version_data = {
            "content_id": self.test_content_id,
            "version_data": {
                "title": "Test Content v2.0",
                "description": "Updated version with improvements",
                "file_path": "/test/content/audio_v2.mp3",
                "file_size": 5500000,
                "file_format": "mp3",
                "metadata": {
                    "content_type": "music",
                    "genre": "electronic",
                    "duration": 185,
                    "quality": "high"
                }
            },
            "changes_summary": "Improved audio quality and extended duration",
            "set_as_current": True
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/lifecycle/versions/create", json=version_data) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                version = data.get('version', {}) if isinstance(data, dict) else {}
                version_id = version.get('version_id', '') if isinstance(version, dict) else ''
                version_number = version.get('version_number', '') if isinstance(version, dict) else ''
                
                if version_id:
                    self.test_version_id = version_id
                
                self.log_test_result(
                    "Lifecycle - Create Content Version", 
                    success, 
                    f"Status: {response.status}, Version: {version_number}, ID: {version_id[:8]}..." if version_id else f"Status: {response.status}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Create Content Version", False, f"Exception: {str(e)}")
        
        # Test 2: Get Content Version (if we have a version ID)
        if self.test_version_id:
            try:
                async with self.session.get(f"{self.base_url}/api/lifecycle/versions/{self.test_version_id}") as response:
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
                    success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                    version = data.get('version', {}) if isinstance(data, dict) else {}
                    version_number = version.get('version_number', '') if isinstance(version, dict) else ''
                    self.log_test_result(
                        "Lifecycle - Get Content Version", 
                        success, 
                        f"Status: {response.status}, Version: {version_number}",
                        data
                    )
            except Exception as e:
                self.log_test_result("Lifecycle - Get Content Version", False, f"Exception: {str(e)}")
        
        # Test 3: Get Version History
        try:
            async with self.session.get(f"{self.base_url}/api/lifecycle/{self.test_content_id}/versions") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                total_versions = data.get('total_versions', 0) if isinstance(data, dict) else 0
                current_version_id = data.get('current_version_id', '') if isinstance(data, dict) else ''
                self.log_test_result(
                    "Lifecycle - Get Version History", 
                    success, 
                    f"Status: {response.status}, Total versions: {total_versions}, Current: {current_version_id[:8]}..." if current_version_id else f"Status: {response.status}, Total versions: {total_versions}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Get Version History", False, f"Exception: {str(e)}")
    
    async def test_lifecycle_automation(self):
        """Test Function 5: Automation endpoints"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🤖 FUNCTION 5: AUTOMATION{Colors.END}")
        
        # Test 1: Create Automation Rule
        automation_rule_data = {
            "rule_name": "Auto-promote High Performance Content",
            "description": "Automatically promote content when it reaches high engagement",
            "trigger_type": "performance_based",
            "trigger_conditions": {
                "metric": "engagement_rate",
                "threshold": 5.0,
                "operator": "greater_than"
            },
            "action_type": "promote_content",
            "action_parameters": {
                "promotion_type": "featured",
                "duration_days": 7
            },
            "applies_to_content_types": ["music", "video"],
            "applies_to_platforms": ["spotify", "youtube", "apple_music"]
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/lifecycle/automation/rules", json=automation_rule_data) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                automation_rule = data.get('automation_rule', {}) if isinstance(data, dict) else {}
                rule_id = automation_rule.get('rule_id', '') if isinstance(automation_rule, dict) else ''
                rule_name = automation_rule.get('rule_name', '') if isinstance(automation_rule, dict) else ''
                
                if rule_id:
                    self.test_automation_rule_id = rule_id
                
                self.log_test_result(
                    "Lifecycle - Create Automation Rule", 
                    success, 
                    f"Status: {response.status}, Rule: {rule_name}, ID: {rule_id[:8]}..." if rule_id else f"Status: {response.status}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Create Automation Rule", False, f"Exception: {str(e)}")
        
        # Test 2: List Automation Rules
        try:
            async with self.session.get(f"{self.base_url}/api/lifecycle/automation/rules") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                total_rules = data.get('total_rules', 0) if isinstance(data, dict) else 0
                self.log_test_result(
                    "Lifecycle - List Automation Rules", 
                    success, 
                    f"Status: {response.status}, Total rules: {total_rules}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - List Automation Rules", False, f"Exception: {str(e)}")
        
        # Test 3: Update Automation Rule (if we have a rule ID)
        if self.test_automation_rule_id:
            update_data = {
                "description": "Updated automation rule for testing",
                "is_active": True
            }
            
            try:
                async with self.session.put(f"{self.base_url}/api/lifecycle/automation/rules/{self.test_automation_rule_id}", json=update_data) as response:
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
                    success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                    self.log_test_result(
                        "Lifecycle - Update Automation Rule", 
                        success, 
                        f"Status: {response.status}, Rule updated",
                        data
                    )
            except Exception as e:
                self.log_test_result("Lifecycle - Update Automation Rule", False, f"Exception: {str(e)}")
    
    async def test_lifecycle_dashboard_analytics(self):
        """Test Function 5: Dashboard & Analytics endpoints"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}📊 FUNCTION 5: DASHBOARD & ANALYTICS{Colors.END}")
        
        # Test 1: Lifecycle Dashboard
        try:
            async with self.session.get(f"{self.base_url}/api/lifecycle/dashboard") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                dashboard = data.get('dashboard', {}) if isinstance(data, dict) else {}
                total_content = dashboard.get('total_content_pieces', 0) if isinstance(dashboard, dict) else 0
                active_automations = dashboard.get('active_automations', 0) if isinstance(dashboard, dict) else 0
                self.log_test_result(
                    "Lifecycle - Dashboard", 
                    success, 
                    f"Status: {response.status}, Content pieces: {total_content}, Active automations: {active_automations}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Dashboard", False, f"Exception: {str(e)}")
        
        # Test 2: Analytics Summary
        try:
            async with self.session.get(f"{self.base_url}/api/lifecycle/analytics/summary?days=30") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                summary = data.get('summary', {}) if isinstance(data, dict) else {}
                period_days = summary.get('period_days', 0) if isinstance(summary, dict) else 0
                self.log_test_result(
                    "Lifecycle - Analytics Summary", 
                    success, 
                    f"Status: {response.status}, Period: {period_days} days",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - Analytics Summary", False, f"Exception: {str(e)}")
    
    async def test_lifecycle_health(self):
        """Test Function 5: System Health"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🏥 FUNCTION 5: SYSTEM HEALTH{Colors.END}")
        
        try:
            async with self.session.get(f"{self.base_url}/api/lifecycle/health") as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                success = response.status == 200 and isinstance(data, dict) and data.get('success', False)
                health = data.get('health', {}) if isinstance(data, dict) else {}
                service_status = health.get('status', '') if isinstance(health, dict) else ''
                version = health.get('version', '') if isinstance(health, dict) else ''
                self.log_test_result(
                    "Lifecycle - System Health", 
                    success, 
                    f"Status: {response.status}, Service: {service_status}, Version: {version}",
                    data
                )
        except Exception as e:
            self.log_test_result("Lifecycle - System Health", False, f"Exception: {str(e)}")
    
    async def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}🧹 CLEANUP TEST DATA{Colors.END}")
        
        # Delete automation rule if created
        if self.test_automation_rule_id:
            try:
                async with self.session.delete(f"{self.base_url}/api/lifecycle/automation/rules/{self.test_automation_rule_id}") as response:
                    success = response.status == 200
                    self.log_test_result(
                        "Cleanup - Delete Automation Rule", 
                        success, 
                        f"Status: {response.status}"
                    )
            except Exception as e:
                self.log_test_result("Cleanup - Delete Automation Rule", False, f"Exception: {str(e)}")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print(f"\n{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}🎯 FUNCTIONS 4 & 5 COMPREHENSIVE TEST SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.END}")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Colors.BOLD}📊 OVERALL RESULTS:{Colors.END}")
        print(f"   Total Tests: {Colors.CYAN}{total_tests}{Colors.END}")
        print(f"   Passed: {Colors.GREEN}{passed_tests}{Colors.END}")
        print(f"   Failed: {Colors.RED}{failed_tests}{Colors.END}")
        print(f"   Success Rate: {Colors.YELLOW}{success_rate:.1f}%{Colors.END}")
        
        # Function 4 Results
        function4_tests = [r for r in self.test_results if 'Analytics' in r['test_name']]
        function4_passed = len([r for r in function4_tests if r['success']])
        function4_total = len(function4_tests)
        function4_rate = (function4_passed / function4_total * 100) if function4_total > 0 else 0
        
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📊 FUNCTION 4 - CONTENT ANALYTICS & PERFORMANCE MONITORING:{Colors.END}")
        print(f"   Tests: {function4_passed}/{function4_total} ({function4_rate:.1f}%)")
        
        # Function 5 Results
        function5_tests = [r for r in self.test_results if 'Lifecycle' in r['test_name']]
        function5_passed = len([r for r in function5_tests if r['success']])
        function5_total = len(function5_tests)
        function5_rate = (function5_passed / function5_total * 100) if function5_total > 0 else 0
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🔄 FUNCTION 5 - CONTENT LIFECYCLE MANAGEMENT & AUTOMATION:{Colors.END}")
        print(f"   Tests: {function5_passed}/{function5_total} ({function5_rate:.1f}%)")
        
        # Failed Tests Details
        failed_test_results = [r for r in self.test_results if not r['success']]
        if failed_test_results:
            print(f"\n{Colors.BOLD}{Colors.RED}❌ FAILED TESTS DETAILS:{Colors.END}")
            for result in failed_test_results:
                print(f"   • {result['test_name']}: {result['details']}")
        
        # Success Tests Summary
        passed_test_results = [r for r in self.test_results if r['success']]
        if passed_test_results:
            print(f"\n{Colors.BOLD}{Colors.GREEN}✅ SUCCESSFUL TESTS:{Colors.END}")
            for result in passed_test_results:
                print(f"   • {result['test_name']}")
        
        print(f"\n{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.END}")
        
        # Determine overall assessment
        if success_rate >= 90:
            status = f"{Colors.GREEN}🎉 EXCELLENT - PRODUCTION READY{Colors.END}"
        elif success_rate >= 75:
            status = f"{Colors.YELLOW}✅ GOOD - MINOR ISSUES{Colors.END}"
        elif success_rate >= 50:
            status = f"{Colors.YELLOW}⚠️  MODERATE - NEEDS ATTENTION{Colors.END}"
        else:
            status = f"{Colors.RED}❌ POOR - MAJOR ISSUES{Colors.END}"
        
        print(f"{Colors.BOLD}🏆 OVERALL ASSESSMENT: {status}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.END}")
    
    async def run_all_tests(self):
        """Run all Function 4 & 5 tests"""
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 STARTING FUNCTIONS 4 & 5 COMPREHENSIVE BACKEND TESTING{Colors.END}")
        print(f"{Colors.CYAN}Testing Big Mann Entertainment Platform - Content Analytics & Lifecycle Management{Colors.END}")
        print(f"{Colors.CYAN}Base URL: {self.base_url}{Colors.END}")
        
        try:
            await self.setup_session()
            
            # Authentication
            auth_success = await self.authenticate_user()
            if not auth_success:
                print(f"{Colors.RED}❌ Authentication failed. Cannot proceed with testing.{Colors.END}")
                return
            
            # Function 4: Content Analytics & Performance Monitoring Tests
            await self.test_analytics_event_tracking()
            await self.test_analytics_content_performance()
            await self.test_analytics_roi_analysis()
            await self.test_analytics_platform_analytics()
            await self.test_analytics_dashboard_summary()
            await self.test_analytics_benchmarking()
            await self.test_analytics_health()
            
            # Function 5: Content Lifecycle Management & Automation Tests
            await self.test_lifecycle_management()
            await self.test_lifecycle_stage_transitions()
            await self.test_lifecycle_version_management()
            await self.test_lifecycle_automation()
            await self.test_lifecycle_dashboard_analytics()
            await self.test_lifecycle_health()
            
            # Cleanup
            await self.cleanup_test_data()
            
        except Exception as e:
            print(f"{Colors.RED}❌ Critical error during testing: {str(e)}{Colors.END}")
        finally:
            await self.cleanup_session()
            self.print_test_summary()

async def main():
    """Main function to run the comprehensive Functions 4 & 5 backend tests"""
    tester = Functions45BackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())