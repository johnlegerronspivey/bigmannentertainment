# Backend Architecture Guide

## Directory Structure

```
/app/backend/
├── server.py                      # Main entry point (~375 lines) - app, middleware, startup, wiring
├── router_setup.py                # External router registration (pre-existing modules)
│
├── config/                        # Configuration (extracted from server.py)
│   ├── database.py                # MongoDB connection (db, client)
│   ├── settings.py                # Environment variables, constants (Settings class)
│   └── platforms.py               # DISTRIBUTION_PLATFORMS (119 platforms, 1100 lines)
│
├── models/                        # Pydantic models (extracted from server.py)
│   ├── core.py                    # User, Token, Media, Purchase, NFT, etc. (315 lines)
│   └── agency.py                  # Agency onboarding models (75 lines)
│
├── auth/                          # Authentication (extracted from server.py)
│   └── service.py                 # verify_password, create_token, get_current_user (87 lines)
│
├── routes/                        # Endpoint handlers (extracted from server.py)
│   ├── auth_routes.py             # Register, login, logout, password reset (438 lines)
│   ├── agency_routes.py           # Agency registration, KYC, talent, contracts (638 lines)
│   ├── admin_routes.py            # User mgmt, content moderation, notifications (286 lines)
│   ├── business_routes.py         # Business identifiers, UPC/ISRC generation (272 lines)
│   ├── media_routes.py            # Upload, library, CRUD, search (537 lines)
│   ├── distribution_routes.py     # Platform management, distribution (422 lines)
│   ├── dao_routes.py              # Smart contracts, governance, disputes (159 lines)
│   ├── licensing_routes.py        # Licensing health, compliance (211 lines)
│   ├── health_routes.py           # Service health checks (437 lines)
│   ├── aws_routes.py              # S3, SES, CDN, media processing (850 lines)
│   └── system_routes.py           # Status, performance, metadata (279 lines)
│
├── services/                      # Business logic classes (extracted from server.py)
│   ├── distribution_svc.py        # DistributionService class (191 lines)
│   ├── email_svc.py               # SESService + EmailService (720 lines)
│   ├── s3_svc.py                  # S3Service (188 lines)
│   ├── ses_transactional_svc.py   # Transactional SES + Notification service (321 lines)
│   └── aws_media_svc.py           # CloudFront, Lambda, Rekognition (219 lines)
│
├── tests/                         # Test files (33+ test files)
├── providers/                     # Social media providers
├── lambda/                        # AWS Lambda functions
├── *_endpoints.py                 # Pre-existing external endpoint modules
├── *_service.py                   # Pre-existing external service modules
└── requirements.txt               # Python dependencies
```

## Import Patterns

### For new code, always import from extracted modules:
```python
from config.database import db
from config.settings import settings
from config.platforms import DISTRIBUTION_PLATFORMS
from models.core import User, Token, MediaContent
from models.agency import AgencyRegistrationRequest
from auth.service import get_current_user, get_current_admin_user
```

### Backward compatibility
`from server import X` still works via re-exports for: User, Token, db, settings aliases, etc.
New code should use the extracted modules directly.

## Refactoring Summary
- **Original server.py**: 8,141 lines (monolith)
- **New server.py**: 375 lines (96% reduction)
- **Extracted modules**: 7,890 lines across 27 files in 5 directories
- **Tests**: 33/33 deep regression tests + 22/22 original tests all pass
```
