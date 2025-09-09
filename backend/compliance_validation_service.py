"""
Compliance Validation Service - Auto-validation against licensing rules and geo-restrictions
Handles compliance checks for content licensing, geographic restrictions, and industry standards.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel
from content_ingestion_service import ContentIngestionRecord, DDEXMetadata, LicensingTerms, GeoRestriction

class ComplianceRuleType(str, Enum):
    LICENSING = "licensing"
    GEO_RESTRICTION = "geo_restriction"
    CONTENT_RATING = "content_rating"
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    TECHNICAL = "technical"
    METADATA = "metadata"
    INDUSTRY_STANDARD = "industry_standard"

class ComplianceSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ComplianceIssue(BaseModel):
    issue_id: str
    rule_type: ComplianceRuleType
    severity: ComplianceSeverity
    title: str
    description: str
    suggested_fix: str
    affected_fields: List[str] = []
    auto_fixable: bool = False
    blocking: bool = False  # Prevents distribution if True
    metadata: Dict[str, Any] = {}

class ComplianceRule(BaseModel):
    rule_id: str
    rule_type: ComplianceRuleType
    name: str
    description: str
    severity: ComplianceSeverity
    territories: List[str] = []  # Empty list means worldwide
    content_types: List[str] = []  # Empty list means all content types
    is_active: bool = True
    validation_function: str  # Function name to call for validation
    metadata: Dict[str, Any] = {}

class ComplianceValidationService:
    def __init__(self):
        self.compliance_rules = self._initialize_compliance_rules()
        self.geo_restrictions_db = self._initialize_geo_restrictions()
        
    def _initialize_compliance_rules(self) -> List[ComplianceRule]:
        """Initialize compliance rules for validation"""
        return [
            # Licensing Rules
            ComplianceRule(
                rule_id="license_001",
                rule_type=ComplianceRuleType.LICENSING,
                name="Valid Licensing Terms Required",
                description="Content must have valid licensing terms defined",
                severity=ComplianceSeverity.CRITICAL,
                validation_function="validate_licensing_terms"
            ),
            
            ComplianceRule(
                rule_id="license_002",
                rule_type=ComplianceRuleType.LICENSING,
                name="Master Rights Ownership",
                description="Master rights ownership must be clearly defined",
                severity=ComplianceSeverity.HIGH,
                validation_function="validate_master_rights"
            ),
            
            ComplianceRule(
                rule_id="license_003",
                rule_type=ComplianceRuleType.LICENSING,
                name="Publishing Rights Clearance",
                description="Publishing rights must be cleared for distribution",
                severity=ComplianceSeverity.HIGH,
                validation_function="validate_publishing_rights"
            ),
            
            # Geographic Restrictions
            ComplianceRule(
                rule_id="geo_001",
                rule_type=ComplianceRuleType.GEO_RESTRICTION,
                name="Territory Licensing Compliance",
                description="Content must comply with territorial licensing restrictions",
                severity=ComplianceSeverity.CRITICAL,
                validation_function="validate_geo_restrictions"
            ),
            
            ComplianceRule(
                rule_id="geo_002",
                rule_type=ComplianceRuleType.GEO_RESTRICTION,
                name="EU Content Regulation",
                description="Content distributed in EU must comply with EU regulations",
                severity=ComplianceSeverity.HIGH,
                territories=["EU", "DE", "FR", "IT", "ES", "NL"],
                validation_function="validate_eu_compliance"
            ),
            
            ComplianceRule(
                rule_id="geo_003",
                rule_type=ComplianceRuleType.GEO_RESTRICTION,
                name="China Content Restrictions",
                description="Content for China market must comply with local content laws",
                severity=ComplianceSeverity.CRITICAL,
                territories=["CN"],
                validation_function="validate_china_compliance"
            ),
            
            # Content Rating Rules
            ComplianceRule(
                rule_id="rating_001",
                rule_type=ComplianceRuleType.CONTENT_RATING,
                name="Explicit Content Labeling",
                description="Explicit content must be properly labeled",
                severity=ComplianceSeverity.HIGH,
                validation_function="validate_explicit_content"
            ),
            
            ComplianceRule(
                rule_id="rating_002",
                rule_type=ComplianceRuleType.CONTENT_RATING,
                name="Parental Advisory Compliance",
                description="Content requiring parental advisory must be flagged",
                severity=ComplianceSeverity.MEDIUM,
                validation_function="validate_parental_advisory"
            ),
            
            # Copyright Rules
            ComplianceRule(
                rule_id="copyright_001",
                rule_type=ComplianceRuleType.COPYRIGHT,
                name="Copyright Ownership Verification",
                description="Copyright ownership must be verified and documented",
                severity=ComplianceSeverity.CRITICAL,
                validation_function="validate_copyright_ownership"
            ),
            
            ComplianceRule(
                rule_id="copyright_002",
                rule_type=ComplianceRuleType.COPYRIGHT,
                name="Sample Clearance",
                description="All samples used must be properly cleared",
                severity=ComplianceSeverity.HIGH,
                validation_function="validate_sample_clearance"
            ),
            
            # Technical Standards
            ComplianceRule(
                rule_id="tech_001",
                rule_type=ComplianceRuleType.TECHNICAL,
                name="Audio Quality Standards",
                description="Audio content must meet minimum quality standards",
                severity=ComplianceSeverity.MEDIUM,
                content_types=["audio"],
                validation_function="validate_audio_quality"
            ),
            
            ComplianceRule(
                rule_id="tech_002",
                rule_type=ComplianceRuleType.TECHNICAL,
                name="Video Format Compliance",
                description="Video content must use approved formats and codecs",
                severity=ComplianceSeverity.MEDIUM,
                content_types=["video"],
                validation_function="validate_video_format"
            ),
            
            # Metadata Standards
            ComplianceRule(
                rule_id="meta_001",
                rule_type=ComplianceRuleType.METADATA,
                name="DDEX Metadata Completeness",
                description="All required DDEX metadata fields must be populated",
                severity=ComplianceSeverity.HIGH,
                validation_function="validate_ddex_completeness"
            ),
            
            ComplianceRule(
                rule_id="meta_002",
                rule_type=ComplianceRuleType.METADATA,
                name="ISRC Format Validation",
                description="ISRC codes must follow international standards",
                severity=ComplianceSeverity.MEDIUM,
                validation_function="validate_isrc_format"
            ),
            
            ComplianceRule(
                rule_id="meta_003",
                rule_type=ComplianceRuleType.METADATA,
                name="Contributor Information Completeness",
                description="All contributors must have complete information",
                severity=ComplianceSeverity.HIGH,
                validation_function="validate_contributor_info"
            ),
            
            # Industry Standards
            ComplianceRule(
                rule_id="industry_001",
                rule_type=ComplianceRuleType.INDUSTRY_STANDARD,
                name="Music Industry Code of Conduct",
                description="Content must comply with music industry ethical standards",
                severity=ComplianceSeverity.MEDIUM,
                validation_function="validate_industry_standards"
            ),
            
            ComplianceRule(
                rule_id="industry_002",
                rule_type=ComplianceRuleType.INDUSTRY_STANDARD,
                name="Platform-Specific Requirements",
                description="Content must meet specific platform distribution requirements",
                severity=ComplianceSeverity.HIGH,
                validation_function="validate_platform_requirements"
            )
        ]
    
    def _initialize_geo_restrictions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize geographic restrictions database"""
        return {
            "CN": {
                "country_name": "China",
                "restrictions": {
                    "explicit_content": False,
                    "political_content": False,
                    "religious_content": False,
                    "gambling_content": False,
                    "violent_content": False
                },
                "required_metadata": ["chinese_title", "content_rating"],
                "licensing_authority": "NCAC",
                "content_review_required": True
            },
            "DE": {
                "country_name": "Germany",
                "restrictions": {
                    "hate_speech": False,
                    "nazi_symbols": False,
                    "explicit_content_labeling": True
                },
                "required_metadata": ["content_rating", "age_classification"],
                "licensing_authority": "GEMA",
                "content_review_required": False
            },
            "US": {
                "country_name": "United States",
                "restrictions": {
                    "copyright_infringement": False,
                    "trademark_violation": False
                },
                "required_metadata": ["parental_advisory"],
                "licensing_authority": "BMI/ASCAP/SESAC",
                "content_review_required": False
            },
            "GB": {
                "country_name": "United Kingdom", 
                "restrictions": {
                    "explicit_content_labeling": True,
                    "age_verification": True
                },
                "required_metadata": ["content_rating"],
                "licensing_authority": "PRS",
                "content_review_required": False
            },
            "IN": {
                "country_name": "India",
                "restrictions": {
                    "religious_sensitivity": True,
                    "cultural_sensitivity": True,
                    "explicit_content": False
                },
                "required_metadata": ["content_rating", "language"],
                "licensing_authority": "IPRS",
                "content_review_required": True
            }
        }
    
    async def validate_content_compliance(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Run comprehensive compliance validation on content record"""
        
        validation_results = {
            "content_id": content_record.content_id,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "pending",
            "issues": [],
            "warnings": [],
            "passed_rules": [],
            "auto_fixes_applied": [],
            "blocking_issues_count": 0,
            "total_issues_count": 0,
            "compliance_score": 0.0,
            "distribution_approved": False
        }
        
        # Run each compliance rule
        for rule in self.compliance_rules:
            if not rule.is_active:
                continue
                
            # Check if rule applies to this content
            if not self._rule_applies_to_content(rule, content_record):
                continue
            
            # Run validation function
            try:
                rule_result = await self._run_validation_rule(rule, content_record)
                
                if rule_result["passed"]:
                    validation_results["passed_rules"].append({
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity.value
                    })
                else:
                    # Create compliance issue
                    issue = ComplianceIssue(
                        issue_id=f"{rule.rule_id}_{content_record.content_id}",
                        rule_type=rule.rule_type,
                        severity=rule.severity,
                        title=rule.name,
                        description=rule_result.get("message", rule.description),
                        suggested_fix=rule_result.get("suggested_fix", "Please review and fix this issue"),
                        affected_fields=rule_result.get("affected_fields", []),
                        auto_fixable=rule_result.get("auto_fixable", False),
                        blocking=rule_result.get("blocking", rule.severity == ComplianceSeverity.CRITICAL)
                    )
                    
                    if issue.severity in [ComplianceSeverity.CRITICAL, ComplianceSeverity.HIGH]:
                        validation_results["issues"].append(issue.dict())
                        if issue.blocking:
                            validation_results["blocking_issues_count"] += 1
                    else:
                        validation_results["warnings"].append(issue.dict())
                    
                    validation_results["total_issues_count"] += 1
                    
                    # Apply auto-fix if possible
                    if issue.auto_fixable and "auto_fix" in rule_result:
                        try:
                            fix_applied = await self._apply_auto_fix(content_record, rule_result["auto_fix"])
                            if fix_applied:
                                validation_results["auto_fixes_applied"].append({
                                    "rule_id": rule.rule_id,
                                    "fix_description": rule_result["auto_fix"]["description"]
                                })
                        except Exception as e:
                            print(f"Auto-fix failed for rule {rule.rule_id}: {str(e)}")
                            
            except Exception as e:
                # Log validation error but continue
                print(f"Validation error for rule {rule.rule_id}: {str(e)}")
                validation_results["warnings"].append({
                    "rule_id": rule.rule_id,
                    "title": f"Validation Error: {rule.name}",
                    "description": f"Could not validate rule: {str(e)}",
                    "severity": "medium"
                })
        
        # Calculate compliance score
        total_rules_run = len([r for r in self.compliance_rules if r.is_active and self._rule_applies_to_content(r, content_record)])
        passed_rules_count = len(validation_results["passed_rules"])
        
        if total_rules_run > 0:
            validation_results["compliance_score"] = (passed_rules_count / total_rules_run) * 100.0
        
        # Determine overall status
        if validation_results["blocking_issues_count"] > 0:
            validation_results["overall_status"] = "rejected"
            validation_results["distribution_approved"] = False
        elif validation_results["total_issues_count"] > 0:
            validation_results["overall_status"] = "needs_review"
            validation_results["distribution_approved"] = False
        else:
            validation_results["overall_status"] = "approved"
            validation_results["distribution_approved"] = True
        
        return validation_results
    
    def _rule_applies_to_content(self, rule: ComplianceRule, content_record: ContentIngestionRecord) -> bool:
        """Check if a compliance rule applies to the given content"""
        
        # Check content type restrictions
        if rule.content_types:
            content_types = [cf.content_type.value for cf in content_record.content_files]
            if not any(ct in rule.content_types for ct in content_types):
                return False
        
        # Check territory restrictions
        if rule.territories:
            content_territories = []
            if content_record.ddex_metadata.licensing_terms:
                content_territories = content_record.ddex_metadata.licensing_terms.territories
            
            if content_territories:
                if not any(territory in rule.territories for territory in content_territories):
                    return False
            # If no territories specified in content, rule applies
        
        return True
    
    async def _run_validation_rule(self, rule: ComplianceRule, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Run a specific validation rule"""
        
        validation_function = getattr(self, rule.validation_function, None)
        if not validation_function:
            return {
                "passed": False,
                "message": f"Validation function {rule.validation_function} not implemented",
                "blocking": False
            }
        
        return await validation_function(content_record)
    
    # Validation Functions
    
    async def validate_licensing_terms(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate that licensing terms are properly defined"""
        
        licensing_terms = content_record.ddex_metadata.licensing_terms
        
        if not licensing_terms:
            return {
                "passed": False,
                "message": "No licensing terms defined for this content",
                "suggested_fix": "Add licensing terms including license type, territories, and usage rights",
                "affected_fields": ["ddex_metadata.licensing_terms"],
                "blocking": True
            }
        
        issues = []
        
        # Check required fields
        if not licensing_terms.license_type:
            issues.append("License type is required")
        
        if not licensing_terms.start_date:
            issues.append("License start date is required")
        
        if not licensing_terms.territories:
            issues.append("Licensed territories must be specified")
        
        if licensing_terms.end_date and licensing_terms.end_date <= licensing_terms.start_date:
            issues.append("License end date must be after start date")
        
        if issues:
            return {
                "passed": False,
                "message": f"Licensing terms validation failed: {'; '.join(issues)}",
                "suggested_fix": "Review and complete all required licensing information",
                "affected_fields": ["ddex_metadata.licensing_terms"],
                "blocking": True
            }
        
        return {"passed": True}
    
    async def validate_master_rights(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate master rights ownership"""
        
        master_rights_owner = content_record.ddex_metadata.master_rights_owner
        
        if not master_rights_owner:
            return {
                "passed": False,
                "message": "Master rights owner must be specified",
                "suggested_fix": "Specify the master rights owner in the metadata",
                "affected_fields": ["ddex_metadata.master_rights_owner"],
                "blocking": True
            }
        
        # Check if owner is in contributors list
        contributor_names = [c.name for c in content_record.ddex_metadata.contributors]
        if master_rights_owner not in contributor_names and master_rights_owner != "Big Mann Entertainment":
            return {
                "passed": False,
                "message": "Master rights owner must be listed as a contributor or be the platform",
                "suggested_fix": "Add master rights owner to contributors list or verify ownership",
                "affected_fields": ["ddex_metadata.master_rights_owner", "ddex_metadata.contributors"],
                "blocking": False
            }
        
        return {"passed": True}
    
    async def validate_publishing_rights(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate publishing rights clearance"""
        
        publishing_rights_owner = content_record.ddex_metadata.publishing_rights_owner
        
        if not publishing_rights_owner:
            return {
                "passed": False,
                "message": "Publishing rights owner must be specified",
                "suggested_fix": "Specify the publishing rights owner in the metadata",
                "affected_fields": ["ddex_metadata.publishing_rights_owner"],
                "blocking": True
            }
        
        # Check for songwriters in contributors
        songwriters = [c for c in content_record.ddex_metadata.contributors if c.role.value in ['songwriter', 'composer']]
        
        if not songwriters:
            return {
                "passed": False,
                "message": "At least one songwriter or composer must be listed as a contributor",
                "suggested_fix": "Add songwriters/composers to the contributors list",
                "affected_fields": ["ddex_metadata.contributors"],
                "blocking": True
            }
        
        return {"passed": True}
    
    async def validate_geo_restrictions(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate geographic distribution restrictions"""
        
        licensing_terms = content_record.ddex_metadata.licensing_terms
        
        if not licensing_terms or not licensing_terms.territories:
            return {
                "passed": False,
                "message": "Geographic territories for distribution must be specified",
                "suggested_fix": "Define the territories where this content can be distributed",
                "affected_fields": ["ddex_metadata.licensing_terms.territories"],
                "blocking": True
            }
        
        # Check for restricted territories
        for territory in licensing_terms.territories:
            if territory in self.geo_restrictions_db:
                restriction_info = self.geo_restrictions_db[territory]
                
                # Check if content review is required
                if restriction_info.get("content_review_required", False):
                    return {
                        "passed": False,
                        "message": f"Content review required for {territory} ({restriction_info['country_name']})",
                        "suggested_fix": f"Submit content for review by {restriction_info.get('licensing_authority', 'local authorities')}",
                        "affected_fields": ["compliance_status"],
                        "blocking": False  # Can be reviewed later
                    }
        
        return {"passed": True}
    
    async def validate_eu_compliance(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate EU-specific compliance requirements"""
        
        licensing_terms = content_record.ddex_metadata.licensing_terms
        eu_territories = ["EU", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "DK", "SE", "NO", "FI"]
        
        if not licensing_terms or not licensing_terms.territories:
            return {"passed": True}  # Not applicable if no territories specified
        
        # Check if content is being distributed to EU
        distributing_to_eu = any(territory in eu_territories for territory in licensing_terms.territories)
        
        if not distributing_to_eu:
            return {"passed": True}  # Not applicable
        
        # EU-specific requirements
        issues = []
        
        # Check for explicit content labeling
        if content_record.ddex_metadata.explicit_content and not content_record.ddex_metadata.parental_warning:
            issues.append("Explicit content must have parental warning for EU distribution")
        
        # Check for GDPR compliance (simplified check)
        contributor_issues = []
        for contributor in content_record.ddex_metadata.contributors:
            if contributor.email and not contributor.metadata.get("gdpr_consent", False):
                contributor_issues.append(f"GDPR consent required for contributor {contributor.name}")
        
        if contributor_issues:
            issues.extend(contributor_issues)
        
        if issues:
            return {
                "passed": False,
                "message": f"EU compliance issues: {'; '.join(issues)}",
                "suggested_fix": "Ensure GDPR compliance and proper content labeling for EU distribution",
                "affected_fields": ["ddex_metadata.parental_warning", "ddex_metadata.contributors"],
                "blocking": False
            }
        
        return {"passed": True}
    
    async def validate_china_compliance(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate China-specific compliance requirements"""
        
        licensing_terms = content_record.ddex_metadata.licensing_terms
        
        if not licensing_terms or "CN" not in licensing_terms.territories:
            return {"passed": True}  # Not applicable
        
        # China has strict content restrictions
        issues = []
        
        # Check explicit content (not allowed)
        if content_record.ddex_metadata.explicit_content:
            issues.append("Explicit content is not permitted for distribution in China")
        
        # Check for required Chinese title
        if not content_record.ddex_metadata.metadata.get("chinese_title"):
            issues.append("Chinese title translation is required for China distribution")
        
        # Check for sensitive keywords (simplified check)
        sensitive_keywords = ["政治", "宗教", "赌博", "暴力"]  # Political, religious, gambling, violence
        content_text = f"{content_record.ddex_metadata.title} {content_record.ddex_metadata.description or ''}"
        
        for keyword in sensitive_keywords:
            if keyword in content_text:
                issues.append(f"Content contains sensitive keyword: {keyword}")
        
        if issues:
            return {
                "passed": False,
                "message": f"China compliance issues: {'; '.join(issues)}",
                "suggested_fix": "Remove sensitive content and add required Chinese translations",
                "affected_fields": ["ddex_metadata.explicit_content", "ddex_metadata.metadata"],
                "blocking": True  # China has strict enforcement
            }
        
        return {"passed": True}
    
    async def validate_explicit_content(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate explicit content labeling"""
        
        # Simple content analysis for explicit material
        explicit_keywords = [
            "fuck", "shit", "bitch", "ass", "damn", "hell", 
            "sex", "drugs", "violence", "kill", "murder"
        ]
        
        content_text = f"{content_record.ddex_metadata.title} {content_record.ddex_metadata.description or ''}"
        content_text_lower = content_text.lower()
        
        found_explicit = any(keyword in content_text_lower for keyword in explicit_keywords)
        
        if found_explicit and not content_record.ddex_metadata.explicit_content:
            return {
                "passed": False,
                "message": "Content appears to contain explicit material but is not marked as explicit",
                "suggested_fix": "Mark content as explicit or review content for explicit material",
                "affected_fields": ["ddex_metadata.explicit_content"],
                "auto_fixable": True,
                "auto_fix": {
                    "action": "set_explicit_flag",
                    "description": "Set explicit content flag to true",
                    "field": "ddex_metadata.explicit_content",
                    "value": True
                },
                "blocking": False
            }
        
        return {"passed": True}
    
    async def validate_parental_advisory(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate parental advisory requirements"""
        
        if content_record.ddex_metadata.explicit_content and not content_record.ddex_metadata.parental_warning:
            return {
                "passed": False,
                "message": "Explicit content requires parental advisory warning",
                "suggested_fix": "Enable parental advisory warning for explicit content",
                "affected_fields": ["ddex_metadata.parental_warning"],
                "auto_fixable": True,
                "auto_fix": {
                    "action": "set_parental_warning",
                    "description": "Set parental warning flag to true",
                    "field": "ddex_metadata.parental_warning", 
                    "value": True
                },
                "blocking": False
            }
        
        return {"passed": True}
    
    async def validate_copyright_ownership(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate copyright ownership documentation"""
        
        # Check for P-Line (phonogram copyright)
        if not content_record.ddex_metadata.p_line:
            return {
                "passed": False,
                "message": "P-Line (phonogram copyright) is required",
                "suggested_fix": "Add P-Line copyright information",
                "affected_fields": ["ddex_metadata.p_line"],
                "blocking": True
            }
        
        # Check for C-Line (composition copyright)
        if not content_record.ddex_metadata.c_line:
            return {
                "passed": False,
                "message": "C-Line (composition copyright) is required",
                "suggested_fix": "Add C-Line copyright information",
                "affected_fields": ["ddex_metadata.c_line"],
                "blocking": True
            }
        
        return {"passed": True}
    
    async def validate_sample_clearance(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate sample clearance (simplified check)"""
        
        # This would typically integrate with sample detection services
        # For now, we'll do a basic check based on metadata
        
        if content_record.ddex_metadata.metadata.get("contains_samples", False):
            sample_clearances = content_record.ddex_metadata.metadata.get("sample_clearances", [])
            
            if not sample_clearances:
                return {
                    "passed": False,
                    "message": "Content marked as containing samples but no clearances documented",
                    "suggested_fix": "Provide sample clearance documentation",
                    "affected_fields": ["ddex_metadata.metadata.sample_clearances"],
                    "blocking": True
                }
        
        return {"passed": True}
    
    async def validate_audio_quality(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate audio quality standards"""
        
        audio_files = [cf for cf in content_record.content_files if cf.content_type.value == "audio"]
        
        for audio_file in audio_files:
            # Check file size as proxy for quality
            if audio_file.file_size < 1024 * 1024:  # Less than 1MB
                return {
                    "passed": False,
                    "message": f"Audio file {audio_file.original_filename} appears to be low quality (small file size)",
                    "suggested_fix": "Upload higher quality audio files (minimum 320kbps MP3 or equivalent)",
                    "affected_fields": ["content_files"],
                    "blocking": False
                }
        
        return {"passed": True}
    
    async def validate_video_format(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate video format compliance"""
        
        video_files = [cf for cf in content_record.content_files if cf.content_type.value == "video"]
        approved_video_formats = [".mp4", ".mov", ".avi", ".mkv"]
        
        for video_file in video_files:
            file_extension = video_file.original_filename.lower().split('.')[-1]
            if f".{file_extension}" not in approved_video_formats:
                return {
                    "passed": False,
                    "message": f"Video format .{file_extension} is not approved for distribution",
                    "suggested_fix": f"Convert video to approved format: {', '.join(approved_video_formats)}",
                    "affected_fields": ["content_files"],
                    "blocking": False
                }
        
        return {"passed": True}
    
    async def validate_ddex_completeness(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate DDEX metadata completeness"""
        
        ddex_metadata = content_record.ddex_metadata
        missing_fields = []
        
        # Required DDEX fields
        required_fields = [
            ("title", "Title"),
            ("main_artist", "Main Artist"),
            ("release_date", "Release Date"),
            ("genre", "Genre"),
            ("contributors", "Contributors")
        ]
        
        for field_name, display_name in required_fields:
            value = getattr(ddex_metadata, field_name, None)
            if not value or (isinstance(value, list) and len(value) == 0):
                missing_fields.append(display_name)
        
        if missing_fields:
            return {
                "passed": False,
                "message": f"Missing required DDEX metadata fields: {', '.join(missing_fields)}",
                "suggested_fix": "Complete all required metadata fields",
                "affected_fields": [f"ddex_metadata.{field[0]}" for field in required_fields if getattr(ddex_metadata, field[0], None) is None],
                "blocking": True
            }
        
        return {"passed": True}
    
    async def validate_isrc_format(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate ISRC format compliance"""
        
        isrc = content_record.ddex_metadata.isrc
        
        if isrc:
            # ISRC format: CC-XXX-YY-NNNNN (but often stored without hyphens: CCXXXYYNNNNN)
            isrc_pattern = r'^[A-Z]{2}[A-Z0-9]{3}[0-9]{2}[0-9]{5}$'
            
            if not re.match(isrc_pattern, isrc.replace('-', '')):
                return {
                    "passed": False,
                    "message": "ISRC format is invalid. Should be CC-XXX-YY-NNNNN or CCXXXYYNNNNN",
                    "suggested_fix": "Correct ISRC format or generate a new valid ISRC",
                    "affected_fields": ["ddex_metadata.isrc"],
                    "blocking": False
                }
        
        return {"passed": True}
    
    async def validate_contributor_info(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate contributor information completeness"""
        
        contributors = content_record.ddex_metadata.contributors
        incomplete_contributors = []
        
        for contributor in contributors:
            if not contributor.name or not contributor.role or contributor.percentage <= 0:
                incomplete_contributors.append(contributor.name or "Unknown")
        
        if incomplete_contributors:
            return {
                "passed": False,
                "message": f"Incomplete contributor information for: {', '.join(incomplete_contributors)}",
                "suggested_fix": "Complete contributor information including name, role, and percentage",
                "affected_fields": ["ddex_metadata.contributors"],
                "blocking": True
            }
        
        # Check if percentages add up to 100%
        total_percentage = sum(c.percentage for c in contributors)
        if abs(total_percentage - 100.0) > 0.01:
            return {
                "passed": False,
                "message": f"Contributor percentages total {total_percentage}% but should total 100%",
                "suggested_fix": "Adjust contributor percentages to total exactly 100%",
                "affected_fields": ["ddex_metadata.contributors"],
                "blocking": True
            }
        
        return {"passed": True}
    
    async def validate_industry_standards(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate industry standards compliance"""
        
        # Basic industry standards check
        issues = []
        
        # Check for minimum metadata standards
        if len(content_record.ddex_metadata.genre) == 0:
            issues.append("At least one genre must be specified")
        
        if len(content_record.ddex_metadata.keywords) == 0:
            issues.append("Keywords should be provided for discoverability")
        
        if not content_record.ddex_metadata.label_name:
            issues.append("Label name should be specified")
        
        if issues:
            return {
                "passed": False,
                "message": f"Industry standards issues: {'; '.join(issues)}",
                "suggested_fix": "Address industry standard requirements for better distribution",
                "affected_fields": ["ddex_metadata.genre", "ddex_metadata.keywords", "ddex_metadata.label_name"],
                "blocking": False
            }
        
        return {"passed": True}
    
    async def validate_platform_requirements(self, content_record: ContentIngestionRecord) -> Dict[str, Any]:
        """Validate platform-specific requirements"""
        
        # This would check against specific platform requirements
        # For now, basic validation
        
        if not content_record.ddex_metadata.isrc:
            return {
                "passed": False,
                "message": "ISRC is required for most major platforms (Spotify, Apple Music, etc.)",
                "suggested_fix": "Generate and assign an ISRC code",
                "affected_fields": ["ddex_metadata.isrc"],
                "auto_fixable": True,
                "auto_fix": {
                    "action": "generate_isrc",
                    "description": "Generate new ISRC code",
                    "field": "ddex_metadata.isrc"
                },
                "blocking": False
            }
        
        return {"passed": True}
    
    async def _apply_auto_fix(self, content_record: ContentIngestionRecord, auto_fix: Dict[str, Any]) -> bool:
        """Apply automatic fix to content record"""
        
        try:
            action = auto_fix.get("action")
            field = auto_fix.get("field")
            value = auto_fix.get("value")
            
            if action == "set_explicit_flag":
                content_record.ddex_metadata.explicit_content = True
                return True
            elif action == "set_parental_warning":
                content_record.ddex_metadata.parental_warning = True
                return True
            elif action == "generate_isrc":
                # This would integrate with ISRC generation service
                new_isrc = f"US{datetime.now().strftime('%y')}B{str(hash(content_record.content_id))[-5:]}"
                content_record.ddex_metadata.isrc = new_isrc
                return True
            
            return False
            
        except Exception as e:
            print(f"Auto-fix failed: {str(e)}")
            return False
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get summary of available compliance rules"""
        
        summary = {
            "total_rules": len(self.compliance_rules),
            "rules_by_type": {},
            "rules_by_severity": {},
            "supported_territories": list(self.geo_restrictions_db.keys()),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Count by type
        for rule in self.compliance_rules:
            rule_type = rule.rule_type.value
            summary["rules_by_type"][rule_type] = summary["rules_by_type"].get(rule_type, 0) + 1
        
        # Count by severity
        for rule in self.compliance_rules:
            severity = rule.severity.value
            summary["rules_by_severity"][severity] = summary["rules_by_severity"].get(severity, 0) + 1
        
        return summary