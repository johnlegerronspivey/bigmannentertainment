#!/usr/bin/env python3
"""
ISRC Generation Fix Test - Testing with correct parameters
"""

import requests
import json

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "upc.isrc.tester@bigmannentertainment.com"
TEST_USER_PASSWORD = "TestPassword123!"

def authenticate():
    """Get auth token"""
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_isrc_with_correct_params():
    """Test ISRC generation with all required parameters"""
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with JSON data including artist_name and track_title
    json_data = {
        "product_name": "Big Mann Hip Hop Track",
        "product_category": "music",
        "artist_name": "Big Mann Entertainment",
        "track_title": "Urban Anthem"
    }
    
    print("🎵 Testing ISRC generation with complete JSON data...")
    response = requests.post(f"{BACKEND_URL}/business/generate-isrc", json=json_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ ISRC JSON generation successful!")
        print(f"   Response: {result}")
    else:
        print(f"❌ ISRC JSON generation failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test with Form data
    form_data = {
        "product_name": "Big Mann R&B Track",
        "product_category": "music",
        "artist_name": "Big Mann Entertainment",
        "track_title": "Smooth Vibes"
    }
    
    print("\n🎵 Testing ISRC generation with complete Form data...")
    response = requests.post(f"{BACKEND_URL}/business/generate-isrc", data=form_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ ISRC Form generation successful!")
        print(f"   Response: {result}")
    else:
        print(f"❌ ISRC Form generation failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_isrc_with_correct_params()