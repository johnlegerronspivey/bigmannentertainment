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

### Phase 10 - Content Distribution Hub (2026-03-11)
- **Distribution Hub** - Central command center for content distribution to all commercial platforms
- **120 Commercial Platforms** across 15 categories:
  - Audio Streaming (14), Commercial Radio (6), Video Platforms (8), Film & Movie (9), Social Media (9), Podcast (5)
  - Modeling Agencies (12): IMG, Elite, Ford, Wilhelmina, Next, Women, Society, Storm, Premier, Select, LA Models, DNA
  - Programmatic DOOH (10): Clear Channel, JCDecaux, Lamar, Outfront, Vistar, Broadsign, Place Exchange, Hivestack, AdQuick, Blip
  - Web3 & Blockchain (8): Ethereum, Polygon, Solana, Audius, Sound.xyz, Royal, OpenSea, Catalog
  - Rights & Licensing (7): ASCAP, BMI, SESAC, SoundExchange, Harry Fox, MLC, MDE
  - International Streaming (8): JOOX, Gaana, Yandex, QQ Music, NetEase, YouTube Music, Mixcloud, ReverbNation
  - Live Streaming (4): Kick, Clubhouse, Twitter Spaces, Spotify Live
  - Entertainment Media (8): WorldStarHipHop, Revolt TV, Shade Room, Hollywood Unlocked, DatPiff, Spinrilla, LiveMixtapes, MyMixtapez
  - Creator Platforms (4): OnlyFans, Fansly, Models.com, Medium
  - Alternative Social (8): Odysee, BitChute, Brighteon, GETTR, Gab, Parler, Truth Social, WhatsApp Business
- **12 System Templates**: All Radio, Major Streaming, Social Blast, Video Everywhere, Film Distribution, Podcast Push, All Modeling Agencies, DOOH Billboard Blast, Web3 Distribution, Entertainment Media, Global Streaming, Rights & Licensing
- **Content Management** - Upload, manage, and organize audio, video, image, and film content
- **Metadata Management** - Basic (title, artist, genre, tags) + Advanced (ISRC, UPC, copyright, publisher, record label, licensing type, territory rights)
- **Rights Management** - Copyright info, licensing terms, royalty splits, DRM settings, exclusive rights
- **Dual Delivery** - Auto-push via API for supported platforms, export packages with full metadata for others
- **Delivery Tracking** - Real-time status per delivery (queued, delivering, delivered, export_ready, failed)
- **Export Packages** - Platform-ready bundles with metadata, rights, delivery instructions, source-of-truth URL
- **Platform Connections** - Store API credentials per platform for auto-push delivery
- **Source of Truth** - App URL is the authoritative source for all distribution operations
- **Endpoints**:
  - `GET /api/distribution-hub/platforms` - 120 platforms in 15 categories
  - `POST /api/distribution-hub/content` - Create content with full metadata
  - `GET /api/distribution-hub/content` - Content library
  - `GET /api/distribution-hub/content/{id}` - Content detail
  - `PUT /api/distribution-hub/content/{id}/metadata` - Update metadata/rights
  - `DELETE /api/distribution-hub/content/{id}` - Delete content
  - `POST /api/distribution-hub/upload` - Upload file + create content
  - `POST /api/distribution-hub/distribute` - Distribute to platforms
  - `GET /api/distribution-hub/deliveries` - Delivery history
  - `GET /api/distribution-hub/deliveries/batch/{batch_id}` - Batch details
  - `PUT /api/distribution-hub/deliveries/{id}/status` - Update delivery status
  - `POST /api/distribution-hub/deliveries/{id}/export` - Generate export package
  - `POST /api/distribution-hub/platforms/connect` - Connect platform
  - `GET /api/distribution-hub/platforms/connected` - Connected platforms
  - `DELETE /api/distribution-hub/platforms/{id}/disconnect` - Disconnect platform
  - `GET /api/distribution-hub/stats` - Hub dashboard statistics

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local disk `/app/uploads/content/`, `/app/uploads/hub/`
- **Key Routes**: `/app/backend/routes/` (23 modular routers)
- **Real-time**: WebSocket at `/api/ws/notifications` and `/api/ws/sla`

## Key API Endpoints
- Content: `GET/POST /api/user-content/`, `GET /api/user-content/file/{file_id}`
- Comments: `POST/GET /api/user-content/{id}/comments`, `DELETE /api/user-content/comments/{id}`
- Notifications: `GET /api/notifications`, `GET /api/notifications/unread-count`, `PUT /api/notifications/{id}/read`
- Messages: `GET /api/messages/conversations`, `POST /api/messages/send`
- Analytics: `GET /api/analytics/overview`
- Social Platforms: `GET /api/social/platforms`, `GET /api/social/connections`
- Distribution Hub: `GET/POST /api/distribution-hub/content`, `POST /api/distribution-hub/distribute`, `GET /api/distribution-hub/deliveries`, `POST /api/distribution-hub/deliveries/{id}/export`
- URL Connect: `POST /api/social/connect-url`, `POST /api/social/connect-url/bulk`
- Live Metrics: `GET /api/social/metrics/dashboard`, `POST /api/social/metrics/refresh`

## DB Collections
- `notifications`, `content_comments`, `user_content`, `messages`, `conversations`, `subscriptions`
- `platform_credentials`: `{ user_id, platform_id, credentials, display_name, status, connection_method }`
- `distribution_hub_content`: `{ id, user_id, title, content_type, metadata (basic+advanced), rights, file_url, status }`
- `distribution_hub_deliveries`: `{ id, batch_id, user_id, content_id, platform_id, delivery_method, status, metadata, rights, source_url }`
- `distribution_hub_credentials`: `{ id, user_id, platform_id, credentials, connected }`

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
- **P0**: Implement actual API push logic for platforms with APIs (YouTube, SoundCloud, Vimeo, TikTok, etc.)
- **P1**: Post-scheduling functionality to connected social media accounts
- **P2**: Automated anomaly detection for social media metrics
- **P2**: Enhanced content preview (lightbox/modal for full-size viewing)
- **P2**: User Verification pending for "New Comment" notification feature
- **P3**: Audience demographics and best-time-to-post insights
- **P3**: Revenue tracking per platform from distribution
