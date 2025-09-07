#!/bin/bash
# AWS Secrets Manager setup script for Big Mann Entertainment
# Sets up environment-specific secrets for multi-environment deployment

set -e

ENVIRONMENT=$1
AWS_REGION="us-east-1"

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <environment>"
    echo "Environment must be one of: development, staging, production"
    exit 1
fi

echo "🔐 Setting up secrets for environment: $ENVIRONMENT"

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    echo "🔑 Processing secret: $secret_name"
    
    # Check if secret exists
    if aws secretsmanager describe-secret --secret-id "$secret_name" --region $AWS_REGION >/dev/null 2>&1; then
        echo "   ↻ Updating existing secret: $secret_name"
        aws secretsmanager update-secret \
            --secret-id "$secret_name" \
            --secret-string "$secret_value" \
            --region $AWS_REGION >/dev/null
    else
        echo "   + Creating new secret: $secret_name"
        aws secretsmanager create-secret \
            --name "$secret_name" \
            --description "$description" \
            --secret-string "$secret_value" \
            --region $AWS_REGION >/dev/null
    fi
    
    echo "   ✅ Secret processed successfully"
}

# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)

# Database secrets
echo "📊 Setting up database secrets..."
DB_SECRET=$(cat <<EOF
{
    "connection_string": "mongodb://localhost:27017",
    "database_name": "bigmann_entertainment_${ENVIRONMENT}",
    "username": "bigmann_${ENVIRONMENT}",
    "password": "$(openssl rand -base64 24)"
}
EOF
)

create_or_update_secret \
    "bigmann/${ENVIRONMENT}/database" \
    "$DB_SECRET" \
    "MongoDB Atlas credentials for $ENVIRONMENT"

# Stripe secrets
echo "💳 Setting up Stripe secrets..."
STRIPE_SECRET=$(cat <<EOF
{
    "publishable_key": "pk_test_$(openssl rand -hex 32)",
    "secret_key": "sk_test_$(openssl rand -hex 32)",
    "webhook_secret": "whsec_$(openssl rand -hex 32)"
}
EOF
)

create_or_update_secret \
    "bigmann/${ENVIRONMENT}/stripe" \
    "$STRIPE_SECRET" \
    "Stripe API credentials for $ENVIRONMENT"

# PayPal secrets
echo "💰 Setting up PayPal secrets..."
PAYPAL_ENV=$([ "$ENVIRONMENT" = "production" ] && echo "live" || echo "sandbox")
PAYPAL_SECRET=$(cat <<EOF
{
    "client_id": "paypal_client_id_$(openssl rand -hex 16)",
    "client_secret": "paypal_client_secret_$(openssl rand -hex 32)",
    "environment": "$PAYPAL_ENV"
}
EOF
)

create_or_update_secret \
    "bigmann/${ENVIRONMENT}/paypal" \
    "$PAYPAL_SECRET" \
    "PayPal API credentials for $ENVIRONMENT"

# Web3 secrets
echo "🔗 Setting up Web3 secrets..."
WEB3_NETWORK=$([ "$ENVIRONMENT" = "production" ] && echo "mainnet" || echo "goerli")
WEB3_SECRET=$(cat <<EOF
{
    "provider_url": "https://eth-${WEB3_NETWORK}.alchemyapi.io/v2/$(openssl rand -hex 16)",
    "private_key": "0x$(openssl rand -hex 32)",
    "contract_addresses": {
        "nft": "0x$(openssl rand -hex 20)",
        "token": "0x$(openssl rand -hex 20)"
    }
}
EOF
)

create_or_update_secret \
    "bigmann/${ENVIRONMENT}/web3" \
    "$WEB3_SECRET" \
    "Web3 configuration for $ENVIRONMENT"

# JWT secrets
echo "🎫 Setting up JWT secrets..."
JWT_SECRET_JSON=$(cat <<EOF
{
    "secret_key": "$JWT_SECRET",
    "algorithm": "HS256",
    "expiration_hours": 24
}
EOF
)

create_or_update_secret \
    "bigmann/${ENVIRONMENT}/jwt" \
    "$JWT_SECRET_JSON" \
    "JWT signing secret for $ENVIRONMENT"

# AWS configuration secrets
echo "☁️ Setting up AWS configuration secrets..."
AWS_CONFIG_SECRET=$(cat <<EOF
{
    "s3_bucket_name": "bigmann-media-${ENVIRONMENT}-$(aws sts get-caller-identity --query Account --output text)",
    "cloudfront_domain": "${ENVIRONMENT}.bigmannentertainment.com",
    "ses_verified_sender": "no-reply@bigmannentertainment.com"
}
EOF
)

create_or_update_secret \
    "bigmann/${ENVIRONMENT}/aws-config" \
    "$AWS_CONFIG_SECRET" \
    "AWS configuration for $ENVIRONMENT"

# Application configuration secrets
echo "⚙️ Setting up application configuration secrets..."
APP_CONFIG_SECRET=$(cat <<EOF
{
    "cors_origins": $([ "$ENVIRONMENT" = "production" ] && echo '["https://bigmannentertainment.com"]' || echo '["http://localhost:3000", "https://'$ENVIRONMENT'.bigmannentertainment.com"]'),
    "debug_mode": $([ "$ENVIRONMENT" = "development" ] && echo "true" || echo "false"),
    "log_level": $([ "$ENVIRONMENT" = "production" ] && echo '"ERROR"' || [ "$ENVIRONMENT" = "staging" ] && echo '"INFO"' || echo '"DEBUG"'),
    "feature_flags": {
        "enable_web3_features": $([ "$ENVIRONMENT" = "development" ] && echo "false" || echo "true"),
        "enable_nft_minting": $([ "$ENVIRONMENT" = "development" ] && echo "false" || echo "true"),
        "enable_payment_processing": true
    }
}
EOF
)

create_or_update_secret \
    "bigmann/${ENVIRONMENT}/app-config" \
    "$APP_CONFIG_SECRET" \
    "Application configuration for $ENVIRONMENT"

echo ""
echo "🎉 Secrets setup completed for $ENVIRONMENT environment"
echo ""
echo "📋 Summary of created/updated secrets:"
echo "   • bigmann/${ENVIRONMENT}/database - MongoDB credentials"
echo "   • bigmann/${ENVIRONMENT}/stripe - Stripe API keys"
echo "   • bigmann/${ENVIRONMENT}/paypal - PayPal credentials"
echo "   • bigmann/${ENVIRONMENT}/web3 - Web3 configuration"
echo "   • bigmann/${ENVIRONMENT}/jwt - JWT signing secret"
echo "   • bigmann/${ENVIRONMENT}/aws-config - AWS service configuration"
echo "   • bigmann/${ENVIRONMENT}/app-config - Application settings"
echo ""
echo "⚠️ IMPORTANT:"
echo "   1. Update the actual API keys in AWS Secrets Manager console"
echo "   2. Configure MongoDB Atlas connection string"
echo "   3. Set up proper Stripe webhook endpoints"
echo "   4. Configure PayPal sandbox/live credentials"
echo "   5. Update Web3 provider URLs and private keys"
echo ""
echo "🔗 Access secrets in AWS Console:"
echo "   https://console.aws.amazon.com/secretsmanager/home?region=${AWS_REGION}#!/listSecrets/"