"""
Agency Success Automation API Endpoints
REST API for automated onboarding, KPI tracking, contracts, and revenue forecasting
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from agency_success_automation_models import (
    OnboardingStatus, ContractStatus, ContractType, BookingStatus, BookingType,
    OnboardingWorkflow, OnboardingTemplate, Contract, ContractTemplate,
    Booking, TalentPerformance, AgencyKPIDashboard, RevenueForecast,
    WorkflowAlert, AutomationDashboard, OnboardingStats, ContractStats, BookingStats
)
import agency_success_automation_service

router = APIRouter(prefix="/api/agency-automation", tags=["Agency Success Automation"])


# =========================
# Request Models
# =========================

class CreateOnboardingRequest(BaseModel):
    talent_id: str
    talent_name: str
    talent_email: str
    agency_id: str
    template_id: Optional[str] = None
    assigned_to: Optional[str] = None


class UpdateOnboardingStepRequest(BaseModel):
    status: str
    data: Optional[dict] = None
    notes: Optional[str] = None
    completed_by: Optional[str] = None


class CreateContractRequest(BaseModel):
    contract_type: str
    title: str
    agency_id: str
    created_by: str
    parties: List[dict]
    terms: dict
    template_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SignContractRequest(BaseModel):
    party_id: str
    signature_ip: str


class CreateBookingRequest(BaseModel):
    booking_type: str
    agency_id: str
    talent_id: str
    talent_name: str
    client_id: str
    client_name: str
    title: str
    start_datetime: datetime
    end_datetime: datetime
    rate: float
    rate_type: str = "hourly"
    commission_percentage: float = 20.0
    description: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[List[str]] = None


class UpdateBookingStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


# =========================
# Health Check
# =========================

@router.get("/health")
async def health_check():
    """Check Agency Success Automation service health"""
    service = agency_success_automation_service.automation_service
    
    if not service:
        return {"status": "unavailable", "message": "Service not initialized"}
    
    return {
        "status": "healthy",
        "service": "Agency Success Automation",
        "features": [
            "Automated Talent Onboarding",
            "Contract Management",
            "Booking Automation",
            "KPI Dashboards",
            "Revenue Forecasting"
        ]
    }


# =========================
# Onboarding Endpoints
# =========================

@router.post("/onboarding", response_model=dict)
async def create_onboarding(request: CreateOnboardingRequest):
    """Create a new onboarding workflow for a talent"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        workflow = await service.create_onboarding_workflow(
            talent_id=request.talent_id,
            talent_name=request.talent_name,
            talent_email=request.talent_email,
            agency_id=request.agency_id,
            template_id=request.template_id,
            assigned_to=request.assigned_to
        )
        
        return workflow.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/onboarding", response_model=List[dict])
async def list_onboarding_workflows(
    agency_id: str = Query(...),
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    """List onboarding workflows for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        workflows = await service.get_onboarding_workflows(
            agency_id=agency_id,
            status=status,
            assigned_to=assigned_to,
            limit=limit
        )
        
        return [w.dict() for w in workflows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/onboarding/{workflow_id}/steps/{step_id}", response_model=dict)
async def update_onboarding_step(
    workflow_id: str,
    step_id: str,
    request: UpdateOnboardingStepRequest
):
    """Update a step in an onboarding workflow"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        workflow = await service.update_onboarding_step(
            workflow_id=workflow_id,
            step_id=step_id,
            status=OnboardingStatus(request.status),
            data=request.data,
            notes=request.notes,
            completed_by=request.completed_by
        )
        
        return workflow.dict()
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/onboarding/stats", response_model=dict)
async def get_onboarding_stats(agency_id: str = Query(...)):
    """Get onboarding statistics for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        stats = await service.get_onboarding_stats(agency_id)
        return stats.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Contract Endpoints
# =========================

@router.post("/contracts", response_model=dict)
async def create_contract(request: CreateContractRequest):
    """Create a new contract"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        contract = await service.create_contract(
            contract_type=ContractType(request.contract_type),
            title=request.title,
            agency_id=request.agency_id,
            created_by=request.created_by,
            parties=request.parties,
            terms=request.terms,
            template_id=request.template_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return contract.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts", response_model=List[dict])
async def list_contracts(
    agency_id: str = Query(...),
    status: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    """List contracts for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        contracts = await service.get_contracts(
            agency_id=agency_id,
            status=status,
            contract_type=contract_type,
            limit=limit
        )
        
        return [c.dict() for c in contracts]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/contracts/{contract_id}/status", response_model=dict)
async def update_contract_status(
    contract_id: str,
    status: str = Query(...),
    updated_by: str = Query(...)
):
    """Update contract status"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        contract = await service.update_contract_status(
            contract_id=contract_id,
            status=ContractStatus(status),
            updated_by=updated_by
        )
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return contract.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts/{contract_id}/sign", response_model=dict)
async def sign_contract(contract_id: str, request: SignContractRequest):
    """Sign a contract"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        contract = await service.sign_contract(
            contract_id=contract_id,
            party_id=request.party_id,
            signature_ip=request.signature_ip
        )
        
        return contract.dict()
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts/stats", response_model=dict)
async def get_contract_stats(agency_id: str = Query(...)):
    """Get contract statistics for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        stats = await service.get_contract_stats(agency_id)
        return stats.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Booking Endpoints
# =========================

@router.post("/bookings", response_model=dict)
async def create_booking(request: CreateBookingRequest):
    """Create a new booking"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        booking = await service.create_booking(
            booking_type=BookingType(request.booking_type),
            agency_id=request.agency_id,
            talent_id=request.talent_id,
            talent_name=request.talent_name,
            client_id=request.client_id,
            client_name=request.client_name,
            title=request.title,
            start_datetime=request.start_datetime,
            end_datetime=request.end_datetime,
            rate=request.rate,
            rate_type=request.rate_type,
            commission_percentage=request.commission_percentage,
            description=request.description,
            location=request.location,
            requirements=request.requirements
        )
        
        return booking.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings", response_model=List[dict])
async def list_bookings(
    agency_id: str = Query(...),
    talent_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500)
):
    """List bookings for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        bookings = await service.get_bookings(
            agency_id=agency_id,
            talent_id=talent_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return [b.dict() for b in bookings]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bookings/{booking_id}/status", response_model=dict)
async def update_booking_status(booking_id: str, request: UpdateBookingStatusRequest):
    """Update booking status"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        booking = await service.update_booking_status(
            booking_id=booking_id,
            status=BookingStatus(request.status),
            notes=request.notes,
            cancellation_reason=request.cancellation_reason
        )
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return booking.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings/stats", response_model=dict)
async def get_booking_stats(agency_id: str = Query(...)):
    """Get booking statistics for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        stats = await service.get_booking_stats(agency_id)
        return stats.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# KPI & Analytics Endpoints
# =========================

@router.get("/kpis", response_model=dict)
async def get_agency_kpis(
    agency_id: str = Query(...),
    period: str = Query("month", regex="^(month|quarter|year)$")
):
    """Get comprehensive KPIs for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        kpis = await service.calculate_agency_kpis(agency_id, period)
        return kpis.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/talent/{talent_id}", response_model=dict)
async def get_talent_performance(
    talent_id: str,
    agency_id: str = Query(...),
    period: str = Query("month", regex="^(month|quarter|year)$")
):
    """Get performance metrics for a specific talent"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        performance = await service.get_talent_performance(agency_id, talent_id, period)
        return performance.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Revenue Forecasting Endpoints
# =========================

@router.get("/forecast", response_model=dict)
async def get_revenue_forecast(
    agency_id: str = Query(...),
    forecast_period: str = Query("monthly", regex="^(monthly|quarterly|yearly)$"),
    months_ahead: int = Query(3, ge=1, le=12)
):
    """Generate revenue forecast for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        forecast = await service.generate_revenue_forecast(
            agency_id=agency_id,
            forecast_period=forecast_period,
            months_ahead=months_ahead
        )
        
        return forecast.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Alerts Endpoints
# =========================

@router.get("/alerts", response_model=List[dict])
async def list_alerts(
    agency_id: str = Query(...),
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100)
):
    """List alerts for an agency"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        alerts = await service.get_alerts(agency_id, unread_only, limit)
        return [a.dict() for a in alerts]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/alerts/{alert_id}/read", response_model=dict)
async def mark_alert_read(alert_id: str):
    """Mark an alert as read"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        success = await service.mark_alert_read(alert_id)
        return {"success": success}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alerts/{alert_id}", response_model=dict)
async def dismiss_alert(alert_id: str):
    """Dismiss an alert"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        success = await service.dismiss_alert(alert_id)
        return {"success": success}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Dashboard Endpoint
# =========================

@router.get("/dashboard", response_model=dict)
async def get_automation_dashboard(agency_id: str = Query(...)):
    """Get comprehensive automation dashboard"""
    try:
        service = agency_success_automation_service.automation_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        dashboard = await service.get_automation_dashboard(agency_id)
        return dashboard.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
