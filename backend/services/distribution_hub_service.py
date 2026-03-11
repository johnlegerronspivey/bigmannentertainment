"""
Distribution Hub Service - Central control center for content distribution.
Manages content uploads, metadata, rights, deliveries, and platform connections.
The app URL is the "source of truth" for all distribution operations.
"""

import os
import uuid
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum

from config.database import db


class ContentType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    FILM = "film"


class DeliveryStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPORT_READY = "export_ready"


class DeliveryMethod(str, Enum):
    API_PUSH = "api_push"
    EXPORT_PACKAGE = "export_package"


PLATFORM_CATEGORIES = {
    "audio_streaming": {
        "label": "Audio Streaming & Radio",
        "platforms": {
            "spotify": {"name": "Spotify", "method": "export_package", "formats": ["audio"], "description": "Major music streaming platform"},
            "apple_music": {"name": "Apple Music", "method": "export_package", "formats": ["audio"], "description": "Apple's music streaming service"},
            "amazon_music": {"name": "Amazon Music", "method": "export_package", "formats": ["audio"], "description": "Amazon's music streaming platform"},
            "tidal": {"name": "TIDAL", "method": "export_package", "formats": ["audio"], "description": "High-fidelity music streaming"},
            "deezer": {"name": "Deezer", "method": "export_package", "formats": ["audio"], "description": "Global music streaming service"},
            "pandora": {"name": "Pandora", "method": "export_package", "formats": ["audio"], "description": "Internet radio and streaming"},
            "iheartradio": {"name": "iHeartRadio", "method": "export_package", "formats": ["audio"], "description": "Radio and podcast platform"},
            "soundcloud": {"name": "SoundCloud", "method": "api_push", "formats": ["audio"], "description": "Audio distribution and sharing"},
            "audiomack": {"name": "Audiomack", "method": "api_push", "formats": ["audio"], "description": "Free music streaming platform"},
            "bandcamp": {"name": "Bandcamp", "method": "export_package", "formats": ["audio"], "description": "Artist-direct music sales"},
            "napster": {"name": "Napster", "method": "export_package", "formats": ["audio"], "description": "Music streaming service"},
            "boomplay": {"name": "Boomplay", "method": "export_package", "formats": ["audio"], "description": "African music streaming"},
            "anghami": {"name": "Anghami", "method": "export_package", "formats": ["audio"], "description": "MENA music streaming"},
            "jiosaavn": {"name": "JioSaavn", "method": "export_package", "formats": ["audio"], "description": "Indian music streaming"},
        }
    },
    "commercial_radio": {
        "label": "Commercial Radio",
        "platforms": {
            "terrestrial_radio": {"name": "Terrestrial Radio (US)", "method": "export_package", "formats": ["audio"], "description": "US commercial radio stations"},
            "bbc_radio": {"name": "BBC Radio", "method": "export_package", "formats": ["audio"], "description": "BBC radio network"},
            "siriusxm": {"name": "SiriusXM", "method": "export_package", "formats": ["audio"], "description": "Satellite radio"},
            "radio_one": {"name": "Radio One Inc.", "method": "export_package", "formats": ["audio"], "description": "Urban radio network"},
            "cumulus_media": {"name": "Cumulus Media", "method": "export_package", "formats": ["audio"], "description": "US radio broadcasting"},
            "entercom_audacy": {"name": "Audacy (Entercom)", "method": "export_package", "formats": ["audio"], "description": "Major US radio network"},
        }
    },
    "video_platforms": {
        "label": "Video Platforms",
        "platforms": {
            "youtube": {"name": "YouTube", "method": "api_push", "formats": ["video", "audio"], "description": "Video sharing and streaming"},
            "vimeo": {"name": "Vimeo", "method": "api_push", "formats": ["video"], "description": "Professional video hosting"},
            "tiktok": {"name": "TikTok", "method": "api_push", "formats": ["video"], "description": "Short-form video platform"},
            "instagram": {"name": "Instagram", "method": "api_push", "formats": ["video", "image"], "description": "Photo and video sharing"},
            "facebook": {"name": "Facebook", "method": "api_push", "formats": ["video", "image", "audio"], "description": "Social networking platform"},
            "dailymotion": {"name": "Dailymotion", "method": "api_push", "formats": ["video"], "description": "Video sharing platform"},
            "twitch": {"name": "Twitch", "method": "api_push", "formats": ["video"], "description": "Live streaming platform"},
            "rumble": {"name": "Rumble", "method": "api_push", "formats": ["video"], "description": "Video sharing platform"},
        }
    },
    "film_movie": {
        "label": "Film & Movie Platforms",
        "platforms": {
            "amazon_prime_video": {"name": "Amazon Prime Video Direct", "method": "export_package", "formats": ["film", "video"], "description": "Self-service video distribution"},
            "vudu_fandango": {"name": "Vudu / Fandango at Home", "method": "export_package", "formats": ["film", "video"], "description": "Digital movie sales & rentals"},
            "itunes_apple_tv": {"name": "iTunes / Apple TV+", "method": "export_package", "formats": ["film", "video"], "description": "Apple's digital storefront"},
            "google_play_movies": {"name": "Google Play Movies", "method": "export_package", "formats": ["film", "video"], "description": "Google's movie distribution"},
            "vimeo_ott": {"name": "Vimeo OTT", "method": "export_package", "formats": ["film", "video"], "description": "Subscription video service builder"},
            "tubi": {"name": "Tubi", "method": "export_package", "formats": ["film", "video"], "description": "Free ad-supported streaming"},
            "pluto_tv": {"name": "Pluto TV", "method": "export_package", "formats": ["film", "video"], "description": "Free ad-supported streaming"},
            "roku_channel": {"name": "Roku Channel", "method": "export_package", "formats": ["film", "video"], "description": "Free streaming on Roku"},
            "filmhub": {"name": "FilmHub", "method": "export_package", "formats": ["film"], "description": "Film distribution aggregator"},
        }
    },
    "social_media": {
        "label": "Social Media",
        "platforms": {
            "twitter_x": {"name": "Twitter/X", "method": "api_push", "formats": ["image", "video", "audio"], "description": "Microblogging platform"},
            "linkedin": {"name": "LinkedIn", "method": "api_push", "formats": ["image", "video"], "description": "Professional networking"},
            "pinterest": {"name": "Pinterest", "method": "api_push", "formats": ["image", "video"], "description": "Visual discovery platform"},
            "snapchat": {"name": "Snapchat", "method": "api_push", "formats": ["image", "video"], "description": "Multimedia messaging"},
            "reddit": {"name": "Reddit", "method": "api_push", "formats": ["image", "video"], "description": "Social news aggregation"},
            "threads": {"name": "Threads", "method": "api_push", "formats": ["image", "video"], "description": "Meta's text-based social app"},
            "bluesky": {"name": "Bluesky", "method": "api_push", "formats": ["image", "video"], "description": "Decentralized social network"},
            "discord": {"name": "Discord", "method": "api_push", "formats": ["audio", "video", "image"], "description": "Community platform"},
            "telegram": {"name": "Telegram", "method": "api_push", "formats": ["audio", "video", "image"], "description": "Messaging platform"},
        }
    },
    "podcast": {
        "label": "Podcast Platforms",
        "platforms": {
            "apple_podcasts": {"name": "Apple Podcasts", "method": "export_package", "formats": ["audio"], "description": "Apple's podcast directory"},
            "spotify_podcasts": {"name": "Spotify for Podcasters", "method": "export_package", "formats": ["audio"], "description": "Spotify podcast hosting"},
            "google_podcasts": {"name": "Google Podcasts", "method": "export_package", "formats": ["audio"], "description": "Google's podcast directory"},
            "stitcher": {"name": "Stitcher", "method": "export_package", "formats": ["audio"], "description": "Podcast listening app"},
            "podbean": {"name": "Podbean", "method": "api_push", "formats": ["audio"], "description": "Podcast hosting platform"},
        }
    }
}


def _get_all_hub_platforms():
    """Return flattened dict of all platforms with category info."""
    result = {}
    for cat_id, cat_data in PLATFORM_CATEGORIES.items():
        for plat_id, plat_data in cat_data["platforms"].items():
            result[plat_id] = {**plat_data, "category": cat_id, "category_label": cat_data["label"]}
    return result


ALL_HUB_PLATFORMS = _get_all_hub_platforms()


class DistributionHubService:
    """Core service for the Distribution Hub — the source of truth for all deliveries."""

    # ─── CONTENT MANAGEMENT ───
    async def create_content(self, user_id: str, data: dict) -> dict:
        content_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        content = {
            "id": content_id,
            "user_id": user_id,
            "title": data["title"],
            "content_type": data["content_type"],
            "description": data.get("description", ""),
            "file_url": data.get("file_url", ""),
            "file_name": data.get("file_name", ""),
            "file_size": data.get("file_size", 0),
            "thumbnail_url": data.get("thumbnail_url", ""),
            "duration": data.get("duration"),
            "metadata": {
                "basic": {
                    "title": data["title"],
                    "artist": data.get("artist", ""),
                    "album": data.get("album", ""),
                    "genre": data.get("genre", ""),
                    "release_date": data.get("release_date", ""),
                    "description": data.get("description", ""),
                    "tags": data.get("tags", []),
                    "language": data.get("language", "en"),
                },
                "advanced": {
                    "isrc": data.get("isrc", ""),
                    "upc": data.get("upc", ""),
                    "iswc": data.get("iswc", ""),
                    "copyright_holder": data.get("copyright_holder", ""),
                    "copyright_year": data.get("copyright_year", ""),
                    "publisher": data.get("publisher", ""),
                    "record_label": data.get("record_label", ""),
                    "licensing_type": data.get("licensing_type", ""),
                    "content_rating": data.get("content_rating", ""),
                    "territory_rights": data.get("territory_rights", ["worldwide"]),
                }
            },
            "rights": {
                "copyright_info": data.get("copyright_info", ""),
                "licensing_terms": data.get("licensing_terms", ""),
                "royalty_splits": data.get("royalty_splits", []),
                "content_id_registered": False,
                "drm_enabled": data.get("drm_enabled", False),
                "exclusive_rights": data.get("exclusive_rights", []),
            },
            "status": "ready",
            "created_at": now,
            "updated_at": now,
        }
        await db.distribution_hub_content.insert_one(content)
        content.pop("_id", None)
        return content

    async def get_content_library(self, user_id: str, content_type: str = None) -> list:
        query = {"user_id": user_id}
        if content_type:
            query["content_type"] = content_type
        items = []
        async for doc in db.distribution_hub_content.find(query, {"_id": 0}).sort("created_at", -1):
            items.append(doc)
        return items

    async def get_content_by_id(self, content_id: str, user_id: str) -> Optional[dict]:
        doc = await db.distribution_hub_content.find_one(
            {"id": content_id, "user_id": user_id}, {"_id": 0}
        )
        return doc

    async def update_content_metadata(self, content_id: str, user_id: str, metadata: dict) -> Optional[dict]:
        update_fields = {}
        if "basic" in metadata:
            for k, v in metadata["basic"].items():
                update_fields[f"metadata.basic.{k}"] = v
        if "advanced" in metadata:
            for k, v in metadata["advanced"].items():
                update_fields[f"metadata.advanced.{k}"] = v
        if "rights" in metadata:
            for k, v in metadata["rights"].items():
                update_fields[f"rights.{k}"] = v
        # Also allow top-level fields like title, description
        for field in ["title", "description", "artist", "genre"]:
            if field in metadata:
                update_fields[field] = metadata[field]
                update_fields[f"metadata.basic.{field}"] = metadata[field]

        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = await db.distribution_hub_content.update_one(
            {"id": content_id, "user_id": user_id},
            {"$set": update_fields}
        )
        if result.modified_count == 0:
            return None
        return await self.get_content_by_id(content_id, user_id)

    async def delete_content(self, content_id: str, user_id: str) -> bool:
        result = await db.distribution_hub_content.delete_one({"id": content_id, "user_id": user_id})
        return result.deleted_count > 0

    # ─── DISTRIBUTION / DELIVERY ───
    async def create_delivery(self, user_id: str, content_id: str, platform_ids: list, metadata_overrides: dict = None) -> dict:
        """Create deliveries for content to selected platforms."""
        content = await self.get_content_by_id(content_id, user_id)
        if not content:
            raise ValueError("Content not found")

        delivery_batch_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        deliveries = []

        for pid in platform_ids:
            platform = ALL_HUB_PLATFORMS.get(pid)
            if not platform:
                continue

            method = platform["method"]
            status = DeliveryStatus.QUEUED if method == "api_push" else DeliveryStatus.EXPORT_READY

            delivery = {
                "id": str(uuid.uuid4()),
                "batch_id": delivery_batch_id,
                "user_id": user_id,
                "content_id": content_id,
                "content_title": content["title"],
                "content_type": content["content_type"],
                "platform_id": pid,
                "platform_name": platform["name"],
                "platform_category": platform["category_label"],
                "delivery_method": method,
                "status": status,
                "metadata": {**content.get("metadata", {}), **(metadata_overrides or {})},
                "rights": content.get("rights", {}),
                "source_url": os.environ.get("FRONTEND_URL", "https://bigmannentertainment.com"),
                "tracking_url": f"/api/distribution-hub/deliveries/{delivery_batch_id}",
                "platform_response": {},
                "error_message": None,
                "retry_count": 0,
                "created_at": now,
                "updated_at": now,
            }
            deliveries.append(delivery)

        if deliveries:
            await db.distribution_hub_deliveries.insert_many(deliveries)
            # Remove _id from each for JSON response
            for d in deliveries:
                d.pop("_id", None)

        # Also record an event in the content's history
        await db.distribution_hub_content.update_one(
            {"id": content_id},
            {
                "$push": {
                    "distribution_history": {
                        "batch_id": delivery_batch_id,
                        "platforms": platform_ids,
                        "created_at": now,
                    }
                },
                "$set": {"updated_at": now}
            }
        )

        api_push_count = len([d for d in deliveries if d["delivery_method"] == "api_push"])
        export_count = len([d for d in deliveries if d["delivery_method"] == "export_package"])

        return {
            "batch_id": delivery_batch_id,
            "total_deliveries": len(deliveries),
            "api_push": api_push_count,
            "export_packages": export_count,
            "deliveries": deliveries,
        }

    async def get_deliveries(self, user_id: str, status: str = None, limit: int = 50) -> list:
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        items = []
        async for doc in db.distribution_hub_deliveries.find(query, {"_id": 0}).sort("created_at", -1).limit(limit):
            items.append(doc)
        return items

    async def get_delivery_batch(self, batch_id: str, user_id: str) -> list:
        items = []
        async for doc in db.distribution_hub_deliveries.find(
            {"batch_id": batch_id, "user_id": user_id}, {"_id": 0}
        ):
            items.append(doc)
        return items

    async def update_delivery_status(self, delivery_id: str, user_id: str, status: str, response_data: dict = None) -> Optional[dict]:
        update = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if response_data:
            update["platform_response"] = response_data
        result = await db.distribution_hub_deliveries.update_one(
            {"id": delivery_id, "user_id": user_id},
            {"$set": update}
        )
        if result.modified_count == 0:
            return None
        doc = await db.distribution_hub_deliveries.find_one({"id": delivery_id}, {"_id": 0})
        return doc

    # ─── EXPORT PACKAGE GENERATION ───
    async def generate_export_package(self, delivery_id: str, user_id: str) -> dict:
        """Generate a platform-ready export package for a delivery."""
        delivery = await db.distribution_hub_deliveries.find_one(
            {"id": delivery_id, "user_id": user_id}, {"_id": 0}
        )
        if not delivery:
            raise ValueError("Delivery not found")

        content = await self.get_content_by_id(delivery["content_id"], user_id)
        if not content:
            raise ValueError("Content not found")

        platform = ALL_HUB_PLATFORMS.get(delivery["platform_id"], {})

        package = {
            "package_id": str(uuid.uuid4()),
            "delivery_id": delivery_id,
            "platform": delivery["platform_name"],
            "platform_id": delivery["platform_id"],
            "content_title": content["title"],
            "content_type": content["content_type"],
            "source_of_truth": os.environ.get("FRONTEND_URL", "https://bigmannentertainment.com"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": {
                "media_file": content.get("file_url", ""),
                "thumbnail": content.get("thumbnail_url", ""),
            },
            "metadata": content.get("metadata", {}),
            "rights": content.get("rights", {}),
            "platform_requirements": {
                "formats": platform.get("formats", []),
                "description": platform.get("description", ""),
            },
            "delivery_instructions": f"Upload to {delivery['platform_name']} using their creator/publisher portal. Use the metadata included in this package.",
            "status": "ready",
        }

        # Update delivery to mark export generated
        await db.distribution_hub_deliveries.update_one(
            {"id": delivery_id},
            {"$set": {
                "status": "export_ready",
                "export_package": package,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )

        return package

    # ─── DASHBOARD STATS ───
    async def get_hub_stats(self, user_id: str) -> dict:
        content_count = await db.distribution_hub_content.count_documents({"user_id": user_id})
        total_deliveries = await db.distribution_hub_deliveries.count_documents({"user_id": user_id})
        delivered = await db.distribution_hub_deliveries.count_documents({"user_id": user_id, "status": "delivered"})
        queued = await db.distribution_hub_deliveries.count_documents({"user_id": user_id, "status": "queued"})
        export_ready = await db.distribution_hub_deliveries.count_documents({"user_id": user_id, "status": "export_ready"})
        failed = await db.distribution_hub_deliveries.count_documents({"user_id": user_id, "status": "failed"})

        # Content type breakdown
        type_breakdown = {}
        for ct in ["audio", "video", "image", "film"]:
            type_breakdown[ct] = await db.distribution_hub_content.count_documents({"user_id": user_id, "content_type": ct})

        # Platform breakdown
        platform_stats = {}
        async for doc in db.distribution_hub_deliveries.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$platform_id", "count": {"$sum": 1}, "delivered": {"$sum": {"$cond": [{"$eq": ["$status", "delivered"]}, 1, 0]}}}},
        ]):
            platform_stats[doc["_id"]] = {"total": doc["count"], "delivered": doc["delivered"]}

        return {
            "content_count": content_count,
            "total_deliveries": total_deliveries,
            "delivered": delivered,
            "queued": queued,
            "export_ready": export_ready,
            "failed": failed,
            "success_rate": round((delivered / max(total_deliveries, 1)) * 100, 1),
            "content_types": type_breakdown,
            "platform_stats": platform_stats,
            "total_platforms_available": len(ALL_HUB_PLATFORMS),
        }

    # ─── PLATFORM CREDENTIALS ───
    async def save_platform_credentials(self, user_id: str, platform_id: str, credentials: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        cred_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "platform_id": platform_id,
            "platform_name": ALL_HUB_PLATFORMS.get(platform_id, {}).get("name", platform_id),
            "credentials": credentials,
            "connected": True,
            "created_at": now,
            "updated_at": now,
        }
        # Upsert
        await db.distribution_hub_credentials.update_one(
            {"user_id": user_id, "platform_id": platform_id},
            {"$set": cred_doc},
            upsert=True
        )
        cred_doc.pop("_id", None)
        cred_doc.pop("credentials", None)  # Don't return creds
        return cred_doc

    async def get_connected_platforms(self, user_id: str) -> list:
        items = []
        async for doc in db.distribution_hub_credentials.find(
            {"user_id": user_id, "connected": True},
            {"_id": 0, "credentials": 0}
        ):
            items.append(doc)
        return items

    async def disconnect_platform(self, user_id: str, platform_id: str) -> bool:
        result = await db.distribution_hub_credentials.update_one(
            {"user_id": user_id, "platform_id": platform_id},
            {"$set": {"connected": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return result.modified_count > 0


    # ─── DISTRIBUTION TEMPLATES ───

    SYSTEM_TEMPLATES = [
        {
            "id": "tpl_all_radio",
            "name": "All Radio Stations",
            "description": "Push to all 6 commercial radio platforms",
            "icon": "radio",
            "is_system": True,
            "platform_ids": ["terrestrial_radio", "bbc_radio", "siriusxm", "radio_one", "cumulus_media", "entercom_audacy"],
        },
        {
            "id": "tpl_major_streaming",
            "name": "Major Streaming",
            "description": "Top audio streaming services (Spotify, Apple Music, Amazon, TIDAL, Deezer, Pandora, SoundCloud)",
            "icon": "music",
            "is_system": True,
            "platform_ids": ["spotify", "apple_music", "amazon_music", "tidal", "deezer", "pandora", "soundcloud"],
        },
        {
            "id": "tpl_social_blast",
            "name": "Social Media Blast",
            "description": "All 9 social media platforms at once",
            "icon": "share",
            "is_system": True,
            "platform_ids": ["twitter_x", "linkedin", "pinterest", "snapchat", "reddit", "threads", "bluesky", "discord", "telegram"],
        },
        {
            "id": "tpl_video_everywhere",
            "name": "Video Everywhere",
            "description": "All major video platforms (YouTube, Vimeo, TikTok, Dailymotion, Twitch, Rumble)",
            "icon": "video",
            "is_system": True,
            "platform_ids": ["youtube", "vimeo", "tiktok", "instagram", "facebook", "dailymotion", "twitch", "rumble"],
        },
        {
            "id": "tpl_film_distribution",
            "name": "Film Distribution",
            "description": "All film & movie platforms (Amazon Prime, iTunes, Tubi, Pluto TV, etc.)",
            "icon": "film",
            "is_system": True,
            "platform_ids": ["amazon_prime_video", "vudu_fandango", "itunes_apple_tv", "google_play_movies", "vimeo_ott", "tubi", "pluto_tv", "roku_channel", "filmhub"],
        },
        {
            "id": "tpl_podcast_push",
            "name": "Full Podcast Push",
            "description": "All podcast directories and hosting platforms",
            "icon": "mic",
            "is_system": True,
            "platform_ids": ["apple_podcasts", "spotify_podcasts", "google_podcasts", "stitcher", "podbean"],
        },
    ]

    async def get_templates(self, user_id: str) -> list:
        """Get system templates + user custom templates."""
        system = [
            {**t, "platform_count": len(t["platform_ids"]), "user_id": None}
            for t in self.SYSTEM_TEMPLATES
        ]
        custom = []
        async for doc in db.distribution_hub_templates.find(
            {"user_id": user_id}, {"_id": 0}
        ).sort("created_at", -1):
            doc["platform_count"] = len(doc.get("platform_ids", []))
            custom.append(doc)
        return system + custom

    async def create_template(self, user_id: str, data: dict) -> dict:
        template_id = f"tpl_custom_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        template = {
            "id": template_id,
            "user_id": user_id,
            "name": data["name"],
            "description": data.get("description", ""),
            "icon": data.get("icon", "layers"),
            "is_system": False,
            "platform_ids": data.get("platform_ids", []),
            "platform_count": len(data.get("platform_ids", [])),
            "created_at": now,
            "updated_at": now,
        }
        await db.distribution_hub_templates.insert_one(template)
        template.pop("_id", None)
        return template

    async def update_template(self, template_id: str, user_id: str, data: dict) -> Optional[dict]:
        # Cannot edit system templates
        if template_id.startswith("tpl_") and not template_id.startswith("tpl_custom_"):
            return None
        update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
        for field in ["name", "description", "icon", "platform_ids"]:
            if field in data:
                update_fields[field] = data[field]
        if "platform_ids" in data:
            update_fields["platform_count"] = len(data["platform_ids"])

        result = await db.distribution_hub_templates.update_one(
            {"id": template_id, "user_id": user_id},
            {"$set": update_fields}
        )
        if result.modified_count == 0:
            return None
        doc = await db.distribution_hub_templates.find_one({"id": template_id}, {"_id": 0})
        return doc

    async def delete_template(self, template_id: str, user_id: str) -> bool:
        if template_id.startswith("tpl_") and not template_id.startswith("tpl_custom_"):
            return False  # Can't delete system templates
        result = await db.distribution_hub_templates.delete_one({"id": template_id, "user_id": user_id})
        return result.deleted_count > 0

    async def get_template_by_id(self, template_id: str, user_id: str) -> Optional[dict]:
        # Check system templates first
        for t in self.SYSTEM_TEMPLATES:
            if t["id"] == template_id:
                return {**t, "platform_count": len(t["platform_ids"]), "user_id": None}
        # Then check custom
        doc = await db.distribution_hub_templates.find_one(
            {"id": template_id, "user_id": user_id}, {"_id": 0}
        )
        return doc


distribution_hub_svc = DistributionHubService()
