# Big Mann Entertainment - CVE Management Platform PRD

## Original Problem Statement
Build a comprehensive enterprise CVE management platform with:
1. **Core CVE Brain**: Central vulnerability database with full lifecycle tracking
2. **SBOM Generation**: Track every dependency in the stack
3. **CI/CD Security Gates**: Dependency, container, and IaC scanning
4. **Automated Remediation**: GitHub API integration for auto-PRs, AWS Inspector/Security Hub
5. **Governance Dashboards**: Rich charts, analytics, trends, SLA tracking

Additionally, an infrastructure automation pipeline for CVE remediation using Terraform, AWS Lambda, and GitHub Actions.

## Architecture
- **Frontend**: React (CRA) with Tailwind CSS, Lucide React icons, Recharts
- **Backend**: FastAPI (Python) with Motor (async MongoDB driver)
- **Database**: MongoDB
- **Security Tools**: Trivy v0.58.2, Grype v0.108.0, Syft v1.42.0, Checkov 3.2.501
- **Background Jobs**: APScheduler (for existing security monitoring)
- **Email**: Resend (for existing CVE alerts)
- **GitHub Integration**: PyGithub for issue/PR creation
- **AWS**: boto3 for Inspector/Security Hub
- **Charts**: Recharts (PieChart, BarChart, AreaChart, LineChart)
- **IaC**: Terraform (multi-environment: dev, staging, prod)
- **CI/CD**: GitHub Actions (Lambda artifact build + upload)

## Key Files
- `/app/backend/cve_management_service.py` - Core CVE brain service (Phase 1)
- `/app/backend/cve_management_endpoints.py` - CVE API endpoints (prefix: /api/cve)
- `/app/backend/scanner_service.py` - Multi-scanner orchestration (Phase 2)
- `/app/backend/scanner_endpoints.py` - Scanner API endpoints (prefix: /api/cve/scanners)
- `/app/backend/remediation_service.py` - Remediation & GitHub/AWS integration (Phase 3)
- `/app/backend/remediation_endpoints.py` - Remediation API endpoints (prefix: /api/cve/remediation)
- `/app/backend/governance_service.py` - Governance analytics service (Phase 4)
- `/app/backend/governance_endpoints.py` - Governance API endpoints (prefix: /api/cve/governance)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Full dashboard UI with 11 tabs

## MongoDB Collections
### Phase 1
- `cve_entries` - CVE records with lifecycle state
- `cve_services` - Service registry with ownership
- `cve_sbom_records` - SBOM snapshots
- `cve_severity_policies` - Configurable SLA policies
- `cve_audit_trail` - Action log

### Phase 2
- `cve_scan_results` - Scanner output (trivy, grype, syft, checkov)
- `cve_policy_rules` - Policy-as-code rules
- `cve_pipeline_configs` - Generated CI/CD pipeline configs

### Phase 3
- `cve_remediation_items` - Remediation tracking (GitHub issues/PRs, status lifecycle)
- `cve_aws_findings` - Cached AWS Inspector findings

## API Endpoints
### Phase 1 (/api/cve/*)
- GET /health, GET /dashboard
- CRUD: /entries, /entries/{id}, /entries/{id}/status
- PUT /entries/{id}/owner - Assign/reassign CVE owner (Phase 4.1)
- POST /entries/bulk-assign - Bulk assign owners (Phase 4.1)
- GET /owners - List available owners and teams (Phase 4.1)
- GET /unassigned - List unassigned open CVEs (Phase 4.1)
- CRUD: /services, /services/{id}
- POST /sbom/generate, GET /sbom/list, GET /sbom/{id}
- GET /policies, PUT /policies
- POST /scan, GET /audit-trail, POST /seed

### Phase 2 (/api/cve/scanners/*)
- GET /tools - Tool installation status
- POST /trivy/fs, /trivy/iac - Trivy scans
- POST /grype - Grype dependency scan
- POST /syft - Syft SBOM generation
- POST /checkov - Checkov IaC scan
- GET /results, GET /results/{id} - Scan history
- CRUD: /policy-rules, POST /policy-rules/seed, POST /policy-rules/evaluate/{scan_id}
- POST /pipeline/generate, GET /pipeline/list, GET /pipeline/{id}

### Phase 3 (/api/cve/remediation/*)
- GET /config - GitHub connection status + stats
- GET /items - List remediation items
- GET /items/{id} - Get single item
- PUT /items/{id}/status - Update remediation status
- POST /create-issue/{cve_id} - Create GitHub issue from CVE
- POST /create-pr/{cve_id} - Create GitHub PR
- POST /bulk-create-issues - Bulk create issues by severity
- POST /sync-github - Sync item statuses with GitHub
- GET /aws/findings, POST /aws/sync, GET /aws/security-hub
- GET /stats - Remediation statistics

### Phase 4 (/api/cve/governance/*)
- GET /metrics, GET /trends, GET /sla, GET /ownership, GET /mttr, GET /scan-activity

## Completed Phases

### Phase 1: CVE Brain & Core Dashboard - COMPLETE
### Phase 2: Scanning & CI/CD Gates - COMPLETE
### Phase 3: Automated Remediation & GitHub/AWS Integration - COMPLETE (Verified Feb 15, 2026)
### Phase 4: Governance Dashboards & Advanced Analytics - COMPLETE
### Phase 4.1: CVE Ownership Model - COMPLETE (Verified Feb 15, 2026)
### Phase 5 Infrastructure: Remediation Automation Pipeline - COMPLETE (User verification pending for Terraform/Lambda)

## Prioritized Backlog

### P1 - Phase 5: Notifications & Reporting
- Email/UI alerts for new CVEs and SLA breaches
- Export governance reports as PDF/CSV
- Email digest of weekly security posture

### P2 - Phase 6: User Management & RBAC
- Role-Based Access Control
- Admin/Manager/Analyst roles

### P2 - Refactoring
- Break down CVEManagementDashboard.jsx (2300+ lines) into per-tab components

### P3 - Enhancements
- Custom SLA policy editor
- Historical risk score tracking
- Jira/ServiceNow integration
- Enhanced SLA Tracking with escalations

## Test Credentials
- Login: enterprise@test.com / TestPass123!
- API: https://cve-infra.preview.emergentagent.com/api/cve
- GitHub Repo: johnlegerronspivey/bigmannentertainment

## User's GitHub Repo
https://github.com/johnlegerronspivey/bigmannentertainment
