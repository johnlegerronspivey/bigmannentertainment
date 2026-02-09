"""
AWS Macie Integration - API Endpoints
REST API for automated sensitive data discovery and PII detection
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime

from macie_models import (
    CustomDataIdentifier, CreateCustomIdentifierRequest,
    ClassificationJob, CreateClassificationJobRequest, JobStatus,
    Finding, SeverityLevel, MacieDashboardStats, FindingStatistics,
    S3BucketInfo, MacieHealthResponse
)
from macie_service import get_macie_service, MacieService

router = APIRouter(prefix="/macie", tags=["AWS Macie PII Detection"])

DEFAULT_USER_ID = "user_001"


def get_service() -> MacieService:
    """Get the Macie service"""
    service = get_macie_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Macie service not initialized")
    return service


# ==================== Health & Dashboard ====================

@router.get("/health")
async def health_check(service: MacieService = Depends(get_service)):
    """Health check endpoint"""
    return await service.check_health()


@router.get("/dashboard", response_model=MacieDashboardStats)
async def get_dashboard_stats(service: MacieService = Depends(get_service)):
    """Get comprehensive dashboard statistics"""
    return await service.get_dashboard_stats()


@router.get("/statistics", response_model=FindingStatistics)
async def get_finding_statistics(service: MacieService = Depends(get_service)):
    """Get aggregated finding statistics"""
    return await service.get_finding_statistics()


# ==================== Custom Data Identifiers ====================

@router.post("/custom-identifiers", response_model=CustomDataIdentifier)
async def create_custom_identifier(
    request: CreateCustomIdentifierRequest,
    service: MacieService = Depends(get_service)
):
    """Create a custom data identifier for detecting proprietary sensitive data"""
    return await service.create_custom_identifier(request)


@router.get("/custom-identifiers", response_model=List[CustomDataIdentifier])
async def list_custom_identifiers(service: MacieService = Depends(get_service)):
    """List all custom data identifiers"""
    return await service.get_custom_identifiers()


@router.get("/custom-identifiers/{identifier_id}", response_model=CustomDataIdentifier)
async def get_custom_identifier(
    identifier_id: str,
    service: MacieService = Depends(get_service)
):
    """Get a specific custom data identifier"""
    identifier = await service.get_custom_identifier(identifier_id)
    if not identifier:
        raise HTTPException(status_code=404, detail="Custom identifier not found")
    return identifier


@router.delete("/custom-identifiers/{identifier_id}")
async def delete_custom_identifier(
    identifier_id: str,
    service: MacieService = Depends(get_service)
):
    """Delete a custom data identifier"""
    success = await service.delete_custom_identifier(identifier_id)
    if not success:
        raise HTTPException(status_code=404, detail="Custom identifier not found")
    return {"success": True, "message": "Custom identifier deleted"}


# ==================== Classification Jobs ====================

@router.post("/jobs", response_model=ClassificationJob)
async def create_classification_job(
    request: CreateClassificationJobRequest,
    service: MacieService = Depends(get_service)
):
    """Create a new classification job for sensitive data discovery"""
    return await service.create_classification_job(request)


@router.get("/jobs")
async def list_classification_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MacieService = Depends(get_service)
):
    """List classification jobs with optional filtering"""
    status_enum = JobStatus(status) if status else None
    jobs, total = await service.get_classification_jobs(status_enum, limit, offset)
    return {
        "success": True,
        "jobs": jobs,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/jobs/{job_id}", response_model=ClassificationJob)
async def get_classification_job(
    job_id: str,
    service: MacieService = Depends(get_service)
):
    """Get a specific classification job"""
    job = await service.get_classification_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Classification job not found")
    return job


@router.post("/jobs/{job_id}/cancel", response_model=ClassificationJob)
async def cancel_classification_job(
    job_id: str,
    service: MacieService = Depends(get_service)
):
    """Cancel a running classification job"""
    job = await service.cancel_classification_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Classification job not found")
    return job


# ==================== Findings ====================

@router.get("/findings")
async def list_findings(
    severity: Optional[str] = Query(None, description="Filter by severity: Low, Medium, High"),
    bucket_name: Optional[str] = Query(None, description="Filter by bucket name"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgement status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MacieService = Depends(get_service)
):
    """List findings with optional filtering"""
    severity_enum = SeverityLevel(severity) if severity else None
    findings, total = await service.get_findings(
        severity=severity_enum,
        bucket_name=bucket_name,
        is_acknowledged=acknowledged,
        limit=limit,
        offset=offset
    )
    return {
        "success": True,
        "findings": findings,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/findings/{finding_id}", response_model=Finding)
async def get_finding(
    finding_id: str,
    service: MacieService = Depends(get_service)
):
    """Get a specific finding"""
    finding = await service.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/findings/{finding_id}/acknowledge", response_model=Finding)
async def acknowledge_finding(
    finding_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: MacieService = Depends(get_service)
):
    """Acknowledge a finding"""
    finding = await service.acknowledge_finding(finding_id, user_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/findings/{finding_id}/archive", response_model=Finding)
async def archive_finding(
    finding_id: str,
    service: MacieService = Depends(get_service)
):
    """Archive a finding"""
    finding = await service.archive_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


# ==================== S3 Buckets ====================

@router.get("/buckets", response_model=List[S3BucketInfo])
async def list_monitored_buckets(service: MacieService = Depends(get_service)):
    """List all monitored S3 buckets"""
    return await service.get_monitored_buckets()


@router.post("/buckets", response_model=S3BucketInfo)
async def add_bucket_to_monitoring(
    bucket_name: str = Query(..., description="Name of the S3 bucket to monitor"),
    service: MacieService = Depends(get_service)
):
    """Add a bucket to monitoring"""
    return await service.add_bucket_to_monitoring(bucket_name)


@router.delete("/buckets/{bucket_name}")
async def remove_bucket_from_monitoring(
    bucket_name: str,
    service: MacieService = Depends(get_service)
):
    """Remove a bucket from monitoring"""
    success = await service.remove_bucket_from_monitoring(bucket_name)
    if not success:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return {"success": True, "message": f"Bucket {bucket_name} removed from monitoring"}


# ==================== PII Types Reference ====================

@router.get("/pii-types")
async def get_pii_types():
    """Get list of supported PII types detected by Macie"""
    return {
        "pii_types": [
            {"id": "USA_SOCIAL_SECURITY_NUMBER", "name": "Social Security Number", "category": "Personal", "risk": "High"},
            {"id": "CREDIT_CARD_NUMBER", "name": "Credit Card Number", "category": "Financial", "risk": "High"},
            {"id": "BANK_ACCOUNT_NUMBER", "name": "Bank Account Number", "category": "Financial", "risk": "High"},
            {"id": "EMAIL_ADDRESS", "name": "Email Address", "category": "Personal", "risk": "Medium"},
            {"id": "PHONE_NUMBER", "name": "Phone Number", "category": "Personal", "risk": "Medium"},
            {"id": "USA_PASSPORT_NUMBER", "name": "Passport Number", "category": "Personal", "risk": "High"},
            {"id": "USA_DRIVERS_LICENSE", "name": "Driver's License", "category": "Personal", "risk": "High"},
            {"id": "DATE_OF_BIRTH", "name": "Date of Birth", "category": "Personal", "risk": "Medium"},
            {"id": "USA_HEALTH_INSURANCE_CLAIM_NUMBER", "name": "Health Insurance Claim Number", "category": "Medical", "risk": "High"},
            {"id": "IP_ADDRESS", "name": "IP Address", "category": "Technical", "risk": "Low"},
            {"id": "NAME", "name": "Full Name", "category": "Personal", "risk": "Low"},
            {"id": "ADDRESS", "name": "Physical Address", "category": "Personal", "risk": "Medium"},
            {"id": "AWS_SECRET_ACCESS_KEY", "name": "AWS Secret Key", "category": "Credentials", "risk": "Critical"},
            {"id": "AWS_ACCESS_KEY_ID", "name": "AWS Access Key ID", "category": "Credentials", "risk": "Critical"}
        ]
    }


# ==================== Severity Reference ====================

@router.get("/severity-levels")
async def get_severity_levels():
    """Get severity level definitions"""
    return {
        "severity_levels": [
            {
                "id": "Low",
                "name": "Low",
                "score_range": "1-39",
                "description": "Minor exposure, limited business impact",
                "color": "#22c55e",
                "action": "Monitor and review when convenient"
            },
            {
                "id": "Medium",
                "name": "Medium",
                "score_range": "40-69",
                "description": "Moderate exposure, potential compliance risk",
                "color": "#eab308",
                "action": "Review within 48 hours, remediate if necessary"
            },
            {
                "id": "High",
                "name": "High",
                "score_range": "70-100",
                "description": "Critical exposure, immediate action required",
                "color": "#ef4444",
                "action": "Immediate review and remediation required"
            }
        ]
    }



# ==================== SNS/EventBridge Notifications ====================

from macie_models import (
    NotificationRule, CreateNotificationRuleRequest,
    NotificationLog, NotificationChannel, NotificationStatus
)

@router.get("/notifications/rules")
async def list_notification_rules(service: MacieService = Depends(get_service)):
    """List all notification rules"""
    rules = await service.get_notification_rules()
    return {"rules": rules, "total": len(rules)}

@router.post("/notifications/rules", response_model=NotificationRule)
async def create_notification_rule(
    request: CreateNotificationRuleRequest,
    service: MacieService = Depends(get_service)
):
    """Create a notification rule for Macie findings"""
    return await service.create_notification_rule(request)

@router.put("/notifications/rules/{rule_id}/toggle")
async def toggle_notification_rule(
    rule_id: str,
    service: MacieService = Depends(get_service)
):
    """Enable or disable a notification rule"""
    rule = await service.toggle_notification_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.delete("/notifications/rules/{rule_id}")
async def delete_notification_rule(
    rule_id: str,
    service: MacieService = Depends(get_service)
):
    """Delete a notification rule"""
    success = await service.delete_notification_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True, "message": "Rule deleted"}

@router.get("/notifications/logs")
async def list_notification_logs(
    rule_id: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MacieService = Depends(get_service)
):
    """Get notification history/logs"""
    channel_enum = NotificationChannel(channel) if channel else None
    logs, total = await service.get_notification_logs(rule_id=rule_id, channel=channel_enum, limit=limit, offset=offset)
    return {"logs": logs, "total": total, "limit": limit, "offset": offset}

@router.post("/notifications/test/{rule_id}")
async def test_notification_rule(
    rule_id: str,
    service: MacieService = Depends(get_service)
):
    """Send a test notification for a rule"""
    result = await service.send_test_notification(rule_id)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return result

@router.get("/notifications/stats")
async def get_notification_stats(service: MacieService = Depends(get_service)):
    """Get notification statistics"""
    return await service.get_notification_stats()
