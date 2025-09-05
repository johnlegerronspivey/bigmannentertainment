"""
Web3 NFT Service for Image Licensing
Handles NFT minting, royalty configuration, and DAO governance integration
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from decimal import Decimal
from dataclasses import dataclass

from web3 import Web3
from eth_account import Account
import uuid

from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class RoyaltyRecipient:
    address: str
    percentage: int
    role: str

@dataclass
class NFTMintRequest:
    to_address: str
    token_uri: str
    license_type: str
    duration: int
    restrictions: str
    commercial_use: bool
    max_resolution: int
    base_pricing: Decimal
    royalty_recipients: List[RoyaltyRecipient]

@dataclass
class DAOProposalRequest:
    proposal_type: str
    title: str
    description: str
    voting_period: int
    proposal_data: Dict[str, Any]

class Web3NFTService:
    def __init__(self, mongo_db=None):
        self.mongo_db = mongo_db
        self.networks = {
            'ethereum': {
                'rpc_url': os.getenv('ETHEREUM_RPC_URL'),
                'chain_id': 1,
                'contracts': {
                    'erc721': os.getenv('ETHEREUM_ERC721_CONTRACT'),
                    'erc1155': os.getenv('ETHEREUM_ERC1155_CONTRACT'),
                    'royalty_splitter': os.getenv('ETHEREUM_ROYALTY_SPLITTER_CONTRACT'),
                    'dao_governance': os.getenv('ETHEREUM_DAO_CONTRACT')
                }
            },
            'polygon': {
                'rpc_url': os.getenv('POLYGON_RPC_URL'),
                'chain_id': 137,
                'contracts': {
                    'erc721': os.getenv('POLYGON_ERC721_CONTRACT'),
                    'erc1155': os.getenv('POLYGON_ERC1155_CONTRACT'),
                    'royalty_splitter': os.getenv('POLYGON_ROYALTY_SPLITTER_CONTRACT'),
                    'dao_governance': os.getenv('POLYGON_DAO_CONTRACT')
                }
            },
            'base': {
                'rpc_url': os.getenv('BASE_RPC_URL', 'https://mainnet.base.org'),
                'chain_id': 8453,
                'contracts': {
                    'erc721': os.getenv('BASE_ERC721_CONTRACT'),
                    'erc1155': os.getenv('BASE_ERC1155_CONTRACT'),
                    'royalty_splitter': os.getenv('BASE_ROYALTY_SPLITTER_CONTRACT'),
                    'dao_governance': os.getenv('BASE_DAO_CONTRACT')
                }
            }
        }
        
        self.web3_instances = {}
        self.contracts = {}
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize Web3 connections and contract instances"""
        for network, config in self.networks.items():
            try:
                if config['rpc_url']:
                    w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
                    if w3.is_connected():
                        self.web3_instances[network] = w3
                        self.contracts[network] = {}
                        
                        # Load contract ABIs and initialize instances
                        self._load_contracts(network)
                        
                        logger.info(f"Connected to {network} network")
                    else:
                        logger.warning(f"Failed to connect to {network} network")
                        
            except Exception as e:
                logger.error(f"Error initializing {network}: {str(e)}")

    def _load_contracts(self, network: str):
        """Load contract ABIs and create contract instances"""
        try:
            # Load ABIs from files
            contract_abis = {}
            
            for contract_type in ['erc721', 'erc1155', 'royalty_splitter', 'dao_governance']:
                abi_file = f"contracts/abis/{contract_type}.json"
                if os.path.exists(abi_file):
                    with open(abi_file, 'r') as f:
                        contract_abis[contract_type] = json.load(f)

            # Create contract instances
            w3 = self.web3_instances[network]
            network_config = self.networks[network]
            
            for contract_type, address in network_config['contracts'].items():
                if address and contract_type in contract_abis:
                    self.contracts[network][contract_type] = w3.eth.contract(
                        address=address,
                        abi=contract_abis[contract_type]
                    )
                    
        except Exception as e:
            logger.error(f"Error loading contracts for {network}: {str(e)}")

    async def mint_nft_license(
        self, 
        network: str,
        token_standard: str,
        mint_request: NFTMintRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """Mint NFT license with embedded licensing terms"""
        
        if network not in self.web3_instances:
            raise ValueError(f"Network {network} not available")

        w3 = self.web3_instances[network]
        
        try:
            # Get account for transactions
            private_key = os.getenv('DEPLOYER_PRIVATE_KEY')
            if not private_key:
                # Simulate minting for development
                return await self._simulate_nft_minting(network, token_standard, mint_request, user_id)
            
            account = Account.from_key(private_key)
            
            if token_standard == 'ERC721':
                return await self._mint_erc721(w3, network, account, mint_request, user_id)
            elif token_standard == 'ERC1155':
                return await self._mint_erc1155(w3, network, account, mint_request, user_id)
            else:
                raise ValueError(f"Unsupported token standard: {token_standard}")
                
        except Exception as e:
            logger.error(f"NFT minting failed: {str(e)}")
            raise

    async def _mint_erc721(
        self,
        w3: Web3,
        network: str,
        account: Account,
        mint_request: NFTMintRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """Mint ERC-721 NFT"""
        
        contract = self.contracts[network].get('erc721')
        if not contract:
            raise ValueError(f"ERC-721 contract not available for {network}")

        try:
            # Prepare license terms tuple
            license_terms = (
                mint_request.license_type,
                mint_request.duration,
                mint_request.restrictions,
                mint_request.commercial_use,
                mint_request.max_resolution
            )
            
            # Calculate primary royalty recipient and percentage
            primary_recipient = mint_request.royalty_recipients[0].address
            total_royalty_percentage = sum(r.percentage for r in mint_request.royalty_recipients)
            
            # Build transaction
            nonce = w3.eth.get_transaction_count(account.address)
            
            transaction = contract.functions.mintImageLicense(
                mint_request.to_address,
                mint_request.token_uri,
                license_terms,
                primary_recipient,
                total_royalty_percentage * 100  # Convert to basis points
            ).build_transaction({
                'chainId': self.networks[network]['chain_id'],
                'gas': 500000,
                'gasPrice': w3.to_wei('25', 'gwei'),
                'nonce': nonce
            })
            
            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Extract token ID from logs
            token_id = None
            for log in receipt.logs:
                try:
                    decoded_log = contract.events.NFTMinted().processLog(log)
                    token_id = decoded_log.args.tokenId
                    break
                except:
                    continue
            
            if token_id is None:
                token_id = int(receipt.logs[0].topics[3].hex(), 16) if receipt.logs else 1
            
            # Setup royalty splits if multiple recipients
            if len(mint_request.royalty_recipients) > 1:
                await self._setup_royalty_splits(
                    network, account, token_id, mint_request.royalty_recipients
                )
            
            # Record minting in database
            await self._record_nft_mint(
                network=network,
                token_standard='ERC721',
                token_id=token_id,
                contract_address=contract.address,
                transaction_hash=tx_hash.hex(),
                user_id=user_id,
                mint_request=mint_request
            )
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'token_id': token_id,
                'contract_address': contract.address,
                'network': network,
                'token_standard': 'ERC721',
                'royalty_recipients': len(mint_request.royalty_recipients)
            }
            
        except Exception as e:
            logger.error(f"ERC-721 minting failed: {str(e)}")
            raise

    async def _mint_erc1155(
        self,
        w3: Web3,
        network: str,
        account: Account,
        mint_request: NFTMintRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """Mint ERC-1155 NFT"""
        
        contract = self.contracts[network].get('erc1155')
        if not contract:
            raise ValueError(f"ERC-1155 contract not available for {network}")

        try:
            # Generate unique token ID
            token_id = int(datetime.now().timestamp() * 1000) % (2**256)
            
            # Prepare batch license terms
            batch_terms = (
                mint_request.license_type,
                mint_request.duration,
                mint_request.restrictions,
                mint_request.commercial_use,
                mint_request.max_resolution,
                1000,  # max_supply
                0      # current_supply
            )
            
            primary_recipient = mint_request.royalty_recipients[0].address
            total_royalty_percentage = sum(r.percentage for r in mint_request.royalty_recipients)
            
            # Create batch license first
            nonce = w3.eth.get_transaction_count(account.address)
            
            create_transaction = contract.functions.createBatchLicense(
                token_id,
                mint_request.token_uri,
                batch_terms,
                primary_recipient,
                total_royalty_percentage * 100
            ).build_transaction({
                'chainId': self.networks[network]['chain_id'],
                'gas': 400000,
                'gasPrice': w3.to_wei('25', 'gwei'),
                'nonce': nonce
            })
            
            signed_create_txn = w3.eth.account.sign_transaction(create_transaction, private_key=account.key)
            create_tx_hash = w3.eth.send_raw_transaction(signed_create_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(create_tx_hash)
            
            # Mint batch to recipient
            mint_nonce = w3.eth.get_transaction_count(account.address)
            
            mint_transaction = contract.functions.mintBatch(
                mint_request.to_address,
                token_id,
                1,  # amount
                b""  # data
            ).build_transaction({
                'chainId': self.networks[network]['chain_id'],
                'gas': 200000,
                'gasPrice': w3.to_wei('25', 'gwei'),
                'nonce': mint_nonce
            })
            
            signed_mint_txn = w3.eth.account.sign_transaction(mint_transaction, private_key=account.key)
            mint_tx_hash = w3.eth.send_raw_transaction(signed_mint_txn.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(mint_tx_hash)
            
            # Setup royalty splits if multiple recipients
            if len(mint_request.royalty_recipients) > 1:
                await self._setup_royalty_splits(
                    network, account, token_id, mint_request.royalty_recipients
                )
            
            # Record minting in database
            await self._record_nft_mint(
                network=network,
                token_standard='ERC1155',
                token_id=token_id,
                contract_address=contract.address,
                transaction_hash=mint_tx_hash.hex(),
                user_id=user_id,
                mint_request=mint_request
            )
            
            return {
                'success': True,
                'transaction_hash': mint_tx_hash.hex(),
                'token_id': token_id,
                'contract_address': contract.address,
                'network': network,
                'token_standard': 'ERC1155',
                'create_tx_hash': create_tx_hash.hex(),
                'royalty_recipients': len(mint_request.royalty_recipients)
            }
            
        except Exception as e:
            logger.error(f"ERC-1155 minting failed: {str(e)}")
            raise

    async def _setup_royalty_splits(
        self,
        network: str,
        account: Account,
        token_id: int,
        recipients: List[RoyaltyRecipient]
    ):
        """Setup royalty splits for multiple recipients"""
        
        splitter_contract = self.contracts[network].get('royalty_splitter')
        if not splitter_contract:
            logger.warning(f"Royalty splitter contract not available for {network}")
            return

        try:
            w3 = self.web3_instances[network]
            
            # Convert recipients to contract format
            contract_shares = []
            for recipient in recipients:
                contract_shares.append((
                    recipient.address,
                    recipient.percentage * 100,  # Convert to basis points
                    recipient.role
                ))
            
            nonce = w3.eth.get_transaction_count(account.address)
            
            transaction = splitter_contract.functions.setNFTRoyaltyShares(
                token_id,
                contract_shares
            ).build_transaction({
                'chainId': self.networks[network]['chain_id'],
                'gas': 300000,
                'gasPrice': w3.to_wei('25', 'gwei'),
                'nonce': nonce
            })
            
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Royalty splits configured for token {token_id} on {network}")
            
        except Exception as e:
            logger.error(f"Failed to setup royalty splits: {str(e)}")

    async def create_dao_proposal(
        self,
        network: str,
        proposal_request: DAOProposalRequest,
        proposer_user_id: str
    ) -> Dict[str, Any]:
        """Create DAO governance proposal"""
        
        dao_contract = self.contracts[network].get('dao_governance')
        if not dao_contract:
            return await self._simulate_dao_proposal(network, proposal_request, proposer_user_id)

        try:
            w3 = self.web3_instances[network]
            private_key = os.getenv('DEPLOYER_PRIVATE_KEY')
            
            if not private_key:
                return await self._simulate_dao_proposal(network, proposal_request, proposer_user_id)
            
            account = Account.from_key(private_key)
            
            if proposal_request.proposal_type == 'licensing_terms':
                return await self._create_licensing_proposal(
                    w3, network, dao_contract, account, proposal_request, proposer_user_id
                )
            elif proposal_request.proposal_type == 'agency_onboarding':
                return await self._create_agency_proposal(
                    w3, network, dao_contract, account, proposal_request, proposer_user_id
                )
            else:
                raise ValueError(f"Unsupported proposal type: {proposal_request.proposal_type}")
                
        except Exception as e:
            logger.error(f"DAO proposal creation failed: {str(e)}")
            raise

    async def _simulate_nft_minting(
        self,
        network: str,
        token_standard: str,
        mint_request: NFTMintRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """Simulate NFT minting for development/testing"""
        
        # Generate simulated transaction hash and token ID
        tx_hash = f"0x{uuid.uuid4().hex}"
        token_id = int(datetime.now().timestamp() * 1000) % 1000000
        
        # Record simulated minting in database
        await self._record_nft_mint(
            network=network,
            token_standard=token_standard,
            token_id=token_id,
            contract_address=f"0x{uuid.uuid4().hex[:40]}",
            transaction_hash=tx_hash,
            user_id=user_id,
            mint_request=mint_request,
            simulated=True
        )
        
        return {
            'success': True,
            'transaction_hash': tx_hash,
            'token_id': token_id,
            'contract_address': f"0x{uuid.uuid4().hex[:40]}",
            'network': network,
            'token_standard': token_standard,
            'royalty_recipients': len(mint_request.royalty_recipients),
            'simulated': True
        }

    async def _simulate_dao_proposal(
        self,
        network: str,
        proposal_request: DAOProposalRequest,
        proposer_user_id: str
    ) -> Dict[str, Any]:
        """Simulate DAO proposal creation for development/testing"""
        
        proposal_id = int(datetime.now().timestamp() * 1000) % 1000000
        tx_hash = f"0x{uuid.uuid4().hex}"
        
        # Record simulated proposal in database
        await self._record_dao_proposal(
            network=network,
            proposal_id=proposal_id,
            proposal_type=proposal_request.proposal_type,
            title=proposal_request.title,
            description=proposal_request.description,
            proposer_user_id=proposer_user_id,
            transaction_hash=tx_hash,
            voting_period=proposal_request.voting_period,
            proposal_data=proposal_request.proposal_data,
            simulated=True
        )
        
        return {
            'success': True,
            'proposal_id': proposal_id,
            'transaction_hash': tx_hash,
            'network': network,
            'proposal_type': proposal_request.proposal_type,
            'voting_period': proposal_request.voting_period,
            'simulated': True
        }

    async def _record_nft_mint(
        self,
        network: str,
        token_standard: str,
        token_id: int,
        contract_address: str,
        transaction_hash: str,
        user_id: str,
        mint_request: NFTMintRequest,
        simulated: bool = False
    ):
        """Record NFT mint in database"""
        
        if not self.mongo_db:
            return

        try:
            nft_record = {
                'id': str(uuid.uuid4()),
                'network': network,
                'token_standard': token_standard,
                'token_id': token_id,
                'contract_address': contract_address,
                'transaction_hash': transaction_hash,
                'user_id': user_id,
                'recipient_address': mint_request.to_address,
                'token_uri': mint_request.token_uri,
                'license_terms': {
                    'license_type': mint_request.license_type,
                    'duration': mint_request.duration,
                    'restrictions': mint_request.restrictions,
                    'commercial_use': mint_request.commercial_use,
                    'max_resolution': mint_request.max_resolution,
                    'base_pricing': str(mint_request.base_pricing)
                },
                'royalty_recipients': [
                    {
                        'address': r.address,
                        'percentage': r.percentage,
                        'role': r.role
                    } for r in mint_request.royalty_recipients
                ],
                'minted_at': datetime.now(timezone.utc),
                'simulated': simulated
            }
            
            await self.mongo_db.nft_licenses.insert_one(nft_record)
            logger.info(f"Recorded NFT mint: {token_id} on {network}")
            
        except Exception as e:
            logger.error(f"Failed to record NFT mint: {str(e)}")

    async def _record_dao_proposal(
        self,
        network: str,
        proposal_id: int,
        proposal_type: str,
        title: str,
        description: str,
        proposer_user_id: str,
        transaction_hash: str,
        voting_period: int,
        proposal_data: Dict[str, Any],
        simulated: bool = False
    ):
        """Record DAO proposal in database"""
        
        if not self.mongo_db:
            return

        try:
            proposal_record = {
                'id': str(uuid.uuid4()),
                'proposal_id': proposal_id,
                'network': network,
                'proposal_type': proposal_type,
                'title': title,
                'description': description,
                'proposer_user_id': proposer_user_id,
                'transaction_hash': transaction_hash,
                'voting_period_days': voting_period,
                'proposal_data': proposal_data,
                'status': 'active',
                'votes_for': 0,
                'votes_against': 0,
                'votes_abstain': 0,
                'created_at': datetime.now(timezone.utc),
                'voting_deadline': datetime.now(timezone.utc).replace(
                    day=datetime.now(timezone.utc).day + voting_period
                ),
                'simulated': simulated
            }
            
            await self.mongo_db.dao_proposals.insert_one(proposal_record)
            logger.info(f"Recorded DAO proposal: {proposal_id} on {network}")
            
        except Exception as e:
            logger.error(f"Failed to record DAO proposal: {str(e)}")

    async def get_user_nfts(self, user_id: str, network: str = None) -> List[Dict[str, Any]]:
        """Get user's minted NFTs"""
        
        if self.mongo_db is None:
            return []

        try:
            query = {'user_id': user_id}
            if network:
                query['network'] = network

            nfts = []
            async for nft in self.mongo_db.nft_licenses.find(query).sort('minted_at', -1):
                nfts.append({
                    'id': nft['id'],
                    'network': nft['network'],
                    'token_standard': nft['token_standard'],
                    'token_id': nft['token_id'],
                    'contract_address': nft['contract_address'],
                    'transaction_hash': nft['transaction_hash'],
                    'recipient_address': nft['recipient_address'],
                    'license_terms': nft['license_terms'],
                    'royalty_recipients': nft['royalty_recipients'],
                    'minted_at': nft['minted_at'].isoformat(),
                    'simulated': nft.get('simulated', False)
                })

            return nfts
            
        except Exception as e:
            logger.error(f"Failed to get user NFTs: {str(e)}")
            return []

    async def get_dao_proposals(self, network: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Get DAO proposals"""
        
        if self.mongo_db is None:
            return []

        try:
            query = {}
            if network:
                query['network'] = network
            if status:
                query['status'] = status

            proposals = []
            async for proposal in self.mongo_db.dao_proposals.find(query).sort('created_at', -1):
                proposals.append({
                    'id': proposal['id'],
                    'proposal_id': proposal['proposal_id'],
                    'network': proposal['network'],
                    'proposal_type': proposal['proposal_type'],
                    'title': proposal['title'],
                    'description': proposal['description'],
                    'status': proposal['status'],
                    'votes_for': proposal['votes_for'],
                    'votes_against': proposal['votes_against'],
                    'votes_abstain': proposal['votes_abstain'],
                    'voting_period_days': proposal['voting_period_days'],
                    'created_at': proposal['created_at'].isoformat(),
                    'voting_deadline': proposal['voting_deadline'].isoformat(),
                    'simulated': proposal.get('simulated', False)
                })

            return proposals
            
        except Exception as e:
            logger.error(f"Failed to get DAO proposals: {str(e)}")
            return []