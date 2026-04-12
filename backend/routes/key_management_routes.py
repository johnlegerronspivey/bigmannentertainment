"""
Key Vault & Secrets Management API routes.
Admin-only endpoints for viewing masked keys, running security scans, and auditing key access.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, HTTPException
from auth.service import get_current_admin_user
from models.core import User
from services.secrets_protection_service import (
    get_vault_summary,
    run_security_scan,
    log_key_access,
    get_audit_log,
    mask_key,
    KEY_REGISTRY,
    detect_key_status,
)

router = APIRouter(prefix="/keys", tags=["Key Vault & Secrets Management"])


@router.get("/vault")
async def get_key_vault(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
):
    """Get all configured keys with masked values and health status. Admin only."""
    await log_key_access(
        user_id=current_user.id,
        key_name="ALL",
        action="vault_view",
        ip_address=request.client.host if request.client else None,
    )
    vault = get_vault_summary()
    return {"status": "success", "data": vault}


@router.get("/security-scan")
async def security_scan(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
):
    """Run a comprehensive security scan on all keys and configuration. Admin only."""
    await log_key_access(
        user_id=current_user.id,
        key_name="ALL",
        action="security_scan",
        ip_address=request.client.host if request.client else None,
    )
    scan = run_security_scan()
    return {"status": "success", "data": scan}


@router.get("/audit-log")
async def get_key_audit_log(
    limit: int = 50,
    key_name: str = None,
    current_user: User = Depends(get_current_admin_user),
):
    """Get key access audit log entries. Admin only."""
    entries = await get_audit_log(limit=limit, key_name=key_name)
    return {
        "status": "success",
        "data": {
            "entries": entries,
            "total": len(entries),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.get("/categories")
async def get_key_categories(
    current_user: User = Depends(get_current_admin_user),
):
    """Get key counts grouped by category."""
    vault = get_vault_summary()
    return {
        "status": "success",
        "data": vault["categories"],
    }


@router.post("/rotate/{key_name}")
async def initiate_key_rotation(
    key_name: str,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
):
    """Log a key rotation event. Actual rotation must be done in .env / secrets manager."""
    if key_name not in KEY_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Key '{key_name}' not found in registry")

    await log_key_access(
        user_id=current_user.id,
        key_name=key_name,
        action="rotation_initiated",
        ip_address=request.client.host if request.client else None,
    )

    return {
        "status": "success",
        "message": f"Rotation event logged for {KEY_REGISTRY[key_name]['label']}. Update the key value in your .env or secrets manager, then restart the service.",
        "key_name": key_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
