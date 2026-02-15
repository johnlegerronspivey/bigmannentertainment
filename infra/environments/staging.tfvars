aws_region          = "us-east-1"
environment         = "staging"
lambda_zip_path     = "s3://model-agency-assets/remediation-staging.zip"
github_secret_arn   = "arn:aws:secretsmanager:us-east-1:314108682794:secret:github/token-staging"
github_repo         = "johnlegerronspivey/bigmannentertainment"
default_branch      = "main"
artifact_bucket_arn = "arn:aws:s3:::model-agency-assets"
artifact_bucket     = "model-agency-assets"
tags = {
  Project     = "ModelAgency"
  Environment = "staging"
  Owner       = "Platform"
}
