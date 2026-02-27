# Big Mann Entertainment - CVE Management Platform PRD

## Original Problem Statement
Build a comprehensive enterprise CVE management platform with:
1. **Core CVE Brain**: Central vulnerability database with full lifecycle tracking
2. **SBOM Generation**: Track every dependency in the stack
3. **CI/CD Security Gates**: Dependency, container, and IaC scanning
4. **Automated Remediation**: GitHub API integration for auto-PRs, AWS Inspector/Security Hub
5. **Governance Dashboards**: Rich charts, analytics, trends, SLA tracking
6. **Notifications & Reporting**: Email/UI alerts, SLA monitoring, CSV/PDF exports, weekly digests

Additionally, an infrastructure automation pipeline for CVE remediation using Terraform, AWS Lambda, and GitHub Actions.

## Architecture
- **Frontend**: React (CRA) with Tailwind CSS, Lucide React icons, Recharts
- **Backend**: FastAPI (Python) with Motor (async MongoDB driver)
- **Database**: MongoDB
- **Security Tools**: Trivy, Grype, Syft, Checkov
- **AWS**: boto3 (Lambda, S3, CloudWatch, Inspector, SES, Rekognition)
- **Charts**: Recharts (frontend), Matplotlib (PDF charts)
- **IaC**: Terraform + AWS CDK (TypeScript)
- **PDF**: fpdf2 + matplotlib

## Backend Directory Structure (Updated Feb 27, 2026)

```
/app/backend/
├── server.py            # Main app entry + SLA WebSocket endpoint
├── router_setup.py      # External router registration
├── config/              # database.py, settings.py, platforms.py
├── models/              # core.py, agency.py
├── auth/                # service.py
├── routes/              # 11 route modules
├── services/            # 5 service modules
├── tests/               # 33+ test files
├── sla_ws_manager.py    # NEW: SLA WebSocket broadcast manager
├── ticketing_service.py # NEW: Jira/ServiceNow integration
├── ticketing_endpoints.py # NEW: Ticketing API endpoints
├── tenant_service.py    # NEW: Multi-tenant management
├── tenant_endpoints.py  # NEW: Tenant API endpoints
├── cve_reporting_service.py # ENHANCED: Matplotlib chart embedding
└── ...existing modules
```

## What's Been Implemented

### Phase 1-6: Core CVE Platform (COMPLETE)
### Enhanced SLA Tracking Phase 1 & 2 (COMPLETE)
### Advanced Reporting & Analytics (COMPLETE)
### Infrastructure Automation (COMPLETE)
### PDF Export & Dashboard Enhancements (COMPLETE - Feb 20, 2026)
### Security Audit & Dependency Upgrades (COMPLETE - Feb 2026)
### Backend Deep Refactoring (COMPLETE - Feb 27, 2026)
### Frontend CVE Dashboard Refactoring Phase 1 & 2 (COMPLETE - Feb 28, 2026)
### React.lazy() Code Splitting (COMPLETE - Feb 28, 2026)
### Route-Level Code Splitting (COMPLETE - Feb 28, 2026)
### ChunkErrorBoundary (COMPLETE - Feb 28, 2026)

### P2 Backlog Features (COMPLETE - Feb 27, 2026)

#### 1. Real-time WebSocket SLA Notifications
- Created `sla_ws_manager.py` — manages WS connections, broadcasts SLA events
- WebSocket endpoint at `/api/ws/sla` with ping/pong keepalive
- Broadcasts: `escalation_run`, `sla_breach`, `sla_warning` events
- Hooked into `run_escalations()` flow for automatic broadcast
- Frontend: `useSLAWebSocket` hook with auto-reconnect (exponential backoff)
- Frontend: `SLANotificationBanner` component with live connection status, collapsible alerts
- Integrated into CVEManagementDashboard header area

#### 2. External Ticketing Integration (Jira & ServiceNow)
- Created `ticketing_service.py` — configuration, ticket CRUD, sync, bulk create
- Supports Jira and ServiceNow providers with simulation mode when no credentials
- API endpoints: config, test-connection, create/list/sync tickets, bulk create, stats
- Frontend: `TicketingTab.jsx` with config panel, stats grid, ticket list, bulk actions
- Added as lazy-loaded tab in CVE Management Dashboard
- **NOTE**: Currently in SIMULATION MODE — real API integration requires credentials

#### 3. Multi-Tenant Support
- Created `tenant_service.py` — organization CRUD, plan limits, user assignment
- Plans: Free (5 users), Pro (25 users), Enterprise (unlimited)
- Seed default tenant assigns all existing users
- API endpoints: CRUD, stats, user assignment, seed
- Frontend: `TenantManagement.jsx` page with org cards, detail panel, user list
- Route: `/tenant-management` with nav link
- Foundation for per-tenant data scoping (to be progressively applied)

#### 4. Advanced PDF with Embedded Charts
- Added `_render_severity_chart()` — matplotlib horizontal bar chart
- Added `_render_risk_gauge()` — polar projection gauge with needle
- Added `_render_trend_chart()` — 7-day CVE trend area chart
- All 3 charts embedded in executive PDF via fpdf2 `image()` method
- PDF size: ~47KB (vs ~5KB text-only), 3 embedded PNG images verified

## Frontend Directory Structure (Updated Feb 27, 2026)

```
/app/frontend/src/
├── CVEManagementDashboard.jsx  # Updated: SLA banner + Ticketing tab
├── TenantManagement.jsx        # NEW: Multi-tenant admin page
├── cve/
│   ├── SLANotificationBanner.jsx # NEW: Real-time SLA alert banner
│   ├── TicketingTab.jsx          # NEW: Jira/ServiceNow ticketing UI
│   ├── hooks/
│   │   └── useSLAWebSocket.js    # NEW: WebSocket hook with auto-reconnect
│   ├── sla/                      # Existing SLA tracker views
│   ├── infra/                    # Existing infrastructure views
│   ├── governance/               # Existing governance views
│   ├── remediation/              # Existing remediation views
│   ├── reporting/                # Existing reporting views
│   └── components/               # Shared UI components
├── components/
│   └── ChunkErrorBoundary.jsx    # Error boundary for lazy loading
└── App.js                        # Updated: tenant route + nav link
```

## Prioritized Backlog

### P0 - All Core Features (COMPLETE)
### P1 - P2 Backlog (COMPLETE)

### P2 - Future Tasks
- Per-tenant data scoping (apply tenant_id filters to all queries)
- Real Jira/ServiceNow API integration (when credentials provided)
- Tenant billing and usage tracking
- Role-based tenant admin (tenant admin vs super admin)
- WebSocket SLA notification preferences per user
- PDF custom report builder with drag-and-drop chart selection

## Test Credentials
- Test user: cveadmin@test.com / Test1234!

## Test Reports
- iteration_33.json - PDF Export + Dashboard (26/26 passed)
- iteration_34.json - Initial Refactoring Regression (22/22 passed)
- iteration_35.json - Deep Refactoring Regression (33/33 passed)
- iteration_36.json - Frontend Refactoring Phase 1 (100% pass)
- iteration_37.json - Frontend Refactoring Phase 2 (100% pass)
- iteration_38.json - React.lazy() code splitting (100% pass)
- iteration_39.json - Route-level code splitting (100% pass)
- iteration_40.json - ChunkErrorBoundary (100% pass)
- iteration_41.json - P2 Backlog Features (86% backend, 100% frontend - 3 timeouts were network-related)
