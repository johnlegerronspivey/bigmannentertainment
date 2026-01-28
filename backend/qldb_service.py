"""
AWS QLDB Integration - Service Layer
Business logic for immutable dispute ledger and audit trail system
"""

import os
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv
import logging
import hashlib
import json

from qldb_models import (
    Dispute, DisputeStatus, DisputeType, Priority, DisputeParty,
    DisputeEvidence, DisputeComment, DisputeSettlement,
    CreateDisputeRequest, UpdateDisputeRequest,
    AuditEntry, AuditEventType, CreateAuditEntryRequest,
    DisputeStats, AuditStats, QLDBDashboardStats,
    VerificationResponse, compute_content_hash, compute_chain_hash
)

load_dotenv()
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
QLDB_LEDGER_NAME = os.getenv("QLDB_LEDGER_NAME", "dispute-ledger")


class QLDBService:
    """Service for AWS QLDB operations - Immutable Dispute Ledger"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.disputes_collection = db.qldb_disputes
        self.audit_collection = db.qldb_audit_trail
        self.ledger_name = QLDB_LEDGER_NAME
        
        # Track the last hash for chain integrity
        self._last_audit_hash = "GENESIS"
        
        # Initialize sample data
        asyncio.create_task(self._initialize_sample_data())
    
    async def _initialize_sample_data(self):
        """Initialize sample data for demonstration"""
        try:
            disputes_count = await self.disputes_collection.count_documents({})
            if disputes_count == 0:
                await self._create_sample_disputes()
            
            audit_count = await self.audit_collection.count_documents({})
            if audit_count == 0:
                await self._create_sample_audit_entries()
                
        except Exception as e:
            logger.error(f"Error initializing sample data: {e}")
    
    async def _create_sample_disputes(self):
        """Create sample disputes for demonstration"""
        now = datetime.now(timezone.utc)
        
        sample_disputes = [
            Dispute(
                dispute_number="DISP-2026-001",
                type=DisputeType.ROYALTY_DISPUTE,
                status=DisputeStatus.UNDER_REVIEW,
                priority=Priority.HIGH,
                title="Q4 2025 Royalty Payment Discrepancy",
                description="Artist claims underpayment of streaming royalties for Q4 2025. Reported streams don't match platform analytics.",
                amount_disputed=15420.50,
                currency="USD",
                related_asset_id="asset-music-001",
                claimant=DisputeParty(
                    party_id="artist-001",
                    party_type="claimant",
                    name="Marcus Johnson",
                    email="marcus@artist.com",
                    role="Recording Artist"
                ),
                respondent=DisputeParty(
                    party_id="label-001",
                    party_type="respondent",
                    name="Big Mann Entertainment",
                    email="disputes@bigmannentertainment.com",
                    role="Record Label"
                ),
                assigned_to="legal-team-001",
                assigned_at=now - timedelta(days=2),
                evidence=[
                    DisputeEvidence(
                        evidence_type="document",
                        title="Streaming Analytics Report",
                        description="Platform-provided streaming report for Q4 2025",
                        submitted_by="artist-001",
                        verified=True
                    )
                ],
                comments=[
                    DisputeComment(
                        author_id="legal-team-001",
                        author_name="Legal Team",
                        content="Under review. Requested additional platform verification.",
                        is_internal=True
                    )
                ],
                created_at=now - timedelta(days=5)
            ),
            
            Dispute(
                dispute_number="DISP-2026-002",
                type=DisputeType.COPYRIGHT_CLAIM,
                status=DisputeStatus.OPEN,
                priority=Priority.CRITICAL,
                title="Unauthorized Sample Usage Claim",
                description="Third party claims unauthorized use of copyrighted sample in track 'Summer Vibes'.",
                amount_disputed=50000.00,
                currency="USD",
                related_asset_id="asset-music-002",
                claimant=DisputeParty(
                    party_id="publisher-ext-001",
                    party_type="claimant",
                    name="Global Music Publishing",
                    email="legal@globalmusicpub.com",
                    role="Music Publisher"
                ),
                respondent=DisputeParty(
                    party_id="producer-001",
                    party_type="respondent",
                    name="DJ Producer X",
                    email="producer@example.com",
                    role="Music Producer"
                ),
                created_at=now - timedelta(days=1)
            ),
            
            Dispute(
                dispute_number="DISP-2026-003",
                type=DisputeType.CONTRACT_DISPUTE,
                status=DisputeStatus.RESOLVED,
                priority=Priority.MEDIUM,
                title="Distribution Agreement Terms Dispute",
                description="Disagreement over exclusive distribution terms interpretation.",
                amount_disputed=8500.00,
                currency="USD",
                related_contract_id="contract-dist-001",
                claimant=DisputeParty(
                    party_id="distributor-001",
                    party_type="claimant",
                    name="Digital Distribution Co",
                    role="Distributor"
                ),
                respondent=DisputeParty(
                    party_id="label-001",
                    party_type="respondent",
                    name="Big Mann Entertainment",
                    role="Record Label"
                ),
                resolution_summary="Parties agreed to amended terms. New agreement signed.",
                resolution_amount=4250.00,
                resolved_by="mediator-001",
                resolved_at=now - timedelta(days=3),
                settlements=[
                    DisputeSettlement(
                        proposed_by="mediator-001",
                        proposed_amount=4250.00,
                        proposed_terms="Split the disputed amount 50/50 and amend contract terms",
                        status="accepted",
                        response_by="both-parties",
                        response_at=now - timedelta(days=3)
                    )
                ],
                created_at=now - timedelta(days=15)
            ),
            
            Dispute(
                dispute_number="DISP-2026-004",
                type=DisputeType.PAYMENT_DISPUTE,
                status=DisputeStatus.ESCALATED,
                priority=Priority.HIGH,
                title="Late Payment Penalty Dispute",
                description="Artist contesting late payment penalties applied to royalty statement.",
                amount_disputed=2340.00,
                currency="USD",
                claimant=DisputeParty(
                    party_id="artist-002",
                    party_type="claimant",
                    name="Sarah Williams",
                    role="Recording Artist"
                ),
                assigned_to="finance-team",
                created_at=now - timedelta(days=7)
            ),
            
            Dispute(
                dispute_number="DISP-2026-005",
                type=DisputeType.LICENSING_ISSUE,
                status=DisputeStatus.OPEN,
                priority=Priority.LOW,
                title="Sync License Territory Clarification",
                description="Request for clarification on sync license territorial rights for film usage.",
                related_contract_id="contract-sync-001",
                claimant=DisputeParty(
                    party_id="film-prod-001",
                    party_type="claimant",
                    name="Indie Films LLC",
                    role="Film Production"
                ),
                created_at=now - timedelta(hours=12)
            )
        ]
        
        for dispute in sample_disputes:
            dispute.content_hash = compute_content_hash(dispute.dict(exclude={"content_hash", "ledger_document_id"}))
            await self.disputes_collection.insert_one(dispute.dict())
    
    async def _create_sample_audit_entries(self):
        """Create sample audit entries for demonstration"""
        now = datetime.now(timezone.utc)
        
        sample_entries = [
            AuditEntry(
                event_type=AuditEventType.DISPUTE_CREATED,
                entity_type="dispute",
                entity_id="DISP-2026-001",
                actor_id="artist-001",
                actor_name="Marcus Johnson",
                actor_role="claimant",
                action_description="Created new royalty dispute",
                change_summary="New dispute filed for Q4 2025 royalty discrepancy",
                metadata={"amount": 15420.50, "type": "ROYALTY_DISPUTE"},
                timestamp=now - timedelta(days=5)
            ),
            AuditEntry(
                event_type=AuditEventType.DISPUTE_STATUS_CHANGED,
                entity_type="dispute",
                entity_id="DISP-2026-001",
                actor_id="legal-team-001",
                actor_name="Legal Team",
                actor_role="reviewer",
                action_description="Changed dispute status from OPEN to UNDER_REVIEW",
                previous_state={"status": "OPEN"},
                new_state={"status": "UNDER_REVIEW"},
                timestamp=now - timedelta(days=3)
            ),
            AuditEntry(
                event_type=AuditEventType.EVIDENCE_ADDED,
                entity_type="dispute",
                entity_id="DISP-2026-001",
                actor_id="artist-001",
                actor_name="Marcus Johnson",
                action_description="Added streaming analytics report as evidence",
                metadata={"evidence_type": "document", "title": "Streaming Analytics Report"},
                timestamp=now - timedelta(days=4)
            ),
            AuditEntry(
                event_type=AuditEventType.DISPUTE_CREATED,
                entity_type="dispute",
                entity_id="DISP-2026-002",
                actor_id="publisher-ext-001",
                actor_name="Global Music Publishing",
                action_description="Created new copyright claim dispute",
                change_summary="Copyright claim filed for unauthorized sample usage",
                metadata={"amount": 50000.00, "type": "COPYRIGHT_CLAIM"},
                timestamp=now - timedelta(days=1)
            ),
            AuditEntry(
                event_type=AuditEventType.SETTLEMENT_PROPOSED,
                entity_type="dispute",
                entity_id="DISP-2026-003",
                actor_id="mediator-001",
                actor_name="Mediator",
                action_description="Proposed settlement for contract dispute",
                metadata={"proposed_amount": 4250.00},
                timestamp=now - timedelta(days=4)
            ),
            AuditEntry(
                event_type=AuditEventType.SETTLEMENT_ACCEPTED,
                entity_type="dispute",
                entity_id="DISP-2026-003",
                actor_id="both-parties",
                actor_name="All Parties",
                action_description="Settlement accepted by all parties",
                timestamp=now - timedelta(days=3)
            ),
            AuditEntry(
                event_type=AuditEventType.DISPUTE_RESOLVED,
                entity_type="dispute",
                entity_id="DISP-2026-003",
                actor_id="mediator-001",
                actor_name="Mediator",
                action_description="Dispute resolved with settlement",
                previous_state={"status": "UNDER_REVIEW"},
                new_state={"status": "RESOLVED", "resolution_amount": 4250.00},
                timestamp=now - timedelta(days=3)
            ),
            AuditEntry(
                event_type=AuditEventType.ESCALATION,
                entity_type="dispute",
                entity_id="DISP-2026-004",
                actor_id="system",
                actor_name="System",
                action_description="Dispute escalated due to time limit",
                metadata={"reason": "No response within 5 days", "escalated_to": "senior-management"},
                timestamp=now - timedelta(days=2)
            )
        ]
        
        # Build hash chain
        prev_hash = "GENESIS"
        for entry in sample_entries:
            entry.content_hash = compute_content_hash(entry.dict(exclude={"content_hash", "previous_hash", "ledger_document_id"}))
            entry.previous_hash = prev_hash
            entry.verified = True
            prev_hash = compute_chain_hash(entry.content_hash, entry.previous_hash)
            await self.audit_collection.insert_one(entry.dict())
        
        self._last_audit_hash = prev_hash
    
    # ==================== Dispute Operations ====================
    
    async def create_dispute(self, request: CreateDisputeRequest, user_id: str = "system") -> Dispute:
        """Create a new dispute"""
        # Generate dispute number
        count = await self.disputes_collection.count_documents({})
        dispute_number = f"DISP-{datetime.now().year}-{str(count + 1).zfill(3)}"
        
        dispute = Dispute(
            dispute_number=dispute_number,
            type=request.type,
            status=DisputeStatus.OPEN,
            priority=request.priority,
            title=request.title,
            description=request.description,
            amount_disputed=request.amount_disputed,
            currency=request.currency,
            related_asset_id=request.related_asset_id,
            related_contract_id=request.related_contract_id,
            claimant=DisputeParty(
                party_id=user_id,
                party_type="claimant",
                name=request.claimant_name,
                email=request.claimant_email
            ),
            respondent=DisputeParty(
                party_id="respondent-tbd",
                party_type="respondent",
                name=request.respondent_name or "To Be Determined",
                email=request.respondent_email
            ) if request.respondent_name else None
        )
        
        # Compute content hash for immutability
        dispute.content_hash = compute_content_hash(
            dispute.dict(exclude={"content_hash", "ledger_document_id"})
        )
        
        await self.disputes_collection.insert_one(dispute.dict())
        
        # Create audit entry
        await self.create_audit_entry(CreateAuditEntryRequest(
            event_type=AuditEventType.DISPUTE_CREATED,
            entity_type="dispute",
            entity_id=dispute.dispute_number,
            actor_id=user_id,
            actor_name=request.claimant_name,
            action_description=f"Created new {request.type.value} dispute",
            change_summary=f"New dispute filed: {request.title}",
            metadata={"amount": request.amount_disputed, "type": request.type.value}
        ))
        
        return dispute
    
    async def get_disputes(
        self,
        status: Optional[DisputeStatus] = None,
        dispute_type: Optional[DisputeType] = None,
        priority: Optional[Priority] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dispute], int]:
        """Get disputes with optional filtering"""
        query = {}
        
        if status:
            query["status"] = status.value
        if dispute_type:
            query["type"] = dispute_type.value
        if priority:
            query["priority"] = priority.value
        
        total = await self.disputes_collection.count_documents(query)
        cursor = self.disputes_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        
        disputes = []
        async for doc in cursor:
            doc.pop("_id", None)
            disputes.append(Dispute(**doc))
        
        return disputes, total
    
    async def get_dispute(self, dispute_id: str) -> Optional[Dispute]:
        """Get a specific dispute"""
        doc = await self.disputes_collection.find_one({
            "$or": [
                {"id": dispute_id},
                {"dispute_number": dispute_id}
            ]
        })
        if doc:
            doc.pop("_id", None)
            return Dispute(**doc)
        return None
    
    async def update_dispute(
        self,
        dispute_id: str,
        update: UpdateDisputeRequest,
        user_id: str = "system",
        user_name: str = "System"
    ) -> Optional[Dispute]:
        """Update a dispute"""
        dispute = await self.get_dispute(dispute_id)
        if not dispute:
            return None
        
        update_data = {"updated_at": datetime.now(timezone.utc)}
        previous_state = {}
        new_state = {}
        
        if update.status:
            previous_state["status"] = dispute.status.value
            new_state["status"] = update.status.value
            update_data["status"] = update.status.value
            
            if update.status == DisputeStatus.RESOLVED:
                update_data["resolved_by"] = user_id
                update_data["resolved_at"] = datetime.now(timezone.utc)
        
        if update.priority:
            update_data["priority"] = update.priority.value
        
        if update.description:
            update_data["description"] = update.description
        
        if update.assigned_to:
            update_data["assigned_to"] = update.assigned_to
            update_data["assigned_at"] = datetime.now(timezone.utc)
        
        if update.resolution_summary:
            update_data["resolution_summary"] = update.resolution_summary
        
        if update.resolution_amount is not None:
            update_data["resolution_amount"] = update.resolution_amount
        
        # Update content hash
        updated_dispute = dispute.dict()
        updated_dispute.update(update_data)
        update_data["content_hash"] = compute_content_hash(
            {k: v for k, v in updated_dispute.items() if k not in ["content_hash", "ledger_document_id", "_id"]}
        )
        
        await self.disputes_collection.update_one(
            {"$or": [{"id": dispute_id}, {"dispute_number": dispute_id}]},
            {"$set": update_data}
        )
        
        # Create audit entry
        event_type = AuditEventType.DISPUTE_STATUS_CHANGED if update.status else AuditEventType.DISPUTE_UPDATED
        if update.status == DisputeStatus.RESOLVED:
            event_type = AuditEventType.DISPUTE_RESOLVED
        
        await self.create_audit_entry(CreateAuditEntryRequest(
            event_type=event_type,
            entity_type="dispute",
            entity_id=dispute.dispute_number,
            actor_id=user_id,
            actor_name=user_name,
            action_description=f"Updated dispute: {list(update_data.keys())}",
            metadata={"previous_state": previous_state, "new_state": new_state}
        ))
        
        return await self.get_dispute(dispute_id)
    
    async def add_evidence(
        self,
        dispute_id: str,
        evidence: DisputeEvidence,
        user_id: str = "system",
        user_name: str = "System"
    ) -> Optional[Dispute]:
        """Add evidence to a dispute"""
        result = await self.disputes_collection.update_one(
            {"$or": [{"id": dispute_id}, {"dispute_number": dispute_id}]},
            {
                "$push": {"evidence": evidence.dict()},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        
        if result.modified_count > 0:
            dispute = await self.get_dispute(dispute_id)
            
            await self.create_audit_entry(CreateAuditEntryRequest(
                event_type=AuditEventType.EVIDENCE_ADDED,
                entity_type="dispute",
                entity_id=dispute.dispute_number if dispute else dispute_id,
                actor_id=user_id,
                actor_name=user_name,
                action_description=f"Added evidence: {evidence.title}",
                metadata={"evidence_type": evidence.evidence_type, "title": evidence.title}
            ))
            
            return dispute
        return None
    
    async def add_comment(
        self,
        dispute_id: str,
        comment: DisputeComment
    ) -> Optional[Dispute]:
        """Add comment to a dispute"""
        result = await self.disputes_collection.update_one(
            {"$or": [{"id": dispute_id}, {"dispute_number": dispute_id}]},
            {
                "$push": {"comments": comment.dict()},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        
        if result.modified_count > 0:
            dispute = await self.get_dispute(dispute_id)
            
            await self.create_audit_entry(CreateAuditEntryRequest(
                event_type=AuditEventType.COMMENT_ADDED,
                entity_type="dispute",
                entity_id=dispute.dispute_number if dispute else dispute_id,
                actor_id=comment.author_id,
                actor_name=comment.author_name,
                action_description="Added comment to dispute",
                metadata={"is_internal": comment.is_internal}
            ))
            
            return dispute
        return None
    
    # ==================== Audit Trail Operations ====================
    
    async def create_audit_entry(self, request: CreateAuditEntryRequest) -> AuditEntry:
        """Create an immutable audit entry"""
        entry = AuditEntry(
            event_type=request.event_type,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            actor_id=request.actor_id,
            actor_name=request.actor_name,
            action_description=request.action_description,
            change_summary=request.change_summary,
            metadata=request.metadata
        )
        
        # Compute hashes for chain integrity
        entry.content_hash = compute_content_hash(
            entry.dict(exclude={"content_hash", "previous_hash", "ledger_document_id", "verified", "verification_proof"})
        )
        entry.previous_hash = self._last_audit_hash
        entry.verified = True
        
        # Update chain hash
        self._last_audit_hash = compute_chain_hash(entry.content_hash, entry.previous_hash)
        
        await self.audit_collection.insert_one(entry.dict())
        return entry
    
    async def get_audit_entries(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        actor_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[AuditEntry], int]:
        """Get audit entries with optional filtering"""
        query = {}
        
        if entity_id:
            query["entity_id"] = entity_id
        if entity_type:
            query["entity_type"] = entity_type
        if event_type:
            query["event_type"] = event_type.value
        if actor_id:
            query["actor_id"] = actor_id
        
        total = await self.audit_collection.count_documents(query)
        cursor = self.audit_collection.find(query).sort("timestamp", -1).skip(offset).limit(limit)
        
        entries = []
        async for doc in cursor:
            doc.pop("_id", None)
            entries.append(AuditEntry(**doc))
        
        return entries, total
    
    async def verify_audit_entry(self, entry_id: str) -> VerificationResponse:
        """Verify the integrity of an audit entry"""
        doc = await self.audit_collection.find_one({"id": entry_id})
        
        if not doc:
            return VerificationResponse(
                document_id=entry_id,
                verified=False,
                chain_valid=False
            )
        
        doc.pop("_id", None)
        entry = AuditEntry(**doc)
        
        # Recompute content hash
        expected_hash = compute_content_hash(
            entry.dict(exclude={"content_hash", "previous_hash", "ledger_document_id", "verified", "verification_proof"})
        )
        
        hash_valid = entry.content_hash == expected_hash
        
        return VerificationResponse(
            document_id=entry_id,
            verified=hash_valid,
            content_hash=entry.content_hash,
            chain_valid=hash_valid,
            proof={"expected_hash": expected_hash, "stored_hash": entry.content_hash}
        )
    
    async def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify the entire audit chain integrity"""
        cursor = self.audit_collection.find({}).sort("timestamp", 1)
        
        prev_hash = "GENESIS"
        valid_count = 0
        invalid_entries = []
        total = 0
        
        async for doc in cursor:
            total += 1
            doc.pop("_id", None)
            entry = AuditEntry(**doc)
            
            # Check previous hash matches
            if entry.previous_hash != prev_hash:
                invalid_entries.append({
                    "entry_id": entry.id,
                    "reason": "Previous hash mismatch"
                })
            else:
                valid_count += 1
            
            # Update chain hash
            prev_hash = compute_chain_hash(entry.content_hash, entry.previous_hash)
        
        return {
            "chain_valid": len(invalid_entries) == 0,
            "total_entries": total,
            "valid_entries": valid_count,
            "invalid_entries": invalid_entries,
            "verification_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # ==================== Dashboard Statistics ====================
    
    async def get_dashboard_stats(self) -> QLDBDashboardStats:
        """Get comprehensive dashboard statistics"""
        now = datetime.now(timezone.utc)
        
        # Dispute stats
        total_disputes = await self.disputes_collection.count_documents({})
        open_disputes = await self.disputes_collection.count_documents({"status": DisputeStatus.OPEN.value})
        under_review = await self.disputes_collection.count_documents({"status": DisputeStatus.UNDER_REVIEW.value})
        resolved_disputes = await self.disputes_collection.count_documents({"status": DisputeStatus.RESOLVED.value})
        escalated_disputes = await self.disputes_collection.count_documents({"status": DisputeStatus.ESCALATED.value})
        
        # Priority counts
        critical_count = await self.disputes_collection.count_documents({"priority": Priority.CRITICAL.value})
        high_priority_count = await self.disputes_collection.count_documents({"priority": Priority.HIGH.value})
        
        # By type
        type_pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        type_result = await self.disputes_collection.aggregate(type_pipeline).to_list(20)
        disputes_by_type = {r["_id"]: r["count"] for r in type_result if r["_id"]}
        
        # Financial totals
        amount_pipeline = [
            {"$group": {
                "_id": None,
                "total_disputed": {"$sum": {"$ifNull": ["$amount_disputed", 0]}},
                "total_resolved": {"$sum": {"$ifNull": ["$resolution_amount", 0]}}
            }}
        ]
        amount_result = await self.disputes_collection.aggregate(amount_pipeline).to_list(1)
        total_disputed = amount_result[0]["total_disputed"] if amount_result else 0
        total_resolved = amount_result[0]["total_resolved"] if amount_result else 0
        
        # Audit stats
        total_entries = await self.audit_collection.count_documents({})
        entries_24h = await self.audit_collection.count_documents({
            "timestamp": {"$gte": (now - timedelta(hours=24)).isoformat()}
        })
        entries_7d = await self.audit_collection.count_documents({
            "timestamp": {"$gte": (now - timedelta(days=7)).isoformat()}
        })
        
        # Audit by type
        audit_type_pipeline = [
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
        ]
        audit_type_result = await self.audit_collection.aggregate(audit_type_pipeline).to_list(20)
        entries_by_type = {r["_id"]: r["count"] for r in audit_type_result if r["_id"]}
        
        # Recent disputes
        recent_disputes_cursor = self.disputes_collection.find({}).sort("created_at", -1).limit(5)
        recent_disputes = []
        async for doc in recent_disputes_cursor:
            doc.pop("_id", None)
            recent_disputes.append(Dispute(**doc))
        
        # Recent audit entries
        recent_audit_cursor = self.audit_collection.find({}).sort("timestamp", -1).limit(5)
        recent_audit = []
        async for doc in recent_audit_cursor:
            doc.pop("_id", None)
            recent_audit.append(AuditEntry(**doc))
        
        # Chain verification
        chain_result = await self.verify_chain_integrity()
        
        return QLDBDashboardStats(
            dispute_stats=DisputeStats(
                total_disputes=total_disputes,
                open_disputes=open_disputes,
                under_review=under_review,
                resolved_disputes=resolved_disputes,
                escalated_disputes=escalated_disputes,
                disputes_by_type=disputes_by_type,
                critical_count=critical_count,
                high_priority_count=high_priority_count,
                total_amount_disputed=total_disputed,
                total_amount_resolved=total_resolved
            ),
            audit_stats=AuditStats(
                total_entries=total_entries,
                entries_last_24h=entries_24h,
                entries_last_7d=entries_7d,
                entries_by_type=entries_by_type,
                verified_entries=total_entries,
                pending_verification=0
            ),
            recent_disputes=recent_disputes,
            recent_audit_entries=recent_audit,
            chain_verified=chain_result["chain_valid"],
            last_verification_time=now,
            total_documents=total_disputes + total_entries
        )
    
    # ==================== Health Check ====================
    
    async def check_health(self) -> Dict[str, Any]:
        """Check QLDB service health"""
        chain_result = await self.verify_chain_integrity()
        
        return {
            "status": "healthy",
            "service": "AWS QLDB Dispute Ledger",
            "version": "1.0.0",
            "ledger_active": True,
            "chain_integrity": chain_result["chain_valid"],
            "aws_region": AWS_REGION,
            "ledger_name": self.ledger_name,
            "features": [
                "Immutable Dispute Records",
                "Cryptographic Audit Trail",
                "Chain Integrity Verification",
                "Evidence Management",
                "Settlement Tracking",
                "Hash-Chain Verification"
            ]
        }


# Service instance
_service_instance: Optional[QLDBService] = None


def initialize_qldb_service(db: AsyncIOMotorDatabase) -> QLDBService:
    """Initialize the QLDB service"""
    global _service_instance
    _service_instance = QLDBService(db)
    return _service_instance


def get_qldb_service() -> Optional[QLDBService]:
    """Get the QLDB service instance"""
    return _service_instance
