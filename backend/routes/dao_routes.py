"""DAO and Smart Contract endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter
from config.database import db
from dao_smart_contracts import dao_contract_manager

router = APIRouter(tags=["DAO"])

# DAO and Smart Contract endpoints
@router.get("/dao/contracts")
async def get_dao_contracts():
    """Get all DAO smart contracts"""
    try:
        contracts = dao_contract_manager.get_smart_contracts()
        
        return {
            "success": True,
            "contracts": contracts,
            "total_count": len(contracts),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/dao/governance")
async def dao_governance_action(request: dict):
    """Handle DAO governance actions (create proposal, vote, execute)"""
    try:
        action_type = request.get("action_type")
        
        if action_type == "create_proposal":
            description = request.get("description", "")
            target_address = request.get("target_address")
            call_data = request.get("call_data", "").encode() if request.get("call_data") else b''
            
            proposal = await dao_contract_manager.create_proposal(description, target_address, call_data)
            
            return {
                "success": True,
                "proposal": proposal,
                "action": "proposal_created",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        elif action_type == "vote":
            proposal_id = request.get("proposal_id")
            support = request.get("support", True)
            voter_address = request.get("voter_address", "0x" + "1" * 40)
            
            vote = await dao_contract_manager.vote_on_proposal(proposal_id, support, voter_address)
            
            return {
                "success": True,
                "vote": vote,
                "action": "vote_cast",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        elif action_type == "execute":
            proposal_id = request.get("proposal_id")
            
            execution = await dao_contract_manager.execute_proposal(proposal_id)
            
            return {
                "success": True,
                "execution": execution,
                "action": "proposal_executed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        else:
            return {
                "success": False,
                "error": "Invalid action_type. Supported: create_proposal, vote, execute",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/dao/disputes") 
async def get_dao_disputes():
    """Get all DAO disputes"""
    try:
        proposals = await dao_contract_manager.get_all_proposals()
        
        # Filter disputes (proposals related to content removal, licensing disputes, etc.)
        disputes = [p for p in proposals if any(keyword in p.get('description', '').lower() 
                   for keyword in ['dispute', 'removal', 'copyright', 'licensing'])]
        
        return {
            "success": True,
            "disputes": disputes,
            "total_count": len(disputes),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/dao/stats")
async def get_dao_stats():
    """Get DAO statistics"""
    try:
        stats = dao_contract_manager.get_dao_stats()
        
        return {
            "success": True,
            "dao_stats": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/dao/health")
async def dao_health():
    """DAO service health check"""
    try:
        stats = dao_contract_manager.get_dao_stats()
        
        return {
            "status": "healthy",
            "service": "dao_governance",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_network": stats.get("network", "mock"),
            "contract_address": stats.get("contract_address"),
            "token_address": stats.get("token_address"),
            "metrics": {
                "total_proposals": stats.get("total_proposals", 0),
                "active_proposals": stats.get("active_proposals", 0),
                "total_token_holders": stats.get("total_token_holders", 0),
                "participation_rate": stats.get("governance_participation_rate", 0)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "service": "dao_governance",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

# Payment & Financial Services Endpoints

