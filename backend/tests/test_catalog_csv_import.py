"""
Catalog CSV Import Feature Tests
================================
Tests for CSV template download, preview, and import endpoints.
Endpoints tested:
- GET /api/uln/labels/{label_id}/catalog/csv-template
- POST /api/uln/labels/{label_id}/catalog/preview-csv
- POST /api/uln/labels/{label_id}/catalog/import-csv
"""

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"
TEST_LABEL_ID = "BM-LBL-9D0377FB"


class TestCatalogCSVImport:
    """Tests for Catalog CSV Import feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        data = login_response.json()
        token = data.get("access_token") or data.get("token")
        assert token, "No token in login response"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.token = token
        yield
        self.session.close()
    
    # ── CSV Template Download Tests ──────────────────────────────────
    
    def test_csv_template_download_success(self):
        """GET /api/uln/labels/{label_id}/catalog/csv-template - should return CSV template"""
        response = self.session.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/csv-template"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert "text/csv" in response.headers.get("Content-Type", ""), "Expected CSV content type"
        assert "Content-Disposition" in response.headers, "Expected Content-Disposition header"
        
        # Verify CSV content has expected headers
        csv_content = response.text
        assert "title" in csv_content.lower(), "CSV should contain 'title' column"
        assert "type" in csv_content.lower(), "CSV should contain 'type' column"
        assert "artist" in csv_content.lower(), "CSV should contain 'artist' column"
        assert "isrc" in csv_content.lower(), "CSV should contain 'isrc' column"
        assert "upc" in csv_content.lower(), "CSV should contain 'upc' column"
        
        print(f"CSV Template downloaded successfully, size: {len(csv_content)} bytes")
    
    def test_csv_template_requires_auth(self):
        """GET /api/uln/labels/{label_id}/catalog/csv-template - should require authentication"""
        # Create new session without auth
        no_auth_session = requests.Session()
        response = no_auth_session.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/csv-template"
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        no_auth_session.close()
    
    # ── CSV Preview Tests ────────────────────────────────────────────
    
    def test_csv_preview_valid_file(self):
        """POST /api/uln/labels/{label_id}/catalog/preview-csv - should preview valid CSV"""
        csv_content = """title,type,artist,isrc,upc,release_date,genre,status,platforms,streams_total
Test Track 1,single,Test Artist,USRC12345678,012345678901,2026-03-15,Hip-Hop,draft,Spotify;Apple Music,0
Test Album,album,Test Artist,USRC12345679,012345678902,2026-06-01,R&B,pre-release,Spotify;Tidal,0"""
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        
        # Remove Content-Type header for multipart upload
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/preview-csv",
            headers=headers,
            files=files
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert data.get("total_rows") == 2, f"Expected 2 rows, got {data.get('total_rows')}"
        assert data.get("valid_count") == 2, f"Expected 2 valid rows, got {data.get('valid_count')}"
        assert "headers" in data, "Expected headers in response"
        assert "preview_rows" in data, "Expected preview_rows in response"
        
        print(f"Preview successful: {data.get('total_rows')} rows, {data.get('valid_count')} valid")
    
    def test_csv_preview_missing_title(self):
        """POST /api/uln/labels/{label_id}/catalog/preview-csv - should flag rows with missing title"""
        csv_content = """title,type,artist,isrc,upc
,single,Test Artist,USRC12345678,012345678901
Valid Track,single,Test Artist,USRC12345679,012345678902"""
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/preview-csv",
            headers=headers,
            files=files
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert len(data.get("validation_errors", [])) >= 1, "Expected at least 1 validation error"
        
        # Check that the error mentions title
        errors = data.get("validation_errors", [])
        error_text = str(errors)
        assert "title" in error_text.lower(), f"Expected 'title' in error message: {errors}"
        
        print(f"Validation errors correctly detected: {errors}")
    
    def test_csv_preview_empty_file(self):
        """POST /api/uln/labels/{label_id}/catalog/preview-csv - should reject empty CSV"""
        csv_content = """title,type,artist,isrc,upc"""  # Headers only, no data
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/preview-csv",
            headers=headers,
            files=files
        )
        
        assert response.status_code == 400, f"Expected 400 for empty CSV, got {response.status_code}"
        print("Empty CSV correctly rejected")
    
    def test_csv_preview_missing_title_column(self):
        """POST /api/uln/labels/{label_id}/catalog/preview-csv - should reject CSV without title column"""
        csv_content = """type,artist,isrc,upc
single,Test Artist,USRC12345678,012345678901"""
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/preview-csv",
            headers=headers,
            files=files
        )
        
        assert response.status_code == 400, f"Expected 400 for missing title column, got {response.status_code}"
        print("CSV without title column correctly rejected")
    
    def test_csv_preview_non_csv_file(self):
        """POST /api/uln/labels/{label_id}/catalog/preview-csv - should reject non-CSV files"""
        files = {"file": ("test.txt", io.BytesIO(b"not a csv file"), "text/plain")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/preview-csv",
            headers=headers,
            files=files
        )
        
        assert response.status_code == 400, f"Expected 400 for non-CSV file, got {response.status_code}"
        print("Non-CSV file correctly rejected")
    
    # ── CSV Import Tests ─────────────────────────────────────────────
    
    def test_csv_import_success(self):
        """POST /api/uln/labels/{label_id}/catalog/import-csv - should import valid CSV"""
        # Use unique ISRC/UPC to avoid duplicate detection
        import uuid
        unique_id = uuid.uuid4().hex[:8].upper()
        
        csv_content = f"""title,type,artist,isrc,upc,release_date,genre,status,platforms,streams_total
TEST Import Track {unique_id},single,Test Artist,TEST{unique_id}A,TEST{unique_id}01,2026-03-15,Hip-Hop,draft,Spotify;Apple Music,0"""
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/import-csv",
            headers=headers,
            files=files,
            data={"skip_duplicates": "true"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert data.get("imported_count") >= 1, f"Expected at least 1 imported, got {data.get('imported_count')}"
        assert data.get("label_id") == TEST_LABEL_ID, "Expected correct label_id in response"
        
        # Verify imported assets have required fields
        imported = data.get("imported", [])
        if imported:
            asset = imported[0]
            assert "asset_id" in asset, "Imported asset should have asset_id"
            assert "title" in asset, "Imported asset should have title"
        
        print(f"Import successful: {data.get('imported_count')} imported, {data.get('skipped_count')} skipped, {data.get('error_count')} errors")
    
    def test_csv_import_duplicate_detection(self):
        """POST /api/uln/labels/{label_id}/catalog/import-csv - should skip duplicates when skip_duplicates=true"""
        import uuid
        unique_id = uuid.uuid4().hex[:8].upper()
        
        csv_content = f"""title,type,artist,isrc,upc
TEST Duplicate Track {unique_id},single,Test Artist,DUP{unique_id}A,DUP{unique_id}01"""
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # First import
        response1 = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/import-csv",
            headers=headers,
            files=files,
            data={"skip_duplicates": "true"}
        )
        
        assert response1.status_code == 200, f"First import failed: {response1.text}"
        data1 = response1.json()
        assert data1.get("imported_count") == 1, "First import should import 1 asset"
        
        # Second import with same ISRC/UPC - should skip
        files2 = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        response2 = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/import-csv",
            headers=headers,
            files=files2,
            data={"skip_duplicates": "true"}
        )
        
        assert response2.status_code == 200, f"Second import failed: {response2.text}"
        data2 = response2.json()
        assert data2.get("imported_count") == 0, f"Second import should import 0 (duplicate), got {data2.get('imported_count')}"
        assert data2.get("skipped_count") == 1, f"Second import should skip 1, got {data2.get('skipped_count')}"
        
        # Verify skip reason mentions duplicate
        skipped = data2.get("skipped", [])
        if skipped:
            assert "Duplicate" in skipped[0].get("reason", ""), f"Skip reason should mention duplicate: {skipped}"
        
        print(f"Duplicate detection working: first import={data1.get('imported_count')}, second import={data2.get('imported_count')}, skipped={data2.get('skipped_count')}")
    
    def test_csv_import_validation_errors(self):
        """POST /api/uln/labels/{label_id}/catalog/import-csv - should report validation errors"""
        csv_content = """title,type,artist,isrc,upc
,single,Test Artist,USRC12345678,012345678901
Valid Track,single,Test Artist,USRC12345679,012345678902"""
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/import-csv",
            headers=headers,
            files=files,
            data={"skip_duplicates": "true"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert data.get("error_count") >= 1, f"Expected at least 1 error, got {data.get('error_count')}"
        
        errors = data.get("errors", [])
        assert len(errors) >= 1, "Expected errors array with at least 1 error"
        
        print(f"Validation errors correctly reported: {errors}")
    
    def test_csv_import_invalid_label(self):
        """POST /api/uln/labels/{label_id}/catalog/import-csv - should fail for non-existent label"""
        csv_content = """title,type,artist
Test Track,single,Test Artist"""
        
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/INVALID-LABEL-ID/catalog/import-csv",
            headers=headers,
            files=files,
            data={"skip_duplicates": "true"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid label, got {response.status_code}"
        print("Invalid label correctly rejected")
    
    # ── Integration Tests ────────────────────────────────────────────
    
    def test_full_import_workflow(self):
        """Full workflow: download template -> preview -> import"""
        import uuid
        unique_id = uuid.uuid4().hex[:8].upper()
        
        # Step 1: Download template
        template_response = self.session.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/csv-template"
        )
        assert template_response.status_code == 200, "Template download failed"
        print("Step 1: Template downloaded")
        
        # Step 2: Create test CSV based on template format
        csv_content = f"""title,type,artist,isrc,upc,release_date,genre,status,platforms,streams_total
TEST Workflow Track {unique_id},single,Workflow Artist,WF{unique_id}AA,WF{unique_id}001,2026-04-01,Pop,draft,Spotify;Apple Music;YouTube Music,0"""
        
        # Step 3: Preview CSV
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        preview_response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/preview-csv",
            headers=headers,
            files=files
        )
        assert preview_response.status_code == 200, f"Preview failed: {preview_response.text}"
        preview_data = preview_response.json()
        assert preview_data.get("valid_count") == 1, "Preview should show 1 valid row"
        print(f"Step 2: Preview successful - {preview_data.get('valid_count')} valid rows")
        
        # Step 4: Import CSV
        files2 = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        import_response = requests.post(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog/import-csv",
            headers=headers,
            files=files2,
            data={"skip_duplicates": "true"}
        )
        assert import_response.status_code == 200, f"Import failed: {import_response.text}"
        import_data = import_response.json()
        assert import_data.get("imported_count") == 1, "Import should import 1 asset"
        print(f"Step 3: Import successful - {import_data.get('imported_count')} imported")
        
        # Step 5: Verify asset in catalog
        catalog_response = self.session.get(
            f"{BASE_URL}/api/uln/labels/{TEST_LABEL_ID}/catalog"
        )
        assert catalog_response.status_code == 200, "Catalog fetch failed"
        catalog_data = catalog_response.json()
        
        # Find our imported asset
        assets = catalog_data.get("assets", [])
        found = any(f"TEST Workflow Track {unique_id}" in a.get("title", "") for a in assets)
        assert found, f"Imported asset not found in catalog"
        print("Step 4: Asset verified in catalog")
        
        print("Full workflow test PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
