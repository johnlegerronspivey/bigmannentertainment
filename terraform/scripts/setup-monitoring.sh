#!/bin/bash
# Setup CloudWatch Monitoring Dashboards
# Creates comprehensive monitoring for all infrastructure

set -e

echo "📊 Setting up CloudWatch Monitoring Dashboards"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="bme-agency"
AWS_REGION=${AWS_REGION:-us-east-1}
ENVIRONMENT=${1:-dev}

echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"
echo -e "${BLUE}Region: $AWS_REGION${NC}"
echo ""

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials valid${NC}"

# Get infrastructure outputs
cd ..
echo ""
echo "📥 Getting infrastructure outputs..."

S3_BUCKET=$(terraform output -raw portfolio_bucket_name 2>/dev/null || echo "")
CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id 2>/dev/null || echo "")
DYNAMODB_TABLE=$(terraform output -raw license_registry_table_name 2>/dev/null || echo "")
LAMBDA_ARN=$(terraform output -raw metadata_parser_function_arn 2>/dev/null || echo "")

if [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}❌ No infrastructure deployed. Run ./deploy-dev.sh first${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Infrastructure outputs retrieved${NC}"

# Create Main Dashboard
echo ""
echo "📊 Creating main monitoring dashboard..."

DASHBOARD_NAME="${PROJECT_NAME}-${ENVIRONMENT}-main"

aws cloudwatch put-dashboard \
    --dashboard-name "$DASHBOARD_NAME" \
    --region "$AWS_REGION" \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/S3", "BucketSizeBytes", {"stat": "Average", "label": "Portfolio Storage"}],
                        [".", "NumberOfObjects", {"stat": "Average"}]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "'"$AWS_REGION"'",
                    "title": "S3 Storage Metrics",
                    "yAxis": {"left": {"label": "Bytes"}},
                    "width": 12,
                    "height": 6
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/CloudFront", "Requests", {"stat": "Sum"}],
                        [".", "BytesDownloaded", {"stat": "Sum"}],
                        [".", "4xxErrorRate", {"stat": "Average"}],
                        [".", "5xxErrorRate", {"stat": "Average"}]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "'"$AWS_REGION"'",
                    "title": "CloudFront Performance",
                    "width": 12,
                    "height": 6
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/DynamoDB", "ConsumedReadCapacityUnits", {"stat": "Sum"}],
                        [".", "ConsumedWriteCapacityUnits", {"stat": "Sum"}],
                        [".", "UserErrors", {"stat": "Sum"}],
                        [".", "SystemErrors", {"stat": "Sum"}]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "'"$AWS_REGION"'",
                    "title": "DynamoDB Performance",
                    "width": 12,
                    "height": 6
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
                        [".", "Errors", {"stat": "Sum"}],
                        [".", "Duration", {"stat": "Average"}],
                        [".", "ConcurrentExecutions", {"stat": "Maximum"}]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "'"$AWS_REGION"'",
                    "title": "Lambda Functions",
                    "width": 12,
                    "height": 6
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Cognito", "UserAuthentication", {"stat": "Sum"}],
                        [".", "SignInSuccesses", {"stat": "Sum"}],
                        [".", "SignInThrottles", {"stat": "Sum"}]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "'"$AWS_REGION"'",
                    "title": "Cognito Authentication",
                    "width": 12,
                    "height": 6
                }
            },
            {
                "type": "log",
                "properties": {
                    "query": "SOURCE '\''/aws/lambda/ImageMetadataParser'\'' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20",
                    "region": "'"$AWS_REGION"'",
                    "title": "Recent Errors",
                    "width": 24,
                    "height": 6
                }
            }
        ]
    }'

echo -e "${GREEN}✓ Main dashboard created: $DASHBOARD_NAME${NC}"

# Create Cost Dashboard
echo ""
echo "💰 Creating cost monitoring dashboard..."

COST_DASHBOARD_NAME="${PROJECT_NAME}-${ENVIRONMENT}-costs"

aws cloudwatch put-dashboard \
    --dashboard-name "$COST_DASHBOARD_NAME" \
    --region "$AWS_REGION" \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Billing", "EstimatedCharges", {"stat": "Maximum"}]
                    ],
                    "period": 21600,
                    "stat": "Maximum",
                    "region": "us-east-1",
                    "title": "Estimated Monthly Charges",
                    "yAxis": {"left": {"label": "USD"}},
                    "width": 24,
                    "height": 6
                }
            }
        ]
    }'

echo -e "${GREEN}✓ Cost dashboard created: $COST_DASHBOARD_NAME${NC}"

# Create CloudWatch Alarms
echo ""
echo "🔔 Creating CloudWatch alarms..."

# High error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "${PROJECT_NAME}-${ENVIRONMENT}-high-error-rate" \
    --alarm-description "Alert when error rate is high" \
    --metric-name 5xxErrorRate \
    --namespace AWS/CloudFront \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 5.0 \
    --comparison-operator GreaterThanThreshold \
    --region "$AWS_REGION"

echo -e "${GREEN}✓ High error rate alarm created${NC}"

# DynamoDB throttling alarm
if [ -n "$DYNAMODB_TABLE" ]; then
    aws cloudwatch put-metric-alarm \
        --alarm-name "${PROJECT_NAME}-${ENVIRONMENT}-dynamodb-throttle" \
        --alarm-description "Alert when DynamoDB requests are throttled" \
        --metric-name UserErrors \
        --namespace AWS/DynamoDB \
        --dimensions Name=TableName,Value="$DYNAMODB_TABLE" \
        --statistic Sum \
        --period 300 \
        --evaluation-periods 2 \
        --threshold 10 \
        --comparison-operator GreaterThanThreshold \
        --region "$AWS_REGION"
    
    echo -e "${GREEN}✓ DynamoDB throttling alarm created${NC}"
fi

# Lambda error alarm
if [ -n "$LAMBDA_ARN" ]; then
    LAMBDA_NAME=$(echo "$LAMBDA_ARN" | awk -F: '{print $NF}')
    
    aws cloudwatch put-metric-alarm \
        --alarm-name "${PROJECT_NAME}-${ENVIRONMENT}-lambda-errors" \
        --alarm-description "Alert when Lambda functions have errors" \
        --metric-name Errors \
        --namespace AWS/Lambda \
        --dimensions Name=FunctionName,Value="$LAMBDA_NAME" \
        --statistic Sum \
        --period 300 \
        --evaluation-periods 1 \
        --threshold 5 \
        --comparison-operator GreaterThanThreshold \
        --region "$AWS_REGION"
    
    echo -e "${GREEN}✓ Lambda error alarm created${NC}"
fi

# Cost alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "${PROJECT_NAME}-${ENVIRONMENT}-high-costs" \
    --alarm-description "Alert when estimated charges exceed threshold" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --dimensions Name=Currency,Value=USD \
    --statistic Maximum \
    --period 21600 \
    --evaluation-periods 1 \
    --threshold 1000 \
    --comparison-operator GreaterThanThreshold \
    --region us-east-1

echo -e "${GREEN}✓ Cost alarm created${NC}"

# Create SNS topic for alerts (if not exists)
echo ""
echo "📧 Setting up SNS notifications..."

SNS_TOPIC_NAME="${PROJECT_NAME}-${ENVIRONMENT}-alerts"
SNS_TOPIC_ARN=$(aws sns create-topic --name "$SNS_TOPIC_NAME" --region "$AWS_REGION" --query 'TopicArn' --output text 2>/dev/null || echo "")

if [ -n "$SNS_TOPIC_ARN" ]; then
    echo -e "${GREEN}✓ SNS topic created: $SNS_TOPIC_ARN${NC}"
    
    # Subscribe email (optional)
    read -p "Enter email address for alerts (or press Enter to skip): " ALERT_EMAIL
    
    if [ -n "$ALERT_EMAIL" ]; then
        aws sns subscribe \
            --topic-arn "$SNS_TOPIC_ARN" \
            --protocol email \
            --notification-endpoint "$ALERT_EMAIL" \
            --region "$AWS_REGION"
        
        echo -e "${YELLOW}⚠️  Check your email and confirm the subscription${NC}"
    fi
fi

# Create Log Insights queries
echo ""
echo "📝 Creating CloudWatch Insights queries..."

# Save useful queries
mkdir -p ../monitoring-queries

cat > ../monitoring-queries/errors-last-hour.txt << 'EOF'
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
EOF

cat > ../monitoring-queries/slow-requests.txt << 'EOF'
fields @timestamp, @message, @duration
| filter @duration > 1000
| sort @duration desc
| limit 20
EOF

cat > ../monitoring-queries/user-activity.txt << 'EOF'
fields @timestamp, userIdentity.principalId, eventName
| filter eventSource = "s3.amazonaws.com"
| stats count() by eventName
| sort count desc
EOF

echo -e "${GREEN}✓ Query templates saved to monitoring-queries/${NC}"

# Generate monitoring report
echo ""
echo "📋 Generating monitoring report..."

cat > ../monitoring-report-${ENVIRONMENT}.md << EOF
# Monitoring Report - $ENVIRONMENT
Generated: $(date)

## CloudWatch Dashboards

### Main Dashboard
https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=$DASHBOARD_NAME

**Metrics Tracked:**
- S3 Storage (size, object count)
- CloudFront (requests, bandwidth, errors)
- DynamoDB (read/write capacity, errors)
- Lambda (invocations, errors, duration)
- Cognito (authentication events)

### Cost Dashboard
https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=$COST_DASHBOARD_NAME

**Metrics Tracked:**
- Estimated monthly charges
- Service-level cost breakdown

## CloudWatch Alarms

| Alarm | Threshold | Action |
|-------|-----------|--------|
| High Error Rate | 5% 5xx errors | SNS notification |
| DynamoDB Throttling | 10 throttled requests | SNS notification |
| Lambda Errors | 5 errors | SNS notification |
| High Costs | \$1,000/month | SNS notification |

## Log Groups

- \`/aws/lambda/ImageMetadataParser\` - Image processing logs
- \`/aws/cloudfront/$CLOUDFRONT_ID\` - CDN access logs
- \`/model-agency/platform\` - Application logs

## Useful Queries

### Find Errors (Last Hour)
\`\`\`
$(cat ../monitoring-queries/errors-last-hour.txt)
\`\`\`

### Slow Requests
\`\`\`
$(cat ../monitoring-queries/slow-requests.txt)
\`\`\`

## Next Steps

1. Subscribe to SNS topic for email alerts
2. Set up PagerDuty integration (optional)
3. Configure Slack notifications (optional)
4. Review dashboards daily
5. Set up automated reports

## Resources

- CloudWatch Console: https://console.aws.amazon.com/cloudwatch
- SNS Topic: $SNS_TOPIC_ARN
- Documentation: /terraform/monitoring-queries/

EOF

echo -e "${GREEN}✓ Monitoring report generated: monitoring-report-${ENVIRONMENT}.md${NC}"

# Display summary
echo ""
echo -e "${GREEN}✅ Monitoring Setup Complete!${NC}"
echo ""
echo "📊 Dashboards Created:"
echo "  Main: $DASHBOARD_NAME"
echo "  Cost: $COST_DASHBOARD_NAME"
echo ""
echo "🔔 Alarms Created:"
echo "  ✓ High error rate"
echo "  ✓ DynamoDB throttling"
echo "  ✓ Lambda errors"
echo "  ✓ High costs"
echo ""
echo "📧 SNS Topic:"
echo "  $SNS_TOPIC_ARN"
echo ""
echo "🔗 Quick Links:"
echo "  Dashboards: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:"
echo "  Alarms: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#alarmsV2:"
echo "  Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups"
echo ""
echo "📋 Report: monitoring-report-${ENVIRONMENT}.md"
echo ""

cd scripts
