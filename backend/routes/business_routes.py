"""Business identifiers endpoints - UPC, ISRC, GLN generation."""
import uuid
import hashlib
import random
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from config.database import db
from config.settings import settings
from auth.service import get_current_user
from models.core import User, ProductIdentifier, BusinessIdentifiers

router = APIRouter(tags=["Business"])

UPC_COMPANY_PREFIX = settings.UPC_COMPANY_PREFIX
GLOBAL_LOCATION_NUMBER = settings.GLOBAL_LOCATION_NUMBER
ISRC_PREFIX = settings.ISRC_PREFIX
PUBLISHER_NUMBER = settings.PUBLISHER_NUMBER
BUSINESS_EIN = settings.BUSINESS_EIN
BUSINESS_ADDRESS = settings.BUSINESS_ADDRESS
BUSINESS_PHONE = settings.BUSINESS_PHONE
BUSINESS_NAICS_CODE = settings.BUSINESS_NAICS_CODE
BUSINESS_TIN = settings.BUSINESS_TIN
BUSINESS_LEGAL_NAME = settings.BUSINESS_LEGAL_NAME
PRINCIPAL_NAME = settings.PRINCIPAL_NAME
IPI_BUSINESS = settings.IPI_BUSINESS
IPI_PRINCIPAL = settings.IPI_PRINCIPAL
IPN_NUMBER = settings.IPN_NUMBER
DPID = settings.DPID

@router.get("/business/identifiers")
async def get_business_identifiers(current_user: User = Depends(get_current_user)):
    return BusinessIdentifiers(
        business_legal_name=BUSINESS_LEGAL_NAME,
        business_ein=BUSINESS_EIN,
        business_tin=BUSINESS_TIN,
        business_address=BUSINESS_ADDRESS,
        business_phone=BUSINESS_PHONE,
        business_naics_code=BUSINESS_NAICS_CODE,
        upc_company_prefix=UPC_COMPANY_PREFIX,
        global_location_number=GLOBAL_LOCATION_NUMBER,
        isrc_prefix=ISRC_PREFIX,
        publisher_number=PUBLISHER_NUMBER,
        ipi_business=IPI_BUSINESS,
        ipi_principal=IPI_PRINCIPAL,
        ipn_number=IPN_NUMBER,
        dpid=DPID
    )

@router.post("/business/generate-upc")
async def generate_upc(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Generate UPC code - accepts both Form and JSON data"""
    try:
        # Handle both Form and JSON data
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON data
            body = await request.json()
            product_name = body.get("product_name")
            product_category = body.get("product_category")
        else:
            # Handle Form data
            form_data = await request.form()
            product_name = form_data.get("product_name")
            product_category = form_data.get("product_category")
        
        if not product_name or not product_category:
            raise HTTPException(status_code=400, detail="product_name and product_category are required")
        
        # Use first 6 digits of company prefix for UPC-A format
        company_prefix_6 = UPC_COMPANY_PREFIX[:6]  # "860004"
        
        # Generate 5-digit product code (to make 11 digits total with 6-digit prefix)
        product_code = f"{abs(hash(product_name + product_category)) % 100000:05d}"
        
        # Combine company prefix and product code (11 digits total)
        upc_11_digits = company_prefix_6 + product_code
        
        # Calculate check digit
        check_digit = calculate_upc_check_digit(upc_11_digits)
        
        # Create full UPC
        upc_full = upc_11_digits + check_digit
        
        # Create GTIN (add leading zero to UPC for 13-digit GTIN)
        gtin = "0" + upc_full
        
        # Create product identifier record
        product_identifier = ProductIdentifier(
            product_name=product_name,
            upc_full_code=upc_full,
            gtin=gtin,
            product_category=product_category
        )
        
        # Store in database
        await db.product_identifiers.insert_one(product_identifier.dict())
        
        # Log activity
        await log_activity(
            current_user.id,
            "upc_generated",
            "product_identifier",
            product_identifier.id,
            {
                "product_name": product_name,
                "upc": upc_full,
                "product_category": product_category
            }
        )
        
        return {
            "success": True,
            "message": "UPC generated successfully",
            "data": {
                "product_name": product_name,
                "upc": upc_full,
                "gtin": gtin,
                "company_prefix": UPC_COMPANY_PREFIX,
                "product_code": product_code,
                "check_digit": check_digit,
                "product_category": product_category,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate UPC: {str(e)}")

@router.post("/business/generate-isrc")
async def generate_isrc(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Generate ISRC code - accepts both Form and JSON data"""
    try:
        # Handle both Form and JSON data
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON data
            body = await request.json()
            artist_name = body.get("artist_name")
            track_title = body.get("track_title")
            release_year = body.get("release_year", datetime.utcnow().year)
        else:
            # Handle Form data
            form_data = await request.form()
            artist_name = form_data.get("artist_name")
            track_title = form_data.get("track_title")
            release_year = int(form_data.get("release_year", datetime.utcnow().year))
        
        if not artist_name or not track_title:
            raise HTTPException(status_code=400, detail="artist_name and track_title are required")
        
        # Validate release year
        current_year = datetime.utcnow().year
        if not isinstance(release_year, int) or release_year < 1900 or release_year > current_year + 5:
            release_year = current_year
        
        # Generate 5-digit designation code
        designation_code = f"{abs(hash(track_title + artist_name)) % 100000:05d}"
        
        # Create ISRC code: Country Code (2) + Registrant Code (3) + Year (2) + Designation (5)
        # Format: CC-XXX-YY-NNNNN
        country_code = "US"
        registrant_code = ISRC_PREFIX[:3]  # Use first 3 characters
        year_code = str(release_year)[-2:]  # Last 2 digits of year
        
        isrc_code = f"{country_code}-{registrant_code}-{year_code}-{designation_code}"
        
        # Store ISRC record in database
        isrc_record = {
            "id": str(uuid.uuid4()),
            "isrc_code": isrc_code,
            "artist_name": artist_name,
            "track_title": track_title,
            "release_year": release_year,
            "country_code": country_code,
            "registrant_code": ISRC_PREFIX,
            "year_code": year_code,
            "designation_code": designation_code,
            "generated_by": current_user.id,
            "generated_at": datetime.utcnow(),
            "status": "active"
        }
        
        await db.isrc_codes.insert_one(isrc_record)
        
        # Log activity
        await log_activity(
            current_user.id,
            "isrc_generated",
            "isrc_code",
            isrc_record["id"],
            {
                "isrc_code": isrc_code,
                "artist_name": artist_name,
                "track_title": track_title,
                "release_year": release_year
            }
        )
        
        return {
            "success": True,
            "message": "ISRC generated successfully",
            "data": {
                "isrc_code": isrc_code,
                "artist_name": artist_name,
                "track_title": track_title,
                "release_year": release_year,
                "country_code": country_code,
                "registrant_code": ISRC_PREFIX,
                "year_code": year_code,
                "designation_code": designation_code,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ISRC: {str(e)}")

# Add missing business/products endpoint
@router.get("/business/products")
async def get_business_products(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get all product identifiers for the business"""
    try:
        # Get products from database
        cursor = db.product_identifiers.find({}).skip(skip).limit(limit).sort("created_at", -1)
        products = []
        
        async for product_doc in cursor:
            products.append(ProductIdentifier(**product_doc))
        
        # Get total count
        total_count = await db.product_identifiers.count_documents({})
        
        return {
            "products": products,
            "total_count": total_count,
            "page": skip // limit + 1,
            "pages": (total_count + limit - 1) // limit
        }
    except Exception as e:
        return {
            "products": [],
            "total_count": 0,
            "page": 1,
            "pages": 0,
            "message": "No products found"
        }


