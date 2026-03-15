"""Amazon QuickSight & Athena routes - Data analytics & BI dashboards."""
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from auth.service import get_current_user
from models.core import User

router = APIRouter(prefix="/aws-data", tags=["AWS Data Analytics"])
logger = logging.getLogger(__name__)

_qs_svc = None
_athena_svc = None


def _quicksight():
    global _qs_svc
    if _qs_svc is None:
        from services.quicksight_service import QuickSightService
        _qs_svc = QuickSightService()
    return _qs_svc


def _athena():
    global _athena_svc
    if _athena_svc is None:
        from services.athena_service import AthenaService
        _athena_svc = AthenaService()
    return _athena_svc


# ── Pydantic models ──────────────────────────────────────────────
class StartQueryRequest(BaseModel):
    query: str
    database: str = "default"
    work_group: str = "primary"


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def data_status(current_user: User = Depends(get_current_user)):
    """Overall status of QuickSight + Athena."""
    qs = _quicksight()
    ath = _athena()
    return {
        "quicksight": qs.get_status(),
        "athena": ath.get_status(),
    }


# ══════════════════════════════════════════════════════════════════
#  QUICKSIGHT - Dashboards
# ══════════════════════════════════════════════════════════════════
@router.get("/quicksight/dashboards")
async def list_dashboards(current_user: User = Depends(get_current_user)):
    """List QuickSight dashboards."""
    qs = _quicksight()
    if not qs.available:
        raise HTTPException(503, "QuickSight not available")
    try:
        dashboards = qs.list_dashboards()
        return {"dashboards": dashboards, "total": len(dashboards)}
    except Exception as e:
        logger.error(f"List dashboards error: {e}")
        raise HTTPException(500, f"Failed to list dashboards: {str(e)}")


@router.get("/quicksight/dashboards/{dashboard_id}")
async def describe_dashboard(
    dashboard_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get dashboard details."""
    qs = _quicksight()
    if not qs.available:
        raise HTTPException(503, "QuickSight not available")
    try:
        return qs.describe_dashboard(dashboard_id)
    except Exception as e:
        raise HTTPException(404, f"Dashboard not found: {str(e)}")


@router.get("/quicksight/datasets")
async def list_datasets(current_user: User = Depends(get_current_user)):
    """List QuickSight datasets."""
    qs = _quicksight()
    if not qs.available:
        raise HTTPException(503, "QuickSight not available")
    try:
        datasets = qs.list_datasets()
        return {"datasets": datasets, "total": len(datasets)}
    except Exception as e:
        logger.error(f"List datasets error: {e}")
        raise HTTPException(500, f"Failed to list datasets: {str(e)}")


@router.get("/quicksight/data-sources")
async def list_data_sources(current_user: User = Depends(get_current_user)):
    """List QuickSight data sources."""
    qs = _quicksight()
    if not qs.available:
        raise HTTPException(503, "QuickSight not available")
    try:
        sources = qs.list_data_sources()
        return {"data_sources": sources, "total": len(sources)}
    except Exception as e:
        logger.error(f"List data sources error: {e}")
        raise HTTPException(500, f"Failed to list data sources: {str(e)}")


@router.get("/quicksight/analyses")
async def list_analyses(current_user: User = Depends(get_current_user)):
    """List QuickSight analyses."""
    qs = _quicksight()
    if not qs.available:
        raise HTTPException(503, "QuickSight not available")
    try:
        analyses = qs.list_analyses()
        return {"analyses": analyses, "total": len(analyses)}
    except Exception as e:
        logger.error(f"List analyses error: {e}")
        raise HTTPException(500, f"Failed to list analyses: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  ATHENA - SQL Queries on S3
# ══════════════════════════════════════════════════════════════════
@router.get("/athena/work-groups")
async def list_work_groups(current_user: User = Depends(get_current_user)):
    """List Athena work groups."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        groups = ath.list_work_groups()
        return {"work_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List work groups error: {e}")
        raise HTTPException(500, f"Failed to list work groups: {str(e)}")


@router.get("/athena/databases")
async def list_databases(
    catalog: str = Query("AwsDataCatalog"),
    current_user: User = Depends(get_current_user),
):
    """List Athena databases."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        databases = ath.list_databases(catalog)
        return {"databases": databases, "total": len(databases)}
    except Exception as e:
        logger.error(f"List databases error: {e}")
        raise HTTPException(500, f"Failed to list databases: {str(e)}")


@router.get("/athena/tables")
async def list_tables(
    catalog: str = Query("AwsDataCatalog"),
    database: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """List tables in a database."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        tables = ath.list_table_metadata(catalog, database)
        return {"tables": tables, "total": len(tables)}
    except Exception as e:
        logger.error(f"List tables error: {e}")
        raise HTTPException(500, f"Failed to list tables: {str(e)}")


@router.get("/athena/saved-queries")
async def list_saved_queries(
    work_group: str = Query("primary"),
    current_user: User = Depends(get_current_user),
):
    """List saved named queries."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        queries = ath.list_named_queries(work_group)
        return {"queries": queries, "total": len(queries)}
    except Exception as e:
        logger.error(f"List named queries error: {e}")
        raise HTTPException(500, f"Failed to list queries: {str(e)}")


@router.post("/athena/query")
async def start_query(
    body: StartQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Start an Athena query execution."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        result = ath.start_query(body.query, body.database, body.work_group)
        return result
    except Exception as e:
        logger.error(f"Start query error: {e}")
        raise HTTPException(500, f"Failed to start query: {str(e)}")


@router.get("/athena/query/{execution_id}/status")
async def query_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
):
    """Check query execution status."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        return ath.get_query_status(execution_id)
    except Exception as e:
        raise HTTPException(404, f"Query not found: {str(e)}")


@router.get("/athena/query/{execution_id}/results")
async def query_results(
    execution_id: str,
    max_results: int = Query(100, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get query results."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        return ath.get_query_results(execution_id, max_results)
    except Exception as e:
        raise HTTPException(500, f"Failed to get results: {str(e)}")


@router.get("/athena/executions")
async def list_executions(
    work_group: str = Query("primary"),
    current_user: User = Depends(get_current_user),
):
    """List recent query executions."""
    ath = _athena()
    if not ath.available:
        raise HTTPException(503, "Athena not available")
    try:
        execs = ath.list_query_executions(work_group)
        return {"executions": execs, "total": len(execs)}
    except Exception as e:
        logger.error(f"List executions error: {e}")
        raise HTTPException(500, f"Failed to list executions: {str(e)}")
