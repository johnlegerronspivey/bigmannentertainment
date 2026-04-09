# ULN Social Media Management & Creator Tools Platform — PRD

## Original Problem Statement
Build a social media management and creator tools platform featuring the Unified Label Network (ULN). The platform includes a ULN Notification System and an immutable Ownership Protection System for John LeGerron Spivey and Big Mann Entertainment.

## Core Users
- **Owner**: John LeGerron Spivey (Big Mann Entertainment)
- **Admin**: Platform administrators managing compliance, CVE monitoring
- **Creators**: Artists, producers, contributors on the label

## Tech Stack
- **Frontend**: React + Vite 8 (Rolldown/Oxc) + Tailwind CSS v4
- **Backend**: FastAPI + Python
- **Database**: MongoDB (Motor async driver)
- **Routing**: `/api` prefix auto-routed to backend via Kubernetes ingress

## Completed Features

### Phase 1 — Core Platform (Completed)
- [x] ULN Notification System
- [x] Strict Immutable Ownership & Percentage Protections
- [x] DNS Health Checker & AWS Route 53 Health Monitoring
- [x] Automated CVE Monitoring Dashboard
- [x] Mandatory GS1 & Business Identifiers Enforcement

### Phase 2 — Infrastructure (Completed)
- [x] Migrate frontend from CRA to Vite 8
- [x] Upgrade Tailwind CSS from v3 to v4

### Phase 3 — Revenue & Analytics (Completed)
- [x] Connect mocked Revenue Tracking to real data sources
- [x] CSV/Excel export for revenue reports
- [x] Date-Range picker controls for export UI and transaction lists
- [x] Creator Analytics de-mocking (Demographics, Geography, Best Times)
- [x] Analytics Forecasting & Comprehensive Platform De-mocking (Revenue, Performance, ROI, Trends, Forecast)

### Phase 4 — Non-Analytics Module De-mocking (Completed 2026-04-09)
- [x] Content Manager — real data from `user_content` + `label_assets` collections
- [x] Compliance Center — real data from `compliance_documents`, `compliance_audit_logs`, `label_rights`
- [x] Sponsorship & Campaigns — real data from `campaigns`, `campaign_performance`, `partnerships`
- [x] Contributor Hub — real data from `label_members`, `creator_profiles`, `royalty_earnings`, `payment_transactions`
- [x] KPI Dashboard — real-time aggregation from all 4 modules
- [x] Frontend hardcoded fallbacks scrubbed (all replaced with `0` defaults)
- [x] Router prefix fix (`/api/platform` → `/platform` under api_router)

## Key API Endpoints
| Endpoint | Status |
|---|---|
| GET /api/platform/content/stats | Real |
| GET /api/platform/content/assets | Real |
| GET /api/platform/content/folders | Real |
| GET /api/platform/content/search | Real |
| GET /api/platform/compliance/status | Real |
| GET /api/platform/compliance/alerts | Real |
| GET /api/platform/sponsorship/campaigns | Real |
| GET /api/platform/sponsorship/analytics | Real |
| GET /api/platform/sponsorship/opportunities | Real |
| GET /api/platform/contributors/search | Real |
| GET /api/platform/contributors/stats | Real |
| GET /api/platform/contributors/collaborations | Real |
| GET /api/platform/contributors/requests | Real |
| GET /api/platform/contributors/payments | Real |
| GET /api/platform/analytics/revenue | Real |
| GET /api/platform/analytics/performance | Real |
| GET /api/platform/analytics/roi | Real |
| GET /api/platform/analytics/trends | Real |
| POST /api/platform/analytics/forecast | Real |

## Key DB Collections
- `user_content` (8 docs), `label_assets` (12 docs)
- `compliance_documents` (1805 docs), `compliance_audit_logs` (51+), `label_rights` (1 doc)
- `campaigns` (12 docs), `campaign_performance` (9 docs), `partnerships` (8 docs)
- `label_members` (43 docs), `creator_profiles` (2 docs)
- `royalty_earnings` (955 docs), `payment_transactions` (4 docs)
- `revenue_tracking` (278 docs), `analytics_events` (3869 docs)

## Backlog (Prioritized)
### P2 — Upcoming
- [ ] Scheduled email reports (auto-send weekly/monthly revenue summaries as CSV)
- [ ] AI-powered content recommendations (analyze patterns, suggest strategies)

### P3 — Future
- [ ] Refactor `ComprehensivePlatformComponents.js` (~4300 lines) into smaller components
- [ ] Real-time WebSocket notifications
- [ ] Advanced permission-based role management

## Technical Notes
- **Vite 8**: Uses `transformWithOxc: { lang: 'jsx' }`. Do NOT revert to esbuild.
- **Tailwind v4**: `@apply` in non-entry CSS requires `@reference "./index.css"`.
- **MongoDB**: Always exclude `_id` in projections. Use `or 0` pattern for nullable aggregation values.
- **Router**: Comprehensive platform endpoints use prefix `/platform` (NOT `/api/platform`) since they're nested under `api_router` with `/api` prefix.
