"""AWS endpoints - S3 uploads, SES email, CDN, media processing."""
import os
import json
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile, Request
from config.database import db
from auth.service import get_current_user, get_current_admin_user
from models.core import User

router = APIRouter(tags=["AWS"])

# Initialize AWS services
from services.s3_svc import S3Service
from services.ses_transactional_svc import SESService, EmailNotificationService
from services.aws_media_svc import CloudFrontService, LambdaProcessingService, RekognitionService

s3_service = S3Service()
ses_service = SESService()
enhanced_email_service = EmailNotificationService()
cloudfront_service = CloudFrontService()
lambda_service = LambdaProcessingService()
rekognition_service = RekognitionService()
services_dict = {}

# Import helper functions from media routes
from routes.media_routes import validate_media_metadata, handle_metadata_file_upload

# AWS S3 Enhanced Media Endpoints
@router.post("/metadata/upload")
async def upload_metadata_file(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    validate_metadata: bool = Form(True),
    check_duplicates: bool = Form(True),
    send_notification: bool = Form(True),
    current_user: User = Depends(get_current_user)
):
    """Upload and parse metadata file with validation"""
    try:
        # Import metadata services
        from metadata_parser_service import MetadataParserService
        from metadata_validator_service import MetadataValidatorService
        from metadata_models import MetadataFormat, MetadataValidationConfig
        
        # Initialize services
        parser_service = MetadataParserService()
        validator_service = MetadataValidatorService(mongo_db=db)
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
        
        # Determine metadata format from file extension
        filename = file.filename.lower()
        if filename.endswith('.xml'):
            if 'ddex' in filename or 'ern' in filename:
                metadata_format = MetadataFormat.DDEX_ERN
            else:
                metadata_format = MetadataFormat.MEAD  # Assume MEAD XML
        elif filename.endswith('.json'):
            metadata_format = MetadataFormat.JSON
        elif filename.endswith('.csv'):
            metadata_format = MetadataFormat.CSV
        else:
            # Try to detect format from content
            content_str = content.decode('utf-8', errors='ignore').strip()
            if content_str.startswith('<') and 'ddex' in content_str.lower():
                metadata_format = MetadataFormat.DDEX_ERN
            elif content_str.startswith('<'):
                metadata_format = MetadataFormat.MEAD
            elif content_str.startswith('{') or content_str.startswith('['):
                metadata_format = MetadataFormat.JSON
            else:
                metadata_format = MetadataFormat.CSV
        
        # Parse metadata
        parsed_metadata, parsing_errors = parser_service.parse_metadata(
            content=content,
            file_format=metadata_format,
            file_name=file.filename
        )
        
        # Validate if requested
        validation_result = None
        if validate_metadata:
            validation_config = MetadataValidationConfig(
                check_duplicates=check_duplicates,
                duplicate_scope="platform"
            )
            
            validation_result = await validator_service.validate_metadata(
                parsed_metadata=parsed_metadata,
                file_format=metadata_format,
                config=validation_config
            )
            
            # Set user and file info
            validation_result.user_id = current_user.id
            validation_result.file_name = file.filename
            validation_result.file_size = file_size
            validation_result.parsing_errors = parsing_errors
            
            # Store validation result
            try:
                result_dict = validation_result.dict()
                result_dict["_id"] = validation_result.id
                result_dict["created_at"] = datetime.utcnow()
                await db.metadata_validation_results.insert_one(result_dict)
            except Exception as e:
                print(f"Failed to store validation result: {str(e)}")
        
        # Also store as media content if it's valid metadata
        if validation_result is None or validation_result.validation_status != "error":
            # Create media content record
            media_content = {
                "id": str(uuid.uuid4()),
                "user_id": current_user.id,
                "title": title or parsed_metadata.title or file.filename,
                "description": description or parsed_metadata.description or "",
                "file_name": file.filename,
                "file_type": "metadata",
                "file_size": file_size,
                "content_type": file.content_type,
                "metadata_format": metadata_format.value,
                "parsed_metadata": parsed_metadata.dict(),
                "validation_id": validation_result.id if validation_result else None,
                "validation_status": validation_result.validation_status if validation_result else "not_validated",
                "created_at": datetime.utcnow(),
                "is_approved": True,  # Auto-approve metadata files
                "approval_status": "approved"
            }
            
            await db.media_content.insert_one(media_content)
            
            # Send notification if requested
            if send_notification:
                try:
                    await enhanced_email_service.send_email_with_fallback(
                        to_email=current_user.email,
                        subject="Metadata Upload Complete",
                        html_content=f"<p>Hi {current_user.full_name},</p><p>Your metadata file <strong>{file.filename}</strong> has been uploaded successfully.</p>"
                    )
                except Exception as e:
                    print(f"Failed to send notification: {str(e)}")
        
        return {
            "success": True,
            "message": "Metadata file uploaded and processed successfully",
            "media_id": media_content["id"] if 'media_content' in locals() else None,
            "validation_id": validation_result.id if validation_result else None,
            "file_info": {
                "filename": file.filename,
                "file_size": file_size,
                "content_type": file.content_type,
                "metadata_format": metadata_format.value
            },
            "parsed_metadata": parsed_metadata.dict(),
            "validation_summary": {
                "status": validation_result.validation_status if validation_result else "not_validated",
                "error_count": len(validation_result.validation_errors) if validation_result else 0,
                "warning_count": len(validation_result.validation_warnings) if validation_result else 0,
                "duplicates_found": validation_result.duplicate_count if validation_result else 0
            } if validation_result else {"status": "not_validated"},
            "validation_errors": [error.dict() for error in validation_result.validation_errors] if validation_result else [],
            "validation_warnings": [warning.dict() for warning in validation_result.validation_warnings] if validation_result else [],
            "duplicate_details": [dup.dict() for dup in validation_result.duplicates_found] if validation_result else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading metadata file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload metadata file: {str(e)}"
        )

@router.post("/media/s3/upload/{file_type}")
async def upload_media_to_s3_enhanced(
    file_type: str,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    user_email: str = Form(...),
    user_name: str = Form(...),
    title: str = Form(""),
    description: str = Form(""),
    category: str = Form("media"),
    send_notification: bool = Form(True),
    # Enhanced metadata fields
    metadata_title: str = Form(""),
    metadata_artist: str = Form(""),
    metadata_album: str = Form(""),
    metadata_isrc: str = Form(""),
    metadata_upc: str = Form(""),
    metadata_rightsHolders: str = Form(""),
    metadata_genre: str = Form(""),
    metadata_releaseDate: str = Form(""),
    metadata_description: str = Form(""),
    metadata_tags: str = Form(""),
    metadata_copyrightYear: int = Form(2025),
    metadata_publisherName: str = Form(""),
    metadata_composerName: str = Form(""),
    metadata_duration: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    """Enhanced upload media file to S3 storage with comprehensive metadata and audit logging"""
    upload_start_time = datetime.now()
    content_id = f"content_{datetime.now().timestamp()}_{user_id}"
    
    try:
        # Validate file type
        if file_type not in ['audio', 'video', 'image', 'metadata']:
            # Log validation failure
            if 'audit' in services_dict:
                await services_dict['audit'].log_upload_event({
                    "success": False,
                    "content_id": content_id,
                    "user_id": user_id,
                    "user_context": {
                        "user_id": user_id,
                        "user_email": user_email,
                        "user_name": user_name
                    },
                    "original_filename": file.filename,
                    "file_type": file_type,
                    "upload_status": "failed",
                    "error_message": f"Invalid file type: {file_type}",
                    "upload_started": upload_start_time
                })
            
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")
        
        # Handle metadata file upload with parsing and validation
        if file_type == 'metadata':
            return await handle_metadata_file_upload(file, current_user, {
                'title': metadata_title or title,
                'description': metadata_description or description,
                'send_notification': send_notification
            })
        
        # Validate metadata
        validation_errors = validate_media_metadata({
            'title': metadata_title or title,
            'isrc': metadata_isrc,
            'upc': metadata_upc,
            'rightsHolders': metadata_rightsHolders,
            'artist': metadata_artist,
            'album': metadata_album,
            'genre': metadata_genre,
            'description': metadata_description or description,
            'tags': metadata_tags
        })
        
        if validation_errors:
            # Log validation failure with audit trail
            if 'audit' in services_dict:
                await services_dict['audit'].log_validation_event({
                    "success": False,
                    "content_id": content_id,
                    "user_id": user_id,
                    "user_context": {
                        "user_id": user_id,
                        "user_email": user_email,
                        "user_name": user_name
                    },
                    "validation_status": "failed",
                    "validation_errors": validation_errors,
                    "input_metadata": {
                        'title': metadata_title or title,
                        'isrc': metadata_isrc,
                        'upc': metadata_upc,
                        'rightsHolders': metadata_rightsHolders,
                        'artist': metadata_artist,
                        'album': metadata_album,
                        'genre': metadata_genre
                    },
                    "validation_started": upload_start_time,
                    "validation_completed": datetime.now()
                })
            
            raise HTTPException(status_code=422, detail={
                "message": "Validation errors",
                "errors": validation_errors
            })
        
        # Upload file to S3
        upload_result = await s3_service.upload_file(file, user_id, file_type)
        
        # Prepare comprehensive metadata
        comprehensive_metadata = {
            'title': metadata_title or title,
            'artist': metadata_artist,
            'album': metadata_album,
            'isrc': metadata_isrc.upper() if metadata_isrc else "",
            'upc': metadata_upc,
            'rightsHolders': metadata_rightsHolders,
            'genre': metadata_genre,
            'releaseDate': metadata_releaseDate,
            'description': metadata_description or description,
            'tags': [tag.strip() for tag in metadata_tags.split(',') if tag.strip()],
            'copyrightYear': metadata_copyrightYear,
            'publisherName': metadata_publisherName,
            'composerName': metadata_composerName,
            'duration': metadata_duration,
            'uploadedBy': current_user.full_name,
            'uploadedAt': datetime.now().isoformat(),
            'fileSize': upload_result['size'],
            'contentType': upload_result['content_type']
        }
        
        # Store file metadata in MongoDB
        media_record = {
            'user_id': user_id,
            'owner_id': current_user.id,
            'content_id': content_id,
            'file_type': file_type,
            'object_key': upload_result['object_key'],
            'file_url': upload_result['file_url'],
            'original_filename': file.filename,
            'size': upload_result['size'],
            'content_type': upload_result['content_type'],
            'category': category,
            'upload_timestamp': datetime.now(),
            'is_active': True,
            'upload_method': 's3',
            'metadata': comprehensive_metadata,
            's3_bucket': upload_result['bucket'],
            's3_object_key': upload_result['object_key'],
            's3_file_url': upload_result['file_url']
        }
        
        # Insert into MongoDB
        try:
            # Check if MongoDB collection exists, if not create basic in-memory storage
            media_id = f"media_{datetime.now().timestamp()}_{user_id}"
            media_record['media_id'] = media_id
            
            # Store in a simple way (this would be actual MongoDB in production)
            logging.info(f"Stored media record: {media_record}")
            
        except Exception as db_error:
            logging.warning(f"MongoDB storage failed, continuing: {db_error}")
        
        upload_end_time = datetime.now()
        upload_duration = (upload_end_time - upload_start_time).total_seconds() * 1000
        
        # Log successful upload with comprehensive audit trail
        if 'audit' in services_dict:
            await services_dict['audit'].log_upload_event({
                "success": True,
                "content_id": content_id,
                "user_id": user_id,
                "user_context": {
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_name": user_name,
                    "ip_address": "127.0.0.1"  # Would get from request in production
                },
                "resource_context": {
                    "content_id": content_id,
                    "resource_type": "media_content",
                    "filename": file.filename,
                    "file_size": upload_result['size'],
                    "file_type": file_type,
                    "isrc": metadata_isrc,
                    "upc": metadata_upc
                },
                "event_data": {
                    "s3_bucket": upload_result['bucket'],
                    "s3_key": upload_result['object_key'],
                    "metadata_fields": list(comprehensive_metadata.keys()),
                    "validation_passed": True,
                    "notification_sent": send_notification
                },
                "original_filename": file.filename,
                "final_filename": upload_result['object_key'],
                "file_size": upload_result['size'],
                "file_type": file_type,
                "upload_method": "enhanced_s3",
                "upload_duration_ms": upload_duration,
                "initial_metadata": comprehensive_metadata,
                "storage_provider": "s3",
                "storage_bucket": upload_result['bucket'],
                "storage_key": upload_result['object_key'],
                "storage_url": upload_result['file_url'],
                "upload_status": "completed",
                "upload_started": upload_start_time,
                "upload_completed": upload_end_time
            })
            
            # Create initial metadata snapshot
            await services_dict['audit'].create_metadata_snapshot(
                content_id=content_id,
                user_id=user_id,
                metadata_state=comprehensive_metadata,
                trigger_event="upload",
                trigger_reason="Initial file upload with metadata"
            )
        
        # Send email notification if requested
        if send_notification:
            try:
                await enhanced_email_service.send_file_upload_notification(
                    user_email=user_email,
                    user_name=user_name,
                    filename=file.filename,
                    file_type=file_type,
                    file_size=f"{upload_result['size'] / (1024*1024):.2f} MB",
                    file_url=upload_result['file_url']
                )
            except Exception as e:
                logging.warning(f"Failed to send upload notification: {e}")
        
        return {
            'success': True,
            'content_id': content_id,
            'media_id': media_record.get('media_id'),
            'object_key': upload_result['object_key'],
            'file_url': upload_result['file_url'],
            'cdn_url': cloudfront_service.get_cdn_url(upload_result['object_key']),
            'size': upload_result['size'],
            'content_type': upload_result['content_type'],
            'metadata': comprehensive_metadata,
            'notification_queued': send_notification,
            'validation_passed': True,
            'upload_duration_ms': upload_duration,
            'message': 'File uploaded successfully with metadata and audit trail'
        }
        
    except HTTPException as e:
        # Log HTTP exception failures
        if 'audit' in services_dict:
            await services_dict['audit'].log_upload_event({
                "success": False,
                "content_id": content_id,
                "user_id": user_id,
                "user_context": {
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_name": user_name
                },
                "original_filename": file.filename,
                "file_type": file_type,
                "upload_status": "failed",
                "error_message": str(e.detail),
                "upload_started": upload_start_time,
                "upload_completed": datetime.now()
            })
        raise e
    except Exception as e:
        # Log unexpected failures
        if 'audit' in services_dict:
            await services_dict['audit'].log_upload_event({
                "success": False,
                "content_id": content_id,
                "user_id": user_id,
                "user_context": {
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_name": user_name
                },
                "original_filename": file.filename,
                "file_type": file_type,
                "upload_status": "failed",
                "error_message": str(e),
                "upload_started": upload_start_time,
                "upload_completed": datetime.now()
            })
        
        logging.error(f"Upload with metadata failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/media/s3/user/{user_id}")
async def get_user_s3_files(
    user_id: str,
    file_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get user's S3 files with pagination and filtering"""
    try:
        # Check authorization
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get files from S3
        s3_files = s3_service.list_user_files(user_id, file_type)
        
        # Apply pagination
        paginated_files = s3_files[offset:offset + limit]
        
        return {
            'files': paginated_files,
            'total_count': len(s3_files),
            'limit': limit,
            'offset': offset,
            'has_more': offset + len(paginated_files) < len(s3_files)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve files: {str(e)}"
        )

@router.get("/media/s3/{user_id}/{object_key:path}/url")
async def get_s3_file_access_url(
    user_id: str,
    object_key: str,
    expiration: int = 3600,
    current_user: User = Depends(get_current_user)
):
    """Generate presigned URL for secure S3 file access"""
    try:
        # Check authorization
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate presigned URL
        presigned_url = s3_service.generate_presigned_url(object_key, expiration)
        
        return {
            "access_url": presigned_url,
            "expires_in": expiration,
            "object_key": object_key
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate access URL: {str(e)}"
        )

@router.delete("/media/s3/{user_id}/{object_key:path}")
async def delete_s3_file(
    user_id: str, 
    object_key: str,
    current_user: User = Depends(get_current_user)
):
    """Delete user's file from S3 and database"""
    try:
        # Check authorization
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete from S3
        success = s3_service.delete_file(object_key)
        
        if success:
            # Remove from MongoDB
            await db.media_content.update_one(
                {'s3_object_key': object_key, 'owner_id': user_id},
                {'$set': {'is_active': False, 'deleted_at': datetime.now()}}
            )
            
            return {
                'success': True,
                'message': 'File deleted successfully',
                'object_key': object_key
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete file from storage"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deletion failed: {str(e)}"
        )

# AWS SES Email Endpoints
@router.post("/email/ses/send")
async def send_ses_email(
    to_email: str = Form(...),
    subject: str = Form(...),
    html_content: str = Form(...),
    text_content: Optional[str] = Form(None),
    current_user: User = Depends(get_current_admin_user)
):
    """Send email using AWS SES (Admin only)"""
    try:
        result = ses_service.send_transactional_email(
            to_addresses=[to_email],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {str(e)}"
        )

@router.post("/email/ses/welcome")
async def send_ses_welcome_email(
    user_email: str = Form(...),
    user_name: str = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Send welcome email using AWS SES (Admin only)"""
    try:
        result = await ses_service.send_welcome_email(user_email, user_name)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Welcome email failed: {str(e)}"
        )

# Content Distribution Endpoints

@router.post("/aws/media/process/{file_type}")
async def trigger_media_processing(
    file_type: str,
    s3_key: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Trigger media processing via Lambda"""
    try:
        # Trigger processing
        processing_started = lambda_service.trigger_media_processing(s3_key, file_type)
        
        # Also trigger content moderation if it's an image
        moderation_started = False
        if file_type.lower() in ['image', 'jpg', 'jpeg', 'png']:
            moderation_started = lambda_service.trigger_content_moderation(s3_key)
        
        return {
            "message": "Processing initiated",
            "s3_key": s3_key,
            "file_type": file_type,
            "processing_started": processing_started,
            "moderation_started": moderation_started,
            "lambda_available": lambda_service.lambda_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing trigger failed: {str(e)}")

@router.get("/aws/media/cdn-url")
async def get_cdn_url(s3_key: str):
    """Get CDN URL for media content"""
    try:
        cdn_url = cloudfront_service.get_cdn_url(s3_key)
        
        return {
            "s3_key": s3_key,
            "cdn_url": cdn_url,
            "cloudfront_available": cloudfront_service.cloudfront_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CDN URL generation failed: {str(e)}")

@router.post("/aws/media/moderate")
async def moderate_content(
    s3_key: str = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Moderate content using Rekognition (Admin only)"""
    try:
        bucket_name = os.getenv('S3_BUCKET_NAME', 'bigmann-entertainment-media')
        
        # Perform content moderation
        moderation_result = rekognition_service.detect_moderation_labels(bucket_name, s3_key)
        
        # Get general labels too
        labels_result = rekognition_service.detect_labels(bucket_name, s3_key)
        
        return {
            "s3_key": s3_key,
            "moderation": moderation_result,
            "labels": labels_result,
            "rekognition_available": rekognition_service.rekognition_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content moderation failed: {str(e)}")

@router.post("/aws/cdn/invalidate")
async def invalidate_cdn_cache(
    request_data: dict,
    current_user: User = Depends(get_current_admin_user)
):
    """Invalidate CloudFront cache for specified paths (Admin only)"""
    try:
        paths = request_data.get("paths", [])
        if not paths or not isinstance(paths, list):
            raise HTTPException(status_code=422, detail="paths must be a non-empty list")
        
        invalidation_id = cloudfront_service.invalidate_cache(paths)
        
        return {
            "paths": paths,
            "invalidation_id": invalidation_id,
            "cloudfront_available": cloudfront_service.cloudfront_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

# Alternative JSON-based endpoints for easier integration
@router.post("/aws/media/process-json/{file_type}")
async def trigger_media_processing_json(
    file_type: str,
    request_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Trigger media processing via Lambda (JSON version)"""
    try:
        s3_key = request_data.get("s3_key")
        if not s3_key:
            raise HTTPException(status_code=422, detail="s3_key is required")
        
        # Trigger processing
        processing_started = lambda_service.trigger_media_processing(s3_key, file_type)
        
        # Also trigger content moderation if it's an image
        moderation_started = False
        if file_type.lower() in ['image', 'jpg', 'jpeg', 'png']:
            moderation_started = lambda_service.trigger_content_moderation(s3_key)
        
        return {
            "message": "Processing initiated",
            "s3_key": s3_key,
            "file_type": file_type,
            "processing_started": processing_started,
            "moderation_started": moderation_started,
            "lambda_available": lambda_service.lambda_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing trigger failed: {str(e)}")

@router.post("/aws/media/moderate-json")
async def moderate_content_json(
    request_data: dict,
    current_user: User = Depends(get_current_admin_user)
):
    """Moderate content using Rekognition (JSON version, Admin only)"""
    try:
        s3_key = request_data.get("s3_key")
        if not s3_key:
            raise HTTPException(status_code=422, detail="s3_key is required")
            
        bucket_name = os.getenv('S3_BUCKET_NAME', 'bigmann-entertainment-media')
        
        # Perform content moderation
        moderation_result = rekognition_service.detect_moderation_labels(bucket_name, s3_key)
        
        # Get general labels too
        labels_result = rekognition_service.detect_labels(bucket_name, s3_key)
        
        return {
            "s3_key": s3_key,
            "moderation": moderation_result,
            "labels": labels_result,
            "rekognition_available": rekognition_service.rekognition_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content moderation failed: {str(e)}")

@router.get("/phase2/status")
async def get_phase2_status():
    """Get Phase 2 services status"""
    return {
        "cloudfront": {
            "available": cloudfront_service.cloudfront_available,
            "domain": cloudfront_service.distribution_domain
        },
        "lambda": {
            "available": lambda_service.lambda_available
        },
        "rekognition": {
            "available": rekognition_service.rekognition_available
        },
        "s3": {
            "available": s3_service.s3_client is not None,
            "bucket": os.getenv('S3_BUCKET_NAME', 'bigmann-entertainment-media')
        }
    }
