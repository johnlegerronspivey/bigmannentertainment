"""
Lifecycle Management API Endpoints - Function 5: Content Lifecycle Management & Automation
Provides API endpoints for content lifecycle management, versioning, and automation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from lifecycle_management_service import (
    LifecycleManagementService,
    ContentLifecycle,
    ContentVersion,
    AutomationRule,
    LifecyclePolicy,
    ContentStatus,
    LifecycleStage,
    AutomationTrigger,
    ActionType
)

# Initialize service
lifecycle_service = LifecycleManagementService()

# Create router
router = APIRouter(prefix="/api/lifecycle", tags=["Content Lifecycle Management & Automation"])
security = HTTPBearer()

# Request models
class CreateLifecycleRequest(BaseModel):
    content_id: str
    initial_version: Dict[str, Any]
    policies: Optional[List[str]] = None

class CreateVersionRequest(BaseModel):
    content_id: str
    version_data: Dict[str, Any]
    changes_summary: str = ""
    set_as_current: bool = True

class StageTransitionRequest(BaseModel):
    content_id: str
    new_stage: LifecycleStage
    notes: str = ""

class StatusUpdateRequest(BaseModel):
    content_id: str
    new_status: ContentStatus
    notes: str = ""

class AutomationRuleRequest(BaseModel):
    rule_name: str
    description: str = ""
    trigger_type: AutomationTrigger
    trigger_conditions: Dict[str, Any] = {}
    action_type: ActionType
    action_parameters: Dict[str, Any] = {}
    applies_to_content_types: List[str] = []
    applies_to_platforms: List[str] = []

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This would integrate with your authentication system
    # For now, returning a mock user ID
    return "user_123"

# Content Lifecycle Management Endpoints

@router.post("/create")
async def create_content_lifecycle(
    request: CreateLifecycleRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new content lifecycle"""
    try:
        # Create ContentVersion object from request data
        initial_version_data = request.initial_version
        from lifecycle_management_service import ContentVersion
        
        initial_version = ContentVersion(
            content_id=request.content_id,
            version_number="1.0",
            title=initial_version_data["title"],
            description=initial_version_data.get("description"),
            file_path=initial_version_data["file_path"],
            file_size=initial_version_data.get("file_size", 0),
            file_format=initial_version_data.get("file_format", ""),
            created_by=user_id,
            metadata=initial_version_data.get("metadata", {})
        )
        
        lifecycle = await lifecycle_service.create_content_lifecycle(
            content_id=request.content_id,
            user_id=user_id,
            initial_version=initial_version,
            policies=request.policies
        )
        
        return {
            "success": True,
            "lifecycle": lifecycle,
            "message": "Content lifecycle created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Moved to end of file to avoid path conflicts

@router.get("/")
async def list_content_lifecycles(
    status: Optional[ContentStatus] = None,
    stage: Optional[LifecycleStage] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user)
):
    """List all content lifecycles for user"""
    try:
        lifecycles = await lifecycle_service.get_user_content_lifecycles(
            user_id=user_id,
            status_filter=status,
            stage_filter=stage,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "lifecycles": lifecycles,
            "total_items": len(lifecycles),
            "limit": limit,
            "offset": offset,
            "filters": {
                "status": status.value if status else None,
                "stage": stage.value if stage else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stage/transition")
async def transition_lifecycle_stage(
    request: StageTransitionRequest,
    user_id: str = Depends(get_current_user)
):
    """Transition content to a new lifecycle stage"""
    try:
        success = await lifecycle_service.transition_lifecycle_stage(
            content_id=request.content_id,
            user_id=user_id,
            new_stage=request.new_stage,
            notes=request.notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Content lifecycle not found")
        
        return {
            "success": True,
            "content_id": request.content_id,
            "new_stage": request.new_stage.value,
            "message": "Lifecycle stage transitioned successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/status/update")
async def update_content_status(
    request: StatusUpdateRequest,
    user_id: str = Depends(get_current_user)
):
    """Update content status"""
    try:
        success = await lifecycle_service.update_content_status(
            content_id=request.content_id,
            user_id=user_id,
            new_status=request.new_status,
            notes=request.notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Content lifecycle not found")
        
        return {
            "success": True,
            "content_id": request.content_id,
            "new_status": request.new_status.value,
            "message": "Content status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Versioning Endpoints

@router.post("/versions/create")
async def create_content_version(
    request: CreateVersionRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new version of existing content"""
    try:
        version = await lifecycle_service.create_content_version(
            content_id=request.content_id,
            user_id=user_id,
            version_data=request.version_data,
            changes_summary=request.changes_summary,
            set_as_current=request.set_as_current
        )
        
        return {
            "success": True,
            "version": version,
            "message": "Content version created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions/{version_id}")
async def get_content_version(
    version_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get specific content version"""
    try:
        version = await lifecycle_service.get_content_version(version_id, user_id)
        
        if not version:
            raise HTTPException(status_code=404, detail="Content version not found")
        
        return {
            "success": True,
            "version": version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_id}/versions")
async def get_content_version_history(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get version history for content"""
    try:
        lifecycle = await lifecycle_service.get_content_lifecycle(content_id, user_id)
        
        if not lifecycle:
            raise HTTPException(status_code=404, detail="Content lifecycle not found")
        
        # Get all versions for this content
        versions = []
        for version_id in lifecycle.version_history:
            version = await lifecycle_service.get_content_version(version_id, user_id)
            if version:
                versions.append(version)
        
        # Sort by version number
        versions.sort(key=lambda x: x.version_number, reverse=True)
        
        return {
            "success": True,
            "content_id": content_id,
            "versions": versions,
            "current_version_id": lifecycle.current_version_id,
            "total_versions": len(versions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Automation Management Endpoints

@router.post("/automation/rules")
async def create_automation_rule(
    request: AutomationRuleRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new automation rule"""
    try:
        rule_data = request.dict()
        rule = await lifecycle_service.create_automation_rule(user_id, rule_data)
        
        return {
            "success": True,
            "automation_rule": rule,
            "message": "Automation rule created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automation/rules")
async def list_automation_rules(
    is_active: Optional[bool] = None,
    trigger_type: Optional[AutomationTrigger] = None,
    user_id: str = Depends(get_current_user)
):
    """List automation rules for user"""
    try:
        query = {"user_id": user_id}
        
        if is_active is not None:
            query["is_active"] = is_active
        
        if trigger_type:
            query["trigger_type"] = trigger_type.value
        
        cursor = lifecycle_service.automation_rules_collection.find(query)
        rules = []
        
        for rule_data in cursor:
            try:
                rule_data['_id'] = str(rule_data['_id'])
                rules.append(AutomationRule(**rule_data))
            except Exception as e:
                print(f"Error parsing automation rule: {e}")
                continue
        
        return {
            "success": True,
            "automation_rules": rules,
            "total_rules": len(rules),
            "filters": {
                "is_active": is_active,
                "trigger_type": trigger_type.value if trigger_type else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/automation/rules/{rule_id}")
async def update_automation_rule(
    rule_id: str,
    rule_updates: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Update an automation rule"""
    try:
        # Update rule in database
        rule_updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = lifecycle_service.automation_rules_collection.update_one(
            {"rule_id": rule_id, "user_id": user_id},
            {"$set": rule_updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Automation rule not found")
        
        return {
            "success": True,
            "rule_id": rule_id,
            "message": "Automation rule updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/automation/rules/{rule_id}")
async def delete_automation_rule(
    rule_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete an automation rule"""
    try:
        result = lifecycle_service.automation_rules_collection.delete_one({
            "rule_id": rule_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Automation rule not found")
        
        return {
            "success": True,
            "rule_id": rule_id,
            "message": "Automation rule deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard and Analytics Endpoints

@router.get("/dashboard")
async def get_lifecycle_dashboard(
    user_id: str = Depends(get_current_user)
):
    """Get lifecycle management dashboard"""
    try:
        dashboard = await lifecycle_service.get_lifecycle_dashboard(user_id)
        
        return {
            "success": True,
            "dashboard": dashboard,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/summary")
async def get_lifecycle_analytics_summary(
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get lifecycle analytics summary"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get lifecycle changes in the period
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "updated_at": {"$gte": cutoff_date.isoformat()}
                }
            },
            {
                "$group": {
                    "_id": "$current_status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_activity = {}
        cursor = lifecycle_service.lifecycles_collection.aggregate(pipeline)
        
        for result in cursor:
            status_activity[result["_id"]] = result["count"]
        
        # Get automation activity
        automation_cursor = lifecycle_service.automation_rules_collection.find({
            "user_id": user_id,
            "last_executed": {"$gte": cutoff_date.isoformat()}
        })
        
        automation_executions = list(automation_cursor)
        
        summary = {
            "period_days": days,
            "status_activity": status_activity,
            "total_status_changes": sum(status_activity.values()),
            "automation_executions": len(automation_executions),
            "total_automation_runs": sum(rule.get("execution_count", 0) for rule in automation_executions),
            "most_active_status": max(status_activity.items(), key=lambda x: x[1])[0] if status_activity else None,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "analytics_summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Configuration and Templates Endpoints

@router.get("/templates/automation-rules")
async def get_automation_rule_templates(
    user_id: str = Depends(get_current_user)
):
    """Get automation rule templates"""
    try:
        templates = {
            "auto_archive_old_content": {
                "name": "Auto-Archive Old Content",
                "description": "Automatically archive content that hasn't been viewed in 90 days",
                "trigger_type": "time_based",
                "trigger_conditions": {"days_inactive": 90},
                "action_type": "archive_content",
                "action_parameters": {"reason": "Inactive for 90 days"}
            },
            "promote_high_performing_content": {
                "name": "Promote High-Performing Content",
                "description": "Automatically promote content with high engagement rates",
                "trigger_type": "performance_based",
                "trigger_conditions": {"engagement_rate_threshold": 10.0},
                "action_type": "promote_content",
                "action_parameters": {"promotion_budget": 50}
            },
            "notify_low_performance": {
                "name": "Notify for Low Performance",
                "description": "Send notification when content underperforms",
                "trigger_type": "performance_based",
                "trigger_conditions": {"views_threshold": 100, "days_since_publish": 7},
                "action_type": "send_notification",
                "action_parameters": {"message": "Content may need optimization"}
            },
            "schedule_content_review": {
                "name": "Schedule Content Review",
                "description": "Schedule regular content reviews",
                "trigger_type": "time_based",
                "trigger_conditions": {"interval_days": 30},
                "action_type": "send_notification",
                "action_parameters": {"message": "Time for content review"}
            }
        }
        
        return {
            "success": True,
            "automation_templates": templates,
            "total_templates": len(templates)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enums")
async def get_lifecycle_enums(
    user_id: str = Depends(get_current_user)
):
    """Get available enum values for lifecycle management"""
    try:
        enums = {
            "content_statuses": [status.value for status in ContentStatus],
            "lifecycle_stages": [stage.value for stage in LifecycleStage],
            "automation_triggers": [trigger.value for trigger in AutomationTrigger],
            "action_types": [action.value for action in ActionType]
        }
        
        return {
            "success": True,
            "enums": enums
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Bulk Operations Endpoints

@router.post("/bulk/status-update")
async def bulk_status_update(
    content_ids: List[str],
    new_status: ContentStatus,
    notes: str = "",
    user_id: str = Depends(get_current_user)
):
    """Update status for multiple content items"""
    try:
        updated_count = 0
        failed_updates = []
        
        for content_id in content_ids:
            try:
                success = await lifecycle_service.update_content_status(
                    content_id, user_id, new_status, notes
                )
                if success:
                    updated_count += 1
                else:
                    failed_updates.append({"content_id": content_id, "error": "Not found"})
            except Exception as e:
                failed_updates.append({"content_id": content_id, "error": str(e)})
        
        return {
            "success": len(failed_updates) == 0,
            "updated_count": updated_count,
            "failed_updates": failed_updates,
            "total_requested": len(content_ids),
            "new_status": new_status.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk/stage-transition")
async def bulk_stage_transition(
    content_ids: List[str],
    new_stage: LifecycleStage,
    notes: str = "",
    user_id: str = Depends(get_current_user)
):
    """Transition multiple content items to new stage"""
    try:
        updated_count = 0
        failed_updates = []
        
        for content_id in content_ids:
            try:
                success = await lifecycle_service.transition_lifecycle_stage(
                    content_id, user_id, new_stage, notes
                )
                if success:
                    updated_count += 1
                else:
                    failed_updates.append({"content_id": content_id, "error": "Not found"})
            except Exception as e:
                failed_updates.append({"content_id": content_id, "error": str(e)})
        
        return {
            "success": len(failed_updates) == 0,
            "updated_count": updated_count,
            "failed_updates": failed_updates,
            "total_requested": len(content_ids),
            "new_stage": new_stage.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Health and Monitoring

@router.get("/health")
async def health_check():
    """Health check endpoint for lifecycle management service"""
    try:
        # Test database connections
        lifecycles_count = lifecycle_service.lifecycles_collection.count_documents({})
        versions_count = lifecycle_service.versions_collection.count_documents({})
        automation_rules_count = lifecycle_service.automation_rules_collection.count_documents({})
        
        health_status = {
            "service": "Content Lifecycle Management & Automation API",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "5.0.0",
            "database_connection": "healthy",
            "scheduler_running": lifecycle_service.scheduler_running,
            "total_lifecycles": lifecycles_count,
            "total_versions": versions_count,
            "total_automation_rules": automation_rules_count,
            "supported_statuses": len(ContentStatus),
            "supported_stages": len(LifecycleStage),
            "supported_triggers": len(AutomationTrigger),
            "supported_actions": len(ActionType)
        }
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }

# Content lifecycle detail endpoint - placed at end to avoid path conflicts
@router.get("/{content_id}")
async def get_content_lifecycle(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get content lifecycle details"""
    try:
        lifecycle = await lifecycle_service.get_content_lifecycle(content_id, user_id)
        
        if not lifecycle:
            raise HTTPException(status_code=404, detail="Content lifecycle not found")
        
        return {
            "success": True,
            "lifecycle": lifecycle
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))