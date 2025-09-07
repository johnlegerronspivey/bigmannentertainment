#!/bin/bash
# Domain Setup Script for Big Mann Entertainment
# Sets up DNS and SSL certificates for bigmannentertainment.com

set -e

DOMAIN="bigmannentertainment.com"
AWS_REGION="us-east-1"

echo "🌐 Setting up domain configuration for $DOMAIN"

# Check if hosted zone exists
check_hosted_zone() {
    echo "🔍 Checking for existing hosted zone..."
    
    ZONE_ID=$(aws route53 list-hosted-zones-by-name \
        --dns-name "$DOMAIN" \
        --query 'HostedZones[0].Id' \
        --output text 2>/dev/null || echo "None")
    
    if [ "$ZONE_ID" != "None" ] && [ -n "$ZONE_ID" ]; then
        echo "✅ Found existing hosted zone: $ZONE_ID"
        echo "Name servers for your domain registrar:"
        aws route53 get-hosted-zone --id "$ZONE_ID" \
            --query 'DelegationSet.NameServers' \
            --output table
        return 0
    else
        echo "⚠️ No hosted zone found for $DOMAIN"
        echo "To set up the domain:"
        echo "1. Create a hosted zone in Route 53 for $DOMAIN"
        echo "2. Update your domain registrar's name servers"
        echo "3. Re-run this script"
        return 1
    fi
}

# Create SSL certificates
create_certificates() {
    echo "🔐 Setting up SSL certificates..."
    
    # Request certificate for main domain and wildcard
    CERT_ARN=$(aws acm request-certificate \
        --domain-name "$DOMAIN" \
        --subject-alternative-names "*.$DOMAIN" \
        --validation-method DNS \
        --region $AWS_REGION \
        --query 'CertificateArn' \
        --output text)
    
    if [ -n "$CERT_ARN" ]; then
        echo "✅ Certificate requested: $CERT_ARN"
        echo "⏳ Waiting for DNS validation records..."
        
        # Wait for certificate details to be available
        sleep 10
        
        # Get validation records
        aws acm describe-certificate \
            --certificate-arn "$CERT_ARN" \
            --region $AWS_REGION \
            --query 'Certificate.DomainValidationOptions[*].[DomainName,ResourceRecord.Name,ResourceRecord.Value]' \
            --output table
            
        echo ""
        echo "📋 Next steps:"
        echo "1. Add the DNS validation records to your hosted zone"
        echo "2. Wait for certificate validation (usually 5-10 minutes)"
        echo "3. Deploy the updated infrastructure"
    else
        echo "❌ Failed to request certificate"
        return 1
    fi
}

# Test DNS resolution
test_dns() {
    echo "🔍 Testing DNS resolution..."
    
    local subdomains=("dev" "staging" "api-dev" "api-staging" "api")
    
    for subdomain in "${subdomains[@]}"; do
        local test_domain="${subdomain}.${DOMAIN}"
        if nslookup "$test_domain" >/dev/null 2>&1; then
            echo "✅ $test_domain resolves"
        else
            echo "⚠️ $test_domain does not resolve (expected before deployment)"
        fi
    done
    
    # Test main domain
    if nslookup "$DOMAIN" >/dev/null 2>&1; then
        echo "✅ $DOMAIN resolves"
    else
        echo "⚠️ $DOMAIN does not resolve"
    fi
}

# Update CloudFormation stacks with domain configuration
update_stacks() {
    echo "🚀 Updating CloudFormation stacks with domain configuration..."
    
    local environments=("Development" "Staging" "Production")
    
    for env in "${environments[@]}"; do
        local stack_name="BigMann-${env}"
        
        echo "📦 Checking stack: $stack_name"
        
        if aws cloudformation describe-stacks --stack-name "$stack_name" >/dev/null 2>&1; then
            echo "⏳ Stack exists, update will be applied on next deployment"
        else
            echo "ℹ️ Stack $stack_name does not exist yet"
        fi
    done
}

# Main execution
main() {
    echo "🎯 Starting domain setup for Big Mann Entertainment"
    echo "Domain: $DOMAIN"
    echo "Region: $AWS_REGION"
    echo "=========================================="
    
    if check_hosted_zone; then
        echo ""
        test_dns
        echo ""
        update_stacks
        echo ""
        echo "✅ Domain configuration completed"
        echo ""
        echo "🔗 Useful links:"
        echo "Route 53 Console: https://console.aws.amazon.com/route53/v2/hostedzones"
        echo "Certificate Manager: https://console.aws.amazon.com/acm/home?region=${AWS_REGION}"
        echo ""
        echo "📋 Next steps:"
        echo "1. Ensure DNS records are properly configured"
        echo "2. Wait for SSL certificate validation"
        echo "3. Deploy updated infrastructure: cdk deploy BigMann-Development"
    else
        echo ""
        echo "💡 To create a hosted zone manually:"
        echo "aws route53 create-hosted-zone --name $DOMAIN --caller-reference $(date +%s)"
        echo ""
        echo "Or use the AWS Console:"
        echo "https://console.aws.amazon.com/route53/v2/hostedzones"
    fi
}

# Execute main function
main