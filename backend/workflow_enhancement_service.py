"""
Workflow Enhancement Service
Provides workflow progress tracking and user journey analytics for Big Mann Entertainment
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class WorkflowEnhancementService:
    """Service to track and enhance user workflow progression"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def get_user_workflow_progress(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user workflow progress"""
        try:
            # Get user's content uploads
            uploads_count = await self.db.media_library.count_documents({"user_id": user_id})
            
            # Get user's distributions
            distributions_count = await self.db.distribution_jobs.count_documents({"user_id": user_id})
            
            # Get user's earnings (mock data for now)
            earnings_data = await self._calculate_user_earnings(user_id)
            
            # Get user's payouts
            payouts_count = await self.db.payout_requests.count_documents({"user_id": user_id})
            
            # Calculate progress percentages
            progress_data = {
                "uploads_count": uploads_count,
                "library_count": uploads_count,  # Same as uploads for now
                "distributions_count": distributions_count,
                "earnings_total": earnings_data.get("total_earnings", 0),
                "earnings_pending": earnings_data.get("pending_earnings", 0),
                "earnings_paid": earnings_data.get("paid_earnings", 0),
                "payouts_count": payouts_count,
                "workflow_completion": await self._calculate_workflow_completion(user_id),
                "next_steps": await self._get_next_steps(user_id),
                "achievements": await self._get_user_achievements(user_id),
                "milestones": await self._get_user_milestones(user_id)
            }
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error getting user workflow progress: {str(e)}")
            return {
                "uploads_count": 0,
                "library_count": 0,
                "distributions_count": 0,
                "earnings_total": 0,
                "earnings_pending": 0,
                "earnings_paid": 0,
                "payouts_count": 0,
                "workflow_completion": 0,
                "next_steps": [],
                "achievements": [],
                "milestones": []
            }
    
    async def track_user_action(self, user_id: str, action: str, details: Dict[str, Any] = None) -> bool:
        """Track user actions for analytics and progress"""
        try:
            action_record = {
                "user_id": user_id,
                "action": action,
                "details": details or {},
                "timestamp": datetime.now(timezone.utc),
                "session_id": details.get("session_id") if details else None
            }
            
            await self.db.user_actions.insert_one(action_record)
            
            # Update user progress milestones
            await self._update_user_milestones(user_id, action)
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking user action: {str(e)}")
            return False
    
    async def get_user_analytics(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get user analytics for the specified period"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            
            # Get action counts by type
            action_pipeline = [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start_date}}},
                {"$group": {"_id": "$action", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            action_counts = {}
            async for result in self.db.user_actions.aggregate(action_pipeline):
                action_counts[result["_id"]] = result["count"]
            
            # Get daily activity
            daily_pipeline = [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$timestamp"
                            }
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            daily_activity = []
            async for result in self.db.user_actions.aggregate(daily_pipeline):
                daily_activity.append({
                    "date": result["_id"],
                    "activity_count": result["count"]
                })
            
            analytics = {
                "period_days": period_days,
                "total_actions": sum(action_counts.values()),
                "action_breakdown": action_counts,
                "daily_activity": daily_activity,
                "most_active_day": max(daily_activity, key=lambda x: x["activity_count"]) if daily_activity else None,
                "engagement_score": await self._calculate_engagement_score(user_id, period_days)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return {}
    
    async def get_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's onboarding progress and status"""
        try:
            onboarding_steps = [
                {"step": "registration", "title": "Account Created", "completed": True},
                {"step": "profile", "title": "Profile Completed", "completed": await self._check_profile_completion(user_id)},
                {"step": "upload", "title": "First Upload", "completed": await self._check_first_upload(user_id)},
                {"step": "distribution", "title": "First Distribution", "completed": await self._check_first_distribution(user_id)},
                {"step": "earnings", "title": "First Earnings", "completed": await self._check_first_earnings(user_id)}
            ]
            
            completed_steps = sum(1 for step in onboarding_steps if step["completed"])
            total_steps = len(onboarding_steps)
            
            return {
                "onboarding_steps": onboarding_steps,
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "completion_percentage": (completed_steps / total_steps) * 100,
                "current_step": next((i + 1 for i, step in enumerate(onboarding_steps) if not step["completed"]), total_steps),
                "is_complete": completed_steps == total_steps,
                "next_action": await self._get_next_onboarding_action(onboarding_steps)
            }
            
        except Exception as e:
            logger.error(f"Error getting onboarding status: {str(e)}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _calculate_user_earnings(self, user_id: str) -> Dict[str, float]:
        """Calculate user's earnings (mock implementation)"""
        try:
            # In a real implementation, this would calculate actual earnings
            # For now, return mock data based on user activity
            distributions = await self.db.distribution_jobs.count_documents({"user_id": user_id})
            uploads = await self.db.media_library.count_documents({"user_id": user_id})
            
            # Mock earnings calculation
            base_earnings = (distributions * 15.75) + (uploads * 5.50)
            total_earnings = base_earnings
            pending_earnings = base_earnings * 0.3
            paid_earnings = base_earnings * 0.7
            
            return {
                "total_earnings": round(total_earnings, 2),
                "pending_earnings": round(pending_earnings, 2),
                "paid_earnings": round(paid_earnings, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating earnings: {str(e)}")
            return {"total_earnings": 0, "pending_earnings": 0, "paid_earnings": 0}
    
    async def _calculate_workflow_completion(self, user_id: str) -> int:
        """Calculate overall workflow completion percentage"""
        try:
            milestones = [
                await self._check_profile_completion(user_id),
                await self._check_first_upload(user_id),
                await self._check_first_distribution(user_id),
                await self._check_first_earnings(user_id),
                await self.db.payout_requests.count_documents({"user_id": user_id}) > 0
            ]
            
            completed = sum(1 for milestone in milestones if milestone)
            return int((completed / len(milestones)) * 100)
            
        except Exception as e:
            logger.error(f"Error calculating workflow completion: {str(e)}")
            return 0
    
    async def _get_next_steps(self, user_id: str) -> List[Dict[str, str]]:
        """Get recommended next steps for the user"""
        next_steps = []
        
        try:
            # Check what the user hasn't done yet and suggest next steps
            if not await self._check_first_upload(user_id):
                next_steps.append({
                    "action": "upload_content",
                    "title": "Upload Your First Content",
                    "description": "Start by uploading your media content to get ready for distribution",
                    "link": "/upload",
                    "priority": "high"
                })
            elif not await self._check_first_distribution(user_id):
                next_steps.append({
                    "action": "start_distribution",
                    "title": "Distribute to Platforms",
                    "description": "Share your content across 106+ platforms worldwide",
                    "link": "/distribute", 
                    "priority": "high"
                })
            elif not await self._check_first_earnings(user_id):
                next_steps.append({
                    "action": "check_earnings",
                    "title": "Monitor Your Earnings",
                    "description": "Track revenue and royalties from your distributed content",
                    "link": "/earnings",
                    "priority": "medium"
                })
            else:
                next_steps.append({
                    "action": "optimize_strategy",
                    "title": "Optimize Your Strategy", 
                    "description": "Analyze performance and optimize your distribution strategy",
                    "link": "/analytics",
                    "priority": "low"
                })
            
            return next_steps[:3]  # Return top 3 next steps
            
        except Exception as e:
            logger.error(f"Error getting next steps: {str(e)}")
            return []
    
    async def _get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's achievements and badges"""
        achievements = []
        
        try:
            uploads_count = await self.db.media_library.count_documents({"user_id": user_id})
            distributions_count = await self.db.distribution_jobs.count_documents({"user_id": user_id})
            
            # First upload achievement
            if uploads_count >= 1:
                achievements.append({
                    "id": "first_upload",
                    "title": "First Upload",
                    "description": "Uploaded your first content",
                    "icon": "🎵",
                    "unlocked_at": datetime.now(timezone.utc).isoformat()
                })
            
            # Multiple uploads achievements
            if uploads_count >= 10:
                achievements.append({
                    "id": "content_creator",
                    "title": "Content Creator",
                    "description": "Uploaded 10+ pieces of content",
                    "icon": "🎨",
                    "unlocked_at": datetime.now(timezone.utc).isoformat()
                })
            
            # Distribution achievements
            if distributions_count >= 1:
                achievements.append({
                    "id": "global_distributor",
                    "title": "Global Distributor",
                    "description": "Started your first distribution",
                    "icon": "🌍",
                    "unlocked_at": datetime.now(timezone.utc).isoformat()
                })
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error getting achievements: {str(e)}")
            return []
    
    async def _get_user_milestones(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's milestones and progress markers"""
        try:
            milestones = []
            
            # Check for key milestones
            user_created = await self.db.users.find_one({"id": user_id})
            if user_created:
                milestones.append({
                    "id": "account_created",
                    "title": "Account Created",
                    "achieved": True,
                    "date": user_created.get("created_at", datetime.now(timezone.utc)).isoformat()
                })
            
            first_upload = await self.db.media_library.find_one({"user_id": user_id})
            if first_upload:
                milestones.append({
                    "id": "first_upload", 
                    "title": "First Content Uploaded",
                    "achieved": True,
                    "date": first_upload.get("created_at", datetime.now(timezone.utc)).isoformat()
                })
            
            first_distribution = await self.db.distribution_jobs.find_one({"user_id": user_id})
            if first_distribution:
                milestones.append({
                    "id": "first_distribution",
                    "title": "First Distribution Started", 
                    "achieved": True,
                    "date": first_distribution.get("created_at", datetime.now(timezone.utc)).isoformat()
                })
            
            return milestones
            
        except Exception as e:
            logger.error(f"Error getting milestones: {str(e)}")
            return []
    
    async def _update_user_milestones(self, user_id: str, action: str):
        """Update user milestones based on actions"""
        try:
            milestone_record = {
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.now(timezone.utc),
                "milestone_type": self._get_milestone_type(action)
            }
            
            # Only insert if this milestone doesn't already exist
            existing = await self.db.user_milestones.find_one({
                "user_id": user_id,
                "milestone_type": milestone_record["milestone_type"]
            })
            
            if not existing:
                await self.db.user_milestones.insert_one(milestone_record)
                
        except Exception as e:
            logger.error(f"Error updating milestones: {str(e)}")
    
    def _get_milestone_type(self, action: str) -> str:
        """Map action to milestone type"""
        milestone_mapping = {
            "upload": "first_upload",
            "distribute": "first_distribution", 
            "earnings": "first_earnings",
            "payout": "first_payout"
        }
        return milestone_mapping.get(action, "other")
    
    async def _check_profile_completion(self, user_id: str) -> bool:
        """Check if user profile is complete"""
        try:
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                return False
                
            required_fields = ["full_name", "email", "business_name", "address_line1", "city", "country"]
            return all(user.get(field) for field in required_fields)
            
        except Exception as e:
            logger.error(f"Error checking profile completion: {str(e)}")
            return False
    
    async def _check_first_upload(self, user_id: str) -> bool:
        """Check if user has made their first upload"""
        try:
            return await self.db.media_library.count_documents({"user_id": user_id}) > 0
        except Exception as e:
            logger.error(f"Error checking first upload: {str(e)}")
            return False
    
    async def _check_first_distribution(self, user_id: str) -> bool:
        """Check if user has started their first distribution"""
        try:
            return await self.db.distribution_jobs.count_documents({"user_id": user_id}) > 0
        except Exception as e:
            logger.error(f"Error checking first distribution: {str(e)}")
            return False
    
    async def _check_first_earnings(self, user_id: str) -> bool:
        """Check if user has received their first earnings"""
        try:
            # Mock check - in real implementation, check actual earnings records
            distributions = await self.db.distribution_jobs.count_documents({"user_id": user_id})
            return distributions > 0  # Assume earnings after first distribution
        except Exception as e:
            logger.error(f"Error checking first earnings: {str(e)}")
            return False
    
    async def _get_next_onboarding_action(self, onboarding_steps: List[Dict]) -> Optional[Dict[str, str]]:
        """Get the next recommended onboarding action"""
        for step in onboarding_steps:
            if not step["completed"]:
                action_mapping = {
                    "profile": {"title": "Complete Your Profile", "link": "/profile"},
                    "upload": {"title": "Upload Content", "link": "/upload"},
                    "distribution": {"title": "Start Distribution", "link": "/distribute"},
                    "earnings": {"title": "Check Earnings", "link": "/earnings"}
                }
                return action_mapping.get(step["step"], {"title": "Continue Setup", "link": "/"})
        
        return None
    
    async def _calculate_engagement_score(self, user_id: str, period_days: int) -> int:
        """Calculate user engagement score (0-100)"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            
            # Count different types of engagement
            action_count = await self.db.user_actions.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            })
            
            # Calculate score based on activity
            if action_count >= 50:
                return 100
            elif action_count >= 25:
                return 80
            elif action_count >= 10:
                return 60
            elif action_count >= 5:
                return 40
            elif action_count >= 1:
                return 20
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0