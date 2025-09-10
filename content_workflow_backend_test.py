#!/usr/bin/env python3
"""
Content Workflow System Comprehensive Backend Testing
Testing the complete content workflow system with three main services:
1. Workflow Service - Content ingestion, versioning, QC
2. Transcoding Service - Format optimization and transcoding profiles  
3. Distribution Service - Platform distribution and delivery management

This test suite provides detailed analysis of:
- Service health status for all three services
- Available transcoding profiles and configurations
- Available distribution platforms and capabilities
- Dashboard data structure and content
- Authentication integration testing
- Error handling and system readiness assessment
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class ContentWorkflowTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "workflow.tester@bigmannentertainment.com"
        self.test_user_password = "WorkflowTest2025!"
        self.test_results = []
        self.content_id = None
        self.version_id = None
        self.distribution_id = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
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
                
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          files: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request with comprehensive error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add auth header if available
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers, params=data) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                if files:
                    # Handle file upload
                    form_data = aiohttp.FormData()
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, str(value))
                    for key, file_data in files.items():
                        form_data.add_field(key, file_data[1], filename=file_data[0])
                    
                    async with self.session.post(url, data=form_data, headers=headers) as response:
                        response_text = await response.text()
                        try:
                            response_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            response_data = {"raw_response": response_text}
                        return {
                            "status": response.status,
                            "data": response_data,
                            "headers": dict(response.headers)
                        }
                else:
                    # Handle JSON data
                    json_headers = headers or {}
                    json_headers["Content-Type"] = "application/json"
                    async with self.session.post(url, json=data, headers=json_headers) as response:
                        response_text = await response.text()
                        try:
                            response_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            response_data = {"raw_response": response_text}
                        return {
                            "status": response.status,
                            "data": response_data,
                            "headers": dict(response.headers)
                        }
            else:
                # Handle other methods
                async with self.session.request(method, url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
                    
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }

    async def test_authentication_integration(self):
        """Test authentication integration for workflow system"""
        print("\n🔐 TESTING AUTHENTICATION INTEGRATION")
        
        # Test user registration
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": "Workflow Tester",
            "date_of_birth": "1990-01-01T00:00:00",
            "address_line1": "123 Workflow Street",
            "city": "Content City",
            "state_province": "CA",
            "postal_code": "90210",
            "country": "USA"
        }
        
        response = await self.make_request("POST", "/auth/register", registration_data)
        
        if response["status"] == 201:
            self.log_test("User Registration", "PASS", "New workflow user registered successfully", response["data"])
            if "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
        elif response["status"] == 400 and "already registered" in str(response["data"]).lower():
            self.log_test("User Registration", "PASS", "User already exists, proceeding to login", response["data"])
        else:
            self.log_test("User Registration", "FAIL", f"Status: {response['status']}", response["data"])
            
        # Test user login if registration failed or user exists
        if not self.auth_token:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = await self.make_request("POST", "/auth/login", login_data)
            
            if response["status"] == 200 and "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
                self.log_test("User Login", "PASS", "Authentication successful", response["data"])
            else:
                self.log_test("User Login", "FAIL", f"Status: {response['status']}", response["data"])
                return False
                
        # Test authenticated user profile
        response = await self.make_request("GET", "/auth/me")
        
        if response["status"] == 200:
            self.log_test("User Profile Access", "PASS", "Profile retrieved successfully", response["data"])
        else:
            self.log_test("User Profile Access", "FAIL", f"Status: {response['status']}", response["data"])
            
        return True

    async def test_workflow_service_health(self):
        """Test workflow service health and status"""
        print("\n🔄 TESTING WORKFLOW SERVICE HEALTH")
        
        response = await self.make_request("GET", "/workflow/health")
        
        if response["status"] == 200:
            health_data = response["data"]
            components = health_data.get("components", {})
            
            # Analyze service components
            component_status = []
            for component, status in components.items():
                component_status.append(f"{component}: {status}")
            
            self.log_test("Workflow Service Health", "PASS", 
                         f"Service healthy with components: {', '.join(component_status)}", 
                         health_data)
            
            # Verify all critical components are operational
            critical_components = ["master_intake", "versioning", "technical_qc", "transcoding", "distribution"]
            all_operational = all(components.get(comp) == "operational" for comp in critical_components)
            
            if all_operational:
                self.log_test("Workflow Components Status", "PASS", 
                             "All critical workflow components operational", components)
            else:
                self.log_test("Workflow Components Status", "FAIL", 
                             "Some workflow components not operational", components)
        else:
            self.log_test("Workflow Service Health", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_workflow_dashboard_data(self):
        """Test workflow dashboard data structure and content"""
        print("\n📊 TESTING WORKFLOW DASHBOARD DATA")
        
        response = await self.make_request("GET", "/workflow/dashboard")
        
        if response["status"] == 200:
            dashboard_data = response["data"]
            
            if "dashboard" in dashboard_data:
                dashboard = dashboard_data["dashboard"]
                
                # Analyze content summary
                content_summary = dashboard.get("content_summary", {})
                self.log_test("Content Summary Data", "PASS", 
                             f"Master content: {content_summary.get('master_content_pieces', 0)}, "
                             f"Versions: {content_summary.get('total_versions', 0)}, "
                             f"Storage: {content_summary.get('storage_used_gb', 0)}GB", 
                             content_summary)
                
                # Analyze quality assurance data
                qa_summary = dashboard.get("quality_assurance", {})
                self.log_test("Quality Assurance Data", "PASS", 
                             f"QC runs: {qa_summary.get('total_qc_runs', 0)}, "
                             f"Passed: {qa_summary.get('passed', 0)}, "
                             f"Failed: {qa_summary.get('failed', 0)}, "
                             f"Warnings: {qa_summary.get('warnings', 0)}", 
                             qa_summary)
                
                # Analyze distribution channels
                dist_channels = dashboard.get("distribution_channels", {})
                self.log_test("Distribution Channels Data", "PASS", 
                             f"Available channels: {dist_channels.get('available_channels', 0)}, "
                             f"Delivery profiles: {dist_channels.get('total_delivery_profiles', 0)}", 
                             dist_channels)
                
                self.log_test("Dashboard Structure", "PASS", "Complete dashboard data structure verified", dashboard_data)
            else:
                self.log_test("Dashboard Structure", "FAIL", "Dashboard data missing", dashboard_data)
        else:
            self.log_test("Workflow Dashboard", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_transcoding_service_health(self):
        """Test transcoding service health and available profiles"""
        print("\n🎬 TESTING TRANSCODING SERVICE HEALTH")
        
        response = await self.make_request("GET", "/transcoding/health")
        
        if response["status"] == 200:
            health_data = response["data"]
            
            # Analyze supported profiles
            supported_profiles = health_data.get("supported_profiles", [])
            audio_standards = health_data.get("audio_standards", [])
            
            self.log_test("Transcoding Service Health", "PASS", 
                         f"Service healthy with {len(supported_profiles)} profiles and {len(audio_standards)} audio standards", 
                         health_data)
            
            # Test transcoding profiles endpoint
            profiles_response = await self.make_request("GET", "/transcoding/profiles")
            
            if profiles_response["status"] == 200:
                profiles_data = profiles_response["data"]
                profiles = profiles_data.get("data", {}).get("profiles", [])
                
                # Analyze profile configurations
                profile_analysis = []
                for profile in profiles:
                    profile_name = profile.get("name", "Unknown")
                    container = profile.get("container", "Unknown")
                    video_specs = profile.get("video_specs", {})
                    audio_specs = profile.get("audio_specs", {})
                    
                    profile_analysis.append({
                        "name": profile_name,
                        "container": container,
                        "video_resolution": video_specs.get("resolution"),
                        "video_bitrate": video_specs.get("bitrate"),
                        "audio_bitrate": audio_specs.get("bitrate"),
                        "audio_sample_rate": audio_specs.get("sample_rate")
                    })
                
                self.log_test("Transcoding Profiles Configuration", "PASS", 
                             f"Retrieved {len(profiles)} transcoding profiles with detailed configurations", 
                             {"profiles_count": len(profiles), "sample_profiles": profile_analysis[:3]})
                
                # Analyze audio standards
                audio_standards_data = profiles_data.get("data", {}).get("audio_standards", [])
                standards_analysis = []
                for standard in audio_standards_data:
                    standards_analysis.append({
                        "standard": standard.get("standard"),
                        "description": standard.get("description")
                    })
                
                self.log_test("Audio Standards Configuration", "PASS", 
                             f"Retrieved {len(audio_standards_data)} audio standards", 
                             {"standards": standards_analysis})
            else:
                self.log_test("Transcoding Profiles", "FAIL", f"Status: {profiles_response['status']}", profiles_response["data"])
        else:
            self.log_test("Transcoding Service Health", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_distribution_service_health(self):
        """Test distribution service health and platform capabilities"""
        print("\n🌐 TESTING DISTRIBUTION SERVICE HEALTH")
        
        response = await self.make_request("GET", "/distribution/health")
        
        if response["status"] == 200:
            health_data = response["data"]
            
            available_platforms = health_data.get("available_platforms", 0)
            delivery_methods = health_data.get("supported_delivery_methods", [])
            platform_types = health_data.get("platform_types", [])
            
            self.log_test("Distribution Service Health", "PASS", 
                         f"Service healthy with {available_platforms} platforms, "
                         f"{len(delivery_methods)} delivery methods, "
                         f"{len(platform_types)} platform types", 
                         health_data)
            
            # Test platform connectors endpoint
            platforms_response = await self.make_request("GET", "/distribution/platforms")
            
            if platforms_response["status"] == 200:
                platforms_data = platforms_response["data"]
                connectors = platforms_data.get("data", {}).get("connectors", [])
                platforms_by_type = platforms_data.get("data", {}).get("platforms_by_type", {})
                
                # Analyze platform capabilities
                platform_analysis = []
                for connector in connectors[:5]:  # Sample first 5 platforms
                    platform_analysis.append({
                        "platform_name": connector.get("platform_name"),
                        "platform_type": connector.get("platform_type"),
                        "supported_formats": connector.get("supported_formats", []),
                        "max_file_size_mb": connector.get("max_file_size_mb"),
                        "authentication_method": connector.get("authentication_method"),
                        "metadata_requirements": len(connector.get("metadata_requirements", []))
                    })
                
                self.log_test("Distribution Platform Capabilities", "PASS", 
                             f"Retrieved {len(connectors)} platform connectors with detailed capabilities", 
                             {"total_platforms": len(connectors), "sample_platforms": platform_analysis})
                
                # Analyze platform distribution by type
                type_distribution = {}
                for ptype, platforms in platforms_by_type.items():
                    type_distribution[ptype] = len(platforms)
                
                self.log_test("Platform Type Distribution", "PASS", 
                             f"Platforms distributed across {len(type_distribution)} types", 
                             type_distribution)
            else:
                self.log_test("Distribution Platforms", "FAIL", f"Status: {platforms_response['status']}", platforms_response["data"])
        else:
            self.log_test("Distribution Service Health", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_content_workflow_operations(self):
        """Test end-to-end content workflow operations"""
        print("\n📁 TESTING CONTENT WORKFLOW OPERATIONS")
        
        # Test content ingestion
        test_content = b"RIFF\x24\x08WAVEfmt \x10\x01\x02\x44\xac\x10\xb1\x02\x04\x10data\x08" + b"test_audio_content" * 100
        
        files = {
            "file": ("workflow_test.wav", test_content, "audio/wav")
        }
        
        ingest_data = {
            "content_type": "audio",
            "title": "Workflow Test Content",
            "description": "Test content for workflow system validation"
        }
        
        response = await self.make_request("POST", "/workflow/ingest", ingest_data, files=files)
        
        if response["status"] == 200:
            ingest_result = response["data"]
            if "data" in ingest_result and "content_id" in ingest_result["data"]:
                self.content_id = ingest_result["data"]["content_id"]
                
                self.log_test("Content Ingestion", "PASS", 
                             f"Content ingested successfully with ID: {self.content_id}", 
                             ingest_result["data"])
                
                # Test content version creation
                version_data = {
                    "quality_profile": "high_quality",
                    "version_name": "Test Version 1.0",
                    "changes_summary": "Initial version for workflow testing"
                }
                
                version_response = await self.make_request("POST", f"/workflow/content/{self.content_id}/version", version_data)
                
                if version_response["status"] == 200:
                    version_result = version_response["data"]
                    if "data" in version_result and "version_id" in version_result["data"]:
                        self.version_id = version_result["data"]["version_id"]
                        
                        self.log_test("Content Versioning", "PASS", 
                                     f"Version created successfully with ID: {self.version_id}", 
                                     version_result["data"])
                        
                        # Test technical QC
                        qc_response = await self.make_request("POST", f"/workflow/qc/{self.version_id}")
                        
                        if qc_response["status"] == 200:
                            qc_result = qc_response["data"]
                            qc_data = qc_result.get("data", {})
                            
                            self.log_test("Technical Quality Control", "PASS", 
                                         f"QC completed with status: {qc_data.get('overall_status')}, "
                                         f"Score: {qc_data.get('qc_score')}", 
                                         qc_data)
                        else:
                            self.log_test("Technical Quality Control", "FAIL", f"Status: {qc_response['status']}", qc_response["data"])
                    else:
                        self.log_test("Content Versioning", "FAIL", "Version ID not returned", version_result)
                else:
                    self.log_test("Content Versioning", "FAIL", f"Status: {version_response['status']}", version_response["data"])
            else:
                self.log_test("Content Ingestion", "FAIL", "Content ID not returned", ingest_result)
        else:
            self.log_test("Content Ingestion", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_workflow_enums_and_configuration(self):
        """Test workflow enums and configuration endpoints"""
        print("\n⚙️ TESTING WORKFLOW CONFIGURATION")
        
        # Test workflow enums
        response = await self.make_request("GET", "/workflow/enums")
        
        if response["status"] == 200:
            enums_data = response["data"]
            
            content_types = enums_data.get("content_types", [])
            quality_profiles = enums_data.get("quality_profiles", [])
            distribution_channels = enums_data.get("distribution_channels", [])
            workflow_stages = enums_data.get("workflow_stages", [])
            
            self.log_test("Workflow Enums", "PASS", 
                         f"Retrieved enums - Content types: {len(content_types)}, "
                         f"Quality profiles: {len(quality_profiles)}, "
                         f"Distribution channels: {len(distribution_channels)}, "
                         f"Workflow stages: {len(workflow_stages)}", 
                         enums_data)
        else:
            self.log_test("Workflow Enums", "FAIL", f"Status: {response['status']}", response["data"])
        
        # Test delivery profiles
        response = await self.make_request("GET", "/workflow/delivery-profiles")
        
        if response["status"] == 200:
            profiles_data = response["data"]
            
            if "data" in profiles_data:
                data = profiles_data["data"]
                profiles = data.get("profiles", [])
                profiles_by_channel = data.get("profiles_by_channel", {})
                available_channels = data.get("available_channels", [])
                
                self.log_test("Delivery Profiles", "PASS", 
                             f"Retrieved {len(profiles)} delivery profiles across {len(available_channels)} channels", 
                             {"total_profiles": len(profiles), "channels": available_channels})
            else:
                self.log_test("Delivery Profiles", "FAIL", "Delivery profiles data structure invalid", profiles_data)
        else:
            self.log_test("Delivery Profiles", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_error_handling_and_edge_cases(self):
        """Test error handling and edge cases"""
        print("\n🚨 TESTING ERROR HANDLING")
        
        # Test invalid authentication
        old_token = self.auth_token
        self.auth_token = "invalid_workflow_token_12345"
        
        response = await self.make_request("GET", "/workflow/dashboard")
        
        if response["status"] == 401:
            self.log_test("Invalid Authentication Handling", "PASS", "Properly rejects invalid tokens", response["data"])
        else:
            self.log_test("Invalid Authentication Handling", "FAIL", f"Status: {response['status']}", response["data"])
        
        # Restore valid token
        self.auth_token = old_token
        
        # Test invalid content ID
        response = await self.make_request("GET", "/workflow/content/invalid_content_id_12345")
        
        if response["status"] == 404:
            self.log_test("Invalid Content ID Handling", "PASS", "Properly handles non-existent content", response["data"])
        else:
            self.log_test("Invalid Content ID Handling", "FAIL", f"Status: {response['status']}", response["data"])
        
        # Test invalid transcoding job
        response = await self.make_request("GET", "/transcoding/jobs/invalid_job_id_12345")
        
        if response["status"] == 404:
            self.log_test("Invalid Transcoding Job Handling", "PASS", "Properly handles non-existent jobs", response["data"])
        else:
            self.log_test("Invalid Transcoding Job Handling", "FAIL", f"Status: {response['status']}", response["data"])
        
        # Test invalid distribution job
        response = await self.make_request("GET", "/distribution/jobs/invalid_distribution_id_12345")
        
        if response["status"] == 404:
            self.log_test("Invalid Distribution Job Handling", "PASS", "Properly handles non-existent distributions", response["data"])
        else:
            self.log_test("Invalid Distribution Job Handling", "FAIL", f"Status: {response['status']}", response["data"])

    async def test_system_statistics_and_monitoring(self):
        """Test system statistics and monitoring endpoints"""
        print("\n📈 TESTING SYSTEM STATISTICS")
        
        # Test transcoding statistics
        response = await self.make_request("GET", "/transcoding/statistics")
        
        if response["status"] == 200:
            stats_data = response["data"]
            if "data" in stats_data:
                data = stats_data["data"]
                total_jobs = data.get("total_jobs", 0)
                success_rate = data.get("success_rate", 0)
                status_breakdown = data.get("status_breakdown", {})
                
                self.log_test("Transcoding Statistics", "PASS", 
                             f"Total jobs: {total_jobs}, Success rate: {success_rate:.1f}%", 
                             {"total_jobs": total_jobs, "success_rate": success_rate, "status_breakdown": status_breakdown})
            else:
                self.log_test("Transcoding Statistics", "FAIL", "Statistics data structure invalid", stats_data)
        else:
            self.log_test("Transcoding Statistics", "FAIL", f"Status: {response['status']}", response["data"])
        
        # Test distribution statistics
        response = await self.make_request("GET", "/distribution/statistics")
        
        if response["status"] == 200:
            stats_data = response["data"]
            if "data" in stats_data:
                data = stats_data["data"]
                total_distributions = data.get("total_distributions", 0)
                overall_success_rate = data.get("overall_success_rate", 0)
                platform_performance = data.get("platform_performance", {})
                
                self.log_test("Distribution Statistics", "PASS", 
                             f"Total distributions: {total_distributions}, Success rate: {overall_success_rate:.1f}%", 
                             {"total_distributions": total_distributions, "success_rate": overall_success_rate})
            else:
                self.log_test("Distribution Statistics", "FAIL", "Statistics data structure invalid", stats_data)
        else:
            self.log_test("Distribution Statistics", "FAIL", f"Status: {response['status']}", response["data"])

    def generate_comprehensive_summary(self):
        """Generate comprehensive test summary with detailed analysis"""
        print("\n" + "="*100)
        print("🎯 CONTENT WORKFLOW SYSTEM - COMPREHENSIVE TEST RESULTS")
        print("="*100)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Skipped: {skipped_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 SERVICE HEALTH STATUS:")
        service_tests = [
            ("Workflow Service", [t for t in self.test_results if "Workflow Service" in t["test"]]),
            ("Transcoding Service", [t for t in self.test_results if "Transcoding Service" in t["test"]]),
            ("Distribution Service", [t for t in self.test_results if "Distribution Service" in t["test"]])
        ]
        
        for service_name, service_results in service_tests:
            if service_results:
                service_status = "✅ HEALTHY" if all(t["status"] == "PASS" for t in service_results) else "❌ ISSUES"
                print(f"   {service_name}: {service_status}")
            else:
                print(f"   {service_name}: ⚠️ NOT TESTED")
        
        print(f"\n📋 CRITICAL FINDINGS:")
        critical_issues = [t for t in self.test_results if t["status"] == "FAIL"]
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No critical issues found!")
        
        print(f"\n🎉 SYSTEM READINESS ASSESSMENT:")
        
        # Assess workflow system readiness
        workflow_components = [
            "Workflow Service Health",
            "Transcoding Service Health", 
            "Distribution Service Health",
            "Authentication Integration",
            "Dashboard Data Structure"
        ]
        
        component_status = {}
        for component in workflow_components:
            matching_tests = [t for t in self.test_results if component in t["test"]]
            if matching_tests:
                component_status[component] = "✅ READY" if all(t["status"] == "PASS" for t in matching_tests) else "❌ ISSUES"
            else:
                component_status[component] = "⚠️ NOT TESTED"
        
        for component, status in component_status.items():
            print(f"   {component}: {status}")
        
        # Overall readiness assessment
        ready_components = len([s for s in component_status.values() if "READY" in s])
        total_components = len(component_status)
        readiness_percentage = (ready_components / total_components * 100) if total_components > 0 else 0
        
        print(f"\n🏁 OVERALL SYSTEM READINESS: {readiness_percentage:.1f}%")
        
        if readiness_percentage >= 90:
            print("🎉 EXCELLENT: Content workflow system is production-ready!")
        elif readiness_percentage >= 75:
            print("✅ GOOD: Content workflow system is functional with minor issues")
        elif readiness_percentage >= 50:
            print("⚠️ NEEDS ATTENTION: Content workflow system has significant issues")
        else:
            print("❌ CRITICAL: Content workflow system requires major fixes")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": success_rate,
            "readiness_percentage": readiness_percentage,
            "critical_issues": len(critical_issues),
            "service_status": {service: status for service, status in component_status.items()}
        }

    async def run_comprehensive_workflow_tests(self):
        """Run comprehensive content workflow system tests"""
        print("🚀 STARTING CONTENT WORKFLOW SYSTEM COMPREHENSIVE TESTING")
        print("Testing Complete Content Workflow System for Big Mann Entertainment")
        print("Services: Workflow, Transcoding, Distribution")
        print("="*100)
        
        try:
            await self.setup_session()
            
            # Authentication integration testing
            auth_success = await self.test_authentication_integration()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with workflow tests")
                return
            
            # Core service health testing
            await self.test_workflow_service_health()
            await self.test_transcoding_service_health()
            await self.test_distribution_service_health()
            
            # Dashboard and configuration testing
            await self.test_workflow_dashboard_data()
            await self.test_workflow_enums_and_configuration()
            
            # End-to-end workflow testing
            await self.test_content_workflow_operations()
            
            # System monitoring and statistics
            await self.test_system_statistics_and_monitoring()
            
            # Error handling and edge cases
            await self.test_error_handling_and_edge_cases()
            
            # Generate comprehensive summary
            summary = self.generate_comprehensive_summary()
            
            return summary
            
        except Exception as e:
            print(f"❌ Critical error during workflow testing: {str(e)}")
            self.log_test("Critical Error", "FAIL", str(e))
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = ContentWorkflowTester()
    
    print("🎵 BIG MANN ENTERTAINMENT PLATFORM")
    print("Content Workflow System Comprehensive Backend Testing")
    print("Testing Workflow, Transcoding, and Distribution Services")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*100)
    
    summary = await tester.run_comprehensive_workflow_tests()
    
    if summary:
        print(f"\n🏁 CONTENT WORKFLOW TESTING COMPLETED")
        print(f"Final Success Rate: {summary['success_rate']:.1f}%")
        print(f"System Readiness: {summary['readiness_percentage']:.1f}%")
        
        if summary['readiness_percentage'] >= 90:
            print("🎉 EXCELLENT: Content workflow system is production-ready!")
        elif summary['readiness_percentage'] >= 75:
            print("✅ GOOD: Content workflow system is functional")
        else:
            print("⚠️ NEEDS ATTENTION: Content workflow system requires fixes")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())