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

### Phase 14 - API Credentials Manager (2026-03-12)
- **API Credentials Reference Guide** - Comprehensive markdown guide at `/app/docs/API_CREDENTIALS_GUIDE.md` covering all 10 live adapter platforms with step-by-step credential setup instructions, developer portal links, and security best practices
- **Credentials Guide API Endpoint** - `GET /api/distribution-hub/adapters/credentials-guide` returns structured credential requirements for each live adapter (field labels, placeholders, help text, developer portal URLs, costs)
- **Enhanced Platform Connections UI** - Replaced basic single-input credential form with platform-specific credential management dashboard featuring:
  - Per-platform credential forms with labeled fields (e.g., Telegram: bot_token + chat_id, Bluesky: handle + app_password)
  - Quick Setup instructions with developer portal links for each platform
  - Password visibility toggles for sensitive fields
  - Status bar showing connected/available/total live adapter counts
  - Search/filter for available platforms
  - Platform-branded color accents for visual distinction

### Phase 15 - Live Social Media Integrations & CloudFront Setup (2026-03-13)
- **AWS CloudFront CDN Distribution** - Programmatically created CloudFront distribution (E2LURX26QTXMXJ) for S3 media bucket using AWS access keys. Distribution domain: d3brubd69k8lxz.cloudfront.net. Auto-saved to .env.
- **Twitter/X Live Integration** - Bearer token-based connection (read-only), OAuth 2.0 PKCE flow for write access (tweet.read, tweet.write, users.read, offline.access). Auth URL generation with code_verifier/code_challenge.
- **TikTok Live Integration** - OAuth 2.0 flow with client_key/client_secret for user authorization (user.info.basic, video.publish). Token exchange and refresh support.
- **Snapchat Live Integration** - JWT Canvas S2S token from env for read+write. New SnapchatAdapter added to platform_adapters.py for content delivery via Ads/Creative API. Snapchat metrics adapter added to live_metrics_service.
- **Live Integrations Dashboard** - New `/integrations` page with tabs: Social Platforms (connection status, test buttons, OAuth connect), Infrastructure (CloudFront status), Test Results
- **OAuth Callback Handler** - `/oauth/callback` page handles return from Twitter/TikTok OAuth flows with PKCE verification
- **Env-Var Credential Fallback** - Delivery engine falls back to .env credentials when user hasn't saved platform-specific credentials
- **Credential Management API** - Save, retrieve (masked), and test credentials for any platform
- **11 Platform Delivery Adapters** - Added Snapchat to existing 10 (YouTube, Twitter/X, TikTok, SoundCloud, Vimeo, Bluesky, Discord, Telegram, Instagram, Facebook)

### Phase 16 - Live Write Actions & Multi-Platform Publishing (2026-03-13)
- **Unified Multi-Platform Publish** - `POST /api/integrations/publish` accepts text, target platforms array, and optional media_url. Posts to all selected platforms simultaneously using stored OAuth tokens, returns per-platform results with success/error details.
- **Publish History** - `GET /api/integrations/publish/history` returns recent publish records with text, platforms, results, succeeded/total counts, and timestamps. Stored in MongoDB `publish_history` collection.
- **Twitter/X Write API** - `POST /api/integrations/twitter/tweet` posts tweets using OAuth 2.0 user access token (requires write scope via OAuth flow).
- **TikTok Write API** - `POST /api/integrations/tiktok/publish` supports video publishing via PULL_FROM_URL and photo publishing. Requires OAuth user token with video.publish scope.
- **Snapchat Write API** - `POST /api/integrations/snapchat/publish` creates Snap Ad creatives via the Ads API using JWT token. Verifies org, fetches ad accounts, creates creative.
- **Publish Composer UI** - New "Publish" tab (default) on Live Integrations page with:
  - Text area with 280-character counter
  - Optional media URL input (required for TikTok video)
  - Platform selector buttons showing connected/not-connected state
  - Disabled state for unconnected platforms with clear "(not connected)" label
  - "Publish Now" button with loading state
- **Publish Results Display** - Per-platform success/failure cards with platform icons, badges, and error messages
- **Publish History Feed** - Recent posts section showing text preview, platform indicators (green/red dots), succeeded/total badge, and timestamp

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local disk `/app/uploads/content/`, `/app/uploads/hub/`
- **CDN**: AWS CloudFront (d3brubd69k8lxz.cloudfront.net) -> S3 bigmann-entertainment-media
- **Key Routes**: `/app/backend/routes/` (24 core routers) + `/app/backend/api/` (78 endpoint routers)
- **Real-time**: WebSocket at `/api/ws/notifications` and `/api/ws/sla`

### Backend Directory Structure
```
/app/backend/
├── server.py              # Entry point
├── startup.py             # Startup/shutdown hooks
├── router_setup.py        # Additional router wiring
├── middleware.py           # HTTP middleware
├── api/                   # 78 endpoint modules
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
- Delivery Engine: `GET /api/distribution-hub/adapters`, `GET /api/distribution-hub/adapters/credentials-guide`, `GET /api/distribution-hub/deliveries/batch/{id}/progress`
- Live Integrations: `GET /api/integrations/status/all`, `GET /api/integrations/{platform}/test`, `GET /api/integrations/{platform}/auth-url`, `POST /api/integrations/{platform}/callback`, `GET /api/integrations/cloudfront/status`, `POST /api/integrations/cloudfront/setup`, `POST /api/integrations/credentials/save`
- **Publishing**: `POST /api/integrations/publish`, `GET /api/integrations/publish/history`, `POST /api/integrations/twitter/tweet`, `POST /api/integrations/tiktok/publish`, `POST /api/integrations/snapchat/publish`
- Analytics: `GET /api/analytics/overview`, `GET /api/analytics/content-performance`
- Anomaly Detection: `POST /api/analytics/anomalies/scan`, `GET /api/analytics/anomalies`
- Demographics: `GET /api/analytics/demographics`, `GET /api/analytics/best-times`, `GET /api/analytics/geo`
- Revenue: `GET /api/analytics/revenue/overview`, `GET /api/analytics/revenue/platform/{id}`

## DB Collections
- `notifications`, `content_comments`, `user_content`, `messages`, `conversations`, `subscriptions`
- `platform_credentials`, `distribution_hub_content`, `distribution_hub_deliveries`, `distribution_hub_credentials`
- `anomaly_alerts`, `metrics_history`, `audience_analytics`, `revenue_tracking`
- `publish_history`

## 3rd Party Integrations
- Stripe, PayPal (payments)
- AWS Services (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, etc.)
- Google Generative AI
- Social Media Live APIs (Twitter v2, YouTube Data v3, Instagram Graph, etc.)
- URL-based public scraping (25 platforms)

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Verification Status (2026-03-13)
All features verified and signed off:
- **P0**: Distribution Hub Public Content URLs - VERIFIED
- **P1**: Creator Analytics (Anomaly Detection, Demographics, Revenue, Best Times, Geo) - VERIFIED
- **P2**: Distribution Hub Live Delivery Engine (10 adapters) - VERIFIED
- **P3**: New Comment Real-Time Notifications - VERIFIED
- **P4**: 120 Platform Expansion (123 platforms, 16 categories) - VERIFIED
- **P14**: API Credentials Manager & Guide - VERIFIED
- **P15**: CloudFront CDN Setup (E2LURX26QTXMXJ) - VERIFIED
- **P15**: Twitter/X Live Integration (Bearer + OAuth) - VERIFIED
- **P15**: TikTok Live Integration (OAuth flow) - VERIFIED
- **P15**: Snapchat Live Integration (JWT + Adapter) - VERIFIED
- **P15**: Live Integrations Dashboard UI - VERIFIED
- **P16**: Multi-Platform Write Actions & Publish UI - VERIFIED (2026-03-13)

### Phase 17 - CVE Vulnerability Remediation (2026-02-27)
- **Frontend: 11 CVE vulnerabilities resolved** via yarn resolutions:
  - `minimatch` 10.2.2 → >=10.2.3 (CVE-2026-27903, CVE-2026-27904 — ReDoS HIGH)
  - `hono` 4.12.2 → >=4.12.7 (CVE-2026-29045 arbitrary file access HIGH, CVE-2026-29086 cookie injection MODERATE, CVE-2026-29085 SSE injection MODERATE, prototype pollution MODERATE)
  - `serialize-javascript` 6.0.2 → >=7.0.3 (RCE HIGH)
  - `flatted` 3.3.2 → >=3.4.0 (CVE-2026-32141 DoS HIGH)
  - `rollup` 2.79.2 → >=2.80.0 (CVE-2026-27606 path traversal HIGH)
  - `svgo` 1.3.2 → >=2.8.1 (CVE-2026-29074 Billion Laughs DoS HIGH)
  - `fast-xml-parser` 5.3.7 → >=5.3.8 (CVE-2026-27942 stack overflow LOW)
  - `@tootallnate/once` 1.1.2 → >=3.0.1 (CVE-2026-3449 LOW)
- **Backend: 2 CVE vulnerabilities resolved** via pip upgrade:
  - `authlib` 1.6.6 → 1.6.7 (GHSA-7wc2-qxgw-g8gg)
  - `awscli` 1.42.25 → 1.44.58 (GHSA-747p-wmpv-9c78)
- **Final audit: 0 vulnerabilities** on both frontend and backend

## Backlog
- **P1**: Post-scheduling functionality to connected social media accounts
- **P2**: Enhanced content preview (lightbox/modal for full-size viewing)
- **P2**: Replace mock data in analytics with real API-sourced data
- **P3**: Real-time WebSocket delivery status updates (currently uses polling)
- **P3**: Revenue auto-import from platform APIs when credentials are connected
