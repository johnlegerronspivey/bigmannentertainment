"""
Support System Models
Multi-Tiered Support System with Live Chat, Ticketing, DAO Arbitration, Knowledge Base & AI Automation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

# Enums for Support System

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_USER = "pending_user"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED_TO_DAO = "escalated_to_dao"

class TicketCategory(str, Enum):
    TECHNICAL_SUPPORT = "technical_support"
    LICENSING_DISPUTE = "licensing_dispute"
    ROYALTY_ISSUE = "royalty_issue"
    PLATFORM_BUG = "platform_bug"
    CONTENT_REMOVAL = "content_removal"
    PAYMENT_ISSUE = "payment_issue"
    ACCOUNT_ACCESS = "account_access"
    GENERAL_INQUIRY = "general_inquiry"
    DAO_GOVERNANCE = "dao_governance"
    SMART_CONTRACT = "smart_contract"

class ChatMessageType(str, Enum):
    USER_MESSAGE = "user_message"
    AGENT_MESSAGE = "agent_message"
    SYSTEM_MESSAGE = "system_message"
    AI_MESSAGE = "ai_message"

class DisputeType(str, Enum):
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    ROYALTY_CALCULATION = "royalty_calculation"
    LICENSING_TERMS = "licensing_terms"
    PLATFORM_VIOLATION = "platform_violation"
    CONTENT_AUTHENTICITY = "content_authenticity"
    SMART_CONTRACT_BREACH = "smart_contract_breach"

class KnowledgeBaseType(str, Enum):
    FAQ = "faq"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    API_DOCS = "api_docs"
    TROUBLESHOOTING = "troubleshooting"
    ONBOARDING = "onboarding"

class ChatStatus(str, Enum):
    WAITING = "waiting"
    CONNECTED = "connected"
    TRANSFERRED = "transferred"
    ENDED = "ended"

# Support Ticket Models

class SupportTicketDto(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    asset_id: Optional[str] = None
    related_content_id: Optional[str] = None
    user_contact_email: Optional[str] = None
    attachments: Optional[List[str]] = []  # File URLs
    metadata: Optional[Dict[str, Any]] = {}

class SupportTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus = TicketStatus.OPEN
    assigned_agent_id: Optional[str] = None
    asset_id: Optional[str] = None
    related_content_id: Optional[str] = None
    user_contact_email: Optional[str] = None
    attachments: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # DAO Integration
    dao_dispute_id: Optional[str] = None
    escalated_to_dao: bool = False
    dao_resolution: Optional[str] = None
    
    # AI Analysis
    ai_tags: List[str] = []
    ai_suggested_category: Optional[TicketCategory] = None
    ai_sentiment_score: Optional[float] = None
    ai_summary: Optional[str] = None

# Ticket Response Models

class TicketResponse(BaseModel):
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: str
    user_id: str  # Could be agent or user
    user_type: str  # "user", "agent", "system", "ai"
    message: str
    attachments: List[str] = []
    is_internal_note: bool = False  # For agent-only notes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # AI Analysis
    ai_sentiment_score: Optional[float] = None
    ai_suggested_actions: List[str] = []

# Live Chat Models

class ChatRequestDto(BaseModel):
    initial_message: str = Field(..., min_length=1, max_length=1000)
    category: Optional[TicketCategory] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    user_context: Optional[Dict[str, Any]] = {}

class ChatSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    agent_id: Optional[str] = None
    status: ChatStatus = ChatStatus.WAITING
    category: Optional[TicketCategory] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    
    # Session metadata
    user_context: Dict[str, Any] = {}
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    agent_response_time_avg: Optional[float] = None
    
    # Post-chat
    user_satisfaction_rating: Optional[int] = None  # 1-5 stars
    created_ticket_id: Optional[str] = None  # If chat escalated to ticket

class ChatMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    sender_id: str
    message_type: ChatMessageType
    content: str
    attachments: List[str] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # AI Features
    ai_auto_response: bool = False
    ai_confidence_score: Optional[float] = None
    read_by_recipient: bool = False

# DAO Arbitration Models

class DisputeDto(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)
    dispute_type: DisputeType
    involved_parties: List[str]  # User IDs
    asset_id: Optional[str] = None
    smart_contract_address: Optional[str] = None
    evidence_files: List[str] = []
    requested_resolution: str = Field(..., min_length=20, max_length=2000)

class DAODispute(BaseModel):
    dispute_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: Optional[str] = None  # Link to support ticket
    created_by_user_id: str
    title: str
    description: str
    dispute_type: DisputeType
    
    # Involved Parties
    involved_parties: List[str] = []  # User IDs
    asset_id: Optional[str] = None
    smart_contract_address: Optional[str] = None
    
    # Evidence
    evidence_files: List[str] = []
    evidence_summary: Optional[str] = None  # AI-generated
    
    # DAO Governance
    dao_proposal_id: Optional[str] = None
    voting_threshold: float = 0.6  # 60% approval needed
    voting_period_days: int = 7
    
    # Resolution
    requested_resolution: str
    final_resolution: Optional[str] = None
    resolution_approved: Optional[bool] = None
    compensation_amount: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    voting_started_at: Optional[datetime] = None
    voting_ends_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Blockchain Integration
    blockchain_tx_hash: Optional[str] = None
    smart_contract_updated: bool = False

# Knowledge Base Models

class KnowledgeBaseDto(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=50, max_length=50000)
    article_type: KnowledgeBaseType
    tags: List[str] = []
    category: Optional[str] = None
    is_featured: bool = False
    is_public: bool = True

class KnowledgeBaseArticle(BaseModel):
    article_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str  # Markdown supported
    article_type: KnowledgeBaseType
    tags: List[str] = []
    category: Optional[str] = None
    
    # Visibility & Organization
    is_featured: bool = False
    is_public: bool = True
    display_order: int = 0
    
    # Authorship & Approval
    author_id: str
    reviewed_by_id: Optional[str] = None
    approved: bool = False
    
    # Analytics
    view_count: int = 0
    helpful_votes: int = 0
    unhelpful_votes: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    
    # AI Enhancement
    ai_summary: Optional[str] = None
    ai_tags: List[str] = []
    related_articles: List[str] = []  # Article IDs

# AI Automation Models

class AITicketAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: str
    
    # Classification
    suggested_category: TicketCategory
    suggested_priority: TicketPriority
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    
    # Sentiment Analysis
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)  # -1 (negative) to 1 (positive)
    sentiment_label: str  # "positive", "neutral", "negative"
    
    # Auto-tagging
    detected_tags: List[str] = []
    suggested_kb_articles: List[str] = []  # Article IDs
    
    # Content Analysis
    summary: str
    key_issues: List[str] = []
    suggested_actions: List[str] = []
    escalation_recommended: bool = False
    
    # Processing Info
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ai_model_used: str = "gpt-4"
    processing_time_ms: Optional[int] = None

# Response Models

class SupportDashboardData(BaseModel):
    user_id: str
    
    # Ticket Statistics
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    avg_resolution_time_hours: float
    
    # Recent Activity
    recent_tickets: List[SupportTicket]
    recent_messages: List[ChatMessage]
    
    # Knowledge Base Usage
    viewed_articles: List[str] = []  # Article IDs
    bookmarked_articles: List[str] = []
    
    # DAO Participation
    active_disputes: List[DAODispute]
    voting_participations: int
    
    # System Health
    system_status: str = "operational"
    support_queue_length: int = 0
    avg_response_time_minutes: int = 5

class SupportSystemHealth(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Service Status
    live_chat_active: bool = True
    ticketing_system_active: bool = True
    dao_integration_active: bool = True
    knowledge_base_active: bool = True
    ai_automation_active: bool = True
    
    # Statistics
    total_active_tickets: int = 0
    total_active_chats: int = 0
    total_kb_articles: int = 0
    total_active_disputes: int = 0
    
    # Performance Metrics
    avg_ticket_resolution_time_hours: float = 24.0
    avg_chat_response_time_minutes: float = 2.5
    system_uptime_percentage: float = 99.9
    user_satisfaction_score: float = 4.2  # Out of 5

# Search and Filter Models

class TicketSearchQuery(BaseModel):
    query: Optional[str] = None
    category: Optional[TicketCategory] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class KnowledgeBaseSearchQuery(BaseModel):
    query: Optional[str] = None
    article_type: Optional[KnowledgeBaseType] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)