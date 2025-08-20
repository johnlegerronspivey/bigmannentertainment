#!/usr/bin/env python3
"""
Test API structure to understand routing
"""

import requests
import json

BASE_URL = "https://content-nexus-15.preview.emergentagent.com"

def test_api_endpoints():
    """Test various API endpoints to understand the structure"""
    
    endpoints_to_test = [
        "/api/distribution/platforms",  # Known working endpoint
        "/api/auth/register",  # Known working endpoint (POST)
        "/api/label/artists",  # Label endpoint we want to test
        "/api/label/ar/demos",  # Demo submission endpoint
        "/docs",  # FastAPI docs
        "/openapi.json",  # OpenAPI spec
    ]
    
    for endpoint in endpoints_to_test:
        url = f"{BASE_URL}{endpoint}"
        print(f"\nTesting: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS")
                if endpoint == "/openapi.json":
                    # Check if label endpoints are in the OpenAPI spec
                    try:
                        spec = response.json()
                        paths = spec.get('paths', {})
                        label_paths = [path for path in paths.keys() if '/label/' in path]
                        print(f"Label paths in OpenAPI: {label_paths[:5]}")
                    except:
                        print("Could not parse OpenAPI spec")
                elif "distribution" in endpoint:
                    print("Distribution endpoint working - API is accessible")
            elif response.status_code == 404:
                print("❌ NOT FOUND")
            elif response.status_code == 405:
                print("⚠️ METHOD NOT ALLOWED (endpoint exists but wrong method)")
            else:
                print(f"❌ ERROR: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT")
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🔍 TESTING API STRUCTURE")
    print("=" * 50)
    test_api_endpoints()