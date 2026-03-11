"""
AWS-Powered Modeling Agency Platform Models
Comprehensive data models for AWS-integrated agency management
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============== Image & Portfolio Management Models ==============

class ImageMetadata(BaseModel):
    """Image metadata extracted from Rekognition"""
    faces_detected: int = 0
    labels: List[str] = []
    moderation_labels: List[str] = []
    dominant_colors: List[str] = []
    exif_data: Dict[str, Any] = {}
    ai_confidence: float = 0.0

class PortfolioImage(BaseModel):
    """Individual portfolio image"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str
    agency_id: str
    s3_key: str
    s3_bucket: str
    cloudfront_url: str
    thumbnail_url: Optional[str] = None
    file_size: int
    dimensions: Dict[str, int]  # {width, height}
    format: str  # jpeg, png, etc.
    metadata: ImageMetadata
    tags: List[str] = []
    is_public: bool = False
    license_status: str = "available"  # available, licensed, exclusive
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class ModelPortfolio(BaseModel):
    """Complete model portfolio"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str
    model_name: str
    agency_id: str
    agency_name: str
    bio: Optional[str] = None
    measurements: Dict[str, Any] = {}
    experience_years: Optional[int] = None
    categories: List[str] = []  # fashion, commercial, fitness, etc.
    images: List[PortfolioImage] = []
    total_images: int = 0
    public_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Smart Licensing & Royalty Engine Models ==============

class LicenseType(str, Enum):
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    PRINT = "print"
    DIGITAL = "digital"
    WORLDWIDE = "worldwide"
    REGIONAL = "regional"

class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BASE = "base"

class SmartLicense(BaseModel):
    """Smart contract-based license"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_type: LicenseType
    image_id: str
    model_id: str
    agency_id: str
    licensee_id: str
    licensee_name: str
    blockchain_network: BlockchainNetwork
    contract_address: Optional[str] = None
    token_id: Optional[str] = None
    nft_metadata_uri: Optional[str] = None
    license_fee: float
    currency: str = "USD"
    royalty_percentage: float = 10.0
    duration_days: Optional[int] = None
    usage_rights: List[str] = []
    territory: str = "worldwide"
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, expired, terminated
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RoyaltyPayment(BaseModel):
    """Royalty payment record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_id: str
    model_id: str
    agency_id: str
    amount: float
    currency: str
    fx_rate: float = 1.0
    usd_equivalent: float
    tax_withheld: float = 0.0
    net_amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"


# ============== Agency Onboarding & Compliance Models ==============

class KYCStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESUBMISSION_REQUIRED = "resubmission_required"

class AgencyOnboarding(BaseModel):
    """Agency onboarding record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_name: str
    business_registration_number: str
    country: str
    contact_email: EmailStr
    contact_phone: str
    kyc_status: KYCStatus = KYCStatus.PENDING
    documents: List[Dict[str, str]] = []  # [{type, s3_key, upload_date}]
    verification_notes: Optional[str] = None
    cognito_user_id: Optional[str] = None
    step_function_execution_arn: Optional[str] = None
    current_step: str = "registration"
    completed_steps: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

class ComplianceDocument(BaseModel):
    """Compliance document (release forms, contracts, IDs)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str  # model_release, agency_contract, id_verification, etc.
    model_id: Optional[str] = None
    agency_id: str
    s3_key: str
    s3_bucket: str
    file_name: str
    file_size: int
    macie_scan_status: str = "pending"  # pending, clean, flagged
    macie_findings: List[str] = []
    expiry_date: Optional[datetime] = None
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(BaseModel):
    """Immutable audit log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # onboarding_step, license_created, payment_processed, etc.
    actor_id: str
    actor_type: str  # agency, model, admin
    resource_type: str  # portfolio, license, payment, etc.
    resource_id: str
    action: str
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    cloudtrail_event_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============== Support System & DAO Disputes Models ==============

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_RESPONSE = "waiting_response"
    RESOLVED = "resolved"
    CLOSED = "closed"

class SupportTicket(BaseModel):
    """Support ticket"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_number: str
    user_id: str
    user_type: str  # model, agency, licensee
    category: str  # technical, licensing, payment, dispute
    subject: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    assigned_agent: Optional[str] = None
    amazon_connect_contact_id: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    attachments: List[str] = []  # S3 keys
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class DAODispute(BaseModel):
    """DAO dispute case"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dispute_type: str  # license_violation, payment_dispute, content_dispute
    plaintiff_id: str
    defendant_id: str
    license_id: Optional[str] = None
    description: str
    evidence: List[str] = []  # S3 keys for evidence uploads
    qldb_ledger_id: Optional[str] = None
    blockchain_vote_contract: Optional[str] = None
    voting_start_date: datetime
    voting_end_date: datetime
    votes_for: int = 0
    votes_against: int = 0
    total_votes: int = 0
    resolution: Optional[str] = None
    status: str = "voting"  # voting, resolved, appealed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class DisputeVote(BaseModel):
    """Individual dispute vote"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dispute_id: str
    voter_id: str
    vote: str  # for, against, abstain
    voting_power: float = 1.0
    blockchain_tx_hash: Optional[str] = None
    qldb_document_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============== Knowledge-Based Work Instructions (KBWI) Models ==============

class KBWICategory(str, Enum):
    ONBOARDING = "onboarding"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    LICENSING = "licensing"
    COMPLIANCE = "compliance"
    SUPPORT = "support"
    TECHNICAL = "technical"

class KBWIUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class KBWIDocument(BaseModel):
    """Knowledge-based work instruction"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: KBWICategory
    urgency: KBWIUrgency
    role_access: List[str] = []  # agency_admin, model, support_agent, etc.
    content: str  # Markdown or HTML
    tags: List[str] = []
    s3_key: Optional[str] = None
    amplify_url: Optional[str] = None
    search_keywords: List[str] = []
    version: str = "1.0"
    helpful_count: int = 0
    not_helpful_count: int = 0
    views: int = 0
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class KBWIFeedback(BaseModel):
    """KBWI feedback"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kbwi_id: str
    user_id: str
    was_helpful: bool
    comments: Optional[str] = None
    suggested_improvements: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============== Security & Monitoring Models ==============

class AccessLog(BaseModel):
    """Access control log"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_type: str
    resource_type: str
    resource_id: str
    action: str  # read, write, delete, etc.
    access_granted: bool
    iam_role: Optional[str] = None
    ip_address: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SecurityAlert(BaseModel):
    """Security monitoring alert"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str  # fraud_detection, unusual_access, data_breach_attempt
    severity: str  # low, medium, high, critical
    description: str
    affected_resources: List[str] = []
    cloudwatch_alarm_name: Optional[str] = None
    sns_notification_sent: bool = False
    remediation_steps: List[str] = []
    status: str = "open"  # open, investigating, resolved
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class BackupRecord(BaseModel):
    """Backup and recovery record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    backup_type: str  # daily, weekly, monthly, on_demand
    resources: List[str] = []  # dynamodb_tables, s3_buckets, etc.
    aws_backup_job_id: Optional[str] = None
    s3_backup_location: Optional[str] = None
    backup_size_bytes: int = 0
    status: str = "completed"
    started_at: datetime
    completed_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Dashboard & Analytics Models ==============

class AgencyDashboard(BaseModel):
    """Agency platform dashboard data"""
    agency_id: str
    total_models: int = 0
    total_portfolios: int = 0
    total_images: int = 0
    active_licenses: int = 0
    total_revenue: float = 0.0
    pending_royalties: float = 0.0
    open_tickets: int = 0
    pending_disputes: int = 0
    compliance_score: float = 100.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
