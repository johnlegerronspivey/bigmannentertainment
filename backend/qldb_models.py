"""
AWS QLDB Integration - Pydantic Models
Immutable audit trails for dispute resolution
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class DisputeStatus(str, Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    MEDIATION = "mediation"
    ARBITRATION = "arbitration"
    RESOLVED = "resolved"
    CLOSED = "closed"
    APPEALED = "appealed"


class DisputeCategory(str, Enum):
    ROYALTY_DISPUTE = "royalty_dispute"
    CONTRACT_BREACH = "contract_breach"
    COPYRIGHT_CLAIM = "copyright_claim"
    PAYMENT_ISSUE = "payment_issue"
    LICENSE_VIOLATION = "license_violation"
    OWNERSHIP_DISPUTE = "ownership_dispute"
    DISTRIBUTION_RIGHTS = "distribution_rights"
    OTHER = "other"


class TransactionType(str, Enum):
    DISPUTE_CREATED = "DISPUTE_CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    EVIDENCE_ADDED = "EVIDENCE_ADDED"
    PARTY_ADDED = "PARTY_ADDED"
    COMMENT_ADDED = "COMMENT_ADDED"
    AMOUNT_ADJUSTED = "AMOUNT_ADJUSTED"
    RESOLUTION_PROPOSED = "RESOLUTION_PROPOSED"
    RESOLUTION_ACCEPTED = "RESOLUTION_ACCEPTED"
    RESOLUTION_REJECTED = "RESOLUTION_REJECTED"
    APPEAL_FILED = "APPEAL_FILED"
    CLOSED = "CLOSED"


class PartyRole(str, Enum):
    INITIATOR = "initiator"
    RESPONDENT = "respondent"
    MEDIATOR = "mediator"
    ARBITRATOR = "arbitrator"
    WITNESS = "witness"
    REPRESENTATIVE = "representative"


class EvidenceType(str, Enum):
    DOCUMENT = "document"
    CONTRACT = "contract"
    COMMUNICATION = "communication"
    FINANCIAL_RECORD = "financial_record"
    AUDIO_RECORDING = "audio_recording"
    VIDEO_EVIDENCE = "video_evidence"
    SCREENSHOT = "screenshot"
    OTHER = "other"


# Party Models
class Party(BaseModel):
    """Party involved in a dispute"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    party_id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: PartyRole = PartyRole.INITIATOR
    organization: Optional[str] = None
    address: Optional[str] = None
    representative_name: Optional[str] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class CreatePartyRequest(BaseModel):
    party_id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: PartyRole = PartyRole.INITIATOR
    organization: Optional[str] = None


# Evidence Models
class Evidence(BaseModel):
    """Evidence submitted for a dispute"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_id: str = Field(default_factory=lambda: f"EVD-{uuid.uuid4().hex[:8].upper()}")
    dispute_id: str
    
    # Evidence details
    title: str
    description: Optional[str] = None
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    
    # File info
    file_name: str
    file_type: str
    file_size: int = 0
    s3_location: str
    
    # Submission info
    submitted_by: str
    submitted_by_name: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Verification
    hash_sha256: Optional[str] = None
    is_verified: bool = False
    verified_at: Optional[datetime] = None


class AddEvidenceRequest(BaseModel):
    title: str
    description: Optional[str] = None
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    file_name: str
    file_type: str
    file_size: int = 0
    s3_location: str
    submitted_by: str
    submitted_by_name: str


# Transaction Models (Audit Trail Entries)
class AuditTransaction(BaseModel):
    """Immutable transaction record in the ledger"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str = Field(default_factory=lambda: f"TXN-{uuid.uuid4().hex[:12].upper()}")
    dispute_id: str
    
    # Transaction details
    transaction_type: TransactionType
    action: str
    description: str
    
    # Actor info
    actor_id: str
    actor_name: str
    actor_role: Optional[str] = None
    
    # State changes
    old_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Ledger info (populated after insertion)
    block_address: Optional[Dict[str, Any]] = None
    document_id: Optional[str] = None
    version: int = 1


class RecordTransactionRequest(BaseModel):
    transaction_type: TransactionType
    action: str
    description: str
    actor_id: str
    actor_name: str
    actor_role: Optional[str] = None
    old_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Dispute Models
class Dispute(BaseModel):
    """Dispute record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dispute_id: str = Field(default_factory=lambda: f"DSP-{uuid.uuid4().hex[:8].upper()}")
    
    # Dispute details
    title: str
    description: str
    category: DisputeCategory = DisputeCategory.OTHER
    status: DisputeStatus = DisputeStatus.OPEN
    
    # Parties
    initiating_party_id: str
    responding_party_id: str
    parties: List[Party] = []
    
    # Financial
    disputed_amount: Optional[float] = None
    settled_amount: Optional[float] = None
    currency: str = "USD"
    
    # Related entities
    related_contract_id: Optional[str] = None
    related_asset_ids: List[str] = []
    
    # Resolution
    resolution_summary: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    # Evidence
    evidence_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    
    # Ledger info
    ledger_document_id: Optional[str] = None


class CreateDisputeRequest(BaseModel):
    title: str
    description: str
    category: DisputeCategory = DisputeCategory.OTHER
    initiating_party_id: str
    responding_party_id: str
    parties: List[CreatePartyRequest] = []
    disputed_amount: Optional[float] = None
    currency: str = "USD"
    related_contract_id: Optional[str] = None
    related_asset_ids: List[str] = []
    due_date: Optional[datetime] = None


class UpdateDisputeRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DisputeStatus] = None
    disputed_amount: Optional[float] = None
    settled_amount: Optional[float] = None
    resolution_summary: Optional[str] = None
    due_date: Optional[datetime] = None


# Verification Models
class LedgerDigest(BaseModel):
    """Ledger digest for verification"""
    digest: str  # Base64 encoded
    digest_tip_address: Dict[str, Any]
    ledger_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VerificationRequest(BaseModel):
    document_id: str
    block_address: Dict[str, Any]
    digest: str  # Base64 encoded digest to verify against


class VerificationResult(BaseModel):
    """Result of cryptographic verification"""
    verified: bool
    document_id: str
    block_address: Dict[str, Any]
    revision_hash: Optional[str] = None
    proof_hash: Optional[str] = None
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: str = ""


# History Models
class DocumentRevision(BaseModel):
    """Single revision of a document"""
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    block_address: Dict[str, Any]
    version: int


class DocumentHistory(BaseModel):
    """Complete history of a document"""
    document_id: str
    dispute_id: str
    revisions: List[DocumentRevision] = []
    total_revisions: int = 0


# Dashboard Stats
class QLDBDashboardStats(BaseModel):
    """QLDB dashboard statistics"""
    # Dispute counts
    total_disputes: int = 0
    open_disputes: int = 0
    in_review_disputes: int = 0
    resolved_disputes: int = 0
    closed_disputes: int = 0
    
    # Transaction counts
    total_transactions: int = 0
    transactions_today: int = 0
    transactions_this_week: int = 0
    
    # Evidence counts
    total_evidence: int = 0
    
    # Financial
    total_disputed_amount: float = 0.0
    total_settled_amount: float = 0.0
    average_disputed_amount: float = 0.0
    
    # By category
    disputes_by_category: Dict[str, int] = {}
    
    # Ledger info
    ledger_name: str = ""
    ledger_status: str = "ACTIVE"
    is_connected: bool = False
    
    # Recent activity
    recent_transactions: List[AuditTransaction] = []
    
    # Timestamps
    last_transaction_time: Optional[datetime] = None


# Health Response
class QLDBHealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "AWS QLDB Immutable Audit Trail"
    version: str = "1.0.0"
    ledger_name: str = ""
    ledger_status: str = "UNKNOWN"
    aws_connected: bool = False
    aws_region: str = "us-east-1"
    features: List[str] = []
