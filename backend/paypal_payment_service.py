"""
PayPal Payment Service
Handles PayPal payment processing for Big Mann Entertainment platform
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from decimal import Decimal
import uuid

import paypalrestsdk
from paypalrestsdk import Payment, WebProfile
from paypalrestsdk.exceptions import ResourceNotFound, UnauthorizedAccess, MissingConfig

logger = logging.getLogger(__name__)

class PayPalPaymentService:
    def __init__(self, mongo_db=None):
        self.mongo_db = mongo_db
        
        # PayPal configuration
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        self.webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')
        
        # Environment setup (sandbox by default, use live for production)
        self.is_sandbox = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox').lower() == 'sandbox'
        
        if self.is_sandbox:
            environment = SandboxEnvironment(
                client_id=self.client_id, 
                client_secret=self.client_secret
            )
        else:
            environment = LiveEnvironment(
                client_id=self.client_id, 
                client_secret=self.client_secret
            )
        
        self.client = PayPalHttpClient(environment)
        
        logger.info(f"PayPal service initialized - Environment: {'sandbox' if self.is_sandbox else 'live'}")

    async def create_order(
        self,
        amount: Decimal,
        currency: str = "USD",
        description: str = "Big Mann Entertainment Service",
        reference_id: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a PayPal order for payment"""
        
        try:
            # Generate reference ID if not provided
            if not reference_id:
                reference_id = f"BME_{uuid.uuid4().hex[:12]}"
            
            # Create order request
            request = OrdersCreateRequest()
            request.prefer('return=representation')
            
            # Order details
            order_body = {
                "intent": "CAPTURE",
                "application_context": {
                    "brand_name": "Big Mann Entertainment",
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                    "shipping_preference": "NO_SHIPPING"
                },
                "purchase_units": [{
                    "reference_id": reference_id,
                    "description": description,
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    }
                }]
            }
            
            # Add return URLs if provided
            if return_url and cancel_url:
                order_body["application_context"]["return_url"] = return_url
                order_body["application_context"]["cancel_url"] = cancel_url
            
            request.request_body(order_body)
            
            # Execute request
            response = self.client.execute(request)
            
            # Store order in database
            order_record = {
                "id": str(uuid.uuid4()),
                "paypal_order_id": response.result.id,
                "reference_id": reference_id,
                "amount": str(amount),
                "currency": currency,
                "description": description,
                "status": response.result.status,
                "user_id": user_id,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            if self.mongo_db:
                await self.mongo_db.paypal_orders.insert_one(order_record)
            
            # Return order details
            result = {
                "success": True,
                "order_id": response.result.id,
                "reference_id": reference_id,
                "status": response.result.status,
                "amount": str(amount),
                "currency": currency,
                "approval_url": None
            }
            
            # Extract approval URL for redirect
            for link in response.result.links:
                if link.rel == "approve":
                    result["approval_url"] = link.href
                    break
            
            logger.info(f"PayPal order created: {response.result.id}")
            return result
            
        except HttpError as e:
            logger.error(f"PayPal order creation failed: {str(e)}")
            error_details = json.loads(e.message) if hasattr(e, 'message') else str(e)
            return {
                "success": False,
                "error": "PayPal order creation failed",
                "details": error_details
            }
        except Exception as e:
            logger.error(f"Unexpected error creating PayPal order: {str(e)}")
            return {
                "success": False,
                "error": "Unexpected error during order creation",
                "details": str(e)
            }

    async def capture_order(self, order_id: str) -> Dict[str, Any]:
        """Capture payment for a PayPal order"""
        
        try:
            # Create capture request
            request = OrdersCaptureRequest(order_id)
            request.prefer('return=representation')
            
            # Execute capture
            response = self.client.execute(request)
            
            # Extract capture details
            capture_result = response.result
            purchase_unit = capture_result.purchase_units[0]
            
            if purchase_unit.payments and purchase_unit.payments.captures:
                capture = purchase_unit.payments.captures[0]
                
                # Update order in database
                if self.mongo_db:
                    await self.mongo_db.paypal_orders.update_one(
                        {"paypal_order_id": order_id},
                        {
                            "$set": {
                                "status": capture_result.status,
                                "capture_id": capture.id,
                                "captured_at": datetime.now(timezone.utc),
                                "updated_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                
                # Create payment record
                payment_record = {
                    "id": str(uuid.uuid4()),
                    "paypal_order_id": order_id,
                    "paypal_capture_id": capture.id,
                    "amount": capture.amount.value,
                    "currency": capture.amount.currency_code,
                    "status": capture.status,
                    "reference_id": purchase_unit.reference_id,
                    "created_at": datetime.now(timezone.utc)
                }
                
                if self.mongo_db:
                    await self.mongo_db.paypal_payments.insert_one(payment_record)
                
                logger.info(f"PayPal payment captured: {capture.id}")
                
                return {
                    "success": True,
                    "capture_id": capture.id,
                    "order_id": order_id,
                    "status": capture.status,
                    "amount": capture.amount.value,
                    "currency": capture.amount.currency_code,
                    "reference_id": purchase_unit.reference_id
                }
            else:
                return {
                    "success": False,
                    "error": "No captures found in payment response"
                }
                
        except HttpError as e:
            logger.error(f"PayPal capture failed: {str(e)}")
            error_details = json.loads(e.message) if hasattr(e, 'message') else str(e)
            return {
                "success": False,
                "error": "PayPal capture failed",
                "details": error_details
            }
        except Exception as e:
            logger.error(f"Unexpected error capturing PayPal payment: {str(e)}")
            return {
                "success": False,
                "error": "Unexpected error during capture",
                "details": str(e)
            }

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get PayPal order details"""
        
        try:
            request = OrdersGetRequest(order_id)
            response = self.client.execute(request)
            
            order = response.result
            
            return {
                "success": True,
                "order_id": order.id,
                "status": order.status,
                "amount": order.purchase_units[0].amount.value,
                "currency": order.purchase_units[0].amount.currency_code,
                "reference_id": order.purchase_units[0].reference_id,
                "created_at": order.create_time,
                "updated_at": order.update_time
            }
            
        except HttpError as e:
            logger.error(f"Failed to get PayPal order: {str(e)}")
            return {
                "success": False,
                "error": "Failed to retrieve order",
                "details": str(e)
            }

    async def refund_capture(
        self, 
        capture_id: str, 
        amount: Optional[Decimal] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refund a captured payment"""
        
        try:
            request = CapturesRefundRequest(capture_id)
            
            refund_body = {}
            if amount:
                refund_body["amount"] = {
                    "value": str(amount),
                    "currency_code": "USD"  # Default to USD, should be dynamic
                }
            if note:
                refund_body["note_to_payer"] = note
            
            if refund_body:
                request.request_body(refund_body)
            
            response = self.client.execute(request)
            refund = response.result
            
            # Record refund in database
            if self.mongo_db:
                refund_record = {
                    "id": str(uuid.uuid4()),
                    "paypal_refund_id": refund.id,
                    "paypal_capture_id": capture_id,
                    "amount": refund.amount.value,
                    "currency": refund.amount.currency_code,
                    "status": refund.status,
                    "note": note,
                    "created_at": datetime.now(timezone.utc)
                }
                await self.mongo_db.paypal_refunds.insert_one(refund_record)
            
            logger.info(f"PayPal refund created: {refund.id}")
            
            return {
                "success": True,
                "refund_id": refund.id,
                "capture_id": capture_id,
                "status": refund.status,
                "amount": refund.amount.value,
                "currency": refund.amount.currency_code
            }
            
        except HttpError as e:
            logger.error(f"PayPal refund failed: {str(e)}")
            return {
                "success": False,
                "error": "PayPal refund failed",
                "details": str(e)
            }

    async def verify_webhook_signature(
        self,
        headers: Dict[str, str],
        body: str
    ) -> bool:
        """Verify PayPal webhook signature"""
        
        if not self.webhook_id:
            logger.warning("PayPal webhook ID not configured")
            return False
        
        try:
            request = WebhookVerifySignatureRequest()
            request.request_body({
                'auth_algo': headers.get('PAYPAL-AUTH-ALGO'),
                'cert_id': headers.get('PAYPAL-CERT-ID'), 
                'transmission_id': headers.get('PAYPAL-TRANSMISSION-ID'),
                'transmission_sig': headers.get('PAYPAL-TRANSMISSION-SIG'),
                'transmission_time': headers.get('PAYPAL-TRANSMISSION-TIME'),
                'webhook_id': self.webhook_id,
                'webhook_event': json.loads(body)
            })
            
            response = self.client.execute(request)
            return response.result.verification_status == "SUCCESS"
            
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False

    async def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PayPal webhook events"""
        
        event_type = event_data.get('event_type')
        resource = event_data.get('resource', {})
        
        logger.info(f"Processing PayPal webhook event: {event_type}")
        
        try:
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                # Payment was completed
                capture_id = resource.get('id')
                order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
                
                if self.mongo_db and order_id:
                    await self.mongo_db.paypal_orders.update_one(
                        {"paypal_order_id": order_id},
                        {
                            "$set": {
                                "status": "COMPLETED",
                                "capture_id": capture_id,
                                "webhook_processed_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                
                return {"status": "processed", "action": "payment_completed"}
                
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                # Payment was denied
                order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
                
                if self.mongo_db and order_id:
                    await self.mongo_db.paypal_orders.update_one(
                        {"paypal_order_id": order_id},
                        {
                            "$set": {
                                "status": "DENIED",
                                "webhook_processed_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                
                return {"status": "processed", "action": "payment_denied"}
                
            elif event_type == 'PAYMENT.CAPTURE.REFUNDED':
                # Payment was refunded
                refund_id = resource.get('id')
                
                if self.mongo_db:
                    await self.mongo_db.paypal_refunds.update_one(
                        {"paypal_refund_id": refund_id},
                        {
                            "$set": {
                                "status": "COMPLETED",
                                "webhook_processed_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                
                return {"status": "processed", "action": "payment_refunded"}
            
            else:
                logger.info(f"Unhandled PayPal webhook event: {event_type}")
                return {"status": "ignored", "event_type": event_type}
                
        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_user_payments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's PayPal payment history"""
        
        if not self.mongo_db:
            return []
        
        try:
            payments = []
            async for payment in self.mongo_db.paypal_payments.find(
                {"user_id": user_id}
            ).sort("created_at", -1):
                payments.append({
                    "id": payment["id"],
                    "paypal_capture_id": payment["paypal_capture_id"],
                    "amount": payment["amount"],
                    "currency": payment["currency"],
                    "status": payment["status"],
                    "reference_id": payment["reference_id"],
                    "created_at": payment["created_at"].isoformat()
                })
            
            return payments
            
        except Exception as e:
            logger.error(f"Error retrieving user PayPal payments: {str(e)}")
            return []

    async def get_payment_analytics(self) -> Dict[str, Any]:
        """Get PayPal payment analytics"""
        
        if not self.mongo_db:
            return {}
        
        try:
            # Get payment stats
            total_payments = await self.mongo_db.paypal_payments.count_documents({})
            completed_payments = await self.mongo_db.paypal_payments.count_documents({"status": "COMPLETED"})
            
            # Calculate total revenue
            pipeline = [
                {"$match": {"status": "COMPLETED"}},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": {"$toDouble": "$amount"}},
                    "avg_payment": {"$avg": {"$toDouble": "$amount"}}
                }}
            ]
            
            revenue_result = await self.mongo_db.paypal_payments.aggregate(pipeline).to_list(1)
            total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
            avg_payment = revenue_result[0]["avg_payment"] if revenue_result else 0
            
            return {
                "total_payments": total_payments,
                "completed_payments": completed_payments,
                "total_revenue": round(total_revenue, 2),
                "average_payment": round(avg_payment, 2),
                "success_rate": round((completed_payments / total_payments * 100), 2) if total_payments > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating PayPal analytics: {str(e)}")
            return {}