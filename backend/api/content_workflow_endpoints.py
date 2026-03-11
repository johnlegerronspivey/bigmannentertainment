"""
Content Workflow API Endpoints
Provides REST API for the end-to-end content distribution workflow
"""

import os
import uuid
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from content_workflow_service import (
    ContentWorkflowService, 
    MasterContent, 
    ContentVersion, 
    TechnicalQCResult,
    ContentType,
    QualityProfile,
    DistributionChannel,
    WorkflowStage
)

router = APIRouter(prefix="/api/workflow", tags=["Content Workflow"])
security = HTTPBearer()

# Initialize service
workflow_service = ContentWorkflowService()

# Request/Response Models
class MasterContentRequest(BaseModel):
    content_type: ContentType
    title: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ContentVersionRequest(BaseModel):
    quality_profile: QualityProfile
    version_name: Optional[str] = None
    changes_summary: str = ""

class WorkflowRequest(BaseModel):
    target_profiles: List[QualityProfile]
    target_channels: List[DistributionChannel]
    auto_progress: bool = True
    require_approval: List[WorkflowStage] = []

class WorkflowResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Authentication dependency (simplified)
async def get_current_user(token: str = Depends(security)):
    # In production, implement proper JWT token validation
    return {"user_id": "demo_user_123", "username": "demo_user"}

@router.get("/health")
async def workflow_health():
    """Health check for workflow service"""
    return {
        "status": "healthy",
        "service": "Content Workflow Service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "master_intake": "operational",
            "versioning": "operational", 
            "technical_qc": "operational",
            "transcoding": "operational",
            "distribution": "operational"
        }
    }

@router.get("/dashboard")
async def get_workflow_dashboard(current_user = Depends(get_current_user)):
    """Get workflow dashboard data"""
    
    try:
        user_id = current_user["user_id"]
        
        # Get master content summary
        master_content_count = workflow_service.master_content_collection.count_documents({
            "user_id": user_id
        })
        
        # Get versions summary
        versions_count = workflow_service.content_versions_collection.count_documents({
            "created_by": user_id
        })
        
        # Get QC results summary
        qc_results = list(workflow_service.technical_qc_collection.find({
            "performed_by": {"$regex": user_id}
        }))
        
        qc_summary = {
            "total_qc_runs": len(qc_results),
            "passed": len([r for r in qc_results if r.get("overall_status") == "passed"]),
            "failed": len([r for r in qc_results if r.get("overall_status") == "failed"]),
            "warnings": len([r for r in qc_results if r.get("overall_status") == "warning"])
        }
        
        # Get delivery profiles
        delivery_profiles = list(workflow_service.delivery_profiles_collection.find({
            "is_active": True
        }))
        
        channels_summary = {}
        for profile in delivery_profiles:
            channel = profile.get("channel")
            if channel not in channels_summary:
                channels_summary[channel] = 0
            channels_summary[channel] += 1
        
        return {
            "success": True,
            "dashboard": {
                "content_summary": {
                    "master_content_pieces": master_content_count,
                    "total_versions": versions_count,
                    "storage_used_gb": 0.0  # Placeholder
                },
                "quality_assurance": qc_summary,
                "distribution_channels": {
                    "available_channels": len(channels_summary),
                    "channels_by_type": channels_summary,
                    "total_delivery_profiles": len(delivery_profiles)
                },
                "recent_activity": []  # Placeholder for recent workflow activities
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {e}")

@router.post("/ingest")
async def ingest_master_content(
    file: UploadFile = File(...),
    content_type: ContentType = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    current_user = Depends(get_current_user)
):
    """Ingest master content file"""
    
    try:
        user_id = current_user["user_id"]
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Prepare metadata
        metadata = {
            "title": title,
            "description": description,
            "original_filename": file.filename,
            "content_type": file.content_type
        }
        
        # Ingest master content
        master_content = await workflow_service.ingest_master_content(
            user_id=user_id,
            file_path=temp_file_path,
            content_type=content_type,
            metadata=metadata
        )
        
        return WorkflowResponse(
            success=True,
            message="Master content ingested successfully",
            data={
                "content_id": master_content.content_id,
                "title": master_content.title,
                "file_size": master_content.file_size,
                "checksum_sha256": master_content.checksum_sha256,
                "content_type": master_content.content_type.value
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest content: {e}")

@router.post("/content/{content_id}/version")
async def create_content_version(
    content_id: str,
    version_request: ContentVersionRequest,
    current_user = Depends(get_current_user)
):
    """Create a new immutable version of content"""
    
    try:
        user_id = current_user["user_id"]
        
        version = await workflow_service.create_content_version(
            content_id=content_id,
            user_id=user_id,
            quality_profile=version_request.quality_profile,
            version_name=version_request.version_name,
            changes_summary=version_request.changes_summary
        )
        
        return WorkflowResponse(
            success=True,
            message="Content version created successfully",
            data={
                "version_id": version.version_id,
                "version_number": version.version_number,
                "version_name": version.version_name,
                "quality_profile": version.quality_profile.value,
                "file_size": version.file_size,
                "is_current": version.is_current,
                "checksum_sha256": version.checksum_sha256
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create version: {e}")

@router.post("/qc/{version_id}")
async def perform_technical_qc(
    version_id: str,
    target_profile: Optional[QualityProfile] = None,
    current_user = Depends(get_current_user)
):
    """Perform technical quality control on content version"""
    
    try:
        # Get version to find content_id
        version = workflow_service.content_versions_collection.find_one({
            "version_id": version_id
        })
        
        if not version:
            raise HTTPException(status_code=404, detail="Content version not found")
        
        content_id = version["content_id"]
        
        qc_result = await workflow_service.perform_technical_qc(
            content_id=content_id,
            version_id=version_id,
            target_profile=target_profile
        )
        
        return WorkflowResponse(
            success=True,
            message="Technical QC completed",
            data={
                "qc_id": qc_result.qc_id,
                "overall_status": qc_result.overall_status,
                "qc_score": qc_result.qc_score,
                "checks": {
                    "frame_rate": qc_result.frame_rate_check,
                    "resolution": qc_result.resolution_check,
                    "bit_rate": qc_result.bit_rate_check,
                    "color_range": qc_result.color_range_check,
                    "loudness": qc_result.loudness_check,
                    "true_peak": qc_result.true_peak_check,
                    "pse_safe": qc_result.pse_flash_check
                },
                "critical_issues": qc_result.critical_issues,
                "warnings": qc_result.warnings,
                "suggestions": qc_result.suggestions
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QC failed: {e}")

@router.get("/content/{content_id}")
async def get_content_details(
    content_id: str,
    current_user = Depends(get_current_user)
):
    """Get detailed information about content and its versions"""
    
    try:
        user_id = current_user["user_id"]
        
        # Get master content
        master_content = workflow_service.master_content_collection.find_one({
            "content_id": content_id,
            "user_id": user_id
        })
        
        if not master_content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Get all versions
        versions = list(workflow_service.content_versions_collection.find({
            "content_id": content_id,
            "created_by": user_id
        }).sort("created_at", -1))
        
        # Get QC results
        qc_results = list(workflow_service.technical_qc_collection.find({
            "content_id": content_id
        }).sort("performed_at", -1))
        
        # Clean up MongoDB ObjectIds
        for item in [master_content] + versions + qc_results:
            if "_id" in item:
                item["_id"] = str(item["_id"])
        
        return WorkflowResponse(
            success=True,
            message="Content details retrieved",
            data={
                "master_content": master_content,
                "versions": versions,
                "qc_results": qc_results,
                "version_count": len(versions),
                "latest_qc_status": qc_results[0].get("overall_status") if qc_results else "not_tested"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content details: {e}")

@router.get("/content")
async def list_user_content(
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """List all content for the current user"""
    
    try:
        user_id = current_user["user_id"]
        
        # Get master content with pagination
        cursor = workflow_service.master_content_collection.find({
            "user_id": user_id
        }).sort("created_at", -1).skip(offset).limit(limit)
        
        content_list = []
        for content in cursor:
            # Get version count
            version_count = workflow_service.content_versions_collection.count_documents({
                "content_id": content["content_id"]
            })
            
            # Get latest QC status
            latest_qc = workflow_service.technical_qc_collection.find_one({
                "content_id": content["content_id"]
            }, sort=[("performed_at", -1)])
            
            content["_id"] = str(content["_id"])
            content["version_count"] = version_count
            content["latest_qc_status"] = latest_qc.get("overall_status") if latest_qc else "not_tested"
            
            content_list.append(content)
        
        # Get total count
        total_count = workflow_service.master_content_collection.count_documents({
            "user_id": user_id
        })
        
        return WorkflowResponse(
            success=True,
            message="Content list retrieved",
            data={
                "content": content_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list content: {e}")

@router.get("/delivery-profiles")
async def get_delivery_profiles(current_user = Depends(get_current_user)):
    """Get available delivery profiles for distribution channels"""
    
    try:
        profiles = list(workflow_service.delivery_profiles_collection.find({
            "is_active": True
        }))
        
        # Clean up MongoDB ObjectIds
        for profile in profiles:
            profile["_id"] = str(profile["_id"])
        
        # Group by channel
        profiles_by_channel = {}
        for profile in profiles:
            channel = profile.get("channel")
            if channel not in profiles_by_channel:
                profiles_by_channel[channel] = []
            profiles_by_channel[channel].append(profile)
        
        return WorkflowResponse(
            success=True,
            message="Delivery profiles retrieved",
            data={
                "profiles": profiles,
                "profiles_by_channel": profiles_by_channel,
                "total_profiles": len(profiles),
                "available_channels": list(profiles_by_channel.keys())
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get delivery profiles: {e}")

@router.get("/enums")
async def get_workflow_enums():
    """Get all enum values for workflow configuration"""
    
    return {
        "content_types": [ct.value for ct in ContentType],
        "quality_profiles": [qp.value for qp in QualityProfile],
        "distribution_channels": [dc.value for dc in DistributionChannel],
        "workflow_stages": [ws.value for ws in WorkflowStage]
    }

@router.post("/content/{content_id}/workflow")
async def create_content_workflow(
    content_id: str,
    workflow_request: WorkflowRequest,
    current_user = Depends(get_current_user)
):
    """Create a new workflow for content distribution"""
    
    try:
        user_id = current_user["user_id"]
        
        # Verify content exists
        master_content = workflow_service.master_content_collection.find_one({
            "content_id": content_id,
            "user_id": user_id
        })
        
        if not master_content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Create workflow (simplified implementation)
        workflow_id = str(uuid.uuid4())
        
        workflow_data = {
            "workflow_id": workflow_id,
            "content_id": content_id,
            "user_id": user_id,
            "current_stage": WorkflowStage.INTAKE.value,
            "overall_status": "created",
            "target_profiles": [profile.value for profile in workflow_request.target_profiles],
            "target_channels": [channel.value for channel in workflow_request.target_channels],
            "auto_progress": workflow_request.auto_progress,
            "require_approval": [stage.value for stage in workflow_request.require_approval],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        workflow_service.content_workflows_collection.insert_one(workflow_data)
        
        return WorkflowResponse(
            success=True,
            message="Content workflow created",
            data={
                "workflow_id": workflow_id,
                "content_id": content_id,
                "target_profiles": workflow_request.target_profiles,
                "target_channels": workflow_request.target_channels,
                "current_stage": WorkflowStage.INTAKE.value
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {e}")

@router.get("/workflows")
async def list_workflows(
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """List workflows for the current user"""
    
    try:
        user_id = current_user["user_id"]
        
        query = {"user_id": user_id}
        if status:
            query["overall_status"] = status
        
        workflows = list(workflow_service.content_workflows_collection.find(query).sort("updated_at", -1))
        
        # Clean up MongoDB ObjectIds and add content info
        for workflow in workflows:
            workflow["_id"] = str(workflow["_id"])
            
            # Get content title
            content = workflow_service.master_content_collection.find_one({
                "content_id": workflow["content_id"]
            })
            workflow["content_title"] = content.get("title", "Unknown") if content else "Unknown"
        
        return WorkflowResponse(
            success=True,
            message="Workflows retrieved",
            data={
                "workflows": workflows,
                "total_workflows": len(workflows)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {e}")