"""
Big Mann Entertainment - DAO 2.0 Governance API Endpoints
RESTful API for advanced DAO governance with multi-chain support
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging

from dao_governance_v2_models import (
    NetworkType, ProposalState, ProposalCategory, VoteOption,
    CreateProposalRequest, CastVoteRequest, DelegateVotesRequest
)
from dao_governance_v2_service import dao_governance_v2_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dao-v2", tags=["DAO Governance V2"])


# ============== HEALTH CHECK ==============

@router.get("/health")
async def dao_v2_health():
    """Health check for DAO V2 service"""
    return {
        "status": "healthy",
        "service": "DAO Governance V2",
        "version": "2.0",
        "features": [
            "Token-based weighted voting",
            "Multi-chain support (Ethereum + Polygon)",
            "On-chain/off-chain hybrid governance",
            "Treasury management",
            "Member roles & delegation"
        ]
    }


# ============== PROPOSALS ==============

@router.get("/proposals")
async def get_proposals(
    user_id: Optional[str] = Query(None),
    state: Optional[ProposalState] = Query(None),
    category: Optional[ProposalCategory] = Query(None),
    network: Optional[NetworkType] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get governance proposals with filters"""
    try:
        result = await dao_governance_v2_service.get_proposals(
            user_id=user_id,
            state=state,
            category=category,
            network=network,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_proposals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get a single proposal by ID"""
    try:
        result = await dao_governance_v2_service.get_proposal(proposal_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Proposal not found"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proposals")
async def create_proposal(
    request: CreateProposalRequest,
    user_id: str = Query(...),
    wallet_address: str = Query(...)
):
    """Create a new governance proposal"""
    try:
        result = await dao_governance_v2_service.create_proposal(
            request=request,
            user_id=user_id,
            wallet_address=wallet_address
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create proposal"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}/votes")
async def get_proposal_votes(
    proposal_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get votes for a specific proposal"""
    try:
        result = await dao_governance_v2_service.get_proposal_votes(
            proposal_id=proposal_id,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_proposal_votes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== VOTING ==============

@router.post("/vote")
async def cast_vote(
    request: CastVoteRequest,
    user_id: str = Query(...),
    wallet_address: str = Query(...)
):
    """Cast a vote on a proposal"""
    try:
        result = await dao_governance_v2_service.cast_vote(
            request=request,
            user_id=user_id,
            wallet_address=wallet_address
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to cast vote"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cast_vote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== MEMBERS ==============

@router.get("/members/me")
async def get_my_profile(
    user_id: str = Query(...),
    wallet_address: Optional[str] = Query(None)
):
    """Get current user's DAO member profile"""
    try:
        result = await dao_governance_v2_service.get_member_profile(
            user_id=user_id,
            wallet_address=wallet_address
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_my_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/members/{member_id}")
async def get_member_profile(member_id: str):
    """Get a specific member's profile"""
    try:
        result = await dao_governance_v2_service.get_member_profile(user_id=member_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_member_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== DELEGATION ==============

@router.post("/delegate")
async def delegate_votes(
    request: DelegateVotesRequest,
    user_id: str = Query(...),
    wallet_address: str = Query(...)
):
    """Delegate voting power to another address"""
    try:
        result = await dao_governance_v2_service.delegate_votes(
            request=request,
            user_id=user_id,
            wallet_address=wallet_address
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delegate votes"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delegate_votes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/delegates")
async def get_delegates(network: Optional[NetworkType] = Query(None)):
    """Get list of available delegates"""
    try:
        result = await dao_governance_v2_service.get_delegates(network=network)
        return result
    except Exception as e:
        logger.error(f"Error in get_delegates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== TREASURY ==============

@router.get("/treasury")
async def get_treasury(network: Optional[NetworkType] = Query(None)):
    """Get treasury information"""
    try:
        result = await dao_governance_v2_service.get_treasury(network=network)
        return result
    except Exception as e:
        logger.error(f"Error in get_treasury: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== GOVERNANCE ==============

@router.get("/metrics")
async def get_governance_metrics():
    """Get comprehensive governance metrics"""
    try:
        result = await dao_governance_v2_service.get_governance_metrics()
        return result
    except Exception as e:
        logger.error(f"Error in get_governance_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_governance_config():
    """Get governance configuration"""
    try:
        result = await dao_governance_v2_service.get_governance_config()
        return result
    except Exception as e:
        logger.error(f"Error in get_governance_config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/council")
async def get_council_members():
    """Get DAO Council members"""
    try:
        result = await dao_governance_v2_service.get_council_members()
        return result
    except Exception as e:
        logger.error(f"Error in get_council_members: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== NETWORKS ==============

@router.get("/networks")
async def get_supported_networks():
    """Get supported blockchain networks"""
    return {
        "success": True,
        "networks": [
            {
                "id": "ethereum",
                "name": "Ethereum Mainnet",
                "chain_id": 1,
                "symbol": "ETH",
                "explorer": "https://etherscan.io",
                "rpc": "https://mainnet.infura.io/v3/",
                "is_primary": True
            },
            {
                "id": "polygon",
                "name": "Polygon",
                "chain_id": 137,
                "symbol": "MATIC",
                "explorer": "https://polygonscan.com",
                "rpc": "https://polygon-rpc.com",
                "is_primary": False
            },
            {
                "id": "ethereum_sepolia",
                "name": "Ethereum Sepolia (Testnet)",
                "chain_id": 11155111,
                "symbol": "ETH",
                "explorer": "https://sepolia.etherscan.io",
                "rpc": "https://sepolia.infura.io/v3/",
                "is_testnet": True
            },
            {
                "id": "polygon_mumbai",
                "name": "Polygon Mumbai (Testnet)",
                "chain_id": 80001,
                "symbol": "MATIC",
                "explorer": "https://mumbai.polygonscan.com",
                "rpc": "https://rpc-mumbai.maticvigil.com",
                "is_testnet": True
            }
        ]
    }
