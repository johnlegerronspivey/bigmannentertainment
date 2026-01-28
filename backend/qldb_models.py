"""
AWS QLDB Integration - Pydantic Models
Immutable dispute ledger and audit trail system
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import hashlib


class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


class DisputeType(str, Enum):
    ROYALTY_DISPUTE = "ROYALTY_DISPUTE"
    CONTRACT_DISPUTE = "CONTRACT_DISPUTE"
    PAYMENT_DISPUTE = "PAYMENT_DISPUTE"
    COPYRIGHT_CLAIM = "COPYRIGHT_CLAIM"
    OWNERSHIP_DISPUTE = "OWNERSHIP_DISPUTE"
    LICENSING_ISSUE = "LICENSING_ISSUE"
    DISTRIBUTION_DISPUTE = "DISTRIBUTION_DISPUTE"
    OTHER = "OTHER"


class AuditEventType(str, Enum):
    DISPUTE_CREATED = "DISPUTE_CREATED"
    DISPUTE_UPDATED = "DISPUTE_UPDATED"
    DISPUTE_STATUS_CHANGED = "DISPUTE_STATUS_CHANGED"
    DISPUTE_RESOLVED = "DISPUTE_RESOLVED"
    EVIDENCE_ADDED = "EVIDENCE_ADDED"
    COMMENT_ADDED = "COMMENT_ADDED"
    ASSIGNMENT_CHANGED = "ASSIGNMENT_CHANGED"
    ESCALATION = "ESCALATION"
    SETTLEMENT_PROPOSED = "SETTLEMENT_PROPOSED"
    SETTLEMENT_ACCEPTED = "SETTLEMENT_ACCEPTED"
    SETTLEMENT_REJECTED = "SETTLEMENT_REJECTED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Dispute Models
class DisputeParty(BaseModel):
    """Party involved in a dispute"""
    party_id: str
    party_type: str  # claimant, respondent, mediator
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None


class DisputeEvidence(BaseModel):
    """Evidence submitted for a dispute"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str  # document, audio, video, contract, statement
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_hash: Optional[str] = None
    submitted_by: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False


class DisputeComment(BaseModel):
    """Comment on a dispute"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    author_name: str
    content: str
    is_internal: bool = False  # Internal notes vs public comments
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DisputeSettlement(BaseModel):
    """Settlement proposal for a dispute"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposed_by: str
    proposed_amount: Optional[float] = None
    proposed_terms: str
    status: str = "pending"  # pending, accepted, rejected, counter
    created_at: datetime = Field(default_factory=datetime.utcnow)
    response_by: Optional[str] = None
    response_at: Optional[datetime] = None
    response_notes: Optional[str] = None


class Dispute(BaseModel):
    """Main dispute record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dispute_number: Optional[str] = None  # Human-readable dispute number
    
    # Classification
    type: DisputeType
    status: DisputeStatus = DisputeStatus.OPEN
    priority: Priority = Priority.MEDIUM
    
    # Details
    title: str
    description: str
    amount_disputed: Optional[float] = None
    currency: str = "USD"
    
    # Related entities
    related_asset_id: Optional[str] = None
    related_contract_id: Optional[str] = None
    related_transaction_id: Optional[str] = None
    
    # Parties
    claimant: DisputeParty
    respondent: Optional[DisputeParty] = None
    mediator: Optional[DisputeParty] = None
    
    # Evidence and comments
    evidence: List[DisputeEvidence] = []
    comments: List[DisputeComment] = []
    settlements: List[DisputeSettlement] = []
    
    # Assignment
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    
    # Resolution
    resolution_summary: Optional[str] = None
    resolution_amount: Optional[float] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Immutability
    ledger_document_id: Optional[str] = None
    content_hash: Optional[str] = None


class CreateDisputeRequest(BaseModel):
    """Request to create a new dispute"""
    type: DisputeType
    title: str
    description: str
    amount_disputed: Optional[float] = None
    currency: str = "USD"
    priority: Priority = Priority.MEDIUM
    
    related_asset_id: Optional[str] = None
    related_contract_id: Optional[str] = None
    
    claimant_name: str
    claimant_email: Optional[str] = None
    
    respondent_name: Optional[str] = None
    respondent_email: Optional[str] = None


class UpdateDisputeRequest(BaseModel):
    """Request to update a dispute"""
    status: Optional[DisputeStatus] = None
    priority: Optional[Priority] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_summary: Optional[str] = None
    resolution_amount: Optional[float] = None


# Audit Trail Models
class AuditEntry(BaseModel):
    """Immutable audit log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Event classification
    event_type: AuditEventType
    entity_type: str  # dispute, settlement, evidence, etc.
    entity_id: str
    
    # Actor information
    actor_id: str
    actor_name: str
    actor_role: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Change details
    action_description: str
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    change_summary: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    # Immutability verification
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    ledger_document_id: Optional[str] = None
    
    # Verification status
    verified: bool = False
    verification_proof: Optional[Dict[str, Any]] = None


class CreateAuditEntryRequest(BaseModel):
    """Request to create an audit entry"""
    event_type: AuditEventType
    entity_type: str
    entity_id: str
    actor_id: str
    actor_name: str
    action_description: str
    change_summary: Optional[str] = None
    metadata: Dict[str, Any] = {}


# Dashboard Statistics
class DisputeStats(BaseModel):
    """Dispute statistics"""
    total_disputes: int = 0
    open_disputes: int = 0
    under_review: int = 0
    resolved_disputes: int = 0
    escalated_disputes: int = 0
    
    # By type
    disputes_by_type: Dict[str, int] = {}
    
    # By priority
    critical_count: int = 0
    high_priority_count: int = 0
    
    # Financial
    total_amount_disputed: float = 0.0
    total_amount_resolved: float = 0.0
    average_resolution_time_days: float = 0.0


class AuditStats(BaseModel):
    """Audit trail statistics"""
    total_entries: int = 0
    entries_last_24h: int = 0
    entries_last_7d: int = 0
    
    # By event type
    entries_by_type: Dict[str, int] = {}
    
    # Verification
    verified_entries: int = 0
    pending_verification: int = 0


class QLDBDashboardStats(BaseModel):
    """Complete dashboard statistics"""
    dispute_stats: DisputeStats = DisputeStats()
    audit_stats: AuditStats = AuditStats()
    
    # Recent activity
    recent_disputes: List[Dispute] = []
    recent_audit_entries: List[AuditEntry] = []
    
    # Chain integrity
    chain_verified: bool = True
    last_verification_time: Optional[datetime] = None
    total_documents: int = 0


# API Response Models
class DisputesResponse(BaseModel):
    """Paginated disputes response"""
    success: bool = True
    disputes: List[Dispute] = []
    total: int = 0
    limit: int = 50
    offset: int = 0


class AuditEntriesResponse(BaseModel):
    """Paginated audit entries response"""
    success: bool = True
    entries: List[AuditEntry] = []
    total: int = 0
    limit: int = 50
    offset: int = 0


class VerificationResponse(BaseModel):
    """Document verification response"""
    document_id: str
    verified: bool
    content_hash: Optional[str] = None
    chain_valid: bool = True
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)
    proof: Optional[Dict[str, Any]] = None


class QLDBHealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "AWS QLDB Dispute Ledger"
    version: str = "1.0.0"
    ledger_active: bool = True
    chain_integrity: bool = True
    aws_region: str = "us-east-1"
    features: List[str] = []


# Utility Functions
def compute_content_hash(data: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of content for immutability verification"""
    import json
    content_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content_str.encode()).hexdigest()


def compute_chain_hash(content_hash: str, previous_hash: str) -> str:
    """Compute chained hash for audit trail integrity"""
    combined = f"{previous_hash}{content_hash}"
    return hashlib.sha256(combined.encode()).hexdigest()
