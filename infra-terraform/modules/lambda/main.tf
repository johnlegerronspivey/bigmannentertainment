data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.project}-${var.env}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "basic_exec" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "campaign" {
  filename         = var.campaign_zip
  function_name    = "${var.project}-${var.env}-campaign"
  role             = aws_iam_role.lambda_role.arn
  handler          = "campaign.handler"
  runtime          = "nodejs18.x"
  source_code_hash = filebase64sha256(var.campaign_zip)

  environment {
    variables = {
      CAMPAIGNS_TABLE = var.campaigns_table
      REGION          = var.aws_region
    }
  }

  tags = var.tags
}

resource "aws_lambda_function" "creative" {
  filename         = var.creative_zip
  function_name    = "${var.project}-${var.env}-creative"
  role             = aws_iam_role.lambda_role.arn
  handler          = "creative.handler"
  runtime          = "nodejs18.x"
  source_code_hash = filebase64sha256(var.creative_zip)

  environment {
    variables = {
      CREATIVES_TABLE = var.creatives_table
      S3_BUCKET       = var.s3_bucket
    }
  }

  tags = var.tags
}

resource "aws_iam_policy" "dynamo_policy" {
  name = "${var.project}-${var.env}-dynamo-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:Scan"
        ]
        Effect = "Allow"
        Resource = [
          var.campaigns_table_arn,
          var.creatives_table_arn,
          var.attribution_table_arn,
          var.royalties_table_arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dynamo_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamo_policy.arn
}
