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
from industry_models import IndustryPartner, ContentDistribution, IndustryAnalytics, IndustryIdentifier, MusicDataExchange, MDXTrack

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/industry", tags=["Industry Integration"])

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
        
        # Log distribution activity
        from server import log_activity
        await log_activity(
            current_user.id,
            "global_content_distribution",
            "product",
            product_id,
            {
                "product_name": product.get("product_name"),
                "total_platforms": results["total_platforms"],
                "successful": results["successful_distributions"],
                "failed": results["failed_distributions"]
            },
            request
        )
        
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