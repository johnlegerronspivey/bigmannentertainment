from fastapi import APIRouter

# Router Imports
from backend.content_removal_endpoints import router as content_removal_router
from backend.workflow_integration_endpoints_simple import router as workflow_integration_router
from backend.support_endpoints import router as support_router
from backend.uln_endpoints import uln_router
from backend.uln_blockchain_endpoints import router as blockchain_router
from backend.ethereum_endpoints import router as ethereum_router
from backend.ethereum_advanced_endpoints import router as ethereum_advanced_router
from backend.profile_endpoints import router as profile_router
from backend.social_oauth_service import router as oauth_router
from backend.social_integration_endpoints import router as social_integration_router
from backend.aws_organizations_endpoints import router as aws_organizations_router
from backend.enterprise_phase1_endpoints import router as enterprise_phase1_router
from backend.digital_twin_endpoints import router as digital_twin_router
from backend.royalty_marketplace_endpoints import router as royalty_marketplace_router
from backend.aws_enterprise_mapping_endpoints import router as aws_enterprise_mapping_router
from backend.agency_success_automation_endpoints import router as agency_automation_router
from backend.dao_governance_v2_endpoints import router as dao_v2_router
from backend.creative_studio_endpoints import router as creative_studio_router
from backend.macie_endpoints import router as macie_router
from backend.guardduty_endpoints import router as guardduty_router
from backend.qldb_endpoints import router as qldb_router
from backend.agency_onboarding_endpoints import agency_router
from backend.social_media_strategy_endpoints import router as social_strategy_router
from backend.social_media_phases_5_10_endpoints import router as social_phases_5_10_router
from backend.royalty_engine_endpoints import router as royalty_engine_router
from backend.social_media_royalty_endpoints import router as social_media_royalty_router
from backend.content_ingestion_endpoints import router as content_ingestion_router
from backend.comprehensive_platform_endpoints import router as comprehensive_platform_router
from backend.content_workflow_endpoints import router as content_workflow_router
from backend.transcoding_endpoints import router as transcoding_router
from backend.distribution_endpoints import router as distribution_router
from backend.premium_features_endpoints import router as premium_router
from backend.mlc_endpoints import router as mlc_router
from backend.mde_endpoints import router as mde_router
from backend.gs1_endpoints import router as gs1_router
from backend.analytics_endpoints import router as analytics_router
from backend.lifecycle_endpoints import router as lifecycle_router
from backend.enhanced_features_endpoints import router as enhanced_features_router
from backend.agency_aws_endpoints import router as agency_aws_router
from backend.snapchat_endpoints import router as snapchat_router
from backend.ddex_endpoints import ddex_router
from backend.music_reports_endpoints import music_reports_router
from backend.workflow_enhancement_endpoints import workflow_router
from backend.sponsorship_endpoints import sponsorship_router
from backend.tax_endpoints import tax_router
from backend.industry_endpoints import industry_router
from backend.label_endpoints import label_router
from backend.stripe_endpoints import stripe_router
from backend.licensing_endpoints import licensing_router
from backend.comprehensive_licensing_endpoints import comprehensive_licensing_router
from backend.pdooh_endpoints import router as pdooh_router
from backend.metadata_endpoints import router as metadata_router
from backend.batch_endpoints import router as batch_router
from backend.reporting_endpoints import router as reporting_router
from backend.rights_endpoints import router as rights_router
from backend.smart_contract_endpoints import router as contracts_router
from backend.audit_endpoints import router as audit_router
from backend.media_upload_endpoints import media_router
from backend.paypal_endpoints import paypal_router

# Main API Router
api_router = APIRouter(prefix="/api")

# Include Routers
routers = [
    content_removal_router, workflow_integration_router, support_router, uln_router,
    blockchain_router, ethereum_router, ethereum_advanced_router, profile_router,
    oauth_router, social_integration_router, aws_organizations_router, enterprise_phase1_router,
    digital_twin_router, royalty_marketplace_router, aws_enterprise_mapping_router,
    agency_automation_router, dao_v2_router, creative_studio_router, macie_router,
    guardduty_router, qldb_router, agency_router, social_strategy_router, social_phases_5_10_router,
    royalty_engine_router, social_media_royalty_router, content_ingestion_router,
    comprehensive_platform_router, content_workflow_router, transcoding_router, distribution_router,
    premium_router, mlc_router, mde_router, gs1_router, analytics_router, lifecycle_router,
    enhanced_features_router, agency_aws_router, snapchat_router, ddex_router, music_reports_router,
    workflow_router, sponsorship_router, tax_router, industry_router, label_router,
    stripe_router, licensing_router, comprehensive_licensing_router, pdooh_router,
    metadata_router, batch_router, reporting_router, rights_router, contracts_router,
    audit_router, media_router, paypal_router
]

for router in routers:
    api_router.include_router(router)
