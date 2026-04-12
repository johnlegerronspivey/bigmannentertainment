"""
Secrets Protection Service — Key masking, health checks, audit logging, and leak prevention.
Centralizes all sensitive key management operations.
"""
import os
import re
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional
from enum import Enum
from config.database import db


class KeySensitivity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class KeyStatus(str, Enum):
    CONFIGURED = "configured"
    MISSING = "missing"
    PLACEHOLDER = "placeholder"
    ROTATED = "rotated"


# Registry of all known keys with metadata
KEY_REGISTRY = {
    "AWS_ACCESS_KEY_ID": {
        "label": "AWS Access Key",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "cloud",
        "description": "AWS IAM access key for cloud services",
        "rotation_days": 90,
        "placeholder_patterns": ["YOUR_", "EXAMPLE", "AKIA1234"],
    },
    "AWS_SECRET_ACCESS_KEY": {
        "label": "AWS Secret Key",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "cloud",
        "description": "AWS IAM secret access key",
        "rotation_days": 90,
        "placeholder_patterns": ["YOUR_", "EXAMPLE"],
    },
    "SECRET_KEY": {
        "label": "JWT Secret Key",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "authentication",
        "description": "JWT signing secret for authentication tokens",
        "rotation_days": 180,
        "placeholder_patterns": ["changeme", "secret", "default"],
    },
    "STRIPE_API_KEY": {
        "label": "Stripe API Key",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "payments",
        "description": "Stripe secret key for payment processing",
        "rotation_days": 365,
        "placeholder_patterns": ["sk_test_", "YOUR_"],
    },
    "PAYPAL_CLIENT_SECRET": {
        "label": "PayPal Client Secret",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "payments",
        "description": "PayPal OAuth client secret",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_"],
    },
    "PAYPAL_CLIENT_ID": {
        "label": "PayPal Client ID",
        "sensitivity": KeySensitivity.MEDIUM,
        "category": "payments",
        "description": "PayPal OAuth client identifier",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_"],
    },
    "ETHEREUM_PRIVATE_KEY": {
        "label": "Ethereum Private Key",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "blockchain",
        "description": "Ethereum wallet private key for transactions",
        "rotation_days": 0,
        "placeholder_patterns": ["0x0000", "YOUR_"],
    },
    "INFURA_PROJECT_ID": {
        "label": "Infura Project ID",
        "sensitivity": KeySensitivity.HIGH,
        "category": "blockchain",
        "description": "Infura project ID for Ethereum RPC access",
        "rotation_days": 365,
        "placeholder_patterns": ["your_infura", "YOUR_"],
    },
    "OPENAI_API_KEY": {
        "label": "OpenAI API Key",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "ai",
        "description": "OpenAI API key for AI model access",
        "rotation_days": 365,
        "placeholder_patterns": ["sk-proj-xxx", "YOUR_"],
    },
    "CLAUDE_API_KEY": {
        "label": "Claude API Key",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "ai",
        "description": "Anthropic Claude API key",
        "rotation_days": 365,
        "placeholder_patterns": ["sk-ant-xxx", "YOUR_"],
    },
    "GOOGLE_API_KEY": {
        "label": "Google API Key",
        "sensitivity": KeySensitivity.HIGH,
        "category": "ai",
        "description": "Google Cloud API key",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_", "AIzaSy_example"],
    },
    "GITHUB_TOKEN": {
        "label": "GitHub Personal Access Token",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "devops",
        "description": "GitHub PAT for repo access and CI/CD",
        "rotation_days": 90,
        "placeholder_patterns": ["ghp_xxx", "YOUR_"],
    },
    "RESEND_API_KEY": {
        "label": "Resend Email API Key",
        "sensitivity": KeySensitivity.HIGH,
        "category": "email",
        "description": "Resend API key for transactional emails",
        "rotation_days": 365,
        "placeholder_patterns": ["re_xxx", "YOUR_"],
    },
    "SNAPCHAT_API_TOKEN": {
        "label": "Snapchat API Token",
        "sensitivity": KeySensitivity.HIGH,
        "category": "social",
        "description": "Snapchat Business API JWT token",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_"],
    },
    "TIKTOK_CLIENT_SECRET": {
        "label": "TikTok Client Secret",
        "sensitivity": KeySensitivity.HIGH,
        "category": "social",
        "description": "TikTok OAuth client secret",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_"],
    },
    "TIKTOK_CLIENT_KEY": {
        "label": "TikTok Client Key",
        "sensitivity": KeySensitivity.MEDIUM,
        "category": "social",
        "description": "TikTok OAuth client key",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_"],
    },
    "TWITTER_CLIENT_SECRET": {
        "label": "Twitter Client Secret",
        "sensitivity": KeySensitivity.HIGH,
        "category": "social",
        "description": "Twitter/X OAuth client secret",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_"],
    },
    "TWITTER_BEARER_TOKEN": {
        "label": "Twitter Bearer Token",
        "sensitivity": KeySensitivity.HIGH,
        "category": "social",
        "description": "Twitter/X API bearer token",
        "rotation_days": 365,
        "placeholder_patterns": ["YOUR_", "AAAA_example"],
    },
    "EMAIL_PASSWORD": {
        "label": "SMTP Email Password",
        "sensitivity": KeySensitivity.HIGH,
        "category": "email",
        "description": "SMTP server authentication password",
        "rotation_days": 180,
        "placeholder_patterns": ["YOUR_", "production_app_password_here"],
    },
    "GS1_API_KEY": {
        "label": "GS1 US API Key",
        "sensitivity": KeySensitivity.MEDIUM,
        "category": "business",
        "description": "GS1 US Data Hub API key",
        "rotation_days": 365,
        "placeholder_patterns": ["production_gs1_api_key_here", "YOUR_"],
    },
    "MONGO_URL": {
        "label": "MongoDB Connection String",
        "sensitivity": KeySensitivity.CRITICAL,
        "category": "database",
        "description": "MongoDB connection URI",
        "rotation_days": 0,
        "placeholder_patterns": [],
    },
}

# Regex patterns that indicate a secret value in text
SECRET_PATTERNS = [
    (r'sk_live_[A-Za-z0-9]{20,}', "Stripe Live Key"),
    (r'sk_test_[A-Za-z0-9]{20,}', "Stripe Test Key"),
    (r'sk-proj-[A-Za-z0-9_-]{20,}', "OpenAI API Key"),
    (r'sk-ant-[A-Za-z0-9_-]{20,}', "Anthropic API Key"),
    (r'AKIA[A-Z0-9]{16}', "AWS Access Key ID"),
    (r'github_pat_[A-Za-z0-9_]{20,}', "GitHub PAT"),
    (r'ghp_[A-Za-z0-9]{36,}', "GitHub PAT (classic)"),
    (r're_[A-Za-z0-9_]{10,}', "Resend API Key"),
    (r'AIzaSy[A-Za-z0-9_-]{33}', "Google API Key"),
    (r'0x[a-fA-F0-9]{64}', "Ethereum Private Key"),
    (r'eyJhbGciOi[A-Za-z0-9_.-]{50,}', "JWT Token"),
    (r'mongodb(\+srv)?://[^\s"\']+', "MongoDB URI"),
]


def mask_key(value: str, visible_chars: int = 4) -> str:
    """Mask a key value showing only last N characters."""
    if not value or len(value) <= visible_chars:
        return "****"
    return "*" * min(len(value) - visible_chars, 40) + value[-visible_chars:]


def get_key_fingerprint(value: str) -> str:
    """Generate a non-reversible fingerprint for a key value."""
    if not value:
        return ""
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def detect_key_status(env_name: str) -> KeyStatus:
    """Determine if a key is properly configured, missing, or a placeholder."""
    value = os.environ.get(env_name, "")
    if not value:
        return KeyStatus.MISSING

    registry_entry = KEY_REGISTRY.get(env_name, {})
    placeholder_patterns = registry_entry.get("placeholder_patterns", [])
    for pattern in placeholder_patterns:
        if pattern.lower() in value.lower():
            return KeyStatus.PLACEHOLDER

    return KeyStatus.CONFIGURED


def sanitize_text(text: str) -> str:
    """Remove any secret patterns from arbitrary text (error messages, logs)."""
    sanitized = text
    for pattern, label in SECRET_PATTERNS:
        sanitized = re.sub(pattern, f"[REDACTED:{label}]", sanitized)
    return sanitized


def scan_for_leaks(text: str) -> List[Dict]:
    """Scan text for any leaked secret patterns. Returns list of findings."""
    findings = []
    for pattern, label in SECRET_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            findings.append({
                "type": label,
                "masked_value": mask_key(match, 4),
                "position": text.find(match),
                "severity": "critical",
            })
    return findings


def get_vault_summary() -> Dict:
    """Get a complete summary of all keys in the vault with masked values and health status."""
    vault = []
    categories = {}

    for key_name, meta in KEY_REGISTRY.items():
        value = os.environ.get(key_name, "")
        status = detect_key_status(key_name)
        masked = mask_key(value) if value else "NOT SET"
        fingerprint = get_key_fingerprint(value) if value else ""
        category = meta.get("category", "other")

        entry = {
            "key_name": key_name,
            "label": meta["label"],
            "sensitivity": meta["sensitivity"],
            "category": category,
            "description": meta["description"],
            "status": status,
            "masked_value": masked,
            "fingerprint": fingerprint,
            "rotation_days": meta.get("rotation_days", 0),
            "value_length": len(value) if value else 0,
        }
        vault.append(entry)

        if category not in categories:
            categories[category] = {"total": 0, "configured": 0, "missing": 0, "placeholder": 0}
        categories[category]["total"] += 1
        categories[category][status] += 1

    total = len(vault)
    configured = sum(1 for v in vault if v["status"] == KeyStatus.CONFIGURED)
    missing = sum(1 for v in vault if v["status"] == KeyStatus.MISSING)
    placeholder = sum(1 for v in vault if v["status"] == KeyStatus.PLACEHOLDER)
    critical_missing = sum(
        1 for v in vault
        if v["status"] != KeyStatus.CONFIGURED and v["sensitivity"] == KeySensitivity.CRITICAL
    )

    health_score = round((configured / total) * 100) if total > 0 else 0

    return {
        "keys": vault,
        "summary": {
            "total_keys": total,
            "configured": configured,
            "missing": missing,
            "placeholder": placeholder,
            "critical_missing": critical_missing,
            "health_score": health_score,
        },
        "categories": categories,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def run_security_scan() -> Dict:
    """Run a comprehensive security scan checking for common issues."""
    issues = []

    # Check for weak JWT secret
    secret = os.environ.get("SECRET_KEY", "")
    if secret and len(secret) < 32:
        issues.append({
            "severity": "critical",
            "category": "authentication",
            "title": "Weak JWT Secret Key",
            "description": "SECRET_KEY is shorter than 32 characters. Use a strong random value.",
            "remediation": "Generate a 64+ character random secret: python -c \"import secrets; print(secrets.token_hex(32))\"",
        })

    # Check for missing critical keys
    for key_name, meta in KEY_REGISTRY.items():
        if meta["sensitivity"] == KeySensitivity.CRITICAL:
            status = detect_key_status(key_name)
            if status == KeyStatus.PLACEHOLDER:
                issues.append({
                    "severity": "high",
                    "category": meta["category"],
                    "title": f"Placeholder value for {meta['label']}",
                    "description": f"{key_name} appears to contain a placeholder value instead of a real key.",
                    "remediation": f"Replace the placeholder in .env with a valid {meta['label']}.",
                })

    # Check CORS configuration
    cors = os.environ.get("CORS_ORIGINS", "")
    if cors.strip('"').strip("'") == "*":
        issues.append({
            "severity": "medium",
            "category": "network",
            "title": "Wildcard CORS Policy",
            "description": "CORS_ORIGINS is set to '*', allowing requests from any origin.",
            "remediation": "Restrict CORS_ORIGINS to specific trusted domains.",
        })

    # Check for Ethereum private key exposure
    eth_key = os.environ.get("ETHEREUM_PRIVATE_KEY", "")
    if eth_key and eth_key != "0x" + "0" * 64:
        issues.append({
            "severity": "info",
            "category": "blockchain",
            "title": "Ethereum Private Key Present",
            "description": "An Ethereum private key is configured. Ensure it is stored securely and never exposed in logs.",
            "remediation": "Consider using a hardware wallet or AWS KMS for production private key management.",
        })

    critical_count = sum(1 for i in issues if i["severity"] == "critical")
    high_count = sum(1 for i in issues if i["severity"] == "high")
    medium_count = sum(1 for i in issues if i["severity"] == "medium")

    return {
        "issues": issues,
        "total_issues": len(issues),
        "by_severity": {"critical": critical_count, "high": high_count, "medium": medium_count},
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": "critical" if critical_count > 0 else ("warning" if high_count > 0 else "healthy"),
    }


async def log_key_access(user_id: str, key_name: str, action: str, ip_address: str = None):
    """Log an audit entry for key vault access."""
    entry = {
        "user_id": user_id,
        "key_name": key_name,
        "action": action,
        "ip_address": ip_address or "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.key_audit_log.insert_one(entry)


async def get_audit_log(limit: int = 50, key_name: str = None) -> List[Dict]:
    """Retrieve key access audit log entries."""
    query = {}
    if key_name:
        query["key_name"] = key_name
    cursor = db.key_audit_log.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)
