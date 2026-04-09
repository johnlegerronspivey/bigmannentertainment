"""
Revenue Tracking API Endpoints — Real data CRUD backed by MongoDB.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import csv
import io

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


@router.get("/export")
async def export_transactions(
    platform_id: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="ISO date string, e.g. 2025-01-01"),
    date_to: Optional[str] = Query(None, description="ISO date string, e.g. 2025-12-31"),
    current_user: User = Depends(get_current_user),
):
    """Export revenue transactions as a CSV file."""
    query = {"user_id": current_user.id}
    if platform_id:
        query["platform_id"] = platform_id
    if source:
        query["source"] = source
    if date_from or date_to:
        date_filter = {}
        if date_from:
            date_filter["$gte"] = date_from
        if date_to:
            date_filter["$lte"] = date_to + "T23:59:59"
        query["date"] = date_filter

    records = []
    async for doc in db[REVENUE_COLLECTION].find(query, {"_id": 0}).sort("date", -1):
        records.append(doc)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Platform", "Content Title", "Source", "Amount (USD)", "Currency", "Description"])

    for r in records:
        writer.writerow([
            r.get("date", "")[:10],
            r.get("platform_name", r.get("platform_id", "")),
            r.get("content_title", ""),
            r.get("source", ""),
            r.get("amount", 0),
            r.get("currency", "USD"),
            r.get("description", ""),
        ])

    output.seek(0)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"revenue_report_{now_str}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
