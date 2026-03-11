"""
AWS Enterprise Mapping Models - Full Infrastructure Integration
Models for AWS resource tracking, cost management, and enterprise mapping
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class AWSServiceType(str, Enum):
    """AWS Service Categories"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORKING = "networking"
    SECURITY = "security"
    ANALYTICS = "analytics"
    AI_ML = "ai_ml"
    MANAGEMENT = "management"
    APPLICATION = "application"
    MEDIA = "media"
    BLOCKCHAIN = "blockchain"


class ResourceStatus(str, Enum):
    """Resource operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    TERMINATED = "terminated"


class CostTier(str, Enum):
    """Cost classification tiers"""
    FREE_TIER = "free_tier"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AWSResource(BaseModel):
    """Base model for AWS resources"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str  # AWS ARN or resource ID
    resource_type: str  # e.g., "ec2:instance", "s3:bucket"
    service_type: AWSServiceType
    name: str
    status: ResourceStatus = ResourceStatus.ACTIVE
    region: str
    account_id: str
    
    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Cost tracking
    monthly_cost: float = 0.0
    cost_tier: CostTier = CostTier.FREE_TIER
    
    # Additional details
    configuration: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class EC2Instance(AWSResource):
    """EC2 Instance resource"""
    instance_type: str = "t3.micro"
    state: str = "running"
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None
    security_groups: List[str] = Field(default_factory=list)
    ami_id: Optional[str] = None
    key_name: Optional[str] = None


class S3Bucket(AWSResource):
    """S3 Bucket resource"""
    bucket_name: str
    versioning_enabled: bool = False
    encryption_enabled: bool = True
    public_access_blocked: bool = True
    object_count: int = 0
    total_size_bytes: int = 0
    storage_class: str = "STANDARD"


class RDSInstance(AWSResource):
    """RDS Database Instance"""
    db_instance_identifier: str
    engine: str  # mysql, postgres, etc.
    engine_version: str
    instance_class: str = "db.t3.micro"
    allocated_storage: int = 20
    multi_az: bool = False
    endpoint: Optional[str] = None
    port: int = 5432
    database_name: Optional[str] = None


class LambdaFunction(AWSResource):
    """Lambda Function resource"""
    function_name: str
    runtime: str = "python3.11"
    handler: str = "index.handler"
    memory_size: int = 128
    timeout: int = 30
    code_size: int = 0
    last_invocation: Optional[datetime] = None
    invocations_count: int = 0
    average_duration_ms: float = 0.0


class CloudFrontDistribution(AWSResource):
    """CloudFront Distribution"""
    distribution_id: str
    domain_name: str
    origin_domain: str
    price_class: str = "PriceClass_100"
    enabled: bool = True
    http_version: str = "http2"
    default_root_object: Optional[str] = None


class IAMRole(AWSResource):
    """IAM Role"""
    role_name: str
    arn: str
    assume_role_policy: Dict[str, Any] = Field(default_factory=dict)
    attached_policies: List[str] = Field(default_factory=list)
    inline_policies: List[str] = Field(default_factory=list)
    last_used: Optional[datetime] = None


class VPCNetwork(AWSResource):
    """VPC Network"""
    vpc_id: str
    cidr_block: str
    is_default: bool = False
    state: str = "available"
    subnets: List[str] = Field(default_factory=list)
    route_tables: List[str] = Field(default_factory=list)
    internet_gateway: Optional[str] = None
    nat_gateways: List[str] = Field(default_factory=list)


class CostBreakdown(BaseModel):
    """Cost breakdown by service/resource"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    period_start: datetime
    period_end: datetime
    total_cost: float
    currency: str = "USD"
    
    # Breakdown by service
    by_service: Dict[str, float] = Field(default_factory=dict)
    
    # Breakdown by region
    by_region: Dict[str, float] = Field(default_factory=dict)
    
    # Top cost contributors
    top_resources: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Trends
    previous_period_cost: Optional[float] = None
    cost_change_percentage: Optional[float] = None
    
    # Budget
    budget_limit: Optional[float] = None
    budget_used_percentage: Optional[float] = None
    
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InfrastructureMap(BaseModel):
    """Complete infrastructure mapping"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    account_id: str
    
    # Resource counts by service type
    resource_counts: Dict[str, int] = Field(default_factory=dict)
    
    # Resources by region
    resources_by_region: Dict[str, int] = Field(default_factory=dict)
    
    # Health metrics
    healthy_resources: int = 0
    warning_resources: int = 0
    critical_resources: int = 0
    
    # Cost metrics
    total_monthly_cost: float = 0.0
    cost_by_service: Dict[str, float] = Field(default_factory=dict)
    
    # Security posture
    compliant_resources: int = 0
    non_compliant_resources: int = 0
    security_score: float = 0.0
    
    # Generated timestamp
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        use_enum_values = True


class ResourceRelationship(BaseModel):
    """Relationship between AWS resources"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_resource_id: str
    target_resource_id: str
    relationship_type: str  # e.g., "depends_on", "communicates_with", "hosted_in"
    direction: str = "outbound"  # outbound, inbound, bidirectional
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceQuota(BaseModel):
    """AWS Service Quota tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_code: str
    quota_code: str
    quota_name: str
    value: float
    unit: str
    adjustable: bool = False
    current_usage: Optional[float] = None
    usage_percentage: Optional[float] = None
    region: str
    account_id: str
    last_checked: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceCheck(BaseModel):
    """AWS Config compliance check result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    resource_type: str
    rule_name: str
    compliance_status: str  # COMPLIANT, NON_COMPLIANT, NOT_APPLICABLE
    annotation: Optional[str] = None
    last_evaluated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AWSRegionInfo(BaseModel):
    """AWS Region information"""
    region_name: str
    region_code: str
    enabled: bool = True
    resource_count: int = 0
    total_cost: float = 0.0
    availability_zones: List[str] = Field(default_factory=list)


class EnterpriseMetrics(BaseModel):
    """Enterprise-wide AWS metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Organization metrics
    total_accounts: int = 0
    active_accounts: int = 0
    total_resources: int = 0
    
    # Cost metrics
    total_monthly_cost: float = 0.0
    cost_forecast_next_month: float = 0.0
    budget_remaining: float = 0.0
    
    # Performance metrics
    average_cpu_utilization: float = 0.0
    average_memory_utilization: float = 0.0
    
    # Security metrics
    security_score: float = 0.0
    open_security_findings: int = 0
    
    # Compliance metrics
    compliance_score: float = 0.0
    non_compliant_resources: int = 0
    
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResourceAction(BaseModel):
    """Action to perform on AWS resource"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    action_type: str  # start, stop, terminate, resize, backup
    parameters: Dict[str, Any] = Field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResourceAlert(BaseModel):
    """Alert for AWS resource"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    resource_name: str
    alert_type: str  # cost, performance, security, availability
    severity: str  # low, medium, high, critical
    title: str
    description: str
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
