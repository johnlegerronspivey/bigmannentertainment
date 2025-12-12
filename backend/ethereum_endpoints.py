"""
Ethereum Connection and Utility Endpoints
Provides endpoints to test Ethereum connection and check wallet balances
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from web3 import Web3
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ethereum", tags=["ethereum"])

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

class WalletBalanceRequest(BaseModel):
    address: str

class WalletBalanceResponse(BaseModel):
    success: bool
    address: str
    balance_wei: Optional[str] = None
    balance_eth: Optional[str] = None
    network: Optional[str] = None
    error: Optional[str] = None

class ConnectionStatusResponse(BaseModel):
    success: bool
    connected: bool
    network: Optional[str] = None
    chain_id: Optional[int] = None
    block_number: Optional[int] = None
    rpc_url_preview: Optional[str] = None
    wallet_address: Optional[str] = None
    error: Optional[str] = None

@router.get("/connection-status", response_model=ConnectionStatusResponse)
async def get_connection_status():
    """
    Check Ethereum connection status
    """
    try:
        w3 = get_web3_connection()
        
        if not w3:
            return ConnectionStatusResponse(
                success=False,
                connected=False,
                error="Web3 connection not initialized"
            )
        
        is_connected = w3.is_connected()
        
        if not is_connected:
            return ConnectionStatusResponse(
                success=False,
                connected=False,
                error="Unable to connect to Ethereum network"
            )
        
        # Get network information
        chain_id = w3.eth.chain_id
        block_number = w3.eth.block_number
        network = os.getenv('ETHEREUM_NETWORK', 'unknown')
        rpc_url = os.getenv('ETHEREUM_RPC_URL', '')
        wallet_address = os.getenv('ETHEREUM_WALLET_ADDRESS')
        
        # Preview RPC URL (hide sensitive parts)
        rpc_preview = rpc_url[:50] + "..." if len(rpc_url) > 50 else rpc_url
        
        return ConnectionStatusResponse(
            success=True,
            connected=True,
            network=network,
            chain_id=chain_id,
            block_number=block_number,
            rpc_url_preview=rpc_preview,
            wallet_address=wallet_address
        )
        
    except Exception as e:
        logger.error(f"Error checking connection status: {e}")
        return ConnectionStatusResponse(
            success=False,
            connected=False,
            error=str(e)
        )

@router.post("/wallet-balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(request: WalletBalanceRequest):
    """
    Get ETH balance for a wallet address
    """
    try:
        w3 = get_web3_connection()
        
        if not w3 or not w3.is_connected():
            raise HTTPException(
                status_code=503,
                detail="Ethereum connection not available"
            )
        
        # Validate address
        if not Web3.is_address(request.address):
            raise HTTPException(
                status_code=400,
                detail="Invalid Ethereum address"
            )
        
        # Convert to checksum address
        address = Web3.to_checksum_address(request.address)
        
        # Get balance
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        network = os.getenv('ETHEREUM_NETWORK', 'unknown')
        
        return WalletBalanceResponse(
            success=True,
            address=address,
            balance_wei=str(balance_wei),
            balance_eth=str(balance_eth),
            network=network
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wallet balance: {str(e)}"
        )

@router.get("/configured-wallet", response_model=WalletBalanceResponse)
async def get_configured_wallet_balance():
    """
    Get balance for the configured wallet address
    """
    try:
        wallet_address = os.getenv('ETHEREUM_WALLET_ADDRESS')
        
        if not wallet_address:
            raise HTTPException(
                status_code=400,
                detail="No wallet address configured"
            )
        
        return await get_wallet_balance(WalletBalanceRequest(address=wallet_address))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting configured wallet balance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wallet balance: {str(e)}"
        )

@router.get("/transaction/{tx_hash}")
async def get_transaction_info(tx_hash: str):
    """
    Get information about a transaction
    """
    try:
        w3 = get_web3_connection()
        
        if not w3 or not w3.is_connected():
            raise HTTPException(
                status_code=503,
                detail="Ethereum connection not available"
            )
        
        # Get transaction
        try:
            tx = w3.eth.get_transaction(tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction not found: {str(e)}"
            )
        
        return {
            "success": True,
            "transaction_hash": tx_hash,
            "from_address": tx['from'],
            "to_address": tx['to'],
            "value_wei": str(tx['value']),
            "value_eth": str(w3.from_wei(tx['value'], 'ether')),
            "gas": tx['gas'],
            "gas_price": str(tx['gasPrice']),
            "block_number": tx['blockNumber'],
            "status": receipt['status'] if receipt else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transaction: {str(e)}"
        )

@router.get("/capabilities")
async def get_wallet_capabilities():
    """
    Check what capabilities are available (read-only vs transaction signing)
    """
    try:
        private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
        wallet_address = os.getenv('ETHEREUM_WALLET_ADDRESS')
        
        has_private_key = bool(private_key and private_key != '')
        
        capabilities = {
            "read_operations": True,
            "transaction_signing": has_private_key,
            "wallet_configured": bool(wallet_address),
            "features": {
                "view_balance": True,
                "view_transactions": True,
                "send_transactions": has_private_key,
                "deploy_contracts": has_private_key,
                "sign_messages": has_private_key
            }
        }
        
        return {
            "success": True,
            "capabilities": capabilities,
            "mode": "full" if has_private_key else "read-only"
        }
        
    except Exception as e:
        logger.error(f"Error checking capabilities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check capabilities: {str(e)}"
        )

@router.post("/sign-message")
async def sign_message(message: str):
    """
    Sign a message with the configured private key (proof that we can sign)
    """
    try:
        private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
        
        if not private_key:
            raise HTTPException(
                status_code=400,
                detail="Private key not configured. Cannot sign messages."
            )
        
        w3 = get_web3_connection()
        
        if not w3 or not w3.is_connected():
            raise HTTPException(
                status_code=503,
                detail="Ethereum connection not available"
            )
        
        # Import Account for signing
        from eth_account import Account
        from eth_account.messages import encode_defunct
        
        # Create account from private key
        account = Account.from_key(private_key)
        
        # Create message to sign
        message_to_sign = encode_defunct(text=message)
        
        # Sign the message
        signed_message = account.sign_message(message_to_sign)
        
        return {
            "success": True,
            "message": message,
            "signature": signed_message.signature.hex(),
            "signer_address": account.address,
            "v": signed_message.v,
            "r": signed_message.r.to_bytes(32, 'big').hex(),
            "s": signed_message.s.to_bytes(32, 'big').hex()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error signing message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sign message: {str(e)}"
        )
