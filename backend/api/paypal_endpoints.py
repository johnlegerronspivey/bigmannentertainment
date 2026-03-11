"""
PayPal Payment Endpoints
FastAPI endpoints for PayPal payment processing
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
from decimal import Decimal
import json

from paypal_payment_service import PayPalPaymentService
from auth.service import get_current_user
from models.core import User
from config.database import db

logger = logging.getLogger(__name__)

# Initialize PayPal router
paypal_router = APIRouter(prefix="/paypal", tags=["PayPal Payments"])

# Initialize PayPal service
paypal_service = PayPalPaymentService(db)

from pydantic import BaseModel

class PayPalOrderRequest(BaseModel):
    amount: float
    currency: str = "USD"
    description: Optional[str] = "Big Mann Entertainment Service"
    reference_id: Optional[str] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@paypal_router.post("/orders")
async def create_paypal_order(
    order_request: PayPalOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a PayPal order for payment"""
    
    try:
        # Validate amount
        if order_request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        
        # Create payment (using the correct method name)
        result = await paypal_service.create_payment(
            amount=Decimal(str(order_request.amount)),
            currency=order_request.currency,
            description=order_request.description,
            reference_id=order_request.reference_id,
            return_url=order_request.return_url,
            cancel_url=order_request.cancel_url,
            user_id=current_user.id,
            metadata=order_request.metadata
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400, 
                detail=f"PayPal order creation failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "payment_id": result["payment_id"],
            "approval_url": result["approval_url"],
            "reference_id": result["reference_id"],
            "amount": result["amount"],
            "currency": result["currency"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating PayPal order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@paypal_router.post("/orders/{payment_id}/capture")
async def capture_paypal_payment(
    payment_id: str,
    payer_id: str,
    current_user: User = Depends(get_current_user)
):
    """Capture payment for a PayPal payment"""
    
    try:
        result = await paypal_service.execute_payment(payment_id, payer_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"PayPal capture failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "sale_id": result["sale_id"],
            "payment_id": result["payment_id"],
            "status": result["status"],
            "amount": result["amount"],
            "currency": result["currency"],
            "transaction_id": result["transaction_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error capturing PayPal order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@paypal_router.get("/orders/{payment_id}")
async def get_paypal_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get PayPal payment details"""
    
    try:
        result = await paypal_service.get_payment(payment_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving PayPal order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

class PayPalRefundRequest(BaseModel):
    amount: Optional[float] = None
    note: Optional[str] = None

@paypal_router.post("/captures/{sale_id}/refund")
async def refund_paypal_sale(
    sale_id: str,
    refund_request: PayPalRefundRequest,
    current_user: User = Depends(get_current_user)
):
    """Refund a PayPal sale"""
    
    try:
        refund_amount = Decimal(str(refund_request.amount)) if refund_request.amount else None
        
        result = await paypal_service.refund_sale(
            sale_id=sale_id,
            amount=refund_amount,
            note=refund_request.note
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"PayPal refund failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "refund_id": result["refund_id"],
            "sale_id": result["sale_id"],
            "status": result["status"],
            "amount": result["amount"],
            "currency": result["currency"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PayPal refund: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@paypal_router.get("/payments")
async def get_user_paypal_payments(
    current_user: User = Depends(get_current_user)
):
    """Get user's PayPal payment history"""
    
    try:
        payments = await paypal_service.get_user_payments(current_user.id)
        
        return {
            "success": True,
            "payments": payments,
            "total": len(payments)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user PayPal payments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@paypal_router.get("/analytics")
async def get_paypal_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get PayPal payment analytics (admin only)"""
    
    try:
        # Check if user has admin access (implement your admin check logic)
        # For now, we'll return analytics for all authenticated users
        analytics = await paypal_service.get_payment_analytics()
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error retrieving PayPal analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@paypal_router.post("/webhooks")
async def paypal_webhook_handler(request: Request):
    """Handle PayPal webhook events"""
    
    try:
        # Get headers and body
        headers = dict(request.headers)
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Verify webhook signature
        is_valid = await paypal_service.verify_webhook_signature(headers, body_str)
        
        if not is_valid:
            logger.warning("Invalid PayPal webhook signature")
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
        # Parse webhook data
        try:
            webhook_data = json.loads(body_str)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Process webhook event
        result = await paypal_service.handle_webhook_event(webhook_data)
        
        logger.info(f"PayPal webhook processed: {result}")
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "result": result}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# PayPal subscription endpoints (for future implementation)
@paypal_router.post("/subscriptions")
async def create_paypal_subscription(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """Create PayPal subscription (placeholder for future implementation)"""
    
    # This would integrate with PayPal's subscription API
    # For now, return a placeholder response
    return {
        "success": False,
        "message": "PayPal subscriptions not yet implemented",
        "plan_id": plan_id
    }

@paypal_router.get("/config")
async def get_paypal_config():
    """Get PayPal configuration for frontend"""
    
    try:
        # Return public configuration (client ID only, never the secret)
        config = {
            "client_id": paypal_service.client_id,
            "environment": "sandbox" if paypal_service.is_sandbox else "live",
            "currency": "USD"
        }
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error(f"Error getting PayPal config: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")