output "secrets_arn" {
  value = aws_secretsmanager_secret.blockchain_keys.arn
}
