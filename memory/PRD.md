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
- **Ownership Protection System (2026-03-29)** — Immutable ownership guard for John LeGerron Spivey / Big Mann Entertainment. Protects account identity, label ownership roles, and revenue percentages (master_licensing >= 100%). Includes startup drift correction, audit trail for blocked violations, and API verification endpoint.
- **DNS Health Checker (2026-03-29)** — Full DNS lookup and health monitoring system. Supports 9 record types (A, AAAA, MX, NS, TXT, CNAME, SOA, SRV, CAA), comprehensive domain health checks with scoring (A record, IPv6, nameservers, mail, SPF, DMARC, SOA, HTTP, HTTPS), domain monitoring with refresh, and lookup history. Uses real dnspython library. Frontend page at /dns-health with 4 tabs.
- **Automated CVE Monitor (2026-03-29)** — Real-time CVE vulnerability tracking from NVD (National Vulnerability Database) feeds. Features: NVD API integration pulling live CVE data, Watch Rules for monitoring keywords/packages/vendors with severity filters, automated alert generation when watched items match new CVEs, alert management (acknowledge/dismiss), severity breakdown charts, 7-day trend visualization. Backend at /api/cve-monitor, Frontend at /cve-monitor with 4 tabs (Overview, CVE Feed, Watch Rules, Alerts). Uses real NVD API — no mocked data.

- **Catalog CSV Bulk Import (2026-03-29)** — Full CSV upload workflow for migrating existing catalogs into label assets. Features: CSV template download with example data, drag-and-drop file upload, CSV preview with per-row validation, bulk import with ISRC/UPC duplicate detection, skip-duplicates toggle, detailed import report (imported/skipped/errors), audit trail logging. Backend at /api/uln/labels/{label_id}/catalog (csv-template, preview-csv, import-csv). Frontend at /catalog-import with 3-step wizard (Upload, Preview, Results). Accessible from Label dropdown nav and LabelCatalog "Import CSV" button.

### Ownership Protection Details (2026-03-29)
**Protected Fields (IMMUTABLE):**
- Account: email, full_name, business_name, role (super_admin), is_admin (true), is_active (true), account_status (active)
- Label membership: owner role on all labels — cannot be demoted or removed
- Revenue: master_licensing >= 100%, default_royalty_share >= 100%

**Guard Points:**
1. `utils/ownership_guard.py` — Central guard module with constants + validation functions
2. `routes/admin_routes.py` — Admin user update blocked for protected fields
3. `services/uln_label_members_service.py` — Role change & removal blocked
4. `api/uln_endpoints.py` — Revenue percentage modification blocked + status verification endpoint
5. `api/rbac_endpoints.py` — CVE role change & account deactivation blocked
6. `startup.py` — Server boot re-asserts correct values (drift correction)
7. `uln_audit_trail` collection — All blocked attempts logged with severity "critical"

**Verification endpoint:** `GET /api/uln/ownership-protection/status`

### Backlog
- **P0**: Revenue Tracking — Connect mocked-up feature to real data sources
- **P1**: Quick Actions Panel for GS1 Hub
- **P2**: Governance Dashboard widget on Overview tab

## Architecture
```
/app
├── backend/
│   ├── api/
│   │   ├── dns_health_endpoints.py (DNS Health Checker)
│   │   ├── cve_monitor_endpoints.py (Automated CVE Monitor)
│   │   ├── uln_endpoints.py (+ ownership protection status endpoint)
│   │   ├── uln_label_members_endpoints.py
│   │   ├── uln_catalog_distribution_endpoints.py (+ CSV import endpoints)
│   │   ├── uln_governance_disputes_endpoints.py
│   │   ├── uln_notification_endpoints.py
│   │   └── rbac_endpoints.py (+ ownership guard)
│   ├── services/
│   │   ├── dns_health_service.py (DNS lookup, health check, monitoring)
│   │   ├── cve_monitor_service.py (NVD feed, watches, alerts)
│   │   ├── catalog_import_service.py (CSV parsing, validation, bulk import)
│   │   ├── uln_service.py
│   │   ├── uln_label_members_service.py (+ ownership guard)
│   │   ├── uln_catalog_distribution_service.py
│   │   ├── uln_governance_disputes_service.py
│   │   └── uln_notification_service.py
│   ├── routes/
│   │   └── admin_routes.py (+ ownership guard)
│   ├── utils/
│   │   ├── uln_auth.py
│   │   └── ownership_guard.py (central protection module)
│   ├── startup.py (+ drift correction on boot)
│   └── router_setup.py
├── frontend/src/
│   ├── pages/
│   │   ├── DNSHealthPage.jsx (DNS Health Checker)
│   │   ├── CVEMonitorDashboard.jsx (Automated CVE Monitor)
│   │   └── CatalogImportPage.jsx (CSV Bulk Import)
│   ├── ULNComponents.js (Orchestrator)
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
│       └── ULNNotifications.js
└── memory/PRD.md
```

## Key API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/dns/lookup` | POST | DNS record lookup (9 types) |
| `/api/dns/health/{domain}` | GET | Comprehensive DNS health check with scoring |
| `/api/dns/history` | GET | Lookup history (paginated) |
| `/api/dns/monitors` | GET/POST | List/add monitored domains |
| `/api/dns/monitors/{id}` | DELETE | Remove monitored domain |
| `/api/dns/monitors/{id}/refresh` | POST | Refresh health check on monitor |
| `/api/cve-monitor/health` | GET | CVE Monitor health check |
| `/api/cve-monitor/stats` | GET | Monitoring statistics (feeds, watches, alerts, trends) |
| `/api/cve-monitor/feed` | GET | Cached CVE feed entries with search/filter |
| `/api/cve-monitor/feed/refresh` | POST | Fetch fresh CVEs from NVD API |
| `/api/cve-monitor/watches` | GET/POST | List/create watch rules |
| `/api/cve-monitor/watches/{id}/toggle` | PUT | Toggle watch enabled/disabled |
| `/api/cve-monitor/watches/{id}` | DELETE | Delete watch rule |
| `/api/cve-monitor/watches/{id}/refresh` | POST | Refresh specific watch against NVD |
| `/api/cve-monitor/alerts` | GET | List alerts with status/severity filter |
| `/api/cve-monitor/alerts/{id}/acknowledge` | PUT | Acknowledge an alert |
| `/api/cve-monitor/alerts/{id}/dismiss` | PUT | Dismiss an alert |
| `/api/cve-monitor/alerts/acknowledge-all` | POST | Acknowledge all new alerts |
| `/api/uln/ownership-protection/status` | GET | Verify immutable ownership integrity |
| `/api/uln/labels/{id}/catalog/csv-template` | GET | Download CSV import template |
| `/api/uln/labels/{id}/catalog/preview-csv` | POST | Preview & validate CSV before import |
| `/api/uln/labels/{id}/catalog/import-csv` | POST | Bulk import assets from CSV |
| `/api/uln/notifications` | GET/POST | List/create notifications |
| `/api/uln/notifications/unread-count` | GET | Unread count |
| `/api/uln/notifications/{id}/read` | PUT | Mark as read |
| `/api/uln/notifications/read-all` | PUT | Mark all as read |
| `/api/uln/notifications/preferences` | GET/PUT | User preferences |
| `/api/admin/users/{id}` | PUT | Update user (GUARDED) |

## Test Credentials
- Email: `owner@bigmannentertainment.com`
- Password: `Test1234!`
- Protected User ID: `0659dd6d-e447-4022-a05a-f775b1509572`
- Known Label ID: `BM-LBL-9D0377FB`

## Project Health
- **Mocked**: Revenue Tracking (Pending real API integration)
- **All other features**: Real MongoDB-backed implementations (including DNS Health Checker using real dnspython)
