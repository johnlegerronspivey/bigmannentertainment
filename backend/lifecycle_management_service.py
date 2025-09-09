"""
Lifecycle Management Service - Function 5: Content Lifecycle Management & Automation
Handles automated content workflows, versioning, lifecycle policies, and optimization.
"""

import os
import uuid
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from pymongo import MongoClient
import schedule
import threading

class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    LIVE = "live"
    PAUSED = "paused"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DELETED = "deleted"

class LifecycleStage(str, Enum):
    CREATION = "creation"
    PRODUCTION = "production"
    REVIEW = "review"
    DISTRIBUTION = "distribution"
    ACTIVE = "active"
    OPTIMIZATION = "optimization"
    MAINTENANCE = "maintenance"
    RETIREMENT = "retirement"

class AutomationTrigger(str, Enum):
    TIME_BASED = "time_based"
    PERFORMANCE_BASED = "performance_based"
    ENGAGEMENT_BASED = "engagement_based"
    REVENUE_BASED = "revenue_based"
    USER_ACTION = "user_action"
    EXTERNAL_EVENT = "external_event"

class ActionType(str, Enum):
    PROMOTE_CONTENT = "promote_content"
    PAUSE_CONTENT = "pause_content"
    ARCHIVE_CONTENT = "archive_content"
    UPDATE_METADATA = "update_metadata"
    REDISTRIBUTE = "redistribute"
    SEND_NOTIFICATION = "send_notification"
    GENERATE_REPORT = "generate_report"
    OPTIMIZE_TAGS = "optimize_tags"
    SCHEDULE_REPOST = "schedule_repost"
    UPDATE_PRICING = "update_pricing"

class ContentVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    version_number: str
    title: str
    description: Optional[str] = None
    file_path: str
    file_size: int
    file_format: str
    
    # Version metadata
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_current: bool = False
    is_published: bool = False
    
    # Changes from previous version
    changes_summary: str = ""
    parent_version_id: Optional[str] = None
    
    # Quality metrics
    quality_score: Optional[float] = None
    metadata: Dict[str, Any] = {}

class LifecyclePolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    policy_name: str
    description: str
    
    # Policy conditions
    content_types: List[str] = []  # Which content types this applies to
    platforms: List[str] = []      # Which platforms this applies to
    
    # Stage-specific rules
    stage_rules: Dict[LifecycleStage, Dict[str, Any]] = {}
    
    # Automation rules
    automation_rules: List[Dict[str, Any]] = []
    
    # Policy settings
    is_active: bool = True
    priority: int = 1  # Higher number = higher priority
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class ContentLifecycle(BaseModel):
    lifecycle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    user_id: str
    
    # Current state
    current_status: ContentStatus = ContentStatus.DRAFT
    current_stage: LifecycleStage = LifecycleStage.CREATION
    
    # Version management
    current_version_id: str
    version_history: List[str] = []  # List of version IDs
    
    # Lifecycle timeline
    stage_history: List[Dict[str, Any]] = []
    status_history: List[Dict[str, Any]] = []
    
    # Automation tracking
    active_automations: List[str] = []  # List of automation rule IDs
    completed_actions: List[Dict[str, Any]] = []
    scheduled_actions: List[Dict[str, Any]] = []
    
    # Performance triggers
    performance_thresholds: Dict[str, float] = {}
    last_performance_check: Optional[datetime] = None
    
    # Lifecycle policies applied
    applied_policies: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Expiration and archival
    expires_at: Optional[datetime] = None
    archive_after: Optional[datetime] = None
    auto_delete_after: Optional[datetime] = None

class AutomationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    rule_name: str
    description: str
    
    # Trigger configuration
    trigger_type: AutomationTrigger
    trigger_conditions: Dict[str, Any] = {}
    
    # Action configuration
    action_type: ActionType
    action_parameters: Dict[str, Any] = {}
    
    # Rule settings
    is_active: bool = True
    applies_to_content_types: List[str] = []
    applies_to_platforms: List[str] = []
    
    # Execution tracking
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class LifecycleManagementService:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ.get('MONGO_URL'))
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'bigmann_entertainment')]
        
        # Collections
        self.lifecycles_collection = self.db['content_lifecycles']
        self.versions_collection = self.db['content_versions']
        self.policies_collection = self.db['lifecycle_policies']
        self.automation_rules_collection = self.db['automation_rules']
        
        # Initialize automation scheduler
        self.scheduler_running = False
        self.start_automation_scheduler()
        
        # Default lifecycle policies
        self.default_policies = self._initialize_default_policies()
    
    def _initialize_default_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default lifecycle policies"""
        return {
            "music_standard": {
                "name": "Standard Music Content Policy",
                "description": "Standard lifecycle policy for music content",
                "stage_rules": {
                    LifecycleStage.CREATION: {
                        "max_duration_days": 7,
                        "required_metadata": ["title", "artist", "genre", "duration"]
                    },
                    LifecycleStage.REVIEW: {
                        "max_duration_days": 3,
                        "auto_approve_threshold": 0.8
                    },
                    LifecycleStage.ACTIVE: {
                        "performance_review_interval_days": 30,
                        "auto_archive_threshold": {"views": 100, "days": 90}
                    }
                }
            },
            "video_standard": {
                "name": "Standard Video Content Policy",
                "description": "Standard lifecycle policy for video content",
                "stage_rules": {
                    LifecycleStage.CREATION: {
                        "max_duration_days": 14,
                        "required_metadata": ["title", "description", "tags", "thumbnail"]
                    },
                    LifecycleStage.REVIEW: {
                        "max_duration_days": 5,
                        "quality_threshold": 0.7
                    },
                    LifecycleStage.ACTIVE: {
                        "performance_review_interval_days": 14,
                        "auto_promote_threshold": {"views": 10000, "engagement_rate": 5.0}
                    }
                }
            }
        }
    
    def start_automation_scheduler(self):
        """Start the automation scheduler in a background thread"""
        if not self.scheduler_running:
            self.scheduler_running = True
            
            # Schedule automation checks
            schedule.every(1).hours.do(self._run_automation_checks)
            schedule.every(1).days.at("02:00").do(self._run_lifecycle_maintenance)
            
            # Start scheduler thread
            scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            scheduler_thread.start()
            
            print("✅ Lifecycle automation scheduler started")
    
    def _run_scheduler(self):
        """Run the automation scheduler"""
        while self.scheduler_running:
            schedule.run_pending()
            threading.Event().wait(60)  # Check every minute
    
    async def create_content_lifecycle(self, 
                                     content_id: str,
                                     user_id: str,
                                     initial_version: ContentVersion,
                                     policies: List[str] = None) -> ContentLifecycle:
        """Create a new content lifecycle"""
        
        # Create initial version
        initial_version.content_id = content_id
        initial_version.created_by = user_id
        initial_version.is_current = True
        
        version_dict = initial_version.dict()
        version_dict["created_at"] = initial_version.created_at.isoformat()
        
        version_result = self.versions_collection.insert_one(version_dict)
        version_id = str(version_result.inserted_id)
        
        # Update the version document with the version_id
        self.versions_collection.update_one(
            {"_id": version_result.inserted_id},
            {"$set": {"version_id": version_id}}
        )
        
        # Create lifecycle
        lifecycle = ContentLifecycle(
            content_id=content_id,
            user_id=user_id,
            current_version_id=version_id,
            version_history=[version_id],
            applied_policies=policies or []
        )
        
        # Add initial stage history
        lifecycle.stage_history.append({
            "stage": LifecycleStage.CREATION.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": "Content lifecycle created"
        })
        
        lifecycle.status_history.append({
            "status": ContentStatus.DRAFT.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": "Initial content creation"
        })
        
        # Apply default policies if none specified
        if not policies:
            content_type = initial_version.metadata.get("content_type", "music")
            if content_type in self.default_policies:
                await self._apply_lifecycle_policy(lifecycle, f"{content_type}_standard")
        
        # Store lifecycle
        lifecycle_dict = lifecycle.dict()
        lifecycle_dict["created_at"] = lifecycle.created_at.isoformat()
        lifecycle_dict["updated_at"] = lifecycle.updated_at.isoformat()
        
        if lifecycle.expires_at:
            lifecycle_dict["expires_at"] = lifecycle.expires_at.isoformat()
        if lifecycle.archive_after:
            lifecycle_dict["archive_after"] = lifecycle.archive_after.isoformat()
        if lifecycle.auto_delete_after:
            lifecycle_dict["auto_delete_after"] = lifecycle.auto_delete_after.isoformat()
        if lifecycle.last_performance_check:
            lifecycle_dict["last_performance_check"] = lifecycle.last_performance_check.isoformat()
        
        result = self.lifecycles_collection.insert_one(lifecycle_dict)
        lifecycle.lifecycle_id = str(result.inserted_id)
        
        # Update the lifecycle document with the lifecycle_id
        self.lifecycles_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"lifecycle_id": lifecycle.lifecycle_id}}
        )
        
        return lifecycle
    
    async def create_content_version(self, 
                                   content_id: str,
                                   user_id: str,
                                   version_data: Dict[str, Any],
                                   changes_summary: str = "",
                                   set_as_current: bool = True) -> ContentVersion:
        """Create a new version of existing content"""
        
        # Get current lifecycle
        lifecycle = await self.get_content_lifecycle(content_id, user_id)
        if not lifecycle:
            raise ValueError("Content lifecycle not found")
        
        # Get current version for reference
        current_version = await self.get_content_version(lifecycle.current_version_id, user_id)
        
        # Determine next version number
        version_parts = current_version.version_number.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1]) if len(version_parts) > 1 else 0
        
        # Increment version (minor for small changes, major for significant changes)
        if len(changes_summary.split()) > 10:  # Significant changes
            new_version = f"{major + 1}.0"
        else:
            new_version = f"{major}.{minor + 1}"
        
        # Create new version
        new_version_obj = ContentVersion(
            content_id=content_id,
            version_number=new_version,
            title=version_data.get("title", current_version.title),
            description=version_data.get("description", current_version.description),
            file_path=version_data["file_path"],
            file_size=version_data.get("file_size", 0),
            file_format=version_data.get("file_format", current_version.file_format),
            created_by=user_id,
            changes_summary=changes_summary,
            parent_version_id=current_version.version_id,
            metadata=version_data.get("metadata", {})
        )
        
        # Set as current if requested
        if set_as_current:
            new_version_obj.is_current = True
            # Update previous version
            self.versions_collection.update_one(
                {"version_id": current_version.version_id, "created_by": user_id},
                {"$set": {"is_current": False}}
            )
        
        # Store new version
        version_dict = new_version_obj.dict()
        version_dict["created_at"] = new_version_obj.created_at.isoformat()
        
        result = self.versions_collection.insert_one(version_dict)
        new_version_obj.version_id = str(result.inserted_id)
        
        # Update the version document with the version_id
        self.versions_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"version_id": new_version_obj.version_id}}
        )
        
        # Update lifecycle
        if set_as_current:
            await self._update_lifecycle_current_version(content_id, user_id, new_version_obj.version_id)
        
        return new_version_obj
    
    async def transition_lifecycle_stage(self, 
                                       content_id: str,
                                       user_id: str,
                                       new_stage: LifecycleStage,
                                       notes: str = "") -> bool:
        """Transition content to a new lifecycle stage"""
        
        try:
            lifecycle = await self.get_content_lifecycle(content_id, user_id)
            if not lifecycle:
                return False
            
            old_stage = lifecycle.current_stage
            
            # Add to stage history
            stage_entry = {
                "stage": new_stage.value,
                "previous_stage": old_stage.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "notes": notes
            }
            
            # Update lifecycle
            update_operations = {
                "$set": {
                    "current_stage": new_stage.value,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"stage_history": stage_entry}
            }
            
            self.lifecycles_collection.update_one(
                {"content_id": content_id, "user_id": user_id},
                update_operations
            )
            
            # Trigger stage-specific automations
            await self._trigger_stage_automations(content_id, user_id, new_stage)
            
            return True
            
        except Exception as e:
            print(f"Error transitioning lifecycle stage: {e}")
            return False
    
    async def update_content_status(self, 
                                  content_id: str,
                                  user_id: str,
                                  new_status: ContentStatus,
                                  notes: str = "") -> bool:
        """Update content status"""
        
        try:
            lifecycle = await self.get_content_lifecycle(content_id, user_id)
            if not lifecycle:
                return False
            
            old_status = lifecycle.current_status
            
            # Add to status history
            status_entry = {
                "status": new_status.value,
                "previous_status": old_status.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "notes": notes
            }
            
            # Update lifecycle
            update_operations = {
                "$set": {
                    "current_status": new_status.value,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"status_history": status_entry}
            }
            
            self.lifecycles_collection.update_one(
                {"content_id": content_id, "user_id": user_id},
                update_operations
            )
            
            # Trigger status-specific automations
            await self._trigger_status_automations(content_id, user_id, new_status)
            
            return True
            
        except Exception as e:
            print(f"Error updating content status: {e}")
            return False
    
    async def create_automation_rule(self, 
                                   user_id: str,
                                   rule_data: Dict[str, Any]) -> AutomationRule:
        """Create a new automation rule"""
        
        automation_rule = AutomationRule(
            user_id=user_id,
            rule_name=rule_data["rule_name"],
            description=rule_data.get("description", ""),
            trigger_type=AutomationTrigger(rule_data["trigger_type"]),
            trigger_conditions=rule_data.get("trigger_conditions", {}),
            action_type=ActionType(rule_data["action_type"]),
            action_parameters=rule_data.get("action_parameters", {}),
            applies_to_content_types=rule_data.get("applies_to_content_types", []),
            applies_to_platforms=rule_data.get("applies_to_platforms", [])
        )
        
        # Store automation rule
        rule_dict = automation_rule.dict()
        rule_dict["created_at"] = automation_rule.created_at.isoformat()
        
        if automation_rule.updated_at:
            rule_dict["updated_at"] = automation_rule.updated_at.isoformat()
        if automation_rule.last_executed:
            rule_dict["last_executed"] = automation_rule.last_executed.isoformat()
        if automation_rule.next_execution:
            rule_dict["next_execution"] = automation_rule.next_execution.isoformat()
        
        result = self.automation_rules_collection.insert_one(rule_dict)
        automation_rule.rule_id = str(result.inserted_id)
        
        # Update the rule document with the rule_id
        self.automation_rules_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"rule_id": automation_rule.rule_id}}
        )
        
        return automation_rule
    
    async def get_content_lifecycle(self, content_id: str, user_id: str) -> Optional[ContentLifecycle]:
        """Get content lifecycle"""
        
        try:
            lifecycle_data = self.lifecycles_collection.find_one({
                "content_id": content_id,
                "user_id": user_id
            })
            
            if lifecycle_data:
                lifecycle_data['_id'] = str(lifecycle_data['_id'])
                return ContentLifecycle(**lifecycle_data)
            
            return None
            
        except Exception as e:
            print(f"Error getting content lifecycle: {e}")
            return None
    
    async def get_content_version(self, version_id: str, user_id: str) -> Optional[ContentVersion]:
        """Get specific content version"""
        
        try:
            version_data = self.versions_collection.find_one({
                "version_id": version_id,
                "created_by": user_id
            })
            
            if version_data:
                version_data['_id'] = str(version_data['_id'])
                return ContentVersion(**version_data)
            
            return None
            
        except Exception as e:
            print(f"Error getting content version: {e}")
            return None
    
    async def get_user_content_lifecycles(self, user_id: str, 
                                        status_filter: Optional[ContentStatus] = None,
                                        stage_filter: Optional[LifecycleStage] = None,
                                        limit: int = 50,
                                        offset: int = 0) -> List[ContentLifecycle]:
        """Get all content lifecycles for a user"""
        
        try:
            query = {"user_id": user_id}
            
            if status_filter:
                query["current_status"] = status_filter.value
            
            if stage_filter:
                query["current_stage"] = stage_filter.value
            
            cursor = self.lifecycles_collection.find(query).sort("updated_at", -1).skip(offset).limit(limit)
            
            lifecycles = []
            for lifecycle_data in cursor:
                try:
                    lifecycle_data['_id'] = str(lifecycle_data['_id'])
                    lifecycles.append(ContentLifecycle(**lifecycle_data))
                except Exception as e:
                    print(f"Error parsing lifecycle data: {e}")
                    continue
            
            return lifecycles
            
        except Exception as e:
            print(f"Error getting user content lifecycles: {e}")
            return []
    
    async def _apply_lifecycle_policy(self, lifecycle: ContentLifecycle, policy_name: str):
        """Apply a lifecycle policy to content"""
        
        if policy_name in self.default_policies:
            policy = self.default_policies[policy_name]
            
            # Set performance thresholds based on policy
            stage_rules = policy.get("stage_rules", {})
            
            if LifecycleStage.ACTIVE.value in stage_rules:
                active_rules = stage_rules[LifecycleStage.ACTIVE.value]
                
                # Set auto-archive threshold
                if "auto_archive_threshold" in active_rules:
                    threshold = active_rules["auto_archive_threshold"]
                    lifecycle.performance_thresholds.update(threshold)
                
                # Set performance review interval
                if "performance_review_interval_days" in active_rules:
                    days = active_rules["performance_review_interval_days"]
                    lifecycle.archive_after = datetime.now(timezone.utc) + timedelta(days=days * 3)
    
    async def _update_lifecycle_current_version(self, content_id: str, user_id: str, version_id: str):
        """Update the current version in lifecycle"""
        
        self.lifecycles_collection.update_one(
            {"content_id": content_id, "user_id": user_id},
            {
                "$set": {
                    "current_version_id": version_id,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"version_history": version_id}
            }
        )
    
    async def _trigger_stage_automations(self, content_id: str, user_id: str, stage: LifecycleStage):
        """Trigger automations based on stage transition"""
        
        # Get applicable automation rules
        rules_cursor = self.automation_rules_collection.find({
            "user_id": user_id,
            "is_active": True,
            "trigger_type": AutomationTrigger.USER_ACTION.value
        })
        
        for rule_data in rules_cursor:
            try:
                rule = AutomationRule(**rule_data)
                
                # Check if rule applies to this stage transition
                if rule.trigger_conditions.get("stage") == stage.value:
                    await self._execute_automation_rule(rule, content_id, user_id)
                    
            except Exception as e:
                print(f"Error executing stage automation: {e}")
    
    async def _trigger_status_automations(self, content_id: str, user_id: str, status: ContentStatus):
        """Trigger automations based on status change"""
        
        # Get applicable automation rules
        rules_cursor = self.automation_rules_collection.find({
            "user_id": user_id,
            "is_active": True,
            "trigger_type": AutomationTrigger.USER_ACTION.value
        })
        
        for rule_data in rules_cursor:
            try:
                rule = AutomationRule(**rule_data)
                
                # Check if rule applies to this status change
                if rule.trigger_conditions.get("status") == status.value:
                    await self._execute_automation_rule(rule, content_id, user_id)
                    
            except Exception as e:
                print(f"Error executing status automation: {e}")
    
    async def _execute_automation_rule(self, rule: AutomationRule, content_id: str, user_id: str):
        """Execute an automation rule"""
        
        try:
            action_executed = False
            
            if rule.action_type == ActionType.SEND_NOTIFICATION:
                # Send notification (would integrate with notification service)
                print(f"Notification: {rule.action_parameters.get('message', 'Content status updated')}")
                action_executed = True
                
            elif rule.action_type == ActionType.UPDATE_METADATA:
                # Update content metadata (would integrate with content service)
                print(f"Updating metadata for content {content_id}")
                action_executed = True
                
            elif rule.action_type == ActionType.ARCHIVE_CONTENT:
                # Archive content
                await self.update_content_status(content_id, user_id, ContentStatus.ARCHIVED, "Auto-archived by rule")
                action_executed = True
                
            elif rule.action_type == ActionType.PROMOTE_CONTENT:
                # Promote content (would integrate with marketing service)
                print(f"Promoting content {content_id}")
                action_executed = True
            
            # Update rule execution tracking
            if action_executed:
                self.automation_rules_collection.update_one(
                    {"rule_id": rule.rule_id, "user_id": user_id},
                    {
                        "$inc": {"execution_count": 1},
                        "$set": {"last_executed": datetime.now(timezone.utc).isoformat()}
                    }
                )
            
        except Exception as e:
            print(f"Error executing automation rule {rule.rule_id}: {e}")
    
    def _run_automation_checks(self):
        """Run periodic automation checks"""
        asyncio.create_task(self._check_performance_based_automations())
        asyncio.create_task(self._check_time_based_automations())
    
    async def _check_performance_based_automations(self):
        """Check for performance-based automation triggers"""
        
        try:
            # Get all active content lifecycles
            cursor = self.lifecycles_collection.find({
                "current_status": {"$in": [ContentStatus.LIVE.value, ContentStatus.PUBLISHED.value]}
            })
            
            for lifecycle_data in cursor:
                try:
                    lifecycle = ContentLifecycle(**lifecycle_data)
                    
                    # Check performance thresholds
                    if lifecycle.performance_thresholds:
                        # This would integrate with analytics service to check actual performance
                        # For now, simulate performance check
                        needs_action = await self._evaluate_performance_thresholds(lifecycle)
                        
                        if needs_action:
                            await self._trigger_performance_automations(lifecycle)
                            
                except Exception as e:
                    print(f"Error checking performance automation: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in performance automation check: {e}")
    
    async def _check_time_based_automations(self):
        """Check for time-based automation triggers"""
        
        try:
            now = datetime.now(timezone.utc)
            
            # Check for expired content
            cursor = self.lifecycles_collection.find({
                "expires_at": {"$lte": now.isoformat()},
                "current_status": {"$ne": ContentStatus.EXPIRED.value}
            })
            
            for lifecycle_data in cursor:
                try:
                    lifecycle = ContentLifecycle(**lifecycle_data)
                    await self.update_content_status(
                        lifecycle.content_id, 
                        lifecycle.user_id, 
                        ContentStatus.EXPIRED,
                        "Auto-expired by system"
                    )
                except Exception as e:
                    print(f"Error expiring content: {e}")
            
            # Check for content to archive
            cursor = self.lifecycles_collection.find({
                "archive_after": {"$lte": now.isoformat()},
                "current_status": {"$nin": [ContentStatus.ARCHIVED.value, ContentStatus.EXPIRED.value]}
            })
            
            for lifecycle_data in cursor:
                try:
                    lifecycle = ContentLifecycle(**lifecycle_data)
                    await self.update_content_status(
                        lifecycle.content_id,
                        lifecycle.user_id,
                        ContentStatus.ARCHIVED,
                        "Auto-archived by system"
                    )
                except Exception as e:
                    print(f"Error archiving content: {e}")
                    
        except Exception as e:
            print(f"Error in time-based automation check: {e}")
    
    async def _evaluate_performance_thresholds(self, lifecycle: ContentLifecycle) -> bool:
        """Evaluate if content performance meets thresholds"""
        
        # This would integrate with analytics service to get actual performance data
        # For now, return a simulated result
        
        if "views" in lifecycle.performance_thresholds:
            min_views = lifecycle.performance_thresholds["views"]
            # Simulated check - in reality, would call analytics service
            if min_views > 1000:  # Simulate underperforming content
                return True
        
        return False
    
    async def _trigger_performance_automations(self, lifecycle: ContentLifecycle):
        """Trigger automations based on performance"""
        
        # Get performance-based automation rules for this user
        rules_cursor = self.automation_rules_collection.find({
            "user_id": lifecycle.user_id,
            "is_active": True,
            "trigger_type": AutomationTrigger.PERFORMANCE_BASED.value
        })
        
        for rule_data in rules_cursor:
            try:
                rule = AutomationRule(**rule_data)
                await self._execute_automation_rule(rule, lifecycle.content_id, lifecycle.user_id)
            except Exception as e:
                print(f"Error executing performance automation: {e}")
    
    def _run_lifecycle_maintenance(self):
        """Run daily lifecycle maintenance tasks"""
        asyncio.create_task(self._cleanup_old_versions())
        asyncio.create_task(self._update_lifecycle_analytics())
    
    async def _cleanup_old_versions(self):
        """Clean up old content versions"""
        
        try:
            # Keep only last 10 versions per content
            pipeline = [
                {"$group": {
                    "_id": "$content_id",
                    "versions": {"$push": {
                        "version_id": "$version_id",
                        "created_at": "$created_at",
                        "is_current": "$is_current"
                    }}
                }}
            ]
            
            cursor = self.versions_collection.aggregate(pipeline)
            
            for content_group in cursor:
                versions = content_group["versions"]
                
                # Sort by creation date, keep current version and last 9 others
                current_versions = [v for v in versions if v.get("is_current")]
                other_versions = [v for v in versions if not v.get("is_current")]
                other_versions.sort(key=lambda x: x["created_at"], reverse=True)
                
                # Keep current + 9 most recent
                versions_to_keep = current_versions + other_versions[:9]
                versions_to_delete = other_versions[9:]
                
                # Delete old versions
                for version in versions_to_delete:
                    self.versions_collection.delete_one({"version_id": version["version_id"]})
                    
        except Exception as e:
            print(f"Error in version cleanup: {e}")
    
    async def _update_lifecycle_analytics(self):
        """Update lifecycle analytics and insights"""
        
        try:
            # This would calculate lifecycle performance metrics
            # For now, just update last performance check timestamps
            
            now = datetime.now(timezone.utc)
            
            self.lifecycles_collection.update_many(
                {"last_performance_check": {"$lt": (now - timedelta(days=1)).isoformat()}},
                {"$set": {"last_performance_check": now.isoformat()}}
            )
            
        except Exception as e:
            print(f"Error updating lifecycle analytics: {e}")
    
    async def get_lifecycle_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get lifecycle management dashboard data"""
        
        try:
            # Get lifecycle summary
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$current_status",
                    "count": {"$sum": 1}
                }}
            ]
            
            status_counts = {}
            cursor = self.lifecycles_collection.aggregate(pipeline)
            
            for result in cursor:
                status_counts[result["_id"]] = result["count"]
            
            # Get stage distribution
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$current_stage",
                    "count": {"$sum": 1}
                }}
            ]
            
            stage_counts = {}
            cursor = self.lifecycles_collection.aggregate(pipeline)
            
            for result in cursor:
                stage_counts[result["_id"]] = result["count"]
            
            # Get recent activity
            recent_lifecycles = await self.get_user_content_lifecycles(user_id, limit=10)
            
            # Get automation summary
            automation_cursor = self.automation_rules_collection.find({"user_id": user_id})
            automation_rules = list(automation_cursor)
            
            dashboard = {
                "user_id": user_id,
                "total_content_pieces": sum(status_counts.values()),
                "status_distribution": status_counts,
                "stage_distribution": stage_counts,
                "active_automations": len([r for r in automation_rules if r.get("is_active", True)]),
                "recent_activity": [
                    {
                        "content_id": lc.content_id,
                        "current_status": lc.current_status,
                        "current_stage": lc.current_stage,
                        "last_updated": lc.updated_at.isoformat() if isinstance(lc.updated_at, datetime) else lc.updated_at
                    }
                    for lc in recent_lifecycles[:5]
                ],
                "automation_summary": {
                    "total_rules": len(automation_rules),
                    "active_rules": len([r for r in automation_rules if r.get("is_active", True)]),
                    "total_executions": sum(r.get("execution_count", 0) for r in automation_rules)
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            print(f"Error getting lifecycle dashboard: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }