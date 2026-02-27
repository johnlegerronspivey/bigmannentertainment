"""
Batch Processing API Endpoints
Handles batch metadata processing, bulk uploads, and batch reporting
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from auth.service import get_current_user, get_current_admin_user as require_admin
from metadata_models import MetadataValidationConfig
from batch_processing_service import BatchProcessingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/batch", tags=["Batch Processing"])

# Global service (will be initialized in server.py)
batch_service = None
mongo_db = None

def init_batch_service(db, services_dict):
    """Initialize batch processing service"""
    global batch_service, mongo_db
    mongo_db = db
    batch_service = BatchProcessingService(mongo_db=db)
    services_dict['batch_processor'] = batch_service

@router.post("/upload-archive")
async def upload_archive_batch(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    validate_metadata: bool = Form(True),
    check_duplicates: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process archive file (ZIP, TAR, GZ) containing metadata files"""
    
    try:
        # Validate file type
        allowed_extensions = ['.zip', '.tar', '.tar.gz', '.tgz', '.gz']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported archive format. Allowed: {allowed_extensions}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Size limit for archives (500MB)
        if file_size > 500 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Archive too large. Maximum size is 500MB."
            )
        
        # Create validation config
        validation_config = MetadataValidationConfig(
            check_duplicates=check_duplicates,
            duplicate_scope="platform"
        ) if validate_metadata else None
        
        # Start batch processing
        batch_result = await batch_service.process_archive(
            archive_content=content,
            filename=file.filename,
            user_id=current_user.id,
            validation_config=validation_config
        )
        
        return {
            "success": True,
            "message": "Archive uploaded and processing started",
            "batch_id": batch_result.batch_id,
            "status": batch_result.status,
            "total_files": batch_result.total_files,
            "processed_files": batch_result.processed_files,
            "successful_files": batch_result.successful_files,
            "failed_files": batch_result.failed_files,
            "processing_time": batch_result.processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing archive: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process archive: {str(e)}"
        )

@router.post("/upload-multiple")
async def upload_multiple_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    validate_metadata: bool = Form(True),
    check_duplicates: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process multiple metadata files"""
    
    try:
        # Validate file count
        if len(files) > 50:
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 files allowed per batch"
            )
        
        # Process files
        files_data = []
        total_size = 0
        
        for file in files:
            content = await file.read()
            file_size = len(content)
            total_size += file_size
            
            # Detect format
            filename_lower = file.filename.lower()
            if filename_lower.endswith('.json'):
                file_format = 'json'
            elif filename_lower.endswith('.xml'):
                file_format = 'ddex_ern' if 'ddex' in filename_lower else 'mead'
            elif filename_lower.endswith('.csv'):
                file_format = 'csv'
            elif filename_lower.endswith('.id3'):
                file_format = 'id3'
            elif filename_lower.endswith('.musicbrainz'):
                file_format = 'musicbrainz'
            else:
                file_format = 'json'  # Default
            
            files_data.append({
                'filename': file.filename,
                'content': content,
                'format': file_format
            })
        
        # Check total size (100MB limit for multi-file)
        if total_size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Total files size too large. Maximum is 100MB."
            )
        
        # Create validation config
        validation_config = MetadataValidationConfig(
            check_duplicates=check_duplicates,
            duplicate_scope="platform"
        ) if validate_metadata else None
        
        # Start batch processing
        batch_result = await batch_service.process_multiple_files(
            files_data=files_data,
            user_id=current_user.id,
            validation_config=validation_config
        )
        
        return {
            "success": True,
            "message": "Multiple files uploaded and processed",
            "batch_id": batch_result.batch_id,
            "status": batch_result.status,
            "total_files": batch_result.total_files,
            "processed_files": batch_result.processed_files,
            "successful_files": batch_result.successful_files,
            "failed_files": batch_result.failed_files,
            "success_rate": batch_result.to_dict().get('success_rate', 0),
            "processing_time": batch_result.processing_time,
            "file_results": batch_result.file_results[:10]  # Return first 10 results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing multiple files: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process multiple files: {str(e)}"
        )

@router.get("/status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of a batch processing job"""
    
    try:
        # Check active batches first
        status = batch_service.get_batch_status(batch_id)
        
        if status:
            return {
                "success": True,
                "batch_status": status
            }
        
        # Check database for completed batches
        if mongo_db:
            batch_record = await mongo_db["batch_processing_results"].find_one({
                "_id": batch_id,
                "user_id": current_user.id
            })
            
            if batch_record:
                batch_record.pop("_id", None)
                return {
                    "success": True,
                    "batch_status": batch_record
                }
        
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch status: {str(e)}"
        )

@router.get("/history")
async def get_batch_history(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get batch processing history for current user"""
    
    try:
        history = await batch_service.get_batch_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            **history
        }
        
    except Exception as e:
        logger.error(f"Error getting batch history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch history: {str(e)}"
        )

@router.get("/report/{batch_id}")
async def get_batch_report(
    batch_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate detailed report for a batch processing job"""
    
    try:
        report = await batch_service.generate_batch_report(
            batch_id=batch_id,
            user_id=current_user.id
        )
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail="Batch report not found"
            )
        
        return {
            "success": True,
            "batch_report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating batch report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate batch report: {str(e)}"
        )

# Admin endpoints
@router.get("/admin/all-batches")
async def admin_get_all_batches(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(require_admin)
):
    """Admin endpoint to get all batch processing jobs"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get total count
        total_count = await mongo_db["batch_processing_results"].count_documents({})
        
        # Get paginated results
        cursor = mongo_db["batch_processing_results"].find({}).sort("created_at", -1).skip(offset).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id for response
        for result in results:
            result.pop("_id", None)
        
        return {
            "success": True,
            "batches": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all batches: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get all batches: {str(e)}"
        )

@router.get("/admin/statistics")
async def admin_get_batch_statistics(
    current_user: dict = Depends(require_admin)
):
    """Admin endpoint to get platform batch processing statistics"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get statistics
        total_batches = await mongo_db["batch_processing_results"].count_documents({})
        
        # Count by status
        completed_batches = await mongo_db["batch_processing_results"].count_documents({"status": "completed"})
        failed_batches = await mongo_db["batch_processing_results"].count_documents({"status": "failed"})
        processing_batches = await mongo_db["batch_processing_results"].count_documents({"status": "processing"})
        
        # Calculate aggregate statistics
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_files_processed": {"$sum": "$total_files"},
                    "total_successful_files": {"$sum": "$successful_files"},
                    "total_failed_files": {"$sum": "$failed_files"},
                    "avg_success_rate": {"$avg": "$success_rate"},
                    "avg_processing_time": {"$avg": "$processing_time"}
                }
            }
        ]
        
        aggregate_result = await mongo_db["batch_processing_results"].aggregate(pipeline).to_list(1)
        aggregate_stats = aggregate_result[0] if aggregate_result else {}
        
        return {
            "success": True,
            "batch_statistics": {
                "total_batches": total_batches,
                "completed_batches": completed_batches,
                "failed_batches": failed_batches,
                "processing_batches": processing_batches,
                "success_rate": (completed_batches / total_batches * 100) if total_batches > 0 else 0,
                "total_files_processed": aggregate_stats.get("total_files_processed", 0),
                "total_successful_files": aggregate_stats.get("total_successful_files", 0),
                "total_failed_files": aggregate_stats.get("total_failed_files", 0),
                "platform_avg_success_rate": aggregate_stats.get("avg_success_rate", 0),
                "avg_processing_time": aggregate_stats.get("avg_processing_time", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting batch statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch statistics: {str(e)}"
        )