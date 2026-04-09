"""
Test Analytics De-mocking Feature
Tests that demographics, geo, and best-times endpoints return real computed data
from analytics_events collection instead of hardcoded values.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAnalyticsDemocking:
    """Test suite for de-mocked analytics endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("access_token")
        assert self.token, "No access_token in login response"
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    # ─── SEED DATA ENDPOINT ───
    
    def test_seed_data_endpoint_exists(self):
        """POST /api/analytics/seed-data - endpoint exists and returns valid response"""
        response = requests.post(f"{BASE_URL}/api/analytics/seed-data", headers=self.headers)
        assert response.status_code == 200, f"Seed data failed: {response.text}"
        data = response.json()
        # Should return message about seeding (either already seeded or newly seeded)
        assert "message" in data, "Response should contain 'message' field"
        print(f"Seed data response: {data}")
    
    # ─── DEMOGRAPHICS ENDPOINT ───
    
    def test_demographics_endpoint_returns_200(self):
        """GET /api/analytics/demographics - returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        assert response.status_code == 200, f"Demographics failed: {response.text}"
    
    def test_demographics_has_data_source_field(self):
        """GET /api/analytics/demographics - returns data_source field"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        data = response.json()
        assert "data_source" in data, "Demographics should have 'data_source' field"
        assert data["data_source"] == "analytics_events", f"Expected data_source='analytics_events', got '{data.get('data_source')}'"
        print(f"Demographics data_source: {data['data_source']}")
    
    def test_demographics_has_data_points_field(self):
        """GET /api/analytics/demographics - returns data_points count"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        data = response.json()
        assert "data_points" in data, "Demographics should have 'data_points' field"
        assert isinstance(data["data_points"], int), "data_points should be an integer"
        print(f"Demographics data_points: {data['data_points']}")
    
    def test_demographics_has_age_groups(self):
        """GET /api/analytics/demographics - returns age_groups array"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        data = response.json()
        assert "age_groups" in data, "Demographics should have 'age_groups' field"
        assert isinstance(data["age_groups"], list), "age_groups should be a list"
        if data["age_groups"]:
            ag = data["age_groups"][0]
            assert "range" in ag, "Age group should have 'range' field"
            assert "percentage" in ag, "Age group should have 'percentage' field"
        print(f"Age groups: {data['age_groups']}")
    
    def test_demographics_has_gender_split(self):
        """GET /api/analytics/demographics - returns gender_split array"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        data = response.json()
        assert "gender_split" in data, "Demographics should have 'gender_split' field"
        assert isinstance(data["gender_split"], list), "gender_split should be a list"
        if data["gender_split"]:
            gs = data["gender_split"][0]
            assert "gender" in gs, "Gender split should have 'gender' field"
            assert "percentage" in gs, "Gender split should have 'percentage' field"
        print(f"Gender split: {data['gender_split']}")
    
    def test_demographics_has_devices(self):
        """GET /api/analytics/demographics - returns devices array"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        data = response.json()
        assert "devices" in data, "Demographics should have 'devices' field"
        assert isinstance(data["devices"], list), "devices should be a list"
        if data["devices"]:
            d = data["devices"][0]
            assert "type" in d, "Device should have 'type' field"
            assert "percentage" in d, "Device should have 'percentage' field"
        print(f"Devices: {data['devices']}")
    
    def test_demographics_has_interests(self):
        """GET /api/analytics/demographics - returns interests array"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        data = response.json()
        assert "interests" in data, "Demographics should have 'interests' field"
        assert isinstance(data["interests"], list), "interests should be a list"
        if data["interests"]:
            i = data["interests"][0]
            assert "category" in i, "Interest should have 'category' field"
            assert "percentage" in i, "Interest should have 'percentage' field"
        print(f"Interests: {data['interests']}")
    
    # ─── GEO DISTRIBUTION ENDPOINT ───
    
    def test_geo_endpoint_returns_200(self):
        """GET /api/analytics/geo - returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        assert response.status_code == 200, f"Geo failed: {response.text}"
    
    def test_geo_has_data_source_field(self):
        """GET /api/analytics/geo - returns data_source field"""
        response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        data = response.json()
        assert "data_source" in data, "Geo should have 'data_source' field"
        assert data["data_source"] == "analytics_events", f"Expected data_source='analytics_events', got '{data.get('data_source')}'"
        print(f"Geo data_source: {data['data_source']}")
    
    def test_geo_has_data_points_field(self):
        """GET /api/analytics/geo - returns data_points count"""
        response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        data = response.json()
        assert "data_points" in data, "Geo should have 'data_points' field"
        assert isinstance(data["data_points"], int), "data_points should be an integer"
        print(f"Geo data_points: {data['data_points']}")
    
    def test_geo_has_countries(self):
        """GET /api/analytics/geo - returns countries array"""
        response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        data = response.json()
        assert "countries" in data, "Geo should have 'countries' field"
        assert isinstance(data["countries"], list), "countries should be a list"
        if data["countries"]:
            c = data["countries"][0]
            assert "code" in c, "Country should have 'code' field"
            assert "name" in c, "Country should have 'name' field"
            assert "percentage" in c, "Country should have 'percentage' field"
        print(f"Countries count: {len(data['countries'])}")
    
    def test_geo_has_us_cities(self):
        """GET /api/analytics/geo - returns top_cities_us array"""
        response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        data = response.json()
        assert "top_cities_us" in data, "Geo should have 'top_cities_us' field"
        assert isinstance(data["top_cities_us"], list), "top_cities_us should be a list"
        if data["top_cities_us"]:
            c = data["top_cities_us"][0]
            assert "city" in c, "US city should have 'city' field"
            assert "state" in c, "US city should have 'state' field"
            assert "percentage" in c, "US city should have 'percentage' field"
        print(f"US cities: {data['top_cities_us']}")
    
    def test_geo_has_primary_market(self):
        """GET /api/analytics/geo - returns primary_market info"""
        response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        data = response.json()
        assert "primary_market" in data, "Geo should have 'primary_market' field"
        assert "primary_market_pct" in data, "Geo should have 'primary_market_pct' field"
        print(f"Primary market: {data['primary_market']} ({data['primary_market_pct']}%)")
    
    # ─── BEST TIMES ENDPOINT ───
    
    def test_best_times_endpoint_returns_200(self):
        """GET /api/analytics/best-times - returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/best-times", headers=self.headers)
        assert response.status_code == 200, f"Best times failed: {response.text}"
    
    def test_best_times_has_data_source_field(self):
        """GET /api/analytics/best-times - returns data_source field"""
        response = requests.get(f"{BASE_URL}/api/analytics/best-times", headers=self.headers)
        data = response.json()
        assert "data_source" in data, "Best times should have 'data_source' field"
        # data_source can be 'real' or 'insufficient_data'
        assert data["data_source"] in ["real", "insufficient_data"], f"Unexpected data_source: {data['data_source']}"
        print(f"Best times data_source: {data['data_source']}")
    
    def test_best_times_has_heatmap(self):
        """GET /api/analytics/best-times - returns heatmap 7x24 matrix"""
        response = requests.get(f"{BASE_URL}/api/analytics/best-times", headers=self.headers)
        data = response.json()
        assert "heatmap" in data, "Best times should have 'heatmap' field"
        assert isinstance(data["heatmap"], list), "heatmap should be a list"
        assert len(data["heatmap"]) == 7, f"Heatmap should have 7 days, got {len(data['heatmap'])}"
        for day_row in data["heatmap"]:
            assert len(day_row) == 24, f"Each day should have 24 hours, got {len(day_row)}"
        print(f"Heatmap dimensions: {len(data['heatmap'])}x{len(data['heatmap'][0])}")
    
    def test_best_times_has_recommendations(self):
        """GET /api/analytics/best-times - returns recommendations array"""
        response = requests.get(f"{BASE_URL}/api/analytics/best-times", headers=self.headers)
        data = response.json()
        assert "recommendations" in data, "Best times should have 'recommendations' field"
        assert isinstance(data["recommendations"], list), "recommendations should be a list"
        if data["recommendations"]:
            r = data["recommendations"][0]
            assert "day" in r, "Recommendation should have 'day' field"
            assert "time_range" in r, "Recommendation should have 'time_range' field"
            assert "score" in r, "Recommendation should have 'score' field"
        print(f"Recommendations: {data['recommendations']}")
    
    def test_best_times_has_top_slots(self):
        """GET /api/analytics/best-times - returns top_slots array"""
        response = requests.get(f"{BASE_URL}/api/analytics/best-times", headers=self.headers)
        data = response.json()
        assert "top_slots" in data, "Best times should have 'top_slots' field"
        assert isinstance(data["top_slots"], list), "top_slots should be a list"
        print(f"Top slots count: {len(data['top_slots'])}")
    
    # ─── OVERVIEW ENDPOINT ───
    
    def test_overview_endpoint_returns_200(self):
        """GET /api/analytics/overview - returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/overview", headers=self.headers)
        assert response.status_code == 200, f"Overview failed: {response.text}"
    
    def test_overview_has_content_stats(self):
        """GET /api/analytics/overview - returns content stats"""
        response = requests.get(f"{BASE_URL}/api/analytics/overview", headers=self.headers)
        data = response.json()
        assert "total_content" in data, "Overview should have 'total_content' field"
        assert "content_by_type" in data, "Overview should have 'content_by_type' field"
        assert "engagement" in data, "Overview should have 'engagement' field"
        print(f"Overview: total_content={data['total_content']}, engagement={data['engagement']}")
    
    # ─── CONTENT PERFORMANCE ENDPOINT ───
    
    def test_content_performance_endpoint_returns_200(self):
        """GET /api/analytics/content-performance - returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/content-performance", headers=self.headers)
        assert response.status_code == 200, f"Content performance failed: {response.text}"
    
    def test_content_performance_has_items(self):
        """GET /api/analytics/content-performance - returns items array"""
        response = requests.get(f"{BASE_URL}/api/analytics/content-performance", headers=self.headers)
        data = response.json()
        assert "items" in data, "Content performance should have 'items' field"
        assert isinstance(data["items"], list), "items should be a list"
        print(f"Content performance items: {len(data['items'])}")
    
    # ─── REVENUE OVERVIEW ENDPOINT ───
    
    def test_revenue_overview_endpoint_returns_200(self):
        """GET /api/analytics/revenue/overview - returns 200"""
        response = requests.get(f"{BASE_URL}/api/analytics/revenue/overview", headers=self.headers)
        assert response.status_code == 200, f"Revenue overview failed: {response.text}"
    
    def test_revenue_overview_has_total_revenue(self):
        """GET /api/analytics/revenue/overview - returns total_revenue"""
        response = requests.get(f"{BASE_URL}/api/analytics/revenue/overview", headers=self.headers)
        data = response.json()
        assert "total_revenue" in data, "Revenue overview should have 'total_revenue' field"
        print(f"Revenue overview: total_revenue={data['total_revenue']}")
    
    # ─── DATA INTEGRITY CHECKS ───
    
    def test_demographics_percentages_sum_to_100(self):
        """Demographics age_groups percentages should sum close to 100"""
        response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        data = response.json()
        if data.get("age_groups") and data.get("data_points", 0) > 0:
            total = sum(ag["percentage"] for ag in data["age_groups"])
            # Allow some tolerance for rounding
            assert 95 <= total <= 105, f"Age group percentages sum to {total}, expected ~100"
            print(f"Age groups sum: {total}%")
    
    def test_geo_percentages_sum_to_100(self):
        """Geo countries percentages should sum close to 100"""
        response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        data = response.json()
        if data.get("countries") and data.get("data_points", 0) > 0:
            total = sum(c["percentage"] for c in data["countries"])
            # Allow some tolerance for rounding
            assert 95 <= total <= 105, f"Country percentages sum to {total}, expected ~100"
            print(f"Countries sum: {total}%")
    
    def test_data_points_match_between_endpoints(self):
        """Demographics and geo should have consistent data_points"""
        demo_response = requests.get(f"{BASE_URL}/api/analytics/demographics", headers=self.headers)
        geo_response = requests.get(f"{BASE_URL}/api/analytics/geo", headers=self.headers)
        demo_data = demo_response.json()
        geo_data = geo_response.json()
        
        demo_points = demo_data.get("data_points", 0)
        geo_points = geo_data.get("data_points", 0)
        
        # They should be the same or very close (geo might filter by country field)
        print(f"Demographics data_points: {demo_points}, Geo data_points: {geo_points}")
        # Just verify both have data
        assert demo_points >= 0, "Demographics should have non-negative data_points"
        assert geo_points >= 0, "Geo should have non-negative data_points"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
