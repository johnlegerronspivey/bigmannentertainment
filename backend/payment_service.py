import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

from payment_models import (
    PaymentTransaction, BankAccount, DigitalWallet, RoyaltySplit, 
    RoyaltyPayment, UserEarnings, PayoutRequest, PlatformRevenue,
    TaxDocument, PaymentStatus, PaymentMethod, TransactionType,
    PayoutSchedule, RoyaltySplitType, EarningsSummary, PaymentPackage
)

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.stripe_api_key = os.environ.get('STRIPE_API_KEY')
        if not self.stripe_api_key:
            logger.warning("STRIPE_API_KEY not found in environment variables")
        
        # Predefined payment packages for security
        self.payment_packages = {
            "basic": PaymentPackage(
                id="basic",
                name="Basic Plan",
                description="Access to basic features",
                amount=9.99,
                features=["Upload media", "Basic analytics", "Standard support"]
            ),
            "premium": PaymentPackage(
                id="premium", 
                name="Premium Plan",
                description="Advanced features for professionals",
                amount=29.99,
                features=["Unlimited uploads", "Advanced analytics", "Priority support", "Royalty management"]
            ),
            "enterprise": PaymentPackage(
                id="enterprise",
                name="Enterprise Plan", 
                description="Full suite for labels and distributors",
                amount=99.99,
                features=["White-label platform", "API access", "Custom integrations", "Dedicated support"]
            ),
            "single_track": PaymentPackage(
                id="single_track",
                name="Single Track Purchase",
                description="Purchase individual track",
                amount=0.99,
                features=["High-quality download", "Personal use license"]
            ),
            "album": PaymentPackage(
                id="album",
                name="Album Purchase", 
                description="Purchase full album",
                amount=9.99,
                features=["All tracks", "High-quality downloads", "Bonus content"]
            )
        }

    def get_stripe_checkout(self, host_url: str) -> StripeCheckout:
        """Initialize Stripe checkout with webhook URL"""
        webhook_url = f"{host_url}/api/webhook/stripe"
        return StripeCheckout(api_key=self.stripe_api_key, webhook_url=webhook_url)

    async def create_checkout_session(self, request_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, str]:
        """Create a Stripe checkout session"""
        try:
            origin_url = request_data.get('origin_url')
            package_id = request_data.get('package_id')
            media_id = request_data.get('media_id')
            
            if not origin_url:
                raise ValueError("Origin URL is required")

            # Get amount from predefined packages for security
            if package_id and package_id in self.payment_packages:
                package = self.payment_packages[package_id]
                amount = package.amount
                currency = package.currency
                metadata = {
                    "package_id": package_id,
                    "package_name": package.name,
                    "user_id": user_id or "anonymous"
                }
            elif media_id:
                # Handle media purchase
                media = await self.db.media_content.find_one({"id": media_id})
                if not media:
                    raise ValueError("Media not found")
                amount = float(media.get('price', 0.99))
                currency = "usd"
                metadata = {
                    "media_id": media_id,
                    "media_title": media.get('title', 'Unknown'),
                    "user_id": user_id or "anonymous"
                }
            else:
                raise ValueError("Either package_id or media_id is required")

            # Add custom metadata
            if request_data.get('metadata'):
                metadata.update(request_data['metadata'])

            # Create success and cancel URLs
            success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{origin_url}/payment/cancel"

            # Initialize Stripe checkout
            stripe_checkout = self.get_stripe_checkout(origin_url)

            # Create checkout session request
            checkout_request = CheckoutSessionRequest(
                amount=amount,
                currency=currency,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )

            # Create checkout session
            session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)

            # Store transaction in database
            transaction = PaymentTransaction(
                user_id=user_id,
                session_id=session.session_id,
                stripe_session_id=session.session_id,
                amount=amount,
                currency=currency,
                payment_method=PaymentMethod.STRIPE,
                transaction_type=TransactionType.PURCHASE,
                status=PaymentStatus.INITIATED,
                metadata=metadata
            )

            # Convert to dict and handle datetime serialization
            transaction_dict = transaction.dict()
            transaction_dict['created_at'] = transaction.created_at
            transaction_dict['updated_at'] = transaction.updated_at

            await self.db.payment_transactions.insert_one(transaction_dict)

            logger.info(f"Created checkout session {session.session_id} for amount {amount} {currency}")

            return {
                "url": session.url,
                "session_id": session.session_id,
                "amount": amount,
                "currency": currency
            }

        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise

    async def get_checkout_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a checkout session"""
        try:
            # Get transaction from database
            transaction = await self.db.payment_transactions.find_one({"stripe_session_id": session_id})
            if not transaction:
                raise ValueError(f"Transaction not found for session {session_id}")

            # Get status from Stripe
            stripe_checkout = self.get_stripe_checkout("https://placeholder.com")  # URL not used for status check
            status_response: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)

            # Update transaction status if changed
            if transaction['status'] != status_response.payment_status:
                update_data = {
                    'status': status_response.payment_status,
                    'payment_status': status_response.payment_status,
                    'updated_at': datetime.utcnow()
                }

                # If payment completed, process royalties
                if status_response.payment_status == 'paid' and transaction['status'] != 'paid':
                    update_data['processed_at'] = datetime.utcnow()
                    await self.process_successful_payment(transaction, status_response)

                await self.db.payment_transactions.update_one(
                    {"stripe_session_id": session_id},
                    {"$set": update_data}
                )

            return {
                "status": status_response.status,
                "payment_status": status_response.payment_status,
                "amount_total": status_response.amount_total / 100,  # Convert from cents
                "currency": status_response.currency,
                "metadata": status_response.metadata
            }

        except Exception as e:
            logger.error(f"Error getting checkout status: {str(e)}")
            raise

    async def process_successful_payment(self, transaction: Dict[str, Any], status_response: CheckoutStatusResponse):
        """Process a successful payment and handle royalties"""
        try:
            metadata = transaction.get('metadata', {})
            media_id = metadata.get('media_id')
            amount = transaction['amount']

            # If this is a media purchase, process royalty splits
            if media_id:
                await self.process_royalty_splits(media_id, transaction['id'], amount)

            # Record platform revenue
            await self.record_platform_revenue(transaction)

            logger.info(f"Successfully processed payment for transaction {transaction['id']}")

        except Exception as e:
            logger.error(f"Error processing successful payment: {str(e)}")

    async def process_royalty_splits(self, media_id: str, transaction_id: str, total_amount: float):
        """Process royalty splits for a media purchase"""
        try:
            # Get royalty splits for this media
            splits_cursor = self.db.royalty_splits.find({"media_id": media_id, "is_active": True})
            splits = await splits_cursor.to_list(length=100)

            for split in splits:
                if split['split_type'] == RoyaltySplitType.PERCENTAGE:
                    royalty_amount = total_amount * (split['percentage'] / 100)
                else:
                    royalty_amount = split['fixed_amount']

                # Create royalty payment record
                royalty_payment = RoyaltyPayment(
                    media_id=media_id,
                    original_transaction_id=transaction_id,
                    recipient_id=split['recipient_id'],
                    recipient_email=split['recipient_email'],
                    amount=royalty_amount,
                    split_percentage=split.get('percentage', 0)
                )

                # Convert to dict and handle datetime serialization
                royalty_dict = royalty_payment.dict()
                royalty_dict['created_at'] = royalty_payment.created_at

                await self.db.royalty_payments.insert_one(royalty_dict)

                # Update user earnings
                await self.update_user_earnings(split['recipient_id'], royalty_amount)

            logger.info(f"Processed {len(splits)} royalty splits for media {media_id}")

        except Exception as e:
            logger.error(f"Error processing royalty splits: {str(e)}")

    async def update_user_earnings(self, user_id: str, amount: float):
        """Update user earnings balance"""
        try:
            # Get or create user earnings record
            earnings = await self.db.user_earnings.find_one({"user_id": user_id})
            
            if earnings:
                # Update existing earnings
                await self.db.user_earnings.update_one(
                    {"user_id": user_id},
                    {
                        "$inc": {
                            "total_earnings": amount,
                            "available_balance": amount
                        },
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
            else:
                # Create new earnings record
                new_earnings = UserEarnings(
                    user_id=user_id,
                    total_earnings=amount,
                    available_balance=amount
                )
                earnings_dict = new_earnings.dict()
                earnings_dict['created_at'] = new_earnings.created_at
                earnings_dict['updated_at'] = new_earnings.updated_at
                
                await self.db.user_earnings.insert_one(earnings_dict)

            logger.info(f"Updated earnings for user {user_id}: +${amount}")

        except Exception as e:
            logger.error(f"Error updating user earnings: {str(e)}")

    async def record_platform_revenue(self, transaction: Dict[str, Any]):
        """Record platform revenue from transaction"""
        try:
            # Platform takes 30% commission
            commission_rate = 0.30
            commission_amount = transaction['amount'] * commission_rate

            platform_revenue = PlatformRevenue(
                transaction_id=transaction['id'],
                revenue_type="commission",
                amount=commission_amount,
                percentage=commission_rate * 100
            )

            revenue_dict = platform_revenue.dict()
            revenue_dict['created_at'] = platform_revenue.created_at

            await self.db.platform_revenue.insert_one(revenue_dict)

            logger.info(f"Recorded platform revenue: ${commission_amount} from transaction {transaction['id']}")

        except Exception as e:
            logger.error(f"Error recording platform revenue: {str(e)}")

    # Bank Account Management
    async def add_bank_account(self, user_id: str, account_data: Dict[str, Any]) -> str:
        """Add a bank account for a user"""
        try:
            # If this is marked as primary, unset other primary accounts
            if account_data.get('is_primary'):
                await self.db.bank_accounts.update_many(
                    {"user_id": user_id},
                    {"$set": {"is_primary": False}}
                )

            bank_account = BankAccount(
                user_id=user_id,
                **account_data
            )

            account_dict = bank_account.dict()
            account_dict['created_at'] = bank_account.created_at
            account_dict['updated_at'] = bank_account.updated_at

            await self.db.bank_accounts.insert_one(account_dict)
            return bank_account.id

        except Exception as e:
            logger.error(f"Error adding bank account: {str(e)}")
            raise

    async def get_user_bank_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bank accounts for a user"""
        try:
            cursor = self.db.bank_accounts.find({"user_id": user_id})
            accounts = await cursor.to_list(length=100)
            
            # Convert ObjectId to string for serialization
            for account in accounts:
                if "_id" in account:
                    account["_id"] = str(account["_id"])
            
            return accounts

        except Exception as e:
            logger.error(f"Error getting user bank accounts: {str(e)}")
            return []

    # Digital Wallet Management
    async def add_digital_wallet(self, user_id: str, wallet_data: Dict[str, Any]) -> str:
        """Add a digital wallet for a user"""
        try:
            if wallet_data.get('is_primary'):
                await self.db.digital_wallets.update_many(
                    {"user_id": user_id},
                    {"$set": {"is_primary": False}}
                )

            wallet = DigitalWallet(
                user_id=user_id,
                **wallet_data
            )

            wallet_dict = wallet.dict()
            wallet_dict['created_at'] = wallet.created_at
            wallet_dict['updated_at'] = wallet.updated_at

            await self.db.digital_wallets.insert_one(wallet_dict)
            return wallet.id

        except Exception as e:
            logger.error(f"Error adding digital wallet: {str(e)}")
            raise

    async def get_user_digital_wallets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all digital wallets for user"""
        try:
            cursor = self.db.digital_wallets.find({"user_id": user_id})
            wallets = await cursor.to_list(length=100)
            
            for wallet in wallets:
                if "_id" in wallet:
                    wallet["_id"] = str(wallet["_id"])
            
            return wallets

        except Exception as e:
            logger.error(f"Error getting user digital wallets: {str(e)}")
            return []

    # Royalty Management
    async def create_royalty_split(self, split_data: Dict[str, Any]) -> str:
        """Create a royalty split for media"""
        try:
            royalty_split = RoyaltySplit(**split_data)

            split_dict = royalty_split.dict()
            split_dict['created_at'] = royalty_split.created_at
            split_dict['updated_at'] = royalty_split.updated_at

            await self.db.royalty_splits.insert_one(split_dict)
            return royalty_split.id

        except Exception as e:
            logger.error(f"Error creating royalty split: {str(e)}")
            raise

    async def get_media_royalty_splits(self, media_id: str) -> List[Dict[str, Any]]:
        """Get royalty splits for media"""
        try:
            cursor = self.db.royalty_splits.find({"media_id": media_id, "is_active": True})
            splits = await cursor.to_list(length=100)
            
            for split in splits:
                if "_id" in split:
                    split["_id"] = str(split["_id"])
            
            return splits

        except Exception as e:
            logger.error(f"Error getting media royalty splits: {str(e)}")
            return []

    # Earnings and Payouts
    async def get_user_earnings(self, user_id: str) -> Dict[str, Any]:
        """Get user earnings summary"""
        try:
            earnings = await self.db.user_earnings.find_one({"user_id": user_id})
            if not earnings:
                # Create default earnings record
                default_earnings = UserEarnings(user_id=user_id)
                earnings_dict = default_earnings.dict()
                earnings_dict['created_at'] = default_earnings.created_at
                earnings_dict['updated_at'] = default_earnings.updated_at
                
                await self.db.user_earnings.insert_one(earnings_dict)
                earnings = earnings_dict

            # Get recent transactions
            recent_cursor = self.db.royalty_payments.find(
                {"recipient_id": user_id}
            ).sort("created_at", -1).limit(10)
            recent_transactions = await recent_cursor.to_list(length=10)

            # Convert ObjectId to string
            if "_id" in earnings:
                earnings["_id"] = str(earnings["_id"])
            
            for transaction in recent_transactions:
                if "_id" in transaction:
                    transaction["_id"] = str(transaction["_id"])

            return {
                "earnings": earnings,
                "recent_transactions": recent_transactions
            }

        except Exception as e:
            logger.error(f"Error getting user earnings: {str(e)}")
            return {"earnings": {}, "recent_transactions": []}

    async def request_payout(self, user_id: str, payout_data: Dict[str, Any]) -> str:
        """Request a payout"""
        try:
            # Check if user has sufficient balance
            earnings = await self.db.user_earnings.find_one({"user_id": user_id})
            if not earnings or earnings['available_balance'] < payout_data['amount']:
                raise ValueError("Insufficient balance for payout")

            # Check minimum payout threshold
            if payout_data['amount'] < earnings.get('minimum_payout_threshold', 10.0):
                raise ValueError(f"Minimum payout amount is ${earnings.get('minimum_payout_threshold', 10.0)}")

            payout_request = PayoutRequest(
                user_id=user_id,
                **payout_data
            )

            payout_dict = payout_request.dict()
            payout_dict['requested_at'] = payout_request.requested_at

            await self.db.payout_requests.insert_one(payout_dict)

            # Update user balance (move from available to pending)
            await self.db.user_earnings.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "available_balance": -payout_data['amount'],
                        "pending_balance": payout_data['amount']
                    }
                }
            )

            return payout_request.id

        except Exception as e:
            logger.error(f"Error requesting payout: {str(e)}")
            raise

    async def get_payment_packages(self) -> List[Dict[str, Any]]:
        """Get available payment packages"""
        return [package.dict() for package in self.payment_packages.values()]