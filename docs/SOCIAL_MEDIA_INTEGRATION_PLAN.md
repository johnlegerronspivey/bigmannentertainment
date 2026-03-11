# Social Media OAuth Integration - Implementation Plan
## Full Scope Implementation Starting with Twitter/X

### Overview
Comprehensive social media integration with OAuth authentication, posting capabilities, metrics tracking, and webhook support. Starting with Twitter/X API integration using provided credentials.

### Credentials Provided
- **Twitter API Key**: ****3xzpi4 (partially masked)
- **Twitter API Secret**: kPGsAu5DXeVT6JtGLqguKsjWOnhyLtLQen0Zx32LRtN3q
- **Twitter Bearer Token**: AAAAAAAAAAAAAAAAAAAAAGed4gEAAAAAYVjuFoyKr45pY6cYyu8MVImQZDU%3DOXbNIxI10JdrMnsnTquyqs6OBg33InY0h29L0N8AtZFpNmfOkw

---

## Phase 1: Database Schema & Models ✅
**Files to Create/Modify:**
- `/app/backend/social_media_models.py` (NEW)
- `/app/backend/profile_models.py` (UPDATE - add relationships)
- `/app/backend/pg_database.py` (UPDATE - import new models)

**Database Tables:**
1. **oauth_tokens** - Store encrypted OAuth tokens
   - id, user_id, provider, access_token (encrypted), refresh_token (encrypted)
   - token_type, expires_at, scope, created_at, updated_at

2. **social_connections** - User's connected platforms
   - id, user_id, provider, platform_user_id, username, connected_at
   - is_active, last_sync, profile_data (JSON)

3. **social_posts** - Posted content tracking
   - id, user_id, content, media_urls (JSON), platforms (array)
   - scheduled_for, posted_at, status, platform_post_ids (JSON)

4. **social_metrics** - Analytics data
   - id, post_id, provider, metrics_data (JSON)
   - collected_at, likes, shares, comments, views, engagement_rate

---

## Phase 2: OAuth Provider Registry ✅
**Files to Create/Modify:**
- `/app/backend/oauth_config.py` (NEW) - Centralized provider configuration
- `/app/backend/.env` (UPDATE) - Add Twitter credentials
- `/app/backend/social_oauth_service.py` (UPDATE) - Enhanced OAuth flow

**Features:**
- Dynamic provider registration
- Environment-based configuration
- OAuth 2.0 flow for Twitter
- Token encryption/decryption utilities
- Automatic token refresh logic

---

## Phase 3: Twitter API Integration ✅
**Files to Create/Modify:**
- `/app/backend/providers/twitter_provider.py` (NEW)
- `/app/backend/providers/__init__.py` (NEW)
- `/app/backend/social_api_service.py` (NEW)

**Twitter API Endpoints to Integrate:**
1. **OAuth 2.0 Flow**
   - Authorization URL generation
   - Token exchange
   - Token refresh

2. **Posting API** (Twitter API v2)
   - POST /2/tweets
   - Media upload support
   - Thread posting

3. **Metrics API**
   - GET /2/tweets/:id/metrics
   - User metrics
   - Engagement analytics

4. **User Profile**
   - GET /2/users/me
   - Public metrics retrieval

---

## Phase 4: Abstract Provider Interface ✅
**Files to Create:**
- `/app/backend/providers/base_provider.py` (NEW)
- `/app/backend/providers/twitter_provider.py` (ENHANCE)

**Base Provider Class Methods:**
```python
class BaseSocialProvider:
    - connect_oauth()
    - refresh_token()
    - post_content(content, media)
    - get_post_metrics(post_id)
    - get_user_metrics()
    - verify_webhook(payload, signature)
    - handle_webhook_event(event)
```

---

## Phase 5: Unified API Endpoints ✅
**Files to Create/Modify:**
- `/app/backend/social_integration_endpoints.py` (NEW)
- `/app/backend/server.py` (UPDATE - register router)

**New Endpoints:**
```
POST   /api/social/connect/{provider}       - Initiate OAuth
GET    /api/social/callback/{provider}      - OAuth callback
POST   /api/social/disconnect/{provider}    - Disconnect account
GET    /api/social/connections              - List connections
POST   /api/social/post                     - Unified posting
GET    /api/social/posts                    - List user posts
GET    /api/social/posts/{post_id}          - Get post details
DELETE /api/social/posts/{post_id}          - Delete post
GET    /api/social/metrics/dashboard        - Aggregated metrics
GET    /api/social/metrics/post/{post_id}   - Post-specific metrics
POST   /api/social/webhook/{provider}       - Webhook receiver
GET    /api/social/webhook/verify           - Webhook verification
```

---

## Phase 6: Frontend Integration ✅
**Files to Modify:**
- `/app/frontend/src/SocialMediaDashboard.js` (UPDATE)
- `/app/frontend/src/ProfileSettings.js` (UPDATE)
- `/app/frontend/src/components/OAuthConnect.js` (NEW)
- `/app/frontend/src/components/PostComposer.js` (NEW)

**Features:**
1. **OAuth Connection Flow**
   - Connect Twitter button
   - OAuth popup/redirect flow
   - Connection status indicator

2. **Real-Time Dashboard**
   - Live metrics from Twitter API
   - Connection status
   - Follower count, engagement rate

3. **Post Composer**
   - Rich text editor
   - Media upload
   - Platform selection
   - Schedule for later
   - Preview before posting

4. **Analytics View**
   - Post performance charts
   - Engagement trends
   - Best posting times

---

## Phase 7: Security & Compliance ✅
**Files to Create/Modify:**
- `/app/backend/encryption_utils.py` (NEW)
- `/app/backend/rate_limiter.py` (NEW)
- `/app/backend/audit_logger.py` (ENHANCE)

**Security Features:**
1. **Token Encryption**
   - Encrypt access/refresh tokens at rest
   - Use Fernet symmetric encryption
   - Store encryption key in environment

2. **Rate Limiting**
   - API endpoint rate limits
   - Twitter API rate limit handling
   - Retry with exponential backoff

3. **Audit Logging**
   - Log all OAuth connections
   - Log all post operations
   - Log all API calls

4. **Webhook Security**
   - Signature verification
   - Payload validation
   - Replay attack prevention

---

## Phase 8: Testing & Validation ✅
**Testing Strategy:**
1. **Backend Testing**
   - Test OAuth flow with real Twitter credentials
   - Test posting functionality
   - Test metrics retrieval
   - Verify webhook handling

2. **Frontend Testing**
   - Test connection flow
   - Test post composer
   - Test metrics dashboard
   - Responsive design verification

3. **Integration Testing**
   - End-to-end OAuth flow
   - Post creation and verification on Twitter
   - Metrics accuracy validation

---

## Implementation Order

### Step 1: Database Foundation (30 min)
- Create social_media_models.py
- Update pg_database.py
- Run migrations

### Step 2: OAuth Configuration (30 min)
- Create oauth_config.py
- Update .env with Twitter credentials
- Enhance social_oauth_service.py

### Step 3: Provider Implementation (1 hour)
- Create base_provider.py
- Implement twitter_provider.py
- Add encryption utilities

### Step 4: API Endpoints (1 hour)
- Create social_integration_endpoints.py
- Implement all unified endpoints
- Add to server.py

### Step 5: Frontend Enhancement (1 hour)
- Update SocialMediaDashboard.js
- Create OAuth connect component
- Implement real API calls

### Step 6: Security & Testing (30 min)
- Add rate limiting
- Enhance audit logging
- Run comprehensive tests

**Total Estimated Time: 4-5 hours**

---

## Success Criteria
✅ Users can connect Twitter account via OAuth 2.0  
✅ Users can post tweets from BME platform  
✅ Real-time metrics displayed in dashboard  
✅ Tokens encrypted and securely stored  
✅ Webhooks functional for event notifications  
✅ Rate limiting prevents API abuse  
✅ Comprehensive audit trail maintained  
✅ All tests passing (backend & frontend)  

---

## Future Enhancements (Post-MVP)
- Add Facebook, Instagram, TikTok, LinkedIn
- Scheduled posting with job queue (Celery)
- AI-powered content suggestions
- Multi-image/video post support
- Analytics export (CSV/PDF)
- Team collaboration features
