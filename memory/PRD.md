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
- **Background Jobs**: APScheduler (for existing security monitoring)
- **Email**: Resend (for existing CVE alerts)

## Key Files
- `/app/backend/cve_management_service.py` - Core CVE brain service
- `/app/backend/cve_management_endpoints.py` - API endpoints (prefix: /api/cve)
- `/app/frontend/src/CVEManagementDashboard.jsx` - Full dashboard UI with 6 tabs
- `/app/backend/security_audit_service.py` - Existing security audit monitoring
- `/app/backend/security_audit_endpoints.py` - Existing audit endpoints

## MongoDB Collections (CVE Platform)
- `cve_entries` - CVE records with lifecycle state (detected→triaged→in_progress→fixed→verified→dismissed)
- `cve_services` - Service registry with ownership, criticality, tech stack
- `cve_sbom_records` - SBOM snapshots with component lists
- `cve_severity_policies` - Configurable SLA policies per severity level
- `cve_audit_trail` - Every action logged with timestamp and user

## API Endpoints (all /api/cve/*)
- GET /health, GET /dashboard
- CRUD: /entries, /entries/{id}, /entries/{id}/status
- CRUD: /services, /services/{id}
- POST /sbom/generate, GET /sbom/list, GET /sbom/{id}
- GET /policies, PUT /policies
- POST /scan (comprehensive vulnerability scan)
- GET /audit-trail
- POST /seed (sample data)

## What's Been Implemented

### Phase 0 (Previous): Security Audit System
- CVE-2026-1615 vulnerability fix
- Automated CVE monitoring with APScheduler
- Email alerts via Resend
- Persistent storage in MongoDB

### Phase 1 (Feb 14, 2026): CVE Brain & Core Dashboard - COMPLETE
- Central CVE database with full lifecycle tracking (6 states)
- SBOM generation parsing package.json and requirements.txt (293 components)
- Service registry with 4 pre-configured services (frontend, backend, blockchain, AWS infra)
- Severity policy engine (Critical: 24h SLA, High: 72h, Medium: 336h, Low: 720h)
- Comprehensive scan engine (yarn audit + pip-audit with auto-CVE creation)
- Complete audit trail for all actions
- 6-tab dashboard UI (Overview, CVE Database, Services, SBOM, Policies, Audit Trail)
- Testing: 100% backend (24/24), 100% frontend

## Phased Roadmap

### Phase 2 (Upcoming): Scanning & CI/CD Gates
- Multi-scanner integration (trivy, checkov, tfsec, grype)
- Container image scanning
- IaC scanning for Terraform
- CI/CD pipeline config generator (GitHub Actions YAML)
- Policy-as-code rules engine

### Phase 3 (Future): Automated Remediation & GitHub Integration
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
