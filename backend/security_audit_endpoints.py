"""
Security Audit API Endpoints
"""

from fastapi import APIRouter, Query
from typing import Optional

from security_audit_service import get_security_audit_service

router = APIRouter(prefix="/security", tags=["Security Audit"])


@router.get("/health")
async def security_health():
    return {"status": "healthy", "service": "Security Audit Monitor"}


@router.get("/audit")
async def run_security_audit(force: bool = Query(False, description="Force fresh audit (bypass cache)")):
    """Run a full dependency security audit on frontend and backend."""
    service = get_security_audit_service()
    return await service.run_full_audit(force=force)


@router.get("/audit/frontend")
async def run_frontend_audit():
    """Run audit on frontend (yarn) dependencies only."""
    service = get_security_audit_service()
    return await service.run_frontend_audit()


@router.get("/audit/backend")
async def run_backend_audit():
    """Run audit on backend (pip) dependencies only."""
    service = get_security_audit_service()
    return await service.run_backend_audit()


@router.get("/audit/history")
async def get_audit_history(limit: int = Query(20, ge=1, le=100)):
    """Get previous audit results."""
    service = get_security_audit_service()
    return await service.get_audit_history(limit=limit)
