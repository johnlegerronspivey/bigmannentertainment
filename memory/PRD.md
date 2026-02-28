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

## Architecture
- **Frontend:** React + Shadcn UI
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based with super_admin/tenant_admin roles
- **LLM:** Google Gemini (gemini-2.5-flash/pro) via native google-generativeai SDK
- **Payments:** Stripe via native stripe SDK
- **Integrations:** Jira (live), Stripe, PayPal, AWS

## Credentials
- Super Admin: cveadmin@test.com / Test1234!
- Tenant Admin: enterprise@test.com / test

## Key Files (Integration Migration)
- `/app/backend/llm_service.py` — LlmChat, UserMessage classes (Google Gemini)
- `/app/backend/stripe_native_service.py` — StripeCheckout classes (native Stripe)
- `/app/backend/.env` — GOOGLE_API_KEY configured

## Backlog
- P0: User verification of all completed features
- P1: AWS credentials integration (pending user input)
- P1: Domain configuration (pending user input)
- Future tasks: TBD based on user feedback
