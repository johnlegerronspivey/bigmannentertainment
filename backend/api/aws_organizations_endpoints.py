"""
AWS Organizations API Endpoints - State field management
Provides REST API for account lifecycle monitoring using new State field
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timezone

from aws_organizations_models import (
    AWSOrganizationAccount,
    AccountState,
    AccountStateChange,
    AccountStateSeverity,
    OrganizationSummary,
    StateMonitoringConfig,
    AccountStateHistoryQuery
)
import aws_organizations_service

router = APIRouter(prefix="/api/aws-organizations", tags=["AWS Organizations"])


@router.get("/health", response_model=dict)
async def health_check():
    """Check AWS Organizations service health"""
    org_service = aws_organizations_service.org_service
    if not org_service or not org_service.org_client:
        return {
            "status": "unavailable",
            "message": "AWS Organizations client not initialized. Check credentials."
        }
    
    try:
        org_info = org_service.org_client.describe_organization()
        return {
            "status": "healthy",
            "organization_id": org_info['Organization']['Id'],
            "message": "AWS Organizations service operational"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/accounts", response_model=List[AWSOrganizationAccount])
async def list_accounts(
    state: Optional[AccountState] = Query(None, description="Filter by account state"),
    severity: Optional[AccountStateSeverity] = Query(None, description="Filter by severity")
):
    """
    List all accounts in organization
    Uses new State field (PENDING_ACTIVATION, ACTIVE, SUSPENDED, PENDING_CLOSURE, CLOSED)
    """
    try:
        org_service = aws_organizations_service.org_service
        if not org_service:
            raise HTTPException(status_code=503, detail="AWS Organizations service not available")
        
        # Get all accounts
        if state:
            accounts = await org_service.get_accounts_by_state(state)
        else:
            accounts = await org_service.list_all_accounts()
        
        # Filter by severity if specified
        if severity:
            accounts = [
                acc for acc in accounts 
                if org_service._get_state_severity(acc.state) == severity
            ]
        
        return accounts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing accounts: {str(e)}")


@router.get("/accounts/{account_id}", response_model=AWSOrganizationAccount)
async def get_account(account_id: str):
    """Get specific account details by ID"""
    try:
        org_service = aws_organizations_service.org_service
        if not org_service:
            raise HTTPException(status_code=503, detail="AWS Organizations service not available")
        
        account = await org_service.get_account_by_id(account_id)
        
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
        
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting account: {str(e)}")


@router.get("/accounts/state/{state}", response_model=List[AWSOrganizationAccount])
async def get_accounts_by_state(state: AccountState):
    """Get all accounts in a specific state"""
    try:
        org_service = aws_organizations_service.org_service
        if not org_service:
            raise HTTPException(status_code=503, detail="AWS Organizations service not available")
        
        accounts = await org_service.get_accounts_by_state(state)
        return accounts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting accounts: {str(e)}")


@router.get("/accounts/critical", response_model=List[AWSOrganizationAccount])
async def get_critical_accounts():
    """Get accounts in critical states (SUSPENDED, CLOSED)"""
    try:
        org_service = aws_organizations_service.org_service
        if not org_service:
            raise HTTPException(status_code=503, detail="AWS Organizations service not available")
        
        critical_accounts = await org_service.get_critical_accounts()
        return critical_accounts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting critical accounts: {str(e)}")


@router.get("/summary", response_model=OrganizationSummary)
async def get_organization_summary():
    """Get summary of organization account states"""
    try:
        org_service = aws_organizations_service.org_service
        if not org_service:
            raise HTTPException(status_code=503, detail="AWS Organizations service not available")
        
        summary = await org_service.get_organization_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.get("/state-changes", response_model=List[AccountStateChange])
async def get_state_changes(
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    state: Optional[AccountState] = Query(None, description="Filter by state"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """Get account state change history"""
    try:
        if not org_service:
            raise HTTPException(status_code=503, detail="AWS Organizations service not available")
        
        changes = await org_service.get_state_history(
            account_id=account_id,
            state=state,
            limit=limit
        )
        
        return changes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting state changes: {str(e)}")


@router.post("/monitor", response_model=List[AccountStateChange])
async def monitor_state_changes():
    """
    Monitor for state changes since last check
    Compares current states with last known states and tracks changes
    """
    try:
        org_service = aws_organizations_service.org_service
        if not org_service:
            raise HTTPException(status_code=503, detail="AWS Organizations service not available")
        
        changes = await org_service.monitor_state_changes()
        
        return changes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error monitoring state changes: {str(e)}")


@router.get("/states/enum", response_model=dict)
async def get_state_enum():
    """Get all available account states and their descriptions"""
    return {
        "states": {
            "PENDING_ACTIVATION": {
                "value": "PENDING_ACTIVATION",
                "description": "Account created but not yet fully activated",
                "severity": "normal"
            },
            "ACTIVE": {
                "value": "ACTIVE",
                "description": "Account is operational and ready for use",
                "severity": "normal"
            },
            "SUSPENDED": {
                "value": "SUSPENDED",
                "description": "Account under AWS-enforced suspension",
                "severity": "critical"
            },
            "PENDING_CLOSURE": {
                "value": "PENDING_CLOSURE",
                "description": "Account with in-process closure request",
                "severity": "warning"
            },
            "CLOSED": {
                "value": "CLOSED",
                "description": "Account in 90-day reinstatement window",
                "severity": "critical"
            }
        },
        "deprecation_notice": "The Status field is deprecated and will be removed on September 9, 2026. Use State field instead."
    }


@router.get("/migration-info", response_model=dict)
async def get_migration_info():
    """Get information about Status -> State migration"""
    return {
        "migration": {
            "announcement_date": "2025-09-09",
            "deprecation_date": "2026-09-09",
            "status": "Both State and Status fields available until deprecation",
            "recommendation": "Update all code to use State field before September 9, 2026"
        },
        "field_changes": {
            "old_field": "Status",
            "new_field": "State",
            "reason": "Provides more granular account lifecycle visibility"
        },
        "api_endpoints_affected": [
            "DescribeAccount",
            "ListAccounts",
            "ListAccountsForParent",
            "ListDelegatedAdministrators"
        ]
    }
