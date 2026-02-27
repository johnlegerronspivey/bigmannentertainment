"""Distribution endpoints - platform management, content distribution."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Form
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from auth.service import get_current_user
from models.core import User, DistributionRequest

router = APIRouter(tags=["Distribution"])

@router.get("/distribution/platforms")
async def get_distribution_platforms():
    """Get all available distribution platforms organized by category"""
    try:
        # Return platforms organized in a structure the frontend expects
        return {
            "platforms": DISTRIBUTION_PLATFORMS,
            "total_count": len(DISTRIBUTION_PLATFORMS),
            "categories": _organize_platforms_by_category()
        }
    except Exception as e:
        logging.error(f"Error getting distribution platforms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get distribution platforms: {str(e)}")

def _organize_platforms_by_category():
    """Helper function to organize platforms by category"""
    categories = {}
    for platform_id, config in DISTRIBUTION_PLATFORMS.items():
        category = config.get("type", "other")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": platform_id,
            "name": config["name"],
            "description": config.get("description", ""),
            "supported_formats": config.get("supported_formats", []),
            "max_file_size": config.get("max_file_size", 0)
        })
    return categories

@router.post("/distribution/distribute")
async def distribute_content(
    request: DistributionRequest,
    current_user: User = Depends(get_current_user)
):
    # Verify user owns the media
    media = await db.media_content.find_one({"id": request.media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if media["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to distribute this media")
    
    # Start distribution process
    distribution = await distribution_service.distribute_content(
        media_id=request.media_id,
        platforms=request.platforms,
        user_id=current_user.id,
        custom_message=request.custom_message,
        hashtags=request.hashtags
    )
    
    return {
        "distribution_id": distribution.id,
        "media_id": request.media_id,
        "platforms": request.platforms,
        "status": distribution.status,
        "results": distribution.results,
        "message": "Distribution initiated successfully"
    }

@router.get("/distribution/history")
async def get_distribution_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    # Get media IDs owned by user
    user_media = []
    async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
        user_media.append(media["id"])
    
    if not user_media:
        return {"distributions": [], "total_count": 0}
    
    # Get distributions for user's media
    query = {"media_id": {"$in": user_media}}
    cursor = db.content_distributions.find(query).skip(skip).limit(limit).sort("created_at", -1)
    
    distributions = []
    async for dist in cursor:
        distributions.append(ContentDistribution(**dist))
    
    total_count = await db.content_distributions.count_documents(query)
    
    return {
        "distributions": distributions,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

# MISSING DISTRIBUTION ENDPOINTS - IMPLEMENTING FOR 100% FUNCTIONALITY

@router.get("/distribution/status")
async def get_distribution_status(current_user: User = Depends(get_current_user)):
    """Get overall distribution status and statistics"""
    try:
        # Get user's media
        user_media = []
        async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
            user_media.append(media["id"])
        
        if not user_media:
            return {
                "status": {
                    "total_media": 0,
                    "distributed_media": 0,
                    "active_distributions": 0,
                    "pending_distributions": 0,
                    "failed_distributions": 0,
                    "success_rate": 0
                },
                "platform_status": {},
                "recent_activity": []
            }
        
        # Get distributions for user's media
        all_distributions = []
        async for dist in db.content_distributions.find({"media_id": {"$in": user_media}}):
            all_distributions.append(dist)
        
        # Calculate statistics
        total_distributions = len(all_distributions)
        active_distributions = len([d for d in all_distributions if d.get("status") == "processing"])
        completed_distributions = len([d for d in all_distributions if d.get("status") == "completed"])
        failed_distributions = len([d for d in all_distributions if d.get("status") in ["failed", "partial"]])
        
        success_rate = (completed_distributions / max(total_distributions, 1)) * 100
        
        # Platform status breakdown
        platform_status = {}
        for platform_id in DISTRIBUTION_PLATFORMS.keys():
            platform_distributions = [d for d in all_distributions if platform_id in d.get("target_platforms", [])]
            platform_status[platform_id] = {
                "name": DISTRIBUTION_PLATFORMS[platform_id]["name"],
                "total_distributions": len(platform_distributions),
                "successful": len([d for d in platform_distributions if d.get("status") == "completed"]),
                "failed": len([d for d in platform_distributions if d.get("status") in ["failed", "partial"]]),
                "last_distribution": max([d.get("created_at", datetime.min) for d in platform_distributions]) if platform_distributions else None
            }
        
        return {
            "status": {
                "total_media": len(user_media),
                "total_distributions": total_distributions,
                "active_distributions": active_distributions,
                "completed_distributions": completed_distributions,
                "failed_distributions": failed_distributions,
                "success_rate": round(success_rate, 1)
            },
            "platform_status": platform_status,
            "recent_activity": all_distributions[-5:] if all_distributions else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get distribution status: {str(e)}")

@router.get("/distribution/analytics")
async def get_distribution_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get distribution analytics and performance metrics"""
    try:
        # Get user's media
        user_media = []
        async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
            user_media.append(media["id"])
        
        if not user_media:
            return {
                "analytics": {
                    "overview": {"total_distributions": 0},
                    "platform_performance": {},
                    "trends": [],
                    "top_content": []
                }
            }
        
        # Get distributions for the specified period
        start_date = datetime.utcnow() - timedelta(days=days)
        distributions = []
        async for dist in db.content_distributions.find({
            "media_id": {"$in": user_media},
            "created_at": {"$gte": start_date}
        }):
            distributions.append(dist)
        
        # Calculate performance by platform
        platform_performance = {}
        for platform_id, platform_info in DISTRIBUTION_PLATFORMS.items():
            platform_dists = [d for d in distributions if platform_id in d.get("target_platforms", [])]
            
            if platform_dists:
                successful = len([d for d in platform_dists if d.get("status") == "completed"])
                platform_performance[platform_id] = {
                    "name": platform_info["name"],
                    "type": platform_info["type"],
                    "total_distributions": len(platform_dists),
                    "successful_distributions": successful,
                    "success_rate": (successful / len(platform_dists)) * 100 if platform_dists else 0,
                    "avg_processing_time": "2.5 hours",  # Would calculate from actual data
                    "revenue_generated": 0  # Would integrate with payment data
                }
        
        # Generate trend data (simplified)
        trends = []
        for i in range(min(days, 7)):  # Last 7 days or requested days
            date = (datetime.utcnow() - timedelta(days=i)).date()
            day_distributions = [d for d in distributions if d.get("created_at", datetime.min).date() == date]
            trends.append({
                "date": date.isoformat(),
                "distributions": len(day_distributions),
                "successful": len([d for d in day_distributions if d.get("status") == "completed"])
            })
        
        return {
            "analytics": {
                "overview": {
                    "total_distributions": len(distributions),
                    "period_days": days,
                    "avg_distributions_per_day": len(distributions) / max(days, 1),
                    "overall_success_rate": (len([d for d in distributions if d.get("status") == "completed"]) / max(len(distributions), 1)) * 100
                },
                "platform_performance": platform_performance,
                "trends": trends[::-1],  # Reverse to show oldest first
                "top_performing_platforms": sorted(
                    platform_performance.items(), 
                    key=lambda x: x[1]["success_rate"], 
                    reverse=True
                )[:5]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get distribution analytics: {str(e)}")

@router.get("/distribution/platforms/{platform_id}")
async def get_platform_details(platform_id: str, current_user: User = Depends(get_current_user)):
    """Get detailed information about a specific distribution platform"""
    if platform_id not in DISTRIBUTION_PLATFORMS:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    platform_config = DISTRIBUTION_PLATFORMS[platform_id]
    
    # Get user's distributions for this platform
    user_media = []
    async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
        user_media.append(media["id"])
    
    platform_distributions = []
    if user_media:
        async for dist in db.content_distributions.find({
            "media_id": {"$in": user_media},
            "target_platforms": platform_id
        }):
            platform_distributions.append(dist)
    
    # Calculate platform-specific statistics
    total_distributions = len(platform_distributions)
    successful = len([d for d in platform_distributions if d.get("status") == "completed"])
    success_rate = (successful / max(total_distributions, 1)) * 100
    
    return {
        "platform": {
            "id": platform_id,
            "name": platform_config["name"],
            "type": platform_config["type"],
            "description": platform_config.get("description", ""),
            "supported_formats": platform_config["supported_formats"],
            "max_file_size": platform_config["max_file_size"],
            "credentials_required": platform_config["credentials_required"],
            "api_endpoint": platform_config.get("api_endpoint"),
            "target_demographics": platform_config.get("target_demographics"),
            "content_guidelines": platform_config.get("content_guidelines"),
            "revenue_sharing": platform_config.get("revenue_sharing"),
            "platform_features": platform_config.get("platform_features", [])
        },
        "user_statistics": {
            "total_distributions": total_distributions,
            "successful_distributions": successful,
            "success_rate": round(success_rate, 1),
            "last_distribution": max([d.get("created_at", datetime.min) for d in platform_distributions]) if platform_distributions else None,
            "recent_distributions": platform_distributions[-5:] if platform_distributions else []
        }
    }

@router.post("/distribution/schedule")
async def schedule_distribution(
    media_id: str = Form(...),
    platforms: str = Form(...),  # JSON string
    scheduled_time: str = Form(...),
    custom_message: Optional[str] = Form(None),
    hashtags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Schedule content distribution for future execution"""
    try:
        # Parse platforms JSON
        try:
            platforms_list = json.loads(platforms)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid platforms format")
        
        # Parse scheduled time
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format")
        
        # Verify user owns the media
        media = await db.media_content.find_one({"id": media_id})
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        if media["owner_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to distribute this media")
        
        # Parse hashtags
        hashtag_list = []
        if hashtags:
            hashtag_list = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
        
        # Create scheduled distribution
        scheduled_distribution = ContentDistribution(
            media_id=media_id,
            target_platforms=platforms_list,
            status="scheduled",
            scheduled_time=scheduled_datetime,
            results={"scheduled_for": scheduled_datetime.isoformat()},
        )
        
        # Store in database
        await db.content_distributions.insert_one(scheduled_distribution.dict())
        
        # Log activity
        await log_activity(
            current_user.id,
            "distribution_scheduled",
            "distribution",
            scheduled_distribution.id,
            {
                "media_id": media_id,
                "platforms": platforms_list,
                "scheduled_time": scheduled_datetime.isoformat()
            }
        )
        
        return {
            "message": "Distribution scheduled successfully",
            "distribution_id": scheduled_distribution.id,
            "scheduled_time": scheduled_datetime.isoformat(),
            "platforms": platforms_list,
            "status": "scheduled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule distribution: {str(e)}")

@router.delete("/distribution/{distribution_id}")
async def cancel_distribution(distribution_id: str, current_user: User = Depends(get_current_user)):
    """Cancel a distribution (if not already completed)"""
    # Find distribution
    distribution = await db.content_distributions.find_one({"id": distribution_id})
    if not distribution:
        raise HTTPException(status_code=404, detail="Distribution not found")
    
    # Verify user owns the media
    media = await db.media_content.find_one({"id": distribution["media_id"]})
    if not media or media["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this distribution")
    
    # Check if distribution can be cancelled
    if distribution["status"] in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel distribution with status: {distribution['status']}")
    
    # Update distribution status
    await db.content_distributions.update_one(
        {"id": distribution_id},
        {
            "$set": {
                "status": "cancelled",
                "updated_at": datetime.utcnow(),
                "results": {
                    **distribution.get("results", {}),
                    "cancelled_by": current_user.id,
                    "cancelled_at": datetime.utcnow().isoformat()
                }
            }
        }
    )
    
    # Log activity
    await log_activity(
        current_user.id,
        "distribution_cancelled",
        "distribution",
        distribution_id,
        {"reason": "user_request"}
    )
    
    return {
        "message": "Distribution cancelled successfully",
        "distribution_id": distribution_id,
        "status": "cancelled"
    }

# Admin Endpoints

