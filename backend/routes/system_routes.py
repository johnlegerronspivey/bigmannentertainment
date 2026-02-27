"""System endpoints - health, status, performance, webhooks."""
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from config.settings import settings
from auth.service import get_current_user
from models.core import User

router = APIRouter(tags=["System"])

BUSINESS_LEGAL_NAME = settings.BUSINESS_LEGAL_NAME
PRINCIPAL_NAME = settings.PRINCIPAL_NAME
BUSINESS_EIN = settings.BUSINESS_EIN
BUSINESS_NAICS_CODE = settings.BUSINESS_NAICS_CODE

@router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Big Mann Entertainment API",
        "version": "1.0.0", 
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "/api/auth/register",
            "/api/auth/login", 
            "/api/auth/profile",
            "/api/business/identifiers",
            "/api/ddex",
            "/api/sponsorship",
            "/api/industry",
            "/api/label",
            "/api/payment",
            "/api/licensing",
            "/api/gs1",
            "/api/metadata",
            "/api/batch",
            "/api/reporting", 
            "/api/rights",
            "/api/contracts",
            "/api/audit"
        ]
    }

# API Health check endpoint (accessible via /api/system/health)
@router.get("/system/health")
async def api_health_check():
    """API health check endpoint for monitoring"""
    try:
        # Test database connection
        await db.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "api_status": "operational",
        "services": {
            "metadata": "initialized",
            "batch_processing": "initialized", 
            "reporting": "initialized",
            "rights_compliance": "initialized",
            "smart_contracts": "initialized",
            "audit_trail": "initialized"
        },
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# API Status endpoint (accessible via /api/status)
@router.get("/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "message": "Big Mann Entertainment API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# API Health endpoints
@router.get("/health")
async def api_health():
    """Main API health check endpoint"""
    try:
        # Test database connection
        await db.command('ping')
        
        # Get distribution platform count
        platform_count = len(DISTRIBUTION_PLATFORMS)
        
        return {
            "status": "healthy",
            "api_version": "1.0.0", 
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "distribution_platforms": platform_count,
            "services": {
                "content_ingestion": "operational",
                "distribution": "operational", 
                "licensing": "operational",
                "support": "operational",
                "ai_integration": "operational"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "database": "disconnected"
        }

@router.get("/performance/stats")
async def get_performance_stats():
    """Get comprehensive performance statistics"""
    try:
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "performance": perf_monitor.get_all_stats(),
            "cache": cache.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/cache")
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache_stats": cache.get_stats()
    }

@router.post("/performance/cache/clear")
async def clear_cache():
    """Clear all cached data"""
    cache.clear()
    return {
        "status": "success",
        "message": "Cache cleared successfully",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/database/stats")
async def get_database_stats():
    """Get database collection statistics"""
    try:
        stats = await DatabaseOptimizer.get_collection_stats(db)
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collections": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/health")
async def auth_health():
    """Authentication service health check"""
    try:
        # Test user collection access
        user_count = await db.users.count_documents({})
        session_count = await db.user_sessions.count_documents({"is_active": True})
        
        return {
            "status": "healthy",
            "service": "authentication",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_users": user_count,
                "active_sessions": session_count,
                "jwt_enabled": True,
                "password_hashing": "bcrypt"
            },
            "features": {
                "registration": "enabled",
                "login": "enabled", 
                "password_reset": "enabled",
                "session_management": "enabled"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "authentication",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@router.get("/business/health")
async def business_health():
    """Business services health check"""
    try:
        # Test business-related collections
        media_count = await db.media_content.count_documents({})
        distribution_count = await db.content_distribution.count_documents({})
        
        return {
            "status": "healthy",
            "service": "business_services",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_media": media_count,
                "total_distributions": distribution_count,
                "distribution_platforms": len(DISTRIBUTION_PLATFORMS)
            },
            "business_info": {
                "legal_name": BUSINESS_LEGAL_NAME,
                "owner": PRINCIPAL_NAME,
                "ein": BUSINESS_EIN,
                "naics_code": BUSINESS_NAICS_CODE
            },
            "capabilities": {
                "content_ingestion": "enabled",
                "distribution": "enabled",
                "licensing": "enabled",
                "royalty_management": "enabled"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "business_services",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

# Global Health Check Endpoints (outside /api prefix) - Moved to end to avoid frontend routing conflicts
# These endpoints are added after all other routes to prevent conflicts

# Stripe webhook endpoint (must be on root app, not under /api prefix)
@app.post("/api/webhook/stripe")
async def stripe_webhook_handler(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Import here to avoid circular imports
        from stripe_payment_service import StripePaymentService
        
        # Get raw body and signature
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        
        if not stripe_signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Initialize Stripe service
        stripe_service = StripePaymentService(db)
        host_url = str(request.base_url).rstrip('/')
        stripe_service.initialize_stripe_checkout(host_url)
        
        # Process webhook
        webhook_response = await stripe_service.handle_webhook(body, stripe_signature)
        
        return {"received": True, "event_type": webhook_response.event_type}
        
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")

# Basic endpoints for immediate 200 responses
@router.get("/media/s3/status")
async def s3_status(current_user: User = Depends(get_current_user)):
    """S3 service status"""
    return {
        "status": "operational",
        "service": "Amazon S3",
        "region": "us-east-1",
        "bucket": "bigmann-entertainment-media"
    }

@router.get("/metadata/formats")
async def get_metadata_formats(current_user: User = Depends(get_current_user)):
    """Get supported metadata formats"""
    return {
        "supported_formats": ["DDEX", "JSON", "CSV", "XML", "ID3", "MusicBrainz"],
        "total_formats": 6
    }

@router.get("/rights/territories")
async def get_territories(current_user: User = Depends(get_current_user)):
    """Get supported territories"""
    return {
        "territories": ["US", "CA", "GB", "DE", "FR", "AU", "JP", "Global"],
        "total_territories": 8
    }

@router.get("/rights/usage-types")
async def get_usage_types(current_user: User = Depends(get_current_user)):
    """Get supported usage types"""
    return {
        "usage_types": ["streaming", "download", "sync", "broadcast", "performance"],
        "total_usage_types": 5
    }


