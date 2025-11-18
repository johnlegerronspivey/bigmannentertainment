"""
AWS Organizations Models - Using new State field (Sept 2025 update)
Replaces deprecated Status field with granular State tracking
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AccountState(str, Enum):
    """AWS Organizations Account States (new field as of Sept 2025)"""
    PENDING_ACTIVATION = "PENDING_ACTIVATION"  # Account created but not yet activated
    ACTIVE = "ACTIVE"  # Account is operational and ready
    SUSPENDED = "SUSPENDED"  # Account under AWS-enforced suspension
    PENDING_CLOSURE = "PENDING_CLOSURE"  # Account closure in progress
    CLOSED = "CLOSED"  # Account in 90-day reinstatement window


class AccountStateSeverity(str, Enum):
    """Severity levels for account states"""
    NORMAL = "normal"  # ACTIVE, PENDING_ACTIVATION
    WARNING = "warning"  # PENDING_CLOSURE
    CRITICAL = "critical"  # SUSPENDED, CLOSED


class AWSOrganizationAccount(BaseModel):
    """AWS Organization Account with new State field"""
    id: str = Field(..., description="AWS Account ID")
    arn: str = Field(..., description="Account ARN")
    email: str = Field(..., description="Account email")
    name: str = Field(..., description="Account name")
    state: AccountState = Field(..., description="Account lifecycle state (new field)")
    joined_method: Optional[str] = Field(None, description="How account joined (INVITED or CREATED)")
    joined_timestamp: Optional[datetime] = Field(None, description="When account joined")
    
    # Additional metadata
    organization_id: Optional[str] = None
    parent_ou_id: Optional[str] = None
    parent_ou_name: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class AccountStateChange(BaseModel):
    """Track account state changes over time"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    account_id: str
    account_name: str
    account_email: str
    previous_state: Optional[AccountState] = None
    new_state: AccountState
    detected_at: datetime = Field(default_factory=lambda: datetime.now(__import__('datetime').timezone.utc))
    severity: AccountStateSeverity
    
    class Config:
        use_enum_values = True


class AccountStateAlert(BaseModel):
    """Alert configuration for account state monitoring"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    alert_name: str
    monitored_states: List[AccountState] = Field(
        default=[AccountState.SUSPENDED, AccountState.PENDING_CLOSURE, AccountState.CLOSED]
    )
    notification_email: Optional[str] = None
    notification_sns_topic: Optional[str] = None
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(__import__('datetime').timezone.utc))
    last_triggered: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class OrganizationSummary(BaseModel):
    """Summary of organization account states"""
    organization_id: str
    total_accounts: int
    accounts_by_state: Dict[str, int]  # State -> count
    critical_accounts: int  # SUSPENDED or CLOSED
    warning_accounts: int  # PENDING_CLOSURE
    active_accounts: int  # ACTIVE
    pending_activation: int  # PENDING_ACTIVATION
    last_updated: datetime = Field(default_factory=lambda: datetime.now(__import__('datetime').timezone.utc))


class StateMonitoringConfig(BaseModel):
    """Configuration for state monitoring"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    polling_interval_minutes: int = Field(default=15, ge=5, le=1440)
    alert_on_state_change: bool = True
    track_state_history: bool = True
    retention_days: int = Field(default=90, ge=7, le=365)
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(__import__('datetime').timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(__import__('datetime').timezone.utc))


class AccountStateHistoryQuery(BaseModel):
    """Query parameters for account state history"""
    account_id: Optional[str] = None
    state: Optional[AccountState] = None
    severity: Optional[AccountStateSeverity] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    
    class Config:
        use_enum_values = True
