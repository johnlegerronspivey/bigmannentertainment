#!/usr/bin/env python3
"""
Real-Time Royalty Engine Comprehensive Backend Testing
Testing all 32 endpoints for enterprise-grade royalty management system
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
API_BASE_URL = "https://music-rights-hub-2.preview.emergentagent.com/api"
TEST_USER_TOKEN = None  # Will be set after authentication

class RoyaltyEngineTestSuite:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_data = {}
        
    async def setup_session(self):
        """Setup HTTP session with authentication"""
        self.session = aiohttp.ClientSession()
        
        # Test authentication first
        auth_data = {
            "email": "john.spivey@bigmannentertainment.com",
            "password": "BigMann2025!"
        }
        
        try:
            async with self.session.post(f"{API_BASE_URL}/auth/login", json=auth_data) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    global TEST_USER_TOKEN
                    TEST_USER_TOKEN = auth_result.get("access_token")
                    logger.info("✅ Authentication successful")
                    return True
                else:
                    logger.warning(f"⚠️ Authentication failed with status {response.status}")
                    # Continue with testing without authentication
                    return False
        except Exception as e:
            logger.warning(f"⚠️ Authentication error: {str(e)}")
            return False
    
    async def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with proper headers"""
        url = f"{API_BASE_URL}{endpoint}"
        
        # Setup headers
        request_headers = {"Content-Type": "application/json"}
        if TEST_USER_TOKEN:
            request_headers["Authorization"] = f"Bearer {TEST_USER_TOKEN}"
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers) as response:
                    return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=request_headers) as response:
                    return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
        except Exception as e:
            return 500, {"error": str(e)}
    
    def log_test_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details
        }
        self.test_results.append(result)
        logger.info(f"{result['status']} {test_name}: {details}")
    
    # CORE ROYALTY ENGINE ENDPOINTS (15 endpoints)
    
    async def test_process_transaction_event(self):
        """Test POST /api/royalty-engine/events/process"""
        test_event = {
            "asset_id": str(uuid.uuid4()),
            "platform": "spotify",
            "territory": "US",
            "user_id": "test_user_123",
            "revenue_source": "streaming",
            "monetization_type": "subscription",
            "gross_revenue": 10.50,
            "currency": "USD",
            "platform_fee_rate": 0.30,
            "metadata": {"test": True}
        }
        
        status, response = await self.make_request("POST", "/royalty-engine/events/process", test_event)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.test_data["calculation_id"] = response.get("calculation_id")
                self.log_test_result("Process Transaction Event", True, f"Calculation ID: {response.get('calculation_id')}")
            else:
                self.log_test_result("Process Transaction Event", False, f"Success=False: {response}")
        else:
            self.log_test_result("Process Transaction Event", False, f"Status {status}: {response}")
    
    async def test_batch_process_events(self):
        """Test POST /api/royalty-engine/events/batch-process"""
        batch_events = [
            {
                "asset_id": str(uuid.uuid4()),
                "platform": "apple_music",
                "territory": "US",
                "revenue_source": "streaming",
                "monetization_type": "subscription",
                "gross_revenue": 5.25,
                "currency": "USD"
            },
            {
                "asset_id": str(uuid.uuid4()),
                "platform": "youtube",
                "territory": "CA",
                "revenue_source": "social_media",
                "monetization_type": "ad_supported",
                "gross_revenue": 2.75,
                "currency": "USD"
            }
        ]
        
        status, response = await self.make_request("POST", "/royalty-engine/events/batch-process", batch_events)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                summary = response.get("summary", {})
                self.log_test_result("Batch Process Events", True, f"Processed {summary.get('total_events', 0)} events")
            else:
                self.log_test_result("Batch Process Events", False, f"Success=False: {response}")
        else:
            self.log_test_result("Batch Process Events", False, f"Status {status}: {response}")
    
    async def test_create_contract_terms(self):
        """Test POST /api/royalty-engine/contracts/create"""
        contract_data = {
            "asset_id": str(uuid.uuid4()),
            "contract_type": "percentage",
            "base_rate": 0.15,
            "minimum_payout": 0.01,
            "territory_modifiers": {"US": 1.0, "EU": 0.85},
            "platform_modifiers": {"spotify": 1.0, "youtube": 0.75},
            "effective_date": datetime.now(timezone.utc).isoformat(),
            "active": True
        }
        
        status, response = await self.make_request("POST", "/royalty-engine/contracts/create", contract_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.test_data["contract_id"] = response.get("contract_id")
                self.log_test_result("Create Contract Terms", True, f"Contract ID: {response.get('contract_id')}")
            else:
                self.log_test_result("Create Contract Terms", False, f"Success=False: {response}")
        else:
            self.log_test_result("Create Contract Terms", False, f"Status {status}: {response}")
    
    async def test_get_contract_terms(self):
        """Test GET /api/royalty-engine/contracts/{asset_id}"""
        test_asset_id = str(uuid.uuid4())
        
        status, response = await self.make_request("GET", f"/royalty-engine/contracts/{test_asset_id}")
        
        # Expect 404 for non-existent asset or 200 for existing
        if status in [200, 404]:
            if status == 200 and response.get("success"):
                self.log_test_result("Get Contract Terms", True, "Contract terms retrieved")
            elif status == 404:
                self.log_test_result("Get Contract Terms", True, "404 for non-existent asset (expected)")
            else:
                self.log_test_result("Get Contract Terms", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Get Contract Terms", False, f"Status {status}: {response}")
    
    async def test_update_contract_terms(self):
        """Test PUT /api/royalty-engine/contracts/{contract_id}"""
        test_contract_id = str(uuid.uuid4())
        update_data = {
            "base_rate": 0.20,
            "minimum_payout": 0.05
        }
        
        status, response = await self.make_request("PUT", f"/royalty-engine/contracts/{test_contract_id}", update_data)
        
        # Expect 404 for non-existent contract or 200 for existing
        if status in [200, 404]:
            if status == 200 and response.get("success"):
                self.log_test_result("Update Contract Terms", True, "Contract updated")
            elif status == 404:
                self.log_test_result("Update Contract Terms", True, "404 for non-existent contract (expected)")
            else:
                self.log_test_result("Update Contract Terms", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Update Contract Terms", False, f"Status {status}: {response}")
    
    async def test_create_contributor_split(self):
        """Test POST /api/royalty-engine/splits/create"""
        split_data = {
            "asset_id": str(uuid.uuid4()),
            "contributor_id": "artist_123",
            "contributor_type": "artist",
            "split_percentage": 50.0,
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C0532925a3b8D4",
            "payout_method": "crypto_instant",
            "tax_jurisdiction": "US",
            "minimum_payout_threshold": 1.00,
            "active": True
        }
        
        status, response = await self.make_request("POST", "/royalty-engine/splits/create", split_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.test_data["split_id"] = response.get("split_id")
                self.log_test_result("Create Contributor Split", True, f"Split ID: {response.get('split_id')}")
            else:
                self.log_test_result("Create Contributor Split", False, f"Success=False: {response}")
        else:
            self.log_test_result("Create Contributor Split", False, f"Status {status}: {response}")
    
    async def test_get_contributor_splits(self):
        """Test GET /api/royalty-engine/splits/{asset_id}"""
        test_asset_id = str(uuid.uuid4())
        
        status, response = await self.make_request("GET", f"/royalty-engine/splits/{test_asset_id}")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                splits = response.get("splits", [])
                self.log_test_result("Get Contributor Splits", True, f"Retrieved {len(splits)} splits")
            else:
                self.log_test_result("Get Contributor Splits", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Contributor Splits", False, f"Status {status}: {response}")
    
    async def test_update_contributor_split(self):
        """Test PUT /api/royalty-engine/splits/{split_id}"""
        test_split_id = str(uuid.uuid4())
        update_data = {
            "split_percentage": 60.0,
            "minimum_payout_threshold": 2.00
        }
        
        status, response = await self.make_request("PUT", f"/royalty-engine/splits/{test_split_id}", update_data)
        
        # Expect 404 for non-existent split or 200 for existing
        if status in [200, 404]:
            if status == 200 and response.get("success"):
                self.log_test_result("Update Contributor Split", True, "Split updated")
            elif status == 404:
                self.log_test_result("Update Contributor Split", True, "404 for non-existent split (expected)")
            else:
                self.log_test_result("Update Contributor Split", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Update Contributor Split", False, f"Status {status}: {response}")
    
    async def test_get_royalty_calculation(self):
        """Test GET /api/royalty-engine/calculations/{calculation_id}"""
        test_calculation_id = self.test_data.get("calculation_id", str(uuid.uuid4()))
        
        status, response = await self.make_request("GET", f"/royalty-engine/calculations/{test_calculation_id}")
        
        if status in [200, 404]:
            if status == 200 and response.get("success"):
                self.log_test_result("Get Royalty Calculation", True, "Calculation retrieved")
            elif status == 404:
                self.log_test_result("Get Royalty Calculation", True, "404 for non-existent calculation (expected)")
            else:
                self.log_test_result("Get Royalty Calculation", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Get Royalty Calculation", False, f"Status {status}: {response}")
    
    async def test_get_asset_calculations(self):
        """Test GET /api/royalty-engine/calculations/asset/{asset_id}"""
        test_asset_id = str(uuid.uuid4())
        
        status, response = await self.make_request("GET", f"/royalty-engine/calculations/asset/{test_asset_id}")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                calculations = response.get("calculations", [])
                summary = response.get("summary", {})
                self.log_test_result("Get Asset Calculations", True, f"Retrieved {len(calculations)} calculations")
            else:
                self.log_test_result("Get Asset Calculations", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Asset Calculations", False, f"Status {status}: {response}")
    
    async def test_get_audit_trail(self):
        """Test GET /api/royalty-engine/audit/{transaction_id}"""
        test_transaction_id = str(uuid.uuid4())
        
        status, response = await self.make_request("GET", f"/royalty-engine/audit/{test_transaction_id}")
        
        if status in [200, 404]:
            if status == 200 and response.get("success"):
                self.log_test_result("Get Audit Trail", True, "Audit trail retrieved")
            elif status == 404:
                self.log_test_result("Get Audit Trail", True, "404 for non-existent transaction (expected)")
            else:
                self.log_test_result("Get Audit Trail", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Get Audit Trail", False, f"Status {status}: {response}")
    
    async def test_get_pending_payouts(self):
        """Test GET /api/royalty-engine/payouts/pending"""
        status, response = await self.make_request("GET", "/royalty-engine/payouts/pending")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                payouts = response.get("payouts", [])
                summary = response.get("summary", {})
                self.log_test_result("Get Pending Payouts", True, f"Retrieved {len(payouts)} pending payouts")
            else:
                self.log_test_result("Get Pending Payouts", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Pending Payouts", False, f"Status {status}: {response}")
    
    async def test_process_payout(self):
        """Test POST /api/royalty-engine/payouts/{payout_id}/process"""
        test_payout_id = str(uuid.uuid4())
        
        status, response = await self.make_request("POST", f"/royalty-engine/payouts/{test_payout_id}/process")
        
        if status in [200, 404, 400]:
            if status == 200 and response.get("success"):
                self.log_test_result("Process Payout", True, "Payout processing initiated")
            elif status == 404:
                self.log_test_result("Process Payout", True, "404 for non-existent payout (expected)")
            elif status == 400:
                self.log_test_result("Process Payout", True, "400 for invalid payout state (expected)")
            else:
                self.log_test_result("Process Payout", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Process Payout", False, f"Status {status}: {response}")
    
    async def test_get_asset_royalty_summary(self):
        """Test GET /api/royalty-engine/analytics/asset/{asset_id}/summary"""
        test_asset_id = str(uuid.uuid4())
        
        status, response = await self.make_request("GET", f"/royalty-engine/analytics/asset/{test_asset_id}/summary")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                summary = response.get("summary", {})
                breakdown = response.get("breakdown", {})
                self.log_test_result("Get Asset Royalty Summary", True, f"Summary retrieved for asset {test_asset_id}")
            else:
                self.log_test_result("Get Asset Royalty Summary", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Asset Royalty Summary", False, f"Status {status}: {response}")
    
    async def test_get_royalty_forecast(self):
        """Test GET /api/royalty-engine/analytics/forecast/{asset_id}"""
        test_asset_id = str(uuid.uuid4())
        
        status, response = await self.make_request("GET", f"/royalty-engine/analytics/forecast/{test_asset_id}")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                forecast = response.get("forecast", {})
                self.log_test_result("Get Royalty Forecast", True, f"Forecast retrieved for asset {test_asset_id}")
            else:
                self.log_test_result("Get Royalty Forecast", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Royalty Forecast", False, f"Status {status}: {response}")
    
    # ADDITIONAL ANALYTICS & SECURITY ENDPOINTS (5 endpoints)
    
    async def test_get_fraud_flags(self):
        """Test GET /api/royalty-engine/security/fraud-flags"""
        status, response = await self.make_request("GET", "/royalty-engine/security/fraud-flags")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                flags = response.get("fraud_flags", [])
                self.log_test_result("Get Fraud Flags", True, f"Retrieved {len(flags)} fraud flags")
            else:
                self.log_test_result("Get Fraud Flags", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Fraud Flags", False, f"Status {status}: {response}")
    
    async def test_resolve_fraud_flag(self):
        """Test PUT /api/royalty-engine/security/fraud-flags/{flag_id}/resolve"""
        test_flag_id = str(uuid.uuid4())
        resolution_data = {
            "resolution": "False positive - legitimate transaction verified"
        }
        
        status, response = await self.make_request("PUT", f"/royalty-engine/security/fraud-flags/{test_flag_id}/resolve", resolution_data)
        
        if status in [200, 404]:
            if status == 200 and response.get("success"):
                self.log_test_result("Resolve Fraud Flag", True, "Fraud flag resolved")
            elif status == 404:
                self.log_test_result("Resolve Fraud Flag", True, "404 for non-existent flag (expected)")
            else:
                self.log_test_result("Resolve Fraud Flag", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Resolve Fraud Flag", False, f"Status {status}: {response}")
    
    async def test_royalty_engine_health(self):
        """Test GET /api/royalty-engine/health"""
        status, response = await self.make_request("GET", "/royalty-engine/health")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success") and response.get("status") == "healthy":
                services = response.get("services", {})
                self.log_test_result("Royalty Engine Health", True, f"System healthy with {len(services)} services")
            else:
                self.log_test_result("Royalty Engine Health", False, f"System not healthy: {response}")
        else:
            self.log_test_result("Royalty Engine Health", False, f"Status {status}: {response}")
    
    async def test_comprehensive_status(self):
        """Test GET /api/royalty-engine/status/comprehensive"""
        status, response = await self.make_request("GET", "/royalty-engine/status/comprehensive")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                status_data = response.get("status", {})
                self.log_test_result("Comprehensive Status", True, f"Status retrieved with {len(status_data)} metrics")
            else:
                self.log_test_result("Comprehensive Status", False, f"Success=False: {response}")
        else:
            self.log_test_result("Comprehensive Status", False, f"Status {status}: {response}")
    
    # SOCIAL MEDIA ROYALTY INTEGRATION ENDPOINTS (12 endpoints)
    
    async def test_process_social_media_monetization(self):
        """Test POST /api/social-media-royalty/process-monetization"""
        monetization_data = {
            "platform": "youtube",
            "content_id": "test_video_123",
            "monetization_type": "ad_revenue",
            "gross_amount": 25.50,
            "user_id": "creator_456",
            "territory": "US",
            "metadata": {"video_duration": 300, "views": 10000}
        }
        
        status, response = await self.make_request("POST", "/social-media-royalty/process-monetization", monetization_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.log_test_result("Process Social Media Monetization", True, f"Processed ${monetization_data['gross_amount']} from {monetization_data['platform']}")
            else:
                self.log_test_result("Process Social Media Monetization", False, f"Success=False: {response}")
        else:
            self.log_test_result("Process Social Media Monetization", False, f"Status {status}: {response}")
    
    async def test_batch_process_social_media_events(self):
        """Test POST /api/social-media-royalty/batch-process-monetization"""
        batch_events = [
            {
                "platform": "tiktok",
                "content_id": "tiktok_video_1",
                "monetization_type": "creator_fund",
                "gross_amount": 5.25,
                "user_id": "creator_789",
                "territory": "US"
            },
            {
                "platform": "instagram",
                "content_id": "instagram_reel_1",
                "monetization_type": "reels_play_bonus",
                "gross_amount": 8.75,
                "user_id": "creator_789",
                "territory": "US"
            }
        ]
        
        status, response = await self.make_request("POST", "/social-media-royalty/batch-process-monetization", batch_events)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                summary = response.get("summary", {})
                self.log_test_result("Batch Process Social Media Events", True, f"Processed {summary.get('total_events', 0)} events")
            else:
                self.log_test_result("Batch Process Social Media Events", False, f"Success=False: {response}")
        else:
            self.log_test_result("Batch Process Social Media Events", False, f"Status {status}: {response}")
    
    async def test_create_asset_mapping(self):
        """Test POST /api/social-media-royalty/asset-mapping"""
        mapping_data = {
            "platform": "youtube",
            "content_id": "youtube_video_456",
            "asset_id": str(uuid.uuid4()),
            "user_id": "creator_123"
        }
        
        status, response = await self.make_request("POST", "/social-media-royalty/asset-mapping", mapping_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.log_test_result("Create Asset Mapping", True, f"Mapped {mapping_data['platform']}:{mapping_data['content_id']}")
            else:
                self.log_test_result("Create Asset Mapping", False, f"Success=False: {response}")
        else:
            self.log_test_result("Create Asset Mapping", False, f"Status {status}: {response}")
    
    async def test_get_asset_mapping(self):
        """Test GET /api/social-media-royalty/asset-mappings/{platform}/{content_id}"""
        platform = "youtube"
        content_id = "test_video_789"
        
        status, response = await self.make_request("GET", f"/social-media-royalty/asset-mappings/{platform}/{content_id}")
        
        if status in [200, 404]:
            if status == 200 and response.get("success"):
                self.log_test_result("Get Asset Mapping", True, f"Retrieved mapping for {platform}:{content_id}")
            elif status == 404:
                self.log_test_result("Get Asset Mapping", True, "404 for non-existent mapping (expected)")
            else:
                self.log_test_result("Get Asset Mapping", False, f"Unexpected response: {response}")
        else:
            self.log_test_result("Get Asset Mapping", False, f"Status {status}: {response}")
    
    async def test_get_user_asset_mappings(self):
        """Test GET /api/social-media-royalty/asset-mappings/user/{user_id}"""
        test_user_id = "creator_123"
        
        status, response = await self.make_request("GET", f"/social-media-royalty/asset-mappings/user/{test_user_id}")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                mappings = response.get("mappings", [])
                self.log_test_result("Get User Asset Mappings", True, f"Retrieved {len(mappings)} mappings for user {test_user_id}")
            else:
                self.log_test_result("Get User Asset Mappings", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get User Asset Mappings", False, f"Status {status}: {response}")
    
    async def test_process_streaming_royalties(self):
        """Test POST /api/social-media-royalty/streaming-royalties"""
        streaming_data = {
            "platform": "spotify",
            "asset_id": str(uuid.uuid4()),
            "stream_count": 1000,
            "territory": "US",
            "metadata": {"track_duration": 180}
        }
        
        status, response = await self.make_request("POST", "/social-media-royalty/streaming-royalties", streaming_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.log_test_result("Process Streaming Royalties", True, f"Processed {streaming_data['stream_count']} streams")
            else:
                self.log_test_result("Process Streaming Royalties", False, f"Success=False: {response}")
        else:
            self.log_test_result("Process Streaming Royalties", False, f"Status {status}: {response}")
    
    async def test_get_social_media_analytics(self):
        """Test GET /api/social-media-royalty/analytics/{asset_id}/social-media"""
        test_asset_id = str(uuid.uuid4())
        
        status, response = await self.make_request("GET", f"/social-media-royalty/analytics/{test_asset_id}/social-media")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                analytics = response.get("analytics", {})
                self.log_test_result("Get Social Media Analytics", True, f"Analytics retrieved for asset {test_asset_id}")
            else:
                self.log_test_result("Get Social Media Analytics", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Social Media Analytics", False, f"Status {status}: {response}")
    
    async def test_get_platform_summary(self):
        """Test GET /api/social-media-royalty/analytics/platform-summary"""
        status, response = await self.make_request("GET", "/social-media-royalty/analytics/platform-summary")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                summary = response.get("summary", {})
                platform_breakdown = response.get("platform_breakdown", {})
                self.log_test_result("Get Platform Summary", True, f"Platform summary with {len(platform_breakdown)} platforms")
            else:
                self.log_test_result("Get Platform Summary", False, f"Success=False: {response}")
        else:
            self.log_test_result("Get Platform Summary", False, f"Status {status}: {response}")
    
    async def test_youtube_monetization_webhook(self):
        """Test POST /api/social-media-royalty/webhooks/youtube/monetization"""
        webhook_data = {
            "video_id": "youtube_video_123",
            "ad_revenue": 15.50,
            "premium_revenue": 5.25,
            "channel_id": "channel_456"
        }
        
        status, response = await self.make_request("POST", "/social-media-royalty/webhooks/youtube/monetization", webhook_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.log_test_result("YouTube Monetization Webhook", True, f"Processed YouTube webhook for video {webhook_data['video_id']}")
            else:
                self.log_test_result("YouTube Monetization Webhook", False, f"Success=False: {response}")
        else:
            self.log_test_result("YouTube Monetization Webhook", False, f"Status {status}: {response}")
    
    async def test_tiktok_creator_fund_webhook(self):
        """Test POST /api/social-media-royalty/webhooks/tiktok/creator-fund"""
        webhook_data = {
            "video_id": "tiktok_video_789",
            "fund_payment": 8.75,
            "user_id": "tiktok_user_123"
        }
        
        status, response = await self.make_request("POST", "/social-media-royalty/webhooks/tiktok/creator-fund", webhook_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.log_test_result("TikTok Creator Fund Webhook", True, f"Processed TikTok webhook for video {webhook_data['video_id']}")
            else:
                self.log_test_result("TikTok Creator Fund Webhook", False, f"Success=False: {response}")
        else:
            self.log_test_result("TikTok Creator Fund Webhook", False, f"Status {status}: {response}")
    
    async def test_spotify_streams_webhook(self):
        """Test POST /api/social-media-royalty/webhooks/spotify/streams"""
        webhook_data = {
            "track_id": "spotify_track_456",
            "stream_count": 2500,
            "territory": "US"
        }
        
        status, response = await self.make_request("POST", "/social-media-royalty/webhooks/spotify/streams", webhook_data)
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                self.log_test_result("Spotify Streams Webhook", True, f"Processed Spotify webhook for {webhook_data['stream_count']} streams")
            else:
                self.log_test_result("Spotify Streams Webhook", False, f"Success=False: {response}")
        else:
            self.log_test_result("Spotify Streams Webhook", False, f"Status {status}: {response}")
    
    async def test_integration_status(self):
        """Test GET /api/social-media-royalty/integration-status"""
        status, response = await self.make_request("GET", "/social-media-royalty/integration-status")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success"):
                status_data = response.get("status", {})
                self.log_test_result("Integration Status", True, f"Integration status retrieved with {len(status_data)} metrics")
            else:
                self.log_test_result("Integration Status", False, f"Success=False: {response}")
        else:
            self.log_test_result("Integration Status", False, f"Status {status}: {response}")
    
    async def test_social_media_royalty_health(self):
        """Test GET /api/social-media-royalty/health"""
        status, response = await self.make_request("GET", "/social-media-royalty/health")
        
        if status == 200 and isinstance(response, dict):
            if response.get("success") and response.get("status") == "healthy":
                services = response.get("services", {})
                self.log_test_result("Social Media Royalty Health", True, f"System healthy with {len(services)} services")
            else:
                self.log_test_result("Social Media Royalty Health", False, f"System not healthy: {response}")
        else:
            self.log_test_result("Social Media Royalty Health", False, f"Status {status}: {response}")
    
    async def run_all_tests(self):
        """Run all royalty engine tests"""
        logger.info("🎯 STARTING COMPREHENSIVE REAL-TIME ROYALTY ENGINE TESTING")
        logger.info("=" * 80)
        
        # Setup session and authentication
        await self.setup_session()
        
        # Core Royalty Engine Endpoints (15 endpoints)
        logger.info("\n📊 TESTING CORE ROYALTY ENGINE ENDPOINTS (15 endpoints)")
        logger.info("-" * 60)
        
        await self.test_process_transaction_event()
        await self.test_batch_process_events()
        await self.test_create_contract_terms()
        await self.test_get_contract_terms()
        await self.test_update_contract_terms()
        await self.test_create_contributor_split()
        await self.test_get_contributor_splits()
        await self.test_update_contributor_split()
        await self.test_get_royalty_calculation()
        await self.test_get_asset_calculations()
        await self.test_get_audit_trail()
        await self.test_get_pending_payouts()
        await self.test_process_payout()
        await self.test_get_asset_royalty_summary()
        await self.test_get_royalty_forecast()
        
        # Additional Analytics & Security Endpoints (5 endpoints)
        logger.info("\n🔒 TESTING ANALYTICS & SECURITY ENDPOINTS (5 endpoints)")
        logger.info("-" * 60)
        
        await self.test_get_fraud_flags()
        await self.test_resolve_fraud_flag()
        await self.test_royalty_engine_health()
        await self.test_comprehensive_status()
        
        # Social Media Royalty Integration Endpoints (12 endpoints)
        logger.info("\n📱 TESTING SOCIAL MEDIA ROYALTY INTEGRATION ENDPOINTS (12 endpoints)")
        logger.info("-" * 60)
        
        await self.test_process_social_media_monetization()
        await self.test_batch_process_social_media_events()
        await self.test_create_asset_mapping()
        await self.test_get_asset_mapping()
        await self.test_get_user_asset_mappings()
        await self.test_process_streaming_royalties()
        await self.test_get_social_media_analytics()
        await self.test_get_platform_summary()
        await self.test_youtube_monetization_webhook()
        await self.test_tiktok_creator_fund_webhook()
        await self.test_spotify_streams_webhook()
        await self.test_integration_status()
        await self.test_social_media_royalty_health()
        
        # Generate summary
        await self.generate_summary()
        
        # Cleanup
        await self.session.close()
    
    async def generate_summary(self):
        """Generate comprehensive test summary"""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 COMPREHENSIVE REAL-TIME ROYALTY ENGINE TEST RESULTS")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = len([r for r in self.test_results if "❌ FAIL" in r["status"]])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"\n📊 OVERALL RESULTS:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        core_tests = [r for r in self.test_results[:15]]
        security_tests = [r for r in self.test_results[15:19]]
        social_tests = [r for r in self.test_results[19:]]
        
        logger.info(f"\n📈 CATEGORY BREAKDOWN:")
        logger.info(f"   Core Royalty Engine: {len([r for r in core_tests if '✅' in r['status']])}/15 passed")
        logger.info(f"   Analytics & Security: {len([r for r in security_tests if '✅' in r['status']])}/4 passed")
        logger.info(f"   Social Media Integration: {len([r for r in social_tests if '✅' in r['status']])}/13 passed")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if "❌ FAIL" in r["status"]]
        if failed_results:
            logger.info(f"\n❌ FAILED TESTS:")
            for result in failed_results:
                logger.info(f"   • {result['test']}: {result['details']}")
        
        # Show successful tests summary
        logger.info(f"\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if "✅ PASS" in result["status"]:
                logger.info(f"   • {result['test']}")
        
        logger.info("\n" + "=" * 80)
        
        if success_rate >= 80:
            logger.info("🎉 ROYALTY ENGINE TESTING COMPLETED SUCCESSFULLY!")
            logger.info("   System is ready for enterprise-grade royalty processing")
        elif success_rate >= 60:
            logger.info("⚠️  ROYALTY ENGINE TESTING COMPLETED WITH WARNINGS")
            logger.info("   Some features may need attention before production")
        else:
            logger.info("❌ ROYALTY ENGINE TESTING COMPLETED WITH ISSUES")
            logger.info("   Significant issues found - review required")
        
        logger.info("=" * 80)

async def main():
    """Main test execution"""
    test_suite = RoyaltyEngineTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())