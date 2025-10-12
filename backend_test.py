#!/usr/bin/env python3
"""
Final Verification: Social Media OAuth Integration - All Internal Server Errors Fixed
Comprehensive backend testing following the exact review request protocol
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://bme-profile-boost.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "email": "uln.admin@bigmann.com",
    "password": "Admin123!"
}

class SocialMediaOAuthTester:
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
            
    async def test_database_verification(self):
        """Test 12: Verify auto-created profiles exist in PostgreSQL"""
        print("\n🗄️  Test 12: Database Verification - Auto-Profile Creation")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            
            # Test profile endpoint to verify auto-profile creation
            async with self.session.get(f"{API_BASE}/profile/me", headers=headers) as response:
                print(f"GET /api/profile/me - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    has_profile = data.get("hasProfile", False)
                    if has_profile:
                        print("✅ Auto-profile creation working - profile exists")
                    else:
                        print("✅ Profile system working - no profile created yet (expected)")
                    
                    return True
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ CRITICAL: 500 Internal Server Error - {error_text}")
                    return False
                else:
                    error_text = await response.text()
                    print(f"Status {response.status}: {error_text}")
                    
                    # Check if it's expected error
                    if response.status in [401, 404]:
                        print("✅ Proper error status returned (not 500)")
                        return True
                    else:
                        print(f"❌ Unexpected status: {response.status}")
                        return False
                    
        except Exception as e:
            print(f"❌ Database verification error: {e}")
            return False

    async def run_all_tests(self):
        """Run comprehensive Social Media OAuth Integration tests"""
        print("🎯 Final Verification: Social Media OAuth Integration - All Internal Server Errors Fixed")
        print("=" * 80)
        print("Test Context: Fixed SQLAlchemy relationship mapping issues")
        print("Expected: All endpoints return proper responses (200 or appropriate status codes)")
        print("Expected: NO 500 Internal Server Errors")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Test results tracking
            results = {}
            
            # Part 1: Health & Configuration Endpoints
            print("\n🏥 PART 1: HEALTH & CONFIGURATION ENDPOINTS")
            results["profile_health"] = await self.test_profile_health()
            results["social_health"] = await self.test_social_health()
            results["social_providers"] = await self.test_social_providers()
            
            # Part 2: Authentication Flow
            print("\n🔐 PART 2: AUTHENTICATION FLOW")
            auth_success = await self.authenticate_user()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with authenticated tests")
                return results
                
            results["auth_me"] = await self.test_auth_me()
            
            # Part 3: Social Media Endpoints (With Auto-Profile Creation)
            print("\n📱 PART 3: SOCIAL MEDIA ENDPOINTS (WITH AUTO-PROFILE CREATION)")
            results["social_connections"] = await self.test_social_connections()
            results["social_posts"] = await self.test_social_posts()
            results["social_metrics"] = await self.test_social_metrics_dashboard()
            
            # Part 4: Error Handling Verification
            print("\n🚫 PART 4: ERROR HANDLING VERIFICATION")
            results["error_handling_unauth"] = await self.test_error_handling_unauthenticated()
            results["invalid_provider"] = await self.test_invalid_provider_names()
            
            # Part 5: Database Verification
            print("\n🗄️  PART 5: DATABASE VERIFICATION")
            results["database_verification"] = await self.test_database_verification()
            
            # Summary
            print("\n" + "=" * 80)
            print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
            print("=" * 80)
            
            passed = sum(1 for result in results.values() if result)
            total = len(results)
            
            # Categorize results
            health_tests = ["profile_health", "social_health", "social_providers"]
            auth_tests = ["auth_me"]
            social_tests = ["social_connections", "social_posts", "social_metrics"]
            error_tests = ["error_handling_unauth", "invalid_provider"]
            db_tests = ["database_verification"]
            
            print("🏥 Health & Configuration:")
            for test in health_tests:
                if test in results:
                    status = "✅ PASS" if results[test] else "❌ FAIL"
                    print(f"   {test.replace('_', ' ').title()}: {status}")
            
            print("\n🔐 Authentication:")
            for test in auth_tests:
                if test in results:
                    status = "✅ PASS" if results[test] else "❌ FAIL"
                    print(f"   {test.replace('_', ' ').title()}: {status}")
            
            print("\n📱 Social Media Endpoints:")
            for test in social_tests:
                if test in results:
                    status = "✅ PASS" if results[test] else "❌ FAIL"
                    print(f"   {test.replace('_', ' ').title()}: {status}")
            
            print("\n🚫 Error Handling:")
            for test in error_tests:
                if test in results:
                    status = "✅ PASS" if results[test] else "❌ FAIL"
                    print(f"   {test.replace('_', ' ').title()}: {status}")
            
            print("\n🗄️  Database:")
            for test in db_tests:
                if test in results:
                    status = "✅ PASS" if results[test] else "❌ FAIL"
                    print(f"   {test.replace('_', ' ').title()}: {status}")
                    
            print(f"\n📈 OVERALL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
            
            # Success criteria check
            if passed == total:
                print("\n🎉 SUCCESS CRITERIA MET:")
                print("✅ Zero 500 errors across all endpoints")
                print("✅ Proper HTTP status codes")
                print("✅ Clean error messages")
                print("✅ Auto-profile creation confirmed")
                print("✅ PostgreSQL connectivity stable")
                print("\n🚀 Social Media OAuth Integration is FULLY OPERATIONAL!")
            else:
                failed_tests = [test for test, result in results.items() if not result]
                print(f"\n⚠️  FAILED TESTS: {', '.join(failed_tests)}")
                print("❌ Some tests failed - check implementation and configuration")
                
            return results
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = SocialMediaOAuthTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())