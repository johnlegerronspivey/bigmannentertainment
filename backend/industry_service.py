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
    IndustryAnalytics, RevenueTracking, ENTERTAINMENT_INDUSTRY_PARTNERS,
    IndustryIdentifier, BIG_MANN_INDUSTRY_IDENTIFIERS,
    MusicDataExchange, MDXTrack, MDXRightsManagement, MDXAnalytics, BIG_MANN_MDX_CONFIG,
    MechanicalLicensingCollective, MLCMusicalWork, MLCRoyaltyReport, MLCUsageData, MLCClaimsDispute, BIG_MANN_MLC_CONFIG
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
            
            # Initialize industry identifiers first
            await self.initialize_ipi_numbers()
            
            total_partners = 0
            
            # Add streaming platforms
            for tier, platforms in ENTERTAINMENT_INDUSTRY_PARTNERS["streaming_platforms"].items():
                for platform_data in platforms:
                    platform = StreamingPlatform(
                        category="streaming_platform",
                        tier=tier,
                        **platform_data
                    )
                    await self.db.industry_partners.insert_one(platform.dict())
                    total_partners += 1
            
            # Add photography services
            if "photography_services" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for service_type, services in ENTERTAINMENT_INDUSTRY_PARTNERS["photography_services"].items():
                    for service_data in services:
                        service = IndustryPartner(
                            category="photography_service",
                            tier=service_type,
                            **service_data
                        )
                        await self.db.industry_partners.insert_one(service.dict())
                        total_partners += 1
            
            # Add stock photography platforms
            if "stock_photography" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for tier, platforms in ENTERTAINMENT_INDUSTRY_PARTNERS["stock_photography"].items():
                    for platform_data in platforms:
                        platform = IndustryPartner(
                            category="stock_photography",
                            tier=tier,
                            **platform_data
                        )
                        await self.db.industry_partners.insert_one(platform.dict())
                        total_partners += 1
            
            # Add social media photography platforms
            if "social_media_photography" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for platform_type, platforms in ENTERTAINMENT_INDUSTRY_PARTNERS["social_media_photography"].items():
                    for platform_data in platforms:
                        platform = IndustryPartner(
                            category="social_media_photography",
                            tier=platform_type,
                            **platform_data
                        )
                        await self.db.industry_partners.insert_one(platform.dict())
                        total_partners += 1
            
            # Add video production services
            if "video_production" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for production_type, services in ENTERTAINMENT_INDUSTRY_PARTNERS["video_production"].items():
                    for service_data in services:
                        service = IndustryPartner(
                            category="video_production",
                            tier=production_type,
                            **service_data
                        )
                        await self.db.industry_partners.insert_one(service.dict())
                        total_partners += 1
            
            # Add podcast platforms
            if "podcast_platforms" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for platform_type, platforms in ENTERTAINMENT_INDUSTRY_PARTNERS["podcast_platforms"].items():
                    for platform_data in platforms:
                        platform = IndustryPartner(
                            category="podcast_platform",
                            tier=platform_type,
                            **platform_data
                        )
                        await self.db.industry_partners.insert_one(platform.dict())
                        total_partners += 1
            
            # Add live streaming platforms
            if "live_streaming" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for platform_type, platforms in ENTERTAINMENT_INDUSTRY_PARTNERS["live_streaming"].items():
                    for platform_data in platforms:
                        platform = IndustryPartner(
                            category="live_streaming",
                            tier=platform_type,
                            **platform_data
                        )
                        await self.db.industry_partners.insert_one(platform.dict())
                        total_partners += 1
            
            # Add gaming/esports platforms
            if "gaming_esports" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for platform_type, platforms in ENTERTAINMENT_INDUSTRY_PARTNERS["gaming_esports"].items():
                    for platform_data in platforms:
                        platform = IndustryPartner(
                            category="gaming_esports",
                            tier=platform_type,
                            **platform_data
                        )
                        await self.db.industry_partners.insert_one(platform.dict())
                        total_partners += 1
            
            # Add fashion photography services
            if "fashion_photography" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for photo_type, services in ENTERTAINMENT_INDUSTRY_PARTNERS["fashion_photography"].items():
                    for service_data in services:
                        service = IndustryPartner(
                            category="fashion_photography",
                            tier=photo_type,
                            **service_data
                        )
                        await self.db.industry_partners.insert_one(service.dict())
                        total_partners += 1

            # Add existing record labels
            if "record_labels" in ENTERTAINMENT_INDUSTRY_PARTNERS:
                for tier, labels in ENTERTAINMENT_INDUSTRY_PARTNERS["record_labels"].items():
                    for label_data in labels:
                        label = RecordLabel(
                            category="record_label",
                            tier=tier,
                            **label_data
                        )
                        await self.db.industry_partners.insert_one(label.dict())
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
    
    # Industry Identifiers Management Methods (IPI, ISNI, AARC)
    async def get_industry_identifiers(self, entity_type: Optional[str] = None, identifier_type: Optional[str] = None) -> List[Dict]:
        """Get industry identifiers with optional filtering"""
        try:
            query = {"status": "active"}
            if entity_type:
                query["entity_type"] = entity_type
            
            cursor = self.db.industry_identifiers.find(query)
            identifiers = await cursor.to_list(None)
            
            # Filter by identifier type if specified
            if identifier_type:
                filtered_identifiers = []
                for identifier in identifiers:
                    if identifier_type == "ipi" and identifier.get("ipi_number"):
                        filtered_identifiers.append(identifier)
                    elif identifier_type == "isni" and identifier.get("isni_number"):
                        filtered_identifiers.append(identifier)
                    elif identifier_type == "aarc" and identifier.get("aarc_number"):
                        filtered_identifiers.append(identifier)
                identifiers = filtered_identifiers
            
            return identifiers
            
        except Exception as e:
            logger.error(f"Error retrieving industry identifiers: {str(e)}")
            return []
    
    async def get_ipi_numbers(self, entity_type: Optional[str] = None, role: Optional[str] = None) -> List[Dict]:
        """Get IPI numbers with optional filtering (legacy method)"""
        try:
            query = {"status": "active", "ipi_number": {"$ne": None}}
            if entity_type:
                query["entity_type"] = entity_type
            if role:
                query["ipi_role"] = role
            
            cursor = self.db.industry_identifiers.find(query)
            identifiers = await cursor.to_list(None)
            return identifiers
            
        except Exception as e:
            logger.error(f"Error retrieving IPI numbers: {str(e)}")
            return []
    
    async def add_industry_identifier(self, identifier_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new industry identifier"""
        try:
            # Check if entity already exists
            existing = await self.db.industry_identifiers.find_one({"entity_name": identifier_data.get("entity_name")})
            if existing:
                raise ValueError(f"Entity {identifier_data.get('entity_name')} already exists")
            
            identifier = IndustryIdentifier(**identifier_data)
            await self.db.industry_identifiers.insert_one(identifier.dict())
            
            return {"success": True, "identifier": identifier.dict()}
            
        except Exception as e:
            logger.error(f"Error adding industry identifier: {str(e)}")
            raise
    
    async def add_ipi_number(self, ipi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new IPI number (legacy method)"""
        try:
            # Check if IPI number already exists
            existing = await self.db.industry_identifiers.find_one({"ipi_number": ipi_data.get("ipi_number")})
            if existing:
                raise ValueError(f"IPI number {ipi_data.get('ipi_number')} already exists")
            
            identifier = IndustryIdentifier(**ipi_data)
            await self.db.industry_identifiers.insert_one(identifier.dict())
            
            return {"success": True, "ipi": identifier.dict()}
            
        except Exception as e:
            logger.error(f"Error adding IPI number: {str(e)}")
            raise
    
    async def update_industry_identifier(self, entity_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing industry identifier"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.db.industry_identifiers.update_one(
                {"entity_name": entity_name},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Entity {entity_name} not found")
            
            return {"success": True, "message": "Industry identifier updated successfully"}
            
        except Exception as e:
            logger.error(f"Error updating industry identifier: {str(e)}")
            raise
    
    async def update_ipi_number(self, ipi_number: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing IPI number (legacy method)"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.db.industry_identifiers.update_one(
                {"ipi_number": ipi_number},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise ValueError(f"IPI number {ipi_number} not found")
            
            return {"success": True, "message": "IPI number updated successfully"}
            
        except Exception as e:
            logger.error(f"Error updating IPI number: {str(e)}")
            raise
    
    async def get_industry_identifiers_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive industry identifiers dashboard data"""
        try:
            # Get all industry identifiers
            identifiers = await self.get_industry_identifiers()
            
            # Count by entity type and identifier types
            entity_counts = {}
            ipi_count = 0
            isni_count = 0
            aarc_count = 0
            
            for identifier in identifiers:
                entity_type = identifier.get("entity_type", "unknown")
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                
                if identifier.get("ipi_number"):
                    ipi_count += 1
                if identifier.get("isni_number"):
                    isni_count += 1
                if identifier.get("aarc_number"):
                    aarc_count += 1
            
            return {
                "total_entities": len(identifiers),
                "by_entity_type": entity_counts,
                "identifier_counts": {
                    "ipi": ipi_count,
                    "isni": isni_count,
                    "aarc": aarc_count
                },
                "big_mann_entertainment": {
                    "company_ipi": "813048171",
                    "company_aarc": "RC00002057",
                    "individual_ipi": "578413032", 
                    "individual_isni": "0000000491551894",
                    "individual_aarc": "FA02933539",
                    "status": "active"
                },
                "recent_identifiers": identifiers[-5:] if identifiers else []
            }
            
        except Exception as e:
            logger.error(f"Error getting industry identifiers dashboard data: {str(e)}")
            return {}
    
    async def get_ipi_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive IPI dashboard data (legacy method)"""
        try:
            # Get all IPI numbers
            ipi_numbers = await self.get_ipi_numbers()
            
            # Count by entity type
            entity_counts = {}
            role_counts = {}
            
            for ipi in ipi_numbers:
                entity_type = ipi.get("entity_type", "unknown")
                role = ipi.get("ipi_role", "unknown")
                
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
            logger.error(f"Error getting industry identifiers dashboard data: {str(e)}")
            return {}
    
    # Enhanced Entertainment Industry Management Methods
    async def get_entertainment_partners_by_category(self, category: str, tier: Optional[str] = None) -> List[Dict]:
        """Get entertainment industry partners by category (photography, video, streaming, etc.)"""
        try:
            query = {"category": category, "status": "active"}
            if tier:
                query["tier"] = tier
            
            cursor = self.db.industry_partners.find(query)
            partners = await cursor.to_list(None)
            return partners
            
        except Exception as e:
            logger.error(f"Error retrieving entertainment partners: {str(e)}")
            return []
    
    async def get_photography_services(self, service_type: Optional[str] = None, price_range: Optional[str] = None) -> List[Dict]:
        """Get photography services with filtering options"""
        try:
            query = {"category": "photography_service", "status": "active"}
            if service_type:
                query["tier"] = service_type  # album_cover, promotional, event
            
            cursor = self.db.industry_partners.find(query)
            services = await cursor.to_list(None)
            
            # Filter by price range if specified
            if price_range:
                filtered_services = []
                for service in services:
                    if price_range.lower() in service.get("price_range", "").lower():
                        filtered_services.append(service)
                services = filtered_services
            
            return services
            
        except Exception as e:
            logger.error(f"Error retrieving photography services: {str(e)}")
            return []
    
    async def get_video_production_services(self, production_type: Optional[str] = None) -> List[Dict]:
        """Get video production services"""
        try:
            query = {"category": "video_production", "status": "active"}
            if production_type:
                query["tier"] = production_type  # music_videos, production_companies
            
            cursor = self.db.industry_partners.find(query)
            services = await cursor.to_list(None)
            return services
            
        except Exception as e:
            logger.error(f"Error retrieving video production services: {str(e)}")
            return []
    
    async def get_monetization_opportunities(self, content_type: str = "all") -> Dict[str, Any]:
        """Get comprehensive monetization opportunities across all entertainment platforms"""
        try:
            monetization_data = {}
            
            # Photography monetization
            photo_platforms = await self.get_entertainment_partners_by_category("stock_photography")
            photo_social = await self.get_entertainment_partners_by_category("social_media_photography")
            
            monetization_data["photography"] = {
                "stock_platforms": len(photo_platforms),
                "social_media": len(photo_social),
                "estimated_revenue_range": "$100-$10000/month",
                "top_platforms": [p["name"] for p in photo_platforms[:3]]
            }
            
            # Video monetization
            video_services = await self.get_entertainment_partners_by_category("video_production")
            streaming_platforms = await self.get_entertainment_partners_by_category("live_streaming")
            
            monetization_data["video"] = {
                "production_services": len(video_services),
                "streaming_platforms": len(streaming_platforms),
                "estimated_revenue_range": "$500-$50000/project",
                "top_platforms": [p["name"] for p in streaming_platforms[:3]]
            }
            
            # Audio/Music monetization (existing)
            streaming_services = await self.get_entertainment_partners_by_category("streaming_platform")
            podcast_platforms = await self.get_entertainment_partners_by_category("podcast_platform")
            
            monetization_data["audio"] = {
                "streaming_platforms": len(streaming_services),
                "podcast_platforms": len(podcast_platforms),
                "estimated_revenue_range": "$0.003-$0.005/stream",
                "top_platforms": [p["name"] for p in streaming_services[:3]]
            }
            
            # Gaming monetization
            gaming_platforms = await self.get_entertainment_partners_by_category("gaming_esports")
            
            monetization_data["gaming"] = {
                "platforms": len(gaming_platforms),
                "estimated_revenue_range": "$1000-$100000/license",
                "top_platforms": [p["name"] for p in gaming_platforms[:3]]
            }
            
            # Calculate total opportunities
            monetization_data["summary"] = {
                "total_platforms": len(photo_platforms) + len(streaming_platforms) + len(streaming_services) + len(gaming_platforms),
                "categories_covered": len(monetization_data) - 1,
                "estimated_monthly_potential": "$2000-$200000"
            }
            
            return monetization_data
            
        except Exception as e:
            logger.error(f"Error getting monetization opportunities: {str(e)}")
            return {}
    
    async def get_comprehensive_entertainment_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive entertainment industry dashboard with all categories"""
        try:
            dashboard_data = {}
            
            # Get counts for each category
            categories = [
                "photography_service", "stock_photography", "social_media_photography",
                "video_production", "podcast_platform", "live_streaming",
                "gaming_esports", "fashion_photography", "streaming_platform", "record_label"
            ]
            
            for category in categories:
                partners = await self.get_entertainment_partners_by_category(category)
                dashboard_data[category] = {
                    "count": len(partners),
                    "active_partners": len([p for p in partners if p.get("status") == "active"]),
                    "top_partners": [p["name"] for p in partners[:5]]
                }
            
            # Photography breakdown
            photography_services = await self.get_photography_services()
            dashboard_data["photography_breakdown"] = {
                "album_cover": len([p for p in photography_services if p.get("tier") == "album_cover"]),
                "promotional": len([p for p in photography_services if p.get("tier") == "promotional"]),
                "event": len([p for p in photography_services if p.get("tier") == "event"])
            }
            
            # Video production breakdown
            video_services = await self.get_video_production_services()
            dashboard_data["video_breakdown"] = {
                "music_videos": len([p for p in video_services if p.get("tier") == "music_videos"]),
                "production_companies": len([p for p in video_services if p.get("tier") == "production_companies"])
            }
            
            # Monetization summary
            monetization = await self.get_monetization_opportunities()
            dashboard_data["monetization_summary"] = monetization.get("summary", {})
            
            # Big Mann Entertainment comprehensive overview
            dashboard_data["big_mann_entertainment"] = {
                "total_industry_reach": sum([data["count"] for data in dashboard_data.values() if isinstance(data, dict) and "count" in data]),
                "content_distribution_channels": len(categories),
                "monetization_potential": "High across all entertainment verticals",
                "integrated_services": [
                    "Music Distribution", "Photography Services", "Video Production",
                    "Live Streaming", "Podcast Hosting", "Gaming Integration",
                    "Social Media Content", "Fashion Photography", "Stock Photography"
                ]
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive entertainment dashboard: {str(e)}")
            return {}
    
    # Music Data Exchange (MDX) Integration Methods
    async def initialize_mdx_integration(self) -> Dict[str, Any]:
        """Initialize Music Data Exchange integration for Big Mann Entertainment"""
        try:
            # Clear existing MDX configuration
            await self.db.mdx_configuration.delete_many({})
            
            # Initialize Big Mann Entertainment MDX configuration
            mdx_config = MusicDataExchange(**{
                "entity_name": "Big Mann Entertainment",
                "entity_type": "label",
                "metadata_schema": BIG_MANN_MDX_CONFIG["mdx_configuration"],
                "rights_information": BIG_MANN_MDX_CONFIG["rights_management"],
                "data_mapping": BIG_MANN_MDX_CONFIG["integration_features"],
                "sync_frequency": "real_time",
                "sync_status": "active",
                "ddex_compliant": True,
                "territories": ["US", "UK", "CA", "AU", "global"],
                "distribution_channels": BIG_MANN_MDX_CONFIG["mdx_configuration"]["distribution_channels"],
                "copyright_owners": [
                    {
                        "name": "Big Mann Entertainment",
                        "role": "label",
                        "percentage": 50.0,
                        "ipi_number": "813048171"
                    },
                    {
                        "name": "John LeGerron Spivey",
                        "role": "songwriter",
                        "percentage": 50.0,
                        "ipi_number": "578413032"
                    }
                ],
                "metadata": BIG_MANN_MDX_CONFIG["big_mann_specific"]
            })
            
            await self.db.mdx_configuration.insert_one(mdx_config.dict())
            
            logger.info("MDX integration initialized for Big Mann Entertainment")
            return {
                "success": True,
                "message": "Music Data Exchange integration initialized successfully",
                "mdx_config": mdx_config.dict()
            }
            
        except Exception as e:
            logger.error(f"Error initializing MDX integration: {str(e)}")
            raise
    
    async def sync_track_with_mdx(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync track metadata with Music Data Exchange"""
        try:
            # Create MDX track record
            mdx_track = MDXTrack(**{
                "title": track_data.get("title", "Untitled"),
                "artist_name": track_data.get("artist_name", "Big Mann Entertainment"),
                "album_title": track_data.get("album_title"),
                "track_number": track_data.get("track_number"),
                "duration": track_data.get("duration"),
                "release_date": track_data.get("release_date"),
                "isrc": track_data.get("isrc"),
                "iswc": track_data.get("iswc"),
                "upc": track_data.get("upc"),
                "songwriter_splits": [
                    {
                        "name": "John LeGerron Spivey",
                        "ipi_number": "578413032",
                        "percentage": 100.0,
                        "role": "songwriter"
                    }
                ],
                "publisher_splits": [
                    {
                        "name": "Big Mann Entertainment",
                        "ipi_number": "813048171",
                        "percentage": 100.0,
                        "role": "publisher"
                    }
                ],
                "big_mann_release": True,
                "rights_clearance_status": "cleared",
                "distribution_rights": {
                    "territories": ["global"],
                    "channels": ["streaming", "download", "physical"],
                    "term": "perpetual"
                },
                "monetization_strategy": {
                    "streaming_optimization": True,
                    "sync_licensing": True,
                    "mechanical_licensing": True,
                    "performance_royalties": True
                }
            })
            
            # Store track in database
            await self.db.mdx_tracks.insert_one(mdx_track.dict())
            
            # Simulate MDX API sync (in real implementation, this would call MDX API)
            sync_result = {
                "mdx_track_id": f"MDX{mdx_track.id[:8]}",
                "sync_status": "success",
                "metadata_completeness": 95.0,
                "rights_cleared": True,
                "distribution_approved": True
            }
            
            # Update track with MDX results
            await self.db.mdx_tracks.update_one(
                {"id": mdx_track.id},
                {"$set": {
                    "mdx_track_id": sync_result["mdx_track_id"],
                    "mdx_metadata": sync_result,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "success": True,
                "track_id": mdx_track.id,
                "mdx_track_id": sync_result["mdx_track_id"],
                "sync_result": sync_result,
                "message": "Track successfully synced with Music Data Exchange"
            }
            
        except Exception as e:
            logger.error(f"Error syncing track with MDX: {str(e)}")
            raise
    
    async def get_mdx_tracks(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """Get MDX tracks with optional filtering"""
        try:
            query = {}
            if filters:
                if filters.get("artist_name"):
                    query["artist_name"] = {"$regex": filters["artist_name"], "$options": "i"}
                if filters.get("big_mann_release"):
                    query["big_mann_release"] = filters["big_mann_release"]
                if filters.get("rights_clearance_status"):
                    query["rights_clearance_status"] = filters["rights_clearance_status"]
            
            cursor = self.db.mdx_tracks.find(query)
            tracks = await cursor.to_list(None)
            return tracks
            
        except Exception as e:
            logger.error(f"Error retrieving MDX tracks: {str(e)}")
            return []
    
    async def manage_mdx_rights(self, rights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage rights through Music Data Exchange"""
        try:
            mdx_rights = MDXRightsManagement(**{
                "rights_type": rights_data.get("rights_type", "publishing"),
                "rights_holder": rights_data.get("rights_holder", "Big Mann Entertainment"),
                "rights_percentage": rights_data.get("rights_percentage", 100.0),
                "territories": rights_data.get("territories", ["global"]),
                "rights_start_date": rights_data.get("rights_start_date", datetime.utcnow()),
                "rights_end_date": rights_data.get("rights_end_date"),
                "track_ids": rights_data.get("track_ids", []),
                "clearance_status": "active",
                "licensing_terms": {
                    "mechanical_rate": "statutory",
                    "performance_rate": "standard",
                    "sync_rate": "negotiable"
                },
                "royalty_rates": {
                    "mechanical": 0.091,  # US statutory rate
                    "performance": 0.50,  # Performance share
                    "sync": "negotiable"
                },
                "mdx_sync_status": "synced"
            })
            
            await self.db.mdx_rights.insert_one(mdx_rights.dict())
            
            return {
                "success": True,
                "rights_id": mdx_rights.id,
                "message": "Rights successfully managed through MDX",
                "rights_details": mdx_rights.dict()
            }
            
        except Exception as e:
            logger.error(f"Error managing MDX rights: {str(e)}")
            raise
    
    async def get_mdx_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive MDX dashboard analytics"""
        try:
            # Get MDX tracks and rights data
            tracks = await self.get_mdx_tracks()
            
            # Calculate analytics
            total_tracks = len(tracks)
            big_mann_tracks = len([t for t in tracks if t.get("big_mann_release", False)])
            cleared_tracks = len([t for t in tracks if t.get("rights_clearance_status") == "cleared"])
            
            # Get rights information
            rights_cursor = self.db.mdx_rights.find({})
            rights = await rights_cursor.to_list(None)
            
            # Create analytics record
            analytics = MDXAnalytics(**{
                "report_date": datetime.utcnow(),
                "report_type": "real_time",
                "metadata_completeness": 95.0 if tracks else 0.0,
                "rights_clearance_rate": (cleared_tracks / total_tracks * 100) if total_tracks > 0 else 0.0,
                "sync_success_rate": 98.5,  # Mock data - would be calculated from actual sync logs
                "total_tracks_managed": total_tracks,
                "total_rights_cleared": cleared_tracks,
                "total_distribution_channels": len(BIG_MANN_MDX_CONFIG["mdx_configuration"]["distribution_channels"]),
                "total_territories_covered": len(BIG_MANN_MDX_CONFIG["mdx_configuration"]["territories"]),
                "estimated_revenue_impact": total_tracks * 1500.0,  # Estimated revenue per track
                "rights_revenue_tracked": len(rights) * 2500.0,
                "metadata_optimization_savings": total_tracks * 150.0,
                "big_mann_tracks": big_mann_tracks,
                "big_mann_revenue_impact": big_mann_tracks * 2000.0,
                "sync_performance": {
                    "average_sync_time": "2.3 seconds",
                    "success_rate": "98.5%",
                    "error_rate": "1.5%"
                },
                "error_rates": {
                    "metadata_errors": 2.1,
                    "rights_conflicts": 0.5,
                    "sync_failures": 1.5
                }
            })
            
            # Store analytics
            await self.db.mdx_analytics.insert_one(analytics.dict())
            
            return {
                "analytics": analytics.dict(),
                "big_mann_entertainment": {
                    "total_mdx_tracks": big_mann_tracks,
                    "rights_managed": len(rights),
                    "revenue_optimization": f"${analytics.big_mann_revenue_impact:,.2f}",
                    "metadata_quality": f"{analytics.metadata_completeness}%",
                    "distribution_reach": f"{analytics.total_distribution_channels} platforms",
                    "territory_coverage": f"{analytics.total_territories_covered} territories"
                },
                "platform_integration": {
                    "mdx_status": "fully_integrated",
                    "real_time_sync": True,
                    "automated_rights_clearance": True,
                    "cross_platform_optimization": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting MDX dashboard data: {str(e)}")
            return {}
    
    async def process_mdx_bulk_upload(self, tracks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process bulk upload of tracks to MDX"""
        try:
            processed_tracks = []
            failed_tracks = []
            
            for track_data in tracks_data:
                try:
                    result = await self.sync_track_with_mdx(track_data)
                    processed_tracks.append(result)
                except Exception as e:
                    failed_tracks.append({
                        "track": track_data.get("title", "Unknown"),
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "total_submitted": len(tracks_data),
                "successfully_processed": len(processed_tracks),
                "failed": len(failed_tracks),
                "processed_tracks": processed_tracks,
                "failed_tracks": failed_tracks,
                "message": f"Bulk upload completed: {len(processed_tracks)} successful, {len(failed_tracks)} failed"
            }
            
        except Exception as e:
            logger.error(f"Error processing MDX bulk upload: {str(e)}")
            raise
    
    # Mechanical Licensing Collective (MLC) Integration Methods
    async def initialize_mlc_integration(self) -> Dict[str, Any]:
        """Initialize Mechanical Licensing Collective integration for Big Mann Entertainment"""
        try:
            # Clear existing MLC configuration
            await self.db.mlc_configuration.delete_many({})
            
            # Initialize Big Mann Entertainment MLC configuration
            mlc_config = MechanicalLicensingCollective(**{
                "entity_name": "Big Mann Entertainment",
                "entity_type": "publisher",
                "mlc_member_status": "active",
                "registration_date": datetime.utcnow(),
                "member_number": "BME813048171",  # Based on IPI number
                "contact_info": {
                    "business_name": "Big Mann Entertainment",
                    "address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
                    "phone": "334-669-8638",
                    "email": "info@bigmannentertainment.com"
                },
                "business_info": BIG_MANN_MLC_CONFIG["business_configuration"],
                "tax_info": {
                    "tax_id": "12800",
                    "business_type": "Sound Recording Industries",
                    "naics_code": "512200"
                },
                "publishing_rights": BIG_MANN_MLC_CONFIG["publishing_information"],
                "mechanical_rights_share": 50.0,  # 50% mechanical rights
                "api_access_level": "premium",
                "automated_reporting": True,
                "royalty_collection_enabled": True,
                "metadata_sync_enabled": True,
                "dispute_management_enabled": True,
                "metadata": BIG_MANN_MLC_CONFIG["integration_features"]
            })
            
            await self.db.mlc_configuration.insert_one(mlc_config.dict())
            
            logger.info("MLC integration initialized for Big Mann Entertainment")
            return {
                "success": True,
                "message": "Mechanical Licensing Collective integration initialized successfully",
                "mlc_config": mlc_config.dict()
            }
            
        except Exception as e:
            logger.error(f"Error initializing MLC integration: {str(e)}")
            raise
    
    async def register_musical_work_with_mlc(self, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a musical work with the Mechanical Licensing Collective"""
        try:
            # Create MLC musical work record
            mlc_work = MLCMusicalWork(**{
                "work_title": work_data.get("work_title", "Untitled Work"),
                "alternative_titles": work_data.get("alternative_titles", []),
                "iswc": work_data.get("iswc"),
                "publishers": [
                    {
                        "name": "Big Mann Entertainment",
                        "ipi_number": "813048171",
                        "share_percentage": 50.0,
                        "role": "publisher",
                        "admin_percentage": 100.0
                    }
                ],
                "songwriters": [
                    {
                        "name": "John LeGerron Spivey",
                        "ipi_number": "578413032",
                        "isni_number": "0000000491551894",
                        "share_percentage": 50.0,
                        "role": "songwriter_composer"
                    }
                ],
                "mechanical_rights_share": {
                    "Big Mann Entertainment": 50.0,
                    "John LeGerron Spivey": 50.0
                },
                "rights_start_date": work_data.get("rights_start_date", datetime.utcnow()),
                "big_mann_work": True,
                "submission_status": "submitted",
                "last_submission_date": datetime.utcnow(),
                "mlc_registration_number": f"MLC{work_data.get('work_title', 'Work')[:6].upper()}{str(datetime.utcnow().year)}",
                "internal_catalog_number": work_data.get("catalog_number")
            })
            
            # Store work in database
            await self.db.mlc_works.insert_one(mlc_work.dict())
            
            # Simulate MLC registration response
            registration_result = {
                "mlc_work_id": f"MLC{mlc_work.id[:8]}",
                "registration_status": "accepted",
                "registration_number": mlc_work.mlc_registration_number,
                "effective_date": datetime.utcnow().isoformat(),
                "rights_confirmed": True
            }
            
            # Update work with MLC results
            await self.db.mlc_works.update_one(
                {"id": mlc_work.id},
                {"$set": {
                    "mlc_work_id": registration_result["mlc_work_id"],
                    "submission_status": "accepted",
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "success": True,
                "work_id": mlc_work.id,
                "mlc_work_id": registration_result["mlc_work_id"],
                "registration_result": registration_result,
                "message": f"Musical work '{mlc_work.work_title}' successfully registered with MLC"
            }
            
        except Exception as e:
            logger.error(f"Error registering musical work with MLC: {str(e)}")
            raise
    
    async def get_mlc_works(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """Get MLC registered works with optional filtering"""
        try:
            query = {}
            if filters:
                if filters.get("work_title"):
                    query["work_title"] = {"$regex": filters["work_title"], "$options": "i"}
                if filters.get("big_mann_work"):
                    query["big_mann_work"] = filters["big_mann_work"]
                if filters.get("submission_status"):
                    query["submission_status"] = filters["submission_status"]
            
            cursor = self.db.mlc_works.find(query)
            works = await cursor.to_list(None)
            
            # Convert ObjectId to string for JSON serialization
            for work in works:
                if '_id' in work:
                    work['_id'] = str(work['_id'])
            
            return works
            
        except Exception as e:
            logger.error(f"Error retrieving MLC works: {str(e)}")
            return []
    
    async def process_mlc_royalty_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MLC royalty report for Big Mann Entertainment"""
        try:
            # Get Big Mann Entertainment works for royalty calculation
            big_mann_works = await self.get_mlc_works({"big_mann_work": True})
            
            # Create royalty report
            royalty_report = MLCRoyaltyReport(**{
                "report_period_start": report_data.get("period_start", datetime.utcnow().replace(day=1)),
                "report_period_end": report_data.get("period_end", datetime.utcnow()),
                "report_type": report_data.get("report_type", "monthly"),
                "total_royalties_collected": report_data.get("total_collected", 0.0),
                "administrative_fees": report_data.get("admin_fees", 0.0),
                "publisher_distributions": [
                    {
                        "publisher_name": "Big Mann Entertainment",
                        "ipi_number": "813048171",
                        "amount": report_data.get("total_collected", 0.0) * 0.5,  # 50% share
                        "works_count": len(big_mann_works),
                        "distribution_method": "direct_deposit"
                    }
                ],
                "songwriter_distributions": [
                    {
                        "songwriter_name": "John LeGerron Spivey",
                        "ipi_number": "578413032",
                        "isni_number": "0000000491551894",
                        "amount": report_data.get("total_collected", 0.0) * 0.5,  # 50% share
                        "works_count": len(big_mann_works),
                        "distribution_method": "direct_deposit"
                    }
                ],
                "digital_service_providers": ["Spotify", "Apple Music", "Amazon Music", "YouTube Music"],
                "usage_data": {
                    "total_streams": report_data.get("total_streams", 0),
                    "unique_tracks": len(big_mann_works),
                    "average_per_stream": 0.00091  # Approximate mechanical rate
                },
                "processing_status": "completed",
                "distribution_date": datetime.utcnow(),
                "big_mann_royalties": report_data.get("total_collected", 0.0),
                "big_mann_works_count": len(big_mann_works)
            })
            
            # Calculate net distribution
            royalty_report.total_royalties_distributed = (
                royalty_report.total_royalties_collected - royalty_report.administrative_fees
            )
            royalty_report.net_distribution = royalty_report.total_royalties_distributed
            
            # Store report in database
            await self.db.mlc_royalty_reports.insert_one(royalty_report.dict())
            
            return {
                "success": True,
                "report_id": royalty_report.id,
                "total_distributed": royalty_report.net_distribution,
                "big_mann_share": royalty_report.big_mann_royalties,
                "works_count": len(big_mann_works),
                "message": "MLC royalty report processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing MLC royalty report: {str(e)}")
            raise
    
    async def match_usage_data_to_works(self, usage_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Match DSP usage data to registered MLC works"""
        try:
            matched_count = 0
            unmatched_count = 0
            total_royalties = 0.0
            
            for usage_data in usage_data_list:
                try:
                    # Create usage data record
                    mlc_usage = MLCUsageData(**{
                        "track_title": usage_data.get("track_title", "Unknown"),
                        "artist_name": usage_data.get("artist_name", "Unknown"),
                        "album_title": usage_data.get("album_title"),
                        "isrc": usage_data.get("isrc"),
                        "dsp_name": usage_data.get("dsp_name", "Unknown DSP"),
                        "play_count": usage_data.get("play_count", 0),
                        "stream_date": usage_data.get("stream_date", datetime.utcnow()),
                        "revenue_generated": usage_data.get("revenue", 0.0),
                        "mechanical_royalty_due": usage_data.get("revenue", 0.0) * 0.091,  # Mechanical rate
                        "territory": usage_data.get("territory", "US")
                    })
                    
                    # Attempt to match with Big Mann Entertainment works
                    big_mann_works = await self.get_mlc_works({"big_mann_work": True})
                    matched_work = None
                    
                    for work in big_mann_works:
                        # Simple matching logic (would be more sophisticated in production)
                        if (mlc_usage.track_title.lower() in work.get("work_title", "").lower() or
                            work.get("work_title", "").lower() in mlc_usage.track_title.lower()):
                            matched_work = work
                            break
                    
                    if matched_work:
                        mlc_usage.matched_work_id = matched_work["id"]
                        mlc_usage.matching_confidence = 0.85  # High confidence match
                        mlc_usage.matching_status = "matched"
                        mlc_usage.publisher_share = {"Big Mann Entertainment": 50.0}
                        mlc_usage.songwriter_share = {"John LeGerron Spivey": 50.0}
                        matched_count += 1
                    else:
                        mlc_usage.matching_status = "unmatched"
                        unmatched_count += 1
                    
                    total_royalties += mlc_usage.mechanical_royalty_due
                    
                    # Store usage data
                    await self.db.mlc_usage_data.insert_one(mlc_usage.dict())
                    
                except Exception as usage_error:
                    logger.error(f"Error processing usage data item: {str(usage_error)}")
                    unmatched_count += 1
            
            return {
                "success": True,
                "total_processed": len(usage_data_list),
                "matched_count": matched_count,
                "unmatched_count": unmatched_count,
                "total_royalties_calculated": total_royalties,
                "matching_rate": (matched_count / len(usage_data_list) * 100) if usage_data_list else 0,
                "message": f"Processed {len(usage_data_list)} usage records with {matched_count} matches"
            }
            
        except Exception as e:
            logger.error(f"Error matching usage data to works: {str(e)}")
            raise
    
    async def get_mlc_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive MLC dashboard analytics"""
        try:
            # Get MLC works and reports data
            works = await self.get_mlc_works({"big_mann_work": True})
            
            # Get royalty reports
            reports_cursor = self.db.mlc_royalty_reports.find({})
            reports = await reports_cursor.to_list(None)
            
            # Get usage data
            usage_cursor = self.db.mlc_usage_data.find({"matching_status": "matched"})
            usage_data = await usage_cursor.to_list(None)
            
            # Calculate analytics
            total_works = len(works)
            total_royalties = sum([report.get("big_mann_royalties", 0.0) for report in reports])
            matched_usage_count = len(usage_data)
            
            # Get unmatched usage for matching rate
            unmatched_cursor = self.db.mlc_usage_data.find({"matching_status": "unmatched"})
            unmatched_usage = await unmatched_cursor.to_list(None)
            total_usage = matched_usage_count + len(unmatched_usage)
            matching_rate = (matched_usage_count / total_usage * 100) if total_usage > 0 else 0
            
            return {
                "mlc_integration_status": {
                    "member_status": "Active Publisher",
                    "registration_status": "Fully Registered",
                    "api_integration": "Connected",
                    "automated_processing": "Enabled"
                },
                "works_management": {
                    "total_registered_works": total_works,
                    "active_works": len([w for w in works if w.get("status") == "active"]),
                    "pending_registrations": len([w for w in works if w.get("submission_status") == "pending"]),
                    "registration_success_rate": "98.5%"
                },
                "royalty_collection": {
                    "total_royalties_collected": total_royalties,
                    "monthly_average": total_royalties / max(len(reports), 1),
                    "distribution_frequency": "Monthly",
                    "payment_method": "Direct Deposit"
                },
                "usage_matching": {
                    "total_usage_records": total_usage,
                    "matched_records": matched_usage_count,
                    "unmatched_records": len(unmatched_usage),
                    "matching_rate": f"{matching_rate:.1f}%"
                },
                "big_mann_entertainment": {
                    "publisher_ipi": "813048171",
                    "songwriter_ipi": "578413032",
                    "isni_number": "0000000491551894",
                    "mechanical_rights_share": "50%",
                    "total_catalog_value": f"${total_royalties:,.2f}",
                    "monthly_distribution": f"${total_royalties / max(len(reports), 1):,.2f}"
                },
                "platform_performance": {
                    "spotify_streams": sum([u.get("play_count", 0) for u in usage_data if u.get("dsp_name") == "Spotify"]),
                    "apple_music_streams": sum([u.get("play_count", 0) for u in usage_data if u.get("dsp_name") == "Apple Music"]),
                    "total_streams": sum([u.get("play_count", 0) for u in usage_data]),
                    "revenue_per_stream": 0.00091
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting MLC dashboard data: {str(e)}")
            return {}
    
    async def submit_mlc_claim_or_dispute(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a claim or dispute to MLC"""
        try:
            mlc_claim = MLCClaimsDispute(**{
                "claim_type": claim_data.get("claim_type", "ownership_claim"),
                "work_title": claim_data.get("work_title", "Unknown Work"),
                "work_id": claim_data.get("work_id"),
                "claimant_name": claim_data.get("claimant_name", "Big Mann Entertainment"),
                "claimant_type": claim_data.get("claimant_type", "publisher"),
                "claimed_rights_percentage": claim_data.get("rights_percentage", 50.0),
                "effective_date": claim_data.get("effective_date", datetime.utcnow()),
                "claim_description": claim_data.get("description", "Rights ownership claim"),
                "big_mann_involvement": True,
                "internal_reference": claim_data.get("internal_ref"),
                "affected_royalties": claim_data.get("affected_amount", 0.0)
            })
            
            await self.db.mlc_claims.insert_one(mlc_claim.dict())
            
            return {
                "success": True,
                "claim_id": mlc_claim.id,
                "mlc_claim_id": f"CLAIM{mlc_claim.id[:8]}",
                "claim_status": mlc_claim.claim_status,
                "message": f"Claim submitted successfully for '{mlc_claim.work_title}'"
            }
            
        except Exception as e:
            logger.error(f"Error submitting MLC claim: {str(e)}")
            raise