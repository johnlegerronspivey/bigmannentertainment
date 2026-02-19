resource "aws_kinesis_stream" "impressions" {
  name             = "${var.project}-${var.env}-impressions"
  shard_count      = var.shard_count
  retention_period = var.retention_hours

  tags = var.tags
}
