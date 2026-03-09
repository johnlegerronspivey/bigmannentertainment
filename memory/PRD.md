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
- **File Preview in Content Management** - Image thumbnails, audio player with controls, video player for uploaded content. Backend file-serving endpoint at `/api/user-content/file/{file_id}`.
- **Real-time Notifications** - Bell icon with unread badge in navbar, dropdown panel, full `/notifications` page with pagination/filters, WebSocket for real-time push. Auto-triggers on new messages, subscription confirmations, and new comments.
- **New Comment Notifications** - Full comment system on content items. Users can add, view, and delete comments. Content owners receive `new_comment` notifications when other users comment (self-comments excluded). Frontend shows expandable comment section on each content card.

### Phase 4 - Refactoring (2026-03-09)
- **server.py Refactoring** - Extracted middleware, startup logic, WebSocket routes, and webhook routes into dedicated modules. server.py reduced from 429 to 156 lines (64% reduction).
  - `middleware.py` — Performance tracking, security headers, rate limiting
  - `startup.py` — Database indexes, service initialization, shutdown handler
  - `routes/websocket_routes.py` — SLA and notification WebSocket endpoints
  - `routes/webhook_routes.py` — Stripe webhook endpoint

### Phase 5 - Social Media Platform Connections (2026-03-09)
- **120 Platform Connections Dashboard** - Full credential management system for all 120 distribution platforms (social media, music streaming, podcasts, radio, TV/video streaming, live streaming, blockchain, Web3 music, NFT marketplaces, model agencies, rights organizations, music licensing)
  - Backend: `/app/backend/routes/social_connections_routes.py`
  - Frontend: `/app/frontend/src/SocialMediaDashboardEnhanced.js` at route `/social`
- **Credential Management UI** - Modal-based credential entry with dynamic fields per platform, masked credential display, connect/disconnect per platform
- **Bulk Connect** - One-click "Connect All" for all 120 platforms
- **Dashboard Metrics** - Overview tab with connected platform counts and summaries
- **Social Posts** - Create and list posts to connected platforms
- **Search & Filters** - Search by platform name, filter by category (16 categories) and connection status

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local disk `/app/uploads/content/`
- **Key Routes**: `/app/backend/routes/` (22 modular routers)
- **External Routes**: `/app/backend/router_setup.py` (50+ external endpoint modules)
- **Key Pages**: `/app/frontend/src/pages/`
- **Real-time**: WebSocket at `/api/ws/notifications` and `/api/ws/sla`

## Key API Endpoints
- `GET /api/user-content/` - List user content
- `POST /api/user-content/upload` - Upload content
- `GET /api/user-content/file/{file_id}` - Serve file for preview (public, no auth)
- `POST /api/user-content/{content_id}/comments` - Add comment (auth required)
- `GET /api/user-content/{content_id}/comments` - List comments (public)
- `DELETE /api/user-content/comments/{comment_id}` - Delete comment (auth required)
- `GET /api/notifications` - List notifications (supports `unread_only`, pagination)
- `GET /api/notifications/unread-count` - Get unread notification count
- `PUT /api/notifications/{id}/read` - Mark notification as read
- `PUT /api/notifications/read-all` - Mark all notifications as read
- `DELETE /api/notifications/{id}` - Delete a notification
- `GET /api/messages/conversations` - List conversations
- `POST /api/messages/send` - Send message (also triggers notification)
- `GET /api/analytics/overview` - Dashboard stats
- `POST /api/webhook/stripe` - Stripe webhook handler
- `GET /api/social/platforms` - List all 120 platforms (public)
- `GET /api/social/connections` - List all platforms with connection status (auth)
- `POST /api/social/credentials/{platform_id}` - Save credentials (auth)
- `GET /api/social/credentials/{platform_id}` - Get masked credentials (auth)
- `DELETE /api/social/credentials/{platform_id}` - Disconnect platform (auth)
- `POST /api/social/disconnect/{provider}` - Disconnect alias (auth)
- `GET /api/social/metrics/dashboard` - Dashboard metrics (auth)
- `POST /api/social/bulk-connect` - Bulk connect platforms (auth)
- `POST /api/social/post` - Create social post (auth)
- `GET /api/social/posts` - List user posts (auth)

## DB Collections
- `notifications`: `{ user_id, type, title, message, link, sender_id, sender_name, read, created_at }`
- `content_comments`: `{ content_id, user_id, user_name, text, created_at }`
- `user_content`: `{ user_id, file_id, title, description, content_type, file_size, tags, visibility, stats, ... }`
- `messages`, `conversations`: messaging data
- `subscriptions`: subscription data
- `platform_credentials`: `{ user_id, platform_id, credentials, display_name, status, connected_at, updated_at }`
- `social_posts`: `{ id, user_id, platforms, content, media_urls, status, posted_at, created_at }`

## Notification Types
- `new_message` - When a user receives a direct message (blue icon)
- `new_subscriber` - When a subscription is activated (green icon)
- `new_comment` - When another user comments on content (amber icon)

## 3rd Party Integrations
- Stripe (payments)
- PayPal (payments)
- AWS Services (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, CloudWatch, etc.)
- Google Generative AI

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Backlog
- **P2**: Enhanced content preview (lightbox/modal for full-size viewing)
- **P2**: More notification event types (content likes, new content uploads, system alerts)
