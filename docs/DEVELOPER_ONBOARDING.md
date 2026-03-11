# Developer Onboarding Guide

Welcome to the **Big Mann Entertainment** codebase. This guide will get you from zero to productive as fast as possible.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Repository Structure](#repository-structure)
4. [Local Development Setup](#local-development-setup)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [API Documentation](#api-documentation)
8. [Database Schema](#database-schema)
9. [Key Conventions](#key-conventions)
10. [Common Development Workflows](#common-development-workflows)
11. [Testing](#testing)
12. [Environment Variables](#environment-variables)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)

---

## Project Overview

Big Mann Entertainment is a full-stack **creator tools platform** for music and media distribution. It enables creators to upload content, distribute to 120+ commercial platforms, track analytics, manage royalties, and engage with audiences — all from a single dashboard.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| Content Management | Upload and manage audio, video, images, and film content |
| Distribution Hub | Distribute content to 120+ platforms (Spotify, Apple Music, YouTube, etc.) |
| Creator Analytics | Anomaly detection, demographics, revenue tracking, best-time-to-post |
| Social Connections | Connect and post to social media accounts |
| Direct Messaging | User-to-user messaging system |
| Real-Time Notifications | WebSocket-powered live notifications |
| Payments & Subscriptions | Stripe and PayPal integration |
| Royalty Engine | Real-time royalty calculation and splits |
| Music Industry Standards | DDEX, ISRC/UPC, MLC, CWR support |
| Security | AWS GuardDuty, Macie, CVE management, RBAC |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18 (CRA) + Tailwind CSS + Shadcn/UI |
| **Backend** | Python 3 + FastAPI + Motor (async MongoDB driver) |
| **Database** | MongoDB |
| **File Storage** | Local disk (`/app/uploads/`) — S3 in production |
| **Real-Time** | WebSockets (FastAPI native) |
| **Payments** | Stripe SDK + PayPal SDK |
| **Cloud** | AWS (S3, SES, CloudFront, Lambda, Rekognition, GuardDuty, etc.) |
| **AI** | Google Generative AI |

---

## Repository Structure

```
/app
├── backend/                    # FastAPI backend application
│   ├── server.py               # Entry point — app creation, middleware, router wiring
│   ├── startup.py              # Startup/shutdown lifecycle hooks
│   ├── router_setup.py         # Secondary router wiring (70+ endpoint modules)
│   ├── middleware.py            # HTTP middleware (rate limiting, security headers, perf tracking)
│   ├── api/                    # 77 endpoint modules (extended/specialized routes)
│   ├── routes/                 # 24 core route modules (primary business logic)
│   ├── services/               # 107 service modules (business logic, adapters, engines)
│   ├── models/                 # 30 data model modules (Pydantic models, schemas)
│   ├── utils/                  # 34 utility modules (helpers, formatters, validators)
│   ├── config/                 # Configuration (database, settings, platform registry)
│   ├── auth/                   # Authentication modules (JWT, middleware, decorators)
│   ├── providers/              # Provider modules (external service wrappers)
│   ├── tests/                  # Backend test suites
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Backend environment variables (NEVER commit)
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── App.js              # Root component and routing
│   │   ├── components/         # Reusable UI components
│   │   │   └── ui/             # Shadcn/UI components (Button, Card, Dialog, etc.)
│   │   ├── pages/              # Page-level components (one per route)
│   │   └── ...
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── .env                    # Frontend environment variables
│
├── docs/                       # All project documentation
│   ├── DEVELOPER_ONBOARDING.md # This file
│   ├── API_Quick_Reference.md  # API endpoint quick reference
│   └── ...                     # Security docs, deployment guides, etc.
│
├── memory/                     # Agent memory and product docs
│   └── PRD.md                  # Product Requirements Document
│
├── test_reports/               # Automated test result reports
├── uploads/                    # User-uploaded content files
│   ├── content/                # General content uploads
│   ├── hub/                    # Distribution hub uploads
│   ├── audio/                  # Audio files
│   ├── video/                  # Video files
│   └── image/                  # Image files
│
├── aws/                        # AWS CLI and utilities
├── aws-infrastructure/         # AWS CDK infrastructure
├── infra-terraform/            # Terraform IaC
├── lambda/                     # Lambda function code
├── scripts/                    # Admin/utility scripts
└── tests/                      # Legacy test scripts
```

---

## Local Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ and Yarn
- MongoDB 6+
- Git

### 1. Clone and Install

```bash
# Backend
cd /app/backend
pip install -r requirements.txt

# Frontend
cd /app/frontend
yarn install
```

### 2. Configure Environment

Backend (`/app/backend/.env`):
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=bigmann
SECRET_KEY=your-secret-key
```

Frontend (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. Start Services

The platform uses **supervisor** to manage both services:

```bash
# Start both services
sudo supervisorctl start backend frontend

# Check status
sudo supervisorctl status

# Restart after .env or dependency changes
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

Backend runs on port **8001**, frontend on port **3000**.

### 4. Verify

```bash
# Backend health
curl http://localhost:8001/health

# API docs (Swagger UI)
curl http://localhost:8001/api/docs

# Frontend
open http://localhost:3000
```

---

## Backend Architecture

### Request Flow

```
Client Request
  → Kubernetes Ingress (/api/* → port 8001, else → port 3000)
    → FastAPI Middleware (rate limiting → security headers → perf tracking)
      → Router (api_router with /api prefix)
        → Route Handler (routes/ or api/)
          → Service Layer (services/)
            → Database (MongoDB via Motor)
```

### Key Files

| File | Purpose |
|------|---------|
| `server.py` | App factory — creates FastAPI app, wires middleware, mounts routers |
| `startup.py` | `on_startup` / `on_shutdown` hooks (DB indexes, cleanup) |
| `router_setup.py` | Wires 70+ secondary endpoint modules under `/api` |
| `middleware.py` | HTTP middleware: rate limiting, security headers, performance tracking |
| `config/database.py` | MongoDB connection via Motor async driver |
| `config/settings.py` | Centralized settings (loaded from env vars) |
| `config/platforms.py` | Registry of 120+ distribution platforms |
| `auth/` | JWT creation/verification, auth dependency decorators |

### Route Organization

Routes are split into two groups:

1. **Core Routes** (`routes/`) — 24 modules covering primary business domains:
   - `auth_routes.py` — Login, register, JWT refresh
   - `content_routes.py` — Content CRUD (`/user-content`)
   - `messaging_routes.py` — Direct messaging (`/messages`)
   - `analytics_routes.py` — Creator analytics (`/analytics`)
   - `distribution_hub_routes.py` — Distribution hub (`/distribution-hub`)
   - `notification_routes.py` — Notifications (`/notifications`)
   - `social_connections_routes.py` — Platform connections (`/social`)
   - ... and more

2. **Extended Routes** (`api/`) — 77 modules for specialized features:
   - `ddex_endpoints.py`, `stripe_endpoints.py`, `cve_management_endpoints.py`, etc.
   - These are wired via `router_setup.py`

### Service Layer

Services in `services/` contain all business logic, keeping route handlers thin:

- `platform_adapters.py` — Adapters for delivering content to external platforms
- `delivery_engine.py` — Background delivery processor with retry logic
- `anomaly_service.py` — Z-score anomaly detection on metrics
- `audience_service.py` — Audience demographics and geographic data
- `revenue_service.py` — Revenue tracking across platforms

### Adding a New Endpoint

1. **Create a route file** in `routes/` (core) or `api/` (extended):

```python
# backend/routes/my_feature_routes.py
from fastapi import APIRouter, Depends
from auth.auth_middleware import get_current_user

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("/")
async def list_items(current_user: dict = Depends(get_current_user)):
    """List all items for the current user."""
    return {"items": []}
```

2. **Wire it in `server.py`** (core routes) or `router_setup.py` (extended):

```python
# In server.py — add import and include
from routes.my_feature_routes import router as my_feature_router
# Add to core_routers list
```

3. **Add the service layer** if the endpoint has business logic:

```python
# backend/services/my_feature_service.py
from config.database import db

async def get_items(user_id: str):
    items = await db.my_collection.find(
        {"user_id": user_id},
        {"_id": 0}  # IMPORTANT: Always exclude _id from responses
    ).to_list(100)
    return items
```

---

## Frontend Architecture

### Key Directories

```
frontend/src/
├── App.js                  # Root component, React Router setup
├── components/
│   ├── ui/                 # Shadcn/UI primitives (Button, Card, Dialog, etc.)
│   ├── Navbar.jsx          # Top navigation bar
│   ├── Sidebar.jsx         # Sidebar navigation
│   └── ...                 # Feature-specific components
├── pages/
│   ├── Dashboard.jsx       # Main dashboard
│   ├── ContentManagement.jsx
│   ├── DistributionHub.jsx
│   ├── CreatorAnalytics.jsx
│   ├── Messages.jsx
│   └── ...
└── lib/
    └── utils.js            # Utility functions (cn, formatDate, etc.)
```

### Conventions

- **API calls**: Always use `process.env.REACT_APP_BACKEND_URL` as the base URL
- **Components**: Use Shadcn/UI from `../components/ui/[component]`
- **Styling**: Tailwind CSS utility classes; avoid inline styles
- **State**: React hooks (`useState`, `useEffect`); no global state library
- **Toasts**: Use `sonner` via `../components/ui/sonner`
- **Icons**: `lucide-react` (already installed)
- **Test IDs**: Every interactive element must have `data-testid` (kebab-case)

### Adding a New Page

1. Create the page component in `pages/`:

```jsx
// frontend/src/pages/MyFeature.jsx
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL;

export default function MyFeature() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch(`${API}/api/my-feature`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setData);
  }, []);

  return (
    <div data-testid="my-feature-page" className="p-6">
      <h1 className="text-2xl font-bold mb-4">My Feature</h1>
      {/* ... */}
    </div>
  );
}
```

2. Add a route in `App.js`:

```jsx
<Route path="/my-feature" element={<MyFeature />} />
```

---

## API Documentation

### Interactive Docs

Once the backend is running, access the auto-generated API documentation:

| URL | Format |
|-----|--------|
| `/api/docs` | **Swagger UI** — Interactive API explorer with "Try it out" |
| `/api/redoc` | **ReDoc** — Clean, readable API reference |
| `/api/openapi.json` | **OpenAPI 3.x spec** — Machine-readable JSON schema |

### Quick Auth for Swagger UI

1. Open `/api/docs`
2. Click **Authorize** (lock icon)
3. Enter: `Bearer <your_jwt_token>`
4. Click **Authorize** — all subsequent requests include the token

### Key Endpoint Groups

| Tag | Base Path | Description |
|-----|-----------|-------------|
| Authentication | `/api/auth/*` | Register, login, refresh tokens |
| Content Management | `/api/user-content/*` | Upload, list, search content |
| Distribution Hub | `/api/distribution-hub/*` | Manage distributions and deliveries |
| Creator Analytics | `/api/analytics/*` | Metrics, anomalies, demographics, revenue |
| Social Connections | `/api/social/*` | Platform connections and posts |
| Direct Messaging | `/api/messages/*` | Conversations and messages |
| Notifications | `/api/notifications/*` | Notification list and read status |

---

## Database Schema

MongoDB collections and their key fields:

| Collection | Description | Key Fields |
|------------|-------------|------------|
| `users` | User accounts | `email`, `password_hash`, `role`, `name` |
| `user_content` | Uploaded content | `user_id`, `title`, `file_path`, `content_type` |
| `conversations` | Message threads | `participants`, `last_message`, `updated_at` |
| `messages` | Individual messages | `conversation_id`, `sender_id`, `content` |
| `notifications` | User notifications | `user_id`, `type`, `message`, `read` |
| `content_comments` | Content comments | `content_id`, `user_id`, `comment`, `created_at` |
| `platform_credentials` | Social platform creds | `user_id`, `platform`, `credentials` |
| `distribution_hub_content` | Hub content items | `user_id`, `title`, `metadata`, `rights` |
| `distribution_hub_deliveries` | Delivery records | `content_id`, `platform`, `status`, `batch_id` |
| `anomaly_alerts` | Metric anomalies | `platform`, `metric`, `z_score`, `severity` |
| `audience_analytics` | Demographics data | `user_id`, `age_distribution`, `geo` |
| `revenue_tracking` | Revenue records | `user_id`, `platform`, `amount`, `source` |
| `subscriptions` | User subscriptions | `user_id`, `tier`, `stripe_id`, `status` |

### MongoDB Best Practices

- **Always exclude `_id`** from API responses: `{"_id": 0}` in projections
- **Use `str(doc["_id"])`** if you must return an ID (convert ObjectId to string)
- **DateTime**: Use `datetime.now(timezone.utc)` — never `datetime.utcnow()`
- **Indexes**: Created in `startup.py` on application boot

---

## Key Conventions

### Backend

- **Route handlers should be thin** — delegate to service functions
- **All routes are prefixed with `/api`** — enforced by the API router in `server.py`
- **Auth dependency**: Use `Depends(get_current_user)` for protected endpoints
- **Error handling**: Raise `HTTPException` with appropriate status codes
- **File naming**: `feature_routes.py` for routes, `feature_service.py` for services

### Frontend

- **Named exports** for components: `export const MyComponent = () => {}`
- **Default exports** for pages: `export default function MyPage() {}`
- **data-testid** on every interactive element (buttons, inputs, links, etc.)
- **Shadcn/UI** for all UI primitives — check `/app/frontend/src/components/ui/`

### Git & Code Style

- Commit messages: `feat:`, `fix:`, `refactor:`, `docs:`, `test:` prefixes
- No hardcoded URLs, ports, or credentials — use environment variables
- No `console.log` in production code (use proper logging)

---

## Common Development Workflows

### Adding a New Feature (Full Stack)

1. **Backend**: Create route in `routes/` → create service in `services/` → wire in `server.py`
2. **Frontend**: Create page in `pages/` → add route in `App.js` → add nav link
3. **Test**: `curl` the API → check the frontend page → run test suite

### Debugging a Backend Issue

```bash
# Check backend logs
tail -n 100 /var/log/supervisor/backend.err.log

# Check if backend is running
sudo supervisorctl status backend

# Test a specific endpoint
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
curl -s "$API_URL/api/health" | python3 -m json.tool
```

### Debugging a Frontend Issue

```bash
# Check frontend logs
tail -n 100 /var/log/supervisor/frontend.err.log

# Rebuild after dependency changes
cd /app/frontend && yarn install
sudo supervisorctl restart frontend
```

---

## Testing

### Backend Testing

```bash
# Run all backend tests
cd /app/backend && python -m pytest tests/ -v

# Test a specific endpoint with curl
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@bigmannentertainment.com","password":"Test1234!"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -s "$API_URL/api/user-content/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Test Reports

Automated test reports are stored in `/app/test_reports/iteration_*.json`.

---

## Environment Variables

### Backend (`/app/backend/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URL` | MongoDB connection string | Yes |
| `DB_NAME` | Database name | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `STRIPE_SECRET_KEY` | Stripe API secret key | For payments |
| `AWS_ACCESS_KEY_ID` | AWS access key | For AWS features |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | For AWS features |
| `GOOGLE_AI_API_KEY` | Google Generative AI key | For AI features |
| `APP_BASE_URL` | Public app URL for content delivery | For distribution |

### Frontend (`/app/frontend/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `REACT_APP_BACKEND_URL` | Backend API base URL | Yes |
| `REACT_APP_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | For payments |
| `REACT_APP_PAYPAL_CLIENT_ID` | PayPal client ID | For payments |

> **Important**: Never commit `.env` files. Never add default/fallback values for credentials.

---

## Deployment

### Preview Environment (Emergent)

- Services are managed by `supervisord`
- Backend: port 8001, Frontend: port 3000
- Kubernetes ingress routes `/api/*` → backend, everything else → frontend
- Hot reload is enabled — code changes auto-restart services
- Only restart supervisor for `.env` or dependency changes

### Production

- See `/app/docs/DEPLOYMENT_GUIDE.md` for full production deployment instructions
- AWS infrastructure managed via CDK (`/app/aws-infrastructure/`) or Terraform (`/app/infra-terraform/`)

---

## Troubleshooting

### Backend won't start

```bash
# Check error logs
tail -n 50 /var/log/supervisor/backend.err.log

# Common causes:
# 1. Missing Python dependency → pip install -r requirements.txt
# 2. Import error after moving files → check sys.path in server.py
# 3. MongoDB not reachable → verify MONGO_URL in .env
```

### Frontend shows blank page

```bash
# Check frontend logs
tail -n 50 /var/log/supervisor/frontend.err.log

# Common causes:
# 1. Missing node module → cd /app/frontend && yarn install
# 2. REACT_APP_BACKEND_URL not set → check frontend/.env
# 3. Build error → check logs for JSX/import errors
```

### API returns 404

- Ensure the route is prefixed with `/api`
- Check that the router is included in `server.py` or `router_setup.py`
- Verify the endpoint path doesn't have a double `/api/api/` prefix

### MongoDB ObjectId errors

```
TypeError: Object of type ObjectId is not JSON serializable
```

Fix: Add `{"_id": 0}` to your MongoDB projection, or convert with `str(doc["_id"])`.

---

## Quick Reference Card

```
Backend start:       sudo supervisorctl restart backend
Frontend start:      sudo supervisorctl restart frontend
Backend logs:        tail -f /var/log/supervisor/backend.err.log
Frontend logs:       tail -f /var/log/supervisor/frontend.err.log
Swagger UI:          {APP_URL}/api/docs
ReDoc:               {APP_URL}/api/redoc
OpenAPI JSON:        {APP_URL}/api/openapi.json
Install backend dep: pip install <pkg> && pip freeze > requirements.txt
Install frontend dep: cd /app/frontend && yarn add <pkg>
Run backend tests:   cd /app/backend && python -m pytest tests/ -v
```

---

*Last updated: February 2026*
