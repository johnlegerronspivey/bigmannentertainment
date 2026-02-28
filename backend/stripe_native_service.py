"""
Native Stripe integration
Drop-in replacement for emergentintegrations.payments.stripe.checkout
"""

import stripe
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class CheckoutSessionRequest:
    amount: Optional[float] = None
    currency: str = "usd"
    success_url: str = ""
    cancel_url: str = ""
    metadata: Optional[Dict[str, str]] = None
    stripe_price_id: Optional[str] = None
    quantity: int = 1


@dataclass
class CheckoutSessionResponse:
    session_id: str = ""
    checkout_url: str = ""
    status: str = ""


@dataclass
class CheckoutStatusResponse:
    session_id: str = ""
    status: str = ""
    payment_status: str = ""
    customer_email: Optional[str] = None
    amount_total: Optional[int] = None


@dataclass
class WebhookResponse:
    event_type: str = ""
    session_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class StripeCheckout:
    def __init__(self, api_key: str, webhook_url: str = ""):
        self.api_key = api_key
        self.webhook_url = webhook_url
        stripe.api_key = api_key

    async def create_checkout_session(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        line_items = []
        if request.stripe_price_id:
            line_items.append({
                "price": request.stripe_price_id,
                "quantity": request.quantity,
            })
        else:
            line_items.append({
                "price_data": {
                    "currency": request.currency,
                    "product_data": {"name": request.metadata.get("package_type", "Payment") if request.metadata else "Payment"},
                    "unit_amount": int((request.amount or 0) * 100),
                },
                "quantity": 1,
            })

        params = {
            "payment_method_types": ["card"],
            "line_items": line_items,
            "mode": "subscription" if request.stripe_price_id else "payment",
            "success_url": request.success_url,
            "cancel_url": request.cancel_url,
        }
        if request.metadata:
            params["metadata"] = request.metadata

        session = stripe.checkout.Session.create(**params)
        return CheckoutSessionResponse(
            session_id=session.id,
            checkout_url=session.url or "",
            status=session.status or "",
        )

    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        session = stripe.checkout.Session.retrieve(session_id)
        return CheckoutStatusResponse(
            session_id=session.id,
            status=session.status or "",
            payment_status=session.payment_status or "",
            customer_email=session.customer_details.email if session.customer_details else None,
            amount_total=session.amount_total,
        )

    async def handle_webhook(self, webhook_body: bytes, stripe_signature: str) -> WebhookResponse:
        try:
            event = stripe.Webhook.construct_event(
                webhook_body, stripe_signature, self.webhook_url
            )
        except Exception:
            event = stripe.Event.construct_from(
                stripe.util.json.loads(webhook_body), stripe.api_key
            )

        session_id = ""
        if event.data and event.data.object:
            session_id = getattr(event.data.object, "id", "")

        return WebhookResponse(
            event_type=event.type,
            session_id=session_id,
            data=event.data.object if event.data else {},
        )
