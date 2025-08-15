import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from industry_models import (
    IndustryPartner, StreamingPlatform, RecordLabel, RadioStation, 
    TVNetwork, Venue, BookingAgency, ContentDistribution, 
    IndustryAnalytics, RevenueTracking, INDUSTRY_PARTNERS,
    IndustryIdentifier, BIG_MANN_INDUSTRY_IDENTIFIERS
)

logger = logging.getLogger(__name__)

class IndustryIntegrationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.session = None
        
    async def init_session(self):
        """Initialize HTTP session for API calls"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def initialize_industry_partners(self):
        """Initialize all industry partners from templates"""
        try:
            # Clear existing partners
            await self.db.industry_partners.delete_many({})
            
            # Initialize IPI numbers first
            await self.initialize_ipi_numbers()
            
            total_partners = 0
            
            # Add streaming platforms
            for tier, platforms in INDUSTRY_PARTNERS["streaming_platforms"].items():
                for platform_data in platforms:
                    platform = StreamingPlatform(
                        category="streaming_platform",
                        tier=tier,
                        **platform_data
                    )
                    await self.db.industry_partners.insert_one(platform.dict())
                    total_partners += 1
            
            # Add record labels
            for tier, labels in INDUSTRY_PARTNERS["record_labels"].items():
                for label_data in labels:
                    label = RecordLabel(
                        category="record_label",
                        tier=tier,
                        **label_data
                    )
                    await self.db.industry_partners.insert_one(label.dict())
                    total_partners += 1
            
            # Add radio stations
            for tier, stations in INDUSTRY_PARTNERS["radio_stations"].items():
                for station_data in stations:
                    station = RadioStation(
                        category="radio_station",
                        tier=tier,
                        **station_data
                    )
                    await self.db.industry_partners.insert_one(station.dict())
                    total_partners += 1
            
            # Add TV networks
            for tier, networks in INDUSTRY_PARTNERS["tv_networks"].items():
                for network_data in networks:
                    network = TVNetwork(
                        category="tv_network",
                        tier=tier,
                        **network_data
                    )
                    await self.db.industry_partners.insert_one(network.dict())
                    total_partners += 1
            
            # Add venues
            for tier, venues in INDUSTRY_PARTNERS["venues"].items():
                for venue_data in venues:
                    venue = Venue(
                        category="venue",
                        tier=tier,
                        **venue_data
                    )
                    await self.db.industry_partners.insert_one(venue.dict())
                    total_partners += 1
            
            # Add booking agencies
            for tier, agencies in INDUSTRY_PARTNERS["booking_agencies"].items():
                for agency_data in agencies:
                    agency = BookingAgency(
                        category="booking_agency",
                        tier=tier,
                        **agency_data
                    )
                    await self.db.industry_partners.insert_one(agency.dict())
                    total_partners += 1
            
            logger.info(f"Initialized {total_partners} industry partners")
            return total_partners
            
        except Exception as e:
            logger.error(f"Error initializing industry partners: {str(e)}")
            raise
    
    async def initialize_ipi_numbers(self):
        """Initialize industry identifiers for Big Mann Entertainment (IPI, ISNI, AARC)"""
        try:
            # Clear existing industry identifiers
            await self.db.industry_identifiers.delete_many({})
            
            total_identifiers = 0
            
            # Add Big Mann Entertainment industry identifiers
            for identifier_data in BIG_MANN_INDUSTRY_IDENTIFIERS:
                identifier = IndustryIdentifier(**identifier_data)
                await self.db.industry_identifiers.insert_one(identifier.dict())
                total_identifiers += 1
            
            logger.info(f"Initialized {total_identifiers} industry identifiers")
            return total_identifiers
            
        except Exception as e:
            logger.error(f"Error initializing industry identifiers: {str(e)}")
            raise
    
    async def get_industry_partners(self, category: Optional[str] = None, tier: Optional[str] = None) -> List[Dict]:
        """Get industry partners with optional filtering"""
        try:
            query = {"status": "active"}
            if category:
                query["category"] = category
            if tier:
                query["tier"] = tier
            
            cursor = self.db.industry_partners.find(query)
            partners = await cursor.to_list(None)
            return partners
            
        except Exception as e:
            logger.error(f"Error retrieving industry partners: {str(e)}")
            return []
    
    async def distribute_content_to_all_platforms(self, product_id: str, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute content to all connected platforms"""
        await self.init_session()
        
        try:
            streaming_platforms = await self.get_industry_partners(category="streaming_platform")
            distribution_results = {
                "total_platforms": len(streaming_platforms),
                "successful_distributions": 0,
                "failed_distributions": 0,
                "results": []
            }
            
            for platform in streaming_platforms:
                try:
                    result = await self._distribute_to_platform(
                        product_id, content_metadata, platform
                    )
                    
                    # Store distribution record
                    distribution = ContentDistribution(
                        product_id=product_id,
                        partner_id=platform["id"],
                        distribution_status=result["status"],
                        distribution_date=datetime.utcnow(),
                        partner_content_id=result.get("partner_content_id"),
                        metadata_mapping=result.get("metadata_mapping", {})
                    )
                    
                    await self.db.content_distributions.insert_one(distribution.dict())
                    
                    if result["status"] == "success":
                        distribution_results["successful_distributions"] += 1
                    else:
                        distribution_results["failed_distributions"] += 1
                    
                    distribution_results["results"].append({
                        "platform": platform["name"],
                        "status": result["status"],
                        "message": result.get("message", "")
                    })
                    
                except Exception as e:
                    logger.error(f"Distribution failed for {platform['name']}: {str(e)}")
                    distribution_results["failed_distributions"] += 1
                    distribution_results["results"].append({
                        "platform": platform["name"],
                        "status": "error",
                        "message": str(e)
                    })
            
            return distribution_results
            
        except Exception as e:
            logger.error(f"Error in mass distribution: {str(e)}")
            raise
        finally:
            await self.close_session()
    
    async def _distribute_to_platform(self, product_id: str, metadata: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute content to a specific platform"""
        try:
            # Simulate different platform-specific distribution logic
            platform_name = platform["name"].lower()
            
            if "spotify" in platform_name:
                return await self._distribute_to_spotify(product_id, metadata, platform)
            elif "apple" in platform_name:
                return await self._distribute_to_apple_music(product_id, metadata, platform)
            elif "amazon" in platform_name:
                return await self._distribute_to_amazon_music(product_id, metadata, platform)
            elif "youtube" in platform_name:
                return await self._distribute_to_youtube_music(product_id, metadata, platform)
            elif "tidal" in platform_name:
                return await self._distribute_to_tidal(product_id, metadata, platform)
            else:
                return await self._generic_distribution(product_id, metadata, platform)
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _distribute_to_spotify(self, product_id: str, metadata: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """Spotify-specific distribution logic"""
        try:
            # Simulate Spotify API call
            await asyncio.sleep(0.1)  # Simulate API call delay
            
            # Map metadata to Spotify format
            spotify_metadata = {
                "name": metadata.get("product_name"),
                "artists": [{"name": metadata.get("artist_name", "Unknown Artist")}],
                "album": {"name": metadata.get("album_title", "Single")},
                "duration_ms": (metadata.get("duration_seconds", 0) * 1000),
                "isrc": metadata.get("isrc_code"),
                "explicit": False
            }
            
            # Simulate successful distribution
            return {
                "status": "success",
                "partner_content_id": f"spotify_{product_id}",
                "metadata_mapping": spotify_metadata,
                "message": "Successfully distributed to Spotify"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Spotify distribution failed: {str(e)}"}
    
    async def _distribute_to_apple_music(self, product_id: str, metadata: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """Apple Music-specific distribution logic"""
        try:
            await asyncio.sleep(0.1)
            
            apple_metadata = {
                "songName": metadata.get("product_name"),
                "artistName": metadata.get("artist_name", "Unknown Artist"),
                "albumName": metadata.get("album_title", "Single"),
                "durationInMilliseconds": (metadata.get("duration_seconds", 0) * 1000),
                "isrc": metadata.get("isrc_code"),
                "recordLabel": metadata.get("record_label", "Independent")
            }
            
            return {
                "status": "success", 
                "partner_content_id": f"apple_{product_id}",
                "metadata_mapping": apple_metadata,
                "message": "Successfully distributed to Apple Music"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Apple Music distribution failed: {str(e)}"}
    
    async def _distribute_to_amazon_music(self, product_id: str, metadata: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """Amazon Music-specific distribution logic"""
        try:
            await asyncio.sleep(0.1)
            
            amazon_metadata = {
                "title": metadata.get("product_name"),
                "artist": metadata.get("artist_name", "Unknown Artist"),
                "album": metadata.get("album_title", "Single"),
                "duration": metadata.get("duration_seconds", 0),
                "isrc": metadata.get("isrc_code"),
                "label": metadata.get("record_label", "Independent")
            }
            
            return {
                "status": "success",
                "partner_content_id": f"amazon_{product_id}",
                "metadata_mapping": amazon_metadata,
                "message": "Successfully distributed to Amazon Music"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Amazon Music distribution failed: {str(e)}"}
    
    async def _distribute_to_youtube_music(self, product_id: str, metadata: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """YouTube Music-specific distribution logic"""
        try:
            await asyncio.sleep(0.1)
            
            youtube_metadata = {
                "snippet": {
                    "title": metadata.get("product_name"),
                    "description": f"Official audio by {metadata.get('artist_name', 'Unknown Artist')}",
                    "tags": [metadata.get("artist_name", ""), "music", "official"],
                    "categoryId": "10"  # Music category
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            
            return {
                "status": "success",
                "partner_content_id": f"youtube_{product_id}",
                "metadata_mapping": youtube_metadata,
                "message": "Successfully distributed to YouTube Music"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"YouTube Music distribution failed: {str(e)}"}
    
    async def _distribute_to_tidal(self, product_id: str, metadata: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """Tidal-specific distribution logic"""
        try:
            await asyncio.sleep(0.1)
            
            tidal_metadata = {
                "title": metadata.get("product_name"),
                "artist": metadata.get("artist_name", "Unknown Artist"),
                "album": metadata.get("album_title", "Single"),
                "duration": metadata.get("duration_seconds", 0),
                "isrc": metadata.get("isrc_code"),
                "quality": "HiFi"
            }
            
            return {
                "status": "success",
                "partner_content_id": f"tidal_{product_id}",
                "metadata_mapping": tidal_metadata,
                "message": "Successfully distributed to Tidal"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Tidal distribution failed: {str(e)}"}
    
    async def _generic_distribution(self, product_id: str, metadata: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """Generic distribution logic for other platforms"""
        try:
            await asyncio.sleep(0.1)
            
            return {
                "status": "success",
                "partner_content_id": f"{platform['name'].lower().replace(' ', '_')}_{product_id}",
                "metadata_mapping": metadata,
                "message": f"Successfully distributed to {platform['name']}"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"{platform['name']} distribution failed: {str(e)}"}
    
    async def get_industry_analytics(self, product_id: Optional[str] = None, partner_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive analytics across all industry partners"""
        try:
            query = {}
            if product_id:
                query["product_id"] = product_id
            if partner_id:
                query["partner_id"] = partner_id
            
            # Get analytics data
            cursor = self.db.industry_analytics.find(query)
            analytics = await cursor.to_list(None)
            
            # Aggregate data
            total_plays = sum(a.get("plays", 0) for a in analytics)
            total_streams = sum(a.get("streams", 0) for a in analytics)
            total_downloads = sum(a.get("downloads", 0) for a in analytics)
            total_revenue = sum(a.get("revenue", 0.0) for a in analytics)
            
            return {
                "total_analytics_records": len(analytics),
                "aggregated_data": {
                    "total_plays": total_plays,
                    "total_streams": total_streams,
                    "total_downloads": total_downloads,
                    "total_revenue": total_revenue
                },
                "platform_breakdown": await self._get_platform_breakdown(analytics),
                "territory_breakdown": await self._get_territory_breakdown(analytics)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving industry analytics: {str(e)}")
            return {}
    
    async def _get_platform_breakdown(self, analytics: List[Dict]) -> Dict[str, Any]:
        """Get analytics breakdown by platform"""
        platform_data = {}
        
        for record in analytics:
            partner_id = record.get("partner_id")
            if partner_id:
                partner = await self.db.industry_partners.find_one({"id": partner_id})
                if partner:
                    platform_name = partner["name"]
                    if platform_name not in platform_data:
                        platform_data[platform_name] = {
                            "plays": 0,
                            "streams": 0,
                            "downloads": 0,
                            "revenue": 0.0
                        }
                    
                    platform_data[platform_name]["plays"] += record.get("plays", 0)
                    platform_data[platform_name]["streams"] += record.get("streams", 0)
                    platform_data[platform_name]["downloads"] += record.get("downloads", 0)
                    platform_data[platform_name]["revenue"] += record.get("revenue", 0.0)
        
        return platform_data
    
    async def _get_territory_breakdown(self, analytics: List[Dict]) -> Dict[str, Any]:
        """Get analytics breakdown by territory"""
        territory_data = {}
        
        for record in analytics:
            territories = record.get("territories", {})
            for territory, plays in territories.items():
                if territory not in territory_data:
                    territory_data[territory] = 0
                territory_data[territory] += plays
        
        return territory_data
    
    async def sync_industry_data(self):
        """Sync data with all connected industry partners"""
        try:
            partners = await self.get_industry_partners()
            sync_results = {
                "total_partners": len(partners),
                "successful_syncs": 0,
                "failed_syncs": 0,
                "results": []
            }
            
            for partner in partners:
                try:
                    # Simulate data sync for different partner types
                    if partner["category"] == "streaming_platform":
                        await self._sync_streaming_data(partner)
                    elif partner["category"] == "radio_station":
                        await self._sync_radio_data(partner)
                    elif partner["category"] == "venue":
                        await self._sync_venue_data(partner)
                    
                    sync_results["successful_syncs"] += 1
                    sync_results["results"].append({
                        "partner": partner["name"],
                        "status": "success"
                    })
                    
                except Exception as e:
                    sync_results["failed_syncs"] += 1
                    sync_results["results"].append({
                        "partner": partner["name"],
                        "status": "error",
                        "message": str(e)
                    })
            
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing industry data: {str(e)}")
            raise
    
    async def _sync_streaming_data(self, partner: Dict[str, Any]):
        """Sync data with streaming platforms"""
        # Simulate analytics data collection
        await asyncio.sleep(0.05)
        
        # Generate sample analytics data
        analytics = IndustryAnalytics(
            partner_id=partner["id"],
            date=datetime.utcnow(),
            plays=1000,
            streams=950,
            revenue=4.5,
            territories={"US": 600, "UK": 200, "CA": 150}
        )
        
        await self.db.industry_analytics.insert_one(analytics.dict())
    
    async def _sync_radio_data(self, partner: Dict[str, Any]):
        """Sync data with radio stations"""
        await asyncio.sleep(0.05)
        
        analytics = IndustryAnalytics(
            partner_id=partner["id"],
            date=datetime.utcnow(),
            plays=50,
            revenue=25.0,
            territories={"US": 50}
        )
        
        await self.db.industry_analytics.insert_one(analytics.dict())
    
    async def _sync_venue_data(self, partner: Dict[str, Any]):
        """Sync data with venues"""
        await asyncio.sleep(0.05)
        
        # Venues don't typically have streaming data, but could have booking info
        pass
    
    async def get_industry_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for industry connections"""
        try:
            # Get partner counts by category and tier
            partners = await self.get_industry_partners()
            
            category_counts = {}
            tier_counts = {}
            
            for partner in partners:
                category = partner["category"]
                tier = partner["tier"]
                
                category_counts[category] = category_counts.get(category, 0) + 1
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            # Get distribution status
            distributions_cursor = self.db.content_distributions.find({})
            distributions = await distributions_cursor.to_list(None)
            
            distribution_status = {}
            for dist in distributions:
                status = dist["distribution_status"]
                distribution_status[status] = distribution_status.get(status, 0) + 1
            
            # Get recent analytics
            recent_analytics = await self.db.industry_analytics.find({}).sort("created_at", -1).limit(100).to_list(None)
            
            return {
                "partner_statistics": {
                    "total_partners": len(partners),
                    "by_category": category_counts,
                    "by_tier": tier_counts
                },
                "distribution_statistics": {
                    "total_distributions": len(distributions),
                    "by_status": distribution_status
                },
                "analytics_summary": {
                    "recent_records": len(recent_analytics),
                    "total_plays": sum(a.get("plays", 0) for a in recent_analytics),
                    "total_revenue": sum(a.get("revenue", 0.0) for a in recent_analytics)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    # IPI Number Management Methods
    async def get_ipi_numbers(self, entity_type: Optional[str] = None, role: Optional[str] = None) -> List[Dict]:
        """Get IPI numbers with optional filtering"""
        try:
            query = {"status": "active"}
            if entity_type:
                query["entity_type"] = entity_type
            if role:
                query["role"] = role
            
            cursor = self.db.ipi_numbers.find(query)
            ipi_numbers = await cursor.to_list(None)
            return ipi_numbers
            
        except Exception as e:
            logger.error(f"Error retrieving IPI numbers: {str(e)}")
            return []
    
    async def add_ipi_number(self, ipi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new IPI number"""
        try:
            # Check if IPI number already exists
            existing = await self.db.ipi_numbers.find_one({"ipi_number": ipi_data.get("ipi_number")})
            if existing:
                raise ValueError(f"IPI number {ipi_data.get('ipi_number')} already exists")
            
            ipi = IndustryIdentifier(**ipi_data)
            await self.db.ipi_numbers.insert_one(ipi.dict())
            
            return {"success": True, "ipi": ipi.dict()}
            
        except Exception as e:
            logger.error(f"Error adding IPI number: {str(e)}")
            raise
    
    async def update_ipi_number(self, ipi_number: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing IPI number"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.db.ipi_numbers.update_one(
                {"ipi_number": ipi_number},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise ValueError(f"IPI number {ipi_number} not found")
            
            return {"success": True, "message": "IPI number updated successfully"}
            
        except Exception as e:
            logger.error(f"Error updating IPI number: {str(e)}")
            raise
    
    async def get_ipi_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive IPI dashboard data"""
        try:
            # Get all IPI numbers
            ipi_numbers = await self.get_ipi_numbers()
            
            # Count by entity type
            entity_counts = {}
            role_counts = {}
            
            for ipi in ipi_numbers:
                entity_type = ipi.get("entity_type", "unknown")
                role = ipi.get("role", "unknown")
                
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                role_counts[role] = role_counts.get(role, 0) + 1
            
            return {
                "total_ipi_numbers": len(ipi_numbers),
                "by_entity_type": entity_counts,
                "by_role": role_counts,
                "big_mann_entertainment": {
                    "company_ipi": "813048171",
                    "individual_ipi": "578413032",
                    "status": "active"
                },
                "recent_ipi_numbers": ipi_numbers[-5:] if ipi_numbers else []
            }
            
        except Exception as e:
            logger.error(f"Error getting IPI dashboard data: {str(e)}")
            return {}