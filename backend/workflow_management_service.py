"""
Workflow Management Service - Phase 4: Complete Workflow Management
Implements the 10-phase content management system with scheduling, approval, and monitoring.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
import asyncio
from pydantic import BaseModel, Field
import uuid

class WorkflowPhase(str, Enum):
    AUDIENCE_MAPPING = "audience_mapping"
    CONTENT_PLANNING = "content_planning" 
    ASSET_CREATION = "asset_creation"
    APPROVAL_WORKFLOW = "approval_workflow"
    SCHEDULING = "scheduling"
    ENGAGEMENT = "engagement"
    MONITORING = "monitoring"
    REPORTING = "reporting"
    OPTIMIZATION = "optimization"
    REPURPOSING = "repurposing"

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

class ApprovalType(str, Enum):
    LEGAL = "legal"
    BRAND = "brand"
    PARTNER = "partner"
    TECHNICAL = "technical"
    CREATIVE = "creative"

class ContentAsset(BaseModel):
    asset_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: str  # video, audio, image, copy, thumbnail
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    content: Optional[str] = None  # For text content
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    version: int = 1
    is_active: bool = True

class ApprovalTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    approval_type: ApprovalType
    assigned_to: str
    title: str
    description: str
    content_id: str
    due_date: datetime
    status: WorkflowStatus = WorkflowStatus.PENDING
    comments: List[Dict[str, Any]] = []
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScheduledPost(BaseModel):
    post_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    platform_id: str
    scheduled_time: datetime
    content_variation: Dict[str, Any]
    status: WorkflowStatus = WorkflowStatus.PENDING
    posted_at: Optional[datetime] = None
    platform_post_id: Optional[str] = None
    performance_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EngagementTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform_id: str
    post_id: str
    task_type: str  # respond_comments, reply_dms, monitor_mentions
    priority: str = "medium"  # low, medium, high, urgent
    assigned_to: Optional[str] = None
    due_date: datetime
    status: WorkflowStatus = WorkflowStatus.PENDING
    engagement_data: Dict[str, Any] = {}
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkflowProject(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    objective: str
    target_platforms: List[str]
    content_calendar: Dict[str, Any] = {}
    current_phase: WorkflowPhase = WorkflowPhase.AUDIENCE_MAPPING
    phases_completed: List[WorkflowPhase] = []
    assets: List[ContentAsset] = []
    approval_tasks: List[ApprovalTask] = []
    scheduled_posts: List[ScheduledPost] = []
    engagement_tasks: List[EngagementTask] = []
    team_members: List[Dict[str, str]] = []
    budget: float = 0.0
    budget_spent: float = 0.0
    timeline: Dict[str, datetime] = {}
    performance_metrics: Dict[str, Any] = {}
    status: WorkflowStatus = WorkflowStatus.IN_PROGRESS
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkflowTemplate(BaseModel):
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str  # music_release, product_launch, brand_campaign, etc.
    phases_config: Dict[WorkflowPhase, Dict[str, Any]]
    default_timeline: Dict[str, int]  # Phase duration in days
    required_approvals: List[ApprovalType]
    recommended_platforms: List[str]
    budget_template: Dict[str, float]
    is_active: bool = True

class WorkflowManagementService:
    def __init__(self):
        self.workflow_templates = self._initialize_workflow_templates()
        self.phase_handlers = self._initialize_phase_handlers()
        
    def _initialize_workflow_templates(self) -> Dict[str, WorkflowTemplate]:
        """Initialize predefined workflow templates"""
        return {
            "music_release": WorkflowTemplate(
                name="Music Release Campaign",
                description="Complete workflow for music release from planning to post-release optimization",
                category="music",
                phases_config={
                    WorkflowPhase.AUDIENCE_MAPPING: {
                        "tasks": ["Define target demographics", "Analyze streaming data", "Map fan locations"],
                        "deliverables": ["Audience persona document", "Platform preference analysis"],
                        "tools": ["Spotify for Artists", "Apple Music Analytics", "Social media insights"]
                    },
                    WorkflowPhase.CONTENT_PLANNING: {
                        "tasks": ["Create content calendar", "Plan release sequence", "Design promotional timeline"],
                        "deliverables": ["Content calendar", "Release schedule", "Platform-specific content plan"],
                        "tools": ["Notion", "Airtable", "Google Calendar"]
                    },
                    WorkflowPhase.ASSET_CREATION: {
                        "tasks": ["Record/produce audio", "Create cover art", "Design promotional graphics", "Film music video"],
                        "deliverables": ["Master audio files", "Album artwork", "Promotional materials", "Video content"],
                        "tools": ["Logic Pro", "Photoshop", "Premiere Pro", "Canva"]
                    },
                    WorkflowPhase.APPROVAL_WORKFLOW: {
                        "tasks": ["Legal clearance", "Label approval", "Rights verification"],
                        "deliverables": ["Legal clearance certificate", "Approval documentation"],
                        "required_approvals": [ApprovalType.LEGAL, ApprovalType.PARTNER]
                    },
                    WorkflowPhase.SCHEDULING: {
                        "tasks": ["Schedule release", "Plan promotional posts", "Coordinate platform releases"],
                        "deliverables": ["Release schedule", "Promotional timeline"],
                        "tools": ["DistroKid", "Buffer", "Hootsuite"]
                    }
                },
                default_timeline={
                    "audience_mapping": 3,
                    "content_planning": 5,
                    "asset_creation": 14,
                    "approval_workflow": 3,
                    "scheduling": 2,
                    "engagement": 30,
                    "monitoring": 30,
                    "reporting": 2,
                    "optimization": 7,
                    "repurposing": 7
                },
                required_approvals=[ApprovalType.LEGAL, ApprovalType.PARTNER],
                recommended_platforms=["spotify", "apple_music", "youtube", "instagram", "tiktok"],
                budget_template={
                    "production": 5000.0,
                    "marketing": 2000.0,
                    "distribution": 500.0,
                    "advertising": 1500.0
                }
            ),
            
            "product_launch": WorkflowTemplate(
                name="Product Launch Campaign",
                description="Comprehensive product launch workflow from concept to post-launch analysis",
                category="business",
                phases_config={
                    WorkflowPhase.AUDIENCE_MAPPING: {
                        "tasks": ["Define target market", "Analyze competitor audience", "Create user personas"],
                        "deliverables": ["Market research report", "User persona profiles"],
                        "tools": ["Google Analytics", "Facebook Audience Insights", "SurveyMonkey"]
                    },
                    WorkflowPhase.CONTENT_PLANNING: {
                        "tasks": ["Develop messaging strategy", "Plan content themes", "Create editorial calendar"],
                        "deliverables": ["Messaging framework", "Content strategy document", "Editorial calendar"],
                        "tools": ["Miro", "Trello", "CoSchedule"]
                    },
                    WorkflowPhase.ASSET_CREATION: {
                        "tasks": ["Product photography", "Video production", "Copy writing", "Design graphics"],
                        "deliverables": ["Product images", "Promotional videos", "Marketing copy", "Brand assets"],
                        "tools": ["Lightroom", "Final Cut Pro", "Grammarly", "Figma"]
                    }
                },
                default_timeline={
                    "audience_mapping": 5,
                    "content_planning": 7,
                    "asset_creation": 21,
                    "approval_workflow": 5,
                    "scheduling": 3,
                    "engagement": 60,
                    "monitoring": 60,
                    "reporting": 5,
                    "optimization": 14,
                    "repurposing": 14
                },
                required_approvals=[ApprovalType.LEGAL, ApprovalType.BRAND, ApprovalType.TECHNICAL],
                recommended_platforms=["instagram", "facebook", "linkedin", "youtube", "twitter"],
                budget_template={
                    "content_creation": 8000.0,
                    "advertising": 5000.0,
                    "influencer_partnerships": 3000.0,
                    "tools_software": 1000.0
                }
            ),
            
            "brand_awareness": WorkflowTemplate(
                name="Brand Awareness Campaign",
                description="Build brand recognition and reach through multi-channel content strategy",
                category="branding",
                phases_config={
                    WorkflowPhase.AUDIENCE_MAPPING: {
                        "tasks": ["Brand perception survey", "Audience segmentation", "Competitor analysis"],
                        "deliverables": ["Brand awareness baseline", "Audience segments", "Competitive landscape"],
                        "tools": ["Brandwatch", "Mention", "SEMrush"]
                    },
                    WorkflowPhase.CONTENT_PLANNING: {
                        "tasks": ["Brand storytelling strategy", "Content pillar development", "Cross-channel planning"],
                        "deliverables": ["Brand story framework", "Content pillars", "Channel strategy"],
                        "tools": ["StoryBrand", "ContentCal", "Sprout Social"]
                    }
                },
                default_timeline={
                    "audience_mapping": 7,
                    "content_planning": 10,
                    "asset_creation": 28,
                    "approval_workflow": 5,
                    "scheduling": 3,
                    "engagement": 90,
                    "monitoring": 90,
                    "reporting": 7,
                    "optimization": 21,
                    "repurposing": 21
                },
                required_approvals=[ApprovalType.BRAND, ApprovalType.CREATIVE],
                recommended_platforms=["instagram", "tiktok", "youtube", "facebook", "linkedin"],
                budget_template={
                    "creative_development": 10000.0,
                    "paid_advertising": 8000.0,
                    "influencer_collaborations": 5000.0,
                    "production_costs": 7000.0
                }
            )
        }
    
    def _initialize_phase_handlers(self) -> Dict[WorkflowPhase, callable]:
        """Initialize handlers for each workflow phase"""
        return {
            WorkflowPhase.AUDIENCE_MAPPING: self._handle_audience_mapping,
            WorkflowPhase.CONTENT_PLANNING: self._handle_content_planning,
            WorkflowPhase.ASSET_CREATION: self._handle_asset_creation,
            WorkflowPhase.APPROVAL_WORKFLOW: self._handle_approval_workflow,
            WorkflowPhase.SCHEDULING: self._handle_scheduling,
            WorkflowPhase.ENGAGEMENT: self._handle_engagement,
            WorkflowPhase.MONITORING: self._handle_monitoring,
            WorkflowPhase.REPORTING: self._handle_reporting,
            WorkflowPhase.OPTIMIZATION: self._handle_optimization,
            WorkflowPhase.REPURPOSING: self._handle_repurposing
        }
    
    async def create_workflow_project(self, 
                                    user_id: str,
                                    title: str,
                                    description: str,
                                    objective: str,
                                    target_platforms: List[str],
                                    template_id: Optional[str] = None,
                                    budget: Optional[float] = None) -> WorkflowProject:
        """Create a new workflow project"""
        
        project = WorkflowProject(
            user_id=user_id,
            title=title,
            description=description,
            objective=objective,
            target_platforms=target_platforms,
            budget=budget or 0.0
        )
        
        # Apply template if specified
        if template_id and template_id in self.workflow_templates:
            template = self.workflow_templates[template_id]
            
            # Set timeline based on template
            start_date = datetime.now(timezone.utc)
            for phase_name, duration_days in template.default_timeline.items():
                if hasattr(WorkflowPhase, phase_name.upper()):
                    phase = getattr(WorkflowPhase, phase_name.upper())
                    project.timeline[phase.value] = start_date + timedelta(days=duration_days)
                    start_date = project.timeline[phase.value]
            
            # Create approval tasks based on template
            for approval_type in template.required_approvals:
                approval_task = ApprovalTask(
                    approval_type=approval_type,
                    assigned_to="admin",  # This would be dynamic in real implementation
                    title=f"{approval_type.value.title()} Approval Required",
                    description=f"Review and approve content for {approval_type.value} compliance",
                    content_id=project.project_id,
                    due_date=project.timeline.get(WorkflowPhase.APPROVAL_WORKFLOW.value, start_date)
                )
                project.approval_tasks.append(approval_task)
            
            # Set budget allocation based on template
            if template.budget_template and not budget:
                project.budget = sum(template.budget_template.values())
        
        return project
    
    async def advance_project_phase(self, project: WorkflowProject) -> Dict[str, Any]:
        """Advance project to the next phase"""
        
        current_phase = project.current_phase
        
        # Check if current phase is complete
        phase_complete = await self._is_phase_complete(project, current_phase)
        if not phase_complete:
            return {
                "success": False,
                "message": f"Cannot advance: {current_phase.value} phase is not complete",
                "blocking_tasks": await self._get_blocking_tasks(project, current_phase)
            }
        
        # Mark current phase as completed
        if current_phase not in project.phases_completed:
            project.phases_completed.append(current_phase)
        
        # Determine next phase
        phase_order = list(WorkflowPhase)
        current_index = phase_order.index(current_phase)
        
        if current_index < len(phase_order) - 1:
            next_phase = phase_order[current_index + 1]
            project.current_phase = next_phase
            
            # Initialize next phase
            await self._initialize_phase(project, next_phase)
            
            project.updated_at = datetime.now(timezone.utc)
            
            return {
                "success": True,
                "message": f"Advanced to {next_phase.value} phase",
                "current_phase": next_phase.value,
                "completion_percentage": ((current_index + 1) / len(phase_order)) * 100
            }
        else:
            # Project completed
            project.status = WorkflowStatus.COMPLETED
            project.updated_at = datetime.now(timezone.utc)
            
            return {
                "success": True,
                "message": "Project completed successfully!",
                "current_phase": "completed",
                "completion_percentage": 100
            }
    
    async def _is_phase_complete(self, project: WorkflowProject, phase: WorkflowPhase) -> bool:
        """Check if a phase is complete"""
        
        phase_handler = self.phase_handlers.get(phase)
        if phase_handler:
            return await phase_handler(project, "check_completion")
        
        # Default completion check
        return True
    
    async def _get_blocking_tasks(self, project: WorkflowProject, phase: WorkflowPhase) -> List[str]:
        """Get list of tasks blocking phase completion"""
        
        blocking_tasks = []
        
        if phase == WorkflowPhase.APPROVAL_WORKFLOW:
            for approval_task in project.approval_tasks:
                if approval_task.status not in [WorkflowStatus.APPROVED, WorkflowStatus.COMPLETED]:
                    blocking_tasks.append(f"Pending {approval_task.approval_type.value} approval")
        
        elif phase == WorkflowPhase.ASSET_CREATION:
            required_assets = ["audio", "video", "image", "copy"]
            existing_types = {asset.asset_type for asset in project.assets if asset.is_active}
            
            for asset_type in required_assets:
                if asset_type not in existing_types:
                    blocking_tasks.append(f"Missing {asset_type} asset")
        
        elif phase == WorkflowPhase.SCHEDULING:
            if not project.scheduled_posts:
                blocking_tasks.append("No posts scheduled")
        
        return blocking_tasks
    
    async def _initialize_phase(self, project: WorkflowProject, phase: WorkflowPhase):
        """Initialize a new phase with required tasks and setup"""
        
        phase_handler = self.phase_handlers.get(phase)
        if phase_handler:
            await phase_handler(project, "initialize")
    
    # Phase Handlers
    async def _handle_audience_mapping(self, project: WorkflowProject, action: str) -> Any:
        """Handle audience mapping phase"""
        
        if action == "initialize":
            # Create audience mapping tasks
            project.content_calendar["audience_research"] = {
                "demographics_analysis": {"status": "pending", "due_date": datetime.now(timezone.utc) + timedelta(days=2)},
                "platform_preferences": {"status": "pending", "due_date": datetime.now(timezone.utc) + timedelta(days=2)},
                "competitor_analysis": {"status": "pending", "due_date": datetime.now(timezone.utc) + timedelta(days=3)}
            }
            
        elif action == "check_completion":
            # Check if audience research is complete
            audience_research = project.content_calendar.get("audience_research", {})
            completed_tasks = sum(1 for task in audience_research.values() if task.get("status") == "completed")
            total_tasks = len(audience_research)
            
            return completed_tasks == total_tasks and total_tasks > 0
        
        return True
    
    async def _handle_content_planning(self, project: WorkflowProject, action: str) -> Any:
        """Handle content planning phase"""
        
        if action == "initialize":
            # Create content planning framework
            project.content_calendar["content_strategy"] = {
                "content_themes": {"status": "pending", "themes": []},
                "posting_schedule": {"status": "pending", "schedule": {}},
                "platform_specific_plans": {"status": "pending", "plans": {}}
            }
            
            # Generate platform-specific content plans
            for platform in project.target_platforms:
                project.content_calendar["content_strategy"]["platform_specific_plans"]["plans"][platform] = {
                    "content_types": [],
                    "posting_frequency": "daily",
                    "optimal_times": [],
                    "hashtag_strategy": []
                }
                
        elif action == "check_completion":
            content_strategy = project.content_calendar.get("content_strategy", {})
            return (content_strategy.get("content_themes", {}).get("status") == "completed" and
                   content_strategy.get("posting_schedule", {}).get("status") == "completed")
        
        return True
    
    async def _handle_asset_creation(self, project: WorkflowProject, action: str) -> Any:
        """Handle asset creation phase"""
        
        if action == "initialize":
            # Create asset creation checklist
            required_assets = ["video", "audio", "image", "copy"]
            for asset_type in required_assets:
                # This would create asset creation tasks
                pass
                
        elif action == "check_completion":
            # Check if minimum required assets are created
            asset_types = {asset.asset_type for asset in project.assets if asset.is_active}
            required_types = {"video", "image", "copy"}  # Minimum required
            
            return required_types.issubset(asset_types)
        
        return True
    
    async def _handle_approval_workflow(self, project: WorkflowProject, action: str) -> Any:
        """Handle approval workflow phase"""
        
        if action == "initialize":
            # Set up approval notifications and reminders
            for approval_task in project.approval_tasks:
                if approval_task.status == WorkflowStatus.PENDING:
                    # Send notification to assigned approver
                    await self._send_approval_notification(approval_task)
                    
        elif action == "check_completion":
            # Check if all approval tasks are completed
            pending_approvals = [task for task in project.approval_tasks 
                               if task.status not in [WorkflowStatus.APPROVED, WorkflowStatus.COMPLETED]]
            
            return len(pending_approvals) == 0
        
        return True
    
    async def _handle_scheduling(self, project: WorkflowProject, action: str) -> Any:
        """Handle scheduling phase"""
        
        if action == "initialize":
            # Create scheduled posts based on content calendar
            posting_schedule = project.content_calendar.get("content_strategy", {}).get("posting_schedule", {}).get("schedule", {})
            
            for platform in project.target_platforms:
                # Create scheduled posts for each platform
                scheduled_post = ScheduledPost(
                    content_id=project.project_id,
                    platform_id=platform,
                    scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
                    content_variation={
                        "title": f"{project.title} - {platform}",
                        "description": project.description,
                        "hashtags": [f"#{project.title.replace(' ', '')}", "#BigMannEntertainment"]
                    }
                )
                project.scheduled_posts.append(scheduled_post)
                
        elif action == "check_completion":
            # Check if posts are scheduled for all target platforms
            scheduled_platforms = {post.platform_id for post in project.scheduled_posts}
            target_platforms = set(project.target_platforms)
            
            return target_platforms.issubset(scheduled_platforms)
        
        return True
    
    async def _handle_engagement(self, project: WorkflowProject, action: str) -> Any:
        """Handle engagement phase"""
        
        if action == "initialize":
            # Create engagement monitoring tasks
            for platform in project.target_platforms:
                engagement_task = EngagementTask(
                    platform_id=platform,
                    post_id="",  # Would be filled when posts are published
                    task_type="monitor_engagement",
                    due_date=datetime.now(timezone.utc) + timedelta(days=7),
                    assigned_to="community_manager"
                )
                project.engagement_tasks.append(engagement_task)
                
        elif action == "check_completion":
            # Engagement phase is ongoing, completed when monitoring period ends
            oldest_task = min(project.engagement_tasks, 
                            key=lambda x: x.created_at, 
                            default=None)
            
            if oldest_task:
                monitoring_duration = datetime.now(timezone.utc) - oldest_task.created_at
                return monitoring_duration.days >= 7  # 7 days of monitoring
            
            return True
        
        return True
    
    async def _handle_monitoring(self, project: WorkflowProject, action: str) -> Any:
        """Handle monitoring phase"""
        
        if action == "initialize":
            # Set up performance monitoring
            project.performance_metrics = {
                "tracking_started": datetime.now(timezone.utc),
                "platforms": {platform: {"metrics_collected": False} for platform in project.target_platforms},
                "overall_performance": {"reach": 0, "engagement": 0, "conversions": 0}
            }
            
        elif action == "check_completion":
            # Check if sufficient monitoring data is collected
            tracking_started = project.performance_metrics.get("tracking_started")
            if tracking_started:
                monitoring_duration = datetime.now(timezone.utc) - tracking_started
                return monitoring_duration.days >= 14  # 14 days of monitoring
            
            return False
        
        return True
    
    async def _handle_reporting(self, project: WorkflowProject, action: str) -> Any:
        """Handle reporting phase"""
        
        if action == "initialize":
            # Generate comprehensive performance report
            report_data = await self._generate_project_report(project)
            project.performance_metrics["final_report"] = report_data
            
        elif action == "check_completion":
            # Check if report is generated
            return "final_report" in project.performance_metrics
        
        return True
    
    async def _handle_optimization(self, project: WorkflowProject, action: str) -> Any:
        """Handle optimization phase"""
        
        if action == "initialize":
            # Analyze performance and create optimization recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(project)
            project.performance_metrics["optimizations"] = optimization_recommendations
            
        elif action == "check_completion":
            # Check if optimization recommendations are implemented
            optimizations = project.performance_metrics.get("optimizations", {})
            return optimizations.get("recommendations_implemented", False)
        
        return True
    
    async def _handle_repurposing(self, project: WorkflowProject, action: str) -> Any:
        """Handle repurposing phase"""
        
        if action == "initialize":
            # Identify content for repurposing
            repurposing_plan = await self._create_repurposing_plan(project)
            project.content_calendar["repurposing"] = repurposing_plan
            
        elif action == "check_completion":
            # Check if repurposed content is created
            repurposing_plan = project.content_calendar.get("repurposing", {})
            return repurposing_plan.get("execution_completed", False)
        
        return True
    
    async def _send_approval_notification(self, approval_task: ApprovalTask):
        """Send approval notification to assigned person"""
        # This would integrate with email/notification system
        notification = {
            "type": "approval_request",
            "task_id": approval_task.task_id,
            "title": approval_task.title,
            "assigned_to": approval_task.assigned_to,
            "due_date": approval_task.due_date,
            "approval_type": approval_task.approval_type.value
        }
        
        # Send notification (implementation would go here)
        print(f"Approval notification sent: {notification}")
    
    async def approve_task(self, task_id: str, approver_id: str, comments: Optional[str] = None) -> Dict[str, Any]:
        """Approve an approval task"""
        # This would find and update the approval task
        # For now, returning a success response
        
        return {
            "success": True,
            "task_id": task_id,
            "approved_by": approver_id,
            "approved_at": datetime.now(timezone.utc),
            "comments": comments
        }
    
    async def reject_task(self, task_id: str, approver_id: str, reason: str) -> Dict[str, Any]:
        """Reject an approval task"""
        
        return {
            "success": True,
            "task_id": task_id,
            "rejected_by": approver_id,
            "rejected_at": datetime.now(timezone.utc),
            "reason": reason,
            "status": WorkflowStatus.REJECTED.value
        }
    
    async def add_project_asset(self, project: WorkflowProject, asset: ContentAsset):
        """Add an asset to the project"""
        project.assets.append(asset)
        project.updated_at = datetime.now(timezone.utc)
    
    async def schedule_project_posts(self, project: WorkflowProject) -> Dict[str, Any]:
        """Schedule all project posts across platforms"""
        scheduled_count = 0
        scheduling_results = {}
        
        for scheduled_post in project.scheduled_posts:
            if scheduled_post.status == WorkflowStatus.PENDING:
                # Here you would integrate with actual scheduling service
                scheduled_post.status = WorkflowStatus.APPROVED
                scheduled_count += 1
                
                scheduling_results[scheduled_post.platform_id] = {
                    "scheduled": True,
                    "scheduled_time": scheduled_post.scheduled_time,
                    "post_id": scheduled_post.post_id
                }
        
        return {
            "success": True,
            "scheduled_count": scheduled_count,
            "total_posts": len(project.scheduled_posts),
            "platform_results": scheduling_results
        }
    
    async def _generate_project_report(self, project: WorkflowProject) -> Dict[str, Any]:
        """Generate comprehensive project performance report"""
        
        report = {
            "project_summary": {
                "project_id": project.project_id,
                "title": project.title,
                "objective": project.objective,
                "duration_days": (datetime.now(timezone.utc) - project.created_at).days,
                "phases_completed": len(project.phases_completed),
                "total_phases": len(WorkflowPhase),
                "completion_percentage": (len(project.phases_completed) / len(WorkflowPhase)) * 100
            },
            "budget_analysis": {
                "allocated_budget": project.budget,
                "spent_budget": project.budget_spent,
                "remaining_budget": project.budget - project.budget_spent,
                "budget_utilization": (project.budget_spent / project.budget * 100) if project.budget > 0 else 0
            },
            "asset_summary": {
                "total_assets": len(project.assets),
                "assets_by_type": {},
                "active_assets": len([a for a in project.assets if a.is_active])
            },
            "platform_performance": {},
            "engagement_metrics": {
                "total_tasks": len(project.engagement_tasks),
                "completed_tasks": len([t for t in project.engagement_tasks if t.status == WorkflowStatus.COMPLETED]),
                "average_response_time": "2.3 hours"  # Would be calculated from actual data
            },
            "approval_workflow": {
                "total_approvals": len(project.approval_tasks),
                "approved": len([t for t in project.approval_tasks if t.status == WorkflowStatus.APPROVED]),
                "rejected": len([t for t in project.approval_tasks if t.status == WorkflowStatus.REJECTED]),
                "pending": len([t for t in project.approval_tasks if t.status == WorkflowStatus.PENDING])
            },
            "recommendations": []
        }
        
        # Calculate assets by type
        for asset in project.assets:
            asset_type = asset.asset_type
            report["asset_summary"]["assets_by_type"][asset_type] = \
                report["asset_summary"]["assets_by_type"].get(asset_type, 0) + 1
        
        # Generate platform performance (simulated data)
        for platform in project.target_platforms:
            report["platform_performance"][platform] = {
                "posts_published": len([p for p in project.scheduled_posts if p.platform_id == platform]),
                "total_reach": 5000 + hash(platform) % 10000,
                "engagement_rate": 2.5 + (hash(platform) % 50) / 10,
                "conversions": 10 + hash(platform) % 50
            }
        
        # Generate recommendations
        if report["budget_analysis"]["budget_utilization"] > 90:
            report["recommendations"].append("Budget nearly exhausted - consider additional funding for optimization")
        
        if report["approval_workflow"]["rejected"] > 0:
            report["recommendations"].append("Review approval process - some tasks were rejected")
        
        if len(project.phases_completed) < len(WorkflowPhase):
            report["recommendations"].append("Project not fully completed - continue with remaining phases")
        
        return report
    
    async def _generate_optimization_recommendations(self, project: WorkflowProject) -> Dict[str, Any]:
        """Generate optimization recommendations based on project performance"""
        
        recommendations = {
            "content_optimization": [],
            "platform_optimization": [],
            "timing_optimization": [],
            "budget_optimization": [],
            "engagement_optimization": [],
            "recommendations_implemented": False
        }
        
        # Analyze platform performance and generate recommendations
        performance_data = project.performance_metrics.get("final_report", {}).get("platform_performance", {})
        
        for platform, metrics in performance_data.items():
            engagement_rate = metrics.get("engagement_rate", 0)
            
            if engagement_rate < 2.0:
                recommendations["platform_optimization"].append(
                    f"Improve {platform} content - current engagement rate ({engagement_rate}%) is below optimal"
                )
                recommendations["content_optimization"].append(
                    f"Test different content formats for {platform} to increase engagement"
                )
            
            elif engagement_rate > 5.0:
                recommendations["budget_optimization"].append(
                    f"Increase budget allocation for {platform} - high engagement rate ({engagement_rate}%)"
                )
        
        # Content optimization recommendations
        asset_types = {asset.asset_type for asset in project.assets}
        if "video" not in asset_types:
            recommendations["content_optimization"].append("Add video content to improve engagement across platforms")
        
        if "audio" not in asset_types and any(p in ["spotify", "apple_music"] for p in project.target_platforms):
            recommendations["content_optimization"].append("Create audio content for music streaming platforms")
        
        # Timing optimization
        recommendations["timing_optimization"].extend([
            "Test different posting times to optimize reach",
            "Analyze audience activity patterns for better scheduling",
            "Consider time zone differences for global audience"
        ])
        
        # Engagement optimization
        recommendations["engagement_optimization"].extend([
            "Increase response rate to comments and messages",
            "Create more interactive content (polls, Q&A, live streams)",
            "Implement user-generated content campaigns"
        ])
        
        return recommendations
    
    async def _create_repurposing_plan(self, project: WorkflowProject) -> Dict[str, Any]:
        """Create plan for repurposing existing content"""
        
        repurposing_plan = {
            "high_performing_content": [],
            "repurposing_opportunities": [],
            "new_content_variations": [],
            "execution_timeline": {},
            "execution_completed": False
        }
        
        # Identify high-performing content based on engagement metrics
        platform_performance = project.performance_metrics.get("final_report", {}).get("platform_performance", {})
        
        for platform, metrics in platform_performance.items():
            if metrics.get("engagement_rate", 0) > 4.0:
                repurposing_plan["high_performing_content"].append({
                    "platform": platform,
                    "engagement_rate": metrics["engagement_rate"],
                    "reach": metrics["total_reach"]
                })
        
        # Generate repurposing opportunities
        existing_assets = {asset.asset_type for asset in project.assets if asset.is_active}
        
        if "video" in existing_assets:
            repurposing_plan["repurposing_opportunities"].extend([
                "Create short clips from long-form videos for TikTok and Instagram Reels",
                "Extract audio for podcast episodes",
                "Create quote graphics from video transcripts"
            ])
        
        if "audio" in existing_assets:
            repurposing_plan["repurposing_opportunities"].extend([
                "Create audiogram videos for social media",
                "Generate blog posts from audio transcripts",
                "Create quote cards from audio highlights"
            ])
        
        if "image" in existing_assets:
            repurposing_plan["repurposing_opportunities"].extend([
                "Create carousel posts from individual images",
                "Develop animated GIFs from image sequences",
                "Generate story highlights collections"
            ])
        
        # Create execution timeline
        base_date = datetime.now(timezone.utc)
        for i, opportunity in enumerate(repurposing_plan["repurposing_opportunities"]):
            repurposing_plan["execution_timeline"][f"task_{i+1}"] = {
                "description": opportunity,
                "due_date": base_date + timedelta(days=(i+1)*2),
                "status": "pending"
            }
        
        return repurposing_plan
    
    async def get_project_dashboard(self, project: WorkflowProject) -> Dict[str, Any]:
        """Get comprehensive project dashboard data"""
        
        dashboard = {
            "project_overview": {
                "id": project.project_id,
                "title": project.title,
                "current_phase": project.current_phase.value,
                "status": project.status.value,
                "completion_percentage": (len(project.phases_completed) / len(WorkflowPhase)) * 100,
                "days_active": (datetime.now(timezone.utc) - project.created_at).days
            },
            "phase_progress": {},
            "upcoming_deadlines": [],
            "recent_activity": [],
            "performance_highlights": {},
            "team_activity": {},
            "budget_status": {
                "allocated": project.budget,
                "spent": project.budget_spent,
                "remaining": project.budget - project.budget_spent,
                "utilization_percentage": (project.budget_spent / project.budget * 100) if project.budget > 0 else 0
            }
        }
        
        # Phase progress
        for phase in WorkflowPhase:
            dashboard["phase_progress"][phase.value] = {
                "completed": phase in project.phases_completed,
                "current": phase == project.current_phase,
                "estimated_completion": project.timeline.get(phase.value),
                "status": "completed" if phase in project.phases_completed else 
                         "in_progress" if phase == project.current_phase else "pending"
            }
        
        # Upcoming deadlines
        current_time = datetime.now(timezone.utc)
        
        # Add approval task deadlines
        for approval_task in project.approval_tasks:
            if approval_task.status == WorkflowStatus.PENDING and approval_task.due_date > current_time:
                dashboard["upcoming_deadlines"].append({
                    "type": "approval",
                    "title": approval_task.title,
                    "due_date": approval_task.due_date,
                    "priority": "high" if (approval_task.due_date - current_time).days <= 2 else "medium"
                })
        
        # Add scheduled post deadlines
        for scheduled_post in project.scheduled_posts:
            if scheduled_post.status == WorkflowStatus.PENDING and scheduled_post.scheduled_time > current_time:
                dashboard["upcoming_deadlines"].append({
                    "type": "scheduled_post",
                    "title": f"Post to {scheduled_post.platform_id}",
                    "due_date": scheduled_post.scheduled_time,
                    "priority": "medium"
                })
        
        # Sort deadlines by due date
        dashboard["upcoming_deadlines"].sort(key=lambda x: x["due_date"])
        
        # Recent activity (simulated)
        dashboard["recent_activity"] = [
            {
                "timestamp": current_time - timedelta(hours=2),
                "user": "System",
                "action": f"Advanced to {project.current_phase.value} phase",
                "type": "phase_transition"
            },
            {
                "timestamp": current_time - timedelta(hours=5),
                "user": "Content Creator",
                "action": f"Uploaded {len(project.assets)} assets",
                "type": "asset_upload"
            },
            {
                "timestamp": current_time - timedelta(hours=8),
                "user": "Project Manager",
                "action": "Updated project timeline",
                "type": "timeline_update"
            }
        ]
        
        # Performance highlights
        if project.performance_metrics:
            final_report = project.performance_metrics.get("final_report", {})
            platform_performance = final_report.get("platform_performance", {})
            
            if platform_performance:
                total_reach = sum(metrics.get("total_reach", 0) for metrics in platform_performance.values())
                avg_engagement = sum(metrics.get("engagement_rate", 0) for metrics in platform_performance.values()) / len(platform_performance)
                total_conversions = sum(metrics.get("conversions", 0) for metrics in platform_performance.values())
                
                dashboard["performance_highlights"] = {
                    "total_reach": total_reach,
                    "average_engagement_rate": round(avg_engagement, 2),
                    "total_conversions": total_conversions,
                    "best_performing_platform": max(platform_performance.items(), 
                                                  key=lambda x: x[1].get("engagement_rate", 0))[0] if platform_performance else None
                }
        
        return dashboard