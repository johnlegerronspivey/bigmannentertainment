from fastapi import APIRouter, HTTPException, Depends, Request, Form, Body
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import os
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# Import models and services
from payment_models import PaymentTransaction, CreateCheckoutSessionRequest, CreateCheckoutSessionResponse, PaymentStatusResponse
from stripe_payment_service import StripePaymentService
from auth.service import get_current_user
from models.core import User
from config.database import db

logger = logging.getLogger(__name__)

# Create router
stripe_router = APIRouter(prefix="/payments", tags=["stripe_payments"])

# Initialize Stripe service
stripe_service = StripePaymentService(db)

@stripe_router.get("/packages")
async def get_payment_packages():
    """Get available payment packages"""
    try:
        packages = await stripe_service.get_payment_packages()
        return {"packages": packages}
    except Exception as e:
        logger.error(f"Error getting payment packages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get payment packages")

@stripe_router.post("/checkout/session")
async def create_checkout_session(
    request: Request,
    checkout_data: CreateCheckoutSessionRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a Stripe checkout session"""
    try:
        # Initialize Stripe checkout with current host
        host_url = str(request.base_url).rstrip('/')
        stripe_service.initialize_stripe_checkout(host_url)
        
        # Get user info
        user_id = current_user.id if current_user else None
        email = current_user.email if current_user else None
        
        # Build success and cancel URLs from origin_url
        origin_url = checkout_data.origin_url.rstrip('/')
        success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/payment/cancel"
        
        # Create checkout session
        session_response = await stripe_service.create_checkout_session(
            package_id=checkout_data.package_id,
            amount=checkout_data.amount,
            currency=checkout_data.currency,
            stripe_price_id=checkout_data.stripe_price_id,
            quantity=checkout_data.quantity,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=checkout_data.metadata,
            user_id=user_id,
            email=email
        )
        
        return CreateCheckoutSessionResponse(
            url=session_response.url,
            session_id=session_response.session_id,
            amount=checkout_data.amount or 0.0,
            currency=checkout_data.currency
        )
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@stripe_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str):
    """Get checkout session status"""
    try:
        # Initialize Stripe checkout (needed for status check)
        stripe_service.initialize_stripe_checkout("https://bigmannentertainment.com")
        
        status_response = await stripe_service.get_checkout_status(session_id)
        
        return PaymentStatusResponse(
            status=status_response.status,
            payment_status=status_response.payment_status,
            amount_total=status_response.amount_total,
            currency=status_response.currency,
            metadata=status_response.metadata
        )
        
    except Exception as e:
        logger.error(f"Error getting checkout status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get checkout status: {str(e)}")

@stripe_router.get("/transactions")
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get user's payment transactions"""
    try:
        transactions = await stripe_service.get_user_transactions(current_user.id, limit)
        return {"transactions": transactions}
    except Exception as e:
        logger.error(f"Error getting user transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get transactions")

@stripe_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Get raw body and signature
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        
        if not stripe_signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Initialize Stripe service
        host_url = str(request.base_url).rstrip('/')
        stripe_service.initialize_stripe_checkout(host_url)
        
        # Process webhook
        webhook_response = await stripe_service.handle_webhook(body, stripe_signature)
        
        return {"received": True, "event_type": webhook_response.event_type}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")

# Additional endpoints for subscription management

@stripe_router.post("/subscriptions/create")
async def create_subscription(
    request: Request,
    stripe_price_id: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Create a subscription"""
    try:
        # Initialize Stripe checkout
        host_url = str(request.base_url).rstrip('/')
        stripe_service.initialize_stripe_checkout(host_url)
        
        # Build URLs
        success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{host_url}/payment/cancel"
        
        # Create subscription session
        session_response = await stripe_service.create_checkout_session(
            package_id=None,
            amount=None,
            currency="usd",
            stripe_price_id=stripe_price_id,
            quantity=1,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"subscription": "true"},
            user_id=current_user.id,
            email=current_user.email
        )
        
        return {"url": session_response.url, "session_id": session_response.session_id}
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")

@stripe_router.get("/user/credits")
async def get_user_credits(current_user: User = Depends(get_current_user)):
    """Get user's payment credits and features"""
    try:
        user_credits = await db.user_credits.find_one({"user_id": current_user.id})
        
        if not user_credits:
            user_credits = {
                "user_id": current_user.id,
                "upload_credits": 0,
                "distribution_credits": 0,
                "premium_features": False
            }
        
        return user_credits
        
    except Exception as e:
        logger.error(f"Error getting user credits: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user credits")

@stripe_router.get("/earnings")
async def get_user_earnings(current_user: User = Depends(get_current_user)):
    """Get user's earnings and revenue sharing"""
    try:
        # Get user earnings
        earnings = await db.user_earnings.find_one({"user_id": current_user.id})
        
        if not earnings:
            earnings = {
                "user_id": current_user.id,
                "total_earnings": 0.0,
                "available_balance": 0.0,
                "pending_balance": 0.0,
                "total_paid_out": 0.0,
                "currency": "usd"
            }
        
        # Get recent revenue shares
        revenue_shares = []
        async for share in db.revenue_shares.find(
            {"creator_user_id": current_user.id}
        ).sort("created_at", -1).limit(10):
            revenue_shares.append(share)
        
        return {
            "earnings": earnings,
            "recent_revenue_shares": revenue_shares
        }
        
    except Exception as e:
        logger.error(f"Error getting user earnings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get earnings")

@stripe_router.post("/payout/request")
async def request_payout(
    amount: float = Form(...),
    payout_method: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Request a payout for creator earnings"""
    try:
        # Get user earnings
        earnings = await db.user_earnings.find_one({"user_id": current_user.id})
        
        if not earnings or earnings.get("available_balance", 0) < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance for payout")
        
        # Create payout request
        payout_request = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "amount": amount,
            "currency": "usd",
            "payout_method": payout_method,
            "status": "pending",
            "requested_at": datetime.utcnow()
        }
        
        await db.payout_requests.insert_one(payout_request)
        
        # Update available balance
        await db.user_earnings.update_one(
            {"user_id": current_user.id},
            {
                "$inc": {
                    "available_balance": -amount,
                    "pending_balance": amount
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Payout request submitted successfully", "payout_id": payout_request["id"]}
        
    except Exception as e:
        logger.error(f"Error requesting payout: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to request payout")

# Statistics and analytics endpoints for admin

@stripe_router.get("/admin/revenue")
async def get_platform_revenue(current_user: User = Depends(get_current_user)):
    """Get platform revenue statistics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get total transactions
        total_transactions = await db.payment_transactions.count_documents({"status": "completed"})
        
        # Get total revenue
        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total_revenue": {"$sum": "$amount"}}}
        ]
        
        revenue_result = await db.payment_transactions.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0.0
        
        # Get platform revenue from revenue shares
        platform_pipeline = [
            {"$group": {"_id": None, "platform_revenue": {"$sum": "$platform_amount"}}}
        ]
        
        platform_result = await db.revenue_shares.aggregate(platform_pipeline).to_list(1)
        platform_revenue = platform_result[0]["platform_revenue"] if platform_result else 0.0
        
        return {
            "total_transactions": total_transactions,
            "total_revenue": total_revenue,
            "platform_revenue": platform_revenue,
            "creator_revenue": total_revenue - platform_revenue
        }
        
    except Exception as e:
        logger.error(f"Error getting platform revenue: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get revenue statistics")