"""AWS Infrastructure routes - Step Functions, ElastiCache, Neptune."""
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from auth.service import get_current_user
from models.core import User

router = APIRouter(prefix="/aws-infra", tags=["AWS Infrastructure"])
logger = logging.getLogger(__name__)

_stepfunctions_svc = None
_elasticache_svc = None
_neptune_svc = None


def _stepfunctions():
    global _stepfunctions_svc
    if _stepfunctions_svc is None:
        from services.stepfunctions_service import StepFunctionsService
        _stepfunctions_svc = StepFunctionsService()
    return _stepfunctions_svc


def _elasticache():
    global _elasticache_svc
    if _elasticache_svc is None:
        from services.elasticache_service import ElastiCacheService
        _elasticache_svc = ElastiCacheService()
    return _elasticache_svc


def _neptune():
    global _neptune_svc
    if _neptune_svc is None:
        from services.neptune_service import NeptuneService
        _neptune_svc = NeptuneService()
    return _neptune_svc


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def infra_status(current_user: User = Depends(get_current_user)):
    return {
        "step_functions": _stepfunctions().get_status(),
        "elasticache": _elasticache().get_status(),
        "neptune": _neptune().get_status(),
    }


# ══════════════════════════════════════════════════════════════════
#  STEP FUNCTIONS
# ══════════════════════════════════════════════════════════════════
@router.get("/stepfunctions/state-machines")
async def list_state_machines(current_user: User = Depends(get_current_user)):
    svc = _stepfunctions()
    if not svc.available:
        raise HTTPException(503, "Step Functions not available")
    try:
        machines = svc.list_state_machines()
        return {"state_machines": machines, "total": len(machines)}
    except Exception as e:
        logger.error(f"List state machines error: {e}")
        raise HTTPException(500, f"Failed to list state machines: {str(e)}")


@router.get("/stepfunctions/state-machines/{arn:path}")
async def describe_state_machine(arn: str, current_user: User = Depends(get_current_user)):
    svc = _stepfunctions()
    if not svc.available:
        raise HTTPException(503, "Step Functions not available")
    try:
        return svc.describe_state_machine(arn)
    except Exception as e:
        logger.error(f"Describe state machine error: {e}")
        raise HTTPException(500, f"Failed to describe state machine: {str(e)}")


@router.get("/stepfunctions/executions")
async def list_executions(
    state_machine_arn: str = Query(...),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    svc = _stepfunctions()
    if not svc.available:
        raise HTTPException(503, "Step Functions not available")
    try:
        execs = svc.list_executions(state_machine_arn, status_filter=status_filter)
        return {"executions": execs, "total": len(execs)}
    except Exception as e:
        logger.error(f"List executions error: {e}")
        raise HTTPException(500, f"Failed to list executions: {str(e)}")


@router.get("/stepfunctions/execution/{arn:path}")
async def describe_execution(arn: str, current_user: User = Depends(get_current_user)):
    svc = _stepfunctions()
    if not svc.available:
        raise HTTPException(503, "Step Functions not available")
    try:
        return svc.describe_execution(arn)
    except Exception as e:
        logger.error(f"Describe execution error: {e}")
        raise HTTPException(500, f"Failed to describe execution: {str(e)}")


@router.get("/stepfunctions/activities")
async def list_activities(current_user: User = Depends(get_current_user)):
    svc = _stepfunctions()
    if not svc.available:
        raise HTTPException(503, "Step Functions not available")
    try:
        activities = svc.list_activities()
        return {"activities": activities, "total": len(activities)}
    except Exception as e:
        logger.error(f"List activities error: {e}")
        raise HTTPException(500, f"Failed to list activities: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  ELASTICACHE
# ══════════════════════════════════════════════════════════════════
@router.get("/elasticache/clusters")
async def list_cache_clusters(current_user: User = Depends(get_current_user)):
    svc = _elasticache()
    if not svc.available:
        raise HTTPException(503, "ElastiCache not available")
    try:
        clusters = svc.list_clusters()
        return {"clusters": clusters, "total": len(clusters)}
    except Exception as e:
        logger.error(f"List clusters error: {e}")
        raise HTTPException(500, f"Failed to list clusters: {str(e)}")


@router.get("/elasticache/replication-groups")
async def list_replication_groups(current_user: User = Depends(get_current_user)):
    svc = _elasticache()
    if not svc.available:
        raise HTTPException(503, "ElastiCache not available")
    try:
        groups = svc.list_replication_groups()
        return {"replication_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List replication groups error: {e}")
        raise HTTPException(500, f"Failed to list replication groups: {str(e)}")


@router.get("/elasticache/snapshots")
async def list_cache_snapshots(current_user: User = Depends(get_current_user)):
    svc = _elasticache()
    if not svc.available:
        raise HTTPException(503, "ElastiCache not available")
    try:
        snapshots = svc.list_snapshots()
        return {"snapshots": snapshots, "total": len(snapshots)}
    except Exception as e:
        logger.error(f"List snapshots error: {e}")
        raise HTTPException(500, f"Failed to list snapshots: {str(e)}")


@router.get("/elasticache/reserved-nodes")
async def list_reserved_nodes(current_user: User = Depends(get_current_user)):
    svc = _elasticache()
    if not svc.available:
        raise HTTPException(503, "ElastiCache not available")
    try:
        nodes = svc.list_reserved_nodes()
        return {"reserved_nodes": nodes, "total": len(nodes)}
    except Exception as e:
        logger.error(f"List reserved nodes error: {e}")
        raise HTTPException(500, f"Failed to list reserved nodes: {str(e)}")


@router.get("/elasticache/subnet-groups")
async def list_subnet_groups(current_user: User = Depends(get_current_user)):
    svc = _elasticache()
    if not svc.available:
        raise HTTPException(503, "ElastiCache not available")
    try:
        groups = svc.list_subnet_groups()
        return {"subnet_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List subnet groups error: {e}")
        raise HTTPException(500, f"Failed to list subnet groups: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  NEPTUNE
# ══════════════════════════════════════════════════════════════════
@router.get("/neptune/clusters")
async def list_neptune_clusters(current_user: User = Depends(get_current_user)):
    svc = _neptune()
    if not svc.available:
        raise HTTPException(503, "Neptune not available")
    try:
        clusters = svc.list_clusters()
        return {"clusters": clusters, "total": len(clusters)}
    except Exception as e:
        logger.error(f"List clusters error: {e}")
        raise HTTPException(500, f"Failed to list clusters: {str(e)}")


@router.get("/neptune/instances")
async def list_neptune_instances(current_user: User = Depends(get_current_user)):
    svc = _neptune()
    if not svc.available:
        raise HTTPException(503, "Neptune not available")
    try:
        instances = svc.list_instances()
        return {"instances": instances, "total": len(instances)}
    except Exception as e:
        logger.error(f"List instances error: {e}")
        raise HTTPException(500, f"Failed to list instances: {str(e)}")


@router.get("/neptune/snapshots")
async def list_neptune_snapshots(current_user: User = Depends(get_current_user)):
    svc = _neptune()
    if not svc.available:
        raise HTTPException(503, "Neptune not available")
    try:
        snapshots = svc.list_cluster_snapshots()
        return {"snapshots": snapshots, "total": len(snapshots)}
    except Exception as e:
        logger.error(f"List snapshots error: {e}")
        raise HTTPException(500, f"Failed to list snapshots: {str(e)}")


@router.get("/neptune/parameter-groups")
async def list_parameter_groups(current_user: User = Depends(get_current_user)):
    svc = _neptune()
    if not svc.available:
        raise HTTPException(503, "Neptune not available")
    try:
        groups = svc.list_parameter_groups()
        return {"parameter_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List parameter groups error: {e}")
        raise HTTPException(500, f"Failed to list parameter groups: {str(e)}")


@router.get("/neptune/subnet-groups")
async def list_neptune_subnet_groups(current_user: User = Depends(get_current_user)):
    svc = _neptune()
    if not svc.available:
        raise HTTPException(503, "Neptune not available")
    try:
        groups = svc.list_subnet_groups()
        return {"subnet_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List subnet groups error: {e}")
        raise HTTPException(500, f"Failed to list subnet groups: {str(e)}")
