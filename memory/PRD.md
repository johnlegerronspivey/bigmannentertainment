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
- **Charts**: Recharts
- **IaC**: Terraform + AWS CDK (TypeScript)
- **PDF**: fpdf2

## Backend Directory Structure (Refactored Feb 27, 2026)

```
/app/backend/
├── server.py            # 375 lines (down from 8,141 - 96% reduction)
├── router_setup.py      # External router registration
├── config/              # database.py, settings.py, platforms.py
├── models/              # core.py (315 lines), agency.py (75 lines)
├── auth/                # service.py (87 lines)
├── routes/              # 11 route modules (4,529 lines total)
├── services/            # 5 service modules (1,639 lines total)
├── tests/               # 33+ test files
├── providers/           # Social media providers
├── lambda/              # AWS Lambda functions
└── *_endpoints.py       # Pre-existing external endpoint modules
```

## What's Been Implemented

### Phase 1-6: Core CVE Platform (COMPLETE)
### Enhanced SLA Tracking Phase 1 & 2 (COMPLETE)
### Advanced Reporting & Analytics (COMPLETE)
### Infrastructure Automation (COMPLETE)
### PDF Export & Dashboard Enhancements (COMPLETE - Feb 20, 2026)
### Security Audit & Dependency Upgrades (COMPLETE - Feb 2026)
### Backend Deep Refactoring (COMPLETE - Feb 27, 2026)
- Phase 1: Extracted config/, models/, auth/ from server.py (-1,500 lines)
- Phase 2: Extracted 97 route handlers into 11 routes/ modules
- Phase 2: Extracted 9 service classes into 5 services/ modules
- Server.py: 8,141 → 375 lines (96% reduction)
- All 55 regression tests passed (33 deep + 22 original)
- 4 import bugs found and fixed by testing agent

### Frontend CVE Dashboard Refactoring (COMPLETE - Feb 28, 2026)
- Decomposed InfraTab (995→297 lines), SLATrackerTab (736→121 lines), ReportingTab (513→77 lines)
- Created `cve/infra/` (8 files), `cve/sla/` (8 files), `cve/reporting/` (7 files)
- Extracted shared components to `cve/components/` (ChartTooltip, LoadingStates, CodeBlock, Collapsible, RiskGauge)
- Centralized shared constants to `cve/constants.js` (CHART_COLORS, PIE_COLORS, STATUS_CHART_COLORS)
- GovernanceTab updated to use shared imports (deduped ~30 lines)
- Created barrel exports (`cve/index.js`, `cve/components/index.js`)
- No file over 300 lines; zero code duplication for shared components
- Frontend regression: 100% pass rate (iteration_36.json)

## Frontend Directory Structure (Refactored Feb 28, 2026)

```
/app/frontend/src/cve/
├── index.js              # Barrel export for all tabs
├── shared.js             # API constants, fetcher, utility components
├── constants.js          # Shared chart colors (deduped)
├── components/           # Shared UI components
│   ├── ChartTooltip.jsx
│   ├── CodeBlock.jsx
│   ├── Collapsible.jsx
│   ├── LoadingStates.jsx
│   ├── RiskGauge.jsx
│   └── index.js
├── infra/                # InfraTab decomposed (was 995 lines)
│   ├── InfraTab.jsx (297)
│   ├── LiveLambdaPanel.jsx
│   ├── GitHubRunsPanel.jsx
│   ├── TerraformStatePanel.jsx
│   ├── TerraformModulesPanel.jsx
│   ├── CdkConstructsPanel.jsx
│   ├── DeploySteps.jsx
│   ├── DeploymentLog.jsx
│   ├── helpers.jsx
│   └── index.js
├── sla/                  # SLATrackerTab decomposed (was 736 lines)
│   ├── SLATrackerTab.jsx (121)
│   ├── DashboardView.jsx
│   ├── AtRiskView.jsx
│   ├── EscalationRulesView.jsx
│   ├── EscalationWorkflowView.jsx
│   ├── NotificationSettingsView.jsx
│   ├── TrendsView.jsx
│   ├── badges.jsx
│   └── index.js
├── reporting/            # ReportingTab decomposed (was 513 lines)
│   ├── ReportingTab.jsx (77)
│   ├── ExecutiveView.jsx
│   ├── TrendsView.jsx
│   ├── TeamView.jsx
│   ├── ScannerView.jsx
│   ├── ExportView.jsx
│   └── index.js
├── GovernanceTab.jsx (427, uses shared imports)
├── OverviewTab.jsx
├── CVEDatabaseTab.jsx
├── RemediationTab.jsx
└── ... (other tabs)
```

## Prioritized Backlog

### P0 - All Core Features (COMPLETE)

### P1 - Future Tasks
- Real-time WebSocket notifications for SLA breaches
- External ticketing integration (Jira, ServiceNow)
- Multi-tenant support
- Advanced PDF with embedded charts

## Test Credentials
- Test user: cveadmin@test.com / Test1234!

## Test Reports
- iteration_33.json - PDF Export + Dashboard (26/26 passed)
- iteration_34.json - Initial Refactoring Regression (22/22 passed)
- iteration_35.json - Deep Refactoring Regression (33/33 passed)
- iteration_36.json - Frontend Refactoring Regression (100% pass)
