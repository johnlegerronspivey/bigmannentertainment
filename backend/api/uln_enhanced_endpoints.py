"""
ULN Enhanced Endpoints
======================
API endpoints for all new ULN features:
- Real blockchain ledger
- Live royalty data & analytics
- Label onboarding workflow
- Inter-label messaging
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from uln_auth import get_current_user, get_current_admin_user, User
from uln_blockchain_service import ULNBlockchainService
from uln_analytics_service import ULNAnalyticsService
from uln_messaging_service import ULNMessagingService
from uln_onboarding_service import ULNOnboardingService

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uln-enhanced", tags=["ULN Enhanced"])

blockchain_svc = ULNBlockchainService()
analytics_svc = ULNAnalyticsService()
messaging_svc = ULNMessagingService()
onboarding_svc = ULNOnboardingService()


# ───── Request models ─────

class TransactionRequest(BaseModel):
    tx_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class DeployContractRequest(BaseModel):
    contract_type: str
    label_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ExecuteContractRequest(BaseModel):
    contract_id: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)

class CreateThreadRequest(BaseModel):
    sender_label_id: str
    recipient_label_id: str
    subject: str

class SendMessageRequest(BaseModel):
    thread_id: str
    sender_label_id: str
    sender_name: str
    content: str

class OnboardingStepRequest(BaseModel):
    step: int
    data: Dict[str, Any] = Field(default_factory=dict)


# ══════════════════════════════════════════════
# BLOCKCHAIN LEDGER
# ══════════════════════════════════════════════

@router.get("/blockchain/stats")
async def blockchain_stats(current_user: User = Depends(get_current_user)):
    """Get blockchain chain statistics."""
    stats = await blockchain_svc.get_chain_stats()
    return {"success": True, **stats}

@router.get("/blockchain/blocks")
async def get_blocks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Get blocks from the chain."""
    return await blockchain_svc.get_blocks(limit, offset)

@router.get("/blockchain/blocks/{index}")
async def get_block(index: int, current_user: User = Depends(get_current_user)):
    """Get a specific block by index."""
    block = await blockchain_svc.get_block(index)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"success": True, "block": block}

@router.get("/blockchain/transactions")
async def get_transactions(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    """Get transactions, optionally filtered by status."""
    txs = await blockchain_svc.get_transactions(status, limit)
    return {"success": True, "transactions": txs, "count": len(txs)}

@router.post("/blockchain/transactions")
async def add_transaction(req: TransactionRequest, current_user: User = Depends(get_current_user)):
    """Add a new transaction to the mempool."""
    tx = await blockchain_svc.add_transaction(req.tx_type, req.payload, current_user.id)
    return {"success": True, "transaction": tx}

@router.post("/blockchain/mine")
async def mine_block(current_user: User = Depends(get_current_admin_user)):
    """Mine pending transactions into a new block."""
    result = await blockchain_svc.mine_pending_block()
    return result

@router.get("/blockchain/verify")
async def verify_chain(current_user: User = Depends(get_current_admin_user)):
    """Verify the integrity of the entire blockchain."""
    result = await blockchain_svc.verify_chain()
    return {"success": True, **result}

@router.post("/blockchain/contracts/deploy")
async def deploy_contract(req: DeployContractRequest, current_user: User = Depends(get_current_admin_user)):
    """Deploy a new smart contract."""
    result = await blockchain_svc.deploy_contract(req.contract_type, req.label_id, req.parameters, current_user.id)
    return result

@router.post("/blockchain/contracts/execute")
async def execute_contract(req: ExecuteContractRequest, current_user: User = Depends(get_current_admin_user)):
    """Execute an action on a deployed smart contract."""
    result = await blockchain_svc.execute_contract(req.contract_id, req.action, req.params, current_user.id)
    return result

@router.get("/blockchain/contracts")
async def get_contracts(
    label_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Get deployed smart contracts."""
    contracts = await blockchain_svc.get_contracts(label_id)
    return {"success": True, "contracts": contracts, "count": len(contracts)}


# ══════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════

@router.get("/analytics/cross-label-performance")
async def cross_label_performance(current_user: User = Depends(get_current_user)):
    """Get cross-label performance comparison."""
    return await analytics_svc.get_cross_label_performance()

@router.get("/analytics/revenue-trends")
async def revenue_trends(months: int = Query(12, ge=1, le=36), current_user: User = Depends(get_current_user)):
    """Get monthly revenue trends."""
    return await analytics_svc.get_revenue_trends(months)

@router.get("/analytics/genre-breakdown")
async def genre_breakdown(current_user: User = Depends(get_current_user)):
    """Get label distribution by genre."""
    return await analytics_svc.get_genre_breakdown()

@router.get("/analytics/territory-breakdown")
async def territory_breakdown(current_user: User = Depends(get_current_user)):
    """Get label distribution by territory."""
    return await analytics_svc.get_territory_breakdown()

@router.get("/analytics/content-sharing")
async def content_sharing_analytics(current_user: User = Depends(get_current_user)):
    """Get content sharing analytics."""
    return await analytics_svc.get_content_sharing_analytics()

@router.get("/analytics/dao")
async def dao_analytics(current_user: User = Depends(get_current_user)):
    """Get DAO governance analytics."""
    return await analytics_svc.get_dao_analytics()

@router.post("/analytics/seed-royalties")
async def seed_royalties(current_user: User = Depends(get_current_admin_user)):
    """Seed sample royalty data for dashboards."""
    return await analytics_svc.seed_sample_royalties()


# ══════════════════════════════════════════════
# INTER-LABEL MESSAGING
# ══════════════════════════════════════════════

@router.post("/messaging/threads")
async def create_thread(req: CreateThreadRequest, current_user: User = Depends(get_current_user)):
    """Create a new messaging thread between two labels."""
    return await messaging_svc.create_thread(req.sender_label_id, req.recipient_label_id, req.subject, current_user.id)

@router.get("/messaging/threads")
async def get_threads(label_id: str = Query(...), current_user: User = Depends(get_current_user)):
    """Get all threads for a label."""
    threads = await messaging_svc.get_threads(label_id)
    return {"success": True, "threads": threads, "count": len(threads)}

@router.get("/messaging/threads/{thread_id}")
async def get_thread_messages(
    thread_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Get messages in a thread."""
    return await messaging_svc.get_messages(thread_id, limit, offset)

@router.post("/messaging/messages")
async def send_message(req: SendMessageRequest, current_user: User = Depends(get_current_user)):
    """Send a message in a thread."""
    return await messaging_svc.send_message(req.thread_id, req.sender_label_id, req.sender_name, req.content)

@router.put("/messaging/threads/{thread_id}/read")
async def mark_thread_read(thread_id: str, label_id: str = Query(...), current_user: User = Depends(get_current_user)):
    """Mark all messages in a thread as read."""
    return await messaging_svc.mark_read(thread_id, label_id)

@router.get("/messaging/summary")
async def messaging_summary(current_user: User = Depends(get_current_admin_user)):
    """Admin view of all messaging activity."""
    return await messaging_svc.get_all_threads_summary()


# ══════════════════════════════════════════════
# LABEL ONBOARDING
# ══════════════════════════════════════════════

@router.post("/onboarding/start")
async def start_onboarding(current_user: User = Depends(get_current_user)):
    """Start a new label onboarding session."""
    return await onboarding_svc.start_onboarding(current_user.id)

@router.get("/onboarding/{session_id}")
async def get_onboarding_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Get current onboarding session state."""
    session = await onboarding_svc.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "session": session}

@router.post("/onboarding/{session_id}/step")
async def save_onboarding_step(session_id: str, req: OnboardingStepRequest, current_user: User = Depends(get_current_user)):
    """Save data for a specific onboarding step."""
    return await onboarding_svc.save_step(session_id, req.step, req.data)

@router.post("/onboarding/{session_id}/complete")
async def complete_onboarding(session_id: str, current_user: User = Depends(get_current_user)):
    """Complete onboarding and get registration payload."""
    return await onboarding_svc.complete_onboarding(session_id)

@router.get("/onboarding/user/sessions")
async def get_user_sessions(current_user: User = Depends(get_current_user)):
    """Get all onboarding sessions for current user."""
    sessions = await onboarding_svc.get_user_sessions(current_user.id)
    return {"success": True, "sessions": sessions}
