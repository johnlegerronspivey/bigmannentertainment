"""
Test AWS Live Streaming APIs (IVS + MediaPackage)
Phase B integration testing for AWS Interactive Video Service and MediaPackage
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

class TestAWSLiveStreamingAPIs:
    """Tests for AWS IVS and MediaPackage integration endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup auth token before each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login to get token
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        data = login_resp.json()
        # Note: API returns 'access_token' not 'token'
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.token = token
    
    # ========== STATUS ENDPOINT ==========
    def test_livestream_status(self):
        """GET /api/aws-livestream/status - should return IVS and MediaPackage status"""
        resp = self.session.get(f"{BASE_URL}/api/aws-livestream/status")
        assert resp.status_code == 200, f"Status request failed: {resp.text}"
        data = resp.json()
        
        # Verify IVS status
        assert "ivs" in data, "Response missing 'ivs' key"
        assert data["ivs"]["available"] == True, "IVS should be available"
        assert "region" in data["ivs"], "IVS status missing region"
        
        # Verify MediaPackage status
        assert "mediapackage" in data, "Response missing 'mediapackage' key"
        assert data["mediapackage"]["available"] == True, "MediaPackage should be available"
        assert "region" in data["mediapackage"], "MediaPackage status missing region"
        
        print(f"Status: IVS available={data['ivs']['available']}, MediaPackage available={data['mediapackage']['available']}")
    
    # ========== IVS CHANNELS ==========
    def test_list_ivs_channels_empty(self):
        """GET /api/aws-livestream/ivs/channels - should return list of IVS channels"""
        resp = self.session.get(f"{BASE_URL}/api/aws-livestream/ivs/channels")
        assert resp.status_code == 200, f"List IVS channels failed: {resp.text}"
        data = resp.json()
        
        assert "channels" in data, "Response missing 'channels' key"
        assert "total" in data, "Response missing 'total' key"
        assert isinstance(data["channels"], list), "Channels should be a list"
        print(f"IVS channels: {data['total']} total")
    
    def test_create_and_delete_ivs_channel(self):
        """POST /api/aws-livestream/ivs/channels - create IVS channel and verify, then delete"""
        # Create channel
        channel_name = f"TEST_channel_{int(time.time())}"
        create_resp = self.session.post(f"{BASE_URL}/api/aws-livestream/ivs/channels", json={
            "name": channel_name,
            "channel_type": "STANDARD",
            "latency_mode": "LOW"
        })
        assert create_resp.status_code == 200, f"Create IVS channel failed: {create_resp.text}"
        data = create_resp.json()
        
        # Verify response structure
        assert "channel_arn" in data, "Response missing 'channel_arn'"
        assert "channel_name" in data, "Response missing 'channel_name'"
        assert data["channel_name"] == channel_name, "Channel name mismatch"
        assert "playback_url" in data, "Response missing 'playback_url'"
        assert "stream_key_value" in data, "Response missing 'stream_key_value'"
        assert "ingest_endpoint" in data, "Response missing 'ingest_endpoint'"
        
        channel_arn = data["channel_arn"]
        print(f"Created IVS channel: {channel_name}, ARN: {channel_arn[:50]}...")
        
        # Clean up - delete the channel
        delete_resp = self.session.delete(f"{BASE_URL}/api/aws-livestream/ivs/channels/{requests.utils.quote(channel_arn, safe='')}")
        assert delete_resp.status_code == 200, f"Delete IVS channel failed: {delete_resp.text}"
        delete_data = delete_resp.json()
        assert delete_data.get("deleted") == True, "Delete should return deleted=True"
        print(f"Deleted IVS channel: {channel_name}")
    
    # ========== MEDIAPACKAGE FORMATS ==========
    def test_mediapackage_formats(self):
        """GET /api/aws-livestream/mediapackage/formats - should return 4 packaging formats"""
        resp = self.session.get(f"{BASE_URL}/api/aws-livestream/mediapackage/formats")
        assert resp.status_code == 200, f"Get formats failed: {resp.text}"
        data = resp.json()
        
        assert "formats" in data, "Response missing 'formats' key"
        formats = data["formats"]
        assert len(formats) == 4, f"Expected 4 formats, got {len(formats)}"
        
        # Verify all 4 formats exist
        expected_formats = ["hls", "dash", "mss", "cmaf"]
        for fmt in expected_formats:
            assert fmt in formats, f"Missing format: {fmt}"
            assert "label" in formats[fmt], f"Format {fmt} missing 'label'"
            assert "description" in formats[fmt], f"Format {fmt} missing 'description'"
        
        print(f"MediaPackage formats: {list(formats.keys())}")
    
    # ========== MEDIAPACKAGE CHANNELS ==========
    def test_list_mediapackage_channels(self):
        """GET /api/aws-livestream/mediapackage/channels - should return list of MP channels"""
        resp = self.session.get(f"{BASE_URL}/api/aws-livestream/mediapackage/channels")
        assert resp.status_code == 200, f"List MP channels failed: {resp.text}"
        data = resp.json()
        
        assert "channels" in data, "Response missing 'channels' key"
        assert "total" in data, "Response missing 'total' key"
        assert isinstance(data["channels"], list), "Channels should be a list"
        print(f"MediaPackage channels: {data['total']} total")
    
    def test_create_and_delete_mediapackage_channel(self):
        """POST /api/aws-livestream/mediapackage/channels - create and delete MP channel"""
        # Create channel
        channel_id = f"test-mp-channel-{int(time.time())}"
        create_resp = self.session.post(f"{BASE_URL}/api/aws-livestream/mediapackage/channels", json={
            "channel_id": channel_id,
            "description": "Test MediaPackage channel for automated testing"
        })
        assert create_resp.status_code == 200, f"Create MP channel failed: {create_resp.text}"
        data = create_resp.json()
        
        # Verify response structure
        assert "id" in data, "Response missing 'id'"
        assert data["id"] == channel_id, "Channel ID mismatch"
        assert "arn" in data, "Response missing 'arn'"
        assert "ingest_endpoints" in data, "Response missing 'ingest_endpoints'"
        
        print(f"Created MediaPackage channel: {channel_id}")
        
        # Clean up - delete the channel
        delete_resp = self.session.delete(f"{BASE_URL}/api/aws-livestream/mediapackage/channels/{channel_id}")
        assert delete_resp.status_code == 200, f"Delete MP channel failed: {delete_resp.text}"
        delete_data = delete_resp.json()
        assert delete_data.get("deleted") == True, "Delete should return deleted=True"
        print(f"Deleted MediaPackage channel: {channel_id}")
    
    # ========== IVS STREAMS ==========
    def test_list_ivs_streams(self):
        """GET /api/aws-livestream/ivs/streams - should return streams list"""
        resp = self.session.get(f"{BASE_URL}/api/aws-livestream/ivs/streams")
        assert resp.status_code == 200, f"List IVS streams failed: {resp.text}"
        data = resp.json()
        
        assert "streams" in data, "Response missing 'streams' key"
        assert "total" in data, "Response missing 'total' key"
        assert isinstance(data["streams"], list), "Streams should be a list"
        print(f"IVS streams: {data['total']} active")
    
    # ========== MEDIAPACKAGE ENDPOINTS ==========
    def test_list_mediapackage_endpoints(self):
        """GET /api/aws-livestream/mediapackage/endpoints - should return endpoints list"""
        resp = self.session.get(f"{BASE_URL}/api/aws-livestream/mediapackage/endpoints")
        assert resp.status_code == 200, f"List MP endpoints failed: {resp.text}"
        data = resp.json()
        
        assert "endpoints" in data, "Response missing 'endpoints' key"
        assert "total" in data, "Response missing 'total' key"
        assert isinstance(data["endpoints"], list), "Endpoints should be a list"
        print(f"MediaPackage endpoints: {data['total']} total")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
