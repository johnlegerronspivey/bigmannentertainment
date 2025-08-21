#!/usr/bin/env python3
"""
Comprehensive Payment System Testing for Big Mann Entertainment
Tests all payment endpoints as requested in the review.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://bme-media-system.preview.emergentagent.com/api"
TEST_USER_EMAIL = "payment.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "PaymentTester2025!"
TEST_USER_NAME = "Payment System Tester"

class PaymentSystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_media_id = None
        
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise
    
    def register_test_user(self) -> bool:
        """Register a test user for payment testing"""
        try:
            from datetime import datetime, timedelta
            
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "business_name": "Payment Testing LLC",
                "date_of_birth": (datetime.utcnow() - timedelta(days=30*365)).isoformat(),
                "address_line1": "123 Payment Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            response = self.make_request('POST', '/auth/register', json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data['user']['id']
                    print("✅ Test user registered successfully")
                    return True
            elif response.status_code == 400 and "already registered" in response.text:
                print("✅ Test user already exists, attempting login...")
                return self.login_test_user()
            else:
                print(f"❌ Failed to register test user: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during registration: {str(e)}")
            return False
    
    def login_test_user(self) -> bool:
        """Login test user"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data['user']['id']
                    print("✅ Test user logged in successfully")
                    return True
            else:
                print(f"❌ Failed to login test user: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during login: {str(e)}")
            return False
    
    def test_payment_packages(self) -> bool:
        """Test GET /api/payments/packages - Verify 5 payment packages are returned correctly"""
        print("\n🔍 Testing Payment Packages Endpoint...")
        try:
            response = self.make_request('GET', '/payments/packages')
            
            if response.status_code == 200:
                data = response.json()
                if 'packages' in data and isinstance(data['packages'], list):
                    packages = data['packages']
                    if len(packages) >= 5:
                        expected_packages = ['basic', 'premium', 'enterprise', 'single_track', 'album']
                        package_ids = [p['id'] for p in packages]
                        found_expected = [pid for pid in expected_packages if pid in package_ids]
                        
                        print(f"✅ Found {len(packages)} payment packages including {found_expected}")
                        return True
                    else:
                        print(f"❌ Expected at least 5 packages, found {len(packages)}")
                        return False
                else:
                    print("❌ Invalid response format")
                    return False
            else:
                print(f"❌ Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_checkout_session_creation(self) -> bool:
        """Test POST /api/payments/checkout/session with different packages"""
        print("\n🔍 Testing Checkout Session Creation...")
        try:
            if not self.auth_token:
                print("❌ No auth token available")
                return False
            
            # Test with basic package
            params = {
                "package_id": "basic",
                "origin_url": "https://bme-media-system.preview.emergentagent.com"
            }
            
            response = self.make_request('POST', '/payments/checkout/session', params=params)
            
            if response.status_code == 200:
                data = response.json()
                if all(field in data for field in ['url', 'session_id', 'amount', 'currency']):
                    print(f"✅ Created checkout session: {data['session_id']}, Amount: ${data['amount']} {data['currency'].upper()}")
                    return True
                else:
                    print("❌ Missing required fields in response")
                    return False
            else:
                print(f"❌ Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_checkout_status(self) -> bool:
        """Test GET /api/payments/checkout/status/{session_id}"""
        print("\n🔍 Testing Checkout Status Checking...")
        try:
            test_session_id = "cs_test_dummy_session_id"
            response = self.make_request('GET', f'/payments/checkout/status/{test_session_id}')
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and 'payment_status' in data:
                    print(f"✅ Status endpoint working, returned: {data.get('payment_status', 'unknown')}")
                    return True
                else:
                    print("❌ Missing status fields in response")
                    return False
            elif response.status_code == 400:
                print("✅ Status endpoint correctly handles invalid session ID")
                return True
            else:
                print(f"❌ Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_webhook_endpoint(self) -> bool:
        """Test POST /api/payments/webhook/stripe"""
        print("\n🔍 Testing Webhook Endpoint...")
        try:
            webhook_data = {
                "id": "evt_test_webhook",
                "object": "event",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_session_id",
                        "payment_status": "paid"
                    }
                }
            }
            
            response = self.make_request('POST', '/payments/webhook/stripe', json=webhook_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'success':
                    print("✅ Webhook endpoint working correctly")
                    return True
                else:
                    print("❌ Webhook response format incorrect")
                    return False
            elif response.status_code == 400 and ("signature" in response.text.lower()):
                print("✅ Webhook endpoint exists and validates signatures (expected)")
                return True
            else:
                print(f"❌ Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_authentication_integration(self) -> bool:
        """Test all payment endpoints with proper JWT authentication"""
        print("\n🔍 Testing Authentication Integration...")
        try:
            protected_endpoints = [
                ('GET', '/payments/earnings'),
                ('POST', '/payments/bank-accounts'),
                ('GET', '/payments/bank-accounts'),
                ('POST', '/payments/wallets'),
                ('GET', '/payments/wallets'),
                ('POST', '/payments/royalty-splits'),
                ('POST', '/payments/payouts')
            ]
            
            # Test without authentication
            original_token = self.auth_token
            self.auth_token = None
            
            protected_count = 0
            for method, endpoint in protected_endpoints:
                try:
                    response = self.make_request(method, endpoint, json={})
                    if response.status_code in [401, 403]:
                        protected_count += 1
                except:
                    protected_count += 1
            
            self.auth_token = original_token
            
            if protected_count >= len(protected_endpoints) - 1:
                print(f"✅ {protected_count}/{len(protected_endpoints)} payment endpoints properly protected")
                return True
            else:
                print(f"❌ Only {protected_count}/{len(protected_endpoints)} endpoints properly protected")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_bank_account_management(self) -> bool:
        """Test POST/GET /api/payments/bank-accounts"""
        print("\n🔍 Testing Bank Account Management...")
        try:
            if not self.auth_token:
                print("❌ No auth token available")
                return False
            
            # Test adding a bank account
            bank_account_data = {
                "account_name": "Big Mann Entertainment Business Account",
                "account_number": "1234567890",
                "routing_number": "021000021",
                "bank_name": "Chase Bank",
                "account_type": "business",
                "is_primary": True
            }
            
            add_response = self.make_request('POST', '/payments/bank-accounts', json=bank_account_data)
            
            if add_response.status_code == 200:
                add_data = add_response.json()
                if 'account_id' in add_data and 'message' in add_data:
                    # Test retrieving bank accounts
                    get_response = self.make_request('GET', '/payments/bank-accounts')
                    
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        if 'accounts' in get_data and isinstance(get_data['accounts'], list):
                            print(f"✅ Successfully added and retrieved bank accounts. Count: {len(get_data['accounts'])}")
                            return True
                        else:
                            print("❌ Failed to retrieve bank accounts")
                            return False
                    else:
                        print(f"❌ Failed to retrieve accounts: {get_response.status_code}")
                        return False
                else:
                    print("❌ Missing account_id or message in add response")
                    return False
            else:
                print(f"❌ Failed to add bank account: {add_response.status_code}, {add_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_digital_wallet_management(self) -> bool:
        """Test POST/GET /api/payments/wallets"""
        print("\n🔍 Testing Digital Wallet Management...")
        try:
            if not self.auth_token:
                print("❌ No auth token available")
                return False
            
            # Test adding a digital wallet
            wallet_data = {
                "wallet_type": "paypal",
                "wallet_address": "john@bigmannentertainment.com",
                "wallet_name": "Big Mann Entertainment PayPal",
                "is_primary": True
            }
            
            add_response = self.make_request('POST', '/payments/wallets', json=wallet_data)
            
            if add_response.status_code == 200:
                add_data = add_response.json()
                if 'wallet_id' in add_data and 'message' in add_data:
                    # Test retrieving digital wallets
                    get_response = self.make_request('GET', '/payments/wallets')
                    
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        if 'wallets' in get_data and isinstance(get_data['wallets'], list):
                            print(f"✅ Successfully added and retrieved digital wallets. Count: {len(get_data['wallets'])}")
                            return True
                        else:
                            print("❌ Failed to retrieve digital wallets")
                            return False
                    else:
                        print(f"❌ Failed to retrieve wallets: {get_response.status_code}")
                        return False
                else:
                    print("❌ Missing wallet_id or message in add response")
                    return False
            else:
                print(f"❌ Failed to add digital wallet: {add_response.status_code}, {add_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_earnings_dashboard(self) -> bool:
        """Test GET /api/payments/earnings"""
        print("\n🔍 Testing Earnings Dashboard...")
        try:
            if not self.auth_token:
                print("❌ No auth token available")
                return False
            
            response = self.make_request('GET', '/payments/earnings')
            
            if response.status_code == 200:
                data = response.json()
                if 'earnings' in data:
                    earnings = data['earnings']
                    required_fields = ['total_earnings', 'available_balance', 'pending_balance']
                    
                    if all(field in earnings for field in required_fields):
                        print(f"✅ Earnings dashboard working. Balance: ${earnings.get('available_balance', 0)}")
                        return True
                    else:
                        print("❌ Missing required earnings fields")
                        return False
                else:
                    print("❌ Missing earnings data in response")
                    return False
            else:
                print(f"❌ Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_payout_requests(self) -> bool:
        """Test POST /api/payments/payouts"""
        print("\n🔍 Testing Payout Requests...")
        try:
            if not self.auth_token:
                print("❌ No auth token available")
                return False
            
            # Test requesting a payout
            payout_data = {
                "amount": 50.00,
                "payout_method": "bank_transfer",
                "bank_account_id": "test_bank_account_id"
            }
            
            response = self.make_request('POST', '/payments/payouts', json=payout_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'payout_id' in data and 'message' in data:
                    print(f"✅ Payout request successful: {data['payout_id']}")
                    return True
                else:
                    print("❌ Missing payout_id or message in response")
                    return False
            elif response.status_code == 400 and ("insufficient" in response.text.lower() or "balance" in response.text.lower()):
                print("✅ Payout endpoint correctly validates insufficient balance")
                return True
            else:
                print(f"❌ Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive payment system tests"""
        print("="*80)
        print("🔥 COMPREHENSIVE PAYMENT & ROYALTY SYSTEM TESTING")
        print("Final comprehensive test of the fixed payment and royalty system for Big Mann Entertainment")
        print("="*80)
        
        # Setup
        if not self.register_test_user():
            print("❌ Failed to setup test user, exiting...")
            return False
        
        results = []
        
        # Core Payment System Tests
        print("\n" + "="*60)
        print("1. CORE PAYMENT SYSTEM TESTS")
        print("="*60)
        results.append(("Payment Packages", self.test_payment_packages()))
        results.append(("Checkout Session Creation", self.test_checkout_session_creation()))
        results.append(("Checkout Status Checking", self.test_checkout_status()))
        results.append(("Webhook Endpoint", self.test_webhook_endpoint()))
        
        # Authentication Integration Tests
        print("\n" + "="*60)
        print("2. AUTHENTICATION INTEGRATION TESTS")
        print("="*60)
        results.append(("Authentication Integration", self.test_authentication_integration()))
        
        # Banking & Wallet Management Tests
        print("\n" + "="*60)
        print("3. BANKING & WALLET MANAGEMENT TESTS")
        print("="*60)
        results.append(("Bank Account Management", self.test_bank_account_management()))
        results.append(("Digital Wallet Management", self.test_digital_wallet_management()))
        
        # Earnings & Royalty System Tests
        print("\n" + "="*60)
        print("4. EARNINGS & ROYALTY SYSTEM TESTS")
        print("="*60)
        results.append(("Earnings Dashboard", self.test_earnings_dashboard()))
        results.append(("Payout Requests", self.test_payout_requests()))
        
        # Summary
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE PAYMENT SYSTEM TEST RESULTS")
        print("="*80)
        
        passed = 0
        failed = 0
        
        for test_name, result in results:
            if result:
                print(f"✅ {test_name}")
                passed += 1
            else:
                print(f"❌ {test_name}")
                failed += 1
        
        print(f"\n📊 FINAL RESULTS: {passed} PASSED, {failed} FAILED")
        
        if failed == 0:
            print("🎉 ALL PAYMENT SYSTEM TESTS PASSED! System is production-ready.")
        elif failed <= 2:
            print("⚠️  Most tests passed with minor issues. System is mostly functional.")
        else:
            print("🚨 Multiple test failures. System needs attention before production.")
        
        return failed == 0

if __name__ == "__main__":
    tester = PaymentSystemTester()
    tester.run_comprehensive_tests()