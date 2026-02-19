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
- **Email**: Resend (for CVE alerts + Phase 5 notifications + SLA digest)
- **GitHub Integration**: PyGitHub for issue/PR creation + workflow runs
- **AWS**: boto3 for Lambda, S3, CloudWatch, Inspector/Security Hub
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
- `/app/backend/sla_tracker_service.py` - SLA Tracker service (Phase 1 + Phase 2)
- `/app/backend/sla_tracker_endpoints.py` - SLA API endpoints (prefix: /api/cve/sla)
- `/app/backend/cve_reporting_service.py` - Advanced Reporting service
- `/app/backend/cve_reporting_endpoints.py` - Reporting API endpoints (prefix: /api/cve/reporting)
- `/app/backend/iac_service.py` - Infrastructure Automation service (LIVE AWS/GitHub integration)
- `/app/backend/iac_endpoints.py` - IaC API endpoints (prefix: /api/cve/iac)

### Frontend (Refactored)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Thin orchestrator (149 lines)
- `/app/frontend/src/cve/shared.js` - Shared constants, API URLs, utility components
- `/app/frontend/src/cve/OverviewTab.jsx` - Dashboard overview
- `/app/frontend/src/cve/CVEDatabaseTab.jsx` - CVE listing, filtering, creation
- `/app/frontend/src/cve/AssignOwnerModal.jsx` - Owner assignment modal
- `/app/frontend/src/cve/ScannersTab.jsx` - Security scanner tools
- `/app/frontend/src/cve/RemediationTab.jsx` - GitHub issues/PRs, AWS findings
- `/app/frontend/src/cve/GovernanceTab.jsx` - Charts, risk gauge, trends
- `/app/frontend/src/cve/NotificationsTab.jsx` - Notifications, preferences
- `/app/frontend/src/cve/ServicesTab.jsx` - Service registry + SBOMTab
- `/app/frontend/src/cve/CICDTab.jsx` - Pipeline generator
- `/app/frontend/src/cve/PolicyEngineTab.jsx` - Policy-as-code rules engine
- `/app/frontend/src/cve/PoliciesTab.jsx` - SLA policies config + AuditTrailTab
- `/app/frontend/src/cve/UserManagementTab.jsx` - User management with RBAC
- `/app/frontend/src/cve/SLATrackerTab.jsx` - SLA Tracker with 6 sub-views
- `/app/frontend/src/cve/ReportingTab.jsx` - Advanced Reporting
- `/app/frontend/src/cve/InfraTab.jsx` - Infrastructure Automation with LIVE data

## What's Been Implemented

### Phase 1-5: Core CVE Platform (COMPLETE)
- CVE lifecycle management (detect, triage, fix, verify)
- SBOM generation, Multi-scanner integration, CI/CD pipeline generation
- Policy-as-code rules engine, Automated remediation via GitHub
- AWS Inspector/Security Hub integration, Governance dashboards with charts
- Notifications with email alerts, CSV export

### Phase 6: User Management & RBAC (COMPLETE)
- Role-based access control (Admin, Manager, Analyst)

### Enhanced SLA Tracking Phase 1 & 2 (COMPLETE)
- SLA Dashboard, At-Risk CVEs, Configurable escalation rules
- Auto-Escalation Scheduler, Proactive Email Notifications
- Escalation Workflow Management, SLA Digest Email

### Advanced Reporting & Analytics (COMPLETE)
- Executive Summary, Trends, Team Performance, Scanner Effectiveness, Export

### Infrastructure Automation - LOCAL (COMPLETE - Feb 18, 2026)
- Terraform configs, Lambda function, GitHub Actions CI/CD workflow
- IaC Management Tab with overview cards, environment selector, viewers, deployment commands

### Infrastructure Automation - LIVE DATA (COMPLETE - Feb 18, 2026)
- **AWS Lambda Live**: Fetches real function configs + CloudWatch metrics (invocations, errors, duration, throttles) via boto3
- **GitHub Actions Live**: Fetches real workflow runs with status/conclusion/branch from PyGitHub
- **Terraform State Live**: Reads Terraform state from S3 backend (resources, versions)
- **Connection Status**: Real-time LIVE/OFFLINE badges for Lambda, S3, GitHub
- **Non-blocking I/O**: All boto3/PyGitHub calls wrapped in `asyncio.to_thread()` to prevent event loop blocking
- **4 New API Endpoints**: /live-status, /lambda/live, /github/runs, /terraform/state
- **Frontend**: LiveLambdaPanel (function cards with metrics), GitHubRunsPanel (run history), TerraformStatePanel (resource list), Connection status bar
- Test report: iteration_30.json (30/30 backend tests, 100% frontend verification)
- Live data verified: 9 Lambda functions, 15 GitHub workflow runs, S3 bucket connected

### Terraform Modules Repository (COMPLETE - Feb 19, 2026)
- **44 Terraform files** created under `/app/infra-terraform/` with production-grade modular architecture
- **11 Modules**: cognito, s3-cloudfront, dynamodb, kinesis, lambda, eventbridge, sns, secrets-manager, qldb, media-convert, stepfunctions
- **30 total resources** across all modules
- **2 Environment configs**: prod (high-capacity) and staging (lower allocation)
- **Top-level files**: provider.tf, versions.tf, variables.tf, outputs.tf, README.md
- **New API Endpoint**: GET /api/cve/iac/terraform/modules — scans and returns module metadata with file contents
- **Frontend**: TerraformModuleCard (expandable with resources/variables/outputs/code), TerraformModulesPanel, TerraformEnvsPanel, TF Modules stat card
- Test report: iteration_31.json (15/15 backend tests, 100% frontend verification)

### CVE Vulnerability Remediation (COMPLETE)
- All Python/Node.js CVEs resolved

## Prioritized Backlog

### P0 - All Core Features (COMPLETE)
All phases 1-6 complete with Enhanced SLA Tracking, Advanced Reporting, and Live IaC Integration.

### P1 - Future Tasks
- PDF export for reports (in addition to CSV)
- Real-time WebSocket notifications for SLA breaches
- Integration with external ticketing systems (Jira, ServiceNow)
- Multi-tenant support

## Test Credentials
- Test user: cveadmin@test.com / Test1234!

## Test Reports
- iteration_3.json - Advanced Reporting & Analytics
- iteration_28.json - Enhanced SLA Tracking Phase 2
- iteration_29.json - IaC Integration (Local)
- iteration_30.json - IaC Live AWS/GitHub Integration (30/30 tests passed)
