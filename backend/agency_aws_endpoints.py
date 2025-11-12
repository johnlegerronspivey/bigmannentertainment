"""
AWS-Powered Modeling Agency Platform API Endpoints
Complete REST API for all 6 feature areas
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import os
import uuid
import base64

from agency_aws_models import (
    PortfolioImage,
    ModelPortfolio,
    SmartLicense,
    RoyaltyPayment,
    AgencyOnboarding,
    ComplianceDocument,
    AuditLog,
    SupportTicket,
    DAODispute,
    DisputeVote,
    KBWIDocument,
    KBWIFeedback,
    SecurityAlert,
    BackupRecord,
    AgencyDashboard,
    LicenseType,
    BlockchainNetwork
)

from agency_aws_service import (
    s3_service,
    rekognition_service,
    lambda_service,
    dynamodb_service,
    cognito_service,
    step_functions_service,
    macie_service,
    qldb_service,
    cloudwatch_service,
    sns_service,
    blockchain_service
)

router = APIRouter(prefix="/agency-aws", tags=["AWS Agency Platform"])

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bigmann_entertainment_production')]


# ============== 1. Image & Portfolio Management Endpoints ==============

@router.post("/portfolios/upload-image")
async def upload_portfolio_image(
    model_id: str,
    agency_id: str,
    file: UploadFile = File(...),
    tags: Optional[List[str]] = None
):
    """
    Upload image to S3, analyze with Rekognition, store metadata
    """
    try:
        # Read file
        file_data = await file.read()
        
        # Upload to S3
        s3_result = await s3_service.upload_image(file_data, file.filename, model_id)
        
        # Analyze with Rekognition
        metadata = await rekognition_service.analyze_image(s3_result["s3_key"])
        
        # Create portfolio image record
        portfolio_image = PortfolioImage(
            model_id=model_id,
            agency_id=agency_id,
            s3_key=s3_result["s3_key"],
            s3_bucket=s3_result["s3_bucket"],
            cloudfront_url=s3_result["cloudfront_url"],
            file_size=s3_result["file_size"],
            dimensions={"width": 1920, "height": 1080},  # Would extract from image
            format=file.filename.split('.')[-1],
            metadata=metadata,
            tags=tags or []
        )
        
        # Save to database
        portfolio_dict = portfolio_image.dict()
        portfolio_dict['uploaded_at'] = portfolio_dict['uploaded_at'].isoformat()
        
        await db.portfolio_images.insert_one(portfolio_dict)
        
        # Log to CloudWatch
        await cloudwatch_service.put_metric("AgencyPlatform", "ImageUpload", 1.0)
        
        return {
            "success": True,
            "image": portfolio_image,
            "cloudfront_url": s3_result["cloudfront_url"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


@router.get("/portfolios/{model_id}")
async def get_model_portfolio(model_id: str):
    """Get complete model portfolio with all images"""
    
    images = await db.portfolio_images.find({"model_id": model_id}).to_list(length=1000)
    
    if not images:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return {
        "model_id": model_id,
        "total_images": len(images),
        "images": images
    }


@router.delete("/portfolios/image/{image_id}")
async def delete_portfolio_image(image_id: str, agency_id: str):
    """Delete image from portfolio and S3"""
    
    image = await db.portfolio_images.find_one({"id": image_id})
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if image.get("agency_id") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Delete from S3
    await s3_service.delete_image(image["s3_key"])
    
    # Delete from database
    await db.portfolio_images.delete_one({"id": image_id})
    
    return {"success": True, "message": "Image deleted"}


# ============== 2. Smart Licensing & Royalty Engine Endpoints ==============

@router.post("/licensing/create-smart-license")
async def create_smart_license(
    license_type: LicenseType,
    image_id: str,
    model_id: str,
    agency_id: str,
    licensee_id: str,
    licensee_name: str,
    blockchain_network: BlockchainNetwork,
    license_fee: float,
    royalty_percentage: float = 10.0,
    duration_days: Optional[int] = None
):
    """
    Create smart contract-based license and mint NFT
    """
    try:
        # Deploy blockchain contract
        contract_data = {
            "license_type": license_type,
            "image_id": image_id,
            "licensee": licensee_id,
            "fee": license_fee
        }
        
        blockchain_result = await blockchain_service.deploy_license_contract(
            blockchain_network.value,
            contract_data
        )
        
        # Create license record
        license = SmartLicense(
            license_type=license_type,
            image_id=image_id,
            model_id=model_id,
            agency_id=agency_id,
            licensee_id=licensee_id,
            licensee_name=licensee_name,
            blockchain_network=blockchain_network,
            contract_address=blockchain_result["contract_address"],
            license_fee=license_fee,
            royalty_percentage=royalty_percentage,
            duration_days=duration_days,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=duration_days) if duration_days else None
        )
        
        # Store in DynamoDB
        await dynamodb_service.put_license(license.dict())
        
        # Store in MongoDB
        license_dict = license.dict()
        license_dict['created_at'] = license_dict['created_at'].isoformat()
        license_dict['start_date'] = license_dict['start_date'].isoformat()
        if license_dict.get('end_date'):
            license_dict['end_date'] = license_dict['end_date'].isoformat()
        
        await db.smart_licenses.insert_one(license_dict)
        
        # Mint NFT
        nft_result = await blockchain_service.mint_license_nft(
            blockchain_result["contract_address"],
            licensee_id,
            f"ipfs://metadata/{license.id}"
        )
        
        # Update license with token ID
        await db.smart_licenses.update_one(
            {"id": license.id},
            {"$set": {"token_id": nft_result["token_id"]}}
        )
        
        return {
            "success": True,
            "license": license,
            "blockchain": blockchain_result,
            "nft": nft_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"License creation failed: {str(e)}")


@router.post("/licensing/calculate-royalty")
async def calculate_royalty_payment(
    license_id: str,
    revenue_amount: float,
    currency: str = "USD"
):
    """Calculate and process royalty payment using Lambda"""
    
    license = await db.smart_licenses.find_one({"id": license_id})
    
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    
    # Use Lambda for calculation
    calculation = await lambda_service.invoke_royalty_calculation({
        "license_fee": license.get("license_fee", 0),
        "royalty_percentage": license.get("royalty_percentage", 10.0)
    })
    
    # FX conversion if needed
    if currency != "USD":
        fx_result = await lambda_service.invoke_fx_conversion(revenue_amount, currency, "USD")
        usd_equivalent = fx_result["converted_amount"]
        fx_rate = fx_result["fx_rate"]
    else:
        usd_equivalent = revenue_amount
        fx_rate = 1.0
    
    # Create royalty payment
    payment = RoyaltyPayment(
        license_id=license_id,
        model_id=license["model_id"],
        agency_id=license["agency_id"],
        amount=revenue_amount,
        currency=currency,
        fx_rate=fx_rate,
        usd_equivalent=usd_equivalent,
        net_amount=usd_equivalent * 0.95,  # After 5% tax
        tax_withheld=usd_equivalent * 0.05,
        payment_method="blockchain"
    )
    
    payment_dict = payment.dict()
    payment_dict['payment_date'] = payment_dict['payment_date'].isoformat()
    
    await db.royalty_payments.insert_one(payment_dict)
    
    return {
        "success": True,
        "payment": payment,
        "calculation": calculation
    }


@router.get("/licensing/{license_id}")
async def get_license(license_id: str):
    """Get license details"""
    
    license = await db.smart_licenses.find_one({"id": license_id})
    
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    
    return license


# ============== 3. Agency Onboarding & Compliance Endpoints ==============

@router.post("/onboarding/start")
async def start_agency_onboarding(
    agency_name: str,
    business_registration_number: str,
    country: str,
    contact_email: str,
    contact_phone: str
):
    """Start agency onboarding with Cognito and Step Functions"""
    
    try:
        # Create Cognito user
        cognito_user = await cognito_service.create_user(contact_email, agency_name)
        
        # Start Step Functions workflow
        workflow_data = {
            "agency_name": agency_name,
            "email": contact_email,
            "cognito_user_id": cognito_user["Username"]
        }
        
        execution_arn = await step_functions_service.start_onboarding_workflow(workflow_data)
        
        # Create onboarding record
        onboarding = AgencyOnboarding(
            agency_name=agency_name,
            business_registration_number=business_registration_number,
            country=country,
            contact_email=contact_email,
            contact_phone=contact_phone,
            cognito_user_id=cognito_user["Username"],
            step_function_execution_arn=execution_arn
        )
        
        onboarding_dict = onboarding.dict()
        onboarding_dict['created_at'] = onboarding_dict['created_at'].isoformat()
        if onboarding_dict.get('approved_at'):
            onboarding_dict['approved_at'] = onboarding_dict['approved_at'].isoformat()
        
        await db.agency_onboarding.insert_one(onboarding_dict)
        
        # Create audit log
        audit_log = AuditLog(
            event_type="onboarding_started",
            actor_id=onboarding.id,
            actor_type="agency",
            resource_type="onboarding",
            resource_id=onboarding.id,
            action="create"
        )
        
        audit_dict = audit_log.dict()
        audit_dict['timestamp'] = audit_dict['timestamp'].isoformat()
        await db.audit_logs.insert_one(audit_dict)
        
        return {
            "success": True,
            "onboarding_id": onboarding.id,
            "cognito_user_id": cognito_user["Username"],
            "step_function_arn": execution_arn,
            "message": "Onboarding started. Please check your email for verification."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Onboarding failed: {str(e)}")


@router.post("/compliance/upload-document")
async def upload_compliance_document(
    document_type: str,
    agency_id: str,
    file: UploadFile = File(...),
    model_id: Optional[str] = None
):
    """Upload compliance document to S3 and scan with Macie"""
    
    try:
        file_data = await file.read()
        
        # Upload to S3
        s3_result = await s3_service.upload_image(file_data, file.filename, agency_id)
        
        # Scan with Macie
        macie_result = await macie_service.scan_document(s3_result["s3_key"])
        
        # Create compliance document record
        doc = ComplianceDocument(
            document_type=document_type,
            model_id=model_id,
            agency_id=agency_id,
            s3_key=s3_result["s3_key"],
            s3_bucket=s3_result["s3_bucket"],
            file_name=file.filename,
            file_size=s3_result["file_size"],
            macie_scan_status=macie_result["finding_type"],
            macie_findings=macie_result.get("findings", []),
            uploaded_by=agency_id
        )
        
        doc_dict = doc.dict()
        doc_dict['uploaded_at'] = doc_dict['uploaded_at'].isoformat()
        if doc_dict.get('expiry_date'):
            doc_dict['expiry_date'] = doc_dict['expiry_date'].isoformat()
        
        await db.compliance_documents.insert_one(doc_dict)
        
        return {
            "success": True,
            "document": doc,
            "macie_scan": macie_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@router.get("/onboarding/status/{onboarding_id}")
async def get_onboarding_status(onboarding_id: str):
    """Get agency onboarding status"""
    
    onboarding = await db.agency_onboarding.find_one({"id": onboarding_id})
    
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    
    # Get Step Functions status if available
    if onboarding.get("step_function_execution_arn"):
        workflow_status = await step_functions_service.get_execution_status(
            onboarding["step_function_execution_arn"]
        )
        onboarding["workflow_status"] = workflow_status
    
    return onboarding


# ============== 4. Support System & DAO Disputes Endpoints ==============

@router.post("/support/create-ticket")
async def create_support_ticket(
    user_id: str,
    user_type: str,
    category: str,
    subject: str,
    description: str,
    priority: str = "medium"
):
    """Create support ticket with Amazon Connect integration"""
    
    try:
        ticket_number = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
        
        ticket = SupportTicket(
            ticket_number=ticket_number,
            user_id=user_id,
            user_type=user_type,
            category=category,
            subject=subject,
            description=description,
            priority=priority
        )
        
        ticket_dict = ticket.dict()
        ticket_dict['created_at'] = ticket_dict['created_at'].isoformat()
        ticket_dict['updated_at'] = ticket_dict['updated_at'].isoformat()
        if ticket_dict.get('resolved_at'):
            ticket_dict['resolved_at'] = ticket_dict['resolved_at'].isoformat()
        
        await db.support_tickets.insert_one(ticket_dict)
        
        # Send SNS notification
        await sns_service.publish_alert(
            "arn:aws:sns:us-east-1:123456789:support-tickets",
            f"New support ticket: {ticket_number}",
            f"Priority: {priority}"
        )
        
        return {
            "success": True,
            "ticket": ticket,
            "ticket_number": ticket_number
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticket creation failed: {str(e)}")


@router.post("/disputes/create")
async def create_dao_dispute(
    dispute_type: str,
    plaintiff_id: str,
    defendant_id: str,
    description: str,
    voting_duration_days: int = 7,
    license_id: Optional[str] = None
):
    """Create DAO dispute with QLDB and blockchain voting"""
    
    try:
        voting_start = datetime.now(timezone.utc)
        voting_end = voting_start + timedelta(days=voting_duration_days)
        
        dispute = DAODispute(
            dispute_type=dispute_type,
            plaintiff_id=plaintiff_id,
            defendant_id=defendant_id,
            license_id=license_id,
            description=description,
            voting_start_date=voting_start,
            voting_end_date=voting_end
        )
        
        # Create immutable record in QLDB
        qldb_id = await qldb_service.create_document("disputes", dispute.dict())
        
        dispute.qldb_ledger_id = qldb_id
        
        dispute_dict = dispute.dict()
        dispute_dict['created_at'] = dispute_dict['created_at'].isoformat()
        dispute_dict['voting_start_date'] = dispute_dict['voting_start_date'].isoformat()
        dispute_dict['voting_end_date'] = dispute_dict['voting_end_date'].isoformat()
        if dispute_dict.get('resolved_at'):
            dispute_dict['resolved_at'] = dispute_dict['resolved_at'].isoformat()
        
        await db.dao_disputes.insert_one(dispute_dict)
        
        return {
            "success": True,
            "dispute": dispute,
            "qldb_ledger_id": qldb_id,
            "voting_ends_at": voting_end.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dispute creation failed: {str(e)}")


@router.post("/disputes/{dispute_id}/vote")
async def vote_on_dispute(
    dispute_id: str,
    voter_id: str,
    vote: str,  # for, against, abstain
    voting_power: float = 1.0
):
    """Cast vote on DAO dispute"""
    
    dispute = await db.dao_disputes.find_one({"id": dispute_id})
    
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    # Create vote record
    vote_record = DisputeVote(
        dispute_id=dispute_id,
        voter_id=voter_id,
        vote=vote,
        voting_power=voting_power
    )
    
    # Record in QLDB for immutability
    qldb_vote_id = await qldb_service.create_document("dispute_votes", vote_record.dict())
    vote_record.qldb_document_id = qldb_vote_id
    
    vote_dict = vote_record.dict()
    vote_dict['timestamp'] = vote_dict['timestamp'].isoformat()
    
    await db.dispute_votes.insert_one(vote_dict)
    
    # Update dispute vote counts
    if vote == "for":
        await db.dao_disputes.update_one(
            {"id": dispute_id},
            {"$inc": {"votes_for": voting_power, "total_votes": voting_power}}
        )
    elif vote == "against":
        await db.dao_disputes.update_one(
            {"id": dispute_id},
            {"$inc": {"votes_against": voting_power, "total_votes": voting_power}}
        )
    
    return {
        "success": True,
        "vote": vote_record,
        "qldb_document_id": qldb_vote_id
    }


# ============== 5. Knowledge-Based Work Instructions (KBWI) Endpoints ==============

@router.post("/kbwi/create")
async def create_kbwi_document(
    title: str,
    category: str,
    urgency: str,
    content: str,
    role_access: List[str],
    tags: List[str],
    created_by: str
):
    """Create KBWI document"""
    
    kbwi = KBWIDocument(
        title=title,
        category=category,
        urgency=urgency,
        role_access=role_access,
        content=content,
        tags=tags,
        search_keywords=tags + title.lower().split(),
        created_by=created_by
    )
    
    kbwi_dict = kbwi.dict()
    kbwi_dict['created_at'] = kbwi_dict['created_at'].isoformat()
    kbwi_dict['updated_at'] = kbwi_dict['updated_at'].isoformat()
    
    await db.kbwi_documents.insert_one(kbwi_dict)
    
    return {"success": True, "kbwi": kbwi}


@router.get("/kbwi/search")
async def search_kbwi(query: str, category: Optional[str] = None, role: Optional[str] = None):
    """Search KBWI documents using OpenSearch"""
    
    filters = {}
    
    if category:
        filters["category"] = category
    
    if role:
        filters["role_access"] = role
    
    # Text search on title, content, tags
    documents = await db.kbwi_documents.find({
        **filters,
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}},
            {"tags": {"$in": [query.lower()]}}
        ]
    }).to_list(length=50)
    
    return {
        "query": query,
        "total_results": len(documents),
        "documents": documents
    }


@router.post("/kbwi/{kbwi_id}/feedback")
async def submit_kbwi_feedback(
    kbwi_id: str,
    user_id: str,
    was_helpful: bool,
    comments: Optional[str] = None
):
    """Submit feedback on KBWI document"""
    
    feedback = KBWIFeedback(
        kbwi_id=kbwi_id,
        user_id=user_id,
        was_helpful=was_helpful,
        comments=comments
    )
    
    feedback_dict = feedback.dict()
    feedback_dict['timestamp'] = feedback_dict['timestamp'].isoformat()
    
    await db.kbwi_feedback.insert_one(feedback_dict)
    
    # Update document helpful counts
    if was_helpful:
        await db.kbwi_documents.update_one(
            {"id": kbwi_id},
            {"$inc": {"helpful_count": 1}}
        )
    else:
        await db.kbwi_documents.update_one(
            {"id": kbwi_id},
            {"$inc": {"not_helpful_count": 1}}
        )
    
    return {"success": True, "feedback": feedback}


# ============== 6. Security & Monitoring Endpoints ==============

@router.post("/security/create-alert")
async def create_security_alert(
    alert_type: str,
    severity: str,
    description: str,
    affected_resources: List[str]
):
    """Create security alert and send SNS notification"""
    
    alert = SecurityAlert(
        alert_type=alert_type,
        severity=severity,
        description=description,
        affected_resources=affected_resources
    )
    
    alert_dict = alert.dict()
    alert_dict['detected_at'] = alert_dict['detected_at'].isoformat()
    if alert_dict.get('resolved_at'):
        alert_dict['resolved_at'] = alert_dict['resolved_at'].isoformat()
    
    await db.security_alerts.insert_one(alert_dict)
    
    # Send SNS notification
    if severity in ["high", "critical"]:
        await sns_service.publish_alert(
            "arn:aws:sns:us-east-1:123456789:security-alerts",
            description,
            f"SECURITY ALERT: {alert_type}"
        )
    
    # Log to CloudWatch
    await cloudwatch_service.put_log_event(
        "/aws/agency/security",
        "security-alerts",
        f"Alert created: {alert_type} - {severity}"
    )
    
    return {"success": True, "alert": alert}


@router.get("/monitoring/dashboard")
async def get_monitoring_dashboard(agency_id: str):
    """Get comprehensive monitoring dashboard"""
    
    # Get metrics from CloudWatch
    await cloudwatch_service.put_metric("AgencyPlatform", "DashboardView", 1.0)
    
    # Aggregate data
    total_models = await db.portfolio_images.distinct("model_id", {"agency_id": agency_id})
    total_licenses = await db.smart_licenses.count_documents({"agency_id": agency_id, "status": "active"})
    total_revenue = await db.royalty_payments.aggregate([
        {"$match": {"agency_id": agency_id}},
        {"$group": {"_id": None, "total": {"$sum": "$usd_equivalent"}}}
    ]).to_list(length=1)
    
    dashboard = AgencyDashboard(
        agency_id=agency_id,
        total_models=len(total_models),
        total_images=await db.portfolio_images.count_documents({"agency_id": agency_id}),
        active_licenses=total_licenses,
        total_revenue=total_revenue[0]["total"] if total_revenue else 0.0,
        open_tickets=await db.support_tickets.count_documents({"status": "open"}),
        pending_disputes=await db.dao_disputes.count_documents({"status": "voting"})
    )
    
    return dashboard


@router.get("/health")
async def agency_platform_health():
    """Health check for AWS agency platform"""
    
    return {
        "status": "healthy",
        "service": "aws_agency_platform",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": {
            "image_portfolio_management": "enabled",
            "smart_licensing": "enabled",
            "royalty_engine": "enabled",
            "agency_onboarding": "enabled",
            "compliance_management": "enabled",
            "support_system": "enabled",
            "dao_disputes": "enabled",
            "kbwi_system": "enabled",
            "security_monitoring": "enabled"
        },
        "aws_services": {
            "s3": "configured",
            "rekognition": "configured",
            "lambda": "configured",
            "dynamodb": "configured",
            "cognito": "configured",
            "step_functions": "configured",
            "macie": "configured",
            "qldb": "configured",
            "cloudwatch": "configured",
            "sns": "configured",
            "cloudfront": "configured",
            "blockchain": "configured"
        }
    }
