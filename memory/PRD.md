# ULN Social Media Management & Creator Tools Platform — PRD

## Original Problem Statement
Build a social media management and creator tools platform featuring the Unified Label Network (ULN). The platform includes a ULN Notification System and an immutable Ownership Protection System for John LeGerron Spivey and Big Mann Entertainment.

## Core Requirements

### Verified & Complete
- ULN Notification System (In-app notifications for Governance, Disputes, Members, etc.)
- Strict Immutable Ownership & Percentage Protections (master_licensing enforced at 100%)
- DNS Health Checker and lookup functionality
- Automated CVE Monitoring Dashboard
- Mandatory GS1 & Business Identifiers Enforcement
- Fix and upgrade all CVE vulnerabilities (Backend to 0, Frontend to 0)
- Migrate frontend application from Create React App (CRA) to Vite
- Upgrade Tailwind CSS from v3 to v4
- DUNS Number 080955411 added to protected Business & GS1 Identifiers (2026-04-08)
- Business Registration Number updated to Taxpayer ID 12800 (2026-04-08)
- AWS External DNS Health Tracking via Route 53 (2026-04-09) — Register targets, monitor from 13+ global AWS regions, refresh status, delete targets
- Revenue Tracking connected to real MongoDB data (2026-04-09) — Full CRUD: overview, per-platform detail, record revenue, paginated transactions with filtering

### Pending
- "Register New Target" for DNS Health Checker (local DNS monitors — separate from AWS)

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React (Vite 8 with Rolldown/Oxc) + Tailwind CSS v4 (CSS-first)
- **Key Collections**: label_assets, label_rights, label_distributions, uln_labels, users, label_members, business_information, gs1_database, label_governance, label_disputes, business_identifiers, aws_dns_targets, revenue_tracking

## Protected Owner
- Owner: John LeGerron Spivey
- Business: Big Mann Entertainment
- DUNS: 080955411
- EIN: 270658077
- Taxpayer ID: 12800
- GS1 Company Prefix: 08600043402
- GLN: 0860004340201

## Upcoming Tasks (Priority Order)
- P1: "Register New Target" for local DNS Health Checker (monitors)
- P2: General feature completion and real data integration

## Tech Stack Notes
- Vite 8 uses Rolldown/Oxc (NOT esbuild) — configured via `transformWithOxc`
- Tailwind v4 CSS-first config in `index.css` with `@theme inline`
- `@apply` in secondary CSS files requires `@reference "./index.css"`
- shadcn/ui components configured for Tailwind v4

## Revenue Tracking (Implemented 2026-04-09)
### Backend
- Service: `/app/backend/services/revenue_tracking_service.py`
- Endpoints: `/app/backend/api/revenue_tracking_endpoints.py`
- Routes: Registered via `router_setup.py` under `/api/revenue`

### API Endpoints
- `GET /api/revenue/overview` — Revenue overview with platform/source/trend breakdowns
- `GET /api/revenue/platform/{platform_id}` — Per-platform detail with recent transactions
- `POST /api/revenue/record` — Record new revenue entry
- `GET /api/revenue/transactions` — Paginated, filterable transaction list
- `DELETE /api/revenue/transactions/{date_key}` — Delete a transaction

### Frontend
- Page: `/app/frontend/src/pages/RevenueTrackingPage.jsx`
- Route: `/revenue` (protected)
- Navigation: Finance dropdown in NavigationBar
- Features: Overview dashboard, Platform cards, Transaction list with filters, Record Revenue form

## AWS External DNS Health Tracking (Implemented 2026-04-09)
### Backend
- Service: `/app/backend/services/aws_dns_health_service.py`
- Endpoints: `/app/backend/api/aws_dns_health_endpoints.py`
- Routes: Registered via `router_setup.py` under `/api/aws-dns`

### API Endpoints
- `POST /api/aws-dns/targets` — Register new domain target
- `GET /api/aws-dns/targets` — List user's registered targets
- `GET /api/aws-dns/targets/{target_id}` — Get single target
- `POST /api/aws-dns/targets/{target_id}/refresh` — Refresh status from AWS
- `DELETE /api/aws-dns/targets/{target_id}` — Delete target + AWS health check
- `GET /api/aws-dns/aws-checks` — List all AWS health checks (admin view)

### Frontend
- Added "AWS Health" tab to `/app/frontend/src/pages/DNSHealthPage.jsx`
- Features: Register form with advanced options, target cards with status badges, global region grid
