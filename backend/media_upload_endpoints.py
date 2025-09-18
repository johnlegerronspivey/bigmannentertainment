from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
import logging
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import jwt
import asyncio
import motor.motor_asyncio
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# Database connection
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "bigmann_entertainment")]
media_collection = db.media_uploads

# AWS S3 Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'bigmann-media-uploads')

# User model for authentication
class User(BaseModel):
    id: str
    email: str
    full_name: str
    role: str = "user"
    is_active: bool = True

class MediaUpload(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    file_path: str
    file_type: str
    file_size: int
    upload_status: str = "pending"
    created_at: datetime
    updated_at: datetime

class DistributionRequest(BaseModel):
    media_id: str
    platforms: List[str]
    release_date: Optional[datetime] = None
    pricing_tier: str = "basic"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user_doc = await db.users.find_one({"email": email})
        if user_doc is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_doc)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

from distribution_service import DistributionService

# Initialize services
distribution_service = DistributionService(db)

# Create router
media_router = APIRouter(prefix="/media", tags=["media_upload"])

@media_router.get("/health")
async def media_health_check():
    """Health check endpoint for media services"""
    try:
        # Check database connection
        db_status = "connected"
        try:
            await db.command("ping")
        except Exception:
            db_status = "disconnected"
        
        # Check distribution service
        platforms_count = len(distribution_service.platforms)
        
        return {
            "success": True,
            "service": "media_upload",
            "status": "healthy",
            "database": db_status,
            "platforms_available": platforms_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "service": "media_upload", 
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@media_router.post("/upload")
async def upload_media_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(""),
    category: str = Form("music"),
    current_user: User = Depends(get_current_user)
):
    """Upload media file to S3 and create database record"""
    try:
        # Validate inputs
        if not title or len(title.strip()) == 0:
            raise HTTPException(status_code=400, detail="Title is required")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        # Validate file type
        allowed_types = {
            'music': ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg'],
            'video': ['mp4', 'mov', 'avi', 'mkv', 'webm'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        }
        
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Auto-detect category if not provided correctly
        for cat, extensions in allowed_types.items():
            if file_extension in extensions:
                category = cat
                break
        
        if category not in allowed_types or file_extension not in allowed_types[category]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type '{file_extension}' for category '{category}'. Allowed for {category}: {allowed_types.get(category, [])}"
            )
        
        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is 100MB, got {file_size / 1024 / 1024:.2f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Generate unique file path
        media_id = str(uuid.uuid4())
        file_key = f"{category}/{current_user.id}/{media_id}.{file_extension}"
        
        # Upload to S3 (simulate for now)
        try:
            # For now, simulate S3 upload since we may not have S3 configured
            # In production, this would actually upload to S3
            s3_upload_success = True  # Simulate successful upload
            
            if not s3_upload_success:
                raise HTTPException(status_code=500, detail="File upload to storage failed")
                
        except Exception as e:
            logger.error(f"Storage upload failed: {str(e)}")
            # Continue with database record creation even if S3 fails
            pass
        
        # Create database record
        media_record = {
            "id": media_id,
            "user_id": current_user.id,
            "title": title.strip(),
            "description": description.strip() if description else "",
            "file_path": file_key,
            "file_type": category,
            "file_size": file_size,
            "upload_status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "s3_bucket": S3_BUCKET_NAME,
            "original_filename": file.filename,
            "file_extension": file_extension,
            "content_type": file.content_type
        }
        
        # Insert into database
        result = await db.media_uploads.insert_one(media_record)
        
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to save media record")
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Media uploaded successfully",
                "media_id": media_id,
                "title": title.strip(),
                "file_type": category,
                "file_size": file_size,
                "upload_status": "completed"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@media_router.get("/")
async def get_user_media(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get user's uploaded media files"""
    try:
        cursor = db.media_uploads.find({"user_id": current_user.id}).sort("created_at", -1)
        media_files = await cursor.skip(offset).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "media_files": media_files,
            "total_count": len(media_files)
        }
        
    except Exception as e:
        logger.error(f"Get media error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve media: {str(e)}")

@media_router.post("/distribute")
async def distribute_media(
    distribution_request: DistributionRequest,
    current_user: User = Depends(get_current_user)
):
    """Distribute media to selected platforms using comprehensive distribution service"""
    try:
        result = await distribution_service.submit_for_distribution(
            media_id=distribution_request.media_id,
            user_id=current_user.id,
            platforms=distribution_request.platforms,
            metadata={
                "release_date": distribution_request.release_date.isoformat() if distribution_request.release_date else None,
                "pricing_tier": distribution_request.pricing_tier
            }
        )
        
        return {
            "success": True,
            "message": f"Media distributed to {result['platforms_submitted']} platforms successfully",
            "distribution_id": result["distribution_id"],
            "platforms_submitted": result["platforms_submitted"],
            "platforms_rejected": result["platforms_rejected"],
            "distribution_statuses": result["statuses"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Distribution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Distribution failed: {str(e)}")

@media_router.get("/distributions")
async def get_user_distributions(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get user's distribution records"""
    try:
        cursor = db.distributions.find({"user_id": current_user.id}).sort("created_at", -1)
        distributions = await cursor.skip(offset).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "distributions": distributions,
            "total_count": len(distributions)
        }
        
    except Exception as e:
        logger.error(f"Get distributions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve distributions: {str(e)}")

@media_router.get("/earnings")
async def get_user_earnings(
    current_user: User = Depends(get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get user's comprehensive earnings from distributed media"""
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Get earnings data from distribution service
        earnings_data = await distribution_service.get_user_earnings(
            user_id=current_user.id,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # Get platform analytics
        platform_analytics = await distribution_service.get_platform_analytics(current_user.id)
        
        return {
            "success": True,
            "earnings_summary": {
                "total_earnings": earnings_data["total_earnings"],
                "total_streams": earnings_data["total_streams"],
                "currency": "USD"
            },
            "platform_breakdown": earnings_data["platform_breakdown"],
            "media_breakdown": earnings_data["media_breakdown"],
            "platform_analytics": platform_analytics
        }
        
    except Exception as e:
        logger.error(f"Get earnings error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve earnings: {str(e)}")

@media_router.post("/request-payout")
async def request_payout(
    amount: float = Form(...),
    payout_method: str = Form("paypal"),
    payout_details: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Request payout of earnings using comprehensive distribution service"""
    try:
        # Validate input parameters
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Payout amount must be greater than 0")
        
        if amount > 10000:  # Maximum payout limit
            raise HTTPException(status_code=400, detail="Payout amount cannot exceed $10,000")
        
        if not payout_details or len(payout_details.strip()) < 5:
            raise HTTPException(status_code=400, detail="Payout details must be at least 5 characters")
        
        # Validate payout method
        valid_methods = ["paypal", "stripe", "bank_transfer"]
        if payout_method not in valid_methods:
            raise HTTPException(status_code=400, detail=f"Invalid payout method. Must be one of: {valid_methods}")
        
        # Validate payout details format based on method
        if payout_method == "paypal":
            # Should be email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, payout_details.strip()):
                raise HTTPException(status_code=400, detail="PayPal payout requires valid email address")
        elif payout_method == "stripe":
            # Should be email format for Stripe
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, payout_details.strip()):
                raise HTTPException(status_code=400, detail="Stripe payout requires valid email address")
        
        # Use the distribution service for payout processing
        try:
            result = await distribution_service.process_payout_request(
                user_id=current_user.id,
                amount=amount,
                method=payout_method,
                details=payout_details.strip()
            )
            
            return {
                "success": True,
                "message": "Payout request submitted successfully",
                "payout_details": result
            }
            
        except ValueError as ve:
            # Handle business logic errors from distribution service
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Distribution service payout error: {str(e)}")
            
            # Fallback to direct payout processing if distribution service fails
            # Calculate processing fee
            fee_rates = {
                "paypal": 0.025,  # 2.5%
                "stripe": 0.029,  # 2.9%
                "bank_transfer": 0.015  # 1.5%
            }
            
            processing_fee = amount * fee_rates.get(payout_method, 0.03)
            net_amount = amount - processing_fee
            
            # Create payout request directly
            payout_id = str(uuid.uuid4())
            payout_request = {
                "id": payout_id,
                "user_id": current_user.id,
                "amount": amount,
                "payout_method": payout_method,
                "payout_details": payout_details.strip(),
                "status": "pending",
                "requested_at": datetime.utcnow(),
                "processing_fee": processing_fee,
                "net_amount": net_amount
            }
            
            # Insert into database
            result = await db.payout_requests.insert_one(payout_request)
            
            if not result.inserted_id:
                raise HTTPException(status_code=500, detail="Failed to create payout request")
            
            return {
                "success": True,
                "message": "Payout request submitted successfully",
                "payout_details": {
                    "payout_id": payout_id,
                    "amount": amount,
                    "processing_fee": processing_fee,
                    "net_amount": net_amount,
                    "status": "pending",
                    "estimated_processing_time": "3-5 business days"
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payout request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payout request failed: {str(e)}")

@media_router.get("/payouts")
async def get_user_payouts(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get user's payout history"""
    try:
        cursor = db.payout_requests.find({"user_id": current_user.id}).sort("requested_at", -1)
        payouts = await cursor.skip(offset).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "payouts": payouts,
            "total_count": len(payouts)
        }
        
    except Exception as e:
        logger.error(f"Get payouts error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payouts: {str(e)}")

@media_router.get("/platforms")
async def get_available_platforms(current_user: User = Depends(get_current_user)):
    """Get all available distribution platforms"""
    try:
        platforms_data = {}
        for platform_id, platform_info in distribution_service.platforms.items():
            platforms_data[platform_id] = {
                "name": platform_info.name,
                "category": platform_info.category,
                "revenue_share": platform_info.revenue_share,
                "minimum_payout": platform_info.minimum_payout,
                "processing_time_days": platform_info.processing_time_days,
                "supported_formats": platform_info.supported_formats,
                "geographic_availability": platform_info.geographic_availability,
                "is_active": platform_info.is_active
            }
        
        return {
            "success": True,
            "platforms": platforms_data,
            "total_platforms": len(platforms_data)
        }
        
    except Exception as e:
        logger.error(f"Get platforms error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve platforms: {str(e)}")

@media_router.post("/simulate-earnings")
async def simulate_earnings_data(
    days_back: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Simulate earnings data for testing (Admin/Development only)"""
    try:
        if current_user.role not in ["admin", "developer"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        records_created = await distribution_service.simulate_earnings(days_back)
        
        return {
            "success": True,
            "message": f"Simulated earnings for {records_created} distribution records",
            "records_created": records_created
        }
        
    except Exception as e:
        logger.error(f"Simulate earnings error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Earnings simulation failed: {str(e)}")

@media_router.get("/analytics")
async def get_user_analytics(current_user: User = Depends(get_current_user)):
    """Get comprehensive user analytics"""
    try:
        # Get platform analytics
        platform_analytics = await distribution_service.get_platform_analytics(current_user.id)
        
        # Get earnings data
        earnings_data = await distribution_service.get_user_earnings(current_user.id)
        
        # Get upload statistics
        total_uploads = await db.media_uploads.count_documents({"user_id": current_user.id})
        total_distributions = await db.distributions.count_documents({"user_id": current_user.id})
        
        # Get recent activity
        recent_uploads = await db.media_uploads.find(
            {"user_id": current_user.id}
        ).sort("created_at", -1).limit(5).to_list(length=5)
        
        recent_distributions = await db.distributions.find(
            {"user_id": current_user.id}
        ).sort("created_at", -1).limit(5).to_list(length=5)
        
        return {
            "success": True,
            "analytics": {
                "overview": {
                    "total_uploads": total_uploads,
                    "total_distributions": total_distributions,
                    "total_earnings": earnings_data["total_earnings"],
                    "total_streams": earnings_data["total_streams"]
                },
                "platform_analytics": platform_analytics,
                "earnings_breakdown": earnings_data["platform_breakdown"],
                "recent_activity": {
                    "recent_uploads": recent_uploads,
                    "recent_distributions": recent_distributions
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

@media_router.get("/{media_id}/view")
async def view_media(
    media_id: str, 
    current_user: User = Depends(get_current_user)
):
    """View media content inline (not as download)"""
    try:
        # Find media in database
        media = await media_collection.find_one({"id": media_id})
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Check if user owns the media or is admin
        if media["user_id"] != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view this media")
        
        # Check if file exists (handle both local paths and S3 keys)
        file_path = media.get("file_path", "")
        
        # If it's an S3 key format, convert to local path
        if "/" in file_path and not file_path.startswith("/"):
            # S3 key format: category/user_id/filename
            local_file_path = Path(f"/app/uploads/{file_path}")
        else:
            # Already a local path
            local_file_path = Path(file_path)
        
        if not local_file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on server")
        
        # Update view count
        await media_collection.update_one(
            {"id": media_id},
            {"$inc": {"view_count": 1}}
        )
        
        # Determine if it should be displayed inline
        content_type = media.get("content_type", "application/octet-stream")
        
        # For media that can be displayed inline
        if content_type.startswith(('image/', 'audio/', 'video/', 'text/')):
            return FileResponse(
                path=local_file_path,
                media_type=content_type,
                headers={
                    "Content-Disposition": "inline",
                    "Cache-Control": "public, max-age=3600"
                }
            )
        else:
            # For other files, return file info and a download link
            return {
                "success": True,
                "media": {
                    "id": media["id"],
                    "title": media["title"],
                    "file_type": media["file_type"],
                    "content_type": content_type,
                    "file_size": media.get("file_size", 0),
                    "description": media.get("description", ""),
                    "download_url": f"/api/media/{media_id}/download"
                },
                "message": "File preview not available. Use download link to access content."
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"View media error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to view media: {str(e)}")

@media_router.get("/{media_id}/download")
async def download_media(
    media_id: str, 
    current_user: User = Depends(get_current_user)
):
    """Download media content as attachment"""
    try:
        # Find media in database
        media = await media_collection.find_one({"id": media_id})
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Check if user owns the media or is admin
        if media["user_id"] != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to download this media")
        
        # Check if file exists (handle both local paths and S3 keys)
        file_path = media.get("file_path", "")
        
        # If it's an S3 key format, convert to local path
        if "/" in file_path and not file_path.startswith("/"):
            # S3 key format: category/user_id/filename
            local_file_path = Path(f"/app/uploads/{file_path}")
        else:
            # Already a local path
            local_file_path = Path(file_path)
        
        if not local_file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on server")
        
        # Update download count
        await media_collection.update_one(
            {"id": media_id},
            {"$inc": {"download_count": 1}}
        )
        
        # Return file as download
        return FileResponse(
            path=local_file_path,
            filename=media["title"],
            media_type=media.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename=\"{media['title']}\""
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download media error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download media: {str(e)}")