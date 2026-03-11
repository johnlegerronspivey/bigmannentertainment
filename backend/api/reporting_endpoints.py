"""
Advanced Reporting API Endpoints
Provides comprehensive analytics, reporting, and export capabilities
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
import io

from auth.service import get_current_user, get_current_admin_user as require_admin
from advanced_reporting_service import AdvancedReportingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Advanced Reporting"])

# Global service (will be initialized in server.py)
reporting_service = None
mongo_db = None

def init_reporting_service(db, services_dict):
    """Initialize advanced reporting service"""
    global reporting_service, mongo_db
    mongo_db = db
    reporting_service = AdvancedReportingService(mongo_db=db)
    services_dict['advanced_reporter'] = reporting_service

@router.get("/comprehensive")
async def get_comprehensive_report(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: dict = Depends(get_current_user)
):
    """Generate comprehensive metadata validation report for user"""
    
    try:
        # Parse date range
        date_range = None
        if start_date and end_date:
            date_range = {
                'start_date': start_date,
                'end_date': end_date
            }
        
        report = await reporting_service.generate_comprehensive_report(
            user_id=current_user.id,
            date_range=date_range
        )
        
        return {
            "success": True,
            "report": report
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate comprehensive report: {str(e)}"
        )

@router.get("/duplicates")
async def get_duplicate_report(
    scope: str = Query("user", description="Scope: 'user' or 'platform'"),
    current_user: dict = Depends(get_current_user)
):
    """Generate detailed duplicate detection report"""
    
    try:
        # Admin required for platform scope
        if scope == "platform" and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=403,
                detail="Admin access required for platform-wide duplicate report"
            )
        
        user_id = current_user.id if scope == "user" else None
        
        report = await reporting_service.generate_duplicate_report(
            user_id=user_id,
            scope=scope
        )
        
        return {
            "success": True,
            "duplicate_report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating duplicate report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate duplicate report: {str(e)}"
        )

@router.get("/error-trends")
async def get_error_trend_report(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user)
):
    """Generate error trend analysis report"""
    
    try:
        report = await reporting_service.generate_error_trend_report(
            user_id=current_user.id,
            days=days
        )
        
        return {
            "success": True,
            "error_trend_report": report
        }
        
    except Exception as e:
        logger.error(f"Error generating error trend report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate error trend report: {str(e)}"
        )

@router.get("/export/csv")
async def export_report_csv(
    report_type: str = Query(..., description="Type: validation_summary, format_analysis, duplicate_patterns, error_analysis"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Export report data as CSV"""
    
    try:
        # Generate the appropriate report data
        if report_type == "validation_summary":
            date_range = None
            if start_date and end_date:
                date_range = {'start_date': start_date, 'end_date': end_date}
            
            report_data = await reporting_service.generate_comprehensive_report(
                user_id=current_user.id,
                date_range=date_range
            )
            
        elif report_type == "duplicate_patterns":
            report_data = await reporting_service.generate_duplicate_report(
                user_id=current_user.id,
                scope="user"
            )
            
        elif report_type == "error_analysis":
            report_data = await reporting_service.generate_error_trend_report(
                user_id=current_user.id,
                days=30
            )
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported report type: {report_type}"
            )
        
        # Export to CSV
        csv_content = await reporting_service.export_report_csv(report_data, report_type)
        
        if not csv_content:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate CSV export"
            )
        
        # Create response
        filename = f"metadata_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export CSV: {str(e)}"
        )

@router.get("/export/json")
async def export_report_json(
    report_type: str = Query(..., description="Type: comprehensive, duplicates, error_trends"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Export report data as JSON"""
    
    try:
        # Generate the appropriate report data
        if report_type == "comprehensive":
            date_range = None
            if start_date and end_date:
                date_range = {'start_date': start_date, 'end_date': end_date}
            
            report_data = await reporting_service.generate_comprehensive_report(
                user_id=current_user.id,
                date_range=date_range
            )
            
        elif report_type == "duplicates":
            report_data = await reporting_service.generate_duplicate_report(
                user_id=current_user.id,
                scope="user"
            )
            
        elif report_type == "error_trends":
            report_data = await reporting_service.generate_error_trend_report(
                user_id=current_user.id,
                days=30
            )
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported report type: {report_type}"
            )
        
        # Export to JSON
        json_content = await reporting_service.export_report_json(report_data)
        
        if not json_content:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate JSON export"
            )
        
        # Create response
        filename = f"metadata_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return StreamingResponse(
            io.BytesIO(json_content),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting JSON: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export JSON: {str(e)}"
        )

# Admin endpoints
@router.get("/admin/platform-analytics")
async def admin_get_platform_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin)
):
    """Admin endpoint for platform-wide analytics"""
    
    try:
        # Parse date range
        date_range = None
        if start_date and end_date:
            date_range = {
                'start_date': start_date,
                'end_date': end_date
            }
        
        analytics = await reporting_service.generate_platform_analytics(
            date_range=date_range
        )
        
        return {
            "success": True,
            "platform_analytics": analytics
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating platform analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate platform analytics: {str(e)}"
        )

@router.get("/admin/dashboard-metrics")
async def admin_get_dashboard_metrics(
    current_user: dict = Depends(require_admin)
):
    """Admin endpoint for dashboard metrics"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get current date ranges
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Today's metrics
        today_query = {"upload_date": {"$gte": today}}
        today_validations = await mongo_db["metadata_validation_results"].count_documents(today_query)
        today_errors = await mongo_db["metadata_validation_results"].count_documents({
            **today_query,
            "validation_status": "error"
        })
        
        # This week's metrics
        week_query = {"upload_date": {"$gte": week_ago}}
        week_validations = await mongo_db["metadata_validation_results"].count_documents(week_query)
        week_duplicates = await mongo_db["metadata_validation_results"].count_documents({
            **week_query,
            "duplicate_count": {"$gt": 0}
        })
        
        # This month's metrics
        month_query = {"upload_date": {"$gte": month_ago}}
        month_validations = await mongo_db["metadata_validation_results"].count_documents(month_query)
        
        # Active users (users who uploaded in the last 7 days)
        active_users_pipeline = [
            {"$match": week_query},
            {"$group": {"_id": "$user_id"}},
            {"$count": "active_users"}
        ]
        
        active_users_result = await mongo_db["metadata_validation_results"].aggregate(active_users_pipeline).to_list(1)
        active_users = active_users_result[0]["active_users"] if active_users_result else 0
        
        # Quality score (percentage of valid validations this month)
        if month_validations > 0:
            valid_month = await mongo_db["metadata_validation_results"].count_documents({
                **month_query,
                "validation_status": "valid"
            })
            quality_score = (valid_month / month_validations) * 100
        else:
            quality_score = 0
        
        return {
            "success": True,
            "dashboard_metrics": {
                "today": {
                    "validations": today_validations,
                    "errors": today_errors,
                    "error_rate": (today_errors / today_validations * 100) if today_validations > 0 else 0
                },
                "this_week": {
                    "validations": week_validations,
                    "duplicates": week_duplicates,
                    "active_users": active_users
                },
                "this_month": {
                    "validations": month_validations,
                    "quality_score": round(quality_score, 1)
                },
                "system_health": {
                    "status": "healthy" if today_errors < today_validations * 0.1 else "degraded",
                    "last_updated": now.isoformat()
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )

@router.get("/admin/format-usage-trends")
async def admin_get_format_usage_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: dict = Depends(require_admin)
):
    """Admin endpoint for metadata format usage trends"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Aggregate format usage by day
        pipeline = [
            {
                "$match": {
                    "upload_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$upload_date"}},
                        "format": "$file_format"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": "$_id.date",
                    "formats": {
                        "$push": {
                            "format": "$_id.format", 
                            "count": "$count"
                        }
                    },
                    "total": {"$sum": "$count"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        results = await mongo_db["metadata_validation_results"].aggregate(pipeline).to_list(None)
        
        # Process results into trend data
        trend_data = {}
        for result in results:
            date = result["_id"]
            trend_data[date] = {
                "total": result["total"],
                "formats": {format_info["format"]: format_info["count"] for format_info in result["formats"]}
            }
        
        return {
            "success": True,
            "format_usage_trends": {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "daily_trends": trend_data
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting format usage trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get format usage trends: {str(e)}"
        )