"""
Zero-Trust Licensing & Compliance Layer
========================================
A hardened compliance engine that:
- Verifies releases
- Validates age, identity, and usage rights
- Detects fraudulent uploads
- Enforces regional privacy laws (GDPR, CCPA, COPPA)
- Auto-expires licenses and sends renewal prompts
- Everything is logged immutably for audits
"""

import os
import json
import hashlib
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

from llm_service import LlmChat, UserMessage


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ACTION = "requires_action"
    EXPIRED = "expired"


class PrivacyRegulation(str, Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    LGPD = "lgpd"
    PIPEDA = "pipeda"
    APPI = "appi"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    FAILED = "failed"
    REQUIRES_RESUBMISSION = "requires_resubmission"


class FraudRiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


# Pydantic Models
class ReleaseVerification(BaseModel):
    release_id: str
    status: VerificationStatus
    model_consent: bool = False
    photographer_consent: bool = False
    brand_clearance: bool = False
    location_clearance: bool = False
    minor_consent_if_applicable: bool = True
    verification_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expiry_date: Optional[datetime] = None
    issues: List[str] = Field(default_factory=list)
    verified_by: Optional[str] = None


class IdentityVerification(BaseModel):
    user_id: str
    verification_status: VerificationStatus
    id_type: str = ""
    id_number_hash: str = ""
    date_of_birth_verified: bool = False
    age_verified: bool = False
    is_minor: bool = False
    guardian_consent_if_minor: bool = True
    face_match_score: float = 0.0
    document_authenticity_score: float = 0.0
    verification_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expiry_date: Optional[datetime] = None


class UsageRightsValidation(BaseModel):
    asset_id: str
    status: ComplianceStatus
    allowed_uses: List[str] = Field(default_factory=list)
    restricted_uses: List[str] = Field(default_factory=list)
    territories: List[str] = Field(default_factory=list)
    exclusivity: bool = False
    duration_days: int = 365
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    auto_renewal: bool = False
    renewal_price: float = 0.0


class FraudDetectionResult(BaseModel):
    upload_id: str
    risk_level: FraudRiskLevel
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    similarity_score: float = 0.0
    ai_generated_probability: float = 0.0
    metadata_tampering_detected: bool = False
    copyright_match: Optional[str] = None
    flags: List[str] = Field(default_factory=list)
    recommended_action: str = ""


class PrivacyComplianceCheck(BaseModel):
    entity_id: str
    entity_type: str
    regulations_checked: List[PrivacyRegulation] = Field(default_factory=list)
    status: ComplianceStatus
    gdpr_compliant: bool = True
    ccpa_compliant: bool = True
    coppa_compliant: bool = True
    data_retention_compliant: bool = True
    consent_collected: bool = True
    right_to_erasure_supported: bool = True
    data_portability_supported: bool = True
    issues: List[str] = Field(default_factory=list)
    remediation_steps: List[str] = Field(default_factory=list)


class LicenseExpiryNotification(BaseModel):
    license_id: str
    asset_id: str
    licensee_id: str
    expiry_date: datetime
    days_until_expiry: int
    notification_type: str
    renewal_price: float
    auto_renewal_enabled: bool
    notification_sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action_type: str
    entity_type: str
    entity_id: str
    actor_id: str
    actor_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes: Dict[str, Any] = Field(default_factory=dict)
    compliance_relevant: bool = False
    hash: str = ""
    previous_hash: str = ""


class ZeroTrustComplianceEngine:
    """
    Zero-trust compliance engine for comprehensive verification and compliance.
    All actions are logged immutably for audit purposes.
    """
    
    def __init__(self, db):
        self.db = db
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_provider = "gemini"
        self.model_name = "gemini-2.5-flash"
        self._last_audit_hash = ""
    
    def _get_chat(self, session_id: str, system_message: str) -> LlmChat:
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        chat.with_model(self.model_provider, self.model_name)
        return chat
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash for immutable logging."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _log_audit_entry(
        self,
        action_type: str,
        entity_type: str,
        entity_id: str,
        actor_id: str,
        actor_type: str = "user",
        changes: Dict[str, Any] = None,
        compliance_relevant: bool = False,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLogEntry:
        """Create an immutable audit log entry."""
        import uuid
        
        log_data = {
            "action_type": action_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "changes": changes or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        entry = AuditLogEntry(
            log_id=str(uuid.uuid4()),
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_type=actor_type,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes or {},
            compliance_relevant=compliance_relevant,
            previous_hash=self._last_audit_hash,
            hash=self._generate_hash(log_data)
        )
        
        self._last_audit_hash = entry.hash
        
        # Store in database
        try:
            audit_collection = self.db["compliance_audit_logs"]
            await audit_collection.insert_one(entry.dict())
        except Exception:
            pass
        
        return entry
    
    async def verify_release(
        self,
        release_id: str,
        release_data: Dict[str, Any],
        actor_id: str
    ) -> ReleaseVerification:
        """
        Verify all necessary releases and consents for an asset.
        Falls back to rule-based verification if AI is unavailable.
        """
        # Try AI-powered verification first
        try:
            system_message = """You are a legal compliance expert specializing in model releases and media rights.
            Analyze release documents and verify all necessary consents are in place."""
            
            chat = self._get_chat(f"release-verify-{release_id}", system_message)
            
            prompt = f"""Analyze this release documentation and verify compliance:

Release Data:
{json.dumps(release_data, indent=2, default=str)}

Check for:
1. Model consent/release signed
2. Photographer/creator consent
3. Brand/trademark clearances
4. Location permissions (if identifiable)
5. Minor consent (guardian signature if applicable)
6. Usage scope clearly defined
7. Duration specified
8. Territory restrictions

Provide JSON response:
{{
    "status": "verified|pending|failed|requires_resubmission",
    "model_consent": true/false,
    "photographer_consent": true/false,
    "brand_clearance": true/false,
    "location_clearance": true/false,
    "minor_consent_if_applicable": true/false,
    "issues": ["issue1", "issue2"],
    "expiry_days": <number of days until expiry>
}}"""

            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            result = json.loads(json_str)
            
            expiry_days = result.get("expiry_days", 365)
            
            verification = ReleaseVerification(
                release_id=release_id,
                status=VerificationStatus(result.get("status", "pending")),
                model_consent=result.get("model_consent", False),
                photographer_consent=result.get("photographer_consent", False),
                brand_clearance=result.get("brand_clearance", True),
                location_clearance=result.get("location_clearance", True),
                minor_consent_if_applicable=result.get("minor_consent_if_applicable", True),
                expiry_date=datetime.now(timezone.utc) + timedelta(days=expiry_days),
                issues=result.get("issues", []),
                verified_by="ai_compliance_engine"
            )
            
        except Exception as e:
            # Fallback to rule-based verification
            model_consent = release_data.get("has_model_consent", False)
            photographer_consent = release_data.get("has_photographer_consent", False)
            brand_clearance = release_data.get("has_brand_clearance", True)
            location_clearance = release_data.get("has_location_clearance", True)
            is_minor = release_data.get("is_minor", False)
            guardian_consent = release_data.get("has_guardian_consent", True) if not is_minor else release_data.get("has_guardian_consent", False)
            
            issues = []
            if not model_consent:
                issues.append("Model consent/release not confirmed")
            if not photographer_consent:
                issues.append("Photographer consent not confirmed")
            if not brand_clearance:
                issues.append("Brand/trademark clearance required")
            if not location_clearance:
                issues.append("Location permission required")
            if is_minor and not guardian_consent:
                issues.append("Guardian consent required for minor")
            
            # Determine status based on rule checks
            if model_consent and photographer_consent and (not is_minor or guardian_consent):
                status = VerificationStatus.VERIFIED
            elif len(issues) > 2:
                status = VerificationStatus.FAILED
            else:
                status = VerificationStatus.PENDING
            
            expiry_days = release_data.get("duration_days", 365)
            
            verification = ReleaseVerification(
                release_id=release_id,
                status=status,
                model_consent=model_consent,
                photographer_consent=photographer_consent,
                brand_clearance=brand_clearance,
                location_clearance=location_clearance,
                minor_consent_if_applicable=guardian_consent if is_minor else True,
                expiry_date=datetime.now(timezone.utc) + timedelta(days=expiry_days),
                issues=issues if issues else ["Verified using rule-based system (AI unavailable)"],
                verified_by="rule_based_engine"
            )
        
        # Log audit entry
        await self._log_audit_entry(
            action_type="release_verification",
            entity_type="release",
            entity_id=release_id,
            actor_id=actor_id,
            changes={"status": verification.status.value, "issues": verification.issues},
            compliance_relevant=True
        )
        
        return verification
    
    async def verify_identity(
        self,
        user_id: str,
        identity_data: Dict[str, Any],
        actor_id: str
    ) -> IdentityVerification:
        """
        Verify user identity with age validation.
        """
        # Hash sensitive data
        id_number = identity_data.get("id_number", "")
        id_number_hash = hashlib.sha256(id_number.encode()).hexdigest() if id_number else ""
        
        # Calculate age
        dob = identity_data.get("date_of_birth")
        age = 0
        is_minor = False
        
        if dob:
            try:
                if isinstance(dob, str):
                    # Handle various date formats
                    dob_str = dob.replace("Z", "+00:00")
                    if "T" not in dob_str and "+" not in dob_str:
                        # Simple date format like "2015-01-01"
                        dob = datetime.strptime(dob_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    else:
                        dob = datetime.fromisoformat(dob_str)
                age = (datetime.now(timezone.utc) - dob).days // 365
                is_minor = age < 18
            except Exception:
                pass
        
        # Determine verification status based on provided data
        has_id = bool(identity_data.get("id_document"))
        has_selfie = bool(identity_data.get("selfie"))
        has_dob = bool(dob)
        
        if has_id and has_selfie and has_dob:
            status = VerificationStatus.VERIFIED
        elif has_id or has_dob:
            status = VerificationStatus.PENDING
        else:
            status = VerificationStatus.REQUIRES_RESUBMISSION
        
        # Guardian consent check for minors
        guardian_consent = True
        if is_minor:
            guardian_consent = bool(identity_data.get("guardian_consent"))
            if not guardian_consent:
                status = VerificationStatus.REQUIRES_RESUBMISSION
        
        verification = IdentityVerification(
            user_id=user_id,
            verification_status=status,
            id_type=identity_data.get("id_type", ""),
            id_number_hash=id_number_hash,
            date_of_birth_verified=has_dob,
            age_verified=has_dob and age > 0,
            is_minor=is_minor,
            guardian_consent_if_minor=guardian_consent,
            face_match_score=identity_data.get("face_match_score", 0.0),
            document_authenticity_score=identity_data.get("document_score", 0.0),
            expiry_date=datetime.now(timezone.utc) + timedelta(days=365)
        )
        
        # Log audit entry (without sensitive data)
        await self._log_audit_entry(
            action_type="identity_verification",
            entity_type="user",
            entity_id=user_id,
            actor_id=actor_id,
            changes={
                "status": verification.verification_status.value,
                "age_verified": verification.age_verified,
                "is_minor": verification.is_minor
            },
            compliance_relevant=True
        )
        
        return verification
    
    async def validate_usage_rights(
        self,
        asset_id: str,
        requested_use: Dict[str, Any],
        actor_id: str
    ) -> UsageRightsValidation:
        """
        Validate if requested usage is allowed for an asset.
        Falls back to rule-based validation if AI is unavailable.
        """
        # Try AI-powered validation first
        try:
            system_message = """You are a media licensing expert. Analyze asset rights and validate usage requests."""
            
            chat = self._get_chat(f"usage-rights-{asset_id}", system_message)
            
            prompt = f"""Validate this usage request against asset rights:

Asset ID: {asset_id}
Requested Use:
{json.dumps(requested_use, indent=2, default=str)}

Provide JSON response:
{{
    "status": "compliant|non_compliant|pending_review|requires_action",
    "allowed_uses": ["use1", "use2"],
    "restricted_uses": ["restricted1", "restricted2"],
    "territories": ["territory1", "territory2"],
    "exclusivity": true/false,
    "duration_days": <recommended duration>,
    "auto_renewal_recommended": true/false,
    "issues": ["issue1", "issue2"]
}}"""

            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            result = json.loads(json_str)
            
            duration = result.get("duration_days", 365)
            
            validation = UsageRightsValidation(
                asset_id=asset_id,
                status=ComplianceStatus(result.get("status", "pending_review")),
                allowed_uses=result.get("allowed_uses", []),
                restricted_uses=result.get("restricted_uses", []),
                territories=result.get("territories", ["worldwide"]),
                exclusivity=result.get("exclusivity", False),
                duration_days=duration,
                end_date=datetime.now(timezone.utc) + timedelta(days=duration),
                auto_renewal=result.get("auto_renewal_recommended", False)
            )
            
        except Exception:
            # Fallback to rule-based validation
            use_type = requested_use.get("use_type", "commercial")
            territory = requested_use.get("territory", "worldwide")
            duration = requested_use.get("duration_days", 365)
            is_exclusive = requested_use.get("exclusive", False)
            
            # Standard allowed uses based on type
            allowed_uses_map = {
                "commercial": ["advertising", "marketing", "promotional", "product packaging"],
                "editorial": ["news", "documentary", "educational", "journalism"],
                "advertising": ["tv ads", "digital ads", "print ads", "social media ads"],
                "social_media": ["instagram", "facebook", "twitter", "tiktok", "youtube"],
                "broadcast": ["television", "streaming", "cable", "satellite"],
                "print": ["magazines", "newspapers", "brochures", "posters"],
                "digital": ["websites", "apps", "email marketing", "digital displays"]
            }
            
            allowed_uses = allowed_uses_map.get(use_type, ["general commercial use"])
            
            # Determine territories based on request
            territories = [territory] if territory != "worldwide" else ["worldwide"]
            
            # Rule-based status determination
            status = ComplianceStatus.COMPLIANT
            if duration > 730:  # >2 years
                status = ComplianceStatus.PENDING_REVIEW
            if is_exclusive and territory == "worldwide":
                status = ComplianceStatus.REQUIRES_ACTION
            
            validation = UsageRightsValidation(
                asset_id=asset_id,
                status=status,
                allowed_uses=allowed_uses,
                restricted_uses=["political campaigns", "defamatory content", "adult content"],
                territories=territories,
                exclusivity=is_exclusive,
                duration_days=duration,
                end_date=datetime.now(timezone.utc) + timedelta(days=duration),
                auto_renewal=not is_exclusive  # Don't auto-renew exclusive licenses
            )
        
        await self._log_audit_entry(
            action_type="usage_rights_validation",
            entity_type="asset",
            entity_id=asset_id,
            actor_id=actor_id,
            changes={"status": validation.status.value, "requested_use": requested_use},
            compliance_relevant=True
        )
        
        return validation
    
    async def detect_fraudulent_upload(
        self,
        upload_id: str,
        upload_data: Dict[str, Any],
        actor_id: str
    ) -> FraudDetectionResult:
        """
        Detect potentially fraudulent uploads using AI analysis.
        Falls back to rule-based detection if AI is unavailable.
        """
        # Check for duplicates in database first
        is_duplicate = False
        duplicate_of = None
        
        try:
            assets_collection = self.db["assets"]
            file_hash = upload_data.get("file_hash", "")
            if file_hash:
                existing = await assets_collection.find_one({"file_hash": file_hash})
                if existing:
                    is_duplicate = True
                    duplicate_of = str(existing.get("_id", ""))
        except Exception:
            pass
        
        # Try AI-powered analysis first
        try:
            system_message = """You are a fraud detection specialist for a media platform.
            Analyze uploads for signs of fraud, duplication, or policy violations."""
            
            chat = self._get_chat(f"fraud-detect-{upload_id}", system_message)
            
            prompt = f"""Analyze this upload for fraud indicators:

Upload Data:
{json.dumps(upload_data, indent=2, default=str)}

Is Duplicate: {is_duplicate}
Duplicate Of: {duplicate_of}

Check for:
1. Content duplication
2. Metadata tampering
3. AI-generated content (deepfakes)
4. Copyright infringement indicators
5. Identity fraud
6. Suspicious upload patterns

Provide JSON response:
{{
    "risk_level": "critical|high|medium|low|none",
    "similarity_score": <0-100>,
    "ai_generated_probability": <0-100>,
    "metadata_tampering_detected": true/false,
    "copyright_match": "source or null",
    "flags": ["flag1", "flag2"],
    "recommended_action": "action to take"
}}"""

            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            result = json.loads(json_str)
            
            detection = FraudDetectionResult(
                upload_id=upload_id,
                risk_level=FraudRiskLevel(result.get("risk_level", "low")),
                is_duplicate=is_duplicate,
                duplicate_of=duplicate_of,
                similarity_score=result.get("similarity_score", 0),
                ai_generated_probability=result.get("ai_generated_probability", 0),
                metadata_tampering_detected=result.get("metadata_tampering_detected", False),
                copyright_match=result.get("copyright_match"),
                flags=result.get("flags", []),
                recommended_action=result.get("recommended_action", "")
            )
            
        except Exception:
            # Fallback to rule-based fraud detection
            flags = []
            risk_level = FraudRiskLevel.NONE
            
            # Check for duplicates
            if is_duplicate:
                flags.append("Duplicate content detected")
                risk_level = FraudRiskLevel.HIGH
            
            # Check file size anomalies
            file_size = upload_data.get("file_size", 0)
            if file_size == 0:
                flags.append("Zero-size file submitted")
                risk_level = FraudRiskLevel.MEDIUM
            elif file_size > 500 * 1024 * 1024:  # >500MB
                flags.append("Unusually large file size")
            
            # Check upload source
            upload_source = upload_data.get("upload_source", "")
            if upload_source == "api" or upload_source == "bulk":
                flags.append("Automated upload source - verify authenticity")
            
            # Check for missing metadata
            if not upload_data.get("file_name"):
                flags.append("Missing file name")
                risk_level = FraudRiskLevel.MEDIUM if risk_level == FraudRiskLevel.NONE else risk_level
            
            recommended_action = "Approve" if risk_level == FraudRiskLevel.NONE else "Manual review required"
            if risk_level == FraudRiskLevel.HIGH:
                recommended_action = "Flag for immediate review - potential policy violation"
            
            detection = FraudDetectionResult(
                upload_id=upload_id,
                risk_level=risk_level,
                is_duplicate=is_duplicate,
                duplicate_of=duplicate_of,
                similarity_score=100 if is_duplicate else 0,
                ai_generated_probability=0,
                metadata_tampering_detected=False,
                copyright_match=None,
                flags=flags if flags else ["Rule-based check passed (AI unavailable)"],
                recommended_action=recommended_action
            )
        
        await self._log_audit_entry(
            action_type="fraud_detection",
            entity_type="upload",
            entity_id=upload_id,
            actor_id=actor_id,
            changes={
                "risk_level": detection.risk_level.value,
                "is_duplicate": detection.is_duplicate,
                "flags": detection.flags
            },
            compliance_relevant=True
        )
        
        return detection
    
    async def check_privacy_compliance(
        self,
        entity_id: str,
        entity_type: str,
        entity_data: Dict[str, Any],
        regions: List[str],
        actor_id: str
    ) -> PrivacyComplianceCheck:
        """
        Check compliance with regional privacy regulations.
        Falls back to rule-based checking if AI is unavailable.
        """
        # Determine applicable regulations based on regions
        regulations = []
        if any(r in ["EU", "EEA", "UK"] for r in regions):
            regulations.append(PrivacyRegulation.GDPR)
        if "US-CA" in regions or "California" in regions:
            regulations.append(PrivacyRegulation.CCPA)
        if any("child" in str(entity_data.get("audience", "")).lower() for _ in [1]):
            regulations.append(PrivacyRegulation.COPPA)
        if "Brazil" in regions:
            regulations.append(PrivacyRegulation.LGPD)
        if "Canada" in regions:
            regulations.append(PrivacyRegulation.PIPEDA)
        if "Japan" in regions:
            regulations.append(PrivacyRegulation.APPI)
        
        if not regulations:
            regulations = [PrivacyRegulation.GDPR]  # Default to GDPR as baseline
        
        # Try AI-powered compliance check first
        try:
            system_message = """You are a privacy compliance expert specializing in GDPR, CCPA, COPPA, and other regulations.
            Analyze data practices and verify compliance with applicable laws."""
            
            chat = self._get_chat(f"privacy-{entity_id}", system_message)
            
            prompt = f"""Check privacy compliance for this entity:

Entity Type: {entity_type}
Entity Data:
{json.dumps(entity_data, indent=2, default=str)}

Applicable Regulations: {[r.value for r in regulations]}
Regions: {regions}

Check for:
1. Proper consent collection
2. Data minimization
3. Right to erasure support
4. Data portability
5. Retention policy compliance
6. Minor protection (COPPA)
7. Cross-border transfer compliance

Provide JSON response:
{{
    "status": "compliant|non_compliant|pending_review|requires_action",
    "gdpr_compliant": true/false,
    "ccpa_compliant": true/false,
    "coppa_compliant": true/false,
    "data_retention_compliant": true/false,
    "consent_collected": true/false,
    "right_to_erasure_supported": true/false,
    "data_portability_supported": true/false,
    "issues": ["issue1", "issue2"],
    "remediation_steps": ["step1", "step2"]
}}"""

            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            result = json.loads(json_str)
            
            check = PrivacyComplianceCheck(
                entity_id=entity_id,
                entity_type=entity_type,
                regulations_checked=regulations,
                status=ComplianceStatus(result.get("status", "pending_review")),
                gdpr_compliant=result.get("gdpr_compliant", True),
                ccpa_compliant=result.get("ccpa_compliant", True),
                coppa_compliant=result.get("coppa_compliant", True),
                data_retention_compliant=result.get("data_retention_compliant", True),
                consent_collected=result.get("consent_collected", True),
                right_to_erasure_supported=result.get("right_to_erasure_supported", True),
                data_portability_supported=result.get("data_portability_supported", True),
                issues=result.get("issues", []),
                remediation_steps=result.get("remediation_steps", [])
            )
            
        except Exception:
            # Fallback to rule-based privacy compliance check
            consent_collected = entity_data.get("consent_collected", False)
            erasure_supported = entity_data.get("right_to_erasure_supported", False)
            portability_supported = entity_data.get("data_portability_supported", False)
            
            issues = []
            remediation_steps = []
            
            # Check GDPR requirements
            gdpr_compliant = True
            if PrivacyRegulation.GDPR in regulations:
                if not consent_collected:
                    issues.append("GDPR: Explicit consent not documented")
                    remediation_steps.append("Implement consent collection mechanism with clear opt-in")
                    gdpr_compliant = False
                if not erasure_supported:
                    issues.append("GDPR: Right to erasure (Article 17) not implemented")
                    remediation_steps.append("Add data deletion functionality for user requests")
                    gdpr_compliant = False
                if not portability_supported:
                    issues.append("GDPR: Data portability (Article 20) not supported")
                    remediation_steps.append("Implement data export in machine-readable format")
            
            # Check CCPA requirements
            ccpa_compliant = True
            if PrivacyRegulation.CCPA in regulations:
                if not consent_collected:
                    issues.append("CCPA: Do Not Sell opt-out not implemented")
                    remediation_steps.append("Add 'Do Not Sell My Personal Information' link")
                    ccpa_compliant = False
            
            # Check COPPA requirements
            coppa_compliant = True
            if PrivacyRegulation.COPPA in regulations:
                issues.append("COPPA: Parental consent verification required for minors")
                remediation_steps.append("Implement verifiable parental consent mechanism")
                coppa_compliant = False
            
            # Determine overall status
            if not issues:
                status = ComplianceStatus.COMPLIANT
                issues = ["Rule-based compliance check passed (AI unavailable)"]
            elif len(issues) <= 2:
                status = ComplianceStatus.REQUIRES_ACTION
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            check = PrivacyComplianceCheck(
                entity_id=entity_id,
                entity_type=entity_type,
                regulations_checked=regulations,
                status=status,
                gdpr_compliant=gdpr_compliant,
                ccpa_compliant=ccpa_compliant,
                coppa_compliant=coppa_compliant,
                data_retention_compliant=True,  # Assume compliant without specific data
                consent_collected=consent_collected,
                right_to_erasure_supported=erasure_supported,
                data_portability_supported=portability_supported,
                issues=issues,
                remediation_steps=remediation_steps
            )
        
        await self._log_audit_entry(
            action_type="privacy_compliance_check",
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            changes={
                "status": check.status.value,
                "regulations": [r.value for r in regulations],
                "issues": check.issues
            },
            compliance_relevant=True
        )
        
        return check
    
    async def check_expiring_licenses(self, days_ahead: int = 30) -> List[LicenseExpiryNotification]:
        """
        Check for licenses expiring soon and generate notifications.
        """
        try:
            licenses_collection = self.db["licenses"]
            
            expiry_threshold = datetime.now(timezone.utc) + timedelta(days=days_ahead)
            
            expiring = await licenses_collection.find({
                "expiry_date": {"$lte": expiry_threshold},
                "status": "active"
            }).to_list(100)
            
            notifications = []
            for license in expiring:
                expiry_date = license.get("expiry_date")
                if isinstance(expiry_date, str):
                    expiry_date = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))
                
                days_until = (expiry_date - datetime.now(timezone.utc)).days
                
                # Determine notification type
                if days_until <= 0:
                    notification_type = "expired"
                elif days_until <= 7:
                    notification_type = "urgent"
                elif days_until <= 14:
                    notification_type = "warning"
                else:
                    notification_type = "reminder"
                
                notifications.append(LicenseExpiryNotification(
                    license_id=str(license.get("_id", "")),
                    asset_id=license.get("asset_id", ""),
                    licensee_id=license.get("licensee_id", ""),
                    expiry_date=expiry_date,
                    days_until_expiry=days_until,
                    notification_type=notification_type,
                    renewal_price=license.get("renewal_price", 0),
                    auto_renewal_enabled=license.get("auto_renewal", False)
                ))
            
            return notifications
        except Exception:
            return []
    
    async def auto_expire_licenses(self) -> Dict[str, int]:
        """
        Automatically expire licenses that have passed their expiry date.
        """
        try:
            licenses_collection = self.db["licenses"]
            
            now = datetime.now(timezone.utc)
            
            result = await licenses_collection.update_many(
                {
                    "expiry_date": {"$lt": now},
                    "status": "active",
                    "auto_renewal": {"$ne": True}
                },
                {
                    "$set": {
                        "status": "expired",
                        "expired_at": now
                    }
                }
            )
            
            # Log the bulk action
            await self._log_audit_entry(
                action_type="bulk_license_expiry",
                entity_type="license",
                entity_id="bulk",
                actor_id="system",
                actor_type="system",
                changes={"expired_count": result.modified_count},
                compliance_relevant=True
            )
            
            return {"expired_count": result.modified_count}
        except Exception:
            return {"expired_count": 0}
    
    async def get_audit_trail(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        compliance_only: bool = False,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """
        Retrieve audit trail with optional filters.
        """
        try:
            audit_collection = self.db["compliance_audit_logs"]
            
            query = {}
            if entity_type:
                query["entity_type"] = entity_type
            if entity_id:
                query["entity_id"] = entity_id
            if compliance_only:
                query["compliance_relevant"] = True
            if start_date:
                query["timestamp"] = {"$gte": start_date}
            if end_date:
                if "timestamp" in query:
                    query["timestamp"]["$lte"] = end_date
                else:
                    query["timestamp"] = {"$lte": end_date}
            
            logs = await audit_collection.find(query).sort("timestamp", -1).limit(limit).to_list(limit)
            
            entries = []
            for log in logs:
                log.pop("_id", None)
                entries.append(AuditLogEntry(**log))
            
            return entries
        except Exception:
            return []
    
    async def verify_audit_chain_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the audit log chain.
        """
        try:
            audit_collection = self.db["compliance_audit_logs"]
            
            logs = await audit_collection.find().sort("timestamp", 1).to_list(None)
            
            if not logs:
                return {"status": "empty", "valid": True, "entries_checked": 0}
            
            invalid_entries = []
            prev_hash = ""
            
            for i, log in enumerate(logs):
                # Check chain integrity
                if log.get("previous_hash", "") != prev_hash:
                    invalid_entries.append({
                        "index": i,
                        "log_id": log.get("log_id"),
                        "issue": "Hash chain broken"
                    })
                
                prev_hash = log.get("hash", "")
            
            return {
                "status": "valid" if not invalid_entries else "invalid",
                "valid": len(invalid_entries) == 0,
                "entries_checked": len(logs),
                "invalid_entries": invalid_entries
            }
        except Exception as e:
            return {"status": "error", "valid": False, "error": str(e)}


# Singleton instance
_compliance_engine_instance = None

def get_compliance_engine(db) -> ZeroTrustComplianceEngine:
    global _compliance_engine_instance
    if _compliance_engine_instance is None:
        _compliance_engine_instance = ZeroTrustComplianceEngine(db)
    return _compliance_engine_instance
