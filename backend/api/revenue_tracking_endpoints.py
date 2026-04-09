"""
Revenue Tracking API Endpoints — Real data CRUD backed by MongoDB.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from auth.service import get_current_user
from models.core import User
from services.revenue_tracking_service import (
    get_revenue_overview,
    get_platform_revenue_detail,
    record_revenue,
)
from config.database import db

router = APIRouter(prefix="/revenue", tags=["Revenue Tracking"])

REVENUE_COLLECTION = "revenue_tracking"


class RecordRevenueRequest(BaseModel):
    platform_id: str
    platform_name: str
    content_id: Optional[str] = ""
    content_title: Optional[str] = ""
    source: str = "streaming"
    amount: float
    description: Optional[str] = ""


@router.get("/overview")
async def revenue_overview(current_user: User = Depends(get_current_user)):
    """Get comprehensive revenue overview for the current user."""
    data = await get_revenue_overview(current_user.id)
    return data


@router.get("/platform/{platform_id}")
async def platform_detail(platform_id: str, current_user: User = Depends(get_current_user)):
    """Get detailed revenue for a specific platform."""
    data = await get_platform_revenue_detail(current_user.id, platform_id)
    return data


@router.post("/record")
async def add_revenue(req: RecordRevenueRequest, current_user: User = Depends(get_current_user)):
    """Record a new revenue entry."""
    result = await record_revenue(current_user.id, req.dict())
    return result


@router.get("/transactions")
async def list_transactions(
    platform_id: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """List revenue transactions with optional filters."""
    query = {"user_id": current_user.id}
    if platform_id:
        query["platform_id"] = platform_id
    if source:
        query["source"] = source

    total = await db[REVENUE_COLLECTION].count_documents(query)
    records = []
    async for doc in (
        db[REVENUE_COLLECTION]
        .find(query, {"_id": 0})
        .sort("date", -1)
        .skip(skip)
        .limit(limit)
    ):
        records.append(doc)

    return {"transactions": records, "total": total, "limit": limit, "skip": skip}


@router.delete("/transactions/{date_key}")
async def delete_transaction(date_key: str, current_user: User = Depends(get_current_user)):
    """Delete a revenue transaction by its date key."""
    result = await db[REVENUE_COLLECTION].delete_one(
        {"user_id": current_user.id, "date": date_key}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}
