#!/usr/bin/env python3
"""
Phase 2 Metadata Parser & Validator Backend Testing
Big Mann Entertainment Platform - Production Readiness Verification

Tests the Phase 2 Enhanced Metadata Parser & Validator system
Target: 85%+ overall success rate across all Phase 2 features
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://mediacloud-bme.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class MetadataPhase2Tester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
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
        """Setup user authentication"""
        print("🔐 Setting up authentication...")
        
        # Try to register a test user
        user_data = {
            "email": "phase2.test@bigmannentertainment.com",
            "password": "Phase2Test2025!",
            "full_name": "Phase 2 Tester",
            "business_name": "Big Mann Entertainment Testing",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "1314 Lincoln Heights Street",
            "city": "Alexander City",
            "state_province": "Alabama",
            "postal_code": "35010",
            "country": "United States"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            if response.status_code == 201:
                result = response.json()
                self.user_token = result.get('access_token')
                print(f"✅ User registered and authenticated")
                return True
            elif response.status_code == 400:
                # User might already exist, try login
                login_data = {
                    "email": "phase2.test@bigmannentertainment.com",
                    "password": "Phase2Test2025!"
                }
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    result = response.json()
                    self.user_token = result.get('access_token')
                    print(f"✅ User logged in successfully")
                    return True
        except Exception as e:
            print(f"❌ Authentication setup failed: {str(e)}")
            
        return False

    def test_supported_formats_extended(self):
        """Test 1: Extended Format Support - Verify Phase 2 formats"""
        test_name = "Extended Format Support Verification"
        
        try:
            response = self.session.get(f"{API_BASE}/metadata/formats/supported")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    formats = result.get('supported_formats', {})
                    validation_features = result.get('validation_features', {})
                    
                    # Check for required formats
                    expected_formats = ['ddex_ern', 'mead', 'json', 'csv']
                    found_formats = list(formats.keys())
                    
                    formats_found = all(fmt in found_formats for fmt in expected_formats)
                    
                    # Check validation features
                    required_features = [
                        'schema_validation', 'required_fields', 'format_validation',
                        'duplicate_detection', 'business_rules'
                    ]
                    features_found = all(feature in validation_features for feature in required_features)
                    
                    total_formats = len(found_formats)
                    
                    success = formats_found and features_found and total_formats >= 4
                    
                    self.log_result(
                        test_name, 
                        success,
                        f"Found {total_formats} formats with complete validation features",
                        "" if success else "Missing required formats or validation features"
                    )
                    return success
                    
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def test_metadata_parsing_json(self):
        """Test 2: Enhanced Metadata Processing - JSON Validation"""
        test_name = "Enhanced JSON Metadata Validation"
        
        if not self.user_token:
            self.log_result(test_name, False, "", "No authentication token available")
            return False
            
        try:
            # Comprehensive metadata for validation
            metadata_json = {
                "title": "Phase 2 Enhanced Test Track",
                "artist": "Big Mann Entertainment",
                "album": "Metadata Validation Suite",
                "isrc": "US-QZ9-25-67890",
                "upc": "860004340212",
                "release_date": "2025-01-15T00:00:00Z",
                "genre": "Hip-Hop",
                "duration": "3:45",
                "track_number": 1,
                "total_tracks": 12,
                "rights_holders": [
                    "Big Mann Entertainment",
                    "John LeGerron Spivey"
                ],
                "publisher_name": "Big Mann Publishing",
                "composer_name": "John LeGerron Spivey",
                "copyright_year": 2025,
                "copyright_owner": "Big Mann Entertainment",
                "description": "Phase 2 comprehensive metadata validation test"
            }
            
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "metadata_json": metadata_json,
                "check_duplicates": True
            }
            
            response = self.session.post(
                f"{API_BASE}/metadata/validate-json",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    validation_status = result.get('validation_status')
                    validation_errors = result.get('validation_errors', [])
                    validation_warnings = result.get('validation_warnings', [])
                    schema_valid = result.get('schema_valid', False)
                    processing_time = result.get('processing_time', 0)
                    
                    # Enhanced validation should pass with comprehensive metadata
                    is_valid = validation_status in ['VALID', 'WARNING']
                    
                    success = is_valid and schema_valid
                    
                    self.log_result(
                        test_name,
                        success,
                        f"Status: {validation_status}, Errors: {len(validation_errors)}, Warnings: {len(validation_warnings)}, Time: {processing_time}ms",
                        "" if success else f"Validation failed: {validation_errors[:2] if validation_errors else 'Schema invalid'}"
                    )
                    return success
            else:
                self.log_result(test_name, False, "", f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def test_duplicate_detection(self):
        """Test 3: Advanced Duplicate Detection"""
        test_name = "Advanced Duplicate Detection"
        
        if not self.user_token:
            self.log_result(test_name, False, "", "No authentication token available")
            return False
            
        try:
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            # Test ISRC duplicate detection
            test_isrc = "US-QZ9-25-TEST1"
            
            response = self.session.get(
                f"{API_BASE}/metadata/duplicates/check",
                params={
                    "identifier_type": "isrc",
                    "identifier_value": test_isrc
                },
                headers=headers
            )
            
            isrc_success = False
            if response.status_code == 200:
                result = response.json()
                isrc_success = result.get('success', False)
            
            # Test UPC duplicate detection
            test_upc = "860004340299"
            
            response = self.session.get(
                f"{API_BASE}/metadata/duplicates/check",
                params={
                    "identifier_type": "upc",
                    "identifier_value": test_upc
                },
                headers=headers
            )
            
            upc_success = False
            if response.status_code == 200:
                result = response.json()
                upc_success = result.get('success', False)
            
            success = isrc_success and upc_success
            
            self.log_result(
                test_name,
                success,
                f"ISRC check: {'✅' if isrc_success else '❌'}, UPC check: {'✅' if upc_success else '❌'}",
                "" if success else "One or both duplicate detection checks failed"
            )
            return success
            
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def test_batch_processing_simulation(self):
        """Test 4: Batch Processing System - Multi-file processing"""
        test_name = "Batch Processing System"
        
        if not self.user_token:
            self.log_result(test_name, False, "", "No authentication token available")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.user_token}'}
            
            batch_results = []
            batch_start_time = time.time()
            
            # Simulate batch processing by uploading multiple files
            for i in range(3):
                metadata = {
                    "title": f"Batch Test Track {i+1}",
                    "artist": "Big Mann Entertainment",
                    "album": "Batch Processing Test",
                    "isrc": f"US-QZ9-25-BATCH{i+1:02d}",
                    "release_date": "2025-01-15T00:00:00Z",
                    "rights_holders": ["Big Mann Entertainment"]
                }
                
                content = json.dumps(metadata).encode('utf-8')
                
                files = {'file': ('batch_test.json', content, 'application/json')}
                data = {
                    'format': 'json',
                    'validate': 'true',
                    'check_duplicates': 'true'
                }
                
                response = self.session.post(
                    f"{API_BASE}/metadata/upload",
                    files=files,
                    data=data,
                    headers={'Authorization': f'Bearer {self.user_token}'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    batch_results.append({
                        'file': f'batch_test_{i+1}.json',
                        'success': result.get('success', False),
                        'validation_status': result.get('validation_status'),
                        'processing_time': result.get('processing_time', 0)
                    })
                else:
                    batch_results.append({
                        'file': f'batch_test_{i+1}.json',
                        'success': False,
                        'error': f"HTTP {response.status_code}"
                    })
                    
            batch_end_time = time.time()
            batch_processing_time = (batch_end_time - batch_start_time) * 1000
            
            successful_uploads = sum(1 for r in batch_results if r.get('success'))
            total_uploads = len(batch_results)
            
            success = successful_uploads >= 2  # At least 2 out of 3 should succeed
            
            self.log_result(
                test_name,
                success,
                f"Processed {successful_uploads}/{total_uploads} files in {batch_processing_time:.2f}ms",
                "" if success else f"Only {successful_uploads} out of {total_uploads} files processed successfully"
            )
            return success
            
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def test_user_statistics_reporting(self):
        """Test 5: Advanced Reporting - User Statistics"""
        test_name = "User Statistics Reporting"
        
        if not self.user_token:
            self.log_result(test_name, False, "", "No authentication token available")
            return False
            
        try:
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(f"{API_BASE}/metadata/statistics", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    statistics = result.get('statistics', {})
                    
                    total_validations = statistics.get('total_validations', 0)
                    validation_status = statistics.get('validation_status', {})
                    format_distribution = statistics.get('format_distribution', {})
                    success_rate = statistics.get('success_rate', 0)
                    
                    # Check if statistics are comprehensive
                    has_status_breakdown = len(validation_status) > 0 or total_validations == 0
                    has_format_breakdown = len(format_distribution) > 0 or total_validations == 0
                    
                    success = has_status_breakdown and total_validations >= 0
                    
                    self.log_result(
                        test_name,
                        success,
                        f"Validations: {total_validations}, Success rate: {success_rate}%, Status breakdown: {len(validation_status)} items",
                        "" if success else "Statistics endpoint not providing comprehensive data"
                    )
                    return success
            else:
                self.log_result(test_name, False, "", f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def test_validation_results_retrieval(self):
        """Test 6: Validation Results Retrieval"""
        test_name = "Validation Results Retrieval"
        
        if not self.user_token:
            self.log_result(test_name, False, "", "No authentication token available")
            return False
            
        try:
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"{API_BASE}/metadata/validation-results",
                params={'limit': 10, 'offset': 0},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    validation_results = result.get('validation_results', [])
                    total_count = result.get('total_count', 0)
                    
                    success = total_count >= 0  # Should at least return 0 or more
                    
                    self.log_result(
                        test_name,
                        success,
                        f"Retrieved {len(validation_results)} results from {total_count} total",
                        "" if success else "Failed to retrieve validation results"
                    )
                    return success
            else:
                self.log_result(test_name, False, "", f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def test_authentication_security(self):
        """Test 7: Authentication Security"""
        test_name = "Authentication Security"
        
        try:
            # Test endpoints without authentication
            endpoints_to_test = [
                ('/metadata/parse', 'POST'),
                ('/metadata/validate-json', 'POST'),
                ('/metadata/statistics', 'GET'),
                ('/metadata/duplicates/check', 'GET'),
                ('/metadata/validation-results', 'GET')
            ]
            
            auth_results = []
            
            for endpoint, method in endpoints_to_test:
                try:
                    if method == 'GET':
                        response = self.session.get(f"{API_BASE}{endpoint}")
                    elif method == 'POST':
                        response = self.session.post(f"{API_BASE}{endpoint}", json={})
                    
                    auth_results.append({
                        'endpoint': endpoint,
                        'method': method,
                        'status': response.status_code,
                        'properly_protected': response.status_code in [401, 403]
                    })
                except Exception as e:
                    auth_results.append({
                        'endpoint': endpoint,
                        'method': method,
                        'error': str(e),
                        'properly_protected': False
                    })
            
            protected_count = sum(1 for r in auth_results if r.get('properly_protected'))
            total_tested = len(auth_results)
            
            success = protected_count >= total_tested * 0.8  # 80% should be protected
            
            self.log_result(
                test_name,
                success,
                f"Protected endpoints: {protected_count}/{total_tested} ({protected_count/total_tested*100:.1f}%)",
                "" if success else f"Only {protected_count} out of {total_tested} endpoints properly protected"
            )
            return success
            
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def test_admin_endpoints_protection(self):
        """Test 8: Admin Endpoints Protection"""
        test_name = "Admin Endpoints Protection"
        
        try:
            # Test admin endpoints without admin privileges
            admin_endpoints = [
                '/metadata/admin/platform-statistics',
                '/metadata/admin/all-results'
            ]
            
            headers = {}
            if self.user_token:
                headers['Authorization'] = f'Bearer {self.user_token}'
            
            protected_count = 0
            
            for endpoint in admin_endpoints:
                try:
                    response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
                    
                    # Should return 403 (Forbidden) for non-admin users or 401 for unauthenticated
                    if response.status_code in [401, 403]:
                        protected_count += 1
                        
                except Exception:
                    pass  # Network errors are acceptable for this test
            
            total_tested = len(admin_endpoints)
            success = protected_count >= total_tested * 0.8  # 80% should be protected
            
            self.log_result(
                test_name,
                success,
                f"Admin endpoints protected: {protected_count}/{total_tested}",
                "" if success else f"Only {protected_count} out of {total_tested} admin endpoints properly protected"
            )
            return success
            
        except Exception as e:
            self.log_result(test_name, False, "", f"Error: {str(e)}")
            
        return False

    def run_comprehensive_tests(self):
        """Run all Phase 2 metadata tests"""
        print("🎯 PHASE 2 METADATA PARSER & VALIDATOR COMPREHENSIVE TESTING")
        print("=" * 70)
        print("Big Mann Entertainment Platform - Production Readiness Verification")
        print("Target: 85%+ overall success rate across all Phase 2 features")
        print("=" * 70)
        
        # Setup authentication (optional for some tests)
        auth_success = self.setup_authentication()
        if not auth_success:
            print("⚠️  Authentication setup failed - some tests will be skipped")
        
        print("\n🧪 Running Phase 2 Metadata Tests...")
        print("-" * 50)
        
        # Run all tests
        test_functions = [
            self.test_supported_formats_extended,
            self.test_metadata_parsing_json,
            self.test_duplicate_detection,
            self.test_batch_processing_simulation,
            self.test_user_statistics_reporting,
            self.test_validation_results_retrieval,
            self.test_authentication_security,
            self.test_admin_endpoints_protection
        ]
        
        for i, test_func in enumerate(test_functions, 1):
            print(f"\n[{i}/{len(test_functions)}] Running {test_func.__name__.replace('test_', '').replace('_', ' ').title()}...")
            test_func()
            time.sleep(0.5)  # Small delay between tests
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("🎉 PHASE 2 METADATA PARSER & VALIDATOR TESTING COMPLETED")
        print("=" * 70)
        
        print(f"\n📊 COMPREHENSIVE TEST RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Determine overall status
        target_success_rate = 85.0
        if success_rate >= target_success_rate:
            print(f"\n🎯 TARGET ACHIEVED: {success_rate:.1f}% ≥ {target_success_rate}% - PRODUCTION READY!")
            overall_status = "PRODUCTION READY"
        else:
            print(f"\n⚠️  TARGET MISSED: {success_rate:.1f}% < {target_success_rate}% - NEEDS ATTENTION")
            overall_status = "NEEDS ATTENTION"
        
        print(f"\n🏆 FINAL ASSESSMENT: {overall_status}")
        
        # Phase 2 feature summary
        print(f"\n🎯 PHASE 2 FEATURE VERIFICATION:")
        print("-" * 40)
        
        feature_results = {
            "Extended Format Support": any("Extended Format" in r['test'] for r in self.test_results if r['success']),
            "Enhanced Metadata Processing": any("Enhanced" in r['test'] or "JSON" in r['test'] for r in self.test_results if r['success']),
            "Batch Processing System": any("Batch Processing" in r['test'] for r in self.test_results if r['success']),
            "Advanced Reporting": any("Statistics" in r['test'] or "Reporting" in r['test'] for r in self.test_results if r['success']),
            "Admin Features": any("Admin" in r['test'] for r in self.test_results if r['success']),
            "Authentication Security": any("Authentication" in r['test'] for r in self.test_results if r['success']),
            "Duplicate Detection": any("Duplicate" in r['test'] for r in self.test_results if r['success']),
            "Validation Results": any("Validation Results" in r['test'] for r in self.test_results if r['success'])
        }
        
        for feature, verified in feature_results.items():
            status = "✅ VERIFIED" if verified else "❌ FAILED"
            print(f"   {feature}: {status}")
        
        print(f"\n🎯 PHASE 2 METADATA PARSER & VALIDATOR: {overall_status}")
        print("=" * 70)
        
        return success_rate >= target_success_rate

def main():
    """Main test execution"""
    tester = MetadataPhase2Tester()
    success = tester.run_comprehensive_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())