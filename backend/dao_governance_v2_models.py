"""
Big Mann Entertainment - DAO 2.0 Governance Models
Advanced DAO governance with multi-chain support (Ethereum + Polygon)
Token-based weighted voting, Treasury management, Member roles
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============== ENUMS ==============

class NetworkType(str, Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"
    POLYGON_MUMBAI = "polygon_mumbai"


class GovernanceType(str, Enum):
    """Type of governance mechanism"""
    ON_CHAIN = "on_chain"  # Votes recorded on blockchain
    OFF_CHAIN = "off_chain"  # Votes recorded in database (Snapshot-like)
    HYBRID = "hybrid"  # Critical votes on-chain, others off-chain


class ProposalCategory(str, Enum):
    """Categories of proposals"""
    TREASURY_ALLOCATION = "treasury_allocation"
    REVENUE_DISTRIBUTION = "revenue_distribution"
    PLATFORM_UPGRADE = "platform_upgrade"
    POLICY_CHANGE = "policy_change"
    PARTNERSHIP = "partnership"
    GOVERNANCE_CHANGE = "governance_change"
    EMERGENCY_ACTION = "emergency_action"
    FEATURE_REQUEST = "feature_request"
    CONTRACT_UPGRADE = "contract_upgrade"
    TOKEN_DISTRIBUTION = "token_distribution"


class ProposalState(str, Enum):
    """States of a proposal lifecycle"""
    DRAFT = "draft"
    PENDING = "pending"  # Waiting for voting period
    ACTIVE = "active"  # Voting in progress
    CANCELED = "canceled"
    DEFEATED = "defeated"
    SUCCEEDED = "succeeded"
    QUEUED = "queued"  # In timelock
    EXPIRED = "expired"
    EXECUTED = "executed"


class VoteOption(str, Enum):
    """Voting options"""
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


class MemberRole(str, Enum):
    """DAO member governance roles"""
    OBSERVER = "observer"  # Can view, no voting
    MEMBER = "member"  # Standard voting rights
    DELEGATE = "delegate"  # Can receive delegated votes
    COUNCIL = "council"  # Council member with elevated privileges
    GUARDIAN = "guardian"  # Emergency actions
    ADMIN = "admin"  # Full administrative access


class TreasuryAssetType(str, Enum):
    """Types of treasury assets"""
    NATIVE = "native"  # ETH, MATIC
    ERC20 = "erc20"
    ERC721 = "erc721"
    STABLECOIN = "stablecoin"


class TransactionType(str, Enum):
    """Types of treasury transactions"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SWAP = "swap"
    STAKE = "stake"
    UNSTAKE = "unstake"
    REWARD = "reward"
    GOVERNANCE_ALLOCATION = "governance_allocation"


# ============== BASE MODELS ==============

class GovernanceToken(BaseModel):
    """ERC-20 Governance Token Model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    symbol: str
    contract_address: str
    network: NetworkType
    decimals: int = 18
    total_supply: float
    circulating_supply: float
    current_price_usd: float = 0.0
    market_cap_usd: float = 0.0
    holders_count: int = 0
    is_primary_token: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TokenHolder(BaseModel):
    """Token holder with balance information"""
    wallet_address: str
    token_balance: float
    voting_power: float  # May differ due to delegation
    delegated_votes: float = 0.0  # Votes delegated to this holder
    delegate_address: Optional[str] = None  # Address this holder delegates to
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DAOMember(BaseModel):
    """Enhanced DAO member with roles and reputation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    wallet_addresses: List[str] = Field(default_factory=list)  # Multiple wallets supported
    primary_wallet: str
    role: MemberRole = MemberRole.MEMBER
    
    # Token holdings per network
    token_balances: Dict[str, float] = Field(default_factory=dict)  # {network: balance}
    total_voting_power: float = 0.0
    delegated_power: float = 0.0
    
    # Delegation
    delegates_to: Optional[str] = None  # Address this member delegates to
    delegators: List[str] = Field(default_factory=list)  # Addresses that delegate to this member
    
    # Stats
    proposals_created: int = 0
    votes_cast: int = 0
    proposals_passed: int = 0
    participation_rate: float = 0.0
    reputation_score: float = 0.0
    
    # Permissions
    can_create_proposals: bool = True
    can_vote: bool = True
    is_delegate: bool = False
    is_council_member: bool = False
    
    # Metadata
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Delegation(BaseModel):
    """Vote delegation record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    delegator_address: str
    delegate_address: str
    network: NetworkType
    delegated_amount: float
    transaction_hash: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


# ============== PROPOSAL MODELS ==============

class ProposalAction(BaseModel):
    """Action to be executed if proposal passes"""
    target_contract: str
    function_signature: str
    call_data: str
    value: float = 0.0  # ETH/MATIC value to send
    description: str


class ProposalV2(BaseModel):
    """Enhanced DAO Proposal with multi-chain support"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_number: int  # Sequential numbering
    
    # Basic info
    title: str
    description: str
    summary: str = ""
    category: ProposalCategory
    
    # Governance type
    governance_type: GovernanceType = GovernanceType.HYBRID
    network: NetworkType = NetworkType.ETHEREUM
    
    # Proposer info
    proposer_id: str
    proposer_address: str
    proposer_name: Optional[str] = None
    
    # State
    state: ProposalState = ProposalState.DRAFT
    
    # Timing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    voting_starts: Optional[datetime] = None
    voting_ends: Optional[datetime] = None
    execution_eta: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    
    # Thresholds
    quorum_required: float = 10.0  # Percentage of total voting power
    approval_threshold: float = 50.0  # Percentage of yes votes needed
    proposal_threshold: float = 1.0  # Min voting power to create proposal
    
    # Voting stats
    total_votes: int = 0
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    
    # Weighted voting
    weight_for: float = 0.0
    weight_against: float = 0.0
    weight_abstain: float = 0.0
    total_voting_power_snapshot: float = 0.0  # Total at proposal creation
    
    # Actions (for executable proposals)
    actions: List[ProposalAction] = Field(default_factory=list)
    
    # Treasury
    treasury_impact: float = 0.0  # Estimated treasury impact in USD
    requires_treasury_approval: bool = False
    
    # Blockchain data
    on_chain_proposal_id: Optional[int] = None
    creation_tx_hash: Optional[str] = None
    execution_tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    
    # Metadata
    discussion_url: Optional[str] = None
    ipfs_hash: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VoteRecord(BaseModel):
    """Individual vote record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    voter_id: str
    voter_address: str
    
    choice: VoteOption
    voting_power: float
    reason: Optional[str] = None
    
    # Blockchain data
    network: NetworkType = NetworkType.ETHEREUM
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    is_on_chain: bool = False
    
    voted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Signature for off-chain votes
    signature: Optional[str] = None
    signed_message: Optional[str] = None


# ============== TREASURY MODELS ==============

class TreasuryAsset(BaseModel):
    """Treasury asset holding"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: TreasuryAssetType
    symbol: str
    name: str
    contract_address: Optional[str] = None
    network: NetworkType
    balance: float
    value_usd: float
    percentage_of_treasury: float = 0.0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TreasuryTransaction(BaseModel):
    """Treasury transaction record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_type: TransactionType
    
    # Asset info
    asset_symbol: str
    asset_address: Optional[str] = None
    network: NetworkType
    amount: float
    value_usd: float
    
    # Addresses
    from_address: str
    to_address: str
    
    # Governance
    proposal_id: Optional[str] = None
    approved_by: Optional[str] = None
    
    # Blockchain
    transaction_hash: str
    block_number: int
    gas_used: int = 0
    gas_price_gwei: float = 0.0
    
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Treasury(BaseModel):
    """DAO Treasury state"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "BME DAO Treasury"
    
    # Multi-chain addresses
    addresses: Dict[str, str] = Field(default_factory=dict)  # {network: address}
    
    # Holdings
    total_value_usd: float = 0.0
    assets: List[TreasuryAsset] = Field(default_factory=list)
    
    # Stats
    monthly_inflow: float = 0.0
    monthly_outflow: float = 0.0
    pending_allocations: float = 0.0
    
    # Governance
    multisig_signers: List[str] = Field(default_factory=list)
    required_signatures: int = 3
    
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============== GOVERNANCE CONFIG ==============

class GovernanceConfig(BaseModel):
    """DAO Governance configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dao_name: str = "Big Mann Entertainment DAO"
    dao_version: str = "2.0"
    
    # Networks
    primary_network: NetworkType = NetworkType.ETHEREUM
    supported_networks: List[NetworkType] = Field(default_factory=lambda: [
        NetworkType.ETHEREUM, NetworkType.POLYGON
    ])
    
    # Contract addresses per network
    governance_contracts: Dict[str, str] = Field(default_factory=dict)
    token_contracts: Dict[str, str] = Field(default_factory=dict)
    treasury_contracts: Dict[str, str] = Field(default_factory=dict)
    timelock_contracts: Dict[str, str] = Field(default_factory=dict)
    
    # Voting parameters
    voting_delay_blocks: int = 1  # Blocks before voting starts
    voting_period_blocks: int = 50400  # ~7 days on Ethereum
    voting_period_seconds: int = 604800  # 7 days fallback
    
    # Thresholds
    proposal_threshold: float = 100.0  # Tokens needed to create proposal
    quorum_percentage: float = 10.0  # % of total supply for quorum
    approval_threshold: float = 50.0  # % of votes for approval
    
    # Role requirements
    council_threshold: float = 10000.0  # Tokens to become council
    delegate_threshold: float = 1000.0  # Tokens to become delegate
    
    # Timelock
    timelock_delay_seconds: int = 172800  # 2 days
    
    # Features
    delegation_enabled: bool = True
    snapshot_voting_enabled: bool = True  # Off-chain voting
    multi_chain_voting: bool = True
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============== METRICS MODELS ==============

class GovernanceMetrics(BaseModel):
    """DAO Governance analytics"""
    # Proposals
    total_proposals: int = 0
    active_proposals: int = 0
    passed_proposals: int = 0
    rejected_proposals: int = 0
    executed_proposals: int = 0
    
    # Participation
    total_votes_cast: int = 0
    unique_voters: int = 0
    average_participation_rate: float = 0.0
    average_quorum_reached: float = 0.0
    
    # Token holders
    total_token_holders: int = 0
    active_voters_30d: int = 0
    total_delegated_power: float = 0.0
    delegation_rate: float = 0.0
    
    # Treasury
    treasury_total_usd: float = 0.0
    treasury_proposals_count: int = 0
    total_treasury_allocated: float = 0.0
    
    # By network
    metrics_by_network: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemberStats(BaseModel):
    """Individual member statistics"""
    member_id: str
    wallet_address: str
    
    # Holdings
    total_tokens: float = 0.0
    voting_power: float = 0.0
    voting_power_rank: int = 0
    
    # Activity
    proposals_created: int = 0
    proposals_passed: int = 0
    votes_cast: int = 0
    participation_rate: float = 0.0
    
    # Delegation
    delegators_count: int = 0
    delegated_to_count: int = 0
    total_delegated_power: float = 0.0
    
    # Reputation
    reputation_score: float = 0.0
    streak_days: int = 0
    
    # Role
    role: MemberRole = MemberRole.MEMBER
    role_since: Optional[datetime] = None


# ============== REQUEST/RESPONSE MODELS ==============

class CreateProposalRequest(BaseModel):
    """Request to create a new proposal"""
    title: str
    description: str
    summary: Optional[str] = None
    category: ProposalCategory
    governance_type: GovernanceType = GovernanceType.HYBRID
    network: NetworkType = NetworkType.ETHEREUM
    
    # Optional timing (defaults to standard voting period)
    voting_starts: Optional[datetime] = None
    voting_ends: Optional[datetime] = None
    
    # Optional custom thresholds
    quorum_required: Optional[float] = None
    approval_threshold: Optional[float] = None
    
    # Actions (for executable proposals)
    actions: List[ProposalAction] = Field(default_factory=list)
    
    # Treasury
    treasury_amount: Optional[float] = None
    
    # Metadata
    discussion_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class CastVoteRequest(BaseModel):
    """Request to cast a vote"""
    proposal_id: str
    choice: VoteOption
    reason: Optional[str] = None
    
    # For off-chain voting
    signature: Optional[str] = None
    signed_message: Optional[str] = None


class DelegateVotesRequest(BaseModel):
    """Request to delegate votes"""
    delegate_address: str
    network: NetworkType = NetworkType.ETHEREUM
    expires_at: Optional[datetime] = None


class TreasuryAllocationRequest(BaseModel):
    """Request for treasury allocation"""
    asset_symbol: str
    amount: float
    recipient_address: str
    network: NetworkType = NetworkType.ETHEREUM
    description: str
    proposal_id: Optional[str] = None


# ============== API RESPONSE MODELS ==============

class ProposalResponse(BaseModel):
    """API response for proposal data"""
    success: bool
    proposal: Optional[ProposalV2] = None
    error: Optional[str] = None
    message: Optional[str] = None
    transaction_hash: Optional[str] = None


class VoteResponse(BaseModel):
    """API response for vote data"""
    success: bool
    vote: Optional[VoteRecord] = None
    error: Optional[str] = None
    message: Optional[str] = None
    current_results: Optional[Dict[str, Any]] = None


class TreasuryResponse(BaseModel):
    """API response for treasury data"""
    success: bool
    treasury: Optional[Treasury] = None
    error: Optional[str] = None
    insights: List[str] = Field(default_factory=list)


class MemberResponse(BaseModel):
    """API response for member data"""
    success: bool
    member: Optional[DAOMember] = None
    stats: Optional[MemberStats] = None
    error: Optional[str] = None
