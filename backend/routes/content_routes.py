"""
User Content Uploads & Management - CRUD for creator content (audio, video, images)
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
import uuid
import os
import shutil
from pathlib import Path
from config.database import db
from auth.service import get_current_user

router = APIRouter(prefix="/user-content", tags=["Content Management"])

UPLOAD_DIR = Path("/app/uploads/content")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "video": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
}
ALL_ALLOWED = [ext for exts in ALLOWED_TYPES.values() for ext in exts]
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def get_content_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    for ctype, exts in ALLOWED_TYPES.items():
        if ext in exts:
            return ctype
    return "other"


def serialize_content(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    for key in ["created_at", "updated_at"]:
        if key in doc and isinstance(doc[key], datetime):
            doc[key] = doc[key].isoformat()
    return doc


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    visibility: Optional[str] = None


@router.post("/upload")
async def upload_content(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    tags: str = Form(""),
    visibility: str = Form("public"),
    current_user=Depends(get_current_user),
):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    ext = Path(file.filename).suffix.lower()
    if ext not in ALL_ALLOWED:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALL_ALLOWED)}")

    file_id = str(uuid.uuid4())
    safe_name = f"{file_id}{ext}"
    file_path = UPLOAD_DIR / safe_name

    size = 0
    with open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 256):
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail="File too large. Max 100MB.")
            f.write(chunk)

    content_type = get_content_type(file.filename)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    content_doc = {
        "user_id": user_id,
        "file_id": file_id,
        "original_filename": file.filename,
        "stored_filename": safe_name,
        "title": title or Path(file.filename).stem,
        "description": description,
        "content_type": content_type,
        "file_extension": ext,
        "file_size": size,
        "tags": tag_list,
        "visibility": visibility if visibility in ["public", "private", "subscribers"] else "public",
        "stats": {"views": 0, "downloads": 0, "likes": 0},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = await db.user_content.insert_one(content_doc)
    content_doc["_id"] = result.inserted_id

    # Update creator profile stats
    await db.creator_profiles.update_one(
        {"user_id": user_id},
        {"$inc": {"stats.total_assets": 1}},
    )

    return serialize_content(content_doc)


@router.get("")
async def list_my_content(
    content_type: Optional[str] = None,
    visibility: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user=Depends(get_current_user),
):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    query = {"user_id": user_id}
    if content_type and content_type in ALLOWED_TYPES:
        query["content_type"] = content_type
    if visibility:
        query["visibility"] = visibility
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search]}},
        ]

    cursor = db.user_content.find(query).sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        items.append(serialize_content(doc))
    total = await db.user_content.count_documents(query)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


MIME_MAP = {
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".flac": "audio/flac",
    ".aac": "audio/aac", ".ogg": "audio/ogg", ".m4a": "audio/mp4",
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska", ".webm": "video/webm",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
}


@router.get("/file/{file_id}")
async def serve_file(file_id: str):
    """Serve an uploaded content file by its file_id for preview/playback."""
    doc = await db.user_content.find_one({"file_id": file_id}, {"_id": 0, "stored_filename": 1, "file_extension": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    file_path = UPLOAD_DIR / doc["stored_filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File missing from storage")
    media_type = MIME_MAP.get(doc.get("file_extension", ""), "application/octet-stream")
    return FileResponse(file_path, media_type=media_type)


@router.get("/{content_id}")
async def get_content(content_id: str, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    try:
        doc = await db.user_content.find_one({"_id": ObjectId(content_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid content ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Content not found")
    return serialize_content(doc)


@router.put("/{content_id}")
async def update_content(content_id: str, data: ContentUpdate, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    try:
        doc = await db.user_content.find_one({"_id": ObjectId(content_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid content ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Content not found")

    updates = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    if "visibility" in updates and updates["visibility"] not in ["public", "private", "subscribers"]:
        raise HTTPException(status_code=400, detail="Invalid visibility option")
    updates["updated_at"] = datetime.now(timezone.utc)

    await db.user_content.update_one({"_id": ObjectId(content_id)}, {"$set": updates})
    updated = await db.user_content.find_one({"_id": ObjectId(content_id)})
    return serialize_content(updated)


@router.delete("/{content_id}")
async def delete_content(content_id: str, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    try:
        doc = await db.user_content.find_one({"_id": ObjectId(content_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid content ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Content not found")

    # Remove file from disk
    file_path = UPLOAD_DIR / doc["stored_filename"]
    if file_path.exists():
        os.remove(file_path)

    await db.user_content.delete_one({"_id": ObjectId(content_id)})

    # Update creator profile stats
    await db.creator_profiles.update_one(
        {"user_id": user_id},
        {"$inc": {"stats.total_assets": -1}},
    )

    return {"message": "Content deleted successfully"}


@router.get("/public/browse")
async def browse_public_content(
    content_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    query = {"visibility": "public"}
    if content_type and content_type in ALLOWED_TYPES:
        query["content_type"] = content_type
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search]}},
        ]

    cursor = db.user_content.find(query).sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        items.append(serialize_content(doc))
    total = await db.user_content.count_documents(query)
    return {"items": items, "total": total}
