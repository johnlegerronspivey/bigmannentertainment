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

# Initialize services
content_ingestion = ContentIngestionService()
ddex_service = DDEXMetadataService()
compliance_service = ComplianceValidationService()

# Create router
router = APIRouter(prefix="/api/content-ingestion", tags=["Content Ingestion"])
security = HTTPBearer()

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This would integrate with your authentication system
    # For now, returning a mock user ID
    return "user_123"

# File Upload Endpoints

@router.post("/upload")
async def upload_content_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
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
            user_id=user_id
        )
        
        # Extract technical metadata
        technical_metadata = await content_ingestion.extract_technical_metadata(content_file)
        content_file.technical_metadata.update(technical_metadata)
        
        return {
            "success": True,
            "content_file": content_file,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user)
):
    """Upload multiple content files"""
    try:
        uploaded_files = []
        
        for file in files:
            # Read file data
            file_data = await file.read()
            
            # Validate file size
            if len(file_data) > 100 * 1024 * 1024:
                continue  # Skip large files
            
            # Upload file
            content_file = await content_ingestion.upload_content_file(
                file_data=file_data,
                filename=file.filename,
                content_type=file.content_type,
                user_id=user_id
            )
            
            uploaded_files.append(content_file)
        
        return {
            "success": True,
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files),
            "message": f"Uploaded {len(uploaded_files)} files successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    user_id: str = Depends(get_current_user)
):
    """Create a content ingestion record with DDEX metadata"""
    try:
        # Parse JSON fields
        genre_list = json.loads(genre) if genre else []
        contributors_data = json.loads(contributors) if contributors else []
        file_ids_list = json.loads(file_ids) if file_ids else []
        licensing_data = json.loads(licensing_terms) if licensing_terms else None
        metadata_dict = json.loads(additional_metadata) if additional_metadata else {}
        
        # Parse release date
        release_date_obj = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
        
        # Create contributors
        contributor_objects = []
        for contrib_data in contributors_data:
            contributor = Contributor(
                name=contrib_data.get("name", ""),
                role=ContributorRole(contrib_data.get("role", "artist")),
                percentage=float(contrib_data.get("percentage", 0)),
                email=contrib_data.get("email"),
                phone=contrib_data.get("phone"),
                address=contrib_data.get("address"),
                tax_id=contrib_data.get("tax_id"),
                payment_info=contrib_data.get("payment_info"),
                metadata=contrib_data.get("metadata", {})
            )
            contributor_objects.append(contributor)
        
        # Create licensing terms if provided
        licensing_terms_obj = None
        if licensing_data:
            licensing_terms_obj = LicensingTerms(
                license_type=LicenseType(licensing_data.get("license_type", "non_exclusive")),
                start_date=datetime.fromisoformat(licensing_data.get("start_date", release_date).replace('Z', '+00:00')),
                end_date=datetime.fromisoformat(licensing_data["end_date"].replace('Z', '+00:00')) if licensing_data.get("end_date") else None,
                territories=licensing_data.get("territories", ["worldwide"]),
                geo_restrictions=GeoRestriction(licensing_data.get("geo_restrictions", "worldwide")),
                excluded_territories=licensing_data.get("excluded_territories", []),
                usage_rights=licensing_data.get("usage_rights", []),
                sync_rights=licensing_data.get("sync_rights", False),
                remix_rights=licensing_data.get("remix_rights", False),
                sampling_rights=licensing_data.get("sampling_rights", False),
                master_use_rights=licensing_data.get("master_use_rights", False),
                performance_rights=licensing_data.get("performance_rights", True),
                mechanical_rights=licensing_data.get("mechanical_rights", True),
                digital_rights=licensing_data.get("digital_rights", True),
                streaming_rights=licensing_data.get("streaming_rights", True),
                broadcast_rights=licensing_data.get("broadcast_rights", False),
                metadata=licensing_data.get("metadata", {})
            )
        
        # Generate ISRC and ISWC if not provided
        isrc = metadata_dict.get("isrc") or await content_ingestion.generate_isrc()
        iswc = metadata_dict.get("iswc") or await content_ingestion.generate_iswc()
        
        # Create DDEX metadata
        ddex_metadata = DDEXMetadata(
            title=title,
            subtitle=metadata_dict.get("subtitle"),
            display_title=metadata_dict.get("display_title"),
            original_title=metadata_dict.get("original_title"),
            release_type=metadata_dict.get("release_type", "Single"),
            genre=genre_list,
            subgenre=metadata_dict.get("subgenre", []),
            language=metadata_dict.get("language", "en"),
            original_language=metadata_dict.get("original_language"),
            main_artist=main_artist,
            featured_artists=metadata_dict.get("featured_artists", []),
            all_artists=metadata_dict.get("all_artists", [main_artist]),
            contributors=contributor_objects,
            release_date=release_date_obj,
            original_release_date=datetime.fromisoformat(metadata_dict["original_release_date"].replace('Z', '+00:00')) if metadata_dict.get("original_release_date") else None,
            p_line=metadata_dict.get("p_line"),
            c_line=metadata_dict.get("c_line"),
            label_name=metadata_dict.get("label_name", "Big Mann Entertainment"),
            label_code=metadata_dict.get("label_code"),
            distributor=metadata_dict.get("distributor", "Big Mann Entertainment"),
            price_category=metadata_dict.get("price_category"),
            commercial_model=metadata_dict.get("commercial_model", "SubscriptionModel"),
            duration=metadata_dict.get("duration"),
            explicit_content=metadata_dict.get("explicit_content", False),
            parental_warning=metadata_dict.get("parental_warning", False),
            licensing_terms=licensing_terms_obj,
            publishing_rights_owner=metadata_dict.get("publishing_rights_owner"),
            master_rights_owner=metadata_dict.get("master_rights_owner", "Big Mann Entertainment"),
            keywords=metadata_dict.get("keywords", []),
            description=metadata_dict.get("description"),
            producer_notes=metadata_dict.get("producer_notes"),
            liner_notes=metadata_dict.get("liner_notes"),
            message_recipient=metadata_dict.get("message_recipient", []),
            isrc=isrc,
            iswc=iswc,
            grid=metadata_dict.get("grid"),
            icpn=metadata_dict.get("icpn"),
            upc=metadata_dict.get("upc"),
            ean=metadata_dict.get("ean")
        )
        
        # Get content files (mock for now - would retrieve from storage)
        content_files = []
        for file_id in file_ids_list:
            # This would retrieve actual ContentFile objects
            # For now, creating mock objects
            content_file = ContentFile(
                file_id=file_id,
                original_filename=f"file_{file_id}.mp3",
                content_type="audio",
                mime_type="audio/mpeg",
                file_size=5000000,
                file_hash="mock_hash",
                s3_key=f"content/{user_id}/{file_id}",
                s3_bucket="bigmann-content",
                s3_url=f"https://bigmann-content.s3.amazonaws.com/content/{user_id}/{file_id}"
            )
            content_files.append(content_file)
        
        # Create ingestion record
        ingestion_record = await content_ingestion.create_content_ingestion_record(
            user_id=user_id,
            content_files=content_files,
            ddex_metadata=ddex_metadata
        )
        
        return {
            "success": True,
            "content_record": ingestion_record,
            "message": "Content ingestion record created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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