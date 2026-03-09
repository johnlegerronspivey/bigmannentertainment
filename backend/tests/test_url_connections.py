"""
Test URL-based Social Media Connections
- Tests for URL-supported endpoint
- Tests for URL detection endpoint
- Tests for URL connect endpoint (single and bulk)
- Tests for connections endpoint with URL-related fields
- Tests for dashboard metrics with source_method field
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestURLConnections:
    """Test suite for URL-based social media connections"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get authentication token before tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token") or data.get("token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            pytest.skip("Authentication failed")
    
    # ──────────────────────────────────────────────────────────────
    # GET /api/social/url-supported - List platforms with URL adapters
    # ──────────────────────────────────────────────────────────────
    
    def test_url_supported_returns_platforms(self):
        """GET /api/social/url-supported returns list of platforms with URL adapters"""
        response = requests.get(f"{BASE_URL}/api/social/url-supported", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "platforms" in data
        assert "count" in data
        assert "url_examples" in data
        assert data["count"] == 13, f"Expected 13 URL-supported platforms, got {data['count']}"
        
        # Verify url_examples is a dict with platform examples
        assert isinstance(data["url_examples"], dict)
        print(f"URL-supported platforms: {data['platforms']}")
        print(f"Count: {data['count']}")
    
    def test_url_supported_includes_expected_platforms(self):
        """GET /api/social/url-supported includes all expected platforms"""
        response = requests.get(f"{BASE_URL}/api/social/url-supported", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        expected_platforms = [
            "youtube", "twitter", "reddit", "tiktok", "instagram",
            "twitch", "soundcloud", "spotify", "facebook", "linkedin",
            "pinterest", "threads", "vimeo"
        ]
        
        for platform in expected_platforms:
            assert platform in data["platforms"], f"Expected {platform} in URL-supported platforms"
    
    def test_url_supported_has_url_examples(self):
        """GET /api/social/url-supported includes url_examples dict"""
        response = requests.get(f"{BASE_URL}/api/social/url-supported", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "url_examples" in data
        examples = data["url_examples"]
        
        # Verify some key platform examples
        assert "youtube" in examples
        assert "youtube.com" in examples["youtube"].lower()
        
        assert "twitter" in examples
        assert "x.com" in examples["twitter"].lower()
        
        assert "tiktok" in examples
        assert "tiktok.com" in examples["tiktok"].lower()
        
        print(f"URL examples: {examples}")
    
    # ──────────────────────────────────────────────────────────────
    # POST /api/social/url-detect - Auto-detect platform from URL
    # ──────────────────────────────────────────────────────────────
    
    def test_url_detect_youtube(self):
        """POST /api/social/url-detect detects YouTube from URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://youtube.com/@MrBeast"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["platform_id"] == "youtube"
        assert data["username"] == "MrBeast"
        assert "platform_name" in data
        print(f"YouTube detection: {data}")
    
    def test_url_detect_twitter_x(self):
        """POST /api/social/url-detect detects Twitter/X from URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://x.com/elonmusk"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["platform_id"] == "twitter"
        assert data["username"] == "elonmusk"
        print(f"Twitter/X detection: {data}")
    
    def test_url_detect_reddit(self):
        """POST /api/social/url-detect detects Reddit from URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://reddit.com/user/spez"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["platform_id"] == "reddit"
        assert data["username"] == "spez"
        print(f"Reddit detection: {data}")
    
    def test_url_detect_tiktok(self):
        """POST /api/social/url-detect detects TikTok from URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://tiktok.com/@khaby.lame"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["platform_id"] == "tiktok"
        assert data["username"] == "khaby.lame"
        assert data.get("has_live_metrics") == True
        print(f"TikTok detection: {data}")
    
    def test_url_detect_instagram(self):
        """POST /api/social/url-detect detects Instagram from URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://instagram.com/cristiano"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["platform_id"] == "instagram"
        assert data["username"] == "cristiano"
        print(f"Instagram detection: {data}")
    
    def test_url_detect_invalid_url_returns_400(self):
        """POST /api/social/url-detect returns 400 for invalid URLs"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://unknownplatform.com/someuser"},
            headers=self.headers)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"Invalid URL response: {data}")
    
    def test_url_detect_empty_url_returns_400(self):
        """POST /api/social/url-detect returns 400 for empty URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": ""},
            headers=self.headers)
        assert response.status_code == 400
    
    # ──────────────────────────────────────────────────────────────
    # POST /api/social/connect-url - Connect platform using URL
    # ──────────────────────────────────────────────────────────────
    
    def test_connect_url_tiktok(self):
        """POST /api/social/connect-url connects TikTok using profile URL"""
        response = requests.post(f"{BASE_URL}/api/social/connect-url", 
            json={
                "profile_url": "https://www.tiktok.com/@khaby.lame",
                "platform_id": "tiktok"
            },
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["platform_id"] == "tiktok"
        assert data["connection_method"] == "url"
        assert "username" in data
        
        # TikTok should return initial_metrics with followers
        if data.get("metrics_available"):
            assert "initial_metrics" in data
            assert "followers" in data["initial_metrics"]
            print(f"TikTok initial metrics: {data['initial_metrics']}")
        
        print(f"TikTok URL connect: {data}")
    
    def test_connect_url_auto_detects_platform(self):
        """POST /api/social/connect-url auto-detects platform when not provided"""
        response = requests.post(f"{BASE_URL}/api/social/connect-url", 
            json={"profile_url": "https://www.youtube.com/@MrBeast"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["platform_id"] == "youtube"
        assert data["connection_method"] == "url"
        print(f"Auto-detected platform: {data}")
    
    def test_connect_url_returns_initial_metrics(self):
        """POST /api/social/connect-url returns initial_metrics when available"""
        response = requests.post(f"{BASE_URL}/api/social/connect-url", 
            json={"profile_url": "https://www.tiktok.com/@khaby.lame"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "metrics_available" in data
        # Note: metrics_available may be True or False depending on if scraping succeeded
        if data.get("metrics_available"):
            assert "initial_metrics" in data
            assert isinstance(data["initial_metrics"], dict)
            print(f"Initial metrics received: {data['initial_metrics']}")
        else:
            print("No initial metrics available (scraping may have failed)")
    
    def test_connect_url_saves_credentials_with_profile_url(self):
        """POST /api/social/connect-url saves credentials with profile_url field"""
        # Connect reddit via URL
        response = requests.post(f"{BASE_URL}/api/social/connect-url", 
            json={"profile_url": "https://reddit.com/user/testuser123"},
            headers=self.headers)
        assert response.status_code == 200
        
        # Verify connection shows profile_url in connections list
        conn_response = requests.get(f"{BASE_URL}/api/social/connections", headers=self.headers)
        assert conn_response.status_code == 200
        data = conn_response.json()
        
        reddit_conn = next((c for c in data["connections"] if c["platform_id"] == "reddit"), None)
        assert reddit_conn is not None
        assert reddit_conn["connected"] == True
        assert reddit_conn["connection_method"] == "url"
        assert "reddit.com" in reddit_conn.get("profile_url", "").lower()
        print(f"Reddit connection: {reddit_conn}")
    
    # ──────────────────────────────────────────────────────────────
    # POST /api/social/connect-url/bulk - Bulk connect URLs
    # ──────────────────────────────────────────────────────────────
    
    def test_bulk_connect_urls(self):
        """POST /api/social/connect-url/bulk connects multiple URLs at once"""
        response = requests.post(f"{BASE_URL}/api/social/connect-url/bulk", 
            json={
                "urls": [
                    "https://www.youtube.com/@MKBHD",
                    "https://x.com/MKBHD",
                    "https://www.instagram.com/mkbhd"
                ]
            },
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "results" in data
        assert "connected_count" in data
        
        # At least some should succeed
        assert data["connected_count"] >= 1
        
        for result in data["results"]:
            assert "url" in result
            assert "success" in result
            if result["success"]:
                assert "platform_id" in result
                assert "platform_name" in result
        
        print(f"Bulk connect results: {data}")
    
    def test_bulk_connect_handles_invalid_urls(self):
        """POST /api/social/connect-url/bulk handles invalid URLs gracefully"""
        response = requests.post(f"{BASE_URL}/api/social/connect-url/bulk", 
            json={
                "urls": [
                    "https://www.youtube.com/@TestChannel",
                    "https://invalid-platform.com/user123",
                    "https://www.tiktok.com/@testuser"
                ]
            },
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should still return results, some may fail
        assert "results" in data
        
        # Check that invalid URL has error
        invalid_result = next((r for r in data["results"] if "invalid-platform" in r["url"]), None)
        if invalid_result:
            assert invalid_result["success"] == False
            assert "error" in invalid_result
        
        print(f"Bulk connect with invalid: {data}")
    
    # ──────────────────────────────────────────────────────────────
    # GET /api/social/connections - Connection fields for URL mode
    # ──────────────────────────────────────────────────────────────
    
    def test_connections_includes_url_fields(self):
        """GET /api/social/connections includes has_url_connect, connection_method, profile_url, url_example"""
        response = requests.get(f"{BASE_URL}/api/social/connections", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "connections" in data
        assert len(data["connections"]) > 0
        
        for conn in data["connections"]:
            assert "has_url_connect" in conn, f"Missing has_url_connect for {conn['platform_id']}"
            assert "url_example" in conn, f"Missing url_example for {conn['platform_id']}"
            
            if conn["connected"]:
                assert "connection_method" in conn, f"Missing connection_method for {conn['platform_id']}"
                # profile_url may be empty string if connected via API
                assert "profile_url" in conn, f"Missing profile_url for {conn['platform_id']}"
        
        print(f"Verified {len(data['connections'])} connections have URL fields")
    
    def test_connections_url_connected_platforms_have_via_url(self):
        """Platforms connected via URL show connection_method='url' and have profile_url"""
        # First connect TikTok via URL
        requests.post(f"{BASE_URL}/api/social/connect-url", 
            json={"profile_url": "https://www.tiktok.com/@khaby.lame"},
            headers=self.headers)
        
        response = requests.get(f"{BASE_URL}/api/social/connections", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        tiktok = next((c for c in data["connections"] if c["platform_id"] == "tiktok"), None)
        assert tiktok is not None
        assert tiktok["connected"] == True
        assert tiktok["connection_method"] == "url"
        assert "tiktok.com" in tiktok["profile_url"].lower()
        assert tiktok["has_url_connect"] == True
        
        print(f"TikTok connection: {tiktok}")
    
    # ──────────────────────────────────────────────────────────────
    # GET /api/social/metrics/dashboard - URL source_method field
    # ──────────────────────────────────────────────────────────────
    
    def test_dashboard_metrics_includes_source_method(self):
        """GET /api/social/metrics/dashboard platforms show source_method for URL connections"""
        # First ensure TikTok is connected via URL
        requests.post(f"{BASE_URL}/api/social/connect-url", 
            json={"profile_url": "https://www.tiktok.com/@khaby.lame"},
            headers=self.headers)
        
        response = requests.get(f"{BASE_URL}/api/social/metrics/dashboard", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "platforms" in data
        
        # Find TikTok in platforms
        tiktok = next((p for p in data["platforms"] if p["platform"] == "tiktok"), None)
        if tiktok:
            assert "data_source" in tiktok
            # If URL fetch succeeded, should be "live" with source_method "url"
            if tiktok.get("data_source") == "live":
                assert "source_method" in tiktok
                assert tiktok["source_method"] == "url"
                print(f"TikTok shows live data via URL: {tiktok}")
            else:
                print(f"TikTok shows simulated (URL fetch may have failed): {tiktok}")
        else:
            print("TikTok not found in dashboard platforms")
    
    def test_dashboard_live_count_includes_url_connections(self):
        """Dashboard live_count includes URL-connected platforms with real data"""
        response = requests.get(f"{BASE_URL}/api/social/metrics/dashboard", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "live_count" in data
        assert "simulated_count" in data
        assert "connected_count" in data
        
        # live_count + simulated_count should equal connected_count
        assert data["live_count"] + data["simulated_count"] == data["connected_count"]
        
        print(f"Live: {data['live_count']}, Simulated: {data['simulated_count']}, Total: {data['connected_count']}")


class TestURLDetectionPatterns:
    """Test URL detection patterns for various platform URL formats"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get authentication token before tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token") or data.get("token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            pytest.skip("Authentication failed")
    
    def test_twitter_old_domain(self):
        """Detects Twitter from twitter.com domain"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://twitter.com/jack"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "twitter"
    
    def test_twitter_with_at_symbol(self):
        """Detects Twitter from URL with @ symbol"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://x.com/@elonmusk"},
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "twitter"
        # Username should be extracted without @
        assert data["username"] in ["elonmusk", "@elonmusk"]
    
    def test_youtube_channel_format(self):
        """Detects YouTube from /channel/ URL format"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://www.youtube.com/channel/UC-lHJZR3Gqxm24_Vd_AJ5Yw"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "youtube"
    
    def test_youtube_user_format(self):
        """Detects YouTube from /user/ URL format"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://www.youtube.com/user/PewDiePie"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "youtube"
    
    def test_reddit_u_format(self):
        """Detects Reddit from /u/ URL format"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://www.reddit.com/u/spez"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "reddit"
    
    def test_spotify_artist_format(self):
        """Detects Spotify from artist URL format"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://open.spotify.com/artist/4gzpq5DPGxSnKTe4SA8HAU"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "spotify"
    
    def test_linkedin_in_format(self):
        """Detects LinkedIn from /in/ URL format"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://www.linkedin.com/in/satyanadella"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "linkedin"
    
    def test_linkedin_company_format(self):
        """Detects LinkedIn from /company/ URL format"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://www.linkedin.com/company/microsoft"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "linkedin"
    
    def test_twitch_format(self):
        """Detects Twitch from twitch.tv URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://www.twitch.tv/ninja"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "twitch"
    
    def test_threads_format(self):
        """Detects Threads from threads.net URL"""
        response = requests.post(f"{BASE_URL}/api/social/url-detect", 
            json={"profile_url": "https://www.threads.net/@zuck"},
            headers=self.headers)
        assert response.status_code == 200
        assert response.json()["platform_id"] == "threads"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
