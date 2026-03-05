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
        ├── App.js                          # Main router (354 lines, lazy imports only)
        ├── components/
        │   ├── layout/
        │   │   └── NavigationBar.jsx       # Navigation component
        │   ├── ui/                         # Shadcn UI components
        │   ├── ChunkErrorBoundary.jsx
        │   ├── ErrorBoundary.js
        │   ├── LoadingSkeleton.js
        │   └── LoadingSpinner.js
        ├── contexts/
        │   └── AuthContext.jsx             # Auth context (AuthProvider, useAuth, ProtectedRoute, AdminRoute)
        ├── pages/                          # Extracted page components
        │   ├── HomePage.jsx
        │   ├── LoginPage.jsx
        │   ├── RegisterPage.jsx
        │   ├── ForgotPasswordPage.jsx
        │   ├── ResetPasswordPage.jsx
        │   ├── NotFoundPage.jsx
        │   ├── AdminNotificationsPage.jsx
        │   ├── LibraryPage.jsx
        │   ├── DistributePage.jsx
        │   ├── PlatformsPage.jsx
        │   └── PricingPage.jsx
        ├── admin/
        │   └── DomainConfigPage.jsx
        ├── cve/                            # CVE management module
        └── [feature component files]       # ~60+ feature-specific component files
```

## Completed Features
- Navigation Bar UI ✅ (Approved)
- Domain Configuration Page ✅ (Approved)
- CVE Management Dashboard ✅ (Approved)
- SLA Tracker Dashboard ✅ (Approved)
- Tenant Management (RBAC) ✅ (Approved)
- Auth context extraction to AuthContext.jsx ✅
- Navigation extraction to NavigationBar.jsx ✅
- Page components extraction to /pages/ directory ✅ (11 components, App.js: 3196→354 lines)

## Credentials
- Owner: owner@bigmannentertainment.com / Test1234!
- Super Admin: cveadmin@test.com / Test1234!

## Backlog
- P2: Further component extraction if needed (feature-specific files in src/ root)
- P3: Backend file organization (routes into /routes/, models into /models/)
