"""
AWS QLDB Integration - API Endpoints
REST API for immutable dispute ledger and audit trail system
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime

from qldb_models import (
    Dispute, DisputeStatus, DisputeType, Priority,
    DisputeEvidence, DisputeComment, DisputeSettlement,
    CreateDisputeRequest, UpdateDisputeRequest,
    AuditEntry, AuditEventType, CreateAuditEntryRequest,
    QLDBDashboardStats, QLDBHealthResponse,
    DisputesResponse, AuditEntriesResponse, VerificationResponse
)
from qldb_service import get_qldb_service, QLDBService

router = APIRouter(prefix="/qldb", tags=["AWS QLDB Dispute Ledger"])

DEFAULT_USER_ID = "user_001"
DEFAULT_USER_NAME = "System User"


def get_service() -> QLDBService:
    """Get the QLDB service"""
    service = get_qldb_service()
    if service is None:
        raise HTTPException(status_code=503, detail="QLDB service not initialized")
    return service


# ==================== Health & Dashboard ====================

@router.get("/health", response_model=QLDBHealthResponse)
async def health_check(service: QLDBService = Depends(get_service)):
    """Health check endpoint"""
    return await service.check_health()


@router.get("/dashboard", response_model=QLDBDashboardStats)
async def get_dashboard_stats(service: QLDBService = Depends(get_service)):
    """Get comprehensive dashboard statistics"""
    return await service.get_dashboard_stats()


# ==================== Disputes ====================

@router.post("/disputes", response_model=Dispute)
async def create_dispute(
    request: CreateDisputeRequest,
    user_id: str = Query(default=DEFAULT_USER_ID),
    service: QLDBService = Depends(get_service)
):
    """Create a new dispute - recorded immutably in ledger"""
    return await service.create_dispute(request, user_id)


@router.get("/disputes", response_model=DisputesResponse)
async def list_disputes(
    status: Optional[str] = Query(None, description="Filter by status"),
    dispute_type: Optional[str] = Query(None, description="Filter by dispute type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: QLDBService = Depends(get_service)
):
    """List disputes with optional filtering"""
    status_enum = DisputeStatus(status) if status else None
    type_enum = DisputeType(dispute_type) if dispute_type else None
    priority_enum = Priority(priority) if priority else None
    
    disputes, total = await service.get_disputes(
        status=status_enum,
        dispute_type=type_enum,
        priority=priority_enum,
        limit=limit,
        offset=offset
    )
    
    return DisputesResponse(
        success=True,
        disputes=disputes,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/disputes/{dispute_id}", response_model=Dispute)
async def get_dispute(
    dispute_id: str,
    service: QLDBService = Depends(get_service)
):
    """Get a specific dispute"""
    dispute = await service.get_dispute(dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


@router.patch("/disputes/{dispute_id}", response_model=Dispute)
async def update_dispute(
    dispute_id: str,
    update: UpdateDisputeRequest,
    user_id: str = Query(default=DEFAULT_USER_ID),
    user_name: str = Query(default=DEFAULT_USER_NAME),
    service: QLDBService = Depends(get_service)
):
    """Update a dispute - all changes are recorded in audit trail"""
    dispute = await service.update_dispute(dispute_id, update, user_id, user_name)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


@router.post("/disputes/{dispute_id}/evidence", response_model=Dispute)
async def add_evidence(
    dispute_id: str,
    evidence_type: str = Query(..., description="Type of evidence: document, audio, video, contract, statement"),
    title: str = Query(...),
    description: Optional[str] = Query(None),
    file_url: Optional[str] = Query(None),
    user_id: str = Query(default=DEFAULT_USER_ID),
    user_name: str = Query(default=DEFAULT_USER_NAME),
    service: QLDBService = Depends(get_service)
):
    """Add evidence to a dispute"""
    evidence = DisputeEvidence(
        evidence_type=evidence_type,
        title=title,
        description=description,
        file_url=file_url,
        submitted_by=user_id
    )
    
    dispute = await service.add_evidence(dispute_id, evidence, user_id, user_name)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


@router.post("/disputes/{dispute_id}/comments", response_model=Dispute)
async def add_comment(
    dispute_id: str,
    content: str = Query(...),
    is_internal: bool = Query(False),
    user_id: str = Query(default=DEFAULT_USER_ID),
    user_name: str = Query(default=DEFAULT_USER_NAME),
    service: QLDBService = Depends(get_service)
):
    """Add comment to a dispute"""
    comment = DisputeComment(
        author_id=user_id,
        author_name=user_name,
        content=content,
        is_internal=is_internal
    )
    
    dispute = await service.add_comment(dispute_id, comment)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


# ==================== Audit Trail ====================

@router.get("/audit", response_model=AuditEntriesResponse)
async def list_audit_entries(
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: QLDBService = Depends(get_service)
):
    """List audit trail entries"""
    event_enum = AuditEventType(event_type) if event_type else None
    
    entries, total = await service.get_audit_entries(
        entity_id=entity_id,
        entity_type=entity_type,
        event_type=event_enum,
        actor_id=actor_id,
        limit=limit,
        offset=offset
    )
    
    return AuditEntriesResponse(
        success=True,
        entries=entries,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/audit/{entry_id}/verify", response_model=VerificationResponse)
async def verify_audit_entry(
    entry_id: str,
    service: QLDBService = Depends(get_service)
):
    """Verify the cryptographic integrity of an audit entry"""
    return await service.verify_audit_entry(entry_id)


@router.get("/audit/chain/verify")
async def verify_chain_integrity(service: QLDBService = Depends(get_service)):
    """Verify the integrity of the entire audit chain"""
    return await service.verify_chain_integrity()


@router.get("/disputes/{dispute_id}/audit", response_model=AuditEntriesResponse)
async def get_dispute_audit_trail(
    dispute_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: QLDBService = Depends(get_service)
):
    """Get audit trail for a specific dispute"""
    entries, total = await service.get_audit_entries(
        entity_id=dispute_id,
        limit=limit,
        offset=offset
    )
    
    return AuditEntriesResponse(
        success=True,
        entries=entries,
        total=total,
        limit=limit,
        offset=offset
    )


# ==================== Reference Data ====================

@router.get("/dispute-types")
async def get_dispute_types():
    """Get available dispute types"""
    return {
        "dispute_types": [
            {"id": "ROYALTY_DISPUTE", "name": "Royalty Dispute", "description": "Disputes related to royalty payments"},
            {"id": "CONTRACT_DISPUTE", "name": "Contract Dispute", "description": "Disputes over contract terms"},
            {"id": "PAYMENT_DISPUTE", "name": "Payment Dispute", "description": "General payment-related disputes"},
            {"id": "COPYRIGHT_CLAIM", "name": "Copyright Claim", "description": "Copyright infringement claims"},
            {"id": "OWNERSHIP_DISPUTE", "name": "Ownership Dispute", "description": "Disputes over asset ownership"},
            {"id": "LICENSING_ISSUE", "name": "Licensing Issue", "description": "Licensing term disputes"},
            {"id": "DISTRIBUTION_DISPUTE", "name": "Distribution Dispute", "description": "Distribution agreement disputes"},
            {"id": "OTHER", "name": "Other", "description": "Other dispute types"}
        ]
    }


@router.get("/dispute-statuses")
async def get_dispute_statuses():
    """Get available dispute statuses"""
    return {
        "statuses": [
            {"id": "OPEN", "name": "Open", "description": "Newly filed dispute", "color": "#dc2626"},
            {"id": "UNDER_REVIEW", "name": "Under Review", "description": "Being reviewed by team", "color": "#ca8a04"},
            {"id": "RESOLVED", "name": "Resolved", "description": "Successfully resolved", "color": "#16a34a"},
            {"id": "ESCALATED", "name": "Escalated", "description": "Escalated to higher authority", "color": "#ea580c"},
            {"id": "CLOSED", "name": "Closed", "description": "Closed without resolution", "color": "#6b7280"},
            {"id": "REJECTED", "name": "Rejected", "description": "Dispute rejected", "color": "#9ca3af"}
        ]
    }


@router.get("/priorities")
async def get_priorities():
    """Get priority levels"""
    return {
        "priorities": [
            {"id": "LOW", "name": "Low", "description": "Low priority", "color": "#2563eb"},
            {"id": "MEDIUM", "name": "Medium", "description": "Medium priority", "color": "#ca8a04"},
            {"id": "HIGH", "name": "High", "description": "High priority", "color": "#ea580c"},
            {"id": "CRITICAL", "name": "Critical", "description": "Critical priority", "color": "#dc2626"}
        ]
    }


@router.get("/event-types")
async def get_event_types():
    """Get audit event types"""
    return {
        "event_types": [
            {"id": "DISPUTE_CREATED", "name": "Dispute Created"},
            {"id": "DISPUTE_UPDATED", "name": "Dispute Updated"},
            {"id": "DISPUTE_STATUS_CHANGED", "name": "Status Changed"},
            {"id": "DISPUTE_RESOLVED", "name": "Dispute Resolved"},
            {"id": "EVIDENCE_ADDED", "name": "Evidence Added"},
            {"id": "COMMENT_ADDED", "name": "Comment Added"},
            {"id": "ASSIGNMENT_CHANGED", "name": "Assignment Changed"},
            {"id": "ESCALATION", "name": "Escalation"},
            {"id": "SETTLEMENT_PROPOSED", "name": "Settlement Proposed"},
            {"id": "SETTLEMENT_ACCEPTED", "name": "Settlement Accepted"},
            {"id": "SETTLEMENT_REJECTED", "name": "Settlement Rejected"},
            {"id": "DOCUMENT_UPLOADED", "name": "Document Uploaded"},
            {"id": "VERIFICATION_COMPLETED", "name": "Verification Completed"}
        ]
    }
