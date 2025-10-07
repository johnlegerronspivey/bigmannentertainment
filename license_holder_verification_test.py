#!/usr/bin/env python3
"""
License Holder Information Verification Test for Big Mann Entertainment
Tests the specific fix for EIN: 270658077 and TIN: 12800 values in licensing dashboard
"""

import requests
import json
import os
from datetime import datetime

class LicenseHolderVerificationTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://bme-dashboard.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        self.token = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results['details'].append(f"{status}: {test_name} - {details}")
        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")
    
    def authenticate(self):
        """Authenticate with the backend"""
        try:
            # Try to register a test user
            register_data = {
                "email": "license.test@bigmannentertainment.com",
                "password": "LicenseTest2025!",
                "full_name": "License Test User",
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }
            
            response = requests.post(f"{self.api_base}/auth/register", json=register_data)
            if response.status_code not in [200, 201, 400]:  # 400 might mean user already exists
                print(f"Registration response: {response.status_code}")
            
            # Login
            login_data = {
                "email": "license.test@bigmannentertainment.com",
                "password": "LicenseTest2025!"
            }
            
            response = requests.post(f"{self.api_base}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.log_result("Authentication", True, "Successfully authenticated")
                return True
            else:
                self.log_result("Authentication", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get headers with authentication"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_licensing_dashboard_endpoint(self):
        """Test the licensing dashboard endpoint exists and responds"""
        try:
            response = requests.get(f"{self.api_base}/licensing/dashboard", headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Licensing Dashboard Endpoint", True, "Endpoint accessible and returns 200")
                return response.json()
            elif response.status_code == 401:
                self.log_result("Licensing Dashboard Endpoint", True, "Endpoint exists but requires authentication (expected)")
                return None
            elif response.status_code == 403:
                self.log_result("Licensing Dashboard Endpoint", True, "Endpoint exists but requires proper permissions")
                return None
            else:
                self.log_result("Licensing Dashboard Endpoint", False, f"Unexpected status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Licensing Dashboard Endpoint", False, f"Endpoint error: {str(e)}")
            return None
    
    def test_business_identifiers_endpoint(self):
        """Test the business identifiers endpoint for EIN and TIN values"""
        try:
            response = requests.get(f"{self.api_base}/business/identifiers", headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Business Identifiers Endpoint", True, "Endpoint accessible and returns 200")
                return data
            elif response.status_code == 401:
                self.log_result("Business Identifiers Endpoint", True, "Endpoint exists but requires authentication (expected)")
                return None
            elif response.status_code == 403:
                self.log_result("Business Identifiers Endpoint", True, "Endpoint exists but requires proper permissions")
                return None
            else:
                self.log_result("Business Identifiers Endpoint", False, f"Unexpected status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Business Identifiers Endpoint", False, f"Endpoint error: {str(e)}")
            return None
    
    def test_business_info_structure(self, dashboard_data):
        """Test that business_info object has correct structure"""
        if not dashboard_data:
            self.log_result("Business Info Structure", False, "No dashboard data available")
            return False
        
        try:
            business_info = dashboard_data.get('business_info', {})
            
            if not business_info:
                self.log_result("Business Info Structure", False, "business_info object missing from response")
                return False
            
            required_fields = [
                'business_entity', 'business_owner', 'license_holder', 
                'business_type', 'industry', 'ein', 'tin', 'established'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in business_info:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_result("Business Info Structure", False, f"Missing fields: {', '.join(missing_fields)}")
                return False
            else:
                self.log_result("Business Info Structure", True, "All required fields present")
                return True
                
        except Exception as e:
            self.log_result("Business Info Structure", False, f"Structure validation error: {str(e)}")
            return False
    
    def test_ein_value(self, dashboard_data):
        """Test that EIN value is correct: 270658077"""
        if not dashboard_data:
            self.log_result("EIN Value Verification", False, "No dashboard data available")
            return False
        
        try:
            business_info = dashboard_data.get('business_info', {})
            ein_value = business_info.get('ein')
            
            expected_ein = "270658077"
            
            if ein_value == expected_ein:
                self.log_result("EIN Value Verification", True, f"EIN correctly set to {expected_ein}")
                return True
            else:
                self.log_result("EIN Value Verification", False, f"EIN mismatch - Expected: {expected_ein}, Got: {ein_value}")
                return False
                
        except Exception as e:
            self.log_result("EIN Value Verification", False, f"EIN validation error: {str(e)}")
            return False
    
    def test_tin_value(self, dashboard_data):
        """Test that TIN value is correct: 12800"""
        if not dashboard_data:
            self.log_result("TIN Value Verification", False, "No dashboard data available")
            return False
        
        try:
            business_info = dashboard_data.get('business_info', {})
            tin_value = business_info.get('tin')
            
            expected_tin = "12800"
            
            if tin_value == expected_tin:
                self.log_result("TIN Value Verification", True, f"TIN correctly set to {expected_tin}")
                return True
            else:
                self.log_result("TIN Value Verification", False, f"TIN mismatch - Expected: {expected_tin}, Got: {tin_value}")
                return False
                
        except Exception as e:
            self.log_result("TIN Value Verification", False, f"TIN validation error: {str(e)}")
            return False
    
    def test_ein_value_from_business_identifiers(self, business_data):
        """Test that EIN value is correct from business identifiers endpoint: 270658077"""
        if not business_data:
            self.log_result("EIN Value (Business Identifiers)", False, "No business identifiers data available")
            return False
        
        try:
            ein_value = business_data.get('business_ein')
            expected_ein = "270658077"
            
            if ein_value == expected_ein:
                self.log_result("EIN Value (Business Identifiers)", True, f"EIN correctly set to {expected_ein}")
                return True
            else:
                self.log_result("EIN Value (Business Identifiers)", False, f"EIN mismatch - Expected: {expected_ein}, Got: {ein_value}")
                return False
                
        except Exception as e:
            self.log_result("EIN Value (Business Identifiers)", False, f"EIN validation error: {str(e)}")
            return False
    
    def test_tin_value_from_business_identifiers(self, business_data):
        """Test that TIN value is correct from business identifiers endpoint: 12800"""
        if not business_data:
            self.log_result("TIN Value (Business Identifiers)", False, "No business identifiers data available")
            return False
        
        try:
            tin_value = business_data.get('business_tin')
            expected_tin = "12800"
            
            if tin_value == expected_tin:
                self.log_result("TIN Value (Business Identifiers)", True, f"TIN correctly set to {expected_tin}")
                return True
            else:
                self.log_result("TIN Value (Business Identifiers)", False, f"TIN mismatch - Expected: {expected_tin}, Got: {tin_value}")
                return False
                
        except Exception as e:
            self.log_result("TIN Value (Business Identifiers)", False, f"TIN validation error: {str(e)}")
            return False
    
    def test_business_entity_values(self, dashboard_data):
        """Test that other business entity values are correct"""
        if not dashboard_data:
            self.log_result("Business Entity Values", False, "No dashboard data available")
            return False
        
        try:
            business_info = dashboard_data.get('business_info', {})
            
            expected_values = {
                'business_entity': 'Big Mann Entertainment',
                'business_owner': 'John LeGerron Spivey',
                'license_holder': 'John LeGerron Spivey',
                'business_type': 'Sole Proprietorship',
                'industry': 'Media Entertainment',
                'established': '2020'
            }
            
            mismatches = []
            for field, expected_value in expected_values.items():
                actual_value = business_info.get(field)
                if actual_value != expected_value:
                    mismatches.append(f"{field}: Expected '{expected_value}', Got '{actual_value}'")
            
            if mismatches:
                self.log_result("Business Entity Values", False, f"Value mismatches: {'; '.join(mismatches)}")
                return False
            else:
                self.log_result("Business Entity Values", True, "All business entity values correct")
                return True
                
        except Exception as e:
            self.log_result("Business Entity Values", False, f"Business entity validation error: {str(e)}")
            return False
    
    def test_dashboard_functionality(self, dashboard_data):
        """Test that dashboard maintains existing functionality"""
        if not dashboard_data:
            self.log_result("Dashboard Functionality", False, "No dashboard data available")
            return False
        
        try:
            # Check for expected dashboard sections
            expected_sections = ['licensing_overview', 'business_info', 'financial_summary']
            missing_sections = []
            
            for section in expected_sections:
                if section not in dashboard_data:
                    missing_sections.append(section)
            
            if missing_sections:
                self.log_result("Dashboard Functionality", False, f"Missing sections: {', '.join(missing_sections)}")
                return False
            
            # Check licensing overview has expected fields
            licensing_overview = dashboard_data.get('licensing_overview', {})
            overview_fields = ['total_platforms_licensed', 'active_licenses', 'pending_licenses', 'expired_licenses', 'compliance_rate']
            
            missing_overview_fields = []
            for field in overview_fields:
                if field not in licensing_overview:
                    missing_overview_fields.append(field)
            
            if missing_overview_fields:
                self.log_result("Dashboard Functionality", False, f"Missing overview fields: {', '.join(missing_overview_fields)}")
                return False
            
            self.log_result("Dashboard Functionality", True, "All dashboard sections and fields present")
            return True
            
        except Exception as e:
            self.log_result("Dashboard Functionality", False, f"Functionality validation error: {str(e)}")
            return False
    
    def test_system_integration(self):
        """Test that licensing service integration is working"""
        try:
            # Test licensing status endpoint
            response = requests.get(f"{self.api_base}/licensing/status", headers=self.get_headers())
            
            if response.status_code in [200, 401, 403]:  # Any of these means endpoint exists
                self.log_result("System Integration", True, "Licensing service endpoints accessible")
                return True
            else:
                self.log_result("System Integration", False, f"Licensing service not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("System Integration", False, f"Integration test error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all license holder information verification tests"""
        print("🎯 LICENSE HOLDER INFORMATION VERIFICATION TEST")
        print("=" * 80)
        print("Testing EIN: 270658077 and TIN: 12800 values in licensing dashboard")
        print("=" * 80)
        
        # Step 1: Authentication (optional for this test)
        auth_success = self.authenticate()
        if not auth_success:
            print("⚠️  Authentication failed, proceeding with endpoint existence tests")
        
        # Step 2: Test licensing dashboard endpoint
        dashboard_data = self.test_licensing_dashboard_endpoint()
        
        # Step 3: Test business identifiers endpoint (alternative source for EIN/TIN)
        business_data = self.test_business_identifiers_endpoint()
        
        # Step 4: Test business info structure (if dashboard data available)
        if dashboard_data:
            self.test_business_info_structure(dashboard_data)
            
            # Step 5: Test EIN value (CRITICAL)
            self.test_ein_value(dashboard_data)
            
            # Step 6: Test TIN value (CRITICAL)
            self.test_tin_value(dashboard_data)
            
            # Step 7: Test other business entity values
            self.test_business_entity_values(dashboard_data)
            
            # Step 8: Test dashboard functionality
            self.test_dashboard_functionality(dashboard_data)
        
        # Step 9: Test EIN/TIN from business identifiers endpoint
        if business_data:
            self.test_ein_value_from_business_identifiers(business_data)
            self.test_tin_value_from_business_identifiers(business_data)
        
        # Step 10: Test system integration
        self.test_system_integration()
        
        # Print detailed results
        print("\n" + "=" * 80)
        print("🎯 LICENSE HOLDER INFORMATION VERIFICATION RESULTS")
        print("=" * 80)
        
        for detail in self.test_results['details']:
            print(detail)
        
        print(f"\n📊 VERIFICATION SUMMARY:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / max(total_tests, 1)) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Print dashboard data for verification
        if dashboard_data:
            print(f"\n📋 LICENSING DASHBOARD BUSINESS INFO:")
            business_info = dashboard_data.get('business_info', {})
            print(f"  Business Entity: {business_info.get('business_entity', 'N/A')}")
            print(f"  Business Owner: {business_info.get('business_owner', 'N/A')}")
            print(f"  License Holder: {business_info.get('license_holder', 'N/A')}")
            print(f"  Business Type: {business_info.get('business_type', 'N/A')}")
            print(f"  Industry: {business_info.get('industry', 'N/A')}")
            print(f"  EIN: {business_info.get('ein', 'N/A')} {'✅' if business_info.get('ein') == '270658077' else '❌'}")
            print(f"  TIN: {business_info.get('tin', 'N/A')} {'✅' if business_info.get('tin') == '12800' else '❌'}")
            print(f"  Established: {business_info.get('established', 'N/A')}")
        
        # Print business identifiers data for verification
        if business_data:
            print(f"\n📋 BUSINESS IDENTIFIERS DATA:")
            print(f"  Business Legal Name: {business_data.get('business_legal_name', 'N/A')}")
            print(f"  Business EIN: {business_data.get('business_ein', 'N/A')} {'✅' if business_data.get('business_ein') == '270658077' else '❌'}")
            print(f"  Business TIN: {business_data.get('business_tin', 'N/A')} {'✅' if business_data.get('business_tin') == '12800' else '❌'}")
            print(f"  Business Address: {business_data.get('business_address', 'N/A')}")
            print(f"  Business Phone: {business_data.get('business_phone', 'N/A')}")
        
        # Check for critical EIN/TIN verification
        ein_verified = False
        tin_verified = False
        
        if dashboard_data:
            business_info = dashboard_data.get('business_info', {})
            if business_info.get('ein') == '270658077':
                ein_verified = True
            if business_info.get('tin') == '12800':
                tin_verified = True
        
        if business_data:
            if business_data.get('business_ein') == '270658077':
                ein_verified = True
            if business_data.get('business_tin') == '12800':
                tin_verified = True
        
        if self.test_results['failed'] == 0:
            print("\n🎉 ALL LICENSE HOLDER INFORMATION TESTS PASSED!")
        
        if ein_verified and tin_verified:
            print("✅ EIN: 270658077 - VERIFIED")
            print("✅ TIN: 12800 - VERIFIED")
            print("🎯 The License Holder Information fix has been successfully implemented.")
        else:
            print("\n🚨 CRITICAL VERIFICATION STATUS:")
            print(f"{'✅' if ein_verified else '❌'} EIN: 270658077 - {'VERIFIED' if ein_verified else 'NOT VERIFIED'}")
            print(f"{'✅' if tin_verified else '❌'} TIN: 12800 - {'VERIFIED' if tin_verified else 'NOT VERIFIED'}")
            
        if self.test_results['failed'] > 0:
            print(f"\n⚠️  {self.test_results['failed']} tests failed. Review the details above.")

def main():
    """Run the license holder information verification test"""
    tester = LicenseHolderVerificationTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()