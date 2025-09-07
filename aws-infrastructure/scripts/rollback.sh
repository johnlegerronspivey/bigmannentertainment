#!/bin/bash
# AWS Multi-Environment Rollback Script for Big Mann Entertainment
# Provides quick rollback capabilities for deployments

set -e

ENVIRONMENT=$1
COMPONENT=$2
TARGET_VERSION=$3

if [ -z "$ENVIRONMENT" ] || [ -z "$COMPONENT" ]; then
    echo "Usage: $0 <environment> <component> [target_version]"
    echo "Environments: development, staging, production"
    echo "Components: frontend, backend, all"
    echo "If target_version is not specified, rolls back to previous version"
    exit 1
fi

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🔄 Starting rollback for $COMPONENT in $ENVIRONMENT environment"

rollback_backend() {
    echo "⏪ Rolling back backend..."
    
    CLUSTER_NAME="bigmann-$ENVIRONMENT-cluster"
    SERVICE_NAME="bigmann-$ENVIRONMENT-backend-service"
    
    if [ -n "$TARGET_VERSION" ]; then
        # Roll back to specific version
        IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/bigmann-fastapi-$ENVIRONMENT:$TARGET_VERSION"
        echo "🎯 Rolling back to version: $TARGET_VERSION"
        
        # Create new task definition with target version
        CURRENT_TASK_DEF=$(aws ecs describe-services \
            --cluster $CLUSTER_NAME \
            --services $SERVICE_NAME \
            --query 'services[0].taskDefinition' --output text)
        
        # Get current task definition
        TASK_DEF_JSON=$(aws ecs describe-task-definition \
            --task-definition $CURRENT_TASK_DEF \
            --query 'taskDefinition')
        
        # Update image URI in task definition
        NEW_TASK_DEF=$(echo $TASK_DEF_JSON | jq --arg IMAGE "$IMAGE_URI" \
            '.containerDefinitions[0].image = $IMAGE' | \
            jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .placementConstraints, .compatibilities, .registeredAt, .registeredBy)')
        
        # Register new task definition
        NEW_TASK_ARN=$(aws ecs register-task-definition \
            --cli-input-json "$NEW_TASK_DEF" \
            --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Update service
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --task-definition $NEW_TASK_ARN
    else
        # Roll back to previous version
        echo "🔍 Finding previous task definition..."
        PREVIOUS_TASK_ARN=$(aws ecs list-task-definitions \
            --family-prefix "bigmann-$ENVIRONMENT-backend" \
            --sort DESC \
            --max-items 2 \
            --query 'taskDefinitionArns[1]' --output text)
        
        if [ "$PREVIOUS_TASK_ARN" = "None" ] || [ -z "$PREVIOUS_TASK_ARN" ]; then
            echo "❌ No previous task definition found for rollback"
            exit 1
        fi
        
        echo "⏪ Rolling back to task definition: $PREVIOUS_TASK_ARN"
        
        # Update service with previous task definition
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --task-definition $PREVIOUS_TASK_ARN
    fi
    
    # Wait for rollback to complete
    echo "⏳ Waiting for rollback to complete..."
    aws ecs wait services-stable \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION
    
    echo "✅ Backend rollback completed"
}

rollback_frontend() {
    echo "⏪ Rolling back frontend..."
    
    S3_BUCKET="bigmann-frontend-$ENVIRONMENT-$AWS_ACCOUNT_ID"
    
    if [ -n "$TARGET_VERSION" ]; then
        # Restore from specific backup
        BACKUP_PREFIX="backups/$TARGET_VERSION/"
        echo "🎯 Restoring from backup: $BACKUP_PREFIX"
    else
        # Find most recent backup
        BACKUP_PREFIX=$(aws s3 ls "s3://$S3_BUCKET/backups/" | sort | tail -1 | awk '{print $2}')
        if [ -z "$BACKUP_PREFIX" ]; then
            echo "❌ No backup found for rollback"
            exit 1
        fi
        echo "🔍 Found most recent backup: $BACKUP_PREFIX"
    fi
    
    # Create current backup before rollback
    CURRENT_BACKUP="backups/pre-rollback-$(date +%Y%m%d-%H%M%S)/"
    echo "💾 Creating pre-rollback backup: $CURRENT_BACKUP"
    aws s3 sync "s3://$S3_BUCKET/" "s3://$S3_BUCKET/$CURRENT_BACKUP" \
        --exclude "backups/*"
    
    # Restore from backup
    echo "⏪ Restoring from backup..."
    aws s3 sync "s3://$S3_BUCKET/$BACKUP_PREFIX" "s3://$S3_BUCKET/" \
        --delete \
        --exclude "backups/*"
    
    # Invalidate CloudFront
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
    
    echo "✅ Frontend rollback completed"
}

rollback_infrastructure() {
    echo "⏪ Rolling back infrastructure..."
    echo "⚠️ Infrastructure rollback requires manual intervention"
    echo "   Please use CDK to deploy a previous version or CloudFormation console to rollback the stack"
    echo "   Stack name: BigMann-${ENVIRONMENT^}"
    
    # List recent stack events for reference
    echo "📋 Recent stack events:"
    aws cloudformation describe-stack-events \
        --stack-name "BigMann-${ENVIRONMENT^}" \
        --max-items 10 \
        --query 'StackEvents[*].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId]' \
        --output table
}

create_backup() {
    echo "💾 Creating backup for $COMPONENT in $ENVIRONMENT..."
    
    if [ "$COMPONENT" = "frontend" ] || [ "$COMPONENT" = "all" ]; then
        S3_BUCKET="bigmann-frontend-$ENVIRONMENT-$AWS_ACCOUNT_ID"
        BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
        
        echo "📦 Creating frontend backup: $BACKUP_NAME"
        aws s3 sync "s3://$S3_BUCKET/" "s3://$S3_BUCKET/backups/$BACKUP_NAME/" \
            --exclude "backups/*"
        
        echo "✅ Frontend backup created: s3://$S3_BUCKET/backups/$BACKUP_NAME/"
    fi
    
    if [ "$COMPONENT" = "backend" ] || [ "$COMPONENT" = "all" ]; then
        # Backend backup is handled through ECR image tags
        echo "📦 Backend versions are preserved in ECR with image tags"
        echo "   Repository: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/bigmann-fastapi-$ENVIRONMENT"
    fi
}

run_health_checks() {
    echo "🩺 Running post-rollback health checks..."
    
    if [ "$COMPONENT" = "backend" ] || [ "$COMPONENT" = "all" ]; then
        # Backend health check
        ALB_DNS=$(aws cloudformation describe-stacks \
            --stack-name "BigMann-${ENVIRONMENT^}" \
            --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
            --output text --region $AWS_REGION)
        
        if [ -n "$ALB_DNS" ] && [ "$ALB_DNS" != "None" ]; then
            BACKEND_URL="http://$ALB_DNS"
            echo "🌐 Testing backend URL: $BACKEND_URL/health"
            
            for i in {1..5}; do
                if curl -f -s "$BACKEND_URL/health" > /dev/null; then
                    echo "✅ Backend health check passed"
                    break
                else
                    echo "⏳ Waiting for backend to be ready (attempt $i/5)..."
                    sleep 10
                fi
                
                if [ $i -eq 5 ]; then
                    echo "❌ Backend health check failed after rollback"
                    exit 1
                fi
            done
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
                echo "❌ Frontend health check failed after rollback"
                exit 1
            fi
        fi
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
            --subject "Rollback $status: $ENVIRONMENT $COMPONENT" \
            --message "$message" --region $AWS_REGION || echo "⚠️ Failed to send notification"
    else
        echo "📧 Notification: $status - $message"
    fi
}

# Main execution
main() {
    echo "🚀 Starting rollback process..."
    
    # Create backup before rollback (safety measure)
    create_backup
    
    case $COMPONENT in
        backend)
            rollback_backend
            ;;
        frontend)
            rollback_frontend
            ;;
        infrastructure)
            rollback_infrastructure
            return 0  # Skip health checks for infrastructure
            ;;
        all)
            rollback_backend
            rollback_frontend
            ;;
        *)
            echo "❌ Invalid component: $COMPONENT"
            exit 1
            ;;
    esac
    
    run_health_checks
    
    echo "🎉 Rollback completed successfully"
    send_notification "SUCCESS" "Rollback completed successfully for $COMPONENT in $ENVIRONMENT environment"
}

# Trap errors and send failure notifications
trap 'send_notification "FAILED" "Rollback failed for $COMPONENT in $ENVIRONMENT environment"' ERR

# Execute main function
main