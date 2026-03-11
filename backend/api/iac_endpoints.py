"""
Infrastructure Automation API Endpoints
Provides both local file-based data and live AWS/GitHub API data.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from iac_service import get_iac_service

router = APIRouter(prefix="/cve/iac", tags=["Infrastructure Automation"])


class DeploymentRecord(BaseModel):
    environment: str
    component: str = "lambda"
    version: str = ""
    status: str = "success"
    deployed_by: str = "manual"
    notes: str = ""


class RDSUpgradeRequest(BaseModel):
    instance_id: str
    target_version: str
    apply_immediately: bool = True


# ── existing endpoints (local file-based) ──────────────────────────

@router.get("/overview")
async def get_iac_overview():
    svc = get_iac_service()
    return await svc.get_overview()


@router.get("/terraform")
async def get_terraform_configs():
    svc = get_iac_service()
    return await svc.get_terraform_configs()


@router.get("/lambda")
async def get_lambda_config():
    svc = get_iac_service()
    return await svc.get_lambda_config()


@router.get("/workflow")
async def get_workflow_config():
    svc = get_iac_service()
    return await svc.get_workflow_config()


@router.get("/deployments")
async def get_deployments(limit: int = Query(20, ge=1, le=100)):
    svc = get_iac_service()
    return await svc.get_deployments(limit=limit)


@router.post("/deployments")
async def record_deployment(data: DeploymentRecord):
    svc = get_iac_service()
    return await svc.record_deployment(data.dict())


@router.get("/commands/{environment}")
async def get_deployment_commands(environment: str):
    if environment not in ["dev", "staging", "prod"]:
        raise HTTPException(status_code=400, detail="Invalid environment. Use dev, staging, or prod.")
    svc = get_iac_service()
    return await svc.get_deployment_commands(environment)


# ── RDS management endpoints ────────────────────────────────────────

@router.get("/rds/instances")
async def get_rds_instances():
    """List all PostgreSQL RDS instances with version and status info."""
    svc = get_iac_service()
    return await svc.get_rds_instances()


@router.get("/rds/upgrade-targets/{instance_id}")
async def get_rds_upgrade_targets(instance_id: str):
    """Get available minor version upgrade targets for a specific RDS instance."""
    svc = get_iac_service()
    return await svc.get_rds_upgrade_targets(instance_id)


@router.post("/rds/upgrade")
async def upgrade_rds_instance(data: RDSUpgradeRequest):
    """Initiate a minor version upgrade on an RDS PostgreSQL instance."""
    svc = get_iac_service()
    result = await svc.upgrade_rds_instance(
        instance_id=data.instance_id,
        target_version=data.target_version,
        apply_immediately=data.apply_immediately,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Upgrade failed"))
    return result


# ── NEW live data endpoints ─────────────────────────────────────────

@router.get("/live-status")
async def get_live_status():
    """Check connectivity to AWS Lambda, S3, and GitHub APIs."""
    svc = get_iac_service()
    return await svc.get_live_status()


@router.get("/lambda/live")
async def get_lambda_live():
    """Fetch real Lambda function data and CloudWatch metrics from AWS."""
    svc = get_iac_service()
    return await svc.get_lambda_live()


@router.get("/github/runs")
async def get_github_runs(limit: int = Query(15, ge=1, le=50)):
    """Fetch GitHub Actions workflow runs."""
    svc = get_iac_service()
    return await svc.get_github_runs(limit=limit)


@router.get("/github/repo")
async def get_github_repo_info():
    """Fetch GitHub repo info, recent commits, branches, and open PRs."""
    svc = get_iac_service()
    return await svc.get_github_repo_info()


@router.get("/s3/artifacts")
async def get_s3_artifacts(prefix: str = Query("", description="S3 key prefix filter"), max_keys: int = Query(50, ge=1, le=200)):
    """List objects in the configured S3 bucket."""
    svc = get_iac_service()
    return await svc.get_s3_artifacts(prefix=prefix, max_keys=max_keys)


@router.get("/cloudwatch/alarms")
async def get_cloudwatch_alarms():
    """List CloudWatch metric and composite alarms."""
    svc = get_iac_service()
    return await svc.get_cloudwatch_alarms()


@router.get("/terraform/state")
async def get_terraform_state(environment: str = Query("dev")):
    """Read Terraform state from S3 backend."""
    if environment not in ["dev", "staging", "prod"]:
        raise HTTPException(status_code=400, detail="Invalid environment.")
    svc = get_iac_service()
    return await svc.get_terraform_state(environment=environment)


@router.get("/terraform/modules")
async def get_terraform_modules():
    """Return the infra-terraform module structure with file contents and metadata."""
    svc = get_iac_service()
    return await svc.get_terraform_modules()


@router.get("/cdk/constructs")
async def get_cdk_constructs():
    """Return the infra-cdk construct structure with file contents and metadata."""
    svc = get_iac_service()
    return await svc.get_cdk_constructs()
