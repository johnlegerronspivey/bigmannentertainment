#!/bin/bash
# Deploy to Development Environment
# Includes validation, planning, and deployment

set -e

echo "🚀 Deploying to Development Environment"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT="dev"
TFVARS_FILE="environments/${ENVIRONMENT}.tfvars"
PLAN_FILE="tfplan-${ENVIRONMENT}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="logs/deploy-${ENVIRONMENT}-${TIMESTAMP}.log"

# Create logs directory
mkdir -p ../logs

echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"
echo -e "${BLUE}Timestamp: $TIMESTAMP${NC}"
echo ""

# Change to terraform directory
cd ..

# Check if backend is initialized
echo "🔍 Checking backend initialization..."
if [ ! -f "backend-config.hcl" ]; then
    echo -e "${RED}❌ Backend not initialized${NC}"
    echo "Run ./scripts/initialize-backend.sh first"
    exit 1
fi
echo -e "${GREEN}✓ Backend configured${NC}"

# Check if tfvars file exists
if [ ! -f "$TFVARS_FILE" ]; then
    echo -e "${RED}❌ Environment file not found: $TFVARS_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Environment config found${NC}"

# Select dev workspace
echo ""
echo "🏗️  Selecting dev workspace..."
terraform workspace select dev || terraform workspace new dev
echo -e "${GREEN}✓ Dev workspace active${NC}"

# Validate Terraform configuration
echo ""
echo "✅ Validating Terraform configuration..."
terraform validate | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo -e "${RED}❌ Validation failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Configuration is valid${NC}"

# Format check
echo ""
echo "🎨 Checking Terraform formatting..."
terraform fmt -check -recursive || {
    echo -e "${YELLOW}⚠️  Formatting issues found. Auto-fixing...${NC}"
    terraform fmt -recursive
    echo -e "${GREEN}✓ Formatting applied${NC}"
}

# Security scan with tfsec
echo ""
echo "🔒 Running security scan..."
if command -v tfsec &> /dev/null; then
    tfsec . --soft-fail | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠️  tfsec not installed. Skipping security scan.${NC}"
    echo "Install: brew install tfsec"
fi

# Generate deployment plan
echo ""
echo "📋 Generating Terraform plan..."
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
        echo -e "${RED}❌ Plan failed${NC}"
        exit 1
        ;;
    2)
        echo -e "${YELLOW}⚠️  Changes detected${NC}"
        ;;
esac

# Show plan summary
echo ""
echo "📊 Plan Summary:"
terraform show -json "$PLAN_FILE" | jq -r '
    .resource_changes[] |
    "\(.change.actions[0]) \(.type).\(.name)"
' | sort | uniq -c | tee -a "$LOG_FILE"

# Cost estimation (if infracost is installed)
echo ""
echo "💰 Estimating costs..."
if command -v infracost &> /dev/null; then
    infracost breakdown --path . --terraform-var-file="$TFVARS_FILE" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠️  Infracost not installed. Skipping cost estimation.${NC}"
    echo "Install: brew install infracost"
fi

# Confirmation prompt
echo ""
echo -e "${YELLOW}⚠️  This will deploy changes to DEV environment${NC}"
echo "Review the plan above carefully."
echo ""
read -p "Do you want to proceed with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}❌ Deployment cancelled${NC}"
    rm -f "$PLAN_FILE"
    exit 0
fi

# Apply the plan
echo ""
echo "🚀 Applying Terraform plan..."
terraform apply "$PLAN_FILE" | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Deployment successful${NC}"

# Cleanup plan file
rm -f "$PLAN_FILE"

# Get outputs
echo ""
echo "📤 Terraform Outputs:"
terraform output -json > "outputs/dev-outputs-${TIMESTAMP}.json"
terraform output | tee -a "$LOG_FILE"

# Save deployment info
cat > "deployments/dev-${TIMESTAMP}.json" << EOF
{
    "environment": "$ENVIRONMENT",
    "timestamp": "$TIMESTAMP",
    "workspace": "dev",
    "status": "success",
    "log_file": "$LOG_FILE"
}
EOF

# Test deployment
echo ""
echo "🧪 Testing deployment..."

# Get CloudFront URL from outputs
CLOUDFRONT_URL=$(terraform output -raw cloudfront_domain_name 2>/dev/null || echo "")
if [ -n "$CLOUDFRONT_URL" ]; then
    echo "Testing CloudFront: https://$CLOUDFRONT_URL"
    curl -I "https://$CLOUDFRONT_URL" &>/dev/null && echo -e "${GREEN}✓ CloudFront accessible${NC}" || echo -e "${YELLOW}⚠️  CloudFront not yet ready${NC}"
fi

# Get Cognito User Pool
COGNITO_POOL_ID=$(terraform output -raw cognito_user_pool_id 2>/dev/null || echo "")
if [ -n "$COGNITO_POOL_ID" ]; then
    echo -e "${GREEN}✓ Cognito User Pool: $COGNITO_POOL_ID${NC}"
fi

# Get S3 bucket
S3_BUCKET=$(terraform output -raw portfolio_bucket_name 2>/dev/null || echo "")
if [ -n "$S3_BUCKET" ]; then
    echo -e "${GREEN}✓ Portfolio Bucket: $S3_BUCKET${NC}"
    # Test S3 access
    aws s3 ls "s3://$S3_BUCKET" &>/dev/null && echo -e "${GREEN}✓ S3 bucket accessible${NC}" || echo -e "${YELLOW}⚠️  S3 access check failed${NC}"
fi

# Display deployment summary
echo ""
echo -e "${GREEN}✅ Development Deployment Complete!${NC}"
echo ""
echo "📊 Deployment Summary:"
echo "  Environment: $ENVIRONMENT"
echo "  Timestamp: $TIMESTAMP"
echo "  Log: $LOG_FILE"
echo "  Outputs: outputs/dev-outputs-${TIMESTAMP}.json"
echo ""
echo "🔗 Quick Links:"
echo "  AWS Console: https://console.aws.amazon.com"
echo "  S3 Bucket: https://s3.console.aws.amazon.com/s3/buckets/$S3_BUCKET"
[ -n "$CLOUDFRONT_URL" ] && echo "  CloudFront: https://$CLOUDFRONT_URL"
echo ""
echo "Next steps:"
echo "1. Test the deployment: ./test-deployment.sh dev"
echo "2. Set up monitoring: ./setup-monitoring.sh"
echo "3. Deploy to staging: ./deploy-staging.sh"
echo ""

cd scripts
