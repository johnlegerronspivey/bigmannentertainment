"""
Modular Agency Workspaces
=========================
Each agency gets a customizable workspace with:
- Branding
- Custom dashboards
- Talent pipelines
- Internal notes
- Contract templates
- AI-generated casting suggestions

Think "Notion + Salesforce + Getty Images" for modeling.
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

from llm_service import LlmChat, UserMessage


class WorkspaceTheme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"


class PipelineStage(str, Enum):
    SCOUTING = "scouting"
    CONTACTED = "contacted"
    INTERVIEWING = "interviewing"
    CONTRACTED = "contracted"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class NoteVisibility(str, Enum):
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class TemplateType(str, Enum):
    MODEL_CONTRACT = "model_contract"
    BOOKING_AGREEMENT = "booking_agreement"
    NDA = "nda"
    RELEASE_FORM = "release_form"
    INVOICE = "invoice"
    PROPOSAL = "proposal"


# Pydantic Models
class AgencyBranding(BaseModel):
    agency_id: str
    logo_url: Optional[str] = None
    primary_color: str = "#6366f1"
    secondary_color: str = "#8b5cf6"
    accent_color: str = "#f59e0b"
    font_family: str = "Inter"
    tagline: Optional[str] = None
    custom_css: Optional[str] = None
    favicon_url: Optional[str] = None


class DashboardWidget(BaseModel):
    widget_id: str
    widget_type: str
    title: str
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0, "w": 4, "h": 3})
    config: Dict[str, Any] = Field(default_factory=dict)
    visible: bool = True


class CustomDashboard(BaseModel):
    dashboard_id: str
    agency_id: str
    name: str
    description: str = ""
    widgets: List[DashboardWidget] = Field(default_factory=list)
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TalentPipelineEntry(BaseModel):
    entry_id: str
    agency_id: str
    talent_id: str
    talent_name: str
    stage: PipelineStage
    source: str = ""
    assigned_to: Optional[str] = None
    rating: int = Field(default=0, ge=0, le=5)
    tags: List[str] = Field(default_factory=list)
    notes: str = ""
    last_contact: Optional[datetime] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TalentPipeline(BaseModel):
    pipeline_id: str
    agency_id: str
    name: str
    description: str = ""
    stages: List[PipelineStage] = Field(default_factory=lambda: list(PipelineStage))
    entries: List[TalentPipelineEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InternalNote(BaseModel):
    note_id: str
    agency_id: str
    entity_type: str
    entity_id: str
    author_id: str
    author_name: str
    content: str
    visibility: NoteVisibility = NoteVisibility.TEAM
    pinned: bool = False
    tags: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContractTemplate(BaseModel):
    template_id: str
    agency_id: str
    template_type: TemplateType
    name: str
    description: str = ""
    content: str
    variables: List[str] = Field(default_factory=list)
    is_default: bool = False
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CastingSuggestion(BaseModel):
    suggestion_id: str
    agency_id: str
    campaign_id: Optional[str] = None
    campaign_name: str
    suggested_talents: List[Dict[str, Any]] = Field(default_factory=list)
    match_criteria: Dict[str, Any] = Field(default_factory=dict)
    ai_reasoning: str = ""
    confidence_score: float = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgencyWorkspace(BaseModel):
    workspace_id: str
    agency_id: str
    agency_name: str
    branding: AgencyBranding
    dashboards: List[CustomDashboard] = Field(default_factory=list)
    pipelines: List[TalentPipeline] = Field(default_factory=list)
    templates: List[ContractTemplate] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModularAgencyWorkspaceService:
    """
    Service for managing modular agency workspaces.
    Provides Notion + Salesforce + Getty Images experience for modeling agencies.
    """
    
    def __init__(self, db):
        self.db = db
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_provider = "gemini"
        self.model_name = "gemini-2.5-flash"
    
    def _get_chat(self, session_id: str, system_message: str) -> LlmChat:
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        chat.with_model(self.model_provider, self.model_name)
        return chat
    
    async def create_workspace(self, agency_id: str, agency_name: str, branding: Dict[str, Any] = None) -> AgencyWorkspace:
        """
        Create a new agency workspace with default configuration.
        """
        import uuid
        
        workspace_id = str(uuid.uuid4())
        
        # Create default branding
        default_branding = AgencyBranding(
            agency_id=agency_id,
            **(branding or {})
        )
        
        # Create default dashboard
        default_dashboard = CustomDashboard(
            dashboard_id=str(uuid.uuid4()),
            agency_id=agency_id,
            name="Main Dashboard",
            description="Your agency's main dashboard",
            is_default=True,
            widgets=[
                DashboardWidget(
                    widget_id=str(uuid.uuid4()),
                    widget_type="stats_overview",
                    title="Overview",
                    position={"x": 0, "y": 0, "w": 12, "h": 2}
                ),
                DashboardWidget(
                    widget_id=str(uuid.uuid4()),
                    widget_type="talent_pipeline",
                    title="Talent Pipeline",
                    position={"x": 0, "y": 2, "w": 6, "h": 4}
                ),
                DashboardWidget(
                    widget_id=str(uuid.uuid4()),
                    widget_type="recent_bookings",
                    title="Recent Bookings",
                    position={"x": 6, "y": 2, "w": 6, "h": 4}
                ),
                DashboardWidget(
                    widget_id=str(uuid.uuid4()),
                    widget_type="ai_insights",
                    title="AI Insights",
                    position={"x": 0, "y": 6, "w": 4, "h": 3}
                ),
                DashboardWidget(
                    widget_id=str(uuid.uuid4()),
                    widget_type="casting_suggestions",
                    title="Casting Suggestions",
                    position={"x": 4, "y": 6, "w": 8, "h": 3}
                )
            ]
        )
        
        # Create default talent pipeline
        default_pipeline = TalentPipeline(
            pipeline_id=str(uuid.uuid4()),
            agency_id=agency_id,
            name="Main Talent Pipeline",
            description="Track potential and current talent"
        )
        
        # Create default contract templates
        default_templates = [
            ContractTemplate(
                template_id=str(uuid.uuid4()),
                agency_id=agency_id,
                template_type=TemplateType.MODEL_CONTRACT,
                name="Standard Model Contract",
                description="Default contract for model representation",
                content=self._get_default_model_contract_template(),
                variables=["model_name", "agency_name", "start_date", "commission_rate", "territory"],
                is_default=True
            ),
            ContractTemplate(
                template_id=str(uuid.uuid4()),
                agency_id=agency_id,
                template_type=TemplateType.BOOKING_AGREEMENT,
                name="Standard Booking Agreement",
                description="Default booking agreement template",
                content=self._get_default_booking_template(),
                variables=["client_name", "model_name", "booking_date", "rate", "usage_terms"],
                is_default=True
            ),
            ContractTemplate(
                template_id=str(uuid.uuid4()),
                agency_id=agency_id,
                template_type=TemplateType.RELEASE_FORM,
                name="Model Release Form",
                description="Standard model release form",
                content=self._get_default_release_template(),
                variables=["model_name", "shoot_date", "usage_scope", "territory", "duration"],
                is_default=True
            )
        ]
        
        workspace = AgencyWorkspace(
            workspace_id=workspace_id,
            agency_id=agency_id,
            agency_name=agency_name,
            branding=default_branding,
            dashboards=[default_dashboard],
            pipelines=[default_pipeline],
            templates=default_templates,
            settings={
                "notifications_enabled": True,
                "ai_suggestions_enabled": True,
                "auto_pipeline_updates": True,
                "timezone": "UTC"
            }
        )
        
        # Save to database
        try:
            workspaces_collection = self.db["agency_workspaces"]
            await workspaces_collection.insert_one(workspace.dict())
        except Exception:
            pass
        
        return workspace
    
    def _get_default_model_contract_template(self) -> str:
        return """MODEL REPRESENTATION AGREEMENT

This Agreement is made between {{agency_name}} ("Agency") and {{model_name}} ("Model").

1. REPRESENTATION
The Agency agrees to represent the Model for modeling, promotional, and related work in {{territory}}.

2. TERM
This agreement begins on {{start_date}} and continues for a period of one (1) year.

3. COMMISSION
The Model agrees to pay the Agency a commission of {{commission_rate}}% on all bookings.

4. OBLIGATIONS
[Standard obligations clause]

5. TERMINATION
[Standard termination clause]

Signatures:
_____________________
Model: {{model_name}}
Date: _______________

_____________________
Agency: {{agency_name}}
Date: _______________
"""
    
    def _get_default_booking_template(self) -> str:
        return """BOOKING AGREEMENT

Client: {{client_name}}
Model: {{model_name}}
Booking Date: {{booking_date}}
Rate: {{rate}}

USAGE TERMS:
{{usage_terms}}

This booking confirmation is subject to our standard terms and conditions.

Confirmed by:
_____________________
Date: _______________
"""
    
    def _get_default_release_template(self) -> str:
        return """MODEL RELEASE FORM

I, {{model_name}}, hereby grant permission to use my likeness in photographs/videos taken on {{shoot_date}}.

USAGE SCOPE: {{usage_scope}}
TERRITORY: {{territory}}
DURATION: {{duration}}

I release and discharge all claims arising from use of these images within the scope defined above.

Model Signature: _____________________
Date: _______________
Witness: _______________
"""
    
    async def get_workspace(self, agency_id: str) -> Optional[AgencyWorkspace]:
        """
        Get an agency's workspace.
        """
        try:
            workspaces_collection = self.db["agency_workspaces"]
            workspace_data = await workspaces_collection.find_one({"agency_id": agency_id})
            
            if workspace_data:
                workspace_data.pop("_id", None)
                return AgencyWorkspace(**workspace_data)
            
            return None
        except Exception:
            return None
    
    async def update_branding(self, agency_id: str, branding_updates: Dict[str, Any]) -> AgencyBranding:
        """
        Update agency branding.
        """
        try:
            workspaces_collection = self.db["agency_workspaces"]
            
            update_fields = {f"branding.{k}": v for k, v in branding_updates.items()}
            update_fields["updated_at"] = datetime.now(timezone.utc)
            
            await workspaces_collection.update_one(
                {"agency_id": agency_id},
                {"$set": update_fields}
            )
            
            workspace = await self.get_workspace(agency_id)
            return workspace.branding if workspace else AgencyBranding(agency_id=agency_id)
        except Exception:
            return AgencyBranding(agency_id=agency_id, **branding_updates)
    
    async def create_dashboard(self, agency_id: str, name: str, description: str = "", widgets: List[Dict] = None) -> CustomDashboard:
        """
        Create a custom dashboard for the agency.
        """
        import uuid
        
        dashboard = CustomDashboard(
            dashboard_id=str(uuid.uuid4()),
            agency_id=agency_id,
            name=name,
            description=description,
            widgets=[DashboardWidget(**w) for w in (widgets or [])]
        )
        
        try:
            workspaces_collection = self.db["agency_workspaces"]
            await workspaces_collection.update_one(
                {"agency_id": agency_id},
                {
                    "$push": {"dashboards": dashboard.dict()},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
        except Exception:
            pass
        
        return dashboard
    
    async def add_talent_to_pipeline(
        self,
        agency_id: str,
        pipeline_id: str,
        talent_data: Dict[str, Any]
    ) -> TalentPipelineEntry:
        """
        Add a talent to a pipeline.
        """
        import uuid
        
        entry = TalentPipelineEntry(
            entry_id=str(uuid.uuid4()),
            agency_id=agency_id,
            talent_id=talent_data.get("talent_id", str(uuid.uuid4())),
            talent_name=talent_data.get("talent_name", "Unknown"),
            stage=PipelineStage(talent_data.get("stage", "scouting")),
            source=talent_data.get("source", ""),
            assigned_to=talent_data.get("assigned_to"),
            rating=talent_data.get("rating", 0),
            tags=talent_data.get("tags", []),
            notes=talent_data.get("notes", "")
        )
        
        try:
            workspaces_collection = self.db["agency_workspaces"]
            await workspaces_collection.update_one(
                {"agency_id": agency_id, "pipelines.pipeline_id": pipeline_id},
                {
                    "$push": {"pipelines.$.entries": entry.dict()},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
        except Exception:
            pass
        
        return entry
    
    async def move_talent_stage(
        self,
        agency_id: str,
        pipeline_id: str,
        entry_id: str,
        new_stage: PipelineStage
    ) -> bool:
        """
        Move a talent to a different pipeline stage.
        """
        try:
            workspaces_collection = self.db["agency_workspaces"]
            result = await workspaces_collection.update_one(
                {
                    "agency_id": agency_id,
                    "pipelines.pipeline_id": pipeline_id,
                    "pipelines.entries.entry_id": entry_id
                },
                {
                    "$set": {
                        "pipelines.$[p].entries.$[e].stage": new_stage.value,
                        "pipelines.$[p].entries.$[e].updated_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                array_filters=[
                    {"p.pipeline_id": pipeline_id},
                    {"e.entry_id": entry_id}
                ]
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def add_note(
        self,
        agency_id: str,
        entity_type: str,
        entity_id: str,
        author_id: str,
        author_name: str,
        content: str,
        visibility: NoteVisibility = NoteVisibility.TEAM,
        tags: List[str] = None
    ) -> InternalNote:
        """
        Add an internal note to any entity.
        """
        import uuid
        
        note = InternalNote(
            note_id=str(uuid.uuid4()),
            agency_id=agency_id,
            entity_type=entity_type,
            entity_id=entity_id,
            author_id=author_id,
            author_name=author_name,
            content=content,
            visibility=visibility,
            tags=tags or []
        )
        
        try:
            notes_collection = self.db["agency_notes"]
            await notes_collection.insert_one(note.dict())
        except Exception:
            pass
        
        return note
    
    async def get_notes(
        self,
        agency_id: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 50
    ) -> List[InternalNote]:
        """
        Get notes for an agency, optionally filtered by entity.
        """
        try:
            notes_collection = self.db["agency_notes"]
            
            query = {"agency_id": agency_id}
            if entity_type:
                query["entity_type"] = entity_type
            if entity_id:
                query["entity_id"] = entity_id
            
            notes = await notes_collection.find(query).sort("created_at", -1).limit(limit).to_list(limit)
            
            return [InternalNote(**{k: v for k, v in n.items() if k != "_id"}) for n in notes]
        except Exception:
            return []
    
    async def create_contract_template(
        self,
        agency_id: str,
        template_type: TemplateType,
        name: str,
        content: str,
        description: str = "",
        variables: List[str] = None
    ) -> ContractTemplate:
        """
        Create a custom contract template.
        """
        import uuid
        
        template = ContractTemplate(
            template_id=str(uuid.uuid4()),
            agency_id=agency_id,
            template_type=template_type,
            name=name,
            description=description,
            content=content,
            variables=variables or []
        )
        
        try:
            workspaces_collection = self.db["agency_workspaces"]
            await workspaces_collection.update_one(
                {"agency_id": agency_id},
                {
                    "$push": {"templates": template.dict()},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
        except Exception:
            pass
        
        return template
    
    async def generate_contract_from_template(
        self,
        agency_id: str,
        template_id: str,
        variables: Dict[str, str]
    ) -> str:
        """
        Generate a contract from a template by filling in variables.
        """
        try:
            workspace = await self.get_workspace(agency_id)
            if not workspace:
                return ""
            
            template = next((t for t in workspace.templates if t.template_id == template_id), None)
            if not template:
                return ""
            
            content = template.content
            for var, value in variables.items():
                content = content.replace(f"{{{{{var}}}}}", str(value))
            
            return content
        except Exception:
            return ""
    
    async def generate_casting_suggestions(
        self,
        agency_id: str,
        campaign_requirements: Dict[str, Any]
    ) -> CastingSuggestion:
        """
        Generate AI-powered casting suggestions for a campaign.
        """
        import uuid
        
        system_message = """You are an expert casting director for a modeling agency.
        Analyze campaign requirements and suggest the best talent matches from the roster."""
        
        chat = self._get_chat(f"casting-{agency_id}", system_message)
        
        # Get agency's talent roster
        try:
            models_collection = self.db["models"]
            roster = await models_collection.find({"agency_id": agency_id, "status": "active"}).to_list(50)
            roster_summary = [
                {
                    "id": str(m.get("_id", "")),
                    "name": m.get("name", ""),
                    "categories": m.get("categories", []),
                    "experience_level": m.get("experience_level", ""),
                    "measurements": m.get("measurements", {}),
                    "skills": m.get("skills", []),
                    "rating": m.get("rating", 0)
                }
                for m in roster
            ]
        except Exception:
            roster_summary = []
        
        prompt = f"""Analyze this campaign and suggest the best talent matches:

Campaign Requirements:
{json.dumps(campaign_requirements, indent=2, default=str)}

Available Talent Roster:
{json.dumps(roster_summary, indent=2, default=str)}

Provide JSON response:
{{
    "suggested_talents": [
        {{
            "talent_id": "id",
            "talent_name": "name",
            "match_score": <0-100>,
            "match_reasons": ["reason1", "reason2"]
        }}
    ],
    "ai_reasoning": "overall reasoning for selections",
    "confidence_score": <0-100>
}}

Consider:
- Physical requirements match
- Experience level
- Previous campaign performance
- Availability
- Brand fit
- Budget constraints"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            result = json.loads(json_str)
            
            suggestion = CastingSuggestion(
                suggestion_id=str(uuid.uuid4()),
                agency_id=agency_id,
                campaign_id=campaign_requirements.get("campaign_id"),
                campaign_name=campaign_requirements.get("campaign_name", "Unnamed Campaign"),
                suggested_talents=result.get("suggested_talents", []),
                match_criteria=campaign_requirements,
                ai_reasoning=result.get("ai_reasoning", ""),
                confidence_score=result.get("confidence_score", 50)
            )
            
            # Store suggestion
            try:
                suggestions_collection = self.db["casting_suggestions"]
                await suggestions_collection.insert_one(suggestion.dict())
            except Exception:
                pass
            
            return suggestion
        except (json.JSONDecodeError, KeyError):
            return CastingSuggestion(
                suggestion_id=str(uuid.uuid4()),
                agency_id=agency_id,
                campaign_name=campaign_requirements.get("campaign_name", "Unnamed Campaign"),
                ai_reasoning="Unable to generate suggestions - please try again",
                confidence_score=0
            )
    
    async def get_ai_insights(self, agency_id: str) -> Dict[str, Any]:
        """
        Get AI-generated insights for the agency dashboard.
        """
        system_message = """You are a business intelligence analyst for a modeling agency.
        Provide actionable insights based on agency performance data."""
        
        chat = self._get_chat(f"insights-{agency_id}", system_message)
        
        # Gather agency metrics
        try:
            # Get basic stats
            models_collection = self.db["models"]
            bookings_collection = self.db["bookings"]
            
            active_models = await models_collection.count_documents({"agency_id": agency_id, "status": "active"})
            
            recent_bookings = await bookings_collection.find({
                "agency_id": agency_id,
                "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=30)}
            }).to_list(100)
            
            total_revenue = sum(b.get("amount", 0) for b in recent_bookings)
            
            metrics = {
                "active_models": active_models,
                "bookings_30d": len(recent_bookings),
                "revenue_30d": total_revenue,
                "avg_booking_value": total_revenue / len(recent_bookings) if recent_bookings else 0
            }
        except Exception:
            metrics = {
                "active_models": 0,
                "bookings_30d": 0,
                "revenue_30d": 0,
                "avg_booking_value": 0
            }
        
        prompt = f"""Analyze these agency metrics and provide insights:

Metrics:
{json.dumps(metrics, indent=2)}

Provide JSON response:
{{
    "performance_summary": "brief summary",
    "key_insights": ["insight1", "insight2", "insight3"],
    "opportunities": ["opportunity1", "opportunity2"],
    "risks": ["risk1", "risk2"],
    "recommended_actions": ["action1", "action2", "action3"]
}}"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            insights = json.loads(json_str)
            insights["metrics"] = metrics
            insights["generated_at"] = datetime.now(timezone.utc).isoformat()
            
            return insights
        except (json.JSONDecodeError, KeyError):
            return {
                "metrics": metrics,
                "performance_summary": "Analysis unavailable",
                "key_insights": [],
                "opportunities": [],
                "risks": [],
                "recommended_actions": [],
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_widget_data(self, agency_id: str, widget_type: str) -> Dict[str, Any]:
        """
        Get data for a specific dashboard widget.
        """
        try:
            if widget_type == "stats_overview":
                models_collection = self.db["models"]
                bookings_collection = self.db["bookings"]
                
                active_models = await models_collection.count_documents({"agency_id": agency_id, "status": "active"})
                total_bookings = await bookings_collection.count_documents({"agency_id": agency_id})
                
                recent_bookings = await bookings_collection.find({
                    "agency_id": agency_id,
                    "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=30)}
                }).to_list(100)
                
                return {
                    "active_models": active_models,
                    "total_bookings": total_bookings,
                    "bookings_this_month": len(recent_bookings),
                    "revenue_this_month": sum(b.get("amount", 0) for b in recent_bookings)
                }
            
            elif widget_type == "talent_pipeline":
                workspace = await self.get_workspace(agency_id)
                if workspace and workspace.pipelines:
                    pipeline = workspace.pipelines[0]
                    stage_counts = {}
                    for entry in pipeline.entries:
                        stage = entry.stage.value
                        stage_counts[stage] = stage_counts.get(stage, 0) + 1
                    return {"stages": stage_counts, "total": len(pipeline.entries)}
                return {"stages": {}, "total": 0}
            
            elif widget_type == "recent_bookings":
                bookings_collection = self.db["bookings"]
                bookings = await bookings_collection.find(
                    {"agency_id": agency_id}
                ).sort("created_at", -1).limit(5).to_list(5)
                
                return {
                    "bookings": [
                        {
                            "id": str(b.get("_id", "")),
                            "client": b.get("client_name", ""),
                            "model": b.get("model_name", ""),
                            "amount": b.get("amount", 0),
                            "date": b.get("booking_date", "")
                        }
                        for b in bookings
                    ]
                }
            
            elif widget_type == "ai_insights":
                return await self.get_ai_insights(agency_id)
            
            elif widget_type == "casting_suggestions":
                suggestions_collection = self.db["casting_suggestions"]
                suggestions = await suggestions_collection.find(
                    {"agency_id": agency_id}
                ).sort("created_at", -1).limit(3).to_list(3)
                
                return {
                    "suggestions": [
                        {
                            "id": s.get("suggestion_id", ""),
                            "campaign": s.get("campaign_name", ""),
                            "talents_count": len(s.get("suggested_talents", [])),
                            "confidence": s.get("confidence_score", 0)
                        }
                        for s in suggestions
                    ]
                }
            
            return {}
        except Exception:
            return {}


# Singleton instance
_workspace_service_instance = None

def get_workspace_service(db) -> ModularAgencyWorkspaceService:
    global _workspace_service_instance
    if _workspace_service_instance is None:
        _workspace_service_instance = ModularAgencyWorkspaceService(db)
    return _workspace_service_instance
