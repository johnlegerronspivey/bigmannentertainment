"""
AWS GuardDuty Integration - API Endpoints
REST API for real-time threat detection and security monitoring
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime

from guardduty_models import (
    Detector, Finding, FindingUpdate, FindingStatus, SeverityLevel,
    GuardDutyDashboardStats, GuardDutyHealthResponse, FindingsResponse,
    DetectorsResponse, THREAT_TYPES
)
from guardduty_service import get_guardduty_service, GuardDutyService

router = APIRouter(prefix="/guardduty", tags=["AWS GuardDuty Threat Detection"])

DEFAULT_USER_ID = "user_001"


def get_service() -> GuardDutyService:
    """Get the GuardDuty service"""
    service = get_guardduty_service()
    if service is None:
        raise HTTPException(status_code=503, detail="GuardDuty service not initialized")
    return service


# ==================== Health & Dashboard ====================

@router.get("/health", response_model=GuardDutyHealthResponse)
async def health_check(service: GuardDutyService = Depends(get_service)):
    """Health check endpoint"""
    return await service.check_health()


@router.get("/dashboard", response_model=GuardDutyDashboardStats)
async def get_dashboard_stats(service: GuardDutyService = Depends(get_service)):
    """Get comprehensive dashboard statistics"""
    return await service.get_dashboard_stats()


# ==================== Detectors ====================

@router.get("/detectors", response_model=DetectorsResponse)
async def list_detectors(service: GuardDutyService = Depends(get_service)):
    """List all GuardDuty detectors"""
    detectors = await service.get_detectors()
    return DetectorsResponse(
        success=True,
        detectors=detectors,
        total=len(detectors)
    )


@router.get("/detectors/{detector_id}", response_model=Detector)
async def get_detector(
    detector_id: str,
    service: GuardDutyService = Depends(get_service)
):
    """Get a specific detector"""
    detector = await service.get_detector(detector_id)
    if not detector:
        raise HTTPException(status_code=404, detail="Detector not found")
    return detector


@router.post("/detectors", response_model=Detector)
async def create_detector(service: GuardDutyService = Depends(get_service)):
    """Create a new GuardDuty detector"""
    return await service.create_detector()


@router.post("/detectors/{detector_id}/sync")
async def sync_findings(
    detector_id: str,
    service: GuardDutyService = Depends(get_service)
):
    """Sync findings from AWS GuardDuty for a detector"""
    synced_count = await service.sync_findings_from_aws(detector_id)
    return {
        "success": True,
        "message": f"Synced {synced_count} findings from AWS",
        "synced_count": synced_count
    }


# ==================== Findings ====================

@router.get("/findings", response_model=FindingsResponse)
async def list_findings(
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="Filter by status: NEW, ACKNOWLEDGED, RESOLVED, ARCHIVED"),
    category: Optional[str] = Query(None, description="Filter by threat category"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    days_back: int = Query(30, ge=1, le=365, description="Days of history to retrieve"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: GuardDutyService = Depends(get_service)
):
    """List findings with optional filtering"""
    severity_enum = SeverityLevel(severity) if severity else None
    status_enum = FindingStatus(status) if status else None
    
    findings, total = await service.get_findings(
        severity_level=severity_enum,
        status=status_enum,
        category=category,
        resource_type=resource_type,
        days_back=days_back,
        limit=limit,
        offset=offset
    )
    
    return FindingsResponse(
        success=True,
        findings=findings,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(findings) < total
    )


@router.get("/findings/{finding_id}", response_model=Finding)
async def get_finding(
    finding_id: str,
    service: GuardDutyService = Depends(get_service)
):
    """Get a specific finding"""
    finding = await service.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.patch("/findings/{finding_id}", response_model=Finding)
async def update_finding(
    finding_id: str,
    update: FindingUpdate,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: GuardDutyService = Depends(get_service)
):
    """Update a finding's status or notes"""
    finding = await service.update_finding(finding_id, update, user_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/findings/{finding_id}/acknowledge", response_model=Finding)
async def acknowledge_finding(
    finding_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: GuardDutyService = Depends(get_service)
):
    """Acknowledge a finding"""
    finding = await service.acknowledge_finding(finding_id, user_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/findings/{finding_id}/resolve", response_model=Finding)
async def resolve_finding(
    finding_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    notes: Optional[str] = Query(None, description="Resolution notes"),
    service: GuardDutyService = Depends(get_service)
):
    """Resolve a finding"""
    finding = await service.resolve_finding(finding_id, user_id, notes)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/findings/{finding_id}/archive", response_model=Finding)
async def archive_finding(
    finding_id: str,
    service: GuardDutyService = Depends(get_service)
):
    """Archive a finding"""
    finding = await service.archive_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


# ==================== Reference Data ====================

@router.get("/threat-types")
async def get_threat_types():
    """Get reference information about threat types"""
    return {
        "threat_types": [
            {
                "category": category,
                "description": data["description"],
                "severity_range": data["severity_range"],
                "examples": data["examples"]
            }
            for category, data in THREAT_TYPES.items()
        ]
    }


@router.get("/severity-levels")
async def get_severity_levels():
    """Get severity level definitions"""
    return {
        "severity_levels": [
            {
                "id": "CRITICAL",
                "name": "Critical",
                "score_range": "9.0-10.0",
                "description": "Immediate action required - active compromise detected",
                "color": "#dc2626",
                "action": "Escalate to security team immediately"
            },
            {
                "id": "HIGH",
                "name": "High",
                "score_range": "7.0-8.9",
                "description": "Serious threat - potential active attack",
                "color": "#ea580c",
                "action": "Investigate within 4 hours"
            },
            {
                "id": "MEDIUM",
                "name": "Medium",
                "score_range": "4.0-6.9",
                "description": "Suspicious activity - requires investigation",
                "color": "#ca8a04",
                "action": "Investigate within 24 hours"
            },
            {
                "id": "LOW",
                "name": "Low",
                "score_range": "1.0-3.9",
                "description": "Informational - low risk activity",
                "color": "#2563eb",
                "action": "Review when convenient"
            }
        ]
    }


@router.get("/resource-types")
async def get_resource_types():
    """Get supported resource types"""
    return {
        "resource_types": [
            {"id": "Instance", "name": "EC2 Instance", "icon": "server"},
            {"id": "AccessKey", "name": "IAM Access Key", "icon": "key"},
            {"id": "S3Bucket", "name": "S3 Bucket", "icon": "database"},
            {"id": "IAMUser", "name": "IAM User", "icon": "user"},
            {"id": "EKSCluster", "name": "EKS Cluster", "icon": "cloud"},
            {"id": "ECSCluster", "name": "ECS Cluster", "icon": "cloud"},
            {"id": "Lambda", "name": "Lambda Function", "icon": "code"},
            {"id": "RDSDBInstance", "name": "RDS Database", "icon": "database"},
            {"id": "Container", "name": "Container", "icon": "box"}
        ]
    }


@router.get("/finding-statuses")
async def get_finding_statuses():
    """Get finding status definitions"""
    return {
        "statuses": [
            {
                "id": "NEW",
                "name": "New",
                "description": "Newly discovered finding requiring review",
                "color": "#dc2626"
            },
            {
                "id": "ACKNOWLEDGED",
                "name": "Acknowledged",
                "description": "Finding acknowledged by security team",
                "color": "#ca8a04"
            },
            {
                "id": "RESOLVED",
                "name": "Resolved",
                "description": "Finding has been remediated",
                "color": "#16a34a"
            },
            {
                "id": "ARCHIVED",
                "name": "Archived",
                "description": "Finding archived (false positive or accepted risk)",
                "color": "#6b7280"
            }
        ]
    }
