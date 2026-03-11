# Creator Profile System - Setup Guide

## 🎯 Overview
Comprehensive creator profile system with:
- **Dual Database**: PostgreSQL (profiles) + MongoDB (existing)
- **GS1 Integration**: GTIN, GLN, ISRC, ISAN, QR codes
- **DAO Governance**: Proposals, voting, royalty adjustments
- **Social OAuth**: Facebook, Instagram, TikTok, YouTube, Twitter
- **Integration**: User auth, ULN, media upload, earnings

## 📦 Components Created

### Backend Files
1. `pg_database.py` - PostgreSQL connection manager
2. `profile_models.py` - SQLAlchemy models (11 tables)
3. `gs1_profile_service.py` - GS1 identifier generation
4. `profile_service.py` - Profile data aggregation service
5. `profile_endpoints.py` - FastAPI REST endpoints
6. `social_oauth_service.py` - OAuth integration
7. `init_profiles.py` - Database initialization script

### Database Models
- **UserProfile**: Creator profiles with GS1 metadata
- **Asset**: Content with GTIN/ISRC/ISAN
- **Royalty**: Payment tracking
- **Sponsor**: Sponsorship management
- **TraceEvent**: EPCIS-style traceability
- **Comment**: Fan engagement
- **Proposal**: DAO governance proposals
- **Vote**: Weighted voting system
- **SocialConnection**: OAuth token management

## 🔧 Setup Instructions

### Step 1: PostgreSQL Database

**Option A: AWS RDS (Recommended for Production)**
1. Create PostgreSQL instance on AWS RDS
2. Note connection details

**Option B: Heroku Postgres**
1. Add Heroku Postgres addon
2. Get DATABASE_URL from config vars

**Option C: Local Docker (Development)**
```bash
docker run --name bigmann-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=bigmann_profiles \
  -p 5432:5432 \
  -d postgres:15
```

### Step 2: Environment Variables

Add to `/app/backend/.env`:

```bash
# PostgreSQL Connection
POSTGRES_URL=postgresql+asyncpg://username:password@host:port/database
# Example: postgresql+asyncpg://postgres:password@localhost:5432/bigmann_profiles

# GS1 Configuration (already set)
GS1_COMPANY_PREFIX=8600043402
GLOBAL_LOCATION_NUMBER=0860004340201
ISRC_PREFIX=QZ9H8
GS1_DIGITAL_LINK_BASE=https://id.gs1.org

# Social Media OAuth (Optional - Users will connect via UI)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
```

### Step 3: Initialize Database

```bash
cd /app/backend
python init_profiles.py
```

This creates all PostgreSQL tables.

### Step 4: Update Main Server

The profile endpoints need to be registered in `server.py`. I'll do this in the next step.

## 📡 API Endpoints

### Profile Management
- `GET /api/profile/{username}` - Get public profile
- `POST /api/profile/create` - Create profile (authenticated)
- `PUT /api/profile/update` - Update profile (authenticated)
- `GET /api/profile/me` - Get own profile (authenticated)

### Assets & GS1
- `POST /api/profile/assets/create` - Create asset with GS1 identifiers
- `GET /api/profile/assets/{asset_id}` - Get asset with QR code

### DAO Governance
- `POST /api/profile/dao/proposals/create` - Create proposal
- `POST /api/profile/dao/proposals/{id}/vote` - Vote on proposal
- `GET /api/profile/dao/proposals` - List proposals
- `GET /api/profile/dao/proposals/{id}` - Get proposal details

### Social OAuth
- `GET /api/oauth/connect/{provider}` - Initiate OAuth (facebook, tiktok, google, twitter)
- `GET /api/oauth/callback/{provider}` - OAuth callback
- `POST /api/oauth/disconnect/{provider}` - Disconnect account
- `GET /api/oauth/status` - Check OAuth config

### Health
- `GET /api/profile/health` - Service health check

## 🎨 Frontend Components (To Be Created)

### Required React Components
1. **CreatorProfilePage.jsx** - Main profile page
2. **IdentityHeader.jsx** - Profile header with social links
3. **ContentGrid.jsx** - Asset grid with GS1 metadata
4. **AssetCard.jsx** - Individual asset cards
5. **TraceabilityTimeline.jsx** - EPCIS event timeline
6. **RoyaltyDashboard.jsx** - Earnings overview
7. **DAOGovernance.jsx** - Proposals and voting
8. **SocialConnections.jsx** - OAuth integration UI
9. **ProfileSettings.jsx** - Profile management
10. **QRCodeDisplay.jsx** - GS1 QR code viewer

### Routing
Add to App.js:
```jsx
<Route path="/profile/:username" element={<CreatorProfilePage />} />
<Route path="/profile/settings" element={<ProtectedRoute><ProfileSettings /></ProtectedRoute>} />
<Route path="/assets/:assetId" element={<AssetDetailPage />} />
```

## 🔐 OAuth Setup Instructions

### Facebook/Instagram
1. Go to https://developers.facebook.com
2. Create new app
3. Add Facebook Login and Instagram Basic Display
4. Set redirect URI: `https://yourdomain.com/api/oauth/callback/facebook`
5. Copy App ID and App Secret to .env

### TikTok
1. Go to https://developers.tiktok.com
2. Create new app
3. Add "Login Kit" and "Video Kit"
4. Set redirect URI: `https://yourdomain.com/api/oauth/callback/tiktok`
5. Copy Client Key and Client Secret to .env

### YouTube (Google)
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Set redirect URI: `https://yourdomain.com/api/oauth/callback/google`
6. Copy Client ID and Client Secret to .env

### Twitter
1. Go to https://developer.twitter.com
2. Create new app
3. Enable OAuth 2.0
4. Set redirect URI: `https://yourdomain.com/api/oauth/callback/twitter`
5. Copy Client ID and Client Secret to .env

## 🧪 Testing

### Test Profile Creation
```bash
curl -X POST https://yourdomain.com/api/profile/create \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "John Spivey",
    "tagline": "Empowering creators",
    "bio": "Founder of Big Mann Entertainment",
    "location": "Montgomery, AL"
  }'
```

### Test Asset Creation with GS1
```bash
curl -X POST https://yourdomain.com/api/profile/assets/create \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Freedom Flow",
    "asset_type": "music",
    "description": "Hip-hop track",
    "license": "Creative Commons BY-NC"
  }'
```

### View Profile
```bash
curl https://yourdomain.com/api/profile/johnspivey
```

## 🔄 Integration with Existing Features

### User Registration
When user registers, automatically create profile:
```python
# In registration endpoint
from profile_service import profile_service

profile = await profile_service.create_profile(
    mongo_user_id=user.id,
    username=user.email.split('@')[0],
    data={"display_name": user.email.split('@')[0]}
)
```

### Media Upload
When user uploads media, create asset:
```python
# In upload endpoint
from profile_service import profile_service

asset = await profile_service.create_asset(
    user_id=profile_id,
    asset_data={
        "title": media_title,
        "asset_type": "music",  # or video, image
        "mongo_media_id": media.id,
        "thumbnail_url": media.thumbnail,
        "content_url": media.url
    }
)
# Returns GTIN, ISRC, QR code, etc.
```

### Earnings Dashboard
Link PostgreSQL royalties to existing earnings:
```python
# Sync royalties from MongoDB to PostgreSQL
# This allows public display if user enables it
```

### ULN Integration
Link labels to creator profiles:
```python
# In ULN service, reference profile GLN
# Enable cross-label content sharing with GS1 traceability
```

## 📊 Database Schema

### PostgreSQL Tables
- `user_profiles` - Creator profiles
- `assets` - Content with GS1 identifiers
- `royalties` - Payment tracking
- `sponsors` - Sponsorships
- `trace_events` - Traceability log
- `comments` - User comments
- `proposals` - DAO proposals
- `votes` - DAO votes
- `social_connections` - OAuth tokens

### Indexes
- `user_profiles.username` (unique)
- `user_profiles.mongo_user_id` (unique)
- `assets.gtin` (unique)
- `assets.mongo_media_id`

## 🚀 Next Steps

1. ✅ Set up PostgreSQL database
2. ✅ Add POSTGRES_URL to .env
3. ⏳ Run init_profiles.py
4. ⏳ Update server.py to include profile routes
5. ⏳ Create frontend components
6. ⏳ Configure OAuth apps
7. ⏳ Test end-to-end flow

## 💡 Features Enabled

✅ **GS1 Compliance**: Every asset gets proper identifiers
✅ **Traceability**: Full EPCIS-style event logging
✅ **DAO Governance**: Community-driven decisions
✅ **Social Integration**: Multi-platform OAuth
✅ **Public Profiles**: SEO-friendly creator pages
✅ **QR Codes**: Scannable asset identifiers
✅ **Smart Contracts**: Ready for blockchain triggers
✅ **Royalty Transparency**: Optional public display
✅ **Fan Engagement**: Comments and interactions
✅ **Sponsorships**: Brand partnership management

## 📞 Support

For issues or questions:
1. Check logs: `tail -f /var/log/supervisor/backend.err.log`
2. Test health: `curl https://yourdomain.com/api/profile/health`
3. Verify PostgreSQL connection
