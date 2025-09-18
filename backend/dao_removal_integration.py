"""
DAO Removal Integration Service
Blockchain-based governance for content removal decisions
"""

import os
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from web3 import Web3
from eth_account import Account
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class DAOProposal:
    """DAO removal proposal structure"""
    proposal_id: str
    content_id: str
    proposer: str
    title: str
    description: str
    removal_reason: str
    target_platforms: List[str]
    territory_scope: str
    voting_start: datetime
    voting_end: datetime
    votes_for: int = 0
    votes_against: int = 0
    total_votes: int = 0
    status: str = "active"  # active, passed, rejected, executed
    blockchain_tx_hash: Optional[str] = None
    smart_contract_address: Optional[str] = None

@dataclass 
class DAOVote:
    """Individual DAO vote"""
    vote_id: str
    proposal_id: str
    voter: str
    vote: str  # "for" or "against"
    vote_weight: int
    timestamp: datetime
    blockchain_tx_hash: Optional[str] = None

class DAORemovalIntegration:
    """Service for blockchain-based DAO governance of content removal"""
    
    def __init__(self):
        # Blockchain configuration
        self.web3_provider_url = os.getenv('WEB3_INFURA_URL', 'https://mainnet.infura.io/v3/your-key')
        self.contract_address = os.getenv('DAO_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000')
        self.blockchain_network = os.getenv('BLOCKCHAIN_NETWORK', 'ethereum_mainnet')
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.web3_provider_url))
        self.is_connected = False
        
        # Smart contract ABI for DAO governance
        self.contract_abi = self._load_contract_abi()
        self.contract = None
        
        # Governance parameters
        self.min_voting_period = 24  # hours
        self.max_voting_period = 168  # hours (7 days)
        self.quorum_threshold = 100  # minimum votes required
        self.approval_threshold = 0.6  # 60% approval required
        
        try:
            self._initialize_blockchain_connection()
        except Exception as e:
            logger.warning(f"Blockchain connection failed: {e}")
    
    def _load_contract_abi(self) -> List[Dict]:
        """Load smart contract ABI for DAO governance"""
        # This would be the actual ABI for the DAO removal governance contract
        return [
            {
                "inputs": [
                    {"name": "contentId", "type": "string"},
                    {"name": "removalReason", "type": "string"},
                    {"name": "description", "type": "string"},
                    {"name": "votingDuration", "type": "uint256"}
                ],
                "name": "proposeRemoval",
                "outputs": [{"name": "proposalId", "type": "uint256"}],
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "proposalId", "type": "uint256"},
                    {"name": "support", "type": "bool"}
                ],
                "name": "vote",
                "outputs": [],
                "type": "function"
            },
            {
                "inputs": [{"name": "proposalId", "type": "uint256"}],
                "name": "executeProposal",
                "outputs": [],
                "type": "function"
            },
            {
                "inputs": [{"name": "proposalId", "type": "uint256"}],
                "name": "getProposal",
                "outputs": [
                    {"name": "contentId", "type": "string"},
                    {"name": "proposer", "type": "address"},
                    {"name": "votesFor", "type": "uint256"},
                    {"name": "votesAgainst", "type": "uint256"},
                    {"name": "startTime", "type": "uint256"},
                    {"name": "endTime", "type": "uint256"},
                    {"name": "executed", "type": "bool"}
                ],
                "type": "function"
            },
            {
                "inputs": [{"name": "user", "type": "address"}],
                "name": "getVotingPower",
                "outputs": [{"name": "power", "type": "uint256"}],
                "type": "function"
            }
        ]
    
    def _initialize_blockchain_connection(self):
        """Initialize blockchain connection and contract instance"""
        try:
            if self.w3.isConnected():
                self.is_connected = True
                logger.info("Connected to blockchain network")
                
                # Initialize contract if address is provided
                if self.contract_address != '0x0000000000000000000000000000000000000000':
                    self.contract = self.w3.eth.contract(
                        address=self.contract_address,
                        abi=self.contract_abi
                    )
                    logger.info(f"DAO contract initialized at {self.contract_address}")
            else:
                logger.warning("Failed to connect to blockchain network")
                
        except Exception as e:
            logger.error(f"Blockchain initialization error: {e}")
            self.is_connected = False
    
    async def create_removal_proposal(
        self,
        content_id: str,
        proposer_address: str,
        title: str,
        description: str,
        removal_reason: str,
        target_platforms: List[str] = None,
        territory_scope: str = "worldwide",
        voting_duration_hours: int = 72
    ) -> DAOProposal:
        """Create a new DAO removal proposal"""
        
        # Validate voting duration
        if voting_duration_hours < self.min_voting_period:
            voting_duration_hours = self.min_voting_period
        elif voting_duration_hours > self.max_voting_period:
            voting_duration_hours = self.max_voting_period
        
        # Create proposal object
        proposal = DAOProposal(
            proposal_id=f"dao_removal_{int(datetime.now().timestamp())}",
            content_id=content_id,
            proposer=proposer_address,
            title=title,
            description=description,
            removal_reason=removal_reason,
            target_platforms=target_platforms or [],
            territory_scope=territory_scope,
            voting_start=datetime.now(timezone.utc),
            voting_end=datetime.now(timezone.utc) + timedelta(hours=voting_duration_hours)
        )
        
        # Submit to blockchain if connected
        if self.is_connected and self.contract:
            try:
                blockchain_proposal_id = await self._submit_proposal_to_blockchain(proposal)
                proposal.blockchain_tx_hash = blockchain_proposal_id
                proposal.smart_contract_address = self.contract_address
                logger.info(f"Proposal submitted to blockchain: {blockchain_proposal_id}")
            except Exception as e:
                logger.error(f"Blockchain proposal submission failed: {e}")
                # Continue with off-chain proposal
        
        return proposal
    
    async def _submit_proposal_to_blockchain(self, proposal: DAOProposal) -> str:
        """Submit proposal to blockchain smart contract"""
        
        if not self.contract:
            raise Exception("Smart contract not initialized")
        
        try:
            # Build transaction for proposal creation
            # This would use the actual private key in production
            private_key = os.getenv('DAO_PRIVATE_KEY', '')
            if not private_key:
                raise Exception("DAO private key not configured")
            
            account = Account.from_key(private_key)
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            # Build transaction
            transaction = self.contract.functions.proposeRemoval(
                proposal.content_id,
                proposal.removal_reason,
                proposal.description,
                int((proposal.voting_end - proposal.voting_start).total_seconds())
            ).buildTransaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.toWei('20', 'gwei')
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.transactionHash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain transaction failed: {e}")
            raise
    
    async def cast_vote(
        self,
        proposal_id: str,
        voter_address: str,
        vote: str,
        vote_weight: Optional[int] = None
    ) -> DAOVote:
        """Cast a vote on a DAO removal proposal"""
        
        if vote not in ["for", "against"]:
            raise ValueError("Vote must be 'for' or 'against'")
        
        # Get voting power if not specified
        if vote_weight is None:
            vote_weight = await self._get_voting_power(voter_address)
        
        # Create vote object
        dao_vote = DAOVote(
            vote_id=f"vote_{int(datetime.now().timestamp())}_{voter_address[-8:]}",
            proposal_id=proposal_id,
            voter=voter_address,
            vote=vote,
            vote_weight=vote_weight,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Submit to blockchain if connected
        if self.is_connected and self.contract:
            try:
                tx_hash = await self._submit_vote_to_blockchain(dao_vote)
                dao_vote.blockchain_tx_hash = tx_hash
                logger.info(f"Vote submitted to blockchain: {tx_hash}")
            except Exception as e:
                logger.error(f"Blockchain vote submission failed: {e}")
                # Continue with off-chain vote
        
        return dao_vote
    
    async def _submit_vote_to_blockchain(self, vote: DAOVote) -> str:
        """Submit vote to blockchain smart contract"""
        
        if not self.contract:
            raise Exception("Smart contract not initialized")
        
        try:
            # This would use the voter's private key in production
            private_key = os.getenv('DAO_PRIVATE_KEY', '')
            account = Account.from_key(private_key)
            
            # Convert proposal ID to uint256 for blockchain
            proposal_id_uint = int(vote.proposal_id.split('_')[-1]) if '_' in vote.proposal_id else 0
            
            # Build vote transaction
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            transaction = self.contract.functions.vote(
                proposal_id_uint,
                vote.vote == "for"
            ).buildTransaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.toWei('20', 'gwei')
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.transactionHash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain vote transaction failed: {e}")
            raise
    
    async def _get_voting_power(self, voter_address: str) -> int:
        """Get voting power for a user"""
        
        if self.is_connected and self.contract:
            try:
                # Query voting power from smart contract
                voting_power = self.contract.functions.getVotingPower(voter_address).call()
                return int(voting_power)
            except Exception as e:
                logger.error(f"Failed to get voting power from blockchain: {e}")
        
        # Default voting power
        return 1
    
    async def check_proposal_outcome(self, proposal: DAOProposal) -> Dict[str, Any]:
        """Check if a proposal has passed and can be executed"""
        
        # Check if voting period has ended
        if datetime.now(timezone.utc) < proposal.voting_end:
            return {
                "status": "voting_active",
                "can_execute": False,
                "message": "Voting period is still active"
            }
        
        # Check quorum
        if proposal.total_votes < self.quorum_threshold:
            return {
                "status": "failed_quorum",
                "can_execute": False,
                "message": f"Insufficient votes. Required: {self.quorum_threshold}, Received: {proposal.total_votes}"
            }
        
        # Check approval threshold
        approval_rate = proposal.votes_for / proposal.total_votes if proposal.total_votes > 0 else 0
        
        if approval_rate >= self.approval_threshold:
            return {
                "status": "passed",
                "can_execute": True,
                "approval_rate": approval_rate,
                "votes_for": proposal.votes_for,
                "votes_against": proposal.votes_against,
                "total_votes": proposal.total_votes
            }
        else:
            return {
                "status": "rejected",
                "can_execute": False,
                "approval_rate": approval_rate,
                "message": f"Insufficient approval. Required: {self.approval_threshold * 100}%, Received: {approval_rate * 100}%"
            }
    
    async def execute_proposal(self, proposal: DAOProposal) -> Dict[str, Any]:
        """Execute a passed DAO proposal"""
        
        # Check if proposal can be executed
        outcome = await self.check_proposal_outcome(proposal)
        
        if not outcome["can_execute"]:
            raise ValueError(f"Proposal cannot be executed: {outcome['message']}")
        
        # Execute on blockchain if connected
        execution_tx = None
        if self.is_connected and self.contract:
            try:
                execution_tx = await self._execute_proposal_on_blockchain(proposal)
                logger.info(f"Proposal executed on blockchain: {execution_tx}")
            except Exception as e:
                logger.error(f"Blockchain execution failed: {e}")
        
        # Return execution result
        return {
            "status": "executed",
            "proposal_id": proposal.proposal_id,
            "execution_tx": execution_tx,
            "outcome": outcome,
            "executed_at": datetime.now(timezone.utc)
        }
    
    async def _execute_proposal_on_blockchain(self, proposal: DAOProposal) -> str:
        """Execute proposal on blockchain smart contract"""
        
        if not self.contract:
            raise Exception("Smart contract not initialized")
        
        try:
            private_key = os.getenv('DAO_PRIVATE_KEY', '')
            account = Account.from_key(private_key)
            
            # Convert proposal ID for blockchain
            proposal_id_uint = int(proposal.proposal_id.split('_')[-1]) if '_' in proposal.proposal_id else 0
            
            # Build execution transaction
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            transaction = self.contract.functions.executeProposal(
                proposal_id_uint
            ).buildTransaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.w3.toWei('20', 'gwei')
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.transactionHash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain execution transaction failed: {e}")
            raise
    
    async def get_blockchain_proposal_data(self, proposal_id: str) -> Dict[str, Any]:
        """Get proposal data from blockchain"""
        
        if not self.is_connected or not self.contract:
            return {"error": "Blockchain not connected"}
        
        try:
            # Convert proposal ID for blockchain query
            proposal_id_uint = int(proposal_id.split('_')[-1]) if '_' in proposal_id else 0
            
            # Query proposal data
            proposal_data = self.contract.functions.getProposal(proposal_id_uint).call()
            
            return {
                "content_id": proposal_data[0],
                "proposer": proposal_data[1],
                "votes_for": proposal_data[2],
                "votes_against": proposal_data[3],
                "start_time": datetime.fromtimestamp(proposal_data[4], tz=timezone.utc),
                "end_time": datetime.fromtimestamp(proposal_data[5], tz=timezone.utc),
                "executed": proposal_data[6]
            }
            
        except Exception as e:
            logger.error(f"Failed to query blockchain proposal: {e}")
            return {"error": str(e)}
    
    async def sync_with_blockchain(self, proposal: DAOProposal) -> DAOProposal:
        """Sync proposal data with blockchain state"""
        
        if not self.is_connected or not self.contract:
            return proposal
        
        try:
            blockchain_data = await self.get_blockchain_proposal_data(proposal.proposal_id)
            
            if "error" not in blockchain_data:
                # Update proposal with blockchain data
                proposal.votes_for = blockchain_data["votes_for"]
                proposal.votes_against = blockchain_data["votes_against"]
                proposal.total_votes = proposal.votes_for + proposal.votes_against
                
                if blockchain_data["executed"]:
                    proposal.status = "executed"
                elif datetime.now(timezone.utc) > blockchain_data["end_time"]:
                    outcome = await self.check_proposal_outcome(proposal)
                    proposal.status = outcome["status"]
                
                logger.info(f"Synced proposal {proposal.proposal_id} with blockchain")
            
        except Exception as e:
            logger.error(f"Failed to sync with blockchain: {e}")
        
        return proposal
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get blockchain connection status"""
        return {
            "connected": self.is_connected,
            "network": self.blockchain_network,
            "contract_address": self.contract_address,
            "provider_url": self.web3_provider_url,
            "latest_block": self.w3.eth.block_number if self.is_connected else None
        }
    
    async def get_user_dao_stats(self, user_address: str) -> Dict[str, Any]:
        """Get DAO participation statistics for a user"""
        
        voting_power = await self._get_voting_power(user_address)
        
        return {
            "user_address": user_address,
            "voting_power": voting_power,
            "can_propose": voting_power >= 10,  # Minimum tokens to propose
            "can_vote": voting_power >= 1,
            "blockchain_connected": self.is_connected
        }

# Global DAO integration instance
dao_integration = DAORemovalIntegration()

async def get_dao_service() -> DAORemovalIntegration:
    """Get DAO integration service instance"""
    return dao_integration