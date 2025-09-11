# Social Media Phases 5-10: API Quick Reference

## Authentication
All endpoints require JWT Bearer token:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

## Base URL
```
https://your-domain.com/api/social-media-advanced
```

## Phase 5: Advanced Content Scheduling

### Create Scheduling Rule
```bash
POST /scheduling/rules
Content-Type: application/json

{
  "name": "Instagram Daily Posts",
  "platforms": ["instagram"],
  "content_types": ["image", "video"],
  "optimal_times": {
    "monday": ["09:00", "17:00"],
    "tuesday": ["10:00", "18:00"]
  },
  "frequency": "daily",
  "auto_optimize": true
}
```

### Create Content Queue
```bash
POST /scheduling/queues
Content-Type: application/json

{
  "name": "Weekly Content Queue",
  "content_items": ["content_1", "content_2"],
  "scheduling_rule_id": "rule_123",
  "is_active": true
}
```

### Batch Schedule Content
```bash
POST /scheduling/batch-schedule
Content-Type: application/json

{
  "queue_id": "queue_123",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-07T23:59:59Z"
}
```

### Optimize Posting Times
```bash
GET /scheduling/optimize-times/instagram
```

## Phase 6: Real-time Analytics

### Track Metric
```bash
POST /analytics/track-metric
Content-Type: application/json

{
  "platform": "instagram",
  "content_id": "post_123",
  "metric_type": "engagement",
  "value": 150.0,
  "metadata": {"post_type": "image"}
}
```

### Get Real-time Metrics
```bash
GET /analytics/real-time?platform=instagram&time_window=3600
```

### Generate Performance Report
```bash
POST /analytics/generate-report
Content-Type: application/json

{
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z",
  "platforms": ["instagram", "twitter"]
}
```

### Create A/B Test
```bash
POST /analytics/ab-test
Content-Type: application/json

{
  "content_variants": ["Variant A", "Variant B"],
  "platforms": ["instagram", "twitter"],
  "duration_hours": 24
}
```

## Phase 7: Community Management

### Process Engagement
```bash
POST /engagement/process
Content-Type: application/json

{
  "platform": "instagram",
  "engagement_type": "comment",
  "from_user": "user123",
  "to_user": "bigmannent",
  "content": "Love this new track!",
  "post_id": "post_456"
}
```

### Get Unified Inbox
```bash
GET /engagement/unified-inbox?status=unread&priority=high
```

### Create Auto-Response Rule
```bash
POST /engagement/auto-response-rule
Content-Type: application/json

{
  "name": "Welcome Message",
  "triggers": ["hello", "hi", "hey"],
  "response_template": "Hi {user}! Thanks for reaching out on {platform}!",
  "platforms": ["instagram", "twitter"],
  "is_active": true
}
```

## Phase 8: Campaign Orchestration

### Create Campaign
```bash
POST /campaigns/create
Content-Type: application/json

{
  "name": "Summer Album Launch",
  "description": "Promoting new summer album release",
  "start_date": "2025-06-01T00:00:00Z",
  "end_date": "2025-06-30T23:59:59Z",
  "platforms": ["instagram", "twitter", "tiktok"],
  "budget_total": 5000.0,
  "budget_allocation": {
    "instagram": 2000.0,
    "twitter": 1500.0,
    "tiktok": 1500.0
  },
  "content_templates": ["album_promo"],
  "target_audience": {
    "age_range": "18-35",
    "interests": ["music", "hip-hop"]
  },
  "goals": {
    "reach": 100000,
    "engagement": 5.0
  }
}
```

### Adapt Content for Platforms
```bash
POST /campaigns/{campaign_id}/adapt-content
Content-Type: application/json

{
  "content_id": "promo_content_1",
  "platforms": ["instagram", "twitter", "tiktok"]
}
```

### Optimize Budget Allocation
```bash
POST /campaigns/{campaign_id}/optimize-budget
Content-Type: application/json
```

### Track Campaign Performance
```bash
POST /campaigns/{campaign_id}/track-performance
Content-Type: application/json

{
  "platform": "instagram",
  "metrics": {
    "engagement_rate": 4.5,
    "reach": 25000,
    "conversions": 150
  },
  "budget_spent": 800.0
}
```

## Phase 9: Influencer Management

### Discover Influencers
```bash
POST /influencers/discover
Content-Type: application/json

{
  "categories": ["music", "lifestyle"],
  "min_followers": 10000,
  "min_engagement_rate": 3.0
}
```

### Create Partnership
```bash
POST /partnerships/create
Content-Type: application/json

{
  "influencer_id": "inf_123",
  "campaign_id": "camp_456",
  "partnership_type": "sponsored_post",
  "deliverables": ["1 Instagram post", "3 stories"],
  "compensation": {
    "amount": 1000,
    "currency": "USD"
  },
  "contract_terms": {
    "duration": "30 days",
    "exclusivity": false
  },
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z"
}
```

### Track Partnership Performance
```bash
POST /partnerships/{partnership_id}/track-performance
Content-Type: application/json

{
  "engagement_rate": 6.2,
  "reach": 50000,
  "conversions": 200,
  "roi": 2.5
}
```

### Get Brand Ambassadors
```bash
GET /partnerships/brand-ambassadors
```

## Phase 10: AI Optimization

### Generate Content Recommendations
```bash
POST /ai/content-recommendations
Content-Type: application/json

{
  "platforms": ["instagram", "twitter", "tiktok"]
}
```

### Predict Trends
```bash
POST /ai/predict-trends
Content-Type: application/json

{
  "categories": ["music", "entertainment", "technology"]
}
```

### Optimize Content for Platform
```bash
POST /ai/optimize-content
Content-Type: application/json

{
  "content": "Check out our latest album drop!",
  "target_platform": "instagram"
}
```

### Get Executive Dashboard
```bash
GET /ai/executive-dashboard
```

## Health & Status Endpoints

### Health Check
```bash
GET /health
```

### Comprehensive Status
```bash
GET /status/comprehensive
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Endpoint-specific data
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information"
}
```

## HTTP Status Codes
- `200` - OK: Request successful
- `201` - Created: Resource created successfully
- `400` - Bad Request: Invalid request data
- `401` - Unauthorized: Authentication required
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource not found
- `422` - Unprocessable Entity: Validation error
- `500` - Internal Server Error: Server error

## Rate Limits
- **Standard**: 100 requests per minute
- **Analytics**: 50 requests per minute
- **AI Endpoints**: 20 requests per minute

## Platform Types
```json
["twitter", "facebook", "instagram", "linkedin", "tiktok", "youtube", "pinterest"]
```

## Content Types
```json
["image", "video", "text", "carousel", "story", "live"]
```

## Engagement Types
```json
["comment", "mention", "direct_message", "reply", "review"]
```

## Campaign Status
```json
["draft", "scheduled", "active", "paused", "completed", "cancelled"]
```

## Partnership Types
```json
["sponsored_post", "collaboration", "brand_ambassador"]
```

---

## cURL Examples

### Authenticate and Get Token
```bash
curl -X POST "https://your-domain.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Create Scheduling Rule
```bash
curl -X POST "https://your-domain.com/api/social-media-advanced/scheduling/rules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Instagram Posts",
    "platforms": ["instagram"],
    "content_types": ["image"],
    "frequency": "daily",
    "auto_optimize": true
  }'
```

### Get Real-time Analytics
```bash
curl -X GET "https://your-domain.com/api/social-media-advanced/analytics/real-time?platform=instagram" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Campaign
```bash
curl -X POST "https://your-domain.com/api/social-media-advanced/campaigns/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Album Promotion",
    "platforms": ["instagram", "twitter"],
    "budget_total": 2000.0,
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T23:59:59Z"
  }'
```

---

*API Quick Reference v1.0*
*Last Updated: January 2025*