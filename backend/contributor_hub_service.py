"""
Big Mann Entertainment - Contributor Hub Service
Phase 4: Advanced Features - Contributor Hub Backend
"""

import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContributorRole(str, Enum):
    ARTIST = "artist"
    PRODUCER = "producer"
    SONGWRITER = "songwriter"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    MIXER = "mixer"
    MASTERING_ENGINEER = "mastering_engineer"
    COMPOSER = "composer"
    LYRICIST = "lyricist"
    PERFORMER = "performer"

class CollaborationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"

class ContributorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

# Pydantic Models
class ContributorProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    stage_name: str
    real_name: Optional[str] = None
    bio: str = ""
    roles: List[ContributorRole]
    skills: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    contact_info: Dict[str, str] = Field(default_factory=dict)
    social_links: Dict[str, str] = Field(default_factory=dict)
    portfolio_urls: List[str] = Field(default_factory=list)
    hourly_rate: Optional[float] = None
    availability: str = "available"  # available, busy, unavailable
    rating: float = 0.0
    total_collaborations: int = 0
    successful_projects: int = 0
    status: ContributorStatus = ContributorStatus.ACTIVE
    verification_level: str = "basic"  # basic, verified, premium
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CollaborationRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str
    to_user_id: str
    project_title: str
    project_description: str
    required_roles: List[ContributorRole]
    budget_range: Optional[Dict[str, float]] = None  # {"min": 500, "max": 2000}
    timeline: Optional[str] = None
    deliverables: List[str] = Field(default_factory=list)
    status: CollaborationStatus = CollaborationStatus.PENDING
    message: Optional[str] = None
    terms: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    responded_at: Optional[datetime] = None
    response_message: Optional[str] = None

class Collaboration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    project_title: str
    participants: List[str]  # user_ids
    roles_assignment: Dict[str, ContributorRole]  # user_id -> role
    status: CollaborationStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_total: Optional[float] = None
    payment_splits: Dict[str, float] = Field(default_factory=dict)  # user_id -> percentage
    deliverables: List[Dict[str, Any]] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    communication_channel: Optional[str] = None
    assets_shared: List[str] = Field(default_factory=list)  # asset_ids
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContributorPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contributor_id: str
    collaboration_id: Optional[str] = None
    amount: float
    currency: str = "USD"
    payment_type: str = "collaboration"  # collaboration, royalty, bonus
    status: PaymentStatus = PaymentStatus.PENDING
    description: str
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    tax_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContributorReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_id: str
    reviewer_id: str
    reviewee_id: str
    rating: float  # 1-5 stars
    review_text: Optional[str] = None
    categories: Dict[str, float] = Field(default_factory=dict)  # communication, quality, timeliness
    would_collaborate_again: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContributorHubService:
    """Service for managing contributors and collaborations"""
    
    def __init__(self):
        self.profiles_cache = {}
        self.requests_cache = {}
        self.collaborations_cache = {}
        self.payments_cache = {}
        self.reviews_cache = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample contributor data"""
        sample_profiles = [
            ContributorProfile(
                id="contrib_001",
                user_id="user_001",
                stage_name="BeatMaster Pro",
                real_name="Marcus Johnson",
                bio="Professional music producer with 10+ years experience in hip-hop and R&B",
                roles=[ContributorRole.PRODUCER, ContributorRole.MIXER],
                skills=["Logic Pro", "Pro Tools", "Ableton Live", "Beat Making", "Mixing"],
                genres=["Hip-Hop", "R&B", "Trap", "Pop"],
                location="Atlanta, GA",
                contact_info={"email": "beatmaster@example.com", "phone": "+1-555-0123"},
                social_links={"instagram": "@beatmasterpro", "twitter": "@beatmasterpro"},
                hourly_rate=150.0,
                rating=4.8,
                total_collaborations=45,
                successful_projects=42,
                verification_level="verified"
            ),
            ContributorProfile(
                id="contrib_002",
                user_id="user_002",
                stage_name="VocalQueen",
                real_name="Sarah Williams",
                bio="Versatile vocalist specializing in pop, soul, and contemporary R&B",
                roles=[ContributorRole.VOCALIST, ContributorRole.SONGWRITER],
                skills=["Lead Vocals", "Harmony", "Songwriting", "Studio Recording"],
                genres=["Pop", "R&B", "Soul", "Contemporary"],
                location="Los Angeles, CA",
                contact_info={"email": "vocalqueen@example.com"},
                social_links={"instagram": "@vocalqueen", "tiktok": "@vocalqueen"},
                hourly_rate=200.0,
                rating=4.9,
                total_collaborations=38,
                successful_projects=37,
                verification_level="premium"
            ),
            ContributorProfile(
                id="contrib_003",
                user_id="user_003",
                stage_name="GuitarGuru",
                real_name="Alex Thompson",
                bio="Session guitarist and composer for film, TV, and music production",
                roles=[ContributorRole.INSTRUMENTALIST, ContributorRole.COMPOSER],
                skills=["Electric Guitar", "Acoustic Guitar", "Composition", "Recording"],
                genres=["Rock", "Pop", "Country", "Blues", "Jazz"],
                location="Nashville, TN",
                contact_info={"email": "guitarguru@example.com", "phone": "+1-555-0456"},
                hourly_rate=120.0,
                rating=4.7,
                total_collaborations=52,
                successful_projects=48,
                verification_level="verified"
            )
        ]
        
        for profile in sample_profiles:
            self.profiles_cache[profile.id] = profile
    
    async def create_contributor_profile(self, profile_data: ContributorProfile, user_id: str) -> Dict[str, Any]:
        """Create a new contributor profile"""
        try:
            profile = ContributorProfile(**profile_data.dict())
            profile.user_id = user_id
            
            self.profiles_cache[profile.id] = profile
            
            logger.info(f"Created contributor profile: {profile.id}")
            return {
                "success": True,
                "profile_id": profile.id,
                "message": "Contributor profile created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating contributor profile: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_contributors(self, user_id: str,
                                roles: List[ContributorRole] = None,
                                skills: List[str] = None,
                                genres: List[str] = None,
                                location: str = None,
                                budget_max: float = None,
                                rating_min: float = None,
                                limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search for contributors based on criteria"""
        try:
            contributors = list(self.profiles_cache.values())
            
            # Apply filters
            if roles:
                contributors = [c for c in contributors if any(role in c.roles for role in roles)]
            if skills:
                contributors = [c for c in contributors if any(skill in c.skills for skill in skills)]
            if genres:
                contributors = [c for c in contributors if any(genre in c.genres for genre in genres)]
            if location:
                contributors = [c for c in contributors if location.lower() in c.location.lower() if c.location]
            if budget_max:
                contributors = [c for c in contributors if hasattr(c, 'hourly_rate') and c.hourly_rate and c.hourly_rate <= budget_max]
            if rating_min:
                contributors = [c for c in contributors if c.rating >= rating_min]
            
            # Apply pagination
            total = len(contributors)
            results = contributors[offset:offset + limit]
            
            return {
                "success": True,
                "contributors": [contrib.dict() for contrib in results],
                "total": total,
                "limit": limit,
                "offset": offset,
                "filters_applied": {
                    "roles": roles,
                    "skills": skills,
                    "genres": genres,
                    "location": location,
                    "budget_max": budget_max,
                    "rating_min": rating_min
                }
            }
        except Exception as e:
            logger.error(f"Error searching contributors: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contributors": []
            }
    
    async def send_collaboration_request(self, request_data: CollaborationRequest, user_id: str) -> Dict[str, Any]:
        """Send a collaboration request"""
        try:
            request = CollaborationRequest(**request_data.dict())
            request.from_user_id = user_id
            
            self.requests_cache[request.id] = request
            
            logger.info(f"Sent collaboration request: {request.id}")
            return {
                "success": True,
                "request_id": request.id,
                "message": "Collaboration request sent successfully"
            }
        except Exception as e:
            logger.error(f"Error sending collaboration request: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_collaboration_requests(self, user_id: str, 
                                       request_type: str = "all",  # all, sent, received
                                       status: CollaborationStatus = None) -> Dict[str, Any]:
        """Get collaboration requests for a user"""
        try:
            # Sample requests for demo
            sample_requests = [
                CollaborationRequest(
                    id="req_001",
                    from_user_id="user_001",
                    to_user_id=user_id,
                    project_title="Hip-Hop Album Production",
                    project_description="Looking for a skilled producer to work on my upcoming hip-hop album",
                    required_roles=[ContributorRole.PRODUCER, ContributorRole.MIXER],
                    budget_range={"min": 2000, "max": 5000},
                    timeline="4-6 weeks",
                    deliverables=["Beat production", "Mixing", "Mastering"],
                    status=CollaborationStatus.PENDING,
                    message="Hi! Love your work. Would like to collaborate on my new project."
                ),
                CollaborationRequest(
                    id="req_002",
                    from_user_id=user_id,
                    to_user_id="user_002",
                    project_title="Pop Single Vocals",
                    project_description="Need a female vocalist for an upcoming pop single",
                    required_roles=[ContributorRole.VOCALIST],
                    budget_range={"min": 800, "max": 1500},
                    timeline="2 weeks",
                    deliverables=["Lead vocals", "Harmony vocals"],
                    status=CollaborationStatus.ACCEPTED,
                    message="Hi Sarah! Would love to work with you on this track.",
                    responded_at=datetime.now(timezone.utc) - timedelta(days=2),
                    response_message="Sounds great! Let's do it."
                ),
                CollaborationRequest(
                    id="req_003",
                    from_user_id="user_003",
                    to_user_id=user_id,
                    project_title="Acoustic Guitar Session",
                    project_description="Need acoustic guitar for a country-pop crossover track",
                    required_roles=[ContributorRole.INSTRUMENTALIST],
                    budget_range={"min": 300, "max": 600},
                    timeline="1 week",
                    deliverables=["Acoustic guitar recording"],
                    status=CollaborationStatus.COMPLETED,
                    message="Quick session needed for this track."
                )
            ]
            
            # Filter by request type
            if request_type == "sent":
                sample_requests = [r for r in sample_requests if r.from_user_id == user_id]
            elif request_type == "received":
                sample_requests = [r for r in sample_requests if r.to_user_id == user_id]
            
            # Filter by status
            if status:
                sample_requests = [r for r in sample_requests if r.status == status]
            
            return {
                "success": True,
                "requests": [req.dict() for req in sample_requests],
                "total": len(sample_requests),
                "summary": {
                    "pending": len([r for r in sample_requests if r.status == CollaborationStatus.PENDING]),
                    "accepted": len([r for r in sample_requests if r.status == CollaborationStatus.ACCEPTED]),
                    "in_progress": len([r for r in sample_requests if r.status == CollaborationStatus.IN_PROGRESS]),
                    "completed": len([r for r in sample_requests if r.status == CollaborationStatus.COMPLETED])
                }
            }
        except Exception as e:
            logger.error(f"Error fetching collaboration requests: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "requests": []
            }
    
    async def respond_to_collaboration_request(self, request_id: str, response: str, 
                                             message: str, user_id: str) -> Dict[str, Any]:
        """Respond to a collaboration request"""
        try:
            if response not in ["accept", "decline"]:
                return {
                    "success": False,
                    "error": "Invalid response. Must be 'accept' or 'decline'"
                }
            
            # In production, this would update the database
            logger.info(f"User {user_id} {response}ed collaboration request {request_id}")
            
            # If accepted, create a collaboration
            collaboration_id = None
            if response == "accept":
                collaboration_id = str(uuid.uuid4())
                logger.info(f"Created collaboration: {collaboration_id}")
            
            return {
                "success": True,
                "message": f"Collaboration request {response}ed successfully",
                "collaboration_id": collaboration_id,
                "responded_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error responding to collaboration request: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_active_collaborations(self, user_id: str) -> Dict[str, Any]:
        """Get active collaborations for a user"""
        try:
            # Sample active collaborations
            collaborations = [
                Collaboration(
                    id="collab_001",
                    request_id="req_002",
                    project_title="Pop Single Vocals",
                    participants=["user_001", "user_002"],
                    roles_assignment={"user_001": ContributorRole.PRODUCER, "user_002": ContributorRole.VOCALIST},
                    status=CollaborationStatus.IN_PROGRESS,
                    start_date=datetime.now(timezone.utc) - timedelta(days=5),
                    budget_total=1200.0,
                    payment_splits={"user_001": 60.0, "user_002": 40.0},
                    milestones=[
                        {"title": "Instrumental complete", "status": "completed", "date": "2024-01-15"},
                        {"title": "Vocals recorded", "status": "in_progress", "due_date": "2024-01-22"},
                        {"title": "Final mix", "status": "pending", "due_date": "2024-01-25"}
                    ]
                ),
                Collaboration(
                    id="collab_002",
                    request_id="req_003",
                    project_title="Acoustic Guitar Session",
                    participants=["user_001", "user_003"],
                    roles_assignment={"user_001": ContributorRole.PRODUCER, "user_003": ContributorRole.INSTRUMENTALIST},
                    status=CollaborationStatus.COMPLETED,
                    start_date=datetime.now(timezone.utc) - timedelta(days=20),
                    end_date=datetime.now(timezone.utc) - timedelta(days=10),
                    budget_total=500.0,
                    payment_splits={"user_001": 70.0, "user_003": 30.0}
                )
            ]
            
            return {
                "success": True,
                "collaborations": [collab.dict() for collab in collaborations],
                "total": len(collaborations),
                "by_status": {
                    "in_progress": len([c for c in collaborations if c.status == CollaborationStatus.IN_PROGRESS]),
                    "completed": len([c for c in collaborations if c.status == CollaborationStatus.COMPLETED]),
                    "pending": len([c for c in collaborations if c.status == CollaborationStatus.PENDING])
                }
            }
        except Exception as e:
            logger.error(f"Error fetching active collaborations: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "collaborations": []
            }
    
    async def get_contributor_payments(self, user_id: str, status: PaymentStatus = None) -> Dict[str, Any]:
        """Get payment information for a contributor"""
        try:
            # Sample payments
            payments = [
                ContributorPayment(
                    id="pay_001",
                    contributor_id=user_id,
                    collaboration_id="collab_002",
                    amount=150.0,
                    payment_type="collaboration",
                    status=PaymentStatus.PAID,
                    description="Payment for Acoustic Guitar Session",
                    payment_date=datetime.now(timezone.utc) - timedelta(days=5),
                    payment_method="PayPal",
                    transaction_id="TXN123456789"
                ),
                ContributorPayment(
                    id="pay_002",
                    contributor_id=user_id,
                    amount=480.0,
                    payment_type="collaboration",
                    status=PaymentStatus.PROCESSING,
                    description="Payment for Pop Single Vocals project",
                    payment_method="Bank Transfer"
                ),
                ContributorPayment(
                    id="pay_003",
                    contributor_id=user_id,
                    amount=75.50,
                    payment_type="royalty",
                    status=PaymentStatus.PAID,
                    description="Royalty payment for Q4 2023",
                    payment_date=datetime.now(timezone.utc) - timedelta(days=30),
                    payment_method="Stripe"
                )
            ]
            
            if status:
                payments = [p for p in payments if p.status == status]
            
            total_earned = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
            pending_amount = sum(p.amount for p in payments if p.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING])
            
            return {
                "success": True,
                "payments": [payment.dict() for payment in payments],
                "total": len(payments),
                "summary": {
                    "total_earned": total_earned,
                    "pending_amount": pending_amount,
                    "this_month": sum(p.amount for p in payments if p.payment_date and 
                                    p.payment_date >= datetime.now(timezone.utc) - timedelta(days=30) and
                                    p.status == PaymentStatus.PAID),
                    "by_status": {
                        "paid": len([p for p in payments if p.status == PaymentStatus.PAID]),
                        "processing": len([p for p in payments if p.status == PaymentStatus.PROCESSING]),
                        "pending": len([p for p in payments if p.status == PaymentStatus.PENDING])
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error fetching contributor payments: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "payments": []
            }
    
    async def submit_review(self, review_data: ContributorReview, user_id: str) -> Dict[str, Any]:
        """Submit a review for a collaboration"""
        try:
            review = ContributorReview(**review_data.dict())
            review.reviewer_id = user_id
            
            self.reviews_cache[review.id] = review
            
            logger.info(f"Submitted review: {review.id}")
            return {
                "success": True,
                "review_id": review.id,
                "message": "Review submitted successfully"
            }
        except Exception as e:
            logger.error(f"Error submitting review: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_contributor_stats(self, user_id: str) -> Dict[str, Any]:
        """Get contributor statistics and performance metrics"""
        try:
            stats = {
                "profile": {
                    "total_collaborations": 15,
                    "successful_projects": 14,
                    "success_rate": 93.3,
                    "average_rating": 4.7,
                    "total_reviews": 12,
                    "response_rate": 98.5,
                    "average_response_time": "2.3 hours"
                },
                "earnings": {
                    "total_earned": 12450.75,
                    "this_month": 1850.00,
                    "pending": 650.00,
                    "average_project_value": 830.05
                },
                "activity": {
                    "active_collaborations": 2,
                    "pending_requests": 3,
                    "completed_this_month": 2,
                    "projects_in_queue": 1
                },
                "skills_performance": {
                    "most_requested_skill": "Music Production",
                    "highest_rated_skill": "Mixing",
                    "skill_ratings": {
                        "Production": 4.8,
                        "Mixing": 4.9,
                        "Songwriting": 4.6,
                        "Vocals": 4.7
                    }
                },
                "monthly_trends": [
                    {"month": "Jan", "projects": 2, "earnings": 1200, "rating": 4.8},
                    {"month": "Feb", "projects": 3, "earnings": 1850, "rating": 4.7},
                    {"month": "Mar", "projects": 1, "earnings": 800, "rating": 4.9},
                    {"month": "Apr", "projects": 4, "earnings": 2400, "rating": 4.6},
                    {"month": "May", "projects": 2, "earnings": 1650, "rating": 4.8},
                    {"month": "Jun", "projects": 3, "earnings": 1950, "rating": 4.7}
                ]
            }
            
            return {
                "success": True,
                "stats": stats,
                "insights": [
                    "Your success rate is excellent at 93.3%",
                    "Mixing is your highest-rated skill at 4.9 stars",
                    "You're earning 15% more than last month",
                    "Fast response time gives you a competitive advantage"
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching contributor stats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
contributor_hub_service = ContributorHubService()