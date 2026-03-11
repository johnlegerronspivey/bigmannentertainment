"""
Enhanced Features Models for BME Platform
- AI-Powered Release Optimization
- Social Platform Native Distribution
- Smart Royalty Routing & Splits
- Metadata & Cover Art Automation
- Global Market Support
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============== AI-Powered Release Optimization Models ==============

class ReleaseOptimizationRequest(BaseModel):
    """Request for AI-powered release optimization analysis"""
    release_id: str
    artist_name: str
    track_title: str
    genre: str
    release_date: Optional[datetime] = None
    target_audience: Optional[str] = None
    budget: Optional[float] = None
    previous_performance: Optional[Dict[str, Any]] = None

class PlatformRecommendation(BaseModel):
    """AI recommendation for a specific platform"""
    platform_name: str
    platform_type: str  # streaming, social_media, radio, etc.
    priority: str  # high, medium, low
    estimated_reach: int
    estimated_engagement_rate: float
    reasoning: str
    optimal_timing: Optional[str] = None

class ReleaseOptimization(BaseModel):
    """AI-generated release optimization analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str
    artist_name: str
    track_title: str
    genre: str
    platform_recommendations: List[PlatformRecommendation]
    optimal_release_strategy: str
    target_markets: List[str]
    estimated_total_reach: int
    confidence_score: float  # 0.0 to 1.0
    ai_insights: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Social Platform Native Distribution Models ==============

class SocialPlatformType(str, Enum):
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    ONLYFANS = "onlyfans"

class SocialDistributionRequest(BaseModel):
    """Request for social platform native distribution"""
    media_id: str
    platforms: List[SocialPlatformType]
    caption: str
    hashtags: List[str] = []
    scheduled_time: Optional[datetime] = None
    auto_optimize_format: bool = True

class SocialDistribution(BaseModel):
    """Social platform native distribution record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    media_id: str
    platform: SocialPlatformType
    status: str  # pending, processing, published, failed
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    caption: str
    hashtags: List[str] = []
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    scheduled_time: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Smart Royalty Routing & Splits Models ==============

class SplitType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

class RoyaltySplit(BaseModel):
    """Individual royalty split configuration"""
    collaborator_id: str
    collaborator_name: str
    split_type: SplitType
    value: float  # percentage (0-100) or fixed amount
    notes: Optional[str] = None

class RoyaltyRouting(BaseModel):
    """Smart royalty routing configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str
    track_title: str
    total_splits: int
    splits: List[RoyaltySplit]
    auto_reconciliation: bool = True
    reconciliation_frequency: str = "daily"  # daily, weekly, monthly
    total_percentage: float = 100.0
    status: str = "active"  # active, paused, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RoyaltyTransaction(BaseModel):
    """Individual royalty transaction record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    routing_id: str
    platform: str
    revenue_amount: float
    currency: str = "USD"
    collaborator_payments: List[Dict[str, Any]]  # {collaborator_id, amount, status}
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    reconciliation_status: str = "pending"  # pending, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Metadata & Cover Art Automation Models ==============

class MetadataAutoFillRequest(BaseModel):
    """Request for automated metadata generation"""
    audio_file_path: Optional[str] = None
    track_title: Optional[str] = None
    artist_name: Optional[str] = None
    genre: Optional[str] = None
    ai_enhance: bool = True

class CoverArtGenerationRequest(BaseModel):
    """Request for AI-generated cover art"""
    track_title: str
    artist_name: str
    genre: str
    mood: Optional[str] = None
    color_preference: Optional[str] = None
    style: Optional[str] = None  # abstract, realistic, minimalist, etc.

class AutomatedMetadata(BaseModel):
    """Automated metadata generation result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    track_id: str
    title: str
    artist: str
    album: Optional[str] = None
    genre: str
    release_year: Optional[int] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    mood: Optional[str] = None
    language: Optional[str] = None
    lyrics_summary: Optional[str] = None
    ai_generated_tags: List[str] = []
    cover_art_url: Optional[str] = None
    cover_art_base64: Optional[str] = None
    validation_status: str = "pending"  # pending, approved, rejected
    platforms_accepted: List[str] = []
    platforms_rejected: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Global Market Support Models ==============

class GlobalMarket(str, Enum):
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    CHINA = "china"
    INDIA = "india"
    AFRICA = "africa"
    LATIN_AMERICA = "latin_america"
    MIDDLE_EAST = "middle_east"
    SOUTHEAST_ASIA = "southeast_asia"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CNY = "CNY"  # Chinese Yuan
    INR = "INR"  # Indian Rupee
    ZAR = "ZAR"  # South African Rand
    BRL = "BRL"  # Brazilian Real
    AED = "AED"  # UAE Dirham

class GlobalMarketConfig(BaseModel):
    """Configuration for global market support"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str
    enabled_markets: List[GlobalMarket]
    primary_currency: Currency
    supported_currencies: List[Currency]
    region_specific_platforms: Dict[str, List[str]]  # {market: [platform_names]}
    localized_metadata: Dict[str, Dict[str, str]]  # {market: {field: value}}
    pricing_by_region: Dict[str, float]  # {market: price}
    distribution_rights: Dict[str, bool]  # {market: has_rights}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MarketPerformance(BaseModel):
    """Performance tracking for global markets"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str
    market: GlobalMarket
    total_streams: int = 0
    total_revenue: float = 0.0
    currency: Currency
    top_platforms: List[Dict[str, Any]] = []  # {platform, streams, revenue}
    growth_rate: float = 0.0
    market_penetration: float = 0.0  # percentage
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Dashboard & Analytics Models ==============

class EnhancedFeaturesDashboard(BaseModel):
    """Consolidated dashboard data for all enhanced features"""
    user_id: str
    ai_optimization_count: int = 0
    social_distributions_count: int = 0
    active_royalty_routings: int = 0
    automated_metadata_count: int = 0
    enabled_global_markets: int = 0
    total_ai_insights_generated: int = 0
    total_cover_arts_generated: int = 0
    total_social_reach: int = 0
    total_royalty_transactions: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
