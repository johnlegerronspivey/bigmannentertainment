#!/usr/bin/env python3
"""
Test ULN Authentication
=======================
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://social-profile-sync.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_uln_auth():
    async with aiohttp.ClientSession() as session:
        # Register user
        registration_data = {
            "email": f"ulnauth_{int(datetime.now().timestamp())}@test.com",
            "password": "TestPass123!",
            "full_name": "ULN Auth Test",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Test St",
            "city": "Test City",
            "state_province": "Test State",
            "postal_code": "12345",
            "country": "US"
        }
        
        print("🔐 Registering user...")
        async with session.post(f"{API_BASE}/auth/register", json=registration_data) as response:
            print(f"Registration status: {response.status}")
            if response.status not in [200, 201, 400]:
                text = await response.text()
                print(f"Registration response: {text}")
        
        # Login
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        print("🔑 Logging in...")
        async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            print(f"Login status: {response.status}")
            if response.status == 200:
                data = await response.json()
                token = data.get("access_token")
                print(f"Got token: {token[:20]}..." if token else "No token received")
                
                if token:
                    # Test ULN endpoints with token
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    print("\n📁 Testing Label Directory...")
                    async with session.get(f"{API_BASE}/uln/labels/directory", headers=headers) as response:
                        print(f"Label Directory status: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            print(f"Success: {data.get('success')}")
                            if data.get('success'):
                                labels = data.get('labels', [])
                                print(f"Found {len(labels)} labels")
                        else:
                            text = await response.text()
                            print(f"Error response: {text}")
                    
                    print("\n📊 Testing Dashboard Stats...")
                    async with session.get(f"{API_BASE}/uln/dashboard/stats", headers=headers) as response:
                        print(f"Dashboard Stats status: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            print(f"Success: {data.get('success')}")
                            if data.get('success'):
                                stats = data.get('dashboard_stats', {})
                                print(f"Total labels: {stats.get('total_labels', 0)}")
                        else:
                            text = await response.text()
                            print(f"Error response: {text}")
            else:
                text = await response.text()
                print(f"Login failed: {text}")

if __name__ == "__main__":
    asyncio.run(test_uln_auth())