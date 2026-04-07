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

---

## API Endpoints (GS1 Business Identifiers)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gs1-identifiers/protected-owner` | Get immutable protected owner identifiers |
| POST | `/api/gs1-identifiers/validate` | Validate a single GS1/business identifier |
| GET | `/api/gs1-identifiers/labels/{label_id}` | Get label business identifiers |
| PUT | `/api/gs1-identifiers/labels/{label_id}` | Create/update label business identifiers |
| GET | `/api/gs1-identifiers/labels/{label_id}/compliance` | Compliance check for mandatory identifiers |

---

### Quick Actions Panel for GS1 Hub (Verified — Apr 7, 2026)
- 8 quick-action cards: Create Product, Generate Barcode, License All Platforms, Compliance Check, Business Identifiers, CSV Catalog Import, Generate Comprehensive Licenses, Statutory Rates
- Real-time badge counts from `/api/gs1/quick-actions/summary`
- Tab switching, API actions (License All, Generate Comprehensive), and page navigation
- Success/error result banners with auto-dismiss
- Backend: `/app/backend/api/gs1_endpoints.py` (quick-actions/summary)
- Frontend: `/app/frontend/src/pages/GS1LicensingHub.jsx` (QuickActionsPanel component)

---

## Upcoming Tasks
- (P0) Revenue Tracking: Connect mocked revenue feature to real data sources
- (P2) Governance Dashboard widget on Overview tab (active rules count, open disputes)

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
│   │   ├── gs1_endpoints.py
│   │   ├── cve_monitor_endpoints.py
│   │   └── ...
│   ├── services/
│   │   ├── catalog_import_service.py
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
