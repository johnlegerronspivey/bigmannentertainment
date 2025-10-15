#!/usr/bin/env python3
"""
Comprehensive Platform License Generation Testing
Testing the comprehensive platform license generation functionality for all 115+ platforms
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-profile-sync.preview.emergentagent.com/api"
ADMIN_EMAIL = "uln.admin@bigmann.com"
ADMIN_PASSWORD = "Admin123!"

class ComprehensiveLicenseGenerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, status, details):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {details}")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", "PASS", f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Authentication", "FAIL", f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Authentication error: {str(e)}")
            return False
    
    def test_distribution_platforms_availability(self):
        """Test that distribution platforms are available"""
        try:
            response = self.session.get(f"{BACKEND_URL}/distribution/platforms")
            
            if response.status_code == 200:
                data = response.json()
                platform_count = data.get("total_count", data.get("total_platforms", 0))
                
                if platform_count >= 115:
                    self.log_test("Distribution Platforms Availability", "PASS", 
                                f"Found {platform_count} platforms (meets 115+ requirement)")
                    return True
                else:
                    self.log_test("Distribution Platforms Availability", "FAIL", 
                                f"Only {platform_count} platforms found (need 115+)")
                    return False
            else:
                self.log_test("Distribution Platforms Availability", "FAIL", 
                            f"Failed to get platforms: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Distribution Platforms Availability", "FAIL", 
                        f"Error checking platforms: {str(e)}")
            return False
    
    def test_comprehensive_license_generation(self):
        """Test the main comprehensive license generation endpoint"""
        try:
            # Test the comprehensive license generation endpoint
            response = self.session.post(
                f"{BACKEND_URL}/comprehensive-licensing/generate-all-platform-licenses",
                json={
                    "include_compliance_docs": True,
                    "generate_workflows": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = [
                    "message", "master_agreement", "agreement_id", 
                    "business_entity", "platforms_licensed", "platform_categories",
                    "comprehensive_features"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test("License Generation Response Structure", "FAIL", 
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify platforms licensed count
                platforms_licensed = data.get("platforms_licensed", 0)
                if platforms_licensed >= 115:
                    self.log_test("License Generation", "PASS", 
                                f"Successfully generated licenses for {platforms_licensed} platforms")
                    
                    # Test individual response components
                    self.verify_response_components(data)
                    return True
                else:
                    self.log_test("License Generation", "FAIL", 
                                f"Only {platforms_licensed} platforms licensed (need 115+)")
                    return False
                    
            else:
                self.log_test("License Generation", "FAIL", 
                            f"Endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("License Generation", "FAIL", 
                        f"Error testing license generation: {str(e)}")
            return False
    
    def verify_response_components(self, data):
        """Verify individual components of the response"""
        
        # Test message field
        message = data.get("message", "")
        if "comprehensive platform licensing" in message.lower():
            self.log_test("Response Message", "PASS", "Message field contains expected content")
        else:
            self.log_test("Response Message", "FAIL", f"Unexpected message: {message}")
        
        # Test master_agreement object
        master_agreement = data.get("master_agreement")
        if isinstance(master_agreement, dict) and master_agreement:
            self.log_test("Master Agreement Object", "PASS", "Master agreement object exists and is populated")
        else:
            self.log_test("Master Agreement Object", "FAIL", "Master agreement object missing or empty")
        
        # Test agreement_id
        agreement_id = data.get("agreement_id")
        if agreement_id and isinstance(agreement_id, str):
            self.log_test("Agreement ID", "PASS", f"Agreement ID generated: {agreement_id}")
        else:
            self.log_test("Agreement ID", "FAIL", "Agreement ID missing or invalid")
        
        # Test business_entity
        business_entity = data.get("business_entity")
        if business_entity:
            self.log_test("Business Entity", "PASS", f"Business entity populated: {business_entity}")
        else:
            self.log_test("Business Entity", "FAIL", "Business entity missing")
        
        # Test platform_categories
        platform_categories = data.get("platform_categories", [])
        if isinstance(platform_categories, list) and len(platform_categories) > 0:
            self.log_test("Platform Categories", "PASS", 
                        f"Found {len(platform_categories)} platform categories")
        else:
            self.log_test("Platform Categories", "FAIL", "Platform categories missing or empty")
        
        # Test comprehensive_features
        comprehensive_features = data.get("comprehensive_features", [])
        expected_features = [
            "Business information integration",
            "Multi-platform category licensing", 
            "Automated compliance documentation"
        ]
        
        found_features = 0
        for feature in expected_features:
            if any(feature.lower() in f.lower() for f in comprehensive_features):
                found_features += 1
        
        if found_features >= 2:
            self.log_test("Comprehensive Features", "PASS", 
                        f"Found {found_features}/{len(expected_features)} expected features")
        else:
            self.log_test("Comprehensive Features", "FAIL", 
                        f"Only found {found_features}/{len(expected_features)} expected features")
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        
        # Test without authentication
        temp_headers = self.session.headers.copy()
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/comprehensive-licensing/generate-all-platform-licenses"
            )
            
            if response.status_code in [401, 403]:
                self.log_test("Authentication Required", "PASS", 
                            "Endpoint properly requires authentication")
            else:
                self.log_test("Authentication Required", "FAIL", 
                            f"Endpoint should require auth but returned: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication Required", "FAIL", f"Error testing auth: {str(e)}")
        
        # Restore headers
        self.session.headers.update(temp_headers)
    
    def test_licensing_dashboard(self):
        """Test the licensing dashboard endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/comprehensive-licensing/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if "comprehensive_licensing_dashboard" in data:
                    self.log_test("Licensing Dashboard", "PASS", "Dashboard endpoint accessible")
                else:
                    self.log_test("Licensing Dashboard", "FAIL", "Dashboard data missing")
            else:
                self.log_test("Licensing Dashboard", "FAIL", 
                            f"Dashboard endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Licensing Dashboard", "FAIL", f"Dashboard error: {str(e)}")
    
    def run_all_tests(self):
        """Run all comprehensive license generation tests"""
        print("🚀 Starting Comprehensive Platform License Generation Testing")
        print("=" * 70)
        
        # Test 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with other tests")
            return False
        
        # Test 2: Distribution platforms availability
        self.test_distribution_platforms_availability()
        
        # Test 3: Main license generation endpoint
        self.test_comprehensive_license_generation()
        
        # Test 4: Error handling
        self.test_error_handling()
        
        # Test 5: Dashboard access
        self.test_licensing_dashboard()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        total_tests = len(self.test_results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [t for t in self.test_results if t["status"] == "FAIL"]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = ComprehensiveLicenseGenerationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Comprehensive license generation is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()