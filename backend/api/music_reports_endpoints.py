"""
Music Reports API Endpoints
Enhanced endpoints for Music Reports integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth.service import get_current_user
from models.core import User
from config.database import db
from music_reports_service import MusicReportsService

# Create router
music_reports_router = APIRouter(prefix="/music-reports", tags=["Music Reports"])

@music_reports_router.get("/dashboard")
async def get_music_reports_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive Music Reports dashboard data"""
    try:
        service = MusicReportsService(db)
        
        # Get all dashboard data
        integration_status = await service.get_integration_status(current_user.id)
        cwr_works = await service.get_cwr_works_for_music_reports(current_user.id)
        royalty_data = await service.get_royalty_data(current_user.id)
        sync_capabilities = await service.get_sync_capabilities()
        
        dashboard_data = {
            "user_info": {
                "user_id": current_user.id,
                "full_name": current_user.full_name,
                "email": current_user.email
            },
            "integration_status": integration_status,
            "cwr_works": cwr_works,
            "royalty_summary": {
                "total_collected": royalty_data.get("total_collected", 0),
                "pending_payment": royalty_data.get("pending_payment", 0),
                "paid_out": royalty_data.get("paid_out", 0),
                "collections_by_territory": royalty_data.get("collections_by_territory", {}),
                "collections_by_source": royalty_data.get("collections_by_source", {})
            },
            "sync_capabilities": sync_capabilities,
            "quick_stats": {
                "total_works": len(cwr_works),
                "works_synced": len([w for w in cwr_works if w.get("music_reports_status") == "synced"]),
                "pending_sync": len([w for w in cwr_works if w.get("music_reports_status") == "pending_sync"]),
                "sync_errors": integration_status.get("sync_errors", 0)
            },
            "recent_activity": await _get_recent_activity(db, current_user.id)
        }
        
        return {"music_reports_dashboard": dashboard_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load Music Reports dashboard: {str(e)}")

@music_reports_router.get("/integration-status")
async def get_integration_status(
    current_user: User = Depends(get_current_user)
):
    """Get detailed Music Reports integration status"""
    try:
        service = MusicReportsService(db)
        status = await service.get_integration_status(current_user.id)
        
        return {"integration_status": status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

@music_reports_router.get("/cwr-works")
async def get_cwr_works(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, description="Number of works to return"),
    offset: int = Query(0, description="Number of works to skip")
):
    """Get CWR works formatted for Music Reports"""
    try:
        service = MusicReportsService(db)
        works = await service.get_cwr_works_for_music_reports(current_user.id)
        
        # Apply pagination
        total_works = len(works)
        paginated_works = works[offset:offset + limit]
        
        return {
            "cwr_works": paginated_works,
            "pagination": {
                "total": total_works,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_works
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get CWR works: {str(e)}")

@music_reports_router.post("/sync")
async def initiate_sync(
    current_user: User = Depends(get_current_user)
):
    """Initiate synchronization with Music Reports"""
    try:
        service = MusicReportsService(db)
        sync_result = await service.sync_with_music_reports(current_user.id)
        
        return {"sync_result": sync_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate sync: {str(e)}")

@music_reports_router.get("/royalties")
async def get_royalty_data(
    current_user: User = Depends(get_current_user),
    period: Optional[str] = Query(None, description="Period to get royalties for (e.g., '2024-Q4')")
):
    """Get royalty collection data from Music Reports"""
    try:
        service = MusicReportsService(db)
        royalty_data = await service.get_royalty_data(current_user.id, period)
        
        return {"royalty_data": royalty_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get royalty data: {str(e)}")

@music_reports_router.get("/royalties/summary")
async def get_royalty_summary(
    current_user: User = Depends(get_current_user)
):
    """Get royalty collection summary"""
    try:
        service = MusicReportsService(db)
        royalty_data = await service.get_royalty_data(current_user.id)
        
        summary = {
            "total_collected": royalty_data.get("total_collected", 0),
            "pending_payment": royalty_data.get("pending_payment", 0),
            "paid_out": royalty_data.get("paid_out", 0),
            "currency": royalty_data.get("currency", "USD"),
            "last_payment": royalty_data.get("payment_schedule", [{}])[0] if royalty_data.get("payment_schedule") else None,
            "next_payment": next((p for p in royalty_data.get("payment_schedule", []) if p.get("status") == "pending"), None)
        }
        
        return {"royalty_summary": summary}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get royalty summary: {str(e)}")

@music_reports_router.get("/capabilities")
async def get_sync_capabilities(
    current_user: User = Depends(get_current_user)
):
    """Get Music Reports sync capabilities and supported features"""
    try:
        service = MusicReportsService(db)
        capabilities = await service.get_sync_capabilities()
        
        return {"capabilities": capabilities}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

@music_reports_router.get("/sync-history")
async def get_sync_history(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, description="Number of sync records to return")
):
    """Get Music Reports sync history"""
    try:
        # Get sync history from database
        sync_history = await db.music_reports_sync_history.find(
            {"user_id": current_user.id}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        # Format sync history
        formatted_history = []
        for record in sync_history:
            formatted_record = {
                "sync_id": record.get("sync_id"),
                "timestamp": record.get("timestamp").isoformat() if record.get("timestamp") else None,
                "status": record.get("status"),
                "works_processed": record.get("works_processed", 0),
                "duration": record.get("metadata", {}).get("duration_seconds"),
                "errors": record.get("metadata", {}).get("errors", [])
            }
            formatted_history.append(formatted_record)
        
        return {"sync_history": formatted_history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sync history: {str(e)}")

@music_reports_router.get("/statements")
async def get_royalty_statements(
    current_user: User = Depends(get_current_user)
):
    """Get royalty statements from Music Reports"""
    try:
        service = MusicReportsService(db)
        royalty_data = await service.get_royalty_data(current_user.id)
        
        statements = royalty_data.get("statements", [])
        
        return {"statements": statements}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statements: {str(e)}")

@music_reports_router.get("/statements/{statement_id}")
async def download_statement(
    statement_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download a specific royalty statement"""
    try:
        # In a real implementation, this would generate/fetch the actual statement
        # For now, return mock data
        statement_info = {
            "statement_id": statement_id,
            "user_id": current_user.id,
            "generated_date": datetime.now(timezone.utc).isoformat(),
            "download_url": f"/api/music-reports/statements/{statement_id}/download",
            "format": "PDF",
            "size": "245 KB",
            "status": "ready"
        }
        
        return {"statement": statement_info}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statement: {str(e)}")

# Helper functions

async def _get_recent_activity(db, user_id: str) -> list:
    """Get recent Music Reports activity"""
    try:
        activities = []
        
        # Add recent sync activities
        recent_syncs = await db.music_reports_sync_history.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(5).to_list(5)
        
        for sync in recent_syncs:
            activities.append({
                "type": "sync",
                "message": f"Sync completed - {sync.get('works_processed', 0)} works processed",
                "timestamp": sync.get("timestamp").isoformat() if sync.get("timestamp") else None,
                "status": sync.get("status")
            })
        
        # Add mock activities if no real data
        if not activities:
            activities = [
                {
                    "type": "system",
                    "message": "Music Reports integration initialized",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "info"
                },
                {
                    "type": "config",
                    "message": "CWR framework configured for multiple PROs",
                    "timestamp": (datetime.now(timezone.utc)).isoformat(),
                    "status": "success"
                },
                {
                    "type": "pending",
                    "message": "Awaiting Music Reports API credentials for live sync",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "warning"
                }
            ]
        
        return activities[:10]  # Return max 10 activities
        
    except Exception as e:
        return [{
            "type": "error",
            "message": f"Error loading activity: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "error"
        }]