"""
Social Media Royalty Integration Endpoints
API endpoints for connecting Social Media Phases 5-10 with Real-Time Royalty Engine
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import logging
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field

from social_media_royalty_integration import (
    social_media_processor,
    streaming_integration
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/social-media-royalty", tags=["Social Media Royalty Integration"])
security = HTTPBearer()

# Request Models
class SocialMediaMonetizationEvent(BaseModel):
    platform: str
    content_id: str
    monetization_type: str
    gross_amount: float
    user_id: str
    territory: str = "US"
    metadata: Optional[Dict[str, Any]] = {}

class AssetMappingRequest(BaseModel):
    platform: str
    content_id: str
    asset_id: str
    user_id: str

class StreamingRoyaltyRequest(BaseModel):
    platform: str
    asset_id: str
    stream_count: int
    territory: str = "US"
    metadata: Optional[Dict[str, Any]] = {}

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return "user_123"

# Social Media Monetization Processing Endpoints

@router.post("/process-monetization", response_model=Dict[str, Any])
async def process_social_media_monetization(
    event: SocialMediaMonetizationEvent,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Process a social media monetization event and calculate royalties"""
    try:
        calculation_id = await social_media_processor.process_social_media_monetization(
            platform=event.platform,
            content_id=event.content_id,
            monetization_type=event.monetization_type,
            gross_amount=Decimal(str(event.gross_amount)),
            user_id=event.user_id,
            territory=event.territory,
            metadata=event.metadata
        )
        
        if calculation_id:
            return {
                "success": True,
                "message": "Social media monetization processed successfully",
                "calculation_id": calculation_id,
                "platform": event.platform,
                "gross_amount": event.gross_amount
            }
        else:
            return {
                "success": False,
                "message": "No associated music asset found for this content",
                "platform": event.platform,
                "content_id": event.content_id
            }
            
    except Exception as e:
        logger.error(f"Failed to process social media monetization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process monetization: {str(e)}")

@router.post("/batch-process-monetization", response_model=Dict[str, Any])
async def batch_process_social_media_events(
    events: List[SocialMediaMonetizationEvent],
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Process multiple social media monetization events in batch"""
    try:
        # Convert to dict format for processing
        event_dicts = []
        for event in events:
            event_dicts.append({
                "id": str(uuid.uuid4()),
                "platform": event.platform,
                "content_id": event.content_id,
                "monetization_type": event.monetization_type,
                "gross_amount": event.gross_amount,
                "user_id": event.user_id,
                "territory": event.territory,
                "metadata": event.metadata
            })
        
        result = await social_media_processor.batch_process_social_media_events(event_dicts)
        
        return {
            "success": True,
            "message": f"Processed {result['total_events']} social media events",
            "summary": result
        }
        
    except Exception as e:
        logger.error(f"Failed to batch process social media events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to batch process events")

# Asset Mapping Management Endpoints

@router.post("/asset-mapping", response_model=Dict[str, str])
async def create_asset_mapping(
    mapping: AssetMappingRequest,
    user_id: str = Depends(get_current_user)
):
    """Create mapping between social media content and music asset"""
    try:
        success = await social_media_processor.create_asset_mapping(
            platform=mapping.platform,
            content_id=mapping.content_id,
            asset_id=mapping.asset_id,
            user_id=mapping.user_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Asset mapping created successfully",
                "mapping": f"{mapping.platform}:{mapping.content_id} -> {mapping.asset_id}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create asset mapping")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create asset mapping: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create asset mapping")

@router.get("/asset-mappings/{platform}/{content_id}", response_model=Dict[str, Any])
async def get_asset_mapping(
    platform: str,
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get asset mapping for social media content"""
    try:
        mapping = await social_media_processor.royalty_engine.db.social_media_mappings.find_one({
            "platform": platform,
            "content_id": content_id,
            "active": True
        })
        
        if mapping:
            return {
                "success": True,
                "mapping": mapping
            }
        else:
            raise HTTPException(status_code=404, detail="Asset mapping not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get asset mapping: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get asset mapping")

@router.get("/asset-mappings/user/{user_id}", response_model=Dict[str, Any])
async def get_user_asset_mappings(
    user_id: str,
    platform: Optional[str] = None,
    limit: int = Query(100, le=1000),
    current_user: str = Depends(get_current_user)
):
    """Get all asset mappings for a user"""
    try:
        query = {"user_id": user_id, "active": True}
        if platform:
            query["platform"] = platform
        
        mappings = await social_media_processor.royalty_engine.db.social_media_mappings.find(
            query
        ).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "user_id": user_id,
            "mappings": mappings,
            "count": len(mappings)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user asset mappings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user asset mappings")

# Streaming Platform Integration Endpoints

@router.post("/streaming-royalties", response_model=Dict[str, Any])
async def process_streaming_royalties(
    request: StreamingRoyaltyRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Process streaming platform royalties"""
    try:
        calculation_id = await streaming_integration.process_streaming_royalties(
            platform=request.platform,
            asset_id=request.asset_id,
            stream_count=request.stream_count,
            territory=request.territory,
            metadata=request.metadata
        )
        
        if calculation_id:
            return {
                "success": True,
                "message": "Streaming royalties processed successfully",
                "calculation_id": calculation_id,
                "platform": request.platform,
                "stream_count": request.stream_count
            }
        else:
            return {
                "success": False,
                "message": "Stream count below minimum payout threshold",
                "platform": request.platform,
                "stream_count": request.stream_count
            }
            
    except Exception as e:
        logger.error(f"Failed to process streaming royalties: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process streaming royalties: {str(e)}")

# Analytics and Reporting Endpoints

@router.get("/analytics/{asset_id}/social-media", response_model=Dict[str, Any])
async def get_social_media_analytics(
    asset_id: str,
    days: int = Query(30, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get social media royalty analytics for an asset"""
    try:
        analytics = await social_media_processor.get_social_media_analytics(asset_id, days)
        
        if "error" in analytics:
            raise HTTPException(status_code=500, detail=analytics["error"])
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get social media analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get social media analytics")

@router.get("/analytics/platform-summary", response_model=Dict[str, Any])
async def get_platform_revenue_summary(
    days: int = Query(30, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get revenue summary across all social media platforms"""
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Aggregate data across all social media transactions
        pipeline = [
            {
                "$match": {
                    "revenue_source": "social_media",
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "platform": "$platform",
                        "monetization_type": "$monetization_type"
                    },
                    "total_revenue": {"$sum": "$gross_revenue"},
                    "event_count": {"$sum": 1},
                    "avg_revenue": {"$avg": "$gross_revenue"}
                }
            },
            {
                "$sort": {"total_revenue": -1}
            }
        ]
        
        aggregation_result = await social_media_processor.royalty_engine.collection_events.aggregate(
            pipeline
        ).to_list(length=None)
        
        # Format results
        platform_summary = {}
        total_revenue = 0
        total_events = 0
        
        for result in aggregation_result:
            platform = result["_id"]["platform"]
            monetization_type = result["_id"]["monetization_type"]
            revenue = float(result["total_revenue"])
            events = result["event_count"]
            
            if platform not in platform_summary:
                platform_summary[platform] = {
                    "total_revenue": 0,
                    "total_events": 0,
                    "monetization_types": {}
                }
            
            platform_summary[platform]["total_revenue"] += revenue
            platform_summary[platform]["total_events"] += events
            platform_summary[platform]["monetization_types"][monetization_type] = {
                "revenue": revenue,
                "events": events,
                "avg_revenue": float(result["avg_revenue"])
            }
            
            total_revenue += revenue
            total_events += events
        
        return {
            "success": True,
            "period_days": days,
            "summary": {
                "total_revenue": total_revenue,
                "total_events": total_events,
                "platform_count": len(platform_summary),
                "avg_revenue_per_event": total_revenue / total_events if total_events > 0 else 0
            },
            "platform_breakdown": platform_summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get platform summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get platform summary")

# Webhook Endpoints for Platform Integration

@router.post("/webhooks/youtube/monetization", response_model=Dict[str, str])
async def youtube_monetization_webhook(
    webhook_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Webhook endpoint for YouTube monetization events"""
    try:
        # Verify webhook signature (in production)
        # verify_youtube_webhook_signature(webhook_data)
        
        # Extract monetization data
        video_id = webhook_data.get("video_id")
        ad_revenue = webhook_data.get("ad_revenue", 0)
        premium_revenue = webhook_data.get("premium_revenue", 0)
        channel_id = webhook_data.get("channel_id")
        
        if not video_id or not channel_id:
            raise HTTPException(status_code=400, detail="Missing required webhook data")
        
        # Process ad revenue
        if ad_revenue > 0:
            await social_media_processor.process_social_media_monetization(
                platform="youtube",
                content_id=video_id,
                monetization_type="ad_revenue",
                gross_amount=Decimal(str(ad_revenue)),
                user_id=channel_id,
                territory="US",
                metadata={"webhook_source": "youtube_partner_program"}
            )
        
        # Process premium revenue
        if premium_revenue > 0:
            await social_media_processor.process_social_media_monetization(
                platform="youtube",
                content_id=video_id,
                monetization_type="premium_revenue",
                gross_amount=Decimal(str(premium_revenue)),
                user_id=channel_id,
                territory="US",
                metadata={"webhook_source": "youtube_premium"}
            )
        
        return {
            "success": True,
            "message": "YouTube monetization webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"YouTube webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/webhooks/tiktok/creator-fund", response_model=Dict[str, str])
async def tiktok_creator_fund_webhook(
    webhook_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Webhook endpoint for TikTok Creator Fund payments"""
    try:
        video_id = webhook_data.get("video_id")
        fund_payment = webhook_data.get("fund_payment", 0)
        user_id = webhook_data.get("user_id")
        
        if not video_id or not user_id or fund_payment <= 0:
            raise HTTPException(status_code=400, detail="Invalid webhook data")
        
        await social_media_processor.process_social_media_monetization(
            platform="tiktok",
            content_id=video_id,
            monetization_type="creator_fund",
            gross_amount=Decimal(str(fund_payment)),
            user_id=user_id,
            territory="US",
            metadata={"webhook_source": "tiktok_creator_fund"}
        )
        
        return {
            "success": True,
            "message": "TikTok Creator Fund webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"TikTok webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/webhooks/spotify/streams", response_model=Dict[str, str])
async def spotify_streams_webhook(
    webhook_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Webhook endpoint for Spotify streaming data"""
    try:
        track_id = webhook_data.get("track_id")
        stream_count = webhook_data.get("stream_count", 0)
        territory = webhook_data.get("territory", "US")
        
        if not track_id or stream_count <= 0:
            raise HTTPException(status_code=400, detail="Invalid streaming data")
        
        await streaming_integration.process_streaming_royalties(
            platform="spotify",
            asset_id=track_id,
            stream_count=stream_count,
            territory=territory,
            metadata={"webhook_source": "spotify_for_artists"}
        )
        
        return {
            "success": True,
            "message": "Spotify streaming webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Spotify webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

# Integration Status and Health Endpoints

@router.get("/integration-status", response_model=Dict[str, Any])
async def get_integration_status(
    user_id: str = Depends(get_current_user)
):
    """Get status of social media royalty integrations"""
    try:
        # Get counts of various integration elements
        status = {
            "asset_mappings": {
                "total": await social_media_processor.royalty_engine.db.social_media_mappings.count_documents({"active": True}),
                "by_platform": {}
            },
            "processed_events": {
                "last_24h": await social_media_processor.royalty_engine.collection_events.count_documents({
                    "revenue_source": "social_media",
                    "timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(hours=24)}
                }),
                "last_7d": await social_media_processor.royalty_engine.collection_events.count_documents({
                    "revenue_source": "social_media",
                    "timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(days=7)}
                })
            },
            "platform_integrations": {
                "youtube": "webhook_available",
                "tiktok": "webhook_available", 
                "spotify": "webhook_available",
                "instagram": "manual_processing",
                "facebook": "manual_processing",
                "twitter": "manual_processing"
            }
        }
        
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get integration status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get integration status")

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check for social media royalty integration"""
    return {
        "success": True,
        "status": "healthy",
        "message": "Social Media Royalty Integration is operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "social_media_processor": "healthy",
            "streaming_integration": "healthy",
            "asset_mapping": "healthy",
            "webhook_processing": "healthy"
        }
    }