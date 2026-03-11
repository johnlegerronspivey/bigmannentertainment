"""
Creative Studio for Agencies - Service Layer
Business logic for creative content management with AI-powered design generation
"""

import os
import uuid
import base64
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
import google.generativeai as genai
from dotenv import load_dotenv

from creative_studio_models import (
    BrandKit, BrandAsset, BrandColor, BrandFont, AssetType,
    DesignTemplate, DesignElement, TemplateCategory, SocialPlatform,
    CreativeProject, ProjectStatus, ProjectCollaborator, ProjectComment,
    ProjectVersion, CollaboratorRole, AIGenerationRequest, AIGenerationResult,
    PublishConfig, PublishResult, CreativeStudioStats, PLATFORM_DIMENSIONS,
    CreateBrandKitRequest, CreateProjectRequest, UpdateProjectRequest,
    ExportFormat
)

load_dotenv()

# Initialize Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class CreativeStudioService:
    """Service for Creative Studio operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.brand_kits_collection = db.creative_studio_brand_kits
        self.projects_collection = db.creative_studio_projects
        self.templates_collection = db.creative_studio_templates
        self.ai_generations_collection = db.creative_studio_ai_generations
        self.publish_history_collection = db.creative_studio_publish_history
        
        # Initialize sample data
        asyncio.create_task(self._initialize_sample_data())
    
    async def _initialize_sample_data(self):
        """Initialize sample templates and data"""
        try:
            # Check if templates exist
            count = await self.templates_collection.count_documents({})
            if count == 0:
                await self._create_sample_templates()
        except Exception as e:
            print(f"Error initializing sample data: {e}")
    
    async def _create_sample_templates(self):
        """Create sample design templates"""
        sample_templates = [
            # Social Media Templates
            DesignTemplate(
                name="Instagram Post - Modern Grid",
                description="Clean grid layout for Instagram posts",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=SocialPlatform.INSTAGRAM_POST,
                width=1080,
                height=1080,
                elements=[
                    DesignElement(
                        element_type="shape",
                        position={"x": 0, "y": 0},
                        size={"width": 1080, "height": 1080},
                        styles={"backgroundColor": "#f8f9fa"}
                    ),
                    DesignElement(
                        element_type="text",
                        content="Your Headline Here",
                        position={"x": 100, "y": 400},
                        size={"width": 880, "height": 100},
                        styles={"fontSize": 48, "fontWeight": "bold", "textAlign": "center"}
                    )
                ],
                tags=["instagram", "modern", "minimal"],
                is_system_template=True
            ),
            DesignTemplate(
                name="Instagram Story - Gradient",
                description="Vibrant gradient story template",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=SocialPlatform.INSTAGRAM_STORY,
                width=1080,
                height=1920,
                elements=[
                    DesignElement(
                        element_type="shape",
                        position={"x": 0, "y": 0},
                        size={"width": 1080, "height": 1920},
                        styles={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"}
                    ),
                    DesignElement(
                        element_type="text",
                        content="SWIPE UP",
                        position={"x": 340, "y": 1700},
                        size={"width": 400, "height": 60},
                        styles={"fontSize": 24, "color": "#ffffff", "textAlign": "center"}
                    )
                ],
                tags=["instagram", "story", "gradient"],
                is_system_template=True
            ),
            DesignTemplate(
                name="Twitter Post - Quote",
                description="Elegant quote card for Twitter",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=SocialPlatform.TWITTER_POST,
                width=1200,
                height=675,
                elements=[
                    DesignElement(
                        element_type="shape",
                        position={"x": 0, "y": 0},
                        size={"width": 1200, "height": 675},
                        styles={"backgroundColor": "#1a1a2e"}
                    ),
                    DesignElement(
                        element_type="text",
                        content='"Your inspiring quote here"',
                        position={"x": 100, "y": 250},
                        size={"width": 1000, "height": 150},
                        styles={"fontSize": 36, "color": "#ffffff", "fontStyle": "italic", "textAlign": "center"}
                    )
                ],
                tags=["twitter", "quote", "dark"],
                is_system_template=True
            ),
            DesignTemplate(
                name="YouTube Thumbnail - Gaming",
                description="Eye-catching gaming thumbnail",
                category=TemplateCategory.VIDEO_THUMBNAILS,
                platform=SocialPlatform.YOUTUBE_THUMBNAIL,
                width=1280,
                height=720,
                elements=[
                    DesignElement(
                        element_type="shape",
                        position={"x": 0, "y": 0},
                        size={"width": 1280, "height": 720},
                        styles={"background": "linear-gradient(45deg, #ff6b6b, #feca57)"}
                    ),
                    DesignElement(
                        element_type="text",
                        content="EPIC WIN!",
                        position={"x": 400, "y": 300},
                        size={"width": 480, "height": 120},
                        styles={"fontSize": 72, "fontWeight": "bold", "color": "#ffffff", "textShadow": "4px 4px 8px rgba(0,0,0,0.5)"}
                    )
                ],
                tags=["youtube", "gaming", "thumbnail"],
                is_system_template=True
            ),
            # Marketing Templates
            DesignTemplate(
                name="Facebook Ad - Product Showcase",
                description="Clean product showcase template",
                category=TemplateCategory.ADVERTISING,
                platform=SocialPlatform.FACEBOOK_POST,
                width=1200,
                height=630,
                elements=[
                    DesignElement(
                        element_type="shape",
                        position={"x": 0, "y": 0},
                        size={"width": 1200, "height": 630},
                        styles={"backgroundColor": "#ffffff"}
                    ),
                    DesignElement(
                        element_type="text",
                        content="50% OFF",
                        position={"x": 50, "y": 50},
                        size={"width": 200, "height": 80},
                        styles={"fontSize": 36, "fontWeight": "bold", "color": "#e74c3c", "backgroundColor": "#fff3cd", "borderRadius": 8}
                    ),
                    DesignElement(
                        element_type="text",
                        content="Shop Now",
                        position={"x": 900, "y": 500},
                        size={"width": 250, "height": 80},
                        styles={"fontSize": 24, "fontWeight": "bold", "color": "#ffffff", "backgroundColor": "#3498db", "borderRadius": 40, "textAlign": "center"}
                    )
                ],
                tags=["facebook", "ad", "product", "sale"],
                is_system_template=True
            ),
            DesignTemplate(
                name="LinkedIn Banner - Professional",
                description="Professional LinkedIn banner",
                category=TemplateCategory.BANNERS,
                platform=SocialPlatform.LINKEDIN_BANNER,
                width=1584,
                height=396,
                elements=[
                    DesignElement(
                        element_type="shape",
                        position={"x": 0, "y": 0},
                        size={"width": 1584, "height": 396},
                        styles={"background": "linear-gradient(90deg, #2c3e50, #34495e)"}
                    ),
                    DesignElement(
                        element_type="text",
                        content="Your Company Name",
                        position={"x": 50, "y": 150},
                        size={"width": 600, "height": 80},
                        styles={"fontSize": 42, "fontWeight": "bold", "color": "#ffffff"}
                    ),
                    DesignElement(
                        element_type="text",
                        content="Innovation • Excellence • Growth",
                        position={"x": 50, "y": 240},
                        size={"width": 500, "height": 40},
                        styles={"fontSize": 18, "color": "#bdc3c7"}
                    )
                ],
                tags=["linkedin", "banner", "professional"],
                is_system_template=True
            ),
        ]
        
        for template in sample_templates:
            await self.templates_collection.insert_one(template.dict())
    
    # ==================== Brand Kit Operations ====================
    
    async def create_brand_kit(self, agency_id: str, request: CreateBrandKitRequest) -> BrandKit:
        """Create a new brand kit"""
        brand_kit = BrandKit(
            agency_id=agency_id,
            name=request.name,
            description=request.description,
            colors=request.colors,
            fonts=request.fonts,
            voice_tone=request.voice_tone,
            tagline=request.tagline,
            brand_values=request.brand_values
        )
        
        await self.brand_kits_collection.insert_one(brand_kit.dict())
        return brand_kit
    
    async def get_brand_kits(self, agency_id: str) -> List[BrandKit]:
        """Get all brand kits for an agency"""
        cursor = self.brand_kits_collection.find({"agency_id": agency_id})
        brand_kits = []
        async for doc in cursor:
            doc.pop("_id", None)
            brand_kits.append(BrandKit(**doc))
        return brand_kits
    
    async def get_brand_kit(self, brand_kit_id: str) -> Optional[BrandKit]:
        """Get a specific brand kit"""
        doc = await self.brand_kits_collection.find_one({"id": brand_kit_id})
        if doc:
            doc.pop("_id", None)
            return BrandKit(**doc)
        return None
    
    async def update_brand_kit(self, brand_kit_id: str, updates: Dict[str, Any]) -> Optional[BrandKit]:
        """Update a brand kit"""
        updates["updated_at"] = datetime.utcnow()
        await self.brand_kits_collection.update_one(
            {"id": brand_kit_id},
            {"$set": updates}
        )
        return await self.get_brand_kit(brand_kit_id)
    
    async def delete_brand_kit(self, brand_kit_id: str) -> bool:
        """Delete a brand kit"""
        result = await self.brand_kits_collection.delete_one({"id": brand_kit_id})
        return result.deleted_count > 0
    
    async def add_brand_asset(self, brand_kit_id: str, asset: BrandAsset) -> Optional[BrandKit]:
        """Add an asset to a brand kit"""
        await self.brand_kits_collection.update_one(
            {"id": brand_kit_id},
            {
                "$push": {"assets": asset.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return await self.get_brand_kit(brand_kit_id)
    
    # ==================== Template Operations ====================
    
    async def get_templates(
        self,
        category: Optional[TemplateCategory] = None,
        platform: Optional[SocialPlatform] = None,
        search: Optional[str] = None
    ) -> List[DesignTemplate]:
        """Get design templates with filters"""
        query = {}
        
        if category:
            query["category"] = category.value
        if platform:
            query["platform"] = platform.value
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search.lower()]}}
            ]
        
        cursor = self.templates_collection.find(query).sort("usage_count", -1)
        templates = []
        async for doc in cursor:
            doc.pop("_id", None)
            templates.append(DesignTemplate(**doc))
        return templates
    
    async def get_template(self, template_id: str) -> Optional[DesignTemplate]:
        """Get a specific template"""
        doc = await self.templates_collection.find_one({"id": template_id})
        if doc:
            doc.pop("_id", None)
            return DesignTemplate(**doc)
        return None
    
    async def increment_template_usage(self, template_id: str):
        """Increment template usage count"""
        await self.templates_collection.update_one(
            {"id": template_id},
            {"$inc": {"usage_count": 1}}
        )
    
    # ==================== Project Operations ====================
    
    async def create_project(
        self,
        agency_id: str,
        owner_id: str,
        request: CreateProjectRequest
    ) -> CreativeProject:
        """Create a new creative project"""
        # Determine dimensions
        if request.width and request.height:
            width, height = request.width, request.height
        elif request.platform:
            dims = PLATFORM_DIMENSIONS.get(request.platform, {"width": 1080, "height": 1080})
            width, height = dims["width"], dims["height"]
        elif request.template_id:
            template = await self.get_template(request.template_id)
            if template:
                width, height = template.width, template.height
            else:
                width, height = 1080, 1080
        else:
            width, height = 1080, 1080
        
        # Get template elements if using a template
        elements = []
        if request.template_id:
            template = await self.get_template(request.template_id)
            if template:
                elements = template.elements
                await self.increment_template_usage(request.template_id)
        
        project = CreativeProject(
            agency_id=agency_id,
            name=request.name,
            description=request.description,
            category=request.category,
            platform=request.platform,
            template_id=request.template_id,
            brand_kit_id=request.brand_kit_id,
            width=width,
            height=height,
            elements=elements,
            owner_id=owner_id,
            collaborators=[
                ProjectCollaborator(
                    user_id=owner_id,
                    user_email="owner@agency.com",
                    user_name="Project Owner",
                    role=CollaboratorRole.OWNER
                )
            ]
        )
        
        await self.projects_collection.insert_one(project.dict())
        return project
    
    async def get_projects(
        self,
        agency_id: str,
        status: Optional[ProjectStatus] = None,
        category: Optional[TemplateCategory] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[CreativeProject], int]:
        """Get projects with filters"""
        query = {"agency_id": agency_id}
        
        if status:
            query["status"] = status.value
        if category:
            query["category"] = category.value
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search.lower()]}}
            ]
        
        total = await self.projects_collection.count_documents(query)
        cursor = self.projects_collection.find(query).sort("updated_at", -1).skip(offset).limit(limit)
        
        projects = []
        async for doc in cursor:
            doc.pop("_id", None)
            projects.append(CreativeProject(**doc))
        
        return projects, total
    
    async def get_project(self, project_id: str) -> Optional[CreativeProject]:
        """Get a specific project"""
        doc = await self.projects_collection.find_one({"id": project_id})
        if doc:
            doc.pop("_id", None)
            return CreativeProject(**doc)
        return None
    
    async def update_project(
        self,
        project_id: str,
        request: UpdateProjectRequest
    ) -> Optional[CreativeProject]:
        """Update a project"""
        updates = {"updated_at": datetime.utcnow()}
        
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.elements is not None:
            updates["elements"] = [e.dict() for e in request.elements]
        if request.background_color is not None:
            updates["background_color"] = request.background_color
        if request.background_image is not None:
            updates["background_image"] = request.background_image
        if request.status is not None:
            updates["status"] = request.status.value
        if request.tags is not None:
            updates["tags"] = request.tags
        
        await self.projects_collection.update_one(
            {"id": project_id},
            {"$set": updates}
        )
        return await self.get_project(project_id)
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        result = await self.projects_collection.delete_one({"id": project_id})
        return result.deleted_count > 0
    
    async def save_project_version(self, project_id: str, user_id: str, name: Optional[str] = None) -> Optional[CreativeProject]:
        """Save a version snapshot of the project"""
        project = await self.get_project(project_id)
        if not project:
            return None
        
        version = ProjectVersion(
            version_number=project.current_version + 1,
            name=name,
            elements_snapshot=project.elements,
            created_by=user_id
        )
        
        await self.projects_collection.update_one(
            {"id": project_id},
            {
                "$push": {"versions": version.dict()},
                "$inc": {"current_version": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return await self.get_project(project_id)
    
    # ==================== Collaboration Operations ====================
    
    async def add_collaborator(
        self,
        project_id: str,
        user_id: str,
        user_email: str,
        user_name: str,
        role: CollaboratorRole
    ) -> Optional[CreativeProject]:
        """Add a collaborator to a project"""
        collaborator = ProjectCollaborator(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            role=role
        )
        
        await self.projects_collection.update_one(
            {"id": project_id},
            {
                "$push": {"collaborators": collaborator.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return await self.get_project(project_id)
    
    async def remove_collaborator(self, project_id: str, user_id: str) -> Optional[CreativeProject]:
        """Remove a collaborator from a project"""
        await self.projects_collection.update_one(
            {"id": project_id},
            {
                "$pull": {"collaborators": {"user_id": user_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return await self.get_project(project_id)
    
    async def add_comment(
        self,
        project_id: str,
        user_id: str,
        user_name: str,
        content: str,
        position: Optional[Dict[str, float]] = None
    ) -> Optional[CreativeProject]:
        """Add a comment to a project"""
        comment = ProjectComment(
            user_id=user_id,
            user_name=user_name,
            content=content,
            position=position
        )
        
        await self.projects_collection.update_one(
            {"id": project_id},
            {
                "$push": {"comments": comment.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return await self.get_project(project_id)
    
    async def resolve_comment(self, project_id: str, comment_id: str, user_id: str) -> Optional[CreativeProject]:
        """Resolve a comment"""
        await self.projects_collection.update_one(
            {"id": project_id, "comments.id": comment_id},
            {
                "$set": {
                    "comments.$.is_resolved": True,
                    "comments.$.resolved_by": user_id,
                    "comments.$.resolved_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return await self.get_project(project_id)
    
    # ==================== AI Generation Operations ====================
    
    async def generate_ai_image(
        self,
        request: AIGenerationRequest,
        user_id: str
    ) -> AIGenerationResult:
        """Generate an image using Gemini AI"""
        import time
        start_time = time.time()
        
        # Build the prompt
        prompt = request.prompt
        if request.style:
            prompt = f"{prompt}, in {request.style} style"
        
        # If brand kit specified, try to incorporate brand elements
        if request.brand_kit_id:
            brand_kit = await self.get_brand_kit(request.brand_kit_id)
            if brand_kit and brand_kit.colors:
                primary_colors = [c.hex_code for c in brand_kit.colors[:3]]
                prompt = f"{prompt}. Use these brand colors: {', '.join(primary_colors)}"
        
        try:
            # Use Gemini for image generation
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Generate the image
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="image/png"
                )
            )
            
            # Extract image data
            image_data = None
            image_url = None
            
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data'):
                        image_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                        # In production, upload to S3 and get URL
                        image_url = f"data:image/png;base64,{image_data[:100]}..."
                        break
            
            if not image_data:
                # Fallback: return a placeholder
                image_url = f"https://placehold.co/{request.width}x{request.height}/667eea/ffffff?text=AI+Generated"
                image_data = None
            
        except Exception as e:
            print(f"AI generation error: {e}")
            # Return placeholder on error
            image_url = f"https://placehold.co/{request.width}x{request.height}/667eea/ffffff?text=AI+Generated"
            image_data = None
        
        generation_time = int((time.time() - start_time) * 1000)
        
        result = AIGenerationResult(
            prompt=request.prompt,
            image_url=image_url,
            image_data=image_data,
            width=request.width,
            height=request.height,
            generation_time_ms=generation_time
        )
        
        # Store generation history
        await self.ai_generations_collection.insert_one({
            **result.dict(),
            "user_id": user_id,
            "style": request.style,
            "platform": request.platform.value if request.platform else None
        })
        
        return result
    
    async def get_ai_generation_history(self, user_id: str, limit: int = 20) -> List[AIGenerationResult]:
        """Get AI generation history for a user"""
        cursor = self.ai_generations_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            doc.pop("user_id", None)
            results.append(AIGenerationResult(**doc))
        return results
    
    # ==================== Export & Publish Operations ====================
    
    async def export_project(
        self,
        project_id: str,
        format: ExportFormat,
        quality: int = 90,
        scale: float = 1.0
    ) -> Dict[str, Any]:
        """Export a project to specified format"""
        project = await self.get_project(project_id)
        if not project:
            return {"success": False, "error": "Project not found"}
        
        # In production, this would render the project and upload to S3
        # For now, return mock data
        export_url = f"https://cdn.bigmannentertainment.com/exports/{project_id}.{format.value}"
        
        export_record = {
            "format": format.value,
            "url": export_url,
            "exported_at": datetime.utcnow().isoformat(),
            "quality": quality,
            "scale": scale
        }
        
        await self.projects_collection.update_one(
            {"id": project_id},
            {"$push": {"exported_files": export_record}}
        )
        
        return {
            "success": True,
            "url": export_url,
            "format": format.value,
            "width": int(project.width * scale),
            "height": int(project.height * scale)
        }
    
    async def publish_to_platform(
        self,
        project_id: str,
        config: PublishConfig,
        user_id: str
    ) -> PublishResult:
        """Publish a project to a social platform"""
        project = await self.get_project(project_id)
        if not project:
            return PublishResult(
                project_id=project_id,
                platform=config.platform,
                status="failed",
                error_message="Project not found"
            )
        
        # In production, this would integrate with social media APIs
        # For now, simulate successful publishing
        result = PublishResult(
            project_id=project_id,
            platform=config.platform,
            status="published",
            platform_post_id=f"post_{uuid.uuid4().hex[:12]}",
            platform_url=f"https://{config.platform.value.split('_')[0]}.com/p/{uuid.uuid4().hex[:8]}",
            published_at=datetime.utcnow()
        )
        
        # Store publish history
        await self.publish_history_collection.insert_one({
            **result.dict(),
            "user_id": user_id,
            "caption": config.caption,
            "hashtags": config.hashtags
        })
        
        # Update project status
        await self.projects_collection.update_one(
            {"id": project_id},
            {"$set": {"status": ProjectStatus.PUBLISHED.value, "updated_at": datetime.utcnow()}}
        )
        
        return result
    
    async def get_publish_history(
        self,
        agency_id: str,
        platform: Optional[SocialPlatform] = None,
        limit: int = 50
    ) -> List[PublishResult]:
        """Get publishing history"""
        query = {}
        if platform:
            query["platform"] = platform.value
        
        cursor = self.publish_history_collection.find(query).sort("created_at", -1).limit(limit)
        
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            doc.pop("user_id", None)
            results.append(PublishResult(**doc))
        return results
    
    # ==================== Dashboard Stats ====================
    
    async def get_studio_stats(self, agency_id: str) -> CreativeStudioStats:
        """Get creative studio statistics"""
        # Projects stats
        total_projects = await self.projects_collection.count_documents({"agency_id": agency_id})
        projects_in_progress = await self.projects_collection.count_documents({
            "agency_id": agency_id,
            "status": {"$in": [ProjectStatus.IN_PROGRESS.value, ProjectStatus.REVIEW.value]}
        })
        projects_published = await self.projects_collection.count_documents({
            "agency_id": agency_id,
            "status": ProjectStatus.PUBLISHED.value
        })
        
        # Brand kits
        total_brand_kits = await self.brand_kits_collection.count_documents({"agency_id": agency_id})
        
        # AI generations (approximate)
        ai_generations_count = await self.ai_generations_collection.count_documents({})
        
        # Get unique collaborators
        pipeline = [
            {"$match": {"agency_id": agency_id}},
            {"$unwind": "$collaborators"},
            {"$group": {"_id": "$collaborators.user_id"}},
            {"$count": "total"}
        ]
        result = await self.projects_collection.aggregate(pipeline).to_list(1)
        total_collaborators = result[0]["total"] if result else 0
        
        return CreativeStudioStats(
            total_projects=total_projects,
            projects_in_progress=projects_in_progress,
            projects_published=projects_published,
            total_brand_kits=total_brand_kits,
            ai_generations_count=ai_generations_count,
            total_collaborators=total_collaborators,
            storage_used_mb=125.5  # Mock value
        )


# Service instance (initialized with db in endpoints)
_service_instance: Optional[CreativeStudioService] = None


def initialize_creative_studio_service(db: AsyncIOMotorDatabase) -> CreativeStudioService:
    """Initialize the Creative Studio service"""
    global _service_instance
    _service_instance = CreativeStudioService(db)
    return _service_instance


def get_creative_studio_service() -> Optional[CreativeStudioService]:
    """Get the Creative Studio service instance"""
    return _service_instance
