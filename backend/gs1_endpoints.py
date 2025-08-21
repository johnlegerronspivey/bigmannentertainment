from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import base64
import os

from app.database import get_db
from app.models.products import MusicRelease
from app.models.locations import Location
from gs1_models import (
    GS1Product, GS1Location, BarcodeRequest, BarcodeResponse, 
    DistributionPlatform, GS1ValidationResult
)
from gs1_service import GS1USService
from app.services.barcode_service import BarcodeService

router = APIRouter()

# Initialize GS1 service
def get_gs1_service() -> GS1USService:
    """Dependency to get GS1 US service instance"""
    api_key = os.getenv("GS1_API_KEY")
    company_prefix = os.getenv("GS1_COMPANY_PREFIX")
    account_id = os.getenv("GS1_COMPANY_ACCOUNT_ID")
    
    if not all([api_key, company_prefix, account_id]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GS1 US configuration not properly set"
        )
    
    return GS1USService(api_key, company_prefix, account_id)

def get_barcode_service() -> BarcodeService:
    """Dependency to get barcode service instance"""
    return BarcodeService()

class MusicReleaseCreate(BaseModel):
    title: str = Field(..., max_length=200)
    artist_name: str = Field(..., max_length=255)
    label_name: str = Field(..., max_length=255)
    release_date: datetime
    genre: Optional[str] = Field(None, max_length=100)
    duration_seconds: Optional[int] = Field(None, ge=1)
    isrc: Optional[str] = Field(None, regex=r"^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$")
    catalog_number: Optional[str] = Field(None, max_length=50)
    distribution_format: str = Field("Digital", max_length=50)

class LocationCreate(BaseModel):
    location_name: str = Field(..., max_length=255)
    organization_name: str = Field(..., max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    street_address: Optional[str] = Field(None, max_length=255)
    address_locality: Optional[str] = Field(None, max_length=100)
    address_region: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country_code: str = Field("US", max_length=2)
    gln_type: str = Field("Legal Entity", max_length=50)
    supply_chain_role: Optional[str] = Field(None, max_length=100)
    industry: str = Field("Entertainment", max_length=100)

@router.get("/business-info")
async def get_business_info(
    gs1_service: GS1USService = Depends(get_gs1_service)
):
    """Get Big Mann Entertainment business information"""
    return gs1_service.get_big_mann_entertainment_info()

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_music_product(
    product_data: MusicReleaseCreate,
    db: Session = Depends(get_db),
    gs1_service: GS1USService = Depends(get_gs1_service)
):
    """Create new music product with UPC/GTIN and register with GS1"""
    try:
        # Get last sequence number for UPC generation
        last_release = db.query(MusicRelease).order_by(MusicRelease.id.desc()).first()
        last_sequence = 0
        if last_release and last_release.upc:
            try:
                # Extract sequence from existing UPC
                prefix_len = len(gs1_service.company_prefix)
                last_sequence = int(last_release.upc[prefix_len:-1])
            except (ValueError, IndexError):
                last_sequence = 0
        
        # Create release data
        release_data = gs1_service.create_music_release_data(
            title=product_data.title,
            artist_name=product_data.artist_name,
            label_name=product_data.label_name,
            release_date=product_data.release_date,
            genre=product_data.genre,
            duration_seconds=product_data.duration_seconds,
            isrc=product_data.isrc,
            catalog_number=product_data.catalog_number,
            distribution_format=product_data.distribution_format,
            last_sequence=last_sequence
        )
        
        # Register with GS1 US Data Hub
        gs1_response = await gs1_service.register_gtin_with_gs1(release_data)
        
        # Create database record
        db_release = MusicRelease(
            gtin=release_data["gtin"],
            upc=release_data["upc"],
            title=release_data["title"],
            artist_name=release_data["artist_name"],
            label_name=release_data["label_name"],
            release_date=release_data["release_date"],
            genre=release_data.get("genre"),
            duration_seconds=release_data.get("duration_seconds"),
            brand_name=release_data["brand_name"],
            product_description=release_data["product_description"],
            isrc=release_data.get("isrc"),
            catalog_number=release_data.get("catalog_number"),
            distribution_format=release_data["distribution_format"]
        )
        
        db.add(db_release)
        db.commit()
        db.refresh(db_release)
        
        return {
            "message": "Music product created successfully",
            "product": {
                "id": db_release.id,
                "gtin": db_release.gtin,
                "upc": db_release.upc,
                "title": db_release.title,
                "artist_name": db_release.artist_name,
                "label_name": db_release.label_name,
                "created_at": db_release.created_at.isoformat()
            },
            "gs1_registration": gs1_response,
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create music product: {str(e)}"
        )

@router.post("/locations", status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    db: Session = Depends(get_db),
    gs1_service: GS1USService = Depends(get_gs1_service)
):
    """Create new location with GLN and register with GS1"""
    try:
        # Get last sequence number for GLN generation
        last_location = db.query(Location).order_by(Location.id.desc()).first()
        last_sequence = 0
        if last_location and last_location.gln:
            try:
                # Extract sequence from existing GLN
                prefix_len = len(gs1_service.company_prefix)
                last_sequence = int(last_location.gln[prefix_len:-1])
            except (ValueError, IndexError):
                last_sequence = 0
        
        # Create location data
        loc_data = gs1_service.create_location_data(
            location_name=location_data.location_name,
            organization_name=location_data.organization_name,
            gln_type=location_data.gln_type,
            street_address=location_data.street_address,
            address_locality=location_data.address_locality,
            address_region=location_data.address_region,
            postal_code=location_data.postal_code,
            country_code=location_data.country_code,
            supply_chain_role=location_data.supply_chain_role,
            industry=location_data.industry,
            last_sequence=last_sequence
        )
        
        # Register with GS1 US Data Hub
        gs1_response = await gs1_service.register_gln_with_gs1(loc_data)
        
        # Create database record
        db_location = Location(
            gln=loc_data["gln"],
            location_name=loc_data["location_name"],
            organization_name=loc_data["organization_name"],
            street_address=loc_data.get("street_address"),
            address_locality=loc_data.get("address_locality"),
            address_region=loc_data.get("address_region"),
            postal_code=loc_data.get("postal_code"),
            country_code=loc_data["country_code"],
            gln_type=loc_data["gln_type"],
            supply_chain_role=loc_data.get("supply_chain_role"),
            industry=loc_data["industry"]
        )
        
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        
        return {
            "message": "Location created successfully",
            "location": {
                "id": db_location.id,
                "gln": db_location.gln,
                "location_name": db_location.location_name,
                "organization_name": db_location.organization_name,
                "created_at": db_location.created_at.isoformat()
            },
            "gs1_registration": gs1_response,
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create location: {str(e)}"
        )

@router.post("/barcode/generate", response_model=BarcodeResponse)
async def generate_barcode(
    request: BarcodeRequest,
    barcode_service: BarcodeService = Depends(get_barcode_service)
):
    """Generate barcode for UPC code"""
    try:
        options = {}
        if request.width:
            options['module_width'] = request.width
        if request.height:
            options['module_height'] = request.height
        if request.dpi:
            options['dpi'] = request.dpi
        
        barcode_data, content_type = barcode_service.generate_upc_barcode(
            request.upc_code,
            request.format_type,
            options if options else None
        )
        
        encoded_data = base64.b64encode(barcode_data).decode('utf-8')
        
        return BarcodeResponse(
            upc_code=request.upc_code,
            format_type=request.format_type,
            content_type=content_type,
            data=encoded_data,
            size_bytes=len(barcode_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate barcode: {str(e)}"
        )

@router.post("/validate")
async def validate_identifier(
    identifier: str,
    identifier_type: str,
    gs1_service: GS1USService = Depends(get_gs1_service)
):
    """Validate UPC, GTIN, or GLN identifier"""
    try:
        if identifier_type.upper() == "UPC":
            if len(identifier) != 12:
                return GS1ValidationResult(
                    is_valid=False,
                    identifier=identifier,
                    identifier_type="UPC",
                    validation_message="UPC must be exactly 12 digits",
                    format_valid=False
                )
        elif identifier_type.upper() in ["GTIN", "GLN"]:
            if len(identifier) != 13:
                return GS1ValidationResult(
                    is_valid=False,
                    identifier=identifier,
                    identifier_type=identifier_type.upper(),
                    validation_message=f"{identifier_type.upper()} must be exactly 13 digits",
                    format_valid=False
                )
        
        # Validate format
        format_valid = identifier.isdigit()
        check_digit_valid = gs1_service.validate_check_digit(identifier)
        
        is_valid = format_valid and check_digit_valid
        
        validation_message = "Valid identifier"
        if not format_valid:
            validation_message = f"Invalid format: {identifier_type.upper()} must contain only digits"
        elif not check_digit_valid:
            validation_message = "Invalid check digit"
        
        return GS1ValidationResult(
            is_valid=is_valid,
            identifier=identifier,
            identifier_type=identifier_type.upper(),
            validation_message=validation_message,
            check_digit_valid=check_digit_valid,
            format_valid=format_valid
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

@router.get("/products")
async def list_products(
    skip: int = 0,
    limit: int = 50,
    artist_filter: Optional[str] = None,
    label_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List music products with optional filtering"""
    query = db.query(MusicRelease)
    
    if artist_filter:
        query = query.filter(MusicRelease.artist_name.ilike(f"%{artist_filter}%"))
    
    if label_filter:
        query = query.filter(MusicRelease.label_name.ilike(f"%{label_filter}%"))
    
    releases = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "products": [
            {
                "id": release.id,
                "gtin": release.gtin,
                "upc": release.upc,
                "title": release.title,
                "artist_name": release.artist_name,
                "label_name": release.label_name,
                "release_date": release.release_date.isoformat(),
                "genre": release.genre,
                "gtin_status": release.gtin_status
            }
            for release in releases
        ],
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "has_more": skip + limit < total
        },
        "business_entity": "Big Mann Entertainment"
    }

@router.get("/locations")
async def list_locations(
    skip: int = 0,
    limit: int = 50,
    organization_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List locations with optional filtering"""
    query = db.query(Location)
    
    if organization_filter:
        query = query.filter(Location.organization_name.ilike(f"%{organization_filter}%"))
    
    locations = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "locations": [
            {
                "id": location.id,
                "gln": location.gln,
                "location_name": location.location_name,
                "organization_name": location.organization_name,
                "gln_type": location.gln_type,
                "country_code": location.country_code,
                "gln_status": location.gln_status
            }
            for location in locations
        ],
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "has_more": skip + limit < total
        },
        "business_entity": "Big Mann Entertainment"
    }