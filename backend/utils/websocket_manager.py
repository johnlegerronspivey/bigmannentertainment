"""
WebSocket Manager for Real-Time Support Chat
Handles WebSocket connections, message routing, and real-time features
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Set, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionInfo:
    """Information about an active WebSocket connection"""
    
    def __init__(self, websocket: WebSocket, user_id: str, user_type: str, session_id: str = None):
        self.websocket = websocket
        self.user_id = user_id
        self.user_type = user_type  # 'customer', 'agent', 'admin'
        self.session_id = session_id
        self.connected_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.is_typing = False
        self.typing_timeout_task = None

class SupportWebSocketManager:
    """Manages WebSocket connections for the support system"""
    
    def __init__(self):
        # Active connections: websocket -> ConnectionInfo
        self.active_connections: Dict[WebSocket, ConnectionInfo] = {}
        
        # User-based lookup: user_id -> Set[WebSocket]
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
        # Session-based lookup: session_id -> Set[WebSocket]
        self.session_connections: Dict[str, Set[WebSocket]] = {}
        
        # Agent availability tracking
        self.available_agents: Set[str] = set()
        self.agent_workload: Dict[str, int] = {}
        
        # Typing indicators: session_id -> {user_id: typing_info}
        self.typing_indicators: Dict[str, Dict[str, Dict]] = {}
        
        # Background tasks
        self.cleanup_task = None
        self.heartbeat_task = None
        
    async def connect(self, websocket: WebSocket, user_id: str, user_type: str, session_id: str = None) -> bool:
        """Accept and register a new WebSocket connection"""
        try:
            await websocket.accept()
            
            connection_info = ConnectionInfo(websocket, user_id, user_type, session_id)
            
            # Register connection
            self.active_connections[websocket] = connection_info
            
            # Add to user lookup
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
            
            # Add to session lookup if session_id provided
            if session_id:
                if session_id not in self.session_connections:
                    self.session_connections[session_id] = set()
                self.session_connections[session_id].add(websocket)
            
            # Track agent availability
            if user_type == "agent":
                self.available_agents.add(user_id)
                if user_id not in self.agent_workload:
                    self.agent_workload[user_id] = 0
            
            # Start background tasks if this is the first connection
            if len(self.active_connections) == 1:
                await self._start_background_tasks()
            
            logger.info(f"WebSocket connected: user_id={user_id}, type={user_type}, session={session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            return False
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect and cleanup WebSocket connection"""
        if websocket not in self.active_connections:
            return
            
        connection_info = self.active_connections[websocket]
        user_id = connection_info.user_id
        session_id = connection_info.session_id
        
        # Clear typing indicator if active
        if connection_info.is_typing and session_id:
            await self._clear_typing_indicator(session_id, user_id, connection_info.user_type)
        
        # Cancel typing timeout task
        if connection_info.typing_timeout_task:
            connection_info.typing_timeout_task.cancel()
        
        # Remove from all tracking structures
        del self.active_connections[websocket]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        if session_id and session_id in self.session_connections:
            self.session_connections[session_id].discard(websocket)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        # Update agent availability
        if connection_info.user_type == "agent":
            # Only remove from available if no other connections
            if user_id not in self.user_connections:
                self.available_agents.discard(user_id)
                self.agent_workload.pop(user_id, None)
        
        # Stop background tasks if no connections remain
        if not self.active_connections:
            await self._stop_background_tasks()
        
        logger.info(f"WebSocket disconnected: user_id={user_id}, session={session_id}")
    
    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a specific user"""
        if user_id not in self.user_connections:
            return False
        
        message_json = json.dumps(message)
        failed_connections = []
        
        for websocket in self.user_connections[user_id].copy():
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Failed to send personal message to {user_id}: {e}")
                failed_connections.append(websocket)
        
        # Cleanup failed connections
        for websocket in failed_connections:
            await self.disconnect(websocket)
        
        return len(self.user_connections.get(user_id, [])) > 0
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any], exclude_user: str = None):
        """Broadcast message to all participants in a session"""
        if session_id not in self.session_connections:
            return False
        
        message_json = json.dumps(message)
        failed_connections = []
        sent_count = 0
        
        for websocket in self.session_connections[session_id].copy():
            connection_info = self.active_connections.get(websocket)
            if not connection_info:
                failed_connections.append(websocket)
                continue
                
            if exclude_user and connection_info.user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(message_json)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to session {session_id}: {e}")
                failed_connections.append(websocket)
        
        # Cleanup failed connections
        for websocket in failed_connections:
            await self.disconnect(websocket)
        
        return sent_count > 0
    
    async def broadcast_to_agents(self, message: Dict[str, Any], exclude_agent: str = None):
        """Broadcast message to all available agents"""
        message_json = json.dumps(message)
        failed_connections = []
        sent_count = 0
        
        for user_id in self.available_agents.copy():
            if exclude_agent and user_id == exclude_agent:
                continue
                
            if user_id in self.user_connections:
                for websocket in self.user_connections[user_id].copy():
                    try:
                        await websocket.send_text(message_json)
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Failed to broadcast to agent {user_id}: {e}")
                        failed_connections.append(websocket)
        
        # Cleanup failed connections
        for websocket in failed_connections:
            await self.disconnect(websocket)
        
        return sent_count > 0
    
    async def handle_typing_indicator(self, session_id: str, user_id: str, user_type: str, is_typing: bool):
        """Handle typing indicator updates"""
        try:
            connection_info = None
            
            # Find connection info for this user in this session
            for websocket, info in self.active_connections.items():
                if info.user_id == user_id and info.session_id == session_id:
                    connection_info = info
                    break
            
            if not connection_info:
                return
            
            # Cancel existing typing timeout
            if connection_info.typing_timeout_task:
                connection_info.typing_timeout_task.cancel()
                connection_info.typing_timeout_task = None
            
            connection_info.is_typing = is_typing
            
            if is_typing:
                # Set timeout to automatically clear typing indicator
                connection_info.typing_timeout_task = asyncio.create_task(
                    self._auto_clear_typing(session_id, user_id, user_type)
                )
                
                # Update typing indicators tracking
                if session_id not in self.typing_indicators:
                    self.typing_indicators[session_id] = {}
                
                self.typing_indicators[session_id][user_id] = {
                    "user_type": user_type,
                    "started_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                # Clear typing indicator
                if session_id in self.typing_indicators:
                    self.typing_indicators[session_id].pop(user_id, None)
                    if not self.typing_indicators[session_id]:
                        del self.typing_indicators[session_id]
            
            # Broadcast typing status to other session participants
            await self.broadcast_to_session(
                session_id,
                {
                    "type": "typing_indicator",
                    "user_id": user_id,
                    "user_type": user_type,
                    "is_typing": is_typing,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                exclude_user=user_id
            )
            
        except Exception as e:
            logger.error(f"Error handling typing indicator: {e}")
    
    async def update_agent_availability(self, agent_id: str, is_available: bool):
        """Update agent availability status"""
        if is_available:
            self.available_agents.add(agent_id)
        else:
            self.available_agents.discard(agent_id)
        
        # Broadcast availability change
        await self.broadcast_to_agents({
            "type": "agent_availability_changed",
            "agent_id": agent_id,
            "is_available": is_available,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Notify active sessions if agent goes offline
        if not is_available and agent_id in self.user_connections:
            for websocket in self.user_connections[agent_id]:
                connection_info = self.active_connections.get(websocket)
                if connection_info and connection_info.session_id:
                    await self.broadcast_to_session(
                        connection_info.session_id,
                        {
                            "type": "agent_unavailable",
                            "agent_id": agent_id,
                            "message": "Your agent is temporarily unavailable. We're finding another agent to assist you.",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    )
    
    def get_session_participants(self, session_id: str) -> List[Dict[str, Any]]:
        """Get information about session participants"""
        participants = []
        
        if session_id in self.session_connections:
            for websocket in self.session_connections[session_id]:
                connection_info = self.active_connections.get(websocket)
                if connection_info:
                    participants.append({
                        "user_id": connection_info.user_id,
                        "user_type": connection_info.user_type,
                        "connected_at": connection_info.connected_at.isoformat(),
                        "is_typing": connection_info.is_typing
                    })
        
        return participants
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent IDs"""
        return list(self.available_agents)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "active_sessions": len(self.session_connections),
            "available_agents": len(self.available_agents),
            "users_online": len(self.user_connections),
            "typing_sessions": len(self.typing_indicators)
        }
    
    async def _auto_clear_typing(self, session_id: str, user_id: str, user_type: str):
        """Auto-clear typing indicator after timeout"""
        await asyncio.sleep(3)  # 3 second timeout
        await self.handle_typing_indicator(session_id, user_id, user_type, False)
    
    async def _clear_typing_indicator(self, session_id: str, user_id: str, user_type: str):
        """Clear typing indicator for disconnected user"""
        if session_id in self.typing_indicators:
            self.typing_indicators[session_id].pop(user_id, None)
            if not self.typing_indicators[session_id]:
                del self.typing_indicators[session_id]
        
        await self.broadcast_to_session(
            session_id,
            {
                "type": "typing_indicator",
                "user_id": user_id,
                "user_type": user_type,
                "is_typing": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            exclude_user=user_id
        )
    
    async def _start_background_tasks(self):
        """Start background maintenance tasks"""
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        if not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def _stop_background_tasks(self):
        """Stop background maintenance tasks"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            self.cleanup_task = None
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
    
    async def _cleanup_loop(self):
        """Periodic cleanup of stale connections"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                current_time = datetime.now(timezone.utc)
                stale_connections = []
                
                for websocket, connection_info in self.active_connections.items():
                    # Mark connections as stale if no activity for 10 minutes
                    if (current_time - connection_info.last_activity).total_seconds() > 600:
                        stale_connections.append(websocket)
                
                for websocket in stale_connections:
                    logger.warning(f"Cleaning up stale connection for user {self.active_connections[websocket].user_id}")
                    await self.disconnect(websocket)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat to detect disconnected clients"""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                heartbeat_message = {
                    "type": "heartbeat",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                failed_connections = []
                
                for websocket, connection_info in self.active_connections.items():
                    try:
                        await websocket.send_text(json.dumps(heartbeat_message))
                        connection_info.last_activity = datetime.now(timezone.utc)
                    except Exception:
                        failed_connections.append(websocket)
                
                # Cleanup failed connections
                for websocket in failed_connections:
                    await self.disconnect(websocket)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

# Global WebSocket manager instance
websocket_manager = SupportWebSocketManager()