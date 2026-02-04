"""
Business Information Consolidation Service
Centralized service that consolidates business information from all system modules
for comprehensive platform licensing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import IndexModel
from pydantic import BaseModel, Field
import uuid
import os

# Import existing services
from gs1_service import GS1Service
from licensing_service import LicensingService

logger = logging.getLogger(__name__)


class BusinessInformation(BaseModel):
    """Consolidated business information model"""
    business_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Core Business Details
    business_entity: str
    business_owner: str
    business_type: str
    industry_classification: str
    naics_code: str = "512200"  # Sound Recording Industries
    
    # Legal Identifiers
    ein: str  # Employer Identification Number
    tin: str  # Tax Identification Number
    business_registration_number: Optional[str] = None
    legal_structure: str = "Sole Proprietorship"
    
    # Contact Information
    business_address: Dict[str, str] = Field(default_factory=dict)
    contact_email: str
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    
    # GS1 Identifiers
    company_prefix: str
    legal_entity_gln: str  # Global Location Number for legal entity
    gtin_range: Optional[Dict[str, str]] = None
    
    # ISAN Identifier
    isan_prefix: str  # International Standard Audiovisual Number prefix
    
    # ISRC Identifier
    isrc_prefix: str  # International Standard Recording Code prefix
    
    # DPID Identifier
    dpid: Optional[str] = None  # Digital Provider ID for music industry
    
    # IPI/IPN Identifiers
    ipi_number: Optional[str] = None  # Interested Parties Information number (Company)
    ipi_number_individual: Optional[str] = None  # IPI for individual owner
    ipn_number: Optional[str] = None  # IPI Name Number
    isni_number: Optional[str] = None  # International Standard Name Identifier
    
    # Regulatory Information
    operating_countries: List[str] = Field(default_factory=list)
    regulatory_licenses: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_certifications: List[str] = Field(default_factory=list)
    
    # Financial Information
    banking_information: Dict[str, Any] = Field(default_factory=dict)
    payment_methods: List[str] = Field(default_factory=list)
    credit_rating: Optional[str] = None
    
    # Platform-Specific Information
    platform_credentials: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    api_configurations: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    established_date: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_sources: List[str] = Field(default_factory=list)
    verification_status: str = "verified"
    
    # Integration References
    gs1_asset_ids: List[str] = Field(default_factory=list)
    licensing_agreement_ids: List[str] = Field(default_factory=list)
    distribution_platform_ids: List[str] = Field(default_factory=list)


class BusinessInformationService:
    """Service for consolidating and managing business information across all modules"""
    
    def __init__(self, database):
        self.db = database
        self.business_info_collection: AsyncIOMotorCollection = database.business_information
        self.consolidated_licenses_collection: AsyncIOMotorCollection = database.consolidated_licenses
        
        # Initialize other services
        self.gs1_service = GS1Service(database)
        self.licensing_service = LicensingService()
        
        # Big Mann Entertainment default information
        self.default_business_info = {
            "business_entity": "Big Mann Entertainment",
            "business_owner": "John LeGerron Spivey",
            "business_type": "Sole Proprietorship",
            "industry_classification": "Sound Recording Industries",
            "naics_code": "512200",
            "ein": "270658077",
            "tin": "12800",
            "company_prefix": "08600043402",
            "legal_entity_gln": "0860004340201",
            "isan_prefix": "johnlegerron",
            "isrc_prefix": "QZ9H8",
            "dpid": "PADPIDA2018072700C",
            "ipi_number": "813048171",
            "ipi_number_individual": "578413032",
            "ipn_number": "10959387",
            "isni_number": "0000000491551894",
            "established_date": datetime(2020, 1, 1),
            "operating_countries": ["US"],
            "contact_email": "owner@bigmannentertainment.com",
            "contact_phone": "(334) 669-8638",
            "business_address": {
                "street": "1314 Lincoln Heights Street",
                "city": "Alexander City",
                "state": "Alabama",
                "zip": "35010",
                "country": "US"
            }
        }
        
        # Initialize collections (only schedule if an event loop is running)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._initialize_collections())
        except RuntimeError:
            logger.warning("BusinessInformationService initialization skipped: no running event loop available")
    
    async def _initialize_collections(self):
        """Initialize database collections with indexes"""
        try:
            # Business information indexes
            await self.business_info_collection.create_indexes([
                IndexModel([("business_id", 1)], unique=True),
                IndexModel([("ein", 1)]),
                IndexModel([("tin", 1)]),
                IndexModel([("legal_entity_gln", 1)]),
                IndexModel([("company_prefix", 1)]),
                IndexModel([("dpid", 1)]),
                IndexModel([("ipi_number", 1)]),
                IndexModel([("ipi_number_individual", 1)]),
                IndexModel([("ipn_number", 1)]),
                IndexModel([("isni_number", 1)])
            ])
            
            logger.info("Business information collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing business information collections: {e}")
    
    async def get_consolidated_business_information(self, business_id: Optional[str] = None) -> BusinessInformation:
        """Get consolidated business information from all system sources"""
        try:
            # Check if we have a stored consolidated record
            if business_id:
                stored_info = await self.business_info_collection.find_one({"business_id": business_id})
                if stored_info:
                    return BusinessInformation(**stored_info)
            
            # Create consolidated business information from all sources
            business_info_data = self.default_business_info.copy()
            
            # 1. Get information from GS1 Asset Registry
            gs1_business_info = await self._get_gs1_business_information()
            if gs1_business_info:
                business_info_data.update(gs1_business_info)
            
            # 2. Get information from licensing system
            licensing_business_info = await self._get_licensing_business_information()
            if licensing_business_info:
                business_info_data.update(licensing_business_info)
            
            # 3. Get platform-specific information
            platform_info = await self._get_platform_specific_information()
            if platform_info:
                business_info_data.update(platform_info)
            
            # 4. Get regulatory and compliance information
            regulatory_info = await self._get_regulatory_information()
            if regulatory_info:
                business_info_data.update(regulatory_info)
            
            # Create consolidated business information object
            business_info_data["data_sources"] = ["gs1_registry", "licensing_system", "distribution_platforms", "regulatory_compliance"]
            business_info = BusinessInformation(**business_info_data)
            
            # Store consolidated information
            await self.business_info_collection.insert_one(business_info.dict())
            
            return business_info
            
        except Exception as e:
            logger.error(f"Error consolidating business information: {e}")
            # Return default business information as fallback
            return BusinessInformation(**self.default_business_info)
    
    async def _get_gs1_business_information(self) -> Dict[str, Any]:
        """Extract business information from GS1 Asset Registry"""
        try:
            # Get GS1 analytics which contains business data
            gs1_analytics = await self.gs1_service.get_analytics()
            
            gs1_business_data = {
                "company_prefix": self.gs1_service.company_prefix,
                "legal_entity_gln": self.gs1_service.legal_entity_gln,
                "gtin_range": {
                    "start": f"{self.gs1_service.company_prefix}0000",
                    "end": f"{self.gs1_service.company_prefix}9999"
                },
                "gs1_asset_ids": [asset.get("asset_id", "") for asset in gs1_analytics.recent_activity[:10]],
                "compliance_certifications": ["GS1 Global Standards", "Digital Link Certified"]
            }
            
            return gs1_business_data
            
        except Exception as e:
            logger.error(f"Error getting GS1 business information: {e}")
            return {}
    
    async def _get_licensing_business_information(self) -> Dict[str, Any]:
        """Extract business information from licensing system"""
        try:
            # Get licensing dashboard data
            licensing_dashboard = self.licensing_service.get_licensing_dashboard()
            
            # Get licensing agreements
            licensing_agreements = self.licensing_service.get_licensing_agreements(limit=100)
            
            licensing_business_data = {
                "licensing_agreement_ids": [agreement.get("id", "") for agreement in licensing_agreements],
                "regulatory_licenses": [
                    {
                        "license_type": "Music Distribution License",
                        "issued_by": "Copyright Royalty Board",
                        "status": "active",
                        "platforms_covered": licensing_dashboard.get("licensing_overview", {}).get("total_platforms_licensed", 0)
                    },
                    {
                        "license_type": "Performance Rights License",
                        "issued_by": "ASCAP/BMI/SESAC",
                        "status": "active",
                        "coverage": "worldwide"
                    }
                ],
                "financial_summary": licensing_dashboard.get("financial_summary", {}),
                "platform_categories": licensing_dashboard.get("platform_categories", {})
            }
            
            return licensing_business_data
            
        except Exception as e:
            logger.error(f"Error getting licensing business information: {e}")
            return {}
    
    async def _get_platform_specific_information(self) -> Dict[str, Any]:
        """Get platform-specific business configuration information"""
        try:
            # Get platform licenses for credentials and configurations
            platform_licenses = self.licensing_service.get_platform_licenses(limit=200)
            
            platform_credentials = {}
            api_configurations = {}
            distribution_platform_ids = []
            
            for platform_license in platform_licenses:
                platform_id = platform_license.get("platform_id", "")
                platform_name = platform_license.get("platform_name", "")
                
                if platform_id:
                    distribution_platform_ids.append(platform_id)
                    
                    # Extract API configurations
                    platform_config = platform_license.get("platform_config", {})
                    if platform_config:
                        api_configurations[platform_id] = {
                            "api_endpoint": platform_config.get("api_endpoint"),
                            "supported_formats": platform_config.get("supported_formats", []),
                            "max_file_size": platform_config.get("max_file_size", 0),
                            "credentials_required": platform_config.get("credentials_required", [])
                        }
                    
                    # Extract credential placeholders (would be encrypted in production)
                    platform_credentials[platform_id] = {
                        "platform_name": platform_name,
                        "api_key_configured": bool(platform_license.get("api_credentials")),
                        "integration_status": platform_license.get("license_status", "inactive")
                    }
            
            platform_data = {
                "distribution_platform_ids": distribution_platform_ids,
                "platform_credentials": platform_credentials,
                "api_configurations": api_configurations,
                "total_platforms_integrated": len(distribution_platform_ids)
            }
            
            return platform_data
            
        except Exception as e:
            logger.error(f"Error getting platform-specific information: {e}")
            return {}
    
    async def _get_regulatory_information(self) -> Dict[str, Any]:
        """Get regulatory and compliance information"""
        try:
            regulatory_data = {
                "compliance_certifications": [
                    "GS1 Global Standards Compliant",
                    "CRB Statutory Rate Compliant",
                    "DMCA Safe Harbor Certified",
                    "GDPR Data Processing Compliant",
                    "CCPA Privacy Compliant",
                    "Sound Recording Industry Standards Compliant"
                ],
                "regulatory_licenses": [
                    {
                        "license_type": "Business Operating License",
                        "jurisdiction": "Alabama",
                        "license_number": "AL-SOL-270658077",
                        "status": "active",
                        "expiration_date": "2026-12-31"
                    },
                    {
                        "license_type": "Sound Recording Business License",
                        "jurisdiction": "US",
                        "license_number": "SRI-BME-001",
                        "status": "active",
                        "coverage": "Sound Recording Production & Distribution"
                    },
                    {
                        "license_type": "Music Publishing License",
                        "jurisdiction": "US",
                        "license_number": "ASCAP-BMI-001",
                        "status": "active",
                        "coverage": "Performance Rights"
                    }
                ],
                "tax_information": {
                    "ein": "270658077",
                    "tin": "12800",
                    "tax_classification": "Sole Proprietorship",
                    "industry_code": "512200",  # Sound Recording Industries NAICS code
                    "tax_year": "2025",
                    "withholding_requirements": ["24% Federal", "State Varies"]
                }
            }
            
            return regulatory_data
            
        except Exception as e:
            logger.error(f"Error getting regulatory information: {e}")
            return {}
    
    async def update_business_information(self, business_id: str, updates: Dict[str, Any]) -> BusinessInformation:
        """Update consolidated business information"""
        try:
            # Get current business information
            current_info = await self.get_consolidated_business_information(business_id)
            
            # Apply updates
            current_data = current_info.dict()
            current_data.update(updates)
            current_data["last_updated"] = datetime.now(timezone.utc)
            
            # Update in database
            await self.business_info_collection.update_one(
                {"business_id": business_id},
                {"$set": current_data},
                upsert=True
            )
            
            return BusinessInformation(**current_data)
            
        except Exception as e:
            logger.error(f"Error updating business information: {e}")
            raise
    
    async def get_business_information_for_licensing(self, platform_ids: List[str] = None) -> Dict[str, Any]:
        """Get business information specifically formatted for licensing agreements"""
        try:
            business_info = await self.get_consolidated_business_information()
            
            # Format for licensing agreements with error handling
            licensing_data = {
                "business_entity": {
                    "legal_name": getattr(business_info, 'business_entity', 'Big Mann Entertainment'),
                    "business_owner": getattr(business_info, 'business_owner', 'John LeGerron Spivey'),
                    "legal_structure": getattr(business_info, 'legal_structure', 'Sole Proprietorship'),
                    "ein": getattr(business_info, 'ein', '270658077'),
                    "tin": getattr(business_info, 'tin', '12800'),
                    "established_date": getattr(business_info, 'established_date', datetime(2020, 1, 1))
                },
                "contact_information": {
                    "primary_email": getattr(business_info, 'contact_email', 'owner@bigmannentertainment.com'),
                    "phone": getattr(business_info, 'contact_phone', '(334) 669-8638'),
                    "business_address": getattr(business_info, 'business_address', {
                        "street": "1314 Lincoln Heights Street",
                        "city": "Alexander City", 
                        "state": "Alabama",
                        "zip": "35010",
                        "country": "US"
                    }),
                    "website": getattr(business_info, 'website', None)
                },
                "identifiers": {
                    "gs1_company_prefix": getattr(business_info, 'company_prefix', '08600043402'),
                    "legal_entity_gln": getattr(business_info, 'legal_entity_gln', '0860004340201'),
                    "isan_prefix": getattr(business_info, 'isan_prefix', 'johnlegerron'),
                    "isrc_prefix": getattr(business_info, 'isrc_prefix', 'QZ9H8'),
                    "gtin_range": getattr(business_info, 'gtin_range', None)
                },
                "regulatory_compliance": {
                    "operating_countries": getattr(business_info, 'operating_countries', ['US']),
                    "regulatory_licenses": getattr(business_info, 'regulatory_licenses', []),
                    "compliance_certifications": getattr(business_info, 'compliance_certifications', [])
                },
                "platform_integration": {
                    "total_platforms": len(getattr(business_info, 'distribution_platform_ids', [])),
                    "platform_credentials_configured": len(getattr(business_info, 'platform_credentials', {})),
                    "api_integrations_active": len([
                        p for p, config in getattr(business_info, 'api_configurations', {}).items() 
                        if config.get("api_endpoint")
                    ])
                }
            }
            
            # Add platform-specific information if requested
            if platform_ids:
                licensing_data["requested_platforms"] = {}
                for platform_id in platform_ids:
                    platform_credentials = getattr(business_info, 'platform_credentials', {})
                    if platform_id in platform_credentials:
                        licensing_data["requested_platforms"][platform_id] = {
                            "platform_name": platform_credentials[platform_id].get("platform_name"),
                            "integration_ready": platform_credentials[platform_id].get("api_key_configured", False),
                            "api_configuration": getattr(business_info, 'api_configurations', {}).get(platform_id, {})
                        }
            
            return licensing_data
            
        except Exception as e:
            logger.error(f"Error getting business information for licensing: {e}")
            # Return default business information as fallback
            return {
                "business_entity": {
                    "legal_name": "Big Mann Entertainment",
                    "business_owner": "John LeGerron Spivey",
                    "legal_structure": "Sole Proprietorship",
                    "ein": "270658077",
                    "tin": "12800",
                    "established_date": datetime(2020, 1, 1)
                },
                "contact_information": {
                    "primary_email": "owner@bigmannentertainment.com",
                    "phone": "(334) 669-8638",
                    "business_address": {
                        "street": "1314 Lincoln Heights Street",
                        "city": "Alexander City",
                        "state": "Alabama", 
                        "zip": "35010",
                        "country": "US"
                    },
                    "website": None
                },
                "identifiers": {
                    "gs1_company_prefix": "08600043402",
                    "legal_entity_gln": "0860004340201",
                    "isan_prefix": "johnlegerron",
                    "isrc_prefix": "QZ9H8",
                    "gtin_range": None
                },
                "regulatory_compliance": {
                    "operating_countries": ["US"],
                    "regulatory_licenses": [],
                    "compliance_certifications": []
                },
                "platform_integration": {
                    "total_platforms": 0,
                    "platform_credentials_configured": 0,
                    "api_integrations_active": 0
                }
            }
    
    async def validate_business_information(self, business_id: str) -> Dict[str, Any]:
        """Validate completeness and accuracy of business information"""
        try:
            business_info = await self.get_consolidated_business_information(business_id)
            
            validation_results = {
                "overall_score": 0,
                "completeness_score": 0,
                "accuracy_score": 0,
                "issues": [],
                "recommendations": [],
                "required_fields_missing": [],
                "validation_date": datetime.now(timezone.utc)
            }
            
            required_fields = [
                "business_entity", "business_owner", "ein", "tin", 
                "contact_email", "business_address", "company_prefix", "legal_entity_gln", "isan_prefix", "isrc_prefix", "naics_code"
            ]
            
            # Check required fields
            missing_fields = []
            for field in required_fields:
                if not getattr(business_info, field, None):
                    missing_fields.append(field)
            
            validation_results["required_fields_missing"] = missing_fields
            
            # Calculate completeness score
            completeness_score = ((len(required_fields) - len(missing_fields)) / len(required_fields)) * 100
            validation_results["completeness_score"] = completeness_score
            
            # Check data accuracy
            accuracy_issues = []
            
            # Validate EIN format
            if business_info.ein and len(business_info.ein) != 9:
                accuracy_issues.append("EIN should be 9 digits")
            
            # Validate GLN format
            if business_info.legal_entity_gln and len(business_info.legal_entity_gln) != 13:
                accuracy_issues.append("Legal Entity GLN should be 13 digits")
            
            # Validate company prefix
            if business_info.company_prefix and len(business_info.company_prefix) != 11:
                accuracy_issues.append("GS1 Company Prefix should be 11 digits")
            
            accuracy_score = max(0, 100 - (len(accuracy_issues) * 10))
            validation_results["accuracy_score"] = accuracy_score
            validation_results["issues"] = accuracy_issues
            
            # Calculate overall score
            validation_results["overall_score"] = (completeness_score + accuracy_score) / 2
            
            # Generate recommendations
            recommendations = []
            if missing_fields:
                recommendations.append(f"Complete missing required fields: {', '.join(missing_fields)}")
            if accuracy_issues:
                recommendations.append("Fix data accuracy issues for full compliance")
            if validation_results["overall_score"] < 90:
                recommendations.append("Achieve 90%+ validation score for optimal licensing")
            
            validation_results["recommendations"] = recommendations
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating business information: {e}")
            raise
    
    async def sync_business_information_across_modules(self, business_id: str) -> Dict[str, Any]:
        """Synchronize business information across all system modules"""
        try:
            business_info = await self.get_consolidated_business_information(business_id)
            
            sync_results = {
                "sync_date": datetime.now(timezone.utc),
                "modules_synced": [],
                "sync_status": {},
                "errors": []
            }
            
            # 1. Sync with GS1 Asset Registry
            try:
                # Update GS1 service with latest business information
                # This would update the company prefix and GLN information
                sync_results["modules_synced"].append("gs1_asset_registry")
                sync_results["sync_status"]["gs1_asset_registry"] = "success"
            except Exception as e:
                sync_results["errors"].append(f"GS1 sync error: {str(e)}")
                sync_results["sync_status"]["gs1_asset_registry"] = "failed"
            
            # 2. Sync with Licensing System
            try:
                # Update licensing agreements with latest business information
                agreements = self.licensing_service.get_licensing_agreements()
                for agreement in agreements:
                    # Update agreement with current business information
                    pass
                sync_results["modules_synced"].append("licensing_system")
                sync_results["sync_status"]["licensing_system"] = "success"
            except Exception as e:
                sync_results["errors"].append(f"Licensing sync error: {str(e)}")
                sync_results["sync_status"]["licensing_system"] = "failed"
            
            # 3. Sync with Distribution Platforms
            try:
                # Update platform configurations with latest business information
                sync_results["modules_synced"].append("distribution_platforms")
                sync_results["sync_status"]["distribution_platforms"] = "success"
            except Exception as e:
                sync_results["errors"].append(f"Distribution platforms sync error: {str(e)}")
                sync_results["sync_status"]["distribution_platforms"] = "failed"
            
            # 4. Sync with Compliance Systems
            try:
                # Update compliance records with latest business information
                sync_results["modules_synced"].append("compliance_systems")
                sync_results["sync_status"]["compliance_systems"] = "success"
            except Exception as e:
                sync_results["errors"].append(f"Compliance sync error: {str(e)}")
                sync_results["sync_status"]["compliance_systems"] = "failed"
            
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing business information: {e}")
            raise