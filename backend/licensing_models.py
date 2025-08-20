from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
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