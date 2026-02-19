resource "aws_qldb_ledger" "ledger" {
  name                = "${var.project}-${var.env}-ledger"
  permissions_mode    = "ALLOW_ALL"
  deletion_protection = false
  tags                = var.tags
}
