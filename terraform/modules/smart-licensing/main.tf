# Smart Licensing Module - DynamoDB & Blockchain Integration

resource "aws_dynamodb_table" "license_registry" {
  name           = "${var.project_name}-license-registry-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "TokenID"
  range_key      = "LicenseID"
  
  attribute {
    name = "TokenID"
    type = "S"
  }
  
  attribute {
    name = "LicenseID"
    type = "S"
  }
  
  attribute {
    name = "ModelID"
    type = "S"
  }
  
  attribute {
    name = "AgencyID"
    type = "S"
  }
  
  attribute {
    name = "CreatedAt"
    type = "N"
  }
  
  global_secondary_index {
    name            = "ModelIDIndex"
    hash_key        = "ModelID"
    range_key       = "CreatedAt"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "AgencyIDIndex"
    hash_key        = "AgencyID"
    range_key       = "CreatedAt"
    projection_type = "ALL"
  }
  
  ttl {
    attribute_name = "ExpirationTime"
    enabled        = true
  }
  
  point_in_time_recovery {
    enabled = var.environment == "prod" ? true : false
  }
  
  server_side_encryption {
    enabled = true
  }
  
  tags = merge(var.tags, {
    Name = "License Registry"
  })
}

# DynamoDB table for royalty payments
resource "aws_dynamodb_table" "royalty_payments" {
  name           = "${var.project_name}-royalty-payments-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PaymentID"
  range_key      = "Timestamp"
  
  attribute {
    name = "PaymentID"
    type = "S"
  }
  
  attribute {
    name = "Timestamp"
    type = "N"
  }
  
  attribute {
    name = "LicenseID"
    type = "S"
  }
  
  global_secondary_index {
    name            = "LicenseIDIndex"
    hash_key        = "LicenseID"
    range_key       = "Timestamp"
    projection_type = "ALL"
  }
  
  point_in_time_recovery {
    enabled = var.environment == "prod" ? true : false
  }
  
  server_side_encryption {
    enabled = true
  }
  
  tags = merge(var.tags, {
    Name = "Royalty Payments"
  })
}

# Lambda for royalty calculations
resource "aws_lambda_function" "royalty_calculator" {
  filename      = "${path.module}/lambda/royalty_calculator.zip"
  function_name = "${var.project_name}-royalty-calculator-${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 30
  
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.royalty_payments.name
      BLOCKCHAIN     = var.blockchain_type
      ENVIRONMENT    = var.environment
    }
  }
  
  tags = var.tags
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-lambda-royalty-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.tags
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${var.environment}"
  role = aws_iam_role.lambda_exec.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.license_registry.arn,
          aws_dynamodb_table.royalty_payments.arn,
          "${aws_dynamodb_table.license_registry.arn}/index/*",
          "${aws_dynamodb_table.royalty_payments.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_license_creation" {
  alarm_name          = "${var.project_name}-high-license-creation-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ConsumedWriteCapacityUnits"
  namespace           = "AWS/DynamoDB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1000"
  alarm_description   = "Alert when license creation spikes"
  
  dimensions = {
    TableName = aws_dynamodb_table.license_registry.name
  }
  
  tags = var.tags
}
