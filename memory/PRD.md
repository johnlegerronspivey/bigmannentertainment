# Big Mann Entertainment - CVE Management Platform PRD

## Original Problem Statement
Build a comprehensive enterprise CVE management platform with:
1. **Core CVE Brain**: Central vulnerability database with full lifecycle tracking
2. **SBOM Generation**: Track every dependency in the stack
3. **CI/CD Security Gates**: Dependency, container, and IaC scanning
4. **Automated Remediation**: GitHub API integration for auto-PRs
5. **Governance Dashboards**: Rich charts, analytics, trends

## Architecture
- **Frontend**: React (CRA) with Tailwind CSS, Lucide React icons
- **Backend**: FastAPI (Python) with Motor (async MongoDB driver)
- **Database**: MongoDB
- **Security Tools**: Trivy v0.58.2, Grype v0.108.0, Syft v1.42.0, Checkov 3.2.501
- **Background Jobs**: APScheduler (for existing security monitoring)
- **Email**: Resend (for existing CVE alerts)
- **GitHub Integration**: PyGithub for issue/PR creation
- **AWS**: boto3 for Inspector/Security Hub

## Key Files
- `/app/backend/cve_management_service.py` - Core CVE brain service (Phase 1)
- `/app/backend/cve_management_endpoints.py` - CVE API endpoints (prefix: /api/cve)
- `/app/backend/scanner_service.py` - Multi-scanner orchestration (Phase 2)
- `/app/backend/scanner_endpoints.py` - Scanner API endpoints (prefix: /api/cve/scanners)
- `/app/backend/remediation_service.py` - Remediation & GitHub integration (Phase 3)
- `/app/backend/remediation_endpoints.py` - Remediation API endpoints (prefix: /api/cve/remediation)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Full dashboard UI with 10 tabs
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
- Auto-create GitHub PRs with dependency version bumps (requirements.txt, package.json, pyproject.toml)
- Bulk issue creation by severity level
- GitHub sync to track issue/PR status (open, merged, closed)
- Remediation workflow lifecycle (open → issue_created → pr_created → in_review → merged → deployed → verified → closed)
- AWS Inspector integration (live boto3 client, finding import)
- AWS Security Hub summary endpoint
- New "Remediation" tab with 4 sub-views (Items, Create from CVEs, Bulk Ops, AWS Findings)
- Dashboard now has 10 tabs total
- Testing: 100% (17/17 backend, all frontend)
- Note: GitHub token has read-only permissions; create operations return informative error. Update token at github.com/settings/tokens for full write access.

## Phased Roadmap

### Phase 4 (Next): Governance Dashboards & Advanced Analytics
- Rich analytics dashboards (charts, trends, time-to-remediate)
- CVE ownership model and SLA tracking
- Export/reporting for audit readiness
- Historical trend visualization

## User's GitHub Repo
https://github.com/johnlegerronspivey/bigmannentertainment

## Test Credentials
- Login: enterprise@test.com / TestPass123!
- API: https://vuln-shift-left.preview.emergentagent.com/api/cve
- Scanner API: https://vuln-shift-left.preview.emergentagent.com/api/cve/scanners
- Remediation API: https://vuln-shift-left.preview.emergentagent.com/api/cve/remediation
