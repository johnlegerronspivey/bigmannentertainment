"""Amazon Managed Blockchain routes - Blockchain network management."""
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from auth.service import get_current_user
from models.core import User

router = APIRouter(prefix="/aws-blockchain", tags=["AWS Managed Blockchain"])
logger = logging.getLogger(__name__)

_bc_svc = None


def _blockchain():
    global _bc_svc
    if _bc_svc is None:
        from services.managed_blockchain_service import ManagedBlockchainService
        _bc_svc = ManagedBlockchainService()
    return _bc_svc


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def blockchain_status(current_user: User = Depends(get_current_user)):
    """Overall status of Managed Blockchain."""
    bc = _blockchain()
    return {"managed_blockchain": bc.get_status()}


# ══════════════════════════════════════════════════════════════════
#  NETWORKS
# ══════════════════════════════════════════════════════════════════
@router.get("/networks")
async def list_networks(current_user: User = Depends(get_current_user)):
    """List blockchain networks."""
    bc = _blockchain()
    if not bc.available:
        raise HTTPException(503, "Managed Blockchain not available")
    try:
        networks = bc.list_networks()
        return {"networks": networks, "total": len(networks)}
    except Exception as e:
        logger.error(f"List networks error: {e}")
        raise HTTPException(500, f"Failed to list networks: {str(e)}")


@router.get("/networks/{network_id}")
async def get_network(
    network_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get network details."""
    bc = _blockchain()
    if not bc.available:
        raise HTTPException(503, "Managed Blockchain not available")
    try:
        return bc.get_network(network_id)
    except Exception as e:
        raise HTTPException(404, f"Network not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  MEMBERS
# ══════════════════════════════════════════════════════════════════
@router.get("/networks/{network_id}/members")
async def list_members(
    network_id: str,
    current_user: User = Depends(get_current_user),
):
    """List network members."""
    bc = _blockchain()
    if not bc.available:
        raise HTTPException(503, "Managed Blockchain not available")
    try:
        members = bc.list_members(network_id)
        return {"members": members, "total": len(members)}
    except Exception as e:
        logger.error(f"List members error: {e}")
        raise HTTPException(500, f"Failed to list members: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  NODES
# ══════════════════════════════════════════════════════════════════
@router.get("/networks/{network_id}/members/{member_id}/nodes")
async def list_nodes(
    network_id: str,
    member_id: str,
    current_user: User = Depends(get_current_user),
):
    """List nodes for a member."""
    bc = _blockchain()
    if not bc.available:
        raise HTTPException(503, "Managed Blockchain not available")
    try:
        nodes = bc.list_nodes(network_id, member_id)
        return {"nodes": nodes, "total": len(nodes)}
    except Exception as e:
        logger.error(f"List nodes error: {e}")
        raise HTTPException(500, f"Failed to list nodes: {str(e)}")


@router.get("/networks/{network_id}/members/{member_id}/nodes/{node_id}")
async def get_node(
    network_id: str,
    member_id: str,
    node_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get node details."""
    bc = _blockchain()
    if not bc.available:
        raise HTTPException(503, "Managed Blockchain not available")
    try:
        return bc.get_node(network_id, member_id, node_id)
    except Exception as e:
        raise HTTPException(404, f"Node not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  PROPOSALS
# ══════════════════════════════════════════════════════════════════
@router.get("/networks/{network_id}/proposals")
async def list_proposals(
    network_id: str,
    current_user: User = Depends(get_current_user),
):
    """List proposals for a network."""
    bc = _blockchain()
    if not bc.available:
        raise HTTPException(503, "Managed Blockchain not available")
    try:
        proposals = bc.list_proposals(network_id)
        return {"proposals": proposals, "total": len(proposals)}
    except Exception as e:
        logger.error(f"List proposals error: {e}")
        raise HTTPException(500, f"Failed to list proposals: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  ACCESSORS
# ══════════════════════════════════════════════════════════════════
@router.get("/accessors")
async def list_accessors(current_user: User = Depends(get_current_user)):
    """List blockchain accessors (token-based access)."""
    bc = _blockchain()
    if not bc.available:
        raise HTTPException(503, "Managed Blockchain not available")
    try:
        accessors = bc.list_accessors()
        return {"accessors": accessors, "total": len(accessors)}
    except Exception as e:
        logger.error(f"List accessors error: {e}")
        raise HTTPException(500, f"Failed to list accessors: {str(e)}")
