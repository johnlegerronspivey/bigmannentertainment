#!/usr/bin/env python3
"""
Test public label endpoints that don't require authentication
"""

import requests
import json

BASE_URL = "https://industry-connect-1.preview.emergentagent.com/api"

def test_demo_submission_public():
    """Test POST /api/label/ar/demos (public endpoint - no auth required)"""
    try:
        demo_data = {
            "artist_name": "Demo Artist Test",
            "contact_email": "demoartist@example.com",
            "genre": "hip-hop",
            "submission_type": "demo",
            "audio_files": [
                {
                    "title": "Demo Track 1",
                    "url": "/uploads/demo_track_1.mp3",
                    "duration": "3:45"
                }
            ],
            "bio": "Aspiring artist looking to get signed to Big Mann Entertainment"
        }
        
        response = requests.post(f"{BASE_URL}/label/ar/demos", json=demo_data)
        
        print(f"Demo Submission Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'success' in data and data['success'] and 'submission_id' in data:
                print(f"✅ Demo submission successful: {data.get('submission_id')}")
                return True
            else:
                print(f"❌ Demo submission failed - Invalid response format")
                return False
        else:
            print(f"❌ Demo submission failed")
            return False
            
    except Exception as e:
        print(f"❌ Demo submission failed - Exception: {str(e)}")
        return False

def test_register_new_user():
    """Try to register a new user for testing"""
    try:
        from datetime import datetime, timedelta
        
        user_data = {
            "email": "labeltest@bigmannentertainment.com",
            "password": "LabelTest2025!",
            "full_name": "Label Test User",
            "business_name": "Big Mann Entertainment",
            "date_of_birth": (datetime.utcnow() - timedelta(days=25*365)).isoformat(),
            "address_line1": "1314 Lincoln Heights Street",
            "city": "Alexander City",
            "state_province": "Alabama",
            "postal_code": "35010",
            "country": "United States"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        print(f"User Registration Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if 'access_token' in data:
                print(f"✅ User registration successful")
                return data['access_token']
            else:
                print(f"❌ User registration failed - no access token")
                return None
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ User already exists, trying to login...")
            return test_login_new_user()
        else:
            print(f"❌ User registration failed")
            return None
            
    except Exception as e:
        print(f"❌ User registration failed - Exception: {str(e)}")
        return None

def test_login_new_user():
    """Try to login with the new test user"""
    try:
        login_data = {
            "email": "labeltest@bigmannentertainment.com",
            "password": "LabelTest2025!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        print(f"Login Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print(f"✅ Login successful")
                return data['access_token']
            else:
                print(f"❌ Login failed - no access token")
                return None
        else:
            print(f"❌ Login failed")
            return None
            
    except Exception as e:
        print(f"❌ Login failed - Exception: {str(e)}")
        return None

if __name__ == "__main__":
    print("🎵 TESTING BIG MANN ENTERTAINMENT LABEL ENDPOINTS")
    print("=" * 60)
    
    # Test public demo submission endpoint
    print("\n1. Testing Public Demo Submission Endpoint...")
    test_demo_submission_public()
    
    # Try to get authentication for other tests
    print("\n2. Testing Authentication...")
    auth_token = test_register_new_user()
    
    if auth_token:
        print(f"\n✅ Got authentication token: {auth_token[:20]}...")
        print("Authentication successful - can proceed with authenticated endpoint tests")
    else:
        print("\n❌ Could not get authentication token")
        print("Cannot test authenticated endpoints")