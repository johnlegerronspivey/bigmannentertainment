#!/usr/bin/env python3
"""
BME Application Comprehensive Backend Testing
Testing all backend systems including ULN, Creator Profile, Licensing, and Social Media Integration
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://creator-profile-hub.preview.emergentagent.com/api"
ADMIN_EMAIL = "uln.admin@bigmann.com"
ADMIN_PASSWORD = "Admin123!"

class BMEComprehensiveBackendTester:
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
    
    def test_main_health_endpoint(self):
        """Test main health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                if status == "healthy":
                    self.log_test("Main Health Endpoint", "PASS", 
                                f"System healthy - {data.get('message', 'No message')}")
                    return True
                else:
                    self.log_test("Main Health Endpoint", "FAIL", 
                                f"System status: {status}")
                    return False
            else:
                self.log_test("Main Health Endpoint", "FAIL", 
                            f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Main Health Endpoint", "FAIL", 
                        f"Error checking health: {str(e)}")
            return False
    
    def test_uln_health_endpoint(self):
        """Test ULN health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/uln/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                if status == "healthy":
                    labels_count = data.get("total_labels", 0)
                    self.log_test("ULN Health Endpoint", "PASS", 
                                f"ULN system healthy with {labels_count} labels")
                    return True
                else:
                    self.log_test("ULN Health Endpoint", "FAIL", 
                                f"ULN status: {status}")
                    return False
            else:
                self.log_test("ULN Health Endpoint", "FAIL", 
                            f"ULN health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("ULN Health Endpoint", "FAIL", 
                        f"Error checking ULN health: {str(e)}")
            return False
    
    def test_uln_label_hub(self):
        """Test ULN label directory/hub"""
        try:
            response = self.session.get(f"{BACKEND_URL}/uln/dashboard/label-hub")
            
            if response.status_code == 200:
                data = response.json()
                labels = data.get("labels", [])
                total_labels = data.get("total_labels", len(labels))
                self.log_test("ULN Label Hub", "PASS", 
                            f"Retrieved {total_labels} labels from hub")
                return True
            elif response.status_code == 403:
                self.log_test("ULN Label Hub", "FAIL", 
                            "Access denied - requires admin permissions")
                return False
            else:
                self.log_test("ULN Label Hub", "FAIL", 
                            f"Label hub failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Label Hub", "FAIL", 
                        f"Error accessing label hub: {str(e)}")
            return False
    
    def test_uln_edit_label_api(self):
        """Test generic Edit Label API"""
        try:
            # First get a label to edit
            hub_response = self.session.get(f"{BACKEND_URL}/uln/dashboard/label-hub")
            if hub_response.status_code != 200:
                self.log_test("ULN Edit Label API", "FAIL", "Cannot get labels for editing test")
                return False
            
            labels = hub_response.json().get("labels", [])
            if not labels:
                self.log_test("ULN Edit Label API", "FAIL", "No labels available for editing")
                return False
            
            # Test editing the first label
            test_label = labels[0]
            global_id = test_label.get("global_id")
            
            if not global_id:
                self.log_test("ULN Edit Label API", "FAIL", "No global_id found in label")
                return False
            
            # Test update
            update_data = {
                "status": "active",
                "updated_by": "backend_test"
            }
            
            response = self.session.patch(
                f"{BACKEND_URL}/uln/labels/{global_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("ULN Edit Label API", "PASS", 
                            f"Successfully updated label {global_id}")
                return True
            else:
                self.log_test("ULN Edit Label API", "FAIL", 
                            f"Edit failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Edit Label API", "FAIL", 
                        f"Error testing edit API: {str(e)}")
            return False
    
    def test_uln_advanced_search(self):
        """Test ULN advanced search"""
        try:
            search_data = {
                "name": "Atlantic",
                "label_type": "major",
                "status": "active"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/uln/labels/advanced-search",
                json=search_data
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)
                self.log_test("ULN Advanced Search", "PASS", 
                            f"Search returned {total} results")
                return True
            else:
                self.log_test("ULN Advanced Search", "FAIL", 
                            f"Search failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Advanced Search", "FAIL", 
                        f"Error testing advanced search: {str(e)}")
            return False
    
    def test_uln_bulk_edit(self):
        """Test ULN bulk edit"""
        try:
            # Get some labels first
            hub_response = self.session.get(f"{BACKEND_URL}/uln/dashboard/label-hub")
            if hub_response.status_code != 200:
                self.log_test("ULN Bulk Edit", "FAIL", "Cannot get labels for bulk edit test")
                return False
            
            labels = hub_response.json().get("labels", [])
            if len(labels) < 2:
                self.log_test("ULN Bulk Edit", "FAIL", "Need at least 2 labels for bulk edit test")
                return False
            
            # Test bulk edit on first 2 labels
            label_ids = [labels[0].get("global_id"), labels[1].get("global_id")]
            
            bulk_data = {
                "label_ids": label_ids,
                "update_data": {
                    "status": "active",
                    "updated_by": "bulk_test"
                }
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/uln/labels/bulk-edit",
                json=bulk_data
            )
            
            if response.status_code == 200:
                data = response.json()
                updated_count = data.get("updated_count", 0)
                self.log_test("ULN Bulk Edit", "PASS", 
                            f"Bulk updated {updated_count} labels")
                return True
            else:
                self.log_test("ULN Bulk Edit", "FAIL", 
                            f"Bulk edit failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Bulk Edit", "FAIL", 
                        f"Error testing bulk edit: {str(e)}")
            return False
    
    def test_uln_export(self):
        """Test ULN export"""
        try:
            export_data = {
                "format": "json",
                "include_metadata": True
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/uln/labels/export",
                json=export_data
            )
            
            if response.status_code == 200:
                data = response.json()
                exported_count = data.get("exported_count", 0)
                self.log_test("ULN Export", "PASS", 
                            f"Exported {exported_count} labels")
                return True
            else:
                self.log_test("ULN Export", "FAIL", 
                            f"Export failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Export", "FAIL", 
                        f"Error testing export: {str(e)}")
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