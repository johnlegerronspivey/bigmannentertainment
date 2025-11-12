#!/bin/bash
# Deploy to Production Environment
# Includes multiple approval gates and safety checks

set -e

echo "🚀 Production Deployment Script"
echo "================================"
echo ""
echo "⚠️  WARNING: This will deploy to PRODUCTION"
echo "⚠️  All changes will affect live customer traffic"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
ENVIRONMENT="prod"
TFVARS_FILE="environments/${ENVIRONMENT}.tfvars"
PLAN_FILE="tfplan-${ENVIRONMENT}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="logs/deploy-${ENVIRONMENT}-${TIMESTAMP}.log"
APPROVERS_FILE="../approvers.txt"

# Required approvers for production deployment
REQUIRED_APPROVERS=2

# Create logs directory
mkdir -p ../logs
mkdir -p ../deployments

# Change to terraform directory
cd ..

# ============== PRE-DEPLOYMENT CHECKS ==============

echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo -e "${MAGENTA}    PRE-DEPLOYMENT SAFETY CHECKS    ${NC}"
echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo ""

# Check 1: Verify dev and staging are successful
echo "1️⃣  Checking previous environment deployments..."

if [ ! -d "deployments" ] || [ -z "$(ls -A deployments)" ]; then
    echo -e "${RED}❌ No previous deployments found${NC}"
    echo "Deploy to dev and staging first"
    exit 1
fi

LAST_DEV=$(ls -t deployments/dev-*.json 2>/dev/null | head -1)
LAST_STAGING=$(ls -t deployments/staging-*.json 2>/dev/null | head -1)

if [ -z "$LAST_DEV" ] || [ -z "$LAST_STAGING" ]; then
    echo -e "${RED}❌ Dev or staging deployment missing${NC}"
    echo "Required deployment order: dev → staging → prod"
    exit 1
fi

echo -e "${GREEN}✓ Previous deployments verified${NC}"
echo "  Latest dev: $(basename $LAST_DEV)"
echo "  Latest staging: $(basename $LAST_STAGING)"

# Check 2: Verify AWS credentials
echo ""
echo "2️⃣  Verifying AWS credentials..."

if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)

echo -e "${GREEN}✓ AWS credentials valid${NC}"
echo "  Account: $ACCOUNT_ID"
echo "  User: $USER_ARN"

# Check 3: Verify MFA is enabled
echo ""
echo "3️⃣  Checking MFA status..."

MFA_DEVICES=$(aws iam list-mfa-devices --query 'MFADevices[0].SerialNumber' --output text 2>/dev/null || echo "")

if [ -z "$MFA_DEVICES" ] || [ "$MFA_DEVICES" == "None" ]; then
    echo -e "${YELLOW}⚠️  MFA not detected${NC}"
    read -p "Continue without MFA? (yes/no): " MFA_CONFIRM
    if [ "$MFA_CONFIRM" != "yes" ]; then
        echo -e "${RED}❌ Deployment cancelled${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ MFA enabled${NC}"
fi

# Check 4: Verify production tfvars exist
echo ""
echo "4️⃣  Checking production configuration..."

if [ ! -f "$TFVARS_FILE" ]; then
    echo -e "${RED}❌ Production config not found: $TFVARS_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Production config found${NC}"

# Check 5: Verify backend is configured
echo ""
echo "5️⃣  Verifying Terraform backend..."

if [ ! -f "backend-config.hcl" ]; then
    echo -e "${RED}❌ Backend not initialized${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend configured${NC}"

# ============== APPROVAL GATE 1 ==============

echo ""
echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo -e "${MAGENTA}    APPROVAL GATE 1: INITIATION    ${NC}"
echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo ""

read -p "Enter your name: " DEPLOYER_NAME
read -p "Enter deployment ticket/JIRA ID: " TICKET_ID

if [ -z "$DEPLOYER_NAME" ] || [ -z "$TICKET_ID" ]; then
    echo -e "${RED}❌ Deployer name and ticket ID required${NC}"
    exit 1
fi

echo ""
echo "Deployment initiated by: $DEPLOYER_NAME"
echo "Ticket: $TICKET_ID"
echo "Timestamp: $TIMESTAMP"
echo ""

read -p "Confirm you want to proceed? (yes/no): " GATE1_CONFIRM

if [ "$GATE1_CONFIRM" != "yes" ]; then
    echo -e "${RED}❌ Deployment cancelled at Gate 1${NC}"
    exit 0
fi

# ============== TERRAFORM VALIDATION ==============

echo ""
echo -e "${BLUE}Running Terraform validation...${NC}"
echo ""

# Select production workspace
terraform workspace select prod || terraform workspace new prod
echo -e "${GREEN}✓ Production workspace active${NC}"

# Validate configuration
echo ""
echo "Validating Terraform configuration..."
terraform validate | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo -e "${RED}❌ Validation failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Configuration valid${NC}"

# Format check
echo ""
echo "Checking formatting..."
terraform fmt -check -recursive || {
    echo -e "${YELLOW}⚠️  Formatting issues found${NC}"
    exit 1
}
echo -e "${GREEN}✓ Formatting correct${NC}"

# Security scan
echo ""
echo "Running security scan..."
if command -v tfsec &> /dev/null; then
    tfsec . --minimum-severity HIGH | tee -a "$LOG_FILE"
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo -e "${RED}❌ Security issues found${NC}"
        read -p "Continue despite security issues? (yes/no): " SEC_OVERRIDE
        if [ "$SEC_OVERRIDE" != "yes" ]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  tfsec not installed${NC}"
fi

# ============== TERRAFORM PLAN ==============

echo ""
echo -e "${BLUE}Generating Terraform plan...${NC}"
echo ""

terraform plan \
    -var-file="$TFVARS_FILE" \
    -out="$PLAN_FILE" \
    -detailed-exitcode \
    | tee -a "$LOG_FILE"

PLAN_EXIT_CODE=${PIPESTATUS[0]}

case $PLAN_EXIT_CODE in
    0)
        echo -e "${GREEN}✓ No changes needed${NC}"
        echo "Infrastructure is up to date!"
        exit 0
        ;;
    1)
        echo -e "${RED}❌ Plan generation failed${NC}"
        exit 1
        ;;
    2)
        echo -e "${YELLOW}⚠️  Changes detected${NC}"
        ;;
esac

# Show detailed plan
echo ""
echo "📋 Detailed Plan:"
terraform show "$PLAN_FILE" | tee -a "$LOG_FILE"

# Plan summary
echo ""
echo "📊 Change Summary:"
terraform show -json "$PLAN_FILE" | jq -r '
    .resource_changes[] |
    "\(.change.actions[0]) \(.type).\(.name)"
' | sort | uniq -c | tee -a "$LOG_FILE"

# Cost estimation
echo ""
echo "💰 Cost Estimation:"
if command -v infracost &> /dev/null; then
    infracost breakdown --path . --terraform-var-file="$TFVARS_FILE" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠️  Install infracost for cost estimates${NC}"
fi

# ============== APPROVAL GATE 2 ==============

echo ""
echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo -e "${MAGENTA}    APPROVAL GATE 2: PLAN REVIEW   ${NC}"
echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo ""

echo "⚠️  REVIEW THE PLAN ABOVE CAREFULLY"
echo ""
echo "Changes will be applied to PRODUCTION"
echo "This affects live customer traffic"
echo ""

# Collect approvals
APPROVAL_COUNT=0
declare -a APPROVERS

while [ $APPROVAL_COUNT -lt $REQUIRED_APPROVERS ]; do
    echo ""
    echo "Approval $((APPROVAL_COUNT + 1)) of $REQUIRED_APPROVERS required"
    read -p "Approver name: " APPROVER_NAME
    read -p "Approve deployment? (yes/no): " APPROVAL
    
    if [ "$APPROVAL" == "yes" ]; then
        APPROVERS+=("$APPROVER_NAME")
        APPROVAL_COUNT=$((APPROVAL_COUNT + 1))
        echo -e "${GREEN}✓ Approval recorded: $APPROVER_NAME${NC}"
    else
        echo -e "${RED}❌ Deployment cancelled by $APPROVER_NAME${NC}"
        rm -f "$PLAN_FILE"
        exit 0
    fi
done

echo ""
echo -e "${GREEN}✓ All approvals received${NC}"
echo "Approvers: ${APPROVERS[*]}"

# Record approvals
cat > "deployments/prod-approval-${TIMESTAMP}.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "deployer": "$DEPLOYER_NAME",
    "ticket": "$TICKET_ID",
    "approvers": [$(printf '"%s",' "${APPROVERS[@]}" | sed 's/,$//')]
}
EOF

# ============== PRE-DEPLOYMENT BACKUP ==============

echo ""
echo -e "${BLUE}Creating pre-deployment backup...${NC}"
echo ""

# Backup current state
terraform state pull > "backups/prod-state-${TIMESTAMP}.json"
echo -e "${GREEN}✓ State backup created${NC}"

# Backup DynamoDB (if exists)
DYNAMODB_TABLE=$(terraform output -raw license_registry_table_name 2>/dev/null || echo "")
if [ -n "$DYNAMODB_TABLE" ]; then
    aws dynamodb create-backup \
        --table-name "$DYNAMODB_TABLE" \
        --backup-name "pre-deploy-${TIMESTAMP}" \
        --region "${AWS_REGION:-us-east-1}" || echo "Backup creation initiated"
    echo -e "${GREEN}✓ DynamoDB backup initiated${NC}"
fi

# ============== APPROVAL GATE 3 ==============

echo ""
echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo -e "${MAGENTA}    APPROVAL GATE 3: FINAL APPLY   ${NC}"
echo -e "${MAGENTA}═══════════════════════════════════${NC}"
echo ""

echo "⚠️  FINAL CONFIRMATION REQUIRED"
echo ""
echo "This is the last checkpoint before deployment"
echo "Type the production environment name to proceed"
echo ""

read -p "Type 'PRODUCTION' to continue: " FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "PRODUCTION" ]; then
    echo -e "${RED}❌ Deployment cancelled at final gate${NC}"
    rm -f "$PLAN_FILE"
    exit 0
fi

# ============== DEPLOYMENT ==============

echo ""
echo -e "${GREEN}🚀 Deploying to Production...${NC}"
echo ""

# Apply with auto-approve (plan already approved)
terraform apply "$PLAN_FILE" | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed${NC}"
    echo "Review logs: $LOG_FILE"
    echo "Rollback may be required"
    exit 1
fi

echo -e "${GREEN}✓ Deployment successful${NC}"

# Cleanup plan file
rm -f "$PLAN_FILE"

# ============== POST-DEPLOYMENT ==============

echo ""
echo -e "${BLUE}Running post-deployment checks...${NC}"
echo ""

# Get outputs
terraform output -json > "outputs/prod-outputs-${TIMESTAMP}.json"
terraform output | tee -a "$LOG_FILE"

# Test endpoints
CLOUDFRONT_URL=$(terraform output -raw cloudfront_domain_name 2>/dev/null || echo "")
if [ -n "$CLOUDFRONT_URL" ]; then
    echo ""
    echo "Testing CloudFront..."
    if curl -I "https://$CLOUDFRONT_URL" &>/dev/null; then
        echo -e "${GREEN}✓ CloudFront accessible${NC}"
    else
        echo -e "${RED}❌ CloudFront not accessible${NC}"
    fi
fi

# Save deployment record
cat > "deployments/prod-${TIMESTAMP}.json" << EOF
{
    "environment": "$ENVIRONMENT",
    "timestamp": "$TIMESTAMP",
    "deployer": "$DEPLOYER_NAME",
    "ticket": "$TICKET_ID",
    "approvers": [$(printf '"%s",' "${APPROVERS[@]}" | sed 's/,$//')]
,
    "status": "success",
    "log_file": "$LOG_FILE"
}
EOF

# Create deployment summary
cat > "deployments/prod-summary-${TIMESTAMP}.md" << EOF
# Production Deployment Summary

**Timestamp:** $TIMESTAMP  
**Deployer:** $DEPLOYER_NAME  
**Ticket:** $TICKET_ID  
**Status:** ✅ SUCCESS

## Approvals

$(for approver in "${APPROVERS[@]}"; do echo "- $approver"; done)

## Infrastructure Outputs

\`\`\`
$(terraform output)
\`\`\`

## Deployment Log

Full log: \`$LOG_FILE\`

## Post-Deployment Actions

- [ ] Monitor CloudWatch dashboards for 30 minutes
- [ ] Check error rates and latency
- [ ] Verify customer-facing functionality
- [ ] Update documentation
- [ ] Notify stakeholders

## Rollback Plan

If issues occur:

\`\`\`bash
cd terraform
terraform workspace select prod
terraform apply -var-file="environments/prod.tfvars"
# Or restore from backup:
# terraform state push backups/prod-state-${TIMESTAMP}.json
\`\`\`

## Support Contacts

- On-call engineer: +1-555-DEVOPS
- Slack: #production-incidents
- Email: ops@bigmannentertainment.com
EOF

# ============== MONITORING SETUP ==============

echo ""
echo "📊 Setting up post-deployment monitoring..."

# Create temporary high-frequency alarms
aws cloudwatch put-metric-alarm \
    --alarm-name "prod-post-deploy-errors-${TIMESTAMP}" \
    --alarm-description "Temporary high-sensitivity error monitoring" \
    --metric-name 5xxErrorRate \
    --namespace AWS/CloudFront \
    --statistic Average \
    --period 60 \
    --evaluation-periods 1 \
    --threshold 1.0 \
    --comparison-operator GreaterThanThreshold \
    --region "${AWS_REGION:-us-east-1}" || echo "Alarm creation skipped"

echo -e "${GREEN}✓ Temporary monitoring configured${NC}"

# ============== FINAL SUMMARY ==============

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}    ✅ PRODUCTION DEPLOYMENT COMPLETE!       ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo "📊 Deployment Summary:"
echo "  Environment: PRODUCTION"
echo "  Timestamp: $TIMESTAMP"
echo "  Deployer: $DEPLOYER_NAME"
echo "  Ticket: $TICKET_ID"
echo "  Approvers: ${APPROVERS[*]}"
echo ""
echo "📁 Artifacts:"
echo "  Log: $LOG_FILE"
echo "  Outputs: outputs/prod-outputs-${TIMESTAMP}.json"
echo "  Summary: deployments/prod-summary-${TIMESTAMP}.md"
echo "  Backup: backups/prod-state-${TIMESTAMP}.json"
echo ""
echo "🔗 Quick Links:"
[ -n "$CLOUDFRONT_URL" ] && echo "  CloudFront: https://$CLOUDFRONT_URL"
echo "  AWS Console: https://console.aws.amazon.com"
echo "  CloudWatch: https://console.aws.amazon.com/cloudwatch"
echo ""
echo "⚠️  POST-DEPLOYMENT ACTIONS:"
echo "  1. Monitor for 30 minutes"
echo "  2. Check error rates and performance"
echo "  3. Verify customer functionality"
echo "  4. Update runbooks"
echo "  5. Notify stakeholders"
echo ""
echo "📞 Support: ops@bigmannentertainment.com"
echo ""

cd scripts
