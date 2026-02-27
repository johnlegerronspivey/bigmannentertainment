# Backend Architecture Guide

## Directory Structure

```
/app/backend/
├── server.py                      # Main FastAPI app entry point (middleware, startup, wiring)
├── router_setup.py                # Central router registration (all external endpoint modules)
│
├── config/                        # Configuration (extracted from server.py)
│   ├── __init__.py
│   ├── database.py                # MongoDB connection (db, client)
│   ├── settings.py                # Environment variables, constants (Settings class)
│   └── platforms.py               # DISTRIBUTION_PLATFORMS (119 platforms)
│
├── models/                        # Pydantic models (extracted from server.py)
│   ├── __init__.py                # Re-exports all models
│   ├── core.py                    # User, Token, Media, Purchase, NFT, etc.
│   └── agency.py                  # Agency onboarding models
│
├── auth/                          # Authentication (extracted from server.py)
│   ├── __init__.py                # Re-exports auth functions
│   └── service.py                 # verify_password, create_token, get_current_user, etc.
│
├── routes/                        # Route packages (for new endpoints)
│   └── __init__.py
│
├── services/                      # Service packages (for new services)
│   └── __init__.py
│
├── tests/                         # Test files
│   ├── test_cve_management.py
│   ├── test_cve_reporting.py
│   └── ... (30+ test files)
│
├── providers/                     # Social media providers
│   ├── base_provider.py
│   ├── snapchat_provider.py
│   ├── tiktok_provider.py
│   └── twitter_provider.py
│
├── lambda/                        # AWS Lambda functions
│   ├── doohCampaignManager.py
│   └── doohTriggerEngine.py
│
├── *_endpoints.py                 # API endpoint modules (registered in router_setup.py)
├── *_service.py                   # Business logic services
├── *_models.py                    # Domain-specific models
└── requirements.txt               # Python dependencies
```

## Import Patterns

### For new code, import from extracted modules:
```python
# Database
from config.database import db

# Settings
from config.settings import settings

# Models
from models.core import User, Token, MediaContent
from models.agency import AgencyRegistrationRequest

# Auth
from auth.service import get_current_user, get_current_admin_user

# Platforms config
from config.platforms import DISTRIBUTION_PLATFORMS
```

### Backward compatibility
Existing code that uses `from server import X` will still work via re-exports in server.py,
but new code should use the extracted modules directly.

## Key Design Decisions
1. **Flat file structure preserved** for existing modules to minimize migration risk
2. **New directories** (config/, models/, auth/) for extracted shared code
3. **server.py** remains the entry point but is significantly slimmer
4. **router_setup.py** handles all external router registration
```
