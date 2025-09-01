"""
Rights & Compliance Service
Handles territory rights validation, usage rights checking, and embargo logic
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
import logging
from collections import defaultdict

from rights_models import (
    TerritoryCode, UsageRightType, RightsStatus, ComplianceStatus,
    EmbargoType, TerritoryRights, UsageRights, EmbargoRestriction,
    ComplianceRule, RightsOwnership, ComplianceCheckResult,
    RightsValidationConfig, TerritoryMapping, TERRITORY_MAPPINGS,
    UsageRightTemplate, STANDARD_USAGE_TEMPLATES, RightsAuditLog
)

logger = logging.getLogger(__name__)

class RightsComplianceService:
    """Service for rights validation and compliance checking"""
    
    def __init__(self, mongo_db=None):
        self.mongo_db = mongo_db
        self.territory_mappings = TERRITORY_MAPPINGS
        self.usage_templates = STANDARD_USAGE_TEMPLATES
        
        # Initialize compliance rules
        self.compliance_rules = self._load_default_compliance_rules()
        
    def _load_default_compliance_rules(self) -> List[ComplianceRule]:
        """Load default compliance rules"""
        
        rules = [
            # US Compliance Rules
            ComplianceRule(
                rule_name="US DMCA Compliance",
                rule_description="Digital Millennium Copyright Act compliance for US streaming",
                territories=[TerritoryCode.US],
                usage_types=[UsageRightType.STREAMING, UsageRightType.DOWNLOAD],
                required_fields=["title", "artist", "isrc", "rights_holders"],
                validation_logic={
                    "copyright_notice_required": True,
                    "takedown_policy_required": True,
                    "user_generated_content_filtering": True
                },
                severity="error"
            ),
            
            # EU Compliance Rules
            ComplianceRule(
                rule_name="EU DSM Directive Compliance",
                rule_description="Digital Single Market Directive compliance",
                territories=[TerritoryCode.EU],
                usage_types=[UsageRightType.STREAMING, UsageRightType.DOWNLOAD, 
                           UsageRightType.PUBLIC_PERFORMANCE],
                required_fields=["title", "artist", "isrc", "rights_holders", 
                               "publisher_name", "composer_name"],
                validation_logic={
                    "content_recognition_required": True,
                    "rightsholder_notification": True,
                    "revenue_sharing_required": True,
                    "collective_licensing_preferred": True
                },
                severity="error"
            ),
            
            # Global Sync Rights Rules
            ComplianceRule(
                rule_name="Synchronization Rights Verification",
                rule_description="Master and publishing sync rights verification",
                territories=[TerritoryCode.GLOBAL],
                usage_types=[UsageRightType.SYNC],
                required_fields=["title", "artist", "isrc", "master_owner", 
                               "publishing_owner", "duration"],
                validation_logic={
                    "master_clearance_required": True,
                    "publishing_clearance_required": True,
                    "territory_restrictions_check": True,
                    "usage_period_defined": True
                },
                severity="error"
            ),
            
            # Broadcasting Rules
            ComplianceRule(
                rule_name="Broadcast Performance Rights",
                rule_description="Radio and TV performance rights verification",
                territories=[TerritoryCode.US, TerritoryCode.EU, TerritoryCode.GLOBAL],
                usage_types=[UsageRightType.RADIO, UsageRightType.TV, 
                           UsageRightType.PUBLIC_PERFORMANCE],
                required_fields=["title", "artist", "publisher_name", "composer_name"],
                validation_logic={
                    "pro_registration_required": True,
                    "cue_sheet_data_complete": True,
                    "performance_tracking_enabled": True
                },
                severity="warning"
            )
        ]
        
        return rules
    
    async def check_rights_compliance(self, content_id: str, isrc: Optional[str] = None,
                                    territories: List[TerritoryCode] = None,
                                    usage_types: List[UsageRightType] = None,
                                    config: Optional[RightsValidationConfig] = None,
                                    checked_by: str = "system") -> ComplianceCheckResult:
        """Comprehensive rights compliance check"""
        
        start_time = datetime.now()
        
        # Set defaults
        if not territories:
            territories = [TerritoryCode.US]
        if not usage_types:
            usage_types = [UsageRightType.STREAMING]
        if not config:
            config = RightsValidationConfig()
        
        # Initialize result
        result = ComplianceCheckResult(
            content_id=content_id,
            isrc=isrc,
            requested_territories=territories,
            requested_usage_types=usage_types,
            checked_by=checked_by,
            overall_status=ComplianceStatus.UNKNOWN,
            territory_compliance={},
            usage_compliance={}
        )
        
        try:
            # Load rights ownership data
            rights_data = await self._load_rights_ownership(content_id, isrc)
            
            if not rights_data:
                result.overall_status = ComplianceStatus.NON_COMPLIANT
                result.violations.append({
                    "type": "missing_rights_data",
                    "message": "No rights ownership data found for content",
                    "severity": "error"
                })
                return result
            
            # 1. Territory Rights Check
            if config.check_territory_rights:
                territory_results = await self._check_territory_rights(
                    rights_data, territories, result
                )
                result.territory_compliance.update(territory_results)
            
            # 2. Usage Rights Check
            if config.check_usage_rights:
                usage_results = await self._check_usage_rights(
                    rights_data, usage_types, territories, result
                )
                result.usage_compliance.update(usage_results)
            
            # 3. Embargo Check
            if config.check_embargo_restrictions:
                await self._check_embargo_restrictions(
                    rights_data, territories, usage_types, result
                )
            
            # 4. Expiry Date Check
            if config.check_expiry_dates:
                await self._check_expiry_dates(
                    rights_data, territories, usage_types, config, result
                )
            
            # 5. Compliance Rules Check
            await self._check_compliance_rules(
                rights_data, territories, usage_types, result
            )
            
            # 6. Determine Overall Status
            result.overall_status = self._determine_overall_compliance_status(result)
            
            # 7. Generate Recommendations
            result.recommendations = await self._generate_recommendations(result, rights_data)
            result.required_actions = await self._generate_required_actions(result)
            
        except Exception as e:
            logger.error(f"Rights compliance check error: {str(e)}")
            result.overall_status = ComplianceStatus.UNKNOWN
            result.violations.append({
                "type": "system_error",
                "message": f"Compliance check failed: {str(e)}",
                "severity": "error"
            })
        
        # Calculate processing time
        end_time = datetime.now()
        result.processing_time = (end_time - start_time).total_seconds()
        
        # Store compliance check result
        await self._store_compliance_result(result)
        
        return result
    
    async def _load_rights_ownership(self, content_id: str, isrc: Optional[str]) -> Optional[RightsOwnership]:
        """Load rights ownership data from database"""
        
        if self.mongo_db is None:
            return None
        
        try:
            # Try to find by content_id first
            query = {"content_id": content_id}
            rights_record = await self.mongo_db["rights_ownership"].find_one(query)
            
            # If not found and ISRC provided, try ISRC
            if not rights_record and isrc:
                query = {"isrc": isrc}
                rights_record = await self.mongo_db["rights_ownership"].find_one(query)
            
            if rights_record:
                # Remove MongoDB _id
                rights_record.pop("_id", None)
                return RightsOwnership(**rights_record)
            
        except Exception as e:
            logger.error(f"Error loading rights ownership: {str(e)}")
        
        return None
    
    async def _check_territory_rights(self, rights_data: RightsOwnership, 
                                    territories: List[TerritoryCode],
                                    result: ComplianceCheckResult) -> Dict[str, ComplianceStatus]:
        """Check territory-specific rights compliance"""
        
        territory_compliance = {}
        
        for territory in territories:
            # Check if rights exist for this territory
            territory_rights = [
                tr for tr in rights_data.territory_rights 
                if tr.territory == territory or 
                   (tr.territory == TerritoryCode.GLOBAL and territory != TerritoryCode.GLOBAL)
            ]
            
            if not territory_rights:
                territory_compliance[territory.value] = ComplianceStatus.NON_COMPLIANT
                result.missing_rights.append({
                    "type": "territory_rights",
                    "territory": territory.value,
                    "message": f"No rights found for territory {territory.value}",
                    "severity": "error"
                })
                continue
            
            # Check rights status for territory
            active_rights = []
            for tr in territory_rights:
                # Check if rights are currently active
                now = datetime.now()
                
                if tr.effective_date > now:
                    result.warnings.append({
                        "type": "future_rights",
                        "territory": territory.value,
                        "message": f"Rights not yet effective until {tr.effective_date.date()}",
                        "severity": "warning"
                    })
                elif tr.expiry_date and tr.expiry_date < now:
                    result.expired_rights.append({
                        "type": "expired_territory_rights",
                        "territory": territory.value,
                        "expiry_date": tr.expiry_date.isoformat(),
                        "message": f"Territory rights expired on {tr.expiry_date.date()}",
                        "severity": "error"
                    })
                else:
                    active_rights.append(tr)
            
            if active_rights:
                # Check rights coverage percentage
                total_percentage = sum(tr.rights_percentage for tr in active_rights)
                
                if total_percentage >= 100:
                    territory_compliance[territory.value] = ComplianceStatus.COMPLIANT
                elif total_percentage >= 50:
                    territory_compliance[territory.value] = ComplianceStatus.WARNING
                    result.warnings.append({
                        "type": "partial_territory_rights",
                        "territory": territory.value,
                        "coverage": total_percentage,
                        "message": f"Only {total_percentage}% rights coverage in {territory.value}",
                        "severity": "warning"
                    })
                else:
                    territory_compliance[territory.value] = ComplianceStatus.NON_COMPLIANT
                    result.violations.append({
                        "type": "insufficient_territory_rights",
                        "territory": territory.value,
                        "coverage": total_percentage,
                        "message": f"Insufficient rights coverage ({total_percentage}%) in {territory.value}",
                        "severity": "error"
                    })
            else:
                territory_compliance[territory.value] = ComplianceStatus.NON_COMPLIANT
        
        return territory_compliance
    
    async def _check_usage_rights(self, rights_data: RightsOwnership,
                                usage_types: List[UsageRightType],
                                territories: List[TerritoryCode],
                                result: ComplianceCheckResult) -> Dict[str, ComplianceStatus]:
        """Check usage-specific rights compliance"""
        
        usage_compliance = {}
        
        for usage_type in usage_types:
            # Find usage rights for this type
            relevant_rights = [
                ur for ur in rights_data.usage_rights 
                if ur.usage_type == usage_type
            ]
            
            if not relevant_rights:
                usage_compliance[usage_type.value] = ComplianceStatus.NON_COMPLIANT
                result.missing_rights.append({
                    "type": "usage_rights",
                    "usage_type": usage_type.value,
                    "message": f"No {usage_type.value} rights found",
                    "severity": "error"
                })
                continue
            
            # Check territory coverage for this usage type
            covered_territories = set()
            active_rights = []
            
            for ur in relevant_rights:
                # Check if rights are active
                now = datetime.now()
                
                if ur.effective_date > now:
                    result.warnings.append({
                        "type": "future_usage_rights",
                        "usage_type": usage_type.value,
                        "message": f"{usage_type.value} rights not yet effective until {ur.effective_date.date()}",
                        "severity": "warning"
                    })
                elif ur.expiry_date and ur.expiry_date < now:
                    result.expired_rights.append({
                        "type": "expired_usage_rights",
                        "usage_type": usage_type.value,
                        "expiry_date": ur.expiry_date.isoformat(),
                        "message": f"{usage_type.value} rights expired on {ur.expiry_date.date()}",
                        "severity": "error"
                    })
                else:
                    active_rights.append(ur)
                    covered_territories.update(ur.territories)
            
            # Check if requested territories are covered
            requested_territories = set(territories)
            
            if TerritoryCode.GLOBAL in covered_territories:
                # Global rights cover all territories
                usage_compliance[usage_type.value] = ComplianceStatus.COMPLIANT
            else:
                missing_territories = requested_territories - covered_territories
                
                if not missing_territories:
                    usage_compliance[usage_type.value] = ComplianceStatus.COMPLIANT
                elif len(missing_territories) < len(requested_territories):
                    usage_compliance[usage_type.value] = ComplianceStatus.WARNING
                    result.warnings.append({
                        "type": "partial_usage_rights",
                        "usage_type": usage_type.value,
                        "missing_territories": [t.value for t in missing_territories],
                        "message": f"{usage_type.value} rights missing for territories: {[t.value for t in missing_territories]}",
                        "severity": "warning"
                    })
                else:
                    usage_compliance[usage_type.value] = ComplianceStatus.NON_COMPLIANT
                    result.violations.append({
                        "type": "insufficient_usage_rights",
                        "usage_type": usage_type.value,
                        "missing_territories": [t.value for t in missing_territories],
                        "message": f"No {usage_type.value} rights for requested territories",
                        "severity": "error"
                    })
        
        return usage_compliance
    
    async def _check_embargo_restrictions(self, rights_data: RightsOwnership,
                                        territories: List[TerritoryCode],
                                        usage_types: List[UsageRightType],
                                        result: ComplianceCheckResult):
        """Check for embargo restrictions"""
        
        now = datetime.now()
        
        for embargo in rights_data.embargo_restrictions:
            # Check if embargo is currently active
            if embargo.restriction_start <= now and (
                not embargo.restriction_end or embargo.restriction_end > now
            ):
                # Check if embargo affects requested territories/usage
                affected_territories = set(embargo.affected_territories) & set(territories)
                affected_usage = set(embargo.affected_usage_types) & set(usage_types)
                
                if affected_territories and affected_usage:
                    result.embargoed_items.append({
                        "type": "active_embargo",
                        "embargo_type": embargo.embargo_type.value,
                        "affected_territories": [t.value for t in affected_territories],
                        "affected_usage_types": [u.value for u in affected_usage],
                        "restriction_end": embargo.restriction_end.isoformat() if embargo.restriction_end else None,
                        "reason": embargo.reason,
                        "message": f"Embargo active: {embargo.reason}",
                        "severity": "error"
                    })
    
    async def _check_expiry_dates(self, rights_data: RightsOwnership,
                                territories: List[TerritoryCode],
                                usage_types: List[UsageRightType],
                                config: RightsValidationConfig,
                                result: ComplianceCheckResult):
        """Check for expiring rights"""
        
        now = datetime.now()
        warning_date = now + timedelta(days=config.grace_period_days)
        
        # Check territory rights expiry
        for tr in rights_data.territory_rights:
            if tr.expiry_date and tr.territory in territories:
                if tr.expiry_date < now:
                    # Already handled in territory check
                    pass
                elif tr.expiry_date <= warning_date:
                    result.warnings.append({
                        "type": "expiring_territory_rights",
                        "territory": tr.territory.value,
                        "expiry_date": tr.expiry_date.isoformat(),
                        "days_until_expiry": (tr.expiry_date - now).days,
                        "message": f"Territory rights for {tr.territory.value} expiring on {tr.expiry_date.date()}",
                        "severity": "warning"
                    })
        
        # Check usage rights expiry
        for ur in rights_data.usage_rights:
            if ur.expiry_date and ur.usage_type in usage_types:
                territory_overlap = set(ur.territories) & set(territories)
                if territory_overlap:
                    if ur.expiry_date < now:
                        # Already handled in usage check
                        pass
                    elif ur.expiry_date <= warning_date:
                        result.warnings.append({
                            "type": "expiring_usage_rights",
                            "usage_type": ur.usage_type.value,
                            "territories": [t.value for t in territory_overlap],
                            "expiry_date": ur.expiry_date.isoformat(),
                            "days_until_expiry": (ur.expiry_date - now).days,
                            "message": f"{ur.usage_type.value} rights expiring on {ur.expiry_date.date()}",
                            "severity": "warning"
                        })
    
    async def _check_compliance_rules(self, rights_data: RightsOwnership,
                                    territories: List[TerritoryCode],
                                    usage_types: List[UsageRightType],
                                    result: ComplianceCheckResult):
        """Check against compliance rules"""
        
        for rule in self.compliance_rules:
            # Check if rule applies to requested territories/usage
            rule_territories = set(rule.territories)
            rule_usage_types = set(rule.usage_types)
            
            territory_match = bool(rule_territories & set(territories)) or TerritoryCode.GLOBAL in rule_territories
            usage_match = bool(rule_usage_types & set(usage_types))
            
            if territory_match and usage_match and rule.is_active:
                # Rule applies - check requirements
                rule_violations = []
                
                # Check required fields (would need metadata integration)
                for field in rule.required_fields:
                    # This would integrate with metadata to check field presence
                    # For now, we'll simulate the check
                    pass
                
                # Check validation logic
                for logic_key, logic_value in rule.validation_logic.items():
                    # Implement specific logic checks based on rule requirements
                    if logic_key == "master_clearance_required" and logic_value:
                        if not rights_data.master_owner:
                            rule_violations.append(f"Master owner not specified (required by {rule.rule_name})")
                    
                    if logic_key == "publishing_clearance_required" and logic_value:
                        if not rights_data.publishing_owner:
                            rule_violations.append(f"Publishing owner not specified (required by {rule.rule_name})")
                
                # Add violations to result
                for violation in rule_violations:
                    if rule.severity == "error":
                        result.violations.append({
                            "type": "compliance_rule_violation",
                            "rule_name": rule.rule_name,
                            "message": violation,
                            "severity": "error"
                        })
                    else:
                        result.warnings.append({
                            "type": "compliance_rule_warning",
                            "rule_name": rule.rule_name,
                            "message": violation,
                            "severity": "warning"
                        })
    
    def _determine_overall_compliance_status(self, result: ComplianceCheckResult) -> ComplianceStatus:
        """Determine overall compliance status"""
        
        # Check for violations
        if result.violations or result.expired_rights or result.embargoed_items:
            return ComplianceStatus.NON_COMPLIANT
        
        # Check for missing rights
        if result.missing_rights:
            return ComplianceStatus.NON_COMPLIANT
        
        # Check individual territory/usage compliance
        territory_statuses = list(result.territory_compliance.values())
        usage_statuses = list(result.usage_compliance.values())
        
        all_statuses = territory_statuses + usage_statuses
        
        if all(status == ComplianceStatus.COMPLIANT for status in all_statuses):
            if result.warnings:
                return ComplianceStatus.WARNING
            else:
                return ComplianceStatus.COMPLIANT
        elif any(status == ComplianceStatus.NON_COMPLIANT for status in all_statuses):
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.WARNING
    
    async def _generate_recommendations(self, result: ComplianceCheckResult, 
                                      rights_data: RightsOwnership) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if result.missing_rights:
            recommendations.append("Acquire missing rights for identified territories and usage types")
        
        if result.expired_rights:
            recommendations.append("Renew expired rights or remove content from affected territories/platforms")
        
        if result.embargoed_items:
            recommendations.append("Wait for embargo restrictions to lift or seek override permissions")
        
        if result.warnings:
            warning_count = len([w for w in result.warnings if "expiring" in w.get("type", "")])
            if warning_count > 0:
                recommendations.append("Proactively renew expiring rights to avoid service interruption")
        
        # Territory-specific recommendations
        non_compliant_territories = [
            territory for territory, status in result.territory_compliance.items() 
            if status == ComplianceStatus.NON_COMPLIANT
        ]
        
        if non_compliant_territories:
            recommendations.append(
                f"Secure rights clearance for territories: {', '.join(non_compliant_territories)}"
            )
        
        return recommendations
    
    async def _generate_required_actions(self, result: ComplianceCheckResult) -> List[str]:
        """Generate required actions for compliance"""
        
        actions = []
        
        # Critical violations
        critical_violations = [v for v in result.violations if v.get("severity") == "error"]
        if critical_violations:
            actions.append("Address critical compliance violations before content release")
        
        # Embargoed items
        if result.embargoed_items:
            actions.append("Remove content from embargoed territories/platforms immediately")
        
        # Expired rights
        if result.expired_rights:
            actions.append("Cease distribution where rights have expired")
        
        return actions
    
    async def _store_compliance_result(self, result: ComplianceCheckResult):
        """Store compliance check result in database"""
        
        if self.mongo_db is None:
            return
        
        try:
            result_dict = result.dict()
            result_dict["_id"] = result.check_id
            result_dict["stored_at"] = datetime.now()
            
            await self.mongo_db["compliance_check_results"].insert_one(result_dict)
            logger.info(f"Stored compliance result {result.check_id}")
            
        except Exception as e:
            logger.error(f"Failed to store compliance result: {str(e)}")
    
    async def create_rights_ownership(self, rights_data: RightsOwnership) -> str:
        """Create new rights ownership record"""
        
        if self.mongo_db is None:
            raise ValueError("Database not available")
        
        try:
            rights_dict = rights_data.dict()
            rights_dict["_id"] = rights_data.content_id
            rights_dict["created_at"] = datetime.now()
            
            await self.mongo_db["rights_ownership"].insert_one(rights_dict)
            
            # Log audit trail
            await self._log_rights_audit("created", rights_data.content_id, rights_data.created_by)
            
            return rights_data.content_id
            
        except Exception as e:
            logger.error(f"Error creating rights ownership: {str(e)}")
            raise
    
    async def _log_rights_audit(self, action: str, content_id: str, actor: str, 
                              changes: Dict[str, Any] = None):
        """Log rights audit trail"""
        
        if self.mongo_db is None:
            return
        
        try:
            audit_log = RightsAuditLog(
                content_id=content_id,
                action=action,
                actor=actor,
                changes=changes or {}
            )
            
            audit_dict = audit_log.dict()
            audit_dict["_id"] = audit_log.log_id
            
            await self.mongo_db["rights_audit_logs"].insert_one(audit_dict)
            
        except Exception as e:
            logger.error(f"Failed to log rights audit: {str(e)}")
    
    def get_territory_info(self, territory: TerritoryCode) -> Optional[TerritoryMapping]:
        """Get detailed territory information"""
        return self.territory_mappings.get(territory)
    
    def get_usage_template(self, template_name: str) -> Optional[UsageRightTemplate]:
        """Get usage rights template"""
        return self.usage_templates.get(template_name)