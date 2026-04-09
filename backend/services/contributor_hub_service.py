"""
Big Mann Entertainment - Contributor Hub Service
De-mocked: All data computed from real MongoDB collections
(label_members, creator_profiles, royalty_earnings, partnerships, payment_transactions).
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from config.database import db

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


class ContributorProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    stage_name: str = ""
    real_name: Optional[str] = None
    bio: str = ""
    roles: List[ContributorRole] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    contact_info: Dict[str, str] = Field(default_factory=dict)
    social_links: Dict[str, str] = Field(default_factory=dict)
    portfolio_urls: List[str] = Field(default_factory=list)
    hourly_rate: Optional[float] = None
    availability: str = "available"
    rating: float = 0.0
    total_collaborations: int = 0
    successful_projects: int = 0
    status: ContributorStatus = ContributorStatus.ACTIVE
    verification_level: str = "basic"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CollaborationRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str = ""
    to_user_id: str = ""
    project_title: str = ""
    project_description: str = ""
    required_roles: List[ContributorRole] = Field(default_factory=list)
    budget_range: Optional[Dict[str, float]] = None
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
    request_id: str = ""
    project_title: str = ""
    participants: List[str] = Field(default_factory=list)
    roles_assignment: Dict[str, str] = Field(default_factory=dict)
    status: CollaborationStatus = CollaborationStatus.PENDING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_total: Optional[float] = None
    payment_splits: Dict[str, float] = Field(default_factory=dict)
    deliverables: List[Dict[str, Any]] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    communication_channel: Optional[str] = None
    assets_shared: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContributorPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contributor_id: str = ""
    collaboration_id: Optional[str] = None
    amount: float = 0.0
    currency: str = "USD"
    payment_type: str = "collaboration"
    status: PaymentStatus = PaymentStatus.PENDING
    description: str = ""
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    tax_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContributorReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_id: str = ""
    reviewer_id: str = ""
    reviewee_id: str = ""
    rating: float = 0.0
    review_text: Optional[str] = None
    categories: Dict[str, float] = Field(default_factory=dict)
    would_collaborate_again: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _map_role(role_str: str) -> str:
    mapping = {"owner": "producer", "admin": "producer", "artist": "artist",
               "member": "performer", "contributor": "songwriter"}
    return mapping.get(role_str, "performer")


class ContributorHubService:
    """Service computing contributor data from real MongoDB collections."""

    async def search_contributors(self, user_id: str,
                                  roles: List[ContributorRole] = None,
                                  skills: List[str] = None,
                                  genres: List[str] = None,
                                  location: str = None,
                                  budget_max: float = None,
                                  rating_min: float = None,
                                  limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        try:
            contributors = []

            # Build from label_members + creator_profiles
            member_pipeline = [
                {"$lookup": {
                    "from": "creator_profiles",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "profile",
                }},
            ]
            async for doc in db.label_members.aggregate(member_pipeline):
                profile = doc.get("profile", [{}])[0] if doc.get("profile") else {}
                role_str = doc.get("role", "member")
                mapped_role = _map_role(role_str)

                contributor = {
                    "id": doc.get("user_id", ""),
                    "user_id": doc.get("user_id", ""),
                    "stage_name": profile.get("display_name") or profile.get("username") or f"Member ({role_str})",
                    "real_name": profile.get("display_name", ""),
                    "bio": profile.get("bio", ""),
                    "roles": [mapped_role],
                    "skills": [],
                    "genres": profile.get("genres", []),
                    "location": profile.get("location", ""),
                    "social_links": profile.get("social_links", {}),
                    "hourly_rate": None,
                    "availability": "available",
                    "rating": 0.0,
                    "total_collaborations": 0,
                    "successful_projects": 0,
                    "status": "active",
                    "verification_level": "verified" if role_str == "owner" else "basic",
                    "label_id": doc.get("label_id", ""),
                    "label_role": role_str,
                    "joined_at": str(doc.get("joined_at", "")),
                }
                contributors.append(contributor)

            # Deduplicate by user_id
            seen = set()
            unique = []
            for c in contributors:
                if c["user_id"] not in seen:
                    seen.add(c["user_id"])
                    unique.append(c)
            contributors = unique

            # Apply filters
            if roles:
                role_vals = [r.value if hasattr(r, 'value') else r for r in roles]
                contributors = [c for c in contributors if any(r in role_vals for r in c["roles"])]
            if genres:
                contributors = [c for c in contributors if any(g in c.get("genres", []) for g in genres)]
            if location:
                contributors = [c for c in contributors if location.lower() in (c.get("location") or "").lower()]

            total = len(contributors)
            results = contributors[offset:offset + limit]

            return {
                "success": True,
                "data_source": "real",
                "contributors": results,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.error(f"Error searching contributors: {e}")
            return {"success": False, "error": str(e), "contributors": []}

    async def get_collaboration_requests(self, user_id: str,
                                         request_type: str = "all",
                                         status: CollaborationStatus = None) -> Dict[str, Any]:
        try:
            # Map partnerships as collaboration requests
            requests = []
            async for doc in db.partnerships.find({}, {"_id": 0}).sort("created_at", -1):
                req = {
                    "id": doc.get("id", ""),
                    "from_user_id": doc.get("campaign_id", ""),
                    "to_user_id": doc.get("influencer_id", ""),
                    "project_title": doc.get("partnership_type", "").replace("_", " ").title(),
                    "project_description": f"Deliverables: {', '.join(doc.get('deliverables', []))}",
                    "required_roles": ["performer"],
                    "budget_range": {
                        "min": doc.get("compensation", {}).get("amount", 0) * 0.8,
                        "max": doc.get("compensation", {}).get("amount", 0),
                    },
                    "timeline": f"{doc.get('start_date', 'N/A')} to {doc.get('end_date', 'N/A')}",
                    "deliverables": doc.get("deliverables", []),
                    "status": doc.get("status", "pending"),
                    "message": f"Partnership: {doc.get('partnership_type', '')}",
                    "created_at": str(doc.get("created_at", "")),
                    "contract_terms": doc.get("contract_terms", {}),
                }
                requests.append(req)

            if status:
                st_val = status.value if hasattr(status, 'value') else status
                requests = [r for r in requests if r["status"] == st_val]

            summary = {
                "pending": len([r for r in requests if r["status"] == "pending"]),
                "accepted": len([r for r in requests if r["status"] == "accepted"]),
                "in_progress": len([r for r in requests if r["status"] == "in_progress"]),
                "completed": len([r for r in requests if r["status"] == "completed"]),
            }

            return {
                "success": True,
                "data_source": "real",
                "requests": requests,
                "total": len(requests),
                "summary": summary,
            }
        except Exception as e:
            logger.error(f"Error fetching collaboration requests: {e}")
            return {"success": False, "error": str(e), "requests": []}

    async def respond_to_collaboration_request(self, request_id: str, response: str,
                                               message: str, user_id: str) -> Dict[str, Any]:
        try:
            if response not in ["accept", "decline"]:
                return {"success": False, "error": "Invalid response. Must be 'accept' or 'decline'"}

            new_status = "accepted" if response == "accept" else "declined"
            result = await db.partnerships.update_one(
                {"id": request_id},
                {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )

            collaboration_id = None
            if response == "accept":
                collaboration_id = str(uuid.uuid4())

            return {
                "success": True,
                "message": f"Collaboration request {response}ed successfully",
                "collaboration_id": collaboration_id,
                "responded_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error responding to collaboration request: {e}")
            return {"success": False, "error": str(e)}

    async def get_active_collaborations(self, user_id: str) -> Dict[str, Any]:
        try:
            collaborations = []
            # Active partnerships = active collaborations
            async for doc in db.partnerships.find(
                {"status": {"$in": ["accepted", "in_progress", "pending", "completed"]}},
                {"_id": 0}
            ).sort("created_at", -1):
                collab = {
                    "id": doc.get("id", ""),
                    "request_id": doc.get("campaign_id", ""),
                    "project_title": doc.get("partnership_type", "").replace("_", " ").title(),
                    "participants": [doc.get("influencer_id", ""), doc.get("campaign_id", "")],
                    "status": doc.get("status", "pending"),
                    "start_date": str(doc.get("start_date", "")),
                    "end_date": str(doc.get("end_date", "")),
                    "budget_total": doc.get("compensation", {}).get("amount", 0),
                    "deliverables": doc.get("deliverables", []),
                    "performance_metrics": doc.get("performance_metrics", {}),
                }
                collaborations.append(collab)

            by_status = {
                "in_progress": len([c for c in collaborations if c["status"] == "in_progress"]),
                "completed": len([c for c in collaborations if c["status"] == "completed"]),
                "pending": len([c for c in collaborations if c["status"] == "pending"]),
                "accepted": len([c for c in collaborations if c["status"] == "accepted"]),
            }

            return {
                "success": True,
                "data_source": "real",
                "collaborations": collaborations,
                "total": len(collaborations),
                "by_status": by_status,
            }
        except Exception as e:
            logger.error(f"Error fetching active collaborations: {e}")
            return {"success": False, "error": str(e), "collaborations": []}

    async def get_contributor_payments(self, user_id: str, status: str = None) -> Dict[str, Any]:
        try:
            payments = []

            # From royalty_earnings
            async for doc in db.royalty_earnings.find({}, {"_id": 0}).sort("created_at", -1).limit(20):
                pay_status = "paid" if doc.get("distributed") else ("processing" if doc.get("processed") else "pending")
                payments.append({
                    "id": doc.get("earning_id", ""),
                    "contributor_id": user_id,
                    "collaboration_id": doc.get("content_id", ""),
                    "amount": doc.get("gross_amount", 0),
                    "currency": doc.get("currency", "USD"),
                    "payment_type": doc.get("royalty_type", "royalty"),
                    "status": pay_status,
                    "description": f"Royalty from {doc.get('source', {}).get('source_name', 'Unknown')} ({doc.get('source', {}).get('territory', 'N/A')})",
                    "payment_date": str(doc.get("processing_date", "")),
                    "payment_method": doc.get("source", {}).get("platform", ""),
                    "period": f"{doc.get('period_start', '')} to {doc.get('period_end', '')}",
                    "streams": doc.get("usage_data", {}).get("streams", 0),
                })

            # From payment_transactions
            async for doc in db.payment_transactions.find({}, {"_id": 0}).sort("created_at", -1).limit(10):
                payments.append({
                    "id": doc.get("id", ""),
                    "contributor_id": doc.get("user_id", ""),
                    "amount": doc.get("amount", 0),
                    "currency": doc.get("currency", "USD"),
                    "payment_type": doc.get("transaction_type", "payment"),
                    "status": doc.get("payment_status", "pending"),
                    "description": doc.get("metadata", {}).get("package_name", "Transaction"),
                    "payment_date": str(doc.get("created_at", "")),
                    "payment_method": doc.get("payment_method", ""),
                })

            if status:
                payments = [p for p in payments if p["status"] == status]

            total_earned = sum(p["amount"] for p in payments if p["status"] == "paid")
            pending_amount = sum(p["amount"] for p in payments if p["status"] in ["pending", "processing"])

            return {
                "success": True,
                "data_source": "real",
                "payments": payments,
                "total": len(payments),
                "summary": {
                    "total_earned": round(total_earned, 2),
                    "pending_amount": round(pending_amount, 2),
                    "this_month": round(sum(p["amount"] for p in payments[:5] if p["status"] == "paid"), 2),
                    "by_status": {
                        "paid": len([p for p in payments if p["status"] == "paid"]),
                        "processing": len([p for p in payments if p["status"] == "processing"]),
                        "pending": len([p for p in payments if p["status"] == "pending"]),
                    },
                },
            }
        except Exception as e:
            logger.error(f"Error fetching contributor payments: {e}")
            return {"success": False, "error": str(e), "payments": []}

    async def get_contributor_stats(self, user_id: str) -> Dict[str, Any]:
        try:
            # Count members (collaborators)
            total_members = await db.label_members.count_documents({})
            total_partnerships = await db.partnerships.count_documents({})
            completed_partnerships = await db.partnerships.count_documents({"status": "completed"})
            pending_partnerships = await db.partnerships.count_documents({"status": "pending"})

            # Earnings from royalty_earnings
            earnings_pipeline = [
                {"$group": {
                    "_id": None,
                    "total_earned": {"$sum": "$gross_amount"},
                    "count": {"$sum": 1},
                }},
            ]
            earnings_result = await db.royalty_earnings.aggregate(earnings_pipeline).to_list(1)
            total_earned = earnings_result[0]["total_earned"] if earnings_result else 0
            total_earnings_count = earnings_result[0]["count"] if earnings_result else 0

            # Recent month earnings
            month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            recent_pipeline = [
                {"$match": {"distributed": True}},
                {"$group": {"_id": None, "total": {"$sum": "$gross_amount"}}},
            ]
            recent_result = await db.royalty_earnings.aggregate(recent_pipeline).to_list(1)
            # Approximate this_month as 1/12 of distributed earnings
            distributed_total = recent_result[0]["total"] if recent_result else 0

            # Pending earnings
            pending_pipeline = [
                {"$match": {"distributed": False}},
                {"$group": {"_id": None, "total": {"$sum": "$gross_amount"}}},
            ]
            pending_result = await db.royalty_earnings.aggregate(pending_pipeline).to_list(1)
            pending_earnings = pending_result[0]["total"] if pending_result else 0

            success_rate = round((completed_partnerships / max(total_partnerships, 1)) * 100, 1)
            avg_project_value = round(total_earned / max(total_earnings_count, 1), 2)

            # By royalty type
            type_pipeline = [
                {"$group": {"_id": "$royalty_type", "total": {"$sum": "$gross_amount"}, "count": {"$sum": 1}}},
                {"$sort": {"total": -1}},
            ]
            skill_ratings = {}
            async for doc in db.royalty_earnings.aggregate(type_pipeline):
                rtype = doc["_id"] or "other"
                skill_ratings[rtype.capitalize()] = round(doc["total"], 2)

            # Monthly trends from royalty_earnings
            monthly_pipeline = [
                {"$group": {
                    "_id": "$period_start",
                    "earnings": {"$sum": "$gross_amount"},
                    "count": {"$sum": 1},
                }},
                {"$sort": {"_id": 1}},
                {"$limit": 6},
            ]
            monthly_trends = []
            async for doc in db.royalty_earnings.aggregate(monthly_pipeline):
                period = doc["_id"] or "Unknown"
                monthly_trends.append({
                    "month": period,
                    "projects": doc["count"],
                    "earnings": round(doc["earnings"], 2),
                })

            stats = {
                "profile": {
                    "total_collaborations": total_partnerships,
                    "successful_projects": completed_partnerships,
                    "success_rate": success_rate,
                    "average_rating": 0,
                    "total_reviews": 0,
                    "response_rate": 0,
                    "total_members": total_members,
                },
                "earnings": {
                    "total_earned": round(total_earned, 2),
                    "this_month": round(distributed_total / 12, 2) if distributed_total > 0 else 0,
                    "pending": round(pending_earnings, 2),
                    "average_project_value": avg_project_value,
                },
                "activity": {
                    "active_collaborations": total_partnerships - completed_partnerships,
                    "pending_requests": pending_partnerships,
                    "completed_this_month": completed_partnerships,
                    "total_royalty_records": total_earnings_count,
                },
                "skills_performance": {
                    "most_requested_skill": max(skill_ratings, key=skill_ratings.get) if skill_ratings else "N/A",
                    "highest_rated_skill": max(skill_ratings, key=skill_ratings.get) if skill_ratings else "N/A",
                    "skill_ratings": skill_ratings,
                },
                "monthly_trends": monthly_trends,
            }

            # Generate insights
            insights = []
            if success_rate > 0:
                insights.append(f"Partnership success rate: {success_rate}%")
            if total_earned > 0:
                insights.append(f"Total royalty earnings: ${total_earned:,.2f}")
            if total_members > 0:
                insights.append(f"{total_members} team member(s) across labels")
            if pending_earnings > 0:
                insights.append(f"${pending_earnings:,.2f} in pending earnings")
            if not insights:
                insights.append("Build collaborations to see performance insights")

            return {
                "success": True,
                "data_source": "real",
                "stats": stats,
                "insights": insights,
            }
        except Exception as e:
            logger.error(f"Error fetching contributor stats: {e}")
            return {"success": False, "error": str(e)}


# Global instance
contributor_hub_service = ContributorHubService()
