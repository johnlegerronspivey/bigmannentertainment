# Big Mann Entertainment - Product Requirements Document

## Original Problem Statement
Build a comprehensive creator tools platform for Big Mann Entertainment that enables content management, distribution, analytics, messaging, and monetization for music/media creators.

## Core Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **File Storage**: Local `/app/uploads/content/`, `/app/uploads/hub/`
- **CDN**: AWS CloudFront via `cdn.bigmannentertainment.com`
- **Key Routes**: `/app/backend/routes/` (24 core routers) + `/app/backend/api/` (78+ endpoint routers)

## Unified Label Network (ULN) — Architectural Vision

### What a "Unified Label" Means
A unified label is: Identity-centric, Rights-aware, Distribution-native, Governance-enabled, Audit-ready.
**Label = Tenant + Rights Authority + Distribution Hub + Governance Node.**

### Upgrade Plan (3 Layers)
- **Phase A — Identity & Ownership (Quick Win)** COMPLETE
  - `label_members` collection: `{labelId, userId, role, joinedAt}`
  - `GET /api/uln/me/labels` — user's labels with roles
  - `POST/DELETE /api/uln/labels/{id}/members` — add/remove members
  - `PUT /api/uln/labels/{id}/members/{userId}/role` — change roles
  - Label Switcher dropdown in ULN header
  - Members tab with table, role badges, add/remove/edit
  - Auto-add owner on label registration
  - Role hierarchy: owner(4) > admin(3) > a_and_r(2) > viewer(1)
  - Testing: 100% pass (iteration_93)

- **Phase B — Catalog, Rights & Distribution** COMPLETE
  - `label_assets` collection: Real CRUD (create, read, update, delete) for catalog assets
  - `label_rights` collection: Rights splits (party, role, percentage), territories, AI consent, sponsorship rules, exclusive flag
  - `label_endpoints` collection: Real CRUD for DSP distribution endpoints (platform, status, type)
  - CRUD APIs: POST/PUT/DELETE for assets, PUT for rights (upsert), POST/PUT/DELETE for endpoints
  - `GET /api/uln/labels/{id}/catalog` — real assets (no seed data)
  - `GET /api/uln/labels/{id}/distribution/status` — real endpoints with summary
  - `GET /api/uln/labels/{id}/audit-snapshot` — v2.0 snapshot including rights data
  - Frontend refactored: Split into `LabelCatalog.js`, `LabelDistributionStatus.js`, `LabelAuditSnapshot.js`
  - Catalog tab: Add/Edit/Delete assets + Rights management panel per asset
  - Distribution tab: Add/Edit/Delete endpoints + summary cards + health bar
  - Testing: 100% pass (iteration_94, 30/30 backend + all frontend verified)

- **Phase C — Governance, Disputes & Audit** (FUTURE)
  - `label_disputes` collection
  - `GET /api/uln/labels/{id}/disputes`
  - Dispute resolution, governance rules
  - Unified Label Dashboard

## Key Features Implemented (Summary)

### Phases 1-11: Core Platform
- Auth (JWT), Creator profiles, Media upload/distribution, Stripe/PayPal payments
- Watermarking, Admin panel, AWS integrations, Web3/DAO governance
- Content management, DMs, Analytics, File preview, Notifications
- Social Media 120-platform connections, URL-based connections (25 adapters)
- Distribution Hub (12 templates, 10 platform delivery adapters)
- Advanced Analytics (anomaly detection, demographics, revenue tracking)

### Phase 31: ULN Enhanced Features
- Real Blockchain (SHA-256 hash chain, proof-of-work, Merkle tree)
- Live Royalty Data (955 earnings across 20 labels)
- ULN Analytics Dashboard
- Label Onboarding Wizard (5-step)
- Inter-Label Messaging (threads + read receipts)

### Phase 32: Enhanced Facebook & Instagram URL Scrapers
- 3-strategy Facebook scraper (HTML, mobile, Graph API)
- 3-strategy Instagram scraper (API, HTML, oEmbed)
- Manual metrics fallback when auto-scraping fails

### Phase 33: ULN Phase A — Identity & Label Switcher
- label_members collection with role hierarchy
- GET /me/labels + CRUD member endpoints
- Auto-owner on registration
- Label Switcher UI + Members tab

### Phase 34: ULN Phase A — Catalog, Distribution & Audit Snapshot
- Seed-data based catalog and distribution endpoints (now superseded by Phase B)

### Phase 35: ULN Phase B — Real Catalog, Rights & Distribution (Feb 2026)
- Replaced seed data with real MongoDB CRUD for `label_assets`, `label_rights`, `label_endpoints`
- Full REST API: POST/PUT/DELETE assets, PUT rights (upsert), POST/PUT/DELETE endpoints
- Frontend refactored from monolithic `ULNComponents.js` (2900+ lines) into dedicated split components
- Rights management: revenue splits, territory selection, AI consent toggle, sponsorship rules
- Distribution management: platform endpoints with health monitoring
- Audit snapshot upgraded to v2.0 (includes rights data)

## Key API Endpoints
- Auth: `POST /api/auth/login`, `POST /api/auth/register`
- ULN Core: `GET/POST /api/uln/labels`, `GET /api/uln/dashboard/stats`
- ULN Members: `GET /api/uln/me/labels`, `GET/POST /api/uln/labels/{id}/members`, `PUT/DELETE member/{userId}`
- ULN Catalog: `GET /api/uln/labels/{id}/catalog`, `POST/PUT/DELETE /api/uln/labels/{id}/catalog/assets/{assetId}`
- ULN Rights: `GET/PUT /api/uln/labels/{id}/catalog/assets/{assetId}/rights`
- ULN Distribution: `GET /api/uln/labels/{id}/distribution/status`, `POST/PUT/DELETE /api/uln/labels/{id}/endpoints/{endpointId}`
- ULN Audit: `GET /api/uln/labels/{id}/audit-snapshot`
- Social: `GET /api/social/platforms`, `POST /api/social/connect-url`
- Distribution: `POST /api/distribution-hub/distribute`
- Analytics: `GET /api/analytics/overview`

## DB Collections
- `users`, `uln_labels`, `label_members`, `label_assets`, `label_rights`, `label_endpoints`
- `uln_blockchain_blocks`, `uln_blockchain_transactions`
- `uln_smart_contracts_live`, `royalty_earnings`, `uln_onboarding`, `uln_message_threads`, `uln_messages`
- `platform_credentials`, `platform_metrics`, `user_content`, `distribution_hub_content`
- `uln_audit_trail`, `notifications`, `messages`, `conversations`

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Backlog (Prioritized)
- **P1**: Phase C — Governance, Disputes & Audit (label_disputes, dispute resolution, governance rules)
- **P1**: Connect to Live APIs for real-time metrics (blocked by Meta API keys)
- **P2**: Revenue auto-import from platform APIs
- **P3**: Quick Actions Panel for GS1 Hub
- **P4**: DNS Health Checker
- **P5**: Automated CVE monitoring dashboard
- **P5**: ULN Notification System
