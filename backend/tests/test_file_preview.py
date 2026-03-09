"""
Test File Preview Feature - Content Management Page
Tests for file serving endpoint and content CRUD operations for previews
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for owner account"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Authentication failed: {response.status_code}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get auth headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestFileServingEndpoint:
    """Tests for GET /api/user-content/file/{file_id} - public file serving"""
    
    def test_serve_image_file_returns_correct_content_type(self, auth_headers):
        """Test that image files are served with correct MIME type"""
        # First get list of content to find an image
        response = requests.get(
            f"{BASE_URL}/api/user-content?content_type=image",
            headers=auth_headers
        )
        assert response.status_code == 200
        items = response.json().get("items", [])
        
        if not items:
            pytest.skip("No image content available for testing")
        
        image_item = items[0]
        file_id = image_item["file_id"]
        
        # Test file serving endpoint (no auth required)
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{file_id}")
        assert file_response.status_code == 200
        assert "image/" in file_response.headers.get("content-type", "")
        print(f"Image served with content-type: {file_response.headers.get('content-type')}")
    
    def test_serve_audio_file_returns_correct_content_type(self, auth_headers):
        """Test that audio files are served with correct MIME type"""
        # Get list of audio content
        response = requests.get(
            f"{BASE_URL}/api/user-content?content_type=audio",
            headers=auth_headers
        )
        assert response.status_code == 200
        items = response.json().get("items", [])
        
        if not items:
            pytest.skip("No audio content available for testing")
        
        audio_item = items[0]
        file_id = audio_item["file_id"]
        
        # Test file serving endpoint (no auth required)
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{file_id}")
        assert file_response.status_code == 200
        content_type = file_response.headers.get("content-type", "")
        assert "audio/" in content_type, f"Expected audio/* content-type, got: {content_type}"
        print(f"Audio served with content-type: {content_type}")
    
    def test_serve_nonexistent_file_returns_404(self):
        """Test that non-existent file IDs return 404"""
        response = requests.get(f"{BASE_URL}/api/user-content/file/nonexistent-file-id-12345")
        assert response.status_code == 404
        assert "not found" in response.json().get("detail", "").lower()
    
    def test_file_serving_is_public_no_auth_required(self, auth_headers):
        """Test that file serving doesn't require authentication"""
        # Get a file_id from authenticated content list
        response = requests.get(f"{BASE_URL}/api/user-content", headers=auth_headers)
        assert response.status_code == 200
        items = response.json().get("items", [])
        
        if not items:
            pytest.skip("No content available")
        
        file_id = items[0]["file_id"]
        
        # Access file WITHOUT auth header
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{file_id}")
        assert file_response.status_code == 200, "File serving should not require authentication"


class TestContentListingForPreview:
    """Tests for content listing with file_id for preview generation"""
    
    def test_content_list_includes_file_id(self, auth_headers):
        """Test that content list includes file_id for building preview URLs"""
        response = requests.get(f"{BASE_URL}/api/user-content", headers=auth_headers)
        assert response.status_code == 200
        
        items = response.json().get("items", [])
        if not items:
            pytest.skip("No content available")
        
        for item in items:
            assert "file_id" in item, "Content item must include file_id"
            assert "content_type" in item, "Content item must include content_type"
            assert item["content_type"] in ["audio", "video", "image"], f"Invalid content_type: {item['content_type']}"
    
    def test_content_list_filter_by_type(self, auth_headers):
        """Test filtering content by type for preview rendering"""
        for content_type in ["audio", "image", "video"]:
            response = requests.get(
                f"{BASE_URL}/api/user-content?content_type={content_type}",
                headers=auth_headers
            )
            assert response.status_code == 200
            items = response.json().get("items", [])
            
            # All returned items should match the filter
            for item in items:
                assert item["content_type"] == content_type
    
    def test_content_includes_stats_and_metadata(self, auth_headers):
        """Test that content items include stats, tags, visibility for display"""
        response = requests.get(f"{BASE_URL}/api/user-content", headers=auth_headers)
        assert response.status_code == 200
        
        items = response.json().get("items", [])
        if not items:
            pytest.skip("No content available")
        
        item = items[0]
        # Verify all fields needed for content card display
        assert "title" in item
        assert "description" in item
        assert "tags" in item
        assert "visibility" in item
        assert "stats" in item
        assert "views" in item["stats"]
        assert "downloads" in item["stats"]
        assert "likes" in item["stats"]


class TestUploadWithPreview:
    """Tests for uploading content that can be previewed"""
    
    def test_upload_image_for_preview(self, auth_headers):
        """Test uploading an image file that will have thumbnail preview"""
        # Create a small test PNG (1x1 pixel transparent PNG)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'file': ('TEST_preview_test.png', io.BytesIO(png_data), 'image/png')}
        data = {
            'title': 'TEST_Preview_Image',
            'description': 'Test image for preview feature',
            'tags': 'test,preview,cleanup',
            'visibility': 'public'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-content/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["content_type"] == "image"
        assert "file_id" in result
        
        # Verify the file can be served for preview
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{result['file_id']}")
        assert file_response.status_code == 200
        assert "image/" in file_response.headers.get("content-type", "")
        
        print(f"Uploaded image with file_id: {result['file_id']}")
    
    def test_upload_audio_for_player(self, auth_headers):
        """Test uploading an audio file that will have audio player preview"""
        # Minimal valid MP3 file (ID3 header)
        mp3_data = b'ID3\x04\x00\x00\x00\x00\x00\x00'
        
        files = {'file': ('TEST_preview_audio.mp3', io.BytesIO(mp3_data), 'audio/mpeg')}
        data = {
            'title': 'TEST_Preview_Audio',
            'description': 'Test audio for player feature',
            'tags': 'test,preview,cleanup',
            'visibility': 'public'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-content/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["content_type"] == "audio"
        assert "file_id" in result
        
        # Verify the file can be served for audio player
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{result['file_id']}")
        assert file_response.status_code == 200
        assert "audio/" in file_response.headers.get("content-type", "")
        
        print(f"Uploaded audio with file_id: {result['file_id']}")


class TestContentManagementOperations:
    """Tests for edit and delete operations on content items"""
    
    def test_update_content_metadata(self, auth_headers):
        """Test updating content title/description/tags while preview remains functional"""
        # Get list of content
        response = requests.get(f"{BASE_URL}/api/user-content", headers=auth_headers)
        assert response.status_code == 200
        items = response.json().get("items", [])
        
        if not items:
            pytest.skip("No content available for update test")
        
        # Find a TEST_ item to update
        test_item = next((i for i in items if i.get("title", "").startswith("TEST_")), None)
        if not test_item:
            pytest.skip("No TEST_ content available for update test")
        
        content_id = test_item["id"]
        original_file_id = test_item["file_id"]
        
        # Update metadata - uses /api/user-content/{id} endpoint
        update_response = requests.put(
            f"{BASE_URL}/api/user-content/{content_id}",
            headers=auth_headers,
            json={
                "title": "TEST_Updated_Title",
                "description": "Updated description for preview test",
                "tags": ["updated", "test", "preview"]
            }
        )
        
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["title"] == "TEST_Updated_Title"
        
        # Verify file is still accessible after metadata update
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{original_file_id}")
        assert file_response.status_code == 200, "File should still be accessible after metadata update"
    
    def test_delete_content_removes_file(self, auth_headers):
        """Test that deleting content removes the file (preview no longer works)"""
        # Upload a test file to delete
        mp3_data = b'ID3\x04\x00\x00\x00\x00\x00\x00'
        files = {'file': ('TEST_to_delete.mp3', io.BytesIO(mp3_data), 'audio/mpeg')}
        data = {'title': 'TEST_ToDelete_ForPreview', 'visibility': 'private'}
        
        upload_response = requests.post(
            f"{BASE_URL}/api/user-content/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert upload_response.status_code == 200
        content_id = upload_response.json()["id"]
        file_id = upload_response.json()["file_id"]
        
        # Verify file exists
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{file_id}")
        assert file_response.status_code == 200
        
        # Delete content
        delete_response = requests.delete(
            f"{BASE_URL}/api/user-content/{content_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        
        # Verify file is no longer accessible
        file_response = requests.get(f"{BASE_URL}/api/user-content/file/{file_id}")
        assert file_response.status_code == 404, "File should be removed after content deletion"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
