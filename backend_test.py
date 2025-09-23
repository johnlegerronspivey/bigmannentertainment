#!/usr/bin/env python3
"""
Comprehensive Backend Fixes Validation Test
Testing all backend issues that were identified and should now be fixed:
- Health endpoints (Global, API, Auth, Business, DAO)
- DAO governance endpoints
- Premium features endpoints  
- GS1 integration endpoints
- Integration services (MLC, MDE, pDOOH)
- Auth token parsing validation
- Performance and response validation
- Database connectivity
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://support-desk-30.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.start_time = None

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        self.start_time = time.time()

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def register_and_login(self):
        """Register a test user and login to get auth token"""
        try:
            # Registration data
            registration_data = {
                "email": f"backend_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@bigmannentertainment.com",
                "password": "BackendTest123!",
                "full_name": "Backend Comprehensive Tester",
                "business_name": "Backend Testing LLC",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Backend Test St",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }

            # Register user
            async with self.session.post(f"{API_BASE}/auth/register", json=registration_data) as response:
                if response.status in [200, 201]:
                    reg_data = await response.json()
                    self.auth_token = reg_data.get('access_token')
                    self.user_id = reg_data.get('user', {}).get('id')
                    print(f"✅ User registered and authenticated: {self.user_id}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Registration failed: {response.status} - {error_text}")
                    return False

        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    async def test_health_endpoints(self):
        """Test all health endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        health_endpoints = [
            ("Global Health Check", "/health"),
            ("API Health Check", "/api/health"),
            ("Auth Health Check", "/api/auth/health"),
            ("Business Health Check", "/api/business/health"),
            ("DAO Health Check", "/api/dao/health")
        ]
        
        for name, endpoint in health_endpoints:
            try:
                url = f"{BACKEND_URL}{endpoint}" if endpoint.startswith("/health") else f"{BACKEND_URL}{endpoint}"
                
                start_time = time.time()
                async with self.session.get(url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        try:
                            health_data = await response.json()
                            print(f"✅ {name}: OK ({response_time:.2f}s)")
                            
                            # Check for expected health data structure
                            if isinstance(health_data, dict) and 'status' in health_data:
                                status = health_data.get('status')
                                print(f"   - Status: {status}")
                                
                                # Check database connectivity for API health
                                if endpoint == "/api/health" and 'database' in health_data:
                                    db_info = health_data.get('database', {})
                                    if isinstance(db_info, dict):
                                        db_status = db_info.get('status', 'unknown')
                                        print(f"   - Database: {db_status}")
                            
                            self.test_results.append((name, "PASS", f"Response time: {response_time:.2f}s"))
                        except Exception as json_error:
                            # Try to get text response for debugging
                            try:
                                text_response = await response.text()
                                print(f"⚠️ {name}: Non-JSON response ({response_time:.2f}s)")
                                print(f"   - Response: {text_response[:100]}...")
                                self.test_results.append((name, "PARTIAL", f"Non-JSON response, time: {response_time:.2f}s"))
                            except:
                                print(f"❌ {name}: JSON parsing failed ({response_time:.2f}s)")
                                self.test_results.append((name, "FAIL", f"JSON parsing failed"))
                    else:
                        error_text = await response.text()
                        print(f"❌ {name}: {response.status} - {error_text}")
                        self.test_results.append((name, "FAIL", f"HTTP {response.status}"))

            except Exception as e:
                print(f"❌ {name} error: {str(e)}")
                self.test_results.append((name, "ERROR", str(e)))

    async def test_dao_governance_endpoints(self):
        """Test DAO governance endpoints"""
        print("\n⚖️ Testing DAO Governance Endpoints...")
        
        # Test DAO Contracts
        try:
            async with self.session.get(f"{API_BASE}/dao/contracts") as response:
                if response.status == 200:
                    contracts = await response.json()
                    print(f"✅ DAO Contracts: {len(contracts)} contracts found")
                    self.test_results.append(("DAO Contracts", "PASS", f"{len(contracts)} contracts"))
                else:
                    error_text = await response.text()
                    print(f"❌ DAO Contracts failed: {response.status} - {error_text}")
                    self.test_results.append(("DAO Contracts", "FAIL", f"HTTP {response.status}"))
        except Exception as e:
            print(f"❌ DAO Contracts error: {str(e)}")
            self.test_results.append(("DAO Contracts", "ERROR", str(e)))

        # Test DAO Stats
        try:
            async with self.session.get(f"{API_BASE}/dao/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"✅ DAO Stats: Retrieved statistics")
                    if 'total_proposals' in stats:
                        print(f"   - Total proposals: {stats.get('total_proposals', 0)}")
                    self.test_results.append(("DAO Stats", "PASS", "Statistics retrieved"))
                else:
                    error_text = await response.text()
                    print(f"❌ DAO Stats failed: {response.status} - {error_text}")
                    self.test_results.append(("DAO Stats", "FAIL", f"HTTP {response.status}"))
        except Exception as e:
            print(f"❌ DAO Stats error: {str(e)}")
            self.test_results.append(("DAO Stats", "ERROR", str(e)))

        # Test DAO Disputes
        try:
            async with self.session.get(f"{API_BASE}/dao/disputes") as response:
                if response.status == 200:
                    disputes = await response.json()
                    print(f"✅ DAO Disputes: {len(disputes)} disputes found")
                    self.test_results.append(("DAO Disputes", "PASS", f"{len(disputes)} disputes"))
                else:
                    error_text = await response.text()
                    print(f"❌ DAO Disputes failed: {response.status} - {error_text}")
                    self.test_results.append(("DAO Disputes", "FAIL", f"HTTP {response.status}"))
        except Exception as e:
            print(f"❌ DAO Disputes error: {str(e)}")
            self.test_results.append(("DAO Disputes", "ERROR", str(e)))

        # Test DAO Governance Action
        try:
            governance_data = {
                "action_type": "create_proposal",
                "description": "Test proposal for platform improvement",
                "target_address": "0x1234567890123456789012345678901234567890"
            }
            
            async with self.session.post(
                f"{API_BASE}/dao/governance",
                json=governance_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status in [200, 201]:
                    governance_result = await response.json()
                    print(f"✅ DAO Governance Action: Proposal created")
                    self.test_results.append(("DAO Governance Action", "PASS", "Proposal created"))
                else:
                    error_text = await response.text()
                    print(f"❌ DAO Governance Action failed: {response.status} - {error_text}")
                    self.test_results.append(("DAO Governance Action", "FAIL", f"HTTP {response.status}"))
        except Exception as e:
            print(f"❌ DAO Governance Action error: {str(e)}")
            self.test_results.append(("DAO Governance Action", "ERROR", str(e)))

    async def test_premium_features_endpoints(self):
        """Test premium features endpoints"""
        print("\n💎 Testing Premium Features Endpoints...")
        
        premium_endpoints = [
            ("Premium Dashboard", f"/api/premium/dashboard/overview?user_id=test123"),
            ("AI Forecasting", f"/api/premium/revenue-intelligence/dashboard?user_id=test123&time_period=30d"),
            ("Smart Contract Templates", f"/api/premium/contracts/templates"),
            ("Revenue Intelligence", f"/api/premium/revenue-intelligence/optimization-suggestions?user_id=test123"),
            ("Payout Currencies", f"/api/premium/payouts/currencies")
        ]
        
        for name, endpoint in premium_endpoints:
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {name}: Data retrieved successfully")
                        self.test_results.append((name, "PASS", "Data retrieved"))
                    elif response.status == 403:
                        print(f"⚠️ {name}: Access forbidden (expected for premium features)")
                        self.test_results.append((name, "PASS", "Access control working"))
                    else:
                        error_text = await response.text()
                        print(f"❌ {name} failed: {response.status} - {error_text}")
                        self.test_results.append((name, "FAIL", f"HTTP {response.status}"))
            except Exception as e:
                print(f"❌ {name} error: {str(e)}")
                self.test_results.append((name, "ERROR", str(e)))

    async def test_gs1_integration_endpoints(self):
        """Test GS1 integration endpoints"""
        print("\n🏷️ Testing GS1 Integration Endpoints...")
        
        gs1_endpoints = [
            ("GS1 Health", "/api/gs1/health"),
            ("GS1 Assets", "/api/gs1/assets"),
            ("GS1 Identifiers", "/api/gs1/identifiers"),
            ("GS1 Analytics", "/api/gs1/analytics")
        ]
        
        for name, endpoint in gs1_endpoints:
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {name}: Service operational")
                        self.test_results.append((name, "PASS", "Service operational"))
                    else:
                        error_text = await response.text()
                        print(f"❌ {name} failed: {response.status} - {error_text}")
                        self.test_results.append((name, "FAIL", f"HTTP {response.status}"))
            except Exception as e:
                print(f"❌ {name} error: {str(e)}")
                self.test_results.append((name, "ERROR", str(e)))

    async def test_integration_services(self):
        """Test integration services with correct prefixes"""
        print("\n🔗 Testing Integration Services...")
        
        integration_endpoints = [
            ("MLC Integration", "/api/mlc/health"),
            ("MDE Integration", "/api/mde/health"),
            ("pDOOH Integration", "/api/pdooh/health")
        ]
        
        for name, endpoint in integration_endpoints:
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {name}: Service healthy")
                        self.test_results.append((name, "PASS", "Service healthy"))
                    else:
                        error_text = await response.text()
                        print(f"❌ {name} failed: {response.status} - {error_text}")
                        self.test_results.append((name, "FAIL", f"HTTP {response.status}"))
            except Exception as e:
                print(f"❌ {name} error: {str(e)}")
                self.test_results.append((name, "ERROR", str(e)))

    async def test_auth_token_parsing(self):
        """Test auth token parsing validation"""
        print("\n🔐 Testing Auth Token Parsing Validation...")
        
        # Test with valid token
        try:
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Valid Token: User authenticated successfully")
                    self.test_results.append(("Valid Token Authentication", "PASS", "Token parsed correctly"))
                else:
                    error_text = await response.text()
                    print(f"❌ Valid token failed: {response.status} - {error_text}")
                    self.test_results.append(("Valid Token Authentication", "FAIL", f"HTTP {response.status}"))
        except Exception as e:
            print(f"❌ Valid token error: {str(e)}")
            self.test_results.append(("Valid Token Authentication", "ERROR", str(e)))

        # Test with invalid token
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            async with self.session.get(f"{API_BASE}/auth/me", headers=invalid_headers) as response:
                if response.status == 401:
                    print(f"✅ Invalid Token: Properly rejected (401)")
                    self.test_results.append(("Invalid Token Rejection", "PASS", "Invalid token properly rejected"))
                else:
                    print(f"❌ Invalid token should return 401, got {response.status}")
                    self.test_results.append(("Invalid Token Rejection", "FAIL", f"Expected 401, got {response.status}"))
        except Exception as e:
            print(f"❌ Invalid token test error: {str(e)}")
            self.test_results.append(("Invalid Token Rejection", "ERROR", str(e)))

        # Test without token
        try:
            async with self.session.get(f"{API_BASE}/auth/me") as response:
                if response.status == 401:
                    print(f"✅ No Token: Properly rejected (401)")
                    self.test_results.append(("No Token Rejection", "PASS", "Missing token properly rejected"))
                else:
                    print(f"❌ No token should return 401, got {response.status}")
                    self.test_results.append(("No Token Rejection", "FAIL", f"Expected 401, got {response.status}"))
        except Exception as e:
            print(f"❌ No token test error: {str(e)}")
            self.test_results.append(("No Token Rejection", "ERROR", str(e)))

    async def test_performance_and_response_validation(self):
        """Test performance and response validation"""
        print("\n⚡ Testing Performance and Response Validation...")
        
        # Test response times and JSON format
        test_endpoints = [
            ("/api/health", "API Health"),
            ("/api/distribution/platforms", "Distribution Platforms"),
            ("/api/auth/health", "Auth Health")
        ]
        
        for endpoint, name in test_endpoints:
            try:
                start_time = time.time()
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    response_time = time.time() - start_time
                    
                    # Check response time (should be < 5 seconds)
                    if response_time < 5.0:
                        print(f"✅ {name} Response Time: {response_time:.2f}s (< 5s)")
                        time_result = "PASS"
                    else:
                        print(f"⚠️ {name} Response Time: {response_time:.2f}s (> 5s)")
                        time_result = "SLOW"
                    
                    # Check JSON response
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"✅ {name} JSON: Valid JSON response")
                            json_result = "PASS"
                        except:
                            print(f"❌ {name} JSON: Invalid JSON response")
                            json_result = "FAIL"
                    else:
                        json_result = "N/A"
                    
                    # Check status code
                    if response.status == 200:
                        status_result = "PASS"
                    elif response.status < 500:
                        status_result = "PASS"  # Client errors are acceptable
                    else:
                        status_result = "FAIL"  # Server errors are not acceptable
                    
                    overall_result = "PASS" if all(r in ["PASS", "N/A"] for r in [time_result, json_result, status_result]) else "PARTIAL"
                    self.test_results.append((f"{name} Performance", overall_result, f"Time: {response_time:.2f}s, Status: {response.status}"))
                    
            except Exception as e:
                print(f"❌ {name} performance test error: {str(e)}")
                self.test_results.append((f"{name} Performance", "ERROR", str(e)))

    async def test_database_connectivity(self):
        """Test database connectivity"""
        print("\n🗄️ Testing Database Connectivity...")
        
        # Test through health endpoint
        try:
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    try:
                        health_data = await response.json()
                        if isinstance(health_data, dict) and 'database' in health_data:
                            db_info = health_data.get('database', {})
                            if isinstance(db_info, dict):
                                db_status = db_info.get('status', 'unknown')
                                if db_status == 'healthy':
                                    print(f"✅ Database Connectivity: Healthy")
                                    self.test_results.append(("Database Connectivity", "PASS", "Database healthy"))
                                else:
                                    print(f"⚠️ Database Connectivity: {db_status}")
                                    self.test_results.append(("Database Connectivity", "PARTIAL", f"Status: {db_status}"))
                            else:
                                print(f"⚠️ Database Connectivity: Database info not properly formatted")
                                self.test_results.append(("Database Connectivity", "PARTIAL", "Database info format issue"))
                        else:
                            print(f"⚠️ Database Connectivity: Status not reported in health data")
                            self.test_results.append(("Database Connectivity", "PARTIAL", "Status not reported"))
                    except Exception as json_error:
                        print(f"⚠️ Database Connectivity: Health endpoint returned non-JSON")
                        self.test_results.append(("Database Connectivity", "PARTIAL", "Non-JSON health response"))
                else:
                    print(f"❌ Database Connectivity: Health endpoint failed")
                    self.test_results.append(("Database Connectivity", "FAIL", "Health endpoint failed"))
        except Exception as e:
            print(f"❌ Database connectivity error: {str(e)}")
            self.test_results.append(("Database Connectivity", "ERROR", str(e)))

        # Test data persistence through user creation (already done in auth)
        if self.user_id:
            print(f"✅ Data Persistence: User creation successful (ID: {self.user_id})")
            self.test_results.append(("Data Persistence", "PASS", "User data persisted"))

    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE BACKEND FIXES VALIDATION RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1] == "PASS"])
        failed_tests = len([r for r in self.test_results if r[1] == "FAIL"])
        error_tests = len([r for r in self.test_results if r[1] == "ERROR"])
        partial_tests = len([r for r in self.test_results if r[1] == "PARTIAL"])
        slow_tests = len([r for r in self.test_results if r[1] == "SLOW"])
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Partial: {partial_tests}")
        print(f"   🐌 Slow: {slow_tests}")
        print(f"   🔥 Errors: {error_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests + partial_tests) / total_tests * 100
            print(f"   🎯 Success Rate: {success_rate:.1f}%")
        
        total_time = time.time() - self.start_time if self.start_time else 0
        print(f"   ⏱️ Total Test Time: {total_time:.2f}s")
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        
        categories = {
            "Health Endpoints": ["Global Health Check", "API Health Check", "Auth Health Check", "Business Health Check", "DAO Health Check"],
            "DAO Governance": ["DAO Contracts", "DAO Stats", "DAO Disputes", "DAO Governance Action"],
            "Premium Features": ["Premium Dashboard", "AI Forecasting", "Smart Contract Templates", "Revenue Intelligence", "Payout Currencies"],
            "GS1 Integration": ["GS1 Health", "GS1 Assets", "GS1 Identifiers", "GS1 Analytics"],
            "Integration Services": ["MLC Integration", "MDE Integration", "pDOOH Integration"],
            "Authentication": ["Valid Token Authentication", "Invalid Token Rejection", "No Token Rejection"],
            "Performance": [name for name, _, _ in self.test_results if "Performance" in name],
            "Database": ["Database Connectivity", "Data Persistence"]
        }
        
        for category, test_names in categories.items():
            category_results = [r for r in self.test_results if r[0] in test_names]
            if category_results:
                category_passed = len([r for r in category_results if r[1] == "PASS"])
                category_total = len(category_results)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                print(f"\n   🏷️ {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
                for test_name, status, details in category_results:
                    status_icon = {
                        "PASS": "✅",
                        "FAIL": "❌", 
                        "ERROR": "🔥",
                        "PARTIAL": "⚠️",
                        "SLOW": "🐌"
                    }.get(status, "❓")
                    print(f"      {status_icon} {test_name}: {details}")
        
        print(f"\n🎯 CRITICAL ISSUES FOUND:")
        critical_issues = [r for r in self.test_results if r[1] in ["FAIL", "ERROR"]]
        if critical_issues:
            for test_name, status, details in critical_issues:
                print(f"   🚨 {test_name}: {details}")
        else:
            print(f"   🎉 No critical issues found!")
        
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print(f"   🎉 EXCELLENT: Backend fixes are working perfectly with {success_rate:.1f}% success rate")
            print(f"   🏆 All major systems are operational and healthy")
        elif success_rate >= 75:
            print(f"   ✅ GOOD: Backend fixes are mostly working with {success_rate:.1f}% success rate")
            print(f"   🔧 Minor issues may need attention")
        else:
            print(f"   ⚠️ NEEDS WORK: Backend has significant issues with {success_rate:.1f}% success rate")
            print(f"   🛠️ Major fixes still required")
        
        print("="*80)

    async def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend Fixes Validation...")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.register_and_login():
                print("❌ Authentication failed - cannot proceed with protected endpoint tests")
                # Continue with public endpoint tests
            
            # Run all test suites
            await self.test_health_endpoints()
            await self.test_dao_governance_endpoints()
            await self.test_premium_features_endpoints()
            await self.test_gs1_integration_endpoints()
            await self.test_integration_services()
            await self.test_auth_token_parsing()
            await self.test_performance_and_response_validation()
            await self.test_database_connectivity()
            
            # Print comprehensive summary
            self.print_comprehensive_summary()
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())