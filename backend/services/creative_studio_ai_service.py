"""
Creative Studio AI Assets Service
Advanced AI-powered content generation: text, color palettes, layout suggestions, smart resize
"""

import os
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def _get_gemini_model():
    """Get Gemini model for text generation"""
    try:
        import google.generativeai as genai
        if not GOOGLE_API_KEY:
            return None
        genai.configure(api_key=GOOGLE_API_KEY)
        return genai.GenerativeModel('gemini-2.0-flash-exp')
    except Exception:
        return None


class AIAssetsService:
    """AI-powered creative asset generation"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.generations_collection = db.creative_studio_ai_text_generations

    async def generate_text(self, prompt: str, text_type: str = "headline",
                            tone: str = "professional", brand_context: str = "",
                            count: int = 5) -> Dict[str, Any]:
        """Generate text content using Gemini AI"""
        model = _get_gemini_model()

        type_instructions = {
            "headline": "Generate short, punchy headlines (5-10 words each)",
            "caption": "Generate social media captions (1-3 sentences each)",
            "tagline": "Generate brand taglines (3-8 words each)",
            "description": "Generate product/service descriptions (2-4 sentences each)",
            "cta": "Generate call-to-action button text (2-5 words each)",
            "hashtags": "Generate relevant hashtag sets (5-8 hashtags per set)"
        }

        instruction = type_instructions.get(text_type, type_instructions["headline"])
        brand_note = f"\nBrand context: {brand_context}" if brand_context else ""
        tone_note = f"\nTone: {tone}"

        full_prompt = f"""{instruction}
Topic/Theme: {prompt}{brand_note}{tone_note}
Generate exactly {count} options. Return as a JSON array of strings. Only output the JSON array, nothing else."""

        try:
            if model:
                response = model.generate_content(full_prompt)
                text = response.text.strip()
                # Parse JSON from response
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                results = json.loads(text.strip())
                if isinstance(results, list):
                    results = results[:count]
                else:
                    results = [str(results)]
            else:
                results = self._fallback_text(prompt, text_type, count)
        except Exception as e:
            print(f"AI text generation error: {e}")
            results = self._fallback_text(prompt, text_type, count)

        record = {
            "prompt": prompt,
            "text_type": text_type,
            "tone": tone,
            "results": results,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await self.generations_collection.insert_one(record)

        return {"results": results, "text_type": text_type, "prompt": prompt}

    def _fallback_text(self, prompt: str, text_type: str, count: int) -> List[str]:
        """Rule-based fallback when AI is unavailable"""
        words = prompt.split()[:4]
        base = " ".join(words).title()
        fallbacks = {
            "headline": [
                f"{base}: The Future Is Now",
                f"Discover {base} Today",
                f"Unlock the Power of {base}",
                f"{base} — Reimagined",
                f"The Art of {base}"
            ],
            "caption": [
                f"Introducing our latest {base.lower()} collection. Bold, beautiful, and built for you.",
                f"Step into the spotlight with {base.lower()}. Your audience is waiting.",
                f"Every great story starts here. Welcome to {base.lower()}.",
                f"Elevate your brand with {base.lower()}. #NewBeginnings",
                f"Create. Inspire. Transform. That's the {base.lower()} way."
            ],
            "tagline": [
                f"{base} — Beyond Ordinary",
                f"Think {base}. Think Big.",
                f"{base}. Elevated.",
                f"The {base} Experience",
                f"{base}. Redefined."
            ],
            "cta": ["Get Started", "Learn More", "Try It Free", "Join Now", "Explore"],
            "hashtags": [
                f"#{base.replace(' ','')} #Creative #Design #Brand #Innovation",
                f"#{base.replace(' ','')} #DigitalArt #ContentCreation #Marketing",
                f"#{base.replace(' ','')} #Branding #Agency #Social #Trending"
            ],
            "description": [
                f"{base} is a comprehensive solution designed for modern creatives and agencies.",
                f"Transform your workflow with {base.lower()} — where innovation meets execution.",
                f"Built for teams that demand more, {base.lower()} delivers on every front."
            ]
        }
        return fallbacks.get(text_type, fallbacks["headline"])[:count]

    async def generate_color_palette(self, prompt: str, mood: str = "modern",
                                     count: int = 5) -> Dict[str, Any]:
        """Generate a color palette using AI"""
        model = _get_gemini_model()

        full_prompt = f"""Generate a {mood} color palette for: {prompt}
Return exactly {count} colors as a JSON array of objects with keys: "name", "hex", "usage".
Usage should be one of: primary, secondary, accent, background, text.
Only output the JSON array, nothing else."""

        try:
            if model:
                response = model.generate_content(full_prompt)
                text = response.text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                colors = json.loads(text.strip())
                if isinstance(colors, list):
                    colors = colors[:count]
                else:
                    colors = self._fallback_palette(mood, count)
            else:
                colors = self._fallback_palette(mood, count)
        except Exception as e:
            print(f"AI palette generation error: {e}")
            colors = self._fallback_palette(mood, count)

        return {"colors": colors, "mood": mood, "prompt": prompt}

    def _fallback_palette(self, mood: str, count: int) -> List[Dict]:
        palettes = {
            "modern": [
                {"name": "Midnight", "hex": "#1a1a2e", "usage": "primary"},
                {"name": "Electric Violet", "hex": "#8b5cf6", "usage": "secondary"},
                {"name": "Hot Pink", "hex": "#ec4899", "usage": "accent"},
                {"name": "Soft Gray", "hex": "#f1f5f9", "usage": "background"},
                {"name": "Dark Slate", "hex": "#334155", "usage": "text"}
            ],
            "warm": [
                {"name": "Sunset Orange", "hex": "#f97316", "usage": "primary"},
                {"name": "Coral", "hex": "#fb7185", "usage": "secondary"},
                {"name": "Gold", "hex": "#f59e0b", "usage": "accent"},
                {"name": "Cream", "hex": "#fef3c7", "usage": "background"},
                {"name": "Walnut", "hex": "#78350f", "usage": "text"}
            ],
            "cool": [
                {"name": "Ocean Blue", "hex": "#3b82f6", "usage": "primary"},
                {"name": "Teal", "hex": "#14b8a6", "usage": "secondary"},
                {"name": "Sky", "hex": "#38bdf8", "usage": "accent"},
                {"name": "Ice", "hex": "#f0f9ff", "usage": "background"},
                {"name": "Navy", "hex": "#1e3a5f", "usage": "text"}
            ],
            "luxury": [
                {"name": "Black", "hex": "#0a0a0a", "usage": "primary"},
                {"name": "Gold", "hex": "#d4af37", "usage": "secondary"},
                {"name": "Champagne", "hex": "#f7e7ce", "usage": "accent"},
                {"name": "Ivory", "hex": "#fffff0", "usage": "background"},
                {"name": "Charcoal", "hex": "#36454f", "usage": "text"}
            ]
        }
        return palettes.get(mood, palettes["modern"])[:count]

    async def suggest_layouts(self, content_type: str, platform: str = "instagram_post",
                              element_count: int = 3) -> Dict[str, Any]:
        """Suggest design layouts based on content type and platform, using AI when available"""
        platform_sizes = {
            "instagram_post": {"width": 1080, "height": 1080},
            "instagram_story": {"width": 1080, "height": 1920},
            "twitter_post": {"width": 1200, "height": 675},
            "facebook_post": {"width": 1200, "height": 630},
            "youtube_thumbnail": {"width": 1280, "height": 720},
            "linkedin_post": {"width": 1200, "height": 627},
            "linkedin_banner": {"width": 1584, "height": 396},
            "pinterest_pin": {"width": 1000, "height": 1500},
            "tiktok_video": {"width": 1080, "height": 1920},
            "twitter_header": {"width": 1500, "height": 500},
        }
        size = platform_sizes.get(platform, {"width": 1080, "height": 1080})
        w, h = size["width"], size["height"]

        # Try AI-powered layout suggestions first
        model = _get_gemini_model()
        ai_layouts = None
        if model and content_type:
            try:
                ai_prompt = f"""Suggest 2 creative layout ideas for a {content_type} design on {platform.replace('_',' ')} ({w}x{h}px).
For each layout, give: name, description (1 sentence), and a color scheme (3 hex colors).
Return JSON array: [{{"name":"...", "description":"...", "colors":["#hex1","#hex2","#hex3"]}}]
Only output the JSON array."""
                response = model.generate_content(ai_prompt)
                text = response.text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                ai_data = json.loads(text.strip())
                if isinstance(ai_data, list) and len(ai_data) > 0:
                    ai_layouts = ai_data[:2]
            except Exception as e:
                print(f"AI layout suggestion error: {e}")

        layouts = self._generate_layouts(content_type, w, h, element_count, ai_hints=ai_layouts)
        return {"layouts": layouts, "platform": platform, "canvas": size}

    def _generate_layouts(self, content_type: str, w: int, h: int,
                          element_count: int, ai_hints: list = None) -> List[Dict]:
        """Generate layout suggestions with optional AI-generated hints"""
        layouts = []

        # If AI gave us hints, use them as the first layouts
        if ai_hints:
            for hint in ai_hints:
                colors = hint.get("colors", ["#1a1a2e", "#8b5cf6", "#ffffff"])
                bg = colors[0] if len(colors) > 0 else "#1a1a2e"
                accent = colors[1] if len(colors) > 1 else "#8b5cf6"
                text_c = colors[2] if len(colors) > 2 else "#ffffff"
                layouts.append({
                    "name": hint.get("name", "AI Layout"),
                    "description": hint.get("description", "AI-suggested layout"),
                    "ai_generated": True,
                    "elements": [
                        {"type": "rect", "x": 0, "y": 0, "width": w, "height": h,
                         "style": {"backgroundColor": bg}},
                        {"type": "rect", "x": w * 0.08, "y": h * 0.12, "width": w * 0.35, "height": h * 0.04,
                         "style": {"backgroundColor": accent}},
                        {"type": "text", "x": w * 0.08, "y": h * 0.22, "width": w * 0.84, "height": h * 0.18,
                         "content": hint.get("name", "Headline"),
                         "style": {"fontSize": 48, "fontWeight": "bold", "color": text_c, "textAlign": "left"}},
                        {"type": "text", "x": w * 0.08, "y": h * 0.45, "width": w * 0.6, "height": h * 0.1,
                         "content": hint.get("description", "Description text"),
                         "style": {"fontSize": 20, "color": text_c, "textAlign": "left"}}
                    ]
                })

        # Layout 1: Centered Hero
        layouts.append({
            "name": "Centered Hero",
            "description": "Bold centered text with clean spacing",
            "elements": [
                {"type": "rect", "x": 0, "y": 0, "width": w, "height": h,
                 "style": {"backgroundColor": "#1a1a2e"}},
                {"type": "text", "x": w * 0.1, "y": h * 0.35, "width": w * 0.8, "height": h * 0.15,
                 "content": "Your Headline Here",
                 "style": {"fontSize": 48, "fontWeight": "bold", "color": "#ffffff", "textAlign": "center"}},
                {"type": "text", "x": w * 0.15, "y": h * 0.55, "width": w * 0.7, "height": h * 0.08,
                 "content": "Supporting description text goes here",
                 "style": {"fontSize": 20, "color": "#94a3b8", "textAlign": "center"}}
            ]
        })

        # Layout 2: Split Layout
        layouts.append({
            "name": "Split Layout",
            "description": "Image on one side, text on the other",
            "elements": [
                {"type": "rect", "x": 0, "y": 0, "width": w * 0.5, "height": h,
                 "style": {"backgroundColor": "#8b5cf6"}},
                {"type": "rect", "x": w * 0.5, "y": 0, "width": w * 0.5, "height": h,
                 "style": {"backgroundColor": "#f8fafc"}},
                {"type": "text", "x": w * 0.55, "y": h * 0.3, "width": w * 0.4, "height": h * 0.15,
                 "content": "Your Message",
                 "style": {"fontSize": 36, "fontWeight": "bold", "color": "#1e293b", "textAlign": "left"}},
                {"type": "text", "x": w * 0.55, "y": h * 0.5, "width": w * 0.4, "height": h * 0.1,
                 "content": "Add description here",
                 "style": {"fontSize": 16, "color": "#64748b", "textAlign": "left"}}
            ]
        })

        # Layout 3: Bold Typography
        layouts.append({
            "name": "Bold Typography",
            "description": "Large typography-focused design",
            "elements": [
                {"type": "rect", "x": 0, "y": 0, "width": w, "height": h,
                 "style": {"backgroundColor": "#0f172a"}},
                {"type": "text", "x": w * 0.05, "y": h * 0.15, "width": w * 0.9, "height": h * 0.3,
                 "content": "MAKE IT",
                 "style": {"fontSize": 72, "fontWeight": "bold", "color": "#f59e0b", "textAlign": "left"}},
                {"type": "text", "x": w * 0.05, "y": h * 0.45, "width": w * 0.9, "height": h * 0.3,
                 "content": "HAPPEN",
                 "style": {"fontSize": 72, "fontWeight": "bold", "color": "#ffffff", "textAlign": "left"}},
                {"type": "text", "x": w * 0.05, "y": h * 0.8, "width": w * 0.5, "height": h * 0.08,
                 "content": "yourwebsite.com",
                 "style": {"fontSize": 18, "color": "#64748b", "textAlign": "left"}}
            ]
        })

        # Layout 4: Minimal Card
        layouts.append({
            "name": "Minimal Card",
            "description": "Clean card design with accent line",
            "elements": [
                {"type": "rect", "x": 0, "y": 0, "width": w, "height": h,
                 "style": {"backgroundColor": "#ffffff"}},
                {"type": "rect", "x": w * 0.1, "y": h * 0.3, "width": w * 0.02, "height": h * 0.4,
                 "style": {"backgroundColor": "#8b5cf6"}},
                {"type": "text", "x": w * 0.18, "y": h * 0.32, "width": w * 0.7, "height": h * 0.15,
                 "content": "Clean Design",
                 "style": {"fontSize": 40, "fontWeight": "bold", "color": "#1e293b", "textAlign": "left"}},
                {"type": "text", "x": w * 0.18, "y": h * 0.5, "width": w * 0.65, "height": h * 0.15,
                 "content": "Simple and elegant layouts that let your content shine.",
                 "style": {"fontSize": 18, "color": "#64748b", "textAlign": "left"}}
            ]
        })

        # Layout 5: Gradient Overlay
        layouts.append({
            "name": "Gradient Overlay",
            "description": "Text over a gradient background — great for stories",
            "elements": [
                {"type": "rect", "x": 0, "y": 0, "width": w, "height": h,
                 "style": {"backgroundColor": "#0ea5e9"}},
                {"type": "rect", "x": 0, "y": h * 0.5, "width": w, "height": h * 0.5,
                 "style": {"backgroundColor": "#1e293b", "opacity": 0.7}},
                {"type": "text", "x": w * 0.08, "y": h * 0.6, "width": w * 0.84, "height": h * 0.12,
                 "content": "Your Story",
                 "style": {"fontSize": 52, "fontWeight": "bold", "color": "#ffffff", "textAlign": "left"}},
                {"type": "text", "x": w * 0.08, "y": h * 0.75, "width": w * 0.7, "height": h * 0.08,
                 "content": "Tap to explore more",
                 "style": {"fontSize": 18, "color": "#cbd5e1", "textAlign": "left"}}
            ]
        })

        # Layout 6: Grid Showcase
        layouts.append({
            "name": "Grid Showcase",
            "description": "Multi-panel grid for product/portfolio display",
            "elements": [
                {"type": "rect", "x": 0, "y": 0, "width": w, "height": h,
                 "style": {"backgroundColor": "#f1f5f9"}},
                {"type": "rect", "x": w * 0.04, "y": h * 0.04, "width": w * 0.44, "height": h * 0.44,
                 "style": {"backgroundColor": "#e2e8f0", "borderRadius": 8}},
                {"type": "rect", "x": w * 0.52, "y": h * 0.04, "width": w * 0.44, "height": h * 0.44,
                 "style": {"backgroundColor": "#e2e8f0", "borderRadius": 8}},
                {"type": "rect", "x": w * 0.04, "y": h * 0.52, "width": w * 0.92, "height": h * 0.18,
                 "style": {"backgroundColor": "#1e293b", "borderRadius": 8}},
                {"type": "text", "x": w * 0.1, "y": h * 0.56, "width": w * 0.8, "height": h * 0.1,
                 "content": "Featured Collection",
                 "style": {"fontSize": 32, "fontWeight": "bold", "color": "#ffffff", "textAlign": "center"}},
                {"type": "text", "x": w * 0.08, "y": h * 0.78, "width": w * 0.84, "height": h * 0.06,
                 "content": "Shop the look — Limited edition",
                 "style": {"fontSize": 16, "color": "#64748b", "textAlign": "center"}}
            ]
        })

        return layouts

    async def smart_resize(self, project_id: str, target_platforms: List[str]) -> Dict[str, Any]:
        """Generate resized versions of a project for different platforms"""
        from creative_studio_service import get_creative_studio_service
        svc = get_creative_studio_service()
        if not svc:
            return {"error": "Service not available"}

        project = await svc.get_project(project_id)
        if not project:
            return {"error": "Project not found"}

        platform_sizes = {
            "instagram_post": {"width": 1080, "height": 1080},
            "instagram_story": {"width": 1080, "height": 1920},
            "twitter_post": {"width": 1200, "height": 675},
            "facebook_post": {"width": 1200, "height": 630},
            "youtube_thumbnail": {"width": 1280, "height": 720},
            "linkedin_post": {"width": 1200, "height": 627},
            "linkedin_banner": {"width": 1584, "height": 396},
            "pinterest_pin": {"width": 1000, "height": 1500},
        }

        resized = []
        orig_w, orig_h = project.width, project.height

        for platform in target_platforms:
            target = platform_sizes.get(platform)
            if not target:
                continue

            tw, th = target["width"], target["height"]
            scale_x = tw / orig_w
            scale_y = th / orig_h
            scale = min(scale_x, scale_y)

            offset_x = (tw - orig_w * scale) / 2
            offset_y = (th - orig_h * scale) / 2

            adapted_elements = []
            for el in project.elements:
                el_dict = el.dict() if hasattr(el, 'dict') else el
                new_el = {**el_dict}
                pos = new_el.get("position", {})
                size = new_el.get("size", {})
                new_el["position"] = {
                    "x": pos.get("x", 0) * scale + offset_x,
                    "y": pos.get("y", 0) * scale + offset_y
                }
                new_el["size"] = {
                    "width": size.get("width", 100) * scale,
                    "height": size.get("height", 100) * scale
                }
                # Scale font sizes in styles
                styles = new_el.get("styles", {})
                if "fontSize" in styles:
                    styles["fontSize"] = max(10, int(styles["fontSize"] * scale))
                    new_el["styles"] = styles
                adapted_elements.append(new_el)

            resized.append({
                "platform": platform,
                "width": tw,
                "height": th,
                "elements": adapted_elements
            })

        return {"resized_versions": resized, "original_size": {"width": orig_w, "height": orig_h}}


# Singleton
_ai_assets_service = None


def initialize_ai_assets_service(db: AsyncIOMotorDatabase) -> AIAssetsService:
    global _ai_assets_service
    _ai_assets_service = AIAssetsService(db)
    return _ai_assets_service


def get_ai_assets_service():
    return _ai_assets_service
