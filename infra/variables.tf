variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
}

variable "lambda_zip_path" {
  description = "S3 URI to the remediation Lambda zip (e.g. s3://bucket/remediation-dev.zip)"
  type        = string
}

variable "github_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the GitHub PAT"
  type        = string
}

variable "github_repo" {
  description = "GitHub owner/repo for issue creation (e.g. your-org/your-repo)"
  type        = string
}

variable "default_branch" {
  description = "Default branch for PRs"
  type        = string
  default     = "main"
}

variable "artifact_bucket_arn" {
  description = "ARN of the S3 bucket storing Lambda artifacts"
  type        = string
}

variable "artifact_bucket" {
  description = "Name of the S3 bucket storing Lambda artifacts"
  type        = string
}

variable "tags" {
  description = "Default tags applied to all resources"
  type        = map(string)
  default     = {}
}
