"""
Content Removal Module Models
Comprehensive data models for content takedown and removal management
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from enum import Enum
import uuid

class RemovalReason(str, Enum):
    """Enumeration of removal reasons"""
    RIGHTS_REVOKED = "rights_revoked"
    LICENSING_EXPIRED = "licensing_expired"
    COPYRIGHT_DISPUTE = "copyright_dispute"
    TAKEDOWN_REQUEST = "takedown_request"
    COMPLIANCE_VIOLATION = "compliance_violation"
    DAO_VOTE = "dao_vote"
    LEGAL_ORDER = "legal_order"
    CONTENT_POLICY = "content_policy"
    ARTIST_REQUEST = "artist_request"
    ADMIN_ACTION = "admin_action"

class RemovalStatus(str, Enum):
    """Status of removal request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class RemovalUrgency(str, Enum):
    """Urgency level for removal"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    LEGAL = "legal"

class PlatformRemovalStatus(str, Enum):
    """Status of removal on specific platform"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"

class DisputeStatus(str, Enum):
    """Status of dispute resolution"""
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    AWAITING_EVIDENCE = "awaiting_evidence"
    RESOLVED = "resolved"
    CLOSED = "closed"

class RemovalEvidence(BaseModel):
    """Evidence supporting removal request"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str
    file_type: str  # legal_notice, dao_vote, correspondence, screenshot
    file_name: str
    file_size: int
    mime_type: str
    description: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PlatformRemovalResult(BaseModel):
    """Result of removal attempt on specific platform"""
    platform_id: str
    platform_name: str
    status: PlatformRemovalStatus
    attempted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    confirmation_id: Optional[str] = None
    ddex_message_id: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = {}

class DAOVoteDetails(BaseModel):
    """Details of DAO governance vote for removal"""
    proposal_id: str
    vote_result: str  # approved, rejected
    total_votes: int
    approval_votes: int
    rejection_votes: int
    vote_percentage: float
    voting_deadline: datetime
    completed_at: datetime
    blockchain_tx_hash: Optional[str] = None
    smart_contract_address: Optional[str] = None

class RemovalRequest(BaseModel):
    """Main removal request model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Content Information
    content_id: str
    content_title: str
    content_type: str  # audio, video, image, album, playlist
    artist_name: Optional[str] = None
    release_id: Optional[str] = None
    isrc_code: Optional[str] = None
    upc_code: Optional[str] = None
    
    # Request Details
    reason: RemovalReason
    urgency: RemovalUrgency = RemovalUrgency.MEDIUM
    description: str
    requested_by: str  # User ID
    requester_role: str  # creator, admin, dao, legal
    
    # Platforms and Scope
    target_platforms: List[str] = []  # Empty means all platforms
    territory_scope: str = "worldwide"  # worldwide, US, EU, etc.
    effective_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Evidence and Documentation
    evidence_files: List[RemovalEvidence] = []
    legal_notice_ref: Optional[str] = None
    dao_vote_details: Optional[DAOVoteDetails] = None
    
    # Status and Processing
    status: RemovalStatus = RemovalStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Platform Removal Results
    platform_results: List[PlatformRemovalResult] = []
    
    # Royalty Impact
    royalty_suspended: bool = False
    royalty_suspension_date: Optional[datetime] = None
    estimated_revenue_impact: Optional[float] = None
    
    # Audit Trail
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Additional Metadata
    metadata: Dict[str, Any] = {}

class RemovalRequestCreate(BaseModel):
    """Model for creating removal request"""
    content_id: str
    reason: RemovalReason
    urgency: RemovalUrgency = RemovalUrgency.MEDIUM
    description: str
    target_platforms: List[str] = []
    territory_scope: str = "worldwide"
    effective_date: Optional[datetime] = None
    legal_notice_ref: Optional[str] = None

class RemovalRequestUpdate(BaseModel):
    """Model for updating removal request"""
    status: Optional[RemovalStatus] = None
    rejection_reason: Optional[str] = None
    target_platforms: Optional[List[str]] = None
    territory_scope: Optional[str] = None
    effective_date: Optional[datetime] = None

class DisputeRequest(BaseModel):
    """Dispute against removal request"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    removal_request_id: str
    disputed_by: str  # User ID
    dispute_reason: str
    evidence_description: str
    evidence_files: List[RemovalEvidence] = []
    status: DisputeStatus = DisputeStatus.OPEN
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

class DDEXTakedownMessage(BaseModel):
    """DDEX ERN Takedown Message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    removal_request_id: str
    message_sender: str = "BigMannEntertainment"
    message_recipient: str
    release_id: str
    takedown_reason: str
    effective_date: datetime
    territory_code: str = "Worldwide"
    xml_content: str
    sent_at: Optional[datetime] = None
    delivery_status: str = "pending"  # pending, sent, delivered, failed
    delivery_attempts: int = 0
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RemovalAnalytics(BaseModel):
    """Analytics and reporting for removal requests"""
    total_requests: int = 0
    pending_requests: int = 0
    approved_requests: int = 0
    completed_requests: int = 0
    disputed_requests: int = 0
    
    # By reason
    requests_by_reason: Dict[str, int] = {}
    
    # By platform
    requests_by_platform: Dict[str, int] = {}
    
    # Time-based metrics
    average_processing_time_hours: float = 0.0
    fastest_completion_hours: float = 0.0
    slowest_completion_hours: float = 0.0
    
    # Revenue impact
    total_revenue_suspended: float = 0.0
    estimated_revenue_loss: float = 0.0
    
    # Compliance metrics
    legal_removal_count: int = 0
    dao_removal_count: int = 0
    admin_removal_count: int = 0
    creator_removal_count: int = 0

class ComplianceReport(BaseModel):
    """Compliance reporting for removal activities"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str  # monthly, quarterly, annual, incident
    period_start: datetime
    period_end: datetime
    
    # Summary statistics
    total_removals: int = 0
    legal_removals: int = 0
    voluntary_removals: int = 0
    disputed_removals: int = 0
    
    # Platform breakdown
    platform_statistics: Dict[str, Dict[str, int]] = {}
    
    # Revenue impact
    revenue_impact_summary: Dict[str, float] = {}
    
    # Compliance status
    compliance_score: float = 0.0
    outstanding_issues: List[str] = []
    recommendations: List[str] = []
    
    generated_by: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_path: Optional[str] = None