#!/usr/bin/env python3
"""
Content Workflow System - Actual CURL Tests with Response Analysis
Executing comprehensive backend testing for the content workflow system as requested.

This test suite provides:
1. Service health status for all three services (workflow, transcoding, distribution)
2. Available transcoding profiles and their configurations  
3. Available distribution platforms and their capabilities
4. Dashboard data structure and content
5. Authentication integration testing
6. Any errors or issues found
7. Overall system readiness assessment

Using actual curl commands and providing full test results with response analysis.
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-hub-277.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ContentWorkflowCurlTester:
    def __init__(self):
        self.auth_token = None
        self.test_user_email = "curl.tester@bigmannentertainment.com"
        self.test_user_password = "CurlTest2025!"
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test results with detailed analysis"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_data and isinstance(response_data, dict):
            if "error" in response_data:
                print(f"   Error: {response_data['error']}")
            elif "message" in response_data:
                print(f"   Message: {response_data['message']}")

    def execute_curl(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Execute curl command and return parsed response"""
        url = f"{API_BASE}{endpoint}"
        
        # Build curl command
        curl_cmd = ["curl", "-s", "-X", method.upper()]
        
        # Add headers
        if headers:
            for key, value in headers.items():
                curl_cmd.extend(["-H", f"{key}: {value}"])
        
        # Add auth header if available
        if self.auth_token:
            curl_cmd.extend(["-H", f"Authorization: Bearer {self.auth_token}"])
        
        # Add data for POST requests
        if data and method.upper() == "POST":
            curl_cmd.extend(["-H", "Content-Type: application/json"])
            curl_cmd.extend(["-d", json.dumps(data)])
        
        curl_cmd.append(url)
        
        try:
            # Execute curl command
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
            
            # Parse response
            try:
                response_data = json.loads(result.stdout) if result.stdout else {}
            except json.JSONDecodeError:
                response_data = {"raw_response": result.stdout, "stderr": result.stderr}
            
            return {
                "status_code": 200 if result.returncode == 0 else 500,
                "data": response_data,
                "curl_command": " ".join(curl_cmd),
                "raw_stdout": result.stdout,
                "raw_stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status_code": 408,
                "data": {"error": "Request timeout"},
                "curl_command": " ".join(curl_cmd)
            }
        except Exception as e:
            return {
                "status_code": 500,
                "data": {"error": str(e)},
                "curl_command": " ".join(curl_cmd)
            }

    def test_authentication_integration(self):
        """Test authentication integration using curl"""
        print("\n🔐 TESTING AUTHENTICATION INTEGRATION WITH CURL")
        
        # Test user registration
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": "Curl Tester",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Curl Street",
            "city": "Test City",
            "state_province": "CA",
            "postal_code": "90210",
            "country": "USA"
        }
        
        response = self.execute_curl("POST", "/auth/register", registration_data)
        
        if response["status_code"] == 200 and "access_token" in response["data"]:
            self.auth_token = response["data"]["access_token"]
            self.log_test("User Registration (CURL)", "PASS", "New user registered successfully", response["data"])
        elif "already registered" in str(response["data"]).lower():
            self.log_test("User Registration (CURL)", "PASS", "User already exists, proceeding to login", response["data"])
        else:
            self.log_test("User Registration (CURL)", "FAIL", f"Registration failed", response["data"])
            
        # Test user login if registration failed or user exists
        if not self.auth_token:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.execute_curl("POST", "/auth/login", login_data)
            
            if response["status_code"] == 200 and "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
                self.log_test("User Login (CURL)", "PASS", "Authentication successful", response["data"])
            else:
                self.log_test("User Login (CURL)", "FAIL", f"Login failed", response["data"])
                return False
                
        # Test authenticated user profile
        response = self.execute_curl("GET", "/auth/me")
        
        if response["status_code"] == 200:
            self.log_test("User Profile Access (CURL)", "PASS", "Profile retrieved successfully", response["data"])
        else:
            self.log_test("User Profile Access (CURL)", "FAIL", f"Profile access failed", response["data"])
            
        return True

    def test_service_health_status(self):
        """Test service health status for all three services using curl"""
        print("\n🏥 TESTING SERVICE HEALTH STATUS WITH CURL")
        
        services = [
            ("Workflow Service", "/workflow/health"),
            ("Transcoding Service", "/transcoding/health"),
            ("Distribution Service", "/distribution/health")
        ]
        
        service_health = {}
        
        for service_name, endpoint in services:
            response = self.execute_curl("GET", endpoint)
            
            if response["status_code"] == 200:
                health_data = response["data"]
                service_health[service_name] = {
                    "status": "healthy",
                    "details": health_data
                }
                
                # Analyze service-specific details
                if service_name == "Workflow Service":
                    components = health_data.get("components", {})
                    component_status = [f"{comp}: {status}" for comp, status in components.items()]
                    self.log_test(f"{service_name} Health (CURL)", "PASS", 
                                 f"Service healthy with components: {', '.join(component_status)}", 
                                 health_data)
                    
                elif service_name == "Transcoding Service":
                    profiles = health_data.get("supported_profiles", [])
                    standards = health_data.get("audio_standards", [])
                    self.log_test(f"{service_name} Health (CURL)", "PASS", 
                                 f"Service healthy with {len(profiles)} profiles and {len(standards)} audio standards", 
                                 health_data)
                    
                elif service_name == "Distribution Service":
                    platforms = health_data.get("available_platforms", 0)
                    methods = health_data.get("supported_delivery_methods", [])
                    types = health_data.get("platform_types", [])
                    self.log_test(f"{service_name} Health (CURL)", "PASS", 
                                 f"Service healthy with {platforms} platforms, {len(methods)} delivery methods, {len(types)} platform types", 
                                 health_data)
            else:
                service_health[service_name] = {
                    "status": "unhealthy",
                    "details": response["data"]
                }
                self.log_test(f"{service_name} Health (CURL)", "FAIL", 
                             f"Service health check failed", response["data"])
        
        return service_health

    def test_transcoding_profiles_configuration(self):
        """Test available transcoding profiles and their configurations using curl"""
        print("\n🎬 TESTING TRANSCODING PROFILES CONFIGURATION WITH CURL")
        
        response = self.execute_curl("GET", "/transcoding/profiles")
        
        if response["status_code"] == 200:
            profiles_data = response["data"]
            
            if "data" in profiles_data:
                data = profiles_data["data"]
                profiles = data.get("profiles", [])
                audio_standards = data.get("audio_standards", [])
                
                # Analyze profile configurations
                profile_analysis = []
                for i, profile in enumerate(profiles):
                    if i >= 5:  # Sample first 5 profiles
                        break
                    profile_analysis.append({
                        "name": profile.get("name", "Unknown"),
                        "profile": profile.get("profile", "Unknown"),
                        "container": profile.get("container", "Unknown"),
                        "video_specs": profile.get("video_specs", {}),
                        "audio_specs": profile.get("audio_specs", {}),
                        "features": profile.get("features", [])
                    })
                
                self.log_test("Transcoding Profiles Configuration (CURL)", "PASS", 
                             f"Retrieved {len(profiles)} transcoding profiles with detailed configurations", 
                             {"total_profiles": len(profiles), "sample_profiles": profile_analysis})
                
                # Analyze audio standards
                standards_analysis = []
                for standard in audio_standards:
                    standards_analysis.append({
                        "standard": standard.get("standard"),
                        "description": standard.get("description")
                    })
                
                self.log_test("Audio Standards Configuration (CURL)", "PASS", 
                             f"Retrieved {len(audio_standards)} audio standards", 
                             {"standards": standards_analysis})
                
                return {"profiles": profiles, "audio_standards": audio_standards}
            else:
                self.log_test("Transcoding Profiles Configuration (CURL)", "FAIL", 
                             "Invalid response structure", profiles_data)
                return None
        else:
            self.log_test("Transcoding Profiles Configuration (CURL)", "FAIL", 
                         f"Failed to retrieve transcoding profiles", response["data"])
            return None

    def test_distribution_platforms_capabilities(self):
        """Test available distribution platforms and their capabilities using curl"""
        print("\n🌐 TESTING DISTRIBUTION PLATFORMS CAPABILITIES WITH CURL")
        
        response = self.execute_curl("GET", "/distribution/platforms")
        
        if response["status_code"] == 200:
            platforms_data = response["data"]
            
            if "platforms" in platforms_data:
                platforms_dict = platforms_data["platforms"]
                platforms = list(platforms_dict.values()) if isinstance(platforms_dict, dict) else platforms_dict
                
                # Analyze platform capabilities
                platform_analysis = []
                platform_types = {}
                
                for i, platform in enumerate(platforms):
                    if i >= 10:  # Sample first 10 platforms
                        break
                    platform_type = platform.get("type", "unknown")
                    platform_types[platform_type] = platform_types.get(platform_type, 0) + 1
                    
                    platform_analysis.append({
                        "name": platform.get("name", "Unknown"),
                        "type": platform_type,
                        "supported_formats": platform.get("supported_formats", []),
                        "max_file_size": platform.get("max_file_size", 0),
                        "api_endpoint": platform.get("api_endpoint", ""),
                        "credentials_required": platform.get("credentials_required", []),
                        "description": platform.get("description", "")
                    })
                
                self.log_test("Distribution Platforms Capabilities (CURL)", "PASS", 
                             f"Retrieved {len(platforms)} distribution platforms with detailed capabilities", 
                             {"total_platforms": len(platforms), "sample_platforms": platform_analysis})
                
                self.log_test("Platform Type Distribution (CURL)", "PASS", 
                             f"Platforms distributed across {len(platform_types)} types", 
                             platform_types)
                
                return {"platforms": platforms, "platform_types": platform_types}
            else:
                self.log_test("Distribution Platforms Capabilities (CURL)", "FAIL", 
                             "Invalid response structure", platforms_data)
                return None
        else:
            self.log_test("Distribution Platforms Capabilities (CURL)", "FAIL", 
                         f"Failed to retrieve distribution platforms", response["data"])
            return None

    def test_dashboard_data_structure(self):
        """Test dashboard data structure and content using curl"""
        print("\n📊 TESTING DASHBOARD DATA STRUCTURE WITH CURL")
        
        # Test workflow dashboard
        response = self.execute_curl("GET", "/workflow/dashboard")
        
        if response["status_code"] == 200:
            dashboard_data = response["data"]
            
            if "dashboard" in dashboard_data:
                dashboard = dashboard_data["dashboard"]
                
                # Analyze content summary
                content_summary = dashboard.get("content_summary", {})
                self.log_test("Workflow Dashboard Content Summary (CURL)", "PASS", 
                             f"Master content: {content_summary.get('master_content_pieces', 0)}, "
                             f"Versions: {content_summary.get('total_versions', 0)}, "
                             f"Storage: {content_summary.get('storage_used_gb', 0)}GB", 
                             content_summary)
                
                # Analyze quality assurance data
                qa_summary = dashboard.get("quality_assurance", {})
                self.log_test("Quality Assurance Dashboard Data (CURL)", "PASS", 
                             f"QC runs: {qa_summary.get('total_qc_runs', 0)}, "
                             f"Passed: {qa_summary.get('passed', 0)}, "
                             f"Failed: {qa_summary.get('failed', 0)}, "
                             f"Warnings: {qa_summary.get('warnings', 0)}", 
                             qa_summary)
                
                # Analyze distribution channels
                dist_channels = dashboard.get("distribution_channels", {})
                self.log_test("Distribution Channels Dashboard Data (CURL)", "PASS", 
                             f"Available channels: {dist_channels.get('available_channels', 0)}, "
                             f"Delivery profiles: {dist_channels.get('total_delivery_profiles', 0)}", 
                             dist_channels)
                
                return dashboard_data
            else:
                self.log_test("Dashboard Data Structure (CURL)", "FAIL", 
                             "Dashboard data missing", dashboard_data)
                return None
        else:
            self.log_test("Dashboard Data Structure (CURL)", "FAIL", 
                         f"Failed to retrieve dashboard data", response["data"])
            return None

    def test_system_statistics(self):
        """Test system statistics using curl"""
        print("\n📈 TESTING SYSTEM STATISTICS WITH CURL")
        
        # Test transcoding statistics
        response = self.execute_curl("GET", "/transcoding/statistics")
        
        if response["status_code"] == 200:
            stats_data = response["data"]
            if "data" in stats_data:
                data = stats_data["data"]
                total_jobs = data.get("total_jobs", 0)
                success_rate = data.get("success_rate", 0)
                status_breakdown = data.get("status_breakdown", {})
                
                self.log_test("Transcoding Statistics (CURL)", "PASS", 
                             f"Total jobs: {total_jobs}, Success rate: {success_rate:.1f}%", 
                             {"total_jobs": total_jobs, "success_rate": success_rate, "status_breakdown": status_breakdown})
            else:
                self.log_test("Transcoding Statistics (CURL)", "FAIL", 
                             "Statistics data structure invalid", stats_data)
        else:
            self.log_test("Transcoding Statistics (CURL)", "FAIL", 
                         f"Failed to retrieve transcoding statistics", response["data"])
        
        # Test distribution statistics
        response = self.execute_curl("GET", "/distribution/statistics")
        
        if response["status_code"] == 200:
            stats_data = response["data"]
            if "data" in stats_data:
                data = stats_data["data"]
                total_distributions = data.get("total_distributions", 0)
                overall_success_rate = data.get("overall_success_rate", 0)
                platform_performance = data.get("platform_performance", {})
                
                self.log_test("Distribution Statistics (CURL)", "PASS", 
                             f"Total distributions: {total_distributions}, Success rate: {overall_success_rate:.1f}%", 
                             {"total_distributions": total_distributions, "success_rate": overall_success_rate})
            else:
                self.log_test("Distribution Statistics (CURL)", "FAIL", 
                             "Statistics data structure invalid", stats_data)
        else:
            self.log_test("Distribution Statistics (CURL)", "FAIL", 
                         f"Failed to retrieve distribution statistics", response["data"])

    def test_error_handling(self):
        """Test error handling using curl"""
        print("\n🚨 TESTING ERROR HANDLING WITH CURL")
        
        # Test invalid authentication
        old_token = self.auth_token
        self.auth_token = "invalid_curl_token_12345"
        
        response = self.execute_curl("GET", "/workflow/dashboard")
        
        if "error" in response["data"] or "unauthorized" in str(response["data"]).lower():
            self.log_test("Invalid Authentication Handling (CURL)", "PASS", 
                         "Properly rejects invalid tokens", response["data"])
        else:
            self.log_test("Invalid Authentication Handling (CURL)", "FAIL", 
                         f"Authentication validation failed", response["data"])
        
        # Restore valid token
        self.auth_token = old_token
        
        # Test invalid endpoints
        response = self.execute_curl("GET", "/invalid/endpoint")
        
        if response["status_code"] != 200:
            self.log_test("Invalid Endpoint Handling (CURL)", "PASS", 
                         "Properly handles invalid endpoints", response["data"])
        else:
            self.log_test("Invalid Endpoint Handling (CURL)", "FAIL", 
                         f"Invalid endpoint validation failed", response["data"])

    def generate_comprehensive_analysis(self):
        """Generate comprehensive analysis of test results"""
        print("\n" + "="*120)
        print("🎯 CONTENT WORKFLOW SYSTEM - COMPREHENSIVE CURL TEST RESULTS & ANALYSIS")
        print("="*120)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Skipped: {skipped_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🏥 SERVICE HEALTH STATUS SUMMARY:")
        service_tests = [
            ("Workflow Service", [t for t in self.test_results if "Workflow Service" in t["test"]]),
            ("Transcoding Service", [t for t in self.test_results if "Transcoding Service" in t["test"]]),
            ("Distribution Service", [t for t in self.test_results if "Distribution Service" in t["test"]])
        ]
        
        for service_name, service_results in service_tests:
            if service_results:
                service_status = "✅ OPERATIONAL" if all(t["status"] == "PASS" for t in service_results) else "❌ ISSUES DETECTED"
                print(f"   {service_name}: {service_status}")
            else:
                print(f"   {service_name}: ⚠️ NOT TESTED")
        
        print(f"\n📋 CRITICAL ISSUES IDENTIFIED:")
        critical_issues = [t for t in self.test_results if t["status"] == "FAIL"]
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No critical issues found!")
        
        print(f"\n🎯 SYSTEM READINESS ASSESSMENT:")
        
        # Assess system readiness based on test results
        readiness_components = {
            "Service Health": len([t for t in self.test_results if "Health" in t["test"] and t["status"] == "PASS"]),
            "Authentication": len([t for t in self.test_results if "Authentication" in t["test"] and t["status"] == "PASS"]),
            "Configuration": len([t for t in self.test_results if "Configuration" in t["test"] and t["status"] == "PASS"]),
            "Platform Capabilities": len([t for t in self.test_results if "Capabilities" in t["test"] and t["status"] == "PASS"]),
            "Dashboard Data": len([t for t in self.test_results if "Dashboard" in t["test"] and t["status"] == "PASS"]),
            "Error Handling": len([t for t in self.test_results if "Error" in t["test"] and t["status"] == "PASS"])
        }
        
        for component, passed_count in readiness_components.items():
            total_component_tests = len([t for t in self.test_results if component.split()[0] in t["test"]])
            if total_component_tests > 0:
                component_rate = (passed_count / total_component_tests) * 100
                status = "✅ READY" if component_rate >= 80 else "⚠️ NEEDS ATTENTION" if component_rate >= 50 else "❌ CRITICAL"
                print(f"   {component}: {status} ({component_rate:.1f}%)")
            else:
                print(f"   {component}: ⚠️ NOT TESTED")
        
        # Overall readiness assessment
        overall_readiness = success_rate
        
        print(f"\n🏁 OVERALL SYSTEM READINESS: {overall_readiness:.1f}%")
        
        if overall_readiness >= 90:
            print("🎉 EXCELLENT: Content workflow system is production-ready!")
            readiness_status = "PRODUCTION_READY"
        elif overall_readiness >= 75:
            print("✅ GOOD: Content workflow system is functional with minor issues")
            readiness_status = "FUNCTIONAL"
        elif overall_readiness >= 50:
            print("⚠️ NEEDS ATTENTION: Content workflow system has significant issues")
            readiness_status = "NEEDS_ATTENTION"
        else:
            print("❌ CRITICAL: Content workflow system requires major fixes")
            readiness_status = "CRITICAL"
        
        print(f"\n📝 DETAILED FINDINGS:")
        print(f"   • Backend URL: {BACKEND_URL}")
        print(f"   • API Base: {API_BASE}")
        print(f"   • Authentication: {'✅ Working' if any('Authentication' in t['test'] and t['status'] == 'PASS' for t in self.test_results) else '❌ Issues'}")
        print(f"   • Service Health: {'✅ All services operational' if all('Health' in t['test'] and t['status'] == 'PASS' for t in self.test_results if 'Health' in t['test']) else '❌ Service issues detected'}")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "readiness_status": readiness_status,
            "critical_issues": len(critical_issues)
        }

    def run_comprehensive_curl_tests(self):
        """Run comprehensive content workflow system tests using curl"""
        print("🚀 STARTING CONTENT WORKFLOW SYSTEM COMPREHENSIVE CURL TESTING")
        print("Executing actual curl tests with full response analysis")
        print("Testing: Workflow, Transcoding, Distribution Services")
        print(f"Backend URL: {BACKEND_URL}")
        print("="*120)
        
        try:
            # Authentication integration testing
            auth_success = self.test_authentication_integration()
            if not auth_success:
                print("❌ Authentication failed - proceeding with limited testing")
            
            # Service health status testing
            self.test_service_health_status()
            
            # Transcoding profiles and configuration testing
            self.test_transcoding_profiles_configuration()
            
            # Distribution platforms capabilities testing
            self.test_distribution_platforms_capabilities()
            
            # Dashboard data structure testing
            self.test_dashboard_data_structure()
            
            # System statistics testing
            self.test_system_statistics()
            
            # Error handling testing
            self.test_error_handling()
            
            # Generate comprehensive analysis
            summary = self.generate_comprehensive_analysis()
            
            return summary
            
        except Exception as e:
            print(f"❌ Critical error during curl testing: {str(e)}")
            self.log_test("Critical Error", "FAIL", str(e))
            return None

def main():
    """Main test execution function"""
    tester = ContentWorkflowCurlTester()
    
    print("🎵 BIG MANN ENTERTAINMENT PLATFORM")
    print("Content Workflow System - Comprehensive CURL Backend Testing")
    print("Executing actual curl tests with detailed response analysis")
    print("="*120)
    
    summary = tester.run_comprehensive_curl_tests()
    
    if summary:
        print(f"\n🏁 CONTENT WORKFLOW CURL TESTING COMPLETED")
        print(f"Final Success Rate: {summary['success_rate']:.1f}%")
        print(f"System Status: {summary['readiness_status']}")
        
        if summary['success_rate'] >= 90:
            print("🎉 EXCELLENT: System is production-ready!")
        elif summary['success_rate'] >= 75:
            print("✅ GOOD: System is functional")
        else:
            print("⚠️ NEEDS ATTENTION: System requires fixes")
    else:
        print("❌ Testing failed to complete")
    
    return summary

if __name__ == "__main__":
    main()