# Main Terraform Configuration for AWS Modeling Agency Platform
# Orchestrates all infrastructure modules

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "bme-terraform-state"
    key            = "modeling-agency/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.owner
      ManagedBy   = "Terraform"
      Compliance  = "GDPR,CCPA,SOC2"
    }
  }
}

# Local variables
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    Terraform   = "true"
  }
}

# Module: Image & Portfolio Storage
module "portfolio_storage" {
  source = "./modules/portfolio-storage"
  
  environment       = var.environment
  project_name      = var.project_name
  bucket_prefix     = "${var.project_name}-portfolio"
  enable_versioning = var.enable_s3_versioning
  
  tags = local.common_tags
}

# Module: Metadata Extraction & AI Tagging
module "image_metadata" {
  source = "./modules/image-metadata"
  
  environment   = var.environment
  project_name  = var.project_name
  s3_bucket_arn = module.portfolio_storage.bucket_arn
  
  tags = merge(local.common_tags, {
    Module = "ImageMetadata"
  })
}

# Module: Smart Licensing Engine
module "smart_licensing" {
  source = "./modules/smart-licensing"
  
  environment     = var.environment
  project_name    = var.project_name
  blockchain_type = var.blockchain_network
  
  tags = merge(local.common_tags, {
    Module = "SmartLicensing"
  })
}

# Module: Agency Onboarding & KYC
module "agency_onboarding" {
  source = "./modules/agency-onboarding"
  
  environment       = var.environment
  project_name      = var.project_name
  cognito_domain    = "${var.project_name}-${var.environment}"
  enable_mfa        = var.enable_mfa
  
  tags = merge(local.common_tags, {
    Module = "AgencyOnboarding"
  })
}

# Module: Support System & DAO Disputes
module "support_disputes" {
  source = "./modules/support-disputes"
  
  environment  = var.environment
  project_name = var.project_name
  enable_qldb  = var.enable_qldb
  
  tags = merge(local.common_tags, {
    Module = "SupportDisputes"
  })
}

# Module: Knowledge Base (KBWI)
module "knowledge_base" {
  source = "./modules/knowledge-base"
  
  environment  = var.environment
  project_name = var.project_name
  
  tags = merge(local.common_tags, {
    Module = "KBWI"
  })
}

# Module: Monitoring & Security
module "monitoring_security" {
  source = "./modules/monitoring-security"
  
  environment     = var.environment
  project_name    = var.project_name
  alert_email     = var.alert_email
  retention_days  = var.log_retention_days
  
  tags = merge(local.common_tags, {
    Module = "MonitoringSecurity"
  })
}

# Module: CDN (CloudFront)
module "cdn" {
  source = "./modules/cdn"
  
  environment       = var.environment
  project_name      = var.project_name
  s3_bucket_domain  = module.portfolio_storage.bucket_regional_domain_name
  
  tags = merge(local.common_tags, {
    Module = "CDN"
  })
}
