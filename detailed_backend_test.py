#!/usr/bin/env python3
"""
Detailed Backend Testing for Big Mann Entertainment Platform
Focus on Upload-to-Payout Workflow Issues
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class DetailedTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "workflow.tester@bigmannentertainment.com"
        self.test_user_password = "WorkflowTest2025!"
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method: str, endpoint: str, data: dict = None, 
                          files: dict = None, headers: dict = None) -> dict:
        """Make HTTP request with detailed error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add auth header if available
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers, params=data) as response:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    return {
                        "status": response.status,
                        "data": response_data,
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                if files:
                    # Handle file upload
                    form_data = aiohttp.FormData()
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, str(value))
                    for key, file_data in files.items():
                        form_data.add_field(key, file_data[1], filename=file_data[0])
                    
                    async with self.session.post(url, data=form_data, headers=headers) as response:
                        response_text = await response.text()
                        try:
                            response_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            response_data = {"raw_response": response_text}
                        return {
                            "status": response.status,
                            "data": response_data,
                            "headers": dict(response.headers)
                        }
                else:
                    # Handle JSON data
                    json_headers = headers or {}
                    json_headers["Content-Type"] = "application/json"
                    async with self.session.post(url, json=data, headers=json_headers) as response:
                        response_text = await response.text()
                        try:
                            response_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            response_data = {"raw_response": response_text}
                        return {
                            "status": response.status,
                            "data": response_data,
                            "headers": dict(response.headers)
                        }
                        
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
            
    async def authenticate(self):
        """Authenticate user"""
        print("🔐 AUTHENTICATING USER")
        
        # Try login first
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        response = await self.make_request("POST", "/auth/login", login_data)
        
        if response["status"] == 200 and "access_token" in response["data"]:
            self.auth_token = response["data"]["access_token"]
            print(f"✅ Login successful")
            return True
        elif response["status"] == 401:
            # User doesn't exist, try registration
            print("User doesn't exist, registering...")
            
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": "Workflow Tester",
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "CA",
                "postal_code": "90210",
                "country": "USA"
            }
            
            response = await self.make_request("POST", "/auth/register", registration_data)
            
            if response["status"] in [200, 201] and "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
                print(f"✅ Registration successful")
                return True
            else:
                print(f"❌ Registration failed: {response}")
                return False
        else:
            print(f"❌ Login failed: {response}")
            return False
            
    async def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n🏥 TESTING HEALTH ENDPOINTS")
        
        # Test media health
        response = await self.make_request("GET", "/media/health")
        print(f"Media Health: Status {response['status']}")
        if response["status"] == 200:
            print(f"   ✅ Media service healthy: {response['data']}")
        else:
            print(f"   ❌ Media service issue: {response['data']}")
            
        # Test AWS health
        response = await self.make_request("GET", "/aws/health")
        print(f"AWS Health: Status {response['status']}")
        if response["status"] == 200:
            print(f"   ✅ AWS services: {response['data']}")
        else:
            print(f"   ❌ AWS services issue: {response['data']}")
            
    async def test_media_upload_detailed(self):
        """Test media upload with detailed error analysis"""
        print("\n📁 TESTING MEDIA UPLOAD (DETAILED)")
        
        # Create test audio file content (proper WAV header)
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x44\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x08\x00\x00'
        test_audio_content = wav_header + b'\x00' * 2048
        
        # Test media upload
        upload_data = {
            "title": "Test Upload Track",
            "description": "Testing upload functionality",
            "category": "hip-hop",
            "price": "9.99",
            "tags": "test,upload,workflow"
        }
        
        files = {
            "file": ("test_track.wav", test_audio_content, "audio/wav")
        }
        
        response = await self.make_request("POST", "/media/upload", upload_data, files=files)
        print(f"Media Upload: Status {response['status']}")
        print(f"Response: {response['data']}")
        
        if response["status"] == 200:
            print("   ✅ Media upload successful")
            return response["data"].get("media_id")
        else:
            print(f"   ❌ Media upload failed: {response['data']}")
            return None
            
    async def test_distribution_detailed(self, media_id=None):
        """Test distribution system with detailed analysis"""
        print("\n🌐 TESTING DISTRIBUTION (DETAILED)")
        
        # Test platforms endpoint
        response = await self.make_request("GET", "/media/platforms")
        print(f"Platforms: Status {response['status']}")
        if response["status"] == 200:
            platforms = response["data"].get("platforms", [])
            print(f"   ✅ Found {len(platforms)} platforms")
            
            # Show platform categories
            categories = {}
            for platform in platforms:
                cat = platform.get("type", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
            print(f"   Categories: {categories}")
        else:
            print(f"   ❌ Platforms failed: {response['data']}")
            
        # Test distribution if we have media
        if media_id:
            distribution_data = {
                "media_id": media_id,
                "platforms": ["spotify", "apple_music", "youtube"],
                "custom_message": "Test distribution"
            }
            
            response = await self.make_request("POST", "/media/distribute", distribution_data)
            print(f"Distribution: Status {response['status']}")
            print(f"Response: {response['data']}")
            
            if response["status"] == 200:
                print("   ✅ Distribution successful")
                return response["data"].get("distribution_id")
            else:
                print(f"   ❌ Distribution failed: {response['data']}")
                return None
        else:
            print("   ⚠️ No media ID for distribution test")
            return None
            
    async def test_earnings_detailed(self):
        """Test earnings system with detailed analysis"""
        print("\n💰 TESTING EARNINGS (DETAILED)")
        
        # Test earnings endpoint
        response = await self.make_request("GET", "/media/earnings")
        print(f"Earnings: Status {response['status']}")
        print(f"Response: {response['data']}")
        
        if response["status"] == 200:
            print("   ✅ Earnings retrieved successfully")
        else:
            print(f"   ❌ Earnings failed: {response['data']}")
            
        # Test analytics
        response = await self.make_request("GET", "/media/analytics")
        print(f"Analytics: Status {response['status']}")
        if response["status"] == 200:
            analytics = response["data"]
            print(f"   ✅ Analytics: {analytics}")
        else:
            print(f"   ❌ Analytics failed: {response['data']}")
            
    async def test_payout_detailed(self):
        """Test payout system with detailed analysis"""
        print("\n💸 TESTING PAYOUT (DETAILED)")
        
        # Test payout request
        payout_data = {
            "amount": 25.00,
            "payment_method": "paypal",
            "payment_details": {
                "email": self.test_user_email
            }
        }
        
        response = await self.make_request("POST", "/media/request-payout", payout_data)
        print(f"Payout Request: Status {response['status']}")
        print(f"Response: {response['data']}")
        
        if response["status"] == 200:
            print("   ✅ Payout request successful")
        else:
            print(f"   ❌ Payout request failed: {response['data']}")
            
        # Test payment packages
        response = await self.make_request("GET", "/payments/packages")
        print(f"Payment Packages: Status {response['status']}")
        if response["status"] == 200:
            packages = response["data"].get("packages", [])
            print(f"   ✅ Found {len(packages)} payment packages")
        else:
            print(f"   ❌ Payment packages failed: {response['data']}")
            
    async def run_detailed_tests(self):
        """Run detailed workflow tests"""
        print("🎯 DETAILED UPLOAD-TO-PAYOUT WORKFLOW TESTING")
        print("="*60)
        
        try:
            await self.setup_session()
            
            # Authenticate
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed")
                return
                
            # Test health endpoints
            await self.test_health_endpoints()
            
            # Test media upload
            media_id = await self.test_media_upload_detailed()
            
            # Test distribution
            distribution_id = await self.test_distribution_detailed(media_id)
            
            # Test earnings
            await self.test_earnings_detailed()
            
            # Test payout
            await self.test_payout_detailed()
            
            print("\n🏁 DETAILED TESTING COMPLETED")
            
        except Exception as e:
            print(f"❌ Critical error: {str(e)}")
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = DetailedTester()
    await tester.run_detailed_tests()

if __name__ == "__main__":
    asyncio.run(main())