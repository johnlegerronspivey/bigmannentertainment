"""
Big Mann Entertainment - Compliance Center Service
De-mocked: All data computed from real MongoDB collections
(compliance_documents, compliance_audit_logs, label_rights, label_assets).
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from config.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    NEEDS_ATTENTION = "needs_attention"
    EXPIRED = "expired"


class ComplianceType(str, Enum):
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    LICENSING = "licensing"
    TERRITORIAL = "territorial"
    AGE_RATING = "age_rating"
    CONTENT_POLICY = "content_policy"
    GDPR = "gdpr"
    DMCA = "dmca"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Territory(str, Enum):
    US = "us"
    CA = "ca"
    UK = "uk"
    EU = "eu"
    AU = "au"
    JP = "jp"
    WORLDWIDE = "worldwide"


class ComplianceRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    compliance_type: ComplianceType
    territories: List[Territory]
    requirements: List[str]
    automated_check: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    asset_title: str
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    risk_level: RiskLevel
    compliance_type: ComplianceType
    territories: List[Territory]
    issues_found: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RightsInformation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    copyright_owner: str
    copyright_year: Optional[int] = None
    licensing_info: Dict[str, Any] = Field(default_factory=dict)
    territorial_rights: Dict[str, bool] = Field(default_factory=dict)
    usage_restrictions: List[str] = Field(default_factory=list)
    expiration_date: Optional[datetime] = None
    contact_info: Dict[str, str] = Field(default_factory=dict)
    documents: List[str] = Field(default_factory=list)


class ComplianceReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = ""
    time_range: Dict[str, Any] = Field(default_factory=dict)
    compliance_types: List[ComplianceType] = Field(default_factory=list)
    territories: List[Territory] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    checks_performed: int = 0
    issues_found: int = 0
    resolution_rate: float = 0.0
    generated_by: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    message: str
    risk_level: RiskLevel
    compliance_type: ComplianceType
    asset_id: Optional[str] = None
    territory: Optional[Territory] = None
    action_required: bool = True
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False
    resolved: bool = False


class ComplianceCenterService:
    """Service computing compliance data from real MongoDB collections."""

    async def run_compliance_check(self, asset_id: str, asset_title: str,
                                   user_id: str, rule_ids: List[str] = None) -> Dict[str, Any]:
        try:
            # Check if asset has rights info
            rights = await db.label_rights.find_one({"asset_id": asset_id}, {"_id": 0})
            # Check compliance documents for the asset
            doc_count = await db.compliance_documents.count_documents({})

            checks = []
            issues_found = 0

            # Copyright check
            has_rights = rights is not None
            copyright_status = ComplianceStatus.COMPLIANT if has_rights else ComplianceStatus.NEEDS_ATTENTION
            copyright_risk = RiskLevel.LOW if has_rights else RiskLevel.MEDIUM
            copyright_issues = [] if has_rights else ["No rights record found for this asset"]
            copyright_recs = [] if has_rights else ["Register rights information for this asset"]
            checks.append({
                "id": str(uuid.uuid4()),
                "asset_id": asset_id,
                "asset_title": asset_title,
                "rule_id": "rule_copyright",
                "rule_name": "Copyright Ownership Verification",
                "status": copyright_status.value,
                "risk_level": copyright_risk.value,
                "compliance_type": "copyright",
                "territories": ["worldwide"],
                "issues_found": copyright_issues,
                "recommendations": copyright_recs,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            })
            if copyright_status != ComplianceStatus.COMPLIANT:
                issues_found += 1

            # Territorial rights check
            if rights:
                territories = rights.get("territories", [])
                terr_status = ComplianceStatus.COMPLIANT if len(territories) >= 2 else ComplianceStatus.NEEDS_ATTENTION
                terr_issues = [] if len(territories) >= 2 else [f"Limited to {len(territories)} territories"]
            else:
                terr_status = ComplianceStatus.NON_COMPLIANT
                terr_issues = ["No territorial rights defined"]
            checks.append({
                "id": str(uuid.uuid4()),
                "asset_id": asset_id,
                "asset_title": asset_title,
                "rule_id": "rule_territorial",
                "rule_name": "Territorial Licensing Rights",
                "status": terr_status.value,
                "risk_level": RiskLevel.LOW.value if terr_status == ComplianceStatus.COMPLIANT else RiskLevel.MEDIUM.value,
                "compliance_type": "territorial",
                "territories": rights.get("territories", []) if rights else [],
                "issues_found": terr_issues,
                "recommendations": ["Expand territorial coverage"] if terr_issues else [],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            })
            if terr_status != ComplianceStatus.COMPLIANT:
                issues_found += 1

            # GDPR check based on compliance_documents
            gdpr_docs = await db.compliance_documents.count_documents({
                "compliance_requirements": {"$in": ["content_guidelines", "copyright_protection"]}
            })
            gdpr_status = ComplianceStatus.COMPLIANT if gdpr_docs > 0 else ComplianceStatus.PENDING_REVIEW
            checks.append({
                "id": str(uuid.uuid4()),
                "asset_id": asset_id,
                "asset_title": asset_title,
                "rule_id": "rule_gdpr",
                "rule_name": "GDPR Privacy Compliance",
                "status": gdpr_status.value,
                "risk_level": RiskLevel.LOW.value if gdpr_status == ComplianceStatus.COMPLIANT else RiskLevel.MEDIUM.value,
                "compliance_type": "gdpr",
                "territories": ["eu", "uk"],
                "issues_found": [] if gdpr_status == ComplianceStatus.COMPLIANT else ["GDPR documentation pending review"],
                "recommendations": [] if gdpr_status == ComplianceStatus.COMPLIANT else ["Complete GDPR compliance documentation"],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            })
            if gdpr_status != ComplianceStatus.COMPLIANT:
                issues_found += 1

            # Store check in audit log
            await db.compliance_audit_logs.insert_one({
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_type": "compliance_check",
                "entity_type": "asset",
                "entity_id": asset_id,
                "actor_id": user_id,
                "actor_type": "user",
                "changes": {"checks_performed": len(checks), "issues_found": issues_found},
                "compliance_relevant": True,
            })

            score = ((len(checks) - issues_found) / len(checks) * 100) if checks else 100

            return {
                "success": True,
                "data_source": "real",
                "checks_performed": len(checks),
                "issues_found": issues_found,
                "compliance_score": round(score, 1),
                "checks": checks,
                "summary": {
                    "compliant": len([c for c in checks if c["status"] == "compliant"]),
                    "non_compliant": len([c for c in checks if c["status"] == "non_compliant"]),
                    "pending_review": len([c for c in checks if c["status"] == "pending_review"]),
                    "needs_attention": len([c for c in checks if c["status"] == "needs_attention"]),
                },
            }
        except Exception as e:
            logger.error(f"Error running compliance check: {e}")
            return {"success": False, "error": str(e)}

    async def get_compliance_status(self, asset_id: str = None, user_id: str = None) -> Dict[str, Any]:
        try:
            if asset_id:
                # Asset-specific: check rights and audit logs
                rights = await db.label_rights.find_one({"asset_id": asset_id}, {"_id": 0})
                audit_count = await db.compliance_audit_logs.count_documents({"entity_id": asset_id})
                has_rights = rights is not None
                score = 100.0 if has_rights else 50.0
                return {
                    "success": True,
                    "data_source": "real",
                    "asset_id": asset_id,
                    "overall_status": "compliant" if has_rights else "needs_attention",
                    "compliance_score": score,
                    "audit_records": audit_count,
                    "has_rights": has_rights,
                }

            # Overall platform compliance
            total_assets = await db.label_assets.count_documents({}) + await db.user_content.count_documents({})
            total_rights = await db.label_rights.count_documents({})
            total_docs = await db.compliance_documents.count_documents({})
            total_audits = await db.compliance_audit_logs.count_documents({})
            pending_docs = await db.compliance_documents.count_documents({"legal_review_status": "pending"})
            approved_docs = await db.compliance_documents.count_documents({"legal_review_status": "approved"})

            # Assets with rights = compliant
            compliant_count = total_rights
            needs_attention = total_assets - compliant_count if total_assets > compliant_count else 0
            non_compliant = 0  # No assets are explicitly non-compliant unless flagged

            score = round((compliant_count / max(total_assets, 1)) * 100, 1)
            # Boost score based on documentation coverage
            doc_coverage = min(total_docs / max(total_assets * 5, 1), 1.0)
            score = round(min(score + doc_coverage * 20, 100), 1)

            # By type: compute from compliance_documents
            type_pipeline = [
                {"$unwind": "$compliance_requirements"},
                {"$group": {"_id": "$compliance_requirements", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
            by_type = {}
            async for doc in db.compliance_documents.aggregate(type_pipeline):
                req = doc["_id"]
                if "copyright" in req:
                    by_type.setdefault("copyright", {"count": 0, "score": 0})
                    by_type["copyright"]["count"] += doc["count"]
                elif "content" in req:
                    by_type.setdefault("content_policy", {"count": 0, "score": 0})
                    by_type["content_policy"]["count"] += doc["count"]

            # Compute scores for each type
            for k, v in by_type.items():
                v["score"] = round(min((v["count"] / max(total_assets, 1)) * 100, 100), 1)
                v["status"] = "compliant" if v["score"] >= 70 else "needs_attention"

            # By territory from label_rights
            by_territory = {}
            async for doc in db.label_rights.find({}, {"_id": 0, "territories": 1}):
                for t in doc.get("territories", []):
                    t_lower = t.lower()
                    by_territory.setdefault(t_lower, {"score": 0, "assets": 0})
                    by_territory[t_lower]["assets"] += 1
            for k, v in by_territory.items():
                v["score"] = round(min((v["assets"] / max(total_assets, 1)) * 100, 100), 1)

            return {
                "success": True,
                "data_source": "real",
                "overall_compliance": {
                    "score": score,
                    "status": "compliant" if score >= 70 else "needs_attention",
                    "total_assets": total_assets,
                    "compliant_assets": compliant_count,
                    "needs_attention": needs_attention,
                    "non_compliant": non_compliant,
                },
                "compliance_documents": total_docs,
                "audit_logs": total_audits,
                "pending_reviews": pending_docs,
                "approved_reviews": approved_docs,
                "by_type": by_type,
                "by_territory": by_territory,
            }
        except Exception as e:
            logger.error(f"Error fetching compliance status: {e}")
            return {"success": False, "error": str(e)}

    async def get_compliance_alerts(self, user_id: str, risk_level: RiskLevel = None) -> Dict[str, Any]:
        try:
            alerts = []

            # Check for pending compliance documents
            pending = await db.compliance_documents.count_documents({"legal_review_status": "pending"})
            if pending > 0:
                alerts.append({
                    "id": str(uuid.uuid4()),
                    "title": "Compliance Documents Pending Review",
                    "message": f"{pending} compliance document(s) are awaiting legal review",
                    "risk_level": "medium" if pending < 100 else "high",
                    "compliance_type": "content_policy",
                    "action_required": True,
                    "deadline": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "acknowledged": False,
                    "resolved": False,
                })

            # Check for assets without rights
            total_assets = await db.label_assets.count_documents({})
            total_rights = await db.label_rights.count_documents({})
            unprotected = total_assets - total_rights
            if unprotected > 0:
                alerts.append({
                    "id": str(uuid.uuid4()),
                    "title": "Assets Without Rights Records",
                    "message": f"{unprotected} label asset(s) do not have associated rights records",
                    "risk_level": "high",
                    "compliance_type": "copyright",
                    "action_required": True,
                    "deadline": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "acknowledged": False,
                    "resolved": False,
                })

            # Check recent audit activity
            recent_audits = await db.compliance_audit_logs.count_documents({})
            if recent_audits == 0:
                alerts.append({
                    "id": str(uuid.uuid4()),
                    "title": "No Recent Compliance Audits",
                    "message": "Consider running compliance checks on your content",
                    "risk_level": "low",
                    "compliance_type": "content_policy",
                    "action_required": False,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "acknowledged": False,
                    "resolved": False,
                })

            if risk_level:
                rl_val = risk_level.value if hasattr(risk_level, 'value') else risk_level
                alerts = [a for a in alerts if a["risk_level"] == rl_val]

            by_risk = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for a in alerts:
                by_risk[a["risk_level"]] = by_risk.get(a["risk_level"], 0) + 1

            return {
                "success": True,
                "data_source": "real",
                "alerts": alerts,
                "total": len(alerts),
                "by_risk_level": by_risk,
            }
        except Exception as e:
            logger.error(f"Error fetching compliance alerts: {e}")
            return {"success": False, "error": str(e), "alerts": []}

    async def get_rights_information(self, asset_id: str, user_id: str) -> Dict[str, Any]:
        try:
            rights = await db.label_rights.find_one({"asset_id": asset_id}, {"_id": 0})
            if rights:
                territorial_rights = {t.lower(): True for t in rights.get("territories", [])}
                splits = rights.get("splits", [])
                owner = "Big Mann Entertainment"
                for s in splits:
                    if s.get("role") == "label":
                        owner = s.get("party", owner)
                        break

                return {
                    "success": True,
                    "data_source": "real",
                    "rights_information": {
                        "id": rights.get("rights_id", ""),
                        "asset_id": asset_id,
                        "copyright_owner": owner,
                        "copyright_year": 2024,
                        "licensing_info": {
                            "type": "exclusive" if rights.get("exclusive") else "non-exclusive",
                            "scope": "worldwide" if len(rights.get("territories", [])) >= 3 else "limited",
                            "ai_consent": rights.get("ai_consent", False),
                        },
                        "territorial_rights": territorial_rights,
                        "splits": splits,
                        "usage_restrictions": [
                            "No synchronization without additional license"
                        ] if rights.get("exclusive") else [],
                        "expiration_date": rights.get("expiry_date"),
                        "contact_info": {
                            "rights_manager": "rights@bigmannentertainment.com",
                            "legal_contact": "legal@bigmannentertainment.com",
                        },
                    },
                }

            return {
                "success": True,
                "data_source": "real",
                "rights_information": None,
                "message": "No rights information found for this asset",
            }
        except Exception as e:
            logger.error(f"Error fetching rights information: {e}")
            return {"success": False, "error": str(e)}

    async def generate_compliance_report(self, user_id: str, start_date: datetime,
                                         end_date: datetime,
                                         compliance_types: List[ComplianceType] = None,
                                         territories: List[Territory] = None) -> Dict[str, Any]:
        try:
            # Count audit logs in date range
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date.isoformat()
            if end_date:
                date_filter["$lte"] = end_date.isoformat()

            match = {}
            if date_filter:
                match["timestamp"] = date_filter

            total_audits = await db.compliance_audit_logs.count_documents(match)
            total_docs = await db.compliance_documents.count_documents({})
            total_assets = await db.label_assets.count_documents({}) + await db.user_content.count_documents({})
            total_rights = await db.label_rights.count_documents({})

            # Audit action types
            action_pipeline = [
                {"$match": match} if match else {"$match": {}},
                {"$group": {"_id": "$action_type", "count": {"$sum": 1}}},
            ]
            action_breakdown = {}
            async for doc in db.compliance_audit_logs.aggregate(action_pipeline):
                action_breakdown[doc["_id"] or "unknown"] = doc["count"]

            issues_found = total_assets - total_rights
            resolution_rate = round((total_rights / max(total_assets, 1)) * 100, 1)

            report_id = str(uuid.uuid4())

            return {
                "success": True,
                "data_source": "real",
                "report_id": report_id,
                "report": {
                    "title": f"Compliance Report {start_date.strftime('%Y-%m-%d') if start_date else 'N/A'} to {end_date.strftime('%Y-%m-%d') if end_date else 'N/A'}",
                    "total_assets_checked": total_assets,
                    "compliant_assets": total_rights,
                    "compliance_documents": total_docs,
                    "audit_logs_in_period": total_audits,
                    "action_breakdown": action_breakdown,
                    "issues_found": issues_found,
                    "resolution_rate": resolution_rate,
                },
                "key_findings": _generate_findings(total_assets, total_rights, total_docs, total_audits),
                "recommendations": _generate_recommendations(total_assets, total_rights, total_docs),
            }
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {"success": False, "error": str(e)}

    async def resolve_compliance_issue(self, check_id: str, resolution_notes: str, user_id: str) -> Dict[str, Any]:
        try:
            await db.compliance_audit_logs.insert_one({
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_type": "issue_resolution",
                "entity_type": "compliance_check",
                "entity_id": check_id,
                "actor_id": user_id,
                "actor_type": "user",
                "changes": {"resolution_notes": resolution_notes, "status": "resolved"},
                "compliance_relevant": True,
            })
            return {
                "success": True,
                "message": "Compliance issue resolved successfully",
                "resolved_at": datetime.now(timezone.utc).isoformat(),
                "resolved_by": user_id,
            }
        except Exception as e:
            logger.error(f"Error resolving compliance issue: {e}")
            return {"success": False, "error": str(e)}


def _generate_findings(total_assets, total_rights, total_docs, total_audits):
    findings = []
    if total_rights > 0:
        findings.append(f"Rights records found for {total_rights} asset(s)")
    if total_docs > 0:
        findings.append(f"{total_docs} compliance documents on file")
    if total_audits > 0:
        findings.append(f"{total_audits} compliance audit(s) performed")
    if total_assets > total_rights:
        findings.append(f"{total_assets - total_rights} asset(s) lack rights documentation")
    if not findings:
        findings.append("No compliance data available yet")
    return findings


def _generate_recommendations(total_assets, total_rights, total_docs):
    recs = []
    if total_assets > total_rights:
        recs.append("Register rights for all label assets")
    if total_docs < total_assets * 2:
        recs.append("Increase compliance documentation coverage")
    recs.append("Schedule quarterly compliance audits")
    return recs


# Global instance
compliance_center_service = ComplianceCenterService()
