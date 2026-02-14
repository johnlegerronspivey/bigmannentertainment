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

## Key Files
- `/app/backend/cve_management_service.py` - Core CVE brain service (Phase 1)
- `/app/backend/cve_management_endpoints.py` - CVE API endpoints (prefix: /api/cve)
- `/app/backend/scanner_service.py` - Multi-scanner orchestration (Phase 2)
- `/app/backend/scanner_endpoints.py` - Scanner API endpoints (prefix: /api/cve/scanners)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Full dashboard UI with 9 tabs
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
- 3 new tabs added (Scanners, CI/CD, Policy Engine) - total 9 tabs
- Testing: 100% (22/22 backend, all frontend)

## Phased Roadmap

### Phase 3 (Next): Automated Remediation & GitHub Integration
- GitHub API: auto-create issues & PRs on critical CVEs
- Auto-version-bump PR generation
- Auto-assign to team based on ownership
- Remediation workflow engine

### Phase 4 (Future): Governance Dashboards & AWS Integration
- Rich analytics dashboards (charts, trends, time-to-remediate)
- AWS integration configs (Inspector, Security Hub, EventBridge templates)
- Terraform module templates
- Export/reporting for audit readiness

## User's GitHub Repo
https://github.com/johnlegerronspivey/bigmannentertainment

## Test Credentials
- Login: enterprise@test.com / TestPass123!
- API: https://dep-guardian.preview.emergentagent.com/api/cve
- Scanner API: https://dep-guardian.preview.emergentagent.com/api/cve/scanners
