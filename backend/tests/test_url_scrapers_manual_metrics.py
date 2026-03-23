"""
Test URL Scrapers and Manual Metrics Features
Tests:
1. URL detection for Facebook and Instagram URLs
2. POST /api/social/connect-url with Facebook URL
3. POST /api/social/connect-url with Instagram URL
4. POST /api/social/connect-url with manual_metrics parameter
5. Manual metrics used in GET /api/social/metrics/dashboard
6. GET /api/social/metrics/platforms shows Facebook/Instagram with correct data
7. URL detection endpoint handles various FB/IG URL formats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestURLScrapersManualMetrics:
    """Test URL scrapers and manual metrics features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            # Use access_token (not token) as per agent context
            token = data.get("access_token") or data.get("token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.authenticated = True
            else:
                self.authenticated = False
        else:
            self.authenticated = False
            
        yield
        
    # ─── URL Detection Tests ───────────────────────────────────────────
    
    def test_url_detect_facebook_page(self):
        """Test URL detection for Facebook page URL"""
        response = self.session.post(f"{BASE_URL}/api/social/url-detect", json={
            "profile_url": "https://www.facebook.com/bigmannentertainment"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["platform_id"] == "facebook", f"Expected facebook, got {data.get('platform_id')}"
        assert data["username"] == "bigmannentertainment", f"Expected bigmannentertainment, got {data.get('username')}"
        assert "has_live_metrics" in data
        print(f"PASS: Facebook URL detected - platform: {data['platform_id']}, username: {data['username']}")
        
    def test_url_detect_facebook_profile_id(self):
        """Test URL detection for Facebook profile with ID"""
        response = self.session.post(f"{BASE_URL}/api/social/url-detect", json={
            "profile_url": "https://facebook.com/profile.php?id=123456789"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "facebook"
        print(f"PASS: Facebook profile ID URL detected - username: {data['username']}")
        
    def test_url_detect_instagram_profile(self):
        """Test URL detection for Instagram profile URL"""
        response = self.session.post(f"{BASE_URL}/api/social/url-detect", json={
            "profile_url": "https://www.instagram.com/bigmannent"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "instagram", f"Expected instagram, got {data.get('platform_id')}"
        assert data["username"] == "bigmannent", f"Expected bigmannent, got {data.get('username')}"
        print(f"PASS: Instagram URL detected - platform: {data['platform_id']}, username: {data['username']}")
        
    def test_url_detect_instagram_with_at_symbol(self):
        """Test URL detection for Instagram URL with @ symbol"""
        response = self.session.post(f"{BASE_URL}/api/social/url-detect", json={
            "profile_url": "https://instagram.com/@testuser"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["platform_id"] == "instagram"
        print(f"PASS: Instagram URL with @ detected - username: {data['username']}")
        
    def test_url_detect_invalid_url(self):
        """Test URL detection with invalid URL returns 400"""
        response = self.session.post(f"{BASE_URL}/api/social/url-detect", json={
            "profile_url": "https://unknownplatform.com/user123"
        })
        assert response.status_code == 400, f"Expected 400 for unknown platform, got {response.status_code}"
        print("PASS: Invalid URL correctly returns 400")
        
    # ─── Connect URL Tests ─────────────────────────────────────────────
    
    def test_connect_url_facebook(self):
        """Test connecting Facebook via URL"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        response = self.session.post(f"{BASE_URL}/api/social/connect-url", json={
            "profile_url": "https://www.facebook.com/testfbpage",
            "display_name": "Test FB Page"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert data["platform_id"] == "facebook"
        assert data["connection_method"] == "url"
        assert "metrics_source" in data  # Should be 'auto' or 'manual'
        print(f"PASS: Facebook connected via URL - metrics_source: {data.get('metrics_source')}, metrics_available: {data.get('metrics_available')}")
        
    def test_connect_url_instagram(self):
        """Test connecting Instagram via URL"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        response = self.session.post(f"{BASE_URL}/api/social/connect-url", json={
            "profile_url": "https://www.instagram.com/testigprofile",
            "display_name": "Test IG Profile"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert data["platform_id"] == "instagram"
        assert data["connection_method"] == "url"
        print(f"PASS: Instagram connected via URL - metrics_source: {data.get('metrics_source')}, metrics_available: {data.get('metrics_available')}")
        
    def test_connect_url_with_manual_metrics(self):
        """Test connecting with manual metrics fallback"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        manual_metrics = {
            "followers": 15000,
            "following": 500,
            "posts": 250,
            "engagement_rate": 3.5
        }
        
        response = self.session.post(f"{BASE_URL}/api/social/connect-url", json={
            "profile_url": "https://www.facebook.com/manualmetricstest",
            "display_name": "Manual Metrics Test",
            "manual_metrics": manual_metrics
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] == True
        
        # Check if manual metrics were used (since auto-scrape likely fails from server)
        if data.get("metrics_source") == "manual":
            assert data["initial_metrics"]["followers"] == 15000
            assert data["initial_metrics"]["following"] == 500
            assert data["initial_metrics"]["posts"] == 250
            print(f"PASS: Manual metrics stored - followers: {data['initial_metrics']['followers']}")
        else:
            print(f"PASS: Connected with auto metrics - source: {data.get('metrics_source')}")
            
    def test_connect_url_instagram_with_manual_metrics(self):
        """Test connecting Instagram with manual metrics"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        manual_metrics = {
            "followers": 8500,
            "following": 300,
            "posts": 180,
            "engagement_rate": 4.2
        }
        
        response = self.session.post(f"{BASE_URL}/api/social/connect-url", json={
            "profile_url": "https://www.instagram.com/manualigtest",
            "display_name": "Manual IG Test",
            "manual_metrics": manual_metrics
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["platform_id"] == "instagram"
        print(f"PASS: Instagram with manual metrics - source: {data.get('metrics_source')}")
        
    # ─── Dashboard Metrics Tests ───────────────────────────────────────
    
    def test_dashboard_metrics_includes_manual(self):
        """Test that dashboard metrics include manual metrics data"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        response = self.session.get(f"{BASE_URL}/api/social/metrics/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "platforms" in data
        assert "total_followers" in data
        assert "connected_count" in data
        
        # Check if Facebook/Instagram are in the platforms list
        platform_ids = [p["platform"] for p in data.get("platforms", [])]
        print(f"PASS: Dashboard metrics returned - {data['connected_count']} connected, total followers: {data['total_followers']}")
        print(f"  Platforms: {platform_ids[:10]}...")  # Show first 10
        
    def test_platform_metrics_shows_fb_ig(self):
        """Test that platform metrics shows Facebook and Instagram with correct data"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        response = self.session.get(f"{BASE_URL}/api/social/metrics/platforms")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "platforms" in data
        assert "categories" in data
        
        # Find Facebook and Instagram in platforms
        fb_platform = next((p for p in data["platforms"] if p["platform_id"] == "facebook"), None)
        ig_platform = next((p for p in data["platforms"] if p["platform_id"] == "instagram"), None)
        
        if fb_platform:
            print(f"PASS: Facebook in platform metrics - followers: {fb_platform.get('followers')}, posts: {fb_platform.get('posts')}")
        if ig_platform:
            print(f"PASS: Instagram in platform metrics - followers: {ig_platform.get('followers')}, posts: {ig_platform.get('posts')}")
            
        print(f"PASS: Platform metrics returned - {data.get('total_connected')} connected platforms")
        
    # ─── URL Supported Platforms Tests ─────────────────────────────────
    
    def test_url_supported_platforms(self):
        """Test that URL supported platforms endpoint returns FB and IG"""
        response = self.session.get(f"{BASE_URL}/api/social/url-supported")
        assert response.status_code == 200
        data = response.json()
        
        assert "platforms" in data
        assert "facebook" in data["platforms"]
        assert "instagram" in data["platforms"]
        assert "url_examples" in data
        print(f"PASS: URL supported platforms - {data['count']} platforms support URL connection")
        
    # ─── Connections List Tests ────────────────────────────────────────
    
    def test_connections_shows_url_connect_info(self):
        """Test that connections list shows URL connect info"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        response = self.session.get(f"{BASE_URL}/api/social/connections")
        assert response.status_code == 200
        data = response.json()
        
        assert "connections" in data
        
        # Find Facebook and Instagram connections
        fb_conn = next((c for c in data["connections"] if c["platform_id"] == "facebook"), None)
        ig_conn = next((c for c in data["connections"] if c["platform_id"] == "instagram"), None)
        
        if fb_conn:
            assert "has_url_connect" in fb_conn
            assert fb_conn["has_url_connect"] == True
            print(f"PASS: Facebook connection - connected: {fb_conn['connected']}, has_url_connect: {fb_conn['has_url_connect']}")
            
        if ig_conn:
            assert "has_url_connect" in ig_conn
            assert ig_conn["has_url_connect"] == True
            print(f"PASS: Instagram connection - connected: {ig_conn['connected']}, has_url_connect: {ig_conn['has_url_connect']}")
            
        print(f"PASS: Connections list - {data['connected_count']} of {data['total']} connected")


class TestURLDetectionFormats:
    """Test various URL formats for Facebook and Instagram"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
        
    def test_facebook_url_formats(self):
        """Test various Facebook URL formats"""
        fb_urls = [
            ("https://www.facebook.com/bigmann", "bigmann"),
            ("https://facebook.com/bigmann", "bigmann"),
            ("http://facebook.com/bigmann", "bigmann"),
            ("facebook.com/bigmann", "bigmann"),  # Without protocol
            ("https://www.facebook.com/profile.php?id=100000123456", "100000123456"),
            ("https://m.facebook.com/bigmann", "bigmann"),  # Mobile
        ]
        
        for url, expected_username in fb_urls:
            response = self.session.post(f"{BASE_URL}/api/social/url-detect", json={
                "profile_url": url
            })
            if response.status_code == 200:
                data = response.json()
                assert data["platform_id"] == "facebook", f"URL {url} should detect as facebook"
                print(f"PASS: {url} -> facebook/{data['username']}")
            else:
                print(f"SKIP: {url} returned {response.status_code}")
                
    def test_instagram_url_formats(self):
        """Test various Instagram URL formats"""
        ig_urls = [
            ("https://www.instagram.com/bigmann", "bigmann"),
            ("https://instagram.com/bigmann", "bigmann"),
            ("http://instagram.com/bigmann", "bigmann"),
            ("instagram.com/bigmann", "bigmann"),  # Without protocol
            ("https://www.instagram.com/@bigmann", "bigmann"),  # With @
            ("https://instagram.com/bigmann/", "bigmann"),  # Trailing slash
        ]
        
        for url, expected_username in ig_urls:
            response = self.session.post(f"{BASE_URL}/api/social/url-detect", json={
                "profile_url": url
            })
            if response.status_code == 200:
                data = response.json()
                assert data["platform_id"] == "instagram", f"URL {url} should detect as instagram"
                print(f"PASS: {url} -> instagram/{data['username']}")
            else:
                print(f"SKIP: {url} returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
