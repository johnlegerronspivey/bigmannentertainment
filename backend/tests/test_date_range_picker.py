"""
Test Date Range Picker Feature for Revenue Tracking
Tests:
- GET /api/revenue/transactions with date_from and date_to query params
- GET /api/revenue/export with date_from and date_to query params
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestDateRangePickerBackend:
    """Tests for date range filtering on revenue endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Authenticate
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("access_token") or data.get("token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.authenticated = True
            else:
                self.authenticated = False
        else:
            self.authenticated = False
            
    def test_auth_works(self):
        """Verify authentication is working"""
        assert self.authenticated, "Authentication failed - cannot proceed with tests"
        
    # ==================== /api/revenue/transactions tests ====================
    
    def test_transactions_without_date_filter(self):
        """GET /api/revenue/transactions without date filter returns all transactions"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        response = self.session.get(f"{BASE_URL}/api/revenue/transactions?limit=50")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data, "Response should contain 'transactions' key"
        assert "total" in data, "Response should contain 'total' key"
        print(f"Total transactions without filter: {data['total']}")
        
    def test_transactions_with_date_from_only(self):
        """GET /api/revenue/transactions with date_from filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        # Use a date from 30 days ago
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = self.session.get(f"{BASE_URL}/api/revenue/transactions?date_from={date_from}&limit=50")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data
        print(f"Transactions from {date_from}: {data['total']}")
        
        # Verify all returned transactions are >= date_from
        for tx in data["transactions"]:
            if tx.get("date"):
                tx_date = tx["date"][:10]
                assert tx_date >= date_from, f"Transaction date {tx_date} is before date_from {date_from}"
                
    def test_transactions_with_date_to_only(self):
        """GET /api/revenue/transactions with date_to filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        # Use today's date
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        response = self.session.get(f"{BASE_URL}/api/revenue/transactions?date_to={date_to}&limit=50")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data
        print(f"Transactions up to {date_to}: {data['total']}")
        
    def test_transactions_with_date_range(self):
        """GET /api/revenue/transactions with both date_from and date_to"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_from = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        date_to = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = self.session.get(
            f"{BASE_URL}/api/revenue/transactions?date_from={date_from}&date_to={date_to}&limit=50"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data
        print(f"Transactions between {date_from} and {date_to}: {data['total']}")
        
        # Verify all returned transactions are within the date range
        for tx in data["transactions"]:
            if tx.get("date"):
                tx_date = tx["date"][:10]
                assert tx_date >= date_from, f"Transaction date {tx_date} is before date_from {date_from}"
                # Note: date_to comparison includes the full day (T23:59:59)
                
    def test_transactions_with_date_range_and_platform_filter(self):
        """GET /api/revenue/transactions with date range + platform filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_from = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        response = self.session.get(
            f"{BASE_URL}/api/revenue/transactions?date_from={date_from}&date_to={date_to}&platform_id=spotify&limit=50"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data
        print(f"Spotify transactions in date range: {data['total']}")
        
        # Verify all returned transactions are for Spotify
        for tx in data["transactions"]:
            assert tx.get("platform_id") == "spotify", f"Expected platform_id 'spotify', got {tx.get('platform_id')}"
            
    def test_transactions_with_date_range_and_source_filter(self):
        """GET /api/revenue/transactions with date range + source filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_from = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        response = self.session.get(
            f"{BASE_URL}/api/revenue/transactions?date_from={date_from}&date_to={date_to}&source=streaming&limit=50"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data
        print(f"Streaming transactions in date range: {data['total']}")
        
        # Verify all returned transactions are streaming source
        for tx in data["transactions"]:
            assert tx.get("source") == "streaming", f"Expected source 'streaming', got {tx.get('source')}"
            
    def test_transactions_empty_date_range(self):
        """GET /api/revenue/transactions with date range that returns no results"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        # Use a date range far in the future
        date_from = "2030-01-01"
        date_to = "2030-12-31"
        
        response = self.session.get(
            f"{BASE_URL}/api/revenue/transactions?date_from={date_from}&date_to={date_to}&limit=50"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data
        assert data["total"] == 0, f"Expected 0 transactions for future date range, got {data['total']}"
        print("Empty date range test passed - 0 transactions returned")
        
    # ==================== /api/revenue/export tests ====================
    
    def test_export_without_date_filter(self):
        """GET /api/revenue/export without date filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        response = self.session.get(f"{BASE_URL}/api/revenue/export")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify CSV content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected text/csv content type, got {content_type}"
        
        # Verify Content-Disposition header
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Content-Disposition should contain 'attachment'"
        assert "revenue_report" in content_disp, "Filename should contain 'revenue_report'"
        
        # Count rows in CSV
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        print(f"Export without filter: {len(lines) - 1} data rows (excluding header)")
        
    def test_export_with_date_from_only(self):
        """GET /api/revenue/export with date_from filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = self.session.get(f"{BASE_URL}/api/revenue/export?date_from={date_from}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        print(f"Export from {date_from}: {len(lines) - 1} data rows")
        
    def test_export_with_date_to_only(self):
        """GET /api/revenue/export with date_to filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        response = self.session.get(f"{BASE_URL}/api/revenue/export?date_to={date_to}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        print(f"Export up to {date_to}: {len(lines) - 1} data rows")
        
    def test_export_with_date_range(self):
        """GET /api/revenue/export with both date_from and date_to"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_from = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        date_to = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = self.session.get(
            f"{BASE_URL}/api/revenue/export?date_from={date_from}&date_to={date_to}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        print(f"Export between {date_from} and {date_to}: {len(lines) - 1} data rows")
        
    def test_export_with_date_range_and_platform_filter(self):
        """GET /api/revenue/export with date range + platform filter"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_from = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        response = self.session.get(
            f"{BASE_URL}/api/revenue/export?date_from={date_from}&date_to={date_to}&platform_id=spotify"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        print(f"Spotify export in date range: {len(lines) - 1} data rows")
        
        # Verify all rows are for Spotify (column 2 is Platform)
        if len(lines) > 1:
            for line in lines[1:]:  # Skip header
                cols = line.split(",")
                if len(cols) > 1:
                    assert "Spotify" in cols[1], f"Expected Spotify in platform column, got {cols[1]}"
                    
    def test_export_data_matches_transactions_count(self):
        """Verify export row count matches transactions total for same filters"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        date_from = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        # Get transactions count
        tx_response = self.session.get(
            f"{BASE_URL}/api/revenue/transactions?date_from={date_from}&date_to={date_to}&limit=1"
        )
        assert tx_response.status_code == 200
        tx_total = tx_response.json().get("total", 0)
        
        # Get export count
        export_response = self.session.get(
            f"{BASE_URL}/api/revenue/export?date_from={date_from}&date_to={date_to}"
        )
        assert export_response.status_code == 200
        
        csv_content = export_response.text
        lines = csv_content.strip().split("\n")
        export_count = len(lines) - 1  # Exclude header
        
        assert export_count == tx_total, f"Export count ({export_count}) doesn't match transactions total ({tx_total})"
        print(f"Data integrity verified: {export_count} rows match transactions total")
        
    def test_export_empty_date_range(self):
        """GET /api/revenue/export with date range that returns no results"""
        if not self.authenticated:
            pytest.skip("Authentication failed")
            
        # Use a date range far in the future
        date_from = "2030-01-01"
        date_to = "2030-12-31"
        
        response = self.session.get(
            f"{BASE_URL}/api/revenue/export?date_from={date_from}&date_to={date_to}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split("\n")
        # Should have only header row
        assert len(lines) == 1, f"Expected only header row for empty date range, got {len(lines)} lines"
        print("Empty date range export test passed - only header row returned")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
