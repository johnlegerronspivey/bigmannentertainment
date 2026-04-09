"""AWS External DNS Health Tracking API endpoints."""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from auth.service import get_current_user
from models.core import User
from services.aws_dns_health_service import (
    create_health_check,
    get_health_check_status,
    list_aws_health_checks,
    delete_health_check,
    save_target,
    list_targets,
    get_target,
    update_target_status,
    delete_target,
)
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aws-dns", tags=["AWS DNS Health Tracking"])


class RegisterTargetRequest(BaseModel):
    domain: str
    port: int = 443
    protocol: str = "HTTPS"
    resource_path: str = "/"
    failure_threshold: int = 3
    request_interval: int = 30


@router.post("/targets")
async def register_target(body: RegisterTargetRequest, current_user: User = Depends(get_current_user)):
    """Register a new domain for AWS Route 53 external health tracking."""
    domain = body.domain.strip().lower()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")

    try:
        result = create_health_check(
            domain=domain,
            port=body.port,
            protocol=body.protocol,
            resource_path=body.resource_path,
            failure_threshold=body.failure_threshold,
            request_interval=body.request_interval,
        )
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        logger.error("Route 53 create_health_check failed: %s — %s", code, msg)
        raise HTTPException(status_code=502, detail=f"AWS error: {msg}")

    doc = await save_target(
        user_id=current_user.id,
        domain=domain,
        health_check_id=result["health_check_id"],
        config=result["config"],
    )
    return doc


@router.get("/targets")
async def get_targets(current_user: User = Depends(get_current_user)):
    """List all registered AWS DNS health targets for the current user."""
    targets = await list_targets(current_user.id)
    return {"targets": targets}


@router.get("/targets/{target_id}")
async def get_single_target(target_id: str, current_user: User = Depends(get_current_user)):
    """Get a single registered target."""
    doc = await get_target(current_user.id, target_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Target not found")
    return doc


@router.post("/targets/{target_id}/refresh")
async def refresh_target_status(target_id: str, current_user: User = Depends(get_current_user)):
    """Refresh the health status of a registered target from AWS Route 53."""
    doc = await get_target(current_user.id, target_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Target not found")

    try:
        status = get_health_check_status(doc["health_check_id"])
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        logger.error("Route 53 get_health_check_status failed: %s — %s", code, msg)
        raise HTTPException(status_code=502, detail=f"AWS error: {msg}")

    await update_target_status(target_id, status["overall_status"], status["checkers"])
    return status


@router.delete("/targets/{target_id}")
async def remove_target(target_id: str, current_user: User = Depends(get_current_user)):
    """Delete a registered target and its AWS Route 53 health check."""
    hc_id = await delete_target(current_user.id, target_id)
    if hc_id is None:
        raise HTTPException(status_code=404, detail="Target not found")

    try:
        delete_health_check(hc_id)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        logger.warning("Failed to delete AWS health check %s: %s — %s", hc_id, code, msg)

    return {"status": "deleted", "health_check_id": hc_id}


@router.get("/aws-checks")
async def list_all_aws_checks(current_user: User = Depends(get_current_user)):
    """List all Route 53 health checks in the AWS account (admin view)."""
    try:
        checks = list_aws_health_checks()
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        logger.error("Route 53 list_health_checks failed: %s — %s", code, msg)
        raise HTTPException(status_code=502, detail=f"AWS error: {msg}")
    return {"checks": checks, "count": len(checks)}
