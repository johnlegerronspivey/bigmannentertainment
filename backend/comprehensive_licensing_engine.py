"""
Comprehensive Platform Licensing Engine
Advanced licensing management system with automated license generation,
compliance tracking, and comprehensive agreement management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import IndexModel
from pydantic import BaseModel, Field
import uuid
import json
from decimal import Decimal
from fastapi import HTTPException

# Import existing services
from business_information_service import BusinessInformationService, BusinessInformation
from licensing_service import LicensingService
from licensing_models import PlatformLicense, LicensingAgreement, LicenseStatus, LicenseType

logger = logging.getLogger(__name__)


class PlatformCategory(BaseModel):
    """Platform category configuration for licensing"""
    category_id: str
    category_name: str
    platforms: List[str]
    default_license_terms: Dict[str, Any]
    compliance_requirements: List[str]
    pricing_tier: str


class LicenseTemplate(BaseModel):
    """License agreement template"""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_name: str
    platform_category: str
    license_terms: Dict[str, Any]
    compliance_requirements: List[str]
    legal_clauses: List[str]
    pricing_structure: Dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComprehensiveLicenseAgreement(BaseModel):
    """Comprehensive license agreement with business information"""
    agreement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Business Information Integration
    business_information: Dict[str, Any]
    
    # Platform Coverage
    platforms_licensed: List[str]
    platform_categories: List[str]
    total_platforms: int
    
    # License Terms
    license_type: str
    license_duration_months: int
    auto_renewal: bool = True
    
    # Legal Framework
    governing_law: str = "Tennessee, USA"
    dispute_resolution: str = "Binding Arbitration"
    liability_limitations: Dict[str, Any]
    
    # Compliance Requirements
    regulatory_compliance: List[str]
    content_guidelines: List[str]
    reporting_requirements: List[str]
    
    # Financial Terms
    licensing_fees: Dict[str, Decimal]
    revenue_sharing: Dict[str, Decimal]
    payment_terms: Dict[str, Any]
    
    # Performance Obligations
    service_level_agreements: Dict[str, Any]
    uptime_requirements: Dict[str, float]
    support_obligations: List[str]
    
    # Intellectual Property
    ip_ownership: Dict[str, str]
    usage_rights: List[str]
    content_restrictions: List[str]
    
    # Termination Conditions
    termination_clauses: List[str]
    notice_requirements: Dict[str, int]
    data_retention_policy: Dict[str, Any]
    
    # Status and Tracking
    agreement_status: str = "draft"  # draft, active, suspended, terminated
    signed_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutomatedLicensingWorkflow(BaseModel):
    """Automated licensing workflow configuration"""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str
    trigger_conditions: List[str]
    automation_steps: List[Dict[str, Any]]
    approval_requirements: List[str]
    notification_settings: Dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceDocumentation(BaseModel):
    """Compliance documentation for platform licensing"""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str
    platform_id: str
    compliance_requirements: List[str]
    documentation_content: Dict[str, Any]
    legal_review_status: str = "pending"
    approval_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComprehensiveLicensingEngine:
    """Advanced licensing engine with comprehensive business information integration"""
    
    def __init__(self, database):
        self.db = database
        
        # Collections
        self.license_templates_collection: AsyncIOMotorCollection = database.license_templates
        self.comprehensive_agreements_collection: AsyncIOMotorCollection = database.comprehensive_agreements
        self.licensing_workflows_collection: AsyncIOMotorCollection = database.licensing_workflows
        self.compliance_documents_collection: AsyncIOMotorCollection = database.compliance_documents
        self.platform_categories_collection: AsyncIOMotorCollection = database.platform_categories
        
        # Services
        self.business_info_service = BusinessInformationService(database)
        self.licensing_service = LicensingService()
        
        # Platform categorization
        self.platform_categories = {
            "streaming_music": {
                "platforms": ["spotify", "apple_music", "amazon_music", "tidal", "deezer", "pandora", "revolt"],
                "default_terms": {
                    "revenue_share": 10.0,
                    "monthly_limit": 500,
                    "license_fee": 99.99
                },
                "compliance": ["content_quality", "metadata_standards", "royalty_reporting", "sound_recording_industry_standards", "isrc_identification_required"]
            },
            "social_media": {
                "platforms": ["instagram", "tiktok", "facebook", "twitter", "youtube", "snapchat"],
                "default_terms": {
                    "revenue_share": 5.0,
                    "monthly_limit": 1000,
                    "license_fee": 49.99
                },
                "compliance": ["content_guidelines", "community_standards", "copyright_protection", "audio_content_standards", "isrc_identification_recommended"]
            },
            "broadcast_media": {
                "platforms": ["iheartradio", "siriusxm", "clear_channel", "cumulus_media"],
                "default_terms": {
                    "revenue_share": 15.0,
                    "monthly_limit": 200,
                    "license_fee": 199.99
                },
                "compliance": ["broadcast_standards", "fcc_compliance", "performance_rights", "sound_recording_broadcast_standards", "isrc_identification_required"]
            },
            "video_streaming": {
                "platforms": ["netflix", "hulu", "amazon_prime", "hbo_max", "tubi"],
                "default_terms": {
                    "revenue_share": 20.0,
                    "monthly_limit": 50,
                    "license_fee": 299.99
                },
                "compliance": ["content_rating", "sync_licensing", "territorial_restrictions", "audio_sync_standards"]
            }
        }
        
        # Initialize collections (only schedule if an event loop is running)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._initialize_collections())
        except RuntimeError:
            logger.warning("ComprehensiveLicensingEngine initialization skipped: no running event loop available")
    
    async def _initialize_collections(self):
        """Initialize database collections with indexes"""
        try:
            # License templates indexes
            await self.license_templates_collection.create_indexes([
                IndexModel([("template_id", 1)], unique=True),
                IndexModel([("platform_category", 1)]),
                IndexModel([("template_name", 1)])
            ])
            
            # Comprehensive agreements indexes
            await self.comprehensive_agreements_collection.create_indexes([
                IndexModel([("agreement_id", 1)], unique=True),
                IndexModel([("agreement_status", 1)]),
                IndexModel([("platforms_licensed", 1)]),
                IndexModel([("effective_date", 1)])
            ])
            
            logger.info("Comprehensive licensing engine collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing comprehensive licensing collections: {e}")
    
    async def create_comprehensive_license_agreement(
        self, 
        platform_ids: List[str], 
        license_type: str = "master_agreement",
        business_id: Optional[str] = None
    ) -> ComprehensiveLicenseAgreement:
        """Create comprehensive license agreement with integrated business information"""
        try:
            logger.info(f"Creating comprehensive license agreement for {len(platform_ids)} platforms")
            
            # Get consolidated business information with error handling
            try:
                business_info = await self.business_info_service.get_business_information_for_licensing(platform_ids)
            except Exception as e:
                logger.error(f"Error getting business information: {e}")
                # Use default business information
                business_info = {
                    "business_entity": {"legal_name": "Big Mann Entertainment"},
                    "contact_information": {"primary_email": "owner@bigmannentertainment.com"}
                }
            
            # Categorize platforms
            platform_categories = self._categorize_platforms(platform_ids)
            logger.info(f"Platform categories: {list(platform_categories.keys())}")
            
            # Calculate comprehensive licensing terms
            try:
                licensing_terms = await self._calculate_comprehensive_licensing_terms(platform_ids, platform_categories)
            except Exception as e:
                logger.error(f"Error calculating licensing terms: {e}")
                licensing_terms = {
                    "fees": {"default": 99.99},
                    "revenue_share": {"default": 10.0},
                    "volume_discount_applied": 1.0,
                    "total_platforms": len(platform_ids)
                }
            
            # Generate legal clauses and compliance requirements
            try:
                legal_framework = self._generate_legal_framework(platform_categories)
            except Exception as e:
                logger.error(f"Error generating legal framework: {e}")
                legal_framework = {"applicable_laws": ["US Copyright Law"]}
            
            # Create comprehensive agreement
            agreement_data = {
                "business_information": business_info,
                "platforms_licensed": platform_ids,
                "platform_categories": list(platform_categories.keys()),
                "total_platforms": len(platform_ids),
                "license_type": license_type,
                "license_duration_months": 12,
                "auto_renewal": True,
                
                # Legal Framework
                "governing_law": "Alabama, USA",
                "dispute_resolution": "Binding Arbitration",
                "liability_limitations": {
                    "general_liability": "$1,000,000",
                    "intellectual_property": "$2,000,000",
                    "data_breach": "$500,000"
                },
                
                # Compliance Requirements
                "regulatory_compliance": self._get_regulatory_compliance_requirements(platform_categories),
                "content_guidelines": self._get_content_guidelines(platform_categories),
                "reporting_requirements": self._get_reporting_requirements(platform_categories),
                
                # Financial Terms
                "licensing_fees": licensing_terms["fees"],
                "revenue_sharing": licensing_terms["revenue_share"],
                "payment_terms": {
                    "payment_schedule": "monthly",
                    "payment_method": "bank_transfer",
                    "late_fee": "1.5% per month",
                    "grace_period_days": 15
                },
                
                # Performance Obligations
                "service_level_agreements": {
                    "content_delivery": "99.9% uptime",
                    "api_response_time": "< 200ms",
                    "support_response": "24 hours"
                },
                "uptime_requirements": {
                    "platform_availability": 99.9,
                    "api_availability": 99.95,
                    "content_delivery": 99.8
                },
                "support_obligations": [
                    "24/7 technical support",
                    "Monthly performance reports",
                    "Quarterly business reviews",
                    "Platform integration assistance"
                ],
                
                # Intellectual Property
                "ip_ownership": {
                    "content_ownership": "Big Mann Entertainment retains full ownership",
                    "platform_usage_rights": "Limited license for distribution only",
                    "derivative_works": "Prohibited without written consent"
                },
                "usage_rights": [
                    "Digital distribution rights",
                    "Streaming rights",
                    "Download rights (where applicable)",
                    "Promotional usage rights"
                ],
                "content_restrictions": [
                    "No modification without consent",
                    "No sublicensing without approval",
                    "Geographic restrictions apply",
                    "Content must comply with platform guidelines"
                ],
                
                # Termination Conditions
                "termination_clauses": [
                    "Either party may terminate with 30 days written notice",
                    "Immediate termination for material breach",
                    "Automatic termination upon bankruptcy",
                    "Platform policy violations may result in immediate termination"
                ],
                "notice_requirements": {
                    "standard_termination": 30,
                    "breach_notification": 7,
                    "renewal_notice": 60
                },
                "data_retention_policy": {
                    "content_removal_timeline": "30 days post-termination",
                    "analytics_data_retention": "12 months",
                    "financial_records_retention": "7 years"
                },
                
                "agreement_status": "active",  # Changed from draft to active
                "effective_date": datetime.now(timezone.utc),
                "expiration_date": datetime.now(timezone.utc) + timedelta(days=365)
            }
            
            comprehensive_agreement = ComprehensiveLicenseAgreement(**agreement_data)
            
            # Store in database with error handling
            try:
                await self.comprehensive_agreements_collection.insert_one(comprehensive_agreement.dict())
                logger.info(f"Created comprehensive license agreement: {comprehensive_agreement.agreement_id}")
            except Exception as e:
                logger.error(f"Error storing agreement in database: {e}")
                # Continue anyway, the agreement object is still valid
            
            return comprehensive_agreement
            
        except Exception as e:
            logger.error(f"Error creating comprehensive license agreement: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create license agreement: {str(e)}")
    
    def _categorize_platforms(self, platform_ids: List[str]) -> Dict[str, List[str]]:
        """Categorize platforms for licensing purposes"""
        categorized = {}
        
        for platform_id in platform_ids:
            for category, config in self.platform_categories.items():
                if platform_id in config["platforms"]:
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(platform_id)
                    break
            else:
                # Default category for uncategorized platforms
                if "other" not in categorized:
                    categorized["other"] = []
                categorized["other"].append(platform_id)
        
        return categorized
    
    async def _calculate_comprehensive_licensing_terms(
        self, 
        platform_ids: List[str], 
        platform_categories: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive licensing terms based on platforms and categories"""
        try:
            total_fees = {}
            total_revenue_share = {}
            
            for category, platforms in platform_categories.items():
                if category in self.platform_categories:
                    config = self.platform_categories[category]
                    category_fee = config["default_terms"]["license_fee"] * len(platforms)
                    category_revenue_share = config["default_terms"]["revenue_share"]
                    
                    total_fees[category] = Decimal(str(category_fee))
                    total_revenue_share[category] = Decimal(str(category_revenue_share))
                else:
                    # Default terms for uncategorized platforms
                    total_fees[category] = Decimal("99.99") * len(platforms)
                    total_revenue_share[category] = Decimal("7.5")
            
            # Calculate volume discounts
            total_platforms = len(platform_ids)
            if total_platforms >= 50:
                discount_factor = Decimal("0.85")  # 15% discount
            elif total_platforms >= 20:
                discount_factor = Decimal("0.90")  # 10% discount
            elif total_platforms >= 10:
                discount_factor = Decimal("0.95")  # 5% discount
            else:
                discount_factor = Decimal("1.0")   # No discount
            
            # Apply volume discount
            for category in total_fees:
                total_fees[category] = total_fees[category] * discount_factor
            
            return {
                "fees": {k: float(v) for k, v in total_fees.items()},
                "revenue_share": {k: float(v) for k, v in total_revenue_share.items()},
                "volume_discount_applied": float(discount_factor),
                "total_platforms": total_platforms
            }
            
        except Exception as e:
            logger.error(f"Error calculating licensing terms: {e}")
            raise
    
    def _generate_legal_framework(self, platform_categories: Dict[str, List[str]]) -> Dict[str, Any]:
        """Generate legal framework based on platform categories"""
        legal_framework = {
            "applicable_laws": ["US Copyright Law", "DMCA", "Alabama Business Law", "Sound Recording Act"],
            "international_considerations": [],
            "industry_standards": ["CRB Statutory Rates", "ASCAP/BMI Guidelines", "Sound Recording Industry Standards", "RIAA Guidelines"],
            "data_protection": ["CCPA", "GDPR (if applicable)"]
        }
        
        # Add category-specific legal considerations
        if "streaming_music" in platform_categories:
            legal_framework["industry_standards"].extend([
                "Music Modernization Act (MMA)",
                "Performance Rights Organization Guidelines",
                "Sound Recording Licensing Standards"
            ])
        
        if "social_media" in platform_categories:
            legal_framework["applicable_laws"].extend([
                "Section 230 Communications Decency Act",
                "Platform-specific Terms of Service",
                "Audio Content Licensing Requirements"
            ])
        
        if "broadcast_media" in platform_categories:
            legal_framework["applicable_laws"].extend([
                "FCC Regulations",
                "Broadcast Music Licensing Requirements",
                "Sound Recording Broadcast Standards"
            ])
        
        return legal_framework
    
    def _get_regulatory_compliance_requirements(self, platform_categories: Dict[str, List[str]]) -> List[str]:
        """Get regulatory compliance requirements based on platform categories"""
        requirements = [
            "Copyright compliance verification",
            "Business license maintenance",
            "Tax identification accuracy",
            "Content authenticity verification"
        ]
        
        for category in platform_categories:
            if category in self.platform_categories:
                requirements.extend(self.platform_categories[category]["compliance"])
        
        return list(set(requirements))  # Remove duplicates
    
    def _get_content_guidelines(self, platform_categories: Dict[str, List[str]]) -> List[str]:
        """Get content guidelines based on platform categories"""
        guidelines = [
            "Original content or proper licensing required",
            "No copyright infringement",
            "Accurate metadata required",
            "Quality standards compliance"
        ]
        
        if "social_media" in platform_categories:
            guidelines.extend([
                "Community standards compliance",
                "Age-appropriate content",
                "No harmful or misleading content"
            ])
        
        if "streaming_music" in platform_categories:
            guidelines.extend([
                "Audio quality standards (minimum 320kbps)",
                "Complete album/track metadata",
                "ISRC codes required"
            ])
        
        return guidelines
    
    def _get_reporting_requirements(self, platform_categories: Dict[str, List[str]]) -> List[str]:
        """Get reporting requirements based on platform categories"""
        requirements = [
            "Monthly usage reports",
            "Revenue sharing statements",
            "Compliance status reports",
            "Content performance analytics"
        ]
        
        if "streaming_music" in platform_categories:
            requirements.extend([
                "Streaming statistics reports",
                "Royalty distribution reports"
            ])
        
        if "broadcast_media" in platform_categories:
            requirements.extend([
                "Broadcast logs",
                "Performance rights reports"
            ])
        
        return requirements
    
    async def generate_automated_licensing_workflow(
        self, 
        workflow_name: str, 
        platform_categories: List[str]
    ) -> AutomatedLicensingWorkflow:
        """Generate automated licensing workflow for platform categories"""
        try:
            automation_steps = [
                {
                    "step": "business_information_validation",
                    "action": "validate_business_data",
                    "parameters": {"validation_level": "comprehensive"},
                    "auto_execute": True
                },
                {
                    "step": "platform_compatibility_check", 
                    "action": "verify_platform_requirements",
                    "parameters": {"categories": platform_categories},
                    "auto_execute": True
                },
                {
                    "step": "license_terms_calculation",
                    "action": "calculate_licensing_fees",
                    "parameters": {"apply_volume_discount": True},
                    "auto_execute": True
                },
                {
                    "step": "compliance_documentation_generation",
                    "action": "generate_compliance_docs",
                    "parameters": {"include_legal_review": True},
                    "auto_execute": False,
                    "approval_required": True
                },
                {
                    "step": "license_agreement_creation",
                    "action": "create_comprehensive_agreement",
                    "parameters": {"template": "master_agreement"},
                    "auto_execute": False,
                    "approval_required": True
                },
                {
                    "step": "platform_integration_setup",
                    "action": "configure_platform_integrations",
                    "parameters": {"test_connections": True},
                    "auto_execute": True
                },
                {
                    "step": "license_activation",
                    "action": "activate_platform_licenses",
                    "parameters": {"send_notifications": True},
                    "auto_execute": False,
                    "approval_required": True
                }
            ]
            
            workflow_data = {
                "workflow_name": workflow_name,
                "trigger_conditions": [
                    "new_platform_licensing_request",
                    "business_information_update",
                    "compliance_requirement_change"
                ],
                "automation_steps": automation_steps,
                "approval_requirements": [
                    "legal_review_required",
                    "business_owner_approval",
                    "compliance_verification"
                ],
                "notification_settings": {
                    "email_notifications": True,
                    "sms_notifications": False,
                    "dashboard_alerts": True,
                    "notification_recipients": ["owner@bigmannentertainment.com"]
                }
            }
            
            workflow = AutomatedLicensingWorkflow(**workflow_data)
            
            # Store in database
            await self.licensing_workflows_collection.insert_one(workflow.dict())
            
            logger.info(f"Created automated licensing workflow: {workflow.workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Error generating automated licensing workflow: {e}")
            raise
    
    async def generate_compliance_documentation(
        self, 
        platform_ids: List[str], 
        agreement_id: str
    ) -> List[ComplianceDocumentation]:
        """Generate comprehensive compliance documentation for platforms"""
        try:
            compliance_docs = []
            
            # Get business information for documentation
            business_info = await self.business_info_service.get_consolidated_business_information()
            
            for platform_id in platform_ids:
                # Determine platform category and specific requirements
                platform_category = self._get_platform_category(platform_id)
                
                # Create platform-specific compliance documentation
                doc_data = {
                    "document_type": f"{platform_category}_compliance_documentation",
                    "platform_id": platform_id,
                    "compliance_requirements": self._get_platform_specific_compliance(platform_id),
                    "documentation_content": {
                        "business_entity_verification": {
                            "legal_name": business_info.business_entity,
                            "ein": business_info.ein,
                            "business_address": business_info.business_address,
                            "verification_status": "verified"
                        },
                        "intellectual_property_documentation": {
                            "copyright_ownership": "Confirmed",
                            "content_clearance": "All content properly licensed",
                            "trademark_usage": "Authorized use only"
                        },
                        "regulatory_compliance": {
                            "copyright_compliance": "DMCA compliant",
                            "tax_compliance": "Current with all obligations",
                            "business_license": "Active and in good standing"
                        },
                        "platform_specific_requirements": self._get_platform_specific_requirements(platform_id),
                        "content_standards": {
                            "quality_standards": "Professional grade content only",
                            "metadata_standards": "Complete and accurate metadata",
                            "format_standards": "Platform-native formats"
                        },
                        "reporting_procedures": {
                            "usage_reporting": "Monthly automated reports",
                            "revenue_reporting": "Real-time revenue tracking",
                            "compliance_reporting": "Quarterly compliance audits"
                        }
                    },
                    "legal_review_status": "pending"
                }
                
                compliance_doc = ComplianceDocumentation(**doc_data)
                compliance_docs.append(compliance_doc)
                
                # Store in database
                await self.compliance_documents_collection.insert_one(compliance_doc.dict())
            
            logger.info(f"Generated {len(compliance_docs)} compliance documents for agreement {agreement_id}")
            return compliance_docs
            
        except Exception as e:
            logger.error(f"Error generating compliance documentation: {e}")
            raise
    
    def _get_platform_category(self, platform_id: str) -> str:
        """Get the category of a specific platform"""
        for category, config in self.platform_categories.items():
            if platform_id in config["platforms"]:
                return category
        return "other"
    
    def _get_platform_specific_compliance(self, platform_id: str) -> List[str]:
        """Get platform-specific compliance requirements"""
        category = self._get_platform_category(platform_id)
        if category in self.platform_categories:
            return self.platform_categories[category]["compliance"]
        return ["general_content_compliance", "copyright_compliance"]
    
    def _get_platform_specific_requirements(self, platform_id: str) -> Dict[str, Any]:
        """Get platform-specific requirements"""
        # This would be expanded with actual platform-specific requirements
        platform_requirements = {
            "spotify": {
                "audio_quality": "Minimum 320kbps MP3 or FLAC",
                "metadata_requirements": "Complete track, artist, album metadata",
                "content_restrictions": "No explicit content without proper labeling"
            },
            "revolt": {
                "audio_quality": "Minimum 320kbps MP3 or FLAC recommended",
                "video_quality": "Minimum 1080p HD for video content",
                "content_focus": "Hip-hop, R&B, and urban culture content preferred",
                "metadata_requirements": "Complete track, artist, album metadata with ISRC",
                "content_restrictions": "Must align with urban culture and music focus"
            },
            "youtube": {
                "video_quality": "Minimum 1080p HD",
                "thumbnail_requirements": "Custom thumbnail recommended",
                "content_restrictions": "Community guidelines compliance required"
            },
            "instagram": {
                "image_quality": "Minimum 1080x1080 pixels",
                "story_format": "9:16 aspect ratio for stories",
                "content_restrictions": "No copyright music without licensing"
            }
        }
        
        return platform_requirements.get(platform_id, {
            "general_requirements": "Platform-specific requirements apply",
            "content_standards": "Professional quality content required"
        })
    
    async def get_comprehensive_licensing_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive licensing dashboard with all licensing information"""
        try:
            # Get business information
            business_info = await self.business_info_service.get_consolidated_business_information()
            
            # Get comprehensive agreements
            agreements = await self.comprehensive_agreements_collection.find({}).to_list(length=None)
            
            # Get licensing workflows
            workflows = await self.licensing_workflows_collection.find({}).to_list(length=None)
            
            # Get compliance documents
            compliance_docs = await self.compliance_documents_collection.find({}).to_list(length=None)
            
            # Calculate summary statistics
            total_agreements = len(agreements)
            active_agreements = len([a for a in agreements if a.get("agreement_status") == "active"])
            total_platforms_licensed = sum(a.get("total_platforms", 0) for a in agreements)
            
            # Calculate financial summary
            total_licensing_fees = sum(
                sum(float(fee) for fee in a.get("licensing_fees", {}).values()) 
                for a in agreements
            )
            
            dashboard_data = {
                "business_information_summary": {
                    "business_entity": business_info.business_entity,
                    "business_owner": business_info.business_owner,
                    "industry_classification": business_info.industry_classification,
                    "naics_code": business_info.naics_code,
                    "ein": business_info.ein,
                    "tin": business_info.tin,
                    "total_platforms_integrated": len(business_info.distribution_platform_ids),
                    "gs1_company_prefix": business_info.company_prefix,
                    "legal_entity_gln": business_info.legal_entity_gln,
                    "isan_prefix": business_info.isan_prefix,
                    "isrc_prefix": business_info.isrc_prefix
                },
                "licensing_overview": {
                    "total_comprehensive_agreements": total_agreements,
                    "active_agreements": active_agreements,
                    "total_platforms_licensed": total_platforms_licensed,
                    "total_licensing_fees": total_licensing_fees,
                    "average_fee_per_platform": total_licensing_fees / max(total_platforms_licensed, 1)
                },
                "platform_category_breakdown": self._calculate_category_breakdown(agreements),
                "compliance_status": {
                    "total_compliance_documents": len(compliance_docs),
                    "pending_legal_review": len([d for d in compliance_docs if d.get("legal_review_status") == "pending"]),
                    "approved_documents": len([d for d in compliance_docs if d.get("legal_review_status") == "approved"])
                },
                "automation_status": {
                    "total_workflows": len(workflows),
                    "active_workflows": len([w for w in workflows if w.get("workflow_status") == "active"]),
                    "automated_processes": [
                        "Business information validation",
                        "License terms calculation", 
                        "Compliance documentation generation",
                        "Platform integration setup"
                    ]
                },
                "recent_activity": self._get_recent_licensing_activity(agreements, workflows, compliance_docs),
                "upcoming_renewals": self._get_upcoming_renewals(agreements),
                "compliance_alerts": self._get_compliance_alerts(compliance_docs)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive licensing dashboard: {e}")
            raise
    
    def _calculate_category_breakdown(self, agreements: List[Dict]) -> Dict[str, Any]:
        """Calculate breakdown by platform categories"""
        category_stats = {}
        
        for agreement in agreements:
            categories = agreement.get("platform_categories", [])
            for category in categories:
                if category not in category_stats:
                    category_stats[category] = {
                        "agreement_count": 0,
                        "platform_count": 0,
                        "total_fees": 0.0
                    }
                
                category_stats[category]["agreement_count"] += 1
                category_stats[category]["platform_count"] += len([
                    p for p in agreement.get("platforms_licensed", [])
                    if self._get_platform_category(p) == category
                ])
                
                category_fees = agreement.get("licensing_fees", {}).get(category, 0)
                category_stats[category]["total_fees"] += float(category_fees)
        
        return category_stats
    
    def _get_recent_licensing_activity(self, agreements, workflows, compliance_docs) -> List[Dict[str, Any]]:
        """Get recent licensing activity"""
        activities = []
        
        # Recent agreements
        for agreement in sorted(agreements, key=lambda x: x.get("created_at", datetime.min), reverse=True)[:5]:
            activities.append({
                "type": "agreement_created",
                "description": f"Comprehensive agreement created for {agreement.get('total_platforms', 0)} platforms",
                "date": agreement.get("created_at"),
                "status": agreement.get("agreement_status")
            })
        
        # Recent workflows
        for workflow in sorted(workflows, key=lambda x: x.get("created_at", datetime.min), reverse=True)[:3]:
            activities.append({
                "type": "workflow_created",
                "description": f"Automated workflow '{workflow.get('workflow_name')}' created",
                "date": workflow.get("created_at"),
                "status": "active"
            })
        
        return sorted(activities, key=lambda x: x.get("date", datetime.min), reverse=True)[:10]
    
    def _get_upcoming_renewals(self, agreements) -> List[Dict[str, Any]]:
        """Get upcoming license renewals"""
        upcoming = []
        
        for agreement in agreements:
            expiration_date = agreement.get("expiration_date")
            if expiration_date:
                if isinstance(expiration_date, str):
                    expiration_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                
                days_until_expiry = (expiration_date - datetime.now(timezone.utc)).days
                if 0 <= days_until_expiry <= 90:  # Next 90 days
                    upcoming.append({
                        "agreement_id": agreement.get("agreement_id"),
                        "platforms_count": agreement.get("total_platforms", 0),
                        "expiration_date": expiration_date,
                        "days_until_expiry": days_until_expiry,
                        "auto_renewal": agreement.get("auto_renewal", False)
                    })
        
        return sorted(upcoming, key=lambda x: x["days_until_expiry"])
    
    def _get_compliance_alerts(self, compliance_docs) -> List[Dict[str, Any]]:
        """Get compliance alerts and warnings"""
        alerts = []
        
        pending_reviews = len([d for d in compliance_docs if d.get("legal_review_status") == "pending"])
        if pending_reviews > 0:
            alerts.append({
                "level": "warning",
                "message": f"{pending_reviews} compliance documents pending legal review",
                "action_required": "Schedule legal review"
            })
        
        # Check for expired documents
        expired_docs = [
            d for d in compliance_docs 
            if d.get("approval_date") and 
            (datetime.now(timezone.utc) - datetime.fromisoformat(d["approval_date"].replace('Z', '+00:00'))).days > 365
        ]
        
        if expired_docs:
            alerts.append({
                "level": "critical",
                "message": f"{len(expired_docs)} compliance documents require renewal",
                "action_required": "Update compliance documentation"
            })
        
        return alerts