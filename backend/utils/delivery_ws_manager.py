"""
Delivery WebSocket Manager — Real-time delivery status updates.
Broadcasts per-delivery and batch-level progress to connected clients.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Set, Any, Optional

from fastapi import WebSocket

logger = logging.getLogger("delivery_ws_manager")


class DeliveryWebSocketManager:
    def __init__(self):
        # user_id -> set of WebSocket connections
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, ws: WebSocket, user_id: str):
        await ws.accept()
        if user_id not in self.connections:
            self.connections[user_id] = set()
        self.connections[user_id].add(ws)
        total = sum(len(v) for v in self.connections.values())
        logger.info(f"Delivery WS connected (user={user_id}) — total: {total}")

    def disconnect(self, ws: WebSocket, user_id: str):
        conns = self.connections.get(user_id)
        if conns:
            conns.discard(ws)
            if not conns:
                del self.connections[user_id]
        total = sum(len(v) for v in self.connections.values())
        logger.info(f"Delivery WS disconnected (user={user_id}) — total: {total}")

    async def send_to_user(self, user_id: str, event: Dict[str, Any]):
        conns = self.connections.get(user_id)
        if not conns:
            return
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(event)
        stale = []
        for ws in conns.copy():
            try:
                await ws.send_text(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            conns.discard(ws)
        if not conns:
            self.connections.pop(user_id, None)

    async def broadcast_delivery_update(
        self,
        user_id: str,
        batch_id: str,
        delivery_id: str,
        platform_id: str,
        status: str,
        error_message: Optional[str] = None,
    ):
        """Broadcast a single delivery status change."""
        await self.send_to_user(user_id, {
            "type": "delivery_update",
            "batch_id": batch_id,
            "delivery_id": delivery_id,
            "platform_id": platform_id,
            "status": status,
            "error_message": error_message,
        })

    async def broadcast_batch_progress(
        self,
        user_id: str,
        batch_id: str,
        progress: Dict[str, Any],
    ):
        """Broadcast batch-level progress summary."""
        await self.send_to_user(user_id, {
            "type": "batch_progress",
            "batch_id": batch_id,
            **progress,
        })


delivery_ws_manager = DeliveryWebSocketManager()
