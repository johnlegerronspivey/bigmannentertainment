"""
Application startup and shutdown event handlers.
Extracted from server.py — initializes database indexes, external services,
payment/metadata pipelines, and AWS media services.
"""
from pathlib import Path
from datetime import datetime, timezone
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

    # Start post scheduler background task
    try:
        from services.scheduler_service import start_scheduler
        start_scheduler()
        print("  Post Scheduler started")
    except Exception as e:
        print(f"  Post Scheduler failed: {str(e)}")

    # ── OWNERSHIP PROTECTION: Enforce immutable owner fields on every startup ──
    try:
        from utils.ownership_guard import (
            PROTECTED_OWNER_USER_ID,
            PROTECTED_OWNER_EMAIL,
            PROTECTED_OWNER_FULL_NAME,
            PROTECTED_BUSINESS_NAME,
            PROTECTED_OWNER_ROLE,
            PROTECTED_OWNER_IS_ADMIN,
            PROTECTED_OWNER_IS_ACTIVE,
            PROTECTED_OWNER_ACCOUNT_STATUS,
        )
        result = await db.users.update_one(
            {"id": PROTECTED_OWNER_USER_ID},
            {"$set": {
                "email": PROTECTED_OWNER_EMAIL,
                "full_name": PROTECTED_OWNER_FULL_NAME,
                "business_name": PROTECTED_BUSINESS_NAME,
                "role": PROTECTED_OWNER_ROLE,
                "is_admin": PROTECTED_OWNER_IS_ADMIN,
                "is_active": PROTECTED_OWNER_IS_ACTIVE,
                "account_status": PROTECTED_OWNER_ACCOUNT_STATUS,
            }},
        )
        if result.modified_count > 0:
            print("  [OWNERSHIP GUARD] Re-asserted protected owner fields (drift detected and corrected)")
        else:
            print("  [OWNERSHIP GUARD] Protected owner fields verified — no drift")

        # Ensure owner membership on every label
        async for lbl in db.uln_labels.find({"status": "active"}, {"_id": 0, "global_id": 1}):
            lid = lbl.get("global_id", {}).get("id")
            if lid:
                existing = await db.label_members.find_one({"label_id": lid, "user_id": PROTECTED_OWNER_USER_ID})
                if existing and existing.get("role") != "owner":
                    await db.label_members.update_one(
                        {"label_id": lid, "user_id": PROTECTED_OWNER_USER_ID},
                        {"$set": {"role": "owner"}},
                    )
                    print(f"  [OWNERSHIP GUARD] Restored owner role on label {lid}")
    except Exception as e:
        print(f"  [OWNERSHIP GUARD] Startup check failed: {str(e)}")

    # ── OWNERSHIP PROTECTION: Enforce immutable business identifiers on every startup ──
    try:
        from utils.ownership_guard import PROTECTED_BUSINESS_IDENTIFIERS, PROTECTED_GS1_COMPANY_PREFIX

        # Find all labels owned by the protected owner
        owner_labels = await db.label_members.find(
            {"user_id": PROTECTED_OWNER_USER_ID, "role": "owner"}, {"_id": 0, "label_id": 1}
        ).to_list(length=None)

        for lbl_doc in owner_labels:
            lid = lbl_doc.get("label_id")
            if not lid:
                continue
            now = datetime.now(timezone.utc).isoformat()
            ident_doc = {
                **PROTECTED_BUSINESS_IDENTIFIERS,
                "label_id": lid,
                "owner_user_id": PROTECTED_OWNER_USER_ID,
                "updated_at": now,
                "updated_by": "system_startup",
            }
            result = await db.business_identifiers.update_one(
                {"label_id": lid},
                {"$set": ident_doc, "$setOnInsert": {"created_at": now, "created_by": "system_startup"}},
                upsert=True,
            )
            if result.upserted_id:
                print(f"  [OWNERSHIP GUARD] Pre-populated business identifiers for label {lid}")
            elif result.modified_count > 0:
                print(f"  [OWNERSHIP GUARD] Re-asserted business identifiers for label {lid}")

        print(f"  [OWNERSHIP GUARD] Business identifiers enforced for {len(owner_labels)} owned labels")
    except Exception as e:
        print(f"  [OWNERSHIP GUARD] Business identifiers startup check failed: {str(e)}")


async def shutdown_event():
    """Cleanup on application shutdown."""
    pass
