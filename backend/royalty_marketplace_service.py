"""
Dynamic Royalty Marketplace Service
Enterprise-grade marketplace for royalty trading, auctions, and smart contract pricing
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os
import hashlib

logger = logging.getLogger(__name__)

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'royalty_marketplace')]


class ListingStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    PAUSED = "paused"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ListingType(str, Enum):
    FIXED_PRICE = "fixed_price"
    AUCTION = "auction"
    DUTCH_AUCTION = "dutch_auction"  # Price decreases over time
    RESERVE_AUCTION = "reserve_auction"  # Has minimum price


class RoyaltyType(str, Enum):
    FULL_OWNERSHIP = "full_ownership"  # 100% of future royalties
    PERCENTAGE_SHARE = "percentage_share"  # Partial share
    TIME_LIMITED = "time_limited"  # Limited duration
    REVENUE_CAP = "revenue_cap"  # Up to X amount


class PaymentCurrency(str, Enum):
    USD = "usd"
    ETH = "eth"
    USDC = "usdc"
    USDT = "usdt"


class BidStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    OUTBID = "outbid"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# Pydantic Models
class RoyaltyListing(BaseModel):
    """Marketplace listing for royalty rights"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    seller_id: str = ""  # Will be set by the endpoint
    title: str
    description: str
    
    # Listing configuration
    listing_type: ListingType
    status: ListingStatus = ListingStatus.DRAFT
    
    # Royalty details
    royalty_type: RoyaltyType
    royalty_percentage: Decimal  # Percentage of royalties being sold (1-100)
    historical_revenue: Decimal = Decimal("0")  # Past 12 months revenue
    projected_revenue: Decimal = Decimal("0")  # Projected annual revenue
    
    # Pricing
    asking_price: Decimal
    minimum_price: Optional[Decimal] = None  # For reserve auctions
    buy_now_price: Optional[Decimal] = None  # Instant purchase option
    payment_currencies: List[PaymentCurrency] = [PaymentCurrency.USD]
    
    # Time limits
    duration_months: Optional[int] = None  # For time-limited royalties
    revenue_cap: Optional[Decimal] = None  # For capped royalties
    
    # Auction settings
    auction_start: Optional[datetime] = None
    auction_end: Optional[datetime] = None
    bid_increment: Decimal = Decimal("100")
    current_bid: Optional[Decimal] = None
    highest_bidder_id: Optional[str] = None
    
    # Smart contract
    contract_address: Optional[str] = None
    blockchain_network: str = "ethereum"
    
    # Metrics
    view_count: int = 0
    bid_count: int = 0
    watchlist_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = []
    genre: Optional[str] = None
    artist_name: Optional[str] = None
    asset_title: Optional[str] = None
    verification_status: str = "pending"
    featured: bool = False


class Bid(BaseModel):
    """Bid on a royalty listing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    bidder_id: str
    
    amount: Decimal
    payment_currency: PaymentCurrency = PaymentCurrency.USD
    
    status: BidStatus = BidStatus.PENDING
    
    # Auto-bid settings
    max_amount: Optional[Decimal] = None  # For proxy bidding
    auto_increment: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    responded_at: Optional[datetime] = None
    
    # Notes
    message: Optional[str] = None
    response_message: Optional[str] = None


class Transaction(BaseModel):
    """Marketplace transaction record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    seller_id: str
    buyer_id: str
    
    # Sale details
    sale_price: Decimal
    payment_currency: PaymentCurrency
    
    # Fees
    platform_fee: Decimal  # Platform commission
    seller_net: Decimal  # Amount seller receives
    
    # Status
    status: str = "pending"  # pending, processing, completed, failed, refunded
    
    # Payment details
    payment_method: str = "crypto"
    transaction_hash: Optional[str] = None
    escrow_address: Optional[str] = None
    
    # Smart contract transfer
    royalty_contract_address: Optional[str] = None
    transfer_tx_hash: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payment_received_at: Optional[datetime] = None
    transfer_completed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class Watchlist(BaseModel):
    """User watchlist for listings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    listing_id: str
    price_alert: Optional[Decimal] = None  # Alert when price drops below
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PriceHistory(BaseModel):
    """Track listing price changes"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    price: Decimal
    bid_id: Optional[str] = None
    change_type: str  # initial, bid, price_update, dutch_decrease
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def serialize_for_mongo(obj):
    """Convert a dict to MongoDB-compatible format (handle Decimal, Enum, etc.)"""
    if isinstance(obj, dict):
        return {k: serialize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_mongo(item) for item in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, 'value'):  # Handle any Enum-like objects
        return obj.value
    return obj


class RoyaltyMarketplaceService:
    """Core marketplace service for royalty trading"""
    
    def __init__(self):
        self.listings = db.marketplace_listings
        self.bids = db.marketplace_bids
        self.transactions = db.marketplace_transactions
        self.watchlists = db.marketplace_watchlists
        self.price_history = db.marketplace_price_history
        self.analytics = db.marketplace_analytics
        
    # Listing Management
    async def create_listing(self, listing: RoyaltyListing) -> Dict[str, Any]:
        """Create a new royalty listing"""
        try:
            # Validate royalty ownership
            # In production, verify seller owns the royalty rights
            
            # Calculate smart pricing recommendation
            pricing_recommendation = await self._calculate_pricing(listing)
            
            # Store the listing - serialize for MongoDB
            listing_dict = serialize_for_mongo(listing.dict())
            listing_dict["pricing_recommendation"] = pricing_recommendation
            await self.listings.insert_one(listing_dict)
            
            # Record initial price
            await self._record_price_change(listing.id, listing.asking_price, "initial")
            
            logger.info(f"Created listing {listing.id} for asset {listing.asset_id}")
            
            return {
                "success": True,
                "listing_id": listing.id,
                "pricing_recommendation": pricing_recommendation
            }
            
        except Exception as e:
            logger.error(f"Failed to create listing: {str(e)}")
            raise
    
    async def update_listing(self, listing_id: str, updates: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update an existing listing"""
        try:
            # Verify ownership
            listing = await self.listings.find_one({"id": listing_id})
            if not listing:
                raise ValueError("Listing not found")
            if listing["seller_id"] != user_id:
                raise ValueError("Not authorized to update this listing")
            if listing["status"] in [ListingStatus.SOLD.value, ListingStatus.CANCELLED.value]:
                raise ValueError("Cannot update a completed listing")
            
            # Record price change if price was updated
            if "asking_price" in updates and float(updates["asking_price"]) != float(listing["asking_price"]):
                await self._record_price_change(listing_id, Decimal(str(updates["asking_price"])), "price_update")
            
            updates["updated_at"] = datetime.now(timezone.utc)
            
            await self.listings.update_one(
                {"id": listing_id},
                {"$set": updates}
            )
            
            return {"success": True, "message": "Listing updated successfully"}
            
        except Exception as e:
            logger.error(f"Failed to update listing {listing_id}: {str(e)}")
            raise
    
    async def publish_listing(self, listing_id: str, user_id: str) -> Dict[str, Any]:
        """Publish a draft listing to the marketplace"""
        try:
            listing = await self.listings.find_one({"id": listing_id})
            if not listing:
                raise ValueError("Listing not found")
            if listing["seller_id"] != user_id:
                raise ValueError("Not authorized")
            if listing["status"] != ListingStatus.DRAFT.value:
                raise ValueError("Listing must be in draft status to publish")
            
            # Set auction times if auction type
            updates = {
                "status": ListingStatus.ACTIVE.value,
                "published_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            if listing["listing_type"] in [ListingType.AUCTION.value, ListingType.DUTCH_AUCTION.value, ListingType.RESERVE_AUCTION.value]:
                if not listing.get("auction_end"):
                    # Default 7-day auction
                    updates["auction_start"] = datetime.now(timezone.utc)
                    updates["auction_end"] = datetime.now(timezone.utc) + timedelta(days=7)
            
            await self.listings.update_one(
                {"id": listing_id},
                {"$set": updates}
            )
            
            return {"success": True, "message": "Listing published successfully"}
            
        except Exception as e:
            logger.error(f"Failed to publish listing {listing_id}: {str(e)}")
            raise
    
    async def get_listing(self, listing_id: str, increment_views: bool = True) -> Dict[str, Any]:
        """Get listing details"""
        try:
            listing = await self.listings.find_one({"id": listing_id}, {"_id": 0})
            if not listing:
                raise ValueError("Listing not found")
            
            if increment_views:
                await self.listings.update_one(
                    {"id": listing_id},
                    {"$inc": {"view_count": 1}}
                )
            
            # Get bid history
            bids = await self.bids.find(
                {"listing_id": listing_id},
                {"_id": 0}
            ).sort("created_at", -1).limit(10).to_list(length=None)
            
            # Get price history
            prices = await self.price_history.find(
                {"listing_id": listing_id},
                {"_id": 0}
            ).sort("timestamp", -1).limit(20).to_list(length=None)
            
            return {
                "success": True,
                "listing": listing,
                "recent_bids": bids,
                "price_history": prices
            }
            
        except Exception as e:
            logger.error(f"Failed to get listing {listing_id}: {str(e)}")
            raise
    
    async def search_listings(
        self,
        query: Optional[str] = None,
        listing_type: Optional[ListingType] = None,
        royalty_type: Optional[RoyaltyType] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        genre: Optional[str] = None,
        featured_only: bool = False,
        sort_by: str = "created_at",
        sort_order: int = -1,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search and filter marketplace listings"""
        try:
            # Build query
            match_query = {"status": ListingStatus.ACTIVE.value}
            
            if query:
                match_query["$or"] = [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"artist_name": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            
            if listing_type:
                match_query["listing_type"] = listing_type.value
            
            if royalty_type:
                match_query["royalty_type"] = royalty_type.value
            
            if min_price is not None:
                match_query["asking_price"] = {"$gte": float(min_price)}
            
            if max_price is not None:
                if "asking_price" in match_query:
                    match_query["asking_price"]["$lte"] = float(max_price)
                else:
                    match_query["asking_price"] = {"$lte": float(max_price)}
            
            if genre:
                match_query["genre"] = genre
            
            if featured_only:
                match_query["featured"] = True
            
            # Execute query with pagination
            skip = (page - 1) * limit
            
            cursor = self.listings.find(match_query, {"_id": 0})
            cursor = cursor.sort(sort_by, sort_order).skip(skip).limit(limit)
            listings = await cursor.to_list(length=None)
            
            # Get total count
            total = await self.listings.count_documents(match_query)
            
            return {
                "success": True,
                "listings": listings,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to search listings: {str(e)}")
            raise
    
    # Bidding System
    async def place_bid(self, bid: Bid) -> Dict[str, Any]:
        """Place a bid on an auction listing"""
        try:
            listing = await self.listings.find_one({"id": bid.listing_id})
            if not listing:
                raise ValueError("Listing not found")
            
            if listing["status"] != ListingStatus.ACTIVE.value:
                raise ValueError("Listing is not active")
            
            if listing["listing_type"] not in [ListingType.AUCTION.value, ListingType.RESERVE_AUCTION.value]:
                raise ValueError("This listing does not accept bids")
            
            # Check auction timing
            now = datetime.now(timezone.utc)
            if listing.get("auction_end") and now > listing["auction_end"]:
                raise ValueError("Auction has ended")
            
            # Validate bid amount
            current_bid = listing.get("current_bid", listing["asking_price"])
            min_bid = Decimal(str(current_bid)) + Decimal(str(listing.get("bid_increment", 100)))
            
            if bid.amount < min_bid:
                raise ValueError(f"Bid must be at least {min_bid}")
            
            # Don't allow self-bidding
            if bid.bidder_id == listing["seller_id"]:
                raise ValueError("Cannot bid on your own listing")
            
            # Mark previous highest bid as outbid
            if listing.get("highest_bidder_id"):
                await self.bids.update_many(
                    {"listing_id": bid.listing_id, "status": BidStatus.PENDING.value},
                    {"$set": {"status": BidStatus.OUTBID.value, "updated_at": now}}
                )
            
            # Store the bid
            await self.bids.insert_one(serialize_for_mongo(bid.dict()))
            
            # Update listing with new highest bid
            await self.listings.update_one(
                {"id": bid.listing_id},
                {
                    "$set": {
                        "current_bid": float(bid.amount),
                        "highest_bidder_id": bid.bidder_id,
                        "updated_at": now
                    },
                    "$inc": {"bid_count": 1}
                }
            )
            
            # Record price change
            await self._record_price_change(bid.listing_id, bid.amount, "bid", bid.id)
            
            # Extend auction if bid placed in last 5 minutes
            if listing.get("auction_end"):
                time_remaining = listing["auction_end"] - now
                if time_remaining.total_seconds() < 300:  # Less than 5 minutes
                    new_end = now + timedelta(minutes=5)
                    await self.listings.update_one(
                        {"id": bid.listing_id},
                        {"$set": {"auction_end": new_end}}
                    )
            
            logger.info(f"Bid {bid.id} placed on listing {bid.listing_id}")
            
            return {
                "success": True,
                "bid_id": bid.id,
                "message": "Bid placed successfully",
                "new_current_bid": float(bid.amount)
            }
            
        except Exception as e:
            logger.error(f"Failed to place bid: {str(e)}")
            raise
    
    async def get_user_bids(self, user_id: str, status: Optional[BidStatus] = None) -> List[Dict[str, Any]]:
        """Get all bids by a user"""
        try:
            query = {"bidder_id": user_id}
            if status:
                query["status"] = status.value
            
            bids = await self.bids.find(query, {"_id": 0}).sort("created_at", -1).to_list(length=None)
            
            # Enrich with listing info
            for bid in bids:
                listing = await self.listings.find_one({"id": bid["listing_id"]}, {"_id": 0, "title": 1, "asset_title": 1, "status": 1})
                bid["listing_info"] = listing
            
            return bids
            
        except Exception as e:
            logger.error(f"Failed to get user bids: {str(e)}")
            raise
    
    # Purchase Flow
    async def buy_now(self, listing_id: str, buyer_id: str, payment_currency: PaymentCurrency = PaymentCurrency.USD) -> Dict[str, Any]:
        """Instant purchase at buy now price"""
        try:
            listing = await self.listings.find_one({"id": listing_id})
            if not listing:
                raise ValueError("Listing not found")
            
            if listing["status"] != ListingStatus.ACTIVE.value:
                raise ValueError("Listing is not active")
            
            if not listing.get("buy_now_price"):
                raise ValueError("This listing does not have a buy now option")
            
            if buyer_id == listing["seller_id"]:
                raise ValueError("Cannot purchase your own listing")
            
            # Create transaction
            platform_fee = Decimal(str(listing["buy_now_price"])) * Decimal("0.05")  # 5% platform fee
            seller_net = Decimal(str(listing["buy_now_price"])) - platform_fee
            
            transaction = Transaction(
                listing_id=listing_id,
                seller_id=listing["seller_id"],
                buyer_id=buyer_id,
                sale_price=Decimal(str(listing["buy_now_price"])),
                payment_currency=payment_currency,
                platform_fee=platform_fee,
                seller_net=seller_net,
                status="pending"
            )
            
            await self.transactions.insert_one(serialize_for_mongo(transaction.dict()))
            
            # Update listing status
            await self.listings.update_one(
                {"id": listing_id},
                {
                    "$set": {
                        "status": ListingStatus.SOLD.value,
                        "sold_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"Buy now executed for listing {listing_id}")
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "message": "Purchase initiated. Please complete payment.",
                "payment_amount": float(listing["buy_now_price"]),
                "platform_fee": float(platform_fee)
            }
            
        except Exception as e:
            logger.error(f"Failed to execute buy now: {str(e)}")
            raise
    
    async def accept_bid(self, listing_id: str, bid_id: str, seller_id: str) -> Dict[str, Any]:
        """Accept a bid and initiate transaction"""
        try:
            listing = await self.listings.find_one({"id": listing_id})
            if not listing:
                raise ValueError("Listing not found")
            
            if listing["seller_id"] != seller_id:
                raise ValueError("Not authorized")
            
            bid = await self.bids.find_one({"id": bid_id, "listing_id": listing_id})
            if not bid:
                raise ValueError("Bid not found")
            
            if bid["status"] != BidStatus.PENDING.value:
                raise ValueError("Bid is no longer valid")
            
            # Create transaction
            platform_fee = Decimal(str(bid["amount"])) * Decimal("0.05")
            seller_net = Decimal(str(bid["amount"])) - platform_fee
            
            transaction = Transaction(
                listing_id=listing_id,
                seller_id=listing["seller_id"],
                buyer_id=bid["bidder_id"],
                sale_price=Decimal(str(bid["amount"])),
                payment_currency=PaymentCurrency(bid.get("payment_currency", "usd")),
                platform_fee=platform_fee,
                seller_net=seller_net,
                status="pending"
            )
            
            await self.transactions.insert_one(serialize_for_mongo(transaction.dict()))
            
            # Update bid status
            await self.bids.update_one(
                {"id": bid_id},
                {
                    "$set": {
                        "status": BidStatus.ACCEPTED.value,
                        "responded_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Reject all other bids
            await self.bids.update_many(
                {"listing_id": listing_id, "id": {"$ne": bid_id}},
                {"$set": {"status": BidStatus.REJECTED.value}}
            )
            
            # Update listing
            await self.listings.update_one(
                {"id": listing_id},
                {
                    "$set": {
                        "status": ListingStatus.SOLD.value,
                        "sold_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "message": "Bid accepted. Awaiting buyer payment."
            }
            
        except Exception as e:
            logger.error(f"Failed to accept bid: {str(e)}")
            raise
    
    async def complete_transaction(self, transaction_id: str, payment_proof: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a transaction after payment confirmation"""
        try:
            transaction = await self.transactions.find_one({"id": transaction_id})
            if not transaction:
                raise ValueError("Transaction not found")
            
            if transaction["status"] != "pending":
                raise ValueError("Transaction is not in pending status")
            
            now = datetime.now(timezone.utc)
            
            # In production, verify payment proof with payment processor
            # For now, we'll simulate verification
            
            await self.transactions.update_one(
                {"id": transaction_id},
                {
                    "$set": {
                        "status": "completed",
                        "payment_received_at": now,
                        "completed_at": now,
                        "transaction_hash": payment_proof.get("tx_hash", f"tx_{uuid.uuid4().hex[:16]}")
                    }
                }
            )
            
            # Transfer royalty rights (in production, interact with smart contract)
            # This would update the royalty contract ownership
            
            logger.info(f"Transaction {transaction_id} completed")
            
            return {
                "success": True,
                "message": "Transaction completed. Royalty rights transferred.",
                "transaction_id": transaction_id
            }
            
        except Exception as e:
            logger.error(f"Failed to complete transaction: {str(e)}")
            raise
    
    # Watchlist
    async def add_to_watchlist(self, user_id: str, listing_id: str, price_alert: Optional[Decimal] = None) -> Dict[str, Any]:
        """Add listing to user's watchlist"""
        try:
            # Check if already watching
            existing = await self.watchlists.find_one({"user_id": user_id, "listing_id": listing_id})
            if existing:
                # Update price alert
                await self.watchlists.update_one(
                    {"id": existing["id"]},
                    {"$set": {"price_alert": float(price_alert) if price_alert else None}}
                )
                return {"success": True, "message": "Watchlist updated"}
            
            watchlist = Watchlist(
                user_id=user_id,
                listing_id=listing_id,
                price_alert=price_alert
            )
            
            await self.watchlists.insert_one(serialize_for_mongo(watchlist.dict()))
            
            # Increment watchlist count
            await self.listings.update_one(
                {"id": listing_id},
                {"$inc": {"watchlist_count": 1}}
            )
            
            return {"success": True, "message": "Added to watchlist"}
            
        except Exception as e:
            logger.error(f"Failed to add to watchlist: {str(e)}")
            raise
    
    async def remove_from_watchlist(self, user_id: str, listing_id: str) -> Dict[str, Any]:
        """Remove listing from watchlist"""
        try:
            result = await self.watchlists.delete_one({"user_id": user_id, "listing_id": listing_id})
            
            if result.deleted_count > 0:
                await self.listings.update_one(
                    {"id": listing_id},
                    {"$inc": {"watchlist_count": -1}}
                )
            
            return {"success": True, "message": "Removed from watchlist"}
            
        except Exception as e:
            logger.error(f"Failed to remove from watchlist: {str(e)}")
            raise
    
    async def get_user_watchlist(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's watchlist with listing details"""
        try:
            watchlist = await self.watchlists.find({"user_id": user_id}, {"_id": 0}).to_list(length=None)
            
            # Enrich with listing info
            for item in watchlist:
                listing = await self.listings.find_one({"id": item["listing_id"]}, {"_id": 0})
                item["listing"] = listing
            
            return watchlist
            
        except Exception as e:
            logger.error(f"Failed to get watchlist: {str(e)}")
            raise
    
    # Smart Pricing
    async def _calculate_pricing(self, listing: RoyaltyListing) -> Dict[str, Any]:
        """Calculate smart pricing recommendation based on multiple factors"""
        try:
            # Base valuation: Multiple of annual revenue
            base_multiple = 3.0  # 3x annual revenue as base
            
            # Adjust based on royalty type
            type_multipliers = {
                RoyaltyType.FULL_OWNERSHIP: 1.0,
                RoyaltyType.PERCENTAGE_SHARE: 0.8,
                RoyaltyType.TIME_LIMITED: 0.5,
                RoyaltyType.REVENUE_CAP: 0.6
            }
            
            type_mult = type_multipliers.get(listing.royalty_type, 0.7)
            
            # Calculate recommended price
            projected = float(listing.projected_revenue) if listing.projected_revenue else float(listing.historical_revenue)
            royalty_share = float(listing.royalty_percentage) / 100
            
            recommended_price = projected * base_multiple * type_mult * royalty_share
            
            # Price ranges
            min_recommended = recommended_price * 0.8
            max_recommended = recommended_price * 1.3
            
            # Confidence based on available data
            confidence = 0.8 if listing.historical_revenue > 0 else 0.5
            
            return {
                "recommended_price": round(recommended_price, 2),
                "price_range": {
                    "min": round(min_recommended, 2),
                    "max": round(max_recommended, 2)
                },
                "valuation_multiple": base_multiple * type_mult,
                "confidence": confidence,
                "factors": {
                    "base_multiple": base_multiple,
                    "type_adjustment": type_mult,
                    "royalty_share": royalty_share
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate pricing: {str(e)}")
            return {"recommended_price": 0, "confidence": 0}
    
    async def _record_price_change(self, listing_id: str, price: Decimal, change_type: str, bid_id: Optional[str] = None):
        """Record price change in history"""
        try:
            record = PriceHistory(
                listing_id=listing_id,
                price=price,
                bid_id=bid_id,
                change_type=change_type
            )
            await self.price_history.insert_one(serialize_for_mongo(record.dict()))
        except Exception as e:
            logger.error(f"Failed to record price change: {str(e)}")
    
    # Analytics
    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace-wide statistics"""
        try:
            now = datetime.now(timezone.utc)
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            last_30d = now - timedelta(days=30)
            
            # Active listings
            active_listings = await self.listings.count_documents({"status": ListingStatus.ACTIVE.value})
            
            # Total volume (completed transactions)
            pipeline = [
                {"$match": {"status": "completed"}},
                {"$group": {"_id": None, "total": {"$sum": "$sale_price"}, "count": {"$sum": 1}}}
            ]
            volume_result = await self.transactions.aggregate(pipeline).to_list(length=1)
            total_volume = volume_result[0]["total"] if volume_result else 0
            total_sales = volume_result[0]["count"] if volume_result else 0
            
            # Recent activity
            recent_listings = await self.listings.count_documents({
                "created_at": {"$gte": last_24h}
            })
            
            recent_bids = await self.bids.count_documents({
                "created_at": {"$gte": last_24h}
            })
            
            # Average sale price
            avg_price_pipeline = [
                {"$match": {"status": "completed"}},
                {"$group": {"_id": None, "avg": {"$avg": "$sale_price"}}}
            ]
            avg_result = await self.transactions.aggregate(avg_price_pipeline).to_list(length=1)
            avg_sale_price = avg_result[0]["avg"] if avg_result else 0
            
            return {
                "active_listings": active_listings,
                "total_volume": float(total_volume),
                "total_sales": total_sales,
                "average_sale_price": float(avg_sale_price) if avg_sale_price else 0,
                "recent_activity": {
                    "new_listings_24h": recent_listings,
                    "new_bids_24h": recent_bids
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get marketplace stats: {str(e)}")
            return {}
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's marketplace statistics"""
        try:
            # Listings stats
            my_listings = await self.listings.count_documents({"seller_id": user_id})
            active_listings = await self.listings.count_documents({
                "seller_id": user_id,
                "status": ListingStatus.ACTIVE.value
            })
            sold_listings = await self.listings.count_documents({
                "seller_id": user_id,
                "status": ListingStatus.SOLD.value
            })
            
            # Sales volume
            sales_pipeline = [
                {"$match": {"seller_id": user_id, "status": "completed"}},
                {"$group": {"_id": None, "total": {"$sum": "$seller_net"}, "count": {"$sum": 1}}}
            ]
            sales_result = await self.transactions.aggregate(sales_pipeline).to_list(length=1)
            total_earned = sales_result[0]["total"] if sales_result else 0
            
            # Purchases
            purchases_pipeline = [
                {"$match": {"buyer_id": user_id, "status": "completed"}},
                {"$group": {"_id": None, "total": {"$sum": "$sale_price"}, "count": {"$sum": 1}}}
            ]
            purchases_result = await self.transactions.aggregate(purchases_pipeline).to_list(length=1)
            total_spent = purchases_result[0]["total"] if purchases_result else 0
            total_purchases = purchases_result[0]["count"] if purchases_result else 0
            
            # Active bids
            active_bids = await self.bids.count_documents({
                "bidder_id": user_id,
                "status": BidStatus.PENDING.value
            })
            
            return {
                "listings": {
                    "total": my_listings,
                    "active": active_listings,
                    "sold": sold_listings
                },
                "sales": {
                    "total_earned": float(total_earned),
                    "count": sold_listings
                },
                "purchases": {
                    "total_spent": float(total_spent),
                    "count": total_purchases
                },
                "active_bids": active_bids
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {}


# Initialize service
marketplace_service = RoyaltyMarketplaceService()
