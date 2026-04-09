"""
Test Suite for De-mocked Platform Modules
Tests: Content Manager, Compliance Center, Sponsorship/Campaigns, Contributor Hub
All endpoints should return data_source='real' and success=True
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://creator-analytics-36.preview.emergentagent.com').rstrip('/')
USER_ID = "user_123"


class TestContentManagerService:
    """Content Manager endpoints - de-mocked from MongoDB (user_content, label_assets)"""

    def test_content_stats_returns_real_data(self):
        """GET /api/platform/content/stats - should return data_source='real'"""
        response = requests.get(f"{BASE_URL}/api/platform/content/stats?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "stats" in data, "Response should contain 'stats' key"
        
        stats = data["stats"]
        assert "total_assets" in stats, "Stats should contain total_assets"
        assert "by_type" in stats, "Stats should contain by_type"
        assert "by_status" in stats, "Stats should contain by_status"
        print(f"✅ Content stats: total_assets={stats.get('total_assets')}, data_source=real")

    def test_content_assets_returns_real_data(self):
        """GET /api/platform/content/assets - should return assets from user_content and label_assets"""
        response = requests.get(f"{BASE_URL}/api/platform/content/assets?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "assets" in data, "Response should contain 'assets' key"
        assert "total" in data, "Response should contain 'total' key"
        
        print(f"✅ Content assets: total={data.get('total')}, assets_returned={len(data.get('assets', []))}")

    def test_content_folders_returns_real_data(self):
        """GET /api/platform/content/folders - should return virtual folders grouped by content type"""
        response = requests.get(f"{BASE_URL}/api/platform/content/folders?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "folders" in data, "Response should contain 'folders' key"
        
        print(f"✅ Content folders: count={len(data.get('folders', []))}")

    def test_content_search_returns_real_data(self):
        """GET /api/platform/content/search - search works across collections"""
        response = requests.get(f"{BASE_URL}/api/platform/content/search?query=test&user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "results" in data, "Response should contain 'results' key"
        
        print(f"✅ Content search: results={len(data.get('results', []))}, query='test'")


class TestComplianceCenterService:
    """Compliance Center endpoints - de-mocked from MongoDB (compliance_documents, compliance_audit_logs, label_rights)"""

    def test_compliance_status_returns_real_data(self):
        """GET /api/platform/compliance/status - should return real compliance data from DB"""
        response = requests.get(f"{BASE_URL}/api/platform/compliance/status?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "overall_compliance" in data, "Response should contain 'overall_compliance' key"
        
        compliance = data["overall_compliance"]
        assert "score" in compliance, "Compliance should contain score"
        assert "status" in compliance, "Compliance should contain status"
        
        print(f"✅ Compliance status: score={compliance.get('score')}, status={compliance.get('status')}")

    def test_compliance_alerts_returns_real_data(self):
        """GET /api/platform/compliance/alerts - should return alerts computed from real data"""
        response = requests.get(f"{BASE_URL}/api/platform/compliance/alerts?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "alerts" in data, "Response should contain 'alerts' key"
        assert "total" in data, "Response should contain 'total' key"
        
        print(f"✅ Compliance alerts: total={data.get('total')}, alerts_returned={len(data.get('alerts', []))}")


class TestSponsorshipCampaignsService:
    """Sponsorship & Campaigns endpoints - de-mocked from MongoDB (campaigns, campaign_performance, partnerships)"""

    def test_campaigns_returns_real_data(self):
        """GET /api/platform/sponsorship/campaigns - should return 12 real campaigns from DB"""
        response = requests.get(f"{BASE_URL}/api/platform/sponsorship/campaigns?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "campaigns" in data, "Response should contain 'campaigns' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "summary" in data, "Response should contain 'summary' key"
        
        print(f"✅ Campaigns: total={data.get('total')}, campaigns_returned={len(data.get('campaigns', []))}")

    def test_campaign_analytics_returns_real_data(self):
        """GET /api/platform/sponsorship/analytics - should return real campaign analytics from DB"""
        response = requests.get(f"{BASE_URL}/api/platform/sponsorship/analytics?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "analytics" in data, "Response should contain 'analytics' key"
        
        analytics = data["analytics"]
        assert "overview" in analytics, "Analytics should contain overview"
        assert "performance_metrics" in analytics, "Analytics should contain performance_metrics"
        
        print(f"✅ Campaign analytics: total_campaigns={analytics.get('overview', {}).get('total_campaigns')}")

    def test_sponsorship_opportunities_returns_real_data(self):
        """GET /api/platform/sponsorship/opportunities - should return 8 real partnership opportunities"""
        response = requests.get(f"{BASE_URL}/api/platform/sponsorship/opportunities?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "opportunities" in data, "Response should contain 'opportunities' key"
        assert "total" in data, "Response should contain 'total' key"
        
        print(f"✅ Sponsorship opportunities: total={data.get('total')}")


class TestContributorHubService:
    """Contributor Hub endpoints - de-mocked from MongoDB (label_members, creator_profiles, royalty_earnings)"""

    def test_contributors_search_returns_real_data(self):
        """GET /api/platform/contributors/search - should return contributors from label_members"""
        response = requests.get(f"{BASE_URL}/api/platform/contributors/search?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "contributors" in data, "Response should contain 'contributors' key"
        assert "total" in data, "Response should contain 'total' key"
        
        print(f"✅ Contributors search: total={data.get('total')}, contributors_returned={len(data.get('contributors', []))}")

    def test_contributor_stats_returns_real_data(self):
        """GET /api/platform/contributors/stats - should return real contributor stats with earnings"""
        response = requests.get(f"{BASE_URL}/api/platform/contributors/stats?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "stats" in data, "Response should contain 'stats' key"
        
        stats = data["stats"]
        assert "profile" in stats, "Stats should contain profile"
        assert "earnings" in stats, "Stats should contain earnings"
        assert "activity" in stats, "Stats should contain activity"
        
        print(f"✅ Contributor stats: total_earned={stats.get('earnings', {}).get('total_earned')}")

    def test_contributor_collaborations_returns_real_data(self):
        """GET /api/platform/contributors/collaborations - should return 8 collaborations"""
        response = requests.get(f"{BASE_URL}/api/platform/contributors/collaborations?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "collaborations" in data, "Response should contain 'collaborations' key"
        assert "total" in data, "Response should contain 'total' key"
        
        print(f"✅ Collaborations: total={data.get('total')}")

    def test_contributor_requests_returns_real_data(self):
        """GET /api/platform/contributors/requests - should return 8 collaboration requests"""
        response = requests.get(f"{BASE_URL}/api/platform/contributors/requests?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "requests" in data, "Response should contain 'requests' key"
        assert "total" in data, "Response should contain 'total' key"
        
        print(f"✅ Collaboration requests: total={data.get('total')}")

    def test_contributor_payments_returns_real_data(self):
        """GET /api/platform/contributors/payments - should return real payments from royalty_earnings"""
        response = requests.get(f"{BASE_URL}/api/platform/contributors/payments?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        assert "payments" in data, "Response should contain 'payments' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "summary" in data, "Response should contain 'summary' key"
        
        print(f"✅ Contributor payments: total={data.get('total')}, total_earned={data.get('summary', {}).get('total_earned')}")


class TestAnalyticsEndpointsRegression:
    """Regression tests for analytics endpoints (tested in iteration_114)"""

    def test_analytics_revenue_still_works(self):
        """GET /api/platform/analytics/revenue - regression test"""
        response = requests.get(f"{BASE_URL}/api/platform/analytics/revenue?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        print(f"✅ Analytics revenue: data_source=real")

    def test_analytics_performance_still_works(self):
        """GET /api/platform/analytics/performance - regression test"""
        response = requests.get(f"{BASE_URL}/api/platform/analytics/performance?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        print(f"✅ Analytics performance: data_source=real")

    def test_analytics_roi_still_works(self):
        """GET /api/platform/analytics/roi - regression test"""
        response = requests.get(f"{BASE_URL}/api/platform/analytics/roi?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        print(f"✅ Analytics ROI: data_source=real")

    def test_analytics_trends_still_works(self):
        """GET /api/platform/analytics/trends - regression test"""
        response = requests.get(f"{BASE_URL}/api/platform/analytics/trends?user_id={USER_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        print(f"✅ Analytics trends: data_source=real")

    def test_analytics_forecast_still_works(self):
        """POST /api/platform/analytics/forecast - regression test"""
        response = requests.post(
            f"{BASE_URL}/api/platform/analytics/forecast?user_id={USER_ID}&metric_type=revenue&time_frame=month"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert data.get("data_source") == "real", f"Expected data_source='real', got {data.get('data_source')}"
        print(f"✅ Analytics forecast: data_source=real")


class TestNoMongoIdInResponses:
    """Verify no MongoDB _id fields appear in any response"""

    def test_content_assets_no_mongo_id(self):
        """Content assets should not contain _id"""
        response = requests.get(f"{BASE_URL}/api/platform/content/assets?user_id={USER_ID}")
        data = response.json()
        
        for asset in data.get("assets", []):
            assert "_id" not in asset, f"Asset contains _id: {asset}"
        print(f"✅ Content assets: no _id fields found")

    def test_campaigns_no_mongo_id(self):
        """Campaigns should not contain _id"""
        response = requests.get(f"{BASE_URL}/api/platform/sponsorship/campaigns?user_id={USER_ID}")
        data = response.json()
        
        for campaign in data.get("campaigns", []):
            assert "_id" not in campaign, f"Campaign contains _id: {campaign}"
        print(f"✅ Campaigns: no _id fields found")

    def test_contributors_no_mongo_id(self):
        """Contributors should not contain _id"""
        response = requests.get(f"{BASE_URL}/api/platform/contributors/search?user_id={USER_ID}")
        data = response.json()
        
        for contributor in data.get("contributors", []):
            assert "_id" not in contributor, f"Contributor contains _id: {contributor}"
        print(f"✅ Contributors: no _id fields found")

    def test_payments_no_mongo_id(self):
        """Payments should not contain _id"""
        response = requests.get(f"{BASE_URL}/api/platform/contributors/payments?user_id={USER_ID}")
        data = response.json()
        
        for payment in data.get("payments", []):
            assert "_id" not in payment, f"Payment contains _id: {payment}"
        print(f"✅ Payments: no _id fields found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
