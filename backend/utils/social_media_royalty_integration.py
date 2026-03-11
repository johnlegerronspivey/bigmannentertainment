"""
Social Media Royalty Integration Service
Connects Social Media Phases 5-10 with Real-Time Royalty Engine for automated royalty processing
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import uuid

from royalty_engine_core import (
    royalty_engine,
    TransactionEvent,
    RevenueSource,
    MonetizationType
)

logger = logging.getLogger(__name__)

class SocialMediaRoyaltyProcessor:
    """Process social media monetization events for royalty calculation"""
    
    def __init__(self):
        self.royalty_engine = royalty_engine
        
        # Social media platform revenue share rates (example rates)
        self.platform_revenue_shares = {
            "youtube": {
                "ad_revenue_share": Decimal("0.55"),  # YouTube shares 55% with creators
                "premium_revenue_share": Decimal("0.55"),
                "super_chat_share": Decimal("0.70")
            },
            "tiktok": {
                "creator_fund_share": Decimal("0.80"),  # TikTok Creator Fund
                "live_gift_share": Decimal("0.50"),
                "brand_partnership_share": Decimal("1.00")  # Full amount goes to creator
            },
            "instagram": {
                "reels_play_bonus": Decimal("1.00"),
                "brand_content_share": Decimal("1.00"),
                "live_badge_share": Decimal("0.95")
            },
            "facebook": {
                "ad_breaks_share": Decimal("0.55"),
                "fan_subscription_share": Decimal("0.70"),
                "stars_share": Decimal("0.95")
            },
            "twitter": {
                "super_follows_share": Decimal("0.70"),
                "tip_jar_share": Decimal("0.97"),
                "spaces_monetization": Decimal("0.80")
            },
            "twitch": {
                "subscription_share": Decimal("0.50"),
                "bits_share": Decimal("1.00"),
                "ad_revenue_share": Decimal("0.50")
            }
        }
        
        # Asset mapping - maps social media content to music assets
        self.asset_mappings = {}  # Will be populated from database
    
    async def process_social_media_monetization(
        self,
        platform: str,
        content_id: str,
        monetization_type: str,
        gross_amount: Decimal,
        user_id: str,
        territory: str = "US",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Process social media monetization event and trigger royalty calculation"""
        
        try:
            # Find associated music asset
            asset_id = await self._find_associated_asset(platform, content_id, user_id)
            if not asset_id:
                logger.warning(f"No associated music asset found for {platform} content {content_id}")
                return None
            
            # Calculate platform fees and net revenue
            net_revenue = await self._calculate_net_revenue(platform, monetization_type, gross_amount)
            
            # Map social media monetization to royalty engine types
            revenue_source = RevenueSource.SOCIAL_MEDIA
            royalty_monetization_type = self._map_monetization_type(monetization_type)
            
            # Create transaction event
            transaction_event = TransactionEvent(
                asset_id=asset_id,
                platform=platform,
                territory=territory,
                user_id=user_id,
                revenue_source=revenue_source,
                monetization_type=royalty_monetization_type,
                gross_revenue=net_revenue,  # Use net revenue after platform fees
                currency="USD",
                platform_fee_rate=Decimal("0.0"),  # Already deducted
                metadata={
                    "original_content_id": content_id,
                    "social_media_monetization_type": monetization_type,
                    "original_gross_amount": float(gross_amount),
                    **(metadata or {})
                }
            )
            
            # Process through royalty engine
            calculation = await self.royalty_engine.process_transaction_event(transaction_event)
            
            logger.info(f"Processed social media royalty for asset {asset_id}: ${calculation.total_royalty}")
            return calculation.id
            
        except Exception as e:
            logger.error(f"Error processing social media monetization: {str(e)}")
            return None
    
    async def _find_associated_asset(self, platform: str, content_id: str, user_id: str) -> Optional[str]:
        """Find the music asset associated with social media content"""
        
        # Try exact mapping first
        mapping_key = f"{platform}:{content_id}"
        if mapping_key in self.asset_mappings:
            return self.asset_mappings[mapping_key]
        
        # Query database for content mappings
        try:
            mapping = await self.royalty_engine.db.social_media_mappings.find_one({
                "platform": platform,
                "content_id": content_id,
                "active": True
            })
            
            if mapping:
                return mapping["asset_id"]
            
            # Try to find by user-asset association
            user_assets = await self.royalty_engine.db.user_assets.find({
                "user_id": user_id,
                "active": True
            }).to_list(length=None)
            
            if user_assets:
                # For now, return the first asset - in production, use more sophisticated matching
                return user_assets[0]["asset_id"]
                
        except Exception as e:
            logger.error(f"Error finding associated asset: {str(e)}")
        
        return None
    
    async def _calculate_net_revenue(self, platform: str, monetization_type: str, gross_amount: Decimal) -> Decimal:
        """Calculate net revenue after platform fees"""
        
        platform_rates = self.platform_revenue_shares.get(platform.lower(), {})
        
        # Find the appropriate revenue share rate
        share_rate = None
        for rate_key, rate_value in platform_rates.items():
            if monetization_type.lower() in rate_key.lower():
                share_rate = rate_value
                break
        
        # Default to 70% if no specific rate found
        if share_rate is None:
            share_rate = Decimal("0.70")
            logger.warning(f"No specific rate found for {platform} {monetization_type}, using default 70%")
        
        net_revenue = gross_amount * share_rate
        return net_revenue
    
    def _map_monetization_type(self, social_monetization_type: str) -> MonetizationType:
        """Map social media monetization types to royalty engine types"""
        
        mapping = {
            "ad_revenue": MonetizationType.AD_SUPPORTED,
            "subscription": MonetizationType.SUBSCRIPTION,
            "premium": MonetizationType.SUBSCRIPTION,
            "tips": MonetizationType.PURCHASE,
            "donations": MonetizationType.PURCHASE,
            "brand_partnership": MonetizationType.SYNC_FEE,
            "sponsored_content": MonetizationType.SYNC_FEE,
            "creator_fund": MonetizationType.PERFORMANCE_ROYALTY,
            "live_streaming": MonetizationType.PERFORMANCE_ROYALTY
        }
        
        for key, value in mapping.items():
            if key in social_monetization_type.lower():
                return value
        
        # Default to ad-supported
        return MonetizationType.AD_SUPPORTED
    
    async def create_asset_mapping(self, platform: str, content_id: str, asset_id: str, user_id: str) -> bool:
        """Create mapping between social media content and music asset"""
        
        try:
            mapping = {
                "id": str(uuid.uuid4()),
                "platform": platform,
                "content_id": content_id,
                "asset_id": asset_id,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "active": True,
                "verified": False  # Requires manual verification
            }
            
            await self.royalty_engine.db.social_media_mappings.insert_one(mapping)
            
            # Cache the mapping
            self.asset_mappings[f"{platform}:{content_id}"] = asset_id
            
            logger.info(f"Created asset mapping: {platform}:{content_id} -> {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating asset mapping: {str(e)}")
            return False
    
    async def batch_process_social_media_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple social media events in batch"""
        
        results = []
        total_revenue = Decimal("0")
        successful_count = 0
        
        for event in events:
            try:
                calculation_id = await self.process_social_media_monetization(
                    platform=event["platform"],
                    content_id=event["content_id"],
                    monetization_type=event["monetization_type"],
                    gross_amount=Decimal(str(event["gross_amount"])),
                    user_id=event["user_id"],
                    territory=event.get("territory", "US"),
                    metadata=event.get("metadata")
                )
                
                if calculation_id:
                    results.append({
                        "event_id": event.get("id", str(uuid.uuid4())),
                        "status": "success",
                        "calculation_id": calculation_id
                    })
                    successful_count += 1
                    total_revenue += Decimal(str(event["gross_amount"]))
                else:
                    results.append({
                        "event_id": event.get("id", str(uuid.uuid4())),
                        "status": "skipped",
                        "reason": "No associated asset found"
                    })
                    
            except Exception as e:
                results.append({
                    "event_id": event.get("id", str(uuid.uuid4())),
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "total_events": len(events),
            "successful_events": successful_count,
            "failed_events": len([r for r in results if r["status"] == "error"]),
            "skipped_events": len([r for r in results if r["status"] == "skipped"]),
            "total_revenue_processed": float(total_revenue),
            "results": results
        }
    
    async def get_social_media_analytics(self, asset_id: str, days: int = 30) -> Dict[str, Any]:
        """Get social media royalty analytics for an asset"""
        
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Get social media transactions for the asset
            transactions = await self.royalty_engine.collection_events.find({
                "asset_id": asset_id,
                "revenue_source": "social_media",
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }).to_list(length=None)
            
            if not transactions:
                return {
                    "asset_id": asset_id,
                    "period_days": days,
                    "total_revenue": 0,
                    "total_events": 0,
                    "platform_breakdown": {},
                    "monetization_breakdown": {}
                }
            
            # Analyze the data
            platform_revenue = {}
            monetization_revenue = {}
            total_revenue = Decimal("0")
            
            for tx in transactions:
                platform = tx["platform"]
                monetization_type = tx["monetization_type"]
                revenue = Decimal(str(tx["gross_revenue"]))
                
                # Platform breakdown
                if platform not in platform_revenue:
                    platform_revenue[platform] = Decimal("0")
                platform_revenue[platform] += revenue
                
                # Monetization type breakdown
                if monetization_type not in monetization_revenue:
                    monetization_revenue[monetization_type] = Decimal("0")
                monetization_revenue[monetization_type] += revenue
                
                total_revenue += revenue
            
            return {
                "asset_id": asset_id,
                "period_days": days,
                "total_revenue": float(total_revenue),
                "total_events": len(transactions),
                "average_revenue_per_event": float(total_revenue / len(transactions)),
                "platform_breakdown": {k: float(v) for k, v in platform_revenue.items()},
                "monetization_breakdown": {k: float(v) for k, v in monetization_revenue.items()},
                "top_platform": max(platform_revenue.items(), key=lambda x: x[1])[0] if platform_revenue else None,
                "top_monetization": max(monetization_revenue.items(), key=lambda x: x[1])[0] if monetization_revenue else None
            }
            
        except Exception as e:
            logger.error(f"Error getting social media analytics: {str(e)}")
            return {"error": str(e)}

class StreamingPlatformIntegration:
    """Integration with streaming platforms for automated royalty processing"""
    
    def __init__(self):
        self.social_processor = SocialMediaRoyaltyProcessor()
        
        # Streaming platform APIs configuration
        self.platform_configs = {
            "spotify": {
                "api_base": "https://api.spotify.com/v1",
                "royalty_rate": Decimal("0.003"),  # ~$0.003 per stream
                "minimum_payout": Decimal("0.01")
            },
            "apple_music": {
                "api_base": "https://api.music.apple.com/v1",
                "royalty_rate": Decimal("0.007"),  # ~$0.007 per stream
                "minimum_payout": Decimal("0.01")
            },
            "youtube_music": {
                "api_base": "https://www.googleapis.com/youtube/v3",
                "royalty_rate": Decimal("0.001"),  # ~$0.001 per stream
                "minimum_payout": Decimal("0.01")
            }
        }
    
    async def process_streaming_royalties(
        self,
        platform: str,
        asset_id: str,
        stream_count: int,
        territory: str = "US",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Process streaming royalties"""
        
        try:
            platform_config = self.platform_configs.get(platform.lower())
            if not platform_config:
                logger.error(f"Unsupported streaming platform: {platform}")
                return None
            
            # Calculate gross revenue
            gross_revenue = Decimal(str(stream_count)) * platform_config["royalty_rate"]
            
            if gross_revenue < platform_config["minimum_payout"]:
                logger.info(f"Stream revenue ${gross_revenue} below minimum payout threshold")
                return None
            
            # Create transaction event
            transaction_event = TransactionEvent(
                asset_id=asset_id,
                platform=platform,
                territory=territory,
                revenue_source=RevenueSource.STREAMING,
                monetization_type=MonetizationType.SUBSCRIPTION,
                gross_revenue=gross_revenue,
                currency="USD",
                platform_fee_rate=Decimal("0.0"),  # Already calculated in rate
                metadata={
                    "stream_count": stream_count,
                    "rate_per_stream": float(platform_config["royalty_rate"]),
                    **(metadata or {})
                }
            )
            
            # Process through royalty engine
            calculation = await royalty_engine.process_transaction_event(transaction_event)
            
            logger.info(f"Processed streaming royalty for {asset_id}: {stream_count} streams = ${calculation.total_royalty}")
            return calculation.id
            
        except Exception as e:
            logger.error(f"Error processing streaming royalties: {str(e)}")
            return None

# Initialize integration services
social_media_processor = SocialMediaRoyaltyProcessor()
streaming_integration = StreamingPlatformIntegration()