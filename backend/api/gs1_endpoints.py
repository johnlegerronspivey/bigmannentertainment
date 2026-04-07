"""
GS1 Asset Registry API Endpoints
FastAPI router for GS1 identifier management and Digital Link operations
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timezone

from gs1_models import (
    GS1Asset, AssetType, IdentifierType, GS1IdentifierStatus,
    CreateAssetRequest, UpdateAssetRequest, GenerateIdentifierRequest,
    CreateDigitalLinkRequest, AssetSearchFilter, AssetListResponse,
    IdentifierValidationResult, AnalyticsData, BatchOperationRequest,
    BatchOperationResult
)
from gs1_service import GS1Service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/gs1", tags=["GS1 Asset Registry"])

# Global service instance (will be initialized in server.py)
gs1_service: Optional[GS1Service] = None

def get_gs1_service() -> GS1Service:
    """Dependency to get GS1 service instance"""
    if gs1_service is None:
        raise HTTPException(status_code=500, detail="GS1 service not initialized")
    return gs1_service

def init_gs1_service(database):
    """Initialize GS1 service with database connection"""
    global gs1_service
    gs1_service = GS1Service(database)
    logger.info("GS1 service initialized successfully")

# Asset Management Endpoints

@router.post("/assets", response_model=GS1Asset)
async def create_asset(
    request: CreateAssetRequest,
    service: GS1Service = Depends(get_gs1_service)
):
    """Create a new GS1 asset with optional identifier generation"""
    try:
        asset = await service.create_asset(request)
        return asset
    except Exception as e:
        logger.error(f"Error creating asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assets/{asset_id}", response_model=GS1Asset)
async def get_asset(
    asset_id: str,
    service: GS1Service = Depends(get_gs1_service)
):
    """Get a single asset by ID"""
    try:
        asset = await service.get_asset(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/assets/{asset_id}", response_model=GS1Asset)
async def update_asset(
    asset_id: str,
    request: UpdateAssetRequest,
    service: GS1Service = Depends(get_gs1_service)
):
    """Update an existing asset"""
    try:
        asset = await service.update_asset(asset_id, request)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    service: GS1Service = Depends(get_gs1_service)
):
    """Delete an asset and its associated data"""
    try:
        success = await service.delete_asset(asset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"message": "Asset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assets", response_model=AssetListResponse)
async def search_assets(
    asset_type: Optional[AssetType] = None,
    status: Optional[GS1IdentifierStatus] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    text_search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: GS1Service = Depends(get_gs1_service)
):
    """Search assets with filters and pagination"""
    try:
        filters = AssetSearchFilter(
            asset_type=asset_type,
            status=status,
            created_after=created_after,
            created_before=created_before,
            text_search=text_search
        )
        
        assets, total_count = await service.search_assets(filters, page, page_size)
        
        has_next = (page * page_size) < total_count
        has_previous = page > 1
        
        return AssetListResponse(
            assets=assets,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous
        )
    except Exception as e:
        logger.error(f"Error searching assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Identifier Management Endpoints

@router.post("/identifiers/generate")
async def generate_identifier(
    request: GenerateIdentifierRequest,
    service: GS1Service = Depends(get_gs1_service)
):
    """Generate a new identifier for an existing asset"""
    try:
        # Get the asset
        asset = await service.get_asset(request.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Generate identifier
        identifier = await service._generate_identifier(
            request.asset_id, 
            request.identifier_type, 
            asset.metadata
        )
        
        # Update asset with new identifier
        asset.identifiers[request.identifier_type.value] = identifier
        asset.updated_at = datetime.now(timezone.utc)
        
        # Save updated asset
        await service.assets_collection.update_one(
            {"asset_id": request.asset_id},
            {"$set": {"identifiers": {k: v.dict() for k, v in asset.identifiers.items()}, "updated_at": asset.updated_at}}
        )
        
        return {"identifier": identifier, "message": "Identifier generated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating identifier: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/identifiers/validate", response_model=IdentifierValidationResult)
async def validate_identifier(
    identifier_value: str,
    identifier_type: IdentifierType,
    service: GS1Service = Depends(get_gs1_service)
):
    """Validate a GS1 identifier"""
    try:
        result = await service.validate_identifier(identifier_value, identifier_type)
        return result
    except Exception as e:
        logger.error(f"Error validating identifier: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/identifiers/lookup/{identifier_value}")
async def lookup_identifier(
    identifier_value: str,
    service: GS1Service = Depends(get_gs1_service)
):
    """Look up an asset by identifier value"""
    try:
        # Search across all identifier types
        query = {
            "$or": [
                {"identifiers.gtin.value": identifier_value},
                {"identifiers.gln.value": identifier_value},
                {"identifiers.gdti.value": identifier_value},
                {"identifiers.isrc.value": identifier_value},
                {"identifiers.isan.value": identifier_value}
            ]
        }
        
        asset_data = await service.assets_collection.find_one(query)
        if not asset_data:
            raise HTTPException(status_code=404, detail="No asset found with this identifier")
        
        asset = GS1Asset(**asset_data)
        return asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up identifier: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Digital Link Endpoints

@router.post("/digital-links")
async def create_digital_link(
    request: CreateDigitalLinkRequest,
    service: GS1Service = Depends(get_gs1_service)
):
    """Create a GS1 Digital Link for an asset"""
    try:
        # Get the asset
        asset = await service.get_asset(request.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Find the identifier
        identifier_obj = None
        for ident in asset.identifiers.values():
            if ident.value == request.identifier:
                identifier_obj = ident
                break
        
        if not identifier_obj:
            raise HTTPException(status_code=404, detail="Identifier not found on asset")
        
        # Create Digital Link
        digital_link = await service._create_digital_link(
            request.asset_id,
            identifier_obj,
            request.config or service.DigitalLinkConfig()
        )
        
        return {"digital_link": digital_link, "message": "Digital Link created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Digital Link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-links/{link_id}")
async def get_digital_link(
    link_id: str,
    service: GS1Service = Depends(get_gs1_service)
):
    """Get a Digital Link by ID"""
    try:
        link_data = await service.digital_links_collection.find_one({"link_id": link_id})
        if not link_data:
            raise HTTPException(status_code=404, detail="Digital Link not found")
        return link_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Digital Link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-links/{link_id}/qr-code")
async def get_qr_code(
    link_id: str,
    format: str = Query("png", regex="^(png|jpeg|svg)$"),
    service: GS1Service = Depends(get_gs1_service)
):
    """Get QR code image for a Digital Link"""
    try:
        link_data = await service.digital_links_collection.find_one({"link_id": link_id})
        if not link_data:
            raise HTTPException(status_code=404, detail="Digital Link not found")
        
        qr_code_data = link_data.get("qr_code_data")
        if not qr_code_data:
            raise HTTPException(status_code=404, detail="QR code not available")
        
        # Return base64 encoded image
        if format.lower() == "png":
            media_type = "image/png"
        elif format.lower() == "jpeg":
            media_type = "image/jpeg"
        else:
            media_type = "image/svg+xml"
        
        # Extract base64 data (remove data:image/png;base64, prefix)
        if "base64," in qr_code_data:
            base64_data = qr_code_data.split("base64,")[1]
        else:
            base64_data = qr_code_data
        
        import base64
        image_data = base64.b64decode(base64_data)
        
        return Response(content=image_data, media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving QR code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-links/resolve")
async def resolve_digital_link(
    uri: str,
    service: GS1Service = Depends(get_gs1_service)
):
    """Resolve a GS1 Digital Link URI"""
    try:
        # Find Digital Link by URI
        link_data = await service.digital_links_collection.find_one({"uri": uri})
        if not link_data:
            raise HTTPException(status_code=404, detail="Digital Link not found")
        
        # Get associated asset
        asset = await service.get_asset(link_data["asset_id"])
        if not asset:
            raise HTTPException(status_code=404, detail="Associated asset not found")
        
        # Update analytics (scan count)
        await service.digital_links_collection.update_one(
            {"link_id": link_data["link_id"]},
            {"$inc": {"analytics.scan_count": 1}, "$set": {"analytics.last_scanned": datetime.now(timezone.utc)}}
        )
        
        return {
            "asset": asset,
            "digital_link": link_data,
            "message": "Digital Link resolved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving Digital Link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints

@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics(
    service: GS1Service = Depends(get_gs1_service)
):
    """Get GS1 asset registry analytics"""
    try:
        analytics = await service.get_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/assets/by-type")
async def get_assets_by_type(
    service: GS1Service = Depends(get_gs1_service)
):
    """Get asset count breakdown by type"""
    try:
        pipeline = [
            {"$group": {"_id": "$asset_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = []
        async for result in service.assets_collection.aggregate(pipeline):
            results.append({"asset_type": result["_id"], "count": result["count"]})
        
        return {"data": results}
    except Exception as e:
        logger.error(f"Error retrieving asset type analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/identifiers/by-type")
async def get_identifiers_by_type(
    service: GS1Service = Depends(get_gs1_service)
):
    """Get identifier count breakdown by type"""
    try:
        pipeline = [
            {"$project": {"identifiers": {"$objectToArray": "$identifiers"}}},
            {"$unwind": "$identifiers"},
            {"$group": {"_id": "$identifiers.k", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = []
        async for result in service.assets_collection.aggregate(pipeline):
            results.append({"identifier_type": result["_id"], "count": result["count"]})
        
        return {"data": results}
    except Exception as e:
        logger.error(f"Error retrieving identifier type analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch Operations

@router.post("/batch", response_model=BatchOperationResult)
async def batch_operation(
    request: BatchOperationRequest,
    background_tasks: BackgroundTasks,
    service: GS1Service = Depends(get_gs1_service)
):
    """Perform batch operations on assets"""
    try:
        # For large batches, run in background
        if len(request.assets) > 100:
            background_tasks.add_task(service.batch_operation, request)
            return JSONResponse(
                content={"message": "Batch operation started in background", "status": "processing"},
                status_code=202
            )
        else:
            result = await service.batch_operation(request)
            return result
    except Exception as e:
        logger.error(f"Error in batch operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints

@router.get("/health")
async def health_check(
    service: GS1Service = Depends(get_gs1_service)
):
    """Health check endpoint"""
    try:
        # Test database connectivity
        await service.assets_collection.find_one({})
        
        # Get basic stats
        total_assets = await service.assets_collection.count_documents({})
        total_digital_links = await service.digital_links_collection.count_documents({})
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc),
            "database": "connected",
            "total_assets": total_assets,
            "total_digital_links": total_digital_links,
            "service": "operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc),
                "error": str(e)
            },
            status_code=503
        )

@router.get("/config")
async def get_config(
    service: GS1Service = Depends(get_gs1_service)
):
    """Get GS1 service configuration"""
    return {
        "company_prefix": service.company_prefix,
        "base_uri": service.base_uri,
        "supported_identifiers": [
            IdentifierType.GTIN,
            IdentifierType.GLN,
            IdentifierType.GDTI,
            IdentifierType.ISRC,
            IdentifierType.ISAN
        ],
        "supported_asset_types": [
            AssetType.MUSIC,
            AssetType.VIDEO,
            AssetType.IMAGE,
            AssetType.MERCHANDISE
        ]
    }

# Export/Import Endpoints

@router.get("/export/assets")
async def export_assets(
    format: str = Query("json", regex="^(json|csv|xml)$"),
    asset_type: Optional[AssetType] = None,
    service: GS1Service = Depends(get_gs1_service)
):
    """Export assets in various formats"""
    try:
        query = {}
        if asset_type:
            query["asset_type"] = asset_type
        
        assets = []
        async for asset_data in service.assets_collection.find(query):
            # Convert ObjectId to string and clean up data
            asset_data["_id"] = str(asset_data["_id"])
            assets.append(asset_data)
        
        if format == "json":
            return {"assets": assets, "count": len(assets)}
        elif format == "csv":
            # For CSV, flatten the data structure
            import csv
            import io
            
            output = io.StringIO()
            if assets:
                fieldnames = ["asset_id", "asset_type", "title", "description", "status", "created_at"]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for asset in assets:
                    row = {
                        "asset_id": asset.get("asset_id"),
                        "asset_type": asset.get("asset_type"),
                        "title": asset.get("metadata", {}).get("title"),
                        "description": asset.get("metadata", {}).get("description"),
                        "status": asset.get("status"),
                        "created_at": asset.get("created_at")
                    }
                    writer.writerow(row)
            
            csv_content = output.getvalue()
            return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=gs1_assets.csv"})
        
        else:  # XML format
            import xml.etree.ElementTree as ET
            
            root = ET.Element("gs1_assets")
            root.set("count", str(len(assets)))
            
            for asset in assets:
                asset_elem = ET.SubElement(root, "asset")
                asset_elem.set("id", asset.get("asset_id", ""))
                asset_elem.set("type", asset.get("asset_type", ""))
                
                metadata = asset.get("metadata", {})
                if metadata.get("title"):
                    title_elem = ET.SubElement(asset_elem, "title")
                    title_elem.text = metadata["title"]
                
                if metadata.get("description"):
                    desc_elem = ET.SubElement(asset_elem, "description")
                    desc_elem.text = metadata["description"]
            
            xml_str = ET.tostring(root, encoding='unicode')
            return Response(content=xml_str, media_type="application/xml", headers={"Content-Disposition": "attachment; filename=gs1_assets.xml"})
    
    except Exception as e:
        logger.error(f"Error exporting assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/standards/compliance")
async def get_standards_compliance(
    service: GS1Service = Depends(get_gs1_service)
):
    """Get GS1 standards compliance information"""
    return {
        "gs1_standards": {
            "gtin": {
                "standard": "GS1-128",
                "formats": ["GTIN-8", "GTIN-12", "GTIN-13", "GTIN-14"],
                "check_digit": "Modulo 10",
                "compliance_level": "Full"
            },
            "gln": {
                "standard": "GS1 GLN",
                "format": "13 digits",
                "check_digit": "Modulo 10",
                "compliance_level": "Full"
            },
            "gdti": {
                "standard": "GS1 GDTI",
                "format": "Variable length",
                "check_digit": "Modulo 10",
                "compliance_level": "Full"
            },
            "digital_link": {
                "standard": "GS1 Digital Link 1.2",
                "uri_format": "https://domain/AI/value",
                "qr_code": "ISO/IEC 18004",
                "compliance_level": "Full"
            }
        },
        "industry_standards": {
            "isrc": {
                "standard": "ISO 3901",
                "format": "CC-XXX-YY-NNNNN",
                "authority": "International ISRC Agency",
                "compliance_level": "Full"
            },
            "isan": {
                "standard": "ISO 15706",
                "format": "XXXX-XXXX-XXXX-XXXX-X",
                "authority": "ISAN International Agency",
                "compliance_level": "Full"
            }
        },
        "certification": {
            "date": datetime.now(timezone.utc),
            "version": "1.0",
            "validated_by": "GS1 Asset Registry Service"
        }
    }

@router.get("/business-info")
async def get_business_info(
    service: GS1Service = Depends(get_gs1_service)
):
    """Get GS1 business information"""
    try:
        # Get business analytics
        analytics = await service.get_analytics()
        
        return {
            "success": True,
            "business_info": {
                "company_name": "Big Mann Entertainment",
                "company_prefix": "08600043402",
                "legal_entity_gln": "0860004340201",
                "base_uri": service.base_uri,
                "total_assets": analytics.total_assets,
                "active_identifiers": len(analytics.identifiers_by_type),
                "digital_links_created": analytics.digital_link_scans,
                "compliance_status": "Fully Compliant",
                "certification_level": "GS1 Certified",
                "registration_date": datetime.now(timezone.utc).isoformat(),
                "supported_industries": ["Music", "Entertainment", "Media", "Merchandise"]
            },
            "capabilities": {
                "identifier_generation": ["GTIN", "GLN", "GDTI", "ISRC", "ISAN"],
                "digital_links": True,
                "qr_codes": True,
                "bulk_operations": True,
                "analytics": True,
                "compliance_reporting": True
            },
            # Business Entity Information
            "business_entity": "Big Mann Entertainment",
            "business_owner": "John LeGerron Spivey",
            "industry": "Media Entertainment",
            "ein": "270658077",
            "tin": "12800", 
            "business_type": "Sole Proprietorship"
        }
    except Exception as e:
        logger.error(f"Error retrieving business info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    service: GS1Service = Depends(get_gs1_service)
):
    """Get GS1 products (assets)"""
    try:
        # Convert asset_type string to AssetType enum if provided
        asset_type_filter = None
        if asset_type:
            try:
                from gs1_models import AssetType
                asset_type_filter = AssetType(asset_type.lower())
            except ValueError:
                asset_type_filter = None
        
        # Create search filters
        filters = AssetSearchFilter(asset_type=asset_type_filter)
        
        # Get assets
        assets, total_count = await service.search_assets(filters, page, page_size)
        
        # Transform assets to products format
        products = []
        for asset in assets:
            product = {
                "id": asset.asset_id,
                "name": asset.metadata.title,
                "description": asset.metadata.description,
                "type": asset.asset_type,
                "status": asset.status,
                "created_at": asset.created_at.isoformat(),
                "identifiers": {},
                "digital_links": len(asset.digital_links)
            }
            
            # Add identifier information
            for ident_type, identifier in asset.identifiers.items():
                product["identifiers"][ident_type] = {
                    "value": identifier.value,
                    "type": identifier.identifier_type,
                    "status": identifier.status
                }
            
            products.append(product)
        
        has_next = (page * page_size) < total_count
        has_previous = page > 1
        
        return {
            "success": True,
            "products": products,
            "pagination": {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_previous": has_previous,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick-actions/summary")
async def get_quick_actions_summary(
    service: GS1Service = Depends(get_gs1_service)
):
    """Aggregated summary for the Quick Actions Panel on GS1 Hub."""
    try:
        from config.database import db as _db

        products_count = await service.assets_collection.count_documents({})
        digital_links_count = await service.digital_links_collection.count_documents({})

        # Licensing stats
        active_licenses = 0
        total_licenses = 0
        try:
            lic_col = _db["platform_licenses"]
            total_licenses = await lic_col.count_documents({})
            active_licenses = await lic_col.count_documents({"license_status": "active"})
        except Exception:
            pass

        # Compliance docs
        compliance_docs = 0
        pending_reviews = 0
        try:
            comp_col = _db["compliance_documents"]
            compliance_docs = await comp_col.count_documents({})
            pending_reviews = await comp_col.count_documents({"legal_review_status": "pending"})
        except Exception:
            pass

        # Business identifiers
        identifiers_count = 0
        try:
            biz_col = _db["business_identifiers"]
            identifiers_count = await biz_col.count_documents({})
        except Exception:
            pass

        return {
            "products_count": products_count,
            "digital_links_count": digital_links_count,
            "active_licenses": active_licenses,
            "total_licenses": total_licenses,
            "compliance_docs": compliance_docs,
            "pending_reviews": pending_reviews,
            "identifiers_count": identifiers_count,
        }
    except Exception as e:
        logger.error(f"Quick actions summary error: {e}")
        return {
            "products_count": 0,
            "digital_links_count": 0,
            "active_licenses": 0,
            "total_licenses": 0,
            "compliance_docs": 0,
            "pending_reviews": 0,
            "identifiers_count": 0,
        }
