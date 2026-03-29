"""Admin endpoints - notifications, user management, content moderation."""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Form
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from auth.service import get_current_user, get_current_admin_user
from models.core import User, MediaContent, UserUpdate, ContentModerationAction
from models.agency import NotificationRequest

router = APIRouter(tags=["Admin"])

@router.post("/admin/send-notification")
async def send_notification(
    notification: NotificationRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """Send notification email to user"""
    try:
        email_sent = await email_service.send_notification_email(
            notification.email,
            notification.subject,
            notification.message,
            notification.user_name
        )
        
        if email_sent:
            return {"message": "Notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email service error: {str(e)}")

# Bulk notification endpoint
@router.post("/admin/send-bulk-notification")
async def send_bulk_notification(
    subject: str = Form(...),
    message: str = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Send notification to all active users"""
    try:
        # Get all active users
        users = []
        async for user_doc in db.users.find({"is_active": True}):
            # Remove MongoDB _id field to prevent ObjectId serialization issues
            if "_id" in user_doc:
                del user_doc["_id"]
            users.append(User(**user_doc))
        
        success_count = 0
        failure_count = 0
        
        for user in users:
            try:
                email_sent = await email_service.send_notification_email(
                    user.email,
                    subject,
                    message,
                    user.full_name
                )
                if email_sent:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                print(f"Failed to send notification to {user.email}: {str(e)}")
                failure_count += 1
        
        return {
            "message": f"Bulk notification completed",
            "total_users": len(users),
            "successful": success_count,
            "failed": failure_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk notification failed: {str(e)}")


@router.get("/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    cursor = db.users.find({}, {"password_hash": 0}).skip(skip).limit(limit).sort("created_at", -1)
    users = []
    
    async for user_doc in cursor:
        # Remove MongoDB _id field to prevent ObjectId serialization issues
        if "_id" in user_doc:
            del user_doc["_id"]
        users.append(User(**user_doc))
    
    total_count = await db.users.count_documents({})
    
    return {
        "users": users,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@router.put("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    # OWNERSHIP PROTECTION — block changes to protected owner account
    from utils.ownership_guard import block_protected_user_update, log_ownership_violation, is_protected_owner
    update_fields = {}
    if user_update.full_name is not None:
        update_fields["full_name"] = user_update.full_name
    if user_update.business_name is not None:
        update_fields["business_name"] = user_update.business_name
    if user_update.is_active is not None:
        update_fields["is_active"] = user_update.is_active
    if user_update.role is not None:
        update_fields["role"] = user_update.role
        update_fields["is_admin"] = user_update.role in ["admin", "super_admin", "moderator"]
    if user_update.account_status is not None:
        update_fields["account_status"] = user_update.account_status

    blocked = block_protected_user_update(user_id, update_fields, actor_description=current_user.id)
    if blocked:
        await log_ownership_violation(db, current_user.id, "admin_update_user", {"target": user_id, "updates": list(update_fields.keys())})
        raise HTTPException(status_code=403, detail=blocked)

    # Find user
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build update data
    update_data = update_fields.copy()
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    # Get updated user
    updated_user_doc = await db.users.find_one({"id": user_id}, {"password_hash": 0})
    
    # Remove MongoDB _id field to prevent ObjectId serialization issues
    if "_id" in updated_user_doc:
        del updated_user_doc["_id"]
    
    return User(**updated_user_doc)

@router.get("/admin/media")
async def get_all_media(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    cursor = db.media_content.find({}).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    total_count = await db.media_content.count_documents({})
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@router.post("/admin/media/{media_id}/moderate")
async def moderate_content(
    media_id: str,
    action: ContentModerationAction,
    current_user: User = Depends(get_current_admin_user)
):
    # Find media
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Update based on action
    update_data = {"updated_at": datetime.utcnow()}
    
    if action.action == "approve":
        update_data.update({
            "is_approved": True,
            "approval_status": "approved",
            "is_published": True
        })
    elif action.action == "reject":
        update_data.update({
            "is_approved": False,
            "approval_status": "rejected",
            "is_published": False
        })
    elif action.action == "feature":
        update_data["is_featured"] = True
    elif action.action == "unfeature":
        update_data["is_featured"] = False
    
    if action.notes:
        update_data["moderation_notes"] = action.notes
    
    await db.media_content.update_one({"id": media_id}, {"$set": update_data})
    
    return {"message": f"Content {action.action}d successfully"}

# Add missing admin content endpoints
@router.get("/admin/content/pending")
async def get_pending_content(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    """Get content pending approval"""
    cursor = db.media_content.find({"approval_status": "pending"}).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    total_count = await db.media_content.count_documents({"approval_status": "pending"})
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@router.get("/admin/content/reported")
async def get_reported_content(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    """Get reported content"""
    cursor = db.media_content.find({"$or": [{"approval_status": "reported"}, {"moderation_notes": {"$exists": True}}]}).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    total_count = await db.media_content.count_documents({"$or": [{"approval_status": "reported"}, {"moderation_notes": {"$exists": True}}]})
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }



@router.get("/admin/analytics")
async def get_admin_analytics(current_user: User = Depends(get_current_admin_user)):
    # Get various analytics
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    total_media = await db.media_content.count_documents({})
    approved_media = await db.media_content.count_documents({"is_approved": True})
    total_distributions = await db.content_distributions.count_documents({})
    
    # Get recent activity (simplified)
    recent_users = await db.users.count_documents({
        "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    recent_media = await db.media_content.count_documents({
        "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "recent": recent_users
        },
        "media": {
            "total": total_media,
            "approved": approved_media,
            "recent": recent_media
        },
        "distributions": {
            "total": total_distributions
        },
        "platforms": {
            "total": len(DISTRIBUTION_PLATFORMS),
            "by_type": {}
        }
    }


