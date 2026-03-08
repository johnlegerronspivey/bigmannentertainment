from fastapi import APIRouter

# Router Imports
from content_removal_endpoints import router as content_removal_router
from workflow_integration_endpoints_simple import router as workflow_integration_router
from support_endpoints import router as support_router
from uln_endpoints import uln_router
from uln_blockchain_endpoints import router as blockchain_router
from ethereum_endpoints import router as ethereum_router
from ethereum_advanced_endpoints import router as ethereum_advanced_router
from social_oauth_service import router as oauth_router
from aws_organizations_endpoints import router as aws_organizations_router
from enterprise_phase1_endpoints import router as enterprise_phase1_router
from digital_twin_endpoints import router as digital_twin_router
from royalty_marketplace_endpoints import router as royalty_marketplace_router
from aws_enterprise_mapping_endpoints import router as aws_enterprise_mapping_router
from agency_success_automation_endpoints import router as agency_automation_router
from dao_governance_v2_endpoints import router as dao_v2_router
from creative_studio_endpoints import router as creative_studio_router
from macie_endpoints import router as macie_router
from guardduty_endpoints import router as guardduty_router
from qldb_endpoints import router as qldb_router
# agency_router excluded due to local definition/fallback in server.py
from social_media_strategy_endpoints import router as social_strategy_router
from social_media_phases_5_10_endpoints import router as social_phases_5_10_router
from royalty_engine_endpoints import router as royalty_engine_router
from social_media_royalty_endpoints import router as social_media_royalty_router
from content_ingestion_endpoints import router as content_ingestion_router
from comprehensive_platform_endpoints import router as comprehensive_platform_router
from content_workflow_endpoints import router as content_workflow_router
from transcoding_endpoints import router as transcoding_router
from distribution_endpoints import router as distribution_router
from premium_features_endpoints import router as premium_router
from mlc_endpoints import router as mlc_router
from mde_endpoints import router as mde_router
from gs1_endpoints import router as gs1_router
from analytics_endpoints import router as analytics_router
from lifecycle_endpoints import router as lifecycle_router
from enhanced_features_endpoints import router as enhanced_features_router
from agency_aws_endpoints import router as agency_aws_router
from snapchat_endpoints import router as snapchat_router
from ddex_endpoints import ddex_router
from music_reports_endpoints import music_reports_router
from workflow_enhancement_endpoints import workflow_router
from sponsorship_endpoints import sponsorship_router
from tax_endpoints import tax_router
from industry_endpoints import industry_router
from label_endpoints import label_router
from stripe_endpoints import stripe_router
from licensing_endpoints import licensing_router
from comprehensive_licensing_endpoints import comprehensive_licensing_router
from pdooh_endpoints import router as pdooh_router
from metadata_endpoints import router as metadata_router
from batch_endpoints import router as batch_router
from reporting_endpoints import router as reporting_router
from rights_endpoints import router as rights_router
from smart_contract_endpoints import router as contracts_router
from audit_endpoints import router as audit_router
from media_upload_endpoints import media_router
from paypal_endpoints import paypal_router
from moderation_endpoints import router as moderation_router
from creative_studio_collab_endpoints import router as collab_router, ai_router as ai_assets_router
from usage_analytics_endpoints import router as usage_analytics_router
from aws_cloudwatch_endpoints import router as cloudwatch_router
from security_audit_endpoints import router as security_audit_router
from cve_management_endpoints import router as cve_management_router
from scanner_endpoints import router as scanner_router
from remediation_endpoints import router as remediation_router
from governance_endpoints import router as governance_router
from notification_endpoints import router as notification_router, reports_router
from rbac_endpoints import router as rbac_router
from sla_tracker_endpoints import router as sla_tracker_router
from cve_reporting_endpoints import router as cve_reporting_router
from iac_endpoints import router as iac_router
from ticketing_endpoints import router as ticketing_router
from tenant_endpoints import router as tenant_router

# Main API Router
api_router = APIRouter(prefix="/api")

# Include Routers
routers = [
    content_removal_router, workflow_integration_router, support_router, uln_router,
    blockchain_router, ethereum_router, ethereum_advanced_router,
    oauth_router, aws_organizations_router, enterprise_phase1_router,
    digital_twin_router, royalty_marketplace_router, aws_enterprise_mapping_router,
    agency_automation_router, dao_v2_router, creative_studio_router, macie_router,
    guardduty_router, qldb_router, # agency_router excluded
    social_strategy_router, social_phases_5_10_router,
    royalty_engine_router, social_media_royalty_router, content_ingestion_router,
    comprehensive_platform_router, content_workflow_router, transcoding_router, distribution_router,
    premium_router, mlc_router, mde_router, gs1_router, analytics_router, lifecycle_router,
    enhanced_features_router, agency_aws_router, snapchat_router, ddex_router, music_reports_router,
    workflow_router, sponsorship_router, tax_router, industry_router, label_router,
    stripe_router, licensing_router, comprehensive_licensing_router, pdooh_router,
    metadata_router, batch_router, reporting_router, rights_router, contracts_router,
    audit_router, media_router, paypal_router, moderation_router,
    collab_router, ai_assets_router,
    usage_analytics_router,
    cloudwatch_router,
    security_audit_router,
    cve_management_router,
    scanner_router,
    remediation_router,
    governance_router,
    notification_router,
    reports_router,
    rbac_router,
    sla_tracker_router,
    cve_reporting_router,
    iac_router,
    ticketing_router,
    tenant_router
]

for router in routers:
    api_router.include_router(router)
