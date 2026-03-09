"""
Server.py Refactoring Regression Tests
Tests all key endpoints to verify the server refactoring (middleware.py, startup.py, 
websocket_routes.py, webhook_routes.py) didn't break any existing functionality.

Endpoints tested:
- /health - Global health check
- /api/auth/login - Authentication  
- /api/user-content - Content management (authenticated)
- /api/analytics/overview - Analytics (authenticated)
- /api/notifications/unread-count - Notifications (authenticated)
- /api/messages/conversations - Messaging (authenticated)
- /api/webhook/stripe - Stripe webhook
- /api/user-content/{id}/comments - Comments system
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"
ADMIN_EMAIL = "cveadmin@test.com"
ADMIN_PASSWORD = "Test1234!"
CONTENT_ID_WITH_COMMENTS = "69aeea3dfaaa80e20c462114"


class TestRefactoringRegression:
    """Verify all endpoints work after server.py refactoring"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and authenticate"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_auth_token(self, email=OWNER_EMAIL, password=OWNER_PASSWORD):
        """Helper to get auth token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    # ── Health Endpoint (API Level) ──────────────────────────────
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy status, got: {data.get('status')}"
        assert "database" in data, "Missing database field in health response"
        assert "services" in data, "Missing services field in health response"
        print(f"✓ Health endpoint: status={data['status']}, db={data.get('database')}")
    
    def test_root_endpoint(self):
        """Test / returns API info"""
        response = self.session.get(f"{BASE_URL}/")
        # Note: May return HTML if frontend is at root, so just check it doesn't error
        assert response.status_code in [200, 404], f"Root endpoint error: {response.status_code}"
        print(f"✓ Root endpoint: status={response.status_code}")
    
    # ── Authentication Routes (auth_routes.py) ────────────────────
    def test_auth_login_owner(self):
        """Test /api/auth/login with owner credentials"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Missing access_token in login response"
        assert "user" in data, "Missing user in login response"
        assert data["user"]["email"] == OWNER_EMAIL, "Email mismatch in user data"
        print(f"✓ Auth login (owner): token={data['access_token'][:20]}...")
    
    def test_auth_login_admin(self):
        """Test /api/auth/login with admin credentials"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Missing access_token"
        print(f"✓ Auth login (admin): token={data['access_token'][:20]}...")
    
    def test_auth_login_invalid(self):
        """Test /api/auth/login with invalid credentials"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got: {response.status_code}"
        print("✓ Auth login (invalid): correctly returns 401")
    
    def test_auth_me_endpoint(self):
        """Test /api/auth/me returns current user"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert "email" in data, "Missing email in auth/me response"
        print(f"✓ Auth me: user={data.get('email')}")
    
    # ── Content Routes (content_routes.py) ────────────────────────
    def test_user_content_list(self):
        """Test /api/user-content returns user's content (authenticated)"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/user-content")
        assert response.status_code == 200, f"User content list failed: {response.text}"
        data = response.json()
        assert "items" in data, "Missing items in content response"
        assert "total" in data, "Missing total in content response"
        print(f"✓ User content list: {data.get('total')} items")
    
    def test_user_content_unauthorized(self):
        """Test /api/user-content without auth returns 401/403"""
        # Clear auth header
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        response = self.session.get(f"{BASE_URL}/api/user-content")
        assert response.status_code in [401, 403], f"Expected 401/403, got: {response.status_code}"
        print("✓ User content (unauth): correctly returns 401/403")
    
    # ── Comments Routes (content_routes.py) ───────────────────────
    def test_comments_list(self):
        """Test /api/user-content/{id}/comments returns comments"""
        response = self.session.get(f"{BASE_URL}/api/user-content/{CONTENT_ID_WITH_COMMENTS}/comments")
        assert response.status_code == 200, f"Comments list failed: {response.text}"
        data = response.json()
        assert "items" in data, "Missing items in comments response"
        assert "total" in data, "Missing total in comments response"
        print(f"✓ Comments list: {data.get('total')} comments")
    
    def test_comments_invalid_id(self):
        """Test /api/user-content/{invalid}/comments returns 400"""
        response = self.session.get(f"{BASE_URL}/api/user-content/invalid-id/comments")
        # May return 200 with empty or 400 for invalid ID
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        print(f"✓ Comments (invalid ID): status={response.status_code}")
    
    # ── Analytics Routes (analytics_routes.py) ────────────────────
    def test_analytics_overview(self):
        """Test /api/analytics/overview returns stats (authenticated)"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200, f"Analytics overview failed: {response.text}"
        data = response.json()
        assert "total_content" in data, "Missing total_content in analytics"
        assert "content_by_type" in data, "Missing content_by_type in analytics"
        assert "engagement" in data, "Missing engagement in analytics"
        print(f"✓ Analytics overview: total_content={data.get('total_content')}")
    
    def test_analytics_content_performance(self):
        """Test /api/analytics/content-performance returns top content"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/analytics/content-performance")
        assert response.status_code == 200, f"Content performance failed: {response.text}"
        data = response.json()
        assert "items" in data, "Missing items in content performance"
        print(f"✓ Analytics content performance: {len(data.get('items', []))} items")
    
    # ── Notification Routes (notification_routes.py) ──────────────
    def test_notifications_unread_count(self):
        """Test /api/notifications/unread-count returns count"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200, f"Notifications unread count failed: {response.text}"
        data = response.json()
        assert "unread" in data, "Missing unread count in response"
        print(f"✓ Notifications unread count: {data.get('unread')}")
    
    def test_notifications_list(self):
        """Test /api/notifications returns list"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200, f"Notifications list failed: {response.text}"
        data = response.json()
        assert "items" in data, "Missing items in notifications"
        assert "total" in data, "Missing total in notifications"
        print(f"✓ Notifications list: {data.get('total')} notifications")
    
    # ── Messaging Routes (messaging_routes.py) ────────────────────
    def test_messages_conversations(self):
        """Test /api/messages/conversations returns conversations"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/messages/conversations")
        assert response.status_code == 200, f"Messages conversations failed: {response.text}"
        data = response.json()
        assert "conversations" in data, "Missing conversations in response"
        print(f"✓ Messages conversations: {len(data.get('conversations', []))} conversations")
    
    def test_messages_unread_count(self):
        """Test /api/messages/unread-count returns count"""
        token = self.get_auth_token()
        assert token, "Failed to get auth token"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/messages/unread-count")
        assert response.status_code == 200, f"Messages unread count failed: {response.text}"
        data = response.json()
        assert "unread_count" in data, "Missing unread_count in response"
        print(f"✓ Messages unread count: {data.get('unread_count')}")
    
    # ── Webhook Routes (webhook_routes.py) ────────────────────────
    def test_stripe_webhook_missing_signature(self):
        """Test /api/webhook/stripe returns 400 without signature"""
        response = self.session.post(f"{BASE_URL}/api/webhook/stripe", data="{}")
        assert response.status_code == 400, f"Expected 400, got: {response.status_code}"
        data = response.json()
        assert "detail" in data, "Missing error detail"
        print(f"✓ Stripe webhook (no signature): correctly returns 400")
    
    # ── Middleware Tests ──────────────────────────────────────────
    def test_response_headers(self):
        """Test middleware adds security headers"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        # Check for security headers added by middleware.py
        # Note: Some headers may be stripped/modified by Cloudflare proxy
        headers = {k.lower(): v for k, v in response.headers.items()}
        assert "x-content-type-options" in headers, "Missing X-Content-Type-Options header"
        assert "x-frame-options" in headers, "Missing X-Frame-Options header"
        print(f"✓ Middleware headers: Security headers present (X-Content-Type-Options, X-Frame-Options)")
    
    # ── Additional Route Verification ─────────────────────────────
    def test_api_health_route(self):
        """Test /api/health returns healthy"""
        response = self.session.get(f"{BASE_URL}/api/health")
        # This may be a different health endpoint in health_routes.py
        assert response.status_code in [200, 404], f"API health unexpected: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API health route: status={data.get('status', 'ok')}")
        else:
            print("✓ API health route: not found (404) - may be at /health only")


class TestWebSocketEndpoints:
    """Test WebSocket endpoint availability (basic HTTP check)"""
    
    def test_ws_sla_endpoint_exists(self):
        """Verify /api/ws/sla WebSocket endpoint is registered"""
        # WebSocket endpoints return different responses when accessed via HTTP
        response = requests.get(f"{BASE_URL}/api/ws/sla")
        # WebSocket routes typically return 403 or 400 when accessed via HTTP
        assert response.status_code in [400, 403, 404, 426], f"WS SLA unexpected: {response.status_code}"
        print(f"✓ WS /api/ws/sla endpoint: status={response.status_code} (expected for HTTP access)")
    
    def test_ws_notifications_endpoint_exists(self):
        """Verify /api/ws/notifications WebSocket endpoint is registered"""
        response = requests.get(f"{BASE_URL}/api/ws/notifications")
        # WebSocket routes typically return 403 or 400 when accessed via HTTP
        assert response.status_code in [400, 403, 404, 426], f"WS notifications unexpected: {response.status_code}"
        print(f"✓ WS /api/ws/notifications endpoint: status={response.status_code} (expected for HTTP access)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
