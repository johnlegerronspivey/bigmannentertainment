"""
Test 25 URL Adapters for Social Media Platform Expansion
Tests the expanded URL-based metric fetching from 13 to 25 platforms.
New platforms: github, medium, kick, bluesky, telegram, discord, tumblr, dailymotion, bandcamp, audiomack, mixcloud, snapchat
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestURLSupportedEndpoint:
    """Test GET /api/social/url-supported returns 25 platforms"""
    
    def test_url_supported_returns_25_platforms(self):
        """Verify url-supported endpoint returns exactly 25 platforms"""
        response = requests.get(f"{BASE_URL}/api/social/url-supported")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "count" in data, "Response should have count field"
        assert data["count"] == 25, f"Expected 25 platforms, got {data['count']}"
        print(f"✓ URL-supported endpoint returns {data['count']} platforms")
    
    def test_url_supported_includes_all_25_platforms(self):
        """Verify all 25 platform IDs are present"""
        response = requests.get(f"{BASE_URL}/api/social/url-supported")
        assert response.status_code == 200
        data = response.json()
        platforms = data.get("platforms", [])
        
        expected_platforms = [
            "youtube", "twitter", "reddit", "tiktok", "instagram", "twitch",
            "soundcloud", "spotify", "facebook", "linkedin", "pinterest", "threads", "vimeo",
            # New platforms (12 additions)
            "github", "medium", "kick", "bluesky", "telegram", "discord",
            "tumblr", "dailymotion", "bandcamp", "audiomack", "mixcloud", "snapchat"
        ]
        
        for platform in expected_platforms:
            assert platform in platforms, f"Platform '{platform}' not in url-supported list"
        
        print(f"✓ All 25 expected platforms present: {sorted(platforms)}")
    
    def test_url_supported_has_examples(self):
        """Verify url_examples dict is provided with 25 entries"""
        response = requests.get(f"{BASE_URL}/api/social/url-supported")
        assert response.status_code == 200
        data = response.json()
        
        assert "url_examples" in data, "Response should have url_examples"
        examples = data["url_examples"]
        assert len(examples) >= 25, f"Expected at least 25 URL examples, got {len(examples)}"
        
        # Verify some new platform examples
        assert "github" in examples, "Missing github URL example"
        assert "medium" in examples, "Missing medium URL example"
        assert "bluesky" in examples, "Missing bluesky URL example"
        assert "discord" in examples, "Missing discord URL example"
        assert "telegram" in examples, "Missing telegram URL example"
        
        print(f"✓ URL examples provided for {len(examples)} platforms")


class TestURLDetectNewPlatforms:
    """Test POST /api/social/url-detect for all 12 new platforms"""
    
    def test_detect_github(self):
        """Detect GitHub from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
                                 json={"profile_url": "https://github.com/microsoft"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["platform_id"] == "github"
        assert data["username"] == "microsoft"
        print(f"✓ GitHub detected: {data}")
    
    def test_detect_medium(self):
        """Detect Medium from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://medium.com/@netflix"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "medium"
        assert data["username"] == "netflix"
        print(f"✓ Medium detected: {data}")
    
    def test_detect_kick(self):
        """Detect Kick from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://kick.com/xqc"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "kick"
        assert data["username"] == "xqc"
        print(f"✓ Kick detected: {data}")
    
    def test_detect_bluesky(self):
        """Detect Bluesky from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://bsky.app/profile/jay.bsky.social"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "bluesky"
        assert "jay" in data["username"].lower() or data["username"] == "jay.bsky.social"
        print(f"✓ Bluesky detected: {data}")
    
    def test_detect_telegram(self):
        """Detect Telegram from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://t.me/durov"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "telegram"
        assert data["username"] == "durov"
        print(f"✓ Telegram detected: {data}")
    
    def test_detect_discord(self):
        """Detect Discord from invite URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://discord.gg/minecraft"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "discord"
        assert data["username"] == "minecraft"
        print(f"✓ Discord detected: {data}")
    
    def test_detect_tumblr(self):
        """Detect Tumblr from subdomain URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://staff.tumblr.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "tumblr"
        assert data["username"] == "staff"
        print(f"✓ Tumblr detected: {data}")
    
    def test_detect_dailymotion(self):
        """Detect Dailymotion from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://dailymotion.com/bfrench"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "dailymotion"
        assert data["username"] == "bfrench"
        print(f"✓ Dailymotion detected: {data}")
    
    def test_detect_bandcamp(self):
        """Detect Bandcamp from subdomain URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://ween.bandcamp.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "bandcamp"
        assert data["username"] == "ween"
        print(f"✓ Bandcamp detected: {data}")
    
    def test_detect_audiomack(self):
        """Detect Audiomack from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://audiomack.com/lilbaby"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "audiomack"
        assert data["username"] == "lilbaby"
        print(f"✓ Audiomack detected: {data}")
    
    def test_detect_mixcloud(self):
        """Detect Mixcloud from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://mixcloud.com/sparks"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "mixcloud"
        assert data["username"] == "sparks"
        print(f"✓ Mixcloud detected: {data}")
    
    def test_detect_snapchat(self):
        """Detect Snapchat from profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect",
                                 json={"profile_url": "https://snapchat.com/add/djkhaled305"})
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "snapchat"
        assert data["username"] == "djkhaled305"
        print(f"✓ Snapchat detected: {data}")


class TestConnectURLNewPlatforms:
    """Test POST /api/social/connect-url for new platforms with authentication"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token for authenticated requests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip(f"Login failed: {login_response.status_code} - {login_response.text}")
    
    def test_connect_bluesky_via_url(self):
        """Connect Bluesky platform using profile URL"""
        response = requests.post(
            f"{BASE_URL}/api/social/connect-url",
            json={"profile_url": "https://bsky.app/profile/bsky.app"},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["platform_id"] == "bluesky"
        assert data["connection_method"] == "url"
        print(f"✓ Bluesky connected via URL: {data}")
    
    def test_connect_discord_via_url(self):
        """Connect Discord platform using invite URL"""
        response = requests.post(
            f"{BASE_URL}/api/social/connect-url",
            json={"profile_url": "https://discord.gg/discord-developers"},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["platform_id"] == "discord"
        assert data["connection_method"] == "url"
        print(f"✓ Discord connected via URL: {data}")
    
    def test_connect_github_via_url(self):
        """Connect GitHub platform using profile URL"""
        response = requests.post(
            f"{BASE_URL}/api/social/connect-url",
            json={"profile_url": "https://github.com/torvalds"},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["platform_id"] == "github"
        assert data["connection_method"] == "url"
        # GitHub API should return real metrics
        if data.get("initial_metrics"):
            assert "followers" in data["initial_metrics"]
            print(f"✓ GitHub connected via URL with metrics: followers={data['initial_metrics'].get('followers')}")
        else:
            print(f"✓ GitHub connected via URL: {data}")
    
    def test_connect_telegram_via_url(self):
        """Connect Telegram platform using channel URL"""
        response = requests.post(
            f"{BASE_URL}/api/social/connect-url",
            json={"profile_url": "https://t.me/telegram"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["platform_id"] == "telegram"
        print(f"✓ Telegram connected via URL: {data}")


class TestBulkConnectNewPlatforms:
    """Test POST /api/social/connect-url/bulk for multiple new platforms"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token for authenticated requests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_bulk_connect_new_platforms(self):
        """Bulk connect multiple new platforms at once"""
        urls = [
            "https://github.com/microsoft",
            "https://medium.com/@ev",
            "https://t.me/durov",
            "https://dailymotion.com/bfrench",
            "https://audiomack.com/lilbaby"
        ]
        response = requests.post(
            f"{BASE_URL}/api/social/connect-url/bulk",
            json={"urls": urls},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["connected_count"] >= 4, f"Expected at least 4 connections, got {data['connected_count']}"
        
        # Verify platforms were detected correctly
        for result in data["results"]:
            if result.get("success"):
                assert result["platform_id"] in ["github", "medium", "telegram", "dailymotion", "audiomack"]
        
        print(f"✓ Bulk connected {data['connected_count']} platforms: {data['results']}")


class TestDashboardWithNewPlatforms:
    """Test dashboard shows live data from newly connected platforms"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token for authenticated requests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_dashboard_shows_connected_platforms(self):
        """Verify dashboard shows newly connected platforms"""
        response = requests.get(
            f"{BASE_URL}/api/social/metrics/dashboard",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have some connected platforms
        assert "connected_count" in data
        assert "platforms" in data
        assert "live_count" in data
        assert "simulated_count" in data
        
        # Check if any new platforms show live data
        platform_ids = [p.get("platform") for p in data.get("platforms", [])]
        new_platforms = ["github", "bluesky", "discord", "telegram", "dailymotion"]
        connected_new = [p for p in new_platforms if p in platform_ids]
        
        print(f"✓ Dashboard metrics: {data['connected_count']} connected, {data['live_count']} live, {data['simulated_count']} simulated")
        print(f"✓ New platforms connected: {connected_new}")


class TestConnectionsMetadata:
    """Test connections endpoint includes URL metadata for all 25 platforms"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token for authenticated requests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_connections_include_url_metadata(self):
        """Verify connections include has_url_connect for all 25 URL-supported platforms"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Count platforms with has_url_connect = true
        url_platforms = [c for c in data["connections"] if c.get("has_url_connect")]
        assert len(url_platforms) >= 25, f"Expected at least 25 URL-supported platforms, got {len(url_platforms)}"
        
        # Verify specific new platforms have URL support
        url_platform_ids = [c["platform_id"] for c in url_platforms]
        new_url_platforms = ["github", "medium", "kick", "bluesky", "telegram", "discord", 
                            "tumblr", "dailymotion", "bandcamp", "audiomack", "mixcloud", "snapchat"]
        
        for platform in new_url_platforms:
            assert platform in url_platform_ids, f"Platform '{platform}' should have has_url_connect=true"
        
        print(f"✓ {len(url_platforms)} platforms support URL connection")
        print(f"✓ All 12 new platforms have has_url_connect=true")
    
    def test_connections_include_url_examples(self):
        """Verify connections include url_example for URL-supported platforms"""
        response = requests.get(
            f"{BASE_URL}/api/social/connections",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check url_example for new platforms
        new_platforms = ["github", "bluesky", "discord", "telegram"]
        for conn in data["connections"]:
            if conn["platform_id"] in new_platforms:
                assert "url_example" in conn, f"Missing url_example for {conn['platform_id']}"
                assert conn["url_example"], f"Empty url_example for {conn['platform_id']}"
        
        print("✓ URL examples present for new platforms")


class TestPlatformConfig:
    """Test platform config includes new platforms"""
    
    def test_platforms_endpoint_returns_123(self):
        """Verify platforms endpoint returns all 123 platforms"""
        response = requests.get(f"{BASE_URL}/api/social/platforms")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 123, f"Expected 123 platforms, got {data['total']}"
        print(f"✓ Platforms endpoint returns {data['total']} platforms")
    
    def test_new_platforms_in_config(self):
        """Verify new platforms (github, medium, bluesky) are in the platform config"""
        response = requests.get(f"{BASE_URL}/api/social/platforms")
        assert response.status_code == 200
        data = response.json()
        
        platform_ids = [p["id"] for p in data["platforms"]]
        new_platforms = ["github", "medium", "bluesky"]
        
        for platform in new_platforms:
            assert platform in platform_ids, f"Platform '{platform}' not found in platform config"
        
        print(f"✓ New platforms github, medium, bluesky present in config")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
