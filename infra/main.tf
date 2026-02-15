# CVE Remediation Infrastructure
# Lambda + EventBridge + IAM for automated vulnerability remediation
#
# Usage:
#   cd infra
#   terraform init
#   terraform workspace select dev || terraform workspace new dev
#   terraform apply -var-file=./environments/dev.tfvars

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "model-agency-assets"
    key            = "remediation/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }
}

locals {
  function_name = "cve-remediation-${var.environment}"
}

# -------------------------------------------------------------------
# IAM Role for Lambda
# -------------------------------------------------------------------

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "remediation_lambda" {
  name               = "${local.function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "lambda_permissions" {
  # CloudWatch Logs
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  # Secrets Manager — read GitHub token
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [var.github_secret_arn]
  }

  # CloudWatch Metrics — custom metrics
  statement {
    actions   = ["cloudwatch:PutMetricData"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "cloudwatch:namespace"
      values   = ["CVERemediation"]
    }
  }

  # S3 — read Lambda artifact
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${var.artifact_bucket_arn}/*"]
  }
}

resource "aws_iam_role_policy" "remediation_lambda" {
  name   = "${local.function_name}-policy"
  role   = aws_iam_role.remediation_lambda.id
  policy = data.aws_iam_policy_document.lambda_permissions.json
}

# -------------------------------------------------------------------
# Lambda Function
# -------------------------------------------------------------------

resource "aws_lambda_function" "remediation" {
  function_name = local.function_name
  role          = aws_iam_role.remediation_lambda.arn
  handler       = "remediation_lambda.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 256

  s3_bucket = var.artifact_bucket
  s3_key    = replace(var.lambda_zip_path, "s3://${var.artifact_bucket}/", "")

  environment {
    variables = {
      GITHUB_SECRET_ARN = var.github_secret_arn
      GITHUB_REPO       = var.github_repo
      DEFAULT_BRANCH    = var.default_branch
      ENVIRONMENT       = var.environment
      AWS_REGION_CUSTOM = var.aws_region
    }
  }

  tags = {
    Component = "CVERemediation"
  }
}

# -------------------------------------------------------------------
# CloudWatch Log Group (explicit for retention control)
# -------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "remediation" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = 30
}

# -------------------------------------------------------------------
# EventBridge Rule — Inspector Findings
# -------------------------------------------------------------------

resource "aws_cloudwatch_event_rule" "inspector_finding" {
  name        = "${local.function_name}-inspector-trigger"
  description = "Routes Inspector findings to the remediation Lambda"

  event_pattern = jsonencode({
    source      = ["aws.inspector2"]
    detail-type = ["Inspector2 Finding"]
    detail = {
      severity = ["CRITICAL", "HIGH"]
    }
  })
}

resource "aws_cloudwatch_event_target" "remediation_lambda" {
  rule = aws_cloudwatch_event_rule.inspector_finding.name
  arn  = aws_lambda_function.remediation.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remediation.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.inspector_finding.arn
}
