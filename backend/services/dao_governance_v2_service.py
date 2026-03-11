"""
Big Mann Entertainment - DAO 2.0 Governance Service
Advanced DAO governance with multi-chain support (Ethereum + Polygon)
Token-based weighted voting, Treasury management, Member roles
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from dao_governance_v2_models import (
    NetworkType, GovernanceType, ProposalCategory, ProposalState, VoteOption, MemberRole,
    TreasuryAssetType, TransactionType,
    GovernanceToken, TokenHolder, DAOMember, Delegation,
    ProposalV2, ProposalAction, VoteRecord,
    TreasuryAsset, TreasuryTransaction, Treasury,
    GovernanceConfig, GovernanceMetrics, MemberStats,
    CreateProposalRequest, CastVoteRequest, DelegateVotesRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DAOGovernanceV2Service:
    """Enhanced DAO Governance Service with multi-chain support"""
    
    def __init__(self):
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._initialized = False
        
        # In-memory caches for demo/fallback
        self.proposals_cache: Dict[str, ProposalV2] = {}
        self.votes_cache: Dict[str, VoteRecord] = {}
        self.members_cache: Dict[str, DAOMember] = {}
        self.treasury_cache: Optional[Treasury] = None
        self.config_cache: Optional[GovernanceConfig] = None
        self.proposal_counter = 0
    
    def initialize(self, db: AsyncIOMotorDatabase):
        """Initialize service with database"""
        self.db = db
        self._initialized = True
        self._init_default_data()
        logger.info("DAO Governance V2 Service initialized")
    
    def _init_default_data(self):
        """Initialize default governance configuration and sample data"""
        # Governance configuration
        self.config_cache = GovernanceConfig(
            dao_name="Big Mann Entertainment DAO",
            dao_version="2.0",
            primary_network=NetworkType.ETHEREUM,
            supported_networks=[NetworkType.ETHEREUM, NetworkType.POLYGON],
            governance_contracts={
                "ethereum": "0xBME_GOV_ETH_CONTRACT_ADDRESS",
                "polygon": "0xBME_GOV_POLYGON_CONTRACT_ADDRESS"
            },
            token_contracts={
                "ethereum": "0xBME_TOKEN_ETH_CONTRACT_ADDRESS",
                "polygon": "0xBME_TOKEN_POLYGON_CONTRACT_ADDRESS"
            },
            treasury_contracts={
                "ethereum": "0xBME_TREASURY_ETH_CONTRACT_ADDRESS",
                "polygon": "0xBME_TREASURY_POLYGON_CONTRACT_ADDRESS"
            },
            proposal_threshold=100.0,
            quorum_percentage=10.0,
            approval_threshold=50.0,
            council_threshold=10000.0,
            delegate_threshold=1000.0,
            voting_period_seconds=604800  # 7 days
        )
        
        # Treasury
        self.treasury_cache = Treasury(
            name="BME DAO Treasury",
            addresses={
                "ethereum": "0xBME_TREASURY_ETH",
                "polygon": "0xBME_TREASURY_POLYGON"
            },
            total_value_usd=2_850_000.0,
            assets=[
                TreasuryAsset(
                    asset_type=TreasuryAssetType.NATIVE,
                    symbol="ETH",
                    name="Ethereum",
                    network=NetworkType.ETHEREUM,
                    balance=520.5,
                    value_usd=1_350_000.0,
                    percentage_of_treasury=47.4
                ),
                TreasuryAsset(
                    asset_type=TreasuryAssetType.STABLECOIN,
                    symbol="USDC",
                    name="USD Coin",
                    contract_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    network=NetworkType.ETHEREUM,
                    balance=1_200_000.0,
                    value_usd=1_200_000.0,
                    percentage_of_treasury=42.1
                ),
                TreasuryAsset(
                    asset_type=TreasuryAssetType.NATIVE,
                    symbol="MATIC",
                    name="Polygon",
                    network=NetworkType.POLYGON,
                    balance=250_000.0,
                    value_usd=200_000.0,
                    percentage_of_treasury=7.0
                ),
                TreasuryAsset(
                    asset_type=TreasuryAssetType.ERC20,
                    symbol="BME",
                    name="BME Governance Token",
                    contract_address="0xBME_TOKEN_CONTRACT",
                    network=NetworkType.ETHEREUM,
                    balance=100_000.0,
                    value_usd=100_000.0,
                    percentage_of_treasury=3.5
                )
            ],
            monthly_inflow=185_000.0,
            monthly_outflow=95_000.0,
            pending_allocations=75_000.0,
            multisig_signers=[
                "0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A",
                "0x8b5C9F7e3A1d2E6F4C8B7A9e3D2F1C8E4A7B9C6D",
                "0x3F8E7D6C5B4A9e8d7c6b5a4F3E2d1C0B9A8e7d6c"
            ],
            required_signatures=2
        )
        
        # Sample members
        self._init_sample_members()
        self._init_sample_proposals()
    
    def _init_sample_members(self):
        """Initialize sample DAO members"""
        members = [
            DAOMember(
                id="member_001",
                user_id="user_001",
                wallet_addresses=["0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A"],
                primary_wallet="0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A",
                role=MemberRole.COUNCIL,
                token_balances={"ethereum": 25000.0, "polygon": 5000.0},
                total_voting_power=30000.0,
                delegated_power=8500.0,
                proposals_created=5,
                votes_cast=28,
                proposals_passed=4,
                participation_rate=92.5,
                reputation_score=95.2,
                is_council_member=True,
                display_name="John Spivey",
                bio="Founder & CEO of Big Mann Entertainment"
            ),
            DAOMember(
                id="member_002",
                user_id="user_002",
                wallet_addresses=["0x8b5C9F7e3A1d2E6F4C8B7A9e3D2F1C8E4A7B9C6D"],
                primary_wallet="0x8b5C9F7e3A1d2E6F4C8B7A9e3D2F1C8E4A7B9C6D",
                role=MemberRole.DELEGATE,
                token_balances={"ethereum": 5000.0, "polygon": 2000.0},
                total_voting_power=7000.0,
                delegated_power=12500.0,
                is_delegate=True,
                delegators=["0xAAA...", "0xBBB...", "0xCCC..."],
                proposals_created=2,
                votes_cast=35,
                participation_rate=100.0,
                reputation_score=98.5,
                display_name="Sarah Chen",
                bio="Community delegate and active contributor"
            ),
            DAOMember(
                id="member_003",
                user_id="user_003",
                wallet_addresses=["0x3F8E7D6C5B4A9e8d7c6b5a4F3E2d1C0B9A8e7d6c"],
                primary_wallet="0x3F8E7D6C5B4A9e8d7c6b5a4F3E2d1C0B9A8e7d6c",
                role=MemberRole.COUNCIL,
                token_balances={"ethereum": 18000.0, "polygon": 3000.0},
                total_voting_power=21000.0,
                proposals_created=3,
                votes_cast=25,
                proposals_passed=2,
                participation_rate=85.7,
                reputation_score=91.3,
                is_council_member=True,
                display_name="Michael Torres",
                bio="Council member and treasury advisor"
            ),
            DAOMember(
                id="member_004",
                user_id="user_004",
                wallet_addresses=["0x1234567890AbCdEf1234567890AbCdEf12345678"],
                primary_wallet="0x1234567890AbCdEf1234567890AbCdEf12345678",
                role=MemberRole.MEMBER,
                token_balances={"ethereum": 1500.0, "polygon": 500.0},
                total_voting_power=2000.0,
                votes_cast=12,
                participation_rate=65.4,
                reputation_score=72.8,
                display_name="Alex Kim"
            )
        ]
        
        for member in members:
            self.members_cache[member.id] = member
    
    def _init_sample_proposals(self):
        """Initialize sample proposals"""
        now = datetime.now(timezone.utc)
        
        proposals = [
            ProposalV2(
                id="prop_001",
                proposal_number=1,
                title="Increase Artist Revenue Share to 75%",
                description="Proposal to increase the artist revenue share from the current 70% to 75% on all streaming platforms. This adjustment aims to better compensate creators for their work while maintaining platform sustainability.",
                summary="Increase artist revenue share from 70% to 75%",
                category=ProposalCategory.REVENUE_DISTRIBUTION,
                governance_type=GovernanceType.HYBRID,
                network=NetworkType.ETHEREUM,
                proposer_id="user_001",
                proposer_address="0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A",
                proposer_name="John Spivey",
                state=ProposalState.ACTIVE,
                voting_starts=now - timedelta(days=2),
                voting_ends=now + timedelta(days=5),
                quorum_required=10.0,
                approval_threshold=50.0,
                total_votes=312,
                votes_for=245,
                votes_against=52,
                votes_abstain=15,
                weight_for=185_000.0,
                weight_against=42_000.0,
                weight_abstain=8_000.0,
                total_voting_power_snapshot=750_000.0,
                on_chain_proposal_id=1,
                discussion_url="https://forum.bigmannentertainment.com/proposal-1",
                tags=["revenue", "artists", "streaming"]
            ),
            ProposalV2(
                id="prop_002",
                proposal_number=2,
                title="Treasury Allocation for Marketing Campaign",
                description="Allocate $150,000 from the treasury for a comprehensive Q1 2026 marketing campaign targeting emerging markets in Asia and Latin America.",
                summary="Allocate $150k for Q1 marketing campaign",
                category=ProposalCategory.TREASURY_ALLOCATION,
                governance_type=GovernanceType.ON_CHAIN,
                network=NetworkType.ETHEREUM,
                proposer_id="user_003",
                proposer_address="0x3F8E7D6C5B4A9e8d7c6b5a4F3E2d1C0B9A8e7d6c",
                proposer_name="Michael Torres",
                state=ProposalState.SUCCEEDED,
                voting_starts=now - timedelta(days=12),
                voting_ends=now - timedelta(days=5),
                execution_eta=now + timedelta(days=2),
                quorum_required=15.0,
                approval_threshold=60.0,
                total_votes=198,
                votes_for=165,
                votes_against=28,
                votes_abstain=5,
                weight_for=145_000.0,
                weight_against=25_000.0,
                weight_abstain=3_500.0,
                total_voting_power_snapshot=750_000.0,
                treasury_impact=-150_000.0,
                requires_treasury_approval=True,
                on_chain_proposal_id=2,
                tags=["treasury", "marketing", "expansion"]
            ),
            ProposalV2(
                id="prop_003",
                proposal_number=3,
                title="Add Polygon Network Support for NFTs",
                description="Implement Polygon network support for NFT minting and trading to reduce gas fees for users. This includes deploying new smart contracts on Polygon and updating the frontend.",
                summary="Add Polygon support for lower-cost NFTs",
                category=ProposalCategory.PLATFORM_UPGRADE,
                governance_type=GovernanceType.HYBRID,
                network=NetworkType.POLYGON,
                proposer_id="user_002",
                proposer_address="0x8b5C9F7e3A1d2E6F4C8B7A9e3D2F1C8E4A7B9C6D",
                proposer_name="Sarah Chen",
                state=ProposalState.ACTIVE,
                voting_starts=now - timedelta(days=1),
                voting_ends=now + timedelta(days=6),
                quorum_required=10.0,
                approval_threshold=50.0,
                total_votes=87,
                votes_for=72,
                votes_against=10,
                votes_abstain=5,
                weight_for=65_000.0,
                weight_against=8_500.0,
                weight_abstain=3_200.0,
                total_voting_power_snapshot=750_000.0,
                treasury_impact=-25_000.0,
                on_chain_proposal_id=3,
                tags=["polygon", "nft", "gas-optimization"]
            ),
            ProposalV2(
                id="prop_004",
                proposal_number=4,
                title="Establish DAO Council Election Process",
                description="Create a formal election process for DAO Council members with term limits and voting procedures. Council members will serve 6-month terms with a maximum of 2 consecutive terms.",
                summary="Formalize DAO Council elections",
                category=ProposalCategory.GOVERNANCE_CHANGE,
                governance_type=GovernanceType.ON_CHAIN,
                network=NetworkType.ETHEREUM,
                proposer_id="user_001",
                proposer_address="0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A",
                proposer_name="John Spivey",
                state=ProposalState.DRAFT,
                voting_starts=now + timedelta(days=3),
                voting_ends=now + timedelta(days=10),
                quorum_required=20.0,
                approval_threshold=66.0,
                total_votes=0,
                total_voting_power_snapshot=750_000.0,
                tags=["governance", "council", "elections"]
            ),
            ProposalV2(
                id="prop_005",
                proposal_number=5,
                title="Partnership with Universal Music Group",
                description="Formal partnership agreement with Universal Music Group for content distribution and licensing. This partnership will expand our reach and provide exclusive content opportunities.",
                summary="Strategic partnership with Universal Music",
                category=ProposalCategory.PARTNERSHIP,
                governance_type=GovernanceType.HYBRID,
                network=NetworkType.ETHEREUM,
                proposer_id="user_001",
                proposer_address="0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A",
                proposer_name="John Spivey",
                state=ProposalState.EXECUTED,
                voting_starts=now - timedelta(days=20),
                voting_ends=now - timedelta(days=13),
                executed_at=now - timedelta(days=10),
                quorum_required=15.0,
                approval_threshold=60.0,
                total_votes=245,
                votes_for=218,
                votes_against=22,
                votes_abstain=5,
                weight_for=195_000.0,
                weight_against=18_000.0,
                weight_abstain=4_000.0,
                total_voting_power_snapshot=750_000.0,
                on_chain_proposal_id=5,
                execution_tx_hash="0xabc123...",
                tags=["partnership", "music", "distribution"]
            )
        ]
        
        for proposal in proposals:
            self.proposals_cache[proposal.id] = proposal
            self.proposal_counter = max(self.proposal_counter, proposal.proposal_number)
    
    # ============== PROPOSAL METHODS ==============
    
    async def create_proposal(self, request: CreateProposalRequest, user_id: str, wallet_address: str) -> Dict[str, Any]:
        """Create a new governance proposal"""
        try:
            # Validate user can create proposals
            member = self._get_member_by_user_id(user_id)
            if not member:
                return {"success": False, "error": "User is not a DAO member"}
            
            if member.total_voting_power < self.config_cache.proposal_threshold:
                return {
                    "success": False,
                    "error": f"Insufficient voting power. Required: {self.config_cache.proposal_threshold}, Have: {member.total_voting_power}"
                }
            
            # Create proposal
            self.proposal_counter += 1
            now = datetime.now(timezone.utc)
            
            voting_starts = request.voting_starts or (now + timedelta(hours=24))
            voting_ends = request.voting_ends or (voting_starts + timedelta(seconds=self.config_cache.voting_period_seconds))
            
            proposal = ProposalV2(
                proposal_number=self.proposal_counter,
                title=request.title,
                description=request.description,
                summary=request.summary or request.description[:200],
                category=request.category,
                governance_type=request.governance_type,
                network=request.network,
                proposer_id=user_id,
                proposer_address=wallet_address,
                proposer_name=member.display_name,
                state=ProposalState.DRAFT,
                voting_starts=voting_starts,
                voting_ends=voting_ends,
                quorum_required=request.quorum_required or self.config_cache.quorum_percentage,
                approval_threshold=request.approval_threshold or self.config_cache.approval_threshold,
                actions=request.actions,
                treasury_impact=request.treasury_amount or 0.0,
                requires_treasury_approval=request.treasury_amount is not None and request.treasury_amount != 0,
                discussion_url=request.discussion_url,
                tags=request.tags,
                total_voting_power_snapshot=750_000.0  # Would query from blockchain
            )
            
            # Save to cache
            self.proposals_cache[proposal.id] = proposal
            
            # Update member stats
            member.proposals_created += 1
            member.last_active = now
            
            # Store in database if available
            if self.db is not None:
                await self.db.dao_proposals_v2.insert_one(proposal.model_dump())
            
            logger.info(f"Created proposal #{proposal.proposal_number}: {proposal.title}")
            
            return {
                "success": True,
                "proposal_id": proposal.id,
                "proposal_number": proposal.proposal_number,
                "message": "Proposal created successfully",
                "voting_starts": proposal.voting_starts.isoformat(),
                "voting_ends": proposal.voting_ends.isoformat(),
                "governance_type": proposal.governance_type.value,
                "network": proposal.network.value
            }
            
        except Exception as e:
            logger.error(f"Error creating proposal: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_proposals(
        self,
        user_id: Optional[str] = None,
        state: Optional[ProposalState] = None,
        category: Optional[ProposalCategory] = None,
        network: Optional[NetworkType] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get governance proposals with filters"""
        try:
            proposals = list(self.proposals_cache.values())
            
            # Apply filters
            if state:
                proposals = [p for p in proposals if p.state == state]
            if category:
                proposals = [p for p in proposals if p.category == category]
            if network:
                proposals = [p for p in proposals if p.network == network]
            
            # Sort by creation date (newest first)
            proposals.sort(key=lambda x: x.created_at, reverse=True)
            
            # Pagination
            total = len(proposals)
            proposals = proposals[offset:offset + limit]
            
            # Calculate stats
            all_proposals = list(self.proposals_cache.values())
            stats = {
                "total": len(all_proposals),
                "active": len([p for p in all_proposals if p.state == ProposalState.ACTIVE]),
                "succeeded": len([p for p in all_proposals if p.state == ProposalState.SUCCEEDED]),
                "executed": len([p for p in all_proposals if p.state == ProposalState.EXECUTED]),
                "defeated": len([p for p in all_proposals if p.state == ProposalState.DEFEATED]),
                "draft": len([p for p in all_proposals if p.state == ProposalState.DRAFT])
            }
            
            return {
                "success": True,
                "proposals": [p.model_dump() for p in proposals],
                "total": total,
                "limit": limit,
                "offset": offset,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error fetching proposals: {str(e)}")
            return {"success": False, "error": str(e), "proposals": []}
    
    async def get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Get a single proposal by ID"""
        try:
            proposal = self.proposals_cache.get(proposal_id)
            if not proposal:
                return {"success": False, "error": "Proposal not found"}
            
            # Get votes for this proposal
            votes = [v for v in self.votes_cache.values() if v.proposal_id == proposal_id]
            
            # Calculate participation
            quorum_progress = (proposal.weight_for + proposal.weight_against + proposal.weight_abstain) / proposal.total_voting_power_snapshot * 100
            approval_progress = (proposal.weight_for / (proposal.weight_for + proposal.weight_against) * 100) if (proposal.weight_for + proposal.weight_against) > 0 else 0
            
            return {
                "success": True,
                "proposal": proposal.model_dump(),
                "votes_count": len(votes),
                "quorum_progress": round(quorum_progress, 2),
                "approval_progress": round(approval_progress, 2),
                "quorum_met": quorum_progress >= proposal.quorum_required,
                "approval_met": approval_progress >= proposal.approval_threshold
            }
            
        except Exception as e:
            logger.error(f"Error fetching proposal: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ============== VOTING METHODS ==============
    
    async def cast_vote(self, request: CastVoteRequest, user_id: str, wallet_address: str) -> Dict[str, Any]:
        """Cast a vote on a proposal"""
        try:
            proposal = self.proposals_cache.get(request.proposal_id)
            if not proposal:
                return {"success": False, "error": "Proposal not found"}
            
            # Check if voting is active
            now = datetime.now(timezone.utc)
            if proposal.state != ProposalState.ACTIVE:
                if now < proposal.voting_starts:
                    return {"success": False, "error": "Voting has not started yet"}
                if now > proposal.voting_ends:
                    return {"success": False, "error": "Voting has ended"}
            
            # Get member voting power
            member = self._get_member_by_user_id(user_id)
            if not member:
                return {"success": False, "error": "User is not a DAO member"}
            
            # Check if already voted
            existing_vote = next(
                (v for v in self.votes_cache.values() 
                 if v.proposal_id == request.proposal_id and v.voter_id == user_id),
                None
            )
            if existing_vote:
                return {"success": False, "error": "You have already voted on this proposal"}
            
            # Calculate voting power
            voting_power = member.total_voting_power + member.delegated_power
            
            # Create vote record
            vote = VoteRecord(
                proposal_id=request.proposal_id,
                voter_id=user_id,
                voter_address=wallet_address,
                choice=request.choice,
                voting_power=voting_power,
                reason=request.reason,
                network=proposal.network,
                is_on_chain=proposal.governance_type in [GovernanceType.ON_CHAIN, GovernanceType.HYBRID],
                transaction_hash=f"0x{uuid.uuid4().hex}" if proposal.governance_type != GovernanceType.OFF_CHAIN else None,
                signature=request.signature,
                signed_message=request.signed_message
            )
            
            # Update proposal votes
            proposal.total_votes += 1
            if request.choice == VoteOption.FOR:
                proposal.votes_for += 1
                proposal.weight_for += voting_power
            elif request.choice == VoteOption.AGAINST:
                proposal.votes_against += 1
                proposal.weight_against += voting_power
            else:
                proposal.votes_abstain += 1
                proposal.weight_abstain += voting_power
            
            # Update member stats
            member.votes_cast += 1
            member.last_active = now
            
            # Save vote
            self.votes_cache[vote.id] = vote
            
            # Store in database if available
            if self.db is not None:
                await self.db.dao_votes_v2.insert_one(vote.model_dump())
            
            logger.info(f"Vote cast on proposal {proposal.proposal_number} by {wallet_address}: {request.choice.value}")
            
            return {
                "success": True,
                "vote_id": vote.id,
                "transaction_hash": vote.transaction_hash,
                "voting_power": voting_power,
                "message": f"Vote '{request.choice.value}' cast successfully",
                "current_results": {
                    "votes_for": proposal.votes_for,
                    "votes_against": proposal.votes_against,
                    "votes_abstain": proposal.votes_abstain,
                    "weight_for": proposal.weight_for,
                    "weight_against": proposal.weight_against,
                    "weight_abstain": proposal.weight_abstain
                }
            }
            
        except Exception as e:
            logger.error(f"Error casting vote: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_proposal_votes(self, proposal_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get votes for a proposal"""
        try:
            votes = [v for v in self.votes_cache.values() if v.proposal_id == proposal_id]
            votes.sort(key=lambda x: x.voted_at, reverse=True)
            
            total = len(votes)
            votes = votes[offset:offset + limit]
            
            return {
                "success": True,
                "votes": [v.model_dump() for v in votes],
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error fetching votes: {str(e)}")
            return {"success": False, "error": str(e), "votes": []}
    
    # ============== MEMBER METHODS ==============
    
    def _get_member_by_user_id(self, user_id: str) -> Optional[DAOMember]:
        """Get member by user ID"""
        return next((m for m in self.members_cache.values() if m.user_id == user_id), None)
    
    def _get_member_by_wallet(self, wallet_address: str) -> Optional[DAOMember]:
        """Get member by wallet address"""
        wallet_lower = wallet_address.lower()
        return next(
            (m for m in self.members_cache.values() 
             if wallet_lower in [w.lower() for w in m.wallet_addresses]),
            None
        )
    
    async def get_member_profile(self, user_id: str, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Get DAO member profile with stats"""
        try:
            member = self._get_member_by_user_id(user_id)
            if not member:
                # Create new member
                member = DAOMember(
                    user_id=user_id,
                    wallet_addresses=[wallet_address] if wallet_address else [],
                    primary_wallet=wallet_address or "",
                    token_balances={"ethereum": 0.0, "polygon": 0.0},
                    total_voting_power=0.0
                )
                self.members_cache[member.id] = member
            
            # Calculate stats
            member_votes = [v for v in self.votes_cache.values() if v.voter_id == user_id]
            member_proposals = [p for p in self.proposals_cache.values() if p.proposer_id == user_id]
            
            # Participation rate
            active_proposals = [p for p in self.proposals_cache.values() if p.state != ProposalState.DRAFT]
            participation_rate = (len(member_votes) / len(active_proposals) * 100) if active_proposals else 0
            
            stats = MemberStats(
                member_id=member.id,
                wallet_address=member.primary_wallet,
                total_tokens=sum(member.token_balances.values()),
                voting_power=member.total_voting_power + member.delegated_power,
                voting_power_rank=1,  # Would calculate from all members
                proposals_created=len(member_proposals),
                proposals_passed=len([p for p in member_proposals if p.state == ProposalState.EXECUTED]),
                votes_cast=len(member_votes),
                participation_rate=round(participation_rate, 1),
                delegators_count=len(member.delegators),
                delegated_to_count=1 if member.delegates_to else 0,
                total_delegated_power=member.delegated_power,
                reputation_score=member.reputation_score,
                role=member.role,
                role_since=member.joined_at
            )
            
            return {
                "success": True,
                "member": member.model_dump(),
                "stats": stats.model_dump(),
                "recent_votes": [v.model_dump() for v in member_votes[-5:]],
                "recent_proposals": [p.model_dump() for p in member_proposals[-5:]]
            }
            
        except Exception as e:
            logger.error(f"Error fetching member profile: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delegate_votes(self, request: DelegateVotesRequest, user_id: str, wallet_address: str) -> Dict[str, Any]:
        """Delegate voting power to another address"""
        try:
            member = self._get_member_by_user_id(user_id)
            if not member:
                return {"success": False, "error": "User is not a DAO member"}
            
            delegate_member = self._get_member_by_wallet(request.delegate_address)
            if not delegate_member:
                return {"success": False, "error": "Delegate address not found in DAO"}
            
            if not delegate_member.is_delegate and delegate_member.role != MemberRole.COUNCIL:
                return {"success": False, "error": "Target address is not a delegate"}
            
            # Remove previous delegation
            if member.delegates_to:
                old_delegate = self._get_member_by_wallet(member.delegates_to)
                if old_delegate:
                    old_delegate.delegated_power -= member.total_voting_power
                    if wallet_address in old_delegate.delegators:
                        old_delegate.delegators.remove(wallet_address)
            
            # Set new delegation
            member.delegates_to = request.delegate_address
            delegate_member.delegated_power += member.total_voting_power
            delegate_member.delegators.append(wallet_address)
            
            # Create delegation record
            delegation = Delegation(
                delegator_address=wallet_address,
                delegate_address=request.delegate_address,
                network=request.network,
                delegated_amount=member.total_voting_power,
                transaction_hash=f"0x{uuid.uuid4().hex}",
                expires_at=request.expires_at
            )
            
            logger.info(f"Delegated {member.total_voting_power} voting power from {wallet_address} to {request.delegate_address}")
            
            return {
                "success": True,
                "delegation_id": delegation.id,
                "transaction_hash": delegation.transaction_hash,
                "delegated_amount": delegation.delegated_amount,
                "delegate_address": request.delegate_address,
                "delegate_new_power": delegate_member.total_voting_power + delegate_member.delegated_power,
                "message": "Voting power delegated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error delegating votes: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_delegates(self, network: Optional[NetworkType] = None) -> Dict[str, Any]:
        """Get list of delegates"""
        try:
            delegates = [m for m in self.members_cache.values() if m.is_delegate or m.role == MemberRole.DELEGATE]
            
            return {
                "success": True,
                "delegates": [
                    {
                        "id": d.id,
                        "wallet_address": d.primary_wallet,
                        "display_name": d.display_name,
                        "bio": d.bio,
                        "total_voting_power": d.total_voting_power + d.delegated_power,
                        "own_tokens": d.total_voting_power,
                        "delegated_power": d.delegated_power,
                        "delegators_count": len(d.delegators),
                        "votes_cast": d.votes_cast,
                        "participation_rate": d.participation_rate,
                        "reputation_score": d.reputation_score
                    }
                    for d in delegates
                ],
                "total_delegates": len(delegates)
            }
            
        except Exception as e:
            logger.error(f"Error fetching delegates: {str(e)}")
            return {"success": False, "error": str(e), "delegates": []}
    
    # ============== TREASURY METHODS ==============
    
    async def get_treasury(self, network: Optional[NetworkType] = None) -> Dict[str, Any]:
        """Get treasury information"""
        try:
            treasury = self.treasury_cache
            
            # Filter assets by network if specified
            assets = treasury.assets
            if network:
                assets = [a for a in assets if a.network == network]
            
            # Sample transactions
            transactions = [
                {
                    "id": "tx_001",
                    "type": "deposit",
                    "asset": "USDC",
                    "amount": 50000.0,
                    "from": "0x742d35C6...",
                    "description": "Q4 Revenue Deposit",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
                },
                {
                    "id": "tx_002",
                    "type": "withdrawal",
                    "asset": "USDC",
                    "amount": 25000.0,
                    "to": "0x8b5C9F7e...",
                    "proposal_id": "prop_002",
                    "description": "Marketing Campaign Allocation",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
                },
                {
                    "id": "tx_003",
                    "type": "reward",
                    "asset": "ETH",
                    "amount": 5.2,
                    "from": "Staking Rewards",
                    "description": "Monthly staking rewards",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
                }
            ]
            
            return {
                "success": True,
                "treasury": {
                    "name": treasury.name,
                    "total_value_usd": treasury.total_value_usd,
                    "addresses": treasury.addresses,
                    "assets": [a.model_dump() for a in assets],
                    "monthly_inflow": treasury.monthly_inflow,
                    "monthly_outflow": treasury.monthly_outflow,
                    "net_flow": treasury.monthly_inflow - treasury.monthly_outflow,
                    "pending_allocations": treasury.pending_allocations,
                    "multisig_signers": treasury.multisig_signers,
                    "required_signatures": treasury.required_signatures
                },
                "recent_transactions": transactions,
                "flow_chart": [
                    {"month": "Sep", "inflow": 125000, "outflow": 45000},
                    {"month": "Oct", "inflow": 148000, "outflow": 62000},
                    {"month": "Nov", "inflow": 165000, "outflow": 78000},
                    {"month": "Dec", "inflow": 185000, "outflow": 95000}
                ],
                "insights": [
                    "Treasury has grown 18% this quarter",
                    "47% of holdings in ETH, 42% in stablecoins",
                    "Average monthly net inflow: $75,000",
                    "2 pending allocation proposals totaling $175,000"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching treasury: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ============== GOVERNANCE METRICS ==============
    
    async def get_governance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive governance metrics"""
        try:
            proposals = list(self.proposals_cache.values())
            votes = list(self.votes_cache.values())
            members = list(self.members_cache.values())
            
            # Calculate metrics
            metrics = GovernanceMetrics(
                total_proposals=len(proposals),
                active_proposals=len([p for p in proposals if p.state == ProposalState.ACTIVE]),
                passed_proposals=len([p for p in proposals if p.state in [ProposalState.SUCCEEDED, ProposalState.EXECUTED]]),
                rejected_proposals=len([p for p in proposals if p.state == ProposalState.DEFEATED]),
                executed_proposals=len([p for p in proposals if p.state == ProposalState.EXECUTED]),
                total_votes_cast=len(votes),
                unique_voters=len(set(v.voter_id for v in votes)),
                average_participation_rate=sum(m.participation_rate for m in members) / len(members) if members else 0,
                total_token_holders=len(members),
                active_voters_30d=len(set(v.voter_id for v in votes if v.voted_at >= datetime.now(timezone.utc) - timedelta(days=30))),
                total_delegated_power=sum(m.delegated_power for m in members),
                delegation_rate=len([m for m in members if m.delegates_to]) / len(members) * 100 if members else 0,
                treasury_total_usd=self.treasury_cache.total_value_usd if self.treasury_cache else 0,
                treasury_proposals_count=len([p for p in proposals if p.category == ProposalCategory.TREASURY_ALLOCATION])
            )
            
            # Governance token info
            token_info = {
                "name": "BME Governance Token",
                "symbol": "BME",
                "total_supply": 1_000_000.0,
                "circulating_supply": 750_000.0,
                "holders": len(members),
                "price_usd": 1.0,
                "market_cap_usd": 750_000.0
            }
            
            # Participation trends
            participation_trends = [
                {"month": "Sep", "participation": 58.2, "proposals": 3, "unique_voters": 145},
                {"month": "Oct", "participation": 62.7, "proposals": 4, "unique_voters": 178},
                {"month": "Nov", "participation": 71.3, "proposals": 2, "unique_voters": 165},
                {"month": "Dec", "participation": 78.5, "proposals": 5, "unique_voters": 234}
            ]
            
            return {
                "success": True,
                "metrics": metrics.model_dump(),
                "token": token_info,
                "participation_trends": participation_trends,
                "top_voters": [
                    {"address": m.primary_wallet[:10] + "...", "votes": m.votes_cast, "power": m.total_voting_power}
                    for m in sorted(members, key=lambda x: x.votes_cast, reverse=True)[:5]
                ],
                "insights": [
                    f"Participation rate has increased 35% over 4 months",
                    f"{metrics.executed_proposals} proposals successfully executed",
                    f"{metrics.active_voters_30d} active voters in the last 30 days",
                    f"${metrics.treasury_total_usd:,.0f} in treasury"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching governance metrics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ============== CONFIGURATION ==============
    
    async def get_governance_config(self) -> Dict[str, Any]:
        """Get governance configuration"""
        try:
            config = self.config_cache
            return {
                "success": True,
                "config": config.model_dump(),
                "networks": [n.value for n in config.supported_networks],
                "contracts": {
                    "governance": config.governance_contracts,
                    "token": config.token_contracts,
                    "treasury": config.treasury_contracts,
                    "timelock": config.timelock_contracts
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching config: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_council_members(self) -> Dict[str, Any]:
        """Get DAO Council members"""
        try:
            council = [m for m in self.members_cache.values() if m.role == MemberRole.COUNCIL or m.is_council_member]
            
            return {
                "success": True,
                "council": [
                    {
                        "id": m.id,
                        "wallet_address": m.primary_wallet,
                        "display_name": m.display_name,
                        "bio": m.bio,
                        "voting_power": m.total_voting_power,
                        "proposals_created": m.proposals_created,
                        "votes_cast": m.votes_cast,
                        "reputation_score": m.reputation_score,
                        "joined_at": m.joined_at.isoformat()
                    }
                    for m in council
                ],
                "total_council_members": len(council),
                "council_threshold": self.config_cache.council_threshold
            }
            
        except Exception as e:
            logger.error(f"Error fetching council: {str(e)}")
            return {"success": False, "error": str(e)}


# Global service instance
dao_governance_v2_service = DAOGovernanceV2Service()


def initialize_dao_v2_service(db: AsyncIOMotorDatabase) -> DAOGovernanceV2Service:
    """Initialize the DAO Governance V2 service"""
    dao_governance_v2_service.initialize(db)
    return dao_governance_v2_service
