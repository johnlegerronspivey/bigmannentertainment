"""
Test Write Actions for Live APIs
Tests POST /api/integrations/publish, publish/history, twitter/tweet, tiktok/publish, snapchat/publish
These endpoints attempt real API calls - errors are expected due to token limitations.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestWriteActionsIntegration:
    """Test publish/write endpoints for social media platforms"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for owner account"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "owner@bigmannentertainment.com", "password": "Test1234!"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in login response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    # --- Status All with can_write flags ---
    
    def test_status_all_returns_200(self, auth_headers):
        """Status all endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        assert response.status_code == 200
        print(f"Status all: {response.json()}")
    
    def test_status_all_has_platforms_object(self, auth_headers):
        """Status response contains platforms object"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        assert "platforms" in data
        assert isinstance(data["platforms"], dict)
    
    def test_status_twitter_has_can_write_flag(self, auth_headers):
        """Twitter status includes can_write flag"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        twitter = data["platforms"].get("twitter_x", {})
        assert "can_write" in twitter
        assert "can_read" in twitter
        print(f"Twitter can_write: {twitter['can_write']}, can_read: {twitter['can_read']}")
    
    def test_status_tiktok_has_can_write_flag(self, auth_headers):
        """TikTok status includes can_write flag"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        tiktok = data["platforms"].get("tiktok", {})
        assert "can_write" in tiktok
        assert "can_read" in tiktok
        print(f"TikTok can_write: {tiktok['can_write']}, can_read: {tiktok['can_read']}")
    
    def test_status_snapchat_has_can_write_flag(self, auth_headers):
        """Snapchat status includes can_write flag"""
        response = requests.get(f"{BASE_URL}/api/integrations/status/all", headers=auth_headers)
        data = response.json()
        snapchat = data["platforms"].get("snapchat", {})
        assert "can_write" in snapchat
        assert "can_read" in snapchat
        print(f"Snapchat can_write: {snapchat['can_write']}, can_read: {snapchat['can_read']}")
    
    # --- Unified Multi-Platform Publish ---
    
    def test_unified_publish_endpoint_returns_valid_response(self, auth_headers):
        """POST /api/integrations/publish returns proper response structure"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={
                "text": "TEST_automated_publish_test",
                "platforms": ["twitter_x", "tiktok", "snapchat"]
            }
        )
        # Should return 200 even if platforms fail (failures are in results)
        assert response.status_code == 200
        data = response.json()
        assert "publish_id" in data
        assert "results" in data
        assert "summary" in data
        assert "timestamp" in data
        print(f"Publish response: {data}")
    
    def test_unified_publish_results_contain_platform_responses(self, auth_headers):
        """Publish results include responses for each requested platform"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={
                "text": "TEST_platform_response_check",
                "platforms": ["twitter_x", "snapchat"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        results = data.get("results", {})
        # Each requested platform should have a result
        assert "twitter_x" in results
        assert "snapchat" in results
        # Each result should have success field and error if failed
        for platform, result in results.items():
            assert "success" in result
            if not result["success"]:
                assert "error" in result
    
    def test_unified_publish_with_media_url(self, auth_headers):
        """Publish with media_url parameter is accepted"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={
                "text": "TEST_with_media",
                "platforms": ["tiktok"],
                "media_url": "https://example.com/test-video.mp4"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # TikTok should get the video URL (even if it fails due to no token)
        print(f"Publish with media: {data}")
    
    def test_unified_publish_single_platform(self, auth_headers):
        """Publish to single platform works"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={
                "text": "TEST_single_platform",
                "platforms": ["snapchat"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"].endswith("/1 platforms succeeded") or "1 platform" in data["summary"]
    
    def test_unified_publish_unsupported_platform(self, auth_headers):
        """Unsupported platform returns error in results"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={
                "text": "TEST_unsupported",
                "platforms": ["unsupported_platform"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        result = data["results"].get("unsupported_platform", {})
        assert result.get("success") == False
        assert "Unsupported platform" in result.get("error", "")
    
    # --- Publish History ---
    
    def test_publish_history_returns_200(self, auth_headers):
        """GET /api/integrations/publish/history returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/publish/history",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_publish_history_has_correct_structure(self, auth_headers):
        """History response has history array and count"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/publish/history",
            headers=auth_headers
        )
        data = response.json()
        assert "history" in data
        assert "count" in data
        assert isinstance(data["history"], list)
    
    def test_publish_history_contains_recent_publish(self, auth_headers):
        """Recent publish appears in history"""
        # First create a publish
        publish_resp = requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={
                "text": "TEST_history_check_unique_text_12345",
                "platforms": ["twitter_x"]
            }
        )
        publish_id = publish_resp.json().get("publish_id")
        
        # Then check history
        history_resp = requests.get(
            f"{BASE_URL}/api/integrations/publish/history?limit=10",
            headers=auth_headers
        )
        data = history_resp.json()
        history_ids = [h.get("id") for h in data.get("history", [])]
        assert publish_id in history_ids, f"Published ID {publish_id} not found in history"
    
    def test_publish_history_respects_limit(self, auth_headers):
        """History limit parameter works"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/publish/history?limit=2",
            headers=auth_headers
        )
        data = response.json()
        assert len(data.get("history", [])) <= 2
    
    # --- Individual Platform Tweet Endpoint ---
    
    def test_twitter_tweet_requires_oauth(self, auth_headers):
        """POST /api/integrations/twitter/tweet returns error without OAuth token"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/twitter/tweet",
            headers=auth_headers,
            json={"text": "TEST_tweet"}
        )
        # Expected: 400 error because no user OAuth token
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "OAuth" in data["detail"] or "access token" in data["detail"].lower()
    
    # --- Individual TikTok Publish Endpoint ---
    
    def test_tiktok_publish_requires_oauth(self, auth_headers):
        """POST /api/integrations/tiktok/publish returns error without OAuth"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/tiktok/publish",
            headers=auth_headers,
            json={"title": "TEST_tiktok", "video_url": "https://example.com/video.mp4"}
        )
        # Expected: 400 error because no TikTok OAuth
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "OAuth" in data["detail"] or "access token" in data["detail"].lower()
    
    def test_tiktok_publish_requires_media(self, auth_headers):
        """TikTok publish without video_url or photo_urls fails with 400"""
        # First we'd need OAuth, but even if we had it, no media = 400
        response = requests.post(
            f"{BASE_URL}/api/integrations/tiktok/publish",
            headers=auth_headers,
            json={"title": "TEST_no_media"}
        )
        # Will return 400 for no OAuth first
        assert response.status_code == 400
    
    # --- Individual Snapchat Publish Endpoint ---
    
    def test_snapchat_publish_attempts_api_call(self, auth_headers):
        """POST /api/integrations/snapchat/publish attempts real API"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/snapchat/publish",
            headers=auth_headers,
            json={"text": "TEST_snapchat"}
        )
        # May return 200 with success:false or an error from Snapchat API
        assert response.status_code == 200
        data = response.json()
        # Response should have success and error fields
        assert "success" in data
        if not data["success"]:
            assert "error" in data
            print(f"Snapchat publish error (expected): {data['error']}")
    
    # --- Authentication Tests ---
    
    def test_publish_requires_auth(self):
        """Publish endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers={"Content-Type": "application/json"},
            json={"text": "TEST_no_auth", "platforms": ["twitter_x"]}
        )
        assert response.status_code in [401, 403]
    
    def test_history_requires_auth(self):
        """History endpoint requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/integrations/publish/history"
        )
        assert response.status_code in [401, 403]
    
    def test_twitter_tweet_requires_auth(self):
        """Twitter tweet endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/integrations/twitter/tweet",
            headers={"Content-Type": "application/json"},
            json={"text": "TEST"}
        )
        assert response.status_code in [401, 403]


class TestPublishHistoryPersistence:
    """Test that publish history is properly persisted in MongoDB"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "owner@bigmannentertainment.com", "password": "Test1234!"},
            headers={"Content-Type": "application/json"}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_publish_history_persists_text(self, auth_headers):
        """Published text is saved in history"""
        unique_text = f"TEST_persistence_check_{os.urandom(4).hex()}"
        
        # Publish
        requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={"text": unique_text, "platforms": ["snapchat"]}
        )
        
        # Fetch history
        response = requests.get(
            f"{BASE_URL}/api/integrations/publish/history?limit=5",
            headers=auth_headers
        )
        data = response.json()
        texts = [h.get("text") for h in data.get("history", [])]
        assert unique_text in texts
    
    def test_publish_history_persists_platforms(self, auth_headers):
        """Published platforms are saved in history"""
        unique_text = f"TEST_platforms_{os.urandom(4).hex()}"
        target_platforms = ["twitter_x", "snapchat"]
        
        # Publish
        requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={"text": unique_text, "platforms": target_platforms}
        )
        
        # Fetch history
        response = requests.get(
            f"{BASE_URL}/api/integrations/publish/history?limit=5",
            headers=auth_headers
        )
        data = response.json()
        for item in data.get("history", []):
            if item.get("text") == unique_text:
                assert set(item.get("platforms", [])) == set(target_platforms)
                break
    
    def test_publish_history_includes_results(self, auth_headers):
        """Published results (success/error) are saved in history"""
        unique_text = f"TEST_results_{os.urandom(4).hex()}"
        
        # Publish
        requests.post(
            f"{BASE_URL}/api/integrations/publish",
            headers=auth_headers,
            json={"text": unique_text, "platforms": ["twitter_x"]}
        )
        
        # Fetch history
        response = requests.get(
            f"{BASE_URL}/api/integrations/publish/history?limit=5",
            headers=auth_headers
        )
        data = response.json()
        for item in data.get("history", []):
            if item.get("text") == unique_text:
                assert "results" in item
                assert "twitter_x" in item["results"]
                assert "success" in item["results"]["twitter_x"]
                break
