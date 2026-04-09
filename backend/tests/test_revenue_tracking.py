"""
Revenue Tracking API Tests
Tests for the real MongoDB-backed revenue tracking endpoints:
- GET /api/revenue/overview - Revenue overview with totals, by_platform, by_source, monthly_trend
- GET /api/revenue/transactions - Paginated transactions with filtering
- POST /api/revenue/record - Create new revenue entry
- GET /api/revenue/platform/{platform_id} - Platform-specific breakdown
- DELETE /api/revenue/transactions/{date_key} - Delete transaction
- Authentication required for all endpoints
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestRevenueTrackingAuth:
    """Test authentication requirements for revenue endpoints"""
    
    def test_overview_requires_auth(self):
        """GET /api/revenue/overview should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/revenue/overview")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: /api/revenue/overview requires authentication")
    
    def test_transactions_requires_auth(self):
        """GET /api/revenue/transactions should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/revenue/transactions")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: /api/revenue/transactions requires authentication")
    
    def test_record_requires_auth(self):
        """POST /api/revenue/record should return 401 without token"""
        response = requests.post(f"{BASE_URL}/api/revenue/record", json={
            "platform_id": "spotify",
            "platform_name": "Spotify",
            "source": "streaming",
            "amount": 100.00
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: /api/revenue/record requires authentication")
    
    def test_platform_detail_requires_auth(self):
        """GET /api/revenue/platform/{id} should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/revenue/platform/spotify")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: /api/revenue/platform/{id} requires authentication")


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for testing"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
    data = response.json()
    # Token key is 'access_token' per test_credentials.md
    token = data.get("access_token") or data.get("token")
    assert token, f"No token in response: {data}"
    print(f"PASS: Login successful, got token")
    return token


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestRevenueOverview:
    """Test GET /api/revenue/overview endpoint"""
    
    def test_overview_returns_data(self, auth_headers):
        """Overview should return total_revenue, by_platform, by_source, monthly_trend"""
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify required fields exist
        assert "total_revenue" in data, "Missing total_revenue"
        assert "by_platform" in data, "Missing by_platform"
        assert "by_source" in data, "Missing by_source"
        assert "monthly_trend" in data, "Missing monthly_trend"
        assert "top_earning_content" in data, "Missing top_earning_content"
        assert "total_transactions" in data, "Missing total_transactions"
        
        # Verify data types
        assert isinstance(data["total_revenue"], (int, float)), "total_revenue should be numeric"
        assert isinstance(data["by_platform"], list), "by_platform should be a list"
        assert isinstance(data["by_source"], list), "by_source should be a list"
        assert isinstance(data["monthly_trend"], list), "monthly_trend should be a list"
        
        print(f"PASS: Overview returned total_revenue=${data['total_revenue']}, {len(data['by_platform'])} platforms, {data['total_transactions']} transactions")
    
    def test_overview_platform_structure(self, auth_headers):
        """Each platform in by_platform should have required fields"""
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        if data["by_platform"]:
            platform = data["by_platform"][0]
            assert "platform_id" in platform, "Platform missing platform_id"
            assert "platform_name" in platform, "Platform missing platform_name"
            assert "total" in platform, "Platform missing total"
            assert "count" in platform, "Platform missing count"
            assert "percentage" in platform, "Platform missing percentage"
            print(f"PASS: Platform structure verified - {platform['platform_name']}: ${platform['total']}")
    
    def test_overview_monthly_trend_structure(self, auth_headers):
        """Monthly trend should have month and amount fields"""
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        if data["monthly_trend"]:
            month = data["monthly_trend"][0]
            assert "month" in month, "Month entry missing month field"
            assert "amount" in month, "Month entry missing amount field"
            print(f"PASS: Monthly trend structure verified - {len(data['monthly_trend'])} months")


class TestRevenueTransactions:
    """Test GET /api/revenue/transactions endpoint"""
    
    def test_transactions_returns_list(self, auth_headers):
        """Transactions endpoint should return paginated list"""
        response = requests.get(f"{BASE_URL}/api/revenue/transactions", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "transactions" in data, "Missing transactions field"
        assert "total" in data, "Missing total field"
        assert "limit" in data, "Missing limit field"
        assert "skip" in data, "Missing skip field"
        
        assert isinstance(data["transactions"], list), "transactions should be a list"
        print(f"PASS: Transactions returned {len(data['transactions'])} items, total={data['total']}")
    
    def test_transactions_filter_by_platform(self, auth_headers):
        """Transactions should filter by platform_id"""
        response = requests.get(
            f"{BASE_URL}/api/revenue/transactions?platform_id=spotify",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned transactions should be for spotify
        for tx in data["transactions"]:
            assert tx.get("platform_id") == "spotify", f"Expected spotify, got {tx.get('platform_id')}"
        
        print(f"PASS: Platform filter works - {len(data['transactions'])} spotify transactions")
    
    def test_transactions_filter_by_source(self, auth_headers):
        """Transactions should filter by source"""
        response = requests.get(
            f"{BASE_URL}/api/revenue/transactions?source=streaming",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned transactions should be streaming
        for tx in data["transactions"]:
            assert tx.get("source") == "streaming", f"Expected streaming, got {tx.get('source')}"
        
        print(f"PASS: Source filter works - {len(data['transactions'])} streaming transactions")
    
    def test_transactions_pagination(self, auth_headers):
        """Transactions should support limit and skip"""
        response = requests.get(
            f"{BASE_URL}/api/revenue/transactions?limit=5&skip=0",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["transactions"]) <= 5, "Limit not respected"
        assert data["limit"] == 5, "Limit not returned correctly"
        assert data["skip"] == 0, "Skip not returned correctly"
        
        print(f"PASS: Pagination works - limit=5, got {len(data['transactions'])} transactions")


class TestRecordRevenue:
    """Test POST /api/revenue/record endpoint"""
    
    def test_record_revenue_success(self, auth_headers):
        """Should successfully record a new revenue entry"""
        test_amount = 123.45
        payload = {
            "platform_id": "TEST_platform",
            "platform_name": "TEST Platform",
            "content_id": "TEST_content_001",
            "content_title": "TEST Track",
            "source": "streaming",
            "amount": test_amount,
            "description": "TEST revenue entry"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/revenue/record",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Missing message in response"
        print(f"PASS: Revenue recorded successfully - ${test_amount}")
    
    def test_record_revenue_appears_in_transactions(self, auth_headers):
        """Recorded revenue should appear in transactions list"""
        # Record a unique entry
        unique_id = f"TEST_verify_{int(time.time())}"
        payload = {
            "platform_id": unique_id,
            "platform_name": "TEST Verify Platform",
            "source": "ad_revenue",
            "amount": 999.99,
            "description": "TEST verification entry"
        }
        
        # Record it
        response = requests.post(
            f"{BASE_URL}/api/revenue/record",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        
        # Verify it appears in transactions
        response = requests.get(
            f"{BASE_URL}/api/revenue/transactions?platform_id={unique_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1, "Recorded entry not found in transactions"
        
        # Verify the entry details
        found = False
        for tx in data["transactions"]:
            if tx.get("platform_id") == unique_id:
                assert tx.get("amount") == 999.99, "Amount mismatch"
                assert tx.get("source") == "ad_revenue", "Source mismatch"
                found = True
                break
        
        assert found, "Recorded entry not found with correct details"
        print(f"PASS: Recorded revenue verified in transactions - {unique_id}")
    
    def test_record_revenue_updates_overview(self, auth_headers):
        """Recording revenue should update the overview totals"""
        # Get initial overview
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200
        initial_total = response.json()["total_revenue"]
        initial_tx_count = response.json()["total_transactions"]
        
        # Record new revenue
        payload = {
            "platform_id": "TEST_overview_update",
            "platform_name": "TEST Overview",
            "source": "sync_licensing",
            "amount": 50.00
        }
        response = requests.post(
            f"{BASE_URL}/api/revenue/record",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        
        # Get updated overview
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200
        new_total = response.json()["total_revenue"]
        new_tx_count = response.json()["total_transactions"]
        
        # Verify totals increased
        assert new_total >= initial_total, "Total revenue should increase"
        assert new_tx_count > initial_tx_count, "Transaction count should increase"
        
        print(f"PASS: Overview updated - total: ${initial_total} -> ${new_total}, count: {initial_tx_count} -> {new_tx_count}")


class TestPlatformDetail:
    """Test GET /api/revenue/platform/{platform_id} endpoint"""
    
    def test_platform_detail_returns_data(self, auth_headers):
        """Platform detail should return breakdown for specific platform"""
        # First get overview to find a platform with data
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200
        
        platforms = response.json().get("by_platform", [])
        if not platforms:
            pytest.skip("No platforms with revenue data")
        
        platform_id = platforms[0]["platform_id"]
        
        # Get platform detail
        response = requests.get(
            f"{BASE_URL}/api/revenue/platform/{platform_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "platform_id" in data, "Missing platform_id"
        assert "total_revenue" in data, "Missing total_revenue"
        assert "by_source" in data, "Missing by_source"
        assert "transaction_count" in data, "Missing transaction_count"
        assert "recent_transactions" in data, "Missing recent_transactions"
        
        print(f"PASS: Platform detail for {platform_id} - ${data['total_revenue']}, {data['transaction_count']} transactions")
    
    def test_platform_detail_recent_transactions(self, auth_headers):
        """Platform detail should include recent transactions"""
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        platforms = response.json().get("by_platform", [])
        if not platforms:
            pytest.skip("No platforms with revenue data")
        
        platform_id = platforms[0]["platform_id"]
        
        response = requests.get(
            f"{BASE_URL}/api/revenue/platform/{platform_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        recent = data.get("recent_transactions", [])
        
        # Verify transaction structure if any exist
        if recent:
            tx = recent[0]
            assert "date" in tx, "Transaction missing date"
            assert "amount" in tx, "Transaction missing amount"
            assert "source" in tx, "Transaction missing source"
            print(f"PASS: Recent transactions verified - {len(recent)} transactions for {platform_id}")
        else:
            print(f"PASS: Platform detail returned (no recent transactions)")


class TestRevenueDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_overview_totals_match_transactions(self, auth_headers):
        """Overview total should match sum of transactions"""
        # Get overview
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200
        overview = response.json()
        
        # Get all transactions (up to 200)
        response = requests.get(
            f"{BASE_URL}/api/revenue/transactions?limit=200",
            headers=auth_headers
        )
        assert response.status_code == 200
        tx_data = response.json()
        
        # Calculate sum from transactions
        tx_sum = sum(tx.get("amount", 0) for tx in tx_data["transactions"])
        
        # Compare (allow small floating point difference)
        diff = abs(overview["total_revenue"] - tx_sum)
        # If there are more transactions than we fetched, the sum will be less
        if tx_data["total"] <= 200:
            assert diff < 0.01, f"Total mismatch: overview={overview['total_revenue']}, tx_sum={tx_sum}"
        
        print(f"PASS: Data integrity verified - overview total=${overview['total_revenue']}, tx_sum=${tx_sum:.2f}")
    
    def test_no_mongodb_id_in_responses(self, auth_headers):
        """Responses should not contain MongoDB _id field"""
        # Check overview
        response = requests.get(f"{BASE_URL}/api/revenue/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "_id" not in data, "Overview contains _id"
        
        # Check transactions
        response = requests.get(f"{BASE_URL}/api/revenue/transactions", headers=auth_headers)
        assert response.status_code == 200
        tx_data = response.json()
        for tx in tx_data["transactions"]:
            assert "_id" not in tx, "Transaction contains _id"
        
        print("PASS: No MongoDB _id in responses")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
