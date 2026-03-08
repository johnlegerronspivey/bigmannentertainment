"""
Subscription Tiers - Manage creator subscription plans
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from config.database import db
from auth.service import get_current_user
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscription Tiers"])

TIERS = {
    "free": {
        "id": "free",
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": [
            "Basic creator profile",
            "Up to 5 media uploads",
            "Standard watermark",
            "Community support",
        ],
        "limits": {"max_uploads": 5, "max_distributions": 2, "watermark_custom": False, "analytics": "basic"},
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "price_monthly": 9.99,
        "price_yearly": 99.99,
        "stripe_price_monthly": "price_pro_monthly",
        "stripe_price_yearly": "price_pro_yearly",
        "features": [
            "Enhanced creator profile",
            "Unlimited media uploads",
            "Custom watermarks",
            "Priority distribution",
            "Advanced analytics",
            "Email support",
        ],
        "limits": {"max_uploads": -1, "max_distributions": 50, "watermark_custom": True, "analytics": "advanced"},
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price_monthly": 29.99,
        "price_yearly": 299.99,
        "stripe_price_monthly": "price_enterprise_monthly",
        "stripe_price_yearly": "price_enterprise_yearly",
        "features": [
            "Premium creator profile with verification badge",
            "Unlimited everything",
            "White-label watermarks",
            "Priority distribution to 120+ platforms",
            "Real-time analytics dashboard",
            "Dedicated account manager",
            "API access",
            "Custom integrations",
        ],
        "limits": {"max_uploads": -1, "max_distributions": -1, "watermark_custom": True, "analytics": "realtime"},
    },
}


def serialize_sub(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    for k in ["created_at", "updated_at", "current_period_start", "current_period_end"]:
        if k in doc and isinstance(doc[k], datetime):
            doc[k] = doc[k].isoformat()
    return doc


@router.get("/tiers")
async def list_tiers():
    """List all available subscription tiers"""
    return {"tiers": list(TIERS.values())}


@router.get("/me")
async def get_my_subscription(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    sub = await db.subscriptions.find_one({"user_id": user_id, "status": {"$in": ["active", "trialing"]}})
    if not sub:
        return {
            "tier": "free",
            "status": "active",
            "tier_details": TIERS["free"],
        }
    return {
        "subscription": serialize_sub(sub),
        "tier": sub.get("tier", "free"),
        "status": sub.get("status", "active"),
        "tier_details": TIERS.get(sub.get("tier", "free"), TIERS["free"]),
    }


@router.post("/checkout")
async def create_subscription_checkout(
    request: Request,
    current_user=Depends(get_current_user),
):
    """Create a Stripe checkout session for a subscription tier"""
    body = await request.json()
    tier_id = body.get("tier_id")
    billing = body.get("billing", "monthly")

    if tier_id not in TIERS or tier_id == "free":
        raise HTTPException(status_code=400, detail="Invalid tier. Choose 'pro' or 'enterprise'.")

    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    user_email = current_user.get("email") if isinstance(current_user, dict) else current_user.email

    tier = TIERS[tier_id]
    price = tier[f"price_{billing}"] if billing == "yearly" else tier["price_monthly"]

    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_API_KEY")
        if not stripe.api_key:
            raise HTTPException(status_code=500, detail="Stripe not configured")

        frontend_url = os.environ.get("FRONTEND_URL", "")
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=user_email,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Big Mann Entertainment - {tier['name']} Plan",
                        "description": f"{'Monthly' if billing == 'monthly' else 'Yearly'} subscription",
                    },
                    "unit_amount": int(price * 100),
                    "recurring": {"interval": "month" if billing == "monthly" else "year"},
                },
                "quantity": 1,
            }],
            success_url=f"{frontend_url}/subscription?status=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/subscription?status=cancelled",
            metadata={
                "user_id": user_id,
                "tier_id": tier_id,
                "billing": billing,
            },
        )

        # Store pending subscription
        await db.subscriptions.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "tier": tier_id,
                    "billing": billing,
                    "status": "pending",
                    "stripe_session_id": session.id,
                    "updated_at": datetime.now(timezone.utc),
                },
                "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
            },
            upsert=True,
        )

        return {"checkout_url": session.url, "session_id": session.id}

    except ImportError:
        raise HTTPException(status_code=500, detail="Stripe library not available")
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")


@router.post("/confirm")
async def confirm_subscription(request: Request, current_user=Depends(get_current_user)):
    """Confirm a subscription after Stripe checkout"""
    body = await request.json()
    session_id = body.get("session_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_API_KEY")
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            tier_id = session.metadata.get("tier_id", "pro")
            billing = session.metadata.get("billing", "monthly")

            await db.subscriptions.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "status": "active",
                        "tier": tier_id,
                        "billing": billing,
                        "stripe_subscription_id": session.subscription,
                        "stripe_customer_id": session.customer,
                        "current_period_start": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

            # Update creator profile tier
            await db.creator_profiles.update_one(
                {"user_id": user_id},
                {"$set": {"subscription_tier": tier_id}},
            )

            return {"status": "active", "tier": tier_id}

        return {"status": session.payment_status}

    except Exception as e:
        logger.error(f"Subscription confirm error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel")
async def cancel_subscription(current_user=Depends(get_current_user)):
    """Cancel current subscription"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    sub = await db.subscriptions.find_one({"user_id": user_id, "status": "active"})

    if not sub:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")

    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_API_KEY")

        if sub.get("stripe_subscription_id"):
            stripe.Subscription.modify(sub["stripe_subscription_id"], cancel_at_period_end=True)

        await db.subscriptions.update_one(
            {"user_id": user_id},
            {"$set": {"status": "cancelled", "updated_at": datetime.now(timezone.utc)}},
        )

        await db.creator_profiles.update_one(
            {"user_id": user_id},
            {"$set": {"subscription_tier": "free"}},
        )

        return {"status": "cancelled", "message": "Subscription cancelled. You'll retain access until end of billing period."}

    except Exception as e:
        logger.error(f"Cancel subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
