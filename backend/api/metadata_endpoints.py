"""
Metadata Parser & Validator API Endpoints
Handles API endpoints for metadata parsing, validation, and duplicate detection
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import json

from auth.service import get_current_user, get_current_admin_user as require_admin
from metadata_models import (
    MetadataFormat, MetadataValidationResult, MetadataValidationConfig,
    ParsedMetadata, DuplicateRecord, ValidationStatus
)
from metadata_parser_service import MetadataParserService
from metadata_validator_service import MetadataValidatorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metadata", tags=["Metadata Parser & Validator"])

# Global services (will be initialized in server.py)
parser_service = None
validator_service = None
mongo_db = None

def init_metadata_services(db, services_dict):
    """Initialize metadata services with database and other services"""
    global parser_service, validator_service, mongo_db
    mongo_db = db
    parser_service = MetadataParserService()
    validator_service = MetadataValidatorService(mongo_db=db)
    
    # Store services for access from other modules
    services_dict['metadata_parser'] = parser_service
    services_dict['metadata_validator'] = validator_service

@router.post("/parse", response_model=Dict[str, Any])
async def parse_metadata_file(
    file: UploadFile = File(...),
    format: MetadataFormat = Form(...),
    validate_metadata: bool = Form(True),
    check_duplicates: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """
    Parse and optionally validate metadata file
    Supports DDEX ERN (XML), MEAD, JSON, and CSV formats
    """
    try:
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 50MB."
            )
        
        # Parse metadata
        parsed_metadata, parsing_errors = parser_service.parse_metadata(
            content=file_content,
            file_format=format,
            file_name=file.filename
        )
        
        # Initialize validation result
        validation_result = MetadataValidationResult(
            user_id=current_user.id,
            file_name=file.filename,
            file_size=file_size,
            file_format=format,
            parsing_status=ValidationStatus.VALID if not parsing_errors else ValidationStatus.WARNING,
            parsing_errors=parsing_errors,
            parsed_metadata=parsed_metadata,
            validation_status=ValidationStatus.PENDING  # Will be updated if validation is performed
        )
        
        # Perform validation if requested
        if validate_metadata:
            validation_config = MetadataValidationConfig(
                check_duplicates=check_duplicates,
                duplicate_scope="platform"
            )
            
            validation_result = await validator_service.validate_metadata(
                parsed_metadata=parsed_metadata,
                file_format=format,
                config=validation_config
            )
            
            # Set user and file info
            validation_result.user_id = current_user.id
            validation_result.file_name = file.filename
            validation_result.file_size = file_size
            validation_result.parsing_errors = parsing_errors
        
        # Store validation result in database
        try:
            result_dict = validation_result.dict()
            result_dict["_id"] = validation_result.id
            result_dict["created_at"] = datetime.now()
            
            await mongo_db["metadata_validation_results"].insert_one(result_dict)
            logger.info(f"Stored validation result {validation_result.id} for user {current_user.id}")
            
        except Exception as e:
            logger.error(f"Failed to store validation result: {str(e)}")
            # Continue without storing - don't fail the request
        
        return {
            "success": True,
            "message": "Metadata parsed and validated successfully",
            "validation_id": validation_result.id,
            "parsing_status": validation_result.parsing_status,
            "validation_status": validation_result.validation_status,
            "parsed_metadata": validation_result.parsed_metadata.dict(),
            "validation_errors": [error.dict() for error in validation_result.validation_errors],
            "validation_warnings": [warning.dict() for warning in validation_result.validation_warnings],
            "duplicates_found": validation_result.duplicate_count,
            "duplicate_details": [dup.dict() for dup in validation_result.duplicates_found],
            "processing_time": validation_result.processing_time,
            "total_records": 1,
            "statistics": {
                "valid_records": 1 if validation_result.validation_status == ValidationStatus.VALID else 0,
                "warning_records": 1 if validation_result.validation_status == ValidationStatus.WARNING else 0,
                "error_records": 1 if validation_result.validation_status == ValidationStatus.ERROR else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing metadata file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse metadata file: {str(e)}"
        )

@router.post("/validate-json", response_model=Dict[str, Any])
async def validate_json_metadata(
    metadata_json: Dict[str, Any],
    check_duplicates: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate JSON metadata object directly (without file upload)
    """
    try:
        # Convert JSON to ParsedMetadata object
        parsed_metadata = ParsedMetadata(**metadata_json)
        
        # Validate metadata
        validation_config = MetadataValidationConfig(
            check_duplicates=check_duplicates,
            duplicate_scope="platform"
        )
        
        validation_result = await validator_service.validate_metadata(
            parsed_metadata=parsed_metadata,
            file_format=MetadataFormat.JSON,
            config=validation_config
        )
        
        # Set user info
        validation_result.user_id = current_user.id
        validation_result.file_name = "direct_json_validation"
        validation_result.file_size = len(json.dumps(metadata_json).encode('utf-8'))
        
        return {
            "success": True,
            "message": "JSON metadata validated successfully",
            "validation_status": validation_result.validation_status,
            "validation_errors": [error.dict() for error in validation_result.validation_errors],
            "validation_warnings": [warning.dict() for warning in validation_result.validation_warnings],
            "duplicates_found": validation_result.duplicate_count,
            "duplicate_details": [dup.dict() for dup in validation_result.duplicates_found],
            "schema_valid": validation_result.schema_valid,
            "processing_time": validation_result.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error validating JSON metadata: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate JSON metadata: {str(e)}"
        )

@router.get("/validation-results/{validation_id}")
async def get_validation_result(
    validation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get validation result by ID"""
    try:
        result = await mongo_db["metadata_validation_results"].find_one({
            "_id": validation_id,
            "user_id": current_user.id  # Users can only access their own results
        })
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Validation result not found"
            )
        
        # Remove MongoDB _id for response
        result.pop("_id", None)
        
        return {
            "success": True,
            "validation_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving validation result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve validation result: {str(e)}"
        )

@router.get("/validation-results", response_model=Dict[str, Any])
async def list_validation_results(
    limit: int = 20,
    offset: int = 0,
    status_filter: Optional[ValidationStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """List validation results for current user"""
    try:
        query = {"user_id": current_user.id}
        
        if status_filter:
            query["validation_status"] = status_filter
        
        # Get total count
        total_count = await mongo_db["metadata_validation_results"].count_documents(query)
        
        # Get paginated results
        cursor = mongo_db["metadata_validation_results"].find(query).sort("upload_date", -1).skip(offset).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id for response
        for result in results:
            result.pop("_id", None)
        
        return {
            "success": True,
            "validation_results": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing validation results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list validation results: {str(e)}"
        )

@router.get("/duplicates/check")
async def check_identifier_duplicates(
    identifier_type: str,
    identifier_value: str,
    current_user: dict = Depends(get_current_user)
):
    """Check for duplicates of a specific identifier (ISRC, UPC, EAN)"""
    try:
        if identifier_type.lower() not in ['isrc', 'upc', 'ean']:
            raise HTTPException(
                status_code=400,
                detail="Invalid identifier type. Must be 'isrc', 'upc', or 'ean'"
            )
        
        duplicates = await validator_service._find_identifier_duplicates(
            identifier_type.lower(), 
            identifier_value
        )
        
        return {
            "success": True,
            "identifier_type": identifier_type.lower(),
            "identifier_value": identifier_value,
            "duplicates_found": len(duplicates),
            "duplicate_details": [dup.dict() for dup in duplicates]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking duplicates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check duplicates: {str(e)}"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_metadata_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get metadata validation statistics for current user"""
    try:
        user_query = {"user_id": current_user.id}
        
        # Count by validation status
        total_validations = await mongo_db["metadata_validation_results"].count_documents(user_query)
        
        valid_count = await mongo_db["metadata_validation_results"].count_documents({
            **user_query,
            "validation_status": ValidationStatus.VALID
        })
        
        warning_count = await mongo_db["metadata_validation_results"].count_documents({
            **user_query, 
            "validation_status": ValidationStatus.WARNING
        })
        
        error_count = await mongo_db["metadata_validation_results"].count_documents({
            **user_query,
            "validation_status": ValidationStatus.ERROR
        })
        
        # Count by format
        format_stats = {}
        for format_type in MetadataFormat:
            count = await mongo_db["metadata_validation_results"].count_documents({
                **user_query,
                "file_format": format_type
            })
            format_stats[format_type] = count
        
        # Duplicate statistics
        duplicate_count = await mongo_db["metadata_validation_results"].count_documents({
            **user_query,
            "duplicate_count": {"$gt": 0}
        })
        
        return {
            "success": True,
            "statistics": {
                "total_validations": total_validations,
                "validation_status": {
                    "valid": valid_count,
                    "warning": warning_count,
                    "error": error_count
                },
                "format_distribution": format_stats,
                "files_with_duplicates": duplicate_count,
                "success_rate": round((valid_count / total_validations * 100), 2) if total_validations > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting metadata statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metadata statistics: {str(e)}"
        )

@router.get("/formats/supported")
async def get_supported_formats():
    """Get list of supported metadata formats and their specifications"""
    return {
        "success": True,
        "supported_formats": {
            "ddex_ern": {
                "name": "DDEX ERN",
                "description": "Digital Data Exchange Electronic Release Notification",
                "file_extensions": [".xml"],
                "supported_versions": list(DDEX_VERSIONS.keys()),
                "mime_types": ["application/xml", "text/xml"],
                "max_file_size": "50MB"
            },
            "mead": {
                "name": "MEAD",
                "description": "Music and Entertainment Asset Database",
                "file_extensions": [".json", ".xml", ".csv"],
                "mime_types": ["application/json", "application/xml", "text/csv"],
                "max_file_size": "50MB"
            },
            "json": {
                "name": "JSON Metadata",
                "description": "Standard JSON metadata format",
                "file_extensions": [".json"],
                "mime_types": ["application/json"],
                "max_file_size": "50MB"
            },
            "csv": {
                "name": "CSV Metadata", 
                "description": "Comma-Separated Values metadata format",
                "file_extensions": [".csv"],
                "mime_types": ["text/csv", "application/csv"],
                "max_file_size": "50MB"
            }
        },
        "validation_features": {
            "schema_validation": "XSD for XML, JSON Schema for JSON",
            "required_fields": ["title", "artist", "isrc", "release_date", "rights_holders"],
            "format_validation": "ISRC, UPC, EAN format checking",
            "duplicate_detection": "Platform-wide ISRC/UPC duplicate detection",
            "business_rules": "Date validation, track numbering, rights validation"
        }
    }

@router.post("/upload", response_model=Dict[str, Any])
async def upload_metadata_file(
    file: UploadFile = File(...),
    format: MetadataFormat = Form(...),
    validate_metadata: bool = Form(True),
    check_duplicates: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process metadata file (alias for parse endpoint)
    This endpoint provides the same functionality as /parse but with upload semantics
    """
    try:
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 50MB."
            )
        
        # Parse metadata
        parsed_metadata, parsing_errors = parser_service.parse_metadata(
            content=file_content,
            file_format=format,
            file_name=file.filename
        )
        
        # Initialize validation result
        validation_result = MetadataValidationResult(
            user_id=current_user.id,
            file_name=file.filename,
            file_size=file_size,
            file_format=format,
            parsing_status=ValidationStatus.VALID if not parsing_errors else ValidationStatus.WARNING,
            parsing_errors=parsing_errors,
            parsed_metadata=parsed_metadata,
            validation_status=ValidationStatus.PENDING
        )
        
        # Perform validation if requested
        if validate_metadata:
            validation_config = MetadataValidationConfig(
                check_duplicates=check_duplicates,
                duplicate_scope="platform"
            )
            
            validation_result = await validator_service.validate_metadata(
                parsed_metadata=parsed_metadata,
                file_format=format,
                config=validation_config
            )
            
            # Set user and file info
            validation_result.user_id = current_user.id
            validation_result.file_name = file.filename
            validation_result.file_size = file_size
            validation_result.parsing_errors = parsing_errors
        
        # Store validation result in database
        try:
            result_dict = validation_result.dict()
            result_dict["_id"] = validation_result.id
            result_dict["created_at"] = datetime.now()
            
            await mongo_db["metadata_validation_results"].insert_one(result_dict)
            logger.info(f"Stored validation result {validation_result.id} for user {current_user.id}")
            
        except Exception as e:
            logger.error(f"Failed to store validation result: {str(e)}")
            # Continue without storing - don't fail the request
        
        return {
            "success": True,
            "message": "Metadata file uploaded and processed successfully",
            "validation_id": validation_result.id,
            "parsing_status": validation_result.parsing_status,
            "validation_status": validation_result.validation_status,
            "parsed_metadata": validation_result.parsed_metadata.dict(),
            "validation_errors": [error.dict() for error in validation_result.validation_errors],
            "validation_warnings": [warning.dict() for warning in validation_result.validation_warnings],
            "duplicates_found": validation_result.duplicate_count,
            "duplicate_details": [dup.dict() for dup in validation_result.duplicates_found],
            "processing_time": validation_result.processing_time,
            "upload_status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading metadata file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload metadata file: {str(e)}"
        )

# Admin endpoints
@router.get("/admin/all-results", response_model=Dict[str, Any])
async def admin_get_all_validation_results(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[ValidationStatus] = None,
    current_user: dict = Depends(require_admin)
):
    """Admin endpoint to get all validation results across platform"""
    try:
        query = {}
        
        if status_filter:
            query["validation_status"] = status_filter
        
        # Get total count
        total_count = await mongo_db["metadata_validation_results"].count_documents(query)
        
        # Get paginated results
        cursor = mongo_db["metadata_validation_results"].find(query).sort("upload_date", -1).skip(offset).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id for response
        for result in results:
            result.pop("_id", None)
        
        return {
            "success": True,
            "validation_results": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting all validation results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get all validation results: {str(e)}"
        )

@router.get("/admin/platform-statistics")
async def admin_get_platform_statistics(
    current_user: dict = Depends(require_admin)
):
    """Admin endpoint to get platform-wide metadata statistics"""
    try:
        # Overall statistics
        total_validations = await mongo_db["metadata_validation_results"].count_documents({})
        
        # Count by validation status
        status_stats = {}
        for status in ValidationStatus:
            count = await mongo_db["metadata_validation_results"].count_documents({
                "validation_status": status
            })
            status_stats[status] = count
        
        # Count by format
        format_stats = {}
        for format_type in MetadataFormat:
            count = await mongo_db["metadata_validation_results"].count_documents({
                "file_format": format_type
            })
            format_stats[format_type] = count
        
        # User statistics
        unique_users_cursor = mongo_db["metadata_validation_results"].distinct("user_id")
        unique_users_list = await unique_users_cursor.to_list(length=None)
        unique_users = len(unique_users_list)
        
        # Duplicate statistics
        total_duplicates = await mongo_db["metadata_validation_results"].count_documents({
            "duplicate_count": {"$gt": 0}
        })
        
        return {
            "success": True,
            "platform_statistics": {
                "total_validations": total_validations,
                "unique_users": unique_users,
                "validation_status": status_stats,
                "format_distribution": format_stats,
                "files_with_duplicates": total_duplicates,
                "overall_success_rate": round(
                    (status_stats.get(ValidationStatus.VALID, 0) / total_validations * 100), 2
                ) if total_validations > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting platform statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get platform statistics: {str(e)}"
        )

# Import DDEX_VERSIONS for the formats endpoint
from metadata_models import DDEX_VERSIONS