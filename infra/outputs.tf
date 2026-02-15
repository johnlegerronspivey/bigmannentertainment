output "remediation_lambda_arn" {
  description = "ARN of the deployed remediation Lambda function"
  value       = aws_lambda_function.remediation.arn
}

output "remediation_lambda_name" {
  description = "Name of the deployed remediation Lambda function"
  value       = aws_lambda_function.remediation.function_name
}

output "inspector_event_rule_name" {
  description = "Name of the EventBridge rule that triggers the Lambda"
  value       = aws_cloudwatch_event_rule.inspector_finding.name
}

output "lambda_log_group" {
  description = "CloudWatch Log Group for Lambda execution logs"
  value       = aws_cloudwatch_log_group.remediation.name
}

output "lambda_role_arn" {
  description = "IAM Role ARN used by the Lambda function"
  value       = aws_iam_role.remediation_lambda.arn
}
