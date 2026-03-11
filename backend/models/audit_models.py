"""
Audit Trail & Logging Models
Handles immutable logging, audit trails, and metadata snapshots for compliance
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import uuid
import hashlib
import json

class AuditEventType(str, Enum):
    """Types of audit events"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    RIGHTS_CHECK = "rights_check"
    METADATA_UPDATE = "metadata_update"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    COMPLIANCE_CHECK = "compliance_check"
    CONTRACT_TRIGGER = "contract_trigger"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    DATA_DELETION = "data_deletion"

class AuditSeverity(str, Enum):
    """Severity levels for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditOutcome(str, Enum):
    """Outcome of audited operations"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELLED = "cancelled"

class ImmutableAuditLog(BaseModel):
    """Immutable audit log entry with cryptographic integrity"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Event Information
    event_type: AuditEventType
    event_name: str
    event_description: str
    severity: AuditSeverity = AuditSeverity.INFO
    outcome: AuditOutcome = AuditOutcome.SUCCESS
    
    # User Context
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Resource Context
    resource_type: Optional[str] = None  # content, user, contract, etc.
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    
    # Content Context (for media files)
    content_id: Optional[str] = None
    isrc: Optional[str] = None
    upc: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    
    # Event Data
    event_data: Dict[str, Any] = {}
    metadata_before: Optional[Dict[str, Any]] = None
    metadata_after: Optional[Dict[str, Any]] = None
    
    # System Context
    platform_version: Optional[str] = None
    api_endpoint: Optional[str] = None
    request_method: Optional[str] = None
    response_status: Optional[int] = None
    processing_time_ms: Optional[float] = None
    
    # Compliance Context
    compliance_flags: List[str] = []
    territory_codes: List[str] = []
    usage_rights: List[str] = []
    
    # Integrity & Chain
    previous_log_hash: Optional[str] = None
    log_hash: Optional[str] = None
    digital_signature: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    
    def generate_hash(self) -> str:
        """Generate cryptographic hash for integrity verification"""
        # Create deterministic string from log data
        hash_data = {
            "log_id": self.log_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "event_name": self.event_name,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "event_data": self.event_data,
            "previous_log_hash": self.previous_log_hash
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def model_post_init(self, __context):
        """Generate hash after model initialization"""
        if not self.log_hash:
            self.log_hash = self.generate_hash()

class MetadataSnapshot(BaseModel):
    """Timestamped snapshot of metadata for legal compliance"""
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    snapshot_timestamp: datetime = Field(default_factory=datetime.now)
    
    # Content Identification
    isrc: Optional[str] = None
    upc: Optional[str] = None
    filename: str
    original_filename: Optional[str] = None
    
    # Complete Metadata State
    metadata_version: int = 1
    metadata_state: Dict[str, Any] = {}
    
    # Validation State
    validation_status: str = "pending"
    validation_score: Optional[float] = None
    validation_errors: List[Dict[str, Any]] = []
    validation_warnings: List[Dict[str, Any]] = []
    
    # Rights State
    rights_status: str = "pending"
    territory_rights: Dict[str, str] = {}  # territory -> status
    usage_rights: Dict[str, str] = {}      # usage_type -> status
    rights_expiry: Optional[datetime] = None
    
    # Compliance State
    compliance_status: str = "pending"
    compliance_score: Optional[float] = None
    compliance_flags: List[str] = []
    
    # File Information
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_hash: Optional[str] = None
    storage_location: Optional[str] = None
    
    # User Context
    user_id: str
    user_email: Optional[str] = None
    
    # Trigger Information
    trigger_event: Optional[str] = None
    trigger_reason: Optional[str] = None
    
    # Legal Compliance
    retention_period_years: int = 7
    legal_holds: List[str] = []  # Legal hold IDs
    
    # Snapshot Integrity
    snapshot_hash: Optional[str] = None
    previous_snapshot_hash: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    
    def generate_snapshot_hash(self) -> str:
        """Generate hash for snapshot integrity"""
        hash_data = {
            "snapshot_id": self.snapshot_id,
            "content_id": self.content_id,
            "timestamp": self.snapshot_timestamp.isoformat(),
            "metadata_state": self.metadata_state,
            "validation_status": self.validation_status,
            "rights_status": self.rights_status,
            "compliance_status": self.compliance_status,
            "user_id": self.user_id,
            "previous_snapshot_hash": self.previous_snapshot_hash
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(hash_string.encode()).hexdigest()

class UploadAuditLog(BaseModel):
    """Specialized audit log for file uploads"""
    upload_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_log_id: str  # Reference to main audit log
    
    # Upload Details
    content_id: str
    original_filename: str
    final_filename: str
    file_size: int
    file_type: str
    mime_type: Optional[str] = None
    
    # Upload Process
    upload_method: str  # direct, s3, etc.
    upload_duration_ms: Optional[float] = None
    chunks_uploaded: Optional[int] = None
    upload_progress: List[Dict[str, Any]] = []  # Progress checkpoints
    
    # File Validation
    file_hash_md5: Optional[str] = None
    file_hash_sha256: Optional[str] = None
    virus_scan_result: Optional[str] = None
    content_type_validated: bool = False
    
    # Metadata at Upload
    initial_metadata: Dict[str, Any] = {}
    metadata_source: str = "user_input"  # user_input, file_embedded, api, etc.
    
    # Storage Information
    storage_provider: str = "s3"
    storage_region: Optional[str] = None
    storage_bucket: Optional[str] = None
    storage_key: Optional[str] = None
    storage_url: Optional[str] = None
    
    # Processing Pipeline
    processing_steps: List[Dict[str, Any]] = []
    processing_errors: List[str] = []
    
    # User Context (duplicated for easy querying)
    user_id: str
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Upload Status
    upload_status: str = "completed"
    error_message: Optional[str] = None
    
    # Timestamps
    upload_started: datetime = Field(default_factory=datetime.now)
    upload_completed: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

class ValidationAuditLog(BaseModel):
    """Specialized audit log for metadata validation"""
    validation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_log_id: str  # Reference to main audit log
    
    # Validation Context
    content_id: str
    validation_type: str  # schema, business_rules, duplicate_check, etc.
    validation_format: str  # ddex, json, csv, etc.
    
    # Validation Input
    input_metadata: Dict[str, Any] = {}
    input_hash: Optional[str] = None
    
    # Validation Configuration
    validation_rules: List[str] = []
    validation_config: Dict[str, Any] = {}
    schema_version: Optional[str] = None
    
    # Validation Results
    validation_status: str  # passed, failed, warning
    validation_score: Optional[float] = None
    confidence_score: Optional[float] = None
    
    # Detailed Results
    field_results: Dict[str, Dict[str, Any]] = {}  # field -> validation result
    validation_errors: List[Dict[str, Any]] = []
    validation_warnings: List[Dict[str, Any]] = []
    validation_info: List[Dict[str, Any]] = []
    
    # Duplicate Detection
    duplicate_check_performed: bool = False
    duplicates_found: List[Dict[str, Any]] = []
    duplicate_identifiers: List[str] = []  # ISRCs, UPCs that were duplicates
    
    # Business Rules
    business_rules_applied: List[str] = []
    business_rule_violations: List[Dict[str, Any]] = []
    
    # Performance Metrics
    validation_duration_ms: float
    rules_processed: int = 0
    fields_validated: int = 0
    
    # System Context
    validator_version: Optional[str] = None
    validation_engine: str = "bigmann_validator"
    
    # User Context
    user_id: str
    triggered_by: str = "user"  # user, system, api, etc.
    
    # Timestamps
    validation_started: datetime = Field(default_factory=datetime.now)
    validation_completed: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

class RightsCheckAuditLog(BaseModel):
    """Specialized audit log for rights and compliance checks"""
    rights_check_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_log_id: str  # Reference to main audit log
    
    # Rights Check Context
    content_id: str
    check_type: str  # territory, usage, expiry, embargo
    check_scope: str  # single_territory, global, usage_specific
    
    # Content Information
    isrc: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    
    # Rights Configuration
    territory_codes: List[str] = []
    usage_rights: List[str] = []  # streaming, sync, broadcast, etc.
    rights_holders: List[Dict[str, Any]] = []
    
    # Check Parameters
    target_territories: List[str] = []
    target_usage_types: List[str] = []
    check_date: datetime = Field(default_factory=datetime.now)
    future_date_check: Optional[datetime] = None
    
    # Rights Check Results
    overall_status: str  # compliant, non_compliant, partial, unknown
    overall_score: Optional[float] = None
    
    # Territory Results
    territory_results: Dict[str, Dict[str, Any]] = {}  # territory -> result
    territory_violations: List[Dict[str, Any]] = []
    territory_warnings: List[Dict[str, Any]] = []
    
    # Usage Rights Results
    usage_results: Dict[str, Dict[str, Any]] = {}  # usage_type -> result
    usage_violations: List[Dict[str, Any]] = []
    usage_warnings: List[Dict[str, Any]] = []
    
    # Expiry and Embargo Checks
    expiry_checks: List[Dict[str, Any]] = []
    embargo_checks: List[Dict[str, Any]] = []
    expired_rights: List[Dict[str, Any]] = []
    active_embargos: List[Dict[str, Any]] = []
    
    # Compliance Integration
    compliance_frameworks: List[str] = []  # GDPR, DMCA, etc.
    compliance_violations: List[Dict[str, Any]] = []
    
    # Performance Metrics
    check_duration_ms: float
    territories_checked: int = 0
    usage_types_checked: int = 0
    
    # System Context
    rights_engine_version: Optional[str] = None
    data_sources: List[str] = []  # Where rights data came from
    
    # User Context
    user_id: str
    triggered_by: str = "user"
    
    # Timestamps
    check_started: datetime = Field(default_factory=datetime.now)
    check_completed: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

class AuditLogQuery(BaseModel):
    """Query parameters for audit log searches"""
    # Time Range
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Filtering
    event_types: List[AuditEventType] = []
    severities: List[AuditSeverity] = []
    outcomes: List[AuditOutcome] = []
    user_ids: List[str] = []
    resource_ids: List[str] = []
    content_ids: List[str] = []
    
    # Search
    search_text: Optional[str] = None
    
    # Pagination
    limit: int = 50
    offset: int = 0
    
    # Sorting
    sort_by: str = "timestamp"
    sort_order: str = "desc"  # asc, desc

class AuditReport(BaseModel):
    """Audit report generation configuration"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_name: str
    report_type: str  # summary, detailed, compliance, security
    
    # Report Scope
    query: AuditLogQuery
    include_metadata_snapshots: bool = False
    include_file_details: bool = False
    include_user_details: bool = False
    
    # Export Configuration
    export_format: str = "pdf"  # pdf, csv, json, xlsx
    include_charts: bool = True
    include_statistics: bool = True
    
    # Compliance Configuration
    compliance_frameworks: List[str] = []
    retention_analysis: bool = False
    privacy_redaction: bool = True
    
    # Generated Report Info
    generated_by: str
    generated_at: datetime = Field(default_factory=datetime.now)
    report_size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None

class RealTimeAlert(BaseModel):
    """Real-time alert for suspicious activities or compliance violations"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str  # security, compliance, performance, error
    severity: AuditSeverity
    
    # Alert Details
    title: str
    message: str
    description: Optional[str] = None
    
    # Context
    event_type: AuditEventType
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Alert Rules
    rule_name: Optional[str] = None
    rule_condition: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    
    # Related Data
    related_log_ids: List[str] = []
    related_content_ids: List[str] = []
    
    # Alert Status
    status: str = "active"  # active, acknowledged, resolved, suppressed
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Notification
    notification_channels: List[str] = []  # email, slack, webhook
    notification_sent: bool = False
    notification_attempts: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AuditStatistics(BaseModel):
    """Audit trail statistics and metrics"""
    stats_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Time Period
    period_start: datetime
    period_end: datetime
    period_type: str = "daily"  # hourly, daily, weekly, monthly
    
    # Event Counts
    total_events: int = 0
    events_by_type: Dict[str, int] = {}
    events_by_severity: Dict[str, int] = {}
    events_by_outcome: Dict[str, int] = {}
    events_by_user: Dict[str, int] = {}
    
    # Upload Statistics
    total_uploads: int = 0
    successful_uploads: int = 0
    failed_uploads: int = 0
    total_upload_size_bytes: int = 0
    
    # Validation Statistics
    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    validation_success_rate: float = 0.0
    
    # Rights Check Statistics
    total_rights_checks: int = 0
    compliant_rights_checks: int = 0
    non_compliant_rights_checks: int = 0
    rights_compliance_rate: float = 0.0
    
    # Performance Metrics
    average_upload_time_ms: float = 0.0
    average_validation_time_ms: float = 0.0
    average_rights_check_time_ms: float = 0.0
    
    # Top Items
    top_users_by_activity: List[Dict[str, Any]] = []
    top_content_by_activity: List[Dict[str, Any]] = []
    most_common_errors: List[Dict[str, Any]] = []
    
    # Compliance Metrics
    gdpr_requests: int = 0
    data_deletion_requests: int = 0
    privacy_violations: int = 0
    
    # System Health
    system_errors: int = 0
    security_events: int = 0
    performance_issues: int = 0
    
    # Generated Info
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = "system"