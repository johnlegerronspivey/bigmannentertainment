"""
Creative Studio for Agencies - Pydantic Models
Full-featured creative content management system with AI-powered design generation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# Enums
class TemplateCategory(str, Enum):
    SOCIAL_MEDIA = "social_media"
    MARKETING = "marketing"
    ADVERTISING = "advertising"
    DOCUMENTS = "documents"
    VIDEO_THUMBNAILS = "video_thumbnails"
    BANNERS = "banners"
    PRESENTATIONS = "presentations"
    EMAIL = "email"


class SocialPlatform(str, Enum):
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_STORY = "instagram_story"
    INSTAGRAM_REEL = "instagram_reel"
    TWITTER_POST = "twitter_post"
    TWITTER_HEADER = "twitter_header"
    FACEBOOK_POST = "facebook_post"
    FACEBOOK_COVER = "facebook_cover"
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_BANNER = "linkedin_banner"
    TIKTOK_VIDEO = "tiktok_video"
    YOUTUBE_THUMBNAIL = "youtube_thumbnail"
    YOUTUBE_BANNER = "youtube_banner"
    PINTEREST_PIN = "pinterest_pin"


class AssetType(str, Enum):
    LOGO = "logo"
    COLOR_PALETTE = "color_palette"
    FONT = "font"
    IMAGE = "image"
    ICON = "icon"
    PATTERN = "pattern"
    TEMPLATE = "template"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CollaboratorRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    COMMENTER = "commenter"
    VIEWER = "viewer"


class ExportFormat(str, Enum):
    PNG = "png"
    JPG = "jpg"
    WEBP = "webp"
    PDF = "pdf"
    SVG = "svg"


# Platform dimensions configuration
PLATFORM_DIMENSIONS = {
    SocialPlatform.INSTAGRAM_POST: {"width": 1080, "height": 1080},
    SocialPlatform.INSTAGRAM_STORY: {"width": 1080, "height": 1920},
    SocialPlatform.INSTAGRAM_REEL: {"width": 1080, "height": 1920},
    SocialPlatform.TWITTER_POST: {"width": 1200, "height": 675},
    SocialPlatform.TWITTER_HEADER: {"width": 1500, "height": 500},
    SocialPlatform.FACEBOOK_POST: {"width": 1200, "height": 630},
    SocialPlatform.FACEBOOK_COVER: {"width": 820, "height": 312},
    SocialPlatform.LINKEDIN_POST: {"width": 1200, "height": 627},
    SocialPlatform.LINKEDIN_BANNER: {"width": 1584, "height": 396},
    SocialPlatform.TIKTOK_VIDEO: {"width": 1080, "height": 1920},
    SocialPlatform.YOUTUBE_THUMBNAIL: {"width": 1280, "height": 720},
    SocialPlatform.YOUTUBE_BANNER: {"width": 2560, "height": 1440},
    SocialPlatform.PINTEREST_PIN: {"width": 1000, "height": 1500},
}


# Models
class BrandColor(BaseModel):
    """Brand color definition"""
    name: str
    hex_code: str
    rgb: Optional[Dict[str, int]] = None
    usage: str = "primary"  # primary, secondary, accent, background, text


class BrandFont(BaseModel):
    """Brand font definition"""
    name: str
    family: str
    weight: str = "regular"
    style: str = "normal"
    usage: str = "heading"  # heading, body, accent


class BrandAsset(BaseModel):
    """Brand asset (logo, image, etc.)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    asset_type: AssetType
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class BrandKit(BaseModel):
    """Complete brand kit for an agency"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    name: str
    description: Optional[str] = None
    
    # Brand identity
    logo_primary: Optional[BrandAsset] = None
    logo_secondary: Optional[BrandAsset] = None
    logo_icon: Optional[BrandAsset] = None
    
    # Colors
    colors: List[BrandColor] = []
    
    # Typography
    fonts: List[BrandFont] = []
    
    # Assets
    assets: List[BrandAsset] = []
    
    # Guidelines
    voice_tone: Optional[str] = None
    tagline: Optional[str] = None
    brand_values: List[str] = []
    
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class DesignElement(BaseModel):
    """Individual design element in a project"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    element_type: str  # text, image, shape, logo, background
    content: Optional[str] = None  # text content or asset URL
    position: Dict[str, float] = {"x": 0, "y": 0}
    size: Dict[str, float] = {"width": 100, "height": 100}
    rotation: float = 0
    opacity: float = 1.0
    z_index: int = 0
    styles: Dict[str, Any] = {}  # CSS-like styles
    is_locked: bool = False


class DesignTemplate(BaseModel):
    """Design template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category: TemplateCategory
    platform: Optional[SocialPlatform] = None
    
    # Dimensions
    width: int
    height: int
    
    # Template content
    elements: List[DesignElement] = []
    background_color: str = "#ffffff"
    background_image: Optional[str] = None
    
    # Metadata
    thumbnail_url: Optional[str] = None
    tags: List[str] = []
    is_premium: bool = False
    usage_count: int = 0
    
    # Creator info
    created_by: Optional[str] = None
    is_system_template: bool = False
    
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class ProjectCollaborator(BaseModel):
    """Project collaborator"""
    user_id: str
    user_email: str
    user_name: str
    role: CollaboratorRole
    invited_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    joined_at: Optional[datetime] = None


class ProjectComment(BaseModel):
    """Comment on a project"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    content: str
    position: Optional[Dict[str, float]] = None  # Position on canvas
    is_resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class ProjectVersion(BaseModel):
    """Version history entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version_number: int
    name: Optional[str] = None
    elements_snapshot: List[DesignElement] = []
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class CreativeProject(BaseModel):
    """Creative design project"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    name: str
    description: Optional[str] = None
    
    # Project type
    category: TemplateCategory
    platform: Optional[SocialPlatform] = None
    template_id: Optional[str] = None  # Source template
    
    # Canvas
    width: int
    height: int
    background_color: str = "#ffffff"
    background_image: Optional[str] = None
    
    # Design content
    elements: List[DesignElement] = []
    
    # Brand association
    brand_kit_id: Optional[str] = None
    
    # Collaboration
    owner_id: str
    collaborators: List[ProjectCollaborator] = []
    comments: List[ProjectComment] = []
    
    # Versioning
    versions: List[ProjectVersion] = []
    current_version: int = 1
    
    # Status
    status: ProjectStatus = ProjectStatus.DRAFT
    
    # Export
    exported_files: List[Dict[str, str]] = []  # {format, url, exported_at}
    
    # Metadata
    tags: List[str] = []
    is_favorite: bool = False
    
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class AIGenerationRequest(BaseModel):
    """Request for AI image generation"""
    prompt: str
    style: Optional[str] = None  # photorealistic, illustration, minimal, etc.
    width: int = 1024
    height: int = 1024
    platform: Optional[SocialPlatform] = None
    brand_kit_id: Optional[str] = None  # To incorporate brand colors
    reference_image_url: Optional[str] = None  # For image editing


class AIGenerationResult(BaseModel):
    """Result of AI image generation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str
    image_url: str
    image_data: Optional[str] = None  # Base64 for preview
    width: int
    height: int
    model_used: str = "gemini-3-pro-image-preview"
    generation_time_ms: int
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class PublishConfig(BaseModel):
    """Configuration for publishing to platforms"""
    platform: SocialPlatform
    caption: Optional[str] = None
    hashtags: List[str] = []
    scheduled_time: Optional[datetime] = None
    is_auto_resize: bool = True


class PublishResult(BaseModel):
    """Result of publishing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    platform: SocialPlatform
    status: str  # pending, published, failed
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())


# Request/Response Models
class CreateBrandKitRequest(BaseModel):
    name: str
    description: Optional[str] = None
    colors: List[BrandColor] = []
    fonts: List[BrandFont] = []
    voice_tone: Optional[str] = None
    tagline: Optional[str] = None
    brand_values: List[str] = []


class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: TemplateCategory
    platform: Optional[SocialPlatform] = None
    template_id: Optional[str] = None
    brand_kit_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    elements: Optional[List[DesignElement]] = None
    background_color: Optional[str] = None
    background_image: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None


class AddCollaboratorRequest(BaseModel):
    user_email: str
    role: CollaboratorRole = CollaboratorRole.EDITOR


class AddCommentRequest(BaseModel):
    content: str
    position: Optional[Dict[str, float]] = None


class ExportProjectRequest(BaseModel):
    format: ExportFormat = ExportFormat.PNG
    quality: int = 90  # 1-100
    scale: float = 1.0  # 1x, 2x, etc.


class PublishProjectRequest(BaseModel):
    platforms: List[PublishConfig]


# Dashboard Stats
class CreativeStudioStats(BaseModel):
    total_projects: int = 0
    projects_in_progress: int = 0
    projects_published: int = 0
    total_brand_kits: int = 0
    total_templates_used: int = 0
    ai_generations_count: int = 0
    total_collaborators: int = 0
    storage_used_mb: float = 0
