"""
Test Distribution Hub - 120 Platforms and 12 Templates Expansion
Tests the expanded platform categories including:
- 15 categories total
- 120 platforms across all categories
- 12 system templates (6 original + 6 new)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestPlatformCounts:
    """Test all 15 platform categories have correct platform counts"""
    
    @pytest.fixture(scope="class")
    def platforms_data(self):
        """Fetch platforms data once for all tests in class"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/platforms")
        assert response.status_code == 200, f"Failed to get platforms: {response.text}"
        return response.json()
    
    def test_total_platforms_is_120(self, platforms_data):
        """Verify total platform count is exactly 120"""
        total = platforms_data.get("total_platforms", 0)
        assert total == 120, f"Expected 120 total platforms, got {total}"
        print(f"PASS: Total platforms = {total}")
    
    def test_audio_streaming_has_14_platforms(self, platforms_data):
        """Audio Streaming & Radio category has 14 platforms"""
        categories = platforms_data.get("categories", {})
        audio = categories.get("audio_streaming", {})
        count = len(audio.get("platforms", {}))
        assert count == 14, f"Expected 14 audio_streaming platforms, got {count}"
        print(f"PASS: audio_streaming = {count} platforms")
    
    def test_commercial_radio_has_6_platforms(self, platforms_data):
        """Commercial Radio category has 6 platforms"""
        categories = platforms_data.get("categories", {})
        radio = categories.get("commercial_radio", {})
        count = len(radio.get("platforms", {}))
        assert count == 6, f"Expected 6 commercial_radio platforms, got {count}"
        print(f"PASS: commercial_radio = {count} platforms")
    
    def test_video_platforms_has_8(self, platforms_data):
        """Video Platforms category has 8 platforms"""
        categories = platforms_data.get("categories", {})
        video = categories.get("video_platforms", {})
        count = len(video.get("platforms", {}))
        assert count == 8, f"Expected 8 video_platforms, got {count}"
        print(f"PASS: video_platforms = {count} platforms")
    
    def test_film_movie_has_9_platforms(self, platforms_data):
        """Film & Movie category has 9 platforms"""
        categories = platforms_data.get("categories", {})
        film = categories.get("film_movie", {})
        count = len(film.get("platforms", {}))
        assert count == 9, f"Expected 9 film_movie platforms, got {count}"
        print(f"PASS: film_movie = {count} platforms")
    
    def test_social_media_has_9_platforms(self, platforms_data):
        """Social Media category has 9 platforms"""
        categories = platforms_data.get("categories", {})
        social = categories.get("social_media", {})
        count = len(social.get("platforms", {}))
        assert count == 9, f"Expected 9 social_media platforms, got {count}"
        print(f"PASS: social_media = {count} platforms")
    
    def test_podcast_has_5_platforms(self, platforms_data):
        """Podcast category has 5 platforms"""
        categories = platforms_data.get("categories", {})
        podcast = categories.get("podcast", {})
        count = len(podcast.get("platforms", {}))
        assert count == 5, f"Expected 5 podcast platforms, got {count}"
        print(f"PASS: podcast = {count} platforms")
    
    # NEW CATEGORIES TESTS
    
    def test_modeling_agencies_has_12_platforms(self, platforms_data):
        """Modeling Agencies category has 12 platforms"""
        categories = platforms_data.get("categories", {})
        modeling = categories.get("modeling_agencies", {})
        count = len(modeling.get("platforms", {}))
        assert count == 12, f"Expected 12 modeling_agencies platforms, got {count}"
        
        # Verify specific platforms
        platforms = modeling.get("platforms", {})
        expected = ["img_models", "elite_model", "ford_models", "wilhelmina", "next_management",
                    "women_management", "society_management", "storm_models", "premier_models",
                    "select_models", "la_models", "dna_models"]
        for p_id in expected:
            assert p_id in platforms, f"Missing modeling platform: {p_id}"
        print(f"PASS: modeling_agencies = {count} platforms")
    
    def test_dooh_programmatic_has_10_platforms(self, platforms_data):
        """Programmatic DOOH category has 10 platforms"""
        categories = platforms_data.get("categories", {})
        dooh = categories.get("dooh_programmatic", {})
        count = len(dooh.get("platforms", {}))
        assert count == 10, f"Expected 10 dooh_programmatic platforms, got {count}"
        
        # Verify specific platforms
        platforms = dooh.get("platforms", {})
        expected = ["clear_channel", "jcdecaux", "lamar_advertising", "outfront_media",
                    "vistar_media", "broadsign", "place_exchange", "hivestack", "adquick", "blip_billboards"]
        for p_id in expected:
            assert p_id in platforms, f"Missing DOOH platform: {p_id}"
        print(f"PASS: dooh_programmatic = {count} platforms")
    
    def test_web3_blockchain_has_8_platforms(self, platforms_data):
        """Web3 & Blockchain category has 8 platforms"""
        categories = platforms_data.get("categories", {})
        web3 = categories.get("web3_blockchain", {})
        count = len(web3.get("platforms", {}))
        assert count == 8, f"Expected 8 web3_blockchain platforms, got {count}"
        print(f"PASS: web3_blockchain = {count} platforms")
    
    def test_rights_licensing_has_7_platforms(self, platforms_data):
        """Rights & Licensing category has 7 platforms"""
        categories = platforms_data.get("categories", {})
        rights = categories.get("rights_licensing", {})
        count = len(rights.get("platforms", {}))
        assert count == 7, f"Expected 7 rights_licensing platforms, got {count}"
        print(f"PASS: rights_licensing = {count} platforms")
    
    def test_international_streaming_has_8_platforms(self, platforms_data):
        """International Streaming category has 8 platforms"""
        categories = platforms_data.get("categories", {})
        intl = categories.get("international_streaming", {})
        count = len(intl.get("platforms", {}))
        assert count == 8, f"Expected 8 international_streaming platforms, got {count}"
        print(f"PASS: international_streaming = {count} platforms")
    
    def test_live_streaming_has_4_platforms(self, platforms_data):
        """Live Streaming & Audio Social category has 4 platforms"""
        categories = platforms_data.get("categories", {})
        live = categories.get("live_streaming", {})
        count = len(live.get("platforms", {}))
        assert count == 4, f"Expected 4 live_streaming platforms, got {count}"
        print(f"PASS: live_streaming = {count} platforms")
    
    def test_entertainment_media_has_8_platforms(self, platforms_data):
        """Entertainment & Hip-Hop Media category has 8 platforms"""
        categories = platforms_data.get("categories", {})
        entertainment = categories.get("entertainment_media", {})
        count = len(entertainment.get("platforms", {}))
        assert count == 8, f"Expected 8 entertainment_media platforms, got {count}"
        print(f"PASS: entertainment_media = {count} platforms")
    
    def test_creator_platforms_has_4_platforms(self, platforms_data):
        """Creator & Content Platforms category has 4 platforms"""
        categories = platforms_data.get("categories", {})
        creator = categories.get("creator_platforms", {})
        count = len(creator.get("platforms", {}))
        assert count == 4, f"Expected 4 creator_platforms, got {count}"
        print(f"PASS: creator_platforms = {count} platforms")
    
    def test_alternative_social_has_8_platforms(self, platforms_data):
        """Alternative Social & Video category has 8 platforms"""
        categories = platforms_data.get("categories", {})
        alt = categories.get("alternative_social", {})
        count = len(alt.get("platforms", {}))
        assert count == 8, f"Expected 8 alternative_social platforms, got {count}"
        print(f"PASS: alternative_social = {count} platforms")
    
    def test_15_categories_exist(self, platforms_data):
        """Verify all 15 categories exist"""
        categories = platforms_data.get("categories", {})
        expected_categories = [
            "audio_streaming", "commercial_radio", "video_platforms", "film_movie",
            "social_media", "podcast", "modeling_agencies", "dooh_programmatic",
            "web3_blockchain", "rights_licensing", "international_streaming",
            "live_streaming", "entertainment_media", "creator_platforms", "alternative_social"
        ]
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        assert len(categories) == 15, f"Expected 15 categories, got {len(categories)}"
        print(f"PASS: All 15 categories exist")


class TestSystemTemplates:
    """Test all 12 system templates"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for templates endpoint"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Auth returns 'access_token' not 'token'
        return data.get("access_token")
    
    @pytest.fixture(scope="class")
    def templates_data(self, auth_token):
        """Fetch templates data once"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/distribution-hub/templates", headers=headers)
        assert response.status_code == 200, f"Failed to get templates: {response.text}"
        return response.json()
    
    def test_12_system_templates_exist(self, templates_data):
        """Verify exactly 12 system templates"""
        system_count = templates_data.get("system_count", 0)
        assert system_count == 12, f"Expected 12 system templates, got {system_count}"
        print(f"PASS: system_count = {system_count}")
    
    def test_original_6_templates_exist(self, templates_data):
        """Verify original 6 templates still exist"""
        templates = templates_data.get("templates", [])
        system_templates = [t for t in templates if t.get("is_system")]
        template_ids = [t["id"] for t in system_templates]
        
        original_templates = [
            "tpl_all_radio", "tpl_major_streaming", "tpl_social_blast",
            "tpl_video_everywhere", "tpl_film_distribution", "tpl_podcast_push"
        ]
        for t_id in original_templates:
            assert t_id in template_ids, f"Missing original template: {t_id}"
        print("PASS: All 6 original templates exist")
    
    def test_new_6_templates_exist(self, templates_data):
        """Verify 6 new templates exist"""
        templates = templates_data.get("templates", [])
        system_templates = [t for t in templates if t.get("is_system")]
        template_ids = [t["id"] for t in system_templates]
        
        new_templates = [
            "tpl_all_modeling", "tpl_dooh_blast", "tpl_web3_distribution",
            "tpl_entertainment_media", "tpl_global_streaming", "tpl_rights_licensing"
        ]
        for t_id in new_templates:
            assert t_id in template_ids, f"Missing new template: {t_id}"
        print("PASS: All 6 new templates exist")
    
    def test_tpl_all_modeling_has_12_platforms(self, templates_data):
        """All Modeling Agencies template has 12 platforms"""
        templates = templates_data.get("templates", [])
        tpl = next((t for t in templates if t["id"] == "tpl_all_modeling"), None)
        assert tpl is not None, "Template tpl_all_modeling not found"
        count = tpl.get("platform_count") or len(tpl.get("platform_ids", []))
        assert count == 12, f"Expected 12 platforms in tpl_all_modeling, got {count}"
        assert tpl.get("icon") == "camera", f"Expected icon 'camera', got {tpl.get('icon')}"
        print(f"PASS: tpl_all_modeling has {count} platforms, icon=camera")
    
    def test_tpl_dooh_blast_has_10_platforms(self, templates_data):
        """DOOH Billboard Blast template has 10 platforms"""
        templates = templates_data.get("templates", [])
        tpl = next((t for t in templates if t["id"] == "tpl_dooh_blast"), None)
        assert tpl is not None, "Template tpl_dooh_blast not found"
        count = tpl.get("platform_count") or len(tpl.get("platform_ids", []))
        assert count == 10, f"Expected 10 platforms in tpl_dooh_blast, got {count}"
        assert tpl.get("icon") == "monitor", f"Expected icon 'monitor', got {tpl.get('icon')}"
        print(f"PASS: tpl_dooh_blast has {count} platforms, icon=monitor")
    
    def test_tpl_web3_distribution_has_8_platforms(self, templates_data):
        """Web3 Distribution template has 8 platforms"""
        templates = templates_data.get("templates", [])
        tpl = next((t for t in templates if t["id"] == "tpl_web3_distribution"), None)
        assert tpl is not None, "Template tpl_web3_distribution not found"
        count = tpl.get("platform_count") or len(tpl.get("platform_ids", []))
        assert count == 8, f"Expected 8 platforms in tpl_web3_distribution, got {count}"
        assert tpl.get("icon") == "hexagon", f"Expected icon 'hexagon', got {tpl.get('icon')}"
        print(f"PASS: tpl_web3_distribution has {count} platforms, icon=hexagon")
    
    def test_tpl_entertainment_media_has_8_platforms(self, templates_data):
        """Entertainment Media Push template has 8 platforms"""
        templates = templates_data.get("templates", [])
        tpl = next((t for t in templates if t["id"] == "tpl_entertainment_media"), None)
        assert tpl is not None, "Template tpl_entertainment_media not found"
        count = tpl.get("platform_count") or len(tpl.get("platform_ids", []))
        assert count == 8, f"Expected 8 platforms in tpl_entertainment_media, got {count}"
        assert tpl.get("icon") == "star", f"Expected icon 'star', got {tpl.get('icon')}"
        print(f"PASS: tpl_entertainment_media has {count} platforms, icon=star")
    
    def test_tpl_global_streaming_has_8_platforms(self, templates_data):
        """Global Streaming template has 8 platforms"""
        templates = templates_data.get("templates", [])
        tpl = next((t for t in templates if t["id"] == "tpl_global_streaming"), None)
        assert tpl is not None, "Template tpl_global_streaming not found"
        count = tpl.get("platform_count") or len(tpl.get("platform_ids", []))
        assert count == 8, f"Expected 8 platforms in tpl_global_streaming, got {count}"
        assert tpl.get("icon") == "globe", f"Expected icon 'globe', got {tpl.get('icon')}"
        print(f"PASS: tpl_global_streaming has {count} platforms, icon=globe")
    
    def test_tpl_rights_licensing_has_7_platforms(self, templates_data):
        """Rights & Licensing template has 7 platforms"""
        templates = templates_data.get("templates", [])
        tpl = next((t for t in templates if t["id"] == "tpl_rights_licensing"), None)
        assert tpl is not None, "Template tpl_rights_licensing not found"
        count = tpl.get("platform_count") or len(tpl.get("platform_ids", []))
        assert count == 7, f"Expected 7 platforms in tpl_rights_licensing, got {count}"
        assert tpl.get("icon") == "shield", f"Expected icon 'shield', got {tpl.get('icon')}"
        print(f"PASS: tpl_rights_licensing has {count} platforms, icon=shield")


class TestDistributionFlow:
    """Test distribution flow with new platform categories"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_create_test_content(self, headers):
        """Create test content for distribution"""
        response = requests.post(f"{BASE_URL}/api/distribution-hub/content", headers=headers, json={
            "title": "TEST_120_Platforms_Content",
            "content_type": "image",
            "description": "Test content for 120 platform distribution",
            "artist": "Test Artist"
        })
        assert response.status_code == 200, f"Failed to create content: {response.text}"
        data = response.json()
        content_id = data.get("content", {}).get("id")
        assert content_id is not None, "Content ID not returned"
        print(f"PASS: Created test content with ID: {content_id}")
        return content_id
    
    def test_distribute_to_modeling_agencies(self, headers, test_create_test_content):
        """Test distribution to modeling agencies category"""
        content_id = test_create_test_content
        
        # Distribute to 3 modeling agencies
        platform_ids = ["img_models", "elite_model", "ford_models"]
        response = requests.post(f"{BASE_URL}/api/distribution-hub/distribute", headers=headers, json={
            "content_id": content_id,
            "platform_ids": platform_ids
        })
        assert response.status_code == 200, f"Distribution failed: {response.text}"
        data = response.json()
        assert data.get("deliveries") is not None
        assert len(data["deliveries"]) == 3, f"Expected 3 deliveries, got {len(data['deliveries'])}"
        
        # Verify export_package method for modeling agencies
        for d in data["deliveries"]:
            assert d["delivery_method"] == "export_package", f"Expected export_package, got {d['delivery_method']}"
            assert d["status"] == "export_ready"
        print(f"PASS: Distributed to 3 modeling agencies with export_package method")
    
    def test_distribute_to_dooh_platforms(self, headers, test_create_test_content):
        """Test distribution to DOOH platforms"""
        content_id = test_create_test_content
        
        # Distribute to 2 DOOH platforms
        platform_ids = ["clear_channel", "jcdecaux"]
        response = requests.post(f"{BASE_URL}/api/distribution-hub/distribute", headers=headers, json={
            "content_id": content_id,
            "platform_ids": platform_ids
        })
        assert response.status_code == 200, f"Distribution failed: {response.text}"
        data = response.json()
        assert len(data["deliveries"]) == 2
        
        # Verify api_push method for DOOH
        for d in data["deliveries"]:
            assert d["delivery_method"] == "api_push", f"Expected api_push, got {d['delivery_method']}"
            assert d["status"] == "queued"
        print(f"PASS: Distributed to 2 DOOH platforms with api_push method")
    
    def test_hub_stats_show_120_platforms(self, headers):
        """Verify hub stats show 120 platforms available"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("total_platforms_available") == 120, f"Expected 120, got {data.get('total_platforms_available')}"
        print(f"PASS: Hub stats show 120 platforms available")


class TestModelingAgenciesPlatformDetails:
    """Verify specific modeling agency platform names"""
    
    @pytest.fixture(scope="class")
    def modeling_platforms(self):
        """Get modeling agencies platforms"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/platforms")
        assert response.status_code == 200
        data = response.json()
        return data.get("categories", {}).get("modeling_agencies", {}).get("platforms", {})
    
    def test_img_models_platform(self, modeling_platforms):
        """IMG Models platform exists with correct name"""
        assert "img_models" in modeling_platforms
        assert modeling_platforms["img_models"]["name"] == "IMG Models"
        print("PASS: IMG Models platform verified")
    
    def test_elite_model_platform(self, modeling_platforms):
        """Elite Model Management platform exists"""
        assert "elite_model" in modeling_platforms
        assert modeling_platforms["elite_model"]["name"] == "Elite Model Management"
        print("PASS: Elite Model Management platform verified")
    
    def test_ford_models_platform(self, modeling_platforms):
        """Ford Models platform exists"""
        assert "ford_models" in modeling_platforms
        assert modeling_platforms["ford_models"]["name"] == "Ford Models"
        print("PASS: Ford Models platform verified")
    
    def test_wilhelmina_platform(self, modeling_platforms):
        """Wilhelmina Models platform exists"""
        assert "wilhelmina" in modeling_platforms
        assert "Wilhelmina" in modeling_platforms["wilhelmina"]["name"]
        print("PASS: Wilhelmina platform verified")
    
    def test_dna_models_platform(self, modeling_platforms):
        """DNA Models platform exists"""
        assert "dna_models" in modeling_platforms
        assert modeling_platforms["dna_models"]["name"] == "DNA Models"
        print("PASS: DNA Models platform verified")


class TestDOOHPlatformDetails:
    """Verify specific DOOH platform names"""
    
    @pytest.fixture(scope="class")
    def dooh_platforms(self):
        """Get DOOH platforms"""
        response = requests.get(f"{BASE_URL}/api/distribution-hub/platforms")
        assert response.status_code == 200
        data = response.json()
        return data.get("categories", {}).get("dooh_programmatic", {}).get("platforms", {})
    
    def test_clear_channel_platform(self, dooh_platforms):
        """Clear Channel Outdoor platform exists"""
        assert "clear_channel" in dooh_platforms
        assert "Clear Channel" in dooh_platforms["clear_channel"]["name"]
        assert dooh_platforms["clear_channel"]["method"] == "api_push"
        print("PASS: Clear Channel platform verified")
    
    def test_jcdecaux_platform(self, dooh_platforms):
        """JCDecaux platform exists"""
        assert "jcdecaux" in dooh_platforms
        assert dooh_platforms["jcdecaux"]["name"] == "JCDecaux"
        print("PASS: JCDecaux platform verified")
    
    def test_blip_billboards_platform(self, dooh_platforms):
        """Blip Billboards platform exists"""
        assert "blip_billboards" in dooh_platforms
        assert "Blip" in dooh_platforms["blip_billboards"]["name"]
        print("PASS: Blip Billboards platform verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
