# Production Environment Configuration

environment            = "prod"
aws_region            = "us-east-1"
project_name          = "bme-agency"
owner                 = "Big Mann Entertainment"

# S3 Configuration
enable_s3_versioning  = true  # Enabled for data protection

# Cognito Configuration
enable_mfa            = true  # Required for production security

# Blockchain Configuration
blockchain_network    = "ethereum"  # Use Ethereum mainnet in production

# QLDB Configuration
enable_qldb           = true

# Monitoring Configuration
alert_email           = "ops-alerts@bigmannentertainment.com"
log_retention_days    = 90  # Longer retention for compliance

# Cost Configuration
cost_center           = "Production"
budget_limit_monthly  = 10000  # Higher budget for production
