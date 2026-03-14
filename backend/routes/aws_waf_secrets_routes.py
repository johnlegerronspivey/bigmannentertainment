"""AWS WAF & Secrets Manager routes - Security hardening."""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from config.database import db
from auth.service import get_current_user
from models.core import User
from datetime import datetime, timezone

router = APIRouter(prefix="/aws-security", tags=["AWS Security"])
logger = logging.getLogger(__name__)

# Lazy-init services
_waf_svc = None
_sm_svc = None


def _waf():
    global _waf_svc
    if _waf_svc is None:
        from services.waf_service import WAFService
        _waf_svc = WAFService()
    return _waf_svc


def _secrets():
    global _sm_svc
    if _sm_svc is None:
        from services.secrets_manager_service import SecretsManagerService
        _sm_svc = SecretsManagerService()
    return _sm_svc


# ── Pydantic models ──────────────────────────────────────────────
class CreateWebACLRequest(BaseModel):
    name: str
    scope: str = "REGIONAL"
    default_action: str = "allow"
    description: str = ""


class DeleteWebACLRequest(BaseModel):
    name: str
    acl_id: str
    lock_token: str
    scope: str = "REGIONAL"


class CreateIPSetRequest(BaseModel):
    name: str
    addresses: List[str]
    ip_version: str = "IPV4"
    scope: str = "REGIONAL"
    description: str = ""


class DeleteIPSetRequest(BaseModel):
    name: str
    ip_set_id: str
    lock_token: str
    scope: str = "REGIONAL"


class CreateSecretRequest(BaseModel):
    name: str
    secret_value: str
    description: str = ""
    is_json: bool = False


class UpdateSecretRequest(BaseModel):
    secret_value: str
    description: Optional[str] = None


class RotateSecretRequest(BaseModel):
    rotation_lambda_arn: str = ""
    days: int = 30


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def security_status(current_user: User = Depends(get_current_user)):
    """Overall status of WAF + Secrets Manager."""
    waf = _waf()
    sm = _secrets()

    waf_status = waf.get_status()
    sm_status = sm.get_status()

    waf_acls = await db.waf_web_acls.count_documents({"user_id": current_user.id})
    sm_secrets = await db.managed_secrets.count_documents({"user_id": current_user.id})

    return {
        "waf": {**waf_status, "total_acls": waf_acls},
        "secrets_manager": {**sm_status, "total_secrets": sm_secrets},
    }


# ══════════════════════════════════════════════════════════════════
#  WAF - Web ACLs
# ══════════════════════════════════════════════════════════════════
@router.get("/waf/web-acls")
async def list_web_acls(
    scope: str = Query("REGIONAL", description="REGIONAL or CLOUDFRONT"),
    current_user: User = Depends(get_current_user),
):
    """List Web ACLs."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        acls = waf.list_web_acls(scope=scope)
        return {"web_acls": acls, "total": len(acls)}
    except Exception as e:
        logger.error(f"List web ACLs error: {e}")
        raise HTTPException(500, f"Failed to list web ACLs: {str(e)}")


@router.get("/waf/web-acls/{acl_id}")
async def get_web_acl(
    acl_id: str,
    name: str = Query(..., description="Web ACL name"),
    scope: str = Query("REGIONAL"),
    current_user: User = Depends(get_current_user),
):
    """Get Web ACL details."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        return waf.get_web_acl(name, acl_id, scope)
    except Exception as e:
        raise HTTPException(404, f"Web ACL not found: {str(e)}")


@router.post("/waf/web-acls")
async def create_web_acl(
    body: CreateWebACLRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a Web ACL."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        result = waf.create_web_acl(
            body.name, body.scope, body.default_action, body.description
        )
        doc = {**result, "user_id": current_user.id, "scope": body.scope}
        await db.waf_web_acls.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Create web ACL error: {e}")
        raise HTTPException(500, f"Failed to create web ACL: {str(e)}")


@router.delete("/waf/web-acls")
async def delete_web_acl(
    body: DeleteWebACLRequest,
    current_user: User = Depends(get_current_user),
):
    """Delete a Web ACL."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    success = waf.delete_web_acl(body.name, body.acl_id, body.lock_token, body.scope)
    if success:
        await db.waf_web_acls.delete_one({"id": body.acl_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete web ACL")


# ══════════════════════════════════════════════════════════════════
#  WAF - IP Sets
# ══════════════════════════════════════════════════════════════════
@router.get("/waf/ip-sets")
async def list_ip_sets(
    scope: str = Query("REGIONAL"),
    current_user: User = Depends(get_current_user),
):
    """List IP sets."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        sets = waf.list_ip_sets(scope=scope)
        return {"ip_sets": sets, "total": len(sets)}
    except Exception as e:
        logger.error(f"List IP sets error: {e}")
        raise HTTPException(500, f"Failed to list IP sets: {str(e)}")


@router.get("/waf/ip-sets/{ip_set_id}")
async def get_ip_set(
    ip_set_id: str,
    name: str = Query(..., description="IP set name"),
    scope: str = Query("REGIONAL"),
    current_user: User = Depends(get_current_user),
):
    """Get IP set details."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        return waf.get_ip_set(name, ip_set_id, scope)
    except Exception as e:
        raise HTTPException(404, f"IP set not found: {str(e)}")


@router.post("/waf/ip-sets")
async def create_ip_set(
    body: CreateIPSetRequest,
    current_user: User = Depends(get_current_user),
):
    """Create an IP set."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        result = waf.create_ip_set(
            body.name, body.addresses, body.ip_version, body.scope, body.description
        )
        doc = {**result, "user_id": current_user.id}
        await db.waf_ip_sets.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Create IP set error: {e}")
        raise HTTPException(500, f"Failed to create IP set: {str(e)}")


@router.delete("/waf/ip-sets")
async def delete_ip_set(
    body: DeleteIPSetRequest,
    current_user: User = Depends(get_current_user),
):
    """Delete an IP set."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    success = waf.delete_ip_set(body.name, body.ip_set_id, body.lock_token, body.scope)
    if success:
        await db.waf_ip_sets.delete_one({"id": body.ip_set_id})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete IP set")


# ══════════════════════════════════════════════════════════════════
#  WAF - Rule Groups & Managed Rules
# ══════════════════════════════════════════════════════════════════
@router.get("/waf/rule-groups")
async def list_rule_groups(
    scope: str = Query("REGIONAL"),
    current_user: User = Depends(get_current_user),
):
    """List custom rule groups."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        groups = waf.list_rule_groups(scope=scope)
        return {"rule_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List rule groups error: {e}")
        raise HTTPException(500, f"Failed to list rule groups: {str(e)}")


@router.get("/waf/managed-rules")
async def list_managed_rules(
    scope: str = Query("REGIONAL"),
    current_user: User = Depends(get_current_user),
):
    """List AWS-managed rule groups available."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        groups = waf.list_available_managed_rule_groups(scope=scope)
        return {"managed_rule_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List managed rules error: {e}")
        raise HTTPException(500, f"Failed to list managed rules: {str(e)}")


@router.get("/waf/web-acls/{acl_id}/resources")
async def list_acl_resources(
    acl_id: str,
    name: str = Query(...),
    scope: str = Query("REGIONAL"),
    current_user: User = Depends(get_current_user),
):
    """List resources associated with a Web ACL."""
    waf = _waf()
    if not waf.available:
        raise HTTPException(503, "WAF not available")
    try:
        acl = waf.get_web_acl(name, acl_id, scope)
        resources = waf.list_resources_for_web_acl(acl["arn"])
        return {"resources": resources, "total": len(resources)}
    except Exception as e:
        logger.error(f"List ACL resources error: {e}")
        raise HTTPException(500, f"Failed to list resources: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  SECRETS MANAGER - Secrets
# ══════════════════════════════════════════════════════════════════
@router.get("/secrets")
async def list_secrets(current_user: User = Depends(get_current_user)):
    """List secrets."""
    sm = _secrets()
    if not sm.available:
        raise HTTPException(503, "Secrets Manager not available")
    try:
        secrets = sm.list_secrets()
        return {"secrets": secrets, "total": len(secrets)}
    except Exception as e:
        logger.error(f"List secrets error: {e}")
        raise HTTPException(500, f"Failed to list secrets: {str(e)}")


@router.get("/secrets/{secret_name:path}")
async def describe_secret(secret_name: str, current_user: User = Depends(get_current_user)):
    """Get secret metadata (not the value)."""
    sm = _secrets()
    if not sm.available:
        raise HTTPException(503, "Secrets Manager not available")
    try:
        return sm.describe_secret(secret_name)
    except Exception as e:
        raise HTTPException(404, f"Secret not found: {str(e)}")


@router.get("/secrets/{secret_name:path}/info")
async def get_secret_info(secret_name: str, current_user: User = Depends(get_current_user)):
    """Get secret value info (key count, type) without exposing the actual value."""
    sm = _secrets()
    if not sm.available:
        raise HTTPException(503, "Secrets Manager not available")
    try:
        return sm.get_secret_value(secret_name)
    except Exception as e:
        raise HTTPException(404, f"Secret not found: {str(e)}")


@router.post("/secrets")
async def create_secret(
    body: CreateSecretRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new secret."""
    sm = _secrets()
    if not sm.available:
        raise HTTPException(503, "Secrets Manager not available")
    try:
        result = sm.create_secret(
            body.name, body.secret_value, body.description, body.is_json
        )
        doc = {**result, "user_id": current_user.id}
        await db.managed_secrets.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Create secret error: {e}")
        raise HTTPException(500, f"Failed to create secret: {str(e)}")


@router.put("/secrets/{secret_name:path}")
async def update_secret(
    secret_name: str,
    body: UpdateSecretRequest,
    current_user: User = Depends(get_current_user),
):
    """Update a secret's value."""
    sm = _secrets()
    if not sm.available:
        raise HTTPException(503, "Secrets Manager not available")
    try:
        result = sm.update_secret(secret_name, body.secret_value, body.description)
        return result
    except Exception as e:
        logger.error(f"Update secret error: {e}")
        raise HTTPException(500, f"Failed to update secret: {str(e)}")


@router.delete("/secrets/{secret_name:path}")
async def delete_secret(
    secret_name: str,
    force: bool = Query(False, description="Force delete without recovery window"),
    current_user: User = Depends(get_current_user),
):
    """Delete a secret (7-day recovery window by default)."""
    sm = _secrets()
    if not sm.available:
        raise HTTPException(503, "Secrets Manager not available")
    success = sm.delete_secret(secret_name, force)
    if success:
        await db.managed_secrets.delete_one({"name": secret_name})
        return {"deleted": True, "recovery_window": "none" if force else "7 days"}
    raise HTTPException(500, "Failed to delete secret")


@router.post("/secrets/{secret_name:path}/rotate")
async def rotate_secret(
    secret_name: str,
    body: RotateSecretRequest,
    current_user: User = Depends(get_current_user),
):
    """Trigger secret rotation."""
    sm = _secrets()
    if not sm.available:
        raise HTTPException(503, "Secrets Manager not available")
    try:
        result = sm.rotate_secret(secret_name, body.rotation_lambda_arn, body.days)
        return result
    except Exception as e:
        logger.error(f"Rotate secret error: {e}")
        raise HTTPException(500, f"Failed to rotate secret: {str(e)}")
