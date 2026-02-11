"""
Phase 12 Backend Tests: Usage Analytics + Enhanced AI Layout/Resize
Tests for the new analytics tracking APIs and enhanced AI layout suggestions.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestUsageAnalyticsHealth:
    """Health check for analytics tracking service"""
    
    def test_analytics_health(self):
        """GET /api/analytics-tracking/health - health check returns healthy"""
        response = requests.get(f"{BASE_URL}/api/analytics-tracking/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy"
        assert "Usage Analytics" in data.get("service", "")
        print("PASS: Analytics health check returns healthy")


class TestUsageAnalyticsTracking:
    """Tests for event tracking endpoints"""
    
    def test_track_single_event(self):
        """POST /api/analytics-tracking/track - track single event"""
        payload = {
            "event_type": "test_page_view",
            "category": "testing",
            "user_id": "test_user_001",
            "metadata": {"page": "/test", "browser": "pytest"}
        }
        response = requests.post(
            f"{BASE_URL}/api/analytics-tracking/track",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("tracked") == True, "Event should be tracked"
        assert data.get("event_type") == "test_page_view"
        assert data.get("category") == "testing"
        assert "event_id" in data, "Response should contain event_id"
        print(f"PASS: Single event tracked with id {data.get('event_id')}")
    
    def test_track_batch_events(self):
        """POST /api/analytics-tracking/track-batch - track multiple events"""
        payload = {
            "events": [
                {"event_type": "batch_event_1", "category": "testing", "user_id": "batch_user_001"},
                {"event_type": "batch_event_2", "category": "testing", "user_id": "batch_user_002"},
                {"event_type": "batch_event_3", "category": "ai_tools", "user_id": "batch_user_001"},
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/analytics-tracking/track-batch",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("tracked") == 3, f"Expected 3 events tracked, got {data.get('tracked')}"
        print(f"PASS: Batch tracked {data.get('tracked')} events")


class TestUsageAnalyticsDashboard:
    """Tests for dashboard statistics endpoint"""
    
    def test_dashboard_7d(self):
        """GET /api/analytics-tracking/dashboard?period=7d - returns stats"""
        response = requests.get(f"{BASE_URL}/api/analytics-tracking/dashboard?period=7d")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check required fields
        assert "total_events" in data, "Response should contain total_events"
        assert "active_users" in data, "Response should contain active_users"
        assert "categories" in data, "Response should contain categories"
        assert "top_events" in data, "Response should contain top_events"
        assert "daily_trend" in data, "Response should contain daily_trend"
        assert data.get("period") == "7d"
        
        # Validate data types
        assert isinstance(data["total_events"], int), "total_events should be integer"
        assert isinstance(data["active_users"], int), "active_users should be integer"
        assert isinstance(data["categories"], dict), "categories should be dict"
        assert isinstance(data["top_events"], list), "top_events should be list"
        assert isinstance(data["daily_trend"], list), "daily_trend should be list"
        
        print(f"PASS: Dashboard 7d returns total_events={data['total_events']}, active_users={data['active_users']}")
    
    def test_dashboard_30d(self):
        """GET /api/analytics-tracking/dashboard?period=30d - returns stats for 30 days"""
        response = requests.get(f"{BASE_URL}/api/analytics-tracking/dashboard?period=30d")
        assert response.status_code == 200
        data = response.json()
        assert data.get("period") == "30d"
        assert "total_events" in data
        print(f"PASS: Dashboard 30d returns data with period=30d")
    
    def test_dashboard_1d(self):
        """GET /api/analytics-tracking/dashboard?period=1d - returns today's stats"""
        response = requests.get(f"{BASE_URL}/api/analytics-tracking/dashboard?period=1d")
        assert response.status_code == 200
        data = response.json()
        assert data.get("period") == "1d"
        print(f"PASS: Dashboard 1d returns data")


class TestUsageAnalyticsFeatures:
    """Tests for feature usage breakdown endpoint"""
    
    def test_features_7d(self):
        """GET /api/analytics-tracking/features?period=7d - returns feature breakdown"""
        response = requests.get(f"{BASE_URL}/api/analytics-tracking/features?period=7d")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "features" in data, "Response should contain features"
        assert data.get("period") == "7d"
        assert isinstance(data["features"], dict), "features should be dict"
        
        # If features exist, verify structure
        for category, feature_data in data["features"].items():
            assert "total" in feature_data, f"Category {category} should have total"
            assert "events" in feature_data, f"Category {category} should have events"
        
        print(f"PASS: Features endpoint returns {len(data['features'])} categories")


class TestUsageAnalyticsUserActivity:
    """Tests for user activity endpoint"""
    
    def test_user_activity(self):
        """GET /api/analytics-tracking/users/user_001?period=30d - returns user activity"""
        response = requests.get(f"{BASE_URL}/api/analytics-tracking/users/user_001?period=30d")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("user_id") == "user_001"
        assert data.get("period") == "30d"
        assert "activity" in data, "Response should contain activity"
        assert "daily_trend" in data, "Response should contain daily_trend"
        assert "total_events" in data, "Response should contain total_events"
        
        print(f"PASS: User activity for user_001 returns total_events={data['total_events']}")


class TestUsageAnalyticsRealtime:
    """Tests for real-time statistics endpoint"""
    
    def test_realtime_stats(self):
        """GET /api/analytics-tracking/realtime - returns last hour events"""
        response = requests.get(f"{BASE_URL}/api/analytics-tracking/realtime")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "last_hour_events" in data, "Response should contain last_hour_events"
        assert "top_events" in data, "Response should contain top_events"
        assert "timestamp" in data, "Response should contain timestamp"
        assert isinstance(data["last_hour_events"], int), "last_hour_events should be int"
        
        print(f"PASS: Realtime stats returns last_hour_events={data['last_hour_events']}")


class TestEnhancedAILayoutSuggestions:
    """Tests for enhanced AI layout suggestions with content_type"""
    
    def test_suggest_layouts_with_content_type(self):
        """POST /api/creative-studio/ai-assets/suggest-layouts - with content_type parameter"""
        payload = {
            "content_type": "promotional",
            "platform": "instagram_post"
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/suggest-layouts",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "layouts" in data, "Response should contain layouts"
        assert "platform" in data, "Response should contain platform"
        assert "canvas" in data, "Response should contain canvas"
        
        layouts = data["layouts"]
        assert len(layouts) >= 6, f"Expected at least 6 layouts, got {len(layouts)}"
        
        # Check for specific layout names including new ones
        layout_names = [l.get("name") for l in layouts]
        print(f"Layout names: {layout_names}")
        
        # Check that Gradient Overlay and Grid Showcase are present
        assert "Gradient Overlay" in layout_names, "Should include Gradient Overlay layout"
        assert "Grid Showcase" in layout_names, "Should include Grid Showcase layout"
        
        print(f"PASS: Suggest layouts returns {len(layouts)} layouts including Gradient Overlay and Grid Showcase")
    
    def test_suggest_layouts_linkedin_banner(self):
        """POST /api/creative-studio/ai-assets/suggest-layouts - for linkedin_banner platform"""
        payload = {
            "content_type": "event",
            "platform": "linkedin_banner"
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/suggest-layouts",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("platform") == "linkedin_banner"
        canvas = data.get("canvas", {})
        assert canvas.get("width") == 1584, f"Expected width 1584, got {canvas.get('width')}"
        assert canvas.get("height") == 396, f"Expected height 396, got {canvas.get('height')}"
        
        print(f"PASS: LinkedIn banner layout has correct dimensions 1584x396")
    
    def test_suggest_layouts_pinterest_pin(self):
        """POST /api/creative-studio/ai-assets/suggest-layouts - for pinterest_pin platform"""
        payload = {
            "content_type": "product",
            "platform": "pinterest_pin"
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/suggest-layouts",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("platform") == "pinterest_pin"
        canvas = data.get("canvas", {})
        assert canvas.get("width") == 1000
        assert canvas.get("height") == 1500
        
        print(f"PASS: Pinterest pin layout has correct dimensions 1000x1500")
    
    def test_suggest_layouts_tiktok_video(self):
        """POST /api/creative-studio/ai-assets/suggest-layouts - for tiktok_video platform"""
        payload = {
            "content_type": "announcement",
            "platform": "tiktok_video"
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/suggest-layouts",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("platform") == "tiktok_video"
        canvas = data.get("canvas", {})
        assert canvas.get("width") == 1080
        assert canvas.get("height") == 1920
        
        print(f"PASS: TikTok video layout has correct dimensions 1080x1920")
    
    def test_suggest_layouts_twitter_header(self):
        """POST /api/creative-studio/ai-assets/suggest-layouts - for twitter_header platform"""
        payload = {
            "content_type": "portfolio",
            "platform": "twitter_header"
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/suggest-layouts",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("platform") == "twitter_header"
        canvas = data.get("canvas", {})
        assert canvas.get("width") == 1500
        assert canvas.get("height") == 500
        
        print(f"PASS: Twitter header layout has correct dimensions 1500x500")


class TestAIAssetsHealth:
    """Health check for AI assets service"""
    
    def test_ai_assets_health(self):
        """GET /api/creative-studio/ai-assets/health - health check"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/ai-assets/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: AI Assets health check returns healthy")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
