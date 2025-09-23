"""
Support System API Endpoints
Multi-Tiered Support System: Live Chat, Ticketing, DAO Arbitration, Knowledge Base & AI Automation
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import logging
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import os

from support_models import (
    SupportTicketDto, SupportTicket, TicketResponse, ChatRequestDto, ChatSession,
    ChatMessage, DisputeDto, DAODispute, KnowledgeBaseDto, KnowledgeBaseArticle,
    AITicketAnalysis, SupportDashboardData, SupportSystemHealth,
    TicketSearchQuery, KnowledgeBaseSearchQuery, TicketStatus, TicketPriority,
    TicketCategory, ChatStatus, ChatMessageType, DisputeType, KnowledgeBaseType
)
from support_service import SupportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support", tags=["Support System"])

# Authentication setup
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bigmann_entertainment')]

# Initialize support service
support_service = SupportService(db)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return {"id": user_id, "username": user.get("username", ""), "is_admin": user.get("is_admin", False)}

# WebSocket connection manager for real-time chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    async def connect(self, websocket: WebSocket, user_id: str, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.user_sessions[user_id] = session_id
        logger.info(f"User {user_id} connected to chat session {session_id}")
    
    def disconnect(self, session_id: str, user_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"User {user_id} disconnected from session {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to session {session_id}: {e}")

manager = ConnectionManager()

# =========== SYSTEM HEALTH & OVERVIEW ===========

@router.get("/health", response_model=SupportSystemHealth)
async def get_support_system_health():
    """Get support system health and statistics"""
    try:
        health = await support_service.get_system_health()
        return health
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

@router.get("/dashboard", response_model=SupportDashboardData)
async def get_support_dashboard(current_user: dict = Depends(get_current_user)):
    """Get user's comprehensive support dashboard"""
    try:
        dashboard = await support_service.get_user_support_dashboard(current_user["id"])
        return dashboard
    except Exception as e:
        logger.error(f"Failed to get support dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

# =========== TICKETING SYSTEM ===========

@router.post("/tickets", response_model=SupportTicket)
async def create_support_ticket(
    ticket: SupportTicketDto,
    current_user: dict = Depends(get_current_user)
):
    """Create new support ticket"""
    try:
        new_ticket = await support_service.create_ticket(ticket.dict(), current_user["id"])
        return new_ticket
    except Exception as e:
        logger.error(f"Failed to create ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")

@router.get("/tickets/{ticket_id}", response_model=SupportTicket)
async def get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific support ticket"""
    try:
        ticket = await support_service.get_ticket(ticket_id, current_user["id"])
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticket: {str(e)}")

@router.get("/tickets", response_model=Dict[str, Any])
async def search_tickets(
    query: Optional[str] = Query(None),
    category: Optional[TicketCategory] = Query(None),
    status: Optional[TicketStatus] = Query(None),
    priority: Optional[TicketPriority] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Search and filter support tickets"""
    try:
        search_query = TicketSearchQuery(
            query=query,
            category=category,
            status=status,
            priority=priority,
            page=page,
            page_size=page_size
        )
        
        tickets, total_count = await support_service.search_tickets(search_query, current_user["id"])
        
        return {
            "tickets": tickets,
            "pagination": {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"Failed to search tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search tickets: {str(e)}")

@router.put("/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    status: TicketStatus,
    current_user: dict = Depends(get_current_user)
):
    """Update ticket status"""
    try:
        success = await support_service.update_ticket_status(ticket_id, status, current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Ticket not found or no permission")
        
        return {"success": True, "message": f"Ticket status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update ticket status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

@router.post("/tickets/{ticket_id}/responses", response_model=TicketResponse)
async def add_ticket_response(
    ticket_id: str,
    message: str = Form(...),
    attachments: Optional[List[UploadFile]] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Add response to support ticket"""
    try:
        # Handle file uploads (simplified - store file paths)
        attachment_paths = []
        if attachments:
            for file in attachments:
                # In production, upload to cloud storage
                file_path = f"/uploads/tickets/{ticket_id}/{file.filename}"
                attachment_paths.append(file_path)
        
        response = await support_service.add_ticket_response(
            ticket_id, current_user["id"], message, "user", attachment_paths
        )
        return response
    except Exception as e:
        logger.error(f"Failed to add ticket response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add response: {str(e)}")

@router.post("/tickets/{ticket_id}/escalate-to-dao", response_model=DAODispute)
async def escalate_ticket_to_dao(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Escalate support ticket to DAO arbitration"""
    try:
        dispute = await support_service.escalate_ticket_to_dao(ticket_id, current_user["id"])
        if not dispute:
            raise HTTPException(status_code=404, detail="Ticket not found or cannot be escalated")
        return dispute
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to escalate ticket to DAO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to escalate: {str(e)}")

# =========== LIVE CHAT SYSTEM ===========

@router.post("/chat/sessions", response_model=ChatSession)
async def create_chat_session(
    chat_request: ChatRequestDto,
    current_user: dict = Depends(get_current_user)
):
    """Create new live chat session"""
    try:
        session = await support_service.create_chat_session(
            current_user["id"], 
            chat_request.initial_message,
            chat_request.category
        )
        return session
    except Exception as e:
        logger.error(f"Failed to create chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")

@router.get("/chat/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get chat session details"""
    try:
        session = await support_service.get_chat_session(session_id, current_user["id"])
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_chat_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all messages for a chat session"""
    try:
        messages = await support_service.get_chat_messages(session_id, current_user["id"])
        return messages
    except Exception as e:
        logger.error(f"Failed to get chat messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.put("/chat/sessions/{session_id}/end")
async def end_chat_session(
    session_id: str,
    satisfaction_rating: Optional[int] = Form(None, ge=1, le=5),
    current_user: dict = Depends(get_current_user)
):
    """End chat session with optional satisfaction rating"""
    try:
        success = await support_service.end_chat_session(session_id, current_user["id"], satisfaction_rating)
        if not success:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Disconnect WebSocket if active
        manager.disconnect(session_id, current_user["id"])
        
        return {"success": True, "message": "Chat session ended successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

# WebSocket endpoint for real-time chat
@router.websocket("/chat/sessions/{session_id}/ws")
async def websocket_chat(websocket: WebSocket, session_id: str, user_id: str):
    """WebSocket endpoint for real-time chat"""
    try:
        # Connect to WebSocket
        await manager.connect(websocket, user_id, session_id)
        
        # Verify session exists and user has access
        session = await support_service.get_chat_session(session_id, user_id)
        if not session:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        # Handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "chat_message":
                    # Add message to database
                    message = await support_service.add_chat_message(
                        session_id=session_id,
                        sender_id=user_id,
                        message_type=ChatMessageType.USER_MESSAGE,
                        content=message_data.get("content", "")
                    )
                    
                    # Broadcast message back to confirm receipt
                    await manager.send_message(session_id, {
                        "type": "message_sent",
                        "message": message.dict()
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error in session {session_id}: {e}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(session_id, user_id)

# =========== DAO ARBITRATION SYSTEM ===========

@router.post("/dao/disputes", response_model=DAODispute)
async def create_dao_dispute(
    dispute: DisputeDto,
    current_user: dict = Depends(get_current_user)
):
    """Create new DAO dispute for arbitration"""
    try:
        new_dispute = await support_service.create_dao_dispute(dispute.dict(), current_user["id"])
        return new_dispute
    except Exception as e:
        logger.error(f"Failed to create DAO dispute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create dispute: {str(e)}")

@router.get("/dao/disputes/{dispute_id}", response_model=DAODispute)
async def get_dao_dispute(
    dispute_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get DAO dispute details"""
    try:
        dispute = await support_service.get_dao_dispute(dispute_id)
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
        
        # Check if user has access (involved party or admin)
        if (current_user["id"] not in dispute.involved_parties and 
            dispute.created_by_user_id != current_user["id"] and 
            not current_user.get("is_admin", False)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return dispute
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get DAO dispute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dispute: {str(e)}")

@router.get("/dao/disputes", response_model=List[DAODispute])
async def get_user_dao_disputes(
    current_user: dict = Depends(get_current_user)
):
    """Get user's DAO disputes"""
    try:
        # Find disputes where user is involved
        cursor = db.dao_disputes.find({
            "$or": [
                {"created_by_user_id": current_user["id"]},
                {"involved_parties": current_user["id"]}
            ]
        }).sort("created_at", -1)
        
        disputes = []
        async for doc in cursor:
            if "_id" in doc:
                del doc["_id"]
            disputes.append(DAODispute(**doc))
        
        return disputes
    except Exception as e:
        logger.error(f"Failed to get user disputes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get disputes: {str(e)}")

# =========== KNOWLEDGE BASE SYSTEM ===========

@router.post("/knowledge-base/articles", response_model=KnowledgeBaseArticle)
async def create_knowledge_base_article(
    article: KnowledgeBaseDto,
    current_user: dict = Depends(get_current_user)
):
    """Create new knowledge base article"""
    try:
        new_article = await support_service.create_knowledge_base_article(article.dict(), current_user["id"])
        return new_article
    except Exception as e:
        logger.error(f"Failed to create KB article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")

@router.get("/knowledge-base/articles/{article_id}", response_model=KnowledgeBaseArticle)
async def get_knowledge_base_article(article_id: str):
    """Get knowledge base article (increments view count)"""
    try:
        article = await support_service.get_knowledge_base_article(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get KB article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get article: {str(e)}")

@router.get("/knowledge-base/articles", response_model=Dict[str, Any])
async def search_knowledge_base(
    query: Optional[str] = Query(None),
    article_type: Optional[KnowledgeBaseType] = Query(None),
    category: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    is_featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Search knowledge base articles"""
    try:
        search_query = KnowledgeBaseSearchQuery(
            query=query,
            article_type=article_type,
            category=category,
            tags=tags,
            is_featured=is_featured,
            page=page,
            page_size=page_size
        )
        
        articles, total_count = await support_service.search_knowledge_base(search_query)
        
        return {
            "articles": articles,
            "pagination": {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"Failed to search knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search: {str(e)}")

# =========== AI AUTOMATION SYSTEM ===========

@router.get("/ai/suggestions/kb-articles")
async def get_ai_kb_suggestions(
    query: str = Query(..., min_length=3),
    limit: int = Query(5, ge=1, le=10)
):
    """Get AI-powered knowledge base article suggestions"""
    try:
        article_ids = await support_service.suggest_kb_articles_for_query(query, limit)
        
        # Get full article details
        suggestions = []
        for article_id in article_ids:
            article = await support_service.get_knowledge_base_article(article_id)
            if article:
                suggestions.append({
                    "article_id": article.article_id,
                    "title": article.title,
                    "article_type": article.article_type,
                    "tags": article.tags,
                    "helpful_votes": article.helpful_votes
                })
        
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Failed to get AI KB suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/ai/analysis/ticket/{ticket_id}", response_model=AITicketAnalysis)
async def get_ticket_ai_analysis(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get AI analysis for a support ticket"""
    try:
        # Verify ticket access
        ticket = await support_service.get_ticket(ticket_id, current_user["id"])
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Get AI analysis
        analysis_data = await db.ai_ticket_analyses.find_one({"ticket_id": ticket_id})
        if not analysis_data:
            # Trigger analysis if not exists
            analysis = await support_service.analyze_ticket_with_ai(ticket_id)
        else:
            if "_id" in analysis_data:
                del analysis_data["_id"]
            analysis = AITicketAnalysis(**analysis_data)
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ticket AI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")

# =========== ADMIN ENDPOINTS (FOR AGENTS) ===========

@router.get("/admin/tickets/queue", response_model=List[SupportTicket])
async def get_agent_ticket_queue(
    status: Optional[TicketStatus] = Query(TicketStatus.OPEN),
    priority: Optional[TicketPriority] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get ticket queue for support agents (admin only)"""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Build query for unassigned tickets
        query = {"assigned_agent_id": None}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        
        cursor = db.support_tickets.find(query).sort([
            ("priority", -1),  # High priority first
            ("created_at", 1)   # Oldest first
        ]).limit(limit)
        
        tickets = []
        async for doc in cursor:
            if "_id" in doc:
                del doc["_id"]
            tickets.append(SupportTicket(**doc))
        
        return tickets
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue: {str(e)}")

@router.put("/admin/tickets/{ticket_id}/assign")
async def assign_ticket_to_agent(
    ticket_id: str,
    agent_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Assign ticket to agent (admin only)"""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # If no agent_id provided, assign to current admin
        if not agent_id:
            agent_id = current_user["id"]
        
        result = await db.support_tickets.update_one(
            {"ticket_id": ticket_id},
            {"$set": {
                "assigned_agent_id": agent_id,
                "status": TicketStatus.IN_PROGRESS,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {"success": True, "message": f"Ticket assigned to agent {agent_id}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assign: {str(e)}")