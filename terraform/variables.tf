# Global Variables for AWS Modeling Agency Platform

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "bme-agency"
}

variable "owner" {
  description = "Owner of the infrastructure"
  type        = string
  default     = "Big Mann Entertainment"
}

# S3 Configuration
variable "enable_s3_versioning" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

# Cognito Configuration
variable "enable_mfa" {
  description = "Enable MFA for Cognito users"
  type        = bool
  default     = true
}

# Blockchain Configuration
variable "blockchain_network" {
  description = "Blockchain network for licensing (ethereum, polygon, base)"
  type        = string
  default     = "polygon"
  
  validation {
    condition     = contains(["ethereum", "polygon", "base"], var.blockchain_network)
    error_message = "Blockchain network must be ethereum, polygon, or base."
  }
}

# QLDB Configuration
variable "enable_qldb" {
  description = "Enable QLDB for dispute ledger"
  type        = bool
  default     = true
}

# Monitoring Configuration
variable "alert_email" {
  description = "Email for CloudWatch alerts"
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
  
  validation {
    condition     = contains([1, 3, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch value."
  }
}

# Cost Tracking
variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "ModelingAgency"
}

variable "budget_limit_monthly" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 5000
}
