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
- `/app/backend/cve_reporting_service.py` - Advanced Reporting service (CSV + PDF export + dashboard trends)
- `/app/backend/cve_reporting_endpoints.py` - Reporting API endpoints (prefix: /api/cve/reporting)
- `/app/backend/iac_service.py` - Infrastructure Automation service (LIVE AWS/GitHub + CDK/TF parsing)
- `/app/backend/iac_endpoints.py` - IaC API endpoints (prefix: /api/cve/iac)

### Frontend (Refactored)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Thin orchestrator with responsive tabs
- `/app/frontend/src/cve/shared.js` - Shared constants, API URLs, utility components
- `/app/frontend/src/cve/OverviewTab.jsx` - Enhanced dashboard with trend indicators, sparkline
- `/app/frontend/src/cve/CVEDatabaseTab.jsx` - CVE listing with debounced search, active filter chips
- `/app/frontend/src/cve/AssignOwnerModal.jsx` - Owner assignment modal
- `/app/frontend/src/cve/ScannersTab.jsx` - Security scanner tools
- `/app/frontend/src/cve/RemediationTab.jsx` - GitHub issues/PRs, AWS findings
- `/app/frontend/src/cve/GovernanceTab.jsx` - Charts, risk gauge, trends (with skeleton loading)
- `/app/frontend/src/cve/NotificationsTab.jsx` - Notifications, preferences
- `/app/frontend/src/cve/ServicesTab.jsx` - Service registry + SBOMTab
- `/app/frontend/src/cve/CICDTab.jsx` - Pipeline generator
- `/app/frontend/src/cve/PolicyEngineTab.jsx` - Policy-as-code rules engine
- `/app/frontend/src/cve/PoliciesTab.jsx` - SLA policies config + AuditTrailTab
- `/app/frontend/src/cve/UserManagementTab.jsx` - User management with RBAC
- `/app/frontend/src/cve/SLATrackerTab.jsx` - SLA Tracker with 6 sub-views
- `/app/frontend/src/cve/ReportingTab.jsx` - Advanced Reporting with CSV + PDF export
- `/app/frontend/src/cve/InfraTab.jsx` - Infrastructure Automation with LIVE data + Terraform + CDK

### Infrastructure as Code
- `/app/infra-terraform/` - Production-grade Terraform repository (47+ files)
- `/app/infra-terraform/modules/` - 12 reusable modules
- `/app/infra-cdk/` - CDK TypeScript project for Programmatic DOOH platform
- `/app/infra-cdk/lib/constructs/` - 8 constructs

## What's Been Implemented

### Phase 1-6: Core CVE Platform (COMPLETE)
- CVE lifecycle management, SBOM generation, Multi-scanner integration
- CI/CD pipeline generation, Policy-as-code rules engine
- Automated remediation via GitHub, AWS Inspector/Security Hub
- Governance dashboards, Notifications, User Management & RBAC

### Enhanced SLA Tracking Phase 1 & 2 (COMPLETE)
- SLA Dashboard, At-Risk CVEs, Configurable escalation rules
- Auto-Escalation Scheduler, Proactive Email Notifications

### Advanced Reporting & Analytics (COMPLETE)
- Executive Summary, Trends, Team Performance, Scanner Effectiveness, Export

### Infrastructure Automation (COMPLETE)
- Terraform configs, Lambda function, GitHub Actions CI/CD
- Live AWS/GitHub data integration
- Terraform Modules Repository (12 modules)
- CDK TypeScript Project + VPC Module

### PDF Export & Dashboard Enhancements (COMPLETE - Feb 20, 2026)
- **PDF Export**: Professional formatted PDF reports (Executive, CVE Database, Team Performance)
- **Dashboard Trends**: 7-day mini sparkline, week-over-week delta indicators
- **Search Improvements**: Debounced search (350ms), active filter chips with clear all
- **Loading Skeletons**: Animated skeleton states in Overview, Governance tabs
- **Responsive Tabs**: Better tab navigation on mobile/tablet viewports
- **New Backend Endpoints**: `/export/executive-pdf`, `/export/cves-pdf`, `/export/team-pdf`, `/dashboard-trends`
- Test report: iteration_33.json (26/26 backend tests, 100% frontend verification)

## Prioritized Backlog

### P0 - All Core Features (COMPLETE)
All phases 1-6 complete with Enhanced SLA, Reporting, Live IaC, Terraform, CDK, PDF Export.

### P1 - Future Tasks
- Real-time WebSocket notifications for SLA breaches
- Integration with external ticketing systems (Jira, ServiceNow)
- Multi-tenant support
- Advanced PDF with embedded charts/graphs

## Test Credentials
- Test user: cveadmin@test.com / Test1234!

## Test Reports
- iteration_3.json - Advanced Reporting & Analytics
- iteration_28.json - Enhanced SLA Tracking Phase 2
- iteration_29.json - IaC Integration (Local)
- iteration_30.json - IaC Live AWS/GitHub Integration (30/30 tests passed)
- iteration_31.json - Terraform Modules Repository (15/15 tests passed)
- iteration_32.json - CDK Constructs + VPC Module (25/25 tests passed)
- iteration_33.json - PDF Export + Dashboard Enhancements (26/26 tests passed)
