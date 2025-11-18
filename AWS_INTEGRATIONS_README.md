# AWS Integrations - Big Mann Entertainment Platform

Complete guide to all AWS service integrations in the BME platform.

## 📚 Table of Contents

1. [Active AWS Services](#active-aws-services)
2. [Recent Updates](#recent-updates)
3. [Service Deprecations](#service-deprecations)
4. [Documentation Index](#documentation-index)
5. [Quick Links](#quick-links)

---

## 🚀 Active AWS Services

### Core Services

#### 1. **AWS Organizations**
- **Status**: ✅ Fully Integrated (Nov 2025)
- **Purpose**: Account lifecycle management
- **Features**: 
  - State-based account monitoring (new State field)
  - Critical account alerts
  - State change history tracking
  - Real-time account status
- **Dashboard**: `/aws-organizations`
- **API**: `/api/aws-organizations/*`
- **Docs**: `AWS_ORGANIZATIONS_GUIDE.md`

#### 2. **AWS Lambda**
- **Status**: ✅ Active
- **Runtime**: Node.js 22.x (updated Nov 2025)
- **Functions**:
  - Authentication challenges (Amplify)
  - Serverless processing
  - Event-driven workflows
- **Tools**: `aws-lambda-update/` scripts
- **Docs**: `aws-lambda-update/README.md`

#### 3. **AWS S3**
- **Status**: ✅ Active
- **Purpose**: Media storage, portfolios, documents
- **Features**:
  - Asset management
  - Thumbnail generation
  - Watermarked previews
  - Encrypted storage
- **Service**: `backend/aws_storage_service.py`
- **Docs**: `AWS_AGENCY_PLATFORM_GUIDE.md`

#### 4. **AWS Cognito**
- **Status**: ✅ Active
- **Purpose**: User authentication
- **Features**:
  - Agency authentication
  - Custom auth challenges
  - User pool management
- **Integration**: Amplify + Lambda triggers

#### 5. **Amazon Rekognition**
- **Status**: ✅ Active
- **Purpose**: AI-powered image analysis
- **Features**:
  - Face detection
  - Label detection
  - Content moderation
  - Image metadata extraction
- **Service**: `backend/agency_aws_service.py`

### Supporting Services

#### 6. **AWS DynamoDB**
- **Status**: ✅ Active
- **Purpose**: Licensing metadata, fast key-value storage
- **Use Cases**: 
  - License tracking
  - Real-time data access
  - Serverless applications

#### 7. **AWS CloudWatch**
- **Status**: ✅ Active
- **Purpose**: Monitoring, logging, alerting
- **Features**:
  - Custom metrics
  - Log aggregation
  - Alarm configuration
  - Dashboard creation

#### 8. **AWS SNS**
- **Status**: ✅ Active
- **Purpose**: Notifications
- **Features**:
  - Email alerts
  - SMS notifications
  - Topic-based messaging

#### 9. **AWS Step Functions**
- **Status**: ✅ Active (Mock)
- **Purpose**: Workflow orchestration
- **Use Cases**:
  - Agency onboarding workflows
  - Multi-step processes

#### 10. **AWS QLDB**
- **Status**: ✅ Active (Mock)
- **Purpose**: Immutable ledger for disputes
- **Features**:
  - Cryptographically verifiable
  - Complete history
  - Tamper-proof records

#### 11. **AWS Macie**
- **Status**: ✅ Active (Mock)
- **Purpose**: Sensitive data detection
- **Use Cases**:
  - Document scanning
  - PII detection
  - Compliance validation

---

## 📅 Recent Updates

### November 2025

#### ✅ AWS Organizations - State Field Migration
**Date**: November 18, 2025

**Changes**:
- Implemented new State field support
- Built complete account lifecycle management system
- Created dashboard at `/aws-organizations`
- Added state change tracking
- MongoDB integration for history

**Impact**: 
- ✅ Ready for Status field deprecation (Sept 9, 2026)
- ✅ Enhanced account monitoring capabilities
- ✅ Granular state tracking (5 states vs 2)

**Migration**: Not required - feature is new to BME platform

---

#### ✅ Lambda Runtime Update
**Date**: November 18, 2025

**Changes**:
- Updated 4 Lambda functions from Node.js 20.x → 22.x
- Verified all functions active and healthy
- Created backup configurations

**Functions Updated**:
- amplify-login-create-auth-challenge-ec5da3fb
- amplify-login-custom-message-ec5da3fb
- amplify-login-define-auth-challenge-ec5da3fb
- amplify-login-verify-auth-challenge-ec5da3fb

**Impact**: 
- ✅ Latest stable Node.js runtime
- ✅ Improved performance and security
- ✅ Extended support lifecycle

---

## ⚠️ Service Deprecations

### 1. AWS S3 - Owner.DisplayName Removal

**Removal Date**: November 21, 2025

**Details**:
- Owner.DisplayName attribute being removed from all S3 API responses
- Preview period: July 15 - November 21, 2025
- Affects: GetBucketAcl, GetObjectAcl, ListObjects, ListObjectsV2, and more
- Migration: Use Owner.ID (canonical ID) instead

**BME Platform Status**:
- ✅ Platform already compliant
- ✅ No Owner.DisplayName usage found
- ✅ No migration required

**Documentation**: `AWS_S3_OWNER_DISPLAYNAME_DEPRECATION.md`

**Action Required**: 
- ℹ️ None for BME platform (already compliant)
- ℹ️ Monitor for any external S3 integrations
- ✅ Documentation created for awareness

---

### 2. AWS Config - Natural Language Querying

**Deprecation Date**: January 15, 2026

**Details**:
- Natural language query processor (preview) being discontinued
- Feature was never implemented in BME platform
- No migration required for BME

**Recommended Alternative**: Amazon Q Developer

**Documentation**: `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md`

**Action Required**: 
- ℹ️ None for BME platform (feature not used)
- ℹ️ Consider Amazon Q Developer for future natural language queries
- ✅ Documentation created for awareness

---

## 📖 Documentation Index

### Main Guides

| Document | Purpose | Status |
|----------|---------|--------|
| `AWS_ORGANIZATIONS_GUIDE.md` | Complete Organizations management guide | ✅ Current |
| `AWS_ORGANIZATIONS_QUICK_START.md` | Quick reference for Organizations | ✅ Current |
| `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md` | Config deprecation & migration | ✅ Current |
| `AWS_SERVICES_UPDATE_LOG.md` | Service updates tracking | ✅ Current |
| `AWS_INTEGRATIONS_README.md` | This file | ✅ Current |
| `AWS_AGENCY_PLATFORM_GUIDE.md` | Agency platform AWS setup | ✅ Current |
| `TERRAFORM_INFRASTRUCTURE_GUIDE.md` | IaC documentation | ✅ Current |
| `AWS_DEPLOYMENT_GUIDE.md` | Deployment procedures | ✅ Current |

### Deprecation & Migration Guides

#### AWS S3
| Document | Purpose | Length |
|----------|---------|--------|
| **AWS_S3_OWNER_DISPLAYNAME_DEPRECATION.md** | Owner.DisplayName removal guide | 12 min |

#### AWS Config
| Document | Purpose | Length |
|----------|---------|--------|
| **AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md** | Full deprecation guide | 15 min |
| **AWS_CONFIG_QUERY_MIGRATION_QUICK_REF.md** | Quick migration reference | 3 min |

### Service-Specific Docs

| Service | Documentation Location |
|---------|----------------------|
| Lambda | `aws-lambda-update/README.md` |
| S3 Storage | `backend/aws_storage_service.py` (docstrings) |
| Organizations | `backend/aws_organizations_service.py` (docstrings) |
| Terraform | `terraform/README.md` |
| Agency Platform | `backend/agency_aws_service.py` (docstrings) |

### Scripts & Tools

| Tool | Location | Purpose |
|------|----------|---------|
| Lambda Update (Python) | `aws-lambda-update/update-lambda-runtime.py` | Update Lambda runtimes |
| Lambda Update (Bash) | `aws-lambda-update/update-lambda-runtime.sh` | Shell version |
| Terraform Setup | `terraform/scripts/setup-credentials.sh` | AWS credentials setup |
| Terraform Deploy | `terraform/scripts/deploy-*.sh` | Environment deployment |

---

## 🔗 Quick Links

### Dashboards
- **AWS Organizations**: `/aws-organizations`
- **Agency Platform**: `/agency-dashboard`
- **Enhanced Features**: `/enhanced-features`

### API Endpoints
- **Organizations**: `http://backend/api/aws-organizations/*`
- **Agency AWS**: `http://backend/api/agency-aws/*`
- **S3 Storage**: Via storage service (internal)

### AWS Console
- [Organizations Console](https://console.aws.amazon.com/organizations/)
- [Lambda Console](https://console.aws.amazon.com/lambda/)
- [S3 Console](https://console.aws.amazon.com/s3/)
- [Cognito Console](https://console.aws.amazon.com/cognito/)
- [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)

### AWS Documentation
- [Organizations API Reference](https://docs.aws.amazon.com/organizations/latest/APIReference/)
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [S3 User Guide](https://docs.aws.amazon.com/s3/)
- [Rekognition Developer Guide](https://docs.aws.amazon.com/rekognition/)

---

## 🔧 Configuration

### Environment Variables

**Required**:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

**Optional (Service-Specific)**:
```bash
# S3
S3_BUCKET_NAME=bme-agency-assets

# Cognito
AWS_COGNITO_USER_POOL_ID=us-east-1_xxxxx

# Organizations (auto-detected)
# No additional config needed
```

### IAM Permissions Required

**Minimum Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "organizations:DescribeOrganization",
        "organizations:ListAccounts",
        "organizations:DescribeAccount",
        "lambda:GetFunctionConfiguration",
        "lambda:UpdateFunctionConfiguration",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "rekognition:DetectFaces",
        "rekognition:DetectLabels"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🧪 Testing

### Test AWS Credentials
```bash
# Via AWS CLI
aws sts get-caller-identity

# Via Python
python3 /app/test_aws_permissions.py
```

### Test Services

**Organizations**:
```bash
curl http://localhost:8001/api/aws-organizations/health
```

**Lambda Functions**:
```bash
aws lambda get-function-configuration --function-name amplify-login-create-auth-challenge-ec5da3fb
```

**S3 Access**:
```bash
aws s3 ls s3://your-bucket-name
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Organizations Service Unavailable
**Symptom**: Health check returns "unavailable"

**Solutions**:
- Check AWS credentials in `.env`
- Verify Organizations is enabled
- Ensure using management account
- Check IAM permissions

#### 2. Lambda Update Fails
**Symptom**: Runtime update errors

**Solutions**:
- Verify AWS credentials
- Check Lambda function exists
- Ensure IAM permissions for Lambda
- Review backup file for rollback

#### 3. S3 Upload Fails
**Symptom**: Asset upload errors

**Solutions**:
- Check S3 bucket exists
- Verify bucket permissions
- Check AWS credentials
- Review bucket policy

### Getting Help

**Internal Resources**:
- Review service logs: `tail -f /var/log/supervisor/backend.err.log`
- Check documentation in this repository
- Review service-specific docstrings

**AWS Support**:
- AWS Support Center
- AWS re:Post community
- AWS Personal Health Dashboard

---

## 📊 Service Status

| Service | Status | Last Updated | Next Review |
|---------|--------|-------------|-------------|
| Organizations | ✅ Operational | Nov 2025 | Jan 2026 |
| Lambda | ✅ Operational | Nov 2025 | Mar 2026 |
| S3 | ✅ Operational | Stable | - |
| Cognito | ✅ Operational | Stable | - |
| Rekognition | ✅ Operational | Stable | - |
| DynamoDB | ✅ Operational | Stable | - |
| CloudWatch | ✅ Operational | Stable | - |

---

## 🎯 Best Practices

### 1. Credential Management
- Store credentials in `.env` files
- Never commit credentials to git
- Rotate keys regularly
- Use IAM roles when possible

### 2. Service Monitoring
- Check AWS Service Health Dashboard weekly
- Subscribe to AWS "What's New"
- Review Personal Health Dashboard
- Set up CloudWatch alarms

### 3. Cost Optimization
- Enable S3 lifecycle policies
- Use Lambda reserved concurrency wisely
- Monitor CloudWatch logs retention
- Review unused resources monthly

### 4. Security
- Follow principle of least privilege
- Enable MFA for AWS accounts
- Use encryption at rest (S3, DynamoDB)
- Regularly audit IAM permissions

### 5. Backup & Recovery
- Keep Lambda configuration backups
- Version S3 buckets
- Export Organizations state history
- Document disaster recovery procedures

---

## 🚀 Future Integrations

### Planned
- [ ] Amazon Q Developer integration
- [ ] AWS Control Tower for multi-account management
- [ ] AWS Cost Explorer API integration
- [ ] Enhanced CloudWatch dashboards
- [ ] AWS EventBridge for event-driven architecture

### Under Consideration
- [ ] AWS AppSync for GraphQL API
- [ ] Amazon Textract for document processing
- [ ] AWS Comprehend for sentiment analysis
- [ ] Amazon Polly for text-to-speech
- [ ] AWS MediaConvert for video transcoding

---

## 📝 Contributing

### Adding New AWS Service Integration

1. **Research**: Review AWS documentation
2. **Plan**: Document service purpose and features
3. **Implement**: Create service layer in `backend/`
4. **Test**: Verify integration works
5. **Document**: Update this README and create service docs
6. **Deploy**: Roll out to production
7. **Monitor**: Track usage and costs

### Updating Existing Integration

1. **Review Change**: Check AWS announcements
2. **Impact Assessment**: Evaluate BME platform impact
3. **Test Changes**: Verify in development
4. **Update Code**: Implement required changes
5. **Update Docs**: Reflect changes in documentation
6. **Deploy**: Roll out with monitoring
7. **Log Update**: Add to `AWS_SERVICES_UPDATE_LOG.md`

---

## 📞 Contact

**AWS Account Issues**:
- Contact AWS support via console
- Escalate to TAM if applicable

**BME Platform AWS Questions**:
- Review documentation in `/app/`
- Check service logs
- Consult `AWS_SERVICES_UPDATE_LOG.md`

---

**Last Updated**: November 18, 2025
**Next Review**: December 18, 2025
**Maintained By**: BME Platform Engineering Team
