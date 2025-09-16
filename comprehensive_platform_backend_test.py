#!/usr/bin/env python3
"""
Comprehensive Platform Backend Testing
Big Mann Entertainment - Comprehensive Backend API Testing

This script tests all comprehensive platform backend endpoints including:
1. DAO Governance Blockchain Integration
2. AI-Powered Royalty Forecasting  
3. Dynamic Smart Contract Builder
4. All 9 Platform Modules Backend
5. MLC, MDE, and GS1 Integrations

Focus Areas:
- DAO governance endpoints with blockchain integration
- Premium features (AI forecasting, smart contracts)
- Comprehensive platform module integration
- Integration endpoints functionality
- Authentication and error handling
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import uuid

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://musicdao-platform.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensivePlatformTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.auth_token = None
        self.test_user_id = "test_user_comprehensive_platform"
        
    async def setup_session(self):
        """Setup HTTP session with proper headers"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'ComprehensivePlatformTester/1.0'
            }
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return success status and response data"""
        try:
            url = f"{API_BASE}{endpoint}"
            headers = {}
            
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
                
            if method.upper() == 'GET':
                async with self.session.get(url, params=params, headers=headers) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data, params=params, headers=headers) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            elif method.upper() == 'PUT':
                async with self.session.put(url, json=data, params=params, headers=headers) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
            elif method.upper() == 'DELETE':
                async with self.session.delete(url, params=params, headers=headers) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data, response.status
                    
        except Exception as e:
            return False, {'error': str(e)}, 500

    # ===== DAO GOVERNANCE BLOCKCHAIN INTEGRATION TESTS =====
    
    async def test_dao_governance_endpoints(self):
        """Test DAO Governance blockchain integration endpoints"""
        print("\n🔗 Testing DAO Governance Blockchain Integration...")
        
        # Test get DAO proposals
        success, data, status = await self.make_request(
            'GET', 
            '/platform/dao/proposals',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "DAO Proposals Retrieval", 
            success,
            f"Status: {status}, Proposals: {len(data.get('proposals', [])) if success else 'N/A'}"
        )
        
        # Test DAO metrics
        success, data, status = await self.make_request(
            'GET',
            '/platform/dao/metrics',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "DAO Metrics", 
            success,
            f"Status: {status}, Metrics available: {bool(data.get('metrics')) if success else False}"
        )
        
        # Test DAO member profile
        success, data, status = await self.make_request(
            'GET',
            '/platform/dao/member',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "DAO Member Profile", 
            success,
            f"Status: {status}, Member found: {bool(data.get('member')) if success else False}"
        )
        
        # Test DAO treasury information
        success, data, status = await self.make_request(
            'GET',
            '/platform/dao/treasury',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "DAO Treasury Info", 
            success,
            f"Status: {status}, Treasury value: ${data.get('treasury', {}).get('total_value_usd', 0) if success else 0}"
        )
        
        # Test DAO smart contracts
        success, data, status = await self.make_request(
            'GET',
            '/platform/dao/contracts',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "DAO Smart Contracts", 
            success,
            f"Status: {status}, Contracts: {len(data.get('contract_info', {}).get('contracts', [])) if success else 0}"
        )
        
        # Test blockchain integration status
        success, data, status = await self.make_request(
            'GET',
            '/platform/dao/blockchain/status'
        )
        self.log_result(
            "Blockchain Integration Status", 
            success,
            f"Status: {status}, Connected: {data.get('blockchain_connected', False) if success else False}"
        )
        
        # Test create DAO proposal
        proposal_data = {
            "title": "Test Proposal - Platform Enhancement",
            "description": "Test proposal for comprehensive platform testing",
            "proposal_type": "platform_upgrade",
            "proposer_address": "0x1234567890123456789012345678901234567890",
            "proposer_id": self.test_user_id,
            "voting_starts": datetime.now(timezone.utc).isoformat(),
            "voting_ends": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "metadata": {"test": True}
        }
        
        success, data, status = await self.make_request(
            'POST',
            '/platform/dao/proposals',
            data=proposal_data,
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Create DAO Proposal", 
            success,
            f"Status: {status}, Proposal created: {bool(data.get('proposal_id')) if success else False}"
        )

    # ===== AI-POWERED ROYALTY FORECASTING TESTS =====
    
    async def test_ai_royalty_forecasting(self):
        """Test AI-Powered Royalty Forecasting endpoints"""
        print("\n🤖 Testing AI-Powered Royalty Forecasting...")
        
        # Test generate forecast
        forecast_request = {
            "period": "monthly",
            "horizon_months": 6,
            "model_type": "ensemble",
            "include_scenarios": False,
            "confidence_intervals": False
        }
        
        success, data, status = await self.make_request(
            'POST',
            '/premium/forecasting/generate',
            data=forecast_request,
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "AI Royalty Forecast Generation", 
            success,
            f"Status: {status}, Revenue predicted: ${data.get('total_predicted_revenue', 0) if success else 0}"
        )
        
        # Test model performance
        success, data, status = await self.make_request(
            'GET',
            '/premium/forecasting/model-performance',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "AI Model Performance", 
            success,
            f"Status: {status}, Accuracy: {data.get('ensemble_accuracy', 0) if success else 0}"
        )
        
        # Test scenario analysis
        scenario_data = {
            "period": "monthly",
            "horizon_months": 3,
            "model_type": "linear_regression"
        }
        
        scenarios = [
            {
                "scenario_type": "platform_expansion",
                "parameter_changes": {"engagement_multiplier": 1.25, "platform_bonus": 0.3},
                "description": "Expanding to 3 additional platforms"
            }
        ]
        
        success, data, status = await self.make_request(
            'POST',
            '/premium/forecasting/scenario-analysis',
            data={
                "base_request": scenario_data,
                "scenarios": scenarios
            },
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "AI Scenario Analysis", 
            success,
            f"Status: {status}, Scenarios: {len(data.get('scenarios', [])) if success else 0}"
        )

    # ===== DYNAMIC SMART CONTRACT BUILDER TESTS =====
    
    async def test_smart_contract_builder(self):
        """Test Dynamic Smart Contract Builder endpoints"""
        print("\n📜 Testing Dynamic Smart Contract Builder...")
        
        # Test get contract templates
        success, data, status = await self.make_request(
            'GET',
            '/premium/contracts/templates',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Smart Contract Templates", 
            success,
            f"Status: {status}, Templates: {len(data) if success and isinstance(data, list) else 0}"
        )
        
        # Test create contract from template
        if success and isinstance(data, list) and len(data) > 0:
            template_id = data[0].get('id')
            contract_data = {
                "template_id": template_id,
                "name": "Test Royalty Contract",
                "description": "Test contract for comprehensive platform testing",
                "customizations": {
                    "royalty_percentage": 15.0,
                    "payment_frequency": "monthly"
                }
            }
            
            success, data, status = await self.make_request(
                'POST',
                '/premium/contracts/from-template',
                data=contract_data,
                params={'user_id': self.test_user_id}
            )
            self.log_result(
                "Create Contract from Template", 
                success,
                f"Status: {status}, Contract ID: {data.get('id', 'N/A') if success else 'N/A'}"
            )
            
            # Test contract simulation if contract was created
            if success and data.get('id'):
                contract_id = data['id']
                simulation_request = {
                    "contract_id": contract_id,
                    "simulation_period_days": 30,
                    "historical_data": {
                        "avg_daily_events": 10,
                        "avg_transaction_value": 25.0
                    },
                    "scenario_parameters": {
                        "events_multiplier": 1.0
                    }
                }
                
                success, data, status = await self.make_request(
                    'POST',
                    f'/premium/contracts/{contract_id}/simulate',
                    data=simulation_request,
                    params={'user_id': self.test_user_id}
                )
                self.log_result(
                    "Smart Contract Simulation", 
                    success,
                    f"Status: {status}, Executions: {data.get('total_executions', 0) if success else 0}"
                )
        
        # Test get user contracts
        success, data, status = await self.make_request(
            'GET',
            f'/premium/contracts/user/{self.test_user_id}',
            params={'requesting_user_id': self.test_user_id}
        )
        self.log_result(
            "User Smart Contracts", 
            success,
            f"Status: {status}, Contracts: {len(data) if success and isinstance(data, list) else 0}"
        )

    # ===== COMPREHENSIVE PLATFORM MODULES TESTS =====
    
    async def test_platform_modules(self):
        """Test all 9 comprehensive platform modules"""
        print("\n🏗️ Testing Comprehensive Platform Modules...")
        
        # Test Global Header - Dashboard KPI
        success, data, status = await self.make_request(
            'GET',
            '/platform/dashboard/kpi',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Global Header - Dashboard KPI", 
            success,
            f"Status: {status}, KPI data: {bool(data.get('data')) if success else False}"
        )
        
        # Test Content Manager
        success, data, status = await self.make_request(
            'GET',
            '/platform/content/assets',
            params={'user_id': self.test_user_id, 'limit': 10}
        )
        self.log_result(
            "Content Manager - Assets", 
            success,
            f"Status: {status}, Assets: {len(data.get('assets', [])) if success else 0}"
        )
        
        # Test Distribution Tracker
        success, data, status = await self.make_request(
            'GET',
            '/platform/distribution/platforms'
        )
        self.log_result(
            "Distribution Tracker - Platforms", 
            success,
            f"Status: {status}, Platforms: {len(data.get('platforms', [])) if success else 0}"
        )
        
        # Test Analytics & Forecasting
        success, data, status = await self.make_request(
            'GET',
            '/platform/analytics/revenue',
            params={'user_id': self.test_user_id, 'time_frame': 'month'}
        )
        self.log_result(
            "Analytics & Forecasting - Revenue", 
            success,
            f"Status: {status}, Revenue data: {bool(data.get('revenue_data')) if success else False}"
        )
        
        # Test Compliance Center
        success, data, status = await self.make_request(
            'GET',
            '/platform/compliance/status',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Compliance Center - Status", 
            success,
            f"Status: {status}, Compliance checks: {len(data.get('compliance_checks', [])) if success else 0}"
        )
        
        # Test Sponsorship & Campaigns
        success, data, status = await self.make_request(
            'GET',
            '/platform/sponsorship/campaigns',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Sponsorship & Campaigns", 
            success,
            f"Status: {status}, Campaigns: {len(data.get('campaigns', [])) if success else 0}"
        )
        
        # Test Contributor Hub
        success, data, status = await self.make_request(
            'GET',
            '/platform/contributors/search',
            params={'user_id': self.test_user_id, 'limit': 5}
        )
        self.log_result(
            "Contributor Hub - Search", 
            success,
            f"Status: {status}, Contributors: {len(data.get('contributors', [])) if success else 0}"
        )
        
        # Test System Health & Logs
        success, data, status = await self.make_request(
            'GET',
            '/platform/system/health'
        )
        self.log_result(
            "System Health & Logs", 
            success,
            f"Status: {status}, System status: {data.get('status', 'unknown') if success else 'unknown'}"
        )
        
        # Test Platform Search
        success, data, status = await self.make_request(
            'GET',
            '/platform/search',
            params={'query': 'test', 'user_id': self.test_user_id}
        )
        self.log_result(
            "Platform Search", 
            success,
            f"Status: {status}, Results: {len(data.get('data', {}).get('results', [])) if success else 0}"
        )

    # ===== MLC INTEGRATION TESTS =====
    
    async def test_mlc_integration(self):
        """Test MLC (Mechanical Licensing Collective) integration"""
        print("\n🎵 Testing MLC Integration...")
        
        # Test get available DSPs
        success, data, status = await self.make_request(
            'GET',
            '/mlc/dsps',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "MLC - Available DSPs", 
            success,
            f"Status: {status}, DSPs: {data.get('total_dsps', 0) if success else 0}"
        )
        
        # Test get registered works
        success, data, status = await self.make_request(
            'GET',
            '/mlc/works',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "MLC - Registered Works", 
            success,
            f"Status: {status}, Works: {data.get('total_works', 0) if success else 0}"
        )
        
        # Test MLC analytics
        success, data, status = await self.make_request(
            'GET',
            '/mlc/analytics',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "MLC - Analytics", 
            success,
            f"Status: {status}, Analytics available: {bool(data.get('analytics')) if success else False}"
        )
        
        # Test compliance status
        success, data, status = await self.make_request(
            'GET',
            '/mlc/compliance/status',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "MLC - Compliance Status", 
            success,
            f"Status: {status}, Compliant: {data.get('overall_compliant', False) if success else False}"
        )
        
        # Test integration status
        success, data, status = await self.make_request(
            'GET',
            '/mlc/integration/status'
        )
        self.log_result(
            "MLC - Integration Status", 
            success,
            f"Status: {status}, Connected: {data.get('integration_status', {}).get('mlc_connected', False) if success else False}"
        )

    # ===== MDE INTEGRATION TESTS =====
    
    async def test_mde_integration(self):
        """Test MDE (Music Data Exchange) integration"""
        print("\n📊 Testing MDE Integration...")
        
        # Test supported standards
        success, data, status = await self.make_request(
            'GET',
            '/mde/standards',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "MDE - Supported Standards", 
            success,
            f"Status: {status}, Standards: {data.get('total_standards', 0) if success else 0}"
        )
        
        # Test metadata entries
        success, data, status = await self.make_request(
            'GET',
            '/mde/metadata',
            params={'user_id': self.test_user_id, 'limit': 10}
        )
        self.log_result(
            "MDE - Metadata Entries", 
            success,
            f"Status: {status}, Entries: {data.get('total_count', 0) if success else 0}"
        )
        
        # Test validations
        success, data, status = await self.make_request(
            'GET',
            '/mde/validations',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "MDE - Validations", 
            success,
            f"Status: {status}, Validations: {data.get('total_validations', 0) if success else 0}"
        )
        
        # Test MDE analytics
        success, data, status = await self.make_request(
            'GET',
            '/mde/analytics',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "MDE - Analytics", 
            success,
            f"Status: {status}, Analytics available: {bool(data.get('analytics')) if success else False}"
        )
        
        # Test integration status
        success, data, status = await self.make_request(
            'GET',
            '/mde/integration/status'
        )
        self.log_result(
            "MDE - Integration Status", 
            success,
            f"Status: {status}, Connected: {data.get('integration_status', {}).get('mde_connected', False) if success else False}"
        )

    # ===== GS1 INTEGRATION TESTS =====
    
    async def test_gs1_integration(self):
        """Test GS1 Asset Registry integration"""
        print("\n🏷️ Testing GS1 Integration...")
        
        # Test health check
        success, data, status = await self.make_request(
            'GET',
            '/gs1/health'
        )
        self.log_result(
            "GS1 - Health Check", 
            success,
            f"Status: {status}, Service: {data.get('status', 'unknown') if success else 'unknown'}"
        )
        
        # Test business info
        success, data, status = await self.make_request(
            'GET',
            '/gs1/business-info'
        )
        self.log_result(
            "GS1 - Business Info", 
            success,
            f"Status: {status}, Company: {data.get('business_info', {}).get('company_name', 'N/A') if success else 'N/A'}"
        )
        
        # Test products
        success, data, status = await self.make_request(
            'GET',
            '/gs1/products',
            params={'page': 1, 'page_size': 10}
        )
        self.log_result(
            "GS1 - Products", 
            success,
            f"Status: {status}, Products: {len(data.get('products', [])) if success else 0}"
        )
        
        # Test analytics
        success, data, status = await self.make_request(
            'GET',
            '/gs1/analytics'
        )
        self.log_result(
            "GS1 - Analytics", 
            success,
            f"Status: {status}, Assets: {data.get('total_assets', 0) if success else 0}"
        )
        
        # Test standards compliance
        success, data, status = await self.make_request(
            'GET',
            '/gs1/standards/compliance'
        )
        self.log_result(
            "GS1 - Standards Compliance", 
            success,
            f"Status: {status}, Standards: {len(data.get('gs1_standards', {})) if success else 0}"
        )

    # ===== PREMIUM FEATURES OVERVIEW TESTS =====
    
    async def test_premium_features_overview(self):
        """Test premium features dashboard overview"""
        print("\n💎 Testing Premium Features Overview...")
        
        # Test premium dashboard overview
        success, data, status = await self.make_request(
            'GET',
            '/premium/dashboard/overview',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Premium Dashboard Overview", 
            success,
            f"Status: {status}, Features active: {bool(data.get('ai_forecasting', {}).get('status') == 'active') if success else False}"
        )
        
        # Test revenue intelligence dashboard
        success, data, status = await self.make_request(
            'GET',
            '/premium/revenue-intelligence/dashboard',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Revenue Intelligence Dashboard", 
            success,
            f"Status: {status}, Revenue: ${data.get('revenue_overview', {}).get('total_revenue', 0) if success else 0}"
        )
        
        # Test optimization suggestions
        success, data, status = await self.make_request(
            'GET',
            '/premium/revenue-intelligence/optimization-suggestions',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Optimization Suggestions", 
            success,
            f"Status: {status}, Suggestions: {len(data.get('suggestions', [])) if success else 0}"
        )
        
        # Test supported currencies
        success, data, status = await self.make_request(
            'GET',
            '/premium/payouts/currencies',
            params={'user_id': self.test_user_id}
        )
        self.log_result(
            "Multi-Currency Payouts", 
            success,
            f"Status: {status}, Currencies: {len(data.get('fiat_currencies', [])) + len(data.get('cryptocurrencies', [])) if success else 0}"
        )

    # ===== MAIN TEST EXECUTION =====
    
    async def run_all_tests(self):
        """Run all comprehensive platform tests"""
        print("🎯 COMPREHENSIVE PLATFORM BACKEND TESTING INITIATED")
        print("=" * 80)
        print("Testing Big Mann Entertainment Comprehensive Platform Backend")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Run all test suites
            await self.test_dao_governance_endpoints()
            await self.test_ai_royalty_forecasting()
            await self.test_smart_contract_builder()
            await self.test_platform_modules()
            await self.test_mlc_integration()
            await self.test_mde_integration()
            await self.test_gs1_integration()
            await self.test_premium_features_overview()
            
        finally:
            await self.cleanup_session()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE PLATFORM BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        # Group results by category
        categories = {
            'DAO Governance': [r for r in self.test_results if 'DAO' in r['test']],
            'AI Forecasting': [r for r in self.test_results if 'AI' in r['test']],
            'Smart Contracts': [r for r in self.test_results if 'Contract' in r['test']],
            'Platform Modules': [r for r in self.test_results if any(x in r['test'] for x in ['Global', 'Content', 'Distribution', 'Analytics', 'Compliance', 'Sponsorship', 'Contributor', 'System', 'Platform'])],
            'MLC Integration': [r for r in self.test_results if 'MLC' in r['test']],
            'MDE Integration': [r for r in self.test_results if 'MDE' in r['test']],
            'GS1 Integration': [r for r in self.test_results if 'GS1' in r['test']],
            'Premium Features': [r for r in self.test_results if 'Premium' in r['test'] or 'Revenue Intelligence' in r['test'] or 'Multi-Currency' in r['test']]
        }
        
        print("\n📊 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                category_passed = len([r for r in results if r['success']])
                category_total = len(results)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                status = "✅" if category_rate == 100 else "⚠️" if category_rate >= 50 else "❌"
                print(f"{status} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print(f"\n❌ FAILED TESTS ({len(failed_results)}):")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
        
        # Show critical insights
        print(f"\n🔍 CRITICAL INSIGHTS:")
        
        # DAO Governance Analysis
        dao_tests = [r for r in self.test_results if 'DAO' in r['test']]
        dao_success_rate = (len([r for r in dao_tests if r['success']]) / len(dao_tests) * 100) if dao_tests else 0
        if dao_success_rate >= 80:
            print("   ✅ DAO Governance blockchain integration is functional")
        else:
            print("   ❌ DAO Governance blockchain integration needs attention")
        
        # AI Forecasting Analysis
        ai_tests = [r for r in self.test_results if 'AI' in r['test']]
        ai_success_rate = (len([r for r in ai_tests if r['success']]) / len(ai_tests) * 100) if ai_tests else 0
        if ai_success_rate >= 80:
            print("   ✅ AI-Powered Royalty Forecasting is operational")
        else:
            print("   ❌ AI-Powered Royalty Forecasting needs fixes")
        
        # Smart Contract Analysis
        contract_tests = [r for r in self.test_results if 'Contract' in r['test']]
        contract_success_rate = (len([r for r in contract_tests if r['success']]) / len(contract_tests) * 100) if contract_tests else 0
        if contract_success_rate >= 80:
            print("   ✅ Dynamic Smart Contract Builder is working")
        else:
            print("   ❌ Dynamic Smart Contract Builder requires attention")
        
        # Integration Analysis
        integration_tests = [r for r in self.test_results if any(x in r['test'] for x in ['MLC', 'MDE', 'GS1'])]
        integration_success_rate = (len([r for r in integration_tests if r['success']]) / len(integration_tests) * 100) if integration_tests else 0
        if integration_success_rate >= 80:
            print("   ✅ MLC, MDE, and GS1 integrations are functional")
        else:
            print("   ❌ Integration endpoints need improvement")
        
        print("\n" + "=" * 80)
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Comprehensive platform backend is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: Most features working, minor issues to address")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Significant issues need attention before production")
        else:
            print("❌ CRITICAL: Major backend issues require immediate fixes")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = ComprehensivePlatformTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())