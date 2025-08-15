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
    """Model for business tax information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_name: str = "Big Mann Entertainment"
    ein: str = "270658077"
    
    # Business address
    address_line1: str = "Digital Media Distribution Empire"
    address_line2: Optional[str] = None
    city: str = "Nationwide"
    state: str = "USA"
    zip_code: str = "00000"
    country: str = "United States"
    
    # Business details
    business_type: str = "corporation"  # corporation, llc, partnership, sole_proprietorship
    tax_classification: str = "c_corporation"
    
    # Contact information
    contact_name: str = "John LeGerron Spivey"
    contact_title: str = "CEO"
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Tax settings
    default_backup_withholding: bool = False
    auto_generate_1099s: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str

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