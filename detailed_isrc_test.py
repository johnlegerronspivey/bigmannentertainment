#!/usr/bin/env python3
"""
Detailed ISRC Generation Test - Check what the generate-upc endpoint returns
"""

import requests
import json

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "isrc.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "ISRCTest2025!"

def authenticate():
    """Get auth token"""
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_isrc_generation():
    """Test ISRC generation endpoint in detail"""
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_data = {
        "artist_name": "ISRC Test Artist",
        "track_title": "ISRC Verification Track",
        "album_title": "ISRC Test Album",
        "record_label": "Big Mann Entertainment",
        "release_year": 2025
    }
    
    print("🎼 Testing /business/generate-isrc endpoint")
    print("=" * 50)
    
    response = requests.post(f"{BACKEND_URL}/business/generate-isrc", json=test_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    # Check for ISRC in response
    response_data = response.json()
    if isinstance(response_data, dict):
        for key, value in response_data.items():
            if "isrc" in key.lower() or ("QZ9H8" in str(value) or "QZ9-H8" in str(value)):
                print(f"\n✅ Found ISRC field: {key} = {value}")
                if "QZ9H8" in str(value) or "QZ9-H8" in str(value):
                    print("✅ ISRC contains correct QZ9H8 prefix!")
                else:
                    print("❌ ISRC does not contain QZ9H8 prefix")

if __name__ == "__main__":
    test_isrc_generation()