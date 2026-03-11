"""
Content Removal API Endpoints
RESTful API for content takedown and removal management
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Header
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import aiofiles
import io
import csv
import json
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

from content_removal_service import ContentRemovalService
from content_removal_models import (
    RemovalRequest, RemovalRequestCreate, RemovalRequestUpdate,
    RemovalStatus, RemovalUrgency, RemovalReason,
    DisputeRequest, RemovalAnalytics, ComplianceReport,
    RemovalEvidence
)

router = APIRouter(prefix="/content-removal", tags=["Content Removal"])

# Dependency injection (will be set by main server)
removal_service: ContentRemovalService = None

def init_removal_service(db: AsyncIOMotorDatabase):
    """Initialize removal service with database connection"""
    global removal_service
    removal_service = ContentRemovalService(db)

def get_removal_service():
    """Get removal service instance"""
    if removal_service is None:
        raise HTTPException(status_code=500, detail="Removal service not initialized")
    return removal_service

# Authentication dependencies (imported from main server)
async def get_current_user_for_removal(authorization: str = Header(None)):
    """Get current user dependency for removal endpoints"""
    try:
        from auth.service import get_current_user
        # Call the actual authentication function
        return await get_current_user(authorization)
    except ImportError:
        raise HTTPException(status_code=500, detail="Authentication system not available")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_current_admin_user_for_removal(authorization: str = Header(None)):
    """Get current admin user dependency - requires admin role"""
    try:
        from auth.service import get_current_user
        # Get the user first
        user = await get_current_user(authorization)
        
        # Check if user has admin role
        user_role = user.get('role', '').lower()
        is_admin = user.get('is_admin', False)
        
        if not is_admin and user_role not in ['admin', 'super_admin', 'legal']:
            raise HTTPException(
                status_code=403, 
                detail="Admin access required. Current role: " + user_role
            )
        return user
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=500, detail="Authentication system not available")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Set up the dependency functions
get_current_user = get_current_user_for_removal
get_current_admin_user = get_current_admin_user_for_removal

@router.post("/requests", response_model=RemovalRequest)
async def create_removal_request(
    request_data: RemovalRequestCreate,
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Create a new content removal request"""
    try:
        removal_request = await service.create_removal_request(
            request_data=request_data,
            requester_id=current_user["id"],
            requester_role=current_user["role"]
        )
        return removal_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create removal request: {str(e)}")

@router.get("/requests", response_model=List[RemovalRequest])
async def get_removal_requests(
    status: Optional[RemovalStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Get removal requests for current user"""
    try:
        requests = await service.get_removal_requests(
            user_id=current_user["id"],
            user_role=current_user["role"],
            status=status,
            limit=limit,
            offset=offset
        )
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch requests: {str(e)}")

@router.get("/requests/{request_id}", response_model=RemovalRequest)
async def get_removal_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Get specific removal request"""
    try:
        request = await service.get_removal_request(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Removal request not found")
        
        # Check permissions
        if current_user["role"] not in ["admin", "super_admin"] and request.requested_by != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return request
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch request: {str(e)}")

@router.put("/requests/{request_id}", response_model=RemovalRequest)
async def update_removal_request(
    request_id: str,
    update_data: RemovalRequestUpdate,
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Update removal request (limited fields for creators)"""
    try:
        # Get existing request
        existing_request = await service.get_removal_request(request_id)
        if not existing_request:
            raise HTTPException(status_code=404, detail="Removal request not found")
        
        # Check permissions
        if current_user["role"] not in ["admin", "super_admin"] and existing_request.requested_by != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Only allow updates to pending requests
        if existing_request.status != RemovalStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot update non-pending requests")
        
        # Creators can only update limited fields
        if current_user["role"] not in ["admin", "super_admin"]:
            # Restrict what creators can update
            allowed_updates = {}
            if update_data.target_platforms is not None:
                allowed_updates["target_platforms"] = update_data.target_platforms
            if update_data.territory_scope is not None:
                allowed_updates["territory_scope"] = update_data.territory_scope
            if update_data.effective_date is not None:
                allowed_updates["effective_date"] = update_data.effective_date
            
            update_data = RemovalRequestUpdate(**allowed_updates)
        
        # Perform update (this would need to be implemented in the service)
        # For now, return the existing request
        return existing_request
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update request: {str(e)}")

@router.post("/requests/{request_id}/approve", response_model=RemovalRequest)
async def approve_removal_request(
    request_id: str,
    notes: Optional[str] = Form(None, description="Approval notes"),
    current_user: dict = Depends(get_current_admin_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Approve removal request (admin only)"""
    try:
        approved_request = await service.approve_removal_request(
            request_id=request_id,
            approver_id=current_user["id"],
            notes=notes
        )
        return approved_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve request: {str(e)}")

@router.post("/requests/{request_id}/reject", response_model=RemovalRequest)
async def reject_removal_request(
    request_id: str,
    reason: str = Form(..., description="Rejection reason"),
    current_user: dict = Depends(get_current_admin_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Reject removal request (admin only)"""
    try:
        rejected_request = await service.reject_removal_request(
            request_id=request_id,
            rejector_id=current_user["id"],
            reason=reason
        )
        return rejected_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject request: {str(e)}")

@router.post("/requests/{request_id}/evidence")
async def upload_evidence(
    request_id: str,
    file: UploadFile = File(...),
    description: str = Form(..., description="Evidence description"),
    file_type: str = Form(..., description="Evidence type (legal_notice, correspondence, etc.)"),
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Upload evidence file for removal request"""
    try:
        # Validate request exists and user has permission
        request = await service.get_removal_request(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Removal request not found")
        
        if current_user["role"] not in ["admin", "super_admin"] and request.requested_by != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate file
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Create evidence record
        evidence_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        filename = f"evidence_{evidence_id}{file_extension}"
        file_path = f"/app/uploads/removal_evidence/{filename}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create evidence record
        evidence = RemovalEvidence(
            id=evidence_id,
            file_path=file_path,
            file_type=file_type,
            file_name=file.filename or filename,
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            description=description,
            uploaded_by=current_user["id"]
        )
        
        # Store evidence in database
        await service.evidence_collection.insert_one(evidence.dict())
        
        # Add evidence to removal request
        await service.collection.update_one(
            {"id": request_id},
            {
                "$push": {"evidence_files": evidence.dict()},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        
        return {
            "message": "Evidence uploaded successfully",
            "evidence_id": evidence_id,
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload evidence: {str(e)}")

@router.get("/requests/{request_id}/evidence/{evidence_id}")
async def download_evidence(
    request_id: str,
    evidence_id: str,
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Download evidence file"""
    try:
        # Validate request and permissions
        request = await service.get_removal_request(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Removal request not found")
        
        if current_user["role"] not in ["admin", "super_admin"] and request.requested_by != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Find evidence
        evidence_doc = await service.evidence_collection.find_one({"id": evidence_id})
        if not evidence_doc:
            raise HTTPException(status_code=404, detail="Evidence not found")
        
        evidence = RemovalEvidence(**evidence_doc)
        
        # Check if file exists
        if not os.path.exists(evidence.file_path):
            raise HTTPException(status_code=404, detail="Evidence file not found")
        
        return FileResponse(
            path=evidence.file_path,
            filename=evidence.file_name,
            media_type=evidence.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download evidence: {str(e)}")

@router.post("/requests/{request_id}/dispute")
async def create_dispute(
    request_id: str,
    dispute_reason: str = Form(..., description="Reason for dispute"),
    evidence_description: str = Form(..., description="Evidence description"),
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Create dispute against removal request"""
    try:
        # Validate request exists
        request = await service.get_removal_request(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Removal request not found")
        
        # Only allow disputes on completed removals
        if request.status not in [RemovalStatus.COMPLETED, RemovalStatus.IN_PROGRESS]:
            raise HTTPException(status_code=400, detail="Can only dispute completed or in-progress removals")
        
        # Create dispute
        dispute = DisputeRequest(
            removal_request_id=request_id,
            disputed_by=current_user["id"],
            dispute_reason=dispute_reason,
            evidence_description=evidence_description
        )
        
        # Store dispute
        await service.disputes_collection.insert_one(dispute.dict())
        
        # Update removal request status
        await service.collection.update_one(
            {"id": request_id},
            {
                "$set": {
                    "status": RemovalStatus.DISPUTED,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "message": "Dispute created successfully",
            "dispute_id": dispute.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dispute: {str(e)}")

@router.get("/analytics", response_model=RemovalAnalytics)
async def get_removal_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: dict = Depends(get_current_admin_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Get removal analytics (admin only)"""
    try:
        analytics = await service.generate_analytics(
            start_date=start_date,
            end_date=end_date
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

@router.get("/platforms")
async def get_supported_platforms(
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Get list of platforms that support takedown"""
    try:
        platforms = []
        for platform_id, config in service.distribution_platforms.items():
            if config.get("supports_takedown", False):
                platforms.append({
                    "id": platform_id,
                    "name": config["name"],
                    "type": config["type"],
                    "takedown_method": config.get("takedown_method", "manual")
                })
        
        return {
            "platforms": platforms,
            "total_count": len(platforms)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch platforms: {str(e)}")

@router.get("/ddex-messages/{request_id}")
async def get_ddex_messages(
    request_id: str,
    current_user: dict = Depends(get_current_admin_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Get DDEX messages for removal request (admin only)"""
    try:
        # Validate request exists
        request_doc = await service.collection.find_one({"id": request_id})
        if not request_doc:
            raise HTTPException(status_code=404, detail="Removal request not found")

        # Get DDEX messages
        cursor = service.ddex_messages_collection.find({"removal_request_id": request_id})
        messages = await cursor.to_list(length=None)
        
        # Convert ObjectId to string and clean up the data
        cleaned_messages = []
        for msg in messages:
            if '_id' in msg:
                del msg['_id']  # Remove MongoDB ObjectId
            cleaned_messages.append(msg)
        
        return {
            "messages": cleaned_messages,
            "total_count": len(cleaned_messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch DDEX messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch DDEX messages: {str(e)}")

@router.get("/ddex-messages/{request_id}/{message_id}/xml")
async def download_ddex_xml(
    request_id: str,
    message_id: str,
    current_user: dict = Depends(get_current_admin_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Download DDEX XML message (admin only)"""
    try:
        # Validate request exists
        request_doc = await service.collection.find_one({"id": request_id})
        if not request_doc:
            raise HTTPException(status_code=404, detail="Removal request not found")

        # Get DDEX message
        message_doc = await service.ddex_messages_collection.find_one({
            "id": message_id,
            "removal_request_id": request_id
        })
        
        if not message_doc:
            raise HTTPException(status_code=404, detail="DDEX message not found")
        
        # Get XML content
        xml_content = message_doc.get("xml_content", "")
        if not xml_content:
            raise HTTPException(status_code=404, detail="XML content not found")
        
        # Create filename
        filename = f"ddex_takedown_{message_id}.xml"
        
        # Return XML content as downloadable file
        return StreamingResponse(
            io.StringIO(xml_content),
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download DDEX XML: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download DDEX XML: {str(e)}")

@router.get("/reports/compliance")
async def generate_compliance_report(
    report_type: str = Query("monthly", description="Report type (monthly, quarterly, annual)"),
    period_start: Optional[datetime] = Query(None, description="Report period start"),
    period_end: Optional[datetime] = Query(None, description="Report period end"),
    format: str = Query("json", description="Report format (json, csv, pdf)"),
    current_user: dict = Depends(get_current_admin_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Generate compliance report (admin only)"""
    try:
        # Default period based on report type
        if not period_end:
            period_end = datetime.now(timezone.utc)
        
        if not period_start:
            if report_type == "monthly":
                period_start = period_end - timedelta(days=30)
            elif report_type == "quarterly":
                period_start = period_end - timedelta(days=90)
            elif report_type == "annual":
                period_start = period_end - timedelta(days=365)
            else:
                period_start = period_end - timedelta(days=30)
        
        # Generate analytics for the period
        analytics = await service.generate_analytics(period_start, period_end)
        
        # Create compliance report
        report = ComplianceReport(
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            total_removals=analytics.total_requests,
            legal_removals=analytics.requests_by_reason.get("legal_order", 0),
            voluntary_removals=analytics.requests_by_reason.get("artist_request", 0),
            disputed_removals=analytics.disputed_requests,
            platform_statistics=analytics.requests_by_platform,
            generated_by=current_user["id"]
        )
        
        if format == "json":
            return report
        elif format == "csv":
            # Generate CSV report
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers and data
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Report Type", report.report_type])
            writer.writerow(["Period Start", report.period_start.isoformat()])
            writer.writerow(["Period End", report.period_end.isoformat()])
            writer.writerow(["Total Removals", report.total_removals])
            writer.writerow(["Legal Removals", report.legal_removals])
            writer.writerow(["Voluntary Removals", report.voluntary_removals])
            writer.writerow(["Disputed Removals", report.disputed_removals])
            
            # Platform breakdown
            writer.writerow([])
            writer.writerow(["Platform Statistics"])
            writer.writerow(["Platform", "Removal Count"])
            for platform, count in report.platform_statistics.items():
                writer.writerow([platform, count])
            
            csv_content = output.getvalue()
            output.close()
            
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=compliance_report_{report_type}.csv"}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if service is initialized
        if removal_service is None:
            return {"status": "unhealthy", "message": "Service not initialized"}
        
        # Basic database connectivity check
        await removal_service.collection.find_one()
        
        return {
            "status": "healthy",
            "service": "content_removal",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# DAO Governance Integration Endpoints

@router.post("/dao/propose-removal")
async def propose_dao_removal(
    content_id: str = Form(...),
    reason: str = Form(...),
    description: str = Form(...),
    voting_duration_hours: int = Form(72, description="Voting duration in hours"),
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Create DAO proposal for content removal"""
    try:
        # Validate user can create DAO proposals
        user_role = current_user.get('role', '').lower()
        user_id = current_user.get('id', current_user.get('email', 'unknown'))
        
        # Allow creators, admins, and legal users to create DAO proposals
        allowed_roles = ['creator', 'admin', 'super_admin', 'legal', 'dao_member']
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Role '{user_role}' cannot create DAO proposals. Allowed roles: {allowed_roles}"
            )
        
        # Validate voting duration
        if voting_duration_hours < 24:
            voting_duration_hours = 24
        elif voting_duration_hours > 168:  # 7 days max
            voting_duration_hours = 168
        
        # This would integrate with the blockchain DAO system
        # For now, create a mock proposal
        proposal_id = str(uuid.uuid4())
        
        # Create removal request with DAO reason
        request_data = RemovalRequestCreate(
            content_id=content_id,
            reason=RemovalReason.DAO_VOTE,
            description=f"DAO Proposal: {description}",
            urgency=RemovalUrgency.MEDIUM
        )
        
        # Set requester role appropriately
        requester_role = "dao_member" if user_role == "creator" else user_role
        
        removal_request = await service.create_removal_request(
            request_data=request_data,
            requester_id=user_id,
            requester_role=requester_role
        )
        
        # Store DAO proposal metadata
        dao_proposal = {
            "id": proposal_id,
            "removal_request_id": removal_request.id,
            "content_id": content_id,
            "proposed_by": user_id,
            "proposer_role": user_role,
            "reason": reason,
            "description": description,
            "voting_duration_hours": voting_duration_hours,
            "proposal_status": "active",
            "votes_for": 0,
            "votes_against": 0,
            "total_votes": 0,
            "created_at": datetime.now(timezone.utc),
            "voting_deadline": datetime.now(timezone.utc) + timedelta(hours=voting_duration_hours)
        }
        
        await service.db.dao_removal_proposals.insert_one(dao_proposal)
        
        logger.info(f"DAO removal proposal created by {user_role} user {user_id}")
        
        return {
            "message": "DAO removal proposal created successfully",
            "proposal_id": proposal_id,
            "removal_request_id": removal_request.id,
            "voting_deadline": dao_proposal["voting_deadline"],
            "proposer_role": user_role,
            "voting_duration_hours": voting_duration_hours
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create DAO proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create DAO proposal: {str(e)}")

@router.get("/dao/proposals")
async def get_dao_proposals(
    status: Optional[str] = Query(None, description="Filter by proposal status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Get DAO removal proposals"""
    try:
        query = {}
        if status:
            query["proposal_status"] = status
        
        cursor = service.db.dao_removal_proposals.find(query).sort("created_at", -1).skip(offset).limit(limit)
        proposals = await cursor.to_list(length=limit)
        
        return {
            "proposals": proposals,
            "total_count": len(proposals)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch DAO proposals: {str(e)}")

@router.post("/dao/proposals/{proposal_id}/vote")
async def vote_on_dao_proposal(
    proposal_id: str,
    vote: str = Form(..., description="Vote: 'for' or 'against'"),
    current_user: dict = Depends(get_current_user),
    service: ContentRemovalService = Depends(get_removal_service)
):
    """Vote on DAO removal proposal"""
    try:
        if vote not in ["for", "against"]:
            raise HTTPException(status_code=400, detail="Vote must be 'for' or 'against'")
        
        user_id = current_user.get('id', current_user.get('email', 'unknown'))
        user_role = current_user.get('role', '').lower()
        
        # Get proposal
        proposal = await service.db.dao_removal_proposals.find_one({"id": proposal_id})
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Check if voting is still open
        voting_deadline = proposal.get("voting_deadline")
        if isinstance(voting_deadline, str):
            voting_deadline = datetime.fromisoformat(voting_deadline.replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) > voting_deadline:
            raise HTTPException(status_code=400, detail="Voting period has ended")
        
        # Check if user already voted
        existing_vote = await service.db.dao_votes.find_one({
            "proposal_id": proposal_id,
            "voter_id": user_id
        })
        
        if existing_vote:
            raise HTTPException(status_code=400, detail="You have already voted on this proposal")
        
        # Determine vote weight based on user role
        vote_weight = 1
        if user_role in ['admin', 'super_admin', 'legal']:
            vote_weight = 3  # Admin votes carry more weight
        elif user_role == 'creator':
            vote_weight = 2  # Creator votes carry moderate weight
        
        # Record vote
        vote_record = {
            "id": str(uuid.uuid4()),
            "proposal_id": proposal_id,
            "voter_id": user_id,
            "voter_role": user_role,
            "vote": vote,
            "vote_weight": vote_weight,
            "timestamp": datetime.now(timezone.utc)
        }
        
        await service.db.dao_votes.insert_one(vote_record)
        
        # Update proposal vote counts
        update_field = "votes_for" if vote == "for" else "votes_against"
        await service.db.dao_removal_proposals.update_one(
            {"id": proposal_id},
            {
                "$inc": {update_field: vote_weight, "total_votes": vote_weight}
            }
        )
        
        logger.info(f"DAO vote recorded: {user_role} user {user_id} voted '{vote}' with weight {vote_weight}")
        
        return {
            "message": "Vote recorded successfully",
            "vote": vote,
            "vote_weight": vote_weight,
            "voter_role": user_role,
            "proposal_id": proposal_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record vote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to record vote: {str(e)}")