"""
Direct Messaging - Conversation-based messaging between users/creators
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db
from auth.service import get_current_user

router = APIRouter(prefix="/messages", tags=["Direct Messaging"])


def serialize_doc(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    for key in ["created_at", "updated_at", "last_message_at"]:
        if key in doc and isinstance(doc[key], datetime):
            doc[key] = doc[key].isoformat()
    return doc


class SendMessage(BaseModel):
    recipient_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1, max_length=5000)


class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


def _conversation_key(user_a: str, user_b: str) -> str:
    """Deterministic key so both users share the same conversation."""
    return "|".join(sorted([user_a, user_b]))


@router.post("/send")
async def send_message(data: SendMessage, current_user=Depends(get_current_user)):
    sender_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    if sender_id == data.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    # Verify recipient exists
    recipient = await db.users.find_one({"id": data.recipient_id}, {"_id": 0, "id": 1, "email": 1, "full_name": 1})
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    conv_key = _conversation_key(sender_id, data.recipient_id)
    now = datetime.now(timezone.utc)

    # Upsert conversation
    conv = await db.conversations.find_one({"conversation_key": conv_key})
    if not conv:
        sender_user = await db.users.find_one({"id": sender_id}, {"_id": 0, "id": 1, "email": 1, "full_name": 1})
        conv_doc = {
            "conversation_key": conv_key,
            "participants": [
                {"user_id": sender_id, "name": (sender_user or {}).get("full_name", sender_user.get("email", "Unknown"))},
                {"user_id": data.recipient_id, "name": recipient.get("full_name", recipient.get("email", "Unknown"))},
            ],
            "last_message": data.content[:100],
            "last_message_at": now,
            "unread_count": {sender_id: 0, data.recipient_id: 1},
            "created_at": now,
            "updated_at": now,
        }
        result = await db.conversations.insert_one(conv_doc)
        conv_id = str(result.inserted_id)
    else:
        conv_id = str(conv["_id"])
        await db.conversations.update_one(
            {"_id": conv["_id"]},
            {
                "$set": {
                    "last_message": data.content[:100],
                    "last_message_at": now,
                    "updated_at": now,
                },
                "$inc": {f"unread_count.{data.recipient_id}": 1},
            },
        )

    # Insert message
    msg_doc = {
        "conversation_id": conv_id,
        "sender_id": sender_id,
        "recipient_id": data.recipient_id,
        "content": data.content,
        "read": False,
        "created_at": now,
    }
    result = await db.messages.insert_one(msg_doc)
    msg_doc["_id"] = result.inserted_id
    return serialize_doc(msg_doc)


@router.get("/conversations")
async def list_conversations(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    cursor = db.conversations.find(
        {"participants.user_id": user_id}
    ).sort("last_message_at", -1)

    conversations = []
    async for doc in cursor:
        serialized = serialize_doc(doc)
        # Add unread count for current user
        unread = doc.get("unread_count", {})
        serialized["my_unread"] = unread.get(user_id, 0)
        # Identify the other participant
        for p in doc.get("participants", []):
            if p["user_id"] != user_id:
                serialized["other_user"] = p
                break
        conversations.append(serialized)

    return {"conversations": conversations}


@router.get("/conversation/{other_user_id}")
async def get_conversation_messages(
    other_user_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user=Depends(get_current_user),
):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    conv_key = _conversation_key(user_id, other_user_id)

    conv = await db.conversations.find_one({"conversation_key": conv_key})
    if not conv:
        return {"messages": [], "conversation": None}

    conv_id = str(conv["_id"])

    cursor = db.messages.find({"conversation_id": conv_id}).sort("created_at", 1).skip(skip).limit(limit)
    messages = []
    async for doc in cursor:
        messages.append(serialize_doc(doc))

    total = await db.messages.count_documents({"conversation_id": conv_id})

    return {"messages": messages, "conversation": serialize_doc(conv) if conv.get("_id") else conv, "total": total}


@router.put("/read/{other_user_id}")
async def mark_as_read(other_user_id: str, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    conv_key = _conversation_key(user_id, other_user_id)

    conv = await db.conversations.find_one({"conversation_key": conv_key})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv_id = str(conv["_id"])

    # Mark all messages from the other user as read
    await db.messages.update_many(
        {"conversation_id": conv_id, "sender_id": other_user_id, "read": False},
        {"$set": {"read": True}},
    )

    # Reset unread count
    await db.conversations.update_one(
        {"_id": conv["_id"]},
        {"$set": {f"unread_count.{user_id}": 0}},
    )

    return {"message": "Messages marked as read"}


@router.delete("/{message_id}")
async def delete_message(message_id: str, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    try:
        msg = await db.messages.find_one({"_id": ObjectId(message_id), "sender_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid message ID")
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found or not yours")

    await db.messages.delete_one({"_id": ObjectId(message_id)})
    return {"message": "Message deleted"}


@router.get("/unread-count")
async def get_unread_count(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    pipeline = [
        {"$match": {"participants.user_id": user_id}},
        {"$project": {"unread": f"$unread_count.{user_id}"}},
        {"$group": {"_id": None, "total": {"$sum": "$unread"}}},
    ]
    result = await db.conversations.aggregate(pipeline).to_list(1)
    total = result[0]["total"] if result else 0
    return {"unread_count": total}
