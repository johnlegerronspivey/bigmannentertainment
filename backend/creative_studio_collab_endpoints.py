"""
Creative Studio Collaboration & AI Assets - API Endpoints
WebSocket for real-time collaboration + REST for activity, versions, AI text/palettes/layouts
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List
from pydantic import BaseModel

from creative_studio_collab_service import get_collab_service
from creative_studio_ai_service import get_ai_assets_service

router = APIRouter(prefix="/creative-studio/collab", tags=["Creative Studio Collaboration"])
ai_router = APIRouter(prefix="/creative-studio/ai-assets", tags=["Creative Studio AI Assets"])


# ==================== WebSocket ====================

@router.websocket("/ws/{project_id}")
async def collaboration_websocket(websocket: WebSocket, project_id: str,
                                   user_id: str = "user_001", user_name: str = "User"):
    """WebSocket endpoint for real-time collaboration"""
    service = get_collab_service()
    if not service:
        await websocket.close(code=1011, reason="Service unavailable")
        return

    await service.connect(project_id, user_id, user_name, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "cursor_move":
                await service.handle_cursor_move(
                    project_id, user_id, data.get("x", 0), data.get("y", 0))
            elif msg_type == "element_update":
                await service.handle_element_update(
                    project_id, user_id, data.get("element", {}))
            elif msg_type == "element_add":
                await service.handle_element_add(
                    project_id, user_id, data.get("element", {}))
            elif msg_type == "element_delete":
                await service.handle_element_delete(
                    project_id, user_id, data.get("element_id", ""))
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await service.disconnect(project_id, user_id)
    except Exception:
        await service.disconnect(project_id, user_id)


# ==================== Activity Feed ====================

@router.get("/activity/{project_id}")
async def get_activity_feed(project_id: str, limit: int = Query(default=50, le=200)):
    """Get activity feed for a project"""
    service = get_collab_service()
    if not service:
        raise HTTPException(status_code=503, detail="Collaboration service unavailable")
    activities = await service.get_activity_feed(project_id, limit)
    return {"activities": activities, "total": len(activities)}


@router.get("/presence/{project_id}")
async def get_presence(project_id: str):
    """Get currently online users in a project"""
    service = get_collab_service()
    if not service:
        raise HTTPException(status_code=503, detail="Collaboration service unavailable")
    users = service.get_online_users(project_id)
    return {"online_users": users, "count": len(users)}


# ==================== Version Management ====================

@router.get("/versions/{project_id}")
async def get_versions(project_id: str):
    """Get version history for a project"""
    service = get_collab_service()
    if not service:
        raise HTTPException(status_code=503, detail="Collaboration service unavailable")
    versions = await service.get_versions(project_id)
    return {"versions": versions, "total": len(versions)}


class RestoreVersionRequest(BaseModel):
    version_id: str
    user_id: str = "user_001"


@router.post("/versions/{project_id}/restore")
async def restore_version(project_id: str, request: RestoreVersionRequest):
    """Restore a project to a previous version"""
    service = get_collab_service()
    if not service:
        raise HTTPException(status_code=503, detail="Collaboration service unavailable")
    result = await service.restore_version(project_id, request.version_id, request.user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Version not found")
    return result


# ==================== Comments ====================

@router.get("/comments/{project_id}")
async def get_comments(project_id: str):
    """Get all comments for a project"""
    service = get_collab_service()
    if not service:
        raise HTTPException(status_code=503, detail="Collaboration service unavailable")
    comments = await service.get_comments(project_id)
    return {"comments": comments, "total": len(comments)}


class AddCommentRequest(BaseModel):
    content: str
    user_id: str = "user_001"
    user_name: str = "User"
    position: Optional[dict] = None


@router.post("/comments/{project_id}")
async def add_comment(project_id: str, request: AddCommentRequest):
    """Add a comment to a project"""
    service = get_collab_service()
    if not service:
        raise HTTPException(status_code=503, detail="Collaboration service unavailable")
    comment = await service.add_comment(
        project_id, request.user_id, request.user_name,
        request.content, request.position)
    if not comment:
        raise HTTPException(status_code=404, detail="Project not found")
    return comment


class ResolveCommentRequest(BaseModel):
    user_id: str = "user_001"


@router.post("/comments/{project_id}/{comment_id}/resolve")
async def resolve_comment(project_id: str, comment_id: str, request: ResolveCommentRequest):
    """Resolve a comment"""
    service = get_collab_service()
    if not service:
        raise HTTPException(status_code=503, detail="Collaboration service unavailable")
    ok = await service.resolve_comment(project_id, comment_id, request.user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"success": True}


# ==================== AI Text Generation ====================

class GenerateTextRequest(BaseModel):
    prompt: str
    text_type: str = "headline"  # headline, caption, tagline, description, cta, hashtags
    tone: str = "professional"
    brand_context: str = ""
    count: int = 5


@ai_router.post("/generate-text")
async def generate_text(request: GenerateTextRequest):
    """Generate text content using AI"""
    service = get_ai_assets_service()
    if not service:
        raise HTTPException(status_code=503, detail="AI Assets service unavailable")
    return await service.generate_text(
        request.prompt, request.text_type, request.tone,
        request.brand_context, request.count)


# ==================== AI Color Palette ====================

class GeneratePaletteRequest(BaseModel):
    prompt: str
    mood: str = "modern"  # modern, warm, cool, luxury, playful, corporate
    count: int = 5


@ai_router.post("/generate-palette")
async def generate_palette(request: GeneratePaletteRequest):
    """Generate a color palette using AI"""
    service = get_ai_assets_service()
    if not service:
        raise HTTPException(status_code=503, detail="AI Assets service unavailable")
    return await service.generate_color_palette(request.prompt, request.mood, request.count)


# ==================== AI Layout Suggestions ====================

class SuggestLayoutsRequest(BaseModel):
    content_type: str = "promotional"
    platform: str = "instagram_post"
    element_count: int = 3


@ai_router.post("/suggest-layouts")
async def suggest_layouts(request: SuggestLayoutsRequest):
    """Get AI-suggested design layouts"""
    service = get_ai_assets_service()
    if not service:
        raise HTTPException(status_code=503, detail="AI Assets service unavailable")
    return await service.suggest_layouts(request.content_type, request.platform, request.element_count)


# ==================== Smart Resize ====================

class SmartResizeRequest(BaseModel):
    project_id: str
    target_platforms: List[str]


@ai_router.post("/smart-resize")
async def smart_resize(request: SmartResizeRequest):
    """Generate smart-resized versions for multiple platforms"""
    service = get_ai_assets_service()
    if not service:
        raise HTTPException(status_code=503, detail="AI Assets service unavailable")
    result = await service.smart_resize(request.project_id, request.target_platforms)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ==================== Health ====================

@router.get("/health")
async def collab_health():
    return {"status": "healthy", "service": "Creative Studio Collaboration"}


@ai_router.get("/health")
async def ai_assets_health():
    return {"status": "healthy", "service": "Creative Studio AI Assets"}
