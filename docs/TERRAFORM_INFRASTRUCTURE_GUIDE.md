# AWS Infrastructure as Code (IaC) Guide
## Terraform + CI/CD for Modeling Agency Platform

---

## 📋 Overview

Complete Infrastructure as Code setup using Terraform for deploying the AWS-powered Modeling Agency Platform across multiple environments with automated CI/CD pipelines.

**Infrastructure Coverage:**
- ✅ 8 Terraform modules
- ✅ 3 environments (dev, staging, prod)
- ✅ GitHub Actions CI/CD
- ✅ Security scanning
- ✅ Cost estimation
- ✅ Automated tagging

---

## 🏗️ Architecture Overview

### Terraform Module Structure

```
terraform/
├── main.tf                      # Root configuration
├── variables.tf                 # Global variables
├── outputs.tf                   # Infrastructure outputs
├── environments/
│   ├── dev.tfvars              # Dev environment config
│   ├── staging.tfvars          # Staging environment config
│   └── prod.tfvars             # Production environment config
└── modules/
    ├── portfolio-storage/      # S3 + lifecycle policies
    ├── image-metadata/         # Lambda + Rekognition
    ├── smart-licensing/        # DynamoDB + blockchain
    ├── agency-onboarding/      # Cognito + Step Functions
    ├── support-disputes/       # SNS + QLDB
    ├── knowledge-base/         # S3 static website
    ├── cdn/                    # CloudFront distribution
    └── monitoring-security/    # CloudWatch + IAM
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Terraform
brew install terraform

# Install AWS CLI
brew install awscli

# Configure AWS credentials
aws configure
```

### Initialize Terraform

```bash
cd terraform

# Initialize backend and providers
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

### Deploy to Development

```bash
# Plan deployment
terraform plan -var-file="environments/dev.tfvars" -out=tfplan

# Review plan and apply
terraform apply tfplan

# View outputs
terraform output
```

---

## 📦 Module Details

### 1. Portfolio Storage Module

**Resources:**
- `aws_s3_bucket` - Main portfolio assets
- `aws_s3_bucket` - Thumbnails
- `aws_s3_bucket_versioning` - Version control
- `aws_s3_bucket_encryption` - AES256 encryption
- `aws_s3_bucket_lifecycle_configuration` - Cost optimization

**Lifecycle Policies:**
- Standard → Standard-IA after 90 days
- Standard-IA → Glacier after 180 days
- Delete old versions after 90 days

**Cost Optimization:**
- Dev: No versioning
- Staging: Versioning enabled
- Prod: Versioning + point-in-time recovery

### 2. Image Metadata Module

**Resources:**
- `aws_lambda_function` - Metadata extraction
- `aws_iam_role` - Lambda execution role
- S3 event triggers for automatic processing
- Integration with Rekognition API

**Features:**
- Face detection
- Label extraction
- Moderation scanning
- EXIF parsing

### 3. Smart Licensing Module

**Resources:**
- `aws_dynamodb_table` - License registry
- `aws_dynamodb_table` - Royalty payments
- `aws_lambda_function` - Royalty calculator
- CloudWatch alarms

**DynamoDB Configuration:**
- Billing: Pay-per-request
- Encryption: Server-side
- Point-in-time recovery (prod only)
- TTL for expired licenses

**GSIs (Global Secondary Indexes):**
- ModelIDIndex - Query by model
- AgencyIDIndex - Query by agency
- LicenseIDIndex - Royalty lookup

### 4. Agency Onboarding Module

**Resources:**
- `aws_cognito_user_pool` - User management
- `aws_cognito_user_pool_client` - App client
- `aws_step_functions_state_machine` - KYC workflow
- S3 for document storage
- Macie for PII scanning

**Cognito Features:**
- Email verification
- MFA (prod only)
- Password policies
- Custom attributes

### 5. Support & Disputes Module

**Resources:**
- `aws_sns_topic` - Alert notifications
- `aws_qldb_ledger` - Immutable dispute records
- Lambda functions for ticket routing
- S3 for evidence storage

**QLDB Configuration:**
- Permissions: STANDARD
- Deletion protection (prod)
- Automatic backups

### 6. Knowledge Base Module

**Resources:**
- `aws_s3_bucket` - Static website hosting
- `aws_s3_bucket_website_configuration` - Website config
- CloudFront distribution
- OpenSearch domain (optional)

**Features:**
- Static site hosting
- Full-text search
- Role-based access
- Version control

### 7. CDN Module

**Resources:**
- `aws_cloudfront_distribution` - Global CDN
- Origin access identity
- Cache behaviors
- Custom error responses

**Configuration:**
- Price class: All edge locations
- HTTP/2 enabled
- Compression enabled
- WAF integration (prod)

### 8. Monitoring & Security Module

**Resources:**
- `aws_cloudwatch_log_group` - Centralized logging
- `aws_cloudwatch_metric_alarm` - Alerts
- `aws_sns_topic` - Notification delivery
- `aws_iam_role` - Service roles
- AWS Backup plans

**Alarms:**
- High error rates
- Unusual access patterns
- Cost thresholds
- DynamoDB throttling

---

## 🏷️ Tagging Strategy

### Default Tags (Applied Automatically)

```hcl
default_tags {
  tags = {
    Project     = "ModelAgencyPlatform"
    Environment = var.environment        # dev, staging, prod
    Owner       = "Big Mann Entertainment"
    ManagedBy   = "Terraform"
    Compliance  = "GDPR,CCPA,SOC2"
  }
}
```

### Module-Specific Tags

```hcl
# Portfolio Storage
{
  Module  = "PortfolioStorage"
  Purpose = "ImageAssets"
}

# Smart Licensing
{
  Module     = "SmartLicensing"
  Blockchain = "Ethereum"
}

# Security
{
  Module      = "MonitoringSecurity"
  AlertLevel  = "Critical"
}
```

### Cost Tracking Tags

```hcl
{
  CostCenter = "ModelingAgency"
  BudgetOwner = "Operations"
  ChargeCode  = "MA-2025-Q1"
}
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**Triggers:**
- Push to `main` branch → Deploy to prod
- Push to `develop` branch → Deploy to staging
- Pull requests → Plan only

**Pipeline Stages:**

1. **Format Check**
   - Validate Terraform formatting
   - Run `terraform fmt -check`

2. **Security Scan**
   - Trivy vulnerability scanning
   - tfsec security analysis
   - Upload to GitHub Security

3. **Terraform Plan**
   - Initialize Terraform
   - Validate configuration
   - Generate execution plan
   - Comment plan on PR

4. **Cost Estimation**
   - Infracost breakdown
   - Compare with budget limits
   - Comment costs on PR

5. **Terraform Apply** (main branch only)
   - Apply changes sequentially
   - Deploy dev → staging → prod
   - Capture outputs

6. **Notifications**
   - Slack notifications
   - Email alerts
   - GitHub commit status

### Required GitHub Secrets

```yaml
# AWS Credentials
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY

# Notifications
SLACK_WEBHOOK_URL

# Cost Estimation
INFRACOST_API_KEY

# Optional
GITHUB_TOKEN (automatically provided)
```

---

## 🌍 Environment Configuration

### Development (`dev.tfvars`)

**Characteristics:**
- Cost-optimized
- Minimal redundancy
- Short log retention (7 days)
- No MFA requirement
- Polygon testnet

**Budget:** $500/month

**Use Cases:**
- Feature development
- Integration testing
- Developer experimentation

### Staging (`staging.tfvars`)

**Characteristics:**
- Production-like setup
- Versioning enabled
- Medium log retention (30 days)
- MFA recommended
- Polygon mainnet

**Budget:** $2,000/month

**Use Cases:**
- QA testing
- Performance testing
- Client demos

### Production (`prod.tfvars`)

**Characteristics:**
- High availability
- Full redundancy
- Long log retention (90 days)
- MFA required
- Ethereum mainnet

**Budget:** $10,000/month

**Use Cases:**
- Live customer traffic
- Revenue-generating operations
- Compliance audits

---

## 💰 Cost Management

### Monthly Cost Breakdown (Production)

| Service | Estimated Cost | Notes |
|---------|----------------|-------|
| S3 Storage | $500 | 10TB portfolio assets |
| CloudFront | $1,500 | Global CDN delivery |
| DynamoDB | $800 | Pay-per-request |
| Lambda | $300 | Metadata processing |
| Cognito | $200 | User management |
| QLDB | $150 | Dispute ledger |
| CloudWatch | $250 | Logging & monitoring |
| Rekognition | $1,000 | Image analysis |
| Data Transfer | $2,000 | Inter-region |
| Other | $500 | Misc services |
| **Total** | **~$7,200/month** | |

### Cost Optimization Strategies

1. **S3 Lifecycle Policies**
   - Move to Standard-IA after 90 days
   - Archive to Glacier after 180 days
   - Estimated savings: 40%

2. **CloudFront Caching**
   - TTL: 24 hours for images
   - Compression enabled
   - Estimated savings: 30%

3. **DynamoDB On-Demand**
   - Pay only for requests
   - No provisioned capacity waste
   - Estimated savings: 25%

4. **Lambda Reserved Concurrency**
   - Limit concurrent executions
   - Prevent runaway costs
   - Budget protection

5. **CloudWatch Log Retention**
   - Dev: 7 days
   - Staging: 30 days
   - Prod: 90 days
   - Estimated savings: 50%

### Budget Alerts

```hcl
# CloudWatch alarm for budget threshold
aws_budgets_budget "monthly" {
  name         = "monthly-budget"
  budget_type  = "COST"
  limit_amount = var.budget_limit_monthly
  time_unit    = "MONTHLY"
  
  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 80
    notification_type   = "FORECASTED"
    subscriber_email_addresses = [var.alert_email]
  }
}
```

---

## 🔒 Security Best Practices

### IAM Policies

**Principle of Least Privilege:**
```hcl
# Lambda execution role - minimal permissions
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:PutItem",
    "dynamodb:GetItem"
  ],
  "Resource": "arn:aws:dynamodb:*:*:table/license-registry"
}
```

### Encryption

- **S3:** AES256 server-side encryption
- **DynamoDB:** Encryption at rest
- **QLDB:** Automatic encryption
- **CloudWatch Logs:** KMS encryption (optional)

### Network Security

- **S3:** Block public access
- **CloudFront:** HTTPS required
- **Cognito:** TLS 1.2 minimum
- **Lambda:** VPC integration (optional)

### Compliance

- **GDPR:** Data retention policies
- **CCPA:** User data deletion
- **SOC 2:** Audit logging
- **HIPAA:** Encryption standards

---

## 🧪 Testing Guide

### Validate Terraform Configuration

```bash
# Format check
terraform fmt -check -recursive

# Validation
terraform validate

# Security scan
tfsec ./terraform

# Cost estimation
infracost breakdown --path ./terraform
```

### Test Deployment

```bash
# Dev environment
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"

# Verify outputs
terraform output

# Test endpoints
curl $(terraform output -raw cloudfront_domain_name)
```

### Rollback Strategy

```bash
# List state versions
terraform state list

# Restore previous state
terraform state pull > backup.tfstate

# Apply previous configuration
git revert HEAD
terraform apply
```

---

## 📊 Monitoring & Alerts

### CloudWatch Dashboards

**Metrics to Monitor:**
- S3 bucket size and request count
- DynamoDB read/write capacity
- Lambda invocations and errors
- CloudFront request rate
- Cognito sign-in failures

### SNS Alert Topics

```hcl
# Critical alerts
aws_sns_topic "critical_alerts" {
  name = "critical-alerts"
  
  subscription {
    protocol = "email"
    endpoint = "ops@bigmannentertainment.com"
  }
  
  subscription {
    protocol = "sms"
    endpoint = "+1-555-0123"
  }
}
```

### Log Aggregation

```hcl
# CloudWatch Logs Insights query
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

---

## 🔄 Disaster Recovery

### Backup Strategy

**Automated Backups:**
- S3 versioning enabled
- DynamoDB point-in-time recovery
- QLDB automatic backups
- Lambda function versions

**Backup Schedule:**
- Hourly: DynamoDB snapshots
- Daily: S3 full backup
- Weekly: Cross-region replication test
- Monthly: Disaster recovery drill

### Recovery Procedures

1. **S3 Recovery**
   ```bash
   # Restore from version
   aws s3api get-object-version \
     --bucket portfolio-bucket \
     --key image.jpg \
     --version-id VERSION_ID
   ```

2. **DynamoDB Recovery**
   ```bash
   # Point-in-time restore
   aws dynamodb restore-table-to-point-in-time \
     --source-table-name license-registry \
     --target-table-name license-registry-restore \
     --restore-date-time 2025-11-12T00:00:00Z
   ```

3. **Full Infrastructure Recovery**
   ```bash
   # Re-apply Terraform
   terraform init
   terraform apply -var-file="environments/prod.tfvars"
   ```

---

## 📝 Maintenance

### Regular Tasks

**Weekly:**
- Review CloudWatch dashboards
- Check cost reports
- Update security patches

**Monthly:**
- Rotate IAM credentials
- Review access logs
- Update Terraform modules
- Test disaster recovery

**Quarterly:**
- Security audit
- Compliance review
- Cost optimization analysis
- Performance benchmarking

### Terraform State Management

```bash
# Remote state backup
terraform state pull > terraform.tfstate.backup

# Lock state (prevent concurrent modifications)
terraform state lock

# Unlock state
terraform state unlock LOCK_ID
```

---

## 🎯 Next Steps

1. **Initial Setup**
   - Configure AWS credentials
   - Initialize Terraform backend
   - Deploy to dev environment

2. **CI/CD Configuration**
   - Set up GitHub secrets
   - Test pipeline with PR
   - Deploy to staging

3. **Production Deployment**
   - Review security settings
   - Configure monitoring
   - Deploy to production

4. **Optimization**
   - Monitor costs
   - Tune performance
   - Implement auto-scaling

---

## 📞 Support

**Infrastructure Issues:**
- Email: infrastructure@bigmannentertainment.com
- Slack: #infrastructure-support

**Emergency Contact:**
- On-call engineer: +1-555-DEVOPS

**Documentation:**
- AWS Console: https://console.aws.amazon.com
- Terraform Docs: https://registry.terraform.io

---

**Last Updated:** November 12, 2025  
**Terraform Version:** 1.6.0  
**AWS Provider Version:** ~> 5.0  
**Status:** ✅ Production Ready
