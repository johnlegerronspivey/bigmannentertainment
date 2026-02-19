resource "aws_secretsmanager_secret" "blockchain_keys" {
  name        = "${var.project}-${var.env}-blockchain-keys"
  description = "Private keys and credentials for blockchain and external APIs"
  tags        = var.tags
}

resource "aws_secretsmanager_secret_version" "initial" {
  secret_id     = aws_secretsmanager_secret.blockchain_keys.id
  secret_string = jsonencode(var.initial_secret_json)
}
