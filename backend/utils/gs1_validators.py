"""
GS1 & Business Identifier Validators
======================================
Format checks and check-digit verification for:
  - GTIN (8, 12, 13, 14)  — Modulo 10 check digit
  - GLN  (13 digits)       — Modulo 10 check digit
  - GS1 Company Prefix     — 7-11 digit numeric
  - ISRC                   — CC-XXX-YY-NNNNN  (ISO 3901)
  - UPC  (GTIN-12)         — Modulo 10 check digit
  - EIN                    — XX-XXXXXXX (9 digits)
  - DUNS                   — 9 digits
  - Business Registration  — non-empty alphanumeric
"""

import re
from typing import Optional


def _gs1_check_digit(digits: str) -> str:
    """Calculate GS1 Modulo 10 check digit for a numeric string (excluding the check digit itself)."""
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        total += n * 3 if i % 2 == 0 else n
    return str((10 - total % 10) % 10)


def validate_gtin(value: str) -> Optional[str]:
    """Validate GTIN-8, GTIN-12, GTIN-13, or GTIN-14. Returns error message or None."""
    cleaned = value.strip()
    if not re.match(r'^\d+$', cleaned):
        return "GTIN must contain only digits"
    if len(cleaned) not in (8, 12, 13, 14):
        return "GTIN must be 8, 12, 13, or 14 digits"
    payload = cleaned[:-1]
    expected = _gs1_check_digit(payload)
    if cleaned[-1] != expected:
        return f"GTIN check digit invalid: expected {expected}, got {cleaned[-1]}"
    return None


def validate_upc(value: str) -> Optional[str]:
    """Validate UPC (GTIN-12). Returns error message or None."""
    cleaned = value.strip()
    if not re.match(r'^\d+$', cleaned):
        return "UPC must contain only digits"
    if len(cleaned) != 12:
        return "UPC must be exactly 12 digits"
    payload = cleaned[:-1]
    expected = _gs1_check_digit(payload)
    if cleaned[-1] != expected:
        return f"UPC check digit invalid: expected {expected}, got {cleaned[-1]}"
    return None


def validate_gln(value: str) -> Optional[str]:
    """Validate GLN (13-digit Global Location Number). Returns error message or None."""
    cleaned = value.strip()
    if not re.match(r'^\d+$', cleaned):
        return "GLN must contain only digits"
    if len(cleaned) != 13:
        return "GLN must be exactly 13 digits"
    payload = cleaned[:-1]
    expected = _gs1_check_digit(payload)
    if cleaned[-1] != expected:
        return f"GLN check digit invalid: expected {expected}, got {cleaned[-1]}"
    return None


def validate_gs1_company_prefix(value: str) -> Optional[str]:
    """Validate GS1 Company Prefix (7-11 digits). Returns error message or None."""
    cleaned = value.strip()
    if not re.match(r'^\d+$', cleaned):
        return "GS1 Company Prefix must contain only digits"
    if len(cleaned) < 7 or len(cleaned) > 11:
        return "GS1 Company Prefix must be 7 to 11 digits"
    return None


def validate_isrc(value: str) -> Optional[str]:
    """Validate ISRC (ISO 3901): CC-XXX-YY-NNNNN or CCXXXYYNNNNN. Returns error message or None."""
    cleaned = value.strip().upper().replace("-", "")
    if len(cleaned) != 12:
        return "ISRC must be 12 characters (CC-XXX-YY-NNNNN)"
    if not re.match(r'^[A-Z]{2}[A-Z0-9]{3}\d{2}\d{5}$', cleaned):
        return "ISRC format invalid: must be CC-XXX-YY-NNNNN (country-registrant-year-designation)"
    return None


def validate_ein(value: str) -> Optional[str]:
    """Validate US EIN: XX-XXXXXXX (9 digits total). Returns error message or None."""
    cleaned = value.strip().replace("-", "")
    if not re.match(r'^\d+$', cleaned):
        return "EIN must contain only digits"
    if len(cleaned) != 9:
        return "EIN must be exactly 9 digits (XX-XXXXXXX)"
    return None


def validate_duns(value: str) -> Optional[str]:
    """Validate DUNS Number (9 digits). Returns error message or None."""
    cleaned = value.strip().replace("-", "")
    if not re.match(r'^\d+$', cleaned):
        return "DUNS number must contain only digits"
    if len(cleaned) != 9:
        return "DUNS number must be exactly 9 digits"
    return None


def validate_business_registration(value: str) -> Optional[str]:
    """Validate business registration number (non-empty alphanumeric). Returns error message or None."""
    cleaned = value.strip()
    if not cleaned:
        return "Business registration number is required"
    if len(cleaned) < 3:
        return "Business registration number must be at least 3 characters"
    return None


# Convenience: validate all business identifiers at once
def validate_business_identifiers(data: dict) -> dict:
    """
    Validate a dict with keys: ein, duns, business_registration_number, gs1_company_prefix, gln.
    Returns dict of {field: error_message} for any invalid fields. Empty dict means all valid.
    """
    errors = {}
    validators = {
        "ein": validate_ein,
        "duns": validate_duns,
        "business_registration_number": validate_business_registration,
        "gs1_company_prefix": validate_gs1_company_prefix,
        "gln": validate_gln,
    }
    for field, validator_fn in validators.items():
        val = data.get(field, "").strip()
        if not val:
            errors[field] = f"{field.replace('_', ' ').title()} is required"
        else:
            err = validator_fn(val)
            if err:
                errors[field] = err
    return errors


def validate_asset_identifiers(data: dict) -> dict:
    """
    Validate asset-level identifiers: gtin (required), isrc (if present), upc (if present).
    Returns dict of {field: error_message}. Empty dict means valid.
    """
    errors = {}
    # GTIN is mandatory for every asset
    gtin_val = data.get("gtin", "").strip()
    if not gtin_val:
        errors["gtin"] = "GTIN is required for every catalog asset"
    else:
        err = validate_gtin(gtin_val)
        if err:
            errors["gtin"] = err

    # ISRC — required for music assets
    isrc_val = data.get("isrc", "").strip()
    if isrc_val:
        err = validate_isrc(isrc_val)
        if err:
            errors["isrc"] = err

    # UPC — required for physical/merchandise
    upc_val = data.get("upc", "").strip()
    if upc_val:
        err = validate_upc(upc_val)
        if err:
            errors["upc"] = err

    return errors
