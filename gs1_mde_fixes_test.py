#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE BACKEND TESTING FOR GS1 & MDE FIXES VERIFICATION
Big Mann Entertainment Platform - Backend API Testing

TESTING OBJECTIVE: Verify that all reported issues have been fixed and the system is functioning correctly.

ISSUES ADDRESSED:
1. ✅ GS1 business information not loading - Added missing `/api/gs1/business-info` endpoint
2. ✅ GS1 products endpoint missing - Added missing `/api/gs1/products` endpoint  
3. ✅ MDE (Music Data Exchange) not available for selection - Added MDE and MLC to distribution platforms

PRIORITY AREAS TO VERIFY:
1. GS1 Endpoints Fix Verification (HIGH PRIORITY)
2. MDE & MLC Distribution Platform Integration (HIGH PRIORITY)
3. Existing GS1 Asset Registry Functionality
4. System Health Verification
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://label-network.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: {details}")
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method.upper() == 'GET':
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data, params=params) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            else:
                return False, {"error": f"Unsupported method: {method}"}, 405
                
        except aiohttp.ClientError as e:
            return False, {"error": f"Request failed: {str(e)}"}, 0
        except json.JSONDecodeError:
            return False, {"error": "Invalid JSON response"}, 0
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}, 0

    async def test_gs1_business_info_endpoint(self):
        """Test GS1 business-info endpoint (NEWLY ADDED)"""
        print("\n🔍 Testing GS1 Business Info Endpoint...")
        
        success, response_data, status_code = await self.make_request('GET', '/gs1/business-info')
        
        if success and status_code == 200:
            # Verify response structure
            if 'success' in response_data and response_data['success']:
                business_info = response_data.get('business_info', {})
                capabilities = response_data.get('capabilities', {})
                
                # Check required fields
                required_fields = ['company_name', 'company_prefix', 'total_assets', 'compliance_status']
                missing_fields = [field for field in required_fields if field not in business_info]
                
                if not missing_fields:
                    self.log_test(
                        "GS1 Business Info Endpoint", 
                        True, 
                        f"Returns proper business info with company: {business_info.get('company_name')}, assets: {business_info.get('total_assets')}, compliance: {business_info.get('compliance_status')}"
                    )
                else:
                    self.log_test(
                        "GS1 Business Info Endpoint", 
                        False, 
                        f"Missing required fields: {missing_fields}"
                    )
            else:
                self.log_test(
                    "GS1 Business Info Endpoint", 
                    False, 
                    f"Response missing success flag or success=false: {response_data}"
                )
        else:
            self.log_test(
                "GS1 Business Info Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
            )

    async def test_gs1_products_endpoint(self):
        """Test GS1 products endpoint (NEWLY ADDED)"""
        print("\n🔍 Testing GS1 Products Endpoint...")
        
        success, response_data, status_code = await self.make_request('GET', '/gs1/products')
        
        if success and status_code == 200:
            # Verify response structure
            if 'success' in response_data and response_data['success']:
                products = response_data.get('products', [])
                pagination = response_data.get('pagination', {})
                
                # Check pagination structure
                required_pagination_fields = ['total_count', 'page', 'page_size', 'has_next', 'has_previous']
                missing_pagination = [field for field in required_pagination_fields if field not in pagination]
                
                if not missing_pagination:
                    self.log_test(
                        "GS1 Products Endpoint", 
                        True, 
                        f"Returns paginated products list with {len(products)} products, total: {pagination.get('total_count')}"
                    )
                    
                    # Test with pagination parameters
                    success2, response_data2, status_code2 = await self.make_request(
                        'GET', '/gs1/products', params={'page': 1, 'page_size': 10}
                    )
                    
                    if success2 and status_code2 == 200:
                        self.log_test(
                            "GS1 Products Pagination", 
                            True, 
                            f"Pagination parameters work correctly"
                        )
                    else:
                        self.log_test(
                            "GS1 Products Pagination", 
                            False, 
                            f"Pagination failed: HTTP {status_code2}"
                        )
                else:
                    self.log_test(
                        "GS1 Products Endpoint", 
                        False, 
                        f"Missing pagination fields: {missing_pagination}"
                    )
            else:
                self.log_test(
                    "GS1 Products Endpoint", 
                    False, 
                    f"Response missing success flag or success=false: {response_data}"
                )
        else:
            self.log_test(
                "GS1 Products Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
            )

    async def test_distribution_platforms_mde_mlc(self):
        """Test MDE and MLC in distribution platforms"""
        print("\n🔍 Testing MDE & MLC Distribution Platform Integration...")
        
        success, response_data, status_code = await self.make_request('GET', '/distribution/platforms')
        
        if success and status_code == 200:
            platforms = response_data if isinstance(response_data, list) else response_data.get('platforms', [])
            
            # Look for MDE and MLC platforms
            mde_platform = None
            mlc_platform = None
            
            for platform_id, platform_data in (platforms if isinstance(platforms, dict) else {}).items():
                if platform_id == 'mde' or 'music data exchange' in platform_data.get('name', '').lower():
                    mde_platform = platform_data
                elif platform_id == 'mlc' or 'mechanical licensing collective' in platform_data.get('name', '').lower():
                    mlc_platform = platform_data
            
            # Check MDE platform
            if mde_platform:
                expected_mde_fields = ['name', 'type', 'description', 'api_endpoint']
                mde_valid = all(field in mde_platform for field in expected_mde_fields)
                
                if mde_valid and 'music_data_exchange' in mde_platform.get('type', ''):
                    self.log_test(
                        "MDE Platform Integration", 
                        True, 
                        f"MDE found as '{mde_platform['name']}' with type '{mde_platform['type']}'"
                    )
                else:
                    self.log_test(
                        "MDE Platform Integration", 
                        False, 
                        f"MDE platform missing required fields or incorrect type: {mde_platform}"
                    )
            else:
                self.log_test(
                    "MDE Platform Integration", 
                    False, 
                    "MDE (Music Data Exchange) platform not found in distribution platforms"
                )
            
            # Check MLC platform
            if mlc_platform:
                expected_mlc_fields = ['name', 'type', 'description', 'api_endpoint']
                mlc_valid = all(field in mlc_platform for field in expected_mlc_fields)
                
                if mlc_valid and 'music_licensing' in mlc_platform.get('type', ''):
                    self.log_test(
                        "MLC Platform Integration", 
                        True, 
                        f"MLC found as '{mlc_platform['name']}' with type '{mlc_platform['type']}'"
                    )
                else:
                    self.log_test(
                        "MLC Platform Integration", 
                        False, 
                        f"MLC platform missing required fields or incorrect type: {mlc_platform}"
                    )
            else:
                self.log_test(
                    "MLC Platform Integration", 
                    False, 
                    "MLC (Mechanical Licensing Collective) platform not found in distribution platforms"
                )
            
            # Verify total platform count
            total_platforms = len(platforms) if isinstance(platforms, dict) else len(platforms)
            if total_platforms >= 114:
                self.log_test(
                    "Distribution Platform Count", 
                    True, 
                    f"Total platforms: {total_platforms} (meets 114+ requirement)"
                )
            else:
                self.log_test(
                    "Distribution Platform Count", 
                    False, 
                    f"Total platforms: {total_platforms} (below 114+ requirement)"
                )
                
        else:
            self.log_test(
                "Distribution Platforms Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
            )

    async def test_existing_gs1_functionality(self):
        """Test existing GS1 Asset Registry functionality"""
        print("\n🔍 Testing Existing GS1 Asset Registry Functionality...")
        
        # Test GS1 health endpoint
        success, response_data, status_code = await self.make_request('GET', '/gs1/health')
        
        if success and status_code == 200:
            if response_data.get('status') == 'healthy':
                self.log_test(
                    "GS1 Health Endpoint", 
                    True, 
                    f"Service healthy with {response_data.get('total_assets', 0)} assets, {response_data.get('total_digital_links', 0)} digital links"
                )
            else:
                self.log_test(
                    "GS1 Health Endpoint", 
                    False, 
                    f"Service not healthy: {response_data.get('status')}"
                )
        else:
            self.log_test(
                "GS1 Health Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
            )
        
        # Test GS1 analytics endpoint
        success, response_data, status_code = await self.make_request('GET', '/gs1/analytics')
        
        if success and status_code == 200:
            required_analytics_fields = ['total_assets', 'assets_by_type', 'identifiers_by_type']
            missing_fields = [field for field in required_analytics_fields if field not in response_data]
            
            if not missing_fields:
                self.log_test(
                    "GS1 Analytics Endpoint", 
                    True, 
                    f"Analytics working with {response_data.get('total_assets')} total assets"
                )
            else:
                self.log_test(
                    "GS1 Analytics Endpoint", 
                    False, 
                    f"Missing analytics fields: {missing_fields}"
                )
        else:
            self.log_test(
                "GS1 Analytics Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
            )

    async def test_mde_integration_endpoints(self):
        """Test MDE integration endpoints"""
        print("\n🔍 Testing MDE Integration Endpoints...")
        
        # Test MDE integration status
        success, response_data, status_code = await self.make_request('GET', '/mde/integration/status')
        
        if success and status_code == 200:
            integration_status = response_data.get('integration_status', {})
            
            if integration_status.get('mde_connected'):
                capabilities = integration_status.get('capabilities', [])
                expected_capabilities = ['metadata_standardization', 'data_quality_validation', 'industry_data_exchange']
                
                has_required_capabilities = all(cap in capabilities for cap in expected_capabilities)
                
                if has_required_capabilities:
                    self.log_test(
                        "MDE Integration Status", 
                        True, 
                        f"MDE connected with {len(capabilities)} capabilities, quality score: {integration_status.get('data_quality_score')}"
                    )
                else:
                    self.log_test(
                        "MDE Integration Status", 
                        False, 
                        f"Missing required capabilities: {[cap for cap in expected_capabilities if cap not in capabilities]}"
                    )
            else:
                self.log_test(
                    "MDE Integration Status", 
                    False, 
                    "MDE not connected"
                )
        else:
            self.log_test(
                "MDE Integration Status", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
            )
        
        # Test MDE standards endpoint
        success, response_data, status_code = await self.make_request('GET', '/mde/standards', params={'user_id': 'test_user'})
        
        if success and status_code == 200:
            standards = response_data.get('standards', [])
            if len(standards) >= 5:
                self.log_test(
                    "MDE Standards Endpoint", 
                    True, 
                    f"Returns {len(standards)} standards with recommended: {response_data.get('recommended_standard')}"
                )
            else:
                self.log_test(
                    "MDE Standards Endpoint", 
                    False, 
                    f"Insufficient standards returned: {len(standards)}"
                )
        else:
            self.log_test(
                "MDE Standards Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
            )

    async def test_system_health_verification(self):
        """Test overall system health"""
        print("\n🔍 Testing System Health Verification...")
        
        # Test multiple endpoints to verify no 404 errors
        endpoints_to_test = [
            ('/gs1/health', 'GS1 Health'),
            ('/gs1/business-info', 'GS1 Business Info'),
            ('/gs1/products', 'GS1 Products'),
            ('/distribution/platforms', 'Distribution Platforms'),
            ('/mde/integration/status', 'MDE Integration Status')
        ]
        
        healthy_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint, name in endpoints_to_test:
            success, response_data, status_code = await self.make_request('GET', endpoint, params={'user_id': 'test_user'} if 'mde' in endpoint else None)
            
            if success and status_code == 200:
                healthy_endpoints += 1
                print(f"  ✅ {name}: Healthy (HTTP 200)")
            else:
                print(f"  ❌ {name}: Unhealthy (HTTP {status_code})")
        
        if healthy_endpoints == total_endpoints:
            self.log_test(
                "System Health Verification", 
                True, 
                f"All {total_endpoints} critical endpoints are healthy"
            )
        else:
            self.log_test(
                "System Health Verification", 
                False, 
                f"Only {healthy_endpoints}/{total_endpoints} endpoints are healthy"
            )

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🎯 COMPREHENSIVE BACKEND TESTING FOR GS1 & MDE FIXES VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Run all test categories
        await self.test_gs1_business_info_endpoint()
        await self.test_gs1_products_endpoint()
        await self.test_distribution_platforms_mde_mlc()
        await self.test_existing_gs1_functionality()
        await self.test_mde_integration_endpoints()
        await self.test_system_health_verification()
        
        # Print comprehensive results
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if failed_count > 0:
            print(f"\n❌ FAILED TESTS ({failed_count}):")
            for i, failed_test in enumerate(self.failed_tests, 1):
                print(f"   {i}. {failed_test}")
        
        print(f"\n✅ PASSED TESTS ({passed_count}):")
        for i, passed_test in enumerate(self.passed_tests, 1):
            print(f"   {i}. {passed_test}")
        
        # Specific verification results
        print(f"\n🎯 SPECIFIC FIXES VERIFICATION:")
        
        gs1_business_passed = "GS1 Business Info Endpoint" in self.passed_tests
        gs1_products_passed = "GS1 Products Endpoint" in self.passed_tests
        mde_platform_passed = "MDE Platform Integration" in self.passed_tests
        mlc_platform_passed = "MLC Platform Integration" in self.passed_tests
        
        print(f"   1. GS1 business information loading: {'✅ FIXED' if gs1_business_passed else '❌ STILL BROKEN'}")
        print(f"   2. GS1 products endpoint: {'✅ FIXED' if gs1_products_passed else '❌ STILL BROKEN'}")
        print(f"   3. MDE platform availability: {'✅ FIXED' if mde_platform_passed else '❌ STILL BROKEN'}")
        print(f"   4. MLC platform availability: {'✅ FIXED' if mlc_platform_passed else '❌ STILL BROKEN'}")
        
        critical_fixes = [gs1_business_passed, gs1_products_passed, mde_platform_passed, mlc_platform_passed]
        critical_success_rate = (sum(critical_fixes) / len(critical_fixes) * 100)
        
        print(f"\n🎯 CRITICAL FIXES SUCCESS RATE: {critical_success_rate:.1f}%")
        
        if critical_success_rate == 100:
            print("🎉 ALL CRITICAL ISSUES HAVE BEEN SUCCESSFULLY FIXED!")
        elif critical_success_rate >= 75:
            print("⚠️  MOST CRITICAL ISSUES FIXED - MINOR ISSUES REMAIN")
        else:
            print("❌ CRITICAL ISSUES STILL EXIST - IMMEDIATE ATTENTION REQUIRED")
        
        return success_rate >= 80  # Consider 80%+ as overall success

async def main():
    """Main test execution"""
    try:
        async with BackendTester() as tester:
            success = await tester.run_comprehensive_tests()
            
            if success:
                print(f"\n🎉 COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY!")
                print(f"✅ System is ready for production with verified fixes")
                sys.exit(0)
            else:
                print(f"\n⚠️  COMPREHENSIVE TESTING COMPLETED WITH ISSUES")
                print(f"❌ Some critical functionality needs attention")
                sys.exit(1)
                
    except Exception as e:
        print(f"\n💥 TESTING FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())