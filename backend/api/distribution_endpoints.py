"""
Distribution Orchestration API Endpoints
Provides REST API for content distribution operations
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from distribution_orchestration_service import (
    DistributionOrchestrationService,
    DistributionJob,
    DeliveryMethod,
    DeliveryStatus,
    PlatformType
)

router = APIRouter(prefix="/api/distribution", tags=["Distribution"])
security = HTTPBearer()

# Initialize service
distribution_service = DistributionOrchestrationService()

# Request/Response Models
class DistributionRequest(BaseModel):
    content_id: str
    version_id: str
    platform_name: str
    delivery_profile_id: str
    source_files: List[Dict[str, str]]
    metadata: Dict[str, Any]

class BulkDistributionRequest(BaseModel):
    content_id: str
    version_id: str
    platforms: List[str]  # List of platform names
    source_files: List[Dict[str, str]]
    metadata: Dict[str, Any]

class DistributionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Authentication dependency (simplified)
async def get_current_user(token: str = Depends(security)):
    return {"user_id": "demo_user_123", "username": "demo_user"}

@router.get("/health")
async def distribution_health():
    """Health check for distribution service"""
    
    # Get available platforms count
    connectors = await distribution_service.get_platform_connectors()
    
    return {
        "status": "healthy",
        "service": "Distribution Orchestration Service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "available_platforms": len(connectors),
        "supported_delivery_methods": [method.value for method in DeliveryMethod],
        "platform_types": [ptype.value for ptype in PlatformType]
    }

@router.post("/jobs")
async def create_distribution_job(
    distribution_request: DistributionRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Create a new distribution job"""
    
    try:
        user_id = current_user["user_id"]
        
        # Create distribution job
        job = await distribution_service.create_distribution_job(
            content_id=distribution_request.content_id,
            version_id=distribution_request.version_id,
            user_id=user_id,
            platform_name=distribution_request.platform_name,
            delivery_profile_id=distribution_request.delivery_profile_id,
            source_files=distribution_request.source_files,
            metadata=distribution_request.metadata
        )
        
        # Start distribution in background
        background_tasks.add_task(distribution_service.execute_distribution_job, job.distribution_id)
        
        return DistributionResponse(
            success=True,
            message="Distribution job created and started",
            data={
                "distribution_id": job.distribution_id,
                "content_id": job.content_id,
                "platform_name": job.platform_name,
                "platform_type": job.platform_type.value,
                "delivery_method": job.delivery_method.value,
                "status": job.status.value,
                "created_at": job.created_at.isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create distribution job: {e}")

@router.post("/bulk")
async def create_bulk_distribution(
    bulk_request: BulkDistributionRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Create distribution jobs for multiple platforms"""
    
    try:
        user_id = current_user["user_id"]
        
        distribution_jobs = []
        
        for platform_name in bulk_request.platforms:
            # Find matching delivery profile for this platform
            delivery_profiles = list(distribution_service.db['delivery_profiles'].find({
                "channel": {"$regex": platform_name.lower()},
                "is_active": True
            }))
            
            if not delivery_profiles:
                # Use generic profile if specific one not found
                delivery_profiles = list(distribution_service.db['delivery_profiles'].find({
                    "is_active": True
                }).limit(1))
            
            if delivery_profiles:
                delivery_profile_id = delivery_profiles[0]["profile_id"]
                
                # Create distribution job
                job = await distribution_service.create_distribution_job(
                    content_id=bulk_request.content_id,
                    version_id=bulk_request.version_id,
                    user_id=user_id,
                    platform_name=platform_name,
                    delivery_profile_id=delivery_profile_id,
                    source_files=bulk_request.source_files,
                    metadata=bulk_request.metadata
                )
                
                distribution_jobs.append({
                    "distribution_id": job.distribution_id,
                    "platform_name": platform_name,
                    "status": job.status.value
                })
                
                # Start distribution in background
                background_tasks.add_task(distribution_service.execute_distribution_job, job.distribution_id)
        
        return DistributionResponse(
            success=True,
            message=f"Bulk distribution created for {len(distribution_jobs)} platforms",
            data={
                "content_id": bulk_request.content_id,
                "distribution_jobs": distribution_jobs,
                "total_platforms": len(distribution_jobs)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bulk distribution: {e}")

@router.get("/jobs/{distribution_id}")
async def get_distribution_job_status(
    distribution_id: str,
    current_user = Depends(get_current_user)
):
    """Get status of a distribution job"""
    
    try:
        job = await distribution_service.get_distribution_status(distribution_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Distribution job not found")
        
        # Verify user ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        job_data = {
            "distribution_id": job.distribution_id,
            "content_id": job.content_id,
            "version_id": job.version_id,
            "platform_name": job.platform_name,
            "platform_type": job.platform_type.value,
            "delivery_method": job.delivery_method.value,
            "status": job.status.value,
            "progress_percentage": job.progress_percentage,
            "platform_response": job.platform_response,
            "platform_content_id": job.platform_content_id,
            "delivery_receipt": job.delivery_receipt,
            "created_at": job.created_at.isoformat(),
            "error_message": job.error_message
        }
        
        if job.delivery_started_at:
            job_data["delivery_started_at"] = job.delivery_started_at.isoformat()
        if job.delivery_completed_at:
            job_data["delivery_completed_at"] = job.delivery_completed_at.isoformat()
        if job.verification_completed_at:
            job_data["verification_completed_at"] = job.verification_completed_at.isoformat()
        
        return DistributionResponse(
            success=True,
            message="Distribution job status retrieved",
            data=job_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {e}")

@router.get("/jobs")
async def list_distribution_jobs(
    status: Optional[str] = None,
    platform_name: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """List distribution jobs for the current user"""
    
    try:
        user_id = current_user["user_id"]
        
        # Build query
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        if platform_name:
            query["platform_name"] = platform_name
        
        # Get jobs from database
        jobs_data = list(distribution_service.distribution_jobs_collection.find(query).sort("created_at", -1))
        
        # Apply pagination
        total_jobs = len(jobs_data)
        paginated_jobs_data = jobs_data[offset:offset + limit]
        
        jobs = []
        for job_data in paginated_jobs_data:
            job_data["_id"] = str(job_data["_id"])
            job = DistributionJob(**job_data)
            
            job_info = {
                "distribution_id": job.distribution_id,
                "content_id": job.content_id,
                "platform_name": job.platform_name,
                "platform_type": job.platform_type.value,
                "status": job.status.value,
                "progress_percentage": job.progress_percentage,
                "platform_content_id": job.platform_content_id,
                "created_at": job.created_at.isoformat()
            }
            
            if job.delivery_completed_at:
                job_info["delivery_completed_at"] = job.delivery_completed_at.isoformat()
                
            jobs.append(job_info)
        
        return DistributionResponse(
            success=True,
            message="Distribution jobs retrieved",
            data={
                "jobs": jobs,
                "pagination": {
                    "total": total_jobs,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_jobs
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list distribution jobs: {e}")

@router.get("/platforms")
async def get_platform_connectors():
    """Get available platform connectors"""
    
    try:
        connectors = await distribution_service.get_platform_connectors()
        
        connectors_data = []
        for connector in connectors:
            connector_info = {
                "platform_name": connector.platform_name,
                "platform_type": connector.platform_type.value,
                "api_base_url": connector.api_base_url,
                "authentication_method": connector.authentication_method,
                "required_credentials": connector.required_credentials,
                "supported_formats": connector.supported_formats,
                "max_file_size_mb": connector.max_file_size_mb,
                "metadata_requirements": connector.metadata_requirements
            }
            connectors_data.append(connector_info)
        
        # Group by platform type
        platforms_by_type = {}
        for connector in connectors_data:
            ptype = connector["platform_type"]
            if ptype not in platforms_by_type:
                platforms_by_type[ptype] = []
            platforms_by_type[ptype].append(connector)
        
        return DistributionResponse(
            success=True,
            message="Platform connectors retrieved",
            data={
                "connectors": connectors_data,
                "platforms_by_type": platforms_by_type,
                "total_platforms": len(connectors_data)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform connectors: {e}")

@router.post("/jobs/{distribution_id}/retry")
async def retry_distribution_job(
    distribution_id: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Retry a failed distribution job"""
    
    try:
        job = await distribution_service.get_distribution_status(distribution_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Distribution job not found")
        
        # Verify user ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if job.status != DeliveryStatus.FAILED:
            raise HTTPException(status_code=400, detail="Only failed jobs can be retried")
        
        if job.retry_count >= job.max_retries:
            raise HTTPException(status_code=400, detail="Maximum retry attempts exceeded")
        
        # Reset job status and increment retry count
        distribution_service.distribution_jobs_collection.update_one(
            {"distribution_id": distribution_id},
            {
                "$set": {
                    "status": DeliveryStatus.QUEUED.value,
                    "progress_percentage": 0.0,
                    "error_message": None,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$inc": {"retry_count": 1}
            }
        )
        
        # Start distribution in background
        background_tasks.add_task(distribution_service.execute_distribution_job, distribution_id)
        
        return DistributionResponse(
            success=True,
            message="Distribution job retry started",
            data={
                "distribution_id": distribution_id,
                "retry_count": job.retry_count + 1,
                "status": DeliveryStatus.QUEUED.value
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retry distribution job: {e}")

@router.get("/content/{content_id}/distributions")
async def get_content_distributions(
    content_id: str,
    current_user = Depends(get_current_user)
):
    """Get all distributions for a specific content"""
    
    try:
        user_id = current_user["user_id"]
        
        jobs = await distribution_service.list_user_distributions(user_id)
        content_distributions = [job for job in jobs if job.content_id == content_id]
        
        distributions_data = []
        for job in content_distributions:
            distribution_info = {
                "distribution_id": job.distribution_id,
                "platform_name": job.platform_name,
                "platform_type": job.platform_type.value,
                "status": job.status.value,
                "progress_percentage": job.progress_percentage,
                "platform_content_id": job.platform_content_id,
                "created_at": job.created_at.isoformat()
            }
            
            if job.delivery_completed_at:
                distribution_info["delivery_completed_at"] = job.delivery_completed_at.isoformat()
            
            distributions_data.append(distribution_info)
        
        # Group by status
        status_summary = {}
        for dist in distributions_data:
            status = dist["status"]
            if status not in status_summary:
                status_summary[status] = 0
            status_summary[status] += 1
        
        return DistributionResponse(
            success=True,
            message="Content distributions retrieved",
            data={
                "content_id": content_id,
                "distributions": distributions_data,
                "total_distributions": len(distributions_data),
                "status_summary": status_summary
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content distributions: {e}")

@router.get("/statistics")
async def get_distribution_statistics(current_user = Depends(get_current_user)):
    """Get distribution statistics for the user"""
    
    try:
        user_id = current_user["user_id"]
        
        # Get job statistics by status
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_stats = {}
        cursor = distribution_service.distribution_jobs_collection.aggregate(pipeline)
        
        for result in cursor:
            status_stats[result["_id"]] = result["count"]
        
        # Get platform statistics
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$platform_name",
                "count": {"$sum": 1},
                "success_count": {
                    "$sum": {
                        "$cond": [
                            {"$in": ["$status", ["delivered", "verified"]]},
                            1,
                            0
                        ]
                    }
                }
            }}
        ]
        
        platform_stats = {}
        cursor = distribution_service.distribution_jobs_collection.aggregate(pipeline)
        
        for result in cursor:
            platform_stats[result["_id"]] = {
                "total_distributions": result["count"],
                "successful_distributions": result["success_count"],
                "success_rate": (result["success_count"] / result["count"]) * 100
            }
        
        # Get delivery method statistics
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$delivery_method",
                "count": {"$sum": 1}
            }}
        ]
        
        delivery_method_stats = {}
        cursor = distribution_service.distribution_jobs_collection.aggregate(pipeline)
        
        for result in cursor:
            delivery_method_stats[result["_id"]] = result["count"]
        
        # Calculate overall success rate
        total_jobs = sum(status_stats.values())
        successful_jobs = status_stats.get("delivered", 0) + status_stats.get("verified", 0)
        overall_success_rate = (successful_jobs / max(total_jobs, 1)) * 100
        
        return DistributionResponse(
            success=True,
            message="Distribution statistics retrieved",
            data={
                "total_distributions": total_jobs,
                "overall_success_rate": overall_success_rate,
                "status_breakdown": status_stats,
                "platform_performance": platform_stats,
                "delivery_method_usage": delivery_method_stats
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get distribution statistics: {e}")