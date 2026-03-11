"""
GS1 Asset Registry Service
Core business logic for GS1 identifier generation, validation, and management
"""

import asyncio
import hashlib
import os
import qrcode
import io
import base64
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import IndexModel
import re
import logging
import uuid

from gs1_models import (
    GS1Asset, AssetType, IdentifierType, GS1IdentifierStatus,
    GTINIdentifier, GLNIdentifier, GDTIIdentifier, ISRCIdentifier, ISANIdentifier,
    GS1DigitalLink, DigitalLinkConfig, AssetMetadata,
    CreateAssetRequest, UpdateAssetRequest, GenerateIdentifierRequest,
    CreateDigitalLinkRequest, AssetSearchFilter, IdentifierValidationResult,
    AnalyticsData, BatchOperationRequest, BatchOperationResult
)

logger = logging.getLogger(__name__)


class GS1Service:
    """Main service class for GS1 Asset Registry operations"""
    
    def __init__(self, database):
        self.db = database
        self.assets_collection: AsyncIOMotorCollection = database.gs1_assets
        self.identifiers_collection: AsyncIOMotorCollection = database.gs1_identifiers
        self.digital_links_collection: AsyncIOMotorCollection = database.gs1_digital_links
        self.analytics_collection: AsyncIOMotorCollection = database.gs1_analytics
        
        # GS1 Company Prefix (Big Mann Entertainment official prefix)
        self.company_prefix = "08600043402"  # Official GS1 company prefix
        self.legal_entity_gln = "0860004340201"  # Legal Entity Global Location Number
        self.base_uri = os.environ.get("FRONTEND_URL", "https://bigmannentertainment.com")
        
        # Initialize collections (only schedule if an event loop is running)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._initialize_collections())
        except RuntimeError:
            # When imported in non-ASGI contexts (e.g. pytest import of server.py),
            # there may be no running event loop. In that case, we skip background
            # initialization; collections will be created lazily when the service
            # is used under a real event loop.
            logger.warning("GS1Service initialization skipped: no running event loop available")
    
    async def _initialize_collections(self):
        """Initialize database collections with indexes"""
        try:
            # Assets collection indexes
            await self.assets_collection.create_indexes([
                IndexModel([("asset_id", 1)], unique=True),
                IndexModel([("asset_type", 1)]),
                IndexModel([("status", 1)]),
                IndexModel([("created_at", -1)]),
                IndexModel([("metadata.title", "text"), ("metadata.description", "text")]),
                IndexModel([("identifiers.gtin.value", 1)]),
                IndexModel([("identifiers.gln.value", 1)]),
                IndexModel([("identifiers.gdti.value", 1)]),
                IndexModel([("identifiers.isrc.value", 1)]),
                IndexModel([("identifiers.isan.value", 1)])
            ])
            
            # Digital Links collection indexes
            await self.digital_links_collection.create_indexes([
                IndexModel([("link_id", 1)], unique=True),
                IndexModel([("asset_id", 1)]),
                IndexModel([("identifier.value", 1)]),
                IndexModel([("created_at", -1)])
            ])
            
            logger.info("GS1 database collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing GS1 collections: {e}")
    
    # Asset Management Methods
    
    async def create_asset(self, request: CreateAssetRequest, user_id: str = None) -> GS1Asset:
        """Create a new GS1 asset with optional identifier generation"""
        try:
            # Create base asset
            asset = GS1Asset(
                asset_type=request.asset_type,
                metadata=request.metadata,
                created_by=user_id,
                updated_by=user_id
            )
            
            # Generate requested identifiers
            for identifier_type in request.generate_identifiers:
                identifier = await self._generate_identifier(
                    asset.asset_id, 
                    identifier_type, 
                    request.metadata
                )
                asset.identifiers[identifier_type.value] = identifier
            
            # Generate Digital Link if GTIN exists and config provided
            if IdentifierType.GTIN in request.generate_identifiers and request.digital_link_config:
                gtin_identifier = asset.identifiers.get(IdentifierType.GTIN.value)
                if gtin_identifier:
                    digital_link = await self._create_digital_link(
                        asset.asset_id,
                        gtin_identifier,
                        request.digital_link_config
                    )
                    asset.digital_links.append(digital_link)
            
            # Save to database
            result = await self.assets_collection.insert_one(asset.dict())
            if result.inserted_id:
                logger.info(f"Created GS1 asset: {asset.asset_id}")
                await self._update_analytics("asset_created", asset.asset_type)
                return asset
            else:
                raise Exception("Failed to save asset to database")
                
        except Exception as e:
            logger.error(f"Error creating GS1 asset: {e}")
            raise
    
    async def get_asset(self, asset_id: str) -> Optional[GS1Asset]:
        """Retrieve a single asset by ID"""
        try:
            asset_data = await self.assets_collection.find_one({"asset_id": asset_id})
            if asset_data:
                return GS1Asset(**asset_data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving asset {asset_id}: {e}")
            raise
    
    async def update_asset(self, asset_id: str, request: UpdateAssetRequest, user_id: str = None) -> Optional[GS1Asset]:
        """Update an existing asset"""
        try:
            update_data = {"updated_at": datetime.now(timezone.utc)}
            
            if request.metadata:
                update_data["metadata"] = request.metadata.dict()
            if request.status:
                update_data["status"] = request.status
            if request.external_references:
                update_data["external_references"] = request.external_references
            if user_id:
                update_data["updated_by"] = user_id
            
            result = await self.assets_collection.update_one(
                {"asset_id": asset_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_asset(asset_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating asset {asset_id}: {e}")
            raise
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset and its associated data"""
        try:
            # Delete digital links
            await self.digital_links_collection.delete_many({"asset_id": asset_id})
            
            # Delete asset
            result = await self.assets_collection.delete_one({"asset_id": asset_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted GS1 asset: {asset_id}")
                await self._update_analytics("asset_deleted")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting asset {asset_id}: {e}")
            raise
    
    async def search_assets(self, filters: AssetSearchFilter, page: int = 1, page_size: int = 20) -> Tuple[List[GS1Asset], int]:
        """Search assets with filters and pagination"""
        try:
            query = {}
            
            # Build query from filters
            if filters.asset_type:
                query["asset_type"] = filters.asset_type
            if filters.status:
                query["status"] = filters.status
            if filters.created_after:
                query["created_at"] = {"$gte": filters.created_after}
            if filters.created_before:
                if "created_at" in query:
                    query["created_at"]["$lte"] = filters.created_before
                else:
                    query["created_at"] = {"$lte": filters.created_before}
            if filters.text_search:
                query["$text"] = {"$search": filters.text_search}
            
            # Count total results
            total_count = await self.assets_collection.count_documents(query)
            
            # Get paginated results
            skip = (page - 1) * page_size
            cursor = self.assets_collection.find(query).skip(skip).limit(page_size).sort("created_at", -1)
            
            assets = []
            async for asset_data in cursor:
                assets.append(GS1Asset(**asset_data))
            
            return assets, total_count
            
        except Exception as e:
            logger.error(f"Error searching assets: {e}")
            raise
    
    # Identifier Generation Methods
    
    async def _generate_identifier(self, asset_id: str, identifier_type: IdentifierType, metadata: AssetMetadata) -> Union[GTINIdentifier, GLNIdentifier, GDTIIdentifier, ISRCIdentifier, ISANIdentifier]:
        """Generate a specific type of identifier"""
        try:
            if identifier_type == IdentifierType.GTIN:
                return await self._generate_gtin(asset_id, metadata)
            elif identifier_type == IdentifierType.GLN:
                return await self._generate_gln(asset_id, metadata)
            elif identifier_type == IdentifierType.GDTI:
                return await self._generate_gdti(asset_id, metadata)
            elif identifier_type == IdentifierType.ISRC:
                return await self._generate_isrc(asset_id, metadata)
            elif identifier_type == IdentifierType.ISAN:
                return await self._generate_isan(asset_id, metadata)
            else:
                raise ValueError(f"Unsupported identifier type: {identifier_type}")
                
        except Exception as e:
            logger.error(f"Error generating {identifier_type} identifier: {e}")
            raise
    
    async def _generate_gtin(self, asset_id: str, metadata: AssetMetadata) -> GTINIdentifier:
        """Generate GTIN identifier"""
        # Generate unique item reference
        item_ref = str(hash(asset_id) % 10000).zfill(4)
        
        # Construct GTIN-13
        gtin_base = self.company_prefix + item_ref
        check_digit = self._calculate_gtin_check_digit(gtin_base)
        gtin_value = gtin_base + check_digit
        
        return GTINIdentifier(
            value=gtin_value,
            company_prefix=self.company_prefix,
            item_reference=item_ref,
            check_digit=check_digit,
            gtin_format="GTIN-13",
            metadata={
                "generated_for": asset_id,
                "generation_method": "automatic",
                "title": metadata.title if metadata else "Generated GTIN"
            }
        )
    
    async def _generate_gln(self, asset_id: str, metadata: AssetMetadata) -> GLNIdentifier:
        """Generate GLN identifier"""
        # Generate unique location reference
        location_ref = str(hash(asset_id + "location") % 1000).zfill(3)
        
        # Construct GLN
        gln_base = self.company_prefix + location_ref
        check_digit = self._calculate_gtin_check_digit(gln_base)  # Same algorithm as GTIN
        gln_value = gln_base + check_digit
        
        return GLNIdentifier(
            value=gln_value,
            company_prefix=self.company_prefix,
            location_reference=location_ref,
            check_digit=check_digit,
            location_type="Digital",
            metadata={
                "generated_for": asset_id,
                "generation_method": "automatic",
                "location_name": metadata.title if metadata else "Generated Location"
            }
        )
    
    async def _generate_gdti(self, asset_id: str, metadata: AssetMetadata) -> GDTIIdentifier:
        """Generate GDTI identifier"""
        # Generate document type and serial
        doc_type = "001"
        serial = str(hash(asset_id + "document"))[-8:]
        
        # Construct GDTI
        gdti_base = self.company_prefix + doc_type
        check_digit = self._calculate_gtin_check_digit(gdti_base)
        gdti_value = gdti_base + check_digit + serial
        
        return GDTIIdentifier(
            value=gdti_value,
            company_prefix=self.company_prefix,
            document_type=doc_type,
            serial_component=serial,
            check_digit=check_digit,
            metadata={
                "generated_for": asset_id,
                "generation_method": "automatic",
                "document_title": metadata.title if metadata else "Generated Document"
            }
        )
    
    async def _generate_isrc(self, asset_id: str, metadata: AssetMetadata) -> ISRCIdentifier:
        """Generate ISRC identifier"""
        country_code = "US"
        registrant_code = "BME"  # Big Mann Entertainment
        year = str(datetime.now().year)[-2:]
        designation = str(hash(asset_id) % 100000).zfill(5)
        
        isrc_value = f"{country_code}{registrant_code}{year}{designation}"
        
        return ISRCIdentifier(
            value=isrc_value,
            country_code=country_code,
            registrant_code=registrant_code,
            year_of_reference=year,
            designation_code=designation,
            metadata={
                "generated_for": asset_id,
                "generation_method": "automatic",
                "recording_title": metadata.title if metadata else "Generated Recording"
            }
        )
    
    async def _generate_isan(self, asset_id: str, metadata: AssetMetadata) -> ISANIdentifier:
        """Generate ISAN identifier"""
        # Generate ISAN root (simplified version)
        root_parts = []
        for i in range(4):
            part = hex(hash(asset_id + str(i)) % 65536)[2:].upper().zfill(4)
            root_parts.append(part)
        
        root = "-".join(root_parts)
        check_digit = hex(hash(root) % 16)[2:].upper()
        isan_value = f"{root}-{check_digit}"
        
        return ISANIdentifier(
            value=isan_value,
            root=root,
            check_digit=check_digit,
            metadata={
                "generated_for": asset_id,
                "generation_method": "automatic",
                "work_title": metadata.title if metadata else "Generated Audiovisual Work"
            }
        )
    
    def _calculate_gtin_check_digit(self, gtin_base: str) -> str:
        """Calculate GTIN check digit using modulo 10 algorithm"""
        total = 0
        for i, digit in enumerate(reversed(gtin_base)):
            weight = 3 if i % 2 == 0 else 1
            total += int(digit) * weight
        
        check_digit = (10 - (total % 10)) % 10
        return str(check_digit)
    
    # Digital Link Methods
    
    async def _create_digital_link(self, asset_id: str, identifier: Union[GTINIdentifier, GLNIdentifier, GDTIIdentifier], config: DigitalLinkConfig) -> GS1DigitalLink:
        """Create GS1 Digital Link"""
        try:
            # Construct URI
            if isinstance(identifier, GTINIdentifier):
                uri = f"{config.base_uri}/01/{identifier.value}"
            elif isinstance(identifier, GLNIdentifier):
                uri = f"{config.base_uri}/414/{identifier.value}"
            elif isinstance(identifier, GDTIIdentifier):
                uri = f"{config.base_uri}/253/{identifier.value}"
            else:
                raise ValueError(f"Unsupported identifier type for Digital Link: {type(identifier)}")
            
            # Add query parameters
            if config.query_params:
                query_string = "&".join([f"{k}={v}" for k, v in config.query_params.items()])
                uri += f"?{query_string}"
            
            # Generate QR code
            qr_code_data = await self._generate_qr_code(uri, config)
            
            digital_link = GS1DigitalLink(
                asset_id=asset_id,
                identifier=identifier,
                uri=uri,
                qr_code_data=qr_code_data,
                config=config
            )
            
            # Save to database
            await self.digital_links_collection.insert_one(digital_link.dict())
            
            return digital_link
            
        except Exception as e:
            logger.error(f"Error creating Digital Link: {e}")
            raise
    
    async def _generate_qr_code(self, uri: str, config: DigitalLinkConfig) -> str:
        """Generate QR code for Digital Link URI"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{config.error_correction_level}"),
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format=config.qr_code_format)
            qr_code_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/{config.qr_code_format.lower()};base64,{qr_code_data}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise
    
    # Validation Methods
    
    async def validate_identifier(self, identifier_value: str, identifier_type: IdentifierType) -> IdentifierValidationResult:
        """Validate a GS1 identifier"""
        try:
            errors = []
            suggestions = []
            is_valid = True
            formatted_value = identifier_value.strip().upper()
            
            if identifier_type == IdentifierType.GTIN:
                is_valid, errors, suggestions = self._validate_gtin(formatted_value)
            elif identifier_type == IdentifierType.GLN:
                is_valid, errors, suggestions = self._validate_gln(formatted_value)
            elif identifier_type == IdentifierType.GDTI:
                is_valid, errors, suggestions = self._validate_gdti(formatted_value)
            elif identifier_type == IdentifierType.ISRC:
                is_valid, errors, suggestions = self._validate_isrc(formatted_value)
            elif identifier_type == IdentifierType.ISAN:
                is_valid, errors, suggestions = self._validate_isan(formatted_value)
            
            # Check for duplicates
            existing = await self.assets_collection.find_one({
                f"identifiers.{identifier_type.value}.value": formatted_value
            })
            if existing:
                is_valid = False
                errors.append("Identifier already exists in the system")
            
            return IdentifierValidationResult(
                is_valid=is_valid,
                identifier_type=identifier_type,
                formatted_value=formatted_value,
                errors=errors,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error validating identifier: {e}")
            raise
    
    def _validate_gtin(self, gtin: str) -> Tuple[bool, List[str], List[str]]:
        """Validate GTIN format and check digit"""
        errors = []
        suggestions = []
        
        # Check length
        if len(gtin) not in [8, 12, 13, 14]:
            errors.append("GTIN must be 8, 12, 13, or 14 digits long")
            return False, errors, suggestions
        
        # Check digits only
        if not gtin.isdigit():
            errors.append("GTIN must contain only digits")
            return False, errors, suggestions
        
        # Validate check digit
        check_digit = self._calculate_gtin_check_digit(gtin[:-1])
        if check_digit != gtin[-1]:
            errors.append("Invalid check digit")
            suggestions.append(f"Correct check digit should be: {check_digit}")
            return False, errors, suggestions
        
        return True, errors, suggestions
    
    def _validate_gln(self, gln: str) -> Tuple[bool, List[str], List[str]]:
        """Validate GLN format"""
        errors = []
        suggestions = []
        
        if len(gln) != 13:
            errors.append("GLN must be exactly 13 digits")
            return False, errors, suggestions
        
        if not gln.isdigit():
            errors.append("GLN must contain only digits")
            return False, errors, suggestions
        
        # Validate check digit (same algorithm as GTIN)
        check_digit = self._calculate_gtin_check_digit(gln[:-1])
        if check_digit != gln[-1]:
            errors.append("Invalid check digit")
            suggestions.append(f"Correct check digit should be: {check_digit}")
            return False, errors, suggestions
        
        return True, errors, suggestions
    
    def _validate_gdti(self, gdti: str) -> Tuple[bool, List[str], List[str]]:
        """Validate GDTI format"""
        errors = []
        suggestions = []
        
        if len(gdti) < 14:
            errors.append("GDTI must be at least 14 characters")
            return False, errors, suggestions
        
        # Extract base part (first 13 digits)
        base_part = gdti[:13]
        if not base_part.isdigit():
            errors.append("GDTI base part must contain only digits")
            return False, errors, suggestions
        
        # Validate check digit
        check_digit = self._calculate_gtin_check_digit(base_part[:-1])
        if check_digit != base_part[-1]:
            errors.append("Invalid check digit")
            suggestions.append(f"Correct check digit should be: {check_digit}")
            return False, errors, suggestions
        
        return True, errors, suggestions
    
    def _validate_isrc(self, isrc: str) -> Tuple[bool, List[str], List[str]]:
        """Validate ISRC format"""
        errors = []
        suggestions = []
        
        # Remove hyphens for validation
        isrc_clean = isrc.replace("-", "")
        
        if len(isrc_clean) != 12:
            errors.append("ISRC must be 12 characters (CC-XXX-YY-NNNNN format)")
            return False, errors, suggestions
        
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{3}\d{2}\d{5}$', isrc_clean):
            errors.append("ISRC format must be CC-XXX-YY-NNNNN")
            suggestions.append("Country code (2 letters), Registrant (3 alphanumeric), Year (2 digits), Designation (5 digits)")
            return False, errors, suggestions
        
        return True, errors, suggestions
    
    def _validate_isan(self, isan: str) -> Tuple[bool, List[str], List[str]]:
        """Validate ISAN format"""
        errors = []
        suggestions = []
        
        if not re.match(r'^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]$', isan):
            errors.append("ISAN format must be XXXX-XXXX-XXXX-XXXX-X")
            suggestions.append("Use hexadecimal characters (0-9, A-F) with hyphens")
            return False, errors, suggestions
        
        return True, errors, suggestions
    
    # Analytics Methods
    
    async def get_analytics(self) -> AnalyticsData:
        """Get GS1 asset registry analytics"""
        try:
            # Count total assets
            total_assets = await self.assets_collection.count_documents({})
            
            # Count by asset type
            asset_pipeline = [
                {"$group": {"_id": "$asset_type", "count": {"$sum": 1}}}
            ]
            assets_by_type = {}
            async for result in self.assets_collection.aggregate(asset_pipeline):
                assets_by_type[result["_id"]] = result["count"]
            
            # Count identifiers by type
            identifier_pipeline = [
                {"$project": {"identifiers": {"$objectToArray": "$identifiers"}}},
                {"$unwind": "$identifiers"},
                {"$group": {"_id": "$identifiers.k", "count": {"$sum": 1}}}
            ]
            identifiers_by_type = {}
            async for result in self.assets_collection.aggregate(identifier_pipeline):
                identifiers_by_type[result["_id"]] = result["count"]
            
            # Count digital link scans (mock data for now)
            digital_link_scans = await self.digital_links_collection.count_documents({})
            
            # Get top performing assets (mock data)
            top_performing_assets = [
                {"asset_id": "sample1", "title": "Top Asset 1", "scans": 150},
                {"asset_id": "sample2", "title": "Top Asset 2", "scans": 120},
                {"asset_id": "sample3", "title": "Top Asset 3", "scans": 95}
            ]
            
            # Get recent activity
            recent_activity = []
            recent_assets = self.assets_collection.find({}).sort("created_at", -1).limit(5)
            async for asset in recent_assets:
                recent_activity.append({
                    "type": "asset_created",
                    "asset_id": asset["asset_id"],
                    "title": asset["metadata"]["title"],
                    "timestamp": asset["created_at"]
                })
            
            return AnalyticsData(
                total_assets=total_assets,
                assets_by_type=assets_by_type,
                identifiers_by_type=identifiers_by_type,
                digital_link_scans=digital_link_scans,
                top_performing_assets=top_performing_assets,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            raise
    
    async def _update_analytics(self, event_type: str, asset_type: AssetType = None):
        """Update analytics data"""
        try:
            analytics_doc = {
                "event_type": event_type,
                "asset_type": asset_type,
                "timestamp": datetime.now(timezone.utc)
            }
            await self.analytics_collection.insert_one(analytics_doc)
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    # Batch Operations
    
    async def batch_operation(self, request: BatchOperationRequest) -> BatchOperationResult:
        """Perform batch operations on assets"""
        try:
            start_time = datetime.now()
            results = []
            errors = []
            successful = 0
            failed = 0
            
            for i, asset_data in enumerate(request.assets):
                try:
                    if request.operation == "create":
                        create_req = CreateAssetRequest(**asset_data)
                        result = await self.create_asset(create_req)
                        results.append({"index": i, "asset_id": result.asset_id, "status": "success"})
                        successful += 1
                    elif request.operation == "update":
                        asset_id = asset_data.get("asset_id")
                        update_req = UpdateAssetRequest(**asset_data.get("update_data", {}))
                        result = await self.update_asset(asset_id, update_req)
                        if result:
                            results.append({"index": i, "asset_id": asset_id, "status": "success"})
                            successful += 1
                        else:
                            errors.append({"index": i, "error": "Asset not found or not updated"})
                            failed += 1
                    elif request.operation == "delete":
                        asset_id = asset_data.get("asset_id")
                        result = await self.delete_asset(asset_id)
                        if result:
                            results.append({"index": i, "asset_id": asset_id, "status": "deleted"})
                            successful += 1
                        else:
                            errors.append({"index": i, "error": "Asset not found or not deleted"})
                            failed += 1
                    
                except Exception as e:
                    errors.append({"index": i, "error": str(e)})
                    failed += 1
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return BatchOperationResult(
                total_processed=len(request.assets),
                successful=successful,
                failed=failed,
                errors=errors,
                results=results,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in batch operation: {e}")
            raise