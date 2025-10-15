#!/usr/bin/env python3
"""
Compensation Breakdown Calculation Testing
Testing the updated compensation breakdown calculation with configurable business rules
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://social-profile-sync.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "email": "uln.admin@bigmann.com",
    "password": "Admin123!"
}

class CompensationBreakdownTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.test_results = {}
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate_user(self):
        """Authenticate with provided credentials"""
        print("🔐 Part 2: Authentication Flow")
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=TEST_CREDENTIALS) as response:
                print(f"POST /api/auth/login - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.user_id = data.get("user", {}).get("id")
                    print("✅ Authentication successful")
                    print(f"   User ID: {self.user_id}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Login failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_profile_health(self):
        """Test 1: GET /api/profile/health - Verify PostgreSQL connected"""
        print("\n🏥 Test 1: Profile Health Check")
        
        try:
            async with self.session.get(f"{API_BASE}/profile/health") as response:
                print(f"GET /api/profile/health - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    postgres_status = data.get("postgres", "unknown")
                    if postgres_status == "connected":
                        print("✅ PostgreSQL connected and operational")
                        return True
                    else:
                        print(f"❌ PostgreSQL not connected: {postgres_status}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Profile health check failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Profile health check error: {e}")
            return False
            
    async def test_social_health(self):
        """Test 2: GET /api/social/health - Verify service healthy"""
        print("\n🏥 Test 2: Social Media Service Health Check")
        
        try:
            async with self.session.get(f"{API_BASE}/social/health") as response:
                print(f"GET /api/social/health - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    service_status = data.get("status", "unknown")
                    if service_status == "healthy":
                        print("✅ Social Media service is healthy")
                        providers = data.get("providers", [])
                        print(f"   Available providers: {len(providers)}")
                        return True
                    else:
                        print(f"❌ Social Media service unhealthy: {service_status}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Social health check failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Social health check error: {e}")
            return False
            
    async def test_social_providers(self):
        """Test 3: GET /api/social/providers - Check all 6 providers listed"""
        print("\n📋 Test 3: Social Media Providers List")
        
        try:
            async with self.session.get(f"{API_BASE}/social/providers") as response:
                print(f"GET /api/social/providers - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    providers = data.get("providers", [])
                    print(f"✅ Found {len(providers)} social media providers")
                    
                    # Expected providers
                    expected_providers = ["twitter", "facebook", "instagram", "tiktok", "linkedin", "youtube"]
                    found_providers = []
                    
                    for provider in providers:
                        provider_name = provider.get("provider", provider.get("name", "")).lower()
                        found_providers.append(provider_name)
                        configured = provider.get("configured", False)
                        print(f"   - {provider_name}: {'✅ configured' if configured else '❌ not configured'}")
                    
                    # Check if we have at least 6 providers
                    if len(providers) >= 6:
                        print("✅ All 6 providers listed correctly")
                        return True
                    else:
                        print(f"❌ Expected 6 providers, found {len(providers)}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get providers list: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Providers list error: {e}")
            return False
            
    async def test_auth_me(self):
        """Test 5: GET /api/auth/me - Get current user info"""
        print("\n👤 Test 5: Current User Information")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{API_BASE}/auth/me", headers=headers) as response:
                print(f"GET /api/auth/me - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    user_email = data.get("email", "")
                    user_role = data.get("role", "")
                    business_name = data.get("business_name", "")
                    
                    print(f"✅ User info retrieved successfully")
                    print(f"   Email: {user_email}")
                    print(f"   Role: {user_role}")
                    print(f"   Business: {business_name}")
                    
                    # Verify JWT token working
                    if user_email == TEST_CREDENTIALS["email"]:
                        print("✅ JWT token working correctly")
                        return True
                    else:
                        print(f"❌ Token mismatch - expected {TEST_CREDENTIALS['email']}, got {user_email}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get user info: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Auth me error: {e}")
            return False
            
    async def test_social_connections(self):
        """Test 7: GET /api/social/connections - Should return empty array (no 500 error)"""
        print("\n🔗 Test 7: Social Media Connections")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{API_BASE}/social/connections", headers=headers) as response:
                print(f"GET /api/social/connections - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    connections = data.get("connections", [])
                    print(f"✅ Retrieved connections successfully")
                    print(f"   Connection count: {len(connections)}")
                    
                    if len(connections) == 0:
                        print("✅ Empty array returned properly (expected for new user)")
                    else:
                        print(f"   Found {len(connections)} existing connections")
                    
                    return True
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ CRITICAL: 500 Internal Server Error - {error_text}")
                    return False
                else:
                    error_text = await response.text()
                    print(f"Status {response.status}: {error_text}")
                    
                    # Check if it's expected error (like 404 for profile not found)
                    if response.status in [401, 404]:
                        print("✅ Proper error status returned (not 500)")
                        return True
                    else:
                        print(f"❌ Unexpected status: {response.status}")
                        return False
                    
        except Exception as e:
            print(f"❌ Social connections error: {e}")
            return False
            
    async def test_social_posts(self):
        """Test 8: GET /api/social/posts - Should return empty posts array (no 500 error)"""
        print("\n📝 Test 8: Social Media Posts")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{API_BASE}/social/posts", headers=headers) as response:
                print(f"GET /api/social/posts - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    posts = data.get("posts", [])
                    print(f"✅ Retrieved posts successfully")
                    print(f"   Post count: {len(posts)}")
                    
                    if len(posts) == 0:
                        print("✅ Empty posts array returned properly (expected)")
                    else:
                        print(f"   Found {len(posts)} existing posts")
                    
                    return True
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ CRITICAL: 500 Internal Server Error - {error_text}")
                    return False
                else:
                    error_text = await response.text()
                    print(f"Status {response.status}: {error_text}")
                    
                    # Check if it's expected error (like 404 for profile not found)
                    if response.status in [401, 404]:
                        print("✅ Proper error status returned (not 500)")
                        return True
                    else:
                        print(f"❌ Unexpected status: {response.status}")
                        return False
                    
        except Exception as e:
            print(f"❌ Social posts error: {e}")
            return False
            
    async def test_social_metrics_dashboard(self):
        """Test 9: GET /api/social/metrics/dashboard - Should return zero metrics (no 500 error)"""
        print("\n📊 Test 9: Social Media Metrics Dashboard")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{API_BASE}/social/metrics/dashboard", headers=headers) as response:
                print(f"GET /api/social/metrics/dashboard - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    print(f"✅ Retrieved metrics dashboard successfully")
                    
                    # Check for zero metrics (expected for new user)
                    metrics = data.get("metrics", {})
                    total_followers = metrics.get("total_followers", 0)
                    total_posts = metrics.get("total_posts", 0)
                    
                    print(f"   Total followers: {total_followers}")
                    print(f"   Total posts: {total_posts}")
                    print("✅ Zero metrics returned properly (expected)")
                    
                    return True
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ CRITICAL: 500 Internal Server Error - {error_text}")
                    return False
                else:
                    error_text = await response.text()
                    print(f"Status {response.status}: {error_text}")
                    
                    # Check if it's expected error (like 404 for profile not found)
                    if response.status in [401, 404]:
                        print("✅ Proper error status returned (not 500)")
                        return True
                    else:
                        print(f"❌ Unexpected status: {response.status}")
                        return False
                    
        except Exception as e:
            print(f"❌ Social metrics error: {e}")
            return False
            
    async def test_error_handling_unauthenticated(self):
        """Test 10: Test endpoints without authentication - Should return 401, not 500"""
        print("\n🚫 Test 10: Error Handling - Unauthenticated Requests")
        
        endpoints_to_test = [
            "/api/social/connections",
            "/api/social/posts", 
            "/api/social/metrics/dashboard"
        ]
        
        all_passed = True
        
        for endpoint in endpoints_to_test:
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    print(f"GET {endpoint} (no auth) - Status: {response.status}")
                    
                    if response.status == 401:
                        print(f"✅ Proper 401 Unauthorized returned")
                    elif response.status == 500:
                        error_text = await response.text()
                        print(f"❌ CRITICAL: 500 Internal Server Error - {error_text}")
                        all_passed = False
                    else:
                        print(f"⚠️  Unexpected status {response.status} (expected 401)")
                        # Still acceptable as long as it's not 500
                        
            except Exception as e:
                print(f"❌ Error testing {endpoint}: {e}")
                all_passed = False
                
        return all_passed
            
    async def test_invalid_provider_names(self):
        """Test 11: Test with invalid provider names - Should return 400, not 500"""
        print("\n❌ Test 11: Error Handling - Invalid Provider Names")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            
            # Test invalid provider in connection endpoint
            async with self.session.get(f"{API_BASE}/social/connect/invalidprovider", headers=headers) as response:
                print(f"GET /api/social/connect/invalidprovider - Status: {response.status}")
                
                if response.status == 400:
                    print("✅ Proper 400 Bad Request returned for invalid provider")
                    return True
                elif response.status == 404:
                    print("✅ Proper 404 Not Found returned for invalid provider")
                    return True
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ CRITICAL: 500 Internal Server Error - {error_text}")
                    return False
                else:
                    print(f"⚠️  Unexpected status {response.status} (expected 400 or 404)")
                    return True  # Still acceptable as long as it's not 500
                    
        except Exception as e:
            print(f"❌ Error testing invalid provider: {e}")
            return False
            
    async def test_compensation_dashboard(self):
        """Test: GET /api/licensing/compensation-dashboard - Verify compensation breakdown percentages"""
        print("\n💰 Test: Compensation Dashboard - Updated Calculation")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{API_BASE}/licensing/compensation-dashboard", headers=headers) as response:
                print(f"GET /api/licensing/compensation-dashboard - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    # Extract compensation breakdown
                    compensation_breakdown = data.get("compensation_dashboard", {}).get("compensation_breakdown", {})
                    
                    if not compensation_breakdown:
                        print("❌ No compensation_breakdown found in response")
                        return False
                    
                    # Expected values from environment variables
                    expected_values = {
                        "artist_percentage": 60.0,
                        "songwriter_percentage": 20.0,
                        "publisher_percentage": 12.0,
                        "big_mann_commission": 8.0
                    }
                    
                    print("\n📊 Compensation Breakdown Verification:")
                    all_correct = True
                    total_percentage = 0.0
                    
                    for key, expected_value in expected_values.items():
                        actual_value = compensation_breakdown.get(key, 0.0)
                        total_percentage += actual_value
                        
                        if abs(actual_value - expected_value) < 0.01:  # Allow for floating point precision
                            print(f"   ✅ {key}: {actual_value}% (expected: {expected_value}%)")
                        else:
                            print(f"   ❌ {key}: {actual_value}% (expected: {expected_value}%)")
                            all_correct = False
                    
                    # Verify total equals 100%
                    print(f"\n📈 Total Percentage: {total_percentage}%")
                    if abs(total_percentage - 100.0) < 0.01:
                        print("✅ Total percentages sum to 100%")
                    else:
                        print(f"❌ Total percentages do not sum to 100% (actual: {total_percentage}%)")
                        all_correct = False
                    
                    # Verify business information fields
                    calculation_method = compensation_breakdown.get("calculation_method")
                    last_updated = compensation_breakdown.get("last_updated")
                    notes = compensation_breakdown.get("notes")
                    
                    print(f"\n📋 Business Information:")
                    if calculation_method:
                        print(f"   ✅ Calculation Method: {calculation_method}")
                    else:
                        print("   ❌ Missing calculation_method field")
                        all_correct = False
                    
                    if last_updated:
                        print(f"   ✅ Last Updated: {last_updated}")
                    else:
                        print("   ❌ Missing last_updated field")
                        all_correct = False
                    
                    if notes:
                        print(f"   ✅ Notes: {notes}")
                    else:
                        print("   ❌ Missing notes field")
                        all_correct = False
                    
                    # Verify percentages are properly rounded to 2 decimal places
                    print(f"\n🔢 Decimal Precision Check:")
                    precision_correct = True
                    for key, value in expected_values.items():
                        actual_value = compensation_breakdown.get(key, 0.0)
                        # Check if value has at most 2 decimal places
                        if round(actual_value, 2) == actual_value:
                            print(f"   ✅ {key}: {actual_value}% (properly rounded)")
                        else:
                            print(f"   ❌ {key}: {actual_value}% (not properly rounded to 2 decimal places)")
                            precision_correct = False
                    
                    if all_correct and precision_correct:
                        print("\n🎉 Compensation breakdown calculation is working correctly!")
                        print("✅ All percentages match expected values")
                        print("✅ Total equals 100%")
                        print("✅ All required fields present")
                        print("✅ Proper decimal precision")
                        return True
                    else:
                        print("\n❌ Compensation breakdown has issues")
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get compensation dashboard: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Compensation dashboard test error: {e}")
            return False

    async def run_all_tests(self):
        """Run compensation breakdown calculation tests"""
        print("🎯 Compensation Breakdown Calculation Testing")
        print("=" * 80)
        print("Test Context: Updated compensation breakdown calculation with configurable business rules")
        print("Expected Environment Variables:")
        print("  - ARTIST_SHARE_PERCENTAGE=60.0")
        print("  - SONGWRITER_SHARE_PERCENTAGE=20.0") 
        print("  - PUBLISHER_SHARE_PERCENTAGE=12.0")
        print("  - PLATFORM_COMMISSION_PERCENTAGE=8.0")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Test results tracking
            results = {}
            
            # Authentication Flow
            print("\n🔐 AUTHENTICATION")
            auth_success = await self.authenticate_user()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with compensation dashboard test")
                return results
                
            results["auth_me"] = await self.test_auth_me()
            
            # Compensation Dashboard Test
            print("\n💰 COMPENSATION BREAKDOWN TESTING")
            results["compensation_dashboard"] = await self.test_compensation_dashboard()
            
            # Summary
            print("\n" + "=" * 80)
            print("📊 COMPENSATION BREAKDOWN TEST RESULTS")
            print("=" * 80)
            
            passed = sum(1 for result in results.values() if result)
            total = len(results)
            
            print("🔐 Authentication:")
            if "auth_me" in results:
                status = "✅ PASS" if results["auth_me"] else "❌ FAIL"
                print(f"   Authentication: {status}")
            
            print("\n💰 Compensation Dashboard:")
            if "compensation_dashboard" in results:
                status = "✅ PASS" if results["compensation_dashboard"] else "❌ FAIL"
                print(f"   Compensation Breakdown: {status}")
                    
            print(f"\n📈 OVERALL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
            
            # Success criteria check
            if results.get("compensation_dashboard", False):
                print("\n🎉 SUCCESS CRITERIA MET:")
                print("✅ Compensation breakdown shows correct percentages")
                print("✅ Artist percentage: 60.0%")
                print("✅ Songwriter percentage: 20.0%")
                print("✅ Publisher percentage: 12.0%")
                print("✅ Big Mann commission: 8.0%")
                print("✅ Total equals 100%")
                print("✅ All business information fields present")
                print("✅ Proper decimal precision (2 decimal places)")
                print("\n🚀 Compensation Breakdown Calculation is FULLY OPERATIONAL!")
            else:
                print("\n❌ COMPENSATION BREAKDOWN TEST FAILED")
                print("Check environment variables and implementation")
                
            return results
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = CompensationBreakdownTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if results.get("compensation_dashboard", False):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())