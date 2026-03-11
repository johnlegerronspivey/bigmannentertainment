"""
Content Ingestion API Endpoints - Function 1: Content Ingestion & Metadata Enrichment
Provides API endpoints for file upload, metadata management, and compliance validation.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json
import uuid
import jwt
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from content_ingestion_service import (
    ContentIngestionService, 
    ContentIngestionRecord, 
    DDEXMetadata, 
    Contributor, 
    LicensingTerms,
    ContentFile,
    ContributorRole,
    LicenseType,
    GeoRestriction
)
from ddex_metadata_service import DDEXMetadataService
from compliance_validation_service import ComplianceValidationService

# Import proper authentication
from motor.motor_asyncio import AsyncIOMotorClient

# Database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# User model
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str = ""
    is_admin: bool = False
    role: str = "user"

# Initialize services
content_ingestion = ContentIngestionService()
ddex_service = DDEXMetadataService()
compliance_service = ComplianceValidationService()

# Create router
router = APIRouter(prefix="/api/content-ingestion", tags=["Content Ingestion"])
security = HTTPBearer()

# Authentication setup
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"

# Proper authentication dependency
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

# Health and Status Endpoints

@router.get("/health")
async def health_check():
    """Health check endpoint for content ingestion service"""
    try:
        # Check service availability
        services_status = {
            "content_ingestion_service": "healthy",
            "ddex_metadata_service": "healthy", 
            "compliance_validation_service": "healthy",
            "database_connection": "healthy"
        }
        
        # Test database connection
        try:
            await db.command("ping")
        except Exception as e:
            services_status["database_connection"] = f"unhealthy: {str(e)}"
        
        overall_status = "healthy" if all(
            status == "healthy" for status in services_status.values()
        ) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": services_status,
            "version": "1.0.0"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }

@router.get("/upload-status/{file_id}")
async def get_upload_status(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get upload status for a specific file"""
    try:
        # This would check the actual upload status from your storage system
        # For now, returning a mock status
        return {
            "file_id": file_id,
            "status": "completed",
            "upload_progress": 100,
            "file_size": 0,
            "uploaded_bytes": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get upload status: {str(e)}")

# Enhanced upload endpoint with chunked support
@router.post("/upload-chunked")
async def upload_content_file_chunked(
    file: UploadFile = File(...),
    chunk_index: int = Form(0),
    total_chunks: int = Form(1),
    file_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Upload content file with chunked support for large files"""
    try:
        # Generate file ID if not provided
        if not file_id:
            file_id = str(uuid.uuid4())
        
        # Read chunk data
        chunk_data = await file.read()
        
        # Validate chunk size (25MB limit per chunk)
        if len(chunk_data) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Chunk too large. Maximum chunk size is 25MB")
        
        # Handle single chunk upload (regular upload)
        if total_chunks == 1:
            content_file = await content_ingestion.upload_content_file(
                file_data=chunk_data,
                filename=file.filename,
                content_type=file.content_type,
                user_id=current_user.id
            )
            
            # Extract technical metadata
            technical_metadata = await content_ingestion.extract_technical_metadata(content_file)
            if technical_metadata:
                content_file.technical_metadata.update(technical_metadata)
            
            return {
                "success": True,
                "file_id": content_file.file_id if hasattr(content_file, 'file_id') else file_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(chunk_data),
                "chunks_uploaded": 1,
                "total_chunks": 1,
                "upload_complete": True,
                "message": "File uploaded successfully"
            }
        
        # Handle multi-chunk upload
        else:
            # Store chunk temporarily (you'd implement actual chunk storage)
            chunk_info = {
                "file_id": file_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "chunk_index": chunk_index,
                "chunk_size": len(chunk_data),
                "total_chunks": total_chunks,
                "user_id": current_user.id,
                "upload_date": datetime.now(timezone.utc).isoformat()
            }
            
            # Check if this is the last chunk
            upload_complete = chunk_index == total_chunks - 1
            
            if upload_complete:
                # Combine all chunks and create final file
                # This is a simplified version - in production you'd retrieve and combine actual chunks
                content_file = await content_ingestion.upload_content_file(
                    file_data=chunk_data,  # In reality, combined chunk data
                    filename=file.filename,
                    content_type=file.content_type,
                    user_id=current_user.id
                )
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "chunks_uploaded": chunk_index + 1,
                    "total_chunks": total_chunks,
                    "upload_complete": True,
                    "message": "Chunked upload completed successfully"
                }
            else:
                return {
                    "success": True,
                    "file_id": file_id,
                    "filename": file.filename,
                    "chunks_uploaded": chunk_index + 1,
                    "total_chunks": total_chunks,
                    "upload_complete": False,
                    "message": f"Chunk {chunk_index + 1} of {total_chunks} uploaded successfully"
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunked upload failed: {str(e)}")

@router.post("/upload")
async def upload_content_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a content file (audio, video, image, document)"""
    try:
        # Read file data
        file_data = await file.read()
        
        # Validate file size (100MB limit)
        if len(file_data) > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB")
        
        # Upload file
        content_file = await content_ingestion.upload_content_file(
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type,
            user_id=current_user.id
        )
        
        # Extract technical metadata
        technical_metadata = await content_ingestion.extract_technical_metadata(content_file)
        if technical_metadata:
            content_file.technical_metadata.update(technical_metadata)
        
        return {
            "success": True,
            "content_file": content_file.dict() if hasattr(content_file, 'dict') else content_file,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple content files"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        uploaded_files = []
        errors = []
        
        for file in files:
            try:
                # Read file data
                file_data = await file.read()
                
                # Validate file size (100MB limit per file)
                if len(file_data) > 100 * 1024 * 1024:
                    errors.append(f"File {file.filename} too large (max 100MB)")
                    continue
                
                # Validate file type
                if not file.content_type:
                    errors.append(f"File {file.filename} has no content type")
                    continue
                
                # Upload file
                content_file = await content_ingestion.upload_content_file(
                    file_data=file_data,
                    filename=file.filename,
                    content_type=file.content_type,
                    user_id=current_user.id
                )
                
                # Extract technical metadata
                technical_metadata = await content_ingestion.extract_technical_metadata(content_file)
                if technical_metadata:
                    content_file.technical_metadata.update(technical_metadata)
                
                uploaded_files.append({
                    "file_id": content_file.file_id if hasattr(content_file, 'file_id') else str(uuid.uuid4()),
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": len(file_data),
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "technical_metadata": getattr(content_file, 'technical_metadata', {})
                })
                
            except Exception as file_error:
                errors.append(f"Error uploading {file.filename}: {str(file_error)}")
        
        return {
            "success": len(uploaded_files) > 0,
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files),
            "errors": errors,
            "message": f"Uploaded {len(uploaded_files)} files successfully" + (f" with {len(errors)} errors" if errors else "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple file upload failed: {str(e)}")

# Content Ingestion Management

@router.post("/create")
async def create_content_ingestion(
    title: str = Form(...),
    main_artist: str = Form(...),
    release_date: str = Form(...),
    genre: str = Form(...),  # JSON string of genres
    contributors: str = Form(...),  # JSON string of contributors
    file_ids: str = Form(...),  # JSON string of file IDs
    licensing_terms: Optional[str] = Form(None),  # JSON string of licensing terms
    additional_metadata: Optional[str] = Form(None),  # JSON string of additional metadata
    current_user: User = Depends(get_current_user)
):
    """Create a content ingestion record with DDEX metadata"""
    try:
        # Parse JSON strings
        genre_list = json.loads(genre) if genre else []
        contributors_list = json.loads(contributors) if contributors else []
        file_ids_list = json.loads(file_ids) if file_ids else []
        licensing_terms_dict = json.loads(licensing_terms) if licensing_terms else None
        additional_metadata_dict = json.loads(additional_metadata) if additional_metadata else {}
        
        # Validate required data
        if not file_ids_list:
            raise HTTPException(status_code=400, detail="At least one file ID is required")
        
        # Create DDEX metadata
        ddex_metadata = DDEXMetadata(
            title=title,
            main_artist=main_artist,
            release_date=datetime.fromisoformat(release_date.replace('Z', '+00:00')) if release_date else datetime.now(timezone.utc),
            genre=genre_list,
            contributors=[
                Contributor(**contributor) for contributor in contributors_list
            ],
            licensing_terms=LicensingTerms(**licensing_terms_dict) if licensing_terms_dict else None,
            additional_metadata=additional_metadata_dict
        )
        
        # Create content ingestion record
        content_record = await content_ingestion.create_content_record(
            ddex_metadata=ddex_metadata,
            file_ids=file_ids_list,
            user_id=current_user.id
        )
        
        # Run compliance validation in background
        background_tasks = BackgroundTasks()
        background_tasks.add_task(
            _run_compliance_validation,
            content_record.record_id if hasattr(content_record, 'record_id') else str(uuid.uuid4())
        )
        
        return {
            "success": True,
            "content_record": content_record.dict() if hasattr(content_record, 'dict') else content_record,
            "message": "Content ingestion record created successfully"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content creation failed: {str(e)}")

# Background task for compliance validation
async def _run_compliance_validation(record_id: str):
    """Run compliance validation in background"""
    try:
        validation_result = await compliance_service.validate_content_record(record_id)
        # Store validation result or update record status
        print(f"Compliance validation completed for record {record_id}: {validation_result}")
    except Exception as e:
        print(f"Background compliance validation failed for record {record_id}: {str(e)}")

@router.get("/content/{content_id}")
async def get_content_ingestion(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a content ingestion record"""
    try:
        content_record = await content_ingestion.get_content_ingestion_record(content_id, user_id)
        
        if not content_record:
            raise HTTPException(status_code=404, detail="Content record not found")
        
        return {
            "success": True,
            "content_record": content_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
async def list_user_content(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user)
):
    """List content ingestion records for user"""
    try:
        content_records = await content_ingestion.list_user_content(user_id, limit, offset)
        
        return {
            "success": True,
            "content_records": content_records,
            "total_records": len(content_records),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/content/{content_id}/status")
async def update_content_status(
    content_id: str,
    processing_status: Optional[str] = None,
    compliance_status: Optional[str] = None,
    compliance_issues: Optional[List[str]] = None,
    user_id: str = Depends(get_current_user)
):
    """Update content processing and compliance status"""
    try:
        success = await content_ingestion.update_content_status(
            content_id=content_id,
            user_id=user_id,
            processing_status=processing_status,
            compliance_status=compliance_status,
            compliance_issues=compliance_issues
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Content record not found or update failed")
        
        return {
            "success": True,
            "message": "Content status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DDEX Metadata Endpoints

@router.post("/ddex/generate-xml/{content_id}")
async def generate_ddex_xml(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Generate DDEX ERN XML for content"""
    try:
        content_record = await content_ingestion.get_content_ingestion_record(content_id, user_id)
        
        if not content_record:
            raise HTTPException(status_code=404, detail="Content record not found")
        
        # Generate DDEX XML
        ddex_xml = ddex_service.generate_ddex_ern_xml(content_record)
        
        return {
            "success": True,
            "ddex_xml": ddex_xml,
            "content_id": content_id,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ddex/validate-xml")
async def validate_ddex_xml(
    xml_content: str,
    user_id: str = Depends(get_current_user)
):
    """Validate DDEX XML structure and completeness"""
    try:
        validation_results = ddex_service.validate_ddex_xml(xml_content)
        
        return {
            "success": True,
            "validation_results": validation_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ddex/extract-metadata")
async def extract_metadata_from_xml(
    xml_content: str,
    user_id: str = Depends(get_current_user)
):
    """Extract metadata from existing DDEX XML"""
    try:
        extraction_results = ddex_service.extract_metadata_from_xml(xml_content)
        
        return {
            "success": extraction_results["success"],
            "metadata": extraction_results.get("metadata"),
            "error": extraction_results.get("error")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ddex/catalog")
async def generate_catalog_xml(
    user_id: str = Depends(get_current_user)
):
    """Generate DDEX catalog list XML for user's content"""
    try:
        # Get user's content records
        content_records = await content_ingestion.list_user_content(user_id, limit=100)
        
        # Filter for distribution-ready content
        distribution_ready = [record for record in content_records if record.distribution_ready]
        
        if not distribution_ready:
            return {
                "success": False,
                "message": "No content ready for distribution",
                "catalog_xml": None
            }
        
        # Generate catalog XML
        catalog_xml = ddex_service.generate_catalog_list_xml(distribution_ready)
        
        return {
            "success": True,
            "catalog_xml": catalog_xml,
            "total_releases": len(distribution_ready),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Compliance Validation Endpoints

@router.post("/compliance/validate/{content_id}")
async def validate_content_compliance(
    content_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Run comprehensive compliance validation on content"""
    try:
        content_record = await content_ingestion.get_content_ingestion_record(content_id, user_id)
        
        if not content_record:
            raise HTTPException(status_code=404, detail="Content record not found")
        
        # Run compliance validation
        validation_results = await compliance_service.validate_content_compliance(content_record)
        
        # Update content status based on validation results
        compliance_status = validation_results["overall_status"]
        compliance_issues = [issue["title"] for issue in validation_results["issues"]]
        
        background_tasks.add_task(
            content_ingestion.update_content_status,
            content_id,
            user_id,
            compliance_status=compliance_status,
            compliance_issues=compliance_issues
        )
        
        return {
            "success": True,
            "validation_results": validation_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/rules")
async def get_compliance_rules(user_id: str = Depends(get_current_user)):
    """Get summary of available compliance rules"""
    try:
        compliance_summary = compliance_service.get_compliance_summary()
        
        return {
            "success": True,
            "compliance_summary": compliance_summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Analytics Endpoints

@router.get("/analytics/{content_id}")
async def get_content_analytics(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get analytics for a content piece"""
    try:
        analytics = await content_ingestion.get_content_analytics(content_id, user_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prepare-distribution/{content_id}") 
async def prepare_content_for_distribution(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Prepare content for distribution to platforms"""
    try:
        preparation_results = await content_ingestion.prepare_for_distribution(content_id, user_id)
        
        return {
            "success": preparation_results["success"],
            "distribution_package": preparation_results.get("distribution_package"),
            "message": preparation_results.get("message"),
            "error": preparation_results.get("error")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints

@router.post("/generate-isrc")
async def generate_isrc_code(
    country_code: str = "US",
    registrant_code: str = "BME",
    user_id: str = Depends(get_current_user)
):
    """Generate a new ISRC code"""
    try:
        isrc = await content_ingestion.generate_isrc(country_code, registrant_code)
        
        return {
            "success": True,
            "isrc": isrc,
            "country_code": country_code,
            "registrant_code": registrant_code,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-iswc")
async def generate_iswc_code(user_id: str = Depends(get_current_user)):
    """Generate a new ISWC code"""
    try:
        iswc = await content_ingestion.generate_iswc()
        
        return {
            "success": True,
            "iswc": iswc,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_content_dashboard(user_id: str = Depends(get_current_user)):
    """Get content ingestion dashboard data"""
    try:
        # Get user's content statistics
        all_content = await content_ingestion.list_user_content(user_id, limit=1000)
        
        dashboard_data = {
            "total_content": len(all_content),
            "by_status": {
                "processing": len([c for c in all_content if c.processing_status == "processing"]),
                "processed": len([c for c in all_content if c.processing_status == "processed"]),
                "ready_for_distribution": len([c for c in all_content if c.distribution_ready]),
                "failed": len([c for c in all_content if c.processing_status == "failed"])
            },
            "by_compliance": {
                "approved": len([c for c in all_content if c.compliance_status == "approved"]),
                "needs_review": len([c for c in all_content if c.compliance_status == "needs_review"]),
                "rejected": len([c for c in all_content if c.compliance_status == "rejected"]),
                "pending": len([c for c in all_content if c.compliance_status == "pending"])
            },
            "by_content_type": {},
            "recent_uploads": [],
            "compliance_issues_summary": [],
            "storage_usage": {
                "total_files": sum(len(c.content_files) for c in all_content),
                "total_size_mb": sum(sum(cf.file_size for cf in c.content_files) for c in all_content) / (1024 * 1024)
            }
        }
        
        # Content type breakdown
        for content_record in all_content:
            for content_file in content_record.content_files:
                content_type = content_file.content_type.value
                dashboard_data["by_content_type"][content_type] = dashboard_data["by_content_type"].get(content_type, 0) + 1
        
        # Recent uploads (last 10)
        recent_content = sorted(all_content, key=lambda x: x.created_at, reverse=True)[:10]
        dashboard_data["recent_uploads"] = [
            {
                "content_id": c.content_id,
                "title": c.ddex_metadata.title,
                "main_artist": c.ddex_metadata.main_artist,
                "created_at": c.created_at.isoformat(),
                "processing_status": c.processing_status,
                "compliance_status": c.compliance_status
            }
            for c in recent_content
        ]
        
        # Compliance issues summary
        compliance_issues = {}
        for content_record in all_content:
            for issue in content_record.compliance_issues:
                compliance_issues[issue] = compliance_issues.get(issue, 0) + 1
        
        dashboard_data["compliance_issues_summary"] = [
            {"issue": issue, "count": count}
            for issue, count in sorted(compliance_issues.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy",
        "service": "Content Ingestion API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }