"""
Digital Twin Model Creation System
===================================
Every real model gets a digital twin:
- AI-generated avatar
- Motion-capture ready
- Usable for virtual campaigns, AR try-ons, metaverse shows

Agencies can:
- License the digital twin separately
- Run virtual photoshoots
- Sell digital-only campaigns with zero travel costs

This is a massive revenue multiplier.
"""

import os
import json
import uuid
import base64
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv
import hashlib

load_dotenv()

# AI Integrations
from llm_service import LlmChat, UserMessage, ImageContent


class TwinStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class TwinType(str, Enum):
    AVATAR_2D = "avatar_2d"
    AVATAR_3D = "avatar_3d"
    FULL_BODY = "full_body"
    HEADSHOT = "headshot"
    STYLIZED = "stylized"
    REALISTIC = "realistic"


class TwinStyle(str, Enum):
    PHOTOREALISTIC = "photorealistic"
    FASHION_EDITORIAL = "fashion_editorial"
    COMMERCIAL = "commercial"
    ARTISTIC = "artistic"
    ANIME = "anime"
    CYBERPUNK = "cyberpunk"
    MINIMAL = "minimal"
    LUXURY = "luxury"


class UsageContext(str, Enum):
    VIRTUAL_CAMPAIGN = "virtual_campaign"
    AR_TRYON = "ar_tryon"
    METAVERSE = "metaverse"
    SOCIAL_MEDIA = "social_media"
    E_COMMERCE = "e_commerce"
    GAMING = "gaming"
    NFT = "nft"
    VIRTUAL_PHOTOSHOOT = "virtual_photoshoot"


class LicenseType(str, Enum):
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    LIMITED = "limited"
    TRIAL = "trial"


# Pydantic Models
class DigitalTwinProfile(BaseModel):
    twin_id: str
    model_id: str
    model_name: str
    agency_id: Optional[str] = None
    status: TwinStatus = TwinStatus.PENDING
    twin_type: TwinType = TwinType.AVATAR_2D
    style: TwinStyle = TwinStyle.PHOTOREALISTIC
    
    # Core assets
    base_avatar_url: Optional[str] = None
    avatar_variants: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    
    # 3D/Motion capture data
    is_3d_ready: bool = False
    motion_capture_compatible: bool = False
    ar_compatible: bool = False
    metaverse_compatible: bool = False
    
    # Characteristics preserved from real model
    preserved_features: Dict[str, Any] = Field(default_factory=dict)
    
    # Licensing
    license_type: LicenseType = LicenseType.NON_EXCLUSIVE
    allowed_uses: List[UsageContext] = Field(default_factory=list)
    restricted_uses: List[UsageContext] = Field(default_factory=list)
    
    # Pricing
    base_license_price: float = 500.0
    usage_rate_per_campaign: float = 100.0
    exclusive_multiplier: float = 3.0
    
    # Stats
    total_campaigns: int = 0
    total_revenue: float = 0.0
    views: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)


class VirtualPhotoshoot(BaseModel):
    photoshoot_id: str
    twin_id: str
    client_id: str
    client_name: str
    
    # Shoot configuration
    concept: str
    style: TwinStyle
    background_setting: str
    outfit_description: str
    poses: List[str] = Field(default_factory=list)
    
    # Generated images
    images: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Status
    status: str = "pending"
    images_generated: int = 0
    images_requested: int = 5
    
    # Pricing
    price_per_image: float = 50.0
    total_price: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class TwinLicense(BaseModel):
    license_id: str
    twin_id: str
    licensee_id: str
    licensee_name: str
    
    license_type: LicenseType
    usage_contexts: List[UsageContext] = Field(default_factory=list)
    
    # Terms
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    duration_days: int = 365
    
    # Pricing
    license_fee: float = 0.0
    usage_fee_per_use: float = 0.0
    revenue_share_percent: float = 0.0
    
    # Usage tracking
    total_uses: int = 0
    campaigns: List[str] = Field(default_factory=list)
    
    # Status
    status: str = "active"
    auto_renewal: bool = False
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ARTryOnAsset(BaseModel):
    asset_id: str
    twin_id: str
    asset_type: str  # "clothing", "accessory", "makeup", "hairstyle"
    asset_name: str
    preview_url: Optional[str] = None
    ar_model_url: Optional[str] = None
    compatible_platforms: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetaverseAvatar(BaseModel):
    avatar_id: str
    twin_id: str
    platform: str  # "decentraland", "sandbox", "roblox", "meta_horizon"
    avatar_file_url: Optional[str] = None
    animations: List[str] = Field(default_factory=list)
    wearables: List[str] = Field(default_factory=list)
    compatible: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DigitalTwinService:
    """
    Service for creating and managing digital twins of real models.
    Enables virtual campaigns, AR try-ons, and metaverse presence.
    Uses Google Gemini (Nano Banana) for image generation.
    """
    
    def __init__(self, db):
        self.db = db
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.llm_api_key = self.google_api_key
        self.image_api_key = self.google_api_key
        self.text_api_key = self.google_api_key
        self.model_provider = "gemini"
        self.model_name = "gemini-2.5-flash"
        self.image_model = "gemini-2.5-flash-image"
    
    def _get_chat(self, session_id: str, system_message: str) -> LlmChat:
        chat = LlmChat(
            api_key=self.text_api_key,
            session_id=session_id,
            system_message=system_message
        )
        chat.with_model(self.model_provider, self.model_name)
        return chat
    
    def _get_image_chat(self, session_id: str) -> LlmChat:
        """Create a Gemini chat configured for image generation (Nano Banana)."""
        chat = LlmChat(
            api_key=self.image_api_key,
            session_id=session_id,
            system_message="You are an expert fashion photographer creating high-quality digital avatars and portraits."
        )
        chat.with_model("gemini", self.image_model)
        chat.with_params(modalities=["image", "text"])
        return chat
    
    async def _generate_image(self, prompt: str, session_id: str) -> Optional[str]:
        """Generate an image using Gemini Nano Banana and return base64 data URL."""
        try:
            chat = self._get_image_chat(session_id)
            msg = UserMessage(text=prompt)
            response = await chat.send_message(msg)
            
            # Check if response contains image data (base64)
            if response:
                # If the response starts with base64 image data markers
                if response.startswith("data:image"):
                    return response
                # If it's raw base64
                elif len(response) > 1000 and not response.startswith("{"):
                    return f"data:image/png;base64,{response}"
                # Log for debugging
                print(f"Image gen response type: {type(response)}, len: {len(response)}")
            return None
        except Exception as e:
            error_msg = str(e)
            # Handle quota errors gracefully
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"Image generation quota exceeded. Wait for quota reset.")
            else:
                print(f"Image generation error: {error_msg[:150]}")
            return None
    
    async def create_digital_twin(
        self,
        model_id: str,
        model_data: Dict[str, Any],
        twin_type: TwinType = TwinType.AVATAR_2D,
        style: TwinStyle = TwinStyle.PHOTOREALISTIC,
        generate_immediately: bool = True
    ) -> DigitalTwinProfile:
        """
        Create a digital twin for a real model.
        """
        twin_id = str(uuid.uuid4())
        
        # Extract preserved features from model data
        preserved_features = {
            "hair_color": model_data.get("hair_color", ""),
            "eye_color": model_data.get("eye_color", ""),
            "skin_tone": model_data.get("skin_tone", ""),
            "face_shape": model_data.get("face_shape", ""),
            "height": model_data.get("height", ""),
            "build": model_data.get("build", ""),
            "distinctive_features": model_data.get("distinctive_features", []),
            "style_keywords": model_data.get("style_keywords", [])
        }
        
        # Determine allowed uses based on twin type
        allowed_uses = [UsageContext.VIRTUAL_CAMPAIGN, UsageContext.SOCIAL_MEDIA]
        if twin_type in [TwinType.AVATAR_3D, TwinType.FULL_BODY]:
            allowed_uses.extend([UsageContext.AR_TRYON, UsageContext.METAVERSE, UsageContext.GAMING])
        if style in [TwinStyle.FASHION_EDITORIAL, TwinStyle.LUXURY]:
            allowed_uses.append(UsageContext.E_COMMERCE)
        
        twin = DigitalTwinProfile(
            twin_id=twin_id,
            model_id=model_id,
            model_name=model_data.get("name", "Unknown Model"),
            agency_id=model_data.get("agency_id"),
            twin_type=twin_type,
            style=style,
            preserved_features=preserved_features,
            allowed_uses=allowed_uses,
            is_3d_ready=twin_type == TwinType.AVATAR_3D,
            motion_capture_compatible=twin_type in [TwinType.AVATAR_3D, TwinType.FULL_BODY],
            ar_compatible=twin_type in [TwinType.AVATAR_3D, TwinType.FULL_BODY],
            metaverse_compatible=twin_type == TwinType.AVATAR_3D
        )
        
        # Generate avatar if requested
        if generate_immediately:
            twin = await self._generate_twin_avatar(twin, model_data)
        
        # Save to database
        try:
            twins_collection = self.db["digital_twins"]
            await twins_collection.insert_one(twin.dict())
        except Exception as e:
            print(f"Error saving twin: {e}")
        
        return twin
    
    async def _generate_twin_avatar(
        self,
        twin: DigitalTwinProfile,
        model_data: Dict[str, Any]
    ) -> DigitalTwinProfile:
        """
        Generate the AI avatar for a digital twin using Gemini Nano Banana.
        """
        twin.status = TwinStatus.GENERATING
        
        # Build prompt based on preserved features and style
        prompt = self._build_avatar_prompt(twin, model_data)
        
        try:
            # Generate main avatar using Gemini
            avatar_url = await self._generate_image(prompt, f"twin-avatar-{twin.twin_id}")
            
            if avatar_url:
                twin.base_avatar_url = avatar_url
                twin.thumbnail_url = avatar_url
                twin.status = TwinStatus.ACTIVE
                
                twin.generation_metadata = {
                    "prompt": prompt,
                    "model": "gemini-3-pro-image-preview",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "style": twin.style.value,
                    "type": twin.twin_type.value
                }
            else:
                twin.status = TwinStatus.PENDING
                twin.generation_metadata["error"] = "No image generated"
                
        except Exception as e:
            twin.status = TwinStatus.PENDING
            twin.generation_metadata["error"] = str(e)
        
        twin.updated_at = datetime.now(timezone.utc)
        return twin
    
    def _build_avatar_prompt(self, twin: DigitalTwinProfile, model_data: Dict[str, Any]) -> str:
        """
        Build a detailed prompt for avatar generation.
        """
        features = twin.preserved_features
        style = twin.style.value
        
        # Base prompt
        prompt_parts = [
            f"Professional {style} portrait of a fashion model",
        ]
        
        # Add physical features
        if features.get("hair_color"):
            prompt_parts.append(f"with {features['hair_color']} hair")
        if features.get("eye_color"):
            prompt_parts.append(f"{features['eye_color']} eyes")
        if features.get("skin_tone"):
            prompt_parts.append(f"{features['skin_tone']} skin tone")
        if features.get("face_shape"):
            prompt_parts.append(f"{features['face_shape']} face shape")
        
        # Add style-specific elements
        style_additions = {
            TwinStyle.PHOTOREALISTIC: "ultra realistic, high fashion photography, studio lighting, 8k quality",
            TwinStyle.FASHION_EDITORIAL: "high fashion editorial style, dramatic lighting, vogue magazine quality",
            TwinStyle.COMMERCIAL: "clean commercial photography, bright lighting, approachable expression",
            TwinStyle.ARTISTIC: "artistic portrait, creative lighting, fine art photography style",
            TwinStyle.ANIME: "anime style character, vibrant colors, detailed eyes, studio quality",
            TwinStyle.CYBERPUNK: "cyberpunk aesthetic, neon lighting, futuristic style, sci-fi elements",
            TwinStyle.MINIMAL: "minimalist portrait, soft lighting, clean background, elegant simplicity",
            TwinStyle.LUXURY: "luxury brand aesthetic, sophisticated lighting, premium quality, elegant"
        }
        
        prompt_parts.append(style_additions.get(twin.style, "professional quality"))
        
        # Add type-specific elements
        if twin.twin_type == TwinType.HEADSHOT:
            prompt_parts.append("professional headshot, face focused, neutral background")
        elif twin.twin_type == TwinType.FULL_BODY:
            prompt_parts.append("full body shot, professional pose, fashion photography")
        
        return ", ".join(prompt_parts)
    
    async def generate_avatar_variants(
        self,
        twin_id: str,
        variant_styles: List[str],
        count_per_style: int = 1
    ) -> List[str]:
        """
        Generate multiple style variants of a digital twin using Gemini.
        """
        twin = await self.get_twin(twin_id)
        if not twin:
            return []
        
        variant_urls = []
        
        for idx, style_desc in enumerate(variant_styles):
            prompt = f"{self._build_avatar_prompt(twin, {})} in {style_desc} style"
            
            for i in range(count_per_style):
                try:
                    variant_url = await self._generate_image(
                        prompt, 
                        f"variant-{twin_id}-{idx}-{i}"
                    )
                    if variant_url:
                        variant_urls.append(variant_url)
                except Exception as e:
                    print(f"Error generating variant: {str(e)[:50]}")
        
        # Update twin with variants
        if variant_urls:
            try:
                twins_collection = self.db["digital_twins"]
                await twins_collection.update_one(
                    {"twin_id": twin_id},
                    {
                        "$push": {"avatar_variants": {"$each": variant_urls}},
                        "$set": {"updated_at": datetime.now(timezone.utc)}
                    }
                )
            except Exception:
                pass
        
        return variant_urls
    
    async def create_virtual_photoshoot(
        self,
        twin_id: str,
        client_id: str,
        client_name: str,
        concept: str,
        style: TwinStyle,
        background_setting: str,
        outfit_description: str,
        poses: List[str],
        num_images: int = 5
    ) -> VirtualPhotoshoot:
        """
        Create a virtual photoshoot with a digital twin.
        Zero travel costs, instant delivery.
        """
        photoshoot_id = str(uuid.uuid4())
        
        twin = await self.get_twin(twin_id)
        if not twin:
            raise ValueError("Digital twin not found")
        
        photoshoot = VirtualPhotoshoot(
            photoshoot_id=photoshoot_id,
            twin_id=twin_id,
            client_id=client_id,
            client_name=client_name,
            concept=concept,
            style=style,
            background_setting=background_setting,
            outfit_description=outfit_description,
            poses=poses,
            images_requested=num_images,
            price_per_image=50.0,
            total_price=num_images * 50.0
        )
        
        # Generate photoshoot images
        photoshoot = await self._execute_virtual_photoshoot(photoshoot, twin)
        
        # Save to database
        try:
            photoshoots_collection = self.db["virtual_photoshoots"]
            await photoshoots_collection.insert_one(photoshoot.dict())
        except Exception:
            pass
        
        # Update twin stats
        try:
            twins_collection = self.db["digital_twins"]
            await twins_collection.update_one(
                {"twin_id": twin_id},
                {
                    "$inc": {
                        "total_campaigns": 1,
                        "total_revenue": photoshoot.total_price
                    },
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
        except Exception:
            pass
        
        return photoshoot
    
    async def _execute_virtual_photoshoot(
        self,
        photoshoot: VirtualPhotoshoot,
        twin: DigitalTwinProfile
    ) -> VirtualPhotoshoot:
        """
        Execute a virtual photoshoot by generating images using Gemini.
        """
        photoshoot.status = "generating"
        
        base_prompt = f"""
        Professional {photoshoot.style.value} fashion photoshoot:
        Concept: {photoshoot.concept}
        Setting: {photoshoot.background_setting}
        Outfit: {photoshoot.outfit_description}
        Model features: {json.dumps(twin.preserved_features)}
        High quality, editorial photography, professional lighting
        """
        
        generated_images = []
        
        for i, pose in enumerate(photoshoot.poses[:photoshoot.images_requested]):
            prompt = f"{base_prompt}, Pose: {pose}"
            
            try:
                image_url = await self._generate_image(
                    prompt, 
                    f"photoshoot-{photoshoot.photoshoot_id}-{i}"
                )
                
                if image_url:
                    generated_images.append({
                        "image_id": str(uuid.uuid4()),
                        "image_url": image_url,
                        "pose": pose,
                        "index": i,
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    })
                    
            except Exception as e:
                generated_images.append({
                    "image_id": str(uuid.uuid4()),
                    "error": str(e)[:100],
                    "pose": pose,
                    "index": i
                })
        
        photoshoot.images = generated_images
        photoshoot.images_generated = len([img for img in generated_images if "image_url" in img])
        photoshoot.status = "completed" if photoshoot.images_generated > 0 else "failed"
        photoshoot.completed_at = datetime.now(timezone.utc)
        
        return photoshoot
    
    async def create_twin_license(
        self,
        twin_id: str,
        licensee_id: str,
        licensee_name: str,
        license_type: LicenseType,
        usage_contexts: List[UsageContext],
        duration_days: int = 365,
        auto_renewal: bool = False
    ) -> TwinLicense:
        """
        Create a license for using a digital twin.
        """
        twin = await self.get_twin(twin_id)
        if not twin:
            raise ValueError("Digital twin not found")
        
        # Calculate pricing
        base_fee = twin.base_license_price
        if license_type == LicenseType.EXCLUSIVE:
            base_fee *= twin.exclusive_multiplier
        elif license_type == LicenseType.LIMITED:
            base_fee *= 0.5
        elif license_type == LicenseType.TRIAL:
            base_fee = 0
            duration_days = min(duration_days, 30)
        
        # Adjust for usage contexts
        context_multiplier = len(usage_contexts) * 0.1 + 1.0
        license_fee = base_fee * context_multiplier * (duration_days / 365)
        
        license = TwinLicense(
            license_id=str(uuid.uuid4()),
            twin_id=twin_id,
            licensee_id=licensee_id,
            licensee_name=licensee_name,
            license_type=license_type,
            usage_contexts=usage_contexts,
            duration_days=duration_days,
            end_date=datetime.now(timezone.utc) + timedelta(days=duration_days),
            license_fee=round(license_fee, 2),
            usage_fee_per_use=twin.usage_rate_per_campaign,
            revenue_share_percent=10.0 if license_type == LicenseType.EXCLUSIVE else 15.0,
            auto_renewal=auto_renewal
        )
        
        # Save to database
        try:
            licenses_collection = self.db["twin_licenses"]
            await licenses_collection.insert_one(license.dict())
        except Exception:
            pass
        
        return license
    
    async def create_ar_tryon_asset(
        self,
        twin_id: str,
        asset_type: str,
        asset_name: str,
        product_data: Dict[str, Any]
    ) -> ARTryOnAsset:
        """
        Create an AR try-on compatible asset for the digital twin using Gemini.
        """
        twin = await self.get_twin(twin_id)
        if not twin or not twin.ar_compatible:
            raise ValueError("Twin not found or not AR compatible")
        
        # Generate AR preview image
        prompt = f"""
        AR try-on preview for {asset_type}: {asset_name}
        {product_data.get('description', '')}
        Clean product shot, transparent background, high quality
        """
        
        preview_url = await self._generate_image(prompt, f"ar-asset-{twin_id}-{asset_name[:10]}")
        
        asset = ARTryOnAsset(
            asset_id=str(uuid.uuid4()),
            twin_id=twin_id,
            asset_type=asset_type,
            asset_name=asset_name,
            preview_url=preview_url,
            compatible_platforms=["instagram_ar", "snapchat_lens", "web_ar"]
        )
        
        # Save to database
        try:
            ar_assets_collection = self.db["ar_tryon_assets"]
            await ar_assets_collection.insert_one(asset.dict())
        except Exception:
            pass
        
        return asset
    
    async def create_metaverse_avatar(
        self,
        twin_id: str,
        platform: str,
        animations: List[str] = None,
        wearables: List[str] = None
    ) -> MetaverseAvatar:
        """
        Create a metaverse-compatible avatar from a digital twin.
        """
        twin = await self.get_twin(twin_id)
        if not twin or not twin.metaverse_compatible:
            raise ValueError("Twin not found or not metaverse compatible")
        
        avatar = MetaverseAvatar(
            avatar_id=str(uuid.uuid4()),
            twin_id=twin_id,
            platform=platform,
            animations=animations or ["idle", "walk", "wave", "pose"],
            wearables=wearables or [],
            compatible=True
        )
        
        # Save to database
        try:
            metaverse_collection = self.db["metaverse_avatars"]
            await metaverse_collection.insert_one(avatar.dict())
        except Exception:
            pass
        
        return avatar
    
    async def get_twin(self, twin_id: str) -> Optional[DigitalTwinProfile]:
        """
        Get a digital twin by ID.
        """
        try:
            twins_collection = self.db["digital_twins"]
            twin_data = await twins_collection.find_one({"twin_id": twin_id})
            if twin_data:
                twin_data.pop("_id", None)
                return DigitalTwinProfile(**twin_data)
        except Exception:
            pass
        return None
    
    async def get_twins_by_model(self, model_id: str) -> List[DigitalTwinProfile]:
        """
        Get all digital twins for a model.
        """
        try:
            twins_collection = self.db["digital_twins"]
            twins = await twins_collection.find({"model_id": model_id}).to_list(100)
            return [DigitalTwinProfile(**{k: v for k, v in t.items() if k != "_id"}) for t in twins]
        except Exception:
            return []
    
    async def get_twins_by_agency(self, agency_id: str) -> List[DigitalTwinProfile]:
        """
        Get all digital twins for an agency.
        """
        try:
            twins_collection = self.db["digital_twins"]
            twins = await twins_collection.find({"agency_id": agency_id}).to_list(100)
            return [DigitalTwinProfile(**{k: v for k, v in t.items() if k != "_id"}) for t in twins]
        except Exception:
            return []
    
    async def get_twin_analytics(self, twin_id: str) -> Dict[str, Any]:
        """
        Get analytics for a digital twin.
        """
        twin = await self.get_twin(twin_id)
        if not twin:
            return {}
        
        # Get license data
        try:
            licenses_collection = self.db["twin_licenses"]
            licenses = await licenses_collection.find({"twin_id": twin_id}).to_list(100)
            active_licenses = len([lic for lic in licenses if lic.get("status") == "active"])
            total_license_revenue = sum(lic.get("license_fee", 0) for lic in licenses)
        except Exception:
            active_licenses = 0
            total_license_revenue = 0
        
        # Get photoshoot data
        try:
            photoshoots_collection = self.db["virtual_photoshoots"]
            photoshoots = await photoshoots_collection.find({"twin_id": twin_id}).to_list(100)
            total_photoshoots = len(photoshoots)
            photoshoot_revenue = sum(p.get("total_price", 0) for p in photoshoots)
        except Exception:
            total_photoshoots = 0
            photoshoot_revenue = 0
        
        return {
            "twin_id": twin_id,
            "model_name": twin.model_name,
            "status": twin.status.value,
            "total_campaigns": twin.total_campaigns,
            "total_revenue": twin.total_revenue,
            "views": twin.views,
            "active_licenses": active_licenses,
            "total_license_revenue": total_license_revenue,
            "total_photoshoots": total_photoshoots,
            "photoshoot_revenue": photoshoot_revenue,
            "ar_compatible": twin.ar_compatible,
            "metaverse_compatible": twin.metaverse_compatible,
            "created_at": twin.created_at.isoformat()
        }
    
    async def get_ai_recommendations(self, twin_id: str) -> Dict[str, Any]:
        """
        Get AI-powered recommendations for maximizing twin revenue.
        """
        twin = await self.get_twin(twin_id)
        if not twin:
            return {}
        
        analytics = await self.get_twin_analytics(twin_id)
        
        system_message = """You are a digital asset monetization expert.
        Analyze digital twin performance and provide revenue maximization recommendations."""
        
        chat = self._get_chat(f"twin-recs-{twin_id}", system_message)
        
        prompt = f"""Analyze this digital twin and provide revenue recommendations:

Twin Data:
- Status: {twin.status.value}
- Type: {twin.twin_type.value}
- Style: {twin.style.value}
- AR Compatible: {twin.ar_compatible}
- Metaverse Compatible: {twin.metaverse_compatible}
- Total Campaigns: {analytics.get('total_campaigns', 0)}
- Total Revenue: ${analytics.get('total_revenue', 0)}
- Active Licenses: {analytics.get('active_licenses', 0)}

Provide JSON response:
{{
    "revenue_potential": "high|medium|low",
    "recommended_uses": ["use1", "use2"],
    "pricing_suggestions": ["suggestion1", "suggestion2"],
    "marketing_tips": ["tip1", "tip2"],
    "expansion_opportunities": ["opportunity1", "opportunity2"],
    "estimated_monthly_revenue": <amount>
}}"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            recommendations = json.loads(json_str)
            recommendations["twin_id"] = twin_id
            recommendations["generated_at"] = datetime.now(timezone.utc).isoformat()
            return recommendations
        except (json.JSONDecodeError, KeyError):
            return {
                "twin_id": twin_id,
                "error": "Unable to generate recommendations",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }


# Singleton instance
_twin_service_instance = None

def get_digital_twin_service(db) -> DigitalTwinService:
    global _twin_service_instance
    if _twin_service_instance is None:
        _twin_service_instance = DigitalTwinService(db)
    return _twin_service_instance
