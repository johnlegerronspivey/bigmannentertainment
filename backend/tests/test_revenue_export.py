"""
Revenue Export CSV Feature Tests
Tests the GET /api/revenue/export endpoint for CSV export functionality
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestRevenueExportAuth:
    """Test authentication requirements for export endpoint"""
    
    def test_export_without_auth_returns_401_or_403(self):
        """Export endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/revenue/export")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Export without auth returns {response.status_code}")


class TestRevenueExportBasic:
    """Test basic export functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        token = data.get("access_token")
        assert token, f"No access_token in response: {data}"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_export_returns_200_with_csv_content_type(self, auth_headers):
        """Export should return 200 with text/csv content type"""
        response = requests.get(f"{BASE_URL}/api/revenue/export", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got {content_type}"
        print(f"✓ Export returns 200 with Content-Type: {content_type}")
    
    def test_export_has_content_disposition_header(self, auth_headers):
        """Export should have Content-Disposition header for download"""
        response = requests.get(f"{BASE_URL}/api/revenue/export", headers=auth_headers)
        assert response.status_code == 200
        
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment in Content-Disposition, got {content_disp}"
        assert "filename" in content_disp, f"Expected filename in Content-Disposition, got {content_disp}"
        assert ".csv" in content_disp, f"Expected .csv in filename, got {content_disp}"
        print(f"✓ Export has Content-Disposition: {content_disp}")
    
    def test_export_csv_has_correct_header_row(self, auth_headers):
        """Export CSV should have correct header columns"""
        response = requests.get(f"{BASE_URL}/api/revenue/export", headers=auth_headers)
        assert response.status_code == 200
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        assert len(lines) >= 1, "CSV should have at least header row"
        
        header = lines[0]
        expected_columns = ["Date", "Platform", "Content Title", "Source", "Amount (USD)", "Currency", "Description"]
        for col in expected_columns:
            assert col in header, f"Missing column '{col}' in header: {header}"
        print(f"✓ CSV header row: {header}")
    
    def test_export_csv_has_data_rows(self, auth_headers):
        """Export CSV should have data rows (user has seeded data)"""
        response = requests.get(f"{BASE_URL}/api/revenue/export", headers=auth_headers)
        assert response.status_code == 200
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        assert len(lines) > 1, f"CSV should have data rows, only got {len(lines)} lines"
        
        # Check first data row has expected format
        data_row = lines[1]
        columns = data_row.split(',')
        assert len(columns) >= 7, f"Data row should have 7 columns, got {len(columns)}: {data_row}"
        print(f"✓ CSV has {len(lines) - 1} data rows")
        print(f"  Sample row: {data_row[:100]}...")


class TestRevenueExportFilters:
    """Test export filtering functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_export_filter_by_platform_id(self, auth_headers):
        """Export with platform_id filter should only include that platform"""
        response = requests.get(
            f"{BASE_URL}/api/revenue/export?platform_id=spotify",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        
        # Check that all data rows contain Spotify (case-insensitive check)
        if len(lines) > 1:
            for i, line in enumerate(lines[1:], start=2):
                # Platform is the second column
                lower_line = line.lower()
                assert "spotify" in lower_line, f"Row {i} should contain Spotify: {line}"
            print(f"✓ Platform filter works: {len(lines) - 1} Spotify transactions")
        else:
            print("✓ Platform filter works (no Spotify transactions found)")
    
    def test_export_filter_by_source(self, auth_headers):
        """Export with source filter should only include that source"""
        response = requests.get(
            f"{BASE_URL}/api/revenue/export?source=ad_revenue",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        
        # Check that all data rows contain ad_revenue
        if len(lines) > 1:
            for i, line in enumerate(lines[1:], start=2):
                lower_line = line.lower()
                assert "ad_revenue" in lower_line or "ad revenue" in lower_line, f"Row {i} should contain ad_revenue: {line}"
            print(f"✓ Source filter works: {len(lines) - 1} ad_revenue transactions")
        else:
            print("✓ Source filter works (no ad_revenue transactions found)")
    
    def test_export_filter_by_platform_and_source(self, auth_headers):
        """Export with both platform_id and source filters"""
        response = requests.get(
            f"{BASE_URL}/api/revenue/export?platform_id=spotify&source=streaming",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        
        if len(lines) > 1:
            for i, line in enumerate(lines[1:], start=2):
                lower_line = line.lower()
                assert "spotify" in lower_line, f"Row {i} should contain Spotify: {line}"
                assert "streaming" in lower_line, f"Row {i} should contain streaming: {line}"
            print(f"✓ Combined filters work: {len(lines) - 1} Spotify streaming transactions")
        else:
            print("✓ Combined filters work (no matching transactions)")
    
    def test_export_filter_by_date_range(self, auth_headers):
        """Export with date_from and date_to filters"""
        response = requests.get(
            f"{BASE_URL}/api/revenue/export?date_from=2025-01-01&date_to=2025-12-31",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        
        # Just verify it returns valid CSV
        assert len(lines) >= 1, "Should have at least header row"
        print(f"✓ Date range filter works: {len(lines) - 1} transactions in 2025")


class TestRevenueExportDataIntegrity:
    """Test data integrity of exported CSV"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_export_matches_transactions_count(self, auth_headers):
        """Export row count should match transactions API count"""
        # Get transactions count
        tx_response = requests.get(
            f"{BASE_URL}/api/revenue/transactions?limit=1",
            headers=auth_headers
        )
        assert tx_response.status_code == 200
        total_transactions = tx_response.json().get("total", 0)
        
        # Get export
        export_response = requests.get(
            f"{BASE_URL}/api/revenue/export",
            headers=auth_headers
        )
        assert export_response.status_code == 200
        
        csv_lines = export_response.text.strip().split('\n')
        export_count = len(csv_lines) - 1  # Minus header
        
        assert export_count == total_transactions, \
            f"Export count ({export_count}) should match transactions total ({total_transactions})"
        print(f"✓ Export count matches: {export_count} transactions")
    
    def test_export_filtered_matches_transactions_filtered(self, auth_headers):
        """Filtered export count should match filtered transactions count"""
        # Get filtered transactions count
        tx_response = requests.get(
            f"{BASE_URL}/api/revenue/transactions?platform_id=spotify&limit=1",
            headers=auth_headers
        )
        assert tx_response.status_code == 200
        total_filtered = tx_response.json().get("total", 0)
        
        # Get filtered export
        export_response = requests.get(
            f"{BASE_URL}/api/revenue/export?platform_id=spotify",
            headers=auth_headers
        )
        assert export_response.status_code == 200
        
        csv_lines = export_response.text.strip().split('\n')
        export_count = len(csv_lines) - 1
        
        assert export_count == total_filtered, \
            f"Filtered export count ({export_count}) should match filtered transactions ({total_filtered})"
        print(f"✓ Filtered export count matches: {export_count} Spotify transactions")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
