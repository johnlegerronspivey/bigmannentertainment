"""
Scheduled Posts API Tests
Tests for the Post-Scheduling feature CRUD endpoints:
- POST /api/integrations/scheduled-posts - Create scheduled post
- GET /api/integrations/scheduled-posts - List scheduled posts
- PUT /api/integrations/scheduled-posts/{id} - Update scheduled post
- DELETE /api/integrations/scheduled-posts/{id} - Delete scheduled post
"""
import pytest
import requests
import os
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestScheduledPostsAPI:
    """Scheduled Posts CRUD endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client, auth_token):
        """Setup test fixtures"""
        self.client = api_client
        self.token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        self.created_post_ids = []
    
    def teardown_method(self, method):
        """Cleanup test data after each test"""
        for post_id in self.created_post_ids:
            try:
                requests.delete(
                    f"{BASE_URL}/api/integrations/scheduled-posts/{post_id}",
                    headers=self.headers
                )
            except:
                pass
    
    # --- CREATE TESTS ---
    
    def test_create_scheduled_post_success(self, api_client, auth_token):
        """POST /api/integrations/scheduled-posts - Create with future time"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        future_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        
        payload = {
            "text": "TEST_Scheduled post for testing",
            "platforms": ["twitter_x"],
            "scheduled_time": future_time,
            "media_url": None
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "scheduled_post" in data
        assert data["message"] == "Post scheduled successfully."
        
        post = data["scheduled_post"]
        assert post["text"] == payload["text"]
        assert post["platforms"] == payload["platforms"]
        assert post["status"] == "pending"
        assert "id" in post
        
        # Cleanup
        post_id = post["id"]
        api_client.delete(f"{BASE_URL}/api/integrations/scheduled-posts/{post_id}", headers=headers)
    
    def test_create_scheduled_post_reject_past_time(self, api_client, auth_token):
        """POST /api/integrations/scheduled-posts - Reject past scheduled_time"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        
        payload = {
            "text": "TEST_Past time post",
            "platforms": ["twitter_x"],
            "scheduled_time": past_time
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "future" in data.get("detail", "").lower()
    
    def test_create_scheduled_post_reject_invalid_time_format(self, api_client, auth_token):
        """POST /api/integrations/scheduled-posts - Reject invalid ISO time format"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "text": "TEST_Invalid time format",
            "platforms": ["twitter_x"],
            "scheduled_time": "not-a-valid-date"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "iso" in data.get("detail", "").lower() or "invalid" in data.get("detail", "").lower()
    
    def test_create_scheduled_post_multiple_platforms(self, api_client, auth_token):
        """POST /api/integrations/scheduled-posts - Create with multiple platforms"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        future_time = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
        
        payload = {
            "text": "TEST_Multi-platform scheduled post",
            "platforms": ["twitter_x", "snapchat"],
            "scheduled_time": future_time,
            "media_url": "https://example.com/video.mp4"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        post = data["scheduled_post"]
        assert set(post["platforms"]) == {"twitter_x", "snapchat"}
        assert post["media_url"] == payload["media_url"]
        assert post["total"] == 2
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/integrations/scheduled-posts/{post['id']}", headers=headers)
    
    # --- LIST TESTS ---
    
    def test_list_scheduled_posts_success(self, api_client, auth_token):
        """GET /api/integrations/scheduled-posts - List all scheduled posts"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = api_client.get(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "scheduled_posts" in data
        assert "count" in data
        assert isinstance(data["scheduled_posts"], list)
    
    def test_list_scheduled_posts_filter_by_status(self, api_client, auth_token):
        """GET /api/integrations/scheduled-posts?status=pending - Filter by status"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create a pending post first
        future_time = (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()
        create_resp = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json={"text": "TEST_Filter test post", "platforms": ["twitter_x"], "scheduled_time": future_time},
            headers=headers
        )
        assert create_resp.status_code == 200
        post_id = create_resp.json()["scheduled_post"]["id"]
        
        # Filter by pending status
        response = api_client.get(
            f"{BASE_URL}/api/integrations/scheduled-posts?status=pending",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned posts should have pending status
        for post in data["scheduled_posts"]:
            assert post["status"] == "pending"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/integrations/scheduled-posts/{post_id}", headers=headers)
    
    def test_list_scheduled_posts_with_limit(self, api_client, auth_token):
        """GET /api/integrations/scheduled-posts?limit=5 - Limit results"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = api_client.get(
            f"{BASE_URL}/api/integrations/scheduled-posts?limit=5",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["scheduled_posts"]) <= 5
    
    # --- UPDATE TESTS ---
    
    def test_update_scheduled_post_success(self, api_client, auth_token):
        """PUT /api/integrations/scheduled-posts/{id} - Update pending post"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create a post first
        future_time = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
        create_resp = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json={"text": "TEST_Original text", "platforms": ["twitter_x"], "scheduled_time": future_time},
            headers=headers
        )
        assert create_resp.status_code == 200
        post_id = create_resp.json()["scheduled_post"]["id"]
        
        # Update the post
        new_future_time = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
        update_payload = {
            "text": "TEST_Updated text",
            "scheduled_time": new_future_time
        }
        
        response = api_client.put(
            f"{BASE_URL}/api/integrations/scheduled-posts/{post_id}",
            json=update_payload,
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["scheduled_post"]["text"] == "TEST_Updated text"
        assert data["message"] == "Scheduled post updated."
        
        # Verify persistence with GET
        get_resp = api_client.get(f"{BASE_URL}/api/integrations/scheduled-posts", headers=headers)
        posts = get_resp.json()["scheduled_posts"]
        updated_post = next((p for p in posts if p["id"] == post_id), None)
        assert updated_post is not None
        assert updated_post["text"] == "TEST_Updated text"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/integrations/scheduled-posts/{post_id}", headers=headers)
    
    def test_update_scheduled_post_reject_non_pending(self, api_client, auth_token):
        """PUT /api/integrations/scheduled-posts/{id} - Reject update of non-pending post"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # First get existing posts to find a non-pending one (if any)
        response = api_client.get(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            headers=headers
        )
        data = response.json()
        
        # Find a published or failed post
        non_pending_post = next(
            (p for p in data["scheduled_posts"] if p["status"] != "pending"),
            None
        )
        
        if non_pending_post:
            update_resp = api_client.put(
                f"{BASE_URL}/api/integrations/scheduled-posts/{non_pending_post['id']}",
                json={"text": "TEST_Should fail"},
                headers=headers
            )
            assert update_resp.status_code == 400
            assert "pending" in update_resp.json().get("detail", "").lower() or "cannot" in update_resp.json().get("detail", "").lower()
        else:
            pytest.skip("No non-pending posts available to test this case")
    
    def test_update_scheduled_post_not_found(self, api_client, auth_token):
        """PUT /api/integrations/scheduled-posts/{id} - 404 for non-existent post"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = api_client.put(
            f"{BASE_URL}/api/integrations/scheduled-posts/non-existent-id-12345",
            json={"text": "TEST_Should fail"},
            headers=headers
        )
        
        assert response.status_code == 404
    
    # --- DELETE TESTS ---
    
    def test_delete_scheduled_post_success(self, api_client, auth_token):
        """DELETE /api/integrations/scheduled-posts/{id} - Delete pending post"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Create a post first
        future_time = (datetime.now(timezone.utc) + timedelta(hours=7)).isoformat()
        create_resp = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json={"text": "TEST_To be deleted", "platforms": ["snapchat"], "scheduled_time": future_time},
            headers=headers
        )
        assert create_resp.status_code == 200
        post_id = create_resp.json()["scheduled_post"]["id"]
        
        # Delete the post
        response = api_client.delete(
            f"{BASE_URL}/api/integrations/scheduled-posts/{post_id}",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["message"] == "Scheduled post deleted."
        assert data["id"] == post_id
        
        # Verify deletion with GET
        get_resp = api_client.get(f"{BASE_URL}/api/integrations/scheduled-posts", headers=headers)
        posts = get_resp.json()["scheduled_posts"]
        deleted_post = next((p for p in posts if p["id"] == post_id), None)
        assert deleted_post is None
    
    def test_delete_scheduled_post_not_found(self, api_client, auth_token):
        """DELETE /api/integrations/scheduled-posts/{id} - 404 for non-existent post"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = api_client.delete(
            f"{BASE_URL}/api/integrations/scheduled-posts/non-existent-id-67890",
            headers=headers
        )
        
        assert response.status_code == 404
    
    # --- EDGE CASES ---
    
    def test_create_scheduled_post_requires_auth(self, api_client):
        """POST /api/integrations/scheduled-posts - Requires authentication"""
        future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        
        response = api_client.post(
            f"{BASE_URL}/api/integrations/scheduled-posts",
            json={"text": "TEST_No auth", "platforms": ["twitter_x"], "scheduled_time": future_time},
            headers={"Content-Type": "application/json"}  # No auth header
        )
        
        assert response.status_code in [401, 403]


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_token(api_client):
    """Get authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        # Handle both 'access_token' and 'token' field names
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Authentication failed - skipping authenticated tests: {response.text}")
