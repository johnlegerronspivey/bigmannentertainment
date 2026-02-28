import os
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from stripe_native_service import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Import our models
from payment_models import PaymentTransaction, PaymentStatus, PaymentMethod, TransactionType

logger = logging.getLogger(__name__)

class StripePaymentService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.stripe_api_key = os.environ.get('STRIPE_API_KEY')
        if not self.stripe_api_key:
            raise ValueError("STRIPE_API_KEY environment variable is required")
        
        # Initialize Stripe checkout service
        self.stripe_checkout = None
        
    def initialize_stripe_checkout(self, host_url: str):
        """Initialize Stripe checkout with webhook URL"""
        webhook_url = f"{host_url.rstrip('/')}/api/webhook/stripe"
        self.stripe_checkout = StripeCheckout(
            api_key=self.stripe_api_key, 
            webhook_url=webhook_url
        )
        logger.info(f"Stripe checkout initialized with webhook URL: {webhook_url}")
    
    # Payment packages configuration
    PAYMENT_PACKAGES = {
        "basic_upload": {
            "name": "Basic Upload Package",
            "description": "Upload up to 10 tracks with basic distribution",
            "amount": 9.99,
            "features": ["10 track uploads", "Basic distribution", "Analytics dashboard"]
        },
        "premium_upload": {
            "name": "Premium Upload Package", 
            "description": "Upload up to 50 tracks with premium distribution",
            "amount": 29.99,
            "features": ["50 track uploads", "Premium distribution", "Advanced analytics", "Priority support"]
        },
        "pro_upload": {
            "name": "Pro Upload Package",
            "description": "Unlimited uploads with full distribution network",
            "amount": 99.99,
            "features": ["Unlimited uploads", "Full distribution network", "Revenue analytics", "Dedicated support"]
        },
        "distribution_fee": {
            "name": "Distribution Fee",
            "description": "One-time fee for distribution to selected platforms",
            "amount": 4.99,
            "features": ["Distribution to selected platforms", "Real-time status tracking"]
        }
    }
    
    async def create_checkout_session(self, package_id: Optional[str], amount: Optional[float], 
                                    currency: str, stripe_price_id: Optional[str], 
                                    quantity: int, success_url: str, cancel_url: str,
                                    metadata: Optional[Dict[str, str]], user_id: Optional[str] = None,
                                    email: Optional[str] = None) -> CheckoutSessionResponse:
        """Create a Stripe checkout session"""
        
        if not self.stripe_checkout:
            raise HTTPException(status_code=500, detail="Stripe checkout not initialized")
        
        # Determine amount and package info
        final_amount = None
        package_name = None
        package_type = None
        
        if package_id and package_id in self.PAYMENT_PACKAGES:
            # Use predefined package
            package_info = self.PAYMENT_PACKAGES[package_id]
            final_amount = package_info["amount"]
            package_name = package_info["name"]
            package_type = package_id
            
        elif amount is not None:
            # Use custom amount
            final_amount = float(amount)
            package_name = "Custom Payment"
            package_type = "custom"
        
        elif stripe_price_id:
            # Use Stripe price ID for subscriptions
            package_name = "Subscription"
            package_type = "subscription"
            
        else:
            raise HTTPException(status_code=400, detail="Must provide either package_id, amount, or stripe_price_id")
        
        # Prepare metadata
        session_metadata = {
            "user_id": user_id or "",
            "email": email or "",
            "package_id": package_id or "",
            "package_type": package_type or "",
            "source": "big_mann_entertainment"
        }
        if metadata:
            session_metadata.update(metadata)
        
        try:
            # Create checkout session request
            if stripe_price_id:
                # For subscription/recurring payments
                checkout_request = CheckoutSessionRequest(
                    stripe_price_id=stripe_price_id,
                    quantity=quantity,
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata=session_metadata
                )
            else:
                # For one-time payments
                checkout_request = CheckoutSessionRequest(
                    amount=final_amount,
                    currency=currency,
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata=session_metadata
                )
            
            # Create session with Stripe
            session_response = await self.stripe_checkout.create_checkout_session(checkout_request)
            
            # Store transaction in database
            transaction = PaymentTransaction(
                user_id=user_id,
                email=email,
                session_id=session_response.session_id,
                amount=final_amount or 0.0,
                currency=currency,
                payment_method=PaymentMethod.STRIPE,
                transaction_type=TransactionType.SUBSCRIPTION if stripe_price_id else TransactionType.PURCHASE,
                status=PaymentStatus.INITIATED,
                payment_status="initiated",
                metadata={
                    "package_id": package_id,
                    "package_name": package_name,
                    "package_type": package_type,
                    "stripe_price_id": stripe_price_id,
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    **session_metadata
                }
            )
            
            await self.db.payment_transactions.insert_one(transaction.dict())
            logger.info(f"Created payment transaction for session {session_response.session_id}")
            
            return session_response
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")
    
    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        """Get the status of a checkout session"""
        
        if not self.stripe_checkout:
            raise HTTPException(status_code=500, detail="Stripe checkout not initialized")
        
        try:
            # Get status from Stripe
            status_response = await self.stripe_checkout.get_checkout_status(session_id)
            
            # Update transaction in database
            transaction = await self.db.payment_transactions.find_one({"session_id": session_id})
            if transaction:
                # Prevent duplicate processing
                if transaction.get("payment_status") != "paid" and status_response.payment_status == "paid":
                    # Update transaction status
                    await self.db.payment_transactions.update_one(
                        {"session_id": session_id},
                        {
                            "$set": {
                                "status": PaymentStatus.COMPLETED.value,
                                "payment_status": status_response.payment_status,
                                "stripe_status": status_response.status,
                                "processed_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    # Process post-payment actions
                    await self._process_successful_payment(transaction, status_response)
                    
                elif status_response.status in ["expired", "canceled"]:
                    # Update failed/expired status
                    await self.db.payment_transactions.update_one(
                        {"session_id": session_id},
                        {
                            "$set": {
                                "status": PaymentStatus.EXPIRED.value if status_response.status == "expired" else PaymentStatus.FAILED.value,
                                "payment_status": status_response.payment_status,
                                "stripe_status": status_response.status,
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
            
            return status_response
            
        except Exception as e:
            logger.error(f"Error getting checkout status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get checkout status: {str(e)}")
    
    async def handle_webhook(self, webhook_body: bytes, stripe_signature: str):
        """Handle Stripe webhook events"""
        
        if not self.stripe_checkout:
            raise HTTPException(status_code=500, detail="Stripe checkout not initialized")
        
        try:
            # Process webhook with stripe integration
            webhook_response = await self.stripe_checkout.handle_webhook(webhook_body, stripe_signature)
            
            logger.info(f"Webhook received: {webhook_response.event_type} for session {webhook_response.session_id}")
            
            # Process webhook based on event type
            if webhook_response.event_type == "checkout.session.completed":
                await self._handle_checkout_completed(webhook_response)
            elif webhook_response.event_type == "payment_intent.succeeded":
                await self._handle_payment_succeeded(webhook_response)
            elif webhook_response.event_type == "payment_intent.payment_failed":
                await self._handle_payment_failed(webhook_response)
            
            return webhook_response
            
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")
    
    async def _handle_checkout_completed(self, webhook_response):
        """Handle checkout session completed webhook"""
        session_id = webhook_response.session_id
        
        # Update transaction status
        if session_id:
            await self.db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": PaymentStatus.COMPLETED.value,
                        "payment_status": webhook_response.payment_status,
                        "processed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Get transaction details for post-processing
            transaction = await self.db.payment_transactions.find_one({"session_id": session_id})
            if transaction:
                await self._process_successful_payment(transaction, webhook_response)
    
    async def _handle_payment_succeeded(self, webhook_response):
        """Handle payment succeeded webhook"""
        # Additional processing for successful payments
        logger.info(f"Payment succeeded for session {webhook_response.session_id}")
    
    async def _handle_payment_failed(self, webhook_response):
        """Handle payment failed webhook"""
        session_id = webhook_response.session_id
        
        if session_id:
            await self.db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": PaymentStatus.FAILED.value,
                        "payment_status": "failed",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
    
    async def _process_successful_payment(self, transaction: dict, payment_data):
        """Process actions after successful payment"""
        try:
            user_id = transaction.get("user_id")
            package_type = transaction.get("metadata", {}).get("package_type")
            amount = transaction.get("amount", 0.0)
            
            # Update user credits/features based on package
            if user_id and package_type:
                await self._update_user_credits(user_id, package_type, amount)
            
            # Process revenue sharing if applicable
            media_id = transaction.get("metadata", {}).get("media_id")
            if media_id:
                await self._process_revenue_sharing(transaction["id"], media_id, amount)
            
            logger.info(f"Post-payment processing completed for transaction {transaction['id']}")
            
        except Exception as e:
            logger.error(f"Error in post-payment processing: {str(e)}")
    
    async def _update_user_credits(self, user_id: str, package_type: str, amount: float):
        """Update user credits/features based on purchased package"""
        try:
            # Get or create user credits
            user_credits = await self.db.user_credits.find_one({"user_id": user_id})
            
            if not user_credits:
                user_credits = {
                    "user_id": user_id,
                    "upload_credits": 0,
                    "distribution_credits": 0,
                    "premium_features": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            
            # Add credits based on package type
            if package_type == "basic_upload":
                user_credits["upload_credits"] = user_credits.get("upload_credits", 0) + 10
            elif package_type == "premium_upload":
                user_credits["upload_credits"] = user_credits.get("upload_credits", 0) + 50
                user_credits["premium_features"] = True
            elif package_type == "pro_upload":
                user_credits["upload_credits"] = user_credits.get("upload_credits", 0) + 999  # Unlimited
                user_credits["premium_features"] = True
            elif package_type == "distribution_fee":
                user_credits["distribution_credits"] = user_credits.get("distribution_credits", 0) + 1
            
            user_credits["updated_at"] = datetime.utcnow()
            
            # Upsert user credits
            await self.db.user_credits.update_one(
                {"user_id": user_id},
                {"$set": user_credits},
                upsert=True
            )
            
            logger.info(f"Updated credits for user {user_id}: {package_type}")
            
        except Exception as e:
            logger.error(f"Error updating user credits: {str(e)}")
    
    async def _process_revenue_sharing(self, transaction_id: str, media_id: str, amount: float):
        """Process revenue sharing for content creators"""
        try:
            # Get media details
            media = await self.db.media_content.find_one({"id": media_id})
            if not media:
                return
            
            # Get revenue split configuration (default: 85% creator, 15% platform)
            creator_percentage = 85.0
            platform_percentage = 15.0
            
            creator_amount = amount * (creator_percentage / 100)
            platform_amount = amount * (platform_percentage / 100)
            
            # Create revenue share record
            revenue_share = {
                "id": str(uuid.uuid4()),
                "transaction_id": transaction_id,
                "media_id": media_id,
                "creator_user_id": media.get("owner_id"),
                "total_amount": amount,
                "creator_percentage": creator_percentage,
                "platform_percentage": platform_percentage,
                "creator_amount": creator_amount,
                "platform_amount": platform_amount,
                "currency": "usd",
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.db.revenue_shares.insert_one(revenue_share)
            
            # Update creator earnings
            await self._update_creator_earnings(media.get("owner_id"), creator_amount)
            
            logger.info(f"Revenue sharing processed for transaction {transaction_id}")
            
        except Exception as e:
            logger.error(f"Error processing revenue sharing: {str(e)}")
    
    async def _update_creator_earnings(self, creator_id: str, amount: float):
        """Update creator earnings balance"""
        try:
            if not creator_id:
                return
                
            # Update creator earnings
            await self.db.user_earnings.update_one(
                {"user_id": creator_id},
                {
                    "$inc": {
                        "total_earnings": amount,
                        "pending_balance": amount
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            logger.info(f"Updated earnings for creator {creator_id}: +${amount}")
            
        except Exception as e:
            logger.error(f"Error updating creator earnings: {str(e)}")
    
    async def get_payment_packages(self) -> Dict[str, Any]:
        """Get available payment packages"""
        return self.PAYMENT_PACKAGES
    
    async def get_user_transactions(self, user_id: str, limit: int = 50) -> list:
        """Get user's payment transactions"""
        try:
            transactions = []
            async for transaction in self.db.payment_transactions.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit):
                transactions.append(transaction)
            return transactions
        except Exception as e:
            logger.error(f"Error getting user transactions: {str(e)}")
            return []