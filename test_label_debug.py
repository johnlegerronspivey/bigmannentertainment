#!/usr/bin/env python3
"""
Debug label endpoints
"""

import requests
import json

BASE_URL = "https://1a0564b8-b055-49be-b4c3-af86a4884970.preview.emergentagent.com/api"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OWE5OGExOC1mYWNjLTQ1ZGItOTJiOC1kOTBmY2U5M2M0MmQiLCJlbWFpbCI6ImxhYmVsdGVzdEBiaWdtYW5uZW50ZXJ0YWlubWVudC5jb20iLCJpc19hZG1pbiI6ZmFsc2UsImV4cCI6MTc1NTQ3MjkyMn0.7qOdq0j6jzsi8bYoArcTWB6jOCCZjlRw6hY3mHauNJQ"

def test_single_endpoint():
    """Test a single endpoint with detailed debugging"""
    
    url = f"{BASE_URL}/label/artists"
    headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
    
    print(f"Testing URL: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Data: {data}")
            except:
                print("Response is not valid JSON")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request exception: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_demo_submission():
    """Test demo submission with detailed debugging"""
    
    url = f"{BASE_URL}/label/ar/demos"
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
    
    print(f"\nTesting Demo Submission URL: {url}")
    print(f"Data: {json.dumps(demo_data, indent=2)}")
    
    try:
        # Test without auth first (public endpoint)
        response = requests.post(url, json=demo_data, timeout=10)
        print(f"Status Code (no auth): {response.status_code}")
        print(f"Response Text (no auth): {response.text}")
        
        # Test with auth
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
        response = requests.post(url, json=demo_data, headers=headers, timeout=10)
        print(f"Status Code (with auth): {response.status_code}")
        print(f"Response Text (with auth): {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 DEBUGGING BIG MANN ENTERTAINMENT LABEL ENDPOINTS")
    print("=" * 60)
    
    print("1. Testing Artist Roster Endpoint...")
    test_single_endpoint()
    
    print("\n2. Testing Demo Submission Endpoint...")
    test_demo_submission()