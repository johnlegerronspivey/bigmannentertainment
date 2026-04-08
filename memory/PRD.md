# Big Mann Entertainment - Social Media Management & Creator Tools Platform

## Original Problem Statement
Build a social media management and creator tools platform featuring the Unified Label Network (ULN) with Notification System, immutable Ownership Protection for John LeGerron Spivey / Big Mann Entertainment, DNS Health Checker, CVE Monitoring Dashboard, GS1 & Business Identifiers Enforcement, Quick Actions Panel, Governance Dashboard widget with drill-down, and Revenue Tracking.

## Architecture
- **Frontend**: React 19 + **Tailwind CSS v4** + Shadcn UI (**Vite 8** + Rolldown/Oxc + `@tailwindcss/vite`)
- **Backend**: FastAPI + MongoDB
- **Auth**: JWT-based with bcrypt password hashing

## Completed Features
- [x] ULN Notification System
- [x] Immutable Ownership & Percentage Protections (master_licensing at 100%)
- [x] DNS Health Checker
- [x] Automated CVE Monitoring Dashboard
- [x] GS1 & Business Identifiers Enforcement
- [x] Quick Actions Panel for GS1 Hub
- [x] Governance Dashboard widget on Overview tab
- [x] Interactive drill-down from Governance widget to individual disputes
- [x] **CVE Vulnerability Fix & Upgrade (Apr 8, 2026)**:
  - Backend: 17 vulnerabilities -> 0
  - Frontend: 94 -> 48 (pre-Vite migration)
- [x] **CRA to Vite 8 Migration (Apr 8, 2026)**:
  - Migrated from Create React App + Craco to Vite 8.0.7 with Rolldown/Oxc
  - Frontend vulnerabilities: 48 -> 30 (eliminated all CRA/webpack/react-scripts CVEs)
  - Custom `transformWithOxc` plugin for JSX-in-.js file compat
  - Env var compat: `process.env.REACT_APP_*` preserved via Vite `define`
  - Removed: react-scripts, @craco/craco, cra-template, postinstall patch
  - 100% test pass rate (17/17 backend, all frontend pages verified)
- [x] **Frontend CVE Elimination via Yarn Resolutions (Apr 8, 2026)**:
  - Frontend vulnerabilities: 30 -> 0 (all eliminated)
  - Added yarn resolutions: picomatch>=2.3.2, glob>=10.5.0, yaml>=2.8.3
  - Backend remains at 0 vulnerabilities
  - 100% test pass rate (iteration 107)

- [x] **Tailwind CSS v3 to v4 Migration (Apr 8, 2026)**:
  - Upgraded from Tailwind CSS v3.4.17 to v4.2.2
  - Replaced PostCSS-based plugin with `@tailwindcss/vite` Vite plugin
  - Converted `tailwind.config.js` to CSS-first `@theme inline` in `index.css`
  - Replaced `tailwindcss-animate` with `tw-animate-css`
  - Added `@reference` directive in `App.css` for `@apply` support
  - Removed `tailwind.config.js`, emptied `postcss.config.js`
  - 100% test pass rate (iteration 108, 6+ pages verified)

## Pending / Upcoming Tasks
- [ ] (P0) Connect Revenue Tracking to real data sources (currently mocked)
- [ ] (P1) "Register New Target" for DNS Health Checker (monitor bigmannentertainment.com)
- [ ] (P2) Connect AWS Route 53 external DNS health

## Key API Endpoints
- `GET /api/gs1/quick-actions/summary`
- `GET /api/gs1/governance-overview`
- `GET /api/gs1/disputes` / `GET /api/gs1/disputes/{dispute_id}`
- `GET /api/uln/labels/{label_id}/governance-disputes-summary`
- `GET /api/cve-monitor/health` / `GET /api/cve/health`

## DB Collections
`label_assets`, `label_rights`, `label_distributions`, `uln_labels`, `users`, `label_members`, `business_information`, `gs1_database`, `label_governance`, `label_disputes`

## 3rd Party Integrations
- NVD (National Vulnerability Database) - public REST, no keys
- Facebook/Instagram/Threads URL Scraping - public, no keys
- DNS via dnspython - no keys
- AWS Route 53 (external setup by user)

## Protected Entities
**DO NOT** bypass, remove, or alter ownership protections for:
- John LeGerron Spivey
- Big Mann Entertainment
