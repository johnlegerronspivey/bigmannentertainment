"""
Unified Label Network (ULN) Models
==================================

Comprehensive models for the ULN system including:
- Label Registry with Global Label IDs
- Cross-label content sharing and metadata
- Multi-label royalty engine and distribution
- Smart contract templates and governance
- Compliance and jurisdiction-aware logic
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from enum import Enum
import uuid

# ===== ENUMS AND CONSTANTS =====

class LabelType(str, Enum):
    MAJOR = "major"
    INDEPENDENT = "independent"
    DISTRIBUTION = "distribution"
    PUBLISHING = "publishing"
    MANAGEMENT = "management"

class IntegrationType(str, Enum):
    FULL_INTEGRATION = "full_integration"
    API_PARTNER = "api_partner"
    DISTRIBUTION_ONLY = "distribution_only"
    METADATA_SYNC = "metadata_sync"
    CONTENT_SHARING = "content_sharing"

class ContractType(str, Enum):
    RECORDING = "recording"
    DISTRIBUTION = "distribution"
    PUBLISHING = "publishing"
    MANAGEMENT = "management"
    LICENSING = "licensing"
    CROSS_LABEL = "cross_label"

class TerritoryJurisdiction(str, Enum):
    US = "US"
    UK = "UK"
    EU = "EU"
    CA = "CA"
    AU = "AU"
    JP = "JP"
    GLOBAL = "GLOBAL"

class RoyaltyType(str, Enum):
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    SYNC = "sync"
    MASTER = "master"
    PUBLISHING = "publishing"
    STREAMING = "streaming"

class DAOVoteType(str, Enum):
    CONTENT_APPROVAL = "content_approval"
    TAKEDOWN_REQUEST = "takedown_request"
    ROYALTY_SPLIT_CHANGE = "royalty_split_change"
    CROSS_LABEL_AGREEMENT = "cross_label_agreement"
    COMPLIANCE_OVERRIDE = "compliance_override"

# ===== CORE ULN MODELS =====

class GlobalLabelID(BaseModel):
    """Global unique identifier for labels in the ULN system"""
    id: str = Field(default_factory=lambda: f"BM-LBL-{str(uuid.uuid4())[:8].upper()}")
    verification_status: str = Field(default="pending")
    blockchain_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LabelMetadataProfile(BaseModel):
    """Comprehensive metadata profile for labels in ULN"""
    name: str
    legal_name: Optional[str] = None
    jurisdiction: TerritoryJurisdiction
    tax_status: str
    founded_date: Optional[date] = None
    headquarters: str
    business_registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    contact_information: Dict[str, Any] = Field(default_factory=dict)
    social_media_handles: Dict[str, str] = Field(default_factory=dict)
    genre_specialization: List[str] = Field(default_factory=list)
    territories_of_operation: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    industry_affiliations: List[str] = Field(default_factory=list)

class AssociatedEntity(BaseModel):
    """Creators, admins, DAO delegates associated with a label"""
    entity_id: str
    entity_type: str  # "creator", "admin", "dao_delegate", "artist", "producer"
    name: str
    role: str
    permissions: List[str] = Field(default_factory=list)
    royalty_share: float = Field(default=0.0, ge=0.0, le=1.0)
    jurisdiction: Optional[TerritoryJurisdiction] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SmartContractBinding(BaseModel):
    """Smart contract configuration for rights splits and governance"""
    contract_address: Optional[str] = None
    contract_type: ContractType
    blockchain_network: str = Field(default="ethereum")
    rights_splits: Dict[str, float] = Field(default_factory=dict)
    governance_rules: Dict[str, Any] = Field(default_factory=dict)
    payout_logic: Dict[str, Any] = Field(default_factory=dict)
    dao_integration: bool = Field(default=False)
    auto_execution: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ULNLabel(BaseModel):
    """Complete ULN Label entity with all integrations"""
    global_id: GlobalLabelID = Field(default_factory=GlobalLabelID)
    label_type: LabelType
    integration_type: IntegrationType
    metadata_profile: LabelMetadataProfile
    associated_entities: List[AssociatedEntity] = Field(default_factory=list)
    smart_contracts: List[SmartContractBinding] = Field(default_factory=list)
    
    # Label network connections
    parent_labels: List[str] = Field(default_factory=list)
    subsidiary_labels: List[str] = Field(default_factory=list)
    partner_labels: List[str] = Field(default_factory=list)
    
    # Content and rights management
    content_catalog_id: Optional[str] = None
    rights_database_id: Optional[str] = None
    
    # Financial and operational
    revenue_sharing_agreements: List[Dict[str, Any]] = Field(default_factory=list)
    operational_agreements: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Status and timestamps
    status: str = Field(default="active")
    onboarding_completed: bool = Field(default=False)
    compliance_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ===== CROSS-LABEL CONTENT SHARING =====

class ContentRights(BaseModel):
    """Rights information for cross-label content"""
    content_id: str
    rights_type: str  # "master", "publishing", "sync", "performance"
    ownership_percentage: float = Field(ge=0.0, le=100.0)
    territory_restrictions: List[str] = Field(default_factory=list)
    usage_restrictions: List[str] = Field(default_factory=list)
    expiry_date: Optional[datetime] = None
    exclusive: bool = Field(default=False)

class FederatedContentAccess(BaseModel):
    """Cross-label content access and licensing"""
    content_id: str
    primary_label_id: str
    co_owning_labels: List[str] = Field(default_factory=list)
    licensing_labels: List[str] = Field(default_factory=list)
    
    # Rights distribution
    rights_splits: Dict[str, float] = Field(default_factory=dict)  # label_id: percentage
    content_rights: List[ContentRights] = Field(default_factory=list)
    
    # Metadata and permissions
    shared_metadata: Dict[str, Any] = Field(default_factory=dict)
    role_based_permissions: Dict[str, List[str]] = Field(default_factory=dict)
    access_level: str = Field(default="read_only")  # read_only, edit_metadata, full_access
    
    # Usage tracking
    usage_attribution: Dict[str, Any] = Field(default_factory=dict)
    streams_by_label: Dict[str, int] = Field(default_factory=dict)
    revenue_by_label: Dict[str, float] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ===== MULTI-LABEL ROYALTY ENGINE =====

class RoyaltySource(BaseModel):
    """Source of royalty payments"""
    source_id: str
    source_name: str
    source_type: str  # "streaming", "radio", "sync", "live", "mechanical"
    platform: str
    territory: str
    currency: str = Field(default="USD")

class RoyaltyEarning(BaseModel):
    """Individual royalty earning record"""
    earning_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    source: RoyaltySource
    royalty_type: RoyaltyType
    gross_amount: float
    currency: str = Field(default="USD")
    period_start: date
    period_end: date
    usage_data: Dict[str, Any] = Field(default_factory=dict)  # streams, plays, etc.
    
    # Multi-label distribution
    label_splits: Dict[str, float] = Field(default_factory=dict)  # label_id: amount
    creator_splits: Dict[str, float] = Field(default_factory=dict)  # creator_id: amount
    
    # Processing status
    processed: bool = Field(default=False)
    distributed: bool = Field(default=False)
    processing_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MultiLabelRoyaltyPool(BaseModel):
    """Aggregated royalty pool for multi-label distribution"""
    pool_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pool_period: str  # "2025-Q1", "2025-01", etc.
    participating_labels: List[str]
    
    # Aggregated earnings
    total_gross_earnings: float = Field(default=0.0)
    total_net_earnings: float = Field(default=0.0)
    currency: str = Field(default="USD")
    
    # Earnings by source
    earnings_by_source: Dict[str, float] = Field(default_factory=dict)
    earnings_by_territory: Dict[str, float] = Field(default_factory=dict)
    earnings_by_type: Dict[str, float] = Field(default_factory=dict)
    
    # Distribution data
    label_allocations: Dict[str, float] = Field(default_factory=dict)
    creator_allocations: Dict[str, float] = Field(default_factory=dict)
    
    # DAO and dispute handling
    dao_overrides: List[Dict[str, Any]] = Field(default_factory=list)
    dispute_flags: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Processing status
    calculated: bool = Field(default=False)
    approved: bool = Field(default=False)
    distributed: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    distribution_date: Optional[datetime] = None

class PayoutLedger(BaseModel):
    """Transparent ledger entry for royalty payouts"""
    ledger_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pool_id: str
    recipient_id: str
    recipient_type: str  # "label", "creator", "investor"
    recipient_name: str
    
    # Payout details
    gross_amount: float
    deductions: Dict[str, float] = Field(default_factory=dict)  # taxes, fees, etc.
    net_amount: float
    currency: str = Field(default="USD")
    
    # Breakdown by source/content
    earning_breakdown: Dict[str, float] = Field(default_factory=dict)
    content_breakdown: Dict[str, float] = Field(default_factory=dict)
    
    # Transaction details
    payment_method: str
    transaction_id: Optional[str] = None
    transaction_hash: Optional[str] = None  # blockchain transaction
    
    # Status and compliance
    status: str = Field(default="pending")  # pending, processed, completed, failed
    tax_withholding: float = Field(default=0.0)
    compliance_notes: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

# ===== COMPLIANCE AND GOVERNANCE =====

class JurisdictionRules(BaseModel):
    """Jurisdiction-specific compliance rules"""
    jurisdiction: TerritoryJurisdiction
    tax_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    vat_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    withholding_requirements: Dict[str, float] = Field(default_factory=dict)
    reporting_requirements: List[str] = Field(default_factory=list)
    licensing_requirements: List[str] = Field(default_factory=list)
    data_protection_rules: List[str] = Field(default_factory=list)
    content_restrictions: List[str] = Field(default_factory=list)
    currency_restrictions: List[str] = Field(default_factory=list)

class DAOProposal(BaseModel):
    """DAO governance proposal for ULN decisions"""
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_type: DAOVoteType
    title: str
    description: str
    proposer_id: str
    
    # Proposal details
    affected_labels: List[str] = Field(default_factory=list)
    affected_content: List[str] = Field(default_factory=list)
    proposed_changes: Dict[str, Any] = Field(default_factory=dict)
    
    # Voting mechanics
    voting_power_by_label: Dict[str, float] = Field(default_factory=dict)
    votes_for: Dict[str, float] = Field(default_factory=dict)  # label_id: voting_power
    votes_against: Dict[str, float] = Field(default_factory=dict)
    votes_abstain: Dict[str, float] = Field(default_factory=dict)
    
    # Status and timing
    status: str = Field(default="active")  # draft, active, passed, rejected, executed
    voting_deadline: datetime
    execution_deadline: Optional[datetime] = None
    
    # Results
    total_voting_power: float = Field(default=0.0)
    participation_rate: float = Field(default=0.0)
    approval_threshold: float = Field(default=0.51)  # 51% default
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None

class AuditTrailEntry(BaseModel):
    """Immutable audit trail for ULN operations"""
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    actor_id: str
    actor_type: str  # "label", "user", "system", "dao"
    
    # Action details
    resource_type: str  # "content", "royalty", "contract", "label"
    resource_id: str
    action_description: str
    changes_made: Dict[str, Any] = Field(default_factory=dict)
    
    # Context and metadata
    jurisdiction: Optional[TerritoryJurisdiction] = None
    related_labels: List[str] = Field(default_factory=list)
    compliance_impact: List[str] = Field(default_factory=list)
    
    # Immutability and verification
    previous_hash: Optional[str] = None
    current_hash: str
    blockchain_hash: Optional[str] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ===== REQUEST/RESPONSE MODELS =====

class LabelRegistrationRequest(BaseModel):
    """Request to register a new label in ULN"""
    label_type: LabelType
    integration_type: IntegrationType
    metadata_profile: LabelMetadataProfile
    initial_entities: List[AssociatedEntity] = Field(default_factory=list)
    smart_contract_requirements: Optional[Dict[str, Any]] = None
    onboarding_preferences: Dict[str, Any] = Field(default_factory=dict)

class CrossLabelContentRequest(BaseModel):
    """Request to share content across labels"""
    content_id: str
    requesting_label_id: str
    target_labels: List[str]
    access_level: str
    proposed_rights_splits: Dict[str, float]
    usage_restrictions: List[str] = Field(default_factory=list)
    expiry_date: Optional[datetime] = None

class RoyaltyDistributionRequest(BaseModel):
    """Request to process royalty distribution"""
    pool_period: str
    participating_labels: List[str]
    distribution_method: str = Field(default="proportional")
    override_splits: Optional[Dict[str, float]] = None
    dao_approval_required: bool = Field(default=True)

# ===== DASHBOARD AND UI MODELS =====

class ULNDashboardStats(BaseModel):
    """Statistics for ULN dashboard"""
    total_labels: int = 0
    active_labels: int = 0
    major_labels: int = 0
    independent_labels: int = 0
    total_content_shared: int = 0
    total_royalty_pools: int = 0
    total_dao_proposals: int = 0
    smart_contracts: int = 0
    cross_collaborations: int = 0
    
    # Financial metrics
    total_revenue_processed: float = 0.0
    pending_distributions: float = 0.0
    
    # Geographic distribution
    labels_by_territory: Dict[str, int] = Field(default_factory=dict)
    revenue_by_territory: Dict[str, float] = Field(default_factory=dict)
    
    # Recent activity
    recent_registrations: int = 0
    recent_content_shares: int = 0
    recent_proposals: int = 0
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class LabelHubEntry(BaseModel):
    """Entry for Label Hub UI display"""
    global_id: str
    name: str
    label_type: LabelType
    integration_type: IntegrationType
    territory: str
    genre_focus: List[str] = Field(default_factory=list)
    dao_affiliated: bool = Field(default=False)
    status: str
    last_activity: datetime
    
    # Quick stats
    content_count: int = 0
    shared_content_count: int = 0
    monthly_revenue: float = 0.0
    
    # Visual indicators
    verification_status: str = "pending"
    compliance_status: str = "unknown"
    blockchain_enabled: bool = False

class CreatorPortalEntry(BaseModel):
    """Entry for Creator Portal showing label relationships"""
    creator_id: str
    creator_name: str
    managing_labels: List[str] = Field(default_factory=list)
    distributing_labels: List[str] = Field(default_factory=list)
    content_ids: List[str] = Field(default_factory=list)
    
    # Revenue tracking
    total_earnings: float = 0.0
    earnings_by_label: Dict[str, float] = Field(default_factory=dict)
    pending_payments: float = 0.0
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class InvestorViewEntry(BaseModel):
    """Entry for Investor View showing portfolio performance"""
    investor_id: str
    investor_name: str
    portfolio_labels: List[str] = Field(default_factory=list)
    
    # Performance metrics
    total_investment: float = 0.0
    total_returns: float = 0.0
    roi: float = 0.0
    
    # Performance by label
    performance_by_label: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Risk and diversification
    risk_score: float = 0.0
    diversification_score: float = 0.0
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)