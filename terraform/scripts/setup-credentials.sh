#!/bin/bash
# Secure AWS Credentials Setup Script
# This script configures AWS credentials and sets up MFA

set -e

echo "🔐 AWS Credentials Secure Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install awscli
    else
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    fi
fi

# Check AWS CLI version
echo -e "${GREEN}✓ AWS CLI version:${NC}"
aws --version

echo ""
echo "📝 Enter your AWS credentials"
echo "You can find these in AWS Console → IAM → Users → Security credentials"
echo ""

# Prompt for credentials
read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -sp "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
echo ""
read -p "Default region [us-east-1]: " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# Configure AWS CLI
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
aws configure set region "$AWS_REGION"
aws configure set output json

echo -e "${GREEN}✓ AWS credentials configured${NC}"

# Test credentials
echo ""
echo "🧪 Testing credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo -e "${GREEN}✓ Credentials are valid${NC}"
    aws sts get-caller-identity
else
    echo -e "${RED}❌ Invalid credentials. Please check and try again.${NC}"
    exit 1
fi

# Setup MFA (optional)
echo ""
read -p "Do you want to configure MFA? (y/n): " SETUP_MFA

if [[ "$SETUP_MFA" == "y" ]]; then
    read -p "MFA Device ARN (from IAM console): " MFA_ARN
    read -p "Enter MFA token code: " MFA_TOKEN
    
    # Get temporary credentials with MFA
    TEMP_CREDS=$(aws sts get-session-token \
        --serial-number "$MFA_ARN" \
        --token-code "$MFA_TOKEN" \
        --duration-seconds 43200)
    
    TEMP_ACCESS_KEY=$(echo $TEMP_CREDS | jq -r '.Credentials.AccessKeyId')
    TEMP_SECRET_KEY=$(echo $TEMP_CREDS | jq -r '.Credentials.SecretAccessKey')
    TEMP_SESSION_TOKEN=$(echo $TEMP_CREDS | jq -r '.Credentials.SessionToken')
    
    # Create MFA profile
    aws configure set aws_access_key_id "$TEMP_ACCESS_KEY" --profile mfa
    aws configure set aws_secret_access_key "$TEMP_SECRET_KEY" --profile mfa
    aws configure set aws_session_token "$TEMP_SESSION_TOKEN" --profile mfa
    aws configure set region "$AWS_REGION" --profile mfa
    
    echo -e "${GREEN}✓ MFA profile created${NC}"
    echo -e "${YELLOW}⚠️  Use --profile mfa for AWS CLI commands${NC}"
fi

# Setup GitHub Secrets (for CI/CD)
echo ""
echo "📦 GitHub Secrets Setup"
echo "Add these secrets to your GitHub repository:"
echo "Settings → Secrets and variables → Actions → New repository secret"
echo ""
echo -e "${YELLOW}AWS_ACCESS_KEY_ID:${NC} $AWS_ACCESS_KEY_ID"
echo -e "${YELLOW}AWS_SECRET_ACCESS_KEY:${NC} [REDACTED - Check your secure storage]"
echo ""

# Create encrypted credentials file for team
echo ""
read -p "Do you want to create an encrypted credentials file for your team? (y/n): " CREATE_ENCRYPTED

if [[ "$CREATE_ENCRYPTED" == "y" ]]; then
    # Create credentials file
    cat > .aws_credentials_encrypted << EOF
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_REGION=$AWS_REGION
EOF
    
    # Encrypt with GPG
    if command -v gpg &> /dev/null; then
        read -p "Enter encryption passphrase: " PASSPHRASE
        gpg --symmetric --cipher-algo AES256 --passphrase "$PASSPHRASE" .aws_credentials_encrypted
        rm .aws_credentials_encrypted
        echo -e "${GREEN}✓ Encrypted credentials saved to .aws_credentials_encrypted.gpg${NC}"
        echo -e "${YELLOW}⚠️  Share this file and passphrase securely with your team${NC}"
    else
        echo -e "${YELLOW}⚠️  GPG not found. Install it for encryption: brew install gnupg${NC}"
    fi
fi

# Setup credential rotation reminder
echo ""
echo "🔄 Credential Rotation"
echo "Set a reminder to rotate these credentials in 90 days"
ROTATION_DATE=$(date -v+90d "+%Y-%m-%d" 2>/dev/null || date -d "+90 days" "+%Y-%m-%d")
echo "Rotation due: $ROTATION_DATE"

# Create .env file for local development
cat > ../backend/.env.aws << EOF
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_REGION=$AWS_REGION
AWS_S3_BUCKET=bme-agency-portfolio-dev
AWS_COGNITO_USER_POOL_ID=to-be-created
EOF

echo -e "${GREEN}✓ Local .env.aws file created${NC}"

# Add to .gitignore
if ! grep -q ".env.aws" ../../.gitignore 2>/dev/null; then
    echo ".env.aws" >> ../../.gitignore
    echo ".aws_credentials_encrypted.gpg" >> ../../.gitignore
    echo -e "${GREEN}✓ Added to .gitignore${NC}"
fi

echo ""
echo -e "${GREEN}✅ AWS credentials setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Run: ./initialize-backend.sh"
echo "2. Run: ./deploy-dev.sh"
echo ""
