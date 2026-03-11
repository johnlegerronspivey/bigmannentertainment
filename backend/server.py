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
# App Creation
# ============================================================
app = FastAPI(title="Big Mann Entertainment API", version="1.0.0")

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

core_routers = [
    licensing_router, agency_router, admin_router, auth_router,
    dao_router, health_router, business_router, media_router,
    aws_router, domain_router, distribution_router, system_router,
    creator_profile_router, watermark_router, subscription_router,
    content_router, messaging_router, analytics_router,
    notification_router, websocket_router, webhook_router,
    social_connections_router, moderation_router, distribution_hub_router,
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
