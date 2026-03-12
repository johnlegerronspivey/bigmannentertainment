"""
Tests for API Credentials Reference Guide and Platform Credentials Manager
Tests the /api/distribution-hub/adapters/credentials-guide endpoint and platform connection endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Expected 10 live adapter platforms
EXPECTED_PLATFORMS = [
    'youtube', 'twitter_x', 'tiktok', 'soundcloud', 'vimeo',
    'bluesky', 'discord', 'telegram', 'instagram', 'facebook'
]

# Required fields for each adapter in the guide
REQUIRED_ADAPTER_FIELDS = [
    'platform_id', 'platform_name', 'fields', 'developer_portal',
    'developer_portal_label', 'setup_summary', 'cost'
]

# Expected credential fields per platform
EXPECTED_CREDENTIALS = {
    'youtube': ['access_token'],
    'twitter_x': ['bearer_token'],
    'tiktok': ['access_token'],
    'soundcloud': ['access_token'],
    'vimeo': ['access_token'],
    'bluesky': ['handle', 'app_password'],
    'discord': ['webhook_url'],
    'telegram': ['bot_token', 'chat_id'],
    'instagram': ['access_token', 'page_id'],
    'facebook': ['access_token', 'page_id'],
}


class TestCredentialsGuideEndpoint:
    """Tests for GET /api/distribution-hub/adapters/credentials-guide"""

    def test_credentials_guide_returns_200(self):
        """Test endpoint returns 200 status without authentication"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Credentials guide endpoint returns 200")

    def test_credentials_guide_returns_10_platforms(self):
        """Test endpoint returns exactly 10 platform adapters"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        data = response.json()
        assert 'adapters' in data, "Response should have 'adapters' key"
        assert 'total' in data, "Response should have 'total' key"
        assert data['total'] == 10, f"Expected 10 adapters, got {data['total']}"
        print(f"✓ Credentials guide returns 10 platforms")

    def test_all_expected_platforms_present(self):
        """Test all 10 expected platforms are in the response"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        adapters = response.json().get('adapters', {})
        for platform_id in EXPECTED_PLATFORMS:
            assert platform_id in adapters, f"Missing platform: {platform_id}"
        print(f"✓ All 10 expected platforms present: {', '.join(EXPECTED_PLATFORMS)}")

    def test_each_adapter_has_required_fields(self):
        """Test each adapter has all required fields"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        adapters = response.json().get('adapters', {})
        for platform_id, adapter in adapters.items():
            for field in REQUIRED_ADAPTER_FIELDS:
                assert field in adapter, f"{platform_id} missing field: {field}"
        print(f"✓ All adapters have required fields: {', '.join(REQUIRED_ADAPTER_FIELDS)}")

    def test_each_adapter_has_correct_credential_fields(self):
        """Test each adapter has the correct credential fields"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        adapters = response.json().get('adapters', {})
        for platform_id, expected_creds in EXPECTED_CREDENTIALS.items():
            adapter = adapters.get(platform_id, {})
            fields = adapter.get('fields', [])
            field_keys = [f['key'] for f in fields]
            for cred in expected_creds:
                assert cred in field_keys, f"{platform_id} missing credential field: {cred}"
            print(f"  ✓ {platform_id}: {', '.join(field_keys)}")

    def test_credential_fields_have_required_properties(self):
        """Test each credential field has label, placeholder, type, help"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        adapters = response.json().get('adapters', {})
        for platform_id, adapter in adapters.items():
            for field in adapter.get('fields', []):
                assert 'key' in field, f"{platform_id} field missing 'key'"
                assert 'label' in field, f"{platform_id} field missing 'label'"
                assert 'placeholder' in field, f"{platform_id} field missing 'placeholder'"
                assert 'type' in field, f"{platform_id} field missing 'type'"
                assert 'help' in field, f"{platform_id} field missing 'help'"
        print(f"✓ All credential fields have required properties (key, label, placeholder, type, help)")

    def test_developer_portals_are_valid_urls(self):
        """Test developer portal URLs are valid HTTP(S) URLs"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        adapters = response.json().get('adapters', {})
        for platform_id, adapter in adapters.items():
            url = adapter.get('developer_portal', '')
            assert url.startswith('http://') or url.startswith('https://'), f"{platform_id} has invalid portal URL: {url}"
        print(f"✓ All developer portal URLs are valid")

    def test_telegram_has_bot_token_and_chat_id(self):
        """Test Telegram adapter has bot_token and chat_id fields"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        adapters = response.json().get('adapters', {})
        telegram = adapters.get('telegram', {})
        field_keys = [f['key'] for f in telegram.get('fields', [])]
        assert 'bot_token' in field_keys, "Telegram missing bot_token field"
        assert 'chat_id' in field_keys, "Telegram missing chat_id field"
        print(f"✓ Telegram has bot_token and chat_id fields")

    def test_bluesky_has_handle_and_app_password(self):
        """Test Bluesky adapter has handle and app_password fields"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/adapters/credentials-guide")
        adapters = response.json().get('adapters', {})
        bluesky = adapters.get('bluesky', {})
        field_keys = [f['key'] for f in bluesky.get('fields', [])]
        assert 'handle' in field_keys, "Bluesky missing handle field"
        assert 'app_password' in field_keys, "Bluesky missing app_password field"
        print(f"✓ Bluesky has handle and app_password fields")


class TestPlatformConnectionsAuth:
    """Tests for platform connection endpoints that require authentication"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for authenticated tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        pytest.skip(f"Auth failed: {response.status_code}")

    def test_connect_platform_requires_auth(self):
        """Test platform connection endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/distribution-hub/platforms/connect", json={
            "platform_id": "discord",
            "credentials": {"webhook_url": "https://example.com/webhook"}
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Platform connect endpoint requires authentication")

    def test_get_connected_platforms_requires_auth(self):
        """Test get connected platforms endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/platforms/connected")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Get connected platforms endpoint requires authentication")

    def test_disconnect_platform_requires_auth(self):
        """Test disconnect platform endpoint requires authentication"""
        response = requests.delete(f"{BASE_URL}/api/distribution-hub/platforms/discord/disconnect")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Disconnect platform endpoint requires authentication")

    def test_get_connected_platforms_with_auth(self, auth_token):
        """Test get connected platforms returns list with auth"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/platforms/connected",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'connected_platforms' in data, "Response should have 'connected_platforms' key"
        assert 'total' in data, "Response should have 'total' key"
        print(f"✓ Get connected platforms works with auth, found {data['total']} connected")

    def test_connect_and_disconnect_platform(self, auth_token):
        """Test connecting and disconnecting a test platform"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Connect Discord with test webhook
        connect_response = requests.post(
            f"{BASE_URL}/api/distribution-hub/platforms/connect",
            headers=headers,
            json={
                "platform_id": "discord",
                "credentials": {"webhook_url": "https://discord.com/api/webhooks/test/test123"}
            }
        )
        assert connect_response.status_code == 200, f"Connect failed: {connect_response.status_code} - {connect_response.text}"
        print(f"✓ Connected Discord platform")

        # Verify it's in connected list
        list_response = requests.get(
            f"{BASE_URL}/api/distribution-hub/platforms/connected",
            headers=headers
        )
        connected = list_response.json().get('connected_platforms', [])
        discord_connected = any(p['platform_id'] == 'discord' for p in connected)
        assert discord_connected, "Discord should be in connected list"
        print(f"✓ Discord appears in connected platforms list")

        # Disconnect Discord
        disconnect_response = requests.delete(
            f"{BASE_URL}/api/distribution-hub/platforms/discord/disconnect",
            headers=headers
        )
        assert disconnect_response.status_code == 200, f"Disconnect failed: {disconnect_response.status_code}"
        print(f"✓ Disconnected Discord platform")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
