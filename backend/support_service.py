"""
Support System Service
Core business logic for multi-tiered support system with AI automation
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from ai_support_service import ai_support_service
from support_models import (
    SupportTicket, TicketResponse, ChatSession, ChatMessage, DAODispute, 
    KnowledgeBaseArticle, AITicketAnalysis, SupportDashboardData, 
    SupportSystemHealth, TicketSearchQuery, KnowledgeBaseSearchQuery,
    TicketStatus, TicketPriority, TicketCategory, ChatStatus, DisputeType,
    ChatMessageType, KnowledgeBaseType
)

logger = logging.getLogger(__name__)

class SupportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.tickets_collection = db.support_tickets
        self.ticket_responses_collection = db.ticket_responses
        self.chat_sessions_collection = db.chat_sessions
        self.chat_messages_collection = db.chat_messages
        self.dao_disputes_collection = db.dao_disputes
        self.knowledge_base_collection = db.knowledge_base_articles
        self.ai_analyses_collection = db.ai_ticket_analyses
        
    # =========== TICKETING SYSTEM ===========
    
    async def create_ticket(self, ticket_data: dict, user_id: str) -> SupportTicket:
        """Create a new support ticket with AI-powered enhancements"""
        try:
            ticket_id = str(uuid.uuid4())
            
            # Use AI to auto-categorize the ticket
            ai_analysis = await ai_support_service.auto_categorize_ticket(
                title=ticket_data["title"],
                description=ticket_data["description"]
            )
            
            # Create ticket with AI-enhanced information
            ticket = SupportTicket(
                ticket_id=ticket_id,
                user_id=user_id,
                title=ticket_data["title"],
                description=ticket_data["description"],
                category=TicketCategory(ai_analysis.get("category", ticket_data.get("category", "general_inquiry"))),
                priority=TicketPriority(ai_analysis.get("priority", ticket_data.get("priority", "medium"))),
                asset_id=ticket_data.get("asset_id"),
                user_contact_email=ticket_data.get("user_contact_email"),
                ai_tags=ai_analysis.get("tags", []),
                ai_suggested_category=ai_analysis.get("category"),
                ai_sentiment_score=0.0,  # Will be updated when first message is analyzed
                ai_summary=ai_analysis.get("suggested_response", ""),
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
            
            # Store in database
            await self.tickets_collection.insert_one(ticket.dict())
            
            # Add initial AI-generated response if confidence is high
            if ai_analysis.get("confidence", 0) > 0.8:
                await self.add_ticket_response(
                    ticket_id=ticket_id,
                    user_id="ai_assistant",
                    message=ai_analysis.get("suggested_response", ""),
                    user_type="agent"
                )
            
            # Trigger comprehensive AI analysis in background
            asyncio.create_task(self.analyze_ticket_with_ai(ticket_id))
            
            return ticket
            
        except Exception as e:
            logger.error(f"Failed to create ticket: {str(e)}")
            raise
    
    async def get_ticket(self, ticket_id: str, user_id: str) -> Optional[SupportTicket]:
        """Get ticket by ID (with user access validation)"""
        try:
            ticket_data = await self.tickets_collection.find_one({
                "ticket_id": ticket_id,
                "user_id": user_id  # Ensure user can only access their tickets
            })
            
            if ticket_data:
                if "_id" in ticket_data:
                    del ticket_data["_id"]
                return SupportTicket(**ticket_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get ticket {ticket_id}: {str(e)}")
            return None
    
    async def update_ticket_status(self, ticket_id: str, status: TicketStatus, user_id: str, agent_id: Optional[str] = None) -> bool:
        """Update ticket status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if agent_id:
                update_data["assigned_agent_id"] = agent_id
            
            if status == TicketStatus.RESOLVED:
                update_data["resolved_at"] = datetime.now(timezone.utc).isoformat()
            elif status == TicketStatus.CLOSED:
                update_data["closed_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await self.tickets_collection.update_one(
                {"ticket_id": ticket_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update ticket status: {str(e)}")
            return False
    
    async def add_ticket_response(self, ticket_id: str, user_id: str, message: str, user_type: str = "user", attachments: List[str] = []) -> TicketResponse:
        """Add response to ticket"""
        try:
            response = TicketResponse(
                ticket_id=ticket_id,
                user_id=user_id,
                user_type=user_type,
                message=message,
                attachments=attachments
            )
            
            # Store response
            await self.ticket_responses_collection.insert_one(response.dict())
            
            # Update ticket's updated_at timestamp
            await self.tickets_collection.update_one(
                {"ticket_id": ticket_id},
                {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to add ticket response: {str(e)}")
            raise
    
    async def search_tickets(self, search_query: TicketSearchQuery, user_id: str) -> Tuple[List[SupportTicket], int]:
        """Search tickets with filters and pagination"""
        try:
            # Build MongoDB query
            query = {"user_id": user_id}  # Users can only see their tickets
            
            if search_query.query:
                query["$or"] = [
                    {"title": {"$regex": search_query.query, "$options": "i"}},
                    {"description": {"$regex": search_query.query, "$options": "i"}}
                ]
            
            if search_query.category:
                query["category"] = search_query.category
            if search_query.status:
                query["status"] = search_query.status
            if search_query.priority:
                query["priority"] = search_query.priority
            
            # Date filtering
            if search_query.date_from or search_query.date_to:
                date_filter = {}
                if search_query.date_from:
                    date_filter["$gte"] = search_query.date_from.isoformat()
                if search_query.date_to:
                    date_filter["$lte"] = search_query.date_to.isoformat()
                query["created_at"] = date_filter
            
            # Count total results
            total_count = await self.tickets_collection.count_documents(query)
            
            # Get paginated results
            skip = (search_query.page - 1) * search_query.page_size
            cursor = self.tickets_collection.find(query).sort("created_at", -1).skip(skip).limit(search_query.page_size)
            
            tickets = []
            async for doc in cursor:
                if "_id" in doc:
                    del doc["_id"]
                tickets.append(SupportTicket(**doc))
            
            return tickets, total_count
            
        except Exception as e:
            logger.error(f"Failed to search tickets: {str(e)}")
            return [], 0
    
    # =========== LIVE CHAT SYSTEM ===========
    
    async def create_chat_session(self, user_id: str, initial_message: str, category: Optional[TicketCategory] = None) -> ChatSession:
        """Create new live chat session"""
        try:
            session = ChatSession(
                user_id=user_id,
                category=category
            )
            
            # Store session
            await self.chat_sessions_collection.insert_one(session.dict())
            
            # Add initial message
            initial_msg = ChatMessage(
                session_id=session.session_id,
                sender_id=user_id,
                message_type=ChatMessageType.USER_MESSAGE,
                content=initial_message
            )
            
            await self.chat_messages_collection.insert_one(initial_msg.dict())
            
            # Try to assign to available agent or AI
            await self.try_assign_chat_agent(session.session_id)
            
            logger.info(f"Created chat session {session.session_id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create chat session: {str(e)}")
            raise
    
    async def add_chat_message(self, session_id: str, sender_id: str, message_type: ChatMessageType, content: str) -> ChatMessage:
        """Add message to chat session"""
        try:
            message = ChatMessage(
                session_id=session_id,
                sender_id=sender_id,
                message_type=message_type,
                content=content
            )
            
            await self.chat_messages_collection.insert_one(message.dict())
            
            # If user message, trigger AI auto-response if no agent available
            if message_type == ChatMessageType.USER_MESSAGE:
                asyncio.create_task(self.try_ai_auto_response(session_id, content))
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to add chat message: {str(e)}")
            raise
    
    async def get_chat_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        try:
            session_data = await self.chat_sessions_collection.find_one({
                "session_id": session_id,
                "user_id": user_id
            })
            
            if session_data:
                if "_id" in session_data:
                    del session_data["_id"]
                return ChatSession(**session_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chat session: {str(e)}")
            return None
    
    async def get_chat_messages(self, session_id: str, user_id: str) -> List[ChatMessage]:
        """Get all messages for a chat session"""
        try:
            # Verify user has access to session
            session = await self.get_chat_session(session_id, user_id)
            if not session:
                return []
            
            cursor = self.chat_messages_collection.find(
                {"session_id": session_id}
            ).sort("timestamp", 1)
            
            messages = []
            async for doc in cursor:
                if "_id" in doc:
                    del doc["_id"]
                messages.append(ChatMessage(**doc))
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get chat messages: {str(e)}")
            return []
    
    async def end_chat_session(self, session_id: str, user_id: str, satisfaction_rating: Optional[int] = None) -> bool:
        """End chat session"""
        try:
            update_data = {
                "status": ChatStatus.ENDED,
                "ended_at": datetime.now(timezone.utc).isoformat()
            }
            
            if satisfaction_rating:
                update_data["user_satisfaction_rating"] = satisfaction_rating
            
            result = await self.chat_sessions_collection.update_one(
                {"session_id": session_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to end chat session: {str(e)}")
            return False
    
    # =========== DAO ARBITRATION SYSTEM ===========
    
    async def create_dao_dispute(self, dispute_data: dict, user_id: str) -> DAODispute:
        """Create DAO dispute for arbitration"""
        try:
            dispute = DAODispute(
                created_by_user_id=user_id,
                **dispute_data
            )
            
            # Store in database
            await self.dao_disputes_collection.insert_one(dispute.dict())
            
            # Trigger AI evidence analysis
            if dispute.evidence_files:
                asyncio.create_task(self.analyze_dispute_evidence(dispute.dispute_id))
            
            # Initialize DAO voting process
            await self.initialize_dao_voting(dispute.dispute_id)
            
            logger.info(f"Created DAO dispute {dispute.dispute_id} by user {user_id}")
            return dispute
            
        except Exception as e:
            logger.error(f"Failed to create DAO dispute: {str(e)}")
            raise
    
    async def get_dao_dispute(self, dispute_id: str) -> Optional[DAODispute]:
        """Get DAO dispute by ID"""
        try:
            dispute_data = await self.dao_disputes_collection.find_one({"dispute_id": dispute_id})
            
            if dispute_data:
                if "_id" in dispute_data:
                    del dispute_data["_id"]
                return DAODispute(**dispute_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get DAO dispute: {str(e)}")
            return None
    
    async def escalate_ticket_to_dao(self, ticket_id: str, user_id: str) -> Optional[DAODispute]:
        """Escalate support ticket to DAO arbitration"""
        try:
            # Get ticket details
            ticket = await self.get_ticket(ticket_id, user_id)
            if not ticket:
                return None
            
            # Create DAO dispute from ticket
            dispute_data = {
                "ticket_id": ticket_id,
                "title": f"Escalated: {ticket.title}",
                "description": ticket.description,
                "dispute_type": DisputeType.LICENSING_TERMS,  # Default type
                "involved_parties": [user_id],
                "asset_id": ticket.asset_id,
                "requested_resolution": f"Resolution requested for ticket {ticket_id}"
            }
            
            dispute = await self.create_dao_dispute(dispute_data, user_id)
            
            # Update ticket status
            await self.update_ticket_status(ticket_id, TicketStatus.ESCALATED_TO_DAO, user_id)
            await self.tickets_collection.update_one(
                {"ticket_id": ticket_id},
                {"$set": {"dao_dispute_id": dispute.dispute_id, "escalated_to_dao": True}}
            )
            
            return dispute
            
        except Exception as e:
            logger.error(f"Failed to escalate ticket to DAO: {str(e)}")
            return None
    
    # =========== KNOWLEDGE BASE SYSTEM ===========
    
    async def create_knowledge_base_article(self, article_data: dict, author_id: str) -> KnowledgeBaseArticle:
        """Create new knowledge base article"""
        try:
            article = KnowledgeBaseArticle(
                author_id=author_id,
                **article_data
            )
            
            # Store in database
            await self.knowledge_base_collection.insert_one(article.dict())
            
            # Trigger AI enhancement
            asyncio.create_task(self.enhance_article_with_ai(article.article_id))
            
            logger.info(f"Created KB article {article.article_id}")
            return article
            
        except Exception as e:
            logger.error(f"Failed to create KB article: {str(e)}")
            raise
    
    async def search_knowledge_base(self, search_query: KnowledgeBaseSearchQuery) -> Tuple[List[KnowledgeBaseArticle], int]:
        """Search knowledge base articles"""
        try:
            # Build query
            query = {"is_public": True, "approved": True}  # Only show public, approved articles
            
            if search_query.query:
                query["$or"] = [
                    {"title": {"$regex": search_query.query, "$options": "i"}},
                    {"content": {"$regex": search_query.query, "$options": "i"}},
                    {"tags": {"$in": [search_query.query]}},
                    {"ai_tags": {"$in": [search_query.query]}}
                ]
            
            if search_query.article_type:
                query["article_type"] = search_query.article_type
            if search_query.category:
                query["category"] = search_query.category
            if search_query.is_featured is not None:
                query["is_featured"] = search_query.is_featured
            
            # Count total
            total_count = await self.knowledge_base_collection.count_documents(query)
            
            # Get paginated results
            skip = (search_query.page - 1) * search_query.page_size
            cursor = self.knowledge_base_collection.find(query).sort([
                ("is_featured", -1),  # Featured first
                ("view_count", -1),   # Most viewed next
                ("created_at", -1)    # Newest last
            ]).skip(skip).limit(search_query.page_size)
            
            articles = []
            async for doc in cursor:
                if "_id" in doc:
                    del doc["_id"]
                articles.append(KnowledgeBaseArticle(**doc))
            
            return articles, total_count
            
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {str(e)}")
            return [], 0
    
    async def get_knowledge_base_article(self, article_id: str) -> Optional[KnowledgeBaseArticle]:
        """Get knowledge base article and increment view count"""
        try:
            # Increment view count
            await self.knowledge_base_collection.update_one(
                {"article_id": article_id},
                {"$inc": {"view_count": 1}}
            )
            
            # Get article
            article_data = await self.knowledge_base_collection.find_one({"article_id": article_id})
            
            if article_data:
                if "_id" in article_data:
                    del article_data["_id"]
                return KnowledgeBaseArticle(**article_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get KB article: {str(e)}")
            return None
    
    # =========== AI AUTOMATION SYSTEM ===========
    
    async def analyze_ticket_with_ai(self, ticket_id: str) -> AITicketAnalysis:
        """Analyze ticket with AI for auto-categorization and suggestions"""
        try:
            # Get ticket
            ticket_data = await self.tickets_collection.find_one({"ticket_id": ticket_id})
            if not ticket_data:
                raise ValueError("Ticket not found")
            
            # Simulate AI analysis (replace with actual AI service call)
            analysis = AITicketAnalysis(
                ticket_id=ticket_id,
                suggested_category=TicketCategory.TECHNICAL_SUPPORT,
                suggested_priority=TicketPriority.MEDIUM,
                confidence_score=0.85,
                sentiment_score=0.2,
                sentiment_label="neutral",
                detected_tags=["account", "access", "login"],
                summary="User experiencing technical issues with platform access",
                key_issues=["Authentication error", "Account lockout"],
                suggested_actions=["Reset password", "Check account status"],
                escalation_recommended=False
            )
            
            # Store analysis
            await self.ai_analyses_collection.insert_one(analysis.dict())
            
            # Update ticket with AI insights
            await self.tickets_collection.update_one(
                {"ticket_id": ticket_id},
                {"$set": {
                    "ai_tags": analysis.detected_tags,
                    "ai_suggested_category": analysis.suggested_category,
                    "ai_sentiment_score": analysis.sentiment_score,
                    "ai_summary": analysis.summary
                }}
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze ticket with AI: {str(e)}")
            raise
    
    async def suggest_kb_articles_for_query(self, query: str, limit: int = 5) -> List[str]:
        """AI-powered KB article suggestions"""
        try:
            # Simple keyword matching (replace with AI semantic search)
            search_query = KnowledgeBaseSearchQuery(
                query=query,
                page_size=limit
            )
            
            articles, _ = await self.search_knowledge_base(search_query)
            return [article.article_id for article in articles]
            
        except Exception as e:
            logger.error(f"Failed to suggest KB articles: {str(e)}")
            return []
    
    # =========== DASHBOARD & ANALYTICS ===========
    
    async def get_user_support_dashboard(self, user_id: str) -> SupportDashboardData:
        """Get comprehensive support dashboard for user"""
        try:
            # Get ticket statistics
            total_tickets = await self.tickets_collection.count_documents({"user_id": user_id})
            open_tickets = await self.tickets_collection.count_documents({"user_id": user_id, "status": {"$in": ["open", "in_progress"]}})
            resolved_tickets = await self.tickets_collection.count_documents({"user_id": user_id, "status": "resolved"})
            
            # Get recent tickets
            recent_tickets_cursor = self.tickets_collection.find({"user_id": user_id}).sort("created_at", -1).limit(5)
            recent_tickets = []
            async for doc in recent_tickets_cursor:
                if "_id" in doc:
                    del doc["_id"]
                recent_tickets.append(SupportTicket(**doc))
            
            # Get recent chat messages
            recent_messages = []  # Simplified for now
            
            # Get active disputes
            active_disputes_cursor = self.dao_disputes_collection.find({"created_by_user_id": user_id, "resolved_at": None}).limit(3)
            active_disputes = []
            async for doc in active_disputes_cursor:
                if "_id" in doc:
                    del doc["_id"]
                active_disputes.append(DAODispute(**doc))
            
            dashboard = SupportDashboardData(
                user_id=user_id,
                total_tickets=total_tickets,
                open_tickets=open_tickets,
                resolved_tickets=resolved_tickets,
                avg_resolution_time_hours=24.0,  # Placeholder
                recent_tickets=recent_tickets,
                recent_messages=recent_messages,
                active_disputes=active_disputes,
                voting_participations=0  # Placeholder
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get user dashboard: {str(e)}")
            raise
    
    async def get_system_health(self) -> SupportSystemHealth:
        """Get overall support system health and statistics"""
        try:
            # Count statistics
            total_active_tickets = await self.tickets_collection.count_documents({"status": {"$in": ["open", "in_progress"]}})
            total_active_chats = await self.chat_sessions_collection.count_documents({"status": {"$in": ["waiting", "connected"]}})
            total_kb_articles = await self.knowledge_base_collection.count_documents({"approved": True, "is_public": True})
            total_active_disputes = await self.dao_disputes_collection.count_documents({"resolved_at": None})
            
            health = SupportSystemHealth(
                total_active_tickets=total_active_tickets,
                total_active_chats=total_active_chats,
                total_kb_articles=total_kb_articles,
                total_active_disputes=total_active_disputes
            )
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            raise
    
    # =========== HELPER METHODS ===========
    
    async def try_assign_chat_agent(self, session_id: str):
        """Try to assign available agent to chat session"""
        # Simplified - in production, this would check agent availability
        pass
    
    async def try_ai_auto_response(self, session_id: str, user_message: str):
        """Generate AI auto-response if no agent available"""
        try:
            # Suggest KB articles based on user message
            suggested_articles = await self.suggest_kb_articles_for_query(user_message)
            
            if suggested_articles:
                # Generate AI response with article suggestions
                ai_response = f"I found some helpful articles that might answer your question. Here are some suggestions: {', '.join(suggested_articles[:3])}"
                
                await self.add_chat_message(
                    session_id=session_id,
                    sender_id="ai_assistant",
                    message_type=ChatMessageType.AI_MESSAGE,
                    content=ai_response
                )
        except Exception as e:
            logger.error(f"Failed to generate AI auto-response: {str(e)}")
    
    async def initialize_dao_voting(self, dispute_id: str):
        """Initialize DAO voting process for dispute"""
        try:
            # Update dispute with voting details
            voting_starts = datetime.now(timezone.utc)
            voting_ends = voting_starts + timedelta(days=7)
            
            await self.dao_disputes_collection.update_one(
                {"dispute_id": dispute_id},
                {"$set": {
                    "voting_started_at": voting_starts.isoformat(),
                    "voting_ends_at": voting_ends.isoformat()
                }}
            )
            
            logger.info(f"Initialized DAO voting for dispute {dispute_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize DAO voting: {str(e)}")
    
    async def analyze_dispute_evidence(self, dispute_id: str):
        """AI analysis of dispute evidence files"""
        try:
            # Get dispute
            dispute = await self.get_dao_dispute(dispute_id)
            if not dispute or not dispute.evidence_files:
                return
            
            # Simulate AI evidence analysis
            evidence_summary = "AI analysis of uploaded evidence files shows potential licensing violation with supporting documentation."
            
            # Update dispute with AI analysis
            await self.dao_disputes_collection.update_one(
                {"dispute_id": dispute_id},
                {"$set": {"evidence_summary": evidence_summary}}
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze dispute evidence: {str(e)}")
    
    async def enhance_article_with_ai(self, article_id: str):
        """Enhance knowledge base article with AI-generated tags and related articles"""
        try:
            article = await self.get_knowledge_base_article(article_id)
            if not article:
                return
            
            # Simulate AI enhancement
            ai_tags = ["support", "guide", "tutorial"]
            ai_summary = "This article provides guidance on platform usage."
            
            # Update article
            await self.knowledge_base_collection.update_one(
                {"article_id": article_id},
                {"$set": {
                    "ai_tags": ai_tags,
                    "ai_summary": ai_summary
                }}
            )
            
        except Exception as e:
            logger.error(f"Failed to enhance article with AI: {str(e)}")