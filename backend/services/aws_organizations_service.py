"""
AWS Organizations Service - Uses new State field (Sept 2025 update)
Provides account lifecycle management using granular State tracking
Deprecation Note: Status field will be removed Sept 9, 2026
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta
import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from aws_organizations_models import (
    AWSOrganizationAccount,
    AccountState,
    AccountStateChange,
    AccountStateSeverity,
    OrganizationSummary,
    StateMonitoringConfig
)

logger = logging.getLogger(__name__)


class AWSOrganizationsService:
    """Service for AWS Organizations with State field support"""
    
    def __init__(self, mongo_db=None):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.mongo_db = mongo_db
        
        # Initialize Organizations client
        try:
            self.org_client = boto3.client(
                'organizations',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region_name
            )
            
            # Verify access
            self._verify_organizations_access()
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Error initializing AWS Organizations client: {str(e)}")
            self.org_client = None
    
    def _verify_organizations_access(self):
        """Verify access to AWS Organizations"""
        try:
            self.org_client.describe_organization()
            logger.info("AWS Organizations access verified")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWSOrganizationsNotInUseException':
                logger.warning("AWS Organizations is not enabled for this account")
            else:
                logger.error(f"Error accessing AWS Organizations: {str(e)}")
            raise
    
    def _get_state_severity(self, state: AccountState) -> AccountStateSeverity:
        """Determine severity level for account state"""
        if state in [AccountState.SUSPENDED, AccountState.CLOSED]:
            return AccountStateSeverity.CRITICAL
        elif state == AccountState.PENDING_CLOSURE:
            return AccountStateSeverity.WARNING
        else:
            return AccountStateSeverity.NORMAL
    
    async def list_all_accounts(self) -> List[AWSOrganizationAccount]:
        """List all accounts in organization using new State field"""
        try:
            if not self.org_client:
                raise Exception("Organizations client not initialized")
            
            accounts = []
            paginator = self.org_client.get_paginator('list_accounts')
            
            # Get organization ID
            org_info = self.org_client.describe_organization()
            org_id = org_info['Organization']['Id']
            
            for page in paginator.paginate():
                for account in page['Accounts']:
                    # Use new State field (introduced Sept 2025)
                    account_state = account.get('State', 'ACTIVE')  # Default to ACTIVE if not present
                    
                    # Get parent OU info
                    parent_info = await self._get_account_parent(account['Id'])
                    
                    accounts.append(AWSOrganizationAccount(
                        id=account['Id'],
                        arn=account['Arn'],
                        email=account['Email'],
                        name=account['Name'],
                        state=AccountState(account_state),
                        joined_method=account.get('JoinedMethod'),
                        joined_timestamp=account.get('JoinedTimestamp'),
                        organization_id=org_id,
                        parent_ou_id=parent_info.get('id'),
                        parent_ou_name=parent_info.get('name')
                    ))
            
            logger.info(f"Retrieved {len(accounts)} accounts from AWS Organizations")
            return accounts
            
        except Exception as e:
            logger.error(f"Error listing accounts: {str(e)}")
            raise
    
    async def _get_account_parent(self, account_id: str) -> Dict[str, str]:
        """Get parent organizational unit for account"""
        try:
            response = self.org_client.list_parents(ChildId=account_id)
            if response['Parents']:
                parent = response['Parents'][0]
                parent_id = parent['Id']
                
                # Get parent name if it's an OU
                if parent['Type'] == 'ORGANIZATIONAL_UNIT':
                    ou_info = self.org_client.describe_organizational_unit(OrganizationalUnitId=parent_id)
                    return {'id': parent_id, 'name': ou_info['OrganizationalUnit']['Name']}
                else:
                    return {'id': parent_id, 'name': 'Root'}
            
            return {'id': None, 'name': None}
            
        except Exception as e:
            logger.warning(f"Could not get parent for account {account_id}: {str(e)}")
            return {'id': None, 'name': None}
    
    async def get_account_by_id(self, account_id: str) -> Optional[AWSOrganizationAccount]:
        """Get specific account details using new State field"""
        try:
            if not self.org_client:
                raise Exception("Organizations client not initialized")
            
            response = self.org_client.describe_account(AccountId=account_id)
            account = response['Account']
            
            # Get organization ID
            org_info = self.org_client.describe_organization()
            org_id = org_info['Organization']['Id']
            
            # Get parent OU info
            parent_info = await self._get_account_parent(account_id)
            
            # Use new State field
            account_state = account.get('State', 'ACTIVE')
            
            return AWSOrganizationAccount(
                id=account['Id'],
                arn=account['Arn'],
                email=account['Email'],
                name=account['Name'],
                state=AccountState(account_state),
                joined_method=account.get('JoinedMethod'),
                joined_timestamp=account.get('JoinedTimestamp'),
                organization_id=org_id,
                parent_ou_id=parent_info.get('id'),
                parent_ou_name=parent_info.get('name')
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccountNotFoundException':
                return None
            logger.error(f"Error getting account {account_id}: {str(e)}")
            raise
    
    async def get_accounts_by_state(self, state: AccountState) -> List[AWSOrganizationAccount]:
        """Get all accounts in a specific state"""
        all_accounts = await self.list_all_accounts()
        return [acc for acc in all_accounts if acc.state == state]
    
    async def get_critical_accounts(self) -> List[AWSOrganizationAccount]:
        """Get accounts in critical states (SUSPENDED, CLOSED)"""
        all_accounts = await self.list_all_accounts()
        return [
            acc for acc in all_accounts 
            if acc.state in [AccountState.SUSPENDED, AccountState.CLOSED]
        ]
    
    async def get_organization_summary(self) -> OrganizationSummary:
        """Get summary of organization account states"""
        try:
            accounts = await self.list_all_accounts()
            
            # Get organization ID
            org_info = self.org_client.describe_organization()
            org_id = org_info['Organization']['Id']
            
            # Count by state
            state_counts = {}
            for state in AccountState:
                state_counts[state.value] = sum(1 for acc in accounts if acc.state == state)
            
            return OrganizationSummary(
                organization_id=org_id,
                total_accounts=len(accounts),
                accounts_by_state=state_counts,
                critical_accounts=state_counts.get(AccountState.SUSPENDED.value, 0) + 
                                state_counts.get(AccountState.CLOSED.value, 0),
                warning_accounts=state_counts.get(AccountState.PENDING_CLOSURE.value, 0),
                active_accounts=state_counts.get(AccountState.ACTIVE.value, 0),
                pending_activation=state_counts.get(AccountState.PENDING_ACTIVATION.value, 0)
            )
            
        except Exception as e:
            logger.error(f"Error generating organization summary: {str(e)}")
            raise
    
    async def track_state_change(self, account: AWSOrganizationAccount, previous_state: Optional[AccountState] = None):
        """Track account state change in database"""
        if not self.mongo_db:
            logger.warning("MongoDB not configured, skipping state tracking")
            return
        
        try:
            state_change = AccountStateChange(
                account_id=account.id,
                account_name=account.name,
                account_email=account.email,
                previous_state=previous_state,
                new_state=account.state,
                severity=self._get_state_severity(account.state)
            )
            
            await self.mongo_db.account_state_changes.insert_one(state_change.dict())
            logger.info(f"Tracked state change for account {account.id}: {previous_state} -> {account.state}")
            
        except Exception as e:
            logger.error(f"Error tracking state change: {str(e)}")
    
    async def get_state_history(self, account_id: Optional[str] = None, 
                               state: Optional[AccountState] = None,
                               limit: int = 100) -> List[AccountStateChange]:
        """Get state change history"""
        if not self.mongo_db:
            return []
        
        try:
            query = {}
            if account_id:
                query['account_id'] = account_id
            if state:
                query['new_state'] = state.value
            
            cursor = self.mongo_db.account_state_changes.find(query).sort('detected_at', -1).limit(limit)
            changes = await cursor.to_list(length=limit)
            
            return [AccountStateChange(**change) for change in changes]
            
        except Exception as e:
            logger.error(f"Error getting state history: {str(e)}")
            return []
    
    async def monitor_state_changes(self) -> List[AccountStateChange]:
        """Monitor for state changes since last check"""
        if not self.mongo_db:
            logger.warning("MongoDB not configured, cannot monitor state changes")
            return []
        
        try:
            # Get current accounts
            current_accounts = await self.list_all_accounts()
            
            # Get last known states from database
            last_states = {}
            cursor = self.mongo_db.account_state_changes.find().sort('detected_at', -1)
            async for change in cursor:
                account_id = change['account_id']
                if account_id not in last_states:
                    last_states[account_id] = AccountState(change['new_state'])
            
            # Detect changes
            changes = []
            for account in current_accounts:
                previous_state = last_states.get(account.id)
                
                # If state is different or this is a new account
                if previous_state != account.state:
                    await self.track_state_change(account, previous_state)
                    
                    changes.append(AccountStateChange(
                        account_id=account.id,
                        account_name=account.name,
                        account_email=account.email,
                        previous_state=previous_state,
                        new_state=account.state,
                        severity=self._get_state_severity(account.state)
                    ))
            
            if changes:
                logger.info(f"Detected {len(changes)} account state changes")
            
            return changes
            
        except Exception as e:
            logger.error(f"Error monitoring state changes: {str(e)}")
            return []


# Global service instance (will be initialized with MongoDB in server.py)
org_service: Optional[AWSOrganizationsService] = None


def initialize_service(mongo_db):
    """Initialize service with MongoDB connection"""
    global org_service
    try:
        org_service = AWSOrganizationsService(mongo_db=mongo_db)
        logger.info(f"AWS Organizations service initialized successfully: {org_service is not None}")
        return org_service
    except Exception as e:
        logger.error(f"Failed to initialize AWS Organizations service: {str(e)}")
        org_service = None
        return None
