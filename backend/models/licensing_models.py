from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from decimal import Decimal
import uuid

class LicenseStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"

class LicenseType(str, Enum):
    API_LICENSE = "api_license"
    CONTENT_LICENSE = "content_license"
    DISTRIBUTION_LICENSE = "distribution_license"
    REVENUE_SHARE = "revenue_share"
    ENTERPRISE = "enterprise"

class PlatformLicense(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform_id: str
    platform_name: str
    license_type: LicenseType
    license_status: LicenseStatus
    license_key: Optional[str] = None
    api_credentials: Dict[str, str] = Field(default_factory=dict)
    
    # License terms
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renewal: bool = True
    
    # Compliance and limits
    monthly_limit: Optional[int] = None  # Content upload limit
    usage_count: int = 0
    rate_limit: Optional[int] = None  # API calls per hour
    
    # Financial terms
    license_fee: float = 0.0
    revenue_share_percentage: float = 0.0
    setup_fee: float = 0.0
    
    # Platform specific configuration
    platform_config: Dict[str, Any] = Field(default_factory=dict)
    compliance_requirements: List[str] = Field(default_factory=list)
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    
    # Contact and support
    platform_contact: Optional[str] = None
    support_email: Optional[str] = None
    license_manager: Optional[str] = None

class LicensingAgreement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agreement_name: str
    platform_licenses: List[str] = Field(default_factory=list)  # License IDs
    
    # Agreement details
    agreement_type: str  # "master_agreement", "individual", "bundle"
    total_platforms: int = 0
    active_platforms: int = 0
    
    # Terms
    master_start_date: datetime
    master_end_date: Optional[datetime] = None
    total_license_fee: float = 0.0
    
    # Big Mann Entertainment details
    business_entity: str = "Big Mann Entertainment"
    business_owner: str = "John LeGerron Spivey"
    business_ein: str = "270658077"
    business_tin: str = "12800"
    
    # Legal and compliance
    contract_signed: bool = False
    legal_representative: Optional[str] = None
    compliance_score: float = 100.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LicenseUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_id: str
    platform_id: str
    
    # Usage metrics
    content_uploads: int = 0
    api_calls: int = 0
    data_transfer_mb: float = 0.0
    
    # Time tracking
    usage_date: datetime
    reporting_period: str  # "daily", "weekly", "monthly"
    
    # Revenue tracking
    revenue_generated: float = 0.0
    platform_commission: float = 0.0
    net_revenue: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ComplianceCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_id: str
    platform_id: str
    
    # Compliance details
    check_type: str  # "content_guidelines", "api_limits", "revenue_reporting"
    compliance_status: str  # "compliant", "warning", "violation"
    
    # Check results
    check_description: str
    violation_details: Optional[str] = None
    recommended_action: Optional[str] = None
    
    # Resolution
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    check_date: datetime = Field(default_factory=datetime.utcnow)
    resolution_date: Optional[datetime] = None

class PlatformActivation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform_id: str
    license_id: str
    
    # Activation status
    is_active: bool = True
    activation_date: datetime = Field(default_factory=datetime.utcnow)
    deactivation_date: Optional[datetime] = None
    
    # Activation details
    activated_by: str
    activation_reason: str = "License activated"
    deactivation_reason: Optional[str] = None
    
    # Configuration
    platform_settings: Dict[str, Any] = Field(default_factory=dict)
    integration_status: str = "active"  # "active", "testing", "maintenance"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Statutory Rate Models for Music Licensing
class RoyaltyType(str, Enum):
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    DIGITAL_PERFORMANCE = "digital_performance"
    REPRODUCTION = "reproduction"

class StatutoryRate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    royalty_type: RoyaltyType
    rate_name: str
    
    # Rate information
    rate_per_unit: Decimal  # Rate per play/stream/copy
    rate_percentage: Optional[Decimal] = None  # Percentage of revenue
    minimum_fee: Decimal = Decimal('0.00')
    maximum_fee: Optional[Decimal] = None
    
    # Effective period
    effective_date: datetime
    expiration_date: Optional[datetime] = None
    
    # Rate details
    currency: str = "USD"
    unit_type: str = "per_stream"  # "per_stream", "per_download", "per_minute", "per_composition"
    rate_source: str = "CRB"  # Copyright Royalty Board
    
    # Applicability
    applies_to_platforms: List[str] = Field(default_factory=list)  # Platform IDs
    applies_to_content: List[str] = Field(default_factory=list)   # Content types
    
    # Big Mann Entertainment specific
    big_mann_rate_multiplier: Decimal = Decimal('1.0')  # Custom multiplier
    auto_apply: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DailyCompensation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    compensation_date: datetime
    
    # Platform and license information
    platform_id: str
    license_id: str
    platform_name: str
    
    # Usage metrics for the day
    total_streams: int = 0
    total_downloads: int = 0
    total_views: int = 0
    total_plays: int = 0
    
    # Revenue calculations
    gross_revenue: Decimal = Decimal('0.00')
    platform_commission: Decimal = Decimal('0.00')
    net_revenue: Decimal = Decimal('0.00')
    
    # Statutory rate applications
    mechanical_royalties: Decimal = Decimal('0.00')
    performance_royalties: Decimal = Decimal('0.00')
    sync_royalties: Decimal = Decimal('0.00')
    
    # Daily compensation breakdown
    artist_compensation: Decimal = Decimal('0.00')
    songwriter_compensation: Decimal = Decimal('0.00')
    publisher_compensation: Decimal = Decimal('0.00')
    big_mann_commission: Decimal = Decimal('0.00')
    
    # Payment details
    total_compensation: Decimal = Decimal('0.00')
    payment_status: str = "pending"  # "pending", "processed", "paid", "failed"
    payment_date: Optional[datetime] = None
    payment_reference: Optional[str] = None
    
    # Calculation metadata
    statutory_rates_applied: List[str] = Field(default_factory=list)  # Statutory rate IDs used
    calculation_method: str = "automated"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CompensationPayout(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payout_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Payout details
    recipient_type: str  # "artist", "songwriter", "publisher", "platform"
    recipient_id: str
    recipient_name: str
    recipient_email: Optional[str] = None
    
    # Compensation period
    period_start: datetime
    period_end: datetime
    compensation_days: List[str] = Field(default_factory=list)  # Daily compensation IDs included
    
    # Financial details
    total_amount: Decimal = Decimal('0.00')
    tax_withholding: Decimal = Decimal('0.00')
    net_payout: Decimal = Decimal('0.00')
    
    # Payment method
    payment_method: str = "bank_transfer"  # "bank_transfer", "paypal", "venmo", "check"
    payment_details: Dict[str, str] = Field(default_factory=dict)
    
    # Status tracking
    payout_status: str = "pending"  # "pending", "processing", "completed", "failed", "cancelled"
    transaction_id: Optional[str] = None
    confirmation_number: Optional[str] = None
    
    # Business information
    business_entity: str = "Big Mann Entertainment"
    business_owner: str = "John LeGerron Spivey"
    business_ein: str = "270658077"
    business_tin: str = "12800"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LicenseCompensationSummary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    summary_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Summary period
    period_start: datetime
    period_end: datetime
    period_type: str = "monthly"  # "daily", "weekly", "monthly", "quarterly", "annual"
    
    # Platform summary
    total_platforms_active: int = 0
    total_content_distributed: int = 0
    total_streams_generated: int = 0
    
    # Financial summary
    total_gross_revenue: Decimal = Decimal('0.00')
    total_statutory_royalties: Decimal = Decimal('0.00')
    total_compensations_paid: Decimal = Decimal('0.00')
    total_pending_compensations: Decimal = Decimal('0.00')
    
    # Statutory rate compliance
    statutory_compliance_rate: Decimal = Decimal('100.00')
    rates_applied_count: int = 0
    compliance_issues: List[str] = Field(default_factory=list)
    
    # Big Mann Entertainment performance
    big_mann_total_commission: Decimal = Decimal('0.00')
    big_mann_roi_percentage: Decimal = Decimal('0.00')
    
    created_at: datetime = Field(default_factory=datetime.utcnow)