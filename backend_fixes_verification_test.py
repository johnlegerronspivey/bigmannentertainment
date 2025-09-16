#!/usr/bin/env python3
"""
Backend Fixes Verification Testing for Big Mann Entertainment Platform
Focus: Three Specific Backend Issues That Were Just Fixed

This test suite covers:
1. AI-Powered Royalty Forecasting ML Model Initialization
2. DAO Proposal Creation Validation  
3. Smart Contract Template Creation Validation

Test User ID: test_user_comprehensive_platform
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
import sys
import os

# Configuration
BACKEND_URL = "https://musicdao-platform.preview.emergentagent.com/api"
TEST_USER_ID = "test_user_comprehensive_platform"
TEST_USER_EMAIL = f"test_user_comprehensive_platform@bigmannentertainment.com"
TEST_PASSWORD = "SecureTestPass123!"

class BackendFixesVerificationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = TEST_USER_ID
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()

    def setup_authentication(self):
        """Setup authentication for testing"""
        print("🔐 Setting up authentication...")
        
        # Try to register user first (in case they don't exist)
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Test User Comprehensive Platform",
            "business_name": "Test Business",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
        try:
            response = self.session.post(f"{self.backend_url}/auth/register", json=register_data)
            if response.status_code == 201:
                print("✅ User registered successfully")
            elif response.status_code == 400 and "already exists" in response.text:
                print("ℹ️ User already exists, proceeding with login")
            else:
                print(f"⚠️ Registration response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"⚠️ Registration error: {e}")
        
        # Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{self.backend_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id", TEST_USER_ID)
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def test_ai_royalty_forecasting_ml_models(self):
        """Test AI-Powered Royalty Forecasting ML Model Initialization"""
        print("\n🤖 Testing AI-Powered Royalty Forecasting ML Model Initialization...")
        
        # Test 1: Generate Forecasting Endpoint
        try:
            forecast_data = {
                "asset_id": "test_asset_123",
                "historical_data": [
                    {"period": "2024-01", "revenue": 1000.0, "streams": 5000},
                    {"period": "2024-02", "revenue": 1200.0, "streams": 6000},
                    {"period": "2024-03", "revenue": 1100.0, "streams": 5500}
                ],
                "forecast_periods": 6,
                "confidence_level": 0.95
            }
            
            response = self.session.post(f"{self.backend_url}/premium/forecasting/generate?user_id={self.user_id}", json=forecast_data)
            
            if response.status_code == 200:
                data = response.json()
                if "forecast" in data and "model_metrics" in data:
                    self.log_result(
                        "AI Royalty Forecasting - Generate Forecast",
                        True,
                        f"Forecast generated successfully with {len(data.get('forecast', []))} periods"
                    )
                else:
                    self.log_result(
                        "AI Royalty Forecasting - Generate Forecast",
                        False,
                        "Response missing required fields",
                        f"Response: {data}"
                    )
            else:
                error_msg = response.text
                if "not fitted" in error_msg.lower():
                    self.log_result(
                        "AI Royalty Forecasting - Generate Forecast",
                        False,
                        "ML Model not fitted error still present",
                        f"{response.status_code}: {error_msg}"
                    )
                else:
                    self.log_result(
                        "AI Royalty Forecasting - Generate Forecast",
                        False,
                        f"Unexpected error: {response.status_code}",
                        error_msg
                    )
        except Exception as e:
            self.log_result(
                "AI Royalty Forecasting - Generate Forecast",
                False,
                "Exception occurred",
                str(e)
            )

        # Test 2: Model Performance Endpoint
        try:
            response = self.session.get(f"{self.backend_url}/premium/forecasting/model-performance")
            
            if response.status_code == 200:
                data = response.json()
                if "accuracy_metrics" in data and "model_status" in data:
                    self.log_result(
                        "AI Royalty Forecasting - Model Performance",
                        True,
                        f"Model performance retrieved - Status: {data.get('model_status')}"
                    )
                else:
                    self.log_result(
                        "AI Royalty Forecasting - Model Performance",
                        False,
                        "Response missing required fields",
                        f"Response: {data}"
                    )
            else:
                error_msg = response.text
                if "not fitted" in error_msg.lower():
                    self.log_result(
                        "AI Royalty Forecasting - Model Performance",
                        False,
                        "ML Model not fitted error still present",
                        f"{response.status_code}: {error_msg}"
                    )
                else:
                    self.log_result(
                        "AI Royalty Forecasting - Model Performance",
                        False,
                        f"Unexpected error: {response.status_code}",
                        error_msg
                    )
        except Exception as e:
            self.log_result(
                "AI Royalty Forecasting - Model Performance",
                False,
                "Exception occurred",
                str(e)
            )

        # Test 3: Scenario Analysis Endpoint
        try:
            scenario_data = {
                "user_id": self.user_id,
                "base_scenario": {
                    "monthly_streams": 10000,
                    "stream_rate": 0.004,
                    "growth_rate": 0.05
                },
                "scenarios": [
                    {
                        "name": "optimistic",
                        "monthly_streams": 15000,
                        "stream_rate": 0.005,
                        "growth_rate": 0.10
                    },
                    {
                        "name": "pessimistic", 
                        "monthly_streams": 5000,
                        "stream_rate": 0.003,
                        "growth_rate": 0.02
                    }
                ],
                "forecast_months": 12
            }
            
            response = self.session.post(f"{self.backend_url}/premium/forecasting/scenario-analysis", json=scenario_data)
            
            if response.status_code == 200:
                data = response.json()
                if "scenarios" in data and "comparison" in data:
                    self.log_result(
                        "AI Royalty Forecasting - Scenario Analysis",
                        True,
                        f"Scenario analysis completed with {len(data.get('scenarios', []))} scenarios"
                    )
                else:
                    self.log_result(
                        "AI Royalty Forecasting - Scenario Analysis",
                        False,
                        "Response missing required fields",
                        f"Response: {data}"
                    )
            else:
                error_msg = response.text
                if "not fitted" in error_msg.lower():
                    self.log_result(
                        "AI Royalty Forecasting - Scenario Analysis",
                        False,
                        "ML Model not fitted error still present",
                        f"{response.status_code}: {error_msg}"
                    )
                else:
                    self.log_result(
                        "AI Royalty Forecasting - Scenario Analysis",
                        False,
                        f"Unexpected error: {response.status_code}",
                        error_msg
                    )
        except Exception as e:
            self.log_result(
                "AI Royalty Forecasting - Scenario Analysis",
                False,
                "Exception occurred",
                str(e)
            )

    def test_dao_proposal_creation_validation(self):
        """Test DAO Proposal Creation Validation"""
        print("\n🏛️ Testing DAO Proposal Creation Validation...")
        
        # Test 1: Missing Required Fields Validation
        try:
            invalid_proposal = {
                "title": "Test Proposal",
                # Missing required fields: description, proposal_type, voting_period
            }
            
            response = self.session.post(f"{self.backend_url}/platform/dao/proposals", json=invalid_proposal)
            
            if response.status_code == 422 or response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                if "required" in str(error_data).lower() or "missing" in str(error_data).lower():
                    self.log_result(
                        "DAO Proposal - Missing Fields Validation",
                        True,
                        "Properly validates missing required fields",
                        f"Validation error: {error_data}"
                    )
                else:
                    self.log_result(
                        "DAO Proposal - Missing Fields Validation",
                        False,
                        "Validation error doesn't mention required fields",
                        f"Response: {error_data}"
                    )
            else:
                self.log_result(
                    "DAO Proposal - Missing Fields Validation",
                    False,
                    f"Expected validation error (400/422), got {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "DAO Proposal - Missing Fields Validation",
                False,
                "Exception occurred",
                str(e)
            )

        # Test 2: Valid Proposal Creation (Dictionary Input)
        try:
            valid_proposal_dict = {
                "title": "Test Governance Proposal",
                "description": "This is a test proposal for governance validation",
                "proposal_type": "governance",
                "voting_period": 7,
                "proposer_id": self.user_id,
                "required_quorum": 0.1,
                "options": ["approve", "reject"],
                "metadata": {
                    "category": "platform_improvement",
                    "priority": "medium"
                }
            }
            
            response = self.session.post(f"{self.backend_url}/platform/dao/proposals", json=valid_proposal_dict)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.log_result(
                        "DAO Proposal - Valid Dictionary Creation",
                        True,
                        f"Proposal created successfully with ID: {data.get('id')}"
                    )
                else:
                    self.log_result(
                        "DAO Proposal - Valid Dictionary Creation",
                        False,
                        "Response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "DAO Proposal - Valid Dictionary Creation",
                    False,
                    f"Expected success (200/201), got {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "DAO Proposal - Valid Dictionary Creation",
                False,
                "Exception occurred",
                str(e)
            )

        # Test 3: Valid Proposal Creation (GovernanceProposal Object Format)
        try:
            governance_proposal_object = {
                "title": "Advanced Governance Test Proposal",
                "description": "Testing GovernanceProposal object input format",
                "proposal_type": "treasury",
                "voting_period": 14,
                "proposer_id": self.user_id,
                "required_quorum": 0.15,
                "options": ["approve", "reject", "abstain"],
                "treasury_amount": 1000.0,
                "treasury_recipient": self.user_id,
                "execution_delay": 2,
                "metadata": {
                    "category": "treasury_management",
                    "priority": "high",
                    "budget_category": "development"
                }
            }
            
            response = self.session.post(f"{self.backend_url}/platform/dao/proposals", json=governance_proposal_object)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data and "treasury_amount" in data:
                    self.log_result(
                        "DAO Proposal - GovernanceProposal Object Creation",
                        True,
                        f"Treasury proposal created successfully with ID: {data.get('id')}"
                    )
                else:
                    self.log_result(
                        "DAO Proposal - GovernanceProposal Object Creation",
                        False,
                        "Response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "DAO Proposal - GovernanceProposal Object Creation",
                    False,
                    f"Expected success (200/201), got {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "DAO Proposal - GovernanceProposal Object Creation",
                False,
                "Exception occurred",
                str(e)
            )

    def test_smart_contract_template_creation_validation(self):
        """Test Smart Contract Template Creation Validation"""
        print("\n📜 Testing Smart Contract Template Creation Validation...")
        
        # Test 1: Missing Required Fields Validation
        try:
            invalid_contract = {
                "name": "Test Contract",
                # Missing required fields: template_id, blockchain_network, parameters
            }
            
            response = self.session.post(f"{self.backend_url}/premium/contracts/from-template", json=invalid_contract)
            
            if response.status_code == 422 or response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                if "required" in str(error_data).lower() or "missing" in str(error_data).lower():
                    self.log_result(
                        "Smart Contract Template - Missing Fields Validation",
                        True,
                        "Properly validates missing required fields",
                        f"Validation error: {error_data}"
                    )
                else:
                    self.log_result(
                        "Smart Contract Template - Missing Fields Validation",
                        False,
                        "Validation error doesn't mention required fields",
                        f"Response: {error_data}"
                    )
            else:
                self.log_result(
                    "Smart Contract Template - Missing Fields Validation",
                    False,
                    f"Expected validation error (400/422), got {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Smart Contract Template - Missing Fields Validation",
                False,
                "Exception occurred",
                str(e)
            )

        # Test 2: Valid Contract Template Creation
        try:
            valid_contract_template = {
                "name": "Royalty Distribution Contract",
                "template_id": "royalty_distribution_v1",
                "blockchain_network": "ethereum",
                "owner_id": self.user_id,
                "parameters": {
                    "royalty_percentage": 10.0,
                    "beneficiaries": [
                        {"address": "0x1234567890123456789012345678901234567890", "percentage": 60.0},
                        {"address": "0x0987654321098765432109876543210987654321", "percentage": 40.0}
                    ],
                    "minimum_payout": 0.01,
                    "auto_distribute": True
                },
                "customizations": {
                    "contract_name": "BME Royalty Distribution",
                    "symbol": "BMEROY",
                    "description": "Automated royalty distribution for Big Mann Entertainment"
                }
            }
            
            response = self.session.post(f"{self.backend_url}/premium/contracts/from-template", json=valid_contract_template)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                if "id" in data and "contract_address" in data:
                    self.log_result(
                        "Smart Contract Template - Valid Creation",
                        True,
                        f"Contract created successfully with ID: {data.get('id')}"
                    )
                else:
                    self.log_result(
                        "Smart Contract Template - Valid Creation",
                        False,
                        "Response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Smart Contract Template - Valid Creation",
                    False,
                    f"Expected success (200/201), got {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Smart Contract Template - Valid Creation",
                False,
                "Exception occurred",
                str(e)
            )

        # Test 3: Template Customization Functionality
        try:
            customized_contract = {
                "name": "Custom Revenue Sharing Contract",
                "template_id": "revenue_sharing_v2",
                "blockchain_network": "polygon",
                "owner_id": self.user_id,
                "parameters": {
                    "revenue_split": [
                        {"party": "artist", "percentage": 70.0},
                        {"party": "label", "percentage": 20.0},
                        {"party": "platform", "percentage": 10.0}
                    ],
                    "payment_frequency": "monthly",
                    "minimum_threshold": 100.0
                },
                "customizations": {
                    "contract_name": "BME Revenue Sharing v2",
                    "governance_enabled": True,
                    "upgrade_mechanism": "proxy",
                    "audit_trail": True,
                    "custom_functions": [
                        "emergency_pause",
                        "beneficiary_update",
                        "split_modification"
                    ]
                }
            }
            
            response = self.session.post(f"{self.backend_url}/premium/contracts/from-template", json=customized_contract)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                if "id" in data and "customizations" in data:
                    self.log_result(
                        "Smart Contract Template - Customization Functionality",
                        True,
                        f"Customized contract created with features: {list(data.get('customizations', {}).keys())}"
                    )
                else:
                    self.log_result(
                        "Smart Contract Template - Customization Functionality",
                        False,
                        "Response missing customization fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Smart Contract Template - Customization Functionality",
                    False,
                    f"Expected success (200/201), got {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Smart Contract Template - Customization Functionality",
                False,
                "Exception occurred",
                str(e)
            )

    def run_all_tests(self):
        """Run all backend fixes verification tests"""
        print("🎯 BACKEND FIXES VERIFICATION TESTING INITIATED")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test User ID: {self.user_id}")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run tests for the three specific fixes
        self.test_ai_royalty_forecasting_ml_models()
        self.test_dao_proposal_creation_validation()
        self.test_smart_contract_template_creation_validation()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 BACKEND FIXES VERIFICATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}")
                    if result["error"]:
                        print(f"    Error: {result['error']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        print("\n" + "=" * 60)
        print("🎯 BACKEND FIXES VERIFICATION TESTING COMPLETED")
        print("=" * 60)

if __name__ == "__main__":
    tester = BackendFixesVerificationTester()
    tester.run_all_tests()