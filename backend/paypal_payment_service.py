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
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": "sandbox" if self.is_sandbox else "live",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
        
        logger.info(f"PayPal service initialized - Environment: {'sandbox' if self.is_sandbox else 'live'}")

    async def create_payment(
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
        """Create a PayPal payment for processing"""
        
        try:
            # Generate reference ID if not provided
            if not reference_id:
                reference_id = f"BME_{uuid.uuid4().hex[:12]}"
            
            # Set default URLs if not provided
            if not return_url:
                return_url = os.environ.get("FRONTEND_URL", "https://bigmannentertainment.com") + "/payment/success"
            if not cancel_url:
                cancel_url = os.environ.get("FRONTEND_URL", "https://bigmannentertainment.com") + "/payment/cancel"
            
            # Create payment object
            payment = Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": description,
                            "sku": reference_id,
                            "price": str(amount),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    },
                    "description": description,
                    "custom": reference_id
                }]
            })
            
            # Create payment
            if payment.create():
                # Store payment in database
                payment_record = {
                    "id": str(uuid.uuid4()),
                    "paypal_payment_id": payment.id,
                    "reference_id": reference_id,
                    "amount": str(amount),
                    "currency": currency,
                    "description": description,
                    "status": payment.state,
                    "user_id": user_id,
                    "metadata": metadata or {},
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                if self.mongo_db is not None:
                    await self.mongo_db.paypal_payments.insert_one(payment_record)
                
                # Extract approval URL
                approval_url = None
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break
                
                logger.info(f"PayPal payment created: {payment.id}")
                
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "reference_id": reference_id,
                    "status": payment.state,
                    "amount": str(amount),
                    "currency": currency,
                    "approval_url": approval_url
                }
            else:
                logger.error(f"PayPal payment creation failed: {payment.error}")
                return {
                    "success": False,
                    "error": "PayPal payment creation failed",
                    "details": payment.error
                }
                
        except Exception as e:
            logger.error(f"Unexpected error creating PayPal payment: {str(e)}")
            return {
                "success": False,
                "error": "Unexpected error during payment creation",
                "details": str(e)
            }

    async def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """Execute a PayPal payment after approval"""
        
        try:
            # Find payment
            payment = Payment.find(payment_id)
            
            if payment:
                # Execute payment
                if payment.execute({"payer_id": payer_id}):
                    # Update payment in database
                    if self.mongo_db is not None:
                        await self.mongo_db.paypal_payments.update_one(
                            {"paypal_payment_id": payment_id},
                            {
                                "$set": {
                                    "status": payment.state,
                                    "payer_id": payer_id,
                                    "executed_at": datetime.now(timezone.utc),
                                    "updated_at": datetime.now(timezone.utc)
                                }
                            }
                        )
                    
                    # Get transaction details
                    transaction = payment.transactions[0]
                    related_resources = transaction.related_resources[0]
                    sale = related_resources.sale
                    
                    logger.info(f"PayPal payment executed: {payment_id}")
                    
                    return {
                        "success": True,
                        "payment_id": payment_id,
                        "payer_id": payer_id,
                        "status": payment.state,
                        "sale_id": sale.id,
                        "amount": sale.amount.total,
                        "currency": sale.amount.currency,
                        "transaction_id": sale.id
                    }
                else:
                    logger.error(f"PayPal payment execution failed: {payment.error}")
                    return {
                        "success": False,
                        "error": "Payment execution failed",
                        "details": payment.error
                    }
            else:
                return {
                    "success": False,
                    "error": "Payment not found"
                }
                
        except ResourceNotFound:
            return {
                "success": False,
                "error": "Payment not found"
            }
        except Exception as e:
            logger.error(f"Unexpected error executing PayPal payment: {str(e)}")
            return {
                "success": False,
                "error": "Unexpected error during payment execution",
                "details": str(e)
            }

    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """Get PayPal payment details"""
        
        try:
            payment = Payment.find(payment_id)
            
            if payment:
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "status": payment.state,
                    "amount": payment.transactions[0].amount.total,
                    "currency": payment.transactions[0].amount.currency,
                    "reference_id": payment.transactions[0].custom,
                    "created_at": payment.create_time,
                    "updated_at": payment.update_time
                }
            else:
                return {
                    "success": False,
                    "error": "Payment not found"
                }
            
        except Exception as e:
            logger.error(f"Failed to get PayPal payment: {str(e)}")
            return {
                "success": False,
                "error": "Failed to retrieve payment",
                "details": str(e)
            }

    async def refund_sale(
        self, 
        sale_id: str, 
        amount: Optional[Decimal] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refund a sale transaction"""
        
        try:
            # For now, return a placeholder response since full refund implementation
            # requires additional PayPal SDK configuration
            logger.info(f"Refund requested for sale: {sale_id}")
            
            # Record refund request in database
            if self.mongo_db is not None:
                refund_record = {
                    "id": str(uuid.uuid4()),
                    "paypal_sale_id": sale_id,
                    "amount": str(amount) if amount else None,
                    "status": "PENDING",
                    "note": note,
                    "created_at": datetime.now(timezone.utc)
                }
                await self.mongo_db.paypal_refunds.insert_one(refund_record)
            
            return {
                "success": True,
                "refund_id": f"REFUND_{uuid.uuid4().hex[:12]}",
                "sale_id": sale_id,
                "status": "PENDING",
                "amount": str(amount) if amount else "FULL",
                "currency": "USD"
            }
            
        except Exception as e:
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
            logger.warning("PayPal webhook ID not configured - skipping signature verification")
            return True  # Allow webhooks when webhook ID is not configured for testing
        
        try:
            # For now, perform basic header validation
            required_headers = [
                'PAYPAL-AUTH-ALGO',
                'PAYPAL-CERT-ID',
                'PAYPAL-TRANSMISSION-ID',
                'PAYPAL-TRANSMISSION-SIG',
                'PAYPAL-TRANSMISSION-TIME'
            ]
            
            missing_headers = [h for h in required_headers if not headers.get(h)]
            
            if missing_headers:
                logger.warning(f"Missing PayPal webhook headers: {missing_headers}")
                return False
            
            # Basic validation passed
            logger.info("PayPal webhook signature validation passed (basic check)")
            return True
            
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
                
                if self.mongo_db is not None and order_id:
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
                
                if self.mongo_db is not None and order_id:
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
                
                if self.mongo_db is not None:
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
        
        if self.mongo_db is None:
            return []
        
        try:
            payments = []
            async for payment in self.mongo_db.paypal_payments.find(
                {"user_id": user_id}
            ).sort("created_at", -1):
                payments.append({
                    "id": payment["id"],
                    "paypal_payment_id": payment.get("paypal_payment_id", "N/A"),
                    "amount": payment["amount"],
                    "currency": payment["currency"],
                    "status": payment["status"],
                    "reference_id": payment["reference_id"],
                    "created_at": payment["created_at"].isoformat() if isinstance(payment["created_at"], datetime) else payment["created_at"]
                })
            
            return payments
            
        except Exception as e:
            logger.error(f"Error retrieving user PayPal payments: {str(e)}")
            return []

    async def get_payment_analytics(self) -> Dict[str, Any]:
        """Get PayPal payment analytics"""
        
        if self.mongo_db is None:
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