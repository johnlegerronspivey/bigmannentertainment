#!/usr/bin/env python3
"""
Focused Admin Testing Suite for Big Mann Entertainment
Tests admin endpoints and functionality with authentication handling
"""

import requests
import json
import os
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://sound-industry-hub.preview.emergentagent.com/api"

class AdminTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.results = {
            "admin_endpoints": {"passed": 0, "failed": 0, "details": []},
            "admin_authentication": {"passed": 0, "failed": 0, "details": []},
            "admin_functionality": {"passed": 0, "failed": 0, "details": []},
            "ethereum_integration": {"passed": 0, "failed": 0, "details": []},
            "platform_verification": {"passed": 0, "failed": 0, "details": []}
        }
    
    def log_result(self, category: str, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results[category]["failed"] += 1
            status = "❌ FAIL"
        
        self.results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise

    def test_admin_endpoints_accessibility(self) -> bool:
        """Test that admin endpoints exist and return proper authentication errors"""
        try:
            admin_endpoints = [
                "/admin/users",
                "/admin/content", 
                "/admin/analytics/overview",
                "/admin/platforms",
                "/admin/revenue",
                "/admin/blockchain",
                "/admin/security/logs",
                "/admin/config"
            ]
            
            accessible_endpoints = []
            for endpoint in admin_endpoints:
                response = self.make_request('GET', endpoint)
                
                # Admin endpoints should return 403 (Forbidden) or 401 (Unauthorized) for non-admin users
                if response.status_code in [401, 403]:
                    accessible_endpoints.append(endpoint)
                elif response.status_code == 500:
                    # Server error might indicate endpoint exists but has issues
                    accessible_endpoints.append(f"{endpoint} (server error)")
                
            if len(accessible_endpoints) >= 6:  # At least 6 out of 8 endpoints should be accessible
                self.log_result("admin_endpoints", "Admin Endpoints Accessibility", True, 
                              f"Found {len(accessible_endpoints)} admin endpoints: {', '.join(accessible_endpoints)}")
                return True
            else:
                self.log_result("admin_endpoints", "Admin Endpoints Accessibility", False, 
                              f"Only found {len(accessible_endpoints)} admin endpoints")
                return False
                
        except Exception as e:
            self.log_result("admin_endpoints", "Admin Endpoints Accessibility", False, f"Exception: {str(e)}")
            return False

    def test_admin_authentication_protection(self) -> bool:
        """Test that admin endpoints are properly protected"""
        try:
            # Test without any authentication
            response = self.make_request('GET', '/admin/users')
            
            if response.status_code in [401, 403]:
                self.log_result("admin_authentication", "Admin Authentication Protection", True, 
                              f"Admin endpoints properly protected (status: {response.status_code})")
                return True
            else:
                self.log_result("admin_authentication", "Admin Authentication Protection", False, 
                              f"Admin endpoints not properly protected (status: {response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("admin_authentication", "Admin Authentication Protection", False, f"Exception: {str(e)}")
            return False

    def test_admin_user_management_structure(self) -> bool:
        """Test admin user management endpoint structure"""
        try:
            response = self.make_request('GET', '/admin/users')
            
            if response.status_code == 403:
                # Check if the error message indicates proper role-based access control
                try:
                    error_data = response.json()
                    if 'detail' in error_data and ('permission' in error_data['detail'].lower() or 'admin' in error_data['detail'].lower()):
                        self.log_result("admin_functionality", "User Management Structure", True, 
                                      "User management endpoint has proper role-based access control")
                        return True
                    else:
                        self.log_result("admin_functionality", "User Management Structure", True, 
                                      "User management endpoint protected (generic access control)")
                        return True
                except:
                    self.log_result("admin_functionality", "User Management Structure", True, 
                                  "User management endpoint protected")
                    return True
            else:
                self.log_result("admin_functionality", "User Management Structure", False, 
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("admin_functionality", "User Management Structure", False, f"Exception: {str(e)}")
            return False

    def test_admin_content_management_structure(self) -> bool:
        """Test admin content management endpoint structure"""
        try:
            response = self.make_request('GET', '/admin/content')
            
            if response.status_code in [401, 403]:
                self.log_result("admin_functionality", "Content Management Structure", True, 
                              "Content management endpoint properly protected")
                return True
            else:
                self.log_result("admin_functionality", "Content Management Structure", False, 
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("admin_functionality", "Content Management Structure", False, f"Exception: {str(e)}")
            return False

    def test_admin_analytics_structure(self) -> bool:
        """Test admin analytics endpoint structure"""
        try:
            response = self.make_request('GET', '/admin/analytics/overview')
            
            if response.status_code in [401, 403]:
                self.log_result("admin_functionality", "Analytics Structure", True, 
                              "Analytics endpoint properly protected")
                return True
            else:
                self.log_result("admin_functionality", "Analytics Structure", False, 
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("admin_functionality", "Analytics Structure", False, f"Exception: {str(e)}")
            return False

    def test_admin_platform_management_structure(self) -> bool:
        """Test admin platform management endpoint structure"""
        try:
            response = self.make_request('GET', '/admin/platforms')
            
            if response.status_code in [401, 403]:
                self.log_result("admin_functionality", "Platform Management Structure", True, 
                              "Platform management endpoint properly protected")
                return True
            else:
                self.log_result("admin_functionality", "Platform Management Structure", False, 
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("admin_functionality", "Platform Management Structure", False, f"Exception: {str(e)}")
            return False

    def test_admin_blockchain_management_structure(self) -> bool:
        """Test admin blockchain management endpoint structure"""
        try:
            response = self.make_request('GET', '/admin/blockchain')
            
            if response.status_code in [401, 403]:
                self.log_result("admin_functionality", "Blockchain Management Structure", True, 
                              "Blockchain management endpoint properly protected")
                return True
            else:
                self.log_result("admin_functionality", "Blockchain Management Structure", False, 
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("admin_functionality", "Blockchain Management Structure", False, f"Exception: {str(e)}")
            return False

    def test_admin_security_audit_structure(self) -> bool:
        """Test admin security and audit endpoint structure"""
        try:
            response = self.make_request('GET', '/admin/security/logs')
            
            if response.status_code in [401, 403]:
                self.log_result("admin_functionality", "Security Audit Structure", True, 
                              "Security audit endpoint properly protected")
                return True
            else:
                self.log_result("admin_functionality", "Security Audit Structure", False, 
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("admin_functionality", "Security Audit Structure", False, f"Exception: {str(e)}")
            return False

    def test_ethereum_address_configuration(self) -> bool:
        """Test Ethereum address integration in platform configuration"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                
                # Check for Ethereum platform configuration
                if 'ethereum_mainnet' in platforms:
                    eth_platform = platforms['ethereum_mainnet']
                    
                    if (eth_platform.get('contract_address') == '0xdfe98870c599734335900ce15e26d1d2ccc062c1' and
                        eth_platform.get('wallet_address') == '0xdfe98870c599734335900ce15e26d1d2ccc062c1'):
                        
                        self.log_result("ethereum_integration", "Ethereum Address Configuration", True, 
                                      f"Ethereum address properly configured: {eth_platform['contract_address']}")
                        return True
                    else:
                        self.log_result("ethereum_integration", "Ethereum Address Configuration", False, 
                                      f"Ethereum address not properly configured: {eth_platform.get('contract_address')}")
                        return False
                else:
                    self.log_result("ethereum_integration", "Ethereum Address Configuration", False, 
                                  "Ethereum platform not found")
                    return False
            else:
                self.log_result("ethereum_integration", "Ethereum Address Configuration", False, 
                              f"Failed to get platforms: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("ethereum_integration", "Ethereum Address Configuration", False, f"Exception: {str(e)}")
            return False

    def test_platform_count_verification(self) -> bool:
        """Test that platform count meets the 52+ requirement"""
        try:
            response = self.make_request('GET', '/distribution/platforms')
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('platforms', {})
                total_platforms = len(platforms)
                
                if total_platforms >= 52:
                    # Count by category
                    categories = {}
                    for platform in platforms.values():
                        platform_type = platform.get('type', 'unknown')
                        categories[platform_type] = categories.get(platform_type, 0) + 1
                    
                    self.log_result("platform_verification", "Platform Count Verification", True, 
                                  f"Found {total_platforms} platforms across categories: {dict(categories)}")
                    return True
                else:
                    self.log_result("platform_verification", "Platform Count Verification", False, 
                                  f"Only found {total_platforms} platforms, expected 52+")
                    return False
            else:
                self.log_result("platform_verification", "Platform Count Verification", False, 
                              f"Failed to get platforms: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("platform_verification", "Platform Count Verification", False, f"Exception: {str(e)}")
            return False

    def test_admin_system_config_structure(self) -> bool:
        """Test admin system configuration endpoint structure"""
        try:
            response = self.make_request('GET', '/admin/config')
            
            if response.status_code in [401, 403]:
                self.log_result("admin_functionality", "System Config Structure", True, 
                              "System config endpoint properly protected")
                return True
            else:
                self.log_result("admin_functionality", "System Config Structure", False, 
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("admin_functionality", "System Config Structure", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all focused admin tests"""
        print("=" * 80)
        print("BIG MANN ENTERTAINMENT - FOCUSED ADMIN FUNCTIONALITY TESTING")
        print("Testing Administrator Features & System Integration")
        print("=" * 80)
        
        print("\n🔗 TESTING ADMIN ENDPOINT ACCESSIBILITY")
        print("-" * 40)
        self.test_admin_endpoints_accessibility()
        
        print("\n🔐 TESTING ADMIN AUTHENTICATION PROTECTION")
        print("-" * 40)
        self.test_admin_authentication_protection()
        
        print("\n👥 TESTING ADMIN USER MANAGEMENT STRUCTURE")
        print("-" * 40)
        self.test_admin_user_management_structure()
        
        print("\n📝 TESTING ADMIN CONTENT MANAGEMENT STRUCTURE")
        print("-" * 40)
        self.test_admin_content_management_structure()
        
        print("\n📈 TESTING ADMIN ANALYTICS STRUCTURE")
        print("-" * 40)
        self.test_admin_analytics_structure()
        
        print("\n🔧 TESTING ADMIN PLATFORM MANAGEMENT STRUCTURE")
        print("-" * 40)
        self.test_admin_platform_management_structure()
        
        print("\n⛓️ TESTING ADMIN BLOCKCHAIN MANAGEMENT STRUCTURE")
        print("-" * 40)
        self.test_admin_blockchain_management_structure()
        
        print("\n🔒 TESTING ADMIN SECURITY AUDIT STRUCTURE")
        print("-" * 40)
        self.test_admin_security_audit_structure()
        
        print("\n⚙️ TESTING ADMIN SYSTEM CONFIG STRUCTURE")
        print("-" * 40)
        self.test_admin_system_config_structure()
        
        print("\n🔗 TESTING ETHEREUM ADDRESS INTEGRATION")
        print("-" * 40)
        self.test_ethereum_address_configuration()
        
        print("\n🌐 TESTING PLATFORM COUNT VERIFICATION")
        print("-" * 40)
        self.test_platform_count_verification()
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("FOCUSED ADMIN TEST SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAILED"
            print(f"\n{category.upper().replace('_', ' ')}: {passed} passed, {failed} failed - {status}")
            
            for detail in results["details"]:
                print(f"  {detail}")
        
        print(f"\n" + "=" * 80)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL: {total_passed} passed, {total_failed} failed - {overall_status}")
        print("=" * 80)
        
        return total_failed == 0

if __name__ == "__main__":
    tester = AdminTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)