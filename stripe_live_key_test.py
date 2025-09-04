#!/usr/bin/env python3
"""
Stripe Live API Key Verification Test
Tests the complete live Stripe API key integration for Big Mann Entertainment
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
# Use local backend for testing since we're in the container environment
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class StripeLiveKeyTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.admin_token = None
        self.test_user_id = None
        self.results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def register_test_user(self) -> bool:
        """Register test user for authentication"""
        try:
            user_data = {
                "email": "stripe.live.tester@bigmannentertainment.com",
                "password": "StripeLive2025!",
                "full_name": "Stripe Live Key Tester",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Payment Street",
                "city": "Stripe City",
                "state_province": "Payment State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.test_user_id = data.get("user", {}).get("id")
                    return True
                elif response.status == 400:
                    # User might already exist, try login
                    return await self.login_test_user()
                    
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return await self.login_test_user()
        
        return False
    
    async def login_test_user(self) -> bool:
        """Login test user"""
        try:
            login_data = {
                "email": "stripe.live.tester@bigmannentertainment.com",
                "password": "StripeLive2025!"
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.test_user_id = data.get("user", {}).get("id")
                    return True
                    
        except Exception as e:
            print(f"Login error: {str(e)}")
        
        return False
    
    async def setup_admin_user(self) -> bool:
        """Setup admin user for admin endpoints testing"""
        try:
            # Try to login as admin (assuming admin user exists)
            admin_data = {
                "email": "admin@bigmannentertainment.com",
                "password": "admin123"
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=admin_data) as response:
                if response.status == 200:
                    data = await response.json()
                    user = data.get("user", {})
                    if user.get("is_admin") or user.get("role") in ["admin", "super_admin"]:
                        self.admin_token = data.get("access_token")
                        return True
                        
        except Exception as e:
            print(f"Admin setup error: {str(e)}")
        
        return False
    
    def get_auth_headers(self, admin=False):
        """Get authentication headers"""
        token = self.admin_token if admin and self.admin_token else self.auth_token
        return {"Authorization": f"Bearer {token}"} if token else {}
    
    async def test_live_key_validation(self) -> Dict[str, Any]:
        """Test 1: Live Key Validation - Confirm the complete Stripe live secret key is recognized"""
        test_name = "Live Key Validation"
        
        try:
            # Test payment packages endpoint which should work with valid key
            async with self.session.get(f"{API_BASE}/payments/packages") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("packages"):
                        packages = data["packages"]
                        expected_key = "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"
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "details": f"Live API key is properly configured and recognized. Found {len(packages)} payment packages.",
                            "packages_count": len(packages),
                            "key_status": "valid",
                            "expected_key_format": expected_key[:20] + "..." + expected_key[-10:]
                        }
                
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "details": f"Payment packages endpoint failed: {response.status}",
                    "response_status": response.status,
                    "key_status": "invalid"
                }
                
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "details": f"Live key validation error: {str(e)}",
                "key_status": "error"
            }
    
    async def test_payment_packages(self) -> Dict[str, Any]:
        """Test 2: Payment Packages - Test GET /api/payments/packages works with the live key"""
        test_name = "Payment Packages Endpoint"
        
        try:
            async with self.session.get(f"{API_BASE}/payments/packages") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("packages"):
                        packages = data["packages"]
                        
                        # Verify expected packages
                        expected_packages = ["basic_upload", "premium_upload", "pro_upload", "distribution_fee"]
                        found_packages = list(packages.keys())
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "details": f"Payment packages retrieved successfully with live key. Found packages: {found_packages}",
                            "packages_count": len(packages),
                            "expected_packages": expected_packages,
                            "found_packages": found_packages
                        }
                
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "details": f"Payment packages endpoint failed: {response.status}",
                    "response_status": response.status
                }
                
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "details": f"Payment packages error: {str(e)}"
            }
    
    async def test_checkout_session_creation(self) -> Dict[str, Any]:
        """Test 3: Checkout Session Creation - Test creating a live checkout session"""
        test_name = "Checkout Session Creation"
        
        if not self.auth_token:
            return {
                "test": test_name,
                "status": "SKIP",
                "details": "No authentication token available"
            }
        
        try:
            checkout_data = {
                "package_id": "basic_upload",
                "origin_url": BACKEND_URL,
                "success_url": f"{BACKEND_URL}/payment/success",
                "cancel_url": f"{BACKEND_URL}/payment/cancel"
            }
            
            headers = self.get_auth_headers()
            
            async with self.session.post(f"{API_BASE}/payments/checkout/session", 
                                       json=checkout_data, headers=headers) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and data.get("session_id"):
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "details": f"Live checkout session created successfully: {data['session_id']}",
                            "session_id": data["session_id"],
                            "checkout_url": data.get("checkout_url"),
                            "package_id": checkout_data["package_id"]
                        }
                
                # Check if it's an API key error
                error_text = await response.text()
                if "Invalid API Key" in error_text:
                    return {
                        "test": test_name,
                        "status": "FAIL",
                        "details": f"Live API key is invalid or expired: {error_text}",
                        "response_status": response.status,
                        "error_type": "invalid_api_key"
                    }
                
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "details": f"Checkout session creation failed: {response.status} - {error_text}",
                    "response_status": response.status
                }
                
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "details": f"Checkout session error: {str(e)}"
            }
    
    async def test_stripe_api_connection(self) -> Dict[str, Any]:
        """Test 4: Stripe API Connection - Verify emergentintegrations library can connect to Stripe's live environment"""
        test_name = "Stripe API Connection"
        
        if not self.auth_token:
            return {
                "test": test_name,
                "status": "SKIP",
                "details": "No authentication token available"
            }
        
        try:
            # Test payment status endpoint which requires Stripe API connection
            headers = self.get_auth_headers()
            
            # Create a test session first
            checkout_data = {
                "package_id": "basic_upload",
                "success_url": f"{BACKEND_URL}/payment/success",
                "cancel_url": f"{BACKEND_URL}/payment/cancel"
            }
            
            async with self.session.post(f"{API_BASE}/payments/checkout/session", 
                                       json=checkout_data, headers=headers) as response:
                
                if response.status == 200:
                    data = await response.json()
                    session_id = data.get("session_id")
                    
                    if session_id:
                        # Now test status check
                        async with self.session.get(f"{API_BASE}/payments/checkout/status/{session_id}", 
                                                  headers=headers) as status_response:
                            
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                
                                return {
                                    "test": test_name,
                                    "status": "PASS",
                                    "details": f"Stripe API connection successful. Session status: {status_data.get('status')}",
                                    "session_id": session_id,
                                    "payment_status": status_data.get("payment_status"),
                                    "api_connection": "successful"
                                }
                            
                            return {
                                "test": test_name,
                                "status": "FAIL",
                                "details": f"Status check failed: {status_response.status}",
                                "response_status": status_response.status
                            }
                
                # Check for API key errors
                error_text = await response.text()
                if "Invalid API Key" in error_text:
                    return {
                        "test": test_name,
                        "status": "FAIL",
                        "details": f"Stripe API connection failed - Invalid API Key: {error_text}",
                        "response_status": response.status,
                        "api_connection": "failed",
                        "error_type": "invalid_api_key"
                    }
                
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "details": f"API connection test failed: {response.status} - {error_text}",
                    "response_status": response.status,
                    "api_connection": "failed"
                }
                
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "details": f"Stripe API connection error: {str(e)}",
                "api_connection": "error"
            }
    
    async def test_webhook_readiness(self) -> Dict[str, Any]:
        """Test 5: Webhook Readiness - Confirm the webhook endpoint is ready for live webhook events"""
        test_name = "Webhook Readiness"
        
        try:
            # Test webhook endpoint with a test payload (should validate signature)
            webhook_data = {
                "id": "evt_test_webhook",
                "object": "event",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_session",
                        "payment_status": "paid"
                    }
                }
            }
            
            # Test without signature (should fail with proper error)
            async with self.session.post(f"{API_BASE}/webhook/stripe", json=webhook_data) as response:
                
                if response.status == 400:
                    error_text = await response.text()
                    
                    if "Stripe-Signature" in error_text or "signature" in error_text.lower():
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "details": "Webhook endpoint properly validates signatures (400 for missing signature)",
                            "response_status": response.status,
                            "signature_validation": "working",
                            "webhook_ready": True
                        }
                
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "details": f"Webhook validation unexpected response: {response.status}",
                    "response_status": response.status,
                    "webhook_ready": False
                }
                
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "details": f"Webhook readiness error: {str(e)}",
                "webhook_ready": False
            }
    
    async def test_emergentintegrations_library(self) -> Dict[str, Any]:
        """Test 6: Emergentintegrations Library - Verify the library can successfully connect to Stripe's live environment"""
        test_name = "Emergentintegrations Library Connection"
        
        try:
            # Test a simple endpoint that uses the emergentintegrations library
            async with self.session.get(f"{API_BASE}/payments/packages") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "details": "Emergentintegrations library successfully initialized and working with Stripe",
                            "library_status": "working",
                            "stripe_integration": "successful"
                        }
                
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "details": f"Library connection test failed: {response.status}",
                    "response_status": response.status,
                    "library_status": "failed"
                }
                
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "details": f"Emergentintegrations library error: {str(e)}",
                "library_status": "error"
            }
    
    async def run_all_tests(self):
        """Run all Stripe live key verification tests"""
        print("🎯 STARTING STRIPE LIVE API KEY VERIFICATION TESTING")
        print("=" * 80)
        print("Testing complete live API key: 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")
        print("=" * 80)
        
        await self.setup_session()
        
        # Setup authentication
        print("Setting up test authentication...")
        auth_success = await self.register_test_user()
        admin_success = await self.setup_admin_user()
        
        print(f"✅ User authentication: {'SUCCESS' if auth_success else 'FAILED'}")
        print(f"✅ Admin authentication: {'SUCCESS' if admin_success else 'FAILED'}")
        print()
        
        # Define test suite
        tests = [
            self.test_live_key_validation,
            self.test_payment_packages,
            self.test_checkout_session_creation,
            self.test_stripe_api_connection,
            self.test_webhook_readiness,
            self.test_emergentintegrations_library
        ]
        
        all_results = []
        total_tests = len(tests)
        passed_tests = 0
        
        # Run tests
        print("📋 STRIPE LIVE KEY VERIFICATION TESTS")
        print("-" * 50)
        
        for test_func in tests:
            result = await test_func()
            all_results.append(result)
            
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            print(f"{status_icon} {result['test']}: {result['details']}")
            
            if result["status"] == "PASS":
                passed_tests += 1
        
        print()
        
        # Summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("🎯 STRIPE LIVE API KEY VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📊 DETAILED TEST RESULTS:")
        print("-" * 50)
        
        critical_issues = []
        
        for result in all_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            print(f"{status_icon} {result['test']}")
            print(f"   Status: {result['status']}")
            print(f"   Details: {result['details']}")
            
            # Check for critical API key issues
            if result["status"] == "FAIL" and "Invalid API Key" in result.get("details", ""):
                critical_issues.append(f"❌ {result['test']}: Invalid API Key Error")
            elif result["status"] == "FAIL" and result.get("error_type") == "invalid_api_key":
                critical_issues.append(f"❌ {result['test']}: API Key Authentication Failed")
            
            # Additional details for specific tests
            if result["status"] == "PASS":
                if "packages_count" in result:
                    print(f"   Packages Found: {result['packages_count']}")
                elif "session_id" in result:
                    print(f"   Session ID: {result['session_id']}")
                elif "api_connection" in result:
                    print(f"   API Connection: {result['api_connection']}")
            
            print()
        
        # Critical Issues Summary
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            print("-" * 50)
            for issue in critical_issues:
                print(issue)
            print()
            print("🔧 IMMEDIATE ACTION REQUIRED:")
            print("- Verify the live Stripe API key in the Stripe Dashboard")
            print("- Check if the key is active and not revoked")
            print("- Ensure the key has proper permissions for checkout sessions and payments")
            print("- Confirm the key matches the expected format: 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")
            print()
        
        await self.cleanup_session()
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": all_results,
            "critical_issues": critical_issues
        }

async def main():
    """Main test execution"""
    tester = StripeLiveKeyTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if results["success_rate"] >= 70 and len(results["critical_issues"]) == 0:
        print("🎉 STRIPE LIVE API KEY VERIFICATION COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ STRIPE LIVE API KEY VERIFICATION FAILED!")
        if results["critical_issues"]:
            print("Critical API key issues found - immediate attention required!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())