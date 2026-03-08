"""
Creator Profiles - MongoDB-based profile system for content creators
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db
from auth.service import get_current_user

router = APIRouter(prefix="/creator-profiles", tags=["Creator Profiles"])


class ProfileCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=30)
    bio: Optional[str] = None
    tagline: Optional[str] = None
    location: Optional[str] = None
    genres: List[str] = []
    social_links: dict = {}
    profile_public: bool = True
    show_earnings: bool = False


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    tagline: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    genres: Optional[List[str]] = None
    social_links: Optional[dict] = None
    profile_public: Optional[bool] = None
    show_earnings: Optional[bool] = None
    website: Optional[str] = None


def serialize_profile(doc):
    """Convert MongoDB document to JSON-safe dict"""
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    if "user_id" in doc and isinstance(doc["user_id"], ObjectId):
        doc["user_id"] = str(doc["user_id"])
    for key in ["created_at", "updated_at"]:
        if key in doc and isinstance(doc[key], datetime):
            doc[key] = doc[key].isoformat()
    return doc


@router.post("")
async def create_profile(data: ProfileCreate, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    existing = await db.creator_profiles.find_one({"user_id": user_id})
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    username_taken = await db.creator_profiles.find_one({"username": data.username.lower()})
    if username_taken:
        raise HTTPException(status_code=400, detail="Username already taken")

    profile = {
        "user_id": user_id,
        "username": data.username.lower(),
        "display_name": data.display_name,
        "bio": data.bio or "",
        "tagline": data.tagline or "",
        "location": data.location or "",
        "avatar_url": "",
        "cover_image_url": "",
        "genres": data.genres,
        "social_links": data.social_links,
        "website": "",
        "profile_public": data.profile_public,
        "show_earnings": data.show_earnings,
        "stats": {"total_assets": 0, "total_streams": 0, "total_followers": 0, "total_earnings": 0.0},
        "subscription_tier": "free",
        "verified": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = await db.creator_profiles.insert_one(profile)
    profile["_id"] = result.inserted_id
    return serialize_profile(profile)


@router.get("/me")
async def get_my_profile(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    profile = await db.creator_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please create one first.")
    return serialize_profile(profile)


@router.put("/me")
async def update_my_profile(data: ProfileUpdate, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    profile = await db.creator_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    updates = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    updates["updated_at"] = datetime.now(timezone.utc)

    await db.creator_profiles.update_one({"user_id": user_id}, {"$set": updates})
    updated = await db.creator_profiles.find_one({"user_id": user_id})
    return serialize_profile(updated)


@router.get("/browse")
async def browse_profiles(search: Optional[str] = None, genre: Optional[str] = None, limit: int = 20, skip: int = 0):
    query = {"profile_public": True}
    if search:
        query["$or"] = [
            {"display_name": {"$regex": search, "$options": "i"}},
            {"username": {"$regex": search, "$options": "i"}},
            {"tagline": {"$regex": search, "$options": "i"}},
        ]
    if genre:
        query["genres"] = {"$in": [genre]}

    cursor = db.creator_profiles.find(query).sort("created_at", -1).skip(skip).limit(limit)
    profiles = []
    async for doc in cursor:
        profiles.append(serialize_profile(doc))
    total = await db.creator_profiles.count_documents(query)
    return {"profiles": profiles, "total": total}


@router.get("/u/{username}")
async def get_public_profile(username: str):
    profile = await db.creator_profiles.find_one({"username": username.lower()})
    if not profile:
        raise HTTPException(status_code=404, detail="Creator not found")
    if not profile.get("profile_public", True):
        raise HTTPException(status_code=403, detail="This profile is private")

    # Don't expose earnings if hidden
    if not profile.get("show_earnings", False):
        if "stats" in profile:
            profile["stats"].pop("total_earnings", None)

    return serialize_profile(profile)
