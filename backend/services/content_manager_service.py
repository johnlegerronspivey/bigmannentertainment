"""
Big Mann Entertainment - Content Manager Service
De-mocked: All data computed from real MongoDB collections (user_content, label_assets).
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from config.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    LIVE = "live"
    ARCHIVED = "archived"


class QualityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class ContentFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    MKV = "mkv"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"


class ContentMetadata(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: List[str] = Field(default_factory=list)
    genre: Optional[str] = None
    artist_name: Optional[str] = None
    album_name: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    language: Optional[str] = "en"
    copyright_info: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ContentAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content_type: ContentType
    status: ContentStatus
    format: ContentFormat
    quality_level: QualityLevel
    metadata: ContentMetadata
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    user_id: str
    folder_id: Optional[str] = None
    version: int = 1
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None


class ContentFolder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    parent_id: Optional[str] = None
    user_id: str
    color: Optional[str] = "#3B82F6"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Helpers ────────────────────────────────────────────────────
def _map_extension_to_type(ext: str) -> str:
    ext = (ext or "").lower().lstrip(".")
    audio = {"mp3", "wav", "flac", "aac", "ogg", "m4a"}
    video = {"mp4", "mov", "avi", "mkv", "webm"}
    image = {"jpg", "jpeg", "png", "gif", "webp", "heic", "bmp", "svg"}
    if ext in audio:
        return "audio"
    if ext in video:
        return "video"
    if ext in image:
        return "image"
    return "other"


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.1f} GB"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


class ContentManagerService:
    """Service computing content data from real MongoDB collections."""

    async def get_assets(self, user_id: str, folder_id: str = None,
                         content_type: ContentType = None,
                         status: ContentStatus = None,
                         limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        try:
            # Merge user_content + label_assets into a unified list
            assets = []

            # Query user_content
            async for doc in db.user_content.find({}, {"_id": 0}):
                ct = doc.get("content_type") or _map_extension_to_type(doc.get("file_extension", ""))
                assets.append({
                    "id": doc.get("file_id", ""),
                    "title": doc.get("title") or doc.get("original_filename", "Untitled"),
                    "content_type": ct,
                    "status": "live" if doc.get("visibility") == "public" else "draft",
                    "format": (doc.get("file_extension") or "").lstrip(".") or "unknown",
                    "quality_level": "high",
                    "file_size": doc.get("file_size", 0),
                    "tags": doc.get("tags", []),
                    "description": doc.get("description", ""),
                    "user_id": doc.get("user_id", ""),
                    "created_at": str(doc.get("created_at", "")),
                    "updated_at": str(doc.get("updated_at", "")),
                    "source": "user_content",
                })

            # Query label_assets
            async for doc in db.label_assets.find({}, {"_id": 0}):
                ct = doc.get("type", "audio")
                if ct in ("single", "album", "track"):
                    ct = "audio"
                assets.append({
                    "id": doc.get("asset_id", ""),
                    "title": doc.get("title", "Untitled"),
                    "content_type": ct,
                    "status": doc.get("status", "draft"),
                    "format": "audio",
                    "quality_level": "high",
                    "file_size": 0,
                    "tags": [],
                    "description": f"{doc.get('artist', '')} - {doc.get('genre', '')}",
                    "user_id": doc.get("created_by", ""),
                    "created_at": str(doc.get("created_at", "")),
                    "updated_at": str(doc.get("updated_at", "")),
                    "source": "label_assets",
                    "streams_total": doc.get("streams_total", 0),
                    "platforms": doc.get("platforms", []),
                    "isrc": doc.get("isrc", ""),
                })

            # Apply filters
            if content_type:
                ct_val = content_type.value if hasattr(content_type, 'value') else content_type
                assets = [a for a in assets if a["content_type"] == ct_val]
            if status:
                st_val = status.value if hasattr(status, 'value') else status
                assets = [a for a in assets if a["status"] == st_val]

            total = len(assets)
            paginated = assets[offset:offset + limit]

            return {
                "success": True,
                "data_source": "real",
                "assets": paginated,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.error(f"Error fetching assets: {e}")
            return {"success": False, "error": str(e), "assets": [], "total": 0}

    async def get_asset(self, asset_id: str, user_id: str) -> Dict[str, Any]:
        try:
            # Try user_content first
            doc = await db.user_content.find_one({"file_id": asset_id}, {"_id": 0})
            if doc:
                return {
                    "success": True,
                    "data_source": "real",
                    "asset": {
                        "id": doc.get("file_id"),
                        "title": doc.get("title", "Untitled"),
                        "content_type": doc.get("content_type", "other"),
                        "status": "live" if doc.get("visibility") == "public" else "draft",
                        "description": doc.get("description", ""),
                        "file_size": doc.get("file_size", 0),
                        "tags": doc.get("tags", []),
                    },
                }
            # Try label_assets
            doc = await db.label_assets.find_one({"asset_id": asset_id}, {"_id": 0})
            if doc:
                return {
                    "success": True,
                    "data_source": "real",
                    "asset": {
                        "id": doc.get("asset_id"),
                        "title": doc.get("title", "Untitled"),
                        "content_type": "audio",
                        "status": doc.get("status", "draft"),
                        "description": f"{doc.get('artist', '')} - {doc.get('genre', '')}",
                    },
                }
            return {"success": False, "error": "Asset not found"}
        except Exception as e:
            logger.error(f"Error fetching asset {asset_id}: {e}")
            return {"success": False, "error": str(e)}

    async def update_asset(self, asset_id: str, updates: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            result = await db.user_content.update_one({"file_id": asset_id}, {"$set": updates})
            if result.modified_count == 0:
                result = await db.label_assets.update_one({"asset_id": asset_id}, {"$set": updates})
            return {"success": True, "message": "Asset updated successfully"}
        except Exception as e:
            logger.error(f"Error updating asset {asset_id}: {e}")
            return {"success": False, "error": str(e)}

    async def delete_asset(self, asset_id: str, user_id: str) -> Dict[str, Any]:
        try:
            result = await db.user_content.delete_one({"file_id": asset_id})
            if result.deleted_count == 0:
                await db.label_assets.delete_one({"asset_id": asset_id})
            return {"success": True, "message": "Asset deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting asset {asset_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_folders(self, user_id: str, parent_id: str = None) -> Dict[str, Any]:
        """Build virtual folders from content types found in the DB."""
        try:
            type_pipeline = [
                {"$group": {"_id": "$content_type", "count": {"$sum": 1}}},
            ]
            colors = {"audio": "#10B981", "video": "#F59E0B", "image": "#8B5CF6", "document": "#3B82F6", "other": "#6B7280"}
            folders = []
            async for doc in db.user_content.aggregate(type_pipeline):
                ct = doc["_id"] or "other"
                folders.append({
                    "id": f"folder_{ct}",
                    "name": f"{ct.capitalize()} Files",
                    "description": f"{doc['count']} {ct} file(s)",
                    "user_id": user_id,
                    "color": colors.get(ct, "#3B82F6"),
                    "count": doc["count"],
                })

            # Add label_assets as a folder
            label_count = await db.label_assets.count_documents({})
            if label_count > 0:
                folders.append({
                    "id": "folder_label_assets",
                    "name": "Label Assets",
                    "description": f"{label_count} label-managed asset(s)",
                    "user_id": user_id,
                    "color": "#EF4444",
                    "count": label_count,
                })

            return {"success": True, "data_source": "real", "folders": folders}
        except Exception as e:
            logger.error(f"Error fetching folders: {e}")
            return {"success": False, "error": str(e), "folders": []}

    async def get_content_stats(self, user_id: str) -> Dict[str, Any]:
        try:
            uc_count = await db.user_content.count_documents({})
            la_count = await db.label_assets.count_documents({})
            total_assets = uc_count + la_count

            # By type from user_content
            type_pipeline = [{"$group": {"_id": "$content_type", "count": {"$sum": 1}}}]
            by_type = {}
            async for doc in db.user_content.aggregate(type_pipeline):
                by_type[doc["_id"] or "other"] = doc["count"]
            # Label assets are mostly audio
            by_type["audio"] = by_type.get("audio", 0) + la_count

            # By status
            by_status = {}
            # user_content: public = live, else draft
            public_count = await db.user_content.count_documents({"visibility": "public"})
            draft_count = uc_count - public_count
            # label_assets by status
            la_status_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
            async for doc in db.label_assets.aggregate(la_status_pipeline):
                st = doc["_id"] or "draft"
                if st == "released":
                    st = "live"
                by_status[st] = by_status.get(st, 0) + doc["count"]
            by_status["live"] = by_status.get("live", 0) + public_count
            by_status["draft"] = by_status.get("draft", 0) + draft_count

            # Total storage from user_content
            size_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$file_size"}}}]
            size_result = await db.user_content.aggregate(size_pipeline).to_list(1)
            total_bytes = size_result[0]["total"] if size_result else 0

            # This month stats
            month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_str = month_start.isoformat()
            this_month_uploaded = await db.user_content.count_documents({"created_at": {"$gte": month_str}})
            this_month_la = await db.label_assets.count_documents({"created_at": {"$gte": month_str}})

            return {
                "success": True,
                "data_source": "real",
                "stats": {
                    "total_assets": total_assets,
                    "by_type": by_type,
                    "by_status": by_status,
                    "total_size": _format_size(total_bytes),
                    "this_month": {
                        "uploaded": this_month_uploaded + this_month_la,
                        "approved": by_status.get("live", 0),
                        "distributed": la_count,
                    },
                },
            }
        except Exception as e:
            logger.error(f"Error fetching content stats: {e}")
            return {"success": False, "error": str(e)}

    async def search_content(self, query: str, user_id: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            q_lower = query.lower()
            results = []

            # Search user_content by title, description, tags
            async for doc in db.user_content.find({}, {"_id": 0}):
                title = (doc.get("title") or "").lower()
                desc = (doc.get("description") or "").lower()
                tags = [t.lower() for t in doc.get("tags", [])]
                if q_lower in title or q_lower in desc or any(q_lower in t for t in tags):
                    results.append({
                        "id": doc.get("file_id"),
                        "title": doc.get("title", "Untitled"),
                        "content_type": doc.get("content_type", "other"),
                        "status": "live" if doc.get("visibility") == "public" else "draft",
                        "relevance": 0.9 if q_lower in title else 0.7,
                    })

            # Search label_assets
            async for doc in db.label_assets.find({}, {"_id": 0}):
                title = (doc.get("title") or "").lower()
                artist = (doc.get("artist") or "").lower()
                genre = (doc.get("genre") or "").lower()
                if q_lower in title or q_lower in artist or q_lower in genre:
                    results.append({
                        "id": doc.get("asset_id"),
                        "title": doc.get("title", "Untitled"),
                        "content_type": "audio",
                        "status": doc.get("status", "draft"),
                        "relevance": 0.9 if q_lower in title else 0.7,
                    })

            results.sort(key=lambda x: x["relevance"], reverse=True)
            return {"success": True, "data_source": "real", "results": results, "total": len(results), "query": query}
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return {"success": False, "error": str(e), "results": []}


# Global instance
content_manager_service = ContentManagerService()
