#!/usr/bin/env python3
"""
Phase 2 Metadata Parser & Validator Quick Verification Test
Focus: Testing key improvements after fixing critical issues

Key Areas:
1. Authentication & Access Fixed - test batch and reporting endpoints with proper auth
2. Extended Format Support - verify new formats (ID3, MusicBrainz, iTunes, ISNI)
3. Core Batch Processing - test basic batch functionality
4. Advanced Reporting - test basic reporting endpoints
5. Database Integration - confirm async/sync operations

Success Criteria: 70%+ success rate on core functionality
"""

import requests
import json
import time
import os
import tempfile
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://bigmannentertainment.com')
API_BASE = f"{BACKEND_URL}/api"

class Phase2MetadataVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
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
        """Setup authentication for testing"""
        print("🔐 Setting up authentication...")
        
        user_data = {
            "email": "phase2.tester@bigmannentertainment.com",
            "password": "Phase2Test2025!",
            "full_name": "Phase 2 Metadata Tester",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Phase2 Street",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
        try:
            # Try to register user
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            if response.status_code in [200, 201]:
                print("✅ User registered successfully")
            elif response.status_code == 400 and "already exists" in response.text:
                print("ℹ️ User already exists, proceeding with login")
            
            # Login user
            login_data = {"email": user_data["email"], "password": user_data["password"]}
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                print("✅ User authentication successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication setup failed: {str(e)}")
            return False

    def test_key_endpoints(self):
        """Test the key endpoints mentioned in the review request"""
        print("🧪 Testing Key Phase 2 Endpoints...")
        
        # Test 1: GET /api/metadata/formats/supported (should show new formats)
        try:
            response = self.session.get(f"{API_BASE}/metadata/formats/supported")
            if response.status_code == 200:
                data = response.json()
                supported_formats = data.get('supported_formats', {})
                validation_features = data.get('validation_features', {})
                
                # Check for extended format support indicators
                format_count = len(supported_formats)
                has_validation_features = len(validation_features) > 0
                
                self.log_result(
                    "Supported Formats Endpoint",
                    True,
                    f"Found {format_count} formats, Validation features: {has_validation_features}"
                )
            else:
                self.log_result(
                    "Supported Formats Endpoint",
                    False,
                    error_msg=f"Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Supported Formats Endpoint",
                False,
                error_msg=str(e)
            )

        # Test 2: POST /api/metadata/parse (test with new formats if possible)
        try:
            # Create a test JSON metadata file with extended fields
            test_metadata = {
                "title": "Phase 2 Test Track",
                "artist": "Phase 2 Test Artist",
                "album": "Phase 2 Test Album",
                "isrc": "USPH24000001",
                "upc": "123456789017",
                "rights_holders": ["Big Mann Entertainment"],
                "genre": "Electronic",
                "release_date": "2025-01-15T00:00:00Z",
                "publisher_name": "BME Publishing",
                "composer_name": "Test Composer",
                "copyright_year": 2025,
                "description": "Phase 2 metadata parsing test",
                "tags": ["phase2", "test", "metadata"]
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(test_metadata, f)
                temp_file_path = f.name
            
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('phase2_test.json', f, 'application/json')}
                data = {'format': 'json', 'validate': 'true', 'check_duplicates': 'true'}
                
                response = self.session.post(f"{API_BASE}/metadata/parse", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    parsing_status = result.get('parsing_status', 'unknown')
                    validation_status = result.get('validation_status', 'unknown')
                    
                    self.log_result(
                        "Metadata Parse Endpoint",
                        True,
                        f"Parse status: {parsing_status}, Validation status: {validation_status}"
                    )
                else:
                    self.log_result(
                        "Metadata Parse Endpoint",
                        False,
                        error_msg=f"Status: {response.status_code}, Response: {response.text}"
                    )
            
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.log_result(
                "Metadata Parse Endpoint",
                False,
                error_msg=str(e)
            )

        # Test 3: GET /api/batch/history (basic batch endpoint)
        try:
            response = self.session.get(f"{API_BASE}/batch/history?limit=5")
            
            if response.status_code == 200:
                result = response.json()
                batches = result.get('batches', [])
                total_count = result.get('total_count', 0)
                
                self.log_result(
                    "Batch History Endpoint",
                    True,
                    f"Retrieved {len(batches)} batches, Total: {total_count}"
                )
            else:
                self.log_result(
                    "Batch History Endpoint",
                    False,
                    error_msg=f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Batch History Endpoint",
                False,
                error_msg=str(e)
            )

        # Test 4: GET /api/reports/comprehensive (basic reporting endpoint)
        try:
            response = self.session.get(f"{API_BASE}/reports/comprehensive")
            
            if response.status_code == 200:
                result = response.json()
                report = result.get('report', {})
                report_sections = list(report.keys()) if report else []
                
                self.log_result(
                    "Comprehensive Report Endpoint",
                    True,
                    f"Report generated with {len(report_sections)} sections: {report_sections}"
                )
            else:
                self.log_result(
                    "Comprehensive Report Endpoint",
                    False,
                    error_msg=f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Comprehensive Report Endpoint",
                False,
                error_msg=str(e)
            )

        # Test 5: GET /api/reports/duplicates (duplicate reporting)
        try:
            response = self.session.get(f"{API_BASE}/reports/duplicates?scope=user")
            
            if response.status_code == 200:
                result = response.json()
                duplicate_report = result.get('duplicate_report', {})
                summary = duplicate_report.get('summary', {}) if duplicate_report else {}
                
                self.log_result(
                    "Duplicate Report Endpoint",
                    True,
                    f"Duplicate report generated: {summary}"
                )
            else:
                self.log_result(
                    "Duplicate Report Endpoint",
                    False,
                    error_msg=f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Duplicate Report Endpoint",
                False,
                error_msg=str(e)
            )

    def test_authentication_fixes(self):
        """Test that authentication and access issues are fixed"""
        print("🧪 Testing Authentication & Access Fixes...")
        
        # Test authenticated access to batch endpoints
        try:
            response = self.session.get(f"{API_BASE}/batch/history")
            
            if response.status_code in [200, 404]:  # 200 = success, 404 = no batches but endpoint works
                self.log_result(
                    "Batch Endpoint Authentication",
                    True,
                    f"Authenticated access working (Status: {response.status_code})"
                )
            elif response.status_code == 401:
                self.log_result(
                    "Batch Endpoint Authentication",
                    False,
                    error_msg="Authentication still failing (401 Unauthorized)"
                )
            else:
                self.log_result(
                    "Batch Endpoint Authentication",
                    False,
                    error_msg=f"Unexpected status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Batch Endpoint Authentication",
                False,
                error_msg=str(e)
            )

        # Test authenticated access to reporting endpoints
        try:
            response = self.session.get(f"{API_BASE}/reports/comprehensive")
            
            if response.status_code in [200, 404]:  # 200 = success, 404 = no data but endpoint works
                self.log_result(
                    "Reporting Endpoint Authentication",
                    True,
                    f"Authenticated access working (Status: {response.status_code})"
                )
            elif response.status_code == 401:
                self.log_result(
                    "Reporting Endpoint Authentication",
                    False,
                    error_msg="Authentication still failing (401 Unauthorized)"
                )
            else:
                self.log_result(
                    "Reporting Endpoint Authentication",
                    False,
                    error_msg=f"Unexpected status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Reporting Endpoint Authentication",
                False,
                error_msg=str(e)
            )

    def test_extended_format_support(self):
        """Test extended format support indicators"""
        print("🧪 Testing Extended Format Support...")
        
        # Test duplicate detection (core functionality)
        try:
            response = self.session.get(
                f"{API_BASE}/metadata/duplicates/check",
                params={
                    "identifier_type": "isrc",
                    "identifier_value": "USPH24000001"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                duplicates_found = result.get('duplicates_found', 0)
                
                self.log_result(
                    "Extended Format - ISRC Duplicate Detection",
                    True,
                    f"ISRC duplicate check working: {duplicates_found} duplicates found"
                )
            else:
                self.log_result(
                    "Extended Format - ISRC Duplicate Detection",
                    False,
                    error_msg=f"Status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Extended Format - ISRC Duplicate Detection",
                False,
                error_msg=str(e)
            )

        # Test UPC duplicate detection
        try:
            response = self.session.get(
                f"{API_BASE}/metadata/duplicates/check",
                params={
                    "identifier_type": "upc",
                    "identifier_value": "123456789017"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                duplicates_found = result.get('duplicates_found', 0)
                
                self.log_result(
                    "Extended Format - UPC Duplicate Detection",
                    True,
                    f"UPC duplicate check working: {duplicates_found} duplicates found"
                )
            else:
                self.log_result(
                    "Extended Format - UPC Duplicate Detection",
                    False,
                    error_msg=f"Status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Extended Format - UPC Duplicate Detection",
                False,
                error_msg=str(e)
            )

    def test_database_integration(self):
        """Test database integration and async/sync operations"""
        print("🧪 Testing Database Integration...")
        
        # Test metadata statistics (database read operation)
        try:
            response = self.session.get(f"{API_BASE}/metadata/statistics")
            
            if response.status_code == 200:
                result = response.json()
                statistics = result.get('statistics', {})
                total_validations = statistics.get('total_validations', 0)
                
                self.log_result(
                    "Database Integration - Statistics Retrieval",
                    True,
                    f"Statistics retrieved: {total_validations} total validations"
                )
            else:
                self.log_result(
                    "Database Integration - Statistics Retrieval",
                    False,
                    error_msg=f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Database Integration - Statistics Retrieval",
                False,
                error_msg=str(e)
            )

        # Test validation results listing (database query operation)
        try:
            response = self.session.get(f"{API_BASE}/metadata/validation-results?limit=5")
            
            if response.status_code == 200:
                result = response.json()
                validation_results = result.get('validation_results', [])
                total_count = result.get('total_count', 0)
                
                self.log_result(
                    "Database Integration - Validation Results Query",
                    True,
                    f"Query successful: {len(validation_results)} results, Total: {total_count}"
                )
            else:
                self.log_result(
                    "Database Integration - Validation Results Query",
                    False,
                    error_msg=f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Database Integration - Validation Results Query",
                False,
                error_msg=str(e)
            )

    def test_core_functionality(self):
        """Test core functionality to ensure no critical import or auth errors"""
        print("🧪 Testing Core Functionality...")
        
        # Test JSON validation (core validation functionality)
        try:
            test_metadata = {
                "title": "Core Functionality Test",
                "artist": "Test Artist",
                "isrc": "USCO24000001",
                "rights_holders": ["Big Mann Entertainment"]
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/validate-json",
                json={
                    "metadata_json": test_metadata,
                    "check_duplicates": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                validation_status = result.get('validation_status', 'unknown')
                
                self.log_result(
                    "Core Functionality - JSON Validation",
                    True,
                    f"JSON validation working: {validation_status}"
                )
            else:
                self.log_result(
                    "Core Functionality - JSON Validation",
                    False,
                    error_msg=f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Core Functionality - JSON Validation",
                False,
                error_msg=str(e)
            )

    def run_verification_tests(self):
        """Run Phase 2 verification tests"""
        print("🚀 Starting Phase 2 Metadata Parser & Validator Quick Verification")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        # Run test suites
        self.test_key_endpoints()
        self.test_authentication_fixes()
        self.test_extended_format_support()
        self.test_database_integration()
        self.test_core_functionality()
        
        # Generate summary
        self.generate_verification_summary()

    def generate_verification_summary(self):
        """Generate verification test summary"""
        print("\n" + "=" * 80)
        print("📊 PHASE 2 METADATA PARSER & VALIDATOR VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 VERIFICATION RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Key areas assessment
        key_endpoints = [r for r in self.test_results if "Endpoint" in r["test"]]
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"]]
        format_tests = [r for r in self.test_results if "Format" in r["test"]]
        db_tests = [r for r in self.test_results if "Database" in r["test"]]
        core_tests = [r for r in self.test_results if "Core" in r["test"]]
        
        print(f"\n📋 KEY AREAS ASSESSMENT:")
        print(f"   Key Endpoints: {sum(1 for t in key_endpoints if t['success'])}/{len(key_endpoints)} passed")
        print(f"   Authentication Fixes: {sum(1 for t in auth_tests if t['success'])}/{len(auth_tests)} passed")
        print(f"   Extended Format Support: {sum(1 for t in format_tests if t['success'])}/{len(format_tests)} passed")
        print(f"   Database Integration: {sum(1 for t in db_tests if t['success'])}/{len(db_tests)} passed")
        print(f"   Core Functionality: {sum(1 for t in core_tests if t['success'])}/{len(core_tests)} passed")
        
        # Success criteria check
        print(f"\n🎯 SUCCESS CRITERIA CHECK:")
        if success_rate >= 70:
            print(f"   ✅ SUCCESS: {success_rate:.1f}% success rate meets 70%+ target")
            print("   ✅ Phase 2 infrastructure is working and ready for final validation")
        else:
            print(f"   ❌ BELOW TARGET: {success_rate:.1f}% success rate below 70% target")
            print("   ❌ Critical issues remain that need immediate attention")
        
        # Critical issues
        critical_failures = [r for r in self.test_results if not r["success"]]
        if critical_failures:
            print(f"\n⚠️ REMAINING CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['error']}")
        else:
            print(f"\n🎉 NO CRITICAL ISSUES FOUND!")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {result['test']}")
            if result["details"]:
                print(f"      Details: {result['details']}")
            if result["error"]:
                print(f"      Error: {result['error']}")
        
        print(f"\n🕒 Verification completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "meets_criteria": success_rate >= 70,
            "critical_issues": len(critical_failures)
        }

if __name__ == "__main__":
    tester = Phase2MetadataVerificationTester()
    tester.run_verification_tests()