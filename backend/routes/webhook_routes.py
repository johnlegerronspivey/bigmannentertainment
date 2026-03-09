"""Webhook endpoints — Stripe, etc."""
import logging
from fastapi import APIRouter, Request, HTTPException
from config.database import db

router = APIRouter(tags=["Webhooks"])


@router.post("/webhook/stripe")
async def stripe_webhook_handler(request: Request):
    try:
        from stripe_payment_service import StripePaymentService
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        if not stripe_signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        stripe_service = StripePaymentService(db)
        host_url = str(request.base_url).rstrip('/')
        stripe_service.initialize_stripe_checkout(host_url)
        webhook_response = await stripe_service.handle_webhook(body, stripe_signature)
        return {"received": True, "event_type": webhook_response.event_type}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")
