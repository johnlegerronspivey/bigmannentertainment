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
- **Branding cleanup** (Feb 28, 2026) — Removed all user-visible references to "Emergent"
- **Integration Migration** (Feb 28, 2026) — Native Google Gemini + Stripe SDKs
- **AWS Integration** (Feb 28, 2026) — Live S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, CloudWatch, Inspector, Detective, RDS
- **Domain Configuration** (Mar 1, 2026) — bigmannentertainment.com:
  - CORS, manifest.json, robots.txt, canonical URL
  - Security headers middleware (HSTS, X-Frame-Options, XSS Protection, etc.)
  - SES domain verification endpoints + DNS guide
- **Route53 DNS Integration** (Mar 1, 2026):
  - Live Route53 service connecting to hosted zone Z21AGOWAOOGWWZ
  - Auto-configure endpoint: creates SPF, DMARC, DKIM (3 CNAMEs), SES verification TXT, WWW CNAME, MX
  - CRUD for individual DNS records (add/update/delete)
  - Admin UI at /admin/domain with auto-configure, records table, add/delete, name servers display
  - Successfully auto-configured 8/8 DNS records; SES domain now verified

## Architecture
- **Frontend:** React + Shadcn UI
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based with super_admin/tenant_admin roles
- **LLM:** Google Gemini via native google-generativeai SDK
- **Payments:** Stripe via native stripe SDK
- **AWS:** S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, CloudWatch, Inspector, Detective, RDS, Route53

## Credentials
- Super Admin: cveadmin@test.com / Test1234!
- Tenant Admin: enterprise@test.com / test

## Key Files
- `/app/backend/services/route53_svc.py` — Route53Service class
- `/app/backend/routes/aws_routes.py` — AWS + Domain + Route53 endpoints
- `/app/backend/server.py` — Security headers middleware
- `/app/backend/config/settings.py` — CORS configuration
- `/app/frontend/src/admin/DomainConfigPage.jsx` — Domain config admin UI
- `/app/frontend/public/manifest.json` — PWA manifest
- `/app/frontend/public/robots.txt` — SEO robots file

## Backlog
- P1: User verification of all completed features (SLA Dashboard, Ticketing, etc.)
- Future tasks: TBD based on user feedback
