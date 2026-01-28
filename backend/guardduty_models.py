"""
AWS GuardDuty Integration - Pydantic Models
Real-time threat detection for AWS infrastructure
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ThreatSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DetectorStatus(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class FindingType(str, Enum):
    # EC2 Finding Types
    UNAUTHORIZED_ACCESS_EC2 = "UnauthorizedAccess:EC2"
    RECON_EC2 = "Recon:EC2"
    TROJAN_EC2 = "Trojan:EC2"
    BACKDOOR_EC2 = "Backdoor:EC2"
    CRYPTOMINING_EC2 = "CryptoCurrency:EC2"
    
    # IAM Finding Types
    UNAUTHORIZED_ACCESS_IAM = "UnauthorizedAccess:IAM"
    PERSISTENCE_IAM = "Persistence:IAM"
    POLICY_IAM = "Policy:IAM"
    STEALTH_IAM = "Stealth:IAM"
    
    # S3 Finding Types
    UNAUTHORIZED_ACCESS_S3 = "UnauthorizedAccess:S3"
    POLICY_S3 = "Policy:S3"
    EXFILTRATION_S3 = "Exfiltration:S3"
    IMPACT_S3 = "Impact:S3"
    
    # Other
    PENTEST = "PenTest"
    MALWARE = "Malware"
    UNKNOWN = "Unknown"


class ResourceType(str, Enum):
    EC2_INSTANCE = "Instance"
    EC2_NETWORK_INTERFACE = "NetworkInterface"
    S3_BUCKET = "S3Bucket"
    IAM_ACCESS_KEY = "AccessKey"
    IAM_USER = "IamUser"
    IAM_ROLE = "IamRole"
    EKS_CLUSTER = "EksCluster"
    CONTAINER = "Container"
    LAMBDA_FUNCTION = "LambdaFunction"


# Detector Models
class DetectorFeature(BaseModel):
    """GuardDuty detector feature configuration"""
    name: str
    status: str = "ENABLED"
    additional_configuration: Optional[Dict[str, Any]] = None


class Detector(BaseModel):
    """GuardDuty detector configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detector_id: Optional[str] = None  # AWS detector ID
    account_id: str
    region: str = "us-east-1"
    status: DetectorStatus = DetectorStatus.ENABLED
    
    # Features
    s3_protection_enabled: bool = True
    eks_protection_enabled: bool = True
    malware_protection_enabled: bool = True
    runtime_monitoring_enabled: bool = True
    
    # Publishing
    finding_publishing_frequency: str = "FIFTEEN_MINUTES"
    
    # Stats
    findings_count: int = 0
    last_finding_time: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateDetectorRequest(BaseModel):
    enable_s3_protection: bool = True
    enable_eks_protection: bool = True
    enable_malware_protection: bool = True
    enable_runtime_monitoring: bool = True
    finding_publishing_frequency: str = "FIFTEEN_MINUTES"


# Finding Models
class AffectedResource(BaseModel):
    """Resource affected by a finding"""
    resource_type: ResourceType
    resource_id: str
    resource_name: Optional[str] = None
    region: str = "us-east-1"
    
    # EC2 specific
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None
    image_id: Optional[str] = None
    availability_zone: Optional[str] = None
    
    # S3 specific
    bucket_name: Optional[str] = None
    bucket_arn: Optional[str] = None
    
    # IAM specific
    user_name: Optional[str] = None
    access_key_id: Optional[str] = None
    principal_id: Optional[str] = None
    
    # Network
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    security_groups: List[str] = []
    
    tags: Dict[str, str] = {}


class ThreatIntelligence(BaseModel):
    """Threat intelligence information"""
    threat_name: Optional[str] = None
    threat_list_name: Optional[str] = None


class NetworkConnection(BaseModel):
    """Network connection information"""
    direction: str  # INBOUND, OUTBOUND
    protocol: str  # TCP, UDP
    local_ip: Optional[str] = None
    local_port: Optional[int] = None
    remote_ip: Optional[str] = None
    remote_port: Optional[int] = None
    blocked: bool = False


class Finding(BaseModel):
    """GuardDuty security finding"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    finding_id: Optional[str] = None  # AWS finding ID
    detector_id: str
    account_id: str
    region: str = "us-east-1"
    
    # Finding details
    type: str  # Full finding type (e.g., "UnauthorizedAccess:EC2/TorClient")
    title: str
    description: str
    
    # Severity
    severity: float  # 0.0 - 10.0
    severity_label: ThreatSeverity = ThreatSeverity.LOW
    confidence: float = 0.0  # 0.0 - 100.0
    
    # Resource affected
    resource: Optional[AffectedResource] = None
    
    # Network info
    network_connections: List[NetworkConnection] = []
    
    # Threat intelligence
    threat_intelligence: Optional[ThreatIntelligence] = None
    
    # Status
    is_archived: bool = False
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    # Timestamps
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional context
    service_name: str = "guardduty"
    event_first_seen: Optional[str] = None
    event_last_seen: Optional[str] = None
    count: int = 1
    
    raw_finding: Optional[Dict[str, Any]] = None


# Threat Intelligence Set Models
class ThreatIntelSet(BaseModel):
    """Custom threat intelligence set"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    threat_intel_set_id: Optional[str] = None  # AWS threat intel set ID
    detector_id: str
    name: str
    description: Optional[str] = None
    
    # Location (S3 URI)
    s3_location: str
    format: str = "TXT"  # TXT, STIX, OTX_CSV, ALIEN_VAULT, PROOF_POINT, FIRE_EYE
    
    # Status
    is_active: bool = True
    status: str = "ACTIVE"
    
    # Stats
    ip_count: int = 0
    last_updated: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreateThreatIntelSetRequest(BaseModel):
    name: str
    description: Optional[str] = None
    s3_location: str
    format: str = "TXT"
    activate: bool = True


# Filter Models
class FindingFilter(BaseModel):
    """Filter for findings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    
    # Filter criteria
    criteria: Dict[str, Any] = {}
    
    # Action
    action: str = "NOOP"  # NOOP or ARCHIVE
    
    # Rank
    rank: int = 1
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreateFilterRequest(BaseModel):
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any]
    action: str = "NOOP"
    rank: int = 1


# Dashboard Stats Models
class ThreatStatsByType(BaseModel):
    """Statistics grouped by finding type"""
    finding_type: str
    count: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int


class ThreatStatsByResource(BaseModel):
    """Statistics grouped by resource"""
    resource_type: str
    resource_id: str
    finding_count: int
    most_severe_finding: str


class GuardDutyDashboardStats(BaseModel):
    """Complete dashboard statistics"""
    # Finding counts
    total_findings: int = 0
    active_findings: int = 0
    archived_findings: int = 0
    
    # By severity
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    
    # By category
    ec2_findings: int = 0
    s3_findings: int = 0
    iam_findings: int = 0
    other_findings: int = 0
    
    # Detector info
    detector_status: str = "ENABLED"
    detector_id: Optional[str] = None
    
    # Threat intel
    active_threat_intel_sets: int = 0
    
    # Recent activity
    findings_last_24h: int = 0
    findings_last_7d: int = 0
    
    # Top threats
    top_finding_types: List[ThreatStatsByType] = []
    most_targeted_resources: List[ThreatStatsByResource] = []
    
    # Timestamps
    last_finding_time: Optional[datetime] = None
    last_sync_time: Optional[datetime] = None


# Health Response
class GuardDutyHealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "AWS GuardDuty Threat Detection"
    version: str = "1.0.0"
    detector_enabled: bool = False
    aws_connected: bool = False
    aws_region: str = "us-east-1"
    features: List[str] = []
