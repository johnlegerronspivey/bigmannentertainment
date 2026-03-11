#!/usr/bin/env python3
"""
Debug Label Directory
====================

Debug the ULN Label Directory endpoint to understand why it's returning 404
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://social-profile-sync.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def debug_label_directory():
    """Debug the label directory endpoint"""
    print("🔍 DEBUGGING ULN LABEL DIRECTORY")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Authentication setup
        test_email = f"ulndebug_{int(datetime.now().timestamp())}@test.com"
        test_password = "ULNDebug2025!"
        
        print(f"🔐 Setting up authentication...")
        
        # Register and login
        registration_data = {
            "email": test_email,
            "password": test_password,
            "full_name": "ULN Debug User",
            "date_of_birth": "1990-01-01T00:00:00Z",
            "address_line1": "123 Debug Street",
            "city": "Debug City",
            "state_province": "Debug State",
            "postal_code": "12345",
            "country": "US"
        }
        
        async with session.post(f"{API_BASE}/auth/register", json=registration_data) as response:
            if response.status not in [200, 201]:
                print(f"❌ Registration failed: {response.status}")
                return
        
        login_data = {"email": test_email, "password": test_password}
        async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                return
            
            login_response = await response.json()
            access_token = login_response.get("access_token")
            
            if not access_token:
                print(f"❌ No access token received")
                return
            
            print(f"✅ Authentication successful")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test the label directory endpoint with detailed debugging
        print(f"\n📁 Testing Label Directory endpoint...")
        
        try:
            async with session.get(f"{API_BASE}/uln/labels/directory", headers=headers) as response:
                print(f"   Status Code: {response.status}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success Response:")
                    print(f"      Success: {data.get('success')}")
                    print(f"      Labels: {len(data.get('labels', []))}")
                    print(f"      Total Labels: {data.get('total_labels', 0)}")
                    
                    if data.get('labels'):
                        print(f"   📋 Sample Labels:")
                        for i, label in enumerate(data['labels'][:3]):
                            name = label.get('metadata_profile', {}).get('name', 'Unknown')
                            label_type = label.get('label_type', 'unknown')
                            global_id = label.get('global_id', {}).get('id', 'unknown')
                            print(f"      {i+1}. {name} ({label_type}) - {global_id}")
                else:
                    text = await response.text()
                    print(f"   ❌ Error Response: {text}")
                    
                    # Try to parse as JSON for more details
                    try:
                        error_data = json.loads(text)
                        print(f"   Error Details: {error_data}")
                    except:
                        pass
        
        except Exception as e:
            print(f"   🔥 Exception: {str(e)}")
        
        # Also test individual label retrieval
        print(f"\n🏷️ Testing individual label retrieval...")
        
        # Try to get a specific label (Atlantic Records from our populated data)
        test_label_ids = [
            "BM-LBL-9D0377FB",  # Atlantic Records from our population
            "BM-LBL-583C329B",  # Columbia Records
            "BM-LBL-463D5920"   # Warner Records
        ]
        
        for label_id in test_label_ids:
            try:
                async with session.get(f"{API_BASE}/uln/labels/{label_id}", headers=headers) as response:
                    print(f"   Label {label_id}: Status {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            label = data.get('label', {})
                            name = label.get('metadata_profile', {}).get('name', 'Unknown')
                            print(f"      ✅ Found: {name}")
                            break
                        else:
                            print(f"      ❌ API returned success=false")
                    else:
                        text = await response.text()
                        print(f"      ❌ Error: {text}")
            except Exception as e:
                print(f"      🔥 Exception: {str(e)}")
        
        # Test the health endpoint to compare
        print(f"\n🏥 Testing Health endpoint for comparison...")
        
        try:
            async with session.get(f"{API_BASE}/uln/health") as response:
                print(f"   Status Code: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health Response:")
                    print(f"      Status: {data.get('status')}")
                    print(f"      Total Labels: {data.get('metrics', {}).get('total_labels', 0)}")
                    print(f"      Database: {data.get('database')}")
                else:
                    text = await response.text()
                    print(f"   ❌ Health Error: {text}")
        
        except Exception as e:
            print(f"   🔥 Health Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_label_directory())