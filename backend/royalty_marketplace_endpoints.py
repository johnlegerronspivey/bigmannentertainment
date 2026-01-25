"""
Dynamic Royalty Marketplace API Endpoints
Enterprise-grade marketplace for royalty trading, auctions, and smart contract pricing
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from decimal import Decimal
import logging

from royalty_marketplace_service import (
    marketplace_service,
    RoyaltyListing,
    Bid,
    ListingType,
    ListingStatus,
    RoyaltyType,
    PaymentCurrency,
    BidStatus
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/marketplace", tags=["Royalty Marketplace"])
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user ID from auth token - integrates with main auth system"""
    # In production, decode JWT token to get user_id
    # For now, return a placeholder
    return "user_123"


# ==================== LISTING ENDPOINTS ====================

@router.post("/listings", response_model=Dict[str, Any])
async def create_listing(
    listing: RoyaltyListing,
    user_id: str = Depends(get_current_user)
):
    """Create a new royalty listing"""
    try:
        listing.seller_id = user_id
        result = await marketplace_service.create_listing(listing)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create listing")


@router.get("/listings", response_model=Dict[str, Any])
async def search_listings(
    query: Optional[str] = None,
    listing_type: Optional[str] = None,
    royalty_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    genre: Optional[str] = None,
    featured_only: bool = False,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Search and filter marketplace listings"""
    try:
        lt = ListingType(listing_type) if listing_type else None
        rt = RoyaltyType(royalty_type) if royalty_type else None
        
        result = await marketplace_service.search_listings(
            query=query,
            listing_type=lt,
            royalty_type=rt,
            min_price=Decimal(str(min_price)) if min_price else None,
            max_price=Decimal(str(max_price)) if max_price else None,
            genre=genre,
            featured_only=featured_only,
            sort_by=sort_by,
            sort_order=-1 if sort_order == "desc" else 1,
            page=page,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Failed to search listings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search listings")


@router.get("/listings/featured", response_model=Dict[str, Any])
async def get_featured_listings(
    limit: int = Query(10, ge=1, le=50)
):
    """Get featured marketplace listings"""
    try:
        result = await marketplace_service.search_listings(
            featured_only=True,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get featured listings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get featured listings")


@router.get("/listings/ending-soon", response_model=Dict[str, Any])
async def get_listings_ending_soon(
    hours: int = Query(24, ge=1, le=168)
):
    """Get auction listings ending soon"""
    try:
        # Get active auction listings
        result = await marketplace_service.search_listings(
            listing_type=ListingType.AUCTION,
            sort_by="auction_end",
            sort_order=1,
            limit=20
        )
        
        # Filter for auctions ending within specified hours
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) + timedelta(hours=hours)
        
        filtered = []
        for listing in result.get("listings", []):
            if listing.get("auction_end"):
                auction_end = listing["auction_end"]
                if isinstance(auction_end, str):
                    auction_end = datetime.fromisoformat(auction_end.replace('Z', '+00:00'))
                # Handle naive datetime by assuming UTC
                if auction_end.tzinfo is None:
                    auction_end = auction_end.replace(tzinfo=timezone.utc)
                if auction_end <= cutoff:
                    filtered.append(listing)
        
        return {
            "success": True,
            "listings": filtered,
            "count": len(filtered)
        }
    except Exception as e:
        logger.error(f"Failed to get ending soon listings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get listings")


@router.get("/listings/{listing_id}", response_model=Dict[str, Any])
async def get_listing(listing_id: str):
    """Get listing details"""
    try:
        result = await marketplace_service.get_listing(listing_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get listing")


@router.put("/listings/{listing_id}", response_model=Dict[str, Any])
async def update_listing(
    listing_id: str,
    updates: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Update a listing"""
    try:
        result = await marketplace_service.update_listing(listing_id, updates, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update listing")


@router.post("/listings/{listing_id}/publish", response_model=Dict[str, Any])
async def publish_listing(
    listing_id: str,
    user_id: str = Depends(get_current_user)
):
    """Publish a draft listing"""
    try:
        result = await marketplace_service.publish_listing(listing_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to publish listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish listing")


@router.delete("/listings/{listing_id}", response_model=Dict[str, Any])
async def cancel_listing(
    listing_id: str,
    user_id: str = Depends(get_current_user)
):
    """Cancel a listing"""
    try:
        result = await marketplace_service.update_listing(
            listing_id,
            {"status": ListingStatus.CANCELLED.value},
            user_id
        )
        return {"success": True, "message": "Listing cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel listing")


@router.get("/my-listings", response_model=Dict[str, Any])
async def get_my_listings(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user)
):
    """Get current user's listings"""
    try:
        query = {"seller_id": user_id}
        if status:
            query["status"] = status
        
        listings = await marketplace_service.listings.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip((page - 1) * limit).limit(limit).to_list(length=None)
        
        total = await marketplace_service.listings.count_documents(query)
        
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
        logger.error(f"Failed to get user listings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get listings")


# ==================== BIDDING ENDPOINTS ====================

@router.post("/listings/{listing_id}/bids", response_model=Dict[str, Any])
async def place_bid(
    listing_id: str,
    amount: float,
    max_amount: Optional[float] = None,
    message: Optional[str] = None,
    payment_currency: str = "usd",
    user_id: str = Depends(get_current_user)
):
    """Place a bid on an auction listing"""
    try:
        bid = Bid(
            listing_id=listing_id,
            bidder_id=user_id,
            amount=Decimal(str(amount)),
            max_amount=Decimal(str(max_amount)) if max_amount else None,
            message=message,
            payment_currency=PaymentCurrency(payment_currency)
        )
        
        result = await marketplace_service.place_bid(bid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to place bid: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to place bid")


@router.get("/listings/{listing_id}/bids", response_model=Dict[str, Any])
async def get_listing_bids(
    listing_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Get bids for a listing"""
    try:
        bids = await marketplace_service.bids.find(
            {"listing_id": listing_id},
            {"_id": 0}
        ).sort("amount", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "bids": bids,
            "count": len(bids)
        }
    except Exception as e:
        logger.error(f"Failed to get bids: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get bids")


@router.post("/listings/{listing_id}/bids/{bid_id}/accept", response_model=Dict[str, Any])
async def accept_bid(
    listing_id: str,
    bid_id: str,
    user_id: str = Depends(get_current_user)
):
    """Accept a bid (seller only)"""
    try:
        result = await marketplace_service.accept_bid(listing_id, bid_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to accept bid: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to accept bid")


@router.get("/my-bids", response_model=Dict[str, Any])
async def get_my_bids(
    status: Optional[str] = None,
    user_id: str = Depends(get_current_user)
):
    """Get current user's bids"""
    try:
        bid_status = BidStatus(status) if status else None
        bids = await marketplace_service.get_user_bids(user_id, bid_status)
        
        return {
            "success": True,
            "bids": bids,
            "count": len(bids)
        }
    except Exception as e:
        logger.error(f"Failed to get user bids: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get bids")


# ==================== PURCHASE ENDPOINTS ====================

@router.post("/listings/{listing_id}/buy-now", response_model=Dict[str, Any])
async def buy_now(
    listing_id: str,
    payment_currency: str = "usd",
    user_id: str = Depends(get_current_user)
):
    """Instant purchase at buy now price"""
    try:
        result = await marketplace_service.buy_now(
            listing_id,
            user_id,
            PaymentCurrency(payment_currency)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute buy now: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete purchase")


@router.post("/transactions/{transaction_id}/complete", response_model=Dict[str, Any])
async def complete_transaction(
    transaction_id: str,
    payment_proof: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Complete a transaction with payment proof"""
    try:
        result = await marketplace_service.complete_transaction(transaction_id, payment_proof)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to complete transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete transaction")


@router.get("/transactions/{transaction_id}", response_model=Dict[str, Any])
async def get_transaction(
    transaction_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get transaction details"""
    try:
        transaction = await marketplace_service.transactions.find_one(
            {"id": transaction_id},
            {"_id": 0}
        )
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Verify user is buyer or seller
        if transaction["buyer_id"] != user_id and transaction["seller_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return {
            "success": True,
            "transaction": transaction
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get transaction")


@router.get("/my-transactions", response_model=Dict[str, Any])
async def get_my_transactions(
    role: str = Query("all", regex="^(all|buyer|seller)$"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user)
):
    """Get user's transactions"""
    try:
        query = {}
        
        if role == "buyer":
            query["buyer_id"] = user_id
        elif role == "seller":
            query["seller_id"] = user_id
        else:
            query["$or"] = [{"buyer_id": user_id}, {"seller_id": user_id}]
        
        if status:
            query["status"] = status
        
        transactions = await marketplace_service.transactions.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip((page - 1) * limit).limit(limit).to_list(length=None)
        
        total = await marketplace_service.transactions.count_documents(query)
        
        return {
            "success": True,
            "transactions": transactions,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        logger.error(f"Failed to get transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get transactions")


# ==================== WATCHLIST ENDPOINTS ====================

@router.post("/watchlist/{listing_id}", response_model=Dict[str, Any])
async def add_to_watchlist(
    listing_id: str,
    price_alert: Optional[float] = None,
    user_id: str = Depends(get_current_user)
):
    """Add listing to watchlist"""
    try:
        result = await marketplace_service.add_to_watchlist(
            user_id,
            listing_id,
            Decimal(str(price_alert)) if price_alert else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to add to watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update watchlist")


@router.delete("/watchlist/{listing_id}", response_model=Dict[str, Any])
async def remove_from_watchlist(
    listing_id: str,
    user_id: str = Depends(get_current_user)
):
    """Remove listing from watchlist"""
    try:
        result = await marketplace_service.remove_from_watchlist(user_id, listing_id)
        return result
    except Exception as e:
        logger.error(f"Failed to remove from watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update watchlist")


@router.get("/watchlist", response_model=Dict[str, Any])
async def get_watchlist(user_id: str = Depends(get_current_user)):
    """Get user's watchlist"""
    try:
        watchlist = await marketplace_service.get_user_watchlist(user_id)
        return {
            "success": True,
            "watchlist": watchlist,
            "count": len(watchlist)
        }
    except Exception as e:
        logger.error(f"Failed to get watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get watchlist")


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/stats", response_model=Dict[str, Any])
async def get_marketplace_stats():
    """Get marketplace-wide statistics"""
    try:
        stats = await marketplace_service.get_marketplace_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get marketplace stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/my-stats", response_model=Dict[str, Any])
async def get_my_stats(user_id: str = Depends(get_current_user)):
    """Get user's marketplace statistics"""
    try:
        stats = await marketplace_service.get_user_stats(user_id)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/price-history/{listing_id}", response_model=Dict[str, Any])
async def get_price_history(
    listing_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Get price history for a listing"""
    try:
        history = await marketplace_service.price_history.find(
            {"listing_id": listing_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "price_history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Failed to get price history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get price history")


# ==================== HEALTH CHECK ====================

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Marketplace health check"""
    try:
        # Check database connectivity
        await marketplace_service.listings.find_one()
        
        return {
            "success": True,
            "status": "healthy",
            "service": "Dynamic Royalty Marketplace",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Marketplace service unhealthy")
