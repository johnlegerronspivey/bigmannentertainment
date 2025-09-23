#!/usr/bin/env python3
"""
Business Identifiers Backend Testing for Big Mann Entertainment Platform
Testing ISRC Prefix (QZ9H8) and Publisher Number (PA04UV) functionality
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://support-desk-30.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BusinessIdentifiersTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.test_user_email = "business.test@bigmannentertainment.com"
        self.test_user_password = "BusinessTest2025!"
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def register_test_user(self):
        """Register a test user for authentication"""
        try:
            user_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": "Business Identifiers Test User",
                "business_name": "Test Business LLC",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 201:
                    print("✅ Test user registered successfully")
                    return True
                elif response.status == 400:
                    # User might already exist, try to login
                    print("ℹ️ Test user already exists, proceeding to login")
                    return True
                else:
                    print(f"❌ Failed to register test user: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error registering test user: {str(e)}")
            return False
            
    async def login_test_user(self):
        """Login test user and get authentication token"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Test user logged in successfully")
                    return True
                else:
                    print(f"❌ Failed to login test user: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error logging in test user: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authentication headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_business_identifiers_endpoint(self):
        """Test GET /api/business/identifiers endpoint"""
        print("\n🎯 Testing Business Identifiers Endpoint...")
        
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{API_BASE}/business/identifiers", headers=headers) as response:
                status = response.status
                
                if status == 200:
                    data = await response.json()
                    
                    # Check ISRC Prefix
                    isrc_prefix = data.get("isrc_prefix")
                    if isrc_prefix == "QZ9H8":
                        print("✅ ISRC Prefix correctly returns 'QZ9H8'")
                        self.test_results.append(("ISRC Prefix Check", True, "QZ9H8"))
                    else:
                        print(f"❌ ISRC Prefix incorrect: expected 'QZ9H8', got '{isrc_prefix}'")
                        self.test_results.append(("ISRC Prefix Check", False, f"Expected QZ9H8, got {isrc_prefix}"))
                    
                    # Check Publisher Number
                    publisher_number = data.get("publisher_number")
                    if publisher_number == "PA04UV":
                        print("✅ Publisher Number correctly returns 'PA04UV'")
                        self.test_results.append(("Publisher Number Check", True, "PA04UV"))
                    else:
                        print(f"❌ Publisher Number incorrect: expected 'PA04UV', got '{publisher_number}'")
                        self.test_results.append(("Publisher Number Check", False, f"Expected PA04UV, got {publisher_number}"))
                    
                    # Check all required fields are present
                    required_fields = [
                        "business_legal_name", "business_ein", "business_tin", 
                        "business_address", "business_phone", "business_naics_code",
                        "upc_company_prefix", "global_location_number", 
                        "isrc_prefix", "publisher_number"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    if not missing_fields:
                        print("✅ All required business identifier fields are present")
                        self.test_results.append(("Required Fields Check", True, "All fields present"))
                    else:
                        print(f"❌ Missing required fields: {missing_fields}")
                        self.test_results.append(("Required Fields Check", False, f"Missing: {missing_fields}"))
                    
                    # Check response structure for frontend consumption
                    if isinstance(data, dict) and len(data) >= 10:
                        print("✅ Response structure is correct for frontend consumption")
                        self.test_results.append(("Response Structure Check", True, "Valid JSON object"))
                    else:
                        print("❌ Response structure is not suitable for frontend")
                        self.test_results.append(("Response Structure Check", False, "Invalid structure"))
                        
                    print(f"📋 Full response data: {json.dumps(data, indent=2)}")
                    
                elif status == 401:
                    print("❌ Authentication required - endpoint properly protected")
                    self.test_results.append(("Authentication Protection", True, "401 Unauthorized"))
                elif status == 403:
                    print("❌ Access forbidden - check user permissions")
                    self.test_results.append(("Authentication Protection", False, "403 Forbidden"))
                else:
                    print(f"❌ Unexpected status code: {status}")
                    self.test_results.append(("Endpoint Accessibility", False, f"Status {status}"))
                    
        except Exception as e:
            print(f"❌ Error testing business identifiers endpoint: {str(e)}")
            self.test_results.append(("Business Identifiers Endpoint", False, str(e)))
            
    async def test_isrc_generation_functionality(self):
        """Test ISRC generation using QZ9H8 prefix"""
        print("\n🎯 Testing ISRC Generation Functionality...")
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            # Test ISRC generation with sample data
            isrc_data = {
                "artist_name": "Test Artist",
                "track_title": "Test Track for ISRC",
                "release_year": 2025
            }
            
            async with self.session.post(f"{API_BASE}/business/generate-isrc", 
                                       json=isrc_data, headers=headers) as response:
                status = response.status
                
                if status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        isrc_code = data.get("data", {}).get("isrc_code", "")
                        registrant_code = data.get("data", {}).get("registrant_code", "")
                        
                        # Check if ISRC uses QZ9H8 prefix
                        if "QZ9" in isrc_code and registrant_code == "QZ9H8":
                            print(f"✅ ISRC generation uses correct prefix QZ9H8: {isrc_code}")
                            self.test_results.append(("ISRC Generation Prefix", True, f"Generated: {isrc_code}"))
                        else:
                            print(f"❌ ISRC generation uses incorrect prefix: {isrc_code}")
                            self.test_results.append(("ISRC Generation Prefix", False, f"Generated: {isrc_code}"))
                        
                        # Check ISRC format (CC-XXX-YY-NNNNN)
                        if len(isrc_code.split("-")) == 4:
                            print("✅ ISRC format is correct (CC-XXX-YY-NNNNN)")
                            self.test_results.append(("ISRC Format Check", True, "Correct format"))
                        else:
                            print(f"❌ ISRC format is incorrect: {isrc_code}")
                            self.test_results.append(("ISRC Format Check", False, f"Format: {isrc_code}"))
                            
                        print(f"📋 Generated ISRC data: {json.dumps(data.get('data', {}), indent=2)}")
                        
                    else:
                        print("❌ ISRC generation failed")
                        self.test_results.append(("ISRC Generation", False, "Generation failed"))
                        
                elif status == 401:
                    print("❌ Authentication required for ISRC generation")
                    self.test_results.append(("ISRC Generation Auth", True, "401 Unauthorized"))
                elif status == 400:
                    print("❌ Bad request - check required fields")
                    error_text = await response.text()
                    self.test_results.append(("ISRC Generation", False, f"400 Bad Request: {error_text}"))
                else:
                    print(f"❌ Unexpected status code: {status}")
                    error_text = await response.text()
                    self.test_results.append(("ISRC Generation", False, f"Status {status}: {error_text}"))
                    
        except Exception as e:
            print(f"❌ Error testing ISRC generation: {str(e)}")
            self.test_results.append(("ISRC Generation", False, str(e)))
            
    async def test_authentication_requirements(self):
        """Test authentication requirements for business endpoints"""
        print("\n🎯 Testing Authentication Requirements...")
        
        try:
            # Test without authentication
            async with self.session.get(f"{API_BASE}/business/identifiers") as response:
                if response.status in [401, 403]:
                    print(f"✅ Business identifiers endpoint requires authentication ({response.status})")
                    self.test_results.append(("Auth Required - Identifiers", True, f"{response.status} Authentication Required"))
                else:
                    print(f"❌ Business identifiers endpoint should require auth, got {response.status}")
                    self.test_results.append(("Auth Required - Identifiers", False, f"Status {response.status}"))
            
            # Test ISRC generation without authentication
            isrc_data = {"artist_name": "Test", "track_title": "Test"}
            async with self.session.post(f"{API_BASE}/business/generate-isrc", json=isrc_data) as response:
                if response.status in [401, 403]:
                    print(f"✅ ISRC generation endpoint requires authentication ({response.status})")
                    self.test_results.append(("Auth Required - ISRC Gen", True, f"{response.status} Authentication Required"))
                else:
                    print(f"❌ ISRC generation endpoint should require auth, got {response.status}")
                    self.test_results.append(("Auth Required - ISRC Gen", False, f"Status {response.status}"))
                    
        except Exception as e:
            print(f"❌ Error testing authentication requirements: {str(e)}")
            self.test_results.append(("Authentication Requirements", False, str(e)))
            
    async def test_response_structure_for_frontend(self):
        """Test response structure compatibility with frontend BusinessIdentifiers component"""
        print("\n🎯 Testing Response Structure for Frontend Compatibility...")
        
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{API_BASE}/business/identifiers", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response is JSON serializable
                    try:
                        json.dumps(data)
                        print("✅ Response is JSON serializable")
                        self.test_results.append(("JSON Serializable", True, "Valid JSON"))
                    except Exception:
                        print("❌ Response is not JSON serializable")
                        self.test_results.append(("JSON Serializable", False, "Invalid JSON"))
                    
                    # Check for frontend-expected fields
                    frontend_expected_fields = {
                        "isrc_prefix": "QZ9H8",
                        "publisher_number": "PA04UV",
                        "business_legal_name": str,
                        "business_ein": str,
                        "upc_company_prefix": str,
                        "global_location_number": str
                    }
                    
                    frontend_compatibility = True
                    for field, expected_type in frontend_expected_fields.items():
                        if field in data:
                            if expected_type == str:
                                if isinstance(data[field], str) and data[field]:
                                    print(f"✅ {field}: {data[field]} (valid string)")
                                else:
                                    print(f"❌ {field}: invalid or empty string")
                                    frontend_compatibility = False
                            else:
                                if data[field] == expected_type:
                                    print(f"✅ {field}: {data[field]} (correct value)")
                                else:
                                    print(f"❌ {field}: expected {expected_type}, got {data[field]}")
                                    frontend_compatibility = False
                        else:
                            print(f"❌ Missing field: {field}")
                            frontend_compatibility = False
                    
                    if frontend_compatibility:
                        print("✅ Response structure is fully compatible with frontend")
                        self.test_results.append(("Frontend Compatibility", True, "All fields valid"))
                    else:
                        print("❌ Response structure has compatibility issues")
                        self.test_results.append(("Frontend Compatibility", False, "Field validation failed"))
                        
                else:
                    print(f"❌ Could not test frontend compatibility, status: {response.status}")
                    self.test_results.append(("Frontend Compatibility", False, f"Status {response.status}"))
                    
        except Exception as e:
            print(f"❌ Error testing frontend compatibility: {str(e)}")
            self.test_results.append(("Frontend Compatibility", False, str(e)))
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 BUSINESS IDENTIFIERS TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "📈 Success Rate: 0%")
        
        print("\n📋 DETAILED RESULTS:")
        for test_name, passed, details in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}: {details}")
        
        print("\n🎯 KEY VERIFICATION POINTS:")
        
        # Check specific requirements from review request
        isrc_prefix_test = next((result for result in self.test_results if "ISRC Prefix" in result[0]), None)
        publisher_test = next((result for result in self.test_results if "Publisher Number" in result[0]), None)
        auth_test = next((result for result in self.test_results if "Auth Required" in result[0]), None)
        frontend_test = next((result for result in self.test_results if "Frontend Compatibility" in result[0]), None)
        
        if isrc_prefix_test and isrc_prefix_test[1]:
            print("✅ ISRC Prefix (QZ9H8) verification: PASSED")
        else:
            print("❌ ISRC Prefix (QZ9H8) verification: FAILED")
            
        if publisher_test and publisher_test[1]:
            print("✅ Publisher Number (PA04UV) verification: PASSED")
        else:
            print("❌ Publisher Number (PA04UV) verification: FAILED")
            
        if auth_test and auth_test[1]:
            print("✅ Authentication requirements: PASSED")
        else:
            print("❌ Authentication requirements: FAILED")
            
        if frontend_test and frontend_test[1]:
            print("✅ Frontend compatibility: PASSED")
        else:
            print("❌ Frontend compatibility: FAILED")
        
        print("\n" + "="*80)
        
        return passed_tests, failed_tests, total_tests

async def main():
    """Main test execution function"""
    print("🚀 Starting Business Identifiers Backend Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    tester = BusinessIdentifiersTest()
    
    try:
        # Setup
        await tester.setup_session()
        
        # Authentication setup
        await tester.register_test_user()
        login_success = await tester.login_test_user()
        
        if not login_success:
            print("❌ Failed to authenticate test user, some tests may fail")
        
        # Run all tests
        await tester.test_authentication_requirements()
        await tester.test_business_identifiers_endpoint()
        await tester.test_isrc_generation_functionality()
        await tester.test_response_structure_for_frontend()
        
        # Print summary
        passed, failed, total = tester.print_test_summary()
        
        # Cleanup
        await tester.cleanup_session()
        
        # Exit with appropriate code
        if failed > 0:
            print(f"\n❌ Testing completed with {failed} failures")
            sys.exit(1)
        else:
            print(f"\n✅ All {total} tests passed successfully!")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Critical error during testing: {str(e)}")
        await tester.cleanup_session()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())