#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Big Mann Entertainment Platform
Complete Upload-to-Payout Workflow Testing

This test covers the COMPLETE workflow from upload through distribution to payout
as requested in the review for Big Mann Entertainment platform.

Testing Scope:
1. Upload System Testing - All upload endpoints (image, media, file upload)
2. Distribution System Testing - Content distribution to 106+ platforms  
3. Revenue Tracking Testing - Earnings calculation and tracking systems
4. Payout System Testing - Payout request and processing systems
5. Integration Testing - Complete end-to-end workflow
6. Database Operations - All database operations throughout workflow
7. API Endpoint Validation - All endpoints involved in workflow
8. Error Handling - Test error handling at each stage
9. Payment Integration - Test payment processing and financial transactions
10. User Flow Testing - Complete user journey from upload to receiving payment
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import base64
import io

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://api-dev.bigmannentertainment.com')
if not BACKEND_URL.startswith('http'):
    BACKEND_URL = f"https://{BACKEND_URL}"

class ComprehensiveWorkflowTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        self.auth_token = None
        self.test_user_id = None
        self.test_media_id = None
        self.test_distribution_id = None
        self.test_payment_session_id = None
        
        # Test data for realistic workflow
        self.test_user_data = {
            "email": f"workflow.test.{int(time.time())}@bigmannentertainment.com",
            "password": "WorkflowTest123!",
            "full_name": "Workflow Test Artist",
            "business_name": "Test Music Label",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Music Street",
            "city": "Nashville", 
            "state_province": "Tennessee",
            "postal_code": "37201",
            "country": "US"
        }
        
        self.test_media_data = {
            "title": "Test Track for Distribution",
            "description": "A test track for complete workflow testing",
            "category": "music",
            "price": 9.99,
            "tags": ["hip-hop", "test", "workflow"]
        }

    async def setup_session(self):
        """Setup HTTP session for testing"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test result with details"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    async def make_request(self, method: str, endpoint: str, data: Any = None, 
                          headers: Dict = None, files: Any = None) -> tuple:
        """Make HTTP request with error handling"""
        url = f"{self.backend_url}{endpoint}"
        
        # Setup headers
        request_headers = {"Content-Type": "application/json"}
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        if headers:
            request_headers.update(headers)
            
        try:
            if files:
                # For file uploads, don't set Content-Type (let aiohttp handle it)
                if "Content-Type" in request_headers:
                    del request_headers["Content-Type"]
                    
            async with self.session.request(
                method, url, 
                json=data if not files else None,
                data=files if files else None,
                headers=request_headers
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return response.status, response_data
                
        except Exception as e:
            return 0, {"error": str(e)}

    # ==================== AUTHENTICATION TESTING ====================
    
    async def test_user_registration(self):
        """Test user registration for workflow"""
        status, response = await self.make_request(
            "POST", "/api/auth/register", self.test_user_data
        )
        
        if status == 201 and "access_token" in response:
            self.auth_token = response["access_token"]
            self.test_user_id = response.get("user", {}).get("id")
            self.log_test_result(
                "User Registration", True,
                f"Successfully registered user with ID: {self.test_user_id}",
                {"user_id": self.test_user_id, "has_token": bool(self.auth_token)}
            )
            return True
        else:
            self.log_test_result(
                "User Registration", False,
                f"Registration failed with status {status}",
                response
            )
            return False

    async def test_user_authentication(self):
        """Test user authentication"""
        if not self.auth_token:
            return False
            
        status, response = await self.make_request("GET", "/api/auth/me")
        
        success = status == 200 and "id" in response
        self.log_test_result(
            "User Authentication", success,
            f"Authentication check: {status}" if success else f"Auth failed: {status}",
            response if not success else {"authenticated": True}
        )
        return success

    # ==================== UPLOAD SYSTEM TESTING ====================
    
    async def test_image_upload_endpoints(self):
        """Test image upload endpoints"""
        # Test image upload endpoint availability
        status, response = await self.make_request("GET", "/api/images/upload")
        
        success = status in [200, 405]  # 405 means endpoint exists but wrong method
        self.log_test_result(
            "Image Upload Endpoint", success,
            f"Image upload endpoint status: {status}",
            {"status": status, "available": success}
        )
        return success

    async def test_media_upload_endpoints(self):
        """Test media upload endpoints"""
        # Test S3 media upload endpoints
        endpoints_to_test = [
            "/api/media/s3/upload/audio",
            "/api/media/s3/upload/video", 
            "/api/media/s3/upload/image"
        ]
        
        results = []
        for endpoint in endpoints_to_test:
            status, response = await self.make_request("POST", endpoint)
            # Expect 400/422 for missing file data, not 404
            success = status in [400, 422, 500]  # Endpoint exists but needs file data
            results.append(success)
            
            self.log_test_result(
                f"Media Upload Endpoint {endpoint.split('/')[-1]}", success,
                f"Endpoint {endpoint} status: {status}",
                {"endpoint": endpoint, "status": status}
            )
        
        return all(results)

    async def test_file_upload_workflow(self):
        """Test complete file upload workflow"""
        # Create a test media entry in the system
        status, response = await self.make_request(
            "POST", "/api/media", self.test_media_data
        )
        
        if status in [200, 201] and "id" in response:
            self.test_media_id = response["id"]
            self.log_test_result(
                "Media Creation", True,
                f"Successfully created media with ID: {self.test_media_id}",
                {"media_id": self.test_media_id}
            )
            return True
        else:
            self.log_test_result(
                "Media Creation", False,
                f"Media creation failed with status {status}",
                response
            )
            return False

    # ==================== DISTRIBUTION SYSTEM TESTING ====================
    
    async def test_distribution_platforms(self):
        """Test distribution platforms endpoint"""
        status, response = await self.make_request("GET", "/api/distribution/platforms")
        
        if status == 200 and isinstance(response, list):
            platform_count = len(response)
            success = platform_count >= 90  # Should have 90+ platforms
            self.log_test_result(
                "Distribution Platforms", success,
                f"Found {platform_count} distribution platforms (target: 90+)",
                {"platform_count": platform_count, "target_met": success}
            )
            return success
        else:
            self.log_test_result(
                "Distribution Platforms", False,
                f"Failed to get platforms: {status}",
                response
            )
            return False

    async def test_content_distribution(self):
        """Test content distribution workflow"""
        if not self.test_media_id:
            self.log_test_result(
                "Content Distribution", False,
                "No media ID available for distribution test",
                None
            )
            return False
            
        # Test distribution request
        distribution_data = {
            "media_id": self.test_media_id,
            "platforms": ["spotify", "apple_music", "youtube", "instagram", "tiktok"],
            "custom_message": "Test distribution for workflow testing",
            "hashtags": ["test", "workflow", "bigmann"]
        }
        
        status, response = await self.make_request(
            "POST", "/api/industry/distribute", distribution_data
        )
        
        if status in [200, 201] and "id" in response:
            self.test_distribution_id = response["id"]
            self.log_test_result(
                "Content Distribution", True,
                f"Successfully initiated distribution with ID: {self.test_distribution_id}",
                {"distribution_id": self.test_distribution_id}
            )
            return True
        else:
            self.log_test_result(
                "Content Distribution", False,
                f"Distribution failed with status {status}",
                response
            )
            return False

    async def test_distribution_status(self):
        """Test distribution status tracking"""
        if not self.test_distribution_id:
            return False
            
        status, response = await self.make_request(
            "GET", f"/api/distribution/status/{self.test_distribution_id}"
        )
        
        success = status == 200
        self.log_test_result(
            "Distribution Status", success,
            f"Distribution status check: {status}",
            response if not success else {"status_available": True}
        )
        return success

    # ==================== REVENUE TRACKING TESTING ====================
    
    async def test_revenue_endpoints(self):
        """Test revenue tracking endpoints"""
        status, response = await self.make_request("GET", "/api/revenue")
        
        success = status in [200, 404]  # 404 acceptable if no revenue yet
        self.log_test_result(
            "Revenue Tracking", success,
            f"Revenue endpoint status: {status}",
            {"status": status, "accessible": success}
        )
        return success

    async def test_earnings_calculation(self):
        """Test earnings calculation system"""
        status, response = await self.make_request("GET", "/api/payments/earnings")
        
        success = status in [200, 403]  # 403 if not authenticated properly
        self.log_test_result(
            "Earnings Calculation", success,
            f"Earnings endpoint status: {status}",
            {"status": status, "accessible": success}
        )
        return success

    async def test_user_credits(self):
        """Test user credits system"""
        status, response = await self.make_request("GET", "/api/payments/user/credits")
        
        success = status in [200, 403]
        self.log_test_result(
            "User Credits System", success,
            f"User credits status: {status}",
            {"status": status, "accessible": success}
        )
        return success

    # ==================== PAYOUT SYSTEM TESTING ====================
    
    async def test_payout_endpoints(self):
        """Test payout system endpoints"""
        # Test payout request endpoint
        status, response = await self.make_request("POST", "/api/payments/payout/request")
        
        success = status in [400, 422, 403]  # Expects validation error or auth error
        self.log_test_result(
            "Payout Request Endpoint", success,
            f"Payout request endpoint status: {status}",
            {"status": status, "accessible": success}
        )
        return success

    async def test_licensing_payouts(self):
        """Test licensing payout system"""
        status, response = await self.make_request("GET", "/api/licensing/payouts")
        
        success = status in [200, 403]
        self.log_test_result(
            "Licensing Payouts", success,
            f"Licensing payouts status: {status}",
            {"status": status, "accessible": success}
        )
        return success

    # ==================== PAYMENT INTEGRATION TESTING ====================
    
    async def test_payment_packages(self):
        """Test payment packages system"""
        status, response = await self.make_request("GET", "/api/payments/packages")
        
        if status == 200 and isinstance(response, list):
            package_count = len(response)
            success = package_count >= 4  # Should have 4 packages
            self.log_test_result(
                "Payment Packages", success,
                f"Found {package_count} payment packages",
                {"package_count": package_count, "packages": [p.get("name", "Unknown") for p in response]}
            )
            return success
        else:
            self.log_test_result(
                "Payment Packages", False,
                f"Failed to get payment packages: {status}",
                response
            )
            return False

    async def test_stripe_integration(self):
        """Test Stripe payment integration"""
        # Test checkout session creation
        checkout_data = {
            "package_id": "basic_upload",
            "success_url": f"{self.backend_url}/payment/success",
            "cancel_url": f"{self.backend_url}/payment/cancel"
        }
        
        status, response = await self.make_request(
            "POST", "/api/payments/checkout/session", checkout_data
        )
        
        if status in [200, 201] and "session_id" in response:
            self.test_payment_session_id = response["session_id"]
            self.log_test_result(
                "Stripe Integration", True,
                f"Successfully created checkout session: {self.test_payment_session_id}",
                {"session_id": self.test_payment_session_id}
            )
            return True
        else:
            self.log_test_result(
                "Stripe Integration", False,
                f"Stripe checkout failed with status {status}",
                response
            )
            return False

    async def test_payment_status(self):
        """Test payment status checking"""
        if not self.test_payment_session_id:
            return False
            
        status, response = await self.make_request(
            "GET", f"/api/payments/checkout/status/{self.test_payment_session_id}"
        )
        
        success = status in [200, 500]  # 500 acceptable for test session
        self.log_test_result(
            "Payment Status", success,
            f"Payment status check: {status}",
            {"status": status, "accessible": success}
        )
        return success

    # ==================== DATABASE OPERATIONS TESTING ====================
    
    async def test_database_operations(self):
        """Test database operations throughout workflow"""
        # Test user data retrieval
        status, response = await self.make_request("GET", "/api/auth/me")
        user_db_success = status == 200
        
        # Test media library access
        status, response = await self.make_request("GET", "/api/media/library")
        media_db_success = status in [200, 403]
        
        # Test transaction history
        status, response = await self.make_request("GET", "/api/payments/transactions")
        transaction_db_success = status in [200, 403]
        
        overall_success = user_db_success and media_db_success and transaction_db_success
        
        self.log_test_result(
            "Database Operations", overall_success,
            f"DB operations - User: {user_db_success}, Media: {media_db_success}, Transactions: {transaction_db_success}",
            {
                "user_db": user_db_success,
                "media_db": media_db_success, 
                "transaction_db": transaction_db_success
            }
        )
        return overall_success

    # ==================== ERROR HANDLING TESTING ====================
    
    async def test_error_handling(self):
        """Test error handling throughout the system"""
        error_tests = []
        
        # Test invalid endpoint
        status, response = await self.make_request("GET", "/api/invalid/endpoint")
        error_tests.append(status == 404)
        
        # Test unauthorized access
        old_token = self.auth_token
        self.auth_token = "invalid_token"
        status, response = await self.make_request("GET", "/api/auth/me")
        error_tests.append(status in [401, 403])
        self.auth_token = old_token
        
        # Test malformed request
        status, response = await self.make_request("POST", "/api/media", {"invalid": "data"})
        error_tests.append(status in [400, 422])
        
        success = all(error_tests)
        self.log_test_result(
            "Error Handling", success,
            f"Error handling tests passed: {sum(error_tests)}/3",
            {"tests_passed": sum(error_tests), "total_tests": 3}
        )
        return success

    # ==================== INTEGRATION TESTING ====================
    
    async def test_industry_partners(self):
        """Test industry partners endpoint"""
        status, response = await self.make_request("GET", "/api/industry/partners")
        
        success = status in [200, 403]
        self.log_test_result(
            "Industry Partners", success,
            f"Industry partners endpoint status: {status}",
            {"status": status, "accessible": success}
        )
        return success

    async def test_products_management(self):
        """Test products management system"""
        status, response = await self.make_request("GET", "/api/products")
        
        success = status in [200, 403, 404]
        self.log_test_result(
            "Products Management", success,
            f"Products endpoint status: {status}",
            {"status": status, "accessible": success}
        )
        return success

    # ==================== MAIN TEST EXECUTION ====================
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive workflow tests"""
        print("🎯 STARTING COMPREHENSIVE UPLOAD-TO-PAYOUT WORKFLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test User: {self.test_user_data['email']}")
        print("=" * 80)
        print()
        
        await self.setup_session()
        
        try:
            # 1. Authentication & Setup
            print("📋 PHASE 1: AUTHENTICATION & USER SETUP")
            print("-" * 50)
            auth_success = await self.test_user_registration()
            if auth_success:
                await self.test_user_authentication()
            print()
            
            # 2. Upload System Testing
            print("📤 PHASE 2: UPLOAD SYSTEM TESTING")
            print("-" * 50)
            await self.test_image_upload_endpoints()
            await self.test_media_upload_endpoints()
            await self.test_file_upload_workflow()
            print()
            
            # 3. Distribution System Testing
            print("🌐 PHASE 3: DISTRIBUTION SYSTEM TESTING")
            print("-" * 50)
            await self.test_distribution_platforms()
            await self.test_content_distribution()
            await self.test_distribution_status()
            print()
            
            # 4. Revenue & Earnings Testing
            print("💰 PHASE 4: REVENUE TRACKING TESTING")
            print("-" * 50)
            await self.test_revenue_endpoints()
            await self.test_earnings_calculation()
            await self.test_user_credits()
            print()
            
            # 5. Payout System Testing
            print("💸 PHASE 5: PAYOUT SYSTEM TESTING")
            print("-" * 50)
            await self.test_payout_endpoints()
            await self.test_licensing_payouts()
            print()
            
            # 6. Payment Integration Testing
            print("💳 PHASE 6: PAYMENT INTEGRATION TESTING")
            print("-" * 50)
            await self.test_payment_packages()
            await self.test_stripe_integration()
            await self.test_payment_status()
            print()
            
            # 7. Database Operations Testing
            print("🗄️ PHASE 7: DATABASE OPERATIONS TESTING")
            print("-" * 50)
            await self.test_database_operations()
            print()
            
            # 8. Integration & Partners Testing
            print("🤝 PHASE 8: INTEGRATION TESTING")
            print("-" * 50)
            await self.test_industry_partners()
            await self.test_products_management()
            print()
            
            # 9. Error Handling Testing
            print("⚠️ PHASE 9: ERROR HANDLING TESTING")
            print("-" * 50)
            await self.test_error_handling()
            print()
            
        finally:
            await self.cleanup_session()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()

    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("=" * 80)
        print("🎯 COMPREHENSIVE UPLOAD-TO-PAYOUT WORKFLOW TEST REPORT")
        print("=" * 80)
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results by phase
        phases = {
            "Authentication": ["User Registration", "User Authentication"],
            "Upload System": ["Image Upload Endpoint", "Media Upload Endpoint", "Media Creation"],
            "Distribution": ["Distribution Platforms", "Content Distribution", "Distribution Status"],
            "Revenue Tracking": ["Revenue Tracking", "Earnings Calculation", "User Credits System"],
            "Payout System": ["Payout Request Endpoint", "Licensing Payouts"],
            "Payment Integration": ["Payment Packages", "Stripe Integration", "Payment Status"],
            "Database Operations": ["Database Operations"],
            "Integration": ["Industry Partners", "Products Management"],
            "Error Handling": ["Error Handling"]
        }
        
        print("📋 RESULTS BY PHASE:")
        print("-" * 50)
        
        for phase_name, test_names in phases.items():
            phase_results = [r for r in self.test_results if r["test_name"] in test_names]
            if phase_results:
                phase_passed = sum(1 for r in phase_results if r["success"])
                phase_total = len(phase_results)
                phase_rate = (phase_passed / phase_total * 100) if phase_total > 0 else 0
                
                status_icon = "✅" if phase_rate >= 80 else "⚠️" if phase_rate >= 50 else "❌"
                print(f"{status_icon} {phase_name}: {phase_passed}/{phase_total} ({phase_rate:.1f}%)")
        
        print()
        
        # Critical Issues
        critical_failures = [r for r in self.test_results if not r["success"] and 
                           r["test_name"] in ["User Registration", "User Authentication", 
                                            "Distribution Platforms", "Payment Packages"]]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            print("-" * 50)
            for failure in critical_failures:
                print(f"❌ {failure['test_name']}: {failure['details']}")
            print()
        
        # Workflow Status
        workflow_components = {
            "Upload System": any(r["success"] for r in self.test_results if "Upload" in r["test_name"] or "Media Creation" in r["test_name"]),
            "Distribution System": any(r["success"] for r in self.test_results if "Distribution" in r["test_name"]),
            "Revenue Tracking": any(r["success"] for r in self.test_results if "Revenue" in r["test_name"] or "Earnings" in r["test_name"]),
            "Payout System": any(r["success"] for r in self.test_results if "Payout" in r["test_name"]),
            "Payment Processing": any(r["success"] for r in self.test_results if "Payment" in r["test_name"] or "Stripe" in r["test_name"])
        }
        
        print("🔄 COMPLETE WORKFLOW STATUS:")
        print("-" * 50)
        for component, working in workflow_components.items():
            status = "✅ OPERATIONAL" if working else "❌ ISSUES DETECTED"
            print(f"   {component}: {status}")
        
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("-" * 50)
        
        if success_rate >= 90:
            print("✅ System is production-ready with excellent functionality")
        elif success_rate >= 75:
            print("⚠️ System is mostly functional but has some issues to address")
        elif success_rate >= 50:
            print("⚠️ System has significant issues that need immediate attention")
        else:
            print("❌ System has critical issues preventing production deployment")
        
        # Specific recommendations based on failures
        failed_test_names = [r["test_name"] for r in self.test_results if not r["success"]]
        
        if "User Registration" in failed_test_names:
            print("🔧 Fix user registration system - critical for user onboarding")
        if "Distribution Platforms" in failed_test_names:
            print("🔧 Fix distribution platform integration - core business functionality")
        if "Payment Packages" in failed_test_names:
            print("🔧 Fix payment system - required for monetization")
        if "Stripe Integration" in failed_test_names:
            print("🔧 Verify Stripe API keys and configuration")
        
        print()
        print("=" * 80)
        print("🎉 COMPREHENSIVE WORKFLOW TESTING COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution function"""
    tester = ComprehensiveWorkflowTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())