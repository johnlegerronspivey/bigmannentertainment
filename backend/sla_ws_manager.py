"""
SLA WebSocket Manager — Real-time notifications for SLA breaches.
Manages WebSocket connections and broadcasts SLA events to connected clients.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Set

from fastapi import WebSocket

logger = logging.getLogger("sla_ws_manager")


class SLAWebSocketManager:
    def __init__(self):
        self.connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.add(ws)
        logger.info(f"SLA WS connected — total: {len(self.connections)}")

    def disconnect(self, ws: WebSocket):
        self.connections.discard(ws)
        logger.info(f"SLA WS disconnected — total: {len(self.connections)}")

    async def broadcast(self, event: Dict[str, Any]):
        if not self.connections:
            return
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(event)
        stale = []
        for ws in self.connections.copy():
            try:
                await ws.send_text(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.connections.discard(ws)

    async def broadcast_escalation(self, result: Dict[str, Any]):
        """Broadcast after an escalation run completes."""
        await self.broadcast({
            "type": "escalation_run",
            "escalations_created": result.get("escalations_created", 0),
            "checked": result.get("checked", 0),
            "rules_applied": result.get("rules_applied", 0),
            "email_sent": result.get("email_sent", False),
        })

    async def broadcast_breach(self, cve_id: str, severity: str, hours_overdue: float):
        """Broadcast a single SLA breach event."""
        await self.broadcast({
            "type": "sla_breach",
            "cve_id": cve_id,
            "severity": severity,
            "hours_overdue": round(hours_overdue, 1),
        })

    async def broadcast_warning(self, cve_id: str, severity: str, pct_elapsed: float):
        """Broadcast an SLA warning (approaching breach)."""
        await self.broadcast({
            "type": "sla_warning",
            "cve_id": cve_id,
            "severity": severity,
            "pct_elapsed": round(pct_elapsed, 1),
        })


sla_ws_manager = SLAWebSocketManager()
