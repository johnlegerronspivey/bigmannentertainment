#!/usr/bin/env python3
"""
Detailed Platform Configuration Testing
Tests the specific configurations and metadata for the 7 new platforms
"""

import requests
import json

BASE_URL = "https://bme-media-hub.preview.emergentagent.com/api"

def test_platform_details():
    """Test detailed platform configurations"""
    
    print("🔍 DETAILED PLATFORM CONFIGURATION TESTING")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/distribution/platforms")
        
        if response.status_code == 200:
            data = response.json()
            platforms = data.get('platforms', {})
            
            print(f"📊 Total platforms found: {len(platforms)}")
            
            # Test the 7 new platforms in detail
            new_platforms = {
                'imgmodels': 'IMG Models',
                'elitemodelmanagement': 'Elite Model Management',
                'lamodels': 'LA Models', 
                'stormmanagement': 'Storm Management LA',
                'thesource': 'The Source',
                'billboard': 'Billboard',
                'tmz': 'TMZ'
            }
            
            print("\n🎯 TESTING 7 NEW PLATFORMS:")
            print("-" * 40)
            
            for platform_key, platform_name in new_platforms.items():
                print(f"\n📋 {platform_name} ({platform_key}):")
                
                if platform_key in platforms:
                    platform = platforms[platform_key]
                    
                    # Check basic configuration
                    print(f"  ✅ Type: {platform.get('type', 'MISSING')}")
                    print(f"  ✅ Name: {platform.get('name', 'MISSING')}")
                    print(f"  ✅ API Endpoint: {platform.get('api_endpoint', 'MISSING')}")
                    print(f"  ✅ Max File Size: {platform.get('max_file_size', 'MISSING')} bytes")
                    print(f"  ✅ Supported Formats: {platform.get('supported_formats', 'MISSING')}")
                    
                    # Check credentials
                    creds = platform.get('credentials_required', [])
                    print(f"  ✅ Credentials Required: {len(creds)} items - {creds}")
                    
                    # Check demographics and guidelines
                    demographics = platform.get('target_demographics', 'MISSING')
                    guidelines = platform.get('content_guidelines', 'MISSING')
                    print(f"  ✅ Target Demographics: {demographics[:80]}{'...' if len(demographics) > 80 else ''}")
                    print(f"  ✅ Content Guidelines: {guidelines[:80]}{'...' if len(guidelines) > 80 else ''}")
                    
                    # Check submission process and revenue sharing
                    submission = platform.get('submission_process', 'MISSING')
                    revenue = platform.get('revenue_sharing', 'MISSING')
                    print(f"  ✅ Submission Process: {submission[:60]}{'...' if len(submission) > 60 else ''}")
                    print(f"  ✅ Revenue Sharing: {revenue[:60]}{'...' if len(revenue) > 60 else ''}")
                    
                    # Check platform features if available
                    features = platform.get('platform_features', [])
                    if features:
                        print(f"  ✅ Platform Features: {features}")
                    
                else:
                    print(f"  ❌ Platform not found!")
            
            # Category breakdown
            print("\n📊 PLATFORM CATEGORY BREAKDOWN:")
            print("-" * 40)
            
            categories = {}
            for platform in platforms.values():
                platform_type = platform.get('type', 'unknown')
                if platform_type not in categories:
                    categories[platform_type] = 0
                categories[platform_type] += 1
            
            for category, count in sorted(categories.items()):
                print(f"  {category}: {count} platforms")
            
            # Verify the 7 new platforms are in social_media category
            social_media_platforms = [p for p in platforms.values() if p.get('type') == 'social_media']
            new_social_media = []
            
            for platform_key in new_platforms.keys():
                if platform_key in platforms and platforms[platform_key].get('type') == 'social_media':
                    new_social_media.append(platform_key)
            
            print(f"\n✅ New platforms in social_media category: {len(new_social_media)}/7")
            print(f"   {', '.join(new_social_media)}")
            
            if len(new_social_media) == 7:
                print("🎉 All 7 new platforms correctly categorized as social_media!")
            else:
                print("⚠️  Some platforms may be miscategorized")
                
        else:
            print(f"❌ Failed to get platforms: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_platform_details()