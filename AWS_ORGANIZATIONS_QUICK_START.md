# AWS Organizations Quick Start Guide

## 🚀 Quick Access

### Dashboard URL
```
https://your-domain.com/aws-organizations
```

### API Base URL
```
http://your-backend/api/aws-organizations
```

## 📊 Current Organization Status

Your AWS Organization:
- **Organization ID**: `o-qz4sxadlt4`
- **Total Accounts**: 1
- **Active Accounts**: 1
- **Critical Accounts**: 0

## 🔑 Key Endpoints (Already Working!)

### 1. Check Service Health
```bash
curl http://localhost:8001/api/aws-organizations/health
```
Response:
```json
{
  "status": "healthy",
  "organization_id": "o-qz4sxadlt4",
  "message": "AWS Organizations service operational"
}
```

### 2. View Organization Summary
```bash
curl http://localhost:8001/api/aws-organizations/summary
```

### 3. List All Accounts
```bash
curl http://localhost:8001/api/aws-organizations/accounts
```

### 4. Get Critical Accounts (SUSPENDED/CLOSED)
```bash
curl http://localhost:8001/api/aws-organizations/accounts/critical
```

### 5. Monitor State Changes
```bash
curl -X POST http://localhost:8001/api/aws-organizations/monitor
```

## 📝 What's Working Now

✅ **Backend Services**
- AWS Organizations service initialized
- Connected to organization `o-qz4sxadlt4`
- All API endpoints functional
- State tracking in MongoDB ready

✅ **Frontend Dashboard**
- React component created
- Route configured at `/aws-organizations`
- Real-time data fetching
- State filtering and monitoring

✅ **Database**
- MongoDB collections created:
  - `account_state_changes` - Historical tracking
  - State monitoring configuration

## 🎯 Account States Monitored

| State | Count | Description |
|-------|-------|-------------|
| **ACTIVE** | 1 | ✓ Operational accounts |
| **PENDING_ACTIVATION** | 0 | ⏳ Being activated |
| **SUSPENDED** | 0 | ⚠️ Under AWS suspension |
| **PENDING_CLOSURE** | 0 | 🔒 Being closed |
| **CLOSED** | 0 | ✖ In reinstatement window |

## 🛠️ Testing Commands

### Test All Endpoints
```bash
# Health check
curl http://localhost:8001/api/aws-organizations/health | jq .

# Summary
curl http://localhost:8001/api/aws-organizations/summary | jq .

# List accounts
curl http://localhost:8001/api/aws-organizations/accounts | jq .

# Get state enum
curl http://localhost:8001/api/aws-organizations/states/enum | jq .

# Migration info
curl http://localhost:8001/api/aws-organizations/migration-info | jq .

# State changes history
curl http://localhost:8001/api/aws-organizations/state-changes | jq .

# Monitor for changes
curl -X POST http://localhost:8001/api/aws-organizations/monitor | jq .
```

## 📱 Using the Dashboard

1. **Navigate** to `/aws-organizations` in your browser
2. **View Overview** - See account distribution by state
3. **Browse Accounts** - Filter by state or severity
4. **Check History** - View all state transitions
5. **Monitor** - Check for state changes manually

### Dashboard Tabs

- **Overview**: Visual state distribution and organization info
- **Accounts**: Detailed account list with filters
- **State Changes**: Historical state transition log
- **Monitoring**: Manual state change detection

## 🔔 Alert Configuration

The system automatically tracks state changes for:
- ✅ All state transitions
- 🔴 Critical states: SUSPENDED, CLOSED
- 🟡 Warning states: PENDING_CLOSURE

## 📚 Documentation Files

1. **AWS_ORGANIZATIONS_GUIDE.md** - Complete feature documentation
2. **AWS_ORGANIZATIONS_QUICK_START.md** - This file
3. Backend files:
   - `aws_organizations_models.py` - Data models
   - `aws_organizations_service.py` - Core service
   - `aws_organizations_endpoints.py` - API routes
4. Frontend:
   - `AWSOrganizationsComponent.js` - Dashboard component

## 🎓 Next Steps

### Recommended Actions:

1. **Add More Accounts**
   - Create or invite accounts to your organization
   - Watch state transitions from PENDING_ACTIVATION → ACTIVE

2. **Set Up Monitoring**
   - Schedule regular state checks (cron job)
   - Configure alerts for critical states

3. **Integrate Notifications**
   - Add SNS topic for email alerts
   - Connect Slack webhook for team notifications

4. **Export Reports**
   - Query state changes for compliance
   - Generate monthly account lifecycle reports

### Optional Enhancements:

- [ ] Automated state monitoring (every 15 minutes)
- [ ] Email alerts for critical state changes
- [ ] Slack integration for real-time notifications
- [ ] CSV export of account data
- [ ] Custom alert rules
- [ ] Grafana dashboard integration

## 🐛 Troubleshooting

### Service Not Available
```bash
# Check credentials
env | grep AWS_

# Verify Organizations access
aws organizations describe-organization

# Check backend logs
tail -f /var/log/supervisor/backend.err.log | grep organizations
```

### No Accounts Showing
- Ensure you have accounts in your organization
- Check IAM permissions for ListAccounts
- Verify you're using management account credentials

### Frontend Not Loading
```bash
# Check if frontend is running
curl http://localhost:3000

# Restart frontend
sudo supervisorctl restart bme_services:frontend
```

## 📊 Current Account Details

Your account:
```json
{
  "id": "314108682794",
  "name": "John LeGerron Spivey",
  "email": "bigmannsaintjohn@yahoo.com",
  "state": "ACTIVE",
  "joined_method": "INVITED",
  "joined_timestamp": "2019-08-03T00:00:04.740000Z",
  "organization_id": "o-qz4sxadlt4",
  "parent_ou_name": "Root"
}
```

## ✨ Success Indicators

Your system is ready when you see:

✅ Backend:
```
INFO:aws_organizations_service:AWS Organizations access verified
INFO:aws_organizations_service:AWS Organizations service initialized successfully: True
```

✅ API Health:
```json
{"status": "healthy", "organization_id": "o-qz4sxadlt4"}
```

✅ Frontend: Dashboard loads with account data

## 🎉 Congratulations!

Your AWS Organizations Management System is fully operational and using the new **State field** (Sept 2025 update)!

You're ready for the Status field deprecation on **September 9, 2026**.

---

## 📢 Related AWS Updates

### AWS Config Natural Language Queries
**Deprecation**: January 15, 2026

If you need to query AWS resources using natural language:
- ✅ Use **Amazon Q Developer** instead
- ✅ Alternative: AWS Config SQL queries (free)
- ℹ️ See: `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md`

This BME platform does not use AWS Config natural language queries, so no action is required.
