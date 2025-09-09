"""
Compliance & Dispute Resolution Service
Handles audit logs, dispute management, and DAO voting
"""

import os
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from .agency_models import DisputeCase, AuditLog, DisputeStatus

logger = logging.getLogger(__name__)

class ComplianceDisputeService:
    """Service for compliance monitoring and dispute resolution"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def create_dispute(self, license_contract_id: str, agency_id: str, 
                           dispute_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dispute case"""
        try:
            dispute = DisputeCase(
                license_contract_id=license_contract_id,
                agency_id=agency_id,
                licensee_id=dispute_data.get('licensee_id'),
                dispute_type=dispute_data['dispute_type'],
                title=dispute_data['title'],
                description=dispute_data['description'],
                disputed_amount=dispute_data.get('disputed_amount')
            )
            
            # Insert into database
            dispute_dict = dispute.dict()
            result = await self.db.dispute_cases.insert_one(dispute_dict)
            dispute_dict["_id"] = result.inserted_id
            
            # Create audit log
            await self._create_audit_log(
                entity_type="dispute",
                entity_id=dispute.id,
                action="created",
                actor_id=agency_id,
                actor_type="agency",
                action_data={
                    "dispute_type": dispute.dispute_type,
                    "license_contract_id": license_contract_id,
                    "title": dispute.title
                }
            )
            
            # Auto-assign mediator based on dispute type
            mediator = await self._assign_mediator(dispute.dispute_type)
            if mediator:
                await self.db.dispute_cases.update_one(
                    {"id": dispute.id},
                    {"$set": {"assigned_mediator": mediator["id"]}}
                )
            
            return {
                "dispute_id": dispute.id,
                "status": "created",
                "assigned_mediator": mediator.get("name") if mediator else None,
                "message": "Dispute case created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating dispute: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def get_dispute_details(self, dispute_id: str, actor_id: str) -> Dict[str, Any]:
        """Get detailed dispute information"""
        try:
            dispute = await self.db.dispute_cases.find_one({"id": dispute_id})
            if not dispute:
                return {"status": "error", "error": "Dispute not found"}
            
            # Check access permissions
            if dispute["agency_id"] != actor_id and dispute.get("licensee_id") != actor_id:
                # Check if actor is mediator or admin
                if dispute.get("assigned_mediator") != actor_id:
                    return {"status": "error", "error": "Access denied"}
            
            # Get license contract details
            license_contract = await self.db.license_contracts.find_one(
                {"id": dispute["license_contract_id"]}
            )
            
            # Get evidence files info
            evidence_files = []
            for file_url in dispute.get("evidence_files", []):
                # In production, get file metadata from S3
                evidence_files.append({
                    "url": file_url,
                    "filename": file_url.split("/")[-1],
                    "upload_date": dispute["created_at"]
                })
            
            return {
                "dispute": dispute,
                "license_contract": license_contract,
                "evidence_files": evidence_files,
                "timeline": await self._get_dispute_timeline(dispute_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting dispute details: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def update_dispute_status(self, dispute_id: str, new_status: str, 
                                  actor_id: str, notes: str = None) -> Dict[str, Any]:
        """Update dispute status"""
        try:
            dispute = await self.db.dispute_cases.find_one({"id": dispute_id})
            if not dispute:
                return {"status": "error", "error": "Dispute not found"}
            
            # Validate status transition
            valid_transitions = {
                "open": ["in_review", "resolved"],
                "in_review": ["resolved", "escalated"],
                "escalated": ["resolved"],
                "resolved": []  # Final state
            }
            
            current_status = dispute["status"]
            if new_status not in valid_transitions.get(current_status, []):
                return {
                    "status": "error", 
                    "error": f"Invalid status transition from {current_status} to {new_status}"
                }
            
            # Update dispute
            update_data = {
                "status": new_status,
                "updated_at": datetime.now(timezone.utc)
            }
            
            if new_status == "resolved":
                update_data["resolved_at"] = datetime.now(timezone.utc)
            
            await self.db.dispute_cases.update_one(
                {"id": dispute_id},
                {"$set": update_data}
            )
            
            # Add mediation note
            if notes:
                mediation_note = {
                    "timestamp": datetime.now(timezone.utc),
                    "actor_id": actor_id,
                    "note": notes,
                    "action": f"Status changed to {new_status}"
                }
                
                await self.db.dispute_cases.update_one(
                    {"id": dispute_id},
                    {"$push": {"mediation_notes": mediation_note}}
                )
            
            # Create audit log
            await self._create_audit_log(
                entity_type="dispute",
                entity_id=dispute_id,
                action="status_updated",
                actor_id=actor_id,
                actor_type="mediator",
                action_data={
                    "old_status": current_status,
                    "new_status": new_status,
                    "notes": notes
                }
            )
            
            return {
                "status": "updated",
                "new_status": new_status,
                "message": f"Dispute status updated to {new_status}"
            }
            
        except Exception as e:
            logger.error(f"Error updating dispute status: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def upload_dispute_evidence(self, dispute_id: str, actor_id: str, 
                                    file_urls: List[str], description: str = None) -> Dict[str, Any]:
        """Upload evidence files to dispute"""
        try:
            dispute = await self.db.dispute_cases.find_one({"id": dispute_id})
            if not dispute:
                return {"status": "error", "error": "Dispute not found"}
            
            # Check access permissions
            if dispute["agency_id"] != actor_id and dispute.get("licensee_id") != actor_id:
                return {"status": "error", "error": "Access denied"}
            
            # Add evidence files
            await self.db.dispute_cases.update_one(
                {"id": dispute_id},
                {
                    "$push": {"evidence_files": {"$each": file_urls}},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
            # Add mediation note
            mediation_note = {
                "timestamp": datetime.now(timezone.utc),
                "actor_id": actor_id,
                "note": description or "Evidence files uploaded",
                "action": "evidence_uploaded",
                "files_count": len(file_urls)
            }
            
            await self.db.dispute_cases.update_one(
                {"id": dispute_id},
                {"$push": {"mediation_notes": mediation_note}}
            )
            
            # Create audit log
            await self._create_audit_log(
                entity_type="dispute",
                entity_id=dispute_id,
                action="evidence_uploaded",
                actor_id=actor_id,
                actor_type="party",
                action_data={
                    "files_count": len(file_urls),
                    "description": description
                }
            )
            
            return {
                "status": "uploaded",
                "files_count": len(file_urls),
                "message": "Evidence uploaded successfully"
            }
            
        except Exception as e:
            logger.error(f"Error uploading dispute evidence: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def initiate_dao_voting(self, dispute_id: str, voting_duration_hours: int = 168) -> Dict[str, Any]:
        """Initiate DAO voting for dispute resolution"""
        try:
            dispute = await self.db.dispute_cases.find_one({"id": dispute_id})
            if not dispute:
                return {"status": "error", "error": "Dispute not found"}
            
            if dispute["status"] != "escalated":
                return {"status": "error", "error": "Dispute must be escalated before DAO voting"}
            
            # Create DAO proposal
            voting_deadline = datetime.now(timezone.utc) + timedelta(hours=voting_duration_hours)
            dao_proposal_id = f"dao_dispute_{dispute_id}_{int(datetime.now().timestamp())}"
            
            update_data = {
                "dao_proposal_id": dao_proposal_id,
                "voting_enabled": True,
                "voting_deadline": voting_deadline,
                "votes": {"for": [], "against": [], "abstain": []},
                "updated_at": datetime.now(timezone.utc)
            }
            
            await self.db.dispute_cases.update_one(
                {"id": dispute_id},
                {"$set": update_data}
            )
            
            # Create audit log
            await self._create_audit_log(
                entity_type="dispute",
                entity_id=dispute_id,
                action="dao_voting_initiated",
                actor_id="system",
                actor_type="system",
                action_data={
                    "dao_proposal_id": dao_proposal_id,
                    "voting_deadline": voting_deadline.isoformat(),
                    "duration_hours": voting_duration_hours
                }
            )
            
            return {
                "status": "initiated",
                "dao_proposal_id": dao_proposal_id,
                "voting_deadline": voting_deadline.isoformat(),
                "message": "DAO voting initiated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error initiating DAO voting: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def cast_dao_vote(self, dispute_id: str, voter_id: str, vote: str, 
                          stake_amount: float = 0.0) -> Dict[str, Any]:
        """Cast a vote in DAO dispute resolution"""
        try:
            dispute = await self.db.dispute_cases.find_one({"id": dispute_id})
            if not dispute:
                return {"status": "error", "error": "Dispute not found"}
            
            if not dispute.get("voting_enabled"):
                return {"status": "error", "error": "Voting not enabled for this dispute"}
            
            # Check voting deadline
            if datetime.now(timezone.utc) > dispute["voting_deadline"]:
                return {"status": "error", "error": "Voting period has ended"}
            
            # Validate vote
            if vote not in ["for", "against", "abstain"]:
                return {"status": "error", "error": "Invalid vote option"}
            
            # Check if voter already voted
            all_votes = dispute.get("votes", {})
            for vote_type, voters in all_votes.items():
                if any(v["voter_id"] == voter_id for v in voters):
                    return {"status": "error", "error": "Voter has already cast a vote"}
            
            # Cast vote
            vote_record = {
                "voter_id": voter_id,
                "timestamp": datetime.now(timezone.utc),
                "stake_amount": stake_amount
            }
            
            await self.db.dispute_cases.update_one(
                {"id": dispute_id},
                {"$push": {f"votes.{vote}": vote_record}}
            )
            
            # Create audit log
            await self._create_audit_log(
                entity_type="dispute",
                entity_id=dispute_id,
                action="dao_vote_cast",
                actor_id=voter_id,
                actor_type="dao_member",
                action_data={
                    "vote": vote,
                    "stake_amount": stake_amount
                }
            )
            
            return {
                "status": "cast",
                "vote": vote,
                "message": "Vote cast successfully"
            }
            
        except Exception as e:
            logger.error(f"Error casting DAO vote: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def get_compliance_report(self, agency_id: str, start_date: datetime, 
                                  end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for agency"""
        try:
            # Get audit logs for the period
            audit_logs = await self.db.audit_logs.find({
                "actor_id": agency_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }).to_list(1000)
            
            # Get disputes for the period
            disputes = await self.db.dispute_cases.find({
                "agency_id": agency_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(100)
            
            # Analyze compliance metrics
            total_actions = len(audit_logs)
            action_breakdown = {}
            for log in audit_logs:
                action = log["action"]
                action_breakdown[action] = action_breakdown.get(action, 0) + 1
            
            dispute_breakdown = {}
            for dispute in disputes:
                dispute_type = dispute["dispute_type"]
                dispute_breakdown[dispute_type] = dispute_breakdown.get(dispute_type, 0) + 1
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(
                total_actions, len(disputes), action_breakdown
            )
            
            return {
                "agency_id": agency_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "metrics": {
                    "total_actions": total_actions,
                    "total_disputes": len(disputes),
                    "compliance_score": compliance_score,
                    "action_breakdown": action_breakdown,
                    "dispute_breakdown": dispute_breakdown
                },
                "recent_disputes": disputes[-5:] if disputes else [],
                "recommendations": self._generate_compliance_recommendations(
                    compliance_score, dispute_breakdown
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    # Private helper methods
    
    async def _create_audit_log(self, entity_type: str, entity_id: str, action: str,
                              actor_id: str, actor_type: str, action_data: Dict[str, Any]):
        """Create audit log entry"""
        try:
            audit_log = AuditLog(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                actor_id=actor_id,
                actor_type=actor_type,
                action_data=action_data
            )
            
            await self.db.audit_logs.insert_one(audit_log.dict())
            
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
    
    async def _assign_mediator(self, dispute_type: str) -> Optional[Dict[str, Any]]:
        """Auto-assign mediator based on dispute type"""
        try:
            # Mock mediator assignment - in production, this would be more sophisticated
            mediators = {
                "copyright": {"id": "mediator_copyright", "name": "Copyright Specialist"},
                "usage_violation": {"id": "mediator_usage", "name": "Usage Rights Specialist"},
                "payment": {"id": "mediator_payment", "name": "Payment Specialist"},
                "quality": {"id": "mediator_quality", "name": "Quality Assurance Specialist"}
            }
            
            return mediators.get(dispute_type)
            
        except Exception as e:
            logger.error(f"Error assigning mediator: {str(e)}")
            return None
    
    async def _get_dispute_timeline(self, dispute_id: str) -> List[Dict[str, Any]]:
        """Get dispute timeline events"""
        try:
            # Get audit logs for this dispute
            audit_logs = await self.db.audit_logs.find({
                "entity_type": "dispute",
                "entity_id": dispute_id
            }).sort("timestamp", 1).to_list(100)
            
            # Get mediation notes
            dispute = await self.db.dispute_cases.find_one({"id": dispute_id})
            mediation_notes = dispute.get("mediation_notes", [])
            
            # Combine and sort timeline events
            timeline = []
            
            for log in audit_logs:
                timeline.append({
                    "type": "audit",
                    "timestamp": log["timestamp"],
                    "action": log["action"],
                    "actor_id": log["actor_id"],
                    "data": log["action_data"]
                })
            
            for note in mediation_notes:
                timeline.append({
                    "type": "mediation",
                    "timestamp": note["timestamp"],
                    "action": note.get("action", "note_added"),
                    "actor_id": note["actor_id"], 
                    "note": note["note"]
                })
            
            # Sort by timestamp
            timeline.sort(key=lambda x: x["timestamp"])
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error getting dispute timeline: {str(e)}")
            return []
    
    def _calculate_compliance_score(self, total_actions: int, total_disputes: int, 
                                  action_breakdown: Dict[str, int]) -> float:
        """Calculate compliance score (0-100)"""
        try:
            base_score = 100
            
            # Penalize for disputes
            dispute_penalty = min(total_disputes * 5, 30)  # Max 30 points penalty
            
            # Penalize for certain actions
            penalty_actions = ["violation_reported", "contract_breached", "payment_failed"]
            action_penalty = 0
            for action in penalty_actions:
                action_penalty += action_breakdown.get(action, 0) * 2
            
            # Bonus for positive actions
            bonus_actions = ["license_completed", "payment_received", "verification_passed"]
            action_bonus = 0
            for action in bonus_actions:
                action_bonus += action_breakdown.get(action, 0) * 1
            
            final_score = base_score - dispute_penalty - action_penalty + action_bonus
            return max(0, min(100, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {str(e)}")
            return 50.0  # Default neutral score
    
    def _generate_compliance_recommendations(self, compliance_score: float, 
                                          dispute_breakdown: Dict[str, int]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if compliance_score < 70:
            recommendations.append("Focus on improving dispute resolution processes")
            
        if dispute_breakdown.get("copyright", 0) > 2:
            recommendations.append("Review copyright verification procedures")
            
        if dispute_breakdown.get("payment", 0) > 1:
            recommendations.append("Implement stricter payment processing controls")
            
        if compliance_score > 90:
            recommendations.append("Excellent compliance record - maintain current practices")
        elif compliance_score > 80:
            recommendations.append("Good compliance - minor improvements needed")
        else:
            recommendations.append("Significant compliance improvements required")
            
        return recommendations

# Global service instance
compliance_service = None

def get_compliance_service(db):
    global compliance_service
    if compliance_service is None:
        compliance_service = ComplianceDisputeService(db)
    return compliance_service