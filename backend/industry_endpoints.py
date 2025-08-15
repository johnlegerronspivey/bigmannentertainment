from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from database import get_db
from industry_service import IndustryIntegrationService
from industry_models import IndustryPartner, ContentDistribution, IndustryAnalytics, IPINumber
from server import get_current_user, get_admin_user, User, db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/industry", tags=["Industry Integration"])

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