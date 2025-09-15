#!/usr/bin/env python3
"""
Comprehensive Music Reports Integration Backend Testing
Testing all Music Reports endpoints and DDEX integration for Big Mann Entertainment platform
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://creative-ledger.preview.emergentagent.com/api"

class MusicReportsBackendTester:
    def __init__(self):
        self.session = None
        self.access_token = None
        self.test_user_email = "musicreports.test@bigmannentertainment.com"
        self.test_user_password = "MusicReports2025!"
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def register_test_user(self) -> bool:
        """Register a test user for Music Reports testing"""
        try:
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": "Music Reports Test User",
                "business_name": "Music Reports Test Business",
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "123 Music Reports St",
                "city": "Nashville",
                "state_province": "TN",
                "postal_code": "37201",
                "country": "US"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=registration_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    print(f"✅ Test user registered successfully")
                    return True
                elif response.status == 400:
                    # User might already exist, try to login
                    return await self.login_test_user()
                else:
                    print(f"❌ Registration failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return await self.login_test_user()
            
    async def login_test_user(self) -> bool:
        """Login test user"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    print(f"✅ Test user logged in successfully")
                    return True
                else:
                    print(f"❌ Login failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
            
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
    async def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          expected_status: int = 200, test_name: str = "") -> Dict[str, Any]:
        """Test a single endpoint"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            headers = self.get_auth_headers()
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
                
            success = status == expected_status
            result = {
                "success": success,
                "status": status,
                "expected_status": expected_status,
                "response": response_data,
                "test_name": test_name,
                "endpoint": endpoint
            }
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "test_name": test_name,
                "endpoint": endpoint
            }
            self.test_results.append(result)
            return result
            
    async def test_music_reports_dashboard(self):
        """Test Music Reports dashboard endpoint"""
        print("\n🎵 Testing Music Reports Dashboard...")
        
        result = await self.test_endpoint(
            "GET", 
            "/music-reports/dashboard",
            test_name="Music Reports Dashboard"
        )
        
        if result["success"]:
            dashboard_data = result["response"].get("music_reports_dashboard", {})
            print(f"✅ Dashboard loaded successfully")
            print(f"   - User: {dashboard_data.get('user_info', {}).get('full_name', 'N/A')}")
            print(f"   - Total Works: {dashboard_data.get('quick_stats', {}).get('total_works', 0)}")
            print(f"   - Works Synced: {dashboard_data.get('quick_stats', {}).get('works_synced', 0)}")
            print(f"   - Pending Sync: {dashboard_data.get('quick_stats', {}).get('pending_sync', 0)}")
            print(f"   - Total Collected: ${dashboard_data.get('royalty_summary', {}).get('total_collected', 0)}")
            return True
        else:
            print(f"❌ Dashboard test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_integration_status(self):
        """Test Music Reports integration status endpoint"""
        print("\n🔗 Testing Integration Status...")
        
        result = await self.test_endpoint(
            "GET",
            "/music-reports/integration-status", 
            test_name="Integration Status"
        )
        
        if result["success"]:
            status = result["response"].get("integration_status", {})
            print(f"✅ Integration status retrieved")
            print(f"   - Connected: {status.get('connected', False)}")
            print(f"   - API Version: {status.get('api_version', 'N/A')}")
            print(f"   - Last Sync: {status.get('last_sync', 'Never')}")
            print(f"   - Total Works: {status.get('total_works_registered', 0)}")
            print(f"   - Pending Sync: {status.get('pending_sync', 0)}")
            print(f"   - Total Royalties: ${status.get('total_royalties_collected', 0)}")
            return True
        else:
            print(f"❌ Integration status test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_cwr_works(self):
        """Test CWR works endpoint"""
        print("\n📝 Testing CWR Works...")
        
        result = await self.test_endpoint(
            "GET",
            "/music-reports/cwr-works?limit=10&offset=0",
            test_name="CWR Works"
        )
        
        if result["success"]:
            response_data = result["response"]
            works = response_data.get("cwr_works", [])
            pagination = response_data.get("pagination", {})
            
            print(f"✅ CWR works retrieved")
            print(f"   - Total Works: {pagination.get('total', 0)}")
            print(f"   - Returned: {len(works)}")
            print(f"   - Has More: {pagination.get('has_more', False)}")
            
            if works:
                work = works[0]
                print(f"   - Sample Work: {work.get('title', 'N/A')}")
                print(f"   - Composer: {work.get('composer', 'N/A')}")
                print(f"   - Status: {work.get('music_reports_status', 'N/A')}")
                
            return True
        else:
            print(f"❌ CWR works test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_sync_initiation(self):
        """Test Music Reports sync initiation"""
        print("\n🔄 Testing Sync Initiation...")
        
        result = await self.test_endpoint(
            "POST",
            "/music-reports/sync",
            test_name="Sync Initiation"
        )
        
        if result["success"]:
            sync_result = result["response"].get("sync_result", {})
            print(f"✅ Sync initiated successfully")
            print(f"   - Sync ID: {sync_result.get('sync_id', 'N/A')}")
            print(f"   - Status: {sync_result.get('status', 'N/A')}")
            print(f"   - Works Processed: {sync_result.get('works_processed', 0)}")
            print(f"   - Works Synced: {sync_result.get('works_synced', 0)}")
            return True
        else:
            print(f"❌ Sync initiation test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_royalty_data(self):
        """Test royalty data endpoint"""
        print("\n💰 Testing Royalty Data...")
        
        result = await self.test_endpoint(
            "GET",
            "/music-reports/royalties?period=2024-Q4",
            test_name="Royalty Data"
        )
        
        if result["success"]:
            royalty_data = result["response"].get("royalty_data", {})
            print(f"✅ Royalty data retrieved")
            print(f"   - Period: {royalty_data.get('period', 'N/A')}")
            print(f"   - Total Collected: ${royalty_data.get('total_collected', 0)}")
            print(f"   - Pending Payment: ${royalty_data.get('pending_payment', 0)}")
            print(f"   - Paid Out: ${royalty_data.get('paid_out', 0)}")
            
            collections_by_territory = royalty_data.get("collections_by_territory", {})
            if collections_by_territory:
                print(f"   - Top Territory: {max(collections_by_territory.items(), key=lambda x: x[1])}")
                
            return True
        else:
            print(f"❌ Royalty data test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_royalty_summary(self):
        """Test royalty summary endpoint"""
        print("\n📊 Testing Royalty Summary...")
        
        result = await self.test_endpoint(
            "GET",
            "/music-reports/royalties/summary",
            test_name="Royalty Summary"
        )
        
        if result["success"]:
            summary = result["response"].get("royalty_summary", {})
            print(f"✅ Royalty summary retrieved")
            print(f"   - Total Collected: ${summary.get('total_collected', 0)}")
            print(f"   - Pending Payment: ${summary.get('pending_payment', 0)}")
            print(f"   - Paid Out: ${summary.get('paid_out', 0)}")
            print(f"   - Currency: {summary.get('currency', 'USD')}")
            
            next_payment = summary.get("next_payment")
            if next_payment:
                print(f"   - Next Payment: ${next_payment.get('amount', 0)} on {next_payment.get('payment_date', 'TBD')}")
                
            return True
        else:
            print(f"❌ Royalty summary test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_sync_capabilities(self):
        """Test sync capabilities endpoint"""
        print("\n⚙️ Testing Sync Capabilities...")
        
        result = await self.test_endpoint(
            "GET",
            "/music-reports/capabilities",
            test_name="Sync Capabilities"
        )
        
        if result["success"]:
            capabilities = result["response"].get("capabilities", {})
            print(f"✅ Sync capabilities retrieved")
            print(f"   - Automatic Sync: {capabilities.get('automatic_sync', False)}")
            print(f"   - Bulk Upload: {capabilities.get('bulk_upload', False)}")
            print(f"   - Real-time Updates: {capabilities.get('real_time_updates', False)}")
            print(f"   - Supported Territories: {len(capabilities.get('supported_territories', []))}")
            print(f"   - Supported PRIs: {len(capabilities.get('supported_pris', []))}")
            print(f"   - Max Batch Size: {capabilities.get('max_batch_size', 0)}")
            return True
        else:
            print(f"❌ Sync capabilities test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_sync_history(self):
        """Test sync history endpoint"""
        print("\n📜 Testing Sync History...")
        
        result = await self.test_endpoint(
            "GET",
            "/music-reports/sync-history?limit=10",
            test_name="Sync History"
        )
        
        if result["success"]:
            history = result["response"].get("sync_history", [])
            print(f"✅ Sync history retrieved")
            print(f"   - History Records: {len(history)}")
            
            if history:
                recent = history[0]
                print(f"   - Most Recent: {recent.get('sync_id', 'N/A')}")
                print(f"   - Status: {recent.get('status', 'N/A')}")
                print(f"   - Works Processed: {recent.get('works_processed', 0)}")
                
            return True
        else:
            print(f"❌ Sync history test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_royalty_statements(self):
        """Test royalty statements endpoint"""
        print("\n📄 Testing Royalty Statements...")
        
        result = await self.test_endpoint(
            "GET",
            "/music-reports/statements",
            test_name="Royalty Statements"
        )
        
        if result["success"]:
            statements = result["response"].get("statements", [])
            print(f"✅ Royalty statements retrieved")
            print(f"   - Available Statements: {len(statements)}")
            
            if statements:
                statement = statements[0]
                print(f"   - Latest Statement: {statement.get('statement_id', 'N/A')}")
                print(f"   - Period: {statement.get('period', 'N/A')}")
                print(f"   - Amount: ${statement.get('total_amount', 0)}")
                print(f"   - Format: {statement.get('format', 'N/A')}")
                
            return True
        else:
            print(f"❌ Royalty statements test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_ddex_music_reports_cwr(self):
        """Test DDEX Music Reports CWR integration endpoint"""
        print("\n🎼 Testing DDEX Music Reports CWR Integration...")
        
        result = await self.test_endpoint(
            "GET",
            "/ddex/music-reports/cwr",
            test_name="DDEX Music Reports CWR"
        )
        
        if result["success"]:
            cwr_data = result["response"].get("music_reports_cwr", {})
            integration_status = cwr_data.get("integration_status", {})
            works = cwr_data.get("cwr_works", [])
            
            print(f"✅ DDEX Music Reports CWR integration retrieved")
            print(f"   - Connected: {integration_status.get('connected', False)}")
            print(f"   - Total Works: {integration_status.get('total_works_registered', 0)}")
            print(f"   - Pending Sync: {integration_status.get('pending_sync', 0)}")
            print(f"   - CWR Works: {len(works)}")
            
            capabilities = cwr_data.get("sync_capabilities", {})
            print(f"   - Automatic Sync: {capabilities.get('automatic_sync', False)}")
            print(f"   - Bulk Upload: {capabilities.get('bulk_upload', False)}")
            
            return True
        else:
            print(f"❌ DDEX Music Reports CWR test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_ddex_music_reports_sync(self):
        """Test DDEX Music Reports sync endpoint"""
        print("\n🔄 Testing DDEX Music Reports Sync...")
        
        result = await self.test_endpoint(
            "POST",
            "/ddex/music-reports/sync",
            test_name="DDEX Music Reports Sync"
        )
        
        if result["success"]:
            sync_result = result["response"].get("sync_result", {})
            print(f"✅ DDEX Music Reports sync initiated")
            print(f"   - Sync ID: {sync_result.get('sync_id', 'N/A')}")
            print(f"   - Status: {sync_result.get('status', 'N/A')}")
            print(f"   - Message: {sync_result.get('message', 'N/A')}")
            print(f"   - Works to Sync: {sync_result.get('works_to_sync', 0)}")
            print(f"   - Estimated Duration: {sync_result.get('estimated_duration', 'N/A')}")
            return True
        else:
            print(f"❌ DDEX Music Reports sync test failed: {result.get('error', 'Unknown error')}")
            return False
            
    async def test_authentication_requirements(self):
        """Test that all endpoints require proper authentication"""
        print("\n🔐 Testing Authentication Requirements...")
        
        # Test without authentication
        test_endpoints = [
            "/music-reports/dashboard",
            "/music-reports/integration-status", 
            "/music-reports/cwr-works",
            "/music-reports/royalties",
            "/music-reports/capabilities",
            "/ddex/music-reports/cwr"
        ]
        
        auth_failures = 0
        for endpoint in test_endpoints:
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    if response.status in [401, 403]:
                        auth_failures += 1
                    else:
                        print(f"⚠️ Endpoint {endpoint} doesn't require authentication (status: {response.status})")
            except Exception as e:
                print(f"⚠️ Error testing {endpoint}: {str(e)}")
                
        print(f"✅ Authentication test completed: {auth_failures}/{len(test_endpoints)} endpoints properly secured")
        return auth_failures >= len(test_endpoints) * 0.8  # 80% should be secured
        
    async def run_comprehensive_tests(self):
        """Run all Music Reports integration tests"""
        print("🎯 COMPREHENSIVE MUSIC REPORTS INTEGRATION BACKEND TESTING")
        print("=" * 70)
        
        await self.setup_session()
        
        try:
            # Setup test user
            if not await self.register_test_user():
                print("❌ Failed to setup test user. Aborting tests.")
                return
                
            # Run all tests
            tests = [
                ("Music Reports Dashboard", self.test_music_reports_dashboard),
                ("Integration Status", self.test_integration_status),
                ("CWR Works", self.test_cwr_works),
                ("Sync Initiation", self.test_sync_initiation),
                ("Royalty Data", self.test_royalty_data),
                ("Royalty Summary", self.test_royalty_summary),
                ("Sync Capabilities", self.test_sync_capabilities),
                ("Sync History", self.test_sync_history),
                ("Royalty Statements", self.test_royalty_statements),
                ("DDEX Music Reports CWR", self.test_ddex_music_reports_cwr),
                ("DDEX Music Reports Sync", self.test_ddex_music_reports_sync),
                ("Authentication Requirements", self.test_authentication_requirements)
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                try:
                    if await test_func():
                        passed_tests += 1
                except Exception as e:
                    print(f"❌ {test_name} failed with exception: {str(e)}")
                    
            # Print summary
            print("\n" + "=" * 70)
            print("🎯 MUSIC REPORTS INTEGRATION TEST SUMMARY")
            print("=" * 70)
            
            success_rate = (passed_tests / total_tests) * 100
            print(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Music Reports integration is production-ready!")
            elif success_rate >= 75:
                print("✅ GOOD: Music Reports integration is mostly functional with minor issues")
            elif success_rate >= 50:
                print("⚠️ FAIR: Music Reports integration has significant issues that need attention")
            else:
                print("❌ POOR: Music Reports integration requires major fixes")
                
            # Print detailed results
            print("\n📋 DETAILED TEST RESULTS:")
            for result in self.test_results:
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                print(f"   {status} - {result['test_name']}")
                if not result["success"] and "error" in result:
                    print(f"      Error: {result['error']}")
                    
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = MusicReportsBackendTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())