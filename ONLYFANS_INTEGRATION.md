# OnlyFans Integration Guide

## Overview

OnlyFans has been successfully integrated into the BME platform as both a distribution platform and a social media platform for content creators.

---

## 🎯 Integration Details

### Platform Information

**Name**: OnlyFans  
**Type**: Social Media / Content Subscription Platform  
**Category**: social_media  
**Icon**: 💎

**API Endpoint**: `https://onlyfans.com/api2/v2`

**Supported Formats**:
- Images
- Videos
- Audio

**Maximum File Size**: 500 MB (524,288,000 bytes)

**Required Credentials**:
- `user_id` - OnlyFans user ID
- `auth_token` - Authentication token
- `user_agent` - User agent string for API requests

**Description**: Content subscription and monetization platform for creators

---

## 📍 Where OnlyFans Appears

### 1. Distribution Platforms
OnlyFans is now available in the main distribution platforms list at:
- `/api/distribution/platforms` - Backend API
- `/platforms` - Frontend platforms page
- `/distribute` - Distribution interface

**Total Platforms**: 119 (increased from 118)

### 2. Enhanced Features - Social Platform Distribution
OnlyFans is available in the AI-powered social distribution feature at:
- `/enhanced-features` - Enhanced Features Dashboard
- Social Platform Native Distribution tab

**Available Alongside**:
- TikTok 🎵
- YouTube Shorts ▶️
- Instagram Reels 📸
- OnlyFans 💎

---

## 🚀 How to Use OnlyFans Distribution

### Backend API

**Create Distribution**:
```bash
POST /api/enhanced/social-distribution/create

{
  "media_id": "media-123",
  "platforms": ["onlyfans", "tiktok", "instagram_reels"],
  "caption": "New exclusive content! 💎",
  "hashtags": ["exclusive", "content", "newpost"],
  "scheduled_time": "2025-12-01T18:00:00Z",
  "auto_optimize_format": true
}
```

**Response**:
```json
{
  "id": "dist-456",
  "media_id": "media-123",
  "platform": "onlyfans",
  "status": "pending",
  "caption": "New exclusive content! 💎",
  "hashtags": ["exclusive", "content", "newpost"],
  "views": 0,
  "likes": 0,
  "shares": 0,
  "comments": 0,
  "created_at": "2025-11-12T17:30:00Z"
}
```

### Frontend Interface

**Access Dashboard**:
1. Navigate to `/enhanced-features`
2. Click on "🚀 Social Distribution" tab
3. Enter Media ID
4. Select platforms (including OnlyFans 💎)
5. Add caption and hashtags
6. Optionally schedule posting time
7. Click "Create Distribution"

**Platform Selection**:
The OnlyFans option appears as a button with:
- Icon: 💎
- Label: OnlyFans
- Visual styling with purple/blue theme
- Multi-select capability

---

## 💡 Use Cases

### 1. Multi-Platform Content Strategy
Distribute the same content across multiple platforms simultaneously:
- **OnlyFans**: Premium/exclusive content for subscribers
- **TikTok**: Short-form teaser content
- **Instagram Reels**: Visual highlights
- **YouTube Shorts**: Extended previews

### 2. Content Monetization
Use OnlyFans as the primary monetization platform while using other platforms for audience growth and engagement.

### 3. Scheduled Releases
Schedule content releases across OnlyFans and other platforms for coordinated marketing campaigns.

### 4. Engagement Tracking
Track engagement metrics across all platforms including:
- Views
- Likes
- Shares
- Comments

---

## 🔧 Technical Specifications

### Backend Models

**Enum Addition**:
```python
class SocialPlatformType(str, Enum):
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    ONLYFANS = "onlyfans"  # ← NEW
```

**Distribution Platform Entry**:
```python
"onlyfans": {
    "type": "social_media",
    "name": "OnlyFans",
    "api_endpoint": "https://onlyfans.com/api2/v2",
    "supported_formats": ["image", "video", "audio"],
    "max_file_size": 500 * 1024 * 1024,  # 500 MB
    "credentials_required": ["user_id", "auth_token", "user_agent"],
    "description": "Content subscription and monetization platform for creators"
}
```

### Frontend Component

**Platform Options**:
```javascript
const platformOptions = [
  { value: 'tiktok', label: 'TikTok', icon: '🎵' },
  { value: 'youtube_shorts', label: 'YouTube Shorts', icon: '▶️' },
  { value: 'instagram_reels', label: 'Instagram Reels', icon: '📸' },
  { value: 'onlyfans', label: 'OnlyFans', icon: '💎' }  // ← NEW
];
```

---

## 📊 API Endpoints

### Distribution Platform Endpoints

**Get All Platforms (includes OnlyFans)**:
```bash
GET /api/distribution/platforms

Response:
{
  "total": 119,
  "platforms": [
    {
      "name": "OnlyFans",
      "type": "social_media",
      "api_endpoint": "https://onlyfans.com/api2/v2",
      "supported_formats": ["image", "video", "audio"],
      "max_file_size": 524288000,
      "credentials_required": ["user_id", "auth_token", "user_agent"],
      "description": "Content subscription and monetization platform for creators"
    }
    // ... other platforms
  ]
}
```

### Social Distribution Endpoints

**Create OnlyFans Distribution**:
```bash
POST /api/enhanced/social-distribution/create
```

**Get Distribution Status**:
```bash
GET /api/enhanced/social-distribution/{distribution_id}
```

**Get All Distributions for Media**:
```bash
GET /api/enhanced/social-distribution/media/{media_id}
```

**Update Engagement Metrics**:
```bash
PUT /api/enhanced/social-distribution/{distribution_id}/update-metrics
{
  "views": 1500,
  "likes": 230,
  "shares": 45,
  "comments": 67
}
```

---

## 🔐 Authentication & Credentials

### Required OnlyFans Credentials

To use OnlyFans distribution, you'll need:

1. **User ID**: Your OnlyFans user ID
2. **Auth Token**: API authentication token from OnlyFans
3. **User Agent**: Valid user agent string for API requests

### How to Obtain Credentials

**Note**: OnlyFans API access is typically restricted. Credentials should be obtained through:
- Official OnlyFans API partner programs
- Creator API access (if available)
- OnlyFans business development contacts

**Security Note**: Store credentials securely in environment variables or encrypted storage.

---

## 🧪 Testing

### Test OnlyFans Integration

**Backend Test**:
```bash
# Verify OnlyFans in platforms list
curl http://localhost:8001/api/distribution/platforms | jq '.platforms[] | select(.name == "OnlyFans")'

# Test distribution creation
curl -X POST http://localhost:8001/api/enhanced/social-distribution/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "media_id": "test-media",
    "platforms": ["onlyfans"],
    "caption": "Test post",
    "hashtags": ["test"]
  }'
```

**Frontend Test**:
1. Access `/enhanced-features`
2. Navigate to Social Distribution tab
3. Verify OnlyFans 💎 button appears in platform options
4. Select OnlyFans
5. Create test distribution
6. Verify distribution appears in history

---

## 📈 Platform Statistics

**Updated Platform Counts**:
- **Total Platforms**: 119 (was 118)
- **Social Media Platforms**: 22 (was 21)
- **OnlyFans Position**: Listed in social_media category

**Platform Breakdown**:
- Social Media: 22 platforms (including OnlyFans)
- Music Streaming: 27 platforms
- Podcast: 8 platforms
- Radio: 10 platforms
- Video Streaming: 9 platforms
- Rights Organizations: 5 platforms
- Blockchain/Web3: 10 platforms
- International: 8 platforms
- Additional: 20 platforms

---

## 🎯 Benefits for Creators

### Revenue Opportunities
- **Subscription Model**: Earn recurring revenue from subscribers
- **Pay-Per-View**: Monetize individual content pieces
- **Tips & Donations**: Accept direct payments from fans
- **Exclusive Content**: Premium pricing for exclusive content

### Audience Engagement
- **Direct Connection**: Build direct relationships with subscribers
- **Content Control**: Full control over content distribution
- **Analytics**: Track subscriber growth and engagement
- **Community Building**: Create exclusive communities

### Multi-Platform Strategy
- **Cross-Promotion**: Use other platforms to drive OnlyFans subscriptions
- **Content Repurposing**: Adapt content for different platforms
- **Audience Diversification**: Reach audiences across multiple platforms
- **Brand Building**: Maintain consistent presence across platforms

---

## 📝 Best Practices

### Content Strategy
1. **Exclusive Content**: Reserve premium content for OnlyFans
2. **Teasers**: Use other platforms for promotional content
3. **Consistency**: Maintain regular posting schedule
4. **Quality**: Ensure high-quality content for subscribers

### Distribution Workflow
1. **Create Content**: Prepare content in supported formats
2. **Multi-Platform**: Select OnlyFans + other platforms
3. **Schedule**: Use scheduling for optimal timing
4. **Engage**: Monitor and respond to engagement metrics
5. **Analyze**: Review performance across platforms

### Monetization
1. **Tiered Content**: Offer different content tiers
2. **Promotional Pricing**: Use strategic pricing for growth
3. **Bundle Offerings**: Combine subscription with pay-per-view
4. **Cross-Platform**: Drive traffic from free to paid platforms

---

## 🚧 Current Limitations

- OnlyFans API is not publicly available; implementation requires official API access
- Credentials must be obtained through official channels
- Actual posting functionality requires API authentication setup
- Metrics tracking requires webhook integration with OnlyFans

**Note**: This integration provides the infrastructure and interface for OnlyFans distribution. Actual API connectivity requires official OnlyFans API credentials and authentication setup.

---

## 📞 Support & Resources

**BME Platform**:
- Enhanced Features Dashboard: `/enhanced-features`
- Distribution Platforms: `/platforms`
- API Documentation: `/api/docs`

**OnlyFans Resources**:
- Official Website: https://onlyfans.com
- Creator Support: https://onlyfans.com/help
- Business Inquiries: Contact OnlyFans business development

---

**Implementation Date**: November 12, 2025  
**Status**: ✅ Platform Integration Complete  
**Total Platforms**: 119  
**Enhanced Features**: ✅ Social Distribution Enabled
