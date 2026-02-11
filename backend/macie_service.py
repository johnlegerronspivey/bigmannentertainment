"""
AWS Macie Integration - Service Layer
Business logic for automated sensitive data discovery and PII detection
"""

import os
import boto3
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import logging

from macie_models import (
    CustomDataIdentifier, CreateCustomIdentifierRequest,
    ClassificationJob, CreateClassificationJobRequest, JobStatus, JobType,
    Finding, SeverityLevel, FindingCategory, AffectedResource,
    SensitiveDataOccurrence, MacieDashboardStats, FindingStatistics,
    JobStatistics, AlertRule, S3BucketInfo, PIIType
)

load_dotenv()
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


class MacieService:
    """Service for AWS Macie operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.custom_identifiers_collection = db.macie_custom_identifiers
        self.jobs_collection = db.macie_classification_jobs
        self.findings_collection = db.macie_findings
        self.alerts_collection = db.macie_alerts
        self.buckets_collection = db.macie_buckets
        
        # Initialize Macie client
        self.macie_client = None
        self.s3_client = None
        self.sts_client = None
        self._initialize_aws_clients()
        
        # Initialize sample data
        asyncio.create_task(self._initialize_sample_data())
    
    def _initialize_aws_clients(self):
        """Initialize AWS clients with credentials"""
        try:
            session_kwargs = {"region_name": AWS_REGION}
            if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
                session_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
                session_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY
            
            self.macie_client = boto3.client("macie2", **session_kwargs)
            self.s3_client = boto3.client("s3", **session_kwargs)
            self.sts_client = boto3.client("sts", **session_kwargs)
            logger.info("AWS clients initialized successfully")
        except Exception as e:
            logger.warning(f"AWS clients initialization warning: {e}")
            # Will use mock mode if AWS not available
    
    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        try:
            if self.sts_client:
                return self.sts_client.get_caller_identity()["Account"]
        except Exception:
            pass
        return "314108682794"  # Default account ID
    
    async def _initialize_sample_data(self):
        """Initialize sample data for demonstration"""
        try:
            # Check if data already exists
            identifiers_count = await self.custom_identifiers_collection.count_documents({})
            if identifiers_count == 0:
                await self._create_sample_custom_identifiers()
            
            findings_count = await self.findings_collection.count_documents({})
            if findings_count == 0:
                await self._create_sample_findings()
            
            jobs_count = await self.jobs_collection.count_documents({})
            if jobs_count == 0:
                await self._create_sample_jobs()
            
            buckets_count = await self.buckets_collection.count_documents({})
            if buckets_count == 0:
                await self._create_sample_buckets()
                
        except Exception as e:
            logger.error(f"Error initializing sample data: {e}")
    
    async def _create_sample_custom_identifiers(self):
        """Create sample custom data identifiers"""
        sample_identifiers = [
            CustomDataIdentifier(
                name="Employee ID",
                description="Detects Big Mann Entertainment employee IDs (format: BME-XXXXXX)",
                regex=r"BME-[A-Z0-9]{6}",
                keywords=["employee", "staff", "worker"],
                maximum_match_distance=50
            ),
            CustomDataIdentifier(
                name="Artist Contract Number",
                description="Detects artist contract numbers (format: AC-YYYY-NNNNNN)",
                regex=r"AC-\d{4}-\d{6}",
                keywords=["contract", "artist", "agreement"],
                maximum_match_distance=50
            ),
            CustomDataIdentifier(
                name="Royalty Account ID",
                description="Detects royalty payment account IDs",
                regex=r"ROY-[A-Z]{2}-\d{8}",
                keywords=["royalty", "payment", "account"],
                maximum_match_distance=50
            ),
            CustomDataIdentifier(
                name="Internal Project Code",
                description="Detects internal project codes",
                regex=r"PRJ-[A-Z]{3}-\d{4}",
                keywords=["project", "internal", "code"],
                maximum_match_distance=30
            )
        ]
        
        for identifier in sample_identifiers:
            await self.custom_identifiers_collection.insert_one(identifier.dict())
    
    async def _create_sample_findings(self):
        """Create sample PII findings for demonstration"""
        sample_findings = [
            Finding(
                type="SensitiveData:S3Object/Personal",
                severity=SeverityLevel.HIGH,
                severity_score=85,
                resource=AffectedResource(
                    bucket_name="bme-artist-contracts",
                    object_key="contracts/2024/artist_001_contract.pdf",
                    object_size=245760,
                    public_access=False
                ),
                sensitive_data_types=["SSN", "DATE_OF_BIRTH", "ADDRESS"],
                sensitive_data_occurrences=[
                    SensitiveDataOccurrence(type="USA_SOCIAL_SECURITY_NUMBER", count=2),
                    SensitiveDataOccurrence(type="DATE_OF_BIRTH", count=1),
                    SensitiveDataOccurrence(type="ADDRESS", count=3)
                ],
                total_detections=6
            ),
            Finding(
                type="SensitiveData:S3Object/Financial",
                severity=SeverityLevel.HIGH,
                severity_score=90,
                resource=AffectedResource(
                    bucket_name="bme-royalty-data",
                    object_key="payments/2024/q1_royalty_payments.xlsx",
                    object_size=1048576,
                    public_access=False
                ),
                sensitive_data_types=["BANK_ACCOUNT", "CREDIT_CARD"],
                sensitive_data_occurrences=[
                    SensitiveDataOccurrence(type="BANK_ACCOUNT_NUMBER", count=45),
                    SensitiveDataOccurrence(type="CREDIT_CARD_NUMBER", count=12)
                ],
                total_detections=57
            ),
            Finding(
                type="SensitiveData:S3Object/Personal",
                severity=SeverityLevel.MEDIUM,
                severity_score=55,
                resource=AffectedResource(
                    bucket_name="bme-marketing",
                    object_key="campaigns/email_list_2024.csv",
                    object_size=524288,
                    public_access=False
                ),
                sensitive_data_types=["EMAIL", "PHONE", "NAME"],
                sensitive_data_occurrences=[
                    SensitiveDataOccurrence(type="EMAIL_ADDRESS", count=1250),
                    SensitiveDataOccurrence(type="PHONE_NUMBER", count=890),
                    SensitiveDataOccurrence(type="NAME", count=1250)
                ],
                total_detections=3390
            ),
            Finding(
                type="SensitiveData:S3Object/Credentials",
                severity=SeverityLevel.HIGH,
                severity_score=95,
                resource=AffectedResource(
                    bucket_name="bme-dev-backups",
                    object_key="config/legacy_config.json",
                    object_size=4096,
                    public_access=True  # Critical!
                ),
                sensitive_data_types=["AWS_SECRET_KEY", "API_KEY"],
                sensitive_data_occurrences=[
                    SensitiveDataOccurrence(type="AWS_SECRET_ACCESS_KEY", count=1),
                    SensitiveDataOccurrence(type="AWS_ACCESS_KEY_ID", count=1)
                ],
                total_detections=2,
                is_acknowledged=False
            ),
            Finding(
                type="SensitiveData:S3Object/Personal",
                severity=SeverityLevel.LOW,
                severity_score=25,
                resource=AffectedResource(
                    bucket_name="bme-public-assets",
                    object_key="press/media_contacts.txt",
                    object_size=8192,
                    public_access=True
                ),
                sensitive_data_types=["EMAIL", "PHONE"],
                sensitive_data_occurrences=[
                    SensitiveDataOccurrence(type="EMAIL_ADDRESS", count=15),
                    SensitiveDataOccurrence(type="PHONE_NUMBER", count=15)
                ],
                total_detections=30
            ),
            Finding(
                type="SensitiveData:S3Object/Medical",
                severity=SeverityLevel.HIGH,
                severity_score=88,
                resource=AffectedResource(
                    bucket_name="bme-hr-records",
                    object_key="benefits/health_insurance_enrollments.xlsx",
                    object_size=2097152,
                    public_access=False
                ),
                sensitive_data_types=["SSN", "MEDICAL_RECORD", "DATE_OF_BIRTH"],
                sensitive_data_occurrences=[
                    SensitiveDataOccurrence(type="USA_SOCIAL_SECURITY_NUMBER", count=150),
                    SensitiveDataOccurrence(type="USA_HEALTH_INSURANCE_CLAIM_NUMBER", count=150),
                    SensitiveDataOccurrence(type="DATE_OF_BIRTH", count=150)
                ],
                total_detections=450
            )
        ]
        
        for finding in sample_findings:
            await self.findings_collection.insert_one(finding.dict())
    
    async def _create_sample_jobs(self):
        """Create sample classification jobs"""
        sample_jobs = [
            ClassificationJob(
                name="Weekly Full Scan",
                description="Comprehensive weekly scan of all production buckets",
                job_type=JobType.SCHEDULED,
                status=JobStatus.COMPLETE,
                buckets=["bme-artist-contracts", "bme-royalty-data", "bme-hr-records"],
                sampling_percentage=100,
                objects_scanned=15420,
                objects_matched=234,
                findings_count=6,
                started_at=datetime.now(timezone.utc) - timedelta(hours=4),
                completed_at=datetime.now(timezone.utc) - timedelta(hours=2)
            ),
            ClassificationJob(
                name="Marketing Data Audit",
                description="Scan marketing assets for PII exposure",
                job_type=JobType.ONE_TIME,
                status=JobStatus.COMPLETE,
                buckets=["bme-marketing", "bme-public-assets"],
                sampling_percentage=100,
                objects_scanned=3250,
                objects_matched=45,
                findings_count=2,
                started_at=datetime.now(timezone.utc) - timedelta(days=1),
                completed_at=datetime.now(timezone.utc) - timedelta(days=1, hours=-2)
            ),
            ClassificationJob(
                name="Dev Environment Check",
                description="Security scan of development backup buckets",
                job_type=JobType.ONE_TIME,
                status=JobStatus.COMPLETE,
                buckets=["bme-dev-backups"],
                sampling_percentage=100,
                objects_scanned=890,
                objects_matched=12,
                findings_count=1,
                started_at=datetime.now(timezone.utc) - timedelta(hours=6),
                completed_at=datetime.now(timezone.utc) - timedelta(hours=5)
            ),
            ClassificationJob(
                name="Continuous Monitoring",
                description="Real-time monitoring of high-risk buckets",
                job_type=JobType.SCHEDULED,
                status=JobStatus.RUNNING,
                buckets=["bme-artist-contracts", "bme-hr-records"],
                sampling_percentage=25,
                objects_scanned=2100,
                objects_matched=18,
                findings_count=0,
                started_at=datetime.now(timezone.utc) - timedelta(minutes=30)
            )
        ]
        
        for job in sample_jobs:
            await self.jobs_collection.insert_one(job.dict())
    
    async def _create_sample_buckets(self):
        """Populate with real S3 bucket data from AWS, fallback to samples"""
        real_buckets = await self._fetch_real_s3_buckets()
        if real_buckets:
            for bucket in real_buckets:
                await self.buckets_collection.insert_one(bucket.dict())
            logger.info(f"Macie: loaded {len(real_buckets)} real S3 buckets")
            return

        # Fallback to sample data
        sample_buckets = [
            S3BucketInfo(
                name="bme-artist-contracts", account_id=self._get_account_id(),
                public_access_blocked=True, versioning_enabled=True,
                encryption_type="AES256", object_count=2450,
                total_size_bytes=536870912, is_monitored=True, findings_count=0
            ),
            S3BucketInfo(
                name="bme-public-assets", account_id=self._get_account_id(),
                public_access_blocked=False, versioning_enabled=False,
                encryption_type="AES256", object_count=12500,
                total_size_bytes=53687091200, is_monitored=True, findings_count=0
            )
        ]
        for bucket in sample_buckets:
            await self.buckets_collection.insert_one(bucket.dict())

    async def _fetch_real_s3_buckets(self):
        """Fetch real S3 bucket info from AWS"""
        if not self.s3_client:
            return None
        try:
            resp = self.s3_client.list_buckets()
            buckets = []
            account_id = self._get_account_id()
            for b in resp.get("Buckets", []):
                name = b["Name"]
                # Get encryption
                enc_type = None
                try:
                    enc = self.s3_client.get_bucket_encryption(Bucket=name)
                    enc_type = enc["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"]
                except Exception:
                    pass
                # Get versioning
                versioning = False
                try:
                    v = self.s3_client.get_bucket_versioning(Bucket=name)
                    versioning = v.get("Status") == "Enabled"
                except Exception:
                    pass
                # Get public access
                public_blocked = True
                try:
                    pa = self.s3_client.get_public_access_block(Bucket=name)
                    cfg = pa.get("PublicAccessBlockConfiguration", {})
                    public_blocked = cfg.get("BlockPublicAcls", False) and cfg.get("BlockPublicPolicy", False)
                except Exception:
                    pass

                buckets.append(S3BucketInfo(
                    name=name, account_id=account_id,
                    public_access_blocked=public_blocked,
                    versioning_enabled=versioning,
                    encryption_type=enc_type,
                    object_count=0, total_size_bytes=0,
                    is_monitored=True, findings_count=0
                ))
            return buckets if buckets else None
        except Exception as e:
            logger.warning(f"Failed to fetch real S3 buckets: {e}")
            return None
    
    # ==================== Custom Data Identifiers ====================
    
    async def create_custom_identifier(
        self,
        request: CreateCustomIdentifierRequest
    ) -> CustomDataIdentifier:
        """Create a custom data identifier"""
        identifier = CustomDataIdentifier(
            name=request.name,
            description=request.description,
            regex=request.regex,
            keywords=request.keywords,
            ignore_words=request.ignore_words,
            maximum_match_distance=request.maximum_match_distance
        )
        
        # Try to create in AWS Macie
        try:
            if self.macie_client:
                response = self.macie_client.create_custom_data_identifier(
                    name=request.name,
                    description=request.description or "",
                    regex=request.regex,
                    keywords=request.keywords,
                    ignoreWords=request.ignore_words,
                    maximumMatchDistance=request.maximum_match_distance
                )
                identifier.arn = response.get("customDataIdentifierArn")
        except Exception as e:
            logger.warning(f"AWS Macie create_custom_data_identifier not available: {e}")
        
        await self.custom_identifiers_collection.insert_one(identifier.dict())
        return identifier
    
    async def get_custom_identifiers(self) -> List[CustomDataIdentifier]:
        """Get all custom data identifiers"""
        cursor = self.custom_identifiers_collection.find({})
        identifiers = []
        async for doc in cursor:
            doc.pop("_id", None)
            identifiers.append(CustomDataIdentifier(**doc))
        return identifiers
    
    async def get_custom_identifier(self, identifier_id: str) -> Optional[CustomDataIdentifier]:
        """Get a specific custom identifier"""
        doc = await self.custom_identifiers_collection.find_one({"id": identifier_id})
        if doc:
            doc.pop("_id", None)
            return CustomDataIdentifier(**doc)
        return None
    
    async def delete_custom_identifier(self, identifier_id: str) -> bool:
        """Delete a custom identifier"""
        result = await self.custom_identifiers_collection.delete_one({"id": identifier_id})
        return result.deleted_count > 0
    
    # ==================== Classification Jobs ====================
    
    async def create_classification_job(
        self,
        request: CreateClassificationJobRequest
    ) -> ClassificationJob:
        """Create a new classification job"""
        job = ClassificationJob(
            name=request.name,
            description=request.description,
            job_type=request.job_type,
            buckets=request.bucket_names,
            managed_data_identifier_selector=request.managed_data_identifier_selector,
            custom_data_identifier_ids=request.custom_data_identifier_ids,
            sampling_percentage=request.sampling_percentage,
            status=JobStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )
        
        # Try to create in AWS Macie
        try:
            if self.macie_client:
                response = self.macie_client.create_classification_job(
                    name=request.name,
                    description=request.description or "",
                    jobType=request.job_type.value,
                    s3JobDefinition={
                        "bucketDefinitions": [{
                            "accountId": self._get_account_id(),
                            "buckets": request.bucket_names
                        }]
                    },
                    managedDataIdentifierSelector=request.managed_data_identifier_selector,
                    customDataIdentifierIds=request.custom_data_identifier_ids,
                    samplingPercentage=request.sampling_percentage
                )
                job.job_id = response.get("jobId")
                job.job_arn = response.get("jobArn")
        except Exception as e:
            logger.warning(f"AWS Macie create_classification_job not available: {e}")
        
        await self.jobs_collection.insert_one(job.dict())
        return job
    
    async def get_classification_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[ClassificationJob], int]:
        """Get classification jobs with optional filtering"""
        query = {}
        if status:
            query["status"] = status.value
        
        total = await self.jobs_collection.count_documents(query)
        cursor = self.jobs_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        
        jobs = []
        async for doc in cursor:
            doc.pop("_id", None)
            jobs.append(ClassificationJob(**doc))
        
        return jobs, total
    
    async def get_classification_job(self, job_id: str) -> Optional[ClassificationJob]:
        """Get a specific classification job"""
        doc = await self.jobs_collection.find_one({"id": job_id})
        if doc:
            doc.pop("_id", None)
            return ClassificationJob(**doc)
        return None
    
    async def cancel_classification_job(self, job_id: str) -> Optional[ClassificationJob]:
        """Cancel a running classification job"""
        await self.jobs_collection.update_one(
            {"id": job_id},
            {"$set": {"status": JobStatus.CANCELLED.value, "completed_at": datetime.now(timezone.utc)}}
        )
        return await self.get_classification_job(job_id)
    
    # ==================== Findings ====================
    
    async def get_findings(
        self,
        severity: Optional[SeverityLevel] = None,
        bucket_name: Optional[str] = None,
        is_acknowledged: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Finding], int]:
        """Get findings with filters"""
        query = {}
        
        if severity:
            query["severity"] = severity.value
        if bucket_name:
            query["resource.bucket_name"] = bucket_name
        if is_acknowledged is not None:
            query["is_acknowledged"] = is_acknowledged
        
        total = await self.findings_collection.count_documents(query)
        cursor = self.findings_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        
        findings = []
        async for doc in cursor:
            doc.pop("_id", None)
            findings.append(Finding(**doc))
        
        return findings, total
    
    async def get_finding(self, finding_id: str) -> Optional[Finding]:
        """Get a specific finding"""
        doc = await self.findings_collection.find_one({"id": finding_id})
        if doc:
            doc.pop("_id", None)
            return Finding(**doc)
        return None
    
    async def acknowledge_finding(
        self,
        finding_id: str,
        user_id: str
    ) -> Optional[Finding]:
        """Acknowledge a finding"""
        await self.findings_collection.update_one(
            {"id": finding_id},
            {
                "$set": {
                    "is_acknowledged": True,
                    "acknowledged_by": user_id,
                    "acknowledged_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return await self.get_finding(finding_id)
    
    async def archive_finding(self, finding_id: str) -> Optional[Finding]:
        """Archive a finding"""
        await self.findings_collection.update_one(
            {"id": finding_id},
            {"$set": {"is_archived": True, "updated_at": datetime.now(timezone.utc)}}
        )
        return await self.get_finding(finding_id)
    
    async def get_finding_statistics(self) -> FindingStatistics:
        """Get aggregated finding statistics"""
        # By severity
        severity_pipeline = [
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ]
        severity_result = await self.findings_collection.aggregate(severity_pipeline).to_list(10)
        findings_by_severity = {r["_id"]: r["count"] for r in severity_result}
        
        # By type
        type_pipeline = [
            {"$unwind": "$sensitive_data_types"},
            {"$group": {"_id": "$sensitive_data_types", "count": {"$sum": 1}}}
        ]
        type_result = await self.findings_collection.aggregate(type_pipeline).to_list(20)
        findings_by_type = {r["_id"]: r["count"] for r in type_result}
        
        # By bucket
        bucket_pipeline = [
            {"$group": {"_id": "$resource.bucket_name", "count": {"$sum": 1}}}
        ]
        bucket_result = await self.findings_collection.aggregate(bucket_pipeline).to_list(20)
        findings_by_bucket = {r["_id"]: r["count"] for r in bucket_result if r["_id"]}
        
        # Totals
        total = await self.findings_collection.count_documents({})
        unacknowledged = await self.findings_collection.count_documents({"is_acknowledged": False})
        high_severity = await self.findings_collection.count_documents({"severity": SeverityLevel.HIGH.value})
        
        return FindingStatistics(
            total_findings=total,
            findings_by_severity=findings_by_severity,
            findings_by_type=findings_by_type,
            findings_by_bucket=findings_by_bucket,
            unacknowledged_count=unacknowledged,
            high_severity_count=high_severity
        )
    
    # ==================== S3 Buckets ====================
    
    async def get_monitored_buckets(self) -> List[S3BucketInfo]:
        """Get all monitored S3 buckets"""
        cursor = self.buckets_collection.find({})
        buckets = []
        async for doc in cursor:
            doc.pop("_id", None)
            buckets.append(S3BucketInfo(**doc))
        return buckets
    
    async def add_bucket_to_monitoring(self, bucket_name: str) -> S3BucketInfo:
        """Add a bucket to monitoring"""
        bucket = S3BucketInfo(
            name=bucket_name,
            account_id=self._get_account_id(),
            is_monitored=True
        )
        
        # Try to get bucket info from AWS
        try:
            if self.s3_client:
                # Get bucket location
                location = self.s3_client.get_bucket_location(Bucket=bucket_name)
                bucket.region = location.get("LocationConstraint") or "us-east-1"
        except Exception as e:
            logger.warning(f"Could not get bucket info from AWS: {e}")
        
        await self.buckets_collection.insert_one(bucket.dict())
        return bucket
    
    async def remove_bucket_from_monitoring(self, bucket_name: str) -> bool:
        """Remove a bucket from monitoring"""
        result = await self.buckets_collection.delete_one({"name": bucket_name})
        return result.deleted_count > 0
    
    # ==================== Dashboard Statistics ====================
    
    async def get_dashboard_stats(self) -> MacieDashboardStats:
        """Get comprehensive dashboard statistics"""
        # Job stats
        total_jobs = await self.jobs_collection.count_documents({})
        running_jobs = await self.jobs_collection.count_documents({"status": JobStatus.RUNNING.value})
        completed_jobs = await self.jobs_collection.count_documents({"status": JobStatus.COMPLETE.value})
        paused_jobs = await self.jobs_collection.count_documents({"status": {"$in": [JobStatus.PAUSED.value, JobStatus.USER_PAUSED.value]}})
        
        # Finding stats
        total_findings = await self.findings_collection.count_documents({})
        high_severity = await self.findings_collection.count_documents({"severity": SeverityLevel.HIGH.value})
        medium_severity = await self.findings_collection.count_documents({"severity": SeverityLevel.MEDIUM.value})
        low_severity = await self.findings_collection.count_documents({"severity": SeverityLevel.LOW.value})
        unacknowledged = await self.findings_collection.count_documents({"is_acknowledged": False})
        
        # Custom identifier stats
        total_identifiers = await self.custom_identifiers_collection.count_documents({})
        active_identifiers = await self.custom_identifiers_collection.count_documents({"is_active": True})
        
        # Bucket stats
        monitored_buckets = await self.buckets_collection.count_documents({"is_monitored": True})
        buckets_with_findings = await self.buckets_collection.count_documents({"findings_count": {"$gt": 0}})
        
        # Aggregated scan stats
        scan_pipeline = [
            {"$group": {
                "_id": None,
                "total_scanned": {"$sum": "$objects_scanned"},
                "total_matched": {"$sum": "$objects_matched"}
            }}
        ]
        scan_result = await self.jobs_collection.aggregate(scan_pipeline).to_list(1)
        total_scanned = scan_result[0]["total_scanned"] if scan_result else 0
        total_matched = scan_result[0]["total_matched"] if scan_result else 0
        
        # PII types detected
        pii_pipeline = [
            {"$unwind": "$sensitive_data_types"},
            {"$group": {"_id": "$sensitive_data_types"}},
            {"$project": {"_id": 0, "type": "$_id"}}
        ]
        pii_result = await self.findings_collection.aggregate(pii_pipeline).to_list(20)
        pii_types = [r["type"] for r in pii_result]
        
        # Recent findings
        now = datetime.now(timezone.utc)
        findings_24h = await self.findings_collection.count_documents({
            "created_at": {"$gte": (now - timedelta(hours=24)).isoformat()}
        })
        findings_7d = await self.findings_collection.count_documents({
            "created_at": {"$gte": (now - timedelta(days=7)).isoformat()}
        })
        
        # Last scan time
        last_job = await self.jobs_collection.find_one(
            {"status": JobStatus.COMPLETE.value},
            sort=[("completed_at", -1)]
        )
        last_scan = last_job.get("completed_at") if last_job else None
        
        return MacieDashboardStats(
            total_jobs=total_jobs,
            running_jobs=running_jobs,
            completed_jobs=completed_jobs,
            paused_jobs=paused_jobs,
            total_findings=total_findings,
            high_severity_findings=high_severity,
            medium_severity_findings=medium_severity,
            low_severity_findings=low_severity,
            unacknowledged_findings=unacknowledged,
            total_custom_identifiers=total_identifiers,
            active_custom_identifiers=active_identifiers,
            monitored_buckets=monitored_buckets,
            buckets_with_findings=buckets_with_findings,
            pii_types_detected=pii_types,
            total_objects_scanned=total_scanned,
            total_sensitive_objects=total_matched,
            last_scan_time=last_scan,
            findings_last_24h=findings_24h,
            findings_last_7d=findings_7d
        )
    
    # ==================== Health Check ====================
    
    async def check_health(self) -> Dict[str, Any]:
        """Check Macie service health"""
        macie_enabled = False
        aws_connected = False
        
        try:
            if self.macie_client:
                # Try to get Macie session
                response = self.macie_client.get_macie_session()
                macie_enabled = response.get("status") == "ENABLED"
                aws_connected = True
        except Exception as e:
            logger.warning(f"Macie health check warning: {e}")
        
        return {
            "status": "healthy",
            "service": "AWS Macie PII Detection",
            "version": "1.0.0",
            "macie_enabled": macie_enabled,
            "aws_connected": aws_connected,
            "aws_region": AWS_REGION,
            "features": [
                "Automated PII Detection",
                "Custom Data Identifiers",
                "Classification Jobs",
                "S3 Bucket Monitoring",
                "Finding Management",
                "Dashboard Analytics",
                "SNS/EventBridge Notifications"
            ]
        }

    # ==================== SNS/EventBridge Notification Methods ====================

    async def get_notification_rules(self) -> List[Dict]:
        """Get all notification rules"""
        rules = []
        async for doc in self.db.macie_notification_rules.find():
            doc.pop('_id', None)
            rules.append(doc)
        
        if not rules:
            await self._initialize_sample_notification_rules()
            async for doc in self.db.macie_notification_rules.find():
                doc.pop('_id', None)
                rules.append(doc)
        return rules

    async def _initialize_sample_notification_rules(self):
        """Create sample notification rules"""
        from macie_models import NotificationRule, NotificationChannel, SeverityLevel
        
        count = await self.db.macie_notification_rules.count_documents({})
        if count > 0:
            return
        
        sample_rules = [
            NotificationRule(
                name="High Severity Alert - SNS",
                description="Send SNS notification for all high severity findings",
                channel=NotificationChannel.SNS,
                min_severity=SeverityLevel.HIGH,
                sns_topic_arn="arn:aws:sns:us-east-1:314108682794:macie-high-severity-alerts",
                is_enabled=True,
                notifications_sent=12,
                last_triggered=datetime.now(timezone.utc) - timedelta(hours=2)
            ),
            NotificationRule(
                name="Credit Card Detection - EventBridge",
                description="EventBridge event for credit card number detections",
                channel=NotificationChannel.EVENTBRIDGE,
                min_severity=SeverityLevel.MEDIUM,
                pii_types=["CREDIT_CARD_NUMBER", "BANK_ACCOUNT_NUMBER"],
                eventbridge_bus_name="macie-findings-bus",
                is_enabled=True,
                notifications_sent=5,
                last_triggered=datetime.now(timezone.utc) - timedelta(hours=6)
            ),
            NotificationRule(
                name="PII in Public Buckets - Email",
                description="Email alert when PII is found in publicly accessible buckets",
                channel=NotificationChannel.EMAIL,
                min_severity=SeverityLevel.LOW,
                email_recipients=["security@bigmann.com", "compliance@bigmann.com"],
                is_enabled=True,
                notifications_sent=8,
                last_triggered=datetime.now(timezone.utc) - timedelta(days=1)
            ),
        ]
        
        for rule in sample_rules:
            await self.db.macie_notification_rules.insert_one(rule.dict())
        
        # Also create sample notification logs
        from macie_models import NotificationLog, NotificationStatus
        sample_logs = [
            NotificationLog(
                rule_id=sample_rules[0].id, rule_name=sample_rules[0].name,
                channel=NotificationChannel.SNS, status=NotificationStatus.SENT,
                severity=SeverityLevel.HIGH, pii_type="USA_SOCIAL_SECURITY_NUMBER",
                bucket_name="bigmann-user-uploads",
                message="High severity finding: SSN detected in bigmann-user-uploads/profiles/user_data.csv",
                message_id="sns-msg-" + str(uuid.uuid4())[:8]
            ),
            NotificationLog(
                rule_id=sample_rules[1].id, rule_name=sample_rules[1].name,
                channel=NotificationChannel.EVENTBRIDGE, status=NotificationStatus.SENT,
                severity=SeverityLevel.MEDIUM, pii_type="CREDIT_CARD_NUMBER",
                bucket_name="bigmann-payment-logs",
                message="Credit card number detected in payment log file",
                message_id="eb-" + str(uuid.uuid4())[:8]
            ),
            NotificationLog(
                rule_id=sample_rules[0].id, rule_name=sample_rules[0].name,
                channel=NotificationChannel.SNS, status=NotificationStatus.FAILED,
                severity=SeverityLevel.HIGH, pii_type="AWS_SECRET_ACCESS_KEY",
                bucket_name="bigmann-config-backup",
                message="AWS credentials detected in config backup",
                error="SNS topic not reachable (simulated)"
            ),
            NotificationLog(
                rule_id=sample_rules[2].id, rule_name=sample_rules[2].name,
                channel=NotificationChannel.EMAIL, status=NotificationStatus.SENT,
                severity=SeverityLevel.MEDIUM, pii_type="EMAIL_ADDRESS",
                bucket_name="bigmann-marketing-data",
                message="Email addresses found in public marketing bucket",
                message_id="email-" + str(uuid.uuid4())[:8]
            ),
        ]
        for log in sample_logs:
            await self.db.macie_notification_logs.insert_one(log.dict())

    async def create_notification_rule(self, request) -> Dict:
        """Create a notification rule"""
        from macie_models import NotificationRule
        rule = NotificationRule(
            name=request.name,
            description=request.description,
            channel=request.channel,
            min_severity=request.min_severity,
            pii_types=request.pii_types,
            bucket_names=request.bucket_names,
            sns_topic_arn=request.sns_topic_arn,
            eventbridge_bus_name=request.eventbridge_bus_name,
            email_recipients=request.email_recipients,
        )
        doc = rule.dict()
        await self.db.macie_notification_rules.insert_one(doc)
        doc.pop('_id', None)
        return doc

    async def toggle_notification_rule(self, rule_id: str) -> Optional[Dict]:
        """Toggle a notification rule on/off"""
        doc = await self.db.macie_notification_rules.find_one({"id": rule_id})
        if not doc:
            return None
        new_val = not doc.get("is_enabled", True)
        await self.db.macie_notification_rules.update_one({"id": rule_id}, {"$set": {"is_enabled": new_val}})
        doc["is_enabled"] = new_val
        doc.pop('_id', None)
        return doc

    async def delete_notification_rule(self, rule_id: str) -> bool:
        """Delete a notification rule"""
        result = await self.db.macie_notification_rules.delete_one({"id": rule_id})
        return result.deleted_count > 0

    async def get_notification_logs(self, rule_id: Optional[str] = None, channel=None, limit: int = 50, offset: int = 0):
        """Get notification logs"""
        query = {}
        if rule_id:
            query["rule_id"] = rule_id
        if channel:
            query["channel"] = channel.value if hasattr(channel, 'value') else channel
        
        total = await self.db.macie_notification_logs.count_documents(query)
        cursor = self.db.macie_notification_logs.find(query).sort("created_at", -1).skip(offset).limit(limit)
        logs = []
        async for doc in cursor:
            doc.pop('_id', None)
            logs.append(doc)
        return logs, total

    async def send_test_notification(self, rule_id: str) -> Optional[Dict]:
        """Send a test notification - uses real AWS SNS when available"""
        import uuid as uuid_mod
        doc = await self.db.macie_notification_rules.find_one({"id": rule_id})
        if not doc:
            return None
        doc.pop('_id', None)
        
        from macie_models import NotificationLog, NotificationStatus, NotificationChannel, SeverityLevel
        
        channel = NotificationChannel(doc["channel"])
        status = NotificationStatus.SENT
        message_text = f"[TEST] Test notification from rule: {doc['name']}"
        message_id = "test-" + str(uuid_mod.uuid4())[:8]
        delivery_note = "simulated"

        # Try real SNS if channel is SNS and topic ARN exists
        if channel == NotificationChannel.SNS and doc.get("sns_topic_arn"):
            try:
                if self.s3_client:
                    sns_client = boto3.client("sns", region_name=AWS_REGION,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                    resp = sns_client.publish(
                        TopicArn=doc["sns_topic_arn"],
                        Subject=f"Macie Alert: {doc['name']}",
                        Message=message_text
                    )
                    message_id = resp.get("MessageId", message_id)
                    delivery_note = "delivered via AWS SNS"
                    logger.info(f"Real SNS notification sent: {message_id}")
            except Exception as e:
                logger.warning(f"Real SNS failed, using simulated: {e}")
                delivery_note = "simulated (SNS unavailable)"

        log = NotificationLog(
            rule_id=rule_id,
            rule_name=doc["name"],
            channel=channel,
            status=status,
            severity=SeverityLevel(doc.get("min_severity", "High")),
            message=message_text,
            message_id=message_id
        )
        log_dict = log.dict()
        await self.db.macie_notification_logs.insert_one(log_dict)
        log_dict.pop('_id', None)
        
        # Update rule stats
        await self.db.macie_notification_rules.update_one(
            {"id": rule_id},
            {"$inc": {"notifications_sent": 1}, "$set": {"last_triggered": datetime.now(timezone.utc)}}
        )
        
        return {"success": True, "message": f"Test notification sent ({delivery_note})", "log": log_dict}

    async def get_notification_stats(self) -> Dict:
        """Get notification statistics"""
        rules = await self.get_notification_rules()
        total_rules = len(rules)
        active_rules = sum(1 for r in rules if r.get("is_enabled"))
        total_sent = sum(r.get("notifications_sent", 0) for r in rules)
        
        # Channel breakdown
        by_channel = {}
        for r in rules:
            ch = r.get("channel", "SNS")
            by_channel[ch] = by_channel.get(ch, 0) + 1
        
        # Log stats
        total_logs = await self.db.macie_notification_logs.count_documents({})
        failed_logs = await self.db.macie_notification_logs.count_documents({"status": "FAILED"})
        
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "total_notifications_sent": total_sent,
            "by_channel": by_channel,
            "total_log_entries": total_logs,
            "failed_notifications": failed_logs,
        }


# Service instance
_service_instance: Optional[MacieService] = None


def initialize_macie_service(db: AsyncIOMotorDatabase) -> MacieService:
    """Initialize the Macie service"""
    global _service_instance
    _service_instance = MacieService(db)
    return _service_instance


def get_macie_service() -> Optional[MacieService]:
    """Get the Macie service instance"""
    return _service_instance
