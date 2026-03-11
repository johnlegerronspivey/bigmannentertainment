"""
AWS GuardDuty Integration - Pydantic Models
Real-time threat detection and security monitoring
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FindingStatus(str, Enum):
    NEW = "NEW"
    ARCHIVED = "ARCHIVED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class ThreatCategory(str, Enum):
    BACKDOOR = "Backdoor"
    BEHAVIOR = "Behavior"
    CRYPTOCURRENCY = "CryptoCurrency"
    DEFENSE_EVASION = "DefenseEvasion"
    DISCOVERY = "Discovery"
    EXECUTION = "Execution"
    EXFILTRATION = "Exfiltration"
    IMPACT = "Impact"
    INITIAL_ACCESS = "InitialAccess"
    PENTEST = "PenTest"
    PERSISTENCE = "Persistence"
    POLICY = "Policy"
    PRIVILEGE_ESCALATION = "PrivilegeEscalation"
    RECON = "Recon"
    STEALTH = "Stealth"
    TROJAN = "Trojan"
    UNAUTHORIZED_ACCESS = "UnauthorizedAccess"


class ResourceType(str, Enum):
    INSTANCE = "Instance"
    ACCESS_KEY = "AccessKey"
    S3_BUCKET = "S3Bucket"
    IAM_USER = "IAMUser"
    EKS_CLUSTER = "EKSCluster"
    ECS_CLUSTER = "ECSCluster"
    LAMBDA_FUNCTION = "Lambda"
    RDS_DATABASE = "RDSDBInstance"
    CONTAINER = "Container"


# Detector Models
class DetectorStatus(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class Detector(BaseModel):
    """GuardDuty Detector"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detector_id: Optional[str] = None  # AWS detector ID
    account_id: str
    region: str = "us-east-1"
    status: DetectorStatus = DetectorStatus.ENABLED
    
    # Configuration
    finding_publishing_frequency: str = "FIFTEEN_MINUTES"
    s3_logs_enabled: bool = True
    kubernetes_audit_logs_enabled: bool = True
    malware_protection_enabled: bool = True
    
    # Statistics
    findings_count: int = 0
    last_checked: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Finding Models
class ResourceDetails(BaseModel):
    """Details about the affected resource"""
    resource_type: ResourceType
    instance_id: Optional[str] = None
    access_key_id: Optional[str] = None
    bucket_name: Optional[str] = None
    user_name: Optional[str] = None
    cluster_name: Optional[str] = None
    function_name: Optional[str] = None
    database_instance: Optional[str] = None
    
    # Network details
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    
    # Additional details
    tags: Dict[str, str] = {}
    extra_details: Dict[str, Any] = {}


class ThreatIntelligence(BaseModel):
    """Threat intelligence details"""
    threat_list_name: Optional[str] = None
    threat_names: List[str] = []
    ip_addresses: List[str] = []
    domain_details: List[Dict[str, Any]] = []


class NetworkConnection(BaseModel):
    """Network connection details for network-based threats"""
    local_ip: Optional[str] = None
    local_port: Optional[int] = None
    remote_ip: Optional[str] = None
    remote_port: Optional[int] = None
    protocol: Optional[str] = None
    direction: Optional[str] = None  # INBOUND, OUTBOUND
    blocked: bool = False


class Finding(BaseModel):
    """GuardDuty Security Finding"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    finding_id: Optional[str] = None  # AWS finding ID
    
    # Core details
    account_id: str
    region: str = "us-east-1"
    type: str  # e.g., "Backdoor:EC2/DenialOfService.Tcp"
    title: str
    description: str
    
    # Severity
    severity: float  # 0.0 - 10.0
    severity_level: SeverityLevel = SeverityLevel.MEDIUM
    
    # Classification
    category: Optional[ThreatCategory] = None
    resource: Optional[ResourceDetails] = None
    
    # Threat details
    threat_intelligence: Optional[ThreatIntelligence] = None
    network_connection: Optional[NetworkConnection] = None
    evidence: Optional[Dict[str, Any]] = None
    
    # Status tracking
    status: FindingStatus = FindingStatus.NEW
    archived: bool = False
    user_feedback: Optional[str] = None  # USEFUL, NOT_USEFUL
    
    # Acknowledgement
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FindingUpdate(BaseModel):
    """Update request for a finding"""
    status: Optional[FindingStatus] = None
    user_feedback: Optional[str] = None
    archived: Optional[bool] = None
    notes: Optional[str] = None


# Dashboard Statistics Models
class SeveritySummary(BaseModel):
    """Summary of findings by severity"""
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class StatusSummary(BaseModel):
    """Summary of findings by status"""
    new: int = 0
    acknowledged: int = 0
    resolved: int = 0
    archived: int = 0


class ThreatSummary(BaseModel):
    """Summary of threats by category"""
    category: str
    count: int
    severity_avg: float


class ResourceSummary(BaseModel):
    """Summary of affected resources"""
    resource_type: str
    count: int
    critical_count: int


class GuardDutyDashboardStats(BaseModel):
    """Complete dashboard statistics"""
    # Detector stats
    total_detectors: int = 0
    active_detectors: int = 0
    
    # Finding totals
    total_findings: int = 0
    new_findings: int = 0
    
    # Severity breakdown
    severity_summary: SeveritySummary = SeveritySummary()
    
    # Status breakdown
    status_summary: StatusSummary = StatusSummary()
    
    # Threat analysis
    threats_by_category: List[ThreatSummary] = []
    top_threat_types: List[Dict[str, Any]] = []
    
    # Resource analysis
    resources_by_type: List[ResourceSummary] = []
    most_targeted_resources: List[Dict[str, Any]] = []
    
    # Time-based analysis
    findings_last_24h: int = 0
    findings_last_7d: int = 0
    findings_last_30d: int = 0
    
    # Trend data
    trend_data: List[Dict[str, Any]] = []
    
    # Last update
    last_sync_time: Optional[datetime] = None


# API Response Models
class FindingsResponse(BaseModel):
    """Paginated findings response"""
    success: bool = True
    findings: List[Finding] = []
    total: int = 0
    limit: int = 50
    offset: int = 0
    has_more: bool = False


class DetectorsResponse(BaseModel):
    """Detectors list response"""
    success: bool = True
    detectors: List[Detector] = []
    total: int = 0


class GuardDutyHealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "AWS GuardDuty Threat Detection"
    version: str = "1.0.0"
    guardduty_enabled: bool = False
    aws_connected: bool = False
    aws_region: str = "us-east-1"
    features: List[str] = []


# Threat Types Reference
THREAT_TYPES = {
    "Backdoor": {
        "description": "EC2 instance communicating with known malicious IPs",
        "severity_range": "High to Critical",
        "examples": [
            "Backdoor:EC2/DenialOfService.Tcp",
            "Backdoor:EC2/DenialOfService.Udp",
            "Backdoor:EC2/Spambot",
            "Backdoor:EC2/C&CActivity.B"
        ]
    },
    "CryptoCurrency": {
        "description": "Cryptocurrency mining activity detected",
        "severity_range": "High",
        "examples": [
            "CryptoCurrency:EC2/BitcoinTool.B",
            "CryptoCurrency:EC2/BitcoinTool.B!DNS"
        ]
    },
    "Trojan": {
        "description": "Trojan malware activity detected",
        "severity_range": "High to Critical",
        "examples": [
            "Trojan:EC2/BlackholeTraffic",
            "Trojan:EC2/DropPoint",
            "Trojan:EC2/PhishingDomainRequest"
        ]
    },
    "UnauthorizedAccess": {
        "description": "Unauthorized access attempts detected",
        "severity_range": "Medium to High",
        "examples": [
            "UnauthorizedAccess:EC2/SSHBruteForce",
            "UnauthorizedAccess:EC2/RDPBruteForce",
            "UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B"
        ]
    },
    "Recon": {
        "description": "Reconnaissance activity detected",
        "severity_range": "Low to Medium",
        "examples": [
            "Recon:EC2/PortProbeUnprotectedPort",
            "Recon:EC2/Portscan",
            "Recon:IAMUser/NetworkPermissions"
        ]
    },
    "Policy": {
        "description": "Policy violations detected",
        "severity_range": "Low to Medium",
        "examples": [
            "Policy:IAMUser/RootCredentialUsage",
            "Policy:S3/BucketAnonymousAccessGranted"
        ]
    }
}
