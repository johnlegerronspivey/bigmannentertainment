"""
OWNERSHIP PROTECTION GUARD
============================
IMMUTABLE ownership, identity, and financial protections for
John LeGerron Spivey and Big Mann Entertainment.

These constants and guards CANNOT be overridden, bypassed, or modified
by any user, admin, API call, or automated system. Any attempt to alter
protected fields is rejected with a 403 and logged to the audit trail.

Protected fields:
  - Account ownership (user ID, email, full_name, business_name)
  - Admin/super_admin role and active status
  - Label ownership (owner role on all labels)
  - Revenue/royalty percentages belonging to the protected owner
  - Account deletion or deactivation
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IMMUTABLE CONSTANTS — CANNOT BE CHANGED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROTECTED_OWNER_USER_ID = "0659dd6d-e447-4022-a05a-f775b1509572"
PROTECTED_OWNER_EMAIL = "owner@bigmannentertainment.com"
PROTECTED_OWNER_FULL_NAME = "John LeGerron Spivey"
PROTECTED_BUSINESS_NAME = "Big Mann Entertainment"
PROTECTED_OWNER_ROLE = "super_admin"
PROTECTED_OWNER_IS_ADMIN = True
PROTECTED_OWNER_IS_ACTIVE = True
PROTECTED_OWNER_ACCOUNT_STATUS = "active"

# Fields that can NEVER be changed on the protected owner account
LOCKED_USER_FIELDS = frozenset({
    "email",
    "full_name",
    "business_name",
    "role",
    "is_admin",
    "is_active",
    "account_status",
    "tenant_id",
    "tenant_name",
})

# Revenue/royalty percentage floors — the owner's share can never go below these
MINIMUM_REVENUE_PERCENTAGES = {
    "master_licensing": 100.0,
    "default_royalty_share": 100.0,
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IMMUTABLE BUSINESS & GS1 IDENTIFIERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROTECTED_GS1_COMPANY_PREFIX = "08600043402"
PROTECTED_GLN = "0860004340201"
PROTECTED_EIN = "270658077"
PROTECTED_DUNS = "000000000"  # Placeholder — update when real DUNS assigned
PROTECTED_BUSINESS_REGISTRATION = "BME-2024-001"

PROTECTED_BUSINESS_IDENTIFIERS = {
    "gs1_company_prefix": PROTECTED_GS1_COMPANY_PREFIX,
    "gln": PROTECTED_GLN,
    "ein": PROTECTED_EIN,
    "duns": PROTECTED_DUNS,
    "business_registration_number": PROTECTED_BUSINESS_REGISTRATION,
    "business_entity": PROTECTED_BUSINESS_NAME,
    "business_owner": PROTECTED_OWNER_FULL_NAME,
    "business_type": "Sole Proprietorship",
}

# Fields on business_identifiers that are locked for the protected owner
LOCKED_IDENTIFIER_FIELDS = frozenset({
    "gs1_company_prefix", "gln", "ein", "duns",
    "business_registration_number", "business_entity",
    "business_owner", "business_type",
})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GUARD: USER ACCOUNT MODIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def is_protected_owner(user_id: str = "", email: str = "") -> bool:
    """Check if the target is the protected owner."""
    if user_id and user_id == PROTECTED_OWNER_USER_ID:
        return True
    if email and email.lower() == PROTECTED_OWNER_EMAIL.lower():
        return True
    return False


def block_protected_user_update(user_id: str, updates: Dict[str, Any], actor_description: str = "unknown") -> Optional[str]:
    """
    Returns an error message if the update would violate ownership protection.
    Returns None if the update is safe.
    """
    if not is_protected_owner(user_id=user_id):
        return None

    # Check for any attempt to modify locked fields
    violated = LOCKED_USER_FIELDS & set(updates.keys())
    if violated:
        msg = (
            f"OWNERSHIP PROTECTION: Cannot modify {', '.join(sorted(violated))} "
            f"on the account of {PROTECTED_OWNER_FULL_NAME} / {PROTECTED_BUSINESS_NAME}. "
            f"This field is permanently locked."
        )
        logger.warning(f"[OWNERSHIP GUARD] Blocked by actor '{actor_description}': {msg}")
        return msg

    return None


def block_protected_user_delete(user_id: str = "", email: str = "") -> Optional[str]:
    """
    Returns an error message if someone tries to delete/deactivate the protected owner.
    """
    if is_protected_owner(user_id=user_id, email=email):
        msg = (
            f"OWNERSHIP PROTECTION: The account of {PROTECTED_OWNER_FULL_NAME} / "
            f"{PROTECTED_BUSINESS_NAME} cannot be deleted or deactivated."
        )
        logger.warning(f"[OWNERSHIP GUARD] Blocked account deletion attempt: {msg}")
        return msg
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GUARD: LABEL OWNERSHIP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def block_owner_role_change(label_id: str, user_id: str, new_role: str) -> Optional[str]:
    """
    Prevents anyone from demoting the protected owner's role on any label.
    The owner MUST remain 'owner' on every label they belong to.
    """
    if is_protected_owner(user_id=user_id) and new_role != "owner":
        msg = (
            f"OWNERSHIP PROTECTION: {PROTECTED_OWNER_FULL_NAME}'s owner role on "
            f"label {label_id} cannot be changed. Permanent owner."
        )
        logger.warning(f"[OWNERSHIP GUARD] Blocked role change: {msg}")
        return msg
    return None


def block_owner_removal_from_label(label_id: str, user_id: str) -> Optional[str]:
    """
    Prevents anyone from removing the protected owner from any label.
    """
    if is_protected_owner(user_id=user_id):
        msg = (
            f"OWNERSHIP PROTECTION: {PROTECTED_OWNER_FULL_NAME} cannot be removed "
            f"from label {label_id}. Permanent owner."
        )
        logger.warning(f"[OWNERSHIP GUARD] Blocked member removal: {msg}")
        return msg
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GUARD: REVENUE & ROYALTY PERCENTAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def block_percentage_change(
    entity_id: str,
    field_name: str,
    new_value: float,
    context: str = "",
) -> Optional[str]:
    """
    Prevents any modification that would reduce the protected owner's
    revenue/royalty percentages below the locked minimums.
    """
    if not is_protected_owner(user_id=entity_id):
        return None

    min_pct = MINIMUM_REVENUE_PERCENTAGES.get(field_name)
    if min_pct is not None and new_value < min_pct:
        msg = (
            f"OWNERSHIP PROTECTION: Cannot reduce {PROTECTED_OWNER_FULL_NAME}'s "
            f"'{field_name}' percentage below {min_pct}%. "
            f"Attempted: {new_value}%. Context: {context}"
        )
        logger.warning(f"[OWNERSHIP GUARD] Blocked percentage change: {msg}")
        return msg
    return None


def block_revenue_share_modification(
    agreements: list,
    label_owner_id: str = "",
) -> Optional[str]:
    """
    Validates a list of revenue_sharing_agreements to ensure the protected
    owner's shares are not reduced.
    """
    if not is_protected_owner(user_id=label_owner_id):
        return None

    for agreement in agreements:
        pct = agreement.get("percentage", 0)
        atype = agreement.get("type", "unknown")
        min_pct = MINIMUM_REVENUE_PERCENTAGES.get(atype)
        if min_pct is not None and pct < min_pct:
            msg = (
                f"OWNERSHIP PROTECTION: Revenue agreement '{atype}' percentage "
                f"({pct}%) cannot be set below {min_pct}% for "
                f"{PROTECTED_OWNER_FULL_NAME} / {PROTECTED_BUSINESS_NAME}."
            )
            logger.warning(f"[OWNERSHIP GUARD] Blocked revenue share change: {msg}")
            return msg
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GUARD: BUSINESS & GS1 IDENTIFIERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def block_identifier_change(user_id: str, updates: Dict[str, Any], actor_description: str = "unknown") -> Optional[str]:
    """
    Prevents modification of protected business/GS1 identifiers
    for John LeGerron Spivey / Big Mann Entertainment.
    Returns error message if blocked, None if safe.
    """
    if not is_protected_owner(user_id=user_id):
        return None

    violated = LOCKED_IDENTIFIER_FIELDS & set(updates.keys())
    if violated:
        msg = (
            f"OWNERSHIP PROTECTION: Cannot modify {', '.join(sorted(violated))} "
            f"on the business identifiers of {PROTECTED_OWNER_FULL_NAME} / {PROTECTED_BUSINESS_NAME}. "
            f"These identifiers are permanently locked."
        )
        logger.warning(f"[OWNERSHIP GUARD] Blocked identifier change by '{actor_description}': {msg}")
        return msg
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  AUDIT LOGGING FOR BLOCKED ATTEMPTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def log_ownership_violation(db_instance, actor_id: str, action: str, details: Dict[str, Any]):
    """Log every blocked ownership violation to the audit trail."""
    try:
        await db_instance.uln_audit_trail.insert_one({
            "action_type": "ownership_violation_blocked",
            "actor_id": actor_id,
            "resource_type": "ownership_guard",
            "resource_id": PROTECTED_OWNER_USER_ID,
            "description": f"BLOCKED: {action}",
            "changes": details,
            "timestamp": _now_iso(),
            "severity": "critical",
        })
    except Exception as e:
        logger.error(f"Failed to log ownership violation: {e}")
