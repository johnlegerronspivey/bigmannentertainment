"""
Blockchain Smart Contracts for Royalty Engine
Ethereum/Polygon smart contract integration for immutable royalty calculations
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from decimal import Decimal
import os
import uuid
from web3 import Web3
from eth_account import Account
import hashlib

logger = logging.getLogger(__name__)

# Smart Contract ABI (Application Binary Interface)
ROYALTY_CONTRACT_ABI = [
    {
        "inputs": [
            {"name": "assetId", "type": "string"},
            {"name": "transactionId", "type": "string"},
            {"name": "grossRevenue", "type": "uint256"},
            {"name": "contributors", "type": "address[]"},
            {"name": "splitPercentages", "type": "uint256[]"}
        ],
        "name": "calculateRoyalties",
        "outputs": [{"name": "calculationId", "type": "string"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "calculationId", "type": "string"}],
        "name": "getRoyaltyCalculation",
        "outputs": [
            {"name": "assetId", "type": "string"},
            {"name": "totalRoyalty", "type": "uint256"},
            {"name": "contributors", "type": "address[]"},
            {"name": "payouts", "type": "uint256[]"},
            {"name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "calculationId", "type": "string"},
            {"name": "contributor", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "executePayout",
        "outputs": [{"name": "success", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "assetId", "type": "string"},
            {"indexed": True, "name": "calculationId", "type": "string"},
            {"indexed": False, "name": "totalRoyalty", "type": "uint256"},
            {"indexed": False, "name": "timestamp", "type": "uint256"}
        ],
        "name": "RoyaltyCalculated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "contributor", "type": "address"},
            {"indexed": True, "name": "calculationId", "type": "string"},
            {"indexed": False, "name": "amount", "type": "uint256"},
            {"indexed": False, "name": "timestamp", "type": "uint256"}
        ],
        "name": "PayoutExecuted",
        "type": "event"
    }
]

# ERC-20 Token ABI for stablecoin payments
ERC20_ABI = [
    {
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class BlockchainConfig:
    """Blockchain network configuration"""
    
    # Ethereum Mainnet
    ETHEREUM_RPC_URL = os.getenv('ETHEREUM_RPC_URL', 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID')
    ETHEREUM_CHAIN_ID = 1
    
    # Polygon Mainnet (cheaper transactions)
    POLYGON_RPC_URL = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com/')
    POLYGON_CHAIN_ID = 137
    
    # Testnet URLs for development
    ETHEREUM_GOERLI_RPC_URL = os.getenv('ETHEREUM_GOERLI_RPC_URL', 'https://goerli.infura.io/v3/YOUR_PROJECT_ID')
    POLYGON_MUMBAI_RPC_URL = os.getenv('POLYGON_MUMBAI_RPC_URL', 'https://rpc-mumbai.maticvigil.com/')
    
    # Contract addresses (would be deployed contracts)
    ROYALTY_CONTRACT_ADDRESS = os.getenv('ROYALTY_CONTRACT_ADDRESS', '0x1234567890123456789012345678901234567890')
    USDC_CONTRACT_ADDRESS = os.getenv('USDC_CONTRACT_ADDRESS', '0xA0b86a33E6441E6C74E6E90c3f0C66E70F9c7826')
    
    # Private key for contract interactions (in production, use secure key management)
    PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '0x' + '0' * 64)  # Placeholder
    
    # Gas settings
    GAS_LIMIT = 500000
    GAS_PRICE_GWEI = 20

class BlockchainRoyaltyProcessor:
    """Blockchain integration for royalty processing"""
    
    def __init__(self, network: str = "polygon"):
        self.network = network
        self.config = BlockchainConfig()
        self.w3 = self._initialize_web3()
        self.account = Account.from_key(self.config.PRIVATE_KEY) if self.config.PRIVATE_KEY != ('0x' + '0' * 64) else None
        self.royalty_contract = None
        self.usdc_contract = None
        
        if self.w3 and self.w3.is_connected():
            self._initialize_contracts()
    
    def _initialize_web3(self) -> Optional[Web3]:
        """Initialize Web3 connection"""
        try:
            if self.network == "ethereum":
                rpc_url = self.config.ETHEREUM_RPC_URL
            elif self.network == "polygon":
                rpc_url = self.config.POLYGON_RPC_URL
            else:
                rpc_url = self.config.POLYGON_RPC_URL  # Default to Polygon
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if w3.is_connected():
                logger.info(f"Connected to {self.network} blockchain")
                return w3
            else:
                logger.error(f"Failed to connect to {self.network} blockchain")
                return None
                
        except Exception as e:
            logger.error(f"Error initializing Web3: {e}")
            return None
    
    def _initialize_contracts(self):
        """Initialize smart contract instances"""
        try:
            self.royalty_contract = self.w3.eth.contract(
                address=self.config.ROYALTY_CONTRACT_ADDRESS,
                abi=ROYALTY_CONTRACT_ABI
            )
            
            self.usdc_contract = self.w3.eth.contract(
                address=self.config.USDC_CONTRACT_ADDRESS,
                abi=ERC20_ABI
            )
            
            logger.info("Smart contracts initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing contracts: {e}")
    
    async def calculate_royalties_on_chain(
        self,
        asset_id: str,
        transaction_id: str,
        gross_revenue: Decimal,
        contributors: List[str],  # Wallet addresses
        split_percentages: List[Decimal]
    ) -> Optional[str]:
        """Calculate royalties using blockchain smart contract"""
        
        if not self.w3 or not self.royalty_contract or not self.account:
            logger.error("Blockchain not properly initialized")
            return None
        
        try:
            # Convert revenue to Wei (assuming USDC with 6 decimals)
            revenue_wei = int(gross_revenue * Decimal('1000000'))
            
            # Convert percentages to integers (multiply by 100 for precision)
            percentages_int = [int(pct * 100) for pct in split_percentages]
            
            # Build transaction
            transaction = self.royalty_contract.functions.calculateRoyalties(
                asset_id,
                transaction_id,
                revenue_wei,
                contributors,
                percentages_int
            ).build_transaction({
                'chainId': self.config.POLYGON_CHAIN_ID if self.network == "polygon" else self.config.ETHEREUM_CHAIN_ID,
                'gas': self.config.GAS_LIMIT,
                'gasPrice': self.w3.to_wei(self.config.GAS_PRICE_GWEI, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.config.PRIVATE_KEY)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:  # Success
                logger.info(f"Royalty calculation successful. Tx hash: {tx_hash.hex()}")
                
                # Parse events to get calculation ID
                calculation_id = self._parse_royalty_calculated_event(receipt)
                return calculation_id
            else:
                logger.error(f"Royalty calculation failed. Tx hash: {tx_hash.hex()}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating royalties on-chain: {e}")
            return None
    
    def _parse_royalty_calculated_event(self, receipt) -> Optional[str]:
        """Parse RoyaltyCalculated event from transaction receipt"""
        try:
            # Get event logs
            events = self.royalty_contract.events.RoyaltyCalculated().process_receipt(receipt)
            
            if events:
                return events[0]['args']['calculationId']
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None
    
    async def execute_crypto_payout(
        self,
        recipient_address: str,
        amount: Decimal,
        calculation_id: str
    ) -> Optional[str]:
        """Execute cryptocurrency payout using smart contract"""
        
        if not self.w3 or not self.royalty_contract or not self.account:
            logger.error("Blockchain not properly initialized")
            return None
        
        try:
            # Convert amount to Wei (USDC has 6 decimals)
            amount_wei = int(amount * Decimal('1000000'))
            
            # Build transaction
            transaction = self.royalty_contract.functions.executePayout(
                calculation_id,
                recipient_address,
                amount_wei
            ).build_transaction({
                'chainId': self.config.POLYGON_CHAIN_ID if self.network == "polygon" else self.config.ETHEREUM_CHAIN_ID,
                'gas': self.config.GAS_LIMIT,
                'gasPrice': self.w3.to_wei(self.config.GAS_PRICE_GWEI, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.config.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Payout executed successfully. Tx hash: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"Payout execution failed. Tx hash: {tx_hash.hex()}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing payout: {e}")
            return None
    
    async def get_calculation_from_blockchain(self, calculation_id: str) -> Optional[Dict[str, Any]]:
        """Get royalty calculation data from blockchain"""
        
        if not self.w3 or not self.royalty_contract:
            return None
        
        try:
            result = self.royalty_contract.functions.getRoyaltyCalculation(calculation_id).call()
            
            return {
                "asset_id": result[0],
                "total_royalty": result[1],
                "contributors": result[2],
                "payouts": result[3],
                "timestamp": result[4]
            }
            
        except Exception as e:
            logger.error(f"Error getting calculation from blockchain: {e}")
            return None
    
    async def get_usdc_balance(self, address: str) -> Optional[Decimal]:
        """Get USDC balance for an address"""
        
        if not self.w3 or not self.usdc_contract:
            return None
        
        try:
            balance_wei = self.usdc_contract.functions.balanceOf(address).call()
            # USDC has 6 decimals
            balance = Decimal(balance_wei) / Decimal('1000000')
            return balance
            
        except Exception as e:
            logger.error(f"Error getting USDC balance: {e}")
            return None
    
    async def estimate_gas_cost(self, transaction_type: str) -> Optional[Dict[str, Any]]:
        """Estimate gas cost for different transaction types"""
        
        if not self.w3:
            return None
        
        try:
            current_gas_price = self.w3.eth.gas_price
            
            # Estimated gas usage for different operations
            gas_estimates = {
                "royalty_calculation": 200000,
                "payout_execution": 150000,
                "token_transfer": 21000
            }
            
            gas_limit = gas_estimates.get(transaction_type, 100000)
            estimated_cost_wei = current_gas_price * gas_limit
            estimated_cost_eth = self.w3.from_wei(estimated_cost_wei, 'ether')
            
            return {
                "gas_price_gwei": self.w3.from_wei(current_gas_price, 'gwei'),
                "gas_limit": gas_limit,
                "estimated_cost_wei": estimated_cost_wei,
                "estimated_cost_eth": float(estimated_cost_eth),
                "estimated_cost_usd": float(estimated_cost_eth) * 2000  # Rough ETH price estimate
            }
            
        except Exception as e:
            logger.error(f"Error estimating gas cost: {e}")
            return None

class HybridRoyaltyProcessor:
    """Hybrid processor that uses both database and blockchain"""
    
    def __init__(self):
        self.blockchain_processor = BlockchainRoyaltyProcessor()
        self.use_blockchain = self._should_use_blockchain()
    
    def _should_use_blockchain(self) -> bool:
        """Determine whether to use blockchain based on configuration and transaction value"""
        # Use blockchain for high-value transactions or if explicitly configured
        blockchain_enabled = os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
        return blockchain_enabled and self.blockchain_processor.w3 and self.blockchain_processor.w3.is_connected()
    
    async def process_royalty_calculation(
        self,
        asset_id: str,
        transaction_id: str,
        gross_revenue: Decimal,
        contributors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process royalty calculation using hybrid approach"""
        
        result = {
            "calculation_id": str(uuid.uuid4()),
            "blockchain_hash": None,
            "processing_method": "database"
        }
        
        # Use blockchain for high-value transactions (> $1000) or if explicitly enabled
        if self.use_blockchain and (gross_revenue > Decimal('1000') or os.getenv('FORCE_BLOCKCHAIN', 'false').lower() == 'true'):
            try:
                # Extract wallet addresses and percentages
                wallet_addresses = []
                split_percentages = []
                
                for contributor in contributors:
                    if contributor.get('wallet_address'):
                        wallet_addresses.append(contributor['wallet_address'])
                        split_percentages.append(Decimal(str(contributor['split_percentage'])))
                
                if wallet_addresses and split_percentages:
                    blockchain_calc_id = await self.blockchain_processor.calculate_royalties_on_chain(
                        asset_id,
                        transaction_id,
                        gross_revenue,
                        wallet_addresses,
                        split_percentages
                    )
                    
                    if blockchain_calc_id:
                        result["blockchain_hash"] = blockchain_calc_id
                        result["processing_method"] = "blockchain"
                        logger.info(f"Processed royalty calculation on blockchain: {blockchain_calc_id}")
                    else:
                        logger.warning("Blockchain processing failed, falling back to database")
                        
            except Exception as e:
                logger.error(f"Blockchain processing error: {e}, falling back to database")
        
        return result
    
    async def execute_payout(
        self,
        recipient_address: str,
        amount: Decimal,
        calculation_id: str,
        payout_method: str
    ) -> Dict[str, Any]:
        """Execute payout using appropriate method"""
        
        result = {
            "payout_id": str(uuid.uuid4()),
            "transaction_hash": None,
            "processing_method": "traditional"
        }
        
        # Use blockchain for crypto payouts
        if payout_method in ["crypto_instant", "stablecoin"] and self.use_blockchain and recipient_address:
            try:
                tx_hash = await self.blockchain_processor.execute_crypto_payout(
                    recipient_address,
                    amount,
                    calculation_id
                )
                
                if tx_hash:
                    result["transaction_hash"] = tx_hash
                    result["processing_method"] = "blockchain"
                    logger.info(f"Executed crypto payout on blockchain: {tx_hash}")
                else:
                    logger.warning("Blockchain payout failed, queuing for manual processing")
                    
            except Exception as e:
                logger.error(f"Blockchain payout error: {e}")
        
        return result
    
    async def get_gas_estimate(self, transaction_type: str) -> Optional[Dict[str, Any]]:
        """Get gas cost estimate for blockchain transactions"""
        if self.use_blockchain:
            return await self.blockchain_processor.estimate_gas_cost(transaction_type)
        return None
    
    async def get_blockchain_status(self) -> Dict[str, Any]:
        """Get blockchain integration status"""
        return {
            "blockchain_enabled": self.use_blockchain,
            "network": self.blockchain_processor.network,
            "connected": self.blockchain_processor.w3.is_connected() if self.blockchain_processor.w3 else False,
            "account_address": self.blockchain_processor.account.address if self.blockchain_processor.account else None,
            "contracts_initialized": bool(self.blockchain_processor.royalty_contract and self.blockchain_processor.usdc_contract)
        }

# Initialize hybrid processor
hybrid_processor = HybridRoyaltyProcessor()