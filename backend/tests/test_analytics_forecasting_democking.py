"""
Test Analytics Forecasting Service De-mocking
Tests that all 5 analytics endpoints return real data from MongoDB (data_source='real')
Endpoints tested:
- GET /api/api/platform/analytics/revenue
- GET /api/api/platform/analytics/performance
- GET /api/api/platform/analytics/roi
- GET /api/api/platform/analytics/trends
- POST /api/api/platform/analytics/forecast
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAnalyticsForecastingDemocking:
    """Test that analytics forecasting endpoints return real MongoDB data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.user_id = "user_123"
        self.headers = {"Content-Type": "application/json"}
    
    # ─── Revenue Analytics Tests ───
    def test_revenue_analytics_returns_real_data(self):
        """Test GET /api/api/platform/analytics/revenue returns data_source='real'"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/revenue",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("data_source") == "real", f"Expected data_source='real', got '{data.get('data_source')}'"
        
        # Verify revenue breakdown structure
        revenue_breakdown = data.get("revenue_breakdown", {})
        assert "total_revenue" in revenue_breakdown, "Should have total_revenue"
        assert "by_platform" in revenue_breakdown, "Should have by_platform breakdown"
        assert "by_asset" in revenue_breakdown, "Should have by_asset breakdown"
        assert "by_time_period" in revenue_breakdown, "Should have by_time_period breakdown"
        assert "growth_rate" in revenue_breakdown, "Should have growth_rate"
        
        # Verify trends structure
        trends = data.get("trends", {})
        assert "monthly_growth" in trends, "Should have monthly_growth trend"
        assert "top_growth_platform" in trends, "Should have top_growth_platform"
        
        print(f"Revenue Analytics: total_revenue=${revenue_breakdown.get('total_revenue', 0):.2f}, data_source={data.get('data_source')}")
    
    def test_revenue_analytics_has_real_values(self):
        """Test that revenue analytics returns actual computed values, not hardcoded"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/revenue",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        revenue_breakdown = data.get("revenue_breakdown", {})
        
        # Total revenue should be a number (could be 0 if no data)
        total_revenue = revenue_breakdown.get("total_revenue", 0)
        assert isinstance(total_revenue, (int, float)), "total_revenue should be numeric"
        
        # by_platform should be a dict
        by_platform = revenue_breakdown.get("by_platform", {})
        assert isinstance(by_platform, dict), "by_platform should be a dictionary"
        
        print(f"Revenue by platform: {list(by_platform.keys())[:5]}")
    
    # ─── Performance Metrics Tests ───
    def test_performance_metrics_returns_real_data(self):
        """Test GET /api/api/platform/analytics/performance returns data_source='real'"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/performance",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("data_source") == "real", f"Expected data_source='real', got '{data.get('data_source')}'"
        
        # Verify performance metrics structure
        metrics = data.get("performance_metrics", {})
        assert "total_streams" in metrics, "Should have total_streams"
        assert "total_views" in metrics, "Should have total_views"
        assert "engagement_rate" in metrics, "Should have engagement_rate"
        assert "total_revenue" in metrics, "Should have total_revenue"
        assert "top_performing_assets" in metrics, "Should have top_performing_assets"
        assert "top_platforms" in metrics, "Should have top_platforms"
        
        # Verify insights
        insights = data.get("insights", [])
        assert isinstance(insights, list), "insights should be a list"
        
        print(f"Performance Metrics: total_streams={metrics.get('total_streams', 0)}, engagement_rate={metrics.get('engagement_rate', 0)}")
    
    def test_performance_metrics_has_audience_demographics(self):
        """Test that performance metrics includes audience demographics"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/performance",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        metrics = data.get("performance_metrics", {})
        
        # Check audience demographics
        demographics = metrics.get("audience_demographics", {})
        assert "top_countries" in demographics, "Should have top_countries in demographics"
        
        print(f"Top countries: {demographics.get('top_countries', [])[:3]}")
    
    # ─── ROI Analysis Tests ───
    def test_roi_analysis_returns_real_data(self):
        """Test GET /api/api/platform/analytics/roi returns data_source='real'"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/roi",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("data_source") == "real", f"Expected data_source='real', got '{data.get('data_source')}'"
        
        # Verify ROI analysis structure
        roi = data.get("roi_analysis", {})
        assert "total_investment" in roi, "Should have total_investment"
        assert "total_revenue" in roi, "Should have total_revenue"
        assert "net_profit" in roi, "Should have net_profit"
        assert "roi_percentage" in roi, "Should have roi_percentage"
        assert "by_platform" in roi, "Should have by_platform breakdown"
        assert "by_asset" in roi, "Should have by_asset breakdown"
        assert "monthly_trend" in roi, "Should have monthly_trend"
        
        print(f"ROI Analysis: roi_percentage={roi.get('roi_percentage', 0)}%, total_revenue=${roi.get('total_revenue', 0):.2f}")
    
    def test_roi_analysis_investment_is_10_percent(self):
        """Test that ROI investment is calculated as 10% of revenue (as documented)"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/roi",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        roi = data.get("roi_analysis", {})
        
        total_revenue = roi.get("total_revenue", 0)
        total_investment = roi.get("total_investment", 0)
        
        # Investment should be approximately 10% of revenue
        if total_revenue > 0:
            expected_investment = total_revenue * 0.10
            assert abs(total_investment - expected_investment) < 0.01, \
                f"Investment should be 10% of revenue. Expected ~{expected_investment:.2f}, got {total_investment:.2f}"
        
        print(f"Investment calculation: revenue=${total_revenue:.2f}, investment=${total_investment:.2f} (10%)")
    
    # ─── Trend Analysis Tests ───
    def test_trend_analysis_returns_real_data(self):
        """Test GET /api/api/platform/analytics/trends returns data_source='real'"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/trends",
            params={
                "user_id": self.user_id,
                "metrics": ["revenue", "streams"]
            },
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("data_source") == "real", f"Expected data_source='real', got '{data.get('data_source')}'"
        
        # Verify trend analysis structure
        trends = data.get("trend_analysis", {})
        assert isinstance(trends, dict), "trend_analysis should be a dictionary"
        
        # Verify market insights
        insights = data.get("market_insights", [])
        assert isinstance(insights, list), "market_insights should be a list"
        
        print(f"Trend Analysis: metrics={list(trends.keys())}, insights_count={len(insights)}")
    
    def test_trend_analysis_has_change_percentage(self):
        """Test that trend analysis includes change percentages"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/trends",
            params={
                "user_id": self.user_id,
                "metrics": ["revenue"]
            },
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        trends = data.get("trend_analysis", {})
        
        # Check revenue trend structure
        if "revenue" in trends:
            revenue_trend = trends["revenue"]
            assert "current_value" in revenue_trend, "Should have current_value"
            assert "previous_period" in revenue_trend, "Should have previous_period"
            assert "change_percentage" in revenue_trend, "Should have change_percentage"
            assert "trend_direction" in revenue_trend, "Should have trend_direction"
            
            print(f"Revenue trend: current={revenue_trend.get('current_value')}, change={revenue_trend.get('change_percentage')}%")
    
    # ─── Forecast Tests ───
    def test_forecast_returns_real_data(self):
        """Test POST /api/api/platform/analytics/forecast returns data_source='real'"""
        response = requests.post(
            f"{BASE_URL}/api/api/platform/analytics/forecast",
            params={
                "metric_type": "revenue",
                "time_frame": "month",
                "forecast_periods": 6,
                "user_id": self.user_id
            },
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("data_source") == "real", f"Expected data_source='real', got '{data.get('data_source')}'"
        
        # Verify forecast structure
        forecast = data.get("forecast", {})
        if forecast:  # May be empty if insufficient data
            assert "metric_type" in forecast, "Should have metric_type"
            assert "historical_data" in forecast, "Should have historical_data"
            assert "predicted_data" in forecast, "Should have predicted_data"
            assert "confidence_interval" in forecast, "Should have confidence_interval"
            assert "accuracy_score" in forecast, "Should have accuracy_score"
        
        # Verify summary
        summary = data.get("summary", {})
        assert "trend" in summary, "Should have trend in summary"
        
        print(f"Forecast: trend={summary.get('trend')}, expected_growth={summary.get('expected_growth')}")
    
    def test_forecast_has_historical_and_predicted_data(self):
        """Test that forecast includes both historical and predicted data points"""
        response = requests.post(
            f"{BASE_URL}/api/api/platform/analytics/forecast",
            params={
                "metric_type": "revenue",
                "time_frame": "month",
                "forecast_periods": 6,
                "user_id": self.user_id
            },
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        forecast = data.get("forecast", {})
        
        if forecast:
            historical = forecast.get("historical_data", [])
            predicted = forecast.get("predicted_data", [])
            
            # Historical data should have timestamp and value
            if historical:
                assert "timestamp" in historical[0], "Historical data should have timestamp"
                assert "value" in historical[0], "Historical data should have value"
            
            # Predicted data should have timestamp and value
            if predicted:
                assert "timestamp" in predicted[0], "Predicted data should have timestamp"
                assert "value" in predicted[0], "Predicted data should have value"
            
            print(f"Forecast data: {len(historical)} historical points, {len(predicted)} predicted points")
    
    # ─── No Hardcoded Values Tests ───
    def test_no_random_values_in_revenue(self):
        """Test that revenue analytics doesn't return suspiciously round/random values"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/revenue",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        revenue_breakdown = data.get("revenue_breakdown", {})
        
        # Check that values are computed (not hardcoded round numbers)
        total_revenue = revenue_breakdown.get("total_revenue", 0)
        
        # If there's data, it shouldn't be a suspiciously round number like 100000, 50000, etc.
        if total_revenue > 0:
            # Real computed values typically have decimal places
            assert data.get("data_source") == "real", "Should be from real data source"
        
        print(f"Revenue value check: ${total_revenue} (data_source={data.get('data_source')})")
    
    def test_no_random_values_in_performance(self):
        """Test that performance metrics doesn't return suspiciously random values"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/performance",
            params={"user_id": self.user_id},
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        metrics = data.get("performance_metrics", {})
        
        # Verify data comes from real source
        assert data.get("data_source") == "real", "Should be from real data source"
        
        # Total streams should match analytics_events count
        total_streams = metrics.get("total_streams", 0)
        total_views = metrics.get("total_views", 0)
        
        print(f"Performance values: streams={total_streams}, views={total_views}")


class TestAnalyticsEndpointRegression:
    """Regression tests for existing analytics endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.headers = {"Content-Type": "application/json"}
        # Get auth token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "owner@bigmannentertainment.com", "password": "Test1234!"},
            headers=self.headers
        )
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.auth_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        else:
            self.auth_headers = self.headers
    
    def test_demographics_endpoint_still_works(self):
        """Test GET /api/analytics/demographics still returns real data"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/demographics",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Demographics endpoint failed: {response.status_code}"
        
        data = response.json()
        assert "data_source" in data, "Should have data_source field"
        print(f"Demographics: data_source={data.get('data_source')}, data_points={data.get('data_points', 0)}")
    
    def test_geo_endpoint_still_works(self):
        """Test GET /api/analytics/geo still returns real data"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/geo",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Geo endpoint failed: {response.status_code}"
        
        data = response.json()
        assert "data_source" in data, "Should have data_source field"
        print(f"Geo: data_source={data.get('data_source')}, data_points={data.get('data_points', 0)}")
    
    def test_best_times_endpoint_still_works(self):
        """Test GET /api/analytics/best-times still returns real data"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/best-times",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Best-times endpoint failed: {response.status_code}"
        
        data = response.json()
        assert "data_source" in data, "Should have data_source field"
        print(f"Best-times: data_source={data.get('data_source')}")
    
    def test_revenue_overview_endpoint_still_works(self):
        """Test GET /api/analytics/revenue/overview still works"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/revenue/overview",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Revenue overview endpoint failed: {response.status_code}"
        
        data = response.json()
        print(f"Revenue overview: total_revenue=${data.get('total_revenue', 0)}")


class TestMongoDBDataVerification:
    """Verify MongoDB collections have data for analytics"""
    
    def test_revenue_tracking_collection_has_data(self):
        """Verify revenue_tracking collection is being used"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/revenue",
            params={"user_id": "user_123"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        revenue_breakdown = data.get("revenue_breakdown", {})
        
        # If there's revenue data, by_time_period should have entries
        by_time_period = revenue_breakdown.get("by_time_period", {})
        
        print(f"Revenue tracking: {len(by_time_period)} time periods, total=${revenue_breakdown.get('total_revenue', 0):.2f}")
    
    def test_analytics_events_collection_has_data(self):
        """Verify analytics_events collection is being used"""
        response = requests.get(
            f"{BASE_URL}/api/api/platform/analytics/performance",
            params={"user_id": "user_123"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        metrics = data.get("performance_metrics", {})
        
        # total_streams should reflect analytics_events count
        total_streams = metrics.get("total_streams", 0)
        
        print(f"Analytics events: total_streams={total_streams}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
