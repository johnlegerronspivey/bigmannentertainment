# Big Mann Entertainment - Product Requirements Document

## Original Problem Statement
Big Mann Entertainment is a complete media distribution platform founded by John LeGerron Spivey. The application enables content creators to distribute their media (audio, video, images) across 117+ platforms worldwide, manage royalties, handle compliance, and leverage blockchain technologies.

## Architecture
- **Frontend**: React with lazy-loaded components, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python) with MongoDB
- **3rd Party**: Jira, Stripe, AWS (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, CloudWatch, Inspector, Detective, RDS, Route53), Google Generative AI

## Code Structure
```
/app
├── backend/
│   └── server.py
└── frontend/
    └── src/
        ├── App.js
        ├── components/
        │   ├── layout/NavigationBar.jsx
        │   ├── ui/ (Shadcn UI components)
        │   ├── ChunkErrorBoundary.jsx
        │   ├── ErrorBoundary.js
        │   ├── LoadingSkeleton.js
        │   └── LoadingSpinner.js
        ├── contexts/AuthContext.jsx
        ├── pages/
        │   ├── HomePage.jsx, LoginPage.jsx, RegisterPage.jsx
        │   ├── ForgotPasswordPage.jsx, ResetPasswordPage.jsx
        │   ├── NotFoundPage.jsx, AdminNotificationsPage.jsx
        │   ├── LibraryPage.jsx, DistributePage.jsx
        │   ├── PlatformsPage.jsx, PricingPage.jsx
        │   └── RDSUpgradePage.jsx
        ├── admin/DomainConfigPage.jsx
        ├── cve/ (CVE management module)
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
- Page components extraction to /pages/ directory (11 components)
- Amazon RDS PostgreSQL Minor Version Upgrade (Feb 2026)
- Added "Fansly" to platform list
- **P0 Account Lockout Fix (Feb 2026)**
  - Root cause: expired lockout didn't reset failed_login_attempts, so one wrong password immediately re-locked
  - Fix: auto-clear expired lockouts, MAX_LOGIN_ATTEMPTS 5->10, LOCKOUT_DURATION 30->15 min
  - Added admin endpoints: GET /api/auth/admin/locked-accounts, POST /api/auth/admin/unlock-account
  - Error messages now show remaining attempts
  - All 20 tests passing (16 backend + 4 frontend)

## Auth System Configuration
- MAX_LOGIN_ATTEMPTS: 10
- LOCKOUT_DURATION_MINUTES: 15
- Auto-clear expired lockouts on next login attempt
- Admin can unlock accounts via /api/auth/admin/unlock-account

## Credentials
- Owner: owner@bigmannentertainment.com / Test1234!
- Super Admin: cveadmin@test.com / Test1234!

## Backlog
- P1: Re-evaluate full project backlog with user
- P2: Further component extraction if needed
- P3: Backend file organization (routes into /routes/, models into /models/)
