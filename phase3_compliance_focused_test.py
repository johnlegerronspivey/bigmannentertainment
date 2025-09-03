#!/usr/bin/env python3
"""
Phase 3 Rights & Compliance Focused Test - Test compliance checking with created content
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
import uuid

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://bigmannentertainment.com')
API_BASE = f"{BACKEND_URL}/api"

class ComplianceFocusedTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.test_results = []
        self.test_content_id = None
        self.test_isrc = None
        
    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def setup_authentication(self):
        """Setup user authentication"""
        print("🔐 Setting up authentication...")
        
        try:
            # Login with existing user
            login_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": "rights.tester@bigmannentertainment.com",
                "password": "RightsTest2025!"
            })
            
            if login_response.status_code == 200:
                auth_data = login_response.json()
                if 'access_token' in auth_data:
                    self.user_token = auth_data['access_token']
                    self.session.headers.update({'Authorization': f'Bearer {self.user_token}'})
                    self.log_result("User Authentication", True, "User logged in successfully")
                    return True
                else:
                    self.log_result("User Authentication", False, "", "No access token in response")
                    return False
            else:
                self.log_result("User Authentication", False, "", f"Login failed: {login_response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Setup", False, "", str(e))
            return False

    def create_test_rights_ownership(self):
        """Create test rights ownership for compliance testing"""
        print("\n📝 Creating test rights ownership...")
        
        # Generate test data
        self.test_content_id = f"compliance_test_{uuid.uuid4().hex[:8]}"
        self.test_isrc = f"USQZ9H825{str(uuid.uuid4().hex[:5]).upper()}"
        
        try:
            rights_data = {
                "content_id": self.test_content_id,
                "isrc": self.test_isrc,
                "title": "Big Mann Entertainment Compliance Test Track",
                "territory_rights": [
                    {
                        "territory": "US",
                        "rights_holder": "Big Mann Entertainment",
                        "rights_percentage": 100.0,
                        "effective_date": datetime.now().isoformat(),
                        "is_exclusive": True,
                        "contact_info": {
                            "email": "rights@bigmannentertainment.com",
                            "phone": "334-669-8638"
                        }
                    },
                    {
                        "territory": "EU",
                        "rights_holder": "Big Mann Entertainment Europe",
                        "rights_percentage": 75.0,
                        "effective_date": datetime.now().isoformat(),
                        "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
                        "is_exclusive": False
                    }
                ],
                "usage_rights": [
                    {
                        "usage_type": "streaming",
                        "territories": ["US", "EU"],
                        "rights_holder": "Big Mann Entertainment",
                        "effective_date": datetime.now().isoformat(),
                        "is_exclusive": False,
                        "royalty_rate": 0.006
                    },
                    {
                        "usage_type": "sync",
                        "territories": ["GLOBAL"],
                        "rights_holder": "Big Mann Entertainment Publishing",
                        "effective_date": datetime.now().isoformat(),
                        "is_exclusive": True,
                        "royalty_rate": 2500.0
                    }
                ],
                "master_owner": "Big Mann Entertainment",
                "publishing_owner": "Big Mann Entertainment Publishing",
                "created_by": "compliance_tester"
            }
            
            response = self.session.post(f"{API_BASE}/rights/ownership", json=rights_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'content_id' in data:
                    created_content_id = data['content_id']
                    self.log_result("Test Rights Ownership Creation", True, 
                                  f"Created rights record for content: {created_content_id}")
                    return True
                else:
                    self.log_result("Test Rights Ownership Creation", False, 
                                  "Response missing success flag or content_id")
                    return False
            else:
                self.log_result("Test Rights Ownership Creation", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test Rights Ownership Creation", False, "", str(e))
            return False

    def test_comprehensive_compliance_check(self):
        """Test comprehensive compliance checking"""
        print("\n🔍 Testing Comprehensive Compliance Check...")
        
        try:
            compliance_data = {
                "content_id": self.test_content_id,
                "isrc": self.test_isrc,
                "territories": ["US", "EU"],
                "usage_types": ["streaming", "sync"],
                "strict_mode": False
            }
            
            response = self.session.post(f"{API_BASE}/rights/check-compliance", data=compliance_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'compliance_result' in data:
                    compliance_result = data['compliance_result']
                    summary = data.get('summary', {})
                    
                    # Verify compliance result structure
                    required_fields = ['overall_status', 'territory_compliance', 'usage_compliance', 'check_date']
                    if all(field in compliance_result for field in required_fields):
                        self.log_result("Comprehensive Compliance Check", True, 
                                      f"Compliance check completed successfully")
                        
                        # Check overall status
                        overall_status = compliance_result.get('overall_status')
                        self.log_result("Compliance Status", True, 
                                      f"Overall status: {overall_status}")
                        
                        # Check territory compliance
                        territory_compliance = compliance_result.get('territory_compliance', {})
                        self.log_result("Territory Compliance", True, 
                                      f"Territory compliance: {territory_compliance}")
                        
                        # Check usage compliance
                        usage_compliance = compliance_result.get('usage_compliance', {})
                        self.log_result("Usage Compliance", True, 
                                      f"Usage compliance: {usage_compliance}")
                        
                        # Check summary data
                        if 'processing_time' in summary:
                            self.log_result("Processing Time", True, 
                                          f"Processing time: {summary.get('processing_time')}s")
                        
                        return True
                        
                    else:
                        missing_fields = [f for f in required_fields if f not in compliance_result]
                        self.log_result("Comprehensive Compliance Check", False, 
                                      f"Missing required fields: {missing_fields}")
                        return False
                    
                else:
                    self.log_result("Comprehensive Compliance Check", False, 
                                  "Response missing success flag or compliance_result data")
                    return False
            else:
                self.log_result("Comprehensive Compliance Check", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        
        except Exception as e:
            self.log_result("Comprehensive Compliance Check", False, "", str(e))
            return False

    def test_quick_compliance_check(self):
        """Test quick compliance check"""
        print("\n⚡ Testing Quick Compliance Check...")
        
        try:
            quick_check_data = {
                "isrc": self.test_isrc,
                "territory": "US",
                "usage_type": "streaming"
            }
            
            response = self.session.post(f"{API_BASE}/rights/quick-check", data=quick_check_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'compliance_status' in data:
                    compliance_status = data.get('compliance_status')
                    is_compliant = data.get('is_compliant')
                    summary_message = data.get('summary_message')
                    
                    if (compliance_status in ['compliant', 'non_compliant', 'warning', 'unknown'] and
                        isinstance(is_compliant, bool) and
                        summary_message and self.test_isrc in summary_message):
                        
                        self.log_result("Quick Compliance Check", True, 
                                      f"Quick check result: {compliance_status}, compliant: {is_compliant}")
                        self.log_result("Quick Check Summary", True, 
                                      f"Summary: {summary_message}")
                        return True
                    else:
                        self.log_result("Quick Compliance Check", False, 
                                      f"Invalid quick check response structure")
                        return False
                else:
                    self.log_result("Quick Compliance Check", False, 
                                  "Response missing success flag or compliance_status")
                    return False
            else:
                self.log_result("Quick Compliance Check", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        
        except Exception as e:
            self.log_result("Quick Compliance Check", False, "", str(e))
            return False

    def test_compliance_history_after_checks(self):
        """Test compliance history after running checks"""
        print("\n📊 Testing Compliance History After Checks...")
        
        try:
            response = self.session.get(f"{API_BASE}/rights/compliance-history/{self.test_content_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'compliance_history' in data:
                    compliance_history = data['compliance_history']
                    total_count = data.get('total_count', 0)
                    
                    # Should have at least one compliance check from previous tests
                    if total_count >= 1:
                        self.log_result("Compliance History After Checks", True, 
                                      f"Found {total_count} compliance check(s) in history")
                        
                        if compliance_history and len(compliance_history) > 0:
                            latest_check = compliance_history[0]
                            if ('check_date' in latest_check and 
                                'overall_status' in latest_check and
                                latest_check.get('content_id') == self.test_content_id):
                                
                                self.log_result("Compliance History Structure", True, 
                                              f"Latest check status: {latest_check.get('overall_status')}")
                                return True
                            else:
                                self.log_result("Compliance History Structure", False, 
                                              f"Invalid compliance history entry structure")
                                return False
                        else:
                            self.log_result("Compliance History Data", False, 
                                          f"No compliance history entries despite total_count={total_count}")
                            return False
                    else:
                        self.log_result("Compliance History After Checks", False, 
                                      f"Expected at least 1 compliance check, got {total_count}")
                        return False
                else:
                    self.log_result("Compliance History After Checks", False, 
                                  "Response missing success flag or compliance_history data")
                    return False
            else:
                self.log_result("Compliance History After Checks", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        
        except Exception as e:
            self.log_result("Compliance History After Checks", False, "", str(e))
            return False

    def run_focused_test(self):
        """Run focused compliance testing"""
        print("🎯 PHASE 3 COMPLIANCE FOCUSED TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with testing.")
            return
        
        # Create test rights ownership
        if not self.create_test_rights_ownership():
            print("❌ Test rights ownership creation failed. Cannot proceed with compliance testing.")
            return
        
        # Run compliance tests
        self.test_comprehensive_compliance_check()
        self.test_quick_compliance_check()
        self.test_compliance_history_after_checks()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate focused test report"""
        print("\n" + "=" * 60)
        print("📊 COMPLIANCE FOCUSED TESTING FINAL REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}")
                    if result['error']:
                        print(f"    Error: {result['error']}")
            print()
        
        # Overall assessment
        print()
        if success_rate >= 90:
            print("🎉 COMPLIANCE SYSTEM: FULLY OPERATIONAL")
            print("   All compliance features working correctly")
        elif success_rate >= 70:
            print("⚠️  COMPLIANCE SYSTEM: MOSTLY OPERATIONAL")
            print("   Core compliance features working with minor issues")
        else:
            print("❌ COMPLIANCE SYSTEM: NEEDS ATTENTION")
            print("   Compliance functionality has significant issues")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = ComplianceFocusedTester()
    tester.run_focused_test()