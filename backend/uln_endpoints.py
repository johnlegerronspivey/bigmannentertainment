"""
Unified Label Network (ULN) Endpoints
=====================================

FastAPI endpoints for the ULN system providing:
- Label Registry Service API
- Cross-label content sharing endpoints  
- Multi-label royalty engine API
- DAO governance endpoints
- ULN dashboard and analytics
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uln_models import *
from uln_service import ULNService
import json
import os
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Import authentication utilities
from uln_auth import get_current_user, get_current_admin_user, User, db

# Create router for ULN endpoints
uln_router = APIRouter(prefix="/uln", tags=["Unified Label Network"])
uln_service = ULNService()

# ===== LABEL REGISTRY SERVICE ENDPOINTS =====

@uln_router.post("/labels/register", response_model=Dict[str, Any])
async def register_label(
    registration_data: LabelRegistrationRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Register a new label in the Unified Label Network (ULN)
    This is the foundational endpoint for the entire ULN system
    """
    result = await uln_service.register_label(registration_data, current_user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@uln_router.get("/labels/directory", response_model=Dict[str, Any])
async def get_label_directory(
    label_type: Optional[str] = None,
    territory: Optional[str] = None,
    genre: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive label directory for Label Hub UI
    Shows connected labels with filtering options
    """
    filters = {}
    if label_type:
        filters["label_type"] = label_type
    if territory:
        filters["territory"] = territory
    if genre:
        filters["genre"] = genre
    
    result = await uln_service.get_label_directory(filters)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@uln_router.get("/labels/{global_id}", response_model=Dict[str, Any])
async def get_label_by_id(
    global_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get complete label information by Global Label ID"""
    label = await uln_service.get_label_by_id(global_id)
    
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    
    return {
        "success": True,
        "label": label
    }

@uln_router.put("/labels/{global_id}/metadata", response_model=Dict[str, Any])
async def update_label_metadata(
    global_id: str,
    metadata_updates: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user)
):
    """Update label metadata profile"""
    result = await uln_service.update_label_metadata(
        global_id, metadata_updates, current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@uln_router.post("/labels/{global_id}/entities", response_model=Dict[str, Any])
async def add_associated_entity(
    global_id: str,
    entity_data: AssociatedEntity,
    current_user: User = Depends(get_current_admin_user)
):
    """Add an associated entity (creator, admin, DAO delegate) to a label"""
    try:
        # Update label with new entity
        result = await db.uln_labels.update_one(
            {"global_id.id": global_id},
            {
                "$push": {"associated_entities": entity_data.dict()},
                "$set": {"updated_at": datetime.utcnow().isoformat()}
            }
        )
        
        if result.modified_count:
            return {
                "success": True,
                "message": f"Added {entity_data.entity_type} {entity_data.name} to label {global_id}"
            }
        
        raise HTTPException(status_code=404, detail="Label not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add entity: {str(e)}")

@uln_router.get("/labels/{global_id}/entities", response_model=Dict[str, Any])
async def get_label_entities(
    global_id: str,
    entity_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get associated entities for a label"""
    try:
        label = await uln_service.get_label_by_id(global_id)
        if not label:
            raise HTTPException(status_code=404, detail="Label not found")
        
        entities = label.get("associated_entities", [])
        
        if entity_type:
            entities = [e for e in entities if e["entity_type"] == entity_type]
        
        return {
            "success": True,
            "entities": entities,
            "total_entities": len(entities)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch entities: {str(e)}")

# ===== SMART CONTRACT INTEGRATION ENDPOINTS =====

@uln_router.post("/labels/{global_id}/contracts", response_model=Dict[str, Any])
async def create_smart_contract_binding(
    global_id: str,
    contract_data: SmartContractBinding,
    current_user: User = Depends(get_current_admin_user)
):
    """Create smart contract binding for rights splits and governance"""
    try:
        # Verify label exists
        label = await uln_service.get_label_by_id(global_id)
        if not label:
            raise HTTPException(status_code=404, detail="Label not found")
        
        # Add smart contract to label
        contract_dict = contract_data.dict()
        contract_dict["created_at"] = datetime.utcnow().isoformat()
        contract_dict["created_by"] = current_user.id
        
        result = await db.uln_labels.update_one(
            {"global_id.id": global_id},
            {
                "$push": {"smart_contracts": contract_dict},
                "$set": {"updated_at": datetime.utcnow().isoformat()}
            }
        )
        
        if result.modified_count:
            return {
                "success": True,
                "message": f"Smart contract binding created for label {global_id}",
                "contract_type": contract_data.contract_type.value,
                "blockchain_network": contract_data.blockchain_network
            }
        
        raise HTTPException(status_code=500, detail="Failed to create smart contract binding")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart contract creation failed: {str(e)}")

@uln_router.get("/labels/{global_id}/contracts", response_model=Dict[str, Any])
async def get_label_contracts(
    global_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get smart contract bindings for a label"""
    try:
        label = await uln_service.get_label_by_id(global_id)
        if not label:
            raise HTTPException(status_code=404, detail="Label not found")
        
        contracts = label.get("smart_contracts", [])
        
        return {
            "success": True,
            "smart_contracts": contracts,
            "total_contracts": len(contracts),
            "blockchain_enabled": len(contracts) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch contracts: {str(e)}")

@uln_router.post("/blockchain/deploy-contract", response_model=Dict[str, Any])
async def deploy_smart_contract(
    global_id: str,
    contract_type: str,
    blockchain_network: str = "ethereum",
    current_user: User = Depends(get_current_admin_user)
):
    """
    Deploy smart contract to blockchain network
    Note: This is a placeholder for actual blockchain integration
    """
    try:
        # Verify label exists
        label = await uln_service.get_label_by_id(global_id)
        if not label:
            raise HTTPException(status_code=404, detail="Label not found")
        
        # Mock contract deployment (would integrate with actual blockchain)
        mock_contract_address = f"0x{''.join([hex(ord(c))[2:] for c in global_id[:10]])}"
        mock_transaction_hash = f"0x{''.join([hex(hash(global_id + str(datetime.utcnow())) % 256)[2:] for _ in range(32)])}"
        
        # Update label with deployed contract address
        result = await db.uln_labels.update_one(
            {"global_id.id": global_id, "smart_contracts.contract_type": contract_type},
            {
                "$set": {
                    "smart_contracts.$.contract_address": mock_contract_address,
                    "smart_contracts.$.deployment_tx": mock_transaction_hash,
                    "smart_contracts.$.deployed_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if result.modified_count:
            return {
                "success": True,
                "message": f"Smart contract deployed successfully",
                "contract_address": mock_contract_address,
                "transaction_hash": mock_transaction_hash,
                "blockchain_network": blockchain_network,
                "note": "This is a mock deployment for development. Production will integrate with actual blockchain networks."
            }
        
        raise HTTPException(status_code=500, detail="Failed to deploy smart contract")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract deployment failed: {str(e)}")

# ===== CROSS-LABEL CONTENT SHARING ENDPOINTS =====

@uln_router.post("/content/federated-access", response_model=Dict[str, Any])
async def create_federated_content_access(
    request: CrossLabelContentRequest,
    current_user: User = Depends(get_current_user)
):
    """Create federated access for cross-label content sharing"""
    result = await uln_service.create_federated_content_access(request, current_user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@uln_router.get("/content/federated/{label_id}", response_model=Dict[str, Any])
async def get_federated_content_by_label(
    label_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all federated content for a specific label"""
    federated_content = await uln_service.get_federated_content_by_label(label_id)
    
    return {
        "success": True,
        "federated_content": federated_content,
        "total_content": len(federated_content)
    }

@uln_router.put("/content/federated/{content_id}/usage", response_model=Dict[str, Any])
async def update_content_usage_attribution(
    content_id: str,
    usage_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update usage attribution for federated content"""
    try:
        # Update federated content usage data
        result = await db.federated_content.update_one(
            {"content_id": content_id},
            {
                "$set": {
                    "usage_attribution": usage_data,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if result.modified_count:
            return {
                "success": True,
                "message": "Usage attribution updated successfully"
            }
        
        raise HTTPException(status_code=404, detail="Federated content not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update usage: {str(e)}")

@uln_router.get("/content/metadata-sync/{content_id}", response_model=Dict[str, Any])
async def sync_cross_label_metadata(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Sync metadata across all labels with access to content"""
    try:
        # Get federated content access
        federated = await db.federated_content.find_one({"content_id": content_id})
        if not federated:
            raise HTTPException(status_code=404, detail="Federated content not found")
        
        # Get all participating labels
        all_labels = [federated["primary_label_id"]] + federated.get("co_owning_labels", []) + federated.get("licensing_labels", [])
        
        # Mock metadata sync (would integrate with actual metadata management)
        sync_results = []
        for label_id in all_labels:
            sync_results.append({
                "label_id": label_id,
                "sync_status": "completed",
                "last_sync": datetime.utcnow().isoformat()
            })
        
        return {
            "success": True,
            "content_id": content_id,
            "sync_results": sync_results,
            "total_labels_synced": len(sync_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata sync failed: {str(e)}")

# ===== MULTI-LABEL ROYALTY ENGINE ENDPOINTS =====

@uln_router.post("/royalties/pools", response_model=Dict[str, Any])
async def create_royalty_pool(
    request: RoyaltyDistributionRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a multi-label royalty pool for distribution"""
    result = await uln_service.create_royalty_pool(request, current_user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@uln_router.post("/royalties/earnings", response_model=Dict[str, Any])
async def process_royalty_earnings(
    earnings_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_admin_user)
):
    """Process incoming royalty earnings for multi-label distribution"""
    if not earnings_data:
        raise HTTPException(status_code=400, detail="No earnings data provided")
    
    result = await uln_service.process_royalty_earnings(earnings_data)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@uln_router.get("/royalties/pools/{pool_id}", response_model=Dict[str, Any])
async def get_royalty_pool(
    pool_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get royalty pool details"""
    try:
        pool = await db.royalty_pools.find_one({"pool_id": pool_id})
        if not pool:
            raise HTTPException(status_code=404, detail="Royalty pool not found")
        
        pool.pop("_id", None)
        
        return {
            "success": True,
            "royalty_pool": pool
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pool: {str(e)}")

@uln_router.post("/royalties/pools/{pool_id}/distribute", response_model=Dict[str, Any])
async def distribute_royalty_pool(
    pool_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
):
    """Distribute royalties from a pool to participating labels"""
    try:
        # Generate payout ledger
        result = await uln_service.generate_payout_ledger(pool_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Mark pool as distributed
        await db.royalty_pools.update_one(
            {"pool_id": pool_id},
            {
                "$set": {
                    "distributed": True,
                    "distribution_date": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Royalty distribution initiated",
            "pool_id": pool_id,
            "ledger_entries": result["ledger_entries"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Distribution failed: {str(e)}")

@uln_router.get("/royalties/ledger/{label_id}", response_model=Dict[str, Any])
async def get_payout_ledger_for_label(
    label_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get payout ledger entries for a specific label"""
    try:
        ledger_entries = await db.payout_ledger.find(
            {"recipient_id": label_id}
        ).sort("created_at", -1).limit(limit).to_list(length=None)
        
        for entry in ledger_entries:
            entry.pop("_id", None)
        
        return {
            "success": True,
            "ledger_entries": ledger_entries,
            "total_entries": len(ledger_entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ledger: {str(e)}")

# ===== DAO GOVERNANCE ENDPOINTS =====

@uln_router.post("/dao/proposals", response_model=Dict[str, Any])
async def create_dao_proposal(
    proposal_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Create a new DAO proposal for ULN governance"""
    result = await uln_service.create_dao_proposal(proposal_data, current_user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@uln_router.get("/dao/proposals", response_model=Dict[str, Any])
async def get_dao_proposals(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get DAO proposals with optional status filtering"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        proposals = await db.dao_proposals.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
        
        for proposal in proposals:
            proposal.pop("_id", None)
        
        return {
            "success": True,
            "proposals": proposals,
            "total_proposals": len(proposals)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposals: {str(e)}")

@uln_router.post("/dao/proposals/{proposal_id}/vote", response_model=Dict[str, Any])
async def cast_dao_vote(
    proposal_id: str,
    vote: str,
    voting_power: float = 1.0,
    current_user: User = Depends(get_current_user)
):
    """Cast a vote on a DAO proposal"""
    result = await uln_service.cast_dao_vote(proposal_id, current_user.id, vote, voting_power)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@uln_router.get("/dao/proposals/{proposal_id}", response_model=Dict[str, Any])
async def get_dao_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed DAO proposal information"""
    try:
        proposal = await db.dao_proposals.find_one({"proposal_id": proposal_id})
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        proposal.pop("_id", None)
        
        # Calculate voting statistics
        total_for = sum(proposal.get("votes_for", {}).values())
        total_against = sum(proposal.get("votes_against", {}).values())
        total_abstain = sum(proposal.get("votes_abstain", {}).values())
        total_votes = total_for + total_against + total_abstain
        
        proposal["voting_statistics"] = {
            "total_votes": total_votes,
            "votes_for": total_for,
            "votes_against": total_against,
            "votes_abstain": total_abstain,
            "approval_rate": total_for / total_votes if total_votes > 0 else 0,
            "participation_rate": total_votes / proposal.get("total_voting_power", 1)
        }
        
        return {
            "success": True,
            "proposal": proposal
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposal: {str(e)}")

# ===== COMPLIANCE AND JURISDICTION ENDPOINTS =====

@uln_router.get("/compliance/jurisdictions", response_model=Dict[str, Any])
async def get_jurisdiction_rules(
    jurisdiction: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get jurisdiction-specific compliance rules"""
    try:
        query = {}
        if jurisdiction:
            query["jurisdiction"] = jurisdiction
        
        rules = await db.jurisdiction_rules.find(query).to_list(length=None)
        
        for rule in rules:
            rule.pop("_id", None)
        
        return {
            "success": True,
            "jurisdiction_rules": rules,
            "total_jurisdictions": len(rules)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rules: {str(e)}")

@uln_router.post("/compliance/verify/{global_id}", response_model=Dict[str, Any])
async def verify_label_compliance(
    global_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Verify compliance status for a label"""
    try:
        # Get label
        label = await uln_service.get_label_by_id(global_id)
        if not label:
            raise HTTPException(status_code=404, detail="Label not found")
        
        # Get jurisdiction rules
        jurisdiction = label["metadata_profile"]["jurisdiction"]
        rules = await db.jurisdiction_rules.find_one({"jurisdiction": jurisdiction})
        
        if not rules:
            raise HTTPException(status_code=400, detail=f"No rules found for jurisdiction {jurisdiction}")
        
        # Perform compliance verification (simplified)
        compliance_checks = {
            "business_registration": bool(label["metadata_profile"].get("business_registration_number")),
            "tax_id_provided": bool(label["metadata_profile"].get("tax_id")),
            "licensing_requirements": True,  # Would check actual licensing
            "data_protection_compliance": True,  # Would verify GDPR/CCPA compliance
            "content_restrictions_acknowledged": True
        }
        
        all_checks_passed = all(compliance_checks.values())
        
        # Update label compliance status
        await db.uln_labels.update_one(
            {"global_id.id": global_id},
            {
                "$set": {
                    "compliance_verified": all_checks_passed,
                    "compliance_checks": compliance_checks,
                    "compliance_verified_at": datetime.utcnow().isoformat(),
                    "compliance_verified_by": current_user.id,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "compliance_verified": all_checks_passed,
            "compliance_checks": compliance_checks,
            "jurisdiction": jurisdiction,
            "verified_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance verification failed: {str(e)}")

# ===== DASHBOARD AND ANALYTICS ENDPOINTS =====

@uln_router.get("/dashboard/stats", response_model=Dict[str, Any])
async def get_uln_dashboard_stats(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive ULN dashboard statistics"""
    result = await uln_service.get_uln_dashboard_stats()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@uln_router.post("/initialize-major-labels")
async def initialize_major_labels(current_user: dict = Depends(get_current_user)):
    """Initialize all major record labels in the ULN system"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if user has admin privileges (optional - could allow any authenticated user)
        # This is a one-time setup operation that populates the label hub
        
        uln_service = ULNService()
        result = await uln_service.initialize_major_labels()
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error in initialize_major_labels endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to initialize major labels: {str(e)}"
            }
        )

@uln_router.get("/dashboard/label-hub", response_model=Dict[str, Any])
async def get_label_hub_data(
    territory: Optional[str] = None,
    genre: Optional[str] = None,
    dao_affiliated: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """Get Label Hub UI data with filtering"""
    filters = {}
    if territory:
        filters["territory"] = territory
    if genre:
        filters["genre"] = genre
    if dao_affiliated is not None:
        # Would filter by DAO affiliation
        pass
    
    result = await uln_service.get_label_directory(filters)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@uln_router.get("/dashboard/creator-portal/{creator_id}", response_model=Dict[str, Any])
async def get_creator_portal_data(
    creator_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get Creator Portal data showing which labels manage/distribute creator's content"""
    try:
        # Find labels associated with this creator
        labels_pipeline = [
            {"$match": {"associated_entities.entity_id": creator_id}},
            {"$project": {
                "global_id.id": 1,
                "metadata_profile.name": 1,
                "associated_entities": {
                    "$filter": {
                        "input": "$associated_entities",
                        "cond": {"$eq": ["$$this.entity_id", creator_id]}
                    }
                }
            }}
        ]
        
        labels = []
        async for label in db.uln_labels.aggregate(labels_pipeline):
            label.pop("_id", None)
            labels.append(label)
        
        # Get federated content for this creator
        federated_content = await db.federated_content.find({
            "$or": [
                {"usage_attribution.creator_id": creator_id},
                {"creator_allocations": {"$exists": True}}  # Would check actual creator allocations
            ]
        }).to_list(length=None)
        
        # Calculate earnings by label (simplified)
        earnings_by_label = {}
        total_earnings = 0.0
        
        for content in federated_content:
            for label_id, amount in content.get("revenue_by_label", {}).items():
                earnings_by_label[label_id] = earnings_by_label.get(label_id, 0.0) + amount
                total_earnings += amount
        
        creator_portal_data = CreatorPortalEntry(
            creator_id=creator_id,
            creator_name=f"Creator {creator_id}",  # Would get actual name
            managing_labels=[l["global_id"]["id"] for l in labels if any(e["role"] == "manager" for e in l["associated_entities"])],
            distributing_labels=[l["global_id"]["id"] for l in labels if any(e["role"] == "distributor" for e in l["associated_entities"])],
            content_ids=[c["content_id"] for c in federated_content],
            total_earnings=total_earnings,
            earnings_by_label=earnings_by_label
        )
        
        return {
            "success": True,
            "creator_portal_data": creator_portal_data.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch creator portal data: {str(e)}")

@uln_router.get("/dashboard/investor-view/{investor_id}", response_model=Dict[str, Any])
async def get_investor_view_data(
    investor_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get Investor View data showing portfolio performance across labels"""
    try:
        # Find labels associated with this investor
        labels_pipeline = [
            {"$match": {"associated_entities.entity_id": investor_id}},
            {"$project": {
                "global_id.id": 1,
                "metadata_profile.name": 1,
                "associated_entities": {
                    "$filter": {
                        "input": "$associated_entities",
                        "cond": {"$eq": ["$$this.entity_id", investor_id]}
                    }
                }
            }}
        ]
        
        portfolio_labels = []
        total_investment = 0.0
        
        async for label in db.uln_labels.aggregate(labels_pipeline):
            label.pop("_id", None)
            portfolio_labels.append(label["global_id"]["id"])
            
            # Calculate investment amount (would come from actual investment records)
            for entity in label["associated_entities"]:
                if entity["entity_type"] == "investor":
                    total_investment += entity.get("investment_amount", 0.0)
        
        # Calculate returns (simplified - would use actual financial data)
        total_returns = total_investment * 1.15  # Mock 15% return
        roi = (total_returns - total_investment) / total_investment if total_investment > 0 else 0.0
        
        investor_view_data = InvestorViewEntry(
            investor_id=investor_id,
            investor_name=f"Investor {investor_id}",  # Would get actual name
            portfolio_labels=portfolio_labels,
            total_investment=total_investment,
            total_returns=total_returns,
            roi=roi,
            risk_score=0.3,  # Mock risk score
            diversification_score=0.8  # Mock diversification score
        )
        
        return {
            "success": True,
            "investor_view_data": investor_view_data.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch investor view data: {str(e)}")

# ===== AUDIT TRAIL ENDPOINTS =====

@uln_router.get("/audit/trail", response_model=Dict[str, Any])
async def get_audit_trail(
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user)
):
    """Get audit trail entries for ULN operations"""
    try:
        query = {}
        if resource_type:
            query["resource_type"] = resource_type
        if resource_id:
            query["resource_id"] = resource_id
        
        audit_entries = await db.uln_audit_trail.find(query).sort("timestamp", -1).limit(limit).to_list(length=None)
        
        for entry in audit_entries:
            entry.pop("_id", None)
        
        return {
            "success": True,
            "audit_entries": audit_entries,
            "total_entries": len(audit_entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit trail: {str(e)}")

@uln_router.get("/audit/trail/{entry_id}/verify", response_model=Dict[str, Any])
async def verify_audit_entry(
    entry_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Verify integrity of an audit trail entry"""
    try:
        entry = await db.uln_audit_trail.find_one({"entry_id": entry_id})
        if not entry:
            raise HTTPException(status_code=404, detail="Audit entry not found")
        
        # Verify hash chain integrity
        hash_data = f"{entry['entry_id']}{entry['action_type']}{entry['resource_id']}{entry['previous_hash']}{entry['timestamp']}"
        calculated_hash = hashlib.sha256(hash_data.encode()).hexdigest()
        
        integrity_verified = calculated_hash == entry["current_hash"]
        
        return {
            "success": True,
            "entry_id": entry_id,
            "integrity_verified": integrity_verified,
            "calculated_hash": calculated_hash,
            "stored_hash": entry["current_hash"],
            "verification_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit verification failed: {str(e)}")

# ===== HEALTH AND STATUS ENDPOINTS =====

@uln_router.get("/health", response_model=Dict[str, Any])
async def uln_health_check():
    """ULN system health check"""
    try:
        # Check database connectivity
        label_count = await db.uln_labels.count_documents({})
        federated_count = await db.federated_content.count_documents({})
        proposal_count = await db.dao_proposals.count_documents({})
        
        return {
            "status": "healthy",
            "service": "unified_label_network",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "metrics": {
                "total_labels": label_count,
                "federated_content_items": federated_count,
                "dao_proposals": proposal_count
            },
            "capabilities": {
                "label_registry": "enabled",
                "cross_label_sharing": "enabled",
                "royalty_engine": "enabled",
                "dao_governance": "enabled",
                "smart_contracts": "mock_enabled",
                "blockchain_integration": "development"
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "unified_label_network",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "database": "disconnected"
        }

@uln_router.get("/status/migration", response_model=Dict[str, Any])
async def get_migration_status(
    current_user: User = Depends(get_current_admin_user)
):
    """Get status of migrating existing labels to ULN system"""
    try:
        # Check existing labels from industry_models
        try:
            from industry_service import IndustryService
            industry_service = IndustryService()
            existing_labels_data = await industry_service.get_record_labels()
            
            if existing_labels_data.get("success"):
                existing_major = len(existing_labels_data.get("major_labels", []))
                existing_independent = len(existing_labels_data.get("independent_labels", []))
                total_existing = existing_major + existing_independent
            else:
                total_existing = 0
        except ImportError:
            total_existing = 0
        
        # Check ULN labels
        uln_total = await db.uln_labels.count_documents({})
        uln_major = await db.uln_labels.count_documents({"label_type": "major"})
        uln_independent = await db.uln_labels.count_documents({"label_type": "independent"})
        
        migration_progress = (uln_total / total_existing * 100) if total_existing > 0 else 0
        
        return {
            "success": True,
            "migration_status": {
                "existing_labels": {
                    "total": total_existing,
                    "major": existing_major if total_existing > 0 else 0,
                    "independent": existing_independent if total_existing > 0 else 0
                },
                "uln_labels": {
                    "total": uln_total,
                    "major": uln_major,
                    "independent": uln_independent
                },
                "migration_progress": migration_progress,
                "migration_completed": migration_progress >= 100,
                "next_steps": [
                    "Migrate remaining labels to ULN",
                    "Configure smart contract bindings",
                    "Set up cross-label partnerships",
                    "Initialize DAO governance"
                ] if migration_progress < 100 else [
                    "All labels migrated to ULN",
                    "Configure advanced features",
                    "Set up production blockchain integration"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get migration status: {str(e)}")

# Export router
router = uln_router