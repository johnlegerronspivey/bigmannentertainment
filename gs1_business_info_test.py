#!/usr/bin/env python3
"""
🎯 GS1 BUSINESS INFORMATION FIX VERIFICATION TEST

Testing the specific GS1 business information endpoint fix as requested in the review.
This test verifies that the GS1 business information missing issue has been completely resolved.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://content-workflow-1.preview.emergentagent.com"

class GS1BusinessInfoTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Any = None):
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
    
    async def test_gs1_business_info_endpoint(self):
        """Test the main GS1 business info endpoint"""
        print("\n🏢 Testing GS1 Business Info Endpoint...")
        
        url = f"{self.backend_url}/api/gs1/business-info"
        
        try:
            async with self.session.get(url) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    self.log_test("GS1 Business Info Endpoint", "PASS", 
                                f"Status: {status_code}", response_data)
                    return response_data
                else:
                    self.log_test("GS1 Business Info Endpoint", "FAIL", 
                                f"Expected 200, got {status_code}", response_data)
                    return None
                    
        except Exception as e:
            self.log_test("GS1 Business Info Endpoint", "FAIL", 
                        f"Exception: {str(e)}")
            return None

    async def verify_response_structure(self, response_data: Dict):
        """Verify the response structure matches expected format"""
        print("\n📋 Verifying Response Structure...")
        
        if not response_data:
            self.log_test("Response Structure", "FAIL", "No response data to verify")
            return
        
        # Check success flag
        if response_data.get("success") is True:
            self.log_test("Success Flag", "PASS", "Response includes success: true")
        else:
            self.log_test("Success Flag", "FAIL", f"Success flag: {response_data.get('success')}")
        
        # Check business_info object
        business_info = response_data.get("business_info", {})
        if business_info:
            self.log_test("Business Info Object", "PASS", "business_info object present")
        else:
            self.log_test("Business Info Object", "FAIL", "business_info object missing")
            return
        
        # Check capabilities object
        capabilities = response_data.get("capabilities", {})
        if capabilities:
            self.log_test("Capabilities Object", "PASS", "capabilities object present")
        else:
            self.log_test("Capabilities Object", "FAIL", "capabilities object missing")

    async def verify_traditional_business_fields(self, response_data: Dict):
        """Verify traditional business fields are present"""
        print("\n🏢 Verifying Traditional Business Fields...")
        
        if not response_data:
            return
        
        expected_fields = {
            "business_entity": "Big Mann Entertainment LLC",
            "business_owner": "Big Mann Entertainment Group",
            "industry": "Music & Entertainment",
            "business_type": "Limited Liability Company"
        }
        
        for field, expected_value in expected_fields.items():
            actual_value = response_data.get(field)
            if actual_value == expected_value:
                self.log_test(f"Traditional Field: {field}", "PASS", 
                            f"Value: {actual_value}")
            else:
                self.log_test(f"Traditional Field: {field}", "FAIL", 
                            f"Expected: {expected_value}, Got: {actual_value}")
        
        # Check EIN and TIN (may be masked)
        ein = response_data.get("ein")
        tin = response_data.get("tin")
        
        if ein:
            self.log_test("EIN Field", "PASS", f"EIN present: {ein}")
        else:
            self.log_test("EIN Field", "FAIL", "EIN field missing")
            
        if tin:
            self.log_test("TIN Field", "PASS", f"TIN present: {tin}")
        else:
            self.log_test("TIN Field", "FAIL", "TIN field missing")

    async def verify_gs1_registry_fields(self, response_data: Dict):
        """Verify GS1 registry specific fields"""
        print("\n🏷️ Verifying GS1 Registry Fields...")
        
        if not response_data:
            return
        
        business_info = response_data.get("business_info", {})
        
        expected_gs1_fields = {
            "company_name": "Big Mann Entertainment",
            "compliance_status": "Fully Compliant",
            "certification_level": "GS1 Certified"
        }
        
        for field, expected_value in expected_gs1_fields.items():
            actual_value = business_info.get(field)
            if actual_value == expected_value:
                self.log_test(f"GS1 Field: {field}", "PASS", 
                            f"Value: {actual_value}")
            else:
                self.log_test(f"GS1 Field: {field}", "FAIL", 
                            f"Expected: {expected_value}, Got: {actual_value}")
        
        # Check company_prefix
        company_prefix = business_info.get("company_prefix")
        if company_prefix:
            self.log_test("Company Prefix", "PASS", f"Company prefix: {company_prefix}")
        else:
            self.log_test("Company Prefix", "FAIL", "Company prefix missing")
        
        # Check total_assets (should be a number)
        total_assets = business_info.get("total_assets")
        if isinstance(total_assets, (int, float)):
            self.log_test("Total Assets", "PASS", f"Total assets: {total_assets}")
        else:
            self.log_test("Total Assets", "FAIL", f"Total assets not a number: {total_assets}")

    async def verify_capabilities_fields(self, response_data: Dict):
        """Verify capabilities fields are present and correct"""
        print("\n⚙️ Verifying Capabilities Fields...")
        
        if not response_data:
            return
        
        capabilities = response_data.get("capabilities", {})
        
        # Check identifier_generation array
        identifier_generation = capabilities.get("identifier_generation", [])
        expected_identifiers = ["GTIN", "GLN", "GDTI", "ISRC", "ISAN"]
        
        if isinstance(identifier_generation, list) and len(identifier_generation) >= 5:
            missing_identifiers = [id for id in expected_identifiers if id not in identifier_generation]
            if not missing_identifiers:
                self.log_test("Identifier Generation", "PASS", 
                            f"All expected identifiers present: {identifier_generation}")
            else:
                self.log_test("Identifier Generation", "FAIL", 
                            f"Missing identifiers: {missing_identifiers}")
        else:
            self.log_test("Identifier Generation", "FAIL", 
                        f"Invalid identifier generation array: {identifier_generation}")
        
        # Check boolean capabilities
        boolean_capabilities = {
            "digital_links": True,
            "qr_codes": True,
            "analytics": True
        }
        
        for capability, expected_value in boolean_capabilities.items():
            actual_value = capabilities.get(capability)
            if actual_value == expected_value:
                self.log_test(f"Capability: {capability}", "PASS", 
                            f"Value: {actual_value}")
            else:
                self.log_test(f"Capability: {capability}", "FAIL", 
                            f"Expected: {expected_value}, Got: {actual_value}")

    async def verify_no_missing_fields(self, response_data: Dict):
        """Verify no critical fields are missing or null"""
        print("\n🔍 Verifying No Missing Critical Fields...")
        
        if not response_data:
            return
        
        # Critical fields that should not be null or missing
        critical_fields = [
            "success",
            "business_info",
            "capabilities",
            "business_entity",
            "business_owner",
            "industry",
            "business_type"
        ]
        
        missing_fields = []
        null_fields = []
        
        for field in critical_fields:
            if field not in response_data:
                missing_fields.append(field)
            elif response_data[field] is None:
                null_fields.append(field)
        
        if not missing_fields and not null_fields:
            self.log_test("Critical Fields Check", "PASS", 
                        "All critical fields present and non-null")
        else:
            issues = []
            if missing_fields:
                issues.append(f"Missing: {missing_fields}")
            if null_fields:
                issues.append(f"Null: {null_fields}")
            self.log_test("Critical Fields Check", "FAIL", 
                        f"Issues found: {', '.join(issues)}")

    async def verify_frontend_compatibility(self, response_data: Dict):
        """Verify response structure is compatible with frontend expectations"""
        print("\n🖥️ Verifying Frontend Compatibility...")
        
        if not response_data:
            return
        
        # Check that response can be easily consumed by frontend
        try:
            # Simulate frontend access patterns
            business_entity = response_data.get("business_entity")
            compliance_status = response_data.get("business_info", {}).get("compliance_status")
            capabilities = response_data.get("capabilities", {}).get("identifier_generation", [])
            
            if business_entity and compliance_status and capabilities:
                self.log_test("Frontend Compatibility", "PASS", 
                            "Response structure compatible with frontend access patterns")
            else:
                self.log_test("Frontend Compatibility", "FAIL", 
                            "Response structure may not be compatible with frontend")
                
        except Exception as e:
            self.log_test("Frontend Compatibility", "FAIL", 
                        f"Error accessing response data: {str(e)}")

    async def run_comprehensive_test(self):
        """Run comprehensive GS1 business info test"""
        print("🎯 GS1 BUSINESS INFORMATION FIX VERIFICATION TEST")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        try:
            # Test the main endpoint
            response_data = await self.test_gs1_business_info_endpoint()
            
            if response_data:
                # Verify response structure
                await self.verify_response_structure(response_data)
                
                # Verify traditional business fields
                await self.verify_traditional_business_fields(response_data)
                
                # Verify GS1 registry fields
                await self.verify_gs1_registry_fields(response_data)
                
                # Verify capabilities fields
                await self.verify_capabilities_fields(response_data)
                
                # Verify no missing fields
                await self.verify_no_missing_fields(response_data)
                
                # Verify frontend compatibility
                await self.verify_frontend_compatibility(response_data)
            
        except Exception as e:
            print(f"❌ Critical error during testing: {e}")
            self.log_test("Critical Error", "FAIL", str(e))
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 GS1 BUSINESS INFORMATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 VERIFICATION RESULTS:")
        
        # Categorize tests
        categories = {
            "Endpoint Access": ["GS1 Business Info Endpoint"],
            "Response Structure": ["Success Flag", "Business Info Object", "Capabilities Object"],
            "Traditional Business Fields": ["Traditional Field: business_entity", "Traditional Field: business_owner", 
                                          "Traditional Field: industry", "Traditional Field: business_type", 
                                          "EIN Field", "TIN Field"],
            "GS1 Registry Fields": ["GS1 Field: company_name", "GS1 Field: compliance_status", 
                                  "GS1 Field: certification_level", "Company Prefix", "Total Assets"],
            "Capabilities": ["Identifier Generation", "Capability: digital_links", "Capability: qr_codes", 
                           "Capability: analytics"],
            "Data Integrity": ["Critical Fields Check", "Frontend Compatibility"]
        }
        
        for category, test_names in categories.items():
            category_tests = [t for t in self.test_results if t["test"] in test_names]
            if category_tests:
                category_passed = len([t for t in category_tests if t["status"] == "PASS"])
                category_total = len(category_tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                status_emoji = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 50 else "❌"
                print(f"   {status_emoji} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        print(f"\n🔍 CRITICAL ISSUES:")
        critical_failures = [t for t in self.test_results if t["status"] == "FAIL"]
        
        if critical_failures:
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        else:
            print("   ✅ No critical issues found!")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"   {status_emoji} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"      └─ {result['details']}")
        
        print(f"\n🎉 GS1 BUSINESS INFORMATION TESTING COMPLETED")
        print(f"   Test End Time: {datetime.now().isoformat()}")
        
        if success_rate >= 90:
            print("   🏆 EXCELLENT: GS1 business information is complete and working perfectly!")
        elif success_rate >= 75:
            print("   ✅ GOOD: GS1 business information is mostly complete with minor issues")
        elif success_rate >= 50:
            print("   ⚠️ NEEDS WORK: GS1 business information has significant issues")
        else:
            print("   ❌ CRITICAL: GS1 business information requires major fixes")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    async with GS1BusinessInfoTester() as tester:
        await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())