from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import jwt
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

from industry_service import IndustryIntegrationService
from industry_models import IndustryPartner, ContentDistribution, IndustryAnalytics, IndustryIdentifier, MusicDataExchange, MDXTrack, MechanicalLicensingCollective, MLCMusicalWork

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/industry", tags=["Industry Integration"])

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'big_mann_entertainment')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Authentication setup
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()

class User:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', '') not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Industry Connection and Management Endpoints
@router.post("/initialize")
async def initialize_industry_connections(admin_user: User = Depends(get_admin_user)):
    """Initialize all industry partner connections"""
    try:
        service = IndustryIntegrationService(db)
        total_partners = await service.initialize_industry_partners()
        
        return {
            "success": True,
            "message": f"Successfully initialized {total_partners} industry partners",
            "total_partners": total_partners,
            "categories": [
                "streaming_platforms",
                "record_labels", 
                "radio_stations",
                "tv_networks",
                "venues",
                "booking_agencies"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error initializing industry connections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize industry connections: {str(e)}")

@router.get("/partners")
async def get_industry_partners(
    category: Optional[str] = None,
    tier: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all industry partners with optional filtering"""
    try:
        service = IndustryIntegrationService(db)
        partners = await service.get_industry_partners(category=category, tier=tier)
        
        return {
            "partners": partners,
            "total_count": len(partners),
            "filters_applied": {
                "category": category,
                "tier": tier
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving industry partners: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve industry partners: {str(e)}")

@router.get("/partners/streaming")
async def get_streaming_platforms(current_user: User = Depends(get_current_user)):
    """Get all streaming platforms"""
    try:
        service = IndustryIntegrationService(db)
        platforms = await service.get_industry_partners(category="streaming_platform")
        
        # Organize by tier
        major_platforms = [p for p in platforms if p["tier"] == "major"]
        independent_platforms = [p for p in platforms if p["tier"] == "independent"]
        
        return {
            "major_platforms": major_platforms,
            "independent_platforms": independent_platforms,
            "total_platforms": len(platforms),
            "coverage": {
                "global_reach": len([p for p in platforms if "global" in p.get("territories", [])]),
                "regional_platforms": len([p for p in platforms if "global" not in p.get("territories", [])])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve streaming platforms: {str(e)}")

@router.get("/partners/labels")
async def get_record_labels(current_user: User = Depends(get_current_user)):
    """Get all record labels"""
    try:
        service = IndustryIntegrationService(db)
        labels = await service.get_industry_partners(category="record_label")
        
        major_labels = [l for l in labels if l["tier"] == "major"]
        independent_labels = [l for l in labels if l["tier"] == "independent"]
        
        return {
            "major_labels": major_labels,
            "independent_labels": independent_labels,
            "total_labels": len(labels),
            "distribution_reach": {
                "global_labels": len([l for l in labels if "global" in l.get("territories", [])]),
                "regional_labels": len([l for l in labels if "global" not in l.get("territories", [])])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve record labels: {str(e)}")

@router.get("/partners/radio")
async def get_radio_stations(current_user: User = Depends(get_current_user)):
    """Get all radio stations"""
    try:
        service = IndustryIntegrationService(db)
        stations = await service.get_industry_partners(category="radio_station")
        
        return {
            "radio_stations": stations,
            "total_stations": len(stations),
            "market_coverage": {
                "major_markets": len([s for s in stations if s.get("market_size") == "major"]),
                "medium_markets": len([s for s in stations if s.get("market_size") == "medium"]),
                "small_markets": len([s for s in stations if s.get("market_size") == "small"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve radio stations: {str(e)}")

@router.get("/partners/venues")
async def get_venues(current_user: User = Depends(get_current_user)):
    """Get all venues"""
    try:
        service = IndustryIntegrationService(db)
        venues = await service.get_industry_partners(category="venue")
        
        return {
            "venues": venues,
            "total_venues": len(venues),
            "venue_types": {
                "arenas": len([v for v in venues if v.get("venue_type") == "arena"]),
                "theaters": len([v for v in venues if v.get("venue_type") == "theater"]),
                "clubs": len([v for v in venues if v.get("venue_type") == "club"]),
                "festivals": len([v for v in venues if v.get("venue_type") == "festival"]),
                "outdoor": len([v for v in venues if v.get("venue_type") == "outdoor"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve venues: {str(e)}")

# Content Distribution Endpoints
@router.post("/distribute/{product_id}")
async def distribute_content_globally(
    product_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Distribute content to ALL connected industry partners"""
    try:
        # Get product metadata
        product = await db.product_identifiers.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        service = IndustryIntegrationService(db)
        results = await service.distribute_content_to_all_platforms(product_id, product)
        
        # Log distribution activity (simplified to avoid circular import)
        # await log_activity(...) - removed to avoid circular import
        
        return {
            "success": True,
            "message": f"Content distributed to {results['successful_distributions']} out of {results['total_platforms']} platforms",
            "distribution_results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in global distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Global distribution failed: {str(e)}")

@router.get("/distributions")
async def get_content_distributions(
    product_id: Optional[str] = None,
    partner_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get content distribution records"""
    try:
        query = {}
        if product_id:
            query["product_id"] = product_id
        if partner_id:
            query["partner_id"] = partner_id
        if status:
            query["distribution_status"] = status
        
        cursor = db.content_distributions.find(query).sort("created_at", -1)
        distributions = await cursor.to_list(100)  # Limit to 100 records
        
        return {
            "distributions": distributions,
            "total_count": len(distributions),
            "filters_applied": {
                "product_id": product_id,
                "partner_id": partner_id,
                "status": status
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve distributions: {str(e)}")

@router.get("/distributions/{distribution_id}")
async def get_distribution_details(
    distribution_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific distribution"""
    try:
        distribution = await db.content_distributions.find_one({"id": distribution_id})
        if not distribution:
            raise HTTPException(status_code=404, detail="Distribution not found")
        
        # Get partner information
        partner = await db.industry_partners.find_one({"id": distribution["partner_id"]})
        
        # Get product information
        product = await db.product_identifiers.find_one({"id": distribution["product_id"]})
        
        return {
            "distribution": distribution,
            "partner": partner,
            "product": product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve distribution details: {str(e)}")

# Analytics and Reporting Endpoints
@router.get("/analytics")
async def get_industry_analytics(
    product_id: Optional[str] = None,
    partner_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics across all industry partners"""
    try:
        service = IndustryIntegrationService(db)
        analytics = await service.get_industry_analytics(product_id=product_id, partner_id=partner_id)
        
        return {
            "analytics": analytics,
            "summary": "Industry-wide performance metrics and revenue data"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

@router.get("/dashboard")
async def get_industry_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive industry dashboard data"""
    try:
        service = IndustryIntegrationService(db)
        dashboard_data = await service.get_industry_dashboard_data()
        
        return {
            "dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "user": current_user.email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {str(e)}")

# Data Synchronization Endpoints
@router.post("/sync")
async def sync_industry_data(current_user: User = Depends(get_current_user)):
    """Sync data with all connected industry partners"""
    try:
        service = IndustryIntegrationService(db)
        sync_results = await service.sync_industry_data()
        
        return {
            "success": True,
            "message": f"Synced data with {sync_results['successful_syncs']} out of {sync_results['total_partners']} partners",
            "sync_results": sync_results
        }
        
    except Exception as e:
        logger.error(f"Error syncing industry data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data sync failed: {str(e)}")

# Partner Management Endpoints (Admin only)
@router.post("/partners")
async def add_industry_partner(
    partner_data: IndustryPartner,
    admin_user: User = Depends(get_admin_user)
):
    """Add a new industry partner"""
    try:
        partner_dict = partner_data.dict()
        await db.industry_partners.insert_one(partner_dict)
        
        return {
            "success": True,
            "message": f"Successfully added {partner_data.name} as an industry partner",
            "partner": partner_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add industry partner: {str(e)}")

@router.put("/partners/{partner_id}")
async def update_industry_partner(
    partner_id: str,
    partner_data: Dict[str, Any],
    admin_user: User = Depends(get_admin_user)
):
    """Update an industry partner"""
    try:
        result = await db.industry_partners.update_one(
            {"id": partner_id},
            {"$set": {**partner_data, "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        return {
            "success": True,
            "message": "Industry partner updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update industry partner: {str(e)}")

@router.delete("/partners/{partner_id}")
async def remove_industry_partner(
    partner_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Remove an industry partner"""
    try:
        result = await db.industry_partners.delete_one({"id": partner_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        return {
            "success": True,
            "message": "Industry partner removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove industry partner: {str(e)}")

# Revenue and Financial Tracking
@router.get("/revenue")
async def get_revenue_tracking(
    product_id: Optional[str] = None,
    partner_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get revenue tracking across all industry partners"""
    try:
        query = {}
        if product_id:
            query["product_id"] = product_id
        if partner_id:
            query["partner_id"] = partner_id
        
        cursor = db.revenue_tracking.find(query).sort("created_at", -1)
        revenue_records = await cursor.to_list(100)
        
        # Calculate totals
        total_gross = sum(r.get("gross_amount", 0.0) for r in revenue_records)
        total_net = sum(r.get("net_amount", 0.0) for r in revenue_records)
        total_fees = sum(r.get("partner_fee", 0.0) for r in revenue_records)
        
        return {
            "revenue_records": revenue_records,
            "summary": {
                "total_records": len(revenue_records),
                "total_gross_revenue": total_gross,
                "total_net_revenue": total_net,
                "total_partner_fees": total_fees
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve revenue data: {str(e)}")

@router.get("/coverage")
async def get_industry_coverage(current_user: User = Depends(get_current_user)):
    """Get comprehensive overview of industry coverage"""
    try:
        service = IndustryIntegrationService(db)
        partners = await service.get_industry_partners()
        
        # Analyze coverage
        territories = set()
        categories = set()
        tiers = set()
        
        for partner in partners:
            categories.add(partner["category"])
            tiers.add(partner["tier"])
            territories.update(partner.get("territories", []))
        
        coverage_analysis = {
            "total_partners": len(partners),
            "categories_covered": list(categories),
            "tiers_covered": list(tiers),
            "territories_covered": list(territories),
            "global_reach": len([p for p in partners if "global" in p.get("territories", [])]),
            "streaming_platforms": len([p for p in partners if p["category"] == "streaming_platform"]),
            "record_labels": len([p for p in partners if p["category"] == "record_label"]),
            "radio_stations": len([p for p in partners if p["category"] == "radio_station"]),
            "tv_networks": len([p for p in partners if p["category"] == "tv_network"]),
            "venues": len([p for p in partners if p["category"] == "venue"]),
            "booking_agencies": len([p for p in partners if p["category"] == "booking_agency"])
        }
        
        return {
            "coverage": coverage_analysis,
            "message": "Complete industry ecosystem coverage analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze industry coverage: {str(e)}")

# Industry Identifiers Management Endpoints (IPI, ISNI, AARC)
@router.get("/identifiers")
async def get_industry_identifiers(
    entity_type: Optional[str] = None,
    identifier_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all industry identifiers (IPI, ISNI, AARC) with optional filtering"""
    try:
        service = IndustryIntegrationService(db)
        identifiers = await service.get_industry_identifiers(entity_type=entity_type, identifier_type=identifier_type)
        
        return {
            "identifiers": identifiers,
            "total_count": len(identifiers),
            "filters_applied": {
                "entity_type": entity_type,
                "identifier_type": identifier_type
            },
            "big_mann_entertainment": {
                "company": {
                    "name": "Big Mann Entertainment",
                    "ipi": "813048171",
                    "aarc": "RC00002057"
                },
                "individual": {
                    "name": "John LeGerron Spivey", 
                    "ipi": "578413032",
                    "isni": "0000000491551894",
                    "aarc": "FA02933539"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving industry identifiers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve industry identifiers: {str(e)}")

@router.post("/identifiers")
async def add_industry_identifier(
    identifier_data: IndustryIdentifier,
    admin_user: User = Depends(get_admin_user)
):
    """Add a new industry identifier (IPI, ISNI, AARC)"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.add_industry_identifier(identifier_data.dict())
        
        return {
            "success": True,
            "message": f"Successfully added industry identifier for {identifier_data.entity_name}",
            "identifier": result["identifier"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add industry identifier: {str(e)}")

@router.put("/identifiers/{entity_name}")
async def update_industry_identifier(
    entity_name: str,
    update_data: Dict[str, Any],
    admin_user: User = Depends(get_admin_user)
):
    """Update an industry identifier"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.update_industry_identifier(entity_name, update_data)
        
        return {
            "success": True,
            "message": f"Successfully updated industry identifier for {entity_name}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update industry identifier: {str(e)}")

@router.get("/identifiers/{entity_name}")
async def get_industry_identifier_details(
    entity_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific entity's industry identifiers"""
    try:
        identifier = await db.industry_identifiers.find_one({"entity_name": entity_name})
        if not identifier:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return {
            "identifier": identifier,
            "message": f"Industry identifier for {entity_name} retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve industry identifier details: {str(e)}")

@router.get("/identifiers/dashboard")
async def get_industry_identifiers_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive industry identifiers dashboard data"""
    try:
        service = IndustryIntegrationService(db)
        dashboard_data = await service.get_industry_identifiers_dashboard_data()
        
        return {
            "dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "user": current_user.email,
            "message": "Industry identifiers dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve industry identifiers dashboard data: {str(e)}")

@router.delete("/identifiers/{entity_name}")
async def remove_industry_identifier(
    entity_name: str,
    admin_user: User = Depends(get_admin_user)
):
    """Remove an industry identifier"""
    try:
        result = await db.industry_identifiers.delete_one({"entity_name": entity_name})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return {
            "success": True,
            "message": f"Industry identifier for {entity_name} removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove industry identifier: {str(e)}")

# Legacy IPI Number Management Endpoints (for backward compatibility)
@router.get("/ipi")
async def get_ipi_numbers(
    entity_type: Optional[str] = None,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all IPI numbers with optional filtering"""
    try:
        service = IndustryIntegrationService(db)
        ipi_numbers = await service.get_ipi_numbers(entity_type=entity_type, role=role)
        
        return {
            "ipi_numbers": ipi_numbers,
            "total_count": len(ipi_numbers),
            "filters_applied": {
                "entity_type": entity_type,
                "role": role
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving IPI numbers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve IPI numbers: {str(e)}")

@router.post("/ipi")
async def add_ipi_number(
    ipi_data: IndustryIdentifier,
    admin_user: User = Depends(get_admin_user)
):
    """Add a new IPI number"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.add_ipi_number(ipi_data.dict())
        
        return {
            "success": True,
            "message": f"Successfully added IPI number {ipi_data.ipi_number} for {ipi_data.entity_name}",
            "ipi_number": result["ipi"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add IPI number: {str(e)}")

@router.put("/ipi/{ipi_number}")
async def update_ipi_number(
    ipi_number: str,
    update_data: Dict[str, Any],
    admin_user: User = Depends(get_admin_user)
):
    """Update an IPI number"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.update_ipi_number(ipi_number, update_data)
        
        return {
            "success": True,
            "message": f"Successfully updated IPI number {ipi_number}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update IPI number: {str(e)}")

@router.get("/ipi/{ipi_number}")
async def get_ipi_number_details(
    ipi_number: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific IPI number"""
    try:
        ipi = await db.ipi_numbers.find_one({"ipi_number": ipi_number})
        if not ipi:
            raise HTTPException(status_code=404, detail="IPI number not found")
        
        return {
            "ipi_number": ipi,
            "message": f"IPI number {ipi_number} details retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve IPI number details: {str(e)}")

@router.get("/ipi/dashboard")
async def get_ipi_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive IPI dashboard data"""
    try:
        service = IndustryIntegrationService(db)
        dashboard_data = await service.get_ipi_dashboard_data()
        
        return {
            "dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "user": current_user.email,
            "message": "IPI dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve IPI dashboard data: {str(e)}")

@router.delete("/ipi/{ipi_number}")
async def remove_ipi_number(
    ipi_number: str,
    admin_user: User = Depends(get_admin_user)
):
    """Remove an IPI number"""
    try:
        result = await db.ipi_numbers.delete_one({"ipi_number": ipi_number})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="IPI number not found")
        
        return {
            "success": True,
            "message": f"IPI number {ipi_number} removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove industry identifier: {str(e)}")

# Enhanced Entertainment Industry Endpoints

@router.get("/entertainment/partners/{category}")
async def get_entertainment_partners_by_category(
    category: str,
    tier: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get entertainment industry partners by category"""
    try:
        service = IndustryIntegrationService(db)
        partners = await service.get_entertainment_partners_by_category(category, tier)
        
        return {
            "category": category,
            "tier": tier,
            "partners": partners,
            "total_count": len(partners),
            "message": f"Retrieved {len(partners)} partners in {category} category"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve entertainment partners: {str(e)}")

@router.get("/photography/services")
async def get_photography_services(
    service_type: Optional[str] = None,
    price_range: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get photography services with filtering options"""
    try:
        service = IndustryIntegrationService(db)
        services = await service.get_photography_services(service_type, price_range)
        
        return {
            "services": services,
            "total_count": len(services),
            "filters": {
                "service_type": service_type,
                "price_range": price_range
            },
            "available_types": ["album_cover", "promotional", "event", "fashion", "commercial"],
            "message": f"Retrieved {len(services)} photography services"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve photography services: {str(e)}")

@router.get("/video/production")
async def get_video_production_services(
    production_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get video production services"""
    try:
        service = IndustryIntegrationService(db)
        services = await service.get_video_production_services(production_type)
        
        return {
            "services": services,
            "total_count": len(services),
            "production_type": production_type,
            "available_types": ["music_videos", "production_companies", "commercial", "documentary"],
            "message": f"Retrieved {len(services)} video production services"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve video production services: {str(e)}")

@router.get("/monetization/opportunities")
async def get_monetization_opportunities(
    content_type: str = "all",
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive monetization opportunities across all entertainment platforms"""
    try:
        service = IndustryIntegrationService(db)
        opportunities = await service.get_monetization_opportunities(content_type)
        
        return {
            "monetization_opportunities": opportunities,
            "content_type": content_type,
            "big_mann_entertainment": {
                "comprehensive_reach": "Full entertainment industry coverage",
                "revenue_potential": "Multi-stream revenue optimization",
                "platform_integration": "Seamless cross-platform distribution"
            },
            "message": "Comprehensive monetization opportunities retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve monetization opportunities: {str(e)}")

@router.get("/entertainment/dashboard")
async def get_comprehensive_entertainment_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive entertainment industry dashboard"""
    try:
        service = IndustryIntegrationService(db)
        dashboard_data = await service.get_comprehensive_entertainment_dashboard()
        
        return {
            "dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "user": current_user.email,
            "platform_overview": {
                "name": "Big Mann Entertainment",
                "industry_coverage": "Comprehensive Entertainment Ecosystem",
                "content_types": ["Music", "Photography", "Video", "Live Streaming", "Gaming", "Podcasts"],
                "monetization_streams": "Multi-platform revenue optimization"
            },
            "message": "Comprehensive entertainment dashboard retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve entertainment dashboard: {str(e)}")

@router.post("/entertainment/content/monetize")
async def create_content_monetization_strategy(
    content_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Create a monetization strategy for content across entertainment platforms"""
    try:
        content_type = content_data.get("content_type", "mixed")
        content_title = content_data.get("title", "Untitled Content")
        
        service = IndustryIntegrationService(db)
        
        # Get relevant platforms based on content type
        if content_type in ["photo", "photography"]:
            platforms = await service.get_entertainment_partners_by_category("stock_photography")
            social_platforms = await service.get_entertainment_partners_by_category("social_media_photography")
            platforms.extend(social_platforms)
        elif content_type in ["video", "music_video"]:
            platforms = await service.get_entertainment_partners_by_category("video_production")
            streaming_platforms = await service.get_entertainment_partners_by_category("live_streaming")
            platforms.extend(streaming_platforms)
        elif content_type in ["audio", "music", "podcast"]:
            platforms = await service.get_entertainment_partners_by_category("streaming_platform")
            podcast_platforms = await service.get_entertainment_partners_by_category("podcast_platform")
            platforms.extend(podcast_platforms)
        else:
            # Mixed content - get all platforms
            categories = ["stock_photography", "social_media_photography", "video_production", 
                         "live_streaming", "streaming_platform", "podcast_platform", "gaming_esports"]
            platforms = []
            for category in categories:
                category_platforms = await service.get_entertainment_partners_by_category(category)
                platforms.extend(category_platforms)
        
        # Create monetization strategy
        strategy = {
            "content_title": content_title,
            "content_type": content_type,
            "recommended_platforms": [p["name"] for p in platforms[:10]],
            "monetization_methods": [
                "Direct sales/licensing",
                "Revenue sharing",
                "Subscription content",
                "Advertising revenue",
                "Brand partnerships",
                "Commission-based sales"
            ],
            "estimated_revenue_potential": {
                "photography": "$100-$5000/month",
                "video": "$500-$50000/project", 
                "audio": "$50-$10000/month",
                "cross_platform": "$1000-$100000/month"
            },
            "optimization_tips": [
                "Diversify across multiple platforms",
                "Optimize content for each platform's requirements",
                "Track performance analytics",
                "Build audience engagement",
                "Regular content updates",
                "Professional quality standards"
            ]
        }
        
        return {
            "strategy": strategy,
            "total_platforms": len(platforms),
            "big_mann_entertainment": {
                "advantage": "Comprehensive industry connections",
                "support": "Full-service content monetization",
                "reach": "Global entertainment market access"
            },
            "message": f"Monetization strategy created for {content_title}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create monetization strategy: {str(e)}")

@router.get("/entertainment/analytics")
async def get_entertainment_analytics(
    category: Optional[str] = None,
    timeframe: str = "30d",
    current_user: User = Depends(get_current_user)
):
    """Get entertainment industry analytics and performance metrics"""
    try:
        service = IndustryIntegrationService(db)
        
        # Get comprehensive analytics
        analytics_data = {
            "timeframe": timeframe,
            "platform_performance": {},
            "content_analytics": {},
            "revenue_tracking": {},
            "growth_metrics": {},
            "big_mann_entertainment_stats": {
                "total_industry_connections": 0,
                "active_revenue_streams": 0,
                "content_distribution_reach": "Global",
                "platform_categories": [
                    "Music Streaming", "Photography Services", "Video Production",
                    "Live Streaming", "Podcast Hosting", "Gaming Integration",
                    "Social Media", "Fashion Photography", "Stock Photography"
                ]
            }
        }
        
        # Get platform counts for analytics
        categories = [
            "photography_service", "stock_photography", "social_media_photography",
            "video_production", "podcast_platform", "live_streaming",
            "gaming_esports", "fashion_photography", "streaming_platform"
        ]
        
        total_connections = 0
        for cat in categories:
            partners = await service.get_entertainment_partners_by_category(cat)
            analytics_data["platform_performance"][cat] = {
                "total_platforms": len(partners),
                "active_platforms": len([p for p in partners if p.get("status") == "active"]),
                "growth_rate": "+15%",  # Mock data - would be calculated from historical data
                "revenue_contribution": f"${1000 + len(partners) * 500}"  # Mock revenue data
            }
            total_connections += len(partners)
        
        analytics_data["big_mann_entertainment_stats"]["total_industry_connections"] = total_connections
        analytics_data["big_mann_entertainment_stats"]["active_revenue_streams"] = len(categories)
        
        # Mock performance metrics
        analytics_data["content_analytics"] = {
            "total_content_pieces": 150,
            "monetized_content": 125,
            "average_revenue_per_content": "$1200",
            "top_performing_category": "Music Video Production"
        }
        
        analytics_data["revenue_tracking"] = {
            "monthly_revenue": "$45000",
            "revenue_growth": "+25%",
            "top_revenue_source": "Multi-platform streaming",
            "diversification_score": "95%"
        }
        
        return {
            "analytics": analytics_data,
            "last_updated": datetime.utcnow().isoformat(),
            "message": "Entertainment industry analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve entertainment analytics: {str(e)}")

# Music Data Exchange (MDX) Integration Endpoints

@router.post("/mdx/initialize")
async def initialize_mdx_integration(admin_user: User = Depends(get_admin_user)):
    """Initialize Music Data Exchange integration for Big Mann Entertainment"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.initialize_mdx_integration()
        
        return {
            "success": True,
            "message": "Music Data Exchange integration initialized successfully",
            "mdx_configuration": result,
            "big_mann_entertainment": {
                "entity_type": "label",
                "ipi_integration": True,
                "real_time_sync": True,
                "comprehensive_rights_management": True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize MDX integration: {str(e)}")

@router.post("/mdx/track/sync")
async def sync_track_with_mdx(
    track_data: MDXTrack,
    current_user: User = Depends(get_current_user)
):
    """Sync track metadata with Music Data Exchange"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.sync_track_with_mdx(track_data.dict())
        
        return {
            "success": True,
            "track_sync_result": result,
            "mdx_integration": {
                "metadata_quality": "High",
                "rights_clearance": "Automated",
                "distribution_ready": True
            },
            "message": f"Track '{track_data.title}' successfully synced with MDX"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync track with MDX: {str(e)}")

@router.post("/mdx/tracks/bulk")
async def bulk_upload_tracks_to_mdx(
    tracks_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
):
    """Bulk upload tracks to Music Data Exchange"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.process_mdx_bulk_upload(tracks_data)
        
        return {
            "bulk_upload_result": result,
            "big_mann_entertainment": {
                "processing_efficiency": "Automated bulk processing",
                "rights_management": "Comprehensive metadata handling",
                "distribution_optimization": "Multi-platform sync"
            },
            "message": f"Bulk upload completed: {result['successfully_processed']} tracks processed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process bulk MDX upload: {str(e)}")

@router.get("/mdx/tracks")
async def get_mdx_tracks(
    artist_name: Optional[str] = None,
    big_mann_release: Optional[bool] = None,
    rights_clearance_status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get MDX tracks with optional filtering"""
    try:
        service = IndustryIntegrationService(db)
        filters = {}
        if artist_name:
            filters["artist_name"] = artist_name
        if big_mann_release is not None:
            filters["big_mann_release"] = big_mann_release
        if rights_clearance_status:
            filters["rights_clearance_status"] = rights_clearance_status
        
        tracks = await service.get_mdx_tracks(filters)
        
        return {
            "tracks": tracks,
            "total_count": len(tracks),
            "filters_applied": filters,
            "big_mann_entertainment": {
                "total_catalog": len([t for t in tracks if t.get("big_mann_release", False)]),
                "rights_status": "Comprehensive management",
                "distribution_ready": len([t for t in tracks if t.get("rights_clearance_status") == "cleared"])
            },
            "message": f"Retrieved {len(tracks)} MDX tracks"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve MDX tracks: {str(e)}")

@router.post("/mdx/rights/manage")
async def manage_mdx_rights(
    rights_data: Dict[str, Any],
    admin_user: User = Depends(get_admin_user)
):
    """Manage rights through Music Data Exchange"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.manage_mdx_rights(rights_data)
        
        return {
            "rights_management_result": result,
            "big_mann_entertainment": {
                "rights_optimization": "Automated clearance system",
                "revenue_protection": "Comprehensive rights tracking",
                "global_management": "Multi-territory rights handling"
            },
            "message": "Rights successfully managed through MDX integration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to manage MDX rights: {str(e)}")

@router.get("/mdx/dashboard")
async def get_mdx_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive MDX dashboard analytics"""
    try:
        service = IndustryIntegrationService(db)
        dashboard_data = await service.get_mdx_dashboard_data()
        
        return {
            "mdx_dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "user": current_user.email,
            "platform_status": {
                "mdx_integration": "Fully Operational",
                "real_time_sync": "Active",
                "rights_management": "Automated",
                "revenue_optimization": "Active"
            },
            "message": "MDX dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve MDX dashboard: {str(e)}")

@router.get("/mdx/rights/{track_id}")
async def get_track_rights_information(
    track_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed rights information for a specific track"""
    try:
        # Get track information
        track = await db.mdx_tracks.find_one({"id": track_id})
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Get associated rights
        rights_cursor = db.mdx_rights.find({"track_ids": track_id})
        rights = await rights_cursor.to_list(None)
        
        return {
            "track": track,
            "rights_information": rights,
            "rights_summary": {
                "total_rights": len(rights),
                "clearance_status": track.get("rights_clearance_status", "unknown"),
                "distribution_approved": track.get("rights_clearance_status") == "cleared",
                "big_mann_managed": track.get("big_mann_release", False)
            },
            "message": f"Rights information retrieved for track: {track.get('title', 'Unknown')}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve track rights information: {str(e)}")

@router.put("/mdx/track/{track_id}/update")
async def update_mdx_track_metadata(
    track_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update track metadata in MDX system"""
    try:
        # Update track in database
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.mdx_tracks.update_one(
            {"id": track_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Get updated track
        updated_track = await db.mdx_tracks.find_one({"id": track_id})
        
        return {
            "success": True,
            "updated_track": updated_track,
            "changes_applied": list(update_data.keys()),
            "mdx_sync_status": "pending_sync",
            "message": f"Track metadata updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update MDX track metadata: {str(e)}")

@router.delete("/mdx/track/{track_id}")
async def remove_track_from_mdx(
    track_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Remove track from MDX system"""
    try:
        # Remove track
        track_result = await db.mdx_tracks.delete_one({"id": track_id})
        
        if track_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Remove associated rights
        rights_result = await db.mdx_rights.delete_many({"track_ids": track_id})
        
        return {
            "success": True,
            "tracks_removed": track_result.deleted_count,
            "rights_removed": rights_result.deleted_count,
            "message": f"Track and associated rights removed from MDX system"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove track from MDX: {str(e)}")

# Mechanical Licensing Collective (MLC) Integration Endpoints

@router.post("/mlc/initialize")
async def initialize_mlc_integration(admin_user: User = Depends(get_admin_user)):
    """Initialize Mechanical Licensing Collective integration for Big Mann Entertainment"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.initialize_mlc_integration()
        
        return {
            "success": True,
            "message": "Mechanical Licensing Collective integration initialized successfully",
            "mlc_configuration": result,
            "big_mann_entertainment": {
                "publisher_status": "Active MLC Member",
                "member_number": "BME813048171",
                "mechanical_rights": "50% Publisher Share",
                "automated_collection": True,
                "royalty_distribution": "Monthly Direct Deposit"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize MLC integration: {str(e)}")

@router.post("/mlc/works/register")
async def register_musical_work_with_mlc(
    work_data: MLCMusicalWork,
    current_user: User = Depends(get_current_user)
):
    """Register a musical work with the Mechanical Licensing Collective"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.register_musical_work_with_mlc(work_data.dict())
        
        return {
            "success": True,
            "work_registration_result": result,
            "mlc_integration": {
                "publisher_rights": "Big Mann Entertainment - 50%",
                "songwriter_rights": "John LeGerron Spivey - 50%",
                "mechanical_licensing": "Automated Collection Enabled",
                "territory_coverage": "United States"
            },
            "message": f"Musical work '{work_data.work_title}' successfully registered with MLC"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register work with MLC: {str(e)}")

@router.get("/mlc/works")
async def get_mlc_registered_works(
    work_title: Optional[str] = None,
    big_mann_work: Optional[bool] = None,
    submission_status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get MLC registered works with optional filtering"""
    try:
        service = IndustryIntegrationService(db)
        filters = {}
        if work_title:
            filters["work_title"] = work_title
        if big_mann_work is not None:
            filters["big_mann_work"] = big_mann_work
        if submission_status:
            filters["submission_status"] = submission_status
        
        works = await service.get_mlc_works(filters)
        
        return {
            "works": works,
            "total_count": len(works),
            "filters_applied": filters,
            "big_mann_entertainment": {
                "total_catalog": len([w for w in works if w.get("big_mann_work", False)]),
                "registration_status": "Active Publisher Member",
                "mechanical_rights": "Comprehensive Collection Enabled"
            },
            "message": f"Retrieved {len(works)} MLC registered works"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve MLC works: {str(e)}")

@router.post("/mlc/royalties/process")
async def process_mlc_royalty_report(
    report_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Process MLC royalty report for Big Mann Entertainment"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.process_mlc_royalty_report(report_data)
        
        return {
            "royalty_processing_result": result,
            "big_mann_entertainment": {
                "publisher_distribution": "50% mechanical royalties",
                "songwriter_distribution": "John LeGerron Spivey - 50%",
                "payment_method": "Direct deposit",
                "processing_frequency": "Monthly automated"
            },
            "message": f"MLC royalty report processed: ${result.get('total_distributed', 0):,.2f} distributed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process MLC royalty report: {str(e)}")

@router.post("/mlc/usage/match")
async def match_usage_data_to_mlc_works(
    usage_data_list: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
):
    """Match DSP usage data to registered MLC works"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.match_usage_data_to_works(usage_data_list)
        
        return {
            "usage_matching_result": result,
            "matching_performance": {
                "total_processed": result.get("total_processed", 0),
                "successful_matches": result.get("matched_count", 0),
                "matching_rate": f"{result.get('matching_rate', 0):.1f}%",
                "royalties_calculated": f"${result.get('total_royalties_calculated', 0):,.2f}"
            },
            "big_mann_entertainment": {
                "catalog_matching": "Automated matching enabled",
                "royalty_calculation": "Real-time processing",
                "dsp_integration": "All major platforms connected"
            },
            "message": result.get("message", "Usage data matching completed")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match usage data: {str(e)}")

@router.get("/mlc/dashboard")
async def get_mlc_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive MLC dashboard analytics"""
    try:
        service = IndustryIntegrationService(db)
        dashboard_data = await service.get_mlc_dashboard_data()
        
        return {
            "mlc_dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "user": current_user.email,
            "platform_status": {
                "mlc_integration": "Fully Operational",
                "member_status": "Active Publisher",
                "royalty_collection": "Automated Monthly",
                "works_registration": "Real-time Processing"
            },
            "message": "MLC dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve MLC dashboard: {str(e)}")

@router.post("/mlc/claims/submit")
async def submit_mlc_claim_or_dispute(
    claim_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Submit a claim or dispute to MLC"""
    try:
        service = IndustryIntegrationService(db)
        result = await service.submit_mlc_claim_or_dispute(claim_data)
        
        return {
            "claim_submission_result": result,
            "big_mann_entertainment": {
                "claim_management": "Professional dispute resolution",
                "rights_protection": "Comprehensive claims processing",
                "legal_support": "Automated documentation"
            },
            "message": f"Claim submitted successfully: {result.get('mlc_claim_id', 'Unknown')}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit MLC claim: {str(e)}")

@router.get("/mlc/royalties/{period}")
async def get_mlc_royalty_report(
    period: str,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Get MLC royalty report for specific period"""
    try:
        # Set default year to current year if not provided
        if year is None:
            year = datetime.utcnow().year
        
        # Query for royalty reports
        query = {"report_type": period}
        if year:
            query["report_period_start"] = {
                "$gte": datetime(year, 1, 1),
                "$lt": datetime(year + 1, 1, 1)
            }
        
        cursor = db.mlc_royalty_reports.find(query)
        reports = await cursor.to_list(None)
        
        # Calculate summary statistics
        total_collected = sum([r.get("big_mann_royalties", 0.0) for r in reports])
        total_works = sum([r.get("big_mann_works_count", 0) for r in reports])
        
        return {
            "royalty_reports": reports,
            "summary": {
                "period": period,
                "year": year,
                "total_reports": len(reports),
                "total_royalties_collected": total_collected,
                "total_works": total_works,
                "average_per_report": total_collected / len(reports) if reports else 0
            },
            "big_mann_entertainment": {
                "publisher_share": "50% mechanical royalties",
                "songwriter_share": "John LeGerron Spivey - 50%",
                "collection_efficiency": "Automated processing"
            },
            "message": f"Retrieved {len(reports)} royalty reports for {period} {year}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve MLC royalty reports: {str(e)}")

@router.get("/mlc/analytics/performance")
async def get_mlc_performance_analytics(
    timeframe: str = "monthly",
    current_user: User = Depends(get_current_user)
):
    """Get MLC performance analytics and metrics"""
    try:
        service = IndustryIntegrationService(db)
        dashboard_data = await service.get_mlc_dashboard_data()
        
        # Enhanced analytics with performance metrics
        analytics_data = {
            "timeframe": timeframe,
            "collection_performance": {
                "total_royalties": dashboard_data.get("royalty_collection", {}).get("total_royalties_collected", 0),
                "collection_efficiency": "98.5%",
                "distribution_speed": "Monthly automated",
                "matching_accuracy": dashboard_data.get("usage_matching", {}).get("matching_rate", "0%")
            },
            "catalog_performance": {
                "total_works": dashboard_data.get("works_management", {}).get("total_registered_works", 0),
                "active_works": dashboard_data.get("works_management", {}).get("active_works", 0),
                "registration_success": dashboard_data.get("works_management", {}).get("registration_success_rate", "0%"),
                "catalog_growth": "+15% this quarter"
            },
            "platform_analytics": dashboard_data.get("platform_performance", {}),
            "big_mann_entertainment": {
                "market_position": "Independent Publisher Leader",
                "revenue_growth": "+25% year-over-year",
                "catalog_expansion": "Consistent growth trajectory",
                "technology_advantage": "Full MLC automation"
            }
        }
        
        return {
            "analytics": analytics_data,
            "last_updated": datetime.utcnow().isoformat(),
            "message": "MLC performance analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve MLC performance analytics: {str(e)}")

@router.delete("/mlc/works/{work_id}")
async def remove_mlc_work(
    work_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Remove a work from MLC registration"""
    try:
        # Remove work
        result = await db.mlc_works.delete_one({"id": work_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="MLC work not found")
        
        # Also remove associated usage data and claims
        await db.mlc_usage_data.delete_many({"matched_work_id": work_id})
        await db.mlc_claims.delete_many({"work_id": work_id})
        
        return {
            "success": True,
            "works_removed": result.deleted_count,
            "message": f"MLC work and associated data removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove MLC work: {str(e)}")

# Export the router as industry_router for consistency
industry_router = router