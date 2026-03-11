"""
Content Ingestion Service - Function 1: Content Ingestion & Metadata Enrichment
Handles file uploads, metadata processing, and content management with DDEX compliance.
"""

import os
import uuid
import json
import hashlib
import asyncio
import mimetypes
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field, validator
from pymongo import MongoClient

class ContentType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"

class ContributorRole(str, Enum):
    ARTIST = "artist"
    PRODUCER = "producer"
    SONGWRITER = "songwriter"
    COMPOSER = "composer"
    PERFORMER = "performer"
    ENGINEER = "engineer"
    PUBLISHER = "publisher"
    LABEL = "label"
    MANAGER = "manager"
    FEATURED_ARTIST = "featured_artist"

class LicenseType(str, Enum):
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC = "sync"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER = "master"
    PUBLISHING = "publishing"

class GeoRestriction(str, Enum):
    WORLDWIDE = "worldwide"
    US_ONLY = "us_only"
    EU_ONLY = "eu_only"
    NORTH_AMERICA = "north_america"
    EXCLUDED_REGIONS = "excluded_regions"
    CUSTOM = "custom"

class Contributor(BaseModel):
    contributor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: ContributorRole
    percentage: float = Field(ge=0, le=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    tax_id: Optional[str] = None
    payment_info: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}

class LicensingTerms(BaseModel):
    license_type: LicenseType
    start_date: datetime
    end_date: Optional[datetime] = None
    territories: List[str] = []
    geo_restrictions: GeoRestriction = GeoRestriction.WORLDWIDE
    excluded_territories: List[str] = []
    usage_rights: List[str] = []
    sync_rights: bool = False
    remix_rights: bool = False
    sampling_rights: bool = False
    master_use_rights: bool = False
    performance_rights: bool = True
    mechanical_rights: bool = True
    digital_rights: bool = True
    streaming_rights: bool = True
    broadcast_rights: bool = False
    metadata: Dict[str, Any] = {}

class DDEXMetadata(BaseModel):
    # Core DDEX Release Information
    release_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    grid: Optional[str] = None  # Global Release Identifier
    icpn: Optional[str] = None  # International Cataloguing of Audiovisual Works
    isrc: Optional[str] = None  # International Standard Recording Code
    iswc: Optional[str] = None  # International Standard Musical Work Code
    upc: Optional[str] = None   # Universal Product Code
    ean: Optional[str] = None   # European Article Number
    
    # Release Details
    title: str
    subtitle: Optional[str] = None
    display_title: Optional[str] = None
    original_title: Optional[str] = None
    release_type: str = "Single"  # Album, EP, Single, Compilation
    genre: List[str] = []
    subgenre: List[str] = []
    language: str = "en"
    original_language: Optional[str] = None
    
    # Artist Information
    main_artist: str
    featured_artists: List[str] = []
    all_artists: List[str] = []
    
    # Contributors and Rights
    contributors: List[Contributor] = []
    
    # Release Information
    release_date: datetime
    original_release_date: Optional[datetime] = None
    p_line: Optional[str] = None  # Phonogram copyright
    c_line: Optional[str] = None  # Copyright line
    
    # Label Information
    label_name: Optional[str] = None
    label_code: Optional[str] = None
    distributor: Optional[str] = None
    
    # Commercial Information
    price_category: Optional[str] = None
    commercial_model: str = "SubscriptionModel"
    
    # Technical Information
    duration: Optional[int] = None  # Duration in seconds
    explicit_content: bool = False
    parental_warning: bool = False
    
    # Licensing and Rights
    licensing_terms: Optional[LicensingTerms] = None
    publishing_rights_owner: Optional[str] = None
    master_rights_owner: Optional[str] = None
    
    # Additional Metadata
    keywords: List[str] = []
    description: Optional[str] = None
    producer_notes: Optional[str] = None
    liner_notes: Optional[str] = None
    
    # DDEX Specific
    message_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_sender: str = "BigMannEntertainment"
    message_recipient: List[str] = []
    
    # Validation
    @validator('isrc')
    def validate_isrc(cls, v):
        if v and len(v) != 12:
            raise ValueError('ISRC must be 12 characters long')
        return v
    
    @validator('iswc')
    def validate_iswc(cls, v):
        if v and not v.startswith('T-'):
            raise ValueError('ISWC must start with T-')
        return v

class ContentFile(BaseModel):
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_filename: str
    content_type: ContentType
    mime_type: str
    file_size: int
    file_hash: str
    s3_key: str
    s3_bucket: str
    s3_url: str
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_status: str = "uploaded"  # uploaded, processing, processed, failed
    technical_metadata: Dict[str, Any] = {}  # Duration, bitrate, resolution, etc.

class ContentIngestionRecord(BaseModel):
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content_files: List[ContentFile] = []
    ddex_metadata: DDEXMetadata
    compliance_status: str = "pending"  # pending, approved, rejected, needs_review
    compliance_issues: List[str] = []
    processing_status: str = "ingesting"  # ingesting, processed, failed, ready_for_distribution
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    distribution_ready: bool = False
    metadata: Dict[str, Any] = {}

class ContentIngestionService:
    def __init__(self):
        self.s3_client = self._initialize_s3_client()
        self.bucket_name = os.environ.get('AWS_S3_BUCKET', 'bigmann-content-storage')
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        self.content_collection = self.db['content_ingestion']
        
    def _initialize_s3_client(self):
        """Initialize AWS S3 client"""
        try:
            return boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )
        except Exception as e:
            print(f"Warning: S3 client initialization failed: {e}")
            return None
    
    async def upload_content_file(self, 
                                  file_data: bytes, 
                                  filename: str, 
                                  content_type: str,
                                  user_id: str) -> ContentFile:
        """Upload content file to S3 and create ContentFile record"""
        
        # Generate file ID and S3 key
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1].lower()
        s3_key = f"content/{user_id}/{datetime.now().strftime('%Y/%m/%d')}/{file_id}{file_extension}"
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Determine content type
        mime_type = mimetypes.guess_type(filename)[0] or content_type
        if mime_type.startswith('audio/'):
            content_type_enum = ContentType.AUDIO
        elif mime_type.startswith('video/'):
            content_type_enum = ContentType.VIDEO
        elif mime_type.startswith('image/'):
            content_type_enum = ContentType.IMAGE
        else:
            content_type_enum = ContentType.DOCUMENT
        
        # Upload to S3
        if self.s3_client:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_data,
                    ContentType=mime_type,
                    Metadata={
                        'user_id': user_id,
                        'file_id': file_id,
                        'original_filename': filename,
                        'upload_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                )
                
                s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
                
            except ClientError as e:
                raise Exception(f"S3 upload failed: {str(e)}")
        else:
            # Fallback for local development
            s3_url = f"file://{s3_key}"
        
        # Extract technical metadata (basic for now)
        technical_metadata = {
            'file_size': len(file_data),
            'mime_type': mime_type,
            'file_extension': file_extension,
            'upload_method': 's3' if self.s3_client else 'local'
        }
        
        # Create ContentFile record
        content_file = ContentFile(
            file_id=file_id,
            original_filename=filename,
            content_type=content_type_enum,
            mime_type=mime_type,
            file_size=len(file_data),
            file_hash=file_hash,
            s3_key=s3_key,
            s3_bucket=self.bucket_name,
            s3_url=s3_url,
            technical_metadata=technical_metadata
        )
        
        return content_file
    
    async def create_content_ingestion_record(self,
                                            user_id: str,
                                            content_files: List[ContentFile],
                                            ddex_metadata: DDEXMetadata) -> ContentIngestionRecord:
        """Create a new content ingestion record"""
        
        # Create ingestion record
        ingestion_record = ContentIngestionRecord(
            user_id=user_id,
            content_files=content_files,
            ddex_metadata=ddex_metadata
        )
        
        # Store in MongoDB
        record_dict = ingestion_record.dict()
        # Convert datetime objects to ISO strings for MongoDB
        for key, value in record_dict.items():
            if isinstance(value, datetime):
                record_dict[key] = value.isoformat()
        
        # Handle nested datetime objects
        if record_dict.get('ddex_metadata'):
            ddex_data = record_dict['ddex_metadata']
            for key, value in ddex_data.items():
                if isinstance(value, datetime):
                    ddex_data[key] = value.isoformat()
            
            # Handle licensing terms datetime objects
            if ddex_data.get('licensing_terms'):
                licensing = ddex_data['licensing_terms']
                for key, value in licensing.items():
                    if isinstance(value, datetime):
                        licensing[key] = value.isoformat()
        
        # Handle content files datetime objects
        if record_dict.get('content_files'):
            for file_data in record_dict['content_files']:
                for key, value in file_data.items():
                    if isinstance(value, datetime):
                        file_data[key] = value.isoformat()
        
        # Insert into MongoDB
        result = self.content_collection.insert_one(record_dict)
        ingestion_record.content_id = str(result.inserted_id)
        
        return ingestion_record
    
    async def get_content_ingestion_record(self, content_id: str, user_id: str) -> Optional[ContentIngestionRecord]:
        """Retrieve a content ingestion record"""
        try:
            record = self.content_collection.find_one({
                "content_id": content_id,
                "user_id": user_id
            })
            
            if record:
                # Convert back from MongoDB format
                record['_id'] = str(record['_id'])
                return ContentIngestionRecord(**record)
            
            return None
            
        except Exception as e:
            print(f"Error retrieving content ingestion record: {e}")
            return None
    
    async def list_user_content(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ContentIngestionRecord]:
        """List content ingestion records for a user"""
        try:
            cursor = self.content_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(offset).limit(limit)
            
            records = []
            for record in cursor:
                record['_id'] = str(record['_id'])
                try:
                    records.append(ContentIngestionRecord(**record))
                except Exception as e:
                    print(f"Error parsing record: {e}")
                    continue
            
            return records
            
        except Exception as e:
            print(f"Error listing user content: {e}")
            return []
    
    async def update_content_status(self, 
                                  content_id: str, 
                                  user_id: str,
                                  processing_status: Optional[str] = None,
                                  compliance_status: Optional[str] = None,
                                  compliance_issues: Optional[List[str]] = None) -> bool:
        """Update content processing and compliance status"""
        try:
            update_data = {
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if processing_status:
                update_data["processing_status"] = processing_status
                if processing_status == "processed":
                    update_data["processed_at"] = datetime.now(timezone.utc).isoformat()
                    update_data["distribution_ready"] = True
            
            if compliance_status:
                update_data["compliance_status"] = compliance_status
            
            if compliance_issues:
                update_data["compliance_issues"] = compliance_issues
            
            result = self.content_collection.update_one(
                {"content_id": content_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating content status: {e}")
            return False
    
    async def generate_isrc(self, country_code: str = "US", registrant_code: str = "BME") -> str:
        """Generate a new ISRC code"""
        # ISRC format: CC-XXX-YY-NNNNN
        # CC = Country Code (2 chars)
        # XXX = Registrant Code (3 chars)
        # YY = Year (2 chars)
        # NNNNN = Designation Code (5 digits)
        
        year = datetime.now().year % 100  # Last 2 digits of year
        
        # Get next designation number for this year
        current_year_records = self.content_collection.count_documents({
            "ddex_metadata.isrc": {"$regex": f"^{country_code}{registrant_code}{year:02d}"}
        })
        
        designation_code = (current_year_records + 1) % 100000  # Ensure 5 digits max
        
        isrc = f"{country_code}{registrant_code}{year:02d}{designation_code:05d}"
        return isrc
    
    async def generate_iswc(self) -> str:
        """Generate a new ISWC code"""
        # ISWC format: T-NNN.NNN.NNN-C
        # T = Prefix
        # NNN.NNN.NNN = 9 digit work identifier
        # C = Check digit
        
        # Get count of existing ISWCs to generate unique number
        existing_count = self.content_collection.count_documents({
            "ddex_metadata.iswc": {"$exists": True, "$ne": None}
        })
        
        work_id = existing_count + 1
        work_id_str = f"{work_id:09d}"
        
        # Insert dots
        formatted_id = f"{work_id_str[:3]}.{work_id_str[3:6]}.{work_id_str[6:9]}"
        
        # Calculate check digit (simplified algorithm)
        check_digit = sum(int(d) for d in work_id_str) % 10
        
        iswc = f"T-{formatted_id}-{check_digit}"
        return iswc
    
    async def validate_metadata_completeness(self, ddex_metadata: DDEXMetadata) -> Tuple[bool, List[str]]:
        """Validate DDEX metadata completeness"""
        issues = []
        
        # Required fields validation
        if not ddex_metadata.title:
            issues.append("Title is required")
        
        if not ddex_metadata.main_artist:
            issues.append("Main artist is required")
        
        if not ddex_metadata.release_date:
            issues.append("Release date is required")
        
        if not ddex_metadata.contributors:
            issues.append("At least one contributor is required")
        
        # Contributor validation
        total_percentage = sum(c.percentage for c in ddex_metadata.contributors)
        if abs(total_percentage - 100.0) > 0.01:  # Allow for small floating point errors
            issues.append(f"Contributor percentages must total 100%, currently {total_percentage}%")
        
        # ISRC validation
        if ddex_metadata.isrc:
            if len(ddex_metadata.isrc) != 12:
                issues.append("ISRC must be exactly 12 characters")
            elif not ddex_metadata.isrc[:2].isalpha() or not ddex_metadata.isrc[2:5].isalnum():
                issues.append("ISRC format is invalid")
        
        # Genre validation
        if not ddex_metadata.genre:
            issues.append("At least one genre is required")
        
        return len(issues) == 0, issues
    
    async def extract_technical_metadata(self, content_file: ContentFile) -> Dict[str, Any]:
        """Extract technical metadata from content file"""
        # This would integrate with FFmpeg or similar tools
        # For now, returning basic metadata
        
        technical_metadata = {
            "file_size": content_file.file_size,
            "mime_type": content_file.mime_type,
            "file_hash": content_file.file_hash,
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            "extraction_method": "basic"
        }
        
        # Content-type specific metadata extraction would go here
        if content_file.content_type == ContentType.AUDIO:
            technical_metadata.update({
                "estimated_duration": None,  # Would extract with FFmpeg
                "estimated_bitrate": None,
                "estimated_sample_rate": None,
                "estimated_channels": None,
                "codec": "unknown"
            })
        elif content_file.content_type == ContentType.VIDEO:
            technical_metadata.update({
                "estimated_duration": None,
                "estimated_resolution": None,
                "estimated_fps": None,
                "estimated_bitrate": None,
                "video_codec": "unknown",
                "audio_codec": "unknown"
            })
        elif content_file.content_type == ContentType.IMAGE:
            technical_metadata.update({
                "estimated_dimensions": None,
                "estimated_color_space": None,
                "estimated_dpi": None
            })
        
        return technical_metadata
    
    async def prepare_for_distribution(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """Prepare content for distribution to various platforms"""
        
        # Get content record
        content_record = await self.get_content_ingestion_record(content_id, user_id)
        if not content_record:
            return {"success": False, "error": "Content record not found"}
        
        # Validate compliance status
        if content_record.compliance_status != "approved":
            return {
                "success": False, 
                "error": "Content must be compliance approved before distribution",
                "compliance_status": content_record.compliance_status,
                "compliance_issues": content_record.compliance_issues
            }
        
        # Validate metadata completeness
        is_complete, issues = await self.validate_metadata_completeness(content_record.ddex_metadata)
        if not is_complete:
            return {
                "success": False,
                "error": "Metadata validation failed",
                "issues": issues
            }
        
        # Prepare distribution package
        distribution_package = {
            "content_id": content_id,
            "ddex_metadata": content_record.ddex_metadata.dict(),
            "content_files": [cf.dict() for cf in content_record.content_files],
            "distribution_ready": True,
            "prepared_at": datetime.now(timezone.utc).isoformat(),
            "distribution_formats": []
        }
        
        # Generate platform-specific formats (placeholder)
        for content_file in content_record.content_files:
            if content_file.content_type == ContentType.AUDIO:
                distribution_package["distribution_formats"].extend([
                    {"platform": "spotify", "format": "high_quality_mp3", "required": True},
                    {"platform": "apple_music", "format": "aac", "required": True},
                    {"platform": "youtube_music", "format": "mp3_320", "required": True}
                ])
            elif content_file.content_type == ContentType.VIDEO:
                distribution_package["distribution_formats"].extend([
                    {"platform": "youtube", "format": "1080p_h264", "required": True},
                    {"platform": "tiktok", "format": "vertical_1080p", "required": True},
                    {"platform": "instagram", "format": "square_1080p", "required": True}
                ])
        
        # Mark as ready for distribution
        await self.update_content_status(
            content_id, 
            user_id, 
            processing_status="ready_for_distribution"
        )
        
        return {
            "success": True,
            "distribution_package": distribution_package,
            "message": "Content prepared for distribution successfully"
        }
    
    async def get_content_analytics(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """Get analytics for a content piece"""
        
        content_record = await self.get_content_ingestion_record(content_id, user_id)
        if not content_record:
            return {"error": "Content not found"}
        
        # Mock analytics data - in real implementation would integrate with actual analytics
        analytics = {
            "content_id": content_id,
            "title": content_record.ddx_metadata.title,
            "main_artist": content_record.ddex_metadata.main_artist,
            "upload_date": content_record.created_at.isoformat(),
            "processing_status": content_record.processing_status,
            "compliance_status": content_record.compliance_status,
            "file_stats": {
                "total_files": len(content_record.content_files),
                "total_size_mb": sum(cf.file_size for cf in content_record.content_files) / (1024 * 1024),
                "file_types": list(set(cf.content_type.value for cf in content_record.content_files))
            },
            "metadata_completeness": {
                "isrc_assigned": bool(content_record.ddex_metadata.isrc),
                "iswc_assigned": bool(content_record.ddex_metadata.iswc),
                "contributors_count": len(content_record.ddx_metadata.contributors),
                "genres_count": len(content_record.ddex_metadata.genre),
                "licensing_terms_defined": bool(content_record.ddex_metadata.licensing_terms)
            },
            "distribution_readiness": content_record.distribution_ready,
            "platforms_compatible": [],  # Would be calculated based on content format and metadata
            "estimated_revenue_potential": "medium",  # Would be calculated by ML model
            "optimization_suggestions": []
        }
        
        # Generate optimization suggestions
        if not content_record.ddex_metadata.isrc:
            analytics["optimization_suggestions"].append("Consider assigning an ISRC for better tracking")
        
        if len(content_record.ddx_metadata.genre) < 2:
            analytics["optimization_suggestions"].append("Add more genre tags for better discoverability")
        
        if not content_record.ddex_metadata.keywords:
            analytics["optimization_suggestions"].append("Add keywords to improve search optimization")
        
        return analytics