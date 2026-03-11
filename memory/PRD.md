# Big Mann Entertainment - Product Requirements Document

## Original Problem Statement
Build a comprehensive creator tools platform for Big Mann Entertainment that enables content management, distribution, analytics, messaging, and monetization for music/media creators.

## URL Configuration
- **Production Domain**: `bigmannentertainment.com`
- **Preview/Testing**: Uses Emergent preview URL (kept separate from production)
- All backend services reference `bigmannentertainment.com` for production contexts (emails, payments, OAuth, CORS, CDN, distribution hub source-of-truth)

## Core Features Implemented

### Phase 1 (Previous Sessions)
- User authentication (JWT-based)
- Creator profiles
- Media content upload & distribution
- Subscription/payment system (Stripe, PayPal)
- Watermarking
- Admin panel & moderation
- AWS integrations (S3, SES, CloudFront, Lambda, Rekognition, etc.)
- Web3/DAO governance
- Security (GuardDuty, Macie, QLDB)
- Infrastructure as Code management

### Phase 2 (Previous Session)
- **Content Management** - Upload & manage creator content with search/filter
- **Direct Messaging** - User-to-user messaging system
- **Analytics Dashboard** - Creator insights on content & subscribers

### Phase 3 - File Preview & Notifications
- **File Preview in Content Management** - Image thumbnails, audio player, video player
- **Real-time Notifications** - Bell icon, dropdown panel, full page, WebSocket push
- **New Comment Notifications** - Comment system with real-time notification to content owners

### Phase 4 - Refactoring
- **server.py Refactoring** - Extracted middleware, startup logic, WebSocket/webhook routes

### Phase 5 - Social Media Platform Connections
- **120 Platform Connections Dashboard** - Credential management for all 120 distribution platforms
- **Social Posts** - Create and list posts to connected platforms

### Phase 6 - Real-Time Platform Analytics
- **Analytics Tab** - Aggregate metrics, category breakdown, platform performance
- **Refresh Metrics** - One-click refresh for all platform metrics

### Phase 7 - Live Social Media API Integrations
- **14 Live API Adapters** - Twitter/X, YouTube, Instagram, Facebook, Spotify, TikTok, etc.
- **Graceful Fallback** - Falls back to simulated metrics when API calls fail
- **Metric Caching** - 5-minute TTL in MongoDB

### Phase 8 - URL-Based Platform Connections
- **URL Connect System** - Users paste profile URLs instead of API keys
- **25 URL Metric Adapters** - YouTube, Twitter, Reddit, TikTok, Instagram, etc.
- **123 Total Platforms**

### Phase 9 - Content Distribution Hub
- **Distribution Hub** - Central command center for content distribution to 120 commercial platforms
- **12 System Templates** - Pre-built distribution templates
- **Content Management** - Upload, manage, organize audio/video/image/film content
- **Metadata & Rights Management** - ISRC, UPC, copyright, licensing, royalty splits

### Phase 10 - Real Delivery Engine (2026-03-11)
- **Delivery Engine** - Background processor that executes real API delivery to platforms
- **10 Platform Adapters** - YouTube, Twitter/X, TikTok, SoundCloud, Vimeo, Bluesky, Discord, Telegram, Instagram, Facebook
- **Graceful Credential Fallback** - Auto-push with credentials, export package without
- **Retry Logic** - Up to 3 retries for failed deliveries with exponential backoff
- **Batch Progress Tracking** - Real-time progress polling during delivery
- **Delivery Status Pipeline** - queued -> preparing -> delivering -> delivered/failed/export_ready

### Phase 10.1 - App URL-Based Content Delivery (2026-03-11)
- **APP_BASE_URL Integration** - All platform adapters now use the app's own URL as the base for content delivery
- **Public File URL Resolution** - Content files are served via `APP_BASE_URL + file_path`
- **Adapter-level URL Injection** - Each adapter includes the public content URL in posts/embeds/captions
- **Export Package Source of Truth** - Export packages reference the app URL as the canonical source

### Phase 11 - Advanced Analytics (2026-03-11)
- **Automated Anomaly Detection** - Z-score statistical analysis on platform metrics
- **Audience Demographics** - Age distribution, gender split, interest categories, device breakdown
- **Geographic Distribution** - Country-level audience breakdown with listener counts
- **Best Time to Post** - 7x24 engagement heatmap, recommended posting windows
- **Revenue Tracking** - Per-platform revenue across 10 platforms, revenue by source, 12-month trend

### Phase 12 - Codebase Consolidation (2026-03-11)
- **Backend File Reorganization** - Moved 232 loose .py files from `/app/backend/` root into organized subdirectories:
  - `api/` - 77 endpoint files
  - `services/` - 107 service files (91 moved + 16 existing)
  - `models/` - 30 model files (27 moved + 3 existing)
  - `utils/` - 34 utility/miscellaneous files
  - Root retains only: `server.py`, `startup.py`, `router_setup.py`, `middleware.py`
- **Root-level Cleanup** - Moved 82 markdown docs to `/app/docs/`, 179 legacy test scripts to `/app/tests/legacy/`, 7 admin scripts to `/app/scripts/`
- **sys.path Backward Compatibility** - Added `api/`, `services/`, `models/`, `utils/` to Python path in `server.py` so all existing bare imports continue to work

### Phase 13 - API Documentation & Developer Onboarding (2026-03-11)
- **Auto-Generated Swagger/OpenAPI** - Configured FastAPI with `docs_url=/api/docs`, `redoc_url=/api/redoc`, `openapi_url=/api/openapi.json`
- **Rich API Metadata** - Added description with capabilities table, auth instructions, rate limiting info, contact, license, and terms of service
- **98 OpenAPI Tags** - All endpoint groups categorized with descriptions covering 1,281 paths and 1,399 total endpoints
- **Developer Onboarding Guide** - Comprehensive 600+ line guide at `/app/docs/DEVELOPER_ONBOARDING.md` covering project overview, tech stack, repo structure, backend/frontend architecture, DB schema, conventions, testing, and troubleshooting

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local disk `/app/uploads/content/`, `/app/uploads/hub/`
- **Key Routes**: `/app/backend/routes/` (24 core routers) + `/app/backend/api/` (77 endpoint routers)
- **Real-time**: WebSocket at `/api/ws/notifications` and `/api/ws/sla`

### Backend Directory Structure
```
/app/backend/
├── server.py              # Entry point
├── startup.py             # Startup/shutdown hooks
├── router_setup.py        # Additional router wiring
├── middleware.py           # HTTP middleware
├── api/                   # 77 endpoint modules
├── services/              # 107 service modules
├── models/                # 30 data model modules
├── utils/                 # 34 utility modules
├── routes/                # 24 core route modules
├── config/                # Database, settings, platforms
├── auth/                  # Authentication modules
├── providers/             # Provider modules
└── tests/                 # Backend tests
```

## Key API Endpoints
- Content: `GET/POST /api/user-content/`, `GET /api/user-content/file/{file_id}`
- Notifications: `GET /api/notifications`, `PUT /api/notifications/{id}/read`
- Messages: `GET /api/messages/conversations`, `POST /api/messages/send`
- Social Platforms: `GET /api/social/platforms`, `GET /api/social/connections`
- Distribution Hub: `GET/POST /api/distribution-hub/content`, `POST /api/distribution-hub/distribute`
- Delivery Engine: `GET /api/distribution-hub/adapters`, `GET /api/distribution-hub/deliveries/batch/{id}/progress`
- Analytics: `GET /api/analytics/overview`, `GET /api/analytics/content-performance`
- Anomaly Detection: `POST /api/analytics/anomalies/scan`, `GET /api/analytics/anomalies`
- Demographics: `GET /api/analytics/demographics`, `GET /api/analytics/best-times`, `GET /api/analytics/geo`
- Revenue: `GET /api/analytics/revenue/overview`, `GET /api/analytics/revenue/platform/{id}`

## DB Collections
- `notifications`, `content_comments`, `user_content`, `messages`, `conversations`, `subscriptions`
- `platform_credentials`, `distribution_hub_content`, `distribution_hub_deliveries`, `distribution_hub_credentials`
- `anomaly_alerts`, `metrics_history`, `audience_analytics`, `revenue_tracking`

## 3rd Party Integrations
- Stripe, PayPal (payments)
- AWS Services (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, etc.)
- Google Generative AI
- Social Media Live APIs (Twitter v2, YouTube Data v3, Instagram Graph, etc.)
- URL-based public scraping (25 platforms)

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Backlog
- **P1**: Live Social Media API Integrations (replace placeholder logic with real API calls)
- **P1**: Post-scheduling functionality to connected social media accounts
- **P2**: Enhanced content preview (lightbox/modal for full-size viewing)
- **P2**: Replace mock data in analytics with real API-sourced data
- **P3**: Real-time WebSocket delivery status updates (currently uses polling)
- **P3**: Revenue auto-import from platform APIs when credentials are connected
