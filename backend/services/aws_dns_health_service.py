"""AWS Route 53 External DNS Health Tracking Service."""
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from config.database import db

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def _get_route53_client():
    """Get a boto3 Route 53 client using env credentials."""
    return boto3.client(
        "route53",
        region_name=AWS_REGION,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )


def create_health_check(
    domain: str,
    port: int = 443,
    protocol: str = "HTTPS",
    resource_path: str = "/",
    failure_threshold: int = 3,
    request_interval: int = 30,
) -> dict:
    """Create a Route 53 health check for a domain."""
    client = _get_route53_client()
    caller_ref = f"bme-dns-{uuid.uuid4().hex[:12]}"

    config = {
        "FullyQualifiedDomainName": domain,
        "Port": port,
        "Type": protocol,
        "ResourcePath": resource_path,
        "FailureThreshold": failure_threshold,
        "RequestInterval": request_interval,
    }

    if protocol in ("HTTPS", "HTTPS_STR_MATCH"):
        config["EnableSNI"] = True

    resp = client.create_health_check(
        CallerReference=caller_ref,
        HealthCheckConfig=config,
    )

    hc = resp["HealthCheck"]
    return {
        "health_check_id": hc["Id"],
        "caller_reference": hc["CallerReference"],
        "config": {
            "domain": hc["HealthCheckConfig"].get("FullyQualifiedDomainName"),
            "port": hc["HealthCheckConfig"].get("Port"),
            "type": hc["HealthCheckConfig"].get("Type"),
            "resource_path": hc["HealthCheckConfig"].get("ResourcePath"),
            "failure_threshold": hc["HealthCheckConfig"].get("FailureThreshold"),
            "request_interval": hc["HealthCheckConfig"].get("RequestInterval"),
        },
    }


def get_health_check_status(health_check_id: str) -> dict:
    """Get the current status of a Route 53 health check."""
    client = _get_route53_client()
    resp = client.get_health_check_status(HealthCheckId=health_check_id)
    checkers = []
    for obs in resp.get("HealthCheckObservations", []):
        checkers.append({
            "region": obs.get("Region", "unknown"),
            "ip_address": obs.get("IPAddress", ""),
            "status": obs.get("StatusReport", {}).get("Status", "unknown"),
            "checked_time": obs.get("StatusReport", {}).get("CheckedTime", ""),
        })
    overall_healthy = any("Success" in c["status"] for c in checkers)
    return {
        "health_check_id": health_check_id,
        "overall_status": "healthy" if overall_healthy else "unhealthy",
        "checkers": checkers,
        "checker_count": len(checkers),
    }


def list_aws_health_checks() -> list:
    """List all Route 53 health checks in the account."""
    client = _get_route53_client()
    all_checks = []
    marker = None

    while True:
        kwargs = {"MaxItems": "100"}
        if marker:
            kwargs["Marker"] = marker

        resp = client.list_health_checks(**kwargs)
        for hc in resp.get("HealthChecks", []):
            cfg = hc.get("HealthCheckConfig", {})
            all_checks.append({
                "health_check_id": hc["Id"],
                "domain": cfg.get("FullyQualifiedDomainName", ""),
                "port": cfg.get("Port"),
                "type": cfg.get("Type", ""),
                "resource_path": cfg.get("ResourcePath", "/"),
                "failure_threshold": cfg.get("FailureThreshold"),
                "request_interval": cfg.get("RequestInterval"),
                "health_threshold": hc.get("HealthCheckVersion"),
            })

        if resp.get("IsTruncated"):
            marker = resp.get("NextMarker")
        else:
            break

    return all_checks


def delete_health_check(health_check_id: str) -> bool:
    """Delete a Route 53 health check."""
    client = _get_route53_client()
    client.delete_health_check(HealthCheckId=health_check_id)
    return True


# --------------- MongoDB persistence layer ---------------

async def save_target(user_id: str, domain: str, health_check_id: str, config: dict) -> dict:
    """Save a registered target to MongoDB."""
    doc = {
        "target_id": str(uuid.uuid4()),
        "user_id": user_id,
        "domain": domain,
        "health_check_id": health_check_id,
        "config": config,
        "status": "pending",
        "last_checked": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.aws_dns_targets.insert_one(doc)
    doc.pop("_id", None)
    return doc


async def list_targets(user_id: str) -> list:
    """List all registered AWS DNS targets for a user."""
    cursor = db.aws_dns_targets.find({"user_id": user_id}, {"_id": 0})
    return await cursor.to_list(length=100)


async def get_target(user_id: str, target_id: str) -> Optional[dict]:
    """Get a single target by ID."""
    return await db.aws_dns_targets.find_one(
        {"user_id": user_id, "target_id": target_id}, {"_id": 0}
    )


async def update_target_status(target_id: str, status: str, checkers: list) -> None:
    """Update the cached status of a target."""
    await db.aws_dns_targets.update_one(
        {"target_id": target_id},
        {"$set": {
            "status": status,
            "last_checked": datetime.now(timezone.utc).isoformat(),
            "checkers": checkers,
        }},
    )


async def delete_target(user_id: str, target_id: str) -> Optional[str]:
    """Delete a target from MongoDB and return its health_check_id for AWS cleanup."""
    doc = await db.aws_dns_targets.find_one({"user_id": user_id, "target_id": target_id})
    if not doc:
        return None
    hc_id = doc.get("health_check_id")
    await db.aws_dns_targets.delete_one({"user_id": user_id, "target_id": target_id})
    return hc_id
