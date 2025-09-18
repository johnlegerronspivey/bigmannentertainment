#!/usr/bin/env python3
"""
Focused Authentication Test - Reproducing 401 Errors
Specifically testing the exact scenario from the review request
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Use the correct backend URL
BACKEND_URL = "https://content-workflow-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

async def test_exact_scenario():
    """Test the exact authentication scenario from the review"""
    
    print("🔐 FOCUSED AUTHENTICATION TEST")
    print("Testing exact scenario from review request")
    print("="*60)
    
    # Test data from review request
    test_data = {
        "email": "test.user@bigmannentertainment.com", 
        "password": "TestPassword2025!",
        "full_name": "Test User",
        "business_name": "Test Business",
        "date_of_birth": "1990-01-01T00:00:00Z",
        "address_line1": "123 Test St",
        "city": "Test City", 
        "state_province": "Test State",
        "postal_code": "12345",
        "country": "US"
    }
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Registration
        print("\n1️⃣ Testing Registration...")
        try:
            async with session.post(f"{API_BASE}/auth/register", json=test_data) as response:
                response_text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {response_text[:200]}...")
                
                if response.status == 201:
                    print("   ✅ Registration successful")
                elif response.status == 400:
                    print("   ✅ User already exists (expected)")
                else:
                    print(f"   ❌ Unexpected registration status: {response.status}")
        except Exception as e:
            print(f"   ❌ Registration error: {str(e)}")
        
        # Test 2: Login - The critical test
        print("\n2️⃣ Testing Login (CRITICAL)...")
        login_data = {
            "email": test_data["email"],
            "password": test_data["password"]
        }
        
        try:
            async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                response_text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {response_text}")
                
                if response.status == 200:
                    try:
                        response_data = json.loads(response_text)
                        if "access_token" in response_data:
                            print("   ✅ Login successful with token")
                            token = response_data["access_token"]
                            
                            # Test 3: Protected route access
                            print("\n3️⃣ Testing Protected Route Access...")
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            async with session.get(f"{API_BASE}/content-ingestion/dashboard", headers=headers) as protected_response:
                                protected_text = await protected_response.text()
                                print(f"   Status: {protected_response.status}")
                                print(f"   Response: {protected_text[:200]}...")
                                
                                if protected_response.status == 200:
                                    print("   ✅ Content Ingestion route accessible")
                                elif protected_response.status == 401:
                                    print("   ❌ 401 ERROR: Content Ingestion blocked by authentication")
                                else:
                                    print(f"   ⚠️ Unexpected status: {protected_response.status}")
                        else:
                            print("   ❌ Login response missing access_token")
                    except json.JSONDecodeError:
                        print("   ❌ Invalid JSON response from login")
                elif response.status == 401:
                    print("   ❌ 401 UNAUTHORIZED - This is the reported issue!")
                    print("   🚨 LOGIN FAILING WITH 401 ERROR")
                else:
                    print(f"   ❌ Unexpected login status: {response.status}")
        except Exception as e:
            print(f"   ❌ Login error: {str(e)}")
        
        # Test 4: Multiple login attempts to see if it's consistent
        print("\n4️⃣ Testing Multiple Login Attempts...")
        for i in range(3):
            try:
                async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                    print(f"   Attempt {i+1}: Status {response.status}")
                    if response.status == 401:
                        response_text = await response.text()
                        print(f"   401 Error: {response_text}")
            except Exception as e:
                print(f"   Attempt {i+1} error: {str(e)}")
        
        # Test 5: Check if user exists in database
        print("\n5️⃣ Testing User Existence...")
        try:
            # Try to register the same user again to see if it exists
            async with session.post(f"{API_BASE}/auth/register", json=test_data) as response:
                response_text = await response.text()
                if response.status == 400 and "already" in response_text.lower():
                    print("   ✅ User exists in database")
                elif response.status == 201:
                    print("   ⚠️ User was created (didn't exist before)")
                else:
                    print(f"   ❌ Unexpected response: {response.status} - {response_text}")
        except Exception as e:
            print(f"   ❌ User existence check error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_exact_scenario())