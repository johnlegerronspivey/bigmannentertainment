"""
Scanner API Endpoints - Phase 2: Multi-scanner, CI/CD Pipeline Generator, Policy-as-Code
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from scanner_service import get_scanner_service

router = APIRouter(prefix="/cve/scanners", tags=["Scanners & CI/CD"])


# ─── Request Models ────────────────────────────────────────────

class PolicyRuleCreate(BaseModel):
    name: str
    description: str = ""
    enabled: bool = True
    condition_type: str = "severity_threshold"
    condition: Dict[str, Any] = {}
    action: str = "block_deploy"
    scope: str = "all"


class PolicyRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    condition_type: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    action: Optional[str] = None
    scope: Optional[str] = None


class PipelineConfig(BaseModel):
    repo_name: str = "bigmannentertainment"
    branch: str = "main"
    enable_trivy: bool = True
    enable_grype: bool = True
    enable_checkov: bool = True
    enable_syft: bool = True
    fail_on_critical: bool = True
    fail_on_high: bool = False
    container_image: str = ""
    terraform_dir: str = "terraform/"
    notify_email: str = ""


# ─── Tool Status ───────────────────────────────────────────────

@router.get("/tools")
async def get_tool_status():
    svc = get_scanner_service()
    return await svc.get_tool_status()


# ─── Scanner Endpoints ────────────────────────────────────────

@router.post("/trivy/fs")
async def run_trivy_fs(target: str = Query("/app"), severity: str = Query("CRITICAL,HIGH,MEDIUM,LOW")):
    svc = get_scanner_service()
    return await svc.run_trivy_fs(target=target, severity_filter=severity)


@router.post("/trivy/iac")
async def run_trivy_iac(target: str = Query("/tmp/test_iac")):
    svc = get_scanner_service()
    return await svc.run_trivy_iac(target=target)


@router.post("/grype")
async def run_grype(target: str = Query("dir:/app/backend")):
    svc = get_scanner_service()
    return await svc.run_grype(target=target)


@router.post("/syft")
async def run_syft(target: str = Query("/app")):
    svc = get_scanner_service()
    return await svc.run_syft(target=target)


@router.post("/checkov")
async def run_checkov(target: str = Query("/tmp/test_iac"), framework: str = Query("all")):
    svc = get_scanner_service()
    return await svc.run_checkov(target=target, framework=framework)


# ─── Scan History ──────────────────────────────────────────────

@router.get("/results")
async def list_scan_results(scanner: Optional[str] = Query(None), limit: int = Query(20, ge=1, le=100)):
    svc = get_scanner_service()
    return await svc.list_scan_results(scanner=scanner, limit=limit)


@router.get("/results/{scan_id}")
async def get_scan_result(scan_id: str):
    svc = get_scanner_service()
    result = await svc.get_scan_result(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan result not found")
    return result


# ─── Policy-as-Code Rules ────────────────────────────────────

@router.get("/policy-rules")
async def list_policy_rules():
    svc = get_scanner_service()
    return await svc.list_policy_rules()


@router.post("/policy-rules")
async def create_policy_rule(body: PolicyRuleCreate):
    svc = get_scanner_service()
    return await svc.create_policy_rule(body.dict())


@router.put("/policy-rules/{rule_id}")
async def update_policy_rule(rule_id: str, body: PolicyRuleUpdate):
    svc = get_scanner_service()
    result = await svc.update_policy_rule(rule_id, body.dict(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Policy rule not found")
    return result


@router.delete("/policy-rules/{rule_id}")
async def delete_policy_rule(rule_id: str):
    svc = get_scanner_service()
    ok = await svc.delete_policy_rule(rule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Policy rule not found")
    return {"deleted": True}


@router.post("/policy-rules/evaluate/{scan_id}")
async def evaluate_policies(scan_id: str):
    svc = get_scanner_service()
    scan_result = await svc.get_scan_result(scan_id)
    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan result not found")
    return await svc.evaluate_policies(scan_result)


@router.post("/policy-rules/seed")
async def seed_default_rules():
    svc = get_scanner_service()
    return await svc.seed_default_rules()


# ─── CI/CD Pipeline Generator ────────────────────────────────

@router.post("/pipeline/generate")
async def generate_pipeline(body: PipelineConfig):
    svc = get_scanner_service()
    return await svc.generate_pipeline(body.dict())


@router.get("/pipeline/list")
async def list_pipelines(limit: int = Query(20, ge=1, le=100)):
    svc = get_scanner_service()
    return await svc.list_pipelines(limit=limit)


@router.get("/pipeline/{pipeline_id}")
async def get_pipeline(pipeline_id: str):
    svc = get_scanner_service()
    result = await svc.get_pipeline(pipeline_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline config not found")
    return result
