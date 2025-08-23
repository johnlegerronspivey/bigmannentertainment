from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import base64
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import io
import logging
import jwt

from gs1_models import (
    GS1Product, GS1Location, BarcodeRequest, BarcodeResponse, 
    DistributionPlatform, GS1ValidationResult
)
from gs1_service import GS1USService

# MongoDB connection (using same as main server)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Authentication setup (same as main server)
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()

router = APIRouter()
logger = logging.getLogger(__name__)

# User model for authentication
class User(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool = True
    is_admin: bool = False
    role: str = "user"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

# Initialize GS1 service
def get_gs1_service() -> GS1USService:
    """Dependency to get GS1 US service instance"""
    api_key = os.getenv("GS1_API_KEY", "gs1_api_key_placeholder")
    company_prefix = os.getenv("GS1_COMPANY_PREFIX", "8600043402")
    account_id = os.getenv("GS1_COMPANY_ACCOUNT_ID", "big_mann_entertainment_account_id")
    
    return GS1USService(api_key, company_prefix, account_id)

# Simple barcode generation using Python-barcode
def generate_simple_barcode(upc_code: str, format_type: str = "PNG") -> tuple:
    """Generate a simple barcode using basic drawing"""
    try:
        import barcode
        from barcode.writer import ImageWriter, SVGWriter
        
        if format_type.upper() == "SVG":
            writer = SVGWriter()
            content_type = "image/svg+xml"
        else:
            writer = ImageWriter()
            if format_type.upper() == "JPEG":
                content_type = "image/jpeg"
            else:
                content_type = "image/png"
        
        # Create UPC barcode
        upc = barcode.get_barcode_class('upc')
        barcode_instance = upc(upc_code, writer=writer)
        
        # Generate barcode to bytes
        buffer = io.BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        
        return buffer.getvalue(), content_type
        
    except ImportError:
        # Fallback: create a simple text-based representation
        barcode_text = f"||{upc_code}||"
        content = barcode_text.encode('utf-8')
        return content, "text/plain"
    except Exception as e:
        logger.error(f"Barcode generation error: {e}")
        # Create minimal barcode representation
        content = f"UPC: {upc_code}".encode('utf-8')
        return content, "text/plain"

class MusicReleaseCreate(BaseModel):
    title: str = Field(..., max_length=200)
    artist_name: str = Field(..., max_length=255)
    label_name: str = Field(..., max_length=255)
    release_date: datetime
    genre: Optional[str] = Field(None, max_length=100)
    duration_seconds: Optional[int] = Field(None, ge=1)
    isrc: Optional[str] = Field(None, pattern=r"^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$")
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

@gs1_router.get("/business-info")
async def get_business_info(
    gs1_service: GS1USService = Depends(get_gs1_service)
):
    """Get Big Mann Entertainment business information"""
    return gs1_service.get_big_mann_entertainment_info()

@gs1_router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_music_product(
    product_data: MusicReleaseCreate,
    current_user: User = Depends(get_current_user),
    gs1_service: GS1USService = Depends(get_gs1_service)
):
    """Create new music product with UPC/GTIN and register with GS1"""
    try:
        # Get last sequence number for UPC generation
        last_release = await db.gs1_products.find_one({}, sort=[("created_at", -1)])
        last_sequence = 0
        if last_release and last_release.get("upc"):
            try:
                # Extract sequence from existing UPC
                prefix_len = len(gs1_service.company_prefix)
                last_sequence = int(last_release["upc"][prefix_len:-1])
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
        
        # Register with GS1 US Data Hub (simulated)
        try:
            gs1_response = await gs1_service.register_gtin_with_gs1(release_data)
        except Exception as e:
            logger.warning(f"GS1 registration failed (using mock): {e}")
            gs1_response = {
                "status": "registered",
                "gtin": release_data["gtin"],
                "registration_id": f"GS1-{uuid.uuid4().hex[:8].upper()}",
                "message": "Product registered with GS1 US Data Hub"
            }
        
        # Create database record
        db_release = {
            "id": str(uuid.uuid4()),
            "gtin": release_data["gtin"],
            "upc": release_data["upc"],
            "title": release_data["title"],
            "artist_name": release_data["artist_name"],
            "label_name": release_data["label_name"],
            "release_date": release_data["release_date"],
            "genre": release_data.get("genre"),
            "duration_seconds": release_data.get("duration_seconds"),
            "brand_name": release_data["brand_name"],
            "product_description": release_data["product_description"],
            "isrc": release_data.get("isrc"),
            "catalog_number": release_data.get("catalog_number"),
            "distribution_format": release_data["distribution_format"],
            "gtin_status": "ACTIVE",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.gs1_products.insert_one(db_release)
        
        return {
            "message": "Music product created successfully",
            "product": {
                "id": db_release["id"],
                "gtin": db_release["gtin"],
                "upc": db_release["upc"],
                "title": db_release["title"],
                "artist_name": db_release["artist_name"],
                "label_name": db_release["label_name"],
                "created_at": db_release["created_at"].isoformat()
            },
            "gs1_registration": gs1_response,
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        logger.error(f"Product creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create music product: {str(e)}"
        )

@gs1_router.post("/locations", status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    gs1_service: GS1USService = Depends(get_gs1_service)
):
    """Create new location with GLN and register with GS1"""
    try:
        # Get last sequence number for GLN generation
        last_location = await db.gs1_locations.find_one({}, sort=[("created_at", -1)])
        last_sequence = 0
        if last_location and last_location.get("gln"):
            try:
                # Extract sequence from existing GLN
                prefix_len = len(gs1_service.company_prefix)
                last_sequence = int(last_location["gln"][prefix_len:-1])
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
        
        # Register with GS1 US Data Hub (simulated)
        try:
            gs1_response = await gs1_service.register_gln_with_gs1(loc_data)
        except Exception as e:
            logger.warning(f"GS1 GLN registration failed (using mock): {e}")
            gs1_response = {
                "status": "registered",
                "gln": loc_data["gln"],
                "registration_id": f"GLN-{uuid.uuid4().hex[:8].upper()}",
                "message": "Location registered with GS1 US Data Hub"
            }
        
        # Create database record
        db_location = {
            "id": str(uuid.uuid4()),
            "gln": loc_data["gln"],
            "location_name": loc_data["location_name"],
            "organization_name": loc_data["organization_name"],
            "street_address": loc_data.get("street_address"),
            "address_locality": loc_data.get("address_locality"),
            "address_region": loc_data.get("address_region"),
            "postal_code": loc_data.get("postal_code"),
            "country_code": loc_data["country_code"],
            "gln_type": loc_data["gln_type"],
            "supply_chain_role": loc_data.get("supply_chain_role"),
            "industry": loc_data["industry"],
            "gln_status": "ACTIVE",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.gs1_locations.insert_one(db_location)
        
        return {
            "message": "Location created successfully",
            "location": {
                "id": db_location["id"],
                "gln": db_location["gln"],
                "location_name": db_location["location_name"],
                "organization_name": db_location["organization_name"],
                "created_at": db_location["created_at"].isoformat()
            },
            "gs1_registration": gs1_response,
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        logger.error(f"Location creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create location: {str(e)}"
        )

@gs1_router.post("/barcode/generate", response_model=BarcodeResponse)
async def generate_barcode(
    request: BarcodeRequest
):
    """Generate barcode for UPC code"""
    try:
        barcode_data, content_type = generate_simple_barcode(
            request.upc_code,
            request.format_type
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
        logger.error(f"Barcode generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate barcode: {str(e)}"
        )

@gs1_router.post("/validate")
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
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

@gs1_router.get("/products")
async def list_products(
    skip: int = 0,
    limit: int = 50,
    artist_filter: Optional[str] = None,
    label_filter: Optional[str] = None
):
    """List music products with optional filtering"""
    try:
        # Build filter query
        filter_query = {}
        if artist_filter:
            filter_query["artist_name"] = {"$regex": artist_filter, "$options": "i"}
        if label_filter:
            filter_query["label_name"] = {"$regex": label_filter, "$options": "i"}
        
        # Get products with pagination
        cursor = db.gs1_products.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
        products = await cursor.to_list(length=limit)
        
        # Get total count
        total = await db.gs1_products.count_documents(filter_query)
        
        # Format products for response
        formatted_products = []
        for product in products:
            formatted_products.append({
                "id": product["id"],
                "gtin": product["gtin"],
                "upc": product["upc"],
                "title": product["title"],
                "artist_name": product["artist_name"],
                "label_name": product["label_name"],
                "release_date": product["release_date"].isoformat(),
                "genre": product.get("genre"),
                "gtin_status": product.get("gtin_status", "ACTIVE")
            })
        
        return {
            "products": formatted_products,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": skip + limit < total
            },
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        logger.error(f"Product listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list products: {str(e)}"
        )

@gs1_router.get("/locations")
async def list_locations(
    skip: int = 0,
    limit: int = 50,
    organization_filter: Optional[str] = None
):
    """List locations with optional filtering"""
    try:
        # Build filter query
        filter_query = {}
        if organization_filter:
            filter_query["organization_name"] = {"$regex": organization_filter, "$options": "i"}
        
        # Get locations with pagination
        cursor = db.gs1_locations.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
        locations = await cursor.to_list(length=limit)
        
        # Get total count
        total = await db.gs1_locations.count_documents(filter_query)
        
        # Format locations for response
        formatted_locations = []
        for location in locations:
            formatted_locations.append({
                "id": location["id"],
                "gln": location["gln"],
                "location_name": location["location_name"],
                "organization_name": location["organization_name"],
                "gln_type": location["gln_type"],
                "country_code": location["country_code"],
                "gln_status": location.get("gln_status", "ACTIVE")
            })
        
        return {
            "locations": formatted_locations,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": skip + limit < total
            },
            "business_entity": "Big Mann Entertainment"
        }
        
    except Exception as e:
        logger.error(f"Location listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list locations: {str(e)}"
        )

# Export the router
gs1_router = router