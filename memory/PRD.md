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
│   │   ├── creator_profile_routes.py  (NEW - MongoDB creator profiles)
│   │   ├── watermark_routes.py        (NEW - Content watermarking)
│   │   ├── subscription_routes.py     (NEW - Subscription tiers)
│   │   ├── auth_routes.py, admin_routes.py, ...
│   ├── config/, models/, auth/, services/
│   └── router_setup.py
└── frontend/
    └── src/
        ├── App.js
        ├── pages/
        │   ├── CreatorProfilesPage.jsx  (NEW)
        │   ├── WatermarkPage.jsx        (NEW)
        │   ├── SubscriptionPage.jsx     (NEW)
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

## New Feature Details

### Creator Profiles
- **Backend**: `/api/creator-profiles` (POST, GET /me, PUT /me, GET /browse, GET /u/{username})
- **Frontend**: `/creator-profiles` page with My Profile tab and Browse Creators tab
- **Data**: MongoDB `creator_profiles` collection
- **Fields**: display_name, username, bio, tagline, location, genres, social_links, stats, subscription_tier

### Content Watermarking
- **Backend**: `/api/watermark` (GET/PUT /settings, POST /preview, POST /apply)
- **Frontend**: `/watermark` page with settings panel and image upload/preview
- **Data**: MongoDB `watermark_settings` collection
- **Features**: Custom text, position (6 options), opacity, font size, color, rotation, tiled mode

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
- P2: Backend file organization (routes into /routes/, models into /models/)
- P3: Further component extraction if needed
