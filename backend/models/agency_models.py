"""
Agency Onboarding Module - Entity Models
Multi-chain blockchain integration for image licensing
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class LicenseType(str, Enum):
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    RIGHTS_MANAGED = "rights_managed"
    ROYALTY_FREE = "royalty_free"

class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    POLYGON = "polygon"

class ContractStandard(str, Enum):
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    SPL_TOKEN = "spl_token"

class DisputeStatus(str, Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

# Core Entity Models

class Agency(BaseModel):
    """Agency entity model for talent management and licensing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=2, max_length=200)
    business_registration_number: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    wallet_addresses: Dict[BlockchainNetwork, str] = Field(default_factory=dict)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_documents: List[str] = Field(default_factory=list)  # S3 URLs
    kyc_completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Business Information
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    operating_countries: List[str] = Field(default_factory=list)
    
    # Platform Settings
    commission_rate: float = Field(default=0.15, ge=0.0, le=1.0)  # 15% default
    auto_approve_licenses: bool = False
    min_license_price: float = Field(default=50.0, ge=0.0)
    
    # Metrics
    total_talent: int = 0
    total_assets: int = 0
    total_licenses_sold: int = 0
    total_revenue: float = 0.0

    @validator('contact_info')
    def validate_contact_info(cls, v):
        required_fields = ['email', 'phone', 'address']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Contact info must include {field}')
        return v

    @validator('wallet_addresses')
    def validate_wallet_addresses(cls, v):
        # Basic wallet address validation
        for network, address in v.items():
            if network == BlockchainNetwork.ETHEREUM and not address.startswith('0x'):
                raise ValueError(f'Invalid Ethereum wallet address: {address}')
            elif network == BlockchainNetwork.SOLANA and len(address) not in [32, 44]:
                raise ValueError(f'Invalid Solana wallet address: {address}')
        return v

class Talent(BaseModel):
    """Talent entity linked to agencies"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    name: str = Field(..., min_length=2, max_length=100)
    stage_name: Optional[str] = None
    bio: str = Field(default="", max_length=2000)
    
    # Profile Information
    profile_images: List[str] = Field(default_factory=list)  # S3 URLs
    portfolio_images: List[str] = Field(default_factory=list)  # S3 URLs
    portfolio_videos: List[str] = Field(default_factory=list)  # S3 URLs
    
    # Legal Documents
    release_forms: List[str] = Field(default_factory=list)  # S3 URLs
    model_releases: List[str] = Field(default_factory=list)  # S3 URLs
    property_releases: List[str] = Field(default_factory=list)  # S3 URLs
    
    # Demographics & Categories
    age_range: Optional[str] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    categories: List[str] = Field(default_factory=list)  # fashion, commercial, etc.
    skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    
    # Measurements & Physical Attributes
    measurements: Dict[str, Any] = Field(default_factory=dict)
    physical_attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Availability & Rates
    availability: Dict[str, Any] = Field(default_factory=dict)
    base_rates: Dict[str, float] = Field(default_factory=dict)
    
    # Status & Metadata
    active: bool = True
    verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Licensing Stats
    total_licensed_images: int = 0
    total_licensing_revenue: float = 0.0

class LicenseContract(BaseModel):
    """Smart contract metadata for licensing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    talent_id: Optional[str] = None
    asset_id: str  # Reference to the licensed asset
    
    # Blockchain Information
    blockchain_network: BlockchainNetwork
    contract_standard: ContractStandard
    contract_address: Optional[str] = None
    token_id: Optional[str] = None
    transaction_hash: Optional[str] = None
    
    # License Terms
    license_type: LicenseType
    usage_terms: Dict[str, Any] = Field(default_factory=dict)
    exclusivity: bool = False
    duration_months: Optional[int] = None  # None = perpetual
    territory: List[str] = Field(default_factory=lambda: ["worldwide"])
    
    # Pricing & Royalties
    base_price: float = Field(..., gt=0)
    currency: str = "USD"
    royalty_splits: Dict[str, float] = Field(default_factory=dict)  # {recipient: percentage}
    
    # Usage Restrictions
    allowed_usage: List[str] = Field(default_factory=list)
    prohibited_usage: List[str] = Field(default_factory=list)
    max_print_run: Optional[int] = None
    max_digital_impressions: Optional[int] = None
    
    # Status & Metadata
    status: str = "draft"  # draft, deployed, active, expired
    metadata_uri: Optional[str] = None  # IPFS or S3 URL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deployed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Commercial Information
    licensee_info: Dict[str, Any] = Field(default_factory=dict)
    purchase_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('royalty_splits')
    def validate_royalty_splits(cls, v):
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f'Royalty splits must sum to 1.0, got {total}')
        return v

    @validator('usage_terms')
    def validate_usage_terms(cls, v):
        required_fields = ['commercial_use', 'editorial_use', 'web_use', 'print_use']
        for field in required_fields:
            if field not in v:
                v[field] = False
        return v

class LicenseAsset(BaseModel):
    """Licensed asset (image/video) with metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    talent_id: Optional[str] = None
    
    # Asset Information
    filename: str
    original_filename: str
    file_type: str  # image, video
    mime_type: str
    file_size: int
    
    # Storage URLs
    s3_url: str
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None  # Watermarked preview
    
    # Technical Metadata
    dimensions: Dict[str, int] = Field(default_factory=dict)  # width, height
    duration: Optional[float] = None  # For videos
    color_profile: Optional[str] = None
    dpi: Optional[int] = None
    
    # Descriptive Metadata
    title: str
    description: str = ""
    keywords: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    shoot_date: Optional[datetime] = None
    
    # Rights & Releases
    model_released: bool = False
    property_released: bool = False
    rights_info: Dict[str, Any] = Field(default_factory=dict)
    
    # Licensing Information
    available_for_licensing: bool = True
    license_contracts: List[str] = Field(default_factory=list)  # Contract IDs
    base_license_price: float = Field(default=100.0, gt=0)
    
    # Status & Metrics
    status: str = "active"  # active, archived, suspended
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Analytics
    view_count: int = 0
    download_count: int = 0
    license_count: int = 0
    total_revenue: float = 0.0

class DisputeCase(BaseModel):
    """Dispute resolution case"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_contract_id: str
    agency_id: str
    licensee_id: Optional[str] = None
    
    # Dispute Information
    dispute_type: str  # copyright, usage_violation, payment, quality
    title: str
    description: str
    status: DisputeStatus = DisputeStatus.OPEN
    
    # Evidence
    evidence_files: List[str] = Field(default_factory=list)  # S3 URLs
    supporting_documents: List[str] = Field(default_factory=list)
    
    # Resolution Process
    assigned_mediator: Optional[str] = None
    mediation_notes: List[Dict[str, Any]] = Field(default_factory=list)
    resolution_details: Optional[Dict[str, Any]] = None
    
    # DAO Voting (if enabled)
    dao_proposal_id: Optional[str] = None
    voting_enabled: bool = False
    voting_deadline: Optional[datetime] = None
    votes: Dict[str, Any] = Field(default_factory=dict)
    
    # Timeline
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    
    # Financial Impact
    disputed_amount: Optional[float] = None
    resolution_amount: Optional[float] = None

class AuditLog(BaseModel):
    """Immutable audit log for licensing actions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str  # agency, talent, license, asset, dispute
    entity_id: str
    action: str  # created, updated, licensed, disputed, etc.
    
    # Actor Information
    actor_id: str
    actor_type: str  # agency, admin, system
    actor_ip: Optional[str] = None
    
    # Action Details
    action_data: Dict[str, Any] = Field(default_factory=dict)
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    # Blockchain Integration
    blockchain_tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    
    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_agent: Optional[str] = None
    additional_context: Dict[str, Any] = Field(default_factory=dict)

class RoyaltyPayment(BaseModel):
    """Royalty payment tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_contract_id: str
    agency_id: str
    talent_id: Optional[str] = None
    
    # Payment Information
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    payment_method: str  # crypto, bank_transfer, paypal
    
    # Blockchain Transaction
    blockchain_network: Optional[BlockchainNetwork] = None
    transaction_hash: Optional[str] = None
    wallet_address: Optional[str] = None
    
    # Status & Timing
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    
    # Tax & Compliance
    tax_withheld: float = 0.0
    tax_jurisdiction: Optional[str] = None
    compliance_data: Dict[str, Any] = Field(default_factory=dict)

# Request/Response Models

class AgencyRegistrationRequest(BaseModel):
    """Agency registration request model"""
    name: str = Field(..., min_length=2, max_length=200)
    business_registration_number: Optional[str] = None
    contact_info: Dict[str, Any]
    wallet_addresses: Dict[BlockchainNetwork, str]
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    operating_countries: List[str] = Field(default_factory=list)

class TalentCreationRequest(BaseModel):
    """Talent creation request model"""
    name: str = Field(..., min_length=2, max_length=100)
    stage_name: Optional[str] = None
    bio: str = Field(default="", max_length=2000)
    age_range: Optional[str] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

class LicenseContractRequest(BaseModel):
    """License contract creation request"""
    asset_id: str
    talent_id: Optional[str] = None
    blockchain_network: BlockchainNetwork
    contract_standard: ContractStandard
    license_type: LicenseType
    base_price: float = Field(..., gt=0)
    royalty_splits: Dict[str, float]
    usage_terms: Dict[str, Any]
    exclusivity: bool = False
    duration_months: Optional[int] = None
    territory: List[str] = Field(default_factory=lambda: ["worldwide"])

class AssetUploadRequest(BaseModel):
    """Asset upload request model"""
    talent_id: Optional[str] = None
    title: str
    description: str = ""
    keywords: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    model_released: bool = False
    property_released: bool = False
    base_license_price: float = Field(default=100.0, gt=0)