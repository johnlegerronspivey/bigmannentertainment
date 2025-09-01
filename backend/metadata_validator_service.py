"""
Metadata Validator Service
Handles schema validation, required field checks, and duplicate detection
"""

import re
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import logging
from urllib.parse import urlparse
import requests
from xml.parsers.expat import ExpatError

from metadata_models import (
    ParsedMetadata, MetadataValidationError, ValidationSeverity, 
    ValidationStatus, MetadataValidationResult, DuplicateRecord,
    MetadataValidationConfig, MetadataFormat, DDEX_VERSIONS
)

logger = logging.getLogger(__name__)

class MetadataValidatorService:
    """Service for validating metadata schemas, required fields, and duplicates"""
    
    def __init__(self, mongo_db=None):
        self.mongo_db = mongo_db
        self.validation_config = MetadataValidationConfig()
        
        # ISRC format: Country Code (2) + Registrant Code (3) + Year (2) + Designation Code (5)
        self.isrc_pattern = re.compile(r'^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$')
        
        # UPC format: 12 digits
        self.upc_pattern = re.compile(r'^\d{12}$')
        
        # EAN format: 13 digits  
        self.ean_pattern = re.compile(r'^\d{13}$')
        
        # JSON Schema for standard metadata validation
        self.metadata_json_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1, "maxLength": 500},
                "artist": {"type": "string", "minLength": 1, "maxLength": 200},
                "album": {"type": "string", "maxLength": 200},
                "isrc": {"type": "string", "pattern": "^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$"},
                "upc": {"type": "string", "pattern": "^\\d{12}$"},
                "ean": {"type": "string", "pattern": "^\\d{13}$"},
                "rights_holders": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1
                },
                "genre": {"type": "string", "maxLength": 100},
                "copyright_year": {"type": "integer", "minimum": 1900, "maximum": 2100},
                "duration": {"type": "string", "pattern": "^([0-9]+:)?[0-5]?[0-9]:[0-5][0-9]$"},
                "track_number": {"type": "integer", "minimum": 1, "maximum": 999},
                "release_date": {"type": "string", "format": "date-time"}
            },
            "required": ["title", "artist", "isrc", "rights_holders"]
        }
    
    async def validate_metadata(self, parsed_metadata: ParsedMetadata, file_format: MetadataFormat, 
                         config: Optional[MetadataValidationConfig] = None) -> MetadataValidationResult:
        """Comprehensive metadata validation"""
        
        if config:
            self.validation_config = config
            
        validation_result = MetadataValidationResult(
            user_id="",  # Will be set by caller
            file_name="",  # Will be set by caller
            file_size=0,  # Will be set by caller
            file_format=file_format,
            parsed_metadata=parsed_metadata
        )
        
        start_time = datetime.now()
        
        # 1. Schema Validation
        if self.validation_config.validate_schema:
            schema_errors = self._validate_schema(parsed_metadata, file_format)
            validation_result.schema_errors = schema_errors
            validation_result.schema_valid = len(schema_errors) == 0
        
        # 2. Required Fields Validation
        required_errors = self._validate_required_fields(parsed_metadata)
        validation_result.validation_errors.extend(required_errors)
        
        # 3. Format Validation (ISRC, UPC, etc.)
        format_errors = self._validate_formats(parsed_metadata)
        validation_result.validation_errors.extend(format_errors)
        
        # 4. Business Logic Validation
        business_errors = self._validate_business_logic(parsed_metadata)
        validation_result.validation_errors.extend(business_errors)
        
        # 5. Duplicate Detection
        if self.validation_config.check_duplicates:
            duplicates = await self._check_duplicates(parsed_metadata)
            validation_result.duplicates_found = duplicates
            validation_result.duplicate_count = len(duplicates)
        
        # Determine overall validation status
        validation_result.validation_status = self._determine_validation_status(
            validation_result.validation_errors + validation_result.schema_errors,
            validation_result.duplicates_found
        )
        
        # Calculate processing time
        end_time = datetime.now()
        validation_result.processing_time = (end_time - start_time).total_seconds()
        
        # Categorize errors
        for error in validation_result.validation_errors + validation_result.schema_errors:
            if error.severity in [ValidationSeverity.WARNING, ValidationSeverity.INFO]:
                validation_result.validation_warnings.append(error)
        
        return validation_result
    
    def _validate_schema(self, metadata: ParsedMetadata, file_format: MetadataFormat) -> List[MetadataValidationError]:
        """Validate metadata against appropriate schema"""
        errors = []
        
        try:
            if file_format == MetadataFormat.DDEX_ERN:
                errors.extend(self._validate_ddex_schema(metadata))
            elif file_format in [MetadataFormat.JSON, MetadataFormat.MEAD]:
                errors.extend(self._validate_json_schema(metadata))
            elif file_format == MetadataFormat.CSV:
                errors.extend(self._validate_csv_schema(metadata))
                
        except Exception as e:
            logger.error(f"Schema validation error: {str(e)}")
            errors.append(MetadataValidationError(
                field="schema",
                message=f"Schema validation failed: {str(e)}",
                severity=ValidationSeverity.ERROR,
                error_code="SCHEMA_VALIDATION_ERROR"
            ))
        
        return errors
    
    def _validate_ddex_schema(self, metadata: ParsedMetadata) -> List[MetadataValidationError]:
        """Validate DDEX-specific schema requirements"""
        errors = []
        
        # DDEX version validation
        if not metadata.ddex_version:
            errors.append(MetadataValidationError(
                field="ddex_version",
                message="DDEX version not specified",
                severity=ValidationSeverity.WARNING,
                suggested_fix="Include DDEX version in XML namespace"
            ))
        elif metadata.ddex_version not in DDEX_VERSIONS:
            errors.append(MetadataValidationError(
                field="ddex_version",
                message=f"Unsupported DDEX version: {metadata.ddex_version}",
                severity=ValidationSeverity.WARNING,
                suggested_fix=f"Use supported versions: {list(DDEX_VERSIONS.keys())}"
            ))
        
        # DDEX message ID validation
        if not metadata.ddex_message_id:
            errors.append(MetadataValidationError(
                field="ddex_message_id",
                message="DDEX Message ID is required",
                severity=ValidationSeverity.ERROR,
                error_code="MISSING_MESSAGE_ID"
            ))
        
        # Party ID validation for DDEX
        if not metadata.party_id:
            errors.append(MetadataValidationError(
                field="party_id",
                message="Party ID is recommended for DDEX messages",
                severity=ValidationSeverity.WARNING,
                suggested_fix="Include PartyId in PartyList section"
            ))
        
        return errors
    
    def _validate_json_schema(self, metadata: ParsedMetadata) -> List[MetadataValidationError]:
        """Validate JSON metadata against schema"""
        errors = []
        
        try:
            # Convert parsed metadata to dict for JSON schema validation
            metadata_dict = {}
            
            # Map ParsedMetadata fields to dict
            for field_name in self.metadata_json_schema["properties"].keys():
                value = getattr(metadata, field_name, None)
                if value is not None:
                    # Convert datetime to ISO string for schema validation
                    if isinstance(value, datetime):
                        metadata_dict[field_name] = value.isoformat()
                    else:
                        metadata_dict[field_name] = value
            
            # Validate required fields
            for required_field in self.metadata_json_schema.get("required", []):
                if required_field not in metadata_dict or not metadata_dict[required_field]:
                    errors.append(MetadataValidationError(
                        field=required_field,
                        message=f"Required field '{required_field}' is missing or empty",
                        severity=ValidationSeverity.ERROR,
                        error_code="MISSING_REQUIRED_FIELD"
                    ))
            
            # Validate field properties
            for field_name, field_schema in self.metadata_json_schema["properties"].items():
                if field_name in metadata_dict:
                    value = metadata_dict[field_name]
                    field_errors = self._validate_json_field(field_name, value, field_schema)
                    errors.extend(field_errors)
                    
        except Exception as e:
            logger.error(f"JSON schema validation error: {str(e)}")
            errors.append(MetadataValidationError(
                field="json_schema",
                message=f"JSON schema validation failed: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        return errors
    
    def _validate_json_field(self, field_name: str, value: Any, schema: Dict) -> List[MetadataValidationError]:
        """Validate individual JSON field against schema"""
        errors = []
        
        # Type validation
        expected_type = schema.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(MetadataValidationError(
                field=field_name,
                message=f"Field '{field_name}' must be a string",
                severity=ValidationSeverity.ERROR
            ))
            return errors
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append(MetadataValidationError(
                field=field_name,
                message=f"Field '{field_name}' must be an integer",
                severity=ValidationSeverity.ERROR
            ))
            return errors
        elif expected_type == "array" and not isinstance(value, list):
            errors.append(MetadataValidationError(
                field=field_name,
                message=f"Field '{field_name}' must be an array",
                severity=ValidationSeverity.ERROR
            ))
            return errors
        
        # String validations
        if expected_type == "string" and isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                errors.append(MetadataValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be at least {schema['minLength']} characters",
                    severity=ValidationSeverity.ERROR
                ))
            
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                errors.append(MetadataValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must not exceed {schema['maxLength']} characters",
                    severity=ValidationSeverity.WARNING
                ))
            
            if "pattern" in schema:
                pattern = re.compile(schema["pattern"])
                if not pattern.match(value):
                    errors.append(MetadataValidationError(
                        field=field_name,
                        message=f"Field '{field_name}' does not match required pattern",
                        severity=ValidationSeverity.ERROR,
                        suggested_fix=f"Pattern: {schema['pattern']}"
                    ))
        
        # Integer validations
        if expected_type == "integer" and isinstance(value, int):
            if "minimum" in schema and value < schema["minimum"]:
                errors.append(MetadataValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must be at least {schema['minimum']}",
                    severity=ValidationSeverity.ERROR
                ))
            
            if "maximum" in schema and value > schema["maximum"]:
                errors.append(MetadataValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must not exceed {schema['maximum']}",
                    severity=ValidationSeverity.ERROR
                ))
        
        # Array validations
        if expected_type == "array" and isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                errors.append(MetadataValidationError(
                    field=field_name,
                    message=f"Field '{field_name}' must have at least {schema['minItems']} items",
                    severity=ValidationSeverity.ERROR
                ))
        
        return errors
    
    def _validate_csv_schema(self, metadata: ParsedMetadata) -> List[MetadataValidationError]:
        """Validate CSV-specific requirements"""
        errors = []
        
        # CSV should have basic required fields
        csv_required = ["title", "artist"]
        for field in csv_required:
            value = getattr(metadata, field, None)
            if not value:
                errors.append(MetadataValidationError(
                    field=field,
                    message=f"CSV field '{field}' is required",
                    severity=ValidationSeverity.ERROR,
                    suggested_fix=f"Add '{field}' column to CSV"
                ))
        
        return errors
    
    def _validate_required_fields(self, metadata: ParsedMetadata) -> List[MetadataValidationError]:
        """Validate required fields based on configuration"""
        errors = []
        
        for field_name in self.validation_config.required_fields:
            value = getattr(metadata, field_name, None)
            
            if not value:
                errors.append(MetadataValidationError(
                    field=field_name,
                    message=f"Required field '{field_name}' is missing",
                    severity=ValidationSeverity.ERROR,
                    error_code="MISSING_REQUIRED_FIELD",
                    suggested_fix=f"Provide a value for '{field_name}'"
                ))
            elif isinstance(value, str) and not value.strip():
                errors.append(MetadataValidationError(
                    field=field_name,
                    message=f"Required field '{field_name}' is empty",
                    severity=ValidationSeverity.ERROR,
                    error_code="EMPTY_REQUIRED_FIELD"
                ))
        
        return errors
    
    def _validate_formats(self, metadata: ParsedMetadata) -> List[MetadataValidationError]:
        """Validate identifier formats (ISRC, UPC, etc.)"""
        errors = []
        
        # ISRC validation
        if metadata.isrc and self.validation_config.validate_isrc_format:
            if not self.isrc_pattern.match(metadata.isrc):
                errors.append(MetadataValidationError(
                    field="isrc",
                    message=f"Invalid ISRC format: {metadata.isrc}",
                    severity=ValidationSeverity.ERROR,
                    error_code="INVALID_ISRC_FORMAT",
                    suggested_fix="ISRC format: CC-XXX-YY-NNNNN (e.g., US-S1Z-99-00001)"
                ))
        
        # UPC validation
        if metadata.upc and self.validation_config.validate_upc_format:
            if not self.upc_pattern.match(metadata.upc):
                errors.append(MetadataValidationError(
                    field="upc",
                    message=f"Invalid UPC format: {metadata.upc}",
                    severity=ValidationSeverity.ERROR,
                    error_code="INVALID_UPC_FORMAT",
                    suggested_fix="UPC must be 12 digits"
                ))
        
        # EAN validation
        if metadata.ean:
            if not self.ean_pattern.match(metadata.ean):
                errors.append(MetadataValidationError(
                    field="ean",
                    message=f"Invalid EAN format: {metadata.ean}",
                    severity=ValidationSeverity.ERROR,
                    error_code="INVALID_EAN_FORMAT",
                    suggested_fix="EAN must be 13 digits"
                ))
        
        # Duration format validation
        if metadata.duration:
            duration_pattern = re.compile(r'^([0-9]+:)?[0-5]?[0-9]:[0-5][0-9]$')
            if not duration_pattern.match(metadata.duration):
                errors.append(MetadataValidationError(
                    field="duration",
                    message=f"Invalid duration format: {metadata.duration}",
                    severity=ValidationSeverity.WARNING,
                    suggested_fix="Duration format: MM:SS or HH:MM:SS"
                ))
        
        return errors
    
    def _validate_business_logic(self, metadata: ParsedMetadata) -> List[MetadataValidationError]:
        """Validate business logic rules"""
        errors = []
        
        # Date validations
        if self.validation_config.validate_dates:
            current_year = datetime.now().year
            
            # Release date validation
            if metadata.release_date:
                if metadata.release_date.year > current_year + 2:
                    errors.append(MetadataValidationError(
                        field="release_date",
                        message=f"Release date seems too far in future: {metadata.release_date.date()}",
                        severity=ValidationSeverity.WARNING,
                        suggested_fix="Verify release date is correct"
                    ))
                elif metadata.release_date.year < 1900:
                    errors.append(MetadataValidationError(
                        field="release_date",
                        message=f"Release date seems too old: {metadata.release_date.date()}",
                        severity=ValidationSeverity.WARNING
                    ))
            
            # Copyright year validation
            if metadata.copyright_year:
                if metadata.copyright_year > current_year + 1:
                    errors.append(MetadataValidationError(
                        field="copyright_year",
                        message=f"Copyright year seems too far in future: {metadata.copyright_year}",
                        severity=ValidationSeverity.WARNING
                    ))
                elif metadata.copyright_year < 1900:
                    errors.append(MetadataValidationError(
                        field="copyright_year",
                        message=f"Copyright year seems too old: {metadata.copyright_year}",
                        severity=ValidationSeverity.WARNING
                    ))
        
        # Track number validation
        if metadata.track_number and metadata.total_tracks:
            if metadata.track_number > metadata.total_tracks:
                errors.append(MetadataValidationError(
                    field="track_number",
                    message=f"Track number ({metadata.track_number}) exceeds total tracks ({metadata.total_tracks})",
                    severity=ValidationSeverity.ERROR
                ))
        
        # Rights holders validation
        if metadata.rights_holders:
            for i, holder in enumerate(metadata.rights_holders):
                if not holder or not holder.strip():
                    errors.append(MetadataValidationError(
                        field="rights_holders",
                        message=f"Empty rights holder at position {i+1}",
                        severity=ValidationSeverity.WARNING
                    ))
        
        return errors
    
    async def _check_duplicates(self, metadata: ParsedMetadata) -> List[DuplicateRecord]:
        """Check for duplicate ISRCs and UPCs platform-wide"""
        duplicates = []
        
        if self.mongo_db is None:
            return duplicates
        
        try:
            # Check ISRC duplicates
            if metadata.isrc:
                isrc_duplicates = await self._find_identifier_duplicates("isrc", metadata.isrc)
                duplicates.extend(isrc_duplicates)
            
            # Check UPC duplicates
            if metadata.upc:
                upc_duplicates = await self._find_identifier_duplicates("upc", metadata.upc)
                duplicates.extend(upc_duplicates)
            
            # Check EAN duplicates
            if metadata.ean:
                ean_duplicates = await self._find_identifier_duplicates("ean", metadata.ean)
                duplicates.extend(ean_duplicates)
                
        except Exception as e:
            logger.error(f"Duplicate detection error: {str(e)}")
        
        return duplicates
    
    async def _find_identifier_duplicates(self, identifier_type: str, identifier_value: str) -> List[DuplicateRecord]:
        """Find duplicates for specific identifier"""
        duplicates = []
        
        try:
            # Search in metadata_validation_results collection
            collection = self.mongo_db["metadata_validation_results"]
            
            query = {
                f"parsed_metadata.{identifier_type}": identifier_value,
                "validation_status": {"$ne": "error"}  # Exclude failed validations
            }
            
            cursor = collection.find(query)
            existing_records = await cursor.to_list(length=100)  # Limit to prevent memory issues
            
            for record in existing_records:
                duplicate = DuplicateRecord(
                    identifier_type=identifier_type,
                    identifier_value=identifier_value,
                    first_seen_date=record.get("upload_date", datetime.now()),
                    last_seen_date=datetime.now(),
                    user_id=record.get("user_id", "unknown"),
                    file_name=record.get("file_name", "unknown"),
                    metadata_id=record.get("_id", "unknown")
                )
                duplicates.append(duplicate)
                
        except Exception as e:
            logger.error(f"Error finding {identifier_type} duplicates: {str(e)}")
        
        return duplicates
    
    def _determine_validation_status(self, errors: List[MetadataValidationError], 
                                   duplicates: List[DuplicateRecord]) -> ValidationStatus:
        """Determine overall validation status"""
        
        # Check for critical/error severity issues
        critical_errors = [e for e in errors if e.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]]
        
        if critical_errors:
            return ValidationStatus.ERROR
        
        # Check for warnings or duplicates
        warnings = [e for e in errors if e.severity == ValidationSeverity.WARNING]
        
        if warnings or duplicates:
            return ValidationStatus.WARNING
        
        return ValidationStatus.VALID
    
    def validate_file_size(self, file_size: int) -> Optional[MetadataValidationError]:
        """Validate metadata file size"""
        if file_size > self.validation_config.max_file_size:
            return MetadataValidationError(
                field="file_size",
                message=f"File size ({file_size} bytes) exceeds maximum ({self.validation_config.max_file_size} bytes)",
                severity=ValidationSeverity.ERROR,
                error_code="FILE_TOO_LARGE"
            )
        return None