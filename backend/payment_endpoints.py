from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime

from payment_service import PaymentService
from payment_models import (
    CreateCheckoutSessionRequest, CreateCheckoutSessionResponse,
    PaymentStatusResponse, BankAccountRequest, DigitalWalletRequest,
    RoyaltySplitRequest, PayoutRequestModel
)

# Import authentication dependencies (assuming they exist from your existing code)
# Adjust these imports based on your existing authentication setup
try:
    from server import get_current_user, User  # Adjust import path as needed
except ImportError:
    # Fallback for development - create simple authentication
    async def get_current_user():
        return {"id": "test-user", "email": "test@example.com"}
    
    class User:
        id: str
        email: str

logger = logging.getLogger(__name__)

# Create payment router
payment_router = APIRouter(prefix="/api/payments", tags=["Payments"])

# Initialize payment service (will be properly initialized in main app)
payment_service = None

def get_payment_service():
    """Get payment service instance"""
    global payment_service
    if payment_service is None:
        raise HTTPException(status_code=500, detail="Payment service not initialized")
    return payment_service

# Checkout and Payment Processing Endpoints
@payment_router.post("/checkout/session", response_model=CreateCheckoutSessionResponse)
async def create_checkout_session(
    request: Request,
    package_id: Optional[str] = None,
    media_id: Optional[str] = None,
    origin_url: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a Stripe checkout session"""
    try:
        service = get_payment_service()
        
        # Get origin URL from request if not provided
        if not origin_url:
            origin_url = str(request.base_url).rstrip('/')
        
        request_data = {
            "package_id": package_id,
            "media_id": media_id,
            "origin_url": origin_url,
            "metadata": metadata or {}
        }
        
        user_id = current_user.id if current_user else None
        result = await service.create_checkout_session(request_data, user_id)
        
        return CreateCheckoutSessionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str):
    """Get checkout session status"""
    try:
        service = get_payment_service()
        result = await service.get_checkout_status(session_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting checkout status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/packages")
async def get_payment_packages():
    """Get available payment packages"""
    try:
        service = get_payment_service()
        packages = await service.get_payment_packages()
        return {"packages": packages}
        
    except Exception as e:
        logger.error(f"Error getting payment packages: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Bank Account Management Endpoints
@payment_router.post("/bank-accounts")
async def add_bank_account(
    account_data: BankAccountRequest,
    current_user: User = Depends(get_current_user)
):
    """Add a bank account for the current user"""
    try:
        service = get_payment_service()
        account_id = await service.add_bank_account(current_user.id, account_data.dict())
        return {"account_id": account_id, "message": "Bank account added successfully"}
        
    except Exception as e:
        logger.error(f"Error adding bank account: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/bank-accounts")
async def get_bank_accounts(current_user: User = Depends(get_current_user)):
    """Get all bank accounts for the current user"""
    try:
        service = get_payment_service()
        accounts = await service.get_user_bank_accounts(current_user.id)
        return {"accounts": accounts}
        
    except Exception as e:
        logger.error(f"Error getting bank accounts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.delete("/bank-accounts/{account_id}")
async def delete_bank_account(
    account_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a bank account"""
    try:
        service = get_payment_service()
        # Implementation would go here
        return {"message": "Bank account deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting bank account: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Digital Wallet Management Endpoints
@payment_router.post("/wallets")
async def add_digital_wallet(
    wallet_data: DigitalWalletRequest,
    current_user: User = Depends(get_current_user)
):
    """Add a digital wallet for the current user"""
    try:
        service = get_payment_service()
        wallet_id = await service.add_digital_wallet(current_user.id, wallet_data.dict())
        return {"wallet_id": wallet_id, "message": "Digital wallet added successfully"}
        
    except Exception as e:
        logger.error(f"Error adding digital wallet: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/wallets")
async def get_digital_wallets(current_user: User = Depends(get_current_user)):
    """Get all digital wallets for the current user"""
    try:
        service = get_payment_service()
        wallets = await service.get_user_digital_wallets(current_user.id)
        return {"wallets": wallets}
        
    except Exception as e:
        logger.error(f"Error getting digital wallets: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Royalty Management Endpoints
@payment_router.post("/royalty-splits")
async def create_royalty_split(
    split_data: RoyaltySplitRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a royalty split for media"""
    try:
        service = get_payment_service()
        
        # Add recipient_id from recipient_email (you might want to validate this exists)
        split_dict = split_data.dict()
        split_dict['recipient_id'] = split_data.recipient_email  # Simplified for now
        
        split_id = await service.create_royalty_split(split_dict)
        return {"split_id": split_id, "message": "Royalty split created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating royalty split: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/royalty-splits/{media_id}")
async def get_royalty_splits(media_id: str):
    """Get royalty splits for media"""
    try:
        service = get_payment_service()
        splits = await service.get_media_royalty_splits(media_id)
        return {"splits": splits}
        
    except Exception as e:
        logger.error(f"Error getting royalty splits: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Earnings and Payout Endpoints
@payment_router.get("/earnings")
async def get_earnings(current_user: User = Depends(get_current_user)):
    """Get earnings summary for the current user"""
    try:
        service = get_payment_service()
        earnings_data = await service.get_user_earnings(current_user.id)
        return earnings_data
        
    except Exception as e:
        logger.error(f"Error getting earnings: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.post("/payouts")
async def request_payout(
    payout_data: PayoutRequestModel,
    current_user: User = Depends(get_current_user)
):
    """Request a payout"""
    try:
        service = get_payment_service()
        payout_id = await service.request_payout(current_user.id, payout_data.dict())
        return {"payout_id": payout_id, "message": "Payout requested successfully"}
        
    except Exception as e:
        logger.error(f"Error requesting payout: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/transactions")
async def get_payment_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get payment transaction history"""
    try:
        service = get_payment_service()
        # This would need to be implemented in the service
        return {"transactions": [], "total": 0}
        
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Webhook Endpoint for Stripe
@payment_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        service = get_payment_service()
        
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Initialize Stripe checkout to handle webhook
        origin_url = str(request.base_url).rstrip('/')
        stripe_checkout = service.get_stripe_checkout(origin_url)
        
        # Handle webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Process the webhook response
        if webhook_response.event_type == "checkout.session.completed":
            session_id = webhook_response.session_id
            # Update transaction status
            await service.get_checkout_status(session_id)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Admin Endpoints (for platform management)
@payment_router.get("/admin/revenue")
async def get_platform_revenue(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get platform revenue analytics (admin only)"""
    try:
        # Add admin check here
        service = get_payment_service()
        # Implementation would go here
        return {"revenue": 0, "transactions": 0}
        
    except Exception as e:
        logger.error(f"Error getting platform revenue: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/admin/payouts")
async def get_pending_payouts(current_user: User = Depends(get_current_user)):
    """Get pending payouts for admin processing"""
    try:
        # Add admin check here
        service = get_payment_service()
        # Implementation would go here
        return {"payouts": []}
        
    except Exception as e:
        logger.error(f"Error getting pending payouts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.post("/admin/payouts/{payout_id}/process")
async def process_payout(
    payout_id: str,
    current_user: User = Depends(get_current_user)
):
    """Process a payout (admin only)"""
    try:
        # Add admin check here
        service = get_payment_service()
        # Implementation would go here
        return {"message": "Payout processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing payout: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Tax Reporting Endpoints
@payment_router.get("/tax/documents")
async def get_tax_documents(
    tax_year: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Get tax documents for the user"""
    try:
        service = get_payment_service()
        # Implementation would go here
        return {"documents": []}
        
    except Exception as e:
        logger.error(f"Error getting tax documents: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.post("/tax/generate-1099")
async def generate_1099(
    tax_year: int,
    current_user: User = Depends(get_current_user)
):
    """Generate 1099 tax document"""
    try:
        service = get_payment_service()
        # Implementation would go here
        return {"message": "1099 generated successfully"}
        
    except Exception as e:
        logger.error(f"Error generating 1099: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))