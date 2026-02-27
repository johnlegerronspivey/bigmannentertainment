"""
CVE Management API Endpoints - Phase 1: CVE Brain & Core Dashboard
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from cve_management_service import get_cve_management_service
from tenant_context import get_optional_tenant_id

router = APIRouter(prefix="/cve", tags=["CVE Management"])


# ─── Request Models ────────────────────────────────────────────

class CVECreate(BaseModel):
    cve_id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    severity: str = "medium"
    cvss_score: Optional[float] = 0.0
    affected_package: str = ""
    affected_version: str = ""
    fixed_version: str = ""
    affected_services: List[str] = []
    assigned_to: str = ""
    assigned_team: str = ""
    source: str = "manual"
    references: List[str] = []
    exploitability: str = "unknown"
    tags: List[str] = []


class CVEStatusUpdate(BaseModel):
    status: str
    notes: str = ""


class CVEUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    cvss_score: Optional[float] = None
    affected_package: Optional[str] = None
    affected_version: Optional[str] = None
    fixed_version: Optional[str] = None
    affected_services: Optional[List[str]] = None
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    exploitability: Optional[str] = None
    tags: Optional[List[str]] = None


class ServiceCreate(BaseModel):
    name: str
    description: str = ""
    repo_url: str = ""
    owner: str = ""
    team: str = ""
    environment: str = "production"
    criticality: str = "medium"
    tech_stack: List[str] = []
    tags: List[str] = []


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    repo_url: Optional[str] = None
    owner: Optional[str] = None
    team: Optional[str] = None
    environment: Optional[str] = None
    criticality: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class OwnerAssign(BaseModel):
    assigned_to: str = ""
    assigned_team: str = ""
    notes: str = ""


class BulkOwnerAssign(BaseModel):
    cve_ids: List[str]
    assigned_to: str = ""
    assigned_team: str = ""
    notes: str = ""


class SeverityPoliciesUpdate(BaseModel):
    policies: Dict[str, Any]


# ─── Health ────────────────────────────────────────────────────

@router.get("/health")
async def cve_health():
    return {"status": "healthy", "service": "CVE Management Platform"}


# ─── Dashboard ─────────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard(tenant_id: Optional[str] = Depends(get_optional_tenant_id)):
    service = get_cve_management_service()
    return await service.get_dashboard(tenant_id=tenant_id)


# ─── CVE Entries ───────────────────────────────────────────────

@router.get("/entries")
async def list_cves(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    tenant_id: Optional[str] = Depends(get_optional_tenant_id),
):
    svc = get_cve_management_service()
    return await svc.list_cves(status=status, severity=severity, service=service, search=search, limit=limit, skip=skip, tenant_id=tenant_id)


@router.post("/entries")
async def create_cve(body: CVECreate, tenant_id: Optional[str] = Depends(get_optional_tenant_id)):
    svc = get_cve_management_service()
    return await svc.create_cve(body.dict(), tenant_id=tenant_id)


@router.get("/entries/{cve_entry_id}")
async def get_cve(cve_entry_id: str):
    svc = get_cve_management_service()
    result = await svc.get_cve(cve_entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="CVE not found")
    return result


@router.put("/entries/{cve_entry_id}")
async def update_cve(cve_entry_id: str, body: CVEUpdate):
    svc = get_cve_management_service()
    result = await svc.update_cve(cve_entry_id, body.dict(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="CVE not found")
    return result


@router.put("/entries/{cve_entry_id}/status")
async def update_cve_status(cve_entry_id: str, body: CVEStatusUpdate):
    svc = get_cve_management_service()
    result = await svc.update_cve_status(cve_entry_id, body.status, body.notes)
    if not result:
        raise HTTPException(status_code=404, detail="CVE not found or invalid status")
    return result


# ─── Ownership ─────────────────────────────────────────────────

@router.put("/entries/{cve_entry_id}/owner")
async def assign_owner(cve_entry_id: str, body: OwnerAssign):
    svc = get_cve_management_service()
    result = await svc.assign_owner(cve_entry_id, body.assigned_to, body.assigned_team, body.notes)
    if not result:
        raise HTTPException(status_code=404, detail="CVE not found")
    return result


@router.post("/entries/bulk-assign")
async def bulk_assign_owner(body: BulkOwnerAssign):
    svc = get_cve_management_service()
    return await svc.bulk_assign_owner(body.cve_ids, body.assigned_to, body.assigned_team, body.notes)


@router.get("/owners")
async def get_available_owners():
    svc = get_cve_management_service()
    return await svc.get_available_owners()


@router.get("/unassigned")
async def get_unassigned_cves(severity: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=200)):
    svc = get_cve_management_service()
    return await svc.get_unassigned_cves(severity=severity, limit=limit)


# ─── Services ──────────────────────────────────────────────────

@router.get("/services")
async def list_services():
    svc = get_cve_management_service()
    return await svc.list_services()


@router.post("/services")
async def create_service(body: ServiceCreate):
    svc = get_cve_management_service()
    return await svc.create_service(body.dict())


@router.get("/services/{service_id}")
async def get_service(service_id: str):
    svc = get_cve_management_service()
    result = await svc.get_service(service_id)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.put("/services/{service_id}")
async def update_service(service_id: str, body: ServiceUpdate):
    svc = get_cve_management_service()
    result = await svc.update_service(service_id, body.dict(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.delete("/services/{service_id}")
async def delete_service(service_id: str):
    svc = get_cve_management_service()
    ok = await svc.delete_service(service_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"deleted": True}


# ─── SBOM ──────────────────────────────────────────────────────

@router.post("/sbom/generate")
async def generate_sbom(service_name: str = Query("bigmann-platform"), environment: str = Query("production")):
    svc = get_cve_management_service()
    return await svc.generate_sbom(service_name, environment)


@router.get("/sbom/list")
async def list_sboms(limit: int = Query(20, ge=1, le=100)):
    svc = get_cve_management_service()
    return await svc.list_sboms(limit=limit)


@router.get("/sbom/{sbom_id}")
async def get_sbom(sbom_id: str):
    svc = get_cve_management_service()
    result = await svc.get_sbom(sbom_id)
    if not result:
        raise HTTPException(status_code=404, detail="SBOM not found")
    return result


# ─── Severity Policies ────────────────────────────────────────

@router.get("/policies")
async def get_policies():
    svc = get_cve_management_service()
    return await svc.get_severity_policies()


@router.put("/policies")
async def update_policies(body: SeverityPoliciesUpdate):
    svc = get_cve_management_service()
    return await svc.update_severity_policies(body.policies)


# ─── Comprehensive Scan ───────────────────────────────────────

@router.post("/scan")
async def run_scan():
    svc = get_cve_management_service()
    return await svc.run_comprehensive_scan()


# ─── Audit Trail ──────────────────────────────────────────────

@router.get("/audit-trail")
async def get_audit_trail(
    target_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
):
    svc = get_cve_management_service()
    return await svc.get_audit_trail(target_id=target_id, action=action, limit=limit, skip=skip)


# ─── Seed Data ─────────────────────────────────────────────────

@router.post("/seed")
async def seed_data():
    svc = get_cve_management_service()
    return await svc.seed_sample_data()
