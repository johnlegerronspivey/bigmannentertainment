# Terraform Outputs for AWS Modeling Agency Platform

# Portfolio Storage Outputs
output "portfolio_bucket_name" {
  description = "S3 bucket name for portfolio assets"
  value       = module.portfolio_storage.bucket_name
}

output "portfolio_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.portfolio_storage.bucket_arn
}

# CDN Outputs
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.cdn.distribution_id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = module.cdn.domain_name
}

# Cognito Outputs
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.agency_onboarding.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN"
  value       = module.agency_onboarding.user_pool_arn
  sensitive   = true
}

# DynamoDB Outputs
output "license_registry_table_name" {
  description = "DynamoDB table name for license registry"
  value       = module.smart_licensing.table_name
}

# Lambda Outputs
output "metadata_parser_function_arn" {
  description = "Lambda function ARN for metadata parser"
  value       = module.image_metadata.function_arn
}

# QLDB Outputs
output "dispute_ledger_name" {
  description = "QLDB ledger name for disputes"
  value       = module.support_disputes.ledger_name
}

# SNS Outputs
output "support_alerts_topic_arn" {
  description = "SNS topic ARN for support alerts"
  value       = module.support_disputes.alerts_topic_arn
}

# CloudWatch Outputs
output "log_group_name" {
  description = "CloudWatch log group name"
  value       = module.monitoring_security.log_group_name
}

# KBWI Outputs
output "kbwi_bucket_name" {
  description = "S3 bucket for KBWI documentation"
  value       = module.knowledge_base.bucket_name
}

output "kbwi_website_endpoint" {
  description = "KBWI website endpoint"
  value       = module.knowledge_base.website_endpoint
}

# Summary Output
output "deployment_summary" {
  description = "Deployment summary"
  value = {
    environment          = var.environment
    region               = var.aws_region
    portfolio_bucket     = module.portfolio_storage.bucket_name
    cdn_domain           = module.cdn.domain_name
    cognito_pool         = module.agency_onboarding.user_pool_id
    license_table        = module.smart_licensing.table_name
    dispute_ledger       = module.support_disputes.ledger_name
    kbwi_endpoint        = module.knowledge_base.website_endpoint
  }
}
