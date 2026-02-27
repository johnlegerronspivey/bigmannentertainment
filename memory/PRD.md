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
- **Security Tools**: Trivy v0.58.2, Grype v0.108.0, Syft v1.42.0, Checkov 3.2.501
- **Background Jobs**: APScheduler (for existing security monitoring)
- **Email**: Resend (for CVE alerts + Phase 5 notifications + SLA digest)
- **GitHub Integration**: PyGitHub for issue/PR creation + workflow runs
- **AWS**: boto3 for Lambda, S3, CloudWatch, Inspector/Security Hub
- **Charts**: Recharts (PieChart, BarChart, AreaChart, LineChart)
- **IaC**: Terraform (multi-environment: dev, staging, prod) + AWS CDK (TypeScript)
- **CI/CD**: GitHub Actions (Lambda artifact build + upload)
- **PDF Generation**: fpdf2 (for report exports)

## Backend Directory Structure (Refactored Feb 27, 2026)

```
/app/backend/
├── server.py                      # Main FastAPI app (~6595 lines, reduced from 8141)
├── router_setup.py                # Central router registration
├── config/                        # Extracted configuration
│   ├── database.py                # MongoDB connection (db, client)
│   ├── settings.py                # All env vars & constants
│   └── platforms.py               # 119 distribution platform configs
├── models/                        # Extracted Pydantic models
│   ├── core.py                    # User, Token, Media, Purchase, NFT, etc.
│   └── agency.py                  # Agency onboarding models
├── auth/                          # Extracted authentication
│   └── service.py                 # verify_password, create_token, get_current_user
├── routes/                        # Route packages (for future endpoints)
├── services/                      # Service packages (for future services)
├── tests/                         # 31 test files
├── providers/                     # Social media providers
├── lambda/                        # AWS Lambda functions
├── *_endpoints.py                 # API endpoint modules
├── *_service.py                   # Business logic services
└── *_models.py                    # Domain-specific models
```

## Key Files

### Backend Core
- `/app/backend/server.py` - Main FastAPI app entry point
- `/app/backend/router_setup.py` - Central router registration
- `/app/backend/config/database.py` - MongoDB connection
- `/app/backend/config/settings.py` - Environment variables
- `/app/backend/config/platforms.py` - 119 distribution platform configs
- `/app/backend/models/core.py` - Core Pydantic models
- `/app/backend/models/agency.py` - Agency models
- `/app/backend/auth/service.py` - Auth functions

### CVE Management
- `/app/backend/cve_management_service.py` - Core CVE brain service (Phase 1)
- `/app/backend/cve_management_endpoints.py` - CVE API endpoints (prefix: /api/cve)
- `/app/backend/scanner_service.py` - Multi-scanner orchestration (Phase 2)
- `/app/backend/scanner_endpoints.py` - Scanner API endpoints
- `/app/backend/remediation_service.py` - Remediation & GitHub/AWS integration (Phase 3)
- `/app/backend/governance_service.py` - Governance analytics service (Phase 4)
- `/app/backend/notification_service.py` - Notification & reporting service (Phase 5)
- `/app/backend/rbac_service.py` - RBAC service (Phase 6)
- `/app/backend/sla_tracker_service.py` - SLA Tracker service
- `/app/backend/cve_reporting_service.py` - Advanced Reporting service
- `/app/backend/iac_service.py` - Infrastructure Automation service

### Frontend (Refactored)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Thin orchestrator with responsive tabs
- `/app/frontend/src/cve/shared.js` - Shared constants, API URLs, utility components
- `/app/frontend/src/cve/OverviewTab.jsx` - Enhanced dashboard with trend indicators
- `/app/frontend/src/cve/CVEDatabaseTab.jsx` - CVE listing with debounced search
- `/app/frontend/src/cve/SLATrackerTab.jsx` - SLA Tracker with 6 sub-views
- `/app/frontend/src/cve/ReportingTab.jsx` - Advanced Reporting with CSV + PDF export
- `/app/frontend/src/cve/InfraTab.jsx` - Infrastructure Automation with LIVE data

### Infrastructure as Code
- `/app/infra-terraform/` - Production-grade Terraform repository (47+ files)
- `/app/infra-cdk/` - CDK TypeScript project

## What's Been Implemented

### Phase 1-6: Core CVE Platform (COMPLETE)
- CVE lifecycle management, SBOM generation, Multi-scanner integration
- CI/CD pipeline generation, Policy-as-code rules engine
- Automated remediation via GitHub, AWS Inspector/Security Hub
- Governance dashboards, Notifications, User Management & RBAC

### Enhanced SLA Tracking Phase 1 & 2 (COMPLETE)
### Advanced Reporting & Analytics (COMPLETE)
### Infrastructure Automation (COMPLETE)
### PDF Export & Dashboard Enhancements (COMPLETE - Feb 20, 2026)
### Security Audit & Dependency Upgrades (COMPLETE - Feb 2026)
### Backend Codebase Refactoring (COMPLETE - Feb 27, 2026)
- Extracted `config/` (database, settings, platforms) from server.py
- Extracted `models/` (core, agency) from server.py
- Extracted `auth/` (service) from server.py
- Updated 17 dependent files to import from new module locations
- Reduced server.py from 8141 to 6595 lines (-19%)
- Created ARCHITECTURE.md documentation
- All 22 regression tests passed (100%)

## Prioritized Backlog

### P0 - All Core Features (COMPLETE)
All phases 1-6 complete with Enhanced SLA, Reporting, Live IaC, Terraform, CDK, PDF Export.

### P1 - Future Tasks
- Real-time WebSocket notifications for SLA breaches
- Integration with external ticketing systems (Jira, ServiceNow)
- Multi-tenant support
- Advanced PDF with embedded charts/graphs
- Further server.py decomposition (extract remaining inline endpoints)

## Test Credentials
- Test user: cveadmin@test.com / Test1234!

## Test Reports
- iteration_33.json - PDF Export + Dashboard Enhancements (26/26 tests passed)
- iteration_34.json - Backend Refactoring Regression (22/22 tests passed)
