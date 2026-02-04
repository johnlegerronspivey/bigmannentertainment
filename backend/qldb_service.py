"""
AWS QLDB Integration - Service Layer
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
import amazon.ion.simpleion as ion
from functools import partial

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
    """Service for AWS QLDB operations - Immutable Dispute Ledger"""
    
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

    async def _run_in_executor(self, func, *args):
        """Run a synchronous function in the default executor"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args)

    async def _ensure_schema(self):
        """Ensure QLDB tables and indexes exist"""
        await self._run_in_executor(self._ensure_schema_sync)

    def _ensure_schema_sync(self):
        try:
            def create_tables(transaction):
                tables = transaction.execute_statement("SELECT name FROM information_schema.user_tables")
                table_names = [t['name'] for t in tables]
                
                if 'Disputes' not in table_names:
                    logger.info("Creating Disputes table...")
                    transaction.execute_statement("CREATE TABLE Disputes")
                    transaction.execute_statement("CREATE INDEX ON Disputes(id)")
                    transaction.execute_statement("CREATE INDEX ON Disputes(dispute_number)")
                    transaction.execute_statement("CREATE INDEX ON Disputes(status)")
                
                if 'AuditTrail' not in table_names:
                    logger.info("Creating AuditTrail table...")
                    transaction.execute_statement("CREATE TABLE AuditTrail")
                    transaction.execute_statement("CREATE INDEX ON AuditTrail(id)")
                    transaction.execute_statement("CREATE INDEX ON AuditTrail(entity_id)")
                    transaction.execute_statement("CREATE INDEX ON AuditTrail(timestamp)")

            self.manager.execute_transaction(create_tables)
            logger.info("QLDB Schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize QLDB schema: {e}")

    # ==================== Dispute Operations ====================
    
    async def create_dispute(self, request: CreateDisputeRequest, user_id: str = "system") -> Dispute:
        """Create a new dispute"""
        return await self._run_in_executor(self._create_dispute_sync, request, user_id)

    def _create_dispute_sync(self, request: CreateDisputeRequest, user_id: str) -> Dispute:
        dispute_number = f"DISP-{datetime.now().year}-{os.urandom(2).hex().upper()}" # Simplified for demo
        
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
        
        def txn(transaction):
            transaction.execute_statement("INSERT INTO Disputes ?", ion.loads(json.dumps(dispute.dict(), default=str)))
            
        self.manager.execute_transaction(txn)
        
        # Create audit entry
        self._create_audit_entry_sync(CreateAuditEntryRequest(
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
        return await self._run_in_executor(self._get_disputes_sync, status, dispute_type, priority, limit, offset)

    def _get_disputes_sync(self, status, dispute_type, priority, limit, offset):
        query_parts = ["SELECT * FROM Disputes AS d"]
        where_clauses = []
        params = []
        
        if status:
            where_clauses.append("d.status = ?")
            params.append(status.value)
        if dispute_type:
            where_clauses.append("d.type = ?")
            params.append(dispute_type.value)
        if priority:
            where_clauses.append("d.priority = ?")
            params.append(priority.value)
            
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
            
        query = " ".join(query_parts)
        
        def txn(transaction):
            cursor = transaction.execute_statement(query, *params)
            all_disputes = [Dispute(**d) for d in cursor]
            # Sorting and pagination in Python for simplicity with QLDB (indexes help filtering)
            all_disputes.sort(key=lambda x: x.created_at, reverse=True)
            return all_disputes[offset:offset+limit], len(all_disputes)

        return self.manager.execute_transaction(txn)

    async def get_dispute(self, dispute_id: str) -> Optional[Dispute]:
        return await self._run_in_executor(self._get_dispute_sync, dispute_id)

    def _get_dispute_sync(self, dispute_id: str) -> Optional[Dispute]:
        def txn(transaction):
            # Check both id and dispute_number
            cursor = transaction.execute_statement("SELECT * FROM Disputes WHERE id = ?", dispute_id)
            results = list(cursor)
            if not results:
                cursor = transaction.execute_statement("SELECT * FROM Disputes WHERE dispute_number = ?", dispute_id)
                results = list(cursor)
            
            if results:
                return Dispute(**results[0])
            return None
            
        return self.manager.execute_transaction(txn)

    async def update_dispute(
        self,
        dispute_id: str,
        update: UpdateDisputeRequest,
        user_id: str = "system",
        user_name: str = "System"
    ) -> Optional[Dispute]:
        return await self._run_in_executor(self._update_dispute_sync, dispute_id, update, user_id, user_name)

    def _update_dispute_sync(self, dispute_id, update, user_id, user_name):
        def txn(transaction):
            # 1. Fetch
            cursor = transaction.execute_statement("SELECT * FROM Disputes WHERE id = ? OR dispute_number = ?", dispute_id, dispute_id)
            results = list(cursor)
            if not results:
                return None
            
            current_data = results[0]
            dispute = Dispute(**current_data)
            
            # 2. Update logic
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
            updated_dispute_dict = dispute.dict()
            updated_dispute_dict.update(update_data)
            updated_dispute_dict["content_hash"] = compute_content_hash(
                 {k: v for k, v in updated_dispute_dict.items() if k not in ["content_hash", "ledger_document_id"]}
            )
            
            # 3. Write back
            # QLDB DELETE and INSERT is safer than multiple SETs for complex objects in some drivers, 
            # but UPDATE is better. We'll use UPDATE with the full document or individual fields?
            # Creating a dynamic SET clause is tedious. 
            # We can use REPLACE/UPDATE logic. 
            # "UPDATE Disputes AS d SET d = ? WHERE d.id = ?" 
            
            transaction.execute_statement("UPDATE Disputes AS d SET d = ? WHERE d.id = ?", ion.loads(json.dumps(updated_dispute_dict, default=str)), dispute.id)

            return updated_dispute_dict, previous_state, new_state

        result = self.manager.execute_transaction(txn)
        if not result:
            return None
            
        updated_dict, prev, new_st = result
        
        # Audit
        event_type = AuditEventType.DISPUTE_STATUS_CHANGED if update.status else AuditEventType.DISPUTE_UPDATED
        if update.status == DisputeStatus.RESOLVED:
            event_type = AuditEventType.DISPUTE_RESOLVED

        self._create_audit_entry_sync(CreateAuditEntryRequest(
            event_type=event_type,
            entity_type="dispute",
            entity_id=updated_dict['dispute_number'],
            actor_id=user_id,
            actor_name=user_name,
            action_description=f"Updated dispute",
            metadata={"previous_state": prev, "new_state": new_st}
        ))

        return Dispute(**updated_dict)

    async def add_evidence(self, dispute_id: str, evidence: DisputeEvidence, user_id: str, user_name: str) -> Optional[Dispute]:
        return await self._run_in_executor(self._add_evidence_sync, dispute_id, evidence, user_id, user_name)

    def _add_evidence_sync(self, dispute_id, evidence, user_id, user_name):
        def txn(transaction):
            cursor = transaction.execute_statement("SELECT * FROM Disputes WHERE id = ? OR dispute_number = ?", dispute_id, dispute_id)
            results = list(cursor)
            if not results:
                return None
            
            dispute_dict = results[0]
            if 'evidence' not in dispute_dict:
                dispute_dict['evidence'] = []
            
            dispute_dict['evidence'].append(evidence.dict())
            dispute_dict['updated_at'] = datetime.now(timezone.utc)
            
            transaction.execute_statement("UPDATE Disputes AS d SET d = ? WHERE d.id = ?", ion.loads(json.dumps(dispute_dict, default=str)), dispute_dict['id'])
            return dispute_dict

        result = self.manager.execute_transaction(txn)
        if not result:
            return None

        # Audit
        self._create_audit_entry_sync(CreateAuditEntryRequest(
            event_type=AuditEventType.EVIDENCE_ADDED,
            entity_type="dispute",
            entity_id=result['dispute_number'],
            actor_id=user_id,
            actor_name=user_name,
            action_description=f"Added evidence: {evidence.title}",
            metadata={"evidence_type": evidence.evidence_type, "title": evidence.title}
        ))
        return Dispute(**result)

    async def add_comment(self, dispute_id: str, comment: DisputeComment) -> Optional[Dispute]:
        return await self._run_in_executor(self._add_comment_sync, dispute_id, comment)

    def _add_comment_sync(self, dispute_id, comment):
        def txn(transaction):
            cursor = transaction.execute_statement("SELECT * FROM Disputes WHERE id = ? OR dispute_number = ?", dispute_id, dispute_id)
            results = list(cursor)
            if not results:
                return None
            
            dispute_dict = results[0]
            if 'comments' not in dispute_dict:
                dispute_dict['comments'] = []
            
            dispute_dict['comments'].append(comment.dict())
            dispute_dict['updated_at'] = datetime.now(timezone.utc)
            
            transaction.execute_statement("UPDATE Disputes AS d SET d = ? WHERE d.id = ?", ion.loads(json.dumps(dispute_dict, default=str)), dispute_dict['id'])
            return dispute_dict

        result = self.manager.execute_transaction(txn)
        if not result:
            return None

        self._create_audit_entry_sync(CreateAuditEntryRequest(
            event_type=AuditEventType.COMMENT_ADDED,
            entity_type="dispute",
            entity_id=result['dispute_number'],
            actor_id=comment.author_id,
            actor_name=comment.author_name,
            action_description="Added comment to dispute",
            metadata={"is_internal": comment.is_internal}
        ))
        return Dispute(**result)

    # ==================== Audit Trail Operations ====================

    async def create_audit_entry(self, request: CreateAuditEntryRequest) -> AuditEntry:
        return await self._run_in_executor(self._create_audit_entry_sync, request)

    def _create_audit_entry_sync(self, request: CreateAuditEntryRequest) -> AuditEntry:
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
        
        # Calculate hashes
        entry.content_hash = compute_content_hash(
            entry.dict(exclude={"content_hash", "previous_hash", "ledger_document_id", "verified", "verification_proof"})
        )
        entry.previous_hash = self._last_audit_hash # In a real system, fetch latest from DB
        entry.verified = True
        
        self._last_audit_hash = compute_chain_hash(entry.content_hash, entry.previous_hash)
        
        def txn(transaction):
            transaction.execute_statement("INSERT INTO AuditTrail ?", ion.loads(json.dumps(entry.dict(), default=str)))
            
        self.manager.execute_transaction(txn)
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
        return await self._run_in_executor(self._get_audit_entries_sync, entity_id, entity_type, event_type, actor_id, limit, offset)

    def _get_audit_entries_sync(self, entity_id, entity_type, event_type, actor_id, limit, offset):
        query_parts = ["SELECT * FROM AuditTrail AS a"]
        where_clauses = []
        params = []
        
        if entity_id:
            where_clauses.append("a.entity_id = ?")
            params.append(entity_id)
        if entity_type:
            where_clauses.append("a.entity_type = ?")
            params.append(entity_type)
        if event_type:
            where_clauses.append("a.event_type = ?")
            params.append(event_type.value)
        if actor_id:
            where_clauses.append("a.actor_id = ?")
            params.append(actor_id)

        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
            
        query = " ".join(query_parts)
        
        def txn(transaction):
            cursor = transaction.execute_statement(query, *params)
            entries = [AuditEntry(**d) for d in cursor]
            entries.sort(key=lambda x: x.timestamp, reverse=True)
            return entries[offset:offset+limit], len(entries)

        return self.manager.execute_transaction(txn)

    async def verify_audit_entry(self, entry_id: str) -> VerificationResponse:
        return await self._run_in_executor(self._verify_audit_entry_sync, entry_id)

    def _verify_audit_entry_sync(self, entry_id: str) -> VerificationResponse:
        def txn(transaction):
            cursor = transaction.execute_statement("SELECT * FROM AuditTrail WHERE id = ?", entry_id)
            results = list(cursor)
            return results[0] if results else None
            
        doc = self.manager.execute_transaction(txn)
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
        return await self._run_in_executor(self._verify_chain_integrity_sync)

    def _verify_chain_integrity_sync(self) -> Dict[str, Any]:
        def txn(transaction):
            cursor = transaction.execute_statement("SELECT * FROM AuditTrail")
            return [AuditEntry(**d) for d in cursor]
            
        entries = self.manager.execute_transaction(txn)
        entries.sort(key=lambda x: x.timestamp)
        
        prev_hash = "GENESIS"
        valid_count = 0
        invalid_entries = []
        
        for entry in entries:
            if entry.previous_hash != prev_hash:
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
            def txn(transaction):
                transaction.execute_statement("SELECT 1 FROM information_schema.user_tables LIMIT 1")
            await self._run_in_executor(lambda: self.manager.execute_transaction(txn))
            return {
                "status": "healthy",
                "service": "AWS QLDB Dispute Ledger",
                "mode": "Live Driver",
                "ledger": self.ledger_name
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "service": "AWS QLDB Dispute Ledger"
            }

    async def get_dashboard_stats(self) -> QLDBDashboardStats:
        # Implementing this fully would require more queries. Returning simplified stats.
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
