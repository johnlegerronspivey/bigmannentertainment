"""
Agency Success Automation Models
Pydantic models for automated talent onboarding, KPI tracking, contracts, and revenue forecasting
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


# =========================
# Enums
# =========================

class OnboardingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class OnboardingStepType(str, Enum):
    DOCUMENT_UPLOAD = "document_upload"
    FORM_SUBMISSION = "form_submission"
    VERIFICATION = "verification"
    APPROVAL = "approval"
    TRAINING = "training"
    CONTRACT_SIGNING = "contract_signing"
    PHOTO_SUBMISSION = "photo_submission"
    MEASUREMENT_ENTRY = "measurement_entry"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    COMPLETED = "completed"


class ContractType(str, Enum):
    EXCLUSIVE_REPRESENTATION = "exclusive_representation"
    NON_EXCLUSIVE = "non_exclusive"
    BOOKING_AGREEMENT = "booking_agreement"
    RELEASE_FORM = "release_form"
    NDA = "nda"
    LICENSING_AGREEMENT = "licensing_agreement"
    COLLABORATION = "collaboration"


class BookingStatus(str, Enum):
    INQUIRY = "inquiry"
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class BookingType(str, Enum):
    PHOTOSHOOT = "photoshoot"
    RUNWAY = "runway"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    FITTING = "fitting"
    CASTING = "casting"
    EVENT = "event"
    VIDEO = "video"


class KPICategory(str, Enum):
    REVENUE = "revenue"
    BOOKINGS = "bookings"
    TALENT = "talent"
    CLIENT = "client"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =========================
# Onboarding Models
# =========================

class OnboardingStep(BaseModel):
    """Individual step in onboarding workflow"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int
    step_type: OnboardingStepType
    title: str
    description: str
    status: OnboardingStatus = OnboardingStatus.NOT_STARTED
    required: bool = True
    data: Dict[str, Any] = {}
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    notes: Optional[str] = None


class OnboardingWorkflow(BaseModel):
    """Complete onboarding workflow for a talent"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    talent_id: str
    talent_name: str
    talent_email: str
    agency_id: str
    workflow_name: str = "Standard Talent Onboarding"
    status: OnboardingStatus = OnboardingStatus.NOT_STARTED
    steps: List[OnboardingStep] = []
    progress_percentage: float = 0.0
    current_step: int = 1
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OnboardingTemplate(BaseModel):
    """Template for onboarding workflows"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    agency_id: str
    talent_type: str = "model"  # model, photographer, influencer
    steps: List[Dict[str, Any]] = []
    estimated_duration_days: int = 7
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =========================
# Contract Models
# =========================

class ContractParty(BaseModel):
    """Party involved in a contract"""
    party_id: str
    party_type: str  # talent, agency, client, brand
    name: str
    email: str
    role: str  # signer, witness, cc
    signed: bool = False
    signed_at: Optional[datetime] = None
    signature_ip: Optional[str] = None


class ContractClause(BaseModel):
    """Individual clause in a contract"""
    clause_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    section: str
    title: str
    content: str
    is_negotiable: bool = False
    modified: bool = False


class Contract(BaseModel):
    """Contract document"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_number: str = Field(default_factory=lambda: f"CON-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
    contract_type: ContractType
    title: str
    description: Optional[str] = None
    agency_id: str
    status: ContractStatus = ContractStatus.DRAFT
    parties: List[ContractParty] = []
    clauses: List[ContractClause] = []
    terms: Dict[str, Any] = {}  # compensation, duration, exclusivity, etc.
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_value: float = 0.0
    currency: str = "USD"
    auto_renew: bool = False
    renewal_terms: Optional[Dict[str, Any]] = None
    template_id: Optional[str] = None
    document_url: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContractTemplate(BaseModel):
    """Template for generating contracts"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contract_type: ContractType
    agency_id: str
    clauses: List[Dict[str, Any]] = []
    default_terms: Dict[str, Any] = {}
    is_active: bool = True
    version: str = "1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =========================
# Booking Models
# =========================

class Booking(BaseModel):
    """Booking/job record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_number: str = Field(default_factory=lambda: f"BK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}")
    booking_type: BookingType
    status: BookingStatus = BookingStatus.INQUIRY
    agency_id: str
    talent_id: str
    talent_name: str
    client_id: str
    client_name: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    rate: float = 0.0
    rate_type: str = "hourly"  # hourly, daily, flat
    total_fee: float = 0.0
    agency_commission: float = 0.0
    commission_percentage: float = 20.0
    talent_payout: float = 0.0
    expenses: List[Dict[str, Any]] = []
    requirements: List[str] = []
    notes: Optional[str] = None
    contract_id: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =========================
# KPI & Analytics Models
# =========================

class KPIMetric(BaseModel):
    """Individual KPI metric"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: KPICategory
    value: float
    target: float
    unit: str = ""  # $, %, count, etc.
    trend: str = "stable"  # up, down, stable
    trend_percentage: float = 0.0
    period: str = "month"  # day, week, month, quarter, year
    period_start: datetime
    period_end: datetime
    comparison_value: Optional[float] = None  # Previous period value
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TalentPerformance(BaseModel):
    """Performance metrics for a talent"""
    talent_id: str
    talent_name: str
    agency_id: str
    period: str
    period_start: datetime
    period_end: datetime
    
    # Booking metrics
    total_bookings: int = 0
    completed_bookings: int = 0
    cancelled_bookings: int = 0
    booking_completion_rate: float = 0.0
    
    # Revenue metrics
    total_revenue: float = 0.0
    average_booking_value: float = 0.0
    revenue_growth: float = 0.0
    
    # Client metrics
    unique_clients: int = 0
    repeat_clients: int = 0
    client_satisfaction_score: float = 0.0
    
    # Engagement metrics
    profile_views: int = 0
    inquiries_received: int = 0
    conversion_rate: float = 0.0
    
    # Rating
    performance_score: float = 0.0  # 0-100
    rank_in_agency: int = 0
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgencyKPIDashboard(BaseModel):
    """Agency-wide KPI dashboard"""
    agency_id: str
    period: str
    period_start: datetime
    period_end: datetime
    
    # Revenue KPIs
    total_revenue: float = 0.0
    revenue_target: float = 0.0
    revenue_achievement: float = 0.0
    gross_margin: float = 0.0
    
    # Booking KPIs
    total_bookings: int = 0
    booking_target: int = 0
    average_booking_value: float = 0.0
    booking_conversion_rate: float = 0.0
    
    # Talent KPIs
    active_talent: int = 0
    new_talent_this_period: int = 0
    talent_utilization_rate: float = 0.0
    average_talent_revenue: float = 0.0
    
    # Client KPIs
    active_clients: int = 0
    new_clients_this_period: int = 0
    client_retention_rate: float = 0.0
    average_client_spend: float = 0.0
    
    # Growth KPIs
    revenue_growth_yoy: float = 0.0
    booking_growth_yoy: float = 0.0
    talent_growth_yoy: float = 0.0
    
    # Top performers
    top_talents: List[Dict[str, Any]] = []
    top_clients: List[Dict[str, Any]] = []
    
    metrics: List[KPIMetric] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =========================
# Revenue Forecasting Models
# =========================

class RevenueForecast(BaseModel):
    """Revenue forecast for a period"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    forecast_period: str  # monthly, quarterly, yearly
    period_start: datetime
    period_end: datetime
    
    # Forecast values
    predicted_revenue: float
    confidence_level: float  # 0-1
    lower_bound: float
    upper_bound: float
    
    # Breakdown
    by_booking_type: Dict[str, float] = {}
    by_client_segment: Dict[str, float] = {}
    by_talent_tier: Dict[str, float] = {}
    
    # Factors
    seasonal_factor: float = 1.0
    growth_factor: float = 1.0
    market_factor: float = 1.0
    
    # Assumptions
    assumptions: List[str] = []
    risks: List[str] = []
    opportunities: List[str] = []
    
    # Model info
    model_type: str = "statistical"  # statistical, ml, hybrid
    model_accuracy: float = 0.0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ForecastScenario(BaseModel):
    """Scenario for revenue forecasting"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    scenario_type: str  # optimistic, realistic, pessimistic, custom
    agency_id: str
    base_forecast_id: str
    
    # Adjustments
    revenue_multiplier: float = 1.0
    booking_multiplier: float = 1.0
    new_talent_impact: float = 0.0
    market_event_impact: float = 0.0
    
    # Calculated values
    adjusted_revenue: float = 0.0
    variance_from_base: float = 0.0
    
    description: str = ""
    assumptions: List[str] = []
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =========================
# Automation & Alerts
# =========================

class AutomationRule(BaseModel):
    """Automation rule for workflows"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agency_id: str
    trigger_type: str  # event, schedule, condition
    trigger_config: Dict[str, Any] = {}
    action_type: str  # notification, status_update, assignment, reminder
    action_config: Dict[str, Any] = {}
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowAlert(BaseModel):
    """Alert for workflow events"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    alert_type: str  # onboarding_overdue, contract_expiring, booking_reminder, kpi_alert
    severity: AlertSeverity
    title: str
    message: str
    related_entity_type: str  # onboarding, contract, booking, talent
    related_entity_id: str
    is_read: bool = False
    is_dismissed: bool = False
    action_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None


# =========================
# Response Models
# =========================

class OnboardingStats(BaseModel):
    """Statistics for onboarding workflows"""
    total_workflows: int = 0
    in_progress: int = 0
    pending_review: int = 0
    completed_this_month: int = 0
    average_completion_days: float = 0.0
    overdue_count: int = 0


class ContractStats(BaseModel):
    """Statistics for contracts"""
    total_contracts: int = 0
    active_contracts: int = 0
    pending_signature: int = 0
    expiring_soon: int = 0
    total_contract_value: float = 0.0


class BookingStats(BaseModel):
    """Statistics for bookings"""
    total_bookings: int = 0
    confirmed_bookings: int = 0
    pending_bookings: int = 0
    completed_this_month: int = 0
    total_revenue_this_month: float = 0.0
    average_booking_value: float = 0.0


class AutomationDashboard(BaseModel):
    """Dashboard summary for agency success automation"""
    agency_id: str
    onboarding_stats: OnboardingStats
    contract_stats: ContractStats
    booking_stats: BookingStats
    recent_alerts: List[WorkflowAlert] = []
    upcoming_deadlines: List[Dict[str, Any]] = []
    kpi_summary: Optional[AgencyKPIDashboard] = None
    revenue_forecast: Optional[RevenueForecast] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
