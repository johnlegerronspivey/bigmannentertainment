"""
Ticketing Integration API Endpoints — Jira & ServiceNow
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from ticketing_service import get_ticketing_service

router = APIRouter(prefix="/cve/ticketing", tags=["Ticketing Integration"])


class TicketingConfig(BaseModel):
    provider: str = ""
    settings: Dict[str, Any] = {}


class BulkTicketRequest(BaseModel):
    severity: str = "critical"
    limit: int = 10


# ── Configuration ──────────────────────────────────────────

@router.get("/config")
async def get_config():
    svc = get_ticketing_service()
    return await svc.get_config()


@router.put("/config")
async def save_config(body: TicketingConfig):
    svc = get_ticketing_service()
    return await svc.save_config(body.dict())


@router.post("/test-connection")
async def test_connection():
    svc = get_ticketing_service()
    return await svc.test_connection()


# ── Tickets ────────────────────────────────────────────────

@router.get("/tickets")
async def list_tickets(limit: int = Query(50, ge=1, le=200), skip: int = Query(0, ge=0)):
    svc = get_ticketing_service()
    return await svc.list_tickets(limit=limit, skip=skip)


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    svc = get_ticketing_service()
    result = await svc.get_ticket(ticket_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result


@router.post("/tickets/create/{cve_id}")
async def create_ticket(cve_id: str):
    svc = get_ticketing_service()
    result = await svc.create_ticket(cve_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/tickets/bulk")
async def bulk_create_tickets(body: BulkTicketRequest):
    svc = get_ticketing_service()
    return await svc.bulk_create_tickets(severity=body.severity, limit=body.limit)


@router.post("/tickets/{ticket_id}/sync")
async def sync_ticket(ticket_id: str):
    svc = get_ticketing_service()
    result = await svc.sync_ticket(ticket_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result


@router.post("/sync-all")
async def sync_all_tickets():
    svc = get_ticketing_service()
    return await svc.sync_all_tickets()


@router.get("/stats")
async def get_stats():
    svc = get_ticketing_service()
    return await svc.get_stats()
