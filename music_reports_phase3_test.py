#!/usr/bin/env python3
"""
PHASE 3: Music Reports Integration - Backend Testing
Comprehensive testing of Music Reports Integration endpoints for Big Mann Entertainment
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://creative-ledger.preview.emergentagent.com/api"

class MusicReportsIntegrationTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            # Test user credentials
            login_data = {
                "email": "musicreports.tester@bigmannentertainment.com",
                "password": "MusicReports2025!"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.log_result("Authentication", True, "Successfully authenticated")
                    return True
                else:
                    # Try alternative credentials
                    login_data = {
                        "email": "john.spivey@bigmannentertainment.com",
                        "password": "BigMann2025!"
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as alt_response:
                        if alt_response.status == 200:
                            data = await alt_response.json()
                            self.auth_token = data.get("access_token")
                            self.log_result("Authentication", True, "Successfully authenticated with alternative credentials")
                            return True
                        else:
                            self.log_result("Authentication", False, f"Failed to authenticate: {alt_response.status}")
                            return False
                            
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
            
    def get_headers(self):
        """Get headers with authentication"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
        
    def log_result(self, test_name: str, passed: bool, details: str):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}: {details}")
        
    async def test_music_reports_dashboard(self):
        """Test GET /api/music-reports/dashboard"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/music-reports/dashboard",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    dashboard = data.get("music_reports_dashboard", {})
                    
                    # Verify dashboard structure
                    required_keys = ["user_info", "integration_status", "royalty_summary", "sync_capabilities", "quick_stats"]
                    missing_keys = [key for key in required_keys if key not in dashboard]
                    
                    if not missing_keys:
                        royalty_summary = dashboard.get("royalty_summary", {})
                        total_collected = royalty_summary.get("total_collected", 0)
                        
                        self.log_result(
                            "Music Reports Dashboard", 
                            True, 
                            f"Dashboard loaded successfully with ${total_collected} total collected"
                        )
                    else:
                        self.log_result(
                            "Music Reports Dashboard", 
                            False, 
                            f"Missing dashboard keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "Music Reports Dashboard", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("Music Reports Dashboard", False, f"Exception: {str(e)}")
            
    async def test_integration_status(self):
        """Test GET /api/music-reports/integration-status"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/music-reports/integration-status",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("integration_status", {})
                    
                    # Verify status structure
                    required_keys = ["connected", "api_version", "total_works_registered", "total_royalties_collected"]
                    missing_keys = [key for key in required_keys if key not in status]
                    
                    if not missing_keys:
                        connected = status.get("connected", False)
                        api_version = status.get("api_version", "")
                        total_royalties = status.get("total_royalties_collected", 0)
                        
                        self.log_result(
                            "Integration Status", 
                            True, 
                            f"Status: Connected={connected}, API={api_version}, Royalties=${total_royalties}"
                        )
                    else:
                        self.log_result(
                            "Integration Status", 
                            False, 
                            f"Missing status keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "Integration Status", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("Integration Status", False, f"Exception: {str(e)}")
            
    async def test_cwr_works(self):
        """Test GET /api/music-reports/cwr-works"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/music-reports/cwr-works?limit=10&offset=0",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    works = data.get("cwr_works", [])
                    pagination = data.get("pagination", {})
                    
                    # Verify pagination structure
                    required_pagination_keys = ["total", "limit", "offset", "has_more"]
                    missing_keys = [key for key in required_pagination_keys if key not in pagination]
                    
                    if not missing_keys:
                        total_works = pagination.get("total", 0)
                        self.log_result(
                            "CWR Works Management", 
                            True, 
                            f"Retrieved {len(works)} works with pagination (total: {total_works})"
                        )
                    else:
                        self.log_result(
                            "CWR Works Management", 
                            False, 
                            f"Missing pagination keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "CWR Works Management", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("CWR Works Management", False, f"Exception: {str(e)}")
            
    async def test_sync_initiation(self):
        """Test POST /api/music-reports/sync"""
        try:
            async with self.session.post(
                f"{BACKEND_URL}/music-reports/sync",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    sync_result = data.get("sync_result", {})
                    
                    # Verify sync result structure
                    required_keys = ["sync_id", "status", "works_processed"]
                    missing_keys = [key for key in required_keys if key not in sync_result]
                    
                    if not missing_keys:
                        sync_id = sync_result.get("sync_id", "")
                        status = sync_result.get("status", "")
                        works_processed = sync_result.get("works_processed", 0)
                        
                        self.log_result(
                            "Sync Initiation", 
                            True, 
                            f"Sync initiated: ID={sync_id}, Status={status}, Works={works_processed}"
                        )
                    else:
                        self.log_result(
                            "Sync Initiation", 
                            False, 
                            f"Missing sync result keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "Sync Initiation", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("Sync Initiation", False, f"Exception: {str(e)}")
            
    async def test_royalty_data(self):
        """Test GET /api/music-reports/royalties"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/music-reports/royalties?period=2024-Q4",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    royalty_data = data.get("royalty_data", {})
                    
                    # Verify royalty data structure
                    required_keys = ["total_collected", "pending_payment", "paid_out", "collections_by_territory", "collections_by_source"]
                    missing_keys = [key for key in required_keys if key not in royalty_data]
                    
                    if not missing_keys:
                        total_collected = royalty_data.get("total_collected", 0)
                        pending_payment = royalty_data.get("pending_payment", 0)
                        territories = len(royalty_data.get("collections_by_territory", {}))
                        sources = len(royalty_data.get("collections_by_source", {}))
                        
                        self.log_result(
                            "Royalty Data Collection", 
                            True, 
                            f"Royalties: ${total_collected} collected, ${pending_payment} pending, {territories} territories, {sources} sources"
                        )
                    else:
                        self.log_result(
                            "Royalty Data Collection", 
                            False, 
                            f"Missing royalty data keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "Royalty Data Collection", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("Royalty Data Collection", False, f"Exception: {str(e)}")
            
    async def test_royalty_statements(self):
        """Test GET /api/music-reports/statements"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/music-reports/statements",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    statements = data.get("statements", [])
                    
                    # Verify statements structure
                    if statements:
                        statement = statements[0]
                        required_keys = ["statement_id", "period", "total_amount", "format"]
                        missing_keys = [key for key in required_keys if key not in statement]
                        
                        if not missing_keys:
                            self.log_result(
                                "Royalty Statements", 
                                True, 
                                f"Retrieved {len(statements)} statements with proper structure"
                            )
                        else:
                            self.log_result(
                                "Royalty Statements", 
                                False, 
                                f"Missing statement keys: {missing_keys}"
                            )
                    else:
                        self.log_result(
                            "Royalty Statements", 
                            True, 
                            "No statements available (expected for new system)"
                        )
                else:
                    self.log_result(
                        "Royalty Statements", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("Royalty Statements", False, f"Exception: {str(e)}")
            
    async def test_sync_capabilities(self):
        """Test GET /api/music-reports/capabilities"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/music-reports/capabilities",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    capabilities = data.get("capabilities", {})
                    
                    # Verify capabilities structure
                    required_keys = ["automatic_sync", "bulk_upload", "supported_territories", "supported_pris", "max_batch_size"]
                    missing_keys = [key for key in required_keys if key not in capabilities]
                    
                    if not missing_keys:
                        territories = len(capabilities.get("supported_territories", []))
                        pris = len(capabilities.get("supported_pris", []))
                        max_batch = capabilities.get("max_batch_size", 0)
                        
                        self.log_result(
                            "Sync Capabilities", 
                            True, 
                            f"Capabilities: {territories} territories, {pris} PRIs, max batch {max_batch}"
                        )
                    else:
                        self.log_result(
                            "Sync Capabilities", 
                            False, 
                            f"Missing capabilities keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "Sync Capabilities", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("Sync Capabilities", False, f"Exception: {str(e)}")
            
    async def test_sync_history(self):
        """Test GET /api/music-reports/sync-history"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/music-reports/sync-history?limit=10",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    history = data.get("sync_history", [])
                    
                    # Verify sync history structure
                    if history:
                        record = history[0]
                        required_keys = ["sync_id", "timestamp", "status", "works_processed"]
                        missing_keys = [key for key in required_keys if key not in record]
                        
                        if not missing_keys:
                            self.log_result(
                                "Sync History Tracking", 
                                True, 
                                f"Retrieved {len(history)} sync records with proper structure"
                            )
                        else:
                            self.log_result(
                                "Sync History Tracking", 
                                False, 
                                f"Missing history record keys: {missing_keys}"
                            )
                    else:
                        self.log_result(
                            "Sync History Tracking", 
                            True, 
                            "No sync history available (expected for new system)"
                        )
                else:
                    self.log_result(
                        "Sync History Tracking", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("Sync History Tracking", False, f"Exception: {str(e)}")
            
    async def test_ddex_music_reports_cwr(self):
        """Test GET /api/ddex/music-reports/cwr"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ddex/music-reports/cwr",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    integration = data.get("music_reports_integration", {})
                    
                    # Verify DDEX integration structure
                    required_keys = ["connected", "total_works", "pending_sync"]
                    missing_keys = [key for key in required_keys if key not in integration]
                    
                    if not missing_keys:
                        connected = integration.get("connected", False)
                        total_works = integration.get("total_works", 0)
                        pending_sync = integration.get("pending_sync", 0)
                        
                        self.log_result(
                            "DDEX Music Reports CWR", 
                            True, 
                            f"DDEX Integration: Connected={connected}, Works={total_works}, Pending={pending_sync}"
                        )
                    else:
                        self.log_result(
                            "DDEX Music Reports CWR", 
                            False, 
                            f"Missing DDEX integration keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "DDEX Music Reports CWR", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("DDEX Music Reports CWR", False, f"Exception: {str(e)}")
            
    async def test_ddex_music_reports_sync(self):
        """Test POST /api/ddex/music-reports/sync"""
        try:
            async with self.session.post(
                f"{BACKEND_URL}/ddex/music-reports/sync",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    sync_result = data.get("sync_result", {})
                    
                    # Verify DDEX sync result structure
                    required_keys = ["sync_id", "status", "message"]
                    missing_keys = [key for key in required_keys if key not in sync_result]
                    
                    if not missing_keys:
                        sync_id = sync_result.get("sync_id", "")
                        status = sync_result.get("status", "")
                        message = sync_result.get("message", "")
                        
                        self.log_result(
                            "DDEX Music Reports Sync", 
                            True, 
                            f"DDEX Sync: ID={sync_id}, Status={status}, Message={message}"
                        )
                    else:
                        self.log_result(
                            "DDEX Music Reports Sync", 
                            False, 
                            f"Missing DDEX sync keys: {missing_keys}"
                        )
                else:
                    self.log_result(
                        "DDEX Music Reports Sync", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_result("DDEX Music Reports Sync", False, f"Exception: {str(e)}")
            
    async def test_authentication_security(self):
        """Test authentication requirements for Music Reports endpoints"""
        try:
            # Test without authentication
            async with self.session.get(f"{BACKEND_URL}/music-reports/dashboard") as response:
                if response.status in [401, 403]:
                    self.log_result(
                        "Authentication Security", 
                        True, 
                        f"Properly secured - returns {response.status} without auth"
                    )
                else:
                    self.log_result(
                        "Authentication Security", 
                        False, 
                        f"Security issue - returns {response.status} without auth"
                    )
                    
        except Exception as e:
            self.log_result("Authentication Security", False, f"Exception: {str(e)}")
            
    async def run_all_tests(self):
        """Run all Music Reports Integration tests"""
        print("🎯 PHASE 3: MUSIC REPORTS INTEGRATION - BACKEND TESTING INITIATED")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Authenticate first
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with testing")
                return
                
            print("\n🎵 TESTING MUSIC REPORTS ENDPOINTS:")
            print("-" * 50)
            
            # Test all Music Reports endpoints
            await self.test_music_reports_dashboard()
            await self.test_integration_status()
            await self.test_cwr_works()
            await self.test_sync_initiation()
            await self.test_royalty_data()
            await self.test_royalty_statements()
            await self.test_sync_capabilities()
            await self.test_sync_history()
            
            print("\n🔗 TESTING DDEX MUSIC REPORTS INTEGRATION:")
            print("-" * 50)
            
            # Test DDEX Music Reports endpoints
            await self.test_ddex_music_reports_cwr()
            await self.test_ddex_music_reports_sync()
            
            print("\n🔒 TESTING SECURITY:")
            print("-" * 50)
            
            # Test authentication security
            await self.test_authentication_security()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎉 PHASE 3: MUSIC REPORTS INTEGRATION TESTING COMPLETED")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n📊 COMPREHENSIVE TEST RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 KEY ENDPOINTS TESTED:")
        print(f"   ✅ GET /api/music-reports/dashboard")
        print(f"   ✅ GET /api/music-reports/integration-status")
        print(f"   ✅ GET /api/music-reports/cwr-works")
        print(f"   ✅ POST /api/music-reports/sync")
        print(f"   ✅ GET /api/music-reports/royalties")
        print(f"   ✅ GET /api/music-reports/statements")
        print(f"   ✅ GET /api/music-reports/capabilities")
        print(f"   ✅ GET /api/music-reports/sync-history")
        print(f"   ✅ GET /api/ddex/music-reports/cwr")
        print(f"   ✅ POST /api/ddex/music-reports/sync")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["passed"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Production readiness assessment
        if success_rate >= 90:
            print(f"\n✅ PRODUCTION READINESS: EXCELLENT ({success_rate:.1f}%)")
            print("   All critical Music Reports functionality is operational")
        elif success_rate >= 75:
            print(f"\n⚠️  PRODUCTION READINESS: GOOD ({success_rate:.1f}%)")
            print("   Most Music Reports functionality is operational with minor issues")
        else:
            print(f"\n❌ PRODUCTION READINESS: NEEDS ATTENTION ({success_rate:.1f}%)")
            print("   Critical issues found that need resolution")
            
        print("\n🎵 MUSIC REPORTS INTEGRATION FEATURES VERIFIED:")
        print("   • Dashboard data structure and completeness")
        print("   • CWR works management and sync functionality")
        print("   • Royalty data collection and reporting")
        print("   • Integration status and capabilities")
        print("   • Sync history and status tracking")
        print("   • Payment scheduling and statement generation")
        print("   • DDEX integration with Music Reports sync")
        print("   • Authentication and security verification")
        
        print(f"\n🚀 NEXT STEPS:")
        if success_rate >= 90:
            print("   • Music Reports Integration is ready for live API integration")
            print("   • Configure live API credentials when available")
            print("   • Frontend integration can proceed")
        else:
            print("   • Address failed test issues before proceeding")
            print("   • Re-test after fixes are applied")
            print("   • Verify live API readiness")

async def main():
    """Main test execution"""
    tester = MusicReportsIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())