# AWS Config Natural Language Querying - Deprecation Notice

## ⚠️ Important Announcement

AWS Config's **Natural Language Query Processor** (preview feature) is being **discontinued on January 15, 2026**.

## 📅 Timeline

- **Launch**: 2024 (Preview)
- **Discontinuation**: January 15, 2026
- **Migration Path**: Amazon Q Developer

## 🔍 What Was the Feature?

The AWS Config natural language querying feature allowed users to:
- Write queries in plain English about AWS resource configurations
- Automatically convert natural language prompts to SQL queries
- Query AWS Config advanced queries without knowing SQL
- Explore resource states, compliance, and configurations conversationally

### Example Queries
```
"Show me all EC2 instances in production"
"Find S3 buckets without encryption"
"List non-compliant resources"
"What Lambda functions are using Python 3.8?"
```

### Preview Availability
- **Regions**: US East (N. Virginia), US West (Oregon) only
- **Status**: Public Preview
- **SQL Output**: Advanced queries for AWS Config

## 🚀 Migration to Amazon Q Developer

### What is Amazon Q Developer?

Amazon Q Developer is AWS's AI-powered assistant that provides:
- Natural language querying across AWS services
- Chat-based interface for resource exploration
- Broader AWS service coverage
- Code generation and troubleshooting
- Integration with AWS Console and CLI

### Migration Steps

#### 1. Access Amazon Q Developer

**Via AWS Console:**
```
1. Open AWS Console
2. Click the Amazon Q icon (bottom right)
3. Start asking questions about your resources
```

**Via AWS CLI:**
```bash
# Install Amazon Q CLI
pip install amazon-q-developer-cli

# Configure
q configure

# Query resources
q "Show me all EC2 instances"
```

#### 2. Update Queries

**Old (AWS Config Natural Language):**
```
Navigate to: AWS Config > Advanced Queries > Natural Language
Enter: "Show me all S3 buckets without versioning"
```

**New (Amazon Q Developer):**
```
Open Amazon Q in Console
Ask: "Which S3 buckets don't have versioning enabled?"
```

#### 3. Programmatic Access

**Old Approach (AWS Config API):**
```python
# This was in preview and not widely used
config_client = boto3.client('config')
# Natural language feature had limited API access
```

**New Approach (Amazon Q):**
```python
# Use Amazon Q Developer API
import boto3

q_client = boto3.client('q-developer')
response = q_client.query(
    query="Show me all non-compliant resources",
    context="AWS Config compliance"
)
```

## 📊 Feature Comparison

| Feature | AWS Config NL Query | Amazon Q Developer |
|---------|---------------------|-------------------|
| Status | Discontinuing Jan 2026 | Generally Available |
| Regions | US-East, US-West | All regions |
| Interface | AWS Config console | Console, CLI, IDE |
| Query Types | Config data only | All AWS services |
| SQL Output | Yes | Yes |
| Code Help | No | Yes |
| Troubleshooting | No | Yes |
| Cost | Free (preview) | Pay per query |

## 🔧 Recommended Actions

### Before January 15, 2026

- [ ] Identify any processes using AWS Config natural language queries
- [ ] Test equivalent queries in Amazon Q Developer
- [ ] Update internal documentation
- [ ] Train team on Amazon Q Developer
- [ ] Update automation scripts if needed
- [ ] Review Amazon Q pricing for your use case

### Alternative Query Methods

If you don't want to use Amazon Q Developer, alternatives include:

#### 1. AWS Config Advanced Queries (SQL)
```sql
SELECT
  resourceId,
  resourceType,
  configuration.instanceType,
  configuration.state.name
FROM
  aws_ec2_instance
WHERE
  configuration.state.name = 'running'
```

#### 2. AWS CLI with JMESPath
```bash
aws configservice select-resource-config \
  --expression "SELECT resourceId WHERE resourceType='AWS::EC2::Instance'"
```

#### 3. AWS SDK (Boto3)
```python
import boto3

config = boto3.client('config')
response = config.select_resource_config(
    Expression="""
        SELECT resourceId, resourceType
        WHERE resourceType = 'AWS::EC2::Instance'
    """
)
```

#### 4. AWS Resource Explorer
```bash
# Search resources across your organization
aws resource-explorer-2 search \
  --query-string "resourceType:EC2::Instance"
```

## 💡 Amazon Q Developer Quick Start

### Installation

**Console Access:**
- Already available in AWS Console (no installation needed)
- Look for the Q icon in bottom-right corner

**CLI Installation:**
```bash
# Install via pip
pip install amazon-q-developer-cli

# Or via npm
npm install -g @aws/amazon-q-developer-cli

# Configure
q configure
```

**IDE Integration:**
```bash
# VS Code
1. Install "Amazon Q" extension from VS Code marketplace
2. Sign in with AWS Builder ID or IAM credentials
3. Start querying from command palette (Cmd/Ctrl + Shift + P)

# JetBrains IDEs
1. Install "Amazon Q" plugin
2. Configure AWS credentials
3. Use Q panel to ask questions
```

### Example Queries in Amazon Q

**Resource Discovery:**
```
"Show me all my Lambda functions"
"List S3 buckets created in the last 30 days"
"Find EC2 instances without tags"
```

**Compliance & Security:**
```
"Which resources are non-compliant?"
"Show me publicly accessible S3 buckets"
"Find EC2 instances with open security groups"
```

**Cost Optimization:**
```
"What resources are costing me the most?"
"Show me idle EC2 instances"
"Find unused Elastic IPs"
```

**Code Generation:**
```
"Generate Python code to list all S3 buckets"
"Create a Lambda function to process S3 events"
"Write Terraform for an EC2 instance"
```

## 📚 Resources

### AWS Config Documentation
- [AWS Config Advanced Queries](https://docs.aws.amazon.com/config/latest/developerguide/querying-AWS-resources.html)
- [Query Assistant Deprecation](https://docs.aws.amazon.com/config/latest/developerguide/query-assistant.html)
- [Example Queries](https://docs.aws.amazon.com/config/latest/developerguide/example-query.html)

### Amazon Q Developer Documentation
- [Amazon Q Developer Overview](https://aws.amazon.com/q/developer/)
- [Getting Started Guide](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/what-is.html)
- [CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/q/)
- [Pricing Information](https://aws.amazon.com/q/developer/pricing/)

### Migration Guides
- [AWS Blog: Natural Language Queries](https://aws.amazon.com/blogs/mt/simplify-query-authoring-in-aws-config-advanced-queries-with-natural-language-query-generation/)
- [Transition to Amazon Q](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-aws-builder-center-amazon-q-oracle-databaseaws-and-more-july-14-2025/)

## 🎯 Best Practices

### 1. Start Early
Begin testing Amazon Q Developer now to ensure smooth transition.

### 2. Document Custom Queries
If you have complex AWS Config natural language queries, document them and test equivalents in Amazon Q.

### 3. Train Your Team
Schedule training sessions for your team on Amazon Q Developer before the deprecation date.

### 4. Cost Planning
Review Amazon Q Developer pricing and plan your query usage accordingly.

### 5. Automation Updates
Update any automated processes that rely on AWS Config natural language queries.

## 🔒 Security Considerations

### Amazon Q Permissions
Amazon Q Developer requires appropriate IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "q:Query",
        "q:GetConversation",
        "q:SendMessage"
      ],
      "Resource": "*"
    }
  ]
}
```

### Data Privacy
- Amazon Q respects your AWS IAM permissions
- Queries are scoped to resources you have access to
- No data leaves your AWS account without authorization

## 💰 Pricing

### AWS Config Natural Language Query
- **Cost**: Free (during preview)
- **After deprecation**: N/A

### Amazon Q Developer
- **Free Tier**: Limited queries per month
- **Pro Plan**: $19/user/month (as of 2025)
- **Enterprise**: Custom pricing

**Note**: Check [current pricing](https://aws.amazon.com/q/developer/pricing/) for latest rates.

## 🆘 Support

### Getting Help with Migration

**AWS Support:**
- Contact your AWS account team
- Open a support case
- AWS re:Post community

**Amazon Q Developer:**
- In-product help and examples
- Documentation at docs.aws.amazon.com/amazonq
- Community forums and GitHub

## ✅ Migration Checklist

Use this checklist to track your migration:

### Discovery Phase
- [ ] Identify all uses of AWS Config natural language queries
- [ ] Document existing query patterns
- [ ] List affected teams and processes
- [ ] Review automation dependencies

### Testing Phase
- [ ] Set up Amazon Q Developer access
- [ ] Test equivalent queries in Amazon Q
- [ ] Validate query results match expectations
- [ ] Test API integrations if applicable
- [ ] Measure performance and cost

### Implementation Phase
- [ ] Update internal documentation
- [ ] Train team members
- [ ] Update automation scripts
- [ ] Implement new query methods
- [ ] Test in staging environment

### Validation Phase
- [ ] Verify all queries work in Amazon Q
- [ ] Confirm team adoption
- [ ] Monitor usage and costs
- [ ] Gather feedback

### Completion Phase
- [ ] Remove old AWS Config natural language references
- [ ] Update runbooks and procedures
- [ ] Archive old documentation
- [ ] Confirm no dependencies on deprecated feature

## 🎓 Training Resources

### Online Courses
- AWS Skill Builder: Amazon Q Developer course
- YouTube: AWS Amazon Q tutorials
- AWS Workshops: Hands-on labs

### Documentation
- [Amazon Q Developer User Guide](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/)
- [API Reference](https://docs.aws.amazon.com/amazonq/latest/APIReference/)
- [Best Practices Guide](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/best-practices.html)

## 📝 Summary

**Key Takeaways:**
- AWS Config natural language querying ends January 15, 2026
- Migrate to Amazon Q Developer for enhanced capabilities
- Alternative methods include SQL queries, AWS CLI, and Resource Explorer
- Start migration early to ensure smooth transition
- Amazon Q Developer offers more features beyond just querying

**Action Required:**
Begin planning your migration to Amazon Q Developer or alternative query methods **before January 15, 2026**.

---

**Last Updated**: November 2025
**Status**: Deprecation Notice Active
**Next Review**: December 2025
