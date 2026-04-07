# Big Mann Entertainment — Social Media Management & Creator Tools Platform
## Product Requirements Document (PRD)

### Owner & Protection
- **Protected Owner**: John LeGerron Spivey
- **Protected Business**: Big Mann Entertainment
- **User ID**: 0659dd6d-e447-4022-a05a-f775b1509572
- Immutable Ownership Guard active — cannot be bypassed or altered.

---

## Implemented Features

### Core Platform
- [x] Full-stack app: React frontend + FastAPI backend + MongoDB
- [x] User authentication (JWT-based login/register)
- [x] Admin roles and protected routes
- [x] Unified Label Network (ULN) with full label management

### ULN Notification System (Verified)
- In-app notifications for Governance, Disputes, Members, etc.

### Immutable Ownership & Percentage Protections (Verified)
- `master_licensing` enforced at 100%
- `default_royalty_share` enforced at 100%
- Ownership Guard protects John LeGerron Spivey / Big Mann Entertainment

### ULN Components Refactoring (Verified)
- Phase A/B/C UI components fully refactored

### DNS Health Checker (Verified)
- DNS lookup and health monitoring via dnspython

### Automated CVE Monitoring Dashboard (Verified)
- Real-time CVE monitoring via NVD public API

### Catalog Bulk Import — CSV Upload (Verified)
- Drag-and-drop CSV upload for catalog migration
- Duplication detection (ISRC/UPC)
- Template download
- Backend: `/app/backend/services/catalog_import_service.py`
- Frontend: `/app/frontend/src/pages/CatalogImportPage.jsx`

### Mandatory GS1 & Business Identifiers (Verified — Mar 29, 2026)
- **GS1 Identifiers**: GTIN (8/12/13/14), GLN (13), GS1 Company Prefix (7-11), ISRC (ISO 3901), UPC (12)
- **Business Identifiers**: EIN, DUNS, Business Registration Number
- **Validation**: Full GS1 Modulo-10 check-digit verification + format checks
- **Enforcement**: Mandatory at all touchpoints (label profile, catalog assets, distributions)
- **Protection**: John LeGerron Spivey / Big Mann Entertainment identifiers pre-populated & immutable
- **Compliance API**: Check whether a label has all mandatory identifiers
- Backend: `/app/backend/utils/gs1_validators.py`, `/app/backend/api/gs1_business_identifiers_endpoints.py`
- Frontend: `/app/frontend/src/pages/BusinessIdentifiersPage.jsx`

### Quick Actions Panel for GS1 Hub (Verified — Apr 7, 2026)
- 8 quick-action cards: Create Product, Generate Barcode, License All Platforms, Compliance Check, Business Identifiers, CSV Catalog Import, Generate Comprehensive Licenses, Statutory Rates
- Real-time badge counts from `/api/gs1/quick-actions/summary`
- Tab switching, API actions (License All, Generate Comprehensive), and page navigation
- Success/error result banners with auto-dismiss
- Backend: `/app/backend/api/gs1_endpoints.py` (quick-actions/summary)
- Frontend: `/app/frontend/src/pages/GS1LicensingHub.jsx` (QuickActionsPanel component)

### Governance Dashboard Widget on Overview Tab (Verified — Apr 7, 2026)
- Aggregated governance rules & disputes widget on GS1 Hub Overview tab
- Stats: Active Rules, Total Rules, Open Disputes, Resolved/Closed
- Rules by Type badges, Disputes by Priority breakdown, Dispute Status chips
- Recent Disputes list (last 5) with priority dots, titles, types, label IDs, status badges
- Open count badge when active disputes exist
- Backend: `/app/backend/api/gs1_endpoints.py` (governance-overview endpoint)
- Frontend: `/app/frontend/src/pages/GS1LicensingHub.jsx` (GovernanceWidget component)

### Governance Widget Drill-Down (Verified — Apr 7, 2026)
- Interactive drill-down from Governance widget to individual disputes
- **DisputeDetailModal**: Shows title, status, priority, label name, dispute ID, description, activity timeline, and response form for active disputes
- **DisputeListModal**: Paginated list of all disputes across labels with status/priority filters; each row clickable for detail
- Clickable elements: "open" badge, "View All" button, stat cards, priority rows, status chips, recent dispute rows
- Backend: `GET /api/gs1/disputes` (list with filters), `GET /api/gs1/disputes/{dispute_id}` (detail), `POST /api/gs1/disputes/{dispute_id}/respond` (respond)
- Frontend: `/app/frontend/src/pages/GS1LicensingHub.jsx` (DisputeDetailModal, DisputeListModal components)

---

## API Endpoints

### GS1 Business Identifiers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gs1-identifiers/protected-owner` | Get immutable protected owner identifiers |
| POST | `/api/gs1-identifiers/validate` | Validate a single GS1/business identifier |
| GET | `/api/gs1-identifiers/labels/{label_id}` | Get label business identifiers |
| PUT | `/api/gs1-identifiers/labels/{label_id}` | Create/update label business identifiers |
| GET | `/api/gs1-identifiers/labels/{label_id}/compliance` | Compliance check for mandatory identifiers |

### GS1 Hub & Governance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gs1/quick-actions/summary` | Quick actions panel badge counts |
| GET | `/api/gs1/governance-overview` | Aggregated governance & disputes summary |
| GET | `/api/gs1/disputes` | List all disputes (status, priority, page, page_size params) |
| GET | `/api/gs1/disputes/{dispute_id}` | Single dispute detail with label name |
| POST | `/api/gs1/disputes/{dispute_id}/respond` | Add response/status change to dispute |

---

## Upcoming Tasks
- (P0) Revenue Tracking: Connect mocked revenue feature to real data sources
- (P1) "Register New Target" for in-app DNS Health Checker to monitor bigmannentertainment.com

## Future/Backlog
- Additional dashboard widgets or analytics views
- Further GS1 Hub enhancements
- Platform-wide notification preferences/settings
- Email/push notifications for dispute status changes

## 3rd Party Integrations
- NVD (National Vulnerability Database) — Public REST API (no keys)
- Facebook/Instagram/Threads URL Scraping — Public scraping + manual fallback (no keys)
- DNS Resolution — dnspython (no keys)

## Architecture
```
/app
├── backend/
│   ├── api/
│   │   ├── gs1_business_identifiers_endpoints.py
│   │   ├── uln_catalog_distribution_endpoints.py
│   │   ├── uln_governance_disputes_endpoints.py
│   │   ├── gs1_endpoints.py
│   │   ├── cve_monitor_endpoints.py
│   │   └── ...
│   ├── services/
│   │   ├── catalog_import_service.py
│   │   ├── uln_governance_disputes_service.py
│   │   └── ...
│   ├── utils/
│   │   ├── gs1_validators.py
│   │   ├── ownership_guard.py
│   │   └── ...
│   ├── router_setup.py
│   ├── startup.py
│   └── server.py
├── frontend/src/
│   ├── pages/
│   │   ├── BusinessIdentifiersPage.jsx
│   │   ├── CatalogImportPage.jsx
│   │   ├── GS1LicensingHub.jsx
│   │   └── CVEMonitorDashboard.jsx
│   ├── uln/LabelCatalog.js
│   ├── components/layout/NavigationBar.jsx
│   └── App.js
```
