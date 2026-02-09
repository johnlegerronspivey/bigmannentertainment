"""
AWS QLDB Integration - Service Layer
Refactored to use "Emergent Ledger" (Postgres + JSONB + Hash Chaining)
Business logic for immutable dispute ledger and audit trail system
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from dotenv import load_dotenv
import hashlib
import json
# import amazon.ion.simpleion as ion # Deprecated for JSONB

from qldb_models import (
    Dispute, DisputeStatus, DisputeType, Priority, DisputeParty,
    DisputeEvidence, DisputeComment, DisputeSettlement,
    CreateDisputeRequest, UpdateDisputeRequest,
    AuditEntry, AuditEventType, CreateAuditEntryRequest,
    DisputeStats, AuditStats, QLDBDashboardStats,
    VerificationResponse, compute_content_hash, compute_chain_hash
)

from qldb_manager import qldb_manager

load_dotenv()
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
QLDB_LEDGER_NAME = os.getenv("QLDB_LEDGER_NAME", "dispute-ledger")

class QLDBService:
    """Service for Emergent Ledger (formerly QLDB) operations"""
    
    def __init__(self):
        self.manager = qldb_manager
        self.ledger_name = QLDB_LEDGER_NAME
        self._last_audit_hash = "GENESIS"
        
        # Initialize tables asynchronously
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._ensure_schema())
        except RuntimeError:
            pass

    async def _ensure_schema(self):
        """Ensure Postgres tables exist"""
        await self.manager.initialize()

    # ==================== Dispute Operations ====================
    
    async def create_dispute(self, request: CreateDisputeRequest, user_id: str = "system") -> Dispute:
        """Create a new dispute"""
        dispute_number = f"DISP-{datetime.now().year}-{os.urandom(2).hex().upper()}"
        
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
        
        dispute.content_hash = compute_content_hash(
            dispute.dict(exclude={"content_hash", "ledger_document_id"})
        )
        
        # Insert into Ledger
        # We assume the ID in the dispute object is the document_id
        await self.manager.ledger.insert_document("Disputes", dispute.dict())
        
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
        
        # In our PostgresLedger, we can use a raw query or fetch all for a table
        # Since the driver currently has execute_query returning 'data' blobs, we might need filtering here
        # For efficiency, we should enhance the driver, but for now filtering in memory or basic SQL
        
        # Note: postgres_ledger.execute_query returns all rows for a table currently
        raw_docs = await self.manager.ledger.execute_query("SELECT * FROM Disputes")
        
        all_disputes = []
        for d in raw_docs:
            try:
                dispute = Dispute(**d)
                
                # Apply Filters
                if status and dispute.status != status:
                    continue
                if dispute_type and dispute.type != dispute_type:
                    continue
                if priority and dispute.priority != priority:
                    continue
                    
                all_disputes.append(dispute)
            except Exception as e:
                logger.error(f"Error parsing dispute: {e}")
                continue

        # Sort by created_at desc
        all_disputes.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_disputes[offset:offset+limit], len(all_disputes)

    async def get_dispute(self, dispute_id: str) -> Optional[Dispute]:
        # Try fetching by ID first
        doc = await self.manager.ledger.get_document("Disputes", dispute_id)
        if doc:
            return Dispute(**doc)
            
        # Fallback: Search by dispute_number (inefficient but works for now)
        raw_docs = await self.manager.ledger.execute_query("SELECT * FROM Disputes")
        for d in raw_docs:
            if d.get('dispute_number') == dispute_id:
                return Dispute(**d)
        
        return None

    async def update_dispute(
        self,
        dispute_id: str,
        update: UpdateDisputeRequest,
        user_id: str = "system",
        user_name: str = "System"
    ) -> Optional[Dispute]:
        
        # 1. Fetch current
        dispute = await self.get_dispute(dispute_id)
        if not dispute:
            return None
            
        # 2. Update logic
        current_data = dispute.dict()
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

        # Merge updates
        current_data.update(update_data)
        current_data["content_hash"] = compute_content_hash(
             {k: v for k, v in current_data.items() if k not in ["content_hash", "ledger_document_id"]}
        )
        
        # 3. Write back (Insert new version)
        await self.manager.ledger.insert_document("Disputes", current_data)
        
        # Audit
        event_type = AuditEventType.DISPUTE_STATUS_CHANGED if update.status else AuditEventType.DISPUTE_UPDATED
        if update.status == DisputeStatus.RESOLVED:
            event_type = AuditEventType.DISPUTE_RESOLVED

        await self.create_audit_entry(CreateAuditEntryRequest(
            event_type=event_type,
            entity_type="dispute",
            entity_id=current_data['dispute_number'],
            actor_id=user_id,
            actor_name=user_name,
            action_description=f"Updated dispute",
            metadata={"previous_state": previous_state, "new_state": new_state}
        ))

        return Dispute(**current_data)

    async def add_evidence(self, dispute_id: str, evidence: DisputeEvidence, user_id: str, user_name: str) -> Optional[Dispute]:
        dispute = await self.get_dispute(dispute_id)
        if not dispute:
            return None
            
        dispute_dict = dispute.dict()
        if 'evidence' not in dispute_dict or dispute_dict['evidence'] is None:
            dispute_dict['evidence'] = []
        
        dispute_dict['evidence'].append(evidence.dict())
        dispute_dict['updated_at'] = datetime.now(timezone.utc)
        
        await self.manager.ledger.insert_document("Disputes", dispute_dict)
        
        await self.create_audit_entry(CreateAuditEntryRequest(
            event_type=AuditEventType.EVIDENCE_ADDED,
            entity_type="dispute",
            entity_id=dispute_dict['dispute_number'],
            actor_id=user_id,
            actor_name=user_name,
            action_description=f"Added evidence: {evidence.title}",
            metadata={"evidence_type": evidence.evidence_type, "title": evidence.title}
        ))
        
        return Dispute(**dispute_dict)

    async def add_comment(self, dispute_id: str, comment: DisputeComment) -> Optional[Dispute]:
        dispute = await self.get_dispute(dispute_id)
        if not dispute:
            return None
            
        dispute_dict = dispute.dict()
        if 'comments' not in dispute_dict or dispute_dict['comments'] is None:
            dispute_dict['comments'] = []
        
        dispute_dict['comments'].append(comment.dict())
        dispute_dict['updated_at'] = datetime.now(timezone.utc)
        
        await self.manager.ledger.insert_document("Disputes", dispute_dict)
        
        await self.create_audit_entry(CreateAuditEntryRequest(
            event_type=AuditEventType.COMMENT_ADDED,
            entity_type="dispute",
            entity_id=dispute_dict['dispute_number'],
            actor_id=comment.author_id,
            actor_name=comment.author_name,
            action_description="Added comment to dispute",
            metadata={"is_internal": comment.is_internal}
        ))
        
        return Dispute(**dispute_dict)

    # ==================== Audit Trail Operations ====================

    async def create_audit_entry(self, request: CreateAuditEntryRequest) -> AuditEntry:
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
        
        entry.content_hash = compute_content_hash(
            entry.dict(exclude={"content_hash", "previous_hash", "ledger_document_id", "verified", "verification_proof"})
        )
        entry.previous_hash = self._last_audit_hash 
        entry.verified = True
        
        self._last_audit_hash = compute_chain_hash(entry.content_hash, entry.previous_hash)
        
        await self.manager.ledger.insert_document("AuditTrail", entry.dict())
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
        
        raw_entries = await self.manager.ledger.execute_query("SELECT * FROM AuditTrail")
        entries = []
        
        for d in raw_entries:
            try:
                entry = AuditEntry(**d)
                if entity_id and entry.entity_id != entity_id: continue
                if entity_type and entry.entity_type != entity_type: continue
                if event_type and entry.event_type != event_type: continue
                if actor_id and entry.actor_id != actor_id: continue
                entries.append(entry)
            except: continue
            
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        return entries[offset:offset+limit], len(entries)

    async def verify_audit_entry(self, entry_id: str) -> VerificationResponse:
        doc = await self.manager.ledger.get_document("AuditTrail", entry_id)
        if not doc:
            return VerificationResponse(document_id=entry_id, verified=False, chain_valid=False)
            
        entry = AuditEntry(**doc)
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
        raw_entries = await self.manager.ledger.execute_query("SELECT * FROM AuditTrail")
        entries = [AuditEntry(**d) for d in raw_entries]
        entries.sort(key=lambda x: x.timestamp)
        
        prev_hash = "GENESIS"
        valid_count = 0
        invalid_entries = []
        
        # Note: In a real system we would verify the 'hash' and 'previous_hash' columns of the LedgerTransaction table too
        # But here we are verifying the payload level hashes
        
        for entry in entries:
            if entry.previous_hash != prev_hash:
                # In a high volume system this genesis check might need adjustment (start of stream)
                if prev_hash != "GENESIS": 
                    invalid_entries.append({"entry_id": entry.id, "reason": "Hash mismatch"})
            else:
                valid_count += 1
            prev_hash = compute_chain_hash(entry.content_hash, entry.previous_hash)
            
        return {
            "chain_valid": len(invalid_entries) == 0,
            "total_entries": len(entries),
            "valid_entries": valid_count,
            "invalid_entries": invalid_entries,
            "verification_timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def check_health(self) -> Dict[str, Any]:
        try:
            # Simple check
            await self.manager.ledger.execute_query("SELECT * FROM Disputes LIMIT 1")
            return {
                "status": "healthy",
                "service": "Emergent Ledger (Postgres)",
                "mode": "Active",
                "ledger": self.ledger_name
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "service": "Emergent Ledger (Postgres)"
            }

    async def get_dashboard_stats(self) -> QLDBDashboardStats:
        disputes, _ = await self.get_disputes(limit=5)
        return QLDBDashboardStats(
            recent_disputes=disputes
        )

# Service instance
_service_instance: Optional[QLDBService] = None

def initialize_qldb_service(db=None) -> QLDBService:
    """Initialize the QLDB service"""
    global _service_instance
    _service_instance = QLDBService()
    return _service_instance

def get_qldb_service() -> Optional[QLDBService]:
    """Get the QLDB service instance"""
    return _service_instance
