"""
Phase 1 Enterprise API Endpoints
================================
Combined endpoints for:
- Unified Talent Intelligence Engine
- Executive Insights Dashboard
- Zero-Trust Licensing & Compliance Layer
- Modular Agency Workspaces
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

# Import the four Phase 1 engines
from talent_intelligence_engine import (
    TalentIntelligenceEngine, get_talent_intelligence_engine,
    TalentScore, AssetAnalysis, MarketTrend, AgencyPerformanceInsight, PricingRecommendation
)
from executive_insights_dashboard import (
    ExecutiveInsightsDashboard, get_executive_dashboard,
    TimeRange, ExecutiveSummary, RevenueProjection, AgencyRanking,
    ModelSuccessMetric, LicensingHeatmapData, FraudRiskIndicator, InfrastructureCostInsight
)
from zero_trust_compliance_engine import (
    ZeroTrustComplianceEngine, get_compliance_engine,
    ReleaseVerification, IdentityVerification, UsageRightsValidation,
    FraudDetectionResult, PrivacyComplianceCheck, LicenseExpiryNotification, AuditLogEntry,
    ComplianceStatus, VerificationStatus, PrivacyRegulation
)
from modular_agency_workspace import (
    ModularAgencyWorkspaceService, get_workspace_service,
    AgencyWorkspace, AgencyBranding, CustomDashboard, TalentPipeline,
    TalentPipelineEntry, InternalNote, ContractTemplate, CastingSuggestion,
    PipelineStage, NoteVisibility, TemplateType
)

router = APIRouter(prefix="/enterprise", tags=["Enterprise Phase 1"])


# Database dependency
async def get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    return client[os.environ.get("DB_NAME", "bigmann_entertainment_production")]


# ============================================
# TALENT INTELLIGENCE ENGINE ENDPOINTS
# ============================================

@router.post("/talent/analyze-score/{model_id}", response_model=TalentScore)
async def analyze_talent_score(
    model_id: str,
    model_data: Dict[str, Any] = Body(...),
    db=Depends(get_db)
):
    """Analyze a model's talent score with AI predictions."""
    engine = get_talent_intelligence_engine(db)
    return await engine.analyze_talent_score(model_id, model_data)


@router.post("/talent/analyze-asset/{asset_id}", response_model=AssetAnalysis)
async def analyze_asset_commercial_value(
    asset_id: str,
    asset_data: Dict[str, Any] = Body(...),
    db=Depends(get_db)
):
    """Analyze an asset's commercial value and get recommendations."""
    engine = get_talent_intelligence_engine(db)
    return await engine.analyze_asset_commercial_value(asset_id, asset_data)


@router.get("/talent/market-trends", response_model=List[MarketTrend])
async def get_market_trends(
    category: str = Query(default="modeling"),
    db=Depends(get_db)
):
    """Get AI-predicted market trends for a category."""
    engine = get_talent_intelligence_engine(db)
    return await engine.predict_market_trends(category)


@router.post("/talent/agency-performance/{agency_id}", response_model=AgencyPerformanceInsight)
async def analyze_agency_performance(
    agency_id: str,
    agency_data: Dict[str, Any] = Body(...),
    db=Depends(get_db)
):
    """Analyze agency performance with AI recommendations."""
    engine = get_talent_intelligence_engine(db)
    return await engine.analyze_agency_performance(agency_id, agency_data)


@router.post("/talent/pricing-recommendations", response_model=List[PricingRecommendation])
async def get_pricing_recommendations(
    assets: List[Dict[str, Any]] = Body(...),
    db=Depends(get_db)
):
    """Get dynamic pricing recommendations for assets."""
    engine = get_talent_intelligence_engine(db)
    return await engine.get_pricing_recommendations(assets)


@router.get("/talent/underperforming-assets")
async def flag_underperforming_assets(
    threshold: float = Query(default=30.0),
    db=Depends(get_db)
):
    """Flag underperforming assets with improvement suggestions."""
    engine = get_talent_intelligence_engine(db)
    return await engine.flag_underperforming_assets(threshold)


@router.post("/talent/auto-tag-assets")
async def batch_auto_tag_assets(
    asset_ids: List[str] = Body(...),
    db=Depends(get_db)
):
    """Auto-tag multiple assets with commercial value tags."""
    engine = get_talent_intelligence_engine(db)
    return await engine.batch_auto_tag_assets(asset_ids)


@router.post("/talent/booking-predictions")
async def get_booking_predictions(
    model_ids: List[str] = Body(...),
    db=Depends(get_db)
):
    """Predict booking likelihood for models."""
    engine = get_talent_intelligence_engine(db)
    return await engine.get_model_booking_predictions(model_ids)


# ============================================
# EXECUTIVE INSIGHTS DASHBOARD ENDPOINTS
# ============================================

@router.get("/executive/summary", response_model=ExecutiveSummary)
async def get_executive_summary(
    time_range: TimeRange = Query(default=TimeRange.MONTH),
    db=Depends(get_db)
):
    """Get comprehensive executive summary with AI insights."""
    dashboard = get_executive_dashboard(db)
    return await dashboard.get_executive_summary(time_range)


@router.get("/executive/revenue-projections", response_model=List[RevenueProjection])
async def get_revenue_projections(
    months_ahead: int = Query(default=3, ge=1, le=12),
    db=Depends(get_db)
):
    """Get AI-powered revenue projections."""
    dashboard = get_executive_dashboard(db)
    return await dashboard.get_revenue_projections(months_ahead)


@router.get("/executive/agency-rankings", response_model=List[AgencyRanking])
async def get_agency_rankings(
    limit: int = Query(default=20, ge=1, le=100),
    db=Depends(get_db)
):
    """Get ranked list of agencies by performance."""
    dashboard = get_executive_dashboard(db)
    return await dashboard.get_agency_rankings(limit)


@router.get("/executive/model-analytics", response_model=List[ModelSuccessMetric])
async def get_model_success_analytics(
    limit: int = Query(default=50, ge=1, le=200),
    db=Depends(get_db)
):
    """Get model success analytics with detailed metrics."""
    dashboard = get_executive_dashboard(db)
    return await dashboard.get_model_success_analytics(limit)


@router.get("/executive/licensing-heatmap", response_model=List[LicensingHeatmapData])
async def get_licensing_heatmap(db=Depends(get_db)):
    """Get licensing activity heatmap data."""
    dashboard = get_executive_dashboard(db)
    return await dashboard.get_licensing_heatmap()


@router.get("/executive/fraud-risks", response_model=List[FraudRiskIndicator])
async def detect_fraud_risks(db=Depends(get_db)):
    """Detect potential fraud risks with AI analysis."""
    dashboard = get_executive_dashboard(db)
    return await dashboard.detect_fraud_risks()


@router.get("/executive/infrastructure-costs", response_model=List[InfrastructureCostInsight])
async def get_infrastructure_cost_insights(db=Depends(get_db)):
    """Get infrastructure cost optimization insights."""
    dashboard = get_executive_dashboard(db)
    return await dashboard.get_infrastructure_cost_insights()


# ============================================
# ZERO-TRUST COMPLIANCE ENGINE ENDPOINTS
# ============================================

@router.post("/compliance/verify-release/{release_id}", response_model=ReleaseVerification)
async def verify_release(
    release_id: str,
    release_data: Dict[str, Any] = Body(...),
    actor_id: str = Query(...),
    db=Depends(get_db)
):
    """Verify all necessary releases and consents for an asset."""
    engine = get_compliance_engine(db)
    return await engine.verify_release(release_id, release_data, actor_id)


@router.post("/compliance/verify-identity/{user_id}", response_model=IdentityVerification)
async def verify_identity(
    user_id: str,
    identity_data: Dict[str, Any] = Body(...),
    actor_id: str = Query(...),
    db=Depends(get_db)
):
    """Verify user identity with age validation."""
    engine = get_compliance_engine(db)
    return await engine.verify_identity(user_id, identity_data, actor_id)


@router.post("/compliance/validate-usage-rights/{asset_id}", response_model=UsageRightsValidation)
async def validate_usage_rights(
    asset_id: str,
    requested_use: Dict[str, Any] = Body(...),
    actor_id: str = Query(...),
    db=Depends(get_db)
):
    """Validate if requested usage is allowed for an asset."""
    engine = get_compliance_engine(db)
    return await engine.validate_usage_rights(asset_id, requested_use, actor_id)


@router.post("/compliance/detect-fraud/{upload_id}", response_model=FraudDetectionResult)
async def detect_fraudulent_upload(
    upload_id: str,
    upload_data: Dict[str, Any] = Body(...),
    actor_id: str = Query(...),
    db=Depends(get_db)
):
    """Detect potentially fraudulent uploads."""
    engine = get_compliance_engine(db)
    return await engine.detect_fraudulent_upload(upload_id, upload_data, actor_id)


@router.post("/compliance/check-privacy/{entity_id}", response_model=PrivacyComplianceCheck)
async def check_privacy_compliance(
    entity_id: str,
    entity_type: str = Query(...),
    entity_data: Dict[str, Any] = Body(...),
    regions: List[str] = Query(...),
    actor_id: str = Query(...),
    db=Depends(get_db)
):
    """Check compliance with regional privacy regulations."""
    engine = get_compliance_engine(db)
    return await engine.check_privacy_compliance(entity_id, entity_type, entity_data, regions, actor_id)


@router.get("/compliance/expiring-licenses", response_model=List[LicenseExpiryNotification])
async def check_expiring_licenses(
    days_ahead: int = Query(default=30, ge=1, le=90),
    db=Depends(get_db)
):
    """Check for licenses expiring soon."""
    engine = get_compliance_engine(db)
    return await engine.check_expiring_licenses(days_ahead)


@router.post("/compliance/auto-expire-licenses")
async def auto_expire_licenses(db=Depends(get_db)):
    """Automatically expire past-due licenses."""
    engine = get_compliance_engine(db)
    return await engine.auto_expire_licenses()


@router.get("/compliance/audit-trail", response_model=List[AuditLogEntry])
async def get_audit_trail(
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[str] = Query(default=None),
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    compliance_only: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    db=Depends(get_db)
):
    """Retrieve audit trail with optional filters."""
    engine = get_compliance_engine(db)
    return await engine.get_audit_trail(entity_type, entity_id, start_date, end_date, compliance_only, limit)


@router.get("/compliance/verify-audit-chain")
async def verify_audit_chain_integrity(db=Depends(get_db)):
    """Verify the integrity of the audit log chain."""
    engine = get_compliance_engine(db)
    return await engine.verify_audit_chain_integrity()


# ============================================
# MODULAR AGENCY WORKSPACE ENDPOINTS
# ============================================

@router.post("/workspace/create/{agency_id}", response_model=AgencyWorkspace)
async def create_workspace(
    agency_id: str,
    agency_name: str = Query(...),
    branding: Optional[Dict[str, Any]] = Body(default=None),
    db=Depends(get_db)
):
    """Create a new agency workspace."""
    service = get_workspace_service(db)
    return await service.create_workspace(agency_id, agency_name, branding)


@router.get("/workspace/{agency_id}", response_model=AgencyWorkspace)
async def get_workspace(agency_id: str, db=Depends(get_db)):
    """Get an agency's workspace."""
    service = get_workspace_service(db)
    workspace = await service.get_workspace(agency_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.patch("/workspace/{agency_id}/branding", response_model=AgencyBranding)
async def update_branding(
    agency_id: str,
    branding_updates: Dict[str, Any] = Body(...),
    db=Depends(get_db)
):
    """Update agency branding."""
    service = get_workspace_service(db)
    return await service.update_branding(agency_id, branding_updates)


@router.post("/workspace/{agency_id}/dashboard", response_model=CustomDashboard)
async def create_dashboard(
    agency_id: str,
    name: str = Query(...),
    description: str = Query(default=""),
    widgets: Optional[List[Dict]] = Body(default=None),
    db=Depends(get_db)
):
    """Create a custom dashboard."""
    service = get_workspace_service(db)
    return await service.create_dashboard(agency_id, name, description, widgets)


@router.post("/workspace/{agency_id}/pipeline/{pipeline_id}/talent", response_model=TalentPipelineEntry)
async def add_talent_to_pipeline(
    agency_id: str,
    pipeline_id: str,
    talent_data: Dict[str, Any] = Body(...),
    db=Depends(get_db)
):
    """Add a talent to a pipeline."""
    service = get_workspace_service(db)
    return await service.add_talent_to_pipeline(agency_id, pipeline_id, talent_data)


@router.patch("/workspace/{agency_id}/pipeline/{pipeline_id}/talent/{entry_id}/stage")
async def move_talent_stage(
    agency_id: str,
    pipeline_id: str,
    entry_id: str,
    new_stage: PipelineStage = Query(...),
    db=Depends(get_db)
):
    """Move a talent to a different pipeline stage."""
    service = get_workspace_service(db)
    success = await service.move_talent_stage(agency_id, pipeline_id, entry_id, new_stage)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"success": True, "new_stage": new_stage.value}


@router.post("/workspace/{agency_id}/notes", response_model=InternalNote)
async def add_note(
    agency_id: str,
    entity_type: str = Query(...),
    entity_id: str = Query(...),
    author_id: str = Query(...),
    author_name: str = Query(...),
    content: str = Body(..., embed=True),
    visibility: NoteVisibility = Query(default=NoteVisibility.TEAM),
    tags: Optional[List[str]] = Query(default=None),
    db=Depends(get_db)
):
    """Add an internal note."""
    service = get_workspace_service(db)
    return await service.add_note(agency_id, entity_type, entity_id, author_id, author_name, content, visibility, tags)


@router.get("/workspace/{agency_id}/notes", response_model=List[InternalNote])
async def get_notes(
    agency_id: str,
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db=Depends(get_db)
):
    """Get notes for an agency."""
    service = get_workspace_service(db)
    return await service.get_notes(agency_id, entity_type, entity_id, limit)


@router.post("/workspace/{agency_id}/template", response_model=ContractTemplate)
async def create_contract_template(
    agency_id: str,
    template_type: TemplateType = Query(...),
    name: str = Query(...),
    content: str = Body(..., embed=True),
    description: str = Query(default=""),
    variables: Optional[List[str]] = Query(default=None),
    db=Depends(get_db)
):
    """Create a custom contract template."""
    service = get_workspace_service(db)
    return await service.create_contract_template(agency_id, template_type, name, content, description, variables)


@router.post("/workspace/{agency_id}/template/{template_id}/generate")
async def generate_contract_from_template(
    agency_id: str,
    template_id: str,
    variables: Dict[str, str] = Body(...),
    db=Depends(get_db)
):
    """Generate a contract from a template."""
    service = get_workspace_service(db)
    content = await service.generate_contract_from_template(agency_id, template_id, variables)
    if not content:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"content": content}


@router.post("/workspace/{agency_id}/casting-suggestions", response_model=CastingSuggestion)
async def generate_casting_suggestions(
    agency_id: str,
    campaign_requirements: Dict[str, Any] = Body(...),
    db=Depends(get_db)
):
    """Generate AI-powered casting suggestions."""
    service = get_workspace_service(db)
    return await service.generate_casting_suggestions(agency_id, campaign_requirements)


@router.get("/workspace/{agency_id}/ai-insights")
async def get_workspace_ai_insights(agency_id: str, db=Depends(get_db)):
    """Get AI-generated insights for the agency."""
    service = get_workspace_service(db)
    return await service.get_ai_insights(agency_id)


@router.get("/workspace/{agency_id}/widget/{widget_type}")
async def get_widget_data(agency_id: str, widget_type: str, db=Depends(get_db)):
    """Get data for a specific dashboard widget."""
    service = get_workspace_service(db)
    return await service.get_widget_data(agency_id, widget_type)
