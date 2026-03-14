"""AWS WorkMail & Pinpoint routes - Business email + marketing campaigns."""
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
_pp_svc = None


def _workmail():
    global _wm_svc
    if _wm_svc is None:
        from services.workmail_service import WorkMailService
        _wm_svc = WorkMailService()
    return _wm_svc


def _pinpoint():
    global _pp_svc
    if _pp_svc is None:
        from services.pinpoint_service import PinpointService
        _pp_svc = PinpointService()
    return _pp_svc


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


class CreatePinpointAppRequest(BaseModel):
    name: str


class CreateSegmentRequest(BaseModel):
    application_id: str
    name: str


class CreateCampaignRequest(BaseModel):
    application_id: str
    name: str
    segment_id: str
    description: str = ""
    email_subject: str = ""
    email_html_body: str = ""
    email_from: str = ""


class SendEmailRequest(BaseModel):
    application_id: str
    to_address: str
    subject: str
    html_body: str
    from_address: str


class SendSmsRequest(BaseModel):
    application_id: str
    phone_number: str
    body: str
    message_type: str = "TRANSACTIONAL"


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def comms_status(current_user: User = Depends(get_current_user)):
    """Overall status of WorkMail + Pinpoint."""
    wm = _workmail()
    pp = _pinpoint()

    wm_status = wm.get_status()
    pp_status = pp.get_status()

    wm_users = await db.workmail_users.count_documents({"user_id": current_user.id})
    pp_apps = await db.pinpoint_apps.count_documents({"user_id": current_user.id})

    return {
        "workmail": {**wm_status, "total_users": wm_users},
        "pinpoint": {**pp_status, "total_apps": pp_apps},
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
#  PINPOINT - Applications
# ══════════════════════════════════════════════════════════════════
@router.get("/pinpoint/applications")
async def list_pinpoint_apps(current_user: User = Depends(get_current_user)):
    """List Pinpoint applications (projects)."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        apps = pp.list_applications()
        return {"applications": apps, "total": len(apps)}
    except Exception as e:
        logger.error(f"List apps error: {e}")
        raise HTTPException(500, f"Failed to list applications: {str(e)}")


@router.post("/pinpoint/applications")
async def create_pinpoint_app(
    body: CreatePinpointAppRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a Pinpoint application."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        result = pp.create_application(
            body.name,
            tags={"user_id": current_user.id, "Project": "BigMannEntertainment"},
        )
        doc = {**result, "user_id": current_user.id}
        await db.pinpoint_apps.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Create app error: {e}")
        raise HTTPException(500, f"Failed to create application: {str(e)}")


@router.get("/pinpoint/applications/{application_id}")
async def get_pinpoint_app(application_id: str, current_user: User = Depends(get_current_user)):
    """Get Pinpoint application details."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        return pp.get_application(application_id)
    except Exception as e:
        raise HTTPException(404, f"Application not found: {str(e)}")


@router.delete("/pinpoint/applications/{application_id}")
async def delete_pinpoint_app(application_id: str, current_user: User = Depends(get_current_user)):
    """Delete a Pinpoint application."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    success = pp.delete_application(application_id)
    if success:
        await db.pinpoint_apps.delete_one({"application_id": application_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete application")


# ══════════════════════════════════════════════════════════════════
#  PINPOINT - Segments
# ══════════════════════════════════════════════════════════════════
@router.get("/pinpoint/segments/{application_id}")
async def list_segments(application_id: str, current_user: User = Depends(get_current_user)):
    """List segments for a Pinpoint application."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        segments = pp.list_segments(application_id)
        return {"segments": segments, "total": len(segments)}
    except Exception as e:
        if "ForbiddenException" in str(e) or "deprecated" in str(e).lower():
            return {"segments": [], "total": 0, "deprecated": True, "message": "Pinpoint engagement features (segments) are being deprecated by AWS. Consider using Amazon Connect."}
        logger.error(f"List segments error: {e}")
        raise HTTPException(500, f"Failed to list segments: {str(e)}")


@router.post("/pinpoint/segments")
async def create_segment(
    body: CreateSegmentRequest,
    current_user: User = Depends(get_current_user),
):
    """Create an audience segment."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        result = pp.create_segment(body.application_id, body.name)
        doc = {**result, "user_id": current_user.id}
        await db.pinpoint_segments.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        if "ForbiddenException" in str(e) or "deprecated" in str(e).lower():
            raise HTTPException(410, "Pinpoint segment creation is deprecated by AWS. Consider using Amazon Connect for engagement capabilities.")
        logger.error(f"Create segment error: {e}")
        raise HTTPException(500, f"Failed to create segment: {str(e)}")


@router.delete("/pinpoint/segments/{application_id}/{segment_id}")
async def delete_segment(
    application_id: str, segment_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a Pinpoint segment."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    success = pp.delete_segment(application_id, segment_id)
    if success:
        await db.pinpoint_segments.delete_one({"segment_id": segment_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete segment")


# ══════════════════════════════════════════════════════════════════
#  PINPOINT - Campaigns
# ══════════════════════════════════════════════════════════════════
@router.get("/pinpoint/campaigns/{application_id}")
async def list_campaigns(application_id: str, current_user: User = Depends(get_current_user)):
    """List campaigns for a Pinpoint application."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        campaigns = pp.list_campaigns(application_id)
        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        if "ForbiddenException" in str(e) or "deprecated" in str(e).lower():
            return {"campaigns": [], "total": 0, "deprecated": True, "message": "Pinpoint engagement features (campaigns) are being deprecated by AWS. Consider using Amazon Connect."}
        logger.error(f"List campaigns error: {e}")
        raise HTTPException(500, f"Failed to list campaigns: {str(e)}")


@router.post("/pinpoint/campaigns")
async def create_campaign(
    body: CreateCampaignRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a marketing campaign."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        message_config = {}
        if body.email_subject and body.email_html_body:
            message_config["EmailMessage"] = {
                "Title": body.email_subject,
                "HtmlBody": body.email_html_body,
                "FromAddress": body.email_from or "noreply@bigmannentertainment.com",
            }

        result = pp.create_campaign(
            application_id=body.application_id,
            name=body.name,
            segment_id=body.segment_id,
            message_config=message_config,
            description=body.description,
        )
        doc = {**result, "user_id": current_user.id}
        await db.pinpoint_campaigns.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Create campaign error: {e}")
        raise HTTPException(500, f"Failed to create campaign: {str(e)}")


@router.get("/pinpoint/campaigns/{application_id}/{campaign_id}")
async def get_campaign(
    application_id: str, campaign_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get campaign details."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        return pp.get_campaign(application_id, campaign_id)
    except Exception as e:
        raise HTTPException(404, f"Campaign not found: {str(e)}")


@router.delete("/pinpoint/campaigns/{application_id}/{campaign_id}")
async def delete_campaign(
    application_id: str, campaign_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a campaign."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    success = pp.delete_campaign(application_id, campaign_id)
    if success:
        await db.pinpoint_campaigns.delete_one({"campaign_id": campaign_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete campaign")


# ══════════════════════════════════════════════════════════════════
#  PINPOINT - Direct Messaging
# ══════════════════════════════════════════════════════════════════
@router.post("/pinpoint/send-email")
async def send_email(
    body: SendEmailRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a direct email via Pinpoint."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        result = pp.send_email_message(
            body.application_id, body.to_address,
            body.subject, body.html_body, body.from_address,
        )
        return result
    except Exception as e:
        logger.error(f"Send email error: {e}")
        raise HTTPException(500, f"Failed to send email: {str(e)}")


@router.post("/pinpoint/send-sms")
async def send_sms(
    body: SendSmsRequest,
    current_user: User = Depends(get_current_user),
):
    """Send an SMS message via Pinpoint."""
    pp = _pinpoint()
    if not pp.available:
        raise HTTPException(503, "Pinpoint not available")
    try:
        result = pp.send_sms_message(
            body.application_id, body.phone_number,
            body.body, body.message_type,
        )
        return result
    except Exception as e:
        logger.error(f"Send SMS error: {e}")
        raise HTTPException(500, f"Failed to send SMS: {str(e)}")
