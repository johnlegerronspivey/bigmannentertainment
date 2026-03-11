# AWS Organizations Management System

## Overview

Complete AWS Organizations account lifecycle management system using the **new State field** introduced in September 2025. This system provides real-time monitoring, alerting, and historical tracking of account states across your organization.

## 📋 What's New: State Field Migration

### Background
- **Announcement Date**: September 9, 2025
- **Deprecation Date**: September 9, 2026
- **Change**: AWS Organizations introduced a new `State` field that replaces the old `Status` field

### Why the Change?
The new State field provides **more granular account lifecycle visibility** and enables better automation of account vending pipelines.

### Migration Status
- ✅ Both `State` and `Status` fields available until Sept 9, 2026
- ✅ This system uses only the new `State` field
- ⚠️ Update all code to use `State` before deprecation date

## 🔑 Account States

### Available States

| State | Description | Severity | Icon |
|-------|-------------|----------|------|
| `PENDING_ACTIVATION` | Account created but not yet fully activated | Normal | ⏳ |
| `ACTIVE` | Account operational and ready for use | Normal | ✓ |
| `SUSPENDED` | Account under AWS-enforced suspension | Critical | ⚠ |
| `PENDING_CLOSURE` | Account with in-process closure request | Warning | 🔒 |
| `CLOSED` | Account in 90-day reinstatement window | Critical | ✖ |

### Severity Levels

- **Normal**: `PENDING_ACTIVATION`, `ACTIVE`
- **Warning**: `PENDING_CLOSURE`
- **Critical**: `SUSPENDED`, `CLOSED`

## 🏗️ Architecture

### Backend Components

```
/app/backend/
├── aws_organizations_models.py      # Pydantic models for State management
├── aws_organizations_service.py     # Core service using boto3
└── aws_organizations_endpoints.py   # FastAPI REST API routes
```

### Frontend Components

```
/app/frontend/src/
└── AWSOrganizationsComponent.js    # React dashboard
```

### Database Collections

MongoDB collections for state tracking:
- `account_state_changes` - Historical state transitions
- `state_monitoring_config` - Monitoring configuration

## 🚀 Features

### 1. Real-Time Account Monitoring
- View all accounts in your organization
- Filter by state and severity
- Live state tracking

### 2. State Change Detection
- Automatic detection of state transitions
- Historical tracking in MongoDB
- Severity-based alerting

### 3. Organization Summary
- Total account count
- Distribution by state
- Critical/warning account counts

### 4. State History
- Complete audit trail of state changes
- Filterable by account, state, or date
- Export capabilities

## 📡 API Endpoints

### Health Check
```bash
GET /api/aws-organizations/health
```

### List Accounts
```bash
GET /api/aws-organizations/accounts
GET /api/aws-organizations/accounts?state=ACTIVE
GET /api/aws-organizations/accounts?severity=critical
```

### Get Specific Account
```bash
GET /api/aws-organizations/accounts/{account_id}
```

### Get Accounts by State
```bash
GET /api/aws-organizations/accounts/state/SUSPENDED
GET /api/aws-organizations/accounts/state/ACTIVE
```

### Get Critical Accounts
```bash
GET /api/aws-organizations/accounts/critical
```

### Organization Summary
```bash
GET /api/aws-organizations/summary
```

### State Change History
```bash
GET /api/aws-organizations/state-changes
GET /api/aws-organizations/state-changes?account_id=123456789012
GET /api/aws-organizations/state-changes?state=SUSPENDED&limit=50
```

### Monitor State Changes
```bash
POST /api/aws-organizations/monitor
```
Compares current states with last known states and detects changes.

### Get State Information
```bash
GET /api/aws-organizations/states/enum
GET /api/aws-organizations/migration-info
```

## 🔧 Setup

### Prerequisites

1. **AWS Credentials**
   - AWS Organizations access required
   - Must have `organizations:DescribeOrganization` permission
   - Must have `organizations:ListAccounts` permission
   - Must have `organizations:DescribeAccount` permission

2. **Environment Variables**
   ```bash
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1  # Or your preferred region
   ```

3. **AWS Organizations Enabled**
   - Your AWS account must have Organizations enabled
   - You must be in the management account

### Installation

The system is already integrated into the BME platform. No additional installation required.

### Accessing the Dashboard

1. Log in to BME platform
2. Navigate to: `https://your-domain.com/aws-organizations`
3. View your organization's account states

## 📊 Dashboard Features

### Overview Tab
- Visual distribution of account states
- Organization information
- Quick summary cards

### Accounts Tab
- Detailed account list
- Filter by state and severity
- Account information including:
  - Name, Email, Account ID
  - Current state with visual indicators
  - Organizational Unit (OU)
  - Join date

### State Changes Tab
- Historical state transitions
- Severity indicators
- Timeline of changes

### Monitoring Tab
- Manual state change detection
- Real-time comparison with database
- Alert on critical changes

## 🔔 Alerting

### Automatic Monitoring
State changes are automatically tracked when accounts are queried. The system:
1. Fetches current account states from AWS
2. Compares with last known states in MongoDB
3. Records any state transitions
4. Flags critical/warning state changes

### Critical State Alerts
The system highlights accounts in critical states:
- `SUSPENDED` - Immediate attention required
- `CLOSED` - Account in 90-day reinstatement window
- `PENDING_CLOSURE` - Account closure in progress

## 🛡️ Security

- Uses AWS IAM credentials
- MongoDB stores state history securely
- No sensitive data exposed in frontend
- API protected by authentication middleware

## 📈 Best Practices

### Regular Monitoring
1. **Daily**: Check for critical accounts
2. **Weekly**: Review state change history
3. **Monthly**: Analyze state distribution trends

### State Transitions to Watch
- `ACTIVE` → `SUSPENDED`: Immediate investigation required
- Any account → `PENDING_CLOSURE`: Review if intentional
- `CLOSED` accounts: Track 90-day reinstatement window

### Automation Tips
1. Set up scheduled monitoring checks
2. Integrate with SNS for email alerts
3. Use webhooks for Slack notifications
4. Export state history for compliance reporting

## 🔄 API Responses Affected

The following AWS Organizations API responses now include the `State` field:

1. **DescribeAccount**
   ```python
   response = org_client.describe_account(AccountId='123456789012')
   # New: response['Account']['State']
   # Old: response['Account']['Status'] (deprecated)
   ```

2. **ListAccounts**
   ```python
   response = org_client.list_accounts()
   # New: response['Accounts'][0]['State']
   # Old: response['Accounts'][0]['Status'] (deprecated)
   ```

3. **ListAccountsForParent**
   ```python
   response = org_client.list_accounts_for_parent(ParentId='ou-xxx')
   # New: response['Accounts'][0]['State']
   ```

4. **ListDelegatedAdministrators**
   ```python
   response = org_client.list_delegated_administrators(ServicePrincipal='xxx')
   # New: response['DelegatedAdministrators'][0]['State']
   ```

## 🧪 Testing

### Test API Endpoints

```bash
# Check service health
curl -X GET "${BACKEND_URL}/api/aws-organizations/health"

# List all accounts
curl -X GET "${BACKEND_URL}/api/aws-organizations/accounts"

# Get critical accounts
curl -X GET "${BACKEND_URL}/api/aws-organizations/accounts/critical"

# Get organization summary
curl -X GET "${BACKEND_URL}/api/aws-organizations/summary"

# Monitor state changes
curl -X POST "${BACKEND_URL}/api/aws-organizations/monitor"
```

### Test Frontend

1. Navigate to `/aws-organizations`
2. Verify account list loads
3. Test state filters
4. Check monitoring functionality
5. Review state change history

## 🐛 Troubleshooting

### Service Unavailable
**Error**: "AWS Organizations service not available"
**Solution**: 
1. Check AWS credentials in environment variables
2. Verify Organizations is enabled for your account
3. Ensure you're in the management account
4. Check IAM permissions

### No Accounts Showing
**Error**: Empty account list
**Solution**:
1. Verify you have accounts in your organization
2. Check `ListAccounts` permission
3. Review backend logs for API errors

### State Changes Not Recording
**Error**: State history is empty
**Solution**:
1. Verify MongoDB connection
2. Check `account_state_changes` collection
3. Run manual monitor check
4. Review service initialization logs

### AWS Organizations Not Enabled
**Error**: "AWSOrganizationsNotInUseException"
**Solution**:
1. Enable AWS Organizations in your account
2. Create an organization if needed
3. Ensure you're using the management account credentials

## 📚 Additional Resources

### AWS Organizations
- [AWS Organizations Documentation](https://docs.aws.amazon.com/organizations/)
- [AWS Account State Management](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_account_state.html)
- [AWS Blog: State Field Update](https://aws.amazon.com/blogs/mt/updates-to-account-status-information-in-aws-organizations/)

### Query Methods
- [Amazon Q Developer](https://aws.amazon.com/q/developer/) - For natural language queries about AWS resources
- **Note**: AWS Config natural language querying is being discontinued on January 15, 2026. See `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md` for migration guidance.

## 🔮 Future Enhancements

Planned features:
- [ ] SNS integration for real-time alerts
- [ ] Slack/Teams webhook notifications
- [ ] Automated remediation workflows
- [ ] Custom alert rules
- [ ] State change analytics dashboard
- [ ] Export to CSV/PDF reports
- [ ] Integration with AWS Control Tower
- [ ] Amazon Q Developer integration for natural language queries

**Note**: Consider using Amazon Q Developer for advanced querying capabilities. AWS Config's natural language query feature is being deprecated January 15, 2026. See `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md` for details.

## 📝 Migration Checklist

For teams migrating from Status to State field:

- [x] Update AWS Organizations service to use State field
- [x] Create models for new account states
- [x] Build REST API endpoints
- [x] Develop frontend dashboard
- [x] Implement state change tracking
- [x] Add monitoring capabilities
- [ ] Set up automated alerting (optional)
- [ ] Configure scheduled monitoring (optional)
- [ ] Update internal documentation
- [ ] Train team on new states

## 💡 Example Use Cases

### 1. Account Vending Pipeline
Monitor newly created accounts:
```python
pending_accounts = await org_service.get_accounts_by_state(AccountState.PENDING_ACTIVATION)
for account in pending_accounts:
    # Trigger activation workflow
    pass
```

### 2. Compliance Monitoring
Track suspended accounts:
```python
critical_accounts = await org_service.get_critical_accounts()
if critical_accounts:
    # Send alert to compliance team
    pass
```

### 3. Closure Management
Monitor accounts in closure process:
```python
closing_accounts = await org_service.get_accounts_by_state(AccountState.PENDING_CLOSURE)
# Track 90-day reinstatement window
```

### 4. Natural Language Queries with Amazon Q
For ad-hoc queries about your organization:
```python
# Using Amazon Q Developer for natural language queries
import boto3

q_client = boto3.client('q-developer')
response = q_client.query(
    query="Show me all accounts in PENDING_ACTIVATION state",
    context="AWS Organizations"
)

# Or use this system's REST API for programmatic access
import requests
accounts = requests.get('http://backend/api/aws-organizations/accounts?state=PENDING_ACTIVATION')
```

**Migration Note**: If you previously used AWS Config natural language queries, see `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md` for migration to Amazon Q Developer.

## 🎯 Summary

The AWS Organizations Management System provides:
- ✅ Full support for new State field
- ✅ Real-time account monitoring
- ✅ Historical state tracking
- ✅ Visual dashboard
- ✅ REST API
- ✅ Critical account alerts
- ✅ Future-proof architecture (ready for Sept 2026 deprecation)

**Your organization is now ready for the State field migration!**
