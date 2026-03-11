from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid

class SponsorshipStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BonusType(str, Enum):
    FIXED = "fixed"  # Fixed amount
    PERFORMANCE = "performance"  # Based on metrics
    MILESTONE = "milestone"  # Triggered by reaching goals
    REVENUE_SHARE = "revenue_share"  # Percentage of revenue
    TIERED = "tiered"  # Multiple tiers with different rates

class MetricType(str, Enum):
    VIEWS = "views"
    DOWNLOADS = "downloads"
    STREAMS = "streams"
    ENGAGEMENT = "engagement"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"

class PayoutStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"

# Sponsor Profile
class Sponsor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    brand_name: Optional[str] = None
    contact_person: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Business details
    industry: str
    company_size: Optional[str] = None  # startup, small, medium, large, enterprise
    annual_budget: Optional[float] = None
    
    # Address and legal
    address: Optional[Dict[str, str]] = None
    tax_id: Optional[str] = None
    business_registration: Optional[str] = None
    
    # Brand assets
    logo_url: Optional[str] = None
    brand_colors: List[str] = []
    brand_guidelines_url: Optional[str] = None
    
    # Preferences
    target_audience: List[str] = []
    preferred_content_types: List[str] = []  # music, video, podcast
    preferred_genres: List[str] = []
    
    # Status and metadata
    is_active: bool = True
    tier: str = "bronze"  # bronze, silver, gold, platinum
    total_spent: float = 0.0
    lifetime_value: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Bonus Calculation Rules
class BonusRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    bonus_type: BonusType
    
    # Rule configuration
    base_amount: Optional[float] = None  # Fixed amount or base for calculations
    rate: Optional[float] = None  # Rate for performance-based bonuses
    percentage: Optional[float] = None  # Percentage for revenue sharing
    
    # Metric-based rules
    metric_type: Optional[MetricType] = None
    threshold: Optional[float] = None  # Minimum to trigger bonus
    cap: Optional[float] = None  # Maximum bonus amount
    
    # Tiered structure (for tiered bonuses)
    tiers: List[Dict[str, Any]] = []  # [{"min": 1000, "max": 5000, "rate": 0.05}]
    
    # Milestone configuration
    milestones: List[Dict[str, Any]] = []  # [{"target": 10000, "bonus": 500}]
    
    # Conditions
    minimum_performance: Optional[float] = None
    cooldown_period: Optional[int] = None  # Days between bonus calculations
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Sponsorship Deal/Contract
class SponsorshipDeal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deal_name: str
    sponsor_id: str
    content_creator_id: str  # User who owns the content
    
    # Deal details
    deal_type: str  # content_sponsorship, banner_ads, platform_sponsorship, etc.
    description: str
    requirements: List[str] = []  # What sponsor expects
    deliverables: List[str] = []  # What creator will deliver
    
    # Financial terms
    base_fee: float = 0.0  # Guaranteed payment
    bonus_rules: List[BonusRule] = []
    currency: str = "USD"
    payment_schedule: str = "monthly"  # daily, weekly, monthly, quarterly, milestone
    
    # Content specifications
    content_ids: List[str] = []  # Specific content items sponsored
    content_types: List[str] = []  # Types of content to sponsor
    brand_integration_level: str = "light"  # light, moderate, heavy
    
    # Targeting and placement
    target_platforms: List[str] = []
    target_demographics: Dict[str, Any] = {}
    placement_requirements: Dict[str, Any] = {}
    
    # Timeline
    start_date: date
    end_date: date
    auto_renewal: bool = False
    renewal_terms: Optional[Dict[str, Any]] = None
    
    # Performance tracking
    kpi_targets: Dict[str, float] = {}  # Key performance indicators
    reporting_frequency: str = "weekly"  # daily, weekly, monthly
    
    # Status and approvals
    status: SponsorshipStatus = SponsorshipStatus.DRAFT
    creator_approved: bool = False
    sponsor_approved: bool = False
    admin_approved: bool = False
    
    # Contract details
    contract_url: Optional[str] = None
    terms_accepted_at: Optional[datetime] = None
    signed_by_creator: Optional[str] = None
    signed_by_sponsor: Optional[str] = None
    
    # Metadata
    created_by: str
    notes: Optional[str] = None
    tags: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Performance Metrics Tracking
class PerformanceMetric(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str
    content_id: Optional[str] = None  # Specific content item
    
    # Metric data
    metric_type: MetricType
    metric_value: float
    previous_value: float = 0.0
    change_amount: float = 0.0
    change_percentage: float = 0.0
    
    # Attribution
    platform: Optional[str] = None
    source: Optional[str] = None  # organic, sponsored, viral, etc.
    campaign_id: Optional[str] = None
    
    # Timing
    measurement_date: date = Field(default_factory=date.today)
    measurement_period: str = "daily"  # hourly, daily, weekly, monthly
    
    # Additional context
    audience_demographics: Dict[str, Any] = {}
    engagement_breakdown: Dict[str, Any] = {}
    conversion_data: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Bonus Calculation and Tracking
class BonusCalculation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str
    rule_id: str
    
    # Calculation period
    calculation_date: date = Field(default_factory=date.today)
    period_start: date
    period_end: date
    
    # Metrics used in calculation
    base_metrics: Dict[str, float] = {}  # Raw performance data
    qualifying_metrics: Dict[str, float] = {}  # Metrics that meet thresholds
    
    # Bonus calculation
    base_amount: float = 0.0
    performance_multiplier: float = 1.0
    bonus_amount: float = 0.0
    total_amount: float = 0.0
    
    # Calculation details
    calculation_method: str
    applied_rules: List[Dict[str, Any]] = []
    threshold_met: bool = True
    cap_applied: bool = False
    
    # Status
    is_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Payout Management
class SponsorshipPayout(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str
    recipient_id: str  # Content creator
    sponsor_id: str
    
    # Payout details
    payout_type: str = "bonus"  # base_fee, bonus, milestone, penalty
    amount: float
    currency: str = "USD"
    
    # Related calculations
    calculation_ids: List[str] = []  # Bonus calculations included
    period_start: date
    period_end: date
    
    # Payment processing
    payment_method: str = "bank_transfer"  # bank_transfer, paypal, stripe, check
    payment_details: Dict[str, str] = {}
    processing_fee: float = 0.0
    net_amount: float = 0.0
    
    # Status tracking
    status: PayoutStatus = PayoutStatus.PENDING
    initiated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    # Transaction details
    transaction_id: Optional[str] = None
    payment_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    
    # Reconciliation
    sponsor_invoice_id: Optional[str] = None
    creator_invoice_id: Optional[str] = None
    tax_withholding: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Campaign Performance Summary
class CampaignSummary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str
    summary_period: str = "monthly"  # daily, weekly, monthly, quarterly, yearly
    
    # Performance summary
    total_views: float = 0.0
    total_downloads: float = 0.0
    total_streams: float = 0.0
    total_engagement: float = 0.0
    total_clicks: float = 0.0
    total_conversions: float = 0.0
    total_revenue: float = 0.0
    
    # Calculated metrics
    cpm: float = 0.0  # Cost per thousand impressions
    cpc: float = 0.0  # Cost per click
    cpa: float = 0.0  # Cost per acquisition
    roi: float = 0.0  # Return on investment
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Financial summary
    total_spend: float = 0.0
    base_fees: float = 0.0
    bonus_payments: float = 0.0
    average_bonus_per_period: float = 0.0
    
    # Performance vs targets
    target_achievement: Dict[str, float] = {}  # percentage of each KPI target achieved
    performance_grade: str = "B"  # A, B, C, D, F
    
    # Top performing content
    top_content: List[Dict[str, Any]] = []
    top_platforms: List[Dict[str, Any]] = []
    
    # Summary period
    period_start: date
    period_end: date
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Sponsor Relationship Management
class SponsorInteraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sponsor_id: str
    interaction_type: str  # meeting, email, call, proposal, contract, payment
    
    # Interaction details
    subject: str
    description: str
    participants: List[str] = []  # User IDs involved
    
    # Follow-up and outcomes
    outcome: Optional[str] = None
    next_steps: List[str] = []
    follow_up_date: Optional[date] = None
    
    # Attachments and links
    attachments: List[str] = []
    related_deals: List[str] = []
    
    # Status and priority
    priority: str = "medium"  # low, medium, high, urgent
    is_completed: bool = False
    
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)