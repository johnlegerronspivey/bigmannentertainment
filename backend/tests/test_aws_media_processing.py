"""AWS Media Processing API Tests - MediaConvert & Transcribe Integration"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://publish-test-1.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestAWSMediaProcessingAPIs:
    """Tests for AWS MediaConvert and Transcribe API endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for API calls"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Auth returns access_token not token
        token = data.get("access_token")
        assert token is not None, f"No access_token in response: {data}"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    # ========== STATUS ENDPOINT ==========
    def test_aws_media_status_returns_available(self, auth_headers):
        """GET /api/aws-media/status returns available: true for both services"""
        response = requests.get(f"{BASE_URL}/api/aws-media/status", headers=auth_headers)
        assert response.status_code == 200, f"Status failed: {response.text}"
        
        data = response.json()
        
        # Verify MediaConvert status
        assert "mediaconvert" in data, "Missing mediaconvert status"
        assert data["mediaconvert"].get("available") == True, f"MediaConvert not available: {data['mediaconvert']}"
        
        # Verify Transcribe status
        assert "transcribe" in data, "Missing transcribe status"
        assert data["transcribe"].get("available") == True, f"Transcribe not available: {data['transcribe']}"
        
        print(f"✓ MediaConvert available: {data['mediaconvert'].get('available')}")
        print(f"✓ Transcribe available: {data['transcribe'].get('available')}")
    
    # ========== MEDIACONVERT PRESETS ==========
    def test_mediaconvert_presets_returns_7_options(self, auth_headers):
        """GET /api/aws-media/mediaconvert/presets returns 7 preset options"""
        response = requests.get(f"{BASE_URL}/api/aws-media/mediaconvert/presets", headers=auth_headers)
        assert response.status_code == 200, f"Presets failed: {response.text}"
        
        data = response.json()
        presets = data.get("presets", {})
        
        # Expected 7 presets
        expected_presets = ["youtube_hd", "tiktok_vertical", "instagram_square", "twitter_hd", "hls_adaptive", "audio_mp3", "audio_aac"]
        
        assert len(presets) == 7, f"Expected 7 presets, got {len(presets)}: {list(presets.keys())}"
        
        for preset_name in expected_presets:
            assert preset_name in presets, f"Missing preset: {preset_name}"
            assert "label" in presets[preset_name], f"Preset {preset_name} missing label"
            assert "container" in presets[preset_name], f"Preset {preset_name} missing container"
        
        print(f"✓ Got {len(presets)} presets: {list(presets.keys())}")
    
    # ========== TRANSCRIBE LANGUAGES ==========
    def test_transcribe_languages_returns_13_languages(self, auth_headers):
        """GET /api/aws-media/transcribe/languages returns 13 languages"""
        response = requests.get(f"{BASE_URL}/api/aws-media/transcribe/languages", headers=auth_headers)
        assert response.status_code == 200, f"Languages failed: {response.text}"
        
        data = response.json()
        languages = data.get("languages", {})
        
        assert len(languages) == 13, f"Expected 13 languages, got {len(languages)}: {list(languages.keys())}"
        
        # Verify key languages are present
        expected_langs = ["en-US", "en-GB", "es-US", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN", "hi-IN", "ar-SA"]
        for lang_code in expected_langs:
            assert lang_code in languages, f"Missing language: {lang_code}"
        
        print(f"✓ Got {len(languages)} languages: {list(languages.keys())}")
    
    # ========== MEDIACONVERT JOBS LIST ==========
    def test_mediaconvert_jobs_list(self, auth_headers):
        """GET /api/aws-media/mediaconvert/jobs returns a jobs list"""
        response = requests.get(f"{BASE_URL}/api/aws-media/mediaconvert/jobs", headers=auth_headers)
        assert response.status_code == 200, f"MC Jobs list failed: {response.text}"
        
        data = response.json()
        assert "jobs" in data, f"Missing 'jobs' in response: {data}"
        assert isinstance(data["jobs"], list), f"jobs should be a list: {type(data['jobs'])}"
        
        print(f"✓ MediaConvert jobs list returned {len(data['jobs'])} jobs")
    
    # ========== TRANSCRIBE JOBS LIST ==========
    def test_transcribe_jobs_list(self, auth_headers):
        """GET /api/aws-media/transcribe/jobs returns a jobs list"""
        response = requests.get(f"{BASE_URL}/api/aws-media/transcribe/jobs", headers=auth_headers)
        assert response.status_code == 200, f"Transcribe jobs list failed: {response.text}"
        
        data = response.json()
        assert "jobs" in data, f"Missing 'jobs' in response: {data}"
        assert isinstance(data["jobs"], list), f"jobs should be a list: {type(data['jobs'])}"
        
        print(f"✓ Transcribe jobs list returned {len(data['jobs'])} jobs")
    
    # ========== MEDIACONVERT INVALID PRESET ==========
    def test_mediaconvert_invalid_preset_returns_400(self, auth_headers):
        """POST /api/aws-media/mediaconvert/jobs with invalid preset returns 400 error"""
        payload = {
            "s3_input_key": "test/video.mp4",
            "preset": "INVALID_PRESET_NAME"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/aws-media/mediaconvert/jobs",
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid preset, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have error detail
        assert "detail" in data or "error" in data or "message" in data, f"No error message in response: {data}"
        
        print(f"✓ Invalid preset correctly returns 400 error")
    
    # ========== UNAUTHENTICATED ACCESS ==========
    def test_status_requires_auth(self):
        """Endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-media/status")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Auth required for status endpoint")
    
    def test_presets_requires_auth(self):
        """Presets endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-media/mediaconvert/presets")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Auth required for presets endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
