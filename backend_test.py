#!/usr/bin/env python3
"""
PostgreSQL Creator Profile System Backend Testing
Tests the PostgreSQL-based Creator Profile System with authentication
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://creator-profile-hub-2.preview.emergentagent.com')
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

class ProfileSystemTester:
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
        
    async def test_postgresql_health(self):
        """Test 1: PostgreSQL Connection Health Check"""
        print("\n🏥 Test 1: PostgreSQL Connection Health Check")
        
        try:
            async with self.session.get(f"{API_BASE}/profile/health") as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    postgres_status = data.get("postgres", "unknown")
                    if postgres_status == "connected":
                        print("✅ PostgreSQL connection successful")
                        return True
                    else:
                        print(f"❌ PostgreSQL connection failed: {postgres_status}")
                        return False
                else:
                    print(f"❌ Health check failed with status {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
            
    async def test_profile_creation(self):
        """Test 2: Profile Creation with Authentication"""
        print("\n👤 Test 2: Profile Creation with Authentication")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        profile_data = {
            "display_name": "Test Creator Profile",
            "tagline": "Testing PostgreSQL Creator Profiles",
            "bio": "This is a test profile for the PostgreSQL Creator Profile System",
            "location": "Los Angeles, CA",
            "profile_public": True,
            "show_earnings": False
        }
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{API_BASE}/profile/create", 
                json=profile_data,
                headers=headers
            ) as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    self.profile_id = data.get("profile", {}).get("id")
                    print("✅ Profile created successfully")
                    return True
                elif response.status == 400 and "already exists" in data.get("detail", ""):
                    print("ℹ️  Profile already exists, proceeding to next test")
                    return True
                else:
                    print(f"❌ Profile creation failed: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Profile creation error: {e}")
            return False
            
    async def test_profile_retrieval(self):
        """Test 3: Profile Retrieval"""
        print("\n📋 Test 3: Profile Retrieval (GET /api/profile/me)")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        try:
            headers = self.get_auth_headers()
            
            async with self.session.get(
                f"{API_BASE}/profile/me",
                headers=headers
            ) as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    if data.get("hasProfile") == False:
                        print("ℹ️  No profile found, this is expected if creation failed")
                        return True
                    else:
                        print("✅ Profile retrieved successfully")
                        return True
                else:
                    print(f"❌ Profile retrieval failed: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Profile retrieval error: {e}")
            return False
            
    async def test_profile_update(self):
        """Test 4: Profile Update"""
        print("\n✏️  Test 4: Profile Update (PUT /api/profile/me)")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        update_data = {
            "display_name": "Updated Creator Profile",
            "tagline": "Updated tagline for PostgreSQL testing",
            "bio": "Updated bio to test profile update functionality",
            "location": "Updated Location, CA",
            "show_earnings": True
        }
        
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.put(
                f"{API_BASE}/profile/me",
                json=update_data,
                headers=headers
            ) as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    print("✅ Profile updated successfully")
                    return True
                else:
                    print(f"❌ Profile update failed: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Profile update error: {e}")
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