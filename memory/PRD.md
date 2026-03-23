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

### Phase 11 - Advanced Analytics (2026-03-11)
- **Automated Anomaly Detection** - Z-score statistical analysis on platform metrics
- **Audience Demographics** - Age distribution, gender split, interest categories, device breakdown
- **Geographic Distribution** - Country-level audience breakdown with listener counts
- **Best Time to Post** - 7x24 engagement heatmap, recommended posting windows
- **Revenue Tracking** - Per-platform revenue across 10 platforms, revenue by source, 12-month trend

### Phase 12-30 - Various (Infrastructure, Security, AWS, Cleanup)
See CHANGELOG.md for full details of Phases 12-30.

### Phase 31 - ULN Enhanced Features (2026-03-23)
Five major ULN enhancements implemented and tested (23/23 backend tests passed, 100% frontend):
1. **Real Blockchain Integration** - SHA-256 hash chain, proof-of-work mining, Merkle tree verification
2. **Live Royalty Data** - 955 real royalty earnings across 20 labels, 12 months
3. **ULN Analytics Dashboard** - Cross-label ranking, revenue trends, genre/territory breakdown
4. **Label Onboarding Workflow** - 5-step guided wizard with session persistence
5. **Inter-Label Messaging** - Thread-based conversations with read receipts

### Phase 32 - Enhanced Facebook & Instagram URL Scrapers (2026-03-23)
- **Facebook Scraper Enhancement** - 3-strategy scraping (HTML meta tags + JSON patterns, mobile page fallback, Graph API public endpoint). Extracts: followers, page likes, posts, page name, category, about. Size-based engagement estimation.
- **Instagram Scraper Enhancement** - 3-strategy scraping (web_profile_info API with recent post engagement calc, HTML page scrape with embedded JSON, oEmbed fallback). Extracts: followers, following, posts, bio, full name, verified status.
- **Manual Metrics Fallback** - When auto-scraping fails (Meta blocks cloud IPs), users can enter followers/following/posts/engagement manually. Stored on credential doc and used as dashboard metrics base.
- **Enriched URL Connection Response** - Returns full_name, bio, page_name, category, is_verified, following, page_likes, impressions, reach alongside standard metrics.
- **Frontend Manual Metrics Form** - Toggle-based form with followers/following/posts/engagement fields. Shows "no metrics" prompt with "Add metrics manually" button when auto-scrape fails.
- **Analytics Platform Row** - Now shows posts count alongside followers and engagement.
- **Testing**: 100% pass rate (15/15 backend, all frontend tests passed - iteration_91)

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local disk `/app/uploads/content/`, `/app/uploads/hub/`
- **CDN**: AWS CloudFront via `cdn.bigmannentertainment.com`
- **Key Routes**: `/app/backend/routes/` (24 core routers) + `/app/backend/api/` (78 endpoint routers)
- **WebSockets**: `/api/ws/sla`, `/api/ws/notifications`, `/api/ws/delivery`

## Key API Endpoints
- Content: `GET/POST /api/user-content/`, `GET /api/user-content/file/{file_id}`
- Social Platforms: `GET /api/social/platforms`, `GET /api/social/connections`
- Social URL Connect: `POST /api/social/connect-url`, `POST /api/social/url-detect`, `GET /api/social/url-supported`
- Social Metrics: `GET /api/social/metrics/dashboard`, `GET /api/social/metrics/platforms`, `POST /api/social/metrics/refresh`
- Distribution Hub: `GET/POST /api/distribution-hub/content`, `POST /api/distribution-hub/distribute`
- Live Integrations: `GET /api/integrations/status/all`, `POST /api/integrations/publish`
- Analytics: `GET /api/analytics/overview`, `GET /api/analytics/revenue/overview`

## DB Collections
- `platform_credentials` (includes manual_metrics field for fallback data)
- `platform_metrics`, `notifications`, `content_comments`, `user_content`, `messages`, `conversations`
- `distribution_hub_content`, `distribution_hub_deliveries`, `publish_history`, `scheduled_posts`
- `uln_blockchain_blocks`, `uln_blockchain_transactions`, `uln_smart_contracts_live`, `royalty_earnings`
- `uln_onboarding`, `uln_message_threads`, `uln_messages`

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Backlog
- **P1**: Connect to Live APIs for real-time metrics from social media platforms (blocked by Meta API keys)
- **P2**: Replace mock data in analytics with real API-sourced data
- **P2**: API Key Guidance - help user find/provide Facebook & Google OAuth keys
- **P3**: Revenue auto-import from platform APIs when credentials are connected
- **P3**: Quick Actions Panel for GS1 Hub Overview tab
- **P4**: DNS Health Checker
- **P5**: Automated CVE monitoring dashboard
- **P5**: ULN Notification System
