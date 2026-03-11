"""
Rights & Compliance Models
Handles territory rights, usage rights, embargo logic, and compliance data structures
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid

class TerritoryCode(str, Enum):
    """ISO territory codes and regions"""
    # Individual Countries
    US = "US"  # United States
    CA = "CA"  # Canada
    GB = "GB"  # United Kingdom
    DE = "DE"  # Germany
    FR = "FR"  # France
    IT = "IT"  # Italy
    ES = "ES"  # Spain
    AU = "AU"  # Australia
    JP = "JP"  # Japan
    KR = "KR"  # South Korea
    CN = "CN"  # China
    IN = "IN"  # India
    BR = "BR"  # Brazil
    MX = "MX"  # Mexico
    
    # Regional Groups
    EU = "EU"  # European Union
    NA = "NA"  # North America
    APAC = "APAC"  # Asia Pacific
    LATAM = "LATAM"  # Latin America
    MENA = "MENA"  # Middle East & North Africa
    
    # Global
    GLOBAL = "GLOBAL"  # Worldwide rights

class UsageRightType(str, Enum):
    """Types of usage rights"""
    STREAMING = "streaming"  # Digital streaming services
    DOWNLOAD = "download"  # Digital downloads
    PHYSICAL = "physical"  # Physical distribution
    RADIO = "radio"  # Radio broadcasting
    TV = "tv"  # Television broadcasting
    SYNC = "sync"  # Synchronization (movies, ads, games)
    PUBLIC_PERFORMANCE = "public_performance"  # Live venues, events
    MECHANICAL = "mechanical"  # Mechanical reproduction
    PRINT = "print"  # Sheet music, lyric books
    MASTER = "master"  # Master recording rights
    PUBLISHING = "publishing"  # Publishing and composition rights
    NEIGHBORING = "neighboring"  # Neighboring rights (performers, producers)

class RightsStatus(str, Enum):
    """Rights status types"""
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EMBARGOED = "embargoed"

class ComplianceStatus(str, Enum):
    """Compliance check status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    UNKNOWN = "unknown"
    EXPIRED = "expired"

class EmbargoType(str, Enum):
    """Types of embargo restrictions"""
    RELEASE_DATE = "release_date"  # Cannot be used before release date
    TERRITORY_SPECIFIC = "territory_specific"  # Territory-based restrictions
    USAGE_SPECIFIC = "usage_specific"  # Usage type restrictions
    TIME_WINDOW = "time_window"  # Specific time period restrictions
    PLATFORM_SPECIFIC = "platform_specific"  # Platform/service restrictions

class TerritoryRights(BaseModel):
    """Territory-specific rights information"""
    territory: TerritoryCode
    rights_holder: str
    rights_percentage: float = Field(ge=0, le=100)  # Percentage of rights owned
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    restrictions: Optional[List[str]] = None
    is_exclusive: bool = False
    contact_info: Optional[Dict[str, str]] = None

class UsageRights(BaseModel):
    """Usage-specific rights information"""
    usage_type: UsageRightType
    territories: List[TerritoryCode]
    rights_holder: str
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    is_exclusive: bool = False
    royalty_rate: Optional[float] = None  # Percentage or flat rate
    minimum_guarantee: Optional[float] = None
    advance_amount: Optional[float] = None
    restrictions: Optional[List[str]] = None

class EmbargoRestriction(BaseModel):
    """Embargo and restriction information"""
    embargo_type: EmbargoType
    affected_territories: List[TerritoryCode]
    affected_usage_types: List[UsageRightType]
    restriction_start: datetime
    restriction_end: Optional[datetime] = None
    reason: str
    override_allowed: bool = False
    override_conditions: Optional[List[str]] = None

class ComplianceRule(BaseModel):
    """Individual compliance rule"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str
    rule_description: str
    territories: List[TerritoryCode]
    usage_types: List[UsageRightType]
    required_fields: List[str]  # Metadata fields required for compliance
    validation_logic: Dict[str, Any]  # Custom validation rules
    severity: str = "error"  # error, warning, info
    is_active: bool = True

class RightsOwnership(BaseModel):
    """Complete rights ownership information"""
    content_id: str
    isrc: Optional[str] = None
    title: str
    
    # Territory Rights
    territory_rights: List[TerritoryRights] = []
    
    # Usage Rights
    usage_rights: List[UsageRights] = []
    
    # Embargo Information
    embargo_restrictions: List[EmbargoRestriction] = []
    
    # Ownership Details
    master_owner: Optional[str] = None
    publishing_owner: Optional[str] = None
    neighboring_rights_owner: Optional[str] = None
    
    # Administrative
    created_date: datetime = Field(default_factory=datetime.now)
    updated_date: datetime = Field(default_factory=datetime.now)
    created_by: str
    
    # Compliance Status
    overall_status: RightsStatus = RightsStatus.PENDING
    last_compliance_check: Optional[datetime] = None

class ComplianceCheckResult(BaseModel):
    """Results of a compliance check"""
    check_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    isrc: Optional[str] = None
    
    # Check Parameters
    requested_territories: List[TerritoryCode]
    requested_usage_types: List[UsageRightType]
    check_date: datetime = Field(default_factory=datetime.now)
    
    # Results
    overall_status: ComplianceStatus
    territory_compliance: Dict[str, ComplianceStatus]  # Territory -> Status
    usage_compliance: Dict[str, ComplianceStatus]  # Usage Type -> Status
    
    # Issues Found
    violations: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    missing_rights: List[Dict[str, Any]] = []
    expired_rights: List[Dict[str, Any]] = []
    embargoed_items: List[Dict[str, Any]] = []
    
    # Recommendations
    recommendations: List[str] = []
    required_actions: List[str] = []
    
    # Processing Info
    processing_time: Optional[float] = None
    checked_by: str

class RightsValidationConfig(BaseModel):
    """Configuration for rights validation"""
    check_territory_rights: bool = True
    check_usage_rights: bool = True
    check_embargo_restrictions: bool = True
    check_expiry_dates: bool = True
    strict_mode: bool = False  # Strict vs permissive compliance
    grace_period_days: int = 30  # Grace period for expired rights
    default_territories: List[TerritoryCode] = [TerritoryCode.US]
    default_usage_types: List[UsageRightType] = [UsageRightType.STREAMING]

class TerritoryMapping(BaseModel):
    """Territory grouping and mapping"""
    territory_code: TerritoryCode
    territory_name: str
    region: str
    iso_code: str
    currency: str
    legal_requirements: List[str] = []
    collecting_societies: Dict[str, str] = {}  # Type -> Society name
    time_zone: str
    embargo_prone: bool = False
    
    # Regional Groupings
    eu_member: bool = False
    nafta_member: bool = False
    bilateral_agreements: List[str] = []

# Pre-defined territory mappings
TERRITORY_MAPPINGS = {
    TerritoryCode.US: TerritoryMapping(
        territory_code=TerritoryCode.US,
        territory_name="United States",
        region="North America",
        iso_code="US",
        currency="USD",
        legal_requirements=["DMCA compliance", "Mechanical licensing"],
        collecting_societies={
            "performance": "ASCAP/BMI/SESAC",
            "mechanical": "Harry Fox Agency",
            "synchronization": "Various publishers"
        },
        time_zone="EST/PST",
        embargo_prone=False,
        nafta_member=True
    ),
    TerritoryCode.EU: TerritoryMapping(
        territory_code=TerritoryCode.EU,
        territory_name="European Union",
        region="Europe",
        iso_code="EU",
        currency="EUR",
        legal_requirements=["GDPR compliance", "DSM Directive", "Collective licensing"],
        collecting_societies={
            "performance": "Various (PRS, SACEM, GEMA, etc.)",
            "mechanical": "Various national societies",
            "synchronization": "Various national societies"
        },
        time_zone="CET",
        embargo_prone=True,
        eu_member=True
    ),
    TerritoryCode.GLOBAL: TerritoryMapping(
        territory_code=TerritoryCode.GLOBAL,
        territory_name="Worldwide",
        region="Global",
        iso_code="WW",
        currency="USD",
        legal_requirements=["Multi-jurisdictional compliance"],
        collecting_societies={},
        time_zone="UTC",
        embargo_prone=True
    )
}

class UsageRightTemplate(BaseModel):
    """Template for common usage rights configurations"""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_name: str
    description: str
    usage_types: List[UsageRightType]
    default_territories: List[TerritoryCode]
    standard_royalty_rates: Dict[str, float] = {}  # Usage type -> rate
    exclusivity_default: bool = False
    typical_term_months: Optional[int] = None
    
    # Common restrictions
    common_restrictions: List[str] = []
    
    # Industry standard terms
    industry_standard: bool = False
    created_by: str = "system"

# Pre-defined usage right templates
STANDARD_USAGE_TEMPLATES = {
    "streaming_basic": UsageRightTemplate(
        template_name="Basic Streaming Rights",
        description="Standard digital streaming rights for DSPs",
        usage_types=[UsageRightType.STREAMING, UsageRightType.DOWNLOAD],
        default_territories=[TerritoryCode.US, TerritoryCode.CA],
        standard_royalty_rates={
            "streaming": 0.006,  # $0.006 per stream
            "download": 0.91  # $0.91 per download
        },
        exclusivity_default=False,
        typical_term_months=24,
        industry_standard=True,
        created_by="system"
    ),
    "sync_standard": UsageRightTemplate(
        template_name="Standard Sync Rights",
        description="Synchronization rights for film, TV, and advertising",
        usage_types=[UsageRightType.SYNC],
        default_territories=[TerritoryCode.GLOBAL],
        standard_royalty_rates={
            "sync": 2500.0  # $2,500 base sync fee
        },
        exclusivity_default=True,
        typical_term_months=12,
        common_restrictions=[
            "One-time use only",
            "Territory restrictions may apply",
            "Usage reporting required"
        ],
        industry_standard=True,
        created_by="system"
    ),
    "broadcast_basic": UsageRightTemplate(
        template_name="Basic Broadcast Rights",
        description="Radio and TV broadcasting rights",
        usage_types=[UsageRightType.RADIO, UsageRightType.TV],
        default_territories=[TerritoryCode.US],
        standard_royalty_rates={
            "radio": 0.24,  # Performance royalty
            "tv": 0.45     # Performance royalty
        },
        exclusivity_default=False,
        typical_term_months=36,
        industry_standard=True,
        created_by="system"
    )
}

class RightsAuditLog(BaseModel):
    """Audit trail for rights changes"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    action: str  # created, updated, deleted, checked, etc.
    actor: str  # User who performed action
    timestamp: datetime = Field(default_factory=datetime.now)
    changes: Dict[str, Any] = {}  # What changed
    reason: Optional[str] = None
    ip_address: Optional[str] = None