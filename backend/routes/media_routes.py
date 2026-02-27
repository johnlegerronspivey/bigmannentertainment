"""Media management endpoints - upload, library, CRUD, search."""
import os
import uuid
import hashlib
import aiofiles
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from config.database import db
from auth.service import get_current_user
from models.core import User, MediaContent

router = APIRouter(tags=["Media"])

@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    price: float = Form(0.0),
    tags: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    allowed_types = {
        'audio': ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/flac', 'audio/aac'],
        'video': ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'],
        'image': ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    }
    
    # Determine content type based on MIME type
    content_type = None
    for type_category, mime_types in allowed_types.items():
        if file.content_type in mime_types:
            content_type = type_category
            break
    
    if not content_type:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Create directory if it doesn't exist
    content_dir = uploads_dir / content_type
    content_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = content_dir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Get file size
    file_size = len(content)
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    # Create media record
    media = MediaContent(
        title=title,
        description=description,
        content_type=content_type,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type,
        tags=tag_list,
        category=category,
        price=price,
        owner_id=current_user.id
    )
    
    # Store in database
    await db.media_content.insert_one(media.dict())
    
    return {
        "media_id": media.id,
        "title": title,
        "content_type": content_type,
        "file_size": file_size,
        "category": category,
        "price": price,
        "tags": tag_list,
        "message": "Media uploaded successfully"
    }

@router.get("/media/library")
async def get_media_library(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    # Build query
    query = {"owner_id": current_user.id}
    if content_type:
        query["content_type"] = content_type
    if category:
        query["category"] = category
    
    # Get media items
    cursor = db.media_content.find(query).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    # Get total count
    total_count = await db.media_content.count_documents(query)
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

# Media Analytics Endpoint - MOVED BEFORE PARAMETERIZED ROUTES FOR PROPER ROUTING
@router.get("/media/analytics")
async def get_media_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get media analytics for current user"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user's media
        query = {"owner_id": current_user.id}
        total_media = await db.media_content.count_documents(query)
        
        # Get media by content type
        media_by_type = {}
        for content_type in ["audio", "video", "image"]:
            count = await db.media_content.count_documents({
                "owner_id": current_user.id,
                "content_type": content_type
            })
            media_by_type[content_type] = count
        
        # Get recent uploads
        recent_media = await db.media_content.count_documents({
            "owner_id": current_user.id,
            "created_at": {"$gte": start_date}
        })
        
        # Get approval status
        approved_media = await db.media_content.count_documents({
            "owner_id": current_user.id,
            "is_approved": True
        })
        
        pending_approval = await db.media_content.count_documents({
            "owner_id": current_user.id,
            "approval_status": "pending"
        })
        
        # Calculate storage usage (simplified)
        storage_pipeline = [
            {"$match": {"owner_id": current_user.id}},
            {"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}
        ]
        
        storage_result = await db.media_content.aggregate(storage_pipeline).to_list(1)
        total_storage = storage_result[0]["total_size"] if storage_result else 0
        
        # Get most popular media (by download count)
        popular_media_pipeline = [
            {"$match": {"owner_id": current_user.id}},
            {"$sort": {"download_count": -1}},
            {"$limit": 5},
            {"$project": {"title": 1, "content_type": 1, "download_count": 1, "created_at": 1}}
        ]
        
        popular_media_cursor = db.media_content.aggregate(popular_media_pipeline)
        popular_media = await popular_media_cursor.to_list(5)
        
        # Clean popular media data
        for media in popular_media:
            media.pop("_id", None)
        
        return {
            "analytics": {
                "analytics_period": f"{days} days",
                "overview": {
                    "total_media": total_media,
                    "recent_uploads": recent_media,
                    "approved_media": approved_media,
                    "pending_approval": pending_approval,
                    "approval_rate": (approved_media / max(total_media, 1)) * 100
                },
                "content_breakdown": media_by_type,
                "storage": {
                    "total_bytes": total_storage,
                    "total_mb": round(total_storage / (1024 * 1024), 2),
                    "total_gb": round(total_storage / (1024 * 1024 * 1024), 3)
                },
                "popular_content": popular_media,
                "upload_trends": {
                    "recent_activity": recent_media,
                    "daily_average": round(recent_media / max(days, 1), 2)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get media analytics: {str(e)}")

@router.get("/content/{media_id}")
async def get_media_item(media_id: str, current_user: User = Depends(get_current_user)):
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media or is admin
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this media")
    
    return MediaContent(**media)

@router.get("/content/{media_id}/download")
async def download_media(media_id: str, current_user: User = Depends(get_current_user)):
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media or has purchased it (simplified for now)
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to download this media")
    
    file_path = Path(media["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Update download count
    await db.media_content.update_one(
        {"id": media_id},
        {"$inc": {"download_count": 1}}
    )
    
    return FileResponse(
        path=file_path,
        filename=media["title"],
        media_type=media["mime_type"]
    )

# MISSING MEDIA ENDPOINTS - IMPLEMENTING FOR 100% FUNCTIONALITY

@router.put("/content/{media_id}")
async def update_media(
    media_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Update media metadata"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this media")
    
    # Build update data
    update_data = {"updated_at": datetime.utcnow()}
    
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if category is not None:
        update_data["category"] = category
    if price is not None:
        update_data["price"] = price
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        update_data["tags"] = tag_list
    
    # Update in database
    await db.media_content.update_one({"id": media_id}, {"$set": update_data})
    
    # Get updated media
    updated_media = await db.media_content.find_one({"id": media_id})
    
    return {
        "message": "Media updated successfully",
        "media": MediaContent(**updated_media)
    }

@router.delete("/content/{media_id}")
async def delete_media(media_id: str, current_user: User = Depends(get_current_user)):
    """Delete media and its associated file"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this media")
    
    # Delete file from filesystem
    file_path = Path(media["file_path"])
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass  # File deletion failed, but we'll still remove from database
    
    # Remove from database
    await db.media_content.delete_one({"id": media_id})
    
    # Log activity
    await log_activity(
        current_user.id,
        "media_deleted",
        "media",
        media_id,
        {"title": media["title"], "content_type": media["content_type"]}
    )
    
    return {"message": "Media deleted successfully"}

@router.post("/content/{media_id}/metadata")
async def update_media_metadata(
    media_id: str,
    metadata: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update detailed media metadata"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this media")
    
    # Update metadata
    update_data = {
        "updated_at": datetime.utcnow(),
        "metadata": metadata
    }
    
    await db.media_content.update_one({"id": media_id}, {"$set": update_data})
    
    return {
        "message": "Metadata updated successfully",
        "metadata": metadata
    }

@router.get("/media/search")
async def search_media(
    q: str,  # search query
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Search media content"""
    # Build search query
    search_conditions = []
    
    # Text search on title and description
    if q:
        search_conditions.append({
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}}
            ]
        })
    
    # Filter by content type
    if content_type:
        search_conditions.append({"content_type": content_type})
    
    # Filter by category
    if category:
        search_conditions.append({"category": category})
    
    # Filter by tags
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        search_conditions.append({"tags": {"$in": tag_list}})
    
    # Only show user's own media or public approved media
    visibility_condition = {
        "$or": [
            {"owner_id": current_user.id},
            {"is_published": True, "is_approved": True}
        ]
    }
    search_conditions.append(visibility_condition)
    
    # Combine all conditions
    query = {"$and": search_conditions} if search_conditions else {}
    
    # Execute search
    cursor = db.media_content.find(query).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    # Get total count
    total_count = await db.media_content.count_documents(query)
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "search_query": q,
        "filters": {
            "content_type": content_type,
            "category": category,
            "tags": tags
        },
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

def validate_media_metadata(metadata: dict) -> dict:
    """Validate media metadata and return errors"""
    errors = {}
    
    # Title validation
    title = metadata.get('title', '').strip()
    if not title:
        errors['title'] = 'Title is required'
    elif len(title) > 200:
        errors['title'] = 'Title must be under 200 characters'
    
    # ISRC validation
    isrc = metadata.get('isrc', '').strip()
    if isrc:
        isrc_pattern = re.compile(r'^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$')
        if not isrc_pattern.match(isrc.upper()):
            errors['isrc'] = 'ISRC must be in format: CCXXXYYNNNNN (e.g., USRC17607839)'
    
    # UPC validation
    upc = metadata.get('upc', '').strip()
    if upc:
        if not upc.isdigit() or len(upc) != 12:
            errors['upc'] = 'UPC must be exactly 12 digits'
    
    # Rights holders validation
    rights_holders = metadata.get('rightsHolders', '').strip()
    if rights_holders and len(rights_holders) > 500:
        errors['rightsHolders'] = 'Rights holders must be under 500 characters'
    
    # Tags validation
    tags = metadata.get('tags', '').strip()
    if tags and len(tags) > 200:
        errors['tags'] = 'Tags must be under 200 characters'
    
    # Description validation
    description = metadata.get('description', '').strip()
    if description and len(description) > 1000:
        errors['description'] = 'Description must be under 1000 characters'
    
    return errors

async def handle_metadata_file_upload(file: UploadFile, current_user: User, metadata: dict):
    """Handle metadata file upload with parsing and validation"""
    try:
        # Read and parse metadata file content
        content = await file.read()
        
        # Determine file format and parse accordingly
        if file.filename.endswith('.json'):
            metadata_content = json.loads(content.decode('utf-8'))
        elif file.filename.endswith('.xml'):
            # Basic XML parsing - you might want to use xml.etree.ElementTree for more complex parsing
            metadata_content = {"raw_xml": content.decode('utf-8')}
        elif file.filename.endswith('.csv'):
            # Basic CSV parsing - you might want to use csv module for more complex parsing
            lines = content.decode('utf-8').split('\n')
            metadata_content = {"csv_data": lines}
        else:
            # Treat as plain text
            metadata_content = {"raw_text": content.decode('utf-8')}
        
        # Create metadata record in database
        metadata_record = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "metadata_content": metadata_content,
            "title": metadata.get('title', file.filename),
            "description": metadata.get('description', ''),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store in database
        await db.metadata_files.insert_one(metadata_record)
        
        # Send notification if requested
        if metadata.get('send_notification', False):
            try:
                await email_service.send_file_upload_notification(
                    current_user.email,
                    current_user.full_name,
                    file.filename,
                    "metadata"
                )
            except Exception as e:
                print(f"Failed to send notification: {str(e)}")
        
        return {
            "message": "Metadata file uploaded successfully",
            "metadata_id": metadata_record["id"],
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "parsed_content": metadata_content
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid file encoding: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process metadata file: {str(e)}")


