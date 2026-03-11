"""
GS1 Asset Registry Models and Database Schemas
Comprehensive data models for GS1 identifier management across all asset types
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from enum import Enum
import uuid
import re


class AssetType(str, Enum):
    """Asset type enumeration for GS1 registry"""
    MUSIC = "music"
    VIDEO = "video" 
    IMAGE = "image"
    MERCHANDISE = "merchandise"


class IdentifierType(str, Enum):
    """GS1 identifier type enumeration"""
    GTIN = "gtin"
    GLN = "gln"
    GDTI = "gdti"
    ISRC = "isrc"
    ISAN = "isan"


class GS1IdentifierStatus(str, Enum):
    """Status of GS1 identifier"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"


class BaseGS1Identifier(BaseModel):
    """Base class for all GS1 identifiers"""
    identifier_type: IdentifierType
    value: str
    status: GS1IdentifierStatus = GS1IdentifierStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GTINIdentifier(BaseGS1Identifier):
    """Global Trade Item Number identifier"""
    identifier_type: IdentifierType = IdentifierType.GTIN
    company_prefix: str
    item_reference: str
    check_digit: str
    gtin_format: str = Field(description="GTIN-8, GTIN-12, GTIN-13, or GTIN-14")
    
    @validator('value')
    def validate_gtin_format(cls, v):
        """Validate GTIN format and check digit"""
        if not re.match(r'^\d{8}$|^\d{12}$|^\d{13}$|^\d{14}$', v):
            raise ValueError('GTIN must be 8, 12, 13, or 14 digits')
        return v


class GLNIdentifier(BaseGS1Identifier):
    """Global Location Number identifier"""
    identifier_type: IdentifierType = IdentifierType.GLN
    company_prefix: str
    location_reference: str
    check_digit: str
    location_type: str = Field(description="Physical, Digital, or Logical location")
    
    @validator('value')
    def validate_gln_format(cls, v):
        """Validate GLN format"""
        if not re.match(r'^\d{13}$', v):
            raise ValueError('GLN must be exactly 13 digits')
        return v


class GDTIIdentifier(BaseGS1Identifier):
    """Global Document Type Identifier"""
    identifier_type: IdentifierType = IdentifierType.GDTI
    company_prefix: str
    document_type: str
    serial_component: str
    check_digit: str
    
    @validator('value')
    def validate_gdti_format(cls, v):
        """Validate GDTI format"""
        if not re.match(r'^\d{13}', v):
            raise ValueError('GDTI must start with 13 digits')
        return v


class ISRCIdentifier(BaseGS1Identifier):
    """International Standard Recording Code"""
    identifier_type: IdentifierType = IdentifierType.ISRC
    country_code: str
    registrant_code: str
    year_of_reference: str
    designation_code: str
    
    @validator('value')
    def validate_isrc_format(cls, v):
        """Validate ISRC format"""
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{3}\d{2}\d{5}$', v):
            raise ValueError('ISRC must follow format: CC-XXX-YY-NNNNN')
        return v


class ISANIdentifier(BaseGS1Identifier):
    """International Standard Audiovisual Number"""
    identifier_type: IdentifierType = IdentifierType.ISAN
    root: str
    episode: Optional[str] = None
    check_digit: str
    
    @validator('value')
    def validate_isan_format(cls, v):
        """Validate ISAN format"""
        if not re.match(r'^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]$', v):
            raise ValueError('ISAN must follow format: XXXX-XXXX-XXXX-XXXX-X')
        return v


class DigitalLinkConfig(BaseModel):
    """GS1 Digital Link configuration"""
    base_uri: str = "https://id.gs1.org"
    domain: Optional[str] = None
    path_info: Optional[str] = None
    query_params: Dict[str, str] = Field(default_factory=dict)
    qr_code_format: str = "PNG"
    qr_code_size: int = 200
    error_correction_level: str = "M"


class GS1DigitalLink(BaseModel):
    """GS1 Digital Link representation"""
    link_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    identifier: Union[GTINIdentifier, GLNIdentifier, GDTIIdentifier, ISRCIdentifier, ISANIdentifier]
    uri: str
    qr_code_data: Optional[str] = None
    config: DigitalLinkConfig = Field(default_factory=DigitalLinkConfig)
    analytics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssetMetadata(BaseModel):
    """Asset metadata for different types"""
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Music-specific metadata
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    duration_seconds: Optional[int] = None
    release_date: Optional[datetime] = None
    
    # Video-specific metadata
    director: Optional[str] = None
    producer: Optional[str] = None
    runtime_minutes: Optional[int] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = None
    
    # Image-specific metadata
    photographer: Optional[str] = None
    width_pixels: Optional[int] = None
    height_pixels: Optional[int] = None
    color_profile: Optional[str] = None
    dpi: Optional[int] = None
    
    # Merchandise-specific metadata
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None


class GS1Asset(BaseModel):
    """Main GS1 Asset model"""
    asset_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: AssetType
    metadata: AssetMetadata
    
    # GS1 Identifiers
    identifiers: Dict[str, Union[GTINIdentifier, GLNIdentifier, GDTIIdentifier, ISRCIdentifier, ISANIdentifier]] = Field(default_factory=dict)
    
    # Digital Links
    digital_links: List[GS1DigitalLink] = Field(default_factory=list)
    
    # Status and audit
    status: GS1IdentifierStatus = GS1IdentifierStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Integration with existing systems
    external_references: Dict[str, str] = Field(default_factory=dict)
    sync_status: Dict[str, Any] = Field(default_factory=dict)


# Request/Response Models

class CreateAssetRequest(BaseModel):
    """Request model for creating new assets"""
    asset_type: AssetType
    metadata: AssetMetadata
    generate_identifiers: List[IdentifierType] = Field(default_factory=list)
    digital_link_config: Optional[DigitalLinkConfig] = None


class UpdateAssetRequest(BaseModel):
    """Request model for updating assets"""
    metadata: Optional[AssetMetadata] = None
    status: Optional[GS1IdentifierStatus] = None
    external_references: Optional[Dict[str, str]] = None


class GenerateIdentifierRequest(BaseModel):
    """Request model for generating identifiers"""
    asset_id: str
    identifier_type: IdentifierType
    metadata: Optional[Dict[str, Any]] = None


class CreateDigitalLinkRequest(BaseModel):
    """Request model for creating Digital Links"""
    asset_id: str
    identifier: str
    config: Optional[DigitalLinkConfig] = None


class AssetSearchFilter(BaseModel):
    """Filter model for asset search"""
    asset_type: Optional[AssetType] = None
    status: Optional[GS1IdentifierStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    metadata_query: Optional[Dict[str, Any]] = None
    identifier_type: Optional[IdentifierType] = None
    text_search: Optional[str] = None


class AssetListResponse(BaseModel):
    """Response model for asset listing"""
    assets: List[GS1Asset]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class IdentifierValidationResult(BaseModel):
    """Result of identifier validation"""
    is_valid: bool
    identifier_type: IdentifierType
    formatted_value: str
    errors: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsData(BaseModel):
    """Analytics data for GS1 assets"""
    total_assets: int
    assets_by_type: Dict[AssetType, int]
    identifiers_by_type: Dict[IdentifierType, int]
    digital_link_scans: int
    top_performing_assets: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BatchOperationRequest(BaseModel):
    """Request model for batch operations"""
    operation: str  # create, update, delete, generate_identifiers
    assets: List[Dict[str, Any]]
    options: Dict[str, Any] = Field(default_factory=dict)


class BatchOperationResult(BaseModel):
    """Result of batch operations"""
    total_processed: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_seconds: float