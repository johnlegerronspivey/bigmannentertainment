# AWS Config Natural Language Query Migration - Quick Reference

## ⚠️ DEPRECATION: January 15, 2026

AWS Config natural language query processor is being discontinued.

---

## 🔄 Migration Path

### OLD: AWS Config Natural Language
```
AWS Console → AWS Config → Advanced Queries → Natural Language
"Show me all EC2 instances"
```

### NEW: Amazon Q Developer
```
AWS Console → Amazon Q (bottom right icon)
"Show me all EC2 instances"
```

---

## 📋 Quick Comparison

| Feature | AWS Config NL | Amazon Q | SQL Queries |
|---------|---------------|----------|-------------|
| **Status** | Ending Jan 2026 | Active | Active |
| **Regions** | US East/West | All | All |
| **Cost** | Free (preview) | Paid | Free |
| **Complexity** | Simple | Simple | Advanced |
| **Scope** | Config only | All AWS | Config only |

---

## 🚀 3 Migration Options

### Option 1: Amazon Q Developer (Recommended)
**Best for**: Natural language queries across all AWS services

```bash
# Install CLI
pip install amazon-q-developer-cli

# Configure
q configure

# Query
q "Show me all S3 buckets without encryption"
```

**Pros**: 
- ✅ Natural language
- ✅ All AWS services
- ✅ Code generation
- ✅ Actively developed

**Cons**: 
- ❌ Paid service
- ❌ Requires new setup

---

### Option 2: AWS Config SQL (Free)
**Best for**: Complex queries, automation, no additional cost

```sql
SELECT
  resourceId,
  resourceType,
  configuration.state.name
FROM
  aws_ec2_instance
WHERE
  configuration.state.name = 'running'
```

**Pros**: 
- ✅ Free
- ✅ Powerful
- ✅ Programmatic access

**Cons**: 
- ❌ Requires SQL knowledge
- ❌ Config data only

---

### Option 3: AWS Resource Explorer
**Best for**: Simple resource discovery

```bash
aws resource-explorer-2 search \
  --query-string "resourceType:EC2::Instance"
```

**Pros**: 
- ✅ Simple syntax
- ✅ Cross-account
- ✅ Fast

**Cons**: 
- ❌ Limited query capabilities
- ❌ No complex filtering

---

## 📊 Common Query Translations

### Query 1: List EC2 Instances
**Natural Language (OLD)**:
```
"Show me all EC2 instances"
```

**Amazon Q (NEW)**:
```
"List all EC2 instances in my account"
```

**SQL Alternative**:
```sql
SELECT resourceId, configuration.instanceType
FROM aws_ec2_instance
```

---

### Query 2: Find Unencrypted S3 Buckets
**Natural Language (OLD)**:
```
"Find S3 buckets without encryption"
```

**Amazon Q (NEW)**:
```
"Which S3 buckets don't have encryption enabled?"
```

**SQL Alternative**:
```sql
SELECT resourceId
FROM aws_s3_bucket
WHERE configuration.encryption IS NULL
```

---

### Query 3: Non-Compliant Resources
**Natural Language (OLD)**:
```
"Show me non-compliant resources"
```

**Amazon Q (NEW)**:
```
"What resources are currently non-compliant?"
```

**SQL Alternative**:
```sql
SELECT resourceId, resourceType
FROM resources
WHERE configuration.configurationItemStatus = 'ResourceDiscovered'
AND configuration.complianceType = 'NON_COMPLIANT'
```

---

## 🔧 Quick Setup

### Amazon Q Developer

**Console Access** (Easiest):
1. Open AWS Console
2. Click Q icon (bottom right)
3. Start querying!

**CLI Setup**:
```bash
# Install
pip install amazon-q-developer-cli

# Configure
q configure
# Enter AWS credentials when prompted

# Test
q "Show me my S3 buckets"
```

**VS Code Setup**:
1. Install "Amazon Q" extension
2. Sign in with AWS Builder ID
3. Use Command Palette: "Amazon Q: Chat"

---

### Continue Using SQL

**No setup needed** - just switch to SQL mode in AWS Config Advanced Queries.

**Example Workflow**:
```
1. Go to AWS Config → Advanced Queries
2. Click "Create query"
3. Write SQL query
4. Click "Run query"
5. Export results if needed
```

---

## 💰 Cost Considerations

### AWS Config Natural Language
- **Current**: Free (preview)
- **After Jan 15, 2026**: N/A (discontinued)

### Amazon Q Developer
- **Free Tier**: Limited queries/month
- **Pro**: $19/user/month
- **Usage-based**: Pay per query over free tier

### SQL Queries
- **Cost**: Free (only pay for Config service)
- **No additional charge** for running queries

### Resource Explorer
- **Cost**: Free
- **No additional charge**

---

## 📅 Action Timeline

### By December 15, 2025 (30 days before)
- [ ] Test Amazon Q Developer
- [ ] Document current queries
- [ ] Choose migration path
- [ ] Update team documentation

### By January 1, 2026 (14 days before)
- [ ] Complete migration
- [ ] Train team on new method
- [ ] Update runbooks
- [ ] Test all queries

### By January 15, 2026 (Deadline)
- [ ] Confirm no dependencies on old feature
- [ ] Archive old documentation
- [ ] Update processes

---

## 🆘 Quick Help

### Getting Amazon Q Developer Access
```
1. Go to AWS Console
2. Click Amazon Q icon (bottom right)
3. If prompted, enable Amazon Q for your account
4. Accept terms and conditions
5. Start querying!
```

### SQL Query Help
```
# AWS Config Query Examples
https://docs.aws.amazon.com/config/latest/developerguide/example-query.html

# SQL Reference
https://docs.aws.amazon.com/config/latest/developerguide/querying-AWS-resources.html
```

### Still Stuck?
- Check: `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md` for full guide
- AWS Support: Open console support case
- Community: AWS re:Post forum

---

## 🎯 Recommendation Summary

**For BME Platform**:
1. **Primary**: Use **SQL queries** (free, powerful, no migration needed)
2. **Future**: Consider **Amazon Q** for ad-hoc queries
3. **No Action Required**: Feature was never used in BME

**For General Use**:
- **Casual Users** → Amazon Q Developer (easy, natural language)
- **Power Users** → SQL Queries (free, flexible, powerful)
- **Quick Lookups** → Resource Explorer (fast, simple)

---

## 📚 Full Documentation

- **Complete Guide**: `AWS_CONFIG_NATURAL_LANGUAGE_DEPRECATION.md`
- **Service Updates**: `AWS_SERVICES_UPDATE_LOG.md`
- **AWS Integrations**: `AWS_INTEGRATIONS_README.md`

---

**Quick Ref Version**: 1.0
**Last Updated**: November 18, 2025
**Deprecation Date**: January 15, 2026
