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
- **Real-time Notifications** - Bell icon with unread badge in navbar, dropdown panel, full `/notifications` page with pagination/filters, WebSocket for real-time push. Auto-triggers on new messages and subscription confirmations.

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local disk `/app/uploads/content/`
- **Key Routes**: `/app/backend/routes/` (modular routers)
- **Key Pages**: `/app/frontend/src/pages/`
- **Real-time**: WebSocket at `/api/ws/notifications`

## Key API Endpoints
- `GET /api/user-content/` - List user content
- `POST /api/user-content/upload` - Upload content
- `GET /api/user-content/file/{file_id}` - Serve file for preview (public, no auth)
- `GET /api/notifications` - List notifications (supports `unread_only`, pagination)
- `GET /api/notifications/unread-count` - Get unread notification count
- `PUT /api/notifications/{id}/read` - Mark notification as read
- `PUT /api/notifications/read-all` - Mark all notifications as read
- `DELETE /api/notifications/{id}` - Delete a notification
- `GET /api/messages/conversations` - List conversations
- `POST /api/messages/send` - Send message (also triggers notification)
- `GET /api/analytics/stats` - Dashboard stats

## DB Collections
- `notifications`: `{ user_id, type, title, message, link, sender_id, sender_name, read, created_at }`
- `user_content`: `{ user_id, file_id, title, description, content_type, file_size, tags, visibility, stats, ... }`
- `messages`, `conversations`: messaging data
- `subscriptions`: subscription data

## 3rd Party Integrations
- Stripe (payments)
- PayPal (payments)
- AWS Services (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, CloudWatch, etc.)
- Google Generative AI

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Backlog
- **P1**: Refactor remaining `server.py` logic into dedicated route files
- **P2**: Enhanced content preview (lightbox/modal for full-size viewing)
- **P2**: More notification event types (content likes, new content uploads, system alerts)
