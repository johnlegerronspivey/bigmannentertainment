from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class GLNType(str, Enum):
    LEGAL_ENTITY = "Legal Entity"
    FUNCTION = "Function"
    PHYSICAL_LOCATION = "Physical Location"
    DIGITAL_LOCATION = "Digital Location"

class GS1Location(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gln: str = Field(..., description="13-digit Global Location Number")
    
    # Basic information
    location_name: str = Field(..., max_length=255)
    organization_name: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    
    # Address information
    street_address: Optional[str] = Field(None, max_length=255)
    address_locality: Optional[str] = Field(None, max_length=100)  # City
    address_region: Optional[str] = Field(None, max_length=100)    # State/Province
    postal_code: Optional[str] = Field(None, max_length=20)
    country_code: str = Field("US", max_length=2)
    
    # GS1 attributes
    gln_type: GLNType = GLNType.LEGAL_ENTITY
    supply_chain_role: Optional[str] = Field(None, max_length=100)
    industry: str = Field("Entertainment", max_length=100)
    
    # Hierarchy
    parent_gln: Optional[str] = Field(None, pattern=r"^\d{13}$")
    entity_gln: Optional[str] = Field(None, pattern=r"^\d{13}$")
    
    # Status
    gln_status: str = Field("ACTIVE", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('gln')
    def validate_gln_format(cls, v):
        if not v or len(v) != 13 or not v.isdigit():
            raise ValueError('GLN must be exactly 13 digits')
        return v

class GS1Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gtin: str = Field(..., description="Global Trade Item Number")
    upc: str = Field(..., description="12-digit UPC code")
    
    # Music release information
    title: str = Field(..., max_length=200)
    artist_name: str = Field(..., max_length=255)
    label_name: str = Field(..., max_length=255)
    release_date: datetime
    genre: Optional[str] = Field(None, max_length=100)
    duration_seconds: Optional[int] = Field(None, ge=1)
    
    # GS1 standard fields
    brand_name: Optional[str] = Field(None, max_length=70)
    product_description: Optional[str] = Field(None, max_length=200)
    product_description_language: str = Field("ENG", max_length=3)
    brand_name_language: str = Field("ENG", max_length=3)
    
    # Music industry identifiers
    isrc: Optional[str] = Field(None, regex=r"^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$")
    catalog_number: Optional[str] = Field(None, max_length=50)
    distribution_format: str = Field("Digital", max_length=50)
    
    # Status and metadata
    gtin_status: str = Field("ACTIVE", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('gtin')
    def validate_gtin_format(cls, v):
        if not v or len(v) not in [13, 14] or not v.isdigit():
            raise ValueError('GTIN must be 13 or 14 digits')
        return v
    
    @validator('upc')
    def validate_upc_format(cls, v):
        if not v or len(v) != 12 or not v.isdigit():
            raise ValueError('UPC must be exactly 12 digits')
        return v

class BarcodeRequest(BaseModel):
    upc_code: str = Field(..., regex=r"^\d{12,13}$")
    format_type: str = Field("PNG", regex="^(PNG|JPEG|SVG)$")
    width: Optional[float] = Field(None, ge=0.1, le=2.0)
    height: Optional[float] = Field(None, ge=5.0, le=50.0)
    dpi: Optional[int] = Field(300, ge=72, le=600)
    
class BarcodeResponse(BaseModel):
    upc_code: str
    format_type: str
    content_type: str
    data: str  # Base64 encoded
    size_bytes: int
    
class DistributionPlatform(BaseModel):
    platform_name: str = Field(..., max_length=100)
    platform_type: str = Field("DSP", max_length=50)  # DSP, Distributor, Aggregator
    gln: Optional[str] = Field(None, regex=r"^\d{13}$")
    api_endpoint: Optional[str] = None
    is_active: bool = True
    
class GS1ValidationResult(BaseModel):
    is_valid: bool
    identifier: str
    identifier_type: str  # "UPC", "GTIN", "GLN"
    validation_message: str
    check_digit_valid: bool = False
    format_valid: bool = False