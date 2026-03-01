# Big Mann Entertainment - PRD

## Original Problem Statement
Configure the application to work with the custom domain `bigmannentertainment.com`, including a Domain Configuration admin page, AWS Route53 DNS auto-management, SES email verification, and CloudFront CDN status monitoring.

## Core Requirements
1. Custom domain configuration for `bigmannentertainment.com`
2. Admin panel "Domain Configuration" page
3. SES, CloudFront, Route53 status display
4. Required DNS records listing
5. One-click Route53 DNS auto-configure
6. Manual DNS record add/delete
7. Admin user (`cveadmin@test.com`) with correct permissions

## Architecture
```
/app
├── backend/
│   ├── routes/
│   │   ├── aws_routes.py          # S3, SES email, CDN, Lambda, Rekognition media endpoints
│   │   ├── domain_routes.py       # Domain config + Route53 DNS management endpoints
│   │   ├── health_routes.py       # Health checks (payment, metadata, AWS, etc.)
│   │   ├── admin_routes.py
│   │   ├── auth_routes.py
│   │   ├── agency_routes.py
│   │   ├── business_routes.py
│   │   ├── dao_routes.py
│   │   ├── distribution_routes.py
│   │   ├── licensing_routes.py
│   │   ├── media_routes.py
│   │   └── system_routes.py
│   ├── services/
│   │   ├── route53_svc.py         # AWS Route53 API service
│   │   ├── s3_svc.py
│   │   ├── ses_transactional_svc.py
│   │   └── aws_media_svc.py
│   └── server.py
└── frontend/
    ├── src/admin/DomainConfigPage.jsx
    ├── public/manifest.json
    └── public/robots.txt
```

## What's Been Implemented
- Domain Configuration page with SES/CloudFront/Route53 status
- Route53 DNS auto-configure (8 records)
- Manual DNS record CRUD
- Security headers middleware (CSP, HSTS)
- SEO files (robots.txt, manifest.json)
- Admin access fix for cveadmin@test.com
- **Refactored aws_routes.py** into domain_routes.py + health_routes.py (Feb 2026)

## Key API Endpoints
- `GET /api/domain/status` - Domain configuration status
- `POST /api/domain/ses/verify` - SES domain verification
- `GET /api/domain/ses/check` - SES verification status
- `GET /api/domain/dns-guide` - DNS configuration guide
- `GET /api/route53/zone` - Route53 hosted zone info
- `GET /api/route53/records` - List DNS records
- `POST /api/route53/record` - Create/update DNS record
- `DELETE /api/route53/record` - Delete DNS record
- `POST /api/route53/auto-configure` - Auto-configure all DNS records
- `GET /api/aws/health` - AWS services health check
- `GET /api/phase2/status` - Phase 2 services status

## 3rd Party Integrations
- AWS: S3, SES, CloudFront, Lambda, Rekognition, Route53, GuardDuty, CloudWatch, Inspector, Detective, RDS, Organizations
- Jira (ticketing), Stripe (payments), Google Generative AI

## Credentials
- Super Admin: `cveadmin@test.com` / `Test1234!`

## Backlog
- P1: User verification of all completed features (SLA Dashboard, RBAC, Ticketing, etc.)
- P2: Further route file splits if needed
