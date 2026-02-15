# Big Mann Entertainment - CVE Management Platform PRD

## Original Problem Statement
Build a comprehensive enterprise CVE management platform with:
1. **Core CVE Brain**: Central vulnerability database with full lifecycle tracking
2. **SBOM Generation**: Track every dependency in the stack
3. **CI/CD Security Gates**: Dependency, container, and IaC scanning
4. **Automated Remediation**: GitHub API integration for auto-PRs, AWS Inspector/Security Hub
5. **Governance Dashboards**: Rich charts, analytics, trends, SLA tracking
6. **Notifications & Reporting**: Email/UI alerts, SLA monitoring, CSV exports, weekly digests

Additionally, an infrastructure automation pipeline for CVE remediation using Terraform, AWS Lambda, and GitHub Actions.

## Architecture
- **Frontend**: React (CRA) with Tailwind CSS, Lucide React icons, Recharts
- **Backend**: FastAPI (Python) with Motor (async MongoDB driver)
- **Database**: MongoDB
- **Security Tools**: Trivy v0.58.2, Grype v0.108.0, Syft v1.42.0, Checkov 3.2.501
- **Background Jobs**: APScheduler (for existing security monitoring)
- **Email**: Resend (for CVE alerts + Phase 5 notifications)
- **GitHub Integration**: PyGithub for issue/PR creation
- **AWS**: boto3 for Inspector/Security Hub
- **Charts**: Recharts (PieChart, BarChart, AreaChart, LineChart)
- **IaC**: Terraform (multi-environment: dev, staging, prod)
- **CI/CD**: GitHub Actions (Lambda artifact build + upload)

## Key Files

### Backend
- `/app/backend/cve_management_service.py` - Core CVE brain service (Phase 1)
- `/app/backend/cve_management_endpoints.py` - CVE API endpoints (prefix: /api/cve)
- `/app/backend/scanner_service.py` - Multi-scanner orchestration (Phase 2)
- `/app/backend/scanner_endpoints.py` - Scanner API endpoints (prefix: /api/cve/scanners)
- `/app/backend/remediation_service.py` - Remediation & GitHub/AWS integration (Phase 3)
- `/app/backend/remediation_endpoints.py` - Remediation API endpoints (prefix: /api/cve/remediation)
- `/app/backend/governance_service.py` - Governance analytics service (Phase 4)
- `/app/backend/governance_endpoints.py` - Governance API endpoints (prefix: /api/cve/governance)
- `/app/backend/notification_service.py` - Notification & reporting service (Phase 5)
- `/app/backend/notification_endpoints.py` - Notification API endpoints
- `/app/backend/rbac_service.py` - RBAC service (Phase 6)
- `/app/backend/rbac_endpoints.py` - RBAC API endpoints

### Frontend (Refactored)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Thin orchestrator (149 lines), imports all tab components
- `/app/frontend/src/cve/shared.js` - Shared constants, API URLs, utility components (StatCard, SeverityBadge, StatusBadge, fetcher)
- `/app/frontend/src/cve/OverviewTab.jsx` - Dashboard overview with stats and severity breakdown
- `/app/frontend/src/cve/CVEDatabaseTab.jsx` - CVE listing, filtering, creation, status transitions
- `/app/frontend/src/cve/AssignOwnerModal.jsx` - Owner assignment modal (reused across tabs)
- `/app/frontend/src/cve/ScannersTab.jsx` - Security scanner tools and scan history
- `/app/frontend/src/cve/RemediationTab.jsx` - GitHub issues/PRs, AWS findings, bulk operations
- `/app/frontend/src/cve/GovernanceTab.jsx` - Charts, risk gauge, trends, SLA compliance, ownership
- `/app/frontend/src/cve/NotificationsTab.jsx` - Notifications, preferences, SLA checks, digests
- `/app/frontend/src/cve/ServicesTab.jsx` - Service registry + SBOMTab
- `/app/frontend/src/cve/CICDTab.jsx` - Pipeline generator with YAML preview
- `/app/frontend/src/cve/PolicyEngineTab.jsx` - Policy-as-code rules engine
- `/app/frontend/src/cve/PoliciesTab.jsx` - SLA policies config + AuditTrailTab
- `/app/frontend/src/cve/UserManagementTab.jsx` - User management with RBAC

## What's Been Implemented

### Phase 1-5: Core CVE Platform (COMPLETE)
- CVE lifecycle management (detect, triage, fix, verify)
- SBOM generation
- Multi-scanner integration (Trivy, Grype, Syft, Checkov)
- CI/CD pipeline generation
- Policy-as-code rules engine
- Automated remediation via GitHub
- AWS Inspector/Security Hub integration
- Governance dashboards with charts
- Notifications with email alerts
- CSV export for CVEs and governance data

### Phase 6: User Management & RBAC (COMPLETE)
- Role-based access control (Admin, Manager, Analyst)
- User invitation and management
- Permission-gated UI elements

### Infrastructure Automation (COMPLETE - Pending User Testing)
- Terraform configurations for multi-environment deployment
- Python Lambda function for CVE remediation
- GitHub Actions workflow for CI/CD
- Status: Code ready, awaiting user testing in their own pipeline

### Frontend Refactoring (COMPLETE - Feb 15, 2026)
- Refactored monolithic CVEManagementDashboard.jsx from 2810 lines to 149 lines
- Extracted 13 component files into `/app/frontend/src/cve/` directory
- All 13 tabs verified working with 0 regressions (test report: iteration_25.json)

## Prioritized Backlog

### P1 - Enhanced SLA Tracking
- Proactive notifications and escalations for SLA breaches
- Escalation chains based on severity and time overdue

## Test Credentials
- Admin: Register via /api/auth/register (enterprise users)
- Test user: cveadmin@test.com / Test1234!
