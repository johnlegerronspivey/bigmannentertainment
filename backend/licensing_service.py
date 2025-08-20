from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json
from bson import ObjectId
from pymongo import MongoClient
import os

from licensing_models import (
    PlatformLicense, LicensingAgreement, LicenseUsage, 
    ComplianceCheck, PlatformActivation, LicenseStatus, LicenseType,
    StatutoryRate, RoyaltyType, DailyCompensation, CompensationPayout,
    LicenseCompensationSummary
)

class LicensingService:
    def __init__(self):
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        
        # Collections
        self.platform_licenses = self.db.platform_licenses
        self.licensing_agreements = self.db.licensing_agreements
        self.license_usage = self.db.license_usage
        self.compliance_checks = self.db.compliance_checks
        self.platform_activations = self.db.platform_activations
        self.statutory_rates = self.db.statutory_rates
        self.daily_compensations = self.db.daily_compensations
        self.compensation_payouts = self.db.compensation_payouts
        self.compensation_summaries = self.db.compensation_summaries
        
        # Initialize statutory rates if not present
        # self._initialize_statutory_rates()  # Temporarily disabled to fix Decimal encoding issue
        
    def initialize_all_platform_licenses(self, platforms_config: Dict[str, Any]) -> Dict[str, str]:
        """Initialize licenses for all 83+ platforms"""
        created_licenses = {}
        
        # Default licensing configuration for different platform types
        default_configs = {
            "social_media": {
                "license_type": LicenseType.CONTENT_LICENSE,
                "monthly_limit": 1000,
                "revenue_share_percentage": 5.0,
                "compliance_requirements": ["content_guidelines", "community_standards"]
            },
            "streaming": {
                "license_type": LicenseType.DISTRIBUTION_LICENSE,
                "monthly_limit": 500,
                "revenue_share_percentage": 10.0,
                "compliance_requirements": ["content_quality", "metadata_standards"]
            },
            "streaming_tv": {
                "license_type": LicenseType.ENTERPRISE,
                "monthly_limit": 100,
                "revenue_share_percentage": 15.0,
                "compliance_requirements": ["broadcast_standards", "content_rating"]
            },
            "tv": {
                "license_type": LicenseType.ENTERPRISE,
                "monthly_limit": 50,
                "revenue_share_percentage": 20.0,
                "compliance_requirements": ["broadcast_standards", "fcc_compliance"]
            },
            "radio": {
                "license_type": LicenseType.API_LICENSE,
                "monthly_limit": 200,
                "revenue_share_percentage": 8.0,
                "compliance_requirements": ["audio_standards", "licensing_fees"]
            },
            "fm_broadcast": {
                "license_type": LicenseType.DISTRIBUTION_LICENSE,
                "monthly_limit": 100,
                "revenue_share_percentage": 12.0,
                "compliance_requirements": ["fcc_compliance", "broadcast_quality"]
            },
            "podcast": {
                "license_type": LicenseType.CONTENT_LICENSE,
                "monthly_limit": 300,
                "revenue_share_percentage": 7.0,
                "compliance_requirements": ["content_guidelines", "rss_standards"]
            }
        }
        
        for platform_id, platform_config in platforms_config.items():
            platform_type = platform_config.get("type", "social_media")
            default_config = default_configs.get(platform_type, default_configs["social_media"])
            
            license_data = {
                "platform_id": platform_id,
                "platform_name": platform_config.get("name", platform_id.title()),
                "license_type": default_config["license_type"],
                "license_status": LicenseStatus.ACTIVE,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=365),  # 1 year license
                "monthly_limit": default_config["monthly_limit"],
                "revenue_share_percentage": default_config["revenue_share_percentage"],
                "compliance_requirements": default_config["compliance_requirements"],
                "platform_config": {
                    "api_endpoint": platform_config.get("api_endpoint"),
                    "supported_formats": platform_config.get("supported_formats", []),
                    "max_file_size": platform_config.get("max_file_size", 0),
                    "credentials_required": platform_config.get("credentials_required", [])
                },
                "platform_contact": platform_config.get("support_email"),
                "support_email": platform_config.get("support_email")
            }
            
            platform_license = PlatformLicense(**license_data)
            
            # Insert into database
            result = self.platform_licenses.insert_one(platform_license.dict())
            created_licenses[platform_id] = str(result.inserted_id)
            
        return created_licenses
    
    def create_master_licensing_agreement(self, license_ids: List[str]) -> str:
        """Create a master licensing agreement for all platforms"""
        agreement_data = {
            "agreement_name": "Big Mann Entertainment Master Platform Licensing Agreement",
            "platform_licenses": license_ids,
            "agreement_type": "master_agreement",
            "total_platforms": len(license_ids),
            "active_platforms": len(license_ids),
            "master_start_date": datetime.utcnow(),
            "master_end_date": datetime.utcnow() + timedelta(days=365),
            "total_license_fee": len(license_ids) * 99.99,  # $99.99 per platform
            "business_entity": "Big Mann Entertainment",
            "business_owner": "John LeGerron Spivey",
            "business_ein": "270658077",
            "business_tin": "12800",
            "contract_signed": True,
            "legal_representative": "John LeGerron Spivey",
            "compliance_score": 100.0
        }
        
        agreement = LicensingAgreement(**agreement_data)
        result = self.licensing_agreements.insert_one(agreement.dict())
        return str(result.inserted_id)
    
    def activate_platform_license(self, platform_id: str, license_id: str, activated_by: str) -> str:
        """Activate a platform license"""
        activation_data = {
            "platform_id": platform_id,
            "license_id": license_id,
            "is_active": True,
            "activated_by": activated_by,
            "activation_reason": f"Platform {platform_id} licensed and activated for Big Mann Entertainment",
            "platform_settings": {
                "auto_distribution": True,
                "content_moderation": True,
                "analytics_tracking": True,
                "revenue_tracking": True
            },
            "integration_status": "active"
        }
        
        activation = PlatformActivation(**activation_data)
        result = self.platform_activations.insert_one(activation.dict())
        return str(result.inserted_id)
    
    def get_licensing_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive licensing dashboard data"""
        # Platform license summary
        total_licenses = self.platform_licenses.count_documents({})
        active_licenses = self.platform_licenses.count_documents({"license_status": "active"})
        pending_licenses = self.platform_licenses.count_documents({"license_status": "pending"})
        expired_licenses = self.platform_licenses.count_documents({"license_status": "expired"})
        
        # License types breakdown
        license_types = {}
        for license_type in LicenseType:
            count = self.platform_licenses.count_documents({"license_type": license_type})
            license_types[license_type] = count
        
        # Platform categories
        platform_categories = {}
        licenses = self.platform_licenses.find({})
        for license_doc in licenses:
            platform_config = license_doc.get("platform_config", {})
            category = "Unknown"
            
            # Determine category from API endpoint or other indicators
            api_endpoint = platform_config.get("api_endpoint", "")
            if "social" in api_endpoint or "facebook" in api_endpoint or "twitter" in api_endpoint:
                category = "Social Media"
            elif "music" in api_endpoint or "streaming" in api_endpoint:
                category = "Streaming"
            elif "tv" in api_endpoint or "television" in api_endpoint:
                category = "Television"
            elif "radio" in api_endpoint:
                category = "Radio"
                
            platform_categories[category] = platform_categories.get(category, 0) + 1
        
        # Recent activity
        recent_activations = list(self.platform_activations.find({}).sort("activation_date", -1).limit(10))
        
        # Compliance summary
        total_compliance_checks = self.compliance_checks.count_documents({})
        compliant_checks = self.compliance_checks.count_documents({"compliance_status": "compliant"})
        compliance_rate = (compliant_checks / total_compliance_checks * 100) if total_compliance_checks > 0 else 100
        
        return {
            "licensing_overview": {
                "total_platforms_licensed": total_licenses,
                "active_licenses": active_licenses,
                "pending_licenses": pending_licenses,
                "expired_licenses": expired_licenses,
                "licensing_compliance_rate": compliance_rate
            },
            "license_types_breakdown": license_types,
            "platform_categories": platform_categories,
            "recent_activations": [
                {
                    "platform_id": str(act.get("platform_id", "")),
                    "activation_date": act.get("activation_date"),
                    "integration_status": act.get("integration_status", "active")
                } for act in recent_activations
            ],
            "business_info": {
                "business_entity": "Big Mann Entertainment",
                "business_owner": "John LeGerron Spivey", 
                "ein": "270658077",
                "tin": "12800"
            },
            "financial_summary": {
                "total_licensing_fees": total_licenses * 99.99,
                "monthly_recurring_revenue": active_licenses * 8.33,  # $99.99/12 months
                "revenue_share_potential": "Variable based on content performance"
            }
        }
    
    def get_platform_licenses(self, status: Optional[str] = None, category: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get platform licenses with optional filtering"""
        query = {}
        if status:
            query["license_status"] = status
            
        licenses = list(self.platform_licenses.find(query).skip(offset).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for license_doc in licenses:
            license_doc["_id"] = str(license_doc["_id"])
            
        return licenses
    
    def get_licensing_status(self) -> Dict[str, Any]:
        """Get overall licensing system status and health"""
        total_platforms = self.platform_licenses.count_documents({})
        active_licenses = self.platform_licenses.count_documents({"license_status": "active"})
        
        # Calculate health score based on active licenses and compliance
        health_score = (active_licenses / total_platforms * 100) if total_platforms > 0 else 100
        
        # Get compliance rate
        total_compliance_checks = self.compliance_checks.count_documents({})
        compliant_checks = self.compliance_checks.count_documents({"compliance_status": "compliant"})
        compliance_rate = (compliant_checks / total_compliance_checks * 100) if total_compliance_checks > 0 else 100
        
        return {
            "health_score": health_score,
            "total_platforms": total_platforms,
            "active_licenses": active_licenses,
            "compliance_rate": compliance_rate,
            "system_status": "operational" if health_score > 80 else "degraded"
        }
    
    def get_platform_license_details(self, platform_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific platform license"""
        license_doc = self.platform_licenses.find_one({"platform_id": platform_id})
        
        if license_doc:
            license_doc["_id"] = str(license_doc["_id"])
            return license_doc
        
        return None
    
    def check_platform_compliance(self, platform_id: str) -> Dict[str, Any]:
        """Check compliance status for a specific platform"""
        license_doc = self.platform_licenses.find_one({"platform_id": platform_id})
        
        if not license_doc:
            return {"compliant": False, "score": 0, "details": {"error": "License not found"}}
        
        compliance_score = 100
        compliance_details = {}
        recommendations = []
        
        # Check usage limits
        usage_count = license_doc.get("usage_count", 0)
        monthly_limit = license_doc.get("monthly_limit", 1000)
        
        if usage_count > monthly_limit:
            compliance_score -= 30
            compliance_details["usage_violation"] = f"Usage {usage_count} exceeds limit {monthly_limit}"
            recommendations.append("Reduce usage or upgrade license tier")
        
        # Check license expiration
        end_date = license_doc.get("end_date")
        if end_date:
            try:
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                days_until_expiry = (end_date - datetime.utcnow()).days
                if days_until_expiry < 30:
                    compliance_score -= 20
                    compliance_details["expiry_warning"] = f"License expires in {days_until_expiry} days"
                    recommendations.append("Renew license before expiration")
            except (ValueError, TypeError):
                pass
        
        return {
            "compliant": compliance_score >= 80,
            "score": compliance_score,
            "details": compliance_details,
            "recommendations": recommendations
        }
    
    def get_platform_usage_metrics(self, platform_id: str) -> Dict[str, Any]:
        """Get usage metrics for a platform"""
        license_doc = self.platform_licenses.find_one({"platform_id": platform_id})
        
        if not license_doc:
            return {"error": "Platform not found"}
        
        # Get recent usage data
        usage_docs = list(self.license_usage.find({"platform_id": platform_id}).sort("usage_date", -1).limit(30))
        
        total_uploads = sum(doc.get("content_uploads", 0) for doc in usage_docs)
        total_api_calls = sum(doc.get("api_calls", 0) for doc in usage_docs)
        total_revenue = sum(doc.get("revenue_generated", 0) for doc in usage_docs)
        
        return {
            "total_uploads": total_uploads,
            "total_api_calls": total_api_calls,
            "total_revenue": total_revenue,
            "usage_period": "Last 30 days",
            "monthly_limit": license_doc.get("monthly_limit", 1000),
            "usage_percentage": (total_uploads / license_doc.get("monthly_limit", 1000)) * 100
        }
    
    def deactivate_platform_license(self, platform_id: str, deactivated_by: str) -> str:
        """Deactivate a platform license"""
        # Update license status
        self.platform_licenses.update_one(
            {"platform_id": platform_id},
            {"$set": {"license_status": "inactive", "deactivated_date": datetime.utcnow()}}
        )
        
        # Update activation record
        self.platform_activations.update_one(
            {"platform_id": platform_id},
            {"$set": {"is_active": False, "deactivated_by": deactivated_by, "deactivation_date": datetime.utcnow()}}
        )
        
        return f"deactivation_{platform_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def get_licensing_agreements(self, agreement_type: Optional[str] = None, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get licensing agreements with optional filtering"""
        query = {}
        if agreement_type:
            query["agreement_type"] = agreement_type
        if status:
            query["status"] = status
            
        agreements = list(self.licensing_agreements.find(query).skip(offset).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for agreement in agreements:
            agreement["_id"] = str(agreement["_id"])
            
        return agreements
    
    def update_platform_usage(self, platform_id: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update usage metrics for a platform"""
        # Create usage record
        usage = LicenseUsage(
            license_id=f"license_{platform_id}",
            platform_id=platform_id,
            content_uploads=usage_data.get("uploads_count", 0),
            api_calls=usage_data.get("api_calls", 0),
            data_transfer_mb=usage_data.get("bandwidth_used", 0) / 1024 / 1024,  # Convert bytes to MB
            usage_date=datetime.utcnow(),
            reporting_period="daily",
            revenue_generated=usage_data.get("revenue_generated", 0.0)
        )
        
        self.license_usage.insert_one(usage.dict())
        
        # Update the license's usage count
        self.platform_licenses.update_one(
            {"platform_id": platform_id},
            {"$inc": {"usage_count": usage_data.get("uploads_count", 0)}}
        )
        
        return usage_data
    
    def update_license_usage(self, license_id: str, usage_data: Dict[str, Any]) -> bool:
        """Update license usage metrics"""
        usage = LicenseUsage(
            license_id=license_id,
            platform_id=usage_data.get("platform_id"),
            content_uploads=usage_data.get("content_uploads", 0),
            api_calls=usage_data.get("api_calls", 0),
            data_transfer_mb=usage_data.get("data_transfer_mb", 0.0),
            usage_date=datetime.utcnow(),
            reporting_period="daily",
            revenue_generated=usage_data.get("revenue_generated", 0.0)
        )
        
        self.license_usage.insert_one(usage.dict())
        
        # Update the license's usage count
        self.platform_licenses.update_one(
            {"id": license_id},
            {"$inc": {"usage_count": usage_data.get("content_uploads", 0)}}
        )
        
        return True
    
    def check_compliance(self, platform_id: str, license_id: str) -> Dict[str, Any]:
        """Perform compliance check for a platform license"""
        license_doc = self.platform_licenses.find_one({"platform_id": platform_id})
        
        if not license_doc:
            return {"error": "License not found"}
        
        compliance_results = []
        overall_status = "compliant"
        
        # Check usage limits
        if license_doc.get("usage_count", 0) > license_doc.get("monthly_limit", 1000):
            compliance_results.append({
                "check_type": "usage_limits",
                "status": "violation",
                "message": "Monthly usage limit exceeded"
            })
            overall_status = "violation"
        
        # Check license expiration
        end_date = license_doc.get("end_date")
        if end_date and datetime.fromisoformat(end_date.replace('Z', '+00:00')) < datetime.utcnow():
            compliance_results.append({
                "check_type": "license_expiration", 
                "status": "warning",
                "message": "License expired or expiring soon"
            })
            if overall_status == "compliant":
                overall_status = "warning"
        
        # Record compliance check
        compliance_check = ComplianceCheck(
            license_id=license_id,
            platform_id=platform_id,
            check_type="automated_compliance_check",
            compliance_status=overall_status,
            check_description=f"Automated compliance check for {platform_id}"
        )
        
        self.compliance_checks.insert_one(compliance_check.dict())
        
        return {
            "platform_id": platform_id,
            "overall_compliance": overall_status,
            "checks": compliance_results,
            "check_date": datetime.utcnow().isoformat()
        }
    
    def _initialize_statutory_rates(self) -> None:
        """Initialize current statutory rates if not present"""
        if self.statutory_rates.count_documents({}) == 0:
            # 2025 US Statutory Rates (based on CRB rates)
            current_rates = [
                {
                    "royalty_type": RoyaltyType.MECHANICAL,
                    "rate_name": "Digital Mechanical Royalty (2025)",
                    "rate_per_unit": 0.091,  # $0.091 per reproduction/download
                    "minimum_fee": 0.0175,   # $0.0175 minimum per work
                    "effective_date": datetime(2025, 1, 1),
                    "unit_type": "per_reproduction",
                    "rate_source": "CRB",
                    "big_mann_rate_multiplier": 1.0,
                    "auto_apply": True
                },
                {
                    "royalty_type": RoyaltyType.PERFORMANCE,
                    "rate_name": "Digital Performance Royalty (Streaming)",
                    "rate_per_unit": 0.0022,  # $0.0022 per stream
                    "minimum_fee": 0.0001,
                    "effective_date": datetime(2025, 1, 1),
                    "unit_type": "per_stream",
                    "rate_source": "CRB",
                    "big_mann_rate_multiplier": 1.0,
                    "auto_apply": True
                },
                {
                    "royalty_type": RoyaltyType.SYNCHRONIZATION,
                    "rate_name": "Synchronization License Fee",
                    "rate_per_unit": 500.00,  # $500 base sync fee
                    "rate_percentage": 2.5,   # 2.5% of production budget
                    "minimum_fee": 100.00,
                    "effective_date": datetime(2025, 1, 1),
                    "unit_type": "per_usage",
                    "rate_source": "Industry Standard",
                    "big_mann_rate_multiplier": 1.0,
                    "auto_apply": True
                },
                {
                    "royalty_type": RoyaltyType.DIGITAL_PERFORMANCE,
                    "rate_name": "Interactive Streaming Rate",
                    "rate_per_unit": 0.0084,  # $0.0084 per interactive stream
                    "minimum_fee": 0.0001,
                    "effective_date": datetime(2025, 1, 1),
                    "unit_type": "per_stream",
                    "rate_source": "CRB",
                    "big_mann_rate_multiplier": 1.0,
                    "auto_apply": True
                }
            ]
            
            for rate_data in current_rates:
                statutory_rate = StatutoryRate(**rate_data)
                # Convert Decimal fields to float for MongoDB storage
                rate_dict = statutory_rate.dict()
                for key, value in rate_dict.items():
                    if isinstance(value, Decimal):
                        rate_dict[key] = float(value)
                self.statutory_rates.insert_one(rate_dict)
    
    def get_statutory_rates(self, royalty_type: Optional[str] = None, active_only: bool = True) -> List[Dict]:
        """Get current statutory rates"""
        query = {}
        if royalty_type:
            query["royalty_type"] = royalty_type
        if active_only:
            query["effective_date"] = {"$lte": datetime.utcnow()}
            query["$or"] = [
                {"expiration_date": {"$gte": datetime.utcnow()}},
                {"expiration_date": None}
            ]
        
        rates = list(self.statutory_rates.find(query))
        
        # Convert ObjectId and Decimal for JSON serialization
        for rate in rates:
            rate["_id"] = str(rate["_id"])
            if "rate_per_unit" in rate:
                rate["rate_per_unit"] = float(rate["rate_per_unit"])
            if "rate_percentage" in rate and rate["rate_percentage"]:
                rate["rate_percentage"] = float(rate["rate_percentage"])
            if "minimum_fee" in rate:
                rate["minimum_fee"] = float(rate["minimum_fee"])
            if "maximum_fee" in rate and rate["maximum_fee"]:
                rate["maximum_fee"] = float(rate["maximum_fee"])
            if "big_mann_rate_multiplier" in rate:
                rate["big_mann_rate_multiplier"] = float(rate["big_mann_rate_multiplier"])
        
        return rates
    
    def calculate_daily_compensation(self, compensation_date: datetime = None) -> Dict[str, Any]:
        """Calculate daily compensation for all active platforms"""
        if not compensation_date:
            compensation_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all active platform licenses
        active_licenses = list(self.platform_licenses.find({"license_status": "active"}))
        
        total_compensations_calculated = 0
        total_amount_calculated = Decimal('0.00')
        platform_compensations = []
        
        # Get current statutory rates
        statutory_rates = {
            RoyaltyType.MECHANICAL: self.get_current_rate(RoyaltyType.MECHANICAL),
            RoyaltyType.PERFORMANCE: self.get_current_rate(RoyaltyType.PERFORMANCE),
            RoyaltyType.SYNCHRONIZATION: self.get_current_rate(RoyaltyType.SYNCHRONIZATION),
            RoyaltyType.DIGITAL_PERFORMANCE: self.get_current_rate(RoyaltyType.DIGITAL_PERFORMANCE)
        }
        
        for license_doc in active_licenses:
            platform_id = license_doc["platform_id"]
            
            # Get daily usage metrics (mock data for now - would integrate with actual platform APIs)
            usage_metrics = self._get_daily_usage_metrics(platform_id, compensation_date)
            
            # Calculate compensation based on statutory rates
            compensation_data = self._calculate_platform_compensation(
                license_doc, usage_metrics, statutory_rates, compensation_date
            )
            
            # Store daily compensation
            daily_compensation = DailyCompensation(**compensation_data)
            # Convert Decimal fields to float for MongoDB storage
            compensation_dict = daily_compensation.dict()
            for key, value in compensation_dict.items():
                if isinstance(value, Decimal):
                    compensation_dict[key] = float(value)
            self.daily_compensations.insert_one(compensation_dict)
            
            platform_compensations.append(compensation_data)
            total_compensations_calculated += 1
            total_amount_calculated += Decimal(str(compensation_data["total_compensation"]))
        
        return {
            "compensation_date": compensation_date.isoformat(),
            "total_platforms": total_compensations_calculated,
            "total_compensation": float(total_amount_calculated),
            "platform_breakdown": platform_compensations[:10],  # Show first 10
            "statutory_rates_applied": {
                "mechanical": float(statutory_rates[RoyaltyType.MECHANICAL]["rate_per_unit"]) if statutory_rates[RoyaltyType.MECHANICAL] else 0,
                "performance": float(statutory_rates[RoyaltyType.PERFORMANCE]["rate_per_unit"]) if statutory_rates[RoyaltyType.PERFORMANCE] else 0,
                "sync": float(statutory_rates[RoyaltyType.SYNCHRONIZATION]["rate_per_unit"]) if statutory_rates[RoyaltyType.SYNCHRONIZATION] else 0,
                "digital_performance": float(statutory_rates[RoyaltyType.DIGITAL_PERFORMANCE]["rate_per_unit"]) if statutory_rates[RoyaltyType.DIGITAL_PERFORMANCE] else 0
            },
            "calculation_status": "completed",
            "business_entity": "Big Mann Entertainment",
            "business_owner": "John LeGerron Spivey"
        }
    
    def get_current_rate(self, royalty_type: RoyaltyType) -> Optional[Dict]:
        """Get current rate for a specific royalty type"""
        return self.statutory_rates.find_one({
            "royalty_type": royalty_type,
            "effective_date": {"$lte": datetime.utcnow()},
            "$or": [
                {"expiration_date": {"$gte": datetime.utcnow()}},
                {"expiration_date": None}
            ]
        })
    
    def _get_daily_usage_metrics(self, platform_id: str, date: datetime) -> Dict[str, int]:
        """Get daily usage metrics for a platform (mock data for demo)"""
        # In production, this would integrate with platform APIs
        # For now, generate realistic mock data based on platform type
        
        # Mock data based on platform characteristics
        import random
        base_streams = random.randint(100, 10000)
        
        return {
            "total_streams": base_streams,
            "total_downloads": random.randint(10, base_streams // 10),
            "total_views": random.randint(base_streams // 2, base_streams * 2),
            "total_plays": base_streams + random.randint(0, base_streams // 4)
        }
    
    def _calculate_platform_compensation(self, license_doc: Dict, usage_metrics: Dict, 
                                       statutory_rates: Dict, compensation_date: datetime) -> Dict:
        """Calculate compensation for a single platform"""
        platform_id = license_doc["platform_id"]
        platform_name = license_doc.get("platform_name", platform_id)
        
        # Get statutory rates
        mechanical_rate = statutory_rates.get(RoyaltyType.MECHANICAL, {}).get("rate_per_unit", Decimal('0.091'))
        performance_rate = statutory_rates.get(RoyaltyType.PERFORMANCE, {}).get("rate_per_unit", Decimal('0.0022'))
        sync_rate = statutory_rates.get(RoyaltyType.SYNCHRONIZATION, {}).get("rate_per_unit", Decimal('500.00'))
        digital_rate = statutory_rates.get(RoyaltyType.DIGITAL_PERFORMANCE, {}).get("rate_per_unit", Decimal('0.0084'))
        
        # Calculate royalties based on usage
        mechanical_royalties = Decimal(str(usage_metrics["total_downloads"])) * Decimal(str(mechanical_rate))
        performance_royalties = Decimal(str(usage_metrics["total_streams"])) * Decimal(str(performance_rate))
        sync_royalties = Decimal('0.00')  # Sync is negotiated per usage
        digital_performance_royalties = Decimal(str(usage_metrics["total_plays"])) * Decimal(str(digital_rate))
        
        # Calculate gross revenue (estimated)
        gross_revenue = mechanical_royalties + performance_royalties + digital_performance_royalties
        
        # Platform commission (typically 30%)
        platform_commission = gross_revenue * Decimal('0.30')
        net_revenue = gross_revenue - platform_commission
        
        # Big Mann Entertainment compensation breakdown
        # Artist: 50%, Songwriter: 25%, Publisher: 15%, Big Mann: 10%
        artist_compensation = net_revenue * Decimal('0.50')
        songwriter_compensation = net_revenue * Decimal('0.25')
        publisher_compensation = net_revenue * Decimal('0.15')
        big_mann_commission = net_revenue * Decimal('0.10')
        
        total_compensation = artist_compensation + songwriter_compensation + publisher_compensation
        
        return {
            "compensation_date": compensation_date,
            "platform_id": platform_id,
            "license_id": license_doc.get("id", platform_id),
            "platform_name": platform_name,
            "total_streams": usage_metrics["total_streams"],
            "total_downloads": usage_metrics["total_downloads"],
            "total_views": usage_metrics["total_views"],
            "total_plays": usage_metrics["total_plays"],
            "gross_revenue": float(gross_revenue),
            "platform_commission": float(platform_commission),
            "net_revenue": float(net_revenue),
            "mechanical_royalties": float(mechanical_royalties),
            "performance_royalties": float(performance_royalties),
            "sync_royalties": float(sync_royalties),
            "artist_compensation": float(artist_compensation),
            "songwriter_compensation": float(songwriter_compensation),
            "publisher_compensation": float(publisher_compensation),
            "big_mann_commission": float(big_mann_commission),
            "total_compensation": float(total_compensation),
            "payment_status": "pending",
            "statutory_rates_applied": [
                str(rate.get("_id", "")) for rate in statutory_rates.values() if rate
            ],
            "calculation_method": "automated"
        }
    
    def process_daily_payouts(self, payout_date: datetime = None, minimum_amount: Decimal = Decimal('1.00')) -> Dict[str, Any]:
        """Process daily compensation payouts"""
        if not payout_date:
            payout_date = datetime.utcnow()
        
        # Get pending compensations above minimum amount
        pending_compensations = list(self.daily_compensations.find({
            "payment_status": "pending",
            "total_compensation": {"$gte": float(minimum_amount)}
        }))
        
        payouts_processed = []
        total_payout_amount = Decimal('0.00')
        
        # Group compensations by recipient type for batch payouts
        artist_total = Decimal('0.00')
        songwriter_total = Decimal('0.00')
        publisher_total = Decimal('0.00')
        
        compensation_ids = []
        
        for comp in pending_compensations:
            artist_total += Decimal(str(comp.get("artist_compensation", 0)))
            songwriter_total += Decimal(str(comp.get("songwriter_compensation", 0)))
            publisher_total += Decimal(str(comp.get("publisher_compensation", 0)))
            compensation_ids.append(comp["id"])
        
        # Create payouts for each recipient type
        recipients = [
            ("artist", "Big Mann Artists", artist_total),
            ("songwriter", "John LeGerron Spivey", songwriter_total),
            ("publisher", "Big Mann Entertainment Publishing", publisher_total)
        ]
        
        for recipient_type, recipient_name, amount in recipients:
            if amount > minimum_amount:
                payout_data = {
                    "payout_date": payout_date,
                    "recipient_type": recipient_type,
                    "recipient_id": f"{recipient_type}_collective",
                    "recipient_name": recipient_name,
                    "period_start": payout_date - timedelta(days=1),
                    "period_end": payout_date,
                    "compensation_days": compensation_ids,
                    "total_amount": amount,
                    "tax_withholding": amount * Decimal('0.24'),  # 24% withholding
                    "net_payout": amount * Decimal('0.76'),
                    "payment_method": "bank_transfer",
                    "payment_details": {
                        "bank_name": "Big Mann Entertainment Banking",
                        "routing_number": "XXXX-XXXX",
                        "account_type": "business_checking"
                    },
                    "payout_status": "processing",
                    "business_entity": "Big Mann Entertainment",
                    "business_owner": "John LeGerron Spivey",
                    "business_ein": "270658077",
                    "business_tin": "12800"
                }
                
                payout = CompensationPayout(**payout_data)
                result = self.compensation_payouts.insert_one(payout.dict())
                
                payouts_processed.append({
                    "payout_id": str(result.inserted_id),
                    "recipient": recipient_name,
                    "amount": float(amount),
                    "net_payout": float(amount * Decimal('0.76'))
                })
                
                total_payout_amount += amount
        
        # Update compensation records to 'processing'
        self.daily_compensations.update_many(
            {"id": {"$in": compensation_ids}},
            {"$set": {"payment_status": "processing", "payment_date": payout_date}}
        )
        
        return {
            "payout_date": payout_date.isoformat(),
            "total_payouts_processed": len(payouts_processed),
            "total_payout_amount": float(total_payout_amount),
            "payouts": payouts_processed,
            "compensations_processed": len(compensation_ids),
            "minimum_payout_threshold": float(minimum_amount),
            "business_entity": "Big Mann Entertainment",
            "processing_status": "completed"
        }
    
    def get_compensation_dashboard(self, period_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive compensation dashboard"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Get compensation data for period
        compensations = list(self.daily_compensations.find({
            "compensation_date": {"$gte": start_date, "$lte": end_date}
        }))
        
        payouts = list(self.compensation_payouts.find({
            "payout_date": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Calculate totals
        total_compensation = sum(Decimal(str(comp.get("total_compensation", 0))) for comp in compensations)
        total_payouts = sum(Decimal(str(payout.get("total_amount", 0))) for payout in payouts)
        pending_compensation = sum(Decimal(str(comp.get("total_compensation", 0))) 
                                 for comp in compensations if comp.get("payment_status") == "pending")
        
        # Platform performance
        platform_performance = {}
        for comp in compensations:
            platform = comp.get("platform_name", comp.get("platform_id"))
            if platform not in platform_performance:
                platform_performance[platform] = {
                    "total_compensation": Decimal('0.00'),
                    "total_streams": 0,
                    "total_revenue": Decimal('0.00')
                }
            platform_performance[platform]["total_compensation"] += Decimal(str(comp.get("total_compensation", 0)))
            platform_performance[platform]["total_streams"] += comp.get("total_streams", 0)
            platform_performance[platform]["total_revenue"] += Decimal(str(comp.get("gross_revenue", 0)))
        
        # Convert to JSON-serializable format
        platform_performance_json = {}
        for platform, metrics in platform_performance.items():
            platform_performance_json[platform] = {
                "total_compensation": float(metrics["total_compensation"]),
                "total_streams": metrics["total_streams"],
                "total_revenue": float(metrics["total_revenue"])
            }
        
        return {
            "period_summary": {
                "period_days": period_days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_compensation_calculated": float(total_compensation),
                "total_payouts_processed": float(total_payouts),
                "pending_compensation": float(pending_compensation)
            },
            "statutory_rates": {
                "mechanical_rate": 0.091,
                "performance_rate": 0.0022,
                "sync_rate": 500.00,
                "digital_performance_rate": 0.0084
            },
            "compensation_breakdown": {
                "artist_percentage": 50.0,
                "songwriter_percentage": 25.0,
                "publisher_percentage": 15.0,
                "big_mann_commission": 10.0
            },
            "platform_performance": platform_performance_json,
            "recent_payouts": [
                {
                    "payout_id": str(payout.get("_id", "")),
                    "recipient": payout.get("recipient_name"),
                    "amount": float(payout.get("total_amount", 0)),
                    "status": payout.get("payout_status"),
                    "date": payout.get("payout_date")
                } for payout in payouts[-10:]  # Last 10 payouts
            ],
            "business_info": {
                "business_entity": "Big Mann Entertainment",
                "business_owner": "John LeGerron Spivey",
                "ein": "270658077",
                "tin": "12800"
            }
        }