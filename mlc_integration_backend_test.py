#!/usr/bin/env python3
"""
MLC Integration Backend Testing
Big Mann Entertainment Platform - Comprehensive MLC Testing

This script tests all MLC (Mechanical Licensing Collective) integration endpoints
including work registration, distribution management, usage reporting, and compliance tracking.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

# Test Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://creator-profile-hub-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class MLCIntegrationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = "test_user_mlc_2024"
        self.test_work_ids = []
        self.test_distribution_ids = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
    async def test_mlc_integration_status(self):
        """Test MLC integration status endpoint"""
        try:
            url = f"{API_BASE}/mlc/integration/status"
            async with self.session.get(url) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    integration_status = data.get("integration_status", {})
                    required_fields = ["mlc_connected", "api_version", "capabilities", "supported_territories"]
                    
                    missing_fields = [field for field in required_fields if field not in integration_status]
                    if missing_fields:
                        self.log_test_result(
                            "MLC Integration Status",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                        return False
                    
                    capabilities = integration_status.get("capabilities", [])
                    expected_capabilities = [
                        "work_registration", "distribution_management", "usage_reporting",
                        "mechanical_licensing", "royalty_tracking", "compliance_monitoring"
                    ]
                    
                    missing_capabilities = [cap for cap in expected_capabilities if cap not in capabilities]
                    if missing_capabilities:
                        self.log_test_result(
                            "MLC Integration Status",
                            False,
                            f"Missing capabilities: {missing_capabilities}",
                            data
                        )
                        return False
                    
                    self.log_test_result(
                        "MLC Integration Status",
                        True,
                        f"Integration active with {len(capabilities)} capabilities, {integration_status.get('supported_dsps', 0)} DSPs"
                    )
                    return True
                else:
                    self.log_test_result(
                        "MLC Integration Status",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("MLC Integration Status", False, f"Exception: {str(e)}")
            return False
            
    async def test_available_dsps(self):
        """Test GET /api/mlc/dsps endpoint"""
        try:
            url = f"{API_BASE}/mlc/dsps"
            params = {"user_id": self.test_user_id}
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    dsps = data.get("dsps", [])
                    total_dsps = data.get("total_dsps", 0)
                    mlc_integrated = data.get("mlc_integrated", False)
                    
                    if not dsps:
                        self.log_test_result(
                            "Available DSPs",
                            False,
                            "No DSPs returned",
                            data
                        )
                        return False
                    
                    # Check if MLC is included
                    mlc_found = any(dsp.get("name") == "Mechanical Licensing Collective" for dsp in dsps)
                    if not mlc_found:
                        self.log_test_result(
                            "Available DSPs",
                            False,
                            "MLC not found in DSP list",
                            data
                        )
                        return False
                    
                    # Verify DSP metadata
                    required_dsp_fields = ["name", "type", "territories", "integration_status"]
                    for dsp in dsps:
                        missing_fields = [field for field in required_dsp_fields if field not in dsp]
                        if missing_fields:
                            self.log_test_result(
                                "Available DSPs",
                                False,
                                f"DSP {dsp.get('name', 'Unknown')} missing fields: {missing_fields}",
                                data
                            )
                            return False
                    
                    self.log_test_result(
                        "Available DSPs",
                        True,
                        f"Retrieved {total_dsps} DSPs, MLC integrated: {mlc_integrated}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Available DSPs",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Available DSPs", False, f"Exception: {str(e)}")
            return False
            
    async def test_register_musical_work(self):
        """Test POST /api/mlc/works/register endpoint"""
        try:
            url = f"{API_BASE}/mlc/works/register"
            params = {"user_id": self.test_user_id}
            
            # Test with valid work data
            work_data = {
                "title": "Test Song for MLC Registration",
                "composers": ["John Spivey", "Test Composer"],
                "publishers": ["Big Mann Music Publishing"],
                "duration_seconds": 180,
                "genres": ["Pop", "Electronic"],
                "copyright_owner": "Big Mann Entertainment",
                "mechanical_rights_owner": "Big Mann Music Publishing"
            }
            
            async with self.session.post(url, params=params, json=work_data) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    work_id = data.get("work_id")
                    mlc_registration = data.get("mlc_registration", {})
                    
                    if not work_id:
                        self.log_test_result(
                            "Register Musical Work",
                            False,
                            "No work_id returned",
                            data
                        )
                        return False
                    
                    # Store work ID for later tests
                    self.test_work_ids.append(work_id)
                    
                    # Verify ISWC and ISRC generation
                    required_fields = ["mlc_work_id", "registration_status", "iswc_assigned"]
                    missing_fields = [field for field in required_fields if field not in mlc_registration]
                    
                    if missing_fields:
                        self.log_test_result(
                            "Register Musical Work",
                            False,
                            f"Missing MLC registration fields: {missing_fields}",
                            data
                        )
                        return False
                    
                    self.log_test_result(
                        "Register Musical Work",
                        True,
                        f"Work registered with ID: {work_id}, ISWC: {mlc_registration.get('iswc_assigned')}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Register Musical Work",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Register Musical Work", False, f"Exception: {str(e)}")
            return False
            
    async def test_register_work_validation(self):
        """Test work registration validation for required fields"""
        try:
            url = f"{API_BASE}/mlc/works/register"
            params = {"user_id": self.test_user_id}
            
            # Test with missing required fields
            invalid_work_data = {
                "title": "",  # Empty title
                "composers": [],  # Empty composers
                "publishers": ["Big Mann Music Publishing"],
                "duration_seconds": 180
                # Missing copyright_owner and mechanical_rights_owner
            }
            
            async with self.session.post(url, params=params, json=invalid_work_data) as response:
                data = await response.json()
                
                # Should fail validation
                if response.status != 200 or not data.get("success"):
                    self.log_test_result(
                        "Work Registration Validation",
                        True,
                        "Correctly rejected invalid work data"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Work Registration Validation",
                        False,
                        "Should have rejected invalid work data",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Work Registration Validation", False, f"Exception: {str(e)}")
            return False
            
    async def test_get_registered_works(self):
        """Test GET /api/mlc/works endpoint"""
        try:
            url = f"{API_BASE}/mlc/works"
            params = {"user_id": self.test_user_id}
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    works = data.get("works", [])
                    total_works = data.get("total_works", 0)
                    
                    if total_works == 0:
                        self.log_test_result(
                            "Get Registered Works",
                            False,
                            "No works returned (should have sample data)",
                            data
                        )
                        return False
                    
                    # Verify works data format
                    for work in works:
                        required_fields = ["work_id", "title", "composers", "publishers", "copyright_owner"]
                        missing_fields = [field for field in required_fields if field not in work]
                        if missing_fields:
                            self.log_test_result(
                                "Get Registered Works",
                                False,
                                f"Work missing fields: {missing_fields}",
                                data
                            )
                            return False
                    
                    self.log_test_result(
                        "Get Registered Works",
                        True,
                        f"Retrieved {total_works} registered works"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Get Registered Works",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Get Registered Works", False, f"Exception: {str(e)}")
            return False
            
    async def test_create_distribution_request(self):
        """Test POST /api/mlc/distribution/request endpoint"""
        try:
            url = f"{API_BASE}/mlc/distribution/request"
            params = {"user_id": self.test_user_id}
            
            # Use test work IDs or sample work IDs
            work_ids = self.test_work_ids if self.test_work_ids else ["sample_work_1", "sample_work_2"]
            
            distribution_data = {
                "asset_id": "test_asset_001",
                "work_ids": work_ids,
                "target_dsps": ["Spotify", "Apple Music", "Amazon Music"],
                "license_types": ["mechanical", "streaming"],
                "distribution_date": datetime.now(timezone.utc).isoformat(),
                "territory_codes": ["US", "CA", "GB"],
                "metadata": {
                    "initiated_by": self.test_user_id,
                    "test_distribution": True
                }
            }
            
            async with self.session.post(url, params=params, json=distribution_data) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    request_id = data.get("request_id")
                    distribution_info = data.get("distribution_info", {})
                    
                    if not request_id:
                        self.log_test_result(
                            "Create Distribution Request",
                            False,
                            "No request_id returned",
                            data
                        )
                        return False
                    
                    # Store distribution ID for later tests
                    self.test_distribution_ids.append(request_id)
                    
                    # Verify processing fees calculation
                    processing_fees = distribution_info.get("processing_fees", {})
                    total_fees = distribution_info.get("total_processing_fees", 0)
                    
                    if not processing_fees or total_fees <= 0:
                        self.log_test_result(
                            "Create Distribution Request",
                            False,
                            "Processing fees not calculated correctly",
                            data
                        )
                        return False
                    
                    # Verify estimated delivery date
                    estimated_delivery = distribution_info.get("estimated_delivery_date")
                    if not estimated_delivery:
                        self.log_test_result(
                            "Create Distribution Request",
                            False,
                            "No estimated delivery date provided",
                            data
                        )
                        return False
                    
                    self.log_test_result(
                        "Create Distribution Request",
                        True,
                        f"Distribution request created: {request_id}, Total fees: ${total_fees}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Create Distribution Request",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Create Distribution Request", False, f"Exception: {str(e)}")
            return False
            
    async def test_get_distribution_requests(self):
        """Test GET /api/mlc/distribution/requests endpoint"""
        try:
            url = f"{API_BASE}/mlc/distribution/requests"
            params = {"user_id": self.test_user_id}
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    requests = data.get("requests", [])
                    total_requests = data.get("total_requests", 0)
                    
                    # Verify request data format
                    for req in requests:
                        required_fields = ["request_id", "asset_id", "work_ids", "target_dsps"]
                        missing_fields = [field for field in required_fields if field not in req]
                        if missing_fields:
                            self.log_test_result(
                                "Get Distribution Requests",
                                False,
                                f"Request missing fields: {missing_fields}",
                                data
                            )
                            return False
                    
                    self.log_test_result(
                        "Get Distribution Requests",
                        True,
                        f"Retrieved {total_requests} distribution requests"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Get Distribution Requests",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Get Distribution Requests", False, f"Exception: {str(e)}")
            return False
            
    async def test_usage_reports(self):
        """Test GET /api/mlc/reports/usage endpoint"""
        try:
            # Test without filters
            url = f"{API_BASE}/mlc/reports/usage"
            params = {"user_id": self.test_user_id}
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    reports = data.get("reports", [])
                    total_reports = data.get("total_reports", 0)
                    
                    if total_reports == 0:
                        self.log_test_result(
                            "Usage Reports (No Filters)",
                            False,
                            "No usage reports returned (should have sample data)",
                            data
                        )
                        return False
                    
                    # Verify report data format
                    for report in reports:
                        required_fields = ["report_id", "work_id", "dsp_name", "play_count", "total_mechanical_royalty"]
                        missing_fields = [field for field in required_fields if field not in report]
                        if missing_fields:
                            self.log_test_result(
                                "Usage Reports (No Filters)",
                                False,
                                f"Report missing fields: {missing_fields}",
                                data
                            )
                            return False
                    
                    self.log_test_result(
                        "Usage Reports (No Filters)",
                        True,
                        f"Retrieved {total_reports} usage reports"
                    )
                    
                    # Test with filters
                    return await self.test_usage_reports_with_filters()
                else:
                    self.log_test_result(
                        "Usage Reports (No Filters)",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Usage Reports (No Filters)", False, f"Exception: {str(e)}")
            return False
            
    async def test_usage_reports_with_filters(self):
        """Test usage reports with filters"""
        try:
            url = f"{API_BASE}/mlc/reports/usage"
            params = {
                "user_id": self.test_user_id,
                "dsp_name": "Spotify",
                "territory": "US"
            }
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    reports = data.get("reports", [])
                    filters_applied = data.get("filters_applied", {})
                    
                    # Verify filters were applied
                    if filters_applied.get("dsp_name") != "Spotify" or filters_applied.get("territory") != "US":
                        self.log_test_result(
                            "Usage Reports (With Filters)",
                            False,
                            "Filters not applied correctly",
                            data
                        )
                        return False
                    
                    # Verify filtered results
                    for report in reports:
                        if report.get("dsp_name") != "Spotify" or report.get("territory") != "US":
                            self.log_test_result(
                                "Usage Reports (With Filters)",
                                False,
                                "Filter results contain incorrect data",
                                data
                            )
                            return False
                    
                    self.log_test_result(
                        "Usage Reports (With Filters)",
                        True,
                        f"Retrieved {len(reports)} filtered reports (Spotify, US)"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Usage Reports (With Filters)",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Usage Reports (With Filters)", False, f"Exception: {str(e)}")
            return False
            
    async def test_mlc_analytics(self):
        """Test GET /api/mlc/analytics endpoint"""
        try:
            url = f"{API_BASE}/mlc/analytics"
            params = {"user_id": self.test_user_id}
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    analytics = data.get("analytics", {})
                    
                    # Verify analytics structure
                    required_sections = ["overview", "dsp_performance", "territory_performance", "top_performing_works"]
                    missing_sections = [section for section in required_sections if section not in analytics]
                    
                    if missing_sections:
                        self.log_test_result(
                            "MLC Analytics",
                            False,
                            f"Missing analytics sections: {missing_sections}",
                            data
                        )
                        return False
                    
                    # Verify overview data
                    overview = analytics.get("overview", {})
                    required_overview_fields = ["total_registered_works", "total_plays", "total_mechanical_royalties"]
                    missing_overview = [field for field in required_overview_fields if field not in overview]
                    
                    if missing_overview:
                        self.log_test_result(
                            "MLC Analytics",
                            False,
                            f"Missing overview fields: {missing_overview}",
                            data
                        )
                        return False
                    
                    # Verify DSP performance breakdown
                    dsp_performance = analytics.get("dsp_performance", {})
                    if not dsp_performance:
                        self.log_test_result(
                            "MLC Analytics",
                            False,
                            "No DSP performance data",
                            data
                        )
                        return False
                    
                    # Verify territory performance data
                    territory_performance = analytics.get("territory_performance", {})
                    if not territory_performance:
                        self.log_test_result(
                            "MLC Analytics",
                            False,
                            "No territory performance data",
                            data
                        )
                        return False
                    
                    # Verify top performing works data
                    top_works = analytics.get("top_performing_works", [])
                    if not top_works:
                        self.log_test_result(
                            "MLC Analytics",
                            False,
                            "No top performing works data",
                            data
                        )
                        return False
                    
                    self.log_test_result(
                        "MLC Analytics",
                        True,
                        f"Analytics: {overview.get('total_registered_works', 0)} works, {len(dsp_performance)} DSPs, {len(territory_performance)} territories"
                    )
                    return True
                else:
                    self.log_test_result(
                        "MLC Analytics",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("MLC Analytics", False, f"Exception: {str(e)}")
            return False
            
    async def test_compliance_status(self):
        """Test GET /api/mlc/compliance/status endpoint"""
        try:
            url = f"{API_BASE}/mlc/compliance/status"
            params = {"user_id": self.test_user_id}
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    compliance_status = data.get("compliance_status", {})
                    overall_compliant = data.get("overall_compliant")
                    
                    # Verify compliance indicators
                    required_indicators = ["mlc_registration_current", "usage_reporting_up_to_date", "mechanical_licenses_valid"]
                    missing_indicators = [indicator for indicator in required_indicators if indicator not in compliance_status]
                    
                    if missing_indicators:
                        self.log_test_result(
                            "Compliance Status",
                            False,
                            f"Missing compliance indicators: {missing_indicators}",
                            data
                        )
                        return False
                    
                    # Verify overall compliance calculation
                    if overall_compliant is None:
                        self.log_test_result(
                            "Compliance Status",
                            False,
                            "Overall compliance not calculated",
                            data
                        )
                        return False
                    
                    compliance_count = sum(1 for indicator in required_indicators if compliance_status.get(indicator))
                    expected_overall = compliance_count == len(required_indicators)
                    
                    if overall_compliant != expected_overall:
                        self.log_test_result(
                            "Compliance Status",
                            False,
                            f"Overall compliance calculation incorrect: {overall_compliant} vs expected {expected_overall}",
                            data
                        )
                        return False
                    
                    self.log_test_result(
                        "Compliance Status",
                        True,
                        f"Compliance status: {compliance_count}/{len(required_indicators)} indicators, Overall: {overall_compliant}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Compliance Status",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Compliance Status", False, f"Exception: {str(e)}")
            return False
            
    async def test_single_work_distribution(self):
        """Test POST /api/mlc/works/{work_id}/distribute endpoint"""
        try:
            # Use first available work ID
            if not self.test_work_ids:
                # Try to get works first
                await self.test_get_registered_works()
                if not self.test_work_ids:
                    # Use a sample work ID
                    work_id = "sample_work_1"
                else:
                    work_id = self.test_work_ids[0]
            else:
                work_id = self.test_work_ids[0]
            
            url = f"{API_BASE}/mlc/works/{work_id}/distribute"
            params = {"user_id": self.test_user_id}
            
            distribution_data = {
                "target_dsps": ["Spotify", "Apple Music"],
                "territory_codes": ["US", "CA"]
            }
            
            async with self.session.post(url, params=params, json=distribution_data) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    request_id = data.get("request_id")
                    distribution_info = data.get("distribution_info", {})
                    
                    if not request_id:
                        self.log_test_result(
                            "Single Work Distribution",
                            False,
                            "No request_id returned",
                            data
                        )
                        return False
                    
                    # Verify distribution request creation
                    if not distribution_info:
                        self.log_test_result(
                            "Single Work Distribution",
                            False,
                            "No distribution info returned",
                            data
                        )
                        return False
                    
                    self.log_test_result(
                        "Single Work Distribution",
                        True,
                        f"Single work distribution created: {request_id} for work {work_id}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Single Work Distribution",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Single Work Distribution", False, f"Exception: {str(e)}")
            return False
            
    async def test_royalties_summary(self):
        """Test GET /api/mlc/royalties/summary endpoint"""
        try:
            url = f"{API_BASE}/mlc/royalties/summary"
            params = {
                "user_id": self.test_user_id,
                "period_days": 30
            }
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    summary = data.get("summary", {})
                    dsp_breakdown = data.get("dsp_breakdown", {})
                    
                    # Verify summary structure
                    required_summary_fields = ["total_mechanical_royalties", "total_plays", "unique_works", "unique_dsps"]
                    missing_summary = [field for field in required_summary_fields if field not in summary]
                    
                    if missing_summary:
                        self.log_test_result(
                            "Royalties Summary",
                            False,
                            f"Missing summary fields: {missing_summary}",
                            data
                        )
                        return False
                    
                    # Verify calculations
                    total_royalties = summary.get("total_mechanical_royalties", 0)
                    total_plays = summary.get("total_plays", 0)
                    avg_royalty = summary.get("average_royalty_per_play", 0)
                    
                    if total_plays > 0:
                        expected_avg = total_royalties / total_plays
                        if abs(avg_royalty - expected_avg) > 0.000001:  # Allow for floating point precision
                            self.log_test_result(
                                "Royalties Summary",
                                False,
                                f"Average royalty calculation incorrect: {avg_royalty} vs expected {expected_avg}",
                                data
                            )
                            return False
                    
                    # Verify DSP breakdown
                    if not dsp_breakdown:
                        self.log_test_result(
                            "Royalties Summary",
                            False,
                            "No DSP breakdown provided",
                            data
                        )
                        return False
                    
                    # Test with different time periods
                    success_7_days = await self.test_royalties_summary_period(7)
                    success_90_days = await self.test_royalties_summary_period(90)
                    
                    if not (success_7_days and success_90_days):
                        return False
                    
                    self.log_test_result(
                        "Royalties Summary",
                        True,
                        f"30-day summary: ${total_royalties}, {total_plays} plays, {len(dsp_breakdown)} DSPs"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Royalties Summary",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Royalties Summary", False, f"Exception: {str(e)}")
            return False
            
    async def test_royalties_summary_period(self, period_days: int):
        """Test royalties summary with different time periods"""
        try:
            url = f"{API_BASE}/mlc/royalties/summary"
            params = {
                "user_id": self.test_user_id,
                "period_days": period_days
            }
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    summary = data.get("summary", {})
                    if summary.get("period_days") != period_days:
                        self.log_test_result(
                            f"Royalties Summary ({period_days} days)",
                            False,
                            f"Period days mismatch: {summary.get('period_days')} vs {period_days}",
                            data
                        )
                        return False
                    
                    self.log_test_result(
                        f"Royalties Summary ({period_days} days)",
                        True,
                        f"${summary.get('total_mechanical_royalties', 0)} over {period_days} days"
                    )
                    return True
                else:
                    self.log_test_result(
                        f"Royalties Summary ({period_days} days)",
                        False,
                        f"HTTP {response.status}",
                        data
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(f"Royalties Summary ({period_days} days)", False, f"Exception: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all MLC integration tests"""
        print("🎵 STARTING MLC INTEGRATION COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print()
        
        await self.setup_session()
        
        try:
            # Test sequence
            tests = [
                ("MLC Integration Status", self.test_mlc_integration_status),
                ("Available DSPs", self.test_available_dsps),
                ("Register Musical Work", self.test_register_musical_work),
                ("Work Registration Validation", self.test_register_work_validation),
                ("Get Registered Works", self.test_get_registered_works),
                ("Create Distribution Request", self.test_create_distribution_request),
                ("Get Distribution Requests", self.test_get_distribution_requests),
                ("Usage Reports", self.test_usage_reports),
                ("MLC Analytics", self.test_mlc_analytics),
                ("Compliance Status", self.test_compliance_status),
                ("Single Work Distribution", self.test_single_work_distribution),
                ("Royalties Summary", self.test_royalties_summary)
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                print(f"Running: {test_name}")
                try:
                    success = await test_func()
                    if success:
                        passed_tests += 1
                except Exception as e:
                    self.log_test_result(test_name, False, f"Test execution error: {str(e)}")
                
                # Small delay between tests
                await asyncio.sleep(0.5)
            
            # Print summary
            print("=" * 80)
            print("🎵 MLC INTEGRATION TESTING SUMMARY")
            print("=" * 80)
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            print()
            
            # Print detailed results
            print("DETAILED RESULTS:")
            print("-" * 40)
            for result in self.test_results:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}")
                if result["details"]:
                    print(f"   {result['details']}")
            
            print()
            if passed_tests == total_tests:
                print("🎉 ALL MLC INTEGRATION TESTS PASSED!")
                print("✅ MLC integration is fully functional and ready for production")
            else:
                print("⚠️  SOME TESTS FAILED")
                print("❌ Review failed tests and fix issues before production deployment")
            
            return passed_tests == total_tests
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = MLCIntegrationTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())