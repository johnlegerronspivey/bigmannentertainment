"""
Comprehensive Platform Licensing System API Endpoints
Complete licensing management system with business information integration,
automated workflows, comprehensive compliance documentation, ISAN prefix support
for audiovisual content identification, and ISRC prefix support for sound recording identification
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import jwt
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import logging

# Import our comprehensive licensing services
from business_information_service import BusinessInformationService, BusinessInformation
from comprehensive_licensing_engine import (
    ComprehensiveLicensingEngine, 
    ComprehensiveLicenseAgreement,
    AutomatedLicensingWorkflow,
    ComplianceDocumentation
)

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Database setup
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Authentication setup
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()

logger = logging.getLogger(__name__)

# User Model
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str = ""
    is_admin: bool = False
    role: str = "user"

# Request Models
class ComprehensiveLicensingRequest(BaseModel):
    platform_ids: List[str]
    license_type: str = "master_agreement"
    license_duration_months: int = 12
    auto_renewal: bool = True
    include_compliance_docs: bool = True
    generate_workflows: bool = True

class BusinessInformationUpdateRequest(BaseModel):
    business_entity: Optional[str] = None
    business_owner: Optional[str] = None
    contact_email: Optional[str] = None
    business_address: Optional[Dict[str, str]] = None
    regulatory_licenses: Optional[List[Dict[str, Any]]] = None
    platform_credentials: Optional[Dict[str, Dict[str, str]]] = None

class LicenseAgreementUpdateRequest(BaseModel):
    agreement_status: Optional[str] = None
    licensing_fees: Optional[Dict[str, float]] = None
    revenue_sharing: Optional[Dict[str, float]] = None
    compliance_requirements: Optional[List[str]] = None

class AutomatedWorkflowRequest(BaseModel):
    workflow_name: str
    platform_categories: List[str]
    trigger_conditions: Optional[List[str]] = None
    auto_execute_steps: Optional[List[str]] = None

# Authentication functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

async def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.role not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Initialize services
business_info_service = BusinessInformationService(db)
comprehensive_licensing_engine = ComprehensiveLicensingEngine(db)

# Create router
router = APIRouter(prefix="/comprehensive-licensing", tags=["Comprehensive Platform Licensing"])

# PHASE 1: Business Information Consolidation Endpoints

@router.get("/business-information")
async def get_consolidated_business_information(
    business_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get consolidated business information from all system sources"""
    try:
        business_info = await business_info_service.get_consolidated_business_information(business_id)
        
        return {
            "business_information": business_info.dict(),
            "data_sources": business_info.data_sources,
            "last_updated": business_info.last_updated,
            "verification_status": business_info.verification_status,
            "completeness_score": len([
                field for field in ["business_entity", "business_owner", "ein", "tin", 
                "contact_email", "business_address", "company_prefix", "legal_entity_gln"]
                if getattr(business_info, field, None)
            ]) / 8 * 100
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve business information: {str(e)}")

@router.put("/business-information")
async def update_business_information(
    update_request: BusinessInformationUpdateRequest,
    business_id: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """Update consolidated business information"""
    try:
        # Convert request to dict and filter None values
        updates = {k: v for k, v in update_request.dict().items() if v is not None}
        
        if not business_id:
            # Get existing business information to find ID
            existing_info = await business_info_service.get_consolidated_business_information()
            business_id = existing_info.business_id
        
        updated_info = await business_info_service.update_business_information(business_id, updates)
        
        return {
            "message": "Business information updated successfully",
            "business_information": updated_info.dict(),
            "updated_fields": list(updates.keys()),
            "updated_by": current_user.email,
            "update_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update business information: {str(e)}")

@router.post("/business-information/validate")
async def validate_business_information(
    business_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Validate completeness and accuracy of business information"""
    try:
        if not business_id:
            existing_info = await business_info_service.get_consolidated_business_information()
            business_id = existing_info.business_id
        
        validation_results = await business_info_service.validate_business_information(business_id)
        
        return {
            "validation_results": validation_results,
            "business_id": business_id,
            "validation_date": validation_results["validation_date"],
            "recommendations": validation_results["recommendations"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate business information: {str(e)}")

@router.post("/business-information/sync")
async def sync_business_information(
    business_id: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """Synchronize business information across all system modules"""
    try:
        if not business_id:
            existing_info = await business_info_service.get_consolidated_business_information()
            business_id = existing_info.business_id
        
        sync_results = await business_info_service.sync_business_information_across_modules(business_id)
        
        return {
            "message": "Business information synchronization completed",
            "sync_results": sync_results,
            "synchronized_by": current_user.email,
            "sync_date": sync_results["sync_date"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync business information: {str(e)}")

# PHASE 2: Platform Licensing Engine Endpoints

@router.post("/license-agreements")
async def create_comprehensive_license_agreement(
    licensing_request: ComprehensiveLicensingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """Create comprehensive license agreement with integrated business information"""
    try:
        # Create comprehensive license agreement
        agreement = await comprehensive_licensing_engine.create_comprehensive_license_agreement(
            platform_ids=licensing_request.platform_ids,
            license_type=licensing_request.license_type
        )
        
        # Generate automated workflows if requested
        if licensing_request.generate_workflows:
            background_tasks.add_task(
                _generate_licensing_workflows,
                agreement.agreement_id,
                licensing_request.platform_ids
            )
        
        # Generate compliance documentation if requested
        if licensing_request.include_compliance_docs:
            background_tasks.add_task(
                _generate_compliance_documentation,
                licensing_request.platform_ids,
                agreement.agreement_id
            )
        
        return {
            "message": f"Comprehensive license agreement created for {len(licensing_request.platform_ids)} platforms",
            "agreement": agreement.dict(),
            "agreement_id": agreement.agreement_id,
            "platforms_licensed": licensing_request.platform_ids,
            "total_platforms": len(licensing_request.platform_ids),
            "estimated_annual_cost": sum(agreement.licensing_fees.values()) * 12,
            "created_by": current_user.email,
            "background_tasks": {
                "workflows_generation": licensing_request.generate_workflows,
                "compliance_docs_generation": licensing_request.include_compliance_docs
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comprehensive license agreement: {str(e)}")

@router.get("/license-agreements")
async def get_license_agreements(
    status: Optional[str] = None,
    platform_category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive license agreements with filtering"""
    try:
        query = {}
        if status:
            query["agreement_status"] = status
        if platform_category:
            query["platform_categories"] = platform_category
        
        agreements = await comprehensive_licensing_engine.comprehensive_agreements_collection.find(
            query
        ).skip(offset).limit(limit).to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for agreement in agreements:
            agreement["_id"] = str(agreement["_id"])
        
        return {
            "agreements": agreements,
            "total_count": len(agreements),
            "filters": {
                "status": status,
                "platform_category": platform_category,
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve license agreements: {str(e)}")

@router.get("/license-agreements/{agreement_id}")
async def get_license_agreement_details(
    agreement_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information for a specific license agreement"""
    try:
        agreement = await comprehensive_licensing_engine.comprehensive_agreements_collection.find_one(
            {"agreement_id": agreement_id}
        )
        
        if not agreement:
            raise HTTPException(status_code=404, detail="License agreement not found")
        
        # Get related compliance documents
        compliance_docs = await comprehensive_licensing_engine.compliance_documents_collection.find(
            {"agreement_id": agreement_id}
        ).to_list(length=None)
        
        # Convert ObjectId to string
        agreement["_id"] = str(agreement["_id"])
        for doc in compliance_docs:
            doc["_id"] = str(doc["_id"])
        
        return {
            "agreement": agreement,
            "compliance_documents": compliance_docs,
            "platform_breakdown": {
                "total_platforms": agreement.get("total_platforms", 0),
                "categories": agreement.get("platform_categories", []),
                "platforms_licensed": agreement.get("platforms_licensed", [])
            },
            "financial_summary": {
                "licensing_fees": agreement.get("licensing_fees", {}),
                "revenue_sharing": agreement.get("revenue_sharing", {}),
                "estimated_annual_cost": sum(agreement.get("licensing_fees", {}).values()) * 12
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve license agreement details: {str(e)}")

@router.put("/license-agreements/{agreement_id}")
async def update_license_agreement(
    agreement_id: str,
    update_request: LicenseAgreementUpdateRequest,
    current_user: User = Depends(require_admin)
):
    """Update a comprehensive license agreement"""
    try:
        # Convert request to dict and filter None values
        updates = {k: v for k, v in update_request.dict().items() if v is not None}
        updates["updated_at"] = datetime.utcnow()
        
        result = await comprehensive_licensing_engine.comprehensive_agreements_collection.update_one(
            {"agreement_id": agreement_id},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="License agreement not found or no changes made")
        
        # Get updated agreement
        updated_agreement = await comprehensive_licensing_engine.comprehensive_agreements_collection.find_one(
            {"agreement_id": agreement_id}
        )
        updated_agreement["_id"] = str(updated_agreement["_id"])
        
        return {
            "message": "License agreement updated successfully",
            "agreement": updated_agreement,
            "updated_fields": list(updates.keys()),
            "updated_by": current_user.email,
            "update_date": updates["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update license agreement: {str(e)}")

# PHASE 3: Automated Licensing Workflows Endpoints

@router.post("/workflows")
async def create_automated_licensing_workflow(
    workflow_request: AutomatedWorkflowRequest,
    current_user: User = Depends(require_admin)
):
    """Create automated licensing workflow"""
    try:
        workflow = await comprehensive_licensing_engine.generate_automated_licensing_workflow(
            workflow_name=workflow_request.workflow_name,
            platform_categories=workflow_request.platform_categories
        )
        
        return {
            "message": f"Automated licensing workflow '{workflow_request.workflow_name}' created successfully",
            "workflow": workflow.dict(),
            "workflow_id": workflow.workflow_id,
            "platform_categories": workflow_request.platform_categories,
            "total_automation_steps": len(workflow.automation_steps),
            "created_by": current_user.email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create automated workflow: {str(e)}")

@router.get("/workflows")
async def get_automated_workflows(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get automated licensing workflows"""
    try:
        query = {}
        if status:
            query["workflow_status"] = status
        
        workflows = await comprehensive_licensing_engine.licensing_workflows_collection.find(
            query
        ).to_list(length=None)
        
        # Convert ObjectId to string
        for workflow in workflows:
            workflow["_id"] = str(workflow["_id"])
        
        return {
            "workflows": workflows,
            "total_workflows": len(workflows),
            "active_workflows": len([w for w in workflows if w.get("workflow_status") == "active"]),
            "automation_capabilities": [
                "Business information validation",
                "Platform compatibility checking",
                "License terms calculation",
                "Compliance documentation generation",
                "Agreement creation and setup"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve automated workflows: {str(e)}")

@router.post("/workflows/{workflow_id}/execute")
async def execute_automated_workflow(
    workflow_id: str,
    platform_ids: List[str],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """Execute an automated licensing workflow"""
    try:
        workflow = await comprehensive_licensing_engine.licensing_workflows_collection.find_one(
            {"workflow_id": workflow_id}
        )
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Execute workflow steps in background
        background_tasks.add_task(
            _execute_workflow_steps,
            workflow,
            platform_ids,
            current_user.email
        )
        
        return {
            "message": f"Automated workflow execution started for {len(platform_ids)} platforms",
            "workflow_id": workflow_id,
            "workflow_name": workflow.get("workflow_name"),
            "platforms_to_process": platform_ids,
            "total_automation_steps": len(workflow.get("automation_steps", [])),
            "execution_started_by": current_user.email,
            "execution_started_at": datetime.utcnow().isoformat(),
            "estimated_completion_time": "15-30 minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute automated workflow: {str(e)}")

# PHASE 4: Comprehensive Licensing Dashboard Endpoints

@router.get("/dashboard")
async def get_comprehensive_licensing_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive licensing dashboard with all licensing information"""
    try:
        dashboard_data = await comprehensive_licensing_engine.get_comprehensive_licensing_dashboard()
        
        return {
            "comprehensive_licensing_dashboard": dashboard_data,
            "dashboard_type": "comprehensive_platform_licensing",
            "business_entity": dashboard_data["business_information_summary"]["business_entity"],
            "total_platforms_licensed": dashboard_data["licensing_overview"]["total_platforms_licensed"],
            "total_licensing_investment": dashboard_data["licensing_overview"]["total_licensing_fees"],
            "last_updated": datetime.utcnow().isoformat(),
            "dashboard_capabilities": [
                "Business information consolidation",
                "Comprehensive license agreements",
                "Automated licensing workflows",
                "Compliance documentation management",
                "Real-time platform monitoring"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve comprehensive licensing dashboard: {str(e)}")

@router.get("/compliance-documents")
async def get_compliance_documents(
    platform_id: Optional[str] = None,
    document_type: Optional[str] = None,
    legal_review_status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get compliance documents with optional filtering"""
    try:
        query = {}
        if platform_id:
            query["platform_id"] = platform_id
        if document_type:
            query["document_type"] = document_type
        if legal_review_status:
            query["legal_review_status"] = legal_review_status
        
        documents = await comprehensive_licensing_engine.compliance_documents_collection.find(
            query
        ).limit(limit).to_list(length=None)
        
        # Convert ObjectId to string
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return {
            "compliance_documents": documents,
            "total_documents": len(documents),
            "document_status_breakdown": {
                "pending_review": len([d for d in documents if d.get("legal_review_status") == "pending"]),
                "approved": len([d for d in documents if d.get("legal_review_status") == "approved"]),
                "rejected": len([d for d in documents if d.get("legal_review_status") == "rejected"])
            },
            "filters": {
                "platform_id": platform_id,
                "document_type": document_type,
                "legal_review_status": legal_review_status,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance documents: {str(e)}")

@router.post("/generate-all-platform-licenses")
async def generate_comprehensive_platform_licenses(
    background_tasks: BackgroundTasks,
    include_compliance_docs: bool = True,
    generate_workflows: bool = True,
    current_user: User = Depends(require_admin)
):
    """Generate comprehensive licenses for all 115+ platforms with business information"""
    try:
        # Import with error handling
        try:
            from config.platforms import DISTRIBUTION_PLATFORMS
        except ImportError as e:
            logger.error(f"Failed to import DISTRIBUTION_PLATFORMS: {e}")
            raise HTTPException(status_code=500, detail="Failed to load distribution platforms configuration")
        
        all_platform_ids = list(DISTRIBUTION_PLATFORMS.keys())
        logger.info(f"Generating comprehensive licenses for {len(all_platform_ids)} platforms")
        
        # Validate platform IDs
        if not all_platform_ids:
            raise HTTPException(status_code=400, detail="No distribution platforms found")
        
        # Create comprehensive license agreement with error handling
        try:
            agreement = await comprehensive_licensing_engine.create_comprehensive_license_agreement(
                platform_ids=all_platform_ids,
                license_type="master_comprehensive_agreement"
            )
        except Exception as e:
            logger.error(f"Failed to create comprehensive license agreement: {e}")
            raise HTTPException(status_code=500, detail=f"License agreement creation failed: {str(e)}")
        
        # Generate background tasks
        if generate_workflows:
            background_tasks.add_task(
                _generate_licensing_workflows,
                agreement.agreement_id,
                all_platform_ids
            )
        
        if include_compliance_docs:
            background_tasks.add_task(
                _generate_compliance_documentation,
                all_platform_ids,
                agreement.agreement_id
            )
        
        # Safely access agreement data
        try:
            business_entity_name = agreement.business_information.get("business_entity", {}).get("legal_name", "Big Mann Entertainment")
            annual_investment = sum(float(fee) for fee in agreement.licensing_fees.values()) * 12 if agreement.licensing_fees else 0
        except Exception as e:
            logger.warning(f"Error accessing agreement data: {e}")
            business_entity_name = "Big Mann Entertainment"
            annual_investment = 0
        
        return {
            "message": f"Comprehensive platform licensing initiated for all {len(all_platform_ids)} platforms",
            "master_agreement": agreement.dict(),
            "agreement_id": agreement.agreement_id,
            "business_entity": business_entity_name,
            "platforms_licensed": len(all_platform_ids),
            "platform_categories": agreement.platform_categories,
            "estimated_annual_investment": annual_investment,
            "compliance_documentation": include_compliance_docs,
            "automated_workflows": generate_workflows,
            "created_by": current_user.email,
            "creation_date": datetime.utcnow().isoformat(),
            "comprehensive_features": [
                "Business information integration",
                "Multi-platform category licensing",
                "Automated compliance documentation",
                "Legal framework integration",
                "Revenue sharing optimization",
                "Regulatory compliance coverage"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comprehensive error in generate_comprehensive_platform_licenses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate comprehensive platform licenses: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate comprehensive platform licenses: {str(e)}")

# Background Task Functions

async def _generate_licensing_workflows(agreement_id: str, platform_ids: List[str]):
    """Background task to generate licensing workflows"""
    try:
        # Determine platform categories
        platform_categories = []
        for platform_id in platform_ids:
            category = comprehensive_licensing_engine._get_platform_category(platform_id)
            if category not in platform_categories:
                platform_categories.append(category)
        
        # Generate workflow for each category
        for category in platform_categories:
            await comprehensive_licensing_engine.generate_automated_licensing_workflow(
                workflow_name=f"Automated {category.title()} Licensing Workflow",
                platform_categories=[category]
            )
        
        logger.info(f"Generated {len(platform_categories)} licensing workflows for agreement {agreement_id}")
        
    except Exception as e:
        logger.error(f"Error generating licensing workflows: {e}")

async def _generate_compliance_documentation(platform_ids: List[str], agreement_id: str):
    """Background task to generate compliance documentation"""
    try:
        compliance_docs = await comprehensive_licensing_engine.generate_compliance_documentation(
            platform_ids=platform_ids,
            agreement_id=agreement_id
        )
        
        logger.info(f"Generated {len(compliance_docs)} compliance documents for agreement {agreement_id}")
        
    except Exception as e:
        logger.error(f"Error generating compliance documentation: {e}")

async def _execute_workflow_steps(workflow: Dict, platform_ids: List[str], executed_by: str):
    """Background task to execute workflow steps"""
    try:
        workflow_steps = workflow.get("automation_steps", [])
        
        for step in workflow_steps:
            if step.get("auto_execute", False):
                # Execute the automation step
                logger.info(f"Executing workflow step: {step.get('step')} for {len(platform_ids)} platforms")
                # Implementation would depend on the specific step
                
        logger.info(f"Completed workflow execution for {len(platform_ids)} platforms")
        
    except Exception as e:
        logger.error(f"Error executing workflow steps: {e}")

# Export the router
comprehensive_licensing_router = router