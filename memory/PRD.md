# Big Mann Entertainment - Product Requirements Document

## Original Problem Statement
Build a comprehensive creator tools platform for Big Mann Entertainment that enables content management, distribution, analytics, messaging, and monetization for music/media creators.

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

### Phase 3 (2026-03-09)
- **File Preview in Content Management** - Image thumbnails, audio player with controls, video player for uploaded content
- **Real-time Notifications** - Bell icon with unread badge, dropdown panel, full notifications page, WebSocket push
- **New Comment Notifications** - Comment system on content items with real-time notification to content owners

### Phase 4 - Refactoring (2026-03-09)
- **server.py Refactoring** - Extracted middleware, startup logic, WebSocket/webhook routes into dedicated modules

### Phase 5 - Social Media Platform Connections (2026-03-09)
- **120 Platform Connections Dashboard** - Credential management for all 120 distribution platforms
- **Credential Management UI** - Modal-based credential entry with dynamic fields per platform
- **Bulk Connect** - One-click "Connect All" for all 120 platforms
- **Dashboard Metrics** - Overview tab with connected platform counts
- **Social Posts** - Create and list posts to connected platforms

### Phase 6 - Real-Time Platform Analytics (2026-03-09)
- **Analytics Tab** - Aggregate metrics, category breakdown, platform performance table with sparkline trends
- **Refresh Metrics** - One-click refresh for all platform metrics

### Phase 7 - Live Social Media API Integrations (2026-03-09)
- **14 Live API Adapters** - Twitter/X, YouTube, Instagram, Facebook, Spotify, TikTok, LinkedIn, Twitch, SoundCloud, Reddit, YouTube Music, Threads, Spotify Podcasts, WhatsApp Business
- **Graceful Fallback** - Falls back to simulated metrics when API calls fail
- **Metric Caching** - 5-minute TTL in MongoDB
- **Data Source Indicators** - LIVE/SIM badges on every metric, live/simulated count summaries

### Phase 8 - URL-Based Platform Connections (2026-03-09)
- **URL Connect System** - Users paste profile URLs instead of API keys to connect platforms
- **Auto-Detection** - Platform and username auto-detected from URL patterns (25 platform URL formats)
- **25 URL Metric Adapters** - YouTube, Twitter, Reddit, TikTok, Instagram, Twitch, SoundCloud, Spotify, Facebook, LinkedIn, Pinterest, Threads, Vimeo, Tumblr, Snapchat, Discord, Telegram, Dailymotion, Bandcamp, Audiomack, Mixcloud, GitHub, Medium, Kick, Bluesky
- **Real Public Data** - Bluesky (596K), Discord (418K members), Telegram (10.4M subscribers), GitHub (289K), Dailymotion confirmed live
- **Dual-Mode Modal** - Frontend credential modal has "Profile URL" / "API Keys" toggle tabs
- **Platform Badges** - API (cyan), URL (purple), via URL (green) badges on platform cards
- **Bulk URL Connect** - Connect multiple platforms by pasting multiple profile URLs
- **123 Total Platforms** - Added GitHub, Medium, Bluesky to platform config
- **Endpoints**:
  - `GET /api/social/url-supported` - 25 platforms with URL adapters
  - `POST /api/social/url-detect` - Auto-detect platform from URL
  - `POST /api/social/connect-url` - Connect platform via profile URL
  - `POST /api/social/connect-url/bulk` - Bulk URL connection

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local disk `/app/uploads/content/`
- **Key Routes**: `/app/backend/routes/` (22 modular routers)
- **Real-time**: WebSocket at `/api/ws/notifications` and `/api/ws/sla`

## Key API Endpoints
- Content: `GET/POST /api/user-content/`, `GET /api/user-content/file/{file_id}`
- Comments: `POST/GET /api/user-content/{id}/comments`, `DELETE /api/user-content/comments/{id}`
- Notifications: `GET /api/notifications`, `GET /api/notifications/unread-count`, `PUT /api/notifications/{id}/read`
- Messages: `GET /api/messages/conversations`, `POST /api/messages/send`
- Analytics: `GET /api/analytics/overview`
- Social Platforms: `GET /api/social/platforms`, `GET /api/social/connections`
- Social Credentials: `POST/GET/DELETE /api/social/credentials/{platform_id}`
- URL Connect: `POST /api/social/connect-url`, `POST /api/social/connect-url/bulk`, `POST /api/social/url-detect`, `GET /api/social/url-supported`
- Live Metrics: `GET /api/social/live-supported`, `GET /api/social/metrics/dashboard`, `GET /api/social/metrics/platforms`, `POST /api/social/metrics/refresh`
- Bulk: `POST /api/social/bulk-connect`
- Posts: `POST /api/social/post`, `GET /api/social/posts`

## DB Collections
- `notifications`, `content_comments`, `user_content`, `messages`, `conversations`, `subscriptions`
- `platform_credentials`: `{ user_id, platform_id, credentials (incl. profile_url), display_name, status, connection_method, connected_at }`
- `social_posts`: `{ id, user_id, platforms, content, media_urls, status, posted_at, created_at }`
- `platform_live_metrics`: `{ user_id, platform_id, metrics, refreshed_at }` (5-min TTL cache)
- `platform_metrics`: `{ user_id, platform_id, metrics, data_source, refreshed_at }`

## 3rd Party Integrations
- Stripe, PayPal (payments)
- AWS Services (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, etc.)
- Google Generative AI
- Social Media Live APIs (Twitter v2, YouTube Data v3, Instagram Graph, Facebook Graph, Spotify Web, TikTok, LinkedIn, Twitch Helix, SoundCloud, Reddit)
- URL-based public scraping (25 platforms: YouTube, Twitter, Reddit, TikTok, Instagram, Twitch, SoundCloud, Spotify, Facebook, LinkedIn, Pinterest, Threads, Vimeo, Tumblr, Snapchat, Discord, Telegram, Dailymotion, Bandcamp, Audiomack, Mixcloud, GitHub, Medium, Kick, Bluesky)

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Backlog
- **P1**: Post-scheduling functionality to connected social media accounts
- **P2**: Enhanced content preview (lightbox/modal for full-size viewing)
- **P2**: More notification event types (content likes, new content uploads, system alerts)
- **P2**: User Verification pending for "New Comment" notification feature
- **P2**: Automated anomaly detection for social media metrics
- **P3**: Audience demographics and best-time-to-post insights
