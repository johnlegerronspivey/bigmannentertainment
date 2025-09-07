# Big Mann Entertainment - AWS Multi-Environment Deployment Guide

## 🎯 Overview

This guide provides comprehensive instructions for deploying the Big Mann Entertainment platform across Development, Staging, and Production environments using AWS services.

## 🏗️ Architecture

### Infrastructure Components

- **VPC**: Isolated network environment with public/private subnets
- **ECS Cluster**: Container orchestration for backend services
- **ECR**: Container registry for FastAPI backend images
- **Application Load Balancer**: Traffic distribution and SSL termination
- **S3 + CloudFront**: Frontend hosting and global CDN
- **Secrets Manager**: Secure credential management
- **CloudWatch**: Monitoring and logging
- **SNS**: Alerting and notifications

### Environments

1. **Development**: `BigMann-Development`
   - Single AZ deployment
   - Minimal resources
   - Debug logging enabled
   - Web3 features disabled for testing

2. **Staging**: `BigMann-Staging`
   - Multi-AZ deployment
   - Production-like configuration
   - Integration testing environment
   - Full feature set enabled

3. **Production**: `BigMann-Production`
   - High availability across 3 AZs
   - Auto-scaling enabled
   - Enhanced monitoring
   - Production security hardening

## 🚀 Deployment Status

### ✅ Development Environment
- **Status**: DEPLOYED (Domain Configuration Updated)
- **Stack Name**: BigMann-Development
- **Custom Domain**: https://dev.bigmannentertainment.com
- **API Domain**: https://api-dev.bigmannentertainment.com
- **CloudFront URL**: https://d36jfidccx04u0.cloudfront.net (fallback)
- **Load Balancer**: bigmann-development-alb-1207379331.us-east-1.elb.amazonaws.com
- **ECR Repository**: 314108682794.dkr.ecr.us-east-1.amazonaws.com/bigmann-fastapi-development
- **S3 Bucket**: bigmann-frontend-development-314108682794

### ⏳ Staging Environment
- **Status**: PENDING
- **Next Steps**: Deploy staging stack

### ⏳ Production Environment
- **Status**: PENDING
- **Next Steps**: Deploy production stack after staging validation

## 🔐 Secrets Management

All environment-specific secrets are stored in AWS Secrets Manager:

### Development Secrets
- `bigmann/development/database` - MongoDB credentials
- `bigmann/development/stripe` - Stripe API keys
- `bigmann/development/paypal` - PayPal credentials
- `bigmann/development/web3` - Web3 configuration
- `bigmann/development/jwt` - JWT signing secret
- `bigmann/development/aws-config` - AWS service configuration
- `bigmann/development/app-config` - Application settings

## 📝 Deployment Commands

### Infrastructure Deployment
```bash
# Deploy development environment
cd /app/aws-infrastructure
cdk deploy BigMann-Development --require-approval never

# Deploy staging environment
cdk deploy BigMann-Staging --require-approval never

# Deploy production environment
cdk deploy BigMann-Production --require-approval never
```

### Application Deployment
```bash
# Deploy all components to development
bash /app/aws-infrastructure/scripts/deploy.sh development all

# Deploy only backend to staging
bash /app/aws-infrastructure/scripts/deploy.sh staging backend

# Deploy only frontend to production
bash /app/aws-infrastructure/scripts/deploy.sh production frontend
```

### Environment-Specific Frontend Builds
```bash
cd /app/frontend

# Development build
yarn build:development

# Staging build
yarn build:staging

# Production build
yarn build:production
```

## 🔄 CI/CD Pipeline

The CI/CD pipeline includes:

1. **Source Stage**: GitHub integration
2. **Build Stage**: Parallel backend and frontend builds
3. **Test Stage**: Automated testing suite
4. **Deploy Development**: Automatic deployment to dev
5. **Manual Approval**: Staging deployment approval
6. **Deploy Staging**: Staging environment deployment
7. **Manual Approval**: Production deployment approval
8. **Deploy Production**: Production environment deployment

## 📊 Monitoring & Alerting

### CloudWatch Alarms
- High response time alerts
- Error rate monitoring
- CloudFront error tracking
- ECS service health monitoring

### SNS Notifications
- Deployment success/failure notifications
- Infrastructure health alerts
- Performance degradation warnings

## 🛠️ Management Scripts

### Deployment Script
```bash
/app/aws-infrastructure/scripts/deploy.sh <environment> <component> [version]
```

### Rollback Script
```bash
/app/aws-infrastructure/scripts/rollback.sh <environment> <component> [target_version]
```

### Secrets Setup Script
```bash
/app/aws-infrastructure/scripts/setup-secrets.sh <environment>
```

### Monitoring Script
```bash
/app/aws-infrastructure/scripts/monitor-deployment.sh <environment>
```

## 🌐 Environment URLs

### Development
- **Frontend**: https://dev.bigmannentertainment.com
- **Backend API**: https://api-dev.bigmannentertainment.com
- **Health Check**: https://api-dev.bigmannentertainment.com/health
- **Current CloudFront**: https://d36jfidccx04u0.cloudfront.net (temporary)

### Staging (Pending Deployment)
- **Frontend**: https://staging.bigmannentertainment.com
- **Backend API**: https://api-staging.bigmannentertainment.com

### Production (Pending Deployment)
- **Frontend**: https://bigmannentertainment.com
- **Backend API**: https://api.bigmannentertainment.com

## 🔧 Configuration Management

### Environment Variables

#### Frontend (.env files)
- `.env.development` - Development configuration
- `.env.staging` - Staging configuration
- `.env.production` - Production configuration

#### Backend (AWS Secrets Manager)
All backend configuration is managed through AWS Secrets Manager for enhanced security.

## 🚨 Troubleshooting

### Common Issues

1. **ECR Push Failures**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 314108682794.dkr.ecr.us-east-1.amazonaws.com
   ```

2. **CloudFront Cache Issues**
   ```bash
   aws cloudfront create-invalidation --distribution-id E2N1CXV6XQWOJ1 --paths "/*"
   ```

3. **ECS Service Not Starting**
   - Check CloudWatch logs: `/ecs/bigmann-development-backend`
   - Verify secrets accessibility
   - Check task definition configuration

### Health Checks

```bash
# Backend health check
curl -f http://bigmann-development-alb-1207379331.us-east-1.elb.amazonaws.com/health

# Frontend health check
curl -f https://d36jfidccx04u0.cloudfront.net
```

## 📋 Next Steps

1. **Deploy Backend Application**
   - Build and push Docker image to ECR
   - Create and deploy ECS service
   - Configure health checks

2. **Deploy Frontend Application**
   - Build React application for development
   - Upload to S3 bucket
   - Invalidate CloudFront cache

3. **Setup CI/CD Pipeline**
   - Configure GitHub integration
   - Set up build triggers
   - Test deployment pipeline

4. **Deploy Staging Environment**
   - Repeat process for staging
   - Configure staging-specific settings
   - Run integration tests

5. **Deploy Production Environment**
   - Final production deployment
   - Configure production monitoring
   - Set up backup strategies

## 🔗 Important Links

- **AWS Console**: https://console.aws.amazon.com/
- **CloudFormation Stacks**: https://console.aws.amazon.com/cloudformation/home?region=us-east-1
- **Secrets Manager**: https://console.aws.amazon.com/secretsmanager/home?region=us-east-1
- **ECR Repositories**: https://console.aws.amazon.com/ecr/repositories?region=us-east-1
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups

## ⚠️ Security Notes

1. **API Keys**: Update placeholder API keys in Secrets Manager
2. **Database**: Configure MongoDB Atlas connection string
3. **SSL Certificates**: Set up proper SSL certificates for production
4. **IAM Roles**: Regularly review and audit IAM permissions
5. **Network Security**: Configure security groups and NACLs appropriately

---

**Status**: Development environment successfully deployed and ready for application deployment.
**Next Action**: Deploy backend application to development environment.