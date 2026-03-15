"""AWS WorkMail & Amazon Connect routes - Business email + Contact center."""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from config.database import db
from auth.service import get_current_user
from models.core import User
from datetime import datetime, timezone

router = APIRouter(prefix="/aws-comms", tags=["AWS Communications"])
logger = logging.getLogger(__name__)

# Lazy-init services
_wm_svc = None
_cn_svc = None


def _workmail():
    global _wm_svc
    if _wm_svc is None:
        from services.workmail_service import WorkMailService
        _wm_svc = WorkMailService()
    return _wm_svc


def _connect():
    global _cn_svc
    if _cn_svc is None:
        from services.connect_service import ConnectService
        _cn_svc = ConnectService()
    return _cn_svc


# ── Pydantic models ──────────────────────────────────────────────
class CreateWorkmailUserRequest(BaseModel):
    organization_id: str
    name: str
    display_name: str
    password: str


class RegisterWorkmailUserRequest(BaseModel):
    organization_id: str
    entity_id: str
    email: str


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def comms_status(current_user: User = Depends(get_current_user)):
    """Overall status of WorkMail + Connect."""
    wm = _workmail()
    cn = _connect()

    wm_status = wm.get_status()
    cn_status = cn.get_status()

    wm_users = await db.workmail_users.count_documents({"user_id": current_user.id})

    return {
        "workmail": {**wm_status, "total_users": wm_users},
        "connect": cn_status,
    }


# ══════════════════════════════════════════════════════════════════
#  WORKMAIL - Organizations
# ══════════════════════════════════════════════════════════════════
@router.get("/workmail/organizations")
async def list_organizations(current_user: User = Depends(get_current_user)):
    """List WorkMail organizations."""
    wm = _workmail()
    if not wm.available:
        raise HTTPException(503, "WorkMail not available")
    try:
        orgs = wm.list_organizations()
        return {"organizations": orgs, "total": len(orgs)}
    except Exception as e:
        logger.error(f"List orgs error: {e}")
        raise HTTPException(500, f"Failed to list organizations: {str(e)}")


@router.get("/workmail/organizations/{organization_id}")
async def describe_organization(organization_id: str, current_user: User = Depends(get_current_user)):
    """Describe a specific WorkMail organization."""
    wm = _workmail()
    if not wm.available:
        raise HTTPException(503, "WorkMail not available")
    try:
        return wm.describe_organization(organization_id)
    except Exception as e:
        raise HTTPException(404, f"Organization not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  WORKMAIL - Users
# ══════════════════════════════════════════════════════════════════
@router.get("/workmail/users")
async def list_workmail_users(
    organization_id: str = Query(..., description="WorkMail Organization ID"),
    current_user: User = Depends(get_current_user),
):
    """List users in a WorkMail organization."""
    wm = _workmail()
    if not wm.available:
        raise HTTPException(503, "WorkMail not available")
    try:
        users = wm.list_users(organization_id)
        return {"users": users, "total": len(users)}
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(500, f"Failed to list users: {str(e)}")


@router.post("/workmail/users")
async def create_workmail_user(
    body: CreateWorkmailUserRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a WorkMail user."""
    wm = _workmail()
    if not wm.available:
        raise HTTPException(503, "WorkMail not available")
    try:
        result = wm.create_user(
            body.organization_id, body.name, body.display_name, body.password
        )
        doc = {**result, "user_id": current_user.id, "organization_id": body.organization_id}
        await db.workmail_users.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Create user error: {e}")
        raise HTTPException(500, f"Failed to create user: {str(e)}")


@router.post("/workmail/users/register")
async def register_workmail_user(
    body: RegisterWorkmailUserRequest,
    current_user: User = Depends(get_current_user),
):
    """Register a user to WorkMail (assign email)."""
    wm = _workmail()
    if not wm.available:
        raise HTTPException(503, "WorkMail not available")
    success = wm.register_to_workmail(body.organization_id, body.entity_id, body.email)
    if success:
        return {"registered": True, "email": body.email}
    raise HTTPException(500, "Failed to register user")


@router.delete("/workmail/users/{organization_id}/{user_id}")
async def delete_workmail_user(
    organization_id: str, user_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a WorkMail user."""
    wm = _workmail()
    if not wm.available:
        raise HTTPException(503, "WorkMail not available")
    success = wm.delete_user(organization_id, user_id)
    if success:
        await db.workmail_users.delete_one({"user_id_wm": user_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete user")


# ══════════════════════════════════════════════════════════════════
#  WORKMAIL - Groups
# ══════════════════════════════════════════════════════════════════
@router.get("/workmail/groups")
async def list_workmail_groups(
    organization_id: str = Query(..., description="WorkMail Organization ID"),
    current_user: User = Depends(get_current_user),
):
    """List groups in a WorkMail organization."""
    wm = _workmail()
    if not wm.available:
        raise HTTPException(503, "WorkMail not available")
    try:
        groups = wm.list_groups(organization_id)
        return {"groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List groups error: {e}")
        raise HTTPException(500, f"Failed to list groups: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  AMAZON CONNECT - Instances
# ══════════════════════════════════════════════════════════════════
@router.get("/connect/instances")
async def list_connect_instances(current_user: User = Depends(get_current_user)):
    """List Amazon Connect instances."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        instances = cn.list_instances()
        return {"instances": instances, "total": len(instances)}
    except Exception as e:
        logger.error(f"List instances error: {e}")
        raise HTTPException(500, f"Failed to list instances: {str(e)}")


@router.get("/connect/instances/{instance_id}")
async def describe_connect_instance(instance_id: str, current_user: User = Depends(get_current_user)):
    """Describe a Connect instance."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        return cn.describe_instance(instance_id)
    except Exception as e:
        raise HTTPException(404, f"Instance not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  AMAZON CONNECT - Queues
# ══════════════════════════════════════════════════════════════════
@router.get("/connect/queues")
async def list_connect_queues(
    instance_id: str = Query(..., description="Connect Instance ID"),
    current_user: User = Depends(get_current_user),
):
    """List queues for a Connect instance."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        queues = cn.list_queues(instance_id)
        return {"queues": queues, "total": len(queues)}
    except Exception as e:
        logger.error(f"List queues error: {e}")
        raise HTTPException(500, f"Failed to list queues: {str(e)}")


@router.get("/connect/queues/{instance_id}/{queue_id}")
async def describe_connect_queue(
    instance_id: str, queue_id: str,
    current_user: User = Depends(get_current_user),
):
    """Describe a specific queue."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        return cn.describe_queue(instance_id, queue_id)
    except Exception as e:
        raise HTTPException(404, f"Queue not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  AMAZON CONNECT - Contact Flows
# ══════════════════════════════════════════════════════════════════
@router.get("/connect/contact-flows")
async def list_contact_flows(
    instance_id: str = Query(..., description="Connect Instance ID"),
    current_user: User = Depends(get_current_user),
):
    """List contact flows for a Connect instance."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        flows = cn.list_contact_flows(instance_id)
        return {"contact_flows": flows, "total": len(flows)}
    except Exception as e:
        logger.error(f"List contact flows error: {e}")
        raise HTTPException(500, f"Failed to list contact flows: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  AMAZON CONNECT - Hours of Operation
# ══════════════════════════════════════════════════════════════════
@router.get("/connect/hours-of-operation")
async def list_hours_of_operation(
    instance_id: str = Query(..., description="Connect Instance ID"),
    current_user: User = Depends(get_current_user),
):
    """List hours of operation for a Connect instance."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        hours = cn.list_hours_of_operation(instance_id)
        return {"hours_of_operation": hours, "total": len(hours)}
    except Exception as e:
        logger.error(f"List hours error: {e}")
        raise HTTPException(500, f"Failed to list hours of operation: {str(e)}")


@router.get("/connect/hours-of-operation/{instance_id}/{hours_id}")
async def describe_hours_of_op(
    instance_id: str, hours_id: str,
    current_user: User = Depends(get_current_user),
):
    """Describe hours of operation."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        return cn.describe_hours_of_operation(instance_id, hours_id)
    except Exception as e:
        raise HTTPException(404, f"Hours of operation not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  AMAZON CONNECT - Users
# ══════════════════════════════════════════════════════════════════
@router.get("/connect/users")
async def list_connect_users(
    instance_id: str = Query(..., description="Connect Instance ID"),
    current_user: User = Depends(get_current_user),
):
    """List users in a Connect instance."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        users = cn.list_users(instance_id)
        return {"users": users, "total": len(users)}
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(500, f"Failed to list users: {str(e)}")


@router.get("/connect/users/{instance_id}/{user_id}")
async def describe_connect_user(
    instance_id: str, user_id: str,
    current_user: User = Depends(get_current_user),
):
    """Describe a Connect user."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        return cn.describe_user(instance_id, user_id)
    except Exception as e:
        raise HTTPException(404, f"User not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  AMAZON CONNECT - Routing Profiles
# ══════════════════════════════════════════════════════════════════
@router.get("/connect/routing-profiles")
async def list_routing_profiles(
    instance_id: str = Query(..., description="Connect Instance ID"),
    current_user: User = Depends(get_current_user),
):
    """List routing profiles for a Connect instance."""
    cn = _connect()
    if not cn.available:
        raise HTTPException(503, "Amazon Connect not available")
    try:
        profiles = cn.list_routing_profiles(instance_id)
        return {"routing_profiles": profiles, "total": len(profiles)}
    except Exception as e:
        logger.error(f"List routing profiles error: {e}")
        raise HTTPException(500, f"Failed to list routing profiles: {str(e)}")
