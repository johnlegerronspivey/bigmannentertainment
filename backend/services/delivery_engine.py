"""
Delivery Engine — Processes queued Distribution Hub deliveries as background tasks.
Dispatches to platform adapters for real API delivery, falls back to export packages.
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from config.database import db
from services.platform_adapters import get_adapter, get_supported_platform_ids, DeliveryResult

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


async def _get_user_credentials(user_id: str, platform_id: str) -> Optional[dict]:
    """Fetch saved credentials for a user+platform from the hub credentials collection."""
    doc = await db.distribution_hub_credentials.find_one(
        {"user_id": user_id, "platform_id": platform_id, "connected": True},
        {"_id": 0},
    )
    if doc and doc.get("credentials"):
        return doc["credentials"]
    return None


async def _resolve_file_path(content: dict) -> Optional[str]:
    """Resolve the local file path from a content record."""
    file_url = content.get("file_url", "")
    if not file_url:
        return None
    # Hub files are stored at /app/uploads/hub/<filename>
    if file_url.startswith("/api/distribution-hub/files/"):
        filename = file_url.split("/")[-1]
        path = f"/app/uploads/hub/{filename}"
        if os.path.exists(path):
            return path
    # Content files stored at /app/uploads/content/<filename>
    if file_url.startswith("/api/user-content/file/"):
        filename = file_url.split("/")[-1]
        path = f"/app/uploads/content/{filename}"
        if os.path.exists(path):
            return path
    # Absolute local path
    if file_url.startswith("/app/") and os.path.exists(file_url):
        return file_url
    return None


async def _update_delivery(delivery_id: str, updates: dict):
    """Update a delivery record in the database."""
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.distribution_hub_deliveries.update_one(
        {"id": delivery_id},
        {"$set": updates},
    )


async def execute_delivery(delivery: dict):
    """
    Execute a single delivery: attempt real API push, fall back to export.
    Updates the delivery record with results.
    """
    delivery_id = delivery["id"]
    platform_id = delivery["platform_id"]
    user_id = delivery["user_id"]
    content_id = delivery["content_id"]
    delivery_method = delivery.get("delivery_method", "export_package")

    logger.info(f"Executing delivery {delivery_id} -> {platform_id} ({delivery_method})")

    # Mark as preparing
    await _update_delivery(delivery_id, {"status": "preparing"})

    # If it's an export_package method, skip API push and generate package
    if delivery_method == "export_package":
        await _update_delivery(delivery_id, {
            "status": "export_ready",
            "platform_response": {"method": "export_package", "message": "Ready for manual export/upload"},
        })
        return

    # --- API Push delivery ---
    # Get content details
    content = await db.distribution_hub_content.find_one(
        {"id": content_id, "user_id": user_id}, {"_id": 0}
    )
    if not content:
        await _update_delivery(delivery_id, {
            "status": "failed",
            "error_message": "Content not found",
            "platform_response": {"error": "Content not found"},
        })
        return

    # Get adapter
    adapter = get_adapter(platform_id)
    if not adapter:
        # No adapter — fall back to export_ready
        await _update_delivery(delivery_id, {
            "status": "export_ready",
            "platform_response": {
                "method": "export_package",
                "message": f"No live adapter for {platform_id}; ready for manual export",
            },
        })
        return

    # Get credentials
    credentials = await _get_user_credentials(user_id, platform_id)
    if not credentials:
        await _update_delivery(delivery_id, {
            "status": "export_ready",
            "platform_response": {
                "method": "export_package",
                "message": f"No credentials saved for {platform_id}; connect your account to enable auto-push",
            },
        })
        return

    # Resolve file
    file_path = await _resolve_file_path(content)

    # Mark as delivering
    await _update_delivery(delivery_id, {"status": "delivering"})

    # Attempt delivery with retries
    result = None
    retry = 0
    while retry <= MAX_RETRIES:
        try:
            result = await adapter.deliver(content, credentials, file_path)
            if result.success:
                break
        except Exception as e:
            logger.error(f"Delivery attempt {retry} failed for {delivery_id}: {e}")
            result = DeliveryResult(False, message=str(e))

        retry += 1
        if retry <= MAX_RETRIES:
            logger.info(f"Retrying delivery {delivery_id} (attempt {retry}/{MAX_RETRIES})")
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    # Update final status
    if result and result.success:
        await _update_delivery(delivery_id, {
            "status": "delivered",
            "platform_response": result.to_dict(),
            "error_message": None,
            "retry_count": retry,
        })
        logger.info(f"Delivery {delivery_id} -> {platform_id} SUCCEEDED")
    else:
        error_msg = result.message if result else "Unknown error"
        await _update_delivery(delivery_id, {
            "status": "failed",
            "platform_response": result.to_dict() if result else {},
            "error_message": error_msg,
            "retry_count": retry,
        })
        logger.warning(f"Delivery {delivery_id} -> {platform_id} FAILED: {error_msg}")


async def process_delivery_batch(batch_id: str, user_id: str):
    """
    Process all deliveries in a batch. Runs API-push deliveries concurrently.
    Called as a background task after /distribute.
    """
    deliveries = []
    async for doc in db.distribution_hub_deliveries.find(
        {"batch_id": batch_id, "user_id": user_id}, {"_id": 0}
    ):
        deliveries.append(doc)

    if not deliveries:
        logger.warning(f"No deliveries found for batch {batch_id}")
        return

    logger.info(f"Processing batch {batch_id}: {len(deliveries)} deliveries")

    # Process concurrently with a semaphore to limit parallelism
    semaphore = asyncio.Semaphore(5)

    async def run_with_semaphore(delivery):
        async with semaphore:
            await execute_delivery(delivery)

    tasks = [run_with_semaphore(d) for d in deliveries]
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.info(f"Batch {batch_id} processing complete")


async def retry_failed_delivery(delivery_id: str, user_id: str) -> bool:
    """Retry a single failed delivery."""
    doc = await db.distribution_hub_deliveries.find_one(
        {"id": delivery_id, "user_id": user_id}, {"_id": 0}
    )
    if not doc:
        return False
    if doc.get("status") != "failed":
        return False

    await _update_delivery(delivery_id, {"status": "queued", "error_message": None})
    await execute_delivery(doc)
    return True


async def get_batch_progress(batch_id: str, user_id: str) -> dict:
    """Get progress summary for a delivery batch."""
    counts = {"total": 0, "delivered": 0, "failed": 0, "delivering": 0, "queued": 0, "preparing": 0, "export_ready": 0}
    async for doc in db.distribution_hub_deliveries.find(
        {"batch_id": batch_id, "user_id": user_id}, {"_id": 0, "status": 1}
    ):
        counts["total"] += 1
        status = doc.get("status", "queued")
        if status in counts:
            counts[status] += 1

    completed = counts["delivered"] + counts["failed"] + counts["export_ready"]
    counts["progress_pct"] = round((completed / max(counts["total"], 1)) * 100, 1)
    counts["is_complete"] = completed >= counts["total"]
    return counts
