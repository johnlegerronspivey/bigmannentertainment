"""
Creator Analytics Tests - Testing anomaly detection, demographics, best times, and revenue tracking
Features:
  - Anomaly Detection (scan, alerts, dismiss)
  - Audience Demographics (age, gender, interests, devices)
  - Best Time to Post (heatmap, recommendations)
  - Geographic Distribution
  - Revenue Tracking (overview, platform detail, record)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for the test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Auth failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access_token in response"
    return data["access_token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestAnalyticsOverview:
    """Test base analytics overview endpoints"""
    
    def test_get_overview(self, api_client):
        """GET /api/analytics/overview - Returns content and engagement stats"""
        response = api_client.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "total_content" in data
        assert "content_by_type" in data
        assert "engagement" in data
        assert "subscription_tier" in data
        print(f"✓ Overview: {data['total_content']} content items, tier: {data['subscription_tier']}")
    
    def test_get_content_performance(self, api_client):
        """GET /api/analytics/content-performance - Returns content with stats"""
        response = api_client.get(f"{BASE_URL}/api/analytics/content-performance")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "items" in data
        print(f"✓ Content Performance: {len(data['items'])} items returned")
    
    def test_get_audience(self, api_client):
        """GET /api/analytics/audience - Returns audience growth data"""
        response = api_client.get(f"{BASE_URL}/api/analytics/audience")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "total_followers" in data
        assert "growth" in data
        print(f"✓ Audience: {data['total_followers']} total followers")


class TestAnomalyDetection:
    """Test AI-powered anomaly detection for metrics"""
    
    def test_run_anomaly_scan(self, api_client):
        """POST /api/analytics/anomalies/scan - Runs anomaly detection scan"""
        response = api_client.post(f"{BASE_URL}/api/analytics/anomalies/scan")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "detected" in data
        assert "anomalies" in data
        assert isinstance(data["anomalies"], list)
        
        # Verify anomaly structure if any detected
        if data["anomalies"]:
            anomaly = data["anomalies"][0]
            assert "metric" in anomaly
            assert "direction" in anomaly
            assert "z_score" in anomaly
            assert "change_pct" in anomaly
            assert "platform_id" in anomaly
            assert anomaly["direction"] in ["spike", "drop"]
            print(f"✓ Anomaly Scan: {data['detected']} anomalies detected, first: {anomaly['platform_id']}/{anomaly['metric']} ({anomaly['direction']})")
        else:
            print(f"✓ Anomaly Scan: {data['detected']} anomalies detected")
    
    def test_get_anomaly_alerts(self, api_client):
        """GET /api/analytics/anomalies - Returns list of anomaly alerts"""
        response = api_client.get(f"{BASE_URL}/api/analytics/anomalies")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        assert isinstance(data["alerts"], list)
        
        # Verify alert structure
        if data["alerts"]:
            alert = data["alerts"][0]
            assert "metric" in alert
            assert "direction" in alert
            assert "severity" in alert
            assert alert["severity"] in ["warning", "critical"]
            print(f"✓ Anomaly Alerts: {data['total']} alerts, first severity: {alert['severity']}")
        else:
            print(f"✓ Anomaly Alerts: {data['total']} alerts")
    
    def test_get_anomaly_alerts_include_dismissed(self, api_client):
        """GET /api/analytics/anomalies?include_dismissed=true - Includes dismissed alerts"""
        response = api_client.get(f"{BASE_URL}/api/analytics/anomalies?include_dismissed=true")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "alerts" in data
        print(f"✓ Anomaly Alerts (with dismissed): {data['total']} total alerts")
    
    def test_dismiss_anomaly_alert(self, api_client):
        """POST /api/analytics/anomalies/dismiss - Dismisses an anomaly alert"""
        # First get alerts to find one to dismiss
        alerts_response = api_client.get(f"{BASE_URL}/api/analytics/anomalies")
        alerts_data = alerts_response.json()
        
        if not alerts_data["alerts"]:
            # Run scan to create alerts
            api_client.post(f"{BASE_URL}/api/analytics/anomalies/scan")
            alerts_response = api_client.get(f"{BASE_URL}/api/analytics/anomalies")
            alerts_data = alerts_response.json()
        
        if alerts_data["alerts"]:
            alert = alerts_data["alerts"][0]
            dismiss_response = api_client.post(
                f"{BASE_URL}/api/analytics/anomalies/dismiss",
                json={"platform_id": alert["platform_id"], "metric": alert["metric"]}
            )
            assert dismiss_response.status_code == 200, f"Failed: {dismiss_response.text}"
            result = dismiss_response.json()
            assert "message" in result
            assert result["message"] == "Alert dismissed"
            print(f"✓ Dismissed anomaly: {alert['platform_id']}/{alert['metric']}")
        else:
            print("✓ Skip dismiss test - no alerts to dismiss")


class TestAudienceDemographics:
    """Test audience demographics endpoints"""
    
    def test_get_demographics(self, api_client):
        """GET /api/analytics/demographics - Returns demographic breakdown"""
        response = api_client.get(f"{BASE_URL}/api/analytics/demographics")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        # Validate structure
        assert "age_groups" in data
        assert "gender_split" in data
        assert "interests" in data
        assert "devices" in data
        
        # Validate age groups structure
        assert isinstance(data["age_groups"], list)
        if data["age_groups"]:
            ag = data["age_groups"][0]
            assert "range" in ag
            assert "percentage" in ag
        
        # Validate gender split structure
        assert isinstance(data["gender_split"], list)
        if data["gender_split"]:
            gs = data["gender_split"][0]
            assert "gender" in gs
            assert "percentage" in gs
        
        # Validate interests structure
        assert isinstance(data["interests"], list)
        if data["interests"]:
            int_item = data["interests"][0]
            assert "category" in int_item
            assert "percentage" in int_item
            assert "affinity_index" in int_item
        
        # Validate devices structure
        assert isinstance(data["devices"], list)
        if data["devices"]:
            dev = data["devices"][0]
            assert "type" in dev
            assert "percentage" in dev
        
        print(f"✓ Demographics: {len(data['age_groups'])} age groups, {len(data['gender_split'])} gender categories")


class TestBestTimesToPost:
    """Test best posting time analysis endpoints"""
    
    def test_get_best_times(self, api_client):
        """GET /api/analytics/best-times - Returns engagement heatmap and recommendations"""
        response = api_client.get(f"{BASE_URL}/api/analytics/best-times")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        # Validate structure
        assert "heatmap" in data
        assert "days" in data
        assert "hours" in data
        assert "top_slots" in data
        assert "recommendations" in data
        
        # Validate heatmap is 7x24 grid
        assert isinstance(data["heatmap"], list)
        assert len(data["heatmap"]) == 7, "Heatmap should have 7 days"
        for day_row in data["heatmap"]:
            assert len(day_row) == 24, "Each day should have 24 hours"
            for val in day_row:
                assert 0 <= val <= 1, "Heatmap values should be normalized 0-1"
        
        # Validate recommendations
        assert isinstance(data["recommendations"], list)
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "day" in rec
            assert "time_range" in rec
            assert "score" in rec
            assert "label" in rec
            assert rec["label"] in ["Peak", "High", "Good"]
        
        print(f"✓ Best Times: 7x24 heatmap, {len(data['recommendations'])} recommendations, top label: {data['recommendations'][0]['label'] if data['recommendations'] else 'N/A'}")


class TestGeographicDistribution:
    """Test geographic audience distribution endpoints"""
    
    def test_get_geo_distribution(self, api_client):
        """GET /api/analytics/geo - Returns country and city distribution"""
        response = api_client.get(f"{BASE_URL}/api/analytics/geo")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        # Validate structure
        assert "countries" in data
        assert "top_cities_us" in data
        assert "total_countries" in data
        assert "primary_market" in data
        
        # Validate countries structure
        assert isinstance(data["countries"], list)
        if data["countries"]:
            country = data["countries"][0]
            assert "code" in country
            assert "name" in country
            assert "percentage" in country
            assert "listeners" in country
        
        # Validate US cities structure
        assert isinstance(data["top_cities_us"], list)
        if data["top_cities_us"]:
            city = data["top_cities_us"][0]
            assert "city" in city
            assert "state" in city
            assert "percentage" in city
        
        print(f"✓ Geo Distribution: {data['total_countries']} countries, primary market: {data['primary_market']} ({data.get('primary_market_pct', 0)}%)")


class TestRevenueTracking:
    """Test revenue tracking endpoints"""
    
    def test_get_revenue_overview(self, api_client):
        """GET /api/analytics/revenue/overview - Returns comprehensive revenue data"""
        response = api_client.get(f"{BASE_URL}/api/analytics/revenue/overview")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        # Validate structure
        assert "total_revenue" in data
        assert "currency" in data
        assert "by_platform" in data
        assert "by_source" in data
        assert "monthly_trend" in data
        assert "top_earning_content" in data
        
        # Validate by_platform structure
        assert isinstance(data["by_platform"], list)
        if data["by_platform"]:
            platform = data["by_platform"][0]
            assert "platform_id" in platform
            assert "total" in platform
            assert "percentage" in platform
        
        # Validate by_source structure
        assert isinstance(data["by_source"], list)
        if data["by_source"]:
            source = data["by_source"][0]
            assert "source" in source
            assert "total" in source
            assert "percentage" in source
        
        # Validate monthly_trend - should be 12 months
        assert isinstance(data["monthly_trend"], list)
        assert len(data["monthly_trend"]) == 12, "Should have 12 months of data"
        if data["monthly_trend"]:
            month = data["monthly_trend"][0]
            assert "month" in month
            assert "amount" in month
        
        print(f"✓ Revenue Overview: ${data['total_revenue']} total, {len(data['by_platform'])} platforms, {len(data['by_source'])} sources")
    
    def test_get_platform_revenue_detail(self, api_client):
        """GET /api/analytics/revenue/platform/{platform_id} - Returns platform-specific revenue"""
        # Test with spotify (common platform in seed data)
        platform_id = "spotify"
        response = api_client.get(f"{BASE_URL}/api/analytics/revenue/platform/{platform_id}")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        # Validate structure
        assert "platform_id" in data
        assert data["platform_id"] == platform_id
        assert "total_revenue" in data
        assert "by_source" in data
        assert "transaction_count" in data
        
        print(f"✓ Platform Revenue ({platform_id}): ${data['total_revenue']}, {data['transaction_count']} transactions")
    
    def test_record_revenue_entry(self, api_client):
        """POST /api/analytics/revenue/record - Records new revenue entry"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "platform_id": "test_platform",
            "platform_name": "Test Platform",
            "content_id": f"test_content_{unique_id}",
            "content_title": f"Test Track {unique_id}",
            "source": "streaming",
            "amount": 12.50,
            "description": "Test revenue record"
        }
        
        response = api_client.post(f"{BASE_URL}/api/analytics/revenue/record", json=payload)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Revenue recorded"
        
        print(f"✓ Record Revenue: Successfully recorded ${payload['amount']} for {payload['content_title']}")


class TestBasicRevenue:
    """Test basic revenue endpoint (legacy)"""
    
    def test_get_basic_revenue(self, api_client):
        """GET /api/analytics/revenue - Returns basic revenue insights"""
        response = api_client.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "total_earnings" in data
        assert "monthly_revenue" in data
        print(f"✓ Basic Revenue: ${data['total_earnings']} total earnings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
