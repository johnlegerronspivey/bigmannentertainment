import os
import io
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import json

# IPTC/XMP metadata handling
try:
    from iptcinfo3 import IPTCInfo
    IPTC_AVAILABLE = True
except ImportError:
    IPTC_AVAILABLE = False
    logging.warning("iptcinfo3 not available - IPTC metadata extraction disabled")

try:
    from libxmp import XMPFiles, XMPMeta
    XMP_AVAILABLE = True
except ImportError:
    XMP_AVAILABLE = False
    logging.warning("python-xmp-toolkit not available - XMP metadata extraction disabled")

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class ModelReleaseForm(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str
    model_id: Optional[str] = None
    agency_name: Optional[str] = None
    photographer_name: str
    shoot_date: datetime
    usage_rights: str  # "commercial", "editorial", "limited_commercial", "unrestricted"
    territory_rights: str  # "worldwide", "north_america", "europe", etc.
    duration_rights: str  # "perpetual", "1_year", "5_years", "limited"
    exclusive: bool = False
    signed_date: datetime
    witness_name: Optional[str] = None
    legal_guardian: Optional[str] = None  # For models under 18
    additional_terms: Optional[str] = None
    release_document_url: Optional[str] = None
    status: str = "active"  # active, expired, revoked
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IPTCMetadata(BaseModel):
    headline: Optional[str] = None
    caption: Optional[str] = None
    keywords: List[str] = []
    category: Optional[str] = None
    credit: Optional[str] = None
    source: Optional[str] = None
    copyright_notice: Optional[str] = None
    photographer: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    date_created: Optional[datetime] = None
    urgency: Optional[int] = None
    object_name: Optional[str] = None
    edit_status: Optional[str] = None
    special_instructions: Optional[str] = None

class XMPMetadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    subject: List[str] = []
    rights: Optional[str] = None
    usage_terms: Optional[str] = None
    web_statement: Optional[str] = None
    rating: Optional[int] = None
    label: Optional[str] = None

class DDEXImageDescriptor(BaseModel):
    # DDEX-compliant image descriptors
    resource_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str
    mime_type: str
    file_size: int
    image_width: int
    image_height: int
    color_depth: Optional[int] = None
    resolution: Optional[str] = None  # "72dpi", "300dpi", etc.
    compression_type: Optional[str] = None
    
    # Rights and usage
    usage_type: str  # "Commercial", "Editorial", "Promotional"
    territory: str = "Worldwide"
    exclusive: bool = False
    duration: str = "Perpetual"
    
    # Content descriptors
    genre: Optional[str] = None
    sub_genre: Optional[str] = None
    mood: List[str] = []
    theme: List[str] = []
    
    # Model and shoot information
    model_name: Optional[str] = None
    agency_name: Optional[str] = None
    photographer: Optional[str] = None
    shoot_location: Optional[str] = None
    shoot_date: Optional[datetime] = None
    
    # Technical metadata
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens: Optional[str] = None
    focal_length: Optional[str] = None
    aperture: Optional[str] = None
    iso: Optional[int] = None
    shutter_speed: Optional[str] = None

class ImageMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Basic image properties
    width: int
    height: int
    color_mode: Optional[str] = None
    bit_depth: Optional[int] = None
    dpi: Optional[tuple] = None
    
    # Metadata standards
    exif_data: Dict[str, Any] = {}
    iptc_metadata: Optional[IPTCMetadata] = None
    xmp_metadata: Optional[XMPMetadata] = None
    ddex_descriptor: Optional[DDEXImageDescriptor] = None
    
    # Model release and rights
    model_release: Optional[ModelReleaseForm] = None
    usage_rights: str = "editorial_only"  # editorial_only, commercial, unrestricted
    license_terms: Optional[str] = None
    
    # Business metadata
    agency_id: Optional[str] = None
    photographer_id: Optional[str] = None
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Content tags and categorization
    tags: List[str] = []
    categories: List[str] = []
    content_rating: str = "general"  # general, mature, adult
    
    # Processing status
    status: str = "uploaded"  # uploaded, processing, approved, rejected
    validation_errors: List[str] = []
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ImageMetadataService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        
    async def extract_metadata_from_image(self, image_data: bytes, filename: str) -> ImageMetadata:
        """Extract comprehensive metadata from image file"""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image properties
            width, height = image.size
            file_size = len(image_data)
            mime_type = Image.MIME.get(image.format, 'image/jpeg')
            
            # Initialize metadata object
            metadata = ImageMetadata(
                file_name=filename,
                file_path=f"/uploads/images/{filename}",
                file_size=file_size,
                mime_type=mime_type,
                width=width,
                height=height,
                color_mode=image.mode,
                dpi=image.info.get('dpi')
            )
            
            # Extract EXIF data
            exif_data = self._extract_exif_data(image)
            metadata.exif_data = exif_data
            
            # Extract IPTC metadata if available
            if IPTC_AVAILABLE:
                iptc_data = self._extract_iptc_data(image_data)
                if iptc_data:
                    metadata.iptc_metadata = iptc_data
            
            # Extract XMP metadata if available
            if XMP_AVAILABLE:
                xmp_data = self._extract_xmp_data(image_data)
                if xmp_data:
                    metadata.xmp_metadata = xmp_data
            
            # Generate DDEX-compliant descriptor
            ddex_descriptor = self._generate_ddex_descriptor(metadata, exif_data)
            metadata.ddex_descriptor = ddex_descriptor
            
            # Auto-categorize based on metadata
            metadata.tags = self._generate_auto_tags(metadata)
            metadata.categories = self._categorize_image(metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {filename}: {str(e)}")
            raise
    
    def _extract_exif_data(self, image: Image.Image) -> Dict[str, Any]:
        """Extract EXIF data from image"""
        exif_data = {}
        
        try:
            if hasattr(image, '_getexif') and image._getexif() is not None:
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value) if not isinstance(value, (str, int, float)) else value
                    
        except Exception as e:
            logger.warning(f"Error extracting EXIF data: {str(e)}")
            
        return exif_data
    
    def _extract_iptc_data(self, image_data: bytes) -> Optional[IPTCMetadata]:
        """Extract IPTC metadata from image"""
        if not IPTC_AVAILABLE:
            return None
            
        try:
            info = IPTCInfo(image_data, force=True)
            
            iptc_metadata = IPTCMetadata(
                headline=info.get('headline'),
                caption=info.get('caption/abstract'),
                keywords=info.get('keywords', []),
                category=info.get('category'),
                credit=info.get('credit'),
                source=info.get('source'),
                copyright_notice=info.get('copyright notice'),
                photographer=info.get('by-line'),
                city=info.get('city'),
                state=info.get('province/state'),
                country=info.get('country/primary location name'),
                urgency=info.get('urgency'),
                object_name=info.get('object name'),
                edit_status=info.get('edit status'),
                special_instructions=info.get('special instructions')
            )
            
            # Parse date created
            date_created = info.get('date created')
            if date_created:
                try:
                    iptc_metadata.date_created = datetime.strptime(date_created, '%Y%m%d')
                except ValueError:
                    pass
                    
            return iptc_metadata
            
        except Exception as e:
            logger.warning(f"Error extracting IPTC data: {str(e)}")
            return None
    
    def _extract_xmp_data(self, image_data: bytes) -> Optional[XMPMetadata]:
        """Extract XMP metadata from image"""
        if not XMP_AVAILABLE:
            return None
            
        try:
            # XMP extraction would go here
            # This is a placeholder as XMP extraction requires specialized libraries
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting XMP data: {str(e)}")
            return None
    
    def _generate_ddex_descriptor(self, metadata: ImageMetadata, exif_data: Dict[str, Any]) -> DDEXImageDescriptor:
        """Generate DDEX-compliant image descriptor"""
        
        descriptor = DDEXImageDescriptor(
            file_name=metadata.file_name,
            mime_type=metadata.mime_type,
            file_size=metadata.file_size,
            image_width=metadata.width,
            image_height=metadata.height,
            usage_type="Editorial",  # Default to editorial
            territory="Worldwide",
            exclusive=False,
            duration="Perpetual"
        )
        
        # Extract technical metadata from EXIF
        if exif_data:
            descriptor.camera_make = exif_data.get('Make')
            descriptor.camera_model = exif_data.get('Model')
            descriptor.focal_length = exif_data.get('FocalLength')
            descriptor.aperture = exif_data.get('FNumber')
            descriptor.iso = exif_data.get('ISOSpeedRatings')
            descriptor.shutter_speed = exif_data.get('ExposureTime')
            
            # Extract lens information
            lens_info = exif_data.get('LensModel') or exif_data.get('LensSpecification')
            if lens_info:
                descriptor.lens = str(lens_info)
        
        # Set resolution based on DPI
        if metadata.dpi:
            dpi_x, dpi_y = metadata.dpi
            descriptor.resolution = f"{int(dpi_x)}dpi"
        
        return descriptor
    
    def _generate_auto_tags(self, metadata: ImageMetadata) -> List[str]:
        """Generate automatic tags based on metadata"""
        tags = []
        
        # Add technical tags
        if metadata.width > 3000 and metadata.height > 3000:
            tags.append("high_resolution")
        if metadata.width > metadata.height:
            tags.append("landscape")
        elif metadata.height > metadata.width:
            tags.append("portrait")
        else:
            tags.append("square")
            
        # Add EXIF-based tags
        if metadata.exif_data:
            if 'Make' in metadata.exif_data:
                camera_make = metadata.exif_data['Make'].lower()
                tags.append(f"camera_{camera_make}")
                
        # Add IPTC-based tags
        if metadata.iptc_metadata and metadata.iptc_metadata.keywords:
            tags.extend(metadata.iptc_metadata.keywords)
            
        return tags
    
    def _categorize_image(self, metadata: ImageMetadata) -> List[str]:
        """Categorize image based on metadata"""
        categories = []
        
        # Basic categorization
        if metadata.width >= 2400 and metadata.height >= 2400:
            categories.append("professional")
        
        if metadata.iptc_metadata:
            if metadata.iptc_metadata.category:
                categories.append(metadata.iptc_metadata.category.lower())
                
        return categories
    
    async def create_model_release(self, release_data: Dict[str, Any]) -> ModelReleaseForm:
        """Create a new model release form"""
        try:
            # Convert datetime strings to datetime objects
            if isinstance(release_data.get('shoot_date'), str):
                release_data['shoot_date'] = datetime.fromisoformat(release_data['shoot_date'].replace('Z', '+00:00'))
            if isinstance(release_data.get('signed_date'), str):
                release_data['signed_date'] = datetime.fromisoformat(release_data['signed_date'].replace('Z', '+00:00'))
                
            release_form = ModelReleaseForm(**release_data)
            
            # Store in database
            await self.db.model_releases.insert_one(release_form.dict())
            
            logger.info(f"Created model release for {release_form.model_name}")
            return release_form
            
        except Exception as e:
            logger.error(f"Error creating model release: {str(e)}")
            raise
    
    async def validate_commercial_usage(self, metadata: ImageMetadata) -> Dict[str, Any]:
        """Validate image for commercial usage"""
        validation_result = {
            "approved": False,
            "issues": [],
            "requirements": [],
            "risk_level": "high"
        }
        
        # Check for model release
        if not metadata.model_release:
            validation_result["issues"].append("No model release form attached")
            validation_result["requirements"].append("Model release form required for commercial use")
        else:
            release = metadata.model_release
            
            # Check release validity
            if release.usage_rights not in ["commercial", "unrestricted"]:
                validation_result["issues"].append("Model release does not permit commercial usage")
            
            if release.status != "active":
                validation_result["issues"].append(f"Model release status is {release.status}")
                
            # Check if release has expired
            if release.duration_rights != "perpetual":
                # Add expiration checking logic based on duration_rights
                validation_result["requirements"].append("Check release expiration date")
        
        # Check usage rights in metadata
        if metadata.usage_rights == "editorial_only":
            validation_result["issues"].append("Image marked as editorial only")
        
        # Check for proper attribution
        if not metadata.iptc_metadata or not metadata.iptc_metadata.photographer:
            validation_result["requirements"].append("Photographer attribution required")
        
        # Check for copyright notice
        if not metadata.iptc_metadata or not metadata.iptc_metadata.copyright_notice:
            validation_result["requirements"].append("Copyright notice required")
        
        # Determine approval status
        if len(validation_result["issues"]) == 0:
            validation_result["approved"] = True
            validation_result["risk_level"] = "low"
        elif len(validation_result["issues"]) <= 2:
            validation_result["risk_level"] = "medium"
        
        return validation_result
    
    async def store_image_metadata(self, metadata: ImageMetadata) -> str:
        """Store image metadata in database"""
        try:
            # Convert to dict for storage
            metadata_dict = metadata.dict()
            
            # Store in database
            await self.db.image_metadata.insert_one(metadata_dict)
            
            logger.info(f"Stored metadata for image {metadata.file_name}")
            return metadata.id
            
        except Exception as e:
            logger.error(f"Error storing image metadata: {str(e)}")
            raise
    
    async def get_image_metadata(self, image_id: str) -> Optional[ImageMetadata]:
        """Retrieve image metadata by ID"""
        try:
            metadata_doc = await self.db.image_metadata.find_one({"id": image_id})
            if metadata_doc:
                return ImageMetadata(**metadata_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving image metadata: {str(e)}")
            return None

    async def get_user_images(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's uploaded images with metadata"""
        try:
            query = {"user_id": user_id}
            images = []
            
            async for doc in self.db.image_metadata.find(query).sort("uploaded_at", -1).limit(limit):
                # Convert ObjectId to str for JSON serialization
                doc["_id"] = str(doc["_id"])
                
                # Convert datetime to string
                if doc.get("uploaded_at"):
                    doc["uploaded_at"] = doc["uploaded_at"].isoformat()
                if doc.get("shoot_date"):
                    doc["shoot_date"] = doc["shoot_date"].isoformat()
                
                images.append(doc)
            
            return images
            
        except Exception as e:
            logger.error(f"Error getting user images: {str(e)}")
            return []

    async def get_agency_portfolio(self, agency_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get agency portfolio with images and metadata"""
        try:
            # Query for images associated with the agency
            query = {"agency_name": agency_id}
            portfolio = []
            
            async for doc in self.db.image_metadata.find(query).sort("uploaded_at", -1).limit(limit):
                # Convert ObjectId to str for JSON serialization
                doc["_id"] = str(doc["_id"])
                
                # Convert datetime to string
                if doc.get("uploaded_at"):
                    doc["uploaded_at"] = doc["uploaded_at"].isoformat()
                if doc.get("shoot_date"):
                    doc["shoot_date"] = doc["shoot_date"].isoformat()
                
                # Add portfolio-specific metadata
                portfolio_item = {
                    "metadata_id": doc.get("id"),
                    "filename": doc.get("filename"),
                    "model_name": doc.get("model_name"),
                    "photographer_name": doc.get("photographer_name"),
                    "shoot_date": doc.get("shoot_date"),
                    "usage_rights": doc.get("usage_rights"),
                    "headline": doc.get("headline"),
                    "caption": doc.get("caption"),
                    "keywords": doc.get("keywords", []),
                    "content_rating": doc.get("content_rating"),
                    "dimensions": f"{doc.get('width', 0)}x{doc.get('height', 0)}",
                    "file_size": doc.get("file_size"),
                    "uploaded_at": doc.get("uploaded_at"),
                    "validation": doc.get("validation", {}),
                    "commercial_approved": doc.get("commercial_approved", False),
                    "has_model_release": doc.get("model_release") is not None
                }
                
                portfolio.append(portfolio_item)
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting agency portfolio: {str(e)}")
            return []