# AWS Documentation Index

Complete index of all AWS-related documentation for the Big Mann Entertainment platform.

---

## 📚 Documentation Structure

```
/app/
├── AWS Documentation (You are here)
│   ├── AWS_DOCUMENTATION_INDEX.md (This file)
│   ├── AWS_INTEGRATIONS_README.md (Main overview)
│   ├── AWS_SERVICES_UPDATE_LOG.md (Update tracking)
│   │
│   ├── AWS Organizations (Account Management)
│   │   ├── AWS_ORGANIZATIONS_GUIDE.md (Complete guide)
│   │   └── AWS_ORGANIZATIONS_QUICK_START.md (Quick reference)
│   │
│   ├── AWS Config (Query Deprecation)
│   │   ├── AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md (Full guide)
│   │   └── AWS_CONFIG_QUERY_MIGRATION_QUICK_REF.md (Quick reference)
│   │
│   ├── Lambda Updates
│   │   ├── aws-lambda-update/README.md (Update tools)
│   │   ├── aws-lambda-update/QUICK_START.md (Quick guide)
│   │   └── aws-lambda-update/update-lambda-runtime.py (Script)
│   │
│   ├── Infrastructure & Deployment
│   │   ├── TERRAFORM_INFRASTRUCTURE_GUIDE.md (IaC guide)
│   │   ├── AWS_DEPLOYMENT_GUIDE.md (Deployment procedures)
│   │   └── AWS_AGENCY_PLATFORM_GUIDE.md (Agency platform)
│   │
│   └── Service Code (Backend)
│       ├── backend/aws_organizations_service.py
│       ├── backend/aws_storage_service.py
│       └── backend/agency_aws_service.py
```

---

## 🎯 Quick Navigation

### By Task

#### "I want to monitor my AWS accounts"
→ `AWS_ORGANIZATIONS_GUIDE.md`
→ Dashboard: `/aws-organizations`

#### "I need to update Lambda runtimes"
→ `aws-lambda-update/README.md`
→ `aws-lambda-update/QUICK_START.md`

#### "I need to query AWS resources"
→ `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md` (for migration)
→ Use Amazon Q Developer or SQL queries

#### "I want to deploy AWS infrastructure"
→ `TERRAFORM_INFRASTRUCTURE_GUIDE.md`
→ `AWS_DEPLOYMENT_GUIDE.md`

#### "I need to understand AWS service changes"
→ `AWS_SERVICES_UPDATE_LOG.md`
→ `AWS_INTEGRATIONS_README.md`

#### "I want to manage agency assets in S3"
→ `AWS_AGENCY_PLATFORM_GUIDE.md`
→ Code: `backend/aws_storage_service.py`

---

## 📖 Document Categories

### 🟢 Core Integration Guides

| Document | Purpose | Audience | Length |
|----------|---------|----------|--------|
| **AWS_INTEGRATIONS_README.md** | Main overview of all AWS services | All users | 10 min |
| **AWS_SERVICES_UPDATE_LOG.md** | Track updates and deprecations | Developers | 5 min |
| **AWS_DOCUMENTATION_INDEX.md** | This file - navigation hub | All users | 2 min |

### 🔵 Feature-Specific Guides

#### AWS Organizations
| Document | Purpose | Length |
|----------|---------|--------|
| **AWS_ORGANIZATIONS_GUIDE.md** | Complete implementation guide | 20 min |
| **AWS_ORGANIZATIONS_QUICK_START.md** | Quick reference & examples | 5 min |

#### AWS Config
| Document | Purpose | Length |
|----------|---------|--------|
| **AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md** | Full deprecation guide | 15 min |
| **AWS_CONFIG_QUERY_MIGRATION_QUICK_REF.md** | Quick migration reference | 3 min |

#### Lambda Management
| Document | Purpose | Length |
|----------|---------|--------|
| **aws-lambda-update/README.md** | Update tool documentation | 10 min |
| **aws-lambda-update/QUICK_START.md** | Quick update guide | 3 min |

### 🟡 Infrastructure & Deployment

| Document | Purpose | Length |
|----------|---------|--------|
| **TERRAFORM_INFRASTRUCTURE_GUIDE.md** | Terraform setup and deployment | 25 min |
| **AWS_DEPLOYMENT_GUIDE.md** | General deployment procedures | 15 min |
| **AWS_AGENCY_PLATFORM_GUIDE.md** | Agency platform AWS setup | 20 min |

---

## 🗺️ Learning Paths

### Path 1: New to BME AWS Integration
**Goal**: Understand what AWS services we use and why

```
1. Start: AWS_INTEGRATIONS_README.md (10 min)
   └─ Overview of all services

2. Review: AWS_SERVICES_UPDATE_LOG.md (5 min)
   └─ Recent changes and updates

3. Explore specific service docs as needed
```

### Path 2: AWS Organizations Setup
**Goal**: Set up and use account monitoring

```
1. Quick Start: AWS_ORGANIZATIONS_QUICK_START.md (5 min)
   └─ Immediate hands-on

2. If needed: AWS_ORGANIZATIONS_GUIDE.md (20 min)
   └─ Deep dive into features

3. Access dashboard: /aws-organizations
```

### Path 3: Lambda Management
**Goal**: Update Lambda function runtimes

```
1. Quick guide: aws-lambda-update/QUICK_START.md (3 min)
   └─ Fast update process

2. Run script: update-lambda-runtime.py
   └─ Automated updates

3. If issues: aws-lambda-update/README.md (10 min)
   └─ Troubleshooting
```

### Path 4: Query Migration (Config)
**Goal**: Migrate from Config natural language to Amazon Q

```
1. Quick ref: AWS_CONFIG_QUERY_MIGRATION_QUICK_REF.md (3 min)
   └─ Fast migration options

2. Full guide: AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md (15 min)
   └─ Complete migration process

3. Choose: Amazon Q Developer or SQL queries
```

### Path 5: Infrastructure Deployment
**Goal**: Deploy AWS infrastructure using Terraform

```
1. Setup: TERRAFORM_INFRASTRUCTURE_GUIDE.md (25 min)
   └─ Complete Terraform guide

2. Deploy: Use scripts in terraform/scripts/
   └─ Automated deployment

3. Monitor: AWS_DEPLOYMENT_GUIDE.md (15 min)
   └─ Operational procedures
```

---

## 🔍 Search Index

### By AWS Service

**Organizations**:
- AWS_ORGANIZATIONS_GUIDE.md
- AWS_ORGANIZATIONS_QUICK_START.md
- backend/aws_organizations_service.py

**Lambda**:
- aws-lambda-update/README.md
- aws-lambda-update/QUICK_START.md
- aws-lambda-update/update-lambda-runtime.py

**S3**:
- AWS_AGENCY_PLATFORM_GUIDE.md
- backend/aws_storage_service.py

**Config**:
- AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md
- AWS_CONFIG_QUERY_MIGRATION_QUICK_REF.md

**Rekognition, DynamoDB, Cognito, etc.**:
- AWS_INTEGRATIONS_README.md
- backend/agency_aws_service.py

**Terraform/IaC**:
- TERRAFORM_INFRASTRUCTURE_GUIDE.md
- terraform/README.md

---

## 📅 By Date

### November 2025
- ✅ AWS_ORGANIZATIONS_GUIDE.md - Organizations State field
- ✅ AWS_ORGANIZATIONS_QUICK_START.md - Quick reference
- ✅ AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md - Config deprecation
- ✅ AWS_CONFIG_QUERY_MIGRATION_QUICK_REF.md - Migration quick ref
- ✅ AWS_SERVICES_UPDATE_LOG.md - Update tracking
- ✅ AWS_INTEGRATIONS_README.md - Main overview
- ✅ AWS_DOCUMENTATION_INDEX.md - This file

### October 2025 and Earlier
- TERRAFORM_INFRASTRUCTURE_GUIDE.md
- AWS_DEPLOYMENT_GUIDE.md
- AWS_AGENCY_PLATFORM_GUIDE.md
- aws-lambda-update/README.md

---

## 🎓 Document Status

| Document | Status | Last Updated | Next Review |
|----------|--------|-------------|-------------|
| AWS_INTEGRATIONS_README.md | ✅ Current | Nov 2025 | Dec 2025 |
| AWS_SERVICES_UPDATE_LOG.md | ✅ Current | Nov 2025 | Dec 2025 |
| AWS_ORGANIZATIONS_GUIDE.md | ✅ Current | Nov 2025 | Jan 2026 |
| AWS_S3_OWNER_DISPLAYNAME_DEPRECATION.md | ✅ Current | Nov 2025 | Nov 2025 |
| AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md | ✅ Current | Nov 2025 | Jan 2026 |
| TERRAFORM_INFRASTRUCTURE_GUIDE.md | ✅ Current | Oct 2025 | Mar 2026 |
| AWS_AGENCY_PLATFORM_GUIDE.md | ✅ Current | Sep 2025 | Mar 2026 |

---

## 🔔 Important Dates

### Upcoming Deprecations
- **November 21, 2025**: AWS S3 Owner.DisplayName attribute removed (✅ BME compliant)
- **January 15, 2026**: AWS Config natural language queries discontinued
- **September 9, 2026**: AWS Organizations Status field fully deprecated

### Review Schedule
- **Weekly**: Check AWS Service Health Dashboard
- **Monthly**: Review AWS_SERVICES_UPDATE_LOG.md
- **Quarterly**: Update all documentation
- **Annually**: Major documentation overhaul

---

## 💡 Documentation Best Practices

### When Reading Docs
1. Start with quick reference guides for overview
2. Use full guides for implementation details
3. Check update logs for recent changes
4. Verify document last-updated date

### When Creating/Updating Docs
1. Update AWS_SERVICES_UPDATE_LOG.md first
2. Create/update feature-specific docs
3. Update this index file
4. Add cross-references between docs
5. Include examples and code snippets

---

## 🔗 External Resources

### AWS Official Documentation
- [AWS Documentation Home](https://docs.aws.amazon.com/)
- [AWS What's New](https://aws.amazon.com/new/)
- [AWS Blogs](https://aws.amazon.com/blogs/)

### Service-Specific
- [Organizations](https://docs.aws.amazon.com/organizations/)
- [Lambda](https://docs.aws.amazon.com/lambda/)
- [Config](https://docs.aws.amazon.com/config/)
- [S3](https://docs.aws.amazon.com/s3/)

### Tools
- [Amazon Q Developer](https://aws.amazon.com/q/developer/)
- [AWS CLI](https://aws.amazon.com/cli/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/)

---

## 📊 Documentation Statistics

**Total Documents**: 13 AWS-specific docs
**Total Pages**: ~160 pages equivalent
**Last Major Update**: November 2025
**Coverage**: 11 AWS services documented
**Deprecation Guides**: 3 (Organizations, Config, S3)

---

## 🤝 Contributing

### Adding New Documentation
1. Create document following naming convention: `AWS_[SERVICE]_[TYPE].md`
2. Add entry to this index
3. Update AWS_INTEGRATIONS_README.md
4. Add to AWS_SERVICES_UPDATE_LOG.md if it's an update
5. Cross-reference with related docs

### Updating Existing Documentation
1. Make changes to specific doc
2. Update "Last Updated" date
3. Update this index if structure changes
4. Note changes in AWS_SERVICES_UPDATE_LOG.md

---

## 📞 Getting Help

**Can't find what you need?**
1. Check this index for relevant docs
2. Search AWS_INTEGRATIONS_README.md for service overview
3. Review AWS_SERVICES_UPDATE_LOG.md for recent changes
4. Check service-specific code docstrings
5. Contact platform engineering team

**Report documentation issues**:
- Missing information
- Outdated content
- Broken links
- Unclear instructions

---

## 🎯 Quick Access

### Most Accessed Documents
1. AWS_INTEGRATIONS_README.md - Service overview
2. AWS_ORGANIZATIONS_QUICK_START.md - Account monitoring
3. aws-lambda-update/QUICK_START.md - Lambda updates
4. AWS_SERVICES_UPDATE_LOG.md - What's changed

### Most Important for 2025-2026
1. AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md - Jan 2026 deprecation
2. AWS_ORGANIZATIONS_GUIDE.md - Sept 2026 State field migration
3. AWS_SERVICES_UPDATE_LOG.md - Tracking all changes

---

**Index Version**: 1.0
**Last Updated**: November 18, 2025
**Next Review**: December 18, 2025
**Maintained By**: BME Platform Engineering Team
