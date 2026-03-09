"""
Application startup and shutdown event handlers.
Extracted from server.py — initializes database indexes, external services,
payment/metadata pipelines, and AWS media services.
"""
from pathlib import Path
from config.database import db
from db_optimizer import DatabaseOptimizer

# External service initializers
from content_removal_endpoints import init_removal_service
from aws_organizations_service import initialize_service as init_org_service
from aws_enterprise_mapping_service import initialize_enterprise_mapping
from agency_success_automation_service import initialize_automation_service
from dao_governance_v2_service import initialize_dao_v2_service
from creative_studio_service import initialize_creative_studio_service
from creative_studio_collab_service import initialize_collab_service
from creative_studio_ai_service import initialize_ai_assets_service
from usage_analytics_service import initialize_analytics_tracking
from aws_cloudwatch_service import initialize_cloudwatch_service
from macie_service import initialize_macie_service
from guardduty_service import initialize_guardduty_service
from qldb_service import initialize_qldb_service


async def startup_event():
    """Initialize database indexes, external services, and security modules."""
    # Create uploads directory
    Path("/app/uploads").mkdir(exist_ok=True)

    print("Creating database indexes...")
    await DatabaseOptimizer.ensure_indexes(db)

    # Initialize external services
    init_fns = [
        ("AWS Enterprise Mapping", lambda: initialize_enterprise_mapping(db)),
        ("Agency Success Automation", lambda: initialize_automation_service(db)),
        ("DAO Governance V2", lambda: initialize_dao_v2_service(db)),
        ("Creative Studio", lambda: initialize_creative_studio_service(db)),
        ("Collaboration & AI Assets", lambda: (initialize_collab_service(db), initialize_ai_assets_service(db))),
        ("Usage Analytics", lambda: initialize_analytics_tracking(db)),
        ("Macie PII Detection", lambda: initialize_macie_service(db)),
        ("GuardDuty Threat Detection", lambda: initialize_guardduty_service(db)),
        ("QLDB Dispute Ledger", lambda: initialize_qldb_service(db)),
        ("CloudWatch Monitoring", lambda: initialize_cloudwatch_service()),
    ]

    for name, fn in init_fns:
        try:
            fn()
            print(f"  {name} initialized")
        except Exception as e:
            print(f"  {name} failed: {str(e)}")

    print("Cache service initialized")
    print("Performance monitoring active")

    # CVE & Security Services
    cve_services = [
        ("CVE Monitor", lambda: __import__('security_audit_service').get_security_audit_service()),
        ("CVE Management", lambda: __import__('cve_management_service').initialize_cve_management(db)),
        ("Scanner Service", lambda: __import__('scanner_service').initialize_scanner_service(db)),
        ("Remediation Service", lambda: __import__('remediation_service').initialize_remediation_service(db)),
        ("Governance Service", lambda: __import__('governance_service').initialize_governance_service(db)),
        ("Notification Service", lambda: __import__('notification_service').initialize_notification_service(db)),
        ("RBAC Service", lambda: __import__('rbac_service').initialize_rbac_service(db)),
        ("SLA Tracker", lambda: __import__('sla_tracker_service').initialize_sla_tracker_service(db)),
        ("CVE Reporting", lambda: __import__('cve_reporting_service').initialize_cve_reporting_service(db)),
        ("Infrastructure Automation", lambda: __import__('iac_service').initialize_iac_service(db)),
        ("Ticketing Integration", lambda: __import__('ticketing_service').initialize_ticketing_service(db)),
        ("Multi-Tenant", lambda: __import__('tenant_service').initialize_tenant_service(db)),
    ]

    for name, fn in cve_services:
        try:
            fn()
            print(f"  {name} initialized")
        except Exception as e:
            print(f"  {name} failed: {str(e)}")

    # Initialize content removal and AWS organizations services
    init_removal_service(db)
    init_org_service(db)

    # Initialize Payment Service
    try:
        import payment_endpoints
        from payment_service import PaymentService
        payment_service_instance = PaymentService(db)
        payment_endpoints.payment_service = payment_service_instance
    except Exception:
        pass

    # Initialize Metadata, Batch, Reporting, Rights, Contracts, Audit Services
    try:
        import metadata_endpoints
        import batch_endpoints
        import reporting_endpoints
        import rights_endpoints
        import smart_contract_endpoints
        import audit_endpoints
        services_dict = {}
        metadata_endpoints.init_metadata_services(db, services_dict)
        batch_endpoints.init_batch_service(db, services_dict)
        reporting_endpoints.init_reporting_service(db, services_dict)
        rights_endpoints.init_rights_service(db, services_dict)
        smart_contract_endpoints.init_contract_service(db, services_dict)
        audit_endpoints.init_audit_service(db, services_dict)
    except Exception:
        pass

    # Initialize GS1 service
    try:
        from gs1_endpoints import init_gs1_service
        init_gs1_service(db)
    except Exception:
        pass

    # Initialize Phase 2 AWS services
    from services.aws_media_svc import CloudFrontService, LambdaProcessingService, RekognitionService
    CloudFrontService()
    LambdaProcessingService()
    RekognitionService()


async def shutdown_event():
    """Cleanup on application shutdown."""
    pass
