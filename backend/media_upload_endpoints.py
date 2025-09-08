from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
import logging
import json
import os
import uuid
from datetime import datetime
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

@media_router.post("/upload")
async def upload_media_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form("music"),
    current_user: User = Depends(get_current_user)
):
    """Upload media file to S3 and create database record"""
    try:
        # Validate file type
        allowed_types = {
            'audio': ['mp3', 'wav', 'flac', 'm4a', 'aac'],
            'video': ['mp4', 'mov', 'avi', 'mkv'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        }
        
        file_extension = file.filename.split('.')[-1].lower()
        if category not in allowed_types or file_extension not in allowed_types[category]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type for {category}. Allowed: {allowed_types.get(category, [])}"
            )
        
        # Generate unique file path
        media_id = str(uuid.uuid4())
        file_key = f"{category}/{current_user.id}/{media_id}.{file_extension}"
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': current_user.id,
                    'title': title,
                    'category': category
                }
            )
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail="File upload failed")
        
        # Create database record
        media_record = {
            "id": media_id,
            "user_id": current_user.id,
            "title": title,
            "description": description,
            "file_path": file_key,
            "file_type": category,
            "file_size": file_size,
            "upload_status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "s3_bucket": S3_BUCKET_NAME,
            "original_filename": file.filename
        }
        
        await db.media_uploads.insert_one(media_record)
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Media uploaded successfully",
                "media_id": media_id,
                "file_path": file_key,
                "upload_status": "completed"
            }
        )
        
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
    """Get user's earnings from distributed media"""
    try:
        # Build query
        query = {"user_id": current_user.id}
        
        # Simulate earnings data
        earnings_data = {
            "total_earnings": 156.78,
            "pending_earnings": 23.45,
            "last_payout": 133.33,
            "earnings_by_platform": {
                "spotify": 45.67,
                "apple_music": 38.22,
                "youtube_music": 28.91,
                "amazon_music": 22.14,
                "tidal": 12.83,
                "others": 9.01
            },
            "earnings_by_media": [],
            "payout_history": []
        }
        
        # Get user's media for earnings breakdown
        media_cursor = db.media_uploads.find({"user_id": current_user.id})
        user_media = await media_cursor.to_list(length=None)
        
        for media in user_media:
            earnings_data["earnings_by_media"].append({
                "media_id": media["id"],
                "title": media["title"],
                "total_streams": 1250 + hash(media["id"]) % 10000,
                "total_earnings": 15.67 + (hash(media["id"]) % 50),
                "last_updated": datetime.utcnow().isoformat()
            })
        
        return {
            "success": True,
            "earnings_data": earnings_data
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
    """Request payout of earnings"""
    try:
        # Validate payout amount
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Payout amount must be greater than 0")
        
        # Check user's available balance (simplified)
        available_balance = 156.78  # This would come from actual earnings calculation
        
        if amount > available_balance:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Available: ${available_balance}"
            )
        
        # Create payout request
        payout_id = str(uuid.uuid4())
        payout_request = {
            "id": payout_id,
            "user_id": current_user.id,
            "amount": amount,
            "payout_method": payout_method,
            "payout_details": payout_details,
            "status": "pending",
            "requested_at": datetime.utcnow(),
            "processing_fee": amount * 0.025,  # 2.5% processing fee
            "net_amount": amount * 0.975
        }
        
        await db.payout_requests.insert_one(payout_request)
        
        return {
            "success": True,
            "message": "Payout request submitted successfully",
            "payout_id": payout_id,
            "amount": amount,
            "processing_fee": payout_request["processing_fee"],
            "net_amount": payout_request["net_amount"],
            "status": "pending"
        }
        
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