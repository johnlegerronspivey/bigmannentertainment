variable "project" {
  default = "bigmann-dooh"
}

variable "env" {
  default = "prod"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "campaign_zip" {
  default = "../artifacts/campaign.zip"
}

variable "creative_zip" {
  default = "../artifacts/creative.zip"
}

variable "admin_email" {
  default = "ops@example.com"
}

variable "tfstate_bucket" {
  default = "my-terraform-state-bucket"
}

variable "tags" {
  default = {
    Owner       = "BigMann"
    Environment = "prod"
  }
}

variable "initial_secret_json" {
  default = {
    "blockchain_key" = "REPLACE_ME"
  }
}
