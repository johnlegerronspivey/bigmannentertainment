# Complete AWS Deployment Guide
## Step-by-Step Production Deployment

---

## 📋 Overview

This guide walks you through the complete AWS deployment process from credential setup to production deployment with monitoring.

**Deployment Flow:**
```
Setup → Initialize → Dev → Monitor → Staging → Production
```

**Time Estimate:** 2-3 hours for complete setup

---

## 🔐 Step 1: Configure AWS Credentials Securely

### Prerequisites
- AWS Account with admin access
- AWS CLI installed
- Terraform installed (v1.6.0+)
- Git configured

### Run Credential Setup

```bash
cd terraform/scripts
./setup-credentials.sh
```

**What This Does:**
1. Installs AWS CLI (if needed)
2. Configures AWS credentials
3. Tests credential validity
4. Optionally sets up MFA
5. Creates encrypted credential file
6. Generates GitHub Secrets guide
7. Creates local `.env.aws` file

**Output:**
- `~/.aws/credentials` - AWS credentials
- `backend/.env.aws` - Local environment variables
- `.aws_credentials_encrypted.gpg` - Team-shareable encrypted file

**Security Best Practices:**
- ✅ Enable MFA for production access
- ✅ Rotate credentials every 90 days
- ✅ Never commit credentials to Git
- ✅ Use separate IAM users per team member
- ✅ Apply least privilege permissions

### GitHub Secrets Setup

Add these secrets to your GitHub repository:

1. Go to: `Settings → Secrets and variables → Actions`
2. Click: `New repository secret`
3. Add:
   - `AWS_ACCESS_KEY_ID` - Your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
   - `SLACK_WEBHOOK_URL` - (Optional) For notifications
   - `INFRACOST_API_KEY` - (Optional) For cost estimates

---

## 🚀 Step 2: Initialize Terraform Backend

### Why Backend Initialization?

Remote state storage provides:
- **State Locking** - Prevents concurrent modifications
- **Team Collaboration** - Shared state across team
- **State History** - Versioning and rollback capability
- **Encryption** - Secure state storage

### Run Backend Initialization

```bash
cd terraform/scripts
./initialize-backend.sh
```

**What This Does:**
1. Creates S3 bucket for Terraform state
2. Enables versioning and encryption
3. Blocks public access
4. Creates DynamoDB table for locking
5. Configures backend in Terraform
6. Creates dev/staging/prod workspaces

**Created Resources:**
- S3 Bucket: `bme-agency-terraform-state`
- DynamoDB Table: `bme-agency-terraform-lock`
- Backend Config: `backend-config.hcl`

**Verification:**

```bash
# Check S3 bucket
aws s3 ls bme-agency-terraform-state

# Check DynamoDB table
aws dynamodb describe-table --table-name bme-agency-terraform-lock

# Verify Terraform init
cd ..
terraform workspace list
```

**Expected Output:**
```
* dev
  prod
  staging
```

---

## 🧪 Step 3: Deploy and Test in Dev Environment

### Development Deployment

```bash
cd terraform/scripts
./deploy-dev.sh
```

**Deployment Process:**

1. **Pre-Flight Checks** ✓
   - Backend initialization
   - Configuration validation
   - Workspace selection

2. **Validation** ✓
   - Terraform validate
   - Format check
   - Security scan (tfsec)

3. **Planning** ✓
   - Generate execution plan
   - Show change summary
   - Cost estimation

4. **Confirmation** ⚠️
   - Manual approval required
   - Review plan carefully

5. **Apply** 🚀
   - Execute changes
   - Create infrastructure
   - Save outputs

6. **Testing** ✅
   - Test CloudFront URL
   - Verify S3 bucket access
   - Check Cognito User Pool

**Deployment Time:** ~15-20 minutes

### Infrastructure Created (Dev)

| Resource | Purpose | Config |
|----------|---------|--------|
| S3 Bucket | Portfolio storage | No versioning (cost save) |
| CloudFront | CDN delivery | Basic config |
| DynamoDB | License registry | On-demand billing |
| Lambda | Metadata parser | 128MB memory |
| Cognito | User management | No MFA |
| QLDB | Dispute ledger | Standard mode |

### Testing Deployment

```bash
# Get outputs
cd ..
terraform output

# Test endpoints
CLOUDFRONT_URL=$(terraform output -raw cloudfront_domain_name)
curl -I https://$CLOUDFRONT_URL

# Test S3 access
S3_BUCKET=$(terraform output -raw portfolio_bucket_name)
aws s3 ls s3://$S3_BUCKET

# Test Cognito
COGNITO_POOL=$(terraform output -raw cognito_user_pool_id)
aws cognito-idp describe-user-pool --user-pool-id $COGNITO_POOL
```

### Common Issues & Solutions

**Issue:** Terraform init fails
```bash
# Solution: Check backend credentials
aws sts get-caller-identity

# Reinitialize
terraform init -reconfigure
```

**Issue:** Plan shows unexpected changes
```bash
# Solution: Check workspace
terraform workspace show

# Review state
terraform state list
```

**Issue:** Resource creation fails
```bash
# Solution: Check AWS service limits
aws service-quotas list-service-quotas --service-code s3

# Check CloudWatch logs
aws logs tail /aws/lambda/ImageMetadataParser --follow
```

---

## 📊 Step 4: Set Up Monitoring Dashboards

### CloudWatch Monitoring Setup

```bash
cd terraform/scripts
./setup-monitoring.sh dev
```

**What This Creates:**

1. **Main Dashboard**
   - S3 storage metrics
   - CloudFront performance
   - DynamoDB operations
   - Lambda invocations
   - Cognito authentication

2. **Cost Dashboard**
   - Estimated monthly charges
   - Service-level breakdown

3. **CloudWatch Alarms**
   - High error rate (>5%)
   - DynamoDB throttling
   - Lambda errors
   - Cost threshold ($1,000/month)

4. **SNS Topic**
   - Email notifications
   - SMS alerts (optional)

5. **Log Insights Queries**
   - Error detection
   - Slow requests
   - User activity

### Dashboard Access

**Main Dashboard:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=bme-agency-dev-main
```

**View Alarms:**
```bash
aws cloudwatch describe-alarms --state-value ALARM
```

**Query Logs:**
```bash
# Recent errors
aws logs tail /aws/lambda/ImageMetadataParser --follow --filter-pattern ERROR

# CloudWatch Insights
aws logs insights query \
  --log-group-name /model-agency/platform \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20'
```

### Monitoring Best Practices

1. **Daily Checks**
   - Review dashboard each morning
   - Check alarm status
   - Review cost trends

2. **Weekly Reviews**
   - Analyze error patterns
   - Optimize slow queries
   - Update alarm thresholds

3. **Monthly Tasks**
   - Cost optimization review
   - Performance benchmarking
   - Capacity planning

---

## 🏭 Step 5: Deploy to Staging (Pre-Production)

### Staging Deployment

**Purpose:** Production-like environment for final testing

```bash
# Deploy to staging
cd terraform/scripts
./deploy-staging.sh  # Similar to deploy-dev.sh
```

**Staging Configuration:**
- ✅ Versioning enabled
- ✅ MFA recommended
- ✅ Production-like resources
- ✅ 30-day log retention
- ✅ Polygon mainnet

**Testing Checklist:**

- [ ] All API endpoints functional
- [ ] Authentication flows working
- [ ] Image upload and processing
- [ ] License creation and NFT minting
- [ ] Dispute submission and voting
- [ ] Support ticket creation
- [ ] KBWI search functionality
- [ ] Cost within budget

**Performance Testing:**

```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 https://staging.cloudfront.url/

# Monitor during load
watch -n 1 'aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=DISTRIBUTION_ID \
  --start-time $(date -u -d "5 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum'
```

---

## 🚀 Step 6: Deploy to Production

### Production Deployment with Approvals

**⚠️ CRITICAL: Production requires multiple approvals**

```bash
cd terraform/scripts
./deploy-prod.sh
```

### Approval Gates

#### Gate 1: Initiation
- Deployer identification
- Ticket/JIRA ID required
- Initial confirmation

#### Gate 2: Plan Review
- Terraform plan generated
- Cost estimation shown
- **2 approvers required**
- Each approver confirms changes

#### Gate 3: Final Apply
- Last checkpoint
- Type "PRODUCTION" to confirm
- Creates pre-deployment backup

### Deployment Process

**Pre-Deployment Checks:**
1. ✅ Dev and staging deployments verified
2. ✅ AWS credentials and MFA validated
3. ✅ Configuration files present
4. ✅ Backend initialized
5. ✅ Security scan passed

**Deployment Steps:**
1. Terraform validation
2. Security scanning
3. Plan generation
4. Approval collection
5. State backup
6. Infrastructure apply
7. Post-deployment testing

**Post-Deployment:**
- Outputs saved
- Monitoring configured
- Deployment logged
- Summary created

### Production Configuration

| Feature | Value |
|---------|-------|
| Environment | Production |
| Budget | $10,000/month |
| MFA | Required |
| Versioning | Enabled |
| Backups | Daily |
| Log Retention | 90 days |
| Blockchain | Ethereum mainnet |

### Monitoring Schedule

**First 30 Minutes:**
- Watch dashboards continuously
- Check error rates every 5 minutes
- Monitor latency metrics
- Verify customer functionality

**First 24 Hours:**
- Check dashboards every 2 hours
- Review error logs
- Monitor costs
- Customer feedback

**First Week:**
- Daily dashboard reviews
- Cost tracking
- Performance optimization
- User feedback collection

---

## 🔄 Rollback Procedures

### If Deployment Fails

**Immediate Rollback:**
```bash
cd terraform

# Restore previous state
terraform state push backups/prod-state-TIMESTAMP.json

# Or re-apply previous configuration
git checkout HEAD~1
terraform apply -var-file="environments/prod.tfvars"
```

### If Issues Discovered Post-Deployment

**Quick Fix:**
```bash
# Make configuration changes
# Deploy again
./deploy-prod.sh
```

**Full Rollback:**
```bash
# Restore DynamoDB
aws dynamodb restore-table-from-backup \
  --target-table-name license-registry \
  --backup-arn BACKUP_ARN

# Restore S3 versioned objects
aws s3api list-object-versions \
  --bucket portfolio-bucket \
  --prefix problematic-folder/

# Restore previous version
aws s3api copy-object \
  --copy-source portfolio-bucket/key?versionId=VERSION_ID \
  --bucket portfolio-bucket \
  --key key
```

---

## 📈 Post-Deployment Checklist

### Immediate (0-1 hour)
- [ ] All services running
- [ ] No critical alarms
- [ ] CloudFront serving content
- [ ] API endpoints responding
- [ ] Authentication working
- [ ] Error rates <1%

### Short-term (1-24 hours)
- [ ] Monitor dashboard trends
- [ ] Review application logs
- [ ] Check cost metrics
- [ ] Collect user feedback
- [ ] Update documentation
- [ ] Notify stakeholders

### Medium-term (1-7 days)
- [ ] Performance optimization
- [ ] Cost optimization
- [ ] Capacity planning
- [ ] Security review
- [ ] Backup verification

---

## 🆘 Troubleshooting

### Common Issues

**1. Terraform State Lock**
```bash
# Force unlock (use carefully)
terraform force-unlock LOCK_ID
```

**2. Resource Already Exists**
```bash
# Import existing resource
terraform import aws_s3_bucket.portfolio portfolio-bucket-name
```

**3. Permission Denied**
```bash
# Check IAM permissions
aws iam get-user

# Check assumed role
aws sts get-caller-identity
```

**4. Plan Shows Many Changes**
```bash
# Check for drift
terraform plan -detailed-exitcode

# Refresh state
terraform refresh
```

### Getting Help

**Documentation:**
- Terraform Docs: https://registry.terraform.io
- AWS Docs: https://docs.aws.amazon.com
- Project Wiki: /terraform/README.md

**Support Channels:**
- Email: infrastructure@bigmannentertainment.com
- Slack: #infrastructure-support
- On-call: +1-555-DEVOPS

---

## 📊 Success Metrics

### Deployment Success Criteria

✅ **Infrastructure:**
- All resources created
- No failed deployments
- State synchronized

✅ **Performance:**
- Response time <500ms
- Error rate <0.1%
- 99.9% uptime

✅ **Security:**
- All scans passed
- MFA enabled
- Encryption active

✅ **Cost:**
- Within budget
- Optimizations applied
- Forecasts accurate

---

## 🎯 Next Steps

After successful deployment:

1. **Enable Additional Features**
   ```bash
   # Enable WAF
   # Configure auto-scaling
   # Set up additional alarms
   ```

2. **Optimize Performance**
   ```bash
   # Review CloudWatch metrics
   # Tune Lambda memory
   # Optimize DynamoDB indexes
   ```

3. **Implement Advanced Monitoring**
   ```bash
   # Set up X-Ray tracing
   # Configure custom metrics
   # Integrate with PagerDuty
   ```

4. **Plan for Scale**
   ```bash
   # Load testing
   # Capacity planning
   # Multi-region setup
   ```

---

## 📝 Appendix

### All Scripts Reference

| Script | Purpose | Duration |
|--------|---------|----------|
| `setup-credentials.sh` | Configure AWS access | 5 min |
| `initialize-backend.sh` | Setup remote state | 10 min |
| `deploy-dev.sh` | Deploy development | 20 min |
| `setup-monitoring.sh` | Configure dashboards | 15 min |
| `deploy-staging.sh` | Deploy staging | 25 min |
| `deploy-prod.sh` | Deploy production | 30 min |

### Environment Comparison

| Feature | Dev | Staging | Prod |
|---------|-----|---------|------|
| MFA | No | Recommended | Required |
| Versioning | No | Yes | Yes |
| Backups | Manual | Daily | Hourly |
| Log Retention | 7 days | 30 days | 90 days |
| Budget | $500 | $2,000 | $10,000 |

### Quick Reference Commands

```bash
# Check deployment status
terraform workspace list
terraform state list

# View outputs
terraform output
terraform output -json

# Check costs
aws ce get-cost-and-usage \
  --time-period Start=2025-11-01,End=2025-11-30 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Monitor resources
aws cloudwatch get-dashboard --dashboard-name bme-agency-prod-main
```

---

**Deployment Guide Version:** 1.0  
**Last Updated:** November 12, 2025  
**Status:** ✅ Production Ready
