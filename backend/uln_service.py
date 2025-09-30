"""
Unified Label Network (ULN) Service
===================================

Core service implementing the foundational Label Registry Service and ULN functionality:
- Label registration and identity management
- Cross-label content sharing and metadata sync
- Multi-label royalty engine and distribution
- Smart contract integration and DAO governance
- Compliance and jurisdiction management
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import hashlib
import json
import logging
from uln_models import *

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ULNService:
    """
    Unified Label Network Service - Core implementation for the ULN system
    """
    
    def __init__(self):
        # Database collections
        self.uln_labels = db.uln_labels
        self.federated_content = db.federated_content
        self.royalty_pools = db.royalty_pools
        self.royalty_earnings = db.royalty_earnings
        self.payout_ledger = db.payout_ledger
        self.dao_proposals = db.dao_proposals
        self.audit_trail = db.uln_audit_trail
        self.jurisdiction_rules = db.jurisdiction_rules
        self.smart_contracts = db.uln_smart_contracts
        
        # Initialize jurisdiction rules (will be called lazily when needed)
        self._jurisdiction_rules_initialized = False
        
        # Initialize major labels (will be called when needed)
        self._major_labels_initialized = False
    
    # ===== LABEL REGISTRY SERVICE (FOUNDATIONAL) =====
    
    async def register_label(self, registration_data: LabelRegistrationRequest, 
                           created_by: str) -> Dict[str, Any]:
        """
        Register a new label in the ULN system
        This is the foundational service for the entire ULN
        """
        try:
            # Generate global label ID
            global_id = GlobalLabelID()
            
            # Create complete ULN label
            uln_label = ULNLabel(
                global_id=global_id,
                label_type=registration_data.label_type,
                integration_type=registration_data.integration_type,
                metadata_profile=registration_data.metadata_profile,
                associated_entities=registration_data.initial_entities
            )
            
            # Store in database
            label_dict = uln_label.dict()
            # Convert datetime objects to ISO strings for MongoDB
            label_dict = self._prepare_for_mongo(label_dict)
            
            result = await self.uln_labels.insert_one(label_dict)
            
            if result.inserted_id:
                # Create audit trail entry
                await self._create_audit_entry(
                    action_type="label_registered",
                    actor_id=created_by,
                    actor_type="system",
                    resource_type="label",
                    resource_id=global_id.id,
                    action_description=f"Registered new {registration_data.label_type.value} label: {registration_data.metadata_profile.name}",
                    changes_made={"status": "registered", "global_id": global_id.id}
                )
                
                # Initialize smart contracts if requested
                if registration_data.smart_contract_requirements:
                    await self._initialize_smart_contracts(
                        global_id.id, 
                        registration_data.smart_contract_requirements
                    )
                
                return {
                    "success": True,
                    "global_label_id": global_id.id,
                    "message": f"Label '{registration_data.metadata_profile.name}' successfully registered in ULN",
                    "onboarding_status": "registered",
                    "next_steps": [
                        "Complete compliance verification",
                        "Set up smart contract bindings",
                        "Configure cross-label partnerships"
                    ]
                }
            
            return {
                "success": False,
                "error": "Failed to register label in database"
            }
            
        except Exception as e:
            logger.error(f"Error registering label: {str(e)}")
            return {
                "success": False,
                "error": f"Registration failed: {str(e)}"
            }
    
    async def get_label_by_id(self, global_id: str) -> Optional[Dict[str, Any]]:
        """Get complete label information by global ID"""
        try:
            label = await self.uln_labels.find_one({"global_id.id": global_id})
            if label:
                label.pop("_id", None)
                return self._parse_from_mongo(label)
            return None
        except Exception as e:
            logger.error(f"Error fetching label {global_id}: {str(e)}")
            return None
    
    async def update_label_metadata(self, global_id: str, metadata_updates: Dict[str, Any], 
                                  updated_by: str) -> Dict[str, Any]:
        """Update label metadata profile"""
        try:
            # Prepare update data
            update_dict = {
                f"metadata_profile.{key}": value 
                for key, value in metadata_updates.items()
            }
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.uln_labels.update_one(
                {"global_id.id": global_id},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                # Create audit trail
                await self._create_audit_entry(
                    action_type="label_metadata_updated",
                    actor_id=updated_by,
                    actor_type="admin",
                    resource_type="label",
                    resource_id=global_id,
                    action_description=f"Updated metadata for label {global_id}",
                    changes_made=metadata_updates
                )
                
                return {
                    "success": True,
                    "message": "Label metadata updated successfully"
                }
            
            return {
                "success": False,
                "error": "Label not found or no changes made"
            }
            
        except Exception as e:
            logger.error(f"Error updating label metadata: {str(e)}")
            return {
                "success": False,
                "error": f"Update failed: {str(e)}"
            }
    
    async def get_label_directory(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comprehensive label directory for UI display"""
        try:
            query = {"status": "active"}
            if filters:
                if filters.get("label_type"):
                    query["label_type"] = filters["label_type"]
                if filters.get("territory"):
                    query["metadata_profile.jurisdiction"] = filters["territory"]
                if filters.get("genre"):
                    query["metadata_profile.genre_specialization"] = {"$in": [filters["genre"]]}
            
            labels = await self.uln_labels.find(query).to_list(length=None)
            
            # Process labels for hub display
            label_hub_entries = []
            for label in labels:
                label.pop("_id", None)
                label_data = self._parse_from_mongo(label)
                
                # Create hub entry
                hub_entry = LabelHubEntry(
                    global_id=label_data["global_id"]["id"],
                    name=label_data["metadata_profile"]["name"],
                    label_type=label_data["label_type"],
                    integration_type=label_data["integration_type"],
                    territory=label_data["metadata_profile"]["jurisdiction"],
                    genre_focus=label_data["metadata_profile"].get("genre_specialization", []),
                    dao_affiliated=len(label_data.get("smart_contracts", [])) > 0,
                    status=label_data["status"],
                    last_activity=datetime.fromisoformat(label_data["updated_at"]),
                    verification_status=label_data["global_id"].get("verification_status", "pending"),
                    compliance_status="verified" if label_data.get("compliance_verified") else "pending",
                    blockchain_enabled=any(sc.get("blockchain_network") for sc in label_data.get("smart_contracts", []))
                )
                
                label_hub_entries.append(hub_entry.dict())
            
            # Generate statistics
            stats = await self._generate_directory_stats(labels)
            
            return {
                "success": True,
                "labels": label_hub_entries,  # Changed from label_hub_entries to labels for consistency
                "label_hub_entries": label_hub_entries,  # Keep both for backward compatibility
                "statistics": stats,
                "total_labels": len(label_hub_entries)
            }
            
        except Exception as e:
            logger.error(f"Error fetching label directory: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fetch directory: {str(e)}"
            }
    
    # ===== CROSS-LABEL CONTENT SHARING =====
    
    async def create_federated_content_access(self, request: CrossLabelContentRequest, 
                                            requested_by: str) -> Dict[str, Any]:
        """Create federated access for cross-label content sharing"""
        try:
            # Verify requesting label exists
            requesting_label = await self.get_label_by_id(request.requesting_label_id)
            if not requesting_label:
                return {
                    "success": False,
                    "error": "Requesting label not found in ULN"
                }
            
            # Verify target labels exist
            for target_label_id in request.target_labels:
                target_label = await self.get_label_by_id(target_label_id)
                if not target_label:
                    return {
                        "success": False,
                        "error": f"Target label {target_label_id} not found in ULN"
                    }
            
            # Create federated content access
            federated_access = FederatedContentAccess(
                content_id=request.content_id,
                primary_label_id=request.requesting_label_id,
                licensing_labels=request.target_labels,
                rights_splits=request.proposed_rights_splits,
                access_level=request.access_level,
                usage_attribution={"created_by": requested_by}
            )
            
            # Store in database
            access_dict = federated_access.dict()
            access_dict = self._prepare_for_mongo(access_dict)
            
            result = await self.federated_content.insert_one(access_dict)
            
            if result.inserted_id:
                # Create audit trail
                await self._create_audit_entry(
                    action_type="federated_content_created",
                    actor_id=requested_by,
                    actor_type="label",
                    resource_type="content",
                    resource_id=request.content_id,
                    action_description=f"Created federated access for content {request.content_id}",
                    changes_made={
                        "primary_label": request.requesting_label_id,
                        "target_labels": request.target_labels,
                        "access_level": request.access_level
                    },
                    related_labels=[request.requesting_label_id] + request.target_labels
                )
                
                # TODO: Trigger DAO proposal if required
                if len(request.target_labels) > 2:  # Multiple labels require DAO approval
                    await self._create_dao_proposal_for_content_sharing(request, requested_by)
                
                return {
                    "success": True,
                    "federated_access_id": str(result.inserted_id),
                    "message": "Federated content access created successfully",
                    "dao_approval_required": len(request.target_labels) > 2
                }
            
            return {
                "success": False,
                "error": "Failed to create federated access"
            }
            
        except Exception as e:
            logger.error(f"Error creating federated content access: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create access: {str(e)}"
            }
    
    async def get_federated_content_by_label(self, label_id: str) -> List[Dict[str, Any]]:
        """Get all federated content for a specific label"""
        try:
            query = {
                "$or": [
                    {"primary_label_id": label_id},
                    {"co_owning_labels": {"$in": [label_id]}},
                    {"licensing_labels": {"$in": [label_id]}}
                ]
            }
            
            federated_content = await self.federated_content.find(query).to_list(length=None)
            
            result = []
            for content in federated_content:
                content.pop("_id", None)
                result.append(self._parse_from_mongo(content))
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching federated content: {str(e)}")
            return []
    
    # ===== MULTI-LABEL ROYALTY ENGINE =====
    
    async def create_royalty_pool(self, request: RoyaltyDistributionRequest, 
                                created_by: str) -> Dict[str, Any]:
        """Create a multi-label royalty pool for distribution"""
        try:
            # Verify all participating labels exist
            for label_id in request.participating_labels:
                label = await self.get_label_by_id(label_id)
                if not label:
                    return {
                        "success": False,
                        "error": f"Label {label_id} not found in ULN"
                    }
            
            # Create royalty pool
            royalty_pool = MultiLabelRoyaltyPool(
                pool_period=request.pool_period,
                participating_labels=request.participating_labels
            )
            
            # Store in database
            pool_dict = royalty_pool.dict()
            pool_dict = self._prepare_for_mongo(pool_dict)
            
            result = await self.royalty_pools.insert_one(pool_dict)
            
            if result.inserted_id:
                # Create audit trail
                await self._create_audit_entry(
                    action_type="royalty_pool_created",
                    actor_id=created_by,
                    actor_type="admin",
                    resource_type="royalty_pool",
                    resource_id=royalty_pool.pool_id,
                    action_description=f"Created royalty pool for period {request.pool_period}",
                    changes_made={
                        "participating_labels": request.participating_labels,
                        "distribution_method": request.distribution_method
                    },
                    related_labels=request.participating_labels
                )
                
                # Create DAO proposal if required
                if request.dao_approval_required:
                    await self._create_dao_proposal_for_royalty_distribution(request, created_by)
                
                return {
                    "success": True,
                    "pool_id": royalty_pool.pool_id,
                    "message": "Royalty pool created successfully",
                    "dao_approval_required": request.dao_approval_required
                }
            
            return {
                "success": False,
                "error": "Failed to create royalty pool"
            }
            
        except Exception as e:
            logger.error(f"Error creating royalty pool: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create pool: {str(e)}"
            }
    
    async def process_royalty_earnings(self, earnings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process incoming royalty earnings for multi-label distribution"""
        try:
            processed_earnings = []
            total_processed = 0.0
            
            for earning in earnings_data:
                # Create royalty earning record
                royalty_earning = RoyaltyEarning(
                    content_id=earning["content_id"],
                    source=RoyaltySource(**earning["source"]),
                    royalty_type=RoyaltyType(earning["royalty_type"]),
                    gross_amount=earning["gross_amount"],
                    currency=earning.get("currency", "USD"),
                    period_start=datetime.fromisoformat(earning["period_start"]).date(),
                    period_end=datetime.fromisoformat(earning["period_end"]).date(),
                    usage_data=earning.get("usage_data", {})
                )
                
                # Apply label splits (this would come from federated content access)
                await self._apply_label_splits(royalty_earning)
                
                # Store earning
                earning_dict = royalty_earning.dict()
                earning_dict = self._prepare_for_mongo(earning_dict)
                
                await self.royalty_earnings.insert_one(earning_dict)
                processed_earnings.append(royalty_earning.earning_id)
                total_processed += royalty_earning.gross_amount
            
            return {
                "success": True,
                "processed_earnings": len(processed_earnings),
                "total_amount": total_processed,
                "earnings_ids": processed_earnings
            }
            
        except Exception as e:
            logger.error(f"Error processing royalty earnings: {str(e)}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }
    
    async def generate_payout_ledger(self, pool_id: str) -> Dict[str, Any]:
        """Generate transparent payout ledger for a royalty pool"""
        try:
            # Get royalty pool
            pool = await self.royalty_pools.find_one({"pool_id": pool_id})
            if not pool:
                return {
                    "success": False,
                    "error": "Royalty pool not found"
                }
            
            pool = self._parse_from_mongo(pool)
            
            # Generate ledger entries for each recipient
            ledger_entries = []
            
            for label_id, allocation in pool["label_allocations"].items():
                if allocation > 0:
                    # Get label info
                    label = await self.get_label_by_id(label_id)
                    if label:
                        # Calculate deductions (taxes, fees)
                        deductions = await self._calculate_deductions(
                            label_id, 
                            allocation, 
                            pool["currency"]
                        )
                        
                        # Create ledger entry
                        ledger_entry = PayoutLedger(
                            pool_id=pool_id,
                            recipient_id=label_id,
                            recipient_type="label",
                            recipient_name=label["metadata_profile"]["name"],
                            gross_amount=allocation,
                            deductions=deductions,
                            net_amount=allocation - sum(deductions.values()),
                            currency=pool["currency"]
                        )
                        
                        # Store ledger entry
                        ledger_dict = ledger_entry.dict()
                        ledger_dict = self._prepare_for_mongo(ledger_dict)
                        
                        await self.payout_ledger.insert_one(ledger_dict)
                        ledger_entries.append(ledger_entry.ledger_id)
            
            return {
                "success": True,
                "ledger_entries": len(ledger_entries),
                "total_payouts": len(ledger_entries),
                "pool_id": pool_id
            }
            
        except Exception as e:
            logger.error(f"Error generating payout ledger: {str(e)}")
            return {
                "success": False,
                "error": f"Ledger generation failed: {str(e)}"
            }
    
    # ===== DAO GOVERNANCE SYSTEM =====
    
    async def create_dao_proposal(self, proposal_data: Dict[str, Any], 
                                proposer_id: str) -> Dict[str, Any]:
        """Create a new DAO proposal for ULN governance"""
        try:
            # Calculate voting power for affected labels
            voting_power = {}
            if proposal_data.get("affected_labels"):
                for label_id in proposal_data["affected_labels"]:
                    # Voting power based on label size, revenue, etc. (simplified)
                    voting_power[label_id] = 1.0  # Equal voting for now
            
            # Create DAO proposal
            dao_proposal = DAOProposal(
                proposal_type=DAOVoteType(proposal_data["proposal_type"]),
                title=proposal_data["title"],
                description=proposal_data["description"],
                proposer_id=proposer_id,
                affected_labels=proposal_data.get("affected_labels", []),
                affected_content=proposal_data.get("affected_content", []),
                proposed_changes=proposal_data.get("proposed_changes", {}),
                voting_power_by_label=voting_power,
                voting_deadline=datetime.fromisoformat(proposal_data["voting_deadline"])
            )
            
            # Store proposal
            proposal_dict = dao_proposal.dict()
            proposal_dict = self._prepare_for_mongo(proposal_dict)
            
            result = await self.dao_proposals.insert_one(proposal_dict)
            
            if result.inserted_id:
                # Create audit trail
                await self._create_audit_entry(
                    action_type="dao_proposal_created",
                    actor_id=proposer_id,
                    actor_type="label",
                    resource_type="dao_proposal",
                    resource_id=dao_proposal.proposal_id,
                    action_description=f"Created DAO proposal: {proposal_data['title']}",
                    changes_made={"proposal_type": proposal_data["proposal_type"]},
                    related_labels=proposal_data.get("affected_labels", [])
                )
                
                return {
                    "success": True,
                    "proposal_id": dao_proposal.proposal_id,
                    "message": "DAO proposal created successfully",
                    "voting_deadline": proposal_data["voting_deadline"]
                }
            
            return {
                "success": False,
                "error": "Failed to create DAO proposal"
            }
            
        except Exception as e:
            logger.error(f"Error creating DAO proposal: {str(e)}")
            return {
                "success": False,
                "error": f"Proposal creation failed: {str(e)}"
            }
    
    async def cast_dao_vote(self, proposal_id: str, voter_id: str, 
                          vote: str, voting_power: float) -> Dict[str, Any]:
        """Cast a vote on a DAO proposal"""
        try:
            # Validate vote
            if vote not in ["for", "against", "abstain"]:
                return {
                    "success": False,
                    "error": "Invalid vote. Must be 'for', 'against', or 'abstain'"
                }
            
            # Update proposal with vote
            vote_field = f"votes_{vote}"
            result = await self.dao_proposals.update_one(
                {"proposal_id": proposal_id},
                {
                    "$set": {
                        f"{vote_field}.{voter_id}": voting_power,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            if result.modified_count:
                # Create audit trail
                await self._create_audit_entry(
                    action_type="dao_vote_cast",
                    actor_id=voter_id,
                    actor_type="label",
                    resource_type="dao_proposal",
                    resource_id=proposal_id,
                    action_description=f"Cast {vote} vote on proposal {proposal_id}",
                    changes_made={"vote": vote, "voting_power": voting_power}
                )
                
                # Check if proposal should be resolved
                await self._check_proposal_resolution(proposal_id)
                
                return {
                    "success": True,
                    "message": f"Vote '{vote}' cast successfully",
                    "voting_power": voting_power
                }
            
            return {
                "success": False,
                "error": "Proposal not found or vote already cast"
            }
            
        except Exception as e:
            logger.error(f"Error casting DAO vote: {str(e)}")
            return {
                "success": False,
                "error": f"Vote casting failed: {str(e)}"
            }
    
    # ===== DASHBOARD AND ANALYTICS =====
    
    async def get_uln_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive ULN dashboard statistics"""
        try:
            # Ensure jurisdiction rules are initialized
            await self._initialize_jurisdiction_rules()
            # Count labels by status and type
            total_labels = await self.uln_labels.count_documents({})
            active_labels = await self.uln_labels.count_documents({"status": "active"})
            
            # Count federated content
            total_content_shared = await self.federated_content.count_documents({})
            
            # Count royalty pools
            total_royalty_pools = await self.royalty_pools.count_documents({})
            
            # Count DAO proposals
            total_dao_proposals = await self.dao_proposals.count_documents({})
            active_proposals = await self.dao_proposals.count_documents({"status": "active"})
            
            # Geographic distribution
            labels_by_territory = {}
            territory_pipeline = [
                {"$group": {
                    "_id": "$metadata_profile.jurisdiction", 
                    "count": {"$sum": 1}
                }}
            ]
            async for result in self.uln_labels.aggregate(territory_pipeline):
                labels_by_territory[result["_id"]] = result["count"]
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            thirty_days_ago_iso = thirty_days_ago.isoformat()
            
            recent_registrations = await self.uln_labels.count_documents({
                "created_at": {"$gte": thirty_days_ago_iso}
            })
            
            recent_content_shares = await self.federated_content.count_documents({
                "created_at": {"$gte": thirty_days_ago_iso}
            })
            
            recent_proposals = await self.dao_proposals.count_documents({
                "created_at": {"$gte": thirty_days_ago_iso}
            })
            
            # Financial metrics (simplified - would be calculated from actual earnings)
            total_revenue_pipeline = [
                {"$group": {
                    "_id": None,
                    "total": {"$sum": "$gross_amount"}
                }}
            ]
            
            total_revenue_processed = 0.0
            async for result in self.royalty_earnings.aggregate(total_revenue_pipeline):
                total_revenue_processed = result.get("total", 0.0)
            
            # Pending distributions
            pending_distributions = await self.payout_ledger.count_documents({
                "status": "pending"
            })
            
            stats = ULNDashboardStats(
                total_labels=total_labels,
                active_labels=active_labels,
                total_content_shared=total_content_shared,
                total_royalty_pools=total_royalty_pools,
                total_dao_proposals=total_dao_proposals,
                total_revenue_processed=total_revenue_processed,
                pending_distributions=float(pending_distributions),
                labels_by_territory=labels_by_territory,
                recent_registrations=recent_registrations,
                recent_content_shares=recent_content_shares,
                recent_proposals=recent_proposals
            )
            
            return {
                "success": True,
                "dashboard_stats": stats.dict()
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard stats: {str(e)}")
            return {
                "success": False,
                "error": f"Stats generation failed: {str(e)}"
            }
    
    # ===== HELPER METHODS =====
    
    async def _initialize_jurisdiction_rules(self):
        """Initialize default jurisdiction rules"""
        try:
            if self._jurisdiction_rules_initialized:
                return
                
            # Check if rules already exist
            existing_rules = await self.jurisdiction_rules.count_documents({})
            if existing_rules > 0:
                self._jurisdiction_rules_initialized = True
                return
            
            # Default jurisdiction rules
            default_rules = [
                {
                    "jurisdiction": "US",
                    "tax_rate": 0.30,
                    "vat_rate": 0.0,
                    "withholding_requirements": {"non_resident": 0.30},
                    "reporting_requirements": ["1099", "W9"],
                    "licensing_requirements": ["ASCAP", "BMI", "SESAC"],
                    "data_protection_rules": ["CCPA"],
                    "content_restrictions": ["explicit_content_labeling"],
                    "currency_restrictions": []
                },
                {
                    "jurisdiction": "UK",
                    "tax_rate": 0.20,
                    "vat_rate": 0.20,
                    "withholding_requirements": {},
                    "reporting_requirements": ["VAT_return"],
                    "licensing_requirements": ["PRS", "PPL"],
                    "data_protection_rules": ["GDPR", "UK_GDPR"],
                    "content_restrictions": ["age_verification"],
                    "currency_restrictions": []
                },
                {
                    "jurisdiction": "EU",
                    "tax_rate": 0.25,
                    "vat_rate": 0.21,
                    "withholding_requirements": {},
                    "reporting_requirements": ["VAT_return", "MOSS"],
                    "licensing_requirements": ["local_PRO"],
                    "data_protection_rules": ["GDPR"],
                    "content_restrictions": ["digital_services_act"],
                    "currency_restrictions": []
                }
            ]
            
            for rule in default_rules:
                await self.jurisdiction_rules.insert_one(rule)
            
            self._jurisdiction_rules_initialized = True
            logger.info("Initialized default jurisdiction rules")
            
        except Exception as e:
            logger.error(f"Error initializing jurisdiction rules: {str(e)}")
    
    def _prepare_for_mongo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for MongoDB storage by converting datetime objects"""
        def convert_datetime(obj):
            if isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            else:
                return obj
        
        return convert_datetime(data)
    
    def _parse_from_mongo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse data from MongoDB by converting ISO strings back to datetime objects"""
        def convert_iso_strings(obj):
            if isinstance(obj, dict):
                return {k: convert_iso_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_iso_strings(item) for item in obj]
            elif isinstance(obj, str):
                # Try to parse ISO datetime strings
                if 'T' in obj and obj.endswith('Z') or '+' in obj[-6:]:
                    try:
                        return datetime.fromisoformat(obj.replace('Z', '+00:00'))
                    except ValueError:
                        return obj
                # Try to parse ISO date strings
                elif len(obj) == 10 and obj.count('-') == 2:
                    try:
                        return datetime.fromisoformat(obj).date()
                    except ValueError:
                        return obj
                return obj
            else:
                return obj
        
        return convert_iso_strings(data)
    
    async def _create_audit_entry(self, action_type: str, actor_id: str, actor_type: str,
                                resource_type: str, resource_id: str, action_description: str,
                                changes_made: Dict[str, Any], related_labels: List[str] = None):
        """Create an immutable audit trail entry"""
        try:
            # Get previous hash for chaining
            last_entry = await self.audit_trail.find_one(
                {}, sort=[("timestamp", -1)]
            )
            previous_hash = last_entry.get("current_hash") if last_entry else "genesis"
            
            # Create audit entry
            audit_entry = AuditTrailEntry(
                action_type=action_type,
                actor_id=actor_id,
                actor_type=actor_type,
                resource_type=resource_type,
                resource_id=resource_id,
                action_description=action_description,
                changes_made=changes_made,
                related_labels=related_labels or [],
                previous_hash=previous_hash,
                current_hash=""  # Will be calculated
            )
            
            # Calculate current hash
            hash_data = f"{audit_entry.entry_id}{action_type}{resource_id}{previous_hash}{audit_entry.timestamp.isoformat()}"
            audit_entry.current_hash = hashlib.sha256(hash_data.encode()).hexdigest()
            
            # Store audit entry
            entry_dict = audit_entry.dict()
            entry_dict = self._prepare_for_mongo(entry_dict)
            
            await self.audit_trail.insert_one(entry_dict)
            
        except Exception as e:
            logger.error(f"Error creating audit entry: {str(e)}")
    
    async def _apply_label_splits(self, royalty_earning: RoyaltyEarning):
        """Apply label splits to royalty earnings based on federated content access"""
        try:
            # Find federated content access for this content
            federated = await self.federated_content.find_one({
                "content_id": royalty_earning.content_id
            })
            
            if federated and federated.get("rights_splits"):
                royalty_earning.label_splits = {}
                for label_id, split_percentage in federated["rights_splits"].items():
                    split_amount = royalty_earning.gross_amount * (split_percentage / 100.0)
                    royalty_earning.label_splits[label_id] = split_amount
            
        except Exception as e:
            logger.error(f"Error applying label splits: {str(e)}")
    
    async def _calculate_deductions(self, label_id: str, amount: float, 
                                  currency: str) -> Dict[str, float]:
        """Calculate tax and fee deductions for payout"""
        try:
            # Get label to determine jurisdiction
            label = await self.get_label_by_id(label_id)
            if not label:
                return {}
            
            jurisdiction = label["metadata_profile"]["jurisdiction"]
            
            # Get jurisdiction rules
            rules = await self.jurisdiction_rules.find_one({"jurisdiction": jurisdiction})
            if not rules:
                return {}
            
            deductions = {}
            
            # Tax deduction
            if rules.get("tax_rate", 0) > 0:
                deductions["income_tax"] = amount * rules["tax_rate"]
            
            # VAT deduction
            if rules.get("vat_rate", 0) > 0:
                deductions["vat"] = amount * rules["vat_rate"]
            
            # Platform fee (2.5% standard)
            deductions["platform_fee"] = amount * 0.025
            
            return deductions
            
        except Exception as e:
            logger.error(f"Error calculating deductions: {str(e)}")
            return {}
    
    async def _generate_directory_stats(self, labels: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics for label directory"""
        try:
            stats = {
                "total_labels": len(labels),
                "major_labels": len([l for l in labels if l.get("label_type") == "major"]),
                "independent_labels": len([l for l in labels if l.get("label_type") == "independent"]),
                "territories_covered": len(set(l["metadata_profile"]["jurisdiction"] for l in labels)),
                "genres_covered": len(set(
                    genre for l in labels 
                    for genre in l["metadata_profile"].get("genre_specialization", [])
                )),
                "blockchain_enabled": len([
                    l for l in labels 
                    if len(l.get("smart_contracts", [])) > 0
                ]),
                "dao_affiliated": len([
                    l for l in labels 
                    if any(sc.get("dao_integration") for sc in l.get("smart_contracts", []))
                ])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating directory stats: {str(e)}")
            return {}
    
    async def _initialize_smart_contracts(self, label_id: str, requirements: Dict[str, Any]):
        """Initialize smart contracts for a label"""
        try:
            # This would integrate with actual blockchain networks
            # For now, create placeholder smart contract bindings
            contract_binding = SmartContractBinding(
                contract_type=ContractType(requirements.get("contract_type", "recording")),
                blockchain_network=requirements.get("network", "ethereum"),
                rights_splits=requirements.get("rights_splits", {}),
                governance_rules=requirements.get("governance_rules", {}),
                dao_integration=requirements.get("dao_integration", False)
            )
            
            # Update label with smart contract
            await self.uln_labels.update_one(
                {"global_id.id": label_id},
                {"$push": {"smart_contracts": self._prepare_for_mongo(contract_binding.dict())}}
            )
            
        except Exception as e:
            logger.error(f"Error initializing smart contracts: {str(e)}")
    
    async def _create_dao_proposal_for_content_sharing(self, request: CrossLabelContentRequest, 
                                                     created_by: str):
        """Create DAO proposal for content sharing approval"""
        try:
            proposal_data = {
                "proposal_type": "content_approval",
                "title": f"Cross-label content sharing for {request.content_id}",
                "description": f"Approve federated access for content {request.content_id} across {len(request.target_labels)} labels",
                "affected_labels": [request.requesting_label_id] + request.target_labels,
                "affected_content": [request.content_id],
                "proposed_changes": {
                    "action": "federated_content_access",
                    "content_id": request.content_id,
                    "access_level": request.access_level,
                    "rights_splits": request.proposed_rights_splits
                },
                "voting_deadline": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            await self.create_dao_proposal(proposal_data, created_by)
            
        except Exception as e:
            logger.error(f"Error creating DAO proposal for content sharing: {str(e)}")
    
    async def _create_dao_proposal_for_royalty_distribution(self, request: RoyaltyDistributionRequest,
                                                          created_by: str):
        """Create DAO proposal for royalty distribution approval"""
        try:
            proposal_data = {
                "proposal_type": "royalty_split_change",
                "title": f"Royalty distribution for period {request.pool_period}",
                "description": f"Approve royalty distribution across {len(request.participating_labels)} labels for {request.pool_period}",
                "affected_labels": request.participating_labels,
                "proposed_changes": {
                    "action": "royalty_distribution",
                    "pool_period": request.pool_period,
                    "distribution_method": request.distribution_method,
                    "override_splits": request.override_splits
                },
                "voting_deadline": (datetime.utcnow() + timedelta(days=5)).isoformat()
            }
            
            await self.create_dao_proposal(proposal_data, created_by)
            
        except Exception as e:
            logger.error(f"Error creating DAO proposal for royalty distribution: {str(e)}")
    
    async def _check_proposal_resolution(self, proposal_id: str):
        """Check if a DAO proposal should be resolved based on votes"""
        try:
            proposal = await self.dao_proposals.find_one({"proposal_id": proposal_id})
            if not proposal or proposal["status"] != "active":
                return
            
            # Calculate vote totals
            total_for = sum(proposal.get("votes_for", {}).values())
            total_against = sum(proposal.get("votes_against", {}).values())
            total_abstain = sum(proposal.get("votes_abstain", {}).values())
            total_votes = total_for + total_against + total_abstain
            
            # Check if threshold met
            if total_votes >= proposal["total_voting_power"] * 0.51:  # 51% participation
                approval_rate = total_for / total_votes if total_votes > 0 else 0
                
                if approval_rate >= proposal["approval_threshold"]:
                    # Proposal passed
                    await self.dao_proposals.update_one(
                        {"proposal_id": proposal_id},
                        {"$set": {
                            "status": "passed",
                            "participation_rate": total_votes / proposal["total_voting_power"],
                            "updated_at": datetime.utcnow().isoformat()
                        }}
                    )
                else:
                    # Proposal rejected
                    await self.dao_proposals.update_one(
                        {"proposal_id": proposal_id},
                        {"$set": {
                            "status": "rejected",
                            "participation_rate": total_votes / proposal["total_voting_power"],
                            "updated_at": datetime.utcnow().isoformat()
                        }}
                    )
                
                # Create audit trail
                await self._create_audit_entry(
                    action_type="dao_proposal_resolved",
                    actor_id="system",
                    actor_type="system",
                    resource_type="dao_proposal",
                    resource_id=proposal_id,
                    action_description=f"DAO proposal {proposal_id} resolved automatically",
                    changes_made={
                        "status": "passed" if approval_rate >= proposal["approval_threshold"] else "rejected",
                        "approval_rate": approval_rate,
                        "participation_rate": total_votes / proposal["total_voting_power"]
                    }
                )
            
        except Exception as e:
            logger.error(f"Error checking proposal resolution: {str(e)}")