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
- **Root-level Cleanup** - Moved 82 markdown docs to `/app/docs/`, 7 admin scripts to `/app/scripts/`. Legacy test scripts (179) were moved to `/app/tests/legacy/` then fully removed in Phase 30.
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
- **CDN**: AWS CloudFront via `cdn.bigmannentertainment.com` (distribution E2LURX26QTXMXJ, backed by d3brubd69k8lxz.cloudfront.net) -> S3 bigmann-entertainment-media
- **Key Routes**: `/app/backend/routes/` (24 core routers) + `/app/backend/api/` (78 endpoint routers)
- **WebSockets**: `/api/ws/sla`, `/api/ws/notifications`, `/api/ws/delivery`

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
- **Scheduled Posts**: `POST /api/integrations/scheduled-posts`, `GET /api/integrations/scheduled-posts`, `PUT /api/integrations/scheduled-posts/{id}`, `DELETE /api/integrations/scheduled-posts/{id}`
- **Media Processing**: `GET /api/aws-media/status`, `GET/POST /api/aws-media/mediaconvert/jobs`, `GET /api/aws-media/mediaconvert/presets`, `GET/POST /api/aws-media/transcribe/jobs`, `GET /api/aws-media/transcribe/languages`
- **Live Streaming**: `GET /api/aws-livestream/status`, `GET/POST/DELETE /api/aws-livestream/ivs/channels`, `GET /api/aws-livestream/ivs/streams`, `GET/POST/DELETE /api/aws-livestream/mediapackage/channels`, `GET/POST/DELETE /api/aws-livestream/mediapackage/endpoints`, `GET /api/aws-livestream/mediapackage/formats`
- **Communications**: `GET /api/aws-comms/status`, `GET /api/aws-comms/workmail/organizations`, `GET/POST/DELETE /api/aws-comms/workmail/users`, `GET /api/aws-comms/workmail/groups`, `GET /api/aws-comms/connect/instances`, `GET /api/aws-comms/connect/queues`, `GET /api/aws-comms/connect/contact-flows`, `GET /api/aws-comms/connect/hours-of-operation`, `GET /api/aws-comms/connect/users`, `GET /api/aws-comms/connect/routing-profiles`
- **Security**: `GET /api/aws-security/status`, `GET/POST/DELETE /api/aws-security/waf/web-acls`, `GET/POST/DELETE /api/aws-security/waf/ip-sets`, `GET /api/aws-security/waf/rule-groups`, `GET /api/aws-security/waf/managed-rules`, `GET/POST/PUT/DELETE /api/aws-security/secrets`, `POST /api/aws-security/secrets/{name}/rotate`
- Analytics: `GET /api/analytics/overview`, `GET /api/analytics/content-performance`
- Anomaly Detection: `POST /api/analytics/anomalies/scan`, `GET /api/analytics/anomalies`
- Demographics: `GET /api/analytics/demographics`, `GET /api/analytics/best-times`, `GET /api/analytics/geo`
- Revenue: `GET /api/analytics/revenue/overview`, `GET /api/analytics/revenue/platform/{id}`

## DB Collections
- `notifications`, `content_comments`, `user_content`, `messages`, `conversations`, `subscriptions`
- `platform_credentials`, `distribution_hub_content`, `distribution_hub_deliveries`, `distribution_hub_credentials`
- `anomaly_alerts`, `metrics_history`, `audience_analytics`, `revenue_tracking`
- `publish_history`
- `scheduled_posts`
- `mediaconvert_jobs`, `transcribe_jobs`
- `ivs_channels`, `mediapackage_channels`, `mediapackage_endpoints`
- `workmail_users`
- `waf_web_acls`, `waf_ip_sets`, `managed_secrets`
- `comprehend_analyses`

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

### Phase 17.1 - CloudFront Custom Domain Setup (2026-03-14)
- **ACM Certificate** - Created SSL certificate for `cdn.bigmannentertainment.com` in us-east-1 (ARN: `arn:aws:acm:us-east-1:314108682794:certificate/10607dd1-03b6-408d-acb9-33566fff9a60`) with DNS validation via Route 53
- **CloudFront Alternate Domain** - Updated distribution E2LURX26QTXMXJ with custom domain `cdn.bigmannentertainment.com`, SNI-only SSL, TLSv1.2_2021 minimum
- **Route 53 DNS Alias** - Created A-record alias `cdn.bigmannentertainment.com` -> CloudFront distribution in hosted zone Z21AGOWAOOGWWZ
- **Backend .env Updated** - `CLOUDFRONT_DOMAIN` now set to `cdn.bigmannentertainment.com`

### Phase 18 - AWS Media Processing Integration (2026-03-14)
- **AWS MediaConvert** - Full integration for media transcoding with 7 platform-optimized presets:
  - YouTube HD 1080p, TikTok Vertical 1080x1920, Instagram Square 1080x1080, Twitter/X HD 720p
  - HLS Adaptive Streaming, MP3 Audio 320kbps, AAC Audio 256kbps
  - Automatic IAM role creation (BigMannMediaConvertRole), endpoint discovery, job submission/tracking
- **AWS Transcribe** - Auto-generate captions & subtitles for audio/video content:
  - 13 languages supported (EN, ES, FR, DE, IT, PT, JA, KO, ZH, HI, AR)
  - VTT + SRT subtitle generation, auto-language detection
  - Full transcript text extraction from S3
  - CDN-served subtitle files via `cdn.bigmannentertainment.com`
- **API Endpoints**: `/api/aws-media/status`, `/api/aws-media/mediaconvert/presets`, `/api/aws-media/mediaconvert/jobs`, `/api/aws-media/transcribe/languages`, `/api/aws-media/transcribe/jobs`
- **Frontend**: `/aws-media` page with Transcode + Transcribe tabs, job management, transcript viewer modal
- **Navigation**: Added to Tools dropdown as "Media Processing"
- **Testing**: 100% pass rate (8/8 backend, all frontend tests passed)

### Phase 19 - AWS Live Streaming Integration (2026-03-14)
- **AWS IVS (Interactive Video Service)** - Low-latency live streaming channel management:
  - Create/list/delete IVS channels with Standard/Basic types and Low/Normal latency modes
  - Stream status monitoring with viewer count, health, and state
  - Stream key management for OBS/Streamlabs/FFMPEG ingest
  - Stop active streams
- **AWS Elemental MediaPackage** - Video origination & content packaging:
  - Create/list/delete packaging channels with HLS ingest endpoints
  - Origin endpoint management with 4 packaging formats: HLS, DASH, MSS, CMAF
  - Start-over window and time delay configuration
- **API Endpoints**: `/api/aws-livestream/status`, `/api/aws-livestream/ivs/channels`, `/api/aws-livestream/ivs/streams`, `/api/aws-livestream/mediapackage/channels`, `/api/aws-livestream/mediapackage/endpoints`, `/api/aws-livestream/mediapackage/formats`
- **Frontend**: `/aws-livestream` page with IVS + MediaPackage tabs, channel/endpoint management, stream status modal
- **Navigation**: Added to Tools dropdown as "Live Streaming"
- **Testing**: 100% pass rate (all backend and frontend tests passed)

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

### Phase 20 - AWS Communications Integration (2026-03-14, updated 2026-03-15)
- **AWS WorkMail** - Business email management:
  - List/describe WorkMail organizations
  - List/create/delete users within organizations
  - Register/deregister users to WorkMail email
  - List groups and distribution lists
- **Amazon Connect** - Cloud contact center (migrated from AWS Pinpoint 2026-03-15):
  - List/describe Connect instances
  - Queue management per instance
  - Contact flow listing per instance
  - Hours of operation management
  - Connect user listing per instance
  - Routing profile management
- **API Endpoints**: `/api/aws-comms/status`, `/api/aws-comms/workmail/organizations`, `/api/aws-comms/workmail/users`, `/api/aws-comms/workmail/groups`, `/api/aws-comms/connect/instances`, `/api/aws-comms/connect/queues`, `/api/aws-comms/connect/contact-flows`, `/api/aws-comms/connect/hours-of-operation`, `/api/aws-comms/connect/users`, `/api/aws-comms/connect/routing-profiles`
- **Frontend**: `/aws-comms` page with WorkMail + Amazon Connect tabs, instance/queue/flow/hours/user/routing-profile views
- **Navigation**: Added to Tools dropdown as "Communications"
- **Testing**: Backend 100% (18/18 tests passed), Frontend 100% passed

### Phase 21 - AWS Security Integration (2026-03-14)
- **AWS WAF v2** - Web Application Firewall management:
  - List/create/delete Web ACLs (REGIONAL and CLOUDFRONT scope)
  - Web ACL detail view with rules, capacity, and visibility config
  - List/create/delete IP Sets for blocklists/allowlists (IPv4/IPv6)
  - IP Set detail view with address listing
  - List custom rule groups
  - List 15+ AWS Managed Rule Groups (CommonRuleSet, SQLi, XSS, etc.)
  - List resources associated with Web ACLs
- **AWS Secrets Manager** - Secure credential storage:
  - List all secrets with metadata (created, changed, accessed dates, rotation status, tags)
  - Describe secret metadata and version history
  - Get secret value info (key count, type) without exposing plaintext
  - Create/update/delete secrets with 7-day recovery window
  - Force delete option (bypasses recovery)
  - Secret rotation trigger with Lambda ARN and rotation schedule
  - Secret tagging support
  - Note: Secret names with slashes (e.g., bigmann/development/web3) handled via :path route params
- **API Endpoints**: `/api/aws-security/status`, `/api/aws-security/waf/web-acls`, `/api/aws-security/waf/ip-sets`, `/api/aws-security/waf/rule-groups`, `/api/aws-security/waf/managed-rules`, `/api/aws-security/secrets`, `/api/aws-security/secrets/{name:path}`, `/api/aws-security/secrets/{name:path}/info`, `/api/aws-security/secrets/{name:path}/rotate`
- **Frontend**: `/aws-security` page with WAF Firewall + Secrets Manager tabs, create/delete/detail views for all resources
- **Navigation**: Added to Tools dropdown as "Security (WAF)"
- **Testing**: Backend 100% (16/16 tests passed), Frontend 100% passed

### Phase 22 - AWS AI Analytics Integration (2026-03-15)
- **AWS Comprehend** - Natural Language Processing for content analysis:
  - Sentiment analysis (POSITIVE/NEGATIVE/NEUTRAL/MIXED with confidence scores)
  - Named entity recognition (PERSON, ORGANIZATION, LOCATION, DATE, etc.)
  - Key phrase extraction from content descriptions and comments
  - PII detection (email, phone, address, SSN patterns)
  - Dominant language detection
  - Syntax/part-of-speech analysis
  - Batch sentiment for up to 25 texts
  - Analysis history stored in MongoDB
- **AWS Personalize** - ML-powered content recommendations:
  - Dataset group management for training recommendation models
  - Campaign deployment for real-time recommendations
  - Solution training with 22 built-in AWS recipes
  - Event tracker management for user interaction data
- **API Endpoints**: `/api/aws-ai/status`, `/api/aws-ai/comprehend/sentiment`, `/api/aws-ai/comprehend/entities`, `/api/aws-ai/comprehend/key-phrases`, `/api/aws-ai/comprehend/pii`, `/api/aws-ai/comprehend/language`, `/api/aws-ai/comprehend/syntax`, `/api/aws-ai/comprehend/batch-sentiment`, `/api/aws-ai/comprehend/endpoints`, `/api/aws-ai/comprehend/history`, `/api/aws-ai/personalize/dataset-groups`, `/api/aws-ai/personalize/campaigns`, `/api/aws-ai/personalize/solutions`, `/api/aws-ai/personalize/recipes`, `/api/aws-ai/personalize/datasets`, `/api/aws-ai/personalize/event-trackers`, `/api/aws-ai/personalize/recommendations`
- **Frontend**: `/aws-ai-analytics` page with Comprehend + Personalize tabs
- **Navigation**: Added to Tools dropdown as "AI Analytics"
- **Testing**: 100% pass rate (31/31 backend, all frontend tests passed)

### Phase 22.1 - AWS Data Analytics Integration (2026-03-15)
- **Amazon QuickSight** - Business Intelligence dashboards:
  - List/describe dashboards with sheet details
  - Dataset and data source management
  - Analysis listing and status tracking
  - Note: Requires QuickSight subscription activation in AWS Console
- **AWS Athena** - Interactive S3 log analytics:
  - SQL Query Editor with database selection and query execution
  - Query status polling with auto-refresh on completion
  - Query result display with column headers and rows
  - Work group management
  - Database and table metadata exploration
  - Saved named queries
  - Recent execution history with scan size tracking
- **API Endpoints**: `/api/aws-data/status`, `/api/aws-data/quicksight/dashboards`, `/api/aws-data/quicksight/datasets`, `/api/aws-data/quicksight/data-sources`, `/api/aws-data/quicksight/analyses`, `/api/aws-data/athena/work-groups`, `/api/aws-data/athena/databases`, `/api/aws-data/athena/tables`, `/api/aws-data/athena/saved-queries`, `/api/aws-data/athena/query`, `/api/aws-data/athena/query/{id}/status`, `/api/aws-data/athena/query/{id}/results`, `/api/aws-data/athena/executions`
- **Frontend**: `/aws-data-analytics` page with QuickSight + Athena tabs
- **Navigation**: Added to Tools dropdown as "Data Analytics"

### Phase 22.2 - Amazon Managed Blockchain Integration (2026-03-15)
- **Amazon Managed Blockchain** - Hyperledger Fabric & Ethereum network management:
  - List/describe blockchain networks with framework details
  - Network member management
  - Node listing and detail view per member
  - Governance proposal tracking
  - Token-based accessor management
  - Master-detail UI with network selection
- **API Endpoints**: `/api/aws-blockchain/status`, `/api/aws-blockchain/networks`, `/api/aws-blockchain/networks/{id}`, `/api/aws-blockchain/networks/{id}/members`, `/api/aws-blockchain/networks/{id}/members/{mid}/nodes`, `/api/aws-blockchain/networks/{id}/proposals`, `/api/aws-blockchain/accessors`
- **Frontend**: `/aws-blockchain` page with networks list and detail panel
- **Navigation**: Added to Tools dropdown as "Managed Blockchain"

### Phase 23 - AWS Phase F: AI Content, Messaging & Infrastructure (2026-03-15)
- **Amazon Translate** - Multi-language content translation:
  - Real-time text translation between 75+ languages
  - Auto-detect source language
  - Custom terminology and parallel data management
- **Amazon Polly** - Text-to-speech for audio content:
  - 100+ voices across 30+ languages
  - Neural and standard engine support
  - Lexicon management, speech synthesis tasks
- **Amazon Textract** - Extract text from images/documents:
  - OCR text detection from S3-hosted documents
  - Table and form extraction
  - Async document analysis with job tracking
  - Custom adapter support
- **Amazon SageMaker** - ML model management:
  - Notebook instance listing and monitoring
  - Training job tracking and management
  - Model deployment and endpoint monitoring
  - Processing jobs and feature group management
- **Amazon Kinesis** - Real-time data streaming:
  - Data stream listing with shard and encryption details
  - Firehose delivery stream management
  - Stream metrics and consumer monitoring
- **Amazon SNS** - Simple Notification Service:
  - Topic listing with subscription counts
  - Subscription management by topic
  - Platform application listing
  - Message publishing to topics
- **Amazon SQS** - Simple Queue Service:
  - Queue listing with message depth metrics
  - FIFO and standard queue support
  - Queue attribute inspection
  - Send message and purge operations
- **Amazon EventBridge** - Event-driven automation:
  - Event bus management (default + custom)
  - Rule listing with state and schedule
  - Target inspection per rule
  - Archive and API destination management
  - Connection management
- **AWS Step Functions** - Workflow orchestration:
  - State machine listing (STANDARD/EXPRESS)
  - Execution tracking with status filtering
  - Execution detail view with I/O
  - Activity management
- **Amazon ElastiCache** - Redis/Memcached caching:
  - Cache cluster listing with node info
  - Replication group management (Multi-AZ, auto failover)
  - Snapshot management
  - Reserved node and subnet group listing
- **Amazon Neptune** - Graph database:
  - Graph DB cluster listing with endpoint info
  - Instance management per cluster
  - Cluster snapshot management
  - Parameter group and subnet group listing
- **API Endpoints**: 
  - `/api/aws-ai-content/status`, `/api/aws-ai-content/translate/text`, `/api/aws-ai-content/translate/languages`, `/api/aws-ai-content/translate/terminologies`, `/api/aws-ai-content/translate/parallel-data`
  - `/api/aws-ai-content/polly/voices`, `/api/aws-ai-content/polly/synthesize`, `/api/aws-ai-content/polly/lexicons`, `/api/aws-ai-content/polly/tasks`
  - `/api/aws-ai-content/textract/analyze`, `/api/aws-ai-content/textract/detect-text`, `/api/aws-ai-content/textract/start-analysis`, `/api/aws-ai-content/textract/analysis/{job_id}`, `/api/aws-ai-content/textract/adapters`
  - `/api/aws-ai-content/sagemaker/notebooks`, `/api/aws-ai-content/sagemaker/training-jobs`, `/api/aws-ai-content/sagemaker/models`, `/api/aws-ai-content/sagemaker/endpoints`, `/api/aws-ai-content/sagemaker/processing-jobs`, `/api/aws-ai-content/sagemaker/feature-groups`
  - `/api/aws-messaging/status`, `/api/aws-messaging/kinesis/streams`, `/api/aws-messaging/kinesis/firehose`, `/api/aws-messaging/kinesis/streams/{name}`, `/api/aws-messaging/kinesis/streams/{name}/metrics`
  - `/api/aws-messaging/sns/topics`, `/api/aws-messaging/sns/subscriptions`, `/api/aws-messaging/sns/platform-applications`, `/api/aws-messaging/sns/publish`
  - `/api/aws-messaging/sqs/queues`, `/api/aws-messaging/sqs/queue-details`, `/api/aws-messaging/sqs/send`, `/api/aws-messaging/sqs/purge`
  - `/api/aws-messaging/eventbridge/buses`, `/api/aws-messaging/eventbridge/rules`, `/api/aws-messaging/eventbridge/rules/{name}/targets`, `/api/aws-messaging/eventbridge/archives`, `/api/aws-messaging/eventbridge/connections`, `/api/aws-messaging/eventbridge/api-destinations`
  - `/api/aws-infra/status`, `/api/aws-infra/stepfunctions/state-machines`, `/api/aws-infra/stepfunctions/state-machines/{arn}`, `/api/aws-infra/stepfunctions/executions`, `/api/aws-infra/stepfunctions/execution/{arn}`, `/api/aws-infra/stepfunctions/activities`
  - `/api/aws-infra/elasticache/clusters`, `/api/aws-infra/elasticache/replication-groups`, `/api/aws-infra/elasticache/snapshots`, `/api/aws-infra/elasticache/reserved-nodes`, `/api/aws-infra/elasticache/subnet-groups`
  - `/api/aws-infra/neptune/clusters`, `/api/aws-infra/neptune/instances`, `/api/aws-infra/neptune/snapshots`, `/api/aws-infra/neptune/parameter-groups`, `/api/aws-infra/neptune/subnet-groups`
- **Frontend**: 3 new pages - `/aws-ai-content`, `/aws-messaging`, `/aws-infrastructure`
- **Navigation**: Added to Tools dropdown as "AI Content (Translate/Polly)", "Messaging & Events", "Infrastructure"
- **Testing**: 100% pass rate (19/19 backend, all frontend tests passed)

## Backlog
- **P1**: Connect to Live APIs for real-time metrics from social media platforms
- **P2**: Replace mock data in analytics with real API-sourced data
- **P3**: Revenue auto-import from platform APIs when credentials are connected
- **P2**: API Key Guidance - help user find/provide Facebook & Google OAuth keys
- **P3**: Add Quick Actions Panel to GS1 Hub's Overview tab

### Phase 24 - Content Lightbox / Full-Size Preview (2026-03-15)
- **Lightbox Modal** - Full-screen overlay for viewing uploaded content at full size:
  - Click any content thumbnail or "View" button to open immersive lightbox
  - Full-size image viewing with zoom in/out controls (0.5x to 4x) and zoom reset
  - Full audio player with large visual indicator in styled container
  - Full video player with autoplay
  - Title, content type, file size, and visibility badge in top bar
  - Tags and stats (views, downloads, likes) in bottom bar
  - Item counter showing current position (e.g., "3 / 8")
  - Previous/Next navigation buttons with wrap-around
  - Keyboard support: Escape to close, ArrowLeft/ArrowRight for navigation
  - Backdrop click to close
  - Download button for direct file download
  - Body scroll lock when lightbox is open
  - Hover expand icon overlay on image/video thumbnails
- **Frontend**: Updated `/content-management` page (`ContentManagementPage.jsx`)
- **Testing**: 100% pass rate (17/17 frontend features verified)



### Phase 25 - Real-Time WebSocket Delivery Status (2026-03-15)
- **WebSocket Delivery Manager** (`/app/backend/utils/delivery_ws_manager.py`) - Per-user connection tracking with broadcast capabilities
- **WebSocket Endpoint** - `/api/ws/delivery?user_id=<id>` for real-time delivery status updates
  - Accepts user_id query param, rejects without (code 4001)
  - Ping/pong keepalive support
- **Delivery Engine Integration** - broadcasts `delivery_update` events on every status change (preparing, delivering, delivered, failed, export_ready) and `batch_progress` summaries after each delivery completes
- **Frontend WebSocket Client** - DeliveryTracking component connects via WebSocket when an active batch exists
  - Auto-reconnect with 3s backoff on disconnect
  - Ping keepalive every 25s
  - "Live" / "Reconnecting..." connection indicator with Wifi icon
  - Falls back to initial HTTP fetch for current progress
  - Replaces previous `setTimeout(poll, 3000)` polling approach
- **Testing**: 100% pass rate (9/9 backend, all frontend tests passed)

### Phase 26 - DNS Configuration Guide Update (2026-03-15)
- **Expanded DNS records** from 7 to 16 record types in the DNS Configuration Guide
- New records added: AAAA (IPv6), DKIM (3 CNAME keys), SES verification TXT, CAA (SSL authority), Mail CNAME, Google Search Console TXT, SRV (VoIP)
- Backend `_get_required_dns_records()` in `/app/backend/routes/domain_routes.py` updated
- Frontend auto-renders new records via existing dynamic table in `DomainConfigPage.jsx`

### Phase 27 - Post-Scheduling Feature (2026-03-16)
- **Scheduled Posts CRUD API** - Full lifecycle management for scheduled social media posts:
  - `POST /api/integrations/scheduled-posts` - Create with future ISO 8601 time, validates past times
  - `GET /api/integrations/scheduled-posts` - List with optional status filter (pending/publishing/published/failed)
  - `PUT /api/integrations/scheduled-posts/{id}` - Update text, platforms, time (pending only)
  - `DELETE /api/integrations/scheduled-posts/{id}` - Delete pending or failed posts
- **Background Scheduler Service** (`/app/backend/services/scheduler_service.py`):
  - Runs every 30 seconds checking for due posts
  - Publishes via existing multi-platform engine (Twitter/X, TikTok, Snapchat)
  - Status pipeline: pending -> publishing -> published/failed
  - Saves results to `publish_history` collection for unified feed
  - Registered in `startup.py` as async background task
- **Frontend Scheduling UI** in `LiveIntegrationsPage.jsx`:
  - "Schedule for later" toggle in Publish Composer
  - Shadcn Calendar date picker with Popover + hour/minute UTC selectors
  - "Schedule Post" button (amber theme) replaces "Publish Now" when scheduling
  - New "Scheduled" tab showing all scheduled posts with status badges
  - Inline edit for pending posts (text + datetime-local input)
  - Delete button for pending/failed posts
  - Refresh button, empty state guidance
- **DB Collection**: `scheduled_posts` (id, user_id, text, platforms, media_url, scheduled_time, status, results, created_at, updated_at)
- **Testing**: 100% pass rate (12/12 backend, all frontend tests passed - iteration_88)

### Phase 26 - CVE Vulnerability Remediation Round 2 (2026-02)
- **Frontend: 9 HIGH vulnerabilities resolved** via yarn resolutions:
  - `fast-xml-parser` 5.5.5 → >=5.5.6 (CVE-2026-33036 — numeric entity expansion bypass, DoS HIGH)
- **Backend: 7 vulnerabilities in 5 packages resolved** via pip upgrade:
  - `authlib` 1.6.7 → 1.6.9 (GHSA-wvwj-cvrp-7pv5, GHSA-7432-952r-cw78)
  - `black` 25.1.0 → 26.3.1 (GHSA-3936-cmfr-pm3m)
  - `pyasn1` 0.6.2 → 0.6.3 (GHSA-jr27-m4p2-rc6r)
  - `pyjwt` 2.10.1 → 2.12.1 (GHSA-752w-5fwx-jx9f)
  - `pyopenssl` 25.3.0 → 26.0.0 (GHSA-vp96-hxj8-p424, GHSA-5pwr-322w-8jr4)
- **Final audit: 0 vulnerabilities** on both frontend and backend

### Phase 27 - Unified GS1 & Licensing Hub (2026-03-18)
- **Consolidated 3 separate pages** (`/gs1`, `/licensing`, `/comprehensive-licensing`) into a single unified page at `/gs1-licensing`
- **6 Tabs**: Overview, GS1 & Business, Products & Barcodes, Platform Licensing, Compensation, Agreements & Compliance
- **Overview**: Combined dashboard with stat cards (Platforms Licensed, Active Licenses, Compliance Rate, GS1 Assets), Business Entity summary, Financial Summary, Platform Categories
- **GS1 & Business**: GS1 registry info, business entity details, capabilities (GTIN/GLN/ISRC/ISAN), legal & contact details
- **Products & Barcodes**: UPC/GTIN product CRUD + barcode generator with download
- **Platform Licensing**: License management with activate/deactivate, status filter, "License All Platforms" bulk action
- **Compensation**: Sub-tabs for Statutory Rates, Daily Compensation, Compensation Analytics
- **Agreements & Compliance**: Sub-tabs for License Agreements, Automated Workflows, Compliance Docs + Generate All Licenses
- **Bug Fix**: Fixed GS1 API endpoint routing (double `/api` prefix issue in `gs1_endpoints.py`)
- **Navigation**: Single "GS1 & Licensing" link in Business dropdown; legacy routes redirect to hub
- **Files**: Created `/app/frontend/src/pages/GS1LicensingHub.jsx`, updated `App.js`, `NavigationBar.jsx`, `gs1_endpoints.py`
- **Testing**: 95% pass (iteration_89) + API fix verified


### Phase 28 - Dead Code Cleanup (2026-03-18)
- **Removed 3 unused component files**: `GS1Components.js`, `LicensingComponents.js`, `ComprehensiveLicensingComponents.js`
- **Removed 5 dead lazy imports** from `App.js`: `GS1Dashboard`, `LicensingDashboard`, `PlatformLicenseManager`, `LicensingStatus`, `ComprehensiveLicensingComponents`
- **Kept** `GS1AssetRegistryComponents.js` (still used by `ComprehensivePlatformComponents.js`)
- **Verified**: App loads, GS1 & Licensing Hub renders correctly, zero lint errors

### Phase 29 - Comprehensive Dead Code Cleanup (2026-03-18)
- **28 dead files removed (~11,000 lines)** across frontend and backend
- **Frontend (7 files)**:
  - `EnhancedApp.js` (365 lines) — never imported
  - `EnhancedUploadComponent_old.js` (834 lines) — old copy, superseded by `EnhancedUploadComponent.js`
  - `DOOHRouter.jsx` (234 lines) — never imported
  - `SocialMediaDashboard.js` (353 lines) — replaced by `SocialMediaDashboardEnhanced.js`
  - `utils/accessibility.js` (279 lines) — never imported
  - `utils/formValidation.js` (322 lines) — never imported
  - `utils/logger.js` (39 lines) — never imported
- **Backend Services (7 files)**:
  - `compliance_dispute_service.py`, `delivery_optimization_service.py`, `distribution_svc.py`, `format_optimization_service.py`, `gs1_profile_service.py`, `pinpoint_service.py` (migrated to Connect), `post_scheduler_service.py` (superseded by `scheduler_service.py`)
- **Backend Utils (11 files)**:
  - `blockchain_contracts.py`, `dao_removal_integration.py`, `ddex_integration.py`, `encryption_utils.py`, `enhanced_distribution_platforms.py`, `enhanced_validation.py`, `ethereum_integration.py`, `label_simple.py`, `migrate_labels_to_uln.py`, `postgres_ledger.py`, `qldb_mock.py`
- **Backend API Endpoints (3 files)**:
  - `agency_onboarding_endpoints.py`, `image_upload_endpoints.py`, `ipi_endpoints.py` — never imported in router_setup.py or server.py
- **Also cleaned**: All `__pycache__` directories
- **Verified**: Backend healthy, frontend compiles successfully, login + navigation working

### Phase 30 - Legacy Test Scripts Audit & Cleanup (2026-03-18)
- **183 legacy test files removed (~102,576 lines, 4.9 MB)** from `/app/tests/legacy/`
  - 179 Python test scripts, 2 log files, 2 JSON result files
  - All HTTP-based tests (using `requests` library), none directly imported backend modules
  - 105 files hardcoded to stale preview URLs (e.g. `social-profile-sync.preview.emergentagent.com`)
  - ~40 files referenced deleted modules (QLDB, blockchain/ethereum/DAO, DDEX, agency_onboarding, DOOH/pDOOH)
  - Zero references from any active code, CI/CD config, or other scripts
  - The app maintains 76 active test files in `/app/backend/tests/` covering all modern features
- **Also cleaned**: Empty `/app/tests/` directory and its `__init__.py`
- **Verified**: Backend healthy (all services operational), frontend renders correctly, login working
