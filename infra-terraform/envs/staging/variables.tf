variable "project" {
  default = "bigmann-dooh"
}

variable "env" {
  default = "staging"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "campaign_zip" {
  default = "../artifacts/campaign-staging.zip"
}

variable "creative_zip" {
  default = "../artifacts/creative-staging.zip"
}

variable "admin_email" {
  default = "staging-ops@example.com"
}

variable "tfstate_bucket" {
  default = "my-terraform-state-bucket"
}

variable "tags" {
  default = {
    Owner       = "BigMann"
    Environment = "staging"
  }
}

variable "initial_secret_json" {
  default = {
    "blockchain_key" = "REPLACE_ME_STAGING"
  }
}
