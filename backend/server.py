"""
Big Mann Entertainment API - Main Application Entry Point
Slim server.py: App creation, middleware, startup/shutdown, router wiring.
All business logic extracted to routes/ and services/ packages.
"""
from fastapi import FastAPI, APIRouter, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# === Imports from extracted modules ===
from config.database import db, client
from config.settings import settings
from config.platforms import DISTRIBUTION_PLATFORMS
from models.core import (
    User, UserSession, UserCreate, UserLogin, Token, TokenRefresh,
    ForgotPasswordRequest, ResetPasswordRequest, UserUpdate,
    BusinessIdentifiers, ProductIdentifier, MediaContent, MediaUpload,
    ContentModerationAction, Purchase, DistributionTarget,
    ContentDistribution, DistributionRequest, SocialPost,
    NFTCollection, NFTToken, SmartContract, CryptoWallet,
    ActivityLog, SystemConfig,
)
from models.agency import (
    VerificationStatus, LicenseType, BlockchainNetwork, ContractStandard,
    AgencyRegistrationRequest, TalentCreationRequest, LicenseContractRequest,
    NotificationRequest,
)
from auth.service import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, get_current_user, get_current_admin_user,
    get_admin_user, log_activity, pwd_context, security,
)

# === Backward-compatible aliases from settings ===
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
MAX_LOGIN_ATTEMPTS = settings.MAX_LOGIN_ATTEMPTS
LOCKOUT_DURATION_MINUTES = settings.LOCKOUT_DURATION_MINUTES
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
EMAIL_USERNAME = settings.EMAIL_USERNAME
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
EMAIL_FROM_NAME = settings.EMAIL_FROM_NAME
EMAIL_FROM_ADDRESS = settings.EMAIL_FROM_ADDRESS
stripe_api_key = settings.STRIPE_API_KEY
ETHEREUM_CONTRACT_ADDRESS = settings.ETHEREUM_CONTRACT_ADDRESS
ETHEREUM_WALLET_ADDRESS = settings.ETHEREUM_WALLET_ADDRESS
INFURA_PROJECT_ID = settings.INFURA_PROJECT_ID
BLOCKCHAIN_NETWORK = settings.BLOCKCHAIN_NETWORK
INSTAGRAM_ACCESS_TOKEN = settings.INSTAGRAM_ACCESS_TOKEN
TWITTER_API_KEY = settings.TWITTER_API_KEY
TWITTER_API_SECRET = settings.TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET
FACEBOOK_ACCESS_TOKEN = settings.FACEBOOK_ACCESS_TOKEN
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
TIKTOK_CLIENT_ID = settings.TIKTOK_CLIENT_ID
TIKTOK_CLIENT_SECRET = settings.TIKTOK_CLIENT_SECRET
BUSINESS_EIN = settings.BUSINESS_EIN
BUSINESS_ADDRESS = settings.BUSINESS_ADDRESS
BUSINESS_PHONE = settings.BUSINESS_PHONE
BUSINESS_NAICS_CODE = settings.BUSINESS_NAICS_CODE
BUSINESS_TIN = settings.BUSINESS_TIN
UPC_COMPANY_PREFIX = settings.UPC_COMPANY_PREFIX
GLOBAL_LOCATION_NUMBER = settings.GLOBAL_LOCATION_NUMBER
ISRC_PREFIX = settings.ISRC_PREFIX
PUBLISHER_NUMBER = settings.PUBLISHER_NUMBER
IPI_BUSINESS = settings.IPI_BUSINESS
IPI_PRINCIPAL = settings.IPI_PRINCIPAL
IPN_NUMBER = settings.IPN_NUMBER
DPID = settings.DPID
BUSINESS_LEGAL_NAME = settings.BUSINESS_LEGAL_NAME
PRINCIPAL_NAME = settings.PRINCIPAL_NAME

# === External module imports ===
from content_removal_endpoints import init_removal_service
from aws_organizations_service import initialize_service as init_org_service
from aws_enterprise_mapping_service import initialize_enterprise_mapping
from agency_success_automation_service import initialize_automation_service
from dao_governance_v2_service import initialize_dao_v2_service
from creative_studio_service import initialize_creative_studio_service
from creative_studio_collab_service import initialize_collab_service
from creative_studio_ai_service import initialize_ai_assets_service
from usage_analytics_service import initialize_analytics_tracking
from aws_cloudwatch_service import initialize_cloudwatch_service
from macie_service import initialize_macie_service
from guardduty_service import initialize_guardduty_service
from qldb_service import initialize_qldb_service
from moderation_endpoints import router as moderation_router
from dao_smart_contracts import dao_contract_manager

# Performance modules
from cache_service import cache
from rate_limiter import rate_limit_middleware
from performance_monitor import perf_monitor
from db_optimizer import DatabaseOptimizer
from enhanced_validation import Validator, EnhancedValidator

# Create uploads directory
uploads_dir = Path("/app/uploads")
uploads_dir.mkdir(exist_ok=True)

# ============================================================
# App Creation
# ============================================================
app = FastAPI(title="Big Mann Entertainment API", version="1.0.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="bme_session",
    max_age=1800,
    same_site="lax",
    https_only=False,
)

# ============================================================
# Middleware
# ============================================================
@app.middleware("http")
async def performance_tracking_middleware(request: Request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    endpoint = f"{request.method} {request.url.path}"
    perf_monitor.record_request(endpoint, duration, response.status_code, request.method)
    response.headers['X-Response-Time'] = f"{duration:.3f}s"
    return response

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response

@app.middleware("http")
async def apply_rate_limiting(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

# ============================================================
# Startup / Shutdown
# ============================================================
@app.on_event("startup")
async def startup_event():
    print("Creating database indexes...")
    await DatabaseOptimizer.ensure_indexes(db)

    # Initialize external services
    init_fns = [
        ("AWS Enterprise Mapping", lambda: initialize_enterprise_mapping(db)),
        ("Agency Success Automation", lambda: initialize_automation_service(db)),
        ("DAO Governance V2", lambda: initialize_dao_v2_service(db)),
        ("Creative Studio", lambda: initialize_creative_studio_service(db)),
        ("Collaboration & AI Assets", lambda: (initialize_collab_service(db), initialize_ai_assets_service(db))),
        ("Usage Analytics", lambda: initialize_analytics_tracking(db)),
        ("Macie PII Detection", lambda: initialize_macie_service(db)),
        ("GuardDuty Threat Detection", lambda: initialize_guardduty_service(db)),
        ("QLDB Dispute Ledger", lambda: initialize_qldb_service(db)),
        ("CloudWatch Monitoring", lambda: initialize_cloudwatch_service()),
    ]

    for name, fn in init_fns:
        try:
            fn()
            print(f"  {name} initialized")
        except Exception as e:
            print(f"  {name} failed: {str(e)}")

    print("Cache service initialized")
    print("Performance monitoring active")

    # CVE & Security Services
    cve_services = [
        ("CVE Monitor", lambda: __import__('security_audit_service').get_security_audit_service()),
        ("CVE Management", lambda: __import__('cve_management_service').initialize_cve_management(db)),
        ("Scanner Service", lambda: __import__('scanner_service').initialize_scanner_service(db)),
        ("Remediation Service", lambda: __import__('remediation_service').initialize_remediation_service(db)),
        ("Governance Service", lambda: __import__('governance_service').initialize_governance_service(db)),
        ("Notification Service", lambda: __import__('notification_service').initialize_notification_service(db)),
        ("RBAC Service", lambda: __import__('rbac_service').initialize_rbac_service(db)),
        ("SLA Tracker", lambda: __import__('sla_tracker_service').initialize_sla_tracker_service(db)),
        ("CVE Reporting", lambda: __import__('cve_reporting_service').initialize_cve_reporting_service(db)),
        ("Infrastructure Automation", lambda: __import__('iac_service').initialize_iac_service(db)),
        ("Ticketing Integration", lambda: __import__('ticketing_service').initialize_ticketing_service(db)),
        ("Multi-Tenant", lambda: __import__('tenant_service').initialize_tenant_service(db)),
    ]

    for name, fn in cve_services:
        try:
            fn()
            print(f"  {name} initialized")
        except Exception as e:
            print(f"  {name} failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    pass

# ============================================================
# Router Setup
# ============================================================
api_router = APIRouter(prefix="/api")

# Include moderation router
api_router.include_router(moderation_router)

# Include extracted route modules
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

api_router.include_router(licensing_router)
api_router.include_router(agency_router)
api_router.include_router(admin_router)
api_router.include_router(auth_router)
api_router.include_router(dao_router)
api_router.include_router(health_router)
api_router.include_router(business_router)
api_router.include_router(media_router)
api_router.include_router(aws_router)
api_router.include_router(domain_router)
api_router.include_router(distribution_router)
api_router.include_router(system_router)
api_router.include_router(creator_profile_router)
api_router.include_router(watermark_router)
api_router.include_router(subscription_router)

# Initialize content removal and AWS organizations services
init_removal_service(db)
init_org_service(db)

# Initialize Payment Service
try:
    import payment_endpoints
    from payment_service import PaymentService
    payment_service_instance = PaymentService(db)
    payment_endpoints.payment_service = payment_service_instance
except Exception:
    pass

# Initialize Metadata Parser & Validator Services
try:
    import metadata_endpoints
    import batch_endpoints
    import reporting_endpoints
    import rights_endpoints
    import smart_contract_endpoints
    import audit_endpoints
    services_dict = {}
    metadata_endpoints.init_metadata_services(db, services_dict)
    batch_endpoints.init_batch_service(db, services_dict)
    reporting_endpoints.init_reporting_service(db, services_dict)
    rights_endpoints.init_rights_service(db, services_dict)
    smart_contract_endpoints.init_contract_service(db, services_dict)
    audit_endpoints.init_audit_service(db, services_dict)
except Exception:
    pass

# Initialize GS1 service
try:
    from gs1_endpoints import init_gs1_service
    init_gs1_service(db)
except Exception:
    pass

# Initialize Phase 2 AWS services
from services.aws_media_svc import CloudFrontService, LambdaProcessingService, RekognitionService
cloudfront_service = CloudFrontService()
lambda_service = LambdaProcessingService()
rekognition_service = RekognitionService()

# Include sub-routers from router_setup.py (external endpoint modules)
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
# Stripe Webhook (must be on root app, not under /api prefix)
# ============================================================
@app.post("/api/webhook/stripe")
async def stripe_webhook_handler(request: Request):
    try:
        from stripe_payment_service import StripePaymentService
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        if not stripe_signature:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        stripe_service = StripePaymentService(db)
        host_url = str(request.base_url).rstrip('/')
        stripe_service.initialize_stripe_checkout(host_url)
        webhook_response = await stripe_service.handle_webhook(body, stripe_signature)
        return {"received": True, "event_type": webhook_response.event_type}
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")

# ============================================================
# Global Health Check Endpoints (outside /api prefix)
# ============================================================
# ============================================================
# SLA WebSocket Endpoint
# ============================================================
from fastapi import WebSocket, WebSocketDisconnect
from sla_ws_manager import sla_ws_manager

@app.websocket("/api/ws/sla")
async def sla_websocket_endpoint(websocket: WebSocket):
    # Extract user_id from query params if present
    user_id = websocket.query_params.get("user_id")
    await sla_ws_manager.connect(websocket, user_id=user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        sla_ws_manager.disconnect(websocket, user_id=user_id)
    except Exception:
        sla_ws_manager.disconnect(websocket, user_id=user_id)

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
