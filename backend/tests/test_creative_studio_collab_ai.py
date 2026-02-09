"""
Creative Studio Collaboration & AI Assets API Tests
Tests for P0: Enhanced User Collaboration and P1: Generative AI for Creative Assets
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCollabHealth:
    """Collaboration Health endpoint tests"""

    def test_collab_health_returns_healthy(self):
        """GET /api/creative-studio/collab/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/collab/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Creative Studio Collaboration"


class TestAIAssetsHealth:
    """AI Assets Health endpoint tests"""

    def test_ai_assets_health_returns_healthy(self):
        """GET /api/creative-studio/ai-assets/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/ai-assets/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Creative Studio AI Assets"


class TestAITextGeneration:
    """AI Text Generation endpoint tests"""

    def test_generate_text_headline(self):
        """POST /api/creative-studio/ai-assets/generate-text with headline type"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/generate-text",
            json={"prompt": "music streaming platform", "text_type": "headline", "count": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) >= 1
        assert data["text_type"] == "headline"
        assert data["prompt"] == "music streaming platform"

    def test_generate_text_caption(self):
        """POST /api/creative-studio/ai-assets/generate-text with caption type"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/generate-text",
            json={"prompt": "new album release", "text_type": "caption", "count": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) >= 1
        assert data["text_type"] == "caption"

    def test_generate_text_tagline(self):
        """POST /api/creative-studio/ai-assets/generate-text with tagline type"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/generate-text",
            json={"prompt": "indie artist branding", "text_type": "tagline", "count": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["text_type"] == "tagline"


class TestAIColorPalette:
    """AI Color Palette Generation endpoint tests"""

    def test_generate_palette_modern_mood(self):
        """POST /api/creative-studio/ai-assets/generate-palette with modern mood"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/generate-palette",
            json={"prompt": "jazz music brand", "mood": "modern", "count": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "colors" in data
        assert isinstance(data["colors"], list)
        assert len(data["colors"]) >= 1
        assert data["mood"] == "modern"
        # Verify color structure
        for color in data["colors"]:
            assert "name" in color
            assert "hex" in color
            assert "usage" in color
            assert color["hex"].startswith("#")

    def test_generate_palette_warm_mood(self):
        """POST /api/creative-studio/ai-assets/generate-palette with warm mood"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/generate-palette",
            json={"prompt": "summer vibes", "mood": "warm", "count": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "colors" in data
        assert data["mood"] == "warm"

    def test_generate_palette_cool_mood(self):
        """POST /api/creative-studio/ai-assets/generate-palette with cool mood"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/generate-palette",
            json={"prompt": "electronic music", "mood": "cool", "count": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "colors" in data
        assert data["mood"] == "cool"


class TestAILayoutSuggestions:
    """AI Layout Suggestions endpoint tests"""

    def test_suggest_layouts_instagram(self):
        """POST /api/creative-studio/ai-assets/suggest-layouts for instagram_post"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/suggest-layouts",
            json={"platform": "instagram_post"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "layouts" in data
        assert isinstance(data["layouts"], list)
        assert len(data["layouts"]) >= 1
        assert data["platform"] == "instagram_post"
        # Verify layout structure
        for layout in data["layouts"]:
            assert "name" in layout
            assert "description" in layout
            assert "elements" in layout

    def test_suggest_layouts_youtube_thumbnail(self):
        """POST /api/creative-studio/ai-assets/suggest-layouts for youtube_thumbnail"""
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai-assets/suggest-layouts",
            json={"platform": "youtube_thumbnail"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "youtube_thumbnail"
        assert "canvas" in data
        assert data["canvas"]["width"] == 1280
        assert data["canvas"]["height"] == 720


@pytest.fixture(scope="module")
def test_project_id():
    """Get a valid project ID for testing"""
    response = requests.get(f"{BASE_URL}/api/creative-studio/projects")
    if response.status_code == 200:
        data = response.json()
        projects = data.get("projects", [])
        if projects:
            return projects[0]["id"]
    pytest.skip("No projects available for testing collaboration features")


class TestCollaborationActivity:
    """Collaboration Activity Feed endpoint tests"""

    def test_get_activity_feed(self, test_project_id):
        """GET /api/creative-studio/collab/activity/{project_id} returns activities"""
        response = requests.get(
            f"{BASE_URL}/api/creative-studio/collab/activity/{test_project_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert "total" in data


class TestCollaborationVersions:
    """Collaboration Versions endpoint tests"""

    def test_get_versions(self, test_project_id):
        """GET /api/creative-studio/collab/versions/{project_id} returns versions list"""
        response = requests.get(
            f"{BASE_URL}/api/creative-studio/collab/versions/{test_project_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "versions" in data
        assert "total" in data


class TestCollaborationPresence:
    """Collaboration Presence endpoint tests"""

    def test_get_presence(self, test_project_id):
        """GET /api/creative-studio/collab/presence/{project_id} returns online users"""
        response = requests.get(
            f"{BASE_URL}/api/creative-studio/collab/presence/{test_project_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "online_users" in data
        assert "count" in data


class TestCollaborationComments:
    """Collaboration Comments endpoint tests"""

    def test_get_comments(self, test_project_id):
        """GET /api/creative-studio/collab/comments/{project_id} returns comments"""
        response = requests.get(
            f"{BASE_URL}/api/creative-studio/collab/comments/{test_project_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "comments" in data
        assert "total" in data

    def test_add_comment(self, test_project_id):
        """POST /api/creative-studio/collab/comments/{project_id} creates and returns comment"""
        unique_content = f"TEST_Comment_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/collab/comments/{test_project_id}",
            json={
                "content": unique_content,
                "user_id": "test_user",
                "user_name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["content"] == unique_content
        assert data["user_name"] == "Test User"
        assert data["is_resolved"] is False

    def test_add_comment_and_verify_in_list(self, test_project_id):
        """Create comment then GET to verify persistence"""
        unique_content = f"TEST_VerifyPersist_{uuid.uuid4().hex[:8]}"
        
        # Create comment
        create_response = requests.post(
            f"{BASE_URL}/api/creative-studio/collab/comments/{test_project_id}",
            json={
                "content": unique_content,
                "user_id": "test_user",
                "user_name": "Persistence Test"
            }
        )
        assert create_response.status_code == 200
        created = create_response.json()
        comment_id = created["id"]
        
        # Verify in list
        list_response = requests.get(
            f"{BASE_URL}/api/creative-studio/collab/comments/{test_project_id}"
        )
        assert list_response.status_code == 200
        comments = list_response.json()["comments"]
        found = [c for c in comments if c["id"] == comment_id]
        assert len(found) == 1
        assert found[0]["content"] == unique_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
