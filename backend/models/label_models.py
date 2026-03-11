from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid

# Enums for label operations
class ArtistStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEVELOPMENT = "development"
    RELEASED = "released"
    SUSPENDED = "suspended"

class ContractType(str, Enum):
    RECORDING = "recording"
    DISTRIBUTION = "distribution"
    MANAGEMENT = "management"
    PUBLISHING = "publishing"
    DEVELOPMENT = "development"
    LICENSING = "licensing"

class ContractStatus(str, Enum):
    DRAFT = "draft"
    NEGOTIATION = "negotiation"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class DemoStatus(str, Enum):
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    SIGNED = "signed"

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    PRE_PRODUCTION = "pre_production"
    RECORDING = "recording"
    MIXING = "mixing"
    MASTERING = "mastering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, Enum):
    ALBUM_RELEASE = "album_release"
    SINGLE_RELEASE = "single_release"
    TOUR_PROMOTION = "tour_promotion"
    BRAND_AWARENESS = "brand_awareness"
    SOCIAL_MEDIA = "social_media"
    PR_CAMPAIGN = "pr_campaign"

class FinancialTransactionType(str, Enum):
    ADVANCE = "advance"
    ROYALTY = "royalty"
    EXPENSE = "expense"
    REVENUE = "revenue"
    RECOUP = "recoup"

# Artist Management Models
class ArtistProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage_name: str
    real_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    genres: List[str] = []
    instruments: List[str] = []
    bio: Optional[str] = None
    social_media: Dict[str, str] = {}
    status: ArtistStatus = ArtistStatus.DEVELOPMENT
    signed_date: Optional[datetime] = None
    manager: Optional[str] = None
    booking_agent: Optional[str] = None
    press_contact: Optional[str] = None
    image_url: Optional[str] = None
    monthly_listeners: Dict[str, int] = {}  # Platform: listener count
    streaming_stats: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ArtistContract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artist_id: str
    contract_type: ContractType
    status: ContractStatus = ContractStatus.DRAFT
    start_date: date
    end_date: Optional[date] = None
    territory: List[str] = ["worldwide"]
    
    # Financial terms
    advance_amount: Optional[float] = 0.0
    royalty_rate: float = 0.0  # Percentage
    mechanical_rate: Optional[float] = None
    performance_rate: Optional[float] = None
    sync_rate: Optional[float] = None
    
    # Recording commitment
    album_commitment: Optional[int] = None
    single_commitment: Optional[int] = None
    option_periods: Optional[int] = None
    
    # Terms and conditions
    exclusive: bool = True
    recoupable_expenses: List[str] = []
    creative_control: Dict[str, Any] = {}
    
    # Legal information
    contract_document_url: Optional[str] = None
    signed_by_artist: Optional[bool] = None
    signed_by_label: Optional[bool] = None
    witness: Optional[str] = None
    
    # Metadata
    created_by: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# A&R (Artist & Repertoire) Models
class DemoSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artist_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    genre: str
    submission_type: str  # "demo", "EPK", "live_performance"
    
    # Music files and materials
    audio_files: List[Dict[str, str]] = []  # {"title": "", "url": "", "duration": ""}
    video_links: List[str] = []
    press_kit_url: Optional[str] = None
    social_media_links: Dict[str, str] = {}
    
    # Artist information
    bio: Optional[str] = None
    experience: Optional[str] = None
    achievements: Optional[str] = None
    touring_history: Optional[str] = None
    current_fanbase: Optional[Dict[str, int]] = {}
    
    # A&R evaluation
    status: DemoStatus = DemoStatus.SUBMITTED
    assigned_ar: Optional[str] = None
    evaluation_score: Optional[float] = None  # 1-10 scale
    evaluation_notes: Optional[str] = None
    feedback_sent: bool = False
    
    # Follow-up
    follow_up_date: Optional[datetime] = None
    meeting_scheduled: Optional[datetime] = None
    contract_offered: Optional[bool] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TalentScout(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    specialization: List[str] = []  # Genres they focus on
    territory: List[str] = []
    contact_info: Dict[str, str] = {}
    active: bool = True
    discoveries: List[str] = []  # Artist IDs they discovered
    success_rate: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Studio & Production Management Models
class RecordingStudio(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: Dict[str, str]  # address, city, state, country
    contact_info: Dict[str, str]
    daily_rate: float
    hourly_rate: Optional[float] = None
    equipment: List[str] = []
    amenities: List[str] = []
    capacity: int
    availability: Dict[str, Any] = {}  # Calendar integration
    rating: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RecordingProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    artist_id: str
    project_type: str  # "album", "EP", "single", "mixtape"
    status: ProjectStatus = ProjectStatus.PLANNING
    
    # Timeline
    start_date: Optional[date] = None
    expected_completion: Optional[date] = None
    release_date: Optional[date] = None
    
    # Studio information
    studio_id: Optional[str] = None
    producer: Optional[str] = None
    engineer: Optional[str] = None
    
    # Track information
    tracks: List[Dict[str, Any]] = []  # Track details, status, files
    total_tracks: int = 0
    completed_tracks: int = 0
    
    # Budget and costs
    budget: float = 0.0
    spent: float = 0.0
    expenses: List[Dict[str, Any]] = []
    
    # Personnel
    team_members: List[Dict[str, str]] = []  # role, name, contact
    
    # Files and assets
    session_files: List[str] = []
    mix_files: List[str] = []
    master_files: List[str] = []
    artwork: Optional[str] = None
    
    notes: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Marketing Campaign Models
class MarketingCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    artist_id: str
    release_id: Optional[str] = None  # Associated release
    campaign_type: CampaignType
    
    # Timeline
    start_date: date
    end_date: date
    launch_date: Optional[date] = None
    
    # Target audience
    target_demographics: Dict[str, Any] = {}
    target_territories: List[str] = []
    target_platforms: List[str] = []
    
    # Campaign elements
    social_media_strategy: Dict[str, Any] = {}
    pr_strategy: Dict[str, Any] = {}
    advertising_strategy: Dict[str, Any] = {}
    influencer_strategy: Dict[str, Any] = {}
    
    # Budget and spend
    total_budget: float = 0.0
    spent: float = 0.0
    budget_breakdown: Dict[str, float] = {}
    
    # Content assets
    creative_assets: List[Dict[str, str]] = []  # Images, videos, copy
    press_materials: List[Dict[str, str]] = []
    
    # Performance metrics
    reach: Optional[int] = None
    impressions: Optional[int] = None
    engagement_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    roi: Optional[float] = None
    
    # Team
    campaign_manager: str
    team_members: List[str] = []
    external_agencies: List[Dict[str, str]] = []
    
    status: str = "planning"  # planning, active, completed, paused
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PressRelease(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    headline: str
    artist_id: str
    campaign_id: Optional[str] = None
    
    # Content
    summary: str
    body: str
    quotes: List[Dict[str, str]] = []  # speaker, quote
    
    # Media
    images: List[str] = []
    audio_samples: List[str] = []
    video_links: List[str] = []
    
    # Distribution
    target_outlets: List[str] = []
    sent_to: List[Dict[str, Any]] = []  # outlet, date, response
    pickup_rate: Optional[float] = None
    
    # Contact info
    media_contact: str
    contact_email: str
    contact_phone: Optional[str] = None
    
    embargo_date: Optional[datetime] = None
    published_date: Optional[datetime] = None
    status: str = "draft"  # draft, sent, published
    
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Financial Management Models
class FinancialTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_type: FinancialTransactionType
    artist_id: str
    project_id: Optional[str] = None
    contract_id: Optional[str] = None
    
    amount: float
    currency: str = "USD"
    description: str
    category: str  # "recording", "marketing", "advance", "royalty", etc.
    
    # Payment details
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    invoice_number: Optional[str] = None
    
    # Dates
    transaction_date: date
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    
    # Status
    status: str = "pending"  # pending, paid, overdue, cancelled
    
    # Recoupment tracking
    recoupable: bool = False
    recouped: bool = False
    recouped_amount: float = 0.0
    
    created_by: str
    approved_by: Optional[str] = None
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RoyaltyStatement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artist_id: str
    contract_id: str
    statement_period_start: date
    statement_period_end: date
    
    # Sales and streaming data
    physical_sales: Dict[str, Any] = {}  # Territory: units, revenue
    digital_sales: Dict[str, Any] = {}
    streaming_data: Dict[str, Any] = {}  # Platform: streams, revenue
    sync_revenue: Dict[str, Any] = {}
    performance_revenue: Dict[str, Any] = {}
    
    # Calculations
    gross_revenue: float = 0.0
    label_share: float = 0.0
    artist_share: float = 0.0
    recoupable_expenses: float = 0.0
    net_payable: float = 0.0
    
    # Payment
    payment_due: bool = False
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    
    statement_file_url: Optional[str] = None
    sent_to_artist: bool = False
    
    created_by: str
    approved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Analytics and Reporting Models
class ArtistAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artist_id: str
    reporting_period_start: date
    reporting_period_end: date
    
    # Streaming analytics
    spotify_data: Dict[str, Any] = {}
    apple_music_data: Dict[str, Any] = {}
    youtube_data: Dict[str, Any] = {}
    other_platforms: Dict[str, Any] = {}
    
    # Social media analytics
    instagram_data: Dict[str, Any] = {}
    tiktok_data: Dict[str, Any] = {}
    twitter_data: Dict[str, Any] = {}
    facebook_data: Dict[str, Any] = {}
    
    # Sales data
    physical_sales: Dict[str, Any] = {}
    digital_sales: Dict[str, Any] = {}
    merchandise: Dict[str, Any] = {}
    
    # Performance metrics
    total_streams: int = 0
    monthly_listeners: int = 0
    social_followers: int = 0
    engagement_rate: float = 0.0
    
    # Financial metrics
    total_revenue: float = 0.0
    revenue_breakdown: Dict[str, float] = {}
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str

# Label Dashboard Models
class LabelDashboard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reporting_period_start: date
    reporting_period_end: date
    
    # Overall label metrics
    total_artists: int = 0
    active_projects: int = 0
    releases_this_period: int = 0
    total_streams: int = 0
    total_revenue: float = 0.0
    
    # Top performers
    top_artists: List[Dict[str, Any]] = []
    top_releases: List[Dict[str, Any]] = []
    trending_genres: List[str] = []
    
    # Financial summary
    revenue_breakdown: Dict[str, float] = {}
    expense_breakdown: Dict[str, float] = {}
    profit_loss: float = 0.0
    
    # A&R metrics
    demos_received: int = 0
    artists_signed: int = 0
    conversion_rate: float = 0.0
    
    # Marketing metrics
    active_campaigns: int = 0
    campaign_reach: int = 0
    average_roi: float = 0.0
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str

# Request/Response Models
class ArtistCreate(BaseModel):
    stage_name: str
    real_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    genres: List[str] = []
    bio: Optional[str] = None
    social_media: Dict[str, str] = {}

class ArtistUpdate(BaseModel):
    stage_name: Optional[str] = None
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    genres: Optional[List[str]] = None
    bio: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    status: Optional[ArtistStatus] = None

class DemoSubmissionCreate(BaseModel):
    artist_name: str
    contact_email: str
    genre: str
    submission_type: str
    audio_files: List[Dict[str, str]] = []
    bio: Optional[str] = None

class ContractCreate(BaseModel):
    artist_id: str
    contract_type: ContractType
    start_date: date
    royalty_rate: float
    advance_amount: Optional[float] = 0.0
    exclusive: bool = True

class ProjectCreate(BaseModel):
    title: str
    artist_id: str
    project_type: str
    budget: float = 0.0
    expected_completion: Optional[date] = None

class CampaignCreate(BaseModel):
    name: str
    artist_id: str
    campaign_type: CampaignType
    start_date: date
    end_date: date
    total_budget: float = 0.0