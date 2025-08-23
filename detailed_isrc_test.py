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

def test_upc_generation():
    """Test UPC generation endpoint in detail"""
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_data = {
        "product_name": "Test Song for ISRC Verification",
        "artist_name": "ISRC Test Artist",
        "album_title": "ISRC Test Album",
        "track_title": "ISRC Verification Track",
        "product_category": "audio",
        "record_label": "Big Mann Entertainment",
        "publisher_name": "Big Mann Entertainment Publishing",
        "songwriter_credits": "Test Songwriter"
    }
    
    print("🎼 Testing /business/generate-upc endpoint")
    print("=" * 50)
    
    response = requests.post(f"{BACKEND_URL}/business/generate-upc", json=test_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    # Check for ISRC in response
    response_data = response.json()
    if isinstance(response_data, dict):
        for key, value in response_data.items():
            if "isrc" in key.lower() or ("QZ9H8" in str(value) or "QZ9-H8" in str(value)):
                print(f"\n✅ Found potential ISRC field: {key} = {value}")

if __name__ == "__main__":
    test_upc_generation()