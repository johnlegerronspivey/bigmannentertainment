#!/bin/bash
# AWS Multi-Environment Deployment Script for Big Mann Entertainment
# Based on the comprehensive deployment playbook

set -e

ENVIRONMENT=$1
COMPONENT=$2
VERSION=$3

if [ -z "$ENVIRONMENT" ] || [ -z "$COMPONENT" ]; then
    echo "Usage: $0 <environment> <component> [version]"
    echo "Environments: development, staging, production"
    echo "Components: frontend, backend, infrastructure, all"
    exit 1
fi

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
DEPLOYMENT_ID="${ENVIRONMENT}-${COMPONENT}-${TIMESTAMP}"

echo "🚀 Starting Big Mann Entertainment deployment: $DEPLOYMENT_ID"
echo "Environment: $ENVIRONMENT"
echo "Component: $COMPONENT"
echo "Version: ${VERSION:-latest}"
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"

# Validation functions
validate_environment() {
    case $ENVIRONMENT in
        development|staging|production)
            echo "✅ Valid environment: $ENVIRONMENT"
            ;;
        *)
            echo "❌ Invalid environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
}

check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not installed"
        exit 1
    fi
    
    # Check CDK
    if ! command -v cdk &> /dev/null; then
        echo "❌ AWS CDK not installed"
        exit 1
    fi
    
    # Check Docker (if needed for backend)
    if [ "$COMPONENT" = "backend" ] || [ "$COMPONENT" = "all" ]; then
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not installed"
            exit 1
        fi
    fi
    
    # Check Node.js and Yarn (if needed for frontend)
    if [ "$COMPONENT" = "frontend" ] || [ "$COMPONENT" = "all" ]; then
        if ! command -v node &> /dev/null; then
            echo "❌ Node.js not installed"
            exit 1
        fi
        if ! command -v yarn &> /dev/null; then
            echo "❌ Yarn not installed"
            exit 1
        fi
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "❌ AWS credentials not configured"
        exit 1
    fi
    
    echo "✅ Prerequisites validated"
}

deploy_infrastructure() {
    echo "🏗️ Deploying infrastructure to $ENVIRONMENT..."
    
    cd /app/aws-infrastructure
    
    # Install dependencies
    echo "📦 Installing CDK dependencies..."
    npm install
    
    # Bootstrap CDK (if needed)
    echo "🎯 Bootstrapping CDK environment..."
    cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION || echo "CDK already bootstrapped"
    
    # Deploy the environment stack
    STACK_NAME="BigMann-${ENVIRONMENT^}"
    echo "🚀 Deploying stack: $STACK_NAME"
    
    cdk deploy $STACK_NAME --require-approval never --tags Environment=$ENVIRONMENT,Project=BigMannEntertainment,DeploymentId=$DEPLOYMENT_ID
    
    echo "✅ Infrastructure deployment completed for $ENVIRONMENT"
}

deploy_backend() {
    echo "🔧 Deploying backend to $ENVIRONMENT..."
    
    cd /app/backend
    
    # Build and tag Docker image
    IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/bigmann-fastapi-$ENVIRONMENT"
    IMAGE_TAG="${VERSION:-$TIMESTAMP}"
    
    echo "📦 Building Docker image: $IMAGE_URI:$IMAGE_TAG"
    docker build -t "$IMAGE_URI:$IMAGE_TAG" .
    docker tag "$IMAGE_URI:$IMAGE_TAG" "$IMAGE_URI:latest"
    
    # Login to ECR
    echo "🔐 Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | \
        docker login --username AWS --password-stdin \
        "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Push image
    echo "⬆️ Pushing image to ECR..."
    docker push "$IMAGE_URI:$IMAGE_TAG"
    docker push "$IMAGE_URI:latest"
    
    echo "✅ Backend deployment completed"
}

deploy_frontend() {
    echo "🎨 Deploying frontend to $ENVIRONMENT..."
    
    cd /app/frontend
    
    # Install dependencies
    echo "📦 Installing frontend dependencies..."
    yarn install
    
    # Build React application
    echo "🏗️ Building React application for $ENVIRONMENT..."
    yarn build:$ENVIRONMENT
    
    # Upload to S3
    S3_BUCKET="bigmann-frontend-$ENVIRONMENT-$AWS_ACCOUNT_ID"
    echo "⬆️ Uploading to S3 bucket: $S3_BUCKET"
    
    # Upload files with long cache for assets
    aws s3 sync build/ "s3://$S3_BUCKET/" \
        --delete \
        --cache-control "public, max-age=31536000" \
        --exclude "*.html" \
        --exclude "service-worker.js"
    
    # Upload HTML files with short cache
    aws s3 sync build/ "s3://$S3_BUCKET/" \
        --delete \
        --cache-control "public, max-age=0, must-revalidate" \
        --include "*.html" \
        --include "service-worker.js"
    
    # Invalidate CloudFront distribution
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --stack-name "BigMann-${ENVIRONMENT^}" \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
        --output text --region $AWS_REGION)
    
    if [ -n "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
        echo "🔄 Creating CloudFront invalidation..."
        INVALIDATION_ID=$(aws cloudfront create-invalidation \
            --distribution-id $DISTRIBUTION_ID \
            --paths "/*" \
            --query 'Invalidation.Id' --output text)
        
        echo "⏳ Waiting for invalidation to complete..."
        aws cloudfront wait invalidation-completed \
            --distribution-id $DISTRIBUTION_ID \
            --id $INVALIDATION_ID
    fi
    
    echo "✅ Frontend deployment completed"
}

run_health_checks() {
    echo "🩺 Running health checks..."
    
    if [ "$COMPONENT" = "backend" ] || [ "$COMPONENT" = "all" ]; then
        # Backend health check
        echo "🔍 Checking backend health..."
        
        # Get the load balancer DNS name
        ALB_DNS=$(aws cloudformation describe-stacks \
            --stack-name "BigMann-${ENVIRONMENT^}" \
            --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
            --output text --region $AWS_REGION)
        
        if [ -n "$ALB_DNS" ] && [ "$ALB_DNS" != "None" ]; then
            BACKEND_URL="http://$ALB_DNS"
            echo "🌐 Testing backend URL: $BACKEND_URL/health"
            
            for i in {1..10}; do
                if curl -f -s "$BACKEND_URL/health" > /dev/null; then
                    echo "✅ Backend health check passed"
                    break
                else
                    echo "⏳ Waiting for backend to be ready (attempt $i/10)..."
                    sleep 30
                fi
                
                if [ $i -eq 10 ]; then
                    echo "❌ Backend health check failed"
                    exit 1
                fi
            done
        else
            echo "⚠️ Could not retrieve load balancer DNS, skipping backend health check"
        fi
    fi
    
    if [ "$COMPONENT" = "frontend" ] || [ "$COMPONENT" = "all" ]; then
        # Frontend health check
        CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
            --stack-name "BigMann-${ENVIRONMENT^}" \
            --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
            --output text --region $AWS_REGION)
        
        if [ -n "$CLOUDFRONT_URL" ] && [ "$CLOUDFRONT_URL" != "None" ]; then
            echo "🌐 Testing frontend URL: $CLOUDFRONT_URL"
            
            if curl -f -s "$CLOUDFRONT_URL" > /dev/null; then
                echo "✅ Frontend health check passed"
            else
                echo "❌ Frontend health check failed"
                exit 1
            fi
        else
            echo "⚠️ Could not retrieve CloudFront URL, skipping frontend health check"
        fi
    fi
}

setup_secrets() {
    echo "🔐 Setting up secrets for $ENVIRONMENT..."
    
    # Run the secrets setup script
    if [ -f "/app/aws-infrastructure/scripts/setup-secrets.sh" ]; then
        bash /app/aws-infrastructure/scripts/setup-secrets.sh $ENVIRONMENT
    else
        echo "⚠️ Secrets setup script not found, skipping..."
    fi
}

send_notification() {
    local status=$1
    local message=$2
    
    # Send SNS notification if topic exists
    SNS_TOPIC_ARN=$(aws cloudformation describe-stacks \
        --stack-name "BigMann-${ENVIRONMENT^}" \
        --query 'Stacks[0].Outputs[?OutputKey==`AlertTopicArn`].OutputValue' \
        --output text --region $AWS_REGION 2>/dev/null || echo "")
    
    if [ -n "$SNS_TOPIC_ARN" ] && [ "$SNS_TOPIC_ARN" != "None" ]; then
        aws sns publish \
            --topic-arn $SNS_TOPIC_ARN \
            --subject "Deployment $status: $DEPLOYMENT_ID" \
            --message "$message" --region $AWS_REGION || echo "⚠️ Failed to send notification"
    else
        echo "📧 Notification: $status - $message"
    fi
}

# Main execution
main() {
    validate_environment
    check_prerequisites
    
    echo "🚀 Starting deployment process..."
    
    case $COMPONENT in
        infrastructure)
            deploy_infrastructure
            setup_secrets
            ;;
        backend)
            deploy_backend
            ;;
        frontend)
            deploy_frontend
            ;;
        all)
            deploy_infrastructure
            setup_secrets
            sleep 30 # Wait for infrastructure to settle
            deploy_backend
            deploy_frontend
            ;;
        *)
            echo "❌ Invalid component: $COMPONENT"
            exit 1
            ;;
    esac
    
    run_health_checks
    
    echo "🎉 Deployment completed successfully: $DEPLOYMENT_ID"
    send_notification "SUCCESS" "Deployment $DEPLOYMENT_ID completed successfully for $ENVIRONMENT environment"
}

# Trap errors and send failure notifications
trap 'send_notification "FAILED" "Deployment $DEPLOYMENT_ID failed during execution"' ERR

# Execute main function
main