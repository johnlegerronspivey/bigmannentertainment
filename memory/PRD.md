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
- **Phase A — Identity & Ownership (Quick Win)** ✅ COMPLETE
  - `label_members` collection: `{labelId, userId, role, joinedAt}`
  - `GET /api/uln/me/labels` — user's labels with roles
  - `POST/DELETE /api/uln/labels/{id}/members` — add/remove members
  - `PUT /api/uln/labels/{id}/members/{userId}/role` — change roles
  - Label Switcher dropdown in ULN header
  - Members tab with table, role badges, add/remove/edit
  - Auto-add owner on label registration
  - Role hierarchy: owner(4) > admin(3) > a_and_r(2) > viewer(1)
  - Testing: 100% pass (14/14 backend, all frontend verified - iteration_92)

- **Phase B — Catalog, Rights & Distribution** (UPCOMING)
  - `label_assets` collection: `{labelId, assetId, type, status}`
  - `label_rights` collection: `{assetId, labelId, splits, territories, aiConsent, sponsorshipRules}`
  - `GET /api/uln/labels/{id}/catalog` — all assets under label
  - Rights management UI

- **Phase C — Distribution Graph** (FUTURE)
  - `label_endpoints` collection: `{labelId, platform, endpointType, credentialsRef}`
  - `POST /api/uln/labels/{id}/distribute`
  - `GET /api/uln/labels/{id}/distribution/status`
  - Per-label distribution map UI

- **Phase D — Governance, Disputes & Audit Snapshot** (FUTURE)
  - `label_disputes` collection
  - `GET /api/uln/labels/{id}/disputes`
  - `GET /api/uln/labels/{id}/audit/snapshot` — JSON export
  - Unified Label Dashboard: Catalog / Distribution / Earnings / Governance / Audit

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
- Enriched URL connection response

### Phase 33: ULN Phase A — Identity & Label Switcher ✅
- label_members collection with role hierarchy
- GET /me/labels + CRUD member endpoints
- Auto-owner on registration
- Label Switcher UI + Members tab

## Key API Endpoints
- Auth: `POST /api/auth/login`, `POST /api/auth/register`
- ULN Core: `GET/POST /api/uln/labels`, `GET /api/uln/dashboard/stats`
- ULN Members: `GET /api/uln/me/labels`, `GET/POST /api/uln/labels/{id}/members`, `PUT/DELETE member/{userId}`
- Social: `GET /api/social/platforms`, `POST /api/social/connect-url`
- Distribution: `POST /api/distribution-hub/distribute`
- Analytics: `GET /api/analytics/overview`

## DB Collections
- `users`, `uln_labels`, `label_members` (NEW), `uln_blockchain_blocks`, `uln_blockchain_transactions`
- `uln_smart_contracts_live`, `royalty_earnings`, `uln_onboarding`, `uln_message_threads`, `uln_messages`
- `platform_credentials`, `platform_metrics`, `user_content`, `distribution_hub_content`
- `uln_audit_trail`, `notifications`, `messages`, `conversations`

## Test Credentials
- Owner: `owner@bigmannentertainment.com` / `Test1234!`
- Admin: `cveadmin@test.com` / `Test1234!`

## Backlog (Prioritized)
- **P0**: Phase B — Catalog & Rights Binding (label_assets, label_rights, catalog API)
- **P0**: Phase C — Distribution Graph (label_endpoints, per-label distribution)
- **P1**: Phase D — Governance, Disputes & Audit Snapshot
- **P1**: Connect to Live APIs for real-time metrics (blocked by Meta API keys)
- **P2**: Revenue auto-import from platform APIs
- **P3**: Quick Actions Panel for GS1 Hub
- **P4**: DNS Health Checker
- **P5**: Automated CVE monitoring dashboard
- **P5**: ULN Notification System
