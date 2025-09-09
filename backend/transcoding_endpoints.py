"""
Transcoding API Endpoints - Function 2: Transcoding & Format Optimization
Provides API endpoints for transcoding jobs, format optimization, and quality presets.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json

from transcoding_service import (
    TranscodingService, 
    TranscodingJob, 
    TranscodingStatus,
    QualityPreset,
    OutputFormat,
    TranscodingPreset
)
from format_optimization_service import (
    FormatOptimizationService,
    PlatformType,
    PlatformRequirement,
    OptimizationRule
)

# Initialize services
transcoding_service = TranscodingService()
format_optimization_service = FormatOptimizationService()

# Create router
router = APIRouter(prefix="/api/transcoding", tags=["Transcoding & Format Optimization"])
security = HTTPBearer()

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This would integrate with your authentication system
    # For now, returning a mock user ID
    return "user_123"

# Transcoding Job Management Endpoints

@router.post("/jobs/create")
async def create_transcoding_job(
    content_id: str,
    input_file_path: str,
    input_format: str,
    output_format: OutputFormat,
    quality_preset: QualityPreset = QualityPreset.MEDIUM,
    platform_target: Optional[str] = None,
    custom_settings: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user)
):
    """Create a new transcoding job"""
    try:
        transcoding_job = await transcoding_service.create_transcoding_job(
            user_id=user_id,
            content_id=content_id,
            input_file_path=input_file_path,
            input_format=input_format,
            output_format=output_format,
            quality_preset=quality_preset,
            platform_target=platform_target,
            custom_settings=custom_settings or {}
        )
        
        return {
            "success": True,
            "transcoding_job": transcoding_job,
            "message": "Transcoding job created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/start")
async def start_transcoding_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Start processing a transcoding job"""
    try:
        success = await transcoding_service.start_transcoding_job(job_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Transcoding job not found or cannot be started")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Transcoding job started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}")
async def get_transcoding_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get transcoding job details"""
    try:
        job = await transcoding_service.get_transcoding_job(job_id, user_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Transcoding job not found")
        
        return {
            "success": True,
            "transcoding_job": job
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_transcoding_jobs(
    status: Optional[TranscodingStatus] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user)
):
    """List transcoding jobs for user"""
    try:
        jobs = await transcoding_service.list_user_transcoding_jobs(
            user_id=user_id,
            status_filter=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "transcoding_jobs": jobs,
            "total_jobs": len(jobs),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/cancel")
async def cancel_transcoding_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Cancel a transcoding job"""
    try:
        success = await transcoding_service.cancel_transcoding_job(job_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Transcoding job not found or cannot be cancelled")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Transcoding job cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/progress")
async def get_transcoding_progress(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get real-time transcoding progress"""
    try:
        job = await transcoding_service.get_transcoding_job(job_id, user_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Transcoding job not found")
        
        return {
            "success": True,
            "job_id": job_id,
            "status": job.status,
            "progress_percentage": job.progress_percentage,
            "estimated_duration": job.estimated_duration,
            "actual_duration": job.actual_duration,
            "error_message": job.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Preset Management Endpoints

@router.get("/presets")
async def get_available_presets(user_id: str = Depends(get_current_user)):
    """Get all available transcoding presets"""
    try:
        presets = transcoding_service.get_available_presets()
        
        return {
            "success": True,
            "presets": presets,
            "total_presets": len(presets)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/presets/platform/{platform_name}")
async def get_presets_for_platform(
    platform_name: str,
    user_id: str = Depends(get_current_user)
):
    """Get presets optimized for a specific platform"""
    try:
        presets = transcoding_service.get_presets_for_platform(platform_name)
        
        return {
            "success": True,
            "platform": platform_name,
            "presets": presets,
            "total_presets": len(presets)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/presets/format/{output_format}")
async def get_presets_for_format(
    output_format: OutputFormat,
    user_id: str = Depends(get_current_user)
):
    """Get presets for a specific output format"""
    try:
        presets = transcoding_service.get_presets_for_format(output_format)
        
        return {
            "success": True,
            "output_format": output_format,
            "presets": presets,
            "total_presets": len(presets)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Format Optimization Endpoints

@router.get("/platforms")
async def get_platform_requirements(user_id: str = Depends(get_current_user)):
    """Get format requirements for all supported platforms"""
    try:
        platforms = {}
        for platform_name, req in format_optimization_service.platform_requirements.items():
            platforms[platform_name] = req.dict()
        
        return {
            "success": True,
            "platforms": platforms,
            "total_platforms": len(platforms)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/{platform_name}")
async def get_platform_requirements_detail(
    platform_name: str,
    user_id: str = Depends(get_current_user)
):
    """Get detailed format requirements for a specific platform"""
    try:
        req = format_optimization_service.get_platform_requirements(platform_name)
        
        if not req:
            raise HTTPException(status_code=404, detail=f"Platform {platform_name} not found")
        
        return {
            "success": True,
            "platform_requirements": req
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/type/{platform_type}")
async def get_platforms_by_type(
    platform_type: PlatformType,
    user_id: str = Depends(get_current_user)
):
    """Get all platforms of a specific type"""
    try:
        platforms = format_optimization_service.get_platforms_by_type(platform_type)
        
        return {
            "success": True,
            "platform_type": platform_type,
            "platforms": platforms,
            "total_platforms": len(platforms)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_content_for_platform(
    platform_name: str,
    content_metadata: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Validate if content meets platform requirements"""
    try:
        is_valid, issues = format_optimization_service.validate_content_for_platform(
            platform_name, content_metadata
        )
        
        return {
            "success": True,
            "platform": platform_name,
            "is_valid": is_valid,
            "validation_issues": issues,
            "total_issues": len(issues)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/recommendations")
async def get_optimization_recommendations(
    platform_name: str,
    content_metadata: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user)
):
    """Get optimization recommendations for specific platform and content"""
    try:
        recommendations = format_optimization_service.get_optimization_recommendations(
            platform_name, content_metadata, user_preferences or {}
        )
        
        return {
            "success": True,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/preset")
async def create_optimized_preset(
    platform_name: str,
    content_metadata: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user)
):
    """Create a custom transcoding preset optimized for specific platform"""
    try:
        preset = format_optimization_service.create_optimized_transcoding_preset(
            platform_name, content_metadata, user_preferences or {}
        )
        
        if not preset:
            raise HTTPException(status_code=400, detail=f"Could not create optimized preset for {platform_name}")
        
        return {
            "success": True,
            "optimized_preset": preset,
            "message": f"Optimized preset created for {platform_name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/multi-platform")
async def get_multi_platform_optimization(
    target_platforms: List[str],
    content_metadata: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Get optimization strategy for multiple platforms"""
    try:
        optimization = format_optimization_service.get_multi_platform_optimization(
            target_platforms, content_metadata
        )
        
        return {
            "success": True,
            "multi_platform_optimization": optimization
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics and Analytics Endpoints

@router.get("/stats")
async def get_transcoding_stats(user_id: str = Depends(get_current_user)):
    """Get transcoding statistics for user"""
    try:
        stats = await transcoding_service.get_transcoding_stats(user_id)
        
        return {
            "success": True,
            "transcoding_stats": stats,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formats/supported")
async def get_supported_formats(user_id: str = Depends(get_current_user)):
    """Get all supported input and output formats"""
    try:
        supported_formats = {
            "input_formats": [
                "mp4", "avi", "mov", "mkv", "webm", "flv", "3gp",
                "mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"
            ],
            "output_formats": [format.value for format in OutputFormat],
            "quality_presets": [preset.value for preset in QualityPreset],
            "ffmpeg_available": transcoding_service.ffmpeg_available
        }
        
        return {
            "success": True,
            "supported_formats": supported_formats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/{platform_name}/formats")
async def get_supported_formats_for_platform(
    platform_name: str,
    user_id: str = Depends(get_current_user)
):
    """Get supported formats for a specific platform"""
    try:
        formats = format_optimization_service.get_supported_formats_for_platform(platform_name)
        
        if not formats:
            raise HTTPException(status_code=404, detail=f"Platform {platform_name} not found")
        
        optimal_format = format_optimization_service.get_optimal_format_for_platform(platform_name)
        
        return {
            "success": True,
            "platform": platform_name,
            "supported_formats": [f.value for f in formats],
            "optimal_format": optimal_format.value if optimal_format else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch Operations

@router.post("/jobs/batch")
async def create_batch_transcoding_jobs(
    jobs_config: List[Dict[str, Any]],
    user_id: str = Depends(get_current_user)
):
    """Create multiple transcoding jobs at once"""
    try:
        created_jobs = []
        failed_jobs = []
        
        for i, job_config in enumerate(jobs_config):
            try:
                # Validate required fields
                required_fields = ["content_id", "input_file_path", "input_format", "output_format"]
                for field in required_fields:
                    if field not in job_config:
                        raise ValueError(f"Missing required field: {field}")
                
                # Create transcoding job
                transcoding_job = await transcoding_service.create_transcoding_job(
                    user_id=user_id,
                    content_id=job_config["content_id"],
                    input_file_path=job_config["input_file_path"],
                    input_format=job_config["input_format"],
                    output_format=OutputFormat(job_config["output_format"]),
                    quality_preset=QualityPreset(job_config.get("quality_preset", "medium")),
                    platform_target=job_config.get("platform_target"),
                    custom_settings=job_config.get("custom_settings", {})
                )
                
                created_jobs.append({
                    "index": i,
                    "job_id": transcoding_job.job_id,
                    "content_id": job_config["content_id"]
                })
                
            except Exception as e:
                failed_jobs.append({
                    "index": i,
                    "content_id": job_config.get("content_id", "unknown"),
                    "error": str(e)
                })
        
        return {
            "success": len(failed_jobs) == 0,
            "created_jobs": created_jobs,
            "failed_jobs": failed_jobs,
            "total_requested": len(jobs_config),
            "total_created": len(created_jobs),
            "total_failed": len(failed_jobs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/batch/start")
async def start_batch_transcoding_jobs(
    job_ids: List[str],
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Start multiple transcoding jobs at once"""
    try:
        started_jobs = []
        failed_jobs = []
        
        for job_id in job_ids:
            try:
                success = await transcoding_service.start_transcoding_job(job_id, user_id)
                if success:
                    started_jobs.append(job_id)
                else:
                    failed_jobs.append({"job_id": job_id, "error": "Job not found or cannot be started"})
                    
            except Exception as e:
                failed_jobs.append({"job_id": job_id, "error": str(e)})
        
        return {
            "success": len(failed_jobs) == 0,
            "started_jobs": started_jobs,
            "failed_jobs": failed_jobs,
            "total_requested": len(job_ids),
            "total_started": len(started_jobs),
            "total_failed": len(failed_jobs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Status and Health Check

@router.get("/health")
async def health_check():
    """Health check endpoint for transcoding service"""
    try:
        health_status = {
            "service": "Transcoding & Format Optimization API",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "ffmpeg_available": transcoding_service.ffmpeg_available,
            "total_presets": len(transcoding_service.get_available_presets()),
            "supported_platforms": len(format_optimization_service.platform_requirements),
            "optimization_rules": len(format_optimization_service.optimization_rules)
        }
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }

@router.post("/cleanup")
async def cleanup_old_jobs(
    older_than_days: int = Query(7, ge=1, le=365),
    user_id: str = Depends(get_current_user)  # This would need admin check in real implementation
):
    """Clean up old completed transcoding jobs"""
    try:
        cleaned_count = await transcoding_service.cleanup_completed_jobs(older_than_days)
        
        return {
            "success": True,
            "cleaned_jobs": cleaned_count,
            "older_than_days": older_than_days,
            "message": f"Cleaned up {cleaned_count} old transcoding jobs"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))