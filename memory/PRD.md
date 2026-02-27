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
- **HTTP Client**: httpx (for Jira/ServiceNow API calls)

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

### Per-Tenant Data Scoping (COMPLETE - Feb 27, 2026)
- Added `tenant_id` and `tenant_name` fields to User model
- Created `tenant_context.py` with `get_optional_tenant_id` and `get_required_tenant_id` FastAPI dependencies
- CVEManagementService: `_tenant_filter()` uses backward-compatible `$or` to include legacy docs without tenant_id
- Tenant filtering applied to: `get_dashboard`, `list_cves`, `create_cve`, `_count_overdue`
- Ticketing: `list_tickets`, `create_ticket`, `bulk_create_tickets`, `get_stats` all accept `tenant_id`
- Endpoints use `Depends(get_optional_tenant_id)` for seamless auth-based scoping
- New CVEs and tickets get `tenant_id` set from authenticated user

### Live Jira/ServiceNow Integration (COMPLETE - Feb 27, 2026)
- Implemented real Jira REST API v3 calls: create issue (`POST /rest/api/3/issue`), get status
- Implemented real ServiceNow REST API: create incident, get status by number
- Real `test_connection` endpoint: validates Jira auth via `/rest/api/3/myself`, ServiceNow via incident table
- Simulation mode auto-detected when credentials are incomplete
- Graceful fallback to simulation if real API call fails
- httpx used for async HTTP with 30s timeout

### Per-User WebSocket Notification Preferences (COMPLETE - Feb 27, 2026)
- Per-user preference storage with `sla_notif_prefs:{user_id}` key in MongoDB
- New fields: `muted_severities`, `quiet_hours_enabled`, `quiet_hours_start/end`, per-severity `ws` channel toggle
- `should_notify_user()` method checks: muted severities, quiet hours, event type toggles, per-severity channels
- New API endpoint: `GET /api/cve/sla/notification-preferences/check` for real-time notification decision
- WebSocket manager upgraded to user_id-keyed connections
- Frontend: `NotificationPreferencesPanel.jsx` with per-severity channel matrix, quiet hours, mute toggles
- Integrated into SLA Tracker > Notifications sub-view

## Key Files

### Backend
```
/app/backend/
├── tenant_context.py          # NEW: FastAPI tenant auth dependencies
├── cve_management_service.py  # MODIFIED: tenant filtering on all queries
├── cve_management_endpoints.py # MODIFIED: get_optional_tenant_id dependency
├── ticketing_service.py       # MODIFIED: real Jira/ServiceNow API, tenant filtering
├── ticketing_endpoints.py     # MODIFIED: tenant scoping
├── sla_tracker_service.py     # MODIFIED: per-user prefs, should_notify_user
├── sla_tracker_endpoints.py   # MODIFIED: user_id param, /check endpoint
├── sla_ws_manager.py          # MODIFIED: user_id-keyed connections
├── server.py                  # MODIFIED: WS endpoint passes user_id
├── models/core.py             # MODIFIED: User has tenant_id, tenant_name
├── tenant_service.py          # Tenant CRUD operations
└── tenant_endpoints.py        # Tenant API endpoints
```

### Frontend
```
/app/frontend/src/
├── cve/
│   ├── NotificationPreferencesPanel.jsx  # NEW: per-user WS notification prefs UI
│   ├── hooks/useSLAWebSocket.js          # MODIFIED: passes userId to WS
│   ├── sla/NotificationSettingsView.jsx  # MODIFIED: integrates prefs panel
│   ├── TicketingTab.jsx                  # Ticketing config + ticket list
│   └── SLANotificationBanner.jsx         # Real-time SLA alert banner
├── CVEManagementDashboard.jsx            # Main dashboard with all tabs
└── TenantManagement.jsx                  # Tenant admin page
```

## Prioritized Backlog

### P0 - All Core Features (COMPLETE)
### P1 - P2 Backlog (COMPLETE)
### P1 - Data Scoping & Integration (COMPLETE)

### P2 - Future Tasks
- Tenant billing and usage tracking
- Role-based tenant admin (tenant admin vs super admin)
- PDF custom report builder with drag-and-drop chart selection
- Strict tenant isolation (remove backward-compatible legacy doc access)
- Real-time WebSocket preference-based filtering (broadcast only to matching users)

## Test Credentials
- Test user: cveadmin@test.com / Test1234!
- Tenant: Default Organization (40e6f47e-b021-4605-9e1c-7a0992854f6c)

## Test Reports
- iteration_42.json - Per-tenant scoping, Jira/ServiceNow, Per-user WS prefs (19/19 backend, 100% frontend)
- iteration_41.json - P2 Backlog Features (86% backend, 100% frontend)
- iteration_40.json - ChunkErrorBoundary (100% pass)
- iteration_39.json - Route-level code splitting (100% pass)
- iteration_38.json - React.lazy() code splitting (100% pass)
