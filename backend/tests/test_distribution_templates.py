"""
Distribution Hub Templates API Tests - Testing the new Distribution Templates feature.
Tests system templates (6 pre-built) and custom template CRUD operations.
System template IDs: tpl_all_radio, tpl_major_streaming, tpl_social_blast, tpl_video_everywhere, tpl_film_distribution, tpl_podcast_push
Custom template IDs start with: tpl_custom_
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"

# Expected system templates
SYSTEM_TEMPLATE_IDS = [
    "tpl_all_radio",
    "tpl_major_streaming", 
    "tpl_social_blast",
    "tpl_video_everywhere",
    "tpl_film_distribution",
    "tpl_podcast_push"
]


class TestDistributionTemplates:
    """Distribution Templates API endpoint tests"""
    
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
    
    # ─── GET TEMPLATES TESTS ───
    
    def test_get_templates_returns_system_and_custom(self):
        """GET /api/distribution-hub/templates returns 6 system + any custom templates"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "templates" in data, "Response should have 'templates' field"
        assert "system_count" in data, "Response should have 'system_count' field"
        assert "custom_count" in data, "Response should have 'custom_count' field"
        
        # Should have exactly 6 system templates
        assert data["system_count"] == 6, f"Expected 6 system templates, got {data['system_count']}"
        
        # Verify all system templates are present
        template_ids = [t["id"] for t in data["templates"]]
        for sys_id in SYSTEM_TEMPLATE_IDS:
            assert sys_id in template_ids, f"System template '{sys_id}' should be present"
        
        print(f"✓ GET /templates returns {data['system_count']} system + {data['custom_count']} custom templates")
    
    def test_get_templates_system_templates_have_correct_structure(self):
        """Verify system templates have correct structure with platform_ids, descriptions, icons"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates")
        assert response.status_code == 200
        
        data = response.json()
        system_templates = [t for t in data["templates"] if t.get("is_system")]
        
        for tpl in system_templates:
            assert "id" in tpl, f"Template should have 'id'"
            assert "name" in tpl, f"Template {tpl.get('id')} should have 'name'"
            assert "description" in tpl, f"Template {tpl.get('id')} should have 'description'"
            assert "icon" in tpl, f"Template {tpl.get('id')} should have 'icon'"
            assert "is_system" in tpl and tpl["is_system"] == True, f"Template {tpl.get('id')} should have is_system=True"
            assert "platform_ids" in tpl, f"Template {tpl.get('id')} should have 'platform_ids'"
            assert isinstance(tpl["platform_ids"], list), f"platform_ids should be a list"
            assert len(tpl["platform_ids"]) > 0, f"Template {tpl.get('id')} should have at least 1 platform"
            assert "platform_count" in tpl, f"Template {tpl.get('id')} should have 'platform_count'"
            assert tpl["platform_count"] == len(tpl["platform_ids"]), f"platform_count should match platform_ids length"
        
        print(f"✓ All {len(system_templates)} system templates have correct structure")
    
    def test_get_templates_verify_all_radio_template(self):
        """Verify 'All Radio Stations' template has 6 commercial radio platforms"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates")
        assert response.status_code == 200
        
        data = response.json()
        all_radio = next((t for t in data["templates"] if t["id"] == "tpl_all_radio"), None)
        assert all_radio is not None, "tpl_all_radio template should exist"
        
        expected_platforms = ["terrestrial_radio", "bbc_radio", "siriusxm", "radio_one", "cumulus_media", "entercom_audacy"]
        assert len(all_radio["platform_ids"]) == 6, f"All Radio should have 6 platforms, got {len(all_radio['platform_ids'])}"
        for pid in expected_platforms:
            assert pid in all_radio["platform_ids"], f"Platform '{pid}' should be in All Radio template"
        
        print(f"✓ tpl_all_radio has correct 6 radio platforms")
    
    def test_get_templates_verify_major_streaming_template(self):
        """Verify 'Major Streaming' template has top audio streaming services"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates")
        assert response.status_code == 200
        
        data = response.json()
        major_streaming = next((t for t in data["templates"] if t["id"] == "tpl_major_streaming"), None)
        assert major_streaming is not None, "tpl_major_streaming template should exist"
        
        expected_platforms = ["spotify", "apple_music", "amazon_music", "tidal", "deezer", "pandora", "soundcloud"]
        assert len(major_streaming["platform_ids"]) == 7, f"Major Streaming should have 7 platforms, got {len(major_streaming['platform_ids'])}"
        for pid in expected_platforms:
            assert pid in major_streaming["platform_ids"], f"Platform '{pid}' should be in Major Streaming template"
        
        print(f"✓ tpl_major_streaming has correct 7 streaming platforms")
    
    # ─── GET SINGLE TEMPLATE TESTS ───
    
    def test_get_system_template_by_id(self):
        """GET /api/distribution-hub/templates/{id} returns system template detail"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/tpl_all_radio")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["id"] == "tpl_all_radio", "Template ID should match"
        assert data["name"] == "All Radio Stations", "Template name should match"
        assert data["is_system"] == True, "Should be a system template"
        assert len(data["platform_ids"]) == 6, "Should have 6 platform IDs"
        
        print(f"✓ GET /templates/tpl_all_radio returns correct system template")
    
    def test_get_nonexistent_template_returns_404(self):
        """GET /api/distribution-hub/templates/{id} returns 404 for nonexistent template"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/nonexistent_template")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        print(f"✓ GET /templates/nonexistent_template returns 404")
    
    # ─── CREATE CUSTOM TEMPLATE TESTS ───
    
    def test_create_custom_template(self):
        """POST /api/distribution-hub/templates creates custom template with name, description, icon, platform_ids"""
        template_data = {
            "name": "TEST_My Urban Stations",
            "description": "Urban radio and streaming combo",
            "icon": "radio",
            "platform_ids": ["radio_one", "soundcloud", "audiomack", "boomplay"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/distribution-hub/templates", json=template_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "template" in data, "Response should have 'template' field"
        
        template = data["template"]
        assert template["name"] == template_data["name"], "Name should match"
        assert template["description"] == template_data["description"], "Description should match"
        assert template["icon"] == template_data["icon"], "Icon should match"
        assert template["platform_ids"] == template_data["platform_ids"], "Platform IDs should match"
        assert template["is_system"] == False, "Custom template should not be system"
        assert template["id"].startswith("tpl_custom_"), "Custom template ID should start with tpl_custom_"
        assert template["platform_count"] == 4, "Platform count should be 4"
        
        # Store template ID for subsequent tests
        self.__class__.test_custom_template_id = template["id"]
        print(f"✓ POST /templates created custom template: {template['id']}")
    
    def test_create_template_without_name_fails(self):
        """POST /api/distribution-hub/templates without name should fail"""
        template_data = {
            "description": "Missing name",
            "platform_ids": ["spotify"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/distribution-hub/templates", json=template_data)
        # Should fail with 422 validation error
        assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
        
        print(f"✓ POST /templates without name returns 422")
    
    # ─── GET CUSTOM TEMPLATE BY ID ───
    
    def test_get_custom_template_by_id(self):
        """GET /api/distribution-hub/templates/{id} returns custom template detail"""
        # First create a template
        template_data = {
            "name": "TEST_Get Custom Template",
            "description": "Test template for GET",
            "icon": "music",
            "platform_ids": ["spotify", "apple_music"]
        }
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/templates", json=template_data)
        template_id = create_response.json()["template"]["id"]
        
        # Get the template
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/{template_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["id"] == template_id, "Template ID should match"
        assert data["name"] == template_data["name"], "Name should match"
        assert data["is_system"] == False, "Should not be system template"
        
        print(f"✓ GET /templates/{template_id} returns correct custom template")
    
    # ─── UPDATE CUSTOM TEMPLATE TESTS ───
    
    def test_update_custom_template(self):
        """PUT /api/distribution-hub/templates/{id} updates custom template"""
        # First create a template
        template_data = {
            "name": "TEST_Update Template Original",
            "description": "Original description",
            "icon": "layers",
            "platform_ids": ["youtube"]
        }
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/templates", json=template_data)
        template_id = create_response.json()["template"]["id"]
        
        # Update the template
        update_data = {
            "name": "TEST_Update Template Updated",
            "description": "Updated description",
            "icon": "video",
            "platform_ids": ["youtube", "vimeo", "tiktok"]
        }
        
        response = self.session.put(f"{BASE_URL}/api/distribution-hub/templates/{template_id}", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "template" in data, "Response should have 'template' field"
        
        template = data["template"]
        assert template["name"] == update_data["name"], "Name should be updated"
        assert template["description"] == update_data["description"], "Description should be updated"
        assert template["icon"] == update_data["icon"], "Icon should be updated"
        assert len(template["platform_ids"]) == 3, "Should have 3 platforms"
        assert template["platform_count"] == 3, "Platform count should be 3"
        
        # Verify persistence with GET
        get_response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/{template_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == update_data["name"], "Name should persist"
        
        print(f"✓ PUT /templates/{template_id} updated custom template successfully")
    
    def test_update_system_template_fails(self):
        """PUT /api/distribution-hub/templates/{id} cannot update system templates"""
        update_data = {
            "name": "Hacked System Template",
            "description": "Attempting to modify system template"
        }
        
        response = self.session.put(f"{BASE_URL}/api/distribution-hub/templates/tpl_all_radio", json=update_data)
        # Should return 404 (template not found or cannot be edited)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        # Verify system template unchanged
        get_response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/tpl_all_radio")
        assert get_response.json()["name"] == "All Radio Stations", "System template should be unchanged"
        
        print(f"✓ PUT /templates/tpl_all_radio correctly rejected (system templates cannot be edited)")
    
    # ─── DELETE CUSTOM TEMPLATE TESTS ───
    
    def test_delete_custom_template(self):
        """DELETE /api/distribution-hub/templates/{id} deletes custom template"""
        # First create a template
        template_data = {
            "name": "TEST_Delete Template",
            "description": "Template to delete",
            "platform_ids": ["facebook"]
        }
        create_response = self.session.post(f"{BASE_URL}/api/distribution-hub/templates", json=template_data)
        template_id = create_response.json()["template"]["id"]
        
        # Delete the template
        response = self.session.delete(f"{BASE_URL}/api/distribution-hub/templates/{template_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify deletion
        get_response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/{template_id}")
        assert get_response.status_code == 404, "Deleted template should return 404"
        
        print(f"✓ DELETE /templates/{template_id} deleted custom template successfully")
    
    def test_delete_system_template_fails(self):
        """DELETE /api/distribution-hub/templates/{id} cannot delete system templates"""
        response = self.session.delete(f"{BASE_URL}/api/distribution-hub/templates/tpl_all_radio")
        # Should return 404 (template not found or cannot be deleted)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        # Verify system template still exists
        get_response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/tpl_all_radio")
        assert get_response.status_code == 200, "System template should still exist"
        
        print(f"✓ DELETE /templates/tpl_all_radio correctly rejected (system templates cannot be deleted)")
    
    # ─── ADDITIONAL SYSTEM TEMPLATE VERIFICATION ───
    
    def test_verify_social_blast_template(self):
        """Verify 'Social Media Blast' template has all 9 social platforms"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/tpl_social_blast")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Social Media Blast", "Name should match"
        assert data["icon"] == "share", "Icon should be 'share'"
        assert len(data["platform_ids"]) == 9, f"Should have 9 social platforms, got {len(data['platform_ids'])}"
        
        expected_platforms = ["twitter_x", "linkedin", "pinterest", "snapchat", "reddit", "threads", "bluesky", "discord", "telegram"]
        for pid in expected_platforms:
            assert pid in data["platform_ids"], f"Platform '{pid}' should be in Social Blast template"
        
        print(f"✓ tpl_social_blast has correct 9 social media platforms")
    
    def test_verify_video_everywhere_template(self):
        """Verify 'Video Everywhere' template has 8 video platforms"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/tpl_video_everywhere")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Video Everywhere", "Name should match"
        assert data["icon"] == "video", "Icon should be 'video'"
        assert len(data["platform_ids"]) == 8, f"Should have 8 video platforms, got {len(data['platform_ids'])}"
        
        print(f"✓ tpl_video_everywhere has correct 8 video platforms")
    
    def test_verify_film_distribution_template(self):
        """Verify 'Film Distribution' template has 9 film/movie platforms"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/tpl_film_distribution")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Film Distribution", "Name should match"
        assert data["icon"] == "film", "Icon should be 'film'"
        assert len(data["platform_ids"]) == 9, f"Should have 9 film platforms, got {len(data['platform_ids'])}"
        
        print(f"✓ tpl_film_distribution has correct 9 film/movie platforms")
    
    def test_verify_podcast_push_template(self):
        """Verify 'Full Podcast Push' template has 5 podcast platforms"""
        response = self.session.get(f"{BASE_URL}/api/distribution-hub/templates/tpl_podcast_push")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Full Podcast Push", "Name should match"
        assert data["icon"] == "mic", "Icon should be 'mic'"
        assert len(data["platform_ids"]) == 5, f"Should have 5 podcast platforms, got {len(data['platform_ids'])}"
        
        expected_platforms = ["apple_podcasts", "spotify_podcasts", "google_podcasts", "stitcher", "podbean"]
        for pid in expected_platforms:
            assert pid in data["platform_ids"], f"Platform '{pid}' should be in Podcast Push template"
        
        print(f"✓ tpl_podcast_push has correct 5 podcast platforms")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
