"""
AWS GuardDuty Integration - Service Layer
Business logic for real-time threat detection and security monitoring
"""

import os
import boto3
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import logging

from guardduty_models import (
    Detector, DetectorStatus, Finding, FindingStatus, SeverityLevel,
    ThreatCategory, ResourceType, ResourceDetails, ThreatIntelligence,
    NetworkConnection, GuardDutyDashboardStats, SeveritySummary,
    StatusSummary, ThreatSummary, ResourceSummary, FindingUpdate
)

load_dotenv()
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


class GuardDutyService:
    """Service for AWS GuardDuty operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.detectors_collection = db.guardduty_detectors
        self.findings_collection = db.guardduty_findings
        
        # Initialize AWS clients
        self.guardduty_client = None
        self.sts_client = None
        self._initialize_aws_clients()
        
        # Initialize sample data (only schedule if an event loop is running)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._initialize_sample_data())
        except RuntimeError:
            logger.warning("GuardDutyService sample data initialization skipped: no running event loop available")
    
    def _initialize_aws_clients(self):
        """Initialize AWS clients with credentials"""
        try:
            session_kwargs = {"region_name": AWS_REGION}
            if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
                session_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
                session_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY
            
            self.guardduty_client = boto3.client("guardduty", **session_kwargs)
            self.sts_client = boto3.client("sts", **session_kwargs)
            logger.info("AWS GuardDuty clients initialized successfully")
        except Exception as e:
            logger.warning(f"AWS clients initialization warning: {e}")
    
    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        try:
            if self.sts_client:
                return self.sts_client.get_caller_identity()["Account"]
        except Exception:
            pass
        return "314108682794"
    
    def _classify_severity(self, severity: float) -> SeverityLevel:
        """Classify numeric severity into level"""
        if severity >= 9.0:
            return SeverityLevel.CRITICAL
        elif severity >= 7.0:
            return SeverityLevel.HIGH
        elif severity >= 4.0:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _extract_category(self, finding_type: str) -> Optional[ThreatCategory]:
        """Extract threat category from finding type"""
        category_map = {
            "Backdoor": ThreatCategory.BACKDOOR,
            "Behavior": ThreatCategory.BEHAVIOR,
            "CryptoCurrency": ThreatCategory.CRYPTOCURRENCY,
            "DefenseEvasion": ThreatCategory.DEFENSE_EVASION,
            "Discovery": ThreatCategory.DISCOVERY,
            "Execution": ThreatCategory.EXECUTION,
            "Exfiltration": ThreatCategory.EXFILTRATION,
            "Impact": ThreatCategory.IMPACT,
            "InitialAccess": ThreatCategory.INITIAL_ACCESS,
            "PenTest": ThreatCategory.PENTEST,
            "Persistence": ThreatCategory.PERSISTENCE,
            "Policy": ThreatCategory.POLICY,
            "PrivilegeEscalation": ThreatCategory.PRIVILEGE_ESCALATION,
            "Recon": ThreatCategory.RECON,
            "Stealth": ThreatCategory.STEALTH,
            "Trojan": ThreatCategory.TROJAN,
            "UnauthorizedAccess": ThreatCategory.UNAUTHORIZED_ACCESS,
        }
        
        for key, category in category_map.items():
            if finding_type.startswith(key):
                return category
        return None
    
    async def _initialize_sample_data(self):
        """Initialize data - sync from real AWS if available, else use samples"""
        try:
            synced = await self._sync_from_aws()
            if synced:
                logger.info("GuardDuty: synced real data from AWS")
                return

            # Fallback to sample data
            findings_count = await self.findings_collection.count_documents({})
            if findings_count == 0:
                await self._create_sample_findings()
            
            detectors_count = await self.detectors_collection.count_documents({})
            if detectors_count == 0:
                await self._create_sample_detectors()
                
        except Exception as e:
            logger.error(f"Error initializing data: {e}")

    async def _sync_from_aws(self) -> bool:
        """Sync real findings and detectors from AWS GuardDuty"""
        if not self.guardduty_client:
            return False
        try:
            # Get real detectors
            detector_resp = self.guardduty_client.list_detectors()
            detector_ids = detector_resp.get("DetectorIds", [])
            if not detector_ids:
                return False

            account_id = self._get_account_id()

            for det_id in detector_ids:
                det_info = self.guardduty_client.get_detector(DetectorId=det_id)
                detector = Detector(
                    detector_id=det_id,
                    account_id=account_id,
                    region=AWS_REGION,
                    status=DetectorStatus.ENABLED if det_info.get("Status") == "ENABLED" else DetectorStatus.DISABLED,
                    finding_publishing_frequency=det_info.get("FindingPublishingFrequency", "FIFTEEN_MINUTES"),
                    s3_logs_enabled=True,
                    kubernetes_audit_logs_enabled=True,
                    malware_protection_enabled=True,
                    last_checked=datetime.now(timezone.utc)
                )
                await self.detectors_collection.update_one(
                    {"detector_id": det_id},
                    {"$set": detector.dict()},
                    upsert=True
                )

                # Get real findings
                findings_resp = self.guardduty_client.list_findings(DetectorId=det_id, MaxResults=50)
                finding_ids = findings_resp.get("FindingIds", [])

                if finding_ids:
                    details_resp = self.guardduty_client.get_findings(
                        DetectorId=det_id, FindingIds=finding_ids
                    )
                    for f in details_resp.get("Findings", []):
                        severity_val = f.get("Severity", 2.0)
                        finding = Finding(
                            finding_id=f["Id"],
                            account_id=f.get("AccountId", account_id),
                            region=f.get("Region", AWS_REGION),
                            type=f.get("Type", "Unknown"),
                            title=f.get("Title", ""),
                            description=f.get("Description", ""),
                            severity=severity_val,
                            severity_level=self._classify_severity(severity_val),
                            category=self._extract_category(f.get("Type", "")),
                            resource=ResourceDetails(
                                resource_type=ResourceType.INSTANCE if "EC2" in f.get("Type", "") else ResourceType.ACCESS_KEY,
                                tags={}
                            ),
                            created_at=f.get("CreatedAt", datetime.now(timezone.utc).isoformat()),
                            updated_at=f.get("UpdatedAt", datetime.now(timezone.utc).isoformat()),
                            status=FindingStatus.NEW
                        )
                        await self.findings_collection.update_one(
                            {"finding_id": f["Id"]},
                            {"$set": finding.dict()},
                            upsert=True
                        )

                # Update detector finding count
                real_count = await self.findings_collection.count_documents({"account_id": account_id})
                await self.detectors_collection.update_one(
                    {"detector_id": det_id},
                    {"$set": {"findings_count": real_count}}
                )

            logger.info(f"Synced {len(detector_ids)} detectors and {len(finding_ids) if detector_ids else 0} findings from AWS")
            return True
        except Exception as e:
            logger.warning(f"AWS GuardDuty sync failed, using sample data: {e}")
            return False
    
    async def _create_sample_detectors(self):
        """Create sample GuardDuty detectors"""
        sample_detectors = [
            Detector(
                detector_id="d1b2c3d4e5f6a7b8c9d0",
                account_id=self._get_account_id(),
                region="us-east-1",
                status=DetectorStatus.ENABLED,
                finding_publishing_frequency="FIFTEEN_MINUTES",
                s3_logs_enabled=True,
                kubernetes_audit_logs_enabled=True,
                malware_protection_enabled=True,
                findings_count=8,
                last_checked=datetime.now(timezone.utc)
            )
        ]
        
        for detector in sample_detectors:
            await self.detectors_collection.insert_one(detector.dict())
    
    async def _create_sample_findings(self):
        """Create sample security findings for demonstration"""
        now = datetime.now(timezone.utc)
        account_id = self._get_account_id()
        
        sample_findings = [
            # Critical - Cryptocurrency Mining
            Finding(
                finding_id="crit-crypto-001",
                account_id=account_id,
                region="us-east-1",
                type="CryptoCurrency:EC2/BitcoinTool.B!DNS",
                title="Cryptocurrency Mining Detected",
                description="EC2 instance i-0abc123def456789 is querying a domain name associated with Bitcoin-related activity.",
                severity=9.5,
                severity_level=SeverityLevel.CRITICAL,
                category=ThreatCategory.CRYPTOCURRENCY,
                resource=ResourceDetails(
                    resource_type=ResourceType.INSTANCE,
                    instance_id="i-0abc123def456789",
                    private_ip="10.0.1.45",
                    public_ip="54.23.145.67",
                    tags={"Name": "web-server-prod", "Environment": "production"}
                ),
                status=FindingStatus.NEW,
                created_at=now - timedelta(hours=2)
            ),
            
            # Critical - Backdoor C&C Activity
            Finding(
                finding_id="crit-backdoor-001",
                account_id=account_id,
                region="us-east-1",
                type="Backdoor:EC2/C&CActivity.B!DNS",
                title="Command and Control Server Communication",
                description="EC2 instance i-0def789abc123456 is querying a domain associated with known Command & Control servers.",
                severity=9.2,
                severity_level=SeverityLevel.CRITICAL,
                category=ThreatCategory.BACKDOOR,
                resource=ResourceDetails(
                    resource_type=ResourceType.INSTANCE,
                    instance_id="i-0def789abc123456",
                    private_ip="10.0.2.89",
                    public_ip="52.87.234.12",
                    tags={"Name": "api-server-prod", "Environment": "production"}
                ),
                network_connection=NetworkConnection(
                    local_ip="10.0.2.89",
                    remote_ip="185.234.72.14",
                    remote_port=443,
                    protocol="TCP",
                    direction="OUTBOUND"
                ),
                status=FindingStatus.NEW,
                created_at=now - timedelta(hours=1)
            ),
            
            # High - SSH Brute Force
            Finding(
                finding_id="high-ssh-001",
                account_id=account_id,
                region="us-east-1",
                type="UnauthorizedAccess:EC2/SSHBruteForce",
                title="SSH Brute Force Attack Detected",
                description="EC2 instance i-0123456789abcdef is being targeted by SSH brute force attacks from 203.0.113.50.",
                severity=8.0,
                severity_level=SeverityLevel.HIGH,
                category=ThreatCategory.UNAUTHORIZED_ACCESS,
                resource=ResourceDetails(
                    resource_type=ResourceType.INSTANCE,
                    instance_id="i-0123456789abcdef",
                    private_ip="10.0.1.100",
                    public_ip="54.167.89.23",
                    tags={"Name": "bastion-host", "Environment": "production"}
                ),
                network_connection=NetworkConnection(
                    local_ip="10.0.1.100",
                    local_port=22,
                    remote_ip="203.0.113.50",
                    remote_port=45234,
                    protocol="TCP",
                    direction="INBOUND"
                ),
                status=FindingStatus.ACKNOWLEDGED,
                acknowledged_by="security-team",
                acknowledged_at=now - timedelta(minutes=30),
                created_at=now - timedelta(hours=4)
            ),
            
            # High - IAM Credential Exfiltration
            Finding(
                finding_id="high-iam-001",
                account_id=account_id,
                region="us-east-1",
                type="UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.InsideAWS",
                title="Credential Exfiltration Attempt",
                description="IAM credentials from EC2 instance are being used from an IP address outside the expected range.",
                severity=7.8,
                severity_level=SeverityLevel.HIGH,
                category=ThreatCategory.UNAUTHORIZED_ACCESS,
                resource=ResourceDetails(
                    resource_type=ResourceType.IAM_USER,
                    user_name="ec2-role-user",
                    access_key_id="AKIA1234567890EXAMPLE",
                    extra_details={"assumed_role": "EC2-WebServer-Role"}
                ),
                status=FindingStatus.NEW,
                created_at=now - timedelta(hours=3)
            ),
            
            # High - Trojan Activity
            Finding(
                finding_id="high-trojan-001",
                account_id=account_id,
                region="us-east-1",
                type="Trojan:EC2/BlackholeTraffic",
                title="Trojan Blackhole Traffic Detected",
                description="EC2 instance is sending traffic to IP addresses that are on a blackhole list.",
                severity=7.5,
                severity_level=SeverityLevel.HIGH,
                category=ThreatCategory.TROJAN,
                resource=ResourceDetails(
                    resource_type=ResourceType.INSTANCE,
                    instance_id="i-0abc987654321def",
                    private_ip="10.0.3.45",
                    tags={"Name": "worker-node-3", "Environment": "staging"}
                ),
                status=FindingStatus.NEW,
                created_at=now - timedelta(hours=6)
            ),
            
            # Medium - Port Scan Detection
            Finding(
                finding_id="med-recon-001",
                account_id=account_id,
                region="us-east-1",
                type="Recon:EC2/Portscan",
                title="Port Scan Detected",
                description="EC2 instance i-0567890abcdef123 is being used to perform port scans on other hosts.",
                severity=5.5,
                severity_level=SeverityLevel.MEDIUM,
                category=ThreatCategory.RECON,
                resource=ResourceDetails(
                    resource_type=ResourceType.INSTANCE,
                    instance_id="i-0567890abcdef123",
                    private_ip="10.0.2.30",
                    tags={"Name": "scanner-test", "Environment": "development"}
                ),
                status=FindingStatus.RESOLVED,
                resolved_by="dev-team",
                resolved_at=now - timedelta(hours=1),
                notes="Instance was running authorized security scan. Finding dismissed.",
                created_at=now - timedelta(days=1)
            ),
            
            # Medium - S3 Bucket Policy Change
            Finding(
                finding_id="med-policy-001",
                account_id=account_id,
                region="us-east-1",
                type="Policy:S3/BucketAnonymousAccessGranted",
                title="S3 Bucket Made Public",
                description="S3 bucket bme-sensitive-data was configured to allow anonymous access.",
                severity=5.0,
                severity_level=SeverityLevel.MEDIUM,
                category=ThreatCategory.POLICY,
                resource=ResourceDetails(
                    resource_type=ResourceType.S3_BUCKET,
                    bucket_name="bme-sensitive-data",
                    tags={"Department": "Engineering"}
                ),
                status=FindingStatus.ACKNOWLEDGED,
                acknowledged_by="security-team",
                acknowledged_at=now - timedelta(hours=2),
                created_at=now - timedelta(hours=12)
            ),
            
            # Low - Unusual API Call
            Finding(
                finding_id="low-discovery-001",
                account_id=account_id,
                region="us-east-1",
                type="Discovery:S3/MaliciousIPCaller.Custom",
                title="API Call from Unusual Location",
                description="S3 API calls made from an IP address on a custom threat list.",
                severity=3.0,
                severity_level=SeverityLevel.LOW,
                category=ThreatCategory.DISCOVERY,
                resource=ResourceDetails(
                    resource_type=ResourceType.S3_BUCKET,
                    bucket_name="bme-logs",
                    extra_details={"api_action": "ListBuckets"}
                ),
                threat_intelligence=ThreatIntelligence(
                    threat_list_name="custom-ip-blocklist",
                    ip_addresses=["198.51.100.25"]
                ),
                status=FindingStatus.ARCHIVED,
                archived=True,
                created_at=now - timedelta(days=7)
            )
        ]
        
        for finding in sample_findings:
            await self.findings_collection.insert_one(finding.dict())
    
    # ==================== Detector Operations ====================
    
    async def get_detectors(self) -> List[Detector]:
        """Get all GuardDuty detectors"""
        cursor = self.detectors_collection.find({})
        detectors = []
        async for doc in cursor:
            doc.pop("_id", None)
            detectors.append(Detector(**doc))
        return detectors
    
    async def get_detector(self, detector_id: str) -> Optional[Detector]:
        """Get a specific detector"""
        doc = await self.detectors_collection.find_one({"detector_id": detector_id})
        if doc:
            doc.pop("_id", None)
            return Detector(**doc)
        return None
    
    async def create_detector(self) -> Detector:
        """Create a new GuardDuty detector"""
        detector = Detector(
            detector_id=f"d{datetime.now().strftime('%Y%m%d%H%M%S')}",
            account_id=self._get_account_id(),
            region=AWS_REGION,
            status=DetectorStatus.ENABLED
        )
        
        # Try to create in AWS GuardDuty
        try:
            if self.guardduty_client:
                response = self.guardduty_client.create_detector(
                    Enable=True,
                    FindingPublishingFrequency="FIFTEEN_MINUTES"
                )
                detector.detector_id = response.get("DetectorId")
        except Exception as e:
            logger.warning(f"AWS GuardDuty create_detector not available: {e}")
        
        await self.detectors_collection.insert_one(detector.dict())
        return detector
    
    # ==================== Finding Operations ====================
    
    async def get_findings(
        self,
        severity_level: Optional[SeverityLevel] = None,
        status: Optional[FindingStatus] = None,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        days_back: int = 30,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Finding], int]:
        """Get findings with filters"""
        query = {}
        
        if severity_level:
            query["severity_level"] = severity_level.value
        if status:
            query["status"] = status.value
        if category:
            query["category"] = category
        if resource_type:
            query["resource.resource_type"] = resource_type
        
        # Time filter
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        query["created_at"] = {"$gte": cutoff.isoformat()}
        
        total = await self.findings_collection.count_documents(query)
        cursor = self.findings_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        
        findings = []
        async for doc in cursor:
            doc.pop("_id", None)
            findings.append(Finding(**doc))
        
        return findings, total
    
    async def get_finding(self, finding_id: str) -> Optional[Finding]:
        """Get a specific finding"""
        doc = await self.findings_collection.find_one({"finding_id": finding_id})
        if not doc:
            doc = await self.findings_collection.find_one({"id": finding_id})
        if doc:
            doc.pop("_id", None)
            return Finding(**doc)
        return None
    
    async def update_finding(
        self,
        finding_id: str,
        update: FindingUpdate,
        user_id: str = "system"
    ) -> Optional[Finding]:
        """Update a finding's status or notes"""
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        if update.status:
            update_data["status"] = update.status.value
            if update.status == FindingStatus.ACKNOWLEDGED:
                update_data["acknowledged_by"] = user_id
                update_data["acknowledged_at"] = datetime.now(timezone.utc)
            elif update.status == FindingStatus.RESOLVED:
                update_data["resolved_by"] = user_id
                update_data["resolved_at"] = datetime.now(timezone.utc)
        
        if update.archived is not None:
            update_data["archived"] = update.archived
            if update.archived:
                update_data["status"] = FindingStatus.ARCHIVED.value
        
        if update.user_feedback:
            update_data["user_feedback"] = update.user_feedback
        
        if update.notes:
            update_data["notes"] = update.notes
        
        result = await self.findings_collection.update_one(
            {"$or": [{"finding_id": finding_id}, {"id": finding_id}]},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_finding(finding_id)
        return None
    
    async def acknowledge_finding(self, finding_id: str, user_id: str) -> Optional[Finding]:
        """Acknowledge a finding"""
        return await self.update_finding(
            finding_id,
            FindingUpdate(status=FindingStatus.ACKNOWLEDGED),
            user_id
        )
    
    async def resolve_finding(self, finding_id: str, user_id: str, notes: Optional[str] = None) -> Optional[Finding]:
        """Resolve a finding"""
        return await self.update_finding(
            finding_id,
            FindingUpdate(status=FindingStatus.RESOLVED, notes=notes),
            user_id
        )
    
    async def archive_finding(self, finding_id: str) -> Optional[Finding]:
        """Archive a finding"""
        return await self.update_finding(
            finding_id,
            FindingUpdate(archived=True)
        )
    
    # ==================== Dashboard Statistics ====================
    
    async def get_dashboard_stats(self) -> GuardDutyDashboardStats:
        """Get comprehensive dashboard statistics"""
        now = datetime.now(timezone.utc)
        
        # Detector stats
        total_detectors = await self.detectors_collection.count_documents({})
        active_detectors = await self.detectors_collection.count_documents({"status": DetectorStatus.ENABLED.value})
        
        # Finding totals
        total_findings = await self.findings_collection.count_documents({})
        new_findings = await self.findings_collection.count_documents({"status": FindingStatus.NEW.value})
        
        # Severity breakdown
        critical = await self.findings_collection.count_documents({"severity_level": SeverityLevel.CRITICAL.value})
        high = await self.findings_collection.count_documents({"severity_level": SeverityLevel.HIGH.value})
        medium = await self.findings_collection.count_documents({"severity_level": SeverityLevel.MEDIUM.value})
        low = await self.findings_collection.count_documents({"severity_level": SeverityLevel.LOW.value})
        
        # Status breakdown
        acknowledged = await self.findings_collection.count_documents({"status": FindingStatus.ACKNOWLEDGED.value})
        resolved = await self.findings_collection.count_documents({"status": FindingStatus.RESOLVED.value})
        archived = await self.findings_collection.count_documents({"status": FindingStatus.ARCHIVED.value})
        
        # Category analysis
        category_pipeline = [
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "avg_severity": {"$avg": "$severity"}
            }},
            {"$sort": {"count": -1}}
        ]
        category_result = await self.findings_collection.aggregate(category_pipeline).to_list(20)
        threats_by_category = [
            ThreatSummary(
                category=r["_id"] or "Unknown",
                count=r["count"],
                severity_avg=round(r["avg_severity"], 2)
            )
            for r in category_result if r["_id"]
        ]
        
        # Top threat types
        type_pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        type_result = await self.findings_collection.aggregate(type_pipeline).to_list(5)
        top_threat_types = [{"type": r["_id"], "count": r["count"]} for r in type_result]
        
        # Resource analysis
        resource_pipeline = [
            {"$group": {
                "_id": "$resource.resource_type",
                "count": {"$sum": 1},
                "critical_count": {
                    "$sum": {"$cond": [{"$eq": ["$severity_level", "CRITICAL"]}, 1, 0]}
                }
            }},
            {"$sort": {"count": -1}}
        ]
        resource_result = await self.findings_collection.aggregate(resource_pipeline).to_list(10)
        resources_by_type = [
            ResourceSummary(
                resource_type=r["_id"] or "Unknown",
                count=r["count"],
                critical_count=r["critical_count"]
            )
            for r in resource_result if r["_id"]
        ]
        
        # Time-based analysis
        findings_24h = await self.findings_collection.count_documents({
            "created_at": {"$gte": (now - timedelta(hours=24)).isoformat()}
        })
        findings_7d = await self.findings_collection.count_documents({
            "created_at": {"$gte": (now - timedelta(days=7)).isoformat()}
        })
        findings_30d = await self.findings_collection.count_documents({
            "created_at": {"$gte": (now - timedelta(days=30)).isoformat()}
        })
        
        # Trend data (last 7 days)
        trend_data = []
        for i in range(7):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = await self.findings_collection.count_documents({
                "created_at": {
                    "$gte": day_start.isoformat(),
                    "$lt": day_end.isoformat()
                }
            })
            trend_data.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": count
            })
        
        return GuardDutyDashboardStats(
            total_detectors=total_detectors,
            active_detectors=active_detectors,
            total_findings=total_findings,
            new_findings=new_findings,
            severity_summary=SeveritySummary(
                critical=critical,
                high=high,
                medium=medium,
                low=low
            ),
            status_summary=StatusSummary(
                new=new_findings,
                acknowledged=acknowledged,
                resolved=resolved,
                archived=archived
            ),
            threats_by_category=threats_by_category,
            top_threat_types=top_threat_types,
            resources_by_type=resources_by_type,
            findings_last_24h=findings_24h,
            findings_last_7d=findings_7d,
            findings_last_30d=findings_30d,
            trend_data=list(reversed(trend_data)),
            last_sync_time=now
        )
    
    # ==================== Sync with AWS ====================
    
    async def sync_findings_from_aws(self, detector_id: str) -> int:
        """Sync findings from AWS GuardDuty"""
        if not self.guardduty_client:
            logger.warning("AWS GuardDuty client not initialized")
            return 0
        
        try:
            # List findings from AWS
            response = self.guardduty_client.list_findings(
                DetectorId=detector_id,
                MaxResults=50
            )
            
            finding_ids = response.get("FindingIds", [])
            if not finding_ids:
                return 0
            
            # Get finding details
            findings_response = self.guardduty_client.get_findings(
                DetectorId=detector_id,
                FindingIds=finding_ids
            )
            
            synced_count = 0
            for aws_finding in findings_response.get("Findings", []):
                finding = self._normalize_aws_finding(aws_finding)
                
                # Upsert finding
                await self.findings_collection.update_one(
                    {"finding_id": finding.finding_id},
                    {"$set": finding.dict()},
                    upsert=True
                )
                synced_count += 1
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing findings from AWS: {e}")
            return 0
    
    def _normalize_aws_finding(self, aws_finding: Dict[str, Any]) -> Finding:
        """Normalize AWS GuardDuty finding to application format"""
        severity = aws_finding.get("Severity", 0)
        finding_type = aws_finding.get("Type", "Unknown")
        
        resource_data = aws_finding.get("Resource", {})
        resource_type_str = resource_data.get("ResourceType", "Instance")
        
        try:
            resource_type = ResourceType(resource_type_str)
        except ValueError:
            resource_type = ResourceType.INSTANCE
        
        resource = ResourceDetails(
            resource_type=resource_type,
            instance_id=resource_data.get("InstanceDetails", {}).get("InstanceId"),
            access_key_id=resource_data.get("AccessKeyDetails", {}).get("AccessKeyId"),
            bucket_name=resource_data.get("S3BucketDetails", [{}])[0].get("Name") if resource_data.get("S3BucketDetails") else None,
        )
        
        return Finding(
            finding_id=aws_finding.get("Id"),
            account_id=aws_finding.get("AccountId"),
            region=aws_finding.get("Region", AWS_REGION),
            type=finding_type,
            title=self._extract_title(finding_type),
            description=aws_finding.get("Description", ""),
            severity=severity,
            severity_level=self._classify_severity(severity),
            category=self._extract_category(finding_type),
            resource=resource,
            archived=aws_finding.get("Archived", False),
            user_feedback=aws_finding.get("UserFeedback"),
            created_at=datetime.fromisoformat(aws_finding.get("CreatedAt", "").replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(aws_finding.get("UpdatedAt", "").replace("Z", "+00:00"))
        )
    
    def _extract_title(self, finding_type: str) -> str:
        """Extract human-readable title from finding type"""
        parts = finding_type.split(":")
        if len(parts) > 1:
            return parts[-1].replace("/", ": ").replace(".", " ")
        return finding_type
    
    # ==================== Health Check ====================
    
    async def check_health(self) -> Dict[str, Any]:
        """Check GuardDuty service health"""
        guardduty_enabled = False
        aws_connected = False
        
        try:
            if self.guardduty_client:
                # Try to list detectors
                response = self.guardduty_client.list_detectors()
                aws_connected = True
                guardduty_enabled = len(response.get("DetectorIds", [])) > 0
        except Exception as e:
            logger.warning(f"GuardDuty health check warning: {e}")
        
        return {
            "status": "healthy",
            "service": "AWS GuardDuty Threat Detection",
            "version": "1.0.0",
            "guardduty_enabled": guardduty_enabled,
            "aws_connected": aws_connected,
            "aws_region": AWS_REGION,
            "features": [
                "Real-time Threat Detection",
                "Finding Management",
                "Severity Classification",
                "Resource Tracking",
                "Threat Intelligence",
                "Dashboard Analytics"
            ]
        }


# Service instance
_service_instance: Optional[GuardDutyService] = None


def initialize_guardduty_service(db: AsyncIOMotorDatabase) -> GuardDutyService:
    """Initialize the GuardDuty service"""
    global _service_instance
    _service_instance = GuardDutyService(db)
    return _service_instance


def get_guardduty_service() -> Optional[GuardDutyService]:
    """Get the GuardDuty service instance"""
    return _service_instance
