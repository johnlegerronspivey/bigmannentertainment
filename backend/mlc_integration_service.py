"""
Mechanical Licensing Collective (MLC) Integration Service
Big Mann Entertainment Platform - MLC Distribution Integration

This service handles integration with the Mechanical Licensing Collective
for mechanical licensing, royalty reporting, and distribution management.
"""

import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLCLicenseType(str, Enum):
    MECHANICAL = "mechanical"
    SYNCHRONIZATION = "synchronization"
    DIGITAL_PHONORECORD = "digital_phonorecord"
    STREAMING = "streaming"

class MLCSubmissionStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"

class MLCMusicalWork(BaseModel):
    work_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    composers: List[str]
    publishers: List[str]
    iswc: Optional[str] = None  # International Standard Musical Work Code
    isrc: Optional[str] = None  # International Standard Recording Code
    duration_seconds: int
    genres: List[str] = []
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    copyright_owner: str
    publishing_administrator: Optional[str] = None
    mechanical_rights_owner: str

class MLCUsageReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    work_id: str
    dsp_name: str  # Digital Service Provider name
    usage_date: datetime
    play_count: int
    territory: str
    revenue_generated: float
    mechanical_royalty_rate: float
    total_mechanical_royalty: float
    report_period_start: datetime
    report_period_end: datetime
    submission_status: MLCSubmissionStatus = MLCSubmissionStatus.PENDING

class MLCDistributionRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    work_ids: List[str]
    target_dsps: List[str]
    license_types: List[MLCLicenseType]
    distribution_date: datetime
    territory_codes: List[str]
    metadata: Dict[str, Any] = {}

class MLCIntegrationService:
    """Service for integrating with Mechanical Licensing Collective"""
    
    def __init__(self):
        self.api_base_url = "https://api.themlc.com/v1"  # Mock URL for demo
        self.api_key = "MLC_API_KEY_PLACEHOLDER"  # Would be from environment
        self.works_cache = {}
        self.reports_cache = {}
        self.distributions_cache = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample MLC data for demo"""
        
        # Sample musical works
        sample_works = [
            MLCMusicalWork(
                title="Summer Vibes 2024",
                composers=["John Spivey", "Sarah Johnson"],
                publishers=["Big Mann Music Publishing"],
                iswc="T-123456789-1",
                isrc="USBME2401001",
                duration_seconds=210,
                genres=["Pop", "Electronic"],
                copyright_owner="Big Mann Entertainment",
                mechanical_rights_owner="Big Mann Music Publishing"
            ),
            MLCMusicalWork(
                title="City Lights Groove",
                composers=["Mike Rodriguez", "Lisa Chen"],
                publishers=["Big Mann Music Publishing", "Urban Sounds LLC"],
                iswc="T-123456789-2", 
                isrc="USBME2401002",
                duration_seconds=195,
                genres=["Hip-Hop", "R&B"],
                copyright_owner="Big Mann Entertainment",
                mechanical_rights_owner="Big Mann Music Publishing"
            ),
            MLCMusicalWork(
                title="Acoustic Dreams",
                composers=["Emma Wilson"],
                publishers=["Indie Folk Publishing"],
                iswc="T-123456789-3",
                isrc="USBME2401003", 
                duration_seconds=240,
                genres=["Folk", "Acoustic"],
                copyright_owner="Big Mann Entertainment",
                mechanical_rights_owner="Big Mann Music Publishing"
            )
        ]
        
        for work in sample_works:
            self.works_cache[work.work_id] = work
        
        # Sample usage reports
        sample_reports = []
        dsps = ["Spotify", "Apple Music", "Amazon Music", "YouTube Music", "Tidal"]
        territories = ["US", "CA", "GB", "AU", "DE"]
        
        for work in sample_works:
            for dsp in dsps:
                for territory in territories:
                    play_count = 1000 + (hash(f"{work.work_id}{dsp}{territory}") % 50000)
                    revenue = play_count * 0.004  # $0.004 per play
                    mechanical_rate = 0.091  # Standard mechanical rate
                    mechanical_royalty = play_count * (mechanical_rate / 1000)
                    
                    report = MLCUsageReport(
                        work_id=work.work_id,
                        dsp_name=dsp,
                        usage_date=datetime.now(timezone.utc) - timedelta(days=30),
                        play_count=play_count,
                        territory=territory,
                        revenue_generated=revenue,
                        mechanical_royalty_rate=mechanical_rate,
                        total_mechanical_royalty=mechanical_royalty,
                        report_period_start=datetime.now(timezone.utc) - timedelta(days=60),
                        report_period_end=datetime.now(timezone.utc) - timedelta(days=30),
                        submission_status=MLCSubmissionStatus.ACCEPTED
                    )
                    sample_reports.append(report)
                    self.reports_cache[report.report_id] = report
        
        logger.info(f"Initialized MLC service with {len(sample_works)} works and {len(sample_reports)} reports")
    
    async def register_musical_work(self, work: MLCMusicalWork) -> Dict[str, Any]:
        """Register a musical work with the MLC"""
        try:
            # In production, this would make an API call to MLC
            # For demo, we simulate the registration process
            
            # Validate required fields
            if not work.title or not work.composers or not work.copyright_owner:
                return {
                    "success": False,
                    "error": "Missing required fields: title, composers, or copyright_owner"
                }
            
            # Generate MLC-specific identifiers if not provided
            if not work.iswc:
                work.iswc = f"T-{uuid.uuid4().hex[:9].upper()}-1"
            if not work.isrc:
                work.isrc = f"USBME24{len(self.works_cache):05d}"
            
            # Store the work
            self.works_cache[work.work_id] = work
            
            # Simulate MLC registration response
            mlc_response = {
                "mlc_work_id": f"MLC{uuid.uuid4().hex[:8].upper()}",
                "registration_status": "registered",
                "registration_date": datetime.now(timezone.utc).isoformat(),
                "iswc_assigned": work.iswc,
                "next_steps": [
                    "Submit usage reports from DSPs",
                    "File royalty claims as needed",
                    "Monitor distribution and revenue"
                ]
            }
            
            logger.info(f"Registered musical work: {work.title} (ID: {work.work_id})")
            
            return {
                "success": True,
                "work_id": work.work_id,
                "mlc_registration": mlc_response,
                "message": "Musical work registered successfully with MLC"
            }
            
        except Exception as e:
            logger.error(f"Error registering musical work: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_distribution_request(self, request: MLCDistributionRequest) -> Dict[str, Any]:
        """Create distribution request through MLC network"""
        try:
            # Validate works exist
            missing_works = [wid for wid in request.work_ids if wid not in self.works_cache]
            if missing_works:
                return {
                    "success": False,
                    "error": f"Musical works not found: {missing_works}"
                }
            
            # Store distribution request  
            self.distributions_cache[request.request_id] = request
            
            # Simulate MLC distribution process
            distribution_info = {
                "mlc_distribution_id": f"MLC-DIST-{uuid.uuid4().hex[:8].upper()}",
                "status": "processing",
                "estimated_delivery_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
                "target_dsps": request.target_dsps,
                "territories": request.territory_codes,
                "licenses_required": [lt.value for lt in request.license_types],
                "processing_fees": {
                    "mechanical_licensing": len(request.work_ids) * 2.50,
                    "distribution_processing": len(request.target_dsps) * 5.00,
                    "territory_filing": len(request.territory_codes) * 1.00
                }
            }
            
            total_fees = sum(distribution_info["processing_fees"].values())
            distribution_info["total_processing_fees"] = total_fees
            
            logger.info(f"Created MLC distribution request: {request.request_id}")
            
            return {
                "success": True,
                "request_id": request.request_id,
                "distribution_info": distribution_info,
                "estimated_reach": len(request.target_dsps) * len(request.territory_codes) * 1000000,  # Estimated users
                "message": "Distribution request created and submitted to MLC network"
            }
            
        except Exception as e:
            logger.error(f"Error creating distribution request: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_mlc_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get MLC analytics and performance data"""
        try:
            # Calculate analytics from cached data
            total_works = len(self.works_cache)
            total_reports = len([r for r in self.reports_cache.values() if r.submission_status == MLCSubmissionStatus.ACCEPTED])
            total_plays = sum(r.play_count for r in self.reports_cache.values())
            total_mechanical_royalties = sum(r.total_mechanical_royalty for r in self.reports_cache.values())
            
            # DSP performance breakdown
            dsp_performance = {}
            for report in self.reports_cache.values():
                if report.dsp_name not in dsp_performance:
                    dsp_performance[report.dsp_name] = {
                        "plays": 0,
                        "revenue": 0,
                        "mechanical_royalties": 0
                    }
                dsp_performance[report.dsp_name]["plays"] += report.play_count
                dsp_performance[report.dsp_name]["revenue"] += report.revenue_generated
                dsp_performance[report.dsp_name]["mechanical_royalties"] += report.total_mechanical_royalty
            
            # Territory performance
            territory_performance = {}
            for report in self.reports_cache.values():
                if report.territory not in territory_performance:
                    territory_performance[report.territory] = {
                        "plays": 0,
                        "mechanical_royalties": 0
                    }
                territory_performance[report.territory]["plays"] += report.play_count
                territory_performance[report.territory]["mechanical_royalties"] += report.total_mechanical_royalty
            
            # Top performing works
            work_performance = {}
            for report in self.reports_cache.values():
                if report.work_id not in work_performance:
                    work = self.works_cache.get(report.work_id)
                    work_performance[report.work_id] = {
                        "title": work.title if work else "Unknown",
                        "plays": 0,
                        "mechanical_royalties": 0
                    }
                work_performance[report.work_id]["plays"] += report.play_count
                work_performance[report.work_id]["mechanical_royalties"] += report.total_mechanical_royalty
            
            # Sort top works by plays
            top_works = sorted(work_performance.values(), key=lambda x: x["plays"], reverse=True)[:5]
            
            analytics = {
                "overview": {
                    "total_registered_works": total_works,
                    "total_usage_reports": total_reports,
                    "total_plays": total_plays,
                    "total_mechanical_royalties": round(total_mechanical_royalties, 2),
                    "average_royalty_per_play": round(total_mechanical_royalties / max(total_plays, 1), 6),
                    "active_dsps": len(dsp_performance),
                    "active_territories": len(territory_performance)
                },
                "dsp_performance": dsp_performance,
                "territory_performance": territory_performance,
                "top_performing_works": top_works,
                "recent_activity": {
                    "new_registrations_this_month": 3,
                    "reports_submitted_this_month": len([r for r in self.reports_cache.values() if r.usage_date >= datetime.now(timezone.utc) - timedelta(days=30)]),
                    "processing_distributions": len([d for d in self.distributions_cache.values()])
                },
                "compliance_status": {
                    "mlc_registration_current": True,
                    "usage_reporting_up_to_date": True,
                    "mechanical_licenses_valid": True,
                    "last_audit_date": "2024-01-15",
                    "next_audit_due": "2024-07-15"
                }
            }
            
            return {
                "success": True,
                "analytics": analytics,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting MLC analytics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_dsps(self) -> List[Dict[str, Any]]:
        """Get list of available DSPs through MLC network"""
        dsps = [
            {
                "name": "Mechanical Licensing Collective",
                "type": "licensing_collective",
                "territories": ["US"],
                "mechanical_license_required": True,
                "reporting_frequency": "monthly",
                "minimum_payout": 1.00,
                "integration_status": "active",
                "description": "Official US mechanical licensing collective"
            },
            {
                "name": "Spotify",
                "type": "streaming",
                "territories": ["US", "CA", "GB", "AU", "DE", "FR", "JP", "BR", "MX"],
                "mechanical_license_required": True,
                "reporting_frequency": "monthly",
                "minimum_payout": 10.00,
                "integration_status": "active"
            },
            {
                "name": "Apple Music",
                "type": "streaming", 
                "territories": ["US", "CA", "GB", "AU", "DE", "FR", "JP", "BR", "MX"],
                "mechanical_license_required": True,
                "reporting_frequency": "monthly",
                "minimum_payout": 25.00,
                "integration_status": "active"
            },
            {
                "name": "Amazon Music",
                "type": "streaming",
                "territories": ["US", "CA", "GB", "AU", "DE", "FR", "JP"],
                "mechanical_license_required": True,
                "reporting_frequency": "monthly", 
                "minimum_payout": 10.00,
                "integration_status": "active"
            },
            {
                "name": "YouTube Music",
                "type": "streaming",
                "territories": ["US", "CA", "GB", "AU", "DE", "FR", "JP", "BR", "MX", "IN"],
                "mechanical_license_required": True,
                "reporting_frequency": "monthly",
                "minimum_payout": 10.00,
                "integration_status": "active"
            },
            {
                "name": "Pandora",
                "type": "radio/streaming",
                "territories": ["US"],
                "mechanical_license_required": True,
                "reporting_frequency": "monthly",
                "minimum_payout": 25.00,
                "integration_status": "active"
            }
        ]
        
        return dsps

# Global instance
mlc_integration_service = MLCIntegrationService()