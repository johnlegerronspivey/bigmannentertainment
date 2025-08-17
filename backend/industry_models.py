from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# Industry Identifiers Models (IPI, ISNI, AARC)
class IndustryIdentifier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_name: str  # Name of the person or organization
    entity_type: str  # "company", "individual", "band", "organization"
    
    # IPI (Interested Parties Information) Numbers
    ipi_number: Optional[str] = None  # IPI number (e.g., 813048171, 578413032)
    ipi_role: Optional[str] = None  # "songwriter", "composer", "lyricist", "publisher", "performer", "producer"
    
    # ISNI (International Standard Name Identifier) Numbers  
    isni_number: Optional[str] = None  # ISNI number (e.g., 0000000491551894)
    isni_status: Optional[str] = "active"  # active, inactive, pending
    
    # AARC (Alliance of Artists and Recording Companies) Numbers
    aarc_number: Optional[str] = None  # AARC number (e.g., RC00002057, FA02933539)
    aarc_type: Optional[str] = None  # "record_company", "featured_artist", "performer"
    
    territory: str = "US"  # Territory where identifiers are registered
    status: str = "active"  # active, inactive, pending, suspended
    contact_info: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Music Data Exchange (MDX) Integration Models
class MusicDataExchange(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mdx_id: Optional[str] = None  # MDX system ID
    entity_name: str  # Artist, Label, Publisher name
    entity_type: str  # artist, label, publisher, distributor
    
    # Metadata Information
    metadata_schema: Dict[str, Any] = {}  # MDX metadata structure
    rights_information: Dict[str, Any] = {}  # Rights and ownership data
    licensing_data: Dict[str, Any] = {}  # Licensing and clearance info
    
    # Integration Configuration
    api_credentials: Dict[str, str] = {}  # MDX API access credentials
    data_mapping: Dict[str, Any] = {}  # Data structure mapping
    sync_frequency: str = "daily"  # real_time, hourly, daily, weekly
    last_sync: Optional[datetime] = None
    sync_status: str = "pending"  # pending, active, failed, paused
    
    # Metadata Standards
    ddex_compliant: bool = True
    isrc_codes: List[str] = []
    iswc_codes: List[str] = []
    upc_codes: List[str] = []
    
    # Rights and Ownership
    copyright_owners: List[Dict[str, Any]] = []
    mechanical_rights: Dict[str, Any] = {}
    performance_rights: Dict[str, Any] = {}
    synchronization_rights: Dict[str, Any] = {}
    
    # Distribution Information
    territories: List[str] = []
    distribution_channels: List[str] = []
    release_schedule: Dict[str, Any] = {}
    
    status: str = "active"  # active, inactive, pending, suspended
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# MDX Track/Release Model
class MDXTrack(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mdx_track_id: Optional[str] = None
    
    # Basic Track Information
    title: str
    artist_name: str
    album_title: Optional[str] = None
    track_number: Optional[int] = None
    duration: Optional[int] = None  # Duration in seconds
    release_date: Optional[datetime] = None
    
    # Identification Codes
    isrc: Optional[str] = None
    iswc: Optional[str] = None
    upc: Optional[str] = None  # For album/release
    
    # Rights and Ownership
    songwriter_splits: List[Dict[str, Any]] = []  # Songwriter percentages
    publisher_splits: List[Dict[str, Any]] = []  # Publisher percentages
    performer_credits: List[Dict[str, Any]] = []  # Performer information
    producer_credits: List[Dict[str, Any]] = []  # Producer information
    
    # MDX Specific Data
    mdx_metadata: Dict[str, Any] = {}
    rights_clearance_status: str = "pending"  # pending, cleared, blocked
    distribution_rights: Dict[str, Any] = {}
    
    # Big Mann Entertainment Integration
    big_mann_release: bool = False
    monetization_strategy: Dict[str, Any] = {}
    
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# MDX Rights Management Model
class MDXRightsManagement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4))
    mdx_rights_id: Optional[str] = None
    
    # Rights Information
    rights_type: str  # mechanical, performance, synchronization, master, publishing
    rights_holder: str  # Name of rights holder
    rights_percentage: float  # Percentage of rights owned (0.0-100.0)
    
    # Territory and Duration
    territories: List[str] = []  # Territories where rights apply
    rights_start_date: datetime
    rights_end_date: Optional[datetime] = None  # None for perpetual rights
    
    # Associated Content
    track_ids: List[str] = []  # Associated track IDs
    album_ids: List[str] = []  # Associated album IDs
    
    # Rights Status
    clearance_status: str = "active"  # active, expired, disputed, pending
    licensing_terms: Dict[str, Any] = {}
    royalty_rates: Dict[str, Any] = {}
    
    # MDX Integration
    mdx_sync_status: str = "synced"  # synced, pending, failed
    last_mdx_update: Optional[datetime] = None
    
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# MDX Analytics and Reporting Model
class MDXAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Reporting Period
    report_date: datetime
    report_type: str  # daily, weekly, monthly, quarterly, annual
    
    # Metadata Quality Metrics
    metadata_completeness: float  # Percentage of complete metadata fields
    rights_clearance_rate: float  # Percentage of rights cleared
    sync_success_rate: float  # Percentage of successful MDX syncs
    
    # Content Statistics
    total_tracks_managed: int = 0
    total_rights_cleared: int = 0
    total_distribution_channels: int = 0
    total_territories_covered: int = 0
    
    # Revenue Impact
    estimated_revenue_impact: float = 0.0
    rights_revenue_tracked: float = 0.0
    metadata_optimization_savings: float = 0.0
    
    # Performance Metrics
    sync_performance: Dict[str, Any] = {}
    error_rates: Dict[str, float] = {}
    processing_times: Dict[str, float] = {}
    
    # Big Mann Entertainment Specific
    big_mann_tracks: int = 0
    big_mann_revenue_impact: float = 0.0
    
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Mechanical Licensing Collective (MLC) Integration Models
class MechanicalLicensingCollective(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mlc_account_id: Optional[str] = None  # MLC system account ID
    
    # Entity Information
    entity_name: str  # Publisher, songwriter, or administrator name
    entity_type: str  # publisher, songwriter, admin, dsp
    mlc_member_status: str = "pending"  # pending, active, inactive, suspended
    
    # Registration Information
    registration_date: Optional[datetime] = None
    member_number: Optional[str] = None
    account_status: str = "active"  # active, inactive, suspended, closed
    
    # Contact and Business Information
    contact_info: Dict[str, Any] = {}
    business_info: Dict[str, Any] = {}
    tax_info: Dict[str, Any] = {}
    
    # Rights and Ownership
    publishing_rights: Dict[str, Any] = {}
    mechanical_rights_share: float = 0.0  # Percentage of mechanical rights owned
    territories: List[str] = ["US"]  # MLC primarily handles US
    
    # API Configuration
    api_credentials: Dict[str, str] = {}
    api_access_level: str = "standard"  # standard, premium, administrator
    data_submission_frequency: str = "monthly"  # daily, weekly, monthly, quarterly
    
    # Integration Settings
    automated_reporting: bool = True
    royalty_collection_enabled: bool = True
    metadata_sync_enabled: bool = True
    dispute_management_enabled: bool = True
    
    status: str = "active"
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# MLC Musical Work Registration
class MLCMusicalWork(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mlc_work_id: Optional[str] = None
    
    # Work Identification
    work_title: str
    alternative_titles: List[str] = []
    iswc: Optional[str] = None  # International Standard Musical Work Code
    
    # Rights Holders Information
    publishers: List[Dict[str, Any]] = []  # Publisher information with shares
    songwriters: List[Dict[str, Any]] = []  # Songwriter information with shares
    administrators: List[Dict[str, Any]] = []  # Administrative information
    
    # Mechanical Rights Information
    mechanical_rights_share: Dict[str, float] = {}  # Rights holder shares
    territorial_restrictions: List[str] = []
    rights_start_date: datetime
    rights_end_date: Optional[datetime] = None
    
    # MLC Specific Data
    submission_status: str = "pending"  # pending, submitted, accepted, rejected
    last_submission_date: Optional[datetime] = None
    mlc_registration_number: Optional[str] = None
    
    # Big Mann Entertainment Integration
    big_mann_work: bool = False
    internal_catalog_number: Optional[str] = None
    
    # Metadata and History
    submission_history: List[Dict[str, Any]] = []
    dispute_history: List[Dict[str, Any]] = []
    
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# MLC Royalty Collection and Distribution
class MLCRoyaltyReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mlc_report_id: Optional[str] = None
    
    # Reporting Period
    report_period_start: datetime
    report_period_end: datetime
    report_type: str  # monthly, quarterly, annual, special
    
    # Financial Information
    total_royalties_collected: float = 0.0
    total_royalties_distributed: float = 0.0
    administrative_fees: float = 0.0
    net_distribution: float = 0.0
    
    # Distribution Breakdown
    publisher_distributions: List[Dict[str, Any]] = []
    songwriter_distributions: List[Dict[str, Any]] = []
    unclaimed_royalties: float = 0.0
    
    # Source Information
    digital_service_providers: List[str] = []  # Spotify, Apple Music, etc.
    usage_data: Dict[str, Any] = {}
    stream_counts: Dict[str, int] = {}
    
    # MLC Processing Information
    processing_status: str = "pending"  # pending, processing, completed, disputed
    distribution_date: Optional[datetime] = None
    payment_method: str = "direct_deposit"
    
    # Big Mann Entertainment Specific
    big_mann_royalties: float = 0.0
    big_mann_works_count: int = 0
    
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

# MLC Usage Data and Matching
class MLCUsageData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mlc_usage_id: Optional[str] = None
    
    # Track Identification
    track_title: str
    artist_name: str
    album_title: Optional[str] = None
    isrc: Optional[str] = None
    duration: Optional[int] = None
    
    # Digital Service Provider Information
    dsp_name: str  # Spotify, Apple Music, Amazon Music, etc.
    dsp_track_id: Optional[str] = None
    
    # Usage Statistics
    play_count: int = 0
    stream_date: datetime
    territory: str = "US"
    revenue_generated: float = 0.0
    mechanical_royalty_due: float = 0.0
    
    # Matching Information
    matched_work_id: Optional[str] = None  # MLCMusicalWork ID
    matching_confidence: float = 0.0  # 0.0 to 1.0
    matching_status: str = "unmatched"  # unmatched, matched, disputed
    
    # Rights Holder Information
    publisher_share: Dict[str, float] = {}
    songwriter_share: Dict[str, float] = {}
    
    # Processing Information
    processed_date: Optional[datetime] = None
    royalty_distributed: bool = False
    distribution_date: Optional[datetime] = None
    
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# MLC Claims and Disputes Management  
class MLCClaimsDispute(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mlc_claim_id: Optional[str] = None
    
    # Claim Information
    claim_type: str  # ownership_claim, royalty_dispute, metadata_correction
    work_title: str
    work_id: Optional[str] = None
    claimant_name: str
    claimant_type: str  # publisher, songwriter, administrator
    
    # Claim Details
    claimed_rights_percentage: float = 0.0
    effective_date: datetime
    supporting_documentation: List[str] = []
    claim_description: str
    
    # Disputed Information
    disputed_by: List[str] = []
    dispute_reason: str = ""
    resolution_method: str = "mediation"  # mediation, arbitration, legal
    
    # Processing Status
    claim_status: str = "pending"  # pending, under_review, approved, rejected, disputed
    submission_date: datetime = Field(default_factory=datetime.utcnow)
    resolution_date: Optional[datetime] = None
    
    # Financial Impact
    affected_royalties: float = 0.0
    royalty_hold_amount: float = 0.0
    
    # Big Mann Entertainment Integration
    big_mann_involvement: bool = False
    internal_reference: Optional[str] = None
    
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Big Mann Entertainment MLC Configuration
BIG_MANN_MLC_CONFIG = {
    "entity_name": "Big Mann Entertainment",
    "entity_type": "publisher",
    "member_information": {
        "registration_status": "active",
        "member_type": "publisher",
        "account_classification": "independent_publisher",
        "territories": ["US"],
        "rights_administration": True
    },
    "publishing_information": {
        "publisher_name": "Big Mann Entertainment",
        "publisher_ipi": "813048171",
        "publisher_share": 50.0,  # 50% publisher share
        "administrative_percentage": 100.0,
        "territories_of_representation": ["US"],
        "sub_publishers": []
    },
    "songwriter_information": {
        "primary_songwriter": {
            "name": "John LeGerron Spivey",
            "ipi_number": "578413032",
            "isni_number": "0000000491551894",
            "songwriter_share": 50.0,  # 50% songwriter share
            "territories": ["US"],
            "membership_status": "active"
        }
    },
    "royalty_collection": {
        "collection_enabled": True,
        "distribution_method": "direct_deposit",
        "minimum_threshold": 1.00,  # Minimum $1.00 for distribution
        "frequency": "monthly",
        "currency": "USD"
    },
    "reporting_configuration": {
        "automated_reporting": True,
        "report_frequency": "monthly",
        "data_formats": ["CSV", "JSON", "XML"],
        "real_time_matching": True,
        "usage_data_processing": True
    },
    "integration_features": {
        "metadata_sync": True,
        "automated_work_registration": True,
        "dispute_management": True,
        "royalty_reconciliation": True,
        "cross_platform_tracking": True,
        "analytics_dashboard": True
    },
    "business_configuration": {
        "business_name": "Big Mann Entertainment",
        "business_address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
        "business_phone": "334-669-8638",
        "tax_id": "12800",
        "business_type": "Sound Recording Industries",
        "naics_code": "512200"
    }
}
BIG_MANN_MDX_CONFIG = {
    "entity_name": "Big Mann Entertainment",
    "entity_type": "label",
    "mdx_configuration": {
        "api_version": "v2.1",
        "supported_formats": ["JSON", "XML", "DDEX"],
        "sync_frequency": "real_time",
        "metadata_standards": ["DDEX", "ISRC", "ISWC", "UPC"],
        "territories": ["US", "UK", "CA", "AU", "global"],
        "distribution_channels": [
            "Spotify", "Apple Music", "Amazon Music", "YouTube Music",
            "Tidal", "Bandcamp", "SoundCloud", "Deezer"
        ]
    },
    "rights_management": {
        "mechanical_rights": True,
        "performance_rights": True,
        "synchronization_rights": True,
        "master_rights": True,
        "publishing_rights": True
    },
    "integration_features": {
        "automated_metadata_sync": True,
        "rights_clearance_automation": True,
        "revenue_tracking": True,
        "analytics_reporting": True,
        "multi_territory_support": True,
        "real_time_updates": True
    },
    "big_mann_specific": {
        "ipi_integration": True,
        "isni_integration": True,
        "aarc_integration": True,
        "comprehensive_monetization": True,
        "cross_platform_optimization": True
    }
}

# Photography Services Model
class PhotographyService(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "photography_service"  # photography_service
    service_type: str  # album_cover, promotional, event, fashion, commercial
    specialties: List[str] = []
    price_range: str = ""  # e.g., "$500-$2500"
    equipment_specs: Dict[str, Any] = {}
    portfolio_url: Optional[str] = None
    booking_availability: str = "available"  # available, booked, limited
    turnaround_time: str = ""  # e.g., "3-7 days"
    territories: List[str] = []
    contact_info: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Stock Photography Platform Model
class StockPhotographyPlatform(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "stock_photography"
    platform_type: str  # major, independent, niche
    api_endpoint: Optional[str] = None
    commission_rate: str = ""  # e.g., "15-40%"
    content_types: List[str] = []  # photos, vectors, videos, templates
    upload_requirements: Dict[str, Any] = {}
    review_process: str = ""  # automated, manual, hybrid
    payout_schedule: str = ""  # monthly, quarterly, on-demand
    territories: List[str] = []
    monetization_options: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Video Production Service Model
class VideoProductionService(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "video_production"
    production_type: str  # music_videos, commercial, documentary, live_stream
    specialties: List[str] = []
    equipment_capabilities: List[str] = []  # 4K, 8K, drone, steadicam, etc.
    crew_size: str = ""  # e.g., "5-15 people"
    price_range: str = ""
    post_production_services: List[str] = []  # editing, color_grading, sound_design
    delivery_formats: List[str] = []  # mp4, mov, prores, etc.
    territories: List[str] = []
    portfolio_url: Optional[str] = None
    booking_calendar: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Podcast Platform Model
class PodcastPlatform(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "podcast_platform"
    platform_type: str  # hosting, distribution, production
    api_endpoint: Optional[str] = None
    monetization_options: List[str] = []  # ad_revenue, subscriptions, donations
    content_types: List[str] = []  # audio, video, live
    analytics_features: List[str] = []
    distribution_reach: List[str] = []  # spotify, apple, google, etc.
    upload_limits: Dict[str, Any] = {}
    pricing_model: str = ""  # free, freemium, subscription, per_episode
    territories: List[str] = []
    integration_capabilities: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Live Streaming Platform Model
class LiveStreamingPlatform(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "live_streaming"
    platform_type: str  # major, music_focused, gaming, general
    api_endpoint: Optional[str] = None
    monetization_options: List[str] = []
    content_types: List[str] = []
    streaming_quality: List[str] = []  # 720p, 1080p, 4K
    chat_features: List[str] = []
    interactive_features: List[str] = []  # polls, q&a, donations
    audience_size_limit: Optional[int] = None
    concurrent_viewers_limit: Optional[int] = None
    territories: List[str] = []
    integration_tools: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Gaming/Esports Platform Model
class GamingEsportsPlatform(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "gaming_esports"
    platform_type: str  # game_platform, esports_org, streaming_service
    specialties: List[str] = []
    monetization_options: List[str] = []
    content_types: List[str] = []  # soundtracks, sfx, streaming_music
    audience_demographics: Dict[str, Any] = {}
    partnership_opportunities: List[str] = []
    licensing_options: List[str] = []
    territories: List[str] = []
    api_integration: Optional[str] = None
    revenue_sharing: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Social Media Content Platform Model
class SocialMediaPlatform(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "social_media"
    platform_type: str  # photo_sharing, video_sharing, mixed_content
    api_endpoint: Optional[str] = None
    content_types: List[str] = []
    monetization_options: List[str] = []
    content_specs: Dict[str, Any] = {}  # image_sizes, video_lengths, etc.
    engagement_features: List[str] = []
    advertising_options: List[str] = []
    creator_tools: List[str] = []
    analytics_dashboard: bool = True
    territories: List[str] = []
    integration_capabilities: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Enhanced Revenue Tracking for Entertainment Industry
class EntertainmentRevenueStream(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_name: str
    source_category: str  # photography, video, streaming, gaming, etc.
    revenue_type: str  # commission, licensing, subscription, ad_revenue, etc.
    amount: float
    currency: str = "USD"
    date_earned: datetime
    payout_status: str = "pending"  # pending, processing, paid
    payout_date: Optional[datetime] = None
    commission_rate: Optional[float] = None
    gross_revenue: Optional[float] = None
    net_revenue: float
    platform_fees: Optional[float] = None
    territories: List[str] = []
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Content Monetization Model
class ContentMonetization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    content_type: str  # photo, video, audio, live_stream, etc.
    content_title: str
    monetization_methods: List[str] = []  # ads, subscriptions, tips, licensing
    revenue_streams: List[EntertainmentRevenueStream] = []
    total_revenue: float = 0.0
    active_platforms: List[str] = []
    performance_metrics: Dict[str, Any] = {}
    optimization_suggestions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
class IndustryPartner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # streaming, record_label, radio, tv, venue, booking, etc.
    tier: str  # major, independent, regional, local
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    authentication_type: str = "none"  # none, api_key, oauth, jwt
    status: str = "active"  # active, inactive, pending, suspended
    integration_type: str  # full_api, webhook, manual, scheduled
    supported_formats: List[str] = []  # mp3, wav, flac, mp4, etc.
    content_types: List[str] = []  # audio, video, podcast, live
    territories: List[str] = []  # US, UK, global, etc.
    revenue_share: Optional[float] = None
    contact_info: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    ipi_numbers: List[str] = []  # Associated IPI numbers
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StreamingPlatform(IndustryPartner):
    monthly_active_users: Optional[int] = None
    audio_quality: List[str] = []  # 128kbps, 320kbps, lossless
    video_quality: List[str] = []  # HD, 4K, 8K
    subscription_tiers: List[str] = []
    geographic_coverage: List[str] = []

class RecordLabel(IndustryPartner):
    label_type: str  # major, independent, boutique
    distribution_network: List[str] = []
    artist_roster_size: Optional[int] = None
    genres: List[str] = []

class RadioStation(IndustryPartner):
    frequency: Optional[str] = None
    market_size: str  # major, medium, small
    format: str  # pop, rock, country, talk, etc.
    coverage_area: str
    listener_demographics: Dict[str, Any] = {}

class TVNetwork(IndustryPartner):
    network_type: str  # broadcast, cable, streaming, satellite
    programming_types: List[str] = []
    target_demographics: Dict[str, Any] = {}
    prime_time_slots: List[str] = []

class Venue(IndustryPartner):
    venue_type: str  # arena, theater, club, festival, outdoor
    capacity: Optional[int] = None
    location: Dict[str, str] = {}
    technical_specs: Dict[str, Any] = {}
    booking_calendar: Dict[str, Any] = {}

class BookingAgency(IndustryPartner):
    agency_size: str  # boutique, mid_tier, major
    artist_types: List[str] = []
    commission_rate: Optional[float] = None
    territory_focus: List[str] = []

# Distribution and Content Models
class ContentDistribution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    partner_id: str
    distribution_status: str  # pending, processing, live, failed, removed
    distribution_date: Optional[datetime] = None
    content_url: Optional[str] = None
    partner_content_id: Optional[str] = None
    metadata_mapping: Dict[str, Any] = {}
    performance_metrics: Dict[str, Any] = {}
    revenue_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IndustryAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str
    product_id: Optional[str] = None
    date: datetime
    plays: int = 0
    downloads: int = 0
    streams: int = 0
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    revenue: float = 0.0
    territories: Dict[str, int] = {}
    demographics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RevenueTracking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    distribution_id: str
    partner_id: str
    product_id: str
    revenue_type: str  # streaming, download, licensing, sync
    gross_amount: float
    partner_fee: float
    net_amount: float
    currency: str = "USD"
    period_start: datetime
    period_end: datetime
    payout_status: str  # pending, processing, paid, disputed
    payout_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Industry Connection Templates
# Enhanced Entertainment Industry Partners with Photography, Video, Streaming, Gaming
ENTERTAINMENT_INDUSTRY_PARTNERS = {
    # Existing categories
    "streaming_platforms": {
        "major": [
            {"name": "Spotify", "api_endpoint": "https://api.spotify.com/v1", "supported_formats": ["mp3", "flac"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Apple Music", "api_endpoint": "https://api.music.apple.com/v1", "supported_formats": ["mp3", "aac"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Amazon Music", "api_endpoint": "https://api.amazonalexa.com", "supported_formats": ["mp3", "flac"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "YouTube Music", "api_endpoint": "https://developers.google.com/youtube/v3", "supported_formats": ["mp3", "mp4"], "content_types": ["audio", "video"], "territories": ["global"]},
            {"name": "Tidal", "api_endpoint": "https://api.tidal.com/v1", "supported_formats": ["flac", "mp3"], "content_types": ["audio"], "territories": ["global"]}
        ],
        "independent": [
            {"name": "Bandcamp", "api_endpoint": "https://bandcamp.com/api", "supported_formats": ["flac", "mp3"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "SoundCloud", "api_endpoint": "https://api.soundcloud.com", "supported_formats": ["mp3"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Deezer", "api_endpoint": "https://api.deezer.com", "supported_formats": ["mp3"], "content_types": ["audio"], "territories": ["global"]}
        ]
    },
    
    # Professional Photography Services
    "photography_services": {
        "album_cover": [
            {"name": "Album Cover Zone", "specialties": ["album_covers", "single_covers", "EP_covers"], "price_range": "$500-$2500", "territories": ["US", "UK", "global"]},
            {"name": "Creative Alliance", "specialties": ["album_art", "promotional_photos", "band_photography"], "price_range": "$750-$5000", "territories": ["global"]},
            {"name": "Music Photography Co", "specialties": ["conceptual_covers", "artistic_photography"], "price_range": "$1000-$3000", "territories": ["US", "CA"]}
        ],
        "promotional": [
            {"name": "Artist Photo Studio", "specialties": ["headshots", "promotional_photos", "press_photos"], "price_range": "$300-$1500", "territories": ["US"]},
            {"name": "Music Marketing Photos", "specialties": ["social_media_content", "promotional_campaigns"], "price_range": "$400-$2000", "territories": ["global"]},
            {"name": "Professional Music Photography", "specialties": ["artist_portraits", "lifestyle_shots"], "price_range": "$500-$2500", "territories": ["US", "UK"]}
        ],
        "event": [
            {"name": "Concert Photography Network", "specialties": ["live_concerts", "music_festivals", "studio_sessions"], "price_range": "$200-$1000", "territories": ["US"]},
            {"name": "Live Music Photos", "specialties": ["performance_photography", "backstage_photography"], "price_range": "$250-$1200", "territories": ["global"]},
            {"name": "Event Photo Services", "specialties": ["venue_photography", "audience_shots", "atmosphere_capture"], "price_range": "$300-$800", "territories": ["US", "UK", "CA"]}
        ]
    },
    
    # Stock Photography Platforms
    "stock_photography": {
        "major": [
            {"name": "Shutterstock", "api_endpoint": "https://api.shutterstock.com/v2", "commission_rate": "15-40%", "content_types": ["photos", "vectors", "videos"], "territories": ["global"]},
            {"name": "Getty Images", "api_endpoint": "https://api.gettyimages.com/v3", "commission_rate": "20-45%", "content_types": ["photos", "videos", "editorial"], "territories": ["global"]},
            {"name": "Adobe Stock", "api_endpoint": "https://stock.adobe.io/Rest/Media/1", "commission_rate": "33-35%", "content_types": ["photos", "vectors", "videos", "templates"], "territories": ["global"]},
            {"name": "iStock", "api_endpoint": "https://api.istockphoto.com", "commission_rate": "15-25%", "content_types": ["photos", "vectors", "videos"], "territories": ["global"]}
        ],
        "independent": [
            {"name": "Unsplash", "api_endpoint": "https://api.unsplash.com", "commission_rate": "free+attribution", "content_types": ["photos"], "territories": ["global"]},
            {"name": "500px", "api_endpoint": "https://api.500px.com/v1", "commission_rate": "30-60%", "content_types": ["photos"], "territories": ["global"]},
            {"name": "Alamy", "api_endpoint": "https://api.alamy.com", "commission_rate": "40-50%", "content_types": ["photos", "vectors"], "territories": ["global"]}
        ]
    },
    
    # Social Media Photography Platforms
    "social_media_photography": {
        "content_creation": [
            {"name": "Instagram Creator Studio", "api_endpoint": "https://graph.facebook.com/v17.0", "content_types": ["photos", "stories", "reels"], "monetization": ["creator_fund", "brand_partnerships"], "territories": ["global"]},
            {"name": "TikTok Creator Center", "api_endpoint": "https://developers.tiktok.com/doc", "content_types": ["short_videos", "photos"], "monetization": ["creator_fund", "live_gifts"], "territories": ["global"]},
            {"name": "YouTube Thumbnails", "api_endpoint": "https://developers.google.com/youtube/v3", "content_types": ["thumbnails", "channel_art", "community_posts"], "monetization": ["ad_revenue", "memberships"], "territories": ["global"]},
            {"name": "Pinterest Business", "api_endpoint": "https://developers.pinterest.com/docs/api/v5", "content_types": ["pins", "boards", "idea_pins"], "monetization": ["shopping_ads", "promoted_pins"], "territories": ["global"]}
        ],
        "thumbnail_services": [
            {"name": "Thumbnail Creator Pro", "specialties": ["youtube_thumbnails", "podcast_covers", "social_media_graphics"], "price_range": "$25-$150", "territories": ["global"]},
            {"name": "Social Media Graphics Co", "specialties": ["instagram_posts", "story_templates", "tiktok_graphics"], "price_range": "$50-$300", "territories": ["global"]},
            {"name": "Content Creation Studio", "specialties": ["brand_graphics", "promotional_content", "social_campaigns"], "price_range": "$100-$500", "territories": ["US", "UK"]}
        ]
    },
    
    # Film and Video Production
    "video_production": {
        "music_videos": [
            {"name": "Music Video Network", "specialties": ["music_videos", "lyric_videos", "promotional_videos"], "price_range": "$5000-$50000", "territories": ["US", "UK", "CA"]},
            {"name": "Independent Film Collective", "specialties": ["narrative_videos", "conceptual_videos", "documentary"], "price_range": "$3000-$25000", "territories": ["global"]},
            {"name": "Creative Video Solutions", "specialties": ["commercial_videos", "brand_content", "social_video"], "price_range": "$2000-$15000", "territories": ["US"]}
        ],
        "production_companies": [
            {"name": "Major Production Studios", "specialties": ["feature_films", "documentaries", "series"], "price_range": "$100000+", "territories": ["US", "UK"]},
            {"name": "Independent Production", "specialties": ["indie_films", "short_films", "web_series"], "price_range": "$10000-$100000", "territories": ["global"]},
            {"name": "Commercial Production", "specialties": ["commercials", "corporate_videos", "training_videos"], "price_range": "$5000-$50000", "territories": ["US", "UK", "CA"]}
        ]
    },
    
    # Podcast Industry Integration
    "podcast_platforms": {
        "hosting": [
            {"name": "Spotify for Podcasters", "api_endpoint": "https://api.spotify.com/v1", "monetization": ["ad_revenue", "subscriptions"], "content_types": ["audio", "video"], "territories": ["global"]},
            {"name": "Apple Podcasts", "api_endpoint": "https://podcasts.apple.com/us/genre/podcasts", "monetization": ["subscriptions", "premium_content"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Google Podcasts", "api_endpoint": "https://developers.google.com/search/docs/data-types/podcast", "monetization": ["ad_revenue"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Podscribe", "specialties": ["podcast_advertising", "attribution", "analytics"], "monetization": ["programmatic_ads"], "territories": ["US", "UK"]}
        ],
        "production": [
            {"name": "Podcast Production Network", "specialties": ["full_production", "editing", "sound_design"], "price_range": "$500-$5000", "territories": ["US", "UK"]},
            {"name": "Audio Content Creators", "specialties": ["scripting", "voice_over", "post_production"], "price_range": "$300-$3000", "territories": ["global"]},
            {"name": "Podcast Studio Services", "specialties": ["recording", "mixing", "mastering"], "price_range": "$200-$2000", "territories": ["US", "CA"]}
        ]
    },
    
    # Live Streaming Platforms
    "live_streaming": {
        "major": [
            {"name": "Twitch", "api_endpoint": "https://dev.twitch.tv/docs/api", "monetization": ["subscriptions", "bits", "ads"], "content_types": ["live_video", "music", "gaming"], "territories": ["global"]},
            {"name": "YouTube Live", "api_endpoint": "https://developers.google.com/youtube/v3", "monetization": ["super_chat", "memberships", "ads"], "content_types": ["live_video", "music", "educational"], "territories": ["global"]},
            {"name": "Facebook Live", "api_endpoint": "https://developers.facebook.com/docs/live-video-api", "monetization": ["stars", "fan_subscriptions"], "content_types": ["live_video", "music", "events"], "territories": ["global"]},
            {"name": "Instagram Live", "api_endpoint": "https://developers.facebook.com/docs/instagram-api", "monetization": ["badges", "brand_partnerships"], "content_types": ["live_video", "music"], "territories": ["global"]}
        ],
        "music_focused": [
            {"name": "StageIt", "specialties": ["live_concerts", "intimate_performances"], "monetization": ["ticket_sales", "tips"], "territories": ["US", "UK"]},
            {"name": "Bandsintown PLUS", "specialties": ["virtual_concerts", "livestream_events"], "monetization": ["ticket_sales", "merchandise"], "territories": ["global"]},
            {"name": "Veeps", "specialties": ["premium_livestreams", "exclusive_content"], "monetization": ["ticket_sales", "VIP_packages"], "territories": ["global"]}
        ]
    },
    
    # Gaming and Esports Industry
    "gaming_esports": {
        "platforms": [
            {"name": "Steam", "api_endpoint": "https://steamcommunity.com/dev", "content_types": ["game_soundtracks", "audio_content"], "monetization": ["sales", "dlc"], "territories": ["global"]},
            {"name": "Epic Games Store", "specialties": ["game_audio", "soundtrack_distribution"], "monetization": ["revenue_share"], "territories": ["global"]},
            {"name": "Riot Games", "specialties": ["esports_music", "game_soundtracks"], "monetization": ["licensing", "partnerships"], "territories": ["global"]},
            {"name": "Blizzard Entertainment", "specialties": ["game_music", "cinematic_audio"], "monetization": ["licensing"], "territories": ["global"]}
        ],
        "esports_organizations": [
            {"name": "Team Liquid", "specialties": ["team_anthems", "event_music"], "monetization": ["sponsorships", "licensing"], "territories": ["global"]},
            {"name": "Cloud9", "specialties": ["brand_music", "streaming_content"], "monetization": ["partnerships"], "territories": ["US"]},
            {"name": "FaZe Clan", "specialties": ["content_creation", "music_collaborations"], "monetization": ["brand_deals", "merchandise"], "territories": ["global"]}
        ]
    },
    
    # Fashion Photography
    "fashion_photography": {
        "music_fashion": [
            {"name": "Music Style Photography", "specialties": ["artist_styling", "album_fashion", "stage_outfits"], "price_range": "$1000-$10000", "territories": ["US", "UK"]},
            {"name": "Concert Fashion Studios", "specialties": ["performance_wear", "red_carpet", "editorial"], "price_range": "$1500-$8000", "territories": ["global"]},
            {"name": "Artist Brand Photography", "specialties": ["brand_partnerships", "fashion_campaigns"], "price_range": "$2000-$15000", "territories": ["US", "UK", "EU"]}
        ],
        "commercial": [
            {"name": "Brand Photography Network", "specialties": ["merchandise_photography", "product_shoots"], "price_range": "$500-$5000", "territories": ["global"]},
            {"name": "E-commerce Photo Services", "specialties": ["online_store_photos", "lifestyle_photography"], "price_range": "$300-$3000", "territories": ["US", "UK"]},
            {"name": "Fashion Commerce Studios", "specialties": ["lookbook_photography", "catalog_shoots"], "price_range": "$800-$6000", "territories": ["global"]}
        ]
    },
    
    # Existing categories (abbreviated for space)
    "record_labels": {
        "major": [
            {"name": "Universal Music Group", "api_endpoint": None, "supported_formats": ["mp3", "flac", "vinyl"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Sony Music Entertainment", "api_endpoint": None, "supported_formats": ["mp3", "flac", "vinyl"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Warner Music Group", "api_endpoint": None, "supported_formats": ["mp3", "flac", "vinyl"], "content_types": ["audio"], "territories": ["global"]}
        ]
    }
}

# Big Mann Entertainment Industry Identifiers (IPI, ISNI, AARC)
BIG_MANN_INDUSTRY_IDENTIFIERS = [
    {
        "entity_name": "Big Mann Entertainment",
        "entity_type": "company",
        
        # IPI Information
        "ipi_number": "813048171",
        "ipi_role": "publisher",
        
        # ISNI Information (not applicable for companies typically)
        "isni_number": None,
        "isni_status": None,
        
        # AARC Information  
        "aarc_number": "RC00002057",
        "aarc_type": "record_company",
        
        "territory": "US",
        "status": "active",
        "contact_info": {
            "address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
            "phone": "334-669-8638",
            "email": "info@bigmannentertainment.com"
        },
        "metadata": {
            "registered_date": "2024-01-01",
            "business_type": "Sound Recording Industries",
            "naics_code": "512200"
        }
    },
    {
        "entity_name": "John LeGerron Spivey",
        "entity_type": "individual",
        
        # IPI Information
        "ipi_number": "578413032",
        "ipi_role": "songwriter",
        
        # ISNI Information
        "isni_number": "0000000491551894",
        "isni_status": "active",
        
        # AARC Information
        "aarc_number": "FA02933539", 
        "aarc_type": "featured_artist",
        
        "territory": "US",
        "status": "active",
        "contact_info": {
            "address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
            "phone": "334-669-8638"
        },
        "metadata": {
            "registered_date": "2024-01-01",
            "performing_rights_org": "ASCAP",
            "primary_instrument": "vocals"
        }
    }
]