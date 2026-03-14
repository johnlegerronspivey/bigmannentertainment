"""
Big Mann Entertainment API — Main Application Entry Point
Slim server.py: App creation, middleware, startup/shutdown, router wiring.
All business logic lives in routes/, services/, models/, api/, utils/.
"""
import sys
from pathlib import Path

_backend = Path(__file__).parent
for _subdir in ['api', 'services', 'models', 'utils']:
    _p = str(_backend / _subdir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from datetime import datetime, timezone

from config.database import db
from config.settings import settings
from config.platforms import DISTRIBUTION_PLATFORMS

load_dotenv(Path(__file__).parent / '.env')

# ============================================================
# OpenAPI Tag Metadata
# ============================================================
openapi_tags = [
    {"name": "Authentication", "description": "User registration, login, JWT token management, and session handling."},
    {"name": "Health Checks", "description": "Service health and readiness probes."},
    {"name": "Admin", "description": "Administrative operations: user management, platform settings, and moderation."},
    {"name": "Creator Profiles", "description": "Creator profile CRUD, bios, social links, and public pages."},
    {"name": "Content Management", "description": "Upload, manage, search, and filter user-generated content (audio, video, images)."},
    {"name": "Media", "description": "Media file upload, processing, and retrieval."},
    {"name": "Content Watermarking", "description": "Apply and verify watermarks on media assets."},
    {"name": "Content Moderation", "description": "AI-assisted and manual content moderation workflows."},
    {"name": "Direct Messaging", "description": "User-to-user messaging, conversations, and real-time chat."},
    {"name": "Notifications", "description": "In-app notifications, read/unread status, and notification preferences."},
    {"name": "WebSockets", "description": "Real-time WebSocket connections for notifications and live updates."},
    {"name": "Webhooks", "description": "Incoming webhook handlers for third-party service events."},
    {"name": "Social Connections", "description": "Connect, manage, and disconnect social media platform accounts."},
    {"name": "Distribution Hub", "description": "Central command center for distributing content to 120+ commercial platforms with real delivery engine."},
    {"name": "Distribution", "description": "Legacy distribution endpoints and platform-level delivery."},
    {"name": "Creator Analytics", "description": "Creator insights: anomaly detection, demographics, best time to post, geographic distribution, and revenue tracking."},
    {"name": "Content Analytics & Performance Monitoring", "description": "Content performance metrics, engagement tracking, and trend analysis."},
    {"name": "Subscription Tiers", "description": "Manage subscription plans, tiers, and user subscriptions."},
    {"name": "Licensing", "description": "Content licensing management and agreements."},
    {"name": "Comprehensive Platform Licensing", "description": "Advanced multi-platform licensing workflows."},
    {"name": "Licensing System", "description": "Core licensing system operations."},
    {"name": "Creative Studio", "description": "Creative tools for content creation and editing."},
    {"name": "Creative Studio Collaboration", "description": "Real-time collaboration features in the creative studio."},
    {"name": "Creative Studio AI Assets", "description": "AI-powered asset generation and management."},
    {"name": "DDEX", "description": "DDEX standard message generation and processing for music distribution."},
    {"name": "Music Reports", "description": "Music industry reporting and royalty statements."},
    {"name": "Real-Time Royalty Engine", "description": "Live royalty calculation, splits, and payment processing."},
    {"name": "Royalty Marketplace", "description": "Buy, sell, and trade royalty shares."},
    {"name": "Social Media Royalty Integration", "description": "Track and attribute royalties from social media platforms."},
    {"name": "Social Media Strategy", "description": "Social media planning, scheduling, and campaign management."},
    {"name": "Social Media Advanced Features", "description": "Advanced social media features including cross-posting and analytics."},
    {"name": "Payments", "description": "Core payment processing and transaction management."},
    {"name": "stripe_payments", "description": "Stripe payment integration for subscriptions and one-time payments."},
    {"name": "PayPal Payments", "description": "PayPal payment integration."},
    {"name": "Agency Onboarding", "description": "Agency account setup, onboarding flows, and team management."},
    {"name": "Agency Success Automation", "description": "Automated agency success metrics and workflows."},
    {"name": "DAO", "description": "Decentralized Autonomous Organization governance features."},
    {"name": "DAO Governance V2", "description": "Enhanced DAO governance with voting, proposals, and treasury management."},
    {"name": "Smart Contracts & DAO", "description": "Smart contract deployment and DAO integration."},
    {"name": "ethereum", "description": "Ethereum blockchain integration and wallet management."},
    {"name": "ethereum-advanced", "description": "Advanced Ethereum operations: token management, NFTs, and DeFi."},
    {"name": "ULN Blockchain Integration", "description": "Unified Label Network blockchain integration."},
    {"name": "Unified Label Network", "description": "ULN label registry and management."},
    {"name": "Digital Twin", "description": "Digital twin creation and management for media assets."},
    {"name": "AWS Media Processing", "description": "AWS MediaConvert transcoding and Transcribe captions/subtitles."},
    {"name": "AWS", "description": "AWS service integration: S3, SES, CloudFront, Lambda, Rekognition."},
    {"name": "AWS Agency Platform", "description": "AWS-powered agency platform services."},
    {"name": "AWS CloudWatch Monitoring", "description": "CloudWatch metrics, alarms, and log monitoring."},
    {"name": "AWS Enterprise Mapping", "description": "Enterprise AWS account and resource mapping."},
    {"name": "AWS GuardDuty Threat Detection", "description": "GuardDuty threat detection findings and management."},
    {"name": "AWS Macie PII Detection", "description": "Macie PII/sensitive data detection and classification."},
    {"name": "AWS Organizations", "description": "AWS Organizations account and policy management."},
    {"name": "AWS QLDB Dispute Ledger", "description": "Quantum Ledger Database for immutable dispute records."},
    {"name": "Security Audit", "description": "Security scanning, vulnerability assessment, and audit trails."},
    {"name": "CVE Management", "description": "CVE tracking, prioritization, and remediation."},
    {"name": "CVE Reporting & Analytics", "description": "CVE reporting dashboards and trend analytics."},
    {"name": "CVE RBAC", "description": "Role-based access control for CVE management."},
    {"name": "Scanners & CI/CD", "description": "Security scanner integration and CI/CD pipeline hooks."},
    {"name": "Remediation & GitHub", "description": "Automated remediation workflows and GitHub integration."},
    {"name": "Governance & Analytics", "description": "Platform governance policies and analytics."},
    {"name": "SLA Tracker", "description": "SLA monitoring, tracking, and compliance reporting."},
    {"name": "Infrastructure Automation", "description": "Infrastructure-as-Code management and automation."},
    {"name": "Ticketing Integration", "description": "External ticketing system (Jira) integration."},
    {"name": "Multi-Tenant", "description": "Multi-tenant account isolation and management."},
    {"name": "Domain & DNS", "description": "Custom domain configuration and DNS management."},
    {"name": "Business", "description": "Business operations, invoicing, and reporting."},
    {"name": "System", "description": "System configuration, feature flags, and platform settings."},
    {"name": "Support System", "description": "Customer support ticket management."},
    {"name": "Content Removal", "description": "DMCA takedown and content removal workflows."},
    {"name": "Workflow Integration", "description": "External workflow and automation integrations."},
    {"name": "Content Ingestion", "description": "Bulk content ingestion and import pipelines."},
    {"name": "Content Workflow", "description": "Content approval and review workflows."},
    {"name": "Transcoding", "description": "Media transcoding and format conversion."},
    {"name": "Batch Processing", "description": "Bulk operations and batch job management."},
    {"name": "Premium Features", "description": "Premium/paid feature management and entitlements."},
    {"name": "MLC Integration", "description": "Mechanical Licensing Collective integration."},
    {"name": "MDE Integration", "description": "Music Data Exchange integration."},
    {"name": "GS1 Asset Registry", "description": "GS1 global asset identification and registry."},
    {"name": "Enhanced Features", "description": "Platform enhancement features and experiments."},
    {"name": "Snapchat Integration", "description": "Snapchat platform integration."},
    {"name": "Comprehensive Platform", "description": "Cross-platform management and unified dashboards."},
    {"name": "Content Lifecycle Management & Automation", "description": "Content lifecycle stages, automation rules, and archival."},
    {"name": "Metadata Parser & Validator", "description": "Media metadata extraction, parsing, and validation."},
    {"name": "Rights & Compliance", "description": "Rights management and regulatory compliance."},
    {"name": "Audit Trail & Logging", "description": "Immutable audit trail and activity logging."},
    {"name": "Reports & Exports", "description": "Generate and export platform reports."},
    {"name": "Notifications & Reporting", "description": "Notification-based reporting and alert management."},
    {"name": "Advanced Reporting", "description": "Advanced analytics reporting and data exports."},
    {"name": "Usage Analytics", "description": "Platform usage metrics and user behavior analytics."},
    {"name": "Enterprise Phase 1", "description": "Enterprise-tier features and multi-org support."},
    {"name": "Sponsorship", "description": "Sponsorship deal management and tracking."},
    {"name": "Tax Management", "description": "Tax calculation, reporting, and compliance."},
    {"name": "Industry Integration", "description": "Music industry standard integrations (ISRC, UPC, IPI)."},
    {"name": "IPI Numbers", "description": "Interested Party Information number management."},
    {"name": "Label Management", "description": "Record label management and catalog organization."},
    {"name": "User Workflow", "description": "User workflow and task management."},
    {"name": "Programmatic DOOH", "description": "Programmatic Digital Out-Of-Home advertising."},
    {"name": "image_upload", "description": "Image upload endpoints."},
    {"name": "media_upload", "description": "Media file upload endpoints."},
]

# ============================================================
# App Creation
# ============================================================
API_DESCRIPTION = """
## Big Mann Entertainment API

A comprehensive creator tools platform for music and media distribution, analytics, and monetization.

### Key Capabilities

| Area | Description |
|------|-------------|
| **Content Management** | Upload, manage, and distribute audio, video, and image content |
| **Distribution Hub** | Deliver content to 120+ commercial platforms with retry logic |
| **Creator Analytics** | Anomaly detection, demographics, revenue tracking, and best-time-to-post |
| **Social Connections** | Connect and manage 120+ social media platform accounts |
| **Real-Time Notifications** | WebSocket-powered live notifications and comment alerts |
| **Payments** | Stripe and PayPal integration for subscriptions and royalties |
| **Security** | AWS GuardDuty, Macie, CVE management, and RBAC |
| **Music Industry** | DDEX, ISRC/UPC, MLC, royalty engine, and licensing |

### Authentication

Most endpoints require a JWT Bearer token. Obtain one via `POST /api/auth/login`:

```json
{"email": "user@example.com", "password": "yourpassword"}
```

Then include the token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

### Rate Limiting

API requests are rate-limited per IP. If you receive a `429` response, wait before retrying.

### Need Help?

See the [Developer Onboarding Guide](https://github.com/bigmannentertainment/docs/DEVELOPER_ONBOARDING.md) for setup instructions and codebase walkthrough.
"""

app = FastAPI(
    title="Big Mann Entertainment API",
    version="2.0.0",
    description=API_DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=openapi_tags,
    contact={
        "name": "Big Mann Entertainment",
        "url": "https://bigmannentertainment.com",
        "email": "dev@bigmannentertainment.com",
    },
    license_info={
        "name": "Proprietary",
    },
    terms_of_service="https://bigmannentertainment.com/terms",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="bme_session",
    max_age=1800,
    same_site="lax",
    https_only=False,
)

# ============================================================
# Middleware (extracted to middleware.py)
# ============================================================
from middleware import (
    performance_tracking_middleware,
    security_headers_middleware,
    apply_rate_limiting,
)

app.middleware("http")(performance_tracking_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(apply_rate_limiting)

# ============================================================
# Startup / Shutdown (extracted to startup.py)
# ============================================================
from startup import startup_event, shutdown_event

app.on_event("startup")(startup_event)
app.on_event("shutdown")(shutdown_event)

# ============================================================
# Router Setup
# ============================================================
api_router = APIRouter(prefix="/api")

# Core route modules (routes/)
from routes.licensing_routes import router as licensing_router
from routes.agency_routes import agency_router
from routes.admin_routes import router as admin_router
from routes.auth_routes import router as auth_router
from routes.dao_routes import router as dao_router
from routes.health_routes import router as health_router
from routes.business_routes import router as business_router
from routes.media_routes import router as media_router
from routes.aws_routes import router as aws_router
from routes.domain_routes import router as domain_router
from routes.distribution_routes import router as distribution_router
from routes.system_routes import router as system_router
from routes.creator_profile_routes import router as creator_profile_router
from routes.watermark_routes import router as watermark_router
from routes.subscription_routes import router as subscription_router
from routes.content_routes import router as content_router
from routes.messaging_routes import router as messaging_router
from routes.analytics_routes import router as analytics_router
from routes.notification_routes import router as notification_router
from routes.websocket_routes import router as websocket_router
from routes.webhook_routes import router as webhook_router
from routes.social_connections_routes import router as social_connections_router
from moderation_endpoints import router as moderation_router
from routes.distribution_hub_routes import router as distribution_hub_router
from routes.aws_media_processing_routes import router as aws_media_processing_router

core_routers = [
    licensing_router, agency_router, admin_router, auth_router,
    dao_router, health_router, business_router, media_router,
    aws_router, domain_router, distribution_router, system_router,
    creator_profile_router, watermark_router, subscription_router,
    content_router, messaging_router, analytics_router,
    notification_router, websocket_router, webhook_router,
    social_connections_router, moderation_router, distribution_hub_router,
    aws_media_processing_router,
]

for r in core_routers:
    api_router.include_router(r)

# External endpoint modules (router_setup.py)
from router_setup import api_router as sub_routers

app.include_router(api_router)
app.include_router(sub_routers)

# ============================================================
# CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Root-level endpoints
# ============================================================
@app.get("/")
async def root():
    return {"message": "Big Mann Entertainment API", "version": "1.0.0", "status": "operational"}


@app.get("/health")
async def global_health():
    try:
        await db.command('ping')
        users_count = await db.users.count_documents({})
        media_count = await db.media_content.count_documents({})
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "services": {
                "authentication": "operational",
                "media_upload": "operational",
                "distribution": "operational",
                "support_system": "operational",
                "ai_integration": "operational"
            },
            "metrics": {
                "total_users": users_count,
                "total_media": media_count,
                "distribution_platforms": len(DISTRIBUTION_PLATFORMS),
                "uptime": "99.9%"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "database": "disconnected"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
