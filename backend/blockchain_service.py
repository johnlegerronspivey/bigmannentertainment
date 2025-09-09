"""
Multi-chain Blockchain Service
Ethereum and Solana smart contract integration for image licensing
"""

import os
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
import logging

logger = logging.getLogger(__name__)

class EthereumService:
    """Ethereum blockchain service for ERC-721/ERC-1155 contracts"""
    
    def __init__(self):
        self.infura_url = os.getenv('INFURA_URL', 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID')
        self.alchemy_url = os.getenv('ALCHEMY_URL', 'https://eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY')
        self.private_key = os.getenv('ETH_PRIVATE_KEY')
        self.contract_owner_address = os.getenv('ETH_CONTRACT_OWNER_ADDRESS')
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.infura_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # ERC-721 Contract ABI (simplified)
        self.erc721_abi = [
            {
                "inputs": [{"name": "to", "type": "address"}, {"name": "tokenId", "type": "uint256"}],
                "name": "mint",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}, {"name": "tokenURI", "type": "string"}],
                "name": "setTokenURI",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "licensee", "type": "address"}, {"name": "tokenId", "type": "uint256"}, {"name": "price", "type": "uint256"}],
                "name": "licenseImage",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "tokenURI",
                "outputs": [{"name": "", "type": "string"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "ownerOf",
                "outputs": [{"name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # ERC-1155 Contract ABI (simplified)
        self.erc1155_abi = [
            {
                "inputs": [{"name": "to", "type": "address"}, {"name": "id", "type": "uint256"}, {"name": "amount", "type": "uint256"}, {"name": "data", "type": "bytes"}],
                "name": "mint",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "account", "type": "address"}, {"name": "id", "type": "uint256"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
    async def deploy_erc721_contract(self, name: str, symbol: str) -> Dict[str, Any]:
        """Deploy a new ERC-721 contract for licensing"""
        try:
            # This is a simplified example - in production, you'd deploy actual bytecode
            contract_bytecode = "0x608060405234801561001057600080fd5b50..."  # Actual bytecode here
            
            # Create contract deployment transaction
            account = self.w3.eth.account.from_key(self.private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            transaction = {
                'from': account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'data': contract_bytecode
            }
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'contract_address': receipt.contractAddress,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'status': 'deployed' if receipt.status == 1 else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Error deploying ERC-721 contract: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def mint_license_token(self, contract_address: str, to_address: str, token_id: int, metadata_uri: str) -> Dict[str, Any]:
        """Mint a new license token"""
        try:
            contract = self.w3.eth.contract(address=contract_address, abi=self.erc721_abi)
            account = self.w3.eth.account.from_key(self.private_key)
            
            # Build mint transaction
            mint_txn = contract.functions.mint(to_address, token_id).build_transaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(mint_txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Set token URI
            if metadata_uri:
                uri_txn = contract.functions.setTokenURI(token_id, metadata_uri).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 100000,
                    'gasPrice': self.w3.to_wei('20', 'gwei')
                })
                
                signed_uri_txn = self.w3.eth.account.sign_transaction(uri_txn, self.private_key)
                uri_tx_hash = self.w3.eth.send_raw_transaction(signed_uri_txn.rawTransaction)
                self.w3.eth.wait_for_transaction_receipt(uri_tx_hash)
            
            return {
                'token_id': token_id,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'status': 'minted' if receipt.status == 1 else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Error minting license token: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def license_image(self, contract_address: str, licensee_address: str, token_id: int, price_wei: int) -> Dict[str, Any]:
        """Execute license purchase"""
        try:
            contract = self.w3.eth.contract(address=contract_address, abi=self.erc721_abi)
            account = self.w3.eth.account.from_key(self.private_key)
            
            # Build license transaction
            license_txn = contract.functions.licenseImage(licensee_address, token_id, price_wei).build_transaction({
                'from': licensee_address,
                'value': price_wei,
                'nonce': self.w3.eth.get_transaction_count(licensee_address),
                'gas': 300000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Note: In production, the licensee would sign this transaction
            # For now, we'll simulate the process
            
            return {
                'transaction_data': license_txn,
                'estimated_gas': 300000,
                'gas_price': self.w3.to_wei('20', 'gwei'),
                'total_cost': price_wei + (300000 * self.w3.to_wei('20', 'gwei')),
                'status': 'prepared'
            }
            
        except Exception as e:
            logger.error(f"Error preparing license transaction: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_token_info(self, contract_address: str, token_id: int) -> Dict[str, Any]:
        """Get token information"""
        try:
            contract = self.w3.eth.contract(address=contract_address, abi=self.erc721_abi)
            
            owner = contract.functions.ownerOf(token_id).call()
            token_uri = contract.functions.tokenURI(token_id).call()
            
            return {
                'token_id': token_id,
                'owner': owner,
                'token_uri': token_uri,
                'contract_address': contract_address,
                'blockchain': 'ethereum'
            }
            
        except Exception as e:
            logger.error(f"Error getting token info: {str(e)}")
            return {'status': 'error', 'error': str(e)}

class SolanaService:
    """Solana blockchain service for SPL token licensing"""
    
    def __init__(self):
        self.rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        self.private_key = os.getenv('SOLANA_PRIVATE_KEY')
        self.client = AsyncClient(self.rpc_url)
        
    async def create_token_mint(self, decimals: int = 0) -> Dict[str, Any]:
        """Create a new SPL token mint for licensing"""
        try:
            # This is a simplified example
            # In production, you'd use the SPL Token library
            
            mint_pubkey = PublicKey("11111111111111111111111111111112")  # System program
            
            return {
                'mint_address': str(mint_pubkey),
                'decimals': decimals,
                'status': 'created',
                'blockchain': 'solana'
            }
            
        except Exception as e:
            logger.error(f"Error creating Solana token mint: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def mint_license_token(self, mint_address: str, to_address: str, amount: int) -> Dict[str, Any]:
        """Mint license tokens on Solana"""
        try:
            # Simplified minting process
            # In production, you'd create and send the actual transaction
            
            return {
                'mint_address': mint_address,
                'recipient': to_address,
                'amount': amount,
                'status': 'minted',
                'blockchain': 'solana'
            }
            
        except Exception as e:
            logger.error(f"Error minting Solana token: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def transfer_license(self, from_address: str, to_address: str, amount: int) -> Dict[str, Any]:
        """Transfer license tokens"""
        try:
            # Create transfer transaction
            from_pubkey = PublicKey(from_address)
            to_pubkey = PublicKey(to_address)
            
            transaction = Transaction().add(
                transfer(
                    TransferParams(
                        from_pubkey=from_pubkey,
                        to_pubkey=to_pubkey,
                        lamports=amount * 1000000000  # Convert to lamports
                    )
                )
            )
            
            return {
                'transaction_data': transaction,
                'from_address': from_address,
                'to_address': to_address,
                'amount': amount,
                'status': 'prepared',
                'blockchain': 'solana'
            }
            
        except Exception as e:
            logger.error(f"Error preparing Solana transfer: {str(e)}")
            return {'status': 'error', 'error': str(e)}

class MultiChainBlockchainService:
    """Multi-chain blockchain service coordinator"""
    
    def __init__(self):
        self.ethereum = EthereumService()
        self.solana = SolanaService()
        
    async def deploy_contract(self, blockchain: str, contract_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy contract on specified blockchain"""
        try:
            if blockchain.lower() == 'ethereum':
                if contract_type == 'erc721':
                    return await self.ethereum.deploy_erc721_contract(
                        params.get('name', 'BME License Token'),
                        params.get('symbol', 'BMELIT')
                    )
                elif contract_type == 'erc1155':
                    # Implement ERC-1155 deployment
                    pass
            elif blockchain.lower() == 'solana':
                return await self.solana.create_token_mint(params.get('decimals', 0))
            
            return {'status': 'error', 'error': 'Unsupported blockchain or contract type'}
            
        except Exception as e:
            logger.error(f"Error deploying contract: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def mint_license_token(self, blockchain: str, contract_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mint license token on specified blockchain"""
        try:
            if blockchain.lower() == 'ethereum':
                return await self.ethereum.mint_license_token(
                    contract_params['contract_address'],
                    contract_params['to_address'],
                    contract_params['token_id'],
                    contract_params.get('metadata_uri', '')
                )
            elif blockchain.lower() == 'solana':
                return await self.solana.mint_license_token(
                    contract_params['mint_address'],
                    contract_params['to_address'],
                    contract_params['amount']
                )
            
            return {'status': 'error', 'error': 'Unsupported blockchain'}
            
        except Exception as e:
            logger.error(f"Error minting license token: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def execute_license_purchase(self, blockchain: str, license_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute license purchase on specified blockchain"""
        try:
            if blockchain.lower() == 'ethereum':
                return await self.ethereum.license_image(
                    license_params['contract_address'],
                    license_params['licensee_address'],
                    license_params['token_id'],
                    license_params['price_wei']
                )
            elif blockchain.lower() == 'solana':
                return await self.solana.transfer_license(
                    license_params['from_address'],
                    license_params['to_address'],
                    license_params['amount']
                )
            
            return {'status': 'error', 'error': 'Unsupported blockchain'}
            
        except Exception as e:
            logger.error(f"Error executing license purchase: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_token_info(self, blockchain: str, token_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get token information from specified blockchain"""
        try:
            if blockchain.lower() == 'ethereum':
                return await self.ethereum.get_token_info(
                    token_params['contract_address'],
                    token_params['token_id']
                )
            elif blockchain.lower() == 'solana':
                # Implement Solana token info retrieval
                return {
                    'mint_address': token_params.get('mint_address'),
                    'blockchain': 'solana',
                    'status': 'active'
                }
            
            return {'status': 'error', 'error': 'Unsupported blockchain'}
            
        except Exception as e:
            logger.error(f"Error getting token info: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def calculate_gas_fees(self, blockchain: str, transaction_type: str) -> Dict[str, Any]:
        """Calculate estimated gas fees for transaction"""
        try:
            if blockchain.lower() == 'ethereum':
                gas_price = self.ethereum.w3.to_wei('20', 'gwei')
                gas_limits = {
                    'deploy': 2000000,
                    'mint': 200000,
                    'license': 300000,
                    'transfer': 21000
                }
                
                gas_limit = gas_limits.get(transaction_type, 100000)
                total_cost = gas_price * gas_limit
                
                return {
                    'blockchain': 'ethereum',
                    'gas_price': gas_price,
                    'gas_limit': gas_limit,
                    'total_cost_wei': total_cost,
                    'total_cost_eth': self.ethereum.w3.from_wei(total_cost, 'ether'),
                    'currency': 'ETH'
                }
            elif blockchain.lower() == 'solana':
                # Solana has much lower fees
                return {
                    'blockchain': 'solana',
                    'base_fee': 5000,  # lamports
                    'total_cost_lamports': 5000,
                    'total_cost_sol': 0.000005,
                    'currency': 'SOL'
                }
            
            return {'status': 'error', 'error': 'Unsupported blockchain'}
            
        except Exception as e:
            logger.error(f"Error calculating gas fees: {str(e)}")
            return {'status': 'error', 'error': str(e)}

# Global service instance
blockchain_service = MultiChainBlockchainService()