# ULN Social Media Management & Creator Tools Platform — PRD

## Original Problem Statement
Build a social media management and creator tools platform featuring the Unified Label Network (ULN). The platform includes a ULN Notification System and an immutable Ownership Protection System for John LeGerron Spivey and Big Mann Entertainment.

## Core Requirements

### Verified & Complete
- ULN Notification System (In-app notifications for Governance, Disputes, Members, etc.)
- Strict Immutable Ownership & Percentage Protections (master_licensing enforced at 100%)
- DNS Health Checker and lookup functionality
- Automated CVE Monitoring Dashboard
- Mandatory GS1 & Business Identifiers Enforcement
- Fix and upgrade all CVE vulnerabilities (Backend to 0, Frontend to 0)
- Migrate frontend application from Create React App (CRA) to Vite
- Upgrade Tailwind CSS from v3 to v4
- DUNS Number 080955411 added to protected Business & GS1 Identifiers (2026-04-08)

### Pending
- Connect the mocked Revenue Tracking feature to real data sources
- Setup AWS external DNS health & track via in-app "Register New Target"

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React (Vite 8 with Rolldown/Oxc) + Tailwind CSS v4 (CSS-first)
- **Key Collections**: label_assets, label_rights, label_distributions, uln_labels, users, label_members, business_information, gs1_database, label_governance, label_disputes, business_identifiers

## Protected Owner
- Owner: John LeGerron Spivey
- Business: Big Mann Entertainment
- DUNS: 080955411
- EIN: 270658077
- GS1 Company Prefix: 08600043402
- GLN: 0860004340201

## Upcoming Tasks (Priority Order)
- P0: Connect Revenue Tracking to real data sources
- P1: "Register New Target" for DNS Health Checker
- P2: AWS external DNS health tracking
- P3: General feature completion and real data integration

## Tech Stack Notes
- Vite 8 uses Rolldown/Oxc (NOT esbuild) — configured via `transformWithOxc`
- Tailwind v4 CSS-first config in `index.css` with `@theme inline`
- `@apply` in secondary CSS files requires `@reference "./index.css"`
- shadcn/ui components configured for Tailwind v4
