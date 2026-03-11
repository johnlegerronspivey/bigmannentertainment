"""
SLA WebSocket Manager — Real-time notifications for SLA breaches.
Manages WebSocket connections and broadcasts SLA events to connected clients.
Supports per-user notification preferences.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Set, Optional

from fastapi import WebSocket

logger = logging.getLogger("sla_ws_manager")


class SLAWebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}  # user_id -> ws
        self.anonymous: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket, user_id: Optional[str] = None):
        await ws.accept()
        if user_id:
            self.connections[user_id] = ws
        else:
            self.anonymous.add(ws)
        total = len(self.connections) + len(self.anonymous)
        logger.info(f"SLA WS connected (user={user_id or 'anon'}) — total: {total}")

    def disconnect(self, ws: WebSocket, user_id: Optional[str] = None):
        if user_id and user_id in self.connections:
            del self.connections[user_id]
        self.anonymous.discard(ws)
        total = len(self.connections) + len(self.anonymous)
        logger.info(f"SLA WS disconnected — total: {total}")

    async def broadcast(self, event: Dict[str, Any]):
        """Broadcast to all connections (anonymous + user-keyed)."""
        if not self.connections and not self.anonymous:
            return
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(event)
        stale_anon = []
        stale_users = []

        for ws in self.anonymous.copy():
            try:
                await ws.send_text(payload)
            except Exception:
                stale_anon.append(ws)

        for uid, ws in list(self.connections.items()):
            try:
                await ws.send_text(payload)
            except Exception:
                stale_users.append(uid)

        for ws in stale_anon:
            self.anonymous.discard(ws)
        for uid in stale_users:
            self.connections.pop(uid, None)

    async def send_to_user(self, user_id: str, event: Dict[str, Any]):
        """Send a notification to a specific user."""
        ws = self.connections.get(user_id)
        if not ws:
            return
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        try:
            await ws.send_text(json.dumps(event))
        except Exception:
            self.connections.pop(user_id, None)

    async def broadcast_escalation(self, result: Dict[str, Any]):
        await self.broadcast({
            "type": "escalation_run",
            "escalations_created": result.get("escalations_created", 0),
            "checked": result.get("checked", 0),
            "rules_applied": result.get("rules_applied", 0),
            "email_sent": result.get("email_sent", False),
        })

    async def broadcast_breach(self, cve_id: str, severity: str, hours_overdue: float):
        await self.broadcast({
            "type": "sla_breach",
            "cve_id": cve_id,
            "severity": severity,
            "hours_overdue": round(hours_overdue, 1),
        })

    async def broadcast_warning(self, cve_id: str, severity: str, pct_elapsed: float):
        await self.broadcast({
            "type": "sla_warning",
            "cve_id": cve_id,
            "severity": severity,
            "pct_elapsed": round(pct_elapsed, 1),
        })


sla_ws_manager = SLAWebSocketManager()
