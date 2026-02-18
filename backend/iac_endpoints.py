"""
Infrastructure Automation API Endpoints
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional

from iac_service import get_iac_service

router = APIRouter(prefix="/cve/iac", tags=["Infrastructure Automation"])


class DeploymentRecord(BaseModel):
    environment: str
    component: str = "lambda"
    version: str = ""
    status: str = "success"
    deployed_by: str = "manual"
    notes: str = ""


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
