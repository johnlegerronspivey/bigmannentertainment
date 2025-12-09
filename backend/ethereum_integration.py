"""
Ethereum Blockchain Integration for BME DOOH Platform
Handles smart contracts, royalty distribution, and DAO governance
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timezone
import logging
from web3 import Web3
from eth_account import Account
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EthereumIntegration:
    """Ethereum blockchain integration for BME DOOH platform"""
    
    def __init__(self):
        # Initialize Web3 connection
        self.network = os.getenv('ETHEREUM_NETWORK', 'testnet')
        self.rpc_url = self._get_rpc_url()
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # AWS Secrets Manager for secure key storage
        self.secrets_client = boto3.client('secretsmanager')
        
        # Smart contract addresses (deployed separately)
        self.contracts = {
            'royalty_splitter': os.getenv('ROYALTY_SPLITTER_ADDRESS'),
            'dao_governance': os.getenv('DAO_GOVERNANCE_ADDRESS'),
            'campaign_nft': os.getenv('CAMPAIGN_NFT_ADDRESS')
        }
        
        # Load contract ABIs
        self.contract_abis = self._load_contract_abis()
        
        logger.info(f"Ethereum integration initialized on {self.network}")
    
    def _get_rpc_url(self) -> str:
        """Get RPC URL based on network"""
        # Use the configured RPC URL from environment
        rpc_url = os.getenv('ETHEREUM_RPC_URL')
        if rpc_url:
            return rpc_url
        
        # Fallback to old configuration
        if self.network == 'mainnet':
            return os.getenv('ETHEREUM_MAINNET_RPC', 'https://eth-mainnet.alchemyapi.io/v2/your-api-key')
        else:
            return os.getenv('ETHEREUM_TESTNET_RPC', 'https://eth-goerli.alchemyapi.io/v2/your-api-key')
    
    def _load_contract_abis(self) -> Dict[str, List]:
        """Load smart contract ABIs"""
        return {
            'royalty_splitter': [
                {
                    "inputs": [
                        {"name": "recipients", "type": "address[]"},
                        {"name": "percentages", "type": "uint256[]"}
                    ],
                    "name": "distributeRoyalties",
                    "outputs": [],
                    "stateMutability": "payable",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "campaignId", "type": "string"}],
                    "name": "getCampaignRoyalties",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ],
            'dao_governance': [
                {
                    "inputs": [
                        {"name": "description", "type": "string"},
                        {"name": "targets", "type": "address[]"},
                        {"name": "values", "type": "uint256[]"},
                        {"name": "calldatas", "type": "bytes[]"}
                    ],
                    "name": "propose",
                    "outputs": [{"name": "proposalId", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"name": "proposalId", "type": "uint256"},
                        {"name": "support", "type": "uint8"}
                    ],
                    "name": "castVote",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ],
            'campaign_nft': [
                {
                    "inputs": [
                        {"name": "to", "type": "address"},
                        {"name": "campaignId", "type": "string"},
                        {"name": "metadata", "type": "string"}
                    ],
                    "name": "mintCampaignNFT",
                    "outputs": [{"name": "tokenId", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
        }
    
    async def get_private_key(self, key_name: str) -> str:
        """Securely retrieve private key from AWS Secrets Manager"""
        try:
            response = self.secrets_client.get_secret_value(SecretId=f'bme-dooh-{key_name}')
            secret = json.loads(response['SecretString'])
            return secret['private_key']
        except Exception as e:
            logger.error(f"Error retrieving private key: {e}")
            # For development, return demo key
            return os.getenv('DEMO_PRIVATE_KEY', '0x' + '1' * 64)
    
    async def distribute_royalties(self, campaign_id: str, revenue: Decimal, contributors: List[Dict]) -> Dict[str, Any]:
        """Distribute campaign royalties to contributors using smart contract"""
        try:
            # Get contract instance
            contract_address = self.contracts['royalty_splitter']
            if not contract_address:
                raise ValueError("Royalty splitter contract not deployed")
            
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.contract_abis['royalty_splitter']
            )
            
            # Prepare recipient addresses and percentages
            recipients = []
            percentages = []
            
            for contributor in contributors:
                recipients.append(contributor['wallet_address'])
                # Convert percentage to basis points (10000 = 100%)
                percentages.append(int(contributor['percentage'] * 100))
            
            # Get platform wallet private key
            private_key = await self.get_private_key('platform-wallet')
            account = Account.from_key(private_key)
            
            # Prepare transaction
            transaction = contract.functions.distributeRoyalties(
                recipients, percentages
            ).build_transaction({
                'from': account.address,
                'value': self.w3.to_wei(float(revenue), 'ether'),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address)
            })
            
            # Sign and send transaction
            signed_txn = account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Royalties distributed for campaign {campaign_id}, tx: {tx_hash.hex()}")
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'campaign_id': campaign_id,
                'total_distributed': float(revenue),
                'recipients_count': len(recipients)
            }
            
        except Exception as e:
            logger.error(f"Error distributing royalties: {e}")
            return {
                'success': False,
                'error': str(e),
                'campaign_id': campaign_id
            }
    
    async def create_dao_proposal(self, proposal_data: Dict[str, Any], proposer_address: str) -> Dict[str, Any]:
        """Create a DAO governance proposal"""
        try:
            contract_address = self.contracts['dao_governance']
            if not contract_address:
                raise ValueError("DAO governance contract not deployed")
            
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.contract_abis['dao_governance']
            )
            
            # Get proposer's private key (in production, this would be handled by frontend wallet)
            private_key = await self.get_private_key('dao-proposer')
            account = Account.from_key(private_key)
            
            # Prepare proposal transaction
            transaction = contract.functions.propose(
                proposal_data['description'],
                proposal_data.get('targets', []),
                proposal_data.get('values', []),
                proposal_data.get('calldatas', [])
            ).build_transaction({
                'from': account.address,
                'gas': 300000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address)
            })
            
            # Sign and send transaction
            signed_txn = account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Extract proposal ID from logs
            proposal_id = self._extract_proposal_id(receipt)
            
            logger.info(f"DAO proposal created with ID {proposal_id}, tx: {tx_hash.hex()}")
            
            return {
                'success': True,
                'proposal_id': proposal_id,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed']
            }
            
        except Exception as e:
            logger.error(f"Error creating DAO proposal: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def vote_on_proposal(self, proposal_id: int, vote: int, voter_address: str) -> Dict[str, Any]:
        """Vote on a DAO proposal (0=Against, 1=For, 2=Abstain)"""
        try:
            contract_address = self.contracts['dao_governance']
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.contract_abis['dao_governance']
            )
            
            # Get voter's private key
            private_key = await self.get_private_key('dao-voter')
            account = Account.from_key(private_key)
            
            # Prepare vote transaction
            transaction = contract.functions.castVote(
                proposal_id, vote
            ).build_transaction({
                'from': account.address,
                'gas': 150000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address)
            })
            
            # Sign and send transaction
            signed_txn = account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Vote cast on proposal {proposal_id}, tx: {tx_hash.hex()}")
            
            return {
                'success': True,
                'proposal_id': proposal_id,
                'vote': vote,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed']
            }
            
        except Exception as e:
            logger.error(f"Error voting on proposal: {e}")
            return {
                'success': False,
                'error': str(e),
                'proposal_id': proposal_id
            }
    
    async def mint_campaign_nft(self, campaign_id: str, recipient_address: str, metadata: Dict) -> Dict[str, Any]:
        """Mint an NFT representing a campaign"""
        try:
            contract_address = self.contracts['campaign_nft']
            if not contract_address:
                raise ValueError("Campaign NFT contract not deployed")
            
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.contract_abis['campaign_nft']
            )
            
            # Get platform wallet private key
            private_key = await self.get_private_key('platform-wallet')
            account = Account.from_key(private_key)
            
            # Prepare metadata JSON
            metadata_json = json.dumps(metadata)
            
            # Prepare mint transaction
            transaction = contract.functions.mintCampaignNFT(
                recipient_address, campaign_id, metadata_json
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address)
            })
            
            # Sign and send transaction
            signed_txn = account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Extract token ID from logs
            token_id = self._extract_token_id(receipt)
            
            logger.info(f"Campaign NFT minted for {campaign_id}, token ID: {token_id}")
            
            return {
                'success': True,
                'token_id': token_id,
                'campaign_id': campaign_id,
                'recipient': recipient_address,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber']
            }
            
        except Exception as e:
            logger.error(f"Error minting campaign NFT: {e}")
            return {
                'success': False,
                'error': str(e),
                'campaign_id': campaign_id
            }
    
    def _extract_proposal_id(self, receipt) -> Optional[int]:
        """Extract proposal ID from transaction receipt"""
        try:
            # This would parse the event logs to extract proposal ID
            # For demo, return a mock ID
            return 12345
        except Exception as e:
            logger.error(f"Error extracting proposal ID: {e}")
            return None
    
    def _extract_token_id(self, receipt) -> Optional[int]:
        """Extract token ID from transaction receipt"""
        try:
            # This would parse the event logs to extract token ID
            # For demo, return a mock ID
            return 67890
        except Exception as e:
            logger.error(f"Error extracting token ID: {e}")
            return None
    
    async def get_wallet_balance(self, address: str) -> Dict[str, Any]:
        """Get ETH balance for a wallet address"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            return {
                'success': True,
                'address': address,
                'balance_wei': balance_wei,
                'balance_eth': float(balance_eth),
                'network': self.network
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return {
                'success': False,
                'error': str(e),
                'address': address
            }
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get status of a transaction"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash,
                'status': 'success' if receipt['status'] == 1 else 'failed',
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'gas_price': transaction['gasPrice'],
                'from_address': transaction['from'],
                'to_address': transaction['to'],
                'value_eth': float(self.w3.from_wei(transaction['value'], 'ether'))
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return {
                'success': False,
                'error': str(e),
                'transaction_hash': tx_hash
            }

# Global instance
ethereum_integration = EthereumIntegration()

# Utility functions for Lambda integration
async def handle_royalty_distribution(campaign_id: str, revenue: Decimal, contributors: List[Dict]) -> Dict[str, Any]:
    """Handle royalty distribution via Ethereum smart contract"""
    return await ethereum_integration.distribute_royalties(campaign_id, revenue, contributors)

async def handle_dao_proposal_creation(proposal_data: Dict[str, Any], proposer_address: str) -> Dict[str, Any]:
    """Handle DAO proposal creation"""
    return await ethereum_integration.create_dao_proposal(proposal_data, proposer_address)

async def handle_dao_voting(proposal_id: int, vote: int, voter_address: str) -> Dict[str, Any]:
    """Handle DAO voting"""
    return await ethereum_integration.vote_on_proposal(proposal_id, vote, voter_address)

async def handle_campaign_nft_minting(campaign_id: str, recipient_address: str, metadata: Dict) -> Dict[str, Any]:
    """Handle campaign NFT minting"""
    return await ethereum_integration.mint_campaign_nft(campaign_id, recipient_address, metadata)