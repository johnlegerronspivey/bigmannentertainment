"""
Audit Trail & Logging API Endpoints
Provides secure access to audit logs, metadata snapshots, and compliance reports
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Form, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
import jwt
import json
import io
import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from audit_models import (
    AuditLogQuery, AuditReport, AuditEventType, AuditSeverity, AuditOutcome
)
from audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit Trail & Logging"])

# Global services
audit_service = None
mongo_db = None

# Authentication setup
SECRET_KEY = "big-mann-entertainment-secret-key-2025"
ALGORITHM = "HS256"
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    if mongo_db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    user = await mongo_db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Get current admin user"""
    if not current_user.get('is_admin') and current_user.get('role') not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_current_super_admin_user(current_user: dict = Depends(get_current_user)):
    """Get current super admin user"""
    if current_user.get('role') != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user

def get_user_role(current_user: dict) -> str:
    """Determine user role for access control"""
    if current_user.get('role') == "super_admin":
        return "super_admin"
    elif current_user.get('is_admin') or current_user.get('role') in ["admin", "moderator"]:
        return "admin"
    else:
        return "content_owner"

def init_audit_service(db, services_dict):
    """Initialize audit service"""
    global audit_service, mongo_db
    mongo_db = db
    audit_service = AuditService(mongo_db=db)
    services_dict['audit'] = audit_service

# Audit Log Endpoints

@router.get("/logs")
async def get_audit_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    event_types: Optional[str] = Query(None),
    severities: Optional[str] = Query(None),
    outcomes: Optional[str] = Query(None),
    search_text: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("timestamp"),
    sort_order: str = Query("desc"),
    current_user: dict = Depends(get_current_user)
):
    """Get audit logs with proper access control"""
    
    try:
        # Parse query parameters
        event_type_list = []
        if event_types:
            for et in event_types.split(","):
                try:
                    event_type_list.append(AuditEventType(et.strip()))
                except ValueError:
                    pass
        
        severity_list = []
        if severities:
            for s in severities.split(","):
                try:
                    severity_list.append(AuditSeverity(s.strip()))
                except ValueError:
                    pass
        
        outcome_list = []
        if outcomes:
            for o in outcomes.split(","):
                try:
                    outcome_list.append(AuditOutcome(o.strip()))
                except ValueError:
                    pass
        
        # Build query
        query = AuditLogQuery(
            start_date=start_date,
            end_date=end_date,
            event_types=event_type_list,
            severities=severity_list,
            outcomes=outcome_list,
            search_text=search_text,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Determine user role and get logs
        user_role = get_user_role(current_user)
        user_id = current_user.get('id')
        
        result = await audit_service.query_audit_logs(query, user_role, user_id)
        
        return {
            "success": True,
            "audit_logs": result["logs"],
            "total_count": result["total"],
            "limit": result["limit"],
            "offset": result["offset"],
            "user_access_level": user_role
        }
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit logs: {str(e)}"
        )

@router.get("/logs/{log_id}")
async def get_audit_log_details(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about specific audit log"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get the audit log
        audit_log = await mongo_db["audit_logs"].find_one({"_id": log_id})
        
        if not audit_log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        # Apply access control
        user_role = get_user_role(current_user)
        user_id = current_user.get('id')
        
        if user_role == "content_owner" and audit_log.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Remove MongoDB _id
        audit_log.pop("_id", None)
        
        # Get related logs (upload, validation, rights check)
        related_logs = {}
        
        if audit_log.get("event_type") == "upload":
            upload_log = await mongo_db["upload_audit_logs"].find_one({"audit_log_id": log_id})
            if upload_log:
                upload_log.pop("_id", None)
                related_logs["upload_details"] = upload_log
        
        elif audit_log.get("event_type") == "validation":
            validation_log = await mongo_db["validation_audit_logs"].find_one({"audit_log_id": log_id})
            if validation_log:
                validation_log.pop("_id", None)
                related_logs["validation_details"] = validation_log
        
        elif audit_log.get("event_type") == "rights_check":
            rights_log = await mongo_db["rights_check_audit_logs"].find_one({"audit_log_id": log_id})
            if rights_log:
                rights_log.pop("_id", None)
                related_logs["rights_check_details"] = rights_log
        
        return {
            "success": True,
            "audit_log": audit_log,
            "related_logs": related_logs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit log details: {str(e)}"
        )

@router.get("/snapshots/{content_id}")
async def get_metadata_snapshots(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get metadata snapshots for content"""
    
    try:
        user_role = get_user_role(current_user)
        user_id = current_user.get('id')
        
        snapshots = await audit_service.get_metadata_snapshots(content_id, user_id, user_role)
        
        return {
            "success": True,
            "content_id": content_id,
            "snapshots": snapshots,
            "total_count": len(snapshots)
        }
        
    except Exception as e:
        logger.error(f"Error getting metadata snapshots: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metadata snapshots: {str(e)}"
        )

@router.get("/timeline/{content_id}")
async def get_content_audit_timeline(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get complete audit timeline for specific content"""
    
    try:
        user_role = get_user_role(current_user)
        user_id = current_user.get('id')
        
        # Query all logs for this content
        query = AuditLogQuery(
            content_ids=[content_id],
            sort_by="timestamp",
            sort_order="asc",
            limit=1000
        )
        
        result = await audit_service.query_audit_logs(query, user_role, user_id)
        
        # Get metadata snapshots
        snapshots = await audit_service.get_metadata_snapshots(content_id, user_id, user_role)
        
        # Combine and sort timeline events
        timeline_events = []
        
        # Add audit logs
        for log in result["logs"]:
            timeline_events.append({
                "type": "audit_log",
                "timestamp": log.get("timestamp"),
                "event_type": log.get("event_type"),
                "event_name": log.get("event_name"),
                "severity": log.get("severity"),
                "outcome": log.get("outcome"),
                "data": log
            })
        
        # Add snapshots
        for snapshot in snapshots:
            timeline_events.append({
                "type": "metadata_snapshot",
                "timestamp": snapshot.get("snapshot_timestamp"),
                "event_type": "metadata_update",
                "event_name": f"Metadata Snapshot - {snapshot.get('trigger_event', 'Unknown')}",
                "severity": "info",
                "outcome": "success",
                "data": snapshot
            })
        
        # Sort by timestamp
        timeline_events.sort(key=lambda x: x.get("timestamp", datetime.min))
        
        return {
            "success": True,
            "content_id": content_id,
            "timeline": timeline_events,
            "total_events": len(timeline_events)
        }
        
    except Exception as e:
        logger.error(f"Error getting content audit timeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content audit timeline: {str(e)}"
        )

# Report Generation Endpoints

@router.post("/reports/generate")
async def generate_audit_report(
    report_name: str = Form(...),
    report_type: str = Form("summary"),
    start_date: Optional[datetime] = Form(None),
    end_date: Optional[datetime] = Form(None),
    event_types: Optional[str] = Form(None),
    export_format: str = Form("pdf"),
    include_metadata_snapshots: bool = Form(False),
    include_file_details: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    """Generate comprehensive audit report"""
    
    try:
        # Parse event types
        event_type_list = []
        if event_types:
            for et in event_types.split(","):
                try:
                    event_type_list.append(AuditEventType(et.strip()))
                except ValueError:
                    pass
        
        # Build query
        query = AuditLogQuery(
            start_date=start_date,
            end_date=end_date,
            event_types=event_type_list,
            limit=10000  # Large limit for reports
        )
        
        # Create report configuration
        report_config = AuditReport(
            report_name=report_name,
            report_type=report_type,
            query=query,
            export_format=export_format,
            include_metadata_snapshots=include_metadata_snapshots,
            include_file_details=include_file_details,
            generated_by=current_user.get('id')
        )
        
        # Generate report
        user_role = get_user_role(current_user)
        user_id = current_user.get('id')
        
        report_data = await audit_service.generate_audit_report(report_config, user_role, user_id)
        
        if "error" in report_data:
            raise HTTPException(status_code=500, detail=report_data["error"])
        
        return {
            "success": True,
            "report_id": report_config.report_id,
            "report_data": report_data,
            "download_ready": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating audit report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate audit report: {str(e)}"
        )

@router.get("/reports/{report_id}/download/{format}")
async def download_audit_report(
    report_id: str,
    format: str,
    current_user: dict = Depends(get_current_user)
):
    """Download audit report in specified format"""
    
    try:
        # For demonstration, we'll create a simple report
        # In production, you'd retrieve the stored report data
        
        user_role = get_user_role(current_user)
        user_id = current_user.get('id')
        
        # Query recent audit logs for the report
        query = AuditLogQuery(
            start_date=datetime.now() - timedelta(days=30),
            limit=1000
        )
        
        result = await audit_service.query_audit_logs(query, user_role, user_id)
        
        if format.lower() == "csv":
            return await _generate_csv_report(result["logs"], report_id)
        elif format.lower() == "pdf":
            return await _generate_pdf_report(result["logs"], report_id)
        elif format.lower() == "json":
            return await _generate_json_report(result["logs"], report_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audit report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download audit report: {str(e)}"
        )

# Real-time Monitoring Endpoints

@router.get("/alerts")
async def get_real_time_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get real-time alerts (admin only)"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Build query filters
        query = {}
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity
        
        # Get total count
        total_count = await mongo_db["real_time_alerts"].count_documents(query)
        
        # Get paginated results
        cursor = mongo_db["real_time_alerts"].find(query) \
            .sort("created_at", -1) \
            .skip(offset) \
            .limit(limit)
        
        alerts = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id
        for alert in alerts:
            alert.pop("_id", None)
        
        return {
            "success": True,
            "alerts": alerts,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get real-time alerts: {str(e)}"
        )

@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Acknowledge real-time alert"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Update alert status
        result = await mongo_db["real_time_alerts"].update_one(
            {"_id": alert_id},
            {
                "$set": {
                    "status": "acknowledged",
                    "acknowledged_by": current_user.get('id'),
                    "acknowledged_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "success": True,
            "message": "Alert acknowledged successfully",
            "alert_id": alert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )

# Statistics and Analytics Endpoints

@router.get("/statistics")
async def get_audit_statistics(
    period: str = Query("daily"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get audit trail statistics and analytics"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Default date range
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            if period == "daily":
                start_date = end_date - timedelta(days=30)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=12)
            else:
                start_date = end_date - timedelta(days=365)
        
        # Apply access control
        user_role = get_user_role(current_user)
        user_id = current_user.get('id')
        
        # Build base query with access control
        base_query = {"timestamp": {"$gte": start_date, "$lte": end_date}}
        
        if user_role == "content_owner":
            base_query["user_id"] = user_id
        
        # Get event counts by type
        pipeline = [
            {"$match": base_query},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        events_by_type = {}
        async for result in mongo_db["audit_logs"].aggregate(pipeline):
            events_by_type[result["_id"]] = result["count"]
        
        # Get severity distribution
        pipeline = [
            {"$match": base_query},
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        events_by_severity = {}
        async for result in mongo_db["audit_logs"].aggregate(pipeline):
            events_by_severity[result["_id"]] = result["count"]
        
        # Get outcome distribution
        pipeline = [
            {"$match": base_query},
            {"$group": {"_id": "$outcome", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        events_by_outcome = {}
        async for result in mongo_db["audit_logs"].aggregate(pipeline):
            events_by_outcome[result["_id"]] = result["count"]
        
        # Get total events
        total_events = await mongo_db["audit_logs"].count_documents(base_query)
        
        # Get upload statistics
        upload_query = {**base_query, "event_type": "upload"}
        total_uploads = await mongo_db["audit_logs"].count_documents(upload_query)
        
        successful_uploads = await mongo_db["audit_logs"].count_documents({
            **upload_query,
            "outcome": "success"
        })
        
        # Get validation statistics
        validation_query = {**base_query, "event_type": "validation"}
        total_validations = await mongo_db["audit_logs"].count_documents(validation_query)
        
        successful_validations = await mongo_db["audit_logs"].count_documents({
            **validation_query,
            "outcome": "success"
        })
        
        return {
            "success": True,
            "period": period,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "statistics": {
                "total_events": total_events,
                "events_by_type": events_by_type,
                "events_by_severity": events_by_severity,
                "events_by_outcome": events_by_outcome,
                "upload_stats": {
                    "total_uploads": total_uploads,
                    "successful_uploads": successful_uploads,
                    "success_rate": (successful_uploads / total_uploads * 100) if total_uploads > 0 else 0
                },
                "validation_stats": {
                    "total_validations": total_validations,
                    "successful_validations": successful_validations,
                    "success_rate": (successful_validations / total_validations * 100) if total_validations > 0 else 0
                }
            },
            "user_access_level": user_role
        }
        
    except Exception as e:
        logger.error(f"Error getting audit statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit statistics: {str(e)}"
        )

# Admin Only Endpoints

@router.get("/admin/platform-statistics")
async def get_platform_audit_statistics(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get platform-wide audit statistics (admin only)"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get comprehensive platform statistics
        stats = {}
        
        # Total events
        stats["total_audit_events"] = await mongo_db["audit_logs"].count_documents({})
        
        # Total users with activity
        pipeline = [
            {"$group": {"_id": "$user_id"}},
            {"$count": "unique_users"}
        ]
        
        user_count_result = await mongo_db["audit_logs"].aggregate(pipeline).to_list(length=1)
        stats["active_users"] = user_count_result[0]["unique_users"] if user_count_result else 0
        
        # Total content items tracked
        pipeline = [
            {"$match": {"content_id": {"$ne": None}}},
            {"$group": {"_id": "$content_id"}},
            {"$count": "unique_content"}
        ]
        
        content_count_result = await mongo_db["audit_logs"].aggregate(pipeline).to_list(length=1)
        stats["tracked_content_items"] = content_count_result[0]["unique_content"] if content_count_result else 0
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        stats["recent_activity_24h"] = await mongo_db["audit_logs"].count_documents({
            "timestamp": {"$gte": yesterday}
        })
        
        # Alert counts
        stats["active_alerts"] = await mongo_db["real_time_alerts"].count_documents({
            "status": "active"
        })
        
        stats["total_alerts"] = await mongo_db["real_time_alerts"].count_documents({})
        
        # Storage statistics
        stats["total_snapshots"] = await mongo_db["metadata_snapshots"].count_documents({})
        stats["total_upload_logs"] = await mongo_db["upload_audit_logs"].count_documents({})
        stats["total_validation_logs"] = await mongo_db["validation_audit_logs"].count_documents({})
        stats["total_rights_check_logs"] = await mongo_db["rights_check_audit_logs"].count_documents({})
        
        return {
            "success": True,
            "platform_statistics": stats,
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting platform audit statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get platform audit statistics: {str(e)}"
        )

@router.delete("/admin/cleanup")
async def cleanup_old_audit_data(
    retention_days: int = Query(2555, ge=30, le=3650),  # Default 7 years
    dry_run: bool = Query(True),
    current_user: dict = Depends(get_current_super_admin_user)
):
    """Cleanup old audit data based on retention policy (super admin only)"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Count records that would be deleted
        old_logs_count = await mongo_db["audit_logs"].count_documents({
            "timestamp": {"$lt": cutoff_date}
        })
        
        old_snapshots_count = await mongo_db["metadata_snapshots"].count_documents({
            "snapshot_timestamp": {"$lt": cutoff_date}
        })
        
        old_uploads_count = await mongo_db["upload_audit_logs"].count_documents({
            "created_at": {"$lt": cutoff_date}
        })
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "cutoff_date": cutoff_date,
                "records_to_delete": {
                    "audit_logs": old_logs_count,
                    "metadata_snapshots": old_snapshots_count,
                    "upload_logs": old_uploads_count
                }
            }
        else:
            # Actually delete old records
            deleted_logs = await mongo_db["audit_logs"].delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            deleted_snapshots = await mongo_db["metadata_snapshots"].delete_many({
                "snapshot_timestamp": {"$lt": cutoff_date}
            })
            
            deleted_uploads = await mongo_db["upload_audit_logs"].delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            # Log the cleanup action
            await audit_service.log_audit_event(
                event_type=AuditEventType.DATA_DELETION,
                event_name="Audit Data Cleanup",
                event_description=f"Cleaned up audit data older than {retention_days} days",
                user_context={"user_id": current_user.get('id'), "user_role": "super_admin"},
                event_data={
                    "retention_days": retention_days,
                    "deleted_counts": {
                        "audit_logs": deleted_logs.deleted_count,
                        "metadata_snapshots": deleted_snapshots.deleted_count,
                        "upload_logs": deleted_uploads.deleted_count
                    }
                },
                severity=AuditSeverity.WARNING
            )
            
            return {
                "success": True,
                "dry_run": False,
                "cutoff_date": cutoff_date,
                "deleted_records": {
                    "audit_logs": deleted_logs.deleted_count,
                    "metadata_snapshots": deleted_snapshots.deleted_count,
                    "upload_logs": deleted_uploads.deleted_count
                }
            }
        
    except Exception as e:
        logger.error(f"Error cleaning up audit data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup audit data: {str(e)}"
        )

# Helper functions for report generation

async def _generate_csv_report(logs: List[Dict[str, Any]], report_id: str) -> StreamingResponse:
    """Generate CSV report"""
    output = io.StringIO()
    
    if logs:
        writer = csv.DictWriter(output, fieldnames=logs[0].keys())
        writer.writeheader()
        for log in logs:
            # Convert datetime objects to strings
            formatted_log = {}
            for key, value in log.items():
                if isinstance(value, datetime):
                    formatted_log[key] = value.isoformat()
                else:
                    formatted_log[key] = str(value) if value is not None else ""
            writer.writerow(formatted_log)
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=audit_report_{report_id}.csv"}
    )

async def _generate_json_report(logs: List[Dict[str, Any]], report_id: str) -> StreamingResponse:
    """Generate JSON report"""
    
    # Convert datetime objects to strings for JSON serialization
    formatted_logs = []
    for log in logs:
        formatted_log = {}
        for key, value in log.items():
            if isinstance(value, datetime):
                formatted_log[key] = value.isoformat()
            else:
                formatted_log[key] = value
        formatted_logs.append(formatted_log)
    
    report_data = {
        "report_id": report_id,
        "generated_at": datetime.now().isoformat(),
        "total_records": len(formatted_logs),
        "audit_logs": formatted_logs
    }
    
    json_str = json.dumps(report_data, indent=2, default=str)
    
    return StreamingResponse(
        io.BytesIO(json_str.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=audit_report_{report_id}.json"}
    )

async def _generate_pdf_report(logs: List[Dict[str, Any]], report_id: str) -> StreamingResponse:
    """Generate PDF report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"Big Mann Entertainment - Audit Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Report info
    info = Paragraph(f"Report ID: {report_id}<br/>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Total Records: {len(logs)}", styles['Normal'])
    story.append(info)
    story.append(Spacer(1, 12))
    
    # Summary table
    if logs:
        # Create summary statistics
        event_types = {}
        for log in logs:
            event_type = log.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        summary_data = [['Event Type', 'Count']]
        for event_type, count in event_types.items():
            summary_data.append([event_type, str(count)])
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Event Summary", styles['Heading2']))
        story.append(summary_table)
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=audit_report_{report_id}.pdf"}
    )