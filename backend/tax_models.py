from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import uuid

class TaxDocument(BaseModel):
    """Model for tax documents like 1099s"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str  # 1099-NEC, 1099-MISC, W-9, etc.
    tax_year: int
    recipient_id: str  # User ID receiving the form
    recipient_name: str
    recipient_ein_ssn: Optional[str] = None
    recipient_address: Dict[str, str] = {}
    
    # Business information (payer)
    payer_name: str = "Big Mann Entertainment"
    payer_ein: str = "270658077"
    payer_address: Dict[str, str] = {}
    
    # Tax amounts
    total_payments: float = 0.0
    federal_income_tax_withheld: float = 0.0
    state_tax_withheld: float = 0.0
    
    # 1099-NEC specific fields
    nonemployee_compensation: float = 0.0  # Box 1
    
    # 1099-MISC specific fields
    rents: float = 0.0  # Box 1
    royalties: float = 0.0  # Box 2
    other_income: float = 0.0  # Box 3
    backup_withholding: float = 0.0  # Box 4
    
    # Document status
    status: str = "draft"  # draft, generated, sent, filed
    generated_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    filed_date: Optional[datetime] = None
    
    # Associated records
    sponsorship_deal_ids: List[str] = []
    payment_ids: List[str] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    notes: Optional[str] = None

class TaxPayment(BaseModel):
    """Model for tracking payments that have tax implications"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_type: str  # sponsorship_bonus, base_fee, performance_payment, etc.
    
    # Payment details
    amount: float
    currency: str = "USD"
    payment_date: date
    tax_year: int
    
    # Payer information (Big Mann Entertainment)
    payer_name: str = "Big Mann Entertainment"
    payer_ein: str = "270658077"
    
    # Payee information
    payee_id: str  # User ID
    payee_name: str
    payee_type: str  # individual, business
    payee_ein_ssn: Optional[str] = None
    payee_address: Dict[str, str] = {}
    
    # Tax classification
    is_taxable: bool = True
    tax_category: str  # nonemployee_compensation, royalties, other_income
    backup_withholding_applied: bool = False
    backup_withholding_rate: float = 0.24  # Current federal backup withholding rate
    
    # Withholdings
    federal_tax_withheld: float = 0.0
    state_tax_withheld: float = 0.0
    
    # Associated records
    sponsorship_deal_id: Optional[str] = None
    bonus_calculation_id: Optional[str] = None
    
    # Status
    status: str = "pending"  # pending, processed, reported, disputed
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    notes: Optional[str] = None

class TaxYear(BaseModel):
    """Model for managing tax year configurations and deadlines"""
    year: int
    is_current: bool = False
    
    # Important tax dates
    filing_deadline: date  # Usually April 15th
    extension_deadline: date  # Usually October 15th
    form_1099_deadline: date  # Usually January 31st
    
    # Tax rates and thresholds
    backup_withholding_rate: float = 0.24
    form_1099_threshold: float = 600.0  # Minimum amount requiring 1099
    
    # Status
    is_closed: bool = False
    filing_status: str = "open"  # open, filed, closed
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaxReport(BaseModel):
    """Model for tax reporting and analytics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str  # annual_summary, quarterly_summary, monthly_summary, 1099_report
    tax_year: int
    period_start: date
    period_end: date
    
    # Report data
    total_payments: float = 0.0
    total_taxable_payments: float = 0.0
    total_1099_payments: float = 0.0
    total_backup_withholding: float = 0.0
    
    # Breakdown by category
    nonemployee_compensation: float = 0.0
    royalty_payments: float = 0.0
    other_income: float = 0.0
    
    # Recipient counts
    total_recipients: int = 0
    recipients_over_threshold: int = 0
    
    # Status
    status: str = "draft"  # draft, generated, approved, filed
    generated_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    # Files
    report_file_path: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

class BusinessTaxInfo(BaseModel):
    """Model for business tax and license information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_name: str = "Big Mann Entertainment"
    
    # Tax Identification
    ein: str = "270658077"  # Employer Identification Number
    tin: str = "270658077"  # Taxpayer Identification Number (same as EIN for business)
    
    # License Information
    business_license_number: Optional[str] = None
    license_type: str = "Entertainment/Media Production"
    license_state: str = "AL"  # State where business is licensed
    license_expiration: Optional[date] = None
    
    # Primary Business Address
    address_line1: str = "1314 Lincoln Heights Street"
    address_line2: Optional[str] = None
    city: str = "Alexander City"
    state: str = "AL"
    zip_code: str = "35010"
    county: Optional[str] = "Tallapoosa County"
    country: str = "United States"
    
    # Mailing Address (if different)
    mailing_address_same: bool = True
    mailing_address_line1: Optional[str] = None
    mailing_address_line2: Optional[str] = None
    mailing_city: Optional[str] = None
    mailing_state: Optional[str] = None
    mailing_zip_code: Optional[str] = None
    mailing_country: Optional[str] = None
    
    # Business Details
    business_type: str = "corporation"  # corporation, llc, partnership, sole_proprietorship
    tax_classification: str = "c_corporation"
    naics_code: Optional[str] = "512200"  # Sound Recording Industries
    sic_code: Optional[str] = "7812"  # Motion Picture and Video Tape Production
    
    # Incorporation/Formation Details
    incorporation_state: str = "AL"
    incorporation_date: Optional[date] = None
    state_id_number: Optional[str] = None  # State corporation/LLC ID
    
    # Contact information
    contact_name: str = "John LeGerron Spivey"
    contact_title: str = "CEO"
    contact_phone: Optional[str] = "334-669-8638"
    contact_email: Optional[str] = None
    
    # Business Operations
    business_description: str = "Digital media distribution and sound recording services"
    primary_business_activity: str = "Sound Recording and Media Distribution Platform"
    date_business_started: Optional[date] = None
    fiscal_year_end: str = "December 31"
    
    # Tax settings
    default_backup_withholding: bool = False
    auto_generate_1099s: bool = True
    quarterly_filing_required: bool = True
    
    # License Status
    license_status: str = "active"  # active, expired, suspended, pending_renewal
    compliance_status: str = "compliant"  # compliant, non_compliant, under_review
    
    # Additional Business Registrations
    dba_names: List[str] = []  # Doing Business As names
    federal_tax_deposits: bool = True
    state_tax_registration: bool = True
    sales_tax_permit: Optional[str] = None
    
    # Professional Licenses (if applicable)
    professional_licenses: List[Dict[str, str]] = []  # [{license_type, number, state, expiration}]
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str

class BusinessLicense(BaseModel):
    """Model for individual business licenses"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    license_number: str
    license_type: str  # business_license, entertainment_license, resale_permit, etc.
    license_name: str
    
    # Issuing Authority
    issuing_authority: str  # City, County, State, Federal
    issuing_state: str
    issuing_city: Optional[str] = None
    issuing_county: Optional[str] = None
    
    # License Details
    issue_date: date
    expiration_date: date
    renewal_date: Optional[date] = None
    
    # Status
    status: str = "active"  # active, expired, suspended, revoked, pending
    
    # Requirements
    renewal_required: bool = True
    renewal_fee: Optional[float] = None
    annual_report_required: bool = False
    
    # Business Information
    business_name: str = "Big Mann Entertainment"
    business_address: Dict[str, str] = {}
    
    # Compliance
    compliance_requirements: List[str] = []
    last_compliance_check: Optional[date] = None
    
    # Documents
    license_document_path: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

class BusinessRegistration(BaseModel):
    """Model for business registrations and filings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registration_type: str  # incorporation, llc_formation, dba, trademark, etc.
    registration_number: str
    
    # Filing Details
    filing_state: str
    filing_date: date
    effective_date: date
    
    # Status
    status: str = "active"  # active, dissolved, suspended, merged
    
    # Business Details
    business_name: str = "Big Mann Entertainment"
    registered_agent_name: Optional[str] = None
    registered_agent_address: Dict[str, str] = {}
    
    # Annual Requirements
    annual_report_required: bool = True
    annual_report_due_date: Optional[date] = None
    annual_report_fee: Optional[float] = None
    last_annual_report_filed: Optional[date] = None
    
    # Fees and Payments
    initial_filing_fee: Optional[float] = None
    renewal_fee: Optional[float] = None
    
    # Documents
    certificate_path: Optional[str] = None
    articles_of_incorporation_path: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

class TaxSettings(BaseModel):
    """Model for system-wide tax settings and configurations"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Current tax year settings
    current_tax_year: int = datetime.now().year
    form_1099_threshold: float = 600.0
    backup_withholding_rate: float = 0.24
    
    # Automation settings
    auto_track_sponsorship_payments: bool = True
    auto_generate_tax_documents: bool = True
    auto_send_1099s: bool = False  # Requires manual approval
    
    # Notification settings
    notify_1099_threshold: bool = True
    notify_tax_deadlines: bool = True
    
    # Integration settings
    accounting_system_integration: bool = False
    tax_software_integration: bool = False
    
    # Compliance settings
    require_w9_collection: bool = True
    backup_withholding_threshold: float = 600.0
    
    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str