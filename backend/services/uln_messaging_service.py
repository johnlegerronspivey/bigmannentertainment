"""
ULN Inter-Label Messaging Service
===================================
Real-time messaging between label entities in the Unified Label Network.
Supports direct threads, read receipts, and message history.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
logger = logging.getLogger(__name__)


class ULNMessagingService:
    def __init__(self):
        self.threads = db.uln_message_threads
        self.messages = db.uln_messages

    async def create_thread(self, sender_label_id: str, recipient_label_id: str,
                            subject: str, creator_id: str) -> Dict[str, Any]:
        """Create a new messaging thread between two labels."""
        thread_id = str(uuid.uuid4())
        thread = {
            "thread_id": thread_id,
            "participants": sorted([sender_label_id, recipient_label_id]),
            "subject": subject,
            "created_by": creator_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "message_count": 0,
            "last_message_preview": "",
            "status": "active",
        }
        await self.threads.insert_one(thread)
        return {"success": True, "thread_id": thread_id, "thread": {k: v for k, v in thread.items() if k != "_id"}}

    async def send_message(self, thread_id: str, sender_label_id: str,
                           sender_name: str, content: str) -> Dict[str, Any]:
        """Send a message in an existing thread."""
        thread = await self.threads.find_one({"thread_id": thread_id})
        if not thread:
            return {"success": False, "error": "Thread not found"}
        if sender_label_id not in thread["participants"]:
            return {"success": False, "error": "Sender not a participant"}

        msg_id = str(uuid.uuid4())
        message = {
            "message_id": msg_id,
            "thread_id": thread_id,
            "sender_label_id": sender_label_id,
            "sender_name": sender_name,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read_by": [sender_label_id],
        }
        await self.messages.insert_one(message)
        await self.threads.update_one(
            {"thread_id": thread_id},
            {
                "$inc": {"message_count": 1},
                "$set": {
                    "last_message_preview": content[:120],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            },
        )
        return {"success": True, "message_id": msg_id, "message": {k: v for k, v in message.items() if k != "_id"}}

    async def get_threads(self, label_id: str) -> List[Dict[str, Any]]:
        """Get all threads for a label."""
        threads = await self.threads.find(
            {"participants": label_id, "status": "active"},
            projection={"_id": 0},
        ).sort("updated_at", -1).to_list(length=100)
        # Enrich with unread count
        for t in threads:
            unread = await self.messages.count_documents({
                "thread_id": t["thread_id"],
                "read_by": {"$nin": [label_id]},
            })
            t["unread_count"] = unread
        return threads

    async def get_messages(self, thread_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get messages in a thread."""
        thread = await self.threads.find_one({"thread_id": thread_id}, projection={"_id": 0})
        if not thread:
            return {"success": False, "error": "Thread not found"}
        messages = await self.messages.find(
            {"thread_id": thread_id}, projection={"_id": 0}
        ).sort("timestamp", 1).skip(offset).limit(limit).to_list(length=limit)
        total = await self.messages.count_documents({"thread_id": thread_id})
        return {"success": True, "thread": thread, "messages": messages, "total": total}

    async def mark_read(self, thread_id: str, label_id: str) -> Dict[str, Any]:
        """Mark all messages in a thread as read by a label."""
        result = await self.messages.update_many(
            {"thread_id": thread_id, "read_by": {"$nin": [label_id]}},
            {"$addToSet": {"read_by": label_id}},
        )
        return {"success": True, "marked": result.modified_count}

    async def get_all_threads_summary(self) -> Dict[str, Any]:
        """Admin view: get summary of all threads."""
        total = await self.threads.count_documents({})
        active = await self.threads.count_documents({"status": "active"})
        total_messages = await self.messages.count_documents({})
        recent = await self.threads.find(
            {}, projection={"_id": 0}
        ).sort("updated_at", -1).limit(10).to_list(length=10)
        return {
            "success": True,
            "total_threads": total,
            "active_threads": active,
            "total_messages": total_messages,
            "recent_threads": recent,
        }
