#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Big Mann Entertainment Platform
Focus: MDE Integration & Existing Systems Verification

This test suite covers:
1. MDE Integration Backend (HIGH PRIORITY - NEW)
2. Existing Integrations Verification 
3. Core System Health
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
import sys
import os

# Configuration
BACKEND_URL = "https://music-rights-hub-2.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"mde_test_{int(time.time())}@bigmannentertainment.com"
TEST_PASSWORD = "SecureTestPass123!"

class MDEBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
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
        """Setup test user and authentication"""
        print("🔐 Setting up authentication...")
        
        try:
            # Try to register test user
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "MDE Test User",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }
            
            response = self.session.post(f"{self.backend_url}/auth/register", json=register_data)
            
            if response.status_code == 201:
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
    
    def test_mde_standards(self):
        """Test MDE Standards endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/mde/standards", params={"user_id": self.user_id})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "standards" in data:
                    standards_count = len(data["standards"])
                    recommended = data.get("recommended_standard")
                    self.log_result("MDE Standards", True, 
                                  f"Retrieved {standards_count} standards, recommended: {recommended}")
                else:
                    self.log_result("MDE Standards", False, error="Invalid response structure")
            else:
                self.log_result("MDE Standards", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Standards", False, error=str(e))
    
    def test_mde_metadata_submission(self):
        """Test MDE Metadata Submission endpoint"""
        try:
            metadata = {
                "title": "Test Track for MDE",
                "artist": "Test Artist",
                "album": "Test Album",
                "genre": ["Pop", "Electronic"],
                "duration_ms": 180000,
                "explicit": False,
                "contributors": [
                    {"name": "Test Artist", "role": "artist"},
                    {"name": "Test Producer", "role": "producer"}
                ],
                "rights_holders": [
                    {"name": "Big Mann Entertainment", "type": "label"}
                ],
                "language": "en",
                "label": "Big Mann Entertainment"
            }
            
            response = self.session.post(
                f"{self.backend_url}/mde/metadata/submit",
                json=metadata,
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    metadata_id = data.get("metadata_id")
                    mde_response = data.get("mde_response", {})
                    self.log_result("MDE Metadata Submission", True, 
                                  f"Submitted metadata ID: {metadata_id}, MDE ID: {mde_response.get('mde_id')}")
                    return metadata_id
                else:
                    self.log_result("MDE Metadata Submission", False, error=data.get("error", "Unknown error"))
            else:
                self.log_result("MDE Metadata Submission", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Metadata Submission", False, error=str(e))
        
        return None
    
    def test_mde_metadata_retrieval(self):
        """Test MDE Metadata Retrieval endpoint"""
        try:
            response = self.session.get(
                f"{self.backend_url}/mde/metadata",
                params={"user_id": self.user_id, "limit": 10, "offset": 0}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "metadata" in data:
                    metadata_count = len(data["metadata"])
                    total_count = data.get("total_count", 0)
                    self.log_result("MDE Metadata Retrieval", True, 
                                  f"Retrieved {metadata_count} metadata entries, total: {total_count}")
                else:
                    self.log_result("MDE Metadata Retrieval", False, error="Invalid response structure")
            else:
                self.log_result("MDE Metadata Retrieval", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Metadata Retrieval", False, error=str(e))
    
    def test_mde_metadata_validation(self, metadata_id=None):
        """Test MDE Metadata Validation endpoint"""
        if not metadata_id:
            # Use a sample metadata ID from the cache
            metadata_id = "sample_metadata_id"
        
        try:
            validation_data = {
                "standard": "ddex_ern"
            }
            
            response = self.session.post(
                f"{self.backend_url}/mde/metadata/{metadata_id}/validate",
                json=validation_data,
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    validation_result = data.get("validation_result", {})
                    status = validation_result.get("status")
                    score = validation_result.get("score")
                    self.log_result("MDE Metadata Validation", True, 
                                  f"Validation status: {status}, score: {score}")
                else:
                    self.log_result("MDE Metadata Validation", False, error=data.get("error", "Unknown error"))
            else:
                self.log_result("MDE Metadata Validation", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Metadata Validation", False, error=str(e))
    
    def test_mde_validations(self):
        """Test MDE Validations endpoint"""
        try:
            response = self.session.get(
                f"{self.backend_url}/mde/validations",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "validations" in data:
                    validations_count = len(data["validations"])
                    total_validations = data.get("total_validations", 0)
                    self.log_result("MDE Validations", True, 
                                  f"Retrieved {validations_count} validations, total: {total_validations}")
                else:
                    self.log_result("MDE Validations", False, error="Invalid response structure")
            else:
                self.log_result("MDE Validations", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Validations", False, error=str(e))
    
    def test_mde_quality_summary(self):
        """Test MDE Quality Summary endpoint"""
        try:
            response = self.session.get(
                f"{self.backend_url}/mde/quality/summary",
                params={"user_id": self.user_id, "threshold": 80.0}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "summary" in data:
                    summary = data["summary"]
                    total_entries = summary.get("total_entries", 0)
                    avg_quality = summary.get("average_quality", 0)
                    quality_rate = summary.get("quality_rate", 0)
                    self.log_result("MDE Quality Summary", True, 
                                  f"Total entries: {total_entries}, avg quality: {avg_quality}, quality rate: {quality_rate}%")
                else:
                    self.log_result("MDE Quality Summary", False, error="Invalid response structure")
            else:
                self.log_result("MDE Quality Summary", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Quality Summary", False, error=str(e))
    
    def test_mde_analytics(self):
        """Test MDE Analytics endpoint"""
        try:
            response = self.session.get(
                f"{self.backend_url}/mde/analytics",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "analytics" in data:
                    analytics = data["analytics"]
                    overview = analytics.get("overview", {})
                    total_metadata = overview.get("total_metadata_entries", 0)
                    avg_quality = overview.get("average_quality_score", 0)
                    self.log_result("MDE Analytics", True, 
                                  f"Total metadata: {total_metadata}, avg quality score: {avg_quality}")
                else:
                    self.log_result("MDE Analytics", False, error="Invalid response structure")
            else:
                self.log_result("MDE Analytics", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Analytics", False, error=str(e))
    
    def test_mde_integration_status(self):
        """Test MDE Integration Status endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/mde/integration/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "integration_status" in data:
                    status = data["integration_status"]
                    connected = status.get("mde_connected", False)
                    capabilities = len(status.get("capabilities", []))
                    standards = len(status.get("supported_standards", []))
                    self.log_result("MDE Integration Status", True, 
                                  f"Connected: {connected}, capabilities: {capabilities}, standards: {standards}")
                else:
                    self.log_result("MDE Integration Status", False, error="Invalid response structure")
            else:
                self.log_result("MDE Integration Status", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("MDE Integration Status", False, error=str(e))
    
    def test_dao_governance_integration(self):
        """Test DAO Governance blockchain integration"""
        try:
            response = self.session.get(f"{self.backend_url}/dao/governance/status")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("DAO Governance Integration", True, 
                              f"DAO status retrieved: {data.get('status', 'unknown')}")
            elif response.status_code == 404:
                self.log_result("DAO Governance Integration", False, 
                              error="DAO endpoints not implemented")
            else:
                self.log_result("DAO Governance Integration", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("DAO Governance Integration", False, error=str(e))
    
    def test_premium_features_integration(self):
        """Test Premium Features integration"""
        try:
            response = self.session.get(f"{self.backend_url}/premium/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Premium Features Integration", True, 
                              f"Premium dashboard accessible")
            elif response.status_code == 403:
                self.log_result("Premium Features Integration", True, 
                              f"Premium features properly secured (403 expected)")
            elif response.status_code == 404:
                self.log_result("Premium Features Integration", False, 
                              error="Premium endpoints not implemented")
            else:
                self.log_result("Premium Features Integration", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Premium Features Integration", False, error=str(e))
    
    def test_mlc_integration(self):
        """Test MLC (Mechanical Licensing Collective) integration"""
        try:
            response = self.session.get(f"{self.backend_url}/mlc/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("MLC Integration", True, 
                              f"MLC dashboard accessible")
            elif response.status_code == 403:
                self.log_result("MLC Integration", True, 
                              f"MLC properly secured (403 expected)")
            elif response.status_code == 404:
                self.log_result("MLC Integration", False, 
                              error="MLC endpoints not implemented")
            else:
                self.log_result("MLC Integration", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("MLC Integration", False, error=str(e))
    
    def test_distribution_platforms(self):
        """Test Distribution Platforms endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/distribution/platforms")
            
            if response.status_code == 200:
                data = response.json()
                if "platforms" in data:
                    platform_count = len(data["platforms"])
                    self.log_result("Distribution Platforms", True, 
                                  f"Retrieved {platform_count} distribution platforms")
                else:
                    self.log_result("Distribution Platforms", False, error="Invalid response structure")
            else:
                self.log_result("Distribution Platforms", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Distribution Platforms", False, error=str(e))
    
    def test_server_health(self):
        """Test server health and basic connectivity"""
        try:
            # Test root endpoint
            response = self.session.get(self.backend_url.replace("/api", ""))
            
            if response.status_code == 200:
                self.log_result("Server Health", True, "Server is responding")
            else:
                self.log_result("Server Health", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Server Health", False, error=str(e))
    
    def test_database_connectivity(self):
        """Test database connectivity through user endpoints"""
        try:
            # Test user profile endpoint (requires auth)
            response = self.session.get(f"{self.backend_url}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.log_result("Database Connectivity", True, 
                                  f"Database accessible, user ID: {data['id']}")
                else:
                    self.log_result("Database Connectivity", False, error="Invalid user data")
            elif response.status_code == 401:
                self.log_result("Database Connectivity", True, 
                              "Database accessible (auth required as expected)")
            else:
                self.log_result("Database Connectivity", False, 
                              error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Database Connectivity", False, error=str(e))
    
    def test_authentication_system(self):
        """Test authentication system functionality"""
        try:
            # Test protected endpoint without auth
            session_no_auth = requests.Session()
            response = session_no_auth.get(f"{self.backend_url}/auth/me")
            
            if response.status_code == 401:
                self.log_result("Authentication System", True, 
                              "Authentication properly enforced (401 for unauth requests)")
            else:
                self.log_result("Authentication System", False, 
                              error=f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Authentication System", False, error=str(e))
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🎯 COMPREHENSIVE BACKEND TESTING FOR MDE INTEGRATION & EXISTING FEATURES")
        print("=" * 80)
        print()
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with authenticated tests.")
            return
        
        print("🎵 TESTING MDE INTEGRATION ENDPOINTS (HIGH PRIORITY)")
        print("-" * 50)
        
        # MDE Integration Tests (HIGH PRIORITY)
        self.test_mde_standards()
        metadata_id = self.test_mde_metadata_submission()
        self.test_mde_metadata_retrieval()
        self.test_mde_metadata_validation(metadata_id)
        self.test_mde_validations()
        self.test_mde_quality_summary()
        self.test_mde_analytics()
        self.test_mde_integration_status()
        
        print("🔗 TESTING EXISTING INTEGRATIONS")
        print("-" * 50)
        
        # Existing Integrations Tests
        self.test_dao_governance_integration()
        self.test_premium_features_integration()
        self.test_mlc_integration()
        self.test_distribution_platforms()
        
        print("🏥 TESTING CORE SYSTEM HEALTH")
        print("-" * 50)
        
        # Core System Health Tests
        self.test_server_health()
        self.test_database_connectivity()
        self.test_authentication_system()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
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
        mde_tests = [r for r in self.test_results if "MDE" in r["test"]]
        integration_tests = [r for r in self.test_results if any(x in r["test"] for x in ["DAO", "Premium", "MLC", "Distribution"])]
        health_tests = [r for r in self.test_results if any(x in r["test"] for x in ["Server", "Database", "Authentication"])]
        
        print("🎵 MDE INTEGRATION RESULTS:")
        mde_passed = len([r for r in mde_tests if r["success"]])
        print(f"   {mde_passed}/{len(mde_tests)} MDE tests passed ({(mde_passed/len(mde_tests)*100):.1f}%)")
        
        print("🔗 EXISTING INTEGRATIONS RESULTS:")
        int_passed = len([r for r in integration_tests if r["success"]])
        print(f"   {int_passed}/{len(integration_tests)} integration tests passed ({(int_passed/len(integration_tests)*100):.1f}%)")
        
        print("🏥 CORE SYSTEM HEALTH RESULTS:")
        health_passed = len([r for r in health_tests if r["success"]])
        print(f"   {health_passed}/{len(health_tests)} health tests passed ({(health_passed/len(health_tests)*100):.1f}%)")
        
        print("\n❌ FAILED TESTS:")
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            for result in failed_results:
                print(f"   • {result['test']}: {result['error']}")
        else:
            print("   None! All tests passed! 🎉")
        
        print("\n✅ CRITICAL FINDINGS:")
        
        # MDE Integration Status
        mde_success_rate = (mde_passed / len(mde_tests)) * 100 if mde_tests else 0
        if mde_success_rate >= 80:
            print("   • MDE Integration: EXCELLENT - Ready for production")
        elif mde_success_rate >= 60:
            print("   • MDE Integration: GOOD - Minor issues to resolve")
        else:
            print("   • MDE Integration: NEEDS WORK - Major issues detected")
        
        # Overall System Status
        if success_rate >= 90:
            print("   • Overall System: PRODUCTION READY")
        elif success_rate >= 75:
            print("   • Overall System: MOSTLY READY - Minor fixes needed")
        else:
            print("   • Overall System: REQUIRES ATTENTION - Multiple issues detected")
        
        print("\n🎯 RECOMMENDATIONS:")
        if failed_tests == 0:
            print("   • All systems operational - proceed with deployment")
        else:
            print("   • Address failed tests before production deployment")
            print("   • Focus on MDE integration issues if any")
            print("   • Verify authentication and database connectivity")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = MDEBackendTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()