"""
Metadata Parser & Validator Models
Handles database models for metadata validation, parsing results, and duplicate detection
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class MetadataFormat(str, Enum):
    """Supported metadata formats"""
    DDEX_ERN = "ddex_ern"
    MEAD = "mead"
    JSON = "json"
    CSV = "csv"
    ID3 = "id3"
    MUSICBRAINZ = "musicbrainz"
    ITUNES = "itunes"
    ISNI = "isni"

class ValidationStatus(str, Enum):
    """Validation status types"""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"

class ValidationSeverity(str, Enum):
    """Validation error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetadataValidationError(BaseModel):
    """Individual validation error"""
    field: str
    message: str
    severity: ValidationSeverity
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    error_code: Optional[str] = None
    suggested_fix: Optional[str] = None

class ParsedMetadataField(BaseModel):
    """Individual parsed metadata field"""
    field_name: str
    field_value: Any
    field_type: str
    is_required: bool = False
    validation_status: ValidationStatus = ValidationStatus.PENDING

class ParsedMetadata(BaseModel):
    """Complete parsed metadata object"""
    # Core identification fields
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    isrc: Optional[str] = None
    upc: Optional[str] = None
    ean: Optional[str] = None
    
    # Rights and ownership
    rights_holders: Optional[List[str]] = None
    publisher_name: Optional[str] = None
    composer_name: Optional[str] = None
    copyright_owner: Optional[str] = None
    copyright_year: Optional[int] = None
    
    # Release information
    release_date: Optional[datetime] = None
    original_release_date: Optional[datetime] = None
    genre: Optional[str] = None
    sub_genre: Optional[str] = None
    language: Optional[str] = None
    
    # Technical information
    duration: Optional[str] = None
    track_number: Optional[int] = None
    total_tracks: Optional[int] = None
    disc_number: Optional[int] = None
    total_discs: Optional[int] = None
    
    # DDEX specific fields
    ddex_version: Optional[str] = None
    ddex_message_id: Optional[str] = None
    ddex_message_type: Optional[str] = None
    party_id: Optional[str] = None
    
    # Additional metadata
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    # Validation fields
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_errors: List[MetadataValidationError] = []
    
class DuplicateRecord(BaseModel):
    """Duplicate detection record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identifier_type: str  # 'isrc', 'upc', 'ean'
    identifier_value: str
    first_seen_date: datetime
    last_seen_date: datetime
    user_id: str
    file_name: str
    metadata_id: str
    is_active: bool = True

class MetadataValidationResult(BaseModel):
    """Complete metadata validation result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    file_name: str
    file_size: int
    file_format: MetadataFormat
    upload_date: datetime = Field(default_factory=datetime.now)
    
    # Parsing results
    parsing_status: ValidationStatus = ValidationStatus.PENDING
    parsing_errors: List[MetadataValidationError] = []
    parsed_metadata: Optional[ParsedMetadata] = None
    
    # Validation results
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_errors: List[MetadataValidationError] = []
    validation_warnings: List[MetadataValidationError] = []
    
    # Duplicate detection
    duplicates_found: List[DuplicateRecord] = []
    duplicate_count: int = 0
    
    # Schema validation
    schema_valid: bool = False
    schema_errors: List[MetadataValidationError] = []
    
    # Statistics
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    warning_records: int = 0
    
    # Processing metadata
    processing_time: Optional[float] = None
    aws_s3_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None

class MetadataParsingRequest(BaseModel):
    """Request model for metadata parsing"""
    user_id: str
    file_name: str
    file_content: bytes
    file_format: MetadataFormat
    validation_options: Optional[Dict[str, Any]] = None
    
class MetadataValidationConfig(BaseModel):
    """Configuration for metadata validation"""
    validate_schema: bool = True
    check_duplicates: bool = True
    duplicate_scope: str = "platform"  # 'user' or 'platform'
    required_fields: List[str] = [
        "title", "artist", "isrc", "release_date", "rights_holders"
    ]
    validate_isrc_format: bool = True
    validate_upc_format: bool = True
    validate_dates: bool = True
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
class DDEXVersionInfo(BaseModel):
    """DDEX version information"""
    version: str
    namespace: str
    schema_url: str
    supported_message_types: List[str]

# DDEX version configurations
DDEX_VERSIONS = {
    "ern-4.4": DDEXVersionInfo(
        version="ern-4.4",
        namespace="http://ddex.net/xml/ern/44",
        schema_url="https://ddex.net/xml/ern/44/ern-main.xsd",
        supported_message_types=["NewReleaseMessage", "CatalogTransfer"]
    ),
    "ern-4.3": DDEXVersionInfo(
        version="ern-4.3", 
        namespace="http://ddex.net/xml/ern/43",
        schema_url="https://ddex.net/xml/ern/43/ern-main.xsd",
        supported_message_types=["NewReleaseMessage", "CatalogTransfer"]
    ),
    "ern-4.2": DDEXVersionInfo(
        version="ern-4.2",
        namespace="http://ddex.net/xml/ern/42", 
        schema_url="https://ddex.net/xml/ern/42/ern-main.xsd",
        supported_message_types=["NewReleaseMessage", "CatalogTransfer"]
    ),
    "ern-3.8.1": DDEXVersionInfo(
        version="ern-3.8.1",
        namespace="http://ddex.net/xml/ern/381",
        schema_url="https://ddex.net/xml/ern/381/ern-main.xsd", 
        supported_message_types=["NewReleaseMessage"]
    )
}

class MEADStandardFields(BaseModel):
    """MEAD (Music and Entertainment Asset Database) standard fields"""
    asset_id: Optional[str] = None
    asset_type: Optional[str] = None
    title: Optional[str] = None
    version_title: Optional[str] = None
    artist_name: Optional[str] = None
    album_title: Optional[str] = None
    label_name: Optional[str] = None
    distributor_name: Optional[str] = None
    isrc: Optional[str] = None
    upc: Optional[str] = None
    grid: Optional[str] = None  # Global Release Identifier
    release_date: Optional[str] = None
    territory: Optional[str] = None
    rights_type: Optional[str] = None
    rights_holder: Optional[str] = None
    usage_type: Optional[str] = None
    track_duration: Optional[str] = None
    genre: Optional[str] = None
    explicit_content: Optional[bool] = None