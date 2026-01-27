"""
Creative Studio for Agencies - Backend API Tests
Tests for template-based content creation, AI-powered design generation, brand asset management
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCreativeStudioHealth:
    """Health and stats endpoint tests"""
    
    def test_health_endpoint(self):
        """Test health check returns status and features"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Creative Studio for Agencies"
        assert "features" in data
        assert len(data["features"]) >= 5
        print(f"✓ Health check passed: {data['status']}")
    
    def test_stats_endpoint(self):
        """Test studio stats returns project and brand kit counts"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "projects_in_progress" in data
        assert "projects_published" in data
        assert "total_brand_kits" in data
        assert "storage_used_mb" in data
        print(f"✓ Stats: {data['total_projects']} projects, {data['total_brand_kits']} brand kits")


class TestTemplates:
    """Template endpoint tests"""
    
    def test_get_templates_list(self):
        """Test getting all templates"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/templates")
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        assert len(templates) >= 6  # Should have 6 sample templates
        print(f"✓ Found {len(templates)} templates")
    
    def test_template_has_required_fields(self):
        """Test template structure"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/templates")
        assert response.status_code == 200
        templates = response.json()
        if templates:
            template = templates[0]
            assert "id" in template
            assert "name" in template
            assert "category" in template
            assert "platform" in template
            assert "width" in template
            assert "height" in template
            assert "elements" in template
            print(f"✓ Template structure valid: {template['name']}")
    
    def test_filter_templates_by_category(self):
        """Test filtering templates by category"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/templates?category=social_media")
        assert response.status_code == 200
        templates = response.json()
        for t in templates:
            assert t["category"] == "social_media"
        print(f"✓ Filtered {len(templates)} social_media templates")
    
    def test_filter_templates_by_platform(self):
        """Test filtering templates by platform"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/templates?platform=instagram_post")
        assert response.status_code == 200
        templates = response.json()
        for t in templates:
            assert t["platform"] == "instagram_post"
        print(f"✓ Filtered {len(templates)} instagram_post templates")


class TestBrandKits:
    """Brand kit CRUD tests"""
    
    def test_get_brand_kits_list(self):
        """Test getting all brand kits"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/brand-kits")
        assert response.status_code == 200
        brand_kits = response.json()
        assert isinstance(brand_kits, list)
        print(f"✓ Found {len(brand_kits)} brand kits")
    
    def test_create_brand_kit(self):
        """Test creating a new brand kit"""
        payload = {
            "name": f"TEST_Brand_{uuid.uuid4().hex[:8]}",
            "description": "Test brand kit for automated testing",
            "colors": [
                {"name": "Primary", "hex_code": "#FF5733", "usage": "primary"},
                {"name": "Secondary", "hex_code": "#33FF57", "usage": "secondary"}
            ],
            "fonts": [
                {"name": "Roboto", "family": "Roboto", "weight": "regular", "usage": "heading"}
            ],
            "tagline": "Test tagline",
            "voice_tone": "Professional and friendly"
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/brand-kits",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert len(data["colors"]) == 2
        assert len(data["fonts"]) == 1
        assert "id" in data
        print(f"✓ Created brand kit: {data['name']}")
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/creative-studio/brand-kits/{data['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == payload["name"]
        print(f"✓ Verified brand kit via GET")
        
        return data["id"]
    
    def test_get_nonexistent_brand_kit(self):
        """Test getting a brand kit that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/brand-kits/nonexistent-id")
        assert response.status_code == 404
        print("✓ 404 returned for nonexistent brand kit")


class TestProjects:
    """Project CRUD tests"""
    
    def test_get_projects_list(self):
        """Test getting all projects"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/projects")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] == True
        assert "projects" in data
        assert "total" in data
        print(f"✓ Found {data['total']} projects")
    
    def test_create_project(self):
        """Test creating a new project"""
        payload = {
            "name": f"TEST_Project_{uuid.uuid4().hex[:8]}",
            "description": "Test project for automated testing",
            "category": "social_media",
            "platform": "instagram_post"
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/projects",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["category"] == payload["category"]
        assert data["platform"] == payload["platform"]
        assert data["width"] == 1080  # Instagram post dimensions
        assert data["height"] == 1080
        assert data["status"] == "draft"
        assert "id" in data
        print(f"✓ Created project: {data['name']}")
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/creative-studio/projects/{data['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == payload["name"]
        print(f"✓ Verified project via GET")
        
        return data["id"]
    
    def test_create_project_with_template(self):
        """Test creating a project from a template"""
        # First get a template
        templates_response = requests.get(f"{BASE_URL}/api/creative-studio/templates")
        templates = templates_response.json()
        if templates:
            template = templates[0]
            payload = {
                "name": f"TEST_FromTemplate_{uuid.uuid4().hex[:8]}",
                "description": "Project created from template",
                "category": template["category"],
                "platform": template["platform"],
                "template_id": template["id"]
            }
            response = requests.post(
                f"{BASE_URL}/api/creative-studio/projects",
                json=payload
            )
            assert response.status_code == 200
            data = response.json()
            assert data["template_id"] == template["id"]
            assert data["width"] == template["width"]
            assert data["height"] == template["height"]
            print(f"✓ Created project from template: {template['name']}")
    
    def test_get_nonexistent_project(self):
        """Test getting a project that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/projects/nonexistent-id")
        assert response.status_code == 404
        print("✓ 404 returned for nonexistent project")


class TestPlatforms:
    """Platform configuration tests"""
    
    def test_get_platforms_list(self):
        """Test getting all platforms with dimensions"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/platforms")
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        platforms = data["platforms"]
        assert len(platforms) >= 10  # Should have many platforms
        
        # Check structure
        for platform in platforms:
            assert "id" in platform
            assert "name" in platform
            assert "width" in platform
            assert "height" in platform
        
        print(f"✓ Found {len(platforms)} platforms")
    
    def test_platform_dimensions(self):
        """Test specific platform dimensions"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/platforms")
        data = response.json()
        platforms = {p["id"]: p for p in data["platforms"]}
        
        # Check Instagram Post dimensions
        assert platforms["instagram_post"]["width"] == 1080
        assert platforms["instagram_post"]["height"] == 1080
        
        # Check YouTube Thumbnail dimensions
        assert platforms["youtube_thumbnail"]["width"] == 1280
        assert platforms["youtube_thumbnail"]["height"] == 720
        
        print("✓ Platform dimensions verified")


class TestAIGeneration:
    """AI generation endpoint tests"""
    
    def test_get_ai_styles(self):
        """Test getting available AI styles"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/ai/styles")
        assert response.status_code == 200
        data = response.json()
        assert "styles" in data
        styles = data["styles"]
        assert len(styles) >= 10
        
        # Check structure
        for style in styles:
            assert "id" in style
            assert "name" in style
            assert "description" in style
        
        # Check specific styles exist
        style_ids = [s["id"] for s in styles]
        assert "photorealistic" in style_ids
        assert "illustration" in style_ids
        assert "minimal" in style_ids
        
        print(f"✓ Found {len(styles)} AI styles")
    
    def test_ai_generate_endpoint(self):
        """Test AI image generation endpoint"""
        payload = {
            "prompt": "A beautiful sunset over mountains",
            "style": "photorealistic",
            "width": 1024,
            "height": 1024
        }
        response = requests.post(
            f"{BASE_URL}/api/creative-studio/ai/generate",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "prompt" in data
        assert data["prompt"] == payload["prompt"]
        assert "image_url" in data
        assert "width" in data
        assert "height" in data
        assert "generation_time_ms" in data
        print(f"✓ AI generation completed in {data['generation_time_ms']}ms")


class TestCategories:
    """Category endpoint tests"""
    
    def test_get_categories(self):
        """Test getting template categories"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        categories = data["categories"]
        assert len(categories) >= 5
        
        # Check structure
        for cat in categories:
            assert "id" in cat
            assert "name" in cat
        
        print(f"✓ Found {len(categories)} categories")


class TestPlatformDimensions:
    """Platform dimensions endpoint tests"""
    
    def test_get_platform_dimensions(self):
        """Test getting platform dimensions mapping"""
        response = requests.get(f"{BASE_URL}/api/creative-studio/platform-dimensions")
        assert response.status_code == 200
        data = response.json()
        
        # Check specific platforms
        assert "instagram_post" in data
        assert data["instagram_post"]["width"] == 1080
        assert data["instagram_post"]["height"] == 1080
        
        assert "youtube_thumbnail" in data
        assert data["youtube_thumbnail"]["width"] == 1280
        assert data["youtube_thumbnail"]["height"] == 720
        
        print(f"✓ Platform dimensions mapping verified")


class TestDataIntegrity:
    """Data integrity and persistence tests"""
    
    def test_create_brand_kit_and_verify(self):
        """Test creating a brand kit and verifying persistence"""
        # Create
        payload = {
            "name": f"TEST_Integrity_{uuid.uuid4().hex[:8]}",
            "description": "Data integrity test",
            "colors": [
                {"name": "Test Color", "hex_code": "#123456", "usage": "primary"}
            ],
            "fonts": [],
            "tagline": "Test tagline"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/creative-studio/brand-kits",
            json=payload
        )
        assert create_response.status_code == 200
        created = create_response.json()
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/creative-studio/brand-kits/{created['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        
        assert fetched["name"] == payload["name"]
        assert fetched["description"] == payload["description"]
        assert fetched["tagline"] == payload["tagline"]
        assert len(fetched["colors"]) == 1
        assert fetched["colors"][0]["hex_code"] == "#123456"
        
        print("✓ Brand kit data integrity verified")
    
    def test_create_project_and_verify(self):
        """Test creating a project and verifying persistence"""
        # Create
        payload = {
            "name": f"TEST_ProjectIntegrity_{uuid.uuid4().hex[:8]}",
            "description": "Project data integrity test",
            "category": "marketing",
            "platform": "twitter_post"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/creative-studio/projects",
            json=payload
        )
        assert create_response.status_code == 200
        created = create_response.json()
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/creative-studio/projects/{created['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        
        assert fetched["name"] == payload["name"]
        assert fetched["description"] == payload["description"]
        assert fetched["category"] == payload["category"]
        assert fetched["platform"] == payload["platform"]
        # Twitter post dimensions
        assert fetched["width"] == 1200
        assert fetched["height"] == 675
        
        print("✓ Project data integrity verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
