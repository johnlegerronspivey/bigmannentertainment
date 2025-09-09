#!/usr/bin/env python3
"""
Comprehensive Agency Onboarding Module Backend Testing
Tests blockchain-based image licensing system for Big Mann Entertainment
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timezone
import os
import sys

# Backend URL from environment
BACKEND_URL = "https://bme-platform-1.preview.emergentagent.com/api"

class AgencyOnboardingTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.auth_token = None
        self.test_user_data = {
            "email": f"agency_test_{uuid.uuid4().hex[:8]}@bigmannentertainment.com",
            "password": "AgencyTest123!",
            "full_name": "Agency Test Manager",
            "business_name": "Test Talent Agency LLC",
            "date_of_birth": "1985-06-15T00:00:00Z",
            "address_line1": "123 Agency Street",
            "city": "Los Angeles",
            "state_province": "California",
            "postal_code": "90210",
            "country": "United States"
        }
        self.agency_id = None
        self.talent_id = None
        self.asset_id = None
        self.contract_id = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def register_test_user(self):
        """Register a test user for agency testing"""
        print("🔐 Registering test user for agency testing...")
        
        try:
            async with self.session.post(
                f"{self.backend_url}/auth/register",
                json=self.test_user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print(f"✅ User registered successfully: {self.test_user_data['email']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ User registration failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ User registration error: {str(e)}")
            return False
    
    async def login_test_user(self):
        """Login with test user credentials"""
        print("🔑 Logging in test user...")
        
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            
            async with self.session.post(
                f"{self.backend_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print(f"✅ User login successful")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ User login failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ User login error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_agency_registration(self):
        """Test POST /api/agency/register"""
        print("\n🏢 Testing Agency Registration...")
        
        agency_data = {
            "name": "Big Mann Talent Agency",
            "business_registration_number": "BME-2025-001",
            "contact_info": {
                "email": "contact@bigmanntalent.com",
                "phone": "+1-555-0123",
                "address": "456 Talent Boulevard, Hollywood, CA 90028"
            },
            "wallet_addresses": {
                "ethereum": "0x742d35Cc6634C0532925a3b8D4C2C4e4C4C4C4C4",
                "solana": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
            },
            "business_type": "Talent Management Agency",
            "tax_id": "12-3456789",
            "operating_countries": ["United States", "Canada"]
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/agency/register",
                json=agency_data,
                headers={**self.get_auth_headers(), "Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.agency_id = data.get("agency_id")
                    print(f"✅ Agency registered successfully: {self.agency_id}")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Verification Status: {data.get('verification_status')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Agency registration failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Agency registration error: {str(e)}")
            return False
    
    async def test_agency_profile_get(self):
        """Test GET /api/agency/profile"""
        print("\n📋 Testing Get Agency Profile...")
        
        try:
            async with self.session.get(
                f"{self.backend_url}/agency/profile",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    agency = data.get("agency", {})
                    print(f"✅ Agency profile retrieved successfully")
                    print(f"   Agency Name: {agency.get('name')}")
                    print(f"   Verification Status: {agency.get('verification_status')}")
                    print(f"   Total Talent: {agency.get('total_talent', 0)}")
                    print(f"   Total Assets: {agency.get('total_assets', 0)}")
                    print(f"   Total Licenses: {agency.get('total_licenses_sold', 0)}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Get agency profile failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Get agency profile error: {str(e)}")
            return False
    
    async def test_agency_profile_update(self):
        """Test PUT /api/agency/profile"""
        print("\n✏️ Testing Update Agency Profile...")
        
        update_data = {
            "commission_rate": 0.20,
            "auto_approve_licenses": True,
            "min_license_price": 75.0
        }
        
        try:
            async with self.session.put(
                f"{self.backend_url}/agency/profile",
                json=update_data,
                headers={**self.get_auth_headers(), "Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Agency profile updated successfully")
                    print(f"   Status: {data.get('status')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Update agency profile failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Update agency profile error: {str(e)}")
            return False
    
    async def test_kyc_upload(self):
        """Test POST /api/agency/upload-kyc"""
        print("\n📄 Testing KYC Document Upload...")
        
        # Create mock file data
        mock_file_content = b"Mock KYC Document Content - Business License"
        
        try:
            # Create multipart form data
            data = aiohttp.FormData()
            data.add_field('files', mock_file_content, filename='business_license.pdf', content_type='application/pdf')
            data.add_field('document_type', 'kyc')
            
            async with self.session.post(
                f"{self.backend_url}/agency/upload-kyc",
                data=data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ KYC documents uploaded successfully")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Documents Count: {len(data.get('documents', []))}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ KYC upload failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ KYC upload error: {str(e)}")
            return False
    
    async def test_talent_creation(self):
        """Test POST /api/agency/talent"""
        print("\n👤 Testing Talent Creation...")
        
        talent_data = {
            "name": "Alexandra Johnson",
            "stage_name": "Alex J",
            "bio": "Professional model and actress with 5 years of experience in fashion and commercial photography.",
            "age_range": "25-30",
            "gender": "Female",
            "ethnicity": "Mixed",
            "categories": ["Fashion", "Commercial", "Editorial"],
            "skills": ["Runway", "Photography", "Acting", "Dance"],
            "languages": ["English", "Spanish", "French"]
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/agency/talent",
                json=talent_data,
                headers={**self.get_auth_headers(), "Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.talent_id = data.get("talent_id")
                    print(f"✅ Talent created successfully: {self.talent_id}")
                    print(f"   Status: {data.get('status')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Talent creation failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Talent creation error: {str(e)}")
            return False
    
    async def test_get_agency_talent(self):
        """Test GET /api/agency/talent"""
        print("\n👥 Testing Get Agency Talent List...")
        
        try:
            async with self.session.get(
                f"{self.backend_url}/agency/talent",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    talent_list = data.get("talent", [])
                    print(f"✅ Agency talent list retrieved successfully")
                    print(f"   Total Talent: {data.get('total', 0)}")
                    for talent in talent_list:
                        print(f"   - {talent.get('name')} ({talent.get('stage_name', 'N/A')})")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Get agency talent failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Get agency talent error: {str(e)}")
            return False
    
    async def test_talent_asset_upload(self):
        """Test POST /api/agency/talent/{talent_id}/upload-assets"""
        print("\n🖼️ Testing Talent Asset Upload...")
        
        if not self.talent_id:
            print("❌ No talent ID available for asset upload test")
            return False
        
        # Create mock image data
        mock_image_content = b"Mock Image Content - Professional Headshot"
        
        try:
            # Create multipart form data
            data = aiohttp.FormData()
            data.add_field('files', mock_image_content, filename='headshot.jpg', content_type='image/jpeg')
            
            async with self.session.post(
                f"{self.backend_url}/agency/talent/{self.talent_id}/upload-assets",
                data=data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assets = data.get("assets", [])
                    if assets:
                        self.asset_id = assets[0].get("id")
                    print(f"✅ Talent assets uploaded successfully")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Assets Count: {len(assets)}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Talent asset upload failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Talent asset upload error: {str(e)}")
            return False
    
    async def test_license_contract_creation(self):
        """Test POST /api/agency/license-contract"""
        print("\n📜 Testing License Contract Creation...")
        
        if not self.asset_id:
            print("❌ No asset ID available for license contract test")
            return False
        
        contract_data = {
            "asset_id": self.asset_id,
            "talent_id": self.talent_id,
            "blockchain_network": "ethereum",
            "contract_standard": "erc721",
            "license_type": "exclusive",
            "base_price": 500.0,
            "royalty_splits": {
                "agency": 0.15,
                "talent": 0.70,
                "platform": 0.15
            },
            "usage_terms": {
                "commercial_use": True,
                "editorial_use": True,
                "web_use": True,
                "print_use": True
            },
            "exclusivity": True,
            "duration_months": 12,
            "territory": ["United States", "Canada"]
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/agency/license-contract",
                json=contract_data,
                headers={**self.get_auth_headers(), "Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.contract_id = data.get("contract_id")
                    print(f"✅ License contract created successfully: {self.contract_id}")
                    print(f"   Status: {data.get('status')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ License contract creation failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ License contract creation error: {str(e)}")
            return False
    
    async def test_blockchain_deployment(self):
        """Test POST /api/agency/license-contract/{contract_id}/deploy"""
        print("\n⛓️ Testing Blockchain Contract Deployment...")
        
        if not self.contract_id:
            print("❌ No contract ID available for blockchain deployment test")
            return False
        
        try:
            async with self.session.post(
                f"{self.backend_url}/agency/license-contract/{self.contract_id}/deploy",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Contract deployed to blockchain successfully")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Blockchain Network: {data.get('blockchain_network')}")
                    print(f"   Contract Address: {data.get('contract_address')}")
                    print(f"   Token ID: {data.get('token_id')}")
                    print(f"   Transaction Hash: {data.get('transaction_hash')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Blockchain deployment failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Blockchain deployment error: {str(e)}")
            return False
    
    async def test_agency_dashboard(self):
        """Test GET /api/agency/dashboard"""
        print("\n📊 Testing Agency Dashboard...")
        
        try:
            async with self.session.get(
                f"{self.backend_url}/agency/dashboard",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    dashboard = data.get("dashboard", {})
                    agency_info = dashboard.get("agency_info", {})
                    statistics = dashboard.get("statistics", {})
                    
                    print(f"✅ Agency dashboard retrieved successfully")
                    print(f"   Agency: {agency_info.get('name')}")
                    print(f"   Verification Status: {agency_info.get('verification_status')}")
                    print(f"   KYC Completed: {agency_info.get('kyc_completed')}")
                    print(f"   Total Talent: {statistics.get('total_talent')}")
                    print(f"   Total Assets: {statistics.get('total_assets')}")
                    print(f"   Total Contracts: {statistics.get('total_contracts')}")
                    print(f"   Deployed Contracts: {statistics.get('deployed_contracts')}")
                    print(f"   Active Licenses: {statistics.get('active_licenses')}")
                    print(f"   Total Revenue: ${statistics.get('total_revenue', 0):.2f}")
                    print(f"   Monthly Revenue: ${statistics.get('monthly_revenue', 0):.2f}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Agency dashboard failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Agency dashboard error: {str(e)}")
            return False
    
    async def test_authentication_security(self):
        """Test authentication requirements for all endpoints"""
        print("\n🔒 Testing Authentication Security...")
        
        endpoints_to_test = [
            "/agency/register",
            "/agency/profile",
            "/agency/upload-kyc",
            "/agency/talent",
            "/agency/dashboard"
        ]
        
        security_passed = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint in endpoints_to_test:
            try:
                async with self.session.get(f"{self.backend_url}{endpoint}") as response:
                    if response.status in [401, 403]:
                        print(f"   ✅ {endpoint} - Properly protected (Status: {response.status})")
                        security_passed += 1
                    else:
                        print(f"   ❌ {endpoint} - Security issue (Status: {response.status})")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error testing security: {str(e)}")
        
        print(f"\n🔒 Authentication Security Results: {security_passed}/{total_endpoints} endpoints properly protected")
        return security_passed == total_endpoints
    
    async def run_comprehensive_test(self):
        """Run all agency onboarding tests"""
        print("🎯 COMPREHENSIVE AGENCY ONBOARDING MODULE TESTING")
        print("=" * 60)
        
        await self.setup_session()
        
        test_results = []
        
        try:
            # Authentication Setup
            print("\n📋 PHASE 1: AUTHENTICATION SETUP")
            print("-" * 40)
            
            # Try to register user, if fails try to login
            if not await self.register_test_user():
                if not await self.login_test_user():
                    print("❌ CRITICAL: Cannot authenticate user for testing")
                    return
            
            # Core Agency Tests
            print("\n🏢 PHASE 2: AGENCY MANAGEMENT")
            print("-" * 40)
            
            test_results.append(("Agency Registration", await self.test_agency_registration()))
            test_results.append(("Get Agency Profile", await self.test_agency_profile_get()))
            test_results.append(("Update Agency Profile", await self.test_agency_profile_update()))
            test_results.append(("KYC Document Upload", await self.test_kyc_upload()))
            
            # Talent Management Tests
            print("\n👤 PHASE 3: TALENT MANAGEMENT")
            print("-" * 40)
            
            test_results.append(("Talent Creation", await self.test_talent_creation()))
            test_results.append(("Get Agency Talent", await self.test_get_agency_talent()))
            test_results.append(("Talent Asset Upload", await self.test_talent_asset_upload()))
            
            # Licensing Workflow Tests
            print("\n📜 PHASE 4: LICENSING WORKFLOW")
            print("-" * 40)
            
            test_results.append(("License Contract Creation", await self.test_license_contract_creation()))
            test_results.append(("Blockchain Deployment", await self.test_blockchain_deployment()))
            
            # Dashboard and Security Tests
            print("\n📊 PHASE 5: DASHBOARD & SECURITY")
            print("-" * 40)
            
            test_results.append(("Agency Dashboard", await self.test_agency_dashboard()))
            test_results.append(("Authentication Security", await self.test_authentication_security()))
            
        finally:
            await self.cleanup_session()
        
        # Results Summary
        print("\n" + "=" * 60)
        print("🎯 AGENCY ONBOARDING MODULE TEST RESULTS")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status:<12} {test_name}")
            if result:
                passed_tests += 1
        
        print("-" * 60)
        print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Agency Onboarding Module is fully functional!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOSTLY SUCCESSFUL - Minor issues detected")
        else:
            print("❌ SIGNIFICANT ISSUES - Multiple test failures detected")
        
        return passed_tests, total_tests

async def main():
    """Main test execution"""
    tester = AgencyOnboardingTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())