"""
Snapchat Business Integration API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os

from providers.snapchat_provider import SnapchatProvider, SnapchatMockProvider

router = APIRouter(prefix="/snapchat", tags=["Snapchat Integration"])

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bigmann_entertainment_production')]


class SnapchatTokenRequest(BaseModel):
    """Request to store Snapchat API token"""
    api_token: str
    account_name: Optional[str] = "Snapchat Business"
    user_id: str


class SnapchatPostRequest(BaseModel):
    """Request to create Snapchat post"""
    media_url: str
    caption: str
    duration_ms: int = 10000


class SnapchatAdRequest(BaseModel):
    """Request to create Story Ad"""
    ad_account_id: str
    creative_id: str
    campaign_name: str
    daily_budget: float


@router.post("/connect")
async def connect_snapchat(request: SnapchatTokenRequest):
    """
    Connect Snapchat Business account with API token
    """
    try:
        # Use mock provider for development/testing
        # In production, use: provider = SnapchatProvider(request.api_token)
        provider = SnapchatMockProvider(request.api_token)
        
        # Verify connection
        connection_status = provider.verify_connection()
        
        if not connection_status.get("connected"):
            raise HTTPException(
                status_code=401,
                detail=f"Failed to connect: {connection_status.get('error', 'Unknown error')}"
            )
        
        # Get account info
        account_info = provider.get_account_info()
        
        # Store token and connection info
        snapchat_connection = {
            "user_id": request.user_id,
            "account_name": request.account_name,
            "api_token": request.api_token,  # In production, encrypt this
            "account_id": account_info.get("id"),
            "account_info": account_info,
            "connection_status": connection_status,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        # Update or insert
        await db.snapchat_connections.update_one(
            {"user_id": request.user_id},
            {"$set": snapchat_connection},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Snapchat Business connected successfully",
            "account_id": account_info.get("id"),
            "account_name": account_info.get("name"),
            "connection_status": connection_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


@router.get("/status/{user_id}")
async def get_snapchat_status(user_id: str):
    """
    Get Snapchat connection status
    """
    connection = await db.snapchat_connections.find_one({"user_id": user_id})
    
    if not connection:
        return {
            "connected": False,
            "message": "No Snapchat account connected"
        }
    
    # Test connection with current token
    provider = SnapchatMockProvider(connection["api_token"])
    current_status = provider.verify_connection()
    
    # Update status in database
    await db.snapchat_connections.update_one(
        {"user_id": user_id},
        {"$set": {
            "connection_status": current_status,
            "last_checked": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "connected": current_status.get("connected", False),
        "status": current_status.get("status"),
        "account_info": connection.get("account_info"),
        "connected_at": connection.get("connected_at"),
        "last_checked": datetime.now(timezone.utc).isoformat()
    }


@router.get("/accounts/{user_id}")
async def get_ad_accounts(user_id: str):
    """
    Get Snapchat Ad Accounts
    """
    connection = await db.snapchat_connections.find_one({"user_id": user_id})
    
    if not connection:
        raise HTTPException(status_code=404, detail="Snapchat not connected")
    
    provider = SnapchatMockProvider(connection["api_token"])
    ad_accounts = provider.get_ad_accounts()
    
    return {
        "success": True,
        "ad_accounts": ad_accounts,
        "count": len(ad_accounts)
    }


@router.get("/insights/{user_id}/{ad_account_id}")
async def get_insights(user_id: str, ad_account_id: str, date_range: str = "LAST_7_DAYS"):
    """
    Get Snapchat performance insights
    """
    connection = await db.snapchat_connections.find_one({"user_id": user_id})
    
    if not connection:
        raise HTTPException(status_code=404, detail="Snapchat not connected")
    
    provider = SnapchatMockProvider(connection["api_token"])
    insights = provider.get_insights(ad_account_id, date_range)
    
    if "error" in insights:
        raise HTTPException(status_code=500, detail=insights["error"])
    
    return {
        "success": True,
        "insights": insights,
        "ad_account_id": ad_account_id,
        "date_range": date_range
    }


@router.post("/post")
async def create_snapchat_post(request: SnapchatPostRequest, user_id: str):
    """
    Create a Snapchat Story post
    """
    connection = await db.snapchat_connections.find_one({"user_id": user_id})
    
    if not connection:
        raise HTTPException(status_code=404, detail="Snapchat not connected")
    
    provider = SnapchatMockProvider(connection["api_token"])
    
    result = provider.create_snap(
        media_url=request.media_url,
        caption=request.caption,
        duration_ms=request.duration_ms
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to create snap")
        )
    
    # Log post
    post_record = {
        "user_id": user_id,
        "platform": "snapchat",
        "media_url": request.media_url,
        "caption": request.caption,
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "published"
    }
    
    await db.social_posts.insert_one(post_record)
    
    return {
        "success": True,
        "message": "Snap created successfully",
        "data": result.get("data")
    }


@router.post("/create-ad")
async def create_story_ad(request: SnapchatAdRequest, user_id: str):
    """
    Create a Snapchat Story Ad campaign
    """
    connection = await db.snapchat_connections.find_one({"user_id": user_id})
    
    if not connection:
        raise HTTPException(status_code=404, detail="Snapchat not connected")
    
    provider = SnapchatMockProvider(connection["api_token"])
    
    result = provider.create_story_ad(
        ad_account_id=request.ad_account_id,
        creative_id=request.creative_id,
        name=request.campaign_name,
        daily_budget=request.daily_budget
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to create ad")
        )
    
    # Log campaign
    campaign_record = {
        "user_id": user_id,
        "platform": "snapchat",
        "ad_account_id": request.ad_account_id,
        "campaign_name": request.campaign_name,
        "daily_budget": request.daily_budget,
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }
    
    await db.snapchat_campaigns.insert_one(campaign_record)
    
    return {
        "success": True,
        "message": "Story Ad campaign created successfully",
        "campaign": result.get("campaign")
    }


@router.get("/campaigns/{user_id}")
async def get_campaigns(user_id: str):
    """
    Get all Snapchat campaigns for user
    """
    campaigns = await db.snapchat_campaigns.find(
        {"user_id": user_id}
    ).sort("created_at", -1).to_list(length=100)
    
    return {
        "success": True,
        "campaigns": campaigns,
        "count": len(campaigns)
    }


@router.delete("/disconnect/{user_id}")
async def disconnect_snapchat(user_id: str):
    """
    Disconnect Snapchat account
    """
    result = await db.snapchat_connections.delete_one({"user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No Snapchat connection found")
    
    return {
        "success": True,
        "message": "Snapchat account disconnected"
    }


@router.get("/analytics/{user_id}")
async def get_analytics_summary(user_id: str):
    """
    Get comprehensive Snapchat analytics
    """
    connection = await db.snapchat_connections.find_one({"user_id": user_id})
    
    if not connection:
        raise HTTPException(status_code=404, detail="Snapchat not connected")
    
    # Get posts count
    posts_count = await db.social_posts.count_documents({
        "user_id": user_id,
        "platform": "snapchat"
    })
    
    # Get campaigns count
    campaigns_count = await db.snapchat_campaigns.count_documents({
        "user_id": user_id
    })
    
    # Get insights for first ad account
    provider = SnapchatMockProvider(connection["api_token"])
    ad_accounts = provider.get_ad_accounts()
    
    insights = {}
    if ad_accounts:
        first_account = ad_accounts[0]["id"]
        insights = provider.get_insights(first_account)
    
    return {
        "success": True,
        "summary": {
            "connected": True,
            "account_name": connection.get("account_name"),
            "posts_count": posts_count,
            "campaigns_count": campaigns_count,
            "insights": insights,
            "ad_accounts_count": len(ad_accounts)
        }
    }


@router.get("/health")
async def snapchat_health():
    """
    Snapchat integration health check
    """
    return {
        "status": "healthy",
        "service": "snapchat_integration",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": {
            "account_connection": "enabled",
            "story_posting": "enabled",
            "ad_campaigns": "enabled",
            "analytics": "enabled",
            "insights": "enabled"
        }
    }
