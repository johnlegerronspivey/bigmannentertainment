"""
Workflow Enhancement API Endpoints
Enhanced endpoints for user workflow tracking and progress analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth.service import get_current_user
from models.core import User
from config.database import db
from workflow_enhancement_service import WorkflowEnhancementService

# Create router
workflow_router = APIRouter(prefix="/user", tags=["User Workflow"])

@workflow_router.get("/workflow-progress")
async def get_workflow_progress(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive user workflow progress and analytics"""
    try:
        service = WorkflowEnhancementService(db)
        progress = await service.get_user_workflow_progress(current_user.id)
        
        return {"workflow_progress": progress}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow progress: {str(e)}")

@workflow_router.post("/track-action")
async def track_user_action(
    action_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Track user actions for analytics and progress"""
    try:
        service = WorkflowEnhancementService(db)
        
        action = action_data.get("action")
        details = action_data.get("details", {})
        
        if not action:
            raise HTTPException(status_code=400, detail="Action is required")
        
        success = await service.track_user_action(current_user.id, action, details)
        
        if success:
            return {"message": "Action tracked successfully", "action": action}
        else:
            raise HTTPException(status_code=500, detail="Failed to track action")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track action: {str(e)}")

@workflow_router.get("/analytics")
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    period_days: int = Query(30, description="Number of days to analyze")
):
    """Get user analytics and engagement data"""
    try:
        service = WorkflowEnhancementService(db)
        analytics = await service.get_user_analytics(current_user.id, period_days)
        
        return {"analytics": analytics}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@workflow_router.get("/onboarding-status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user)
):
    """Get user's onboarding progress and completion status"""
    try:
        service = WorkflowEnhancementService(db)
        onboarding = await service.get_onboarding_status(current_user.id)
        
        return {"onboarding": onboarding}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding status: {str(e)}")

@workflow_router.get("/dashboard")
async def get_enhanced_dashboard_data(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard data including progress, analytics, and recommendations"""
    try:
        service = WorkflowEnhancementService(db)
        
        # Get all dashboard components
        progress = await service.get_user_workflow_progress(current_user.id)
        onboarding = await service.get_onboarding_status(current_user.id)
        analytics = await service.get_user_analytics(current_user.id, 7)  # Last 7 days
        
        dashboard_data = {
            "user_info": {
                "user_id": current_user.id,
                "full_name": current_user.full_name,
                "email": current_user.email,
                "member_since": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None
            },
            "progress": progress,
            "onboarding": onboarding,
            "analytics": analytics,
            "quick_actions": [
                {
                    "id": "upload",
                    "title": "Upload Content",
                    "description": "Add new media files",
                    "link": "/upload",
                    "icon": "upload",
                    "enabled": True
                },
                {
                    "id": "distribute",
                    "title": "Distribute",
                    "description": "Share to 106+ platforms",
                    "link": "/distribute", 
                    "icon": "share",
                    "enabled": progress.get("uploads_count", 0) > 0
                },
                {
                    "id": "earnings",
                    "title": "Check Earnings",
                    "description": "Monitor your revenue",
                    "link": "/earnings",
                    "icon": "dollar",
                    "enabled": progress.get("distributions_count", 0) > 0
                }
            ],
            "notifications": await _get_user_notifications(db, current_user.id),
            "tips": await _get_personalized_tips(progress, onboarding)
        }
        
        return {"dashboard": dashboard_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@workflow_router.get("/achievements")
async def get_user_achievements(
    current_user: User = Depends(get_current_user)
):
    """Get user's achievements and badges"""
    try:
        service = WorkflowEnhancementService(db)
        progress = await service.get_user_workflow_progress(current_user.id)
        
        achievements = progress.get("achievements", [])
        milestones = progress.get("milestones", [])
        
        return {
            "achievements": achievements,
            "milestones": milestones,
            "total_achievements": len(achievements),
            "total_milestones": len(milestones)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get achievements: {str(e)}")

@workflow_router.get("/next-steps")
async def get_recommended_next_steps(
    current_user: User = Depends(get_current_user),
    limit: int = Query(5, description="Maximum number of recommendations")
):
    """Get personalized next step recommendations"""
    try:
        service = WorkflowEnhancementService(db)
        progress = await service.get_user_workflow_progress(current_user.id)
        
        next_steps = progress.get("next_steps", [])
        
        return {
            "next_steps": next_steps[:limit],
            "total_recommendations": len(next_steps)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get next steps: {str(e)}")

@workflow_router.post("/complete-milestone")
async def complete_milestone(
    milestone_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Mark a milestone as completed"""
    try:
        service = WorkflowEnhancementService(db)
        
        milestone_id = milestone_data.get("milestone_id")
        milestone_type = milestone_data.get("type")
        
        if not milestone_id or not milestone_type:
            raise HTTPException(status_code=400, detail="Milestone ID and type are required")
        
        # Track the milestone completion
        success = await service.track_user_action(
            current_user.id, 
            f"milestone_completed_{milestone_type}",
            {"milestone_id": milestone_id, "type": milestone_type}
        )
        
        if success:
            return {"message": "Milestone completed successfully", "milestone_id": milestone_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to complete milestone")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete milestone: {str(e)}")

# Helper functions

async def _get_user_notifications(db, user_id: str) -> List[Dict[str, Any]]:
    """Get user notifications and alerts"""
    try:
        notifications = []
        
        # Check for pending distributions
        pending_distributions = await db.distribution_jobs.count_documents({
            "user_id": user_id,
            "status": {"$in": ["pending", "processing"]}
        })
        
        if pending_distributions > 0:
            notifications.append({
                "id": "pending_distributions",
                "type": "info",
                "title": "Distribution in Progress",
                "message": f"You have {pending_distributions} distribution(s) currently processing",
                "action": "View Status",
                "link": "/distribute"
            })
        
        # Check for new earnings (mock)
        uploads_count = await db.media_library.count_documents({"user_id": user_id})
        if uploads_count > 0:
            notifications.append({
                "id": "earnings_available",
                "type": "success",
                "title": "Earnings Update",
                "message": "New earnings data is available for your content",
                "action": "View Earnings",
                "link": "/earnings"
            })
        
        return notifications[:5]  # Return max 5 notifications
        
    except Exception as e:
        return []

async def _get_personalized_tips(progress: Dict, onboarding: Dict) -> List[Dict[str, str]]:
    """Get personalized tips based on user progress"""
    tips = []
    
    try:
        # Tips based on progress
        if progress.get("uploads_count", 0) == 0:
            tips.append({
                "id": "first_upload_tip",
                "title": "Ready to Upload?",
                "message": "Start by uploading high-quality audio, video, or image content. Make sure your files are properly tagged with metadata.",
                "category": "upload"
            })
        
        if progress.get("uploads_count", 0) > 0 and progress.get("distributions_count", 0) == 0:
            tips.append({
                "id": "distribution_tip",
                "title": "Time to Go Global",
                "message": "Your content is ready! Distribute to our 106+ platforms to maximize your reach and earnings potential.",
                "category": "distribution"
            })
        
        if progress.get("distributions_count", 0) > 0:
            tips.append({
                "id": "optimization_tip",
                "title": "Optimize Your Strategy",
                "message": "Track your performance across platforms and focus on the ones generating the most engagement and revenue.",
                "category": "analytics"
            })
        
        # General tips
        tips.extend([
            {
                "id": "metadata_tip",
                "title": "Metadata Matters",
                "message": "Complete metadata helps platforms categorize and promote your content effectively.",
                "category": "general"
            },
            {
                "id": "quality_tip",
                "title": "Quality First",
                "message": "High-quality content performs better across all platforms and generates more revenue.",
                "category": "general"
            }
        ])
        
        return tips[:3]  # Return top 3 tips
        
    except Exception as e:
        return []