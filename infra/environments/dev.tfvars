aws_region          = "us-east-1"
environment         = "dev"
lambda_zip_path     = "s3://model-agency-assets/remediation-dev.zip"
github_secret_arn   = "arn:aws:secretsmanager:us-east-1:123456789012:secret:github/token-dev"
github_repo         = "your-org/your-repo"
default_branch      = "main"
artifact_bucket_arn = "arn:aws:s3:::model-agency-assets"
artifact_bucket     = "model-agency-assets"
tags = {
  Project     = "ModelAgency"
  Environment = "dev"
  Owner       = "Platform"
}
