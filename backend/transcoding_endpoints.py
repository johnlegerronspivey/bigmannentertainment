"""
Transcoding API Endpoints
Provides REST API for content transcoding operations
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from transcoding_service import (
    TranscodingService,
    TranscodingJob,
    TranscodingProfile,
    AudioStandard
)

router = APIRouter(prefix="/api/transcoding", tags=["Transcoding"])
security = HTTPBearer()

# Initialize service
transcoding_service = TranscodingService()

# Request/Response Models
class TranscodingRequest(BaseModel):
    content_id: str
    version_id: str
    source_file_path: str
    profile: TranscodingProfile
    audio_standard: AudioStandard = AudioStandard.STREAMING

class TranscodingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Authentication dependency (simplified)
async def get_current_user(token: str = Depends(security)):
    return {"user_id": "demo_user_123", "username": "demo_user"}

@router.get("/health")
async def transcoding_health():
    """Health check for transcoding service"""
    return {
        "status": "healthy",
        "service": "Transcoding Service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "supported_profiles": [profile.value for profile in TranscodingProfile],
        "audio_standards": [standard.value for standard in AudioStandard]
    }

@router.post("/jobs")
async def create_transcoding_job(
    transcoding_request: TranscodingRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Create a new transcoding job"""
    
    try:
        user_id = current_user["user_id"]
        
        # Create transcoding job
        job = await transcoding_service.create_transcoding_job(
            content_id=transcoding_request.content_id,
            version_id=transcoding_request.version_id,
            user_id=user_id,
            source_file_path=transcoding_request.source_file_path,
            profile=transcoding_request.profile,
            audio_standard=transcoding_request.audio_standard
        )
        
        # Start processing in background
        background_tasks.add_task(transcoding_service.process_transcoding_job, job.job_id)
        
        return TranscodingResponse(
            success=True,
            message="Transcoding job created and started",
            data={
                "job_id": job.job_id,
                "content_id": job.content_id,
                "profile": job.profile.value,
                "audio_standard": job.audio_standard.value,
                "status": job.status,
                "created_at": job.created_at.isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create transcoding job: {e}")

@router.get("/jobs/{job_id}")
async def get_transcoding_job_status(
    job_id: str,
    current_user = Depends(get_current_user)
):
    """Get status of a transcoding job"""
    
    try:
        job = await transcoding_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Transcoding job not found")
        
        # Verify user ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        job_data = {
            "job_id": job.job_id,
            "content_id": job.content_id,
            "version_id": job.version_id,
            "profile": job.profile.value,
            "audio_standard": job.audio_standard.value,
            "status": job.status,
            "progress_percentage": job.progress_percentage,
            "output_files": job.output_files,
            "created_at": job.created_at.isoformat(),
            "error_message": job.error_message
        }
        
        if job.started_at:
            job_data["started_at"] = job.started_at.isoformat()
        if job.completed_at:
            job_data["completed_at"] = job.completed_at.isoformat()
            job_data["processing_time_seconds"] = job.processing_time_seconds
        
        return TranscodingResponse(
            success=True,
            message="Transcoding job status retrieved",
            data=job_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {e}")

@router.get("/jobs")
async def list_transcoding_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """List transcoding jobs for the current user"""
    
    try:
        user_id = current_user["user_id"]
        
        jobs = await transcoding_service.list_user_jobs(user_id, status)
        
        # Apply pagination
        total_jobs = len(jobs)
        paginated_jobs = jobs[offset:offset + limit]
        
        jobs_data = []
        for job in paginated_jobs:
            job_data = {
                "job_id": job.job_id,
                "content_id": job.content_id,
                "version_id": job.version_id,
                "profile": job.profile.value,
                "status": job.status,
                "progress_percentage": job.progress_percentage,
                "created_at": job.created_at.isoformat(),
                "output_files_count": len(job.output_files)
            }
            
            if job.completed_at:
                job_data["completed_at"] = job.completed_at.isoformat()
                job_data["processing_time_seconds"] = job.processing_time_seconds
                
            jobs_data.append(job_data)
        
        return TranscodingResponse(
            success=True,
            message="Transcoding jobs retrieved",
            data={
                "jobs": jobs_data,
                "pagination": {
                    "total": total_jobs,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_jobs
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list transcoding jobs: {e}")

@router.get("/profiles")
async def get_transcoding_profiles():
    """Get available transcoding profiles"""
    
    profiles_info = []
    
    for profile in TranscodingProfile:
        profile_config = transcoding_service.profiles_config.get(profile.value, {})
        
        profiles_info.append({
            "profile": profile.value,
            "name": profile_config.get("name", profile.value.replace("_", " ").title()),
            "description": profile_config.get("description", ""),
            "video_specs": profile_config.get("video", {}),
            "audio_specs": profile_config.get("audio", {}),
            "features": profile_config.get("features", []),
            "container": profile_config.get("video", {}).get("container") or profile_config.get("audio", {}).get("container")
        })
    
    return TranscodingResponse(
        success=True,
        message="Transcoding profiles retrieved",
        data={
            "profiles": profiles_info,
            "audio_standards": [
                {
                    "standard": standard.value,
                    "description": {
                        "atsc_a85": "ATSC A/85 (-24 LKFS) for US Television",
                        "ebu_r128": "EBU R128 (-23 LUFS) for European Television", 
                        "streaming": "Streaming optimized (-16 to -14 LUFS)",
                        "radio": "Radio broadcast (conservative peaks)"
                    }.get(standard.value, "")
                } for standard in AudioStandard
            ]
        }
    )

@router.post("/jobs/{job_id}/retry")
async def retry_transcoding_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Retry a failed transcoding job"""
    
    try:
        job = await transcoding_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Transcoding job not found")
        
        # Verify user ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if job.status != "failed":
            raise HTTPException(status_code=400, detail="Only failed jobs can be retried")
        
        if job.retry_count >= job.max_retries:
            raise HTTPException(status_code=400, detail="Maximum retry attempts exceeded")
        
        # Reset job status and increment retry count
        transcoding_service.transcoding_jobs_collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "queued",
                    "progress_percentage": 0.0,
                    "error_message": None,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$inc": {"retry_count": 1}
            }
        )
        
        # Start processing in background
        background_tasks.add_task(transcoding_service.process_transcoding_job, job_id)
        
        return TranscodingResponse(
            success=True,
            message="Transcoding job retry started",
            data={
                "job_id": job_id,
                "retry_count": job.retry_count + 1,
                "status": "queued"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retry transcoding job: {e}")

@router.delete("/jobs/{job_id}")
async def cancel_transcoding_job(
    job_id: str,
    current_user = Depends(get_current_user)
):
    """Cancel a transcoding job"""
    
    try:
        job = await transcoding_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Transcoding job not found")
        
        # Verify user ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if job.status in ["completed", "failed"]:
            raise HTTPException(status_code=400, detail="Cannot cancel completed or failed jobs")
        
        # Update job status to cancelled
        transcoding_service.transcoding_jobs_collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "cancelled",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return TranscodingResponse(
            success=True,
            message="Transcoding job cancelled",
            data={
                "job_id": job_id,
                "status": "cancelled"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel transcoding job: {e}")

@router.get("/statistics")
async def get_transcoding_statistics(current_user = Depends(get_current_user)):
    """Get transcoding statistics for the user"""
    
    try:
        user_id = current_user["user_id"]
        
        # Get job statistics
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_processing_time": {"$avg": "$processing_time_seconds"}
            }}
        ]
        
        status_stats = {}
        cursor = transcoding_service.transcoding_jobs_collection.aggregate(pipeline)
        
        for result in cursor:
            status_stats[result["_id"]] = {
                "count": result["count"],
                "avg_processing_time_seconds": result.get("avg_processing_time", 0)
            }
        
        # Get profile usage statistics
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$profile",
                "count": {"$sum": 1}
            }}
        ]
        
        profile_stats = {}
        cursor = transcoding_service.transcoding_jobs_collection.aggregate(pipeline)
        
        for result in cursor:
            profile_stats[result["_id"]] = result["count"]
        
        # Get total jobs count
        total_jobs = transcoding_service.transcoding_jobs_collection.count_documents({
            "user_id": user_id
        })
        
        return TranscodingResponse(
            success=True,
            message="Transcoding statistics retrieved",
            data={
                "total_jobs": total_jobs,
                "status_breakdown": status_stats,
                "profile_usage": profile_stats,
                "success_rate": (
                    status_stats.get("completed", {}).get("count", 0) / max(total_jobs, 1)
                ) * 100
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transcoding statistics: {e}")