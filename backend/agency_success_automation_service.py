"""
Agency Success Automation Service
Business logic for automated onboarding, KPI tracking, contracts, and revenue forecasting
"""

import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import uuid
import statistics
import random

from agency_success_automation_models import (
    OnboardingStatus, OnboardingStepType, ContractStatus, ContractType,
    BookingStatus, BookingType, KPICategory, AlertSeverity,
    OnboardingStep, OnboardingWorkflow, OnboardingTemplate,
    ContractParty, ContractClause, Contract, ContractTemplate,
    Booking, KPIMetric, TalentPerformance, AgencyKPIDashboard,
    RevenueForecast, ForecastScenario, AutomationRule, WorkflowAlert,
    OnboardingStats, ContractStats, BookingStats, AutomationDashboard
)

logger = logging.getLogger(__name__)


def _serialize_for_mongo(obj: Any) -> Any:
    """Convert Pydantic models and enums for MongoDB storage"""
    if hasattr(obj, 'dict'):
        return _serialize_for_mongo(obj.dict())
    elif isinstance(obj, dict):
        return {k: _serialize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_for_mongo(item) for item in obj]
    elif hasattr(obj, 'value'):  # Enum
        return obj.value
    elif isinstance(obj, datetime):
        return obj
    else:
        return obj


class AgencySuccessAutomationService:
    """Service for Agency Success Automation features"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.onboarding_collection = db.onboarding_workflows
        self.onboarding_templates = db.onboarding_templates
        self.contracts_collection = db.contracts
        self.contract_templates = db.contract_templates
        self.bookings_collection = db.bookings
        self.kpi_metrics = db.kpi_metrics
        self.talent_performance = db.talent_performance
        self.revenue_forecasts = db.revenue_forecasts
        self.automation_rules = db.automation_rules
        self.alerts_collection = db.workflow_alerts
        
    # =========================
    # Onboarding Workflows
    # =========================
    
    async def create_onboarding_workflow(
        self,
        talent_id: str,
        talent_name: str,
        talent_email: str,
        agency_id: str,
        template_id: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> OnboardingWorkflow:
        """Create a new onboarding workflow for a talent"""
        
        # Get template or use default steps
        if template_id:
            template = await self.onboarding_templates.find_one({"id": template_id})
            steps_config = template.get('steps', []) if template else []
        else:
            steps_config = self._get_default_onboarding_steps()
        
        # Create steps from config
        steps = []
        for i, step_config in enumerate(steps_config, 1):
            steps.append(OnboardingStep(
                step_number=i,
                step_type=OnboardingStepType(step_config.get('step_type', 'form_submission')),
                title=step_config.get('title', f'Step {i}'),
                description=step_config.get('description', ''),
                required=step_config.get('required', True)
            ))
        
        workflow = OnboardingWorkflow(
            talent_id=talent_id,
            talent_name=talent_name,
            talent_email=talent_email,
            agency_id=agency_id,
            steps=steps,
            assigned_to=assigned_to,
            due_date=datetime.now(timezone.utc) + timedelta(days=14),
            status=OnboardingStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc)
        )
        
        await self.onboarding_collection.insert_one(_serialize_for_mongo(workflow))
        logger.info(f"Created onboarding workflow {workflow.id} for talent {talent_name}")
        
        # Create alert for assigned user
        if assigned_to:
            await self._create_alert(
                agency_id=agency_id,
                alert_type="new_onboarding",
                severity=AlertSeverity.MEDIUM,
                title=f"New Onboarding: {talent_name}",
                message=f"A new onboarding workflow has been assigned to you for {talent_name}",
                related_entity_type="onboarding",
                related_entity_id=workflow.id
            )
        
        return workflow
    
    def _get_default_onboarding_steps(self) -> List[Dict]:
        """Get default onboarding steps"""
        return [
            {
                "step_type": "document_upload",
                "title": "Upload Identification Documents",
                "description": "Upload government-issued ID and proof of eligibility to work",
                "required": True
            },
            {
                "step_type": "form_submission",
                "title": "Complete Personal Information Form",
                "description": "Fill out personal details, emergency contacts, and preferences",
                "required": True
            },
            {
                "step_type": "photo_submission",
                "title": "Submit Portfolio Photos",
                "description": "Upload professional photos including headshots, full body, and comp cards",
                "required": True
            },
            {
                "step_type": "measurement_entry",
                "title": "Enter Measurements",
                "description": "Provide accurate measurements for casting purposes",
                "required": True
            },
            {
                "step_type": "verification",
                "title": "Background Verification",
                "description": "Complete background check and reference verification",
                "required": True
            },
            {
                "step_type": "contract_signing",
                "title": "Sign Representation Agreement",
                "description": "Review and sign the agency representation contract",
                "required": True
            },
            {
                "step_type": "training",
                "title": "Complete Onboarding Training",
                "description": "Watch orientation videos and complete agency training modules",
                "required": False
            },
            {
                "step_type": "approval",
                "title": "Final Review & Approval",
                "description": "Final review by agency management for roster addition",
                "required": True
            }
        ]
    
    async def update_onboarding_step(
        self,
        workflow_id: str,
        step_id: str,
        status: OnboardingStatus,
        data: Dict[str, Any] = None,
        notes: str = None,
        completed_by: str = None
    ) -> OnboardingWorkflow:
        """Update a step in an onboarding workflow"""
        
        workflow_doc = await self.onboarding_collection.find_one({"id": workflow_id})
        if not workflow_doc:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Update the specific step
        steps = workflow_doc.get('steps', [])
        updated = False
        completed_steps = 0
        total_required = 0
        
        for step in steps:
            if step['id'] == step_id:
                step['status'] = status.value if hasattr(status, 'value') else status
                if data:
                    step['data'] = data
                if notes:
                    step['notes'] = notes
                if status in [OnboardingStatus.COMPLETED, OnboardingStatus.APPROVED]:
                    step['completed_at'] = datetime.now(timezone.utc)
                    step['completed_by'] = completed_by
                updated = True
            
            # Calculate progress
            if step.get('required', True):
                total_required += 1
                if step.get('status') in ['completed', 'approved']:
                    completed_steps += 1
        
        if not updated:
            raise ValueError(f"Step {step_id} not found in workflow")
        
        # Calculate overall progress
        progress = (completed_steps / total_required * 100) if total_required > 0 else 0
        
        # Determine workflow status
        workflow_status = workflow_doc['status']
        if progress >= 100:
            workflow_status = OnboardingStatus.COMPLETED.value
        elif any(s.get('status') == 'pending_review' for s in steps):
            workflow_status = OnboardingStatus.PENDING_REVIEW.value
        
        # Update workflow
        update_data = {
            'steps': steps,
            'progress_percentage': progress,
            'status': workflow_status,
            'updated_at': datetime.now(timezone.utc)
        }
        
        if workflow_status == OnboardingStatus.COMPLETED.value:
            update_data['completed_at'] = datetime.now(timezone.utc)
        
        await self.onboarding_collection.update_one(
            {"id": workflow_id},
            {"$set": update_data}
        )
        
        # Fetch and return updated workflow
        updated_doc = await self.onboarding_collection.find_one({"id": workflow_id})
        return OnboardingWorkflow(**updated_doc)
    
    async def get_onboarding_workflows(
        self,
        agency_id: str,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 50
    ) -> List[OnboardingWorkflow]:
        """Get onboarding workflows for an agency"""
        
        query = {"agency_id": agency_id}
        if status:
            query['status'] = status
        if assigned_to:
            query['assigned_to'] = assigned_to
        
        cursor = self.onboarding_collection.find(query).sort('created_at', -1).limit(limit)
        workflows = await cursor.to_list(length=limit)
        
        return [OnboardingWorkflow(**w) for w in workflows]
    
    async def get_onboarding_stats(self, agency_id: str) -> OnboardingStats:
        """Get onboarding statistics for an agency"""
        
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Count by status
        pipeline = [
            {"$match": {"agency_id": agency_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_counts = await self.onboarding_collection.aggregate(pipeline).to_list(length=10)
        
        total = sum(s['count'] for s in status_counts)
        in_progress = next((s['count'] for s in status_counts if s['_id'] == 'in_progress'), 0)
        pending = next((s['count'] for s in status_counts if s['_id'] == 'pending_review'), 0)
        
        # Completed this month
        completed_count = await self.onboarding_collection.count_documents({
            "agency_id": agency_id,
            "status": "completed",
            "completed_at": {"$gte": month_start}
        })
        
        # Average completion time
        completed_workflows = await self.onboarding_collection.find({
            "agency_id": agency_id,
            "status": "completed",
            "started_at": {"$exists": True},
            "completed_at": {"$exists": True}
        }).to_list(length=100)
        
        if completed_workflows:
            durations = []
            for w in completed_workflows:
                if w.get('completed_at') and w.get('started_at'):
                    duration = (w['completed_at'] - w['started_at']).days
                    durations.append(duration)
            avg_days = statistics.mean(durations) if durations else 0
        else:
            avg_days = 0
        
        # Overdue count
        overdue = await self.onboarding_collection.count_documents({
            "agency_id": agency_id,
            "status": {"$in": ["in_progress", "pending_review"]},
            "due_date": {"$lt": now}
        })
        
        return OnboardingStats(
            total_workflows=total,
            in_progress=in_progress,
            pending_review=pending,
            completed_this_month=completed_count,
            average_completion_days=round(avg_days, 1),
            overdue_count=overdue
        )
    
    # =========================
    # Contract Management
    # =========================
    
    async def create_contract(
        self,
        contract_type: ContractType,
        title: str,
        agency_id: str,
        created_by: str,
        parties: List[Dict[str, Any]],
        terms: Dict[str, Any],
        template_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Contract:
        """Create a new contract"""
        
        # Get clauses from template or use defaults
        if template_id:
            template = await self.contract_templates.find_one({"id": template_id})
            clauses_config = template.get('clauses', []) if template else []
        else:
            clauses_config = self._get_default_contract_clauses(contract_type)
        
        # Create clauses
        clauses = [ContractClause(**c) for c in clauses_config]
        
        # Create parties
        contract_parties = [ContractParty(**p) for p in parties]
        
        # Calculate total value from terms
        total_value = terms.get('compensation', {}).get('amount', 0)
        
        contract = Contract(
            contract_type=contract_type,
            title=title,
            agency_id=agency_id,
            created_by=created_by,
            parties=contract_parties,
            clauses=clauses,
            terms=terms,
            template_id=template_id,
            start_date=start_date,
            end_date=end_date,
            total_value=total_value,
            status=ContractStatus.DRAFT
        )
        
        await self.contracts_collection.insert_one(_serialize_for_mongo(contract))
        logger.info(f"Created contract {contract.contract_number}")
        
        return contract
    
    def _get_default_contract_clauses(self, contract_type: ContractType) -> List[Dict]:
        """Get default clauses for contract type"""
        base_clauses = [
            {
                "section": "General",
                "title": "Parties",
                "content": "This agreement is entered into by and between the parties listed herein.",
                "is_negotiable": False
            },
            {
                "section": "General",
                "title": "Term",
                "content": "This agreement shall commence on the start date and continue until the end date specified.",
                "is_negotiable": True
            },
            {
                "section": "Compensation",
                "title": "Payment Terms",
                "content": "Compensation shall be paid according to the terms specified in the agreement.",
                "is_negotiable": True
            },
            {
                "section": "Legal",
                "title": "Governing Law",
                "content": "This agreement shall be governed by the laws of the State of [State].",
                "is_negotiable": False
            },
            {
                "section": "Legal",
                "title": "Termination",
                "content": "Either party may terminate this agreement with 30 days written notice.",
                "is_negotiable": True
            }
        ]
        
        if contract_type == ContractType.EXCLUSIVE_REPRESENTATION:
            base_clauses.extend([
                {
                    "section": "Exclusivity",
                    "title": "Exclusive Rights",
                    "content": "Agency shall have exclusive rights to represent talent for all bookings and engagements.",
                    "is_negotiable": True
                },
                {
                    "section": "Commission",
                    "title": "Commission Rate",
                    "content": "Agency commission shall be [X]% of all gross earnings.",
                    "is_negotiable": True
                }
            ])
        
        return base_clauses
    
    async def update_contract_status(
        self,
        contract_id: str,
        status: ContractStatus,
        updated_by: str
    ) -> Contract:
        """Update contract status"""
        
        update_data = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.contracts_collection.update_one(
            {"id": contract_id},
            {"$set": update_data}
        )
        
        contract_doc = await self.contracts_collection.find_one({"id": contract_id})
        return Contract(**contract_doc) if contract_doc else None
    
    async def sign_contract(
        self,
        contract_id: str,
        party_id: str,
        signature_ip: str
    ) -> Contract:
        """Record a party's signature on a contract"""
        
        contract_doc = await self.contracts_collection.find_one({"id": contract_id})
        if not contract_doc:
            raise ValueError(f"Contract {contract_id} not found")
        
        parties = contract_doc.get('parties', [])
        all_signed = True
        
        for party in parties:
            if party['party_id'] == party_id:
                party['signed'] = True
                party['signed_at'] = datetime.now(timezone.utc)
                party['signature_ip'] = signature_ip
            
            if party.get('role') == 'signer' and not party.get('signed'):
                all_signed = False
        
        # Update status if all signers have signed
        new_status = ContractStatus.ACTIVE.value if all_signed else contract_doc['status']
        
        await self.contracts_collection.update_one(
            {"id": contract_id},
            {"$set": {
                "parties": parties,
                "status": new_status,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        updated_doc = await self.contracts_collection.find_one({"id": contract_id})
        return Contract(**updated_doc)
    
    async def get_contracts(
        self,
        agency_id: str,
        status: Optional[str] = None,
        contract_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Contract]:
        """Get contracts for an agency"""
        
        query = {"agency_id": agency_id}
        if status:
            query['status'] = status
        if contract_type:
            query['contract_type'] = contract_type
        
        cursor = self.contracts_collection.find(query).sort('created_at', -1).limit(limit)
        contracts = await cursor.to_list(length=limit)
        
        return [Contract(**c) for c in contracts]
    
    async def get_contract_stats(self, agency_id: str) -> ContractStats:
        """Get contract statistics for an agency"""
        
        now = datetime.now(timezone.utc)
        expiry_threshold = now + timedelta(days=30)
        
        # Count totals
        total = await self.contracts_collection.count_documents({"agency_id": agency_id})
        active = await self.contracts_collection.count_documents({
            "agency_id": agency_id,
            "status": "active"
        })
        pending = await self.contracts_collection.count_documents({
            "agency_id": agency_id,
            "status": "pending_signature"
        })
        
        # Expiring soon
        expiring = await self.contracts_collection.count_documents({
            "agency_id": agency_id,
            "status": "active",
            "end_date": {"$lte": expiry_threshold, "$gt": now}
        })
        
        # Total value of active contracts
        pipeline = [
            {"$match": {"agency_id": agency_id, "status": "active"}},
            {"$group": {"_id": None, "total": {"$sum": "$total_value"}}}
        ]
        value_result = await self.contracts_collection.aggregate(pipeline).to_list(length=1)
        total_value = value_result[0]['total'] if value_result else 0
        
        return ContractStats(
            total_contracts=total,
            active_contracts=active,
            pending_signature=pending,
            expiring_soon=expiring,
            total_contract_value=total_value
        )
    
    # =========================
    # Booking Management
    # =========================
    
    async def create_booking(
        self,
        booking_type: BookingType,
        agency_id: str,
        talent_id: str,
        talent_name: str,
        client_id: str,
        client_name: str,
        title: str,
        start_datetime: datetime,
        end_datetime: datetime,
        rate: float,
        rate_type: str = "hourly",
        commission_percentage: float = 20.0,
        description: str = None,
        location: str = None,
        requirements: List[str] = None
    ) -> Booking:
        """Create a new booking"""
        
        # Calculate fees
        if rate_type == "hourly":
            hours = (end_datetime - start_datetime).total_seconds() / 3600
            total_fee = rate * hours
        elif rate_type == "daily":
            days = max(1, (end_datetime - start_datetime).days)
            total_fee = rate * days
        else:
            total_fee = rate
        
        agency_commission = total_fee * (commission_percentage / 100)
        talent_payout = total_fee - agency_commission
        
        booking = Booking(
            booking_type=booking_type,
            agency_id=agency_id,
            talent_id=talent_id,
            talent_name=talent_name,
            client_id=client_id,
            client_name=client_name,
            title=title,
            description=description,
            location=location,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            rate=rate,
            rate_type=rate_type,
            total_fee=total_fee,
            agency_commission=agency_commission,
            commission_percentage=commission_percentage,
            talent_payout=talent_payout,
            requirements=requirements or [],
            status=BookingStatus.PENDING_CONFIRMATION
        )
        
        await self.bookings_collection.insert_one(_serialize_for_mongo(booking))
        logger.info(f"Created booking {booking.booking_number}")
        
        # Create alert for talent
        await self._create_alert(
            agency_id=agency_id,
            alert_type="new_booking",
            severity=AlertSeverity.MEDIUM,
            title=f"New Booking: {title}",
            message=f"New {booking_type.value} booking with {client_name} on {start_datetime.strftime('%b %d, %Y')}",
            related_entity_type="booking",
            related_entity_id=booking.id
        )
        
        return booking
    
    async def update_booking_status(
        self,
        booking_id: str,
        status: BookingStatus,
        notes: str = None,
        cancellation_reason: str = None
    ) -> Booking:
        """Update booking status"""
        
        update_data = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if status == BookingStatus.CONFIRMED:
            update_data['confirmed_at'] = datetime.now(timezone.utc)
        elif status == BookingStatus.COMPLETED:
            update_data['completed_at'] = datetime.now(timezone.utc)
        elif status == BookingStatus.CANCELLED:
            update_data['cancelled_at'] = datetime.now(timezone.utc)
            update_data['cancellation_reason'] = cancellation_reason
        
        if notes:
            update_data['notes'] = notes
        
        await self.bookings_collection.update_one(
            {"id": booking_id},
            {"$set": update_data}
        )
        
        booking_doc = await self.bookings_collection.find_one({"id": booking_id})
        return Booking(**booking_doc) if booking_doc else None
    
    async def get_bookings(
        self,
        agency_id: str,
        talent_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Booking]:
        """Get bookings for an agency"""
        
        query = {"agency_id": agency_id}
        if talent_id:
            query['talent_id'] = talent_id
        if status:
            query['status'] = status
        if start_date:
            query['start_datetime'] = {"$gte": start_date}
        if end_date:
            query.setdefault('start_datetime', {})['$lte'] = end_date
        
        cursor = self.bookings_collection.find(query).sort('start_datetime', -1).limit(limit)
        bookings = await cursor.to_list(length=limit)
        
        return [Booking(**b) for b in bookings]
    
    async def get_booking_stats(self, agency_id: str) -> BookingStats:
        """Get booking statistics for an agency"""
        
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Count by status
        total = await self.bookings_collection.count_documents({"agency_id": agency_id})
        confirmed = await self.bookings_collection.count_documents({
            "agency_id": agency_id,
            "status": "confirmed"
        })
        pending = await self.bookings_collection.count_documents({
            "agency_id": agency_id,
            "status": {"$in": ["inquiry", "pending_confirmation"]}
        })
        
        # Completed this month
        completed_this_month = await self.bookings_collection.count_documents({
            "agency_id": agency_id,
            "status": "completed",
            "completed_at": {"$gte": month_start}
        })
        
        # Revenue this month
        pipeline = [
            {"$match": {
                "agency_id": agency_id,
                "status": "completed",
                "completed_at": {"$gte": month_start}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$total_fee"}}}
        ]
        revenue_result = await self.bookings_collection.aggregate(pipeline).to_list(length=1)
        monthly_revenue = revenue_result[0]['total'] if revenue_result else 0
        
        # Average booking value
        avg_pipeline = [
            {"$match": {"agency_id": agency_id, "status": "completed"}},
            {"$group": {"_id": None, "avg": {"$avg": "$total_fee"}}}
        ]
        avg_result = await self.bookings_collection.aggregate(avg_pipeline).to_list(length=1)
        avg_value = avg_result[0]['avg'] if avg_result else 0
        
        return BookingStats(
            total_bookings=total,
            confirmed_bookings=confirmed,
            pending_bookings=pending,
            completed_this_month=completed_this_month,
            total_revenue_this_month=monthly_revenue,
            average_booking_value=round(avg_value, 2)
        )
    
    # =========================
    # KPI & Analytics
    # =========================
    
    async def calculate_agency_kpis(self, agency_id: str, period: str = "month") -> AgencyKPIDashboard:
        """Calculate comprehensive KPIs for an agency"""
        
        now = datetime.now(timezone.utc)
        
        # Determine period dates
        if period == "month":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = now
        elif period == "quarter":
            quarter_month = ((now.month - 1) // 3) * 3 + 1
            period_start = now.replace(month=quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = now
        else:  # year
            period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = now
        
        # Get booking stats
        booking_stats = await self.get_booking_stats(agency_id)
        
        # Revenue calculations
        revenue_pipeline = [
            {"$match": {
                "agency_id": agency_id,
                "status": "completed",
                "completed_at": {"$gte": period_start, "$lte": period_end}
            }},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_fee"},
                "total_commission": {"$sum": "$agency_commission"},
                "count": {"$sum": 1}
            }}
        ]
        revenue_result = await self.bookings_collection.aggregate(revenue_pipeline).to_list(length=1)
        revenue_data = revenue_result[0] if revenue_result else {"total_revenue": 0, "total_commission": 0, "count": 0}
        
        # Talent metrics
        talent_pipeline = [
            {"$match": {"agency_id": agency_id}},
            {"$group": {"_id": "$talent_id"}},
            {"$count": "total"}
        ]
        talent_result = await self.bookings_collection.aggregate(talent_pipeline).to_list(length=1)
        active_talent = talent_result[0]['total'] if talent_result else 0
        
        # Client metrics
        client_pipeline = [
            {"$match": {"agency_id": agency_id}},
            {"$group": {"_id": "$client_id"}},
            {"$count": "total"}
        ]
        client_result = await self.bookings_collection.aggregate(client_pipeline).to_list(length=1)
        active_clients = client_result[0]['total'] if client_result else 0
        
        # Top performers
        top_talent_pipeline = [
            {"$match": {"agency_id": agency_id, "status": "completed"}},
            {"$group": {
                "_id": {"talent_id": "$talent_id", "talent_name": "$talent_name"},
                "total_revenue": {"$sum": "$total_fee"},
                "booking_count": {"$sum": 1}
            }},
            {"$sort": {"total_revenue": -1}},
            {"$limit": 5}
        ]
        top_talents = await self.bookings_collection.aggregate(top_talent_pipeline).to_list(length=5)
        
        # Create metrics list
        metrics = [
            KPIMetric(
                name="Total Revenue",
                category=KPICategory.REVENUE,
                value=revenue_data['total_revenue'],
                target=100000,
                unit="$",
                period=period,
                period_start=period_start,
                period_end=period_end
            ),
            KPIMetric(
                name="Total Bookings",
                category=KPICategory.BOOKINGS,
                value=revenue_data['count'],
                target=50,
                unit="count",
                period=period,
                period_start=period_start,
                period_end=period_end
            ),
            KPIMetric(
                name="Active Talent",
                category=KPICategory.TALENT,
                value=active_talent,
                target=100,
                unit="count",
                period=period,
                period_start=period_start,
                period_end=period_end
            )
        ]
        
        return AgencyKPIDashboard(
            agency_id=agency_id,
            period=period,
            period_start=period_start,
            period_end=period_end,
            total_revenue=revenue_data['total_revenue'],
            revenue_target=100000,
            revenue_achievement=revenue_data['total_revenue'] / 100000 * 100 if revenue_data['total_revenue'] else 0,
            gross_margin=revenue_data['total_commission'] / revenue_data['total_revenue'] * 100 if revenue_data['total_revenue'] else 20,
            total_bookings=revenue_data['count'],
            booking_target=50,
            average_booking_value=revenue_data['total_revenue'] / revenue_data['count'] if revenue_data['count'] else 0,
            booking_conversion_rate=65.0,  # Would need inquiry tracking
            active_talent=active_talent,
            talent_utilization_rate=75.0,  # Would need availability tracking
            average_talent_revenue=revenue_data['total_revenue'] / active_talent if active_talent else 0,
            active_clients=active_clients,
            client_retention_rate=85.0,  # Would need historical tracking
            average_client_spend=revenue_data['total_revenue'] / active_clients if active_clients else 0,
            top_talents=[
                {"talent_id": t['_id']['talent_id'], "name": t['_id']['talent_name'], 
                 "revenue": t['total_revenue'], "bookings": t['booking_count']}
                for t in top_talents
            ],
            metrics=metrics
        )
    
    async def get_talent_performance(
        self,
        agency_id: str,
        talent_id: str,
        period: str = "month"
    ) -> TalentPerformance:
        """Get performance metrics for a specific talent"""
        
        now = datetime.now(timezone.utc)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get bookings for talent
        bookings = await self.bookings_collection.find({
            "agency_id": agency_id,
            "talent_id": talent_id,
            "start_datetime": {"$gte": period_start}
        }).to_list(length=1000)
        
        total_bookings = len(bookings)
        completed = sum(1 for b in bookings if b.get('status') == 'completed')
        cancelled = sum(1 for b in bookings if b.get('status') == 'cancelled')
        total_revenue = sum(b.get('total_fee', 0) for b in bookings if b.get('status') == 'completed')
        
        # Get unique clients
        clients = set(b.get('client_id') for b in bookings)
        
        # Get talent name from most recent booking
        talent_name = bookings[0].get('talent_name', 'Unknown') if bookings else 'Unknown'
        
        return TalentPerformance(
            talent_id=talent_id,
            talent_name=talent_name,
            agency_id=agency_id,
            period=period,
            period_start=period_start,
            period_end=now,
            total_bookings=total_bookings,
            completed_bookings=completed,
            cancelled_bookings=cancelled,
            booking_completion_rate=completed / total_bookings * 100 if total_bookings else 0,
            total_revenue=total_revenue,
            average_booking_value=total_revenue / completed if completed else 0,
            unique_clients=len(clients),
            performance_score=min(100, (completed * 10) + (total_revenue / 1000))
        )
    
    # =========================
    # Revenue Forecasting
    # =========================
    
    async def generate_revenue_forecast(
        self,
        agency_id: str,
        forecast_period: str = "monthly",
        months_ahead: int = 3
    ) -> RevenueForecast:
        """Generate revenue forecast based on historical data"""
        
        now = datetime.now(timezone.utc)
        
        # Get historical data (last 6 months)
        six_months_ago = now - timedelta(days=180)
        
        historical_pipeline = [
            {"$match": {
                "agency_id": agency_id,
                "status": "completed",
                "completed_at": {"$gte": six_months_ago}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$completed_at"},
                    "month": {"$month": "$completed_at"}
                },
                "revenue": {"$sum": "$total_fee"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        historical = await self.bookings_collection.aggregate(historical_pipeline).to_list(length=12)
        
        if historical:
            revenues = [h['revenue'] for h in historical]
            avg_revenue = statistics.mean(revenues)
            std_dev = statistics.stdev(revenues) if len(revenues) > 1 else avg_revenue * 0.2
            
            # Apply growth factor
            growth_factor = 1.05  # 5% assumed growth
            predicted = avg_revenue * growth_factor
        else:
            # Default forecast if no historical data
            predicted = 50000
            std_dev = 10000
            avg_revenue = 50000
            growth_factor = 1.0
        
        # Seasonal adjustments
        current_month = now.month
        seasonal_factors = {
            1: 0.8, 2: 0.85, 3: 0.95, 4: 1.0, 5: 1.05, 6: 1.1,
            7: 0.9, 8: 0.85, 9: 1.1, 10: 1.15, 11: 1.1, 12: 0.95
        }
        seasonal_factor = seasonal_factors.get(current_month, 1.0)
        
        predicted_revenue = predicted * seasonal_factor
        confidence = min(0.95, 0.6 + (len(historical) * 0.05))
        
        # Calculate bounds
        lower_bound = max(0, predicted_revenue - (2 * std_dev))
        upper_bound = predicted_revenue + (2 * std_dev)
        
        # Breakdown by type
        type_breakdown = {
            "photoshoot": predicted_revenue * 0.35,
            "runway": predicted_revenue * 0.25,
            "commercial": predicted_revenue * 0.20,
            "editorial": predicted_revenue * 0.15,
            "other": predicted_revenue * 0.05
        }
        
        period_end = now + timedelta(days=30 * months_ahead)
        
        forecast = RevenueForecast(
            agency_id=agency_id,
            forecast_period=forecast_period,
            period_start=now,
            period_end=period_end,
            predicted_revenue=round(predicted_revenue, 2),
            confidence_level=confidence,
            lower_bound=round(lower_bound, 2),
            upper_bound=round(upper_bound, 2),
            by_booking_type=type_breakdown,
            seasonal_factor=seasonal_factor,
            growth_factor=growth_factor,
            market_factor=1.0,
            model_type="statistical",
            model_accuracy=confidence * 100,
            assumptions=[
                f"Based on {len(historical)} months of historical data",
                f"Assumes {(growth_factor - 1) * 100:.0f}% growth trend",
                f"Seasonal adjustment: {seasonal_factor:.2f}x"
            ],
            risks=[
                "Economic downturn could reduce bookings",
                "Key talent departures may impact revenue",
                "Client concentration risk"
            ],
            opportunities=[
                "New market expansion potential",
                "Digital/virtual bookings growth",
                "Premium tier talent acquisition"
            ]
        )
        
        # Store forecast
        await self.revenue_forecasts.insert_one(_serialize_for_mongo(forecast))
        
        return forecast
    
    # =========================
    # Alerts & Automation
    # =========================
    
    async def _create_alert(
        self,
        agency_id: str,
        alert_type: str,
        severity: AlertSeverity,
        title: str,
        message: str,
        related_entity_type: str,
        related_entity_id: str
    ) -> WorkflowAlert:
        """Create a workflow alert"""
        
        alert = WorkflowAlert(
            agency_id=agency_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        
        await self.alerts_collection.insert_one(_serialize_for_mongo(alert))
        return alert
    
    async def get_alerts(
        self,
        agency_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[WorkflowAlert]:
        """Get alerts for an agency"""
        
        query = {"agency_id": agency_id, "is_dismissed": False}
        if unread_only:
            query['is_read'] = False
        
        cursor = self.alerts_collection.find(query).sort('created_at', -1).limit(limit)
        alerts = await cursor.to_list(length=limit)
        
        return [WorkflowAlert(**a) for a in alerts]
    
    async def mark_alert_read(self, alert_id: str) -> bool:
        """Mark an alert as read"""
        result = await self.alerts_collection.update_one(
            {"id": alert_id},
            {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss an alert"""
        result = await self.alerts_collection.update_one(
            {"id": alert_id},
            {"$set": {"is_dismissed": True}}
        )
        return result.modified_count > 0
    
    # =========================
    # Dashboard
    # =========================
    
    async def get_automation_dashboard(self, agency_id: str) -> AutomationDashboard:
        """Get comprehensive automation dashboard"""
        
        onboarding_stats = await self.get_onboarding_stats(agency_id)
        contract_stats = await self.get_contract_stats(agency_id)
        booking_stats = await self.get_booking_stats(agency_id)
        recent_alerts = await self.get_alerts(agency_id, limit=10)
        kpi_summary = await self.calculate_agency_kpis(agency_id)
        
        # Get upcoming deadlines
        now = datetime.now(timezone.utc)
        upcoming_threshold = now + timedelta(days=7)
        
        # Contracts expiring soon
        expiring_contracts = await self.contracts_collection.find({
            "agency_id": agency_id,
            "status": "active",
            "end_date": {"$lte": upcoming_threshold, "$gt": now}
        }).to_list(length=10)
        
        # Upcoming bookings
        upcoming_bookings = await self.bookings_collection.find({
            "agency_id": agency_id,
            "status": "confirmed",
            "start_datetime": {"$lte": upcoming_threshold, "$gt": now}
        }).to_list(length=10)
        
        deadlines = []
        for c in expiring_contracts:
            deadlines.append({
                "type": "contract_expiry",
                "title": f"Contract expiring: {c['title']}",
                "date": c['end_date'],
                "entity_id": c['id']
            })
        for b in upcoming_bookings:
            deadlines.append({
                "type": "booking",
                "title": f"Booking: {b['title']}",
                "date": b['start_datetime'],
                "entity_id": b['id']
            })
        
        deadlines.sort(key=lambda x: x['date'])
        
        try:
            revenue_forecast = await self.generate_revenue_forecast(agency_id)
        except Exception:
            revenue_forecast = None
        
        return AutomationDashboard(
            agency_id=agency_id,
            onboarding_stats=onboarding_stats,
            contract_stats=contract_stats,
            booking_stats=booking_stats,
            recent_alerts=recent_alerts,
            upcoming_deadlines=deadlines[:10],
            kpi_summary=kpi_summary,
            revenue_forecast=revenue_forecast
        )


# Global service instance
automation_service: Optional[AgencySuccessAutomationService] = None


def initialize_automation_service(db: AsyncIOMotorDatabase) -> AgencySuccessAutomationService:
    """Initialize the automation service"""
    global automation_service
    automation_service = AgencySuccessAutomationService(db)
    logger.info("Agency Success Automation service initialized")
    return automation_service
