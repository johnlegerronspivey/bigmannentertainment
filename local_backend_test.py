#!/usr/bin/env python3
"""
🎯 LOCAL BACKEND TESTING FOR GS1 & MDE FIXES VERIFICATION
Big Mann Entertainment Platform - Local Backend API Testing

TESTING OBJECTIVE: Verify that all reported issues have been fixed and the system is functioning correctly.

ISSUES ADDRESSED:
1. ✅ GS1 business information not loading - Added missing `/api/gs1/business-info` endpoint
2. ✅ GS1 products endpoint missing - Added missing `/api/gs1/products` endpoint  
3. ✅ MDE (Music Data Exchange) not available for selection - Added MDE and MLC to distribution platforms
"""

import requests
import json
import sys
from datetime import datetime

# Use local backend URL
BACKEND_URL = "http://localhost:8001/api"

class LocalBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: {details}")
    
    def make_request(self, endpoint: str, params: dict = None):
        """Make HTTP GET request"""
        try:
            url = f"{self.backend_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            return response.status_code, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        except requests.exceptions.RequestException as e:
            return 0, {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return response.status_code, {"error": "Invalid JSON response"}
        except Exception as e:
            return 0, {"error": f"Unexpected error: {str(e)}"}

    def test_gs1_business_info_endpoint(self):
        """Test GS1 business-info endpoint (NEWLY ADDED)"""
        print("\n🔍 Testing GS1 Business Info Endpoint...")
        
        status_code, response_data = self.make_request('/gs1/business-info')
        
        if status_code == 200 and isinstance(response_data, dict):
            if response_data.get('success'):
                business_info = response_data.get('business_info', {})
                
                # Check required fields
                required_fields = ['company_name', 'company_prefix', 'total_assets', 'compliance_status']
                missing_fields = [field for field in required_fields if field not in business_info]
                
                if not missing_fields:
                    self.log_test(
                        "GS1 Business Info Endpoint", 
                        True, 
                        f"Company: {business_info.get('company_name')}, Assets: {business_info.get('total_assets')}, Status: {business_info.get('compliance_status')}"
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
                    f"Response success=false: {response_data}"
                )
        else:
            self.log_test(
                "GS1 Business Info Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else response_data}"
            )

    def test_gs1_products_endpoint(self):
        """Test GS1 products endpoint (NEWLY ADDED)"""
        print("\n🔍 Testing GS1 Products Endpoint...")
        
        status_code, response_data = self.make_request('/gs1/products')
        
        if status_code == 200 and isinstance(response_data, dict):
            if response_data.get('success'):
                products = response_data.get('products', [])
                pagination = response_data.get('pagination', {})
                
                # Check pagination structure
                required_pagination_fields = ['total_count', 'page', 'page_size', 'has_next', 'has_previous']
                missing_pagination = [field for field in required_pagination_fields if field not in pagination]
                
                if not missing_pagination:
                    self.log_test(
                        "GS1 Products Endpoint", 
                        True, 
                        f"Products: {len(products)}, Total: {pagination.get('total_count')}, Page: {pagination.get('page')}"
                    )
                    
                    # Test with pagination parameters
                    status_code2, response_data2 = self.make_request('/gs1/products', params={'page': 1, 'page_size': 10})
                    
                    if status_code2 == 200 and isinstance(response_data2, dict) and response_data2.get('success'):
                        self.log_test(
                            "GS1 Products Pagination", 
                            True, 
                            "Pagination parameters work correctly"
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
                    f"Response success=false: {response_data}"
                )
        else:
            self.log_test(
                "GS1 Products Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else response_data}"
            )

    def test_distribution_platforms_mde_mlc(self):
        """Test MDE and MLC in distribution platforms"""
        print("\n🔍 Testing MDE & MLC Distribution Platform Integration...")
        
        status_code, response_data = self.make_request('/distribution/platforms')
        
        if status_code == 200 and isinstance(response_data, dict):
            platforms = response_data.get('platforms', {})
            
            # Check MDE platform
            mde_platform = platforms.get('mde')
            if mde_platform:
                expected_mde_fields = ['name', 'type', 'description', 'api_endpoint']
                mde_valid = all(field in mde_platform for field in expected_mde_fields)
                
                if mde_valid and mde_platform.get('type') == 'music_data_exchange':
                    self.log_test(
                        "MDE Platform Integration", 
                        True, 
                        f"MDE: '{mde_platform['name']}' with type '{mde_platform['type']}'"
                    )
                else:
                    self.log_test(
                        "MDE Platform Integration", 
                        False, 
                        f"MDE platform invalid: {mde_platform}"
                    )
            else:
                self.log_test(
                    "MDE Platform Integration", 
                    False, 
                    "MDE (Music Data Exchange) platform not found"
                )
            
            # Check MLC platform
            mlc_platform = platforms.get('mlc')
            if mlc_platform:
                expected_mlc_fields = ['name', 'type', 'description', 'api_endpoint']
                mlc_valid = all(field in mlc_platform for field in expected_mlc_fields)
                
                if mlc_valid and mlc_platform.get('type') == 'music_licensing':
                    self.log_test(
                        "MLC Platform Integration", 
                        True, 
                        f"MLC: '{mlc_platform['name']}' with type '{mlc_platform['type']}'"
                    )
                else:
                    self.log_test(
                        "MLC Platform Integration", 
                        False, 
                        f"MLC platform invalid: {mlc_platform}"
                    )
            else:
                self.log_test(
                    "MLC Platform Integration", 
                    False, 
                    "MLC (Mechanical Licensing Collective) platform not found"
                )
            
            # Verify total platform count
            total_platforms = response_data.get('total_count', len(platforms))
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
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else response_data}"
            )

    def test_existing_gs1_functionality(self):
        """Test existing GS1 Asset Registry functionality"""
        print("\n🔍 Testing Existing GS1 Asset Registry Functionality...")
        
        # Test GS1 health endpoint
        status_code, response_data = self.make_request('/gs1/health')
        
        if status_code == 200 and isinstance(response_data, dict):
            if response_data.get('status') == 'healthy':
                self.log_test(
                    "GS1 Health Endpoint", 
                    True, 
                    f"Healthy - Assets: {response_data.get('total_assets', 0)}, Links: {response_data.get('total_digital_links', 0)}"
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
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else response_data}"
            )
        
        # Test GS1 analytics endpoint
        status_code, response_data = self.make_request('/gs1/analytics')
        
        if status_code == 200 and isinstance(response_data, dict):
            required_analytics_fields = ['total_assets', 'assets_by_type', 'identifiers_by_type']
            missing_fields = [field for field in required_analytics_fields if field not in response_data]
            
            if not missing_fields:
                self.log_test(
                    "GS1 Analytics Endpoint", 
                    True, 
                    f"Analytics working - Total assets: {response_data.get('total_assets')}"
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
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else response_data}"
            )

    def test_mde_integration_endpoints(self):
        """Test MDE integration endpoints"""
        print("\n🔍 Testing MDE Integration Endpoints...")
        
        # Test MDE integration status
        status_code, response_data = self.make_request('/mde/integration/status')
        
        if status_code == 200 and isinstance(response_data, dict):
            integration_status = response_data.get('integration_status', {})
            
            if integration_status.get('mde_connected'):
                capabilities = integration_status.get('capabilities', [])
                expected_capabilities = ['metadata_standardization', 'data_quality_validation', 'industry_data_exchange']
                
                has_required_capabilities = all(cap in capabilities for cap in expected_capabilities)
                
                if has_required_capabilities:
                    self.log_test(
                        "MDE Integration Status", 
                        True, 
                        f"MDE connected - Capabilities: {len(capabilities)}, Quality: {integration_status.get('data_quality_score')}"
                    )
                else:
                    missing_caps = [cap for cap in expected_capabilities if cap not in capabilities]
                    self.log_test(
                        "MDE Integration Status", 
                        False, 
                        f"Missing capabilities: {missing_caps}"
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
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else response_data}"
            )
        
        # Test MDE standards endpoint
        status_code, response_data = self.make_request('/mde/standards', params={'user_id': 'test_user'})
        
        if status_code == 200 and isinstance(response_data, dict):
            if response_data.get('success'):
                standards = response_data.get('standards', [])
                if len(standards) >= 5:
                    self.log_test(
                        "MDE Standards Endpoint", 
                        True, 
                        f"Standards: {len(standards)}, Recommended: {response_data.get('recommended_standard')}"
                    )
                else:
                    self.log_test(
                        "MDE Standards Endpoint", 
                        False, 
                        f"Insufficient standards: {len(standards)}"
                    )
            else:
                self.log_test(
                    "MDE Standards Endpoint", 
                    False, 
                    f"Response success=false: {response_data}"
                )
        else:
            self.log_test(
                "MDE Standards Endpoint", 
                False, 
                f"HTTP {status_code}: {response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else response_data}"
            )

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🎯 COMPREHENSIVE BACKEND TESTING FOR GS1 & MDE FIXES VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Run all test categories
        self.test_gs1_business_info_endpoint()
        self.test_gs1_products_endpoint()
        self.test_distribution_platforms_mde_mlc()
        self.test_existing_gs1_functionality()
        self.test_mde_integration_endpoints()
        
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

def main():
    """Main test execution"""
    try:
        tester = LocalBackendTester()
        success = tester.run_comprehensive_tests()
        
        if success:
            print(f"\n🎉 COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY!")
            print(f"✅ System is ready for production with verified fixes")
            return 0
        else:
            print(f"\n⚠️  COMPREHENSIVE TESTING COMPLETED WITH ISSUES")
            print(f"❌ Some critical functionality needs attention")
            return 1
            
    except Exception as e:
        print(f"\n💥 TESTING FAILED WITH EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())