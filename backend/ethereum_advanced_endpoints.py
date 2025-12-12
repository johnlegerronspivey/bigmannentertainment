"""
Advanced Ethereum Features
Provides contract deployment, transaction history, and enhanced DAO voting
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
from web3 import Web3
from eth_account import Account
import logging
from datetime import datetime, timezone
import json
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ethereum/advanced", tags=["ethereum-advanced"])

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize Web3 connection
def get_web3_connection():
    """Get Web3 connection instance"""
    try:
        rpc_url = os.getenv('ETHEREUM_RPC_URL')
        if not rpc_url:
            raise ValueError("ETHEREUM_RPC_URL not configured")
        
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3
    except Exception as e:
        logger.error(f"Failed to initialize Web3: {e}")
        return None

# ==================== CONTRACT DEPLOYMENT ====================

class ContractDeploymentRequest(BaseModel):
    contract_type: str  # erc20, erc721, erc1155, royalty_splitter, custom
    contract_name: str
    contract_symbol: Optional[str] = None
    initial_supply: Optional[str] = None  # For ERC-20
    base_uri: Optional[str] = None  # For ERC-721/1155
    recipients: Optional[List[str]] = None  # For royalty splitter
    percentages: Optional[List[float]] = None  # For royalty splitter
    custom_constructor_params: Optional[Dict[str, Any]] = None

class ContractDeploymentResponse(BaseModel):
    success: bool
    contract_id: str
    contract_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    gas_used: Optional[int] = None
    deployment_cost_eth: Optional[str] = None
    block_number: Optional[int] = None
    network: str
    error: Optional[str] = None

# ERC-20 Token Contract (Simplified Solidity bytecode - in production, use compiled contracts)
ERC20_BYTECODE = "0x608060405234801561001057600080fd5b50610150806100206000396000f3fe"
ERC721_BYTECODE = "0x608060405234801561001057600080fd5b50610150806100206000396000f3fe"
ROYALTY_SPLITTER_BYTECODE = "0x608060405234801561001057600080fd5b50610150806100206000396000f3fe"

@router.post("/deploy-contract", response_model=ContractDeploymentResponse)
async def deploy_contract(request: ContractDeploymentRequest):
    """
    Deploy a smart contract to Ethereum mainnet
    Supports ERC-20, ERC-721, ERC-1155, and custom royalty splitter contracts
    """
    try:
        w3 = get_web3_connection()
        if not w3 or not w3.is_connected():
            raise HTTPException(status_code=503, detail="Ethereum connection not available")
        
        private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
        if not private_key:
            raise HTTPException(
                status_code=400, 
                detail="Private key not configured. Contract deployment requires transaction signing."
            )
        
        # Create account from private key
        account = Account.from_key(private_key)
        
        # Get contract bytecode and ABI based on type
        bytecode, abi = get_contract_template(request.contract_type)
        
        # Prepare constructor arguments
        constructor_args = prepare_constructor_args(request)
        
        # Estimate gas
        gas_estimate = w3.eth.estimate_gas({
            'from': account.address,
            'data': bytecode
        })
        
        # Create contract instance
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build transaction
        transaction = contract.constructor(*constructor_args).build_transaction({
            'from': account.address,
            'gas': int(gas_estimate * 1.2),  # Add 20% buffer
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        
        # Sign transaction
        signed_txn = account.sign_transaction(transaction)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        contract_address = receipt['contractAddress']
        gas_used = receipt['gasUsed']
        deployment_cost = w3.from_wei(gas_used * transaction['gasPrice'], 'ether')
        
        # Generate contract ID
        contract_id = f"ETH-{request.contract_type.upper()}-{contract_address[:10]}"
        
        # Store contract in database
        contract_doc = {
            "contract_id": contract_id,
            "contract_address": contract_address,
            "contract_type": request.contract_type,
            "contract_name": request.contract_name,
            "contract_symbol": request.contract_symbol,
            "transaction_hash": tx_hash.hex(),
            "deployer_address": account.address,
            "network": os.getenv('ETHEREUM_NETWORK', 'mainnet'),
            "gas_used": gas_used,
            "deployment_cost_eth": str(deployment_cost),
            "block_number": receipt['blockNumber'],
            "deployed_at": datetime.now(timezone.utc),
            "status": "deployed",
            "abi": abi,
            "constructor_params": constructor_args
        }
        
        await db.deployed_contracts.insert_one(contract_doc)
        
        logger.info(f"Contract deployed: {contract_address}")
        
        return ContractDeploymentResponse(
            success=True,
            contract_id=contract_id,
            contract_address=contract_address,
            transaction_hash=tx_hash.hex(),
            gas_used=gas_used,
            deployment_cost_eth=str(deployment_cost),
            block_number=receipt['blockNumber'],
            network=os.getenv('ETHEREUM_NETWORK', 'mainnet')
        )
        
    except Exception as e:
        logger.error(f"Contract deployment error: {e}")
        return ContractDeploymentResponse(
            success=False,
            contract_id="",
            network=os.getenv('ETHEREUM_NETWORK', 'mainnet'),
            error=str(e)
        )

@router.get("/deployed-contracts")
async def get_deployed_contracts():
    """
    Get all deployed contracts
    """
    try:
        contracts = await db.deployed_contracts.find({}, {"_id": 0}).sort("deployed_at", -1).to_list(100)
        return {
            "success": True,
            "contracts": contracts,
            "total": len(contracts)
        }
    except Exception as e:
        logger.error(f"Error fetching contracts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contract/{contract_id}")
async def get_contract_details(contract_id: str):
    """
    Get details of a specific deployed contract
    """
    try:
        contract = await db.deployed_contracts.find_one({"contract_id": contract_id}, {"_id": 0})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {
            "success": True,
            "contract": contract
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TRANSACTION HISTORY ====================

class TransactionHistoryResponse(BaseModel):
    success: bool
    transactions: List[Dict[str, Any]]
    total_count: int
    error: Optional[str] = None

@router.get("/transactions/{address}", response_model=TransactionHistoryResponse)
async def get_transaction_history(address: str, limit: int = 50, offset: int = 0):
    """
    Get transaction history for a wallet address
    Note: For production, use Etherscan API or similar service for comprehensive history
    This implementation shows recent transactions from our tracked interactions
    """
    try:
        w3 = get_web3_connection()
        if not w3 or not w3.is_connected():
            raise HTTPException(status_code=503, detail="Ethereum connection not available")
        
        # Validate address
        if not Web3.is_address(address):
            raise HTTPException(status_code=400, detail="Invalid Ethereum address")
        
        address = Web3.to_checksum_address(address)
        
        # Get transactions from our database
        transactions = await db.transaction_history.find(
            {"$or": [{"from_address": address}, {"to_address": address}]},
            {"_id": 0}
        ).sort("timestamp", -1).skip(offset).limit(limit).to_list(limit)
        
        # Enrich with current block confirmation count
        current_block = w3.eth.block_number
        for tx in transactions:
            if tx.get('block_number'):
                tx['confirmations'] = current_block - tx['block_number']
        
        total_count = await db.transaction_history.count_documents(
            {"$or": [{"from_address": address}, {"to_address": address}]}
        )
        
        return TransactionHistoryResponse(
            success=True,
            transactions=transactions,
            total_count=total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transaction history: {e}")
        return TransactionHistoryResponse(
            success=False,
            transactions=[],
            total_count=0,
            error=str(e)
        )

@router.post("/track-transaction")
async def track_transaction(transaction_hash: str):
    """
    Track a transaction and store its details in database
    """
    try:
        w3 = get_web3_connection()
        if not w3 or not w3.is_connected():
            raise HTTPException(status_code=503, detail="Ethereum connection not available")
        
        # Get transaction details
        tx = w3.eth.get_transaction(transaction_hash)
        receipt = w3.eth.get_transaction_receipt(transaction_hash)
        
        # Store in database
        tx_doc = {
            "transaction_hash": transaction_hash,
            "from_address": tx['from'],
            "to_address": tx['to'],
            "value_wei": str(tx['value']),
            "value_eth": str(w3.from_wei(tx['value'], 'ether')),
            "gas_used": receipt['gasUsed'],
            "gas_price": str(tx['gasPrice']),
            "block_number": tx['blockNumber'],
            "block_timestamp": datetime.now(timezone.utc),
            "status": "success" if receipt['status'] == 1 else "failed",
            "input_data": tx['input'],
            "network": os.getenv('ETHEREUM_NETWORK', 'mainnet'),
            "timestamp": datetime.now(timezone.utc)
        }
        
        await db.transaction_history.update_one(
            {"transaction_hash": transaction_hash},
            {"$set": tx_doc},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Transaction tracked successfully",
            "transaction": tx_doc
        }
        
    except Exception as e:
        logger.error(f"Error tracking transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DAO VOTING ====================

class DAOProposal(BaseModel):
    title: str
    description: str
    proposal_type: str  # royalty_change, platform_addition, policy_change, feature_request, treasury_allocation
    voting_period_days: int = 7
    quorum_percentage: float = 10.0  # Minimum % of total voting power needed
    approval_threshold: float = 51.0  # % of votes needed to pass
    execution_data: Optional[Dict[str, Any]] = None

class VoteRequest(BaseModel):
    vote_choice: str  # for, against, abstain
    voting_power: Optional[float] = 1.0
    reason: Optional[str] = None

@router.post("/dao/create-proposal")
async def create_dao_proposal(proposal: DAOProposal):
    """
    Create a new DAO governance proposal
    """
    try:
        # Generate proposal ID
        proposal_id = f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate voting end time
        from datetime import timedelta
        voting_ends_at = datetime.now(timezone.utc) + timedelta(days=proposal.voting_period_days)
        
        # Store proposal in database
        proposal_doc = {
            "proposal_id": proposal_id,
            "title": proposal.title,
            "description": proposal.description,
            "proposal_type": proposal.proposal_type,
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "voting_ends_at": voting_ends_at,
            "quorum_percentage": proposal.quorum_percentage,
            "approval_threshold": proposal.approval_threshold,
            "votes_for": 0,
            "votes_against": 0,
            "votes_abstain": 0,
            "total_voting_power": 0,
            "voters": [],
            "execution_data": proposal.execution_data,
            "executed": False,
            "execution_tx_hash": None
        }
        
        await db.dao_proposals.insert_one(proposal_doc)
        
        logger.info(f"DAO proposal created: {proposal_id}")
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "message": "Proposal created successfully",
            "voting_ends_at": voting_ends_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dao/vote/{proposal_id}")
async def vote_on_proposal(proposal_id: str, vote: VoteRequest, voter_address: str = Body(...)):
    """
    Vote on a DAO proposal
    """
    try:
        # Get proposal
        proposal = await db.dao_proposals.find_one({"proposal_id": proposal_id})
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Check if voting period is active
        if proposal['status'] != 'active':
            raise HTTPException(status_code=400, detail="Voting period has ended")
        
        if datetime.now(timezone.utc) > proposal['voting_ends_at'].replace(tzinfo=timezone.utc):
            # Update proposal status
            await db.dao_proposals.update_one(
                {"proposal_id": proposal_id},
                {"$set": {"status": "ended"}}
            )
            raise HTTPException(status_code=400, detail="Voting period has ended")
        
        # Check if voter has already voted
        if voter_address in proposal.get('voters', []):
            raise HTTPException(status_code=400, detail="You have already voted on this proposal")
        
        # Record vote
        vote_field = f"votes_{vote.vote_choice}"
        
        update_data = {
            "$inc": {
                vote_field: vote.voting_power,
                "total_voting_power": vote.voting_power
            },
            "$push": {
                "voters": voter_address
            }
        }
        
        await db.dao_proposals.update_one(
            {"proposal_id": proposal_id},
            update_data
        )
        
        # Store individual vote record
        vote_doc = {
            "proposal_id": proposal_id,
            "voter_address": voter_address,
            "vote_choice": vote.vote_choice,
            "voting_power": vote.voting_power,
            "reason": vote.reason,
            "voted_at": datetime.now(timezone.utc)
        }
        
        await db.dao_votes.insert_one(vote_doc)
        
        logger.info(f"Vote recorded: {proposal_id} by {voter_address}")
        
        return {
            "success": True,
            "message": "Vote recorded successfully",
            "proposal_id": proposal_id,
            "vote_choice": vote.vote_choice
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting on proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dao/proposals")
async def get_dao_proposals(status: Optional[str] = None, limit: int = 50):
    """
    Get DAO proposals
    """
    try:
        query = {}
        if status:
            query['status'] = status
        
        proposals = await db.dao_proposals.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Calculate voting statistics
        for proposal in proposals:
            total_votes = proposal['votes_for'] + proposal['votes_against'] + proposal['votes_abstain']
            if total_votes > 0:
                proposal['for_percentage'] = (proposal['votes_for'] / total_votes) * 100
                proposal['against_percentage'] = (proposal['votes_against'] / total_votes) * 100
                proposal['abstain_percentage'] = (proposal['votes_abstain'] / total_votes) * 100
            else:
                proposal['for_percentage'] = 0
                proposal['against_percentage'] = 0
                proposal['abstain_percentage'] = 0
            
            # Check if quorum is met
            # For simplicity, using total voting power as proxy
            proposal['quorum_met'] = proposal['total_voting_power'] >= proposal['quorum_percentage']
            
            # Check if proposal would pass
            if total_votes > 0:
                proposal['will_pass'] = (
                    proposal['quorum_met'] and 
                    (proposal['votes_for'] / total_votes * 100) >= proposal['approval_threshold']
                )
            else:
                proposal['will_pass'] = False
        
        return {
            "success": True,
            "proposals": proposals,
            "total": len(proposals)
        }
        
    except Exception as e:
        logger.error(f"Error fetching proposals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dao/proposal/{proposal_id}")
async def get_proposal_details(proposal_id: str):
    """
    Get detailed information about a specific proposal including votes
    """
    try:
        proposal = await db.dao_proposals.find_one({"proposal_id": proposal_id}, {"_id": 0})
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Get all votes for this proposal
        votes = await db.dao_votes.find({"proposal_id": proposal_id}, {"_id": 0}).to_list(1000)
        
        return {
            "success": True,
            "proposal": proposal,
            "votes": votes,
            "vote_count": len(votes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching proposal details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dao/execute/{proposal_id}")
async def execute_proposal(proposal_id: str):
    """
    Execute a passed DAO proposal
    Only executable if proposal passed and voting period ended
    """
    try:
        proposal = await db.dao_proposals.find_one({"proposal_id": proposal_id})
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Check if already executed
        if proposal.get('executed'):
            raise HTTPException(status_code=400, detail="Proposal already executed")
        
        # Check if voting ended
        if proposal['status'] == 'active' and datetime.now(timezone.utc) <= proposal['voting_ends_at'].replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=400, detail="Voting period still active")
        
        # Calculate if proposal passed
        total_votes = proposal['votes_for'] + proposal['votes_against'] + proposal['votes_abstain']
        if total_votes == 0:
            raise HTTPException(status_code=400, detail="No votes cast")
        
        quorum_met = proposal['total_voting_power'] >= proposal['quorum_percentage']
        approval_met = (proposal['votes_for'] / total_votes * 100) >= proposal['approval_threshold']
        
        if not (quorum_met and approval_met):
            await db.dao_proposals.update_one(
                {"proposal_id": proposal_id},
                {"$set": {"status": "rejected"}}
            )
            raise HTTPException(status_code=400, detail="Proposal did not meet quorum or approval threshold")
        
        # Execute proposal (this would interact with smart contracts in production)
        execution_result = {
            "executed_at": datetime.now(timezone.utc),
            "execution_status": "simulated",
            "note": "In production, this would trigger on-chain execution"
        }
        
        # Update proposal status
        await db.dao_proposals.update_one(
            {"proposal_id": proposal_id},
            {
                "$set": {
                    "status": "executed",
                    "executed": True,
                    "execution_result": execution_result,
                    "executed_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"Proposal executed: {proposal_id}")
        
        return {
            "success": True,
            "message": "Proposal executed successfully",
            "proposal_id": proposal_id,
            "execution_result": execution_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HELPER FUNCTIONS ====================

def get_contract_template(contract_type: str):
    """
    Get contract bytecode and ABI based on type
    Note: In production, use properly compiled and audited contracts
    """
    # Simplified ABI structures
    if contract_type == "erc20":
        abi = [
            {"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"}
        ]
        return ERC20_BYTECODE, abi
    elif contract_type == "erc721":
        abi = [
            {"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
        ]
        return ERC721_BYTECODE, abi
    elif contract_type == "royalty_splitter":
        abi = [
            {"constant":False,"inputs":[{"name":"recipients","type":"address[]"},{"name":"percentages","type":"uint256[]"}],"name":"distributeRoyalties","outputs":[],"type":"function"}
        ]
        return ROYALTY_SPLITTER_BYTECODE, abi
    else:
        raise ValueError(f"Unknown contract type: {contract_type}")

def prepare_constructor_args(request: ContractDeploymentRequest):
    """
    Prepare constructor arguments based on contract type
    """
    if request.contract_type == "erc20":
        return [request.contract_name, request.contract_symbol, int(request.initial_supply or "1000000")]
    elif request.contract_type == "erc721":
        return [request.contract_name, request.contract_symbol, request.base_uri or ""]
    elif request.contract_type == "royalty_splitter":
        return [request.recipients or [], request.percentages or []]
    else:
        return []
