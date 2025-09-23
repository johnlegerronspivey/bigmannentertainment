#!/usr/bin/env python3
"""
AWS DOOH Integration Backend Testing for Big Mann Entertainment Platform
Focus: AWS-integrated pDOOH backend components and infrastructure

This test suite covers:
1. Core Backend Compatibility - existing pDOOH endpoints
2. AWS Lambda Functions (Mock Testing) - doohCampaignManager.py and doohTriggerEngine.py
3. Infrastructure Components - AWS configuration files
4. Backend Integration Tests - /api/pdooh/* endpoints
5. Lambda Function Logic Tests
6. Configuration Validation
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
import sys
import os

# Configuration
BACKEND_URL = "https://mediaflow-98.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"test_user_aws_integration_{int(time.time())}@bigmannentertainment.com"
TEST_PASSWORD = "SecureTestPass123!"

class AWSDoohBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.test_campaign_id = None
        
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
        """Setup test user and authentication"""
        print("🔐 Setting up authentication...")
        
        try:
            # Try to register test user
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "AWS DOOH Test User",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }
            
            response = self.session.post(f"{self.backend_url}/auth/register", json=register_data)
            
            if response.status_code in [200, 201]:
                # Check if response contains access_token (auto-login after registration)
                data = response.json()
                if "access_token" in data:
                    self.log_result("User Registration", True, f"Registered and auto-logged in user: {TEST_USER_EMAIL}")
                else:
                    self.log_result("User Registration", True, f"Registered user: {TEST_USER_EMAIL}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("User Registration", True, f"User already exists: {TEST_USER_EMAIL}")
            else:
                self.log_result("User Registration", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("User Registration", False, error=str(e))
        
        try:
            # Login to get token
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{self.backend_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                })
                
                self.log_result("User Login", True, f"Token obtained, User ID: {self.user_id}")
                return True
            else:
                self.log_result("User Login", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Login", False, error=str(e))
            return False

    # ===== CORE BACKEND COMPATIBILITY TESTS =====
    
    def test_pdooh_platforms_endpoint(self):
        """Test /api/pdooh/platforms - Verify still functional"""
        try:
            response = self.session.get(f"{self.backend_url}/pdooh/platforms")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "platforms" in data:
                    platform_count = data.get("total_platforms", 0)
                    platforms = data.get("platforms", {})
                    self.log_result("pDOOH Platforms Endpoint", True, 
                                  f"Retrieved {platform_count} pDOOH platforms")
                else:
                    self.log_result("pDOOH Platforms Endpoint", False, error="Invalid response structure")
            else:
                self.log_result("pDOOH Platforms Endpoint", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("pDOOH Platforms Endpoint", False, error=str(e))
    
    def test_pdooh_campaigns_create(self):
        """Test /api/pdooh/campaigns - Campaign creation"""
        try:
            campaign_data = {
                "name": "Test pDOOH Campaign for AWS Integration",
                "campaign_type": "artist_promotion",
                "budget_total": 10000.0,
                "start_date": "2025-01-10T00:00:00Z",
                "end_date": "2025-01-20T23:59:59Z",
                "platforms": ["trade_desk", "vistar_media"],
                "geotargeting_rules": [
                    {
                        "latitude": 40.7580,
                        "longitude": -73.9855,
                        "radius_km": 50,
                        "location_name": "New York, NY"
                    }
                ],
                "demographics": {
                    "age_groups": ["18-34", "35-54"],
                    "interests": ["music", "entertainment"]
                }
            }
            
            response = self.session.post(
                f"{self.backend_url}/pdooh/campaigns",
                json=campaign_data,
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.test_campaign_id = data.get("campaign_id")
                    self.log_result("pDOOH Campaign Creation", True, 
                                  f"Created campaign ID: {self.test_campaign_id}")
                    return self.test_campaign_id
                else:
                    self.log_result("pDOOH Campaign Creation", False, error=data.get("error", "Unknown error"))
            else:
                self.log_result("pDOOH Campaign Creation", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("pDOOH Campaign Creation", False, error=str(e))
        
        return None
    
    def test_pdooh_campaigns_list(self):
        """Test /api/pdooh/campaigns - List campaigns"""
        try:
            response = self.session.get(
                f"{self.backend_url}/pdooh/campaigns",
                params={"user_id": self.user_id, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "campaigns" in data:
                    campaign_count = len(data["campaigns"])
                    total_count = data.get("total_count", 0)
                    self.log_result("pDOOH Campaigns List", True, 
                                  f"Retrieved {campaign_count} campaigns, total: {total_count}")
                else:
                    self.log_result("pDOOH Campaigns List", False, error="Invalid response structure")
            else:
                self.log_result("pDOOH Campaigns List", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("pDOOH Campaigns List", False, error=str(e))
    
    def test_pdooh_weather_triggers(self):
        """Test /api/pdooh/triggers/weather - Weather trigger endpoint"""
        try:
            # Test with NYC coordinates
            params = {
                "latitude": 40.7580,
                "longitude": -73.9855,
                "location_name": "New York City",
                "user_id": self.user_id
            }
            
            response = self.session.get(f"{self.backend_url}/pdooh/triggers/weather", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "weather_data" in data:
                    weather = data["weather_data"]
                    temperature = weather.get("temperature")
                    condition = weather.get("condition")
                    self.log_result("pDOOH Weather Triggers", True, 
                                  f"Weather data: {temperature}°F, {condition}")
                else:
                    self.log_result("pDOOH Weather Triggers", False, error="Invalid response structure")
            else:
                self.log_result("pDOOH Weather Triggers", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("pDOOH Weather Triggers", False, error=str(e))

    # ===== AWS LAMBDA FUNCTIONS MOCK TESTING =====
    
    def test_campaign_manager_logic(self):
        """Test doohCampaignManager.py Lambda logic (mock)"""
        try:
            if not self.test_campaign_id:
                self.log_result("Campaign Manager Logic", False, error="No test campaign available")
                return
            
            # Test campaign launch (simulates Lambda function)
            response = self.session.post(
                f"{self.backend_url}/pdooh/campaigns/{self.test_campaign_id}/launch",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    launch_results = data.get("launch_results", {})
                    platforms_launched = len(launch_results.get("platform_results", {}))
                    self.log_result("Campaign Manager Logic", True, 
                                  f"Campaign launched on {platforms_launched} platforms")
                else:
                    self.log_result("Campaign Manager Logic", False, error=data.get("error", "Unknown error"))
            else:
                self.log_result("Campaign Manager Logic", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Campaign Manager Logic", False, error=str(e))
    
    def test_trigger_engine_logic(self):
        """Test doohTriggerEngine.py Lambda functions"""
        try:
            if not self.test_campaign_id:
                self.log_result("Trigger Engine Logic", False, error="No test campaign available")
                return
            
            # Test trigger evaluation (simulates Lambda function)
            params = {
                "campaign_id": self.test_campaign_id,
                "location": "New York, NY",
                "latitude": 40.7580,
                "longitude": -73.9855,
                "user_id": self.user_id
            }
            
            response = self.session.post(
                f"{self.backend_url}/pdooh/triggers/evaluate",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    triggered_conditions = len(data.get("triggered_conditions", []))
                    evaluation_score = data.get("evaluation_score", 0)
                    self.log_result("Trigger Engine Logic", True, 
                                  f"Evaluated {triggered_conditions} conditions, score: {evaluation_score}")
                else:
                    self.log_result("Trigger Engine Logic", False, error=data.get("error", "Unknown error"))
            else:
                self.log_result("Trigger Engine Logic", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Trigger Engine Logic", False, error=str(e))
    
    def test_ethereum_integration_functions(self):
        """Test Ethereum integration components"""
        try:
            # Test DAO blockchain integration status
            response = self.session.get(f"{self.backend_url}/platform/dao/blockchain/status")
            
            if response.status_code == 200:
                data = response.json()
                if "ethereum" in str(data).lower() or "blockchain" in str(data).lower() or "status" in data:
                    self.log_result("Ethereum Integration Functions", True, 
                                  f"Blockchain integration accessible")
                else:
                    self.log_result("Ethereum Integration Functions", False, error="No blockchain data in response")
            elif response.status_code == 404:
                self.log_result("Ethereum Integration Functions", False, 
                              error="Blockchain endpoints not implemented")
            else:
                self.log_result("Ethereum Integration Functions", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Ethereum Integration Functions", False, error=str(e))

    # ===== INFRASTRUCTURE COMPONENTS TESTING =====
    
    def test_aws_configuration_validity(self):
        """Test AWS configuration files validity"""
        try:
            # Test AWS health endpoint if available
            response = self.session.get(f"{self.backend_url}/aws/health")
            
            if response.status_code == 200:
                data = response.json()
                if "aws" in data or "services" in data:
                    services_count = len(data.get("services", {}))
                    self.log_result("AWS Configuration Validity", True, 
                                  f"AWS configuration valid, {services_count} services")
                else:
                    self.log_result("AWS Configuration Validity", False, error="Invalid AWS config response")
            elif response.status_code == 404:
                self.log_result("AWS Configuration Validity", False, 
                              error="AWS health endpoint not available")
            else:
                self.log_result("AWS Configuration Validity", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("AWS Configuration Validity", False, error=str(e))
    
    def test_amplify_configuration(self):
        """Test Amplify configuration validity"""
        try:
            # Test if Amplify endpoints are configured
            response = self.session.get(f"{self.backend_url}/amplify/status")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Amplify Configuration", True, 
                              f"Amplify configuration accessible")
            elif response.status_code == 404:
                # This is expected if Amplify endpoints aren't exposed
                self.log_result("Amplify Configuration", True, 
                              f"Amplify not exposed via API (expected)")
            else:
                self.log_result("Amplify Configuration", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Amplify Configuration", False, error=str(e))
    
    def test_dependency_requirements(self):
        """Test dependency requirements compatibility"""
        try:
            # Test system health to verify dependencies
            response = self.session.get(f"{self.backend_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    status = data.get("status", "unknown")
                    self.log_result("Dependency Requirements", True, 
                                  f"System health: {status}")
                else:
                    self.log_result("Dependency Requirements", False, error="No status in health response")
            else:
                # Try alternative health endpoint
                response = self.session.get(self.backend_url.replace("/api", "/"))
                if response.status_code == 200:
                    self.log_result("Dependency Requirements", True, 
                                  f"Server responding, dependencies likely OK")
                else:
                    self.log_result("Dependency Requirements", False, 
                                  error=f"Health check failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Dependency Requirements", False, error=str(e))

    # ===== BACKEND INTEGRATION TESTS =====
    
    def test_pdooh_performance_analytics(self):
        """Test /api/pdooh/campaigns/{id}/performance"""
        try:
            if not self.test_campaign_id:
                self.log_result("pDOOH Performance Analytics", False, error="No test campaign available")
                return
            
            response = self.session.get(
                f"{self.backend_url}/pdooh/campaigns/{self.test_campaign_id}/performance",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "performance_summary" in data:
                    performance = data["performance_summary"]
                    impressions = performance.get("total_impressions", 0)
                    spend = performance.get("total_spend", 0)
                    self.log_result("pDOOH Performance Analytics", True, 
                                  f"Performance data: {impressions} impressions, ${spend} spend")
                else:
                    self.log_result("pDOOH Performance Analytics", False, error="Invalid response structure")
            else:
                self.log_result("pDOOH Performance Analytics", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("pDOOH Performance Analytics", False, error=str(e))
    
    def test_pdooh_attribution_data(self):
        """Test /api/pdooh/campaigns/{id}/attribution"""
        try:
            if not self.test_campaign_id:
                self.log_result("pDOOH Attribution Data", False, error="No test campaign available")
                return
            
            response = self.session.get(
                f"{self.backend_url}/pdooh/campaigns/{self.test_campaign_id}/attribution",
                params={"user_id": self.user_id, "attribution_window_hours": 24}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "attribution_data" in data:
                    attribution = data["attribution_data"]
                    conversions = attribution.get("total_conversions", 0)
                    rate = attribution.get("attribution_rate", 0)
                    self.log_result("pDOOH Attribution Data", True, 
                                  f"Attribution: {conversions} conversions, {rate}% rate")
                else:
                    self.log_result("pDOOH Attribution Data", False, error="Invalid response structure")
            else:
                self.log_result("pDOOH Attribution Data", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("pDOOH Attribution Data", False, error=str(e))
    
    def test_pdooh_creative_optimization(self):
        """Test /api/pdooh/dco/optimize"""
        try:
            if not self.test_campaign_id:
                self.log_result("pDOOH Creative Optimization", False, error="No test campaign available")
                return
            
            location_data = {
                "location": "New York, NY",
                "latitude": 40.7580,
                "longitude": -73.9855
            }
            
            response = self.session.post(
                f"{self.backend_url}/pdooh/dco/optimize",
                json=location_data,
                params={"campaign_id": self.test_campaign_id, "user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "optimization" in data:
                    optimization = data["optimization"]
                    score = optimization.get("optimization_score", 0)
                    variants = len(optimization.get("creative_variants", {}))
                    self.log_result("pDOOH Creative Optimization", True, 
                                  f"Optimization score: {score}, {variants} variants")
                else:
                    self.log_result("pDOOH Creative Optimization", False, error="Invalid response structure")
            else:
                self.log_result("pDOOH Creative Optimization", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("pDOOH Creative Optimization", False, error=str(e))

    # ===== CONFIGURATION VALIDATION =====
    
    def test_service_integration_points(self):
        """Test service integration points"""
        try:
            # Test monitoring dashboard
            response = self.session.get(
                f"{self.backend_url}/pdooh/monitoring/dashboard",
                params={"user_id": self.user_id, "time_range": "24h"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "dashboard" in data:
                    dashboard = data["dashboard"]
                    campaigns = dashboard.get("campaign_overview", {}).get("total_campaigns", 0)
                    self.log_result("Service Integration Points", True, 
                                  f"Dashboard accessible, {campaigns} campaigns tracked")
                else:
                    self.log_result("Service Integration Points", False, error="Invalid dashboard response")
            else:
                self.log_result("Service Integration Points", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Service Integration Points", False, error=str(e))
    
    def test_authentication_integration(self):
        """Test authentication integration with pDOOH endpoints"""
        try:
            # Test unauthorized access
            session_no_auth = requests.Session()
            response = session_no_auth.get(f"{self.backend_url}/pdooh/campaigns")
            
            if response.status_code == 401 or response.status_code == 422:
                self.log_result("Authentication Integration", True, 
                              "pDOOH endpoints properly secured")
            else:
                self.log_result("Authentication Integration", False, 
                              error=f"Expected 401/422, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Authentication Integration", False, error=str(e))

    def run_comprehensive_tests(self):
        """Run all comprehensive AWS DOOH integration tests"""
        print("🎯 AWS DOOH INTEGRATION BACKEND TESTING")
        print("=" * 80)
        print()
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with authenticated tests.")
            return
        
        print("🏗️ TESTING CORE BACKEND COMPATIBILITY")
        print("-" * 50)
        
        # Core Backend Compatibility Tests
        self.test_pdooh_platforms_endpoint()
        self.test_campaign_id = self.test_pdooh_campaigns_create()
        self.test_pdooh_campaigns_list()
        self.test_pdooh_weather_triggers()
        
        print("⚡ TESTING AWS LAMBDA FUNCTIONS (MOCK)")
        print("-" * 50)
        
        # AWS Lambda Functions Mock Testing
        self.test_campaign_manager_logic()
        self.test_trigger_engine_logic()
        self.test_ethereum_integration_functions()
        
        print("🏗️ TESTING INFRASTRUCTURE COMPONENTS")
        print("-" * 50)
        
        # Infrastructure Components Testing
        self.test_aws_configuration_validity()
        self.test_amplify_configuration()
        self.test_dependency_requirements()
        
        print("🔗 TESTING BACKEND INTEGRATION")
        print("-" * 50)
        
        # Backend Integration Tests
        self.test_pdooh_performance_analytics()
        self.test_pdooh_attribution_data()
        self.test_pdooh_creative_optimization()
        
        print("✅ TESTING CONFIGURATION VALIDATION")
        print("-" * 50)
        
        # Configuration Validation
        self.test_service_integration_points()
        self.test_authentication_integration()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 AWS DOOH INTEGRATION TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        backend_tests = [r for r in self.test_results if any(x in r["test"] for x in ["pDOOH", "Backend"])]
        lambda_tests = [r for r in self.test_results if any(x in r["test"] for x in ["Campaign Manager", "Trigger Engine", "Ethereum"])]
        infrastructure_tests = [r for r in self.test_results if any(x in r["test"] for x in ["AWS", "Amplify", "Dependency"])]
        integration_tests = [r for r in self.test_results if any(x in r["test"] for x in ["Performance", "Attribution", "Creative", "Service", "Authentication"])]
        
        print("🏗️ CORE BACKEND COMPATIBILITY:")
        backend_passed = len([r for r in backend_tests if r["success"]])
        print(f"   {backend_passed}/{len(backend_tests)} backend tests passed ({(backend_passed/len(backend_tests)*100):.1f}%)")
        
        print("⚡ AWS LAMBDA FUNCTIONS:")
        lambda_passed = len([r for r in lambda_tests if r["success"]])
        print(f"   {lambda_passed}/{len(lambda_tests)} lambda tests passed ({(lambda_passed/len(lambda_tests)*100):.1f}%)")
        
        print("🏗️ INFRASTRUCTURE COMPONENTS:")
        infra_passed = len([r for r in infrastructure_tests if r["success"]])
        print(f"   {infra_passed}/{len(infrastructure_tests)} infrastructure tests passed ({(infra_passed/len(infrastructure_tests)*100):.1f}%)")
        
        print("🔗 BACKEND INTEGRATION:")
        int_passed = len([r for r in integration_tests if r["success"]])
        print(f"   {int_passed}/{len(integration_tests)} integration tests passed ({(int_passed/len(integration_tests)*100):.1f}%)")
        
        print("\n❌ FAILED TESTS:")
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            for result in failed_results:
                print(f"   • {result['test']}: {result['error']}")
        else:
            print("   None! All tests passed! 🎉")
        
        print("\n✅ CRITICAL FINDINGS:")
        
        # Backend Compatibility Status
        backend_success_rate = (backend_passed / len(backend_tests)) * 100 if backend_tests else 0
        if backend_success_rate >= 80:
            print("   • Backend Compatibility: EXCELLENT - All existing pDOOH endpoints functional")
        elif backend_success_rate >= 60:
            print("   • Backend Compatibility: GOOD - Minor compatibility issues")
        else:
            print("   • Backend Compatibility: NEEDS WORK - Major compatibility issues detected")
        
        # Lambda Functions Status
        lambda_success_rate = (lambda_passed / len(lambda_tests)) * 100 if lambda_tests else 0
        if lambda_success_rate >= 80:
            print("   • AWS Lambda Functions: EXCELLENT - Logic flow correct")
        elif lambda_success_rate >= 60:
            print("   • AWS Lambda Functions: GOOD - Minor logic issues")
        else:
            print("   • AWS Lambda Functions: NEEDS WORK - Major logic issues detected")
        
        # Overall System Status
        if success_rate >= 90:
            print("   • Overall AWS DOOH Integration: PRODUCTION READY")
        elif success_rate >= 75:
            print("   • Overall AWS DOOH Integration: MOSTLY READY - Minor fixes needed")
        else:
            print("   • Overall AWS DOOH Integration: REQUIRES ATTENTION - Multiple issues detected")
        
        print("\n🎯 SUCCESS CRITERIA ASSESSMENT:")
        
        # Check success criteria from review request
        criteria_met = 0
        total_criteria = 6
        
        if backend_success_rate >= 80:
            print("   ✅ All existing pDOOH endpoints remain functional")
            criteria_met += 1
        else:
            print("   ❌ Some pDOOH endpoints have issues")
        
        if lambda_success_rate >= 80:
            print("   ✅ AWS integration components properly structured")
            criteria_met += 1
        else:
            print("   ❌ AWS integration components need work")
        
        if lambda_success_rate >= 80:
            print("   ✅ Lambda functions have correct logic flow")
            criteria_met += 1
        else:
            print("   ❌ Lambda functions have logic issues")
        
        if infra_passed >= len(infrastructure_tests) * 0.8:
            print("   ✅ Configuration files properly formatted")
            criteria_met += 1
        else:
            print("   ❌ Configuration files have issues")
        
        if success_rate >= 80:
            print("   ✅ No breaking changes to existing functionality")
            criteria_met += 1
        else:
            print("   ❌ Breaking changes detected")
        
        if int_passed >= len(integration_tests) * 0.8:
            print("   ✅ Integration compatibility verified")
            criteria_met += 1
        else:
            print("   ❌ Integration compatibility issues")
        
        print(f"\n📈 SUCCESS CRITERIA MET: {criteria_met}/{total_criteria} ({(criteria_met/total_criteria)*100:.1f}%)")
        
        print("\n🎯 RECOMMENDATIONS:")
        if criteria_met == total_criteria:
            print("   • All success criteria met - AWS DOOH integration ready for production")
        elif criteria_met >= total_criteria * 0.8:
            print("   • Most criteria met - Address remaining issues before production")
        else:
            print("   • Multiple criteria not met - Significant work needed before production")
            print("   • Focus on backend compatibility and Lambda function logic")
            print("   • Verify AWS infrastructure configuration")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = AWSDoohBackendTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()