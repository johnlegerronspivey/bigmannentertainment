# Big Mann Entertainment - Product Requirements Document

## Original Problem Statement
Big Mann Entertainment is a complete media distribution platform founded by John LeGerron Spivey. The application enables content creators to distribute their media (audio, video, images) across 120+ platforms worldwide, manage royalties, handle compliance, and leverage blockchain technologies.

## Architecture
- **Frontend**: React with lazy-loaded components, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python) with MongoDB
- **3rd Party**: Jira, Stripe, AWS (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, CloudWatch, Inspector, Detective, RDS, Route53), Google Generative AI

## Code Structure
```
/app
├── backend/
│   ├── server.py
│   ├── routes/
│   │   ├── creator_profile_routes.py  (MongoDB creator profiles)
│   │   ├── watermark_routes.py        (Content watermarking)
│   │   ├── subscription_routes.py     (Subscription tiers)
│   │   ├── content_routes.py          (NEW - User content uploads)
│   │   ├── messaging_routes.py        (NEW - Direct messaging)
│   │   ├── analytics_routes.py        (NEW - Creator analytics)
│   │   ├── auth_routes.py, admin_routes.py, media_routes.py, ...
│   ├── config/, models/, auth/, services/
│   └── router_setup.py
└── frontend/
    └── src/
        ├── App.js
        ├── pages/
        │   ├── CreatorProfilesPage.jsx
        │   ├── WatermarkPage.jsx
        │   ├── SubscriptionPage.jsx
        │   ├── ContentManagementPage.jsx   (NEW)
        │   ├── MessagingPage.jsx           (NEW)
        │   ├── CreatorAnalyticsPage.jsx    (NEW)
        │   ├── HomePage.jsx, LoginPage.jsx, ...
        ├── components/layout/NavigationBar.jsx
        ├── contexts/AuthContext.jsx
        └── utils/apiClient.js
```

## Completed Features
- Navigation Bar UI
- Domain Configuration Page
- CVE Management Dashboard
- SLA Tracker Dashboard
- Tenant Management (RBAC)
- Auth context extraction to AuthContext.jsx
- Navigation extraction to NavigationBar.jsx
- Page components extraction to /pages/ directory
- Amazon RDS PostgreSQL Minor Version Upgrade (Feb 2026)
- Added "Fansly" to platform list
- **P0 Account Lockout Fix (Feb 2026)**
- **Creator Profiles (Mar 2026)** - MongoDB-based profile system with create/edit/browse/search
- **Content Watermarking (Mar 2026)** - Customizable text watermarks with live preview, save/download
- **Subscription Tiers (Mar 2026)** - Free/Pro/Enterprise plans with Stripe checkout integration
- **PostgreSQL Cleanup (Mar 2026)** - Removed 7 obsolete PG-based files, fixed startup crashes
- **User Content Uploads & Management (Mar 2026)** - Upload audio/video/image, CRUD, search, filter by type
- **Direct Messaging (Mar 2026)** - Conversation-based messaging between users, read receipts, unread counts
- **Creator Analytics Dashboard (Mar 2026)** - Overview stats, content performance, audience insights, revenue

## New Feature Details (Mar 2026)

### User Content Uploads & Management
- **Backend**: `/api/user-content` (POST /upload, GET list, GET /{id}, PUT /{id}, DELETE /{id}), `/api/user-content/public/browse`
- **Frontend**: `/content-management` page with upload form, content grid, edit/delete, search/filter
- **Data**: MongoDB `user_content` collection
- **Fields**: user_id, file_id, title, description, content_type, tags, visibility, stats (views/downloads/likes), file_size
- **File Storage**: `/app/uploads/content/` — Max 100MB per file
- **Supported Types**: audio (.mp3,.wav,.flac,.aac,.ogg,.m4a), video (.mp4,.mov,.avi,.mkv,.webm), image (.jpg,.jpeg,.png,.gif,.webp,.bmp)

### Direct Messaging
- **Backend**: `/api/messages` (POST /send, GET /conversations, GET /conversation/{user_id}, PUT /read/{user_id}, DELETE /{id}, GET /unread-count)
- **Frontend**: `/messages` page with conversation list, chat interface, new conversation search
- **Data**: MongoDB `conversations` + `messages` collections
- **Features**: Real-time polling (5s), read receipts, unread badges, search creators to start chat

### Creator Analytics Dashboard
- **Backend**: `/api/analytics` (GET /overview, GET /content-performance, GET /audience, GET /revenue, POST /track)
- **Frontend**: `/creator-analytics` page with 4 tabs: Overview, Content, Audience, Revenue
- **Data**: Aggregates from `user_content`, `creator_profiles`, `conversations`, `analytics_events`

### Creator Profiles
- **Backend**: `/api/creator-profiles` (POST, GET /me, PUT /me, GET /browse, GET /u/{username})
- **Frontend**: `/creator-profiles` page with My Profile tab and Browse Creators tab
- **Data**: MongoDB `creator_profiles` collection

### Content Watermarking
- **Backend**: `/api/watermark` (GET/PUT /settings, POST /preview, POST /apply)
- **Frontend**: `/watermark` page with settings panel and image upload/preview
- **Data**: MongoDB `watermark_settings` collection

### Subscription Tiers
- **Backend**: `/api/subscriptions` (GET /tiers, GET /me, POST /checkout, POST /confirm, POST /cancel)
- **Frontend**: `/subscription` page with 3 tier cards and billing toggle
- **Data**: MongoDB `subscriptions` collection
- **Tiers**: Free ($0), Pro ($9.99/mo), Enterprise ($29.99/mo) with Stripe checkout

## Auth System Configuration
- MAX_LOGIN_ATTEMPTS: 10
- LOCKOUT_DURATION_MINUTES: 15
- Auto-clear expired lockouts on next login attempt
- Admin can unlock accounts via /api/auth/admin/unlock-account

## Credentials
- Owner: owner@bigmannentertainment.com / Test1234!
- Super Admin: cveadmin@test.com / Test1234!

## Backlog
- P2: Real-time Notifications for creators
- P2: Backend file organization (routes into /routes/, models into /models/)
- P3: Further component extraction if needed

## Refactoring Completed
- **PostgreSQL Creator Profile Cleanup (Mar 2026)** - Removed 7 obsolete PG-based files. Made `postgres_client.py` and `postgres_ledger.py` gracefully handle missing PG config.
- **Route Conflict Fix (Mar 2026)** - Changed content routes prefix from `/content` to `/user-content` to avoid conflict with existing `media_routes.py` `/content/{media_id}` endpoints.
