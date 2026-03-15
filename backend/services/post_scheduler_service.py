"""
Post Scheduler Service
Background task that periodically checks for scheduled posts due to be published
and executes them using the existing multi-platform publish flow.
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

_scheduler_running = False


async def execute_scheduled_publish(post: dict) -> dict:
    """Execute a single scheduled post using the same logic as the live publish endpoint."""
    results = {}
    user_id = post["user_id"]
    text = post["text"]
    media_url = post.get("media_url")
    platforms = post["platforms"]

    for platform in platforms:
        try:
            if platform == "twitter_x":
                creds = await get_platform_credentials(user_id, "twitter_x")
                token = creds.get("access_token") if creds else None
                if not token:
                    results[platform] = {"success": False, "error": "No Twitter access token."}
                    continue
                result = await _twitter.post_tweet(text, token)
                results[platform] = result

            elif platform == "tiktok":
                creds = await get_platform_credentials(user_id, "tiktok")
                token = creds.get("access_token") if creds else ""
                if not token:
                    results[platform] = {"success": False, "error": "No TikTok access token."}
                    continue
                if media_url:
                    result = await _tiktok.publish_video(media_url, text, token)
                else:
                    results[platform] = {"success": False, "error": "TikTok requires a video/photo URL."}
                    continue
                results[platform] = result

            elif platform == "snapchat":
                creds = await get_platform_credentials(user_id, "snapchat")
                token = creds.get("api_token") if creds else None
                if not token:
                    results[platform] = {"success": False, "error": "No Snapchat API token."}
                    continue
                result = await _snapchat.publish_content(text, token)
                results[platform] = result
            else:
                results[platform] = {"success": False, "error": f"Unsupported platform: {platform}"}
        except Exception as e:
            logger.error(f"Scheduled publish to {platform} failed: {e}")
            results[platform] = {"success": False, "error": str(e)[:300]}

    return results


async def process_due_posts():
    """Find all scheduled posts that are due and publish them."""
    now = datetime.now(timezone.utc).isoformat()
    cursor = db.scheduled_posts.find(
        {"status": "pending", "scheduled_at": {"$lte": now}},
        {"_id": 0},
    )
    due_posts = await cursor.to_list(length=50)

    for post in due_posts:
        post_id = post["id"]
        logger.info(f"Publishing scheduled post {post_id}")

        await db.scheduled_posts.update_one(
            {"id": post_id},
            {"$set": {"status": "publishing"}},
        )

        try:
            results = await execute_scheduled_publish(post)
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
                    "published_at": datetime.now(timezone.utc).isoformat(),
                }},
            )

            # Also save to publish_history for unified history
            record = {
                "id": str(uuid.uuid4()),
                "user_id": post["user_id"],
                "text": post["text"],
                "media_url": post.get("media_url"),
                "platforms": post["platforms"],
                "results": results,
                "succeeded": succeeded,
                "total": total,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "scheduled",
                "schedule_id": post_id,
            }
            await db.publish_history.insert_one(record)

            logger.info(f"Scheduled post {post_id}: {succeeded}/{total} succeeded")
        except Exception as e:
            logger.error(f"Failed to process scheduled post {post_id}: {e}")
            await db.scheduled_posts.update_one(
                {"id": post_id},
                {"$set": {"status": "failed", "results": {"error": str(e)[:300]}}},
            )


async def scheduler_loop():
    """Background loop that checks for due posts every 30 seconds."""
    global _scheduler_running
    _scheduler_running = True
    logger.info("Post scheduler started")

    while _scheduler_running:
        try:
            await process_due_posts()
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
        await asyncio.sleep(30)


def start_scheduler():
    """Start the background scheduler as an asyncio task."""
    global _scheduler_running
    if not _scheduler_running:
        asyncio.create_task(scheduler_loop())
        logger.info("Post scheduler task created")


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler_running
    _scheduler_running = False
    logger.info("Post scheduler stopped")
