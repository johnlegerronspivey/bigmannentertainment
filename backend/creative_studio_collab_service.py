"""
Creative Studio Collaboration Service
Real-time collaboration, presence tracking, activity feed, version management
"""

import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorDatabase


class ProjectPresence:
    """Track who is active in a project"""
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}  # user_id -> websocket
        self.cursors: Dict[str, Dict] = {}  # user_id -> {x, y}
        self.user_info: Dict[str, Dict] = {}  # user_id -> {name, color, avatar}

    @property
    def active_users(self) -> List[Dict]:
        return [
            {"user_id": uid, "cursor": self.cursors.get(uid), **self.user_info.get(uid, {})}
            for uid in self.connections
        ]


AVATAR_COLORS = [
    "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#3b82f6",
    "#ef4444", "#06b6d4", "#f97316", "#84cc16", "#a855f7"
]


class CollaborationService:
    """Manages real-time collaboration for Creative Studio projects"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.activity_collection = db.creative_studio_activity
        self.projects_collection = db.creative_studio_projects
        self.presence: Dict[str, ProjectPresence] = {}  # project_id -> ProjectPresence

    def _get_presence(self, project_id: str) -> ProjectPresence:
        if project_id not in self.presence:
            self.presence[project_id] = ProjectPresence()
        return self.presence[project_id]

    async def connect(self, project_id: str, user_id: str, user_name: str, websocket: WebSocket):
        """Add a user connection to a project"""
        await websocket.accept()
        p = self._get_presence(project_id)
        color_idx = len(p.connections) % len(AVATAR_COLORS)
        p.connections[user_id] = websocket
        p.user_info[user_id] = {
            "name": user_name,
            "color": AVATAR_COLORS[color_idx],
            "joined_at": datetime.now(timezone.utc).isoformat()
        }
        # Broadcast join
        await self._broadcast(project_id, {
            "type": "user_joined",
            "user_id": user_id,
            "user_name": user_name,
            "color": AVATAR_COLORS[color_idx],
            "active_users": p.active_users
        }, exclude=user_id)
        # Send current state to new user
        await websocket.send_json({
            "type": "presence_state",
            "active_users": p.active_users
        })

    async def disconnect(self, project_id: str, user_id: str):
        """Remove a user from a project"""
        p = self._get_presence(project_id)
        p.connections.pop(user_id, None)
        p.cursors.pop(user_id, None)
        p.user_info.pop(user_id, None)
        if not p.connections:
            self.presence.pop(project_id, None)
        else:
            await self._broadcast(project_id, {
                "type": "user_left",
                "user_id": user_id,
                "active_users": p.active_users
            })

    async def handle_cursor_move(self, project_id: str, user_id: str, x: float, y: float):
        """Update and broadcast cursor position"""
        p = self._get_presence(project_id)
        p.cursors[user_id] = {"x": x, "y": y}
        await self._broadcast(project_id, {
            "type": "cursor_move",
            "user_id": user_id,
            "user_name": p.user_info.get(user_id, {}).get("name", "Unknown"),
            "color": p.user_info.get(user_id, {}).get("color", "#8b5cf6"),
            "x": x, "y": y
        }, exclude=user_id)

    async def handle_element_update(self, project_id: str, user_id: str, element_data: Dict):
        """Broadcast element change to other users"""
        p = self._get_presence(project_id)
        await self._broadcast(project_id, {
            "type": "element_update",
            "user_id": user_id,
            "user_name": p.user_info.get(user_id, {}).get("name", "Unknown"),
            "element": element_data
        }, exclude=user_id)

    async def handle_element_add(self, project_id: str, user_id: str, element_data: Dict):
        """Broadcast new element to other users"""
        p = self._get_presence(project_id)
        await self._broadcast(project_id, {
            "type": "element_add",
            "user_id": user_id,
            "user_name": p.user_info.get(user_id, {}).get("name", "Unknown"),
            "element": element_data
        }, exclude=user_id)

    async def handle_element_delete(self, project_id: str, user_id: str, element_id: str):
        """Broadcast element deletion"""
        p = self._get_presence(project_id)
        await self._broadcast(project_id, {
            "type": "element_delete",
            "user_id": user_id,
            "user_name": p.user_info.get(user_id, {}).get("name", "Unknown"),
            "element_id": element_id
        }, exclude=user_id)

    async def _broadcast(self, project_id: str, message: Dict, exclude: str = None):
        """Send message to all connected users in a project"""
        p = self.presence.get(project_id)
        if not p:
            return
        disconnected = []
        for uid, ws in p.connections.items():
            if uid == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(uid)
        for uid in disconnected:
            await self.disconnect(project_id, uid)

    # ==================== Activity Feed ====================

    async def log_activity(self, project_id: str, user_id: str, user_name: str,
                           action: str, details: Optional[Dict] = None):
        """Log an activity event"""
        activity = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "user_id": user_id,
            "user_name": user_name,
            "action": action,
            "details": details or {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await self.activity_collection.insert_one(activity)
        # Broadcast activity to connected users
        p = self.presence.get(project_id)
        if p:
            activity.pop("_id", None)
            await self._broadcast(project_id, {"type": "activity", **activity})
        return activity

    async def get_activity_feed(self, project_id: str, limit: int = 50) -> List[Dict]:
        """Get activity feed for a project"""
        cursor = self.activity_collection.find(
            {"project_id": project_id}, {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    # ==================== Version Management ====================

    async def get_versions(self, project_id: str) -> List[Dict]:
        """Get version history for a project"""
        doc = await self.projects_collection.find_one(
            {"id": project_id}, {"_id": 0, "versions": 1, "current_version": 1}
        )
        if not doc:
            return []
        versions = doc.get("versions", [])
        versions.reverse()  # newest first
        return versions

    async def restore_version(self, project_id: str, version_id: str, user_id: str) -> Optional[Dict]:
        """Restore a project to a previous version"""
        doc = await self.projects_collection.find_one({"id": project_id}, {"_id": 0})
        if not doc:
            return None

        target = None
        for v in doc.get("versions", []):
            if v.get("id") == version_id:
                target = v
                break
        if not target:
            return None

        # Save current state as a new version before restoring
        current_version_num = doc.get("current_version", 1)
        save_version = {
            "id": str(uuid.uuid4()),
            "version_number": current_version_num + 1,
            "name": "Auto-save before restore",
            "elements_snapshot": doc.get("elements", []),
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        restore_version = {
            "id": str(uuid.uuid4()),
            "version_number": current_version_num + 2,
            "name": f"Restored from v{target.get('version_number', '?')}",
            "elements_snapshot": target.get("elements_snapshot", []),
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        await self.projects_collection.update_one(
            {"id": project_id},
            {
                "$set": {
                    "elements": target.get("elements_snapshot", []),
                    "current_version": current_version_num + 2,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {
                    "versions": {"$each": [save_version, restore_version]}
                }
            }
        )
        await self.log_activity(
            project_id, user_id, "User",
            "version_restored",
            {"restored_version": target.get("version_number")}
        )
        return {"success": True, "elements": target.get("elements_snapshot", []),
                "version_number": current_version_num + 2}

    # ==================== Comments ====================

    async def get_comments(self, project_id: str) -> List[Dict]:
        """Get all comments for a project"""
        doc = await self.projects_collection.find_one(
            {"id": project_id}, {"_id": 0, "comments": 1}
        )
        return doc.get("comments", []) if doc else []

    async def add_comment(self, project_id: str, user_id: str, user_name: str,
                          content: str, position: Optional[Dict] = None) -> Optional[Dict]:
        """Add a comment and broadcast it"""
        comment = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "user_name": user_name,
            "content": content,
            "position": position,
            "is_resolved": False,
            "resolved_by": None,
            "resolved_at": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await self.projects_collection.update_one(
            {"id": project_id},
            {"$push": {"comments": comment}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        await self.log_activity(project_id, user_id, user_name, "comment_added",
                                {"comment_id": comment["id"], "content": content[:80]})
        # Broadcast
        p = self.presence.get(project_id)
        if p:
            await self._broadcast(project_id, {"type": "comment_added", "comment": comment})
        return comment

    async def resolve_comment(self, project_id: str, comment_id: str, user_id: str) -> bool:
        """Resolve a comment"""
        result = await self.projects_collection.update_one(
            {"id": project_id, "comments.id": comment_id},
            {"$set": {
                "comments.$.is_resolved": True,
                "comments.$.resolved_by": user_id,
                "comments.$.resolved_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        if result.modified_count > 0:
            p = self.presence.get(project_id)
            if p:
                await self._broadcast(project_id, {
                    "type": "comment_resolved",
                    "comment_id": comment_id,
                    "resolved_by": user_id
                })
            return True
        return False

    def get_online_users(self, project_id: str) -> List[Dict]:
        """Get list of currently online users in a project"""
        p = self.presence.get(project_id)
        return p.active_users if p else []


# Singleton
_collab_service: Optional[CollaborationService] = None


def initialize_collab_service(db: AsyncIOMotorDatabase) -> CollaborationService:
    global _collab_service
    _collab_service = CollaborationService(db)
    return _collab_service


def get_collab_service() -> Optional[CollaborationService]:
    return _collab_service
