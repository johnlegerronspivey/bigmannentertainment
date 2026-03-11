"""
AWS Macie Integration - Pydantic Models
Automated sensitive data discovery and PII detection
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class FindingCategory(str, Enum):
    CLASSIFICATION = "CLASSIFICATION"
    POLICY = "POLICY"


class JobStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    COMPLETE = "COMPLETE"
    IDLE = "IDLE"
    USER_PAUSED = "USER_PAUSED"


class JobType(str, Enum):
    ONE_TIME = "ONE_TIME"
    SCHEDULED = "SCHEDULED"


class PIIType(str, Enum):
    """Common PII types detected by Macie"""
    SSN = "USA_SOCIAL_SECURITY_NUMBER"
    CREDIT_CARD = "CREDIT_CARD_NUMBER"
    EMAIL = "EMAIL_ADDRESS"
    PHONE = "PHONE_NUMBER"
    PASSPORT = "USA_PASSPORT_NUMBER"
    DRIVERS_LICENSE = "USA_DRIVERS_LICENSE"
    BANK_ACCOUNT = "BANK_ACCOUNT_NUMBER"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    MEDICAL_RECORD = "USA_HEALTH_INSURANCE_CLAIM_NUMBER"
    IP_ADDRESS = "IP_ADDRESS"
    NAME = "NAME"
    ADDRESS = "ADDRESS"


# Custom Data Identifier Models
class CustomDataIdentifier(BaseModel):
    """Custom data identifier for detecting proprietary sensitive data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    regex: str
    keywords: List[str] = []
    ignore_words: List[str] = []
    maximum_match_distance: int = 50
    severity_levels: Optional[List[Dict[str, Any]]] = None
    arn: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class CreateCustomIdentifierRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    regex: str = Field(..., min_length=1, max_length=512)
    keywords: List[str] = []
    ignore_words: List[str] = []
    maximum_match_distance: int = Field(default=50, ge=0, le=300)


# Classification Job Models
class BucketDefinition(BaseModel):
    """S3 bucket definition for classification job"""
    account_id: str
    bucket_name: str
    prefix: Optional[str] = None


class ClassificationJob(BaseModel):
    """Classification job for sensitive data discovery"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: Optional[str] = None  # AWS job ID
    job_arn: Optional[str] = None
    name: str
    description: Optional[str] = None
    job_type: JobType = JobType.ONE_TIME
    status: JobStatus = JobStatus.IDLE
    
    # Target buckets
    buckets: List[str] = []
    
    # Detection settings
    managed_data_identifier_selector: str = "RECOMMENDED"  # ALL, EXCLUDE, INCLUDE, NONE, RECOMMENDED
    custom_data_identifier_ids: List[str] = []
    sampling_percentage: int = 100
    
    # Statistics
    objects_scanned: int = 0
    objects_matched: int = 0
    findings_count: int = 0
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None


class CreateClassificationJobRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=200)
    bucket_names: List[str] = Field(..., min_length=1)
    job_type: JobType = JobType.ONE_TIME
    managed_data_identifier_selector: str = "RECOMMENDED"
    custom_data_identifier_ids: List[str] = []
    sampling_percentage: int = Field(default=100, ge=1, le=100)


# Finding Models
class SensitiveDataOccurrence(BaseModel):
    """Individual occurrence of sensitive data"""
    type: str  # PII type
    count: int
    locations: List[Dict[str, Any]] = []


class AffectedResource(BaseModel):
    """Resource affected by sensitive data finding"""
    bucket_name: str
    object_key: str
    object_size: Optional[int] = None
    object_last_modified: Optional[datetime] = None
    public_access: bool = False


class Finding(BaseModel):
    """Sensitive data finding"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    finding_id: Optional[str] = None  # AWS finding ID
    
    # Classification
    category: FindingCategory = FindingCategory.CLASSIFICATION
    type: str  # e.g., "SensitiveData:S3Object/Personal"
    severity: SeverityLevel = SeverityLevel.MEDIUM
    severity_score: int = 0  # 0-100
    
    # Affected resource
    resource: Optional[AffectedResource] = None
    
    # Sensitive data details
    sensitive_data_types: List[str] = []
    sensitive_data_occurrences: List[SensitiveDataOccurrence] = []
    total_detections: int = 0
    
    # Job association
    job_id: Optional[str] = None
    
    # Status
    is_archived: bool = False
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Dashboard & Statistics Models
class FindingStatistics(BaseModel):
    """Aggregated finding statistics"""
    total_findings: int = 0
    findings_by_severity: Dict[str, int] = {}
    findings_by_type: Dict[str, int] = {}
    findings_by_bucket: Dict[str, int] = {}
    unacknowledged_count: int = 0
    high_severity_count: int = 0


class JobStatistics(BaseModel):
    """Aggregated job statistics"""
    total_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_objects_scanned: int = 0
    total_objects_matched: int = 0


class MacieDashboardStats(BaseModel):
    """Complete dashboard statistics"""
    # Job stats
    total_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    paused_jobs: int = 0
    
    # Finding stats
    total_findings: int = 0
    high_severity_findings: int = 0
    medium_severity_findings: int = 0
    low_severity_findings: int = 0
    unacknowledged_findings: int = 0
    
    # Custom identifier stats
    total_custom_identifiers: int = 0
    active_custom_identifiers: int = 0
    
    # Bucket stats
    monitored_buckets: int = 0
    buckets_with_findings: int = 0
    
    # Detection stats
    pii_types_detected: List[str] = []
    total_objects_scanned: int = 0
    total_sensitive_objects: int = 0
    
    # Recent activity
    last_scan_time: Optional[datetime] = None
    findings_last_24h: int = 0
    findings_last_7d: int = 0


# Alert & Notification Models
class AlertRule(BaseModel):
    """Alert rule for findings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    
    # Conditions
    severity_threshold: SeverityLevel = SeverityLevel.HIGH
    pii_types: List[str] = []  # Empty = all types
    bucket_names: List[str] = []  # Empty = all buckets
    
    # Actions
    notify_email: bool = True
    notify_slack: bool = False
    auto_archive: bool = False
    
    # Status
    is_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreateAlertRuleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    severity_threshold: SeverityLevel = SeverityLevel.HIGH
    pii_types: List[str] = []
    bucket_names: List[str] = []
    notify_email: bool = True


# Scan Configuration Models
class ScanSchedule(BaseModel):
    """Scheduled scan configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    
    # Schedule
    cron_expression: str  # e.g., "0 0 * * 0" for weekly
    timezone: str = "UTC"
    
    # Target
    bucket_names: List[str] = []
    custom_data_identifier_ids: List[str] = []
    
    # Settings
    sampling_percentage: int = 100
    managed_data_identifier_selector: str = "RECOMMENDED"
    
    # Status
    is_enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# S3 Bucket Models
class S3BucketInfo(BaseModel):
    """S3 bucket information for Macie scanning"""
    name: str
    region: str = "us-east-1"
    account_id: str
    
    # Access
    public_access_blocked: bool = True
    versioning_enabled: bool = False
    encryption_type: Optional[str] = None
    
    # Stats
    object_count: int = 0
    total_size_bytes: int = 0
    
    # Macie status
    is_monitored: bool = False
    last_scanned: Optional[datetime] = None
    findings_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# API Response Models
class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[Any] = []
    total: int = 0
    limit: int = 50
    offset: int = 0
    has_more: bool = False


class MacieHealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "AWS Macie PII Detection"
    version: str = "1.0.0"
    macie_enabled: bool = False
    aws_region: str = "us-east-1"
    features: List[str] = []



# --- SNS/EventBridge Notification Models ---

class NotificationChannel(str, Enum):
    SNS = "SNS"
    EVENTBRIDGE = "EVENTBRIDGE"
    EMAIL = "EMAIL"
    SLACK = "SLACK"

class NotificationStatus(str, Enum):
    SENT = "SENT"
    FAILED = "FAILED"
    PENDING = "PENDING"

class NotificationRule(BaseModel):
    """Notification rule for Macie findings via SNS/EventBridge"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    channel: NotificationChannel = NotificationChannel.SNS
    is_enabled: bool = True
    
    # Filters
    min_severity: SeverityLevel = SeverityLevel.HIGH
    pii_types: List[str] = []
    bucket_names: List[str] = []
    
    # Channel config
    sns_topic_arn: Optional[str] = None
    eventbridge_bus_name: Optional[str] = None
    email_recipients: List[str] = []
    slack_webhook_url: Optional[str] = None
    
    # Stats
    notifications_sent: int = 0
    last_triggered: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CreateNotificationRuleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    channel: NotificationChannel = NotificationChannel.SNS
    min_severity: SeverityLevel = SeverityLevel.HIGH
    pii_types: List[str] = []
    bucket_names: List[str] = []
    sns_topic_arn: Optional[str] = None
    eventbridge_bus_name: Optional[str] = None
    email_recipients: List[str] = []

class NotificationLog(BaseModel):
    """Log entry for a sent notification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    rule_name: str
    channel: NotificationChannel
    status: NotificationStatus = NotificationStatus.SENT
    
    # What triggered it
    finding_id: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    pii_type: Optional[str] = None
    bucket_name: Optional[str] = None
    message: str = ""
    
    # Response
    message_id: Optional[str] = None
    error: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
