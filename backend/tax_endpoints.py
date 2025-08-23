from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import jwt
from pathlib import Path
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Database setup
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Authentication setup
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
security = HTTPBearer()

# User Model (local copy to avoid circular imports)
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    business_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    role: str = "user"  # user, admin, moderator, super_admin
    last_login: Optional[datetime] = None
    login_count: int = 0
    account_status: str = "active"  # active, inactive, suspended, banned
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Authentication functions (local copies)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.role not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Activity Log Model (local copy)
class ActivityLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

async def log_activity(user_id: str, action: str, resource_type: str, resource_id: str = None, details: Dict[str, Any] = None):
    """Log user activity for auditing purposes"""
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {}
    )
    await db.activity_logs.insert_one(activity.dict())

# Import tax models and services
try:
    from .tax_models import *
    from .tax_service import TaxCalculationService, Form1099Generator, TaxReportingService, TaxIntegrationService
except ImportError:
    from tax_models import *
    from tax_service import TaxCalculationService, Form1099Generator, TaxReportingService, TaxIntegrationService

# Create Tax router
tax_router = APIRouter(prefix="/tax", tags=["Tax Management"])

# Initialize services
tax_calculator = TaxCalculationService()
form_1099_generator = Form1099Generator()
tax_reporter = TaxReportingService()
tax_integrator = TaxIntegrationService()

# Business Tax Information Endpoints
@tax_router.get("/business-info", response_model=Dict[str, Any])
async def get_business_tax_info(
    current_user: User = Depends(get_current_admin_user)
):
    """Get business tax information"""
    business_info = await db.business_tax_info.find_one({}, {"_id": 0})
    
    if not business_info:
        # Create default business info from environment variables
        default_info = BusinessTaxInfo(
            business_name=os.environ.get('BUSINESS_NAME', 'Big Mann Entertainment'),
            ein=os.environ.get('BUSINESS_EIN', '270658077'),
            address_line1=os.environ.get('BUSINESS_ADDRESS', 'Digital Media Distribution Empire'),
            updated_by=current_user.id
        )
        
        await db.business_tax_info.insert_one(default_info.dict())
        business_info = default_info.dict()
    
    return {"business_info": business_info}

@tax_router.put("/business-info", response_model=Dict[str, Any])
async def update_business_tax_info(
    business_data: BusinessTaxInfo,
    current_user: User = Depends(get_current_admin_user)
):
    """Update business tax information"""
    try:
        business_data.updated_by = current_user.id
        business_data.updated_at = datetime.utcnow()
        
        await db.business_tax_info.delete_many({})  # Remove existing
        await db.business_tax_info.insert_one(business_data.dict())
        
        # Log activity
        await log_activity(
            current_user.id,
            "business_tax_info_updated",
            "tax_management",
            business_data.id,
            {"ein": business_data.ein, "business_name": business_data.business_name}
        )
        
        return {
            "message": "Business tax information updated successfully",
            "ein": business_data.ein
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update business info: {str(e)}")

# Tax Payment Tracking
@tax_router.post("/payments", response_model=Dict[str, Any])
async def record_tax_payment(
    payment_data: TaxPayment,
    current_user: User = Depends(get_current_admin_user)
):
    """Record a tax payment for tracking purposes"""
    try:
        payment_data.created_by = current_user.id
        
        # Calculate tax implications
        payee_info = {
            "user_id": payment_data.payee_id,
            "ein_ssn": payment_data.payee_ein_ssn,
            "payment_type": payment_data.payment_type
        }
        
        tax_calc = tax_calculator.calculate_tax_on_payment(
            payment_data.amount, 
            payee_info
        )
        
        # Update payment with tax calculations
        payment_data.is_taxable = tax_calc["requires_1099"]
        payment_data.tax_category = tax_calc["tax_category"]
        
        # Apply backup withholding if required
        if tax_calc["backup_withholding_required"]:
            payment_data.backup_withholding_applied = True
            payment_data.federal_tax_withheld = tax_calc["backup_withholding_amount"]
        
        # Store in database
        payment_dict = payment_data.dict()
        payment_dict['payment_date'] = payment_dict['payment_date'].isoformat()
        await db.tax_payments.insert_one(payment_dict)
        
        # Log activity
        await log_activity(
            current_user.id,
            "tax_payment_recorded",
            "tax_payment",
            payment_data.id,
            {
                "amount": payment_data.amount,
                "payee_name": payment_data.payee_name,
                "tax_category": payment_data.tax_category
            }
        )
        
        return {
            "message": "Tax payment recorded successfully",
            "payment_id": payment_data.id,
            "tax_calculations": tax_calc
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record tax payment: {str(e)}")

@tax_router.get("/payments", response_model=Dict[str, Any])
async def get_tax_payments(
    tax_year: Optional[int] = Query(None, description="Filter by tax year"),
    payee_id: Optional[str] = Query(None, description="Filter by payee"),
    payment_type: Optional[str] = Query(None, description="Filter by payment type"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, description="Number of records to return"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get tax payments with filtering options"""
    
    query = {}
    if tax_year:
        query["tax_year"] = tax_year
    if payee_id:
        query["payee_id"] = payee_id
    if payment_type:
        query["payment_type"] = payment_type
    
    payments_cursor = db.tax_payments.find(query, {"_id": 0}).skip(skip).limit(limit).sort("payment_date", -1)
    payments = await payments_cursor.to_list(length=limit)
    total = await db.tax_payments.count_documents(query)
    
    return {
        "payments": payments,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# 1099 Generation and Management
@tax_router.post("/generate-1099s/{tax_year}", response_model=Dict[str, Any])
async def generate_1099_forms(
    tax_year: int,
    current_user: User = Depends(get_current_admin_user)
):
    """Generate 1099 forms for a tax year"""
    try:
        # Get all payments for the tax year that meet 1099 requirements
        payments_cursor = db.tax_payments.find({
            "tax_year": tax_year,
            "is_taxable": True,
            "amount": {"$gte": 600}  # $600 threshold for 1099s
        }, {"_id": 0})
        payments = await payments_cursor.to_list(length=None)
        
        # Group payments by payee
        payee_totals = {}
        for payment in payments:
            payee_id = payment["payee_id"]
            if payee_id not in payee_totals:
                payee_totals[payee_id] = {
                    "info": {
                        "user_id": payee_id,
                        "full_name": payment["payee_name"],
                        "ein_ssn": payment.get("payee_ein_ssn"),
                        "address": payment.get("payee_address", {})
                    },
                    "payments": {
                        "total_payments": 0.0,
                        "nonemployee_compensation": 0.0,
                        "royalties": 0.0,
                        "other_income": 0.0,
                        "backup_withholding": 0.0,
                        "deal_ids": [],
                        "payment_ids": []
                    }
                }
            
            payee_data = payee_totals[payee_id]["payments"]
            payee_data["total_payments"] += payment["amount"]
            payee_data["backup_withholding"] += payment.get("federal_tax_withheld", 0.0)
            payee_data["payment_ids"].append(payment["id"])
            
            # Categorize by tax category
            if payment["tax_category"] == "nonemployee_compensation":
                payee_data["nonemployee_compensation"] += payment["amount"]
            elif payment["tax_category"] == "royalties":
                payee_data["royalties"] += payment["amount"]
            else:
                payee_data["other_income"] += payment["amount"]
        
        # Generate 1099 forms
        generated_forms = []
        recipients_list = list(payee_totals.values())
        forms = form_1099_generator.batch_generate_1099s(tax_year, recipients_list)
        
        # Store generated forms in database
        for form in forms:
            form_dict = form.dict()
            form_dict['generated_date'] = form_dict['generated_date'].isoformat()
            await db.tax_documents.insert_one(form_dict)
            generated_forms.append(form.id)
        
        # Log activity
        await log_activity(
            current_user.id,
            "1099_forms_generated",
            "tax_documents",
            None,
            {
                "tax_year": tax_year,
                "forms_generated": len(generated_forms),
                "recipients": len(payee_totals)
            }
        )
        
        return {
            "message": f"Generated {len(generated_forms)} 1099 forms for tax year {tax_year}",
            "forms_generated": len(generated_forms),
            "recipients": len(payee_totals),
            "form_ids": generated_forms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate 1099 forms: {str(e)}")

@tax_router.get("/1099s", response_model=Dict[str, Any])
async def get_1099_forms(
    tax_year: Optional[int] = Query(None, description="Filter by tax year"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, description="Number of records to return"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get 1099 forms with filtering options"""
    
    query = {}
    if tax_year:
        query["tax_year"] = tax_year
    if document_type:
        query["document_type"] = document_type
    if status:
        query["status"] = status
    
    forms_cursor = db.tax_documents.find(query, {"_id": 0}).skip(skip).limit(limit).sort("generated_date", -1)
    forms = await forms_cursor.to_list(length=limit)
    total = await db.tax_documents.count_documents(query)
    
    return {
        "forms": forms,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@tax_router.get("/1099s/{form_id}", response_model=Dict[str, Any])
async def get_1099_form_details(
    form_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get detailed 1099 form information"""
    form = await db.tax_documents.find_one({"id": form_id}, {"_id": 0})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    return {"form": form}

# Tax Reporting
@tax_router.post("/reports/annual/{tax_year}", response_model=Dict[str, Any])
async def generate_annual_tax_report(
    tax_year: int,
    current_user: User = Depends(get_current_admin_user)
):
    """Generate annual tax report"""
    try:
        # Generate the report
        report = tax_reporter.generate_annual_tax_report(tax_year)
        
        # Get actual data from database
        payments_cursor = db.tax_payments.find({"tax_year": tax_year}, {"_id": 0})
        payments = await payments_cursor.to_list(length=None)
        
        # Calculate report totals
        total_payments = sum(p["amount"] for p in payments)
        taxable_payments = sum(p["amount"] for p in payments if p.get("is_taxable", False))
        total_1099_payments = sum(p["amount"] for p in payments if p.get("amount", 0) >= 600)
        backup_withholding = sum(p.get("federal_tax_withheld", 0) for p in payments)
        
        # Update report with actual data
        report.total_payments = total_payments
        report.total_taxable_payments = taxable_payments
        report.total_1099_payments = total_1099_payments
        report.total_backup_withholding = backup_withholding
        
        # Count recipients
        unique_payees = set(p["payee_id"] for p in payments)
        report.total_recipients = len(unique_payees)
        report.recipients_over_threshold = len([p for p in payments if p.get("amount", 0) >= 600])
        
        report.created_by = current_user.id
        
        # Store report in database
        report_dict = report.dict()
        report_dict['period_start'] = report_dict['period_start'].isoformat()
        report_dict['period_end'] = report_dict['period_end'].isoformat()
        report_dict['generated_date'] = report_dict['generated_date'].isoformat()
        await db.tax_reports.insert_one(report_dict)
        
        # Log activity
        await log_activity(
            current_user.id,
            "annual_tax_report_generated",
            "tax_report",
            report.id,
            {
                "tax_year": tax_year,
                "total_payments": total_payments,
                "total_recipients": report.total_recipients
            }
        )
        
        return {
            "message": f"Annual tax report generated for {tax_year}",
            "report_id": report.id,
            "summary": {
                "total_payments": total_payments,
                "taxable_payments": taxable_payments,
                "total_recipients": report.total_recipients,
                "recipients_over_threshold": report.recipients_over_threshold
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate tax report: {str(e)}")

@tax_router.get("/reports", response_model=Dict[str, Any])
async def get_tax_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    tax_year: Optional[int] = Query(None, description="Filter by tax year"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(20, description="Number of records to return"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get tax reports with filtering options"""
    
    query = {}
    if report_type:
        query["report_type"] = report_type
    if tax_year:
        query["tax_year"] = tax_year
    
    reports_cursor = db.tax_reports.find(query, {"_id": 0}).skip(skip).limit(limit).sort("generated_date", -1)
    reports = await reports_cursor.to_list(length=limit)
    total = await db.tax_reports.count_documents(query)
    
    return {
        "reports": reports,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# Tax Dashboard and Analytics
@tax_router.get("/dashboard/{tax_year}", response_model=Dict[str, Any])
async def get_tax_dashboard(
    tax_year: int,
    current_user: User = Depends(get_current_admin_user)
):
    """Get tax dashboard with key metrics"""
    
    # Get payments for the tax year
    payments_cursor = db.tax_payments.find({"tax_year": tax_year}, {"_id": 0})
    payments = await payments_cursor.to_list(length=None)
    
    # Calculate dashboard metrics
    total_payments = sum(p["amount"] for p in payments)
    taxable_payments = sum(p["amount"] for p in payments if p.get("is_taxable", False))
    backup_withholding = sum(p.get("federal_tax_withheld", 0) for p in payments)
    
    # Count forms generated
    forms_count = await db.tax_documents.count_documents({"tax_year": tax_year})
    
    # Count unique recipients
    unique_recipients = len(set(p["payee_id"] for p in payments))
    recipients_over_threshold = len([p for p in payments if p.get("amount", 0) >= 600])
    
    # Payment categories
    nonemployee_comp = sum(p["amount"] for p in payments if p.get("tax_category") == "nonemployee_compensation")
    royalties = sum(p["amount"] for p in payments if p.get("tax_category") == "royalties")
    other_income = sum(p["amount"] for p in payments if p.get("tax_category") == "other_income")
    
    # Check compliance status
    compliance = tax_reporter.check_compliance_status()
    
    return {
        "tax_year": tax_year,
        "business_ein": os.environ.get('BUSINESS_EIN', '270658077'),
        "overview": {
            "total_payments": total_payments,
            "taxable_payments": taxable_payments,
            "backup_withholding": backup_withholding,
            "forms_generated": forms_count,
            "total_recipients": unique_recipients,
            "recipients_over_threshold": recipients_over_threshold
        },
        "payment_categories": {
            "nonemployee_compensation": nonemployee_comp,
            "royalties": royalties,
            "other_income": other_income
        },
        "compliance": compliance,
        "quick_actions": [
            {"label": "Generate 1099s", "action": "generate_1099s", "enabled": True},
            {"label": "Generate Annual Report", "action": "generate_annual_report", "enabled": True},
            {"label": "Export to Accounting", "action": "export_accounting", "enabled": True}
        ]
    }

# Business License Management
@tax_router.get("/licenses", response_model=Dict[str, Any])
async def get_business_licenses(
    license_type: Optional[str] = Query(None, description="Filter by license type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(20, description="Number of records to return"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get business licenses with filtering options"""
    
    query = {}
    if license_type:
        query["license_type"] = license_type
    if status:
        query["status"] = status
    
    licenses_cursor = db.business_licenses.find(query, {"_id": 0}).skip(skip).limit(limit).sort("expiration_date", 1)
    licenses = await licenses_cursor.to_list(length=limit)
    total = await db.business_licenses.count_documents(query)
    
    # Check for expiring licenses (within 90 days)
    expiring_soon = []
    for license in licenses:
        if license.get("expiration_date"):
            exp_date = datetime.strptime(license["expiration_date"], "%Y-%m-%d").date()
            days_until_expiry = (exp_date - date.today()).days
            if days_until_expiry <= 90:
                expiring_soon.append({
                    "license_id": license["id"],
                    "license_name": license["license_name"],
                    "days_until_expiry": days_until_expiry
                })
    
    return {
        "licenses": licenses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "expiring_soon": expiring_soon
    }

@tax_router.post("/licenses", response_model=Dict[str, Any])
async def create_business_license(
    license_data: BusinessLicense,
    current_user: User = Depends(get_current_admin_user)
):
    """Create new business license record"""
    try:
        license_data.created_by = current_user.id
        
        # Convert dates to strings for MongoDB storage
        license_dict = license_data.dict()
        license_dict['issue_date'] = license_dict['issue_date'].isoformat()
        license_dict['expiration_date'] = license_dict['expiration_date'].isoformat()
        if license_dict.get('renewal_date'):
            license_dict['renewal_date'] = license_dict['renewal_date'].isoformat()
        
        await db.business_licenses.insert_one(license_dict)
        
        # Log activity
        await log_activity(
            current_user.id,
            "business_license_created",
            "business_license",
            license_data.id,
            {
                "license_number": license_data.license_number,
                "license_type": license_data.license_type,
                "issuing_authority": license_data.issuing_authority
            }
        )
        
        return {
            "message": "Business license created successfully",
            "license_id": license_data.id,
            "license_number": license_data.license_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create business license: {str(e)}")

@tax_router.get("/licenses/{license_id}", response_model=Dict[str, Any])
async def get_license_details(
    license_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get detailed license information"""
    license = await db.business_licenses.find_one({"id": license_id}, {"_id": 0})
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    
    # Calculate days until expiration
    if license.get("expiration_date"):
        exp_date = datetime.strptime(license["expiration_date"], "%Y-%m-%d").date()
        days_until_expiry = (exp_date - date.today()).days
        license["days_until_expiry"] = days_until_expiry
        license["renewal_needed"] = days_until_expiry <= 90
    
    return {"license": license}

@tax_router.put("/licenses/{license_id}", response_model=Dict[str, Any])
async def update_business_license(
    license_id: str,
    license_data: BusinessLicense,
    current_user: User = Depends(get_current_admin_user)
):
    """Update business license information"""
    try:
        license_data.updated_at = datetime.utcnow()
        
        # Convert dates to strings for MongoDB storage
        license_dict = license_data.dict()
        license_dict['issue_date'] = license_dict['issue_date'].isoformat()
        license_dict['expiration_date'] = license_dict['expiration_date'].isoformat()
        if license_dict.get('renewal_date'):
            license_dict['renewal_date'] = license_dict['renewal_date'].isoformat()
        
        result = await db.business_licenses.replace_one({"id": license_id}, license_dict)
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="License not found")
        
        # Log activity
        await log_activity(
            current_user.id,
            "business_license_updated",
            "business_license",
            license_id,
            {
                "license_number": license_data.license_number,
                "status": license_data.status
            }
        )
        
        return {
            "message": "Business license updated successfully",
            "license_id": license_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update business license: {str(e)}")

# Business Registration Management
@tax_router.get("/registrations", response_model=Dict[str, Any])
async def get_business_registrations(
    registration_type: Optional[str] = Query(None, description="Filter by registration type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get business registrations"""
    
    query = {}
    if registration_type:
        query["registration_type"] = registration_type
    if status:
        query["status"] = status
    
    registrations_cursor = db.business_registrations.find(query, {"_id": 0}).sort("filing_date", -1)
    registrations = await registrations_cursor.to_list(length=None)
    
    # Check for upcoming annual report deadlines
    upcoming_deadlines = []
    for reg in registrations:
        if reg.get("annual_report_due_date") and reg.get("status") == "active":
            due_date = datetime.strptime(reg["annual_report_due_date"], "%Y-%m-%d").date()
            days_until_due = (due_date - date.today()).days
            if 0 <= days_until_due <= 60:  # Due within 60 days
                upcoming_deadlines.append({
                    "registration_id": reg["id"],
                    "registration_type": reg["registration_type"],
                    "due_date": reg["annual_report_due_date"],
                    "days_until_due": days_until_due
                })
    
    return {
        "registrations": registrations,
        "total": len(registrations),
        "upcoming_deadlines": upcoming_deadlines
    }

@tax_router.post("/registrations", response_model=Dict[str, Any])
async def create_business_registration(
    registration_data: BusinessRegistration,
    current_user: User = Depends(get_current_admin_user)
):
    """Create new business registration record"""
    try:
        registration_data.created_by = current_user.id
        
        # Convert dates to strings for MongoDB storage
        reg_dict = registration_data.dict()
        reg_dict['filing_date'] = reg_dict['filing_date'].isoformat()
        reg_dict['effective_date'] = reg_dict['effective_date'].isoformat()
        if reg_dict.get('annual_report_due_date'):
            reg_dict['annual_report_due_date'] = reg_dict['annual_report_due_date'].isoformat()
        if reg_dict.get('last_annual_report_filed'):
            reg_dict['last_annual_report_filed'] = reg_dict['last_annual_report_filed'].isoformat()
        
        await db.business_registrations.insert_one(reg_dict)
        
        # Log activity
        await log_activity(
            current_user.id,
            "business_registration_created",
            "business_registration",
            registration_data.id,
            {
                "registration_number": registration_data.registration_number,
                "registration_type": registration_data.registration_type,
                "filing_state": registration_data.filing_state
            }
        )
        
        return {
            "message": "Business registration created successfully",
            "registration_id": registration_data.id,
            "registration_number": registration_data.registration_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create business registration: {str(e)}")

# Compliance Dashboard
@tax_router.get("/compliance-dashboard", response_model=Dict[str, Any])
async def get_compliance_dashboard(
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive compliance dashboard"""
    
    # Get business info
    business_info = await db.business_tax_info.find_one({}, {"_id": 0})
    
    # Get licenses
    licenses = await db.business_licenses.find({}, {"_id": 0}).to_list(length=None)
    
    # Get registrations
    registrations = await db.business_registrations.find({}, {"_id": 0}).to_list(length=None)
    
    # Calculate compliance metrics
    total_licenses = len(licenses)
    active_licenses = len([l for l in licenses if l.get("status") == "active"])
    expiring_licenses = []
    
    for license in licenses:
        if license.get("expiration_date") and license.get("status") == "active":
            exp_date = datetime.strptime(license["expiration_date"], "%Y-%m-%d").date()
            days_until_expiry = (exp_date - date.today()).days
            if days_until_expiry <= 90:
                expiring_licenses.append({
                    "license_name": license["license_name"],
                    "expiration_date": license["expiration_date"],
                    "days_until_expiry": days_until_expiry
                })
    
    # Registration compliance
    active_registrations = len([r for r in registrations if r.get("status") == "active"])
    upcoming_deadlines = []
    
    for reg in registrations:
        if reg.get("annual_report_due_date") and reg.get("status") == "active":
            due_date = datetime.strptime(reg["annual_report_due_date"], "%Y-%m-%d").date()
            days_until_due = (due_date - date.today()).days
            if 0 <= days_until_due <= 60:
                upcoming_deadlines.append({
                    "registration_type": reg["registration_type"],
                    "due_date": reg["annual_report_due_date"],
                    "days_until_due": days_until_due
                })
    
    # Overall compliance score
    compliance_score = 100
    compliance_issues = []
    
    if expiring_licenses:
        compliance_score -= 10
        compliance_issues.append(f"{len(expiring_licenses)} licenses expiring within 90 days")
    
    if upcoming_deadlines:
        compliance_score -= 5
        compliance_issues.append(f"{len(upcoming_deadlines)} annual reports due within 60 days")
    
    if not business_info:
        compliance_score -= 20
        compliance_issues.append("Business tax information not complete")
    
    return {
        "business_info": business_info,
        "compliance_overview": {
            "compliance_score": max(compliance_score, 0),
            "total_licenses": total_licenses,
            "active_licenses": active_licenses,
            "expiring_licenses": len(expiring_licenses),
            "active_registrations": active_registrations,
            "upcoming_deadlines": len(upcoming_deadlines)
        },
        "alerts": {
            "expiring_licenses": expiring_licenses,
            "upcoming_deadlines": upcoming_deadlines,
            "compliance_issues": compliance_issues
        },
        "quick_actions": [
            {"label": "Update Business Information", "action": "update_business_info", "priority": "medium"},
            {"label": "Renew Expiring Licenses", "action": "renew_licenses", "priority": "high" if expiring_licenses else "low"},
            {"label": "File Annual Reports", "action": "file_annual_reports", "priority": "high" if upcoming_deadlines else "low"},
            {"label": "Generate Tax Reports", "action": "generate_tax_reports", "priority": "medium"}
        ]
    }
@tax_router.get("/settings", response_model=Dict[str, Any])
async def get_tax_settings(
    current_user: User = Depends(get_current_admin_user)
):
    """Get tax system settings"""
    settings = await db.tax_settings.find_one({}, {"_id": 0})
    
    if not settings:
        # Create default settings
        default_settings = TaxSettings(
            updated_by=current_user.id
        )
        await db.tax_settings.insert_one(default_settings.dict())
        settings = default_settings.dict()
    
    return {"settings": settings}

@tax_router.put("/settings", response_model=Dict[str, Any])
async def update_tax_settings(
    settings_data: TaxSettings,
    current_user: User = Depends(get_current_admin_user)
):
    """Update tax system settings"""
    try:
        settings_data.updated_by = current_user.id
        settings_data.updated_at = datetime.utcnow()
        
        await db.tax_settings.delete_many({})  # Remove existing
        await db.tax_settings.insert_one(settings_data.dict())
        
        # Log activity
        await log_activity(
            current_user.id,
            "tax_settings_updated",
            "tax_management",
            settings_data.id,
            {"threshold": settings_data.form_1099_threshold}
        )
        
        return {
            "message": "Tax settings updated successfully",
            "settings_id": settings_data.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tax settings: {str(e)}")

# Missing Business Info Endpoint - ADD FOR IMPROVED FUNCTIONALITY  
@tax_router.get("/business-info")
async def get_business_tax_info(current_user: User = Depends(get_current_user)):
    """Get business tax information (accessible to regular users)"""
    try:
        # Get business tax information
        business_info = await db.business_tax_info.find_one({}, {"_id": 0})
        
        if not business_info:
            # Return default business information from environment variables
            business_info = {
                "business_legal_name": os.environ.get('BUSINESS_LEGAL_NAME', 'Big Mann Entertainment'),
                "business_ein": os.environ.get('BUSINESS_EIN', '270658077'),
                "business_tin": os.environ.get('BUSINESS_TIN', '12800'),
                "business_address": os.environ.get('BUSINESS_ADDRESS', '123 Music Row, Nashville, TN 37203'),
                "business_phone": os.environ.get('BUSINESS_PHONE', '+1-615-555-0100'),
                "principal_name": os.environ.get('PRINCIPAL_NAME', 'John LeGerron Spivey'),
                "business_type": "Entertainment Services",
                "filing_status": "active",
                "tax_year": 2025,
                "accounting_method": "accrual",
                "fiscal_year_end": "12-31"
            }
        
        # Get basic license status
        total_licenses = await db.business_licenses.count_documents({})
        active_licenses = await db.business_licenses.count_documents({"status": "active"})
        
        # Get basic registration status
        total_registrations = await db.business_registrations.count_documents({})
        active_registrations = await db.business_registrations.count_documents({"status": "active"})
        
        return {
            "business_information": business_info,
            "compliance_status": {
                "licenses": {
                    "total": total_licenses,
                    "active": active_licenses,
                    "compliance_score": (active_licenses / max(total_licenses, 1)) * 100 if total_licenses > 0 else 100
                },
                "registrations": {
                    "total": total_registrations,
                    "active": active_registrations,
                    "compliance_score": (active_registrations / max(total_registrations, 1)) * 100 if total_registrations > 0 else 100
                },
                "overall_status": "compliant" if (total_licenses == active_licenses and total_registrations == active_registrations) else "needs_attention"
            },
            "tax_year": 2025,
            "user_access_level": "standard" if not current_user.is_admin else "admin"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve business information: {str(e)}")