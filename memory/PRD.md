# Big Mann Entertainment - CVE Management Platform PRD

## Original Problem Statement
Build a comprehensive enterprise CVE management platform with:
1. **Core CVE Brain**: Central vulnerability database with full lifecycle tracking
2. **SBOM Generation**: Track every dependency in the stack
3. **CI/CD Security Gates**: Dependency, container, and IaC scanning
4. **Automated Remediation**: GitHub API integration for auto-PRs, AWS Inspector/Security Hub
5. **Governance Dashboards**: Rich charts, analytics, trends, SLA tracking

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
- `/tmp/test_iac/main.tf` - Sample Terraform for IaC scanning demos

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
- GET /items - List remediation items (filter by status/severity)
- GET /items/{id} - Get single item
- PUT /items/{id}/status - Update remediation status
- POST /create-issue/{cve_id} - Create GitHub issue from CVE
- POST /create-pr/{cve_id} - Create GitHub PR with dependency bump
- POST /bulk-create-issues - Bulk create issues by severity
- POST /sync-github - Sync item statuses with GitHub
- GET /aws/findings - AWS Inspector findings
- POST /aws/sync - Import AWS findings into CVE DB
- GET /aws/security-hub - Security Hub summary
- GET /stats - Remediation statistics

### Phase 4 (/api/cve/governance/*)
- GET /metrics - Full governance dashboard metrics (risk score, severity dist, fix rate)
- GET /trends?days=30 - Daily detected/fixed trend data
- GET /sla - SLA compliance per severity with overall %
- GET /ownership - Team, person, source, status distribution
- GET /mttr - Mean Time to Remediate by severity
- GET /scan-activity - Scan history and scanner breakdown

## What's Been Implemented

### Phase 0 (Previous): Security Audit System
- CVE-2026-1615 vulnerability fix
- Automated CVE monitoring with APScheduler
- Email alerts via Resend, persistent MongoDB storage

### Phase 1 (Feb 14, 2026): CVE Brain & Core Dashboard - COMPLETE
- Central CVE database with full lifecycle tracking (6 states)
- SBOM generation, Service registry, Severity policy engine
- Comprehensive scan engine, Complete audit trail
- 6-tab dashboard UI
- Testing: 100% (24/24 backend, all frontend)

### Phase 2 (Feb 14, 2026): Scanning & CI/CD Gates - COMPLETE
- Installed real security tools: Trivy v0.58.2, Grype v0.108.0, Syft v1.42.0, Checkov 3.2.501
- Multi-scanner orchestration (5 scan types: trivy-fs, trivy-iac, grype, syft, checkov)
- Real vulnerability data: Grype found 30 vulns (1C/10H/14M), Checkov 42P/32F, Trivy IaC 19 misconfigs
- CI/CD pipeline generator (GitHub Actions YAML with security gates)
- Policy-as-code rules engine (5 rule types: severity threshold, CVSS, package blocklist, IaC failures)
- Deploy gate evaluation (block/warn based on scan results)
- 3 new tabs added (Scanners, CI/CD, Policy Engine)
- Testing: 100% (22/22 backend, all frontend)

### Phase 3 (Feb 14, 2026): Automated Remediation & GitHub/AWS Integration - COMPLETE
- GitHub API integration (PyGithub) - connected to johnlegerronspivey/bigmannentertainment
- Auto-create GitHub issues from CVEs with severity labels, detailed descriptions
- Auto-create GitHub PRs with dependency version bumps
- Bulk issue creation by severity level
- GitHub sync to track issue/PR status
- Remediation workflow lifecycle (open -> issue_created -> pr_created -> in_review -> merged -> deployed -> verified -> closed)
- AWS Inspector integration (live boto3 client, finding import)
- AWS Security Hub summary endpoint
- Enhanced AWS Findings UI with separate Inspector/Security Hub sub-tabs and connection status
- Testing: 100% (17/17 backend, all frontend)

### Phase 4 (Feb 14, 2026): Governance Dashboards & Advanced Analytics - COMPLETE
- Full governance analytics backend with 6 endpoints
- Risk Assessment gauge (weighted score: crit*25 + high*15 + med*5 + low*1)
- Severity distribution pie chart (open CVEs)
- Status distribution donut chart (all CVEs)
- CVE Trends area chart (30-day detected vs fixed)
- SLA Compliance tracking with per-severity progress bars (Critical: 24h, High: 72h, Medium: 168h, Low: 720h)
- Overall SLA compliance percentage
- Mean Time to Remediate (MTTR) bar chart by severity
- CVE ownership stats (by team, assignee, source)
- Open CVEs by service bar chart
- CVEs by source bar chart
- Governance tab with 4 sub-views (Overview, Trends, SLA Compliance, Ownership)
- Dashboard now has 11 tabs total
- Testing: 100% (26/26 backend, all frontend)

### Phase 4.1 (Feb 15, 2026): CVE Ownership Model - COMPLETE
- Backend: Dedicated ownership endpoints (PUT /entries/{id}/owner, POST /entries/bulk-assign, GET /owners, GET /unassigned)
- Backend: assign_owner, bulk_assign_owner, get_available_owners, get_unassigned_cves service methods with full audit trail
- Frontend: Assign/Reassign Owner button in CVE Database expanded view
- Frontend: AssignOwnerModal with dropdown for existing people/teams + New button for custom entry
- Frontend: Create CVE Modal now includes assigned_to and assigned_team fields
- Frontend: Governance > Ownership tab enhanced with unassigned CVE alert banner, unassigned CVE list with quick-assign buttons
- Frontend: Governance > Ownership tab shows Registered Owners and Registered Teams sections
- All ownership changes logged to audit trail
- Testing: 100% (17/17 backend, all frontend features verified)

## Phased Roadmap - ALL PHASES COMPLETE

All 4 phases have been implemented:
- Phase 1: CVE Brain & Core Dashboard
- Phase 2: Scanning & CI/CD Gates
- Phase 3: Automated Remediation & GitHub/AWS Integration
- Phase 4: Governance Dashboards & Advanced Analytics

### Potential Enhancements
- Export governance reports as PDF/CSV
- Email digest of weekly security posture
- Custom SLA policy editor
- Historical risk score tracking
- Integration with Jira/ServiceNow for ticket management
- Enhanced SLA Tracking with notifications and escalations for SLA breaches
- Refactor CVEManagementDashboard.jsx (2200+ lines) into smaller per-tab components

## User's GitHub Repo
https://github.com/johnlegerronspivey/bigmannentertainment

## Test Credentials
- Login: enterprise@test.com / TestPass123!
- API: https://threat-hub-1.preview.emergentagent.com/api/cve
- Scanner API: https://threat-hub-1.preview.emergentagent.com/api/cve/scanners
- Remediation API: https://threat-hub-1.preview.emergentagent.com/api/cve/remediation
- Governance API: https://threat-hub-1.preview.emergentagent.com/api/cve/governance
