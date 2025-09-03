#!/usr/bin/env python3
"""
Phase 3 Rights & Compliance Checker Comprehensive Backend Testing
Tests all Phase 3 features: Territory Rights, Usage Rights, Compliance Validation, Rights Ownership, Templates, Analytics
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

class Phase3RightsComplianceTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
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
        """Setup user and admin authentication"""
        print("🔐 Setting up authentication...")
        
        # Register test user
        user_data = {
            "email": "rights.tester@bigmannentertainment.com",
            "password": "RightsTest2025!",
            "full_name": "Rights Compliance Tester",
            "business_name": "Big Mann Entertainment Rights Division",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "1314 Lincoln Heights Street",
            "city": "Alexander City",
            "state_province": "Alabama",
            "postal_code": "35010",
            "country": "United States"
        }
        
        try:
            # Register user
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            if response.status_code in [200, 201]:
                self.log_result("User Registration", True, "Rights tester user registered successfully")
            else:
                # User might already exist, try login
                login_response = self.session.post(f"{API_BASE}/auth/login", json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                if login_response.status_code == 200:
                    self.log_result("User Login", True, "Existing rights tester user logged in")
                    response = login_response
                else:
                    self.log_result("User Authentication", False, "", f"Registration failed: {response.text}")
                    return False
            
            # Extract token
            auth_data = response.json()
            if 'access_token' in auth_data:
                self.user_token = auth_data['access_token']
                self.session.headers.update({'Authorization': f'Bearer {self.user_token}'})
                self.log_result("User Token Setup", True, "User authentication token configured")
                return True
            else:
                self.log_result("User Token Extraction", False, "", "No access token in response")
                return False
                
        except Exception as e:
            self.log_result("Authentication Setup", False, "", str(e))
            return False

    def test_territory_rights_management(self):
        """Test Territory Rights Management endpoints"""
        print("\n🌍 Testing Territory Rights Management...")
        
        # Test GET /api/rights/territories
        try:
            response = self.session.get(f"{API_BASE}/rights/territories")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'territories' in data:
                    territories = data['territories']
                    
                    # Check for required territories
                    required_territories = ['US', 'EU', 'GLOBAL', 'CA', 'GB', 'DE', 'FR']
                    found_territories = []
                    
                    for territory_code in required_territories:
                        if territory_code in territories:
                            territory_info = territories[territory_code]
                            found_territories.append(territory_code)
                            
                            # Verify territory information structure
                            if 'name' in territory_info and 'region' in territory_info:
                                continue
                            else:
                                self.log_result("Territory Information Structure", False, 
                                              f"Territory {territory_code} missing required fields")
                                return
                    
                    self.log_result("Territory Rights Endpoint", True, 
                                  f"Found {len(found_territories)} territories: {', '.join(found_territories)}")
                    
                    # Test specific territory mappings
                    if 'US' in territories:
                        us_info = territories['US']
                        if us_info.get('name') == 'United States' and us_info.get('currency') == 'USD':
                            self.log_result("US Territory Mapping", True, 
                                          f"US territory correctly mapped: {us_info.get('name')}")
                        else:
                            self.log_result("US Territory Mapping", False, 
                                          f"US territory mapping incorrect: {us_info}")
                    
                    if 'EU' in territories:
                        eu_info = territories['EU']
                        if eu_info.get('name') == 'European Union' and eu_info.get('eu_member'):
                            self.log_result("EU Territory Mapping", True, 
                                          f"EU territory correctly mapped with EU member flag")
                        else:
                            self.log_result("EU Territory Mapping", False, 
                                          f"EU territory mapping incorrect: {eu_info}")
                    
                else:
                    self.log_result("Territory Rights Endpoint", False, 
                                  "Response missing success flag or territories data")
            else:
                self.log_result("Territory Rights Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Territory Rights Management", False, "", str(e))

    def test_usage_rights_validation(self):
        """Test Usage Rights Validation endpoints"""
        print("\n🎵 Testing Usage Rights Validation...")
        
        # Test GET /api/rights/usage-types
        try:
            response = self.session.get(f"{API_BASE}/rights/usage-types")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'usage_types' in data:
                    usage_types = data['usage_types']
                    
                    # Check for required usage types
                    required_usage_types = ['streaming', 'download', 'sync', 'radio', 'tv', 'mechanical', 'publishing']
                    found_usage_types = []
                    
                    for usage_type in required_usage_types:
                        if usage_type in usage_types:
                            usage_info = usage_types[usage_type]
                            found_usage_types.append(usage_type)
                            
                            # Verify usage type has description
                            if 'description' in usage_info:
                                continue
                            else:
                                self.log_result("Usage Type Description", False, 
                                              f"Usage type {usage_type} missing description")
                                return
                    
                    self.log_result("Usage Rights Endpoint", True, 
                                  f"Found {len(found_usage_types)} usage types: {', '.join(found_usage_types)}")
                    
                    # Test specific usage type descriptions
                    if 'streaming' in usage_types:
                        streaming_info = usage_types['streaming']
                        if 'Digital streaming services' in streaming_info.get('description', ''):
                            self.log_result("Streaming Usage Type", True, 
                                          f"Streaming usage type correctly described")
                        else:
                            self.log_result("Streaming Usage Type", False, 
                                          f"Streaming description incorrect: {streaming_info}")
                    
                    if 'sync' in usage_types:
                        sync_info = usage_types['sync']
                        if 'Synchronization' in sync_info.get('description', ''):
                            self.log_result("Sync Usage Type", True, 
                                          f"Sync usage type correctly described")
                        else:
                            self.log_result("Sync Usage Type", False, 
                                          f"Sync description incorrect: {sync_info}")
                    
                else:
                    self.log_result("Usage Rights Endpoint", False, 
                                  "Response missing success flag or usage_types data")
            else:
                self.log_result("Usage Rights Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Usage Rights Validation", False, "", str(e))

    def test_rights_templates_system(self):
        """Test Rights Templates System"""
        print("\n📋 Testing Rights Templates System...")
        
        # Test GET /api/rights/templates/usage-rights
        try:
            response = self.session.get(f"{API_BASE}/rights/templates/usage-rights")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'usage_templates' in data:
                    templates = data['usage_templates']
                    
                    # Check for required templates
                    required_templates = ['streaming_basic', 'sync_standard', 'broadcast_basic']
                    found_templates = []
                    
                    for template_name in required_templates:
                        if template_name in templates:
                            template_info = templates[template_name]
                            found_templates.append(template_name)
                            
                            # Verify template structure
                            required_fields = ['name', 'description', 'usage_types', 'default_territories']
                            if all(field in template_info for field in required_fields):
                                continue
                            else:
                                missing_fields = [f for f in required_fields if f not in template_info]
                                self.log_result("Template Structure", False, 
                                              f"Template {template_name} missing fields: {missing_fields}")
                                return
                    
                    self.log_result("Usage Rights Templates", True, 
                                  f"Found {len(found_templates)} templates: {', '.join(found_templates)}")
                    
                    # Test specific template details
                    if 'streaming_basic' in templates:
                        streaming_template = templates['streaming_basic']
                        if ('streaming' in streaming_template.get('usage_types', []) and 
                            streaming_template.get('industry_standard')):
                            self.log_result("Streaming Template", True, 
                                          f"Streaming template correctly configured")
                        else:
                            self.log_result("Streaming Template", False, 
                                          f"Streaming template configuration incorrect")
                    
                    if 'sync_standard' in templates:
                        sync_template = templates['sync_standard']
                        if ('sync' in sync_template.get('usage_types', []) and 
                            sync_template.get('exclusivity_default')):
                            self.log_result("Sync Template", True, 
                                          f"Sync template correctly configured with exclusivity")
                        else:
                            self.log_result("Sync Template", False, 
                                          f"Sync template configuration incorrect")
                    
                else:
                    self.log_result("Usage Rights Templates", False, 
                                  "Response missing success flag or usage_templates data")
            else:
                self.log_result("Usage Rights Templates", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Rights Templates System", False, "", str(e))

    def test_rights_ownership_management(self):
        """Test Rights Ownership Management"""
        print("\n📝 Testing Rights Ownership Management...")
        
        # Generate test data
        self.test_content_id = f"test_content_{uuid.uuid4().hex[:8]}"
        self.test_isrc = f"USQZ9H825{str(uuid.uuid4().hex[:5]).upper()}"
        
        # Test POST /api/rights/ownership
        try:
            rights_data = {
                "content_id": self.test_content_id,
                "isrc": self.test_isrc,
                "title": "Big Mann Entertainment Rights Test Track",
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
                "created_by": "rights_tester"
            }
            
            response = self.session.post(f"{API_BASE}/rights/ownership", json=rights_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'content_id' in data:
                    created_content_id = data['content_id']
                    self.log_result("Rights Ownership Creation", True, 
                                  f"Created rights record for content: {created_content_id}")
                    
                    # Test GET /api/rights/ownership/{content_id}
                    get_response = self.session.get(f"{API_BASE}/rights/ownership/{created_content_id}")
                    
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        
                        if get_data.get('success') and 'rights_ownership' in get_data:
                            rights_ownership = get_data['rights_ownership']
                            
                            # Verify data integrity
                            if (rights_ownership.get('content_id') == created_content_id and
                                rights_ownership.get('isrc') == self.test_isrc and
                                rights_ownership.get('title') == "Big Mann Entertainment Rights Test Track"):
                                
                                self.log_result("Rights Ownership Retrieval", True, 
                                              f"Successfully retrieved rights data with correct content")
                                
                                # Verify territory rights
                                territory_rights = rights_ownership.get('territory_rights', [])
                                if len(territory_rights) >= 2:
                                    us_rights = next((tr for tr in territory_rights if tr.get('territory') == 'US'), None)
                                    if us_rights and us_rights.get('rights_percentage') == 100.0:
                                        self.log_result("Territory Rights Verification", True, 
                                                      f"US territory rights correctly stored: 100%")
                                    else:
                                        self.log_result("Territory Rights Verification", False, 
                                                      f"US territory rights incorrect: {us_rights}")
                                else:
                                    self.log_result("Territory Rights Verification", False, 
                                                  f"Expected 2+ territory rights, got {len(territory_rights)}")
                                
                                # Verify usage rights
                                usage_rights = rights_ownership.get('usage_rights', [])
                                if len(usage_rights) >= 2:
                                    streaming_rights = next((ur for ur in usage_rights if ur.get('usage_type') == 'streaming'), None)
                                    if streaming_rights and streaming_rights.get('royalty_rate') == 0.006:
                                        self.log_result("Usage Rights Verification", True, 
                                                      f"Streaming usage rights correctly stored: $0.006")
                                    else:
                                        self.log_result("Usage Rights Verification", False, 
                                                      f"Streaming usage rights incorrect: {streaming_rights}")
                                else:
                                    self.log_result("Usage Rights Verification", False, 
                                                  f"Expected 2+ usage rights, got {len(usage_rights)}")
                                
                            else:
                                self.log_result("Rights Ownership Retrieval", False, 
                                              f"Retrieved data doesn't match created data")
                        else:
                            self.log_result("Rights Ownership Retrieval", False, 
                                          "Response missing success flag or rights_ownership data")
                    else:
                        self.log_result("Rights Ownership Retrieval", False, 
                                      f"HTTP {get_response.status_code}: {get_response.text}")
                    
                else:
                    self.log_result("Rights Ownership Creation", False, 
                                  "Response missing success flag or content_id")
            else:
                self.log_result("Rights Ownership Creation", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Rights Ownership Management", False, "", str(e))

    def test_compliance_checking_system(self):
        """Test Compliance Checking System"""
        print("\n🔍 Testing Compliance Checking System...")
        
        if not self.test_content_id or not self.test_isrc:
            self.log_result("Compliance Check Prerequisites", False, 
                          "No test content available for compliance checking")
            return
        
        # Test POST /api/rights/check-compliance
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
                        self.log_result("Compliance Check Structure", True, 
                                      f"Compliance result has all required fields")
                        
                        # Check overall status
                        overall_status = compliance_result.get('overall_status')
                        if overall_status in ['compliant', 'non_compliant', 'warning', 'unknown']:
                            self.log_result("Compliance Status Validation", True, 
                                          f"Overall status: {overall_status}")
                        else:
                            self.log_result("Compliance Status Validation", False, 
                                          f"Invalid overall status: {overall_status}")
                        
                        # Check territory compliance
                        territory_compliance = compliance_result.get('territory_compliance', {})
                        if 'US' in territory_compliance and 'EU' in territory_compliance:
                            self.log_result("Territory Compliance Check", True, 
                                          f"Territory compliance: US={territory_compliance.get('US')}, EU={territory_compliance.get('EU')}")
                        else:
                            self.log_result("Territory Compliance Check", False, 
                                          f"Missing territory compliance data: {territory_compliance}")
                        
                        # Check usage compliance
                        usage_compliance = compliance_result.get('usage_compliance', {})
                        if 'streaming' in usage_compliance and 'sync' in usage_compliance:
                            self.log_result("Usage Compliance Check", True, 
                                          f"Usage compliance: streaming={usage_compliance.get('streaming')}, sync={usage_compliance.get('sync')}")
                        else:
                            self.log_result("Usage Compliance Check", False, 
                                          f"Missing usage compliance data: {usage_compliance}")
                        
                        # Check summary data
                        if 'processing_time' in summary and isinstance(summary.get('processing_time'), (int, float)):
                            self.log_result("Compliance Processing Time", True, 
                                          f"Processing time: {summary.get('processing_time')}s")
                        else:
                            self.log_result("Compliance Processing Time", False, 
                                          f"Invalid processing time: {summary.get('processing_time')}")
                        
                    else:
                        missing_fields = [f for f in required_fields if f not in compliance_result]
                        self.log_result("Compliance Check Structure", False, 
                                      f"Missing required fields: {missing_fields}")
                    
                else:
                    self.log_result("Comprehensive Compliance Check", False, 
                                  "Response missing success flag or compliance_result data")
            else:
                self.log_result("Comprehensive Compliance Check", False, 
                              f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_result("Comprehensive Compliance Check", False, "", str(e))
        
        # Test POST /api/rights/quick-check
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
                    else:
                        self.log_result("Quick Compliance Check", False, 
                                      f"Invalid quick check response structure")
                else:
                    self.log_result("Quick Compliance Check", False, 
                                  "Response missing success flag or compliance_status")
            else:
                self.log_result("Quick Compliance Check", False, 
                              f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_result("Quick Compliance Check", False, "", str(e))

    def test_compliance_history_analytics(self):
        """Test Compliance History & Analytics"""
        print("\n📊 Testing Compliance History & Analytics...")
        
        if not self.test_content_id:
            self.log_result("Compliance History Prerequisites", False, 
                          "No test content available for compliance history")
            return
        
        # Test GET /api/rights/compliance-history/{content_id}
        try:
            response = self.session.get(f"{API_BASE}/rights/compliance-history/{self.test_content_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'compliance_history' in data:
                    compliance_history = data['compliance_history']
                    total_count = data.get('total_count', 0)
                    
                    # Should have at least one compliance check from previous test
                    if total_count >= 1:
                        self.log_result("Compliance History Retrieval", True, 
                                      f"Found {total_count} compliance check(s) in history")
                        
                        if compliance_history and len(compliance_history) > 0:
                            latest_check = compliance_history[0]
                            if ('check_date' in latest_check and 
                                'overall_status' in latest_check and
                                latest_check.get('content_id') == self.test_content_id):
                                
                                self.log_result("Compliance History Structure", True, 
                                              f"Latest check status: {latest_check.get('overall_status')}")
                            else:
                                self.log_result("Compliance History Structure", False, 
                                              f"Invalid compliance history entry structure")
                        else:
                            self.log_result("Compliance History Data", False, 
                                          f"No compliance history entries despite total_count={total_count}")
                    else:
                        self.log_result("Compliance History Retrieval", False, 
                                      f"Expected at least 1 compliance check, got {total_count}")
                else:
                    self.log_result("Compliance History Retrieval", False, 
                                  "Response missing success flag or compliance_history data")
            else:
                self.log_result("Compliance History Retrieval", False, 
                              f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_result("Compliance History Retrieval", False, "", str(e))
        
        # Test GET /api/rights/dashboard/rights-summary
        try:
            response = self.session.get(f"{API_BASE}/rights/dashboard/rights-summary")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'rights_summary' in data:
                    rights_summary = data['rights_summary']
                    
                    # Check required summary fields
                    required_fields = ['total_rights_records', 'recent_compliance_checks', 'compliance_breakdown']
                    if all(field in rights_summary for field in required_fields):
                        total_rights = rights_summary.get('total_rights_records', 0)
                        recent_checks = rights_summary.get('recent_compliance_checks', 0)
                        compliance_breakdown = rights_summary.get('compliance_breakdown', {})
                        
                        # Should have at least one rights record from previous test
                        if total_rights >= 1:
                            self.log_result("Rights Dashboard Summary", True, 
                                          f"Dashboard shows {total_rights} rights record(s), {recent_checks} recent check(s)")
                            
                            if compliance_breakdown and isinstance(compliance_breakdown, dict):
                                self.log_result("Compliance Breakdown", True, 
                                              f"Compliance breakdown: {compliance_breakdown}")
                            else:
                                self.log_result("Compliance Breakdown", False, 
                                              f"Invalid compliance breakdown: {compliance_breakdown}")
                        else:
                            self.log_result("Rights Dashboard Summary", False, 
                                          f"Expected at least 1 rights record, got {total_rights}")
                    else:
                        missing_fields = [f for f in required_fields if f not in rights_summary]
                        self.log_result("Rights Dashboard Summary", False, 
                                      f"Missing required fields: {missing_fields}")
                else:
                    self.log_result("Rights Dashboard Summary", False, 
                                  "Response missing success flag or rights_summary data")
            else:
                self.log_result("Rights Dashboard Summary", False, 
                              f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_result("Rights Dashboard Summary", False, "", str(e))

    def test_authentication_security(self):
        """Test Authentication & Security for Rights endpoints"""
        print("\n🔒 Testing Authentication & Security...")
        
        # Test unauthenticated access
        temp_session = requests.Session()  # No auth headers
        
        # Test protected endpoints without authentication
        protected_endpoints = [
            ("/rights/check-compliance", "POST"),
            ("/rights/ownership", "POST"),
            ("/rights/quick-check", "POST"),
            ("/rights/dashboard/rights-summary", "GET"),
            ("/rights/compliance-history/test123", "GET")
        ]
        
        for endpoint, method in protected_endpoints:
            try:
                if method == "POST":
                    response = temp_session.post(f"{API_BASE}{endpoint}", data={"test": "data"})
                else:
                    response = temp_session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code in [401, 403]:
                    self.log_result(f"Authentication Protection - {endpoint}", True, 
                                  f"Correctly rejected unauthenticated access (HTTP {response.status_code})")
                else:
                    self.log_result(f"Authentication Protection - {endpoint}", False, 
                                  f"Should reject unauthenticated access, got HTTP {response.status_code}")
            
            except Exception as e:
                self.log_result(f"Authentication Protection - {endpoint}", False, "", str(e))
        
        # Test public endpoints (should work without authentication)
        public_endpoints = [
            "/rights/territories",
            "/rights/usage-types", 
            "/rights/templates/usage-rights"
        ]
        
        for endpoint in public_endpoints:
            try:
                response = temp_session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    self.log_result(f"Public Access - {endpoint}", True, 
                                  f"Public endpoint accessible without authentication")
                else:
                    self.log_result(f"Public Access - {endpoint}", False, 
                                  f"Public endpoint should be accessible, got HTTP {response.status_code}")
            
            except Exception as e:
                self.log_result(f"Public Access - {endpoint}", False, "", str(e))

    def run_comprehensive_test(self):
        """Run comprehensive Phase 3 Rights & Compliance testing"""
        print("🎯 PHASE 3 RIGHTS & COMPLIANCE CHECKER COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with testing.")
            return
        
        # Run all test categories
        self.test_territory_rights_management()
        self.test_usage_rights_validation()
        self.test_compliance_checking_system()
        self.test_rights_ownership_management()
        self.test_rights_templates_system()
        self.test_compliance_history_analytics()
        self.test_authentication_security()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 PHASE 3 RIGHTS & COMPLIANCE TESTING FINAL REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Test categories summary
        categories = {
            "Territory Rights Management": ["Territory Rights", "Territory Mapping"],
            "Usage Rights Validation": ["Usage Rights", "Usage Type"],
            "Compliance Checking System": ["Compliance Check", "Quick Check", "Quick Compliance"],
            "Rights Ownership Management": ["Rights Ownership", "Territory Rights Verification", "Usage Rights Verification"],
            "Rights Templates System": ["Usage Rights Templates", "Template", "Streaming Template", "Sync Template"],
            "Compliance History & Analytics": ["Compliance History", "Rights Dashboard", "Compliance Breakdown"],
            "Authentication & Security": ["Authentication Protection", "Public Access"]
        }
        
        print("📋 CATEGORY BREAKDOWN:")
        for category, keywords in categories.items():
            category_tests = [r for r in self.test_results if any(keyword in r['test'] for keyword in keywords)]
            if category_tests:
                category_passed = len([r for r in category_tests if r['success']])
                category_total = len(category_tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                status = "✅" if category_rate >= 90 else "⚠️" if category_rate >= 70 else "❌"
                print(f"  {status} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
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
        
        # Success criteria evaluation
        print("🎯 SUCCESS CRITERIA EVALUATION:")
        
        # Target: 90%+ success rate across all Rights & Compliance features
        if success_rate >= 90:
            print(f"  ✅ Overall Success Rate: {success_rate:.1f}% (Target: 90%+)")
        else:
            print(f"  ❌ Overall Success Rate: {success_rate:.1f}% (Target: 90%+)")
        
        # Check specific feature areas
        territory_tests = [r for r in self.test_results if "Territory" in r['test']]
        territory_success = (len([r for r in territory_tests if r['success']]) / len(territory_tests) * 100) if territory_tests else 0
        
        usage_tests = [r for r in self.test_results if "Usage" in r['test']]
        usage_success = (len([r for r in usage_tests if r['success']]) / len(usage_tests) * 100) if usage_tests else 0
        
        compliance_tests = [r for r in self.test_results if "Compliance" in r['test']]
        compliance_success = (len([r for r in compliance_tests if r['success']]) / len(compliance_tests) * 100) if compliance_tests else 0
        
        print(f"  {'✅' if territory_success >= 90 else '❌'} Territory Rights Management: {territory_success:.1f}%")
        print(f"  {'✅' if usage_success >= 90 else '❌'} Usage Rights Validation: {usage_success:.1f}%")
        print(f"  {'✅' if compliance_success >= 90 else '❌'} Compliance Validation Logic: {compliance_success:.1f}%")
        
        # Overall assessment
        print()
        if success_rate >= 90:
            print("🎉 PHASE 3 RIGHTS & COMPLIANCE SYSTEM: PRODUCTION READY")
            print("   All major features operational with high success rate")
        elif success_rate >= 70:
            print("⚠️  PHASE 3 RIGHTS & COMPLIANCE SYSTEM: NEEDS ATTENTION")
            print("   Core features working but some issues need resolution")
        else:
            print("❌ PHASE 3 RIGHTS & COMPLIANCE SYSTEM: CRITICAL ISSUES")
            print("   Major functionality problems require immediate attention")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = Phase3RightsComplianceTester()
    tester.run_comprehensive_test()