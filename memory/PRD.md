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

### Live Infrastructure Visualization (COMPLETE - Feb 27, 2026)
- **GitHub Repository Panel**: Live repo info (name, stars, forks, language, size), recent commits (10), branches, open PRs with tabbed UI
- **S3 Artifacts Panel**: Live S3 bucket browser with file listing, size display, storage class badges, prefix-based navigation, and text filter
- **CloudWatch Alarms Panel**: Live alarm monitoring with state indicators (OK/ALARM/INSUFFICIENT_DATA), metric details, thresholds
- **Auto-refresh**: Configurable intervals (Off, 30s, 1m, 5m) with last-updated timestamp
- **Enhanced Connection Status Bar**: Added CloudWatch to live connection badges (Lambda, S3, GitHub, CloudWatch)
- **Enhanced Overview Cards**: Added S3 (object count) and CloudWatch Alarms (state) cards alongside existing Terraform, CDK, Lambda, GitHub, Deployments, TF Modules
- **Backend API additions**: `GET /api/cve/iac/github/repo`, `GET /api/cve/iac/s3/artifacts`, `GET /api/cve/iac/cloudwatch/alarms`
- All data sourced from real AWS and GitHub APIs using user's credentials

### Tenant Data Migration (COMPLETE - Feb 27, 2026)
- **Migration Analysis API**: `GET /api/tenants/migration-analysis` returns per-collection breakdown of total/legacy/migrated documents with available tenants
- **Migration Execution API**: `POST /api/tenants/migrate-data` assigns target tenant_id to all legacy documents across 18 CVE collections + users
- **Auto-indexing**: Creates MongoDB `tenant_id` indexes on all migrated collections for query performance
- **Simplified _tenant_filter**: Removed backward-compatible `$or` logic (legacy doc fallback) from `cve_management_service.py` and `ticketing_service.py` — now strict equality
- **Admin UI Panel**: New "Data Migration" sub-tab under Users & RBAC with summary cards (Total/Legacy/Status), collection breakdown table, and one-click migration with tenant selector
- **Migration result**: 275 legacy documents migrated to Default Organization tenant across 18 collections

## Key Files

### Backend
```
/app/backend/
├── iac_service.py             # MODIFIED: Added get_github_repo_info(), get_s3_artifacts(), get_cloudwatch_alarms()
├── iac_endpoints.py           # MODIFIED: Added /github/repo, /s3/artifacts, /cloudwatch/alarms endpoints
├── tenant_context.py          # FastAPI tenant auth dependencies
├── tenant_service.py          # MODIFIED: Added analyze_migration(), run_data_migration() methods
├── tenant_endpoints.py        # MODIFIED: Added /migration-analysis, /migrate-data endpoints
├── cve_management_service.py  # MODIFIED: Simplified _tenant_filter (strict equality)
├── ticketing_service.py       # MODIFIED: Simplified _tenant_filter (strict equality), real Jira/ServiceNow API
├── sla_tracker_service.py     # per-user prefs, should_notify_user
├── sla_ws_manager.py          # user_id-keyed connections
├── server.py                  # WS endpoint passes user_id
└── models/core.py             # User has tenant_id, tenant_name
```

### Frontend
```
/app/frontend/src/cve/
├── TenantMigrationPanel.jsx   # NEW: Migration analysis, execution, and status panel
├── UserManagementTab.jsx      # MODIFIED: Added sub-tabs (Users & Roles, Data Migration)
├── infra/
│   ├── InfraTab.jsx           # MODIFIED: Added new panels, auto-refresh
│   ├── GitHubRepoPanel.jsx    # NEW: Repo info with commits/branches/PRs tabs
│   ├── S3ArtifactsPanel.jsx   # NEW: S3 bucket browser
│   └── CloudWatchAlarmsPanel.jsx # NEW: Alarms with state indicators
```

## Prioritized Backlog

### P0 - All Core Features (COMPLETE)
### P1 - P2 Backlog (COMPLETE)
### P1 - Data Scoping & Integration (COMPLETE)
### P1 - Live Infrastructure Visualization (COMPLETE)
### P1 - Data Migration for Tenancy (COMPLETE - Feb 27, 2026)

### P2 - Future Tasks
- Full Ticketing Configuration UI (admin frontend for Jira/ServiceNow credentials)
- Tenant billing and usage tracking
- Role-based tenant admin (tenant admin vs super admin)
- PDF custom report builder with drag-and-drop chart selection
- Real-time WebSocket preference-based filtering (broadcast only to matching users)

## Test Credentials
- Test user: cveadmin@test.com / Test1234!
- Tenant: Default Organization (40e6f47e-b021-4605-9e1c-7a0992854f6c)

## Test Reports
- iteration_44.json - Tenant Data Migration (19/19 backend 100%, 100% frontend)
- iteration_43.json - Live Infrastructure Visualization (43/43 backend 100%, 100% frontend)
- iteration_42.json - Per-tenant scoping, Jira/ServiceNow, Per-user WS prefs (19/19 backend, 100% frontend)
- iteration_41.json - P2 Backlog Features (86% backend, 100% frontend)
- iteration_40.json - ChunkErrorBoundary (100% pass)
- iteration_39.json - Route-level code splitting (100% pass)
- iteration_38.json - React.lazy() code splitting (100% pass)
