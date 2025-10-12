#!/usr/bin/env python3
"""
Social Media OAuth Integration Backend Testing
Tests the newly implemented Social Media OAuth Integration endpoints
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://bme-profile-boost.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user credentials
TEST_USER = {
    "email": "creator@bigmannentertainment.com",
    "password": "CreatorProfile123!",
    "full_name": "Creator Profile Test User",
    "business_name": "Test Creator Business",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "address_line1": "123 Creator Street",
    "city": "Los Angeles",
    "state_province": "CA",
    "postal_code": "90210",
    "country": "USA"
}

class SocialMediaOAuthTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.profile_id = None
        self.asset_id = None
        self.proposal_id = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def register_and_login(self):
        """Register test user and login to get auth token"""
        print("🔐 Testing user registration and authentication...")
        
        # Try to register user (may already exist)
        try:
            async with self.session.post(f"{API_BASE}/auth/register", json=TEST_USER) as response:
                if response.status == 201:
                    print("✅ User registered successfully")
                elif response.status == 400:
                    print("ℹ️  User already exists, proceeding to login")
                else:
                    print(f"⚠️  Registration response: {response.status}")
        except Exception as e:
            print(f"⚠️  Registration error: {e}")
            
        # Login to get token
        login_data = {"email": TEST_USER["email"], "password": TEST_USER["password"]}
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.user_id = data.get("user", {}).get("id")
                    print("✅ Authentication successful")
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
        
    async def test_social_health(self):
        """Test 1: Social Media Integration Health Check"""
        print("\n🏥 Test 1: Social Media Integration Health Check")
        
        try:
            async with self.session.get(f"{API_BASE}/social/health") as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    service_status = data.get("status", "unknown")
                    if service_status == "healthy":
                        print("✅ Social Media Integration service is healthy")
                        providers = data.get("providers", [])
                        print(f"   Available providers: {len(providers)}")
                        for provider in providers:
                            print(f"   - {provider.get('name', provider.get('provider'))}: {'✅' if provider.get('configured') else '❌'}")
                        return True
                    else:
                        print(f"❌ Social Media service unhealthy: {service_status}")
                        return False
                else:
                    print(f"❌ Health check failed with status {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
            
    async def test_providers_list(self):
        """Test 2: Get Available Social Media Providers"""
        print("\n📋 Test 2: Get Available Social Media Providers")
        
        try:
            async with self.session.get(f"{API_BASE}/social/providers") as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    providers = data.get("providers", [])
                    print(f"✅ Found {len(providers)} social media providers")
                    
                    # Check for Twitter configuration
                    twitter_configured = False
                    for provider in providers:
                        if provider.get("provider") == "twitter":
                            twitter_configured = provider.get("configured", False)
                            print(f"   Twitter configured: {'✅' if twitter_configured else '❌'}")
                            break
                    
                    if twitter_configured:
                        print("✅ Twitter provider is properly configured")
                    else:
                        print("⚠️  Twitter provider not configured (expected for testing)")
                    
                    return True
                else:
                    print(f"❌ Failed to get providers list: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Providers list error: {e}")
            return False
            
    async def test_oauth_status(self):
        """Test 3: OAuth Configuration Status"""
        print("\n🔐 Test 3: OAuth Configuration Status")
        
        try:
            async with self.session.get(f"{API_BASE}/oauth/status") as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    print("✅ OAuth status endpoint working")
                    
                    # Check each platform configuration
                    platforms = ["facebook", "tiktok", "google_youtube", "twitter"]
                    configured_count = 0
                    
                    for platform in platforms:
                        if platform in data:
                            configured = data[platform].get("configured", False)
                            scope = data[platform].get("scope", "")
                            print(f"   {platform}: {'✅' if configured else '❌'} (scope: {scope})")
                            if configured:
                                configured_count += 1
                    
                    print(f"   Total configured platforms: {configured_count}/{len(platforms)}")
                    return True
                else:
                    print(f"❌ OAuth status failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ OAuth status error: {e}")
            return False
            
    async def test_twitter_oauth_connect(self):
        """Test 4: Twitter OAuth Connect Endpoint"""
        print("\n🐦 Test 4: Twitter OAuth Connect Endpoint")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            
            # Test OAuth connect endpoint (should return redirect or error)
            async with self.session.get(
                f"{API_BASE}/social/connect/twitter",
                headers=headers,
                allow_redirects=False
            ) as response:
                print(f"Status: {response.status}")
                
                if response.status == 302:
                    # Redirect to OAuth provider
                    location = response.headers.get('Location', '')
                    print(f"✅ OAuth redirect working: {location[:100]}...")
                    return True
                elif response.status == 400:
                    # Expected if Twitter not configured
                    data = await response.json()
                    error_detail = data.get("detail", "")
                    if "not configured" in error_detail or "Missing API credentials" in error_detail:
                        print("⚠️  Twitter OAuth not configured (expected for testing)")
                        print(f"   Error: {error_detail}")
                        return True
                    else:
                        print(f"❌ Unexpected error: {error_detail}")
                        return False
                else:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    print(f"❌ Unexpected status: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Twitter OAuth connect error: {e}")
            return False
            
    async def test_asset_creation(self):
        """Test 5: Asset Creation with GS1 Identifiers"""
        print("\n🎵 Test 5: Asset Creation with GS1 Identifiers")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        asset_data = {
            "title": "Test Music Track",
            "description": "A test music track for GS1 identifier testing",
            "asset_type": "music",
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "content_url": "https://example.com/track.mp3",
            "license": "All Rights Reserved",
            "copyright_notice": "© 2025 Big Mann Entertainment",
            "rights_holder": "Big Mann Entertainment"
        }
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{API_BASE}/profile/assets/create",
                json=asset_data,
                headers=headers
            ) as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    self.asset_id = data.get("asset", {}).get("id")
                    asset_info = data.get("asset", {})
                    print("✅ Asset created successfully")
                    print(f"   GTIN: {asset_info.get('gtin')}")
                    print(f"   ISRC: {asset_info.get('isrc')}")
                    print(f"   GS1 Digital Link: {asset_info.get('gs1_digital_link')}")
                    return True
                else:
                    print(f"❌ Asset creation failed: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Asset creation error: {e}")
            return False
            
    async def test_dao_proposal_creation(self):
        """Test 6: DAO Proposal Creation"""
        print("\n🗳️  Test 6: DAO Proposal Creation")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        proposal_data = {
            "title": "Test Governance Proposal",
            "description": "This is a test proposal for the DAO governance system to verify PostgreSQL integration",
            "proposal_type": "general",
            "target_asset_id": self.asset_id,
            "target_data": {"test": "data"},
            "voting_ends_in_days": 7
        }
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{API_BASE}/profile/dao/proposals",
                json=proposal_data,
                headers=headers
            ) as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    self.proposal_id = data.get("proposal", {}).get("id")
                    print("✅ DAO proposal created successfully")
                    return True
                else:
                    print(f"❌ DAO proposal creation failed: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ DAO proposal creation error: {e}")
            return False
            
    async def test_dao_voting(self):
        """Test 7: DAO Voting"""
        print("\n🗳️  Test 7: DAO Voting")
        
        if not self.auth_token or not self.proposal_id:
            print("❌ No auth token or proposal ID available")
            return False
            
        vote_data = {
            "choice": "yes",
            "comment": "This is a test vote for the PostgreSQL DAO system"
        }
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{API_BASE}/profile/dao/proposals/{self.proposal_id}/vote",
                json=vote_data,
                headers=headers
            ) as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    vote_counts = data.get("proposal", {}).get("votes", {})
                    print("✅ DAO vote recorded successfully")
                    print(f"   Vote counts: {vote_counts}")
                    return True
                else:
                    print(f"❌ DAO voting failed: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ DAO voting error: {e}")
            return False
            
    async def run_all_tests(self):
        """Run all PostgreSQL Creator Profile System tests"""
        print("🎯 PostgreSQL Creator Profile System Backend Testing")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Test results tracking
            results = {}
            
            # Authentication setup
            auth_success = await self.register_and_login()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with profile tests")
                return results
                
            # Run all tests
            results["postgresql_health"] = await self.test_postgresql_health()
            results["profile_creation"] = await self.test_profile_creation()
            results["profile_retrieval"] = await self.test_profile_retrieval()
            results["profile_update"] = await self.test_profile_update()
            results["asset_creation"] = await self.test_asset_creation()
            results["dao_proposal_creation"] = await self.test_dao_proposal_creation()
            results["dao_voting"] = await self.test_dao_voting()
            
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
                print("🎉 All PostgreSQL Creator Profile System tests passed!")
            else:
                print("⚠️  Some tests failed - check PostgreSQL connection and profile system")
                
            return results
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = ProfileSystemTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())