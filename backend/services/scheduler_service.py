"""
Post Scheduler Service
Background task that checks for due scheduled posts and publishes them
via the existing multi-platform publish engine.
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from config.database import db
from services.social_platform_manager import (
    TwitterConnectionManager,
    TikTokConnectionManager,
    SnapchatConnectionManager,
    get_platform_credentials,
)

logger = logging.getLogger(__name__)

_twitter = TwitterConnectionManager()
_tiktok = TikTokConnectionManager()
_snapchat = SnapchatConnectionManager()

CHECK_INTERVAL_SECONDS = 30


async def _publish_post(post: dict) -> dict:
    """Execute the actual publish for a scheduled post, mirroring the live publish logic."""
    user_id = post["user_id"]
    text = post["text"]
    platforms = post["platforms"]
    media_url = post.get("media_url")
    results = {}

    for platform in platforms:
        try:
            if platform == "twitter_x":
                creds = await get_platform_credentials(user_id, "twitter_x")
                token = creds.get("access_token") if creds else None
                if not token:
                    results[platform] = {"success": False, "error": "No Twitter access token."}
                    continue
                results[platform] = await _twitter.post_tweet(text, token)

            elif platform == "tiktok":
                creds = await get_platform_credentials(user_id, "tiktok")
                token = creds.get("access_token") if creds else ""
                if not token:
                    results[platform] = {"success": False, "error": "No TikTok access token."}
                    continue
                if media_url:
                    results[platform] = await _tiktok.publish_video(media_url, text, token)
                else:
                    results[platform] = {"success": False, "error": "TikTok requires a media URL."}
                    continue

            elif platform == "snapchat":
                creds = await get_platform_credentials(user_id, "snapchat")
                token = creds.get("api_token") if creds else None
                if not token:
                    results[platform] = {"success": False, "error": "No Snapchat API token."}
                    continue
                results[platform] = await _snapchat.publish_content(text, token)

            else:
                results[platform] = {"success": False, "error": f"Unsupported platform: {platform}"}

        except Exception as e:
            logger.error(f"Scheduled publish to {platform} failed: {e}")
            results[platform] = {"success": False, "error": str(e)[:300]}

    return results


async def _process_due_posts():
    """Find and publish all posts whose scheduled_time has passed."""
    now = datetime.now(timezone.utc)
    cursor = db.scheduled_posts.find(
        {"status": "pending", "scheduled_time": {"$lte": now.isoformat()}},
        {"_id": 0},
    )

    due_posts = []
    async for doc in cursor:
        due_posts.append(doc)

    for post in due_posts:
        post_id = post["id"]
        logger.info(f"Publishing scheduled post {post_id}")

        # Mark as publishing
        await db.scheduled_posts.update_one(
            {"id": post_id},
            {"$set": {"status": "publishing", "updated_at": now.isoformat()}},
        )

        results = await _publish_post(post)
        succeeded = sum(1 for r in results.values() if r.get("success"))
        total = len(post["platforms"])
        final_status = "published" if succeeded > 0 else "failed"

        await db.scheduled_posts.update_one(
            {"id": post_id},
            {"$set": {
                "status": final_status,
                "results": results,
                "succeeded": succeeded,
                "total": total,
                "published_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }},
        )

        # Also save to publish_history for unified feed
        record = {
            "id": str(uuid.uuid4()),
            "user_id": post["user_id"],
            "text": post["text"],
            "media_url": post.get("media_url"),
            "platforms": post["platforms"],
            "results": results,
            "succeeded": succeeded,
            "total": total,
            "created_at": now.isoformat(),
            "source": "scheduled",
            "scheduled_post_id": post_id,
        }
        await db.publish_history.insert_one(record)

        logger.info(f"Scheduled post {post_id}: {final_status} ({succeeded}/{total})")


async def run_scheduler():
    """Background loop that checks for due posts every CHECK_INTERVAL_SECONDS."""
    logger.info("Post scheduler started")
    while True:
        try:
            await _process_due_posts()
        except Exception as e:
            logger.error(f"Scheduler tick error: {e}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


def start_scheduler():
    """Launch the scheduler background task."""
    loop = asyncio.get_event_loop()
    loop.create_task(run_scheduler())
    logger.info("Post scheduler background task launched")
