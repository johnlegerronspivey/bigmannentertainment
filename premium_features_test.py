#!/usr/bin/env python3
"""
Premium Features Backend Testing Suite
Big Mann Entertainment Platform - Premium Features Testing

This script tests all Premium Features endpoints including:
- AI Royalty Forecasting
- Smart Contract Builder  
- Multi-Currency Payouts
- Revenue Intelligence
- Premium Dashboard

Author: Testing Agent
Date: 2025-01-08
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Test Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://label-network-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class PremiumFeaturesTestSuite:
    """Comprehensive test suite for Premium Features endpoints"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = "test_user_premium_123"
        self.test_asset_id = "asset_premium_456"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {'raw_response': response_text}
                
                return {
                    'status': response.status,
                    'data': response_data,
                    'headers': dict(response.headers)
                }
        except Exception as e:
            return {
                'status': 0,
                'data': {'error': str(e)},
                'headers': {}
            }
    
    # ===== AI ROYALTY FORECASTING TESTS =====
    
    async def test_ai_forecasting_generate(self):
        """Test AI royalty forecasting generation"""
        test_name = "AI Forecasting - Generate Forecast"
        
        # Test with asset_id
        forecast_request = {
            "asset_id": self.test_asset_id,
            "period": "monthly",
            "horizon_months": 12,
            "model_type": "ensemble",
            "include_scenarios": True,
            "confidence_intervals": True
        }
        
        response = await self.make_request(
            'POST', 
            f'/premium/forecasting/generate?user_id={self.test_user_id}',
            json=forecast_request
        )
        
        if response['status'] == 200:
            data = response['data']
            required_fields = ['asset_id', 'period', 'forecast_data', 'total_predicted_revenue', 'confidence_score']
            
            if all(field in data for field in required_fields):
                self.log_test_result(test_name, True, 
                    f"Forecast generated successfully. Revenue: ${data.get('total_predicted_revenue', 0):.2f}, "
                    f"Confidence: {data.get('confidence_score', 0):.2f}", data)
            else:
                missing = [f for f in required_fields if f not in data]
                self.log_test_result(test_name, False, f"Missing required fields: {missing}", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_ai_forecasting_without_asset(self):
        """Test AI forecasting without specific asset (portfolio forecast)"""
        test_name = "AI Forecasting - Portfolio Forecast"
        
        forecast_request = {
            "period": "quarterly",
            "horizon_months": 6,
            "model_type": "random_forest",
            "include_scenarios": False,
            "confidence_intervals": True
        }
        
        response = await self.make_request(
            'POST', 
            f'/premium/forecasting/generate?user_id={self.test_user_id}',
            json=forecast_request
        )
        
        if response['status'] == 200:
            data = response['data']
            if data.get('asset_id') is None and 'forecast_data' in data:
                self.log_test_result(test_name, True, 
                    f"Portfolio forecast generated. Total revenue: ${data.get('total_predicted_revenue', 0):.2f}", data)
            else:
                self.log_test_result(test_name, False, "Portfolio forecast structure incorrect", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_model_performance(self):
        """Test model performance metrics endpoint"""
        test_name = "AI Forecasting - Model Performance"
        
        response = await self.make_request(
            'GET', 
            f'/premium/forecasting/model-performance?user_id={self.test_user_id}&asset_id={self.test_asset_id}'
        )
        
        if response['status'] == 200:
            data = response['data']
            if 'model_performance' in data and 'ensemble_accuracy' in data:
                self.log_test_result(test_name, True, 
                    f"Model performance retrieved. Ensemble accuracy: {data.get('ensemble_accuracy', 0):.3f}", data)
            else:
                self.log_test_result(test_name, False, "Model performance data incomplete", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_scenario_analysis(self):
        """Test scenario analysis functionality"""
        test_name = "AI Forecasting - Scenario Analysis"
        
        base_request = {
            "asset_id": self.test_asset_id,
            "period": "monthly",
            "horizon_months": 6,
            "model_type": "ensemble"
        }
        
        scenarios = [
            {
                "scenario_type": "platform_expansion",
                "parameter_changes": {"engagement_multiplier": 1.25, "platform_bonus": 0.3},
                "description": "Expanding to 3 additional platforms"
            },
            {
                "scenario_type": "engagement_boost", 
                "parameter_changes": {"engagement_multiplier": 1.4, "viral_factor": 1.2},
                "description": "Viral content strategy"
            }
        ]
        
        response = await self.make_request(
            'POST',
            f'/premium/forecasting/scenario-analysis?user_id={self.test_user_id}',
            json={"base_request": base_request, "scenarios": scenarios}
        )
        
        if response['status'] == 200:
            data = response['data']
            if 'base_forecast' in data and 'scenarios' in data and len(data['scenarios']) == 2:
                self.log_test_result(test_name, True, 
                    f"Scenario analysis completed. {len(data['scenarios'])} scenarios analyzed", data)
            else:
                self.log_test_result(test_name, False, "Scenario analysis data incomplete", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    # ===== SMART CONTRACT BUILDER TESTS =====
    
    async def test_contract_templates(self):
        """Test smart contract templates retrieval"""
        test_name = "Smart Contracts - Get Templates"
        
        response = await self.make_request(
            'GET', 
            f'/premium/contracts/templates?user_id={self.test_user_id}'
        )
        
        if response['status'] == 200:
            data = response['data']
            if isinstance(data, list) and len(data) > 0:
                template_types = [t.get('contract_type') for t in data]
                self.log_test_result(test_name, True, 
                    f"Retrieved {len(data)} templates. Types: {', '.join(set(template_types))}", data)
            else:
                self.log_test_result(test_name, False, "No templates returned or invalid format", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_contract_templates_filtered(self):
        """Test filtered contract templates"""
        test_name = "Smart Contracts - Filtered Templates"
        
        response = await self.make_request(
            'GET', 
            f'/premium/contracts/templates?user_id={self.test_user_id}&contract_type=royalty_split'
        )
        
        if response['status'] == 200:
            data = response['data']
            if isinstance(data, list):
                royalty_templates = [t for t in data if t.get('contract_type') == 'royalty_split']
                self.log_test_result(test_name, True, 
                    f"Retrieved {len(royalty_templates)} royalty split templates", data)
            else:
                self.log_test_result(test_name, False, "Invalid template data format", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_create_contract_from_template(self):
        """Test creating contract from template"""
        test_name = "Smart Contracts - Create from Template"
        
        # First get available templates
        templates_response = await self.make_request(
            'GET', 
            f'/premium/contracts/templates?user_id={self.test_user_id}'
        )
        
        if templates_response['status'] != 200 or not templates_response['data']:
            self.log_test_result(test_name, False, "Could not retrieve templates for testing", None)
            return
        
        template_id = templates_response['data'][0]['id']
        
        contract_data = {
            "template_id": template_id,
            "name": "Test Royalty Contract",
            "description": "Test contract created from template",
            "customizations": {
                "split_percentages": {"artist": 0.6, "producer": 0.25, "platform": 0.15}
            }
        }
        
        response = await self.make_request(
            'POST',
            f'/premium/contracts/from-template?user_id={self.test_user_id}',
            json=contract_data
        )
        
        if response['status'] == 200:
            data = response['data']
            if 'id' in data and 'solidity_code' in data:
                # Store contract ID for later tests
                self.test_contract_id = data['id']
                self.log_test_result(test_name, True, 
                    f"Contract created successfully. ID: {data['id']}", data)
            else:
                self.log_test_result(test_name, False, "Contract creation response incomplete", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_create_custom_contract(self):
        """Test creating custom contract"""
        test_name = "Smart Contracts - Create Custom"
        
        components = [
            {
                "component_type": "trigger",
                "title": "Revenue Trigger",
                "description": "Triggers on revenue events",
                "parameters": {"trigger_type": "platform_event", "event_name": "revenue_received"},
                "position": {"x": 100, "y": 100}
            },
            {
                "component_type": "action", 
                "title": "Split Revenue",
                "description": "Split revenue among participants",
                "parameters": {"action_type": "transfer_funds", "split_logic": "percentage_based"},
                "position": {"x": 300, "y": 100}
            }
        ]
        
        contract_data = {
            "name": "Custom Revenue Splitter",
            "description": "Custom contract for revenue splitting",
            "contract_type": "revenue_sharing",
            "components": components
        }
        
        response = await self.make_request(
            'POST',
            f'/premium/contracts/custom?user_id={self.test_user_id}',
            json=contract_data
        )
        
        if response['status'] == 200:
            data = response['data']
            if 'id' in data and len(data.get('components', [])) == 2:
                self.log_test_result(test_name, True, 
                    f"Custom contract created. ID: {data['id']}, Components: {len(data['components'])}", data)
            else:
                self.log_test_result(test_name, False, "Custom contract creation incomplete", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_contract_simulation(self):
        """Test contract simulation"""
        test_name = "Smart Contracts - Simulation"
        
        # Use contract ID from previous test if available
        if not hasattr(self, 'test_contract_id'):
            self.log_test_result(test_name, False, "No contract ID available for simulation test", None)
            return
        
        simulation_request = {
            "contract_id": self.test_contract_id,
            "historical_data": {
                "avg_daily_events": 15,
                "avg_transaction_value": 50.0
            },
            "scenario_parameters": {
                "events_multiplier": 1.2
            },
            "simulation_period_days": 30
        }
        
        response = await self.make_request(
            'POST',
            f'/premium/contracts/{self.test_contract_id}/simulate?user_id={self.test_user_id}',
            json=simulation_request
        )
        
        if response['status'] == 200:
            data = response['data']
            required_fields = ['total_executions', 'successful_executions', 'gas_estimates', 'financial_projections']
            
            if all(field in data for field in required_fields):
                self.log_test_result(test_name, True, 
                    f"Simulation completed. Executions: {data['total_executions']}, "
                    f"Success rate: {data['successful_executions']/max(data['total_executions'], 1)*100:.1f}%", data)
            else:
                missing = [f for f in required_fields if f not in data]
                self.log_test_result(test_name, False, f"Simulation result missing fields: {missing}", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    # ===== MULTI-CURRENCY PAYOUT TESTS =====
    
    async def test_supported_currencies(self):
        """Test supported currencies endpoint"""
        test_name = "Multi-Currency - Supported Currencies"
        
        response = await self.make_request(
            'GET', 
            f'/premium/payouts/currencies?user_id={self.test_user_id}'
        )
        
        if response['status'] == 200:
            data = response['data']
            if 'fiat_currencies' in data and 'cryptocurrencies' in data:
                fiat_count = len(data['fiat_currencies'])
                crypto_count = len(data['cryptocurrencies'])
                self.log_test_result(test_name, True, 
                    f"Retrieved currencies. Fiat: {fiat_count}, Crypto: {crypto_count}", data)
            else:
                self.log_test_result(test_name, False, "Currency data structure incomplete", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_payout_configuration(self):
        """Test payout preferences configuration"""
        test_name = "Multi-Currency - Configure Preferences"
        
        preferences = {
            "primary_currency": "USD",
            "payout_method": "bank_transfer",
            "minimum_payout": 100.0,
            "payout_frequency": "monthly",
            "crypto_wallets": {
                "BTC": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "ETH": "0x742d35Cc6634C0532925a3b8D4C9db96590b4c5d"
            },
            "auto_convert": True,
            "tax_withholding": 0.0
        }
        
        response = await self.make_request(
            'POST',
            f'/premium/payouts/configure?user_id={self.test_user_id}',
            json=preferences
        )
        
        if response['status'] == 200:
            data = response['data']
            if data.get('success') and 'configuration' in data:
                config = data['configuration']
                self.log_test_result(test_name, True, 
                    f"Preferences configured. Currency: {config.get('primary_currency')}, "
                    f"Method: {config.get('payout_method')}", data)
            else:
                self.log_test_result(test_name, False, "Configuration response incomplete", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_payout_estimation(self):
        """Test payout conversion estimation"""
        test_name = "Multi-Currency - Conversion Estimation"
        
        response = await self.make_request(
            'GET',
            f'/premium/payouts/estimate?amount=1000&from_currency=USD&to_currency=EUR&user_id={self.test_user_id}'
        )
        
        if response['status'] == 200:
            data = response['data']
            required_fields = ['converted_amount', 'conversion_rate', 'fees', 'net_amount']
            
            if all(field in data for field in required_fields):
                self.log_test_result(test_name, True, 
                    f"Conversion estimated. $1000 USD → €{data['converted_amount']:.2f} EUR, "
                    f"Net: €{data['net_amount']:.2f}", data)
            else:
                missing = [f for f in required_fields if f not in data]
                self.log_test_result(test_name, False, f"Estimation missing fields: {missing}", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    # ===== REVENUE INTELLIGENCE TESTS =====
    
    async def test_revenue_intelligence_dashboard(self):
        """Test revenue intelligence dashboard"""
        test_name = "Revenue Intelligence - Dashboard"
        
        response = await self.make_request(
            'GET',
            f'/premium/revenue-intelligence/dashboard?user_id={self.test_user_id}&time_period=30d'
        )
        
        if response['status'] == 200:
            data = response['data']
            required_sections = ['revenue_overview', 'platform_performance', 'roi_metrics', 'predictive_insights']
            
            if all(section in data for section in required_sections):
                revenue = data['revenue_overview'].get('total_revenue', 0)
                growth = data['revenue_overview'].get('revenue_growth', 0)
                self.log_test_result(test_name, True, 
                    f"Dashboard loaded. Revenue: ${revenue:,.2f}, Growth: {growth}%", data)
            else:
                missing = [s for s in required_sections if s not in data]
                self.log_test_result(test_name, False, f"Dashboard missing sections: {missing}", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    async def test_optimization_suggestions(self):
        """Test optimization suggestions"""
        test_name = "Revenue Intelligence - Optimization Suggestions"
        
        response = await self.make_request(
            'GET',
            f'/premium/revenue-intelligence/optimization-suggestions?user_id={self.test_user_id}&focus_area=platform'
        )
        
        if response['status'] == 200:
            data = response['data']
            if 'suggestions' in data and isinstance(data['suggestions'], list):
                suggestion_count = len(data['suggestions'])
                categories = [s.get('category') for s in data['suggestions']]
                self.log_test_result(test_name, True, 
                    f"Retrieved {suggestion_count} suggestions. Categories: {', '.join(set(categories))}", data)
            else:
                self.log_test_result(test_name, False, "Suggestions data structure invalid", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    # ===== PREMIUM DASHBOARD TESTS =====
    
    async def test_premium_dashboard_overview(self):
        """Test premium dashboard overview"""
        test_name = "Premium Dashboard - Overview"
        
        response = await self.make_request(
            'GET',
            f'/premium/dashboard/overview?user_id={self.test_user_id}'
        )
        
        if response['status'] == 200:
            data = response['data']
            required_sections = ['ai_forecasting', 'smart_contracts', 'revenue_intelligence', 'multi_currency_payouts']
            
            if all(section in data for section in required_sections):
                forecasting_status = data['ai_forecasting'].get('status')
                contracts_count = data['smart_contracts'].get('total_contracts', 0)
                self.log_test_result(test_name, True, 
                    f"Dashboard overview loaded. Forecasting: {forecasting_status}, "
                    f"Contracts: {contracts_count}", data)
            else:
                missing = [s for s in required_sections if s not in data]
                self.log_test_result(test_name, False, f"Overview missing sections: {missing}", data)
        else:
            self.log_test_result(test_name, False, 
                f"HTTP {response['status']}: {response['data'].get('detail', 'Unknown error')}", response['data'])
    
    # ===== MAIN TEST EXECUTION =====
    
    async def run_all_tests(self):
        """Run all premium features tests"""
        print("🎯 PREMIUM FEATURES COMPREHENSIVE BACKEND TESTING INITIATED")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        # AI Royalty Forecasting Tests
        print("\n📊 AI ROYALTY FORECASTING TESTS")
        print("-" * 40)
        await self.test_ai_forecasting_generate()
        await self.test_ai_forecasting_without_asset()
        await self.test_model_performance()
        await self.test_scenario_analysis()
        
        # Smart Contract Builder Tests
        print("\n📋 SMART CONTRACT BUILDER TESTS")
        print("-" * 40)
        await self.test_contract_templates()
        await self.test_contract_templates_filtered()
        await self.test_create_contract_from_template()
        await self.test_create_custom_contract()
        await self.test_contract_simulation()
        
        # Multi-Currency Payout Tests
        print("\n💰 MULTI-CURRENCY PAYOUT TESTS")
        print("-" * 40)
        await self.test_supported_currencies()
        await self.test_payout_configuration()
        await self.test_payout_estimation()
        
        # Revenue Intelligence Tests
        print("\n📈 REVENUE INTELLIGENCE TESTS")
        print("-" * 40)
        await self.test_revenue_intelligence_dashboard()
        await self.test_optimization_suggestions()
        
        # Premium Dashboard Tests
        print("\n🎛️ PREMIUM DASHBOARD TESTS")
        print("-" * 40)
        await self.test_premium_dashboard_overview()
        
        # Generate Summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎉 PREMIUM FEATURES TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Group results by category
        categories = {
            'AI Forecasting': [r for r in self.test_results if 'AI Forecasting' in r['test_name']],
            'Smart Contracts': [r for r in self.test_results if 'Smart Contracts' in r['test_name']],
            'Multi-Currency': [r for r in self.test_results if 'Multi-Currency' in r['test_name']],
            'Revenue Intelligence': [r for r in self.test_results if 'Revenue Intelligence' in r['test_name']],
            'Premium Dashboard': [r for r in self.test_results if 'Premium Dashboard' in r['test_name']]
        }
        
        print("\n📊 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                category_passed = sum(1 for r in results if r['success'])
                category_total = len(results)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                print(f"  {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print("\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"  - {result['test_name']}: {result['details']}")
        
        # Show successful tests summary
        passed_results = [r for r in self.test_results if r['success']]
        if passed_results:
            print("\n✅ SUCCESSFUL TESTS:")
            for result in passed_results:
                print(f"  - {result['test_name']}")
        
        print("\n🎯 PREMIUM FEATURES TESTING COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution function"""
    try:
        async with PremiumFeaturesTestSuite() as test_suite:
            await test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())