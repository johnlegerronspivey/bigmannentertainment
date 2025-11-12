# Development Environment Configuration

environment            = "dev"
aws_region            = "us-east-1"
project_name          = "bme-agency"
owner                 = "Big Mann Entertainment"

# S3 Configuration
enable_s3_versioning  = false  # Disabled in dev for cost savings

# Cognito Configuration
enable_mfa            = false  # Disabled in dev for easier testing

# Blockchain Configuration
blockchain_network    = "polygon"  # Use Polygon testnet in dev

# QLDB Configuration
enable_qldb           = true

# Monitoring Configuration
alert_email           = "dev-alerts@bigmannentertainment.com"
log_retention_days    = 7  # Shorter retention in dev

# Cost Configuration
cost_center           = "Development"
budget_limit_monthly  = 500  # Lower budget for dev
