#!/bin/bash
# AWS Deployment Monitoring Script for Big Mann Entertainment
# Monitors the status of CloudFormation stacks and deployments

set -e

ENVIRONMENT=${1:-development}
AWS_REGION="us-east-1"

echo "🔍 Monitoring deployment status for $ENVIRONMENT environment..."

STACK_NAME="BigMann-${ENVIRONMENT^}"

# Function to check stack status
check_stack_status() {
    local stack_status=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].StackStatus' \
        --output text --region $AWS_REGION 2>/dev/null || echo "NOT_EXISTS")
    
    echo "Stack Status: $stack_status"
    
    case $stack_status in
        CREATE_COMPLETE|UPDATE_COMPLETE)
            echo "✅ Stack deployment completed successfully"
            return 0
            ;;
        CREATE_IN_PROGRESS|UPDATE_IN_PROGRESS)
            echo "⏳ Stack deployment in progress..."
            return 1
            ;;
        CREATE_FAILED|UPDATE_FAILED|ROLLBACK_COMPLETE|ROLLBACK_FAILED)
            echo "❌ Stack deployment failed"
            show_stack_events
            return 2
            ;;
        NOT_EXISTS)
            echo "⚠️ Stack does not exist"
            return 3
            ;;
        *)
            echo "❓ Unknown stack status: $stack_status"
            return 4
            ;;
    esac
}

# Function to show recent stack events
show_stack_events() {
    echo "📋 Recent stack events:"
    aws cloudformation describe-stack-events \
        --stack-name "$STACK_NAME" \
        --max-items 10 \
        --query 'StackEvents[*].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId,ResourceStatusReason]' \
        --output table --region $AWS_REGION || echo "Unable to fetch stack events"
}

# Function to get stack outputs
get_stack_outputs() {
    echo "📊 Stack outputs:"
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue,Description]' \
        --output table --region $AWS_REGION
}

# Function to check ECS service health
check_ecs_health() {
    local cluster_name="bigmann-$ENVIRONMENT-cluster"
    local service_name="bigmann-$ENVIRONMENT-backend-service"
    
    echo "🏥 Checking ECS service health..."
    
    local service_status=$(aws ecs describe-services \
        --cluster "$cluster_name" \
        --services "$service_name" \
        --query 'services[0].status' \
        --output text --region $AWS_REGION 2>/dev/null || echo "NOT_EXISTS")
    
    if [ "$service_status" != "NOT_EXISTS" ]; then
        echo "Service Status: $service_status"
        
        local running_count=$(aws ecs describe-services \
            --cluster "$cluster_name" \
            --services "$service_name" \
            --query 'services[0].runningCount' \
            --output text --region $AWS_REGION)
        
        local desired_count=$(aws ecs describe-services \
            --cluster "$cluster_name" \
            --services "$service_name" \
            --query 'services[0].desiredCount' \
            --output text --region $AWS_REGION)
        
        echo "Running tasks: $running_count/$desired_count"
        
        if [ "$running_count" = "$desired_count" ] && [ "$running_count" != "0" ]; then
            echo "✅ ECS service is healthy"
        else
            echo "⚠️ ECS service is not at desired capacity"
        fi
    else
        echo "ℹ️ ECS service not yet created"
    fi
}

# Function to check CloudFront distribution
check_cloudfront_health() {
    echo "🌐 Checking CloudFront distribution..."
    
    local distribution_id=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
        --output text --region $AWS_REGION 2>/dev/null || echo "")
    
    if [ -n "$distribution_id" ] && [ "$distribution_id" != "None" ]; then
        local distribution_status=$(aws cloudfront get-distribution \
            --id "$distribution_id" \
            --query 'Distribution.Status' \
            --output text)
        
        echo "Distribution Status: $distribution_status"
        
        if [ "$distribution_status" = "Deployed" ]; then
            echo "✅ CloudFront distribution is deployed"
            
            local domain_name=$(aws cloudfront get-distribution \
                --id "$distribution_id" \
                --query 'Distribution.DomainName' \
                --output text)
            
            echo "Domain: https://$domain_name"
        else
            echo "⏳ CloudFront distribution is still deploying..."
        fi
    else
        echo "ℹ️ CloudFront distribution not yet created"
    fi
}

# Function to check S3 bucket
check_s3_health() {
    echo "🪣 Checking S3 bucket..."
    
    local bucket_name=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
        --output text --region $AWS_REGION 2>/dev/null || echo "")
    
    if [ -n "$bucket_name" ] && [ "$bucket_name" != "None" ]; then
        if aws s3 ls "s3://$bucket_name" >/dev/null 2>&1; then
            echo "✅ S3 bucket exists and is accessible"
            
            local object_count=$(aws s3 ls "s3://$bucket_name" --recursive | wc -l)
            echo "Objects in bucket: $object_count"
        else
            echo "❌ S3 bucket is not accessible"
        fi
    else
        echo "ℹ️ S3 bucket not yet created"
    fi
}

# Function to check ALB health
check_alb_health() {
    echo "⚖️ Checking Application Load Balancer..."
    
    local alb_dns=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text --region $AWS_REGION 2>/dev/null || echo "")
    
    if [ -n "$alb_dns" ] && [ "$alb_dns" != "None" ]; then
        echo "ALB DNS: $alb_dns"
        
        if curl -f -s "http://$alb_dns/health" >/dev/null 2>&1; then
            echo "✅ ALB health check passed"
        else
            echo "⚠️ ALB health check failed (may be normal if backend not deployed yet)"
        fi
    else
        echo "ℹ️ Application Load Balancer not yet created"
    fi
}

# Main monitoring loop
main() {
    echo "🚀 Starting deployment monitoring for $ENVIRONMENT environment"
    echo "Stack: $STACK_NAME"
    echo "Region: $AWS_REGION"
    echo "=========================================="
    
    local max_attempts=60  # 30 minutes max
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo ""
        echo "🔄 Attempt $attempt/$max_attempts - $(date)"
        echo "----------------------------------------"
        
        if check_stack_status; then
            echo ""
            echo "🎉 Stack deployment completed! Getting detailed status..."
            echo "=========================================="
            
            get_stack_outputs
            echo ""
            
            check_ecs_health
            echo ""
            
            check_cloudfront_health
            echo ""
            
            check_s3_health
            echo ""
            
            check_alb_health
            echo ""
            
            echo "✅ Deployment monitoring completed successfully"
            break
        elif [ $? -eq 2 ]; then
            echo "💥 Stack deployment failed. Exiting..."
            exit 1
        elif [ $? -eq 3 ]; then
            echo "⚠️ Stack does not exist. Please create it first."
            exit 1
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            echo "⏰ Timeout reached. Deployment may still be in progress."
            show_stack_events
            exit 1
        fi
        
        attempt=$((attempt + 1))
        sleep 30
    done
}

# Handle interruption
trap 'echo "🛑 Monitoring interrupted"; exit 130' INT TERM

# Execute main function
main