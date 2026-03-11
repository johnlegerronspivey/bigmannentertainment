"""
Distribution Hub API Tests - Testing all 16 endpoints for the Distribution Hub feature.
Tests content management, distribution, delivery tracking, export packages, and platform connections.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"

class TestDistributionHubAPIs:
    """Distribution Hub API endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication for all tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Authenticate
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token") or login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.authenticated = True
        else:
            self.authenticated = False
            pytest.skip("Authentication failed - skipping authenticated tests")
    
    # ─── PLATFORMS TESTS ───
    
    def test_get_platforms_returns_all_categories(self):
        """GET /api/distribution-hub/platforms returns all 51 platforms in 6 categories"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/platforms")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "categories" in data, "Response should have 'categories' field"
        assert "total_platforms" in data, "Response should have 'total_platforms' field"
        
        # Verify 6 categories
        categories = data["categories"]
        expected_categories = ["audio_streaming", "commercial_radio", "video_platforms", "film_movie", "social_media", "podcast"]
        for cat in expected_categories:
            assert cat in categories, f"Category '{cat}' should be present"
        
        # Verify total platforms count is 51
        assert data["total_platforms"] == 51, f"Expected 51 platforms, got {data['total_platforms']}"
        
        # Count platforms across categories
        total_count = sum(len(cat_data["platforms"]) for cat_data in categories.values())
        assert total_count == 51, f"Total platforms in categories should be 51, got {total_count}"
        
        print(f"✓ GET /platforms returns {data['total_platforms']} platforms in {len(categories)} categories")
    
    # ─── CONTENT CRUD TESTS ───
    
    def test_create_content_with_full_metadata(self):
        """POST /api/distribution-hub/content creates content with full metadata"""
        content_data = {
            "title": "TEST_HUB_Track_01",
            "content_type": "audio",
            "description": "Test track for distribution hub testing",
            "artist": "Test Artist Hub",
            "album": "Test Album",
            "genre": "Hip-Hop",
            "release_date": "2026-01-15",
            "tags": ["test", "hub", "distribution"],
            "isrc": "QZ9H8TEST001",
            "upc": "860004340001",
            "copyright_holder": "Big Mann Entertainment",
            "publisher": "BME Publishing",
            "record_label": "Big Mann Records",
            "licensing_type": "exclusive",
            "territory_rights": ["worldwide"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "content" in data, "Response should have 'content' field"
        
        content = data["content"]
        assert content["title"] == content_data["title"], "Title should match"
        assert content["content_type"] == content_data["content_type"], "Content type should match"
        assert "id" in content, "Content should have an ID"
        assert "metadata" in content, "Content should have metadata"
        assert content["metadata"]["basic"]["artist"] == content_data["artist"], "Artist should match"
        assert content["metadata"]["advanced"]["isrc"] == content_data["isrc"], "ISRC should match"
        
        # Store content ID for subsequent tests
        self.__class__.test_content_id = content["id"]
        print(f"✓ POST /content created content with ID: {content['id']}")
    
    def test_get_content_library(self):
        """GET /api/distribution-hub/content returns content library"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/content")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "content" in data, "Response should have 'content' field"
        assert "total" in data, "Response should have 'total' field"
        assert isinstance(data["content"], list), "Content should be a list"
        
        print(f"✓ GET /content returns {data['total']} content items")
    
    def test_get_content_by_id(self):
        """GET /api/distribution-hub/content/{id} returns content details"""
        # First create content to ensure we have an ID
        content_data = {"title": "TEST_HUB_Track_Detail", "content_type": "video"}
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        content_id = create_response.json()["content"]["id"]
        
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/content/{content_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["id"] == content_id, "Content ID should match"
        assert data["title"] == content_data["title"], "Title should match"
        
        print(f"✓ GET /content/{content_id} returns correct content details")
    
    def test_update_content_metadata(self):
        """PUT /api/distribution-hub/content/{id}/metadata updates metadata and rights"""
        # Create content first
        content_data = {"title": "TEST_HUB_Track_Update", "content_type": "audio"}
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        content_id = create_response.json()["content"]["id"]
        
        # Update metadata
        update_data = {
            "title": "TEST_HUB_Track_Updated",
            "basic": {"artist": "Updated Artist", "genre": "R&B"},
            "advanced": {"isrc": "QZ9H8UPDATED", "copyright_holder": "Updated Holder"},
            "rights": {"copyright_info": "2026 Big Mann Entertainment"}
        }
        
        response = self.session.put(f"{BASE_URL}/api/distribution-hub/content/{content_id}/metadata", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "content" in data, "Response should have 'content' field"
        updated_content = data["content"]
        assert updated_content["title"] == update_data["title"], "Title should be updated"
        assert updated_content["metadata"]["basic"]["artist"] == "Updated Artist", "Artist should be updated"
        assert updated_content["metadata"]["advanced"]["isrc"] == "QZ9H8UPDATED", "ISRC should be updated"
        
        print(f"✓ PUT /content/{content_id}/metadata updated successfully")
    
    def test_delete_content(self):
        """DELETE /api/distribution-hub/content/{id} deletes content"""
        # Create content first
        content_data = {"title": "TEST_HUB_Track_Delete", "content_type": "image"}
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        content_id = create_response.json()["content"]["id"]
        
        # Delete content
        response = self.session.delete(f"{BASE_URL}/api/distribution-hub/content/{content_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify deletion
        get_response = self.session.get(f"{BASE_URL}/api/distribution-hub/content/{content_id}")
        assert get_response.status_code == 404, "Deleted content should return 404"
        
        print(f"✓ DELETE /content/{content_id} deleted successfully and verified")
    
    # ─── DISTRIBUTION / DELIVERY TESTS ───
    
    def test_distribute_to_platforms(self):
        """POST /api/distribution-hub/distribute creates deliveries (api_push vs export_package)"""
        # Create content first
        content_data = {"title": "TEST_HUB_Track_Distribute", "content_type": "audio"}
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        content_id = create_response.json()["content"]["id"]
        
        # Distribute to multiple platforms (mix of api_push and export_package)
        distribute_data = {
            "content_id": content_id,
            "platform_ids": ["spotify", "youtube", "soundcloud", "apple_music"],  # mix of methods
            "metadata_overrides": {}
        }
        
        response = self.session.post(f"{BASE_URL}/api/distribution-hub/distribute", json=distribute_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "batch_id" in data, "Response should have 'batch_id'"
        assert "deliveries" in data, "Response should have 'deliveries'"
        assert len(data["deliveries"]) == 4, f"Should have 4 deliveries, got {len(data['deliveries'])}"
        
        # Check delivery methods
        api_push_count = sum(1 for d in data["deliveries"] if d["delivery_method"] == "api_push")
        export_count = sum(1 for d in data["deliveries"] if d["delivery_method"] == "export_package")
        
        assert api_push_count == data["api_push_count"], "API push count should match"
        assert export_count == data["export_package_count"], "Export count should match"
        
        # Store batch ID for subsequent tests
        self.__class__.test_batch_id = data["batch_id"]
        self.__class__.test_delivery_id = data["deliveries"][0]["id"]
        
        print(f"✓ POST /distribute created {len(data['deliveries'])} deliveries (api_push: {api_push_count}, export: {export_count})")
    
    def test_get_deliveries(self):
        """GET /api/distribution-hub/deliveries returns delivery history"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/deliveries")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "deliveries" in data, "Response should have 'deliveries' field"
        assert "total" in data, "Response should have 'total' field"
        assert isinstance(data["deliveries"], list), "Deliveries should be a list"
        
        print(f"✓ GET /deliveries returns {data['total']} deliveries")
    
    def test_get_deliveries_by_status_filter(self):
        """GET /api/distribution-hub/deliveries?status=queued filters by status"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/deliveries?status=queued")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # All returned deliveries should have queued status
        for delivery in data["deliveries"]:
            assert delivery["status"] == "queued", f"Expected status 'queued', got '{delivery['status']}'"
        
        print(f"✓ GET /deliveries?status=queued filters correctly ({data['total']} queued)")
    
    def test_get_delivery_batch(self):
        """GET /api/distribution-hub/deliveries/batch/{batch_id} returns batch details"""
        # First create a distribution to get a batch_id
        content_data = {"title": "TEST_HUB_Track_Batch", "content_type": "audio"}
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        content_id = create_response.json()["content"]["id"]
        
        distribute_data = {"content_id": content_id, "platform_ids": ["tidal", "deezer"]}
        dist_response = self.session.post(f"{BASE_URL}/api/distribution-hub/distribute", json=distribute_data)
        batch_id = dist_response.json()["batch_id"]
        
        # Get batch details
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/deliveries/batch/{batch_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["batch_id"] == batch_id, "Batch ID should match"
        assert "deliveries" in data, "Response should have 'deliveries'"
        assert len(data["deliveries"]) == 2, f"Should have 2 deliveries in batch"
        
        print(f"✓ GET /deliveries/batch/{batch_id[:8]}... returns {data['total']} deliveries")
    
    def test_generate_export_package(self):
        """POST /api/distribution-hub/deliveries/{id}/export generates export package with source_of_truth"""
        # Create content and distribution first
        content_data = {"title": "TEST_HUB_Track_Export", "content_type": "audio", "artist": "Export Test Artist"}
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        content_id = create_response.json()["content"]["id"]
        
        # Distribute to an export_package platform
        distribute_data = {"content_id": content_id, "platform_ids": ["spotify"]}  # Spotify uses export_package
        dist_response = self.session.post(f"{BASE_URL}/api/distribution-hub/distribute", json=distribute_data)
        delivery_id = dist_response.json()["deliveries"][0]["id"]
        
        # Generate export package
        response = self.session.post(f"{BASE_URL}/api/distribution-hub/deliveries/{delivery_id}/export")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "package" in data, "Response should have 'package' field"
        
        package = data["package"]
        assert "source_of_truth" in package, "Package should have 'source_of_truth'"
        assert "package_id" in package, "Package should have 'package_id'"
        assert "content_title" in package, "Package should have 'content_title'"
        assert "metadata" in package, "Package should have 'metadata'"
        assert "rights" in package, "Package should have 'rights'"
        assert "delivery_instructions" in package, "Package should have 'delivery_instructions'"
        
        print(f"✓ POST /deliveries/{delivery_id[:8]}.../export generated package with source_of_truth: {package['source_of_truth']}")
    
    def test_update_delivery_status(self):
        """PUT /api/distribution-hub/deliveries/{id}/status marks delivery as delivered"""
        # Create content and distribution first
        content_data = {"title": "TEST_HUB_Track_Status", "content_type": "video"}
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/content", json=content_data)
        content_id = create_response.json()["content"]["id"]
        
        distribute_data = {"content_id": content_id, "platform_ids": ["youtube"]}  # YouTube uses api_push
        dist_response = self.session.post(f"{BASE_URL}/api/distribution-hub/distribute", json=distribute_data)
        delivery_id = dist_response.json()["deliveries"][0]["id"]
        
        # Update status to delivered
        response = self.session.put(
            f"{BASE_URL}/api/distribution-hub/deliveries/{delivery_id}/status",
            params={"status": "delivered"},
            json={"marked_manually": True}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["delivery"]["status"] == "delivered", "Status should be 'delivered'"
        
        print(f"✓ PUT /deliveries/{delivery_id[:8]}.../status updated to 'delivered'")
    
    # ─── PLATFORM CREDENTIALS TESTS ───
    
    def test_connect_platform(self):
        """POST /api/distribution-hub/platforms/connect saves platform credentials"""
        connect_data = {
            "platform_id": "soundcloud",
            "credentials": {"api_key": "test_soundcloud_key_123", "api_secret": "test_secret"}
        }
        
        response = self.session.post(f"{BASE_URL}/api/distribution-hub/platforms/connect", json=connect_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "connection" in data, "Response should have 'connection' field"
        assert data["connection"]["platform_id"] == "soundcloud", "Platform ID should match"
        assert data["connection"]["connected"] == True, "Should be connected"
        # Credentials should not be returned
        assert "credentials" not in data["connection"], "Credentials should not be exposed"
        
        print(f"✓ POST /platforms/connect connected to {data['connection']['platform_name']}")
    
    def test_get_connected_platforms(self):
        """GET /api/distribution-hub/platforms/connected returns connected platforms"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/platforms/connected")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "connected_platforms" in data, "Response should have 'connected_platforms'"
        assert "total" in data, "Response should have 'total'"
        assert isinstance(data["connected_platforms"], list), "Connected platforms should be a list"
        
        print(f"✓ GET /platforms/connected returns {data['total']} connected platforms")
    
    def test_disconnect_platform(self):
        """DELETE /api/distribution-hub/platforms/{id}/disconnect removes connection"""
        # First connect a platform
        connect_data = {
            "platform_id": "vimeo",
            "credentials": {"api_key": "test_vimeo_key"}
        }
        self.session.post(f"{BASE_URL}/api/distribution-hub/platforms/connect", json=connect_data)
        
        # Disconnect the platform
        response = self.session.delete(f"{BASE_URL}/api/distribution-hub/platforms/vimeo/disconnect")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify disconnection
        connected_response = self.session.get(f"{BASE_URL}/api/distribution-hub/platforms/connected")
        connected = connected_response.json()["connected_platforms"]
        vimeo_connected = any(p["platform_id"] == "vimeo" for p in connected)
        assert not vimeo_connected, "Vimeo should not be in connected platforms"
        
        print(f"✓ DELETE /platforms/vimeo/disconnect removed connection")
    
    # ─── STATS TESTS ───
    
    def test_get_hub_stats(self):
        """GET /api/distribution-hub/stats returns hub dashboard statistics"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check required fields
        required_fields = ["content_count", "total_deliveries", "delivered", "queued", 
                          "export_ready", "failed", "success_rate", "content_types", 
                          "total_platforms_available"]
        
        for field in required_fields:
            assert field in data, f"Stats should have '{field}' field"
        
        # Validate content_types breakdown
        assert "audio" in data["content_types"], "Content types should include 'audio'"
        assert "video" in data["content_types"], "Content types should include 'video'"
        assert "image" in data["content_types"], "Content types should include 'image'"
        assert "film" in data["content_types"], "Content types should include 'film'"
        
        # Verify platform count matches expected
        assert data["total_platforms_available"] == 51, f"Expected 51 platforms, got {data['total_platforms_available']}"
        
        print(f"✓ GET /stats returns dashboard: {data['content_count']} content, {data['total_deliveries']} deliveries, {data['success_rate']}% success")
    
    # ─── FILE UPLOAD TEST ───
    
    def test_upload_content_file(self):
        """POST /api/distribution-hub/upload uploads file and creates content"""
        # Create a simple test file
        import io
        test_file_content = b"fake audio content for testing"
        test_file = io.BytesIO(test_file_content)
        
        files = {"file": ("test_audio.mp3", test_file, "audio/mpeg")}
        data = {
            "title": "TEST_HUB_Upload_Track",
            "content_type": "audio",
            "description": "Uploaded via API test",
            "artist": "Upload Test Artist",
            "genre": "Test Genre"
        }
        
        # Remove Content-Type header for multipart upload
        headers = {"Authorization": self.session.headers["Authorization"]}
        
        response = requests.post(
            f"{BASE_URL}/api/distribution-hub/upload",
            files=files,
            data=data,
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        resp_data = response.json()
        assert "content" in resp_data, "Response should have 'content'"
        assert resp_data["content"]["title"] == data["title"], "Title should match"
        assert resp_data["content"]["file_name"] == "test_audio.mp3", "File name should match"
        assert resp_data["content"]["file_size"] > 0, "File size should be > 0"
        
        print(f"✓ POST /upload created content with file: {resp_data['content']['file_name']}")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
