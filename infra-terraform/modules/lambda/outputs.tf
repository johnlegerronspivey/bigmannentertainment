output "campaign_lambda_arn" {
  value = aws_lambda_function.campaign.arn
}

output "creative_lambda_arn" {
  value = aws_lambda_function.creative.arn
}
