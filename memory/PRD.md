# Big Mann Entertainment - Product Requirements Document

## Original Problem Statement
Build a social media management and creator tools platform featuring the Unified Label Network (ULN) for cross-label collaboration, content sharing, and royalty distribution. The platform includes Facebook/Instagram URL scrapers and a multi-phase ULN architecture.

## Core Features

### Implemented
- **Facebook & Instagram URL Scrapers** — Public data scraping with manual metric fallback
- **ULN Phase A: Identity & Label Switcher** — `uln_labels`, `label_members`, `GET /me/labels`, Label Switcher UI, Members Tab
- **ULN Phase B: Catalog, Rights & Distribution** — `label_assets`, `label_rights`, `label_endpoints` collections, Full CRUD APIs, modular UI
- **ULN Phase C: Governance, Disputes & Audit** — `label_governance`, `label_disputes` collections, full CRUD APIs, governance rules (5 types), dispute management (6 types) with response timeline, audit trail integration, modular frontend components
- **ULNComponents.js Refactoring (2026-03-25)** — Reduced from 2289 to 224 lines by extracting 6 component groups into `/app/frontend/src/uln/`
- **ULN Notification System (2026-03-27)** — Real-time notification system with MongoDB-backed CRUD, user preferences, type/severity filtering, unread badges (bell + tab), and integration hooks into governance/disputes/members services

### Refactoring Details (Completed 2026-03-25)
Extracted from `ULNComponents.js`:
- `ULNOverview.js` — Overview metrics, global distribution, recent activity, system status
- `LabelHub.js` — Label hub with filters, cards, edit modal, bulk edit, advanced search, export
- `CrossLabelContentSharing.js` — Federated content, metadata sync, permissions, usage attribution
- `RoyaltyPoolManagement.js` — Royalty pools, earnings processing, payout ledger, distribution management
- `DAOGovernance.js` — Proposals, voting interface, governance rules, governance history
- `ULNAnalytics.js` — Network growth, financial analytics, governance analytics

### ULN Notification System (Completed 2026-03-27)
- **Backend**: `uln_notification_service.py` + `uln_notification_endpoints.py`
- **Collections**: `uln_notifications`, `uln_notification_preferences`
- **13 notification types**: member_added, member_removed, governance_rule_created/updated/deleted, dispute_filed/updated/resolved, catalog_asset_added, distribution_updated, royalty_payout, label_registered, system
- **4 severity levels**: info, warning, success, error
- **Features**: CRUD, mark read/all read, delete/clear all, user preferences (enabled toggle + muted types), type filtering, unread-only filter, pagination
- **Frontend**: `ULNNotifications.js` component, notification bell with badge in header, tab with unread count badge
- **Integration**: Auto-emits notifications when governance rules created, disputes filed/responded, members added

### Backlog
- **P1**: Revenue Tracking — Connect mocked-up feature to real data sources
- **P2**: DNS Health Checker
- **P3**: Quick Actions Panel for GS1 Hub
- **P4**: Automated CVE monitoring dashboard
- **P6**: Catalog Bulk Import via CSV
- **P7**: Governance Dashboard widget on Overview tab

## Architecture
```
/app
├── backend/
│   ├── api/
│   │   ├── uln_endpoints.py
│   │   ├── uln_label_members_endpoints.py
│   │   ├── uln_catalog_distribution_endpoints.py
│   │   ├── uln_governance_disputes_endpoints.py
│   │   └── uln_notification_endpoints.py (NEW)
│   ├── services/
│   │   ├── uln_service.py
│   │   ├── uln_label_members_service.py
│   │   ├── uln_catalog_distribution_service.py
│   │   ├── uln_governance_disputes_service.py
│   │   └── uln_notification_service.py (NEW)
│   └── router_setup.py
├── frontend/src/
│   ├── ULNComponents.js (Orchestrator - ~270 lines)
│   └── uln/
│       ├── ULNOverview.js
│       ├── LabelHub.js
│       ├── CrossLabelContentSharing.js
│       ├── RoyaltyPoolManagement.js
│       ├── DAOGovernance.js
│       ├── ULNAnalytics.js
│       ├── LabelCatalog.js
│       ├── LabelDistributionStatus.js
│       ├── LabelAuditSnapshot.js
│       ├── LabelGovernance.js
│       ├── LabelDisputes.js
│       ├── LabelMembers.js
│       └── ULNNotifications.js (NEW)
└── memory/PRD.md
```

## Key API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/uln/me/labels` | GET | List user's labels |
| `/api/uln/labels/{id}/members` | GET/POST | Label members |
| `/api/uln/labels/{id}/catalog` | GET/POST | Catalog assets |
| `/api/uln/labels/{id}/distribution/status` | GET/POST | Distribution endpoints |
| `/api/uln/labels/{id}/audit-snapshot` | GET | Audit snapshot |
| `/api/uln/labels/{id}/governance` | GET/POST | Governance rules |
| `/api/uln/labels/{id}/governance/{rule_id}` | PUT/DELETE | Update/delete rule |
| `/api/uln/labels/{id}/disputes` | GET/POST | Label disputes |
| `/api/uln/labels/{id}/disputes/{dispute_id}` | GET/PUT | Dispute detail/update |
| `/api/uln/labels/{id}/disputes/{dispute_id}/respond` | POST | Respond to dispute |
| `/api/uln/labels/{id}/governance-disputes-summary` | GET | Combined summary |
| `/api/uln/notifications` | GET/POST | List/create notifications |
| `/api/uln/notifications/unread-count` | GET | Unread count |
| `/api/uln/notifications/{id}/read` | PUT | Mark as read |
| `/api/uln/notifications/read-all` | PUT | Mark all as read |
| `/api/uln/notifications/{id}` | DELETE | Delete notification |
| `/api/uln/notifications/clear` | DELETE | Clear all |
| `/api/uln/notifications/preferences` | GET/PUT | User preferences |

## Test Credentials
- Email: `owner@bigmannentertainment.com`
- Password: `Test1234!`
- Known Label ID: `BM-LBL-9D0377FB`

## Project Health
- **Mocked**: Revenue Tracking (pending real API integration)
- **All other features**: Real MongoDB-backed implementations
