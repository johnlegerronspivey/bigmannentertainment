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
- **Emergent name/key cleanup** (Feb 28, 2026) — Removed all user-visible references to "Emergent" from app code, API responses, comments, URLs, and email templates

## Architecture
- **Frontend:** React + Shadcn UI
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based with super_admin/tenant_admin roles
- **Integrations:** Jira (live), Stripe, PayPal, AI (GPT-5, Gemini)

## Credentials
- Super Admin: cveadmin@test.com / Test1234!
- Tenant Admin: enterprise@test.com / test

## Backlog
- P0: User verification of all completed features
- Future tasks: TBD based on user feedback
