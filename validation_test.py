#!/usr/bin/env python3
"""
Quick validation test to verify file validation behavior
"""

import requests
import io
import time

BACKEND_URL = "https://bigmannentertainment.com/api"
TEST_USER_EMAIL = f"validation.test.{int(time.time())}@bigmannentertainment.com"
TEST_USER_PASSWORD = "ValidationTest123!"

def test_validation():
    session = requests.Session()
    
    # Register and login
    user_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": "Validation Test User",
        "date_of_birth": "1990-01-01T00:00:00",
        "address_line1": "123 Test Street",
        "city": "Test City",
        "state_province": "Test State",
        "postal_code": "12345",
        "country": "United States"
    }
    
    reg_response = session.post(f"{BACKEND_URL}/auth/register", json=user_data)
    if reg_response.status_code not in [200, 201]:
        print(f"Registration failed: {reg_response.status_code}")
        return
    
    user_id = reg_response.json().get("user", {}).get("id")
    
    login_response = session.post(f"{BACKEND_URL}/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    token = login_response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("🔍 Testing file validation behavior...")
    
    # Test 1: Oversized file
    print("\n1. Testing oversized audio file (60MB > 50MB limit):")
    oversized_file = io.BytesIO(b'ID3\x03' + b'\x00' * (60 * 1024 * 1024))
    
    files = {'file': ('oversized.mp3', oversized_file, 'audio/mpeg')}
    data = {
        'user_id': user_id,
        'user_email': TEST_USER_EMAIL,
        'user_name': 'Test User',
        'title': 'Oversized Test',
        'description': 'Should be rejected',
        'category': 'music',
        'send_notification': 'false'
    }
    
    response = session.post(f"{BACKEND_URL}/media/s3/upload/audio", files=files, data=data)
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}")
    
    # Test 2: Unsupported format
    print("\n2. Testing unsupported file format (text/plain for audio):")
    text_file = io.BytesIO(b"This is a text file")
    
    files = {'file': ('test.txt', text_file, 'text/plain')}
    data = {
        'user_id': user_id,
        'user_email': TEST_USER_EMAIL,
        'user_name': 'Test User',
        'title': 'Format Test',
        'description': 'Should be rejected',
        'category': 'music',
        'send_notification': 'false'
    }
    
    response = session.post(f"{BACKEND_URL}/media/s3/upload/audio", files=files, data=data)
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}")
    
    print("\n✅ Validation test completed")

if __name__ == "__main__":
    test_validation()