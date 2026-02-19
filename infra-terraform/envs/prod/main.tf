provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source  = "../../modules/vpc"
  project = var.project
  env     = var.env
  tags    = var.tags
}

module "cognito" {
  source  = "../../modules/cognito"
  project = var.project
  env     = var.env
  tags    = var.tags
}

module "frontend" {
  source  = "../../modules/s3-cloudfront"
  project = var.project
  env     = var.env
  tags    = var.tags
}

module "dynamodb" {
  source  = "../../modules/dynamodb"
  project = var.project
  env     = var.env
  tags    = var.tags
}

module "kinesis" {
  source          = "../../modules/kinesis"
  project         = var.project
  env             = var.env
  shard_count     = 4
  retention_hours = 48
  tags            = var.tags
}

module "lambda" {
  source                = "../../modules/lambda"
  project               = var.project
  env                   = var.env
  campaign_zip          = var.campaign_zip
  creative_zip          = var.creative_zip
  campaigns_table       = module.dynamodb.campaigns_table
  creatives_table       = module.dynamodb.creatives_table
  campaigns_table_arn   = module.dynamodb.campaigns_table
  creatives_table_arn   = module.dynamodb.creatives_table
  attribution_table_arn = module.dynamodb.attribution_table
  royalties_table_arn   = module.dynamodb.royalties_table
  s3_bucket             = module.frontend.bucket_name
  aws_region            = var.aws_region
  tags                  = var.tags
}

module "eventbridge" {
  source             = "../../modules/eventbridge"
  project            = var.project
  env                = var.env
  trigger_lambda_arn = module.lambda.campaign_lambda_arn
  tags               = var.tags
}

module "sns" {
  source      = "../../modules/sns"
  project     = var.project
  env         = var.env
  admin_email = var.admin_email
  tags        = var.tags
}

module "secrets" {
  source              = "../../modules/secrets-manager"
  project             = var.project
  env                 = var.env
  initial_secret_json = var.initial_secret_json
  tags                = var.tags
}
