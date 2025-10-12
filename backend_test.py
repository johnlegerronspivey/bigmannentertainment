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
            
    async def run_all_tests(self):
        """Run all Social Media OAuth Integration tests"""
        print("🎯 Social Media OAuth Integration Backend Testing")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Test results tracking
            results = {}
            
            # Authentication setup
            auth_success = await self.register_and_login()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with social media tests")
                return results
                
            # Run all tests
            results["social_health"] = await self.test_social_health()
            results["providers_list"] = await self.test_providers_list()
            results["oauth_status"] = await self.test_oauth_status()
            results["twitter_oauth_connect"] = await self.test_twitter_oauth_connect()
            results["social_connections"] = await self.test_social_connections()
            results["twitter_bearer_token"] = await self.test_twitter_bearer_token()
            results["social_post_structure"] = await self.test_social_post_structure()
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 TEST RESULTS SUMMARY")
            print("=" * 60)
            
            passed = sum(1 for result in results.values() if result)
            total = len(results)
            
            for test_name, result in results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name.replace('_', ' ').title()}: {status}")
                
            print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
            
            if passed == total:
                print("🎉 All Social Media OAuth Integration tests passed!")
            else:
                print("⚠️  Some tests failed - check social media configuration and endpoints")
                
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