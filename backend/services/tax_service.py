from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
from decimal import Decimal
import os

# Import models with fallback
try:
    from .tax_models import *
    from .sponsorship_models import *
except ImportError:
    from tax_models import *
    from sponsorship_models import *

class TaxCalculationService:
    """Service for calculating taxes on sponsorship payments"""
    
    def __init__(self):
        self.current_tax_year = datetime.now().year
        self.form_1099_threshold = 600.00
        self.backup_withholding_rate = 0.24
        self.business_ein = os.environ.get('BUSINESS_EIN', '270658077')
        self.business_name = os.environ.get('BUSINESS_NAME', 'Big Mann Entertainment')
    
    def calculate_tax_on_payment(self, payment_amount: float, payee_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate tax implications for a sponsorship payment"""
        
        # Determine if backup withholding applies
        backup_withholding_required = self._requires_backup_withholding(payee_info)
        backup_withholding_amount = 0.0
        
        if backup_withholding_required:
            backup_withholding_amount = payment_amount * self.backup_withholding_rate
        
        # Determine tax category
        tax_category = self._determine_tax_category(payment_amount, payee_info)
        
        # Calculate net payment after withholding
        net_payment = payment_amount - backup_withholding_amount
        
        return {
            "gross_payment": payment_amount,
            "backup_withholding_amount": backup_withholding_amount,
            "net_payment": net_payment,
            "tax_category": tax_category,
            "requires_1099": payment_amount >= self.form_1099_threshold,
            "backup_withholding_required": backup_withholding_required,
            "tax_year": self.current_tax_year
        }
    
    def _requires_backup_withholding(self, payee_info: Dict[str, Any]) -> bool:
        """Determine if backup withholding is required"""
        
        # Check if payee has provided valid TIN (SSN or EIN)
        has_valid_tin = payee_info.get("ein_ssn") is not None
        
        # Check if payee is subject to backup withholding
        backup_withholding_exempt = payee_info.get("backup_withholding_exempt", False)
        
        # Backup withholding required if no TIN or not exempt
        return not has_valid_tin and not backup_withholding_exempt
    
    def _determine_tax_category(self, amount: float, payee_info: Dict[str, Any]) -> str:
        """Determine the appropriate tax category for the payment"""
        
        payment_type = payee_info.get("payment_type", "sponsorship_bonus")
        
        # Map payment types to tax categories
        category_mapping = {
            "sponsorship_bonus": "nonemployee_compensation",
            "performance_bonus": "nonemployee_compensation", 
            "base_fee": "nonemployee_compensation",
            "royalty": "royalties",
            "licensing_fee": "royalties",
            "other": "other_income"
        }
        
        return category_mapping.get(payment_type, "nonemployee_compensation")
    
    def calculate_annual_taxes(self, user_id: str, tax_year: int) -> Dict[str, Any]:
        """Calculate annual tax summary for a user"""
        
        # This would query the database for all payments to the user in the tax year
        # For now, return a template structure
        
        return {
            "user_id": user_id,
            "tax_year": tax_year,
            "total_payments": 0.0,
            "total_taxable": 0.0,
            "nonemployee_compensation": 0.0,
            "royalties": 0.0,
            "other_income": 0.0,
            "backup_withholding": 0.0,
            "requires_1099": False,
            "estimated_tax_owed": 0.0
        }

class Form1099Generator:
    """Service for generating 1099 tax forms"""
    
    def __init__(self):
        self.business_info = {
            "name": os.environ.get('BUSINESS_NAME', 'Big Mann Entertainment'),
            "ein": os.environ.get('BUSINESS_EIN', '270658077'),
            "address": os.environ.get('BUSINESS_ADDRESS', 'Digital Media Distribution Empire')
        }
    
    def generate_1099_nec(self, recipient_info: Dict[str, Any], payment_data: Dict[str, Any], tax_year: int) -> TaxDocument:
        """Generate a 1099-NEC form for nonemployee compensation"""
        
        form_1099 = TaxDocument(
            document_type="1099-NEC",
            tax_year=tax_year,
            recipient_id=recipient_info["user_id"],
            recipient_name=recipient_info["full_name"],
            recipient_ein_ssn=recipient_info.get("ein_ssn"),
            recipient_address=recipient_info.get("address", {}),
            
            # Payer information
            payer_name=self.business_info["name"],
            payer_ein=self.business_info["ein"],
            payer_address={"line1": self.business_info["address"]},
            
            # Payment amounts
            total_payments=payment_data["total_payments"],
            nonemployee_compensation=payment_data["nonemployee_compensation"],
            federal_income_tax_withheld=payment_data.get("federal_withholding", 0.0),
            backup_withholding=payment_data.get("backup_withholding", 0.0),
            
            # Associated records
            sponsorship_deal_ids=payment_data.get("deal_ids", []),
            payment_ids=payment_data.get("payment_ids", []),
            
            status="generated",
            generated_date=datetime.utcnow(),
            created_by="system"
        )
        
        return form_1099
    
    def generate_1099_misc(self, recipient_info: Dict[str, Any], payment_data: Dict[str, Any], tax_year: int) -> TaxDocument:
        """Generate a 1099-MISC form for miscellaneous income"""
        
        form_1099 = TaxDocument(
            document_type="1099-MISC",
            tax_year=tax_year,
            recipient_id=recipient_info["user_id"],
            recipient_name=recipient_info["full_name"],
            recipient_ein_ssn=recipient_info.get("ein_ssn"),
            recipient_address=recipient_info.get("address", {}),
            
            # Payer information
            payer_name=self.business_info["name"],
            payer_ein=self.business_info["ein"],
            payer_address={"line1": self.business_info["address"]},
            
            # Payment amounts
            total_payments=payment_data["total_payments"],
            royalties=payment_data.get("royalties", 0.0),
            other_income=payment_data.get("other_income", 0.0),
            federal_income_tax_withheld=payment_data.get("federal_withholding", 0.0),
            backup_withholding=payment_data.get("backup_withholding", 0.0),
            
            # Associated records
            sponsorship_deal_ids=payment_data.get("deal_ids", []),
            payment_ids=payment_data.get("payment_ids", []),
            
            status="generated",
            generated_date=datetime.utcnow(),
            created_by="system"
        )
        
        return form_1099
    
    def batch_generate_1099s(self, tax_year: int, recipients: List[Dict[str, Any]]) -> List[TaxDocument]:
        """Generate 1099 forms for multiple recipients"""
        
        generated_forms = []
        
        for recipient in recipients:
            # Determine which type of 1099 to generate
            if recipient["nonemployee_compensation"] >= 600:
                form = self.generate_1099_nec(recipient["info"], recipient["payments"], tax_year)
                generated_forms.append(form)
            elif recipient["royalties"] >= 10 or recipient["other_income"] >= 600:
                form = self.generate_1099_misc(recipient["info"], recipient["payments"], tax_year)
                generated_forms.append(form)
        
        return generated_forms

class TaxReportingService:
    """Service for tax reporting and compliance"""
    
    def __init__(self):
        self.business_ein = os.environ.get('BUSINESS_EIN', '270658077')
        self.current_tax_year = datetime.now().year
    
    def generate_annual_tax_report(self, tax_year: int) -> TaxReport:
        """Generate comprehensive annual tax report"""
        
        # This would aggregate all tax data for the year
        # For now, return a template structure
        
        report = TaxReport(
            report_type="annual_summary",
            tax_year=tax_year,
            period_start=date(tax_year, 1, 1),
            period_end=date(tax_year, 12, 31),
            
            # These would be calculated from actual data
            total_payments=0.0,
            total_taxable_payments=0.0,
            total_1099_payments=0.0,
            total_backup_withholding=0.0,
            
            nonemployee_compensation=0.0,
            royalty_payments=0.0,
            other_income=0.0,
            
            total_recipients=0,
            recipients_over_threshold=0,
            
            status="generated",
            generated_date=datetime.utcnow(),
            created_by="system"
        )
        
        return report
    
    def generate_quarterly_report(self, tax_year: int, quarter: int) -> TaxReport:
        """Generate quarterly tax report"""
        
        # Calculate quarter date range
        quarter_start_month = (quarter - 1) * 3 + 1
        period_start = date(tax_year, quarter_start_month, 1)
        
        if quarter == 4:
            period_end = date(tax_year, 12, 31)
        else:
            next_quarter_month = quarter_start_month + 3
            period_end = date(tax_year, next_quarter_month, 1) - timedelta(days=1)
        
        report = TaxReport(
            report_type="quarterly_summary",
            tax_year=tax_year,
            period_start=period_start,
            period_end=period_end,
            status="generated",
            generated_date=datetime.utcnow(),
            created_by="system"
        )
        
        return report
    
    def check_compliance_status(self) -> Dict[str, Any]:
        """Check current tax compliance status"""
        
        current_date = date.today()
        current_year = current_date.year
        
        # Check important tax deadlines
        deadlines = {
            "1099_deadline": date(current_year, 1, 31),
            "tax_filing_deadline": date(current_year, 4, 15),
            "quarterly_deadlines": [
                date(current_year, 4, 15),  # Q1
                date(current_year, 6, 15),  # Q2
                date(current_year, 9, 15),  # Q3
                date(current_year + 1, 1, 15)  # Q4
            ]
        }
        
        # Calculate compliance metrics
        compliance_status = {
            "current_tax_year": current_year,
            "business_ein": self.business_ein,
            "deadlines": deadlines,
            "compliance_score": 100,  # Would be calculated based on actual compliance
            "outstanding_actions": [],
            "recommendations": [
                "Ensure all sponsorship payments are properly tracked",
                "Collect W-9 forms from all recipients",
                "Generate 1099s by January 31st deadline"
            ]
        }
        
        return compliance_status

class TaxIntegrationService:
    """Service for integrating with external tax systems"""
    
    def __init__(self):
        self.business_ein = os.environ.get('BUSINESS_EIN', '270658077')
    
    def export_to_accounting_system(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export tax data to accounting system (QuickBooks, etc.)"""
        
        # This would integrate with external accounting systems
        # For now, return a template response
        
        return {
            "status": "success",
            "exported_records": 0,
            "export_format": "csv",
            "timestamp": datetime.utcnow(),
            "file_path": None
        }
    
    def import_w9_data(self, recipient_id: str, w9_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import W-9 form data for a recipient"""
        
        # Validate W-9 data
        required_fields = ["name", "business_name", "tax_classification", "address", "tin"]
        
        validation_errors = []
        for field in required_fields:
            if field not in w9_data or not w9_data[field]:
                validation_errors.append(f"Missing required field: {field}")
        
        if validation_errors:
            return {
                "status": "error",
                "errors": validation_errors
            }
        
        # Process valid W-9 data
        return {
            "status": "success",
            "recipient_id": recipient_id,
            "tin_verified": True,
            "backup_withholding_exempt": w9_data.get("backup_withholding_exempt", False)
        }