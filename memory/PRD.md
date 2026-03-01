# Big Mann Entertainment - CVE Management Platform PRD

## Original Problem Statement
Multi-tenant CVE management platform with role-based administration, ticketing integration, SLA tracking, and comprehensive security features.

## Core Requirements
- Role-based tenant admin (super_admin, tenant_admin)
- Full Ticketing Configuration UI (Jira/ServiceNow)
- SLA Tracking Dashboard
- Per-tenant data scoping
- Per-user notifications
- PDF reports
- Dashboard trends
- Live infrastructure visualization

## What's Been Implemented
- All core features listed above
- SLA Tracking Dashboard (MTTR, resolution rates, breach timelines, team performance)
- Role-based access control
- Live Jira integration
- Data migration for tenancy
- **Branding cleanup** (Feb 28, 2026) — Removed all user-visible references to "Emergent" from app
- **Integration Migration** (Feb 28, 2026) — Replaced `emergentintegrations` package with:
  - Native Google Gemini (`google-generativeai`) via `/app/backend/llm_service.py`
  - Native Stripe (`stripe`) via `/app/backend/stripe_native_service.py`
  - Replaced `EMERGENT_LLM_KEY` env var with `GOOGLE_API_KEY`
  - Updated tracking blocker from `.emergent.sh` to `.bigmannentertainment.com`
- **AWS Integration** (Feb 28, 2026) — Live AWS credentials integrated:
  - S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, CloudWatch, Inspector, Detective, RDS
- **Domain Configuration** (Mar 1, 2026) — bigmannentertainment.com:
  - CORS updated for www, api, cdn subdomains
  - PWA manifest.json created
  - robots.txt for SEO
  - Security headers middleware (HSTS, X-Frame-Options, X-Content-Type-Options, XSS Protection, Referrer-Policy, Permissions-Policy)
  - SES domain verification endpoints (initiate, check status)
  - DNS configuration guide endpoint with required records
  - Admin Domain Configuration UI page at /admin/domain
  - Canonical URL meta tag for production SEO
  - SES domain identity verification initiated (Pending DNS record setup)

## Architecture
- **Frontend:** React + Shadcn UI
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based with super_admin/tenant_admin roles
- **LLM:** Google Gemini (gemini-2.5-flash/pro) via native google-generativeai SDK
- **Payments:** Stripe via native stripe SDK
- **Integrations:** Jira (live), Stripe, PayPal, AWS (live)

## Credentials
- Super Admin: cveadmin@test.com / Test1234!
- Tenant Admin: enterprise@test.com / test

## Key Files
- `/app/backend/llm_service.py` — LlmChat, UserMessage classes (Google Gemini)
- `/app/backend/stripe_native_service.py` — StripeCheckout classes (native Stripe)
- `/app/backend/routes/aws_routes.py` — AWS + Domain configuration endpoints
- `/app/backend/server.py` — Security headers middleware
- `/app/backend/config/settings.py` — CORS configuration
- `/app/frontend/src/admin/DomainConfigPage.jsx` — Domain config admin UI
- `/app/frontend/public/manifest.json` — PWA manifest
- `/app/frontend/public/robots.txt` — SEO robots file
- `/app/backend/.env` — All AWS, SES, domain credentials

## Domain Configuration Status
- **Domain:** bigmannentertainment.com
- **SES Verification:** Pending (DKIM tokens generated, DNS records need to be added)
- **CloudFront CDN:** Active at cdn.bigmannentertainment.com
- **Security Headers:** Active (6 headers)
- **DNS Records Required:** 7 records (A, CNAME www/api/cdn, TXT SPF/DMARC, MX)

## Backlog
- P0: User to add DNS records at domain registrar to complete SES verification
- P1: User verification of all completed features (SLA Dashboard, Ticketing, etc.)
- Future tasks: TBD based on user feedback
