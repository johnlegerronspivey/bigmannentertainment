#!/usr/bin/env python3
"""
Test authenticated label endpoints
"""

import requests
import json

BASE_URL = "https://content-nexus-15.preview.emergentagent.com/api"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OWE5OGExOC1mYWNjLTQ1ZGItOTJiOC1kOTBmY2U5M2M0MmQiLCJlbWFpbCI6ImxhYmVsdGVzdEBiaWdtYW5uZW50ZXJ0YWlubWVudC5jb20iLCJpc19hZG1pbiI6ZmFsc2UsImV4cCI6MTc1NTQ3MjkyMn0.7qOdq0j6jzsi8bYoArcTWB6jOCCZjlRw6hY3mHauNJQ"

def make_request(method: str, endpoint: str, **kwargs):
    """Make HTTP request with auth header"""
    url = f"{BASE_URL}{endpoint}"
    headers = kwargs.get('headers', {})
    headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
    kwargs['headers'] = headers
    
    try:
        response = requests.request(method, url, **kwargs)
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_endpoints():
    """Test various label endpoints"""
    
    endpoints_to_test = [
        ("GET", "/label/artists", "Get Artist Roster"),
        ("GET", "/label/ar/demos", "Get Demo Submissions"),
        ("GET", "/label/ar/industry-trends", "Get Industry Trends"),
        ("GET", "/label/ar/industry-contacts?query=radio", "Get Industry Contacts"),
        ("GET", "/label/dashboard", "Get Label Dashboard"),
        ("GET", "/label/studios/available", "Get Available Studios"),
        ("POST", "/label/ar/demos", "Submit Demo (Public)"),
    ]
    
    for method, endpoint, description in endpoints_to_test:
        print(f"\nTesting {description}...")
        print(f"{method} {endpoint}")
        
        if method == "POST" and "demos" in endpoint:
            # Test demo submission
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
            response = make_request(method, endpoint, json=demo_data)
        else:
            response = make_request(method, endpoint)
        
        if response:
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("✅ SUCCESS")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Returned {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   Returned object with keys: {list(data.keys())[:5]}")
                except:
                    print("   Response is not JSON")
            elif response.status_code == 403:
                print("❌ FORBIDDEN - Need admin permissions")
            elif response.status_code == 404:
                print("❌ NOT FOUND - Endpoint not available")
            else:
                print(f"❌ FAILED - {response.text[:100]}")
        else:
            print("❌ REQUEST FAILED")

if __name__ == "__main__":
    print("🎵 TESTING BIG MANN ENTERTAINMENT LABEL ENDPOINTS WITH AUTH")
    print("=" * 70)
    test_endpoints()